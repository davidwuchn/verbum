#!/usr/bin/env python3
"""Synthetic Crystal Sieve — construct the crystal from equations, not extraction.

THE QUESTION: Can we BUILD the crystal from the anti-correlation profile
alone, without ever looking at a trained model's weights?

Session 186 showed:
  - Crystal (extracted signs) → PPL 511.6
  - Decorrelated (same per-matrix stats, no cross-matrix correlation) → PPL 1817
  - Random → PPL 1952
  - The cross-matrix anti-correlation IS the signal

If the anti-correlation depth profile is all that matters, we can:
  1. Define the target profile: agree(l) for each layer l
  2. Generate random T_up ∈ {-1, +1}
  3. Construct T_down by flipping (1 - agree(l)) fraction of T_up entries
  4. This gives synthetic sign pairs with the correct anti-correlation
  5. No reference model needed

FOUR CONDITIONS:
  A. crystal:    T from trained Pythia-160M (the reference, PPL ~511)
  B. synthetic:  T_up random, T_down constructed to match extracted profile
  C. synthetic-universal: T_down constructed from a SMOOTHED universal curve
                          (not the exact per-layer values — tests generalization)
  D. random:     both random (baseline, PPL ~1952)

THE KEY PREDICTIONS:
  - If B ≈ A → the crystal IS the anti-correlation profile (huge: no ref model needed)
  - If B >> D but B < A → profile captures most of the signal but per-neuron details matter
  - If B ≈ D → the profile is not enough (per-neuron sign patterns are essential)

Usage:
  uv run python scripts/experiments/synthetic_crystal_sieve.py --steps 250 --all

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import time

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


# ═══════════════════════════════════════════════════════════════════
# Target anti-correlation profiles
# ═══════════════════════════════════════════════════════════════════

# Measured from Pythia-160M-deduped (session 186, crystal_circuit_types.py)
PYTHIA_160M_PROFILE = [
    0.5292,  # L0  — correlated (EXPAND)
    0.4470,  # L1
    0.3990,  # L2
    0.3755,  # L3  — anti-correlated peak (ORTHO)
    0.3850,  # L4
    0.3877,  # L5
    0.4142,  # L6
    0.4143,  # L7
    0.4480,  # L8  — recovering (transition to ALIGN)
    0.4499,  # L9
    0.4474,  # L10
    0.4398,  # L11 — still anti-correlated (COLLAPSE)
]

def universal_profile(n_layers: int) -> list[float]:
    """Generate a smoothed universal anti-correlation profile for any depth.
    
    The shape: starts correlated (~0.53), dips to anti-correlated (~0.38)
    at about 1/3 depth, recovers to ~0.45 by 2/3 depth, stays there.
    
    This is a parameterized curve, not fit to any specific model.
    Uses the standing-wave insight: the profile is a half-cosine with
    a DC offset, peak anti-correlation at ~layer n/3.
    """
    profile = []
    for l in range(n_layers):
        t = l / max(n_layers - 1, 1)  # 0 to 1
        
        # Parameterized curve:
        # - Start at 0.53 (slightly correlated)
        # - Dip to 0.38 at t ≈ 0.3 (ORTHO)
        # - Recover to 0.45 by t ≈ 0.7 (ALIGN)
        # - Stay at 0.44 through end (COLLAPSE)
        
        # Half-cosine dip centered at t=0.3, width ~0.5
        dip = 0.075 * math.cos(math.pi * (t - 0.3) / 0.5) if 0.05 < t < 0.55 else 0
        base = 0.45 + 0.08 * math.exp(-5 * t)  # starts at 0.53, decays to 0.45
        
        agree = base - max(dip, 0)
        agree = max(0.35, min(0.55, agree))  # clamp
        profile.append(agree)
    
    return profile


# ═══════════════════════════════════════════════════════════════════
# Sieve Linear (same as paired_crystal_sieve.py)
# ═══════════════════════════════════════════════════════════════════

class CrystalSieveLinear(nn.Module):
    def __init__(self, T: torch.Tensor, scale: float, bias: torch.Tensor | None = None):
        super().__init__()
        self.register_buffer('T', T.to(torch.int8))
        self.scale = scale
        self.importance = nn.Parameter(torch.full(T.shape, 2.0, dtype=torch.float32))
        self.bias = nn.Parameter(bias.float()) if bias is not None else None
        self.out_features, self.in_features = T.shape

    def forward(self, x: torch.Tensor, temperature: float = 1.0) -> torch.Tensor:
        mask = torch.sigmoid(self.importance / max(temperature, 0.01))
        W_eff = self.scale * self.T.to(x.dtype) * mask.to(x.dtype)
        return F.linear(x, W_eff, self.bias)

    def active_fraction(self) -> float:
        return (self.importance > 0).float().mean().item()


# ═══════════════════════════════════════════════════════════════════
# Synthetic sign construction
# ═══════════════════════════════════════════════════════════════════

def construct_synthetic_signs(
    shape_up: tuple[int, int],
    shape_down: tuple[int, int],
    target_agreement: float,
    seed: int = 0,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Construct T_up and T_down with a target sign agreement rate.
    
    Algorithm:
      1. Generate random T_up ∈ {-1, +1}
      2. For each neuron j:
         - Start with T_down[:, j] = T_up[j, :] (100% agreement)
         - Flip (1 - target_agreement) fraction of entries
         - This gives exactly target_agreement agreement
    
    Returns T_up (out, in), T_down (in, out) — standard weight shapes.
    """
    rng = torch.Generator().manual_seed(seed)
    
    out_features, in_features = shape_up  # (intermediate, hidden)
    
    # Random T_up
    T_up = (torch.randint(0, 2, shape_up, generator=rng) * 2 - 1).to(torch.int8)
    
    # Construct T_down column by column
    # T_down shape is (hidden, intermediate) — column j corresponds to neuron j
    T_down = torch.zeros(shape_down, dtype=torch.int8)
    
    n_flip = int((1.0 - target_agreement) * in_features)
    
    for j in range(out_features):
        # Start with copy of T_up[j, :] as T_down[:, j]
        T_down[:, j] = T_up[j, :]
        
        # Flip n_flip random positions
        if n_flip > 0:
            flip_idx = torch.randperm(in_features, generator=rng)[:n_flip]
            T_down[flip_idx, j] *= -1
    
    return T_up, T_down


