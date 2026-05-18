"""Build the Universal Lattice Map — cross-model consensus RDM.

Loads N diverse models, runs the lambda kernel probes through each,
computes per-model RDMs, then builds the cross-model CONSENSUS:
positions where ALL models agree on the relational geometry.

The consensus RDM is the universal computational lattice — the crystal
structure that every independently trained model discovered. Positions
where models disagree are model-specific artifacts, not universal.

The output is used as a holographic loss target in holographic_train.py:
the reference beam that burns the universal lattice into the small
model's ternary plates.

Three levels of output:
  1. consensus_rdm:   average RDM across all models (the geometry)
  2. agreement_mask:   per-pair confidence [0,1] (how universal is this distance?)
  3. dimensions:       SVD of consensus RDM (the independent axes of variation)

Usage:
    # Full extraction (requires GPU, loads each model sequentially)
    uv run python scripts/v12/build_lattice_map.py

    # Specific models only
    uv run python scripts/v12/build_lattice_map.py --models qwen3-14b mistral-7b

    # Quick test with small models
    uv run python scripts/v12/build_lattice_map.py --models pythia-1.4b pythia-6.9b

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

# ══════════════════════════════════════════════════════════════════════
# Model registry — diverse architectures, diverse training data
# ══════════════════════════════════════════════════════════════════════

MODELS = {
    # Model key → (HuggingFace ID, n_layers, d_model)
    "qwen3-14b":    ("Qwen/Qwen3-14B",              40, 5120),
    "llama-3-8b":   ("meta-llama/Llama-3.1-8B",      32, 4096),
    "mistral-7b":   ("mistralai/Mistral-7B-v0.3",    32, 4096),
    "olmo-2-13b":   ("allenai/OLMo-2-1124-13B",      40, 5120),
    "olmo-2-7b":    ("allenai/OLMo-2-1124-7B",       32, 4096),
    "pythia-6.9b":  ("EleutherAI/pythia-6.9b",        32, 4096),
    "pythia-2.8b":  ("EleutherAI/pythia-2.8b-deduped", 32, 2560),
    "pythia-1.4b":  ("EleutherAI/pythia-1.4b",        24, 2048),
    "smollm3-3b":   ("HuggingFaceTB/SmolLM3-3B",     36, 2560),
    "phi-4-mini":   ("microsoft/Phi-4-mini-instruct", 32, 3072),
}

# Default model set — architecturally diverse, independently trained
# Using what's cached locally for speed
DEFAULT_MODELS = ["qwen3-14b", "mistral-7b", "olmo-2-13b", "pythia-2.8b"]


# ══════════════════════════════════════════════════════════════════════
# Probe loading — reuse lambda kernel probes
# ══════════════════════════════════════════════════════════════════════

def load_probes(corpus_path: str | None = None) -> list[dict]:
    """Load probes — either from diverse corpus JSON or lambda kernel probes.

    If corpus_path is provided, loads the diverse corpus (multi-domain).
    Otherwise falls back to the 380 lambda kernel probes.

    Returns list of {"prompt": str, "axis": str} dicts.
    (For diverse corpus, axis = "domain/subdomain".)
    """
    if corpus_path and Path(corpus_path).exists():
        import json as _json
        with open(corpus_path) as f:
            corpus = _json.load(f)
        # Normalize: ensure "axis" field exists
        flat = []
        for item in corpus:
            flat.append({
                "prompt": item["prompt"],
                "axis": item.get("axis", f"{item.get('domain', 'unknown')}/{item.get('subdomain', 'unknown')}"),
            })
        # Count domains
        domains = {}
        for item in corpus:
            d = item.get("domain", "unknown")
            domains[d] = domains.get(d, 0) + 1
        print(f"  Loaded diverse corpus: {len(flat)} probes across {len(domains)} domains",
              file=sys.stderr, flush=True)
        for d, n in sorted(domains.items(), key=lambda x: -x[1]):
            print(f"    {d:15s}: {n:4d}", file=sys.stderr, flush=True)
        return flat

    # Fallback: lambda kernel probes
    probes_dir = Path(__file__).parent.parent.parent / "probes"
    sys.path.insert(0, str(probes_dir))
    from lambda_kernel_probes import LAMBDA_PROBES

    flat = []
    for axis, prompts in LAMBDA_PROBES.items():
        for prompt in prompts:
            flat.append({"prompt": prompt, "axis": axis})

    print(f"  Loaded {len(flat)} probes across {len(LAMBDA_PROBES)} axes",
          file=sys.stderr, flush=True)
    return flat


# ══════════════════════════════════════════════════════════════════════
# Depth mapping — relative depth for cross-architecture alignment
# ══════════════════════════════════════════════════════════════════════

def get_target_layers(n_layers: int, depth_fractions: list[float]) -> list[int]:
    """Map relative depth fractions to absolute layer indices.

    depth_fractions: [0.0, 0.25, 0.5, 0.75, 1.0]
    For a 40-layer model: [0, 10, 20, 30, 39]
    For a 32-layer model: [0, 8, 16, 24, 31]

    Using relative depth makes cross-model RDMs comparable:
    "25% depth" means the same thing regardless of layer count.
    """
    layers = []
    for frac in depth_fractions:
        layer = int(round(frac * (n_layers - 1)))
        layer = min(layer, n_layers - 1)
        layers.append(layer)
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for l in layers:
        if l not in seen:
            seen.add(l)
            unique.append(l)
    return unique


# ══════════════════════════════════════════════════════════════════════
# RDM extraction — per model
# ══════════════════════════════════════════════════════════════════════

def extract_rdm(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[float, np.ndarray]:
    """Extract cosine-similarity RDM from one model at each depth fraction.

    Returns: {depth_fraction: rdm_matrix (n_probes, n_probes)}

    The RDM captures the GEOMETRY of the model's representations:
    which probes are close together, which are far apart. This geometry
    is architecture-independent — it's the same whether the model uses
    GQA or MHA, 4096-dim or 5120-dim.
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model = MODELS[model_key]
    target_layers = get_target_layers(n_layers, depth_fractions)

    # Map layer index → depth fraction for output keying
    layer_to_frac = {}
    for frac in depth_fractions:
        layer = int(round(frac * (n_layers - 1)))
        layer = min(layer, n_layers - 1)
        layer_to_frac[layer] = frac

    print(f"\n  ─── {model_key} ({model_name}) ───", file=sys.stderr, flush=True)
    print(f"  Layers: {n_layers}, d_model: {d_model}", file=sys.stderr, flush=True)
    print(f"  Target layers: {target_layers} (fracs: {depth_fractions})",
          file=sys.stderr, flush=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map=device,
        trust_remote_code=True,
    )
    model.eval()

    # Find the transformer layers (handle different architectures)
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
    elif hasattr(model, 'transformer') and hasattr(model.transformer, 'h'):
        layers = model.transformer.h  # GPT-NeoX / Pythia
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers  # Pythia via GPTNeoXForCausalLM
    else:
        raise ValueError(f"Cannot find transformer layers for {model_key}")

    # Hook to capture hidden states at target layers
    hidden_captures = {li: [] for li in target_layers}
    hooks = []

    for li in target_layers:
        def make_hook(layer_idx):
            def hook_fn(module, input, output):
                if isinstance(output, tuple):
                    h = output[0]
                else:
                    h = output
                # Last token's hidden state
                hidden_captures[layer_idx].append(
                    h[:, -1, :].detach().cpu().float()
                )
            return hook_fn
        h = layers[li].register_forward_hook(make_hook(li))
        hooks.append(h)

    # Run probes one at a time (no batching for simplicity)
    print(f"  Running {len(probes)} probes...", file=sys.stderr, flush=True)
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(
            probe["prompt"], return_tensors="pt"
        ).to(device)
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 100 == 0:
            print(f"    {i+1}/{len(probes)} probes done...",
                  file=sys.stderr, flush=True)
    dt = time.time() - t0
    print(f"  Done in {dt:.1f}s ({dt/len(probes)*1000:.1f}ms/probe)",
          file=sys.stderr, flush=True)

    for h in hooks:
        h.remove()

    # Build RDMs (cosine similarity)
    rdms = {}
    for li in target_layers:
        hs = torch.cat(hidden_captures[li], dim=0).numpy()  # (n_probes, d_model)
        # L2-normalize for cosine similarity
        norms = np.linalg.norm(hs, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-8)
        hs_norm = hs / norms
        rdm = hs_norm @ hs_norm.T  # (n_probes, n_probes)
        frac = layer_to_frac.get(li, li / (n_layers - 1))
        rdms[frac] = rdm
        print(f"  L{li} (depth={frac:.0%}): RDM {rdm.shape}, "
              f"mean_sim={rdm.mean():.4f}", file=sys.stderr, flush=True)

    # Cleanup
    del model, tokenizer
    gc.collect()
    try:
        import torch
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        elif torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        pass

    return rdms


