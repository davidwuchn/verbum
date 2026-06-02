#!/usr/bin/env python3
"""Diagnose where ternary model diverges from float16.

Runs BOTH models on the same input and compares hidden states at
every layer boundary. Identifies the compounding error curve.

Also checks: what if we only ternarize FFN? Only attention? Single layer?

Usage:
  uv run python3 scripts/experiments/diagnose_ternary.py --model Qwen/Qwen3-8B

License: MIT
"""

from __future__ import annotations

import argparse
import copy
import gc
import math
import os
import sys
import time
from pathlib import Path

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# Import from our ternarization script
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from full_ternarize import (
    TernaryLinear, ternarize_linear, get_model_layers,
    WEIGHT_NAMES_FFN, WEIGHT_NAMES_ATTN, log,
)


def cosine_sim(a: torch.Tensor, b: torch.Tensor) -> float:
    """Cosine similarity between two tensors (flattened)."""
    a_flat = a.flatten().float()
    b_flat = b.flatten().float()
    return F.cosine_similarity(a_flat.unsqueeze(0), b_flat.unsqueeze(0)).item()


def rmse_ratio(a: torch.Tensor, b: torch.Tensor) -> float:
    """RMSE of difference relative to norm of a."""
    diff = (a.float() - b.float())
    return (diff.pow(2).mean().sqrt() / a.float().pow(2).mean().sqrt()).item()


@torch.no_grad()
def capture_all_hidden_states(model, input_ids: torch.Tensor, device: str) -> list[torch.Tensor]:
    """Run model and capture hidden states after every layer."""
    states = []
    layers = get_model_layers(model)

    # Hook every layer to capture output
    def make_hook(idx):
        def hook_fn(mod, inp, out):
            # Qwen3 decoder layer returns (hidden_states, ...) tuple
            h = out[0] if isinstance(out, tuple) else out
            states.append(h.detach().cpu())
        return hook_fn

    hooks = []
    for i, layer in enumerate(layers):
        hooks.append(layer.register_forward_hook(make_hook(i)))

    # Also capture embedding output (input to first layer)
    embed_state = []
    def embed_hook(mod, inp, out):
        embed_state.append(out.detach().cpu())

    # Find embedding module
    if hasattr(model, 'model') and hasattr(model.model, 'embed_tokens'):
        hooks.append(model.model.embed_tokens.register_forward_hook(embed_hook))

    input_ids = input_ids.to(device)
    model(input_ids)

    for h in hooks:
        h.remove()

    # Prepend embedding state
    if embed_state:
        return embed_state + states
    return states


