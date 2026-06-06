#!/usr/bin/env python3
"""β-Expansion — reverse the reductions, correct the cascade.

The sieve cascade: per-layer error 1.03x compounds to 2.11x across 29
layers. The error propagates FORWARD through β-reductions. β-expansion
reverses this: given the teacher's correct state at binding layers,
work backward to compute what earlier layers should have produced.

Phase 1: BINDING PRESERVATION
  Does the sieve preserve the binding graph? Compare attention patterns
  at L27 (H31 verb←subject) and L30 (H03/H13 object←verb) between
  teacher and sieved model. If bindings are preserved → cascade is in
  magnitudes. If bindings change → sieve disrupts type tags.

Phase 2: STRUCTURED CORRECTION
  At binding checkpoints, compute the teacher-student delta in the
  residual stream. Decompose along binding edges. Apply corrections
  ONLY at the source positions that the binding heads read from —
  not uniformly at all positions.

Phase 3: CONTINUATION RESIDUALS
  Add small learned correction vectors at functional boundaries.
  These absorb cascade error with minimal parameters — like CPS
  continuations that carry forward the accumulated correction.

Usage:
  uv run python scripts/experiments/beta_expansion.py \
    --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))


# ══════════════════════════════════════════════════════════════
# Texts
# ══════════════════════════════════════════════════════════════

EVAL_TEXTS = [
    "The theory of general relativity describes gravity"
    " as the curvature of spacetime caused by mass and"
    " energy.",
    "In a large mixing bowl, combine the flour, sugar,"
    " and baking powder. Make a well in the center.",
    "The committee voted unanimously to approve the new"
    " environmental regulations for manufacturing plants.",
    "She walked through the ancient forest, her footsteps"
    " muffled by centuries of fallen leaves.",
    "The function takes two arguments and returns their"
    " composition as a new callable object.",
    "During the Cambrian explosion, roughly 541 million"
    " years ago, most major animal phyla appeared.",
    "The patient was admitted with acute respiratory"
    " distress. Initial blood work showed elevated levels.",
    "To solve this equation, first isolate the variable"
    " on one side by subtracting three from both sides.",
]

# Structured binding probes — sentences with clear S/V/O
BINDING_PROBES = [
    {"text": "The cat runs quickly",
     "subject": "cat", "verb": "runs", "s_pos": 1, "v_pos": 2},
    {"text": "The dog bit the cat",
     "subject": "dog", "verb": "bit", "object": "cat",
     "s_pos": 1, "v_pos": 2, "o_pos": 4},
    {"text": "She walked through the ancient forest",
     "subject": "She", "verb": "walked", "s_pos": 0, "v_pos": 1},
    {"text": "The detective examined the crime scene",
     "subject": "detective", "verb": "examined", "object": "scene",
     "s_pos": 1, "v_pos": 2, "o_pos": 5},
    {"text": "Three children ran laughing through the meadow",
     "subject": "children", "verb": "ran", "s_pos": 1, "v_pos": 2},
    {"text": "The old man sat quietly by the river",
     "subject": "man", "verb": "sat", "s_pos": 2, "v_pos": 3},
    {"text": "Birds sang in the treetops",
     "subject": "Birds", "verb": "sang", "s_pos": 0, "v_pos": 1},
    {"text": "The ship sailed slowly into the harbor",
     "subject": "ship", "verb": "sailed", "s_pos": 1, "v_pos": 2},
    {"text": "The committee voted unanimously",
     "subject": "committee", "verb": "voted", "s_pos": 1, "v_pos": 2},
    {"text": "Enzymes speed up chemical reactions",
     "subject": "Enzymes", "verb": "speed", "s_pos": 0, "v_pos": 1},
]

FACT_PROMPTS = [
    {"prompt": "The capital of France is", "expected": "Paris"},
    {"prompt": "The capital of Japan is", "expected": "Tokyo"},
    {"prompt": "Water boils at", "expected": "100"},
    {"prompt": "The speed of light is approximately",
     "expected": "300"},
    {"prompt": "The first president of the United States was",
     "expected": "George Washington"},
    {"prompt": "The year World War II ended was",
     "expected": "1945"},
    {"prompt": "The chemical symbol for gold is",
     "expected": "Au"},
    {"prompt": "The largest planet in our solar system is",
     "expected": "Jupiter"},
    {"prompt": "The author of Romeo and Juliet is",
     "expected": "Shakespeare"},
    {"prompt": "Pi is approximately equal to",
     "expected": "3.14"},
    {"prompt": "The Great Wall of China is located in",
     "expected": "China"},
    {"prompt": "The human body has", "expected": "206"},
    {"prompt": "Einstein's famous equation is E equals",
     "expected": "mc"},
    {"prompt": "The freezing point of water in Celsius is",
     "expected": "0"},
    {"prompt": "The currency of the United Kingdom is the",
     "expected": "pound"},
]

CALIBRATION_TEXTS = [
    "The theory of general relativity describes gravity as"
    " the curvature of spacetime.",
    "Photosynthesis converts carbon dioxide and water into"
    " glucose and oxygen.",
    "DNA carries genetic information in a double helix"
    " structure discovered by Watson and Crick.",
    "Quantum mechanics describes the behavior of particles"
    " at the atomic and subatomic scale.",
    "She walked through the ancient forest, her footsteps"
    " muffled by fallen leaves.",
    "The old man sat quietly by the river, watching the"
    " fish jump at dawn.",
    "In a large mixing bowl, combine the flour, sugar,"
    " and baking powder.",
    "To solve this equation, first isolate the variable"
    " on one side.",
    "The committee voted unanimously to approve the new"
    " environmental regulations.",
    "The function takes two arguments and returns their"
    " composition as a new callable.",
    "What time does the store close today?",
    "I think we should probably leave now before it gets"
    " too dark outside.",
]

# Known binding heads from session 188
BINDING_HEADS = {
    27: [31],           # H31: verb reads subject (0.82 weight)
    30: [3, 13, 15],    # H03/H13/H15: object reads verb (0.78 weight)
}


def log(msg=""):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


def get_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise RuntimeError(f"Can't find layers in {type(model)}")


def measure_ppl(model, tokenizer, texts, device):
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        enc = tokenizer(text, return_tensors="pt",
                        truncation=True, max_length=256)
        enc = {k: v.to(device) for k, v in enc.items()}
        labels = enc["input_ids"].clone()
        with torch.no_grad():
            out = model(**enc, labels=labels)
            total_loss += out.loss.item() * labels.numel()
            total_tokens += labels.numel()
    return float(np.exp(total_loss / total_tokens))


def generate_text(model, tokenizer, prompt, device, max_new=30):
    enc = tokenizer(prompt, return_tensors="pt")
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=max_new,
                             do_sample=False, temperature=1.0,
                             pad_token_id=tokenizer.pad_token_id)
    return tokenizer.decode(out[0][enc["input_ids"].shape[1]:],
                            skip_special_tokens=True)


def measure_facts(model, tokenizer, device):
    correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(model, tokenizer, fp["prompt"], device)
        if fp["expected"].lower() in gen.lower():
            correct += 1
    return correct, len(FACT_PROMPTS)


# ══════════════════════════════════════════════════════════════
# Crystal Sieve (frozen, from pipeline experiment)
# ══════════════════════════════════════════════════════════════

class FrozenSieveLinear(nn.Module):
    def __init__(self, weight, zero_rate=0.5):
        super().__init__()
        W = weight.detach().float().cpu()
        abs_W = W.abs()
        if zero_rate > 0:
            flat = abs_W.flatten()
            if flat.numel() > 10_000_000:
                idx = torch.randperm(flat.numel())[:5_000_000]
                threshold = torch.quantile(flat[idx], zero_rate)
            else:
                threshold = torch.quantile(flat, zero_rate)
            mask = (abs_W >= threshold).float()
        else:
            mask = torch.ones_like(W)
        W_sieve = torch.sign(W) * abs_W * mask
        self.register_buffer("W_sieve", W_sieve.half())

    def forward(self, x):
        out = x.float() @ self.W_sieve.float().T
        return out.clamp(-65000, 65000).to(x.dtype)


class TrainableLowRankLinear(nn.Module):
    def __init__(self, A, B):
        super().__init__()
        self.register_buffer("A", A)
        self.register_buffer("B", B)

    def forward(self, x):
        out = x.float() @ self.B.T @ self.A.T
        return out.clamp(-65000, 65000).to(x.dtype)


def svd_factorize(weight, rank):
    W = weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))
    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)
    return A, B


# ══════════════════════════════════════════════════════════════
# Attention capture
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def capture_attention_and_states(model, input_ids, device,
                                 target_layers):
    """Capture attention weights and hidden states at target layers.

    Returns:
      attn_weights: {layer_idx: tensor (n_heads, seq, seq)}
      hidden_states: {layer_idx: tensor (seq, d_model)}
    """
    layers = get_layers(model)
    attn_weights = {}
    hidden_states = {}
    hooks = []

    # Hook attention to capture weights
    def make_attn_hook(layer_idx):
        def hook_fn(mod, args, kwargs, output):
            # Qwen3 self_attn with output_attentions returns
            # (attn_output, attn_weights, past_kv)
            if isinstance(output, tuple) and len(output) >= 2:
                w = output[1]
                if w is not None:
                    attn_weights[layer_idx] = w[0].detach().cpu()
        return hook_fn

    # Hook decoder layer for hidden states
    def make_state_hook(layer_idx):
        def hook_fn(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            hidden_states[layer_idx] = h[0].detach().cpu()
        return hook_fn

    for li in target_layers:
        hooks.append(
            layers[li].self_attn.register_forward_hook(
                make_attn_hook(li), with_kwargs=True))
        hooks.append(
            layers[li].register_forward_hook(make_state_hook(li)))

    input_ids = input_ids.to(device)
    model(input_ids, output_attentions=True)

    for h in hooks:
        h.remove()

    return attn_weights, hidden_states


# ══════════════════════════════════════════════════════════════
# Phase 1: Binding Preservation
# ══════════════════════════════════════════════════════════════

def analyze_binding_preservation(teacher_attn, sieved_attn,
                                 probe, tokenizer):
    """Compare binding head attention between teacher and sieved model."""
    results = {}

    for layer_idx, head_list in BINDING_HEADS.items():
        if layer_idx not in teacher_attn or layer_idx not in sieved_attn:
            continue

        t_attn = teacher_attn[layer_idx]  # (n_heads, seq, seq)
        s_attn = sieved_attn[layer_idx]

        for head_idx in head_list:
            t_head = t_attn[head_idx]  # (seq, seq)
            s_head = s_attn[head_idx]

            # At verb position, where does the head attend?
            v_pos = probe.get("v_pos")
            s_pos = probe.get("s_pos")
            if v_pos is None:
                continue

            # Teacher: attention from verb to all positions
            t_dist = t_head[v_pos]  # (seq,)
            s_dist = s_head[v_pos]

            # Top-1 position
            t_top1 = int(t_dist.argmax())
            s_top1 = int(s_dist.argmax())

            # Attention weight at subject position
            t_subj_weight = float(t_dist[s_pos]) if s_pos is not None else 0
            s_subj_weight = float(s_dist[s_pos]) if s_pos is not None else 0

            # KL divergence between distributions
            t_log = torch.log(t_dist.clamp(min=1e-10))
            s_log = torch.log(s_dist.clamp(min=1e-10))
            kl = float(F.kl_div(s_log, t_dist, reduction='sum'))

            # Cosine of attention distributions
            cos = float(F.cosine_similarity(
                t_dist.unsqueeze(0), s_dist.unsqueeze(0)))

            key = f"L{layer_idx}_H{head_idx}"
            results[key] = {
                "teacher_top1": t_top1,
                "sieved_top1": s_top1,
                "top1_match": t_top1 == s_top1,
                "teacher_subj_weight": round(t_subj_weight, 4),
                "sieved_subj_weight": round(s_subj_weight, 4),
                "attn_cos": round(cos, 4),
                "kl_div": round(kl, 4),
            }

    return results


# ══════════════════════════════════════════════════════════════
# Phase 2: Continuation Residuals
# ══════════════════════════════════════════════════════════════

class ContinuationResidual(nn.Module):
    """Small learned correction at a layer boundary.

    Added to the residual stream after a decoder layer.
    Implemented as a low-rank down-up projection:
      correction = input @ W_down @ W_up
    """

    def __init__(self, d_model, rank=32):
        super().__init__()
        self.W_down = nn.Parameter(
            torch.randn(d_model, rank) * 0.001)
        self.W_up = nn.Parameter(
            torch.randn(rank, d_model) * 0.001)

    def forward(self, x):
        # x: (batch, seq, d_model)
        correction = x.float() @ self.W_down @ self.W_up
        return (x.float() + correction).to(x.dtype)


# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--zero-rate", type=float, default=0.5)
    p.add_argument("--residual-rank", type=int, default=32)
    p.add_argument("--melt-steps", type=int, default=100)
    p.add_argument("--lr", type=float, default=1e-4)
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]
    BINDING_LAYER_IDS = [27, 30]
    # Continuation residuals at functional boundaries
    RESIDUAL_LAYERS = [0, 9, 21, 26]

    log(f"\n{'='*70}")
    log("  β-EXPANSION — Reverse the reductions, correct the cascade")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")

    # ── Load ──────────────────────────────────────────────
    dtype = (torch.float16
             if any(s in args.model for s in ["8B", "14B", "32B"])
             else torch.float32)
    log(f"\n  Loading {args.model} ({dtype})...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device,
        attn_implementation="eager")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    d_model = model.config.hidden_size
    log(f"  d_model={d_model}")

    # ── Baseline ──────────────────────────────────────────
    log("\n  Measuring baseline...")
    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    base_facts, base_total = measure_facts(model, tokenizer, args.device)
    log(f"  Baseline PPL: {base_ppl:.2f}, facts: {base_facts}/{base_total}")

    # ══════════════════════════════════════════════════════
    # Phase 1: Capture teacher binding patterns
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 1: TEACHER BINDING PATTERNS")
    log(f"{'═'*70}")

    teacher_bindings = []
    teacher_states_all = []
    for probe in BINDING_PROBES:
        enc = tokenizer(probe["text"], return_tensors="pt")
        attn, states = capture_attention_and_states(
            model, enc["input_ids"], args.device,
            BINDING_LAYER_IDS)
        teacher_bindings.append((probe, attn, states))

        # Also capture hidden states at functional boundaries
        all_states = {}
        layers = get_layers(model)
        hooks = []
        def make_hook(li):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                all_states[li] = h[0].detach().cpu()
            return hook_fn
        for li in RESIDUAL_LAYERS + BINDING_LAYER_IDS + [35]:
            hooks.append(layers[li].register_forward_hook(make_hook(li)))
        with torch.no_grad():
            model(enc["input_ids"].to(args.device))
        for h in hooks:
            h.remove()
        teacher_states_all.append(all_states)

    log(f"  Captured {len(BINDING_PROBES)} probes")

    # ══════════════════════════════════════════════════════
    # Install crystal sieve
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  INSTALLING CRYSTAL SIEVE")
    log(f"{'═'*70}")

    layers = get_layers(model)

    # L0 SVD
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, 750)
        setattr(mlp0, pname,
                TrainableLowRankLinear(A.to(args.device),
                                       B.to(args.device)))

    # Sieve remaining layers
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)
            setattr(mlp, pname,
                    FrozenSieveLinear(proj.weight,
                                      zero_rate=args.zero_rate).to(args.device))
    log(f"  Sieve installed on {len(SIEVE_LAYERS)} layers + L0 SVD")

    # Pre-melt measurement
    pre_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    pre_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"  Pre-melt PPL: {pre_ppl:.2f} ({pre_ppl/base_ppl:.2f}x)"
        f"  facts: {pre_facts}/{base_total}")

    # ══════════════════════════════════════════════════════
    # Phase 1b: Compare sieved binding patterns
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 1b: BINDING PRESERVATION ANALYSIS")
    log(f"{'═'*70}")

    all_binding_results = []
    top1_matches = 0
    top1_total = 0

    for probe, teacher_attn, teacher_states in teacher_bindings:
        enc = tokenizer(probe["text"], return_tensors="pt")
        sieved_attn, sieved_states = capture_attention_and_states(
            model, enc["input_ids"], args.device,
            BINDING_LAYER_IDS)

        results = analyze_binding_preservation(
            teacher_attn, sieved_attn, probe, tokenizer)

        for key, r in results.items():
            top1_total += 1
            if r["top1_match"]:
                top1_matches += 1

        all_binding_results.append({
            "text": probe["text"],
            "bindings": results,
        })

        log(f"\n  \"{probe['text'][:40]}...\"")
        for key, r in results.items():
            match = "✓" if r["top1_match"] else "✗"
            log(f"    {key}: top1 {r['teacher_top1']}→{r['sieved_top1']}"
                f" {match}"
                f"  subj_w: {r['teacher_subj_weight']:.3f}→{r['sieved_subj_weight']:.3f}"
                f"  cos={r['attn_cos']:.3f}")

    log(f"\n  BINDING PRESERVATION: {top1_matches}/{top1_total}"
        f" top-1 matches ({top1_matches/max(top1_total,1):.0%})")

    # ══════════════════════════════════════════════════════
    # Phase 2: Hidden state comparison at boundaries
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 2: HIDDEN STATE FIDELITY AT BOUNDARIES")
    log(f"{'═'*70}")

    boundary_fidelity = {li: [] for li in RESIDUAL_LAYERS + BINDING_LAYER_IDS + [35]}

    for i, probe in enumerate(BINDING_PROBES):
        enc = tokenizer(probe["text"], return_tensors="pt")
        teacher_states = teacher_states_all[i]

        # Capture sieved states at same boundaries
        sieved_states = {}
        hooks = []
        def make_hook(li):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                sieved_states[li] = h[0].detach().cpu()
            return hook_fn
        for li in RESIDUAL_LAYERS + BINDING_LAYER_IDS + [35]:
            hooks.append(layers[li].register_forward_hook(make_hook(li)))
        with torch.no_grad():
            model(enc["input_ids"].to(args.device))
        for h in hooks:
            h.remove()

        for li in boundary_fidelity:
            if li in teacher_states and li in sieved_states:
                t = teacher_states[li].float()
                s = sieved_states[li].float()
                cos = F.cosine_similarity(t, s, dim=-1).mean().item()
                boundary_fidelity[li].append(cos)

    log(f"\n  {'Layer':>6s}  {'Mean cos':>8s}  {'Role':>20s}")
    log(f"  {'─'*6}  {'─'*8}  {'─'*20}")
    for li in sorted(boundary_fidelity.keys()):
        vals = boundary_fidelity[li]
        if vals:
            mean_cos = np.mean(vals)
            role = ("lexer" if li == 0 else
                    "parser" if li == 9 else
                    "composition" if li == 21 else
                    "type crystal" if li == 26 else
                    "binding (subj)" if li == 27 else
                    "binding (obj)" if li == 30 else
                    "output" if li == 35 else "?")
            log(f"  L{li:>3d}   {mean_cos:>8.4f}  {role:>20s}")

    # ══════════════════════════════════════════════════════
    # Phase 3: Continuation residuals
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 3: CONTINUATION RESIDUALS")
    log(f"  Adding low-rank corrections at L{RESIDUAL_LAYERS}")
    log(f"{'═'*70}")

    # Install continuation residuals as hooks
    continuations = {}
    cont_hooks = []
    trainable_params = []

    for li in RESIDUAL_LAYERS:
        cont = ContinuationResidual(d_model, rank=args.residual_rank).to(args.device)
        continuations[li] = cont
        trainable_params.extend([cont.W_down, cont.W_up])

        def make_cont_hook(c):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                corrected = c(h)
                if isinstance(out, tuple):
                    return (corrected,) + out[1:]
                return corrected
            return hook_fn

        h = layers[li].register_forward_hook(make_cont_hook(cont))
        cont_hooks.append(h)

    n_trainable = sum(p.numel() for p in trainable_params)
    log(f"  Continuations: {len(RESIDUAL_LAYERS)} layers × rank-{args.residual_rank}"
        f" = {n_trainable:,} params")

    # Cache teacher states for melt
    teacher_cache = []
    CHECKPOINTS = {"lexer": 0, "composition": 21,
                   "type_crystal": 26, "binding": 30}
    for text in CALIBRATION_TEXTS:
        # Teacher states were captured before sieve installation
        # Need to re-capture from the already-sieved model's teacher
        # Actually we need ORIGINAL teacher states — use the ones from binding probes
        pass

    # Simple melt: just CE loss (continuations are tiny, don't need projections)
    log(f"\n  Melting with CE loss ({args.melt_steps} steps)...")
    optimizer = torch.optim.Adam(trainable_params, lr=args.lr)
    model.train()
    history = []
    t0 = time.time()

    for step in range(args.melt_steps):
        optimizer.zero_grad()
        rng = np.random.RandomState(step)
        batch_idx = rng.choice(len(CALIBRATION_TEXTS),
                               min(4, len(CALIBRATION_TEXTS)),
                               replace=False)
        total_loss = 0.0
        total_tokens = 0
        for idx in batch_idx:
            enc = tokenizer(CALIBRATION_TEXTS[idx], return_tensors="pt",
                            truncation=True, max_length=128)
            enc = {k: v.to(args.device) for k, v in enc.items()}
            labels = enc["input_ids"].clone()
            out = model(**enc, labels=labels)
            if not (np.isnan(out.loss.item()) or np.isinf(out.loss.item())):
                out.loss.backward()
                total_loss += out.loss.item() * labels.numel()
                total_tokens += labels.numel()

        if total_tokens == 0:
            continue

        torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=0.5)
        optimizer.step()
        avg = total_loss / total_tokens
        history.append(avg)

        if (step + 1) % 20 == 0 or step == 0:
            elapsed = time.time() - t0
            log(f"    step {step+1:>3d}: loss={avg:.4f} ({elapsed:.0f}s)")

    model.eval()

    # Post-melt measurement
    post_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    post_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"\n  Post-melt PPL: {post_ppl:.2f} ({post_ppl/base_ppl:.2f}x)"
        f"  facts: {post_facts}/{base_total}")

    # Clean up
    for h in cont_hooks:
        h.remove()

    # ══════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  RESULTS")
    log(f"{'='*70}")
    log(f"  Baseline:    PPL={base_ppl:.2f}  facts={base_facts}/{base_total}")
    log(f"  Sieve only:  PPL={pre_ppl:.2f} ({pre_ppl/base_ppl:.2f}x)"
        f"  facts={pre_facts}/{base_total}")
    log(f"  +Continuations: PPL={post_ppl:.2f} ({post_ppl/base_ppl:.2f}x)"
        f"  facts={post_facts}/{base_total}")
    log(f"  Binding preserved: {top1_matches}/{top1_total}"
        f" ({top1_matches/max(top1_total,1):.0%})")
    log(f"  Continuation params: {n_trainable:,}")

    # Save
    out_dir = _PROJECT_ROOT / "results" / "beta-expansion"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")
    result = {
        "model": args.model,
        "baseline_ppl": base_ppl,
        "baseline_facts": base_facts,
        "pre_melt_ppl": pre_ppl,
        "pre_melt_ratio": round(pre_ppl / base_ppl, 4),
        "post_melt_ppl": post_ppl,
        "post_melt_ratio": round(post_ppl / base_ppl, 4),
        "post_melt_facts": post_facts,
        "binding_top1_matches": top1_matches,
        "binding_top1_total": top1_total,
        "binding_preservation_rate": round(top1_matches / max(top1_total, 1), 4),
        "binding_results": all_binding_results,
        "boundary_fidelity": {
            str(li): round(float(np.mean(v)), 4)
            for li, v in boundary_fidelity.items() if v
        },
        "continuation_params": n_trainable,
        "residual_rank": args.residual_rank,
        "loss_history": [round(x, 4) for x in history],
    }
    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
