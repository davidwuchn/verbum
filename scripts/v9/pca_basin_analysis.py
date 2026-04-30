"""
PCA analysis on Qwen3-32B L28 activations to answer open design questions.

Questions:
  Q1. d_basin: how many PCA components capture basin structure?
  Q2. Are basins stable across probe subsets (words, expressions, behaviors)?

Inputs: saved activations from session 056 probes:
  - results/cluster-probe/activations.npz       (81 word probes)
  - results/kernel-basins/operator_activations.npz (94 operator probes)
  - results/kernel-basins/expression_activations.npz (54 expression probes)
  - results/behavior-basins/behavior_word_activations.npz (96 behavior probes)
  - results/behavior-depth/invariance_activations.npz (80 behavior-depth probes)

Each key → (64, 5120) array: 64 layers × 5120 hidden dim.
We extract layer 28 (peak typing layer) from each.

Output: PCA statistics, variance curves, d_basin recommendation.

License: MIT
"""

import json
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA


RESULTS_DIR = Path(__file__).parent.parent.parent / "results"
TARGET_LAYER = 28

# ══════════════════════════════════════════════════════════════════
# Load activations
# ══════════════════════════════════════════════════════════════════

def load_l28(npz_path: Path) -> dict[str, np.ndarray]:
    """Load all activations from an npz, extract layer TARGET_LAYER."""
    data = np.load(npz_path)
    out = {}
    for key in data.keys():
        arr = data[key]  # (64, 5120)
        out[key] = arr[TARGET_LAYER]  # (5120,)
    return out


def load_all_subsets() -> dict[str, np.ndarray]:
    """Load all probe subsets, return {subset_name: (n_probes, 5120) matrix}."""
    subsets = {}

    # 1. General word clusters
    words = load_l28(RESULTS_DIR / "cluster-probe" / "activations.npz")
    subsets["words"] = np.stack(list(words.values()))
    print(f"  words: {subsets['words'].shape}")

    # 2. Kernel operator words
    ops = load_l28(RESULTS_DIR / "kernel-basins" / "operator_activations.npz")
    subsets["operators"] = np.stack(list(ops.values()))
    print(f"  operators: {subsets['operators'].shape}")

    # 3. Expressions (cross-notation)
    exprs = load_l28(RESULTS_DIR / "kernel-basins" / "expression_activations.npz")
    subsets["expressions"] = np.stack(list(exprs.values()))
    print(f"  expressions: {subsets['expressions'].shape}")

    # 4. Behavior words
    behav = load_l28(RESULTS_DIR / "behavior-basins" / "behavior_word_activations.npz")
    subsets["behaviors"] = np.stack(list(behav.values()))
    print(f"  behaviors: {subsets['behaviors'].shape}")

    # 5. Behavior depth (word-in-context)
    depth = load_l28(RESULTS_DIR / "behavior-depth" / "invariance_activations.npz")
    subsets["behavior_depth"] = np.stack(list(depth.values()))
    print(f"  behavior_depth: {subsets['behavior_depth'].shape}")

    return subsets


# ══════════════════════════════════════════════════════════════════
# PCA analysis
# ══════════════════════════════════════════════════════════════════