def main():
    parser = argparse.ArgumentParser(description="Diagnose ternary divergence")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--zero-rate", type=float, default=0.35)
    args = parser.parse_args()

    if args.device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    else:
        device = args.device

    log(f"\n{'═' * 78}")
    log(f"  TERNARY DIVERGENCE DIAGNOSIS")
    log(f"{'═' * 78}")
    log(f"  Model: {args.model}, Device: {device}, Zero rate: {args.zero_rate:.0%}")

    # Load model
    log(f"\n  Loading model...")
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.float16,
        device_map=device if device != "mps" else None,
        trust_remote_code=True,
    )
    if device == "mps":
        model = model.to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    log(f"  Loaded: {n_layers} layers")

    # Test input
    test_text = (
        "The capital of France is Paris. The speed of light is approximately "
        "299792458 meters per second. Lambda calculus provides a formal system "
        "for expressing computation based on function abstraction."
    )
    input_ids = tokenizer(test_text, return_tensors="pt").input_ids
    log(f"  Test input: {input_ids.shape[1]} tokens")

    # ── Capture float16 hidden states ─────────────────────────────────
    log(f"\n  Capturing float16 hidden states...")
    float_states = capture_all_hidden_states(model, input_ids, device)
    log(f"  Captured {len(float_states)} states (embed + {len(float_states)-1} layers)")

    # ── Experiment 1: Ternarize ALL layers, measure divergence ────────
    log(f"\n{'═' * 78}")
    log(f"  EXPERIMENT 1: Full ternarization — layer-by-layer divergence")
    log(f"{'═' * 78}")

    # Ternarize one layer at a time, measure cumulative divergence
    layers = get_model_layers(model)

    log(f"\n  {'Layer':>5}  {'Cos(embed)':>11} {'Cos(prev)':>11} {'RMSE ratio':>11} "
        f"{'Norm ratio':>11} {'WCos min':>9}")
    log(f"  {'─'*5}  {'─'*11} {'─'*11} {'─'*11} {'─'*11} {'─'*9}")

    for layer_idx in range(n_layers):
        layer = layers[layer_idx]

        # Record worst weight cosine for this layer
        w_cosines = []

        # Ternarize FFN
        for name in WEIGHT_NAMES_FFN:
            proj = getattr(layer.mlp, name, None)
            if proj is None:
                continue
            tl, cos = ternarize_linear(proj, args.zero_rate)
            tl = tl.to(device)
            setattr(layer.mlp, name, tl)
            w_cosines.append(cos)
            del proj

        # Ternarize attention
        for name in WEIGHT_NAMES_ATTN:
            proj = getattr(layer.self_attn, name, None)
            if proj is None:
                continue
            tl, cos = ternarize_linear(proj, args.zero_rate)
            tl = tl.to(device)
            setattr(layer.self_attn, name, tl)
            w_cosines.append(cos)
            del proj

        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

        # Capture hidden states with layers 0..layer_idx ternarized
        ternary_states = capture_all_hidden_states(model, input_ids, device)

        # Compare at current layer's output (layer_idx+1 because of embed at 0)
        state_idx = layer_idx + 1
        if state_idx < len(float_states) and state_idx < len(ternary_states):
            cos_vs_float = cosine_sim(float_states[state_idx], ternary_states[state_idx])
            rmse = rmse_ratio(float_states[state_idx], ternary_states[state_idx])
            norm_f = float_states[state_idx].float().pow(2).mean().sqrt().item()
            norm_t = ternary_states[state_idx].float().pow(2).mean().sqrt().item()
            norm_ratio = norm_t / norm_f if norm_f > 0 else 0

            # Also compare embedding (should be identical)
            cos_embed = cosine_sim(float_states[0], ternary_states[0])

            min_wcos = min(w_cosines) if w_cosines else 0

            log(f"  {layer_idx:>5}  {cos_embed:>11.6f} {cos_vs_float:>11.6f} "
                f"{rmse:>11.6f} {norm_ratio:>11.4f} {min_wcos:>9.5f}")

        del ternary_states

    # ── Experiment 2: Single-layer ablation ───────────────────────────
    log(f"\n{'═' * 78}")
    log(f"  EXPERIMENT 2: Which single layer causes most damage?")
    log(f"{'═' * 78}")
    log(f"  (Reload needed — reloading float model...)")

    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.float16,
        device_map=device if device != "mps" else None,
        trust_remote_code=True,
    )
    if device == "mps":
        model = model.to(device)
    model.eval()

    layers = get_model_layers(model)

    log(f"\n  {'Layer':>5}  {'Out cos':>11}  {'NLL':>8}  {'PPL':>10}  {'WCos min':>9}")
    log(f"  {'─'*5}  {'─'*11}  {'─'*8}  {'─'*10}  {'─'*9}")

    # For each layer, ternarize ONLY that layer, measure output, then restore
    for layer_idx in range(n_layers):
        layer = layers[layer_idx]

        # Save original modules
        originals = {}
        w_cosines = []

        for name in WEIGHT_NAMES_FFN:
            proj = getattr(layer.mlp, name, None)
            if proj is None:
                continue
            originals[('mlp', name)] = proj
            tl, cos = ternarize_linear(proj, args.zero_rate)
            tl = tl.to(device)
            setattr(layer.mlp, name, tl)
            w_cosines.append(cos)

        for name in WEIGHT_NAMES_ATTN:
            proj = getattr(layer.self_attn, name, None)
            if proj is None:
                continue
            originals[('self_attn', name)] = proj
            tl, cos = ternarize_linear(proj, args.zero_rate)
            tl = tl.to(device)
            setattr(layer.self_attn, name, tl)
            w_cosines.append(cos)

        # Measure output divergence
        ternary_states = capture_all_hidden_states(model, input_ids, device)
        # Compare final layer output
        final_idx = len(float_states) - 1
        cos_final = cosine_sim(float_states[final_idx], ternary_states[final_idx])

        # Quick NLL on the test input
        input_on_device = input_ids.to(device)
        outputs = model(input_on_device)
        logits = outputs.logits
        shift_logits = logits[0, :-1, :].contiguous()
        shift_labels = input_on_device[0, 1:].contiguous()
        nll = F.cross_entropy(shift_logits, shift_labels).item()
        ppl = math.exp(min(nll, 20))  # cap to avoid overflow

        min_wcos = min(w_cosines) if w_cosines else 0

        log(f"  {layer_idx:>5}  {cos_final:>11.6f}  {nll:>8.4f}  {ppl:>10.2f}  {min_wcos:>9.5f}")

        # Restore original modules
        for (parent_name, attr_name), orig in originals.items():
            parent = getattr(layer, parent_name)
            setattr(parent, attr_name, orig)

        del ternary_states
        gc.collect()

    # ── Experiment 3: FFN only vs Attention only ──────────────────────
    log(f"\n{'═' * 78}")
    log(f"  EXPERIMENT 3: FFN-only vs Attention-only ternarization")
    log(f"{'═' * 78}")

    for mode_name, ffn_ternary, attn_ternary in [
        ("FFN only", True, False),
        ("Attention only", False, True),
    ]:
        # Reload
        del model
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

        model = AutoModelForCausalLM.from_pretrained(
            args.model, dtype=torch.float16,
            device_map=device if device != "mps" else None,
            trust_remote_code=True,
        )
        if device == "mps":
            model = model.to(device)
        model.eval()
        layers = get_model_layers(model)

        log(f"\n  --- {mode_name} ---")
        for layer_idx in range(n_layers):
            layer = layers[layer_idx]

            if ffn_ternary:
                for name in WEIGHT_NAMES_FFN:
                    proj = getattr(layer.mlp, name, None)
                    if proj is None:
                        continue
                    tl, _ = ternarize_linear(proj, args.zero_rate)
                    tl = tl.to(device)
                    setattr(layer.mlp, name, tl)
                    del proj

            if attn_ternary:
                for name in WEIGHT_NAMES_ATTN:
                    proj = getattr(layer.self_attn, name, None)
                    if proj is None:
                        continue
                    tl, _ = ternarize_linear(proj, args.zero_rate)
                    tl = tl.to(device)
                    setattr(layer.self_attn, name, tl)
                    del proj

            gc.collect()

        # Measure final divergence
        ternary_states = capture_all_hidden_states(model, input_ids, device)
        final_idx = len(float_states) - 1
        cos_final = cosine_sim(float_states[final_idx], ternary_states[final_idx])

        # NLL
        input_on_device = input_ids.to(device)
        outputs = model(input_on_device)
        logits = outputs.logits
        shift_logits = logits[0, :-1, :].contiguous()
        shift_labels = input_on_device[0, 1:].contiguous()
        nll = F.cross_entropy(shift_logits, shift_labels).item()
        ppl = math.exp(min(nll, 20))

        log(f"  Final hidden cos: {cos_final:.6f}")
        log(f"  NLL: {nll:.4f}, PPL: {ppl:.2f}")

        del ternary_states

    log(f"\n{'═' * 78}")
    log(f"  DIAGNOSIS COMPLETE")
    log(f"{'═' * 78}\n")


if __name__ == "__main__":
    main()
