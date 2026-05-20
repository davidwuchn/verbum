"""Loom Breathing Experiment — Fine-resolution depth curve of subcrystal count.

Session 124, experiment 4. We know the loom breathes: fragments early,
unifies mid, re-fragments late. Now map this precisely to V13's 7-pass
hourglass by measuring at every 3rd layer of Pythia-2.8b (11 depths).

The V13 hourglass:
  L0↑ (fine)    → L1↑ (local)   → L2↑ (phrase)  → apex
  L0↓ (fine)    ← L1↓ (local)   ← L2↓ (phrase)  ←

Question: does the breathing curve match this structure?
- Ascending: fragmentation → unification
- Apex: maximum unity
- Descending: re-fragmentation → partial convergence

Uses 4 probe groups (compose/retrieve/route/neutral) for speed.
Measures subcrystal count at each depth × 3 key angle bands:
  - holographic (64-72°) — where the weave crossing lives
  - transition (58-64°) — where WHNF polarity crosses zero
  - mid_low (35-50°) — where peak fragmentation was found

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/loom_breathing_exp.py

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

# Every 3rd layer + first and last = 11 depths
TARGET_LAYERS = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31]
DEPTHS = [l / (N_LAYERS - 1) for l in TARGET_LAYERS]

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "loom-breathing"

ANGLE_BANDS = [
    ("shared",      0, 35),
    ("mid_low",    35, 50),
    ("attn_clust", 50, 58),
    ("transition", 58, 64),
    ("holographic", 64, 72),
    ("peripheral", 72, 82),
    ("private",    82, 91),
]

DOMAIN_GROUPS = {
    "compose":  ["pure", "lambda"],
    "retrieve": ["retrieval", "analogy"],
    "route":    ["coding", "reasoning", "instruction"],
    "neutral":  ["arithmetic", "narrative", "tool"],
}

COMBINATOR_ORDER = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def load_probes():
    path = Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json"
    with open(path) as f:
        return json.load(f)


def partition_probes(probes):
    groups = {name: [] for name in DOMAIN_GROUPS}
    for i, p in enumerate(probes):
        domain = p["axis"].split("/")[0]
        for group_name, domains in DOMAIN_GROUPS.items():
            if domain in domains:
                groups[group_name].append(i)
                break
    return groups


def get_pure_indices(probes):
    pure_map = {}
    for i, p in enumerate(probes):
        if p["axis"].startswith("pure/"):
            comb = p["axis"].split("/")[1]
            pure_map[comb] = i
    return [pure_map[c] for c in COMBINATOR_ORDER if c in pure_map]


# ══════════════════════════════════════════════════════════════════════

def extract_all(probes):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    log(f"  Loading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float32, device_map="mps",
    )
    model.eval()

    # Extract weights at all target layers
    weights = {}
    for layer_idx in TARGET_LAYERS:
        layer = model.gpt_neox.layers[layer_idx]
        qkv = layer.attention.query_key_value.weight.detach().cpu().float().numpy()
        W_q = qkv[:D_MODEL, :]
        W_up = layer.mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()
        weights[layer_idx] = {"W_q": W_q, "W_up": W_up}

    # Hook hidden states at all target layers
    captures = {l: [] for l in TARGET_LAYERS}
    hooks = []

    for layer_idx in TARGET_LAYERS:
        def make_hook(li):
            def hook_fn(module, input, output):
                inp = input[0] if isinstance(input, tuple) else input
                captures[li].append(inp[:, -1, :].detach().cpu().float())
            return hook_fn
        h = model.gpt_neox.layers[layer_idx].register_forward_hook(make_hook(layer_idx))
        hooks.append(h)

    log(f"  Running {len(probes)} probes through {len(TARGET_LAYERS)} layers...")
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to("mps")
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 30 == 0:
            log(f"    {i + 1}/{len(probes)}")

    for h in hooks:
        h.remove()

    activations = {}
    for l in TARGET_LAYERS:
        activations[l] = torch.cat(captures[l], dim=0).numpy()

    del model, tokenizer
    gc.collect()
    torch.mps.empty_cache()

    return weights, activations


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


def measure_sign_overlap(W_q, mag_profiles, bands, group_names, top_k_frac=0.2):
    sign_W = np.sign(W_q)
    results = {}

    for band_name, band_data in bands.items():
        if band_data["n"] < 2:
            results[band_name] = {"n_dirs": band_data["n"], "overlaps": {}}
            continue

        band_dirs = band_data["dirs"]
        group_signs = {}

        for gname, mag in mag_profiles.items():
            mag_in_band = np.abs(band_dirs.T @ mag)
            n_top = max(1, int(top_k_frac * len(mag_in_band)))
            top_idx = np.argsort(mag_in_band)[-n_top:]
            top_dirs = band_dirs[:, top_idx]
            sign_projected = sign_W @ top_dirs
            group_signs[gname] = np.sign(sign_projected).flatten()

        overlaps = {}
        for i, g1 in enumerate(group_names):
            for j, g2 in enumerate(group_names):
                if j <= i:
                    continue
                s1, s2 = group_signs[g1], group_signs[g2]
                valid = (s1 != 0) & (s2 != 0)
                if valid.sum() == 0:
                    overlaps[f"{g1}_vs_{g2}"] = None
                else:
                    overlaps[f"{g1}_vs_{g2}"] = float(np.mean(s1[valid] == s2[valid]))

        results[band_name] = {"n_dirs": band_data["n"], "overlaps": overlaps}

    return results


def count_subcrystals(overlaps, group_names, threshold=0.55):
    """Count independent subcrystals from pairwise overlaps."""
    n = len(group_names)
    agree = np.ones((n, n), dtype=bool)
    for pair_key, ov in overlaps.items():
        if ov is None or ov < threshold:
            parts = pair_key.split("_vs_")
            i = group_names.index(parts[0])
            j = group_names.index(parts[1])
            agree[i, j] = False
            agree[j, i] = False

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
        clusters.append([group_names[k] for k in sorted(cluster)])

    return len(clusters), clusters


def cosine_matrix(X, indices):
    vecs = X[indices]
    norms = np.maximum(np.linalg.norm(vecs, axis=1, keepdims=True), 1e-8)
    vecs_n = vecs / norms
    return vecs_n @ vecs_n.T


def rdm_correlation(A, B):
    n = A.shape[0]
    idx = np.triu_indices(n, k=1)
    a = A[idx] - A[idx].mean()
    b = B[idx] - B[idx].mean()
    denom = np.sqrt(np.sum(a**2)) * np.sqrt(np.sum(b**2))
    return float(np.sum(a * b) / denom) if denom > 1e-10 else 0.0


# ══════════════════════════════════════════════════════════════════════

def main():
    t0 = time.time()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    probes = load_probes()
    probe_groups = partition_probes(probes)
    pure_indices = get_pure_indices(probes)
    group_names = list(probe_groups.keys())

    log(f"Loaded {len(probes)} probes, {len(group_names)} groups")
    log(f"Target layers: {TARGET_LAYERS}")
    log(f"Depths: {[f'{d:.3f}' for d in DEPTHS]}")

    weights, activations = extract_all(probes)

    # ── Analyze each depth ──
    depth_curve = []

    for layer_idx, depth in zip(TARGET_LAYERS, DEPTHS):
        log(f"\n  Layer {layer_idx:2d} (d={depth:.3f})")

        W_q = weights[layer_idx]["W_q"]
        W_up = weights[layer_idx]["W_up"]
        h = activations[layer_idx]

        angles, dirs = compute_cca(W_q, W_up, SVD_K)
        bands = bin_directions(angles, dirs)

        # Magnitude profiles
        mag_profiles = {}
        for g, idx in probe_groups.items():
            mag_profiles[g] = magnitude_profile(h, idx)

        # Magnitude correlations
        mag_corrs = {}
        for i, g1 in enumerate(group_names):
            for j, g2 in enumerate(group_names):
                if j <= i:
                    continue
                corr = float(np.corrcoef(mag_profiles[g1], mag_profiles[g2])[0, 1])
                mag_corrs[f"{g1}_vs_{g2}"] = corr

        # Sign overlap + subcrystal count at each band
        sign_results = measure_sign_overlap(W_q, mag_profiles, bands, group_names)

        band_counts = {}
        band_clusters = {}
        for band_name, data in sign_results.items():
            if data["n_dirs"] < 2:
                band_counts[band_name] = 0
                band_clusters[band_name] = []
                continue
            count, clusters = count_subcrystals(data["overlaps"], group_names)
            band_counts[band_name] = count
            band_clusters[band_name] = clusters

        # Crystal agreement at key bands
        ref_crystal = cosine_matrix(h, pure_indices)
        band_agreement = {}
        band_whnf = {}
        for band_name, band_data in bands.items():
            if band_data["n"] < 2:
                band_agreement[band_name] = None
                band_whnf[band_name] = None
                continue
            projected = h @ band_data["dirs"]
            cos_mat = cosine_matrix(projected, pure_indices)
            band_agreement[band_name] = rdm_correlation(cos_mat, ref_crystal)
            whnf_idx = COMBINATOR_ORDER.index("WHNF")
            n_comb = len(pure_indices)
            whnf_cos = [cos_mat[whnf_idx, j] for j in range(n_comb) if j != whnf_idx]
            band_whnf[band_name] = float(np.mean(whnf_cos))

        # Total subcrystal count (max across bands)
        max_count = max(band_counts.values()) if band_counts else 0
        max_band = max(band_counts, key=band_counts.get) if band_counts else ""

        # Min overlap across all pairs (how fragmented is this depth?)
        all_overlaps = []
        for data in sign_results.values():
            for ov in data.get("overlaps", {}).values():
                if ov is not None:
                    all_overlaps.append(ov)
        min_overlap = min(all_overlaps) if all_overlaps else 1.0
        mean_overlap = float(np.mean(all_overlaps)) if all_overlaps else 1.0

        entry = {
            "layer": layer_idx,
            "depth": round(depth, 4),
            "band_subcrystal_counts": band_counts,
            "band_clusters": band_clusters,
            "band_agreement": band_agreement,
            "band_whnf_polarity": band_whnf,
            "angle_distribution": {bn: bands[bn]["n"] for bn in bands},
            "magnitude_correlations": mag_corrs,
            "max_subcrystals": max_count,
            "max_subcrystals_band": max_band,
            "min_overlap": min_overlap,
            "mean_overlap": mean_overlap,
        }
        depth_curve.append(entry)

        # Print breathing curve line
        bar_max = "█" * max_count + "░" * (4 - max_count)
        log(f"    max crystals: {max_count} ({max_band:12s})  "
            f"min_overlap: {min_overlap:.3f}  "
            f"mean_overlap: {mean_overlap:.3f}  {bar_max}")

    # ══════════════════════════════════════════════════════════════════
    # Synthesis: breathing curve
    # ══════════════════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("BREATHING CURVE: subcrystal count vs depth")
    log(f"{'='*70}")

    log(f"\n  {'Layer':>5s}  {'Depth':>5s}  {'Max':>3s}  {'Band':>12s}  "
        f"{'MinOv':>5s}  {'MeanOv':>6s}  Curve")
    log("  " + "-" * 65)

    for e in depth_curve:
        n = e["max_subcrystals"]
        bar = "██" * n + "░░" * (4 - n)
        arrow = ""
        log(f"  {e['layer']:5d}  {e['depth']:5.3f}  {n:3d}  {e['max_subcrystals_band']:>12s}  "
            f"{e['min_overlap']:5.3f}  {e['mean_overlap']:6.3f}  {bar}")

    # Per-band breathing curves
    for band_name, _, _ in ANGLE_BANDS:
        log(f"\n  {band_name}:")
        for e in depth_curve:
            n = e["band_subcrystal_counts"].get(band_name, 0)
            bar = "█" * n + "░" * (4 - n)
            whnf = e["band_whnf_polarity"].get(band_name)
            whnf_str = f"WHNF={whnf:+.3f}" if whnf is not None else "WHNF=    -"
            log(f"    L{e['layer']:02d} d={e['depth']:.3f}: {n} crystals  {bar}  {whnf_str}")

    # V13 pass mapping proposal
    log(f"\n{'='*70}")
    log("V13 PASS MAPPING (proposed)")
    log(f"{'='*70}")

    # Find inflection points
    counts = [e["max_subcrystals"] for e in depth_curve]
    min_count_idx = counts.index(min(counts))
    apex_depth = depth_curve[min_count_idx]["depth"]
    apex_layer = depth_curve[min_count_idx]["layer"]

    log(f"\n  Apex (minimum fragmentation): layer {apex_layer}, depth {apex_depth:.3f}")
    log(f"  Ascending arm: layers 1 → {apex_layer}")
    log(f"  Descending arm: layers {apex_layer} → 31")

    log(f"\n  Proposed V13 pass ↔ teacher depth mapping:")
    ascending = [e for e in depth_curve if e["layer"] <= apex_layer]
    descending = [e for e in depth_curve if e["layer"] > apex_layer]

    pass_names = ["L0↑", "L1↑", "L2↑", "apex", "L2↓", "L1↓", "L0↓"]

    # Distribute ascending layers across L0↑, L1↑, L2↑, apex
    n_asc = len(ascending)
    asc_split = max(1, n_asc // 3)  # rough thirds

    for i, e in enumerate(ascending):
        if i < asc_split:
            pass_name = "L0↑"
        elif i < 2 * asc_split:
            pass_name = "L1↑"
        elif i < n_asc - 1:
            pass_name = "L2↑"
        else:
            pass_name = "apex"
        log(f"    {pass_name:5s} → layer {e['layer']:2d} (d={e['depth']:.3f}): "
            f"{e['max_subcrystals']} subcrystals")

    n_desc = len(descending)
    desc_split = max(1, n_desc // 3)

    for i, e in enumerate(descending):
        if i < desc_split:
            pass_name = "L2↓"
        elif i < 2 * desc_split:
            pass_name = "L1↓"
        else:
            pass_name = "L0↓"
        log(f"    {pass_name:5s} → layer {e['layer']:2d} (d={e['depth']:.3f}): "
            f"{e['max_subcrystals']} subcrystals")

    # Save
    results = {
        "model": MODEL_NAME,
        "target_layers": TARGET_LAYERS,
        "depths": [round(d, 4) for d in DEPTHS],
        "breathing_curve": depth_curve,
        "apex": {"layer": apex_layer, "depth": apex_depth},
        "elapsed_seconds": time.time() - t0,
    }

    results_path = RESULTS_DIR / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n✓ Results saved to {results_path}")
    log(f"  Total time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
