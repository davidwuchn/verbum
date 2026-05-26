#!/usr/bin/env python3
"""
Probe: Can ternary plates be encoded as geometry?

If computation collapses to 2D (PR=2.2), the d×d ternary plate
T = V @ Λ @ V^T where V is d×k (positions in k-D space), Λ is k×k.

sign(T[i,j]) should be predictable from the positions V[i,:] and V[j,:]
plus the transform Λ. If so:

  d×d ternary matrix (d² entries) → d positions in kD (d×k entries)

For d=1280, k=2: 1,638,400 → 2,560 values. 640× compression.
For d=4096, k=2: 16,777,216 → 8,192 values. 2048× compression.

This probe tests:
  1. How well does T_reconstructed = V[:,:k] @ Λ[:k,:k] @ V[:,:k]^T
     predict sign(T) for various k?
  2. What k achieves 90%, 95%, 99% sign prediction accuracy?
  3. How does per-dim correlation of the geometric encoding compare?

Uses the algebraic T_full already computed.

License: MIT
"""

from __future__ import annotations

import time
import json
from pathlib import Path

import numpy as np

CACHE_ALGEBRAIC = Path("results/extraction-dimension-sweep/T_full.npy")
CACHE_DATAFITTED = Path("results/datafitted-dimension-sweep/teacher_transforms.npz")


def analyze_geometric_encoding(T, label, max_k=256):
    """Test geometric encoding at various k values."""
    print(f"\n{'='*70}")
    print(f"  {label}: shape={T.shape}")
    print(f"{'='*70}")

    d = T.shape[0]

    # SVD of T
    U, S, Vt = np.linalg.svd(T, full_matrices=False)
    V = Vt.T  # (d, d) — columns are right singular vectors

    total_energy = np.sum(S**2)
    cum_energy = np.cumsum(S**2) / total_energy

    # The actual sign matrix
    sign_T = np.sign(T)
    n_nonzero = np.sum(sign_T != 0)
    n_pos = np.sum(sign_T == 1)
    n_neg = np.sum(sign_T == -1)
    n_zero = np.sum(sign_T == 0)

    print(f"\n  Sign distribution: +1={n_pos/T.size:.1%}  -1={n_neg/T.size:.1%}  0={n_zero/T.size:.1%}")

    # Full ternary quality (sign+gamma baseline)
    gamma = np.mean(np.abs(T), axis=1)
    x_test = np.random.randn(500, d).astype(np.float32)
    y_full = x_test @ T.T
    y_tern = (x_test @ sign_T.astype(np.float32).T) * gamma[None, :]
    baseline_pd = []
    for dim in range(d):
        if y_full[:, dim].std() > 1e-10:
            c = np.corrcoef(y_full[:, dim], y_tern[:, dim])[0, 1]
            if not np.isnan(c):
                baseline_pd.append(c)
    baseline_per_dim = float(np.mean(baseline_pd))
    print(f"  Baseline (full sign+gamma): per_dim={baseline_per_dim:.4f}")

    # Sweep k
    k_values = sorted(set([
        1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 27, 32,
        48, 64, 96, 128, 160, 192, 256,
        384, 512, 640, 768, 896, 1024, 1280,
    ]))
    k_values = [k for k in k_values if k <= min(d, max_k)]

    results = []

    print(f"\n  {'k':>6s} | {'sign_acc':>9s} | {'nonzero_acc':>11s} | {'per_dim':>8s} | {'global':>8s} | "
          f"{'sv_energy':>10s} | {'positions':>10s} | {'encoding':>10s} | {'ratio':>6s}")
    print(f"  {'-'*6} | {'-'*9} | {'-'*11} | {'-'*8} | {'-'*8} | "
          f"{'-'*10} | {'-'*10} | {'-'*10} | {'-'*6}")

    for k in k_values:
        # Reconstruct T from rank-k approximation
        # T_k = U[:,:k] @ diag(S[:k]) @ Vt[:k,:] = (U[:,:k] * S[:k]) @ Vt[:k,:]
        T_k = (U[:, :k] * S[:k]) @ Vt[:k, :]

        # Geometric encoding: positions = V[:,:k] (or U[:,:k] * sqrt(S[:k]))
        # The ternary plate from reconstruction
        sign_T_k = np.sign(T_k)

        # Sign prediction accuracy
        # How many signs does T_k get right?
        correct = np.sum(sign_T_k == sign_T)
        sign_acc = correct / T.size

        # Accuracy on nonzero entries only (more meaningful)
        nonzero_mask = sign_T != 0
        if nonzero_mask.sum() > 0:
            nonzero_acc = np.sum(sign_T_k[nonzero_mask] == sign_T[nonzero_mask]) / nonzero_mask.sum()
        else:
            nonzero_acc = 0.0

        # Per-dim correlation of geometric ternary vs original T
        gamma_k = np.mean(np.abs(T_k), axis=1)
        y_geom = (x_test @ sign_T_k.astype(np.float32).T) * gamma_k[None, :]
        pd = []
        for dim in range(d):
            if y_full[:, dim].std() > 1e-10:
                c = np.corrcoef(y_full[:, dim], y_geom[:, dim])[0, 1]
                if not np.isnan(c):
                    pd.append(c)
        mean_pd = float(np.mean(pd)) if pd else 0.0

        gc = float(np.corrcoef(y_full.flatten(), y_geom.flatten())[0, 1])

        sv_energy = float(cum_energy[k-1])

        # Encoding size: d × k values (the positions) + k singular values + k×k rotation
        encoding_values = d * k + k + k * k
        original_values = d * d

        result = {
            "k": k,
            "sign_accuracy": float(sign_acc),
            "nonzero_accuracy": float(nonzero_acc),
            "per_dim_corr": mean_pd,
            "global_corr": gc,
            "sv_energy": sv_energy,
            "encoding_values": encoding_values,
            "original_values": original_values,
            "compression_ratio": original_values / encoding_values,
            "encoding_bytes_16bit": encoding_values * 2,
            "original_bytes_packed": original_values // 4,  # 2 bits per ternary
        }
        results.append(result)

        flag = ""
        if float(sign_acc) >= 0.95 and (not results[:-1] or results[-2]['sign_accuracy'] < 0.95):
            flag = " ← 95% sign"
        if float(nonzero_acc) >= 0.95 and (not results[:-1] or results[-2]['nonzero_accuracy'] < 0.95):
            flag = flag or " ← 95% nz"
        if float(mean_pd) >= 0.95 and (not results[:-1] or results[-2]['per_dim_corr'] < 0.95):
            flag = flag or " ← 95% pd"

        print(f"  {k:>6d} | {sign_acc:>9.4f} | {nonzero_acc:>11.4f} | {mean_pd:>8.4f} | {gc:>8.4f} | "
              f"{sv_energy:>10.6f} | {original_values:>10,} | {encoding_values:>10,} | "
              f"{original_values/encoding_values:>5.0f}×{flag}")

    # Also test: what if we use quantized positions?
    # In 2D: each position = 2 × 16-bit = 32 bits per dimension
    # In 3D: each position = 3 × 16-bit = 48 bits per dimension
    print(f"\n  Geometric encoding size comparison (d={d}):")
    for k in [2, 3, 4, 8, 16, 27]:
        if k > max_k:
            continue
        enc_bits_16b = d * k * 16  # positions at 16-bit precision
        enc_bits_8b = d * k * 8    # positions at 8-bit precision
        orig_bits = d * d * 2      # packed ternary (2 bits each)
        r = next((r for r in results if r['k'] == k), None)
        acc = r['sign_accuracy'] if r else 0
        pd = r['per_dim_corr'] if r else 0
        print(f"    k={k}: {enc_bits_16b/8/1024:.1f} KB (16b) / {enc_bits_8b/8/1024:.1f} KB (8b) "
              f"vs {orig_bits/8/1024:.1f} KB packed ternary "
              f"| sign_acc={acc:.4f} per_dim={pd:.4f} "
              f"| ratio={orig_bits/enc_bits_16b:.0f}× (16b) / {orig_bits/enc_bits_8b:.0f}× (8b)")

    return results


