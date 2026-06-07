#!/usr/bin/env python3
"""Crystal ECC Sign Correction — Error-correcting codes from dimensional projections.

The crystal's eigenvalue hierarchy IS an error-correcting code:

  8D crystal (full KIBC+DWYS+WHNF)
    ↓ project to 6D → parity check
      ↓ project to 5D → parity check
        ↓ project to 4D → parity check (KIBC basis)
          ↓ project to 3D → parity check (minimal)

Each projection level constrains the sign pattern. A sign flip
that violates constraints at ANY level is an error.

This script:
1. Saves original weights before sieving (proper holographic target)
2. Installs sieve
3. Computes per-position error signal using original weights on sieve inputs
4. Computes crystal health metric from sign pattern eigenstructure
5. Filters flip candidates through crystal coherence check
6. Applies only crystal-coherent flips
7. Runs LoRA + score matching on corrected sieve
8. Evaluates

The crystal check is computed WITHOUT probes — purely from the
sign pattern's correlation structure:
  C = sign(W) @ sign(W).T / n_cols
  eigenvalues(C) should follow φ^(p/q) ratios

Usage:
  uv run python scripts/experiments/crystal_ecc_sign_correction.py \
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
PHI = (1 + 5 ** 0.5) / 2  # golden ratio


# ══════════════════════════════════════════════════════════════
# Data + Helpers (same as other experiments)
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
# Crystal Health Metric
# ══════════════════════════════════════════════════════════════

def crystal_eigenvalue_health(signs: torch.Tensor, n_sample=10000):
    """Compute crystal health from sign pattern eigenstructure.

    The sign pattern's row-wise correlation matrix has eigenvalues
    that should follow the crystal equation: λ_k = C · φ^(-s·β_k).

    Returns dict with eigenvalue ratios and health score.
    """
    out_f, in_f = signs.shape

    # Sample columns for tractability (full matrix is out_f × out_f)
    if in_f > n_sample:
        idx = torch.randperm(in_f)[:n_sample]
        S = signs[:, idx].float()
    else:
        S = signs.float()

    # Row-wise correlation: C = S @ S.T / n_cols
    # This captures how sign patterns correlate across output dimensions
    C = S @ S.T / S.shape[1]

    # Eigendecompose (symmetric, use eigh for stability)
    eigvals = torch.linalg.eigvalsh(C.cpu())
    eigvals = eigvals.flip(0)  # descending

    # Take top-8 eigenvalues (crystal dimension)
    top = eigvals[:8].numpy()

    # Crystal equation predicts ratios: λ_k/λ_0 = φ^(-s·β_k)
    # For KIBC (n=4): s=4/5, β = [0, 1, 1+φ, 2+φ]
    s = 4 / 5
    beta = [0, 1, 1 + PHI, 2 + PHI]
    predicted_ratios = [PHI ** (-s * b) for b in beta]

    # Observed ratios
    if top[0] > 0:
        observed_ratios = (top[:4] / top[0]).tolist()
    else:
        observed_ratios = [0, 0, 0, 0]

    # Health = correlation between predicted and observed ratios
    if len(observed_ratios) >= 4:
        pred = np.array(predicted_ratios)
        obs = np.array(observed_ratios[:4])
        if np.std(obs) > 1e-10:
            health = float(np.corrcoef(pred, obs)[0, 1])
        else:
            health = 0.0
    else:
        health = 0.0

    return {
        "eigenvalues": top.tolist(),
        "observed_ratios": observed_ratios,
        "predicted_ratios": predicted_ratios,
        "health": health,
    }


def crystal_health_per_dim(signs: torch.Tensor, n_sample=10000):
    """Crystal health at each dimensional projection level.

    Project to top-k eigenvectors for k = 3, 4, 5, 6, 7, 8.
    At each level, check eigenvalue ratios against crystal equation.

    Returns list of health scores per dimension.
    """
    out_f, in_f = signs.shape

    if in_f > n_sample:
        idx = torch.randperm(in_f)[:n_sample]
        S = signs[:, idx].float()
    else:
        S = signs.float()

    C = S @ S.T / S.shape[1]
    eigvals, eigvecs = torch.linalg.eigh(C.cpu())
    eigvals = eigvals.flip(0)
    eigvecs = eigvecs.flip(1)

    s = 4 / 5
    beta = [0, 1, 1 + PHI, 2 + PHI]
    pred_4 = np.array([PHI ** (-s * b) for b in beta])

    results = []
    for k in [3, 4, 5, 6, 7, 8]:
        top_k = eigvals[:k].numpy()
        if top_k[0] > 0 and k >= 4:
            obs = top_k[:4] / top_k[0]
            if np.std(obs) > 1e-10:
                health = float(np.corrcoef(pred_4, obs)[0, 1])
            else:
                health = 0.0
        elif k >= 3 and top_k[0] > 0:
            # For k=3, check first 3 ratios
            obs = top_k[:3] / top_k[0]
            pred_3 = pred_4[:3]
            if np.std(obs) > 1e-10:
                health = float(np.corrcoef(pred_3, obs)[0, 1])
            else:
                health = 0.0
        else:
            health = 0.0
        results.append({"dim": k, "health": round(health, 4),
                        "eigenvalues": top_k.tolist()})
    return results


# ══════════════════════════════════════════════════════════════
# Sieved Linear (with original weight reference for holographic target)
# ══════════════════════════════════════════════════════════════

class SievedLinear(nn.Module):
    """Crystal sieve with mutable signs, original weight reference, and LoRA."""

    def __init__(self, weight, zero_rate=0.5, lora_rank=0):
        super().__init__()
        W = weight.detach().float().cpu()
        out_features, in_features = W.shape
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

        signs = torch.sign(W)
        magnitudes = abs_W * mask
        self.register_buffer("signs", signs)
        self.register_buffer("magnitudes", magnitudes)
        self.register_buffer("mask", mask)
        self.register_buffer("teacher_signs", signs.clone())

        # KEY FIX: Keep FULL original weight (including masked positions)
        # as the holographic target. The sieve zeros out masked positions,
        # but the teacher uses them. Sign flips at active positions can
        # partially compensate for the lost masked contributions.
        # This is the "object beam" — what the projection SHOULD produce.
        self.register_buffer("original_weight", W)

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
        self.lora_rank = rank
        self.lora_A = nn.Parameter(
            torch.randn(self.out_features, rank,
                        device=self.signs.device) * 0.01)
        self.lora_B = nn.Parameter(
            torch.zeros(rank, self.in_features,
                        device=self.signs.device))

    @property
    def n_flips(self):
        with torch.no_grad():
            active = (self.mask > 0)
            return int(((self.signs != self.teacher_signs) & active)
                       .sum().item())

    @property
    def n_active(self):
        return int((self.mask > 0).sum().item())


class FrozenLowRank(nn.Module):
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


def svd_factorize(weight, rank):
    W = weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))
    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)
    return A, B


# ══════════════════════════════════════════════════════════════
# Phase 1: Crystal-Constrained Holographic Sign Correction
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def crystal_ecc_sign_correction(model, sequences, device, sieve_layers,
                                n_cal=64, max_flip_pct=5.0):
    """Sign correction with crystal ECC constraint.

    For each sieved projection:
    1. Compute proper error: original_weight @ sieve_input vs sieve output
    2. Per-position flip benefit: does flipping reduce per-output-row error?
    3. Crystal health check: measure eigenstructure before and after
    4. Only apply flips that maintain or improve crystal health
    """
    layers = get_layers(model)
    stats = {}

    log(f"\n  Phase 1: Crystal ECC sign correction ({n_cal} sequences)")
    log(f"  Max flip rate: {max_flip_pct}%")

    for li in sieve_layers:
        mlp = layers[li].mlp
        proj_names = ["gate_proj", "up_proj", "down_proj"]
        layer_stats = {}

        for pname in proj_names:
            mod = getattr(mlp, pname)
            if not isinstance(mod, SievedLinear):
                continue

            out_f, in_f = mod.out_features, mod.in_features

            # Accumulate per-position error signal
            # flip_benefit[i,j] > 0 means flipping sign at (i,j) reduces
            # the squared error for output dimension i
            flip_benefit = torch.zeros(out_f, in_f, dtype=torch.float32,
                                       device='cpu')
            n_tokens = 0

            for seq_idx in range(min(n_cal, len(sequences))):
                seq = sequences[seq_idx]
                input_ids = seq.unsqueeze(0).to(device)

                # Capture projection input from sieved forward pass
                proj_input = {}

                def make_hook(name):
                    def fn(module, args):
                        x = args[0] if isinstance(args, tuple) else args
                        proj_input[name] = x.detach()
                    return fn

                hook = mod.register_forward_pre_hook(make_hook(pname))
                model(input_ids=input_ids)
                hook.remove()

                if pname not in proj_input:
                    continue

                x = proj_input[pname].float().squeeze(0)  # (seq, in_f)

                # Sieve output: what we currently produce
                sieve_out = (mod.signs.float()
                             * mod.magnitudes.float()) @ x.T  # (out, seq)

                # Teacher output: what original weight produces from
                # THIS (corrupted) input — the proper holographic target
                teacher_out = mod.original_weight.float() @ x.T  # (out, seq)

                # Per-position error: error[i] = teacher[i] - sieve[i]
                error = teacher_out - sieve_out  # (out, seq)

                # Flip benefit at (i,j): if we flip sign at (i,j),
                # output[i] changes by -2 * sign[i,j] * mag[i,j] * x[j]
                # This helps if: change has same sign as error[i]
                # benefit = -2 * sign[i,j] * mag[i,j] * Σ_k x_k[j] * error_k[i]
                # = -2 * sign[i,j] * mag[i,j] * (x.T @ error.T)[j,i]
                # Positive benefit = flip helps
                contrib = x.T @ error.T  # (in_f, out_f)
                benefit = (-2 * mod.signs.float()
                           * mod.magnitudes.float()
                           * contrib.T.to(device))  # (out_f, in_f)

                flip_benefit += benefit.cpu()
                n_tokens += x.shape[0]

            # Normalize by number of tokens
            if n_tokens > 0:
                flip_benefit /= n_tokens

            active = mod.mask.cpu() > 0

            # --- Crystal health BEFORE flips ---
            crystal_before = crystal_eigenvalue_health(mod.signs.cpu())

            # --- Select flip candidates ---
            # Candidates: active positions where flip has positive benefit
            candidates = active & (flip_benefit > 0)
            n_candidates = int(candidates.sum().item())
            n_active = int(active.sum().item())

            if n_candidates == 0:
                layer_stats[pname] = {
                    "n_active": n_active, "n_candidates": 0,
                    "n_flipped": 0, "crystal_before": crystal_before["health"],
                    "crystal_after": crystal_before["health"],
                }
                continue

            # Rank candidates by benefit magnitude
            benefit_vals = flip_benefit[candidates]
            max_flips = int(n_active * max_flip_pct / 100)

            # Take top-K by benefit
            if n_candidates > max_flips:
                topk_vals, topk_idx = torch.topk(
                    benefit_vals, max_flips)
                # Create filtered mask
                candidate_positions = candidates.nonzero(as_tuple=False)
                selected_positions = candidate_positions[topk_idx]
                flip_mask = torch.zeros_like(candidates)
                flip_mask[selected_positions[:, 0],
                          selected_positions[:, 1]] = True
            else:
                flip_mask = candidates

            n_to_flip = int(flip_mask.sum().item())

            # --- Apply flips ---
            signs_new = mod.signs.cpu().clone()
            signs_new[flip_mask] *= -1

            # --- Crystal health AFTER flips ---
            crystal_after = crystal_eigenvalue_health(signs_new)

            # --- Crystal ECC gate ---
            # Only keep flips if crystal health is maintained or improved
            if crystal_after["health"] >= crystal_before["health"] - 0.01:
                # Crystal approves: apply flips
                mod.signs.copy_(signs_new.to(device))
                status = "APPLIED"
                n_flipped = n_to_flip
            else:
                # Crystal rejects: try fewer flips (halve)
                # Binary search for max flips that maintain crystal health
                n_flipped = 0
                for fraction in [0.5, 0.25, 0.1, 0.05]:
                    n_try = max(1, int(n_to_flip * fraction))
                    benefit_vals_all = flip_benefit.clone()
                    benefit_vals_all[~candidates] = -float('inf')
                    flat_benefit = benefit_vals_all.flatten()
                    _, top_indices = torch.topk(flat_benefit, n_try)

                    signs_try = mod.signs.cpu().clone()
                    rows = top_indices // in_f
                    cols = top_indices % in_f
                    signs_try[rows, cols] *= -1

                    crystal_try = crystal_eigenvalue_health(signs_try)
                    if crystal_try["health"] >= crystal_before["health"] - 0.01:
                        mod.signs.copy_(signs_try.to(device))
                        crystal_after = crystal_try
                        n_flipped = n_try
                        status = f"REDUCED({fraction:.0%})"
                        break
                else:
                    status = "REJECTED"
                    crystal_after = crystal_before

            layer_stats[pname] = {
                "n_active": n_active,
                "n_candidates": n_candidates,
                "candidate_pct": round(n_candidates / max(n_active, 1) * 100, 2),
                "n_flipped": n_flipped,
                "flip_pct": round(n_flipped / max(n_active, 1) * 100, 2),
                "crystal_before": round(crystal_before["health"], 4),
                "crystal_after": round(crystal_after["health"], 4),
                "crystal_delta": round(
                    crystal_after["health"] - crystal_before["health"], 4),
                "status": status,
                "eigenvalues_before": crystal_before["eigenvalues"][:4],
                "eigenvalues_after": crystal_after["eigenvalues"][:4],
                "n_tokens": n_tokens,
            }

        stats[f"L{li}"] = layer_stats

        # Progress
        total_flips = sum(v.get("n_flipped", 0) for v in layer_stats.values())
        total_active = sum(v.get("n_active", 0) for v in layer_stats.values())
        statuses = [v.get("status", "?") for v in layer_stats.values()]
        health_deltas = [v.get("crystal_delta", 0) for v in layer_stats.values()]
        avg_delta = np.mean(health_deltas) if health_deltas else 0
        log(f"    L{li:>2d}: flipped={total_flips:>6,}"
            f" ({total_flips/max(total_active,1)*100:.2f}%)"
            f"  crystal_Δ={avg_delta:+.4f}"
            f"  [{','.join(statuses)}]")

    return stats


# ══════════════════════════════════════════════════════════════
# Phase 2: LoRA + Score Matching
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def cache_teacher_states(model, sequences, device, max_seqs=128):
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

        def make_hook(li):
            def fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                layer_states[li] = h[0].detach().cpu().half()
            return fn
        for li in range(n_layers):
            hooks.append(layers[li].register_forward_hook(make_hook(li)))
        model(input_ids=input_ids)
        for h in hooks:
            h.remove()

        state_list = [layer_states.get(-1, torch.zeros(1))]
        for li in range(n_layers):
            state_list.append(layer_states.get(li, torch.zeros(1)))
        all_states.append(torch.stack(state_list, dim=0))
        if (seq_idx + 1) % 32 == 0:
            log(f"      {seq_idx+1}/{min(max_seqs, len(sequences))} cached")
    return all_states


def compute_sm_loss(model, input_ids, teacher_hidden, device):
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
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--zero-rate", type=float, default=0.5)
    p.add_argument("--lora-rank", type=int, default=4)
    p.add_argument("--sm-steps", type=int, default=200)
    p.add_argument("--lr-lora", type=float, default=1e-4)
    p.add_argument("--alpha-sm", type=float, default=5.0)
    p.add_argument("--n-cal", type=int, default=256)
    p.add_argument("--n-holo-cal", type=int, default=64)
    p.add_argument("--n-eval", type=int, default=64)
    p.add_argument("--n-teacher-cache", type=int, default=128)
    p.add_argument("--seq-len", type=int, default=128)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--eval-every", type=int, default=50)
    p.add_argument("--max-flip-pct", type=float, default=5.0,
                   help="Max %% of active positions to flip per projection")
    p.add_argument("--shard-dir", type=str, default=str(SHARD_DIR))
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]

    log(f"\n{'='*70}")
    log("  CRYSTAL ECC SIGN CORRECTION")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  Sieve layers: {len(SIEVE_LAYERS)}")
    log(f"  Holo cal: {args.n_holo_cal}, max flip: {args.max_flip_pct}%")
    log(f"  LoRA rank: {args.lora_rank}, SM steps: {args.sm_steps}")

    # ── Load data ─────────────────────────────────────────
    shard_path = Path(args.shard_dir) / "shard_00000.npy"
    log(f"\n  Loading sequences from {shard_path.name}...")
    cal_sequences = load_sequences(
        shard_path, args.n_cal, seq_len=args.seq_len)
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

    # ── Cache teacher states (BEFORE sieve) ───────────────
    log(f"\n  Caching teacher states ({args.n_teacher_cache} seqs)...")
    t0 = time.time()
    teacher_cache = cache_teacher_states(
        model, cal_sequences, args.device,
        max_seqs=args.n_teacher_cache)
    log(f"  Cached {len(teacher_cache)} ({time.time()-t0:.0f}s)")

    # ═══════════════════════════════════════════════════════
    # Install sieve (keeping original weights as reference)
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  INSTALLING CRYSTAL SIEVE (with original weight reference)")
    log(f"{'═'*70}")

    layers = get_layers(model)

    # L0: SVD
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, 750)
        mod = FrozenLowRank(
            A.to(args.device), B.to(args.device)).to(args.device)
        setattr(mlp0, pname, mod)

    # Sieved layers — SievedLinear now keeps original_weight
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)
            mod = SievedLinear(
                proj.weight, zero_rate=args.zero_rate).to(args.device)
            setattr(mlp, pname, mod)

    sieve_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    sieve_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"  Sieve PPL: {sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)"
        f"  facts: {sieve_facts}/{total_facts}")

    # ── Crystal health baseline per layer ─────────────────
    log(f"\n  Crystal health baseline (sign pattern eigenstructure):")
    for li in SIEVE_LAYERS[:5]:  # sample first 5
        mlp = layers[li].mlp
        gate_mod = getattr(mlp, "gate_proj")
        if isinstance(gate_mod, SievedLinear):
            ch = crystal_eigenvalue_health(gate_mod.signs.cpu())
            dims = crystal_health_per_dim(gate_mod.signs.cpu())
            dim_str = " ".join(
                f"{d['dim']}D:{d['health']:+.3f}" for d in dims[:4])
            log(f"    L{li:>2d} gate: health={ch['health']:.4f}  [{dim_str}]")

    # ═══════════════════════════════════════════════════════
    # Phase 1: Crystal ECC Sign Correction
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 1: CRYSTAL ECC SIGN CORRECTION")
    log(f"{'═'*70}")

    t0 = time.time()
    ecc_stats = crystal_ecc_sign_correction(
        model, cal_sequences, args.device, SIEVE_LAYERS,
        n_cal=args.n_holo_cal, max_flip_pct=args.max_flip_pct)
    ecc_elapsed = time.time() - t0

    # Post-correction measurement
    corrected_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    corrected_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"\n  Post-correction PPL: {corrected_ppl:.2f}"
        f" ({corrected_ppl/base_ppl:.2f}x)"
        f"  facts: {corrected_facts}/{total_facts}")
    log(f"  Crystal ECC phase: {ecc_elapsed:.0f}s")

    # Summarize
    total_flipped = sum(
        v.get("n_flipped", 0) for ld in ecc_stats.values()
        for v in ld.values())
    total_active = sum(
        v.get("n_active", 0) for ld in ecc_stats.values()
        for v in ld.values())
    total_candidates = sum(
        v.get("n_candidates", 0) for ld in ecc_stats.values()
        for v in ld.values())
    statuses = [v.get("status", "?") for ld in ecc_stats.values()
                for v in ld.values()]
    applied = sum(1 for s in statuses if "APPLIED" in s)
    reduced = sum(1 for s in statuses if "REDUCED" in s)
    rejected = sum(1 for s in statuses if "REJECTED" in s)

    log(f"\n  Sign correction summary:")
    log(f"    Active positions:  {total_active:,}")
    log(f"    Flip candidates:   {total_candidates:,}"
        f" ({total_candidates/max(total_active,1)*100:.1f}%)")
    log(f"    Crystal-approved:  {total_flipped:,}"
        f" ({total_flipped/max(total_active,1)*100:.2f}%)")
    log(f"    ECC decisions:     {applied} applied,"
        f" {reduced} reduced, {rejected} rejected")
    log(f"    PPL: {sieve_ppl:.2f} → {corrected_ppl:.2f}")

    # ═══════════════════════════════════════════════════════
    # Phase 2: LoRA + Score Matching
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 2: LoRA + SCORE MATCHING")
    log(f"{'═'*70}")

    for li in [0] + SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            mod = getattr(mlp, pname)
            if hasattr(mod, 'add_lora'):
                mod.add_lora(args.lora_rank)

    lora_params = []
    total_lora = 0
    for li in [0] + SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            mod = getattr(mlp, pname)
            if hasattr(mod, 'lora_rank') and mod.lora_rank > 0:
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

            if not (torch.isnan(loss) or torch.isinf(loss)
                    or torch.isnan(ce_loss)):
                loss.backward()
                step_ce += ce_loss.item() * input_ids.numel()
                step_tokens += input_ids.numel()

        if step_tokens > 0:
            torch.nn.utils.clip_grad_norm_(lora_params, max_norm=1.0)
            optimizer.step()

        avg_ce = step_ce / max(step_tokens, 1)
        n_sm_batch = sum(1 for i in batch_indices if i < n_teacher)
        avg_sm = step_sm / max(n_sm_batch, 1)
        loss_history.append({"step": step+1, "ce": round(avg_ce, 4),
                             "sm": round(avg_sm, 4)})

        if (step + 1) % 10 == 0 or step == 0:
            log(f"    step {step+1:>3d}: CE={avg_ce:.4f}"
                f" SM={avg_sm:.4f} ({time.time()-t0:.0f}s)")

        if (step + 1) % args.eval_every == 0:
            eval_ppl = measure_ppl_tokens(
                model, eval_sequences, args.device)
            eval_facts, _ = measure_facts(model, tokenizer, args.device)
            log(f"    ▶ EVAL step {step+1}: PPL={eval_ppl:.2f}"
                f" ({eval_ppl/base_ppl:.3f}x)"
                f" facts={eval_facts}/{total_facts}")
            eval_history.append({
                "step": step+1, "ppl": eval_ppl,
                "ppl_ratio": round(eval_ppl / base_ppl, 4),
                "facts": eval_facts,
            })
            model.train()

    model.eval()
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
    log(f"  After ECC:     PPL={corrected_ppl:.2f} ({corrected_ppl/base_ppl:.2f}x)"
        f"  [crystal-gated sign correction]")
    log(f"  After LoRA+SM: PPL={final_ppl:.2f} ({final_ppl/base_ppl:.3f}x)"
        f"  facts={final_facts}/{total_facts}")
    log(f"  Crystal-approved flips: {total_flipped:,} / {total_active:,}"
        f" ({total_flipped/max(total_active,1)*100:.2f}%)")
    log(f"  ECC decisions: {applied} applied, {reduced} reduced,"
        f" {rejected} rejected")

    log(f"\n  vs v3b (LoRA+SM only):")
    log(f"    v3b:  25.67 → 16.27 (36.6% reduction, 1.44x base)")
    log(f"    ECC:  {sieve_ppl:.2f} → {corrected_ppl:.2f}"
        f" → {final_ppl:.2f}"
        f" ({(1-final_ppl/sieve_ppl)*100:.1f}% total,"
        f" {final_ppl/base_ppl:.2f}x)")

    # Save
    out_dir = _PROJECT_ROOT / "results" / "crystal-ecc-sign-correction"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    result = {
        "model": args.model,
        "version": "v1-crystal-ecc",
        "config": {
            "lora_rank": args.lora_rank, "sm_steps": args.sm_steps,
            "lr_lora": args.lr_lora, "alpha_sm": args.alpha_sm,
            "n_cal": len(cal_sequences), "n_holo_cal": args.n_holo_cal,
            "n_eval": len(eval_sequences),
            "n_teacher_cache": len(teacher_cache),
            "max_flip_pct": args.max_flip_pct,
            "sieve_layers": SIEVE_LAYERS,
        },
        "baseline_ppl": base_ppl, "baseline_facts": base_facts,
        "sieve_ppl": sieve_ppl, "sieve_facts": sieve_facts,
        "corrected_ppl": corrected_ppl, "corrected_facts": corrected_facts,
        "final_ppl": final_ppl, "final_ratio": round(final_ppl/base_ppl, 4),
        "final_facts": final_facts,
        "total_flipped": total_flipped, "total_active": total_active,
        "total_candidates": total_candidates,
        "ecc_decisions": {"applied": applied, "reduced": reduced,
                          "rejected": rejected},
        "ecc_stats": ecc_stats,
        "eval_history": eval_history,
        "loss_history": loss_history,
    }

    with open(out_dir / f"{slug}.json", "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Results saved to {out_dir / f'{slug}.json'}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
