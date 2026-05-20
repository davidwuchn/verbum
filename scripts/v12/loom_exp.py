"""Loom Experiment — Is the weight matrix a 2-beam weave?

Hypothesis: W_q is a fabric woven from two beams (Q crystal + FFN crystal)
crossing at ~67°. The SVD of W_q should decompose into:
  - Warp: input directions (Vt rows — what the weight reads)
  - Weft: output directions (U columns — what the weight produces)
  - Tension: singular values (S — how much each crossing matters)

If it's a loom, the SVD directions should align with the crystal bases,
and the two weight matrices (W_q, W_up) should share input structure
(same warp) but differ in output structure (different weft).

Measurements:
1. SVD-CRYSTAL ALIGNMENT — do W_q's output directions match PCA-Q?
   Do W_up's output directions match PCA-up?

2. SHARED WARP — do W_q and W_up read from the same input directions?
   Principal angles between their Vt (input) spaces.

3. LOOM ANGLE — principal angles between U_q and U_up output spaces.
   Should be ~67° if it's the same angle we measured holographically.

4. WEAVE DECOMPOSITION — project W_q into (Q-crystal × FFN-crystal)
   joint basis. How much energy in warp×weft vs residual?

5. TENSION PROFILE — do the singular values (the magnitudes!) concentrate
   in crystal-aligned directions? This connects magnitudes to the loom.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/loom_exp.py

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
PCA_DIM = 64

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "loom"


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def principal_angles_deg(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Principal angles between column spaces of A and B."""
    Qa, _ = np.linalg.qr(A)
    Qb, _ = np.linalg.qr(B)
    svals = np.linalg.svd(Qa.T @ Qb, compute_uv=False)
    svals = np.clip(svals, 0, 1)
    return np.degrees(np.arccos(svals))


def subspace_overlap(A: np.ndarray, B: np.ndarray) -> float:
    """Mean cos² between subspaces = fraction of A captured by B."""
    Qa, _ = np.linalg.qr(A)
    Qb, _ = np.linalg.qr(B)
    svals = np.linalg.svd(Qa.T @ Qb, compute_uv=False)
    return float(np.mean(svals ** 2))


def load_probes():
    probe_path = Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json"
    with open(probe_path) as f:
        data = json.load(f)
        return data if isinstance(data, list) else data["probes"]


# ══════════════════════════════════════════════════════════════════════
# Extract everything in one model load
# ══════════════════════════════════════════════════════════════════════

def extract_all(probes, depths):
    """Load model, extract W_q + W_up at all layers, Q + up_proj activations at target depths."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    log(f"  Loading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float32, device_map="mps",
    )
    model.eval()

    # ── Extract weights ──
    all_W_q, all_W_up = [], []
    for i in range(N_LAYERS):
        layer = model.gpt_neox.layers[i]
        qkv = layer.attention.query_key_value.weight.detach().cpu().float().numpy()
        all_W_q.append(qkv[:D_MODEL, :])
        all_W_up.append(layer.mlp.dense_h_to_4h.weight.detach().cpu().float().numpy())
    log(f"  Extracted weights from {N_LAYERS} layers")

    # ── Extract activations at target depths ──
    target_layers = {}
    for frac in depths:
        target_layers[frac] = min(int(round(frac * (N_LAYERS - 1))), N_LAYERS - 1)

    captures = {idx: {"Q": [], "up": []} for idx in set(target_layers.values())}
    hooks = []

    for layer_idx in set(target_layers.values()):
        # Q hook (fused QKV, first d_model outputs)
        fused = model.gpt_neox.layers[layer_idx].attention.query_key_value
        def make_q_hook(li):
            def hook_fn(module, input, output):
                captures[li]["Q"].append(output[:, -1, :D_MODEL].detach().cpu().float())
            return hook_fn
        hooks.append(fused.register_forward_hook(make_q_hook(layer_idx)))

        # up_proj hook
        up_proj = model.gpt_neox.layers[layer_idx].mlp.dense_h_to_4h
        def make_up_hook(li):
            def hook_fn(module, input, output):
                captures[li]["up"].append(output[:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(up_proj.register_forward_hook(make_up_hook(layer_idx)))

    log(f"  Running {len(probes)} probes...")
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to("mps")
        with torch.no_grad():
            _ = model(input_ids)
    log(f"  Done in {time.time() - t0:.1f}s")

    for h in hooks:
        h.remove()

    # Stack
    Q_acts, UP_acts = {}, {}
    for frac, li in target_layers.items():
        Q_acts[frac] = torch.cat(captures[li]["Q"], dim=0).numpy()
        UP_acts[frac] = torch.cat(captures[li]["up"], dim=0).numpy()

    del model, tokenizer
    gc.collect()
    torch.mps.empty_cache()

    return all_W_q, all_W_up, Q_acts, UP_acts


def pca_basis(X: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Returns (basis, explained_variance_ratio). basis: (k, d)."""
    centered = X - X.mean(axis=0)
    _, S, Vt = np.linalg.svd(centered, full_matrices=False)
    total = np.sum(S ** 2)
    return Vt[:k], (S[:k] ** 2) / total


