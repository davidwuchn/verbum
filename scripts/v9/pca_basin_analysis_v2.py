"""
PCA analysis v2: mean-centered activations.

V1 showed effective rank ~1 because all L28 hidden states point in
roughly the same direction (high mean norm). The DISCRIMINATIVE
structure lives in the RESIDUALS after subtracting the mean.

This is the standard PCA approach — center the data first. sklearn's
PCA does center by default, but the explained variance ratio is
dominated by the mean direction when the mean norm >> residual norms.

The fix: analyze the CENTERED data explicitly, and use cosine
similarity on centered vectors (which is what the probes measured).

License: MIT
"""

import json
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity


RESULTS_DIR = Path(__file__).parent.parent.parent / "results"
TARGET_LAYER = 28


def load_l28(npz_path: Path) -> dict[str, np.ndarray]:
    """Load all activations from an npz, extract layer TARGET_LAYER."""
    data = np.load(npz_path)
    return {key: data[key][TARGET_LAYER] for key in data.keys()}


def load_all_subsets() -> dict[str, np.ndarray]:
    """Load all probe subsets, return {name: (n, 5120)}."""
    subsets = {}
    paths = {
        "words": RESULTS_DIR / "cluster-probe" / "activations.npz",
        "operators": RESULTS_DIR / "kernel-basins" / "operator_activations.npz",
        "expressions": RESULTS_DIR / "kernel-basins" / "expression_activations.npz",
        "behaviors": RESULTS_DIR / "behavior-basins" / "behavior_word_activations.npz",
        "behavior_depth": RESULTS_DIR / "behavior-depth" / "invariance_activations.npz",
    }
    for name, path in paths.items():
        d = load_l28(path)
        subsets[name] = np.stack(list(d.values()))
        print(f"  {name}: {subsets[name].shape}")
    return subsets


def centered_pca_analysis(X: np.ndarray, label: str, max_components: int = None):
    """PCA on CENTERED data. Report structure in residuals."""
    mean = X.mean(axis=0)
    mean_norm = np.linalg.norm(mean)
    residual_norms = np.linalg.norm(X - mean, axis=1)

    print(f"\n{'='*60}")
    print(f"Centered PCA: {label}")
    print(f"  Samples: {X.shape[0]} × {X.shape[1]}")
    print(f"  Mean norm: {mean_norm:.2f}")
    print(f"  Residual norms: {residual_norms.mean():.2f} ± {residual_norms.std():.2f}")
    print(f"  Mean/residual ratio: {mean_norm / residual_norms.mean():.2f}×")

    # PCA on centered data
    n_comp = max_components or min(X.shape[0] - 1, X.shape[1], 300)
    pca = PCA(n_components=n_comp)
    pca.fit(X)  # PCA centers internally

    cumvar = np.cumsum(pca.explained_variance_ratio_)
    eigenvals = pca.explained_variance_ratio_

    # Effective rank of CENTERED covariance
    eigenvals_pos = eigenvals[eigenvals > 1e-10]
    entropy = -np.sum(eigenvals_pos * np.log(eigenvals_pos))
    effective_rank = np.exp(entropy)

    # Key thresholds
    thresholds = [0.80, 0.85, 0.90, 0.95, 0.99, 0.999]
    d_at = {}
    for t in thresholds:
        idx = np.searchsorted(cumvar, t)
        d_at[t] = int(idx + 1) if idx < len(cumvar) else f">{n_comp}"

    # Knee: where individual component < 1% of centered variance
    knee_1pct = None
    knee_01pct = None
    for i, ev in enumerate(eigenvals):
        if knee_1pct is None and ev < 0.01:
            knee_1pct = i
        if knee_01pct is None and ev < 0.001:
            knee_01pct = i

    print(f"  Effective rank (centered): {effective_rank:.1f}")
    print(f"  Knee (<1% per component): {knee_1pct}")
    print(f"  Knee (<0.1% per component): {knee_01pct}")
    print(f"  Top 10 eigenvalue ratios: {[f'{v:.4f}' for v in eigenvals[:10]]}")
    print(f"  d for thresholds:")
    for t, d in d_at.items():
        print(f"    {t:.0%}: d = {d}")

    dims = [4, 8, 16, 32, 64, 128, 256]
    print(f"  Cumvar at key dims:")
    for d in dims:
        if d-1 < len(cumvar):
            print(f"    d={d:4d}: {cumvar[d-1]:.4f}")

    return {
        "label": label,
        "n_samples": X.shape[0],
        "effective_rank": round(effective_rank, 1),
        "mean_norm": round(float(mean_norm), 2),
        "residual_norm_mean": round(float(residual_norms.mean()), 2),
        "d_at": {f"{t:.0%}": d for t, d in d_at.items()},
        "knee_1pct": knee_1pct,
        "knee_01pct": knee_01pct,
        "top10_eigenvals": [round(float(v), 6) for v in eigenvals[:10]],
        "cumvar": {d: round(float(cumvar[d-1]), 4) for d in dims if d-1 < len(cumvar)},
        "pca": pca,
    }


