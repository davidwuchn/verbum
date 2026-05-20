"""Crystal Lens Experiment — Magnitude decomposition in crystal coordinates.

Key question: how much of the weight matrix's "energy" (Frobenius norm²)
is aligned with the crystal basis vs orthogonal to it?

If most energy is crystal-aligned, we can build a magnitude lens:
  - Crystal directions get fixed magnitude from teacher
  - GD only learns the residual (non-crystal) component
  - This IS the reduction: the crystal directions ARE the beta reductions

Protocol:
  1. Load Pythia-2.8b
  2. Run probes, extract Q activations at each depth
  3. PCA the Q activations → crystal basis (top-k directions)
  4. For each layer: project W_q onto crystal basis
     - Crystal-aligned energy = ||W_q projected onto PCA-Q basis||²
     - Orthogonal energy = ||W_q - projection||²
  5. Build magnitude lens: crystal-basis magnitudes from teacher
  6. Test: sign(W) × crystal_lens vs sign(W) × uniform

Also test: what happens if we use crystal-aligned SVD for compression
instead of raw SVD? The first experiment showed k=512 → 0.741 fidelity
with raw SVD. Crystal-aligned compression might be much better.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/crystal_lens_exp.py

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
PCA_DIM = 64

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "crystal-lens"


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


# ══════════════════════════════════════════════════════════════════════
# Extract Q activations AND weight matrices simultaneously
# ══════════════════════════════════════════════════════════════════════

def extract_all(probes: list[dict], depth_fractions: list[float]):
    """Load model once, extract W_q at all layers AND Q activations at target depths."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    log(f"\n  Loading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float32, device_map="mps",
    )
    model.eval()

    # Extract weight matrices (all layers)
    all_W_q = []
    for i in range(N_LAYERS):
        qkv = model.gpt_neox.layers[i].attention.query_key_value.weight.detach().cpu().float().numpy()
        all_W_q.append(qkv[:D_MODEL, :])  # (2560, 2560)
    log(f"  Extracted W_q from {N_LAYERS} layers")

    # Set up hooks for Q activations at target layers
    target_layers = {}
    for frac in depth_fractions:
        layer_idx = min(int(round(frac * (N_LAYERS - 1))), N_LAYERS - 1)
        target_layers[frac] = layer_idx

    captures = {idx: [] for idx in set(target_layers.values())}
    hooks = []

    for layer_idx in set(target_layers.values()):
        fused = model.gpt_neox.layers[layer_idx].attention.query_key_value

        def make_hook(li):
            def hook_fn(module, input, output):
                captures[li].append(output[:, -1, :D_MODEL].detach().cpu().float())
            return hook_fn
        hooks.append(fused.register_forward_hook(make_hook(layer_idx)))

    # Run probes
    log(f"  Running {len(probes)} probes for Q activations...")
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to("mps")
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 50 == 0:
            log(f"    {i+1}/{len(probes)}...")
    log(f"  Done in {time.time() - t0:.1f}s")

    for h in hooks:
        h.remove()

    # Stack activations
    Q_activations = {}
    for frac, layer_idx in target_layers.items():
        Q_vecs = torch.cat(captures[layer_idx], dim=0).numpy()  # (n_probes, d_model)
        Q_activations[frac] = Q_vecs

    del model, tokenizer
    gc.collect()
    torch.mps.empty_cache()

    return all_W_q, Q_activations


# ══════════════════════════════════════════════════════════════════════
# PCA basis extraction
# ══════════════════════════════════════════════════════════════════════

def extract_pca_basis(Q_vecs: np.ndarray, n_components: int = PCA_DIM):
    """PCA of Q activations → crystal basis directions in d_model space.

    Returns:
      basis: (n_components, d_model) — orthonormal basis vectors
      explained: fraction of variance explained by each component
      mean: (d_model,) — mean Q vector
    """
    mean = Q_vecs.mean(axis=0)
    centered = Q_vecs - mean
    # SVD: centered = U @ diag(S) @ Vt
    # Vt rows are the principal directions in d_model space
    _, S, Vt = np.linalg.svd(centered, full_matrices=False)
    total_var = np.sum(S ** 2)
    explained = S[:n_components] ** 2 / total_var

    return Vt[:n_components], explained, mean


