#!/usr/bin/env python3
"""Cross-model holographic analysis — universality of the holographic landscape.

Three experiments:
  1. Cross-model holographic fraction: is the ternary/float split universal?
  2. Scale-dependent emergence: does holographic fraction grow with scale?
  3. Cross-model sign agreement: what sign patterns are universal?

Uses Pythia family (same architecture, same data, different scale)
to control for architecture and training data, isolating scale effects.

Usage:
    # Full analysis across Pythia family
    uv run python scripts/explore/probe_holographic_cross_model.py

    # Quick: just 70M and 160M
    uv run python scripts/explore/probe_holographic_cross_model.py --models pythia-70m,pythia-160m

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

# Gaussian baselines
GAUSSIAN_TC = float(np.sqrt(2 / np.pi))
GAUSSIAN_CV = float(np.sqrt(np.pi / 2 - 1))

MODELS = {
    # Pythia family — GPT-NeoX architecture, The Pile data
    "pythia-70m": {
        "hf_name": "EleutherAI/pythia-70m-deduped",
        "family": "pythia", "params": "70M",
    },
    "pythia-160m": {
        "hf_name": "EleutherAI/pythia-160m-deduped",
        "family": "pythia", "params": "160M",
    },
    "pythia-410m": {
        "hf_name": "EleutherAI/pythia-410m-deduped",
        "family": "pythia", "params": "410M",
    },
    "pythia-1b": {
        "hf_name": "EleutherAI/pythia-1b-deduped",
        "family": "pythia", "params": "1B",
    },
    # Phi family — Microsoft, different architecture + data
    "phi4-mini": {
        "hf_name": "microsoft/Phi-4-mini-instruct",
        "family": "phi", "params": "3.8B",
    },
    # Qwen3 family — different architecture, different data, different scale
    "qwen3-0.6b": {
        "hf_name": "Qwen/Qwen3-0.6B",
        "family": "qwen3", "params": "0.6B",
    },
    "qwen3-4b": {
        "hf_name": "Qwen/Qwen3-4B",
        "family": "qwen3", "params": "4B",
    },
    # SmolLM3 — HuggingFace, yet another architecture
    "smollm3-3b": {
        "hf_name": "HuggingFaceTB/SmolLM3-3B",
        "family": "smollm", "params": "3B",
    },
}

OUTPUT_DIR = Path("results/holographic-cross-model")


def compute_corrected_score(W_np: np.ndarray) -> float:
    """Corrected holographic score for a weight matrix."""
    W_flat = W_np.reshape(-1).astype(np.float32)
    abs_W = np.abs(W_flat)
    dot = np.sum(abs_W)
    norm_W = np.sqrt(np.sum(W_flat * W_flat) + 1e-12)
    n_nonzero = np.sum(W_flat != 0)
    norm_sign = np.sqrt(float(n_nonzero) + 1e-12)
    tc = float(dot / (norm_W * norm_sign + 1e-12))
    mag_mean = float(np.mean(abs_W))
    mag_std = float(np.std(abs_W))
    cv = mag_std / max(mag_mean, 1e-12)
    return 0.5 * (tc / GAUSSIAN_TC) + 0.5 * (GAUSSIAN_CV / max(cv, 0.01))


def classify_component(name: str) -> str:
    """Classify a parameter name into component type.

    Handles naming conventions across architectures:
      Pythia (GPT-NeoX): query_key_value, dense, dense_h_to_4h
      Qwen3: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
      Phi: qkv_proj, o_proj, gate_up_proj, down_proj
      SmolLM3: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
    """
    name_lower = name.lower()

    # Attention QKV (universally magnitude-dependent)
    if any(s in name_lower for s in [
        "query_key_value", "qkv_proj",
        "q_proj", "k_proj", "v_proj",
        ".wq.", ".wk.", ".wv.",
    ]):
        return "attention_qkv"

    # Attention output projection
    if any(s in name_lower for s in [
        "o_proj", ".wo.",
        "attention.dense",  # Pythia
    ]):
        if "dense_h_to" not in name_lower and "dense_4h" not in name_lower:
            return "attention_out"

    # MLP / FFN (the holographic plate)
    if any(s in name_lower for s in [
        "mlp", "dense_h_to_4h", "dense_4h_to_h",
        "gate_proj", "up_proj", "down_proj",
        "gate_up_proj",  # Phi fused gate+up
        "fc1", "fc2",    # some architectures
    ]):
        if "expert" in name_lower:
            return "expert_ffn"
        if "moe" in name_lower and "gate" in name_lower and "proj" not in name_lower:
            return "moe_gate"
        return "mlp"

    # Embeddings
    if "embed" in name_lower:
        return "embedding"

    # Norms (skip in analysis)
    if any(s in name_lower for s in ["norm", "layernorm", "rmsnorm"]):
        return "norm"

    # MoE routing gate
    if "gate" in name_lower and "proj" not in name_lower:
        return "moe_gate"

    return "other"


def analyze_model(model_key: str) -> dict:
    """Load and analyze a single model's holographic landscape."""
    from transformers import AutoModelForCausalLM

    cfg = MODELS[model_key]
    print(f"\n{'='*60}")
    print(f"Loading {cfg['hf_name']} ({cfg['params']})...")

    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        cfg["hf_name"], torch_dtype=torch.float32,
        device_map="cpu", trust_remote_code=True)
    model.eval()
    print(f"  Loaded in {time.time()-t0:.1f}s")

    results = {
        "model": model_key,
        "hf_name": cfg["hf_name"],
        "params": cfg["params"],
        "matrices": [],
        "by_component": {},
        "sign_patterns": {},  # for cross-model agreement
    }

    total_params = 0
    component_data = defaultdict(lambda: {
        "scores": [], "tc": [], "cv": [], "params": 0, "n": 0
    })

    for name, param in model.named_parameters():
        W = param.detach().cpu().float().numpy()
        n = W.size
        total_params += n

        if n < 1024:
            continue
        if "norm" in name.lower() or "layernorm" in name.lower():
            continue

        score = compute_corrected_score(W)
        W_flat = W.reshape(-1).astype(np.float32)
        abs_W = np.abs(W_flat)
        tc = float(np.sum(abs_W) / (np.sqrt(np.sum(W_flat**2) + 1e-12)
                    * np.sqrt(np.sum(W_flat != 0) + 1e-12)))
        cv = float(np.std(abs_W) / max(np.mean(abs_W), 1e-12))

        ctype = classify_component(name)
        component_data[ctype]["scores"].append(score)
        component_data[ctype]["tc"].append(tc)
        component_data[ctype]["cv"].append(cv)
        component_data[ctype]["params"] += n
        component_data[ctype]["n"] += 1

        results["matrices"].append({
            "name": name, "shape": list(W.shape), "n_params": n,
            "score": score, "tc": tc, "cv": cv, "component": ctype,
        })

        # Store sign pattern for cross-model comparison
        # Only for first few layers (memory-efficient)
        layer_idx = None
        for part in name.split("."):
            try:
                layer_idx = int(part)
                break
            except ValueError:
                continue

        if layer_idx is not None and layer_idx < 4:
            sign_key = name.replace(f".{layer_idx}.", ".{L}.")
            signs = np.sign(W_flat).astype(np.int8)
            results["sign_patterns"][f"{sign_key}_L{layer_idx}"] = {
                "signs_hash": hash(signs.tobytes()),
                "n_pos": int(np.sum(signs > 0)),
                "n_neg": int(np.sum(signs < 0)),
                "n_zero": int(np.sum(signs == 0)),
                "n_total": len(signs),
            }

    results["total_params"] = total_params

    # Summarize by component
    for ctype, info in component_data.items():
        arr_scores = np.array(info["scores"])
        arr_tc = np.array(info["tc"])
        arr_cv = np.array(info["cv"])
        results["by_component"][ctype] = {
            "n_matrices": info["n"],
            "total_params": info["params"],
            "pct_of_model": 100 * info["params"] / total_params,
            "mean_score": float(arr_scores.mean()),
            "std_score": float(arr_scores.std()),
            "mean_tc": float(arr_tc.mean()),
            "mean_cv": float(arr_cv.mean()),
            "ternary_safe": float(arr_scores.mean()) > 0.95,
        }

    # Overall stats
    all_scores = [m["score"] for m in results["matrices"]]
    all_params = [m["n_params"] for m in results["matrices"]]
    total_analyzed = sum(all_params)
    ternary_safe = sum(p for s, p in zip(all_scores, all_params) if s > 0.95)
    results["summary"] = {
        "ternary_safe_pct": 100 * ternary_safe / max(total_analyzed, 1),
        "mean_score": float(np.mean(all_scores)),
        "n_analyzed": len(all_scores),
    }

    del model
    return results


