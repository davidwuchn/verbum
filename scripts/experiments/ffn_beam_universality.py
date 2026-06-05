#!/usr/bin/env python3
"""FFN Beam Universality — Are FFN beam directions universal across models?

THE QUESTION: Do all models promote AND suppress the same vocabulary
directions at the same positions? If so, the holographic beam pattern
is derivable from structure, not learned from data.

MEASUREMENT:
  For each model × each probe text × each ALIGN-phase layer:
    1. Hook FFN output (the beam)
    2. Project beam through unembed → vocabulary logit contribution
    3. Record top-K promoted tokens (constructive interference)
    4. Record top-K suppressed tokens (destructive interference / anti-crystal)
    5. Compare across models

MODELS:
  Same tokenizer family:  Qwen3-0.6B vs Qwen3-8B (direct token comparison)
  Cross-architecture:     Qwen3-8B vs Pythia-410M (semantic comparison)

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/ffn_beam_universality.py

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import sys
import time
from pathlib import Path
from collections import defaultdict

os.environ.setdefault("PYTHONUNBUFFERED", "1")

import numpy as np
import torch
import torch.nn.functional as F

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "ffn-beam-universality"


def log(msg: str = "") -> None:
    print(msg, flush=True)


# ═══════════════════════════════════════════════════════════════════════
# Probe texts — designed to test different beam types
# ═══════════════════════════════════════════════════════════════════════

PROBES = [
    # Factual — strong selectivity expected
    {"text": "The capital of France is", "target_pos": -1, "label": "capital-france"},
    {"text": "Water is composed of two elements:", "target_pos": -1, "label": "water-elements"},
    {"text": "The speed of light is approximately", "target_pos": -1, "label": "speed-of-light"},

    # Syntactic — type-driven prediction
    {"text": "The cat sat on the", "target_pos": -1, "label": "cat-sat-on"},
    {"text": "The quick brown fox jumps over the lazy", "target_pos": -1, "label": "fox-lazy"},
    {"text": "She told him that she would", "target_pos": -1, "label": "she-would"},

    # Binding — predicate-argument structure
    {"text": "The dog bit the cat and the cat", "target_pos": -1, "label": "dog-bit-cat"},
    {"text": "The boy kicked the ball and it", "target_pos": -1, "label": "boy-kicked-ball"},

    # Lambda / formal
    {"text": "In lambda calculus, the identity combinator I applied to y gives", "target_pos": -1, "label": "identity-y"},

    # Negation / anti-crystal test
    {"text": "The earth is not", "target_pos": -1, "label": "earth-is-not"},
    {"text": "To be or not to be, that is the", "target_pos": -1, "label": "to-be-question"},

    # Multi-token context
    {"text": "Machine learning models learn by minimizing a loss function through", "target_pos": -1, "label": "ml-gradient"},
]


# ═══════════════════════════════════════════════════════════════════════
# FFN beam capture
# ═══════════════════════════════════════════════════════════════════════


@torch.no_grad()
def capture_ffn_beams(model, tokenizer, probe_texts, layer_indices, device,
                      top_k=30):
    """Capture FFN output beams projected into vocabulary space.

    For each probe × each layer:
      - Hook MLP output (the beam vector)
      - Project through unembed: beam_logits = unembed(beam)
      - Record top-K promoted (highest) and suppressed (lowest) tokens

    Returns list of dicts with beam information.
    """
    # Get the unembed matrix
    if hasattr(model, 'lm_head'):
        unembed_weight = model.lm_head.weight.float()  # (vocab_size, hidden_dim)
    elif hasattr(model, 'embed_out'):
        unembed_weight = model.embed_out.weight.float()  # Pythia
    else:
        raise RuntimeError("Cannot find lm_head or embed_out")

    # Get model layers
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
    else:
        raise RuntimeError("Cannot find model layers")

    # Also get the final layer norm for proper projection
    if hasattr(model, 'model') and hasattr(model.model, 'norm'):
        final_norm = model.model.norm
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'final_layer_norm'):
        final_norm = model.gpt_neox.final_layer_norm
    else:
        final_norm = None

    results = []

    for probe in probe_texts:
        text = probe["text"]
        label = probe["label"]
        target_pos = probe["target_pos"]

        inputs = tokenizer(text, return_tensors="pt").to(device)
        input_ids = inputs["input_ids"][0]
        seq_len = input_ids.shape[0]

        if target_pos < 0:
            target_pos = seq_len + target_pos  # -1 → last position

        # Hook storage
        ffn_outputs = {}

        def make_hook(layer_idx):
            def hook_fn(module, input, output):
                # output is the MLP output tensor
                ffn_outputs[layer_idx] = output[0, target_pos, :].float().cpu()
            return hook_fn

        # Register hooks
        hooks = []
        for li in layer_indices:
            if li < len(layers):
                h = layers[li].mlp.register_forward_hook(make_hook(li))
                hooks.append(h)

        # Forward pass
        model(**inputs)

        # Remove hooks
        for h in hooks:
            h.remove()

        # Project each FFN output through unembed → vocabulary logits
        for li in layer_indices:
            if li not in ffn_outputs:
                continue

            beam = ffn_outputs[li]  # (hidden_dim,)

            # Apply final norm if available (for proper projection)
            # Note: this is approximate — the real projection goes through
            # residual accumulation + norm. We're projecting the RAW FFN output.
            beam_logits = beam @ unembed_weight.cpu().T  # (vocab_size,)

            # Top-K promoted (highest logit contribution)
            promoted_vals, promoted_idx = beam_logits.topk(top_k)
            promoted_tokens = [tokenizer.decode([idx.item()]).strip() for idx in promoted_idx]

            # Top-K suppressed (most negative logit contribution)
            suppressed_vals, suppressed_idx = (-beam_logits).topk(top_k)
            suppressed_tokens = [tokenizer.decode([idx.item()]).strip() for idx in suppressed_idx]

            # Beam statistics
            beam_norm = beam.norm().item()
            beam_logit_std = beam_logits.std().item()

            results.append({
                "label": label,
                "text": text,
                "layer": li,
                "target_pos": target_pos,
                "target_token": tokenizer.decode([input_ids[target_pos].item()]).strip(),
                "beam_norm": beam_norm,
                "beam_logit_std": beam_logit_std,
                "promoted": [
                    {"token": t, "logit": v.item()}
                    for t, v in zip(promoted_tokens, promoted_vals)
                ],
                "suppressed": [
                    {"token": t, "logit": v.item()}
                    for t, v in zip(suppressed_tokens, suppressed_vals)
                ],
            })

        del ffn_outputs
        gc.collect()

    return results


def compare_beams(results_a, results_b, model_a_name, model_b_name,
                  same_tokenizer=True):
    """Compare beam directions between two models."""
    log(f"\n{'═' * 78}")
    log(f"  BEAM COMPARISON: {model_a_name} vs {model_b_name}")
    log(f"  Same tokenizer: {same_tokenizer}")
    log(f"{'═' * 78}")

    # Group by (label, layer)
    beams_a = {(r["label"], r["layer"]): r for r in results_a}
    beams_b = {(r["label"], r["layer"]): r for r in results_b}

    common_keys = set(beams_a.keys()) & set(beams_b.keys())
    if not common_keys:
        log("  No common (label, layer) pairs!")
        return {}

    comparisons = []
    for key in sorted(common_keys):
        a = beams_a[key]
        b = beams_b[key]

        a_promoted = set(t["token"].lower() for t in a["promoted"][:20])
        b_promoted = set(t["token"].lower() for t in b["promoted"][:20])
        a_suppressed = set(t["token"].lower() for t in a["suppressed"][:20])
        b_suppressed = set(t["token"].lower() for t in b["suppressed"][:20])

        if same_tokenizer:
            # Direct token comparison
            promoted_overlap = len(a_promoted & b_promoted)
            suppressed_overlap = len(a_suppressed & b_suppressed)
            cross_overlap = len(a_promoted & b_suppressed)  # promoted in A, suppressed in B

            promoted_jaccard = promoted_overlap / max(len(a_promoted | b_promoted), 1)
            suppressed_jaccard = suppressed_overlap / max(len(a_suppressed | b_suppressed), 1)
        else:
            # Semantic comparison — just report the tokens
            promoted_overlap = len(a_promoted & b_promoted)
            suppressed_overlap = len(a_suppressed & b_suppressed)
            cross_overlap = len(a_promoted & b_suppressed)

            promoted_jaccard = promoted_overlap / max(len(a_promoted | b_promoted), 1)
            suppressed_jaccard = suppressed_overlap / max(len(a_suppressed | b_suppressed), 1)

        comp = {
            "label": key[0],
            "layer": key[1],
            "promoted_overlap": promoted_overlap,
            "suppressed_overlap": suppressed_overlap,
            "cross_contamination": cross_overlap,
            "promoted_jaccard": promoted_jaccard,
            "suppressed_jaccard": suppressed_jaccard,
        }
        comparisons.append(comp)

        # Show details
        a_top5 = [t["token"] for t in a["promoted"][:5]]
        b_top5 = [t["token"] for t in b["promoted"][:5]]
        a_anti5 = [t["token"] for t in a["suppressed"][:5]]
        b_anti5 = [t["token"] for t in b["suppressed"][:5]]

        shared_p = a_promoted & b_promoted
        shared_s = a_suppressed & b_suppressed

        log(f"\n  ── {key[0]} @ L{key[1]} ──")
        log(f"    {model_a_name} promotes: {', '.join(a_top5)}")
        log(f"    {model_b_name} promotes: {', '.join(b_top5)}")
        log(f"    Shared promoted (top-20): {promoted_overlap}/20  "
            f"J={promoted_jaccard:.3f}  [{', '.join(sorted(shared_p)[:8])}]")
        log(f"    {model_a_name} suppresses: {', '.join(a_anti5)}")
        log(f"    {model_b_name} suppresses: {', '.join(b_anti5)}")
        log(f"    Shared suppressed (top-20): {suppressed_overlap}/20  "
            f"J={suppressed_jaccard:.3f}  [{', '.join(sorted(shared_s)[:8])}]")
        if cross_overlap > 0:
            log(f"    ⚠ Cross-contamination: {cross_overlap} tokens promoted in one, suppressed in other")

    # Summary
    if comparisons:
        mean_pj = np.mean([c["promoted_jaccard"] for c in comparisons])
        mean_sj = np.mean([c["suppressed_jaccard"] for c in comparisons])
        mean_cross = np.mean([c["cross_contamination"] for c in comparisons])
        log(f"\n  SUMMARY:")
        log(f"    Mean promoted Jaccard:   {mean_pj:.3f}")
        log(f"    Mean suppressed Jaccard: {mean_sj:.3f}")
        log(f"    Mean cross-contamination: {mean_cross:.1f}")
        if mean_pj > 0.3:
            log(f"    ✅ Promoted beams show agreement")
        if mean_sj > 0.3:
            log(f"    ✅ Anti-crystal (suppression) shows agreement")
        if mean_pj < 0.1 and mean_sj < 0.1:
            log(f"    ❌ Beams appear model-specific")

    return comparisons


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════


def run_model(model_name, tokenizer_name, layer_indices, device, top_k=30):
    """Load model, capture beams, return results."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    log(f"\n{'═' * 78}")
    log(f"  MODEL: {model_name}")
    log(f"  Layers: {layer_indices}")
    log(f"{'═' * 78}")

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name or model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16, device_map=device,
    )
    model.eval()

    # Get total layers
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        n_layers = len(model.model.layers)
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        n_layers = len(model.gpt_neox.layers)
    else:
        n_layers = 0
    log(f"  Total layers: {n_layers}")

    # Adjust layer indices to model depth
    adjusted_layers = []
    for li in layer_indices:
        if li < n_layers:
            adjusted_layers.append(li)
    if not adjusted_layers:
        # Use fractional depths: 50%, 70%, 80%, 90% of model depth
        adjusted_layers = [
            int(n_layers * 0.50),
            int(n_layers * 0.70),
            int(n_layers * 0.80),
            int(n_layers * 0.90),
        ]
    log(f"  Using layers: {adjusted_layers}")

    # Also get the full model's next-token prediction for reference
    log(f"  Capturing FFN beams...")
    results = capture_ffn_beams(
        model, tokenizer, PROBES, adjusted_layers, device, top_k=top_k,
    )

    # Print beam summaries
    for r in results:
        top3_p = [t["token"] for t in r["promoted"][:3]]
        top3_s = [t["token"] for t in r["suppressed"][:3]]
        log(f"    {r['label']:<20} L{r['layer']:>2}  "
            f"promote=[{', '.join(top3_p)}]  "
            f"suppress=[{', '.join(top3_s)}]  "
            f"norm={r['beam_norm']:.1f}")

    del model
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()

    return results, tokenizer, n_layers, adjusted_layers


