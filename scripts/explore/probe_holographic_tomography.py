#!/usr/bin/env python3
"""Holographic Tomography — Cross-model intersection reveals universal holograms.

If LLMs work like piling photographs until intersections in the projection form
inference patterns, then two independently trained models that converge on the
SAME pattern have found something REAL — not a model-specific artifact.

This probe implements holographic tomography:
  1. Run identical factual probes on multiple models
  2. Capture hidden states (the projected beam at each layer)
  3. Compare RELATIONAL structure (RSA) — model-agnostic
  4. Compare DIRECT hidden states where d_model matches
  5. Compare SIGN patterns at responsive plate regions
  6. Report: what fraction is universal (signal) vs model-specific (noise)?

Models:
  - Qwen3-14B:    d_model=5120, 40 layers, GQA (8 KV heads), Apache-2.0
  - OLMo-2-13B:   d_model=5120, 40 layers, MHA (40 KV heads), Apache-2.0
  Both share d_model=5120 → hidden states live in the SAME dimensionality space
  Different architectures, different training data, different random seeds
  Agreement between them = universal structure

The key insight: cross-model agreement provides DENOISING.
  - Single model: can't distinguish universal structure from training artifact
  - Two models agreeing: probability of coincidental agreement = very low
  - N models agreeing: SNR improves as √N

Usage:
    uv run python scripts/explore/probe_holographic_tomography.py
    uv run python scripts/explore/probe_holographic_tomography.py --layers 0,10,20,30
    uv run python scripts/explore/probe_holographic_tomography.py --quick

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path
from collections import defaultdict

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

OUTPUT_DIR = Path("results/holographic-extraction")

# ══════════════════════════════════════════════════════════════════
# Model registry — models we can probe
# ══════════════════════════════════════════════════════════════════

MODELS = {
    "qwen3-14b": {
        "name": "Qwen/Qwen3-14B",
        "d_model": 5120,
        "n_layers": 40,
        "n_heads": 40,
        "n_kv_heads": 8,
        "layer_accessor": "model.layers",
        "attn_accessor": "self_attn",
        "q_proj": "q_proj",
        "k_proj": "k_proj",
        "v_proj": "v_proj",
        "ffn_gate": "mlp.gate_proj",
        "ffn_up": "mlp.up_proj",
    },
    "olmo-2-13b": {
        "name": "allenai/OLMo-2-1124-13B",
        "d_model": 5120,
        "n_layers": 40,
        "n_heads": 40,
        "n_kv_heads": 40,
        "layer_accessor": "model.layers",
        "attn_accessor": "self_attn",
        "q_proj": "q_proj",
        "k_proj": "k_proj",
        "v_proj": "v_proj",
        "ffn_gate": "mlp.gate_proj",
        "ffn_up": "mlp.up_proj",
    },
}

# ══════════════════════════════════════════════════════════════════
# Factual probes
# ══════════════════════════════════════════════════════════════════

FACTUAL_PROBES = {
    "geography": [
        {"prompt": "The capital of France is", "answer": " Paris"},
        {"prompt": "The capital of Japan is", "answer": " Tokyo"},
        {"prompt": "The capital of Germany is", "answer": " Berlin"},
        {"prompt": "The capital of Italy is", "answer": " Rome"},
        {"prompt": "The capital of Spain is", "answer": " Madrid"},
        {"prompt": "The capital of Russia is", "answer": " Moscow"},
        {"prompt": "The capital of China is", "answer": " Beijing"},
        {"prompt": "The capital of Australia is", "answer": " Canberra"},
        {"prompt": "The largest ocean is the", "answer": " Pacific"},
        {"prompt": "The longest river in the world is the", "answer": " Nile"},
        {"prompt": "The highest mountain in the world is Mount", "answer": " Everest"},
        {"prompt": "The largest continent is", "answer": " Asia"},
    ],
    "science": [
        {"prompt": "Water freezes at zero degrees", "answer": " Celsius"},
        {"prompt": "The speed of light is approximately 300,000 kilometers per", "answer": " second"},
        {"prompt": "The chemical symbol for gold is", "answer": " Au"},
        {"prompt": "DNA stands for deoxyribonucleic", "answer": " acid"},
        {"prompt": "The closest star to Earth is the", "answer": " Sun"},
        {"prompt": "Gravity was described by Isaac", "answer": " Newton"},
        {"prompt": "The theory of relativity was developed by Albert", "answer": " Einstein"},
        {"prompt": "Photosynthesis converts sunlight into", "answer": " energy"},
        {"prompt": "The chemical formula for table salt is Na", "answer": "Cl"},
        {"prompt": "Electrons carry a negative electric", "answer": " charge"},
    ],
    "culture": [
        {"prompt": "Shakespeare wrote Romeo and", "answer": " Juliet"},
        {"prompt": "The Mona Lisa was painted by Leonardo da", "answer": " Vinci"},
        {"prompt": "The Great Wall is located in", "answer": " China"},
        {"prompt": "The Eiffel Tower is in", "answer": " Paris"},
        {"prompt": "The Colosseum is in", "answer": " Rome"},
        {"prompt": "Beethoven composed the Moonlight", "answer": " Son"},
        {"prompt": "The Sistine Chapel was painted by", "answer": " Michel"},
        {"prompt": "The Odyssey was written by", "answer": " Homer"},
    ],
    "math": [
        {"prompt": "Two plus two equals", "answer": " four"},
        {"prompt": "The square root of 144 is", "answer": " 12"},
        {"prompt": "Pi is approximately 3.14", "answer": "15"},
        {"prompt": "A triangle has three", "answer": " sides"},
        {"prompt": "A hexagon has six", "answer": " sides"},
        {"prompt": "The derivative of x squared is", "answer": " 2"},
        {"prompt": "Ten multiplied by ten equals", "answer": " one"},
        {"prompt": "A right angle measures exactly", "answer": " 90"},
    ],
    "common": [
        {"prompt": "The Earth orbits the", "answer": " Sun"},
        {"prompt": "There are 24 hours in a", "answer": " day"},
        {"prompt": "There are 365 days in a", "answer": " year"},
        {"prompt": "The human body has 206", "answer": " bones"},
        {"prompt": "Oxygen is essential for", "answer": " breathing"},
        {"prompt": "The color of the sky is typically", "answer": " blue"},
        {"prompt": "Ice is the solid form of", "answer": " water"},
        {"prompt": "The opposite of hot is", "answer": " cold"},
    ],
}


def flatten_probes() -> list[dict]:
    flat = []
    for category, probes in FACTUAL_PROBES.items():
        for probe in probes:
            flat.append({**probe, "category": category})
    return flat


# ══════════════════════════════════════════════════════════════════
# Hidden state extraction — capture residual stream per model
# ══════════════════════════════════════════════════════════════════


def extract_hidden_states(
    model_key: str,
    target_layers: list[int],
    probes: list[dict],
    device: str,
) -> dict:
    """Extract hidden states and K signs from a model for all factual probes.

    Returns:
        {
            "hidden_states": {layer_idx: ndarray(n_probes, d_model)},
            "k_signs": {layer_idx: ndarray(kv_dim, d_model)},
            "predictions": [{"log_prob": float, "rank": int, "correct": bool}],
            "model_key": str,
        }
    """
    model_info = MODELS[model_key]
    model_name = model_info["name"]

    print(f"  Loading {model_key} ({model_name})...", file=sys.stderr)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device,
    )
    model.eval()

    # Access layers
    layers = model.model.layers

    # ── Capture hidden states via hooks ──
    hidden_captures = {li: [] for li in target_layers}

    hooks = []
    for li in target_layers:
        layer = layers[li]

        def make_hook(layer_idx):
            def hook_fn(module, input, output):
                # Residual stream AFTER this layer (output[0] for most architectures)
                if isinstance(output, tuple):
                    h = output[0]
                else:
                    h = output
                # Last position hidden state
                hidden_captures[layer_idx].append(h[:, -1, :].detach().cpu().float())
            return hook_fn

        h = layer.register_forward_hook(make_hook(li))
        hooks.append(h)

    # ── Run probes ──
    predictions = []
    print(f"  Running {len(probes)} probes...", file=sys.stderr)

    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        answer_ids = tokenizer.encode(probe["answer"], add_special_tokens=False)
        target_id = answer_ids[0] if answer_ids else 0

        with torch.no_grad():
            outputs = model(input_ids)
            logits = outputs.logits[0, -1, :]
            log_probs = F.log_softmax(logits, dim=-1)
            lp = log_probs[target_id].item()
            rank = (torch.argsort(logits, descending=True) == target_id).nonzero()[0].item() + 1
            top1 = torch.argmax(logits).item()

        predictions.append({
            "log_prob": lp,
            "rank": rank,
            "correct": (top1 == target_id),
        })

    # Remove hooks
    for h in hooks:
        h.remove()

    # ── Extract K signs at target layers ──
    print(f"  Extracting K signs at layers {target_layers}...", file=sys.stderr)
    k_signs = {}
    for li in target_layers:
        layer = layers[li]
        attn = getattr(layer, model_info["attn_accessor"])
        k_weight = getattr(attn, model_info["k_proj"]).weight.float()
        k_signs[li] = torch.sign(k_weight).to(torch.int8).cpu().numpy()

    # ── Stack hidden states ──
    hidden_states = {}
    for li in target_layers:
        hidden_states[li] = torch.cat(hidden_captures[li], dim=0).numpy()  # (n_probes, d_model)

    # Free model
    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    return {
        "hidden_states": hidden_states,
        "k_signs": k_signs,
        "predictions": predictions,
        "model_key": model_key,
        "d_model": model_info["d_model"],
        "n_kv_heads": model_info["n_kv_heads"],
    }


# ══════════════════════════════════════════════════════════════════
# Analysis 1: Representational Similarity Analysis (RSA)
# ══════════════════════════════════════════════════════════════════


def compute_rsa(
    data_a: dict,
    data_b: dict,
    target_layers: list[int],
) -> dict:
    """Compare representational geometry across two models.

    RSA: Build fact×fact similarity matrices per model, compare them.
    If both models organize facts similarly (geography clusters, science clusters),
    the second-order correlation (RSA score) will be high.

    This is MODEL-AGNOSTIC — works regardless of d_model differences.
    """
    results = {"layers": []}

    for li in target_layers:
        hs_a = data_a["hidden_states"][li]  # (n_probes, d_model_a)
        hs_b = data_b["hidden_states"][li]  # (n_probes, d_model_b)

        # Normalize for cosine similarity
        hs_a_norm = hs_a / np.maximum(np.linalg.norm(hs_a, axis=1, keepdims=True), 1e-8)
        hs_b_norm = hs_b / np.maximum(np.linalg.norm(hs_b, axis=1, keepdims=True), 1e-8)

        # Fact × fact similarity matrices (RDMs — representational dissimilarity matrices)
        rdm_a = hs_a_norm @ hs_a_norm.T  # (n_probes, n_probes) cosine sim
        rdm_b = hs_b_norm @ hs_b_norm.T

        # Extract upper triangle (excluding diagonal)
        n = rdm_a.shape[0]
        triu_idx = np.triu_indices(n, k=1)
        flat_a = rdm_a[triu_idx]
        flat_b = rdm_b[triu_idx]

        # Second-order correlation (RSA score)
        pearson_r = np.corrcoef(flat_a, flat_b)[0, 1]

        # Spearman rank correlation (more robust)
        from scipy.stats import spearmanr
        spearman_r, spearman_p = spearmanr(flat_a, flat_b)

        # Per-category agreement: do both models cluster same categories?
        results["layers"].append({
            "layer": li,
            "rsa_pearson": float(pearson_r),
            "rsa_spearman": float(spearman_r),
            "rsa_spearman_p": float(spearman_p),
            "mean_sim_a": float(flat_a.mean()),
            "mean_sim_b": float(flat_b.mean()),
        })

    return results


# ══════════════════════════════════════════════════════════════════
# Analysis 2: Direct hidden state alignment (same d_model)
# ══════════════════════════════════════════════════════════════════


def compute_direct_alignment(
    data_a: dict,
    data_b: dict,
    probes: list[dict],
    target_layers: list[int],
) -> dict:
    """For models with the same d_model: how aligned are hidden states for same facts?

    If both models represent "capital of France" in similar directions in R^5120,
    then the DIRECTION of factual storage is universal.

    This goes beyond RSA — it checks not just relational structure but actual
    DIRECTIONAL agreement in the shared vector space.
    """
    assert data_a["d_model"] == data_b["d_model"], "d_model must match for direct alignment"

    categories = [p["category"] for p in probes]
    results = {"layers": []}

    for li in target_layers:
        hs_a = data_a["hidden_states"][li]  # (n_probes, 5120)
        hs_b = data_b["hidden_states"][li]  # (n_probes, 5120)

        # Normalize
        hs_a_norm = hs_a / np.maximum(np.linalg.norm(hs_a, axis=1, keepdims=True), 1e-8)
        hs_b_norm = hs_b / np.maximum(np.linalg.norm(hs_b, axis=1, keepdims=True), 1e-8)

        # Per-fact cosine alignment (same fact, same direction?)
        per_fact_cos = np.sum(hs_a_norm * hs_b_norm, axis=1)  # (n_probes,)

        # Per-category alignment
        cat_alignment = {}
        for cat in FACTUAL_PROBES.keys():
            cat_idx = [i for i, c in enumerate(categories) if c == cat]
            cat_cos = per_fact_cos[cat_idx]
            cat_alignment[cat] = {
                "mean_cos": float(np.mean(cat_cos)),
                "std_cos": float(np.std(cat_cos)),
                "min_cos": float(np.min(cat_cos)),
                "max_cos": float(np.max(cat_cos)),
            }

        # Cross-fact alignment: does model A's "France" align with model B's "Japan"?
        cross_sim = hs_a_norm @ hs_b_norm.T  # (n_probes, n_probes)
        diagonal_mean = float(np.mean(np.diag(cross_sim)))  # same-fact
        off_diagonal = cross_sim[np.triu_indices(len(probes), k=1)]
        off_diag_mean = float(np.mean(off_diagonal))  # different-fact

        # Selectivity: how much more aligned are same-facts vs different-facts?
        selectivity = diagonal_mean - off_diag_mean

        # Effective dimensionality of cross-model shared subspace
        # Use CCA-like: SVD of cross-correlation matrix
        cross_corr = hs_a_norm.T @ hs_b_norm  # (d_model, d_model)
        _, S_cross, _ = np.linalg.svd(cross_corr, full_matrices=False)
        S_cross_norm = S_cross / S_cross.sum()
        shared_eff_dim = 1.0 / (S_cross_norm ** 2).sum()

        results["layers"].append({
            "layer": li,
            "mean_same_fact_cos": diagonal_mean,
            "mean_diff_fact_cos": off_diag_mean,
            "selectivity": selectivity,
            "per_category": cat_alignment,
            "shared_effective_dim": float(shared_eff_dim),
            "top_singular_value": float(S_cross[0]),
        })

    return results


# ══════════════════════════════════════════════════════════════════
# Analysis 3: Sign agreement at plate level
# ══════════════════════════════════════════════════════════════════


def compute_sign_agreement(
    data_a: dict,
    data_b: dict,
    probes: list[dict],
    target_layers: list[int],
) -> dict:
    """Compare K sign patterns between models at domain-responsive regions.

    Since Qwen3-14B has 8 KV heads (K: 1024×5120) and OLMo-2-13B has 40 KV heads
    (K: 5120×5120), we can't directly compare K ROWS. But we CAN compare:

    1. The INPUT SPACE structure: which d_model dimensions have which signs
       - Group K rows by their projection onto hidden state directions for each fact
       - Compare the sign patterns PROJECTED onto fact-relevant subspaces

    2. The FUNCTIONAL agreement: for the same fact's hidden state direction,
       do both models have similar sign patterns in K?
       - Project: how does K respond to the hidden state for "France"?
       - response_A = sign(K_A) @ hidden_state_A_normalized
       - response_B = sign(K_B) @ hidden_state_B_normalized
       - These are scalars: how strongly each K row responds to this fact's beam
       - Can't compare row-by-row (different n_kv_heads) but CAN compare distributions

    3. Column-level sign agreement: K columns (d_model dimension) can be compared
       - For each of the 5120 input dimensions, what fraction of K rows have + vs - sign?
       - This gives a "sign density" per dimension
       - Compare sign densities across models
    """
    categories = [p["category"] for p in probes]
    results = {"layers": []}

    for li in target_layers:
        k_a = data_a["k_signs"][li].astype(np.float32)  # (kv_dim_a, 5120)
        k_b = data_b["k_signs"][li].astype(np.float32)  # (kv_dim_b, 5120)
        hs_a = data_a["hidden_states"][li]  # (n_probes, 5120)
        hs_b = data_b["hidden_states"][li]  # (n_probes, 5120)

        # ── Method 1: Column sign density comparison ──
        # For each of 5120 input dims, what fraction of K rows are positive?
        density_a = (k_a > 0).mean(axis=0)  # (5120,) fraction positive per column
        density_b = (k_b > 0).mean(axis=0)  # (5120,)

        # Correlation of sign densities
        density_corr = np.corrcoef(density_a, density_b)[0, 1]

        # ── Method 2: Functional response agreement ──
        # For each fact: compute K's response to that fact's hidden state direction
        hs_a_norm = hs_a / np.maximum(np.linalg.norm(hs_a, axis=1, keepdims=True), 1e-8)
        hs_b_norm = hs_b / np.maximum(np.linalg.norm(hs_b, axis=1, keepdims=True), 1e-8)

        # Response vectors: how each K row responds to each fact
        # response_A[i, j] = k_a[i] · hs_a_norm[j] (how much K row i responds to fact j)
        response_a = k_a @ hs_a_norm.T  # (kv_dim_a, n_probes)
        response_b = k_b @ hs_b_norm.T  # (kv_dim_b, n_probes)

        # For each fact: sign pattern of response (which K rows activate?)
        # Since kv_dims differ, compare the DISTRIBUTION of responses
        # Mean absolute response per fact
        mean_resp_a = np.abs(response_a).mean(axis=0)  # (n_probes,)
        mean_resp_b = np.abs(response_b).mean(axis=0)  # (n_probes,)

        # Do both models respond MORE strongly to the same facts?
        response_corr = np.corrcoef(mean_resp_a, mean_resp_b)[0, 1]

        # ── Method 3: Hidden-state-projected sign agreement ──
        # Project K into the shared subspace defined by factual hidden states
        # SVD of hidden states gives us the "factual subspace"
        combined_hs = np.vstack([hs_a_norm, hs_b_norm])  # (2*n_probes, 5120)
        _, _, Vt_shared = np.linalg.svd(combined_hs, full_matrices=False)
        # Top-k shared directions (the factual subspace)
        k_dims = min(20, len(probes))
        factual_subspace = Vt_shared[:k_dims]  # (k_dims, 5120)

        # Project K signs into this shared factual subspace
        k_a_proj = k_a @ factual_subspace.T  # (kv_dim_a, k_dims)
        k_b_proj = k_b @ factual_subspace.T  # (kv_dim_b, k_dims)

        # Sign patterns in the factual subspace
        k_a_proj_signs = np.sign(k_a_proj)
        k_b_proj_signs = np.sign(k_b_proj)

        # Column-wise agreement in the projected space
        # For each factual dimension: what fraction of K rows are positive?
        proj_density_a = (k_a_proj_signs > 0).mean(axis=0)  # (k_dims,)
        proj_density_b = (k_b_proj_signs > 0).mean(axis=0)  # (k_dims,)
        proj_density_corr = np.corrcoef(proj_density_a, proj_density_b)[0, 1]

        # ── Per-category functional agreement ──
        cat_response_agreement = {}
        for cat in FACTUAL_PROBES.keys():
            cat_idx = [i for i, c in enumerate(categories) if c == cat]
            cat_resp_a = mean_resp_a[cat_idx]
            cat_resp_b = mean_resp_b[cat_idx]
            if len(cat_idx) > 2:
                cat_corr = np.corrcoef(cat_resp_a, cat_resp_b)[0, 1]
            else:
                cat_corr = 0.0
            cat_response_agreement[cat] = float(cat_corr)

        results["layers"].append({
            "layer": li,
            "column_sign_density_corr": float(density_corr),
            "functional_response_corr": float(response_corr),
            "projected_sign_density_corr": float(proj_density_corr),
            "per_category_response_agreement": cat_response_agreement,
            "mean_abs_response_a": float(mean_resp_a.mean()),
            "mean_abs_response_b": float(mean_resp_b.mean()),
            "factual_subspace_dims": k_dims,
        })

    return results


# ══════════════════════════════════════════════════════════════════
# Analysis 4: Universal hologram extraction
# ══════════════════════════════════════════════════════════════════


def extract_universal_hologram(
    data_a: dict,
    data_b: dict,
    probes: list[dict],
    target_layers: list[int],
) -> dict:
    """Identify the INTERSECTION — what both models agree on.

    The universal hologram is defined as: structure that BOTH models
    converged on independently. This is the denoised signal.

    We measure:
    1. Direction agreement: hidden states that point the same way in both models
    2. Relational agreement: facts that are near each other in both models
    3. The "universal fraction": what percentage of structure is shared
    """
    categories = [p["category"] for p in probes]
    cat_names = list(FACTUAL_PROBES.keys())
    results = {"layers": []}

    for li in target_layers:
        hs_a = data_a["hidden_states"][li]
        hs_b = data_b["hidden_states"][li]

        hs_a_norm = hs_a / np.maximum(np.linalg.norm(hs_a, axis=1, keepdims=True), 1e-8)
        hs_b_norm = hs_b / np.maximum(np.linalg.norm(hs_b, axis=1, keepdims=True), 1e-8)

        # ── Per-fact alignment score ──
        per_fact_cos = np.sum(hs_a_norm * hs_b_norm, axis=1)

        # Facts where both models agree strongly (|cos| > threshold)
        threshold = 0.1  # even weak alignment is meaningful at d=5120
        aligned_mask = np.abs(per_fact_cos) > threshold
        n_aligned = int(aligned_mask.sum())
        universal_fraction = n_aligned / len(probes)

        # ── Category clustering agreement ──
        # Does model A cluster geography together? Does model B?
        # Measure within-category cohesion in each model
        cat_cohesion_a = {}
        cat_cohesion_b = {}
        for cat in cat_names:
            cat_idx = [i for i, c in enumerate(categories) if c == cat]
            if len(cat_idx) < 2:
                continue
            # Within-category cosine (cohesion)
            cat_hs_a = hs_a_norm[cat_idx]
            cat_hs_b = hs_b_norm[cat_idx]
            coh_a = (cat_hs_a @ cat_hs_a.T)[np.triu_indices(len(cat_idx), k=1)].mean()
            coh_b = (cat_hs_b @ cat_hs_b.T)[np.triu_indices(len(cat_idx), k=1)].mean()
            cat_cohesion_a[cat] = float(coh_a)
            cat_cohesion_b[cat] = float(coh_b)

        # Cohesion agreement: do both models find same categories cohesive?
        if cat_cohesion_a and cat_cohesion_b:
            coh_values_a = [cat_cohesion_a[c] for c in cat_names if c in cat_cohesion_a]
            coh_values_b = [cat_cohesion_b[c] for c in cat_names if c in cat_cohesion_b]
            cohesion_agreement = float(np.corrcoef(coh_values_a, coh_values_b)[0, 1])
        else:
            cohesion_agreement = 0.0

        # ── Shared principal subspace ──
        # SVD each model's hidden states, find shared subspace via canonical correlations
        _, S_a, Vt_a = np.linalg.svd(hs_a_norm, full_matrices=False)
        _, S_b, Vt_b = np.linalg.svd(hs_b_norm, full_matrices=False)

        # Canonical correlations between top-k subspaces
        k_sub = min(10, len(probes) - 1)
        Va = Vt_a[:k_sub].T  # (d_model, k_sub) — model A's factual subspace
        Vb = Vt_b[:k_sub].T  # (d_model, k_sub) — model B's factual subspace

        # Cosines between subspace bases (canonical angles)
        cross = Va.T @ Vb  # (k_sub, k_sub)
        _, canonical_corrs, _ = np.linalg.svd(cross)
        # Canonical correlations are the singular values (measure of subspace alignment)

        results["layers"].append({
            "layer": li,
            "universal_fraction": universal_fraction,
            "n_aligned_facts": n_aligned,
            "mean_alignment": float(per_fact_cos.mean()),
            "std_alignment": float(per_fact_cos.std()),
            "cohesion_agreement": cohesion_agreement,
            "category_cohesion_a": cat_cohesion_a,
            "category_cohesion_b": cat_cohesion_b,
            "canonical_correlations": canonical_corrs[:5].tolist(),
            "mean_canonical_corr": float(canonical_corrs[:k_sub].mean()),
            "subspace_overlap_dim": int((canonical_corrs > 0.5).sum()),
        })

    return results


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="Holographic tomography probe")
    parser.add_argument("--models", default="qwen3-14b,olmo-2-13b",
                        help="Comma-separated model keys")
    parser.add_argument("--layers", default="0,10,20,30,39",
                        help="Comma-separated layer indices to probe")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--quick", action="store_true",
                        help="Use fewer layers (0,20,39)")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model_keys = args.models.split(",")
    target_layers = [int(x) for x in args.layers.split(",")]

    if args.quick:
        target_layers = [0, 20, 39]

    probes = flatten_probes()

    print(f"\n{'═'*70}", file=sys.stderr)
    print(f"  HOLOGRAPHIC TOMOGRAPHY — Cross-Model Universal Structure", file=sys.stderr)
    print(f"{'═'*70}", file=sys.stderr)
    print(f"  Models:  {model_keys}", file=sys.stderr)
    print(f"  Layers:  {target_layers}", file=sys.stderr)
    print(f"  Probes:  {len(probes)} facts in {len(FACTUAL_PROBES)} categories", file=sys.stderr)
    print(f"{'═'*70}\n", file=sys.stderr)

    # ══ Extract hidden states from each model ════════════════════
    print("Phase 1: Extracting hidden states from each model...\n", file=sys.stderr)

    model_data = {}
    for mk in model_keys:
        print(f"  ─── {mk} ───", file=sys.stderr)
        t0 = time.time()
        model_data[mk] = extract_hidden_states(mk, target_layers, probes, args.device)
        print(f"  Done in {time.time()-t0:.1f}s\n", file=sys.stderr)

    # ══ Analysis ═════════════════════════════════════════════════
    print(f"{'─'*70}", file=sys.stderr)
    print(f"  Phase 2: CROSS-MODEL ANALYSIS", file=sys.stderr)
    print(f"{'─'*70}\n", file=sys.stderr)

    # For now: pairwise comparison of first two models
    mk_a, mk_b = model_keys[0], model_keys[1]
    data_a, data_b = model_data[mk_a], model_data[mk_b]

    # ── 1. RSA ──
    print("  1) Representational Similarity Analysis (RSA)...", file=sys.stderr)
    rsa_results = compute_rsa(data_a, data_b, target_layers)

    print(f"\n  RSA Results ({mk_a} vs {mk_b}):", file=sys.stderr)
    print(f"  {'Layer':<8} {'Pearson':>9} {'Spearman':>10} {'p-value':>10}", file=sys.stderr)
    print(f"  {'─'*8} {'─'*9} {'─'*10} {'─'*10}", file=sys.stderr)
    for lr in rsa_results["layers"]:
        print(f"  L{lr['layer']:<6} {lr['rsa_pearson']:>9.4f} {lr['rsa_spearman']:>10.4f} "
              f"{lr['rsa_spearman_p']:>10.2e}", file=sys.stderr)

    # ── 2. Direct alignment ──
    if data_a["d_model"] == data_b["d_model"]:
        print(f"\n  2) Direct hidden state alignment (d_model={data_a['d_model']})...", file=sys.stderr)
        align_results = compute_direct_alignment(data_a, data_b, probes, target_layers)

        print(f"\n  Direct Alignment ({mk_a} vs {mk_b}):", file=sys.stderr)
        print(f"  {'Layer':<8} {'SameFact':>9} {'DiffFact':>9} {'Select':>8} "
              f"{'SharedDim':>10}", file=sys.stderr)
        print(f"  {'─'*8} {'─'*9} {'─'*9} {'─'*8} {'─'*10}", file=sys.stderr)
        for lr in align_results["layers"]:
            print(f"  L{lr['layer']:<6} {lr['mean_same_fact_cos']:>9.4f} "
                  f"{lr['mean_diff_fact_cos']:>9.4f} {lr['selectivity']:>8.4f} "
                  f"{lr['shared_effective_dim']:>10.1f}", file=sys.stderr)

        print(f"\n  Per-category alignment (same fact cosine):", file=sys.stderr)
        # Use last layer
        last_layer_align = align_results["layers"][-1]["per_category"]
        print(f"  {'Category':<12} {'Mean cos':>9} {'Std':>8}", file=sys.stderr)
        print(f"  {'─'*12} {'─'*9} {'─'*8}", file=sys.stderr)
        for cat, info in last_layer_align.items():
            print(f"  {cat:<12} {info['mean_cos']:>9.4f} {info['std_cos']:>8.4f}", file=sys.stderr)
    else:
        align_results = None
        print(f"\n  2) SKIPPED (d_model mismatch: {data_a['d_model']} vs {data_b['d_model']})",
              file=sys.stderr)

    # ── 3. Sign agreement ──
    print(f"\n  3) Sign pattern agreement at plate level...", file=sys.stderr)
    sign_results = compute_sign_agreement(data_a, data_b, probes, target_layers)

    print(f"\n  Sign Agreement ({mk_a} vs {mk_b}):", file=sys.stderr)
    print(f"  {'Layer':<8} {'ColDensity':>11} {'FuncResp':>9} {'ProjSign':>9}", file=sys.stderr)
    print(f"  {'─'*8} {'─'*11} {'─'*9} {'─'*9}", file=sys.stderr)
    for lr in sign_results["layers"]:
        print(f"  L{lr['layer']:<6} {lr['column_sign_density_corr']:>11.4f} "
              f"{lr['functional_response_corr']:>9.4f} "
              f"{lr['projected_sign_density_corr']:>9.4f}", file=sys.stderr)

    # ── 4. Universal hologram extraction ──
    print(f"\n  4) Universal hologram identification...", file=sys.stderr)
    universal_results = extract_universal_hologram(data_a, data_b, probes, target_layers)

    print(f"\n  Universal Hologram ({mk_a} ∩ {mk_b}):", file=sys.stderr)
    print(f"  {'Layer':<8} {'UnivrFrac':>10} {'MeanAlign':>10} {'CohAgree':>10} "
          f"{'CanonCorr':>10} {'SubOverlap':>11}", file=sys.stderr)
    print(f"  {'─'*8} {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*11}", file=sys.stderr)
    for lr in universal_results["layers"]:
        print(f"  L{lr['layer']:<6} {lr['universal_fraction']:>10.3f} "
              f"{lr['mean_alignment']:>10.4f} {lr['cohesion_agreement']:>10.4f} "
              f"{lr['mean_canonical_corr']:>10.4f} {lr['subspace_overlap_dim']:>11}",
              file=sys.stderr)

    # ── Prediction accuracy comparison ──
    print(f"\n  Factual recall comparison:", file=sys.stderr)
    for mk in model_keys:
        preds = model_data[mk]["predictions"]
        top1 = sum(1 for p in preds if p["correct"]) / len(preds)
        mean_rank = np.mean([p["rank"] for p in preds])
        mean_lp = np.mean([p["log_prob"] for p in preds])
        print(f"    {mk:<15} top1={top1:.1%}, mean_rank={mean_rank:.0f}, "
              f"mean_logprob={mean_lp:.2f}", file=sys.stderr)

    # ══ Summary ══════════════════════════════════════════════════
    print(f"\n{'═'*70}", file=sys.stderr)
    print(f"  SUMMARY — Universal Hologram Findings", file=sys.stderr)
    print(f"{'═'*70}", file=sys.stderr)

    # Key metrics at best layer
    best_rsa = max(rsa_results["layers"], key=lambda x: x["rsa_pearson"])
    print(f"\n  Best RSA (representational geometry agreement):", file=sys.stderr)
    print(f"    Layer {best_rsa['layer']}: Pearson r={best_rsa['rsa_pearson']:.4f}, "
          f"Spearman ρ={best_rsa['rsa_spearman']:.4f}", file=sys.stderr)

    if align_results:
        best_align = max(align_results["layers"], key=lambda x: x["selectivity"])
        print(f"\n  Best direct alignment (same-fact selectivity):", file=sys.stderr)
        print(f"    Layer {best_align['layer']}: same_fact={best_align['mean_same_fact_cos']:.4f}, "
              f"diff_fact={best_align['mean_diff_fact_cos']:.4f}, "
              f"selectivity={best_align['selectivity']:.4f}", file=sys.stderr)

    best_sign = max(sign_results["layers"], key=lambda x: x["functional_response_corr"])
    print(f"\n  Best sign agreement (functional response):", file=sys.stderr)
    print(f"    Layer {best_sign['layer']}: r={best_sign['functional_response_corr']:.4f}",
          file=sys.stderr)

    best_univ = max(universal_results["layers"], key=lambda x: x["mean_canonical_corr"])
    print(f"\n  Best subspace overlap:", file=sys.stderr)
    print(f"    Layer {best_univ['layer']}: canonical_corr={best_univ['mean_canonical_corr']:.4f}, "
          f"overlap_dims={best_univ['subspace_overlap_dim']}", file=sys.stderr)

    # Verdict
    top_rsa = best_rsa["rsa_pearson"]
    if top_rsa > 0.5:
        print(f"\n  ✅ STRONG universal structure: RSA r={top_rsa:.3f}", file=sys.stderr)
        print(f"     Both models organize factual knowledge SIMILARLY.", file=sys.stderr)
        print(f"     Cross-model intersection reveals denoised universal hologram.", file=sys.stderr)
    elif top_rsa > 0.2:
        print(f"\n  ⚠️  MODERATE universal structure: RSA r={top_rsa:.3f}", file=sys.stderr)
        print(f"     Partial agreement — some structure is shared, some model-specific.", file=sys.stderr)
    else:
        print(f"\n  ❌ WEAK universal structure: RSA r={top_rsa:.3f}", file=sys.stderr)
        print(f"     Models organize facts differently. Universal hologram may not exist at this level.",
              file=sys.stderr)

    # ══ Save results ═════════════════════════════════════════════
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "config": {
            "models": model_keys,
            "target_layers": target_layers,
            "n_probes": len(probes),
            "categories": list(FACTUAL_PROBES.keys()),
        },
        "predictions": {mk: model_data[mk]["predictions"] for mk in model_keys},
        "rsa": rsa_results,
        "direct_alignment": align_results,
        "sign_agreement": sign_results,
        "universal_hologram": universal_results,
    }

    json_path = args.output_dir / "tomography_results.json"
    json_path.write_text(json.dumps(output, indent=2))
    print(f"\n  💾 Results: {json_path}", file=sys.stderr)
    print(f"{'═'*70}\n", file=sys.stderr)


if __name__ == "__main__":
    main()
