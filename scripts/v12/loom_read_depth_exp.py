"""Loom Read Depth Experiment — How does subcrystal structure change with depth?

Session 124, experiment 2. The single-depth loom read (layer 16, depth 0.5)
found 3+ subcrystals: compose and retrieve diverge at the holographic angle
(sign overlap = 0.495), while route/neutral share a beamformer (0.9997 mag
correlation). The universal backbone (shared band 0-35°) had perfect agreement.

Now: does the subcrystal count change with depth? Key hypotheses:

1. Early layers may have FEWER subcrystals (undifferentiated residual stream)
2. Late layers may have MORE subcrystals (deeper computation = more weaves)
3. The FFN chain warp angle shifts with depth (58.7° at L8 → 80.8° at L28)
   — so the angle bands themselves may need to shift
4. The universal backbone may shrink at depth (more of the lattice becomes
   weave-specific as computation progresses)
5. Compose and retrieve agreed at transition (0.901 at depth 0.5) — do they
   split at deeper layers where WHNF retrieval dominates?

Protocol:
  1. Load Pythia-2.8b once
  2. Extract W_q and W_up at 5 target layers (depths 0.1, 0.3, 0.5, 0.7, 0.9)
  3. Hook residual stream + Q activations at each target layer
  4. For each depth:
     a. Compute CCA between W_q and W_up → angle bands (may shift!)
     b. Run all 144 basin probes → hidden states + Q activations
     c. Partition into 4 groups (compose, retrieve, route, neutral)
     d. Measure sign overlap matrix at each angle band
     e. Measure magnitude profile correlations
     f. Measure energy distribution
  5. Synthesize: depth profile of subcrystal structure

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/loom_read_depth_exp.py

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
D_FFN = 10240
SVD_K = 256

# Depths to probe (fraction of total layers)
DEPTHS = [0.1, 0.3, 0.5, 0.7, 0.9]

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "loom-read-depth"

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


def cosine_matrix(X: np.ndarray, indices: list[int]) -> np.ndarray:
    vecs = X[indices]
    norms = np.maximum(np.linalg.norm(vecs, axis=1, keepdims=True), 1e-8)
    vecs_n = vecs / norms
    return vecs_n @ vecs_n.T


def rdm_correlation(A: np.ndarray, B: np.ndarray) -> float:
    n = A.shape[0]
    idx = np.triu_indices(n, k=1)
    a = A[idx] - A[idx].mean()
    b = B[idx] - B[idx].mean()
    denom = np.sqrt(np.sum(a**2)) * np.sqrt(np.sum(b**2))
    return float(np.sum(a * b) / denom) if denom > 1e-10 else 0.0


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
# Extract everything in one model load
# ══════════════════════════════════════════════════════════════════════

def extract_all(probes, depths):
    """Load model once, extract weights + activations at all target depths."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # Convert depth fractions to layer indices
    target_layers = {}
    for d in depths:
        layer_idx = min(int(round(d * (N_LAYERS - 1))), N_LAYERS - 1)
        target_layers[d] = layer_idx

    log(f"  Loading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float32, device_map="mps",
    )
    model.eval()

    # ── Extract weights at all target layers ──
    weights = {}
    for d, layer_idx in target_layers.items():
        layer = model.gpt_neox.layers[layer_idx]
        qkv = layer.attention.query_key_value.weight.detach().cpu().float().numpy()
        W_q = qkv[:D_MODEL, :]
        W_up = layer.mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()
        weights[d] = {"W_q": W_q, "W_up": W_up, "layer_idx": layer_idx}
        log(f"    depth={d:.1f} → layer {layer_idx}: W_q={W_q.shape}, W_up={W_up.shape}")

    # ── Hook all target layers simultaneously ──
    captures = {d: {"h": [], "q": []} for d in depths}
    hooks = []

    for d, layer_idx in target_layers.items():
        # Residual stream input hook
        def make_h_hook(depth):
            def hook_fn(module, input, output):
                inp = input[0] if isinstance(input, tuple) else input
                captures[depth]["h"].append(inp[:, -1, :].detach().cpu().float())
            return hook_fn

        # Q activation hook (from fused QKV)
        def make_q_hook(depth):
            def hook_fn(module, input, output):
                qkv_out = output if not isinstance(output, tuple) else output[0]
                q = qkv_out[:, -1, :D_MODEL].detach().cpu().float()
                captures[depth]["q"].append(q)
            return hook_fn

        h_hook = model.gpt_neox.layers[layer_idx].register_forward_hook(make_h_hook(d))
        q_hook = model.gpt_neox.layers[layer_idx].attention.query_key_value.register_forward_hook(make_q_hook(d))
        hooks.extend([h_hook, q_hook])

    # ── Run all probes ──
    log(f"  Running {len(probes)} probes through {len(depths)} hooked layers...")
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to("mps")
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 30 == 0:
            log(f"    {i + 1}/{len(probes)}")

    for h in hooks:
        h.remove()

    # ── Collate ──
    activations = {}
    for d in depths:
        activations[d] = {
            "h": torch.cat(captures[d]["h"], dim=0).numpy(),
            "q": torch.cat(captures[d]["q"], dim=0).numpy(),
        }
        log(f"    depth={d:.1f}: h={activations[d]['h'].shape}, q={activations[d]['q'].shape}")

    del model, tokenizer
    gc.collect()
    torch.mps.empty_cache()

    return weights, activations


