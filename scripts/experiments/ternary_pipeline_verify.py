#!/usr/bin/env python3
"""Ternary Pipeline Verification — does 2-bit encoding preserve 1.03x?

The β-expansion experiment proved: crystal sieve + 4 continuation
residuals = 1.03x PPL. But the sieve stored full per-weight magnitudes
(sign(W) * |W| * mask as float16 = NO compression).

This experiment verifies: does the COMPRESSED encoding (ternary signs
+ per-row scale + binary mask = 2 bits/weight) give the same result?

If yes: 29 sieved layers compress from 8,352MB to 1,046MB (8x).
If no: we need more magnitude resolution (per-group scaling).

Usage:
  uv run python scripts/experiments/ternary_pipeline_verify.py \
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


def log(msg=""):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


def get_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise RuntimeError(f"Can't find layers in {type(model)}")


def measure_ppl(model, tokenizer, texts, device):
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
    enc = tokenizer(prompt, return_tensors="pt")
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=max_new,
                             do_sample=False, temperature=1.0,
                             pad_token_id=tokenizer.pad_token_id)
    return tokenizer.decode(out[0][enc["input_ids"].shape[1]:],
                            skip_special_tokens=True)


def measure_facts(model, tokenizer, device):
    correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(model, tokenizer, fp["prompt"], device)
        if fp["expected"].lower() in gen.lower():
            correct += 1
    return correct, len(FACT_PROMPTS)


# ══════════════════════════════════════════════════════════════
# Two sieve implementations to compare
# ══════════════════════════════════════════════════════════════

class FullMagnitudeSieve(nn.Module):
    """sign(W) * |W| * mask — stores full per-weight magnitudes."""
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


class TernaryPerRowSieve(nn.Module):
    """sign(W) * per_row_scale * mask — 2 bits/weight + tiny scales.

    This is the COMPRESSED encoding. Stores:
      - ternary: int8 {-1, 0, +1} (could be 2 bits in production)
      - per_row_scale: float16, one per output row
    Reconstructs: W_approx[i,j] = ternary[i,j] * scale[i]
    """
    def __init__(self, weight, zero_rate=0.5):
        super().__init__()
        W = weight.detach().float().cpu()
        out_features, in_features = W.shape

        signs = torch.sign(W)
        abs_W = W.abs()

        if zero_rate > 0:
            flat = abs_W.flatten()
            if flat.numel() > 10_000_000:
                idx = torch.randperm(flat.numel())[:5_000_000]
                threshold = torch.quantile(flat[idx], zero_rate)
            else:
                threshold = torch.quantile(flat, zero_rate)
            signs[abs_W < threshold] = 0

        # Per-row scale: mean |W| of non-zero entries per row
        nonzero = (signs != 0).float()
        row_abs_sum = (abs_W * nonzero).sum(dim=1)
        row_count = nonzero.sum(dim=1).clamp(min=1)
        per_row_scale = row_abs_sum / row_count

        # Precompute W_approx for speed (in production, reconstruct on-the-fly)
        W_approx = signs * per_row_scale.unsqueeze(1)
        self.register_buffer("W_approx", W_approx.half())

        # Storage metrics (what would actually be stored)
        self.ternary_bytes = signs.numel()  # int8 = 1 byte (2 bits in prod)
        self.scale_bytes = out_features * 2  # float16
        self.compressed_mb = (self.ternary_bytes + self.scale_bytes) / 1024 / 1024
        self.orig_mb = W.numel() * 2 / 1024 / 1024

        # Reconstruction quality
        W_full_sieve = torch.sign(W) * abs_W * nonzero
        cos_vs_full = F.cosine_similarity(
            W_full_sieve.reshape(1, -1),
            W_approx.float().reshape(1, -1)).item()
        self.cos_vs_full_sieve = cos_vs_full

    def forward(self, x):
        out = x.float() @ self.W_approx.float().T
        return out.clamp(-65000, 65000).to(x.dtype)


class ContinuationResidual(nn.Module):
    def __init__(self, d_model, rank=32):
        super().__init__()
        self.W_down = nn.Parameter(torch.randn(d_model, rank) * 0.001)
        self.W_up = nn.Parameter(torch.randn(rank, d_model) * 0.001)

    def forward(self, x):
        correction = x.float() @ self.W_down @ self.W_up
        return (x.float() + correction).to(x.dtype)


class TrainableLowRankLinear(nn.Module):
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
    return U[:, :r] * sqrt_S.unsqueeze(0), Vt[:r, :] * sqrt_S.unsqueeze(1)


# ══════════════════════════════════════════════════════════════
# Build pipeline + train continuations
# ══════════════════════════════════════════════════════════════

def build_and_test(model, tokenizer, device, sieve_class,
                   label, base_ppl, base_facts,
                   melt_steps=100, lr=1e-4):
    """Build full pipeline with given sieve class, train continuations."""
    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]
    RESIDUAL_LAYERS = [0, 9, 21, 26]

    layers = get_layers(model)
    d_model = model.config.hidden_size

    # L0 SVD
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, 750)
        setattr(mlp0, pname,
                TrainableLowRankLinear(A.to(device), B.to(device)))

    # Sieve layers
    total_compressed = 0
    total_orig = 0
    cos_values = []
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)
            sieve = sieve_class(proj.weight, zero_rate=0.5).to(device)
            setattr(mlp, pname, sieve)
            if hasattr(sieve, 'compressed_mb'):
                total_compressed += sieve.compressed_mb
                total_orig += sieve.orig_mb
            if hasattr(sieve, 'cos_vs_full_sieve'):
                cos_values.append(sieve.cos_vs_full_sieve)

    if cos_values:
        log(f"    Ternary vs full-magnitude sieve: cos={np.mean(cos_values):.4f}")
    if total_compressed > 0:
        log(f"    Compressed: {total_compressed:.0f}MB vs {total_orig:.0f}MB"
            f" ({total_orig/total_compressed:.1f}x)")

    # Measure pre-melt
    pre_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
    pre_facts, _ = measure_facts(model, tokenizer, device)
    pre_ratio = pre_ppl / base_ppl
    log(f"    Pre-melt: PPL={pre_ppl:.2f} ({pre_ratio:.2f}x)"
        f"  facts={pre_facts}/15")

    # Install continuations
    trainable_params = []
    cont_hooks = []
    for li in RESIDUAL_LAYERS:
        cont = ContinuationResidual(d_model, rank=32).to(device)
        trainable_params.extend([cont.W_down, cont.W_up])

        def make_hook(c):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                corrected = c(h)
                if isinstance(out, tuple):
                    return (corrected,) + out[1:]
                return corrected
            return hook_fn

        cont_hooks.append(
            layers[li].register_forward_hook(make_hook(cont)))

    n_trainable = sum(p.numel() for p in trainable_params)

    # Freeze all, enable continuations
    for param in model.parameters():
        param.requires_grad = False
    for param in trainable_params:
        param.requires_grad = True

    # Train
    optimizer = torch.optim.Adam(trainable_params, lr=lr)
    model.train()
    history = []
    t0 = time.time()

    for step in range(melt_steps):
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
            if not (np.isnan(out.loss.item()) or np.isinf(out.loss.item())):
                out.loss.backward()
                total_loss += out.loss.item() * labels.numel()
                total_tokens += labels.numel()
        if total_tokens == 0:
            continue
        torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=0.5)
        optimizer.step()
        history.append(total_loss / total_tokens)

        if (step + 1) % 25 == 0 or step == 0:
            elapsed = time.time() - t0
            log(f"      step {step+1}: loss={history[-1]:.4f} ({elapsed:.0f}s)")

    model.eval()

    # Measure post-melt
    post_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
    post_facts, _ = measure_facts(model, tokenizer, device)
    post_ratio = post_ppl / base_ppl
    log(f"    Post-melt: PPL={post_ppl:.2f} ({post_ratio:.2f}x)"
        f"  facts={post_facts}/15")

    # Clean up hooks
    for h in cont_hooks:
        h.remove()

    return {
        "label": label,
        "pre_melt_ppl": round(pre_ppl, 4),
        "pre_melt_ratio": round(pre_ratio, 4),
        "pre_melt_facts": pre_facts,
        "post_melt_ppl": round(post_ppl, 4),
        "post_melt_ratio": round(post_ratio, 4),
        "post_melt_facts": post_facts,
        "n_trainable": n_trainable,
        "loss_start": round(history[0], 4) if history else None,
        "loss_end": round(history[-1], 4) if history else None,
        "compressed_mb": round(total_compressed, 1) if total_compressed else None,
        "orig_mb": round(total_orig, 1) if total_orig else None,
    }


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--melt-steps", type=int, default=100)
    args = p.parse_args()

    log(f"\n{'='*70}")
    log("  TERNARY PIPELINE VERIFICATION")
    log("  Does 2-bit encoding preserve the 1.03x result?")
    log(f"{'='*70}")

    dtype = (torch.float16
             if any(s in args.model for s in ["8B", "14B", "32B"])
             else torch.float32)
    log(f"\n  Loading {args.model} ({dtype})...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    log("\n  Measuring baseline...")
    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    base_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"  Baseline: PPL={base_ppl:.2f}, facts={base_facts}/15")

    # ── Test A: Full magnitude sieve (the proven version) ─
    log(f"\n{'═'*70}")
    log("  TEST A: Full magnitude sieve (sign * |W| * mask)")
    log(f"{'═'*70}")

    result_a = build_and_test(
        model, tokenizer, args.device,
        FullMagnitudeSieve, "full_magnitude",
        base_ppl, base_facts, args.melt_steps)

    # Reload model for clean comparison
    log(f"\n  Reloading model for Test B...")
    del model
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    import gc; gc.collect()

    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    model.eval()

    # ── Test B: Ternary per-row sieve (the compressed version) ─
    log(f"\n{'═'*70}")
    log("  TEST B: Ternary per-row sieve (2 bits + per-row scale)")
    log(f"{'═'*70}")

    result_b = build_and_test(
        model, tokenizer, args.device,
        TernaryPerRowSieve, "ternary_per_row",
        base_ppl, base_facts, args.melt_steps)

    # ══════════════════════════════════════════════════════
    # Comparison
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  HEAD-TO-HEAD COMPARISON")
    log(f"{'='*70}")
    log(f"  Baseline: PPL={base_ppl:.2f}")
    log(f"")
    log(f"  {'':>25s}  {'Pre-melt':>10s}  {'Post-melt':>10s}  {'Facts':>6s}  {'Size':>10s}")
    log(f"  {'─'*25}  {'─'*10}  {'─'*10}  {'─'*6}  {'─'*10}")

    for r in [result_a, result_b]:
        size_str = f"{r['compressed_mb']:.0f}MB" if r['compressed_mb'] else "same"
        log(f"  {r['label']:>25s}  {r['pre_melt_ratio']:>8.2f}x  "
            f"{r['post_melt_ratio']:>8.2f}x  "
            f"{r['post_melt_facts']:>4d}/15  {size_str:>10s}")

    delta = result_a["post_melt_ratio"] - result_b["post_melt_ratio"]
    verdict = ("VERIFIED" if abs(delta) < 0.1 else
               "CLOSE" if abs(delta) < 0.3 else "DIFFERENT")
    log(f"\n  Δ(post-melt): {delta:+.4f}x")
    log(f"  VERDICT: {verdict}")

    if result_b['compressed_mb']:
        log(f"\n  COMPRESSION: {result_b['orig_mb']:.0f}MB → {result_b['compressed_mb']:.0f}MB"
            f" = {result_b['orig_mb']/result_b['compressed_mb']:.1f}x"
            f" at {result_b['post_melt_ratio']:.2f}x PPL")

    # Save
    out_dir = _PROJECT_ROOT / "results" / "ternary-pipeline-verify"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")
    result = {
        "model": args.model,
        "baseline_ppl": base_ppl,
        "baseline_facts": base_facts,
        "full_magnitude": result_a,
        "ternary_per_row": result_b,
        "delta_post_melt": round(delta, 4),
        "verdict": verdict,
    }
    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
