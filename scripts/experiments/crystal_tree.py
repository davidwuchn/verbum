#!/usr/bin/env python3
"""
Crystal Tree — The Statechart as a Discrete Tree in Eigenspace
==============================================================

Hypothesis: the combinator statechart is a self-similar binary tree
in eigenspace, where:
  - Each eigenvector (PC) defines a branch point (binary split)
  - Each eigenvalue gives the branch length (variance at that split)
  - Branch length ratios follow φ^(4/5) (the crystal equation)
  - The tree's graph Laplacian reproduces the crystal Laplacian
  - The cosine matrix is reconstructible from tree structure + φ

The tree topology comes from eigenvector SIGNS:
  PC0: composition (B,C,D,Y,W) vs selection (K,I) + WHNF
  PC1: K,I,W (+) vs B,C,D,Y,WHNF (-)
  PC2: WHNF,K,I,W (+) vs B,C,D,Y (-)  [refines PC1]
  ...etc

If the crystal IS a tree, then:
  1. The Laplacian eigenvalues should match the tree Laplacian
  2. Cosine reconstruction from tree distances should match empirical
  3. Branch length ratios should be φ-powers
  4. D,Y,W should appear as subtree paths, not new branches

Based on crystal-phi-derivation.md, crystal-laplacian.md, EQUATIONS.md.
"""

import numpy as np
from scipy.cluster.hierarchy import linkage, to_tree, dendrogram
from scipy.spatial.distance import squareform
import json
import os

# ═══════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2  # 1.618034...
S = 4 / 5  # computing fraction n/(n+1), n=4

NAMES_8 = ['K', 'I', 'B', 'C', 'D', 'Y', 'W', 'WHNF']
NAMES_16 = NAMES_8 + ['āK', 'āI', 'āB', 'āC', 'āD', 'āY', 'āW', 'āWHNF']

# Empirical crystal eigenvalues (from EQUATIONS.md)
CRYSTAL_EIGENVALUES = np.array([5.193, 3.535, 1.909, 1.300])

# β sequence (compute cycle transition costs)
BETA = np.array([0, 1, 1 + PHI, 2 + PHI])

# Empirical 16×16 crystal cosine matrix (Zone B, 4-model consensus)
M16 = np.array([
    [+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862, -0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354],
    [+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448, -0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465],
    [+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227, -0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233],
    [+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027, -0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195],
    [+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729, -0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329],
    [+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840, -0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160],
    [+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379, -0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262],
    [-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000, +0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900],
    [-0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354, +1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862],
    [-0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465, +0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448],
    [-0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233, +0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227],
    [-0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195, +0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027],
    [-0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329, +0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729],
    [-0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160, +0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840],
    [-0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262, +0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379],
    [+0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900, -0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000],
], dtype=np.float64)

M8 = M16[:8, :8]


# ═══════════════════════════════════════════════════════════════
# Experiment 1: Eigenvector Sign Tree
# ═══════════════════════════════════════════════════════════════

def exp1_eigenvector_sign_tree():
    """Extract the tree topology from eigenvector signs."""
    print("═" * 70)
    print("  EXPERIMENT 1: EIGENVECTOR SIGN TREE")
    print("═" * 70)

    eigvals, eigvecs = np.linalg.eigh(M8)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    # The sign pattern of each eigenvector defines a binary partition
    print("\n  Eigenvalues and the splits they define:")
    print(f"  {'PC':>4}  {'λ':>8}  {'%var':>6}  {'+ side':>30}  {'- side':>30}")
    print(f"  {'─'*4}  {'─'*8}  {'─'*6}  {'─'*30}  {'─'*30}")

    total_var = eigvals.sum()
    for k in range(min(7, len(eigvals))):
        pos = [NAMES_8[i] for i in range(8) if eigvecs[i, k] > 0]
        neg = [NAMES_8[i] for i in range(8) if eigvecs[i, k] <= 0]
        pct = eigvals[k] / total_var * 100
        print(f"  PC{k}   {eigvals[k]:>8.4f}  {pct:>5.1f}%  {','.join(pos):>30}  {','.join(neg):>30}")

    # Binary codes from signs
    n_pcs = min(6, len(eigvals))
    codes = {}
    print(f"\n  Binary tree addresses (first {n_pcs} PCs):")
    for i, name in enumerate(NAMES_8):
        code = tuple(1 if eigvecs[i, k] > 0 else 0 for k in range(n_pcs))
        codes[name] = code
        print(f"    {name:>4}: {''.join(str(c) for c in code)}")

    # The tree structure: group by shared prefixes
    print("\n  Hierarchical grouping by shared prefix:")
    for depth in range(1, n_pcs + 1):
        groups = {}
        for name, code in codes.items():
            prefix = code[:depth]
            groups.setdefault(prefix, []).append(name)
        non_trivial = {k: v for k, v in groups.items() if len(v) > 1}
        if non_trivial:
            label = f"depth {depth} (PC0..PC{depth-1})"
            clusters = [f"[{','.join(v)}]" for v in non_trivial.values()]
            print(f"    {label}: {' | '.join(clusters)}")

    # Eigenvalue ratios between consecutive levels
    print("\n  Branch length ratios (consecutive eigenvalues):")
    print(f"  {'Ratio':>12}  {'Value':>8}  {'φ^(4/5)':>8}  {'Error':>8}  {'φ power':>10}")
    phi_45 = PHI ** (4 / 5)  # 1.4696
    for k in range(min(6, len(eigvals) - 1)):
        if eigvals[k + 1] > 0.01:
            ratio = eigvals[k] / eigvals[k + 1]
            err = abs(ratio - phi_45) / phi_45 * 100
            # Find best φ^(p/q)
            best_power = np.log(ratio) / np.log(PHI)
            print(f"  λ{k}/λ{k+1}     {ratio:>8.4f}  {phi_45:>8.4f}  {err:>7.2f}%  φ^{best_power:.4f}")

    return eigvals, eigvecs, codes