# ══════════════════════════════════════════════════════════════════════
# TEST 1: Energy decomposition — crystal vs orthogonal
# ══════════════════════════════════════════════════════════════════════

def test_energy_decomposition(all_W_q, Q_activations, depth_fractions):
    """For each layer: what fraction of ||W_q||² is crystal-aligned?"""
    log(f"\n{'='*60}")
    log(f"TEST 1: Energy decomposition — crystal vs orthogonal")
    log(f"{'='*60}")

    results = []

    for frac in depth_fractions:
        layer_idx = min(int(round(frac * (N_LAYERS - 1))), N_LAYERS - 1)
        W_q = all_W_q[layer_idx]

        # Get PCA basis at this depth
        basis, explained, mean = extract_pca_basis(Q_activations[frac])

        total_energy = float(np.sum(W_q ** 2))

        # Project W_q rows onto crystal basis
        # W_q: (d_model, d_model), basis: (k, d_model)
        # Projection: W_projected = W_q @ basis.T @ basis
        coeffs = W_q @ basis.T  # (d_model, k) — each row's crystal coordinates
        crystal_energy = float(np.sum(coeffs ** 2))
        ortho_energy = total_energy - crystal_energy
        crystal_fraction = crystal_energy / total_energy

        # How much variance do the PCA components explain?
        total_pca_explained = float(np.sum(explained))

        # Magnitude profile in crystal coordinates
        # For each of the k crystal directions, what's the total magnitude?
        per_direction_energy = np.sum(coeffs ** 2, axis=0)  # (k,)
        per_direction_frac = per_direction_energy / total_energy

        # Sign crystal fidelity: project, sign, compare
        W_crystal = coeffs @ basis  # (d_model, d_model) — crystal component
        W_ortho = W_q - W_crystal
        sign_full = np.sign(W_q).astype(np.float32)
        rdm_full = cosine_rdm(sign_full)

        sign_crystal = np.sign(W_crystal).astype(np.float32)
        sign_ortho = np.sign(W_ortho).astype(np.float32)

        fid_crystal = rdm_correlation(rdm_full, cosine_rdm(sign_crystal))
        fid_ortho = rdm_correlation(rdm_full, cosine_rdm(sign_ortho))

        # Continuous fidelity
        rdm_full_cont = cosine_rdm(W_q.astype(np.float32))
        fid_crystal_cont = rdm_correlation(rdm_full_cont, cosine_rdm(W_crystal.astype(np.float32)))

        results.append({
            "depth_frac": frac,
            "layer_idx": layer_idx,
            "total_energy": total_energy,
            "crystal_energy_fraction": crystal_fraction,
            "orthogonal_energy_fraction": 1.0 - crystal_fraction,
            "pca_variance_explained": total_pca_explained,
            "top5_direction_energy": float(np.sum(per_direction_frac[:5])),
            "top10_direction_energy": float(np.sum(per_direction_frac[:10])),
            "sign_fidelity_crystal_only": float(fid_crystal),
            "sign_fidelity_ortho_only": float(fid_ortho),
            "continuous_fidelity_crystal": float(fid_crystal_cont),
        })

        log(f"  L{layer_idx:2d} (d={frac:.1f}): crystal={crystal_fraction:.4f}, "
            f"sign_fid_crystal={fid_crystal:.4f}, sign_fid_ortho={fid_ortho:.4f}, "
            f"cont_fid={fid_crystal_cont:.4f}")

    return results


# ══════════════════════════════════════════════════════════════════════
# TEST 2: Crystal-aligned compression vs raw SVD compression
# ══════════════════════════════════════════════════════════════════════

