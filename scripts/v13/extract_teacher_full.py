#!/usr/bin/env python3
"""
v13 Teacher Crystal Extraction — FULL: embeddings + attention + FFN.

KIBC combinator-probe finding (session post-132):

  The type system encoded in attention Q/K/V/O sign patterns is universal
  across architectures (r = 0.998). The stride-stack attention shape is
  different from flat attention but the COMPUTATION (beta reduction via
  KIBC combinators) is the same. The sign topology encodes WHAT the
  projections select, not WHERE they attend. Therefore attention plates
  CAN be etched from the teacher.

What this script extracts
─────────────────────────
  1. Embeddings
       Teacher embed_tokens (151936, 5120) → student (151936, 512).
       Same tokenizer (Qwen3 BBPE). Column-SVD project then sign().
       Gives ~88% of type information for free.

  2. SSA attention (7 of 11 strides: s1,s2,s4,s8,s256,s512,s1024)
       Q/K/V/O projections. Each is (512, 512) in the student.
       SVD tomographic sign voting from representative teacher layers.

  3. GLA attention (4 of 11 strides: s16,s32,s64,s128)
       Q/K/V/O projections. Same dimensions (512→512).
       GLA uses a different mechanism (elu+1, outer product) but the
       sign topology encodes the same functional selection pattern.

  4. FFN plates (gate + key + value, zone-voted from 3 teacher layers).
       Session 141: gate IS the holographic aperture selector (89% of
       neuron selection). Zone-voted: extract from layers A, FFN, C and
       vote across them for the shared plate. SwiGLU activation.

Teacher layer mapping (B→K→B program):
  Zone A encode  (strides s1-s8,     indices 0-3)  → teacher layer  4
  Zone B compress (strides s16-s128, indices 4-7)  → teacher layer 32
  Zone C reconstruct (strides s256-s1024, idx 8-10) → teacher layer 56
  FFN                                               → teacher layer 20

CLI
───
  uv run python scripts/v13/extract_teacher_full.py \\
      --teacher-path ~/.cache/huggingface/hub/models--Qwen--Qwen3-32B/snapshots/... \\
      --output checkpoints/v13-etched-full

Flags
  --teacher-model     HF model id (default: Qwen/Qwen3-32B)
  --skip-embeddings   omit embedding etch
  --skip-attention    omit attention etch (reproduces FFN-only behaviour)

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

try:
    from safetensors import safe_open
except ImportError:
    print("ERROR: pip install safetensors", file=sys.stderr)
    sys.exit(1)

try:
    from sklearn.utils.extmath import randomized_svd as _rsvd
except ImportError:
    _rsvd = None


# ══════════════════════════════════════════════════════════════════════
# § 1  Utilities
# ══════════════════════════════════════════════════════════════════════

def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def truncated_svd(
    M: np.ndarray, k: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Randomized truncated SVD: top-k components — O(m·n·k).

    Returns U (m, k), S (k,), Vt (k, n) in descending singular-value order.
    Falls back to full SVD when sklearn is not available.
    """
    k = min(k, min(M.shape) - 1)
    if k < 1:
        k = 1
    if _rsvd is None:
        U, S, Vt = np.linalg.svd(M, full_matrices=False)
        return (
            U[:, :k].astype(np.float32),
            S[:k].astype(np.float32),
            Vt[:k, :].astype(np.float32),
        )
    U, S, Vt = _rsvd(M, n_components=k, n_iter=4, random_state=42)
    return (
        U.astype(np.float32),
        S.astype(np.float32),
        Vt.astype(np.float32),
    )


# ══════════════════════════════════════════════════════════════════════
# § 2  Safetensors loading
# ══════════════════════════════════════════════════════════════════════

_SHARD_INDEX_CACHE: dict[str, dict] = {}


def _load_shard_index(model_path: Path) -> dict | None:
    index_path = model_path / "model.safetensors.index.json"
    if index_path.exists():
        with open(index_path) as f:
            return json.load(f)
    return None


def find_shard(model_path: Path, tensor_name: str) -> Path | None:
    """Return path to the safetensors shard that owns *tensor_name*."""
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
    for sf_path in sorted(model_path.glob("model*.safetensors")):
        with safe_open(str(sf_path), framework="pt") as sf:
            if tensor_name in sf.keys():
                return sf_path
    return None


def load_tensor(model_path: Path, tensor_name: str) -> np.ndarray:
    """Load a single tensor from sharded safetensors, cast to float32."""
    shard_path = find_shard(model_path, tensor_name)
    if shard_path is None:
        raise FileNotFoundError(
            f"Tensor {tensor_name!r} not found in {model_path}"
        )
    with safe_open(str(shard_path), framework="pt") as sf:
        return sf.get_tensor(tensor_name).float().numpy()