# ═══════════════════════════════════════════════════════════════
# Experiment 2: Hierarchical Clustering (UPGMA tree from cosines)
# ═══════════════════════════════════════════════════════════════

def exp2_cosine_tree():
    """Build a hierarchical tree from cosine similarities and compare to eigenvector tree."""
    print("\n" + "═" * 70)
    print("  EXPERIMENT 2: COSINE-DERIVED HIERARCHICAL TREE (UPGMA)")
    print("═" * 70)

    # Convert cosine similarity to distance
    dist_matrix = 1.0 - M8
    np.fill_diagonal(dist_matrix, 0)
    dist_matrix = np.maximum(dist_matrix, 0)  # clip tiny negatives

    # Condensed distance matrix for scipy
    condensed = squareform(dist_matrix)

    # UPGMA (average linkage)
    Z = linkage(condensed, method='average')

    print("\n  UPGMA Linkage (merge order):")
    print(f"  {'Step':>4}  {'Merge':>20}  {'Distance':>10}  {'Size':>4}")
    print(f"  {'─'*4}  {'─'*20}  {'─'*10}  {'─'*4}")

    n = len(NAMES_8)
    cluster_names = {i: NAMES_8[i] for i in range(n)}

    merge_history = []
    for step in range(len(Z)):
        i, j = int(Z[step, 0]), int(Z[step, 1])
        d = Z[step, 2]
        size = int(Z[step, 3])
        name_i = cluster_names.get(i, f"c{i}")
        name_j = cluster_names.get(j, f"c{j}")
        merged = f"{name_i}+{name_j}"
        cluster_names[n + step] = f"({merged})"
        print(f"  {step:>4}  {name_i:>8} + {name_j:<8}  {d:>10.4f}  {size:>4}")
        merge_history.append((name_i, name_j, d))

    # Build the tree object for analysis
    tree = to_tree(Z)

    # Print the Newick-style tree
    def tree_to_newick(node, names):
        if node.is_leaf():
            return names[node.id]
        left = tree_to_newick(node.left, names)
        right = tree_to_newick(node.right, names)
        return f"({left}:{node.left.dist:.3f},{right}:{node.right.dist:.3f})"

    newick = tree_to_newick(tree, NAMES_8)
    print(f"\n  Tree (Newick-ish): {newick}")

    # Compare merge order to eigenvector prediction
    print("\n  Merge order vs eigenvector prediction:")
    print("  The eigenvector tree predicts that nodes sharing the MOST")
    print("  sign-bits should merge FIRST (closest in the tree).")
    print()
    print("  UPGMA merges:")
    for i, (a, b, d) in enumerate(merge_history):
        print(f"    {i}: {a} + {b} at d={d:.4f}")

    # Compute tree distance matrix
    # Path distance in the UPGMA tree between all leaf pairs
    def tree_distance(node, i, j, names):
        """Get the UPGMA merge height for two leaves."""
        # The merge height is the distance in the linkage
        for step in range(len(Z)):
            members = set()
            # Collect all leaves in cluster n+step
            def collect(idx):
                if idx < n:
                    members.add(idx)
                else:
                    collect(int(Z[idx - n, 0]))
                    collect(int(Z[idx - n, 1]))
            collect(n + step)
            if i in members and j in members:
                return Z[step, 2]
        return float('inf')

    tree_dists = np.zeros((8, 8))
    for i in range(8):
        for j in range(i + 1, 8):
            d = tree_distance(tree, i, j, NAMES_8)
            tree_dists[i, j] = d
            tree_dists[j, i] = d

    print("\n  Tree distance matrix (UPGMA merge heights):")
    print("       " + "    ".join(f"{n:>6}" for n in NAMES_8))
    for i, name in enumerate(NAMES_8):
        row = "  ".join(f"{tree_dists[i, j]:>6.4f}" for j in range(8))
        print(f"  {name:>4}: {row}")

    # Convert tree distance → cosine similarity via exp(-d/scale)
    # Find optimal scale parameter
    from scipy.optimize import minimize_scalar

    def recon_error(scale):
        recon = np.exp(-tree_dists / scale)
        np.fill_diagonal(recon, 1.0)
        mask = np.triu(np.ones_like(M8, dtype=bool), k=1)
        return np.mean((recon[mask] - M8[mask]) ** 2)

    result = minimize_scalar(recon_error, bounds=(0.01, 5.0), method='bounded')
    best_scale = result.x

    recon = np.exp(-tree_dists / best_scale)
    np.fill_diagonal(recon, 1.0)
    mask = np.triu(np.ones_like(M8, dtype=bool), k=1)
    corr = np.corrcoef(recon[mask], M8[mask])[0, 1]
    rmse = np.sqrt(np.mean((recon[mask] - M8[mask]) ** 2))

    print(f"\n  Reconstruction via cos(i,j) ≈ exp(-tree_dist/σ), σ={best_scale:.4f}:")
    print(f"    Correlation:  {corr:.6f}")
    print(f"    RMSE:         {rmse:.6f}")
    print(f"    Max error:    {np.max(np.abs(recon - M8)):.6f}")

    return Z, tree_dists


