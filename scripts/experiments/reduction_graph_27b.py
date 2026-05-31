"""Reduction Graph Tracer — Qwen3.6-27B (hybrid Mamba + full attention).

Session 174. Traces computation graph through the 27B model.
Architecture: 64 layers, hybrid [L,L,L,F]×16 (17 full attention + 48 linear attention).
  - All 64 layers have SwiGLU MLP (gate_proj, up_proj, down_proj)
  - 17 layers have full self-attention (can output attention weights)
  - 48 layers have linear attention (Mamba-style, no discrete attention matrix)

This means: the FFN opcode decode works on ALL 64 layers, but attention
routing analysis only applies to the 17 full-attention layers.

Key: Qwen3.6-27B is a multimodal model. We load via Qwen3_5ForConditionalGeneration
and access the language model backbone.

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/reduction_graph_27b.py

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

# ══════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════

RESULTS_BASE = Path(__file__).parent.parent.parent / "results" / "reduction-graph"
FINGERPRINT_PATH = (
    Path(__file__).parent.parent.parent
    / "results" / "hologram-reader" / "Qwen_Qwen3.6-27B"
    / "fingerprints_Qwen_Qwen3.6-27B.npz"
)

ALL_OPS = ["K", "I", "B", "C", "D", "Y", "W", "WHNF", "beta_K", "beta_I", "beta_apply", "beta_compose"]
N_OPS = len(ALL_OPS)

# Zone boundaries for 27B (from hologram reader)
ZONES = {
    "SILENT": (0, 31),
    "ENRICH": (32, 53),
    "SUPPRESS": (54, 58),
    "COMMIT": (59, 63),
}

# Full attention layers (every 4th, starting pattern)
FULL_ATTN_LAYERS = [0, 3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63]

# Test inputs
INPUTS = {
    "lambda_apply": "λx.λy.(x y) applied to (λz.z) gives",
    "lambda_compose": "(B f g) x reduces to f (g x) because composition",
    "lambda_church": "λf.λx.(f (f x)) is the Church numeral for 2",
    "lambda_reduce": "(λx.(x x)) (λy.y) beta-reduces to (λy.y) (λy.y) which gives (λy.y)",
    "neutral_factual": "The capital of France is Paris which is a large city",
    "neutral_simple": "The cat sat on the mat and looked at the birds",
    "code_function": "def apply(f, x): return f(x)  # beta reduction in Python",
}


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Load and trace
# ════════════════════════════════════════════════════════════���═════════

def main():
    log("═══ Reduction Graph Tracer — Qwen3.6-27B ═══")
    log(f"Fingerprints: {FINGERPRINT_PATH}")

    # Load fingerprints
    fps_data = np.load(FINGERPRINT_PATH)
    fingerprints = {op: fps_data[op] for op in ALL_OPS if op in fps_data}
    log(f"Loaded {len(fingerprints)} fingerprints, shape {fingerprints['K'].shape}")
    # (64, 5120)

    # Load model
    log("Loading Qwen3.6-27B (bf16, MPS)...")
    t0 = time.time()

    model_name = "Qwen/Qwen3.6-27B"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    # Load the full model — we'll access .model.language_model for text
    from transformers import Qwen3_5ForConditionalGeneration
    model = Qwen3_5ForConditionalGeneration.from_pretrained(
        model_name,
        dtype=torch.bfloat16,
        trust_remote_code=True,
        attn_implementation="eager",  # need attention weights for full-attn layers
    ).to("mps")
    model.eval()

    # Access the language model backbone
    lm = model.model.language_model  # This should have .layers, .embed_tokens, etc.
    n_layers = len(lm.layers)
    log(f"Model loaded in {time.time()-t0:.1f}s — {n_layers} layers")

    # Verify layer structure
    layer0 = lm.layers[0]
    has_mlp = hasattr(layer0, 'mlp') and hasattr(layer0.mlp, 'gate_proj')
    has_linear = hasattr(layer0, 'linear_attn')
    has_full = hasattr(layer0, 'self_attn')
    log(f"Layer 0: mlp={has_mlp}, linear_attn={has_linear}, self_attn={has_full}")

    layer3 = lm.layers[3]
    has_full_3 = hasattr(layer3, 'self_attn')
    log(f"Layer 3: self_attn={has_full_3}")

    all_results = {}

    for input_key, text in INPUTS.items():
        log(f"\n─── Tracing: {input_key} ───")
        log(f"  Text: {text[:60]}")

        # Tokenize
        inputs = tokenizer(text, return_tensors="pt").to("mps")
        tokens = [tokenizer.decode(t) for t in inputs["input_ids"][0]]
        seq_len = len(tokens)
        log(f"  Tokens ({seq_len}): {tokens}")

        # Hook FFN gate_proj outputs
        ffn_gate_acts = {}
        ffn_outputs = {}

        def make_gate_hook(idx):
            def hook(module, inp, out):
                ffn_gate_acts[idx] = out.detach().float().cpu().numpy()[0]
            return hook

        def make_mlp_hook(idx):
            def hook(module, inp, out):
                ffn_outputs[idx] = out.detach().float().cpu().numpy()[0]
            return hook

        hooks = []
        for i in range(n_layers):
            layer = lm.layers[i]
            hooks.append(layer.mlp.gate_proj.register_forward_hook(make_gate_hook(i)))
            hooks.append(layer.mlp.register_forward_hook(make_mlp_hook(i)))

        # Forward pass
        with torch.no_grad():
            try:
                # For the conditional generation model, we call it with pixel_values=None
                outputs = model(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs.get("attention_mask"),
                    output_attentions=True,
                    return_dict=True,
                )
            except Exception as e:
                log(f"  Forward pass with output_attentions failed: {e}")
                log(f"  Trying without output_attentions...")
                outputs = model(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs.get("attention_mask"),
                    output_attentions=False,
                    return_dict=True,
                )

        # Remove hooks
        for h in hooks:
            h.remove()

        log(f"  Captured FFN outputs for {len(ffn_outputs)} layers")

        # ── Decode opcodes per position per layer ──
        per_layer_data = []

        for layer_idx in range(n_layers):
            if layer_idx not in ffn_outputs:
                continue

            ffn_out = ffn_outputs[layer_idx]  # (seq_len, d_model=5120)

            # Gate survival (magnitude-based: what fraction > median?)
            gate_survival = 0.0
            if layer_idx in ffn_gate_acts:
                from scipy.special import expit
                gate_raw = ffn_gate_acts[layer_idx]
                gate_activated = gate_raw * expit(gate_raw)
                # Fraction above 1% of max
                max_mag = np.abs(gate_activated).max()
                gate_survival = float((np.abs(gate_activated) > 0.01 * max_mag).mean())

            # Project FFN output onto combinator fingerprints
            op_energy = np.zeros((seq_len, N_OPS))
            for op_idx, op_name in enumerate(ALL_OPS):
                if op_name not in fingerprints:
                    continue
                fp = fingerprints[op_name][layer_idx]  # (5120,)
                fp_norm = fp / (np.linalg.norm(fp) + 1e-8)
                op_energy[:, op_idx] = ffn_out @ fp_norm

            # Dominant opcode per position
            dominant_idx = np.argmax(np.abs(op_energy), axis=1)
            dominant_ops = [ALL_OPS[idx] for idx in dominant_idx]

            # Op energy means (absolute)
            op_energy_abs = np.abs(op_energy)
            op_means = {op: float(op_energy_abs[:, i].mean()) for i, op in enumerate(ALL_OPS)}

            per_layer_data.append({
                "layer": layer_idx,
                "gate_survival": gate_survival,
                "dominant_ops": dominant_ops,
                "op_energy_means": op_means,
                "top_op_energy_mean": float(op_energy_abs.max(axis=1).mean()),
            })

        # ── Analyze ──
        result = {
            "input_key": input_key,
            "input_text": text,
            "tokens": tokens,
            "n_tokens": seq_len,
            "n_layers": n_layers,
            "per_layer": per_layer_data,
        }

        # Zone summaries
        zone_summaries = {}
        for zone_name, (start, end) in ZONES.items():
            zone_layers = [lr for lr in per_layer_data if start <= lr["layer"] <= end]
            if not zone_layers:
                continue

            # Average op energy
            zone_op_means = {op: np.mean([lr["op_energy_means"][op] for lr in zone_layers])
                           for op in ALL_OPS}
            # Top ops
            sorted_ops = sorted(zone_op_means.items(), key=lambda x: -x[1])[:5]

            # Diversity (entropy of dominant ops)
            all_dom_ops = []
            for lr in zone_layers:
                all_dom_ops.extend(lr["dominant_ops"])
            counts = Counter(all_dom_ops)
            total = sum(counts.values())
            probs = np.array([c / total for c in counts.values()])
            entropy = float(-np.sum(probs * np.log2(probs + 1e-10)))
            max_entropy = np.log2(min(total, N_OPS))
            norm_entropy = entropy / max_entropy if max_entropy > 0 else 0

            zone_summaries[zone_name] = {
                "top_ops": [(op, float(e)) for op, e in sorted_ops],
                "norm_entropy": float(norm_entropy),
                "mean_gate_survival": float(np.mean([lr["gate_survival"] for lr in zone_layers])),
                "mean_top_energy": float(np.mean([lr["top_op_energy_mean"] for lr in zone_layers])),
            }

        result["zone_summaries"] = zone_summaries

        # β_apply localization
        beta_apply_idx = ALL_OPS.index("beta_apply")
        beta_counts = np.zeros(seq_len)
        for lr in per_layer_data:
            for pos, op in enumerate(lr["dominant_ops"]):
                if op == "beta_apply" and pos < seq_len:
                    beta_counts[pos] += 1
        result["beta_apply_per_position"] = beta_counts.tolist()
        top_beta_pos = int(np.argmax(beta_counts))
        result["top_beta_apply_token"] = tokens[top_beta_pos] if top_beta_pos < seq_len else "?"

        all_results[input_key] = result

        # Print summary
        log(f"\n  Zone summaries:")
        for zone_name, zs in zone_summaries.items():
            top3 = " ".join(f"{op}={e:.1f}" for op, e in zs["top_ops"][:3])
            log(f"    {zone_name:10s}: entropy={zs['norm_entropy']:.3f}  energy={zs['mean_top_energy']:.1f}  [{top3}]")
        log(f"  β_apply peak: pos={top_beta_pos} tok={tokens[top_beta_pos]!r}")

        # Free memory
        del ffn_gate_acts, ffn_outputs
        gc.collect()

    # ── Final comparison ──
    log("\n═══ COMPARISON ═══")

    lambda_keys = [k for k in all_results if k.startswith("lambda")]
    neutral_keys = [k for k in all_results if k.startswith("neutral")]

    for zone_name in ZONES:
        l_energies = {op: [] for op in ALL_OPS}
        n_energies = {op: [] for op in ALL_OPS}

        for k in lambda_keys:
            zs = all_results[k]["zone_summaries"].get(zone_name, {})
            if "top_ops" in zs:
                for lr in all_results[k]["per_layer"]:
                    if ZONES[zone_name][0] <= lr["layer"] <= ZONES[zone_name][1]:
                        for op in ALL_OPS:
                            l_energies[op].append(lr["op_energy_means"][op])

        for k in neutral_keys:
            zs = all_results[k]["zone_summaries"].get(zone_name, {})
            if "top_ops" in zs:
                for lr in all_results[k]["per_layer"]:
                    if ZONES[zone_name][0] <= lr["layer"] <= ZONES[zone_name][1]:
                        for op in ALL_OPS:
                            n_energies[op].append(lr["op_energy_means"][op])

        log(f"\n  {zone_name}:")
        for op in ["beta_apply", "beta_compose", "D", "B", "Y", "K", "I"]:
            l_mean = np.mean(l_energies[op]) if l_energies[op] else 0
            n_mean = np.mean(n_energies[op]) if n_energies[op] else 0
            ratio = l_mean / (n_mean + 1e-8) if n_mean > 0 else float('inf')
            marker = "★" if ratio > 1.3 else ("▼" if ratio < 0.7 else " ")
            log(f"    {marker} {op:<14} λ={l_mean:>8.2f}  N={n_mean:>8.2f}  ratio={ratio:.2f}×")

    # Entropy comparison
    log("\n  STRUCTURAL DIVERSITY (norm entropy):")
    for zone_name in ZONES:
        l_ent = [all_results[k]["zone_summaries"].get(zone_name, {}).get("norm_entropy", 0)
                 for k in lambda_keys]
        n_ent = [all_results[k]["zone_summaries"].get(zone_name, {}).get("norm_entropy", 0)
                 for k in neutral_keys]
        l_mean = np.mean(l_ent) if l_ent else 0
        n_mean = np.mean(n_ent) if n_ent else 0
        ratio = l_mean / (n_mean + 1e-8) if n_mean > 0 else 0
        log(f"    {zone_name:10s}: λ={l_mean:.3f}  N={n_mean:.3f}  ratio={ratio:.2f}×")

    # Save results
    out_dir = RESULTS_BASE / "Qwen_Qwen3.6-27B"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Serialize (strip large arrays for JSON)
    def jsonify(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, dict):
            return {k: jsonify(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [jsonify(v) for v in obj]
        return obj

    with open(out_dir / "reduction_graph_results.json", "w") as f:
        json.dump(jsonify(all_results), f, indent=2)
    log(f"\nResults saved to {out_dir / 'reduction_graph_results.json'}")

    # Compact summary
    summary = {
        "model": "Qwen/Qwen3.6-27B",
        "architecture": "hybrid (17 full-attn + 48 linear-attn), 64 layers, d=5120",
        "inputs": {k: v["zone_summaries"] for k, v in all_results.items()},
    }
    with open(out_dir / "summary.json", "w") as f:
        json.dump(jsonify(summary), f, indent=2)
    log(f"Summary saved to {out_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
