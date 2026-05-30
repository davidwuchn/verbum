"""Moiré Decomposition — Reverse-engineering the holographic fact index.

The moiré selectivity experiment (moire_selectivity.py) confirmed that
the SwiGLU moiré pattern is 2.4× more selective than gate alone and
clusters by relation type (2.6× coherence). This script decomposes
the moiré to understand HOW the addressing works.

Four analyses:

  A) RELATION DIRECTION EXTRACTION
     Compute centroid moiré pattern per relation group per layer.
     Decompose: moiré = relation_centroid + entity_residual.
     Variance explained by centroid = how crystallized the relation is.

  B) MODE DECOMPOSITION (SVD)
     SVD of the moiré pattern matrix → independent addressing modes.
     How many modes exist? Do they align with relation types?
     Compare gate-only, up-only, and moiré mode counts.

  C) CROSS-MODE INTERACTION TENSOR
     Project probes onto top-K gate modes and top-K up modes.
     Build interaction matrix: which (gate_mode, up_mode) pairs co-fire.
     Different relations → different quadrants of the interaction space?
     This is the core test of quadratic addressing.

  D) RESIDUAL → MOIRÉ MAPPING
     Hook the residual stream INPUT to each FFN.
     Linear regression: residual → moiré pattern.
     R² measures content-addressability: can the question predict
     which moiré fires without seeing the FFN weights?

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/moire_decompose.py
    uv run python scripts/experiments/moire_decompose.py --model Qwen/Qwen3-4B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PROBES_FILE = Path(__file__).parent.parent.parent / "probes" / "fact_recall.json"
PROBES_EXTENDED = Path(__file__).parent.parent.parent / "probes" / "fact_recall_extended.json"
RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "moire-decompose"


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def load_probes(probe_path: Path | None = None) -> list[dict]:
    path = probe_path or PROBES_FILE
    data = json.load(open(path))
    # Exclude computation/arithmetic controls — keep only fact probes
    exclude = {"computation", "arithmetic", "lambda"}
    return [p for p in data["probes"] if p["category"] not in exclude]


def build_relation_groups(probes: list[dict]) -> dict[str, list[str]]:
    """Auto-detect relation groups from probe categories."""
    groups: dict[str, list[str]] = defaultdict(list)
    for p in probes:
        groups[p["category"]].append(p["id"])
    return dict(groups)


# ---------------------------------------------------------------------------
# Activation hooking — extended to capture residual input
# ---------------------------------------------------------------------------

class DecomposeHook:
    """Captures gate (post-silu), up, moiré, AND residual input per layer."""

    def __init__(self, n_layers: int):
        self.n_layers = n_layers
        self.gate_acts: dict[int, torch.Tensor] = {}
        self.up_acts: dict[int, torch.Tensor] = {}
        self.residual_acts: dict[int, torch.Tensor] = {}
        self.handles: list = []

    def _make_gate_hook(self, layer_idx: int):
        def hook(module, input, output):
            self.gate_acts[layer_idx] = output[0, -1, :].detach().cpu()
        return hook

    def _make_up_hook(self, layer_idx: int):
        def hook(module, input, output):
            self.up_acts[layer_idx] = output[0, -1, :].detach().cpu()
        return hook

    def _make_residual_hook(self, layer_idx: int):
        def hook(module, input, output):
            # MLP forward hook — input[0] is the residual stream entering MLP
            # After post_attention_layernorm, input to MLP is the normed residual
            self.residual_acts[layer_idx] = input[0][0, -1, :].detach().cpu()
        return hook

    def register(self, model):
        for i in range(self.n_layers):
            layer = model.model.layers[i]
            mlp = layer.mlp
            h1 = mlp.gate_proj.register_forward_hook(self._make_gate_hook(i))
            h2 = mlp.up_proj.register_forward_hook(self._make_up_hook(i))
            # Hook the MLP itself to get its input (the normed residual)
            h3 = mlp.register_forward_hook(self._make_residual_hook(i))
            self.handles.extend([h1, h2, h3])
        log(f"  Registered hooks on {self.n_layers} layers (gate + up + residual)")

    def remove(self):
        for h in self.handles:
            h.remove()
        self.handles.clear()

    def get_activations(self) -> dict[int, dict[str, np.ndarray]]:
        result = {}
        for layer_idx in range(self.n_layers):
            if layer_idx not in self.gate_acts:
                continue
            gate_raw = self.gate_acts[layer_idx].float()
            up_raw = self.up_acts[layer_idx].float()
            residual = self.residual_acts[layer_idx].float()

            gate = torch.nn.functional.silu(gate_raw)
            up = up_raw
            moire = gate * up

            result[layer_idx] = {
                "gate": gate.numpy(),
                "up": up.numpy(),
                "moire": moire.numpy(),
                "residual": residual.numpy(),
            }
        return result

    def clear(self):
        self.gate_acts.clear()
        self.up_acts.clear()
        self.residual_acts.clear()


# ---------------------------------------------------------------------------
# Analysis A: Relation Direction Extraction
# ---------------------------------------------------------------------------

def analyze_relation_directions(
    activations: dict[str, dict[int, dict[str, np.ndarray]]],
    probe_ids: list[str],
    n_layers: int,
    relation_groups: dict[str, list[str]] | None = None,
) -> dict:
    """Extract relation centroids and measure variance explained."""
    log("\n--- Analysis A: Relation Direction Extraction ---")

    id_to_group = {}
    for group_name, group_ids in relation_groups.items():
        for gid in group_ids:
            id_to_group[gid] = group_name

    results = {}

    for layer_idx in range(n_layers):
        # Collect moiré patterns grouped by relation
        by_relation: dict[str, list[np.ndarray]] = defaultdict(list)
        all_patterns = []
        all_ids = []

        for pid in probe_ids:
            if layer_idx not in activations[pid]:
                continue
            pattern = activations[pid][layer_idx]["moire"]
            group = id_to_group.get(pid)
            if group:
                by_relation[group].append(pattern)
            all_patterns.append(pattern)
            all_ids.append(pid)

        if len(all_patterns) < 5:
            continue

        # Compute centroids
        centroids = {}
        for group, patterns in by_relation.items():
            centroids[group] = np.mean(patterns, axis=0)

        # Decompose each pattern: moiré = centroid + residual
        variance_explained = {}
        for group, patterns in by_relation.items():
            centroid = centroids[group]
            total_var = 0
            residual_var = 0
            for p in patterns:
                total_var += np.sum(p ** 2)
                residual = p - centroid
                residual_var += np.sum(residual ** 2)
            if total_var > 1e-10:
                variance_explained[group] = 1.0 - (residual_var / total_var)
            else:
                variance_explained[group] = 0.0

        # Cross-centroid similarity (how distinct are relations from each other?)
        groups = sorted(centroids.keys())
        centroid_cos = {}
        for i, g1 in enumerate(groups):
            for g2 in groups[i + 1:]:
                c1, c2 = centroids[g1], centroids[g2]
                n1, n2 = np.linalg.norm(c1), np.linalg.norm(c2)
                if n1 > 1e-10 and n2 > 1e-10:
                    cos = float(np.dot(c1, c2) / (n1 * n2))
                else:
                    cos = 0.0
                centroid_cos[f"{g1}-{g2}"] = cos

        results[layer_idx] = {
            "variance_explained_by_centroid": variance_explained,
            "mean_variance_explained": float(np.mean(list(variance_explained.values()))),
            "centroid_cross_similarity": centroid_cos,
            "mean_centroid_cos": float(np.mean(list(centroid_cos.values()))),
            "n_relations": len(centroids),
            "n_probes": len(all_patterns),
        }

    return results


# ---------------------------------------------------------------------------
# Analysis B: Mode Decomposition (SVD)
# ---------------------------------------------------------------------------

def analyze_modes(
    activations: dict[str, dict[int, dict[str, np.ndarray]]],
    probe_ids: list[str],
    probe_categories: dict[str, str],
    n_layers: int,
    top_k: int = 10,
) -> dict:
    """SVD of moiré, gate, up pattern matrices per layer."""
    log("\n--- Analysis B: Mode Decomposition (SVD) ---")

    results = {}

    for layer_idx in range(n_layers):
        gate_pats = []
        up_pats = []
        moire_pats = []
        cats = []

        for pid in probe_ids:
            if layer_idx not in activations[pid]:
                continue
            acts = activations[pid][layer_idx]
            gate_pats.append(acts["gate"])
            up_pats.append(acts["up"])
            moire_pats.append(acts["moire"])
            cats.append(probe_categories[pid])

        if len(moire_pats) < 5:
            continue

        def svd_analysis(patterns, label):
            mat = np.stack(patterns)  # (n_probes, d_ffn)
            # Center the matrix (zero-mean per feature)
            mat_centered = mat - mat.mean(axis=0, keepdims=True)
            U, S, Vt = np.linalg.svd(mat_centered, full_matrices=False)

            # Variance explained by each mode
            total_var = np.sum(S ** 2)
            var_explained = (S ** 2) / total_var if total_var > 1e-10 else S * 0

            # Effective rank (entropy-based)
            s_norm = S[S > 1e-10]
            p = s_norm / s_norm.sum()
            eff_rank = float(np.exp(-np.sum(p * np.log(p))))

            # 90% variance rank
            cumvar = np.cumsum(var_explained)
            rank_90 = int(np.searchsorted(cumvar, 0.9)) + 1

            # Per-mode category loading (which categories load on which mode)
            # U[:, k] = projection of each probe onto mode k
            unique_cats = sorted(set(cats))
            mode_cat_loadings = {}
            for k in range(min(top_k, len(S))):
                projections = U[:, k]
                cat_mean = {}
                for cat in unique_cats:
                    cat_projs = [projections[i] for i, c in enumerate(cats) if c == cat]
                    cat_mean[cat] = float(np.mean(np.abs(cat_projs))) if cat_projs else 0.0
                mode_cat_loadings[k] = cat_mean

            return {
                "singular_values": S[:top_k].tolist(),
                "variance_explained": var_explained[:top_k].tolist(),
                "cumulative_variance": cumvar[:top_k].tolist(),
                "effective_rank": eff_rank,
                "rank_90": rank_90,
                "mode_category_loadings": mode_cat_loadings,
            }

        results[layer_idx] = {
            "gate": svd_analysis(gate_pats, "gate"),
            "up": svd_analysis(up_pats, "up"),
            "moire": svd_analysis(moire_pats, "moiré"),
            "n_probes": len(moire_pats),
        }

    return results


# ---------------------------------------------------------------------------
# Analysis C: Cross-Mode Interaction Tensor
# ---------------------------------------------------------------------------

def analyze_cross_mode_interaction(
    activations: dict[str, dict[int, dict[str, np.ndarray]]],
    probe_ids: list[str],
    probe_categories: dict[str, str],
    n_layers: int,
    n_modes: int = 8,
) -> dict:
    """Build interaction tensor: which (gate_mode, up_mode) pairs co-fire per relation."""
    log("\n--- Analysis C: Cross-Mode Interaction Tensor ---")

    results = {}

    for layer_idx in range(n_layers):
        gate_pats = []
        up_pats = []
        cats = []
        pids = []

        for pid in probe_ids:
            if layer_idx not in activations[pid]:
                continue
            acts = activations[pid][layer_idx]
            gate_pats.append(acts["gate"])
            up_pats.append(acts["up"])
            cats.append(probe_categories[pid])
            pids.append(pid)

        if len(gate_pats) < 5:
            continue

        # SVD of gate and up separately to get their independent modes
        gate_mat = np.stack(gate_pats)
        up_mat = np.stack(up_pats)

        gate_centered = gate_mat - gate_mat.mean(axis=0, keepdims=True)
        up_centered = up_mat - up_mat.mean(axis=0, keepdims=True)

        _, _, gate_Vt = np.linalg.svd(gate_centered, full_matrices=False)
        _, _, up_Vt = np.linalg.svd(up_centered, full_matrices=False)

        # Top-K modes as basis vectors
        gate_basis = gate_Vt[:n_modes]  # (n_modes, d_ffn)
        up_basis = up_Vt[:n_modes]      # (n_modes, d_ffn)

        # Project each probe onto gate modes and up modes
        # gate_coords[i, k] = how much probe i loads on gate mode k
        gate_coords = gate_centered @ gate_basis.T  # (n_probes, n_modes)
        up_coords = up_centered @ up_basis.T          # (n_probes, n_modes)

        # Build interaction tensor per relation
        # For each probe: interaction[g, u] = gate_coord[g] * up_coord[u]
        # Then average by relation group
        unique_cats = sorted(set(cats))
        interaction_by_relation = {}

        for cat in unique_cats:
            cat_indices = [i for i, c in enumerate(cats) if c == cat]
            if not cat_indices:
                continue

            # Average interaction matrix for this relation
            cat_interactions = []
            for idx in cat_indices:
                # Outer product of gate coords × up coords
                interaction = np.outer(gate_coords[idx], up_coords[idx])  # (n_modes, n_modes)
                cat_interactions.append(interaction)

            avg_interaction = np.mean(cat_interactions, axis=0)
            interaction_by_relation[cat] = avg_interaction

        # Measure: how distinct are the interaction patterns across relations?
        # Pairwise cosine between flattened interaction matrices
        cross_relation_cos = {}
        for i, cat1 in enumerate(unique_cats):
            for cat2 in unique_cats[i + 1:]:
                if cat1 not in interaction_by_relation or cat2 not in interaction_by_relation:
                    continue
                m1 = interaction_by_relation[cat1].flatten()
                m2 = interaction_by_relation[cat2].flatten()
                n1, n2 = np.linalg.norm(m1), np.linalg.norm(m2)
                if n1 > 1e-10 and n2 > 1e-10:
                    cos = float(np.dot(m1, m2) / (n1 * n2))
                else:
                    cos = 0.0
                cross_relation_cos[f"{cat1}-{cat2}"] = cos

        # Which (gate_mode, up_mode) cells dominate for each relation?
        dominant_cells = {}
        for cat, interaction in interaction_by_relation.items():
            abs_int = np.abs(interaction)
            # Find top-3 cells
            flat_idx = np.argsort(abs_int.flatten())[::-1][:3]
            top_cells = []
            for fi in flat_idx:
                g_idx, u_idx = divmod(fi, n_modes)
                top_cells.append({
                    "gate_mode": int(g_idx),
                    "up_mode": int(u_idx),
                    "strength": float(abs_int[g_idx, u_idx]),
                })
            dominant_cells[cat] = top_cells

        # Uniqueness: for each relation, what fraction of its dominant cells
        # are NOT in any other relation's top cells?
        all_dominant_sets = {
            cat: {(c["gate_mode"], c["up_mode"]) for c in cells}
            for cat, cells in dominant_cells.items()
        }
        uniqueness = {}
        for cat, cells in all_dominant_sets.items():
            other_cells = set()
            for other_cat, other in all_dominant_sets.items():
                if other_cat != cat:
                    other_cells |= other
            unique_count = len(cells - other_cells)
            uniqueness[cat] = unique_count / len(cells) if cells else 0.0

        results[layer_idx] = {
            "n_modes": n_modes,
            "cross_relation_cos": cross_relation_cos,
            "mean_cross_cos": float(np.mean(list(cross_relation_cos.values()))) if cross_relation_cos else 0.0,
            "dominant_cells": dominant_cells,
            "uniqueness": uniqueness,
            "interaction_matrices": {
                cat: mat.tolist() for cat, mat in interaction_by_relation.items()
            },
        }

    return results


# ---------------------------------------------------------------------------
# Analysis D: Residual → Moiré Mapping
# ---------------------------------------------------------------------------

def analyze_residual_mapping(
    activations: dict[str, dict[int, dict[str, np.ndarray]]],
    probe_ids: list[str],
    n_layers: int,
) -> dict:
    """Test content-addressability: can residual direction predict moiré pattern?"""
    log("\n--- Analysis D: Residual → Moiré Mapping ---")

    results = {}

    for layer_idx in range(n_layers):
        residuals = []
        moires = []

        for pid in probe_ids:
            if layer_idx not in activations[pid]:
                continue
            acts = activations[pid][layer_idx]
            residuals.append(acts["residual"])
            moires.append(acts["moire"])

        if len(residuals) < 5:
            continue

        R = np.stack(residuals)   # (n_probes, d_model)
        M = np.stack(moires)      # (n_probes, d_ffn)

        # Center both
        R_c = R - R.mean(axis=0, keepdims=True)
        M_c = M - M.mean(axis=0, keepdims=True)

        # Linear regression: M_c ≈ R_c @ W  (least squares)
        # Since n_probes << d_model, this is underdetermined.
        # Use SVD of R_c to project into the subspace spanned by the probes.
        U_r, S_r, Vt_r = np.linalg.svd(R_c, full_matrices=False)
        # Keep modes with significant singular values
        threshold = S_r[0] * 1e-6
        n_modes = int(np.sum(S_r > threshold))

        # Project residuals into their own SVD space
        R_proj = U_r[:, :n_modes] * S_r[:n_modes]  # (n_probes, n_modes)

        # Predict M from R_proj via least squares
        # M_pred = R_proj @ beta, beta = pinv(R_proj) @ M_c
        beta, _, _, _ = np.linalg.lstsq(R_proj, M_c, rcond=None)
        M_pred = R_proj @ beta

        # R² per probe (leave-one-out would be better, but this gives the upper bound)
        ss_res = np.sum((M_c - M_pred) ** 2, axis=1)
        ss_tot = np.sum(M_c ** 2, axis=1)
        r2_per_probe = 1.0 - ss_res / np.maximum(ss_tot, 1e-10)

        # Overall R² (on all dimensions)
        overall_ss_res = np.sum((M_c - M_pred) ** 2)
        overall_ss_tot = np.sum(M_c ** 2)
        overall_r2 = 1.0 - overall_ss_res / max(overall_ss_tot, 1e-10)

        # Cosine similarity between predicted and actual moiré
        cos_sims = []
        for i in range(len(moires)):
            n_pred = np.linalg.norm(M_pred[i])
            n_act = np.linalg.norm(M_c[i])
            if n_pred > 1e-10 and n_act > 1e-10:
                cos_sims.append(float(np.dot(M_pred[i], M_c[i]) / (n_pred * n_act)))
            else:
                cos_sims.append(0.0)

        results[layer_idx] = {
            "overall_r2": float(overall_r2),
            "mean_r2_per_probe": float(np.mean(r2_per_probe)),
            "mean_cos_sim": float(np.mean(cos_sims)),
            "std_cos_sim": float(np.std(cos_sims)),
            "n_residual_modes": n_modes,
            "n_probes": len(residuals),
        }

    return results


# ---------------------------------------------------------------------------
# Printing
# ---------------------------------------------------------------------------

def print_relation_directions(results: dict, n_layers: int):
    log("\n" + "=" * 100)
    log("A: RELATION DIRECTION EXTRACTION")
    log("=" * 100)
    log(f"{'Layer':>5s} | {'mean var expl':>12s} | {'centroid cos':>11s} | per-relation variance explained")
    log("-" * 100)

    for layer_idx in range(n_layers):
        if layer_idx not in results:
            continue
        r = results[layer_idx]
        ve = r["variance_explained_by_centroid"]
        ve_str = "  ".join(f"{k[:3]}={v:.3f}" for k, v in sorted(ve.items()))
        log(f"L{layer_idx:3d}  | {r['mean_variance_explained']:12.4f} | {r['mean_centroid_cos']:11.4f} | {ve_str}")


def print_modes(results: dict, n_layers: int):
    log("\n" + "=" * 100)
    log("B: MODE DECOMPOSITION (SVD)")
    log("=" * 100)
    log(f"{'Layer':>5s} | {'gate eff_r':>10s} {'gate r90':>8s} | {'up eff_r':>8s} {'up r90':>6s} | "
        f"{'moiré eff_r':>11s} {'moiré r90':>9s} | {'top mode var%':>13s}")
    log("-" * 100)

    for layer_idx in range(n_layers):
        if layer_idx not in results:
            continue
        r = results[layer_idx]
        g, u, m = r["gate"], r["up"], r["moire"]
        top_var = m["variance_explained"][0] * 100 if m["variance_explained"] else 0
        log(f"L{layer_idx:3d}  | {g['effective_rank']:10.1f} {g['rank_90']:8d} | "
            f"{u['effective_rank']:8.1f} {u['rank_90']:6d} | "
            f"{m['effective_rank']:11.1f} {m['rank_90']:9d} | "
            f"{top_var:12.1f}%")


def print_cross_modes(results: dict, n_layers: int):
    log("\n" + "=" * 100)
    log("C: CROSS-MODE INTERACTION")
    log("=" * 100)
    log(f"{'Layer':>5s} | {'mean cross cos':>14s} | dominant (gate_mode, up_mode) by relation")
    log("-" * 100)

    for layer_idx in range(n_layers):
        if layer_idx not in results:
            continue
        r = results[layer_idx]
        dom = r["dominant_cells"]
        dom_str = "  ".join(
            f"{cat[:3]}:({cells[0]['gate_mode']},{cells[0]['up_mode']})"
            for cat, cells in sorted(dom.items())
            if cells
        )
        log(f"L{layer_idx:3d}  | {r['mean_cross_cos']:14.4f} | {dom_str}")


def print_residual_mapping(results: dict, n_layers: int):
    log("\n" + "=" * 100)
    log("D: RESIDUAL → MOIRÉ MAPPING (content-addressability)")
    log("=" * 100)
    log(f"{'Layer':>5s} | {'R²':>8s} | {'mean cos':>8s} | {'std cos':>8s} | {'res modes':>9s}")
    log("-" * 100)

    for layer_idx in range(n_layers):
        if layer_idx not in results:
            continue
        r = results[layer_idx]
        log(f"L{layer_idx:3d}  | {r['overall_r2']:8.4f} | {r['mean_cos_sim']:8.4f} | "
            f"{r['std_cos_sim']:8.4f} | {r['n_residual_modes']:9d}")


def print_verdict(
    relation_results: dict,
    mode_results: dict,
    cross_results: dict,
    mapping_results: dict,
    n_layers: int,
):
    log("\n" + "=" * 80)
    log("VERDICT")
    log("=" * 80)

    enrich_start = int(n_layers * 0.5)
    enrich_end = int(n_layers * 0.9)
    enrich_layers = [l for l in range(enrich_start, enrich_end + 1)
                     if l in relation_results]

    if not enrich_layers:
        log("  No ENRICH zone layers with data!")
        return

    # A: Relation directions
    avg_var_expl = np.mean([relation_results[l]["mean_variance_explained"] for l in enrich_layers])
    avg_centroid_cos = np.mean([relation_results[l]["mean_centroid_cos"] for l in enrich_layers])
    log(f"\n  A: Relation direction crystallization (ENRICH zone)")
    log(f"     Variance explained by relation centroid: {avg_var_expl:.3f}")
    log(f"     Cross-relation centroid similarity:      {avg_centroid_cos:.3f}")
    if avg_var_expl > 0.5:
        log(f"     → STRONG. Relations explain >{avg_var_expl:.0%} of moiré variance.")
        log(f"       The coarse grating angle IS the relation direction.")
    elif avg_var_expl > 0.3:
        log(f"     → MODERATE. Relation centroids capture significant structure.")
    else:
        log(f"     → WEAK. Moiré patterns are mostly entity-specific, not relation-driven.")

    # B: Mode count
    avg_moire_rank = np.mean([mode_results[l]["moire"]["effective_rank"] for l in enrich_layers if l in mode_results])
    avg_gate_rank = np.mean([mode_results[l]["gate"]["effective_rank"] for l in enrich_layers if l in mode_results])
    log(f"\n  B: Mode decomposition (ENRICH zone)")
    log(f"     Gate effective rank:  {avg_gate_rank:.1f}")
    log(f"     Moiré effective rank: {avg_moire_rank:.1f}")
    log(f"     Moiré modes per layer (rank-90): {np.mean([mode_results[l]['moire']['rank_90'] for l in enrich_layers if l in mode_results]):.0f}")

    # C: Cross-mode interaction
    avg_cross_cos = np.mean([cross_results[l]["mean_cross_cos"] for l in enrich_layers if l in cross_results])
    log(f"\n  C: Cross-mode interaction (ENRICH zone)")
    log(f"     Mean cross-relation interaction cos: {avg_cross_cos:.3f}")
    if avg_cross_cos < 0.5:
        log(f"     → Relations use DIFFERENT (gate, up) mode combinations.")
        log(f"       The interaction tensor IS the quadratic index.")
    else:
        log(f"     → Relations share similar mode combinations.")

    # D: Content-addressability
    enrich_mapping = [l for l in enrich_layers if l in mapping_results]
    if enrich_mapping:
        avg_r2 = np.mean([mapping_results[l]["overall_r2"] for l in enrich_mapping])
        avg_cos = np.mean([mapping_results[l]["mean_cos_sim"] for l in enrich_mapping])
        log(f"\n  D: Content-addressability (ENRICH zone)")
        log(f"     Residual → Moiré R²:        {avg_r2:.4f}")
        log(f"     Residual → Moiré mean cos:  {avg_cos:.4f}")
        if avg_r2 > 0.8:
            log(f"     → STRONG. Residual direction fully determines moiré pattern.")
            log(f"       The addressing IS content-based.")
        elif avg_r2 > 0.5:
            log(f"     → MODERATE. Residual predicts moiré but with noise.")
        else:
            log(f"     → WEAK. Moiré depends on more than just residual direction.")
            log(f"       (But R² is an upper bound — may improve with more probes.)")

    log("\n" + "=" * 80)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Moiré Decomposition Analysis")
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B", help="HuggingFace model name")
    parser.add_argument("--device", default="mps", help="Device (mps, cuda, cpu)")
    parser.add_argument("--dtype", default="float32", choices=["float16", "bfloat16", "float32"])
    parser.add_argument("--n-modes", type=int, default=8, help="Number of SVD modes for interaction analysis")
    parser.add_argument("--probes", default=None, help="Path to probe JSON file (default: fact_recall.json)")
    args = parser.parse_args()

    dtype_map = {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}
    dtype = dtype_map[args.dtype]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log(f"=== Moiré Decomposition Analysis ===")
    log(f"Model: {args.model}")

    # --- Load probes ---
    probe_path = Path(args.probes) if args.probes else None
    probes = load_probes(probe_path)
    probe_ids = [p["id"] for p in probes]
    probe_categories = {p["id"]: p["category"] for p in probes}
    relation_groups = build_relation_groups(probes)
    log(f"Loaded {len(probes)} fact probes from {probe_path or PROBES_FILE}")
    log(f"  Relation groups ({len(relation_groups)}): {', '.join(f'{k}({len(v)})' for k, v in sorted(relation_groups.items()))}")

    # --- Load model ---
    log("\nLoading model...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        dtype=dtype,
        device_map=args.device,
        trust_remote_code=True,
    )
    model.eval()
    n_layers = model.config.num_hidden_layers
    d_ffn = model.config.intermediate_size
    d_model = model.config.hidden_size
    log(f"Model loaded in {time.time() - t0:.1f}s")
    log(f"  Layers: {n_layers}, d_model: {d_model}, d_ffn: {d_ffn}")

    # --- Collect activations ---
    hook = DecomposeHook(n_layers)
    hook.register(model)

    log("\nCollecting activations...")
    all_activations: dict[str, dict[int, dict[str, np.ndarray]]] = {}
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(args.device)
        with torch.no_grad():
            model(input_ids)
        all_activations[probe["id"]] = hook.get_activations()
        hook.clear()
        if (i + 1) % 10 == 0 or i == len(probes) - 1:
            log(f"  {i + 1}/{len(probes)} probes")
    log(f"Activations collected in {time.time() - t0:.1f}s")

    hook.remove()
    del model
    torch.mps.empty_cache() if args.device == "mps" else None

    # --- Run all analyses ---
    relation_results = analyze_relation_directions(all_activations, probe_ids, n_layers, relation_groups)
    mode_results = analyze_modes(all_activations, probe_ids, probe_categories, n_layers)
    cross_results = analyze_cross_mode_interaction(
        all_activations, probe_ids, probe_categories, n_layers, n_modes=args.n_modes,
    )
    mapping_results = analyze_residual_mapping(all_activations, probe_ids, n_layers)

    # --- Print ---
    print_relation_directions(relation_results, n_layers)
    print_modes(mode_results, n_layers)
    print_cross_modes(cross_results, n_layers)
    print_residual_mapping(mapping_results, n_layers)
    print_verdict(relation_results, mode_results, cross_results, mapping_results, n_layers)

    # --- Save ---
    model_slug = args.model.replace("/", "_")
    probe_slug = Path(args.probes).stem if args.probes else "fact_recall"
    output_file = RESULTS_DIR / f"{model_slug}_{probe_slug}_decompose.json"

    def numpy_safe(obj):
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    output = {
        "model": args.model,
        "dtype": args.dtype,
        "n_layers": n_layers,
        "d_model": d_model,
        "d_ffn": d_ffn,
        "n_probes": len(probes),
        "probe_file": str(probe_path or PROBES_FILE),
        "relation_groups": {k: len(v) for k, v in relation_groups.items()},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "relation_directions": relation_results,
        "mode_decomposition": mode_results,
        "cross_mode_interaction": cross_results,
        "residual_mapping": mapping_results,
    }

    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=numpy_safe)
    log(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
