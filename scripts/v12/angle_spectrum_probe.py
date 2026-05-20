"""Angle Spectrum Probe — What information lives at each crossing angle?

We found 6 characteristic angles: 25°, 45°, 53°, 61°, 67°, 77°.
Now probe: what does each angle band carry?

Protocol:
  1. Take W_q and W_up at depth 0.5 (layer 16)
  2. Compute CCA (canonical correlation analysis) — gives paired directions
     in d_model space at each principal angle
  3. Bin directions into angle bands
  4. For each band: project probe hidden states onto those directions
  5. Compute 8×8 combinator cosine matrix in each band's subspace
  6. Compare to known crystal targets (0.91-0.94 agreement)

Also probe Q↔K crossing — the attention internal structure should
concentrate at a different angle than the holographic crystal.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/angle_spectrum_probe.py

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
SVD_K = 256  # enough directions to populate all angle bands

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "angle-spectrum"

# Known crystal targets from pcaq_targets.json
COMBINATOR_ORDER = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]

# Angle bands (degrees)
ANGLE_BANDS = [
    ("shared",     0, 35),
    ("mid_low",   35, 50),
    ("attn_clust", 50, 58),
    ("transition", 58, 64),
    ("holographic", 64, 72),
    ("peripheral", 72, 82),
    ("private",    82, 91),
]


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def cosine_matrix(X: np.ndarray, indices: list[int]) -> np.ndarray:
    vecs = X[indices]
    norms = np.maximum(np.linalg.norm(vecs, axis=1, keepdims=True), 1e-8)
    vecs_n = vecs / norms
    return vecs_n @ vecs_n.T


def rdm_correlation(A: np.ndarray, B: np.ndarray) -> float:
    n = A.shape[0]
    idx = np.triu_indices(n, k=1)
    a = A[idx] - A[idx].mean()
    b = B[idx] - B[idx].mean()
    denom = np.sqrt(np.sum(a**2)) * np.sqrt(np.sum(b**2))
    return float(np.sum(a * b) / denom) if denom > 1e-10 else 0.0


def load_probes():
    path = Path(__file__).parent.parent.parent / "lattice" / "binding_chain_probes.json"
    with open(path) as f:
        return json.load(f)


def get_pure_indices(probes):
    pure_idx = {}
    for i, p in enumerate(probes):
        if p["axis"].startswith("pure/"):
            comb = p["axis"].split("/")[1]
            pure_idx[comb] = i
    return pure_idx


def extract_all(probes):
    """Extract weights + hidden state activations at target layer."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    log(f"  Loading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float32, device_map="mps")
    model.eval()

    # Weights
    layer = model.gpt_neox.layers[TARGET_LAYER]
    qkv = layer.attention.query_key_value.weight.detach().cpu().float().numpy()
    W_q = qkv[:D_MODEL, :]
    W_k = qkv[D_MODEL:2*D_MODEL, :]
    W_up = layer.mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()

    # Hidden state activations (residual stream input to this layer)
    captures = []
    def hook_fn(module, input, output):
        # input[0] is the residual stream entering this layer
        inp = input[0] if isinstance(input, tuple) else input
        captures.append(inp[:, -1, :].detach().cpu().float())

    hook = model.gpt_neox.layers[TARGET_LAYER].register_forward_hook(hook_fn)

    log(f"  Running {len(probes)} probes...")
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to("mps")
        with torch.no_grad():
            _ = model(input_ids)

    hook.remove()
    hidden_states = torch.cat(captures, dim=0).numpy()  # (n_probes, d_model)
    log(f"  Hidden states: {hidden_states.shape}")

    del model, tokenizer
    gc.collect()
    torch.mps.empty_cache()

    return W_q, W_k, W_up, hidden_states