# ══════════════════════════════════════════════════════════════════════
# Cross-model consensus — the universal lattice
# ══════════════════════════════════════════════════════════════════════

def build_consensus(
    all_rdms: dict[str, dict[float, np.ndarray]],
    depth_fractions: list[float],
) -> dict[float, dict]:
    """Build cross-model consensus RDM at each depth.

    For each depth fraction:
      1. Stack per-model RDMs: (N_models, N_probes, N_probes)
      2. Mean → consensus RDM (the average geometry)
      3. Std → disagreement map (where models differ)
      4. Agreement mask = 1 - (std / max_possible_std)
         Values near 1.0 = universal. Values near 0.0 = model-specific.

    The agreement mask is the KEY output: it tells the holographic loss
    which probe-pair distances to trust. High-agreement pairs drive the
    etch. Low-agreement pairs are ignored (contested territory).

    Returns: {depth_frac: {consensus_rdm, agreement_mask, per_model_rdms, stats}}
    """
    results = {}

    for frac in depth_fractions:
        # Collect RDMs from all models at this depth
        model_rdms = []
        model_keys = []
        for model_key, rdms in all_rdms.items():
            if frac in rdms:
                model_rdms.append(rdms[frac])
                model_keys.append(model_key)

        if len(model_rdms) < 2:
            print(f"  Depth {frac:.0%}: only {len(model_rdms)} models, skipping",
                  file=sys.stderr, flush=True)
            continue

        stacked = np.stack(model_rdms)  # (N_models, N_probes, N_probes)
        n_models = stacked.shape[0]

        # Consensus = mean across models
        consensus_rdm = stacked.mean(axis=0)

        # Mean-subtract (residual mode — removes global similarity bias)
        consensus_rdm_centered = consensus_rdm - consensus_rdm.mean()
        np.fill_diagonal(consensus_rdm_centered, 0.0)

        # Agreement = inverse of cross-model standard deviation
        # Low std → high agreement → universal
        # High std → low agreement → model-specific
        cross_std = stacked.std(axis=0)  # (N_probes, N_probes)

        # Normalize to [0, 1]: agreement = 1 - (std / max_possible_std)
        # For cosine similarities in [-1, 1], max std is ~1.0
        # But in practice, std is much smaller. Use empirical max.
        max_std = cross_std.max() if cross_std.max() > 0 else 1.0
        agreement_mask = 1.0 - (cross_std / max_std)

        # Also compute pairwise model agreement (correlation between RDMs)
        # Upper triangle only (RDM is symmetric)
        n_probes = consensus_rdm.shape[0]
        triu_idx = np.triu_indices(n_probes, k=1)
        model_correlations = {}
        for i in range(n_models):
            for j in range(i + 1, n_models):
                v1 = stacked[i][triu_idx]
                v2 = stacked[j][triu_idx]
                corr = np.corrcoef(v1, v2)[0, 1]
                model_correlations[f"{model_keys[i]}_vs_{model_keys[j]}"] = float(corr)

        mean_agreement = float(agreement_mask[triu_idx].mean())
        high_agreement_frac = float((agreement_mask[triu_idx] > 0.8).mean())
        mean_model_corr = float(np.mean(list(model_correlations.values())))

        stats = {
            "n_models": n_models,
            "n_probes": n_probes,
            "model_keys": model_keys,
            "mean_agreement": mean_agreement,
            "high_agreement_fraction": high_agreement_frac,
            "mean_model_correlation": mean_model_corr,
            "model_correlations": model_correlations,
            "consensus_rdm_mean": float(consensus_rdm.mean()),
            "consensus_rdm_std": float(consensus_rdm.std()),
        }

        print(f"  Depth {frac:.0%}: {n_models} models, "
              f"agreement={mean_agreement:.4f}, "
              f"high_agree={high_agreement_frac:.1%}, "
              f"model_corr={mean_model_corr:.4f}",
              file=sys.stderr, flush=True)

        results[frac] = {
            "consensus_rdm": consensus_rdm_centered,
            "consensus_rdm_raw": consensus_rdm,
            "agreement_mask": agreement_mask,
            "stats": stats,
        }

    return results


