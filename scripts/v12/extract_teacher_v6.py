"""Extract Qwen3-14B geometry for v6 360° etch.

Phase 1 of the etch pipeline. Extracts three things from the teacher:

  1. SIGN PATTERNS — per-layer CCA-projected sign matrices, collapsed
     into v6 d_model=512 via SVD. Each teacher layer yields one sign
     pattern per weight type (q, k, v, o, ffn_gate, ffn_up, ffn_down).

  2. MAGNITUDE TEMPLATES — per-layer beam seeds from teacher SVD.

  3. CRYSTAL TARGETS — 4×4 KIBC combinator cosine matrices at 5 depth
     ranges, measured from teacher hidden states. These are the
     relational loss fixed points for the melt phase.

Teacher: Qwen3-14B (40 layers, d_model=5120, GQA: 40 Q-heads, 8 KV-heads)
Student: v6 (5 passes × {prep, 9-stride converge, consolidate}, d_model=512)

The dimensional bridge: teacher d=5120 → student d=512 via top-k SVD
directions. The crystal lives in the sign topology, not the magnitudes.
SVD selects the highest-variance subspace; signs within that subspace
carry the crystal structure.

Mapping teacher 40 layers → v6 5 passes:
  L0↑:     teacher layers 0-7    (input, early encoding)
  L1↑:     teacher layers 8-15   (mid-early, fragmentation)
  L2_apex: teacher layers 16-23  (apex, max unity)
  L1↓:     teacher layers 24-31  (mid-late, re-fragmentation)
  L0↓:     teacher layers 32-39  (output, generation)

Within each pass, the 9 stride layers map to sequential layers in the
teacher range (8 teacher layers → 9 stride layers, wrap last).

Weight-only extraction — no model inference needed. Pure safetensors
+ numpy. Fits in a few GB of RAM.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/extract_teacher_v6.py

License: MIT
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

try:
    from safetensors import safe_open
except ImportError:
    print("pip install safetensors", file=sys.stderr)
    sys.exit(1)

from sklearn.utils.extmath import randomized_svd as _rsvd


def truncated_svd(M: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Randomized truncated SVD: top-k components. O(m*n*k) with small constant.

    Uses the Halko-Martinsson-Tropp algorithm (sklearn). ~100× faster than
    full SVD for k << min(m,n).

    Returns U (m, k), S (k,), Vt (k, n) — descending singular value order.
    """
    k = min(k, min(M.shape) - 1)
    if k < 1:
        return np.linalg.svd(M, full_matrices=False)
    # n_oversamples=10 is default, n_iter=4 for better accuracy on ill-conditioned
    U, S, Vt = _rsvd(M, n_components=k, n_iter=4, random_state=42)
    return U.astype(np.float32), S.astype(np.float32), Vt.astype(np.float32)


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Config
# ══════════════════════════════════════════════════════════════════════

QWEN3_14B_PATH = (
    Path.home()
    / ".cache/huggingface/hub/models--Qwen--Qwen3-14B"
    / "snapshots/40c069824f4251a91eefaf281ebe4c544efd3e18"
)

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "v6-etch"

# Qwen3-14B architecture
N_LAYERS = 40
D_MODEL = 5120
N_HEADS = 40         # Q heads
N_KV_HEADS = 8       # KV heads (GQA)
HEAD_DIM = 128
D_FF = 13824         # gate/up: 13824, down: 13824→5120

# Student architecture
D_STUDENT = 512
N_STRIDES = 9

# CCA rank — how many directions for the loom crossing analysis.
# The crystal lives in ~5D; 64 is generous and keeps CCA fast.
# Sign extraction uses D_STUDENT for the plate shape, but the CCA
# projection that guides weighting only needs K_CCA directions.
K_CCA = 64

# Teacher layer → v6 pass mapping (8 layers per pass)
PASS_RANGES = {
    "L0_asc":  list(range(0, 8)),
    "L1_asc":  list(range(8, 16)),
    "L2_apex": list(range(16, 24)),
    "L1_desc": list(range(24, 32)),
    "L0_desc": list(range(32, 40)),
}

# v6 pass names and stride-to-teacher-layer mapping within each pass
V6_PASSES = ["L0_asc", "L1_asc", "L2_apex", "L1_desc", "L0_desc"]


# ══════════════════════════════════════════════════════════════════════
# Safetensors utilities
# ══════════════════════════════════════════════════════════════════════