def measure_agreement(T_up: torch.Tensor, T_down: torch.Tensor) -> float:
    """Mean per-neuron sign agreement between T_up rows and T_down columns."""
    down_cols = T_down.T  # (intermediate, hidden)
    return (T_up == down_cols).float().mean(dim=1).mean().item()


# ═══════════════════════════════════════════════════════════════════
# Model patching
# ═══════════════════════════════════════════════════════════════════

def patch_model(model, mode: str, profile: list[float] | None = None):
    """Patch FFN with sieve layers.
    
    Modes:
      crystal:             signs from trained model
      synthetic:           random T_up, T_down constructed to match EXTRACTED profile
      synthetic-universal: random T_up, T_down constructed to match SMOOTHED universal curve
      random:              random signs
    """
    agreements = []
    
    for layer_idx, layer in enumerate(model.gpt_neox.layers):
        mlp = layer.mlp
        W_up = mlp.dense_h_to_4h.weight.data.float()
        W_down = mlp.dense_4h_to_h.weight.data.float()
        
        if mode == "crystal":
            T_up = torch.sign(W_up).to(torch.int8)
            T_up[T_up == 0] = 1
            T_down = torch.sign(W_down).to(torch.int8)
            T_down[T_down == 0] = 1
            
        elif mode in ("synthetic", "synthetic-universal"):
            if profile is None:
                raise ValueError(f"profile required for {mode}")
            target = profile[layer_idx]
            T_up, T_down = construct_synthetic_signs(
                W_up.shape, W_down.shape, target, seed=1000 + layer_idx)
            
        elif mode == "random":
            T_up = (torch.randint(0, 2, W_up.shape) * 2 - 1).to(torch.int8)
            T_down = (torch.randint(0, 2, W_down.shape) * 2 - 1).to(torch.int8)
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        agree = measure_agreement(T_up, T_down)
        agreements.append(agree)
        
        # Use same scale as crystal (from trained weights) for fair comparison
        scale_up = W_up.abs().mean().item()
        scale_down = W_down.abs().mean().item()
        bias_up = mlp.dense_h_to_4h.bias.data if mlp.dense_h_to_4h.bias is not None else None
        bias_down = mlp.dense_4h_to_h.bias.data if mlp.dense_4h_to_h.bias is not None else None
        
        mlp.dense_h_to_4h = CrystalSieveLinear(T_up, scale_up, bias_up)
        mlp.dense_4h_to_h = CrystalSieveLinear(T_down, scale_down, bias_down)
    
    log(f"  Patched 24 layers ({mode})")
    log(f"  Sign agreement profile:")
    for l, a in enumerate(agreements):
        target = profile[l] if profile and mode != "crystal" and mode != "random" else "—"
        tgt_str = f"(target={target:.4f})" if isinstance(target, float) else ""
        log(f"    L{l:2d}: {a:.4f}  {tgt_str}")
    log(f"  Mean agreement: {np.mean(agreements):.4f}")
    
    return model, agreements