# ══════════════════════════════════════════════════════════════════════
# CCA + analysis (reused from loom_read_exp.py)
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

    return angles, dirs, dirs_q, dirs_up


def bin_directions(angles, dirs, dirs_q, dirs_up):
    bands = {}
    for name, lo, hi in ANGLE_BANDS:
        mask = (angles >= lo) & (angles < hi)
        bands[name] = {
            "dirs": dirs[:, mask],
            "dirs_q": dirs_q[:, mask],
            "dirs_up": dirs_up[:, mask],
            "angles": angles[mask],
            "n": int(mask.sum()),
        }
    return bands


def measure_sign_overlap(W_q, mag_profiles, bands, top_k_frac=0.2):
    """Sign overlap between probe groups at each angle band."""
    sign_W = np.sign(W_q)
    groups = list(mag_profiles.keys())
    results = {}

    for band_name, band_data in bands.items():
        if band_data["n"] < 2:
            results[band_name] = {"n_dirs": band_data["n"], "overlaps": {}}
            continue

        band_dirs = band_data["dirs"]
        group_signs = {}

        for group_name, mag_profile in mag_profiles.items():
            mag_in_band = np.abs(band_dirs.T @ mag_profile)
            n_top = max(1, int(top_k_frac * len(mag_in_band)))
            top_idx = np.argsort(mag_in_band)[-n_top:]
            top_dirs = band_dirs[:, top_idx]
            sign_projected = sign_W @ top_dirs
            group_signs[group_name] = np.sign(sign_projected).flatten()

        overlaps = {}
        for i, g1 in enumerate(groups):
            for j, g2 in enumerate(groups):
                if j <= i:
                    continue
                s1 = group_signs[g1]
                s2 = group_signs[g2]
                valid = (s1 != 0) & (s2 != 0)
                if valid.sum() == 0:
                    overlap = None
                else:
                    overlap = float(np.mean(s1[valid] == s2[valid]))
                overlaps[f"{g1}_vs_{g2}"] = overlap

        results[band_name] = {"n_dirs": band_data["n"], "overlaps": overlaps}

    return results


def measure_energy(activations, bands, probe_indices):
    subset = activations[probe_indices]
    total_energy = np.sum(subset ** 2)
    energies = {}
    for band_name, band_data in bands.items():
        if band_data["n"] < 1:
            energies[band_name] = 0.0
            continue
        projected = subset @ band_data["dirs"]
        energies[band_name] = float(np.sum(projected ** 2) / total_energy) if total_energy > 0 else 0.0
    return energies


def measure_magnitude_profile(activations, probe_indices):
    return np.sqrt(np.mean(activations[probe_indices] ** 2, axis=0))


