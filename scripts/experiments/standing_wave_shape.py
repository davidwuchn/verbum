#!/usr/bin/env python3
"""Standing-wave shape preservation — does shape fidelity predict quantization quality?

HYPOTHESIS:
  Quantization works because it preserves the shape (peaks and valleys)
  of the weight magnitude standing wave. Shape fidelity should predict
  model quality (PPL) better than raw bit count.

EXPERIMENT:
  Take Pythia-160M (12 layers, small, fast).
  Quantize FFN weights at multiple levels:
    - Ternary: sign + per-row gamma (1.6 bits, no shape)
    - 2-bit uniform: 4 levels, uniform spacing
    - 2-bit shape-aware: 4 levels at magnitude quartiles (like GPTQ)
    - 3-bit uniform: 8 levels
    - 4-bit uniform: 16 levels
    - 8-bit uniform: 256 levels
    - Float baseline: original weights

  For each, measure:
    1. Per-layer cosine (original vs quantized)
    2. Per-layer shape correlation: Spearman rank correlation of
       |W_orig| vs |W_quant| within each row
       (do peaks stay in the same relative order?)
    3. Full-model perplexity on WikiText-2 validation

  The standing-wave hypothesis predicts:
    - Shape correlation is a better predictor of PPL than bit count
    - 2-bit shape-aware >> ternary despite similar bit budget
    - The compounding failure of ternary is shape loss, not bit loss

Usage:
  uv run python scripts/experiments/standing_wave_shape.py
  uv run python scripts/experiments/standing_wave_shape.py --model EleutherAI/pythia-160m-deduped

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import math
import os
import time
from dataclasses import dataclass, field

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import stats as scipy_stats


def log(msg: str = "") -> None:
    print(msg, flush=True)


# ═══════════════════════════════════════════════════════════════════
# Quantization methods — each returns a reconstructed float tensor
# ═══════════════════════════════════════════════════════════════════

def quantize_ternary(W: torch.Tensor, zero_rate: float = 0.50) -> torch.Tensor:
    """Ternary: sign + per-row gamma + magnitude-based zeros.
    
    The standing-wave TOPOLOGY: preserves sign (phase) and presence
    (nodes), but all antinodes have the same height per row.
    """
    W = W.detach().float().cpu()
    abs_W = W.abs()
    
    if zero_rate > 0:
        thresholds = torch.quantile(abs_W, zero_rate, dim=1, keepdim=True)
        alive = abs_W >= thresholds
    else:
        alive = torch.ones_like(W, dtype=torch.bool)
    
    T = torch.where(alive, torch.sign(W), torch.zeros_like(W))
    
    # Optimal per-row gamma: γ_i = (w_i · t_i) / (t_i · t_i)
    wt = (W * T).sum(dim=1)
    tt = (T * T).sum(dim=1)
    gamma = torch.where(tt > 0, wt / tt, torch.zeros_like(wt))
    
    return gamma.unsqueeze(1) * T


def quantize_nbit_uniform(W: torch.Tensor, n_bits: int) -> torch.Tensor:
    """Uniform n-bit quantization with per-row min/max scaling.
    
    Maps the range [min, max] per row to 2^n_bits uniform levels.
    Preserves shape proportional to level count.
    """
    W = W.detach().float().cpu()
    n_levels = 2 ** n_bits
    
    row_min = W.min(dim=1, keepdim=True).values
    row_max = W.max(dim=1, keepdim=True).values
    row_range = row_max - row_min
    row_range = torch.clamp(row_range, min=1e-10)
    
    # Normalize to [0, 1]
    W_norm = (W - row_min) / row_range
    
    # Quantize to n_levels uniform steps
    W_quant = torch.round(W_norm * (n_levels - 1)) / (n_levels - 1)
    
    # Denormalize
    return W_quant * row_range + row_min


def quantize_nbit_quartile(W: torch.Tensor, n_bits: int) -> torch.Tensor:
    """Shape-aware n-bit quantization: levels at magnitude quantiles.
    
    Like GPTQ/NF4 — places levels where the data actually IS,
    not uniformly. Should preserve shape much better at low bit counts.
    """
    W = W.detach().float().cpu()
    n_levels = 2 ** n_bits
    out_f, in_f = W.shape
    
    W_quant = torch.zeros_like(W)
    
    for i in range(out_f):
        row = W[i]
        # Compute quantile boundaries
        quantiles = torch.linspace(0, 1, n_levels + 1, device=W.device)
        boundaries = torch.quantile(row, quantiles)
        
        # Compute level centers (midpoint of each bin)
        centers = (boundaries[:-1] + boundaries[1:]) / 2
        
        # Assign each weight to nearest center
        # Expand for broadcasting: row (in_f,) vs centers (n_levels,)
        diffs = (row.unsqueeze(1) - centers.unsqueeze(0)).abs()  # (in_f, n_levels)
        assignments = diffs.argmin(dim=1)  # (in_f,)
        W_quant[i] = centers[assignments]
    
    return W_quant


# ═══════════════════════════════════════════════════════════════════
# Shape measurement — the core metric
# ═══════════════════════════════════════════════════════════════════

@dataclass
class LayerMetrics:
    layer_idx: int
    weight_name: str
    cosine: float
    shape_spearman: float  # Spearman rank correlation of |W| vs |W_q| per row, averaged
    shape_pearson: float   # Pearson correlation of |W| vs |W_q| per row, averaged
    peak_preservation: float  # fraction of top-10% magnitude positions that stay in top-10%
    node_preservation: float  # fraction of bottom-10% that stay in bottom-10%


def measure_shape(W_orig: torch.Tensor, W_quant: torch.Tensor) -> dict:
    """Measure how well quantization preserves the magnitude shape.
    
    Returns dict with cosine, spearman, pearson, peak_preservation, node_preservation.
    """
    W_o = W_orig.detach().float().cpu()
    W_q = W_quant.detach().float().cpu()
    
    # 1. Global cosine
    cos = F.cosine_similarity(
        W_o.reshape(1, -1), W_q.reshape(1, -1)
    ).item()
    
    # 2. Per-row Spearman rank correlation of magnitudes
    abs_o = W_o.abs().numpy()
    abs_q = W_q.abs().numpy()
    
    spearman_scores = []
    pearson_scores = []
    
    n_rows = min(abs_o.shape[0], 200)  # sample rows for speed
    row_indices = np.linspace(0, abs_o.shape[0] - 1, n_rows, dtype=int)
    
    for i in row_indices:
        row_o = abs_o[i]
        row_q = abs_q[i]
        
        # Skip constant rows
        if row_o.std() < 1e-10 or row_q.std() < 1e-10:
            continue
        
        sp, _ = scipy_stats.spearmanr(row_o, row_q)
        pe, _ = scipy_stats.pearsonr(row_o, row_q)
        
        if not np.isnan(sp):
            spearman_scores.append(sp)
        if not np.isnan(pe):
            pearson_scores.append(pe)
    
    spearman_mean = float(np.mean(spearman_scores)) if spearman_scores else 0.0
    pearson_mean = float(np.mean(pearson_scores)) if pearson_scores else 0.0
    
    # 3. Peak preservation: do the biggest weights stay biggest?
    # Top 10% by magnitude in original — what fraction stay in top 10% after quant?
    W_o_cpu = W_o.cpu()
    W_q_cpu = W_q.cpu()
    k_top = max(1, W_o_cpu.numel() // 10)
    top_orig = torch.topk(W_o_cpu.abs().reshape(-1), k_top).indices
    top_quant = torch.topk(W_q_cpu.abs().reshape(-1), k_top).indices
    
    top_orig_set = set(top_orig.numpy())
    top_quant_set = set(top_quant.numpy())
    peak_pres = len(top_orig_set & top_quant_set) / len(top_orig_set) if top_orig_set else 0.0
    
    # 4. Node preservation: do the smallest weights stay smallest?
    # Bottom 10% by magnitude
    bot_orig = torch.topk(W_o_cpu.abs().reshape(-1), k_top, largest=False).indices
    bot_quant = torch.topk(W_q_cpu.abs().reshape(-1), k_top, largest=False).indices
    
    bot_orig_set = set(bot_orig.numpy())
    bot_quant_set = set(bot_quant.numpy())
    node_pres = len(bot_orig_set & bot_quant_set) / len(bot_orig_set) if bot_orig_set else 0.0
    
    return {
        'cosine': cos,
        'spearman': spearman_mean,
        'pearson': pearson_mean,
        'peak_preservation': peak_pres,
        'node_preservation': node_pres,
    }


# ═══════════════════════════════════════════════════════════════════
# The experiment
# ═══════════════════════════════════════════════════════════════════

QUANT_METHODS = {
    'ternary_50':       ('Ternary (50% zeros)',    1.6, lambda W: quantize_ternary(W, 0.50)),
    'ternary_35':       ('Ternary (35% zeros)',    1.6, lambda W: quantize_ternary(W, 0.35)),
    'ternary_0':        ('Ternary (no zeros)',     1.6, lambda W: quantize_ternary(W, 0.00)),
    '2bit_uniform':     ('2-bit uniform',          2.0, lambda W: quantize_nbit_uniform(W, 2)),
    '2bit_quartile':    ('2-bit shape-aware',      2.0, lambda W: quantize_nbit_quartile(W, 2)),
    '3bit_uniform':     ('3-bit uniform',          3.0, lambda W: quantize_nbit_uniform(W, 3)),
    '4bit_uniform':     ('4-bit uniform',          4.0, lambda W: quantize_nbit_uniform(W, 4)),
    '4bit_quartile':    ('4-bit shape-aware',      4.0, lambda W: quantize_nbit_quartile(W, 4)),
    '8bit_uniform':     ('8-bit uniform',          8.0, lambda W: quantize_nbit_uniform(W, 8)),
}


class QuantLinear(nn.Module):
    """Drop-in Linear replacement with pre-computed quantized weights."""
    
    def __init__(self, W_quant: torch.Tensor, bias: torch.Tensor | None):
        super().__init__()
        self.register_buffer('weight', W_quant)
        if bias is not None:
            self.register_buffer('bias', bias)
        else:
            self.bias = None
    
    def forward(self, x):
        return F.linear(x, self.weight, self.bias)


def quantize_model(model, method_key: str, device: str = "cpu"):
    """Quantize all FFN weights and collect shape metrics.
    
    Pythia-160M architecture: GPT-NeoX
      FFN: dense_h_to_4h (768 → 3072), dense_4h_to_h (3072 → 768)
    """
    _, label, bits, quant_fn = method_key, *QUANT_METHODS[method_key]
    
    all_metrics = []
    
    for layer_idx, layer in enumerate(model.gpt_neox.layers):
        mlp = layer.mlp
        
        for name in ['dense_h_to_4h', 'dense_4h_to_h']:
            linear = getattr(mlp, name)
            W = linear.weight.data.float()
            
            # Quantize
            W_q = quant_fn(W)
            
            # Measure shape
            m = measure_shape(W, W_q)
            metrics = LayerMetrics(
                layer_idx=layer_idx,
                weight_name=name,
                cosine=m['cosine'],
                shape_spearman=m['spearman'],
                shape_pearson=m['pearson'],
                peak_preservation=m['peak_preservation'],
                node_preservation=m['node_preservation'],
            )
            all_metrics.append(metrics)
            
            # Replace weight
            bias = linear.bias.data.float() if linear.bias is not None else None
            quant_linear = QuantLinear(W_q.to(device), bias.to(device) if bias is not None else None)
            setattr(mlp, name, quant_linear)
    
    return all_metrics


def evaluate_perplexity(model, tokenizer, device, max_tokens: int = 32768):
    """Evaluate perplexity on WikiText-2 validation set."""
    from datasets import load_dataset
    
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="validation")
    
    # Concatenate all text
    texts = [t for t in dataset['text'] if t.strip()]
    full_text = "\n".join(texts)
    
    tokens = tokenizer.encode(full_text, add_special_tokens=False)
    tokens = tokens[:max_tokens]
    
    model.eval()
    seq_len = 256
    total_loss = 0.0
    total_tokens = 0
    
    with torch.no_grad():
        for start in range(0, len(tokens) - seq_len, seq_len):
            chunk = tokens[start:start + seq_len]
            input_ids = torch.tensor([chunk], device=device)
            
            outputs = model(input_ids, labels=input_ids)
            total_loss += outputs.loss.item() * (len(chunk) - 1)
            total_tokens += len(chunk) - 1
    
    avg_loss = total_loss / max(total_tokens, 1)
    ppl = math.exp(min(avg_loss, 20))
    return ppl


def main():
    parser = argparse.ArgumentParser(description="Standing-wave shape preservation experiment")
    parser.add_argument('--model', default='EleutherAI/pythia-160m-deduped')
    parser.add_argument('--device', default='mps' if torch.backends.mps.is_available() else 'cpu')
    parser.add_argument('--max-tokens', type=int, default=32768)
    args = parser.parse_args()
    
    log(f"═══ Standing-Wave Shape Preservation Experiment ═══")
    log(f"Model: {args.model}")
    log(f"Device: {args.device}")
    log()
    
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    # Load tokenizer once
    log("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # ── Float baseline ──
    log("Loading float model for baseline...")
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float32)
    model = model.to(args.device)
    
    log("Evaluating float baseline PPL...")
    float_ppl = evaluate_perplexity(model, tokenizer, args.device, args.max_tokens)
    log(f"  Float PPL: {float_ppl:.2f}")
    log()
    
    # Save original weights for re-use
    log("Caching original weights...")
    original_weights = {}
    for layer_idx, layer in enumerate(model.gpt_neox.layers):
        mlp = layer.mlp
        for name in ['dense_h_to_4h', 'dense_4h_to_h']:
            linear = getattr(mlp, name)
            key = f"layer{layer_idx}.{name}"
            original_weights[key] = {
                'weight': linear.weight.data.float().cpu().clone(),
                'bias': linear.bias.data.float().cpu().clone() if linear.bias is not None else None,
            }
    log(f"  Cached {len(original_weights)} weight matrices")
    log()
    
    # ── Run each quantization method ──
    results = []
    
    for method_key in QUANT_METHODS:
        label, bits, quant_fn = QUANT_METHODS[method_key]
        log(f"{'─' * 60}")
        log(f"Method: {label} ({bits:.1f} bits)")
        
        # Restore original weights
        for layer_idx, layer in enumerate(model.gpt_neox.layers):
            mlp = layer.mlp
            for name in ['dense_h_to_4h', 'dense_4h_to_h']:
                key = f"layer{layer_idx}.{name}"
                orig = original_weights[key]
                
                # Restore as nn.Linear
                in_f = orig['weight'].shape[1]
                out_f = orig['weight'].shape[0]
                has_bias = orig['bias'] is not None
                new_linear = nn.Linear(in_f, out_f, bias=has_bias)
                new_linear.weight.data = orig['weight'].clone().to(args.device)
                if has_bias:
                    new_linear.bias.data = orig['bias'].clone().to(args.device)
                setattr(mlp, name, new_linear)
        
        # Quantize and measure shape
        t0 = time.time()
        metrics = quantize_model(model, method_key, args.device)
        quant_time = time.time() - t0
        
        # Aggregate shape metrics across layers
        avg_cosine = np.mean([m.cosine for m in metrics])
        avg_spearman = np.mean([m.shape_spearman for m in metrics])
        avg_pearson = np.mean([m.shape_pearson for m in metrics])
        avg_peak = np.mean([m.peak_preservation for m in metrics])
        avg_node = np.mean([m.node_preservation for m in metrics])
        
        # Compute compounded cosine (product across layers)
        # Group by layer, average within layer, then multiply across
        layer_cosines = {}
        for m in metrics:
            if m.layer_idx not in layer_cosines:
                layer_cosines[m.layer_idx] = []
            layer_cosines[m.layer_idx].append(m.cosine)
        per_layer_avg = [np.mean(v) for v in layer_cosines.values()]
        compounded_cosine = float(np.prod(per_layer_avg))
        
        log(f"  Avg cosine:         {avg_cosine:.4f}")
        log(f"  Compounded cosine:  {compounded_cosine:.6f}")
        log(f"  Shape (Spearman):   {avg_spearman:.4f}")
        log(f"  Shape (Pearson):    {avg_pearson:.4f}")
        log(f"  Peak preservation:  {avg_peak:.4f}")
        log(f"  Node preservation:  {avg_node:.4f}")
        log(f"  Quantize time:      {quant_time:.1f}s")
        
        # Evaluate PPL
        log(f"  Evaluating PPL...")
        ppl = evaluate_perplexity(model, tokenizer, args.device, args.max_tokens)
        log(f"  PPL: {ppl:.2f}")
        
        results.append({
            'method': method_key,
            'label': label,
            'bits': bits,
            'cosine': avg_cosine,
            'compounded_cosine': compounded_cosine,
            'spearman': avg_spearman,
            'pearson': avg_pearson,
            'peak_preservation': avg_peak,
            'node_preservation': avg_node,
            'ppl': ppl,
            'per_layer': [(m.layer_idx, m.weight_name, m.cosine, m.shape_spearman) for m in metrics],
        })
        
        log()
    
    # ═══ Summary table ═══
    log(f"{'═' * 80}")
    log(f"SUMMARY — Standing-Wave Shape Preservation")
    log(f"{'═' * 80}")
    log(f"Float baseline PPL: {float_ppl:.2f}")
    log()
    log(f"{'Method':<25} {'Bits':>5} {'Cosine':>8} {'Compound':>10} {'Spearman':>10} {'Peak%':>7} {'Node%':>7} {'PPL':>10}")
    log(f"{'─' * 25} {'─' * 5} {'─' * 8} {'─' * 10} {'─' * 10} {'─' * 7} {'─' * 7} {'─' * 10}")
    
    for r in sorted(results, key=lambda x: x['ppl']):
        log(f"{r['label']:<25} {r['bits']:>5.1f} {r['cosine']:>8.4f} {r['compounded_cosine']:>10.6f} "
            f"{r['spearman']:>10.4f} {r['peak_preservation']:>7.3f} {r['node_preservation']:>7.3f} {r['ppl']:>10.2f}")
    
    log()
    
    # ═══ Analysis: Shape vs Bits as PPL predictor ═══
    log(f"{'═' * 80}")
    log(f"ANALYSIS — What predicts PPL?")
    log(f"{'═' * 80}")
    
    ppls = [r['ppl'] for r in results]
    bits_arr = [r['bits'] for r in results]
    spearman_arr = [r['spearman'] for r in results]
    cosine_arr = [r['cosine'] for r in results]
    compound_arr = [r['compounded_cosine'] for r in results]
    peak_arr = [r['peak_preservation'] for r in results]
    
    log_ppls = [math.log(p) for p in ppls]
    
    # Correlate each predictor with log(PPL)
    predictors = [
        ('bits', bits_arr),
        ('cosine', cosine_arr),
        ('compounded_cosine', compound_arr),
        ('spearman (shape)', spearman_arr),
        ('peak_preservation', peak_arr),
    ]
    
    log(f"\nRank correlation with log(PPL):")
    log(f"  (negative = higher metric → lower PPL = better prediction)")
    log()
    
    for name, arr in predictors:
        rho, pval = scipy_stats.spearmanr(arr, log_ppls)
        log(f"  {name:<25} ρ = {rho:+.4f}  (p = {pval:.4f})")
    
    log()
    
    # Key comparison: ternary vs 2-bit
    ternary_50 = next((r for r in results if r['method'] == 'ternary_50'), None)
    twobit_q = next((r for r in results if r['method'] == '2bit_quartile'), None)
    twobit_u = next((r for r in results if r['method'] == '2bit_uniform'), None)
    
    if ternary_50 and twobit_q:
        log(f"KEY COMPARISON — Same bit budget, different shape preservation:")
        log(f"  Ternary 50%:       bits={ternary_50['bits']:.1f}  shape={ternary_50['spearman']:.4f}  PPL={ternary_50['ppl']:.2f}")
        log(f"  2-bit shape-aware: bits={twobit_q['bits']:.1f}  shape={twobit_q['spearman']:.4f}  PPL={twobit_q['ppl']:.2f}")
        if twobit_u:
            log(f"  2-bit uniform:     bits={twobit_u['bits']:.1f}  shape={twobit_u['spearman']:.4f}  PPL={twobit_u['ppl']:.2f}")
        
        ratio = ternary_50['ppl'] / twobit_q['ppl'] if twobit_q['ppl'] > 0 else float('inf')
        log(f"  PPL ratio (ternary/2bit-shape): {ratio:.2f}×")
        log()
        
        if ratio > 2.0:
            log(f"  ✅ HYPOTHESIS SUPPORTED: at similar bit budgets, shape preservation")
            log(f"     dramatically improves quality. Shape > bits.")
        elif ratio > 1.2:
            log(f"  ⚠️  PARTIAL SUPPORT: shape helps, but the effect is moderate.")
        else:
            log(f"  ❌ HYPOTHESIS NOT SUPPORTED: shape doesn't explain the difference.")
    
    log()
    log("Done.")
    
    # Save results
    import json
    out_dir = "results/standing-wave-shape"
    os.makedirs(out_dir, exist_ok=True)
    
    summary = {
        'model': args.model,
        'float_ppl': float_ppl,
        'results': [{k: v for k, v in r.items() if k != 'per_layer'} for r in results],
        'per_layer': {r['method']: r['per_layer'] for r in results},
    }
    
    with open(f"{out_dir}/summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    log(f"Results saved to {out_dir}/summary.json")


if __name__ == '__main__':
    main()
