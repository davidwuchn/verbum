#!/usr/bin/env python3
"""Probe: Does combinator selectivity survive ternary quantization?

Tests whether the combinatory information in Qwen3-32B's attention heads
is stored as topology (sign patterns) or precision (magnitudes).

Method:
  1. Run combinator probe sentences (K, I, B, C active vs control)
  2. Capture per-layer hidden states → compute selectivity scores
  3. For target layers, quantize Q/K/V/O weights to ternary {-1, 0, +1}
  4. Re-run the same sentences → re-compute selectivity
  5. Compare: if selectivity survives, the information is topological

The probe tests multiple sparsity thresholds for the zero-band:
  - threshold=0: pure sign quantization (no zeros)
  - threshold=median: moderate sparsity (~50% zeros)
  - threshold=p75: high sparsity (~75% zeros)

If selectivity survives even at high sparsity, the holographic
structure is in the sign topology, not the magnitudes.

Usage:
    uv run python scripts/explore/probe_ternary_survival.py
    uv run python scripts/explore/probe_ternary_survival.py --quick
    uv run python scripts/explore/probe_ternary_survival.py --layers 1,3,6,24,43

Output: results/ternary-survival/

License: MIT
"""

from __future__ import annotations

import argparse
import copy
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
OUTPUT_DIR = Path("results/ternary-survival")

# Layers to test — includes combinator-selective layers from prior probes
# Layer 1: C-selective (head 34), early gate recognition
# Layer 3: K-selective (head 26), B-selective (head 36)
# Layer 6: I-selective (head 52)
# Layer 24: mid-depth (beam divergence point from holographic probe)
# Layer 43: compositor region (from circuit mapping)
# Layer 56: late convergence
TARGET_LAYERS = [1, 3, 6, 24, 43, 56]

# Sparsity thresholds: what fraction of |w| to zero out
THRESHOLDS = {
    "sign_only": 0.0,     # pure sign: no zeros
    "low_sparse": 0.25,   # 25th percentile → ~25% zeros
    "mid_sparse": 0.50,   # median → ~50% zeros
    "high_sparse": 0.75,  # 75th percentile → ~75% zeros
    "extreme": 0.90,      # 90th percentile → ~90% zeros
}

# Combinator probe sentences (from probe_combinators.py)
COMBINATOR_PROBES = {
    "K": {
        "description": "Selection — choose one referent, discard alternative",
        "active": [
            "The cat, not the dog, chased the mouse across the yard.",
            "Either the president or the minister signed the treaty last week.",
            "John, rather than his brother, won the competition in the end.",
        ],
        "control": [
            "The cat chased the mouse across the yard very quickly.",
            "The president signed the treaty at the ceremony last week.",
            "John won the competition in the end with great effort.",
        ],
    },
    "I": {
        "description": "Identity — forward information unchanged, copy, repeat",
        "active": [
            'He said "hello" and then she also said "hello" to everyone.',
            "The result was five. The answer is five. Five is correct.",
            "She ran quickly. She ran so quickly that nobody could catch her.",
        ],
        "control": [
            'He said "hello" and then she said "goodbye" to everyone.',
            "The result was five. The method is correct. Nothing was wrong.",
            "She ran quickly. The others walked slowly behind the group.",
        ],
    },
    "B": {
        "description": "Composition — nested operations, relative clauses",
        "active": [
            "The man who the dog that the cat chased bit ran away quickly.",
            "The student who read the book that the professor recommended passed.",
            "If every teacher who knows a student that failed helps them, all improve.",
        ],
        "control": [
            "The man ran away quickly after the incident in the park.",
            "The student passed the course with excellent marks this year.",
            "If every teacher helps struggling students then all will improve.",
        ],
    },
    "C": {
        "description": "Flip — argument reordering, passive voice",
        "active": [
            "The mouse was chased by the cat through the garden quickly.",
            "The treaty was signed by the president at the formal ceremony.",
            "The book was read by every student in the advanced class.",
        ],
        "control": [
            "The cat chased the mouse through the garden very quickly.",
            "The president signed the treaty at the formal ceremony today.",
            "Every student read the book in the advanced class this term.",
        ],
    },
}