# ══════════════════════════════════════════════════════════════════════
# SVD — discover universal dimensions
# ══════════════════════════════════════════════════════════════════════

def discover_dimensions(
    consensus_rdm: np.ndarray,
    agreement_mask: np.ndarray,
    min_explained_variance: float = 0.02,
) -> dict:
    """SVD on agreement-weighted consensus RDM to find universal dimensions.

    Weights the RDM by the agreement mask before SVD so that universal
    probe-pair distances contribute more to the decomposition than
    model-specific ones.

    Returns dict with components, explained_variance_ratio, n_dimensions.
    """
    # Weight consensus RDM by agreement
    weighted_rdm = consensus_rdm * agreement_mask

    # SVD
    U, S, Vt = np.linalg.svd(weighted_rdm, full_matrices=False)
    explained = (S ** 2) / (S ** 2).sum()

    # Find dimensions above threshold
    n_dims = int((explained >= min_explained_variance).sum())
    n_dims = max(n_dims, 1)  # at least 1

    # Cumulative variance
    cumvar = np.cumsum(explained)

    print(f"  SVD: {n_dims} dimensions (cumulative variance: {cumvar[n_dims-1]:.1%})",
          file=sys.stderr, flush=True)
    for i in range(min(n_dims + 3, len(explained))):
        marker = "✓" if i < n_dims else " "
        print(f"    {marker} dim {i}: {explained[i]:.4f} (cum: {cumvar[i]:.4f})",
              file=sys.stderr, flush=True)

    return {
        "n_dimensions": n_dims,
        "components": U[:, :n_dims],          # (n_probes, n_dims)
        "singular_values": S[:n_dims],         # (n_dims,)
        "explained_variance_ratio": explained[:n_dims],  # (n_dims,)
        "cumulative_variance": cumvar[:n_dims],
    }