def pca_analysis(X: np.ndarray, label: str, max_components: int = 512) -> dict:
    """Run PCA, report variance explained at key thresholds."""
    n_samples = X.shape[0]
    n_components = min(max_components, n_samples, X.shape[1])

    pca = PCA(n_components=n_components)
    pca.fit(X)

    cumvar = np.cumsum(pca.explained_variance_ratio_)

    # Find d at various thresholds
    thresholds = [0.80, 0.85, 0.90, 0.95, 0.99, 0.999]
    d_at = {}
    for t in thresholds:
        idx = np.searchsorted(cumvar, t)
        if idx < len(cumvar):
            d_at[f"{t:.1%}"] = int(idx + 1)
        else:
            d_at[f"{t:.1%}"] = f">{n_components}"

    # Effective rank (exponential of entropy of normalized eigenvalues)
    eigenvals = pca.explained_variance_ratio_
    eigenvals_pos = eigenvals[eigenvals > 1e-10]
    entropy = -np.sum(eigenvals_pos * np.log(eigenvals_pos))
    effective_rank = np.exp(entropy)

    # First 10 singular values (relative)
    top10 = eigenvals[:10].tolist()

    # Knee detection: find where marginal gain drops below 0.1%
    knee = None
    for i in range(1, len(eigenvals)):
        if eigenvals[i] < 0.001:  # individual component explains < 0.1%
            knee = i
            break

    result = {
        "label": label,
        "n_samples": n_samples,
        "n_features": X.shape[1],
        "n_components_fit": n_components,
        "effective_rank": round(effective_rank, 1),
        "d_at_threshold": d_at,
        "knee_at": knee,
        "top10_var_ratio": [round(v, 6) for v in top10],
        "cumvar_at_10": round(float(cumvar[9]) if len(cumvar) > 9 else cumvar[-1], 4),
        "cumvar_at_32": round(float(cumvar[31]) if len(cumvar) > 31 else cumvar[-1], 4),
        "cumvar_at_64": round(float(cumvar[63]) if len(cumvar) > 63 else cumvar[-1], 4),
        "cumvar_at_128": round(float(cumvar[127]) if len(cumvar) > 127 else cumvar[-1], 4),
        "cumvar_at_256": round(float(cumvar[255]) if len(cumvar) > 255 else cumvar[-1], 4),
    }

    print(f"\n{'='*60}")
    print(f"PCA: {label}")
    print(f"  Samples: {n_samples} × {X.shape[1]}")
    print(f"  Effective rank: {effective_rank:.1f}")
    print(f"  Knee (individual < 0.1%): component {knee}")
    print(f"  d for thresholds:")
    for k, v in d_at.items():
        print(f"    {k}: d = {v}")
    print(f"  Cumulative variance at key dims:")
    print(f"    d=10:  {result['cumvar_at_10']:.4f}")
    print(f"    d=32:  {result['cumvar_at_32']:.4f}")
    print(f"    d=64:  {result['cumvar_at_64']:.4f}")
    print(f"    d=128: {result['cumvar_at_128']:.4f}")
    print(f"    d=256: {result['cumvar_at_256']:.4f}")

    return result


def reconstruction_quality(X: np.ndarray, dims: list[int], label: str):
    """Measure cosine similarity after PCA reconstruction at various dims."""
    from sklearn.metrics.pairwise import cosine_similarity

    n_samples = X.shape[0]
    max_d = min(max(dims), n_samples, X.shape[1])

    pca = PCA(n_components=max_d)
    Z = pca.fit_transform(X)

    print(f"\n{'='*60}")
    print(f"Reconstruction quality: {label}")

    # Original pairwise cosine sim matrix
    orig_sim = cosine_similarity(X)
    # Upper triangle (excluding diagonal)
    triu_idx = np.triu_indices(n_samples, k=1)
    orig_pairs = orig_sim[triu_idx]

    for d in dims:
        if d > max_d:
            continue
        Z_d = Z[:, :d]
        X_recon = Z_d @ pca.components_[:d] + pca.mean_
        recon_sim = cosine_similarity(X_recon)
        recon_pairs = recon_sim[triu_idx]

        # How well does the reconstructed sim matrix match the original?
        sim_corr = np.corrcoef(orig_pairs, recon_pairs)[0, 1]

        # Direct reconstruction cosine sim (per-sample)
        per_sample = np.array([
            np.dot(X[i], X_recon[i]) / (np.linalg.norm(X[i]) * np.linalg.norm(X_recon[i]) + 1e-10)
            for i in range(n_samples)
        ])

        print(f"  d={d:4d}: recon_cos_sim={per_sample.mean():.4f}±{per_sample.std():.4f}, "
              f"sim_matrix_corr={sim_corr:.4f}")


# ══════════════════════════════════════════════════════════════════
# Multi-layer analysis (L0, L16, L28, L32, L48, L63)
# ══════════════════════════════════════════════════════════════════