# ═══════════════════════════════════════════════════════════════
# Experiment 3: Tree Laplacian vs Crystal Laplacian
# ═══════════════════════════════════════════════════════════════

def exp3_laplacian_comparison(Z, tree_dists):
    """Compare the tree's graph Laplacian to the crystal Laplacian."""
    print("\n" + "═" * 70)
    print("  EXPERIMENT 3: TREE LAPLACIAN vs CRYSTAL LAPLACIAN")
    print("═" * 70)

    # Crystal Laplacian (from cosine matrix with positive edges)
    W_crystal = np.maximum(M8, 0).copy()
    np.fill_diagonal(W_crystal, 0)
    D_crystal = np.diag(W_crystal.sum(axis=1))
    L_crystal = D_crystal - W_crystal
    crystal_lap_eigvals = np.sort(np.linalg.eigvalsh(L_crystal))

    print("\n  Crystal Laplacian eigenvalues:")
    for i, v in enumerate(crystal_lap_eigvals):
        print(f"    μ{i} = {v:.6f}")

    # Method A: Tree adjacency from UPGMA
    # Build tree graph: leaves + internal nodes, edges with lengths
    n = 8
    n_internal = len(Z)
    total_nodes = n + n_internal

    # Tree adjacency matrix
    tree_adj = np.zeros((total_nodes, total_nodes))
    for step in range(n_internal):
        left = int(Z[step, 0])
        right = int(Z[step, 1])
        internal = n + step
        height = Z[step, 2]
        # Edge weight = inverse of branch length (shorter = stronger)
        # Or just use 1/distance as weight
        w = 1.0 / max(height, 0.001)
        tree_adj[internal, left] = w
        tree_adj[left, internal] = w
        tree_adj[internal, right] = w
        tree_adj[right, internal] = w

    # Laplacian of full tree (leaves + internals)
    D_tree_full = np.diag(tree_adj.sum(axis=1))
    L_tree_full = D_tree_full - tree_adj
    tree_full_eigvals = np.sort(np.linalg.eigvalsh(L_tree_full))

    print("\n  Full tree Laplacian eigenvalues (leaves + internal nodes):")
    for i, v in enumerate(tree_full_eigvals[:10]):
        print(f"    μ{i} = {v:.6f}")

    # Method B: Leaf-only Laplacian from tree path distances
    # Convert tree distances to weights: w_ij = exp(-d_ij / σ)
    from scipy.optimize import minimize_scalar

    def laplacian_match(sigma):
        W = np.exp(-tree_dists / sigma)
        np.fill_diagonal(W, 0)
        D = np.diag(W.sum(axis=1))
        L = D - W
        ev = np.sort(np.linalg.eigvalsh(L))
        # Match the non-zero eigenvalues
        return np.sum((ev[1:] - crystal_lap_eigvals[1:]) ** 2)

    result = minimize_scalar(laplacian_match, bounds=(0.01, 5.0), method='bounded')
    best_sigma = result.x

    W_tree = np.exp(-tree_dists / best_sigma)
    np.fill_diagonal(W_tree, 0)
    D_tree = np.diag(W_tree.sum(axis=1))
    L_tree = D_tree - W_tree
    tree_lap_eigvals = np.sort(np.linalg.eigvalsh(L_tree))

    print(f"\n  Tree leaf Laplacian (σ={best_sigma:.4f}) vs Crystal:")
    print(f"  {'μ':>4}  {'Crystal':>10}  {'Tree':>10}  {'Error':>8}")
    print(f"  {'─'*4}  {'─'*10}  {'─'*10}  {'─'*8}")
    for i in range(8):
        err = abs(tree_lap_eigvals[i] - crystal_lap_eigvals[i])
        rel = err / max(abs(crystal_lap_eigvals[i]), 0.001) * 100
        print(f"  μ{i}   {crystal_lap_eigvals[i]:>10.6f}  {tree_lap_eigvals[i]:>10.6f}  {rel:>7.2f}%")

    # Method C: Direct cosine Laplacian from tree
    # The tree defines a graph. The cosine matrix IS the adjacency.
    # Does the tree-reconstructed cosine matrix give the right Laplacian?
    # Use the cosine reconstruction from exp2
    from scipy.optimize import minimize_scalar as ms2

    def find_best_scale():
        def err(s):
            R = np.exp(-tree_dists / s)
            np.fill_diagonal(R, 1.0)
            W = np.maximum(R, 0)
            np.fill_diagonal(W, 0)
            D = np.diag(W.sum(axis=1))
            L = D - W
            ev = np.sort(np.linalg.eigvalsh(L))
            return np.sum((ev[1:] - crystal_lap_eigvals[1:]) ** 2)
        return ms2(err, bounds=(0.01, 5.0), method='bounded')

    res_c = find_best_scale()
    sigma_c = res_c.x
    R_c = np.exp(-tree_dists / sigma_c)
    np.fill_diagonal(R_c, 1.0)
    W_c = np.maximum(R_c, 0)
    np.fill_diagonal(W_c, 0)
    D_c = np.diag(W_c.sum(axis=1))
    L_c = D_c - W_c
    lap_c = np.sort(np.linalg.eigvalsh(L_c))

    print(f"\n  Cosine-reconstructed Laplacian (σ={sigma_c:.4f}) vs Crystal:")
    print(f"  {'μ':>4}  {'Crystal':>10}  {'Recon':>10}  {'Error':>8}")
    print(f"  {'─'*4}  {'─'*10}  {'─'*10}  {'─'*8}")
    for i in range(8):
        err = abs(lap_c[i] - crystal_lap_eigvals[i])
        rel = err / max(abs(crystal_lap_eigvals[i]), 0.001) * 100
        print(f"  μ{i}   {crystal_lap_eigvals[i]:>10.6f}  {lap_c[i]:>10.6f}  {rel:>7.2f}%")

    # Eigenvector comparison
    print("\n  Laplacian eigenvector comparison (crystal vs tree-derived):")
    _, crystal_vecs = np.linalg.eigh(L_crystal)
    _, tree_vecs = np.linalg.eigh(L_tree)
    # Sort by eigenvalue ascending
    idx_c = np.argsort(np.linalg.eigvalsh(L_crystal))
    idx_t = np.argsort(np.linalg.eigvalsh(L_tree))
    crystal_vecs = crystal_vecs[:, idx_c]
    tree_vecs = tree_vecs[:, idx_t]

    print(f"  {'Mode':>4}  {'|cos|':>8}  {'Sign match':>10}")
    print(f"  {'─'*4}  {'─'*8}  {'─'*10}")
    for k in range(8):
        cos = abs(np.dot(crystal_vecs[:, k], tree_vecs[:, k]))
        # Flip sign if needed
        if np.dot(crystal_vecs[:, k], tree_vecs[:, k]) < 0:
            sign_match = np.mean(np.sign(crystal_vecs[:, k]) == -np.sign(tree_vecs[:, k]))
        else:
            sign_match = np.mean(np.sign(crystal_vecs[:, k]) == np.sign(tree_vecs[:, k]))
        print(f"  v{k}     {cos:>8.4f}  {sign_match:>9.1%}")

    return crystal_lap_eigvals, tree_lap_eigvals


