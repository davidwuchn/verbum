#!/usr/bin/env python3
"""Scan crystal structure across ALL layers to find depth-dependent Y/W inversion.

Hypothesis: The Y/W sign flip is layer-dependent. The consensus crystal was
derived from specific layer ranges — if Y and W probes activate differently
at different depths, the measurement layer choice determines the sign.

Method:
  For each layer individually:
    1. Extract gate_proj activations for all crystal probes
    2. PCA → combinator projections → cosine matrix
    3. Track Y/W sign relative to consensus at each depth
    4. Find the crossover point where Y/W flip sign

Usage:
  uv run python scripts/experiments/crystal_depth_scan.py --model Qwen/Qwen3-0.6B

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
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from verbum.probes.library import by_combinator  # noqa: E402

PHI = (1 + np.sqrt(5)) / 2
CRYSTAL_COMBINATORS = ["K", "I", "B", "C", "D", "W", "Y", "WHNF"]
CONSENSUS_ORDER = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]

CONSENSUS_8x8 = np.array([
    [+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862],
    [+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448],
    [+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227],
    [+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027],
    [+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729],
    [+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840],
    [+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379],
    [-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000],
])


def find_gate_proj(layer_module):
    mlp = getattr(layer_module, 'mlp', None)
    if mlp is None:
        return None
    if hasattr(mlp, 'gate_proj'):
        return mlp.gate_proj
    elif hasattr(mlp, 'gate_up_proj'):
        return mlp.gate_up_proj
    elif hasattr(mlp, 'dense_h_to_4h'):
        return mlp.dense_h_to_4h
    return None


def get_layers_container(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    elif hasattr(model, 'transformer') and hasattr(model.transformer, 'h'):
        return model.transformer.h
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def extract_single_layer(model, tokenizer, prompts, layer_idx, device):
    """Extract gate_proj activations from a single layer."""
    layers_container = get_layers_container(model)
    intermediate_size = getattr(model.config, 'intermediate_size', None)

    captured = {}

    def hook_fn(module, input, output):
        captured['act'] = output.detach().float()

    gate = find_gate_proj(layers_container[layer_idx])
    if gate is None:
        return None
    hook = gate.register_forward_hook(hook_fn)

    all_acts = []
    for prompt in prompts:
        captured.clear()
        inputs = tokenizer(prompt, return_tensors="pt", padding=False,
                           truncation=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            model(**inputs)
        if 'act' in captured:
            act = captured['act']
            if intermediate_size and act.shape[-1] > intermediate_size:
                act = act[..., :intermediate_size]
            all_acts.append(act.mean(dim=1).squeeze(0).cpu().numpy())

    hook.remove()
    return np.array(all_acts) if all_acts else None


def compute_cosine_at_layer(model, tokenizer, probe_dict, layer_idx,
                            device, combinators):
    """Compute cosine matrix from a single layer's activations."""
    all_acts = []
    labels = []
    for comb in combinators:
        acts = extract_single_layer(model, tokenizer, probe_dict[comb],
                                    layer_idx, device)
        if acts is not None:
            for a in acts:
                all_acts.append(a)
                labels.append(comb)

    all_acts = np.array(all_acts)
    centered = all_acts - all_acts.mean(axis=0)

    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    n_pcs = min(len(combinators) * 2, len(S))
    pcs = Vt[:n_pcs]

    projections = []
    for comb in combinators:
        idx = [i for i, l in enumerate(labels) if l == comb]
        mean_comb = centered[idx].mean(axis=0)
        projections.append(pcs @ mean_comb)

    projections = np.array(projections)
    norms = np.linalg.norm(projections, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normed = projections / norms
    return normed @ normed.T


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-0.6B")
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--n-per-combinator", type=int, default=20,
                        help="Probes per combinator (default 20 for speed)")
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    if args.device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    else:
        device = args.device

    # Select probes
    rng = np.random.RandomState(42)
    combinators = list(CRYSTAL_COMBINATORS)
    probe_dict = {}
    for comb in combinators:
        probes = by_combinator(comb)
        prompts = [p.prompt for p in probes]
        if args.n_per_combinator and len(prompts) > args.n_per_combinator:
            idx = rng.choice(len(prompts), args.n_per_combinator, replace=False)
            prompts = [prompts[i] for i in sorted(idx)]
        probe_dict[comb] = prompts

    total = sum(len(v) for v in probe_dict.values())
    print(f"Model: {args.model}, device: {device}")
    print(f"Probes: {total} ({args.n_per_combinator} per combinator)")

    # Load model
    print(f"Loading {args.model}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.float16,
        device_map=device if device != "mps" else None,
        trust_remote_code=True,
    )
    if device == "mps":
        model = model.to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    print(f"Loaded: {n_layers} layers")

    # Map combinators to consensus order for comparison
    idx_map = [combinators.index(c) for c in CONSENSUS_ORDER if c in combinators]

    # Scan ALL layers
    results_per_layer = []
    print(f"\nScanning {n_layers} layers...")
    print(f"{'Layer':>5} {'Depth%':>6} {'Raw corr':>9} {'YW-neg':>9} {'B-D':>6} {'K-I':>6} {'B-W':>6} {'C-Y':>6} {'D-W':>6}")
    print("─" * 75)

    t0 = time.time()
    for li in range(n_layers):
        depth_pct = li / (n_layers - 1) * 100

        cosine = compute_cosine_at_layer(
            model, tokenizer, probe_dict, li, device, combinators,
        )

        # Extract 8x8 in consensus order
        c8 = cosine[np.ix_(idx_map, idx_map)]

        # Raw correlation with consensus
        raw_corr = np.corrcoef(c8.ravel(), CONSENSUS_8x8.ravel())[0, 1]

        # YW-negated correlation
        c_neg = cosine.copy()
        wi = combinators.index("W")
        yi = combinators.index("Y")
        for fi in [wi, yi]:
            c_neg[fi, :] *= -1
            c_neg[:, fi] *= -1
        c8_neg = c_neg[np.ix_(idx_map, idx_map)]
        neg_corr = np.corrcoef(c8_neg.ravel(), CONSENSUS_8x8.ravel())[0, 1]

        # Key pairs
        ki_i, ii_i = combinators.index("K"), combinators.index("I")
        bi_i, di_i = combinators.index("B"), combinators.index("D")
        ci_i = combinators.index("C")

        bd = cosine[bi_i, di_i]
        ki = cosine[ki_i, ii_i]
        bw = cosine[bi_i, wi]
        cy = cosine[ci_i, yi]
        dw = cosine[di_i, wi]

        print(f"{li:>5} {depth_pct:>5.1f}% {raw_corr:>+9.3f} {neg_corr:>+9.3f} {bd:>+6.3f} {ki:>+6.3f} {bw:>+6.3f} {cy:>+6.3f} {dw:>+6.3f}")

        results_per_layer.append({
            "layer": li,
            "depth_pct": round(depth_pct, 1),
            "raw_corr": float(raw_corr),
            "yw_neg_corr": float(neg_corr),
            "B_D": float(bd),
            "K_I": float(ki),
            "B_W": float(bw),
            "C_Y": float(cy),
            "D_W": float(dw),
            "cosine_matrix": cosine.tolist(),
        })

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s ({elapsed/n_layers:.1f}s per layer)")

    # Find crossover points
    print("\n=== ANALYSIS ===")
    bw_vals = [r["B_W"] for r in results_per_layer]
    cy_vals = [r["C_Y"] for r in results_per_layer]
    dw_vals = [r["D_W"] for r in results_per_layer]
    raw_corrs = [r["raw_corr"] for r in results_per_layer]
    neg_corrs = [r["yw_neg_corr"] for r in results_per_layer]

    # Where does raw > neg (i.e., Y/W are correctly oriented)?
    for i in range(n_layers):
        if raw_corrs[i] > neg_corrs[i]:
            print(f"  Layer {i} ({results_per_layer[i]['depth_pct']:.0f}%): raw ({raw_corrs[i]:.3f}) > neg ({neg_corrs[i]:.3f}) — Y/W naturally aligned")

    # Best raw layer
    best_raw = max(range(n_layers), key=lambda i: raw_corrs[i])
    best_neg = max(range(n_layers), key=lambda i: neg_corrs[i])
    print(f"\n  Best raw layer: {best_raw} ({results_per_layer[best_raw]['depth_pct']:.0f}%) corr={raw_corrs[best_raw]:.3f}")
    print(f"  Best YW-neg layer: {best_neg} ({results_per_layer[best_neg]['depth_pct']:.0f}%) corr={neg_corrs[best_neg]:.3f}")

    # B-W sign crossover
    crossovers = []
    for i in range(1, n_layers):
        if bw_vals[i-1] * bw_vals[i] < 0:
            crossovers.append(i)
    if crossovers:
        print(f"\n  B-W sign crossovers at layers: {crossovers}")
    else:
        print(f"\n  B-W never crosses zero (always {'positive' if bw_vals[0] > 0 else 'negative'})")

    # Save
    model_slug = args.model.replace("/", "_")
    output_path = args.output or f"results/crystal-phi-verify/{model_slug}_depth_scan.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def jsonable(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: jsonable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [jsonable(v) for v in obj]
        return obj

    with open(output_path, 'w') as f:
        json.dump(jsonable({
            "model": args.model,
            "n_layers": n_layers,
            "combinators": combinators,
            "n_per_combinator": args.n_per_combinator,
            "per_layer": results_per_layer,
        }), f, indent=2)
    print(f"\n  Saved to {output_path}")


if __name__ == "__main__":
    main()
