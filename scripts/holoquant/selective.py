#!/usr/bin/env python3
"""HoloQuant v2 — Selective ternarization informed by beam trace.

v1 failed catastrophically (PPL 31→142K on Pythia-160M) because it
ternarized everything above a holographic score threshold.

v2 uses the beam/plate classification from the beam trace (session 098):
  PLATE (ternary-safe): K, V, attention output projections
  MARGINAL: FFN gate (h→4h)
  BEAM (precision): Q projections, FFN output (4h→h), norms, biases

For MoE models (Qwen3.6), the expert FFN weights are plate (93.6%
ternary-safe from holographic landscape). MoE gates are beam.

Ternarization: group-64 scales (sign × per-group-mean-abs).

Usage:
    # Pythia-160M (fast validation)
    uv run python scripts/holoquant/selective.py --model pythia

    # Pythia-1B (scale test)
    uv run python scripts/holoquant/selective.py --model pythia-1b

    # Qwen3.6-35B-A3B (the target)
    uv run python scripts/holoquant/selective.py --model qwen36

    # Test specific configurations
    uv run python scripts/holoquant/selective.py --model pythia --config plate-only
    uv run python scripts/holoquant/selective.py --model pythia --config plate+marginal
    uv run python scripts/holoquant/selective.py --model pythia --config aggressive

License: MIT
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════
# Models
# ══════════════════════════════════════════════════════════════════

MODELS = {
    "pythia": {
        "hf_name": "EleutherAI/pythia-160m-deduped",
        "arch": "gpt_neox",
        "dtype": torch.float32,
    },
    "pythia-1b": {
        "hf_name": "EleutherAI/pythia-1b-deduped",
        "arch": "gpt_neox",
        "dtype": torch.float32,
    },
    "qwen36": {
        "hf_name": "Qwen/Qwen3.6-35B-A3B",
        "arch": "qwen3_5_moe",
        "dtype": torch.float16,
    },
}


# ══════════════════════════════════════════════════════════════════
# Beam/Plate classification
# ══════════════════════════════════════════════════════════════════

# Classification configs: which components to ternarize
CONFIGS = {
    # Conservative: only components confirmed safe by beam trace
    "plate-only": {
        "description": "K, V, O projections only (beam trace: 2.6° avg error)",
        "ternary_patterns": {
            "gpt_neox": [".attention.dense."],
            "qwen3_5_moe": [
                ".k_proj.", ".v_proj.", ".o_proj.",  # full attention layers
                ".linear_attn.out_proj.",  # linear attention output
            ],
        },
        "ternary_kv_in_fused_qkv": True,
    },

    # Moderate: plate + expert FFN gate+up (the holographic plate)
    "plate+experts": {
        "description": "K,V,O + expert FFN gate_up (the holographic plate, 93% of params)",
        "ternary_patterns": {
            "gpt_neox": [".attention.dense.", ".mlp.dense_h_to_4h."],
            "qwen3_5_moe": [
                ".k_proj.", ".v_proj.", ".o_proj.",
                ".linear_attn.out_proj.",
                ".mlp.experts.gate_up_proj",  # packed [256, 1024, 2048] — the plate!
                ".shared_expert.gate_proj.", ".shared_expert.up_proj.",
            ],
        },
        "ternary_kv_in_fused_qkv": True,
    },

    # Aggressive: plate + all expert FFN (gate_up + down)
    "aggressive": {
        "description": "K,V,O + all expert FFN (holographic landscape: 93.6%)",
        "ternary_patterns": {
            "gpt_neox": [
                ".attention.dense.",
                ".mlp.dense_h_to_4h.", ".mlp.dense_4h_to_h.",
            ],
            "qwen3_5_moe": [
                ".k_proj.", ".v_proj.", ".o_proj.",
                ".linear_attn.out_proj.",
                ".mlp.experts.gate_up_proj",  # [256, 1024, 2048]
                ".mlp.experts.down_proj",      # [256, 2048, 512]
                ".shared_expert.gate_proj.", ".shared_expert.up_proj.",
                ".shared_expert.down_proj.",
            ],
        },
        "ternary_kv_in_fused_qkv": True,
    },

    # Full plate: everything the landscape says is ternary-safe + linear attn
    "full-plate": {
        "description": "All holographic: experts + attn + linear_attn out + embed",
        "ternary_patterns": {
            "gpt_neox": [
                ".attention.dense.",
                ".mlp.dense_h_to_4h.", ".mlp.dense_4h_to_h.",
            ],
            "qwen3_5_moe": [
                ".k_proj.", ".v_proj.", ".o_proj.",
                ".linear_attn.out_proj.",
                ".linear_attn.in_proj_z.",  # z gate projection
                ".mlp.experts.gate_up_proj",
                ".mlp.experts.down_proj",
                ".shared_expert.gate_proj.", ".shared_expert.up_proj.",
                ".shared_expert.down_proj.",
                "embed_tokens.",
            ],
        },
        "ternary_kv_in_fused_qkv": True,
    },

    # V1 baseline: ternarize everything (should fail catastrophically)
    "v1-naive": {
        "description": "Ternarize ALL large weight matrices (v1 approach)",
        "ternary_patterns": {
            "gpt_neox": [".weight"],
            "qwen3_5_moe": [".weight", ".gate_up_proj", ".down_proj"],
        },
        "ternary_kv_in_fused_qkv": False,
    },
}


# ══════════════════════════════════════════════════════════════════
# Ternarization
# ══════════════════════════════════════════════════════════════════

def ternarize_group64(W: torch.Tensor) -> torch.Tensor:
    """Ternarize with group-64 scales: sign × per-group mean(|W|).

    Returns reconstructed float tensor (same shape as W).
    """
    group_size = 64
    shape = W.shape
    W_flat = W.reshape(-1).float()
    n = W_flat.shape[0]

    # Pad to group_size multiple
    n_padded = ((n + group_size - 1) // group_size) * group_size
    if n_padded > n:
        W_flat = F.pad(W_flat, (0, n_padded - n))

    W_groups = W_flat.reshape(-1, group_size)
    scales = W_groups.abs().mean(dim=-1, keepdim=True)  # (n_groups, 1)
    signs = torch.sign(W_groups)
    reconstructed = (signs * scales).reshape(-1)[:n].reshape(shape)
    return reconstructed.to(W.dtype)


def ternarize_fused_qkv_kv_only(
    W: torch.Tensor, d_model: int,
) -> torch.Tensor:
    """Ternarize K and V portions of fused QKV, keep Q at precision.

    GPT-NeoX fused QKV: weight shape (3*d_model, d_model)
    First d_model rows = Q (KEEP PRECISION)
    Next d_model rows = K (TERNARIZE)
    Last d_model rows = V (TERNARIZE)
    """
    W_new = W.clone()
    # K portion
    W_new[d_model:2*d_model, :] = ternarize_group64(W[d_model:2*d_model, :])
    # V portion
    W_new[2*d_model:3*d_model, :] = ternarize_group64(W[2*d_model:3*d_model, :])
    return W_new


# ══════════════════════════════════════════════════════════════════
# Classification engine
# ══════════════════════════════════════════════════════════════════

def classify_and_ternarize(
    model,
    config_name: str,
    arch: str,
) -> dict:
    """Apply selective ternarization based on beam/plate classification.

    Returns stats about what was ternarized.
    """
    config = CONFIGS[config_name]
    patterns = config["ternary_patterns"].get(arch, [])
    ternary_kv = config.get("ternary_kv_in_fused_qkv", False)

    d_model = model.config.hidden_size

    stats = {
        "config": config_name,
        "description": config["description"],
        "ternarized": [],
        "kept_precision": [],
        "special_kv": [],
        "params_ternarized": 0,
        "params_precision": 0,
        "params_special": 0,
    }

    for name, param in list(model.named_parameters()):
        n = param.numel()

        # Skip visual encoder entirely (we only care about language model)
        if "visual." in name or "model.visual" in name:
            stats["kept_precision"].append({"name": name, "params": n, "reason": "visual"})
            stats["params_precision"] += n
            continue

        # Skip tiny params (biases, norms)
        if n < 1024:
            stats["kept_precision"].append({"name": name, "params": n, "reason": "small"})
            stats["params_precision"] += n
            continue

        # Skip norms explicitly
        if any(s in name for s in ["layernorm", "layer_norm", "rmsnorm",
                                    "norm.weight", "norm.bias",
                                    "input_layernorm", "post_attention_layernorm",
                                    "q_norm.", "k_norm."]):
            stats["kept_precision"].append({"name": name, "params": n, "reason": "norm"})
            stats["params_precision"] += n
            continue

        # Skip precision-critical beam components explicitly
        # MoE router gate (beam selector)
        if ".mlp.gate.weight" in name:
            stats["kept_precision"].append({"name": name, "params": n, "reason": "moe_gate"})
            stats["params_precision"] += n
            continue

        # Shared expert gate (beam selector for shared expert)
        if ".shared_expert_gate." in name:
            stats["kept_precision"].append({"name": name, "params": n, "reason": "shared_expert_gate"})
            stats["params_precision"] += n
            continue

        # Q projections (beam angle — NEVER ternarize)
        if ".q_proj." in name:
            stats["kept_precision"].append({"name": name, "params": n, "reason": "Q_beam"})
            stats["params_precision"] += n
            continue

        # Conv1d in linear attention (precision-critical readout)
        if "conv1d." in name:
            stats["kept_precision"].append({"name": name, "params": n, "reason": "conv1d"})
            stats["params_precision"] += n
            continue

        # Linear attention timing params (A_log, dt_bias)
        if "A_log" in name or "dt_bias" in name:
            stats["kept_precision"].append({"name": name, "params": n, "reason": "timing"})
            stats["params_precision"] += n
            continue

        # Special handling: fused QKV in GPT-NeoX
        if arch == "gpt_neox" and "query_key_value.weight" in name:
            if ternary_kv:
                param.data = ternarize_fused_qkv_kv_only(param.data, d_model)
                kv_params = 2 * d_model * d_model
                q_params = d_model * d_model
                stats["special_kv"].append({
                    "name": name, "total_params": n,
                    "kv_ternarized": kv_params, "q_kept": q_params,
                })
                stats["params_ternarized"] += kv_params
                stats["params_precision"] += q_params
            elif config_name == "v1-naive":
                param.data = ternarize_group64(param.data)
                stats["ternarized"].append({"name": name, "params": n})
                stats["params_ternarized"] += n
            else:
                stats["kept_precision"].append({"name": name, "params": n, "reason": "Q_in_QKV"})
                stats["params_precision"] += n
            continue

        # Special handling: fused in_proj_qkv in linear attention
        # Shape: [8192, 2048] = Q(4096) + K(2048) + V(2048) or similar
        if "linear_attn.in_proj_qkv." in name:
            if ternary_kv and config_name != "v1-naive":
                # Keep Q at precision, ternarize K,V portions
                # QKV layout: Q is first n_heads*head_dim rows
                # For Qwen3.6: 16 heads × 256 head_dim = 4096 for Q
                # Remaining = K+V
                q_dim = 4096  # 16 heads × 256
                total_rows = param.shape[0]
                kv_dim = total_rows - q_dim
                W_new = param.data.clone()
                W_new[q_dim:, :] = ternarize_group64(param.data[q_dim:, :])
                param.data = W_new
                kv_params = kv_dim * param.shape[1]
                q_params = q_dim * param.shape[1]
                stats["special_kv"].append({
                    "name": name, "total_params": n,
                    "kv_ternarized": kv_params, "q_kept": q_params,
                })
                stats["params_ternarized"] += kv_params
                stats["params_precision"] += q_params
            elif config_name == "v1-naive":
                param.data = ternarize_group64(param.data)
                stats["ternarized"].append({"name": name, "params": n})
                stats["params_ternarized"] += n
            else:
                stats["kept_precision"].append({"name": name, "params": n, "reason": "Q_in_QKV"})
                stats["params_precision"] += n
            continue

        # Check if this param matches any ternary pattern
        should_ternarize = False
        for pattern in patterns:
            if pattern in name:
                should_ternarize = True
                break

        if should_ternarize:
            # Handle 3D expert tensors (packed [n_experts, out, in])
            if param.dim() == 3:
                # Ternarize each expert slice independently
                for ei in range(param.shape[0]):
                    param.data[ei] = ternarize_group64(param.data[ei])
            else:
                param.data = ternarize_group64(param.data)
            stats["ternarized"].append({"name": name, "params": n})
            stats["params_ternarized"] += n
        else:
            reason = "not_matched"
            stats["kept_precision"].append({"name": name, "params": n, "reason": reason})
            stats["params_precision"] += n

    return stats


# ══════════════════════════════════════════════════════════════════
# Perplexity measurement
# ══════════════════════════════════════════════════════════════════

def get_test_texts() -> list[str]:
    return [
        "The transformer architecture revolutionized natural language processing by introducing self-attention mechanisms that allow models to weigh the importance of different parts of the input when producing each part of the output. Unlike recurrent neural networks, transformers can process all positions in parallel, leading to significant speedups during training.",
        "In quantum mechanics, the wave function describes the quantum state of a particle or system of particles. The Schrödinger equation governs how the wave function evolves over time. When a measurement is made, the wave function collapses to an eigenstate of the observable being measured.",
        "The Viable System Model, developed by Stafford Beer in 1972, describes the organizational structure needed for any viable system. It consists of five interacting subsystems: operations, coordination, control, intelligence, and identity. Each subsystem has a specific role in maintaining the viability of the organization.",
        "Lambda calculus is a formal system for expressing computation based on function abstraction and application using variable binding and substitution. It was introduced by Alonzo Church in the 1930s as part of his research into the foundations of mathematics. It has since become the basis for functional programming languages.",
        "The holographic principle suggests that the description of a volume of space can be thought of as encoded on a lower-dimensional boundary to the region. This principle was first proposed by Gerard 't Hooft and later given a precise string-theory interpretation by Leonard Susskind.",
        "Machine learning models learn representations of data through gradient descent optimization. The loss function measures how well the model's predictions match the true labels. Backpropagation efficiently computes the gradient of the loss with respect to each parameter, enabling the model to improve iteratively.",
        "Combinatory logic is a notation to eliminate the need for quantified variables in mathematical logic. It was introduced by Moses Schönfinkel and Haskell Curry. The key combinators are S, K, and I, which together can express any computable function.",
        "The attention mechanism in neural networks allows the model to focus on relevant parts of the input sequence when generating each output token. Multi-head attention splits the representation into multiple subspaces, allowing the model to attend to information from different representation subspaces at different positions.",
    ]


@torch.no_grad()
def measure_perplexity(model, tokenizer, texts: list[str],
                       max_length: int = 512, device: str = "cpu") -> float:
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True,
                          max_length=max_length).to(device)
        input_ids = inputs["input_ids"]
        if input_ids.shape[1] < 2:
            continue
        outputs = model(**inputs, labels=input_ids)
        loss = outputs.loss.item()
        n_tokens = input_ids.shape[1] - 1
        total_loss += loss * n_tokens
        total_tokens += n_tokens
    if total_tokens == 0:
        return float("inf")
    return math.exp(total_loss / total_tokens)


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="HoloQuant v2 — selective ternarization via beam/plate classification")
    parser.add_argument("--model", default="pythia", choices=list(MODELS.keys()))
    parser.add_argument("--config", default="all",
                        help="Config name or 'all' to test all configs")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--save-dir", type=str, default=None,
                        help="Save ternarized model to this directory (safetensors)")
    args = parser.parse_args()

    cfg = MODELS[args.model]
    configs_to_test = list(CONFIGS.keys()) if args.config == "all" else [args.config]

    texts = get_test_texts()

    print(f"HoloQuant v2 — Selective Ternarization")
    print(f"  Model: {cfg['hf_name']}")
    print(f"  Device: {args.device}")
    print(f"  Configs: {', '.join(configs_to_test)}")
    print()

    results = []

    for config_name in configs_to_test:
        print(f"\n{'='*70}")
        print(f"CONFIG: {config_name}")
        print(f"  {CONFIGS[config_name]['description']}")
        print(f"{'='*70}")

        # Fresh model load for each config (ternarization is destructive)
        print(f"  Loading model...", end="", flush=True)
        t0 = time.time()
        tokenizer = AutoTokenizer.from_pretrained(cfg["hf_name"], trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            cfg["hf_name"],
            torch_dtype=cfg["dtype"],
            device_map=args.device,
            trust_remote_code=True,
        )
        model.eval()
        total_params = sum(p.numel() for p in model.parameters())
        print(f" {time.time()-t0:.1f}s ({total_params:,} params)")

        # Baseline perplexity (only measure once)
        if not results:
            print(f"  Measuring baseline perplexity...", end="", flush=True)
            t0 = time.time()
            baseline_ppl = measure_perplexity(
                model, tokenizer, texts, args.max_length, args.device)
            print(f" {baseline_ppl:.2f} ({time.time()-t0:.1f}s)")
        else:
            baseline_ppl = results[0]["baseline_ppl"]
            print(f"  Baseline perplexity: {baseline_ppl:.2f} (cached)")

        # Apply selective ternarization
        print(f"  Applying {config_name}...", end="", flush=True)
        t0 = time.time()
        stats = classify_and_ternarize(model, config_name, cfg["arch"])
        print(f" {time.time()-t0:.1f}s")

        # Stats
        print(f"  Ternarized: {stats['params_ternarized']:,} params "
              f"({100*stats['params_ternarized']/total_params:.1f}%)")
        print(f"  Precision:  {stats['params_precision']:,} params "
              f"({100*stats['params_precision']/total_params:.1f}%)")
        if stats['special_kv']:
            total_kv = sum(s['kv_ternarized'] for s in stats['special_kv'])
            total_q = sum(s['q_kept'] for s in stats['special_kv'])
            print(f"  Fused QKV:  K,V ternarized ({total_kv:,}), Q kept ({total_q:,})")

        # Top ternarized components
        top_ternary = sorted(stats["ternarized"], key=lambda x: -x["params"])[:5]
        if top_ternary:
            print(f"  Top ternarized:")
            for t in top_ternary:
                print(f"    {t['name']:<55} {t['params']:>10,}")

        # Measure HoloQuant perplexity
        print(f"  Measuring HoloQuant perplexity...", end="", flush=True)
        t0 = time.time()
        holo_ppl = measure_perplexity(
            model, tokenizer, texts, args.max_length, args.device)
        print(f" {holo_ppl:.2f} ({time.time()-t0:.1f}s)")

        # Results
        ppl_delta = holo_ppl - baseline_ppl
        ppl_pct = 100 * (holo_ppl - baseline_ppl) / baseline_ppl

        # Memory estimate
        ternary_bytes = stats['params_ternarized'] * 1.85 / 8
        precision_bytes = stats['params_precision'] * (2 if cfg["dtype"] == torch.float16 else 4)
        total_bytes = ternary_bytes + precision_bytes
        original_bytes = total_params * (2 if cfg["dtype"] == torch.float16 else 4)
        avg_bits = (stats['params_ternarized'] * 1.85 +
                    stats['params_precision'] * (16 if cfg["dtype"] == torch.float16 else 32)
                    ) / total_params

        print(f"\n  RESULT:")
        print(f"    Baseline:   {baseline_ppl:.2f}")
        print(f"    HoloQuant:  {holo_ppl:.2f}")
        print(f"    Delta:      {ppl_delta:+.2f} ({ppl_pct:+.1f}%)")
        print(f"    Memory:     {total_bytes/1e6:.1f} MB (was {original_bytes/1e6:.1f} MB)")
        print(f"    Compression: {original_bytes/total_bytes:.1f}×")
        print(f"    Avg bits:   {avg_bits:.2f}")

        if abs(ppl_pct) < 1.0:
            print(f"    ✅ LOSSLESS (< 1% perplexity change)")
        elif abs(ppl_pct) < 5.0:
            print(f"    ✅ NEAR-LOSSLESS (< 5%)")
        elif abs(ppl_pct) < 20.0:
            print(f"    ⚠️  DEGRADED ({ppl_pct:+.1f}%)")
        elif abs(ppl_pct) < 100.0:
            print(f"    ❌ SIGNIFICANT LOSS ({ppl_pct:+.1f}%)")
        else:
            print(f"    ❌ CATASTROPHIC ({ppl_pct:+.1f}%)")

        # Save model if requested
        if args.save_dir:
            save_path = Path(args.save_dir) / config_name
            save_path.mkdir(parents=True, exist_ok=True)
            print(f"\n  Saving ternarized model to {save_path}...", end="", flush=True)
            t0 = time.time()
            model.save_pretrained(save_path, safe_serialization=True)
            tokenizer.save_pretrained(save_path)
            print(f" {time.time()-t0:.1f}s")
            print(f"    Saved to: {save_path}")

        results.append({
            "config": config_name,
            "baseline_ppl": baseline_ppl,
            "holo_ppl": holo_ppl,
            "ppl_delta_pct": ppl_pct,
            "params_ternarized": stats["params_ternarized"],
            "params_precision": stats["params_precision"],
            "pct_ternarized": 100 * stats["params_ternarized"] / total_params,
            "compression": original_bytes / total_bytes,
            "avg_bits": avg_bits,
            "memory_mb": total_bytes / 1e6,
        })

        # Cleanup
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # Final comparison table
    print(f"\n\n{'='*70}")
    print(f"COMPARISON TABLE — {cfg['hf_name']}")
    print(f"{'='*70}")
    print(f"{'Config':<20} {'Ternary%':>8} {'PPL':>8} {'Delta%':>8} "
          f"{'Bits':>6} {'Compr':>6} {'Verdict':>12}")
    print(f"{'─'*20} {'─'*8} {'─'*8} {'─'*8} {'─'*6} {'─'*6} {'─'*12}")

    for r in results:
        if abs(r["ppl_delta_pct"]) < 5:
            verdict = "✅ OK"
        elif abs(r["ppl_delta_pct"]) < 20:
            verdict = "⚠️  WARN"
        elif abs(r["ppl_delta_pct"]) < 100:
            verdict = "❌ BAD"
        else:
            verdict = "❌ DEAD"
        print(f"{r['config']:<20} {r['pct_ternarized']:>7.1f}% {r['holo_ppl']:>8.1f} "
              f"{r['ppl_delta_pct']:>+7.1f}% {r['avg_bits']:>6.2f} "
              f"{r['compression']:>5.1f}× {verdict:>12}")


if __name__ == "__main__":
    main()