# ══════════════════════════════════════════════════════════════════════
# TEST 1: SVD-Crystal alignment
# ══════════════════════════════════════════════════════════════════════

def test_svd_crystal_alignment(all_W_q, all_W_up, Q_acts, UP_acts, depths):
    """Do SVD output directions of W_q/W_up align with crystal bases?"""
    log(f"\n{'='*60}")
    log(f"TEST 1: SVD-Crystal alignment")
    log(f"{'='*60}")

    results = []
    for frac in depths:
        li = min(int(round(frac * (N_LAYERS - 1))), N_LAYERS - 1)

        B_q, _ = pca_basis(Q_acts[frac], PCA_DIM)      # (64, d_model) — Q crystal
        B_up, _ = pca_basis(UP_acts[frac], PCA_DIM)     # (64, d_ffn) — FFN crystal

        W_q = all_W_q[li]   # (d_model, d_model)
        W_up = all_W_up[li]  # (d_ffn, d_model)

        # SVD of W_q
        U_q, S_q, Vt_q = np.linalg.svd(W_q, full_matrices=False)
        # SVD of W_up
        U_up, S_up, Vt_up = np.linalg.svd(W_up, full_matrices=False)

        # All comparisons in d_model space (where both beams cross)
        # Vt rows = input directions in d_model for both W_q and W_up
        # U_q columns = output directions in d_model (W_q is square)
        # U_up columns are in d_ffn — not comparable, skip

        # FFN input basis: use Vt_up (how W_up reads from d_model)
        B_ffn_in = Vt_up[:PCA_DIM, :]  # (64, d_model)

        for k in [64, 128, 256, 512]:
            # W_q output (U_q) ↔ Q crystal (both in d_model)
            overlap_q_out = subspace_overlap(U_q[:, :k], B_q.T)

            # W_q input (Vt_q) ↔ Q crystal
            overlap_q_in_q = subspace_overlap(Vt_q[:k, :].T, B_q.T)

            # W_q input (Vt_q) ↔ FFN input directions
            overlap_q_in_ffn = subspace_overlap(Vt_q[:k, :].T, B_ffn_in.T)

            # W_up input (Vt_up) ↔ Q crystal (cross-beam alignment)
            overlap_up_in_q = subspace_overlap(Vt_up[:k, :].T, B_q.T)

            if k == 64:
                results.append({
                    "depth": frac,
                    "layer": li,
                    "k": k,
                    "Wq_output_vs_Qcrystal": float(overlap_q_out),
                    "Wq_input_vs_Qcrystal": float(overlap_q_in_q),
                    "Wq_input_vs_FFN_input": float(overlap_q_in_ffn),
                    "Wup_input_vs_Qcrystal": float(overlap_up_in_q),
                })
                log(f"  L{li:2d} (d={frac:.1f}) k={k}: "
                    f"Wq_out↔Q={overlap_q_out:.4f}, "
                    f"Wq_in↔Q={overlap_q_in_q:.4f}, "
                    f"Wq_in↔FFN={overlap_q_in_ffn:.4f}, "
                    f"Wup_in↔Q={overlap_up_in_q:.4f}")

    return results


# ══════════════════════════════════════════════════════════════════════
# TEST 2: Shared warp — do W_q and W_up read from the same inputs?
# ══════════════════════════════════════════════════════════════════════

def test_shared_warp(all_W_q, all_W_up, depths):
    """Principal angles between input spaces (Vt) of W_q and W_up."""
    log(f"\n{'='*60}")
    log(f"TEST 2: Shared warp — input space overlap")
    log(f"{'='*60}")

    results = []
    for frac in depths:
        li = min(int(round(frac * (N_LAYERS - 1))), N_LAYERS - 1)

        _, _, Vt_q = np.linalg.svd(all_W_q[li], full_matrices=False)
        _, _, Vt_up = np.linalg.svd(all_W_up[li], full_matrices=False)

        for k in [16, 64, 256]:
            # Principal angles between top-k input subspaces
            angles = principal_angles_deg(Vt_q[:k, :].T, Vt_up[:k, :].T)
            mean_angle = float(angles.mean())
            median_angle = float(np.median(angles))
            min_angle = float(angles.min())

            # Overlap metric
            overlap = subspace_overlap(Vt_q[:k, :].T, Vt_up[:k, :].T)

            results.append({
                "depth": frac,
                "layer": li,
                "k": k,
                "mean_principal_angle": mean_angle,
                "median_principal_angle": median_angle,
                "min_principal_angle": min_angle,
                "overlap": float(overlap),
            })

            if k == 64:
                log(f"  L{li:2d} (d={frac:.1f}) k={k}: "
                    f"mean_angle={mean_angle:.1f}°, "
                    f"overlap={overlap:.4f}")

    return results


