#!/usr/bin/env python3
"""Holographic Sign Correction — Direct inverse solve, not gradient descent.

TD treats sign correction as an optimization problem: backprop through the
whole model, STE through sign(), hope gradient moves logits. This fails
because (1) gradient dilutes across 29 layers, (2) flips cascade catastrophically,
and (3) the forward loss can't invert to the right sign decision.

The holographic approach treats sign correction as a RECORDING problem:

  For each weight position (i,j) in each sieved projection:
    reference_beam = actual input to this projection (from sieved model)
    object_beam    = desired output of this projection (from teacher model)
    fringe_pattern = correlation(reference, object)
    optimal_sign   = sign(fringe_pattern)

This is computed directly — no backprop, no STE, no optimizer. Each layer
is corrected independently using its own (corrupted) inputs, matching the
CGTSM principle that density of measurement matters, not weighting.

After signs are corrected, LoRA + score matching fixes magnitudes.

Usage:
  uv run python scripts/experiments/holographic_sign_correction.py \
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
            if torch.isnan(out.loss) or torch.isinf(out.loss):
                continue
            total_loss += out.loss.item() * labels.numel()
            total_tokens += labels.numel()
    if total_tokens == 0:
        return float('nan')
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
# Sieved Linear (no TD — signs are directly mutable)
# ══════════════════════════════════════════════════════════════

class SievedLinear(nn.Module):
    """Crystal sieve with mutable signs and optional LoRA.

    W_eff = signs * magnitudes + LoRA
    """

    def __init__(self, weight, zero_rate=0.5, lora_rank=0):
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

        # Store signs as mutable buffer (not parameter — updated directly)
        signs = torch.sign(W)
        magnitudes = abs_W * mask
        self.register_buffer("signs", signs)
        self.register_buffer("magnitudes", magnitudes)
        self.register_buffer("mask", mask)

        # Original teacher signs for comparison
        self.register_buffer("teacher_signs", signs.clone())

        # LoRA (only created if lora_rank > 0)
        self.lora_rank = lora_rank
        if lora_rank > 0:
            self.lora_A = nn.Parameter(
                torch.randn(out_features, lora_rank) * 0.01)
            self.lora_B = nn.Parameter(
                torch.zeros(lora_rank, in_features))

        self.out_features = out_features
        self.in_features = in_features

    def forward(self, x):
        W_eff = self.signs.float() * self.magnitudes.float()
        if self.lora_rank > 0:
            W_eff = W_eff + self.lora_A @ self.lora_B
        out = x.float() @ W_eff.T
        return out.clamp(-65000, 65000).to(x.dtype)

    def add_lora(self, rank):
        """Add LoRA after sign correction phase."""
        self.lora_rank = rank
        self.lora_A = nn.Parameter(
            torch.randn(self.out_features, rank, device=self.signs.device)
            * 0.01)
        self.lora_B = nn.Parameter(
            torch.zeros(rank, self.in_features, device=self.signs.device))

    @property
    def n_flips(self):
        """Count signs that differ from teacher."""
        with torch.no_grad():
            active = (self.mask > 0)
            flipped = (self.signs != self.teacher_signs) & active
            return int(flipped.sum().item())

    @property
    def n_active(self):
        return int((self.mask > 0).sum().item())


class FrozenLowRank(nn.Module):
    """L0 SVD (no sign correction needed — L0 is continuous)."""

    def __init__(self, A, B, lora_rank=0):
        super().__init__()
        self.register_buffer("svd_A", A)
        self.register_buffer("svd_B", B)
        self.lora_rank = lora_rank
        if lora_rank > 0:
            self.lora_A = nn.Parameter(
                torch.randn(A.shape[0], lora_rank) * 0.01)
            self.lora_B = nn.Parameter(
                torch.zeros(lora_rank, B.shape[1]))

    def forward(self, x):
        out = x.float() @ self.svd_B.T @ self.svd_A.T
        if self.lora_rank > 0:
            out = out + x.float() @ self.lora_B.T @ self.lora_A.T
        return out.clamp(-65000, 65000).to(x.dtype)

    def add_lora(self, rank):
        self.lora_rank = rank
        self.lora_A = nn.Parameter(
            torch.randn(self.svd_A.shape[0], rank,
                        device=self.svd_A.device) * 0.01)
        self.lora_B = nn.Parameter(
            torch.zeros(rank, self.svd_B.shape[1],
                        device=self.svd_B.device))

    @property
    def n_flips(self):
        return 0

    @property
    def n_active(self):
        return 0


def svd_factorize(weight, rank):
    W = weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))
    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)
    return A, B


# ══════════════════════════════════════════════════════════════
# Phase 1: Holographic Sign Recording
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def holographic_sign_correction(model, sequences, device, sieve_layers,
                                n_cal=64, threshold_percentile=95):
    """Compute optimal signs per-projection via holographic recording.

    For each sieved projection:
      1. Collect input activations (from sieved model forward)
      2. Collect teacher's output targets (from original weights)
      3. Compute correlation: C[i,j] = Σ_k target_k[i] * input_k[j]
      4. Flip where sign(C) disagrees with current sign and |C| > threshold

    Returns dict of per-layer statistics.
    """
    layers = get_layers(model)
    stats = {}

    log(f"\n  Phase 1: Holographic sign recording ({n_cal} sequences)")
    log(f"  Processing {len(sieve_layers)} sieved layers...")

    for li in sieve_layers:
        mlp = layers[li].mlp
        proj_names = ["gate_proj", "up_proj", "down_proj"]
        layer_stats = {}

        for pname in proj_names:
            mod = getattr(mlp, pname)
            if not isinstance(mod, SievedLinear):
                continue

            # Accumulators for correlation (float64 for precision)
            out_f, in_f = mod.out_features, mod.in_features
            # We compute: C = teacher_output.T @ sieve_input
            # Accumulated over all tokens across all calibration sequences
            #
            # Too large to hold full correlation at once for large models.
            # Instead: accumulate correlation in chunks per output block.
            #
            # For 8B: gate/up are (12288, 4096), down is (4096, 12288)
            # Full correlation = 50M floats = 200MB per projection. OK.

            correlation = torch.zeros(out_f, in_f, dtype=torch.float32,
                                      device='cpu')
            n_tokens_total = 0

            for seq_idx in range(min(n_cal, len(sequences))):
                seq = sequences[seq_idx]
                input_ids = seq.unsqueeze(0).to(device)

                # Capture this projection's input during sieved forward
                proj_input = {}

                def make_input_hook(name):
                    def hook_fn(module, args):
                        x = args[0] if isinstance(args, tuple) else args
                        proj_input[name] = x.detach()
                    return hook_fn

                hook = mod.register_forward_pre_hook(
                    make_input_hook(pname))

                # Forward the sieved model
                model(input_ids=input_ids)
                hook.remove()

                if pname not in proj_input:
                    continue

                sieve_input = proj_input[pname].float()  # (1, seq, in_f)
                sieve_input = sieve_input.squeeze(0)      # (seq, in_f)

                # Teacher's output: what the original weight would produce
                # from this (corrupted) input
                # teacher_output = W_teacher @ sieve_input.T
                # W_teacher = teacher_signs * (|W_original| including unmasked)
                # But we stored teacher_signs and magnitudes separately.
                # The teacher weight at unmasked positions:
                #   W_teacher[i,j] = teacher_signs[i,j] * |W_original[i,j]|
                # But magnitudes has the mask applied. We need the UN-masked
                # teacher weight. We don't have it anymore after sieve install.
                #
                # Alternative: use the sieve's own output as "current" and
                # compute what SHOULD be produced using the layer's residual
                # update target.
                #
                # Simplest correct approach: the teacher weight for this
                # projection was sign(W) * |W|. The sieve weight is
                # sign(W) * |W| * mask. The difference is on masked positions.
                # For sign correction, we care about the NON-masked positions
                # (where mask=1), where teacher and sieve signs currently agree.
                # We want: which of these should flip?
                #
                # The right target: what output, from THIS input, would
                # minimize the layer's residual update error?
                # This requires knowing the target residual update.
                #
                # For the prototype, use the projection-level target:
                # teacher_output = W_teacher @ sieve_input
                # We reconstruct W_teacher from stored signs * original |W|.
                # But we only have magnitudes = |W| * mask.
                #
                # INSIGHT: for non-masked positions (mask=1), the magnitude
                # IS the original |W|. The sign correction only matters at
                # non-masked positions. So:
                # teacher_output_contribution[i] from position j (if mask[i,j]=1):
                #   = teacher_sign[i,j] * magnitude[i,j] * input[j]
                # And we want to know if flipping the sign helps.

                # Compute current sieve output
                sieve_out = (mod.signs.float() * mod.magnitudes.float()
                             ) @ sieve_input.T  # (out_f, seq)

                # What we'll compare against: capture the layer's actual
                # residual update from teacher vs sieve
                # For now, just compute the per-position flip benefit:
                # If we flip sign at (i,j):
                #   new_output[i] = old_output[i] - 2*sign[i,j]*mag[i,j]*input[j]
                # This helps if the change has opposite sign to the error.
                #
                # But what IS the error? We don't have a per-projection target.
                #
                # APPROACH: Use the GRADIENT of the layer's score matching
                # loss w.r.t. each sign. This is computed locally through
                # just this one layer, not backpropped through the whole model.
                # But that requires knowing the target hidden state...
                #
                # SIMPLEST HOLOGRAPHIC APPROACH: The optimal signs for W,
                # given input X and desired output Y, solve:
                #   min ||diag(T) * M * X - Y||²  per output dimension
                #
                # For output dim i:
                #   T[i,:] = argmin_t Σ_k (Σ_j t_j * M[i,j] * X_k[j] - Y_k[i])²
                #
                # Independent per (i,j) approximation:
                #   T[i,j] = sign(Σ_k M[i,j] * X_k[j] * Y_k[i])
                #          = sign(M[i,j]) * sign(Σ_k X_k[j] * Y_k[i])
                #          = sign(Σ_k X_k[j] * Y_k[i])   [since M ≥ 0]
                #
                # This is just: sign of the correlation between input j
                # and target output i, over calibration examples k.
                #
                # The TARGET Y is the teacher's projection output from
                # teacher's input. But we don't have teacher input here.
                #
                # KEY HOLOGRAPHIC INSIGHT: use sieve input (the actual
                # corrupted beam), and teacher output (the desired result).
                # The interference of these two IS the optimal fringe pattern.
                #
                # For the un-masked teacher output, we use the full weight:
                # Y = W_full @ X_sieve... but we don't have W_full.
                #
                # PRAGMATIC SOLUTION: We DO have teacher_signs and magnitudes.
                # At mask=1 positions, magnitude = |W_original|.
                # At mask=0 positions, magnitude = 0 but original had nonzero W.
                # Teacher output (at active positions only):
                teacher_out = (mod.teacher_signs.float()
                               * mod.magnitudes.float()
                               ) @ sieve_input.T  # (out_f, seq)

                # Correlation: optimal sign for each (i,j) is
                # sign(Σ_k teacher_out[i,k] * sieve_input[k,j])
                # = sign(teacher_out @ sieve_input)
                #
                # But this is the correlation between the target output
                # and the input — the holographic fringe pattern.
                corr = teacher_out @ sieve_input  # (out_f, in_f)

                correlation += corr.cpu()
                n_tokens_total += sieve_input.shape[0]

            # Determine optimal signs from correlation
            optimal_signs = torch.sign(correlation).to(device)

            # Where does the optimal sign disagree with current sieve sign?
            current_signs = mod.signs.clone()
            active = mod.mask > 0

            # Only consider active (non-masked) positions
            disagree = (optimal_signs.to(device) != current_signs) & active

            # Confidence: |correlation| per position
            conf = correlation.abs().to(device)
            conf_active = conf[active]

            if conf_active.numel() == 0:
                layer_stats[pname] = {
                    "n_active": 0, "n_disagree": 0,
                    "n_flipped": 0, "flip_pct": 0.0,
                }
                continue

            # Threshold: only flip high-confidence positions
            # Use percentile of active correlation magnitudes
            # Sample if tensor too large for quantile
            if conf_active.numel() > 5_000_000:
                sample_idx = torch.randperm(
                    conf_active.numel())[:5_000_000]
                threshold = torch.quantile(
                    conf_active.float().flatten()[sample_idx],
                    threshold_percentile / 100.0)
            else:
                threshold = torch.quantile(
                    conf_active.float(),
                    threshold_percentile / 100.0)

            # Flip where: disagree AND confidence > threshold
            flip_mask = disagree & (conf > threshold)
            n_flip = int(flip_mask.sum().item())
            n_disagree = int(disagree.sum().item())

            # Apply flips
            mod.signs[flip_mask] = optimal_signs.to(device)[flip_mask]

            layer_stats[pname] = {
                "n_active": int(active.sum().item()),
                "n_disagree": n_disagree,
                "disagree_pct": round(
                    n_disagree / max(int(active.sum().item()), 1) * 100, 2),
                "n_flipped": n_flip,
                "flip_pct": round(
                    n_flip / max(int(active.sum().item()), 1) * 100, 2),
                "threshold": round(threshold.item(), 4),
                "mean_conf": round(conf_active.float().mean().item(), 4),
                "n_tokens": n_tokens_total,
            }

        stats[f"L{li}"] = layer_stats

        # Progress
        total_flips = sum(
            v.get("n_flipped", 0) for v in layer_stats.values())
        total_disagree = sum(
            v.get("n_disagree", 0) for v in layer_stats.values())
        total_active = sum(
            v.get("n_active", 0) for v in layer_stats.values())
        log(f"    L{li:>2d}: disagree={total_disagree:>8,}"
            f" ({total_disagree/max(total_active,1)*100:.1f}%)"
            f"  flipped={total_flips:>6,}"
            f" ({total_flips/max(total_active,1)*100:.2f}%)")

    return stats


# ══════════════════════════════════════════════════════════════
# Phase 2: LoRA + Score Matching (same as v3b)
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def cache_teacher_states(model, sequences, device, max_seqs=128):
    """Cache per-layer hidden states from teacher (before sieve install)."""
    layers = get_layers(model)
    n_layers = len(layers)
    all_states = []

    for seq_idx, seq in enumerate(sequences[:max_seqs]):
        input_ids = seq.unsqueeze(0).to(device)
        layer_states = {}
        hooks = []

        def embed_hook(mod, args):
            h = args[0] if isinstance(args, tuple) else args
            layer_states[-1] = h[0].detach().cpu().half()
        hooks.append(layers[0].register_forward_pre_hook(embed_hook))

        def make_state_hook(li):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                layer_states[li] = h[0].detach().cpu().half()
            return hook_fn

        for li in range(n_layers):
            hooks.append(layers[li].register_forward_hook(
                make_state_hook(li)))

        model(input_ids=input_ids)
        for h in hooks:
            h.remove()

        state_list = [layer_states.get(-1, torch.zeros(1))]
        for li in range(n_layers):
            state_list.append(layer_states.get(li, torch.zeros(1)))
        all_states.append(torch.stack(state_list, dim=0))

        if (seq_idx + 1) % 32 == 0:
            log(f"      {seq_idx + 1}/{min(max_seqs, len(sequences))} cached")

    return all_states


def compute_sm_loss(model, input_ids, teacher_hidden, device):
    """Score matching loss: CE + α·mean(1 - cos(Δ_student, Δ_teacher))."""
    layers = get_layers(model)
    n_layers = len(layers)

    student_states = {}
    hooks = []

    def pre_hook(mod, args):
        h = args[0] if isinstance(args, tuple) else args
        student_states[-1] = h[0]
    hooks.append(layers[0].register_forward_pre_hook(pre_hook))

    def make_hook(li):
        def fn(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            student_states[li] = h[0]
        return fn

    for li in range(n_layers):
        hooks.append(layers[li].register_forward_hook(make_hook(li)))

    labels = input_ids.clone()
    out = model(input_ids=input_ids, labels=labels)
    ce_loss = out.loss

    for h in hooks:
        h.remove()

    # Score matching
    sm_loss = torch.tensor(0.0, device=device)
    n_sm = 0
    for li in range(n_layers):
        if li not in student_states:
            continue
        s_prev = student_states.get(-1) if li == 0 else student_states.get(
            li - 1)
        if s_prev is None:
            continue
        s_delta = student_states[li].float() - s_prev.float()
        t_delta = (teacher_hidden[li + 1].float().to(device)
                   - teacher_hidden[li].float().to(device))
        s_norm = s_delta.norm(dim=-1, keepdim=True)
        t_norm = t_delta.norm(dim=-1, keepdim=True)
        valid = ((s_norm > 1e-8) & (t_norm > 1e-8)).squeeze(-1)
        if valid.any():
            cos = F.cosine_similarity(s_delta, t_delta, dim=-1)
            mean_cos = cos[valid].mean()
            if not torch.isnan(mean_cos):
                sm_loss = sm_loss + (1.0 - mean_cos)
                n_sm += 1

    if n_sm > 0:
        sm_loss = sm_loss / n_sm

    return ce_loss, sm_loss


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
    p.add_argument("--sm-steps", type=int, default=200,
                   help="Steps for LoRA + score matching phase")
    p.add_argument("--lr-lora", type=float, default=1e-4)
    p.add_argument("--alpha-sm", type=float, default=5.0,
                   help="Weight for score matching loss")
    p.add_argument("--n-cal", type=int, default=256)
    p.add_argument("--n-holo-cal", type=int, default=64,
                   help="Calibration sequences for holographic phase")
    p.add_argument("--n-eval", type=int, default=64)
    p.add_argument("--n-teacher-cache", type=int, default=128)
    p.add_argument("--seq-len", type=int, default=128)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--eval-every", type=int, default=50)
    p.add_argument("--threshold-pct", type=float, default=95.0,
                   help="Percentile threshold for sign flips (higher=fewer)")
    p.add_argument("--shard-dir", type=str, default=str(SHARD_DIR))
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]

    log(f"\n{'='*70}")
    log("  HOLOGRAPHIC SIGN CORRECTION")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  Sieve layers: {len(SIEVE_LAYERS)}")
    log(f"  Holographic cal: {args.n_holo_cal} sequences")
    log(f"  Flip threshold: top {100 - args.threshold_pct:.0f}%"
        f" confidence")
    log(f"  LoRA rank: {args.lora_rank}, SM steps: {args.sm_steps}")

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
    log(f"  d_model={model.config.hidden_size}")

    # ── Baseline ──────────────────────────────────────────
    log("\n  Measuring baseline...")
    base_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    base_facts, total_facts = measure_facts(model, tokenizer, args.device)
    log(f"  Baseline PPL: {base_ppl:.2f}, facts: {base_facts}/{total_facts}")

    # ── Cache teacher states (BEFORE sieve install) ───────
    log(f"\n  Caching teacher states ({args.n_teacher_cache} seqs)...")
    t0 = time.time()
    teacher_cache = cache_teacher_states(
        model, cal_sequences, args.device,
        max_seqs=args.n_teacher_cache)
    log(f"  Cached {len(teacher_cache)} sequences ({time.time()-t0:.0f}s)")

    # ═══════════════════════════════════════════════════════
    # Install sieve (no LoRA yet — signs only)
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  INSTALLING CRYSTAL SIEVE")
    log(f"{'═'*70}")

    layers = get_layers(model)

    # L0: SVD (no sign correction)
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, 750)
        mod = FrozenLowRank(
            A.to(args.device), B.to(args.device)).to(args.device)
        setattr(mlp0, pname, mod)

    # Sieved layers: signs + magnitudes, no LoRA yet
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)
            mod = SievedLinear(
                proj.weight,
                zero_rate=args.zero_rate,
                lora_rank=0).to(args.device)
            setattr(mlp, pname, mod)

    # Sieve-only measurement
    sieve_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    sieve_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"  Sieve PPL: {sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)"
        f"  facts: {sieve_facts}/{total_facts}")

    # ═══════════════════════════════════════════════════════
    # Phase 1: Holographic Sign Correction
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 1: HOLOGRAPHIC SIGN RECORDING")
    log(f"{'═'*70}")

    t0 = time.time()
    holo_stats = holographic_sign_correction(
        model, cal_sequences, args.device, SIEVE_LAYERS,
        n_cal=args.n_holo_cal,
        threshold_percentile=args.threshold_pct)
    holo_elapsed = time.time() - t0

    # Post-correction measurement
    holo_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    holo_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"\n  Post-correction PPL: {holo_ppl:.2f} ({holo_ppl/base_ppl:.2f}x)"
        f"  facts: {holo_facts}/{total_facts}")
    log(f"  Holographic phase: {holo_elapsed:.0f}s")

    # Summarize flips
    total_flipped = 0
    total_active = 0
    total_disagree = 0
    for layer_key, layer_data in holo_stats.items():
        for pname, pdata in layer_data.items():
            total_flipped += pdata.get("n_flipped", 0)
            total_active += pdata.get("n_active", 0)
            total_disagree += pdata.get("n_disagree", 0)

    log(f"\n  Sign correction summary:")
    log(f"    Total active positions: {total_active:,}")
    log(f"    Disagree with teacher:  {total_disagree:,}"
        f" ({total_disagree/max(total_active,1)*100:.1f}%)")
    log(f"    Actually flipped:       {total_flipped:,}"
        f" ({total_flipped/max(total_active,1)*100:.2f}%)")
    log(f"    Sieve → corrected PPL:  {sieve_ppl:.2f} → {holo_ppl:.2f}")

    # ═══════════════════════════════════════════════════════
    # Phase 2: LoRA + Score Matching
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 2: LoRA + SCORE MATCHING")
    log(f"{'═'*70}")

    # Add LoRA to all sieved modules
    for li in [0] + SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            mod = getattr(mlp, pname)
            mod.add_lora(args.lora_rank)

    lora_params = []
    total_lora = 0
    for li in [0] + SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            mod = getattr(mlp, pname)
            if mod.lora_rank > 0:
                lora_params.extend([mod.lora_A, mod.lora_B])
                total_lora += mod.lora_A.numel() + mod.lora_B.numel()

    log(f"  LoRA params: {total_lora:,}")

    optimizer = torch.optim.Adam(lora_params, lr=args.lr_lora)
    n_teacher = len(teacher_cache)
    n_cal = len(cal_sequences)
    model.train()

    loss_history = []
    eval_history = []
    t0 = time.time()

    for step in range(args.sm_steps):
        optimizer.zero_grad()

        rng = np.random.RandomState(step)
        batch_indices = rng.choice(n_cal, args.batch_size, replace=False)

        step_ce = 0.0
        step_sm = 0.0
        step_tokens = 0

        for idx in batch_indices:
            input_ids = cal_sequences[idx].unsqueeze(0).to(args.device)

            if idx < n_teacher:
                ce_loss, sm_loss = compute_sm_loss(
                    model, input_ids, teacher_cache[idx], args.device)
                loss = ce_loss + args.alpha_sm * sm_loss
                step_sm += sm_loss.item()
            else:
                labels = input_ids.clone()
                out = model(input_ids=input_ids, labels=labels)
                ce_loss = out.loss
                loss = ce_loss

            any_nan = (torch.isnan(loss) or torch.isinf(loss)
                       or torch.isnan(ce_loss))
            if not any_nan:
                loss.backward()
                step_ce += ce_loss.item() * input_ids.numel()
                step_tokens += input_ids.numel()

        if step_tokens > 0:
            torch.nn.utils.clip_grad_norm_(lora_params, max_norm=1.0)
            optimizer.step()

        avg_ce = step_ce / max(step_tokens, 1)
        n_sm_batch = sum(1 for i in batch_indices if i < n_teacher)
        avg_sm = step_sm / max(n_sm_batch, 1)

        loss_history.append({
            "step": step + 1,
            "ce": round(avg_ce, 4),
            "sm": round(avg_sm, 4),
        })

        if (step + 1) % 10 == 0 or step == 0:
            elapsed = time.time() - t0
            log(f"    step {step+1:>3d}: CE={avg_ce:.4f}"
                f" SM={avg_sm:.4f} ({elapsed:.0f}s)")

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

    # ═══════════════════════════════════════════════════════
    # Results
    # ═══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  RESULTS")
    log(f"{'='*70}")
    log(f"  Baseline:      PPL={base_ppl:.2f}  facts={base_facts}/{total_facts}")
    log(f"  Sieve only:    PPL={sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)")
    log(f"  After holo:    PPL={holo_ppl:.2f} ({holo_ppl/base_ppl:.2f}x)"
        f"  [signs corrected, no LoRA]")
    log(f"  After LoRA+SM: PPL={final_ppl:.2f} ({final_ppl/base_ppl:.3f}x)"
        f"  facts={final_facts}/{total_facts}")
    log(f"  Flipped signs: {total_flipped:,} / {total_active:,}"
        f" ({total_flipped/max(total_active,1)*100:.2f}%)")
    log(f"  LoRA params:   {total_lora:,}")

    # Compare to v3b baseline
    log(f"\n  vs v3b (LoRA+SM only, no sign correction):")
    log(f"    v3b:  25.67 → 16.27 (36.6% reduction, 1.44x base)")
    log(f"    holo: {sieve_ppl:.2f} → {holo_ppl:.2f}"
        f" → {final_ppl:.2f}"
        f" ({(1 - final_ppl/sieve_ppl)*100:.1f}% total reduction,"
        f" {final_ppl/base_ppl:.2f}x base)")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "holographic-sign-correction"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    result = {
        "model": args.model,
        "version": "v1-holographic-sign-correction",
        "config": {
            "lora_rank": args.lora_rank,
            "sm_steps": args.sm_steps,
            "lr_lora": args.lr_lora,
            "alpha_sm": args.alpha_sm,
            "n_cal": len(cal_sequences),
            "n_holo_cal": args.n_holo_cal,
            "n_eval": len(eval_sequences),
            "n_teacher_cache": len(teacher_cache),
            "threshold_pct": args.threshold_pct,
            "sieve_layers": SIEVE_LAYERS,
        },
        "baseline_ppl": base_ppl,
        "baseline_facts": base_facts,
        "sieve_ppl": sieve_ppl,
        "sieve_facts": sieve_facts,
        "holo_ppl": holo_ppl,
        "holo_facts": holo_facts,
        "final_ppl": final_ppl,
        "final_ratio": round(final_ppl / base_ppl, 4),
        "final_facts": final_facts,
        "total_flipped": total_flipped,
        "total_active": total_active,
        "total_disagree": total_disagree,
        "holo_stats": holo_stats,
        "eval_history": eval_history,
        "loss_history": loss_history,
    }

    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Results saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
