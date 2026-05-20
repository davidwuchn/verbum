"""Hologram Extraction Experiment — Can we read the COMPLETE crystal?

Hypothesis: The dual-beam technique (PCA-Q + PCA-up, 0.91-0.94 agreement)
can decode the holographic interference patterns from a teacher's weight
matrices. If we can read them, we can etch them into V12's ternary plates.

Experiment:
  1. Load Pythia-2.8b, pick ONE layer at 50% depth (layer 16)
  2. Extract W_q (2560, 2560) and W_up (10240, 2560) — the raw crystals
  3. SVD each to find their principal directions in d_model space
  4. Measure: principal angles between Q and FFN subspaces (holographic angle)
  5. Build unified holographic plate via SVD lens
  6. Ternary quantize the plate
  7. Read back with each beam — measure crystal preservation
  8. Sweep: what fraction of the crystal is captured at different plate sizes?
  9. ALSO: run the basin probes through the model, PCA the activations,
     and verify the beam readings match the weight-space crystals.

This proves (or disproves) that the beam technique gives us WRITABLE
holograms, not just readable crystal indicators.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/hologram_extraction_exp.py

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

# Model config
MODEL_KEY = "pythia-2.8b"
MODEL_NAME = "EleutherAI/pythia-2.8b-deduped"
N_LAYERS = 32
D_MODEL = 2560
D_FFN = 10240
TARGET_LAYER = 16  # 50% depth


def load_probes() -> list[dict]:
    probe_path = Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json"
    with open(probe_path) as f:
        data = json.load(f)
        return data if isinstance(data, list) else data["probes"]


def cosine_rdm(X: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    Xn = X / norms
    return Xn @ Xn.T


def rdm_correlation(A: np.ndarray, B: np.ndarray) -> float:
    """Upper-triangle Pearson correlation between two RDMs."""
    n = A.shape[0]
    idx = np.triu_indices(n, k=1)
    a = A[idx]
    b = B[idx]
    a_c = a - a.mean()
    b_c = b - b.mean()
    denom = (np.sqrt(np.sum(a_c**2)) * np.sqrt(np.sum(b_c**2)))
    if denom < 1e-10:
        return 0.0
    return float(np.sum(a_c * b_c) / denom)


def principal_angles_deg(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Principal angles between column spaces of A and B, in degrees."""
    Qa, _ = np.linalg.qr(A)
    Qb, _ = np.linalg.qr(B)
    M = Qa.T @ Qb
    svals = np.linalg.svd(M, compute_uv=False)
    svals = np.clip(svals, 0, 1)
    return np.degrees(np.arccos(svals))


# ══════════════════════════════════════════════════════════════════════
# Part 1: Extract raw weight matrices from one teacher layer
# ══════════════════════════════════════════════════════════════════════

def extract_teacher_weights():
    """Load Pythia-2.8b, extract W_q and W_up from layer 16."""
    import torch
    from transformers import AutoModelForCausalLM

    print(f"\n  Loading {MODEL_NAME}...", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float32, device_map="mps",
    )
    model.eval()

    layer = model.gpt_neox.layers[TARGET_LAYER]

    # Pythia has fused QKV: query_key_value (3*d_model, d_model)
    qkv_weight = layer.attention.query_key_value.weight.detach().cpu().float().numpy()
    # Split: first d_model rows = Q, next = K, next = V
    W_q = qkv_weight[:D_MODEL, :]        # (2560, 2560)
    W_k = qkv_weight[D_MODEL:2*D_MODEL, :]
    W_v = qkv_weight[2*D_MODEL:, :]

    # FFN: dense_h_to_4h (d_ffn, d_model)
    W_up = layer.mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()  # (10240, 2560)
    W_down = layer.mlp.dense_4h_to_h.weight.detach().cpu().float().numpy()  # (2560, 10240)

    print(f"  W_q:    {W_q.shape}")
    print(f"  W_k:    {W_k.shape}")
    print(f"  W_v:    {W_v.shape}")
    print(f"  W_up:   {W_up.shape}")
    print(f"  W_down: {W_down.shape}")

    del model
    gc.collect()
    import torch as _t
    if _t.backends.mps.is_available():
        _t.mps.empty_cache()

    return W_q, W_k, W_v, W_up, W_down