def measure_band_crystal(activations, bands, pure_indices, reference_crystal):
    results = {}
    for band_name, band_data in bands.items():
        if band_data["n"] < 2:
            results[band_name] = {"agreement": None, "whnf_polarity": None, "n_dirs": band_data["n"]}
            continue

        projected = activations @ band_data["dirs"]
        cos_mat = cosine_matrix(projected, pure_indices)
        agreement = rdm_correlation(cos_mat, reference_crystal)

        whnf_idx = COMBINATOR_ORDER.index("WHNF")
        n_comb = len(pure_indices)
        whnf_cos = [cos_mat[whnf_idx, j] for j in range(n_comb) if j != whnf_idx]

        results[band_name] = {
            "agreement": float(agreement),
            "whnf_polarity": float(np.mean(whnf_cos)),
            "n_dirs": band_data["n"],
        }
    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def analyze_one_depth(
    depth: float,
    W_q: np.ndarray,
    W_up: np.ndarray,
    hidden_states: np.ndarray,
    q_activations: np.ndarray,
    probe_groups: dict,
    pure_indices: list[int],
):
    """Full analysis at one depth. Returns dict of all measurements."""
    log(f"\n{'='*60}")
    log(f"  DEPTH {depth:.1f}")
    log(f"{'='*60}")

    # CCA
    angles, dirs, dirs_q, dirs_up = compute_cca(W_q, W_up, SVD_K)
    bands = bin_directions(angles, dirs, dirs_q, dirs_up)

    # Angle distribution at this depth
    angle_hist = {}
    for name, band_data in bands.items():
        angle_hist[name] = band_data["n"]
    log(f"  Angle distribution: {angle_hist}")

    # Reference crystal
    ref_crystal = cosine_matrix(hidden_states, pure_indices)
    whnf_idx = COMBINATOR_ORDER.index("WHNF")
    n_comb = len(pure_indices)
    whnf_cos = [ref_crystal[whnf_idx, j] for j in range(n_comb) if j != whnf_idx]
    ref_whnf = float(np.mean(whnf_cos))
    log(f"  Reference WHNF polarity: {ref_whnf:+.4f}")

    # Q crystal agreement
    q_crystal = cosine_matrix(q_activations, pure_indices)
    q_agreement = rdm_correlation(q_crystal, ref_crystal)
    log(f"  Q crystal agreement: {q_agreement:.4f}")

    # Band crystal
    band_crystal = measure_band_crystal(hidden_states, bands, pure_indices, ref_crystal)
    log(f"\n  Band crystal:")
    for bn, data in band_crystal.items():
        if data["agreement"] is not None:
            log(f"    {bn:12s}: agr={data['agreement']:.4f}  WHNF={data['whnf_polarity']:+.4f}")

    # Magnitude profiles
    groups = list(probe_groups.keys())
    mag_profiles = {}
    for g, idx in probe_groups.items():
        mag_profiles[g] = measure_magnitude_profile(hidden_states, idx)

    # Magnitude correlations
    mag_corrs = {}
    log(f"\n  Magnitude correlations:")
    for i, g1 in enumerate(groups):
        for j, g2 in enumerate(groups):
            if j <= i:
                continue
            corr = float(np.corrcoef(mag_profiles[g1], mag_profiles[g2])[0, 1])
            mag_corrs[f"{g1}_vs_{g2}"] = corr
            log(f"    {g1} vs {g2}: {corr:.4f}")

    # Energy per group per band
    energy = {}
    for g, idx in probe_groups.items():
        energy[g] = measure_energy(hidden_states, bands, idx)

    # THE KEY: Sign overlap
    sign_overlap = measure_sign_overlap(W_q, mag_profiles, bands)

    log(f"\n  Sign overlaps (★ < 0.55 = different subcrystal):")
    for bn, data in sign_overlap.items():
        if data["n_dirs"] < 2:
            continue
        log(f"    {bn} ({data['n_dirs']} dirs):")
        for pair, ov in data["overlaps"].items():
            if ov is not None:
                marker = "★" if ov < 0.55 else ""
                log(f"      {pair:30s}: {ov:.4f}  {marker}")

    # Count distinct subcrystals per band
    # (groups with mutual overlap < 0.55 are in different subcrystals)
    subcrystal_count = {}
    for bn, data in sign_overlap.items():
        if data["n_dirs"] < 2:
            subcrystal_count[bn] = {"count": 0, "clusters": []}
            continue

        # Build adjacency: groups that agree (overlap >= 0.55) are same crystal
        # Groups with overlap < 0.55 are different crystals
        group_names = list(probe_groups.keys())
        n_g = len(group_names)
        agree_matrix = np.ones((n_g, n_g), dtype=bool)

        for pair_key, ov in data["overlaps"].items():
            if ov is None:
                continue
            parts = pair_key.split("_vs_")
            i_g = group_names.index(parts[0])
            j_g = group_names.index(parts[1])
            if ov < 0.55:
                agree_matrix[i_g, j_g] = False
                agree_matrix[j_g, i_g] = False

        # Simple connected-components clustering
        visited = set()
        clusters = []
        for i in range(n_g):
            if i in visited:
                continue
            cluster = {i}
            queue = [i]
            while queue:
                curr = queue.pop(0)
                for j in range(n_g):
                    if j not in visited and j not in cluster and agree_matrix[curr, j]:
                        cluster.add(j)
                        queue.append(j)
            visited.update(cluster)
            clusters.append([group_names[k] for k in sorted(cluster)])

        subcrystal_count[bn] = {
            "count": len(clusters),
            "clusters": clusters,
        }

    log(f"\n  Subcrystal counts:")
    for bn, data in subcrystal_count.items():
        if data["count"] > 0:
            clusters_str = " | ".join(["+".join(c) for c in data["clusters"]])
            log(f"    {bn:12s}: {data['count']} crystals  [{clusters_str}]")

    return {
        "angle_distribution": angle_hist,
        "reference_whnf_polarity": ref_whnf,
        "q_crystal_agreement": q_agreement,
        "band_crystal": band_crystal,
        "magnitude_correlations": mag_corrs,
        "energy_by_group": energy,
        "sign_overlap": sign_overlap,
        "subcrystal_count": subcrystal_count,
    }


