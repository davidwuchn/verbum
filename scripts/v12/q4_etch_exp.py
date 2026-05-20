"""Q4 Etch Refinement — Can we refocus the beam after quantization?

Q4 flips 12% of signs at the bottom 6th percentile of magnitude.
Crystal fidelity drops from 1.000 to 0.933. Can etching recover it?

Protocol:
  1. Full-precision W_q at layer 16 (Pythia-2.8b)
  2. Q4 simulate → identify all sign flips
  3. Test recovery strategies:
     a. ORACLE: fix all known flips (ceiling)
     b. RESIDUAL-GUIDED: sort flips by |W_orig - W_q4|, fix largest first
     c. Q4-MAG-GUIDED: sort ALL positions by Q4 magnitude, flip signs of
        lowest-magnitude positions toward the gradient direction
        (simulates: "near-zero Q4 weights are likely wrong")
     d. RANDOM: fix random subset of flips (baseline)
  4. Progressive curve: fix N signs at a time, measure crystal recovery

Also test at multiple quantization levels (8,4,3,2 bit) to see
where etching helps most.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/q4_etch_exp.py

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
TARGET_LAYER = 16

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "q4-etch"


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def cosine_rdm(X):
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    return (X / norms) @ (X / norms).T


def rdm_correlation(A, B):
    n = A.shape[0]
    idx = np.triu_indices(n, k=1)
    a = A[idx] - A[idx].mean()
    b = B[idx] - B[idx].mean()
    denom = np.sqrt(np.sum(a**2)) * np.sqrt(np.sum(b**2))
    return float(np.sum(a * b) / denom) if denom > 1e-10 else 0.0


def q4_simulate(W, n_bits=4, block_size=32):
    """Block-wise symmetric quantization."""
    if n_bits == 1:
        return np.sign(W).astype(np.float32)
    W_flat = W.flatten()
    n = len(W_flat)
    pad = (block_size - n % block_size) % block_size
    W_padded = np.concatenate([W_flat, np.zeros(pad)])
    W_blocks = W_padded.reshape(-1, block_size)
    n_levels = 2 ** (n_bits - 1)
    scales = np.maximum(np.max(np.abs(W_blocks), axis=1, keepdims=True), 1e-10)
    W_norm = W_blocks / scales
    W_quant = np.round(W_norm * n_levels).clip(-n_levels, n_levels)
    W_dequant = (W_quant / n_levels) * scales
    return W_dequant.flatten()[:n].reshape(W.shape).astype(np.float32)


def extract_W_q():
    import torch
    from transformers import AutoModelForCausalLM
    log(f"  Loading {MODEL_NAME}...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float32, device_map="cpu")
    model.eval()
    qkv = model.gpt_neox.layers[TARGET_LAYER].attention.query_key_value.weight.detach().float().numpy()
    W_q = qkv[:D_MODEL, :]
    del model; gc.collect()
    return W_q


def measure_crystal(W):
    """Crystal fidelity of sign(W) vs sign(W_original)."""
    return cosine_rdm(np.sign(W).astype(np.float32))


# ══════════════════════════════════════════════════════════════════════
# TEST 1: Progressive etch recovery after Q4
# ══════════════════════════════════════════════════════════════════════

def test_progressive_etch(W_orig, n_bits=4):
    """Fix sign errors progressively, measure crystal recovery."""
    log(f"\n{'='*60}")
    log(f"Progressive etch recovery — {n_bits}-bit quantization")
    log(f"{'='*60}")

    W_q4 = q4_simulate(W_orig, n_bits=n_bits)
    sign_orig = np.sign(W_orig)
    sign_q4 = np.sign(W_q4)
    rdm_orig = cosine_rdm(sign_orig.astype(np.float32))

    # Identify all sign flips
    flip_mask = (sign_orig != sign_q4)
    n_flips = int(flip_mask.sum())
    n_total = W_orig.size
    log(f"  {n_flips:,} sign flips ({n_flips/n_total*100:.1f}% of {n_total:,})")

    # Baseline: Q4 crystal fidelity
    rdm_q4 = cosine_rdm(sign_q4.astype(np.float32))
    fid_q4 = rdm_correlation(rdm_orig, rdm_q4)
    log(f"  Q4 baseline crystal fidelity: {fid_q4:.6f}")

    # Strategy A: ORACLE — fix all known flips
    sign_oracle = sign_q4.copy()
    sign_oracle[flip_mask] = sign_orig[flip_mask]
    fid_oracle = rdm_correlation(rdm_orig, cosine_rdm(sign_oracle.astype(np.float32)))
    log(f"  Oracle (fix all flips): {fid_oracle:.6f}")

    # Compute residual magnitude at each flip site
    residual = np.abs(W_orig - W_q4)
    orig_mag = np.abs(W_orig)
    q4_mag = np.abs(W_q4)

    # Get flip positions sorted by different criteria
    flip_positions = np.argwhere(flip_mask.flatten()).flatten()

    # Strategy B: RESIDUAL-GUIDED (sort by |W_orig - W_q4| descending)
    residual_at_flips = residual.flatten()[flip_positions]
    order_residual = flip_positions[np.argsort(-residual_at_flips)]

    # Strategy C: ORIG-MAG-GUIDED (sort by |W_orig| descending at flip sites)
    origmag_at_flips = orig_mag.flatten()[flip_positions]
    order_origmag = flip_positions[np.argsort(-origmag_at_flips)]

    # Strategy D: Q4-MAG-GUIDED (sort ALL positions by Q4 magnitude ascending,
    # flip the lowest-magnitude Q4 positions toward orig sign)
    # This simulates: "without access to original, near-zero Q4 weights are suspect"
    q4_flat = q4_mag.flatten()
    all_positions_by_q4mag = np.argsort(q4_flat)  # ascending magnitude
    # Filter to only actual flip sites
    flip_set = set(flip_positions)
    order_q4mag = np.array([p for p in all_positions_by_q4mag if p in flip_set])

    # Strategy E: RANDOM
    rng = np.random.RandomState(42)
    order_random = rng.permutation(flip_positions)

    # Progressive curves
    fix_fractions = [0.0, 0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 1.0]
    strategies = {
        "residual": order_residual,
        "orig_mag": order_origmag,
        "q4_mag": order_q4mag,
        "random": order_random,
    }

    results = {"n_bits": n_bits, "n_flips": n_flips, "n_total": n_total,
               "fid_q4_baseline": fid_q4, "fid_oracle": fid_oracle,
               "curves": {}}

    for sname, order in strategies.items():
        curve = []
        for frac in fix_fractions:
            n_fix = min(int(frac * n_flips), len(order))
            sign_fixed = sign_q4.copy().flatten()
            if n_fix > 0:
                positions_to_fix = order[:n_fix]
                sign_fixed[positions_to_fix] = sign_orig.flatten()[positions_to_fix]
            sign_fixed = sign_fixed.reshape(W_orig.shape)

            fid = rdm_correlation(rdm_orig, cosine_rdm(sign_fixed.astype(np.float32)))
            curve.append({"fix_frac": frac, "n_fixed": n_fix, "fidelity": float(fid)})

        results["curves"][sname] = curve

        # Print key points
        fids = {c["fix_frac"]: c["fidelity"] for c in curve}
        log(f"  {sname:12s}: 0%={fids[0.0]:.4f} → 5%={fids[0.05]:.4f} → "
            f"20%={fids[0.20]:.4f} → 100%={fids[1.0]:.4f}")

    return results


# ══════════════════════════════════════════════════════════════════════
# TEST 2: Blind etch (no access to original — realistic scenario)
# ══════════════════════════════════════════════════════════════════════

def test_blind_etch(W_orig, n_bits=4):
    """Without knowing the original, can we identify and fix sign errors?

    Strategy: Q4 weights near zero are suspect. For each near-zero weight,
    the sign of the PRE-QUANTIZATION gradient tells us the correct direction.
    We simulate this with: sign should be sign(residual block mean) — i.e.,
    the average direction that nearby weights want to go.
    """
    log(f"\n{'='*60}")
    log(f"Blind etch — {n_bits}-bit (no original access)")
    log(f"{'='*60}")

    W_q4 = q4_simulate(W_orig, n_bits=n_bits)
    sign_orig = np.sign(W_orig)
    sign_q4 = np.sign(W_q4)
    rdm_orig = cosine_rdm(sign_orig.astype(np.float32))

    flip_mask = (sign_orig != sign_q4)
    n_flips = int(flip_mask.sum())

    fid_baseline = rdm_correlation(rdm_orig, cosine_rdm(sign_q4.astype(np.float32)))

    # Blind strategy: for each position, compute a "confidence" that the sign is correct
    # Low |Q4 weight| = low confidence = likely flip target
    # The DIRECTION to flip: use local gradient approximation
    # Gradient ≈ -(W_q4 - W_orig) for MSE loss, but we don't have W_orig
    # Proxy: the sign of surrounding weights (local consensus)

    # Actually, the simplest blind etch:
    # 1. Find positions where |W_q4| is near zero (bottom percentile)
    # 2. For those positions, flip to the sign of the LOCAL mean (row mean or neighbor mean)
    # This uses the STRUCTURE of the weight matrix to guess the correct sign

    q4_mag = np.abs(W_q4)
    q4_flat_mag = q4_mag.flatten()

    # Sort all positions by Q4 magnitude (ascending = most suspect first)
    suspect_order = np.argsort(q4_flat_mag)

    # For each suspect position, guess the correct sign from row context
    row_means = np.mean(W_q4, axis=1, keepdims=True)  # (d_model, 1)
    col_means = np.mean(W_q4, axis=0, keepdims=True)   # (1, d_model)
    context_sign = np.sign(row_means + col_means)  # additive row+col bias

    results_blind = []
    fix_counts = [0, 100, 500, 1000, 5000, 10000, 50000, 100000, 200000]

    for n_fix in fix_counts:
        if n_fix > len(suspect_order):
            continue
        sign_fixed = sign_q4.copy().flatten()
        if n_fix > 0:
            positions = suspect_order[:n_fix]
            # Flip to context-predicted sign
            ctx_flat = context_sign.flatten()
            for p in positions:
                if ctx_flat[p] != 0 and ctx_flat[p] != sign_fixed[p]:
                    sign_fixed[p] = ctx_flat[p]

        sign_fixed = sign_fixed.reshape(W_orig.shape)
        fid = rdm_correlation(rdm_orig, cosine_rdm(sign_fixed.astype(np.float32)))

        # How many of the positions we touched were actual flip errors?
        if n_fix > 0:
            touched = suspect_order[:n_fix]
            actual_flips = flip_mask.flatten()[touched]
            precision = float(actual_flips.mean())
        else:
            precision = 0.0

        results_blind.append({
            "n_fixed": n_fix,
            "fidelity": float(fid),
            "flip_precision": precision,
        })

        log(f"  Fix {n_fix:6d} suspect positions: fid={fid:.6f}, "
            f"precision={precision:.3f} (fraction that were actual errors)")

    return {"n_bits": n_bits, "baseline": fid_baseline,
            "blind_curve": results_blind}


# ══════════════════════════════════════════════════════════════════════
# TEST 3: Multi-bitwidth comparison
# ══════════════════════════════════════════════════════════════════════

def test_multi_bitwidth(W_orig):
    """How much does etching help at different quantization levels?"""
    log(f"\n{'='*60}")
    log(f"Multi-bitwidth etch potential")
    log(f"{'='*60}")

    sign_orig = np.sign(W_orig)
    rdm_orig = cosine_rdm(sign_orig.astype(np.float32))

    results = []
    for n_bits in [8, 4, 3, 2]:
        W_q = q4_simulate(W_orig, n_bits=n_bits)
        sign_q = np.sign(W_q)
        flip_mask = (sign_orig != sign_q)
        n_flips = int(flip_mask.sum())

        fid_before = rdm_correlation(rdm_orig, cosine_rdm(sign_q.astype(np.float32)))

        # Oracle etch (fix all)
        sign_fixed = sign_q.copy()
        sign_fixed[flip_mask] = sign_orig[flip_mask]
        fid_after = rdm_correlation(rdm_orig, cosine_rdm(sign_fixed.astype(np.float32)))

        # 20% etch (fix top 20% by residual magnitude)
        if n_flips > 0:
            residual = np.abs(W_orig - W_q)
            flip_positions = np.argwhere(flip_mask.flatten()).flatten()
            res_at_flips = residual.flatten()[flip_positions]
            top20 = flip_positions[np.argsort(-res_at_flips)[:int(0.2 * n_flips)]]
            sign_20 = sign_q.copy().flatten()
            sign_20[top20] = sign_orig.flatten()[top20]
            sign_20 = sign_20.reshape(W_orig.shape)
            fid_20 = rdm_correlation(rdm_orig, cosine_rdm(sign_20.astype(np.float32)))
        else:
            fid_20 = fid_before

        recovery = (fid_after - fid_before) / (1.0 - fid_before) * 100

        results.append({
            "n_bits": n_bits,
            "n_flips": n_flips,
            "flip_pct": n_flips / W_orig.size * 100,
            "fid_before": float(fid_before),
            "fid_after_oracle": float(fid_after),
            "fid_after_20pct": float(fid_20),
            "recovery_pct": float(recovery),
        })

        log(f"  {n_bits}-bit: {n_flips:,} flips ({n_flips/W_orig.size*100:.1f}%), "
            f"before={fid_before:.4f}, 20%_etch={fid_20:.4f}, "
            f"oracle={fid_after:.4f}, recovery={recovery:.1f}%")

    return results


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    W_orig = extract_W_q()

    results = {
        "progressive_4bit": test_progressive_etch(W_orig, n_bits=4),
        "progressive_3bit": test_progressive_etch(W_orig, n_bits=3),
        "blind_4bit": test_blind_etch(W_orig, n_bits=4),
        "multi_bitwidth": test_multi_bitwidth(W_orig),
    }

    elapsed = time.time() - t_start
    results["meta"] = {"model": MODEL_NAME, "layer": TARGET_LAYER,
                       "elapsed_seconds": elapsed}

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Q4 Etch Refinement")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s\n")

    log(f"  4-BIT PROGRESSIVE ETCH (fix % of known flips → crystal fidelity):")
    log(f"  {'Strategy':>12s}  {'0%':>8s}  {'5%':>8s}  {'20%':>8s}  {'50%':>8s}  {'100%':>8s}")
    log(f"  {'─'*12}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}")
    for sname in ["residual", "orig_mag", "q4_mag", "random"]:
        curve = results["progressive_4bit"]["curves"][sname]
        fids = {c["fix_frac"]: c["fidelity"] for c in curve}
        log(f"  {sname:>12s}  {fids.get(0.0,0):8.4f}  {fids.get(0.05,0):8.4f}  "
            f"{fids.get(0.20,0):8.4f}  {fids.get(0.50,0):8.4f}  {fids.get(1.0,0):8.4f}")

    log(f"\n  MULTI-BITWIDTH ETCH POTENTIAL:")
    for r in results["multi_bitwidth"]:
        log(f"    {r['n_bits']}-bit: {r['fid_before']:.4f} → {r['fid_after_20pct']:.4f} "
            f"(20% etch) → {r['fid_after_oracle']:.4f} (oracle) | "
            f"recovery={r['recovery_pct']:.1f}%")

    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