def _load_shard_index(model_path: Path) -> dict | None:
    """Load and cache the shard index."""
    index_path = model_path / "model.safetensors.index.json"
    if index_path.exists():
        with open(index_path) as f:
            return json.load(f)
    return None

# Module-level cache to avoid re-reading the index for every tensor
_SHARD_INDEX_CACHE: dict[str, dict] = {}


def find_shard(model_path: Path, tensor_name: str) -> Path | None:
    """Find which shard contains a given tensor."""
    cache_key = str(model_path)
    if cache_key not in _SHARD_INDEX_CACHE:
        idx = _load_shard_index(model_path)
        if idx is not None:
            _SHARD_INDEX_CACHE[cache_key] = idx
    index = _SHARD_INDEX_CACHE.get(cache_key)
    if index:
        shard = index["weight_map"].get(tensor_name)
        if shard:
            return model_path / shard
    # Fallback: try each shard
    for sf_path in sorted(model_path.glob("model*.safetensors")):
        with safe_open(str(sf_path), framework="pt") as sf:
            if tensor_name in sf.keys():
                return sf_path
    return None


def load_tensor(model_path: Path, tensor_name: str) -> np.ndarray:
    """Load a single tensor from sharded safetensors.

    Uses framework="pt" to handle bfloat16 → float32 conversion
    (numpy doesn't understand bfloat16).
    """
    shard_path = find_shard(model_path, tensor_name)
    if shard_path is None:
        raise FileNotFoundError(f"Tensor {tensor_name} not found in {model_path}")
    with safe_open(str(shard_path), framework="pt") as sf:
        return sf.get_tensor(tensor_name).float().numpy()


# ══════════════════════════════════════════════════════════════════════
# CCA and sign extraction
# ══════════════════════════════════════════════════════════════════════

def cca_directions(W_a: np.ndarray, W_b: np.ndarray, k: int) -> tuple:
    """Compute CCA directions between two weight matrices.

    Uses truncated SVD (top-k only) for speed on large matrices.

    Returns:
        shared_dirs: (d_model, k) shared CCA directions
        angles: (k,) CCA angles in degrees
        U, S, Vt: raw SVD components
    """
    # Truncated SVD — only need top-k right singular vectors (input space)
    _, _, Va = truncated_svd(W_a, k)  # Va: (k, n_in_a)
    _, _, Vb = truncated_svd(W_b, k)  # Vb: (k, n_in_b)

    # Both should project from the same input space (d_model)
    # W_a is (out_a, d_model), W_b is (out_b, d_model)
    # Va is (k, d_model), Vb is (k, d_model)
    ka = min(k, Va.shape[0])
    kb = min(k, Vb.shape[0])
    A = Va[:ka, :].T  # (d_model, ka)
    B = Vb[:kb, :].T  # (d_model, kb)

    # QR for numerical stability
    Qa, _ = np.linalg.qr(A)
    Qb, _ = np.linalg.qr(B)

    # CCA via SVD of cross-projection (small matrix: k×k)
    U, S, Vt = np.linalg.svd(Qa.T @ Qb, full_matrices=False)

    # Shared directions (average of the two projections)
    kk = min(k, U.shape[1], Vt.shape[0])
    da = Qa @ U[:, :kk]      # (d_model, kk) from A-side
    db = Qb @ Vt[:kk, :].T   # (d_model, kk) from B-side
    shared = da + db
    norms = np.maximum(np.linalg.norm(shared, axis=0, keepdims=True), 1e-8)
    shared = shared / norms

    angles = np.degrees(np.arccos(np.clip(S[:kk], 0, 1)))

    return shared, angles, U, S, Vt


