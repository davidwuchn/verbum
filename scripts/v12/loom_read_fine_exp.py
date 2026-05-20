"""Loom Read Fine Experiment — Per-domain subcrystal resolution at all depths.

Session 124, experiment 3. The grouped analysis (compose/retrieve/route/neutral)
found the loom breathes with depth. But the groups might hide finer structure.
This experiment uses all 10 individual domains to check:

1. Do domains WITHIN our groups actually agree, or are there finer subcrystals?
   - Is "lambda" different from "pure" within compose?
   - Is "retrieval" different from "analogy" within retrieve?
   - Is "coding" different from "reasoning" within route?
2. At d=0.3 (holographic max), are there more than 3 subcrystals?
3. At d=0.7 (transition max), what's the fine structure?

Uses the same CCA angle band decomposition but measures pairwise sign
overlap between all 10 domains (45 pairs) at each depth × band.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/loom_read_fine_exp.py

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

MODEL_NAME = "EleutherAI/pythia-2.8b-deduped"
N_LAYERS = 32
D_MODEL = 2560
SVD_K = 256

DEPTHS = [0.1, 0.3, 0.5, 0.7, 0.9]

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "loom-read-fine"

ANGLE_BANDS = [
    ("shared",      0, 35),
    ("mid_low",    35, 50),
    ("attn_clust", 50, 58),
    ("transition", 58, 64),
    ("holographic", 64, 72),
    ("peripheral", 72, 82),
    ("private",    82, 91),
]

# All 10 individual domains
ALL_DOMAINS = [
    "pure", "lambda", "arithmetic", "coding", "tool",
    "retrieval", "analogy", "reasoning", "narrative", "instruction",
]

COMBINATOR_ORDER = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def load_probes():
    path = Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json"
    with open(path) as f:
        return json.load(f)


def get_domain_indices(probes):
    """Get probe indices for each domain."""
    domains = {d: [] for d in ALL_DOMAINS}
    for i, p in enumerate(probes):
        d = p["axis"].split("/")[0]
        if d in domains:
            domains[d].append(i)
    return domains


def get_pure_indices(probes):
    pure_map = {}
    for i, p in enumerate(probes):
        if p["axis"].startswith("pure/"):
            comb = p["axis"].split("/")[1]
            pure_map[comb] = i
    return [pure_map[c] for c in COMBINATOR_ORDER if c in pure_map]


# ══════════════════════════════════════════════════════════════════════
# Model extraction (same as depth experiment)
# ══════════════════════════════════════════════════════════════════════

def extract_all(probes, depths):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    target_layers = {}
    for d in depths:
        target_layers[d] = min(int(round(d * (N_LAYERS - 1))), N_LAYERS - 1)

    log(f"  Loading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float32, device_map="mps",
    )
    model.eval()

    weights = {}
    for d, layer_idx in target_layers.items():
        layer = model.gpt_neox.layers[layer_idx]
        qkv = layer.attention.query_key_value.weight.detach().cpu().float().numpy()
        W_q = qkv[:D_MODEL, :]
        W_up = layer.mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()
        weights[d] = {"W_q": W_q, "W_up": W_up, "layer_idx": layer_idx}

    captures = {d: {"h": []} for d in depths}
    hooks = []

    for d, layer_idx in target_layers.items():
        def make_hook(depth):
            def hook_fn(module, input, output):
                inp = input[0] if isinstance(input, tuple) else input
                captures[depth]["h"].append(inp[:, -1, :].detach().cpu().float())
            return hook_fn
        h = model.gpt_neox.layers[layer_idx].register_forward_hook(make_hook(d))
        hooks.append(h)

    log(f"  Running {len(probes)} probes...")
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to("mps")
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 30 == 0:
            log(f"    {i + 1}/{len(probes)}")

    for h in hooks:
        h.remove()

    activations = {}
    for d in depths:
        activations[d] = torch.cat(captures[d]["h"], dim=0).numpy()

    del model, tokenizer
    gc.collect()
    torch.mps.empty_cache()

    return weights, activations


# ══════════════════════════════════════════════════════════════════════
# CCA + sign overlap (same core as before)
# ══════════════════════════════════════════════════════════════════════

def compute_cca(W_q, W_up, k):
    _, _, Vt_q = np.linalg.svd(W_q, full_matrices=False)
    _, _, Vt_up = np.linalg.svd(W_up, full_matrices=False)
    A = Vt_q[:k, :].T
    B = Vt_up[:k, :].T
    Qa, _ = np.linalg.qr(A)
    Qb, _ = np.linalg.qr(B)
    U_cca, S_cca, Vt_cca = np.linalg.svd(Qa.T @ Qb, full_matrices=False)
    angles = np.degrees(np.arccos(np.clip(S_cca, 0, 1)))
    dirs_q = Qa @ U_cca
    dirs_up = Qb @ Vt_cca.T
    dirs = dirs_q + dirs_up
    norms = np.linalg.norm(dirs, axis=0, keepdims=True)
    dirs = dirs / np.maximum(norms, 1e-8)
    return angles, dirs


def bin_directions(angles, dirs):
    bands = {}
    for name, lo, hi in ANGLE_BANDS:
        mask = (angles >= lo) & (angles < hi)
        bands[name] = {"dirs": dirs[:, mask], "n": int(mask.sum())}
    return bands


def magnitude_profile(activations, indices):
    if len(indices) == 0:
        return np.zeros(activations.shape[1])
    return np.sqrt(np.mean(activations[indices] ** 2, axis=0))


def sign_overlap_matrix(W_q, mag_profiles, bands, domain_names, top_k_frac=0.2):
    """Compute pairwise sign overlap for ALL domain pairs at each band.
    
    Returns: {band_name: {n_dirs, overlap_matrix: 10×10 as nested dict}}
    """
    sign_W = np.sign(W_q)
    results = {}

    for band_name, band_data in bands.items():
        if band_data["n"] < 2:
            results[band_name] = {"n_dirs": band_data["n"], "matrix": {}}
            continue

        band_dirs = band_data["dirs"]

        # Extract sign pattern for each domain
        domain_signs = {}
        for dname in domain_names:
            mag = mag_profiles[dname]
            if np.sum(mag) < 1e-10:
                domain_signs[dname] = None
                continue
            mag_in_band = np.abs(band_dirs.T @ mag)
            n_top = max(1, int(top_k_frac * len(mag_in_band)))
            top_idx = np.argsort(mag_in_band)[-n_top:]
            top_dirs = band_dirs[:, top_idx]
            sign_projected = sign_W @ top_dirs
            domain_signs[dname] = np.sign(sign_projected).flatten()

        # Pairwise overlap
        matrix = {}
        for i, d1 in enumerate(domain_names):
            row = {}
            for j, d2 in enumerate(domain_names):
                if domain_signs[d1] is None or domain_signs[d2] is None:
                    row[d2] = None
                    continue
                s1 = domain_signs[d1]
                s2 = domain_signs[d2]
                valid = (s1 != 0) & (s2 != 0)
                if valid.sum() == 0:
                    row[d2] = None
                else:
                    row[d2] = float(np.mean(s1[valid] == s2[valid]))
            matrix[d1] = row

        results[band_name] = {"n_dirs": band_data["n"], "matrix": matrix}

    return results


def cluster_domains(matrix, domain_names, threshold=0.55):
    """Given an overlap matrix, find clusters of domains that agree.
    
    Returns list of clusters (each a list of domain names).
    """
    n = len(domain_names)
    # Build adjacency
    agree = np.ones((n, n), dtype=bool)
    for i, d1 in enumerate(domain_names):
        for j, d2 in enumerate(domain_names):
            if j <= i:
                continue
            ov = matrix.get(d1, {}).get(d2)
            if ov is None or ov < threshold:
                agree[i, j] = False
                agree[j, i] = False

    # Connected components
    visited = set()
    clusters = []
    for i in range(n):
        if i in visited:
            continue
        cluster = {i}
        queue = [i]
        while queue:
            curr = queue.pop(0)
            for j in range(n):
                if j not in visited and j not in cluster and agree[curr, j]:
                    cluster.add(j)
                    queue.append(j)
        visited.update(cluster)
        clusters.append(sorted([domain_names[k] for k in cluster]))

    return clusters


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    t0 = time.time()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log("Loading probes...")
    probes = load_probes()
    domain_indices = get_domain_indices(probes)
    pure_indices = get_pure_indices(probes)

    # Only use domains that have probes
    active_domains = [d for d in ALL_DOMAINS if len(domain_indices[d]) > 0]
    log(f"  {len(probes)} probes, {len(active_domains)} domains:")
    for d in active_domains:
        log(f"    {d}: {len(domain_indices[d])} probes")

    log("\nExtracting from model...")
    weights, activations = extract_all(probes, DEPTHS)

    all_results = {}

    for depth in DEPTHS:
        log(f"\n{'='*60}")
        log(f"  DEPTH {depth:.1f} (layer {weights[depth]['layer_idx']})")
        log(f"{'='*60}")

        W_q = weights[depth]["W_q"]
        W_up = weights[depth]["W_up"]
        h = activations[depth]

        # CCA
        angles, dirs = compute_cca(W_q, W_up, SVD_K)
        bands = bin_directions(angles, dirs)

        # Magnitude profiles per domain
        mag_profiles = {}
        for d in active_domains:
            mag_profiles[d] = magnitude_profile(h, domain_indices[d])

        # Magnitude correlation matrix (all pairs)
        mag_corr = {}
        for i, d1 in enumerate(active_domains):
            for j, d2 in enumerate(active_domains):
                if j <= i:
                    continue
                m1, m2 = mag_profiles[d1], mag_profiles[d2]
                if np.std(m1) < 1e-10 or np.std(m2) < 1e-10:
                    corr = 0.0
                else:
                    corr = float(np.corrcoef(m1, m2)[0, 1])
                mag_corr[f"{d1}_vs_{d2}"] = corr

        # Sign overlap matrix at each band
        overlap_results = sign_overlap_matrix(
            W_q, mag_profiles, bands, active_domains)

        # Cluster at each band
        cluster_results = {}
        for band_name, data in overlap_results.items():
            if data["n_dirs"] < 2:
                cluster_results[band_name] = {"count": 0, "clusters": []}
                continue
            clusters = cluster_domains(data["matrix"], active_domains)
            cluster_results[band_name] = {
                "count": len(clusters),
                "clusters": clusters,
            }

        # Print summary
        log(f"\n  Clusters by band:")
        for band_name, data in cluster_results.items():
            if data["count"] > 0:
                cl_str = " | ".join(["+".join(c) for c in data["clusters"]])
                log(f"    {band_name:12s}: {data['count']} clusters  [{cl_str}]")

        # Print the overlap matrix at holographic band (most interesting)
        holo = overlap_results.get("holographic", {})
        if holo.get("n_dirs", 0) >= 2:
            log(f"\n  Holographic band overlap matrix:")
            header = f"  {'':12s}"
            for d in active_domains:
                header += f" {d[:6]:>6s}"
            log(header)
            for d1 in active_domains:
                row = f"  {d1:12s}"
                for d2 in active_domains:
                    ov = holo["matrix"].get(d1, {}).get(d2)
                    if ov is None:
                        row += "      -"
                    elif d1 == d2:
                        row += "      ."
                    else:
                        marker = "★" if ov < 0.55 else " "
                        row += f" {ov:.3f}{marker}"
                log(row)

        # Same for transition band
        trans = overlap_results.get("transition", {})
        if trans.get("n_dirs", 0) >= 2:
            log(f"\n  Transition band overlap matrix:")
            header = f"  {'':12s}"
            for d in active_domains:
                header += f" {d[:6]:>6s}"
            log(header)
            for d1 in active_domains:
                row = f"  {d1:12s}"
                for d2 in active_domains:
                    ov = trans["matrix"].get(d1, {}).get(d2)
                    if ov is None:
                        row += "      -"
                    elif d1 == d2:
                        row += "      ."
                    else:
                        marker = "★" if ov < 0.55 else " "
                        row += f" {ov:.3f}{marker}"
                log(row)

        # Key magnitude correlations
        log(f"\n  Key magnitude correlations:")
        # Within groups
        within = [
            ("pure", "lambda"),
            ("retrieval", "analogy"),
            ("coding", "reasoning"),
            ("coding", "instruction"),
            ("arithmetic", "narrative"),
        ]
        for d1, d2 in within:
            key = f"{d1}_vs_{d2}"
            corr = mag_corr.get(key, mag_corr.get(f"{d2}_vs_{d1}", None))
            if corr is not None:
                log(f"    {d1} ↔ {d2}: {corr:.4f}")

        # Cross groups
        cross = [
            ("pure", "retrieval"),
            ("lambda", "coding"),
            ("retrieval", "coding"),
        ]
        log(f"  Cross-group:")
        for d1, d2 in cross:
            key = f"{d1}_vs_{d2}"
            corr = mag_corr.get(key, mag_corr.get(f"{d2}_vs_{d1}", None))
            if corr is not None:
                log(f"    {d1} ↔ {d2}: {corr:.4f}")

        all_results[str(depth)] = {
            "layer_idx": weights[depth]["layer_idx"],
            "angle_distribution": {bn: bands[bn]["n"] for bn in bands},
            "magnitude_correlations": mag_corr,
            "overlap_by_band": {
                bn: {
                    "n_dirs": data["n_dirs"],
                    "matrix": data["matrix"],
                }
                for bn, data in overlap_results.items()
            },
            "clusters_by_band": cluster_results,
        }

    # ══════════════════════════════════════════════════════════════════
    # Synthesis
    # ══════════════════════════════════════════════════════════════════
    log(f"\n{'='*60}")
    log("SYNTHESIS: Fine-grained subcrystal structure")
    log(f"{'='*60}")

    # Cluster count evolution
    log(f"\n  Cluster count by depth × band:")
    header = f"  {'band':12s}"
    for d in DEPTHS:
        header += f"  d={d:.1f}"
    log(header)
    log("  " + "-" * (12 + len(DEPTHS) * 7))

    for bn, _, _ in ANGLE_BANDS:
        row = f"  {bn:12s}"
        for d in DEPTHS:
            data = all_results[str(d)]["clusters_by_band"].get(bn, {})
            count = data.get("count", 0)
            row += f"  {count:>4d}" if count > 0 else "     -"
        log(row)

    # Maximum cluster count across all (depth × band)
    max_clusters = 0
    max_where = ""
    for d in DEPTHS:
        for bn, _, _ in ANGLE_BANDS:
            data = all_results[str(d)]["clusters_by_band"].get(bn, {})
            count = data.get("count", 0)
            if count > max_clusters:
                max_clusters = count
                max_where = f"d={d:.1f}, {bn}"
                max_detail = data.get("clusters", [])

    log(f"\n  Maximum subcrystal count: {max_clusters} at {max_where}")
    if max_detail:
        for i, c in enumerate(max_detail):
            log(f"    Crystal {i+1}: {', '.join(c)}")

    # Check within-group agreement
    log(f"\n  Within-group agreement (holographic band, d=0.5):")
    holo_d05 = all_results.get("0.5", {}).get("overlap_by_band", {}).get("holographic", {})
    if holo_d05.get("n_dirs", 0) >= 2:
        mat = holo_d05.get("matrix", {})
        within_pairs = [
            ("pure", "lambda", "compose"),
            ("retrieval", "analogy", "retrieve"),
            ("coding", "reasoning", "route"),
            ("coding", "instruction", "route"),
            ("reasoning", "instruction", "route"),
            ("arithmetic", "narrative", "neutral"),
            ("arithmetic", "tool", "neutral"),
            ("narrative", "tool", "neutral"),
        ]
        for d1, d2, group in within_pairs:
            ov = mat.get(d1, {}).get(d2)
            if ov is not None:
                marker = "★ SPLIT" if ov < 0.55 else "  agree"
                log(f"    {d1:12s} ↔ {d2:12s} ({group:8s}): {ov:.4f}  {marker}")

    # Save
    save_data = {
        "model": MODEL_NAME,
        "depths": DEPTHS,
        "domains": active_domains,
        "n_probes": len(probes),
        "domain_sizes": {d: len(domain_indices[d]) for d in active_domains},
        "per_depth": all_results,
        "elapsed_seconds": time.time() - t0,
    }

    results_path = RESULTS_DIR / "results.json"
    with open(results_path, "w") as f:
        json.dump(save_data, f, indent=2)

    log(f"\n✓ Results saved to {results_path}")
    log(f"  Total time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
