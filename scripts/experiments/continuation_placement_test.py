#!/usr/bin/env python3
"""Continuation Placement Test — Tree-aligned vs Zone-aligned.

Compares two continuation placement strategies:
  A. Zone-aligned (s196):    [0, 9, 21, 26]   — functional zone boundaries
  B. Tree-aligned (s197):    [2, 8, 21, 33]   — bridge node crossover layers

Both use the same crystal sieve (sign ⊙ |W| ⊙ mask₅₀%) on 29 layers,
L0 SVD at r=750, same continuation rank, same training procedure.

If the multi-tree model is correct:
  - Tree-aligned should achieve ≤ zone-aligned PPL
  - Tree-transition continuations (L2, L8, L33) correct phase errors
  - Plateau checkpoint (L21, shared) corrects cascade drift
  - Tree-aligned might need LOWER rank for same quality

The script runs: baseline → sieve → placement A → placement B,
measuring PPL and facts at each stage.

Usage:
  uv run python scripts/experiments/continuation_placement_test.py \
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

# ═══════════════════════════════════════════════════════════
# Eval texts (same as beta_expansion.py)
# ═══════════════════════════════════════════════════════════

EVAL_TEXTS = [
    "The theory of general relativity describes gravity as the curvature of spacetime caused by mass and energy.",
    "In a large mixing bowl, combine the flour, sugar, and baking powder. Make a well in the center.",
    "The committee voted unanimously to approve the new environmental regulations for manufacturing plants.",
    "She walked through the ancient forest, her footsteps muffled by centuries of fallen leaves.",
    "The function takes two arguments and returns their composition as a new callable object.",
    "During the Cambrian explosion, roughly 541 million years ago, most major animal phyla appeared.",
    "The patient was admitted with acute respiratory distress. Initial blood work showed elevated levels.",
    "To solve this equation, first isolate the variable on one side by subtracting three from both sides.",
]

CALIBRATION_TEXTS = [
    "The quick brown fox jumps over the lazy dog near the riverbank.",
    "In mathematics, a prime number is a natural number greater than one.",
    "She carefully arranged the flowers in the vase on the kitchen table.",
    "The algorithm processes each element of the array in linear time.",
    "Historical evidence suggests that agriculture began approximately ten thousand years ago.",
    "The new policy requires all employees to complete the training module.",
    "He opened the old wooden door and stepped into the dimly lit hallway.",
    "The chemical reaction produces hydrogen gas and sodium chloride as byproducts.",
    "After careful consideration, the board decided to proceed with the merger.",
    "The recursive function computes the Fibonacci sequence by calling itself.",
    "Light travels at approximately three hundred thousand kilometers per second.",
    "The ancient ruins were discovered beneath the modern city's foundation.",
]

FACT_PROMPTS = [
    ("The capital of France is", "Paris"),
    ("Water freezes at", "0"),
    ("The speed of light is approximately", "300"),
    ("The chemical symbol for gold is", "Au"),
    ("The largest planet in our solar system is", "Jupiter"),
    ("DNA stands for", "deoxyribonucle"),
    ("The boiling point of water is", "100"),
    ("Shakespeare was born in", "Stratford"),
    ("The square root of 144 is", "12"),
    ("Photosynthesis converts sunlight into", "energy"),
    ("The human body has 206", "bone"),
    ("Pi is approximately", "3.14"),
    ("The Earth orbits the", "Sun"),
    ("Oxygen's atomic number is", "8"),
    ("The Great Wall of China is located in", "China"),
]


def log(msg):
    print(msg, flush=True)


# ═══════════════════════════════════════════════════════════
# Model helpers (from beta_expansion.py)
# ═══════════════════════════════════════════════════════════

def get_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return list(model.model.layers)
    raise RuntimeError("Cannot find layers")


def measure_ppl(model, tokenizer, texts, device):
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        enc = {k: v.to(device) for k, v in enc.items()}
        with torch.no_grad():
            out = model(**enc, labels=enc["input_ids"])
        n = enc["input_ids"].numel()
        total_loss += out.loss.item() * n
        total_tokens += n
    return float(np.exp(total_loss / total_tokens))


def measure_facts(model, tokenizer, device):
    model.eval()
    correct = 0
    for prompt, expected in FACT_PROMPTS:
        enc = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=10, do_sample=False,
                                 temperature=None, top_p=None)
        gen = tokenizer.decode(out[0][enc["input_ids"].shape[1]:],
                               skip_special_tokens=True)
        if expected.lower() in gen.lower():
            correct += 1
    return correct, len(FACT_PROMPTS)


def svd_factorize(weight, rank):
    W = weight.detach().float().cpu()  # SVD on CPU explicitly
    U, S, Vh = torch.linalg.svd(W, full_matrices=False)
    A = U[:, :rank] * S[:rank].unsqueeze(0)
    B = Vh[:rank, :]
    return A, B


class TrainableLowRankLinear(nn.Module):
    def __init__(self, A, B):
        super().__init__()
        self.A = nn.Parameter(A.float())
        self.B = nn.Parameter(B.float())

    def forward(self, x):
        return (x.float() @ self.B.T @ self.A.T).to(x.dtype)


class FrozenSieveLinear(nn.Module):
    def __init__(self, weight, zero_rate=0.5):
        super().__init__()
        W = weight.detach().float().cpu()
        signs = torch.sign(W)
        magnitudes = W.abs()
        # Use numpy for quantile (torch.quantile fails on large MPS tensors)
        threshold = float(np.quantile(magnitudes.numpy().ravel(), zero_rate))
        mask = (magnitudes > threshold).float()
        self.register_buffer('sieve', (signs * magnitudes * mask).to(weight.dtype))

    def forward(self, x):
        return x @ self.sieve.T


class ContinuationResidual(nn.Module):
    def __init__(self, d_model, rank=32):
        super().__init__()
        self.W_down = nn.Parameter(torch.randn(d_model, rank) * 0.001)
        self.W_up = nn.Parameter(torch.randn(rank, d_model) * 0.001)

    def forward(self, x):
        correction = x.float() @ self.W_down @ self.W_up
        return (x.float() + correction).to(x.dtype)


# ═══════════════════════════════════════════════════════════
# Core test
# ═══════════════════════════════════════════════════════════

def install_sieve(model, sieve_layers, device, zero_rate=0.5):
    """Install crystal sieve on specified layers + L0 SVD."""
    layers = get_layers(model)
    # L0 SVD
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, 750)
        setattr(mlp0, pname, TrainableLowRankLinear(A.to(device), B.to(device)))
    # Sieve remaining
    for li in sieve_layers:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)
            setattr(mlp, pname, FrozenSieveLinear(proj.weight, zero_rate).to(device))
    return layers


def run_continuation_test(model, tokenizer, layers, residual_layers, rank,
                          device, label, melt_steps=100, lr=1e-4):
    """Install continuations, train, measure."""
    d_model = model.config.hidden_size
    continuations = {}
    cont_hooks = []
    trainable_params = []

    for li in residual_layers:
        cont = ContinuationResidual(d_model, rank=rank).to(device)
        continuations[li] = cont
        trainable_params.extend([cont.W_down, cont.W_up])

        def make_hook(c):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                corrected = c(h)
                return (corrected,) + out[1:] if isinstance(out, tuple) else corrected
            return hook_fn
        cont_hooks.append(layers[li].register_forward_hook(make_hook(cont)))

    n_params = sum(p.numel() for p in trainable_params)
    log(f"    Continuations at L{residual_layers}, rank={rank}, params={n_params:,}")

    # Train
    optimizer = torch.optim.Adam(trainable_params, lr=lr)
    model.train()
    losses = []
    t0 = time.time()

    for step in range(melt_steps):
        optimizer.zero_grad()
        rng = np.random.RandomState(step + 42)
        batch_idx = rng.choice(len(CALIBRATION_TEXTS), min(4, len(CALIBRATION_TEXTS)), replace=False)
        total_loss = 0.0
        total_tokens = 0
        for idx in batch_idx:
            enc = tokenizer(CALIBRATION_TEXTS[idx], return_tensors="pt",
                            truncation=True, max_length=128)
            enc = {k: v.to(device) for k, v in enc.items()}
            out = model(**enc, labels=enc["input_ids"])
            if not (np.isnan(out.loss.item()) or np.isinf(out.loss.item())):
                out.loss.backward()
                total_loss += out.loss.item() * enc["input_ids"].numel()
                total_tokens += enc["input_ids"].numel()
        if total_tokens > 0:
            torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=0.5)
            optimizer.step()
            losses.append(total_loss / total_tokens)
        if (step + 1) % 25 == 0:
            log(f"      step {step+1}: loss={losses[-1]:.4f} ({time.time()-t0:.0f}s)")

    model.eval()
    ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
    facts, total = measure_facts(model, tokenizer, device)

    # Remove hooks
    for h in cont_hooks:
        h.remove()

    return {
        'label': label,
        'layers': residual_layers,
        'rank': rank,
        'n_params': n_params,
        'ppl': float(ppl),
        'facts': facts,
        'facts_total': total,
        'final_loss': float(losses[-1]) if losses else 0,
        'losses': [float(l) for l in losses],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="mps")
    p.add_argument("--rank", type=int, default=32)
    p.add_argument("--melt-steps", type=int, default=100)
    p.add_argument("--lr", type=float, default=1e-4)
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]

    # The two placement strategies
    ZONE_ALIGNED = [0, 9, 21, 26]       # s196 original
    TREE_ALIGNED = [2, 8, 21, 33]       # s197 prediction

    log(f"\n{'='*70}")
    log("  CONTINUATION PLACEMENT TEST")
    log(f"  Zone-aligned: L{ZONE_ALIGNED}")
    log(f"  Tree-aligned: L{TREE_ALIGNED}")
    log(f"{'='*70}")

    # Load model
    dtype = torch.float16
    log(f"\n  Loading {args.model}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device,
        attn_implementation="eager", trust_remote_code=True)
    model.eval()
    d_model = model.config.hidden_size
    n_layers = model.config.num_hidden_layers
    log(f"  Loaded: {n_layers}L × d={d_model}")

    # Baseline
    log("\n  Measuring baseline...")
    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    base_facts, base_total = measure_facts(model, tokenizer, args.device)
    log(f"  Baseline: PPL={base_ppl:.2f}, facts={base_facts}/{base_total}")

    results = {'baseline_ppl': base_ppl, 'baseline_facts': base_facts,
               'model': args.model, 'placements': []}

    # Free model — we reload fresh for each placement test
    del model
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    import gc; gc.collect()

    for label, placement in [("zone-aligned (s196)", ZONE_ALIGNED),
                              ("tree-aligned (s197)", TREE_ALIGNED)]:
        log(f"\n{'═'*70}")
        log(f"  TEST: {label} — L{placement}")
        log(f"{'═'*70}")

        # Reload fresh model each time
        log("  Loading fresh model...")
        model = AutoModelForCausalLM.from_pretrained(
            args.model, torch_dtype=dtype, device_map=args.device,
            attn_implementation="eager", trust_remote_code=True)
        model.eval()

        # Install sieve
        log("  Installing sieve...")
        layers = install_sieve(model, SIEVE_LAYERS, args.device)

        pre_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
        pre_facts, _ = measure_facts(model, tokenizer, args.device)
        log(f"  Pre-continuation: PPL={pre_ppl:.2f} ({pre_ppl/base_ppl:.2f}x)"
            f"  facts={pre_facts}/{base_total}")

        # Run continuation test
        result = run_continuation_test(
            model, tokenizer, layers, placement, args.rank,
            args.device, label, args.melt_steps, args.lr)

        result['pre_ppl'] = float(pre_ppl)
        result['pre_ratio'] = round(pre_ppl / base_ppl, 4)
        result['post_ratio'] = round(result['ppl'] / base_ppl, 4)
        results['placements'].append(result)

        # Free model before next round
        del model
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        gc.collect()

        log(f"\n  {label}:")
        log(f"    Pre:  PPL={pre_ppl:.2f} ({pre_ppl/base_ppl:.2f}x)")
        log(f"    Post: PPL={result['ppl']:.2f} ({result['ppl']/base_ppl:.2f}x)"
            f"  facts={result['facts']}/{base_total}")

    # Compare
    log(f"\n{'='*70}")
    log("  COMPARISON")
    log(f"{'='*70}")
    log(f"\n  {'Placement':>25}  {'Layers':>15}  {'PPL':>8}  {'Ratio':>7}  {'Facts':>6}  {'Params':>8}")
    log(f"  {'─'*25}  {'─'*15}  {'─'*8}  {'─'*7}  {'─'*6}  {'─'*8}")
    log(f"  {'Baseline':>25}  {'—':>15}  {base_ppl:>8.2f}  {'1.00x':>7}  {f'{base_facts}/{base_total}':>6}  {'—':>8}")

    for r in results['placements']:
        layers_str = ','.join(str(l) for l in r['layers'])
        log(f"  {r['label']:>25}  {layers_str:>15}  {r['ppl']:>8.2f}  "
            f"{r['post_ratio']:.2f}x  {r['facts']}/{r['facts_total']:>2}  {r['n_params']:>8,}")

    winner = min(results['placements'], key=lambda r: r['ppl'])
    log(f"\n  Winner: {winner['label']} (PPL={winner['ppl']:.2f})")

    # Save
    out_dir = _PROJECT_ROOT / "results" / "continuation-placement"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")
    with open(out_dir / f"{slug}.json", "w") as f:
        json.dump(results, f, indent=2)
    log(f"  Saved to {out_dir / slug}.json")


if __name__ == "__main__":
    main()
