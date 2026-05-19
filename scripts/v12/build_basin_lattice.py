"""Build Basin Lattice — multi-domain skill basin exploration.

Hypothesis: the lambda crystal is one of dozens of rotationally invariant
attractor basins. Each skill domain (lambda, arithmetic, coding, tool
calling, etc.) has its own self-similar crystal geometry — a distinct
8×8 cosine matrix that multiple independently trained models converge to.

This script:
  1. Runs 144 probes (9 skill domains + 9 combinator anchors) through models
  2. Extracts per-domain RDMs at multiple depth fractions
  3. Computes cross-model consensus per domain
  4. Extracts per-domain 8×8 combinator cosine geometry
  5. Compares geometries across domains (basin distinctness)
  6. Counts distinct basins via clustering

Key output:
  - Per-domain 8×8 cosine matrices (the basin fingerprints)
  - Cross-domain similarity matrix (how different are the basins?)
  - Cross-model agreement per domain (is this basin universal?)
  - Estimated basin count from clustering

Usage:
    uv run python scripts/v12/build_basin_lattice.py
    uv run python scripts/v12/build_basin_lattice.py --models qwen3-14b mistral-7b
    uv run python scripts/v12/build_basin_lattice.py --models pythia-2.8b pythia-1.4b --quick

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
# Model registry (shared with build_binding_lattice.py)
# ══════════════════════════════════════════════════════════════════════

MODELS = {
    "qwen3.6-27b":  ("Qwen/Qwen3.6-27B",             64, 5120),
    "qwen3-14b":    ("Qwen/Qwen3-14B",                40, 5120),
    "llama-3-8b":   ("meta-llama/Llama-3.1-8B",       32, 4096),
    "mistral-7b":   ("mistralai/Mistral-7B-v0.3",     32, 4096),
    "olmo-2-13b":   ("allenai/OLMo-2-1124-13B",       40, 5120),
    "olmo-2-7b":    ("allenai/OLMo-2-1124-7B",        32, 4096),
    "pythia-6.9b":  ("EleutherAI/pythia-6.9b",         32, 4096),
    "pythia-2.8b":  ("EleutherAI/pythia-2.8b-deduped", 32, 2560),
    "pythia-1.4b":  ("EleutherAI/pythia-1.4b-deduped", 24, 2048),
    "smollm3-3b":   ("HuggingFaceTB/SmolLM3-3B",      36, 2560),
    "phi-4-mini":   ("microsoft/Phi-4-mini-instruct",  32, 3072),
}

DEFAULT_MODELS = ["qwen3-14b", "mistral-7b", "olmo-2-13b", "pythia-2.8b"]
QUICK_MODELS = ["mistral-7b", "pythia-2.8b"]

# Depth fractions — 3 key zones from funnel shape
BASIN_DEPTH_FRACTIONS = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9]
QUICK_DEPTH_FRACTIONS = [0.2, 0.5, 0.8]

# Skill domains (excluding 'pure' anchors)
SKILL_DOMAINS = [
    "lambda", "arithmetic", "coding", "tool", "retrieval",
    "analogy", "reasoning", "narrative", "instruction",
]

COMBINATOR_ORDER = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]


# ══════════════════════════════════════════════════════════════════════
# Probe loading
# ══════════════════════════════════════════════════════════════════════

def load_probes(probe_path: str | None = None) -> list[dict]:
    """Load basin probes from JSON."""
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json")

    path = Path(probe_path)
    if not path.exists():
        print(f"ERROR: Probe file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        probes = json.load(f)

    cats: dict[str, int] = {}
    for p in probes:
        cat = p["axis"].split("/")[0]
        cats[cat] = cats.get(cat, 0) + 1

    print(f"  Loaded {len(probes)} probes from {path.name}:", file=sys.stderr, flush=True)
    for c, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"    {c:12s}: {n:3d}", file=sys.stderr, flush=True)

    return probes


def get_domain_indices(probes: list[dict]) -> dict[str, list[int]]:
    """Map domain names to probe indices."""
    domain_idx: dict[str, list[int]] = {}
    for i, p in enumerate(probes):
        domain = p["axis"].split("/")[0]
        domain_idx.setdefault(domain, []).append(i)
    return domain_idx


def get_pure_indices(probes: list[dict]) -> dict[str, int]:
    """Map combinator names to pure anchor probe indices."""
    pure_idx: dict[str, int] = {}
    for i, p in enumerate(probes):
        if p["axis"].startswith("pure/"):
            comb = p["axis"].split("/")[1]
            pure_idx[comb] = i
    return pure_idx


# ══════════════════════════════════════════════════════════════════════
# Depth mapping
# ══════════════════════════════════════════════════════════════════════

def get_target_layers(n_layers: int, depth_fractions: list[float]) -> list[int]:
    """Map relative depth fractions to absolute layer indices."""
    seen = set()
    unique = []
    for frac in depth_fractions:
        layer = min(int(round(frac * (n_layers - 1))), n_layers - 1)
        if layer not in seen:
            seen.add(layer)
            unique.append(layer)
    return unique


# ══════════════════════════════════════════════════════════════════════
# RDM extraction — per model (reused from build_binding_lattice.py)
# ══════════════════════════════════════════════════════════════════════

def extract_rdm(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[float, np.ndarray]:
    """Extract cosine-similarity RDM from one model at each depth fraction."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model = MODELS[model_key]
    target_layers = get_target_layers(n_layers, depth_fractions)

    layer_to_frac: dict[int, float] = {}
    for frac in depth_fractions:
        layer = min(int(round(frac * (n_layers - 1))), n_layers - 1)
        layer_to_frac[layer] = frac

    print(f"\n  ─── {model_key} ({model_name}) ───", file=sys.stderr, flush=True)
    print(f"  Layers: {n_layers}, d_model: {d_model}", file=sys.stderr, flush=True)
    print(f"  Target layers ({len(target_layers)}): {target_layers}",
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

    # Find transformer layers
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
    elif hasattr(model, 'transformer') and hasattr(model.transformer, 'h'):
        layers = model.transformer.h
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
    else:
        raise ValueError(f"Cannot find transformer layers for {model_key}")

    hidden_captures: dict[int, list] = {li: [] for li in target_layers}
    hooks = []

    for li in target_layers:
        def make_hook(layer_idx):
            def hook_fn(module, input, output):
                h = output[0] if isinstance(output, tuple) else output
                hidden_captures[layer_idx].append(
                    h[:, -1, :].detach().cpu().float()
                )
            return hook_fn
        hooks.append(layers[li].register_forward_hook(make_hook(li)))

    print(f"  Running {len(probes)} probes...", file=sys.stderr, flush=True)
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 50 == 0:
            print(f"    {i+1}/{len(probes)} probes done...",
                  file=sys.stderr, flush=True)
    dt = time.time() - t0
    print(f"  Done in {dt:.1f}s ({dt/len(probes)*1000:.1f}ms/probe)",
          file=sys.stderr, flush=True)

    for h in hooks:
        h.remove()

    # Build cosine RDMs
    rdms = {}
    for li in target_layers:
        hs = torch.cat(hidden_captures[li], dim=0).numpy()
        norms = np.maximum(np.linalg.norm(hs, axis=1, keepdims=True), 1e-8)
        hs_norm = hs / norms
        rdm = hs_norm @ hs_norm.T
        frac = layer_to_frac.get(li, li / (n_layers - 1))
        rdms[frac] = rdm
        print(f"  L{li} (depth={frac:.0%}): RDM {rdm.shape}, "
              f"mean_sim={rdm.mean():.4f}", file=sys.stderr, flush=True)

    del model, tokenizer
    gc.collect()
    try:
        import torch as _torch
        if _torch.backends.mps.is_available():
            _torch.mps.empty_cache()
        elif _torch.cuda.is_available():
            _torch.cuda.empty_cache()
    except Exception:
        pass

    return rdms


# ══════════════════════════════════════════════════════════════════════
# Consensus — cross-model
# ══════════════════════════════════════════════════════════════════════

def build_consensus(
    all_rdms: dict[str, dict[float, np.ndarray]],
    depth_fractions: list[float],
) -> dict[float, dict]:
    """Build cross-model consensus RDM at each depth."""
    results = {}

    for frac in depth_fractions:
        model_rdms = []
        model_keys = []
        for mk, rdms in all_rdms.items():
            if frac in rdms:
                model_rdms.append(rdms[frac])
                model_keys.append(mk)

        if len(model_rdms) < 2:
            continue

        stacked = np.stack(model_rdms)
        n_models, n_probes, _ = stacked.shape

        consensus_rdm = stacked.mean(axis=0)
        cross_std = stacked.std(axis=0)
        max_std = max(cross_std.max(), 1e-8)
        agreement_mask = 1.0 - (cross_std / max_std)

        triu_idx = np.triu_indices(n_probes, k=1)

        # Model-pair correlations
        model_correlations = {}
        for i in range(n_models):
            for j in range(i + 1, n_models):
                v1 = stacked[i][triu_idx]
                v2 = stacked[j][triu_idx]
                corr = np.corrcoef(v1, v2)[0, 1]
                model_correlations[f"{model_keys[i]}_vs_{model_keys[j]}"] = float(corr)

        results[frac] = {
            "consensus_rdm": consensus_rdm,
            "agreement_mask": agreement_mask,
            "stacked_rdms": stacked,
            "stats": {
                "n_models": n_models,
                "n_probes": n_probes,
                "model_keys": model_keys,
                "mean_agreement": float(agreement_mask[triu_idx].mean()),
                "mean_model_correlation": float(np.mean(list(model_correlations.values()))),
                "model_correlations": model_correlations,
            },
        }

        print(f"  Depth {frac:.0%}: {n_models} models, "
              f"agreement={results[frac]['stats']['mean_agreement']:.4f}, "
              f"model_corr={results[frac]['stats']['mean_model_correlation']:.4f}",
              file=sys.stderr, flush=True)

    return results


# ══════════════════════════════════════════════════════════════════════
# Basin analysis — the core new analysis
# ══════════════════════════════════════════════════════════════════════

def extract_domain_combinator_geometry(
    consensus_rdm: np.ndarray,
    agreement_mask: np.ndarray,
    domain_indices: list[int],
    pure_indices: dict[str, int],
) -> dict:
    """Extract 8×8 combinator cosine geometry as seen from a specific domain.

    For each pair of combinators (i, j), compute the average similarity
    between domain probes and each combinator anchor, then compute
    the cosine between the resulting domain→combinator profiles.

    Also extract the raw domain→combinator similarity vector (the
    "basin fingerprint").
    """
    # Domain → combinator similarity: avg sim of domain probes to each combinator anchor
    fingerprint = {}
    for comb in COMBINATOR_ORDER:
        if comb not in pure_indices:
            continue
        ci = pure_indices[comb]
        sims = [float(consensus_rdm[di, ci]) for di in domain_indices]
        agrs = [float(agreement_mask[di, ci]) for di in domain_indices]
        fingerprint[comb] = {
            "mean_sim": float(np.mean(sims)),
            "std_sim": float(np.std(sims)),
            "mean_agree": float(np.mean(agrs)),
        }

    # 8×8 cosine matrix as seen from this domain's perspective
    # Use the sub-RDM of just the pure combinator anchors
    comb_indices = [pure_indices[c] for c in COMBINATOR_ORDER if c in pure_indices]
    n_comb = len(comb_indices)

    cosine_matrix = np.zeros((n_comb, n_comb))
    for i, ci in enumerate(comb_indices):
        for j, cj in enumerate(comb_indices):
            cosine_matrix[i, j] = float(consensus_rdm[ci, cj])

    # Domain-internal similarity (how similar are probes within this domain?)
    n_domain = len(domain_indices)
    if n_domain > 1:
        internal_sims = []
        for i in range(n_domain):
            for j in range(i + 1, n_domain):
                internal_sims.append(float(consensus_rdm[domain_indices[i], domain_indices[j]]))
        internal_coherence = float(np.mean(internal_sims))
    else:
        internal_coherence = 0.0

    # Domain-internal agreement
    if n_domain > 1:
        internal_agrs = []
        for i in range(n_domain):
            for j in range(i + 1, n_domain):
                internal_agrs.append(float(agreement_mask[domain_indices[i], domain_indices[j]]))
        internal_agreement = float(np.mean(internal_agrs))
    else:
        internal_agreement = 0.0

    # Dominant combinator
    dominant = max(fingerprint.keys(), key=lambda c: fingerprint[c]["mean_sim"])

    return {
        "fingerprint": fingerprint,
        "cosine_matrix": cosine_matrix.tolist(),
        "internal_coherence": internal_coherence,
        "internal_agreement": internal_agreement,
        "dominant_combinator": dominant,
        "dominant_sim": fingerprint[dominant]["mean_sim"],
        "n_probes": n_domain,
    }


def analyze_basins(
    consensus_results: dict[float, dict],
    probes: list[dict],
) -> dict:
    """Full basin analysis across all domains and depths."""
    domain_indices = get_domain_indices(probes)
    pure_indices = get_pure_indices(probes)

    analysis = {
        "domains": SKILL_DOMAINS,
        "combinators": COMBINATOR_ORDER,
        "depth_fractions": sorted(consensus_results.keys()),
        "per_domain": {},       # domain → depth → geometry
        "cross_domain": {},     # depth → domain×domain similarity
        "basin_summary": {},    # depth → summary stats
    }

    for frac in sorted(consensus_results.keys()):
        rdm = consensus_results[frac]["consensus_rdm"]
        agr = consensus_results[frac]["agreement_mask"]

        # ── Per-domain geometry ───────────────────────────────
        domain_geometries = {}
        for domain in SKILL_DOMAINS:
            if domain not in domain_indices:
                continue
            geo = extract_domain_combinator_geometry(
                rdm, agr, domain_indices[domain], pure_indices
            )
            domain_geometries[domain] = geo

            if domain not in analysis["per_domain"]:
                analysis["per_domain"][domain] = {}
            analysis["per_domain"][domain][f"{frac:.2f}"] = geo

        # ── Cross-domain similarity ───────────────────────────
        # Compare fingerprints between domains
        domains_with_data = [d for d in SKILL_DOMAINS if d in domain_geometries]
        n_domains = len(domains_with_data)
        cross_sim = np.zeros((n_domains, n_domains))
        cross_agree = np.zeros((n_domains, n_domains))

        for i, di in enumerate(domains_with_data):
            for j, dj in enumerate(domains_with_data):
                # Average cross-domain probe similarity
                sims = []
                agrs = []
                for pi in domain_indices[di]:
                    for pj in domain_indices[dj]:
                        sims.append(float(rdm[pi, pj]))
                        agrs.append(float(agr[pi, pj]))
                cross_sim[i, j] = float(np.mean(sims))
                cross_agree[i, j] = float(np.mean(agrs))

        # Fingerprint-based similarity (cosine between domain→combinator vectors)
        fingerprint_sim = np.zeros((n_domains, n_domains))
        for i, di in enumerate(domains_with_data):
            vi = np.array([domain_geometries[di]["fingerprint"][c]["mean_sim"]
                          for c in COMBINATOR_ORDER if c in domain_geometries[di]["fingerprint"]])
            for j, dj in enumerate(domains_with_data):
                vj = np.array([domain_geometries[dj]["fingerprint"][c]["mean_sim"]
                              for c in COMBINATOR_ORDER if c in domain_geometries[dj]["fingerprint"]])
                ni, nj = np.linalg.norm(vi), np.linalg.norm(vj)
                if ni > 1e-8 and nj > 1e-8:
                    fingerprint_sim[i, j] = float(np.dot(vi, vj) / (ni * nj))

        analysis["cross_domain"][f"{frac:.2f}"] = {
            "domains": domains_with_data,
            "probe_similarity": cross_sim.tolist(),
            "probe_agreement": cross_agree.tolist(),
            "fingerprint_similarity": fingerprint_sim.tolist(),
        }

        # ── Basin summary ─────────────────────────────────────
        # How many distinct basins at this depth?
        triu = np.triu_indices(n_domains, k=1)
        fp_sims = fingerprint_sim[triu]

        analysis["basin_summary"][f"{frac:.2f}"] = {
            "n_domains": n_domains,
            "mean_cross_domain_sim": float(cross_sim[triu].mean()) if len(triu[0]) > 0 else 0,
            "mean_cross_domain_agree": float(cross_agree[triu].mean()) if len(triu[0]) > 0 else 0,
            "mean_fingerprint_sim": float(fp_sims.mean()) if len(fp_sims) > 0 else 0,
            "min_fingerprint_sim": float(fp_sims.min()) if len(fp_sims) > 0 else 0,
            "max_fingerprint_sim": float(fp_sims.max()) if len(fp_sims) > 0 else 0,
            "domain_internal_coherence": {
                d: domain_geometries[d]["internal_coherence"]
                for d in domains_with_data
            },
            "domain_internal_agreement": {
                d: domain_geometries[d]["internal_agreement"]
                for d in domains_with_data
            },
            "dominant_combinators": {
                d: domain_geometries[d]["dominant_combinator"]
                for d in domains_with_data
            },
        }

    return analysis


# ══════════════════════════════════════════════════════════════════════
# Per-model basin agreement (do individual models agree on basin geometry?)
# ══════════════════════════════════════════════════════════════════════

def analyze_per_model_basins(
    consensus_results: dict[float, dict],
    probes: list[dict],
    target_frac: float = 0.5,
) -> dict:
    """Check if individual models agree on basin geometry at a given depth.

    For each domain, extract the domain→combinator fingerprint from
    EACH model separately, then measure cross-model agreement on
    that fingerprint.
    """
    domain_indices = get_domain_indices(probes)
    pure_indices = get_pure_indices(probes)

    if target_frac not in consensus_results:
        # Find closest
        fracs = sorted(consensus_results.keys())
        target_frac = min(fracs, key=lambda f: abs(f - target_frac))

    result = consensus_results[target_frac]
    stacked = result["stacked_rdms"]  # (n_models, n_probes, n_probes)
    n_models = stacked.shape[0]
    model_keys = result["stats"]["model_keys"]

    per_model_results = {}

    for domain in SKILL_DOMAINS:
        if domain not in domain_indices:
            continue

        d_idx = domain_indices[domain]

        # Extract fingerprint from each model
        model_fingerprints = []
        for mi in range(n_models):
            rdm_i = stacked[mi]
            fp = []
            for comb in COMBINATOR_ORDER:
                if comb not in pure_indices:
                    fp.append(0.0)
                    continue
                ci = pure_indices[comb]
                sims = [float(rdm_i[di, ci]) for di in d_idx]
                fp.append(float(np.mean(sims)))
            model_fingerprints.append(np.array(fp))

        # Cross-model correlation on fingerprints
        correlations = []
        for i in range(n_models):
            for j in range(i + 1, n_models):
                corr = np.corrcoef(model_fingerprints[i], model_fingerprints[j])[0, 1]
                correlations.append(float(corr))

        # Cross-model agreement on dominant combinator
        dominants = [COMBINATOR_ORDER[np.argmax(fp)] for fp in model_fingerprints]
        dominant_agreement = len(set(dominants)) == 1

        per_model_results[domain] = {
            "model_fingerprints": {
                mk: {c: float(fp[ci]) for ci, c in enumerate(COMBINATOR_ORDER)}
                for mk, fp in zip(model_keys, model_fingerprints)
            },
            "cross_model_correlation": float(np.mean(correlations)) if correlations else 0.0,
            "per_pair_correlation": correlations,
            "dominant_per_model": dict(zip(model_keys, dominants)),
            "dominant_unanimous": dominant_agreement,
            "consensus_dominant": max(
                COMBINATOR_ORDER,
                key=lambda c: float(np.mean([fp[COMBINATOR_ORDER.index(c)]
                                             for fp in model_fingerprints]))
            ),
        }

    return {
        "depth_fraction": target_frac,
        "n_models": n_models,
        "model_keys": model_keys,
        "domains": per_model_results,
    }


# ══════════════════════════════════════════════════════════════════════
# Pretty printing
# ══════════════════════════════════════════════════════════════════════

def print_basin_analysis(analysis: dict, per_model: dict) -> None:
    """Print human-readable basin analysis."""
    print("\n" + "=" * 90, file=sys.stderr, flush=True)
    print("  CRYSTAL BASIN ANALYSIS — Multi-Domain Skill Attractors", file=sys.stderr, flush=True)
    print("=" * 90, file=sys.stderr, flush=True)

    # ── Domain fingerprints at mid-depth ──────────────────────
    mid_key = None
    for fk in analysis["depth_fractions"]:
        if abs(fk - 0.5) < 0.1:
            mid_key = f"{fk:.2f}"
            break
    if not mid_key:
        mid_key = f"{analysis['depth_fractions'][len(analysis['depth_fractions'])//2]:.2f}"

    print(f"\n  Domain → Combinator Fingerprints (depth {mid_key}):", file=sys.stderr, flush=True)
    print(f"  {'domain':>12s}", end='', file=sys.stderr)
    for c in COMBINATOR_ORDER:
        print(f"  {c:>6s}", end='', file=sys.stderr)
    print(f"  {'dom':>5s}  {'coher':>6s}  {'agree':>6s}", file=sys.stderr, flush=True)
    print("  " + "-" * 100, file=sys.stderr, flush=True)

    for domain in SKILL_DOMAINS:
        if domain not in analysis["per_domain"]:
            continue
        geo = analysis["per_domain"][domain].get(mid_key)
        if not geo:
            continue
        print(f"  {domain:>12s}", end='', file=sys.stderr)
        for c in COMBINATOR_ORDER:
            sim = geo["fingerprint"].get(c, {}).get("mean_sim", 0)
            print(f"  {sim:+.3f}", end='', file=sys.stderr)
        print(f"  {geo['dominant_combinator']:>5s}", end='', file=sys.stderr)
        print(f"  {geo['internal_coherence']:+.3f}", end='', file=sys.stderr)
        print(f"  {geo['internal_agreement']:.3f}", file=sys.stderr, flush=True)

    # ── Cross-domain fingerprint similarity ───────────────────
    cross = analysis["cross_domain"].get(mid_key)
    if cross:
        print(f"\n  Cross-Domain Fingerprint Similarity (depth {mid_key}):", file=sys.stderr, flush=True)
        domains = cross["domains"]
        fp_sim = np.array(cross["fingerprint_similarity"])

        print(f"  {'':>12s}", end='', file=sys.stderr)
        for d in domains:
            print(f"  {d[:6]:>6s}", end='', file=sys.stderr)
        print(file=sys.stderr, flush=True)

        for i, di in enumerate(domains):
            print(f"  {di:>12s}", end='', file=sys.stderr)
            for j, dj in enumerate(domains):
                if i == j:
                    print(f"  {'--':>6s}", end='', file=sys.stderr)
                else:
                    print(f"  {fp_sim[i,j]:+.3f}", end='', file=sys.stderr)
            print(file=sys.stderr, flush=True)

    # ── Basin summary ─────────────────────────────────────────
    print(f"\n  Basin Summary Across Depths:", file=sys.stderr, flush=True)
    print(f"  {'depth':>6s}  {'mean_fp_sim':>11s}  {'min_fp_sim':>10s}  "
          f"{'max_fp_sim':>10s}  {'mean_agree':>10s}",
          file=sys.stderr, flush=True)
    print("  " + "-" * 56, file=sys.stderr, flush=True)

    for frac_key in sorted(analysis["basin_summary"].keys()):
        bs = analysis["basin_summary"][frac_key]
        print(f"  {frac_key:>6s}  {bs['mean_fingerprint_sim']:>11.4f}  "
              f"{bs['min_fingerprint_sim']:>10.4f}  "
              f"{bs['max_fingerprint_sim']:>10.4f}  "
              f"{bs['mean_cross_domain_agree']:>10.4f}",
              file=sys.stderr, flush=True)

    # ── Per-model agreement on basin geometry ─────────────────
    print(f"\n  Per-Model Basin Agreement (depth {per_model['depth_fraction']:.0%}):",
          file=sys.stderr, flush=True)
    print(f"  {'domain':>12s}  {'corr':>6s}  {'unanimous':>9s}  "
          + "  ".join(f"{mk[:8]:>8s}" for mk in per_model["model_keys"]),
          file=sys.stderr, flush=True)
    print("  " + "-" * (35 + 10 * len(per_model["model_keys"])),
          file=sys.stderr, flush=True)

    for domain in SKILL_DOMAINS:
        if domain not in per_model["domains"]:
            continue
        pm = per_model["domains"][domain]
        print(f"  {domain:>12s}  {pm['cross_model_correlation']:+.3f}  "
              f"{'  YES' if pm['dominant_unanimous'] else '   NO':>9s}  ",
              end='', file=sys.stderr)
        for mk in per_model["model_keys"]:
            dom = pm["dominant_per_model"].get(mk, "?")
            print(f"  {dom:>8s}", end='', file=sys.stderr)
        print(file=sys.stderr, flush=True)

    # ── Dominant combinators across depths ─────────────────────
    print(f"\n  Dominant Combinator per Domain × Depth:", file=sys.stderr, flush=True)
    print(f"  {'domain':>12s}", end='', file=sys.stderr)
    for fk in sorted(analysis["basin_summary"].keys()):
        print(f"  {fk:>6s}", end='', file=sys.stderr)
    print(file=sys.stderr, flush=True)

    for domain in SKILL_DOMAINS:
        print(f"  {domain:>12s}", end='', file=sys.stderr)
        for fk in sorted(analysis["basin_summary"].keys()):
            dom = analysis["basin_summary"][fk]["dominant_combinators"].get(domain, "?")
            print(f"  {dom:>6s}", end='', file=sys.stderr)
        print(file=sys.stderr, flush=True)

    print("\n" + "=" * 90, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════════════

def save_results(
    consensus_results: dict[float, dict],
    analysis: dict,
    per_model: dict,
    probes: list[dict],
    all_rdms: dict[str, dict[float, np.ndarray]],
    output_dir: Path,
    model_keys: list[str],
) -> None:
    """Save basin lattice results."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── NPZ: consensus RDMs ──────────────────────────────────
    npz_data = {}
    for frac, result in consensus_results.items():
        key = f"depth_{frac:.2f}"
        npz_data[f"{key}_consensus_rdm"] = result["consensus_rdm"].astype(np.float32)
        npz_data[f"{key}_agreement_mask"] = result["agreement_mask"].astype(np.float32)

    npz_path = output_dir / "basin_lattice.npz"
    np.savez_compressed(str(npz_path), **npz_data)
    print(f"\n  💾 NPZ: {npz_path} ({npz_path.stat().st_size / 1024:.1f} KB)",
          file=sys.stderr, flush=True)

    # ── Per-model RDMs ────────────────────────────────────────
    for model_key, rdms in all_rdms.items():
        model_npz = {}
        for frac, rdm in rdms.items():
            model_npz[f"depth_{frac:.2f}_rdm"] = rdm.astype(np.float32)
        model_path = output_dir / f"rdm_{model_key}.npz"
        np.savez_compressed(str(model_path), **model_npz)
        print(f"  💾 Per-model: {model_path} ({model_path.stat().st_size / 1024:.1f} KB)",
              file=sys.stderr, flush=True)

    # ── JSON: analysis ────────────────────────────────────────
    json_data = {
        "description": "Basin lattice — multi-domain skill attractor exploration",
        "hypothesis": "Each skill domain has a distinct but universal crystal geometry",
        "n_probes": len(probes),
        "n_models": len(model_keys),
        "model_keys": model_keys,
        "models": {k: MODELS[k][0] for k in model_keys if k in MODELS},
        "depth_fractions": sorted(consensus_results.keys()),
        "probes": [{k: v for k, v in p.items() if k != "note"} for p in probes],
        "basin_analysis": analysis,
        "per_model_agreement": per_model,
        "depth_stats": {
            f"{frac:.2f}": consensus_results[frac]["stats"]
            for frac in sorted(consensus_results.keys())
        },
    }

    json_path = output_dir / "basin_lattice.json"
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"  💾 JSON: {json_path}", file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Build basin lattice — multi-domain skill attractor exploration"
    )
    parser.add_argument("--models", nargs="+", default=None,
                        choices=list(MODELS.keys()),
                        help=f"Models to use (default: {DEFAULT_MODELS})")
    parser.add_argument("--probes", type=str, default=None,
                        help="Path to probe JSON")
    parser.add_argument("--output-dir", type=str, default="lattice/basins-v1",
                        help="Output directory")
    parser.add_argument("--device", type=str, default="mps",
                        help="Device for inference")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: 2 models, 3 depths")

    args = parser.parse_args()

    if args.quick:
        model_keys = args.models or QUICK_MODELS
        depth_fractions = QUICK_DEPTH_FRACTIONS
    else:
        model_keys = args.models or DEFAULT_MODELS
        depth_fractions = BASIN_DEPTH_FRACTIONS

    print("=" * 72, file=sys.stderr, flush=True)
    print("  Basin Lattice — Multi-Domain Crystal Basin Exploration",
          file=sys.stderr, flush=True)
    print(f"  Models: {model_keys}", file=sys.stderr, flush=True)
    print(f"  Depths: {[f'{d:.0%}' for d in depth_fractions]}",
          file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t_start = time.time()

    # ── Load probes ───────────────────────────────────────────
    print("\n1. Loading probes...", file=sys.stderr, flush=True)
    probes = load_probes(args.probes)

    # ── Extract RDMs ──────────────────────────────────────────
    print("\n2. Extracting per-model RDMs...", file=sys.stderr, flush=True)
    all_rdms: dict[str, dict[float, np.ndarray]] = {}
    for model_key in model_keys:
        if model_key not in MODELS:
            print(f"  WARNING: Unknown model {model_key}, skipping",
                  file=sys.stderr, flush=True)
            continue
        rdms = extract_rdm(model_key, probes, depth_fractions, args.device)
        all_rdms[model_key] = rdms

    if len(all_rdms) < 2:
        print("ERROR: Need at least 2 models for consensus.",
              file=sys.stderr, flush=True)
        sys.exit(1)

    # ── Build consensus ───────────────────────────────────────
    print("\n3. Building cross-model consensus...", file=sys.stderr, flush=True)
    consensus_results = build_consensus(all_rdms, depth_fractions)

    # ── Basin analysis ────────────────────────────────────────
    print("\n4. Analyzing basins...", file=sys.stderr, flush=True)
    analysis = analyze_basins(consensus_results, probes)

    # ── Per-model agreement ───────────────────────────────────
    print("\n5. Checking per-model basin agreement...", file=sys.stderr, flush=True)
    per_model = analyze_per_model_basins(consensus_results, probes)

    # ── Save ──────────────────────────────────────────────────
    print("\n6. Saving results...", file=sys.stderr, flush=True)
    output_dir = Path(args.output_dir)
    save_results(
        consensus_results, analysis, per_model,
        probes, all_rdms, output_dir, list(all_rdms.keys()),
    )

    # ── Print analysis ────────────────────────────────────────
    print_basin_analysis(analysis, per_model)

    elapsed = time.time() - t_start
    print(f"\n  Total elapsed: {elapsed:.0f}s", file=sys.stderr, flush=True)
    print(f"  Output: {output_dir}/", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