# ══════════════════════════════════════════════════════════════════════
# Part 2: SVD beam analysis — read the crystal from weights
# ══════════════════════════════════════════════════════════════════════

def analyze_weight_crystal(W: np.ndarray, name: str, k_values: list[int]) -> dict:
    """Full SVD analysis of a weight matrix.

    W: (out_features, in_features) = (d_out, d_model)
    Each ROW reads from d_model residual stream.
    SVD: W = U @ diag(S) @ Vt
      - Vt rows = principal directions in d_model (the crystal axes)
      - S = importance of each axis
      - U = what the layer DOES with each crystal reading
    """
    U, S, Vt = np.linalg.svd(W, full_matrices=False)

    total_var = np.sum(S ** 2)
    results = {
        "name": name,
        "shape": list(W.shape),
        "singular_values": S.tolist(),
        "total_frobenius": float(np.sqrt(total_var)),
    }

    # How much crystal is captured at each k?
    for k in k_values:
        k_eff = min(k, len(S))
        explained = float(np.sum(S[:k_eff] ** 2) / total_var)
        results[f"explained_k{k}"] = explained

    # Effective rank
    cumvar = np.cumsum(S ** 2) / total_var
    for threshold in [0.50, 0.80, 0.90, 0.95, 0.99]:
        rank = int(np.searchsorted(cumvar, threshold)) + 1
        results[f"rank_{int(threshold*100)}pct"] = rank

    # Spectral decay
    s_norm = S / (S[0] + 1e-10)
    results["spectral_decay"] = {
        "s10": float(s_norm[min(9, len(s_norm)-1)]),
        "s50": float(s_norm[min(49, len(s_norm)-1)]),
        "s100": float(s_norm[min(99, len(s_norm)-1)]),
        "s256": float(s_norm[min(255, len(s_norm)-1)]),
    }

    return results, U, S, Vt


# ══════════════════════════════════════════════════════════════════════
# Part 3: Build holographic plate and test roundtrip
# ══════════════════════════════════════════════════════════════════════

