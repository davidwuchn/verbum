#!/usr/bin/env python3
"""Residual Boosting v2 — proper calibration with dolma shards.

v1 confirmed: sequential boosting is 2× better than simultaneous.
v1 problems: (a) 16 calibration sentences → overfitting, (b) greedy
placement gets stuck at L35.

v2 fixes:
  - Calibration: dolma shards (real prose, thousands of sequences)
  - Eval: held-out dolma sequences (no overlap with calibration)
  - Placement: round-robin across all boundaries, not greedy
  - No simultaneous mode (established: sequential wins)
  - Expanded residual spectrum: sample all functional zones

Usage:
  uv run python scripts/experiments/residual_boosting_v2.py \
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

SHARD_DIR = Path.home() / "data" / "fractal-bitnet" / "shards-qwen3"
EOD_ID = 151643


# ══════════════════════════════════════════════════════════════
# Data loading from pre-tokenized shards
# ══════════════════════════════════════════════════════════════

def load_sequences(shard_path, n_sequences, seq_len=128, offset=0):
    """Load n_sequences of length seq_len from a shard.

    Splits on EOD tokens to get document boundaries, then takes
    contiguous chunks of seq_len. offset skips the first N tokens
    (use to separate calibration from eval).
    """
    data = np.load(shard_path)
    data = data[offset:]

    sequences = []
    pos = 0
    while len(sequences) < n_sequences and pos + seq_len < len(data):
        chunk = data[pos:pos + seq_len]
        # Skip chunks with EOD in the middle (document boundary)
        eod_positions = np.where(chunk == EOD_ID)[0]
        if len(eod_positions) == 0:
            sequences.append(torch.tensor(chunk, dtype=torch.long))
            pos += seq_len
        else:
            # Jump past the EOD
            pos += int(eod_positions[0]) + 1

    return sequences


# ══════════════════════════════════════════════════════════════
# Fact prompts (small, for tracking knowledge retention)
# ══════════════════════════════════════════════════════════════

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


def measure_ppl_tokens(model, sequences, device):
    """Measure PPL on pre-tokenized sequences."""
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    with torch.no_grad():
        for seq in sequences:
            input_ids = seq.unsqueeze(0).to(device)
            labels = input_ids.clone()
            out = model(input_ids=input_ids, labels=labels)
            n = labels.numel()
            total_loss += out.loss.item() * n
            total_tokens += n
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
# Boosted Residual Correction
# ══════════════════════════════════════════════════════════════

class ResidualCorrection(nn.Module):
    def __init__(self, d_model, rank=32):
        super().__init__()
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
# Functional boundaries
# ══════════════════════════════════════════════════════════════

BOUNDARIES = {
    "lexer":        0,
    "parser":       9,
    "composition": 21,
    "type_crystal": 26,
    "binding":     30,
    "output":      35,
}

# Round-robin order: spread across the depth axis
PLACEMENT_ORDER = [
    ("composition", 21),   # worst single-layer zone
    ("parser",       9),   # early processing
    ("type_crystal", 26),  # binding-prep
    ("binding",     30),   # binding
    ("output",      35),   # collapse
    ("lexer",        0),   # embedding
    # Repeat for more rounds
    ("composition", 21),
    ("parser",       9),
    ("type_crystal", 26),
    ("binding",     30),
    ("output",      35),
    ("lexer",        0),
]


def capture_boundary_states(model, sequences, device, max_seqs=32):
    """Capture teacher hidden states at boundaries."""
    layers = get_layers(model)
    all_states = {name: [] for name in BOUNDARIES}

    for seq in sequences[:max_seqs]:
        input_ids = seq.unsqueeze(0).to(device)
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
            model(input_ids=input_ids)

        for h in hooks:
            h.remove()

        for name, li in BOUNDARIES.items():
            if li in states:
                all_states[name].append(states[li])

    return all_states


def measure_boundary_fidelity(teacher_states, student_states):
    fidelity = {}
    for name in teacher_states:
        cos_vals = []
        n = min(len(teacher_states[name]), len(student_states[name]))
        for i in range(n):
            t = teacher_states[name][i]
            s = student_states[name][i]
            cos = F.cosine_similarity(
                t.float(), s.float(), dim=-1).mean().item()
            cos_vals.append(cos)
        fidelity[name] = float(np.mean(cos_vals)) if cos_vals else 0.0
    return fidelity


# ══════════════════════════════════════════════════════════════
# Training loop for one boosting round
# ══════════════════════════════════════════════════════════════

def train_one_round(model, correction, layer_idx,
                    cal_sequences, device,
                    steps=50, lr=1e-4, batch_size=4):
    """Train a single ResidualCorrection at layer_idx using token sequences."""
    layers = get_layers(model)

    def correction_hook(mod, inp, out):
        h = out[0] if isinstance(out, tuple) else out
        corrected = correction(h)
        if isinstance(out, tuple):
            return (corrected,) + out[1:]
        return corrected

    hook = layers[layer_idx].register_forward_hook(correction_hook)

    trainable = [correction.W_down, correction.W_up]
    optimizer = torch.optim.Adam(trainable, lr=lr)

    model.train()
    history = []
    t0 = time.time()
    n_cal = len(cal_sequences)

    for step in range(steps):
        optimizer.zero_grad()
        rng = np.random.RandomState(step + layer_idx * 1000)
        batch_idx = rng.choice(n_cal, min(batch_size, n_cal), replace=False)

        total_loss = 0.0
        total_tokens = 0

        for idx in batch_idx:
            input_ids = cal_sequences[idx].unsqueeze(0).to(device)
            labels = input_ids.clone()

            out = model(input_ids=input_ids, labels=labels)
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
# Residual spectrum (expanded: sample all zones)
# ══════════════════════════════════════════════════════════════

def analyze_residual_spectrum(model, original_weights, device):
    log(f"\n{'═'*70}")
    log("  RESIDUAL SPECTRUM ANALYSIS")
    log(f"{'═'*70}")

    layers = get_layers(model)
    spectra = {}

    for li, orig_weights in sorted(original_weights.items()):
        layer_spectra = {}
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)

            if isinstance(proj, FrozenSieveLinear):
                W_current = proj.W_sieve.float()
            elif isinstance(proj, FrozenLowRankLinear):
                W_current = (proj.A @ proj.B).float()
            else:
                W_current = proj.weight.detach().float()

            W_orig = orig_weights[pname].float().to(W_current.device)
            W_residual = W_orig - W_current

            with torch.no_grad():
                S = torch.linalg.svdvals(W_residual.cpu())

            total_energy = (S ** 2).sum().item()
            if total_energy < 1e-12:
                layer_spectra[pname] = {
                    "residual_frac": 0.0, "r90": 0, "r95": 0, "r99": 0,
                    "top5_sv": [0.0] * 5,
                }
                continue

            cum_energy = torch.cumsum(S ** 2, dim=0) / total_energy
            r90 = int((cum_energy >= 0.90).float().argmax().item()) + 1
            r95 = int((cum_energy >= 0.95).float().argmax().item()) + 1
            r99 = int((cum_energy >= 0.99).float().argmax().item()) + 1

            residual_norm = W_residual.norm().item()
            original_norm = W_orig.norm().item()

            layer_spectra[pname] = {
                "residual_frac": round(residual_norm / max(original_norm, 1e-12), 4),
                "r90": r90, "r95": r95, "r99": r99,
                "top5_sv": [round(s, 2) for s in S[:5].tolist()],
            }

        spectra[li] = layer_spectra

    # Summary table
    log(f"\n  {'Layer':>6s}  {'Proj':>9s}  {'|res|/|W|':>10s}"
        f"  {'r90':>4s}  {'r95':>4s}  {'r99':>4s}  {'Zone':>12s}")
    log(f"  {'─'*6}  {'─'*9}  {'─'*10}  {'─'*4}  {'─'*4}  {'─'*4}  {'─'*12}")

    zone_map = {
        0: "L0 (SVD)", 1: "EXPAND", 5: "EXPAND",
        10: "ORTHO-early", 15: "SWEET SPOT", 18: "SWEET SPOT",
        22: "BIND-PREP", 25: "BIND-PREP",
        30: "BINDING", 34: "LATE",
    }

    for li in sorted(spectra.keys()):
        zone = zone_map.get(li, "?")
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            sp = spectra[li][pname]
            log(f"  L{li:>3d}   {pname:>9s}  {sp['residual_frac']:>10.4f}"
                f"  {sp['r90']:>4d}  {sp['r95']:>4d}  {sp['r99']:>4d}"
                f"  {zone:>12s}")

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
    p.add_argument("--rank", type=int, default=32)
    p.add_argument("--n-rounds", type=int, default=8)
    p.add_argument("--steps-per-round", type=int, default=50)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--n-cal", type=int, default=256,
                   help="Number of calibration sequences")
    p.add_argument("--n-eval", type=int, default=64,
                   help="Number of eval sequences")
    p.add_argument("--seq-len", type=int, default=128)
    p.add_argument("--shard-dir", type=str,
                   default=str(SHARD_DIR))
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]

    # Representative layers from each zone for spectrum analysis
    SPECTRUM_LAYERS = [1, 5, 10, 15, 18, 22, 25, 30, 34]

    log(f"\n{'='*70}")
    log("  RESIDUAL BOOSTING v2 — dolma calibration, round-robin placement")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  Calibration: {args.n_cal} sequences × {args.seq_len} tokens")
    log(f"  Eval: {args.n_eval} sequences × {args.seq_len} tokens")
    log(f"  Rank per round: {args.rank}")
    log(f"  Rounds: {args.n_rounds}")
    log(f"  Steps/round: {args.steps_per_round}")

    # ── Load data ─────────────────────────────────────────
    shard_path = Path(args.shard_dir) / "shard_00000.npy"
    log(f"\n  Loading sequences from {shard_path.name}...")

    # Calibration from start of shard
    cal_sequences = load_sequences(
        shard_path, args.n_cal, seq_len=args.seq_len, offset=0)
    # Eval from later in shard (no overlap)
    eval_offset = args.n_cal * args.seq_len * 2  # 2× buffer for skipped EODs
    eval_sequences = load_sequences(
        shard_path, args.n_eval, seq_len=args.seq_len, offset=eval_offset)

    log(f"  Loaded {len(cal_sequences)} cal + {len(eval_sequences)} eval sequences")

    # ── Load model ────────────────────────────────────────
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
    base_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    base_facts, total_facts = measure_facts(model, tokenizer, args.device)
    log(f"  Baseline PPL: {base_ppl:.2f}, facts: {base_facts}/{total_facts}")

    # ── Capture teacher states ────────────────────────────
    log("  Capturing teacher boundary states...")
    teacher_states = capture_boundary_states(
        model, cal_sequences, args.device, max_seqs=32)

    # ── Save original weights for spectrum ────────────────
    log("  Saving original FFN weights for spectrum analysis...")
    layers = get_layers(model)
    original_weights = {}
    for li in SPECTRUM_LAYERS:
        if li in SIEVE_LAYERS or li == 0:
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

    sieve_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    sieve_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"  Sieve PPL: {sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)"
        f"  facts: {sieve_facts}/{total_facts}")

    # ── Residual spectrum ─────────────────────────────────
    spectra = analyze_residual_spectrum(model, original_weights, args.device)

    # ═══════════════════════════════════════════════════════
    # Sequential Boosting with round-robin placement
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  SEQUENTIAL BOOSTING — round-robin placement")
    log(f"  {args.n_rounds} rounds × rank-{args.rank}"
        f" × {args.steps_per_round} steps")
    log(f"{'═'*70}")

    corrections = []
    active_hooks = []
    round_results = []
    cumulative_params = 0

    pre_boost_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    log(f"\n  Pre-boosting PPL: {pre_boost_ppl:.2f}")

    for round_idx in range(args.n_rounds):
        # Round-robin placement
        placement_name, target_layer = PLACEMENT_ORDER[
            round_idx % len(PLACEMENT_ORDER)]

        log(f"\n  ── Round {round_idx + 1}/{args.n_rounds} ─────────────")

        # Measure boundary fidelity
        student_states = capture_boundary_states(
            model, cal_sequences, args.device, max_seqs=32)
        fidelity = measure_boundary_fidelity(teacher_states, student_states)

        log(f"    Boundary fidelity:")
        for name in BOUNDARIES:
            marker = " ← TARGET" if name == placement_name else ""
            log(f"      {name:>15s}: {fidelity[name]:.4f}{marker}")

        # Create and train correction
        correction = ResidualCorrection(d_model, rank=args.rank).to(args.device)
        cumulative_params += correction.n_params

        log(f"    Placing rank-{args.rank} correction at"
            f" L{target_layer} ({placement_name})")
        log(f"    Training {correction.n_params:,} params"
            f" (cumulative: {cumulative_params:,})...")

        loss_history = train_one_round(
            model, correction, target_layer,
            cal_sequences, args.device,
            steps=args.steps_per_round, lr=args.lr)

        # Freeze and install permanently
        correction.eval()
        for param in correction.parameters():
            param.requires_grad_(False)

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

        # Measure on HELD-OUT eval
        round_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
        round_facts, _ = measure_facts(model, tokenizer, args.device)

        ppl_vs_base = round_ppl / base_ppl
        ppl_vs_sieve = round_ppl / sieve_ppl

        log(f"    Eval PPL: {round_ppl:.2f}"
            f" ({ppl_vs_base:.3f}x base, {ppl_vs_sieve:.3f}x sieve)")
        log(f"    Facts: {round_facts}/{total_facts}")

        round_results.append({
            "round": round_idx + 1,
            "target_layer": target_layer,
            "target_name": placement_name,
            "fidelity_before": fidelity,
            "eval_ppl": round_ppl,
            "ppl_vs_base": round(ppl_vs_base, 4),
            "ppl_vs_sieve": round(ppl_vs_sieve, 4),
            "facts": round_facts,
            "cumulative_params": cumulative_params,
            "loss_history": [round(x, 4) for x in loss_history],
        })

    # Cleanup
    for h in active_hooks:
        h.remove()

    # ═══════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  RESULTS")
    log(f"{'='*70}")

    log(f"\n  Baseline:   PPL={base_ppl:.2f}  facts={base_facts}/{total_facts}")
    log(f"  Sieve only: PPL={sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)")

    log(f"\n  Sequential boosting ({args.n_rounds} rounds, round-robin):")
    log(f"  {'Rnd':>3s}  {'Layer':>7s}  {'Name':>15s}"
        f"  {'PPL':>7s}  {'vs base':>8s}  {'vs sieve':>9s}"
        f"  {'Facts':>5s}  {'Params':>10s}")
    log(f"  {'─'*3}  {'─'*7}  {'─'*15}  {'─'*7}  {'─'*8}  {'─'*9}"
        f"  {'─'*5}  {'─'*10}")

    for r in round_results:
        log(f"  {r['round']:>3d}  L{r['target_layer']:>5d}"
            f"  {r['target_name']:>15s}"
            f"  {r['eval_ppl']:>7.2f}  {r['ppl_vs_base']:>8.3f}x"
            f"  {r['ppl_vs_sieve']:>9.3f}x"
            f"  {r['facts']:>3d}/15"
            f"  {r['cumulative_params']:>10,}")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "residual-boosting"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    result = {
        "model": args.model,
        "version": "v2",
        "config": {
            "rank": args.rank,
            "n_rounds": args.n_rounds,
            "steps_per_round": args.steps_per_round,
            "lr": args.lr,
            "zero_rate": args.zero_rate,
            "n_cal": len(cal_sequences),
            "n_eval": len(eval_sequences),
            "seq_len": args.seq_len,
            "sieve_layers": SIEVE_LAYERS,
            "placement": "round_robin",
        },
        "baseline_ppl": base_ppl,
        "baseline_facts": base_facts,
        "sieve_ppl": sieve_ppl,
        "sieve_ratio": round(sieve_ppl / base_ppl, 4),
        "sieve_facts": sieve_facts,
        "residual_spectra": {
            str(k): v for k, v in spectra.items()
        },
        "rounds": round_results,
    }

    out_path = out_dir / f"{slug}_v2.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Results saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
