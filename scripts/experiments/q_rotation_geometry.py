#!/usr/bin/env python3
"""Measure: what rotation does W_Q introduce at each layer?

The residual spirals through 325° over 36 layers. At each layer, W_Q
projects the residual into a query direction. The angular difference
between the residual and Q is the "learned rotation" — the reduction
instruction the head applies at that depth.

Questions:
  1. How much does W_Q rotate the residual? (angle between residual and Q)
  2. Is the rotation consistent across inputs? (structural vs data-dependent)
  3. Does the rotation follow the spiral? (correlate with depth)
  4. Do binding heads (H31@L27, H03@L30) have distinctive angles?
  5. What's the geometry between Q and K at each layer?
  6. Do heads at the same layer rotate to different angles? (angular diversity)

Usage:
  uv run python scripts/experiments/q_rotation_geometry.py --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


EVAL_TEXTS = [
    "The dog runs quickly across the field",
    "Water is essential for all living organisms",
    "The king ruled the kingdom wisely for decades",
    "She walked through the ancient forest alone",
    "The function returns the composition of its arguments",
    "Einstein discovered the theory of general relativity",
    "The committee approved the new environmental regulations",
    "Mozart composed his first symphony at age eight",
    "DNA carries genetic information in a double helix",
    "The capital of France is Paris",
    "If it rains tomorrow the ground will be wet",
    "The cat sat on the mat and watched the birds",
    "Democracy originated in ancient Athens",
    "The speed of light is approximately three hundred million meters per second",
    "To solve this equation first isolate the variable",
    "Climate change threatens ecosystems worldwide",
]


def get_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def get_attention_module(layer):
    """Get the self-attention module."""
    if hasattr(layer, 'self_attn'):
        return layer.self_attn
    raise RuntimeError("No attention module found")


def cosine_sim(a, b):
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-10 or nb < 1e-10:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def angle_rad(a, b):
    cos = np.clip(cosine_sim(a, b), -1, 1)
    return float(np.arccos(cos))


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  Q ROTATION GEOMETRY")
    print(f"  What rotation does W_Q introduce at each depth?")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print()

    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    print(f"  Loading {args.model}...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    d_model = model.config.hidden_size
    d_head = d_model // n_heads

    # Check for GQA (grouped query attention)
    n_kv_heads = getattr(model.config, 'num_key_value_heads', n_heads)
    print(f"  Layers: {n_layers}, Heads: {n_heads}, KV Heads: {n_kv_heads}")
    print(f"  d_model: {d_model}, d_head: {d_head}")

    layers = get_layers(model)

    # ── Phase 1: Capture residual + Q + K at every layer ──────────
    print(f"\n  Capturing residual, Q, K at all layers for {len(EVAL_TEXTS)} texts...")

    # We need: pre-attention residual, Q projection, K projection
    # Hook strategy: hook the attention input (residual) and manually compute Q, K

    all_results = []  # per text

    for ti, text in enumerate(EVAL_TEXTS):
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=64)
        inputs_dev = {k: v.to(args.device) for k, v in inputs.items()}

        # Capture attention inputs (post-layernorm, pre-projection)
        attn_inputs = {}
        handles = []

        for li, layer in enumerate(layers):
            # Hook the layer's input_layernorm to get the pre-attention residual
            # Or hook the attention module's pre-hook to get its actual input
            attn = get_attention_module(layer)

            def make_pre_hook(idx):
                def hook_fn(module, args, kwargs):
                    # Qwen3 passes hidden_states as first positional or keyword arg
                    if args:
                        x = args[0]
                    elif 'hidden_states' in kwargs:
                        x = kwargs['hidden_states']
                    else:
                        return
                    attn_inputs[idx] = x.detach().float().cpu()
                return hook_fn

            handles.append(attn.register_forward_pre_hook(make_pre_hook(li), with_kwargs=True))

        with torch.no_grad():
            model(**inputs_dev)

        for h in handles:
            h.remove()

        # Now compute Q and K manually using the weight matrices
        text_result = {"text": text, "layers": []}

        for li in range(n_layers):
            if li not in attn_inputs:
                continue

            attn = get_attention_module(layers[li])
            x = attn_inputs[li]  # (1, seq, d_model)

            # Get Q, K projection weights
            W_q = attn.q_proj.weight.detach().float().cpu()  # (n_heads*d_head, d_model)
            W_k = attn.k_proj.weight.detach().float().cpu()  # (n_kv_heads*d_head, d_model)

            # Compute Q and K
            Q = (x @ W_q.T)[0]  # (seq, n_heads*d_head)
            K = (x @ W_k.T)[0]  # (seq, n_kv_heads*d_head)
            residual = x[0]      # (seq, d_model)

            # Reshape Q into heads: (seq, n_heads, d_head)
            Q_heads = Q.reshape(-1, n_heads, d_head).numpy()
            K_heads = K.reshape(-1, n_kv_heads, d_head).numpy()
            res = residual.numpy()  # (seq, d_model)

            # For each head, measure the angle between residual and Q
            # Use mean-pooled vectors for stability
            res_mean = res.mean(axis=0)  # (d_model,)

            head_angles = []
            head_q_norms = []
            head_k_norms = []
            head_qk_angles = []

            for hi in range(n_heads):
                q_mean = Q_heads[:, hi, :].mean(axis=0)  # (d_head,)

                # The Q projection maps d_model → d_head, so we can't directly
                # compare angles in different spaces. Instead, measure:
                # 1. The angle between Q vectors of consecutive positions (Q diversity)
                # 2. The Q-K alignment per head
                # 3. The Q norm (how much W_Q amplifies)

                head_q_norms.append(float(np.linalg.norm(q_mean)))

                # Q-K alignment (using GQA mapping)
                ki = hi % n_kv_heads  # GQA: multiple Q heads share one K head
                k_mean = K_heads[:, ki, :].mean(axis=0)
                qk_angle = angle_rad(q_mean, k_mean)
                head_qk_angles.append(float(qk_angle))

            # Measure: how much does the FULL Q projection rotate the residual?
            # Project residual through W_q to get the full Q vector
            full_Q = (residual @ W_q.T).numpy()  # (seq, n_heads*d_head)
            full_K = (residual @ W_k.T).numpy()  # (seq, n_kv_heads*d_head)

            # Angle between full Q at consecutive sequence positions
            q_pos_angles = []
            for si in range(len(full_Q) - 1):
                a = angle_rad(full_Q[si], full_Q[si + 1])
                q_pos_angles.append(float(a))

            # Angle between residual directions at same position
            res_pos_angles = []
            for si in range(len(res) - 1):
                a = angle_rad(res[si], res[si + 1])
                res_pos_angles.append(float(a))

            # W_Q as a rotation: angle between input direction and output direction
            # For each position, compute angle(residual[pos], Q[pos]) in terms of
            # how much the direction changed (use normalized vectors in their respective spaces)
            # Since Q is in d_head space and residual is in d_model space, we measure
            # the COLUMN-SPACE rotation of W_q

            # Simpler: measure the singular values of W_q (per head)
            # If W_q is a pure rotation, all singular values = 1
            # If it scales, they'll vary
            head_svd_stats = []
            for hi in range(min(n_heads, 8)):  # sample 8 heads for SVD
                W_q_head = W_q[hi * d_head:(hi + 1) * d_head, :]  # (d_head, d_model)
                svd = np.linalg.svd(W_q_head.numpy(), compute_uv=False)
                head_svd_stats.append({
                    "head": hi,
                    "sv_max": float(svd[0]),
                    "sv_min": float(svd[-1]),
                    "sv_ratio": float(svd[0] / (svd[-1] + 1e-10)),
                    "sv_mean": float(svd.mean()),
                })

            text_result["layers"].append({
                "layer": li,
                "mean_qk_angle_deg": float(np.degrees(np.mean(head_qk_angles))),
                "std_qk_angle_deg": float(np.degrees(np.std(head_qk_angles))),
                "mean_q_norm": float(np.mean(head_q_norms)),
                "mean_q_pos_angle_deg": float(np.degrees(np.mean(q_pos_angles))) if q_pos_angles else 0,
                "mean_res_pos_angle_deg": float(np.degrees(np.mean(res_pos_angles))) if res_pos_angles else 0,
                "svd_stats": head_svd_stats,
            })

        all_results.append(text_result)
        if (ti + 1) % 4 == 0:
            print(f"    {ti+1}/{len(EVAL_TEXTS)} texts processed")

    # ── Aggregate across texts ────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  Results: Q-K angle and W_Q rotation per layer")
    print(f"{'='*70}")

    layer_qk_angles = {li: [] for li in range(n_layers)}
    layer_q_norms = {li: [] for li in range(n_layers)}
    layer_q_pos_angles = {li: [] for li in range(n_layers)}
    layer_res_pos_angles = {li: [] for li in range(n_layers)}
    layer_sv_ratios = {li: [] for li in range(n_layers)}

    for text_result in all_results:
        for lr in text_result["layers"]:
            li = lr["layer"]
            layer_qk_angles[li].append(lr["mean_qk_angle_deg"])
            layer_q_norms[li].append(lr["mean_q_norm"])
            layer_q_pos_angles[li].append(lr["mean_q_pos_angle_deg"])
            layer_res_pos_angles[li].append(lr["mean_res_pos_angle_deg"])
            if lr["svd_stats"]:
                layer_sv_ratios[li].append(np.mean([s["sv_ratio"] for s in lr["svd_stats"]]))

    print(f"\n  {'Layer':>5s}  {'QK_angle':>8s}  {'Q_norm':>7s}  {'Q_pos_∠':>8s}  {'Res_pos_∠':>9s}  {'SV_ratio':>8s}  Visual (QK angle)")
    print(f"  {'─'*5}  {'─'*8}  {'─'*7}  {'─'*8}  {'─'*9}  {'─'*8}  {'─'*35}")

    summary = []
    for li in range(n_layers):
        qk = np.mean(layer_qk_angles[li]) if layer_qk_angles[li] else 0
        qn = np.mean(layer_q_norms[li]) if layer_q_norms[li] else 0
        qp = np.mean(layer_q_pos_angles[li]) if layer_q_pos_angles[li] else 0
        rp = np.mean(layer_res_pos_angles[li]) if layer_res_pos_angles[li] else 0
        sv = np.mean(layer_sv_ratios[li]) if layer_sv_ratios[li] else 0

        bar = "█" * int(qk / 3)
        marker = ""
        if li == 26:
            marker = " ← L27 (verb→subject)"
        elif li == 29:
            marker = " ← L30 (object→verb)"
        elif li == 32:
            marker = " ← L33 (coreference)"

        print(f"  L{li:>2d}    {qk:>7.1f}°  {qn:>7.2f}  {qp:>7.1f}°  {rp:>8.1f}°  {sv:>8.1f}  {bar}{marker}")

        summary.append({
            "layer": li,
            "qk_angle_deg": float(qk),
            "q_norm": float(qn),
            "q_pos_angle_deg": float(qp),
            "res_pos_angle_deg": float(rp),
            "sv_ratio": float(sv),
        })

    # ── Analysis: Q rotation vs depth ─────────────────────────────
    print(f"\n{'='*70}")
    print(f"  Analysis: Q rotation patterns")
    print(f"{'='*70}")

    qk_angles = np.array([s["qk_angle_deg"] for s in summary])
    sv_ratios = np.array([s["sv_ratio"] for s in summary])
    q_pos = np.array([s["q_pos_angle_deg"] for s in summary])
    res_pos = np.array([s["res_pos_angle_deg"] for s in summary])

    # Q-K angle: does it correlate with depth?
    depths = np.arange(n_layers)
    corr_qk_depth = float(np.corrcoef(depths, qk_angles)[0, 1])
    print(f"\n  QK angle vs depth correlation: r = {corr_qk_depth:.3f}")

    # Q positional diversity vs residual positional diversity
    # If Q amplifies position-dependent differences, q_pos > res_pos
    ratio_qr = q_pos / (res_pos + 1e-10)
    print(f"  Q/Residual positional angle ratio: mean = {ratio_qr.mean():.3f}")
    print(f"    (>1 means Q amplifies positional differences, <1 means it suppresses)")

    # SV ratio: how much does W_Q distort?
    print(f"\n  W_Q singular value ratio (condition number):")
    print(f"    Mean across layers: {sv_ratios.mean():.1f}")
    print(f"    If ~1: W_Q is near-rotation (preserves geometry)")
    print(f"    If >>1: W_Q is a projection (collapses dimensions)")

    # Phase analysis
    phase1 = qk_angles[:12]
    phase2 = qk_angles[12:24]
    phase3 = qk_angles[24:]
    print(f"\n  QK angle by phase:")
    print(f"    Phase 1 (L0-L11, EXPAND→ORTHO):  mean={phase1.mean():.1f}° ± {phase1.std():.1f}°")
    print(f"    Phase 2 (L12-L23, OPTIMIZER):     mean={phase2.mean():.1f}° ± {phase2.std():.1f}°")
    print(f"    Phase 3 (L24-L35, BIND→EMIT):     mean={phase3.mean():.1f}° ± {phase3.std():.1f}°")

    # Binding layers specifically
    print(f"\n  Binding layer QK angles:")
    for li in [26, 27, 29, 30, 32, 33]:
        if li < n_layers:
            print(f"    L{li}: {qk_angles[li]:.1f}°  (SV ratio: {sv_ratios[li]:.1f})")

    # ── Load ternary PPL for correlation ──────────────────────────
    ternary_path = Path("results/multilayer-ternary-replace/Qwen_Qwen3-8B.json")
    if ternary_path.exists():
        with open(ternary_path) as f:
            ternary_data = json.load(f)
        scan = {s["layer"]: s["ppl_ratio"] for s in ternary_data.get("full_scan", [])}
        if scan:
            ppl = np.array([scan.get(li, 1.0) for li in range(n_layers)])
            corr_qk_ppl = float(np.corrcoef(qk_angles, ppl)[0, 1])
            corr_sv_ppl = float(np.corrcoef(sv_ratios, ppl)[0, 1])
            print(f"\n  Correlation with ternary PPL:")
            print(f"    QK angle vs PPL ratio: r = {corr_qk_ppl:.3f}")
            print(f"    SV ratio vs PPL ratio: r = {corr_sv_ppl:.3f}")
            print(f"    (positive = bigger angle/ratio → harder to ternarize)")

    # ── Save ──────────────────────────────────────────────────────
    out_dir = Path("results/q-rotation-geometry")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    with open(out_path, "w") as f:
        json.dump({
            "model": args.model,
            "n_layers": n_layers,
            "n_heads": n_heads,
            "n_kv_heads": n_kv_heads,
            "d_head": d_head,
            "summary": summary,
            "correlations": {
                "qk_angle_vs_depth": corr_qk_depth,
            },
        }, f, indent=2)

    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