NULL_PROBES = [
    "The sun rose over the mountains in the early morning light.",
    "Water flows downhill following the path of least resistance.",
    "The library was quiet and the shelves were full of books.",
]


# ══════════════════════════════════════════════════════════════════
# Model loading
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
    print(f"Loaded in {t1-t0:.1f}s: {model.config.num_hidden_layers} layers, "
          f"d={model.config.hidden_size}", file=sys.stderr)
    return model, tokenizer


# ══════════════════════════════════════════════════════════════════
# Selectivity measurement via hidden state divergence
# ══════════════════════════════════════════════════════════════════

def get_hidden_states(model, tokenizer, text: str, layers: list[int]) -> dict:
    """Capture hidden states at specified layers."""
    captured = {}
    hooks = []

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            if isinstance(output, tuple):
                h = output[0]
            else:
                h = output
            captured[layer_idx] = h.detach().cpu().float()
        return hook_fn

    for li in layers:
        layer_module = model.model.layers[li]
        hooks.append(layer_module.register_forward_hook(make_hook(li)))

    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model(**inputs)

    for h in hooks:
        h.remove()

    # Also get the logits for output-level comparison
    logits = outputs.logits[0, -1].detach().cpu().float()

    return {"hidden_states": captured, "logits": logits}


def measure_selectivity(
    model, tokenizer, layers: list[int],
) -> dict:
    """Measure combinator selectivity across all probes.

    For each combinator, compute:
      - Hidden state divergence (active vs control) at each layer
      - Output logit divergence (KL between active and control distributions)

    Returns selectivity scores per combinator per layer.
    """
    results = {}

    for comb_name, comb_data in COMBINATOR_PROBES.items():
        active_texts = comb_data["active"]
        control_texts = comb_data["control"]
        n_pairs = min(len(active_texts), len(control_texts))

        layer_selectivity = {li: [] for li in layers}
        output_kls = []

        for i in range(n_pairs):
            active_hs = get_hidden_states(model, tokenizer, active_texts[i], layers)
            control_hs = get_hidden_states(model, tokenizer, control_texts[i], layers)

            # Per-layer: cosine distance between mean hidden states
            for li in layers:
                h_a = active_hs["hidden_states"][li][0].mean(dim=0)  # (d_model,)
                h_c = control_hs["hidden_states"][li][0].mean(dim=0)
                cos_sim = F.cosine_similarity(h_a.unsqueeze(0), h_c.unsqueeze(0)).item()
                # Selectivity = 1 - cos_sim (higher = more different)
                layer_selectivity[li].append(1.0 - cos_sim)

            # Output-level: KL divergence of logit distributions
            p = F.softmax(active_hs["logits"], dim=-1)
            q = F.softmax(control_hs["logits"], dim=-1)
            kl = F.kl_div(q.log(), p, reduction="sum").item()
            output_kls.append(kl)

            # Clear cache
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()

        results[comb_name] = {
            "layer_selectivity": {
                li: float(np.mean(layer_selectivity[li])) for li in layers
            },
            "output_kl": float(np.mean(output_kls)),
        }

    return results


# ══════════════════════════════════════════════════════════════════
# Ternary quantization of attention weights
# ══════════════════════════════════════════════════════════════════

