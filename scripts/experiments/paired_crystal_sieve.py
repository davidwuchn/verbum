#!/usr/bin/env python3
"""Paired Crystal Sieve — does cross-matrix sign anti-correlation speed convergence?

THE HYPOTHESIS:
  The crystal sieve (session 184) pre-sets per-matrix signs → 10.7× faster.
  Session 186 discovered that the RELATIONSHIP between T_up and T_down at
  each layer determines the phase structure (computation vs lookup).
  
  If we pre-set the cross-matrix anti-correlation profile, training should
  converge even faster — because the phase structure is pre-set, not just
  the per-matrix boundary conditions.

THREE CONDITIONS:
  A. crystal:  T_up, T_down = sign(trained weights), independently  [session 184]
  B. paired:   T_up = sign(trained), T_down SHUFFLED to hit target anti-correlation
               at each layer (from the measured profile 0.53→0.38→0.45)
  C. random:   both T_up, T_down = random {-1, +1}  [baseline]

  The critical comparison is A vs B. Both have the same per-matrix sign
  distributions. They differ only in the cross-matrix correlation. If B
  converges faster than A, the inter-matrix phase structure matters.

  Wait — condition A already HAS the correct anti-correlation (it's from the
  trained model). So B would be disrupting it. Let me reframe:

REVISED THREE CONDITIONS:
  A. crystal:      T = sign(trained weights) — correct per-matrix AND cross-matrix
  B. decorrelated: T_up = sign(trained), T_down columns SHUFFLED to destroy
                   cross-matrix correlation while preserving per-matrix statistics
  C. random:       both T = random {-1, +1}

  If A >> B > C → cross-matrix correlation is load-bearing (our hypothesis)
  If A ≈ B >> C → per-matrix signs are enough, cross-matrix doesn't matter
  If A > B ≈ C → cross-matrix correlation IS the signal (per-matrix is weak alone)

Usage:
  uv run python scripts/experiments/paired_crystal_sieve.py --steps 250
  uv run python scripts/experiments/paired_crystal_sieve.py --steps 500 --all

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import math
import os
import time
import json

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


# ═══════════════════════════════════════════════════════════════════
# Crystal Sieve Linear (from crystal_sieve_prototype.py)
# ═══════════════════════════════════════════════════════════════════

class CrystalSieveLinear(nn.Module):
    """Linear with fixed ternary signs + learnable importance mask."""
    
    def __init__(self, T: torch.Tensor, scale: float, bias: torch.Tensor | None = None):
        super().__init__()
        self.register_buffer('T', T.to(torch.int8))
        self.scale = scale
        self.importance = nn.Parameter(torch.full(T.shape, 2.0, dtype=torch.float32))
        if bias is not None:
            self.bias = nn.Parameter(bias.float())
        else:
            self.bias = None
        self.out_features, self.in_features = T.shape
        
    def forward(self, x: torch.Tensor, temperature: float = 1.0) -> torch.Tensor:
        mask = torch.sigmoid(self.importance / max(temperature, 0.01))
        W_eff = self.scale * self.T.to(x.dtype) * mask.to(x.dtype)
        return F.linear(x, W_eff, self.bias)
    
    def active_fraction(self) -> float:
        return (self.importance > 0).float().mean().item()


# ═══════════════════════════════════════════════════════════════════
# Three initialization modes
# ═══════════════════════════════════════════════════════════════════

def measure_sign_agreement(T_up: torch.Tensor, T_down: torch.Tensor) -> float:
    """Fraction of dims where sign(W_up[j,k]) == sign(W_down[k,j]) averaged over neurons."""
    # T_up: (intermediate, hidden), T_down: (hidden, intermediate)
    # For neuron j: compare T_up[j, :] with T_down[:, j]
    down_cols = T_down.T  # (intermediate, hidden)
    agree = (T_up == down_cols).float().mean(dim=1)  # per-neuron agreement
    return agree.mean().item()


def decorrelate_down(T_up: torch.Tensor, T_down: torch.Tensor, seed: int = 42) -> torch.Tensor:
    """Shuffle T_down columns to destroy cross-matrix correlation while
    preserving per-column sign statistics.
    
    For each column j of T_down (= neuron j's output direction), we shuffle
    the entries. This preserves:
      - The number of +1/-1 per column (per-neuron output sign distribution)
      - The overall distribution of T_down
    It destroys:
      - The correlation between T_up[j, :] and T_down[:, j]
    """
    rng = torch.Generator().manual_seed(seed)
    T_down_shuffled = T_down.clone()
    
    # Shuffle each column independently
    for j in range(T_down_shuffled.shape[1]):
        perm = torch.randperm(T_down_shuffled.shape[0], generator=rng)
        T_down_shuffled[:, j] = T_down_shuffled[perm, j]
    
    return T_down_shuffled


def patch_model(model, mode: str = "crystal"):
    """Replace FFN linears with CrystalSieveLinear.
    
    Modes:
      crystal:      signs from trained model (correct per-matrix AND cross-matrix)
      decorrelated: T_up from trained, T_down columns shuffled (correct per-matrix,
                    destroyed cross-matrix correlation)
      random:       random ternary signs
    """
    n_patched = 0
    agreements_before = []
    agreements_after = []
    
    for layer_idx, layer in enumerate(model.gpt_neox.layers):
        mlp = layer.mlp
        
        # Get both matrices first for cross-matrix analysis
        W_up = mlp.dense_h_to_4h.weight.data.float()
        W_down = mlp.dense_4h_to_h.weight.data.float()
        
        if mode == "crystal":
            T_up = torch.sign(W_up).to(torch.int8)
            T_up[T_up == 0] = 1
            T_down = torch.sign(W_down).to(torch.int8)
            T_down[T_down == 0] = 1
            
        elif mode == "decorrelated":
            T_up = torch.sign(W_up).to(torch.int8)
            T_up[T_up == 0] = 1
            T_down_orig = torch.sign(W_down).to(torch.int8)
            T_down_orig[T_down_orig == 0] = 1
            T_down = decorrelate_down(T_up, T_down_orig, seed=42 + layer_idx).to(torch.int8)
            
        elif mode == "random":
            T_up = (torch.randint(0, 2, W_up.shape) * 2 - 1).to(torch.int8)
            T_down = (torch.randint(0, 2, W_down.shape) * 2 - 1).to(torch.int8)
            
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        # Measure agreement before/after
        agree_orig = measure_sign_agreement(
            torch.sign(W_up).to(torch.int8),
            torch.sign(W_down).to(torch.int8)
        )
        agree_now = measure_sign_agreement(T_up, T_down)
        agreements_before.append(agree_orig)
        agreements_after.append(agree_now)
        
        # Patch up projection
        scale_up = W_up.abs().mean().item()
        bias_up = mlp.dense_h_to_4h.bias.data if mlp.dense_h_to_4h.bias is not None else None
        mlp.dense_h_to_4h = CrystalSieveLinear(T_up, scale_up, bias_up)
        
        # Patch down projection
        scale_down = W_down.abs().mean().item()
        bias_down = mlp.dense_4h_to_h.bias.data if mlp.dense_4h_to_h.bias is not None else None
        mlp.dense_4h_to_h = CrystalSieveLinear(T_down, scale_down, bias_down)
        
        n_patched += 2
    
    log(f"  Patched {n_patched} linear layers ({mode} mode)")
    log(f"\n  SIGN AGREEMENT per layer (before → after patching):")
    for l, (before, after) in enumerate(zip(agreements_before, agreements_after)):
        delta = after - before
        log(f"    L{l:2d}: {before:.4f} → {after:.4f}  (Δ={delta:+.4f})")
    
    mean_before = np.mean(agreements_before)
    mean_after = np.mean(agreements_after)
    log(f"    Mean: {mean_before:.4f} → {mean_after:.4f}")
    
    return model


def freeze_except_masks(model):
    """Freeze everything except importance masks, biases, embeddings, layer norms."""
    n_trainable = 0
    n_frozen = 0
    for name, param in model.named_parameters():
        if any(k in name for k in ['importance', 'bias', 'layernorm', 'layer_norm', 'ln_', 'embed']):
            param.requires_grad = True
            n_trainable += param.numel()
        else:
            param.requires_grad = False
            n_frozen += param.numel()
    log(f"  Trainable: {n_trainable:,} | Frozen: {n_frozen:,}")
    return n_trainable, n_frozen


# ═══════════════════════════════════════════════════════════════════
# Training
# ═══════════════════════════════════════════════════════════════════

def evaluate_ppl(model, loader, device, temperature, max_batches=20):
    model.eval()
    total_loss = 0
    total_tokens = 0
    with torch.no_grad():
        for i, batch in enumerate(loader):
            if i >= max_batches:
                break
            ids = batch['input_ids'].to(device)
            
            # Set temperature on all sieve layers
            for layer in model.gpt_neox.layers:
                for name in ['dense_h_to_4h', 'dense_4h_to_h']:
                    s = getattr(layer.mlp, name)
                    if isinstance(s, CrystalSieveLinear):
                        s._cached_temp = temperature
            
            outputs = model(ids, labels=ids)
            total_loss += outputs.loss.item() * ids.shape[1]
            total_tokens += ids.shape[1]
    
    return math.exp(min(total_loss / max(total_tokens, 1), 20))


def train_sieve(model, train_loader, eval_loader, device, n_steps=250,
                lr=1e-3, temp_start=2.0, temp_end=0.1):
    """Train with temperature annealing. Returns list of (step, loss, ppl) checkpoints."""
    trainable = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=lr, weight_decay=0.01)
    
    temp_decay = (temp_end / temp_start) ** (1.0 / max(n_steps, 1))
    temperature = temp_start
    
    checkpoints = []
    step = 0
    t0 = time.time()
    
    # Initial
    ppl = evaluate_ppl(model, eval_loader, device, temperature)
    checkpoints.append({"step": 0, "ppl": round(ppl, 2), "temp": round(temperature, 3),
                       "elapsed": 0.0})
    log(f"  {'Step':>6s} {'Loss':>8s} {'PPL':>10s} {'Temp':>6s} {'Time':>6s}")
    log(f"  {0:6d} {'─':>8s} {ppl:10.1f} {temperature:6.2f} {0:6.1f}s")
    
    model.train()
    
    while step < n_steps:
        for batch in train_loader:
            if step >= n_steps:
                break
            
            ids = batch['input_ids'].to(device)
            
            # Patch temperature into forward
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
            
            # Restore
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
            
            if step % 25 == 0 or step == 1:
                ppl = evaluate_ppl(model, eval_loader, device, temperature)
                elapsed = time.time() - t0
                log(f"  {step:6d} {loss.item():8.4f} {ppl:10.1f} {temperature:6.2f} {elapsed:6.1f}s")
                checkpoints.append({"step": step, "ppl": round(ppl, 2),
                                   "loss": round(loss.item(), 4),
                                   "temp": round(temperature, 3),
                                   "elapsed": round(elapsed, 1)})
    
    # Final
    ppl = evaluate_ppl(model, eval_loader, device, temperature)
    elapsed = time.time() - t0
    log(f"  {step:6d} {'FINAL':>8s} {ppl:10.1f} {temperature:6.2f} {elapsed:6.1f}s")
    checkpoints.append({"step": step, "ppl": round(ppl, 2), "temp": round(temperature, 3),
                       "elapsed": round(elapsed, 1), "final": True})
    
    return checkpoints


# ═══════════════════════════════════════════════════════════════════
# Data
# ═══════════════════════════════════════════════════════════════════

def prepare_data(tokenizer, seq_len=256, batch_size=4):
    from datasets import load_dataset
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1")
    
    def tokenize(split):
        texts = [t for t in dataset[split]["text"] if len(t.strip()) > 50]
        all_ids = []
        for text in texts:
            all_ids.extend(tokenizer.encode(text, add_special_tokens=False))
        chunks = []
        for i in range(0, len(all_ids) - seq_len, seq_len):
            chunks.append({'input_ids': torch.tensor(all_ids[i:i+seq_len], dtype=torch.long)})
        return chunks
    
    train = tokenize("train")
    val = tokenize("validation")
    log(f"  Train: {len(train)} seqs | Val: {len(val)} seqs")
    return DataLoader(train, batch_size=batch_size, shuffle=True), \
           DataLoader(val, batch_size=batch_size, shuffle=False)


# ═══════════════════════════════════════════════════════════════════
# Run one condition
# ═══════════════════════════════════════════════════════════════════

def run_condition(mode: str, n_steps: int, device, tokenizer, train_loader, eval_loader):
    """Run one experimental condition. Returns checkpoint list."""
    from transformers import AutoModelForCausalLM
    
    log(f"\n{'═' * 72}")
    log(f"CONDITION: {mode.upper()}")
    log(f"{'═' * 72}")
    
    model = AutoModelForCausalLM.from_pretrained(
        "EleutherAI/pythia-160m-deduped", torch_dtype=torch.float32,
        low_cpu_mem_usage=True)
    
    # Baseline (only for first condition)
    model.to(device)
    model.eval()
    baseline_ppl = evaluate_ppl(model, eval_loader, device, temperature=1.0, max_batches=50)
    log(f"  Float baseline PPL: {baseline_ppl:.2f}")
    
    # Patch
    model = model.cpu()
    model = patch_model(model, mode=mode)
    freeze_except_masks(model)
    model.to(device)
    
    # Initial PPL
    init_ppl = evaluate_ppl(model, eval_loader, device, temperature=2.0, max_batches=50)
    log(f"  Initial sieve PPL:  {init_ppl:.2f}")
    
    # Train
    log(f"\n  Training ({n_steps} steps)...")
    checkpoints = train_sieve(model, train_loader, eval_loader, device, n_steps=n_steps)
    
    final_ppl = checkpoints[-1]["ppl"]
    log(f"\n  RESULT: {mode} — init={init_ppl:.1f} → final={final_ppl:.1f} (baseline={baseline_ppl:.1f})")
    
    # Cleanup
    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    
    return {
        "mode": mode,
        "baseline_ppl": round(baseline_ppl, 2),
        "init_ppl": round(init_ppl, 2),
        "final_ppl": final_ppl,
        "checkpoints": checkpoints,
    }


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Paired Crystal Sieve Experiment")
    parser.add_argument("--steps", type=int, default=250)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--all", action="store_true",
                       help="Run all 3 conditions (default: crystal + decorrelated only)")
    parser.add_argument("--mode", type=str, default=None,
                       help="Run single mode: crystal, decorrelated, or random")
    args = parser.parse_args()
    
    log("=" * 72)
    log("PAIRED CRYSTAL SIEVE — CROSS-MATRIX ANTI-CORRELATION TEST")
    log("=" * 72)
    
    if args.device == "auto":
        device = torch.device("mps" if torch.backends.mps.is_available()
                              else "cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    log(f"Device: {device}")
    log(f"Steps: {args.steps}")
    
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m-deduped")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    log("\nPreparing data...")
    train_loader, eval_loader = prepare_data(tokenizer)
    
    # Determine which conditions to run
    if args.mode:
        modes = [args.mode]
    elif args.all:
        modes = ["crystal", "decorrelated", "random"]
    else:
        modes = ["crystal", "decorrelated"]
    
    # Run conditions
    all_results = {}
    for mode in modes:
        result = run_condition(mode, args.steps, device, tokenizer, train_loader, eval_loader)
        all_results[mode] = result
    
    # ── Comparison ──────────────────────────────────────────────
    log(f"\n\n{'═' * 72}")
    log("COMPARISON")
    log(f"{'═' * 72}")
    
    log(f"\n  {'Mode':>14s}  {'Init PPL':>10s}  {'Final PPL':>10s}  {'Baseline':>10s}  {'Recovery':>10s}")
    log(f"  {'─'*14}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*10}")
    
    for mode, r in all_results.items():
        recovery = r['baseline_ppl'] / r['final_ppl'] * 100 if r['final_ppl'] > 0 else 0
        log(f"  {mode:>14s}  {r['init_ppl']:10.1f}  {r['final_ppl']:10.1f}  "
            f"{r['baseline_ppl']:10.1f}  {recovery:9.1f}%")
    
    # The key comparison
    if "crystal" in all_results and "decorrelated" in all_results:
        c = all_results["crystal"]["final_ppl"]
        d = all_results["decorrelated"]["final_ppl"]
        log(f"\n  KEY COMPARISON: crystal={c:.1f} vs decorrelated={d:.1f}")
        
        if c < d * 0.95:
            log(f"  ✅ CROSS-MATRIX CORRELATION IS LOAD-BEARING")
            log(f"     Crystal (with natural anti-correlation) beats decorrelated by {(d/c - 1)*100:.1f}%")
            log(f"     The phase structure in the signs matters beyond per-matrix statistics.")
        elif d < c * 0.95:
            log(f"  ❌ DECORRELATION HELPS (unexpected)")
            log(f"     Decorrelated beats crystal — the natural correlation may be a local minimum.")
        else:
            log(f"  🔶 NO SIGNIFICANT DIFFERENCE")
            log(f"     Per-matrix signs are sufficient. Cross-matrix correlation is cosmetic.")
    
    if "random" in all_results and "crystal" in all_results:
        c = all_results["crystal"]["final_ppl"]
        r = all_results["random"]["final_ppl"]
        log(f"\n  CRYSTAL vs RANDOM: crystal={c:.1f} vs random={r:.1f}")
        log(f"  Crystal advantage: {r/c:.1f}×")
    
    # ── Save ────────────────────────────────────────────────────
    results_dir = os.path.join(os.path.dirname(__file__), "..", "..",
                              "results", "paired-crystal-sieve")
    os.makedirs(results_dir, exist_ok=True)
    
    summary_path = os.path.join(results_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(all_results, f, indent=2)
    log(f"\n  Results saved to {summary_path}")
    
    log(f"\n{'═' * 72}")
    log("DONE")
    log(f"{'═' * 72}")


if __name__ == "__main__":
    main()
