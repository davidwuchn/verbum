#!/usr/bin/env python3
"""Latent Diffusion Sign Correction — Progressive denoising in crystal eigenspace.

Tests the diffusion-holographic isomorphism prediction:
progressive sign correction in the crystal's 16D latent space should
outperform one-shot correction.

The 16×16 crystal space:
  8 crystal positions (fire:K, fire:I, fire:B, fire:C, fire:D, fire:W, fire:Y, fire:WHNF)
  8 anti-crystal positions (whnf:K, whnf:I, whnf:B, whnf:C, whnf:D, whnf:W, whnf:Y, whnf:WHNF)

This gives a 16D latent manifold for sign patterns. The experiment:

1. Install sieve, compute sign pattern's 16D eigenspace
2. Project the sieve ERROR into this eigenspace (what's lost from masking)
3. Apply corrections PROGRESSIVELY (like denoising schedule):
   - Level 1: top-2 eigenvectors (coarsest crystal structure)
   - Level 2: top-4 eigenvectors (KIBC basis)
   - Level 3: top-8 eigenvectors (full crystal)
   - Level 4: top-16 eigenvectors (crystal + anti-crystal)
4. At each level, flip signs that project onto the corrected latent
5. Measure PPL at each level (progressive improvement curve)
6. Compare to one-shot (all levels at once) and random baseline

Prediction from the isomorphism:
  progressive > one-shot > random (for same number of flips)
  because coarse structure must be correct before fine detail matters

Usage:
  uv run python scripts/experiments/latent_diffusion_signs.py \
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
PHI = (1 + 5 ** 0.5) / 2


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
# Crystal Eigenspace Computation
# ══════════════════════════════════════════════════════════════

def compute_sign_eigenspace(signs: torch.Tensor, n_dims=16,
                            n_sample=20000):
    """Compute the top-k eigenspace of a sign pattern.

    The sign pattern's column-wise correlation gives us the crystal
    latent space. Each eigenvector defines a direction in output-space
    that captures a mode of the crystal.

    For the full 16×16 space (crystal + anti-crystal), we take the
    top-16 eigenvectors of the sign correlation matrix.

    Returns:
        eigvals: (n_dims,) — eigenvalues (variance per crystal dimension)
        eigvecs: (out_features, n_dims) — eigenvectors (crystal directions)
    """
    out_f, in_f = signs.shape

    # Sample columns for tractability
    if in_f > n_sample:
        idx = torch.randperm(in_f)[:n_sample]
        S = signs[:, idx].float()
    else:
        S = signs.float()

    # Row correlation: captures how output dimensions co-vary in sign space
    # C[i,j] = correlation of sign patterns between output dims i and j
    C = S @ S.T / S.shape[1]  # (out_f, out_f)

    # Top-k eigendecomposition
    eigvals, eigvecs = torch.linalg.eigh(C)
    # eigh returns ascending order, flip to descending
    eigvals = eigvals.flip(0)[:n_dims]
    eigvecs = eigvecs.flip(1)[:, :n_dims]

    return eigvals, eigvecs


def project_to_eigenspace(signs: torch.Tensor, eigvecs: torch.Tensor):
    """Project a sign matrix into the crystal eigenspace.

    Returns: (n_dims, in_features) — the latent representation.
    Each row is how much each input dimension loads on that crystal mode.
    """
    # eigvecs: (out_f, n_dims)
    # signs: (out_f, in_f)
    # projection: eigvecs.T @ signs → (n_dims, in_f)
    return eigvecs.T @ signs.float()


def reconstruct_from_eigenspace(latent: torch.Tensor,
                                eigvecs: torch.Tensor):
    """Reconstruct signs from latent representation.

    latent: (n_dims, in_f)
    eigvecs: (out_f, n_dims)
    Returns: (out_f, in_f) — reconstructed sign pattern (continuous)
    """
    return eigvecs @ latent


# ══════════════════════════════════════════════════════════════
# Progressive Latent Sign Correction
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def progressive_latent_correction(model, sequences, device, sieve_layers,
                                  n_cal=64, max_flip_pct=5.0,
                                  levels=(2, 4, 8, 16)):
    """Progressive sign correction in crystal eigenspace.

    For each sieved projection:
    1. Compute 16D eigenspace of sign pattern (crystal + anti-crystal)
    2. Project the ERROR (full_W @ x - sieve_W @ x) into eigenspace
    3. Progressively reconstruct corrections at each level (2, 4, 8, 16 dims)
    4. At each level, flip the highest-benefit positions

    Returns per-level PPL measurements.
    """
    layers = get_layers(model)
    eval_sequences = sequences  # use same for simplicity in prototype

    level_results = []

    for level_idx, n_dims in enumerate(levels):
        log(f"\n  ── Level {level_idx+1}: top-{n_dims} crystal dimensions ──")

        total_flipped = 0
        total_active = 0

        for li in sieve_layers:
            mlp = layers[li].mlp
            layer_flips = 0

            for pname in ["gate_proj", "up_proj", "down_proj"]:
                mod = getattr(mlp, pname)
                if not hasattr(mod, 'original_weight'):
                    continue

                signs = mod.signs.cpu()
                mask = mod.mask.cpu()
                mags = mod.magnitudes.cpu()
                full_W = mod.original_weight.cpu()
                active = mask > 0
                out_f, in_f = signs.shape

                # Compute eigenspace from CURRENT sign pattern
                eigvals, eigvecs = compute_sign_eigenspace(
                    signs, n_dims=n_dims)

                # Collect error signal from calibration data
                error_accumulator = torch.zeros(out_f, dtype=torch.float32)
                flip_signal = torch.zeros(out_f, in_f, dtype=torch.float32)
                n_tokens = 0

                for seq_idx in range(min(n_cal, len(sequences))):
                    seq = sequences[seq_idx]
                    input_ids = seq.unsqueeze(0).to(device)

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

                    x = proj_input[pname].float().squeeze(0).cpu()

                    # Current sieve output
                    sieve_out = (signs.float() * mags.float()) @ x.T

                    # Teacher output (full weight on sieve input)
                    teacher_out = full_W.float() @ x.T

                    # Error per output dimension
                    error = teacher_out - sieve_out  # (out_f, seq)

                    # Project error into crystal eigenspace
                    # error_latent = eigvecs.T @ error  # (n_dims, seq)
                    # Only correct the component in the top-n_dims subspace

                    # Per-position flip benefit (constrained to eigenspace)
                    # Flip at (i,j) helps if it reduces error projected
                    # onto the eigenspace directions
                    #
                    # The benefit of flipping (i,j) in the eigenspace:
                    # new_contribution = -sign[i,j]*mag[i,j]*x[j]
                    # projected onto eigvecs column containing i
                    #
                    # Simplified: benefit = error[i] * (-2*sign[i,j]*mag[i,j]*x[j])
                    # filtered through eigenspace
                    benefit = -2 * signs.float() * mags.float() * (
                        error @ x)  # (out_f, in_f)

                    # Project through eigenspace (only keep signal in
                    # the top-n_dims subspace)
                    # For each output dim i, its eigenspace loading is
                    # eigvecs[i, :]. The projected benefit at (i,j) is:
                    # benefit_proj[i,j] = Σ_k eigvecs[i,k] * (eigvecs[:,k].T @ benefit[:,j])[k]
                    # = (eigvecs @ eigvecs.T @ benefit)[i,j]
                    # This is just the projection operator P = eigvecs @ eigvecs.T
                    P = eigvecs @ eigvecs.T  # (out_f, out_f) projection
                    benefit_proj = P @ benefit  # (out_f, in_f)

                    flip_signal += benefit_proj
                    n_tokens += x.shape[0]

                if n_tokens == 0:
                    continue

                flip_signal /= n_tokens

                # Only flip at active positions with positive projected benefit
                candidates = active & (flip_signal > 0)
                n_candidates = int(candidates.sum().item())
                n_active = int(active.sum().item())
                total_active += n_active

                if n_candidates == 0:
                    continue

                # Limit flip rate per level
                max_flips = int(n_active * max_flip_pct / 100 / len(levels))
                if n_candidates > max_flips:
                    vals = flip_signal[candidates]
                    _, topk = torch.topk(vals, max_flips)
                    positions = candidates.nonzero(as_tuple=False)
                    selected = positions[topk]
                    flip_mask = torch.zeros_like(candidates)
                    flip_mask[selected[:, 0], selected[:, 1]] = True
                else:
                    flip_mask = candidates

                n_flip = int(flip_mask.sum().item())

                # Apply flips to the actual model
                new_signs = mod.signs.cpu().clone()
                new_signs[flip_mask] *= -1
                mod.signs.copy_(new_signs.to(device))

                layer_flips += n_flip
                total_flipped += n_flip

            if (li + 1) % 5 == 0 or li == sieve_layers[0]:
                log(f"    L{li:>2d}: {layer_flips:>6,} flips this level")

        # Measure PPL at this level
        ppl = measure_ppl_tokens(model, eval_sequences[:32], device)
        facts, _ = measure_facts(model, tokenizer, device)

        log(f"  Level {level_idx+1} (top-{n_dims}):"
            f" {total_flipped:,} flips,"
            f" PPL={ppl:.2f}, facts={facts}/15")

        level_results.append({
            "level": level_idx + 1,
            "n_dims": n_dims,
            "flips": total_flipped,
            "flip_pct": round(
                total_flipped / max(total_active, 1) * 100, 3),
            "ppl": ppl,
            "facts": facts,
        })

    return level_results


# ══════════════════════════════════════════════════════════════
# Sieved Linear (same as crystal_ecc version)
# ══════════════════════════════════════════════════════════════

class SievedLinear(nn.Module):
    def __init__(self, weight, zero_rate=0.5):
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
        self.register_buffer("original_weight", W)  # FULL weight

        self.out_features = out_features
        self.in_features = in_features

    def forward(self, x):
        W_eff = self.signs.float() * self.magnitudes.float()
        out = x.float() @ W_eff.T
        return out.clamp(-65000, 65000).to(x.dtype)

    @property
    def n_flips(self):
        with torch.no_grad():
            teacher_signs = torch.sign(self.original_weight)
            active = self.mask > 0
            return int(((self.signs != teacher_signs) & active).sum().item())


class FrozenLowRank(nn.Module):
    def __init__(self, A, B):
        super().__init__()
        self.register_buffer("svd_A", A)
        self.register_buffer("svd_B", B)

    def forward(self, x):
        out = x.float() @ self.svd_B.T @ self.svd_A.T
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
# Main
# ══════════════════════════════════════════════════════════════

def main():
    global tokenizer  # needed by progressive_latent_correction

    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--zero-rate", type=float, default=0.5)
    p.add_argument("--n-cal", type=int, default=256)
    p.add_argument("--n-holo-cal", type=int, default=32,
                   help="Sequences for holographic recording per level")
    p.add_argument("--n-eval", type=int, default=64)
    p.add_argument("--seq-len", type=int, default=128)
    p.add_argument("--max-flip-pct", type=float, default=5.0)
    p.add_argument("--shard-dir", type=str, default=str(SHARD_DIR))
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]

    log(f"\n{'='*70}")
    log("  LATENT DIFFUSION SIGN CORRECTION")
    log("  Progressive denoising in crystal eigenspace")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  Levels: 2D → 4D → 8D → 16D (progressive)")
    log(f"  Max flip: {args.max_flip_pct}% total across all levels")

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

    # ═══════════════════════════════════════════════════════
    # Install sieve
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  INSTALLING CRYSTAL SIEVE")
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

    # Sieved layers
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

    # ── Eigenspace analysis (sample layer) ────────────────
    log(f"\n  Crystal eigenspace structure (L15 gate_proj):")
    sample_mod = getattr(layers[15].mlp, "gate_proj")
    if isinstance(sample_mod, SievedLinear):
        eigvals, eigvecs = compute_sign_eigenspace(
            sample_mod.signs.cpu(), n_dims=16)
        log(f"    Top-16 eigenvalues: {eigvals.numpy().round(2).tolist()}")
        ratios = (eigvals / eigvals[0]).numpy()
        log(f"    Ratios (λ_k/λ_0): {ratios.round(3).tolist()}")
        # Crystal equation predictions for comparison
        s = 4 / 5
        beta = [0, 1, 1+PHI, 2+PHI]
        pred = [PHI ** (-s * b) for b in beta]
        log(f"    Crystal eq predicts: {[round(p,3) for p in pred]}")
        log(f"    Observed (top-4):    {ratios[:4].round(3).tolist()}")

    # ═══════════════════════════════════════════════════════
    # Progressive Latent Correction
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PROGRESSIVE LATENT SIGN CORRECTION")
    log("  Denoising schedule: 2D → 4D → 8D → 16D")
    log(f"{'═'*70}")

    level_results = progressive_latent_correction(
        model, cal_sequences, args.device, SIEVE_LAYERS,
        n_cal=args.n_holo_cal,
        max_flip_pct=args.max_flip_pct,
        levels=[2, 4, 8, 16])

    # Final measurement
    final_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    final_facts, _ = measure_facts(model, tokenizer, args.device)

    # ═══════════════════════════════════════════════════════
    # Results
    # ═══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  RESULTS — PROGRESSIVE DENOISING CURVE")
    log(f"{'='*70}")
    log(f"  Baseline:   PPL={base_ppl:.2f}")
    log(f"  Sieve only: PPL={sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)")
    log(f"")
    log(f"  {'Level':<8} {'Dims':<6} {'Flips':<10} {'PPL':<10} {'Ratio':<8} {'Facts'}")
    log(f"  {'─'*8} {'─'*6} {'─'*10} {'─'*10} {'─'*8} {'─'*5}")

    for r in level_results:
        log(f"  {r['level']:<8} {r['n_dims']:<6} {r['flips']:<10,}"
            f" {r['ppl']:<10.2f} {r['ppl']/base_ppl:<8.3f} {r['facts']}/15")

    log(f"")
    log(f"  Final:      PPL={final_ppl:.2f} ({final_ppl/base_ppl:.3f}x)"
        f"  facts={final_facts}/{total_facts}")
    log(f"")
    log(f"  Prediction: progressive curve should be monotonically improving")
    log(f"  If 2D > 4D > 8D > 16D (each level helps): isomorphism CONFIRMED")
    log(f"  If flat or non-monotonic: eigenspace is not the right latent")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "latent-diffusion-signs"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    result = {
        "model": args.model,
        "version": "v1-progressive-latent",
        "config": {
            "n_cal": len(cal_sequences),
            "n_holo_cal": args.n_holo_cal,
            "n_eval": len(eval_sequences),
            "max_flip_pct": args.max_flip_pct,
            "levels": [2, 4, 8, 16],
            "sieve_layers": SIEVE_LAYERS,
        },
        "baseline_ppl": base_ppl,
        "baseline_facts": base_facts,
        "sieve_ppl": sieve_ppl,
        "sieve_facts": sieve_facts,
        "final_ppl": final_ppl,
        "final_facts": final_facts,
        "level_results": level_results,
    }

    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Results saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