def test_crystal_compression(W_q, Q_activations, frac):
    """Compare: crystal-aligned projection vs raw SVD at same k."""
    log(f"\n{'='*60}")
    log(f"TEST 2: Crystal-aligned vs raw SVD compression")
    log(f"{'='*60}")

    sign_full = np.sign(W_q).astype(np.float32)
    rdm_full = cosine_rdm(sign_full)
    rdm_full_cont = cosine_rdm(W_q.astype(np.float32))

    # Crystal basis
    basis, _, _ = extract_pca_basis(Q_activations[frac])

    # Raw SVD of W_q
    U_raw, S_raw, Vt_raw = np.linalg.svd(W_q, full_matrices=False)

    k_values = [64, 128, 256, 384, 512, 768, 1024, 1536]
    results = []

    for k in k_values:
        # Crystal-aligned: project onto top-k PCA-Q directions
        k_eff = min(k, PCA_DIM)  # crystal basis is only PCA_DIM wide
        basis_k = basis[:k_eff]
        coeffs = W_q @ basis_k.T
        W_crystal_k = coeffs @ basis_k
        sign_crystal_k = np.sign(W_crystal_k).astype(np.float32)
        fid_crystal_sign = rdm_correlation(rdm_full, cosine_rdm(sign_crystal_k))
        fid_crystal_cont = rdm_correlation(rdm_full_cont, cosine_rdm(W_crystal_k.astype(np.float32)))

        # Raw SVD: keep top-k singular vectors
        k_svd = min(k, len(S_raw))
        W_svd_k = (U_raw[:, :k_svd] * S_raw[:k_svd]) @ Vt_raw[:k_svd, :]
        sign_svd_k = np.sign(W_svd_k).astype(np.float32)
        fid_svd_sign = rdm_correlation(rdm_full, cosine_rdm(sign_svd_k))
        fid_svd_cont = rdm_correlation(rdm_full_cont, cosine_rdm(W_svd_k.astype(np.float32)))

        # Hybrid: crystal basis + top-k SVD of residual
        if k > k_eff:
            W_residual = W_q - W_crystal_k
            U_res, S_res, Vt_res = np.linalg.svd(W_residual, full_matrices=False)
            k_res = min(k - k_eff, len(S_res))
            W_hybrid = W_crystal_k + (U_res[:, :k_res] * S_res[:k_res]) @ Vt_res[:k_res, :]
        else:
            W_hybrid = W_crystal_k

        sign_hybrid = np.sign(W_hybrid).astype(np.float32)
        fid_hybrid_sign = rdm_correlation(rdm_full, cosine_rdm(sign_hybrid))
        fid_hybrid_cont = rdm_correlation(rdm_full_cont, cosine_rdm(W_hybrid.astype(np.float32)))

        results.append({
            "k": k,
            "crystal_sign_fidelity": float(fid_crystal_sign),
            "crystal_cont_fidelity": float(fid_crystal_cont),
            "svd_sign_fidelity": float(fid_svd_sign),
            "svd_cont_fidelity": float(fid_svd_cont),
            "hybrid_sign_fidelity": float(fid_hybrid_sign),
            "hybrid_cont_fidelity": float(fid_hybrid_cont),
        })

        log(f"  k={k:4d}: crystal_sign={fid_crystal_sign:.4f} "
            f"svd_sign={fid_svd_sign:.4f} hybrid_sign={fid_hybrid_sign:.4f} | "
            f"crystal_cont={fid_crystal_cont:.4f} svd_cont={fid_svd_cont:.4f} "
            f"hybrid_cont={fid_hybrid_cont:.4f}")

    return results


# ══════════════════════════════════════════════════════════════════════
# TEST 3: The lens — crystal magnitudes as fixed template
# ══════════════════════════════════════════════════════════════════════