def print_cross_model_comparison(all_results: list[dict]) -> None:
    """Print cross-model comparison of holographic landscapes."""

    print(f"\n{'='*80}")
    print("EXPERIMENT 1: Cross-Model Holographic Fraction")
    print(f"{'='*80}")

    # Header
    model_names = [r["params"] for r in all_results]
    header = f"{'Component':<20}" + "".join(f"{n:>12}" for n in model_names)
    print(f"\n{header}")
    print("-" * (20 + 12 * len(model_names)))

    # Gather all component types
    all_ctypes = set()
    for r in all_results:
        all_ctypes.update(r["by_component"].keys())

    for ctype in sorted(all_ctypes):
        row = f"{ctype:<20}"
        for r in all_results:
            if ctype in r["by_component"]:
                score = r["by_component"][ctype]["mean_score"]
                row += f"{score:>12.4f}"
            else:
                row += f"{'—':>12}"
        print(row)

    # Ternary-safe summary
    print(f"\n{'Ternary-safe %':<20}", end="")
    for r in all_results:
        print(f"{r['summary']['ternary_safe_pct']:>11.1f}%", end="")
    print()

    print(f"\n{'='*80}")
    print("EXPERIMENT 2: Scale-Dependent Holographic Emergence")
    print(f"{'='*80}")

    # Track which components become MORE holographic with scale
    print(f"\n{'Component':<20} {'Trend':>10} {'Smallest':>10} {'Largest':>10} {'Delta':>10}")
    print("-" * 65)

    for ctype in sorted(all_ctypes):
        scores = []
        for r in all_results:
            if ctype in r["by_component"]:
                scores.append(r["by_component"][ctype]["mean_score"])
            else:
                scores.append(None)

        valid = [(i, s) for i, s in enumerate(scores) if s is not None]
        if len(valid) < 2:
            continue

        first = valid[0][1]
        last = valid[-1][1]
        delta = last - first
        trend = "↑ MORE" if delta > 0.01 else "↓ LESS" if delta < -0.01 else "= SAME"
        print(f"{ctype:<20} {trend:>10} {first:>10.4f} {last:>10.4f} {delta:>+10.4f}")

    print(f"\n{'='*80}")
    print("EXPERIMENT 3: Component-Level Universality")
    print(f"{'='*80}")

    # For each component type, compute cross-model correlation of scores
    # (Are the same layers holographic across models?)
    print("\nCross-model score variance by component:")
    print(f"{'Component':<20} {'Mean':>8} {'StdAcross':>10} {'CV':>8} {'Universal?':>12}")
    print("-" * 65)

    for ctype in sorted(all_ctypes):
        means = []
        for r in all_results:
            if ctype in r["by_component"]:
                means.append(r["by_component"][ctype]["mean_score"])
        if len(means) < 2:
            continue

        arr = np.array(means)
        mean_val = arr.mean()
        std_val = arr.std()
        cv_val = std_val / max(mean_val, 1e-8)
        universal = "YES" if cv_val < 0.05 else "LIKELY" if cv_val < 0.10 else "NO"
        print(f"{ctype:<20} {mean_val:>8.4f} {std_val:>10.4f} {cv_val:>8.4f} {universal:>12}")