# ══════════════════════════════════════════════════════════════════════
# TEST 3: Loom angle — output spaces of W_q vs W_up
# ══════════════════════════════════════════════════════════════════════

def test_loom_angle(all_W_q, all_W_up, depths):
    """The crossing angle between the two beams from the output side."""
    log(f"\n{'='*60}")
    log(f"TEST 3: Loom angle — output space crossing")
    log(f"{'='*60}")

    results = []
    for frac in depths:
        li = min(int(round(frac * (N_LAYERS - 1))), N_LAYERS - 1)

        U_q, _, _ = np.linalg.svd(all_W_q[li], full_matrices=False)
        U_up, _, _ = np.linalg.svd(all_W_up[li], full_matrices=False)

        # W_up output is d_ffn, W_q output is d_model
        # Both live in d_model input space (columns of U are in the row space)
        # Actually U_q: (d_model, d_model), U_up: (d_ffn, d_model)
        # We need to compare in the SHARED d_model space
        # U_q columns are in d_model space
        # U_up columns are in d_ffn space — NOT directly comparable
        # But Vt_q and Vt_up rows ARE in d_model space (input side)

        # The loom angle should be measured on the INPUT side
        # (where both beams read from the same residual stream)
        _, _, Vt_q = np.linalg.svd(all_W_q[li], full_matrices=False)
        _, _, Vt_up = np.linalg.svd(all_W_up[li], full_matrices=False)

        for k in [8, 16, 32, 64]:
            angles = principal_angles_deg(Vt_q[:k, :].T, Vt_up[:k, :].T)

            results.append({
                "depth": frac,
                "layer": li,
                "k": k,
                "angles": angles.tolist(),
                "mean_angle": float(angles.mean()),
                "min_angle": float(angles.min()),
                "max_angle": float(angles.max()),
            })

            if k == 32:
                log(f"  L{li:2d} (d={frac:.1f}) k={k}: "
                    f"angles=[{angles[0]:.1f}°, {angles[k//2]:.1f}°, {angles[-1]:.1f}°], "
                    f"mean={angles.mean():.1f}°")

    return results


# ══════════════════════════════════════════════════════════════════════
# TEST 4: Weave decomposition — warp × weft energy
# ══════════════════════════════════════════════════════════════════════

def test_weave_decomposition(all_W_q, all_W_up, Q_acts, UP_acts, depths):
    """Project W_q into joint (Q-crystal × FFN-crystal) basis.

    The weave matrix M = B_q @ W_q @ B_res.T captures warp×weft crossings.
    Compare energy in:
      - Q-only subspace (crystal lens result: ~2.5%)
      - FFN-only subspace
      - Joint Q+FFN subspace
      - Warp×weft (Q rows × FFN columns of W_q)
    """
    log(f"\n{'='*60}")
    log(f"TEST 4: Weave decomposition")
    log(f"{'='*60}")

    results = []
    for frac in depths:
        li = min(int(round(frac * (N_LAYERS - 1))), N_LAYERS - 1)
        W = all_W_q[li]
        total_energy = float(np.sum(W ** 2))

        B_q, _ = pca_basis(Q_acts[frac], PCA_DIM)   # (64, d_model)
        # For up_proj activations: they're in d_ffn space, but we need d_model basis
        # Use the INPUT to up_proj (= hidden states) as the residual beam
        # Actually, UP_acts are (n_probes, d_ffn) — too big. Let's use the
        # SVD input directions of W_up as the "FFN reading beam" in d_model
        _, _, Vt_up = np.linalg.svd(all_W_up[li], full_matrices=False)
        B_ffn_input = Vt_up[:PCA_DIM, :]  # (64, d_model) — how FFN reads residual

        # Q-only: project W rows onto Q basis
        coeffs_q = W @ B_q.T  # (d_model, 64)
        energy_q_rows = float(np.sum(coeffs_q ** 2))

        # FFN-input-only: project W columns onto FFN input basis
        coeffs_ffn = B_ffn_input @ W.T  # (64, d_model)
        energy_ffn_cols = float(np.sum(coeffs_ffn ** 2))

        # Joint: project W into B_q (output) × B_ffn (input) jointly
        # M = B_q @ W @ B_ffn.T  — the weave matrix (64, 64)
        M_weave = B_q @ W @ B_ffn_input.T  # (64, 64)
        energy_weave = float(np.sum(M_weave ** 2))

        # Reconstruct from weave and measure
        W_weave_reconstructed = B_q.T @ M_weave @ B_ffn_input  # (d_model, d_model)
        recon_energy = float(np.sum(W_weave_reconstructed ** 2))
        recon_error = float(np.sum((W - W_weave_reconstructed) ** 2))

        # Combined (union of Q and FFN subspaces, not intersection)
        B_combined = np.vstack([B_q, B_ffn_input])  # (128, d_model)
        # Orthogonalize
        Q_orth, _ = np.linalg.qr(B_combined.T)  # (d_model, 128)
        coeffs_combined = W @ Q_orth  # (d_model, 128)
        energy_combined = float(np.sum(coeffs_combined ** 2))

        results.append({
            "depth": frac,
            "layer": li,
            "total_energy": total_energy,
            "q_rows_energy_frac": energy_q_rows / total_energy,
            "ffn_cols_energy_frac": energy_ffn_cols / total_energy,
            "weave_energy_frac": energy_weave / total_energy,
            "combined_energy_frac": energy_combined / total_energy,
            "weave_recon_frac": recon_energy / total_energy,
            "random_baseline": 2 * PCA_DIM / D_MODEL,  # expected for 128 random dims
        })

        log(f"  L{li:2d} (d={frac:.1f}): "
            f"Q_rows={energy_q_rows/total_energy:.4f}, "
            f"FFN_cols={energy_ffn_cols/total_energy:.4f}, "
            f"weave={energy_weave/total_energy:.4f}, "
            f"combined={energy_combined/total_energy:.4f} "
            f"(random={2*PCA_DIM/D_MODEL:.4f})")

    return results


