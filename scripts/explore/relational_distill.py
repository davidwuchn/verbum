#!/usr/bin/env python3
"""Relational Distillation — Use cross-model universal geometry as training loss.

The tomography probe (session 105) revealed:
  - RSA between Qwen3-14B and OLMo-2-13B: r=0.7448 (strong!)
  - Direct alignment: cos≈0 (different coordinate systems)
  - Category cohesion agreement: r=0.98

This means: both models organize facts the SAME WAY (topology) but in
DIFFERENT COORDINATES. We can't transplant signs directly, but we CAN
use the shared topology as a training loss.

The relational loss forces the student model to match the universal
factual geometry without constraining which directions it uses.
"France must be near Germany" — regardless of which axis they're on.

Protocol:
  1. Extract universal RDM from both source models (average of their fact×fact
     similarity matrices — the AGREED geometry)
  2. Build extracted plate model (Qwen3-14B signs, frozen plates, trainable beam)
  3. Train condition A: next-token only (Dolma shards)
  4. Train condition B: next-token + relational loss (periodic geometry alignment)
  5. Compare: factual recall, Q diversity, category clustering

The relational loss:
  L_rel = MSE(student_RDM, universal_RDM)
  Where RDM[i,j] = cos(hidden[fact_i], hidden[fact_j])

This is coordinate-free distillation — works across any architecture.

Level 2 (structural template) relational loss:
  L_template = MSE(student_template_RDM, universal_template_RDM)
  Targets EARLY layers (L0-L10) where structural templates cluster.
  Cross-domain same-template pairs should cluster (cos=0.95+ observed).

Combined:
  L_total = L_next_token + λ_domain * L_domain + λ_template * L_template

Usage:
    uv run python scripts/explore/relational_distill.py
    uv run python scripts/explore/relational_distill.py --train-steps 500 --rel-lambda 0.1
    uv run python scripts/explore/relational_distill.py --rel-every 10
    uv run python scripts/explore/relational_distill.py --skip-rdm-extraction --skip-condition-a --template-lambda 0.05

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
    ExtractedModel, SimpleDataLoader, extract_signs,
    D_MODEL, N_HEADS, N_KV_HEADS, HEAD_DIM, VOCAB_SIZE,
)

DATA_DIR = Path("/Users/mwhitford/data/fractal-bitnet/shards-qwen3")
OUTPUT_DIR = Path("results/holographic-extraction")

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
# Level 2: Structural template categorization
# ══════════════════════════════════════════════════════════════════

# Map each probe index to its structural template.
# Probes sharing a template should cluster regardless of domain.
# Derived from session 105 analysis: "the_X_of_Y_is" cross-domain cos=0.95+

TEMPLATE_LABELS = {
    # "The X of Y is" — strongest Level 2 signal (cross-domain cos=0.67, pairs at 0.95+)
    "the_X_of_Y_is": [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 14, 16, 39],
    # "X was VERBed by Y" — attribution template
    "X_was_VERBed_by_Y": [17, 18, 23, 28, 29],
    # "X is in/located in Y" — spatial template
    "X_is_in_Y": [24, 25, 26],
    # "X has N Y" — possession/count template
    "X_has_N_Y": [35, 41, 42],
    # "X equals/is Y" — identity/equation template
    "X_equals_Y": [38, 40, 44],
    # "There are N X in a Y" — quantified existence
    "there_are_N_in": [33, 34],
    # "The superlative X is Y" — extremal template
    "superlative_X_is": [8, 9, 10, 11],
    # "X VERB Y" — simple transitive
    "X_VERB_Y": [19, 22, 30, 32, 36, 37],
}


def build_template_rdm(universal_rdm: dict[int, np.ndarray], layer: int) -> np.ndarray:
    """Build a Level 2 target RDM from the universal RDM.

    For template loss, we want same-template probes to have HIGH similarity
    and different-template probes to have the OBSERVED between-template similarity.

    Returns the full 46×46 RDM with template structure emphasized.
    The template RDM is the universal RDM itself (it already contains the
    template clustering signal), but we can optionally boost same-template
    pairs to make the loss sharper.
    """
    # Use the universal RDM directly — it already encodes template structure
    # at L0 (the strongest level). The relational loss will push the student
    # toward this geometry which naturally contains template clustering.
    return universal_rdm[layer].copy()


def compute_template_metrics(student_rdm: np.ndarray, probes: list[dict]) -> dict:
    """Compute Level 2 template clustering metrics from a student RDM."""
    categories = [p["category"] for p in probes]

    template_within = []
    template_cross_domain = []
    between_template = []

    template_indices_all = set()
    for indices in TEMPLATE_LABELS.values():
        template_indices_all.update(indices)

    for template, indices in TEMPLATE_LABELS.items():
        if len(indices) < 2:
            continue
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                idx_i, idx_j = indices[i], indices[j]
                if idx_i < len(probes) and idx_j < len(probes):
                    sim = student_rdm[idx_i, idx_j]
                    template_within.append(sim)
                    if categories[idx_i] != categories[idx_j]:
                        template_cross_domain.append(sim)

    # Between-template pairs
    templates_list = list(TEMPLATE_LABELS.values())
    for i in range(len(templates_list)):
        for j in range(i + 1, len(templates_list)):
            for idx_i in templates_list[i]:
                for idx_j in templates_list[j]:
                    if idx_i < len(probes) and idx_j < len(probes):
                        between_template.append(student_rdm[idx_i, idx_j])

    return {
        "mean_within_template": float(np.mean(template_within)) if template_within else 0,
        "mean_cross_domain_template": float(np.mean(template_cross_domain)) if template_cross_domain else 0,
        "mean_between_template": float(np.mean(between_template)) if between_template else 0,
        "template_ratio": (float(np.mean(template_within)) / float(np.mean(between_template))
                          if between_template and np.mean(between_template) > 0 else 0),
        "cross_domain_ratio": (float(np.mean(template_cross_domain)) / float(np.mean(between_template))
                              if between_template and template_cross_domain and np.mean(between_template) > 0 else 0),
    }


# ══════════════════════════════════════════════════════════════════
# Phase 1: Extract universal RDM from source models
# ══════════════════════════════════════════════════════════════════

MODELS = {
    "qwen3-14b": "Qwen/Qwen3-14B",
    "olmo-2-13b": "allenai/OLMo-2-1124-13B",
}


def extract_rdm_from_model(
    model_name: str,
    target_layers: list[int],
    probes: list[dict],
    device: str,
) -> dict[int, np.ndarray]:
    """Extract fact×fact RDM at each layer from a source model.

    Returns: {layer_idx: rdm_matrix (n_probes, n_probes)}
    """
    print(f"  Loading {model_name}...", file=sys.stderr)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device,
    )
    model.eval()

    layers = model.model.layers

    # Hook to capture hidden states
    hidden_captures = {li: [] for li in target_layers}
    hooks = []

    for li in target_layers:
        def make_hook(layer_idx):
            def hook_fn(module, input, output):
                if isinstance(output, tuple):
                    h = output[0]
                else:
                    h = output
                hidden_captures[layer_idx].append(h[:, -1, :].detach().cpu().float())
            return hook_fn
        h = layers[li].register_forward_hook(make_hook(li))
        hooks.append(h)

    # Run probes
    print(f"  Running {len(probes)} probes...", file=sys.stderr)
    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        with torch.no_grad():
            _ = model(input_ids)

    for h in hooks:
        h.remove()

    # Build RDMs
    rdms = {}
    for li in target_layers:
        hs = torch.cat(hidden_captures[li], dim=0).numpy()  # (n_probes, d_model)
        # Normalize for cosine similarity
        norms = np.linalg.norm(hs, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-8)
        hs_norm = hs / norms
        rdms[li] = hs_norm @ hs_norm.T  # (n_probes, n_probes) cosine sim

    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    return rdms


def build_universal_rdm(
    model_keys: list[str],
    target_layers: list[int],
    probes: list[dict],
    device: str,
) -> dict[int, np.ndarray]:
    """Build the universal RDM by averaging across source models.

    Returns: {layer_idx: universal_rdm (n_probes, n_probes)}
    """
    all_rdms = {li: [] for li in target_layers}

    for mk in model_keys:
        model_name = MODELS[mk]
        print(f"\n  ─── Extracting RDM from {mk} ───", file=sys.stderr)
        rdms = extract_rdm_from_model(model_name, target_layers, probes, device)
        for li, rdm in rdms.items():
            all_rdms[li].append(rdm)

    # Average across models
    universal = {}
    for li in target_layers:
        stacked = np.stack(all_rdms[li])  # (n_models, n_probes, n_probes)
        universal[li] = stacked.mean(axis=0)  # (n_probes, n_probes)
        # Also compute agreement (std across models — lower = more universal)
        agreement = 1.0 - stacked.std(axis=0).mean()
        print(f"  L{li}: universal RDM built (agreement={agreement:.4f})", file=sys.stderr)

    return universal


# ══════════════════════════════════════════════════════════════════
# Relational Loss
# ══════════════════════════════════════════════════════════════════


class RelationalLoss(nn.Module):
    """Compute relational loss between student's geometry and universal target.

    L_rel = MSE(student_RDM, target_RDM)
    Where RDM[i,j] = cos(hidden_state[fact_i], hidden_state[fact_j])

    Only uses upper triangle (avoids diagonal = 1.0 always).
    """

    def __init__(self, target_rdms: dict[int, np.ndarray], layer_weights: dict[int, float] | None = None,
                 residual: bool = False):
        super().__init__()
        # Register target RDMs as buffers (non-trainable, move with model)
        self.target_layers = sorted(target_rdms.keys())
        self.n_probes = list(target_rdms.values())[0].shape[0]
        self.residual = residual

        for li in self.target_layers:
            rdm_tensor = torch.from_numpy(target_rdms[li]).float()
            self.register_buffer(f"target_rdm_{li}", rdm_tensor)

        # Upper triangle indices (exclude diagonal)
        triu = torch.triu_indices(self.n_probes, self.n_probes, offset=1)
        self.register_buffer("triu_row", triu[0])
        self.register_buffer("triu_col", triu[1])

        # Layer weights (default: equal)
        if layer_weights:
            self.layer_weights = layer_weights
        else:
            self.layer_weights = {li: 1.0 for li in self.target_layers}

    def forward(self, student_hidden_states: dict[int, torch.Tensor],
                probe_indices: list[int] | None = None) -> torch.Tensor:
        """
        Args:
            student_hidden_states: {layer_idx: tensor (n_subset, d_model)}
            probe_indices: if provided, indices into the full RDM for this subset.
                          Used when subsampling probes for memory efficiency.

        Returns:
            Scalar relational loss
        """
        total_loss = torch.tensor(0.0, device=self.triu_row.device)

        for li in self.target_layers:
            if li not in student_hidden_states:
                continue

            hs = student_hidden_states[li]  # (n_subset, d_model)
            n_sub = hs.shape[0]

            # Normalize
            hs_norm = F.normalize(hs, dim=-1)

            # Student RDM
            student_rdm = hs_norm @ hs_norm.T  # (n_subset, n_subset)

            # If residual mode: subtract mean from student RDM too
            if self.residual:
                student_rdm = student_rdm - student_rdm.mean()

            # Get target RDM (full or subset)
            target_rdm_full = getattr(self, f"target_rdm_{li}")
            if probe_indices is not None and len(probe_indices) < self.n_probes:
                # Extract the sub-matrix corresponding to selected probes
                idx = torch.tensor(probe_indices, device=target_rdm_full.device)
                target_sub = target_rdm_full[idx][:, idx]  # (n_subset, n_subset)
            else:
                target_sub = target_rdm_full

            # Upper triangle of the subset
            triu = torch.triu_indices(n_sub, n_sub, offset=1, device=student_rdm.device)
            student_flat = student_rdm[triu[0], triu[1]]
            target_flat = target_sub[triu[0], triu[1]]

            # MSE loss
            layer_loss = F.mse_loss(student_flat, target_flat)
            total_loss = total_loss + self.layer_weights[li] * layer_loss

        return total_loss


# ══════════════════════════════════════════════════════════════════
# Training with relational loss
# ══════════════════════════════════════════════════════════════════


def collect_student_hidden_states(
    model: ExtractedModel,
    probes: list[dict],
    tokenizer,
    target_layers: list[int],
    device: str,
) -> dict[int, torch.Tensor]:
    """Run factual probes through student model, collect hidden states per layer.

    Returns: {layer_idx: tensor (n_probes, d_model)} — WITH gradients attached.
    """
    # We need to run each probe individually (different lengths)
    # Collect last-position hidden states at each target layer
    layer_states = {li: [] for li in target_layers}

    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)

        # Manual forward to capture intermediates
        h = model.embed(input_ids)
        for layer_idx, layer in enumerate(model.layers):
            h = h + layer.attn(layer.input_norm(h))
            h = h + layer.ffn(layer.post_attn_norm(h))

            # Map model's sequential layer index to source layer index
            # Our model has N layers corresponding to target_layers
            if layer_idx < len(target_layers):
                source_layer = target_layers[layer_idx]
                if source_layer in layer_states:
                    layer_states[source_layer].append(h[:, -1, :])  # (1, d_model)

    # Stack into tensors (n_probes, d_model)
    result = {}
    for li, states in layer_states.items():
        if states:
            result[li] = torch.cat(states, dim=0)  # (n_probes, d_model)

    return result


def measure_factual_recall(model, probes, tokenizer, device):
    """Quick factual recall measurement."""
    model.eval()
    log_probs = []
    ranks = []

    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        answer_ids = tokenizer.encode(probe["answer"], add_special_tokens=False)
        if not answer_ids:
            continue
        target_id = answer_ids[0]

        with torch.no_grad():
            logits = model(input_ids)
            lp = F.log_softmax(logits[0, -1, :], dim=-1)
            log_probs.append(lp[target_id].item())
            rank = (torch.argsort(logits[0, -1, :], descending=True) == target_id).nonzero()[0].item() + 1
            ranks.append(rank)

    by_cat = defaultdict(list)
    categories = [p["category"] for p in probes]
    for lp, cat in zip(log_probs, categories):
        by_cat[cat].append(lp)

    return {
        "mean_logprob": float(np.mean(log_probs)),
        "mean_rank": float(np.mean(ranks)),
        "per_category": {cat: float(np.mean(lps)) for cat, lps in by_cat.items()},
    }


def measure_student_rsa(model, probes, tokenizer, target_layers, device):
    """Measure how well student's geometry matches universal target."""
    model.eval()
    with torch.no_grad():
        hs = collect_student_hidden_states(model, probes, tokenizer, target_layers, device)

    rsa_scores = {}
    for li, h in hs.items():
        h_norm = F.normalize(h, dim=-1)
        student_rdm = (h_norm @ h_norm.T).cpu().numpy()
        rsa_scores[li] = student_rdm

    return rsa_scores


