#!/usr/bin/env python3
"""Direct Delta Correction — Compute the answer, don't train for it.

The teacher produces output_t at each layer. The sieve produces output_s.
The delta = output_t - output_s is directly computable. The optimal
rank-k additive correction is the truncated SVD of the weight residual,
optionally weighted by the input covariance (calibration-aware).

Algorithm:
  For each layer sequentially (cascade-aware):
    1. Run calibration data through model → collect actual inputs at this layer
    2. Compute W_delta = W_teacher - W_sieve for each projection
    3. Calibration-aware SVD: SVD(W_delta @ H^{1/2}) → undo whitening
       (H = input covariance, makes SVD optimal for actual input distribution)
    4. Install rank-k correction: A @ B ≈ W_delta (calibration-weighted)
    5. Layer is now corrected; downstream layers see corrected cascade

No training loop. No optimizer. No loss function. No hyperparameters
beyond rank k. One forward pass per layer + one SVD per projection.

Usage:
  uv run python scripts/experiments/direct_delta_correction.py \
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
# Sieve modules
# ══════════════════════════════════════════════════════════════

class SievedLinear(nn.Module):
    """Sieve with stored teacher weight for delta computation."""
    def __init__(self, weight, zero_rate=0.5):
        super().__init__()
        W = weight.detach().float().cpu()
        out_f, in_f = W.shape
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
        self.register_buffer("W_teacher", W.half())
        self.out_features, self.in_features = out_f, in_f
        # LoRA correction (initialized to zero)
        self.lora_A = None
        self.lora_B = None

    def install_correction(self, A, B):
        """Install computed rank-k correction."""
        self.lora_A = A  # (out_f, k) buffer
        self.lora_B = B  # (k, in_f) buffer

    def forward(self, x):
        out = x.float() @ self.W_sieve.float().T
        if self.lora_A is not None:
            out = out + x.float() @ self.lora_B.float().T @ self.lora_A.float().T
        return out.clamp(-65000, 65000).to(x.dtype)

    @property
    def W_delta(self):
        """Weight residual: what the sieve lost."""
        return (self.W_teacher.float() - self.W_sieve.float())


class LowRankLinear(nn.Module):
    """Low-rank approximation with stored teacher weight."""
    def __init__(self, weight, rank):
        super().__init__()
        W = weight.detach().float().cpu()
        U, S, Vt = torch.linalg.svd(W, full_matrices=False)
        r = min(rank, len(S))
        sqrt_S = S[:r].sqrt()
        A = U[:, :r] * sqrt_S.unsqueeze(0)
        B = Vt[:r, :] * sqrt_S.unsqueeze(1)
        self.register_buffer("svd_A", A)
        self.register_buffer("svd_B", B)
        self.register_buffer("W_teacher", W.half())
        self.out_features = A.shape[0]
        self.in_features = B.shape[1]
        self.lora_A = None
        self.lora_B = None

    def install_correction(self, A, B):
        self.lora_A = A
        self.lora_B = B

    def forward(self, x):
        out = x.float() @ self.svd_B.float().T @ self.svd_A.float().T
        if self.lora_A is not None:
            out = out + x.float() @ self.lora_B.float().T @ self.lora_A.float().T
        return out.clamp(-65000, 65000).to(x.dtype)

    @property
    def W_delta(self):
        W_approx = self.svd_A.float() @ self.svd_B.float()
        return (self.W_teacher.float() - W_approx)


# ══════════════════════════════════════════════════════════════
# Direct Delta Computation
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def collect_proj_inputs(model, sequences, device, layer_idx,
                        proj_names, max_seqs=32):
    """Run model forward, collect inputs to each projection at one layer."""
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp
    captured = {pn: [] for pn in proj_names}
    hooks = []

    for pn in proj_names:
        proj = getattr(mlp, pn)
        def make_hook(name):
            def fn(mod, args):
                x = args[0] if isinstance(args, tuple) else args
                captured[name].append(x[0].detach().float().cpu())
            return fn
        hooks.append(proj.register_forward_pre_hook(make_hook(pn)))

    for seq in sequences[:max_seqs]:
        input_ids = seq.unsqueeze(0).to(device)
        model(input_ids=input_ids)

    for h in hooks:
        h.remove()

    # Stack: (total_tokens, in_features)
    result = {}
    for pn in proj_names:
        if captured[pn]:
            result[pn] = torch.cat(captured[pn], dim=0)
    return result


def compute_calibration_aware_svd(W_delta, X, rank, reg=1e-4):
    """Calibration-aware rank-k approximation of W_delta.

    Minimizes E_x[||A@B@x - W_delta@x||²] where x ~ empirical(X).

    This equals minimizing ||A@B@H^½ - W_delta@H^½||²_F
    where H = X.T @ X / n (input covariance).

    Steps:
      1. Compute H^½ via eigendecomposition of X.T @ X
      2. Whiten: W_whitened = W_delta @ H^½
      3. SVD(W_whitened) → truncate to rank k
      4. Unwhiten B: B = B_whitened @ H^{-½}
    """
    n_tokens, in_f = X.shape
    out_f = W_delta.shape[0]

    # Input covariance (regularized for numerical stability)
    H = X.T @ X / n_tokens  # (in_f, in_f)
    H += reg * torch.eye(in_f, device=X.device, dtype=X.dtype)

    # H^{1/2} via eigendecomposition
    eigvals, eigvecs = torch.linalg.eigh(H)
    eigvals = eigvals.clamp(min=1e-8)
    H_sqrt = eigvecs @ torch.diag(eigvals.sqrt()) @ eigvecs.T
    H_inv_sqrt = eigvecs @ torch.diag(1.0 / eigvals.sqrt()) @ eigvecs.T

    # Whiten W_delta
    W_whitened = W_delta @ H_sqrt  # (out_f, in_f)

    # Truncated SVD of whitened delta
    U, S, Vt = torch.linalg.svd(W_whitened, full_matrices=False)
    k = min(rank, len(S))
    sqrt_S = S[:k].sqrt()

    # A in output space (unchanged by whitening)
    A = U[:, :k] * sqrt_S.unsqueeze(0)  # (out_f, k)

    # B in whitened space → unwhiten
    B_whitened = Vt[:k, :] * sqrt_S.unsqueeze(1)  # (k, in_f)
    B = B_whitened @ H_inv_sqrt  # (k, in_f) — unwhitened

    # Reconstruction quality
    W_recon = A @ B
    recon_err = (W_delta - W_recon).norm() / W_delta.norm()
    variance_captured = (S[:k]**2).sum() / (S**2).sum()

    return A, B, {
        "rank": k,
        "recon_error": float(recon_err),
        "variance_captured": float(variance_captured),
        "top_singular_values": S[:min(8, len(S))].tolist(),
    }


def compute_naive_svd(W_delta, rank):
    """Simple SVD of W_delta (no calibration weighting)."""
    U, S, Vt = torch.linalg.svd(W_delta, full_matrices=False)
    k = min(rank, len(S))
    sqrt_S = S[:k].sqrt()
    A = U[:, :k] * sqrt_S.unsqueeze(0)
    B = Vt[:k, :] * sqrt_S.unsqueeze(1)

    W_recon = A @ B
    recon_err = (W_delta - W_recon).norm() / W_delta.norm()
    variance_captured = (S[:k]**2).sum() / (S**2).sum()

    return A, B, {
        "rank": k,
        "recon_error": float(recon_err),
        "variance_captured": float(variance_captured),
        "top_singular_values": S[:min(8, len(S))].tolist(),
    }


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
    p.add_argument("--rank", type=int, default=4,
                   help="Rank for correction (matches v3b LoRA rank)")
    p.add_argument("--calibration-aware", action="store_true",
                   help="Use calibration-aware SVD (weight by input covariance)")
    p.add_argument("--n-cal", type=int, default=64,
                   help="Calibration sequences for input collection")
    p.add_argument("--n-eval", type=int, default=64)
    p.add_argument("--seq-len", type=int, default=128)
    p.add_argument("--eval-every", type=int, default=5,
                   help="Eval PPL every N layers")
    p.add_argument("--shard-dir", type=str, default=str(SHARD_DIR))
    p.add_argument("--ranks", type=str, default="",
                   help="Comma-separated ranks to sweep (e.g. 2,4,8,16,32)")
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]
    ALL_CORRECTED = [0] + SIEVE_LAYERS
    PROJ_NAMES = ["gate_proj", "up_proj", "down_proj"]

    # Rank sweep or single rank
    if args.ranks:
        rank_list = [int(r) for r in args.ranks.split(",")]
    else:
        rank_list = [args.rank]

    log(f"\n{'='*70}")
    log("  DIRECT DELTA CORRECTION")
    log("  Compute the answer, don't train for it")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  Ranks: {rank_list}")
    log(f"  Calibration-aware: {args.calibration_aware}")
    log(f"  Cal sequences: {args.n_cal}")

    # ── Load data ─────────────────────────────────────────
    shard_path = Path(args.shard_dir) / "shard_00000.npy"
    log(f"\n  Loading sequences...")
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

    # ── Install sieve (storing teacher weights) ───────────
    log(f"\n{'═'*70}")
    log("  INSTALLING SIEVE (preserving teacher weights)")
    log(f"{'═'*70}")

    layers = get_layers(model)

    # L0: Low-rank (stores teacher weight)
    mlp0 = layers[0].mlp
    for pname in PROJ_NAMES:
        proj = getattr(mlp0, pname)
        mod = LowRankLinear(proj.weight, rank=750).to(args.device)
        setattr(mlp0, pname, mod)

    # Sieved layers (store teacher weight)
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in PROJ_NAMES:
            proj = getattr(mlp, pname)
            mod = SievedLinear(
                proj.weight, zero_rate=args.zero_rate).to(args.device)
            setattr(mlp, pname, mod)

    sieve_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    sieve_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"  Sieve PPL: {sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)"
        f"  facts: {sieve_facts}/{total_facts}")

    # ═══════════════════════════════════════════════════════
    # Rank sweep
    # ═══════════════════════════════════════════════════════
    all_results = {}

    for rank in rank_list:
        log(f"\n{'═'*70}")
        log(f"  DIRECT DELTA CORRECTION — rank={rank}")
        if args.calibration_aware:
            log(f"  Mode: calibration-aware SVD")
        else:
            log(f"  Mode: naive SVD (no calibration)")
        log(f"{'═'*70}")

        # Reset corrections from previous rank
        for li in ALL_CORRECTED:
            mlp = layers[li].mlp
            for pname in PROJ_NAMES:
                mod = getattr(mlp, pname)
                mod.lora_A = None
                mod.lora_B = None

        layer_stats = {}
        total_correction_params = 0
        t0 = time.time()

        for step_idx, li in enumerate(ALL_CORRECTED):
            mlp = layers[li].mlp
            layer_params = 0

            if args.calibration_aware:
                # Collect actual inputs at this layer (after upstream corrections)
                proj_inputs = collect_proj_inputs(
                    model, cal_sequences, args.device, li, PROJ_NAMES,
                    max_seqs=args.n_cal)

            for pname in PROJ_NAMES:
                mod = getattr(mlp, pname)
                W_delta = mod.W_delta.cpu()  # (out_f, in_f)

                if args.calibration_aware and pname in proj_inputs:
                    X = proj_inputs[pname].cpu()  # (n_tokens, in_f)
                    A, B, svd_stats = compute_calibration_aware_svd(
                        W_delta, X, rank)
                else:
                    A, B, svd_stats = compute_naive_svd(W_delta, rank)

                # Install correction
                mod.install_correction(
                    A.half().to(args.device),
                    B.half().to(args.device))
                n_params = A.numel() + B.numel()
                layer_params += n_params
                total_correction_params += n_params

            layer_stats[li] = {
                "params": layer_params,
                "svd_stats": svd_stats,
            }

            # Periodic eval
            if (step_idx + 1) % args.eval_every == 0 or li == ALL_CORRECTED[-1]:
                ppl = measure_ppl_tokens(model, eval_sequences, args.device)
                layer_stats[li]["ppl"] = ppl
                layer_stats[li]["ppl_ratio"] = round(ppl / base_ppl, 4)
                elapsed = time.time() - t0
                log(f"    L{li:>2d} corrected"
                    f" ({step_idx+1}/{len(ALL_CORRECTED)}):"
                    f" PPL={ppl:.2f} ({ppl/base_ppl:.2f}x)"
                    f" recon_err={svd_stats['recon_error']:.4f}"
                    f" ({elapsed:.0f}s)")

        total_elapsed = time.time() - t0

        # Final measurement
        final_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
        final_facts, _ = measure_facts(model, tokenizer, args.device)

        log(f"\n  Rank {rank} results:")
        log(f"    Sieve:       PPL={sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)")
        log(f"    Corrected:   PPL={final_ppl:.2f} ({final_ppl/base_ppl:.3f}x)"
            f"  facts={final_facts}/{total_facts}")
        log(f"    Params:      {total_correction_params:,}")
        log(f"    Time:        {total_elapsed:.0f}s (no training)")
        log(f"    Improvement: {sieve_ppl:.2f} → {final_ppl:.2f}"
            f" ({(1-final_ppl/sieve_ppl)*100:.1f}% reduction)")

        all_results[rank] = {
            "rank": rank,
            "final_ppl": final_ppl,
            "final_ratio": round(final_ppl / base_ppl, 4),
            "final_facts": final_facts,
            "total_params": total_correction_params,
            "elapsed_s": round(total_elapsed, 1),
            "layer_stats": {str(k): v for k, v in layer_stats.items()},
        }

    # ═══════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  RESULTS SUMMARY")
    log(f"{'='*70}")
    log(f"  Baseline:    PPL={base_ppl:.2f}  facts={base_facts}/{total_facts}")
    log(f"  Sieve only:  PPL={sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)")
    log(f"")
    log(f"  {'Rank':>6} {'PPL':>8} {'Ratio':>8} {'Facts':>6}"
        f" {'Params':>10} {'Time':>6} {'Reduction':>10}")
    log(f"  {'─'*6} {'─'*8} {'─'*8} {'─'*6}"
        f" {'─'*10} {'─'*6} {'─'*10}")

    for rank in rank_list:
        r = all_results[rank]
        red = (1 - r["final_ppl"] / sieve_ppl) * 100
        log(f"  {rank:>6} {r['final_ppl']:>8.2f} {r['final_ratio']:>8.3f}x"
            f" {r['final_facts']:>5}/15 {r['total_params']:>10,}"
            f" {r['elapsed_s']:>5.0f}s {red:>9.1f}%")

    log(f"\n  vs v3b (LoRA rank-4 + SM, trained 200 steps):")
    log(f"    v3b:   25.67 → 16.27 (1.44x, 36.6% reduction, 5.9M params)")
    for rank in rank_list:
        r = all_results[rank]
        red = (1 - r["final_ppl"] / sieve_ppl) * 100
        log(f"    DDC-{rank}: {sieve_ppl:.2f} → {r['final_ppl']:.2f}"
            f" ({r['final_ratio']:.2f}x, {red:.1f}% reduction,"
            f" {r['total_params']:,} params)")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "direct-delta-correction"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")
    mode = "cal-aware" if args.calibration_aware else "naive"

    result = {
        "model": args.model,
        "version": f"v1-direct-delta-{mode}",
        "config": {
            "ranks": rank_list,
            "calibration_aware": args.calibration_aware,
            "n_cal": len(cal_sequences),
            "n_eval": len(eval_sequences),
            "sieve_layers": SIEVE_LAYERS,
        },
        "baseline_ppl": base_ppl, "baseline_facts": base_facts,
        "sieve_ppl": sieve_ppl, "sieve_facts": sieve_facts,
        "rank_results": all_results,
    }

    out_path = out_dir / f"{slug}_{mode}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Results saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
