"""Full Loom Crossing Matrix — all weight matrices, all angles.

Pythia-2.8b has 5 weight matrices per layer, all touching d_model:
  W_q  (2560, 2560) — reads d_model, writes d_model (Q space)
  W_k  (2560, 2560) — reads d_model, writes d_model (K space)
  W_v  (2560, 2560) — reads d_model, writes d_model (V space)
  W_up (10240, 2560) — reads d_model, writes d_ffn
  W_down (2560, 10240) — reads d_ffn, writes d_model

In d_model space (the residual stream), we can compare:
  INPUT directions (Vt rows): W_q, W_k, W_v, W_up — all read from d_model
  OUTPUT directions (U cols):  W_q, W_k, W_v, W_down — all write to d_model

This gives us a full NxN crossing angle matrix at each layer.
Also: cross-layer crossings (layer L output → layer L+1 input).

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/loom_crossings_exp.py

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

MODEL_NAME = "EleutherAI/pythia-2.8b-deduped"
N_LAYERS = 32
D_MODEL = 2560
D_FFN = 10240
SVD_K = 64  # subspace dimension for comparisons

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "loom-crossings"


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def principal_angles_deg(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    Qa, _ = np.linalg.qr(A)
    Qb, _ = np.linalg.qr(B)
    svals = np.linalg.svd(Qa.T @ Qb, compute_uv=False)
    return np.degrees(np.arccos(np.clip(svals, 0, 1)))


def mean_angle(A: np.ndarray, B: np.ndarray) -> float:
    return float(principal_angles_deg(A, B).mean())


def angle_summary(A: np.ndarray, B: np.ndarray) -> dict:
    angles = principal_angles_deg(A, B)
    return {
        "mean": float(angles.mean()),
        "median": float(np.median(angles)),
        "min": float(angles.min()),
        "q25": float(np.percentile(angles, 25)),
        "q75": float(np.percentile(angles, 75)),
        "max": float(angles.max()),
    }


def extract_all_weights():
    """Extract W_q, W_k, W_v, W_up, W_down from every layer."""
    import torch
    from transformers import AutoModelForCausalLM

    log(f"  Loading {MODEL_NAME}...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float32, device_map="cpu")
    model.eval()

    layers_data = []
    for i in range(N_LAYERS):
        layer = model.gpt_neox.layers[i]
        qkv = layer.attention.query_key_value.weight.detach().float().numpy()
        W_q = qkv[:D_MODEL, :]
        W_k = qkv[D_MODEL:2*D_MODEL, :]
        W_v = qkv[2*D_MODEL:, :]
        W_up = layer.mlp.dense_h_to_4h.weight.detach().float().numpy()
        W_down = layer.mlp.dense_4h_to_h.weight.detach().float().numpy()
        layers_data.append({"q": W_q, "k": W_k, "v": W_v, "up": W_up, "down": W_down})
        if (i + 1) % 8 == 0:
            log(f"    Extracted {i+1}/{N_LAYERS}")

    del model
    gc.collect()
    return layers_data


def get_input_basis(W: np.ndarray, k: int) -> np.ndarray:
    """Top-k input directions (Vt rows) in d_model space. Returns (k, d_model)."""
    _, _, Vt = np.linalg.svd(W, full_matrices=False)
    return Vt[:k, :]


def get_output_basis(W: np.ndarray, k: int) -> np.ndarray:
    """Top-k output directions (U columns) in the output space. Returns (d_out, k)."""
    U, _, _ = np.linalg.svd(W, full_matrices=False)
    return U[:, :k]


# ══════════════════════════════════════════════════════════════════════
# TEST 1: Full input-side crossing matrix (all read from d_model)
# ══════════════════════════════════════════════════════════════════════

def test_input_crossings(layers_data, sample_layers):
    """NxN mean angle matrix between input spaces of all 4 weight types."""
    log(f"\n{'='*60}")
    log(f"TEST 1: Input-side crossing angles (d_model readers)")
    log(f"{'='*60}")

    input_names = ["q", "k", "v", "up"]
    results = []

    for li in sample_layers:
        ld = layers_data[li]
        bases = {}
        for name in input_names:
            bases[name] = get_input_basis(ld[name], SVD_K)  # (k, d_model)

        # Full crossing matrix
        matrix = {}
        for a in input_names:
            for b in input_names:
                if a <= b:  # upper triangle + diagonal
                    angles = angle_summary(bases[a].T, bases[b].T)
                    matrix[f"{a}↔{b}"] = angles

        results.append({"layer": li, "depth": li / (N_LAYERS - 1), "crossings": matrix})

        log(f"\n  Layer {li} (d={li/(N_LAYERS-1):.2f}):")
        log(f"  {'':6s} {'q':>8s} {'k':>8s} {'v':>8s} {'up':>8s}")
        for a in input_names:
            row = f"  {a:6s}"
            for b in input_names:
                key = f"{min(a,b)}↔{max(a,b)}"
                if key in matrix:
                    row += f" {matrix[key]['mean']:7.1f}°"
                else:
                    row += f" {'':>7s}"
            log(row)

    return results


# ══════════════════════════════════════════════════════════════════════
# TEST 2: Full output-side crossing matrix (all write to d_model)
# ══════════════════════════════════════════════════════════════════════

def test_output_crossings(layers_data, sample_layers):
    """NxN mean angle matrix between output spaces of W_q, W_k, W_v, W_down."""
    log(f"\n{'='*60}")
    log(f"TEST 2: Output-side crossing angles (d_model writers)")
    log(f"{'='*60}")

    output_names = ["q", "k", "v", "down"]
    results = []

    for li in sample_layers:
        ld = layers_data[li]
        bases = {}
        for name in output_names:
            bases[name] = get_output_basis(ld[name], SVD_K)  # (d_model, k)

        matrix = {}
        for a in output_names:
            for b in output_names:
                if a <= b:
                    angles = angle_summary(bases[a], bases[b])
                    matrix[f"{a}↔{b}"] = angles

        results.append({"layer": li, "depth": li / (N_LAYERS - 1), "crossings": matrix})

        log(f"\n  Layer {li} (d={li/(N_LAYERS-1):.2f}):")
        log(f"  {'':6s} {'q':>8s} {'k':>8s} {'v':>8s} {'down':>8s}")
        for a in output_names:
            row = f"  {a:6s}"
            for b in output_names:
                key = f"{min(a,b)}↔{max(a,b)}"
                if key in matrix:
                    row += f" {matrix[key]['mean']:7.1f}°"
                else:
                    row += f" {'':>7s}"
            log(row)

    return results


# ══════════════════════════════════════════════════════════════════════
# TEST 3: Cross-layer crossings (output of L → input of L+1)
# ══════════════════════════════════════════════════════════════════════

def test_cross_layer(layers_data):
    """How does each layer's output relate to the next layer's input?"""
    log(f"\n{'='*60}")
    log(f"TEST 3: Cross-layer crossings (L output → L+1 input)")
    log(f"{'='*60}")

    results = []
    for li in range(0, N_LAYERS - 1, 4):  # every 4th layer
        # Layer L outputs (in d_model): W_q, W_k, W_v, W_down
        # Layer L+1 inputs (from d_model): W_q, W_k, W_v, W_up
        out_q = get_output_basis(layers_data[li]["q"], SVD_K)
        out_v = get_output_basis(layers_data[li]["v"], SVD_K)
        out_down = get_output_basis(layers_data[li]["down"], SVD_K)

        in_q_next = get_input_basis(layers_data[li+1]["q"], SVD_K).T
        in_up_next = get_input_basis(layers_data[li+1]["up"], SVD_K).T

        angles = {
            "Wq_out→Wq_in": mean_angle(out_q, in_q_next),
            "Wq_out→Wup_in": mean_angle(out_q, in_up_next),
            "Wv_out→Wq_in": mean_angle(out_v, in_q_next),
            "Wv_out→Wup_in": mean_angle(out_v, in_up_next),
            "Wdown_out→Wq_in": mean_angle(out_down, in_q_next),
            "Wdown_out→Wup_in": mean_angle(out_down, in_up_next),
        }

        results.append({"layer": li, "to_layer": li + 1, "angles": angles})
        log(f"  L{li}→L{li+1}: "
            f"q→q={angles['Wq_out→Wq_in']:.1f}°, "
            f"v→q={angles['Wv_out→Wq_in']:.1f}°, "
            f"down→q={angles['Wdown_out→Wq_in']:.1f}°, "
            f"down→up={angles['Wdown_out→Wup_in']:.1f}°")

    return results


# ══════════════════════════════════════════════════════════════════════
# TEST 4: Angle spectrum histogram — find ALL characteristic angles
# ══════════════════════════════════════════════════════════════════════

def test_angle_spectrum(layers_data, sample_layers):
    """Collect ALL principal angles from all crossings, build histogram.
    Are there discrete peaks (characteristic loom angles)?"""
    log(f"\n{'='*60}")
    log(f"TEST 4: Angle spectrum — finding characteristic crossings")
    log(f"{'='*60}")

    all_angles = {"input_crossings": [], "output_crossings": [], "cross_type": []}

    for li in sample_layers:
        ld = layers_data[li]
        input_bases = {n: get_input_basis(ld[n], SVD_K).T for n in ["q", "k", "v", "up"]}
        output_bases = {n: get_output_basis(ld[n], SVD_K) for n in ["q", "k", "v", "down"]}

        # Input-side crossings
        for a in ["q", "k", "v", "up"]:
            for b in ["q", "k", "v", "up"]:
                if a < b:
                    angles = principal_angles_deg(input_bases[a], input_bases[b])
                    for ang in angles:
                        all_angles["input_crossings"].append(float(ang))
                        all_angles["cross_type"].append(f"in:{a}↔{b}")

        # Output-side crossings
        for a in ["q", "k", "v", "down"]:
            for b in ["q", "k", "v", "down"]:
                if a < b:
                    angles = principal_angles_deg(output_bases[a], output_bases[b])
                    for ang in angles:
                        all_angles["output_crossings"].append(float(ang))

    # Histogram
    bins = np.linspace(0, 90, 46)  # 2° bins
    hist_in, _ = np.histogram(all_angles["input_crossings"], bins=bins)
    hist_out, _ = np.histogram(all_angles["output_crossings"], bins=bins)

    # Find peaks
    from scipy.signal import find_peaks
    peaks_in, props_in = find_peaks(hist_in, height=max(hist_in) * 0.1, distance=3)
    peaks_out, props_out = find_peaks(hist_out, height=max(hist_out) * 0.1, distance=3)

    peak_angles_in = [(bins[p] + bins[p+1]) / 2 for p in peaks_in]
    peak_angles_out = [(bins[p] + bins[p+1]) / 2 for p in peaks_out]

    log(f"\n  Input-side angle peaks: {[f'{a:.0f}°' for a in peak_angles_in]}")
    log(f"  Output-side angle peaks: {[f'{a:.0f}°' for a in peak_angles_out]}")
    log(f"  Total input angles: {len(all_angles['input_crossings'])}")
    log(f"  Total output angles: {len(all_angles['output_crossings'])}")

    # Per-crossing-type statistics
    type_stats = {}
    for ang, ctype in zip(all_angles["input_crossings"], all_angles["cross_type"]):
        if ctype not in type_stats:
            type_stats[ctype] = []
        type_stats[ctype].append(ang)

    log(f"\n  Per-crossing-type mean angles:")
    for ctype in sorted(type_stats.keys()):
        vals = type_stats[ctype]
        log(f"    {ctype:15s}: mean={np.mean(vals):.1f}°, "
            f"median={np.median(vals):.1f}°, "
            f"min={np.min(vals):.1f}°")

    return {
        "histogram_input": {"bins": bins.tolist(), "counts": hist_in.tolist()},
        "histogram_output": {"bins": bins.tolist(), "counts": hist_out.tolist()},
        "peak_angles_input": peak_angles_in,
        "peak_angles_output": peak_angles_out,
        "per_type_means": {k: float(np.mean(v)) for k, v in type_stats.items()},
    }


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    layers_data = extract_all_weights()
    sample_layers = [0, 4, 8, 12, 16, 20, 24, 28, 31]

    results = {
        "input_crossings": test_input_crossings(layers_data, sample_layers),
        "output_crossings": test_output_crossings(layers_data, sample_layers),
        "cross_layer": test_cross_layer(layers_data),
        "angle_spectrum": test_angle_spectrum(layers_data, sample_layers),
    }

    elapsed = time.time() - t_start
    results["meta"] = {"model": MODEL_NAME, "svd_k": SVD_K,
                       "elapsed_seconds": elapsed}

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Loom Crossings")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s")
    log(f"  Results saved to {out_path}")


if __name__ == "__main__":
    main()