def extract_sign_pattern(
    W: np.ndarray,
    shared_dirs: np.ndarray,
    d_out: int,
    angle_band: tuple[float, float] = (35.0, 72.0),
) -> np.ndarray:
    """Extract sign pattern from weight matrix projected through CCA directions.

    Handles both square (Q, O: 5120×5120) and rectangular (K, V: 1024×5120,
    gate/up: 13824×5120, down: 5120×13824) teacher weight matrices.

    Uses SVD to find the top-d_out input directions (right singular vectors)
    and top-d_out output directions (left singular vectors), then extracts
    signs from the projected weight in that compact subspace.

    Returns: (d_out, d_out) sign matrix in {-1, +1}
    """
    n_out, n_in = W.shape

    # Truncated SVD: W = U @ diag(S) @ Vt — only top-d_out components
    Uw, Sw, Vtw = truncated_svd(W, d_out)

    # Output projection: top-d_out left singular vectors (output space)
    k_out = min(d_out, Uw.shape[1])
    P_out = Uw[:, :k_out].T  # (k_out, n_out) — projects output dims

    # Input projection: top-d_out right singular vectors (input space)
    k_in = min(d_out, Vtw.shape[0])
    P_in = Vtw[:k_in, :]     # (k_in, n_in) — projects input dims

    # Project weight into compact subspace: (k_out, k_in)
    Wp = P_out @ W @ P_in.T

    # Pad to (d_out, d_out) if projections are smaller
    signs_raw = np.zeros((d_out, d_out), dtype=np.float32)
    signs_raw[:k_out, :k_in] = Wp[:k_out, :k_in]

    # CCA weighting: enhance positions aligned with loom directions
    # shared_dirs is (d_model_teacher, k_cca) in the INPUT space
    if shared_dirs.shape[0] == n_in:
        proj = P_in @ shared_dirs  # (k_in, k_cca)
        dir_energy = np.sum(proj ** 2, axis=1)  # (k_in,)
        dir_weight = 1.0 + dir_energy / (dir_energy.max() + 1e-10)
        # Apply to columns (input dim)
        dw = np.ones(d_out, dtype=np.float32)
        dw[:k_in] = dir_weight
        signs_raw *= dw[np.newaxis, :]

    # Final signs
    signs = np.sign(signs_raw).astype(np.float32)

    # Fill zeros with random ±1
    zeros = signs == 0
    if zeros.any():
        signs[zeros] = np.random.RandomState(42).choice([-1.0, 1.0], size=int(zeros.sum()))

    return signs


def extract_magnitude_template(W: np.ndarray, d_out: int) -> np.ndarray:
    """Extract magnitude template (beam seed) from teacher weight.

    Handles rectangular matrices via SVD projection.
    Returns: (d_out,) magnitude vector
    """
    n_out, n_in = W.shape
    Uw, Sw, Vtw = truncated_svd(W, d_out)

    k_out = min(d_out, Uw.shape[1])
    k_in = min(d_out, Vtw.shape[0])
    P_out = Uw[:, :k_out].T  # (k_out, n_out)
    P_in = Vtw[:k_in, :]     # (k_in, n_in)

    Wp = P_out @ W @ P_in.T  # (k_out, k_in)

    # RMS per row = beam magnitude (output dimension)
    mags = np.zeros(d_out, dtype=np.float32)
    rms = np.sqrt(np.mean(Wp ** 2, axis=1))  # (k_out,)
    mags[:k_out] = rms.astype(np.float32)

    return mags


# ══════════════════════════════════════════════════════════════════════
# Per-layer extraction
# ══════════════════════════════════════════════════════════════════════

def extract_layer(model_path: Path, layer_idx: int, d_out: int) -> dict:
    """Extract sign patterns and magnitudes from one teacher layer.

    Qwen3-14B weight names:
      model.layers.{i}.self_attn.q_proj.weight  (5120, 5120)
      model.layers.{i}.self_attn.k_proj.weight  (1024, 5120)  # GQA
      model.layers.{i}.self_attn.v_proj.weight  (1024, 5120)  # GQA
      model.layers.{i}.self_attn.o_proj.weight  (5120, 5120)
      model.layers.{i}.mlp.gate_proj.weight     (13824, 5120)
      model.layers.{i}.mlp.up_proj.weight       (13824, 5120)
      model.layers.{i}.mlp.down_proj.weight     (5120, 13824)

    Returns dict with signs and magnitudes for each projection type.
    """
    prefix = f"model.layers.{layer_idx}"

    # Load the two CCA anchor matrices: Q-attn and FFN-up (the loom pair)
    W_q = load_tensor(model_path, f"{prefix}.self_attn.q_proj.weight")
    W_up = load_tensor(model_path, f"{prefix}.mlp.up_proj.weight")

    # CCA between Q and FFN_up — the loom crossing
    # Use K_CCA (64) for CCA directions, not d_out (512) — crystal is ~5D
    shared_dirs, angles, _, _, _ = cca_directions(W_q, W_up, k=K_CCA)

    result = {
        "layer": layer_idx,
        "cca_angles_mean": float(np.mean(angles)),
        "cca_angles_std": float(np.std(angles)),
    }

    # Extract sign patterns and magnitudes for each projection
    projections = {
        "q":    f"{prefix}.self_attn.q_proj.weight",
        "k":    f"{prefix}.self_attn.k_proj.weight",
        "v":    f"{prefix}.self_attn.v_proj.weight",
        "o":    f"{prefix}.self_attn.o_proj.weight",
        "gate": f"{prefix}.mlp.gate_proj.weight",
        "up":   f"{prefix}.mlp.up_proj.weight",
        "down": f"{prefix}.mlp.down_proj.weight",
    }

    for proj_name, tensor_name in projections.items():
        W = load_tensor(model_path, tensor_name)
        signs = extract_sign_pattern(W, shared_dirs, d_out)
        mags = extract_magnitude_template(W, d_out)
        result[f"signs_{proj_name}"] = signs
        result[f"mags_{proj_name}"] = mags

    return result