def ternary_quantize_layer(model, layer_idx: int, threshold_percentile: float):
    """Quantize a layer's attention Q/K/V/O weights to ternary.

    Returns: dict of original weights (for restoration) and stats.
    """
    layer = model.model.layers[layer_idx]
    attn = layer.self_attn

    # Qwen3 attention weight names
    weight_names = ["q_proj", "k_proj", "v_proj", "o_proj"]
    originals = {}
    stats = {}

    for wn in weight_names:
        proj = getattr(attn, wn)
        w = proj.weight.data
        originals[wn] = w.clone()

        # Compute threshold from percentile of |w|
        abs_w = w.abs()
        if threshold_percentile > 0:
            # Sample if tensor too large for quantile
            flat = abs_w.float().flatten()
            if flat.numel() > 1_000_000:
                indices = torch.randperm(flat.numel())[:1_000_000]
                sample = flat[indices]
            else:
                sample = flat
            threshold = torch.quantile(sample, threshold_percentile).item()
        else:
            threshold = 0.0

        # Ternary quantize
        scale = abs_w[abs_w > threshold].mean().item() if (abs_w > threshold).any() else 1.0
        ternary = torch.zeros_like(w)
        ternary[w > threshold] = 1.0
        ternary[w < -threshold] = -1.0

        # Apply with scale factor (so magnitudes are approximately preserved)
        proj.weight.data = ternary * scale

        n_total = w.numel()
        n_zero = (ternary == 0).sum().item()
        n_pos = (ternary > 0).sum().item()
        n_neg = (ternary < 0).sum().item()

        stats[wn] = {
            "shape": list(w.shape),
            "threshold": threshold,
            "scale": scale,
            "sparsity": n_zero / n_total,
            "n_pos": n_pos,
            "n_neg": n_neg,
            "n_zero": n_zero,
            "balance": n_pos / max(n_neg, 1),  # should be ~1.0 for balanced
        }

    return originals, stats


def restore_layer(model, layer_idx: int, originals: dict):
    """Restore original weights after quantization test."""
    layer = model.model.layers[layer_idx]
    attn = layer.self_attn
    for wn, w in originals.items():
        getattr(attn, wn).weight.data = w


# ══════════════════════════════════════════════════════════════════
# Core experiment
# ══════════════════════════════════════════════════════════════════