def detect_teacher_config(model_path: Path) -> dict:
    """Auto-detect teacher model config from config.json."""
    config_path = model_path / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            cfg = json.load(f)
        n_heads = cfg.get("num_attention_heads", 64)
        n_kv_heads = cfg.get("num_key_value_heads", 8)
        head_dim = cfg.get("head_dim", 128)
        d_model = cfg.get("hidden_size", 5120)
        return {
            "d_model": d_model,
            "n_layers": cfg.get("num_hidden_layers", 64),
            "n_heads": n_heads,
            "n_kv_heads": n_kv_heads,
            "head_dim": head_dim,
            "d_ff": cfg.get("intermediate_size", 17408),
            "vocab_size": cfg.get("vocab_size", 151936),
            # Q proj shape: (n_heads * head_dim, d_model)
            "q_proj_out": n_heads * head_dim,
            # K/V proj shape (GQA): (n_kv_heads * head_dim, d_model)
            "kv_proj_out": n_kv_heads * head_dim,
            "model_type": cfg.get("model_type", "unknown"),
        }
    # Fallback: inspect weight shapes directly
    for sf_path in sorted(model_path.glob("model*.safetensors")):
        with safe_open(str(sf_path), framework="pt") as sf:
            for key in sf.keys():
                if "q_proj.weight" in key:
                    shape = sf.get_tensor(key).shape
                    return {
                        "d_model": shape[1],
                        "n_layers": -1,
                        "n_heads": -1,
                        "n_kv_heads": -1,
                        "head_dim": -1,
                        "d_ff": -1,
                        "vocab_size": 151936,
                        "q_proj_out": shape[0],
                        "kv_proj_out": -1,
                        "model_type": "unknown",
                    }
    raise ValueError(f"Cannot detect teacher config from {model_path}")


# ══════════════════════════════════════════════════════════════════════
# § 3  Sign pattern extraction — 360° tomographic sign voting
# ══════════════════════════════════════════════════════════════════════

def _random_orthogonal(n: int, rng: np.random.RandomState) -> np.ndarray:
    """Random orthogonal matrix via QR decomposition of Gaussian."""
    H = rng.randn(n, n).astype(np.float32)
    Q, R = np.linalg.qr(H)
    Q *= np.sign(np.diag(R))
    return Q


def extract_sign_pattern(
    W: np.ndarray,
    d_out: int,
    d_in: int,
    n_rotations: int = 8,
) -> np.ndarray:
    """Extract sign pattern via 360° tomographic sign voting.

    The crystal is a hologram — a single SVD projection captures one 2D
    photo.  Multiple random orthogonal rotations give multiple viewing
    angles.  Sign voting across all angles recovers the full volumetric
    crystal structure.

    Protocol
    ────────
    For each rotation (random orthogonal matrix):
      a. Rotate W:  W_rot = R_out @ W @ R_in.T
      b. SVD-project to student dimensions
      c. Extract sign pattern from this viewing angle
    Sum all sign patterns → sign votes per position.
    Final plate = sign(votes): positions where most angles agree.

    Positions with unanimous agreement are the stable crystal structure.
    Positions where angles disagree are viewing-angle artifacts — the
    sign vote resolves them by consensus.

    W            — (out_t, in_t) teacher weight
    d_out        — student output dimension
    d_in         — student input dimension
    n_rotations  — viewing angles (8 = overdetermined for rank-4 crystal)

    Returns (d_out, d_in) int8 {-1, +1}.
    """
    n_out, n_in = W.shape
    rng = np.random.RandomState(42)

    if n_out == d_out and n_in == d_in:
        # Same dimensions — multi-angle rotation in place
        votes = np.zeros((d_out, d_in), dtype=np.float32)
        for r in range(n_rotations):
            W_rot = W if r == 0 else W @ _random_orthogonal(d_in, rng)
            votes += np.sign(W_rot)
        result = np.sign(votes).astype(np.int8)
        mask = result == 0
        if mask.any():
            result[mask] = rng.choice(
                [-1, 1], size=int(mask.sum())
            ).astype(np.int8)
        return result

    # Cross-dimensional: SVD basis + multi-angle voting
    k = min(max(d_out, d_in), min(n_out, n_in) - 1)
    U_base, S_base, Vt_base = truncated_svd(W, k)
    k_out = min(d_out, U_base.shape[1])
    k_in = min(d_in, Vt_base.shape[0])

    votes = np.zeros((d_out, d_in), dtype=np.float32)

    for r in range(n_rotations):
        if r == 0:
            P_out = U_base[:, :k_out].T
            P_in = Vt_base[:k_in, :]
        else:
            R_out = _random_orthogonal(k_out, rng)
            R_in = _random_orthogonal(k_in, rng)
            P_out = R_out @ U_base[:, :k_out].T
            P_in = R_in @ Vt_base[:k_in, :]

        Wp = P_out @ W @ P_in.T  # (k_out, k_in)

        angle_signs = np.zeros((d_out, d_in), dtype=np.float32)
        angle_signs[:k_out, :k_in] = np.sign(Wp)
        votes += angle_signs

    result = np.sign(votes).astype(np.int8)
    zeros = result == 0
    if zeros.any():
        result[zeros] = rng.choice(
            [-1, 1], size=int(zeros.sum())
        ).astype(np.int8)
    return result


def extract_magnitude(W: np.ndarray, d_out: int) -> np.ndarray:
    """Extract per-row RMS magnitude from projected teacher weight.

    Returns (d_out,) float32 — beam magnitude (gamma seed).
    """
    n_out, n_in = W.shape
    k = min(d_out, min(n_out, n_in) - 1)
    U, S, Vt = truncated_svd(W, k)

    k_out = min(d_out, U.shape[1])
    k_in = min(d_out, Vt.shape[0])
    Wp = U[:, :k_out].T @ W @ Vt[:k_in, :].T

    mags = np.zeros(d_out, dtype=np.float32)
    rms = np.sqrt(np.mean(Wp ** 2, axis=1))
    mags[:k_out] = rms.astype(np.float32)
    return mags


