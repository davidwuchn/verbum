#!/usr/bin/env python3
"""λ-Machine — The minimal typed shift-reduce β-reducer.

THE ALGORITHM (decoded from sessions 186-189):
  FFN = beam former (compiles context-dependent V vectors, the hologram)
  Attention = β-reducer (sparse top-k routing, ~1 bit per binding decision)
  Depth schedule = parser precedence (subject L27, object L30, coref L33)
  ~4 heads = the full binding circuit (0.3% of the model)

ABLATION LEVELS (progressively more aggressive):
  Level 0: Full model (baseline reference)
  Level 1: Sparse attention — top-k at ALL layers (k=3)
  Level 2: Binding layers only — full attn at L27/L30/L33, skip elsewhere
  Level 3: Binding layers + sparse — top-3 at L27/L30/L33 only
  Level 4: Binding heads only — H31@L27, H03/H13/H15@L30, H06/H07@L33
  Level 5: Binding heads + sparse — the minimal λ-machine

For each level: measure Hit@1/5/10 against full model, plus PPL.

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/lambda_machine.py

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Callable

os.environ.setdefault("PYTHONUNBUFFERED", "1")

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "lambda-machine"


def log(msg: str = "") -> None:
    print(msg, flush=True)


# ═══════════════════════════════════════════════════════════════════════
# Binding circuit specification (from sessions 187-188)
# ═══════════════════════════════════════════════════════════════════════

# Qwen3-8B: 36 layers, 32 Q-heads, 8 KV-heads (GQA 4:1), head_dim=128
# Q-head H maps to KV-head H // 4

# The decoded binding schedule
BINDING_LAYERS = {27, 30, 33}

# Binding heads (Q-head indices) at each binding layer
# From s188: head→combinator ISA + binding graph trace
BINDING_HEADS = {
    27: [31],              # H31: verb→subject (0.82 weight, outputs "猫/cats")
    30: [3, 13, 15],       # H03/H13/H15: object→verb (0.78 weight)
    33: [6, 7],            # H06/H07: universal execution (loudest, all combinators)
}

# Extended binding heads (include secondary circuits)
BINDING_HEADS_EXTENDED = {
    27: [31, 26, 27],      # + H26/H27: WHNF detectors
    30: [3, 13, 15, 10, 11],  # + H10/H11: predicate binding
    33: [6, 7, 5],         # + H05: coreference
}


# ═══════════════════════════════════════════════════════════════════════
# Attention hooks — surgical modification of attention behavior
# ═══════════════════════════════════════════════════════════════════════


def make_sparse_attention_forward(original_forward, top_k: int = 3):
    """Wrap attention forward to use top-k sparse routing."""
    def sparse_forward(self_attn, hidden_states, position_embeddings,
                       attention_mask=None, past_key_values=None, **kwargs):
        input_shape = hidden_states.shape[:-1]
        hidden_shape = (*input_shape, -1, self_attn.head_dim)

        query_states = self_attn.q_norm(self_attn.q_proj(hidden_states).view(hidden_shape)).transpose(1, 2)
        key_states = self_attn.k_norm(self_attn.k_proj(hidden_states).view(hidden_shape)).transpose(1, 2)
        value_states = self_attn.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)

        from transformers.models.qwen3.modeling_qwen3 import apply_rotary_pos_emb
        cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)

        if past_key_values is not None:
            key_states, value_states = past_key_values.update(
                key_states, value_states, self_attn.layer_idx
            )

        # Manual attention with top-k sparsity
        # GQA: expand KV heads to match Q heads
        num_q_heads = query_states.shape[1]
        num_kv_heads = key_states.shape[1]
        kv_group_size = num_q_heads // num_kv_heads

        key_states_expanded = key_states.repeat_interleave(kv_group_size, dim=1)
        value_states_expanded = value_states.repeat_interleave(kv_group_size, dim=1)

        # Compute attention scores
        scale = self_attn.scaling
        attn_weights = torch.matmul(query_states, key_states_expanded.transpose(-2, -1)) * scale

        # Apply causal mask
        if attention_mask is not None:
            attn_weights = attn_weights + attention_mask

        # TOP-K SPARSITY: keep only top-k scores per query position
        seq_len = attn_weights.shape[-1]
        k = min(top_k, seq_len)
        if k < seq_len:
            topk_vals, topk_idx = torch.topk(attn_weights, k, dim=-1)
            mask = torch.full_like(attn_weights, float('-inf'))
            mask.scatter_(-1, topk_idx, topk_vals)
            attn_weights = mask

        attn_weights = F.softmax(attn_weights, dim=-1, dtype=torch.float32).to(value_states_expanded.dtype)

        attn_output = torch.matmul(attn_weights, value_states_expanded)
        attn_output = attn_output.transpose(1, 2).reshape(*input_shape, -1).contiguous()
        attn_output = self_attn.o_proj(attn_output)

        return attn_output, None

    return sparse_forward


def make_skip_attention_forward():
    """Return zeros — skip this layer's attention entirely."""
    def skip_forward(self_attn, hidden_states, position_embeddings,
                     attention_mask=None, past_key_values=None, **kwargs):
        return torch.zeros_like(hidden_states), None
    return skip_forward