def run_survival_test(
    model, tokenizer,
    target_layers: list[int],
    measure_layers: list[int],
    thresholds: dict[str, float],
) -> dict:
    """Run the full ternary survival experiment.

    1. Measure baseline selectivity (original weights)
    2. For each target layer × threshold:
       a. Quantize attention weights to ternary
       b. Re-measure selectivity
       c. Restore original weights
    3. Compare: survival_ratio = ternary_selectivity / baseline_selectivity
    """
    results = {
        "target_layers": target_layers,
        "measure_layers": measure_layers,
        "thresholds": thresholds,
    }

    # ── Baseline measurement ──────────────────────────────
    print(f"\n  Measuring baseline selectivity...", file=sys.stderr)
    t0 = time.time()
    baseline = measure_selectivity(model, tokenizer, measure_layers)
    t1 = time.time()
    results["baseline"] = baseline
    print(f"  Baseline done in {t1-t0:.1f}s", file=sys.stderr)

    # Print baseline
    print(f"\n  ┌─ Baseline Selectivity ──────────────────────────┐")
    print(f"  │ {'comb':>4} {'output_KL':>10}", end="")
    for li in measure_layers:
        print(f" {'L'+str(li):>8}", end="")
    print()
    for comb in ["K", "I", "B", "C"]:
        b = baseline[comb]
        print(f"  │ {comb:>4} {b['output_kl']:>10.4f}", end="")
        for li in measure_layers:
            print(f" {b['layer_selectivity'][li]:>8.4f}", end="")
        print()
    print(f"  └{'─'*60}┘")

    # ── Per-layer × per-threshold tests ───────────────────
    results["experiments"] = {}

    for target_layer in target_layers:
        results["experiments"][target_layer] = {}

        for thresh_name, thresh_pct in thresholds.items():
            print(f"\n  Testing layer {target_layer}, "
                  f"threshold={thresh_name} ({thresh_pct:.0%})...",
                  file=sys.stderr)

            # Quantize
            originals, quant_stats = ternary_quantize_layer(
                model, target_layer, thresh_pct)

            # Measure
            t0 = time.time()
            quantized = measure_selectivity(model, tokenizer, measure_layers)
            t1 = time.time()

            # Compute survival ratios
            survival = {}
            for comb in ["K", "I", "B", "C"]:
                b_kl = baseline[comb]["output_kl"]
                q_kl = quantized[comb]["output_kl"]
                survival[comb] = {
                    "output_kl_ratio": q_kl / max(b_kl, 1e-8),
                    "layer_ratios": {},
                }
                for li in measure_layers:
                    b_sel = baseline[comb]["layer_selectivity"][li]
                    q_sel = quantized[comb]["layer_selectivity"][li]
                    survival[comb]["layer_ratios"][li] = (
                        q_sel / max(b_sel, 1e-8)
                    )

            results["experiments"][target_layer][thresh_name] = {
                "quant_stats": quant_stats,
                "selectivity": quantized,
                "survival": survival,
                "elapsed_s": t1 - t0,
            }

            # Restore
            restore_layer(model, target_layer, originals)

            # Print summary
            print(f"  ┌─ Layer {target_layer} × {thresh_name} "
                  f"(sparsity: {quant_stats['q_proj']['sparsity']:.1%}) ──┐")
            print(f"  │ {'comb':>4} {'KL_surv':>8}", end="")
            for li in measure_layers:
                print(f" {'L'+str(li):>8}", end="")
            print()
            for comb in ["K", "I", "B", "C"]:
                s = survival[comb]
                kl_r = s["output_kl_ratio"]
                marker = "✓" if 0.5 < kl_r < 2.0 else "✗"
                print(f"  │ {comb:>4} {kl_r:>7.2f}{marker}", end="")
                for li in measure_layers:
                    lr = s["layer_ratios"][li]
                    m2 = "·" if 0.5 < lr < 2.0 else "!"
                    print(f" {lr:>7.2f}{m2}", end="")
                print()
            print(f"  └{'─'*60}┘")

    return results


# ══════════════════════════════════════════════════════════════════
# Summary analysis
# ══════════════════════════════════════════════════════════════════

