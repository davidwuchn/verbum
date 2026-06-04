#!/usr/bin/env python3
"""DVD Group Scale — Ternary bitmasks + per-group gradient scaling.

THE SYNTHESIS: Ternary values aren't weight approximations — they're BITMASKS.
Per-group scaling (like Q4) preserves local gradient structure. The gradient
DVD tells you the envelope. The ternary mask tells you the structure within.

FOUR CONFIGURATIONS head-to-head:
  1. Magnitude mask + per-row scale     (baseline, PPL ~619K from dvd_stamp_test)
  2. Gradient mask  + per-row scale     (DVD stamp, PPL ~188K from dvd_stamp_test)
  3. Magnitude mask + per-group(32) scale  (ternary GPTQ)
  4. Gradient mask  + per-group(32) scale  (DVD player — the synthesis)

Reuses gradient_maps.pt from the DVD stamp test.

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/dvd_group_scale.py

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("PYTHONUNBUFFERED", "1")

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

DVD_DIR = Path(__file__).parent.parent.parent / "results" / "dvd-stamp-test"
RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "dvd-group-scale"

TARGET_MODULES_FFN = ["gate_proj", "up_proj", "down_proj"]
TARGET_MODULES_ATTN = ["q_proj", "k_proj", "v_proj", "o_proj"]
TARGET_MODULES = TARGET_MODULES_FFN + TARGET_MODULES_ATTN


def log(msg: str = "") -> None:
    print(msg, flush=True)


# ═══════════════════════════════════════════════════════════════════════
# TernaryLinear with per-group scaling
# ═══════════════════════════════════════════════════════════════════════


class TernaryLinearGrouped(nn.Module):
    """Ternary Linear with per-group scale factors.

    Instead of one gamma per output row, stores one gamma per GROUP of
    input features (like Q4's per-32-weight scale+zeropoint).

    Storage:
      T:     int8 (out_features, in_features)       ternary bitmask
      gamma: float32 (out_features, n_groups)        per-group scale
      bias:  float32 (out_features,) or None

    Forward:
      W_eff = gamma_expanded * T_float               reconstruct weights
      out = W_eff @ x + bias
    """

    def __init__(self, T: torch.Tensor, gamma: torch.Tensor,
                 group_size: int, bias: torch.Tensor | None = None):
        super().__init__()
        self.register_buffer("T", T.to(torch.int8))
        self.register_buffer("gamma", gamma.to(torch.float32))
        if bias is not None:
            self.register_buffer("bias", bias.to(torch.float32))
        else:
            self.bias = None
        self.out_features = T.shape[0]
        self.in_features = T.shape[1]
        self.group_size = group_size
        self.n_groups = gamma.shape[1]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Expand gamma from (out, n_groups) → (out, in) via repeat_interleave
        gamma = self.gamma.to(device=x.device, dtype=x.dtype)
        gamma_expanded = gamma.repeat_interleave(self.group_size, dim=1)
        # Trim if in_features not exactly divisible
        gamma_expanded = gamma_expanded[:, :self.in_features]

        T_cast = self.T.to(device=x.device, dtype=x.dtype)
        W_eff = gamma_expanded * T_cast
        out = F.linear(x, W_eff)
        if self.bias is not None:
            out = out + self.bias.to(device=x.device, dtype=x.dtype)
        return out

    def extra_repr(self) -> str:
        zeros = (self.T == 0).sum().item()
        total = self.T.numel()
        return (f"in={self.in_features}, out={self.out_features}, "
                f"groups={self.n_groups}, group_size={self.group_size}, "
                f"zeros={zeros}/{total} ({zeros/total*100:.1f}%)")


class TernaryLinearRow(nn.Module):
    """Ternary Linear with per-row scale (baseline)."""

    def __init__(self, T: torch.Tensor, gamma: torch.Tensor,
                 bias: torch.Tensor | None = None):
        super().__init__()
        self.register_buffer("T", T.to(torch.int8))
        self.register_buffer("gamma", gamma.to(torch.float32))
        if bias is not None:
            self.register_buffer("bias", bias.to(torch.float32))
        else:
            self.bias = None
        self.out_features = T.shape[0]
        self.in_features = T.shape[1]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        T_cast = self.T.to(device=x.device, dtype=x.dtype)
        out = F.linear(x, T_cast)
        gamma = self.gamma.to(device=x.device, dtype=x.dtype)
        out = out * gamma
        if self.bias is not None:
            out = out + self.bias.to(device=x.device, dtype=x.dtype)
        return out


# ═══════════════════════════════════════════════════════════════════════
# Mask building (reuse logic from dvd_stamp_test)
# ═══════════════════════════════════════════════════════════════════════


def build_masks(
    model, grad_maps: dict[str, torch.Tensor], zero_rate: float = 0.50,
) -> dict[str, dict[str, torch.Tensor]]:
    """Build magnitude and gradient masks."""
    masks = {"magnitude": {}, "gradient": {}}

    for name, param in model.named_parameters():
        if name not in grad_maps:
            continue

        W = param.data.detach().float().cpu()
        G = grad_maps[name]

        # Magnitude mask: zero smallest |W| per row
        abs_W = W.abs()
        mag_thresh = torch.quantile(abs_W, zero_rate, dim=1, keepdim=True)
        masks["magnitude"][name] = abs_W >= mag_thresh

        # Gradient mask (DVD): zero smallest mean|∇W| per row
        grad_thresh = torch.quantile(G, zero_rate, dim=1, keepdim=True)
        masks["gradient"][name] = G >= grad_thresh

    return masks


# ═══════════════════════════════════════════════════════════════════════
# Ternarization with per-group or per-row scaling
# ═══════════════════════════════════════════════════════════════════════


def ternarize_per_row(W: torch.Tensor, mask: torch.Tensor):
    """Ternarize with per-row optimal gamma. Returns (T, gamma, cosine)."""
    W_f = W.detach().float().cpu()
    T = torch.where(mask, torch.sign(W_f), torch.zeros_like(W_f))
    wt = (W_f * T).sum(dim=1)
    tt = (T * T).sum(dim=1)
    gamma = torch.where(tt > 0, wt / tt, torch.zeros_like(wt))
    # cosine
    W_recon = gamma.unsqueeze(1) * T
    cos = F.cosine_similarity(W_f.reshape(1, -1), W_recon.reshape(1, -1)).item()
    return T.to(torch.int8), gamma, cos


def ternarize_per_group(W: torch.Tensor, mask: torch.Tensor, group_size: int = 32):
    """Ternarize with per-group optimal gamma. Returns (T, gamma, cosine)."""
    W_f = W.detach().float().cpu()
    out_f, in_f = W_f.shape
    T = torch.where(mask, torch.sign(W_f), torch.zeros_like(W_f))

    # Compute per-group gamma: for each (row, group), optimal scalar
    n_groups = (in_f + group_size - 1) // group_size
    gamma = torch.zeros(out_f, n_groups, dtype=torch.float32)

    for g in range(n_groups):
        start = g * group_size
        end = min(start + group_size, in_f)
        W_g = W_f[:, start:end]
        T_g = T[:, start:end]
        wt = (W_g * T_g).sum(dim=1)
        tt = (T_g * T_g).sum(dim=1)
        gamma[:, g] = torch.where(tt > 0, wt / tt, torch.zeros_like(wt))

    # Reconstruct for cosine
    gamma_expanded = gamma.repeat_interleave(group_size, dim=1)[:, :in_f]
    W_recon = gamma_expanded * T
    cos = F.cosine_similarity(W_f.reshape(1, -1), W_recon.reshape(1, -1)).item()
    return T.to(torch.int8), gamma, cos


# ═══════════════════════════════════════════════════════════════════════
# Model surgery
# ═══════════════════════════════════════════════════════════════════════


def get_model_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise RuntimeError("Cannot find layers")


def ternarize_layer(layer, layer_idx, mask_set, scale_mode, group_size, device):
    """Ternarize one layer. Returns dict of per-module cosines."""
    cosines = {}

    for mod_type, mod_names, parent_attr in [
        ("ffn", TARGET_MODULES_FFN, "mlp"),
        ("attn", TARGET_MODULES_ATTN, "self_attn"),
    ]:
        parent = getattr(layer, parent_attr)
        for name in mod_names:
            proj = getattr(parent, name, None)
            if proj is None:
                continue
            if mod_type == "ffn":
                param_name = f"model.layers.{layer_idx}.mlp.{name}.weight"
            else:
                param_name = f"model.layers.{layer_idx}.self_attn.{name}.weight"

            if param_name not in mask_set:
                continue

            W = proj.weight
            mask = mask_set[param_name]
            bias = proj.bias.detach().float().cpu() if proj.bias is not None else None

            if scale_mode == "row":
                T, gamma, cos = ternarize_per_row(W, mask)
                tl = TernaryLinearRow(T, gamma, bias).to(device)
            else:
                T, gamma, cos = ternarize_per_group(W, mask, group_size)
                tl = TernaryLinearGrouped(T, gamma, group_size, bias).to(device)

            cosines[name] = cos
            setattr(parent, name, tl)
            del proj
            gc.collect()

    return cosines


# ═══════════════════════════════════════════════════════════════════════
# Compounding sweep
# ═══════════════════════════════════════════════════════════════════════


@torch.no_grad()
def collect_float_hidden_states(model, tokenizer, probe_texts, device):
    """Float reference hidden states."""
    encoded = tokenizer(
        probe_texts, return_tensors="pt", padding=True,
        truncation=True, max_length=128,
    ).to(device)
    outputs = model(
        input_ids=encoded["input_ids"],
        attention_mask=encoded["attention_mask"],
        output_hidden_states=True,
    )
    mask = encoded["attention_mask"].bool()
    return [hs[mask].float().cpu() for hs in outputs.hidden_states]


PROBE_TEXTS = [
    "The capital of France is Paris, located along the Seine river.",
    "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "(λx. λy. x y) (λz. z) reduces to (λy. y) which is the identity combinator I.",
    "Quantum entanglement occurs when two particles become correlated.",
    "The derivative of sin(x) is cos(x), a fundamental result in calculus.",
    "Once upon a time in a small village there lived an old clockmaker.",
    "SELECT name, age FROM users WHERE age > 18 ORDER BY name;",
    "日本の首都は東京で、世界最大の都市圏の一つです。",
]


@torch.no_grad()
def run_compounding_sweep(config_name, tokenizer, mask_set, scale_mode,
                          group_size, device, model_name):
    """Full compounding sweep for one configuration."""
    from transformers import AutoModelForCausalLM

    log(f"\n{'═' * 78}")
    log(f"  COMPOUNDING: {config_name}")
    log(f"{'═' * 78}")

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16, device_map=device,
    )
    model.eval()

    # Float reference
    log(f"  Collecting float reference...")
    float_hidden = collect_float_hidden_states(model, tokenizer, PROBE_TEXTS, device)
    n_layers = len(float_hidden) - 1
    log(f"  Reference: {n_layers} layers, {float_hidden[0].shape[0]} tokens")

    layers = get_model_layers(model)
    sweep = []

    for depth in range(n_layers):
        layer_cos = ternarize_layer(
            layers[depth], depth, mask_set, scale_mode, group_size, device,
        )
        mean_wcos = np.mean(list(layer_cos.values())) if layer_cos else 0

        # Forward to get hidden states
        encoded = tokenizer(
            PROBE_TEXTS, return_tensors="pt", padding=True,
            truncation=True, max_length=128,
        ).to(device)
        outputs = model(
            input_ids=encoded["input_ids"],
            attention_mask=encoded["attention_mask"],
            output_hidden_states=True,
        )
        mask_tok = encoded["attention_mask"].bool()
        hs_ternary = outputs.hidden_states[depth + 1][mask_tok].float().cpu()
        hs_float = float_hidden[depth + 1]

        cos_per_token = F.cosine_similarity(hs_ternary, hs_float, dim=1)
        mean_cos = cos_per_token.mean().item()
        min_cos = cos_per_token.min().item()

        sweep.append({
            "depth": depth,
            "cumulative_cosine": mean_cos,
            "cumulative_cosine_min": min_cos,
            "weight_cosine_mean": mean_wcos,
        })

        marker = ""
        if depth % 5 == 0 or depth == n_layers - 1:
            marker = f"  wcos={mean_wcos:.4f}"
        log(f"  L{depth:>2}: cos={mean_cos:.6f}  min={min_cos:.6f}{marker}")

        gc.collect()
        if device == "mps":
            torch.mps.empty_cache()

    del model
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()

    return sweep


# ═══════════════════════════════════════════════════════════════════════
# PPL evaluation
# ═══════════════════════════════════════════════════════════════════════


def load_eval_texts():
    try:
        from datasets import load_dataset
        ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
        texts = [t for t in ds["text"] if t.strip()]
        log(f"  Loaded WikiText-2 test: {len(texts)} lines")
        return texts
    except Exception as e:
        log(f"  WikiText-2 unavailable ({e})")
        return None


@torch.no_grad()
def evaluate_perplexity(model, tokenizer, texts, max_length=512, stride=256,
                        max_eval_tokens=16384, device="mps"):
    log(f"  Evaluating PPL...")
    t0 = time.time()

    full_text = "\n\n".join(texts)
    encodings = tokenizer(full_text, return_tensors="pt", truncation=False)
    input_ids = encodings.input_ids[0]
    seq_len = min(input_ids.size(0), max_eval_tokens)
    input_ids = input_ids[:seq_len]
    log(f"  Tokens: {seq_len:,}")

    nlls = []
    n_tokens = 0

    for begin_loc in range(0, seq_len - 1, stride):
        end_loc = min(begin_loc + max_length, seq_len)
        score_begin = stride if begin_loc > 0 else 0
        input_chunk = input_ids[begin_loc:end_loc].unsqueeze(0).to(device)
        outputs = model(input_chunk)
        shift_logits = outputs.logits[0, score_begin:-1, :].contiguous()
        shift_labels = input_chunk[0, score_begin + 1:].contiguous()
        loss = F.cross_entropy(shift_logits, shift_labels, reduction="sum")
        nlls.append(loss.float().cpu().item())
        n_tokens += shift_labels.size(0)
        if end_loc >= seq_len:
            break

    mean_nll = sum(nlls) / n_tokens
    ppl = math.exp(min(mean_nll, 20))  # cap to avoid overflow
    elapsed = time.time() - t0
    log(f"  PPL: {ppl:.2f}  NLL: {mean_nll:.4f}  ({n_tokens:,} tokens, {elapsed:.1f}s)")
    return {"perplexity": ppl, "nll": mean_nll, "n_tokens": n_tokens}


@torch.no_grad()
def run_ppl_test(config_name, tokenizer, mask_set, scale_mode,
                 group_size, device, model_name, eval_texts):
    """Full-model PPL for one configuration."""
    from transformers import AutoModelForCausalLM

    log(f"\n{'═' * 78}")
    log(f"  PPL: {config_name}")
    log(f"{'═' * 78}")

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16, device_map=device,
    )
    model.eval()

    layers = get_model_layers(model)
    n_layers = len(layers)
    all_cosines = []

    for i in range(n_layers):
        lcos = ternarize_layer(layers[i], i, mask_set, scale_mode, group_size, device)
        mean_cos = np.mean(list(lcos.values())) if lcos else 0
        all_cosines.append(mean_cos)
        if i % 6 == 0 or i == n_layers - 1:
            log(f"    L{i:>2} weight_cos={mean_cos:.5f}")

    mean_wcos = np.mean(all_cosines)
    log(f"  Mean weight cosine: {mean_wcos:.5f}")

    ppl_result = evaluate_perplexity(model, tokenizer, eval_texts, device=device)

    del model
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()

    return {
        "ppl": ppl_result["perplexity"],
        "nll": ppl_result["nll"],
        "mean_weight_cosine": float(mean_wcos),
        "per_layer_cosines": [float(c) for c in all_cosines],
    }


# ═══════════════════════════════════════════════════════════════════════
# Size estimation
# ═══════════════════════════════════════════════════════════════════════


def estimate_sizes(n_params: int, n_layers: int, d_model: int, d_ff: int,
                   group_size: int):
    """Estimate storage for each configuration."""
    # Per-row: 1 float32 per output row
    # FFN: gate/up = (d_ff, d_model), down = (d_model, d_ff)
    # Attn: q/k/v/o = (d_model, d_model) approximately
    ffn_rows = n_layers * (d_ff + d_ff + d_model)  # gate + up + down
    attn_rows = n_layers * 4 * d_model  # q, k, v, o
    total_rows = ffn_rows + attn_rows

    # Per-group: 1 float32 per (output_row, group)
    ffn_groups = n_layers * (
        d_ff * ((d_model + group_size - 1) // group_size) * 2 +  # gate, up
        d_model * ((d_ff + group_size - 1) // group_size)         # down
    )
    attn_groups = n_layers * 4 * d_model * ((d_model + group_size - 1) // group_size)
    total_groups = ffn_groups + attn_groups

    ternary_bytes = n_params * math.log2(3) / 8
    row_gamma_bytes = total_rows * 4
    group_gamma_bytes = total_groups * 4

    log(f"\n  Size estimates:")
    log(f"    Ternary bitmask:        {ternary_bytes / 1e9:.3f} GB  ({n_params:,} params × 1.58 bits)")
    log(f"    Per-row gamma:          {row_gamma_bytes / 1e6:.1f} MB  ({total_rows:,} rows × 4B)")
    log(f"    Per-group({group_size}) gamma:    {group_gamma_bytes / 1e6:.1f} MB  ({total_groups:,} groups × 4B)")
    log(f"    Ternary + row gamma:    {(ternary_bytes + row_gamma_bytes) / 1e9:.3f} GB")
    log(f"    Ternary + group gamma:  {(ternary_bytes + group_gamma_bytes) / 1e9:.3f} GB")
    log(f"    Bits/param (row):       {(ternary_bytes + row_gamma_bytes) * 8 / n_params:.2f}")
    log(f"    Bits/param (group):     {(ternary_bytes + group_gamma_bytes) * 8 / n_params:.2f}")
    log(f"    Original fp16:          {n_params * 2 / 1e9:.3f} GB")


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="DVD Group Scale Test")
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--zero-rate", type=float, default=0.50)
    parser.add_argument("--group-size", type=int, default=32)
    parser.add_argument("--skip-compounding", action="store_true",
                        help="Skip compounding sweep (run PPL only)")
    parser.add_argument("--skip-ppl", action="store_true",
                        help="Skip PPL evaluation")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log(f"╔{'═' * 76}╗")
    log(f"║  DVD GROUP SCALE — Ternary Bitmasks + Per-Group Gradient Scaling{' ' * 10}║")
    log(f"║  Model: {args.model:<67}║")
    log(f"║  Group size: {args.group_size:<62}║")
    log(f"║  Zero rate: {args.zero_rate:<63.0%}║")
    log(f"╚{'═' * 76}╝")

    t_start = time.time()

    # ── Load gradient maps from DVD stamp test ──
    grad_map_path = DVD_DIR / "gradient_maps.pt"
    if not grad_map_path.exists():
        log(f"  ERROR: {grad_map_path} not found. Run dvd_stamp_test.py first.")
        sys.exit(1)

    log(f"\n  Loading gradient maps from {grad_map_path}...")
    grad_save = torch.load(grad_map_path, map_location="cpu", weights_only=True)
    grad_maps = {name: g.float() for name, g in grad_save.items()}
    log(f"  Loaded {len(grad_maps)} gradient maps")

    # ── Load model for mask building ──
    log(f"\n  Loading model for mask construction...")
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.model, padding_side="left")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.float16, device_map=args.device,
    )
    model.eval()

    # ── Build masks ──
    masks = build_masks(model, grad_maps, zero_rate=args.zero_rate)
    log(f"  Built masks: magnitude ({len(masks['magnitude'])} tensors), "
        f"gradient ({len(masks['gradient'])} tensors)")

    # ── Quick per-layer weight cosine comparison (4 configs) ──
    log(f"\n{'═' * 78}")
    log(f"  PER-LAYER WEIGHT COSINE — 4 configurations")
    log(f"{'═' * 78}")
    log(f"  {'L':>3}  {'Mag+Row':>9} {'Grad+Row':>9} {'Mag+Grp':>9} {'Grad+Grp':>9}")
    log(f"  {'─' * 3}  {'─' * 9} {'─' * 9} {'─' * 9} {'─' * 9}")

    configs = [
        ("mag_row", "magnitude", "row"),
        ("grad_row", "gradient", "row"),
        ("mag_group", "magnitude", "group"),
        ("grad_group", "gradient", "group"),
    ]
    cosine_summary = {c[0]: [] for c in configs}
    layers = get_model_layers(model)
    n_layers = len(layers)

    for layer_idx in range(n_layers):
        cos_vals = {}
        for cfg_name, mask_name, scale_mode in configs:
            mask_set = masks[mask_name]
            layer_cosines = []
            for mod_name in TARGET_MODULES:
                if mod_name in TARGET_MODULES_FFN:
                    param_name = f"model.layers.{layer_idx}.mlp.{mod_name}.weight"
                    proj = getattr(layers[layer_idx].mlp, mod_name, None)
                else:
                    param_name = f"model.layers.{layer_idx}.self_attn.{mod_name}.weight"
                    proj = getattr(layers[layer_idx].self_attn, mod_name, None)

                if proj is None or param_name not in mask_set:
                    continue

                W = proj.weight
                mask = mask_set[param_name]

                if scale_mode == "row":
                    _, _, cos = ternarize_per_row(W, mask)
                else:
                    _, _, cos = ternarize_per_group(W, mask, args.group_size)
                layer_cosines.append(cos)

            mean_cos = np.mean(layer_cosines) if layer_cosines else 0
            cos_vals[cfg_name] = mean_cos
            cosine_summary[cfg_name].append(mean_cos)

        log(f"  {layer_idx:>3}  "
            f"{cos_vals['mag_row']:>9.5f} {cos_vals['grad_row']:>9.5f} "
            f"{cos_vals['mag_group']:>9.5f} {cos_vals['grad_group']:>9.5f}")

    log(f"\n  Summary:")
    for cfg_name, _, _ in configs:
        vals = cosine_summary[cfg_name]
        log(f"    {cfg_name:<12} mean={np.mean(vals):.6f}  "
            f"min={np.min(vals):.6f}  max={np.max(vals):.6f}")

    # ── Size estimate ──
    total_params = sum(p.numel() for n, p in model.named_parameters()
                       if any(m in n for m in TARGET_MODULES) and "weight" in n)
    estimate_sizes(total_params, n_layers, 4096, 12288, args.group_size)

    # Free model
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    # ── Compounding sweep ──
    if not args.skip_compounding:
        compounding = {}
        for cfg_name, mask_name, scale_mode in configs:
            compounding[cfg_name] = run_compounding_sweep(
                cfg_name, tokenizer, masks[mask_name], scale_mode,
                args.group_size, args.device, args.model,
            )

        # Comparison table
        log(f"\n{'═' * 78}")
        log(f"  COMPOUNDING COMPARISON — 4 Configurations")
        log(f"{'═' * 78}")
        log(f"  {'L':>3}  {'Mag+Row':>9} {'Grad+Row':>9} {'Mag+Grp':>9} {'Grad+Grp':>9}")
        log(f"  {'─' * 3}  {'─' * 9} {'─' * 9} {'─' * 9} {'─' * 9}")

        n = len(compounding["mag_row"])
        for i in range(n):
            vals = {c: compounding[c][i]["cumulative_cosine"] for c in compounding}
            log(f"  {i:>3}  "
                f"{vals['mag_row']:>9.6f} {vals['grad_row']:>9.6f} "
                f"{vals['mag_group']:>9.6f} {vals['grad_group']:>9.6f}")

        log(f"\n  FINAL (layer {n-1}):")
        for c in ["mag_row", "grad_row", "mag_group", "grad_group"]:
            v = compounding[c][-1]["cumulative_cosine"]
            log(f"    {c:<14} cos={v:.6f}")

        with open(RESULTS_DIR / "compounding.json", "w") as f:
            json.dump(compounding, f, indent=2)
    else:
        log("\n  [Skipping compounding sweep]")
        compounding = None

    # ── PPL evaluation ──
    if not args.skip_ppl:
        eval_texts = load_eval_texts()
        if eval_texts is None:
            log("  Cannot run PPL without eval texts")
            ppl_results = None
        else:
            ppl_results = {}
            for cfg_name, mask_name, scale_mode in configs:
                ppl_results[cfg_name] = run_ppl_test(
                    cfg_name, tokenizer, masks[mask_name], scale_mode,
                    args.group_size, args.device, args.model, eval_texts,
                )

            log(f"\n{'═' * 78}")
            log(f"  PERPLEXITY COMPARISON — 4 Configurations")
            log(f"{'═' * 78}")
            log(f"  {'Config':<14} {'PPL':>12}  {'NLL':>8}  {'Weight cos':>10}")
            log(f"  {'─' * 14} {'─' * 12}  {'─' * 8}  {'─' * 10}")
            for cfg_name, _, _ in configs:
                r = ppl_results[cfg_name]
                log(f"  {cfg_name:<14} {r['ppl']:>12.2f}  {r['nll']:>8.4f}  "
                    f"{r['mean_weight_cosine']:>10.5f}")
    else:
        log("\n  [Skipping PPL evaluation]")
        ppl_results = None

    # ── Save all results ──
    all_results = {
        "config": {
            "model": args.model,
            "device": args.device,
            "zero_rate": args.zero_rate,
            "group_size": args.group_size,
        },
        "weight_cosines": {k: [float(v) for v in vals]
                          for k, vals in cosine_summary.items()},
        "compounding": compounding,
        "ppl": ppl_results,
        "elapsed_total": time.time() - t_start,
    }
    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    elapsed = time.time() - t_start
    log(f"\n{'═' * 78}")
    log(f"  COMPLETE — {elapsed:.0f}s total")
    log(f"  Results: {RESULTS_DIR}/")
    log(f"{'═' * 78}")


if __name__ == "__main__":
    main()