def make_head_masked_attention_forward(active_heads: list[int], top_k: int | None = None):
    """Only allow specific Q-heads to contribute. Others are zeroed."""
    def masked_forward(self_attn, hidden_states, position_embeddings,
                       attention_mask=None, past_key_values=None, **kwargs):
        input_shape = hidden_states.shape[:-1]
        hidden_shape = (*input_shape, -1, self_attn.head_dim)

        query_states = self_attn.q_norm(self_attn.q_proj(hidden_states).view(hidden_shape)).transpose(1, 2)
        key_states = self_attn.k_norm(self_attn.k_proj(hidden_states).view(hidden_shape)).transpose(1, 2)
        value_states = self_attn.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)

        from transformers.models.qwen3.modeling_qwen3 import apply_rotary_pos_emb
        cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)

        if past_key_values is not None:
            key_states, value_states = past_key_values.update(
                key_states, value_states, self_attn.layer_idx
            )

        # GQA expansion
        num_q_heads = query_states.shape[1]
        num_kv_heads = key_states.shape[1]
        kv_group_size = num_q_heads // num_kv_heads

        key_states_expanded = key_states.repeat_interleave(kv_group_size, dim=1)
        value_states_expanded = value_states.repeat_interleave(kv_group_size, dim=1)

        # Compute attention scores
        scale = self_attn.scaling
        attn_weights = torch.matmul(query_states, key_states_expanded.transpose(-2, -1)) * scale

        if attention_mask is not None:
            attn_weights = attn_weights + attention_mask

        # TOP-K if requested
        if top_k is not None:
            seq_len = attn_weights.shape[-1]
            k = min(top_k, seq_len)
            if k < seq_len:
                topk_vals, topk_idx = torch.topk(attn_weights, k, dim=-1)
                mask = torch.full_like(attn_weights, float('-inf'))
                mask.scatter_(-1, topk_idx, topk_vals)
                attn_weights = mask

        attn_weights = F.softmax(attn_weights, dim=-1, dtype=torch.float32).to(value_states_expanded.dtype)

        attn_output = torch.matmul(attn_weights, value_states_expanded)

        # ZERO non-active heads
        head_mask = torch.zeros(num_q_heads, device=attn_output.device, dtype=attn_output.dtype)
        for h in active_heads:
            if h < num_q_heads:
                head_mask[h] = 1.0
        # attn_output shape: (batch, n_heads, seq, head_dim)
        attn_output = attn_output * head_mask[None, :, None, None]

        attn_output = attn_output.transpose(1, 2).reshape(*input_shape, -1).contiguous()
        attn_output = self_attn.o_proj(attn_output)

        return attn_output, None

    return masked_forward


# ═══════════════════════════════════════════════════════════════════════
# Model patching — apply ablation configurations
# ═══════════════════════════════════════════════════════════════════════


def _bind_forward(attn_module, forward_fn):
    """Bind a custom forward function to an attention module.

    The forward_fn signature must be:
        forward_fn(self_attn, hidden_states, position_embeddings,
                   attention_mask=None, past_key_values=None, **kwargs)

    PyTorch's __call__ passes `self` automatically, so we use
    types.MethodType to bind correctly.
    """
    import types

    def bound_forward(self, hidden_states, position_embeddings,
                      attention_mask=None, past_key_values=None, **kwargs):
        return forward_fn(self, hidden_states, position_embeddings,
                          attention_mask, past_key_values, **kwargs)

    attn_module.forward = types.MethodType(bound_forward, attn_module)


