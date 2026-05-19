"""Crystal Self-Similarity — Extract unit cell from a big teacher model.

Loads weight tensors shard-by-shard (never the full model), extracts
sign patterns of K/V/O attention projections, decomposes into per-head
blocks, and tests for self-similarity across layers.

If self-similar:
  - The same d_head × d_head sign pattern appears at every layer
  - The "unit cell" = the consensus sign pattern across all layers
  - This is the crystal seed

Pure safetensors + numpy. No model loading, no inference, no GPU.

License: MIT
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

try:
    from safetensors import safe_open
except ImportError:
    print("pip install safetensors")
    sys.exit(1)


# ── Config ────────────────────────────────────────────────────────

QWEN3_14B_PATH = Path.home() / ".cache/huggingface/hub/models--Qwen--Qwen3-14B/snapshots/40c069824f4251a91eefaf281ebe4c544efd3e18"

MODEL_CONFIG = {
    "name": "Qwen3-14B",
    "hidden_size": 5120,
    "num_hidden_layers": 40,
    "num_attention_heads": 40,
    "num_key_value_heads": 8,
    "head_dim": 128,
}


# ── Utilities ────────────────────────────────────────────────────

def cosine_matrix(vecs: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-10
    normed = vecs / norms
    return normed @ normed.T


def upper_triangle(matrix: np.ndarray) -> np.ndarray:
    n = matrix.shape[0]
    idx = np.triu_indices(n, k=1)
    return matrix[idx]


def check_power_law(sv: np.ndarray) -> dict:
    S = sv[sv > 1e-10]
    n = len(S)
    if n < 3:
        return {"alpha": 0.0, "r_squared": 0.0}
    log_k = np.log(np.arange(1, n + 1))
    log_s = np.log(S)
    A = np.vstack([log_k, np.ones(n)]).T
    result = np.linalg.lstsq(A, log_s, rcond=None)
    slope, intercept = result[0]
    predicted = slope * log_k + intercept
    ss_res = ((log_s - predicted) ** 2).sum()
    ss_tot = ((log_s - log_s.mean()) ** 2).sum()
    r_squared = 1 - ss_res / (ss_tot + 1e-10)
    return {"alpha": float(-slope), "r_squared": float(r_squared)}


# ── Weight Loading ───────────────────────────────────────────────

def load_tensor_from_shards(model_path: Path, tensor_name: str) -> np.ndarray:
    """Load a single tensor from sharded safetensors files.

    Reads the index to find which shard contains the tensor,
    then loads only that shard. Memory-efficient.
    """
    index_path = model_path / "model.safetensors.index.json"
    with open(index_path) as f:
        index = json.load(f)

    shard_name = index["weight_map"][tensor_name]
    shard_path = model_path / shard_name

    # Use torch framework to handle bfloat16 → float32 conversion
    with safe_open(str(shard_path), framework="pt") as f:
        tensor = f.get_tensor(tensor_name).float().numpy()

    return tensor


def extract_sign_pattern(weight: np.ndarray) -> np.ndarray:
    """Extract ternary sign pattern from a weight matrix.

    Big models have float16/bfloat16 weights. np.sign gives {-1, 0, +1}.
    In practice, very few weights are exactly 0 in a trained model.
    """
    signs = np.sign(weight).astype(np.int8)
    return signs


# ── Per-Head Decomposition ───────────────────────────────────────

def decompose_into_heads(
    weight: np.ndarray,
    n_heads: int,
    head_dim: int,
) -> list[np.ndarray]:
    """Decompose a (n_heads * head_dim, d_model) weight into per-head blocks.

    Each head's block is (head_dim, d_model). We further decompose the
    d_model axis into head_dim chunks if d_model is a multiple of head_dim.

    Returns list of n_heads arrays, each (head_dim, d_model).
    """
    out_dim, in_dim = weight.shape
    expected = n_heads * head_dim
    assert out_dim == expected, f"Expected {expected}, got {out_dim}"

    heads = []
    for h in range(n_heads):
        start = h * head_dim
        end = start + head_dim
        heads.append(weight[start:end, :])

    return heads


def head_block_geometry(
    head_weight: np.ndarray,
    head_dim: int,
) -> np.ndarray:
    """Compute the d_head × d_head sign geometry of one head block.

    head_weight is (head_dim, d_model). We want the (head_dim, head_dim)
    sign pattern that characterizes this head.

    Method: reshape d_model into chunks of head_dim, take sign, average
    across chunks, then sign of the average.

    This extracts the self-similar unit cell from one head's weight.
    """
    hd, d_model = head_weight.shape
    assert hd == head_dim

    n_chunks = d_model // head_dim
    # Reshape: (head_dim, n_chunks, head_dim)
    chunks = head_weight[:, :n_chunks * head_dim].reshape(hd, n_chunks, head_dim)
    # Sign of each chunk
    sign_chunks = np.sign(chunks)
    # Accumulate signs across chunks (majority vote)
    sign_sum = sign_chunks.sum(axis=1)  # (head_dim, head_dim)
    # Sign of the sum = majority vote
    unit_cell = np.sign(sign_sum).astype(np.int8)

    return unit_cell


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  CRYSTAL SELF-SIMILARITY — TEACHER MODEL")
    print(f"  {MODEL_CONFIG['name']}")
    print("=" * 70)

    model_path = QWEN3_14B_PATH
    n_layers = MODEL_CONFIG["num_hidden_layers"]
    n_heads = MODEL_CONFIG["num_attention_heads"]
    n_kv_heads = MODEL_CONFIG["num_key_value_heads"]
    head_dim = MODEL_CONFIG["head_dim"]
    d_model = MODEL_CONFIG["hidden_size"]

    print(f"\n  d_model={d_model}, d_head={head_dim}, "
          f"n_heads={n_heads}, n_kv_heads={n_kv_heads}, n_layers={n_layers}")
    print(f"  Unit cell size: {head_dim}×{head_dim} = {head_dim**2} positions")

    # ================================================================
    # 1. Extract sign patterns and unit cells per layer
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  1. EXTRACT — Sign patterns per layer (V and O projections)")
    print(f"{'=' * 70}")

    # We focus on V (KV head) and O (full head) projections
    # V: (n_kv_heads * head_dim, d_model) = (1024, 5120)
    # O: (d_model, n_heads * head_dim) = (5120, 5120)

    layer_unit_cells = {"V": [], "O": []}

    for layer_idx in range(n_layers):
        # V projection
        v_name = f"model.layers.{layer_idx}.self_attn.v_proj.weight"
        v_weight = load_tensor_from_shards(model_path, v_name)
        v_signs = extract_sign_pattern(v_weight)

        # V has n_kv_heads heads
        v_heads = decompose_into_heads(v_signs, n_kv_heads, head_dim)
        # Unit cell per head, then average across heads
        v_cells = [head_block_geometry(h, head_dim) for h in v_heads]
        # Majority vote across KV heads
        v_consensus = np.sign(np.stack(v_cells).sum(axis=0)).astype(np.int8)
        layer_unit_cells["V"].append(v_consensus)

        # O projection: (d_model, d_model) but output dim is n_heads*head_dim
        o_name = f"model.layers.{layer_idx}.self_attn.o_proj.weight"
        o_weight = load_tensor_from_shards(model_path, o_name)
        o_signs = extract_sign_pattern(o_weight)

        # O: (d_model, d_model) — output dim has d_model, input has n_heads*head_dim
        # Transpose so rows = heads: (n_heads*head_dim, d_model)
        o_heads = decompose_into_heads(o_signs.T, n_heads, head_dim)
        o_cells = [head_block_geometry(h, head_dim) for h in o_heads]
        o_consensus = np.sign(np.stack(o_cells).sum(axis=0)).astype(np.int8)
        layer_unit_cells["O"].append(o_consensus)

        # Free memory
        del v_weight, v_signs, v_heads, v_cells
        del o_weight, o_signs, o_heads, o_cells

        if layer_idx % 10 == 0 or layer_idx == n_layers - 1:
            print(f"  Layer {layer_idx:>2d}: V zeros={np.sum(v_consensus==0):>5d}/{head_dim**2}  "
                  f"O zeros={np.sum(o_consensus==0):>5d}/{head_dim**2}")

    # ================================================================
    # 2. Self-similarity: cross-layer correlation
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  2. SELF-SIMILARITY — Cross-layer unit cell correlation")
    print(f"{'=' * 70}")

    for ptype in ["V", "O"]:
        cells = layer_unit_cells[ptype]
        n = len(cells)

        # Flatten unit cells for correlation
        flat = np.array([c.ravel().astype(np.float32) for c in cells])  # (n_layers, head_dim^2)

        # Correlation matrix
        corr = np.corrcoef(flat)  # (n_layers, n_layers)

        # Summary stats
        mask = ~np.eye(n, dtype=bool)
        avg_corr = corr[mask].mean()
        min_corr = corr[mask].min()
        max_corr = corr[mask].max()

        print(f"\n  {ptype}-projection unit cells:")
        print(f"    Average cross-layer correlation: {avg_corr:.4f}")
        print(f"    Min: {min_corr:.4f}, Max: {max_corr:.4f}")

        # Show correlation for selected layer pairs
        for i, j in [(0, 1), (0, 20), (0, 39), (10, 30), (19, 20)]:
            if i < n and j < n:
                print(f"    L{i:>2d}↔L{j:>2d}: {corr[i,j]:.4f}")

        # Correlation heatmap (sampled)
        sample_layers = [0, 5, 10, 15, 20, 25, 30, 35, 39]
        sample_layers = [l for l in sample_layers if l < n]
        print(f"\n    Correlation matrix (sampled layers):")
        print(f"    {'':>4s}  " + "  ".join(f"L{l:>2d}" for l in sample_layers))
        for i in sample_layers:
            row = "  ".join(f"{corr[i,j]:.2f}" for j in sample_layers)
            print(f"    L{i:>2d}  {row}")

    # ================================================================
    # 3. Extract the consensus unit cell (average across all layers)
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  3. UNIT CELL — Consensus across all layers")
    print(f"{'=' * 70}")

    for ptype in ["V", "O"]:
        cells = layer_unit_cells[ptype]
        stack = np.stack(cells).astype(np.float32)  # (n_layers, head_dim, head_dim)

        # Majority vote across layers
        vote = stack.sum(axis=0)  # (head_dim, head_dim)
        consensus = np.sign(vote).astype(np.int8)

        # Confidence: what fraction of layers agree?
        agreement = np.abs(vote) / n_layers
        confident = (agreement > 0.6).mean()
        very_confident = (agreement > 0.8).mean()
        unanimous = (agreement == 1.0).mean()

        n_pos = (consensus == 1).sum()
        n_neg = (consensus == -1).sum()
        n_zero = (consensus == 0).sum()

        print(f"\n  {ptype} unit cell ({head_dim}×{head_dim}):")
        print(f"    +1: {n_pos} ({n_pos/consensus.size:.1%})")
        print(f"    -1: {n_neg} ({n_neg/consensus.size:.1%})")
        print(f"     0: {n_zero} ({n_zero/consensus.size:.1%}) (layers disagree)")
        print(f"    >60% agreement: {confident:.1%}")
        print(f"    >80% agreement: {very_confident:.1%}")
        print(f"    Unanimous:      {unanimous:.1%}")

        # SVD of the consensus unit cell
        _, S, _ = np.linalg.svd(consensus.astype(np.float32))
        pl = check_power_law(S)
        eff_rank = (S.sum()**2) / ((S**2).sum() + 1e-10)
        print(f"    SVD: eff_rank={eff_rank:.1f}  "
              f"SV=[{', '.join(f'{s:.1f}' for s in S[:8])}]")
        print(f"    Power law: α={pl['alpha']:.3f}  R²={pl['r_squared']:.3f}")

        # Save the unit cell
        layer_unit_cells[f"{ptype}_consensus"] = consensus
        layer_unit_cells[f"{ptype}_agreement"] = agreement

    # ================================================================
    # 4. Sign balance and structure
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  4. STRUCTURE — Sign balance per layer")
    print(f"{'=' * 70}")

    for ptype in ["V", "O"]:
        cells = layer_unit_cells[ptype]
        print(f"\n  {ptype} sign balance across layers:")
        print(f"    {'Layer':>5s}  {'%+1':>5s}  {'%-1':>5s}  {'%0':>5s}  "
              f"{'corr_w_consensus':>18s}")

        consensus = layer_unit_cells[f"{ptype}_consensus"]
        cons_flat = consensus.ravel().astype(np.float32)

        for i, cell in enumerate(cells):
            flat = cell.ravel().astype(np.float32)
            pos = (cell == 1).mean()
            neg = (cell == -1).mean()
            zero = (cell == 0).mean()
            r = np.corrcoef(flat, cons_flat)[0, 1]
            if i % 5 == 0 or i == len(cells) - 1:
                print(f"    L{i:>3d}  {pos:>5.1%}  {neg:>5.1%}  {zero:>5.1%}  {r:>18.4f}")

    # ================================================================
    # Save
    # ================================================================
    out_path = Path("results/crystal-selfsim-teacher")
    out_path.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        out_path / "unit_cells.npz",
        V_consensus=layer_unit_cells["V_consensus"],
        V_agreement=layer_unit_cells["V_agreement"],
        O_consensus=layer_unit_cells["O_consensus"],
        O_agreement=layer_unit_cells["O_agreement"],
        **{f"V_layer_{i}": c for i, c in enumerate(layer_unit_cells["V"])},
        **{f"O_layer_{i}": c for i, c in enumerate(layer_unit_cells["O"])},
    )

    print(f"\n  Unit cells saved to {out_path}/unit_cells.npz")
    print(f"\n{'=' * 70}")
    print("  DONE")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
