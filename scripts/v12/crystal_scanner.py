"""Crystal Scanner — discover self-similar crystals in any skill domain.

Method: PCA-project Q vectors for domain probes across models and depths.
The domain's INTERNAL geometry (probe×probe RDM) IS the crystal. Measure
cross-model agreement on this geometry to find universal structure.

For each domain, outputs:
  1. Intra-domain consensus RDM in PCA-Q space (the domain crystal)
  2. Cross-model agreement at each depth (where is the crystal sharpest?)
  3. Self-similarity across depths (is the crystal the same at all depths?)
  4. Crystal dimensionality (SVD of the consensus RDM)
  5. Probe cluster structure (natural subclusters within the domain)

Usage:
    uv run python scripts/v12/crystal_scanner.py
    uv run python scripts/v12/crystal_scanner.py --domain coding
    uv run python scripts/v12/crystal_scanner.py --models qwen3-14b mistral-7b olmo-2-13b pythia-2.8b

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

DEPTH_FRACTIONS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

SKILL_DOMAINS = [
    "lambda", "arithmetic", "coding", "tool", "retrieval",
    "analogy", "reasoning", "narrative", "instruction",
]


def load_probes(probe_path: str | None = None) -> list[dict]:
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json")
    with open(probe_path) as f:
        probes = json.load(f)
    print(f"  Loaded {len(probes)} probes", file=sys.stderr, flush=True)
    return probes


def get_domain_indices(probes: list[dict]) -> dict[str, list[int]]:
    domain_idx: dict[str, list[int]] = {}
    for i, p in enumerate(probes):
        d = p["axis"].split("/")[0]
        domain_idx.setdefault(d, []).append(i)
    return domain_idx


def extract_q_vectors(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[float, np.ndarray]:
    """Extract Q vectors from one model. Returns {depth: (n_probes, d_q)}."""
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

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device, trust_remote_code=True,
    )
    model.eval()

    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
        get_attn = lambda l: l.self_attn
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
        get_attn = lambda l: l.attention
    else:
        raise ValueError(f"Unknown arch for {model_key}")

    test_attn = get_attn(layers[0])
    is_fused = hasattr(test_attn, 'query_key_value')

    captures: dict[int, list] = {li: [] for li, _ in target_layers}
    hooks = []

    for layer_idx, frac in target_layers:
        attn_mod = get_attn(layers[layer_idx])
        if is_fused:
            fused = attn_mod.query_key_value
            q_size = d_model
            def make_hook(li, qs):
                def hook_fn(module, input, output):
                    captures[li].append(output[:, -1, :qs].detach().cpu().float())
                return hook_fn
            hooks.append(fused.register_forward_hook(make_hook(layer_idx, q_size)))
        else:
            q_proj = attn_mod.q_proj
            def make_hook(li):
                def hook_fn(module, input, output):
                    captures[li].append(output[:, -1, :].detach().cpu().float())
                return hook_fn
            hooks.append(q_proj.register_forward_hook(make_hook(layer_idx)))

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

    results = {}
    for layer_idx, frac in target_layers:
        mat = torch.cat(captures[layer_idx], dim=0).numpy()
        results[frac] = mat

    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available(): _t.mps.empty_cache()
        elif _t.cuda.is_available(): _t.cuda.empty_cache()
    except Exception: pass

    return results


def pca_project(X: np.ndarray, n_components: int = 64) -> np.ndarray:
    X_centered = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    k = min(n_components, U.shape[1])
    return U[:, :k] * S[:k]


def cosine_rdm(X: np.ndarray) -> np.ndarray:
    norms = np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-8)
    return (X / norms) @ (X / norms).T


def rdm_correlation(rdm_a: np.ndarray, rdm_b: np.ndarray) -> float:
    n = rdm_a.shape[0]
    triu = np.triu_indices(n, k=1)
    return float(np.corrcoef(rdm_a[triu], rdm_b[triu])[0, 1])


def scan_domain(
    domain: str,
    domain_indices: list[int],
    all_q_vectors: dict[str, dict[float, np.ndarray]],
    probes: list[dict],
    pca_dim: int = 64,
) -> dict:
    """Scan one domain for self-similar crystal structure."""
    model_keys = list(all_q_vectors.keys())
    n_probes = len(domain_indices)
    domain_probes = [probes[i] for i in domain_indices]

    # Extract domain-specific PCA-Q RDMs per model per depth
    per_model_rdms: dict[str, dict[float, np.ndarray]] = {}
    for mk in model_keys:
        per_model_rdms[mk] = {}
        for frac in DEPTH_FRACTIONS:
            if frac not in all_q_vectors[mk]:
                continue
            # Extract just this domain's Q vectors
            all_q = all_q_vectors[mk][frac]
            domain_q = all_q[domain_indices]
            # PCA project
            domain_pca = pca_project(domain_q, pca_dim)
            # Build intra-domain RDM
            rdm = cosine_rdm(domain_pca)
            per_model_rdms[mk][frac] = rdm

    # Build consensus RDM per depth
    consensus_rdms: dict[float, np.ndarray] = {}
    agreement_per_depth: dict[float, float] = {}

    for frac in DEPTH_FRACTIONS:
        model_rdms = []
        mk_list = []
        for mk in model_keys:
            if frac in per_model_rdms[mk]:
                model_rdms.append(per_model_rdms[mk][frac])
                mk_list.append(mk)

        if len(model_rdms) < 2:
            continue

        stacked = np.stack(model_rdms)
        consensus = stacked.mean(axis=0)
        consensus_rdms[frac] = consensus

        # Cross-model agreement (mean pairwise RDM correlation)
        corrs = []
        for i in range(len(model_rdms)):
            for j in range(i + 1, len(model_rdms)):
                corrs.append(rdm_correlation(model_rdms[i], model_rdms[j]))
        agreement_per_depth[frac] = float(np.mean(corrs))

    # Self-similarity: cross-depth correlation of consensus RDMs
    depth_keys = sorted(consensus_rdms.keys())
    n_depths = len(depth_keys)
    self_sim = np.zeros((n_depths, n_depths))
    for i, di in enumerate(depth_keys):
        for j, dj in enumerate(depth_keys):
            self_sim[i, j] = rdm_correlation(consensus_rdms[di], consensus_rdms[dj])

    # Crystal dimensionality (SVD of average consensus RDM)
    if consensus_rdms:
        avg_consensus = np.mean(list(consensus_rdms.values()), axis=0)
        np.fill_diagonal(avg_consensus, 0)  # zero diagonal for SVD
        U, S, Vt = np.linalg.svd(avg_consensus, full_matrices=False)
        explained = (S ** 2) / max((S ** 2).sum(), 1e-8)
        cumvar = np.cumsum(explained)
        n_dims_50 = int(np.searchsorted(cumvar, 0.5)) + 1
        n_dims_80 = int(np.searchsorted(cumvar, 0.8)) + 1
        n_dims_95 = int(np.searchsorted(cumvar, 0.95)) + 1
    else:
        explained = np.array([])
        n_dims_50 = n_dims_80 = n_dims_95 = 0

    # Best depth (highest cross-model agreement)
    best_depth = max(agreement_per_depth, key=agreement_per_depth.get) if agreement_per_depth else 0.5
    best_agreement = agreement_per_depth.get(best_depth, 0)

    # Probe clustering at best depth
    best_rdm = consensus_rdms.get(best_depth, np.eye(n_probes))
    # Simple clustering: find probe pairs with highest and lowest similarity
    triu = np.triu_indices(n_probes, k=1)
    sims = best_rdm[triu]
    probe_labels = [p["axis"].split("/")[1] if "/" in p["axis"] else p["axis"]
                    for p in domain_probes]

    # Top-5 most similar pairs
    top_idx = np.argsort(sims)[-5:][::-1]
    top_pairs = [(probe_labels[triu[0][k]], probe_labels[triu[1][k]], float(sims[k]))
                 for k in top_idx]

    # Bottom-5 least similar pairs
    bot_idx = np.argsort(sims)[:5]
    bot_pairs = [(probe_labels[triu[0][k]], probe_labels[triu[1][k]], float(sims[k]))
                 for k in bot_idx]

    return {
        "domain": domain,
        "n_probes": n_probes,
        "n_models": len(model_keys),
        "agreement_per_depth": {f"{f:.2f}": a for f, a in sorted(agreement_per_depth.items())},
        "best_depth": best_depth,
        "best_agreement": best_agreement,
        "self_similarity_matrix": self_sim.tolist(),
        "self_similarity_depths": [f"{d:.2f}" for d in depth_keys],
        "mean_self_similarity": float(self_sim[np.triu_indices(n_depths, k=1)].mean()) if n_depths > 1 else 0,
        "crystal_dims_50pct": n_dims_50,
        "crystal_dims_80pct": n_dims_80,
        "crystal_dims_95pct": n_dims_95,
        "explained_variance_top5": explained[:5].tolist() if len(explained) >= 5 else explained.tolist(),
        "consensus_rdm_at_best": best_rdm.tolist(),
        "probe_labels": probe_labels,
        "most_similar_pairs": top_pairs,
        "least_similar_pairs": bot_pairs,
    }


def print_scan_results(results: dict[str, dict]) -> None:
    """Print crystal scanner results."""
    print(f"\n{'='*90}", file=sys.stderr, flush=True)
    print(f"  CRYSTAL SCANNER — Self-Similar Structure per Domain", file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)

    # ── Summary table ─────────────────────────────────────────
    print(f"\n  {'domain':>12s}  {'best_depth':>10s}  {'agreement':>9s}  {'self_sim':>8s}  "
          f"{'dims_50':>7s}  {'dims_80':>7s}  {'dims_95':>7s}",
          file=sys.stderr, flush=True)
    print(f"  {'-'*70}", file=sys.stderr, flush=True)

    for domain in SKILL_DOMAINS:
        if domain not in results:
            continue
        r = results[domain]
        print(f"  {domain:>12s}  {r['best_depth']:>10.0%}  {r['best_agreement']:>+9.4f}  "
              f"{r['mean_self_similarity']:>+8.4f}  "
              f"{r['crystal_dims_50pct']:>7d}  {r['crystal_dims_80pct']:>7d}  "
              f"{r['crystal_dims_95pct']:>7d}",
              file=sys.stderr, flush=True)

    # ── Per-domain detail ─────────────────────────────────────
    for domain in SKILL_DOMAINS:
        if domain not in results:
            continue
        r = results[domain]

        print(f"\n  ═══ {domain.upper()} ═══", file=sys.stderr, flush=True)

        # Agreement profile across depths
        print(f"  Agreement profile:", file=sys.stderr, flush=True)
        for dk, av in sorted(r["agreement_per_depth"].items()):
            bar = "█" * int(av * 40)
            marker = " ★" if float(dk) == r["best_depth"] else ""
            print(f"    {dk}: {av:+.4f} {bar}{marker}", file=sys.stderr, flush=True)

        # Self-similarity
        print(f"  Mean cross-depth self-similarity: {r['mean_self_similarity']:+.4f}",
              file=sys.stderr, flush=True)

        # Dimensionality
        ev = r["explained_variance_top5"]
        print(f"  Crystal dimensionality: {r['crystal_dims_50pct']}d (50%), "
              f"{r['crystal_dims_80pct']}d (80%), {r['crystal_dims_95pct']}d (95%)",
              file=sys.stderr, flush=True)
        if ev:
            print(f"  Top-5 explained variance: {', '.join(f'{v:.1%}' for v in ev)}",
                  file=sys.stderr, flush=True)

        # Probe structure
        print(f"  Most similar probe pairs:", file=sys.stderr, flush=True)
        for p1, p2, s in r["most_similar_pairs"]:
            print(f"    {p1:>20s} ↔ {p2:<20s}  sim={s:+.4f}", file=sys.stderr, flush=True)
        print(f"  Most different probe pairs:", file=sys.stderr, flush=True)
        for p1, p2, s in r["least_similar_pairs"]:
            print(f"    {p1:>20s} ↔ {p2:<20s}  sim={s:+.4f}", file=sys.stderr, flush=True)

    print(f"\n{'='*90}", file=sys.stderr, flush=True)


def main():
    parser = argparse.ArgumentParser(description="Crystal Scanner")
    parser.add_argument("--models", nargs="+", default=None,
                        choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--domain", type=str, default=None,
                        help="Scan single domain (default: all)")
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--pca-dim", type=int, default=64)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output-dir", type=str, default="results/crystal-scanner")

    args = parser.parse_args()
    model_keys = args.models or (QUICK_MODELS if args.quick else DEFAULT_MODELS)
    domains_to_scan = [args.domain] if args.domain else SKILL_DOMAINS

    print("=" * 72, file=sys.stderr, flush=True)
    print("  Crystal Scanner — Domain Crystal Discovery", file=sys.stderr, flush=True)
    print(f"  Models: {model_keys}", file=sys.stderr, flush=True)
    print(f"  Domains: {domains_to_scan}", file=sys.stderr, flush=True)
    print(f"  PCA dim: {args.pca_dim}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t_start = time.time()
    probes = load_probes(args.probes)
    domain_indices = get_domain_indices(probes)

    # Extract Q vectors from all models
    all_q_vectors: dict[str, dict[float, np.ndarray]] = {}
    for mk in model_keys:
        q_vecs = extract_q_vectors(mk, probes, DEPTH_FRACTIONS, args.device)
        all_q_vectors[mk] = q_vecs

    # Scan each domain
    results: dict[str, dict] = {}
    for domain in domains_to_scan:
        if domain not in domain_indices:
            print(f"  WARNING: domain '{domain}' not found in probes", file=sys.stderr)
            continue
        print(f"\n  Scanning {domain}...", file=sys.stderr, flush=True)
        results[domain] = scan_domain(
            domain, domain_indices[domain], all_q_vectors, probes, args.pca_dim
        )

    # Print results
    print_scan_results(results)

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_data = {
        "description": "Crystal scanner — per-domain self-similar structure",
        "n_models": len(model_keys),
        "model_keys": model_keys,
        "pca_dim": args.pca_dim,
        "domains": results,
    }
    json_path = output_dir / "crystal_scan.json"
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"\n  💾 {json_path}", file=sys.stderr, flush=True)

    elapsed = time.time() - t_start
    print(f"  Total: {elapsed:.0f}s", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
