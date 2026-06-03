#!/usr/bin/env python3
"""Copy the program: per-neuron firing rates from teacher → zero mask.

THE INSIGHT: The teacher computes which neurons fire every forward pass.
The firing rate IS the program. Copy it directly.

Per neuron, not per weight:
  - Zero entire row of gate_proj + up_proj
  - Zero corresponding column of down_proj
  - One binary decision per neuron

Total program size: n_intermediate × n_layers bits = 54 KB for Qwen3-8B.

Usage:
  uv run python scripts/experiments/copy_program.py --model Qwen/Qwen3-8B
  uv run python scripts/experiments/copy_program.py --model Qwen/Qwen3-8B --n-calib 100

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import math
import os
import time

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch
import torch.nn.functional as F

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


def neuron_pruned_cosine(W: torch.Tensor, active_mask_1d: torch.Tensor,
                          dim: str = "row") -> tuple[float, float]:
    """Ternary reconstruction with neuron-level pruning.
    
    dim="row": zero entire rows (for gate/up)
    dim="col": zero entire columns (for down)
    """
    W_f32 = W.float()
    T = torch.sign(W_f32)
    
    if dim == "row":
        # Zero entire rows for inactive neurons
        T[~active_mask_1d, :] = 0
    else:
        # Zero entire columns for inactive neurons
        T[:, ~active_mask_1d] = 0
    
    wt = (W_f32 * T).sum(dim=1)
    tt = (T * T).sum(dim=1).clamp(min=1)
    gamma = wt / tt
    
    W_recon = gamma.unsqueeze(1) * T
    w_flat = W_f32.flatten()
    r_flat = W_recon.flatten()
    cos_pr = (torch.dot(w_flat, r_flat) / 
              (torch.norm(w_flat) * torch.norm(r_flat) + 1e-10)).item()
    
    gamma_c = torch.full_like(gamma, gamma[gamma != 0].mean().item() if (gamma != 0).any() else 0)
    W_recon_c = gamma_c.unsqueeze(1) * T
    cos_c = (torch.dot(w_flat, W_recon_c.flatten()) /
             (torch.norm(w_flat) * torch.norm(W_recon_c.flatten()) + 1e-10)).item()
    
    return cos_pr, cos_c


def run_experiment(model_id: str, layer_indices: list[int], n_calib: int = 50,
                   seq_len: int = 512):
    log("=" * 72)
    log("COPY THE PROGRAM — Neuron Firing Rates → Zero Mask")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Calibration: {n_calib} sequences × {seq_len} tokens")
    log()

    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="cpu",
        low_cpu_mem_usage=True)
    model.eval()

    config = model.config
    n_layers = config.num_hidden_layers
    intermediate = config.intermediate_size
    log(f"Loaded: {n_layers} layers, {intermediate} intermediate neurons")
    log(f"Program size: {intermediate * n_layers} bits = "
        f"{intermediate * n_layers / 8 / 1024:.1f} KB")

    # ── Calibration data ────────────────────────────────────────
    log("\nPreparing calibration data...")
    try:
        from datasets import load_dataset
        dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
        texts = [t for t in dataset["text"] if len(t.strip()) > 100]
    except Exception:
        texts = ["The quick brown fox jumps over the lazy dog. " * 30] * 200

    calib_ids = []
    for text in texts:
        ids = tokenizer.encode(text, add_special_tokens=False, truncation=True,
                               max_length=seq_len)
        if len(ids) >= 32:
            calib_ids.append(torch.tensor(ids[:seq_len]))
        if len(calib_ids) >= n_calib:
            break
    log(f"  {len(calib_ids)} calibration sequences")

    # ── Record per-neuron firing rates ──────────────────────────
    log("\nRecording firing rates...")
    
    # Per-neuron accumulators for ALL layers
    firing_sum = {l: torch.zeros(intermediate) for l in range(n_layers)}
    firing_count = {l: 0 for l in range(n_layers)}
    
    t0 = time.time()
    
    with torch.no_grad():
        for batch_idx, ids in enumerate(calib_ids):
            # Hook ALL layers' gate activations
            captured = {}
            hooks = []
            
            for l in range(n_layers):
                def make_hook(layer_idx):
                    def hook_fn(module, input, output):
                        # gate_proj output, before SiLU
                        gate_act = F.silu(output.detach().float().cpu())
                        # Per-neuron mean absolute activation across sequence
                        captured[layer_idx] = gate_act.squeeze(0).abs().mean(dim=0)
                    return hook_fn
                h = model.model.layers[l].mlp.gate_proj.register_forward_hook(make_hook(l))
                hooks.append(h)
            
            _ = model(ids.unsqueeze(0))
            
            for h in hooks:
                h.remove()
            
            for l in range(n_layers):
                if l in captured:
                    firing_sum[l] += captured[l]
                    firing_count[l] += 1
            
            captured.clear()
            
            if (batch_idx + 1) % 10 == 0:
                log(f"  batch {batch_idx + 1}/{len(calib_ids)}")
    
    elapsed = time.time() - t0
    log(f"  Done in {elapsed:.1f}s")
    
    # Normalize to get mean firing rates
    firing_rates = {}
    for l in range(n_layers):
        if firing_count[l] > 0:
            firing_rates[l] = firing_sum[l] / firing_count[l]
        else:
            firing_rates[l] = torch.zeros(intermediate)

    # ── Analysis per layer ──────────────────────────────────────
    log(f"\n{'═' * 72}")
    log("PER-LAYER FIRING RATE STATISTICS")
    log(f"{'═' * 72}")
    
    log(f"\n  {'Layer':>5s} {'mean_rate':>10s} {'std_rate':>10s} {'CV':>8s} "
        f"{'min':>8s} {'max':>8s} {'near_zero%':>10s}")
    
    for l in range(n_layers):
        fr = firing_rates[l].numpy()
        near_zero = (fr < fr.mean() * 0.1).mean() * 100
        log(f"  {l:5d} {fr.mean():10.4f} {fr.std():10.4f} {fr.std()/fr.mean():8.4f} "
            f"{fr.min():8.4f} {fr.max():8.4f} {near_zero:10.1f}%")

    # ── Test on selected layers ─────────────────────────────────
    for layer_idx in layer_indices:
        log(f"\n{'═' * 72}")
        log(f"LAYER {layer_idx}")
        log(f"{'═' * 72}")
        
        fr = firing_rates[layer_idx]
        W_gate = model.model.layers[layer_idx].mlp.gate_proj.weight.data.float().cpu()
        W_up = model.model.layers[layer_idx].mlp.up_proj.weight.data.float().cpu()
        W_down = model.model.layers[layer_idx].mlp.down_proj.weight.data.float().cpu()
        
        gate_row_norms = W_gate.norm(dim=1)
        
        # Correlation: firing rate vs weight magnitude
        rho_fr_gate, p_val = torch.tensor(0.), torch.tensor(0.)
        from scipy.stats import spearmanr
        rho_fr_gate, p_gate = spearmanr(fr.numpy(), gate_row_norms.numpy())
        log(f"\n  Firing rate vs gate_row_norm: ρ={rho_fr_gate:.4f}")
        
        # ── Sweep neuron pruning rates ──────────────────────────
        log(f"\n  NEURON-LEVEL PRUNING (firing rate → active mask):")
        log(f"  {'prune%':>7s} {'active':>7s} {'gate_pr':>9s} {'gate_c':>9s} "
            f"{'up_pr':>9s} {'up_c':>9s} {'down_pr':>9s} {'down_c':>9s}")
        
        for prune_frac in [0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]:
            # Keep the top (1-prune_frac) neurons by firing rate
            k_keep = int(intermediate * (1 - prune_frac))
            _, top_indices = fr.topk(k_keep)
            active = torch.zeros(intermediate, dtype=torch.bool)
            active[top_indices] = True
            
            cos_gate_pr, cos_gate_c = neuron_pruned_cosine(W_gate, active, "row")
            cos_up_pr, cos_up_c = neuron_pruned_cosine(W_up, active, "row")
            cos_down_pr, cos_down_c = neuron_pruned_cosine(W_down, active, "col")
            
            log(f"  {prune_frac:7.0%} {1-prune_frac:7.0%} "
                f"{cos_gate_pr:9.4f} {cos_gate_c:9.4f} "
                f"{cos_up_pr:9.4f} {cos_up_c:9.4f} "
                f"{cos_down_pr:9.4f} {cos_down_c:9.4f}")
        
        # ── Compare: firing rate vs magnitude vs random ─────────
        log(f"\n  COMPARISON AT 50% PRUNING:")
        
        k_half = intermediate // 2
        
        # By firing rate
        _, top_fr = fr.topk(k_half)
        active_fr = torch.zeros(intermediate, dtype=torch.bool)
        active_fr[top_fr] = True
        
        # By gate row norm (magnitude)
        _, top_mag = gate_row_norms.topk(k_half)
        active_mag = torch.zeros(intermediate, dtype=torch.bool)
        active_mag[top_mag] = True
        
        # Random
        active_rand = torch.zeros(intermediate, dtype=torch.bool)
        active_rand[torch.randperm(intermediate)[:k_half]] = True
        
        # Overlap between methods
        overlap_fr_mag = (active_fr == active_mag).float().mean().item()
        overlap_fr_rand = (active_fr == active_rand).float().mean().item()
        
        for label, active in [("Firing rate", active_fr), 
                               ("Magnitude", active_mag),
                               ("Random", active_rand)]:
            g_pr, g_c = neuron_pruned_cosine(W_gate, active, "row")
            u_pr, u_c = neuron_pruned_cosine(W_up, active, "row")
            d_pr, d_c = neuron_pruned_cosine(W_down, active, "col")
            log(f"    {label:15s}: gate={g_pr:.4f}  up={u_pr:.4f}  down={d_pr:.4f}")
        
        log(f"    Overlap(firing, magnitude): {overlap_fr_mag:.4f}")
        log(f"    Overlap(firing, random):    {overlap_fr_rand:.4f}")
        
        # ── The full chain: crystal signs + firing mask + crystal γ ─
        log(f"\n  FULL CHAIN: crystal signs + firing rate mask + crystal γ:")
        
        UNIVERSAL_C = {'gate': 0.0172, 'up': 0.0172, 'down': 0.0099}
        
        _, top_fr_50 = fr.topk(k_half)
        active_50 = torch.zeros(intermediate, dtype=torch.bool)
        active_50[top_fr_50] = True
        
        for wtype, W, dim in [("gate", W_gate, "row"), 
                                ("up", W_up, "row"), 
                                ("down", W_down, "col")]:
            T = torch.sign(W.float())
            if dim == "row":
                T[~active_50, :] = 0
            else:
                T[:, ~active_50] = 0
            
            c = UNIVERSAL_C[wtype]
            m = W.shape[0]
            frob = W.float().norm().item()
            gamma_crystal = c * frob / math.sqrt(m)
            
            W_recon = gamma_crystal * T
            w_flat = W.float().flatten()
            cos = (torch.dot(w_flat, W_recon.flatten()) /
                   (torch.norm(w_flat) * torch.norm(W_recon.flatten()) + 1e-10)).item()
            
            log(f"    {wtype:5s}: cos={cos:.6f}")

    # ── Global summary ──────────────────────────────────────────
    log(f"\n{'═' * 72}")
    log("FIRING RATE DISTRIBUTION ACROSS ALL LAYERS")
    log(f"{'═' * 72}")
    
    # What fraction of neurons are consistently low-firing across ALL layers?
    all_rates = torch.stack([firing_rates[l] for l in range(n_layers)])  # (n_layers, intermediate)
    mean_across_layers = all_rates.mean(dim=0)  # (intermediate,)
    
    # Neurons that are low-firing in ALL layers = ISA zeros
    threshold = mean_across_layers.mean() * 0.1
    always_low = (all_rates < threshold).all(dim=0).sum().item()
    sometimes_low = (all_rates < threshold).any(dim=0).sum().item()
    never_low = intermediate - sometimes_low
    
    log(f"\n  Always low-firing (all layers): {always_low} neurons ({always_low/intermediate:.1%})")
    log(f"  Sometimes low-firing:           {sometimes_low - always_low} neurons")
    log(f"  Never low-firing:               {never_low} neurons ({never_low/intermediate:.1%})")
    log(f"\n  Program size if neuron-level: {intermediate * n_layers / 8 / 1024:.1f} KB")
    log(f"  ISA-predictable zeros:         {always_low * n_layers / 8 / 1024:.1f} KB saved")

    del model
    gc.collect()

    log(f"\n{'═' * 72}")
    log("DONE")
    log(f"{'═' * 72}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", type=str, default="0,5,10,17,25,35")
    parser.add_argument("--n-calib", type=int, default=50)
    args = parser.parse_args()

    layer_indices = [int(x) for x in args.layers.split(",")]
    run_experiment(args.model, layer_indices, args.n_calib)


if __name__ == "__main__":
    main()