def freeze_except_masks(model):
    n_train = 0
    n_frozen = 0
    for name, param in model.named_parameters():
        if any(k in name for k in ['importance', 'bias', 'layernorm', 'layer_norm', 'ln_', 'embed']):
            param.requires_grad = True
            n_train += param.numel()
        else:
            param.requires_grad = False
            n_frozen += param.numel()
    log(f"  Trainable: {n_train:,} | Frozen: {n_frozen:,}")


# ═══════════════════════════════════════════════════════════════════
# Training (same as paired_crystal_sieve.py)
# ═══════════════════════════════════════════════════════════════════

def evaluate_ppl(model, loader, device, temperature, max_batches=20):
    model.eval()
    total_loss = total_tokens = 0
    with torch.no_grad():
        for i, batch in enumerate(loader):
            if i >= max_batches:
                break
            ids = batch['input_ids'].to(device)
            outputs = model(ids, labels=ids)
            total_loss += outputs.loss.item() * ids.shape[1]
            total_tokens += ids.shape[1]
    return math.exp(min(total_loss / max(total_tokens, 1), 20))


def train_sieve(model, train_loader, eval_loader, device, n_steps=250,
                lr=1e-3, temp_start=2.0, temp_end=0.1):
    trainable = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=lr, weight_decay=0.01)
    temp_decay = (temp_end / temp_start) ** (1.0 / max(n_steps, 1))
    temperature = temp_start
    
    checkpoints = []
    step = 0
    t0 = time.time()
    
    ppl = evaluate_ppl(model, eval_loader, device, temperature)
    checkpoints.append({"step": 0, "ppl": round(ppl, 2)})
    log(f"  {'Step':>6s} {'Loss':>8s} {'PPL':>10s} {'Temp':>6s} {'Time':>6s}")
    log(f"  {0:6d} {'—':>8s} {ppl:10.1f} {temperature:6.2f} {0:6.1f}s")
    
    model.train()
    while step < n_steps:
        for batch in train_loader:
            if step >= n_steps:
                break
            ids = batch['input_ids'].to(device)
            
            originals = {}
            for layer in model.gpt_neox.layers:
                for name in ['dense_h_to_4h', 'dense_4h_to_h']:
                    s = getattr(layer.mlp, name)
                    if isinstance(s, CrystalSieveLinear):
                        orig = s.forward
                        t = temperature
                        def make_fwd(sieve, temp):
                            def fwd(x):
                                return CrystalSieveLinear.forward(sieve, x, temperature=temp)
                            return fwd
                        s.forward = make_fwd(s, t)
                        originals[(id(layer), name)] = orig
            
            outputs = model(ids, labels=ids)
            loss = outputs.loss
            
            for layer in model.gpt_neox.layers:
                for name in ['dense_h_to_4h', 'dense_4h_to_h']:
                    key = (id(layer), name)
                    if key in originals:
                        getattr(layer.mlp, name).forward = originals[key]
            
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable, 1.0)
            optimizer.step()
            temperature *= temp_decay
            step += 1
            
            if step % 50 == 0 or step == 1:
                ppl = evaluate_ppl(model, eval_loader, device, temperature)
                elapsed = time.time() - t0
                log(f"  {step:6d} {loss.item():8.4f} {ppl:10.1f} {temperature:6.2f} {elapsed:6.1f}s")
                checkpoints.append({"step": step, "ppl": round(ppl, 2),
                                   "loss": round(loss.item(), 4),
                                   "elapsed": round(elapsed, 1)})
    
    ppl = evaluate_ppl(model, eval_loader, device, temperature)
    elapsed = time.time() - t0
    log(f"  {step:6d} {'FINAL':>8s} {ppl:10.1f} {temperature:6.2f} {elapsed:6.1f}s")
    checkpoints.append({"step": step, "ppl": round(ppl, 2), "elapsed": round(elapsed, 1), "final": True})
    return checkpoints