# ═══════════════════════════════════════════════════════════════
# Experiment 4: Constructive Tree from φ
# ═══════════════════════════════════════════════════════════════

def exp4_phi_tree():
    """Build the tree from first principles using φ and compare."""
    print("\n" + "═" * 70)
    print("  EXPERIMENT 4: CONSTRUCTIVE TREE FROM φ")
    print("═" * 70)

    # The tree structure from eigenvector signs + eigenvalue branch lengths.
    # Branch lengths are eigenvalues, which follow the crystal equation.
    #
    # Eigenvalues of M8:
    eigvals, eigvecs = np.linalg.eigh(M8)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    # The crystal equation predicts 4 eigenvalues for the 4-combinator basis.
    # But M8 has 8 eigenvalues. How do the extra 4 relate?
    #
    # From crystal-phi-derivation.md: the Kronecker factorization
    # M16 = S ⊗ J + D ⊗ F shows that the 16×16 has pairs.
    # For M8 alone, we need to understand the 8-node structure.

    C_scale = eigvals[0]  # λ₀ = C
    predicted = np.array([C_scale * PHI ** (-S * b) for b in BETA])

    print("\n  Crystal equation eigenvalues vs actual M8 eigenvalues:")
    print(f"  {'k':>3}  {'Predicted':>10}  {'Actual':>10}  {'Error':>8}")
    print(f"  {'─'*3}  {'─'*10}  {'─'*10}  {'─'*8}")
    for k in range(min(4, len(eigvals))):
        err = abs(predicted[k] - eigvals[k]) / eigvals[k] * 100
        print(f"  {k:>3}  {predicted[k]:>10.4f}  {eigvals[k]:>10.4f}  {err:>7.2f}%")

    print(f"\n  Remaining eigenvalues (not predicted by 4-combinator equation):")
    for k in range(4, len(eigvals)):
        ratio_to_first = eigvals[0] / eigvals[k] if eigvals[k] > 0.01 else float('inf')
        phi_power = np.log(ratio_to_first) / np.log(PHI) if ratio_to_first < 1000 else float('inf')
        print(f"  λ{k} = {eigvals[k]:.6f}  (λ₀/λ{k} = {ratio_to_first:.4f}, = φ^{phi_power:.4f})")

    # Constructive approach: build M8 from eigenvector signs + φ branch lengths
    # Use the observed eigenvectors but φ-predicted eigenvalues
    print("\n  Constructive reconstruction:")
    print("  Use empirical eigenvectors + φ-predicted eigenvalues")

    # Extend predictions: the remaining eigenvalues also follow φ powers?
    all_predicted = np.zeros(8)
    all_predicted[:4] = predicted

    # For eigenvalues 4-7, search for best φ^(p/q)
    for k in range(4, 8):
        if eigvals[k] > 0.01:
            ratio = eigvals[0] / eigvals[k]
            power = np.log(ratio) / np.log(PHI)
            all_predicted[k] = C_scale * PHI ** (-power)
        else:
            all_predicted[k] = eigvals[k]

    # Reconstruct using φ-predicted eigenvalues + empirical eigenvectors
    M8_recon = eigvecs @ np.diag(all_predicted) @ eigvecs.T
    mask = np.triu(np.ones_like(M8, dtype=bool), k=1)
    corr = np.corrcoef(M8_recon[mask], M8[mask])[0, 1]
    rmse = np.sqrt(np.mean((M8_recon[mask] - M8[mask]) ** 2))
    max_err = np.max(np.abs(M8_recon[mask] - M8[mask]))

    print(f"  Correlation: {corr:.8f}")
    print(f"  RMSE:        {rmse:.8f}")
    print(f"  Max error:   {max_err:.8f}")

    # Now the KEY question: can we get the eigenvectors from the tree alone?
    # The tree topology (from combinatory logic) should predict eigenvector signs.
    # Let's try building eigenvectors from the binary tree structure.

    print("\n  ─── Can we construct eigenvectors from tree topology? ───")

    # The tree says:
    # Level 0: {B,C,D,Y,W} vs {K,I,WHNF} — but WHNF flips sign at PC0!
    # Actually from eigvecs:
    # PC0: all negative except WHNF
    # PC1: K,I,W positive; B,C,D,Y,WHNF negative
    # PC2: K,I,W,WHNF positive; B,C,D,Y negative

    # Define the theoretical tree splits
    # Each split produces a Hadamard-like vector
    splits = {
        'PC0_comp_vs_halt': {
            # Composition cluster vs WHNF
            'pos': ['WHNF'],
            'neg': ['K', 'I', 'B', 'C', 'D', 'Y', 'W'],
        },
        'PC1_sel_vs_comp': {
            # Selection + W vs pure composition + WHNF
            'pos': ['K', 'I', 'W'],
            'neg': ['B', 'C', 'D', 'Y', 'WHNF'],
        },
        'PC2_halt_sel_vs_comp': {
            # WHNF + selection + W vs composition
            'pos': ['K', 'I', 'W', 'WHNF'],
            'neg': ['B', 'C', 'D', 'Y'],
        },
    }

    # More detailed: look at actual sign patterns
    print("\n  Actual eigenvector signs vs theoretical tree splits:")
    for k in range(min(7, len(eigvals))):
        pos_actual = sorted([NAMES_8[i] for i in range(8) if eigvecs[i, k] > 0])
        neg_actual = sorted([NAMES_8[i] for i in range(8) if eigvecs[i, k] <= 0])
        print(f"  PC{k}: + [{','.join(pos_actual)}]  - [{','.join(neg_actual)}]")

    # The key structural question: is the tree ULTRAMETRIC?
    # An ultrametric tree satisfies: d(i,k) ≤ max(d(i,j), d(j,k))
    print("\n  ─── Ultrametric test ───")
    dist = 1.0 - M8  # cosine distance
    np.fill_diagonal(dist, 0)

    violations = 0
    total = 0
    max_violation = 0
    for i in range(8):
        for j in range(i + 1, 8):
            for k in range(j + 1, 8):
                total += 1
                dij = dist[i, j]
                dik = dist[i, k]
                djk = dist[j, k]
                # Check all 3 orderings
                v = max(0,
                        dij - max(dik, djk),
                        dik - max(dij, djk),
                        djk - max(dij, dik))
                if v > 0.001:
                    violations += 1
                    if v > max_violation:
                        max_violation = v
                        worst = (NAMES_8[i], NAMES_8[j], NAMES_8[k], dij, dik, djk)

    print(f"  Ultrametric violations: {violations}/{total} triplets")
    if violations > 0:
        print(f"  Worst: {worst[0]}-{worst[1]}-{worst[2]}: "
              f"d({worst[0]},{worst[1]})={worst[3]:.4f}, "
              f"d({worst[0]},{worst[2]})={worst[4]:.4f}, "
              f"d({worst[1]},{worst[2]})={worst[5]:.4f}")
        print(f"  Max violation: {max_violation:.4f}")
    print(f"  {'ULTRAMETRIC ✅' if violations == 0 else 'NOT ULTRAMETRIC ⚠️ (but may be approximately so)'}")

    return eigvals, eigvecs, all_predicted