def reconstruction_preserves_basins(X: np.ndarray, group_labels: np.ndarray,
                                     label: str, dims: list[int]):
    """Test: does PCA reconstruction preserve basin separability?"""
    n = X.shape[0]
    max_d = min(max(dims), n - 1, X.shape[1])
    pca = PCA(n_components=max_d)
    Z = pca.fit_transform(X)

    print(f"\n{'='*60}")
    print(f"Basin separability after PCA: {label}")

    # Original cosine sim
    orig_sim = cosine_similarity(X)

    for d in dims:
        if d > max_d:
            continue
        # Work in PCA space directly (cosine sim of PCA coordinates)
        Z_d = Z[:, :d]
        pca_sim = cosine_similarity(Z_d)

        # Within vs between group sim in PCA space
        within, between = [], []
        for i in range(n):
            for j in range(i+1, n):
                if group_labels[i] == group_labels[j]:
                    within.append(pca_sim[i, j])
                else:
                    between.append(pca_sim[i, j])

        within_m = np.mean(within)
        between_m = np.mean(between)
        ratio = within_m / (between_m + 1e-10) if between_m > 0 else float('inf')

        # Also: correlation between original and PCA sim matrices
        triu = np.triu_indices(n, k=1)
        sim_corr = np.corrcoef(orig_sim[triu], pca_sim[triu])[0, 1]

        print(f"  d={d:4d}: within={within_m:.4f}, between={between_m:.4f}, "
              f"ratio={ratio:.2f}×, sim_corr={sim_corr:.4f}")


def cross_subset_stability(subsets: dict[str, np.ndarray]):
    """Do different subsets have the same PCA directions?"""
    print(f"\n{'='*60}")
    print(f"Cross-subset PCA alignment")
    print(f"  (cosine sim between top-k principal components)")

    pca_results = {}
    for name, X in subsets.items():
        if X.shape[0] < 10:
            continue
        n_comp = min(X.shape[0] - 1, 64)
        pca = PCA(n_components=n_comp)
        pca.fit(X)
        pca_results[name] = pca.components_  # (n_comp, 5120)

    names = list(pca_results.keys())
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            n1, n2 = names[i], names[j]
            c1 = pca_results[n1]
            c2 = pca_results[n2]
            # Top-k alignment: for each of top-k PCs in set1,
            # what's max cosine sim to any of top-k PCs in set2?
            for k in [4, 8, 16]:
                k1 = min(k, c1.shape[0])
                k2 = min(k, c2.shape[0])
                sims = np.abs(cosine_similarity(c1[:k1], c2[:k2]))
                # Best match per PC in set1
                best_match = sims.max(axis=1).mean()
                print(f"  {n1:20s} ↔ {n2:20s} top-{k:2d}: avg_best_match={best_match:.4f}")


def multi_layer_centered(subsets: dict):
    """Check centered PCA structure across layers for all combined data."""
    # Re-load with all layers for cluster-probe
    data = np.load(RESULTS_DIR / "cluster-probe" / "activations.npz")
    all_keys = sorted(data.keys())

    layers = [0, 8, 16, 24, 28, 32, 37, 48, 56, 63]
    print(f"\n{'='*60}")
    print(f"Multi-layer centered PCA (cluster-probe, {len(all_keys)} probes)")

    for layer in layers:
        X = np.stack([data[k][layer] for k in all_keys])
        mean_norm = np.linalg.norm(X.mean(axis=0))
        resid_norm = np.linalg.norm(X - X.mean(axis=0), axis=1).mean()

        n_comp = min(X.shape[0] - 1, 80)
        pca = PCA(n_components=n_comp)
        pca.fit(X)
        cumvar = np.cumsum(pca.explained_variance_ratio_)
        eigenvals = pca.explained_variance_ratio_
        eigenvals_pos = eigenvals[eigenvals > 1e-10]
        eff_rank = np.exp(-np.sum(eigenvals_pos * np.log(eigenvals_pos)))

        d90 = int(np.searchsorted(cumvar, 0.90) + 1)
        d95 = int(np.searchsorted(cumvar, 0.95) + 1)

        print(f"  L{layer:2d}: eff_rank={eff_rank:5.1f}, d90={d90:3d}, d95={d95:3d}, "
              f"mean/resid={mean_norm/resid_norm:.1f}×, "
              f"top3=[{eigenvals[0]:.3f}, {eigenvals[1]:.3f}, {eigenvals[2]:.3f}]")


