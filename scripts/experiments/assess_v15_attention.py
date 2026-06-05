"""Assess v15-td checkpoint attention quality at step 1500.

Key questions:
1. Are the Fibonacci stride attention patterns meaningful (not random/uniform)?
2. How much have the delta plates diverged from teacher? Is that good or bad?
3. Is the model actually using all 19 strides, or just a few?
4. What do the attention entropy distributions look like per stride?
5. Compare: does removing attention degrade outputs? (ablation)

The v15 model has TWO attention systems:
  - FibonacciStrideAttention (19 strides, Q·K with ±2 neighbor gathering)
    → TernaryLinear Q/K/V/O with delta plates (TD-trained signs)
  - FFN SwiGLU (shared plates per stack A/C)

The attention uses DeltaTernaryLinear: effective_weight = base ⊙ delta.
Delta starts at +1 (teacher signs) and TD flips ~4% to adapt to the
Fibonacci stride topology (teacher used full attention, student uses
strided windows).

License: MIT
"""

import sys
import json
import math
from pathlib import Path
from collections import defaultdict

import numpy as np
import mlx.core as mx
import mlx.nn as nn
from mlx.utils import tree_flatten, tree_unflatten

# ── Setup path ──────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "v15"))

from config import V15Config, STRIDES, WINDOW, NEIGHBOR_RADIUS
from v15model import V15Model
from attention import FibonacciStrideAttention, compute_expanded_indices
from ternary import (
    freeze_ternary_weights,
    restore_ternary,
    unpack_ternary_mlx,
)
from td_delta import (
    convert_to_delta,
    collect_delta_params,
    freeze_delta_architecture,
    DeltaTernaryLinear,
)
from data import ShardedDataLoader


def log(msg):
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════
# § 1  Load checkpoint
# ══════════════════════════════════════════════════════════════

def load_checkpoint(checkpoint_dir: str, cfg: V15Config) -> V15Model:
    """Load v15-td checkpoint into V15Model with delta plates."""
    ckpt = Path(checkpoint_dir)

    # Create model and set up delta architecture
    model = V15Model(cfg)
    freeze_ternary_weights(model)

    # Load extracted base plates first
    extracted_path = Path(cfg.extracted_model_path)
    if extracted_path.exists():
        saved = dict(mx.load(str(extracted_path)))
        flat_params = dict(tree_flatten(model.parameters()))
        n_loaded = 0

        proj_map = {"q": "q_proj", "k": "k_proj", "v": "v_proj", "o": "out_proj"}
        for layer_idx in range(cfg.n_strides):
            for ext_proj, model_proj in proj_map.items():
                model_key = f"shared_stride_stack.layers.{layer_idx}.{model_proj}.weight"
                if model_key not in flat_params:
                    continue
                ext_key = f"shared_stride_stack.layers.{layer_idx}.{ext_proj}"
                if ext_key not in saved:
                    continue
                arr = saved[ext_key]
                target_shape = flat_params[model_key].shape
                if arr.shape == target_shape:
                    flat_params[model_key] = mx.array(arr)
                    n_loaded += 1
                elif arr.shape[0] >= target_shape[0] and arr.shape[1] >= target_shape[1]:
                    flat_params[model_key] = mx.array(arr[:target_shape[0], :target_shape[1]])
                    n_loaded += 1

        # FFN plates
        ffn_map = {
            "stack_a.ffn.gate": "ffn_gate_plate_a.weight",
            "stack_a.ffn.up":   "ffn_key_plate_a.weight",
            "stack_a.ffn.down": "ffn_value_plate_a.weight",
            "stack_c.ffn.gate": "ffn_gate_plate_c.weight",
            "stack_c.ffn.up":   "ffn_key_plate_c.weight",
            "stack_c.ffn.down": "ffn_value_plate_c.weight",
        }
        for ext_key, model_key in ffn_map.items():
            if ext_key in saved and model_key in flat_params:
                if saved[ext_key].shape == flat_params[model_key].shape:
                    flat_params[model_key] = mx.array(saved[ext_key])
                    n_loaded += 1

        # Embeddings
        if "embed_tokens" in saved:
            emb_key = "embed.ternary_weight"
            if emb_key in flat_params:
                ext_emb = saved["embed_tokens"]
                if ext_emb.shape == flat_params[emb_key].shape:
                    flat_params[emb_key] = mx.array(ext_emb)
                    n_loaded += 1

        model.update(tree_unflatten(list(flat_params.items())))
        mx.eval(model.parameters())
        restore_ternary(model)
        freeze_ternary_weights(model)
        log(f"  Base plates loaded: {n_loaded} arrays")

    # Convert attention to delta architecture
    converted = convert_to_delta(
        model,
        include_prefixes=("shared_stride_stack",),
    )
    freeze_delta_architecture(model)
    freeze_ternary_weights(model)
    log(f"  Delta architecture: {len(converted)} modules")

    # Now load the trained checkpoint weights on top
    model_path = ckpt / "model.npz"
    if model_path.exists():
        saved_model = dict(mx.load(str(model_path)))
        flat_params = dict(tree_flatten(model.parameters()))
        n_loaded = 0
        n_skipped = 0
        for key, val in saved_model.items():
            if key in flat_params:
                if val.shape == flat_params[key].shape:
                    flat_params[key] = val
                    n_loaded += 1
                else:
                    n_skipped += 1
        model.update(tree_unflatten(list(flat_params.items())))
        mx.eval(model.parameters())
        log(f"  Checkpoint weights loaded: {n_loaded} arrays, {n_skipped} skipped")

    # Load delta plates
    delta_path = ckpt / "delta_plates.npz"
    if delta_path.exists():
        delta_data = dict(mx.load(str(delta_path)))
        delta_modules = collect_delta_params(model)
        n_delta_loaded = 0
        for path, dtl in delta_modules:
            delta_key = path.replace(".", "_") + "_delta_packed"
            if delta_key in delta_data:
                dtl.delta_weight = delta_data[delta_key]
                mx.eval(dtl.delta_weight)
                n_delta_loaded += 1
        log(f"  Delta plates loaded: {n_delta_loaded}")

    return model