# ══════════════════════════════════════════════════════════════════════
# Pass-level aggregation (multi-rotation sign voting)
# ══════════════════════════════════════════════════════════════════════

def aggregate_pass_signs(
    layer_extractions: list[dict],
    d_out: int,
    proj_names: list[str],
) -> dict:
    """Aggregate sign patterns across layers within a pass via majority vote.

    Each layer within the pass range casts a ±1 vote at every position.
    The consensus sign = sign(sum(votes)). This is the multi-angle sign
    accumulation proven best in session 117.

    Returns:
        dict mapping proj_name → {signs: (d_out, d_out), mags: (d_out,),
                                   vote_strength: float, n_layers: int}
    """
    result = {}
    for pn in proj_names:
        # Stack all layers' sign votes
        votes = np.stack([le[f"signs_{pn}"] for le in layer_extractions])  # (n_layers, d, d)
        mags_all = np.stack([le[f"mags_{pn}"] for le in layer_extractions])  # (n_layers, d)

        # Majority vote
        vote_sum = np.sum(votes, axis=0)  # (d, d)
        consensus_signs = np.sign(vote_sum).astype(np.float32)

        # Fill ties with random ±1
        ties = consensus_signs == 0
        if ties.any():
            consensus_signs[ties] = np.random.RandomState(42).choice(
                [-1.0, 1.0], size=int(ties.sum())
            )

        # Vote strength: fraction of positions where all layers agree
        n_layers = votes.shape[0]
        agreement = np.abs(vote_sum) / n_layers  # [0, 1]
        vote_strength = float(np.mean(agreement))

        # Magnitude: mean across layers
        consensus_mags = np.mean(mags_all, axis=0)

        result[pn] = {
            "signs": consensus_signs,
            "mags": consensus_mags,
            "vote_strength": vote_strength,
            "n_layers": n_layers,
        }

    return result


# ══════════════════════════════════════════════════════════════════════
# v6 plate mapping
# ══════════════════════════════════════════════════════════════════════

