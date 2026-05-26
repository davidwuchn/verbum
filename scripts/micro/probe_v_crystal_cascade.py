"""
Probe V-Crystal Cascade — Tracing grating-through-grating interference.

THE QUESTION: Attention beta-reduces over V. V carries the accumulated
output of all prior FFN gratings. When attention reduces over V, it mixes
the grating patterns. Then the result goes through the NEXT FFN grating.

This probe measures:
  1. V's combinator typing per head per layer (is V crystal-typed?)
  2. How attention's beta-reduction changes the crystal signature
     (pre-attn V vs post-attn output)
  3. The compound grating effect: does FFN output at layer N predict
     V's crystal profile at layer N+1?
  4. Progressive dimensionality of V in crystal space through depth
     (does the moiré resolve to 2D?)
  5. Off-diagonal energy in V's crystal projection (does V carry
     cross-PC coupling that compounds through depth?)

Uses the micro model (4 layers, d=128) with full trace capture.

Usage:
    cd verbum
    uv run python scripts/micro/probe_v_crystal_cascade.py [checkpoint_dir]

License: MIT
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import mlx.core as mx
import mlx.nn as nn

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import (
    MicroModel, MicroConfig,
    PCAQ_ZONE_B_TARGETS, _precompute_parity_eigenbasis,
    COMBINATOR_NAMES, ANTI_COMBINATOR_NAMES,
    N_COMBINATORS,
)


# ══════════════════════════════════════════════════════════════════════
# Crystal tools
# ══════════════════════════════════════════════════════════════════════

def get_crystal_eigenbasis() -> tuple[np.ndarray, np.ndarray]:
    data = _precompute_parity_eigenbasis(PCAQ_ZONE_B_TARGETS)
    return data["eigvecs"], data["eigvals"]


def project_to_crystal(tensor: np.ndarray, crystal_emb: np.ndarray) -> np.ndarray:
    """Project (..., d_model) tensor into crystal space → (..., 16)."""
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms
    return tensor @ crystal_norm.T


def project_to_eigenbasis(tensor: np.ndarray, crystal_emb: np.ndarray,
                          eigvecs: np.ndarray) -> np.ndarray:
    """Project (..., d_model) → (..., 16) in crystal eigenbasis (PC0=comp, PC1=sel, ...)."""
    crystal_proj = project_to_crystal(tensor, crystal_emb)
    return crystal_proj @ eigvecs


# ══════════════════════════════════════════════════════════════════════
# Data loading
# ══════════════════════════════════════════════════════════════════════

def load_examples(path: str, n: int = 20) -> list[dict]:
    import json
    examples = []
    with open(path) as f:
        for line in f:
            examples.append(json.loads(line))
            if len(examples) >= n:
                break
    return examples


def tokenize_example(example: dict, tokenizer) -> tuple[mx.array, mx.array]:
    """Tokenize a compile example into input_ids and targets."""
    text = example["input"] + "\n" + example["output"]
    tokens = tokenizer.encode(text)
    if len(tokens) > 128:
        tokens = tokens[:128]
    input_ids = mx.array([tokens[:-1]])
    targets = mx.array([tokens[1:]])
    return input_ids, targets


# ══════════════════════════════════════════════════════════════════════
# Core analysis: V crystal cascade
# ══════════════════════════════════════════════════════════════════════

def analyze_v_cascade(traces: list[dict], crystal_emb: np.ndarray,
                      eigvecs: np.ndarray, eigvals: np.ndarray) -> dict:
    """Analyze V through the full grating cascade.

    For each layer, measures how V is typed in crystal space, how
    attention's beta-reduction transforms the crystal signature, and
    how the FFN output feeds into the next layer's V.
    """
    n_layers = len(traces)
    results = {
        "per_layer": [],
        "cross_layer": [],
    }

    prev_ffn_eigen = None  # FFN output in eigenbasis from previous layer

    for layer_idx, trace in enumerate(traces):
        attn = trace["attn"]
        ffn = trace["ffn"]
        block = trace["block"]

        # ── V before attention reduction ──
        # V shape: (B, H, L, d_head) — need to reshape to (B, L, d_model)
        v_raw = np.array(attn["v"])  # (B, H, L, d_head)
        B, H, L, d_head = v_raw.shape
        d_model = H * d_head

        # Reconstruct full V by concatenating heads
        v_full = v_raw.transpose(0, 2, 1, 3).reshape(B, L, d_model)  # (B, L, d_model)

        # Project V into crystal eigenbasis
        v_eigen = project_to_eigenbasis(v_full[0], crystal_emb, eigvecs)  # (L, 16)

        # Per-head V crystal projection
        v_per_head = []
        for h in range(H):
            # Each head's V is in d_head space — we need the full d_model projection
            # Since V = x @ W_v then reshape, we project the per-head slice
            # But per-head is only d_head dims. For crystal projection we need d_model.
            # Instead, look at the contribution of each head to the output.
            pass  # We'll do this via attn_out decomposition below

        # ── V after attention reduction (attn_out) ──
        # attn_out = softmax(QK^T) @ V per head, shape (B, H, L, d_head)
        attn_out = np.array(attn["attn_out"])  # (B, H, L, d_head)
        attn_out_full = attn_out.transpose(0, 2, 1, 3).reshape(B, L, d_model)  # (B, L, d_model)

        # Note: the actual attention contribution to residual goes through o_proj
        # attn_contribution = o_proj(attn_out_full) — captured in block trace
        attn_contribution = np.array(block["attn_contribution"])  # (B, L, d_model)

        # Project attn_out (before o_proj) into eigenbasis
        attn_out_eigen = project_to_eigenbasis(attn_out_full[0], crystal_emb, eigvecs)

        # Project attn_contribution (after o_proj) into eigenbasis
        attn_contrib_eigen = project_to_eigenbasis(attn_contribution[0], crystal_emb, eigvecs)

        # ── FFN output ──
        ffn_out = np.array(block["ffn_contribution"])  # (B, L, d_model)
        ffn_eigen = project_to_eigenbasis(ffn_out[0], crystal_emb, eigvecs)  # (L, 16)

        # ── Residual after full layer ──
        residual_post = np.array(block["residual_post_ffn"])  # (B, L, d_model)
        residual_eigen = project_to_eigenbasis(residual_post[0], crystal_emb, eigvecs)

        # ══════════════════════════════════════════════════════════════
        # Measurements
        # ══════════════════════════════════════════════════════════════

        # 1. V combinator typing: which PCs dominate V at this layer?
        v_pc_energy = np.mean(v_eigen ** 2, axis=0)  # (16,) mean over positions
        v_pc_energy_norm = v_pc_energy / (v_pc_energy.sum() + 1e-8)

        # 2. Attention changes crystal signature
        #    Compare V (pre-reduction) vs attn_out (post-reduction)
        #    Do this position-by-position then average
        v_pc_profile = np.mean(np.abs(v_eigen), axis=0)  # (16,) mean |projection|
        attn_out_pc_profile = np.mean(np.abs(attn_out_eigen), axis=0)
        attn_contrib_pc_profile = np.mean(np.abs(attn_contrib_eigen), axis=0)

        # Crystal signature change: cosine between V profile and attn_out profile
        v_attn_cosine = (
            np.dot(v_pc_profile, attn_out_pc_profile)
            / (np.linalg.norm(v_pc_profile) * np.linalg.norm(attn_out_pc_profile) + 1e-8)
        )

        # 3. Dimensionality in crystal space
        #    Participation ratio of V in eigenbasis
        v_cov = np.cov(v_eigen.T)  # (16, 16) covariance over positions
        v_eigvals_cov = np.linalg.eigvalsh(v_cov)[::-1]
        v_eigvals_cov = np.maximum(v_eigvals_cov, 0)
        v_pr = (v_eigvals_cov.sum() ** 2) / (np.sum(v_eigvals_cov ** 2) + 1e-12)

        attn_out_cov = np.cov(attn_out_eigen.T)
        ao_eigvals = np.linalg.eigvalsh(attn_out_cov)[::-1]
        ao_eigvals = np.maximum(ao_eigvals, 0)
        attn_out_pr = (ao_eigvals.sum() ** 2) / (np.sum(ao_eigvals ** 2) + 1e-12)

        ffn_cov = np.cov(ffn_eigen.T)
        ffn_eigvals = np.linalg.eigvalsh(ffn_cov)[::-1]
        ffn_eigvals = np.maximum(ffn_eigvals, 0)
        ffn_pr = (ffn_eigvals.sum() ** 2) / (np.sum(ffn_eigvals ** 2) + 1e-12)

        residual_cov = np.cov(residual_eigen.T)
        res_eigvals = np.linalg.eigvalsh(residual_cov)[::-1]
        res_eigvals = np.maximum(res_eigvals, 0)
        residual_pr = (res_eigvals.sum() ** 2) / (np.sum(res_eigvals ** 2) + 1e-12)

        # 4. Off-diagonal energy in V's crystal projection
        #    How much of V's crystal-space energy is cross-PC coupling?
        v_outer = v_eigen.T @ v_eigen / L  # (16, 16) — mean outer product
        diag_energy = np.sum(np.diag(v_outer) ** 2)
        total_energy = np.sum(v_outer ** 2)
        off_diag_frac = 1.0 - diag_energy / (total_energy + 1e-12)

        attn_outer = attn_out_eigen.T @ attn_out_eigen / L
        attn_diag_e = np.sum(np.diag(attn_outer) ** 2)
        attn_total_e = np.sum(attn_outer ** 2)
        attn_off_diag = 1.0 - attn_diag_e / (attn_total_e + 1e-12)

        ffn_outer = ffn_eigen.T @ ffn_eigen / L
        ffn_diag_e = np.sum(np.diag(ffn_outer) ** 2)
        ffn_total_e = np.sum(ffn_outer ** 2)
        ffn_off_diag = 1.0 - ffn_diag_e / (ffn_total_e + 1e-12)

        # 5. Per-head attention: which heads shift crystal signature most?
        # attn_weights: (B, H, L, L) — the softmax pattern
        attn_weights = np.array(attn["attn_weights"])  # (B, H, L, L)
        head_analyses = []
        for h in range(H):
            # This head's attention-weighted V
            # attn_weights[0, h] is (L, L), v_raw[0, h] is (L, d_head)
            # head_out = attn_weights[0, h] @ v_raw[0, h]  → (L, d_head)
            # But d_head < d_model, so we can't project to crystal directly.
            # Instead measure: entropy of attention weights (how selective)
            w = attn_weights[0, h]  # (L, L)
            entropy = -np.sum(w * np.log(w + 1e-12), axis=-1).mean()
            # Attention concentration: max weight per query
            max_weight = np.max(w, axis=-1).mean()
            head_analyses.append({
                "head": h,
                "entropy": float(entropy),
                "max_weight": float(max_weight),
            })

        # ── Per-head attn output in crystal eigenbasis ──
        # attn_out is (B, H, L, d_head). We need full d_model for crystal proj.
        # Use: the residual after attention = x_in + o_proj(concat_heads(attn_out))
        # We can examine each head's contribution by zeroing others:
        per_head_crystal = []
        for h in range(H):
            # head h contribution: (L, d_head) occupying dims [h*d_head : (h+1)*d_head]
            # in the concatenated (L, d_model) before o_proj
            head_in_full = np.zeros((L, d_model))
            head_in_full[:, h * d_head:(h + 1) * d_head] = attn_out[0, h]
            # This is what this head contributes to the input of o_proj
            # We can't apply o_proj here without the weights, but we CAN
            # look at the attn_out per head directly in model space
            # Actually — the concat before o_proj IS in d_model space
            head_eigen = project_to_eigenbasis(head_in_full, crystal_emb, eigvecs)
            head_pc_energy = np.mean(head_eigen ** 2, axis=0)
            dominant_pc = int(np.argmax(head_pc_energy[:8]))  # top 8 PCs only
            per_head_crystal.append({
                "head": h,
                "dominant_pc": dominant_pc,
                "dominant_pc_name": COMBINATOR_NAMES[dominant_pc] if dominant_pc < 8 else f"PC{dominant_pc}",
                "pc_energy": head_pc_energy[:8].tolist(),
                "pc_energy_norm": (head_pc_energy[:8] / (head_pc_energy[:8].sum() + 1e-8)).tolist(),
            })

        # ── Cross-layer correlation (FFN output at N → V at N+1) ──
        cross_layer_corr = None
        if prev_ffn_eigen is not None:
            # Correlate FFN output profile from previous layer with V profile at this layer
            # Use position-averaged magnitude profiles
            prev_ffn_profile = np.mean(np.abs(prev_ffn_eigen), axis=0)  # (16,)
            curr_v_profile = np.mean(np.abs(v_eigen), axis=0)  # (16,)
            cross_layer_corr = float(
                np.dot(prev_ffn_profile, curr_v_profile)
                / (np.linalg.norm(prev_ffn_profile) * np.linalg.norm(curr_v_profile) + 1e-8)
            )

            # Also: position-by-position correlation
            # For each position, correlate FFN output eigen profile with V eigen profile
            pos_corrs = []
            for pos in range(min(L, prev_ffn_eigen.shape[0])):
                c = np.corrcoef(prev_ffn_eigen[pos], v_eigen[pos])[0, 1]
                if not np.isnan(c):
                    pos_corrs.append(c)
            cross_layer_pos_mean = float(np.mean(pos_corrs)) if pos_corrs else 0.0
            cross_layer_pos_std = float(np.std(pos_corrs)) if pos_corrs else 0.0
        else:
            cross_layer_pos_mean = None
            cross_layer_pos_std = None

        # ── Store FFN eigen for next layer ──
        prev_ffn_eigen = ffn_eigen.copy()

        # ── Compile layer results ──
        layer_result = {
            "layer": layer_idx,
            # V crystal typing
            "v_pc_energy": v_pc_energy_norm[:8].tolist(),
            "v_dominant_pc": int(np.argmax(v_pc_energy[:8])),
            "v_dominant_pc_name": COMBINATOR_NAMES[int(np.argmax(v_pc_energy[:8]))],
            # Attention transforms crystal
            "v_attn_cosine": float(v_attn_cosine),
            "v_profile_top8": v_pc_profile[:8].tolist(),
            "attn_out_profile_top8": attn_out_pc_profile[:8].tolist(),
            "attn_contrib_profile_top8": attn_contrib_pc_profile[:8].tolist(),
            # Dimensionality
            "v_participation_ratio": float(v_pr),
            "attn_out_participation_ratio": float(attn_out_pr),
            "ffn_participation_ratio": float(ffn_pr),
            "residual_participation_ratio": float(residual_pr),
            # Off-diagonal (cross-PC coupling)
            "v_off_diag_frac": float(off_diag_frac),
            "attn_off_diag_frac": float(attn_off_diag),
            "ffn_off_diag_frac": float(ffn_off_diag),
            # Per-head
            "heads": head_analyses,
            "heads_crystal": per_head_crystal,
            # Cross-layer (FFN[N-1] → V[N])
            "ffn_to_v_cross_layer_cosine": cross_layer_corr,
            "ffn_to_v_pos_corr_mean": cross_layer_pos_mean,
            "ffn_to_v_pos_corr_std": cross_layer_pos_std,
            # FFN crystal profile
            "ffn_pc_profile_top8": np.mean(np.abs(ffn_eigen), axis=0)[:8].tolist(),
        }

        results["per_layer"].append(layer_result)

    return results


# ══════════════════════════════════════════════════════════════════════
# Compound grating analysis
# ══════════════════════════════════════════════════════════════════════

def analyze_compound_grating(model: MicroModel, crystal_emb: np.ndarray,
                              eigvecs: np.ndarray) -> dict:
    """Analyze the composition of FFN gratings through depth.

    Each FFN has an overlay matrix (16×16 in eigenbasis) showing how
    crystal-input maps to crystal-output. Composing these overlay
    matrices shows the cumulative grating effect.

    The 80-91% off-diagonal energy means each grating projects between
    PCs. Composing gratings should show progressive collapse toward
    the comp↔sel eigenplane.
    """
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms

    overlay_matrices = []
    composed = np.eye(16)  # start with identity
    composed_chain = [composed.copy()]

    for layer_idx, block in enumerate(model.blocks):
        ffn = block.ffn

        gate_w = np.array(ffn.gate_proj.weight)   # (d_ff, d_model)
        key_w = np.array(ffn.key_proj.weight)      # (d_ff, d_model)
        value_w = np.array(ffn.value_proj.weight)   # (d_model, d_ff)

        # Project into crystal eigenbasis
        gate_crystal = gate_w @ crystal_norm.T  # (d_ff, 16)
        gate_eigen = gate_crystal @ eigvecs     # (d_ff, 16)
        value_crystal = crystal_norm @ value_w  # (16, d_ff)
        value_eigen = eigvecs.T @ value_crystal # (16, d_ff)

        # Overlay: how crystal input → crystal output through this FFN
        overlay = gate_eigen.T @ value_eigen.T  # (16, 16)
        overlay_matrices.append(overlay)

        # Normalize overlay for composition (otherwise magnitudes explode)
        # Use: overlay / frobenius_norm to see structure, not magnitude
        overlay_normed = overlay / (np.linalg.norm(overlay, 'fro') + 1e-8)

        # Compose: cumulative grating effect
        composed = overlay_normed @ composed
        composed_chain.append(composed.copy())

    # Analyze the composed gratings
    results = {"per_layer_overlay": [], "composed_chain": []}

    for i, overlay in enumerate(overlay_matrices):
        diag = np.diag(overlay)
        off_diag = overlay - np.diag(diag)
        diag_energy = np.sum(diag ** 2)
        off_diag_energy = np.sum(off_diag ** 2)
        total = diag_energy + off_diag_energy

        # Top cross-PC couplings
        off_diag_abs = np.abs(off_diag)
        np.fill_diagonal(off_diag_abs, 0)
        top_couplings = []
        for _ in range(5):
            idx = np.unravel_index(np.argmax(off_diag_abs), off_diag_abs.shape)
            val = float(off_diag[idx])
            top_couplings.append({
                "from_pc": int(idx[0]),
                "to_pc": int(idx[1]),
                "value": val,
                "from_name": COMBINATOR_NAMES[idx[0]] if idx[0] < 8 else f"āPC{idx[0]-8}",
                "to_name": COMBINATOR_NAMES[idx[1]] if idx[1] < 8 else f"āPC{idx[1]-8}",
            })
            off_diag_abs[idx] = 0

        results["per_layer_overlay"].append({
            "layer": i,
            "diag_top8": diag[:8].tolist(),
            "diag_energy_frac": float(diag_energy / (total + 1e-8)),
            "off_diag_energy_frac": float(off_diag_energy / (total + 1e-8)),
            "top_cross_couplings": top_couplings,
            "alternation_sign_pc0": "+" if diag[0] > 0 else "-",
            "alternation_sign_pc1": "+" if diag[1] > 0 else "-",
        })

    # Composed grating analysis
    for i, comp in enumerate(composed_chain):
        # SVD of composed grating — how many effective dimensions?
        u, s, vh = np.linalg.svd(comp)
        s_norm = s / (s.sum() + 1e-8)
        pr = (s.sum() ** 2) / (np.sum(s ** 2) + 1e-12)

        # Which PCs dominate the composed grating?
        diag = np.diag(comp)

        results["composed_chain"].append({
            "after_layer": i - 1,  # -1 = identity (before any grating)
            "singular_values_top4": s[:4].tolist(),
            "sv_concentration": s_norm[:4].tolist(),
            "participation_ratio": float(pr),
            "diag_top8": diag[:8].tolist(),
        })

    return results


# ══════════════════════════════════════════════════════════════════════
# Attention beta-reduction decomposition
# ══════════════════════════════════════════════════════════════════════

def analyze_attention_reduction(traces: list[dict], crystal_emb: np.ndarray,
                                 eigvecs: np.ndarray) -> dict:
    """Decompose attention's beta-reduction in crystal eigenbasis.

    For each layer: the attention weights softmax(QK^T) are the
    combinator application pattern. We can ask:
    - What is the effective dimensionality of the reduction?
    - Does the reduction preserve, amplify, or suppress each PC?
    - Is the reduction typed (different PCs for different heads)?
    """
    results = {"per_layer": []}

    for layer_idx, trace in enumerate(traces):
        attn = trace["attn"]
        attn_weights = np.array(attn["attn_weights"])  # (B, H, L, L)
        v_raw = np.array(attn["v"])  # (B, H, L, d_head)
        attn_out = np.array(attn["attn_out"])  # (B, H, L, d_head)

        B, H, L, d_head = v_raw.shape
        d_model = H * d_head

        # Reconstruct V in d_model space
        v_full = v_raw.transpose(0, 2, 1, 3).reshape(B, L, d_model)[0]  # (L, d_model)
        attn_out_full = attn_out.transpose(0, 2, 1, 3).reshape(B, L, d_model)[0]

        # V in eigenbasis
        v_eigen = project_to_eigenbasis(v_full, crystal_emb, eigvecs)  # (L, 16)
        ao_eigen = project_to_eigenbasis(attn_out_full, crystal_emb, eigvecs)

        # PC-by-PC: does attention amplify or suppress each PC?
        v_pc_power = np.mean(v_eigen ** 2, axis=0)  # (16,)
        ao_pc_power = np.mean(ao_eigen ** 2, axis=0)

        # Gain per PC: attn_out / V (how much each PC is amplified)
        pc_gain = ao_pc_power / (v_pc_power + 1e-12)

        # Effective rank of the attention reduction
        # For each head, SVD of the attention weight matrix
        head_ranks = []
        for h in range(H):
            w = attn_weights[0, h]  # (L, L) — a stochastic matrix (rows sum to 1)
            u, s, vh = np.linalg.svd(w)
            s_norm = s / (s.sum() + 1e-8)
            pr = (s.sum() ** 2) / (np.sum(s ** 2) + 1e-12)
            head_ranks.append({
                "head": h,
                "participation_ratio": float(pr),
                "top_sv_frac": float(s_norm[0]),
                "top3_sv_frac": float(s_norm[:3].sum()),
            })

        results["per_layer"].append({
            "layer": layer_idx,
            "pc_gain_top8": pc_gain[:8].tolist(),
            "gain_comp_sel_ratio": float(pc_gain[0] / (pc_gain[1] + 1e-12)),
            "head_ranks": head_ranks,
        })

    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    checkpoint_dir = sys.argv[1] if len(sys.argv) > 1 else "checkpoints/micro/final"
    checkpoint_path = Path(checkpoint_dir)
    if not checkpoint_path.exists():
        # Try relative from script location
        checkpoint_path = Path(__file__).parent.parent.parent / checkpoint_dir
    assert checkpoint_path.exists(), f"Checkpoint not found: {checkpoint_path}"

    results_dir = Path(__file__).parent.parent.parent / "results" / "v-crystal-cascade"
    results_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("V-Crystal Cascade Probe — Grating-through-grating interference")
    print("=" * 70)

    # ── Load model ──
    print(f"\nLoading model from {checkpoint_path}...")
    cfg = MicroConfig()
    model = MicroModel(cfg)
    weights = mx.load(str(checkpoint_path / "model.npz"))
    # Convert flat keys to nested structure
    nested = {}
    for k, v in weights.items():
        parts = k.split(".")
        d = nested
        for p in parts[:-1]:
            if p not in d:
                d[p] = {}
            d = d[p]
        d[parts[-1]] = v
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())
    print("  Model loaded ✓")

    # ── Crystal setup ──
    crystal_emb = np.array(model.get_all_crystal_embeddings())
    eigvecs, eigvals = get_crystal_eigenbasis()
    print(f"  Crystal eigenbasis: {eigvals[:4]} (top 4 eigenvalues)")

    # ── Crystal health check ──
    diag = model.crystal_diagnostics()
    print(f"  Crystal loss: {diag['crystal_loss']:.6f}")

    # ── Load tokenizer ──
    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B", trust_remote_code=True)
        print("  Tokenizer loaded ✓")
    except Exception as e:
        print(f"  Tokenizer failed: {e}")
        print("  Using simple tokenization fallback")
        tokenizer = None

    # ── Load examples ──
    data_path = Path(__file__).parent.parent.parent / "data" / "compile-eval.jsonl"
    if not data_path.exists():
        data_path = Path(__file__).parent.parent.parent / "data" / "compile-test.jsonl"
    examples = load_examples(str(data_path), n=20)
    print(f"  Loaded {len(examples)} examples")

    # ── Run probes across examples ──
    all_v_cascades = []
    all_compound = None
    all_reductions = []

    for ex_idx, example in enumerate(examples):
        if tokenizer is not None:
            input_ids, targets = tokenize_example(example, tokenizer)
        else:
            # Simple fallback
            text = example["input"] + "\n" + example["output"]
            tokens = [ord(c) % 1000 for c in text]
            input_ids = mx.array([tokens[:-1]])
            targets = mx.array([tokens[1:]])

        # Forward with traces
        model.set_capture(True)
        logits, loss = model(input_ids, targets)
        mx.eval(logits, loss)
        traces = model.get_traces()
        # Force eval all traces
        for t in traces:
            for section in ["block", "attn", "ffn"]:
                for k, v in t[section].items():
                    if isinstance(v, mx.array):
                        mx.eval(v)
        model.set_capture(False)

        # V cascade analysis
        v_cascade = analyze_v_cascade(traces, crystal_emb, eigvecs, eigvals)
        all_v_cascades.append(v_cascade)

        # Attention reduction analysis
        reduction = analyze_attention_reduction(traces, crystal_emb, eigvecs)
        all_reductions.append(reduction)

        if ex_idx == 0:
            print(f"\n  Example 0: '{example['input'][:50]}...'")
            print(f"  Loss: {float(loss.item()):.4f}")

    # Compound grating (model weights, not per-example)
    compound = analyze_compound_grating(model, crystal_emb, eigvecs)

    # ══════════════════════════════════════════════════════════════════
    # Aggregate across examples
    # ══════════════════════════════════════════════════════════════════

    n_examples = len(all_v_cascades)
    n_layers = len(all_v_cascades[0]["per_layer"])

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    # ── 1. V Combinator Typing Per Layer ──
    print("\n1. V COMBINATOR TYPING (mean over examples)")
    print("   Which crystal PCs dominate V at each layer?")
    print(f"   {'Layer':>5} | {'K':>6} {'I':>6} {'B':>6} {'C':>6} {'D':>6} {'Y':>6} {'W':>6} {'WHNF':>6} | Dominant")
    print("   " + "-" * 75)
    for layer in range(n_layers):
        energies = np.mean([vc["per_layer"][layer]["v_pc_energy"] for vc in all_v_cascades], axis=0)
        dom = COMBINATOR_NAMES[int(np.argmax(energies))]
        print(f"   L{layer:>3} | {energies[0]:6.3f} {energies[1]:6.3f} {energies[2]:6.3f} "
              f"{energies[3]:6.3f} {energies[4]:6.3f} {energies[5]:6.3f} "
              f"{energies[6]:6.3f} {energies[7]:6.3f} | {dom}")

    # ── 2. Attention Transforms Crystal ──
    print("\n2. ATTENTION TRANSFORMS CRYSTAL SIGNATURE")
    print("   Cosine(V_profile, attn_out_profile) — how much does reduction change typing?")
    for layer in range(n_layers):
        cosines = [vc["per_layer"][layer]["v_attn_cosine"] for vc in all_v_cascades]
        print(f"   L{layer}: cos = {np.mean(cosines):.4f} ± {np.std(cosines):.4f}"
              f"  (1.0 = no change, <1.0 = crystal signature shifted)")

    # ── 3. Cross-Layer Steering: FFN[N] → V[N+1] ──
    print("\n3. CROSS-LAYER GRATING STEERING: FFN[N] → V[N+1]")
    print("   Does FFN output at layer N predict V crystal profile at layer N+1?")
    for layer in range(n_layers):
        corrs = [vc["per_layer"][layer]["ffn_to_v_cross_layer_cosine"]
                 for vc in all_v_cascades
                 if vc["per_layer"][layer]["ffn_to_v_cross_layer_cosine"] is not None]
        if corrs:
            pos_corrs = [vc["per_layer"][layer]["ffn_to_v_pos_corr_mean"]
                        for vc in all_v_cascades
                        if vc["per_layer"][layer]["ffn_to_v_pos_corr_mean"] is not None]
            print(f"   FFN[{layer-1}]→V[{layer}]: profile_cos = {np.mean(corrs):.4f} ± {np.std(corrs):.4f}"
                  f"  |  pos_corr = {np.mean(pos_corrs):.4f} ± {np.std(pos_corrs):.4f}")
        else:
            print(f"   L{layer}: (first layer — no prior FFN)")

    # ── 4. Progressive Dimensionality ──
    print("\n4. PROGRESSIVE DIMENSIONALITY (Participation Ratio in crystal eigenbasis)")
    print(f"   {'Layer':>5} | {'V_PR':>8} {'AttnOut_PR':>10} {'FFN_PR':>8} {'Residual_PR':>11}")
    print("   " + "-" * 55)
    for layer in range(n_layers):
        v_prs = [vc["per_layer"][layer]["v_participation_ratio"] for vc in all_v_cascades]
        ao_prs = [vc["per_layer"][layer]["attn_out_participation_ratio"] for vc in all_v_cascades]
        ffn_prs = [vc["per_layer"][layer]["ffn_participation_ratio"] for vc in all_v_cascades]
        res_prs = [vc["per_layer"][layer]["residual_participation_ratio"] for vc in all_v_cascades]
        print(f"   L{layer:>3} | {np.mean(v_prs):8.2f} {np.mean(ao_prs):10.2f} "
              f"{np.mean(ffn_prs):8.2f} {np.mean(res_prs):11.2f}")

    # ── 5. Off-Diagonal Energy ──
    print("\n5. OFF-DIAGONAL ENERGY (cross-PC coupling fraction)")
    print(f"   {'Layer':>5} | {'V':>8} {'AttnOut':>8} {'FFN':>8}")
    print("   " + "-" * 40)
    for layer in range(n_layers):
        v_od = [vc["per_layer"][layer]["v_off_diag_frac"] for vc in all_v_cascades]
        ao_od = [vc["per_layer"][layer]["attn_off_diag_frac"] for vc in all_v_cascades]
        ffn_od = [vc["per_layer"][layer]["ffn_off_diag_frac"] for vc in all_v_cascades]
        print(f"   L{layer:>3} | {np.mean(v_od):8.3f} {np.mean(ao_od):8.3f} {np.mean(ffn_od):8.3f}")

    # ── 6. Per-Head Crystal Typing ──
    print("\n6. PER-HEAD CRYSTAL TYPING")
    for layer in range(n_layers):
        print(f"   Layer {layer}:")
        for h in range(cfg.n_heads):
            # Aggregate dominant PC across examples
            dom_pcs = [vc["per_layer"][layer]["heads_crystal"][h]["dominant_pc_name"]
                      for vc in all_v_cascades]
            # Most common dominant
            from collections import Counter
            counts = Counter(dom_pcs)
            most_common = counts.most_common(1)[0]
            # Mean energy per PC
            energies = np.mean(
                [vc["per_layer"][layer]["heads_crystal"][h]["pc_energy_norm"]
                 for vc in all_v_cascades], axis=0)
            top2 = np.argsort(energies)[-2:][::-1]
            print(f"     H{h}: dominant={most_common[0]}({most_common[1]}/{n_examples}) "
                  f" top2=[{COMBINATOR_NAMES[top2[0]]}:{energies[top2[0]]:.3f}, "
                  f"{COMBINATOR_NAMES[top2[1]]}:{energies[top2[1]]:.3f}]")

    # ── 7. Attention Reduction Gain ──
    print("\n7. ATTENTION BETA-REDUCTION: PC GAIN (attn_out_power / V_power)")
    print("   >1 = amplified, <1 = suppressed by the reduction")
    print(f"   {'Layer':>5} | {'K':>6} {'I':>6} {'B':>6} {'C':>6} {'D':>6} {'Y':>6} {'W':>6} {'WHNF':>6} | comp/sel")
    print("   " + "-" * 80)
    for layer in range(n_layers):
        gains = np.mean([r["per_layer"][layer]["pc_gain_top8"] for r in all_reductions], axis=0)
        ratio = np.mean([r["per_layer"][layer]["gain_comp_sel_ratio"] for r in all_reductions])
        print(f"   L{layer:>3} | {gains[0]:6.2f} {gains[1]:6.2f} {gains[2]:6.2f} "
              f"{gains[3]:6.2f} {gains[4]:6.2f} {gains[5]:6.2f} "
              f"{gains[6]:6.2f} {gains[7]:6.2f} | {ratio:.3f}")

    # ── 8. Compound Grating ──
    print("\n8. COMPOUND GRATING (FFN weight overlay composition)")
    print("   Per-layer overlay diagonal (alternation pattern):")
    for ov in compound["per_layer_overlay"]:
        d = ov["diag_top8"]
        print(f"   L{ov['layer']}: [{d[0]:+.3f} {d[1]:+.3f} {d[2]:+.3f} {d[3]:+.3f} "
              f"{d[4]:+.3f} {d[5]:+.3f} {d[6]:+.3f} {d[7]:+.3f}]"
              f"  diag={ov['diag_energy_frac']:.1%} off={ov['off_diag_energy_frac']:.1%}")

    print("\n   Top cross-PC couplings per layer (the projections between PCs):")
    for ov in compound["per_layer_overlay"]:
        top = ov["top_cross_couplings"][:3]
        couplings_str = ", ".join(
            f"{c['from_name']}→{c['to_name']}={c['value']:+.3f}" for c in top)
        print(f"   L{ov['layer']}: {couplings_str}")

    print("\n   Composed grating dimensionality (progressive moiré collapse):")
    print(f"   {'After':>8} | {'PR':>6} | {'SV top4':>35} | {'Diag top4':>25}")
    print("   " + "-" * 85)
    for cc in compound["composed_chain"]:
        sv = cc["singular_values_top4"]
        diag = cc["diag_top8"][:4]
        after = "init" if cc["after_layer"] == -1 else f"L{cc['after_layer']}"
        print(f"   {after:>8} | {cc['participation_ratio']:6.2f} | "
              f"[{sv[0]:.3f} {sv[1]:.3f} {sv[2]:.3f} {sv[3]:.3f}] | "
              f"[{diag[0]:+.3f} {diag[1]:+.3f} {diag[2]:+.3f} {diag[3]:+.3f}]")

    # ── 9. Attention Head Selectivity ──
    print("\n9. ATTENTION HEAD SELECTIVITY (entropy / max_weight)")
    for layer in range(n_layers):
        for h in range(cfg.n_heads):
            entropies = [vc["per_layer"][layer]["heads"][h]["entropy"] for vc in all_v_cascades]
            max_ws = [vc["per_layer"][layer]["heads"][h]["max_weight"] for vc in all_v_cascades]
            print(f"   L{layer} H{h}: entropy={np.mean(entropies):.3f} "
                  f"max_weight={np.mean(max_ws):.3f}")

    # ── Save ──
    summary = {
        "config": {"n_layers": n_layers, "n_heads": cfg.n_heads, "d_model": cfg.d_model,
                    "n_examples": n_examples},
        "compound_grating": compound,
        # Store aggregated per-layer numbers
        "aggregated": {}
    }

    # Aggregate key metrics
    for layer in range(n_layers):
        key = f"layer_{layer}"
        summary["aggregated"][key] = {
            "v_pc_energy": np.mean([vc["per_layer"][layer]["v_pc_energy"]
                                    for vc in all_v_cascades], axis=0).tolist(),
            "v_attn_cosine": float(np.mean([vc["per_layer"][layer]["v_attn_cosine"]
                                            for vc in all_v_cascades])),
            "v_pr": float(np.mean([vc["per_layer"][layer]["v_participation_ratio"]
                                   for vc in all_v_cascades])),
            "ffn_pr": float(np.mean([vc["per_layer"][layer]["ffn_participation_ratio"]
                                     for vc in all_v_cascades])),
            "residual_pr": float(np.mean([vc["per_layer"][layer]["residual_participation_ratio"]
                                          for vc in all_v_cascades])),
            "v_off_diag": float(np.mean([vc["per_layer"][layer]["v_off_diag_frac"]
                                         for vc in all_v_cascades])),
            "ffn_off_diag": float(np.mean([vc["per_layer"][layer]["ffn_off_diag_frac"]
                                           for vc in all_v_cascades])),
            "pc_gain": np.mean([r["per_layer"][layer]["pc_gain_top8"]
                                for r in all_reductions], axis=0).tolist(),
        }
        # Cross-layer
        corrs = [vc["per_layer"][layer]["ffn_to_v_cross_layer_cosine"]
                 for vc in all_v_cascades
                 if vc["per_layer"][layer]["ffn_to_v_cross_layer_cosine"] is not None]
        if corrs:
            summary["aggregated"][key]["ffn_to_v_cosine"] = float(np.mean(corrs))

    out_path = results_dir / "summary.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