if __name__ == "__main__":
    print("Loading all activation subsets from session 056 probes...")
    subsets = load_all_subsets()

    # 1. Per-subset centered PCA
    results = {}
    for name, X in subsets.items():
        results[name] = centered_pca_analysis(X, name)

    # 2. Combined
    all_X = np.concatenate(list(subsets.values()), axis=0)
    results["ALL"] = centered_pca_analysis(all_X, "ALL combined")

    # 3. Basin separability at reduced dimensions (word clusters)
    word_data = load_l28(RESULTS_DIR / "cluster-probe" / "activations.npz")
    word_keys = list(word_data.keys())
    word_X = np.stack(list(word_data.values()))
    word_groups = [k.rsplit("__", 1)[0] for k in word_keys]
    unique_groups = sorted(set(word_groups))
    group_ids = np.array([unique_groups.index(g) for g in word_groups])

    reconstruction_preserves_basins(word_X, group_ids, "word clusters",
                                     [4, 8, 16, 32, 64])

    # 4. Cross-subset PCA stability
    cross_subset_stability(subsets)

    # 5. Multi-layer comparison
    multi_layer_centered(subsets)

    # 6. Behavior-depth: the highest-rank subset
    print(f"\n{'='*60}")
    print(f"DETAILED: behavior_depth (highest effective rank)")
    bd = subsets["behavior_depth"]
    bd_result = results["behavior_depth"]

    # What makes behavior_depth so high-rank?
    # Load metadata to understand
    with open(RESULTS_DIR / "behavior-depth" / "invariance_metadata.json") as f:
        bd_meta = json.load(f)
    print(f"  Metadata keys: {list(bd_meta.keys())[:5]}")

    # Check if it's the word diversity × frame diversity
    bd_keys = list(load_l28(RESULTS_DIR / "behavior-depth" / "invariance_activations.npz").keys())
    print(f"  Keys (first 10): {bd_keys[:10]}")
    # Parse: "word__frame" structure
    words_set = set()
    frames_set = set()
    for k in bd_keys:
        parts = k.split("__")
        if len(parts) == 2:
            words_set.add(parts[0])
            frames_set.add(parts[1])
        else:
            words_set.add(k)
    print(f"  Unique words: {len(words_set)}: {sorted(words_set)[:10]}")
    print(f"  Unique frames: {len(frames_set)}: {sorted(frames_set)[:10]}")

    # 7. Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY & d_basin RECOMMENDATION")
    print("="*60)

    print(f"""
Dataset composition:
  words (semantic clusters):     {subsets['words'].shape[0]:4d} probes, eff_rank={results['words']['effective_rank']}
  operators (kernel ops):        {subsets['operators'].shape[0]:4d} probes, eff_rank={results['operators']['effective_rank']}
  expressions (cross-notation):  {subsets['expressions'].shape[0]:4d} probes, eff_rank={results['expressions']['effective_rank']}
  behaviors (intent words):      {subsets['behaviors'].shape[0]:4d} probes, eff_rank={results['behaviors']['effective_rank']}
  behavior_depth (word×frame):   {subsets['behavior_depth'].shape[0]:4d} probes, eff_rank={results['behavior_depth']['effective_rank']}
  ALL combined:                  {all_X.shape[0]:4d} probes, eff_rank={results['ALL']['effective_rank']}

Key insight: behavior_depth has highest rank because it contains the
SAME WORD in DIFFERENT CONTEXTS. The word×frame cross produces the
richest activation geometry. This IS what the ascending arm must capture.

d_basin recommendation (from centered PCA on ALL combined):""")

    r = results["ALL"]
    print(f"  95% variance: d = {r['d_at']['95%']}")
    print(f"  99% variance: d = {r['d_at']['99%']}")
    print(f"  Knee (<1% per component): {r['knee_1pct']}")
    print(f"  Effective rank: {r['effective_rank']}")

    bd_r = results["behavior_depth"]
    print(f"\nd_basin recommendation (from behavior_depth — hardest subset):")
    print(f"  95% variance: d = {bd_r['d_at']['95%']}")
    print(f"  99% variance: d = {bd_r['d_at']['99%']}")
    print(f"  Knee (<1% per component): {bd_r['knee_1pct']}")
    print(f"  Effective rank: {bd_r['effective_rank']}")