def prepare_data(tokenizer, seq_len=256, batch_size=4):
    from datasets import load_dataset
    ds = load_dataset("wikitext", "wikitext-2-raw-v1")
    def tok(split):
        texts = [t for t in ds[split]["text"] if len(t.strip()) > 50]
        ids = []
        for t in texts:
            ids.extend(tokenizer.encode(t, add_special_tokens=False))
        return DataLoader(
            [{'input_ids': torch.tensor(ids[i:i+seq_len], dtype=torch.long)}
             for i in range(0, len(ids) - seq_len, seq_len)],
            batch_size=batch_size, shuffle=(split == "train"))
    train = tok("train")
    val = tok("validation")
    log(f"  Train: {len(train.dataset)} seqs | Val: {len(val.dataset)} seqs")
    return train, val


# ═══════════════════════════════════════════════════════════════════
# Run
# ═══════════════════════════════════════════════════════════════════

def run_condition(mode, n_steps, device, tokenizer, train_loader, eval_loader, profile=None):
    from transformers import AutoModelForCausalLM
    
    log(f"\n{'═' * 72}")
    log(f"CONDITION: {mode.upper()}")
    log(f"{'═' * 72}")
    
    model = AutoModelForCausalLM.from_pretrained(
        "EleutherAI/pythia-160m-deduped", torch_dtype=torch.float32,
        low_cpu_mem_usage=True)
    model.to(device)
    model.eval()
    baseline = evaluate_ppl(model, eval_loader, device, 1.0, max_batches=50)
    log(f"  Float baseline: {baseline:.2f}")
    
    model = model.cpu()
    model, agreements = patch_model(model, mode, profile)
    freeze_except_masks(model)
    model.to(device)
    
    init_ppl = evaluate_ppl(model, eval_loader, device, 2.0, max_batches=50)
    log(f"  Init PPL: {init_ppl:.1f}")
    
    log(f"\n  Training ({n_steps} steps)...")
    checkpoints = train_sieve(model, train_loader, eval_loader, device, n_steps)
    final_ppl = checkpoints[-1]["ppl"]
    
    log(f"\n  {mode}: init={init_ppl:.1f} → final={final_ppl:.1f} (baseline={baseline:.1f})")
    
    del model; gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    
    return {"mode": mode, "baseline": round(baseline, 2), "init_ppl": round(init_ppl, 2),
            "final_ppl": final_ppl, "agreements": agreements, "checkpoints": checkpoints}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=250)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--all", action="store_true", help="All 4 conditions")
    parser.add_argument("--mode", type=str, default=None)
    args = parser.parse_args()
    
    log("=" * 72)
    log("SYNTHETIC CRYSTAL SIEVE — CONSTRUCT FROM EQUATIONS")
    log("=" * 72)
    
    device = torch.device("mps" if args.device == "auto" and torch.backends.mps.is_available()
                          else "cuda" if args.device == "auto" and torch.cuda.is_available()
                          else "cpu" if args.device == "auto" else args.device)
    log(f"Device: {device}")
    
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m-deduped")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    log("\nPreparing data...")
    train_loader, eval_loader = prepare_data(tokenizer)
    
    # Profiles
    extracted_profile = PYTHIA_160M_PROFILE
    universal = universal_profile(12)
    
    log(f"\n  Extracted profile: {[f'{x:.3f}' for x in extracted_profile]}")
    log(f"  Universal profile: {[f'{x:.3f}' for x in universal]}")
    
    if args.mode:
        modes = [args.mode]
    elif args.all:
        modes = ["crystal", "synthetic", "synthetic-universal", "random"]
    else:
        modes = ["crystal", "synthetic", "synthetic-universal"]
    
    results = {}
    for mode in modes:
        profile = extracted_profile if mode == "synthetic" else \
                  universal if mode == "synthetic-universal" else None
        results[mode] = run_condition(mode, args.steps, device, tokenizer,
                                     train_loader, eval_loader, profile)
    
    # ── Comparison ──────────────────────────────────────────────
    log(f"\n\n{'═' * 72}")
    log("COMPARISON")
    log(f"{'═' * 72}")
    log(f"\n  {'Mode':>22s}  {'Init PPL':>10s}  {'Final PPL':>10s}  {'vs Crystal':>10s}  {'vs Random':>10s}")
    log(f"  {'─'*22}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*10}")
    
    crystal_ppl = results.get("crystal", {}).get("final_ppl", None)
    random_ppl = results.get("random", {}).get("final_ppl", None)
    
    for mode, r in results.items():
        vs_c = f"{r['final_ppl']/crystal_ppl:.2f}×" if crystal_ppl else "—"
        vs_r = f"{random_ppl/r['final_ppl']:.2f}×" if random_ppl else "—"
        log(f"  {mode:>22s}  {r['init_ppl']:10.1f}  {r['final_ppl']:10.1f}  {vs_c:>10s}  {vs_r:>10s}")
    
    # Verdict
    if "synthetic" in results and "crystal" in results:
        s = results["synthetic"]["final_ppl"]
        c = results["crystal"]["final_ppl"]
        ratio = s / c
        log(f"\n  SYNTHETIC vs CRYSTAL: {s:.1f} vs {c:.1f} (ratio={ratio:.2f})")
        if ratio < 1.2:
            log(f"  ✅ SYNTHETIC ≈ CRYSTAL — the anti-correlation profile IS the crystal")
            log(f"     No reference model needed. Construct from equations.")
        elif ratio < 2.0:
            log(f"  🔶 SYNTHETIC captures most of the crystal signal ({1/ratio:.0%})")
            log(f"     Profile is the dominant factor but per-neuron details add value.")
        else:
            log(f"  ❌ SYNTHETIC << CRYSTAL — per-neuron sign patterns matter")
            log(f"     The profile is necessary but not sufficient.")
    
    if "synthetic-universal" in results and "synthetic" in results:
        su = results["synthetic-universal"]["final_ppl"]
        s = results["synthetic"]["final_ppl"]
        log(f"\n  UNIVERSAL vs EXTRACTED PROFILE: {su:.1f} vs {s:.1f}")
        if su / s < 1.3:
            log(f"  ✅ Universal curve works — don't need exact per-layer measurements")
        else:
            log(f"  🔶 Exact profile matters — universal curve is a rougher approximation")
    
    # Save
    results_dir = os.path.join(os.path.dirname(__file__), "..", "..",
                              "results", "synthetic-crystal-sieve")
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, "summary.json"), "w") as f:
        json.dump(results, f, indent=2)
    log(f"\n  Results saved to results/synthetic-crystal-sieve/summary.json")
    
    log(f"\n{'═' * 72}")
    log("DONE")
    log(f"{'═' * 72}")


if __name__ == "__main__":
    main()
