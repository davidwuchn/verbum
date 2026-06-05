"""Assess whether the v15-td model's FFN is performing I-combinator retrieval.

The hypothesis: the SwiGLU FFN with ternary plates acts as a key-value store.
  gate_plate(x) → which memories match (SiLU gating, ~3% fire)
  key_plate(x)  → retrieve the stored value at that key
  value_plate(gate * key) → project retrieved value back to residual

The I combinator (λx.x = identity/copy-forward) corresponds to retrieval:
the input pattern matches a stored key, and the value is read out unchanged.
The relay heads (H20, H17 with cos_self ≈ 1.0 in teacher) then pass this
retrieved value into the residual stream.

Key questions for the v15 student:
1. Is the FFN gate selective? (sparsity = fraction near zero)
2. Does the FFN key-value product look like retrieval? (gate kills ~89%)
3. Is the FFN output coherent or noise? (project through unembed to read)
4. Is there an identity/relay pattern in the attention that follows?
5. How does each stack (A vs C) differ in its FFN retrieval?

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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "v15"))

from config import V15Config, STRIDES
from v15model import V15Model
from ternary import (
    freeze_ternary_weights,
    restore_ternary,
    unpack_ternary_mlx,
)
from td_delta import (
    convert_to_delta,
    collect_delta_params,
    freeze_delta_architecture,
)
from data import ShardedDataLoader


def log(msg):
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════
# § 1  Load checkpoint (same as attention assessment)
# ══════════════════════════════════════════════════════════════

def load_checkpoint(checkpoint_dir: str, cfg: V15Config) -> V15Model:
    ckpt = Path(checkpoint_dir)
    model = V15Model(cfg)
    freeze_ternary_weights(model)

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
        log(f"  Base plates loaded: {n_loaded}")

    converted = convert_to_delta(
        model, include_prefixes=("shared_stride_stack",),
    )
    freeze_delta_architecture(model)
    freeze_ternary_weights(model)
    log(f"  Delta architecture: {len(converted)} modules")

    model_path = ckpt / "model.npz"
    if model_path.exists():
        saved_model = dict(mx.load(str(model_path)))
        flat_params = dict(tree_flatten(model.parameters()))
        n_loaded = 0
        for key, val in saved_model.items():
            if key in flat_params and val.shape == flat_params[key].shape:
                flat_params[key] = val
                n_loaded += 1
        model.update(tree_unflatten(list(flat_params.items())))
        mx.eval(model.parameters())
        log(f"  Checkpoint weights loaded: {n_loaded}")

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
# § 2  FFN Internals Probe
# ══════════════════════════════════════════════════════════════

def probe_ffn_internals(model: V15Model, input_ids: mx.array, cfg: V15Config):
    """Run forward and intercept the FFN at each pass to measure:
    - Gate sparsity (fraction of neurons near-zero after SiLU)
    - Key activation pattern
    - Gate × Key product sparsity
    - FFN output magnitude and coherence
    
    The v15 model runs the FFN once per pass (4 passes per stack, 2 stacks = 8 total).
    Each pass: attention → FFN → S3 gate.
    The FFN is the same plates for all passes within a stack.
    """
    B, L = input_ids.shape
    d = cfg.d_model

    # Embed
    positions = mx.arange(L)
    x = model.embed_norm(model.embed(input_ids) + model.pos_embed(positions))
    mx.eval(x)

    results = {"stack_a": [], "stack_c": []}

    # ── Stack A ───────────────────────────────────────────────
    for pass_idx, band in enumerate(cfg.stack_a_bands):
        x_before = mx.array(x)  # copy for delta measurement

        # Run attention for this band
        x = model.shared_stride_stack(x, stride_range=band, reverse=False)
        mx.eval(x)

        # FFN probe
        ffn_in = model.stack_a.ffn_norm(x)
        mx.eval(ffn_in)

        # Gate: SiLU(gate_plate(x))
        gate_raw = model.stack_a.ffn_gate_plate(ffn_in)
        gate = nn.silu(gate_raw)
        mx.eval(gate)

        # Key: key_plate(x)  
        key = model.stack_a.ffn_key_plate(ffn_in)
        mx.eval(key)

        # Product: gate * key (this is what goes into value_plate)
        product = gate * key
        product = mx.clip(product, -100.0, 100.0)
        mx.eval(product)

        # Value: value_plate(product)
        ffn_out = model.stack_a.ffn_value_plate(product)
        ffn_out = ffn_out * model.stack_a.ffn_scale + model.stack_a.ffn_bias
        mx.eval(ffn_out)

        # Metrics
        gate_np = np.array(gate[0])  # (L, d_ff)
        key_np = np.array(key[0])
        product_np = np.array(product[0])
        ffn_out_np = np.array(ffn_out[0])  # (L, d_model)
        x_np = np.array(x[0])  # (L, d_model)

        # Gate sparsity: what fraction of neurons are near-zero?
        gate_abs = np.abs(gate_np)
        gate_threshold = 0.01 * np.mean(gate_abs)
        gate_sparsity = float(np.mean(gate_abs < gate_threshold))

        # Top-k gate activations per position
        gate_max_per_pos = np.max(gate_abs, axis=1)  # (L,)
        gate_mean_per_pos = np.mean(gate_abs, axis=1)

        # How many neurons fire (>1% of max)?
        gate_fire_threshold = 0.01 * np.max(gate_abs)
        neurons_firing = np.mean(gate_abs > gate_fire_threshold, axis=1)
        mean_firing_frac = float(np.mean(neurons_firing))

        # Product sparsity (gate kills most)
        product_abs = np.abs(product_np)
        product_threshold = 0.01 * np.mean(product_abs[product_abs > 0])
        product_sparsity = float(np.mean(product_abs < product_threshold))

        # FFN output magnitude
        ffn_out_norm = np.sqrt(np.mean(ffn_out_np ** 2, axis=1))  # per position
        x_norm = np.sqrt(np.mean(x_np ** 2, axis=1))

        # FFN contribution relative to residual
        ffn_to_residual_ratio = float(np.mean(ffn_out_norm / (x_norm + 1e-8)))

        # Cosine between FFN output and input (is it identity-like?)
        cos_io = []
        for pos in range(L):
            xn = x_np[pos]
            fn = ffn_out_np[pos]
            dot = np.sum(xn * fn)
            mag = np.sqrt(np.sum(xn ** 2) * np.sum(fn ** 2) + 1e-12)
            cos_io.append(dot / mag)
        mean_cos_io = float(np.mean(cos_io))

        strides_in_band = STRIDES[band[0]:band[1]]
        results["stack_a"].append({
            "pass_idx": pass_idx,
            "band": band,
            "strides": strides_in_band,
            "gate_sparsity": gate_sparsity,
            "mean_firing_frac": mean_firing_frac,
            "product_sparsity": product_sparsity,
            "ffn_output_rms": float(np.mean(ffn_out_norm)),
            "residual_rms": float(np.mean(x_norm)),
            "ffn_to_residual_ratio": ffn_to_residual_ratio,
            "cos_input_output": mean_cos_io,
        })

        # Apply FFN to residual (to advance state for next pass)
        x = x + ffn_out
        mx.eval(x)

    # ── Stack C ───────────────────────────────────────────────
    for pass_idx, band in enumerate(cfg.stack_c_bands):
        x_before = mx.array(x)

        x = model.shared_stride_stack(x, stride_range=band, reverse=True)
        mx.eval(x)

        ffn_in = model.stack_c.ffn_norm(x)
        mx.eval(ffn_in)

        gate_raw = model.stack_c.ffn_gate_plate(ffn_in)
        gate = nn.silu(gate_raw)
        mx.eval(gate)

        key = model.stack_c.ffn_key_plate(ffn_in)
        mx.eval(key)

        product = gate * key
        product = mx.clip(product, -100.0, 100.0)
        mx.eval(product)

        ffn_out = model.stack_c.ffn_value_plate(product)
        ffn_out = ffn_out * model.stack_c.ffn_scale + model.stack_c.ffn_bias
        mx.eval(ffn_out)

        gate_np = np.array(gate[0])
        product_np = np.array(product[0])
        ffn_out_np = np.array(ffn_out[0])
        x_np = np.array(x[0])

        gate_abs = np.abs(gate_np)
        gate_threshold = 0.01 * np.mean(gate_abs)
        gate_sparsity = float(np.mean(gate_abs < gate_threshold))

        gate_fire_threshold = 0.01 * np.max(gate_abs)
        neurons_firing = np.mean(gate_abs > gate_fire_threshold, axis=1)
        mean_firing_frac = float(np.mean(neurons_firing))

        product_abs = np.abs(product_np)
        product_threshold = 0.01 * np.mean(product_abs[product_abs > 0])
        product_sparsity = float(np.mean(product_abs < product_threshold))

        ffn_out_norm = np.sqrt(np.mean(ffn_out_np ** 2, axis=1))
        x_norm = np.sqrt(np.mean(x_np ** 2, axis=1))
        ffn_to_residual_ratio = float(np.mean(ffn_out_norm / (x_norm + 1e-8)))

        cos_io = []
        for pos in range(L):
            xn = x_np[pos]
            fn = ffn_out_np[pos]
            dot = np.sum(xn * fn)
            mag = np.sqrt(np.sum(xn ** 2) * np.sum(fn ** 2) + 1e-12)
            cos_io.append(dot / mag)
        mean_cos_io = float(np.mean(cos_io))

        strides_in_band = list(reversed(STRIDES[band[0]:band[1]]))
        results["stack_c"].append({
            "pass_idx": pass_idx,
            "band": band,
            "strides": strides_in_band,
            "gate_sparsity": gate_sparsity,
            "mean_firing_frac": mean_firing_frac,
            "product_sparsity": product_sparsity,
            "ffn_output_rms": float(np.mean(ffn_out_norm)),
            "residual_rms": float(np.mean(x_norm)),
            "ffn_to_residual_ratio": ffn_to_residual_ratio,
            "cos_input_output": mean_cos_io,
        })

        x = x + ffn_out
        mx.eval(x)

    return results


# ══════════════════════════════════════════════════════════════
# § 3  Attention Relay Detection (I-combinator pattern)
# ══════════════════════════════════════════════════════════════

def detect_relay_heads(model: V15Model, input_ids: mx.array, cfg: V15Config):
    """Check if any attention heads are acting as relays (cos_self ≈ 1.0).

    A relay head passes its V input through unchanged — this is the
    I combinator in action. The head output equals the FFN-compiled
    value at the attended position.
    
    For each stride layer: compute Q·K attention, gather V, compute
    the weighted V output, and measure cos(output, V[max_attn_pos])
    for each head.
    """
    B, L = input_ids.shape
    from attention import compute_expanded_indices, apply_hpe_rotation, _ALPHA, _N_EIGEN_PAIRS

    positions = mx.arange(L)
    x = model.embed_norm(model.embed(input_ids) + model.pos_embed(positions))
    mx.eval(x)

    stride_stack = model.shared_stride_stack
    results = []

    # Probe a subset of layers (local, phrase, sentence, document)
    probe_layers = [0, 4, 10, 14, 18]  # strides 1, 8, 34, 233, 1597

    for layer_idx in range(len(stride_stack.layers)):
        layer = stride_stack.layers[layer_idx]

        if layer_idx in probe_layers:
            # Intercept the attention computation
            n_heads = layer.n_heads
            d_head = layer.d_head
            W_eff = layer.w_eff

            layer._ensure_indices(L)
            indices = layer._cached_indices
            valid = layer._cached_valid
            log_distances = layer._cached_log_distances

            x_norm = layer.norm(x)
            q_in = x_norm
            for mirror in layer.q_mirrors:
                q_in = mirror(q_in)

            Q = layer.q_proj(q_in).reshape(B, L, n_heads, d_head)
            K = (layer.k_proj(x_norm) + layer.k_bias).reshape(B, L, n_heads, d_head)
            V = (layer.v_proj(x_norm) + layer.v_bias).reshape(B, L, n_heads, d_head)

            GD = n_heads * d_head
            K_flat = K.reshape(B, L, GD)
            V_flat = V.reshape(B, L, GD)
            idx = indices.reshape(1, L * W_eff, 1)
            idx_bc = mx.broadcast_to(idx, (B, L * W_eff, GD))
            K_gathered = mx.take_along_axis(K_flat, idx_bc, axis=1).reshape(B, L, W_eff, n_heads, d_head)
            V_gathered = mx.take_along_axis(V_flat, idx_bc, axis=1).reshape(B, L, W_eff, n_heads, d_head)

            Q_r = Q.transpose(0, 2, 1, 3)
            _, K_gathered_rot = apply_hpe_rotation(
                Q_r, K_gathered, log_distances,
                n_pairs=_N_EIGEN_PAIRS,
                freq_scale=layer.hpe_freq_scale,
            )

            K_r = K_gathered_rot.transpose(0, 3, 1, 2, 4)
            attn = (Q_r[:, :, :, None, :] * K_r).sum(axis=-1) * layer.scale
            decay_bias = -(_ALPHA * log_distances)
            attn = attn + decay_bias[None, None, :, :]
            valid_mask = valid[None, None, :, :]
            attn = mx.where(valid_mask, attn, mx.array(float("-inf")))
            attn = mx.clip(attn, -65.0, 65.0)
            attn_weights = mx.softmax(attn, axis=-1)

            V_r = V_gathered.transpose(0, 3, 1, 2, 4)
            attn_out = (attn_weights[:, :, :, :, None] * V_r).sum(axis=3)
            # attn_out: (B, H, L, Dh)
            mx.eval(attn_out, attn_weights)

            # For each head: measure relay-ness
            # cos(attn_output, V_at_self) — if ≈1, the head is relaying self
            # cos(attn_output, V_at_max_attn) — if ≈1, relaying max-attn position
            attn_out_np = np.array(attn_out[0])  # (H, L, Dh)
            attn_wt_np = np.array(attn_weights[0])  # (H, L, W_eff)
            V_np = np.array(V[0])  # (L, H, Dh)

            head_relay_scores = []
            for h in range(n_heads):
                cos_self_list = []
                cos_max_list = []
                for pos in range(min(L, 64)):  # sample positions
                    out_vec = attn_out_np[h, pos]  # (Dh,)
                    self_v = V_np[pos, h]  # V at self position for this head

                    # cos(output, V_self)
                    dot_s = np.sum(out_vec * self_v)
                    mag_s = np.sqrt(np.sum(out_vec ** 2) * np.sum(self_v ** 2) + 1e-12)
                    cos_self_list.append(dot_s / mag_s)

                head_relay_scores.append({
                    "head": h,
                    "mean_cos_self": float(np.mean(cos_self_list)),
                })

            results.append({
                "layer_idx": layer_idx,
                "stride": STRIDES[layer_idx],
                "head_relay": head_relay_scores,
            })

        # Advance residual through the layer
        x = layer(x)
        mx.eval(x)

    return results


# ══════════════════════════════════════════════════════════════
# § 4  Main
# ══════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="checkpoints/v15-td/step_001500")
    parser.add_argument("--extracted", default="checkpoints/v15-extracted/model.npz/model.npz")
    parser.add_argument("--data-dir", default="/Users/mwhitford/data/fractal-bitnet/shards-qwen36")
    parser.add_argument("--seq-len", type=int, default=256)
    args = parser.parse_args()

    cfg = V15Config(extracted_model_path=args.extracted)

    log("=" * 72)
    log("v15-td FFN Retrieval Assessment (I-Combinator Pattern)")
    log("=" * 72)

    log(f"\n§ 1  Loading checkpoint: {args.checkpoint}")
    model = load_checkpoint(args.checkpoint, cfg)

    log(f"\n§ 2  Preparing input (seq_len={args.seq_len})")
    data_loader = ShardedDataLoader(
        args.data_dir, seq_len=args.seq_len, batch_size=1,
        shard_start=54, shard_end=60, seed=999,
    )
    sample_ids, _ = next(data_loader)
    input_ids = mx.array(sample_ids)

    # ── FFN Internals ─────────────────────────────────────────
    log(f"\n§ 3  FFN Internals: Gate Sparsity + Key-Value Retrieval")
    ffn_results = probe_ffn_internals(model, input_ids, cfg)

    log(f"\n  Stack A (ascending, 4 passes):")
    log(f"  {'Pass':>4s} {'Band':>10s} {'Strides':>20s} | {'GateSprs':>8s} {'Fire%':>6s} {'ProdSprs':>8s} | {'FFN_RMS':>7s} {'Res_RMS':>7s} {'Ratio':>6s} | {'cos(I/O)':>8s}")
    for r in ffn_results["stack_a"]:
        strides_str = ",".join(str(s) for s in r["strides"][:5])
        if len(r["strides"]) > 5:
            strides_str += "..."
        log(f"  {r['pass_idx']:4d} {str(r['band']):>10s} {strides_str:>20s}"
            f" | {r['gate_sparsity']:7.1%} {r['mean_firing_frac']:5.1%} {r['product_sparsity']:7.1%}"
            f" | {r['ffn_output_rms']:7.3f} {r['residual_rms']:7.3f} {r['ffn_to_residual_ratio']:6.3f}"
            f" | {r['cos_input_output']:8.4f}")

    log(f"\n  Stack C (descending, 4 passes):")
    log(f"  {'Pass':>4s} {'Band':>10s} {'Strides':>20s} | {'GateSprs':>8s} {'Fire%':>6s} {'ProdSprs':>8s} | {'FFN_RMS':>7s} {'Res_RMS':>7s} {'Ratio':>6s} | {'cos(I/O)':>8s}")
    for r in ffn_results["stack_c"]:
        strides_str = ",".join(str(s) for s in r["strides"][:5])
        if len(r["strides"]) > 5:
            strides_str += "..."
        log(f"  {r['pass_idx']:4d} {str(r['band']):>10s} {strides_str:>20s}"
            f" | {r['gate_sparsity']:7.1%} {r['mean_firing_frac']:5.1%} {r['product_sparsity']:7.1%}"
            f" | {r['ffn_output_rms']:7.3f} {r['residual_rms']:7.3f} {r['ffn_to_residual_ratio']:6.3f}"
            f" | {r['cos_input_output']:8.4f}")

    # ── Attention Relay Detection ─────────────────────────────
    log(f"\n§ 4  Attention Relay Detection (I-combinator = cos_self ≈ 1.0)")
    # Reload model state for relay detection (FFN probe advanced the residual)
    model2 = load_checkpoint(args.checkpoint, cfg)
    relay_results = detect_relay_heads(model2, input_ids, cfg)

    for r in relay_results:
        log(f"\n  Layer {r['layer_idx']} (stride={r['stride']}):")
        log(f"  {'Head':>5s} | {'cos_self':>8s} | {'Interpretation'}")
        for hr in r["head_relay"]:
            cos = hr["mean_cos_self"]
            if cos > 0.8:
                interp = "RELAY (I combinator) — passing V through"
            elif cos > 0.5:
                interp = "PARTIAL relay — some composition"
            elif cos > 0.0:
                interp = "COMPOSITION — transforming V"
            else:
                interp = "ANTI-CORRELATED — inverting V"
            log(f"  {hr['head']:5d} | {cos:8.4f} | {interp}")

    # ── Assessment ────────────────────────────────────────────
    log(f"\n§ 5  Assessment: Is the FFN doing I-combinator retrieval?")

    findings = []
    concerns = []

    # Gate sparsity check
    all_sparsity = ([r["gate_sparsity"] for r in ffn_results["stack_a"]] +
                    [r["gate_sparsity"] for r in ffn_results["stack_c"]])
    avg_sparsity = np.mean(all_sparsity)
    if avg_sparsity > 0.5:
        findings.append(f"FFN gate is {avg_sparsity:.0%} sparse — selective retrieval, not dense mixing")
    elif avg_sparsity > 0.2:
        findings.append(f"FFN gate is {avg_sparsity:.0%} sparse — moderate selectivity")
    else:
        concerns.append(f"FFN gate is only {avg_sparsity:.0%} sparse — more like dense transform than retrieval")

    # Firing fraction
    all_firing = ([r["mean_firing_frac"] for r in ffn_results["stack_a"]] +
                  [r["mean_firing_frac"] for r in ffn_results["stack_c"]])
    avg_firing = np.mean(all_firing)
    findings.append(f"Average {avg_firing:.1%} of neurons fire per position (teacher: ~3%)")

    # FFN output magnitude
    all_ratios = ([r["ffn_to_residual_ratio"] for r in ffn_results["stack_a"]] +
                  [r["ffn_to_residual_ratio"] for r in ffn_results["stack_c"]])
    avg_ratio = np.mean(all_ratios)
    findings.append(f"FFN output is {avg_ratio:.3f}× the residual magnitude")

    # Relay heads
    n_relay = 0
    n_total_heads = 0
    for r in relay_results:
        for hr in r["head_relay"]:
            n_total_heads += 1
            if hr["mean_cos_self"] > 0.8:
                n_relay += 1
    if n_relay > 0:
        findings.append(f"{n_relay}/{n_total_heads} head-layer pairs are relays (cos_self > 0.8) — I combinator present")
    else:
        findings.append(f"No strong relay heads detected (cos_self > 0.8) — attention is compositional, not identity")

    # cos(input, output) — is FFN doing identity?
    all_cos = ([r["cos_input_output"] for r in ffn_results["stack_a"]] +
               [r["cos_input_output"] for r in ffn_results["stack_c"]])
    avg_cos = np.mean(all_cos)
    if avg_cos > 0.5:
        findings.append(f"FFN cos(input, output) = {avg_cos:.3f} — output partially aligned with input (partial identity)")
    elif avg_cos > 0.0:
        findings.append(f"FFN cos(input, output) = {avg_cos:.3f} — output weakly correlated with input")
    else:
        findings.append(f"FFN cos(input, output) = {avg_cos:.3f} — FFN is transforming, not relaying")

    log(f"\n  ✅ Findings:")
    for f in findings:
        log(f"    + {f}")
    if concerns:
        log(f"\n  ⚠️  Concerns:")
        for c in concerns:
            log(f"    - {c}")

    log(f"\n{'='*72}")
    log("FFN retrieval assessment complete.")


if __name__ == "__main__":
    main()
