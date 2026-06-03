#!/usr/bin/env python3
"""Crystal Sieve Prototype — train binary masks on crystal-fixed ternary signs.

THE CONCEPT:
  Sieve (fixed):   signs from crystal equation, scale from crystal
  Sediment (trained): binary mask — which weights are active

COMPARISON:
  A. Crystal init: signs from trained Pythia-160M (= crystal attractor)
  B. Random init:  random ternary signs
  Both train ONLY the importance masks + embeddings + layer norms.

If A converges faster/better than B → the crystal sieve works.

Architecture: Pythia-160M (12 layers, 768 hidden, 3072 intermediate, GPT-NeoX)
FFN: Linear(768→3072) → GELU → Linear(3072→768)  (not gated)
Training: WikiText-2, ~250 steps, measure perplexity.

Usage:
  uv run python scripts/experiments/crystal_sieve_prototype.py
  uv run python scripts/experiments/crystal_sieve_prototype.py --steps 500
  uv run python scripts/experiments/crystal_sieve_prototype.py --mode random  # random ternary baseline

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import math
import os
import time

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


# ═══════════════════════════════════════════════════════════════════
# Crystal Sieve Linear — the core building block
# ═══════════════════════════════════════════════════════════════════

class CrystalSieveLinear(nn.Module):
    """Linear layer with fixed ternary signs + learnable importance mask.
    
    During training: W_eff = scale * T * sigmoid(importance / τ)
    After training:  W_eff = scale * T * (importance > 0).float()
    
    The signs T are FROZEN (the crystal sieve).
    The importance scores are TRAINED (the sediment).
    """
    
    def __init__(self, T: torch.Tensor, scale: float, bias: torch.Tensor | None = None):
        super().__init__()
        self.register_buffer('T', T.to(torch.int8))  # {-1, +1} signs
        self.scale = scale
        
        # Learnable importance mask (continuous during training)
        # Initialize at +2.0 so sigmoid(2.0) ≈ 0.88 — mostly ON initially
        self.importance = nn.Parameter(torch.full(T.shape, 2.0, dtype=torch.float32))
        
        if bias is not None:
            self.bias = nn.Parameter(bias.float())
        else:
            self.bias = None
            
        self.out_features, self.in_features = T.shape
        
    def forward(self, x: torch.Tensor, temperature: float = 1.0) -> torch.Tensor:
        # Soft binary mask
        mask = torch.sigmoid(self.importance / max(temperature, 0.01))
        
        # Effective weight: scale * sign * mask
        W_eff = self.scale * self.T.to(x.dtype) * mask.to(x.dtype)
        
        out = F.linear(x, W_eff, self.bias)
        return out
    
    def active_fraction(self) -> float:
        """Fraction of weights currently active (importance > 0)."""
        return (self.importance > 0).float().mean().item()
    
    def extra_repr(self) -> str:
        return (f"in={self.in_features}, out={self.out_features}, "
                f"scale={self.scale:.4f}, active={self.active_fraction():.1%}")


# ═══════════════════════════════════════════════════════════════════
# Model surgery — replace FFN linears with crystal sieve versions
# ═══════════════════════════════════════════════════════════════════

def extract_crystal_and_patch(model, mode: str = "crystal"):
    """Replace all FFN Linear layers with CrystalSieveLinear.
    
    mode="crystal": signs from trained model (the crystal attractor)
    mode="random":  random ternary signs (baseline)
    """
    n_patched = 0
    
    for layer_idx, layer in enumerate(model.gpt_neox.layers):
        mlp = layer.mlp
        
        for name in ['dense_h_to_4h', 'dense_4h_to_h']:
            linear = getattr(mlp, name)
            W = linear.weight.data.float()
            
            if mode == "crystal":
                # Crystal signs = sign of trained weights (the attractor)
                T = torch.sign(W).to(torch.int8)
                # Ensure no zeros in signs (sign(0) = 0, replace with +1)
                T[T == 0] = 1
            elif mode == "random":
                # Random ternary: {-1, +1} uniformly
                T = torch.randint(0, 2, W.shape, dtype=torch.int8) * 2 - 1
            else:
                raise ValueError(f"Unknown mode: {mode}")
            
            # Crystal scale: ||W||_F / sqrt(m * n * (1 - zero_rate))
            # For initial prototype, use simple mean absolute value
            scale = W.abs().mean().item()
            
            bias = linear.bias.data if linear.bias is not None else None
            
            sieve_linear = CrystalSieveLinear(T, scale, bias)
            setattr(mlp, name, sieve_linear)
            n_patched += 1
    
    log(f"  Patched {n_patched} linear layers ({mode} mode)")
    return model


def freeze_except_masks(model):
    """Freeze everything except importance masks, biases, embeddings, and layer norms."""
    n_frozen = 0
    n_trainable = 0
    
    for name, param in model.named_parameters():
        if 'importance' in name:
            param.requires_grad = True
            n_trainable += param.numel()
        elif 'bias' in name:
            param.requires_grad = True
            n_trainable += param.numel()
        elif 'layernorm' in name or 'layer_norm' in name or 'ln_' in name:
            param.requires_grad = True
            n_trainable += param.numel()
        elif 'embed' in name:
            param.requires_grad = True
            n_trainable += param.numel()
        else:
            param.requires_grad = False
            n_frozen += param.numel()
    
    log(f"  Trainable: {n_trainable:,} params")
    log(f"  Frozen:    {n_frozen:,} params")
    return n_trainable, n_frozen


# ═══════════════════════════════════════════════════════════════════
# Training loop
# ═══════════════════════════════════════════════════════════════════

def evaluate_perplexity(model, eval_dataloader, device, temperature, max_batches=20):
    """Quick perplexity evaluation."""
    model.eval()
    total_loss = 0
    total_tokens = 0
    
    with torch.no_grad():
        for i, batch in enumerate(eval_dataloader):
            if i >= max_batches:
                break
            input_ids = batch['input_ids'].to(device)
            
            # Set temperature for all sieve layers
            for layer in model.gpt_neox.layers:
                for name in ['dense_h_to_4h', 'dense_4h_to_h']:
                    sieve = getattr(layer.mlp, name)
                    if hasattr(sieve, 'importance'):
                        sieve._temp = temperature
            
            outputs = model(input_ids, labels=input_ids)
            total_loss += outputs.loss.item() * input_ids.shape[1]
            total_tokens += input_ids.shape[1]
    
    avg_loss = total_loss / max(total_tokens, 1)
    return math.exp(min(avg_loss, 20))  # cap at exp(20) to avoid overflow


def train(model, train_dataloader, eval_dataloader, device,
          n_steps: int = 250, lr: float = 1e-3, weight_decay: float = 0.01,
          temp_start: float = 2.0, temp_end: float = 0.1):
    """Train importance masks with temperature annealing."""
    
    # Only optimize trainable params
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=lr, weight_decay=weight_decay)
    
    # Temperature schedule: exponential decay
    temp_decay = (temp_end / temp_start) ** (1.0 / max(n_steps, 1))
    temperature = temp_start
    
    model.train()
    step = 0
    epoch = 0
    
    log(f"\n  {'Step':>6s} {'Loss':>8s} {'PPL':>8s} {'Temp':>6s} {'Active':>8s} {'Time':>6s}")
    log(f"  {'─'*6} {'─'*8} {'─'*8} {'─'*6} {'─'*8} {'─'*6}")
    
    t0 = time.time()
    
    # Evaluate at start
    ppl = evaluate_perplexity(model, eval_dataloader, device, temperature)
    active = sum(getattr(layer.mlp, 'dense_h_to_4h').active_fraction() 
                 for layer in model.gpt_neox.layers) / len(model.gpt_neox.layers)
    log(f"  {0:6d} {'─':>8s} {ppl:8.1f} {temperature:6.2f} {active:8.1%} {0:6.1f}s")
    
    while step < n_steps:
        epoch += 1
        for batch in train_dataloader:
            if step >= n_steps:
                break
                
            input_ids = batch['input_ids'].to(device)
            
            # Monkey-patch temperature into sieve layers
            for layer in model.gpt_neox.layers:
                for name in ['dense_h_to_4h', 'dense_4h_to_h']:
                    sieve = getattr(layer.mlp, name)
                    if hasattr(sieve, 'importance'):
                        # Store temp for forward hook
                        pass
            
            # Forward pass — need to handle temperature
            # Override forward of each CrystalSieveLinear
            original_forwards = {}
            for layer in model.gpt_neox.layers:
                for name in ['dense_h_to_4h', 'dense_4h_to_h']:
                    sieve = getattr(layer.mlp, name)
                    if isinstance(sieve, CrystalSieveLinear):
                        orig_forward = sieve.forward
                        temp_val = temperature
                        def make_forward(s, t):
                            def new_forward(x):
                                return CrystalSieveLinear.forward(s, x, temperature=t)
                            return new_forward
                        sieve.forward = make_forward(sieve, temp_val)
                        original_forwards[(id(layer), name)] = orig_forward
            
            outputs = model(input_ids, labels=input_ids)
            loss = outputs.loss
            
            # Restore forwards
            for layer in model.gpt_neox.layers:
                for name in ['dense_h_to_4h', 'dense_4h_to_h']:
                    key = (id(layer), name)
                    if key in original_forwards:
                        sieve = getattr(layer.mlp, name)
                        sieve.forward = original_forwards[key]
            
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
            optimizer.step()
            
            temperature *= temp_decay
            step += 1
            
            if step % 25 == 0 or step == 1:
                model.eval()
                ppl = evaluate_perplexity(model, eval_dataloader, device, temperature)
                active = sum(getattr(layer.mlp, 'dense_h_to_4h').active_fraction() 
                             for layer in model.gpt_neox.layers) / len(model.gpt_neox.layers)
                elapsed = time.time() - t0
                log(f"  {step:6d} {loss.item():8.4f} {ppl:8.1f} {temperature:6.2f} {active:8.1%} {elapsed:6.1f}s")
                model.train()
    
    # Final eval
    model.eval()
    ppl = evaluate_perplexity(model, eval_dataloader, device, temperature)
    active = sum(getattr(layer.mlp, 'dense_h_to_4h').active_fraction() 
                 for layer in model.gpt_neox.layers) / len(model.gpt_neox.layers)
    elapsed = time.time() - t0
    log(f"  {step:6d} {'FINAL':>8s} {ppl:8.1f} {temperature:6.2f} {active:8.1%} {elapsed:6.1f}s")
    
    return ppl


# ═══════════════════════════════════════════════════════════════════
# Data preparation
# ═══════════════════════════════════════════════════════════════════

def prepare_data(tokenizer, seq_len: int = 256, batch_size: int = 4):
    """Prepare WikiText-2 for training."""
    from datasets import load_dataset
    
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1")
    
    def tokenize_and_chunk(split):
        texts = [t for t in dataset[split]["text"] if len(t.strip()) > 50]
        all_ids = []
        for text in texts:
            ids = tokenizer.encode(text, add_special_tokens=False)
            all_ids.extend(ids)
        
        # Chunk into sequences
        chunks = []
        for i in range(0, len(all_ids) - seq_len, seq_len):
            chunk = torch.tensor(all_ids[i:i + seq_len], dtype=torch.long)
            chunks.append({'input_ids': chunk})
        return chunks
    
    train_data = tokenize_and_chunk("train")
    eval_data = tokenize_and_chunk("validation")
    
    log(f"  Train: {len(train_data)} sequences")
    log(f"  Eval:  {len(eval_data)} sequences")
    
    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    eval_loader = DataLoader(eval_data, batch_size=batch_size, shuffle=False)
    
    return train_loader, eval_loader


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def run_experiment(mode: str, n_steps: int, device_str: str):
    log("=" * 72)
    log(f"CRYSTAL SIEVE PROTOTYPE — mode={mode}")
    log("=" * 72)
    
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    # Device
    if device_str == "auto":
        device = torch.device("mps" if torch.backends.mps.is_available()
                              else "cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device_str)
    log(f"Device: {device}")
    
    # Load model and tokenizer
    log("\nLoading Pythia-160M...")
    model_id = "EleutherAI/pythia-160m-deduped"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float32)
    
    # Baseline perplexity (float model)
    log("\nPreparing data...")
    train_loader, eval_loader = prepare_data(tokenizer)
    
    model.to(device)
    model.eval()
    baseline_ppl = evaluate_perplexity(model, eval_loader, device, temperature=1.0, max_batches=50)
    log(f"\nFloat baseline PPL: {baseline_ppl:.2f}")
    
    # Patch model with crystal sieve
    log(f"\nPatching model ({mode} mode)...")
    model = model.cpu()  # patch on CPU
    model = extract_crystal_and_patch(model, mode=mode)
    
    # Freeze non-mask params
    log("Freezing non-mask parameters...")
    n_train, n_frozen = freeze_except_masks(model)
    
    model.to(device)
    
    # Initial PPL (before training masks)
    model.eval()
    init_ppl = evaluate_perplexity(model, eval_loader, device, temperature=2.0, max_batches=50)
    log(f"\nInitial PPL ({mode} sieve, untrained masks): {init_ppl:.2f}")
    
    # Train
    log(f"\nTraining ({n_steps} steps)...")
    final_ppl = train(model, train_loader, eval_loader, device, n_steps=n_steps)
    
    # Summary
    log(f"\n{'=' * 72}")
    log(f"SUMMARY — {mode} mode")
    log(f"{'=' * 72}")
    log(f"  Float baseline PPL:    {baseline_ppl:.2f}")
    log(f"  Initial sieve PPL:     {init_ppl:.2f}")
    log(f"  After {n_steps} steps PPL: {final_ppl:.2f}")
    log(f"  Recovery: {baseline_ppl/final_ppl*100:.1f}% of float baseline")
    
    # Count final active weights
    total_mask_params = 0
    total_active = 0
    for layer in model.gpt_neox.layers:
        for name in ['dense_h_to_4h', 'dense_4h_to_h']:
            sieve = getattr(layer.mlp, name)
            if isinstance(sieve, CrystalSieveLinear):
                total_mask_params += sieve.importance.numel()
                total_active += (sieve.importance > 0).sum().item()
    
    log(f"  Active weights: {total_active:,} / {total_mask_params:,} "
        f"({total_active/total_mask_params:.1%})")
    log(f"  Final model size: {total_active / 8 / 1024 / 1024:.2f} MB "
        f"(1 bit per active weight)")
    
    return final_ppl


def main():
    parser = argparse.ArgumentParser(description="Crystal Sieve Prototype")
    parser.add_argument("--mode", type=str, default="crystal",
                        choices=["crystal", "random"],
                        help="crystal=signs from trained model, random=random ternary")
    parser.add_argument("--steps", type=int, default=250)
    parser.add_argument("--device", type=str, default="auto")
    args = parser.parse_args()
    
    run_experiment(args.mode, args.steps, args.device)


if __name__ == "__main__":
    main()
