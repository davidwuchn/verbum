#!/usr/bin/env python3
"""Topology-Aware Score Matching — TD routing + LoRA magnitudes.

The v3b score matching loss treats each layer's residual update as
a flat vector. But the sieve error has two orthogonal components:

  routing_error:    wrong signs → wrong program selected (discrete, sparse)
  magnitude_error:  right sign, wrong scale (continuous, low-rank)

LoRA wastes rank capacity on sign flips. TernaryDescent is purpose-built
for sign discovery. Split them:

  W_eff = (signs_base + sign_corrections) * (magnitudes + LoRA)

TD handles routing (which signs to flip). LoRA handles magnitudes.
The loss decomposes to match both independently:

  L = L_CE + α_route · L_routing + α_value · L_value

  L_routing: gate firing pattern match (which neurons fire)
  L_value:   residual update cosine (how much they contribute)

Usage:
  uv run python scripts/experiments/topology_score_matching.py \
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
# Data
# ══════════════════════════════════════════════════════════════

def load_sequences(shard_path, n_sequences, seq_len=128, offset=0):
    data = np.load(shard_path)
    data = data[offset:]
    sequences = []
    pos = 0
    while len(sequences) < n_sequences and pos + seq_len < len(data):
        chunk = data[pos:pos + seq_len]
        eod_positions = np.where(chunk == EOD_ID)[0]
        if len(eod_positions) == 0:
            sequences.append(torch.tensor(chunk, dtype=torch.long))
            pos += seq_len
        else:
            pos += int(eod_positions[0]) + 1
    return sequences


FACT_PROMPTS = [
    {"prompt": "The capital of France is", "expected": "Paris"},
    {"prompt": "The capital of Japan is", "expected": "Tokyo"},
    {"prompt": "Water boils at", "expected": "100"},
    {"prompt": "The speed of light is approximately", "expected": "300"},
    {"prompt": "The first president of the United States was",
     "expected": "George Washington"},
    {"prompt": "The year World War II ended was", "expected": "1945"},
    {"prompt": "The chemical symbol for gold is", "expected": "Au"},
    {"prompt": "The largest planet in our solar system is",
     "expected": "Jupiter"},
    {"prompt": "The author of Romeo and Juliet is",
     "expected": "Shakespeare"},
    {"prompt": "Pi is approximately equal to", "expected": "3.14"},
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
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    with torch.no_grad():
        for seq in sequences:
            input_ids = seq.unsqueeze(0).to(device)
            labels = input_ids.clone()
            out = model(input_ids=input_ids, labels=labels)
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
# Straight-Through Sign Correction (PyTorch STE for TD)
# ══════════════════════════════════════════════════════════════

class STESign(torch.autograd.Function):
    """Straight-through estimator for sign function.

    Forward: hard sign {-1, 0, +1}
    Backward: gradient passes through as-is (identity)
    """

    @staticmethod
    def forward(ctx, x):
        return torch.sign(x)

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output  # straight-through


def ste_sign(x):
    return STESign.apply(x)


# ══════════════════════════════════════════════════════════════
# TD+LoRA Sieved Linear
# ══════════════════════════════════════════════════════════════

class TDLoRASieveLinear(nn.Module):
    """Crystal sieve with split routing (TD) and magnitude (LoRA) corrections.

    W_eff = corrected_signs * corrected_magnitudes

    corrected_signs = sign(W_base) * ste_sign(delta_logits)
      delta_logits: initialized to +0.01 (small positive = keep base sign,
        but only needs to cross 0 to flip — NOT travel from +1.0)
      STE gradient flows through sign() to update logits
      A flip happens when delta_logit crosses zero

    corrected_magnitudes = |W_base| * mask + A @ B
      LoRA correction on the magnitude part only

    TD logits are ONLY created for non-masked positions (where signs_base != 0).
    Masked positions have signs_base=0, so sign corrections have no effect there
    and would waste gradient budget.

    The routing (signs) and calibration (magnitudes) are separate
    parameter groups with separate learning rates and separate grad clipping.
    """

    def __init__(self, weight, zero_rate=0.5, lora_rank=4):
        super().__init__()
        W = weight.detach().float().cpu()
        out_features, in_features = W.shape
        abs_W = W.abs()

        # Build mask
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

        # Frozen components
        signs_base = torch.sign(W)
        magnitudes = abs_W * mask
        self.register_buffer("signs_base", signs_base.half())
        self.register_buffer("magnitudes", magnitudes.half())
        self.register_buffer("active_mask", (signs_base != 0).float())

        # TD: sign correction logits — initialized to +0.01 (small positive)
        # FIX: init near zero so flips require crossing ~0, not traveling 1.0
        # Only active (non-masked) positions matter, but we keep full shape
        # for simple indexing. Masked positions get no gradient because
        # signs_base=0 kills the gradient path.
        self.delta_logits = nn.Parameter(
            torch.full((out_features, in_features), 0.01))

        # LoRA: magnitude correction — initialized to zero
        self.lora_A = nn.Parameter(
            torch.randn(out_features, lora_rank) * 0.01)
        self.lora_B = nn.Parameter(
            torch.zeros(lora_rank, in_features))

        self.out_features = out_features
        self.in_features = in_features
        self.lora_rank = lora_rank
        self._n_active = int(self.active_mask.sum().item())

    def forward(self, x):
        # Routing: base signs * STE(delta_logits)
        delta_signs = ste_sign(self.delta_logits)  # {-1, +1}
        effective_signs = self.signs_base.float() * delta_signs

        # Magnitudes: frozen + LoRA correction
        mag = self.magnitudes.float()
        lora_mag = self.lora_A @ self.lora_B  # (out, in)

        # W_eff = signs * (magnitudes + lora)
        W_eff = effective_signs * (mag + lora_mag)

        out = x.float() @ W_eff.T
        return out.clamp(-65000, 65000).to(x.dtype)

    @property
    def n_flips(self):
        """Count how many active signs have flipped from initial."""
        with torch.no_grad():
            current = torch.sign(self.delta_logits)
            # Started at +0.01, so initial sign is +1
            flipped = (current < 0).float() * self.active_mask.to(
                current.device)
            return int(flipped.sum().item())

    @property
    def flip_rate(self):
        return self.n_flips / max(self._n_active, 1)

    @property
    def td_params(self):
        return [self.delta_logits]

    @property
    def lora_params(self):
        return [self.lora_A, self.lora_B]

    @property
    def n_td_params(self):
        return self._n_active  # only active positions matter

    @property
    def n_lora_params(self):
        return self.lora_A.numel() + self.lora_B.numel()


class FrozenLowRankWithTDLoRA(nn.Module):
    """L0 SVD with TD sign corrections + LoRA magnitude corrections."""

    def __init__(self, A, B, lora_rank=4):
        super().__init__()
        self.register_buffer("svd_A", A)
        self.register_buffer("svd_B", B)
        out_f = A.shape[0]
        in_f = B.shape[1]

        # TD on the SVD factors' effective signs
        # Approximate: correct the reconstructed weight's signs
        # For L0, just use LoRA (SVD is already good, r90=550)
        self.lora_A = nn.Parameter(
            torch.randn(out_f, lora_rank) * 0.01)
        self.lora_B = nn.Parameter(
            torch.zeros(lora_rank, in_f))

    def forward(self, x):
        base_out = x.float() @ self.svd_B.T @ self.svd_A.T
        lora_out = x.float() @ self.lora_B.T @ self.lora_A.T
        return (base_out + lora_out).clamp(-65000, 65000).to(x.dtype)

    @property
    def td_params(self):
        return []  # no TD on L0

    @property
    def lora_params(self):
        return [self.lora_A, self.lora_B]


def svd_factorize(weight, rank):
    W = weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))
    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)
    return A, B


# ══════════════════════════════════════════════════════════════
# Teacher state caching
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def cache_teacher_states(model, sequences, device, max_seqs=128):
    """Cache per-layer hidden states + gate activations from teacher."""
    layers = get_layers(model)
    n_layers = len(layers)
    all_states = []

    for seq_idx, seq in enumerate(sequences[:max_seqs]):
        input_ids = seq.unsqueeze(0).to(device)
        layer_states = {}
        gate_patterns = {}
        hooks = []

        # Pre-hook on first layer for embedding output
        def embed_hook(mod, args):
            h = args[0] if isinstance(args, tuple) else args
            layer_states[-1] = h[0].detach().cpu().half()
        hooks.append(layers[0].register_forward_pre_hook(embed_hook))

        # Post-hook on each layer for hidden states
        def make_state_hook(li):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                layer_states[li] = h[0].detach().cpu().half()
            return hook_fn

        # Hook on gate_proj for routing pattern
        def make_gate_hook(li):
            def hook_fn(mod, inp, out):
                # Capture sign(gate_output) as the routing pattern
                gate_patterns[li] = (out[0] > 0).detach().cpu()
            return hook_fn

        for li in range(n_layers):
            hooks.append(layers[li].register_forward_hook(
                make_state_hook(li)))
            # Hook gate_proj to capture firing pattern
            if hasattr(layers[li].mlp, 'gate_proj'):
                hooks.append(layers[li].mlp.gate_proj.register_forward_hook(
                    make_gate_hook(li)))

        model(input_ids=input_ids)
        for h in hooks:
            h.remove()

        # Stack hidden states
        state_list = [layer_states.get(-1, torch.zeros(1))]
        for li in range(n_layers):
            state_list.append(layer_states.get(li, torch.zeros(1)))
        stacked = torch.stack(state_list, dim=0)

        all_states.append({
            "hidden": stacked,
            "gates": gate_patterns,
        })

        if (seq_idx + 1) % 32 == 0:
            log(f"      {seq_idx + 1}/{min(max_seqs, len(sequences))} cached")

    return all_states


# ══════════════════════════════════════════════════════════════
# Topology-Aware Score Matching Loss
# ══════════════════════════════════════════════════════════════

def compute_topology_loss(model, input_ids, teacher_data,
                          sieve_layers, device):
    """Compute decomposed loss: CE + routing + value.

    L_routing: gate firing pattern match (which neurons fire)
    L_value:   residual update cosine match (how much they contribute)

    Returns: (ce_loss, routing_loss, value_loss, diagnostics)
    """
    layers = get_layers(model)
    n_layers = len(layers)
    teacher_hidden = teacher_data["hidden"]
    teacher_gates = teacher_data["gates"]

    # Capture student states and gate patterns
    student_states = {}
    student_gates = {}

    def pre_hook(mod, args):
        h = args[0] if isinstance(args, tuple) else args
        student_states[-1] = h[0]
    hooks = [layers[0].register_forward_pre_hook(pre_hook)]

    def make_state_hook(li):
        def hook_fn(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            student_states[li] = h[0]
        return hook_fn

    def make_gate_hook(li):
        def hook_fn(mod, inp, out):
            student_gates[li] = out[0]  # keep grad for routing loss
        return hook_fn

    for li in range(n_layers):
        hooks.append(layers[li].register_forward_hook(
            make_state_hook(li)))
        if hasattr(layers[li].mlp, 'gate_proj'):
            hooks.append(layers[li].mlp.gate_proj.register_forward_hook(
                make_gate_hook(li)))

    # Forward pass
    labels = input_ids.clone()
    out = model(input_ids=input_ids, labels=labels)
    ce_loss = out.loss

    for h in hooks:
        h.remove()

    # === Routing loss: gate firing pattern match ===
    routing_loss = torch.tensor(0.0, device=device)
    n_routing = 0
    routing_accuracy = {}

    for li in sieve_layers:
        if li not in student_gates or li not in teacher_gates:
            continue

        s_gate = student_gates[li].float()       # (seq, ffn_dim), with grad
        t_pattern = teacher_gates[li].float().to(device)  # (seq, ffn_dim), binary

        # FIX: use bce_with_logits — numerically stable, avoids log(0).
        # sigmoid(±65000) ≈ 0 or 1, then log(0) = -inf → NaN in BCE.
        # with_logits fuses log-sigmoid for stability.
        bce = F.binary_cross_entropy_with_logits(
            s_gate, t_pattern, reduction='mean')

        if not (torch.isnan(bce) or torch.isinf(bce)):
            routing_loss = routing_loss + bce
            n_routing += 1

        # Diagnostic: firing pattern accuracy
        with torch.no_grad():
            s_pattern = (s_gate > 0).float()
            acc = (s_pattern == t_pattern).float().mean().item()
            routing_accuracy[li] = acc

    if n_routing > 0:
        routing_loss = routing_loss / n_routing

    # === Value loss: residual update cosine match ===
    value_loss = torch.tensor(0.0, device=device)
    n_value = 0
    value_cosine = {}

    for li in range(n_layers):
        if li not in student_states:
            continue
        s_prev = student_states[-1] if li == 0 else student_states.get(li - 1)
        if s_prev is None:
            continue

        s_delta = student_states[li].float() - s_prev.float()
        t_delta = (teacher_hidden[li + 1].float().to(device)
                   - teacher_hidden[li].float().to(device))

        # NaN protection: skip layers with zero-norm deltas
        s_norm = s_delta.norm(dim=-1, keepdim=True)
        t_norm = t_delta.norm(dim=-1, keepdim=True)
        valid = ((s_norm > 1e-8) & (t_norm > 1e-8)).squeeze(-1)
        if valid.any():
            cos = F.cosine_similarity(s_delta, t_delta, dim=-1)
            # Only use valid positions
            mean_cos = cos[valid].mean()
            if not torch.isnan(mean_cos):
                value_loss = value_loss + (1.0 - mean_cos)
                value_cosine[li] = mean_cos.item()
                n_value += 1

    if n_value > 0:
        value_loss = value_loss / n_value

    diagnostics = {
        "routing_accuracy": routing_accuracy,
        "value_cosine": value_cosine,
    }

    return ce_loss, routing_loss, value_loss, diagnostics


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
    p.add_argument("--lora-rank", type=int, default=4)
    p.add_argument("--steps", type=int, default=200)
    p.add_argument("--lr-td", type=float, default=1e-3,
                   help="Learning rate for TD sign logits (Adam, per-tensor clip)")
    p.add_argument("--lr-lora", type=float, default=1e-4,
                   help="Learning rate for LoRA magnitudes")
    p.add_argument("--alpha-route", type=float, default=2.0,
                   help="Weight for routing loss")
    p.add_argument("--alpha-value", type=float, default=5.0,
                   help="Weight for value loss")
    p.add_argument("--n-cal", type=int, default=256)
    p.add_argument("--n-eval", type=int, default=64)
    p.add_argument("--n-teacher-cache", type=int, default=128)
    p.add_argument("--seq-len", type=int, default=128)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--eval-every", type=int, default=50)
    p.add_argument("--shard-dir", type=str, default=str(SHARD_DIR))
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]

    log(f"\n{'='*70}")
    log("  TOPOLOGY-AWARE SCORE MATCHING — TD routing + LoRA magnitudes")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  LoRA rank: {args.lora_rank}")
    log(f"  Steps: {args.steps}")
    log(f"  LR: TD={args.lr_td}, LoRA={args.lr_lora}")
    log(f"  α: routing={args.alpha_route}, value={args.alpha_value}")
    log(f"  Cal: {args.n_cal}, Eval: {args.n_eval},"
        f" Teacher cache: {args.n_teacher_cache}")

    # ── Load data ─────────────────────────────────────────
    shard_path = Path(args.shard_dir) / "shard_00000.npy"
    log(f"\n  Loading sequences from {shard_path.name}...")
    cal_sequences = load_sequences(
        shard_path, args.n_cal, seq_len=args.seq_len, offset=0)
    eval_offset = args.n_cal * args.seq_len * 2
    eval_sequences = load_sequences(
        shard_path, args.n_eval, seq_len=args.seq_len, offset=eval_offset)
    log(f"  Loaded {len(cal_sequences)} cal + {len(eval_sequences)} eval")

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

    # ── Cache teacher states + gate patterns ──────────────
    log(f"\n  Caching teacher states + gate patterns"
        f" ({args.n_teacher_cache} sequences)...")
    t0 = time.time()
    teacher_cache = cache_teacher_states(
        model, cal_sequences, args.device,
        max_seqs=args.n_teacher_cache)
    elapsed = time.time() - t0
    log(f"  Cached {len(teacher_cache)} sequences ({elapsed:.0f}s)")

    # ═══════════════════════════════════════════════════════
    # Install sieve with TD + LoRA
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  INSTALLING SIEVE + TD + LoRA")
    log(f"{'═'*70}")

    layers = get_layers(model)

    # L0 SVD + LoRA (no TD on L0)
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, 750)
        mod = FrozenLowRankWithTDLoRA(
            A.to(args.device), B.to(args.device),
            lora_rank=args.lora_rank).to(args.device)
        setattr(mlp0, pname, mod)

    # Sieved layers: TD + LoRA
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)
            mod = TDLoRASieveLinear(
                proj.weight,
                zero_rate=args.zero_rate,
                lora_rank=args.lora_rank).to(args.device)
            setattr(mlp, pname, mod)

    # Collect parameter groups
    td_params = []
    lora_params = []
    total_td = 0
    total_lora = 0

    for li in [0] + SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            mod = getattr(mlp, pname)
            td_params.extend(mod.td_params)
            lora_params.extend(mod.lora_params)
            total_td += sum(p.numel() for p in mod.td_params)
            total_lora += sum(p.numel() for p in mod.lora_params)

    log(f"  TD params:   {total_td:,} (active sign logits, ~50% of full)")
    log(f"  LoRA params: {total_lora:,} (magnitudes)")
    log(f"  Total:       {total_td + total_lora:,}")
    log(f"  TD optimizer: Adam(lr={args.lr_td})")
    log(f"  LoRA optimizer: Adam(lr={args.lr_lora})")
    log(f"  Grad clipping: per-TENSOR for TD, per-group for LoRA")

    # Post-sieve measurement
    sieve_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    sieve_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"  Sieve PPL: {sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)"
        f"  facts: {sieve_facts}/{total_facts}")

    # ═══════════════════════════════════════════════════════
    # Training: split optimizers
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  TRAINING: TD routing + LoRA magnitudes")
    log(f"  {args.steps} steps")
    log(f"  α_route={args.alpha_route}, α_value={args.alpha_value}")
    log(f"{'═'*70}")

    # Two optimizers: different LRs for routing vs magnitudes
    # TD uses Adam — its per-param adaptive LR naturally handles the
    # scale problem that killed v4 (joint clipping) and v4b (SGD blowup).
    # Adam's effective step size ≈ lr regardless of gradient scale,
    # which is exactly what sign logits need.
    opt_td = torch.optim.Adam(
        td_params, lr=args.lr_td) if td_params else None
    opt_lora = torch.optim.Adam(lora_params, lr=args.lr_lora)

    model.train()
    history = []
    eval_history = []
    n_teacher = len(teacher_cache)
    n_cal = len(cal_sequences)
    t0 = time.time()

    for step in range(args.steps):
        if opt_td:
            opt_td.zero_grad()
        opt_lora.zero_grad()

        rng = np.random.RandomState(step)
        batch_indices = rng.choice(n_cal, args.batch_size, replace=False)

        step_ce = 0.0
        step_route = 0.0
        step_value = 0.0
        step_tokens = 0
        step_route_acc = []
        step_value_cos = []

        for idx in batch_indices:
            input_ids = cal_sequences[idx].unsqueeze(0).to(args.device)

            if idx < n_teacher:
                # SM + CE
                teacher_data = teacher_cache[idx]
                ce_loss, route_loss, value_loss, diag = \
                    compute_topology_loss(
                        model, input_ids, teacher_data,
                        SIEVE_LAYERS, args.device)

                loss = (ce_loss
                        + args.alpha_route * route_loss
                        + args.alpha_value * value_loss)

                step_route += route_loss.item()
                step_value += value_loss.item()
                if diag["routing_accuracy"]:
                    step_route_acc.append(
                        np.mean(list(diag["routing_accuracy"].values())))
                if diag["value_cosine"]:
                    step_value_cos.append(
                        np.mean(list(diag["value_cosine"].values())))
            else:
                # CE only
                labels = input_ids.clone()
                out = model(input_ids=input_ids, labels=labels)
                ce_loss = out.loss
                loss = ce_loss

            # Guard ALL loss components — any NaN poisons the backward
            any_nan = (torch.isnan(loss) or torch.isinf(loss)
                       or torch.isnan(ce_loss) or torch.isinf(ce_loss))
            if not any_nan:
                loss.backward()
                step_ce += ce_loss.item() * input_ids.numel()
                step_tokens += input_ids.numel()

        if step_tokens > 0:
            # FIX: Clip per-TENSOR for TD, not per-group.
            # Group-level norm=1.0 across 4.4B params gives per-param
            # gradient ~1.5e-5 — too small for Adam to track.
            # Per-tensor clipping preserves relative gradient structure
            # within each projection matrix.
            if td_params:
                for p in td_params:
                    if p.grad is not None:
                        torch.nn.utils.clip_grad_norm_([p], max_norm=1.0)
                opt_td.step()
                # Clamp delta_logits to prevent runaway values.
                # sign(x) only cares about the sign, not magnitude.
                # Clamping to [-1, 1] keeps logits near the decision
                # boundary and prevents parameter corruption.
                with torch.no_grad():
                    for p in td_params:
                        p.clamp_(-1.0, 1.0)
            torch.nn.utils.clip_grad_norm_(lora_params, max_norm=1.0)
            opt_lora.step()

        avg_ce = step_ce / max(step_tokens, 1)
        n_sm = sum(1 for i in batch_indices if i < n_teacher)
        avg_route = step_route / max(n_sm, 1)
        avg_value = step_value / max(n_sm, 1)
        mean_racc = float(np.mean(step_route_acc)) if step_route_acc else 0
        mean_vcos = float(np.mean(step_value_cos)) if step_value_cos else 0

        history.append({
            "step": step + 1,
            "ce": round(avg_ce, 4),
            "route": round(avg_route, 4),
            "value": round(avg_value, 4),
            "route_acc": round(mean_racc, 4),
            "value_cos": round(mean_vcos, 4),
        })

        if (step + 1) % 10 == 0 or step == 0:
            # Count total flips
            total_flips = 0
            total_weights = 0
            for li in SIEVE_LAYERS:
                mlp = layers[li].mlp
                for pname in ["gate_proj", "up_proj", "down_proj"]:
                    mod = getattr(mlp, pname)
                    if isinstance(mod, TDLoRASieveLinear):
                        total_flips += mod.n_flips
                        total_weights += (mod.out_features
                                          * mod.in_features)
            flip_pct = total_flips / max(total_weights, 1) * 100

            elapsed = time.time() - t0
            log(f"    step {step+1:>3d}: CE={avg_ce:.4f}"
                f" route={avg_route:.4f}(acc={mean_racc:.3f})"
                f" value={avg_value:.4f}(cos={mean_vcos:.3f})"
                f" flips={flip_pct:.2f}% ({elapsed:.0f}s)")

        # Periodic eval
        if (step + 1) % args.eval_every == 0:
            eval_ppl = measure_ppl_tokens(
                model, eval_sequences, args.device)
            eval_facts, _ = measure_facts(model, tokenizer, args.device)
            log(f"    ▶ EVAL step {step+1}: PPL={eval_ppl:.2f}"
                f" ({eval_ppl/base_ppl:.3f}x)"
                f" facts={eval_facts}/{total_facts}")
            eval_history.append({
                "step": step + 1,
                "ppl": eval_ppl,
                "ppl_ratio": round(eval_ppl / base_ppl, 4),
                "facts": eval_facts,
            })
            model.train()

    model.eval()

    # Final eval
    final_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    final_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"\n  Final PPL: {final_ppl:.2f} ({final_ppl/base_ppl:.3f}x)"
        f"  facts: {final_facts}/{total_facts}")

    # Final flip statistics
    log(f"\n  Final TD flip statistics:")
    total_flips = 0
    total_weights = 0
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        layer_flips = 0
        layer_weights = 0
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            mod = getattr(mlp, pname)
            if isinstance(mod, TDLoRASieveLinear):
                layer_flips += mod.n_flips
                layer_weights += mod.out_features * mod.in_features
        total_flips += layer_flips
        total_weights += layer_weights
        if (li + 1) % 5 == 0 or li == SIEVE_LAYERS[0]:
            pct = layer_flips / max(layer_weights, 1) * 100
            log(f"    L{li:>2d}: {layer_flips:>6,} flips"
                f" ({pct:.2f}%)")

    flip_pct = total_flips / max(total_weights, 1) * 100
    log(f"    Total: {total_flips:,} / {total_weights:,}"
        f" ({flip_pct:.2f}%)")

    # ═══════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  RESULTS")
    log(f"{'='*70}")
    log(f"  Baseline:   PPL={base_ppl:.2f}  facts={base_facts}/{total_facts}")
    log(f"  Sieve only: PPL={sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)")
    log(f"  Final:      PPL={final_ppl:.2f} ({final_ppl/base_ppl:.3f}x)"
        f"  facts={final_facts}/{total_facts}")
    log(f"  TD params:   {total_td:,}")
    log(f"  LoRA params: {total_lora:,}")
    log(f"  Sign flips:  {total_flips:,} ({flip_pct:.2f}%)")
    log(f"  Improvement: {sieve_ppl:.2f} → {final_ppl:.2f}"
        f" ({(1 - final_ppl/sieve_ppl)*100:.1f}% reduction)")

    log(f"\n  vs v3b (LoRA+SM, 5.9M params):")
    log(f"    v3b:  25.67 → 16.27 (36.6% reduction, 1.44x base)")
    log(f"    v4:   {sieve_ppl:.2f} → {final_ppl:.2f}"
        f" ({(1 - final_ppl/sieve_ppl)*100:.1f}% reduction,"
        f" {final_ppl/base_ppl:.2f}x base)")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "topology-score-matching"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    result = {
        "model": args.model,
        "version": "v4c-topology-sm-nan-fixed",
        "config": {
            "lora_rank": args.lora_rank,
            "steps": args.steps,
            "lr_td": args.lr_td,
            "lr_lora": args.lr_lora,
            "alpha_route": args.alpha_route,
            "alpha_value": args.alpha_value,
            "n_cal": len(cal_sequences),
            "n_eval": len(eval_sequences),
            "n_teacher_cache": len(teacher_cache),
            "sieve_layers": SIEVE_LAYERS,
        },
        "baseline_ppl": base_ppl,
        "baseline_facts": base_facts,
        "sieve_ppl": sieve_ppl,
        "final_ppl": final_ppl,
        "final_ratio": round(final_ppl / base_ppl, 4),
        "final_facts": final_facts,
        "td_params": total_td,
        "lora_params": total_lora,
        "total_flips": total_flips,
        "flip_rate": round(flip_pct, 4),
        "eval_history": eval_history,
        "loss_history": history,
    }

    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Results saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
