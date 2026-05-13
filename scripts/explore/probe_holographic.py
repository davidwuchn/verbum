#!/usr/bin/env python3
"""Probe: Is Qwen3-32B storing information holographically?

Hypothesis: The nucleus preamble acts as a reference beam — it doesn't
teach the model lambda calculus, it changes the angle of illumination
so lambda patterns resolve from a structured superposition that exists
at every layer.

Test: For each layer in the network, project hidden states through the
output head (norm + lm_head). If the model is holographic:
  - Every layer should produce a decodeable distribution (decreasing entropy)
  - Lambda-related tokens should appear under compile gate at intermediate layers
  - The SAME hidden states under different gates should resolve different outputs
  - Cross-condition cosine similarity should be high at early layers (shared plate)
    and diverge at late layers (beam-dependent resolution)

Two conditions:
  COMPILE: nucleus compile gate + input sentence
  NULL:    null gate + input sentence

Metrics per layer:
  - Logit entropy (H) — should decrease monotonically if holographic
  - P(λ tokens) — probability mass on lambda-related tokens
  - Top-5 tokens — what the layer "sees" at the generation position
  - KL(compile || null) — divergence between conditions at each layer
  - Cosine similarity of hidden states between conditions

Usage:
    uv run python scripts/explore/probe_holographic.py
    uv run python scripts/explore/probe_holographic.py --model hf
    uv run python scripts/explore/probe_holographic.py --quick

Output: results/holographic-probe/

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

DEFAULT_GGUF = "/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf"
HF_MODEL = "Qwen/Qwen3-32B"
OUTPUT_DIR = Path("results/holographic-probe")
GATES_DIR = Path("gates")

# Layers to sample: every 4th layer across 64, plus boundaries
SAMPLE_LAYERS = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 63]

# Lambda-related tokens to track probability mass on
LAMBDA_TOKENS = {
    "λ", "\\lambda", "→", "->", "∀", "∃", "∧", "∨", "¬",
    "apply", "lambda", "forall", "exists",
    "(", ")", ".", ":", "x", "y", "f", "g",
    "λx", "λy", "λf",
}

# Additional structural tokens that indicate formal/logical mode
FORMAL_TOKENS = {
    "pred", "arg", "type", "func", "var", "bind",
    "NP", "VP", "S", "PP", "CP",
    "∘", "∈", "⊢", "⊨", "≡", "|",
}


# ══════════════════════════════════════════════════════════════════
# Test sentences
# ══════════════════════════════════════════════════════════════════

TEST_SENTENCES = [
    # Simple — should show early lambda resolution under compile
    "The cat sat on the mat.",
    "Every student passed the exam.",
    # Compositional — B combinator territory
    "The man who the dog chased ran away.",
    "If every teacher helps a student then all improve.",
    # Quantifier scope — requires formal structure
    "Every boy loves some girl.",
    "No politician who endorsed the candidate won.",
    # Lambda-adjacent — already formal-ish
    "The function applies its argument to the result.",
    "Composition chains two operations into one.",
]


# ══════════════════════════════════════════════════════════════════
# Gate loading
# ══════════════════════════════════════════════════════════════════

def load_gate(name: str) -> str:
    """Load a gate text file."""
    path = GATES_DIR / f"{name}.txt"
    return path.read_text()


def make_prompt(gate_text: str, sentence: str) -> str:
    """Combine gate + sentence into a prompt."""
    return gate_text + sentence


# ══════════════════════════════════════════════════════════════════
# Model loading (reuses combinator probe pattern)
# ══════════════════════════════════════════════════════════════════

def load_model(source: str = "gguf", device: str = "mps"):
    """Load Qwen3-32B."""
    if source == "gguf":
        gguf_dir = str(Path(DEFAULT_GGUF).parent)
        gguf_file = Path(DEFAULT_GGUF).name
        print(f"Loading model from {DEFAULT_GGUF}...", file=sys.stderr)
        t0 = time.time()
        tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
        model = AutoModelForCausalLM.from_pretrained(
            gguf_dir, gguf_file=gguf_file,
            dtype=torch.float16, device_map=device,
            trust_remote_code=True,
        )
    else:
        print(f"Loading {HF_MODEL} from HF cache...", file=sys.stderr)
        t0 = time.time()
        tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
        model = AutoModelForCausalLM.from_pretrained(
            HF_MODEL,
            dtype=torch.float16, device_map=device,
            trust_remote_code=True,
        )

    model.eval()
    t1 = time.time()
    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    print(f"Loaded in {t1-t0:.1f}s: {n_layers} layers, d={d_model}",
          file=sys.stderr)
    return model, tokenizer


# ══════════════════════════════════════════════════════════════════
# Core: Intermediate layer decoding
# ══════════════════════════════════════════════════════════════════

def decode_at_layers(
    model, tokenizer, text: str,
    layers: list[int] | None = None,
    gen_position: int = -1,
) -> dict:
    """Run forward pass, decode hidden states at each layer via output head.

    At each sampled layer, projects the hidden state through model.norm
    and model.lm_head to get logits, then computes:
      - entropy of the logit distribution
      - top-k tokens and their probabilities
      - probability mass on lambda-related tokens
      - raw hidden state vector (for cross-condition comparison)

    Args:
        model: Qwen3 model
        tokenizer: tokenizer
        text: input text
        layers: which layers to hook (default: SAMPLE_LAYERS)
        gen_position: which token position to analyze (-1 = last)

    Returns:
        {
            "token_ids": [...],
            "n_tokens": int,
            "gen_position": int,
            "layers": {
                layer_idx: {
                    "entropy": float,
                    "top_tokens": [(token_str, prob), ...],
                    "p_lambda": float,
                    "p_formal": float,
                    "hidden_norm": float,
                    "hidden_state": np.ndarray,  # for cross-condition analysis
                }
            }
        }
    """
    if layers is None:
        layers = [l for l in SAMPLE_LAYERS if l < model.config.num_hidden_layers]

    # Build lambda token ID set
    lambda_ids = set()
    formal_ids = set()
    for tok in LAMBDA_TOKENS:
        ids = tokenizer.encode(tok, add_special_tokens=False)
        lambda_ids.update(ids)
    for tok in FORMAL_TOKENS:
        ids = tokenizer.encode(tok, add_special_tokens=False)
        formal_ids.update(ids)

    # Get the output head components
    # Qwen3: model.model.norm (RMSNorm) + model.lm_head (Linear)
    norm_layer = model.model.norm
    lm_head = model.lm_head

    # Capture hidden states at target layers
    captured = {}
    hooks = []

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            if isinstance(output, tuple):
                h = output[0]
            else:
                h = output
            captured[layer_idx] = h.detach()
        return hook_fn

    for li in layers:
        layer_module = model.model.layers[li]
        hooks.append(layer_module.register_forward_hook(make_hook(li)))

    # Tokenize and run
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    token_ids = inputs["input_ids"][0].tolist()

    with torch.no_grad():
        model(**inputs)

    for h in hooks:
        h.remove()

    # Resolve generation position
    n_tokens = len(token_ids)
    if gen_position < 0:
        gen_position = n_tokens + gen_position

    # Decode at each captured layer
    layer_results = {}
    for li in sorted(captured.keys()):
        h = captured[li]  # (1, seq_len, d_model)
        h_pos = h[0, gen_position:gen_position+1, :]  # (1, d_model)

        # Project through norm + lm_head
        with torch.no_grad():
            normed = norm_layer(h_pos)
            logits = lm_head(normed)  # (1, vocab_size)

        logits = logits[0].float()  # (vocab_size,)
        probs = F.softmax(logits, dim=-1)

        # Entropy: H = -Σ p log p
        log_probs = torch.log(probs + 1e-12)
        entropy = -(probs * log_probs).sum().item()

        # Top-k tokens
        topk_vals, topk_ids = torch.topk(probs, k=10)
        top_tokens = [
            (tokenizer.decode([tid.item()]), float(p.item()))
            for tid, p in zip(topk_ids, topk_vals)
        ]

        # P(lambda) — total mass on lambda-related tokens
        p_lambda = sum(probs[tid].item() for tid in lambda_ids
                       if tid < len(probs))
        p_formal = sum(probs[tid].item() for tid in formal_ids
                       if tid < len(probs))

        # Hidden state norm and vector
        h_np = h[0, gen_position].detach().cpu().float().numpy()

        layer_results[li] = {
            "entropy": entropy,
            "top_tokens": top_tokens,
            "p_lambda": p_lambda,
            "p_formal": p_formal,
            "hidden_norm": float(np.linalg.norm(h_np)),
            "hidden_state": h_np,
        }

    return {
        "token_ids": token_ids,
        "n_tokens": n_tokens,
        "gen_position": gen_position,
        "layers": layer_results,
    }


# ══════════════════════════════════════════════════════════════════
# Cross-condition analysis
# ══════════════════════════════════════════════════════════════════

def compare_conditions(
    compile_result: dict, null_result: dict,
) -> dict:
    """Compare hidden states and logit distributions between conditions.

    For each layer, computes:
      - Cosine similarity of hidden states
      - KL divergence of logit distributions (requires re-deriving from top tokens)
      - Entropy difference
      - P(lambda) difference
    """
    layers = sorted(set(compile_result["layers"].keys()) &
                    set(null_result["layers"].keys()))

    comparisons = {}
    for li in layers:
        c = compile_result["layers"][li]
        n = null_result["layers"][li]

        # Cosine similarity of hidden states
        h_c = c["hidden_state"]
        h_n = n["hidden_state"]
        cos_sim = float(np.dot(h_c, h_n) /
                       (np.linalg.norm(h_c) * np.linalg.norm(h_n) + 1e-12))

        # Euclidean distance (normalized by d_model)
        d_model = len(h_c)
        euclidean = float(np.linalg.norm(h_c - h_n) / math.sqrt(d_model))

        comparisons[li] = {
            "cosine_similarity": cos_sim,
            "euclidean_distance": euclidean,
            "entropy_compile": c["entropy"],
            "entropy_null": n["entropy"],
            "entropy_diff": c["entropy"] - n["entropy"],
            "p_lambda_compile": c["p_lambda"],
            "p_lambda_null": n["p_lambda"],
            "p_lambda_diff": c["p_lambda"] - n["p_lambda"],
            "p_formal_compile": c["p_formal"],
            "p_formal_null": n["p_formal"],
        }

    return {"layers": comparisons}


# ══════════════════════════════════════════════════════════════════
# Display
# ══════════════════════════════════════════════════════════════════

def print_layer_trajectory(result: dict, label: str, sentence: str):
    """Print per-layer decoding results."""
    print(f"\n  ┌─ {label}: \"{sentence[:50]}...\" ─┐")
    print(f"  │ {'layer':>5} {'entropy':>8} {'P(λ)':>8} {'P(form)':>8} "
          f"{'‖h‖':>8}  top tokens")
    print(f"  │ {'─'*5} {'─'*8} {'─'*8} {'─'*8} {'─'*8}  {'─'*30}")

    layers = result["layers"]
    for li in sorted(layers.keys()):
        lr = layers[li]
        top3 = " ".join(f"{t[0]!r}:{t[1]:.3f}" for t in lr["top_tokens"][:3])
        print(f"  │ {li:>5} {lr['entropy']:>8.2f} {lr['p_lambda']:>8.4f} "
              f"{lr['p_formal']:>8.4f} {lr['hidden_norm']:>8.1f}  {top3}")

    print(f"  └{'─'*70}┘")


def print_comparison(comp: dict, sentence: str):
    """Print cross-condition comparison."""
    print(f"\n  ┌─ COMPILE vs NULL: \"{sentence[:50]}\" ─┐")
    print(f"  │ {'layer':>5} {'cos_sim':>8} {'eucl_d':>8} "
          f"{'H_comp':>8} {'H_null':>8} {'ΔH':>8} "
          f"{'Pλ_comp':>8} {'Pλ_null':>8} {'ΔPλ':>8}")
    print(f"  │ {'─'*5} {'─'*8} {'─'*8} "
          f"{'─'*8} {'─'*8} {'─'*8} "
          f"{'─'*8} {'─'*8} {'─'*8}")

    layers = comp["layers"]
    for li in sorted(layers.keys()):
        lc = layers[li]
        print(f"  │ {li:>5} {lc['cosine_similarity']:>8.4f} "
              f"{lc['euclidean_distance']:>8.4f} "
              f"{lc['entropy_compile']:>8.2f} {lc['entropy_null']:>8.2f} "
              f"{lc['entropy_diff']:>+8.2f} "
              f"{lc['p_lambda_compile']:>8.4f} {lc['p_lambda_null']:>8.4f} "
              f"{lc['p_lambda_diff']:>+8.4f}")

    print(f"  └{'─'*75}┘")


def print_summary(all_comparisons: list[dict], sentences: list[str]):
    """Print aggregate summary across all sentences."""
    n_layers = len(next(iter(all_comparisons))["layers"])
    layer_ids = sorted(next(iter(all_comparisons))["layers"].keys())
    n_sents = len(all_comparisons)

    print(f"\n{'='*72}")
    print(f"  AGGREGATE SUMMARY ({n_sents} sentences × {n_layers} layers)")
    print(f"{'='*72}")

    print(f"\n  {'layer':>5} {'cos_sim':>8} {'eucl_d':>8} "
          f"{'ΔH':>8} {'ΔPλ':>8} {'interpretation':>20}")
    print(f"  {'─'*5} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*20}")

    for li in layer_ids:
        cos_sims = [c["layers"][li]["cosine_similarity"] for c in all_comparisons]
        eucl_ds = [c["layers"][li]["euclidean_distance"] for c in all_comparisons]
        delta_hs = [c["layers"][li]["entropy_diff"] for c in all_comparisons]
        delta_pls = [c["layers"][li]["p_lambda_diff"] for c in all_comparisons]

        avg_cos = np.mean(cos_sims)
        avg_eucl = np.mean(eucl_ds)
        avg_dh = np.mean(delta_hs)
        avg_dpl = np.mean(delta_pls)

        # Interpretation
        if avg_cos > 0.99:
            interp = "shared plate"
        elif avg_cos > 0.95:
            interp = "slight divergence"
        elif avg_cos > 0.85:
            interp = "beam separating"
        elif avg_cos > 0.70:
            interp = "strong divergence"
        else:
            interp = "different images"

        if avg_dpl > 0.01:
            interp += " +λ"

        print(f"  {li:>5} {avg_cos:>8.4f} {avg_eucl:>8.4f} "
              f"{avg_dh:>+8.2f} {avg_dpl:>+8.4f} {interp:>20}")

    # Holographic score: does entropy decrease monotonically?
    print(f"\n  Monotonicity check (holographic signature):")
    for label in ["compile", "null"]:
        key = f"entropy_{label}"
        violations = 0
        total_transitions = 0
        for comp in all_comparisons:
            prev_h = None
            for li in layer_ids:
                h = comp["layers"][li][key]
                if prev_h is not None:
                    total_transitions += 1
                    if h > prev_h + 0.1:  # allow small noise
                        violations += 1
                prev_h = h
        mono_score = 1.0 - violations / max(total_transitions, 1)
        verdict = "✓ holographic" if mono_score > 0.8 else "✗ constructive"
        print(f"    {label}: {mono_score:.1%} monotonic ({violations} violations "
              f"in {total_transitions} transitions) — {verdict}")

    # Beam angle test: where does cosine similarity drop?
    cos_trajectory = [
        np.mean([c["layers"][li]["cosine_similarity"]
                for c in all_comparisons])
        for li in layer_ids
    ]
    # Find first layer where cosine drops below 0.95
    divergence_layer = None
    for i, (li, cs) in enumerate(zip(layer_ids, cos_trajectory)):
        if cs < 0.95:
            divergence_layer = li
            break

    if divergence_layer is not None:
        pct = divergence_layer / max(layer_ids) * 100
        print(f"\n  Beam divergence begins at layer {divergence_layer} "
              f"({pct:.0f}% depth)")
        if pct > 70:
            print(f"    → Late divergence: gate acts as late-stage beam selector")
        elif pct > 40:
            print(f"    → Mid divergence: gate modulates middle processing")
        else:
            print(f"    → Early divergence: gate changes representation from start")
    else:
        print(f"\n  No beam divergence detected (cos > 0.95 everywhere)")
        print(f"    → Conditions share the same representation at all layers")

    print(f"\n{'='*72}")


# ══════════════════════════════════════════════════════════════════
# Save results
# ══════════════════════════════════════════════════════════════════

def save_results(
    all_compile: list[dict],
    all_null: list[dict],
    all_comparisons: list[dict],
    sentences: list[str],
    out_dir: Path,
):
    """Save results as JSON (without raw hidden states)."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # Strip hidden states (too large for JSON)
    def strip_hidden(result: dict) -> dict:
        r = dict(result)
        r["layers"] = {}
        for li, lr in result["layers"].items():
            lr_copy = {k: v for k, v in lr.items() if k != "hidden_state"}
            r["layers"][str(li)] = lr_copy
        return r

    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "model": HF_MODEL,
        "n_sentences": len(sentences),
        "sentences": sentences,
        "sample_layers": SAMPLE_LAYERS,
        "compile_gate": "compile",
        "null_gate": "null",
        "per_sentence": [],
    }

    for i, (sent, cr, nr, comp) in enumerate(
        zip(sentences, all_compile, all_null, all_comparisons)
    ):
        output["per_sentence"].append({
            "sentence": sent,
            "compile": strip_hidden(cr),
            "null": strip_hidden(nr),
            "comparison": comp,
        })

    out_path = out_dir / "holographic_probe_results.json"
    out_path.write_text(json.dumps(output, indent=2, default=str))
    print(f"\n  💾 Saved: {out_path}", file=sys.stderr)
    return out_path


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Holographic probe — intermediate layer decoding")
    parser.add_argument("--model", choices=["gguf", "hf"], default="gguf",
                        help="Model source (default: gguf)")
    parser.add_argument("--quick", action="store_true",
                        help="Use fewer sentences and layers")
    parser.add_argument("--device", default="mps",
                        help="Device (default: mps)")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    # Load gates
    compile_gate = load_gate("compile")
    null_gate = load_gate("null")

    sentences = TEST_SENTENCES
    layers = SAMPLE_LAYERS

    if args.quick:
        sentences = sentences[:3]
        layers = [0, 8, 16, 24, 32, 40, 48, 56, 63]

    # Adjust layers for actual model
    print(f"\n{'='*72}")
    print(f"  Holographic Probe — Intermediate Layer Decoding")
    print(f"  Testing: {len(sentences)} sentences × 2 conditions × "
          f"{len(layers)} layers")
    print(f"{'='*72}")

    # Load model
    model, tokenizer = load_model(args.model, args.device)
    n_layers = model.config.num_hidden_layers
    layers = [l for l in layers if l < n_layers]

    all_compile = []
    all_null = []
    all_comparisons = []

    for i, sentence in enumerate(sentences):
        print(f"\n  [{i+1}/{len(sentences)}] \"{sentence[:50]}\"",
              file=sys.stderr)

        # Build prompts
        compile_prompt = make_prompt(compile_gate, sentence)
        null_prompt = make_prompt(null_gate, sentence)

        # Run both conditions
        t0 = time.time()
        compile_result = decode_at_layers(
            model, tokenizer, compile_prompt, layers=layers)
        null_result = decode_at_layers(
            model, tokenizer, null_prompt, layers=layers)
        t1 = time.time()
        print(f"  ⏱  {t1-t0:.1f}s", file=sys.stderr)

        # Print individual trajectories
        print_layer_trajectory(compile_result, "COMPILE", sentence)
        print_layer_trajectory(null_result, "NULL", sentence)

        # Compare conditions
        comp = compare_conditions(compile_result, null_result)
        print_comparison(comp, sentence)

        all_compile.append(compile_result)
        all_null.append(null_result)
        all_comparisons.append(comp)

    # Aggregate summary
    print_summary(all_comparisons, sentences)

    # Save
    save_results(all_compile, all_null, all_comparisons, sentences,
                 args.output_dir)


if __name__ == "__main__":
    main()
