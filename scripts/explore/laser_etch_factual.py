#!/usr/bin/env python3
"""Laser Etch Factual — Holographic data extraction and transfer via constrained beams.

The indexing probe (probe_factual_indexing.py) revealed that Q collapses to 1D
within ~500 steps when trained freely. The model finds ONE giant beam direction
rather than learning per-domain angles. This is the flood-lamp problem.

This experiment tests the fix: CONSTRAINED BEAM ETCHING.

Hypothesis: If we hold Q at a known domain-specific angle (from PCA of the source
model's Q behavior), the model can read domain-specific facts from the plate without
collapse. Sequential domain etching should produce a model with multi-angle readout
capability — each domain at its own beam angle, no cross-talk.

Protocol:
  Phase 1: CHARACTERIZE — Find beam angles per domain from source model
    - Run source model on factual prompts
    - PCA the intermediate Q vectors per category
    - Measure angular separation between domain subspaces
    - Identify domain-responsive K rows via projection

  Phase 2: EXTRACT — Build targeted plates
    - Full plate: sign(K, V, O, gate, up) from all rows
    - Domain plates: only rows responsive to each domain's beam angle

  Phase 3: TRANSFER — Train with laser vs flood
    - Condition A: Free Q (flood lamp) — baseline, expect collapse
    - Condition B: Constrained Q (laser) — project Q onto domain subspace after each step
    - Condition C: Sequential laser — train domain by domain, lock Q per phase
    - Measure: factual recall, Q effective dimension, attention sharpness

The laser constraint: after each optimizer step, project Q's weight matrix
onto the subspace spanned by the domain's principal beam components. This
holds the beam DIRECTION fixed while allowing magnitude optimization.

Usage:
    uv run python scripts/explore/laser_etch_factual.py
    uv run python scripts/explore/laser_etch_factual.py --train-steps 300 --n-source-layers 2

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
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

sys.path.insert(0, str(Path(__file__).parent))
from extract_and_train import (
    ExtractedModel, ExtractedAttention, TernaryFrozen, SimpleDataLoader, extract_signs,
    D_MODEL, N_HEADS, N_KV_HEADS, HEAD_DIM, VOCAB_SIZE,
)

DATA_DIR = Path("/Users/mwhitford/data/fractal-bitnet/shards-qwen3")
OUTPUT_DIR = Path("results/holographic-extraction")


# ══════════════════════════════════════════════════════════════════
# Factual probes (same as probe_factual_indexing.py)
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
# Phase 1: CHARACTERIZE — Find beam angles from source model
# ══════════════════════════════════════════════════════════════════


def characterize_beam_angles(
    model_name: str,
    layer_indices: list[int],
    tokenizer,
    device: str,
) -> dict:
    """Run source model on factual prompts, extract Q vectors, PCA per domain.

    Returns:
        {
            "domain_subspaces": {category: {"components": ndarray, "mean": ndarray, "explained_var": list}},
            "angular_separation": {(cat_i, cat_j): cosine_between_subspaces},
            "source_q_vectors": {category: list of Q vectors from source model},
        }
    """
    print("  Loading source model for beam characterization...", file=sys.stderr)
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device,
    )
    model.eval()

    probes = flatten_probes()
    categories = list(FACTUAL_PROBES.keys())

    # Hook to capture Q at specified layers
    # We'll use the FIRST layer in layer_indices (typically L0) for beam characterization
    target_layer_idx = layer_indices[0]
    target_layer = model.model.layers[target_layer_idx]

    captured_qs = []
    probe_categories = []

    def q_hook(module, input, output):
        # For Qwen3, q_proj output shape: (B, L, n_heads * head_dim)
        # We want the LAST position's Q (the prediction position)
        captured_qs.append(output[:, -1, :].detach().cpu())

    hook = target_layer.self_attn.q_proj.register_forward_hook(q_hook)

    print(f"  Running {len(probes)} factual prompts through source model (L{target_layer_idx})...",
          file=sys.stderr)

    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        with torch.no_grad():
            _ = model(input_ids)
        probe_categories.append(probe["category"])

    hook.remove()

    # Stack all Q vectors: (n_probes, q_dim)
    all_qs = torch.cat(captured_qs, dim=0).float().numpy()
    print(f"  Captured {all_qs.shape[0]} Q vectors, dim={all_qs.shape[1]}", file=sys.stderr)

    # PCA per domain
    domain_subspaces = {}
    domain_qs = {}

    for cat in categories:
        cat_indices = [i for i, c in enumerate(probe_categories) if c == cat]
        cat_qs = all_qs[cat_indices]  # (n_cat, q_dim)
        domain_qs[cat] = cat_qs

        # Center
        mean = cat_qs.mean(axis=0)
        centered = cat_qs - mean

        # SVD for PCA
        U, S, Vt = np.linalg.svd(centered, full_matrices=False)
        explained_var = (S ** 2) / (S ** 2).sum()

        # Keep components explaining 90% variance
        cumvar = np.cumsum(explained_var)
        n_components = int(np.searchsorted(cumvar, 0.90)) + 1
        n_components = max(n_components, 2)  # at least 2 for subspace angle measurement

        domain_subspaces[cat] = {
            "components": Vt[:n_components],  # (n_comp, q_dim) — principal directions
            "mean": mean,
            "n_components": n_components,
            "explained_variance": explained_var[:n_components].tolist(),
            "total_variance_captured": float(cumvar[n_components - 1]),
        }
        print(f"    {cat}: {n_components} components, "
              f"var_captured={cumvar[n_components-1]:.3f}", file=sys.stderr)

    # Angular separation between domain subspaces
    # Use principal component (1st eigenvector) cosine as proxy
    angular_separation = {}
    for i, cat_i in enumerate(categories):
        for j, cat_j in enumerate(categories):
            if i < j:
                # Cosine between first principal components
                v_i = domain_subspaces[cat_i]["components"][0]
                v_j = domain_subspaces[cat_j]["components"][0]
                cos = np.dot(v_i, v_j) / (np.linalg.norm(v_i) * np.linalg.norm(v_j))
                angle_deg = np.degrees(np.arccos(np.clip(abs(cos), -1, 1)))
                angular_separation[f"{cat_i}_vs_{cat_j}"] = {
                    "cosine": float(cos),
                    "angle_deg": float(angle_deg),
                }

    # Free source model
    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    return {
        "domain_subspaces": domain_subspaces,
        "angular_separation": angular_separation,
        "source_q_vectors": domain_qs,
        "characterization_layer": target_layer_idx,
    }


# ══════════════════════════════════════════════════════════════════
# Phase 2: EXTRACT — Identify domain-responsive plate regions
# ══════════════════════════════════════════════════════════════════


def identify_responsive_rows(
    domain_subspaces: dict,
    extracted_signs: list[dict],
    layer_idx: int = 0,
    top_fraction: float = 0.25,
) -> dict:
    """For each domain, find which K rows respond to that domain's beam angle.

    A K row "responds" to a beam angle if its sign pattern has high projection
    onto the domain's principal Q components. This is the Bragg condition:
    the stored interference pattern (K row) reconstructs when illuminated by
    the matching reference beam (domain Q direction).

    Returns:
        {category: {"responsive_rows": ndarray, "projections": ndarray, "n_rows": int}}
    """
    # K signs from the target layer: (kv_dim, d_model)
    k_signs = extracted_signs[layer_idx]["k"].float().numpy()
    n_kv_rows = k_signs.shape[0]
    top_n = max(1, int(n_kv_rows * top_fraction))

    domain_rows = {}

    for cat, subspace in domain_subspaces.items():
        components = subspace["components"]  # (n_comp, q_dim=d_model)

        # Project each K row onto the domain subspace
        # K row dot principal components → how strongly does this row respond?
        projections = k_signs @ components.T  # (n_kv_rows, n_comp)
        response_strength = np.linalg.norm(projections, axis=1)  # (n_kv_rows,)

        # Top responding rows
        responsive_idx = np.argsort(response_strength)[-top_n:]

        domain_rows[cat] = {
            "responsive_rows": responsive_idx,
            "response_strength": response_strength[responsive_idx].tolist(),
            "n_rows": len(responsive_idx),
            "mean_response": float(response_strength.mean()),
            "max_response": float(response_strength.max()),
            "top_response": float(response_strength[responsive_idx].mean()),
        }

    # Cross-domain overlap: how many rows are shared between domains?
    overlap_matrix = {}
    categories = list(domain_rows.keys())
    for i, cat_i in enumerate(categories):
        rows_i = set(domain_rows[cat_i]["responsive_rows"])
        for j, cat_j in enumerate(categories):
            rows_j = set(domain_rows[cat_j]["responsive_rows"])
            intersection = len(rows_i & rows_j)
            union = len(rows_i | rows_j)
            overlap_matrix[f"{cat_i}_vs_{cat_j}"] = {
                "intersection": intersection,
                "jaccard": intersection / union if union > 0 else 0,
            }

    return {"domain_rows": domain_rows, "overlap_matrix": overlap_matrix}


# ══════════════════════════════════════════════════════════════════
# Phase 3: TRANSFER — Constrained beam training
# ══════════════════════════════════════════════════════════════════


class BeamConstraint:
    """Projects Q weight back onto a target subspace after each optimizer step.

    This is the "laser" — holds the beam direction fixed while allowing
    magnitude optimization within the subspace. After each step:
        Q_new = Q_proj_onto_subspace + α * Q_residual

    With α=0, the beam is perfectly constrained.
    With α>0, the beam can drift slightly (soft constraint).
    """

    def __init__(self, subspace_components: np.ndarray, strength: float = 1.0):
        """
        Args:
            subspace_components: (n_comp, d_model) — the target beam directions
            strength: 1.0 = hard constraint (project fully), 0.0 = no constraint
        """
        # Build projection matrix: P = V^T @ V (project onto subspace spanned by rows of V)
        V = torch.from_numpy(subspace_components).float()  # (n_comp, d_model)
        self.projector = V.T @ V  # (d_model, d_model) — idempotent projection
        self.strength = strength

    def apply(self, q_proj: nn.Linear):
        """Project Q weight onto subspace. Call after optimizer.step()."""
        with torch.no_grad():
            W = q_proj.weight.data  # (out_features, in_features) = (n_heads*head_dim, d_model)
            P = self.projector.to(W.device)

            # Project each row of W onto the subspace
            W_proj = W @ P  # rows projected

            # Blend: constrained direction + residual
            if self.strength >= 1.0:
                q_proj.weight.data = W_proj
            else:
                W_resid = W - W_proj
                q_proj.weight.data = W_proj + (1.0 - self.strength) * W_resid


class MultiDomainBeamConstraint:
    """Manages beam constraints for sequential domain training.

    Each domain gets its own subspace. During that domain's training phase,
    Q is constrained to that domain's beam angle. Between phases, the
    constraint rotates to the next domain.
    """

    def __init__(self, domain_subspaces: dict, strength: float = 1.0):
        self.constraints = {
            cat: BeamConstraint(sub["components"], strength)
            for cat, sub in domain_subspaces.items()
        }
        self.active_domain: str | None = None

    def set_domain(self, domain: str):
        self.active_domain = domain

    def apply(self, q_proj: nn.Linear):
        if self.active_domain and self.active_domain in self.constraints:
            self.constraints[self.active_domain].apply(q_proj)


def measure_q_diversity(model: ExtractedModel, probes: list[dict],
                        tokenizer, device: str) -> dict:
    """Measure Q effective dimensionality and per-domain angular structure."""
    model.eval()
    all_qs = []
    categories = []

    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        with torch.no_grad():
            # Get Q from first layer
            h = model.embed(input_ids)
            h = model.layers[0].input_norm(h)
            q = model.layers[0].attn.q_proj(h)  # (1, L, q_dim)
            all_qs.append(q[0, -1, :].cpu().numpy())  # last position
        categories.append(probe["category"])

    qs = np.array(all_qs)  # (n_probes, q_dim)

    # Effective dimensionality
    norms = np.linalg.norm(qs, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-8)
    qs_normed = qs / norms
    _, S, _ = np.linalg.svd(qs_normed, full_matrices=False)
    S_sq = S ** 2
    S_sq_norm = S_sq / S_sq.sum()
    eff_dim = 1.0 / (S_sq_norm ** 2).sum()

    # Per-category clustering
    cat_names = list(FACTUAL_PROBES.keys())
    within_sims = []
    between_sims = []
    cos_sim = qs_normed @ qs_normed.T

    for i in range(len(probes)):
        for j in range(i + 1, len(probes)):
            if categories[i] == categories[j]:
                within_sims.append(cos_sim[i, j])
            else:
                between_sims.append(cos_sim[i, j])

    clustering_ratio = (np.mean(within_sims) / np.mean(between_sims)
                        if between_sims and np.mean(between_sims) > 0 else 0)

    return {
        "effective_dim": float(eff_dim),
        "q_magnitude_mean": float(np.mean(norms)),
        "q_magnitude_std": float(np.std(norms)),
        "clustering_ratio": float(clustering_ratio),
        "mean_within_sim": float(np.mean(within_sims)) if within_sims else 0,
        "mean_between_sim": float(np.mean(between_sims)) if between_sims else 0,
    }


def measure_factual_recall(model: ExtractedModel, probes: list[dict],
                           tokenizer, device: str) -> dict:
    """Measure log-prob of correct answer for all probes."""
    model.eval()
    results = []

    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        answer_ids = tokenizer.encode(probe["answer"], add_special_tokens=False)
        if not answer_ids:
            continue
        target_id = answer_ids[0]

        with torch.no_grad():
            logits = model(input_ids)
            log_probs = F.log_softmax(logits[0, -1, :], dim=-1)
            lp = log_probs[target_id].item()
            rank = (torch.argsort(logits[0, -1, :], descending=True) == target_id).nonzero()[0].item() + 1

        results.append({
            "prompt": probe["prompt"],
            "category": probe["category"],
            "log_prob": lp,
            "rank": rank,
        })

    # Per-category summary
    by_cat = defaultdict(list)
    for r in results:
        by_cat[r["category"]].append(r["log_prob"])

    cat_summary = {cat: {"mean_logprob": float(np.mean(lps)), "n": len(lps)}
                   for cat, lps in by_cat.items()}

    return {
        "mean_logprob": float(np.mean([r["log_prob"] for r in results])),
        "mean_rank": float(np.mean([r["rank"] for r in results])),
        "per_category": cat_summary,
        "n_probes": len(results),
    }


def train_condition(
    model: ExtractedModel,
    train_loader: SimpleDataLoader,
    probes: list[dict],
    tokenizer,
    n_steps: int,
    lr: float,
    device: str,
    label: str,
    beam_constraint: BeamConstraint | MultiDomainBeamConstraint | None = None,
    eval_every: int = 100,
) -> dict:
    """Train model under a specific beam constraint condition.

    Returns training history + final Q diversity + factual recall.
    """
    model = model.to(device)
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=lr, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_steps)

    history = []
    t0 = time.time()

    for step in range(1, n_steps + 1):
        model.train()
        input_ids, targets = train_loader.next_batch()
        input_ids = input_ids.to(device)
        targets = targets.to(device)

        logits = model(input_ids)
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
        optimizer.step()
        scheduler.step()

        # Apply beam constraint AFTER optimizer step
        if beam_constraint is not None:
            for layer in model.layers:
                if isinstance(beam_constraint, MultiDomainBeamConstraint):
                    beam_constraint.apply(layer.attn.q_proj)
                else:
                    beam_constraint.apply(layer.attn.q_proj)

        if step % eval_every == 0 or step == 1:
            q_div = measure_q_diversity(model, probes, tokenizer, device)
            elapsed = time.time() - t0
            record = {
                "step": step,
                "loss": loss.item(),
                "effective_dim": q_div["effective_dim"],
                "clustering_ratio": q_div["clustering_ratio"],
                "q_magnitude": q_div["q_magnitude_mean"],
                "elapsed": elapsed,
            }
            history.append(record)
            print(f"  [{label}] step {step:>4} | loss {loss.item():.2f} | "
                  f"eff_dim={q_div['effective_dim']:.2f} | "
                  f"cluster={q_div['clustering_ratio']:.3f} | "
                  f"Q_mag={q_div['q_magnitude_mean']:.1f}", file=sys.stderr)

    # Final measurements
    final_q = measure_q_diversity(model, probes, tokenizer, device)
    final_recall = measure_factual_recall(model, probes, tokenizer, device)

    return {
        "label": label,
        "history": history,
        "final_q_diversity": final_q,
        "final_recall": final_recall,
    }


def train_sequential_laser(
    model: ExtractedModel,
    train_loader: SimpleDataLoader,
    probes: list[dict],
    tokenizer,
    domain_subspaces: dict,
    n_steps_per_domain: int,
    lr: float,
    device: str,
    label: str,
    eval_every: int = 50,
) -> dict:
    """Sequential domain-by-domain training with rotating beam constraint.

    For each domain:
      1. Set beam constraint to that domain's subspace
      2. Train for n_steps on general data (constraint forces relevant extraction)
      3. Rotate to next domain

    This is the holographic recording protocol: one exposure per beam angle.
    """
    model = model.to(device)
    categories = list(FACTUAL_PROBES.keys())
    multi_constraint = MultiDomainBeamConstraint(domain_subspaces, strength=1.0)

    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=lr, weight_decay=0.01)
    total_steps = n_steps_per_domain * len(categories)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_steps)

    history = []
    t0 = time.time()
    global_step = 0

    for domain_idx, domain in enumerate(categories):
        multi_constraint.set_domain(domain)
        print(f"\n  [{label}] === DOMAIN: {domain} (beam angle #{domain_idx+1}/{len(categories)}) ===",
              file=sys.stderr)

        for step in range(1, n_steps_per_domain + 1):
            global_step += 1
            model.train()
            input_ids, targets = train_loader.next_batch()
            input_ids = input_ids.to(device)
            targets = targets.to(device)

            logits = model(input_ids)
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
            optimizer.step()
            scheduler.step()

            # Apply domain-specific beam constraint
            for layer in model.layers:
                multi_constraint.apply(layer.attn.q_proj)

            if step % eval_every == 0 or step == 1:
                q_div = measure_q_diversity(model, probes, tokenizer, device)
                record = {
                    "global_step": global_step,
                    "domain": domain,
                    "domain_step": step,
                    "loss": loss.item(),
                    "effective_dim": q_div["effective_dim"],
                    "clustering_ratio": q_div["clustering_ratio"],
                    "q_magnitude": q_div["q_magnitude_mean"],
                    "elapsed": time.time() - t0,
                }
                history.append(record)
                print(f"  [{label}/{domain}] step {step:>3} | loss {loss.item():.2f} | "
                      f"eff_dim={q_div['effective_dim']:.2f} | "
                      f"cluster={q_div['clustering_ratio']:.3f}", file=sys.stderr)

    # Final measurements
    final_q = measure_q_diversity(model, probes, tokenizer, device)
    final_recall = measure_factual_recall(model, probes, tokenizer, device)

    return {
        "label": label,
        "history": history,
        "final_q_diversity": final_q,
        "final_recall": final_recall,
        "domains_trained": categories,
        "steps_per_domain": n_steps_per_domain,
    }


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="Laser etch factual experiment")
    parser.add_argument("--source", default="Qwen/Qwen3-14B")
    parser.add_argument("--train-steps", type=int, default=500,
                        help="Steps per condition (A, B) or total for C")
    parser.add_argument("--n-layers", type=int, default=4)
    parser.add_argument("--layer-stride", type=int, default=10)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--constraint-strength", type=float, default=1.0,
                        help="1.0=hard laser, 0.5=soft constraint, 0.0=free beam")
    parser.add_argument("--top-fraction", type=float, default=0.25,
                        help="Fraction of K rows to consider domain-responsive")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    layer_indices = list(range(0, 40, args.layer_stride))[:args.n_layers]
    probes = flatten_probes()

    tokenizer = AutoTokenizer.from_pretrained(args.source)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"\n{'═'*70}", file=sys.stderr)
    print(f"  LASER ETCH FACTUAL — Holographic Data Transfer", file=sys.stderr)
    print(f"{'═'*70}", file=sys.stderr)
    print(f"  Source:      {args.source}", file=sys.stderr)
    print(f"  Layers:      {layer_indices}", file=sys.stderr)
    print(f"  Steps/cond:  {args.train_steps}", file=sys.stderr)
    print(f"  Constraint:  {args.constraint_strength}", file=sys.stderr)
    print(f"  Probes:      {len(probes)} in {len(FACTUAL_PROBES)} categories", file=sys.stderr)
    print(f"{'═'*70}\n", file=sys.stderr)

    # ══════════════════════════════════════════════════════════════
    # Phase 1: CHARACTERIZE — Find beam angles from source model
    # ══════════════════════════════════════════════════════════════
    print("Phase 1: CHARACTERIZE — Finding domain beam angles...\n", file=sys.stderr)

    beam_info = characterize_beam_angles(args.source, layer_indices, tokenizer, args.device)
    domain_subspaces = beam_info["domain_subspaces"]

    print(f"\n  Angular separation between domains:", file=sys.stderr)
    print(f"  {'Pair':<25} {'Cosine':>8} {'Angle°':>8}", file=sys.stderr)
    print(f"  {'─'*25} {'─'*8} {'─'*8}", file=sys.stderr)
    for pair, info in beam_info["angular_separation"].items():
        print(f"  {pair:<25} {info['cosine']:>8.4f} {info['angle_deg']:>8.1f}°", file=sys.stderr)

    # ══════════════════════════════════════════════════════════════
    # Phase 2: EXTRACT — Signs + responsive row identification
    # ══════════════════════════════════════════════════════════════
    print(f"\nPhase 2: EXTRACT — Signs + domain-responsive rows...\n", file=sys.stderr)

    extracted_signs = extract_signs(args.source, layer_indices, device=args.device)
    intermediate = extracted_signs[0]["gate"].shape[0]

    row_info = identify_responsive_rows(
        domain_subspaces, extracted_signs, layer_idx=0, top_fraction=args.top_fraction
    )

    print(f"  Domain-responsive K rows (top {args.top_fraction:.0%}):", file=sys.stderr)
    print(f"  {'Domain':<12} {'N rows':>8} {'Mean resp':>10} {'Max resp':>10}", file=sys.stderr)
    print(f"  {'─'*12} {'─'*8} {'─'*10} {'─'*10}", file=sys.stderr)
    for cat, info in row_info["domain_rows"].items():
        print(f"  {cat:<12} {info['n_rows']:>8} {info['mean_response']:>10.3f} "
              f"{info['max_response']:>10.3f}", file=sys.stderr)

    print(f"\n  Cross-domain row overlap (Jaccard):", file=sys.stderr)
    categories = list(FACTUAL_PROBES.keys())
    print(f"  {'':>12}", end='', file=sys.stderr)
    for c in categories:
        print(f"{c[:5]:>8}", end='', file=sys.stderr)
    print(file=sys.stderr)
    for ci in categories:
        print(f"  {ci:<12}", end='', file=sys.stderr)
        for cj in categories:
            key = f"{ci}_vs_{cj}"
            j = row_info["overlap_matrix"].get(key, {}).get("jaccard", 0)
            print(f"{j:>8.3f}", end='', file=sys.stderr)
        print(file=sys.stderr)

    # ══════════════════════════════════════════════════════════════
    # Phase 3: TRANSFER — Three conditions
    # ══════════════════════════════════════════════════════════════
    print(f"\n{'─'*70}", file=sys.stderr)
    print(f"  Phase 3: TRANSFER — Laser vs Flood comparison", file=sys.stderr)
    print(f"{'─'*70}\n", file=sys.stderr)

    # Rebuild domain subspaces as numpy arrays for constraints
    subspaces_for_constraint = {
        cat: {"components": sub["components"]}
        for cat, sub in domain_subspaces.items()
    }

    # ── Condition A: Free beam (flood lamp) — expect Q collapse ──
    print("  ═══ Condition A: FREE BEAM (flood lamp baseline) ═══\n", file=sys.stderr)

    model_a = ExtractedModel(
        n_layers=len(layer_indices), d_model=D_MODEL, n_heads=N_HEADS,
        n_kv_heads=N_KV_HEADS, head_dim=HEAD_DIM, intermediate=intermediate,
        vocab_size=VOCAB_SIZE, layer_signs=extracted_signs,
    )
    loader_a = SimpleDataLoader(DATA_DIR, 2, 256, shard_start=0, shard_end=4, seed=42)
    result_a = train_condition(
        model_a, loader_a, probes, tokenizer, args.train_steps,
        args.lr, args.device, "FREE", beam_constraint=None,
    )
    del model_a; gc.collect()

    # ── Condition B: Constrained beam (laser — geography angle for all) ──
    # Use the COMBINED subspace of all domains as the constraint
    # This prevents collapse while allowing multi-domain reading
    print("\n  ═══ Condition B: CONSTRAINED BEAM (multi-domain laser) ═══\n", file=sys.stderr)

    # Combine all domain principal components into one constraint subspace
    all_components = np.vstack([sub["components"][:2] for sub in domain_subspaces.values()])
    # Orthogonalize via SVD
    U, S, Vt = np.linalg.svd(all_components, full_matrices=False)
    # Keep top components that span the multi-domain subspace
    cumvar = np.cumsum(S**2) / (S**2).sum()
    n_keep = int(np.searchsorted(cumvar, 0.95)) + 1
    combined_subspace = Vt[:n_keep]
    print(f"  Combined multi-domain subspace: {n_keep} components "
          f"(from {all_components.shape[0]} raw)\n", file=sys.stderr)

    combined_constraint = BeamConstraint(combined_subspace, strength=args.constraint_strength)

    model_b = ExtractedModel(
        n_layers=len(layer_indices), d_model=D_MODEL, n_heads=N_HEADS,
        n_kv_heads=N_KV_HEADS, head_dim=HEAD_DIM, intermediate=intermediate,
        vocab_size=VOCAB_SIZE, layer_signs=extracted_signs,
    )
    loader_b = SimpleDataLoader(DATA_DIR, 2, 256, shard_start=0, shard_end=4, seed=42)
    result_b = train_condition(
        model_b, loader_b, probes, tokenizer, args.train_steps,
        args.lr, args.device, "CONSTRAINED", beam_constraint=combined_constraint,
    )
    del model_b; gc.collect()

    # ── Condition C: Sequential laser (domain-by-domain) ──
    print("\n  ═══ Condition C: SEQUENTIAL LASER (domain rotation) ═══\n", file=sys.stderr)

    steps_per_domain = args.train_steps // len(categories)

    model_c = ExtractedModel(
        n_layers=len(layer_indices), d_model=D_MODEL, n_heads=N_HEADS,
        n_kv_heads=N_KV_HEADS, head_dim=HEAD_DIM, intermediate=intermediate,
        vocab_size=VOCAB_SIZE, layer_signs=extracted_signs,
    )
    loader_c = SimpleDataLoader(DATA_DIR, 2, 256, shard_start=0, shard_end=4, seed=42)
    result_c = train_sequential_laser(
        model_c, loader_c, probes, tokenizer, subspaces_for_constraint,
        n_steps_per_domain=steps_per_domain, lr=args.lr, device=args.device,
        label="SEQUENTIAL",
    )
    del model_c; gc.collect()

    # ══════════════════════════════════════════════════════════════
    # Results comparison
    # ══════════════════════════════════════════════════════════════
    print(f"\n{'═'*70}", file=sys.stderr)
    print(f"  RESULTS — LASER vs FLOOD COMPARISON", file=sys.stderr)
    print(f"{'═'*70}\n", file=sys.stderr)

    conditions = [
        ("A: Free (flood)", result_a),
        ("B: Constrained (laser)", result_b),
        ("C: Sequential (rotate)", result_c),
    ]

    print(f"  {'Condition':<26} {'EffDim':>8} {'Cluster':>9} {'LogProb':>9} "
          f"{'Rank':>8} {'Q_Mag':>8}", file=sys.stderr)
    print(f"  {'─'*26} {'─'*8} {'─'*9} {'─'*9} {'─'*8} {'─'*8}", file=sys.stderr)

    for name, result in conditions:
        qd = result["final_q_diversity"]
        rc = result["final_recall"]
        print(f"  {name:<26} {qd['effective_dim']:>8.2f} {qd['clustering_ratio']:>9.3f} "
              f"{rc['mean_logprob']:>9.2f} {rc['mean_rank']:>8.0f} "
              f"{qd['q_magnitude_mean']:>8.1f}", file=sys.stderr)

    # Per-category recall comparison
    print(f"\n  Per-category mean log-prob:", file=sys.stderr)
    print(f"  {'Category':<12}", end='', file=sys.stderr)
    for name, _ in conditions:
        print(f"  {name[:12]:>12}", end='', file=sys.stderr)
    print(file=sys.stderr)
    print(f"  {'─'*12}", end='', file=sys.stderr)
    for _ in conditions:
        print(f"  {'─'*12}", end='', file=sys.stderr)
    print(file=sys.stderr)

    for cat in categories:
        print(f"  {cat:<12}", end='', file=sys.stderr)
        for _, result in conditions:
            cat_lp = result["final_recall"]["per_category"].get(cat, {}).get("mean_logprob", 0)
            print(f"  {cat_lp:>12.2f}", end='', file=sys.stderr)
        print(file=sys.stderr)

    # ── Collapse prevention verdict ──
    print(f"\n  ═══ COLLAPSE PREVENTION VERDICT ═══", file=sys.stderr)
    dim_a = result_a["final_q_diversity"]["effective_dim"]
    dim_b = result_b["final_q_diversity"]["effective_dim"]
    dim_c = result_c["final_q_diversity"]["effective_dim"]

    if dim_b > dim_a * 1.5:
        print(f"  ✅ Laser PREVENTS Q collapse: eff_dim {dim_a:.2f} → {dim_b:.2f} "
              f"({dim_b/dim_a:.1f}× more diverse)", file=sys.stderr)
    else:
        print(f"  ⚠️  Laser shows modest effect: eff_dim {dim_a:.2f} → {dim_b:.2f}", file=sys.stderr)

    if dim_c > dim_a * 1.5:
        print(f"  ✅ Sequential laser maintains diversity: eff_dim={dim_c:.2f}", file=sys.stderr)
    else:
        print(f"  ⚠️  Sequential shows: eff_dim={dim_c:.2f}", file=sys.stderr)

    # ── Recall comparison ──
    lp_a = result_a["final_recall"]["mean_logprob"]
    lp_b = result_b["final_recall"]["mean_logprob"]
    lp_c = result_c["final_recall"]["mean_logprob"]
    best = min([(lp_a, "A"), (lp_b, "B"), (lp_c, "C")], key=lambda x: abs(x[0]))

    print(f"\n  Factual recall (higher log-prob = better):", file=sys.stderr)
    print(f"    A (flood):      {lp_a:.2f}", file=sys.stderr)
    print(f"    B (laser):      {lp_b:.2f}", file=sys.stderr)
    print(f"    C (sequential): {lp_c:.2f}", file=sys.stderr)

    # ══════════════════════════════════════════════════════════════
    # Save results
    # ══════════════════════════════════════════════════════════════

    # Convert numpy arrays to lists for JSON serialization
    def serialize_subspaces(subs):
        out = {}
        for cat, sub in subs.items():
            out[cat] = {
                "n_components": sub["n_components"],
                "explained_variance": sub["explained_variance"],
                "total_variance_captured": sub["total_variance_captured"],
                "mean_norm": float(np.linalg.norm(sub["mean"])),
            }
        return out

    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "config": {
            "source_model": args.source,
            "layer_indices": layer_indices,
            "train_steps": args.train_steps,
            "constraint_strength": args.constraint_strength,
            "top_fraction": args.top_fraction,
            "n_probes": len(probes),
        },
        "phase1_characterization": {
            "layer": beam_info["characterization_layer"],
            "domain_subspaces": serialize_subspaces(domain_subspaces),
            "angular_separation": beam_info["angular_separation"],
            "combined_subspace_dim": int(n_keep),
        },
        "phase2_extraction": {
            "domain_rows": {cat: {k: v for k, v in info.items() if k != "responsive_rows"}
                           for cat, info in row_info["domain_rows"].items()},
            "overlap_matrix": row_info["overlap_matrix"],
        },
        "phase3_transfer": {
            "condition_a_free": result_a,
            "condition_b_constrained": result_b,
            "condition_c_sequential": result_c,
        },
        "summary": {
            "q_collapse_prevented": dim_b > dim_a * 1.5,
            "effective_dims": {"free": dim_a, "constrained": dim_b, "sequential": dim_c},
            "recall_logprobs": {"free": lp_a, "constrained": lp_b, "sequential": lp_c},
        },
    }

    json_path = args.output_dir / "laser_etch_results.json"
    json_path.write_text(json.dumps(output, indent=2, default=str))
    print(f"\n  💾 Results: {json_path}", file=sys.stderr)
    print(f"{'═'*70}\n", file=sys.stderr)


if __name__ == "__main__":
    main()