def build_and_test_holographic_plate(
    W_q: np.ndarray,
    W_up: np.ndarray,
    probes: list[dict],
    plate_dims: list[int],
) -> dict:
    """Build unified holographic plate at various sizes, test crystal preservation.

    The plate stores BOTH the attention crystal (from W_q) and the FFN crystal
    (from W_up) in a single ternary medium.

    Steps:
      1. SVD W_q → top-k directions in d_model (the Q crystal)
      2. SVD W_up → top-k directions in d_model (the FFN crystal)
      3. Stack, orthogonalize → unified basis
      4. Ternary quantize → the plate
      5. Read back with each beam → measure preservation

    The key metric: RDM correlation between original weight-space crystal
    and ternary-plate crystal. This is the holographic fidelity.
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    # First: get ground truth activation-space crystals via probes
    print(f"\n  Running {len(probes)} probes through {MODEL_NAME}...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.bfloat16, device_map="mps",
    )
    model.eval()

    layer = model.gpt_neox.layers[TARGET_LAYER]

    hidden_states = []
    q_activations = []
    up_activations = []

    def h_hook(module, input, output):
        hidden_states.append(input[0][:, -1, :].detach().cpu().float())

    def qkv_hook(module, input, output):
        q_activations.append(output[:, -1, :D_MODEL].detach().cpu().float())

    def up_hook(module, input, output):
        up_activations.append(output[:, -1, :].detach().cpu().float())

    hooks = [
        layer.register_forward_hook(h_hook),
        layer.attention.query_key_value.register_forward_hook(qkv_hook),
        layer.mlp.dense_h_to_4h.register_forward_hook(up_hook),
    ]

    t0 = time.time()
    for i, probe in enumerate(probes):
        ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to("mps")
        with torch.no_grad():
            _ = model(ids)
        if (i + 1) % 50 == 0:
            print(f"    {i+1}/{len(probes)}...", flush=True)
    print(f"  Done in {time.time()-t0:.1f}s", flush=True)

    for h in hooks:
        h.remove()

    H = torch.cat(hidden_states, dim=0).numpy()         # (n_probes, 2560)
    Q_act = torch.cat(q_activations, dim=0).numpy()      # (n_probes, 2560)
    UP_act = torch.cat(up_activations, dim=0).numpy()     # (n_probes, 10240)

    del model, tokenizer
    gc.collect()
    import torch as _t
    if _t.backends.mps.is_available():
        _t.mps.empty_cache()

    # Ground truth activation RDMs
    rdm_q_act = cosine_rdm(Q_act)
    rdm_up_act = cosine_rdm(UP_act)
    rdm_h = cosine_rdm(H)

    print(f"\n  Ground truth RDMs computed:")
    print(f"    H shape:   {H.shape}")
    print(f"    Q shape:   {Q_act.shape}")
    print(f"    UP shape:  {UP_act.shape}")

    # Weight-space crystal RDMs (what SVD reads)
    # The crystal IS the weight matrix applied to hidden states
    # Q_crystal = H @ W_q.T, UP_crystal = H @ W_up.T
    Q_weight = H @ W_q.T     # (n_probes, d_q)
    UP_weight = H @ W_up.T   # (n_probes, d_ffn)
    rdm_q_weight = cosine_rdm(Q_weight)
    rdm_up_weight = cosine_rdm(UP_weight)

    # Verify: activation crystal ≈ weight crystal (should be ~1.0)
    q_act_vs_weight = rdm_correlation(rdm_q_act, rdm_q_weight)
    up_act_vs_weight = rdm_correlation(rdm_up_act, rdm_up_weight)
    print(f"\n  Activation vs weight-space crystal:")
    print(f"    Q:  {q_act_vs_weight:.4f} (should be ≈1.0)")
    print(f"    UP: {up_act_vs_weight:.4f} (should be ≈1.0)")

    # ── Now test holographic plates at various sizes ──────────
    results = {}

    # SVD the weight matrices
    U_q, S_q, Vt_q = np.linalg.svd(W_q, full_matrices=False)
    U_up, S_up, Vt_up = np.linalg.svd(W_up, full_matrices=False)

    for plate_k in plate_dims:
        print(f"\n  ── Plate dim k={plate_k} ──")

        k_q = min(plate_k, Vt_q.shape[0])
        k_up = min(plate_k, Vt_up.shape[0])

        # ── Method A: Separate plates (no holographic combination) ──
        # Just ternary-quantize the top-k SVD directions of each
        V_q_topk = Vt_q[:k_q].T   # (d_model, k_q) — Q crystal directions
        V_up_topk = Vt_up[:k_up].T  # (d_model, k_up) — FFN crystal directions

        # Continuous readout
        Q_svd_cont = H @ V_q_topk        # (n_probes, k_q)
        UP_svd_cont = H @ V_up_topk      # (n_probes, k_up)
        rdm_q_svd_cont = cosine_rdm(Q_svd_cont)
        rdm_up_svd_cont = cosine_rdm(UP_svd_cont)

        # Ternary readout
        V_q_tern = np.sign(V_q_topk)
        V_up_tern = np.sign(V_up_topk)
        Q_svd_tern = H @ V_q_tern
        UP_svd_tern = H @ V_up_tern
        rdm_q_svd_tern = cosine_rdm(Q_svd_tern)
        rdm_up_svd_tern = cosine_rdm(UP_svd_tern)

        sep_q_cont = rdm_correlation(rdm_q_act, rdm_q_svd_cont)
        sep_q_tern = rdm_correlation(rdm_q_act, rdm_q_svd_tern)
        sep_up_cont = rdm_correlation(rdm_up_act, rdm_up_svd_cont)
        sep_up_tern = rdm_correlation(rdm_up_act, rdm_up_svd_tern)

        print(f"    Separate plates:")
        print(f"      Q:  continuous={sep_q_cont:.4f}  ternary={sep_q_tern:.4f}")
        print(f"      UP: continuous={sep_up_cont:.4f}  ternary={sep_up_tern:.4f}")

        # ── Method B: Unified holographic plate ──
        # Stack both SVD directions, orthogonalize, ternary quantize
        V_combined = np.hstack([V_q_topk, V_up_topk])  # (d_model, k_q + k_up)
        Q_orth, R = np.linalg.qr(V_combined)
        plate_dim_total = Q_orth.shape[1]

        # Continuous unified plate
        plate_cont = Q_orth[:, :plate_dim_total]
        readout_cont = H @ plate_cont    # (n_probes, plate_dim_total)
        q_cont = readout_cont[:, :k_q]
        up_cont = readout_cont[:, k_q:]
        rdm_q_holo_cont = cosine_rdm(q_cont)
        rdm_up_holo_cont = cosine_rdm(up_cont)

        # Ternary unified plate
        plate_tern = np.sign(plate_cont)
        readout_tern = H @ plate_tern
        q_tern = readout_tern[:, :k_q]
        up_tern = readout_tern[:, k_q:]
        rdm_q_holo_tern = cosine_rdm(q_tern)
        rdm_up_holo_tern = cosine_rdm(up_tern)

        holo_q_cont = rdm_correlation(rdm_q_act, rdm_q_holo_cont)
        holo_q_tern = rdm_correlation(rdm_q_act, rdm_q_holo_tern)
        holo_up_cont = rdm_correlation(rdm_up_act, rdm_up_holo_cont)
        holo_up_tern = rdm_correlation(rdm_up_act, rdm_up_holo_tern)

        print(f"    Unified holographic plate ({plate_dim_total} cols):")
        print(f"      Q:  continuous={holo_q_cont:.4f}  ternary={holo_q_tern:.4f}")
        print(f"      UP: continuous={holo_up_cont:.4f}  ternary={holo_up_tern:.4f}")

        # ── Method C: Direct weight ternary (no SVD lens, just sign(W)) ──
        W_q_tern = np.sign(W_q)
        W_up_tern = np.sign(W_up)
        Q_direct = H @ W_q_tern.T
        UP_direct = H @ W_up_tern.T
        rdm_q_direct = cosine_rdm(Q_direct)
        rdm_up_direct = cosine_rdm(UP_direct)
        direct_q = rdm_correlation(rdm_q_act, rdm_q_direct)
        direct_up = rdm_correlation(rdm_up_act, rdm_up_direct)

        # ── Cross-talk: does Q beam read FFN signal? ──
        crosstalk_q_reads_up = rdm_correlation(rdm_up_act, rdm_q_holo_tern)
        crosstalk_up_reads_q = rdm_correlation(rdm_q_act, rdm_up_holo_tern)

        # ── Principal angles between Q and UP subspaces ──
        angles = principal_angles_deg(V_q_topk, V_up_topk)

        results[plate_k] = {
            "separate_q_continuous": sep_q_cont,
            "separate_q_ternary": sep_q_tern,
            "separate_up_continuous": sep_up_cont,
            "separate_up_ternary": sep_up_tern,
            "holographic_q_continuous": holo_q_cont,
            "holographic_q_ternary": holo_q_tern,
            "holographic_up_continuous": holo_up_cont,
            "holographic_up_ternary": holo_up_tern,
            "direct_ternary_q": direct_q,
            "direct_ternary_up": direct_up,
            "crosstalk_q_reads_up": crosstalk_q_reads_up,
            "crosstalk_up_reads_q": crosstalk_up_reads_q,
            "principal_angles_mean_deg": float(np.mean(angles)),
            "principal_angles_min_deg": float(np.min(angles)),
            "principal_angles_top10_deg": angles[:10].tolist(),
            "plate_total_dims": plate_dim_total,
        }

        if plate_k == plate_dims[0]:
            # Only compute once
            results["direct_ternary"] = {
                "q_preservation": direct_q,
                "up_preservation": direct_up,
            }

    results["activation_vs_weight"] = {
        "q": q_act_vs_weight,
        "up": up_act_vs_weight,
    }

    return results


# ══════════════════════════════════════════════════════════════════════
# Part 4: Sign structure comparison (V12 vs teacher)
# ══════════════════════════════════════════════════════════════════════

def weight_sign_structure(W: np.ndarray, name: str) -> dict:
    """Characterize the sign structure of a weight matrix."""
    U, S, Vt = np.linalg.svd(W, full_matrices=False)
    total_var = np.sum(S ** 2)

    # The sign pattern in the SVD basis
    # V directions (d_model space): how structured are they?
    V_top64 = Vt[:64]

    # Autocorrelation within each direction
    autocorrs = []
    for i in range(min(64, V_top64.shape[0])):
        row = V_top64[i]
        if len(row) > 1 and np.std(row) > 0:
            ac = np.corrcoef(row[:-1], row[1:])[0, 1]
            if not np.isnan(ac):
                autocorrs.append(ac)

    # Sign pattern of SVD directions
    V_signs = np.sign(V_top64)
    # How much of the structure survives ternary quantization?
    V_tern_recon = V_signs  # ternary version
    # Per-direction: cos(original, ternary)
    cos_per_dir = []
    for i in range(V_top64.shape[0]):
        d = np.dot(V_top64[i], V_tern_recon[i])
        n1 = np.linalg.norm(V_top64[i])
        n2 = np.linalg.norm(V_tern_recon[i])
        if n1 > 0 and n2 > 0:
            cos_per_dir.append(d / (n1 * n2))

    return {
        "name": name,
        "mean_svd_dir_autocorr": float(np.mean(autocorrs)) if autocorrs else 0.0,
        "mean_ternary_cosine": float(np.mean(cos_per_dir)) if cos_per_dir else 0.0,
        "explained_top64": float(np.sum(S[:64]**2) / total_var),
        "rank_90pct": int(np.searchsorted(np.cumsum(S**2)/total_var, 0.90)) + 1,
        "spectral_decay_10": float(S[9] / (S[0] + 1e-10)),
        "spectral_decay_50": float(S[49] / (S[0] + 1e-10)) if len(S) > 49 else 0.0,
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    output_dir = Path("/Users/mwhitford/src/verbum/results/hologram-extraction")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"  Hologram Extraction Experiment")
    print(f"  Model: {MODEL_NAME} layer {TARGET_LAYER} (50% depth)")
    print(f"{'='*70}")

    # ── Step 1: Extract raw weights ──────────────────────────
    print(f"\n{'─'*60}")
    print(f"  STEP 1: Extract teacher weight matrices")
    print(f"{'─'*60}")
    W_q, W_k, W_v, W_up, W_down = extract_teacher_weights()

    # ── Step 2: SVD crystal analysis ─────────────────────────
    print(f"\n{'─'*60}")
    print(f"  STEP 2: SVD beam analysis — read the crystal")
    print(f"{'─'*60}")

    k_values = [8, 16, 32, 64, 128, 256, 512]
    q_analysis, U_q, S_q, Vt_q = analyze_weight_crystal(W_q, "W_q", k_values)
    up_analysis, U_up, S_up, Vt_up = analyze_weight_crystal(W_up, "W_up", k_values)

    print(f"\n  W_q crystal spectrum:")
    print(f"    Explained variance: " + ", ".join(
        f"k={k}: {q_analysis[f'explained_k{k}']:.3f}" for k in k_values[:5]))
    print(f"    Effective rank: 90%→{q_analysis['rank_90pct']} | "
          f"95%→{q_analysis['rank_95pct']} | 99%→{q_analysis['rank_99pct']}")

    print(f"\n  W_up crystal spectrum:")
    print(f"    Explained variance: " + ", ".join(
        f"k={k}: {up_analysis[f'explained_k{k}']:.3f}" for k in k_values[:5]))
    print(f"    Effective rank: 90%→{up_analysis['rank_90pct']} | "
          f"95%→{up_analysis['rank_95pct']} | 99%→{up_analysis['rank_99pct']}")

    # Principal angles between Q and FFN subspaces
    V_q_64 = Vt_q[:64].T   # (d_model, 64)
    V_up_64 = Vt_up[:64].T
    angles = principal_angles_deg(V_q_64, V_up_64)
    print(f"\n  Holographic angle (Q ↔ FFN, top-64):")
    print(f"    Mean: {np.mean(angles):.1f}° | Min: {np.min(angles):.1f}° | Max: {np.max(angles):.1f}°")
    print(f"    Top-10: {', '.join(f'{a:.1f}°' for a in angles[:10])}")

    # ── Step 3: Sign structure analysis ──────────────────────
    print(f"\n{'─'*60}")
    print(f"  STEP 3: Weight sign structure (is the crystal in the signs?)")
    print(f"{'─'*60}")

    q_sign = weight_sign_structure(W_q, "W_q")
    up_sign = weight_sign_structure(W_up, "W_up")

    for label, ss in [("W_q", q_sign), ("W_up", up_sign)]:
        print(f"\n  {label}:")
        print(f"    SVD direction autocorrelation: {ss['mean_svd_dir_autocorr']:.4f}")
        print(f"    Ternary cosine (sign(Vt) vs Vt): {ss['mean_ternary_cosine']:.4f}")
        print(f"    Explained(k=64): {ss['explained_top64']:.3f}")
        print(f"    Rank(90%): {ss['rank_90pct']}")

    # ── Step 4: Holographic plate roundtrip ──────────────────
    print(f"\n{'─'*60}")
    print(f"  STEP 4: Holographic plate roundtrip (the acid test)")
    print(f"{'─'*60}")

    probes = load_probes()
    plate_dims = [16, 32, 64, 128, 256]
    plate_results = build_and_test_holographic_plate(W_q, W_up, probes, plate_dims)

    # ── Summary table ─────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  SUMMARY — Crystal extraction fidelity")
    print(f"{'='*70}")

    print(f"\n  {'k':>4s} │ {'Sep Q':>7s} {'Sep UP':>7s} │ {'Holo Q':>7s} {'Holo UP':>7s} │ {'Cross Q→UP':>10s} {'Cross UP→Q':>10s} │ {'Angle':>6s}")
    print(f"  {'─'*4}─┼─{'─'*7}─{'─'*7}─┼─{'─'*7}─{'─'*7}─┼─{'─'*10}─{'─'*10}─┼─{'─'*6}")
    for k in plate_dims:
        r = plate_results[k]
        print(f"  {k:4d} │ {r['separate_q_ternary']:7.4f} {r['separate_up_ternary']:7.4f} │ "
              f"{r['holographic_q_ternary']:7.4f} {r['holographic_up_ternary']:7.4f} │ "
              f"{r['crosstalk_q_reads_up']:10.4f} {r['crosstalk_up_reads_q']:10.4f} │ "
              f"{r['principal_angles_mean_deg']:5.1f}°")

    print(f"\n  Direct sign(W) ternary (full-rank, no SVD):")
    dt = plate_results.get("direct_ternary", {})
    print(f"    Q: {dt.get('q_preservation', 0):.4f} | UP: {dt.get('up_preservation', 0):.4f}")

    print(f"\n  Activation ↔ weight crystal match:")
    aw = plate_results.get("activation_vs_weight", {})
    print(f"    Q: {aw.get('q', 0):.4f} | UP: {aw.get('up', 0):.4f}")

    # ── Save ──────────────────────────────────────────────────
    all_results = {
        "model": MODEL_KEY,
        "layer": TARGET_LAYER,
        "q_crystal": q_analysis,
        "up_crystal": up_analysis,
        "q_sign_structure": q_sign,
        "up_sign_structure": up_sign,
        "holographic_angle": {
            "mean_deg": float(np.mean(angles)),
            "min_deg": float(np.min(angles)),
            "top10_deg": angles[:10].tolist(),
        },
        "plate_roundtrip": {str(k): v for k, v in plate_results.items()
                           if isinstance(k, int)},
        "direct_ternary": plate_results.get("direct_ternary"),
        "activation_vs_weight": plate_results.get("activation_vs_weight"),
    }

    out_path = output_dir / "results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=lambda x: x.tolist() if hasattr(x, 'tolist') else str(x))
    print(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
