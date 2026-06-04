#!/usr/bin/env python3
"""FFN β-Reduction Trace: Do FFNs compute reduction programs that attention executes?

HYPOTHESIS: Each FFN layer produces a list of β-reduction instructions —
neurons fire on input patterns (gate_proj keys) and emit transformation
directions (down_proj values). These directions are projected into the
residual stream where the NEXT attention layer routes values between
positions to execute those reductions.

The FFN is the COMPILER (produces the reduction program).
Attention is the EXECUTOR (carries out reductions by moving information).

MEASUREMENTS:
  1. For each FFN layer L:
     - Which neurons fire? (gate activation magnitude)
     - What do active neurons "say"? Project W_down[:, j] through unembed
       → top-k tokens each neuron promotes/suppresses
     - What is the "reduction program"? Aggregate active neuron outputs

  2. For attention at layer L+1:
     - What positions does each head connect? (attention patterns)
     - Do attention patterns correlate with FFN output directions?

  3. Compile gate vs null gate:
     - Does compile mode produce a DIFFERENT reduction program?
     - Which neurons are compile-selective? (fire in compile, silent in null)

  4. β-reduction signature:
     - In lambda calculus, β-reduction replaces (λx.M)N with M[x:=N]
     - If FFNs compute reductions: the active neuron pattern should change
       at token positions where application/abstraction occurs
     - Neurons at those positions should write directions that "substitute"
       (combine the function's body with the argument)

ARCHITECTURE (Qwen3-8B):
  Gated FFN: output = down_proj(SiLU(gate_proj(x)) * up_proj(x))
  - gate_proj.weight[j, :] = key (what triggers neuron j)
  - up_proj.weight[j, :]   = value (modulated by gate)
  - down_proj.weight[:, j]  = output direction (what neuron j writes)
  - 36 layers, 12288 intermediate, 4096 hidden, 151936 vocab

Usage:
  uv run python scripts/experiments/ffn_reduction_trace.py
  uv run python scripts/experiments/ffn_reduction_trace.py --layers 0,8,17,24,35
  uv run python scripts/experiments/ffn_reduction_trace.py --top-k 20

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
from dataclasses import dataclass, field

os.environ.setdefault("PYTHONUNBUFFERED", "1")

import numpy as np
import torch
import torch.nn.functional as F
from scipy import stats as scipy_stats

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


# ─── Data structures ────────────────────────────────────────────

@dataclass
class NeuronTrace:
    """What a single neuron says during a forward pass."""
    neuron_idx: int
    gate_activation: float        # scalar: how strongly it fired
    top_tokens_promote: list[tuple[str, float]]  # (token, logit) promoted
    top_tokens_suppress: list[tuple[str, float]]  # (token, logit) suppressed
    circuit_type: str             # projector/inverter/etc from cos(gate, down)


@dataclass
class LayerFFNTrace:
    """Complete FFN trace for one layer, one input position."""
    layer_idx: int
    position: int
    token: str
    n_active: int
    n_total: int
    active_fraction: float
    top_neurons: list[NeuronTrace]      # most active neurons
    aggregate_top_promote: list[tuple[str, float]]  # sum of active down_proj → unembed
    aggregate_top_suppress: list[tuple[str, float]]


@dataclass
class AttentionTrace:
    """Attention pattern at one layer."""
    layer_idx: int
    n_heads: int
    patterns: np.ndarray  # (n_heads, seq_len, seq_len) attention weights


@dataclass
class FullTrace:
    """Complete trace for one input."""
    prompt: str
    tokens: list[str]
    gate: str  # "compile" or "null"
    ffn_traces: dict[int, list[LayerFFNTrace]]   # layer_idx → per-position traces
    attn_traces: dict[int, AttentionTrace]        # layer_idx → attention patterns


# ─── Circuit type classification ────────────────────────────────

def classify_circuit(cos_val: float) -> str:
    if cos_val > 0.5:
        return "identity"
    elif cos_val > 0.2:
        return "transform"
    elif cos_val > -0.2:
        return "projector"
    elif cos_val > -0.5:
        return "suppressor"
    else:
        return "inverter"


# ─── Main experiment ────────────────────────────────────────────

def run_experiment(
    model_id: str = "Qwen/Qwen3-8B",
    layer_indices: list[int] | None = None,
    top_k: int = 10,
    n_top_neurons: int = 50,
    activation_threshold: float = 0.1,
):
    log("=" * 72)
    log("FFN β-REDUCTION TRACE")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Top-K tokens: {top_k}")
    log(f"Top neurons per position: {n_top_neurons}")
    log(f"Activation threshold: {activation_threshold}")
    log()

    from transformers import AutoModelForCausalLM, AutoTokenizer

    # ── Load model ──────────────────────────────────────────────
    log("Loading model...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="mps",
        low_cpu_mem_usage=True,
        attn_implementation="eager",
    )
    model.eval()
    dt = time.time() - t0
    log(f"  Loaded in {dt:.1f}s")

    config = model.config
    n_layers = config.num_hidden_layers
    hidden_size = config.hidden_size
    intermediate_size = config.intermediate_size
    vocab_size = config.vocab_size
    n_heads = config.num_attention_heads
    log(f"  {n_layers} layers, hidden={hidden_size}, intermediate={intermediate_size}")
    log(f"  {n_heads} heads, vocab={vocab_size}")

    # Default: sample across depth phases
    if layer_indices is None:
        # EXPAND(0-5), ORTHO(6-22), ALIGN(23-30), COLLAPSE(31-35)
        layer_indices = [0, 3, 6, 10, 14, 18, 22, 26, 30, 33, 35]
        layer_indices = [l for l in layer_indices if l < n_layers]
    log(f"  Tracing layers: {layer_indices}")

    # ── Get unembedding matrix ──────────────────────────────────
    if hasattr(model, 'lm_head'):
        W_unembed = model.lm_head.weight.data.cpu().float()  # (vocab, hidden)
    else:
        W_unembed = model.model.embed_tokens.weight.data.cpu().float()
    log(f"  W_unembed: {W_unembed.shape}")

    # ── Precompute cos(gate, down) for circuit types ────────────
    log("\nPrecomputing circuit types (cos(gate_proj, down_proj))...")
    circuit_cos = {}  # layer_idx → array of cos values per neuron
    for li in layer_indices:
        layer = model.model.layers[li]
        W_gate = layer.mlp.gate_proj.weight.data.cpu().float()  # (intermediate, hidden)
        W_down = layer.mlp.down_proj.weight.data.cpu().float()   # (hidden, intermediate)
        # cos(gate_row_j, down_col_j) for each neuron j
        gate_norms = W_gate.norm(dim=1)  # (intermediate,)
        down_norms = W_down.norm(dim=0)   # (intermediate,)
        cos_vals = (W_gate * W_down.T).sum(dim=1) / (gate_norms * down_norms + 1e-8)
        circuit_cos[li] = cos_vals.cpu().numpy()
        types = [classify_circuit(c) for c in circuit_cos[li]]
        from collections import Counter
        dist = Counter(types)
        log(f"  L{li}: " + " ".join(f"{t}={100*n/len(types):.0f}%" for t, n in dist.most_common()))

    # ── Define probes ───────────────────────────────────────────
    compile_gate = "The dog runs. → λx. runs(dog)\nBe helpful but concise. → λ assist(x). helpful(x) | concise(x)\n\nInput: "
    null_gate = "You are a helpful assistant. Respond naturally and concisely.\n\nInput: "

    probes = [
        "The dog runs.",
        "Every student reads a book.",
        "The cat that sat on the mat is black.",
        "If it rains, the ground is wet.",
        "Someone believes that the earth is flat.",
    ]

    # ── Hook setup ──────────────────────────────────────────────
    # We need to capture:
    #   1. Gate activations per neuron per position (from FFN)
    #   2. FFN output per position (the full down_proj output)
    #   3. Attention patterns per head (from attention)

    def trace_one(prompt: str, gate_name: str, gate_text: str) -> dict:
        """Run one forward pass and capture FFN + attention traces."""
        full_text = gate_text + prompt
        inputs = tokenizer(full_text, return_tensors="pt")
        input_ids = inputs["input_ids"].to(model.device)
        seq_len = input_ids.shape[1]

        # Find where the probe tokens start (after the gate)
        gate_only = tokenizer(gate_text, return_tensors="pt")
        gate_len = gate_only["input_ids"].shape[1]
        tokens = [tokenizer.decode(t) for t in input_ids[0]]

        log(f"\n  [{gate_name}] \"{prompt}\"")
        log(f"    Tokens ({seq_len}): {tokens[gate_len:]}")

        # Storage for hooks
        gate_activations = {}   # layer_idx → (seq_len, intermediate)
        ffn_outputs = {}        # layer_idx → (seq_len, hidden)
        attn_patterns = {}      # layer_idx → (n_heads, seq_len, seq_len)

        hooks = []

        for li in layer_indices:
            layer = model.model.layers[li]

            # ── FFN gate activation hook ────────────────────────
            # We hook the gate_proj output BEFORE SiLU
            # Actually we need the full gated activation = SiLU(gate(x)) * up(x)
            # Let's hook the MLP forward to capture intermediate values

            gate_act_storage = {}
            ffn_out_storage = {}

            def make_mlp_hook(layer_idx, ga_storage, fo_storage):
                def hook_fn(module, args, output):
                    x = args[0]  # input to MLP
                    with torch.no_grad():
                        gate_out = module.gate_proj(x)  # (batch, seq, intermediate)
                        gate_activated = module.act_fn(gate_out)  # SiLU(gate(x))
                        up_out = module.up_proj(x)
                        # The effective per-neuron activation (before down_proj)
                        neuron_activations = gate_activated * up_out  # (batch, seq, intermediate)
                        ga_storage[layer_idx] = neuron_activations[0].cpu().float()
                        fo_storage[layer_idx] = output[0].cpu().float() if isinstance(output, tuple) else output.cpu().float()
                return hook_fn

            h = layer.mlp.register_forward_hook(
                make_mlp_hook(li, gate_activations, ffn_outputs)
            )
            hooks.append(h)

            # ── Attention pattern hook ──────────────────────────
            # For the NEXT layer (L+1), capture attention patterns
            next_li = li + 1
            if next_li < n_layers and next_li not in [l for l in layer_indices]:
                # Also hook the next layer's attention
                pass  # We'll hook all layers in layer_indices AND their +1

            attn_storage = {}

            def make_attn_hook(layer_idx, storage):
                def hook_fn(module, args, kwargs, output):
                    # output is (attn_output, attn_weights, past_key_value)
                    # But we need to force output_attentions=True
                    # Actually, let's capture from the attention weights if available
                    if isinstance(output, tuple) and len(output) > 1 and output[1] is not None:
                        storage[layer_idx] = output[1][0].cpu().float().numpy()  # (n_heads, seq, seq)
                    return output
                return hook_fn

        # Remove previous hooks and set up fresh
        for h in hooks:
            h.remove()
        hooks.clear()

        # Re-register all hooks
        for li in layer_indices:
            layer = model.model.layers[li]
            h = layer.mlp.register_forward_hook(
                make_mlp_hook(li, gate_activations, ffn_outputs)
            )
            hooks.append(h)

        # We need attention weights — must pass output_attentions=True
        # But capturing all 36 layers of attention is expensive
        # Let's capture attention for layers that FOLLOW our FFN layers
        attn_layer_indices = sorted(set(
            [li + 1 for li in layer_indices if li + 1 < n_layers]
            + layer_indices  # also capture attention AT the same layer
        ))

        # Actually, let's use a simpler approach: capture attention at our target layers
        # The question is: does FFN at L predict attention at L (same layer, attn runs first)
        # or at L+1 (next layer)? In transformers: x → attn → ffn → next layer
        # So FFN at L writes to residual, then attention at L+1 reads it.
        # The prediction: FFN(L) output → attention(L+1) pattern.

        # Forward pass with output_attentions
        with torch.no_grad():
            outputs = model(
                input_ids,
                output_attentions=True,
                return_dict=True,
            )

        # Collect attention patterns
        all_attentions = outputs.attentions  # tuple of (batch, n_heads, seq, seq)
        for li in layer_indices:
            if li < len(all_attentions):
                attn_patterns[li] = all_attentions[li][0].cpu().float().numpy()
            # Also get L+1
            next_li = li + 1
            if next_li < len(all_attentions):
                attn_patterns[next_li] = all_attentions[next_li][0].cpu().float().numpy()

        # Now the MLP hooks should have fired during the forward pass
        # But wait — we used model() which doesn't go through our hooks
        # because output_attentions changes the path? Let's check.

        # Actually hooks fire regardless. But we need to re-run with hooks.
        # The forward pass above should have triggered the hooks.

        # Remove hooks
        for h in hooks:
            h.remove()
        hooks.clear()

        # ── Analyze FFN activations ─────────────────────────────
        result = {
            "prompt": prompt,
            "gate": gate_name,
            "tokens": tokens,
            "gate_len": gate_len,
            "seq_len": seq_len,
            "layers": {},
        }

        for li in layer_indices:
            if li not in gate_activations:
                log(f"    L{li}: no activation data (hook didn't fire)")
                continue

            acts = gate_activations[li]  # (seq_len, intermediate)

            # Focus on probe tokens (after gate prefix)
            layer_result = {
                "layer": li,
                "positions": [],
            }

            for pos in range(gate_len, seq_len):
                neuron_acts = acts[pos]  # (intermediate,)
                act_magnitudes = neuron_acts.abs()

                # Which neurons are active?
                active_mask = act_magnitudes > activation_threshold
                n_active = active_mask.sum().item()

                # Top-N most active neurons
                topk_vals, topk_idx = act_magnitudes.topk(min(n_top_neurons, intermediate_size))

                pos_result = {
                    "position": pos,
                    "token": tokens[pos],
                    "n_active": n_active,
                    "active_fraction": n_active / intermediate_size,
                    "top_neurons": [],
                }

                # For each top neuron, project through unembedding
                for rank, (val, idx) in enumerate(zip(topk_vals.tolist(), topk_idx.tolist())):
                    # What this neuron writes: down_proj.weight[:, idx]
                    W_down_col = model.model.layers[li].mlp.down_proj.weight.data[:, idx].cpu().float()

                    # Project through unembedding: logit contribution
                    logits = W_unembed @ W_down_col  # (vocab,)

                    # Scale by activation magnitude
                    signed_act = neuron_acts[idx].item()
                    logits_scaled = logits * signed_act

                    # Top-k promoted and suppressed tokens
                    top_promote = logits_scaled.topk(top_k)
                    top_suppress = (-logits_scaled).topk(top_k)

                    promote_tokens = [(tokenizer.decode(t.item()).strip(), v.item())
                                     for t, v in zip(top_promote.indices, top_promote.values)]
                    suppress_tokens = [(tokenizer.decode(t.item()).strip(), v.item())
                                      for t, v in zip(top_suppress.indices, top_suppress.values)]

                    circuit_type = classify_circuit(circuit_cos[li][idx])

                    pos_result["top_neurons"].append({
                        "neuron_idx": idx,
                        "activation": signed_act,
                        "abs_activation": val,
                        "circuit_type": circuit_type,
                        "promote": promote_tokens[:5],  # keep top 5 for readability
                        "suppress": suppress_tokens[:5],
                    })

                # Aggregate: sum of ALL active neurons' contributions
                if n_active > 0:
                    active_indices = active_mask.nonzero(as_tuple=True)[0]
                    W_down_active = model.model.layers[li].mlp.down_proj.weight.data[:, active_indices].cpu().float()
                    active_acts = neuron_acts[active_indices].float()
                    # Weighted sum of down_proj columns
                    aggregate_dir = W_down_active @ active_acts  # (hidden,)
                    aggregate_logits = W_unembed @ aggregate_dir  # (vocab,)

                    agg_top = aggregate_logits.topk(top_k)
                    agg_bot = (-aggregate_logits).topk(top_k)
                    pos_result["aggregate_promote"] = [
                        (tokenizer.decode(t.item()).strip(), v.item())
                        for t, v in zip(agg_top.indices, agg_top.values)
                    ]
                    pos_result["aggregate_suppress"] = [
                        (tokenizer.decode(t.item()).strip(), v.item())
                        for t, v in zip(agg_bot.indices, agg_bot.values)
                    ]
                else:
                    pos_result["aggregate_promote"] = []
                    pos_result["aggregate_suppress"] = []

                layer_result["positions"].append(pos_result)

            result["layers"][li] = layer_result

        # ── Attention pattern analysis ──────────────────────────
        result["attention"] = {}
        for li, pattern in attn_patterns.items():
            # pattern: (n_kv_heads_or_heads, seq, seq) — may be GQA
            # For each head, what's the dominant attention pattern for probe tokens?
            head_summaries = []
            actual_heads = pattern.shape[0]
            for h in range(actual_heads):
                # Focus on probe token positions attending to other probe tokens
                probe_attn = pattern[h, gate_len:, gate_len:]  # (n_probe, n_probe)
                # What fraction of attention goes to each position?
                # Mean attention from each probe position
                mean_attn = probe_attn.mean(axis=0)  # (n_probe,)
                head_summaries.append({
                    "head": h,
                    "mean_attn_to_probe_positions": mean_attn.tolist(),
                    "max_attn_position": int(np.argmax(mean_attn)),
                    "entropy": float(-np.sum(probe_attn * np.log(probe_attn + 1e-10)) / probe_attn.shape[0]),
                })
            result["attention"][li] = {
                "n_heads": actual_heads,
                "heads": head_summaries,
            }

        return result

    # ── Run all probes under both gates ─────────────────────────
    all_results = []
    for probe in probes:
        log(f"\n{'─' * 60}")
        log(f"PROBE: {probe}")

        compile_result = trace_one(probe, "compile", compile_gate)
        all_results.append(compile_result)

        null_result = trace_one(probe, "null", null_gate)
        all_results.append(null_result)

        # ── Compare compile vs null for this probe ──────────
        log(f"\n  COMPILE vs NULL comparison:")
        for li in layer_indices:
            if li not in compile_result["layers"] or li not in null_result["layers"]:
                continue
            c_layer = compile_result["layers"][li]
            n_layer = null_result["layers"][li]

            # Compare active fractions
            c_fracs = [p["active_fraction"] for p in c_layer["positions"]]
            n_fracs = [p["active_fraction"] for p in n_layer["positions"]]
            c_mean = np.mean(c_fracs) if c_fracs else 0
            n_mean = np.mean(n_fracs) if n_fracs else 0

            log(f"    L{li:2d}: compile_active={c_mean:.3f} null_active={n_mean:.3f} "
                f"delta={c_mean - n_mean:+.3f}")

    # ── Cross-layer analysis: FFN → Attention correlation ───────
    log(f"\n{'=' * 72}")
    log("FFN → ATTENTION CORRELATION ANALYSIS")
    log("=" * 72)

    for result in all_results:
        log(f"\n  [{result['gate']}] \"{result['prompt']}\"")
        gate_len = result["gate_len"]
        tokens = result["tokens"]

        for li in layer_indices:
            next_li = li + 1
            if li not in result["layers"] or next_li not in result.get("attention", {}):
                continue

            ffn_layer = result["layers"][li]
            attn_next = result["attention"][next_li]

            # For each position, does the FFN output direction correlate with
            # where attention sends information?

            # Simple measure: does the aggregate promote direction at position p
            # correlate with which positions attend TO p at the next layer?
            log(f"    L{li} FFN → L{next_li} Attn:")

            for pos_data in ffn_layer["positions"]:
                pos = pos_data["position"]
                tok = pos_data["token"]
                n_active = pos_data["n_active"]

                # What does this position's FFN say?
                if pos_data["aggregate_promote"]:
                    top3 = [t for t, v in pos_data["aggregate_promote"][:3]]
                else:
                    top3 = ["(none)"]

                # How much attention does this position RECEIVE at L+1?
                # (columns of attention matrix = who is attended to)
                rel_pos = pos - gate_len
                if rel_pos < 0:
                    continue
                received = []
                for h_data in attn_next["heads"]:
                    mean_attn = h_data["mean_attn_to_probe_positions"]
                    if rel_pos < len(mean_attn):
                        received.append(mean_attn[rel_pos])

                avg_received = np.mean(received) if received else 0

                log(f"      pos={pos} [{tok:>12s}] active={n_active:5d} "
                    f"promotes=[{', '.join(top3):>30s}] "
                    f"attn_received={avg_received:.3f}")

    # ── Position-level reduction signature ──────────────────────
    log(f"\n{'=' * 72}")
    log("POSITION-LEVEL REDUCTION SIGNATURE")
    log("=" * 72)
    log("Looking for β-reduction signatures: do function/argument positions")
    log("show different neuron activation patterns?")
    log()

    for result in all_results:
        if result["gate"] != "compile":
            continue
        log(f"\n  \"{result['prompt']}\"")
        gate_len = result["gate_len"]
        tokens = result["tokens"]

        for li in layer_indices[:5]:  # Show first 5 layers for readability
            if li not in result["layers"]:
                continue
            ffn_layer = result["layers"][li]

            log(f"\n    L{li}:")
            for pos_data in ffn_layer["positions"]:
                pos = pos_data["position"]
                tok = pos_data["token"]
                n_active = pos_data["n_active"]
                frac = pos_data["active_fraction"]

                # Circuit type distribution of top neurons
                from collections import Counter
                ct_dist = Counter(n["circuit_type"] for n in pos_data["top_neurons"][:20])
                ct_str = " ".join(f"{t[0]}:{n}" for t, n in ct_dist.most_common(3))

                # Top 3 things this position promotes
                if pos_data["aggregate_promote"]:
                    top3 = [f"{t}({v:.1f})" for t, v in pos_data["aggregate_promote"][:3]]
                else:
                    top3 = ["(none)"]

                log(f"      [{tok:>12s}] active={frac:.2%} types=[{ct_str:>20s}] "
                    f"→ [{', '.join(top3)}]")

    # ── Save results ────────────────────────────────────────────
    results_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "results", "ffn-reduction-trace"
    )
    os.makedirs(results_dir, exist_ok=True)

    # Save summary (without huge attention matrices)
    summary = {
        "model": model_id,
        "layers_traced": layer_indices,
        "n_probes": len(probes),
        "probes": probes,
        "top_k": top_k,
        "n_top_neurons": n_top_neurons,
        "activation_threshold": activation_threshold,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # Compile-selective neurons: fire more in compile than null
    log(f"\n{'=' * 72}")
    log("COMPILE-SELECTIVE NEURONS")
    log("=" * 72)

    for li in layer_indices:
        compile_acts = []
        null_acts = []
        for result in all_results:
            if li not in result["layers"]:
                continue
            for pos_data in result["layers"][li]["positions"]:
                acts = {n["neuron_idx"]: n["activation"] for n in pos_data["top_neurons"]}
                if result["gate"] == "compile":
                    compile_acts.append(acts)
                else:
                    null_acts.append(acts)

        if not compile_acts or not null_acts:
            continue

        # Find neurons that appear in compile but not null (or vice versa)
        all_compile_neurons = set()
        all_null_neurons = set()
        for acts in compile_acts:
            all_compile_neurons.update(acts.keys())
        for acts in null_acts:
            all_null_neurons.update(acts.keys())

        compile_only = all_compile_neurons - all_null_neurons
        null_only = all_null_neurons - all_compile_neurons
        shared = all_compile_neurons & all_null_neurons

        log(f"\n  L{li}: compile_only={len(compile_only)} null_only={len(null_only)} "
            f"shared={len(shared)}")

        # For shared neurons, which ones have the biggest activation difference?
        if shared:
            diffs = []
            for nidx in shared:
                c_mean = np.mean([acts.get(nidx, 0) for acts in compile_acts])
                n_mean = np.mean([acts.get(nidx, 0) for acts in null_acts])
                diffs.append((nidx, c_mean - n_mean, c_mean, n_mean))
            diffs.sort(key=lambda x: abs(x[1]), reverse=True)

            log(f"    Top compile-biased neurons:")
            for nidx, diff, c_mean, n_mean in diffs[:5]:
                ct = classify_circuit(circuit_cos[li][nidx])
                log(f"      neuron {nidx}: compile={c_mean:.3f} null={n_mean:.3f} "
                    f"delta={diff:+.3f} type={ct}")

            log(f"    Top null-biased neurons:")
            for nidx, diff, c_mean, n_mean in sorted(diffs, key=lambda x: x[1])[:5]:
                ct = classify_circuit(circuit_cos[li][nidx])
                log(f"      neuron {nidx}: compile={c_mean:.3f} null={n_mean:.3f} "
                    f"delta={diff:+.3f} type={ct}")

    # ── Depth profile of reduction activity ─────────────────────
    log(f"\n{'=' * 72}")
    log("DEPTH PROFILE: WHERE IS THE REDUCTION PROGRAM WRITTEN?")
    log("=" * 72)

    for gate_name in ["compile", "null"]:
        log(f"\n  [{gate_name}]:")
        for li in layer_indices:
            fracs = []
            n_actives = []
            for result in all_results:
                if result["gate"] != gate_name or li not in result["layers"]:
                    continue
                for pos_data in result["layers"][li]["positions"]:
                    fracs.append(pos_data["active_fraction"])
                    n_actives.append(pos_data["n_active"])

            if fracs:
                mean_frac = np.mean(fracs)
                std_frac = np.std(fracs)
                mean_active = np.mean(n_actives)
                log(f"    L{li:2d}: active={mean_frac:.3f}±{std_frac:.3f} "
                    f"({mean_active:.0f}/{intermediate_size} neurons)")

    # Save compact results
    compact_results = []
    for result in all_results:
        compact = {
            "prompt": result["prompt"],
            "gate": result["gate"],
            "tokens": result["tokens"][result["gate_len"]:],
            "layers": {},
        }
        for li, layer_data in result["layers"].items():
            compact["layers"][str(li)] = {
                "positions": [
                    {
                        "token": p["token"],
                        "n_active": p["n_active"],
                        "active_fraction": p["active_fraction"],
                        "top_5_promote": p["aggregate_promote"][:5] if p.get("aggregate_promote") else [],
                        "top_5_suppress": p["aggregate_suppress"][:5] if p.get("aggregate_suppress") else [],
                        "top_3_neurons": [
                            {
                                "idx": n["neuron_idx"],
                                "act": round(n["activation"], 4),
                                "type": n["circuit_type"],
                                "promote": n["promote"][:3],
                            }
                            for n in p["top_neurons"][:3]
                        ],
                    }
                    for p in layer_data["positions"]
                ],
            }
        compact_results.append(compact)

    summary["results"] = compact_results

    summary_path = os.path.join(results_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    log(f"\nResults saved to {results_dir}/")
    log(f"  summary.json: {os.path.getsize(summary_path) / 1024:.1f} KB")

    # ── Final summary ───────────────────────────────────────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT COMPLETE")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Layers traced: {layer_indices}")
    log(f"Probes: {len(probes)} × 2 gates = {len(all_results)} forward passes")
    log()

    return all_results


def main():
    parser = argparse.ArgumentParser(description="FFN β-Reduction Trace")
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", default=None, help="Comma-separated layer indices")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--top-neurons", type=int, default=50)
    parser.add_argument("--threshold", type=float, default=0.1)
    args = parser.parse_args()

    layer_indices = None
    if args.layers:
        layer_indices = [int(l) for l in args.layers.split(",")]

    run_experiment(
        model_id=args.model,
        layer_indices=layer_indices,
        top_k=args.top_k,
        n_top_neurons=args.top_neurons,
        activation_threshold=args.threshold,
    )


if __name__ == "__main__":
    main()