def main():
    np.random.seed(42)
    t0 = time.time()

    all_results = {}

    # Test on algebraic T_full (5120×5120) if available
    if CACHE_ALGEBRAIC.exists():
        print(f"\n  Loading algebraic T_full...", flush=True)
        T_alg = np.load(str(CACHE_ALGEBRAIC))
        all_results["algebraic_5120"] = analyze_geometric_encoding(
            T_alg, "Algebraic Full Model (5120×5120)", max_k=256)

    # Test on data-fitted transforms if available
    if CACHE_DATAFITTED.exists():
        print(f"\n  Loading data-fitted transforms...", flush=True)
        data = np.load(str(CACHE_DATAFITTED))
        T_df = data["T_full"]
        all_results["datafitted_5120"] = analyze_geometric_encoding(
            T_df, "Data-Fitted Full Model (5120×5120)", max_k=256)

    # Also test on the STUDENT-space plates (1280×1280)
    composed_path = Path("checkpoints/v14-composed/composed_plates.npz")
    if composed_path.exists():
        print(f"\n  Loading student-space composed plates...", flush=True)
        plates = np.load(str(composed_path))
        signs = plates["full_signs"].astype(np.float32)
        gamma = plates["full_gamma"]
        # Reconstruct the float transform from sign+gamma
        T_student = signs * gamma[:, None]
        all_results["student_1280"] = analyze_geometric_encoding(
            T_student, "Student Full Plate (1280×1280)", max_k=256)

    # Save
    out_dir = Path("results/geometric-encoding")
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "results.json", "w") as f:
        json.dump(all_results, f, indent=2,
                  default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else x)

    dt = time.time() - t0
    print(f"\n{'='*70}")
    print(f"  All done in {dt:.0f}s")
    print(f"  Saved to {out_dir}/results.json")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