def map_teacher_to_v6_plates(
    pass_aggregations: dict[str, dict],
    v6_meta: dict,
) -> dict:
    """Map aggregated teacher sign patterns to v6 ternary plate shapes.

    v6 ternary weight layout:
      - stride_stack.layers.{0-8}.{q,k,v,out}_proj.ternary_weight: (512, 128)
      - prep.up.ternary_weight: (1536, 128), prep.down.ternary_weight: (512, 384)
      - consolidate.up.ternary_weight: (2048, 128), consolidate.down.ternary_weight: (512, 512)
      - s3_passes.{0-4}.proj_align.{0-2}.ternary_weight: (512, 192)
      - s3_passes.{0-4}.proj_delta.{0-2}.ternary_weight: (512, 128)
      - s4.{q,k,v}_proj.ternary_weight, s4.summary_proj.ternary_weight
      - meta_s4.{q,k,v,out}_proj.ternary_weight
      - mod_projs.{0-2}.ternary_weight: (512, 128)

    The mapping:
      Teacher Q → v6 stride_stack q_proj  (attention routing)
      Teacher K → v6 stride_stack k_proj  (attention addressing)
      Teacher V → v6 stride_stack v_proj  (attention content)
      Teacher O → v6 stride_stack out_proj (attention output)
      Teacher gate → v6 prep.up (gating / encoding)
      Teacher up   → v6 consolidate.up (FFN expansion)
      Teacher down → v6 prep.down, consolidate.down (FFN compression)
      Teacher Q (aggregated) → v6 s3 proj_align, s4 projections

    Returns dict: v6_key → (signs, mags) arrays cropped to v6 shapes
    """
    plates = {}

    for pass_idx, pass_name in enumerate(V6_PASSES):
        agg = pass_aggregations[pass_name]

        # ── Stride stack layers (9 per pass, but shared across passes) ──
        # v6 has ONE stride stack shared by all passes (not per-pass).
        # Teacher layer mapping: stride_layer i ↔ teacher layer range
        # We'll collect all 5 pass-worth of votes, stride layers get the
        # consensus of the pass that maps to their depth position.
        for stride_idx in range(N_STRIDES):
            for proj, teacher_proj in [("q", "q"), ("k", "k"), ("v", "v"), ("out", "o")]:
                key = f"stride_stack.layers.{stride_idx}.{proj}_proj"
                shape = (512, 128)  # all stride proj shapes are (512, 128)
                signs = agg[teacher_proj]["signs"][:shape[0], :shape[1]]
                mags = agg[teacher_proj]["mags"][:shape[0]]

                # If this stride already has a plate from an earlier pass,
                # accumulate votes (the stride stack is shared)
                if key in plates:
                    existing = plates[key]
                    existing["vote_sum"] += signs
                    existing["mag_sum"] += mags
                    existing["n_votes"] += 1
                else:
                    plates[key] = {
                        "vote_sum": signs.copy(),
                        "mag_sum": mags.copy(),
                        "n_votes": 1,
                        "shape": shape,
                    }

        # ── FFN plates (shared across passes) ──
        # prep.up: (1536, 128) ← teacher gate_proj
        key = "prep.up"
        shape = (1536, 128)
        signs = agg["gate"]["signs"][:shape[0], :shape[1]]
        mags = agg["gate"]["mags"][:shape[0]]
        if key in plates:
            plates[key]["vote_sum"] += signs
            plates[key]["mag_sum"] += mags
            plates[key]["n_votes"] += 1
        else:
            plates[key] = {"vote_sum": signs.copy(), "mag_sum": mags.copy(),
                          "n_votes": 1, "shape": shape}

        # prep.down: (512, 384) ← teacher down_proj (compression)
        key = "prep.down"
        shape = (512, 384)
        signs = agg["down"]["signs"][:shape[0], :shape[1]]
        mags = agg["down"]["mags"][:shape[0]]
        if key in plates:
            plates[key]["vote_sum"] += signs
            plates[key]["mag_sum"] += mags
            plates[key]["n_votes"] += 1
        else:
            plates[key] = {"vote_sum": signs.copy(), "mag_sum": mags.copy(),
                          "n_votes": 1, "shape": shape}

        # consolidate.up: (2048, 128) ← teacher up_proj (expansion)
        key = "consolidate.up"
        shape = (2048, 128)
        signs = agg["up"]["signs"][:shape[0], :shape[1]]
        mags = agg["up"]["mags"][:shape[0]]
        if key in plates:
            plates[key]["vote_sum"] += signs
            plates[key]["mag_sum"] += mags
            plates[key]["n_votes"] += 1
        else:
            plates[key] = {"vote_sum": signs.copy(), "mag_sum": mags.copy(),
                          "n_votes": 1, "shape": shape}

        # consolidate.down: (512, 512) ← teacher down_proj
        key = "consolidate.down"
        shape = (512, 512)
        signs = agg["down"]["signs"][:shape[0], :shape[1]]
        mags = agg["down"]["mags"][:shape[0]]
        if key in plates:
            plates[key]["vote_sum"] += signs
            plates[key]["mag_sum"] += mags
            plates[key]["n_votes"] += 1
        else:
            plates[key] = {"vote_sum": signs.copy(), "mag_sum": mags.copy(),
                          "n_votes": 1, "shape": shape}

        # ── S3 plates (per-pass, NOT shared) ──
        for reg_idx in range(3):  # 3 registers
            # proj_align: (512, 192)
            key = f"s3_passes.{pass_idx}.proj_align.{reg_idx}"
            shape = (512, 192)
            signs = agg["q"]["signs"][:shape[0], :shape[1]]
            mags = agg["q"]["mags"][:shape[0]]
            plates[key] = {"vote_sum": signs.copy(), "mag_sum": mags.copy(),
                          "n_votes": 1, "shape": shape}

            # proj_delta: (512, 128)
            key = f"s3_passes.{pass_idx}.proj_delta.{reg_idx}"
            shape = (512, 128)
            signs = agg["q"]["signs"][:shape[0], :shape[1]]
            mags = agg["q"]["mags"][:shape[0]]
            plates[key] = {"vote_sum": signs.copy(), "mag_sum": mags.copy(),
                          "n_votes": 1, "shape": shape}

    # ── Finalize: vote_sum → consensus signs ──
    final_plates = {}
    for key, plate_data in plates.items():
        vote_sum = plate_data["vote_sum"]
        n = plate_data["n_votes"]
        consensus = np.sign(vote_sum).astype(np.float32)
        # Fill ties
        ties = consensus == 0
        if ties.any():
            consensus[ties] = np.random.RandomState(hash(key) % 2**31).choice(
                [-1.0, 1.0], size=int(ties.sum())
            )
        final_plates[key] = {
            "signs": consensus,
            "mags": plate_data["mag_sum"] / n,
            "vote_strength": float(np.mean(np.abs(vote_sum) / n)),
            "shape": plate_data["shape"],
        }

    return final_plates