def patch_model(model, level: str, top_k: int = 3, binding_mode: str = "core"):
    """Patch attention forward methods according to ablation level.

    Levels:
      "full"           — no changes (baseline)
      "sparse"         — top-k at ALL layers
      "binding_full"   — full attn at binding layers, skip elsewhere
      "binding_sparse" — top-k at binding layers, skip elsewhere
      "heads_full"     — only binding heads at binding layers, skip elsewhere
      "heads_sparse"   — binding heads + top-k at binding layers, skip elsewhere
    """
    layers = model.model.layers
    n_layers = len(layers)

    heads = BINDING_HEADS if binding_mode == "core" else BINDING_HEADS_EXTENDED

    skip_fn = make_skip_attention_forward()
    sparse_fn = make_sparse_attention_forward(None, top_k)

    for i, layer in enumerate(layers):
        attn = layer.self_attn
        is_binding = i in BINDING_LAYERS

        if level == "full":
            pass  # no changes

        elif level == "sparse":
            _bind_forward(attn, sparse_fn)

        elif level == "binding_full":
            if not is_binding:
                _bind_forward(attn, skip_fn)

        elif level == "binding_sparse":
            if is_binding:
                _bind_forward(attn, sparse_fn)
            else:
                _bind_forward(attn, skip_fn)

        elif level == "heads_full":
            if is_binding:
                active = heads.get(i, [])
                _bind_forward(attn, make_head_masked_attention_forward(active, None))
            else:
                _bind_forward(attn, skip_fn)

        elif level == "heads_sparse":
            if is_binding:
                active = heads.get(i, [])
                _bind_forward(attn, make_head_masked_attention_forward(active, top_k))
            else:
                _bind_forward(attn, skip_fn)

    log(f"    Patched {n_layers} layers with level={level}")


# ═══════════════════════════════════════════════════════════════════════
# Evaluation
# ═══════════════════════════════════════════════════════════════════════


PROBE_TEXTS = [
    # Factual
    "The capital of France is",
    "The speed of light is approximately",
    "Water is composed of two elements:",
    # Reasoning
    "If all dogs are animals and all animals are living things, then all dogs are",
    "The next number in the sequence 2, 4, 8, 16, 32 is",
    # Code
    "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(",
    # Narrative
    "Once upon a time, in a forest deep and dark, there lived a",
    # Lambda / formal
    "In lambda calculus, the identity combinator I = λx.x applied to any term y gives",
    "The composition combinator B = λf.λg.λx.f(g(x)) when applied to f and g produces",
    # Multi-token prediction
    "The quick brown fox jumps over the lazy",
    "To be or not to be, that is the",
    "Machine learning models learn by minimizing a loss function through",
    # Binding test sentences (from s188)
    "The cat sat on the",
    "The dog bit the cat and the cat",
    "She told him that she would",
    "The boy kicked the ball and it",
]


@torch.no_grad()
def get_logits(model, tokenizer, texts, device):
    """Get next-token logits for each text."""
    all_logits = []
    for text in texts:
        inputs = tokenizer(text, return_tensors="pt").to(device)
        outputs = model(**inputs)
        # Last position logits = next token prediction
        last_logits = outputs.logits[0, -1, :]  # (vocab_size,)
        all_logits.append(last_logits.float().cpu())
    return all_logits


def compare_logits(ref_logits, test_logits, tokenizer, texts):
    """Compare test logits against reference. Return hit rates and details."""
    results = []
    for i, (ref, test, text) in enumerate(zip(ref_logits, test_logits, texts)):
        ref_probs = F.softmax(ref, dim=0)
        test_probs = F.softmax(test, dim=0)

        ref_top1 = ref.argmax().item()
        test_top1 = test.argmax().item()

        ref_top10 = ref.topk(10).indices.tolist()
        test_top10 = test.topk(10).indices.tolist()

        ref_top50 = set(ref.topk(50).indices.tolist())
        test_top50 = set(test.topk(50).indices.tolist())

        hit1 = test_top1 == ref_top1
        hit5 = ref_top1 in test.topk(5).indices.tolist()
        hit10 = ref_top1 in test_top10

        # Rank of reference's top-1 in test distribution
        test_sorted = test.argsort(descending=True)
        ref_rank = (test_sorted == ref_top1).nonzero(as_tuple=True)[0]
        ref_rank = ref_rank[0].item() if len(ref_rank) > 0 else -1

        # KL divergence (ref || test) on top-100 tokens
        top100_idx = ref.topk(100).indices
        ref_p = ref_probs[top100_idx]
        test_p = test_probs[top100_idx]
        # Clamp for numerical stability
        kl = (ref_p * (torch.log(ref_p.clamp(min=1e-10)) - torch.log(test_p.clamp(min=1e-10)))).sum().item()

        # Top-50 overlap (Jaccard)
        overlap = len(ref_top50 & test_top50) / len(ref_top50 | test_top50)

        results.append({
            "text": text[:60],
            "hit1": hit1,
            "hit5": hit5,
            "hit10": hit10,
            "ref_rank_in_test": ref_rank,
            "kl_div": kl,
            "top50_overlap": overlap,
            "ref_token": tokenizer.decode([ref_top1]),
            "test_token": tokenizer.decode([test_top1]),
        })

    return results