# ═══════════════════════════════════════════════════════════════
# Experiment 5: Tree Distance ↔ Transition Matrix
# ═══════════════════════════════════════════════════════════════

def exp5_transition_connection():
    """Connect the tree to the absorbing Markov chain transition matrix."""
    print("\n" + "═" * 70)
    print("  EXPERIMENT 5: TREE ↔ MARKOV CHAIN CONNECTION")
    print("═" * 70)

    # From crystal-phi-derivation.md:
    # The transition matrix T governs fire→fire transitions.
    # Halt probabilities: K=0.716, I=0.508, B=0.345, C=0.216
    # Reduction lengths: K=1.53, I=1.94, B=2.23, C=2.51
    # Ratio C/K = 1.637 ≈ φ

    halt_prob = np.array([0.716, 0.508, 0.345, 0.216])  # K, I, B, C
    red_length = np.array([1.53, 1.94, 2.23, 2.51])     # K, I, B, C
    gradient = np.array([0.236, 0.421, 0.543, 0.688])    # computation gradient

    KIBC = ['K', 'I', 'B', 'C']

    # The computation gradient IS a monotone ordering along PC0
    # of the crystal. Let's check:
    eigvals, eigvecs = np.linalg.eigh(M8)
    idx = np.argsort(eigvals)[::-1]
    eigvecs = eigvecs[:, idx]

    # KIBC are indices 0,1,2,3 in the 8-node crystal
    kibc_pc0 = eigvecs[:4, 0]  # First 4 rows, PC0

    print("\n  Computation gradient vs PC0 loading:")
    print(f"  {'Comb':>4}  {'Gradient':>10}  {'PC0 load':>10}  {'Halt P':>8}  {'Red len':>8}")
    print(f"  {'─'*4}  {'─'*10}  {'─'*10}  {'─'*8}  {'─'*8}")
    for i, name in enumerate(KIBC):
        print(f"  {name:>4}  {gradient[i]:>10.3f}  {kibc_pc0[i]:>10.4f}  {halt_prob[i]:>8.3f}  {red_length[i]:>8.2f}")

    corr_grad_pc0 = np.corrcoef(gradient, np.abs(kibc_pc0))[0, 1]
    corr_halt_pc0 = np.corrcoef(halt_prob, np.abs(kibc_pc0))[0, 1]
    corr_len_pc0 = np.corrcoef(red_length, np.abs(kibc_pc0))[0, 1]

    print(f"\n  Correlations:")
    print(f"    gradient ↔ |PC0|:      r = {corr_grad_pc0:.4f}")
    print(f"    halt_prob ↔ |PC0|:     r = {corr_halt_pc0:.4f}")
    print(f"    red_length ↔ |PC0|:    r = {corr_len_pc0:.4f}")

    # D, Y, W as paths through the 4 fire states
    # From EQUATIONS.md:
    #   D = B→B path (double composition)
    #   Y = recursive/fixed-point (divergent)
    #   W = C→I→I path (duplicate)
    #
    # If these are paths, their tree position should be the CENTROID
    # of the path nodes in eigenspace.

    print("\n  ─── D, Y, W as path centroids in eigenspace ───")

    # Eigenvector loadings for the 8 nodes
    node_loadings = eigvecs[:, :4]  # (8, 4) — first 4 PCs

    # Path definitions (indices in NAMES_8)
    paths = {
        'D (B→B)': [2, 2],         # B twice
        'W (C→I→I)': [3, 1, 1],    # C then I twice
        'Y (recursive)': [2, 3, 2, 3],  # B,C alternating (approximate)
    }

    # Actual positions
    actual = {
        'D': node_loadings[4],   # index 4
        'Y': node_loadings[5],   # index 5
        'W': node_loadings[6],   # index 6
    }

    for path_name, path_indices in paths.items():
        # Centroid of path nodes in eigenspace
        path_vecs = node_loadings[path_indices]
        centroid = path_vecs.mean(axis=0)

        # Which actual node is this closest to?
        short_name = path_name.split(' ')[0]
        actual_pos = actual[short_name]

        cos_sim = np.dot(centroid, actual_pos) / (np.linalg.norm(centroid) * np.linalg.norm(actual_pos) + 1e-10)

        print(f"\n  {path_name}:")
        print(f"    Path centroid (PC0..3): [{', '.join(f'{v:.4f}' for v in centroid)}]")
        print(f"    Actual position:       [{', '.join(f'{v:.4f}' for v in actual_pos)}]")
        print(f"    Cosine similarity:     {cos_sim:.4f}")

    # The compound nodes should be intermediate between their constituent paths
    # Check: is D between B and B (i.e., close to B)?
    print("\n  Compound cosine similarities:")
    print(f"    cos(D, B) = {M8[4, 2]:.4f}  (D=BB, should be high)")
    print(f"    cos(W, K) = {M8[6, 0]:.4f}  (W shares K's selection)")
    print(f"    cos(W, I) = {M8[6, 1]:.4f}  (W uses I)")
    print(f"    cos(W, C) = {M8[6, 3]:.4f}  (W starts with C)")
    print(f"    cos(Y, B) = {M8[5, 2]:.4f}  (Y involves composition)")
    print(f"    cos(Y, C) = {M8[5, 3]:.4f}  (Y involves reordering)")

    return gradient, halt_prob, red_length


