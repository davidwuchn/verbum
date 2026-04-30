"""
Re-fit PCA projector on full 80K oracle data.

Subsamples ~50K word vectors (every 8th shard fully, rest sampled)
for PCA fitting — more than enough for stable 64-component PCA.
Computes mean from ALL data in a streaming pass.

Key: L2-normalize first (session 057 discovery — basin geometry is
in direction, not magnitude).

Output: results/oracle-data/pca_projector.npz

License: MIT
"""

import sys
import time
from pathlib import Path

import numpy as np

D_BASIN = 64
D_HIDDEN = 5120
SHARD_DIR = Path(__file__).parent.parent.parent / "results" / "oracle-data"
N_SHARDS = 160


def l2_normalize(X: np.ndarray) -> np.ndarray:
    """L2-normalize each row."""
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-8)
    return X / norms


def main():
    print(f"Re-fitting PCA projector on full oracle data")
    print(f"  d_basin={D_BASIN}, shard_dir={SHARD_DIR}")
    t0 = time.time()

    # Collect a representative sample for PCA (every 4th shard = ~40 shards × ~2700 = ~110K)
    # Plus compute global mean from ALL shards
    print("\nLoading shards (sample for PCA, mean from all)...")
    running_sum = np.zeros(D_HIDDEN, dtype=np.float64)
    total_words = 0
    sample_vecs = []

    for i in range(N_SHARDS):
        d = np.load(SHARD_DIR / f"shard_{i:04d}.npz", allow_pickle=True)
        vecs = d["word_vectors"].astype(np.float32)
        normed = l2_normalize(vecs)
        running_sum += normed.sum(axis=0).astype(np.float64)
        total_words += vecs.shape[0]

        # Sample every 4th shard fully for PCA
        if i % 4 == 0:
            sample_vecs.append(normed)

        if i % 40 == 0:
            elapsed = time.time() - t0
            print(f"  shard {i}/{N_SHARDS}: {total_words} words, {elapsed:.1f}s")

    global_mean = (running_sum / total_words).astype(np.float32)
    sample = np.concatenate(sample_vecs, axis=0)
    print(f"\n  Total: {total_words} words")
    print(f"  PCA sample: {sample.shape[0]} vectors from {len(sample_vecs)} shards")
    print(f"  Mean norm: {np.linalg.norm(global_mean):.4f}")
    del sample_vecs

    # Center and fit PCA
    print(f"\nFitting PCA (n_components={D_BASIN}) on {sample.shape[0]} vectors...")
    sample_centered = sample - global_mean
    del sample

    # Use numpy SVD directly — faster than sklearn for this size
    # Center: already done. SVD on (n, d) with n >> d
    U, S, Vt = np.linalg.svd(sample_centered, full_matrices=False)
    # Vt[:d_basin] = top d_basin components (each is 1×5120)
    components = Vt[:D_BASIN].astype(np.float32)  # (d_basin, 5120)

    # Explained variance ratio
    var = (S ** 2) / (sample_centered.shape[0] - 1)
    total_var = var.sum()
    explained_ratio = (var[:D_BASIN] / total_var).astype(np.float32)
    cumvar = np.cumsum(explained_ratio)

    t1 = time.time()
    print(f"  SVD complete in {t1-t0:.1f}s")
    print(f"  Explained variance at d={D_BASIN}: {cumvar[-1]:.3f}")
    print(f"  Top 8 ratios: {explained_ratio[:8]}")

    # Effective rank
    p = explained_ratio[explained_ratio > 0]
    eff_rank = np.exp(-np.sum(p * np.log(p + 1e-10)))
    print(f"  Effective rank (Shannon): {eff_rank:.1f}")

    del sample_centered, U, S, Vt

    # Validation: project shard 0 and check per-stratum separation
    print(f"\nValidation: shard 0 per-stratum similarity...")
    d = np.load(SHARD_DIR / "shard_0000.npz", allow_pickle=True)
    vecs = d["word_vectors"].astype(np.float32)
    strata = d["strata"]  # per-sentence
    offsets = d["sentence_offsets"]

    # Expand strata to per-word
    n_words = vecs.shape[0]
    word_strata = np.empty(n_words, dtype=strata.dtype)
    for si in range(len(offsets)):
        start = offsets[si]
        end = offsets[si + 1] if si + 1 < len(offsets) else n_words
        word_strata[start:end] = strata[si]

    normed = l2_normalize(vecs)
    centered = normed - global_mean
    projected = centered @ components.T  # (n, d_basin)

    from sklearn.metrics.pairwise import cosine_similarity
    unique_strata = np.unique(word_strata)
    for s in unique_strata:
        mask = word_strata == s
        if mask.sum() < 2:
            continue
        # subsample if too many for cosine_similarity matrix
        idxs = np.where(mask)[0]
        if len(idxs) > 500:
            idxs = np.random.default_rng(42).choice(idxs, 500, replace=False)
        sim = cosine_similarity(projected[idxs])
        within = sim[np.triu_indices(sim.shape[0], k=1)].mean()
        print(f"  {s:15s}: {mask.sum():4d} words, within-sim={within:.3f}")

    # Save
    out_path = SHARD_DIR / "pca_projector.npz"
    np.savez_compressed(
        out_path,
        components=components,              # (d_basin, 5120)
        mean=global_mean,                   # (5120,)
        explained_variance_ratio=explained_ratio,
        d_basin=np.array(D_BASIN),
        n_samples=np.array(total_words),
    )
    size_mb = out_path.stat().st_size / 1e6
    print(f"\nSaved: {out_path} ({size_mb:.1f} MB)")
    print(f"  components: {components.shape}")
    print(f"  n_samples: {total_words}")
    print(f"  Total time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