def print_summary(results: dict):
    """Print aggregate survival analysis."""
    print(f"\n{'='*72}")
    print(f"  TERNARY SURVIVAL SUMMARY")
    print(f"{'='*72}")

    experiments = results["experiments"]
    thresholds = results["thresholds"]
    measure_layers = results["measure_layers"]

    # Aggregate: for each threshold, what's the mean survival ratio?
    for thresh_name in thresholds:
        output_survivals = []
        layer_survivals = []

        for target_layer in experiments:
            if thresh_name not in experiments[target_layer]:
                continue
            exp = experiments[target_layer][thresh_name]
            for comb in ["K", "I", "B", "C"]:
                s = exp["survival"][comb]
                output_survivals.append(s["output_kl_ratio"])
                for li in measure_layers:
                    layer_survivals.append(s["layer_ratios"][li])

        if output_survivals:
            mean_out = np.mean(output_survivals)
            mean_layer = np.mean(layer_survivals)
            median_out = np.median(output_survivals)

            # How many survived (ratio between 0.5 and 2.0)?
            survived_out = sum(1 for r in output_survivals if 0.5 < r < 2.0)
            total_out = len(output_survivals)
            survived_layer = sum(1 for r in layer_survivals if 0.5 < r < 2.0)
            total_layer = len(layer_survivals)

            sparsity = "?"
            for tl in experiments:
                if thresh_name in experiments[tl]:
                    sparsity = experiments[tl][thresh_name]["quant_stats"]["q_proj"]["sparsity"]
                    break

            verdict = "✓ TOPOLOGICAL" if survived_out / max(total_out, 1) > 0.7 else "✗ precision-dependent"

            print(f"\n  {thresh_name} (sparsity={sparsity:.1%}):")
            print(f"    Output KL survival: {survived_out}/{total_out} "
                  f"({survived_out/max(total_out,1):.0%}) "
                  f"mean={mean_out:.2f} median={median_out:.2f}")
            print(f"    Layer selectivity:  {survived_layer}/{total_layer} "
                  f"({survived_layer/max(total_layer,1):.0%}) "
                  f"mean={mean_layer:.2f}")
            print(f"    Verdict: {verdict}")

    # Final verdict
    print(f"\n{'─'*72}")

    # Check if sign_only preserves selectivity
    sign_survivals = []
    for target_layer in experiments:
        if "sign_only" in experiments[target_layer]:
            exp = experiments[target_layer]["sign_only"]
            for comb in ["K", "I", "B", "C"]:
                sign_survivals.append(exp["survival"][comb]["output_kl_ratio"])

    if sign_survivals:
        sign_survived = sum(1 for r in sign_survivals if 0.5 < r < 2.0)
        sign_total = len(sign_survivals)
        sign_frac = sign_survived / max(sign_total, 1)

        if sign_frac > 0.7:
            print(f"  🔬 CONCLUSION: Combinator selectivity is TOPOLOGICAL.")
            print(f"     Sign structure alone preserves {sign_frac:.0%} of selectivity.")
            print(f"     The holographic plate hypothesis is supported.")
        elif sign_frac > 0.4:
            print(f"  🔬 CONCLUSION: Mixed evidence.")
            print(f"     Sign structure preserves {sign_frac:.0%} of selectivity.")
            print(f"     Some combinatory info is topological, some requires precision.")
        else:
            print(f"  🔬 CONCLUSION: Combinator selectivity is PRECISION-DEPENDENT.")
            print(f"     Sign structure preserves only {sign_frac:.0%} of selectivity.")
            print(f"     The holographic plate hypothesis is NOT supported.")

    print(f"\n{'='*72}")


# ══════════════════════════════════════════════════════════════════
# Save results
# ══════════════════════════════════════════════════════════════════

def save_results(results: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ternary_survival_results.json"

    # Convert numpy types for JSON
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    out_path.write_text(json.dumps(results, indent=2, default=convert))
    print(f"\n  💾 Saved: {out_path}", file=sys.stderr)
    return out_path


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Ternary survival probe — does combinator selectivity "
                    "survive ternary quantization?")
    parser.add_argument("--model", choices=["gguf", "hf"], default="gguf")
    parser.add_argument("--quick", action="store_true",
                        help="Test fewer layers and thresholds")
    parser.add_argument("--layers", type=str, default=None,
                        help="Comma-separated target layers (default: 1,3,6,24,43,56)")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    target_layers = TARGET_LAYERS
    thresholds = THRESHOLDS
    # Measurement layers: include targets + some reference points
    measure_layers = [0, 8, 16, 32, 48, 63]

    if args.layers:
        target_layers = [int(l) for l in args.layers.split(",")]

    if args.quick:
        target_layers = [3, 24]  # K/B selective + beam divergence point
        thresholds = {
            "sign_only": 0.0,
            "mid_sparse": 0.50,
            "high_sparse": 0.75,
        }
        measure_layers = [0, 16, 32, 63]

    print(f"\n{'='*72}")
    print(f"  Ternary Survival Probe")
    print(f"  Target layers: {target_layers}")
    print(f"  Thresholds: {list(thresholds.keys())}")
    print(f"  Measure layers: {measure_layers}")
    print(f"{'='*72}")

    model, tokenizer = load_model(args.model, args.device)

    results = run_survival_test(
        model, tokenizer,
        target_layers=target_layers,
        measure_layers=measure_layers,
        thresholds=thresholds,
    )

    print_summary(results)
    save_results(results, args.output_dir)


if __name__ == "__main__":
    main()
