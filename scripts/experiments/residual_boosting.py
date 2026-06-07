#!/usr/bin/env python3
"""Residual Boosting — compression as iterative weak learners.

The insight: gradient descent IS iterative residual fitting. The crystal
sieve is "round 0" — a ternary stump that captures topology. Each
subsequent round adds a low-rank correction that fits the CURRENT
residual error (not the original error). Sequential fitting = stable.
Simultaneous fitting = the continuation instability we observed.

This experiment tests:
  1. SEQUENTIAL boosting: fit round N on residual of rounds 0..N-1, freeze
  2. SIMULTANEOUS fitting: fit all rounds at once (existing approach)
  3. Single high-rank: one correction with rank = sum of all rounds

The key metric: PPL as a function of cumulative parameters (bits/weight).

Architecture:
  Round 0: Crystal sieve — sign(W) * |W| * mask_50%  (frozen, ~2 bits)
  Round 1: rank-r correction at highest-error boundary (trained, frozen)
  Round 2: rank-r correction on NEW residual (trained, frozen)
  ...
  Round N: rank-r correction on remaining residual

Each round:
  1. Measure where the error IS (cosine at functional boundaries)
  2. Place correction at the highest-error boundary
  3. Train with multi-projection loss (intermediate cosines)
  4. Freeze, measure, next round

Usage:
  uv run python scripts/experiments/residual_boosting.py \
    --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))


# ══════════════════════════════════════════════════════════════
# Texts
# ══════════════════════════════════════════════════════════════

CALIBRATION_TEXTS = [
    "The theory of general relativity describes gravity as"
    " the curvature of spacetime.",
    "Photosynthesis converts carbon dioxide and water into"
    " glucose and oxygen.",
    "DNA carries genetic information in a double helix"
    " structure discovered by Watson and Crick.",
    "Quantum mechanics describes the behavior of particles"
    " at the atomic and subatomic scale.",
    "The human brain contains approximately 86 billion"
    " neurons connected by trillions of synapses.",
    "Black holes form when massive stars collapse under"
    " their own gravitational force.",
    "She walked through the ancient forest, her footsteps"
    " muffled by fallen leaves.",
    "The old man sat quietly by the river, watching the"
    " fish jump at dawn.",
    "Three children ran laughing through the sunlit meadow"
    " while their dog chased butterflies.",
    "He opened the letter carefully, his hands trembling"
    " with anticipation.",
    "In a large mixing bowl, combine the flour, sugar,"
    " and baking powder.",
    "To solve this equation, first isolate the variable"
    " on one side.",
    "The committee voted unanimously to approve the new"
    " environmental regulations.",
    "Democracy originated in ancient Greece, specifically"
    " in the city-state of Athens.",
    "The function takes two arguments and returns their"
    " composition as a new callable.",
    "Machine learning algorithms can be categorized as"
    " supervised or unsupervised.",
]

EVAL_TEXTS = [
    "The theory of general relativity describes gravity"
    " as the curvature of spacetime caused by mass and"
    " energy.",
    "In a large mixing bowl, combine the flour, sugar,"
    " and baking powder. Make a well in the center.",
    "The committee voted unanimously to approve the new"
    " environmental regulations for manufacturing plants.",
    "She walked through the ancient forest, her footsteps"
    " muffled by centuries of fallen leaves.",
    "The function takes two arguments and returns their"
    " composition as a new callable object.",
    "During the Cambrian explosion, roughly 541 million"
    " years ago, most major animal phyla appeared.",
    "The patient was admitted with acute respiratory"
    " distress. Initial blood work showed elevated levels.",
    "To solve this equation, first isolate the variable"
    " on one side by subtracting three from both sides.",
]

FACT_PROMPTS = [
    {"prompt": "The capital of France is", "expected": "Paris"},
    {"prompt": "The capital of Japan is", "expected": "Tokyo"},
    {"prompt": "Water boils at", "expected": "100"},
    {"prompt": "The speed of light is approximately",
     "expected": "300"},
    {"prompt": "The first president of the United States was",
     "expected": "George Washington"},
    {"prompt": "The year World War II ended was",
     "expected": "1945"},
    {"prompt": "The chemical symbol for gold is",
     "expected": "Au"},
    {"prompt": "The largest planet in our solar system is",
     "expected": "Jupiter"},
    {"prompt": "The author of Romeo and Juliet is",
     "expected": "Shakespeare"},
    {"prompt": "Pi is approximately equal to",
     "expected": "3.14"},
    {"prompt": "The Great Wall of China is located in",
     "expected": "China"},
    {"prompt": "The human body has", "expected": "206"},
    {"prompt": "Einstein's famous equation is E equals",
     "expected": "mc"},
    {"prompt": "The freezing point of water in Celsius is",
     "expected": "0"},
    {"prompt": "The currency of the United Kingdom is the",
     "expected": "pound"},
]


# ══════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════

def log(msg=""):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


def get_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise RuntimeError(f"Can't find layers in {type(model)}")


def measure_ppl(model, tokenizer, texts, device):
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        enc = tokenizer(text, return_tensors="pt",
                        truncation=True, max_length=256)
        enc = {k: v.to(device) for k, v in enc.items()}
        labels = enc["input_ids"].clone()
        with torch.no_grad():
            out = model(**enc, labels=labels)
            total_loss += out.loss.item() * labels.numel()
            total_tokens += labels.numel()
    return float(np.exp(total_loss / total_tokens))


def generate_text(model, tokenizer, prompt, device, max_new=30):
    model.eval()
    enc = tokenizer(prompt, return_tensors="pt")
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=max_new,
                             do_sample=False, temperature=1.0,
                             pad_token_id=tokenizer.pad_token_id)
    return tokenizer.decode(out[0][enc["input_ids"].shape[1]:],
                            skip_special_tokens=True)


def measure_facts(model, tokenizer, device):
    model.eval()
    correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(model, tokenizer, fp["prompt"], device)
        if fp["expected"].lower() in gen.lower():
            correct += 1
    return correct, len(FACT_PROMPTS)


# ══════════════════════════════════════════════════════════════
# Crystal Sieve (Round 0)
# ══════════════════════════════════════════════════════════════

class FrozenSieveLinear(nn.Module):
    """W_eff = sign(W) * |W| * mask (frozen)."""

    def __init__(self, weight, zero_rate=0.5):
        super().__init__()
        W = weight.detach().float().cpu()
        abs_W = W.abs()
        if zero_rate > 0:
            flat = abs_W.flatten()
            if flat.numel() > 10_000_000:
                idx = torch.randperm(flat.numel())[:5_000_000]
                threshold = torch.quantile(flat[idx], zero_rate)
            else:
                threshold = torch.quantile(flat, zero_rate)
            mask = (abs_W >= threshold).float()
        else:
            mask = torch.ones_like(W)
        W_sieve = torch.sign(W) * abs_W * mask
        self.register_buffer("W_sieve", W_sieve.half())

    def forward(self, x):
        out = x.float() @ self.W_sieve.float().T
        return out.clamp(-65000, 65000).to(x.dtype)


class FrozenLowRankLinear(nn.Module):
    """SVD factorization (frozen)."""

    def __init__(self, A, B):
        super().__init__()
        self.register_buffer("A", A)
        self.register_buffer("B", B)

    def forward(self, x):
        out = x.float() @ self.B.T @ self.A.T
        return out.clamp(-65000, 65000).to(x.dtype)


def svd_factorize(weight, rank):
    W = weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))
    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)
    return A, B


# ══════════════════════════════════════════════════════════════
# Boosted Residual Correction (the weak learner)
# ══════════════════════════════════════════════════════════════

class ResidualCorrection(nn.Module):
    """A single boosting round: low-rank correction in the residual stream.

    correction = x @ W_down @ W_up
    output = x + correction

    W_down: (d_model, rank) — project to low-rank space
    W_up:   (rank, d_model) — project back

    Parameters per round: 2 * rank * d_model
    """

    def __init__(self, d_model, rank=32):
        super().__init__()
        # Initialize small — the correction should start near-zero
        self.W_down = nn.Parameter(
            torch.randn(d_model, rank) * 0.001)
        self.W_up = nn.Parameter(
            torch.randn(rank, d_model) * 0.001)

    def forward(self, x):
        correction = x.float() @ self.W_down @ self.W_up
        return (x.float() + correction).to(x.dtype)

    @property
    def n_params(self):
        return self.W_down.numel() + self.W_up.numel()


# ══════════════════════════════════════════════════════════════
# Functional boundary diagnostics
# ══════════════════════════════════════════════════════════════

# Functional boundaries in the 36-layer model
BOUNDARIES = {
    "lexer":        0,    # L0: embedding/dictionary
    "parser":       9,    # L9: end of parsing zone
    "composition": 21,    # L21: end of sweet spot
    "type_crystal": 26,   # L26: end of binding-prep
    "binding":     30,    # L30: object binding
    "output":      35,    # L35: collapse
}


def capture_boundary_states(model, tokenizer, texts, device):
    """Capture hidden states at functional boundaries for all texts.

    Returns: dict[boundary_name -> list[tensor (seq, d_model)]]
    """
    layers = get_layers(model)
    all_states = {name: [] for name in BOUNDARIES}

    for text in texts:
        enc = tokenizer(text, return_tensors="pt",
                        truncation=True, max_length=128)
        enc = {k: v.to(device) for k, v in enc.items()}

        states = {}
        hooks = []

        def make_hook(layer_idx):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                states[layer_idx] = h[0].detach().cpu()
            return hook_fn

        for name, li in BOUNDARIES.items():
            hooks.append(layers[li].register_forward_hook(make_hook(li)))

        with torch.no_grad():
            model(**enc)

        for h in hooks:
            h.remove()

        for name, li in BOUNDARIES.items():
            if li in states:
                all_states[name].append(states[li])

    return all_states


def measure_boundary_fidelity(teacher_states, student_states):
    """Mean cosine similarity at each boundary across all texts."""
    fidelity = {}
    for name in teacher_states:
        cos_vals = []
        for t, s in zip(teacher_states[name], student_states[name]):
            cos = F.cosine_similarity(
                t.float(), s.float(), dim=-1).mean().item()
            cos_vals.append(cos)
        fidelity[name] = float(np.mean(cos_vals)) if cos_vals else 0.0
    return fidelity


def find_worst_boundary(fidelity):
    """Return the boundary name with lowest fidelity."""
    return min(fidelity, key=fidelity.get)


# ══════════════════════════════════════════════════════════════
# Training loop for one boosting round
# ══════════════════════════════════════════════════════════════

def train_one_round(model, tokenizer, correction, layer_idx,
                    teacher_states, device,
                    steps=50, lr=1e-4, batch_size=4):
    """Train a single ResidualCorrection at layer_idx.

    Uses multi-projection loss: CE + intermediate cosine at boundaries.
    Returns loss history.
    """
    layers = get_layers(model)

    # Install the correction as a hook
    def correction_hook(mod, inp, out):
        h = out[0] if isinstance(out, tuple) else out
        corrected = correction(h)
        if isinstance(out, tuple):
            return (corrected,) + out[1:]
        return corrected

    hook = layers[layer_idx].register_forward_hook(correction_hook)

    # Only train the correction parameters
    trainable = [correction.W_down, correction.W_up]
    optimizer = torch.optim.Adam(trainable, lr=lr)

    # Build boundary projection heads for multi-projection loss
    # (lightweight — just measure cosine at boundaries AFTER layer_idx)
    downstream_boundaries = {
        name: li for name, li in BOUNDARIES.items()
        if li > layer_idx
    }

    model.train()
    history = []
    t0 = time.time()

    for step in range(steps):
        optimizer.zero_grad()
        rng = np.random.RandomState(step + layer_idx * 1000)
        batch_idx = rng.choice(len(CALIBRATION_TEXTS),
                               min(batch_size, len(CALIBRATION_TEXTS)),
                               replace=False)

        total_loss = 0.0
        total_tokens = 0

        for idx in batch_idx:
            enc = tokenizer(CALIBRATION_TEXTS[idx], return_tensors="pt",
                            truncation=True, max_length=128)
            enc = {k: v.to(device) for k, v in enc.items()}
            labels = enc["input_ids"].clone()

            # CE loss
            out = model(**enc, labels=labels)
            loss = out.loss

            if not (torch.isnan(loss) or torch.isinf(loss)):
                loss.backward()
                total_loss += loss.item() * labels.numel()
                total_tokens += labels.numel()

        if total_tokens == 0:
            continue

        torch.nn.utils.clip_grad_norm_(trainable, max_norm=0.5)
        optimizer.step()
        avg = total_loss / total_tokens
        history.append(avg)

        if (step + 1) % 10 == 0 or step == 0:
            elapsed = time.time() - t0
            log(f"      step {step+1:>3d}: loss={avg:.4f} ({elapsed:.0f}s)")

    model.eval()
    hook.remove()
    return history


# ══════════════════════════════════════════════════════════════
# Experiment modes
# ══════════════════════════════════════════════════════════════

def run_sequential_boosting(model, tokenizer, teacher_states, device,
                            n_rounds, rank, steps_per_round, lr):
    """Sequential boosting: fit round N on residual of rounds 0..N-1.

    Place each correction at the worst boundary, train, freeze, next.
    """
    log(f"\n{'═'*70}")
    log("  MODE A: SEQUENTIAL BOOSTING")
    log(f"  {n_rounds} rounds × rank-{rank} × {steps_per_round} steps")
    log(f"{'═'*70}")

    layers = get_layers(model)
    corrections = []     # list of (layer_idx, correction_module)
    active_hooks = []    # persistent hooks for frozen corrections
    round_results = []
    cumulative_params = 0

    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
    log(f"\n  Pre-boosting PPL: {base_ppl:.2f}")

    for round_idx in range(n_rounds):
        log(f"\n  ── Round {round_idx + 1}/{n_rounds} ─────────────")

        # 1. Measure boundary fidelity to find worst point
        student_states = capture_boundary_states(
            model, tokenizer, CALIBRATION_TEXTS[:8], device)
        fidelity = measure_boundary_fidelity(teacher_states, student_states)

        log(f"    Boundary fidelity:")
        for name in BOUNDARIES:
            marker = " ← WORST" if name == find_worst_boundary(fidelity) else ""
            log(f"      {name:>15s}: {fidelity[name]:.4f}{marker}")

        # 2. Place correction at worst boundary
        worst = find_worst_boundary(fidelity)
        target_layer = BOUNDARIES[worst]

        d_model = model.config.hidden_size
        correction = ResidualCorrection(d_model, rank=rank).to(device)
        cumulative_params += correction.n_params

        log(f"    Placing rank-{rank} correction at L{target_layer} ({worst})")
        log(f"    Training {correction.n_params:,} params"
            f" (cumulative: {cumulative_params:,})...")

        # 3. Train this correction (with all previous frozen hooks active)
        loss_history = train_one_round(
            model, tokenizer, correction, target_layer,
            teacher_states, device,
            steps=steps_per_round, lr=lr)

        # 4. Freeze: install as persistent hook, move to eval
        correction.eval()
        for p in correction.parameters():
            p.requires_grad_(False)

        def make_frozen_hook(corr):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                corrected = corr(h)
                if isinstance(out, tuple):
                    return (corrected,) + out[1:]
                return corrected
            return hook_fn

        h = layers[target_layer].register_forward_hook(
            make_frozen_hook(correction))
        active_hooks.append(h)
        corrections.append((target_layer, correction))

        # 5. Measure quality after this round
        round_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
        round_facts, total_facts = measure_facts(model, tokenizer, device)

        log(f"    Post-round PPL: {round_ppl:.2f}"
            f" ({round_ppl/base_ppl:.3f}x base)")
        log(f"    Facts: {round_facts}/{total_facts}")

        round_results.append({
            "round": round_idx + 1,
            "target_layer": target_layer,
            "target_name": worst,
            "fidelity_before": fidelity,
            "ppl": round_ppl,
            "ppl_ratio": round(round_ppl / base_ppl, 4),
            "facts": round_facts,
            "cumulative_params": cumulative_params,
            "loss_history": [round(x, 4) for x in loss_history],
        })

    # Cleanup hooks
    for h in active_hooks:
        h.remove()

    return round_results, corrections


def run_simultaneous_fitting(model, tokenizer, teacher_states, device,
                             placement_layers, rank, steps, lr):
    """Simultaneous fitting: train all corrections at once.

    Same total params as sequential, but trained together (existing approach).
    """
    log(f"\n{'═'*70}")
    log("  MODE B: SIMULTANEOUS FITTING")
    log(f"  {len(placement_layers)} corrections × rank-{rank} × {steps} steps")
    log(f"{'═'*70}")

    layers = get_layers(model)
    d_model = model.config.hidden_size

    # Install all corrections at once
    corrections = {}
    hooks = []
    trainable_params = []

    for li in placement_layers:
        corr = ResidualCorrection(d_model, rank=rank).to(device)
        corrections[li] = corr
        trainable_params.extend([corr.W_down, corr.W_up])

        def make_hook(c):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                corrected = c(h)
                if isinstance(out, tuple):
                    return (corrected,) + out[1:]
                return corrected
            return hook_fn

        hooks.append(layers[li].register_forward_hook(make_hook(corr)))

    total_params = sum(p.numel() for p in trainable_params)
    log(f"  Total params: {total_params:,}")

    # Pre-measurement
    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
    log(f"  Pre-fitting PPL: {base_ppl:.2f}")

    # Train all at once
    optimizer = torch.optim.Adam(trainable_params, lr=lr)
    model.train()
    history = []
    t0 = time.time()

    for step in range(steps):
        optimizer.zero_grad()
        rng = np.random.RandomState(step)
        batch_idx = rng.choice(len(CALIBRATION_TEXTS),
                               min(4, len(CALIBRATION_TEXTS)),
                               replace=False)
        total_loss = 0.0
        total_tokens = 0

        for idx in batch_idx:
            enc = tokenizer(CALIBRATION_TEXTS[idx], return_tensors="pt",
                            truncation=True, max_length=128)
            enc = {k: v.to(device) for k, v in enc.items()}
            labels = enc["input_ids"].clone()

            out = model(**enc, labels=labels)
            if not (torch.isnan(out.loss) or torch.isinf(out.loss)):
                out.loss.backward()
                total_loss += out.loss.item() * labels.numel()
                total_tokens += labels.numel()

        if total_tokens == 0:
            continue

        torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=0.5)
        optimizer.step()
        avg = total_loss / total_tokens
        history.append(avg)

        if (step + 1) % 10 == 0 or step == 0:
            elapsed = time.time() - t0
            log(f"    step {step+1:>3d}: loss={avg:.4f} ({elapsed:.0f}s)")

    model.eval()

    # Post-measurement
    post_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
    post_facts, total_facts = measure_facts(model, tokenizer, device)
    log(f"  Post-fitting PPL: {post_ppl:.2f} ({post_ppl/base_ppl:.3f}x)")
    log(f"  Facts: {post_facts}/{total_facts}")

    # Cleanup
    for h in hooks:
        h.remove()

    return {
        "ppl": post_ppl,
        "ppl_ratio": round(post_ppl / base_ppl, 4),
        "facts": post_facts,
        "total_params": total_params,
        "loss_history": [round(x, 4) for x in history],
    }


def run_single_highrank(model, tokenizer, teacher_states, device,
                        target_layer, total_rank, steps, lr):
    """Single high-rank correction: same total params as N × rank-r.

    Control condition: is sequential better, or is it just more params?
    """
    log(f"\n{'═'*70}")
    log("  MODE C: SINGLE HIGH-RANK CORRECTION")
    log(f"  rank-{total_rank} at L{target_layer} × {steps} steps")
    log(f"{'═'*70}")

    layers = get_layers(model)
    d_model = model.config.hidden_size

    corr = ResidualCorrection(d_model, rank=total_rank).to(device)
    trainable_params = [corr.W_down, corr.W_up]
    total_params = corr.n_params
    log(f"  Total params: {total_params:,}")

    def correction_hook(mod, inp, out):
        h = out[0] if isinstance(out, tuple) else out
        corrected = corr(h)
        if isinstance(out, tuple):
            return (corrected,) + out[1:]
        return corrected

    hook = layers[target_layer].register_forward_hook(correction_hook)

    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
    log(f"  Pre-fitting PPL: {base_ppl:.2f}")

    optimizer = torch.optim.Adam(trainable_params, lr=lr)
    model.train()
    history = []
    t0 = time.time()

    for step in range(steps):
        optimizer.zero_grad()
        rng = np.random.RandomState(step)
        batch_idx = rng.choice(len(CALIBRATION_TEXTS),
                               min(4, len(CALIBRATION_TEXTS)),
                               replace=False)
        total_loss = 0.0
        total_tokens = 0

        for idx in batch_idx:
            enc = tokenizer(CALIBRATION_TEXTS[idx], return_tensors="pt",
                            truncation=True, max_length=128)
            enc = {k: v.to(device) for k, v in enc.items()}
            labels = enc["input_ids"].clone()

            out = model(**enc, labels=labels)
            if not (torch.isnan(out.loss) or torch.isinf(out.loss)):
                out.loss.backward()
                total_loss += out.loss.item() * labels.numel()
                total_tokens += labels.numel()

        if total_tokens == 0:
            continue

        torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=0.5)
        optimizer.step()
        avg = total_loss / total_tokens
        history.append(avg)

        if (step + 1) % 10 == 0 or step == 0:
            elapsed = time.time() - t0
            log(f"    step {step+1:>3d}: loss={avg:.4f} ({elapsed:.0f}s)")

    model.eval()
    hook.remove()

    post_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
    post_facts, total_facts = measure_facts(model, tokenizer, device)
    log(f"  Post-fitting PPL: {post_ppl:.2f} ({post_ppl/base_ppl:.3f}x)")
    log(f"  Facts: {post_facts}/{total_facts}")

    return {
        "ppl": post_ppl,
        "ppl_ratio": round(post_ppl / base_ppl, 4),
        "facts": post_facts,
        "total_params": total_params,
        "loss_history": [round(x, 4) for x in history],
    }


# ══════════════════════════════════════════════════════════════
# Residual spectrum analysis
# ══════════════════════════════════════════════════════════════

def analyze_residual_spectrum(model, original_weights, device):
    """Compute SVD spectrum of W_residual = W_original - W_current.

    Shows how much error remains and how compressible it is.
    """
    log(f"\n{'═'*70}")
    log("  RESIDUAL SPECTRUM ANALYSIS")
    log(f"{'═'*70}")

    layers = get_layers(model)
    spectra = {}

    for li, orig_weights in original_weights.items():
        layer_spectra = {}
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)

            # Get current weight
            if isinstance(proj, FrozenSieveLinear):
                W_current = proj.W_sieve.float()
            elif isinstance(proj, FrozenLowRankLinear):
                W_current = (proj.A @ proj.B).float()
            else:
                W_current = proj.weight.detach().float()

            # Residual
            W_orig = orig_weights[pname].float().to(W_current.device)
            W_residual = W_orig - W_current

            # SVD of residual — just top singular values
            with torch.no_grad():
                S = torch.linalg.svdvals(W_residual.cpu())

            # Cumulative energy
            total_energy = (S ** 2).sum().item()
            cum_energy = torch.cumsum(S ** 2, dim=0) / total_energy

            # Find rank needed for 90%, 95%, 99% of residual energy
            r90 = int((cum_energy >= 0.90).float().argmax().item()) + 1
            r95 = int((cum_energy >= 0.95).float().argmax().item()) + 1
            r99 = int((cum_energy >= 0.99).float().argmax().item()) + 1

            residual_norm = W_residual.norm().item()
            original_norm = W_orig.norm().item()

            layer_spectra[pname] = {
                "residual_frac": round(residual_norm / original_norm, 4),
                "r90": r90, "r95": r95, "r99": r99,
                "top10_sv": [round(s, 2) for s in S[:10].tolist()],
            }

        spectra[li] = layer_spectra

    # Summary table
    log(f"\n  {'Layer':>6s}  {'Proj':>9s}  {'|res|/|W|':>10s}"
        f"  {'r90':>4s}  {'r95':>4s}  {'r99':>4s}")
    log(f"  {'─'*6}  {'─'*9}  {'─'*10}  {'─'*4}  {'─'*4}  {'─'*4}")
    for li in sorted(spectra.keys()):
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            sp = spectra[li][pname]
            log(f"  L{li:>3d}   {pname:>9s}  {sp['residual_frac']:>10.4f}"
                f"  {sp['r90']:>4d}  {sp['r95']:>4d}  {sp['r99']:>4d}")

    return spectra


# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--zero-rate", type=float, default=0.5)
    p.add_argument("--rank", type=int, default=32,
                   help="Rank per boosting round")
    p.add_argument("--n-rounds", type=int, default=6,
                   help="Number of sequential boosting rounds")
    p.add_argument("--steps-per-round", type=int, default=50,
                   help="Training steps per boosting round")
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--skip-simultaneous", action="store_true",
                   help="Skip mode B (simultaneous) to save time")
    p.add_argument("--skip-single", action="store_true",
                   help="Skip mode C (single high-rank)")
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]

    log(f"\n{'='*70}")
    log("  RESIDUAL BOOSTING — Compression as iterative weak learners")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  Sieve layers: {len(SIEVE_LAYERS)}")
    log(f"  Rank per round: {args.rank}")
    log(f"  Rounds: {args.n_rounds}")
    log(f"  Steps/round: {args.steps_per_round}")

    # ── Load ──────────────────────────────────────────────
    dtype = (torch.float16
             if any(s in args.model for s in ["8B", "14B", "32B"])
             else torch.float32)
    log(f"\n  Loading {args.model} ({dtype})...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device,
        attn_implementation="eager")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    d_model = model.config.hidden_size
    log(f"  d_model={d_model}")

    # ── Baseline ──────────────────────────────────────────
    log("\n  Measuring baseline...")
    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    base_facts, total_facts = measure_facts(model, tokenizer, args.device)
    log(f"  Baseline PPL: {base_ppl:.2f}, facts: {base_facts}/{total_facts}")

    # ── Capture teacher states BEFORE sieving ─────────────
    log("\n  Capturing teacher boundary states...")
    teacher_states = capture_boundary_states(
        model, tokenizer, CALIBRATION_TEXTS[:8], args.device)

    # ── Save original weights for spectrum analysis ───────
    log("  Saving original FFN weights...")
    layers = get_layers(model)
    original_weights = {}
    for li in SIEVE_LAYERS[:5] + [SIEVE_LAYERS[-1]]:  # sample for speed
        orig = {}
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            orig[pname] = getattr(mlp, pname).weight.detach().cpu().clone()
        original_weights[li] = orig

    # ═══════════════════════════════════════════════════════
    # Install crystal sieve (Round 0)
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  ROUND 0: CRYSTAL SIEVE")
    log(f"{'═'*70}")

    # L0 SVD
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, 750)
        setattr(mlp0, pname,
                FrozenLowRankLinear(A.to(args.device),
                                   B.to(args.device)))

    # Sieve remaining layers
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)
            setattr(mlp, pname,
                    FrozenSieveLinear(proj.weight,
                                     zero_rate=args.zero_rate).to(args.device))

    log(f"  Sieve installed on {len(SIEVE_LAYERS)} layers + L0 SVD")

    # Post-sieve measurement
    sieve_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    sieve_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"  Sieve PPL: {sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)"
        f"  facts: {sieve_facts}/{total_facts}")

    # ── Residual spectrum analysis ────────────────────────
    spectra = analyze_residual_spectrum(model, original_weights, args.device)

    # ═══════════════════════════════════════════════════════
    # MODE A: Sequential Boosting
    # ═══════════════════════════════════════════════════════
    seq_results, seq_corrections = run_sequential_boosting(
        model, tokenizer, teacher_states, args.device,
        n_rounds=args.n_rounds,
        rank=args.rank,
        steps_per_round=args.steps_per_round,
        lr=args.lr,
    )

    # Need to reload model for fair comparison of Mode B and C
    # (model is mutated by Mode A's sieve + corrections)

    # ═══════════════════════════════════════════════════════
    # MODE B: Simultaneous Fitting (if not skipped)
    # ═══════════════════════════════════════════════════════
    sim_result = None
    if not args.skip_simultaneous:
        # Reload and re-sieve for fair comparison
        log("\n  Reloading model for simultaneous comparison...")
        del model
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        import gc; gc.collect()

        model = AutoModelForCausalLM.from_pretrained(
            args.model, torch_dtype=dtype, device_map=args.device,
            attn_implementation="eager")
        model.eval()
        layers = get_layers(model)

        # Re-install sieve
        mlp0 = layers[0].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp0, pname)
            A, B = svd_factorize(proj.weight, 750)
            setattr(mlp0, pname,
                    FrozenLowRankLinear(A.to(args.device),
                                       B.to(args.device)))
        for li in SIEVE_LAYERS:
            mlp = layers[li].mlp
            for pname in ["gate_proj", "up_proj", "down_proj"]:
                proj = getattr(mlp, pname)
                setattr(mlp, pname,
                        FrozenSieveLinear(proj.weight,
                                         zero_rate=args.zero_rate).to(args.device))

        # Use the SAME layers that sequential chose
        seq_layers = list(set(
            r["target_layer"] for r in seq_results
        ))
        # If sequential chose fewer unique layers, pad with boundary defaults
        if len(seq_layers) < args.n_rounds:
            for name, li in BOUNDARIES.items():
                if li not in seq_layers:
                    seq_layers.append(li)
                if len(seq_layers) >= args.n_rounds:
                    break

        sim_result = run_simultaneous_fitting(
            model, tokenizer, teacher_states, args.device,
            placement_layers=seq_layers[:args.n_rounds],
            rank=args.rank,
            steps=args.steps_per_round * args.n_rounds,  # same total steps
            lr=args.lr,
        )

    # ═══════════════════════════════════════════════════════
    # MODE C: Single High-Rank (if not skipped)
    # ═══════════════════════════════════════════════════════
    single_result = None
    if not args.skip_single:
        # Reload and re-sieve
        log("\n  Reloading model for single-rank comparison...")
        del model
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        import gc; gc.collect()

        model = AutoModelForCausalLM.from_pretrained(
            args.model, torch_dtype=dtype, device_map=args.device,
            attn_implementation="eager")
        model.eval()
        layers = get_layers(model)

        mlp0 = layers[0].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp0, pname)
            A, B = svd_factorize(proj.weight, 750)
            setattr(mlp0, pname,
                    FrozenLowRankLinear(A.to(args.device),
                                       B.to(args.device)))
        for li in SIEVE_LAYERS:
            mlp = layers[li].mlp
            for pname in ["gate_proj", "up_proj", "down_proj"]:
                proj = getattr(mlp, pname)
                setattr(mlp, pname,
                        FrozenSieveLinear(proj.weight,
                                         zero_rate=args.zero_rate).to(args.device))

        # Same total rank as sequential (n_rounds × rank)
        total_rank = args.n_rounds * args.rank
        # Place at the worst boundary from sequential round 1
        target = seq_results[0]["target_layer"] if seq_results else 21

        single_result = run_single_highrank(
            model, tokenizer, teacher_states, args.device,
            target_layer=target,
            total_rank=total_rank,
            steps=args.steps_per_round * args.n_rounds,
            lr=args.lr,
        )

    # ═══════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  COMPARISON SUMMARY")
    log(f"{'='*70}")

    log(f"\n  Baseline:     PPL={base_ppl:.2f}  facts={base_facts}/{total_facts}")
    log(f"  Sieve only:   PPL={sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)")

    log(f"\n  Sequential boosting ({args.n_rounds} rounds):")
    for r in seq_results:
        log(f"    Round {r['round']}: L{r['target_layer']:>2d} ({r['target_name']:>15s})"
            f"  PPL={r['ppl']:.2f} ({r['ppl_ratio']:.3f}x)"
            f"  facts={r['facts']}/{total_facts}"
            f"  params={r['cumulative_params']:,}")

    if sim_result:
        log(f"\n  Simultaneous:  PPL={sim_result['ppl']:.2f}"
            f" ({sim_result['ppl_ratio']:.3f}x)"
            f"  facts={sim_result['facts']}/{total_facts}"
            f"  params={sim_result['total_params']:,}")

    if single_result:
        log(f"\n  Single rank-{args.n_rounds * args.rank}:"
            f"  PPL={single_result['ppl']:.2f}"
            f" ({single_result['ppl_ratio']:.3f}x)"
            f"  facts={single_result['facts']}/{total_facts}"
            f"  params={single_result['total_params']:,}")

    # ── Save results ──────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "residual-boosting"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    result = {
        "model": args.model,
        "config": {
            "rank": args.rank,
            "n_rounds": args.n_rounds,
            "steps_per_round": args.steps_per_round,
            "lr": args.lr,
            "zero_rate": args.zero_rate,
            "sieve_layers": SIEVE_LAYERS,
        },
        "baseline_ppl": base_ppl,
        "baseline_facts": base_facts,
        "sieve_ppl": sieve_ppl,
        "sieve_ratio": round(sieve_ppl / base_ppl, 4),
        "sieve_facts": sieve_facts,
        "residual_spectra": {
            str(k): v for k, v in spectra.items()
        },
        "sequential": seq_results,
        "simultaneous": sim_result,
        "single_highrank": single_result,
    }

    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Results saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