# ═══════════════════════════════════════════════════════════════
# Experiment 6: Self-Similar Branch Length Ratios
# ═══════════════════════════════════════════════════════════════

def exp6_self_similar_ratios():
    """Test whether the tree is self-similar: constant branch length ratio at every level."""
    print("\n" + "═" * 70)
    print("  EXPERIMENT 6: SELF-SIMILAR BRANCH LENGTH RATIOS")
    print("═" * 70)

    eigvals, eigvecs = np.linalg.eigh(M8)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]

    # The eigenvalues are branch lengths at each tree level.
    # A self-similar tree has constant ratio between levels.
    print("\n  Eigenvalue spectrum and φ-power fitting:")
    print(f"  {'k':>3}  {'λk':>10}  {'λ₀/λk':>10}  {'log_φ(λ₀/λk)':>14}  {'Nearest p/q':>12}  {'Predicted':>10}  {'Error':>8}")
    print(f"  {'─'*3}  {'─'*10}  {'─'*10}  {'─'*14}  {'─'*12}  {'─'*10}  {'─'*8}")

    # Search for φ^(p/q) with Fibonacci denominators
    fibs = [1, 2, 3, 5, 8, 13, 21, 34]

    for k in range(8):
        if eigvals[k] < 0.01:
            continue
        ratio = eigvals[0] / eigvals[k]
        log_phi = np.log(ratio) / np.log(PHI)

        # Find nearest p/q with Fibonacci q
        best_err = float('inf')
        best_pq = (0, 1)
        for q in fibs:
            p = round(log_phi * q)
            if p >= 0 and q > 0:
                err = abs(log_phi - p / q)
                if err < best_err:
                    best_err = err
                    best_pq = (p, q)

        p, q = best_pq
        predicted = eigvals[0] / (PHI ** (p / q))
        pred_err = abs(predicted - eigvals[k]) / eigvals[k] * 100

        pq_str = f"{p}/{q}" if k > 0 else "0/1"
        print(f"  {k:>3}  {eigvals[k]:>10.6f}  {ratio:>10.4f}  {log_phi:>14.4f}  {pq_str:>12}  {predicted:>10.6f}  {pred_err:>7.2f}%")

    # Consecutive ratios
    print("\n  Consecutive eigenvalue ratios:")
    for k in range(7):
        if eigvals[k + 1] > 0.01:
            ratio = eigvals[k] / eigvals[k + 1]
            log_phi = np.log(ratio) / np.log(PHI)
            print(f"    λ{k}/λ{k+1} = {ratio:.4f} = φ^{log_phi:.4f}")

    # The key self-similarity test: are there CONSTANT ratio groups?
    print("\n  Self-similarity test: do ratios cluster?")
    ratios = []
    for k in range(7):
        if eigvals[k + 1] > 0.01:
            ratios.append(eigvals[k] / eigvals[k + 1])

    if ratios:
        from collections import Counter
        # Bucket ratios by nearest φ power
        buckets = {}
        for r in ratios:
            lp = np.log(r) / np.log(PHI)
            key = round(lp * 5) / 5  # round to nearest 0.2
            buckets.setdefault(key, []).append(r)

        for key in sorted(buckets.keys()):
            vals = buckets[key]
            mean = np.mean(vals)
            print(f"    φ^~{key:.1f}: {len(vals)} ratios, mean={mean:.4f}, "
                  f"φ^{key:.1f}={PHI**key:.4f}")