def train_condition(
    model: ExtractedModel,
    train_loader: SimpleDataLoader,
    probes: list[dict],
    tokenizer,
    target_layers: list[int],
    n_steps: int,
    lr: float,
    device: str,
    label: str,
    rel_loss_fn: RelationalLoss | None = None,
    rel_lambda: float = 0.1,
    rel_every: int = 5,
    eval_every: int = 100,
    template_loss_fn: RelationalLoss | None = None,
    template_lambda: float = 0.0,
    eval_probes: list[dict] | None = None,
) -> dict:
    """Train with optional relational loss (Level 1 domain + Level 2 template).

    Every `rel_every` steps: compute relational losses on probes and backprop.
    Level 1 (domain): forces category clustering at deep layers.
    Level 2 (template): forces structural template clustering at early layers.

    Args:
        probes: probes used for relational loss (can be crystal seed 311 probes)
        eval_probes: probes used for factual recall measurement (always 46 factual probes)
    """
    if eval_probes is None:
        eval_probes = probes
    model = model.to(device)
    if rel_loss_fn is not None:
        rel_loss_fn = rel_loss_fn.to(device)
    if template_loss_fn is not None:
        template_loss_fn = template_loss_fn.to(device)

    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=lr, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_steps)

    history = []
    t0 = time.time()

    for step in range(1, n_steps + 1):
        model.train()

        # ── Next-token loss (every step) ──
        input_ids, targets = train_loader.next_batch()
        input_ids = input_ids.to(device)
        targets = targets.to(device)

        logits = model(input_ids)
        loss_nt = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))

        total_loss = loss_nt
        rel_loss_val = 0.0

        # ── Relational loss (every rel_every steps) ──
        if (rel_loss_fn is not None or template_loss_fn is not None) and step % rel_every == 0:
            # Subsample probes if too many (avoid OOM with 311 forward passes + grad)
            rel_batch_size = min(50, len(probes))
            if len(probes) > rel_batch_size:
                rng = np.random.default_rng(step)
                probe_indices = rng.choice(len(probes), rel_batch_size, replace=False)
                probe_subset = [probes[i] for i in sorted(probe_indices)]
            else:
                probe_subset = probes
                probe_indices = list(range(len(probes)))

            student_hs = collect_student_hidden_states(
                model, probe_subset, tokenizer, target_layers, device
            )
            # Level 1: Domain geometry loss (on subset)
            if rel_loss_fn is not None:
                loss_rel = rel_loss_fn(student_hs, probe_indices=probe_indices)
                total_loss = total_loss + rel_lambda * loss_rel
                rel_loss_val = loss_rel.item()
            # Level 2: Template geometry loss (on subset)
            if template_loss_fn is not None and template_lambda > 0:
                loss_tmpl = template_loss_fn(student_hs, probe_indices=probe_indices)
                total_loss = total_loss + template_lambda * loss_tmpl
                rel_loss_val += loss_tmpl.item()  # combine for logging

        optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
        optimizer.step()
        scheduler.step()

        if step % eval_every == 0 or step == 1:
            elapsed = time.time() - t0
            tok_per_sec = step * 2 * 256 / elapsed

            record = {
                "step": step,
                "loss_nt": loss_nt.item(),
                "loss_rel": rel_loss_val,
                "loss_total": total_loss.item(),
                "elapsed": elapsed,
                "tok_per_sec": tok_per_sec,
            }
            history.append(record)
            rel_str = f" | rel={rel_loss_val:.4f}" if rel_loss_fn else ""
            print(f"  [{label}] step {step:>4} | nt={loss_nt.item():.2f}{rel_str} | "
                  f"{tok_per_sec:.0f} tok/s", file=sys.stderr)

    # ── Final evaluation ──
    model.eval()
    final_recall = measure_factual_recall(model, eval_probes, tokenizer, device)

    # Measure final student RDM and compare to universal
    final_rdms = measure_student_rsa(model, probes, tokenizer, target_layers, device)

    # Measure template metrics (Level 2)
    template_metrics = {}
    for li, rdm in final_rdms.items():
        template_metrics[str(li)] = compute_template_metrics(rdm, probes)

    return {
        "label": label,
        "history": history,
        "final_recall": final_recall,
        "final_student_rdms": {str(li): rdm.tolist() for li, rdm in final_rdms.items()},
        "template_metrics": template_metrics,
    }


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="Relational distillation experiment")
    parser.add_argument("--source", default="Qwen/Qwen3-14B")
    parser.add_argument("--train-steps", type=int, default=500)
    parser.add_argument("--n-layers", type=int, default=4)
    parser.add_argument("--layer-stride", type=int, default=10)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--rel-lambda", type=float, default=0.1,
                        help="Weight of relational loss")
    parser.add_argument("--rel-every", type=int, default=5,
                        help="Apply relational loss every N steps")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--skip-rdm-extraction", action="store_true",
                        help="Load cached universal RDM if available")
    parser.add_argument("--skip-sign-extraction", action="store_true",
                        help="Load cached plate signs if available")
    parser.add_argument("--skip-condition-a", action="store_true",
                        help="Skip baseline (NT-only) — use when rerunning with new lambdas")
    parser.add_argument("--template-lambda", type=float, default=0.0,
                        help="Weight of Level 2 template loss (0=disabled). Targets L0 structure.")
    parser.add_argument("--residual", action="store_true",
                        help="Use residual RDM (mean-subtracted). Removes PC1 'all facts alike' "
                             "signal, focuses loss on discriminative structure (domain/template/answer_type).")
    parser.add_argument("--crystal-seed", type=Path, default=None,
                        help="Path to verified_dimensions.json from crystal seed probe. "
                             "Uses the full 311-probe RDM as relational target (much richer constraints).")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    layer_indices = list(range(0, 40, args.layer_stride))[:args.n_layers]

    # ── Probe selection: crystal seed (311) or factual only (46) ──
    if args.crystal_seed and args.crystal_seed.exists():
        print(f"  Loading crystal seed probes from {args.crystal_seed}...", file=sys.stderr)
        crystal_data = json.load(args.crystal_seed.open())
        rel_probes = [{"prompt": p["prompt"], "category": p.get("axis", "unknown")}
                      for p in crystal_data["probes"]]
        print(f"  Crystal seed: {len(rel_probes)} probes, "
              f"{crystal_data['total_dimensions']} verified dimensions", file=sys.stderr)
    else:
        rel_probes = None  # will use factual probes

    # Factual probes always used for RECALL measurement (consistent comparison)
    factual_probes = flatten_probes()

    tokenizer = AutoTokenizer.from_pretrained(args.source)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Probes for relational loss (crystal seed if available, else factual)
    if rel_probes is None:
        rel_probes = factual_probes

    print(f"\n{'═'*70}", file=sys.stderr)
    print(f"  RELATIONAL DISTILLATION — Universal Geometry as Training Loss", file=sys.stderr)
    print(f"{'═'*70}", file=sys.stderr)
    print(f"  Source:      {args.source}", file=sys.stderr)
    print(f"  Layers:      {layer_indices}", file=sys.stderr)
    print(f"  Steps:       {args.train_steps}", file=sys.stderr)
    print(f"  Rel lambda:  {args.rel_lambda}", file=sys.stderr)
    print(f"  Rel every:   {args.rel_every} steps", file=sys.stderr)
    print(f"  Rel probes:  {len(rel_probes)} ({'crystal seed' if args.crystal_seed else 'factual'})",
          file=sys.stderr)
    print(f"  Eval probes: {len(factual_probes)} (factual recall measurement)", file=sys.stderr)
    print(f"  Residual:    {args.residual}", file=sys.stderr)
    print(f"{'═'*70}\n", file=sys.stderr)

    # ══ Phase 1: Build universal RDM ═════════════════════════════

    # If crystal seed provided, load RDM from it directly
    if args.crystal_seed and args.crystal_seed.exists():
        print("Phase 1: Loading RDM from crystal seed...", file=sys.stderr)
        # Crystal seed targets are per-layer RDMs already in residual form
        crystal_targets = crystal_data["targets"]
        universal_rdm = {}
        for li in layer_indices:
            li_str = str(li)
            if li_str in crystal_targets:
                universal_rdm[li] = np.array(crystal_targets[li_str]["rdm"])
                print(f"  L{li}: loaded {universal_rdm[li].shape[0]}×{universal_rdm[li].shape[1]} RDM "
                      f"(residual={crystal_targets[li_str].get('residual', False)})", file=sys.stderr)
            else:
                # Fall back to nearest available layer
                available = sorted(crystal_targets.keys(), key=lambda k: abs(int(k) - li))
                nearest = available[0]
                universal_rdm[li] = np.array(crystal_targets[nearest]["rdm"])
                print(f"  L{li}: using L{nearest} RDM (nearest available)", file=sys.stderr)
        # Crystal seed already applies residual internally — skip the residual step below
        skip_residual_transform = True
    else:
        skip_residual_transform = False
        rdm_cache_path = args.output_dir / "universal_rdm_cache.json"

        if args.skip_rdm_extraction and rdm_cache_path.exists():
            print("Phase 1: Loading cached universal RDM...", file=sys.stderr)
            cached = json.load(rdm_cache_path.open())
            universal_rdm = {int(k): np.array(v) for k, v in cached.items()}
        else:
            print("Phase 1: Building universal RDM from source models...\n", file=sys.stderr)
            universal_rdm = build_universal_rdm(
                list(MODELS.keys()), layer_indices, rel_probes, args.device
        )
        # Cache for reuse
        cache_data = {str(k): v.tolist() for k, v in universal_rdm.items()}
        rdm_cache_path.write_text(json.dumps(cache_data))
        print(f"\n  Cached universal RDM to {rdm_cache_path}\n", file=sys.stderr)

    # Show RDM structure
    print(f"  Universal RDM structure (L{layer_indices[0]}):", file=sys.stderr)
    rdm0 = universal_rdm[layer_indices[0]]
    categories = [p.get("category", p.get("axis", "unknown")) for p in rel_probes]
    cat_names = sorted(set(categories))[:10]  # show top 10 categories max
    print(f"  {'':>12}", end='', file=sys.stderr)
    for c in cat_names:
        print(f"{c[:6]:>8}", end='', file=sys.stderr)
    print(file=sys.stderr)
    for ci in cat_names:
        idx_i = [k for k, c in enumerate(categories) if c == ci]
        print(f"  {ci:<12}", end='', file=sys.stderr)
        for cj in cat_names:
            idx_j = [k for k, c in enumerate(categories) if c == cj]
            # Mean similarity between categories
            sims = [rdm0[i, j] for i in idx_i for j in idx_j if i != j]
            mean_sim = np.mean(sims) if sims else 0
            print(f"{mean_sim:>8.3f}", end='', file=sys.stderr)
        print(file=sys.stderr)

    # ── Optional: Residual RDM (mean-subtracted) ──
    if args.residual and not skip_residual_transform:
        print(f"\n  Applying RESIDUAL transformation (mean-subtracted RDM)...", file=sys.stderr)
        print(f"  Removes PC1 (93.3% — 'all facts alike'), focuses on discriminative structure.",
              file=sys.stderr)
        for li in list(universal_rdm.keys()):
            rdm_orig = universal_rdm[li]
            rdm_mean = rdm_orig.mean()
            rdm_residual = rdm_orig - rdm_mean
            # Keep diagonal at 0 (self-similarity is uninformative in residual space)
            np.fill_diagonal(rdm_residual, 0.0)
            universal_rdm[li] = rdm_residual
            # Report signal amplification
            orig_std = rdm_orig[np.triu_indices(len(rdm_orig), k=1)].std()
            resid_std = rdm_residual[np.triu_indices(len(rdm_residual), k=1)].std()
            print(f"    L{li}: mean_removed={rdm_mean:.4f}, "
                  f"signal_std: {orig_std:.4f} → {resid_std:.4f}", file=sys.stderr)
    elif skip_residual_transform:
        print(f"\n  Residual already applied by crystal seed.", file=sys.stderr)

    # ══ Phase 2: Extract plate signs ═════════════════════════════
    print(f"\nPhase 2: Extracting plate signs from {args.source}...", file=sys.stderr)
    extracted_signs = extract_signs(args.source, layer_indices, device=args.device)
    intermediate = extracted_signs[0]["gate"].shape[0]

    # ══ Phase 3: Build relational loss ═══════════════════════════
    print(f"\nPhase 3: Building relational loss module...", file=sys.stderr)

    # RSA-weighted layer strengths (from tomography: L0=0.74, L10=0.58, L20=0.56, L30=0.66)
    rsa_weights = {0: 0.74, 10: 0.58, 20: 0.56, 30: 0.66}
    layer_weights = {}
    for li in layer_indices:
        # Use RSA score as weight (or 0.5 default)
        layer_weights[li] = rsa_weights.get(li, 0.5)
    # Normalize so weights sum to 1
    total_w = sum(layer_weights.values())
    layer_weights = {li: w / total_w for li, w in layer_weights.items()}

    print(f"  Level 1 (domain) layer weights: {layer_weights}", file=sys.stderr)
    if args.residual:
        print(f"  Mode: RESIDUAL (mean-subtracted, discriminative only)", file=sys.stderr)

    rel_loss_fn = RelationalLoss(universal_rdm, layer_weights, residual=args.residual)

    # Level 2: Template loss (targets early layers where structural templates cluster)
    template_loss_fn = None
    if args.template_lambda > 0:
        # Template structure is strongest at L0 (1.48× ratio), weaker deeper
        template_layer_weights = {}
        template_rsa = {0: 1.48, 10: 1.19, 20: 1.10, 30: 1.05}  # from session 105 probe
        for li in layer_indices:
            # Only include layers where template signal exists (ratio > 1.1)
            ratio = template_rsa.get(li, 1.0)
            if ratio > 1.05:
                template_layer_weights[li] = ratio - 1.0  # weight by signal strength
        if template_layer_weights:
            total_tw = sum(template_layer_weights.values())
            template_layer_weights = {li: w / total_tw for li, w in template_layer_weights.items()}
            template_loss_fn = RelationalLoss(universal_rdm, template_layer_weights, residual=args.residual)
            print(f"  Level 2 (template) layer weights: {template_layer_weights}", file=sys.stderr)
            print(f"  Template lambda: {args.template_lambda}", file=sys.stderr)
        else:
            print(f"  ⚠️  No layers with template signal > 1.05 — template loss disabled",
                  file=sys.stderr)

    # ══ Phase 4: Train conditions ════════════════════════════════
    print(f"\n{'─'*70}", file=sys.stderr)
    print(f"  Phase 4: TRAINING", file=sys.stderr)
    print(f"{'─'*70}\n", file=sys.stderr)

    # ── Condition A: Next-token only (skippable) ──
    if args.skip_condition_a:
        print("  ═══ Condition A: SKIPPED (--skip-condition-a) ═══\n", file=sys.stderr)
        # Load from previous results if available
        prev_results_path = args.output_dir / "relational_distill_results.json"
        if prev_results_path.exists():
            prev = json.load(prev_results_path.open())
            result_a = prev.get("condition_a_nt_only", {
                "label": "NT-ONLY (cached)",
                "history": [],
                "final_recall": {"mean_logprob": 0, "mean_rank": 0, "per_category": {}},
            })
            print(f"  Loaded Condition A from previous run: logprob={result_a['final_recall'].get('mean_logprob', '?')}",
                  file=sys.stderr)
        else:
            result_a = {
                "label": "NT-ONLY (skipped)",
                "history": [],
                "final_recall": {"mean_logprob": 0, "mean_rank": 0, "per_category": {}},
            }
    else:
        print("  ═══ Condition A: NEXT-TOKEN ONLY (baseline) ═══\n", file=sys.stderr)

        model_a = ExtractedModel(
            n_layers=len(layer_indices), d_model=D_MODEL, n_heads=N_HEADS,
            n_kv_heads=N_KV_HEADS, head_dim=HEAD_DIM, intermediate=intermediate,
            vocab_size=VOCAB_SIZE, layer_signs=extracted_signs,
        )
        loader_a = SimpleDataLoader(DATA_DIR, 2, 256, shard_start=0, shard_end=4, seed=42)

        result_a = train_condition(
            model_a, loader_a, rel_probes, tokenizer, layer_indices,
            n_steps=args.train_steps, lr=args.lr, device=args.device,
            label="NT-ONLY", rel_loss_fn=None,
            eval_every=100, eval_probes=factual_probes,
        )
        del model_a
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

    # ── Condition B: Next-token + Relational (Level 1 + optional Level 2) ──
    level_str = "L1+L2" if template_loss_fn else "L1"
    lambda_str = f"λ_dom={args.rel_lambda}"
    if args.template_lambda > 0:
        lambda_str += f", λ_tmpl={args.template_lambda}"
    print(f"\n  ═══ Condition B: NT + RELATIONAL ({level_str}, {lambda_str}) ═══\n",
          file=sys.stderr)

    model_b = ExtractedModel(
        n_layers=len(layer_indices), d_model=D_MODEL, n_heads=N_HEADS,
        n_kv_heads=N_KV_HEADS, head_dim=HEAD_DIM, intermediate=intermediate,
        vocab_size=VOCAB_SIZE, layer_signs=extracted_signs,
    )
    loader_b = SimpleDataLoader(DATA_DIR, 2, 256, shard_start=0, shard_end=4, seed=42)

    # Combined loss: domain (Level 1) + template (Level 2)
    # We pass the domain loss as rel_loss_fn and handle template separately in train_condition
    result_b = train_condition(
        model_b, loader_b, rel_probes, tokenizer, layer_indices,
        n_steps=args.train_steps, lr=args.lr, device=args.device,
        label="NT+REL", rel_loss_fn=rel_loss_fn,
        rel_lambda=args.rel_lambda, rel_every=args.rel_every,
        eval_every=100, eval_probes=factual_probes,
        template_loss_fn=template_loss_fn,
        template_lambda=args.template_lambda,
    )
    del model_b
    gc.collect()

    # ══ Phase 5: Results ═════════════════════════════════════════
    print(f"\n{'═'*70}", file=sys.stderr)
    print(f"  RESULTS — Relational Distillation", file=sys.stderr)
    print(f"{'═'*70}\n", file=sys.stderr)

    # Recall comparison
    ra = result_a["final_recall"]
    rb = result_b["final_recall"]

    print(f"  {'Metric':<25} {'NT-Only':>12} {'NT+Relational':>14} {'Δ':>10}", file=sys.stderr)
    print(f"  {'─'*25} {'─'*12} {'─'*14} {'─'*10}", file=sys.stderr)
    print(f"  {'Mean log-prob':<25} {ra['mean_logprob']:>12.2f} {rb['mean_logprob']:>14.2f} "
          f"{rb['mean_logprob']-ra['mean_logprob']:>+10.2f}", file=sys.stderr)
    print(f"  {'Mean rank':<25} {ra['mean_rank']:>12.0f} {rb['mean_rank']:>14.0f} "
          f"{rb['mean_rank']-ra['mean_rank']:>+10.0f}", file=sys.stderr)

    # Per-category
    print(f"\n  Per-category log-prob:", file=sys.stderr)
    print(f"  {'Category':<12} {'NT-Only':>10} {'NT+Rel':>10} {'Δ':>10} {'Winner':>8}", file=sys.stderr)
    print(f"  {'─'*12} {'─'*10} {'─'*10} {'─'*10} {'─'*8}", file=sys.stderr)
    wins_a, wins_b = 0, 0
    for cat in cat_names:
        lp_a = ra["per_category"].get(cat, 0)
        lp_b = rb["per_category"].get(cat, 0)
        delta = lp_b - lp_a
        winner = "REL" if lp_b > lp_a else "BASE"
        if lp_b > lp_a:
            wins_b += 1
        else:
            wins_a += 1
        print(f"  {cat:<12} {lp_a:>10.2f} {lp_b:>10.2f} {delta:>+10.2f} {winner:>8}", file=sys.stderr)

    # Geometry comparison (RSA of student vs universal target)
    print(f"\n  Geometry alignment (student RDM vs universal RDM):", file=sys.stderr)
    print(f"  {'Layer':<8} {'RSA(NT-Only)':>13} {'RSA(NT+Rel)':>12} {'Δ':>8}", file=sys.stderr)
    print(f"  {'─'*8} {'─'*13} {'─'*12} {'─'*8}", file=sys.stderr)

    for li in layer_indices:
        li_str = str(li)
        if li_str in result_a["final_student_rdms"] and li_str in result_b["final_student_rdms"]:
            rdm_a_student = np.array(result_a["final_student_rdms"][li_str])
            rdm_b_student = np.array(result_b["final_student_rdms"][li_str])
            target = universal_rdm[li]

            # RSA: correlation between student RDM and universal
            n = rdm_a_student.shape[0]
            triu = np.triu_indices(n, k=1)

            rsa_a = np.corrcoef(rdm_a_student[triu], target[triu])[0, 1]
            rsa_b = np.corrcoef(rdm_b_student[triu], target[triu])[0, 1]

            print(f"  L{li:<6} {rsa_a:>13.4f} {rsa_b:>12.4f} {rsa_b-rsa_a:>+8.4f}", file=sys.stderr)

    # Training curves
    print(f"\n  Training loss trajectories:", file=sys.stderr)
    print(f"  {'Step':>6} {'NT-Only':>10} {'NT+Rel(nt)':>11} {'Rel loss':>10}", file=sys.stderr)
    print(f"  {'─'*6} {'─'*10} {'─'*11} {'─'*10}", file=sys.stderr)
    for ha, hb in zip(result_a["history"], result_b["history"]):
        print(f"  {ha['step']:>6} {ha['loss_nt']:>10.2f} {hb['loss_nt']:>11.2f} "
              f"{hb['loss_rel']:>10.4f}", file=sys.stderr)

    # Verdict
    print(f"\n  ═══ VERDICT ═══", file=sys.stderr)
    if rb["mean_logprob"] > ra["mean_logprob"]:
        improvement = (rb["mean_logprob"] - ra["mean_logprob"]) / abs(ra["mean_logprob"]) * 100
        print(f"  ✅ Relational loss IMPROVES factual recall by {improvement:.1f}%", file=sys.stderr)
        print(f"     Category wins: NT+Rel={wins_b}, NT-Only={wins_a}", file=sys.stderr)
    else:
        print(f"  ⚠️  Relational loss does not improve factual recall", file=sys.stderr)
        print(f"     Category wins: NT+Rel={wins_b}, NT-Only={wins_a}", file=sys.stderr)
        print(f"     May need: higher lambda, more steps, or different rel_every", file=sys.stderr)

    # ══ Save results ═════════════════════════════════════════════
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "config": {
            "source_model": args.source,
            "layer_indices": layer_indices,
            "train_steps": args.train_steps,
            "rel_lambda": args.rel_lambda,
            "rel_every": args.rel_every,
            "lr": args.lr,
            "n_probes": len(probes),
            "rsa_layer_weights": layer_weights,
        },
        "universal_rdm_summary": {
            str(li): {
                "mean_within_cat": float(np.mean([
                    universal_rdm[li][i, j]
                    for ci in cat_names
                    for i in [k for k, c in enumerate(categories) if c == ci]
                    for j in [k for k, c in enumerate(categories) if c == ci]
                    if i != j
                ])),
                "mean_between_cat": float(np.mean([
                    universal_rdm[li][i, j]
                    for i in range(len(probes))
                    for j in range(i + 1, len(probes))
                    if categories[i] != categories[j]
                ])),
            }
            for li in layer_indices
        },
        "condition_a_nt_only": result_a,
        "condition_b_nt_rel": result_b,
        "summary": {
            "recall_improvement_pct": (rb["mean_logprob"] - ra["mean_logprob"]) / abs(ra["mean_logprob"]) * 100 if ra["mean_logprob"] != 0 else 0,
            "category_wins": {"nt_only": wins_a, "nt_rel": wins_b},
            "relational_helps": rb["mean_logprob"] > ra["mean_logprob"],
        },
    }

    # Don't save full student RDMs (large) — just the RSA scores
    json_path = args.output_dir / "relational_distill_results.json"

    # Remove large RDM arrays from output to keep file manageable
    for key in ["condition_a_nt_only", "condition_b_nt_rel"]:
        if "final_student_rdms" in output[key]:
            del output[key]["final_student_rdms"]

    json_path.write_text(json.dumps(output, indent=2))
    print(f"\n  💾 Results: {json_path}", file=sys.stderr)
    print(f"{'═'*70}\n", file=sys.stderr)


if __name__ == "__main__":
    main()
