#!/usr/bin/env python3
"""Activation-weighted zero mask extraction from teacher model.

THE PROCEDURE:
  1. Run calibration data through teacher
  2. Hook FFN layers to capture gate activations + inputs
  3. Compute per-weight importance: E[|gate_act[i]| · |x[j]|]
  4. Zero the least important 50% per row
  5. Crystal signs + activation zero mask + constant γ → reconstruct

THREE IMPORTANCE METRICS:
  A. Static magnitude: |W[i,j]|  (current baseline, needs float weights)
  B. Activation only: E[|gate[i]| · |x[j]|]  (from calibration, no weight magnitudes)
  C. Combined: E[|gate[i]| · |x[j]|] · |W[i,j]|  (activation × magnitude)

Usage:
  uv run python scripts/experiments/activation_zero_mask.py --model Qwen/Qwen3-8B
  uv run python scripts/experiments/activation_zero_mask.py --model Qwen/Qwen3-8B --n-calib 200

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


def ternary_with_mask(W: torch.Tensor, zero_mask: torch.Tensor) -> tuple[float, float]:
    """Reconstruct and return (cos_perrow, cos_const)."""
    W_f32 = W.float()
    T = torch.sign(W_f32)
    T[zero_mask] = 0
    wt = (W_f32 * T).sum(dim=1)
    tt = (T * T).sum(dim=1).clamp(min=1)
    gamma = wt / tt

    W_recon_pr = gamma.unsqueeze(1) * T
    w_flat = W_f32.flatten()
    cos_pr = (torch.dot(w_flat, W_recon_pr.flatten()) /
              (torch.norm(w_flat) * torch.norm(W_recon_pr.flatten()) + 1e-10)).item()

    gamma_c = torch.full_like(gamma, gamma.mean().item())
    W_recon_c = gamma_c.unsqueeze(1) * T
    cos_c = (torch.dot(w_flat, W_recon_c.flatten()) /
             (torch.norm(w_flat) * torch.norm(W_recon_c.flatten()) + 1e-10)).item()

    return cos_pr, cos_c


def run_experiment(model_id: str, layer_indices: list[int], n_calib: int = 100,
                   seq_len: int = 512):
    log("=" * 72)
    log("ACTIVATION-WEIGHTED ZERO MASK EXTRACTION")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Calibration: {n_calib} sequences × {seq_len} tokens")
    log(f"Layers: {layer_indices}")
    log()

    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="cpu",
        low_cpu_mem_usage=True)
    model.eval()
    log(f"Loaded {model_id}")

    # ── Prepare calibration data ────────────────────────────────
    log("\nPreparing calibration data...")
    try:
        from datasets import load_dataset
        dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
        texts = [t for t in dataset["text"] if len(t.strip()) > 100][:n_calib * 2]
    except Exception:
        log("  WikiText not available, using synthetic calibration data")
        texts = [
            "The quick brown fox jumps over the lazy dog. " * 20,
            "In mathematics, the golden ratio is approximately 1.618. " * 20,
            "Language models learn to predict the next token in a sequence. " * 20,
        ] * (n_calib // 3 + 1)

    calib_ids = []
    for text in texts:
        ids = tokenizer.encode(text, add_special_tokens=False, truncation=True,
                               max_length=seq_len)
        if len(ids) >= 32:
            calib_ids.append(torch.tensor(ids[:seq_len]))
        if len(calib_ids) >= n_calib:
            break

    log(f"  {len(calib_ids)} calibration sequences prepared")

    # ── Process each layer ──────────────────────────────────────
    for layer_idx in layer_indices:
        log(f"\n{'═' * 72}")
        log(f"LAYER {layer_idx}")
        log(f"{'═' * 72}")

        target_layer = model.model.layers[layer_idx]
        W_gate = target_layer.mlp.gate_proj.weight.data.float().cpu()
        W_up = target_layer.mlp.up_proj.weight.data.float().cpu()
        W_down = target_layer.mlp.down_proj.weight.data.float().cpu()
        m_inter, m_hidden = W_gate.shape

        # Accumulators for activation statistics
        # For up_proj importance: E[|SiLU(gate_act)[i]| · |x[j]|]
        gate_act_abs_sum = torch.zeros(m_inter)       # Σ|SiLU(gate_act)[i]|
        input_abs_sum = torch.zeros(m_hidden)          # Σ|x[j]|
        # For the outer product (too large to store full), accumulate per-row:
        # importance_up[i,j] = E[|gate[i]| · |x[j]|]
        # We'll compute this as outer product of marginals + correction
        # Actually, just accumulate it directly per batch since we need per-weight

        importance_up = torch.zeros(m_inter, m_hidden)
        importance_down_input = torch.zeros(m_inter)  # E[|hidden[i]|] for down_proj
        n_tokens = 0

        # Hook to capture inputs and gate activations
        captured = {}

        def make_hook(name):
            def hook_fn(module, input, output):
                captured[name] = input[0].detach().float().cpu()
            return hook_fn

        # We need the input to the MLP (after layernorm)
        # In Qwen, the MLP input goes through a post_attention_layernorm
        # The actual FFN computation is in the mlp module
        hook_handle = target_layer.mlp.register_forward_hook(
            lambda mod, inp, out: captured.update({'mlp_input': inp[0].detach().float().cpu()}))

        log(f"\n  Running calibration ({len(calib_ids)} sequences)...")
        t0 = time.time()

        with torch.no_grad():
            for batch_idx, ids in enumerate(calib_ids):
                ids_input = ids.unsqueeze(0)  # (1, seq_len)
                _ = model(ids_input)

                if 'mlp_input' not in captured:
                    log(f"    WARNING: mlp_input not captured at batch {batch_idx}")
                    continue

                x = captured['mlp_input'].squeeze(0)  # (seq_len, hidden)
                seq_len_actual = x.shape[0]

                # Compute gate activation
                gate_out = F.silu(x @ W_gate.T)  # (seq, intermediate)

                # Accumulate per-weight importance for up_proj
                # importance_up[i,j] += Σ_t |gate_out[t,i]| · |x[t,j]|
                gate_abs = gate_out.abs()  # (seq, inter)
                x_abs = x.abs()            # (seq, hidden)

                # Outer product sum: (inter, seq) @ (seq, hidden) = (inter, hidden)
                importance_up += gate_abs.T @ x_abs

                # For down_proj: importance of column i ∝ E[|hidden[i]|]
                # hidden = gate_out ⊙ (x @ W_up.T)
                up_out = x @ W_up.T  # (seq, intermediate)
                hidden = gate_out * up_out
                importance_down_input += hidden.abs().sum(dim=0)  # (intermediate,)

                n_tokens += seq_len_actual

                captured.clear()

                if (batch_idx + 1) % 20 == 0:
                    log(f"    batch {batch_idx+1}/{len(calib_ids)}")

        hook_handle.remove()
        elapsed = time.time() - t0
        log(f"  Done: {n_tokens} tokens in {elapsed:.1f}s")

        # Normalize
        importance_up /= n_tokens
        importance_down_input /= n_tokens

        # ── Build zero masks from different importance metrics ───
        log(f"\n  ZERO MASK COMPARISON:")

        abs_up = W_up.abs()
        abs_down = W_down.abs()

        for target_label, W_target, abs_target in [
            ("up_proj", W_up, abs_up),
            ("down_proj", W_down, abs_down),
        ]:
            log(f"\n    {target_label}:")

            # Build importance scores for this target
            if target_label == "up_proj":
                # Method A: static magnitude
                score_static = abs_target

                # Method B: activation only (no weight magnitudes)
                score_activation = importance_up

                # Method C: activation × magnitude
                score_combined = importance_up * abs_target

            else:
                # For down_proj (4096, 12288):
                # Each column i of down corresponds to intermediate neuron i
                # importance ∝ E[|hidden[i]|] for column i
                # Per-weight: importance_down[j,i] = importance_down_input[i] · |down[j,i]|

                # Method A: static magnitude
                score_static = abs_target

                # Method B: activation only — broadcast neuron importance to columns
                # down is (hidden, intermediate), so column i = neuron i
                score_activation = importance_down_input.unsqueeze(0).expand_as(W_down)

                # Method C: activation × magnitude
                score_combined = score_activation * abs_target

            for zero_rate in [0.35, 0.50]:
                log(f"\n      Zero rate: {zero_rate:.0%}")

                # Static magnitude zeros (baseline)
                thresh_s = torch.quantile(score_static, zero_rate, dim=1, keepdim=True)
                mask_static = score_static < thresh_s
                cos_s_pr, cos_s_c = ternary_with_mask(W_target, mask_static)

                # Activation-only zeros
                # For per-row threshold, we need score_activation to have per-row variation
                if score_activation.dim() == 2 and score_activation.shape == W_target.shape:
                    thresh_a = torch.quantile(score_activation, zero_rate, dim=1, keepdim=True)
                    mask_activ = score_activation < thresh_a
                else:
                    # Fallback: global threshold
                    thresh_a = torch.quantile(score_activation.flatten(),
                                              zero_rate).item()
                    mask_activ = score_activation < thresh_a
                cos_a_pr, cos_a_c = ternary_with_mask(W_target, mask_activ)

                # Combined zeros (activation × magnitude)
                thresh_c = torch.quantile(score_combined, zero_rate, dim=1, keepdim=True)
                mask_combined = score_combined < thresh_c
                cos_c_pr, cos_c_c = ternary_with_mask(W_target, mask_combined)

                # Random zeros (reference)
                mask_rand = torch.zeros_like(W_target, dtype=torch.bool)
                n_per_row = int(W_target.shape[1] * zero_rate)
                for row in range(W_target.shape[0]):
                    idx = torch.randperm(W_target.shape[1])[:n_per_row]
                    mask_rand[row, idx] = True
                cos_r_pr, cos_r_c = ternary_with_mask(W_target, mask_rand)

                log(f"        Static magnitude:       cos_pr={cos_s_pr:.6f}  cos_c={cos_s_c:.6f}")
                log(f"        Activation only:         cos_pr={cos_a_pr:.6f}  cos_c={cos_a_c:.6f}")
                log(f"        Activation × magnitude:  cos_pr={cos_c_pr:.6f}  cos_c={cos_c_c:.6f}")
                log(f"        Random:                  cos_pr={cos_r_pr:.6f}  cos_c={cos_r_c:.6f}")

        # ── The full extraction chain ───────────────────────────
        log(f"\n  FULL EXTRACTION CHAIN (crystal signs + activation mask + crystal γ):")

        UNIVERSAL_C_UP = 0.0172
        UNIVERSAL_C_DOWN = 0.0099

        for target_label, W_target, score in [
            ("up_proj", W_up, importance_up * abs_up),
            ("down_proj", W_down, importance_down_input.unsqueeze(0).expand_as(W_down) * abs_down),
        ]:
            W_f32 = W_target.float()
            m, n = W_f32.shape

            # Signs from crystal (= sign of float weights, 100% accurate)
            T = torch.sign(W_f32)

            # Zero mask from activation × magnitude at 50%
            thresh = torch.quantile(score, 0.50, dim=1, keepdim=True)
            mask = score < thresh
            T[mask] = 0

            # Crystal gamma: constant per matrix
            c = UNIVERSAL_C_UP if "up" in target_label else UNIVERSAL_C_DOWN
            frob = W_f32.norm().item()
            gamma_crystal = c * frob / math.sqrt(m)

            W_recon = gamma_crystal * T
            w_flat = W_f32.flatten()
            cos = (torch.dot(w_flat, W_recon.flatten()) /
                   (torch.norm(w_flat) * torch.norm(W_recon.flatten()) + 1e-10)).item()

            # Compare with baseline
            thresh_base = torch.quantile(W_f32.abs(), 0.50, dim=1, keepdim=True)
            mask_base = W_f32.abs() < thresh_base
            T_base = torch.sign(W_f32)
            T_base[mask_base] = 0
            wt = (W_f32 * T_base).sum(dim=1)
            tt = (T_base * T_base).sum(dim=1).clamp(min=1)
            gamma_true = wt / tt
            W_recon_base = gamma_true.unsqueeze(1) * T_base
            cos_base = (torch.dot(w_flat, W_recon_base.flatten()) /
                        (torch.norm(w_flat) * torch.norm(W_recon_base.flatten()) + 1e-10)).item()

            log(f"    {target_label:10s}: activation_mask + crystal_γ = {cos:.6f}  "
                f"(baseline magnitude @50% = {cos_base:.6f}  "
                f"gap = {cos - cos_base:+.6f})")

    del model
    gc.collect()

    log(f"\n{'═' * 72}")
    log("DONE")
    log(f"{'═' * 72}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", type=str, default="0,5,10,17,25,35")
    parser.add_argument("--n-calib", type=int, default=100)
    args = parser.parse_args()

    layer_indices = [int(x) for x in args.layers.split(",")]
    run_experiment(args.model, layer_indices, n_calib=args.n_calib)


if __name__ == "__main__":
    main()
