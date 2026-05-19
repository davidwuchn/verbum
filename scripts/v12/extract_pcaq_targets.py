"""Extract 8×8 combinator cosine targets from PCA-projected Q space.

Uses the binding chain probes (which include pure combinator anchors)
run through multiple models. Extracts Q vectors, PCA-projects to top-k
dimensions, then measures the 8×8 combinator cosine matrix in PCA-Q
space. These are the SHARP crystal constants for V13.

Comparison: also extracts hidden-state targets for direct comparison.

Usage:
    uv run python scripts/v12/extract_pcaq_targets.py
    uv run python scripts/v12/extract_pcaq_targets.py --models qwen3-14b mistral-7b olmo-2-13b pythia-2.8b
    uv run python scripts/v12/extract_pcaq_targets.py --pca-dim 64

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

MODELS = {
    "qwen3-14b":    ("Qwen/Qwen3-14B",                40, 5120),
    "llama-3-8b":   ("meta-llama/Llama-3.1-8B",       32, 4096),
    "mistral-7b":   ("mistralai/Mistral-7B-v0.3",     32, 4096),
    "olmo-2-13b":   ("allenai/OLMo-2-1124-13B",       40, 5120),
    "olmo-2-7b":    ("allenai/OLMo-2-1124-7B",        32, 4096),
    "pythia-2.8b":  ("EleutherAI/pythia-2.8b-deduped", 32, 2560),
    "pythia-1.4b":  ("EleutherAI/pythia-1.4b-deduped", 24, 2048),
    "smollm3-3b":   ("HuggingFaceTB/SmolLM3-3B",      36, 2560),
}

DEFAULT_MODELS = ["qwen3-14b", "mistral-7b", "olmo-2-13b", "pythia-2.8b"]
QUICK_MODELS = ["mistral-7b", "pythia-2.8b"]

# Zone depths from v13-funnel-shape.md
ZONE_DEPTHS = {
    "A": [0.0, 0.1, 0.2],       # encode
    "B": [0.3, 0.4, 0.5, 0.6],  # compute
    "C": [0.7, 0.8, 0.9],       # converge
}
ALL_DEPTHS = sorted(set(d for ds in ZONE_DEPTHS.values() for d in ds))

COMBINATOR_ORDER = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]


def load_probes(probe_path: str | None = None) -> list[dict]:
    """Load binding chain probes (includes pure combinator anchors)."""
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "binding_chain_probes.json")
    with open(probe_path) as f:
        probes = json.load(f)
    print(f"  Loaded {len(probes)} probes", file=sys.stderr, flush=True)
    return probes


def get_pure_indices(probes: list[dict]) -> dict[str, int]:
    pure_idx = {}
    for i, p in enumerate(probes):
        if p["axis"].startswith("pure/"):
            comb = p["axis"].split("/")[1]
            pure_idx[comb] = i
    return pure_idx


def extract_vectors(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[float, dict[str, np.ndarray]]:
    """Extract hidden and Q vectors from one model."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model = MODELS[model_key]
    target_layers = []
    frac_to_layer = {}
    for frac in depth_fractions:
        layer = min(int(round(frac * (n_layers - 1))), n_layers - 1)
        if layer not in [l for l, _ in target_layers]:
            target_layers.append((layer, frac))
            frac_to_layer[frac] = layer

    print(f"\n  ─── {model_key} ({model_name}) ───", file=sys.stderr, flush=True)
    print(f"  Layers: {n_layers}, d_model: {d_model}", file=sys.stderr, flush=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device, trust_remote_code=True,
    )
    model.eval()

    # Architecture detection
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
        get_attn = lambda l: l.self_attn
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
        get_attn = lambda l: l.attention
    else:
        raise ValueError(f"Unknown architecture for {model_key}")

    test_attn = get_attn(layers[0])
    is_fused = hasattr(test_attn, 'query_key_value')

    captures: dict[int, dict[str, list]] = {}
    hooks = []

    for layer_idx, frac in target_layers:
        captures[layer_idx] = {"hidden": [], "Q": []}
        layer_mod = layers[layer_idx]
        attn_mod = get_attn(layer_mod)

        def make_hidden_hook(li):
            def hook_fn(module, input, output):
                h = output[0] if isinstance(output, tuple) else output
                captures[li]["hidden"].append(h[:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(layer_mod.register_forward_hook(make_hidden_hook(layer_idx)))

        if is_fused:
            fused = attn_mod.query_key_value
            q_size = d_model  # Q always gets d_model dims
            def make_fused_hook(li, qs):
                def hook_fn(module, input, output):
                    captures[li]["Q"].append(output[:, -1, :qs].detach().cpu().float())
                return hook_fn
            hooks.append(fused.register_forward_hook(make_fused_hook(layer_idx, q_size)))
        else:
            q_proj = attn_mod.q_proj
            def make_q_hook(li):
                def hook_fn(module, input, output):
                    captures[li]["Q"].append(output[:, -1, :].detach().cpu().float())
                return hook_fn
            hooks.append(q_proj.register_forward_hook(make_q_hook(layer_idx)))

    print(f"  Running {len(probes)} probes...", file=sys.stderr, flush=True)
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 50 == 0:
            print(f"    {i+1}/{len(probes)}...", file=sys.stderr, flush=True)
    dt = time.time() - t0
    print(f"  Done in {dt:.1f}s", file=sys.stderr, flush=True)

    for h in hooks:
        h.remove()

    import torch as _t
    results = {}
    for layer_idx, frac in target_layers:
        space_vecs = {}
        for space in ["hidden", "Q"]:
            vecs = captures[layer_idx][space]
            if vecs:
                space_vecs[space] = _t.cat(vecs, dim=0).numpy()
        results[frac] = space_vecs

    del model, tokenizer
    gc.collect()
    try:
        if _t.backends.mps.is_available(): _t.mps.empty_cache()
        elif _t.cuda.is_available(): _t.cuda.empty_cache()
    except Exception: pass

    return results


def pca_project(X: np.ndarray, n_components: int = 64) -> np.ndarray:
    X_centered = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    k = min(n_components, U.shape[1])
    return U[:, :k] * S[:k]


def cosine_matrix(X: np.ndarray, indices: list[int]) -> np.ndarray:
    """Extract cosine similarity matrix for specific indices."""
    vecs = X[indices]
    norms = np.maximum(np.linalg.norm(vecs, axis=1, keepdims=True), 1e-8)
    vecs_norm = vecs / norms
    return vecs_norm @ vecs_norm.T


def extract_targets(
    all_vectors: dict[str, dict[float, dict[str, np.ndarray]]],
    probes: list[dict],
    pca_dim: int = 64,
) -> dict:
    """Extract 8×8 combinator cosine targets from PCA-Q and hidden spaces."""
    pure_idx = get_pure_indices(probes)
    comb_indices = [pure_idx[c] for c in COMBINATOR_ORDER if c in pure_idx]
    n_comb = len(comb_indices)
    model_keys = list(all_vectors.keys())

    results = {}

    for frac in ALL_DEPTHS:
        # Collect per-model cosine matrices in each space
        per_model = {"hidden": [], "Q_raw": [], "Q_pca": []}

        for mk in model_keys:
            if frac not in all_vectors[mk]:
                continue

            for space_key, transform in [
                ("hidden", lambda X: X),
                ("Q_raw", lambda X: X),
                ("Q_pca", lambda X: pca_project(X, pca_dim)),
            ]:
                src = "hidden" if space_key == "hidden" else "Q"
                if src not in all_vectors[mk][frac]:
                    continue
                vecs = all_vectors[mk][frac][src]
                try:
                    tvecs = transform(vecs)
                except Exception:
                    continue
                cos = cosine_matrix(tvecs, comb_indices)
                per_model[space_key].append(cos)

        # Consensus (average across models)
        frac_results = {}
        for space_key in ["hidden", "Q_raw", "Q_pca"]:
            matrices = per_model[space_key]
            if len(matrices) < 2:
                continue

            stacked = np.stack(matrices)
            consensus = stacked.mean(axis=0)
            std = stacked.std(axis=0)

            # Cross-model agreement (mean pairwise correlation of upper-tri)
            triu = np.triu_indices(n_comb, k=1)
            corrs = []
            for i in range(len(matrices)):
                for j in range(i + 1, len(matrices)):
                    v1 = matrices[i][triu]
                    v2 = matrices[j][triu]
                    corrs.append(float(np.corrcoef(v1, v2)[0, 1]))
            mean_corr = float(np.mean(corrs))

            frac_results[space_key] = {
                "matrix": consensus,
                "std": std,
                "agreement": mean_corr,
                "n_models": len(matrices),
                "upper_tri": consensus[triu].tolist(),
                "upper_tri_std": std[triu].tolist(),
            }

        results[frac] = frac_results

    return results


def print_targets(results: dict, pca_dim: int) -> None:
    """Print 8×8 combinator cosine targets in copy-pasteable format."""
    
    print(f"\n{'='*90}", file=sys.stderr, flush=True)
    print(f"  8×8 COMBINATOR COSINE TARGETS", file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)

    # ── Per-zone targets ──────────────────────────────────────
    for zone_name, zone_depths in ZONE_DEPTHS.items():
        print(f"\n  ═══ Zone {zone_name} ═══", file=sys.stderr, flush=True)

        for space in ["hidden", "Q_pca"]:
            # Average across zone depths
            zone_matrices = []
            zone_agreements = []
            for frac in zone_depths:
                if frac in results and space in results[frac]:
                    zone_matrices.append(results[frac][space]["matrix"])
                    zone_agreements.append(results[frac][space]["agreement"])

            if not zone_matrices:
                continue

            avg_matrix = np.mean(zone_matrices, axis=0)
            avg_agree = np.mean(zone_agreements)

            print(f"\n  Zone {zone_name} — {space} (agreement={avg_agree:.3f}):",
                  file=sys.stderr, flush=True)
            print(f"  {'':>6s}", end='', file=sys.stderr)
            for c in COMBINATOR_ORDER:
                print(f"  {c:>7s}", end='', file=sys.stderr)
            print(file=sys.stderr, flush=True)

            for i, ci in enumerate(COMBINATOR_ORDER):
                print(f"  {ci:>6s}", end='', file=sys.stderr)
                for j, cj in enumerate(COMBINATOR_ORDER):
                    if i == j:
                        print(f"  {'--':>7s}", end='', file=sys.stderr)
                    else:
                        print(f"  {avg_matrix[i,j]:+.4f}", end='', file=sys.stderr)
                print(file=sys.stderr, flush=True)

    # ── Agreement comparison across depths ────────────────────
    print(f"\n\n  Cross-Model Agreement: hidden vs Q_pca (PCA dim={pca_dim})",
          file=sys.stderr, flush=True)
    print(f"  {'depth':>6s}  {'hidden':>8s}  {'Q_pca':>8s}  {'delta':>8s}",
          file=sys.stderr, flush=True)
    print(f"  {'-'*34}", file=sys.stderr, flush=True)

    for frac in ALL_DEPTHS:
        h_agree = results.get(frac, {}).get("hidden", {}).get("agreement", 0)
        q_agree = results.get(frac, {}).get("Q_pca", {}).get("agreement", 0)
        delta = q_agree - h_agree
        marker = "★" if delta > 0.05 else " "
        print(f"  {frac:>6.0%}  {h_agree:>+8.4f}  {q_agree:>+8.4f}  {delta:>+8.4f} {marker}",
              file=sys.stderr, flush=True)

    # ── Python-pasteable format ───────────────────────────────
    print(f"\n\n  # Python-pasteable PCA-Q targets (zone-averaged)",
          file=sys.stderr, flush=True)
    
    for zone_name, zone_depths in ZONE_DEPTHS.items():
        zone_matrices = []
        for frac in zone_depths:
            if frac in results and "Q_pca" in results[frac]:
                zone_matrices.append(results[frac]["Q_pca"]["matrix"])
        if not zone_matrices:
            continue
        avg = np.mean(zone_matrices, axis=0)
        
        print(f"\n  # Zone {zone_name} ({', '.join(f'{d:.0%}' for d in zone_depths)})",
              file=sys.stderr, flush=True)
        print(f"  # Order: {', '.join(COMBINATOR_ORDER)}",
              file=sys.stderr, flush=True)
        print(f"  pcaq_zone_{zone_name.lower()}_targets = (", file=sys.stderr, flush=True)
        for i in range(len(COMBINATOR_ORDER)):
            row = []
            for j in range(len(COMBINATOR_ORDER)):
                row.append(f"{avg[i,j]:+.4f}")
            print(f"      ({', '.join(row)}),  # {COMBINATOR_ORDER[i]}",
                  file=sys.stderr, flush=True)
        print(f"  )", file=sys.stderr, flush=True)


def save_results(results: dict, output_dir: Path, pca_dim: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON with all targets
    json_data = {
        "description": "8×8 combinator cosine targets from PCA-Q and hidden spaces",
        "pca_dim": pca_dim,
        "combinator_order": COMBINATOR_ORDER,
        "zone_definitions": {k: v for k, v in ZONE_DEPTHS.items()},
        "per_depth": {},
    }

    for frac in ALL_DEPTHS:
        frac_data = {}
        for space_key in ["hidden", "Q_raw", "Q_pca"]:
            if frac in results and space_key in results[frac]:
                r = results[frac][space_key]
                frac_data[space_key] = {
                    "matrix": r["matrix"].tolist(),
                    "std": r["std"].tolist(),
                    "agreement": r["agreement"],
                    "n_models": r["n_models"],
                    "upper_tri_values": r["upper_tri"],
                    "upper_tri_std": r["upper_tri_std"],
                }
        json_data["per_depth"][f"{frac:.2f}"] = frac_data

    # Zone averages
    json_data["zone_targets"] = {}
    for zone_name, zone_depths in ZONE_DEPTHS.items():
        for space_key in ["hidden", "Q_pca"]:
            matrices = []
            agreements = []
            for frac in zone_depths:
                if frac in results and space_key in results[frac]:
                    matrices.append(results[frac][space_key]["matrix"])
                    agreements.append(results[frac][space_key]["agreement"])
            if matrices:
                avg = np.mean(matrices, axis=0)
                json_data["zone_targets"][f"zone_{zone_name}_{space_key}"] = {
                    "matrix": avg.tolist(),
                    "agreement": float(np.mean(agreements)),
                    "depths": zone_depths,
                }

    json_path = output_dir / "pcaq_targets.json"
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)
    print(f"\n  💾 {json_path}", file=sys.stderr, flush=True)


def main():
    parser = argparse.ArgumentParser(description="Extract PCA-Q combinator targets")
    parser.add_argument("--models", nargs="+", default=None,
                        choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--pca-dim", type=int, default=64)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output-dir", type=str, default="results/pcaq-targets")

    args = parser.parse_args()
    model_keys = args.models or (QUICK_MODELS if args.quick else DEFAULT_MODELS)

    print("=" * 72, file=sys.stderr, flush=True)
    print("  Extract PCA-Q Combinator Cosine Targets", file=sys.stderr, flush=True)
    print(f"  Models: {model_keys}", file=sys.stderr, flush=True)
    print(f"  PCA dim: {args.pca_dim}", file=sys.stderr, flush=True)
    print(f"  Depths: {ALL_DEPTHS}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t_start = time.time()
    probes = load_probes(args.probes)

    all_vectors = {}
    for mk in model_keys:
        vecs = extract_vectors(mk, probes, ALL_DEPTHS, args.device)
        all_vectors[mk] = vecs

    if len(all_vectors) < 2:
        print("ERROR: Need ≥2 models", file=sys.stderr)
        sys.exit(1)

    print("\n  Extracting targets...", file=sys.stderr, flush=True)
    results = extract_targets(all_vectors, probes, args.pca_dim)

    print_targets(results, args.pca_dim)
    save_results(results, Path(args.output_dir), args.pca_dim)

    elapsed = time.time() - t_start
    print(f"\n  Total: {elapsed:.0f}s", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