# ══════════════════════════════════════════════════════════════════════
# Crystal target extraction (weight-space, no inference)
# ══════════════════════════════════════════════════════════════════════

def extract_crystal_targets_from_weights(model_path: Path, d_out: int) -> dict:
    """Extract per-pass crystal geometry targets from teacher weights.

    Uses the CCA angle spectrum as a proxy for crystal geometry at each
    depth range. The CCA angles between Q and FFN_up at each depth
    define the loom structure — they're the relational invariant.

    Also extracts per-layer sign overlap matrices: the cosine similarity
    between sign patterns of consecutive layers. This is the depth
    coherence signal.

    Returns dict with per-pass angle statistics and overlap metrics.
    """
    targets = {}

    for pass_name, layer_range in PASS_RANGES.items():
        angles_all = []
        sign_overlaps = []

        prev_signs_q = None
        for li in layer_range:
            # Load Q and FFN_up for CCA
            W_q = load_tensor(model_path, f"model.layers.{li}.self_attn.q_proj.weight")
            W_up = load_tensor(model_path, f"model.layers.{li}.mlp.up_proj.weight")

            _, angles, _, _, _ = cca_directions(W_q, W_up, k=d_out)
            angles_all.append(angles)

            # Sign overlap with previous layer
            _, Sq, Vtq = truncated_svd(W_q, d_out)
            Pq = Vtq[:d_out, :]
            signs_q = np.sign(Pq @ W_q.T @ Pq.T).flatten()
            if prev_signs_q is not None:
                overlap = float(np.mean(signs_q * prev_signs_q))
                sign_overlaps.append(overlap)
            prev_signs_q = signs_q

        all_angles = np.stack(angles_all)
        targets[pass_name] = {
            "cca_angles_mean": float(np.mean(all_angles)),
            "cca_angles_std": float(np.std(all_angles)),
            "cca_angles_median": float(np.median(all_angles)),
            "sign_overlap_mean": float(np.mean(sign_overlaps)) if sign_overlaps else 0.0,
            "sign_overlap_min": float(np.min(sign_overlaps)) if sign_overlaps else 0.0,
            "n_layers": len(layer_range),
        }

    return targets


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    log("=" * 60)
    log("  Teacher Extraction: Qwen3-14B → v6 format")
    log(f"  Teacher: {QWEN3_14B_PATH}")
    log(f"  Target d_model: {D_STUDENT}")
    log(f"  Passes: {V6_PASSES}")
    log("=" * 60)

    # Verify teacher model exists
    if not QWEN3_14B_PATH.exists():
        log(f"ERROR: Teacher model not found at {QWEN3_14B_PATH}")
        sys.exit(1)

    # ── Phase 1: Per-layer extraction ──
    log(f"\nPhase 1: Extracting sign patterns from {N_LAYERS} layers...")
    layer_extractions = {}

    for li in range(N_LAYERS):
        t1 = time.time()
        le = extract_layer(QWEN3_14B_PATH, li, D_STUDENT)
        dt = time.time() - t1
        log(f"  Layer {li:2d}/{N_LAYERS}: CCA angle {le['cca_angles_mean']:.1f}° "
            f"± {le['cca_angles_std']:.1f}° ({dt:.1f}s)")
        layer_extractions[li] = le

    # ── Phase 2: Aggregate into v6 passes ──
    log(f"\nPhase 2: Aggregating layers into 5 v6 passes...")
    proj_names = ["q", "k", "v", "o", "gate", "up", "down"]
    pass_aggregations = {}

    for pass_name in V6_PASSES:
        layer_range = PASS_RANGES[pass_name]
        layer_list = [layer_extractions[li] for li in layer_range]
        agg = aggregate_pass_signs(layer_list, D_STUDENT, proj_names)
        pass_aggregations[pass_name] = agg

        log(f"  {pass_name}: layers {layer_range[0]}-{layer_range[-1]}")
        for pn in proj_names:
            log(f"    {pn:5s}: vote_strength={agg[pn]['vote_strength']:.3f}")

    # ── Phase 3: Map to v6 plate shapes ──
    log(f"\nPhase 3: Mapping to v6 plate shapes...")

    # Load v6 meta for shape reference
    v6_meta_path = Path("checkpoints/vsm-lm-v6/step_032500/meta.json")
    with open(v6_meta_path) as f:
        v6_meta = json.load(f)

    v6_plates = map_teacher_to_v6_plates(pass_aggregations, v6_meta)

    log(f"  Generated {len(v6_plates)} plate targets")
    # Summary by category
    categories = {"stride_stack": 0, "prep": 0, "consolidate": 0, "s3": 0, "other": 0}
    for key in v6_plates:
        if key.startswith("stride_stack"):
            categories["stride_stack"] += 1
        elif key.startswith("prep"):
            categories["prep"] += 1
        elif key.startswith("consolidate"):
            categories["consolidate"] += 1
        elif key.startswith("s3"):
            categories["s3"] += 1
        else:
            categories["other"] += 1
    for cat, count in categories.items():
        log(f"    {cat}: {count} plates")

    # Vote strength summary
    strengths = [v6_plates[k]["vote_strength"] for k in v6_plates]
    log(f"  Vote strength: mean={np.mean(strengths):.3f}, "
        f"min={np.min(strengths):.3f}, max={np.max(strengths):.3f}")

    # ── Phase 4: Crystal geometry targets ──
    log(f"\nPhase 4: Extracting crystal geometry targets...")
    crystal_targets = extract_crystal_targets_from_weights(QWEN3_14B_PATH, D_STUDENT)

    for pass_name, tgt in crystal_targets.items():
        log(f"  {pass_name}: CCA={tgt['cca_angles_mean']:.1f}° "
            f"overlap={tgt['sign_overlap_mean']:.3f}")

    # ── Save ──
    log(f"\nSaving to {RESULTS_DIR}/...")

    # Save plates as npz (signs + mags for each plate key)
    plate_signs = {}
    plate_mags = {}
    plate_meta = {}
    for key, data in v6_plates.items():
        safe_key = key.replace(".", "_")
        plate_signs[safe_key] = data["signs"]
        plate_mags[safe_key] = data["mags"]
        plate_meta[key] = {
            "vote_strength": data["vote_strength"],
            "shape": list(data["shape"]),
        }

    np.savez_compressed(RESULTS_DIR / "plate_signs.npz", **plate_signs)
    np.savez_compressed(RESULTS_DIR / "plate_mags.npz", **plate_mags)

    # Save metadata
    meta = {
        "teacher": "Qwen3-14B",
        "teacher_path": str(QWEN3_14B_PATH),
        "teacher_layers": N_LAYERS,
        "teacher_d_model": D_MODEL,
        "student_d_model": D_STUDENT,
        "pass_ranges": {k: list(v) for k, v in PASS_RANGES.items()},
        "plate_meta": plate_meta,
        "crystal_targets": crystal_targets,
        "n_plates": len(v6_plates),
        "elapsed": time.time() - t0,
    }
    with open(RESULTS_DIR / "extraction_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    # Save CCA angle profiles (for analysis)
    angle_profile = {}
    for li, le in layer_extractions.items():
        angle_profile[f"layer_{li}"] = {
            "mean": le["cca_angles_mean"],
            "std": le["cca_angles_std"],
        }
    with open(RESULTS_DIR / "cca_angle_profile.json", "w") as f:
        json.dump(angle_profile, f, indent=2)

    total_time = time.time() - t0
    log(f"\n{'=' * 60}")
    log(f"  Extraction complete in {total_time:.1f}s")
    log(f"  {len(v6_plates)} plates extracted")
    log(f"  Results: {RESULTS_DIR}/")
    log(f"{'=' * 60}")


if __name__ == "__main__":
    main()