def save_results(all_results: list[dict], output_dir: Path) -> None:
    """Save all results to JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for r in all_results:
        # Remove sign_patterns from saved JSON (too large, keep summary)
        r_save = {k: v for k, v in r.items() if k != "sign_patterns"}
        outpath = output_dir / f"landscape_{r['model']}.json"
        with open(outpath, "w") as f:
            json.dump(r_save, f, indent=2)
        print(f"  Saved {outpath}")

    # Cross-model summary
    summary = {
        "models": [r["model"] for r in all_results],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "by_model": {
            r["model"]: r["summary"] for r in all_results
        },
        "by_component_by_model": {
            r["model"]: r["by_component"] for r in all_results
        },
    }
    with open(output_dir / "cross_model_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  Saved cross_model_summary.json")


def main():
    parser = argparse.ArgumentParser(
        description="Cross-model holographic landscape analysis")
    parser.add_argument(
        "--models", default=",".join(MODELS.keys()),
        help="Comma-separated model keys to analyze")
    parser.add_argument(
        "--output", default=str(OUTPUT_DIR),
        help="Output directory")
    args = parser.parse_args()

    model_keys = [m.strip() for m in args.models.split(",")]
    output_dir = Path(args.output)

    print("Cross-Model Holographic Analysis")
    print(f"  Models: {', '.join(model_keys)}")
    print(f"  Output: {output_dir}")

    all_results = []
    for key in model_keys:
        if key not in MODELS:
            print(f"  Unknown model: {key}, skipping")
            continue
        results = analyze_model(key)
        all_results.append(results)

    if len(all_results) < 2:
        print("Need at least 2 models for cross-model comparison")
        return

    print_cross_model_comparison(all_results)
    save_results(all_results, output_dir)
    print(f"\nDone. Results in {output_dir}/")


if __name__ == "__main__":
    main()