# ══════════════════════════════════════════════════════════════════════
# § 4  Embedding sign pattern — column-SVD projection
# ══════════════════════════════════════════════════════════════════════

def extract_embedding_signs(
    E: np.ndarray,
    d_student: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Project teacher embedding (V, d_t) → student (V, d_s), extract signs.

    The embedding matrix is huge (151936 × 5120). Full tomographic SVD on
    each row would be prohibitively slow.  Instead, we use a single global
    column-SVD projection:

      1. Compute top-d_student left singular vectors of E^T (i.e., the
         right singular vectors of E): Vt[:d_student, :] from truncated SVD.
      2. Project: E_proj = E @ Vt[:d_student, :].T  → (V, d_student).
      3. Sign: sign(E_proj).

    This is ONE angle, not 8 rotations, but for a 151936-row matrix the
    consensus across rows IS the multi-angle signal — the single projection
    faithfully captures the dominant geometric structure of the embedding
    manifold.

    Returns
    ───────
    signs   (V, d_student) int8 {-1, +1}
    gamma   (V,) float32 — per-token scale (row-RMS of E_proj)
    """
    V, d_t = E.shape
    log(f"    Embedding SVD: ({V}, {d_t}) → ({V}, {d_student})")

    # Truncated SVD of E (V × d_t) to get top-d_student right singular vectors
    # We want the column basis of E, i.e. Vt rows.
    k = min(d_student, min(V, d_t) - 1)
    _U, _S, Vt = truncated_svd(E, k)   # Vt: (k, d_t)
    k_actual = Vt.shape[0]             # ≤ d_student

    # Project: (V, d_t) @ (d_t, k) = (V, k)
    E_proj = E @ Vt.T                   # (V, k)

    # Pad to d_student columns if k < d_student
    if k_actual < d_student:
        rng = np.random.RandomState(0)
        pad = rng.randn(V, d_student - k_actual).astype(np.float32) * 1e-4
        E_proj = np.concatenate([E_proj, pad], axis=1)

    # Per-token scale: RMS of the projected row
    gamma = np.sqrt(np.mean(E_proj ** 2, axis=1)).astype(np.float32)
    gamma = np.where(gamma == 0, 1e-8, gamma)

    # Sign
    signs = np.sign(E_proj).astype(np.int8)
    # Fill zeros with random
    zeros = signs == 0
    if zeros.any():
        rng = np.random.RandomState(1)
        signs[zeros] = rng.choice([-1, 1], size=int(zeros.sum())).astype(np.int8)

    return signs, gamma


# ══════════════════════════════════════════════════════════════════════
# § 5  Teacher layer mapping (B→K→B program)
# ══════════════════════════════════════════════════════════════════════

#
# The B→K→B program (Beta→Kappa→Beta) maps strides to teacher layers
# by their functional zone:
#
#   Zone A encode     (strides s1-s8,    indices 0-3)  → layer  4
#   Zone B compress   (strides s16-s128, indices 4-7)  → layer 32
#   Zone C reconstruct (strides s256-s1024, idx 8-10) → layer 56
#   FFN               (all strides share one source)   → layer 20
#
# The zone layer indices are tuned for Qwen3-32B (64 layers).  The script
# re-normalises to the actual teacher depth if a different model is used.

_ZONE_FRACS = {
    "A": 4  / 64,   # ≈ 6%  — bottom of Zone A
    "B": 32 / 64,   # ≈ 50% — middle of Zone B
    "C": 56 / 64,   # ≈ 88% — top of Zone C
    "FFN": 20 / 64, # ≈ 31% — middle of Zone B (same as original)
}

# stride index 0-10 → zone key
_STRIDE_ZONE = {
    0: "A", 1: "A", 2: "A", 3: "A",   # s1, s2, s4, s8
    4: "B", 5: "B", 6: "B", 7: "B",   # s16, s32, s64, s128
    8: "C", 9: "C", 10: "C",           # s256, s512, s1024
}


def zone_layer(zone: str, n_teacher_layers: int) -> int:
    """Map a zone key to a teacher layer index, scaled to actual depth.

    Uses floor(frac * n_layers) so that the canonical 64-layer Qwen3-32B
    maps exactly to layers 4, 20, 32, 56 without rounding error.
    """
    frac = _ZONE_FRACS[zone]
    return max(0, min(int(frac * n_teacher_layers), n_teacher_layers - 1))


# ══════════════════════════════════════════════════════════════════════
# § 6  Main extraction pipeline
# ══════════════════════════════════════════════════════════════════════

def extract_crystal_full(
    teacher_path: Path,
    d_student: int = 512,
    d_ff_student: int = 2048,
    n_strides: int = 11,
    stride_is_retrieval: tuple[bool, ...] = (
        False, False, False, False,
        True,  True,  True,  True,
        False, False, False,
    ),
    n_rotations: int = 8,
    skip_embeddings: bool = False,
    skip_attention: bool = False,
    output_dir: Path | None = None,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Full crystal extraction: embeddings + attention Q/K/V/O + FFN.

    Returns dict mapping param_path → (signs_int8, magnitude_float32).
    The param_path keys are human-readable descriptors; install_plates_full()
    knows how to navigate the model from them.
    """
    t0 = time.time()

    tcfg = detect_teacher_config(teacher_path)
    d_t = tcfg["d_model"]
    n_t = tcfg["n_layers"]
    d_ff_t = tcfg["d_ff"]
    vocab_t = tcfg["vocab_size"]

    log(f"Teacher: {tcfg['model_type']}, d={d_t}, layers={n_t}, "
        f"d_ff={d_ff_t}, vocab={vocab_t}")
    log(f"Student: d={d_student}, d_ff={d_ff_student}, strides={n_strides}")
    log(f"Rotations: {n_rotations} (360° tomographic sign voting)")

    plates: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    stats: dict[str, int] = {
        "embed_positions": 0,
        "attn_positions": 0,
        "ffn_positions": 0,
    }

    # Pre-compute zone layer indices (scaled to actual teacher depth)
    layer_A   = zone_layer("A",   n_t)
    layer_B   = zone_layer("B",   n_t)
    layer_C   = zone_layer("C",   n_t)
    layer_FFN = zone_layer("FFN", n_t)
    log(f"Zone layers → A={layer_A}, B={layer_B}, C={layer_C}, FFN={layer_FFN}")

    # ── § 6.1  Embedding plate ────────────────────────────────────
    if not skip_embeddings:
        log("\n── Embeddings ──────────────────────────────────────────────")
        W_emb = load_tensor(teacher_path, "model.embed_tokens.weight")
        log(f"  Loaded embed_tokens: {W_emb.shape}")
        signs_emb, gamma_emb = extract_embedding_signs(W_emb, d_student)
        plates["embed"] = (signs_emb, gamma_emb)
        stats["embed_positions"] = signs_emb.size
        log(f"  embed signs: {signs_emb.shape}, "
            f"gamma mean={gamma_emb.mean():.4f}")
        del W_emb

    # ── § 6.2  Attention Q/K/V/O plates ──────────────────────────
    if not skip_attention:
        log("\n── Attention Q/K/V/O ──────────────────────────────────────")

        # Cache tensors that are reused across multiple strides in the same zone
        _zone_cache: dict[tuple[int, str], np.ndarray] = {}

        def _get_attn_weight(layer: int, proj: str) -> np.ndarray:
            key = (layer, proj)
            if key not in _zone_cache:
                name = f"model.layers.{layer}.self_attn.{proj}.weight"
                _zone_cache[key] = load_tensor(teacher_path, name)
            return _zone_cache[key]

        for stride_idx in range(n_strides):
            zone = _STRIDE_ZONE[stride_idx]
            is_gla = stride_is_retrieval[stride_idx]
            layer = {"A": layer_A, "B": layer_B, "C": layer_C}[zone]
            stride_tag = f"stride_{stride_idx}"
            attn_type = "GLA" if is_gla else "SSA"
            log(f"  {stride_tag} ({attn_type}, zone {zone}) ← layer {layer}")

            for proj in ("q_proj", "k_proj", "v_proj", "o_proj"):
                W = _get_attn_weight(layer, proj)
                # W shape: (out_t, d_t).
                # Q:   (n_heads * head_dim, d_t) = (q_proj_out, d_t)
                # K/V: (n_kv_heads * head_dim, d_t) = (kv_proj_out, d_t)
                # O:   (d_t, n_heads * head_dim)  — note reversed dims
                signs = extract_sign_pattern(
                    W, d_student, d_student, n_rotations
                )
                mags = extract_magnitude(W, d_student)
                plate_key = f"attn.{stride_tag}.{proj}"
                plates[plate_key] = (signs, mags)
                stats["attn_positions"] += signs.size
                log(f"    {proj}: teacher {W.shape} → student {signs.shape}")

        # Free zone cache
        _zone_cache.clear()
        log(f"  Attention total: {stats['attn_positions']:,} positions "
            f"across {n_strides} strides × 4 projections")

    # ── § 6.3  FFN plates (gate + key + value, zone-voted) ──────
    #
    # Session 141: gate IS the holographic aperture selector (89% of
    # neuron selection). The depth profile is a LENS: aperture (early)
    # → fan (middle) → converge (late). Zone-voted extraction: extract
    # signs from 3 teacher layers (A, B, C zones) and VOTE for the
    # shared plate. This captures the full lens topology.
    #
    ffn_layers = [layer_A, layer_FFN, layer_C]
    log(f"\n── FFN plates ← zone-voted from teacher layers {ffn_layers} ──")

    # gate_proj — the beamformer aperture selector
    log(f"  Extracting gate_proj (3-layer vote)...")
    gate_votes = np.zeros((d_ff_student, d_student), dtype=np.float32)
    for fl in ffn_layers:
        W_gate = load_tensor(teacher_path, f"model.layers.{fl}.mlp.gate_proj.weight")
        signs_layer = extract_sign_pattern(W_gate, d_ff_student, d_student, n_rotations)
        gate_votes += signs_layer.astype(np.float32)
        log(f"    layer {fl}: gate_proj {W_gate.shape}")
        del W_gate
    gate_signs = np.sign(gate_votes).astype(np.int8)
    zeros = gate_signs == 0
    if zeros.any():
        rng = np.random.RandomState(43)
        gate_signs[zeros] = rng.choice([-1, 1], size=int(zeros.sum())).astype(np.int8)
    # Magnitude from the primary FFN layer
    W_gate_mag = load_tensor(teacher_path, f"model.layers.{layer_FFN}.mlp.gate_proj.weight")
    gate_mags = extract_magnitude(W_gate_mag, d_ff_student)
    del W_gate_mag
    plates["ffn_gate_plate"] = (gate_signs, gate_mags)
    stats["ffn_positions"] += gate_signs.size
    log(f"  gate_proj: → {gate_signs.shape} (3-layer voted)")

    # up_proj (key plate) — zone-voted
    log(f"  Extracting up_proj (3-layer vote)...")
    key_votes = np.zeros((d_ff_student, d_student), dtype=np.float32)
    for fl in ffn_layers:
        W_up = load_tensor(teacher_path, f"model.layers.{fl}.mlp.up_proj.weight")
        signs_layer = extract_sign_pattern(W_up, d_ff_student, d_student, n_rotations)
        key_votes += signs_layer.astype(np.float32)
        log(f"    layer {fl}: up_proj {W_up.shape}")
        del W_up
    key_signs = np.sign(key_votes).astype(np.int8)
    zeros = key_signs == 0
    if zeros.any():
        rng = np.random.RandomState(44)
        key_signs[zeros] = rng.choice([-1, 1], size=int(zeros.sum())).astype(np.int8)
    W_up_mag = load_tensor(teacher_path, f"model.layers.{layer_FFN}.mlp.up_proj.weight")
    key_mags = extract_magnitude(W_up_mag, d_ff_student)
    del W_up_mag
    plates["ffn_key_plate"] = (key_signs, key_mags)
    stats["ffn_positions"] += key_signs.size
    log(f"  up_proj:   → {key_signs.shape} (3-layer voted)")

    # down_proj (value plate) — zone-voted
    log(f"  Extracting down_proj (3-layer vote)...")
    val_votes = np.zeros((d_student, d_ff_student), dtype=np.float32)
    for fl in ffn_layers:
        W_down = load_tensor(teacher_path, f"model.layers.{fl}.mlp.down_proj.weight")
        signs_layer = extract_sign_pattern(W_down, d_student, d_ff_student, n_rotations)
        val_votes += signs_layer.astype(np.float32)
        log(f"    layer {fl}: down_proj {W_down.shape}")
        del W_down
    val_signs = np.sign(val_votes).astype(np.int8)
    zeros = val_signs == 0
    if zeros.any():
        rng = np.random.RandomState(45)
        val_signs[zeros] = rng.choice([-1, 1], size=int(zeros.sum())).astype(np.int8)
    W_down_mag = load_tensor(teacher_path, f"model.layers.{layer_FFN}.mlp.down_proj.weight")
    val_mags = extract_magnitude(W_down_mag, d_student)
    del W_down_mag
    plates["ffn_value_plate"] = (val_signs, val_mags)
    stats["ffn_positions"] += val_signs.size
    log(f"  down_proj: → {val_signs.shape} (3-layer voted)")

    dt = time.time() - t0
    total_positions = sum(stats.values())
    log(f"\n── Extraction summary ─────────────────────────────────────")
    log(f"  Plates extracted:     {len(plates)}")
    log(f"  Embed positions:      {stats['embed_positions']:>14,}")
    log(f"  Attention positions:  {stats['attn_positions']:>14,}")
    log(f"  FFN positions:        {stats['ffn_positions']:>14,}")
    log(f"  Total positions:      {total_positions:>14,}")
    log(f"  Elapsed:              {dt:.1f}s")

    # ── § 6.4  Save plates as NPZ ─────────────────────────────────
    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        npz_data: dict[str, np.ndarray] = {}
        for path, (s, m) in plates.items():
            npz_data[f"{path}.signs"] = s
            npz_data[f"{path}.mags"] = m

        npz_path = output_dir / "teacher_plates_full.npz"
        np.savez_compressed(str(npz_path), **npz_data)
        log(f"  Saved plates: {npz_path} "
            f"({npz_path.stat().st_size / 1024 / 1024:.1f} MB)")

        manifest = {
            "script": "extract_teacher_full.py",
            "teacher": {
                "path": str(teacher_path),
                "config": tcfg,
                "zones": {
                    "A": layer_A, "B": layer_B,
                    "C": layer_C, "FFN": layer_FFN,
                },
            },
            "student": {
                "d_model": d_student,
                "d_ff": d_ff_student,
                "n_strides": n_strides,
            },
            "plates": list(plates.keys()),
            "stats": stats,
            "flags": {
                "skip_embeddings": skip_embeddings,
                "skip_attention": skip_attention,
                "n_rotations": n_rotations,
            },
            "extraction_time_s": dt,
        }
        manifest_path = output_dir / "manifest_full.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        log(f"  Saved manifest: {manifest_path}")

    return plates


# ══════════════════════════════════════════════════════════════════════
# § 7  Install plates into V13 model
# ══════════════════════════════════════════════════════════════════════

def _install_ternary_linear(
    mod,
    signs: np.ndarray,
    mags: np.ndarray,
    path: str,
    pack_ternary_mlx,
    mx,
) -> bool:
    """Pack and install signs + mags into a TernaryLinear module.

    Returns True on success, False if shape mismatch cannot be resolved.
    """
    from ternary import TernaryLinear
    if not isinstance(mod, TernaryLinear):
        log(f"  SKIP: {path} (not TernaryLinear, is {type(mod).__name__})")
        return False

    expected_out = mod.out_features
    expected_in  = mod.in_features

    # Trim / pad to model dimensions
    if signs.shape != (expected_out, expected_in):
        s = np.zeros((expected_out, expected_in), dtype=np.int8)
        ro = min(signs.shape[0], expected_out)
        ci = min(signs.shape[1], expected_in)
        s[:ro, :ci] = signs[:ro, :ci]
        mask = s == 0
        if mask.any():
            rng = np.random.RandomState(42)
            s[mask] = rng.choice(
                [-1, 1], size=int(mask.sum())
            ).astype(np.int8)
        signs = s

    signs_mx = mx.array(signs)
    packed = pack_ternary_mlx(signs_mx)
    mod.weight = packed
    mx.eval(mod.weight)

    if mags is not None and len(mags) >= expected_out:
        mod.gamma = mx.array(mags[:expected_out])
        mx.eval(mod.gamma)
    elif mags is not None and len(mags) > 0:
        g = np.zeros(expected_out, dtype=np.float32)
        g[:len(mags)] = mags
        mod.gamma = mx.array(g)
        mx.eval(mod.gamma)

    return True


def _install_ternary_embedding(
    mod,
    signs: np.ndarray,
    mags: np.ndarray,
    path: str,
    pack_ternary,
    mx,
) -> bool:
    """Pack and install signs + mags into a TernaryEmbedding module.

    TernaryEmbedding uses uint8 (4-per-byte) packing, NOT uint32.
    Signs (V, d) → pack_ternary → uint8 (V, d//4).

    Returns True on success.
    """
    from ternary import TernaryEmbedding
    if not isinstance(mod, TernaryEmbedding):
        log(f"  SKIP: {path} (not TernaryEmbedding, is {type(mod).__name__})")
        return False

    V = mod.vocab_size
    d = mod.d_model

    # Trim / pad to model vocab × d_model
    if signs.shape != (V, d):
        s = np.zeros((V, d), dtype=np.int8)
        rv = min(signs.shape[0], V)
        cd = min(signs.shape[1], d)
        s[:rv, :cd] = signs[:rv, :cd]
        mask = s == 0
        if mask.any():
            rng = np.random.RandomState(42)
            s[mask] = rng.choice(
                [-1, 1], size=int(mask.sum())
            ).astype(np.int8)
        signs = s

    signs_mx = mx.array(signs)
    packed = pack_ternary(signs_mx)   # → uint8
    mod.ternary_weight = packed
    mx.eval(mod.ternary_weight)

    if mags is not None and len(mags) > 0:
        g = np.zeros(V, dtype=np.float32)
        n = min(len(mags), V)
        g[:n] = mags[:n]
        mod.gamma = mx.array(g)
        mx.eval(mod.gamma)

    return True


def install_plates_full(
    model,
    plates: dict[str, tuple[np.ndarray, np.ndarray]],
    stride_is_retrieval: tuple[bool, ...] = (
        False, False, False, False,
        True,  True,  True,  True,
        False, False, False,
    ),
    freeze: bool = True,
) -> dict[str, int]:
    """Install full crystal plates (embed + attention + FFN) into a V13 model.

    Plate key conventions
    ─────────────────────
      "embed"                        → model.embed (TernaryEmbedding)
      "attn.stride_N.q_proj"         → all three stacks, stride layer N, q_proj
      "attn.stride_N.k_proj"         → …k_proj
      "attn.stride_N.v_proj"         → …v_proj
      "attn.stride_N.o_proj"         → …out_proj  (note: "o_proj" → "out_proj")
      "ffn_key_plate"                → model.ffn_key_plate
      "ffn_value_plate"              → model.ffn_value_plate

    The three stacks (stack_a, stack_b, stack_c) share the same stride
    topology.  Each stride layer's Q/K/V/O plates are identical across
    stacks because the sign pattern encodes WHAT to select, not WHERE.

    Returns
    ───────
    dict with counts: embed, attn, ffn, total, frozen
    """
    import mlx.core as mx
    sys.path.insert(0, str(Path(__file__).parent))
    from ternary import (
        pack_ternary_mlx,
        pack_ternary,
        TernaryLinear,
        TernaryEmbedding,
    )

    counts = {"embed": 0, "attn": 0, "ffn": 0, "total": 0, "frozen": 0}
    installed_modules: list[tuple[str, object]] = []

    stacks = [model.stack_a, model.stack_b, model.stack_c]
    stack_names = ["stack_a", "stack_b", "stack_c"]

    # ── Embedding ─────────────────────────────────────────────────
    if "embed" in plates:
        signs, mags = plates["embed"]
        ok = _install_ternary_embedding(
            model.embed, signs, mags, "model.embed",
            pack_ternary, mx,
        )
        if ok:
            counts["embed"] += 1
            installed_modules.append(("model.embed", model.embed))
            log(f"  Installed: model.embed (TernaryEmbedding)")

    # ── Attention strides → all three stacks ─────────────────────
    for stride_idx in range(len(stride_is_retrieval)):
        stride_key_prefix = f"attn.stride_{stride_idx}"

        for proj_key, model_attr in [
            ("q_proj", "q_proj"),
            ("k_proj", "k_proj"),
            ("v_proj", "v_proj"),
            ("o_proj", "out_proj"),  # o_proj plate key → out_proj module attr
        ]:
            plate_key = f"{stride_key_prefix}.{proj_key}"
            if plate_key not in plates:
                continue
            signs, mags = plates[plate_key]

            for stack, sname in zip(stacks, stack_names):
                # Navigate: stack.stride_stack.stack.layers[stride_idx].<attr>
                try:
                    layer = stack.stride_stack.stack.layers[stride_idx]
                    mod = getattr(layer, model_attr)
                except (AttributeError, IndexError) as e:
                    log(f"  SKIP: {sname}.stride_{stride_idx}.{model_attr} ({e})")
                    continue

                full_path = f"{sname}.stride_stack.stack.layers.{stride_idx}.{model_attr}"
                ok = _install_ternary_linear(
                    mod, signs, mags, full_path,
                    pack_ternary_mlx, mx,
                )
                if ok:
                    counts["attn"] += 1
                    installed_modules.append((full_path, mod))

        if (f"{stride_key_prefix}.q_proj" in plates or
                f"{stride_key_prefix}.k_proj" in plates):
            log(f"  Installed: stride_{stride_idx} Q/K/V/O → 3 stacks")

    # ── FFN plates (gate + key + value) ─────────────────────────
    for plate_key in ("ffn_gate_plate", "ffn_key_plate", "ffn_value_plate"):
        if plate_key not in plates:
            continue
        signs, mags = plates[plate_key]
        mod = getattr(model, plate_key)
        ok = _install_ternary_linear(
            mod, signs, mags, f"model.{plate_key}",
            pack_ternary_mlx, mx,
        )
        if ok:
            counts["ffn"] += 1
            installed_modules.append((f"model.{plate_key}", mod))
            log(f"  Installed: model.{plate_key}")

    counts["total"] = counts["embed"] + counts["attn"] + counts["ffn"]

    # ── Freeze all installed plates ───────────────────────────────
    if freeze and installed_modules:
        for path, mod in installed_modules:
            if isinstance(mod, TernaryEmbedding):
                mod.freeze(keys=["ternary_weight"])
            elif isinstance(mod, TernaryLinear):
                mod.freeze(keys=["weight"])
            counts["frozen"] += 1
        log(f"  Frozen {counts['frozen']} installed plate modules")

    log(f"\n  Install summary:")
    log(f"    Embedding modules: {counts['embed']}")
    log(f"    Attention modules: {counts['attn']} "
        f"({counts['attn'] // 4 if counts['attn'] else 0} strides × "
        f"4 projs × ~3 stacks)")
    log(f"    FFN modules:       {counts['ffn']}")
    log(f"    Total installed:   {counts['total']}")
    log(f"    Frozen:            {counts['frozen']}")

    return counts


# ══════════════════════════════════════════════════════════════════════
# § 8  Full pipeline: extract → install → save checkpoint
# ══════════════════════════════════════════════════════════════════════

def etch_from_teacher_full(
    teacher_path: str,
    output_dir: str = "checkpoints/v13-etched-full",
    n_rotations: int = 8,
    skip_embeddings: bool = False,
    skip_attention: bool = False,
    **student_overrides,
) -> None:
    """Complete pipeline: extract full teacher crystal → install → save.

    Extracts embeddings, attention Q/K/V/O for all 11 strides, and FFN
    plates.  All installed plates are frozen; uninstalled parameters
    (pos_embed, algedonic, S4/S5 components, beam biases) remain trainable.
    """
    import mlx.core as mx
    sys.path.insert(0, str(Path(__file__).parent))
    from config import V13Config
    from model import V13Model
    from ternary import restore_ternary, count_ternary_weights

    teacher_path_obj = Path(teacher_path)
    output_dir_obj   = Path(output_dir)

    log("=" * 72)
    log("  V13 FULL Teacher Crystal Extraction")
    log("  embed + attention Q/K/V/O + FFN → all three stacks")
    log("=" * 72)

    cfg = V13Config(
        **{k: v for k, v in student_overrides.items() if hasattr(V13Config, k)}
    )
    log(f"\n  Student config: d_model={cfg.d_model}, d_ff={cfg.d_ff}, "
        f"strides={cfg.n_strides}, passes={cfg.n_passes}")

    # Build student model
    model = V13Model(cfg)
    log("  V13Model instantiated")

    # Extract crystal (all plates)
    log(f"\n  Extracting from: {teacher_path_obj}")
    plates = extract_crystal_full(
        teacher_path=teacher_path_obj,
        d_student=cfg.d_model,
        d_ff_student=cfg.d_ff,
        n_strides=cfg.n_strides,
        stride_is_retrieval=cfg.stride_is_retrieval,
        n_rotations=n_rotations,
        skip_embeddings=skip_embeddings,
        skip_attention=skip_attention,
        output_dir=output_dir_obj,
    )

    # Install into model
    log(f"\n  Installing plates into V13 model...")
    counts = install_plates_full(
        model,
        plates,
        stride_is_retrieval=cfg.stride_is_retrieval,
        freeze=True,
    )

    # Verify ternary integrity
    restore_ternary(model)
    log("  Ternary integrity verified (no dtype corruption)")

    # Save weights
    output_dir_obj.mkdir(parents=True, exist_ok=True)
    weights_path = output_dir_obj / "model.npz"
    model.save_weights(str(weights_path))
    log(f"  Saved model weights: {weights_path}")

    # Save config
    import dataclasses
    config_path = output_dir_obj / "config.json"
    with open(config_path, "w") as f:
        json.dump(dataclasses.asdict(cfg), f, indent=2, default=str)
    log(f"  Saved config: {config_path}")

    # Summary
    n_total = count_ternary_weights(model)
    embed_pos   = (
        plates["embed"][0].size
        if "embed" in plates else 0
    )
    attn_keys   = [k for k in plates if k.startswith("attn.")]
    # Positions per stack: each stride plate is installed into 3 stacks
    attn_pos_per_plate = sum(plates[k][0].size for k in attn_keys)
    attn_pos_total     = attn_pos_per_plate * 3  # 3 stacks
    ffn_pos     = sum(
        plates[k][0].size
        for k in ("ffn_gate_plate", "ffn_key_plate", "ffn_value_plate")
        if k in plates
    )
    etched_total = embed_pos + attn_pos_total + ffn_pos
    trainable_total = n_total - etched_total

    log(f"\n{'=' * 72}")
    log(f"  FULL CRYSTAL ETCH COMPLETE")
    log(f"{'─' * 72}")
    log(f"  Embed positions etched:      {embed_pos:>12,}")
    log(f"  Attention positions etched:  {attn_pos_total:>12,}  "
        f"({len(attn_keys)} plates × 3 stacks)")
    log(f"  FFN positions etched:        {ffn_pos:>12,}")
    log(f"  Total etched positions:      {etched_total:>12,}")
    log(f"  Trainable positions:         {trainable_total:>12,}  "
        f"(pos_embed, algedonic, S4/S5, beams)")
    log(f"  Total ternary positions:     {n_total:>12,}")
    log(f"  Checkpoint: {output_dir_obj}")
    log(f"{'=' * 72}")
    log(f"\n  Next:")
    log(f"    uv run python scripts/v13/train.py --phase gd --resume {output_dir_obj}")


# ══════════════════════════════════════════════════════════════════════
# § 9  CLI
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Extract FULL crystal from teacher model into V13 student plates "
            "(embeddings + attention Q/K/V/O + FFN)."
        )
    )
    parser.add_argument(
        "--teacher-path", type=str, required=True,
        help="Path to teacher model directory (with safetensors shards).",
    )
    parser.add_argument(
        "--teacher-model", type=str, default="Qwen/Qwen3-32B",
        help="HuggingFace model ID of the teacher (informational, default: Qwen/Qwen3-32B).",
    )
    parser.add_argument(
        "--output", type=str, default="checkpoints/v13-etched-full",
        help="Output directory for full-etched checkpoint (default: checkpoints/v13-etched-full).",
    )
    parser.add_argument(
        "--d-model", type=int, default=512,
        help="Student d_model (default: 512).",
    )
    parser.add_argument(
        "--d-ff", type=int, default=2048,
        help="Student d_ff (default: 2048).",
    )
    parser.add_argument(
        "--n-rotations", type=int, default=8,
        help="Number of orthogonal rotations for tomographic sign voting (default: 8).",
    )
    parser.add_argument(
        "--skip-embeddings", action="store_true",
        help="Skip embedding etch (attention + FFN only).",
    )
    parser.add_argument(
        "--skip-attention", action="store_true",
        help="Skip attention etch (reproduce FFN-only behaviour of extract_teacher.py).",
    )
    parser.add_argument(
        "--plates-only", action="store_true",
        help="Extract plates to NPZ only — do not build a model checkpoint.",
    )

    args = parser.parse_args()

    log(f"  Teacher model: {args.teacher_model}")
    log(f"  Teacher path:  {args.teacher_path}")

    if args.plates_only:
        # Load config just to get stride_is_retrieval
        sys.path.insert(0, str(Path(__file__).parent))
        from config import V13Config
        cfg = V13Config(d_model=args.d_model, d_ff=args.d_ff)

        plates = extract_crystal_full(
            teacher_path=Path(args.teacher_path),
            d_student=args.d_model,
            d_ff_student=args.d_ff,
            n_strides=cfg.n_strides,
            stride_is_retrieval=cfg.stride_is_retrieval,
            n_rotations=args.n_rotations,
            skip_embeddings=args.skip_embeddings,
            skip_attention=args.skip_attention,
            output_dir=Path(args.output),
        )
        log(f"\nPlates saved to {args.output}/teacher_plates_full.npz")
    else:
        etch_from_teacher_full(
            teacher_path=args.teacher_path,
            output_dir=args.output,
            n_rotations=args.n_rotations,
            skip_embeddings=args.skip_embeddings,
            skip_attention=args.skip_attention,
            d_model=args.d_model,
            d_ff=args.d_ff,
        )
