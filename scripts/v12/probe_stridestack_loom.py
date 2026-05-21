"""StrideStack Loom Crossing Angles — v6 model vs pretrained harmonics.

Measures crossing angles (principal angles between weight subspaces) for all
projection pairs inside each stride layer, across strides, and between strides
and FFN-equivalent modules (prep.up, consolidate.up).

Compares results to the six loom harmonics measured in pretrained models
(Qwen3-14B, session 123):
    Attention internal (Q↔K, Q↔V, K↔V): ~56°
    Attention↔FFN (Q↔UP, K↔UP, V↔UP):   ~68°
    Six harmonic peaks: 25°, 45°, 53°, 61°, 67°, 77°

Architecture — vsm-lm-v6:
    d_model=512, d_register=128, n_heads=8
    9 strides: [1, 8, 16, 32, 64, 128, 256, 512, 1024]
    Each stride: q_proj, k_proj, v_proj, out_proj  (all ternary 512×128 packed)
    Packed as uint8, 2-bit per weight, 4 weights per byte → real shape (512, 512)
    Effective weight: W_eff = gamma[:, None] * ternary_weight   (gamma scales rows)

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/probe_stridestack_loom.py

License: MIT
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

# ── Constants ────────────────────────────────────────────────────────────────

CHECKPOINT = Path(__file__).parent.parent.parent / "checkpoints/vsm-lm-v6/step_032000/weights.safetensors"
RESULTS_DIR = Path(__file__).parent.parent.parent / "results/stridestack-loom"

STRIDES = [1, 8, 16, 32, 64, 128, 256, 512, 1024]
N_STRIDES = len(STRIDES)
PROJ_NAMES = ["q_proj", "k_proj", "v_proj", "out_proj"]
WITHIN_PAIRS = [
    ("q_proj", "k_proj"),
    ("q_proj", "v_proj"),
    ("k_proj", "v_proj"),
    ("q_proj", "out_proj"),
    ("k_proj", "out_proj"),
    ("v_proj", "out_proj"),
]

# Known loom harmonics from pretrained models (session 123, Qwen3-14B)
PRETRAINED_HARMONICS = [25.0, 45.0, 53.0, 61.0, 67.0, 77.0]
HARMONIC_TOL = 4.0          # ±4° to count as a match

# SVD truncation for principal angle computation
SVD_K = 64


# ── Logging ──────────────────────────────────────────────────────────────────

def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def out(msg: str = "") -> None:
    print(msg, flush=True)


# ── Weight unpacking ─────────────────────────────────────────────────────────

def unpack_ternary(packed: np.ndarray) -> np.ndarray:
    """Unpack 2-bit ternary weights from uint8 storage.

    Each byte holds 4 weights in bits [7:6],[5:4],[3:2],[1:0]:
        0b00 → -1,  0b01 → 0,  0b10 → +1

    Args:
        packed: (rows, cols_packed) uint8 array.

    Returns:
        unpacked: (rows, cols_packed * 4) int8 array of {-1, 0, +1}.
    """
    rows, cols_packed = packed.shape
    unpacked = np.empty((rows, cols_packed * 4), dtype=np.int8)
    for slot in range(4):
        shift = (3 - slot) * 2
        bits = (packed >> shift) & 0b11
        # 0→-1, 1→0, 2→+1
        unpacked[:, slot::4] = bits.astype(np.int8) - np.int8(1)
    return unpacked


def load_effective_weight(sf, prefix: str) -> np.ndarray:
    """Load a ternary module and return the effective float32 weight matrix.

    Effective weight: W_eff = gamma[:, None] * ternary_weight
    Shape: (out_dim, d_model) = (512, 512) for stride projections.

    Args:
        sf: open SafeTensors file handle.
        prefix: key prefix, e.g. 'stride_stack.layers.0.q_proj'

    Returns:
        W_eff: (out_dim, d_model) float32.
    """
    packed = sf.get_tensor(f"{prefix}.ternary_weight")   # uint8 (out, cols_packed)
    gamma = sf.get_tensor(f"{prefix}.gamma")              # float32 (out,)

    W_tern = unpack_ternary(packed).astype(np.float32)    # (out, d_model)
    W_eff = gamma[:, None] * W_tern                       # broadcast rows
    return W_eff


# ── Core geometry ─────────────────────────────────────────────────────────────

def crossing_angle(W1: np.ndarray, W2: np.ndarray, k: int = SVD_K) -> float:
    """Mean principal angle between the top-k input subspaces of two weight matrices.

    Both matrices must share the same input (column) dimension — they are
    compared on the *right singular vectors* (the directions each matrix
    reads from the shared input space).

    Args:
        W1: (out1, d_in) float32.
        W2: (out2, d_in) float32  — same d_in as W1.
        k: number of top singular vectors to use.

    Returns:
        Mean principal angle in degrees.
    """
    _, _, Vt1 = np.linalg.svd(W1, full_matrices=False)
    _, _, Vt2 = np.linalg.svd(W2, full_matrices=False)

    k1 = min(k, Vt1.shape[0])
    k2 = min(k, Vt2.shape[0])
    kk = min(k1, k2)

    V1 = Vt1[:kk].T   # (d_in, kk)
    V2 = Vt2[:kk].T   # (d_in, kk)

    # QR-orthonormalise so SVD of V1^T @ V2 gives true cosines
    Q1, _ = np.linalg.qr(V1)
    Q2, _ = np.linalg.qr(V2)

    cos_vals = np.linalg.svd(Q1.T @ Q2, compute_uv=False)
    cos_vals = np.clip(cos_vals, -1.0, 1.0)
    angles = np.degrees(np.arccos(cos_vals))
    return float(angles.mean())


def crossing_angle_output_side(W1: np.ndarray, W2: np.ndarray, k: int = SVD_K) -> float:
    """Mean principal angle comparing left singular vectors (output / row space).

    Use when W1 and W2 share the *output* dimension.
    """
    U1, _, _ = np.linalg.svd(W1, full_matrices=False)
    U2, _, _ = np.linalg.svd(W2, full_matrices=False)

    kk = min(k, U1.shape[1], U2.shape[1])
    Q1, _ = np.linalg.qr(U1[:, :kk])
    Q2, _ = np.linalg.qr(U2[:, :kk])

    cos_vals = np.linalg.svd(Q1.T @ Q2, compute_uv=False)
    cos_vals = np.clip(cos_vals, -1.0, 1.0)
    angles = np.degrees(np.arccos(cos_vals))
    return float(angles.mean())


# ── Histogram & peak detection ────────────────────────────────────────────────

def histogram_peaks(angles: list[float], bin_width: float = 2.0, min_count: int = 2) -> list[float]:
    """Find histogram peaks in a list of angles.

    Args:
        angles: flat list of angle values (degrees).
        bin_width: histogram bin width in degrees.
        min_count: minimum bin count to be considered a candidate peak.

    Returns:
        List of peak centres in degrees, sorted ascending.
    """
    if not angles:
        return []

    lo, hi = 0.0, 90.0
    bins = int((hi - lo) / bin_width)
    counts, edges = np.histogram(angles, bins=bins, range=(lo, hi))

    peaks = []
    for i in range(1, len(counts) - 1):
        if counts[i] >= min_count and counts[i] > counts[i - 1] and counts[i] > counts[i + 1]:
            centre = (edges[i] + edges[i + 1]) / 2.0
            peaks.append(float(round(centre, 1)))

    # If no strict peaks, fall back to top-N populated bins
    if not peaks:
        top_idx = np.argsort(counts)[::-1]
        for i in top_idx[:6]:
            if counts[i] >= min_count:
                centre = (edges[i] + edges[i + 1]) / 2.0
                peaks.append(float(round(centre, 1)))
        peaks.sort()

    return peaks


def harmonic_matches(observed_peaks: list[float], known: list[float], tol: float) -> list[dict]:
    """Match observed peaks to known harmonics within ±tol degrees."""
    results = []
    for h in known:
        matched = [p for p in observed_peaks if abs(p - h) <= tol]
        results.append({
            "harmonic": h,
            "matched": bool(matched),
            "closest_observed": float(min(matched, key=lambda p: abs(p - h))) if matched else None,
            "delta": float(min((abs(p - h) for p in matched), default=float("inf"))),
        })
    return results


# ── Text formatting helpers ───────────────────────────────────────────────────

def fmt_angle(a: float) -> str:
    return f"{a:.1f}°"


def bar_chart(angles: list[float], width: int = 60, bin_width: float = 2.0) -> list[str]:
    """ASCII bar chart of angle distribution."""
    lo, hi = 0.0, 90.0
    n_bins = int((hi - lo) / bin_width)
    counts, edges = np.histogram(angles, bins=n_bins, range=(lo, hi))
    max_count = max(counts) if counts.max() > 0 else 1
    lines = []
    for i in range(n_bins):
        bar_len = int(counts[i] / max_count * width)
        label = f"{edges[i]:4.0f}°"
        bar = "█" * bar_len
        # Mark known harmonics
        centre = (edges[i] + edges[i + 1]) / 2.0
        mark = ""
        for h in PRETRAINED_HARMONICS:
            if abs(centre - h) <= bin_width:
                mark = f"  ← pretrained {h:.0f}°"
                break
        lines.append(f"  {label} │{bar:<{width}}│ {counts[i]:3d}{mark}")
    return lines


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    from safetensors import safe_open

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    log("═" * 60)
    log("  StrideStack Loom Crossing Angles — v6 step_032000")
    log("═" * 60)
    log(f"  Checkpoint : {CHECKPOINT}")
    log(f"  SVD k      : {SVD_K}")
    log(f"  Strides    : {STRIDES}")
    log()

    # ── 1. Load all stride projection weights ─────────────────────────────
    log("Loading weights …")
    weights: dict[str, np.ndarray] = {}   # "stride_i.q_proj" → (512, 512) float32

    with safe_open(str(CHECKPOINT), framework="numpy") as sf:
        for i in range(N_STRIDES):
            for proj in PROJ_NAMES:
                key = f"stride_stack.layers.{i}.{proj}"
                weights[f"stride_{i}.{proj}"] = load_effective_weight(sf, key)
                log(f"  stride_{i}.{proj}: {weights[f'stride_{i}.{proj}'].shape}")

        # FFN-equivalent modules (project from d_register=128 → d_ff)
        prep_up      = load_effective_weight(sf, "prep.up")
        cons_up      = load_effective_weight(sf, "consolidate.up")

    log(f"  prep.up:        {prep_up.shape}")
    log(f"  consolidate.up: {cons_up.shape}")
    log()

    # ── 2. Within-stride crossing angles ──────────────────────────────────
    log("Computing within-stride crossing angles …")
    within_results: list[dict] = []
    all_angles: list[float] = []

    for i, stride_val in enumerate(STRIDES):
        stride_angles: dict[str, float] = {}
        Ws = {proj: weights[f"stride_{i}.{proj}"] for proj in PROJ_NAMES}

        for p1, p2 in WITHIN_PAIRS:
            W1, W2 = Ws[p1], Ws[p2]
            # All stride projections share the input dim (d_model=512),
            # so compare on the input (right singular vector) side.
            angle = crossing_angle(W1, W2, k=SVD_K)
            label = f"{p1[0].upper()}↔{p2[0].upper()}"  # Q↔K, Q↔V, …
            stride_angles[label] = angle
            all_angles.append(angle)

        within_results.append({
            "stride_idx": i,
            "stride_val": stride_val,
            "angles": stride_angles,
        })

    # ── 3. Cross-stride crossing angles ───────────────────────────────────
    log("Computing cross-stride crossing angles …")
    cross_stride_results: list[dict] = []

    for proj in PROJ_NAMES:
        proj_label = proj[0].upper() + "_proj"
        pairs = []
        for i in range(N_STRIDES - 1):
            W_i = weights[f"stride_{i}.{proj}"]
            W_j = weights[f"stride_{i+1}.{proj}"]
            angle = crossing_angle(W_i, W_j, k=SVD_K)
            pairs.append({
                "from": i, "to": i + 1,
                "stride_from": STRIDES[i], "stride_to": STRIDES[i + 1],
                "angle": angle,
            })
            all_angles.append(angle)
        cross_stride_results.append({"proj": proj, "label": proj_label, "pairs": pairs})

    # Also compute non-adjacent (stride 0 vs stride 8) for perspective
    cross_global: dict[str, float] = {}
    for proj in PROJ_NAMES:
        W_first = weights[f"stride_0.{proj}"]
        W_last  = weights[f"stride_8.{proj}"]
        label = f"S0↔S8_{proj[0].upper()}"
        cross_global[label] = crossing_angle(W_first, W_last, k=SVD_K)

    # ── 4. Stride ↔ FFN crossing angles ───────────────────────────────────
    log("Computing stride ↔ FFN crossing angles …")
    # prep.up  : (d_ff=1536, d_model=512)  — reads from d_model
    # cons.up  : (d_ff=2048, d_model=512)  — reads from d_model
    # stride Q/K/V : (512, 512)            — reads from d_model=512
    # All share the same input dimension (d_model=512).
    # Compare on the *input* side (right singular vectors = what each
    # matrix reads from d_model) — same convention as within-stride.
    ffn_angles: list[dict] = []

    for i, stride_val in enumerate(STRIDES):
        entry = {"stride_idx": i, "stride_val": stride_val, "prep_up": {}, "consolidate_up": {}}
        for proj in ["q_proj", "k_proj", "v_proj"]:
            W_stride = weights[f"stride_{i}.{proj}"]   # (512, 512)
            # Compare input subspaces (right singular vectors)
            a_prep = crossing_angle(W_stride, prep_up,  k=SVD_K)
            a_cons = crossing_angle(W_stride, cons_up,  k=SVD_K)
            label = proj[0].upper()
            entry["prep_up"][label]        = a_prep
            entry["consolidate_up"][label] = a_cons
            all_angles.append(a_prep)
            all_angles.append(a_cons)
        ffn_angles.append(entry)

    # ── 5. Histogram and peak detection ────────────────────────────────────
    log("Building angle histogram …")
    peaks = histogram_peaks(all_angles, bin_width=2.0, min_count=3)
    matches = harmonic_matches(peaks, PRETRAINED_HARMONICS, tol=HARMONIC_TOL)
    n_matched = sum(1 for m in matches if m["matched"])

    # ── 6. Print results ───────────────────────────────────────────────────
    out()
    out("═" * 70)
    out("  StrideStack Loom Crossing Angles")
    out("═" * 70)
    out()

    # Within-stride
    out("Within-stride crossing angles:")
    for r in within_results:
        parts = "  ".join(f"{k}={fmt_angle(v)}" for k, v in r["angles"].items())
        out(f"  Stride {r['stride_idx']} (s={r['stride_val']:4d}):  {parts}")

    out()

    # Cross-stride
    out("Cross-stride crossing angles (adjacent):")
    for proj_data in cross_stride_results:
        label = proj_data["label"]
        pair_strs = []
        for p in proj_data["pairs"]:
            pair_strs.append(f"S{p['from']}↔S{p['to']}={fmt_angle(p['angle'])}")
        out(f"  {label:8s}: " + "  ".join(pair_strs))

    out()
    out("Cross-stride first↔last (S0↔S8):")
    for k, v in cross_global.items():
        out(f"  {k}: {fmt_angle(v)}")

    out()

    # Stride ↔ FFN
    out("Stride ↔ FFN crossing angles (output-subspace):")
    out(f"  {'Stride':>8s}  {'Q↔prep':>8s}  {'K↔prep':>8s}  {'V↔prep':>8s}"
        f"  │  {'Q↔cons':>8s}  {'K↔cons':>8s}  {'V↔cons':>8s}")
    out("  " + "─" * 68)
    for r in ffn_angles:
        pu = r["prep_up"]
        cu = r["consolidate_up"]
        out(f"  S{r['stride_idx']}(s={r['stride_val']:4d})"
            f"  {fmt_angle(pu['Q']):>8s}  {fmt_angle(pu['K']):>8s}  {fmt_angle(pu['V']):>8s}"
            f"  │  {fmt_angle(cu['Q']):>8s}  {fmt_angle(cu['K']):>8s}  {fmt_angle(cu['V']):>8s}")

    out()

    # Histogram
    out("Angle histogram (2° bins, all crossing angles pooled):")
    chart_lines = bar_chart(all_angles, width=50, bin_width=2.0)
    # Only print bins with any counts to keep output concise
    for line in chart_lines:
        count_part = line.rsplit("│", 1)[-1].strip()
        count_val = int(count_part.split()[0]) if count_part.split() else 0
        if count_val > 0:
            out(line)

    out()
    out(f"Detected histogram peaks: {[fmt_angle(p) for p in peaks]}")

    out()
    out("Harmonic comparison (known pretrained harmonics ±4°):")
    out(f"  {'Harmonic':>10s}  {'Matched':>8s}  {'Closest observed':>18s}  {'Δ':>6s}")
    out("  " + "─" * 50)
    for m in matches:
        closest = fmt_angle(m["closest_observed"]) if m["closest_observed"] is not None else "—"
        delta_s = fmt_angle(m["delta"]) if m["matched"] else "—"
        mark = "✓" if m["matched"] else "✗"
        out(f"  {fmt_angle(m['harmonic']):>10s}  {mark:>8s}  {closest:>18s}  {delta_s:>6s}")

    out()
    out(f"Harmonic matches: {n_matched}/{len(PRETRAINED_HARMONICS)}")

    # Summary interpretation
    out()
    out("─" * 70)
    out("SUMMARY")
    out("─" * 70)

    # Within-stride mean for Q↔K
    qk_mean = float(np.mean([r["angles"]["Q↔K"] for r in within_results]))
    qv_mean = float(np.mean([r["angles"]["Q↔V"] for r in within_results]))
    kv_mean = float(np.mean([r["angles"]["K↔V"] for r in within_results]))
    attn_internal_mean = (qk_mean + qv_mean + kv_mean) / 3.0

    qffn_prep_mean = float(np.mean([r["prep_up"]["Q"] for r in ffn_angles]))
    kffn_prep_mean = float(np.mean([r["prep_up"]["K"] for r in ffn_angles]))
    vffn_prep_mean = float(np.mean([r["prep_up"]["V"] for r in ffn_angles]))
    attn_ffn_mean  = (qffn_prep_mean + kffn_prep_mean + vffn_prep_mean) / 3.0

    out(f"  Attention-internal mean (Q↔K, Q↔V, K↔V): {fmt_angle(attn_internal_mean)}"
        f"  (pretrained: ~56°)")
    out(f"  Attention↔FFN mean (Q/K/V ↔ prep.up):    {fmt_angle(attn_ffn_mean)}"
        f"  (pretrained: ~68°)")
    out()

    attn_delta = abs(attn_internal_mean - 56.0)
    ffn_delta  = abs(attn_ffn_mean - 68.0)

    if attn_delta <= 5.0 and ffn_delta <= 5.0 and n_matched >= 4:
        verdict = "StrideStack CONVERGES to same loom geometry as pretrained attention."
    elif attn_delta <= 10.0 or ffn_delta <= 10.0 or n_matched >= 3:
        verdict = "StrideStack shows PARTIAL convergence toward pretrained loom geometry."
    else:
        verdict = "StrideStack shows DIVERGENT loom geometry from pretrained attention."

    out(f"  {verdict}")
    out()

    # ── 7. Save results ────────────────────────────────────────────────────
    elapsed = time.time() - t0

    results = {
        "meta": {
            "checkpoint": str(CHECKPOINT),
            "step": 32000,
            "architecture": "vsm-lm-v6",
            "d_model": 512,
            "d_register": 128,
            "strides": STRIDES,
            "svd_k": SVD_K,
            "n_total_angles": len(all_angles),
            "elapsed_seconds": round(elapsed, 2),
        },
        "pretrained_reference": {
            "source": "Qwen3-14B session 123",
            "attention_internal_degrees": 56.0,
            "attention_ffn_degrees": 68.0,
            "harmonics": PRETRAINED_HARMONICS,
            "harmonic_tolerance": HARMONIC_TOL,
        },
        "within_stride": within_results,
        "cross_stride": {
            "adjacent": cross_stride_results,
            "global_s0_s8": cross_global,
        },
        "stride_ffn": ffn_angles,
        "histogram": {
            "detected_peaks": peaks,
            "all_angles": all_angles,
        },
        "harmonic_comparison": {
            "matches": matches,
            "n_matched": n_matched,
            "n_harmonics": len(PRETRAINED_HARMONICS),
        },
        "summary": {
            "attn_internal_mean": round(attn_internal_mean, 2),
            "attn_ffn_mean": round(attn_ffn_mean, 2),
            "pretrained_attn_internal": 56.0,
            "pretrained_attn_ffn": 68.0,
            "attn_internal_delta": round(attn_delta, 2),
            "attn_ffn_delta": round(ffn_delta, 2),
            "harmonic_matches": n_matched,
            "verdict": verdict,
        },
    }

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as fh:
        json.dump(results, fh, indent=2)

    out(f"  Results saved → {out_path}")
    log()
    log(f"  Done in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