def test_crystal_lens(W_q, Q_activations, frac):
    """Build a magnitude template from crystal projections. Test as a lens.

    Compare:
      A. sign(W_q) alone (uniform magnitude) — baseline
      B. sign(W_q) × |W_q| (true magnitudes) — best case
      C. sign(W_q) × crystal_lens (fixed template from PCA directions)
      D. sign(W_q) × row_norm_lens (per-row magnitude normalization)
    """
    log(f"\n{'='*60}")
    log(f"TEST 3: Crystal magnitude lens")
    log(f"{'='*60}")

    # Ground truth: the CONTINUOUS cosine RDM (what the model actually uses)
    rdm_continuous = cosine_rdm(W_q.astype(np.float32))

    # Also compare against sign-only RDM
    sign_full = np.sign(W_q).astype(np.float32)
    rdm_sign = cosine_rdm(sign_full)

    # A. Sign only (uniform magnitude)
    fid_sign_vs_cont = rdm_correlation(rdm_continuous, rdm_sign)

    # B. True magnitudes (identity — should be perfect)
    fid_true = rdm_correlation(rdm_continuous, rdm_continuous)

    # C. Crystal lens
    basis, explained, mean = extract_pca_basis(Q_activations[frac])
    coeffs = W_q @ basis.T  # (d_model, k) — crystal coordinates

    # The lens: for each row of W_q, compute its magnitude in each crystal direction
    # Then reconstruct: sign(W) scaled by crystal magnitudes
    # Per-direction magnitude profile (averaged across all rows)
    dir_magnitudes = np.sqrt(np.mean(coeffs ** 2, axis=0))  # (k,) — RMS per direction

    # Crystal lens: project sign(W_q) onto crystal basis, scale by dir_magnitudes
    sign_coeffs = sign_full @ basis.T  # (d_model, k) — signs in crystal space
    lens_coeffs = sign_coeffs * dir_magnitudes[None, :]  # scale by per-direction magnitude
    W_lens = lens_coeffs @ basis  # back to d_model space
    fid_lens_vs_cont = rdm_correlation(rdm_continuous, cosine_rdm(W_lens.astype(np.float32)))

    # D. Row-norm lens: scale each row by its original L2 norm
    row_norms = np.linalg.norm(W_q, axis=1, keepdims=True)  # (d_model, 1)
    W_rownorm = sign_full * row_norms
    fid_rownorm_vs_cont = rdm_correlation(rdm_continuous, cosine_rdm(W_rownorm.astype(np.float32)))

    # E. Crystal projection with TRUE magnitudes (not averaged)
    W_crystal_true = coeffs @ basis  # crystal component with true per-row magnitudes
    fid_crystal_true = rdm_correlation(rdm_continuous, cosine_rdm(W_crystal_true.astype(np.float32)))

    # F. Per-row crystal lens (each row gets its own magnitude profile)
    row_dir_magnitudes = np.abs(coeffs)  # (d_model, k) — per-row per-direction
    lens_per_row = (np.sign(coeffs) * row_dir_magnitudes) @ basis  # use sign from coeffs, not sign(W_q)
    # Actually this is just = coeffs @ basis = W_crystal_true. Let me think...
    # The lens idea: use sign(W_q) for the sign pattern, but crystal magnitudes for scaling
    # Per-row: project the sign into crystal space, scale by THIS ROW's crystal magnitudes
    sign_in_crystal = sign_full @ basis.T  # (d_model, k)
    # Scale by actual crystal magnitudes from THIS layer's W_q
    scaled = sign_in_crystal * np.abs(coeffs)  # sign from sign(W) × magnitude from crystal projection
    W_lens_perrow = scaled @ basis
    fid_lens_perrow = rdm_correlation(rdm_continuous, cosine_rdm(W_lens_perrow.astype(np.float32)))

    results = {
        "A_sign_only": float(fid_sign_vs_cont),
        "B_true_magnitudes": float(fid_true),
        "C_crystal_lens_avg": float(fid_lens_vs_cont),
        "D_row_norm_lens": float(fid_rownorm_vs_cont),
        "E_crystal_true_mag": float(fid_crystal_true),
        "F_crystal_lens_perrow": float(fid_lens_perrow),
        "pca_variance_explained": float(np.sum(explained)),
        "direction_magnitude_profile": dir_magnitudes.tolist(),
    }

    log(f"  A. sign(W) only:          {fid_sign_vs_cont:.4f} (baseline)")
    log(f"  B. true magnitudes:        {fid_true:.4f} (upper bound)")
    log(f"  C. crystal lens (avg mag): {fid_lens_vs_cont:.4f}")
    log(f"  D. row-norm lens:          {fid_rownorm_vs_cont:.4f}")
    log(f"  E. crystal (true mag):     {fid_crystal_true:.4f}")
    log(f"  F. crystal lens (per-row): {fid_lens_perrow:.4f}")

    return results


# ══════════════════════════════════════════════════════════════════════
# TEST 4: Cross-layer crystal alignment
# ══════════════════════════════════════════════════════════════════════