def multi_layer_pca():
    """Check if PCA structure changes across layers."""
    # Load the full-layer data from cluster-probe
    data = np.load(RESULTS_DIR / "cluster-probe" / "activations.npz")
    all_keys = sorted(data.keys())

    layers = [0, 16, 28, 32, 48, 63]
    print(f"\n{'='*60}")
    print(f"Multi-layer PCA (cluster-probe, {len(all_keys)} probes)")

    for layer in layers:
        X = np.stack([data[k][layer] for k in all_keys])
        n_comp = min(X.shape[0], X.shape[1], 80)
        pca = PCA(n_components=n_comp)
        pca.fit(X)
        cumvar = np.cumsum(pca.explained_variance_ratio_)

        eigenvals = pca.explained_variance_ratio_
        eigenvals_pos = eigenvals[eigenvals > 1e-10]
        effective_rank = np.exp(-np.sum(eigenvals_pos * np.log(eigenvals_pos)))

        d90 = int(np.searchsorted(cumvar, 0.90) + 1) if cumvar[-1] >= 0.90 else f">{n_comp}"
        d95 = int(np.searchsorted(cumvar, 0.95) + 1) if cumvar[-1] >= 0.95 else f">{n_comp}"
        d99 = int(np.searchsorted(cumvar, 0.99) + 1) if cumvar[-1] >= 0.99 else f">{n_comp}"

        print(f"  L{layer:2d}: eff_rank={effective_rank:5.1f}, "
              f"d90={d90}, d95={d95}, d99={d99}, "
              f"cumvar@32={cumvar[min(31,len(cumvar)-1)]:.4f}")


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Loading all activation subsets from session 056 probes...")
    subsets = load_all_subsets()

    # 1. Per-subset PCA
    results = {}
    for name, X in subsets.items():
        results[name] = pca_analysis(X, name)

    # 2. Combined PCA (all probes)
    all_X = np.concatenate(list(subsets.values()), axis=0)
    results["ALL"] = pca_analysis(all_X, "ALL (combined)")

    # 3. Reconstruction quality at key dimensions
    reconstruction_quality(all_X, [8, 16, 32, 64, 128, 256], "ALL combined")

    # 4. Multi-layer comparison
    multi_layer_pca()

    # 5. Basin separability at reduced dimensions
    # Load cluster metadata to get group labels
    print(f"\n{'='*60}")
    print("Basin separability at reduced dimensions")

    with open(RESULTS_DIR / "cluster-probe" / "metadata.json") as f:
        cluster_meta = json.load(f)

    # Build label mapping from metadata
    word_data = load_l28(RESULTS_DIR / "cluster-probe" / "activations.npz")
    word_keys = list(word_data.keys())
    word_X = np.stack(list(word_data.values()))  # (81, 5120)

    # Extract group from key: "groupname__word_1234" → "groupname"
    word_groups = [k.rsplit("__", 1)[0] for k in word_keys]
    unique_groups = sorted(set(word_groups))
    group_ids = np.array([unique_groups.index(g) for g in word_groups])

    from sklearn.metrics.pairwise import cosine_similarity

    max_d = min(word_X.shape[0], word_X.shape[1], 256)
    pca = PCA(n_components=max_d)
    Z = pca.fit_transform(word_X)

    for d in [8, 16, 32, 64, 128, 256]:
        if d > max_d:
            continue
        Z_d = Z[:, :d]
        sim = cosine_similarity(Z_d)

        # Within-group vs between-group similarity
        within = []
        between = []
        for i in range(len(Z_d)):
            for j in range(i+1, len(Z_d)):
                if group_ids[i] == group_ids[j]:
                    within.append(sim[i, j])
                else:
                    between.append(sim[i, j])

        within_mean = np.mean(within)
        between_mean = np.mean(between)
        ratio = within_mean / (between_mean + 1e-10)

        print(f"  d={d:4d}: within={within_mean:.4f}, between={between_mean:.4f}, "
              f"ratio={ratio:.2f}×")

    # 6. Summary recommendation
    print(f"\n{'='*60}")
    print("SUMMARY & RECOMMENDATIONS")
    print("="*60)
    r = results["ALL"]
    print(f"\nCombined dataset: {r['n_samples']} probes × {r['n_features']} features")
    print(f"Effective rank: {r['effective_rank']}")
    print(f"\nVariance thresholds (ALL combined):")
    for k, v in r['d_at_threshold'].items():
        print(f"  {k} variance: d = {v}")
    print(f"\nRecommendation:")
    print(f"  d_basin should be set to capture ≥95% variance")
    print(f"  → d_basin = {r['d_at_threshold'].get('95.0%', '?')}")
    print(f"  (with {r['d_at_threshold'].get('99.0%', '?')} for 99% coverage)")