# ══════════════════════════════════════════════════════════════════════
# Save — the lattice artifact
# ══════════════════════════════════════════════════════════════════════

def save_lattice(
    consensus_results: dict[float, dict],
    dimension_results: dict[float, dict],
    probes: list[dict],
    output_dir: Path,
    model_keys: list[str],
) -> None:
    """Save the universal lattice map as .npz and .json."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── NPZ: numpy arrays for use in training ─────────────────
    npz_data = {}
    for frac, result in consensus_results.items():
        key = f"depth_{frac:.2f}"
        npz_data[f"{key}_consensus_rdm"] = result["consensus_rdm"].astype(np.float32)
        npz_data[f"{key}_agreement_mask"] = result["agreement_mask"].astype(np.float32)
        if frac in dimension_results:
            dims = dimension_results[frac]
            npz_data[f"{key}_components"] = dims["components"].astype(np.float32)
            npz_data[f"{key}_singular_values"] = dims["singular_values"].astype(np.float32)
            npz_data[f"{key}_explained_variance"] = dims["explained_variance_ratio"].astype(np.float32)

    npz_path = output_dir / "universal_lattice.npz"
    np.savez_compressed(str(npz_path), **npz_data)
    print(f"\n  💾 NPZ: {npz_path} ({npz_path.stat().st_size / 1024:.1f} KB)",
          file=sys.stderr, flush=True)

    # ── JSON: human-readable metadata ──────────────────────────
    json_data = {
        "description": "Universal lattice map — cross-model consensus RDM",
        "n_probes": len(probes),
        "n_models": len(model_keys),
        "model_keys": model_keys,
        "models": {k: MODELS[k][0] for k in model_keys if k in MODELS},
        "depth_fractions": sorted(consensus_results.keys()),
        "probes": probes,
        "depths": {},
    }

    for frac in sorted(consensus_results.keys()):
        stats = consensus_results[frac]["stats"]
        depth_info = {
            "stats": stats,
        }
        if frac in dimension_results:
            dims = dimension_results[frac]
            depth_info["n_dimensions"] = dims["n_dimensions"]
            depth_info["explained_variance_ratio"] = [
                float(v) for v in dims["explained_variance_ratio"]
            ]
            depth_info["cumulative_variance"] = [
                float(v) for v in dims["cumulative_variance"]
            ]
        json_data["depths"][f"{frac:.2f}"] = depth_info

    json_path = output_dir / "universal_lattice.json"
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)
    print(f"  💾 JSON: {json_path}", file=sys.stderr, flush=True)

    # ── Also save in v12 relational loss format ────────────────
    # Compatible with lambda_kernel_verified_dimensions.json schema
    # so train.py can use it directly.
    compat_data = {
        "n_probes": len(probes),
        "probes": probes,
        "targets": {},
        "source": "cross-model consensus lattice",
        "n_models": len(model_keys),
        "model_keys": model_keys,
    }

    for frac, result in consensus_results.items():
        # Map depth fraction to approximate Qwen3-14B layer index
        # (for compatibility with existing code that uses integer keys)
        approx_layer = int(round(frac * 39))  # 40-layer model
        compat_data["targets"][str(approx_layer)] = {
            "rdm": result["consensus_rdm"].tolist(),
            "agreement_mask": result["agreement_mask"].tolist(),
            "n_probes": len(probes),
            "depth_fraction": frac,
        }
        if frac in dimension_results:
            compat_data["total_dimensions"] = dimension_results[frac]["n_dimensions"]

    compat_path = output_dir / "lattice_relational_target.json"
    with open(compat_path, "w") as f:
        json.dump(compat_data, f)
    print(f"  💾 Compat: {compat_path} (v12 relational loss format)",
          file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Build universal lattice map — cross-model consensus RDM"
    )
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()),
                        help=f"Models to use (default: {DEFAULT_MODELS})")
    parser.add_argument("--corpus", type=str, default=None,
                        help="Path to diverse corpus JSON (from build_diverse_corpus.py). "
                             "If not set, uses lambda kernel probes only.")
    parser.add_argument("--output-dir", type=str, default="lattice",
                        help="Output directory (default: lattice/)")
    parser.add_argument("--device", type=str, default="mps",
                        help="Device for model inference (mps, cuda, cpu)")
    parser.add_argument("--depth-fractions", nargs="+", type=float,
                        default=[0.0, 0.25, 0.5, 0.75],
                        help="Relative depth fractions to extract RDMs at")
    parser.add_argument("--min-explained-variance", type=float, default=0.02,
                        help="Minimum explained variance to count as a dimension")

    args = parser.parse_args()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  Universal Lattice Map — Cross-Model Consensus", file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print(f"  Depths: {args.depth_fractions}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t_start = time.time()

    # ── Load probes ───────────────────────────────────────────
    print("\n1. Loading probes...", file=sys.stderr, flush=True)
    probes = load_probes(corpus_path=args.corpus)

    # ── Extract RDMs from each model ──────────────────────────
    print("\n2. Extracting per-model RDMs...", file=sys.stderr, flush=True)
    all_rdms: dict[str, dict[float, np.ndarray]] = {}
    for model_key in args.models:
        if model_key not in MODELS:
            print(f"  WARNING: Unknown model {model_key}, skipping",
                  file=sys.stderr, flush=True)
            continue
        rdms = extract_rdm(model_key, probes, args.depth_fractions, args.device)
        all_rdms[model_key] = rdms

    if len(all_rdms) < 2:
        print("ERROR: Need at least 2 models for consensus. Exiting.",
              file=sys.stderr, flush=True)
        sys.exit(1)

    # ── Build cross-model consensus ───────────────────────────
    print("\n3. Building cross-model consensus...", file=sys.stderr, flush=True)
    consensus_results = build_consensus(all_rdms, args.depth_fractions)

    # ── Discover universal dimensions via SVD ─────────────────
    print("\n4. Discovering universal dimensions...", file=sys.stderr, flush=True)
    dimension_results = {}
    for frac, result in consensus_results.items():
        print(f"\n  Depth {frac:.0%}:", file=sys.stderr, flush=True)
        dims = discover_dimensions(
            result["consensus_rdm"],
            result["agreement_mask"],
            min_explained_variance=args.min_explained_variance,
        )
        dimension_results[frac] = dims

    # ── Save ──────────────────────────────────────────────────
    print("\n5. Saving lattice map...", file=sys.stderr, flush=True)
    output_dir = Path(args.output_dir)
    save_lattice(
        consensus_results, dimension_results,
        probes, output_dir, list(all_rdms.keys()),
    )

    elapsed = time.time() - t_start
    print(f"\n{'='*72}", file=sys.stderr, flush=True)
    print(f"  Universal Lattice Map Complete", file=sys.stderr, flush=True)
    print(f"  Models: {len(all_rdms)}", file=sys.stderr, flush=True)
    print(f"  Probes: {len(probes)}", file=sys.stderr, flush=True)
    print(f"  Depths: {len(consensus_results)}", file=sys.stderr, flush=True)
    for frac in sorted(consensus_results.keys()):
        s = consensus_results[frac]["stats"]
        d = dimension_results.get(frac, {})
        print(f"    {frac:.0%}: agreement={s['mean_agreement']:.4f}, "
              f"model_corr={s['mean_model_correlation']:.4f}, "
              f"dims={d.get('n_dimensions', '?')}",
              file=sys.stderr, flush=True)
    print(f"  Elapsed: {elapsed:.0f}s", file=sys.stderr, flush=True)
    print(f"  Output: {output_dir}/", file=sys.stderr, flush=True)
    print(f"{'='*72}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