def main():
    parser = argparse.ArgumentParser(description="FFN Beam Universality")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--top-k", type=int, default=30)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log(f"╔{'═' * 76}╗")
    log(f"║  FFN BEAM UNIVERSALITY — Do all models form the same beams?{' ' * 15}║")
    log(f"║  Promoted = constructive interference (what to predict){' ' * 20}║")
    log(f"║  Suppressed = destructive interference (anti-crystal){' ' * 21}║")
    log(f"╚{'═' * 76}╝")

    t_start = time.time()

    # ── Model 1: Qwen3-8B (our main model) ──
    # ALIGN phase layers for 36-layer model: ~L18 (50%), L25 (70%), L29 (80%), L32 (90%)
    qwen8b_results, qwen8b_tok, qwen8b_nl, qwen8b_layers = run_model(
        "Qwen/Qwen3-8B", None,
        [18, 25, 29, 32], args.device, args.top_k,
    )

    # ── Model 2: Qwen3-0.6B (same tokenizer, 13× smaller) ──
    # 28 layers: L14 (50%), L20 (71%), L22 (79%), L25 (89%)
    qwen06b_results, qwen06b_tok, qwen06b_nl, qwen06b_layers = run_model(
        "Qwen/Qwen3-0.6B", None,
        [14, 20, 22, 25], args.device, args.top_k,
    )

    # ── Model 3: Pythia-410M (different architecture, different tokenizer) ──
    # 24 layers: L12 (50%), L17 (71%), L19 (79%), L22 (92%)
    pythia_results, pythia_tok, pythia_nl, pythia_layers = run_model(
        "EleutherAI/pythia-410m", None,
        [12, 17, 19, 22], args.device, args.top_k,
    )

    # ── Comparisons ──

    # For cross-model comparison at matching FRACTIONAL depths,
    # we need to align by depth fraction, not layer index.
    # Map each model's layers to fractional depths
    def align_by_fraction(results_a, n_layers_a, results_b, n_layers_b):
        """Re-label layer indices as fractional depths for comparison."""
        for r in results_a:
            r["depth_frac"] = r["layer"] / n_layers_a
            r["layer_orig"] = r["layer"]
        for r in results_b:
            r["depth_frac"] = r["layer"] / n_layers_b
            r["layer_orig"] = r["layer"]

        # Match by closest fractional depth
        aligned_a, aligned_b = [], []
        for ra in results_a:
            best_match = min(results_b,
                             key=lambda rb: abs(rb["depth_frac"] - ra["depth_frac"])
                             if rb["label"] == ra["label"] else 999,
                             default=None)
            if best_match and best_match["label"] == ra["label"]:
                # Temporarily set same layer for comparison
                common_layer = int(ra["depth_frac"] * 100)  # use % as key
                ra_copy = dict(ra)
                rb_copy = dict(best_match)
                ra_copy["layer"] = common_layer
                rb_copy["layer"] = common_layer
                aligned_a.append(ra_copy)
                aligned_b.append(rb_copy)

        return aligned_a, aligned_b

    # Comparison 1: Qwen3-8B vs Qwen3-0.6B (same tokenizer)
    a1, b1 = align_by_fraction(
        [dict(r) for r in qwen8b_results], qwen8b_nl,
        [dict(r) for r in qwen06b_results], qwen06b_nl,
    )
    comp1 = compare_beams(a1, b1, "Qwen3-8B", "Qwen3-0.6B", same_tokenizer=True)

    # Comparison 2: Qwen3-8B vs Pythia-410M (different tokenizer)
    a2, b2 = align_by_fraction(
        [dict(r) for r in qwen8b_results], qwen8b_nl,
        [dict(r) for r in pythia_results], pythia_nl,
    )
    comp2 = compare_beams(a2, b2, "Qwen3-8B", "Pythia-410M", same_tokenizer=False)

    # Comparison 3: Qwen3-0.6B vs Pythia-410M (different tokenizer)
    a3, b3 = align_by_fraction(
        [dict(r) for r in qwen06b_results], qwen06b_nl,
        [dict(r) for r in pythia_results], pythia_nl,
    )
    comp3 = compare_beams(a3, b3, "Qwen3-0.6B", "Pythia-410M", same_tokenizer=False)

    # ── Save results ──
    all_results = {
        "models": {
            "qwen3_8b": {"n_layers": qwen8b_nl, "layers_used": qwen8b_layers,
                         "beams": qwen8b_results},
            "qwen3_06b": {"n_layers": qwen06b_nl, "layers_used": qwen06b_layers,
                          "beams": qwen06b_results},
            "pythia_410m": {"n_layers": pythia_nl, "layers_used": pythia_layers,
                            "beams": pythia_results},
        },
        "comparisons": {
            "qwen8b_vs_qwen06b": comp1,
            "qwen8b_vs_pythia": comp2,
            "qwen06b_vs_pythia": comp3,
        },
        "elapsed_total": time.time() - t_start,
    }

    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    elapsed = time.time() - t_start
    log(f"\n{'═' * 78}")
    log(f"  COMPLETE — {elapsed:.0f}s total")
    log(f"  Results: {RESULTS_DIR}/")
    log(f"{'═' * 78}")


if __name__ == "__main__":
    main()