@torch.no_grad()
def evaluate_ppl(model, tokenizer, max_eval_tokens=8192, device="mps"):
    """Quick PPL on WikiText-2."""
    try:
        from datasets import load_dataset
        ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
        texts = [t for t in ds["text"] if t.strip()]
    except Exception:
        texts = PROBE_TEXTS
        log("    (WikiText-2 unavailable, using probe texts)")

    full_text = "\n\n".join(texts)
    encodings = tokenizer(full_text, return_tensors="pt", truncation=False)
    input_ids = encodings.input_ids[0]
    seq_len = min(input_ids.size(0), max_eval_tokens)
    input_ids = input_ids[:seq_len]

    nlls, n_tokens = [], 0
    stride, max_length = 256, 512

    for begin_loc in range(0, seq_len - 1, stride):
        end_loc = min(begin_loc + max_length, seq_len)
        score_begin = stride if begin_loc > 0 else 0
        chunk = input_ids[begin_loc:end_loc].unsqueeze(0).to(device)
        logits = model(chunk).logits
        shift_logits = logits[0, score_begin:-1, :].contiguous()
        shift_labels = chunk[0, score_begin + 1:].contiguous()
        loss = F.cross_entropy(shift_logits, shift_labels, reduction="sum")
        nlls.append(loss.float().cpu().item())
        n_tokens += shift_labels.size(0)
        if end_loc >= seq_len:
            break

    nll = sum(nlls) / n_tokens
    ppl = math.exp(min(nll, 20))
    return ppl, nll, n_tokens


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════


LEVELS = [
    ("full",            "Full model (baseline)"),
    ("sparse",          "Sparse top-3 at ALL layers"),
    ("binding_full",    "Full attn at L27/L30/L33 only, skip others"),
    ("binding_sparse",  "Sparse top-3 at L27/L30/L33 only"),
    ("heads_full",      "Binding heads only at L27/L30/L33"),
    ("heads_sparse",    "Binding heads + sparse at L27/L30/L33 (λ-machine)"),
]


