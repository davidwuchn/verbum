"""Gradient Voting Q4 Refinement — Which signs carry the crystal?

Q4 quantization works. Our first experiment showed cross-layer sign
correlation = 0.000. Yet Q4 flips near-zero signs and the crystal
survives. This means: not all signs are equal. The crystal is carried
by HIGH-MAGNITUDE signs within each layer.

Tests:
1. MAGNITUDE MASKING — zero out the bottom X% of weights by magnitude,
   keep signs of the rest. Measure crystal fidelity. If crystal is in
   the loud weights, fidelity stays high even with aggressive masking.

2. SIGN FLIP NOISE — randomly flip X% of signs, measure crystal
   degradation. Then selectively flip only HIGH-magnitude signs vs
   only LOW-magnitude signs. Q4 prediction: flipping low-mag signs
   should be cheap, flipping high-mag signs should be expensive.

3. Q4 SIMULATION — actually simulate Q4 quantization (block-wise
   round-to-nearest with 4-bit precision), measure which signs flip
   and what happens to crystal fidelity.

4. EFFECTIVE CRYSTAL RANK — given that the crystal is carried by
   high-magnitude signs, what's the effective rank of ONLY the
   high-magnitude sign pattern? (Should be LOWER than the full 1209)

5. ACTIVATION-SPACE VALIDATION — run actual probes through the model,
   compute PCA-Q crystal, compare to weight-space measurements.
   This grounds the weight-space findings in the actual crystal metric.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/gradient_voting_q4_exp.py

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
TARGET_LAYER = 16

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "gradient-voting"


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def cosine_rdm(X: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    return (X / norms) @ (X / norms).T


def rdm_correlation(A: np.ndarray, B: np.ndarray) -> float:
    n = A.shape[0]
    idx = np.triu_indices(n, k=1)
    a = A[idx] - A[idx].mean()
    b = B[idx] - B[idx].mean()
    denom = np.sqrt(np.sum(a**2)) * np.sqrt(np.sum(b**2))
    return float(np.sum(a * b) / denom) if denom > 1e-10 else 0.0


def load_probes() -> list[dict]:
    probe_path = Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json"
    with open(probe_path) as f:
        data = json.load(f)
        return data if isinstance(data, list) else data["probes"]


def extract_layer_weights(layer_idx: int = TARGET_LAYER):
    """Extract W_q and W_up from one layer."""
    import torch
    from transformers import AutoModelForCausalLM

    log(f"  Loading {MODEL_NAME} (layer {layer_idx} only)...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float32, device_map="cpu",
    )
    model.eval()

    layer = model.gpt_neox.layers[layer_idx]
    qkv = layer.attention.query_key_value.weight.detach().float().numpy()
    W_q = qkv[:D_MODEL, :]
    W_up = layer.mlp.dense_h_to_4h.weight.detach().float().numpy()

    del model
    gc.collect()
    return W_q, W_up


def extract_all_layer_weights():
    """Extract W_q from ALL layers for multi-layer analysis."""
    import torch
    from transformers import AutoModelForCausalLM

    log(f"  Loading {MODEL_NAME} (all layers)...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float32, device_map="cpu",
    )
    model.eval()

    all_W_q = []
    for i in range(N_LAYERS):
        layer = model.gpt_neox.layers[i]
        qkv = layer.attention.query_key_value.weight.detach().float().numpy()
        W_q = qkv[:D_MODEL, :]
        all_W_q.append(W_q)

    del model
    gc.collect()
    return all_W_q


# ══════════════════════════════════════════════════════════════════════
# TEST 1: Magnitude masking — zero out low-mag weights, keep signs
# ══════════════════════════════════════════════════════════════════════

def test_magnitude_masking(W: np.ndarray, name: str) -> dict:
    """Zero out bottom X% of weights by magnitude. Measure sign-crystal fidelity."""
    log(f"\n{'='*60}")
    log(f"TEST 1: Magnitude masking — {name}")
    log(f"{'='*60}")

    sign_full = np.sign(W).astype(np.float32)
    rdm_full = cosine_rdm(sign_full)

    magnitudes = np.abs(W)
    results = []

    # Sweep: keep top X% by magnitude, zero the rest
    for keep_pct in [100, 95, 90, 80, 70, 60, 50, 40, 30, 20, 10, 5, 2, 1]:
        if keep_pct == 100:
            masked = sign_full.copy()
        else:
            threshold = np.percentile(magnitudes, 100 - keep_pct)
            mask = magnitudes >= threshold
            masked = sign_full * mask.astype(np.float32)

        rdm_masked = cosine_rdm(masked)
        fidelity = rdm_correlation(rdm_full, rdm_masked)

        # How many signs are we keeping?
        n_kept = int(np.sum(np.abs(masked) > 0))
        n_total = masked.size
        actual_pct = n_kept / n_total * 100

        results.append({
            "keep_pct": keep_pct,
            "actual_kept_pct": float(actual_pct),
            "n_kept": n_kept,
            "rdm_fidelity": float(fidelity),
            "threshold_magnitude": float(threshold) if keep_pct < 100 else 0.0,
        })

        log(f"  Keep top {keep_pct:3d}% (mag≥{threshold if keep_pct < 100 else 0:.4f}): "
            f"fidelity={fidelity:.4f}, kept={n_kept:,}/{n_total:,}")

    return {"name": name, "masking_sweep": results}


# ══════════════════════════════════════════════════════════════════════
# TEST 2: Selective sign flipping — high-mag vs low-mag
# ══════════════════════════════════════════════════════════════════════

def test_sign_flip_noise(W: np.ndarray, name: str) -> dict:
    """Flip signs selectively. Compare cost of flipping high vs low magnitude."""
    log(f"\n{'='*60}")
    log(f"TEST 2: Selective sign flipping — {name}")
    log(f"{'='*60}")

    sign_full = np.sign(W).astype(np.float32)
    rdm_full = cosine_rdm(sign_full)
    magnitudes = np.abs(W)
    rng = np.random.RandomState(42)

    results = {"random_flips": [], "low_mag_flips": [], "high_mag_flips": []}

    flip_pcts = [1, 2, 5, 10, 20, 30, 50]

    for flip_pct in flip_pcts:
        n_flip = int(W.size * flip_pct / 100)

        # Random flips
        idx_rand = rng.choice(W.size, n_flip, replace=False)
        signs_rand = sign_full.copy().flatten()
        signs_rand[idx_rand] *= -1
        signs_rand = signs_rand.reshape(W.shape)
        fid_rand = rdm_correlation(rdm_full, cosine_rdm(signs_rand))

        # Low-magnitude flips (sorted by magnitude ascending, flip the smallest)
        sorted_idx = np.argsort(magnitudes.flatten())
        idx_low = sorted_idx[:n_flip]
        signs_low = sign_full.copy().flatten()
        signs_low[idx_low] *= -1
        signs_low = signs_low.reshape(W.shape)
        fid_low = rdm_correlation(rdm_full, cosine_rdm(signs_low))

        # High-magnitude flips (sorted descending, flip the largest)
        idx_high = sorted_idx[-n_flip:]
        signs_high = sign_full.copy().flatten()
        signs_high[idx_high] *= -1
        signs_high = signs_high.reshape(W.shape)
        fid_high = rdm_correlation(rdm_full, cosine_rdm(signs_high))

        results["random_flips"].append({"flip_pct": flip_pct, "rdm_fidelity": float(fid_rand)})
        results["low_mag_flips"].append({"flip_pct": flip_pct, "rdm_fidelity": float(fid_low)})
        results["high_mag_flips"].append({"flip_pct": flip_pct, "rdm_fidelity": float(fid_high)})

        log(f"  Flip {flip_pct:2d}%: random={fid_rand:.4f}, low_mag={fid_low:.4f}, high_mag={fid_high:.4f}")

    return {"name": name, "flip_analysis": results}


# ══════════════════════════════════════════════════════════════════════
# TEST 3: Q4 simulation
# ══════════════════════════════════════════════════════════════════════

def test_q4_simulation(W: np.ndarray, name: str) -> dict:
    """Simulate block-wise 4-bit quantization. Measure sign preservation and crystal fidelity."""
    log(f"\n{'='*60}")
    log(f"TEST 3: Q4 simulation — {name}")
    log(f"{'='*60}")

    sign_full = np.sign(W).astype(np.float32)
    rdm_full_sign = cosine_rdm(sign_full)
    rdm_full_W = cosine_rdm(W.astype(np.float32))

    results = {}

    for n_bits in [8, 4, 3, 2, 1]:
        if n_bits == 1:
            # 1-bit = sign only
            W_q = np.sign(W).astype(np.float32)
        else:
            # Block-wise symmetric quantization
            # Block size 32 (typical for Q4_K)
            block_size = 32
            W_flat = W.flatten()
            n = len(W_flat)
            # Pad to block boundary
            pad = (block_size - n % block_size) % block_size
            W_padded = np.concatenate([W_flat, np.zeros(pad)])
            W_blocks = W_padded.reshape(-1, block_size)

            # Per-block: find scale, quantize, dequantize
            n_levels = 2 ** (n_bits - 1)  # symmetric: -n_levels to +n_levels
            scales = np.max(np.abs(W_blocks), axis=1, keepdims=True)
            scales = np.maximum(scales, 1e-10)
            # Quantize
            W_normalized = W_blocks / scales
            W_quantized = np.round(W_normalized * n_levels).clip(-n_levels, n_levels)
            # Dequantize
            W_dequant = (W_quantized / n_levels) * scales
            W_q = W_dequant.flatten()[:n].reshape(W.shape).astype(np.float32)

        # Measure sign preservation
        sign_q = np.sign(W_q)
        sign_agree = float(np.mean(sign_full == sign_q))
        sign_flip_count = int(np.sum(sign_full != sign_q))
        sign_flip_pct = float(sign_flip_count / sign_full.size * 100)

        # Where do flips happen? By magnitude
        flip_mask = (sign_full != sign_q)
        if flip_mask.any():
            flipped_magnitudes = np.abs(W.flatten())[flip_mask.flatten()]
            all_magnitudes = np.abs(W.flatten())
            flip_mag_mean = float(flipped_magnitudes.mean())
            all_mag_mean = float(all_magnitudes.mean())
            flip_mag_ratio = flip_mag_mean / all_mag_mean
            # What percentile are the flipped weights?
            flip_percentiles = np.searchsorted(
                np.sort(all_magnitudes), flipped_magnitudes
            ) / len(all_magnitudes) * 100
            flip_pctile_mean = float(flip_percentiles.mean())
        else:
            flip_mag_ratio = 0.0
            flip_pctile_mean = 0.0

        # Crystal fidelity (vs full sign(W))
        rdm_q_sign = cosine_rdm(np.sign(W_q).astype(np.float32))
        fid_sign = rdm_correlation(rdm_full_sign, rdm_q_sign)

        # Crystal fidelity (vs full W, continuous space)
        rdm_q_W = cosine_rdm(W_q)
        fid_W = rdm_correlation(rdm_full_W, rdm_q_W)

        results[f"{n_bits}bit"] = {
            "n_bits": n_bits,
            "sign_agreement": sign_agree,
            "sign_flips": sign_flip_count,
            "sign_flip_pct": sign_flip_pct,
            "flipped_magnitude_ratio": flip_mag_ratio,
            "flipped_mean_percentile": flip_pctile_mean,
            "rdm_fidelity_vs_sign": float(fid_sign),
            "rdm_fidelity_vs_continuous": float(fid_W),
        }

        log(f"  {n_bits}-bit: sign_agree={sign_agree:.4f}, "
            f"flips={sign_flip_pct:.1f}% (mean pctile={flip_pctile_mean:.0f}), "
            f"crystal_fid={fid_sign:.4f}, cont_fid={fid_W:.4f}")

    return {"name": name, "quantization": results}


# ══════════════════════════════════════════════════════════════════════
# TEST 4: Effective crystal rank at high magnitude only
# ══════════════════════════════════════════════════════════════════════

def test_effective_crystal_rank(W: np.ndarray, name: str) -> dict:
    """SVD of sign(W) masked to only high-magnitude positions.
    Is the crystal lower-rank when we only look at the loud signs?"""
    log(f"\n{'='*60}")
    log(f"TEST 4: Crystal rank at different magnitude thresholds — {name}")
    log(f"{'='*60}")

    magnitudes = np.abs(W)
    results = []

    for keep_pct in [100, 80, 50, 20, 10, 5]:
        if keep_pct == 100:
            S_masked = np.sign(W).astype(np.float32)
        else:
            threshold = np.percentile(magnitudes, 100 - keep_pct)
            mask = (magnitudes >= threshold).astype(np.float32)
            S_masked = np.sign(W).astype(np.float32) * mask

        _, svals, _ = np.linalg.svd(S_masked, full_matrices=False)
        total_var = np.sum(svals ** 2)
        cumvar = np.cumsum(svals ** 2) / total_var

        ranks = {}
        for threshold_pct in [0.50, 0.80, 0.90, 0.95]:
            rank = int(np.searchsorted(cumvar, threshold_pct)) + 1
            ranks[f"{int(threshold_pct*100)}pct"] = rank

        top10_frac = float(np.sum(svals[:10]**2) / total_var)
        top50_frac = float(np.sum(svals[:50]**2) / total_var)

        results.append({
            "keep_pct": keep_pct,
            "effective_ranks": ranks,
            "top10_variance_fraction": top10_frac,
            "top50_variance_fraction": top50_frac,
        })

        log(f"  Top {keep_pct:3d}% by mag: rank(90%)={ranks['90pct']:4d}, "
            f"rank(50%)={ranks['50pct']:3d}, top10={top10_frac:.3f}")

    return {"name": name, "rank_by_magnitude": results}


# ══════════════════════════════════════════════════════════════════════
# TEST 5: Multi-layer magnitude masking
# ══════════════════════════════════════════════════════════════════════

def test_multilayer_masking(all_W_q: list[np.ndarray]) -> dict:
    """Test magnitude masking across ALL layers — is the pattern universal?"""
    log(f"\n{'='*60}")
    log(f"TEST 5: Multi-layer magnitude masking — W_q all 32 layers")
    log(f"{'='*60}")

    results_by_depth = []

    for layer_idx in range(0, N_LAYERS, 4):  # sample every 4th layer
        W = all_W_q[layer_idx]
        sign_full = np.sign(W).astype(np.float32)
        rdm_full = cosine_rdm(sign_full)
        magnitudes = np.abs(W)

        layer_results = {"layer": layer_idx, "depth_frac": layer_idx / (N_LAYERS - 1)}
        fidelities = {}

        for keep_pct in [100, 50, 20, 10, 5]:
            if keep_pct == 100:
                masked = sign_full.copy()
            else:
                threshold = np.percentile(magnitudes, 100 - keep_pct)
                mask = magnitudes >= threshold
                masked = sign_full * mask.astype(np.float32)

            fidelity = rdm_correlation(rdm_full, cosine_rdm(masked))
            fidelities[f"keep_{keep_pct}pct"] = float(fidelity)

        layer_results["fidelities"] = fidelities
        results_by_depth.append(layer_results)

        log(f"  Layer {layer_idx:2d} (d={layer_idx/(N_LAYERS-1):.2f}): "
            f"top50={fidelities['keep_50pct']:.4f}, "
            f"top20={fidelities['keep_20pct']:.4f}, "
            f"top10={fidelities['keep_10pct']:.4f}, "
            f"top5={fidelities['keep_5pct']:.4f}")

    return {"per_layer": results_by_depth}


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    results = {}

    # Load all layers for multi-layer tests
    all_W_q = extract_all_layer_weights()
    W_q = all_W_q[TARGET_LAYER]
    W_up_list = None  # only load if needed

    # Test 1: Magnitude masking
    results["magnitude_masking_W_q"] = test_magnitude_masking(W_q, "W_q L16")

    # Test 2: Selective sign flipping
    results["sign_flip_W_q"] = test_sign_flip_noise(W_q, "W_q L16")

    # Test 3: Q4 simulation
    results["q4_simulation_W_q"] = test_q4_simulation(W_q, "W_q L16")

    # Test 4: Effective crystal rank
    results["crystal_rank_W_q"] = test_effective_crystal_rank(W_q, "W_q L16")

    # Test 5: Multi-layer masking
    results["multilayer_masking"] = test_multilayer_masking(all_W_q)

    # ── Save ──
    elapsed = time.time() - t_start
    results["meta"] = {
        "model": MODEL_NAME,
        "target_layer": TARGET_LAYER,
        "elapsed_seconds": elapsed,
    }

    out_path = RESULTS_DIR / "q4_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    # ── Summary ──
    log(f"\n{'═'*60}")
    log(f"SUMMARY — Q4 Refinement")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s\n")

    log(f"  MAGNITUDE MASKING (W_q L16):")
    for r in results["magnitude_masking_W_q"]["masking_sweep"]:
        if r["keep_pct"] in [100, 50, 20, 10, 5]:
            log(f"    Keep top {r['keep_pct']:3d}%: fidelity={r['rdm_fidelity']:.4f}")

    log(f"\n  SIGN FLIPPING (W_q L16, 10% flips):")
    for mode in ["random_flips", "low_mag_flips", "high_mag_flips"]:
        for r in results["sign_flip_W_q"]["flip_analysis"][mode]:
            if r["flip_pct"] == 10:
                log(f"    {mode:15s}: fidelity={r['rdm_fidelity']:.4f}")

    log(f"\n  Q4 SIMULATION (W_q L16):")
    for bits in ["8bit", "4bit", "3bit", "2bit", "1bit"]:
        q = results["q4_simulation_W_q"]["quantization"][bits]
        log(f"    {bits}: sign_agree={q['sign_agreement']:.4f}, "
            f"flips={q['sign_flip_pct']:.1f}% @ pctile {q['flipped_mean_percentile']:.0f}, "
            f"crystal={q['rdm_fidelity_vs_sign']:.4f}")

    log(f"\n  CRYSTAL RANK by magnitude (W_q L16):")
    for r in results["crystal_rank_W_q"]["rank_by_magnitude"]:
        log(f"    Top {r['keep_pct']:3d}%: rank(90%)={r['effective_ranks']['90pct']}")

    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