def main():
    t0 = time.time()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load probes
    log("Loading probes...")
    probes = load_probes()
    probe_groups = partition_probes(probes)
    pure_indices = get_pure_indices(probes)

    log(f"  {len(probes)} probes, {len(pure_indices)} pure anchors")
    for g, idx in probe_groups.items():
        log(f"  {g}: {len(idx)} probes")

    # Extract everything in one model load
    log("\nExtracting from model (one load, all depths)...")
    weights, activations = extract_all(probes, DEPTHS)

    # Analyze each depth
    depth_results = {}
    for d in DEPTHS:
        W_q = weights[d]["W_q"]
        W_up = weights[d]["W_up"]
        h = activations[d]["h"]
        q = activations[d]["q"]

        depth_results[str(d)] = analyze_one_depth(
            d, W_q, W_up, h, q, probe_groups, pure_indices)

    # ══════════════════════════════════════════════════════════════════
    # Synthesis: depth profile
    # ══════════════════════════════════════════════════════════════════
    log(f"\n{'='*60}")
    log("SYNTHESIS: Depth profile of subcrystal structure")
    log(f"{'='*60}")

    log(f"\n  Subcrystal count by depth × band:")
    header = f"  {'band':12s}"
    for d in DEPTHS:
        header += f"  d={d:.1f}"
    log(header)
    log("  " + "-" * (12 + len(DEPTHS) * 7))

    for bn, _, _ in ANGLE_BANDS:
        row = f"  {bn:12s}"
        for d in DEPTHS:
            data = depth_results[str(d)]["subcrystal_count"].get(bn, {})
            count = data.get("count", 0)
            row += f"  {count:>4d}" if count > 0 else "     -"
        log(row)

    log(f"\n  Key sign overlaps at holographic band (64-72°):")
    for d in DEPTHS:
        data = depth_results[str(d)]["sign_overlap"].get("holographic", {})
        overlaps = data.get("overlaps", {})
        log(f"\n  depth={d:.1f}:")
        for pair, ov in overlaps.items():
            if ov is not None:
                marker = "★" if ov < 0.55 else ""
                log(f"    {pair:30s}: {ov:.4f}  {marker}")

    log(f"\n  WHNF polarity evolution (transition band):")
    for d in DEPTHS:
        bc = depth_results[str(d)]["band_crystal"].get("transition", {})
        whnf = bc.get("whnf_polarity")
        if whnf is not None:
            log(f"    depth={d:.1f}: {whnf:+.4f}")

    log(f"\n  Magnitude profile: compose vs route divergence:")
    for d in DEPTHS:
        mc = depth_results[str(d)]["magnitude_correlations"]
        cr = mc.get("compose_vs_route", 0)
        rn = mc.get("route_vs_neutral", 0)
        log(f"    depth={d:.1f}: compose↔route={cr:.4f}  route↔neutral={rn:.4f}")

    # Save
    all_results = {
        "model": MODEL_NAME,
        "depths": DEPTHS,
        "target_layers": {str(d): min(int(round(d * (N_LAYERS - 1))), N_LAYERS - 1) for d in DEPTHS},
        "n_probes": len(probes),
        "probe_groups": {k: len(v) for k, v in probe_groups.items()},
        "per_depth": depth_results,
        "elapsed_seconds": time.time() - t0,
    }

    results_path = RESULTS_DIR / "results.json"
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)

    log(f"\n✓ Results saved to {results_path}")
    log(f"  Total time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
