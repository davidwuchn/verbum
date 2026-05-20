"""FFN Deduplication Test — how many unique concepts does the FFN store?

Pool W_up rows from ALL layers, SVD to find effective rank, cluster
to find duplicates. If effective rank << total neuron count, massive
deduplication is possible.

Usage:
    uv run python scripts/v12/ffn_dedup_test.py
    uv run python scripts/v12/ffn_dedup_test.py --models mistral-7b

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import sys
import time
from pathlib import Path
import json

import numpy as np

MODELS = {
    "mistral-7b": ("mistralai/Mistral-7B-v0.3", 32, 4096),
    "pythia-2.8b": ("EleutherAI/pythia-2.8b-deduped", 32, 2560),
}

DEFAULT_MODELS = ["mistral-7b", "pythia-2.8b"]


def run_dedup(model_key, device="mps"):
    """Extract W_up from all layers, pool, analyze duplication."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model = MODELS[model_key]
    print(f"\n  ─── {model_key} ({model_name}) ───", file=sys.stderr, flush=True)
    print(f"  {n_layers} layers, d_model={d_model}", file=sys.stderr, flush=True)

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map="cpu", trust_remote_code=True,
    )
    model.eval()

    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
    else:
        raise ValueError("Unknown arch")

    # Extract W_up from every layer
    all_w_up_rows = []
    layer_labels = []
    d_ffn = None

    for li in range(n_layers):
        mlp = layers[li].mlp if hasattr(layers[li], 'mlp') else getattr(layers[li], 'feed_forward', None)
        if mlp is None:
            continue
        if hasattr(mlp, 'up_proj'):
            w = mlp.up_proj.weight.detach().cpu().float().numpy()
        elif hasattr(mlp, 'dense_h_to_4h'):
            w = mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()
        else:
            continue

        d_ffn = w.shape[0]
        all_w_up_rows.append(w)
        layer_labels.extend([li] * d_ffn)

        if (li + 1) % 8 == 0:
            print(f"    Extracted {li+1}/{n_layers} layers...", file=sys.stderr, flush=True)

    del model
    gc.collect()

    # Pool all rows
    pooled = np.vstack(all_w_up_rows)  # (total_neurons, d_model)
    total_neurons = pooled.shape[0]
    layer_labels = np.array(layer_labels)

    print(f"\n  Pooled: {total_neurons} neurons × {d_model}d "
          f"({d_ffn} per layer × {n_layers} layers)",
          file=sys.stderr, flush=True)

    # ── Test 1: SVD effective rank ────────────────────────────
    print(f"\n  SVD of pooled W_up ({total_neurons} × {d_model})...",
          file=sys.stderr, flush=True)

    # Center
    pooled_centered = pooled - pooled.mean(axis=0, keepdims=True)

    # SVD (right singular vectors give the key subspace)
    # For large matrices, use randomized SVD or just compute on the
    # covariance matrix: pooled.T @ pooled is (d_model × d_model)
    cov = pooled_centered.T @ pooled_centered / total_neurons  # (d_model, d_model)
    eigvals, eigvecs = np.linalg.eigh(cov)
    # Sort descending
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    total_var = eigvals.sum()
    explained = eigvals / max(total_var, 1e-8)
    cumvar = np.cumsum(explained)

    dims_50 = int(np.searchsorted(cumvar, 0.5)) + 1
    dims_80 = int(np.searchsorted(cumvar, 0.8)) + 1
    dims_90 = int(np.searchsorted(cumvar, 0.9)) + 1
    dims_95 = int(np.searchsorted(cumvar, 0.95)) + 1
    dims_99 = int(np.searchsorted(cumvar, 0.99)) + 1

    print(f"  Effective rank of pooled FFN keys:", file=sys.stderr, flush=True)
    print(f"    50% variance: {dims_50}d", file=sys.stderr, flush=True)
    print(f"    80% variance: {dims_80}d", file=sys.stderr, flush=True)
    print(f"    90% variance: {dims_90}d", file=sys.stderr, flush=True)
    print(f"    95% variance: {dims_95}d", file=sys.stderr, flush=True)
    print(f"    99% variance: {dims_99}d", file=sys.stderr, flush=True)
    print(f"    Top-10 explained: {', '.join(f'{v:.1%}' for v in explained[:10])}",
          file=sys.stderr, flush=True)

    # ── Test 2: Cross-layer cosine similarity ─────────────────
    # Sample neurons from different layers, measure cosine similarity
    print(f"\n  Cross-layer neuron similarity...", file=sys.stderr, flush=True)

    # Normalize all rows
    norms = np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-8)
    pooled_norm = pooled / norms

    # Sample: take first 1000 neurons from each of a few layers
    sample_layers = [0, n_layers//4, n_layers//2, 3*n_layers//4, n_layers-1]
    n_sample = min(1000, d_ffn)

    cross_layer_sims = {}
    for i, li in enumerate(sample_layers):
        for j, lj in enumerate(sample_layers):
            if j <= i:
                continue
            start_i = li * d_ffn
            start_j = lj * d_ffn
            rows_i = pooled_norm[start_i:start_i+n_sample]
            rows_j = pooled_norm[start_j:start_j+n_sample]

            # For each neuron in layer i, find max cosine to any neuron in layer j
            sim_matrix = rows_i @ rows_j.T  # (n_sample, n_sample)
            max_sims = sim_matrix.max(axis=1)
            mean_max = float(max_sims.mean())
            frac_high = float((max_sims > 0.9).mean())
            frac_mid = float((max_sims > 0.7).mean())

            cross_layer_sims[f"L{li}_L{lj}"] = {
                "mean_max_sim": mean_max,
                "frac_above_0.9": frac_high,
                "frac_above_0.7": frac_mid,
            }
            print(f"    L{li:2d} ↔ L{lj:2d}: mean_max_sim={mean_max:+.4f}, "
                  f">{'.9'}={frac_high:.1%}, >{'.7'}={frac_mid:.1%}",
                  file=sys.stderr, flush=True)

    # ── Test 3: Cluster to count unique concepts ──────────────
    print(f"\n  Clustering to find unique concepts...", file=sys.stderr, flush=True)

    # Use agglomerative-like approach on a sample
    # Take a random sample of neurons, cluster by cosine > threshold
    rng = np.random.RandomState(42)
    sample_size = min(5000, total_neurons)
    sample_idx = rng.choice(total_neurons, sample_size, replace=False)
    sample_norm = pooled_norm[sample_idx]
    sample_layers_arr = layer_labels[sample_idx]

    # Cosine similarity matrix of sample
    sim = sample_norm @ sample_norm.T  # (sample_size, sample_size)

    # Count unique clusters at different thresholds
    thresholds = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
    print(f"  {'threshold':>10s}  {'n_clusters':>10s}  {'dedup_ratio':>11s}  "
          f"{'unique_est':>10s}  {'cross_layer':>11s}",
          file=sys.stderr, flush=True)
    print(f"  {'-'*58}", file=sys.stderr, flush=True)

    cluster_results = {}
    for thresh in thresholds:
        # Simple greedy clustering
        assigned = np.zeros(sample_size, dtype=bool)
        n_clusters = 0
        cross_layer_clusters = 0

        for i in range(sample_size):
            if assigned[i]:
                continue
            # Find all unassigned neurons similar to this one
            similar = (~assigned) & (sim[i] > thresh)
            similar_idx = np.where(similar)[0]

            # Check if cluster spans multiple layers
            cluster_layers = set(sample_layers_arr[similar_idx].tolist())
            if len(cluster_layers) > 1:
                cross_layer_clusters += 1

            assigned[similar_idx] = True
            n_clusters += 1

        dedup_ratio = 1.0 - (n_clusters / sample_size)
        unique_est = int(n_clusters * (total_neurons / sample_size))
        cross_layer_frac = cross_layer_clusters / max(n_clusters, 1)

        print(f"  {thresh:>10.2f}  {n_clusters:>10,}  {dedup_ratio:>10.1%}  "
              f"{unique_est:>10,}  {cross_layer_frac:>10.1%}",
              file=sys.stderr, flush=True)

        cluster_results[str(thresh)] = {
            "n_clusters": n_clusters,
            "dedup_ratio": dedup_ratio,
            "unique_estimate": unique_est,
            "cross_layer_fraction": cross_layer_frac,
        }

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{'='*70}", file=sys.stderr, flush=True)
    print(f"  SUMMARY — {model_key}", file=sys.stderr, flush=True)
    print(f"{'='*70}", file=sys.stderr, flush=True)
    print(f"  Total neurons: {total_neurons:,}", file=sys.stderr, flush=True)
    print(f"  Effective key dimensions: {dims_90}d (90% var), "
          f"{dims_99}d (99% var)", file=sys.stderr, flush=True)
    print(f"  At cosine threshold 0.7:", file=sys.stderr, flush=True)
    c7 = cluster_results["0.7"]
    print(f"    Unique concepts: ~{c7['unique_estimate']:,} "
          f"(dedup {c7['dedup_ratio']:.0%})", file=sys.stderr, flush=True)
    print(f"    Cross-layer clusters: {c7['cross_layer_fraction']:.0%} "
          f"(duplicates span layers)", file=sys.stderr, flush=True)
    print(f"  At cosine threshold 0.9:", file=sys.stderr, flush=True)
    c9 = cluster_results["0.9"]
    print(f"    Unique concepts: ~{c9['unique_estimate']:,} "
          f"(dedup {c9['dedup_ratio']:.0%})", file=sys.stderr, flush=True)

    # V13 capacity comparison
    v13_ternary = 130_000_000
    vectors_at_512 = v13_ternary // 512
    print(f"\n  V13 at 130M FFN plates: {vectors_at_512:,} ternary vectors",
          file=sys.stderr, flush=True)
    print(f"  Unique concepts at 0.7 threshold: ~{c7['unique_estimate']:,}",
          file=sys.stderr, flush=True)
    if vectors_at_512 > c7['unique_estimate']:
        ratio = vectors_at_512 / c7['unique_estimate']
        print(f"  → V13 has {ratio:.1f}× MORE capacity than unique concepts!",
              file=sys.stderr, flush=True)
    else:
        ratio = c7['unique_estimate'] / vectors_at_512
        print(f"  → Need {ratio:.1f}× more plates to store all unique concepts",
              file=sys.stderr, flush=True)

    return {
        "total_neurons": total_neurons,
        "d_ffn": d_ffn,
        "n_layers": n_layers,
        "d_model": d_model,
        "effective_rank": {
            "50pct": dims_50, "80pct": dims_80, "90pct": dims_90,
            "95pct": dims_95, "99pct": dims_99,
        },
        "top10_explained": explained[:10].tolist(),
        "cross_layer_similarity": cross_layer_sims,
        "clustering": cluster_results,
    }


def main():
    parser = argparse.ArgumentParser(description="FFN Deduplication Test")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()))
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--output-dir", type=str, default="results/ffn-dedup")

    args = parser.parse_args()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  FFN Deduplication — How Many Unique Concepts?", file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t0 = time.time()
    all_results = {}
    for mk in args.models:
        all_results[mk] = run_dedup(mk, args.device)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "analysis.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n  💾 {output_dir}/analysis.json", file=sys.stderr, flush=True)
    print(f"  Total: {time.time()-t0:.0f}s", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