# ══════════════════════════════════════════════════════════════════════
# TEST 5: Tension profile — SVD singular values in crystal coords
# ══════════════════════════════════════════════════════════════════════

def test_tension_profile(all_W_q, Q_acts, UP_acts, depths):
    """Do the high-magnitude (high-S) SVD directions align with crystal?"""
    log(f"\n{'='*60}")
    log(f"TEST 5: Tension profile — magnitude × crystal alignment")
    log(f"{'='*60}")

    results = []
    for frac in depths:
        li = min(int(round(frac * (N_LAYERS - 1))), N_LAYERS - 1)
        W = all_W_q[li]

        U, S, Vt = np.linalg.svd(W, full_matrices=False)
        B_q, _ = pca_basis(Q_acts[frac], PCA_DIM)

        # For each SVD component i: how aligned is it with the crystal?
        # Component i: outer product of U[:,i] (output) and Vt[i,:] (input)
        # Crystal alignment of output direction: |B_q @ U[:,i]|²
        output_crystal_alignment = np.sum((B_q @ U) ** 2, axis=0)  # (d_model,)

        # Weighted by singular value: are high-S directions more crystal-aligned?
        total_s2 = np.sum(S ** 2)
        s2_frac = S ** 2 / total_s2

        # Top-k crystal alignment weighted by importance
        for k in [16, 64, 256]:
            top_k_alignment = float(np.sum(output_crystal_alignment[:k] * s2_frac[:k]))
            bottom_k_alignment = float(np.sum(output_crystal_alignment[-k:] * s2_frac[-k:]))
            mean_top = float(np.mean(output_crystal_alignment[:k]))
            mean_bottom = float(np.mean(output_crystal_alignment[-k:]))

            if k == 64:
                results.append({
                    "depth": frac,
                    "layer": li,
                    "k": k,
                    "top_k_mean_crystal_alignment": mean_top,
                    "bottom_k_mean_crystal_alignment": mean_bottom,
                    "ratio": mean_top / (mean_bottom + 1e-10),
                })
                log(f"  L{li:2d} (d={frac:.1f}) k={k}: "
                    f"top_align={mean_top:.4f}, "
                    f"bottom_align={mean_bottom:.4f}, "
                    f"ratio={mean_top/(mean_bottom+1e-10):.2f}×")

    return results


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    probes = load_probes()
    depths = [0.0, 0.2, 0.5, 0.7, 0.9]

    all_W_q, all_W_up, Q_acts, UP_acts = extract_all(probes, depths)

    results = {
        "svd_crystal_alignment": test_svd_crystal_alignment(
            all_W_q, all_W_up, Q_acts, UP_acts, depths),
        "shared_warp": test_shared_warp(all_W_q, all_W_up, depths),
        "loom_angle": test_loom_angle(all_W_q, all_W_up, depths),
        "weave_decomposition": test_weave_decomposition(
            all_W_q, all_W_up, Q_acts, UP_acts, depths),
        "tension_profile": test_tension_profile(
            all_W_q, Q_acts, UP_acts, depths),
    }

    elapsed = time.time() - t_start
    results["meta"] = {"model": MODEL_NAME, "elapsed_seconds": elapsed,
                       "pca_dim": PCA_DIM}

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Loom Structure")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s")
    log(f"  Results saved to {out_path}")


if __name__ == "__main__":
    main()
