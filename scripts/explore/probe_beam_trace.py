#!/usr/bin/env python3
"""Probe: Trace the holographic beam through layers.

The hologram exists (93.6% ternary-safe, universal across models).
Q is the beam angle, V is the plate (session 093: same V for B and C,
cos=1.000, but Q cos=0.005). HoloQuant failed because it tried to
reconstruct the plate without the beam. The beam is small — Q projections,
MoE gates, norms — the 6.4% precision-critical component.

This probe traces the beam (activation vector) through each layer,
decomposing every layer's contribution into:
  1. Angular rotation (direction change) — the beam-forming operation
  2. Magnitude scaling (norm change) — amplitude adjustment
  3. Attention vs FFN contribution to each

Then tests whether the angular rotation correlates with Q projections,
and whether ternary Q preserves the beam angle (if yes → beamformer is tiny).

Two conditions:
  COMPILE: nucleus compile gate + input sentence
  NULL:    null gate + input sentence

The compile gate acts as a reference beam at a different angle.
Both conditions illuminate the same holographic plate (weights).
The beam divergence reveals the beamforming structure.

Model: Pythia-160M (12 layers, 12 heads, d=768, GPT-NeoX)
  - Universal hologram confirmed (r=0.9801 with Qwen3-32B)
  - Small enough for fast iteration
  - use_parallel_residual=True (attn + FFN added in parallel)
  - Fused QKV: query_key_value projection (768 → 2304)

Usage:
    uv run python scripts/explore/probe_beam_trace.py
    uv run python scripts/explore/probe_beam_trace.py --quick
    uv run python scripts/explore/probe_beam_trace.py --device mps

Output: results/beam-trace/

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

MODEL_NAME = "EleutherAI/pythia-160m-deduped"
OUTPUT_DIR = Path("results/beam-trace")
GATES_DIR = Path("gates")

# Pythia-160M: 12 layers, 12 heads, head_dim=64, d_model=768
# use_parallel_residual=True: h_{l+1} = h_l + Attn(h_l) + FFN(h_l)
# Fused QKV projection: query_key_value (768 → 2304 = 3 * 768)

TEST_SENTENCES = [
    "The cat sat on the mat.",
    "Every student passed the exam.",
    "The man who the dog chased ran away.",
    "John gave Mary a book about himself.",
    "If it rains, the ground gets wet.",
    "The professor who published the paper won the award.",
    "No student who failed the test passed the course.",
    "The key to the cabinets was on the table.",
]


# ══════════════════════════════════════════════════════════════════
# Gate loading
# ══════════════════════════════════════════════════════════════════

def load_gate(name: str) -> str:
    path = GATES_DIR / f"{name}.txt"
    return path.read_text()


def make_prompt(gate_text: str, sentence: str) -> str:
    return gate_text + sentence


# ══════════════════════════════════════════════════════════════════
# Model loading
# ══════════════════════════════════════════════════════════════════

def load_model(device: str = "mps"):
    """Load Pythia-160M."""
    print(f"Loading {MODEL_NAME}...", file=sys.stderr, end="", flush=True)
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float32,
        device_map=device,
        trust_remote_code=True,
    )
    model.eval()
    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    print(f" {time.time()-t0:.1f}s ({n_layers} layers, d={d_model})",
          file=sys.stderr)
    return model, tokenizer


# ══════════════════════════════════════════════════════════════════
# Angular decomposition math
# ══════════════════════════════════════════════════════════════════

def angular_decomposition(h_pre: np.ndarray, h_post: np.ndarray) -> dict:
    """Decompose the residual update h_pre → h_post into angle + magnitude.

    h_post = h_pre + delta
    delta = delta_parallel + delta_perp

    Angular rotation: angle between h_pre direction and h_post direction.
    Magnitude scaling: ||h_post|| / ||h_pre||.

    The perpendicular component of delta is what rotates the beam.
    The parallel component scales it.
    """
    delta = h_post - h_pre

    norm_pre = np.linalg.norm(h_pre)
    norm_post = np.linalg.norm(h_post)
    norm_delta = np.linalg.norm(delta)

    if norm_pre < 1e-12 or norm_post < 1e-12:
        return {
            "angle_rad": 0.0,
            "angle_deg": 0.0,
            "mag_ratio": 1.0,
            "delta_norm": float(norm_delta),
            "delta_parallel_frac": 0.0,
            "delta_perp_frac": 0.0,
        }

    # Unit vectors
    u_pre = h_pre / norm_pre

    # Cosine of angle between h_pre and h_post
    cos_angle = np.clip(np.dot(h_pre, h_post) / (norm_pre * norm_post), -1.0, 1.0)
    angle_rad = float(np.arccos(cos_angle))

    # Decompose delta into parallel and perpendicular to h_pre
    delta_parallel_mag = np.dot(delta, u_pre)  # signed projection
    delta_parallel = delta_parallel_mag * u_pre
    delta_perp = delta - delta_parallel

    norm_delta_parallel = np.linalg.norm(delta_parallel)
    norm_delta_perp = np.linalg.norm(delta_perp)

    # Fractions of delta that are parallel vs perpendicular
    if norm_delta > 1e-12:
        parallel_frac = float(norm_delta_parallel / norm_delta)
        perp_frac = float(norm_delta_perp / norm_delta)
    else:
        parallel_frac = 0.0
        perp_frac = 0.0

    return {
        "angle_rad": float(angle_rad),
        "angle_deg": float(np.degrees(angle_rad)),
        "mag_ratio": float(norm_post / norm_pre),
        "norm_pre": float(norm_pre),
        "norm_post": float(norm_post),
        "delta_norm": float(norm_delta),
        "delta_parallel_mag": float(delta_parallel_mag),
        "delta_perp_norm": float(norm_delta_perp),
        "delta_parallel_frac": parallel_frac,
        "delta_perp_frac": perp_frac,
    }


def beam_divergence(h_compile: np.ndarray, h_null: np.ndarray) -> dict:
    """Measure beam divergence between compile and null conditions."""
    norm_c = np.linalg.norm(h_compile)
    norm_n = np.linalg.norm(h_null)

    if norm_c < 1e-12 or norm_n < 1e-12:
        return {"cosine": 0.0, "angle_deg": 90.0, "norm_ratio": 0.0}

    cos_sim = float(np.dot(h_compile, h_null) / (norm_c * norm_n))
    cos_sim = np.clip(cos_sim, -1.0, 1.0)
    angle = float(np.degrees(np.arccos(cos_sim)))

    return {
        "cosine": cos_sim,
        "angle_deg": angle,
        "norm_compile": float(norm_c),
        "norm_null": float(norm_n),
        "norm_ratio": float(norm_c / norm_n),
    }


# ══════════════════════════════════════════════════════════════════
# Core: Hook-based beam trace
# ══════════════════════════════════════════════════════════════════

def trace_beam(
    model, tokenizer, text: str,
    gen_position: int = -1,
) -> dict:
    """Run forward pass with hooks on every layer.

    Captures:
      - Input to each layer (pre-attention/FFN)
      - Output of each layer (post-attention+FFN)
      - Attention output alone (for attn vs FFN decomposition)
      - Hidden state at each layer boundary

    Pythia (GPTNeoX) with use_parallel_residual=True:
      h_{l+1} = h_l + Attn(LN_a(h_l)) + FFN(LN_f(h_l))
      Both branches read from h_l, not from h_l + Attn(LN_a(h_l))

    We hook:
      - layer input (residual stream before this layer)
      - attention output (just the attn branch contribution)
      - FFN output (just the FFN branch contribution)
      - layer output (residual stream after this layer)
    """
    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size

    # Capture dictionaries
    layer_inputs = {}     # residual stream entering each layer
    attn_outputs = {}     # attention branch output (before residual add)
    ffn_outputs = {}      # FFN branch output (before residual add)
    layer_outputs = {}    # residual stream leaving each layer

    hooks = []

    # Hook layer input: the input to the transformer block
    for li in range(n_layers):
        layer = model.gpt_neox.layers[li]

        # Layer-level hook: captures input and output of entire block
        def make_layer_hook(idx):
            def hook_fn(module, inp, out):
                # inp is tuple, first element is hidden_states
                h_in = inp[0] if isinstance(inp, tuple) else inp
                layer_inputs[idx] = h_in.detach()
                # out is tuple, first element is hidden_states
                h_out = out[0] if isinstance(out, tuple) else out
                layer_outputs[idx] = h_out.detach()
            return hook_fn
        hooks.append(layer.register_forward_hook(make_layer_hook(li)))

        # Attention output hook
        def make_attn_hook(idx):
            def hook_fn(module, inp, out):
                # GPTNeoX attention returns (attn_output, ...) or just attn_output
                h = out[0] if isinstance(out, tuple) else out
                attn_outputs[idx] = h.detach()
            return hook_fn
        hooks.append(layer.attention.register_forward_hook(make_attn_hook(li)))

        # FFN (MLP) output hook
        def make_ffn_hook(idx):
            def hook_fn(module, inp, out):
                h = out if not isinstance(out, tuple) else out[0]
                ffn_outputs[idx] = h.detach()
            return hook_fn
        hooks.append(layer.mlp.register_forward_hook(make_ffn_hook(li)))

    # Also capture the embedding output (before first layer)
    embed_output = {}

    def embed_hook(module, inp, out):
        embed_output[0] = out.detach()
    hooks.append(model.gpt_neox.embed_in.register_forward_hook(embed_hook))

    # Run forward pass
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    token_ids = inputs["input_ids"][0].tolist()
    n_tokens = len(token_ids)

    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)

    # Clean up hooks
    for h in hooks:
        h.remove()

    # Resolve generation position
    if gen_position < 0:
        gen_position = n_tokens + gen_position

    # Extract per-layer beam data at gen_position
    results = {
        "token_ids": token_ids,
        "n_tokens": n_tokens,
        "gen_position": gen_position,
        "layers": {},
    }

    # Embedding (layer -1 → layer 0 input)
    if 0 in embed_output:
        h_embed = embed_output[0][0, gen_position].cpu().float().numpy()
        results["embedding"] = {
            "hidden_state": h_embed.tolist(),
            "norm": float(np.linalg.norm(h_embed)),
        }

    for li in range(n_layers):
        if li not in layer_inputs or li not in layer_outputs:
            continue

        h_in = layer_inputs[li][0, gen_position].cpu().float().numpy()
        h_out = layer_outputs[li][0, gen_position].cpu().float().numpy()

        # Attention and FFN contributions
        h_attn = attn_outputs[li][0, gen_position].cpu().float().numpy() if li in attn_outputs else None
        h_ffn = ffn_outputs[li][0, gen_position].cpu().float().numpy() if li in ffn_outputs else None

        # Angular decomposition of full layer
        layer_decomp = angular_decomposition(h_in, h_out)

        # Angular contribution of attn branch alone
        attn_decomp = None
        if h_attn is not None:
            h_after_attn = h_in + h_attn  # hypothetical: what if only attn added
            attn_decomp = angular_decomposition(h_in, h_after_attn)

        # Angular contribution of FFN branch alone
        ffn_decomp = None
        if h_ffn is not None:
            h_after_ffn = h_in + h_ffn  # hypothetical: what if only FFN added
            ffn_decomp = angular_decomposition(h_in, h_after_ffn)

        # How much of the total rotation is from attn vs FFN?
        # In parallel residual: delta = attn + ffn
        # The rotation from each can be measured by the perpendicular component
        attn_perp_frac = 0.0
        ffn_perp_frac = 0.0
        if h_attn is not None and h_ffn is not None:
            norm_in = np.linalg.norm(h_in)
            if norm_in > 1e-12:
                u_in = h_in / norm_in
                # Perpendicular components
                attn_perp = h_attn - np.dot(h_attn, u_in) * u_in
                ffn_perp = h_ffn - np.dot(h_ffn, u_in) * u_in
                total_perp = attn_perp + ffn_perp
                norm_total_perp = np.linalg.norm(total_perp)
                if norm_total_perp > 1e-12:
                    # Project each onto total perpendicular direction
                    u_perp = total_perp / norm_total_perp
                    attn_proj = float(np.dot(attn_perp, u_perp))
                    ffn_proj = float(np.dot(ffn_perp, u_perp))
                    total_proj = attn_proj + ffn_proj
                    if abs(total_proj) > 1e-12:
                        attn_perp_frac = attn_proj / total_proj
                        ffn_perp_frac = ffn_proj / total_proj

        results["layers"][li] = {
            "decomposition": layer_decomp,
            "attn_decomposition": attn_decomp,
            "ffn_decomposition": ffn_decomp,
            "attn_rotation_frac": float(attn_perp_frac),
            "ffn_rotation_frac": float(ffn_perp_frac),
            "hidden_state_in": h_in.tolist(),
            "hidden_state_out": h_out.tolist(),
            "attn_output": h_attn.tolist() if h_attn is not None else None,
            "ffn_output": h_ffn.tolist() if h_ffn is not None else None,
        }

    return results


# ══════════════════════════════════════════════════════════════════
# Q-correlation analysis
# ══════════════════════════════════════════════════════════════════

def extract_q_projections(model) -> dict[int, np.ndarray]:
    """Extract Q weight matrices from every layer.

    Pythia uses fused query_key_value: (3*d_model, d_model)
    Q is the first d_model rows.
    """
    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size

    q_weights = {}
    for li in range(n_layers):
        layer = model.gpt_neox.layers[li]
        # Fused QKV: query_key_value.weight is (3*d_model, d_model)
        qkv_weight = layer.attention.query_key_value.weight.data
        q_w = qkv_weight[:d_model, :].cpu().float().numpy()  # (d_model, d_model)
        q_weights[li] = q_w

    return q_weights


def q_subspace_analysis(
    h_in: np.ndarray,
    delta_perp: np.ndarray,
    q_weight: np.ndarray,
) -> dict:
    """Measure how much of the angular rotation lives in the Q subspace.

    Q maps the input to query space. If the beam angle is controlled by Q,
    then the perpendicular component of delta should align with the Q subspace.

    We compute:
    1. Q(h_in) — the query vector for this input
    2. Project delta_perp onto the column space of Q^T (= row space of Q)
    3. Fraction of delta_perp explained by Q subspace
    """
    norm_perp = np.linalg.norm(delta_perp)
    if norm_perp < 1e-12:
        return {"q_explained_frac": 0.0, "q_residual_frac": 1.0}

    # Q subspace: rows of Q weight matrix span the query space in output
    # Q^T columns span the query subspace in input space
    # For rotation analysis: does delta_perp lie in the row space of Q?
    # Project delta_perp onto top singular vectors of Q
    # Use truncated SVD for efficiency
    try:
        U, S, Vt = np.linalg.svd(q_weight, full_matrices=False)
        # U: (d_model, d_model) — left singular vectors (output/query space)
        # S: (d_model,) — singular values
        # Vt: (d_model, d_model) — right singular vectors (input space)

        # delta_perp lives in input space (d_model)
        # Project onto V (columns = right singular vectors)
        V = Vt.T  # (d_model, d_model)

        # Take top-k components that capture 90% variance
        cumvar = np.cumsum(S**2) / np.sum(S**2)
        k_90 = int(np.searchsorted(cumvar, 0.90)) + 1
        k_99 = int(np.searchsorted(cumvar, 0.99)) + 1

        # Projection onto top-k_90 subspace
        V_k = V[:, :k_90]  # (d_model, k_90)
        proj = V_k @ (V_k.T @ delta_perp)  # project and reconstruct
        explained_90 = float(np.linalg.norm(proj) / norm_perp)

        V_k99 = V[:, :k_99]
        proj_99 = V_k99 @ (V_k99.T @ delta_perp)
        explained_99 = float(np.linalg.norm(proj_99) / norm_perp)

        # Full projection (should be ~1.0 for square Q)
        proj_full = q_weight.T @ (q_weight @ delta_perp)
        proj_full_norm = np.linalg.norm(proj_full)
        # Normalize by ||Q||^2 * ||delta_perp|| for fair comparison
        # Actually for square Q, V spans the full space, so full explained = 1.0
        # More meaningful: does Q AMPLIFY the perpendicular component?
        q_delta = q_weight @ delta_perp  # (d_model,)
        q_hin = q_weight @ h_in  # (d_model,)
        q_delta_norm = float(np.linalg.norm(q_delta))
        q_hin_norm = float(np.linalg.norm(q_hin))

        # Ratio: how much does Q amplify delta_perp relative to h_in?
        if q_hin_norm > 1e-12:
            q_amplification = (q_delta_norm / norm_perp) / (q_hin_norm / np.linalg.norm(h_in))
        else:
            q_amplification = 0.0

        return {
            "q_explained_90": explained_90,
            "q_explained_99": explained_99,
            "q_rank_90": int(k_90),
            "q_rank_99": int(k_99),
            "q_amplification": float(q_amplification),
            "q_delta_norm": q_delta_norm,
            "q_hin_norm": q_hin_norm,
        }
    except Exception as e:
        return {"error": str(e)}


# ══════════════════════════════════════════════════════════════════
# Ternary beamformer test
# ══════════════════════════════════════════════════════════════════

def ternarize_weight(W: np.ndarray, mode: str = "group") -> np.ndarray:
    """Ternarize a weight matrix.

    Modes:
      "sign" — pure sign (W → sign(W))
      "group" — ternary with per-group scale (groups of 64)
      "global" — ternary with global scale

    Returns reconstructed float matrix.
    """
    if mode == "sign":
        return np.sign(W).astype(np.float32)

    elif mode == "global":
        scale = np.abs(W).mean()
        return np.sign(W).astype(np.float32) * scale

    elif mode == "group":
        group_size = 64
        shape = W.shape
        W_flat = W.reshape(-1)
        n = len(W_flat)
        n_padded = ((n + group_size - 1) // group_size) * group_size
        W_padded = np.zeros(n_padded, dtype=np.float32)
        W_padded[:n] = W_flat

        W_groups = W_padded.reshape(-1, group_size)
        scales = np.abs(W_groups).mean(axis=-1, keepdims=True)  # (n_groups, 1)
        signs = np.sign(W_groups)  # (n_groups, group_size)
        reconstructed = (signs * scales).reshape(-1)[:n].reshape(shape)
        return reconstructed.astype(np.float32)

    else:
        raise ValueError(f"Unknown mode: {mode}")


def test_ternary_beam(
    model, tokenizer, text: str,
    gen_position: int = -1,
) -> dict:
    """Test whether ternarizing Q/V/FFN preserves the beam angle.

    For each component type (Q, V_proj, FFN), replace with ternary
    and measure beam angle deviation from full-precision baseline.

    This is destructive — we modify weights in-place and restore.
    """
    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size

    # Get baseline beam
    baseline = trace_beam(model, tokenizer, text, gen_position)
    baseline_states = {}
    for li in range(n_layers):
        if li in baseline["layers"]:
            baseline_states[li] = np.array(baseline["layers"][li]["hidden_state_out"])

    results = {"baseline_norms": {}, "tests": {}}
    for li in range(n_layers):
        if li in baseline_states:
            results["baseline_norms"][li] = float(np.linalg.norm(baseline_states[li]))

    # Test each component type × ternarization mode
    components = {
        "Q": lambda li: model.gpt_neox.layers[li].attention.query_key_value,
        "attn_dense": lambda li: model.gpt_neox.layers[li].attention.dense,
        "FFN_dense_h_to_4h": lambda li: model.gpt_neox.layers[li].mlp.dense_h_to_4h,
        "FFN_dense_4h_to_h": lambda li: model.gpt_neox.layers[li].mlp.dense_4h_to_h,
    }

    modes = ["sign", "global", "group"]

    for comp_name, get_module in components.items():
        for mode in modes:
            test_key = f"{comp_name}_{mode}"
            print(f"  Testing {test_key}...", file=sys.stderr, end="", flush=True)

            # Save original weights
            originals = {}
            for li in range(n_layers):
                module = get_module(li)
                originals[li] = module.weight.data.clone()

                # Ternarize
                W_np = module.weight.data.cpu().float().numpy()
                if comp_name == "Q":
                    # Only ternarize the Q portion (first d_model rows of QKV)
                    W_q = W_np[:d_model, :]
                    W_q_ternary = ternarize_weight(W_q, mode)
                    W_np[:d_model, :] = W_q_ternary
                else:
                    W_np = ternarize_weight(W_np, mode)

                module.weight.data = torch.tensor(W_np, device=module.weight.device,
                                                   dtype=module.weight.dtype)

            # Run modified forward pass
            modified = trace_beam(model, tokenizer, text, gen_position)

            # Measure angular deviation from baseline
            deviations = {}
            for li in range(n_layers):
                if li in modified["layers"] and li in baseline_states:
                    h_mod = np.array(modified["layers"][li]["hidden_state_out"])
                    h_base = baseline_states[li]
                    dev = beam_divergence(h_mod, h_base)
                    deviations[li] = dev

            results["tests"][test_key] = deviations

            # Restore original weights
            for li in range(n_layers):
                module = get_module(li)
                module.weight.data = originals[li]

            print(f" done", file=sys.stderr)

    # Per-layer isolation test: ternarize ONE layer at a time (group mode only)
    # This measures each layer's individual sensitivity to ternarization
    for comp_name, get_module in components.items():
        test_key = f"{comp_name}_per_layer_group"
        print(f"  Testing {test_key}...", file=sys.stderr, end="", flush=True)

        per_layer_devs = {}
        for target_li in range(n_layers):
            module = get_module(target_li)
            original = module.weight.data.clone()

            # Ternarize just this one layer
            W_np = module.weight.data.cpu().float().numpy()
            if comp_name == "Q":
                W_q = W_np[:d_model, :]
                W_q_ternary = ternarize_weight(W_q, "group")
                W_np[:d_model, :] = W_q_ternary
            else:
                W_np = ternarize_weight(W_np, "group")

            module.weight.data = torch.tensor(W_np, device=module.weight.device,
                                               dtype=module.weight.dtype)

            # Run and measure
            modified = trace_beam(model, tokenizer, text, gen_position)

            # Measure deviation at the LAST layer (cumulative effect)
            last_li = n_layers - 1
            if last_li in modified["layers"] and last_li in baseline_states:
                h_mod = np.array(modified["layers"][last_li]["hidden_state_out"])
                h_base = baseline_states[last_li]
                dev = beam_divergence(h_mod, h_base)
                per_layer_devs[target_li] = dev

            # Restore
            module.weight.data = original

        results["tests"][test_key] = per_layer_devs
        print(f" done", file=sys.stderr)

    return results


# ══════════════════════════════════════════════════════════════════
# Main analysis pipeline
# ══════════════════════════════════════════════════════════════════

def analyze_beam_trace(
    model, tokenizer,
    sentences: list[str],
    quick: bool = False,
) -> dict:
    """Full beam-trace analysis."""

    compile_gate = load_gate("compile")
    null_gate = load_gate("null")

    if quick:
        sentences = sentences[:3]

    all_results = []
    q_weights = extract_q_projections(model)

    for si, sentence in enumerate(sentences):
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"Sentence {si+1}/{len(sentences)}: {sentence}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

        compile_prompt = make_prompt(compile_gate, sentence)
        null_prompt = make_prompt(null_gate, sentence)

        # Trace beam for both conditions
        print(f"  Tracing compile beam...", file=sys.stderr)
        compile_trace = trace_beam(model, tokenizer, compile_prompt)
        print(f"  Tracing null beam...", file=sys.stderr)
        null_trace = trace_beam(model, tokenizer, null_prompt)

        n_layers = model.config.num_hidden_layers

        # Compare beams at each layer
        layer_analysis = {}
        for li in range(n_layers):
            if li not in compile_trace["layers"] or li not in null_trace["layers"]:
                continue

            cl = compile_trace["layers"][li]
            nl = null_trace["layers"][li]

            h_c = np.array(cl["hidden_state_out"])
            h_n = np.array(nl["hidden_state_out"])

            # Beam divergence at this layer
            div = beam_divergence(h_c, h_n)

            # Angular decomposition for each condition
            h_c_in = np.array(cl["hidden_state_in"])
            h_n_in = np.array(nl["hidden_state_in"])

            # Q-subspace analysis: does Q explain the angular rotation?
            # Compute perpendicular component of delta for compile condition
            h_c_out = np.array(cl["hidden_state_out"])
            delta_c = h_c_out - h_c_in
            norm_c_in = np.linalg.norm(h_c_in)
            if norm_c_in > 1e-12:
                u_c_in = h_c_in / norm_c_in
                delta_c_perp = delta_c - np.dot(delta_c, u_c_in) * u_c_in
            else:
                delta_c_perp = delta_c

            q_analysis = q_subspace_analysis(h_c_in, delta_c_perp, q_weights[li])

            # Differential Q analysis: what does Q do differently for compile vs null?
            h_n_out = np.array(nl["hidden_state_out"])
            delta_n = h_n_out - h_n_in
            norm_n_in = np.linalg.norm(h_n_in)
            if norm_n_in > 1e-12:
                u_n_in = h_n_in / norm_n_in
                delta_n_perp = delta_n - np.dot(delta_n, u_n_in) * u_n_in
            else:
                delta_n_perp = delta_n

            # The "differential beam rotation" — how differently do the two beams rotate?
            diff_perp = delta_c_perp - delta_n_perp
            diff_perp_norm = float(np.linalg.norm(diff_perp))
            avg_perp_norm = (np.linalg.norm(delta_c_perp) + np.linalg.norm(delta_n_perp)) / 2
            diff_relative = diff_perp_norm / max(avg_perp_norm, 1e-12)

            layer_analysis[li] = {
                "beam_divergence": div,
                "compile_decomposition": cl["decomposition"],
                "null_decomposition": nl["decomposition"],
                "compile_attn_rotation_frac": cl["attn_rotation_frac"],
                "compile_ffn_rotation_frac": cl["ffn_rotation_frac"],
                "null_attn_rotation_frac": nl["attn_rotation_frac"],
                "null_ffn_rotation_frac": nl["ffn_rotation_frac"],
                "q_subspace": q_analysis,
                "differential_rotation_norm": diff_perp_norm,
                "differential_rotation_relative": float(diff_relative),
            }

        # Ternary beamformer test (only on first sentence to save time)
        ternary_test = None
        if si == 0:
            print(f"\n  Ternary beamformer test...", file=sys.stderr)
            ternary_test = test_ternary_beam(
                model, tokenizer, compile_prompt)

        # Strip hidden state vectors from layer analysis (keep decompositions only)
        layer_analysis_clean = {}
        for li, la in layer_analysis.items():
            la_clean = {k: v for k, v in la.items()
                        if k not in ("hidden_state_in", "hidden_state_out",
                                     "attn_output", "ffn_output")}
            layer_analysis_clean[li] = la_clean

        sent_result = {
            "sentence": sentence,
            "compile_tokens": compile_trace["n_tokens"],
            "null_tokens": null_trace["n_tokens"],
            "layers": layer_analysis_clean,
            "ternary_test": ternary_test,
        }

        all_results.append(sent_result)

        # Print summary
        print(f"\n  {'Layer':>5} {'Cos':>7} {'Angle':>7} "
              f"{'C_rot°':>7} {'N_rot°':>7} "
              f"{'C_attn%':>7} {'C_ffn%':>7} "
              f"{'Q_amp':>7}",
              file=sys.stderr)
        for li in sorted(layer_analysis.keys()):
            la = layer_analysis[li]
            print(f"  {li:>5} "
                  f"{la['beam_divergence']['cosine']:>7.4f} "
                  f"{la['beam_divergence']['angle_deg']:>7.2f} "
                  f"{la['compile_decomposition']['angle_deg']:>7.2f} "
                  f"{la['null_decomposition']['angle_deg']:>7.2f} "
                  f"{100*la['compile_attn_rotation_frac']:>6.1f}% "
                  f"{100*la['compile_ffn_rotation_frac']:>6.1f}% "
                  f"{la['q_subspace'].get('q_amplification', 0):>7.3f}",
                  file=sys.stderr)

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "model": MODEL_NAME,
        "n_sentences": len(sentences),
        "n_layers": model.config.num_hidden_layers,
        "d_model": model.config.hidden_size,
        "sentences": all_results,
    }


# ══════════════════════════════════════════════════════════════════
# Summary printing
# ══════════════════════════════════════════════════════════════════

def print_ternary_summary(results: dict):
    """Print ternary beamformer test summary."""
    for sent in results["sentences"]:
        if sent.get("ternary_test") is None:
            continue

        test = sent["ternary_test"]
        print(f"\n{'='*70}")
        print(f"TERNARY BEAMFORMER TEST: {sent['sentence']}")
        print(f"{'='*70}")

        # Separate all-layer tests from per-layer isolation tests
        all_layer_tests = {}
        per_layer_tests = {}
        for test_key in sorted(test["tests"].keys()):
            if "per_layer" in test_key:
                per_layer_tests[test_key] = test["tests"][test_key]
            else:
                all_layer_tests[test_key] = test["tests"][test_key]

        # All-layer tests
        print(f"\n  ALL LAYERS TERNARIZED SIMULTANEOUSLY:")
        for test_key in sorted(all_layer_tests.keys()):
            deviations = all_layer_tests[test_key]
            if not deviations:
                continue
            angles = [d["angle_deg"] for d in deviations.values()]
            max_layer = max(deviations.keys(), key=lambda x: int(x))
            last = deviations[max_layer]
            print(f"    {test_key:<35} "
                  f"last_cos={last['cosine']:.4f}  "
                  f"last_angle={last['angle_deg']:.2f}°  "
                  f"mean_angle={np.mean(angles):.2f}°")

        # Per-layer isolation tests
        if per_layer_tests:
            print(f"\n  PER-LAYER ISOLATION (ternarize ONE layer, measure final output):")
            for test_key in sorted(per_layer_tests.keys()):
                devs = per_layer_tests[test_key]
                if not devs:
                    continue
                comp = test_key.replace("_per_layer_group", "")
                angles = []
                print(f"    {comp}:")
                for li in sorted(devs.keys(), key=lambda x: int(x)):
                    d = devs[li]
                    angles.append(d["angle_deg"])
                    marker = " ←" if d["angle_deg"] > 5.0 else ""
                    print(f"      L{int(li):>2}: cos={d['cosine']:.4f}  "
                          f"angle={d['angle_deg']:.2f}°{marker}")
                print(f"      MEAN: {np.mean(angles):.2f}°  MAX: {np.max(angles):.2f}°")


def print_cross_sentence_summary(results: dict):
    """Print summary across all sentences."""
    n_layers = results["n_layers"]
    n_sentences = len(results["sentences"])

    print(f"\n{'='*70}")
    print(f"CROSS-SENTENCE BEAM TRACE SUMMARY ({n_sentences} sentences)")
    print(f"{'='*70}")

    # Average beam divergence per layer
    print(f"\n  {'Layer':>5} {'Cos':>8} {'Angle':>8} "
          f"{'C_rot°':>8} {'N_rot°':>8} "
          f"{'Attn%':>7} {'FFN%':>7} "
          f"{'DiffRot':>8}")

    for li in range(n_layers):
        cosines = []
        angles = []
        c_rots = []
        n_rots = []
        attn_fracs = []
        ffn_fracs = []
        diff_rots = []

        for sent in results["sentences"]:
            if li in sent["layers"]:
                la = sent["layers"][li]
                cosines.append(la["beam_divergence"]["cosine"])
                angles.append(la["beam_divergence"]["angle_deg"])
                c_rots.append(la["compile_decomposition"]["angle_deg"])
                n_rots.append(la["null_decomposition"]["angle_deg"])
                attn_fracs.append(la["compile_attn_rotation_frac"])
                ffn_fracs.append(la["compile_ffn_rotation_frac"])
                diff_rots.append(la.get("differential_rotation_relative", 0))

        if cosines:
            print(f"  {li:>5} "
                  f"{np.mean(cosines):>8.4f} "
                  f"{np.mean(angles):>8.2f} "
                  f"{np.mean(c_rots):>8.2f} "
                  f"{np.mean(n_rots):>8.2f} "
                  f"{100*np.mean(attn_fracs):>6.1f}% "
                  f"{100*np.mean(ffn_fracs):>6.1f}% "
                  f"{np.mean(diff_rots):>8.3f}")


# ══════════════════════════════════════════════════════════════════
# JSON serialization helper
# ══════════════════════════════════════════════════════════════════

def make_serializable(obj):
    """Convert numpy types and nested dicts with int keys for JSON."""
    if isinstance(obj, dict):
        return {str(k): make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Beam trace probe — trace holographic beam through layers")
    parser.add_argument("--device", default="mps",
                        help="Device (mps, cpu, cuda)")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: 3 sentences only")
    parser.add_argument("--no-ternary", action="store_true",
                        help="Skip ternary beamformer test")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model, tokenizer = load_model(args.device)

    # Run analysis
    results = analyze_beam_trace(
        model, tokenizer, TEST_SENTENCES, quick=args.quick)

    # Print summaries
    print_cross_sentence_summary(results)
    print_ternary_summary(results)

    # Serialize for JSON
    save_results = make_serializable(results)

    # Save
    output_path = OUTPUT_DIR / "beam_trace_results.json"
    with open(output_path, "w") as f:
        json.dump(save_results, f, indent=2, default=str)
    print(f"\nSaved: {output_path}", file=sys.stderr)

    # Save compact summary
    summary = {
        "model": results["model"],
        "timestamp": results["timestamp"],
        "n_sentences": results["n_sentences"],
        "per_layer_averages": {},
    }
    for li in range(results["n_layers"]):
        cosines = []
        c_rots = []
        attn_fracs = []
        ffn_fracs = []
        diff_rots = []
        q_amps = []

        for sent in results["sentences"]:
            if li in sent["layers"]:
                la = sent["layers"][li]
                cosines.append(la["beam_divergence"]["cosine"])
                c_rots.append(la["compile_decomposition"]["angle_deg"])
                attn_fracs.append(la["compile_attn_rotation_frac"])
                ffn_fracs.append(la["compile_ffn_rotation_frac"])
                diff_rots.append(la.get("differential_rotation_relative", 0))
                q_amps.append(la["q_subspace"].get("q_amplification", 0))

        if cosines:
            summary["per_layer_averages"][li] = {
                "beam_cosine": float(np.mean(cosines)),
                "rotation_deg": float(np.mean(c_rots)),
                "attn_rotation_frac": float(np.mean(attn_fracs)),
                "ffn_rotation_frac": float(np.mean(ffn_fracs)),
                "differential_rotation": float(np.mean(diff_rots)),
                "q_amplification": float(np.mean(q_amps)),
            }

    summary_path = OUTPUT_DIR / "beam_trace_summary.json"
    with open(summary_path, "w") as f:
        json.dump(make_serializable(summary), f, indent=2)
    print(f"Saved: {summary_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