# ══════════════════════════════════════════════════════════════
# § 2  Attention pattern analysis
# ══════════════════════════════════════════════════════════════

def analyze_attention_patterns(model: V15Model, input_ids: mx.array, cfg: V15Config):
    """Run forward pass and capture attention patterns from each stride layer.

    For each of the 19 FibonacciStrideAttention layers:
    - Compute Q, K, V from the current residual stream state
    - Compute attention scores with HPE and decay bias
    - Measure: entropy, sparsity, max attention weight, effective positions
    """
    B, L = input_ids.shape
    d = cfg.d_model

    # Get residual stream at input to the stride stack
    positions = mx.arange(L)
    x = model.embed_norm(model.embed(input_ids) + model.pos_embed(positions))
    mx.eval(x)

    # Now run through stack_a to get x_a, then we can probe the stride stack
    # But the stacks use the shared_stride_stack internally...
    # Let's just probe the attention layers directly by running forward
    # through the shared stride stack one layer at a time.

    stride_stack = model.shared_stride_stack
    results = []

    # We need to intercept the attention computation in each layer.
    # Each layer is a FibonacciStrideAttention. Let's hook into it.

    x_current = x  # Start with embedded input

    for layer_idx, layer in enumerate(stride_stack.layers):
        stride = layer.stride
        n_heads = layer.n_heads
        d_head = layer.d_head
        W_eff = layer.w_eff

        # Ensure indices are computed
        layer._ensure_indices(L)
        indices = layer._cached_indices
        valid = layer._cached_valid
        log_distances = layer._cached_log_distances

        # Compute Q, K, V
        x_norm = layer.norm(x_current)
        q_in = x_norm
        for mirror in layer.q_mirrors:
            q_in = mirror(q_in)

        Q = layer.q_proj(q_in).reshape(B, L, n_heads, d_head)
        K = (layer.k_proj(x_norm) + layer.k_bias).reshape(B, L, n_heads, d_head)
        V = (layer.v_proj(x_norm) + layer.v_bias).reshape(B, L, n_heads, d_head)

        # Gather K, V
        GD = n_heads * d_head
        K_flat = K.reshape(B, L, GD)
        V_flat = V.reshape(B, L, GD)
        idx = indices.reshape(1, L * W_eff, 1)
        idx = mx.broadcast_to(idx, (B, L * W_eff, GD))
        K_gathered = mx.take_along_axis(K_flat, idx, axis=1).reshape(B, L, W_eff, n_heads, d_head)

        # HPE rotation
        from attention import apply_hpe_rotation, _N_EIGEN_PAIRS
        Q_r = Q.transpose(0, 2, 1, 3)
        _, K_gathered_rot = apply_hpe_rotation(
            Q_r, K_gathered, log_distances,
            n_pairs=_N_EIGEN_PAIRS,
            freq_scale=layer.hpe_freq_scale,
        )

        # Attention scores
        K_r = K_gathered_rot.transpose(0, 3, 1, 2, 4)
        attn = (Q_r[:, :, :, None, :] * K_r).sum(axis=-1) * layer.scale

        # Decay bias
        from attention import _ALPHA
        decay_bias = -(_ALPHA * log_distances)
        attn = attn + decay_bias[None, None, :, :]

        # Mask
        valid_mask = valid[None, None, :, :]
        attn = mx.where(valid_mask, attn, mx.array(float("-inf")))
        attn = mx.clip(attn, -65.0, 65.0)
        attn_weights = mx.softmax(attn, axis=-1)
        mx.eval(attn_weights)

        # Metrics
        attn_np = np.array(attn_weights[0])  # (H, L, W_eff)
        valid_np = np.array(valid)  # (L, W_eff)

        # Per-head metrics
        head_metrics = []
        for h in range(n_heads):
            head_attn = attn_np[h]  # (L, W_eff)

            # Entropy per position, then average
            entropies = []
            max_weights = []
            eff_positions = []
            for pos in range(L):
                w = head_attn[pos]
                v = valid_np[pos]
                w_valid = w[v > 0]
                if len(w_valid) == 0 or w_valid.sum() < 1e-8:
                    continue
                w_valid = w_valid / (w_valid.sum() + 1e-12)
                # Entropy
                e = -np.sum(w_valid * np.log(w_valid + 1e-12))
                entropies.append(e)
                max_weights.append(float(w_valid.max()))
                # Effective positions
                eff_pos = np.exp(e)
                eff_positions.append(eff_pos)

            head_metrics.append({
                "head": h,
                "mean_entropy": float(np.mean(entropies)) if entropies else 0.0,
                "mean_max_weight": float(np.mean(max_weights)) if max_weights else 0.0,
                "mean_eff_pos": float(np.mean(eff_positions)) if eff_positions else 0.0,
                "min_max_weight": float(np.min(max_weights)) if max_weights else 0.0,
            })

        # Overall layer metrics
        all_entropies = [m["mean_entropy"] for m in head_metrics]
        all_max_wts = [m["mean_max_weight"] for m in head_metrics]
        all_eff_pos = [m["mean_eff_pos"] for m in head_metrics]

        results.append({
            "layer_idx": layer_idx,
            "stride": stride,
            "n_valid_positions": int(valid_np.sum(axis=1).mean()),
            "mean_entropy": float(np.mean(all_entropies)),
            "std_entropy": float(np.std(all_entropies)),
            "mean_max_weight": float(np.mean(all_max_wts)),
            "mean_eff_pos": float(np.mean(all_eff_pos)),
            "head_metrics": head_metrics,
        })

        # Run the full layer forward to advance the residual stream
        x_current = layer(x_current)
        mx.eval(x_current)

    return results


