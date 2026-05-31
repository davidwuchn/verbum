"""Reduction Graph Tracer — Decode FFN→Attention computation as beta reduction graph.

Session 174. Tests the hypothesis:
  FFN proposes reductions (via gating) → Attention executes them (via routing)

For each input:
  1. At each layer, capture FFN gate activations (which neurons survive)
  2. Project surviving activations onto combinator fingerprints → decode per-position opcodes
  3. Capture attention patterns
  4. Check: does attention preferentially route between positions with compatible operations?
     (e.g., β_apply source → argument target)

Comparison: lambda input (should show structured reduction graph) vs neutral text (less structured).

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/reduction_graph_tracer.py
    uv run python scripts/experiments/reduction_graph_tracer.py --model Qwen/Qwen3-4B

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ══════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════

RESULTS_BASE = Path(__file__).parent.parent.parent / "results" / "reduction-graph"
HOLOGRAM_BASE = Path(__file__).parent.parent.parent / "results" / "hologram-reader"
FINGERPRINT_BASE = Path(__file__).parent.parent.parent / "results" / "hologram-reader"

# Combinator names matching hologram reader
ALL_OPS = ["K", "I", "B", "C", "D", "Y", "W", "WHNF", "beta_K", "beta_I", "beta_apply", "beta_compose"]

# Test inputs — lambda expression vs neutral control
INPUTS = {
    "lambda_apply": "λx.λy.(x y) applied to (λz.z) gives",
    "lambda_compose": "(B f g) x reduces to f (g x) because composition",
    "lambda_church": "λf.λx.(f (f x)) is the Church numeral for 2",
    "neutral_factual": "The capital of France is Paris which is a large city",
    "neutral_simple": "The cat sat on the mat and looked at the birds",
    "code_function": "def apply(f, x): return f(x)  # beta reduction in Python",
}

# Zone boundaries for 0.6B (from hologram reader)
ZONES_06B = {
    "SILENT": (0, 13),
    "ENRICH": (14, 22),
    "SUPPRESS": (23, 25),
    "COMMIT": (26, 27),
}


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Load combinator fingerprints
# ══════════════════════════════════════════════════════════════════════

def load_fingerprints(model_name: str) -> dict[str, np.ndarray]:
    """Load per-layer combinator direction fingerprints. Shape: (n_layers, d_model)."""
    model_slug = model_name.replace("/", "_")
    fp_path = FINGERPRINT_BASE / model_slug / f"fingerprints_{model_slug}.npz"
    if not fp_path.exists():
        raise FileNotFoundError(f"No fingerprints at {fp_path}. Run hologram_reader.py first.")
    data = np.load(fp_path)
    fps = {op: data[op] for op in ALL_OPS if op in data}
    log(f"Loaded {len(fps)} combinator fingerprints, shape {list(fps.values())[0].shape}")
    return fps


# ══════════════════════════════════════════════════════════════════════
# Model loading and hooking
# ══════════════════════════════════════════════════════════════════════

@dataclass
class LayerTrace:
    """Captured activations from one layer for one input."""
    layer_idx: int
    # Per-position combinator energy: shape (seq_len, n_ops)
    op_energy: np.ndarray
    # Per-position dominant opcode
    dominant_ops: list[str]
    # Gate survival rate per position
    gate_survival: np.ndarray
    # Attention pattern: shape (n_heads, seq_len, seq_len)
    attention: np.ndarray


@dataclass
class ForwardTrace:
    """Complete trace of one forward pass."""
    input_text: str
    input_key: str
    tokens: list[str]
    n_layers: int
    layers: list[LayerTrace] = field(default_factory=list)


def trace_forward(
    model,
    tokenizer,
    fingerprints: dict[str, np.ndarray],
    input_text: str,
    input_key: str,
    device: str = "mps",
) -> ForwardTrace:
    """Run forward pass with hooks, decode reduction graph."""

    # Tokenize
    inputs = tokenizer(input_text, return_tensors="pt").to(device)
    input_ids = inputs["input_ids"]
    seq_len = input_ids.shape[1]
    tokens = [tokenizer.decode(t) for t in input_ids[0]]

    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    n_ops = len(ALL_OPS)

    # Storage for hook captures
    gate_acts = {}  # layer_idx -> (seq_len, d_ff)
    ffn_outputs = {}  # layer_idx -> (seq_len, d_model)
    attention_weights = {}  # layer_idx -> (n_heads, seq_len, seq_len)
    hidden_states = {}  # layer_idx -> (seq_len, d_model) — input to FFN

    # Register hooks
    hooks = []

    def make_gate_hook(layer_idx):
        """Hook into the gate projection to capture which neurons fire."""
        def hook_fn(module, input, output):
            # For Qwen2-style SwiGLU: gate_proj output before activation
            # The actual gating is: act(gate_proj(x)) * up_proj(x)
            # We want the gate values to know which neurons survive
            gate_acts[layer_idx] = output.detach().cpu().numpy()[0]  # (seq_len, d_ff)
        return hook_fn

    def make_ffn_output_hook(layer_idx):
        """Capture FFN output (what gets added to residual)."""
        def hook_fn(module, input, output):
            ffn_outputs[layer_idx] = output.detach().cpu().numpy()[0]  # (seq_len, d_model)
        return hook_fn

    def make_attn_hook(layer_idx):
        """Capture attention weights."""
        def hook_fn(module, input, output):
            # output is typically (attn_output, attn_weights, past_kv) or just attn_output
            if isinstance(output, tuple) and len(output) >= 2 and output[1] is not None:
                attention_weights[layer_idx] = output[1].detach().cpu().numpy()[0]  # (n_heads, seq_len, seq_len)
        return hook_fn

    def make_hidden_hook(layer_idx):
        """Capture hidden state entering the FFN (post-attention residual)."""
        def hook_fn(module, input, output):
            # input to MLP is the post-attention hidden state
            if isinstance(input, tuple):
                hidden_states[layer_idx] = input[0].detach().cpu().numpy()[0]  # (seq_len, d_model)
            else:
                hidden_states[layer_idx] = input.detach().cpu().numpy()[0]
        return hook_fn

    for i in range(n_layers):
        layer = model.model.layers[i]
        # Hook gate_proj to get gating signal
        hooks.append(layer.mlp.gate_proj.register_forward_hook(make_gate_hook(i)))
        # Hook MLP module to get FFN output
        hooks.append(layer.mlp.register_forward_hook(make_ffn_output_hook(i)))
        # Hook the MLP's forward to get its input hidden state
        hooks.append(layer.mlp.register_forward_hook(make_hidden_hook(i)))
        # Hook attention to get weights (need output_attentions=True)
        hooks.append(layer.self_attn.register_forward_hook(make_attn_hook(i)))

    # Forward pass with attention output
    with torch.no_grad():
        outputs = model(
            **inputs,
            output_attentions=True,
            return_dict=True,
        )

    # Extract attention weights from model output if hooks didn't capture
    if not attention_weights and hasattr(outputs, 'attentions') and outputs.attentions is not None:
        for i, attn in enumerate(outputs.attentions):
            attention_weights[i] = attn.detach().cpu().numpy()[0]  # (n_heads, seq_len, seq_len)

    # Remove hooks
    for h in hooks:
        h.remove()

    # ══════════════════════════════════════════════════════════════════
    # Decode: project FFN output onto combinator fingerprints
    # ══════════════════════════════════════════════════════════════════

    trace = ForwardTrace(
        input_text=input_text,
        input_key=input_key,
        tokens=tokens,
        n_layers=n_layers,
    )

    for layer_idx in range(n_layers):
        # Get the FFN contribution to residual stream
        if layer_idx not in ffn_outputs:
            continue

        ffn_out = ffn_outputs[layer_idx]  # (seq_len, d_model)

        # Gate survival: fraction of neurons that survived SwiGLU
        gate_survival = np.zeros(seq_len)
        if layer_idx in gate_acts:
            # SwiGLU: act(gate) * up  → neuron "fires" where act(gate) > 0
            # For SiLU: silu(x) > 0 iff x > ~-0.278 (but magnitude matters)
            # Use |silu(gate)| > small_threshold
            from scipy.special import expit  # sigmoid
            gate_raw = gate_acts[layer_idx]  # (seq_len, d_ff)
            # SiLU(x) = x * sigmoid(x)
            gate_activated = gate_raw * expit(gate_raw)
            gate_survival = (np.abs(gate_activated) > 0.01).mean(axis=1)  # fraction per position

        # Project FFN output onto each combinator fingerprint
        op_energy = np.zeros((seq_len, n_ops))
        for op_idx, op_name in enumerate(ALL_OPS):
            if op_name not in fingerprints:
                continue
            fp = fingerprints[op_name][layer_idx]  # (d_model,)
            # Normalize fingerprint
            fp_norm = fp / (np.linalg.norm(fp) + 1e-8)
            # Project each position's FFN output onto this direction
            # Dot product gives alignment strength
            op_energy[:, op_idx] = ffn_out @ fp_norm  # (seq_len,)

        # Dominant opcode per position
        dominant_idx = np.argmax(np.abs(op_energy), axis=1)
        dominant_ops = [ALL_OPS[idx] for idx in dominant_idx]

        # Get attention for this layer
        attn = attention_weights.get(layer_idx)
        if attn is None:
            attn = np.zeros((1, seq_len, seq_len))

        trace.layers.append(LayerTrace(
            layer_idx=layer_idx,
            op_energy=op_energy,
            dominant_ops=dominant_ops,
            gate_survival=gate_survival,
            attention=attn,
        ))

    return trace


# ══════════════════════════════════════════════════════════════════════
# Analysis: Reduction graph coherence
# ══════════════════════════════════════════════════════════════════════

def analyze_reduction_graph(trace: ForwardTrace) -> dict[str, Any]:
    """Analyze whether attention routes along valid reduction edges.

    A 'valid reduction edge' is when:
    - Position A has high β_apply energy (it's a function wanting to apply)
    - Position B is nearby and has high I/K/argument energy
    - Attention from A→B or B→A is high

    We measure: what fraction of top attention flows along β_apply edges
    vs random edges.
    """
    results = {
        "input_key": trace.input_key,
        "input_text": trace.input_text,
        "tokens": trace.tokens,
        "n_tokens": len(trace.tokens),
        "per_layer": [],
    }

    for lt in trace.layers:
        layer_result = {
            "layer": lt.layer_idx,
            "gate_survival_mean": float(lt.gate_survival.mean()),
            "gate_survival_std": float(lt.gate_survival.std()),
        }

        # Per-position dominant opcode
        layer_result["dominant_ops"] = lt.dominant_ops

        # Op energy statistics
        op_energy_abs = np.abs(lt.op_energy)
        # Top opcode energy per position
        layer_result["top_op_energy_mean"] = float(op_energy_abs.max(axis=1).mean())

        # Combinator energy breakdown (mean absolute across positions)
        op_means = {}
        for op_idx, op_name in enumerate(ALL_OPS):
            op_means[op_name] = float(op_energy_abs[:, op_idx].mean())
        layer_result["op_energy_means"] = op_means

        # ── Reduction edge analysis ──
        # Find positions with high β_apply (proposing application)
        beta_apply_idx = ALL_OPS.index("beta_apply")
        beta_apply_energy = lt.op_energy[:, beta_apply_idx]  # (seq_len,)

        # Find positions with high argument energy (K, I, or general combinator)
        # These are potential "argument" positions for apply
        arg_energy = op_energy_abs[:, :8].max(axis=1)  # max of K,I,B,C,D,Y,W,WHNF

        seq_len = len(trace.tokens)
        if seq_len < 2 or lt.attention.shape[-1] != seq_len:
            layer_result["reduction_edge_score"] = None
            results["per_layer"].append(layer_result)
            continue

        # Average attention across heads
        attn_avg = lt.attention.mean(axis=0)  # (seq_len, seq_len)

        # Score: how much attention flows FROM high-β_apply positions TO high-arg positions
        # Normalize energies to [0, 1]
        ba_range = beta_apply_energy.max() - beta_apply_energy.min()
        arg_range = arg_energy.max() - arg_energy.min()
        ba_norm = (beta_apply_energy - beta_apply_energy.min()) / (ba_range + 1e-8)
        arg_norm = (arg_energy - arg_energy.min()) / (arg_range + 1e-8)

        # Reduction edge weight matrix: source has β_apply, target has argument
        reduction_edges = np.outer(ba_norm, arg_norm)  # (seq_len, seq_len)
        # Zero diagonal (no self-reduction)
        np.fill_diagonal(reduction_edges, 0)

        # How much attention aligns with reduction edges?
        # Weighted correlation: do high-attention edges coincide with high-reduction edges?
        attn_flat = attn_avg.flatten()
        reduc_flat = reduction_edges.flatten()

        # Normalize for correlation
        if attn_flat.std() > 1e-8 and reduc_flat.std() > 1e-8:
            corr = np.corrcoef(attn_flat, reduc_flat)[0, 1]
        else:
            corr = 0.0

        layer_result["reduction_edge_correlation"] = float(corr)

        # Also: fraction of top-K attention that flows along reduction edges
        k = min(20, seq_len * seq_len // 4)
        top_attn_idx = np.argsort(attn_flat)[-k:]
        top_reduc_idx = np.argsort(reduc_flat)[-k:]
        overlap = len(set(top_attn_idx) & set(top_reduc_idx))
        layer_result["top_edge_overlap_frac"] = float(overlap / k)

        # β_apply concentration: does β_apply energy vary by position or is it uniform?
        layer_result["beta_apply_std"] = float(beta_apply_energy.std())
        layer_result["beta_apply_mean"] = float(beta_apply_energy.mean())

        results["per_layer"].append(layer_result)

    # ── Summary statistics ──
    correlations = [
        lr["reduction_edge_correlation"]
        for lr in results["per_layer"]
        if lr.get("reduction_edge_correlation") is not None
    ]
    if correlations:
        results["summary"] = {
            "mean_reduction_correlation": float(np.mean(correlations)),
            "max_reduction_correlation": float(np.max(correlations)),
            "std_reduction_correlation": float(np.std(correlations)),
            # By zone
            "zone_correlations": {},
        }
        # Zone breakdown (for 0.6B)
        for zone_name, (start, end) in ZONES_06B.items():
            zone_corrs = [
                lr["reduction_edge_correlation"]
                for lr in results["per_layer"]
                if lr.get("reduction_edge_correlation") is not None
                and start <= lr["layer"] <= end
            ]
            if zone_corrs:
                results["summary"]["zone_correlations"][zone_name] = {
                    "mean": float(np.mean(zone_corrs)),
                    "max": float(np.max(zone_corrs)),
                }
    else:
        results["summary"] = {"mean_reduction_correlation": None}

    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Trace reduction graph through model")
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B", help="HuggingFace model name")
    parser.add_argument("--device", default="mps", help="Device (mps, cuda, cpu)")
    parser.add_argument("--inputs", nargs="*", default=None, help="Subset of input keys to run")
    args = parser.parse_args()

    model_name = args.model
    model_slug = model_name.replace("/", "_")
    device = args.device

    log(f"═══ Reduction Graph Tracer ═══")
    log(f"Model: {model_name}")
    log(f"Device: {device}")

    # Load fingerprints
    fingerprints = load_fingerprints(model_name)

    # Load model
    log(f"Loading model...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,  # float32 for MPS compatibility
        trust_remote_code=True,
        attn_implementation="eager",  # need attention weights
    ).to(device)
    model.eval()
    log(f"Model loaded in {time.time() - t0:.1f}s")

    # Select inputs
    input_keys = args.inputs or list(INPUTS.keys())
    inputs_to_run = {k: INPUTS[k] for k in input_keys if k in INPUTS}

    # Run traces
    all_results = {}
    for key, text in inputs_to_run.items():
        log(f"\n─── Tracing: {key} ───")
        log(f"  Text: {text[:60]}...")

        trace = trace_forward(model, tokenizer, fingerprints, text, key, device)
        log(f"  Tokens: {len(trace.tokens)}, Layers traced: {len(trace.layers)}")

        result = analyze_reduction_graph(trace)
        all_results[key] = result

        # Print summary
        if result["summary"]["mean_reduction_correlation"] is not None:
            log(f"  Mean reduction correlation: {result['summary']['mean_reduction_correlation']:.4f}")
            log(f"  Max reduction correlation:  {result['summary']['max_reduction_correlation']:.4f}")
            if result["summary"].get("zone_correlations"):
                for zone, zc in result["summary"]["zone_correlations"].items():
                    log(f"    {zone:10s}: mean={zc['mean']:.4f}  max={zc['max']:.4f}")

    # ── Comparison ──
    log(f"\n═══ COMPARISON ═══")
    lambda_keys = [k for k in all_results if k.startswith("lambda_")]
    neutral_keys = [k for k in all_results if k.startswith("neutral_")]

    lambda_corrs = [
        all_results[k]["summary"]["mean_reduction_correlation"]
        for k in lambda_keys
        if all_results[k]["summary"]["mean_reduction_correlation"] is not None
    ]
    neutral_corrs = [
        all_results[k]["summary"]["mean_reduction_correlation"]
        for k in neutral_keys
        if all_results[k]["summary"]["mean_reduction_correlation"] is not None
    ]

    if lambda_corrs and neutral_corrs:
        lambda_mean = np.mean(lambda_corrs)
        neutral_mean = np.mean(neutral_corrs)
        log(f"  Lambda inputs mean correlation:  {lambda_mean:.4f}")
        log(f"  Neutral inputs mean correlation: {neutral_mean:.4f}")
        log(f"  Ratio (lambda/neutral):          {lambda_mean / (neutral_mean + 1e-8):.2f}x")
    else:
        log(f"  Insufficient data for comparison")

    # ── Per-layer opcode decode (show first lambda input) ──
    if lambda_keys:
        first_lambda = all_results[lambda_keys[0]]
        log(f"\n═══ OPCODE DECODE: {lambda_keys[0]} ═══")
        log(f"  Tokens: {first_lambda['tokens']}")
        # Show a few representative layers
        for lr in first_lambda["per_layer"]:
            if lr["layer"] in [0, 7, 14, 21, 26, 27]:  # one from each zone
                log(f"\n  Layer {lr['layer']:2d} (gate_survival={lr['gate_survival_mean']:.3f}):")
                log(f"    Dominant ops: {lr['dominant_ops']}")
                top_ops = sorted(lr["op_energy_means"].items(), key=lambda x: -x[1])[:4]
                log(f"    Top energy:   {', '.join(f'{k}={v:.3f}' for k, v in top_ops)}")

    # Save results
    out_dir = RESULTS_BASE / model_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "reduction_graph_results.json"

    # Convert numpy for JSON serialization
    def jsonify(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, dict):
            return {k: jsonify(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [jsonify(v) for v in obj]
        return obj

    with open(out_path, "w") as f:
        json.dump(jsonify(all_results), f, indent=2)
    log(f"\nResults saved to {out_path}")

    # Also save a compact summary
    summary = {
        "model": model_name,
        "inputs": {k: v["summary"] for k, v in all_results.items()},
        "comparison": {
            "lambda_mean_corr": float(np.mean(lambda_corrs)) if lambda_corrs else None,
            "neutral_mean_corr": float(np.mean(neutral_corrs)) if neutral_corrs else None,
            "ratio": float(np.mean(lambda_corrs) / (np.mean(neutral_corrs) + 1e-8)) if lambda_corrs and neutral_corrs else None,
        },
    }
    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    log(f"Summary saved to {out_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