def main():
    parser = argparse.ArgumentParser(description="λ-Machine Test")
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--skip-ppl", action="store_true")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log(f"╔{'═' * 76}╗")
    log(f"║  λ-MACHINE — Typed Shift-Reduce β-Reducer{' ' * 33}║")
    log(f"║  The minimal algorithm: FFN beamforms, ~4 heads bind, 3 layers reduce{' ' * 5}║")
    log(f"║  Model: {args.model:<67}║")
    log(f"║  Sparse top-k: {args.top_k:<60}║")
    log(f"╚{'═' * 76}╝")

    t_start = time.time()

    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.model, padding_side="left")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    all_results = {}

    for level_name, level_desc in LEVELS:
        log(f"\n{'═' * 78}")
        log(f"  LEVEL: {level_name} — {level_desc}")
        log(f"{'═' * 78}")

        # Load fresh model for each level
        log(f"  Loading fresh model...")
        model = AutoModelForCausalLM.from_pretrained(
            args.model, torch_dtype=torch.float16, device_map=args.device,
        )
        model.eval()

        # Get reference logits before patching (only for "full" level)
        if level_name == "full":
            log(f"  Collecting reference logits...")
            ref_logits = get_logits(model, tokenizer, PROBE_TEXTS, args.device)
            all_results["ref_logits_collected"] = True

        # Patch the model
        if level_name != "full":
            patch_model(model, level_name, top_k=args.top_k)

        # Get test logits
        log(f"  Collecting logits...")
        test_logits = get_logits(model, tokenizer, PROBE_TEXTS, args.device)

        # Compare against reference
        if level_name == "full":
            # Self-comparison (should be perfect)
            comparison = compare_logits(ref_logits, test_logits, tokenizer, PROBE_TEXTS)
        else:
            comparison = compare_logits(ref_logits, test_logits, tokenizer, PROBE_TEXTS)

        # Summary stats
        hit1 = sum(1 for r in comparison if r["hit1"]) / len(comparison) * 100
        hit5 = sum(1 for r in comparison if r["hit5"]) / len(comparison) * 100
        hit10 = sum(1 for r in comparison if r["hit10"]) / len(comparison) * 100
        mean_rank = np.mean([r["ref_rank_in_test"] for r in comparison])
        median_rank = np.median([r["ref_rank_in_test"] for r in comparison])
        mean_kl = np.mean([r["kl_div"] for r in comparison])
        mean_overlap = np.mean([r["top50_overlap"] for r in comparison])

        log(f"\n  Hit@1:  {hit1:.0f}%  ({sum(1 for r in comparison if r['hit1'])}/{len(comparison)})")
        log(f"  Hit@5:  {hit5:.0f}%")
        log(f"  Hit@10: {hit10:.0f}%")
        log(f"  Mean rank of ref top-1: {mean_rank:.1f}  (median: {median_rank:.0f})")
        log(f"  Mean KL(ref||test): {mean_kl:.4f}")
        log(f"  Top-50 overlap: {mean_overlap:.3f}")

        # Per-prompt details
        log(f"\n  Per-prompt:")
        log(f"  {'#':>2} {'Hit':>3} {'Rank':>5} {'Ref→':>12} {'Test→':>12} {'Text'}")
        for j, r in enumerate(comparison):
            hit_str = "✓" if r["hit1"] else ("~" if r["hit5"] else "✗")
            log(f"  {j:>2}   {hit_str:>1}  {r['ref_rank_in_test']:>5} "
                f"{r['ref_token']:>12} {r['test_token']:>12} {r['text'][:45]}")

        # PPL
        if not args.skip_ppl:
            log(f"\n  Evaluating PPL...")
            ppl, nll, n_tokens = evaluate_ppl(model, tokenizer, device=args.device)
            log(f"  PPL: {ppl:.2f}  NLL: {nll:.4f}")
        else:
            ppl, nll = None, None

        all_results[level_name] = {
            "description": level_desc,
            "hit1_pct": hit1,
            "hit5_pct": hit5,
            "hit10_pct": hit10,
            "mean_rank": float(mean_rank),
            "median_rank": float(median_rank),
            "mean_kl": float(mean_kl),
            "top50_overlap": float(mean_overlap),
            "ppl": ppl,
            "nll": nll,
            "per_prompt": comparison,
        }

        del model
        gc.collect()
        if args.device == "mps":
            torch.mps.empty_cache()

    # ── Final comparison ──
    log(f"\n{'═' * 78}")
    log(f"  FINAL COMPARISON — λ-Machine Ablation Levels")
    log(f"{'═' * 78}")
    log(f"  {'Level':<20} {'Hit@1':>6} {'Hit@5':>6} {'Hit@10':>7} {'MedRank':>8} {'KL':>8} {'PPL':>10}")
    log(f"  {'─' * 20} {'─' * 6} {'─' * 6} {'─' * 7} {'─' * 8} {'─' * 8} {'─' * 10}")

    for level_name, level_desc in LEVELS:
        r = all_results[level_name]
        ppl_str = f"{r['ppl']:.1f}" if r['ppl'] is not None else "skip"
        log(f"  {level_name:<20} {r['hit1_pct']:>5.0f}% {r['hit5_pct']:>5.0f}% "
            f"{r['hit10_pct']:>6.0f}% {r['median_rank']:>7.0f} "
            f"{r['mean_kl']:>8.4f} {ppl_str:>10}")

    # Save
    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    elapsed = time.time() - t_start
    log(f"\n{'═' * 78}")
    log(f"  COMPLETE — {elapsed:.0f}s total")
    log(f"  Results: {RESULTS_DIR}/")
    log(f"{'═' * 78}")


if __name__ == "__main__":
    main()
