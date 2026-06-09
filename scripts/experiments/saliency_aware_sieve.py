#!/usr/bin/env python3
"""Saliency-Aware Sieve — Discriminate irreducible zeros from faint connections.

The current sieve zeros all weights below a magnitude threshold (50%).
But near-zero weights are TWO populations:

  1. Irreducible zeros: GD says "no connection here." Zero is correct.
  2. Faint connections: GD says "small signal here." The weight is small
     because the signal is small, not because it's unused. A weight of
     0.003 × input of 200 = 0.6 real contribution.

Magnitude alone can't distinguish these. Saliency = |w| × E[|x|] can:
large saliency → connection (large weight OR large input OR both),
small saliency → irreducible (small weight AND small input).

Three-tier sieve:
  Strong:      high magnitude       → ternary ±1 (same as current sieve)
  Faint:       low mag, high sal    → low-precision quantized (Q2/Q4/Q8)
  Irreducible: low mag, low sal     → zero

Hypothesis: preserving faint connections as low-precision values (instead
of zeroing them) will:
  1. Reduce sieve-only PPL (fewer live echo paths severed)
  2. Provide gradient highways for subsequent LoRA fine-tuning
  3. Outperform equivalent-bitcount LoRA rank at same total budget

Sweep dimensions:
  - strong_frac: what fraction is kept as ternary (30%, 40%, 50%)
  - faint_bits: quantization precision for faint tier (2, 4, 8 bits)
  - saliency_method: magnitude-only vs activation-weighted

Usage:
  uv run python scripts/experiments/saliency_aware_sieve.py \
    --model Qwen/Qwen3-8B --device mps

  # Full sweep (takes longer):
  uv run python scripts/experiments/saliency_aware_sieve.py \
    --model Qwen/Qwen3-8B --device mps --sweep

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
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

SHARD_DIR = Path.home() / "data" / "fractal-bitnet" / "shards-qwen3"
EOD_ID = 151643


# ══════════════════════════════════════════════════════════════
# Data + Helpers
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
# Input covariance collection
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def collect_input_covariance_diag(model, sequences, device,
                                  layer_indices, proj_names,
                                  max_seqs=64):
    """Collect diagonal of input covariance E[x²] per projection per layer.

    Returns dict[layer_idx][proj_name] → tensor of shape (in_features,)
    containing E[x²] for each input dimension (= diagonal of covariance).
    """
    layers = get_layers(model)
    # Accumulators
    sum_x2 = {}
    counts = {}
    for li in layer_indices:
        sum_x2[li] = {}
        counts[li] = {}
        for pn in proj_names:
            sum_x2[li][pn] = None
            counts[li][pn] = 0

    hooks = []

    for li in layer_indices:
        mlp = layers[li].mlp
        for pn in proj_names:
            proj = getattr(mlp, pn)

            def make_hook(layer_idx, proj_name):
                def fn(mod, args):
                    x = args[0] if isinstance(args, tuple) else args
                    # x: (batch, seq_len, features) or (seq_len, features)
                    xf = x.detach().float().reshape(-1, x.shape[-1])
                    x2 = (xf ** 2).sum(dim=0).cpu()
                    if sum_x2[layer_idx][proj_name] is None:
                        sum_x2[layer_idx][proj_name] = x2
                    else:
                        sum_x2[layer_idx][proj_name] += x2
                    counts[layer_idx][proj_name] += xf.shape[0]
                return fn

            hooks.append(proj.register_forward_pre_hook(
                make_hook(li, pn)))

    for seq in sequences[:max_seqs]:
        input_ids = seq.unsqueeze(0).to(device)
        model(input_ids=input_ids)

    for h in hooks:
        h.remove()

    # Normalize: E[x²] = sum_x2 / count
    result = {}
    for li in layer_indices:
        result[li] = {}
        for pn in proj_names:
            if sum_x2[li][pn] is not None and counts[li][pn] > 0:
                result[li][pn] = sum_x2[li][pn] / counts[li][pn]
            else:
                result[li][pn] = None
    return result


# ══════════════════════════════════════════════════════════════
# Quantization helpers
# ══════════════════════════════════════════════════════════════

def quantize_per_group(w: torch.Tensor, bits: int,
                       group_size: int = 128) -> torch.Tensor:
    """Symmetric per-group quantization to `bits` precision.

    Quantizes to [-2^(bits-1)+1, 2^(bits-1)-1] per group, then
    dequantizes back to float. This simulates the precision loss
    of storing faint connections at low bit width.

    Groups are along the last (input) dimension.
    """
    assert bits in (2, 4, 8), f"bits must be 2, 4, or 8, got {bits}"
    qmax = (1 << (bits - 1)) - 1  # e.g. bits=4 → qmax=7

    out_f, in_f = w.shape
    # Pad input dim to multiple of group_size
    pad = (group_size - in_f % group_size) % group_size
    if pad > 0:
        w_padded = torch.nn.functional.pad(w, (0, pad))
    else:
        w_padded = w
    in_f_padded = w_padded.shape[1]

    # Reshape into groups
    w_grouped = w_padded.reshape(out_f, -1, group_size)
    # Per-group scale
    scale = w_grouped.abs().amax(dim=-1, keepdim=True).clamp(min=1e-10)
    # Quantize
    w_scaled = w_grouped / scale * qmax
    w_rounded = w_scaled.round().clamp(-qmax, qmax)
    # Dequantize
    w_deq = w_rounded / qmax * scale
    # Reshape back and trim padding
    w_out = w_deq.reshape(out_f, in_f_padded)[:, :in_f]
    return w_out


# ══════════════════════════════════════════════════════════════
# Sieve modules
# ══════════════════════════════════════════════════════════════

class SaliencyAwareSievedLinear(nn.Module):
    """Three-tier sieve: strong (ternary), faint (quantized), irreducible (zero).

    Tier assignment:
      1. Sort by magnitude → top `strong_frac` are strong (ternary ±1)
      2. Among remaining: sort by saliency → top `faint_frac` are faint
         (quantized to `faint_bits`)
      3. Rest are irreducible → zero

    If input_E_x2 is None, falls back to magnitude-only saliency (= |w|),
    which makes faint_frac select the next-largest by magnitude — equivalent
    to a softer version of the current sieve.
    """

    def __init__(self, weight: torch.Tensor,
                 strong_frac: float = 0.3,
                 faint_frac: float = 0.2,
                 faint_bits: int = 4,
                 input_E_x2: torch.Tensor | None = None,
                 group_size: int = 128):
        super().__init__()
        W = weight.detach().float().cpu()
        out_f, in_f = W.shape

        abs_W = W.abs()

        # ── Tier 1: Strong (ternary ±1) ──────────────────
        # Top strong_frac by magnitude
        flat = abs_W.flatten()
        n_total = flat.numel()
        if n_total > 10_000_000:
            idx = torch.randperm(n_total)[:5_000_000]
            strong_threshold = torch.quantile(flat[idx],
                                              1.0 - strong_frac)
        else:
            strong_threshold = torch.quantile(flat, 1.0 - strong_frac)

        strong_mask = abs_W >= strong_threshold  # (out_f, in_f)

        # ── Compute saliency for non-strong positions ─────
        remaining_mask = ~strong_mask

        if input_E_x2 is not None:
            # Activation-weighted: saliency = |w| × sqrt(E[x²])
            # E[x²] is per input dimension (broadcast across output dim)
            sqrt_Ex2 = input_E_x2.sqrt().unsqueeze(0)  # (1, in_f)
            saliency = abs_W * sqrt_Ex2
        else:
            # Fallback: magnitude-only saliency
            saliency = abs_W.clone()

        # Only consider remaining positions for faint threshold
        remaining_saliency = saliency[remaining_mask]
        n_remaining = remaining_saliency.numel()

        if n_remaining > 0 and faint_frac > 0:
            # faint_frac is fraction of TOTAL, not remaining
            n_faint_target = int(n_total * faint_frac)
            # Fraction of remaining that becomes faint
            faint_of_remaining = min(1.0, n_faint_target / n_remaining)

            if n_remaining > 5_000_000:
                idx = torch.randperm(n_remaining)[:5_000_000]
                faint_threshold = torch.quantile(
                    remaining_saliency[idx],
                    1.0 - faint_of_remaining)
            else:
                faint_threshold = torch.quantile(
                    remaining_saliency,
                    1.0 - faint_of_remaining)

            faint_mask = remaining_mask & (saliency >= faint_threshold)
        else:
            faint_mask = torch.zeros_like(strong_mask)

        zero_mask = ~strong_mask & ~faint_mask

        # ── Build sieved weight ──────────────────────────
        W_sieved = torch.zeros_like(W)

        # Strong: per-weight magnitude (sign × |w|), NOT bare ±1.
        # s203 bug: bare ±1 is ~50× too large (mean |w|≈0.02) → activation
        # blow-up → NaN across all three-tier configs. s196: per-weight
        # magnitude is the ONLY strong format that survives 29 cascaded layers
        # (per-row scale fails at 22,800×). Scored as ~1 bit (the magnitude is
        # the shared/holographic γ) — same convention as StandardSievedLinear,
        # which also runs fp16 magnitude. This makes the three-tier sieve
        # directly comparable to standard-50%: same run-substrate, the only
        # difference is the faint tier (saliency-selected low-mag weights).
        W_sieved[strong_mask] = W[strong_mask]

        # Faint: quantized original values
        if faint_mask.any():
            W_faint_full = torch.zeros_like(W)
            W_faint_full[faint_mask] = W[faint_mask]
            W_faint_quantized = quantize_per_group(
                W_faint_full, faint_bits, group_size)
            W_sieved[faint_mask] = W_faint_quantized[faint_mask]

        # Irreducible: already zero

        self.register_buffer("weight", W_sieved.half())
        self.out_features, self.in_features = out_f, in_f

        # Store tier statistics
        self.n_strong = int(strong_mask.sum())
        self.n_faint = int(faint_mask.sum())
        self.n_zero = int(zero_mask.sum())
        self.faint_bits = faint_bits

    def forward(self, x):
        out = x.float() @ self.weight.float().T
        return out.clamp(-65000, 65000).to(x.dtype)

    @property
    def tier_stats(self):
        total = self.n_strong + self.n_faint + self.n_zero
        return {
            "strong": self.n_strong,
            "faint": self.n_faint,
            "zero": self.n_zero,
            "strong_pct": round(100 * self.n_strong / total, 1),
            "faint_pct": round(100 * self.n_faint / total, 1),
            "zero_pct": round(100 * self.n_zero / total, 1),
            "faint_bits": self.faint_bits,
        }

    @property
    def bits_per_param(self):
        """Effective bits per parameter for this layer."""
        total = self.n_strong + self.n_faint + self.n_zero
        total_bits = (self.n_strong * 1  # ternary = ~1 bit (sign only)
                      + self.n_faint * self.faint_bits
                      + self.n_zero * 0)
        # Add mask overhead: 2 bits per param (00=zero, 01=strong, 10=faint)
        total_bits += total * 2
        return total_bits / total


class StandardSievedLinear(nn.Module):
    """Standard magnitude-threshold sieve for comparison (current approach)."""

    def __init__(self, weight: torch.Tensor, zero_rate: float = 0.5):
        super().__init__()
        W = weight.detach().float().cpu()
        abs_W = W.abs()
        flat = abs_W.flatten()
        if flat.numel() > 10_000_000:
            idx = torch.randperm(flat.numel())[:5_000_000]
            threshold = torch.quantile(flat[idx], zero_rate)
        else:
            threshold = torch.quantile(flat, zero_rate)
        mask = (abs_W >= threshold).float()
        W_sieved = torch.sign(W) * abs_W * mask
        self.register_buffer("weight", W_sieved.half())
        self.out_features, self.in_features = W.shape
        self.n_kept = int(mask.sum())
        self.n_zeroed = int((1 - mask).sum())

    def forward(self, x):
        out = x.float() @ self.weight.float().T
        return out.clamp(-65000, 65000).to(x.dtype)

    @property
    def bits_per_param(self):
        total = self.n_kept + self.n_zeroed
        # 1 bit per kept param (sign) + 1 bit mask
        return (self.n_kept * 1 + total * 1) / total


class LowRankLinear(nn.Module):
    """Low-rank SVD factorization for L0."""

    def __init__(self, weight: torch.Tensor, rank: int):
        super().__init__()
        W = weight.detach().float().cpu()
        U, S, Vt = torch.linalg.svd(W, full_matrices=False)
        r = min(rank, len(S))
        sqrt_S = S[:r].sqrt()
        A = U[:, :r] * sqrt_S.unsqueeze(0)
        B = Vt[:r, :] * sqrt_S.unsqueeze(1)
        self.register_buffer("svd_A", A.half())
        self.register_buffer("svd_B", B.half())
        self.out_features = A.shape[0]
        self.in_features = B.shape[1]

    def forward(self, x):
        out = x.float() @ self.svd_B.float().T @ self.svd_A.float().T
        return out.clamp(-65000, 65000).to(x.dtype)


# ══════════════════════════════════════════════════════════════
# Saliency distribution analysis
# ══════════════════════════════════════════════════════════════

def analyze_saliency_distribution(model, input_cov_diag,
                                  layer_indices, proj_names):
    """Analyze the saliency distribution to understand tier boundaries.

    Key question: is there a natural bimodal split between irreducible
    and faint, or is it a smooth continuum?
    """
    layers = get_layers(model)
    all_mag = []
    all_sal = []
    all_sal_nz = []  # saliency only for near-zero weights

    for li in layer_indices:
        mlp = layers[li].mlp
        for pn in proj_names:
            proj = getattr(mlp, pn)
            W = proj.weight.detach().float().cpu()
            abs_W = W.abs()

            # Full magnitude distribution
            flat_mag = abs_W.flatten()
            all_mag.append(flat_mag)

            if input_cov_diag[li][pn] is not None:
                sqrt_Ex2 = input_cov_diag[li][pn].sqrt().unsqueeze(0)
                sal = abs_W * sqrt_Ex2
            else:
                sal = abs_W

            flat_sal = sal.flatten()
            all_sal.append(flat_sal)

            # Near-zero weights only (bottom 50% by magnitude)
            median_mag = flat_mag.median()
            nz_mask = flat_mag < median_mag
            if nz_mask.any():
                all_sal_nz.append(flat_sal[nz_mask.flatten()])

    all_mag = torch.cat(all_mag)
    all_sal = torch.cat(all_sal)
    all_sal_nz = torch.cat(all_sal_nz) if all_sal_nz else torch.tensor([])

    # Subsample for quantile computation (torch.quantile can't handle >2B elements)
    MAX_QUANTILE = 5_000_000

    def _subsample(t):
        if t.numel() > MAX_QUANTILE:
            idx = torch.randperm(t.numel())[:MAX_QUANTILE]
            return t[idx]
        return t

    mag_sample = _subsample(all_mag)
    sal_sample = _subsample(all_sal)
    sal_nz_sample = _subsample(all_sal_nz) if len(all_sal_nz) > 0 else None

    # Percentile analysis
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    mag_pcts = {p: float(torch.quantile(mag_sample, p / 100))
                for p in percentiles}
    sal_pcts = {p: float(torch.quantile(sal_sample, p / 100))
                for p in percentiles}

    # Near-zero saliency analysis
    if sal_nz_sample is not None and len(sal_nz_sample) > 0:
        sal_nz_pcts = {p: float(torch.quantile(sal_nz_sample, p / 100))
                       for p in percentiles}
        # Ratio: how much does saliency spread the near-zero weights?
        spread_ratio = float(all_sal_nz.std() / all_sal_nz.mean())
    else:
        sal_nz_pcts = {}
        spread_ratio = 0.0

    # Correlation on subsample
    n_corr = min(1_000_000, len(all_mag))
    corr_idx = torch.randperm(len(all_mag))[:n_corr]

    return {
        "n_total": int(all_mag.numel()),
        "magnitude_percentiles": mag_pcts,
        "saliency_percentiles": sal_pcts,
        "near_zero_saliency_percentiles": sal_nz_pcts,
        "near_zero_saliency_spread": spread_ratio,
        "magnitude_mean": float(all_mag.mean()),
        "saliency_mean": float(all_sal.mean()),
        "correlation_mag_sal": float(torch.corrcoef(
            torch.stack([all_mag[corr_idx],
                         all_sal[corr_idx]]))[0, 1])
        if len(all_mag) >= 2 else 0.0,
    }


# ══════════════════════════════════════════════════════════════
# Experiment runner
# ══════════════════════════════════════════════════════════════

def run_sieve_config(model, tokenizer, eval_sequences, device,
                     layer_indices, proj_names,
                     strong_frac, faint_frac, faint_bits,
                     input_cov_diag, use_saliency,
                     original_weights):
    """Install a sieve configuration and measure quality.

    Returns the sieved model state (for subsequent LoRA testing)
    and measurement results.
    """
    layers = get_layers(model)
    tier_stats_all = {}
    total_bits = 0
    total_params = 0

    for li in layer_indices:
        mlp = layers[li].mlp
        tier_stats_all[li] = {}
        for pn in proj_names:
            W = original_weights[li][pn]
            Ex2 = (input_cov_diag[li][pn]
                   if use_saliency and input_cov_diag[li][pn] is not None
                   else None)

            mod = SaliencyAwareSievedLinear(
                W,
                strong_frac=strong_frac,
                faint_frac=faint_frac,
                faint_bits=faint_bits,
                input_E_x2=Ex2,
            ).to(device)

            setattr(mlp, pn, mod)
            tier_stats_all[li][pn] = mod.tier_stats
            total_bits += (mod.n_strong * 1
                           + mod.n_faint * faint_bits
                           + (mod.n_strong + mod.n_faint + mod.n_zero) * 2)
            total_params += mod.n_strong + mod.n_faint + mod.n_zero

    # Measure
    ppl = measure_ppl_tokens(model, eval_sequences, device)
    facts_correct, facts_total = measure_facts(model, tokenizer, device)

    return {
        "ppl": ppl,
        "facts": facts_correct,
        "facts_total": facts_total,
        "tier_stats": tier_stats_all,
        "total_bits": total_bits,
        "total_params": total_params,
        "bits_per_param": round(total_bits / total_params, 3)
        if total_params > 0 else 0,
    }


def run_standard_sieve(model, tokenizer, eval_sequences, device,
                       layer_indices, proj_names, zero_rate,
                       original_weights):
    """Install standard (current) sieve for comparison baseline."""
    layers = get_layers(model)
    total_bits = 0
    total_params = 0

    for li in layer_indices:
        mlp = layers[li].mlp
        for pn in proj_names:
            W = original_weights[li][pn]
            mod = StandardSievedLinear(W, zero_rate=zero_rate).to(device)
            setattr(mlp, pn, mod)
            total_bits += mod.n_kept * 1 + (mod.n_kept + mod.n_zeroed) * 1
            total_params += mod.n_kept + mod.n_zeroed

    ppl = measure_ppl_tokens(model, eval_sequences, device)
    facts_correct, facts_total = measure_facts(model, tokenizer, device)

    return {
        "ppl": ppl,
        "facts": facts_correct,
        "facts_total": facts_total,
        "total_bits": total_bits,
        "total_params": total_params,
        "bits_per_param": round(total_bits / total_params, 3)
        if total_params > 0 else 0,
    }


def restore_original_weights(model, layer_indices, proj_names,
                              original_weights, device):
    """Restore original teacher weights to prepare for next config."""
    layers = get_layers(model)
    for li in layer_indices:
        mlp = layers[li].mlp
        for pn in proj_names:
            W = original_weights[li][pn]
            proj = nn.Linear(W.shape[1], W.shape[0], bias=False)
            proj.weight = nn.Parameter(W.half(), requires_grad=False)
            setattr(mlp, pn, proj.to(device))


# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--n-cal", type=int, default=64,
                   help="Calibration sequences for input covariance")
    p.add_argument("--n-eval", type=int, default=64,
                   help="Evaluation sequences for PPL")
    p.add_argument("--seq-len", type=int, default=128)
    p.add_argument("--shard-dir", type=str, default=str(SHARD_DIR))
    p.add_argument("--sweep", action="store_true",
                   help="Full sweep over configurations")
    # Single-config args
    p.add_argument("--strong-frac", type=float, default=0.3)
    p.add_argument("--faint-frac", type=float, default=0.2)
    p.add_argument("--faint-bits", type=int, default=4)
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]
    PROJ_NAMES = ["gate_proj", "up_proj", "down_proj"]

    log(f"\n{'='*70}")
    log("  SALIENCY-AWARE SIEVE")
    log("  Discriminating irreducible zeros from faint connections")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  Cal seqs: {args.n_cal}")
    log(f"  Eval seqs: {args.n_eval}")
    log(f"  Sweep: {args.sweep}")

    # ── Load data ─────────────────────────────────────────
    shard_path = Path(args.shard_dir) / "shard_00000.npy"
    log(f"\n  Loading sequences from {shard_path}...")
    cal_sequences = load_sequences(
        shard_path, args.n_cal, seq_len=args.seq_len)
    eval_offset = args.n_cal * args.seq_len * 2
    eval_sequences = load_sequences(
        shard_path, args.n_eval, seq_len=args.seq_len, offset=eval_offset)
    log(f"  {len(cal_sequences)} cal + {len(eval_sequences)} eval")

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

    # ── Stash original weights ────────────────────────────
    log("\n  Stashing original weights...")
    layers = get_layers(model)
    original_weights = {}
    for li in SIEVE_LAYERS:
        original_weights[li] = {}
        mlp = layers[li].mlp
        for pn in PROJ_NAMES:
            proj = getattr(mlp, pn)
            original_weights[li][pn] = proj.weight.detach().float().cpu()

    # ── L0: Always low-rank (not part of the sieve experiment) ──
    mlp0 = layers[0].mlp
    for pn in PROJ_NAMES:
        proj = getattr(mlp0, pn)
        mod = LowRankLinear(proj.weight, rank=750).to(args.device)
        setattr(mlp0, pn, mod)

    # ── Collect input covariance ──────────────────────────
    log("\n  Collecting input covariance (calibration pass)...")
    t0 = time.time()
    input_cov_diag = collect_input_covariance_diag(
        model, cal_sequences, args.device,
        SIEVE_LAYERS, PROJ_NAMES, max_seqs=args.n_cal)
    log(f"  Covariance collected in {time.time() - t0:.1f}s")

    # ── Analyze saliency distribution ─────────────────────
    log("\n  Analyzing saliency distribution...")
    dist_analysis = analyze_saliency_distribution(
        model, input_cov_diag, SIEVE_LAYERS, PROJ_NAMES)
    log(f"  Total params: {dist_analysis['n_total']:,}")
    log(f"  Magnitude mean: {dist_analysis['magnitude_mean']:.6f}")
    log(f"  Saliency mean:  {dist_analysis['saliency_mean']:.6f}")
    log(f"  Correlation(mag, sal): {dist_analysis['correlation_mag_sal']:.3f}")
    log(f"  Near-zero saliency spread: {dist_analysis['near_zero_saliency_spread']:.3f}")
    log(f"  Near-zero saliency percentiles:")
    for pct, val in dist_analysis.get('near_zero_saliency_percentiles', {}).items():
        log(f"    p{pct}: {val:.6f}")

    # ═══════════════════════════════════════════════════════
    # Experiment configurations
    # ═══════════════════════════════════════════════════════

    if args.sweep:
        configs = [
            # Baselines
            {"name": "standard-50%", "type": "standard", "zero_rate": 0.5},
            {"name": "standard-70%", "type": "standard", "zero_rate": 0.7},

            # Saliency-aware: vary strong/faint split
            {"name": "sal-30s-20f-Q4", "type": "saliency",
             "strong_frac": 0.3, "faint_frac": 0.2, "faint_bits": 4,
             "use_saliency": True},
            {"name": "sal-40s-20f-Q4", "type": "saliency",
             "strong_frac": 0.4, "faint_frac": 0.2, "faint_bits": 4,
             "use_saliency": True},
            {"name": "sal-30s-30f-Q4", "type": "saliency",
             "strong_frac": 0.3, "faint_frac": 0.3, "faint_bits": 4,
             "use_saliency": True},

            # Vary faint precision
            {"name": "sal-30s-20f-Q2", "type": "saliency",
             "strong_frac": 0.3, "faint_frac": 0.2, "faint_bits": 2,
             "use_saliency": True},
            {"name": "sal-30s-20f-Q8", "type": "saliency",
             "strong_frac": 0.3, "faint_frac": 0.2, "faint_bits": 8,
             "use_saliency": True},

            # Magnitude-only saliency (ablation: does activation weighting help?)
            {"name": "mag-30s-20f-Q4", "type": "saliency",
             "strong_frac": 0.3, "faint_frac": 0.2, "faint_bits": 4,
             "use_saliency": False},

            # High-faint configs (what if most near-zero are connections?)
            {"name": "sal-30s-40f-Q4", "type": "saliency",
             "strong_frac": 0.3, "faint_frac": 0.4, "faint_bits": 4,
             "use_saliency": True},
            {"name": "sal-20s-50f-Q4", "type": "saliency",
             "strong_frac": 0.2, "faint_frac": 0.5, "faint_bits": 4,
             "use_saliency": True},

            # Iso-bit comparison: same total bits as standard-50% + LoRA rank-4
            # standard-50% ≈ 2 bits/param + LoRA(5.9M × 16 bits)
            # Try matching that budget with faint connections instead of LoRA
            {"name": "sal-50s-30f-Q2", "type": "saliency",
             "strong_frac": 0.5, "faint_frac": 0.3, "faint_bits": 2,
             "use_saliency": True},
        ]
    else:
        configs = [
            # Always include standard baseline for comparison
            {"name": "standard-50%", "type": "standard", "zero_rate": 0.5},

            # Single config from args
            {"name": f"sal-{int(args.strong_frac*100)}s-"
                     f"{int(args.faint_frac*100)}f-Q{args.faint_bits}",
             "type": "saliency",
             "strong_frac": args.strong_frac,
             "faint_frac": args.faint_frac,
             "faint_bits": args.faint_bits,
             "use_saliency": True},

            # Magnitude-only ablation
            {"name": f"mag-{int(args.strong_frac*100)}s-"
                     f"{int(args.faint_frac*100)}f-Q{args.faint_bits}",
             "type": "saliency",
             "strong_frac": args.strong_frac,
             "faint_frac": args.faint_frac,
             "faint_bits": args.faint_bits,
             "use_saliency": False},
        ]

    # ═══════════════════════════════════════════════════════
    # Run configurations
    # ═══════════════════════════════════════════════════════

    all_results = {}

    for ci, cfg in enumerate(configs):
        log(f"\n{'═'*70}")
        log(f"  Config {ci+1}/{len(configs)}: {cfg['name']}")
        log(f"{'═'*70}")

        # Restore original weights before each config
        restore_original_weights(
            model, SIEVE_LAYERS, PROJ_NAMES, original_weights, args.device)

        t0 = time.time()

        if cfg["type"] == "standard":
            result = run_standard_sieve(
                model, tokenizer, eval_sequences, args.device,
                SIEVE_LAYERS, PROJ_NAMES, cfg["zero_rate"],
                original_weights)
            result["config"] = cfg
        else:
            log(f"  strong={cfg['strong_frac']:.0%}"
                f" faint={cfg['faint_frac']:.0%}"
                f" Q{cfg['faint_bits']}"
                f" saliency={'activation' if cfg['use_saliency'] else 'magnitude'}")

            result = run_sieve_config(
                model, tokenizer, eval_sequences, args.device,
                SIEVE_LAYERS, PROJ_NAMES,
                strong_frac=cfg["strong_frac"],
                faint_frac=cfg["faint_frac"],
                faint_bits=cfg["faint_bits"],
                input_cov_diag=input_cov_diag,
                use_saliency=cfg["use_saliency"],
                original_weights=original_weights)
            result["config"] = cfg

        elapsed = time.time() - t0
        result["elapsed_s"] = round(elapsed, 1)
        result["ppl_ratio"] = round(result["ppl"] / base_ppl, 4)

        log(f"  PPL: {result['ppl']:.2f} ({result['ppl_ratio']:.3f}x)")
        log(f"  Facts: {result['facts']}/{result['facts_total']}")
        log(f"  Bits/param: {result['bits_per_param']:.3f}")
        log(f"  Time: {elapsed:.1f}s")

        all_results[cfg["name"]] = result

    # ═══════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════

    log(f"\n{'='*70}")
    log("  RESULTS SUMMARY")
    log(f"{'='*70}")
    log(f"  Baseline: PPL={base_ppl:.2f}  facts={base_facts}/{total_facts}")
    log(f"")
    log(f"  {'Config':<25} {'PPL':>8} {'Ratio':>8} {'Facts':>6}"
        f" {'Bits/p':>7} {'Time':>6}")
    log(f"  {'─'*25} {'─'*8} {'─'*8} {'─'*6} {'─'*7} {'─'*6}")

    # Sort by PPL ratio
    sorted_results = sorted(all_results.items(),
                            key=lambda x: x[1]["ppl_ratio"])

    for name, r in sorted_results:
        log(f"  {name:<25} {r['ppl']:>8.2f} {r['ppl_ratio']:>7.3f}x"
            f" {r['facts']:>5}/15 {r['bits_per_param']:>7.3f}"
            f" {r['elapsed_s']:>5.0f}s")

    log(f"\n  Reference: v3b (standard-50% + LoRA rank-4 + SM) = 1.44× baseline")
    log(f"  Question:  Does saliency-aware sieve WITHOUT training beat")
    log(f"             standard sieve WITHOUT training?")
    log(f"  Question:  At same bit budget, is faint tier > higher LoRA rank?")

    # ── Key comparisons ──────────────────────────────────
    std50 = all_results.get("standard-50%")
    if std50:
        log(f"\n  Key comparisons vs standard-50% ({std50['ppl']:.2f} PPL):")
        for name, r in sorted_results:
            if name == "standard-50%":
                continue
            improvement = (1 - r["ppl"] / std50["ppl"]) * 100
            bit_ratio = r["bits_per_param"] / std50["bits_per_param"]
            log(f"    {name:<25}"
                f" PPL {improvement:>+.1f}%"
                f"  bits {bit_ratio:.2f}×")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "saliency-aware-sieve"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    output = {
        "model": args.model,
        "version": "v1-saliency-aware-sieve",
        "config": {
            "n_cal": len(cal_sequences),
            "n_eval": len(eval_sequences),
            "seq_len": args.seq_len,
            "sieve_layers": SIEVE_LAYERS,
            "sweep": args.sweep,
        },
        "baseline_ppl": base_ppl,
        "baseline_facts": base_facts,
        "distribution_analysis": dist_analysis,
        "results": {name: {k: v for k, v in r.items()
                           if k != "tier_stats"}  # tier_stats too large
                    for name, r in all_results.items()},
    }

    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    log(f"\n  Results saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