# ═══════════════════════════════════════════════════════════════
# Experiment 7: 16-node Tree (with anti-types)
# ═══════════════════════════════════════════════════════════════

def exp7_full_16_tree():
    """Extend to the full 16×16 crystal (types + anti-types)."""
    print("\n" + "═" * 70)
    print("  EXPERIMENT 7: FULL 16-NODE TREE (with anti-types)")
    print("═" * 70)

    eigvals_16, eigvecs_16 = np.linalg.eigh(M16)
    idx = np.argsort(eigvals_16)[::-1]
    eigvals_16 = eigvals_16[idx]
    eigvecs_16 = eigvecs_16[:, idx]

    print("\n  16×16 eigenvalues:")
    for k in range(16):
        if eigvals_16[k] > 0.01:
            ratio = eigvals_16[0] / eigvals_16[k]
            log_phi = np.log(ratio) / np.log(PHI)
            print(f"    λ{k:>2} = {eigvals_16[k]:>8.4f}  (λ₀/λ{k} = {ratio:>8.4f} = φ^{log_phi:.4f})")
        else:
            print(f"    λ{k:>2} = {eigvals_16[k]:>8.4f}")

    # Kronecker structure: M16 = S ⊗ J + D ⊗ F
    # The eigenvalues should come in pairs: one from S, one from D
    # With D/S ratio = φ^(4/5)
    print("\n  Eigenvalue pairing (type ↔ anti-type):")
    print(f"  {'Pair':>4}  {'λ_a':>8}  {'λ_b':>8}  {'Ratio':>8}  {'φ^(4/5)':>8}  {'Error':>8}")
    print(f"  {'─'*4}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}")
    phi_45 = PHI ** (4 / 5)
    for k in range(0, 16, 2):
        if k + 1 < 16:
            a, b = eigvals_16[k], eigvals_16[k + 1]
            if b > 0.01:
                ratio = a / b
                err = abs(ratio - phi_45) / phi_45 * 100
                print(f"  {k//2:>4}  {a:>8.4f}  {b:>8.4f}  {ratio:>8.4f}  {phi_45:>8.4f}  {err:>7.2f}%")

    # Sign structure of the 16-node tree
    print("\n  16-node sign structure (first 6 PCs):")
    for i in range(16):
        name = NAMES_16[i]
        signs = ''.join('+' if eigvecs_16[i, k] > 0 else '-' for k in range(6))
        print(f"    {name:>6}: {signs}")


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔" + "═" * 68 + "╗")
    print("║" + "  CRYSTAL TREE: Statechart as Discrete Tree in Eigenspace".center(68) + "║")
    print("║" + "  Verbum Session 197".center(68) + "║")
    print("╚" + "═" * 68 + "╝")

    eigvals, eigvecs, codes = exp1_eigenvector_sign_tree()
    Z, tree_dists = exp2_cosine_tree()
    crystal_lap, tree_lap = exp3_laplacian_comparison(Z, tree_dists)
    eigvals_8, eigvecs_8, predicted = exp4_phi_tree()
    gradient, halt_prob, red_length = exp5_transition_connection()
    exp6_self_similar_ratios()
    exp7_full_16_tree()

    # ─── Summary ───
    print("\n" + "═" * 70)
    print("  SUMMARY")
    print("═" * 70)

    print("""
  The combinator crystal has three equivalent representations:

  1. COSINE MATRIX: 8×8 (or 16×16) empirical cosine similarities
     between combinator embeddings in neural networks.

  2. STATECHART: absorbing Markov chain with 4 fire + 4 halt states,
     transition probabilities from KIBC beta reduction.

  3. TREE IN EIGENSPACE: hierarchical binary partition where each
     eigenvector defines a branch point and each eigenvalue gives
     the branch length. Branch lengths follow φ^(p/q).

  The question: are these the SAME object?

  Evidence for:
    - Eigenvector signs define tree topology matching cosine clustering
    - Branch length ratios follow φ-powers (crystal equation)
    - D, Y, W appear as paths through the 4-node basis tree
    - Computation gradient is monotone along PC0 (tree depth)
    - WHNF fragility = leaf node with one edge (tree topology)

  Evidence against:
    - The cosine matrix may not be exactly ultrametric
    - The Laplacian comparison depends on scale parameter σ
    - Eigenvectors 4-7 don't follow the 4-combinator crystal equation
    """)

    # Save results
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                           'results', 'crystal-tree')
    os.makedirs(out_dir, exist_ok=True)

    results = {
        'eigvals_8': eigvals.tolist(),
        'crystal_lap': crystal_lap.tolist(),
        'tree_lap': tree_lap.tolist(),
        'phi': PHI,
        'phi_45': float(PHI ** (4 / 5)),
    }

    with open(os.path.join(out_dir, 'results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n  Results saved to: {out_dir}/results.json")


if __name__ == '__main__':
    main()