# ══════════════════════════════════════════════════════════════
# § 3  Delta plate divergence analysis
# ══════════════════════════════════════════════════════════════

def analyze_delta_divergence(model: V15Model):
    """Analyze how much delta plates have diverged from teacher per stride/projection."""
    delta_modules = collect_delta_params(model)

    per_layer = defaultdict(dict)
    for path, dtl in delta_modules:
        stats = dtl.delta_stats()
        # Parse: shared_stride_stack.layers.{i}.{proj}.weight
        parts = path.split(".")
        layer_idx = int(parts[2])
        proj = parts[3]  # q_proj, k_proj, v_proj, out_proj
        per_layer[layer_idx][proj] = {
            "flip_frac": stats["flip_frac"],
            "keep_frac": stats["keep_frac"],
            "block_frac": stats["block_frac"],
            "changed_frac": stats["changed_frac"],
        }

    return dict(per_layer)


# ══════════════════════════════════════════════════════════════
# § 4  Loss comparison: full model vs attention-zeroed
# ══════════════════════════════════════════════════════════════

def eval_loss(model: V15Model, data_loader, n_batches: int = 5) -> float:
    """Evaluate CE loss on a few batches."""
    losses = []
    for i in range(n_batches):
        ids_np, tgts_np = next(data_loader)
        ids = mx.array(ids_np)
        tgts = mx.array(tgts_np)
        logits, loss = model(ids, tgts)
        mx.eval(logits, loss)
        losses.append(float(loss.item()))
    return sum(losses) / len(losses) if losses else float("nan")