def compute_cca_directions(W_a: np.ndarray, W_b: np.ndarray, k: int):
    """Compute canonical correlation analysis between input spaces.

    Returns:
      angles: (k,) principal angles in degrees
      dirs_a: (k, d_model) directions in d_model that W_a prefers
      dirs_b: (k, d_model) directions in d_model that W_b prefers
      dirs_shared: (k, d_model) midpoint directions (bisector of each pair)
    """
    # SVD to get input bases
    _, _, Vt_a = np.linalg.svd(W_a, full_matrices=False)
    _, _, Vt_b = np.linalg.svd(W_b, full_matrices=False)

    # Top-k input subspaces
    A = Vt_a[:k, :].T  # (d_model, k)
    B = Vt_b[:k, :].T  # (d_model, k)

    # QR orthogonalize
    Qa, _ = np.linalg.qr(A)  # (d_model, k)
    Qb, _ = np.linalg.qr(B)  # (d_model, k)

    # CCA: SVD of Qa.T @ Qb
    U_cca, S_cca, Vt_cca = np.linalg.svd(Qa.T @ Qb, full_matrices=False)

    angles = np.degrees(np.arccos(np.clip(S_cca, 0, 1)))

    # CCA directions in d_model space
    dirs_a = Qa @ U_cca      # (d_model, k) — directions from A's perspective
    dirs_b = Qb @ Vt_cca.T   # (d_model, k) — directions from B's perspective

    # Shared midpoint directions
    dirs_shared = dirs_a + dirs_b
    norms = np.linalg.norm(dirs_shared, axis=0, keepdims=True)
    dirs_shared = dirs_shared / np.maximum(norms, 1e-8)

    return angles, dirs_a, dirs_b, dirs_shared