def test_cross_layer_crystal(all_W_q, Q_activations, depth_fractions):
    """Use one depth's crystal basis to decompose ALL layers.
    Does the crystal basis from depth 0.5 work for depth 0.1? 0.9?
    """
    log(f"\n{'='*60}")
    log(f"TEST 4: Cross-layer crystal alignment")
    log(f"{'='*60}")

    results = {}

    for ref_frac in [0.2, 0.5, 0.8]:
        ref_basis, _, _ = extract_pca_basis(Q_activations[ref_frac])

        layer_results = []
        for layer_idx in range(0, N_LAYERS, 2):  # every other layer
            W_q = all_W_q[layer_idx]
            total_energy = np.sum(W_q ** 2)
            coeffs = W_q @ ref_basis.T
            crystal_fraction = np.sum(coeffs ** 2) / total_energy

            layer_results.append({
                "layer": layer_idx,
                "depth_frac": layer_idx / (N_LAYERS - 1),
                "crystal_fraction": float(crystal_fraction),
            })

        results[f"ref_{ref_frac}"] = layer_results
        fracs = [r["crystal_fraction"] for r in layer_results]
        log(f"  Ref depth={ref_frac}: crystal fraction range "
            f"[{min(fracs):.4f}, {max(fracs):.4f}], mean={np.mean(fracs):.4f}")

    return results


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    probes = load_probes()
    depth_fractions = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    all_W_q, Q_activations = extract_all(probes, depth_fractions)

    results = {}

    # Test 1: Energy decomposition
    results["energy_decomposition"] = test_energy_decomposition(
        all_W_q, Q_activations, depth_fractions
    )

    # Test 2: Crystal vs SVD compression (at depth 0.5)
    target_layer = min(int(round(0.5 * (N_LAYERS - 1))), N_LAYERS - 1)
    results["compression_comparison"] = test_crystal_compression(
        all_W_q[target_layer], Q_activations, 0.5
    )

    # Test 3: Crystal lens
    results["crystal_lens"] = test_crystal_lens(
        all_W_q[target_layer], Q_activations, 0.5
    )

    # Test 4: Cross-layer alignment
    results["cross_layer_crystal"] = test_cross_layer_crystal(
        all_W_q, Q_activations, depth_fractions
    )

    elapsed = time.time() - t_start
    results["meta"] = {
        "model": MODEL_NAME,
        "pca_dim": PCA_DIM,
        "n_probes": len(probes),
        "elapsed_seconds": elapsed,
    }

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    # ── Summary ──
    log(f"\n{'═'*60}")
    log(f"SUMMARY — Crystal Lens")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s\n")

    log(f"  ENERGY DECOMPOSITION (PCA-Q k={PCA_DIM}):")
    for r in results["energy_decomposition"]:
        log(f"    d={r['depth_frac']:.1f} L{r['layer_idx']:2d}: "
            f"crystal={r['crystal_energy_fraction']:.4f}, "
            f"sign_fid={r['sign_fidelity_crystal_only']:.4f}, "
            f"cont_fid={r['continuous_fidelity_crystal']:.4f}")

    log(f"\n  CRYSTAL LENS (d=0.5):")
    lens = results["crystal_lens"]
    log(f"    sign only:     {lens['A_sign_only']:.4f}")
    log(f"    crystal lens:  {lens['C_crystal_lens_avg']:.4f}")
    log(f"    crystal true:  {lens['E_crystal_true_mag']:.4f}")
    log(f"    row-norm:      {lens['D_row_norm_lens']:.4f}")
    log(f"    true mag:      {lens['B_true_magnitudes']:.4f}")

    log(f"\n  COMPRESSION (k=512, d=0.5):")
    for r in results["compression_comparison"]:
        if r["k"] == 512:
            log(f"    Crystal-aligned: sign={r['crystal_sign_fidelity']:.4f}, "
                f"cont={r['crystal_cont_fidelity']:.4f}")
            log(f"    Raw SVD:         sign={r['svd_sign_fidelity']:.4f}, "
                f"cont={r['svd_cont_fidelity']:.4f}")
            log(f"    Hybrid:          sign={r['hybrid_sign_fidelity']:.4f}, "
                f"cont={r['hybrid_cont_fidelity']:.4f}")

    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