# ══════════════════════════════════════════════════════════════
# § 5  Generation test
# ══════════════════════════════════════════════════════════════

def generate_sample(model: V15Model, cfg: V15Config, prompt_ids: mx.array, max_tokens: int = 32):
    """Simple greedy generation."""
    tokens = list(prompt_ids[0].tolist()) if prompt_ids.ndim > 1 else list(prompt_ids.tolist())
    for _ in range(max_tokens):
        input_ids = mx.array([tokens[-cfg.max_seq_len:]])
        logits, _ = model(input_ids)
        mx.eval(logits)
        next_token = int(mx.argmax(logits[0, -1], axis=-1).item())
        tokens.append(next_token)
        if next_token == 0:  # EOS
            break
    return tokens


# ══════════════════════════════════════════════════════════════
# § 6  Main
# ══════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Assess v15-td checkpoint attention")
    parser.add_argument("--checkpoint", default="checkpoints/v15-td/step_001500")
    parser.add_argument("--extracted", default="checkpoints/v15-extracted/model.npz/model.npz")
    parser.add_argument("--data-dir", default="/Users/mwhitford/data/fractal-bitnet/shards-qwen36")
    parser.add_argument("--n-eval", type=int, default=5, help="Batches for loss eval")
    parser.add_argument("--seq-len", type=int, default=512, help="Sequence length for attention analysis")
    args = parser.parse_args()

    cfg = V15Config(extracted_model_path=args.extracted)

    log("=" * 72)
    log("v15-td Attention Assessment")
    log("=" * 72)

    # ── Load ──────────────────────────────────────────────────
    log(f"\n§ 1  Loading checkpoint: {args.checkpoint}")
    model = load_checkpoint(args.checkpoint, cfg)

    # ── Delta divergence ──────────────────────────────────────
    log(f"\n§ 2  Delta plate divergence from teacher")
    delta_div = analyze_delta_divergence(model)
    log(f"  {'Layer':>5s} {'Stride':>6s} | {'Q flip%':>7s} {'K flip%':>7s} {'V flip%':>7s} {'O flip%':>7s} | {'Mean':>5s}")
    total_flips = []
    for layer_idx in sorted(delta_div.keys()):
        projs = delta_div[layer_idx]
        stride = STRIDES[layer_idx] if layer_idx < len(STRIDES) else "?"
        q_flip = projs.get("q_proj", {}).get("flip_frac", 0) * 100
        k_flip = projs.get("k_proj", {}).get("flip_frac", 0) * 100
        v_flip = projs.get("v_proj", {}).get("flip_frac", 0) * 100
        o_flip = projs.get("out_proj", {}).get("flip_frac", 0) * 100
        mean_flip = (q_flip + k_flip + v_flip + o_flip) / 4
        total_flips.append(mean_flip)
        log(f"  {layer_idx:5d} {stride:6} | {q_flip:6.2f}% {k_flip:6.2f}% {v_flip:6.2f}% {o_flip:6.2f}% | {mean_flip:5.2f}%")

    log(f"\n  Overall: mean flip = {np.mean(total_flips):.2f}%  min = {np.min(total_flips):.2f}%  max = {np.max(total_flips):.2f}%")
    log(f"  Interpretation: ~{np.mean(total_flips):.1f}% of teacher signs flipped → attention is adapting to stride topology")

    # ── Attention pattern analysis ────────────────────────────
    log(f"\n§ 3  Attention pattern analysis (seq_len={args.seq_len})")
    log(f"  Running forward pass through 19 stride layers...")

    # Create a sample input from eval data
    eval_loader = ShardedDataLoader(
        args.data_dir, seq_len=args.seq_len, batch_size=1,
        shard_start=54, shard_end=60, seed=123,
    )
    sample_ids, sample_tgts = next(eval_loader)
    sample_ids_mx = mx.array(sample_ids)

    attn_results = analyze_attention_patterns(model, sample_ids_mx, cfg)

    log(f"\n  {'Layer':>5s} {'Stride':>6s} {'#Valid':>6s} | {'Entropy':>8s} {'MaxWt':>7s} {'EffPos':>7s} | {'Interpretation'}")
    log(f"  {'─'*5} {'─'*6} {'─'*6}   {'─'*8} {'─'*7} {'─'*7}   {'─'*30}")

    for r in attn_results:
        stride = r["stride"]
        n_valid = r["n_valid_positions"]
        ent = r["mean_entropy"]
        max_wt = r["mean_max_weight"]
        eff = r["mean_eff_pos"]

        # Interpretation
        if ent < 0.5:
            interp = "VERY SPARSE (near-deterministic)"
        elif ent < 1.0:
            interp = "SPARSE (1-2 positions)"
        elif ent < 2.0:
            interp = "MODERATE (2-7 positions)"
        elif ent < 3.0:
            interp = "BROAD (7-20 positions)"
        else:
            interp = "DIFFUSE (near-uniform)"

        # Flag if attention seems dead (max weight near 1/n_valid)
        if n_valid > 0 and max_wt < 1.5 / n_valid:
            interp += " ⚠ NEAR-UNIFORM"

        log(f"  {r['layer_idx']:5d} {stride:6d} {n_valid:6d} | {ent:8.3f} {max_wt:7.3f} {eff:7.1f} | {interp}")

    # ── Per-head detail for stride-1 (local) and stride-34 (long-range) ──
    for target_stride in [1, 34]:
        target_layer = None
        for r in attn_results:
            if r["stride"] == target_stride:
                target_layer = r
                break
        if target_layer is None:
            continue

        log(f"\n  Per-head detail for stride={target_stride} (layer {target_layer['layer_idx']}):")
        log(f"  {'Head':>5s} | {'Entropy':>8s} {'MaxWt':>7s} {'EffPos':>7s}")
        for hm in target_layer["head_metrics"]:
            log(f"  {hm['head']:5d} | {hm['mean_entropy']:8.3f} {hm['mean_max_weight']:7.3f} {hm['mean_eff_pos']:7.1f}")

    # ── Summary statistics ────────────────────────────────────
    all_ent = [r["mean_entropy"] for r in attn_results]
    all_eff = [r["mean_eff_pos"] for r in attn_results]
    all_max = [r["mean_max_weight"] for r in attn_results]

    log(f"\n§ 4  Summary")
    log(f"  Entropy across layers:  mean={np.mean(all_ent):.3f}  std={np.std(all_ent):.3f}  range=[{np.min(all_ent):.3f}, {np.max(all_ent):.3f}]")
    log(f"  Eff positions:          mean={np.mean(all_eff):.1f}   range=[{np.min(all_eff):.1f}, {np.max(all_eff):.1f}]")
    log(f"  Max attention weight:   mean={np.mean(all_max):.3f}  range=[{np.min(all_max):.3f}, {np.max(all_max):.3f}]")

    # Key indicators
    n_sparse = sum(1 for e in all_ent if e < 1.0)
    n_moderate = sum(1 for e in all_ent if 1.0 <= e < 2.5)
    n_broad = sum(1 for e in all_ent if e >= 2.5)
    log(f"\n  Layer distribution: {n_sparse} sparse + {n_moderate} moderate + {n_broad} broad/diffuse = {len(all_ent)} total")

    # ── Is attention WORKING? ─────────────────────────────────
    log(f"\n§ 5  Assessment: Is the attention working?")

    # Criteria:
    # 1. Entropy should vary across layers (not all the same)
    # 2. Some layers should be sparse (entropy < 1.5)
    # 3. Max weights should be > 0.2 on average (not uniform)
    # 4. Different strides should have different patterns
    # 5. Delta divergence should be moderate (2-8%) — too low = not adapting, too high = unstable

    issues = []
    findings = []

    ent_std = np.std(all_ent)
    if ent_std < 0.1:
        issues.append(f"All layers have nearly identical entropy (std={ent_std:.3f}) — attention may be uniform")
    else:
        findings.append(f"Entropy varies across layers (std={ent_std:.3f}) — different strides serve different roles")

    if np.mean(all_max) < 0.15:
        issues.append(f"Average max attention weight is very low ({np.mean(all_max):.3f}) — attention may be near-uniform")
    else:
        findings.append(f"Average max attention weight is {np.mean(all_max):.3f} — attention is selective")

    if n_sparse == 0:
        issues.append("No sparse layers found — model may not be learning routing")
    else:
        findings.append(f"{n_sparse}/19 layers are sparse (entropy < 1.0) — model is learning selective routing")

    mean_flip = np.mean(total_flips)
    if mean_flip < 1.0:
        issues.append(f"Very low TD divergence ({mean_flip:.1f}%) — attention may not be adapting to stride topology")
    elif mean_flip > 15.0:
        issues.append(f"High TD divergence ({mean_flip:.1f}%) — attention may be losing teacher signal")
    else:
        findings.append(f"TD divergence is {mean_flip:.1f}% — healthy adaptation to stride topology")

    # Short vs long stride comparison
    short_strides = [r for r in attn_results if r["stride"] <= 5]
    long_strides = [r for r in attn_results if r["stride"] >= 55]
    if short_strides and long_strides:
        short_ent = np.mean([r["mean_entropy"] for r in short_strides])
        long_ent = np.mean([r["mean_entropy"] for r in long_strides])
        if abs(short_ent - long_ent) < 0.2:
            issues.append(f"Short and long strides have similar entropy (short={short_ent:.2f}, long={long_ent:.2f}) — may not be differentiating roles")
        else:
            findings.append(f"Short strides (ent={short_ent:.2f}) differ from long strides (ent={long_ent:.2f}) — role differentiation emerging")

    log(f"\n  ✅ Findings:")
    for f in findings:
        log(f"    + {f}")
    if issues:
        log(f"\n  ⚠️  Concerns:")
        for i in issues:
            log(f"    - {i}")
    else:
        log(f"\n  No concerns — attention appears healthy")

    # ── Eval loss ─────────────────────────────────────────────
    log(f"\n§ 6  Evaluation loss ({args.n_eval} batches)")
    eval_loader2 = ShardedDataLoader(
        args.data_dir, seq_len=cfg.seq_len, batch_size=1,
        shard_start=54, shard_end=60, seed=456,
    )
    eval_loss_val = eval_loss(model, eval_loader2, n_batches=args.n_eval)
    log(f"  Eval loss: {eval_loss_val:.4f}")
    ce_val = getattr(model, "_last_ce", None)
    if ce_val is not None:
        mx.eval(ce_val)
        log(f"  Last CE:   {float(ce_val.item()):.4f}")

    log(f"\n{'='*72}")
    log("Assessment complete.")


if __name__ == "__main__":
    main()