def probe_angle_bands(
    angles: np.ndarray,
    dirs_shared: np.ndarray,
    hidden_states: np.ndarray,
    pure_indices: list[int],
    crossing_name: str,
) -> list[dict]:
    """Project hidden states onto each angle band, measure crystal structure."""
    log(f"\n  {crossing_name}:")

    results = []
    for band_name, lo, hi in ANGLE_BANDS:
        mask = (angles >= lo) & (angles < hi)
        n_dirs = int(mask.sum())

        if n_dirs < 2:
            results.append({
                "band": band_name, "angle_range": [lo, hi],
                "n_directions": n_dirs, "crystal_agreement": None,
            })
            log(f"    {band_name:12s} [{lo:2d}°-{hi:2d}°]: {n_dirs:3d} dirs — too few")
            continue

        # Project hidden states onto this band's directions
        band_dirs = dirs_shared[:, mask]  # (d_model, n_dirs)
        projected = hidden_states @ band_dirs  # (n_probes, n_dirs)

        # Compute 8×8 combinator cosine matrix
        cos_mat = cosine_matrix(projected, pure_indices)

        # Compare to full hidden state cosine matrix (the crystal reference)
        cos_full = cosine_matrix(hidden_states, pure_indices)
        agreement = rdm_correlation(cos_mat, cos_full)

        # Also compute raw combinator similarities within this band
        n_comb = len(pure_indices)
        upper_tri = cos_mat[np.triu_indices(n_comb, k=1)]
        mean_cos = float(upper_tri.mean())
        std_cos = float(upper_tri.std())

        # WHNF polarity (is WHNF anti-correlated with others in this band?)
        whnf_idx = COMBINATOR_ORDER.index("WHNF")
        whnf_cos = [cos_mat[whnf_idx, j] for j in range(n_comb) if j != whnf_idx]
        mean_whnf = float(np.mean(whnf_cos))

        results.append({
            "band": band_name,
            "angle_range": [lo, hi],
            "n_directions": n_dirs,
            "crystal_agreement": float(agreement),
            "mean_cosine": mean_cos,
            "std_cosine": std_cos,
            "whnf_polarity": mean_whnf,
        })

        log(f"    {band_name:12s} [{lo:2d}°-{hi:2d}°]: {n_dirs:3d} dirs, "
            f"crystal={agreement:.4f}, mean_cos={mean_cos:.3f}, "
            f"WHNF={mean_whnf:.3f}")

    return results


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    probes = load_probes()
    pure_idx = get_pure_indices(probes)
    pure_indices = [pure_idx[c] for c in COMBINATOR_ORDER if c in pure_idx]
    log(f"  Pure combinator indices: {len(pure_indices)}")

    W_q, W_k, W_up, hidden_states = extract_all(probes)

    results = {}

    # ── Q ↔ UP crossing (holographic) ──
    log(f"\n{'='*60}")
    log(f"Q ↔ UP crossing (the holographic pair)")
    log(f"{'='*60}")
    angles_qu, dirs_a_qu, dirs_b_qu, dirs_shared_qu = compute_cca_directions(W_q, W_up, SVD_K)
    log(f"  Angle range: [{angles_qu.min():.1f}°, {angles_qu.max():.1f}°]")
    log(f"  Angle distribution: "
        f"<30°={np.sum(angles_qu < 30)}, "
        f"30-50°={np.sum((angles_qu >= 30) & (angles_qu < 50))}, "
        f"50-60°={np.sum((angles_qu >= 50) & (angles_qu < 60))}, "
        f"60-72°={np.sum((angles_qu >= 60) & (angles_qu < 72))}, "
        f"72-82°={np.sum((angles_qu >= 72) & (angles_qu < 82))}, "
        f">82°={np.sum(angles_qu >= 82)}")

    results["q_up"] = probe_angle_bands(
        angles_qu, dirs_shared_qu, hidden_states, pure_indices, "Q↔UP")

    # ── Q ↔ K crossing (attention internal) ──
    log(f"\n{'='*60}")
    log(f"Q ↔ K crossing (attention addressing)")
    log(f"{'='*60}")
    angles_qk, dirs_a_qk, dirs_b_qk, dirs_shared_qk = compute_cca_directions(W_q, W_k, SVD_K)
    log(f"  Angle range: [{angles_qk.min():.1f}°, {angles_qk.max():.1f}°]")
    log(f"  Angle distribution: "
        f"<30°={np.sum(angles_qk < 30)}, "
        f"30-50°={np.sum((angles_qk >= 30) & (angles_qk < 50))}, "
        f"50-60°={np.sum((angles_qk >= 50) & (angles_qk < 60))}, "
        f"60-72°={np.sum((angles_qk >= 60) & (angles_qk < 72))}, "
        f">72°={np.sum(angles_qk >= 72)}")

    results["q_k"] = probe_angle_bands(
        angles_qk, dirs_shared_qk, hidden_states, pure_indices, "Q↔K")

    # ── K ↔ UP crossing (key-FFN) ──
    log(f"\n{'='*60}")
    log(f"K ↔ UP crossing (key-FFN)")
    log(f"{'='*60}")
    angles_ku, _, _, dirs_shared_ku = compute_cca_directions(W_k, W_up, SVD_K)
    results["k_up"] = probe_angle_bands(
        angles_ku, dirs_shared_ku, hidden_states, pure_indices, "K↔UP")

    # ── Save ──
    elapsed = time.time() - t_start
    results["meta"] = {"model": MODEL_NAME, "target_layer": TARGET_LAYER,
                       "svd_k": SVD_K, "n_probes": len(probes),
                       "elapsed_seconds": elapsed}

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    # ── Summary ──
    log(f"\n{'═'*60}")
    log(f"SUMMARY — Angle Spectrum Probe")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s\n")

    log(f"  CRYSTAL AGREEMENT BY ANGLE BAND:")
    log(f"  {'Band':>12s} {'Q↔UP':>8s} {'Q↔K':>8s} {'K↔UP':>8s}")
    log(f"  {'─'*12} {'─'*8} {'─'*8} {'─'*8}")
    for i, (band_name, lo, hi) in enumerate(ANGLE_BANDS):
        vals = []
        for key in ["q_up", "q_k", "k_up"]:
            r = results[key][i]
            v = r["crystal_agreement"]
            vals.append(f"{v:.4f}" if v is not None else "   n/a")
        log(f"  {band_name:>12s}  {'  '.join(vals)}")

    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
