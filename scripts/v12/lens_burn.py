"""Lens burn — initialize combinator mirrors from warped lens directions.

Takes the warped lens (teacher operation directions at 7 depths) and writes
them as ternary sign patterns into the model's combinator mirrors. This gives
the model the teacher's coordinate system: mirrors point WHERE each operation
lives in hidden space, before any training.

The lens provides directions for K, I, B, C, M (5 ops).
D, Y, W, WHNF (3 new ops + terminal) start random (no teacher data).

Protocol:
  1. Load warped lens (pass_N_dir_{K,I,B,C,M} vectors, 512-dim each)
  2. For each op with lens data: convert float direction → ternary signs
  3. Write signs into model.stride_stack.combinator_mirrors[op_idx]
  4. The mirror is now aligned with the teacher's operation subspace
  5. Holographic recording then crystallizes plates from this starting point

Why this works:
  - TernaryMirror is a 512×512 weight matrix of {-1, 0, +1}
  - It deflects the Q beam toward a specific angle before attention
  - sign(teacher_direction) gives the ternary approximation of that angle
  - The 37° angular resolution of ternary is sufficient (teacher ops are 55-154° apart)
  - This is NOT direct alignment (no hidden state matching) — just beam aiming

Usage:
    uv run python scripts/v12/lens_burn.py
    uv run python scripts/v12/lens_burn.py --lens lens/warped_lens.npz --checkpoint checkpoints/v12-holo-8op

License: MIT
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import mlx.core as mx
import numpy as np
from mlx.utils import tree_flatten

sys.path.insert(0, str(Path(__file__).parent))

from config import V12Config
from model import V12Model, create_model, count_parameters
from kernel import N_COMBINATORS, COMBINATOR_NAMES
from ternary import (
    pack_ternary_mlx,
    unpack_ternary_mlx,
    TernaryMirror,
    freeze_ternary_weights,
    restore_ternary,
)


# ══════════════════════════════════════════════════════════════════════
# Lens burn — write teacher directions into combinator mirrors
# ══════════════════════════════════════════════════════════════════════


# Map from combinator index to lens op name (only 5 of 8 have lens data)
LENS_OPS = {0: "K", 1: "I", 2: "B", 3: "C", 4: "M"}
# Note: M is at combinator index 4 here because the lens was built when
# M was treated as a combinator for direction extraction, even though
# in the neural pathway M is a layer type. The direction data is still
# valid for initializing a mirror — it shows where M-like patterns live.
# D=4, Y=5, W=6, WHNF=7 in the new 8-way dispatch don't have lens data.

# The actual mapping for 8-op dispatch:
#   Combinator.K=0, I=1, B=2, C=3, D=4, Y=5, W=6, WHNF=7
# Lens provides: K, I, B, C, M (indices 0-3 map directly, M→index 4 in old)
# In the new 8-op system: K=0, I=1, B=2, C=3 map directly from lens
# D=4 has no lens data, but M's direction could inform it (M≠D though)
# Simplest: burn K,I,B,C into mirrors 0-3. Leave 4-7 random.
BURN_MAP = {0: "K", 1: "I", 2: "B", 3: "C"}
# M direction could optionally be used for one of the new ops, but
# it's safer to leave them random and let holographic recording find them.


def direction_to_ternary(direction: np.ndarray, threshold: float = 0.0) -> np.ndarray:
    """Convert a float direction vector to ternary signs.

    Args:
        direction: (d,) float vector (should be unit-normalized or near it)
        threshold: minimum magnitude to be non-zero (0.0 = pure sign)

    Returns:
        (d,) int8 array of {-1, 0, +1}
    """
    signs = np.sign(direction).astype(np.int8)
    if threshold > 0:
        # Zero out small-magnitude positions (these are ambiguous)
        abs_dir = np.abs(direction)
        signs[abs_dir < threshold] = 0
    return signs


def build_mirror_weight(direction: np.ndarray, d_model: int = 512) -> mx.array:
    """Build a full (d_model × d_model) ternary mirror from a direction vector.

    The mirror acts as y = W @ x (with ternary W). We want it to:
    1. Preserve most of x (identity-like baseline)
    2. Add a bias toward the operation's direction d

    Strategy: Identity + rank-1 projection toward d.
    In ternary: W[i, j] = sign(δ_ij + α * d[i] * d[j])

    With α=1 and unit d:
    - Diagonal: sign(1 + d[i]²) = +1 always (identity preserved)
    - Off-diagonal: sign(d[i] * d[j]) = the outer product structure
    - Net effect: output = x + projection_toward_d(x)

    This is the ternary approximation of I + d⊗d — an identity-plus-
    projection operator that biases computation toward the operation's
    subspace while preserving input information.

    The holographic recording will refine this from the starting point.
    """
    d = direction / (np.linalg.norm(direction) + 1e-8)  # unit normalize

    # Build I + α * outer(d, d), then take signs
    # α controls how much the direction dominates over identity
    # α=0.5: mild bias (identity dominates for small d[i]*d[j])
    # α=2.0: strong bias (direction dominates for most positions)
    alpha = 1.0  # balanced: identity and direction roughly equal weight

    identity = np.eye(d_model, dtype=np.float32)
    outer = np.outer(d, d)  # (d_model, d_model)
    combined = identity + alpha * outer
    signs = np.sign(combined).astype(np.int8)

    # sign(1 + α*d[i]*d[j]) for diagonal is always +1 (since d[i]² ≥ 0)
    # Off-diagonal: sign(α*d[i]*d[j]) = sign(d[i])*sign(d[j])
    # So this effectively creates:
    #   diagonal = all +1
    #   off-diagonal = sign(d[i]) * sign(d[j])
    # Which is the identity matrix XOR'd with the outer product pattern.

    return pack_ternary_mlx(mx.array(signs))


def burn_lens_into_model(
    model: V12Model,
    lens_path: str = "lens/warped_lens.npz",
    pass_idx: int = 3,  # which pass's directions to use (apex = most informative)
    verbose: bool = True,
) -> dict:
    """Write warped lens directions into combinator mirrors.

    Args:
        model: V12Model with stride_stack.combinator_mirrors
        lens_path: path to warped_lens.npz
        pass_idx: which pass index to use for the direction extraction
                  (default: 3 = apex, where K/I are strongest)
        verbose: print progress

    Returns:
        Dict with burn stats
    """
    lens = np.load(lens_path)
    d_model = model.cfg.d_model

    mirrors = model.stride_stack.combinator_mirrors
    assert len(mirrors) == N_COMBINATORS, \
        f"Expected {N_COMBINATORS} mirrors, got {len(mirrors)}"

    stats = {"burned": [], "skipped": [], "pass_idx": pass_idx}

    for comb_idx, op_name in BURN_MAP.items():
        key = f"pass_{pass_idx}_dir_{op_name}"
        if key not in lens:
            if verbose:
                print(f"  ⚠️  {op_name} (idx={comb_idx}): no lens data at pass {pass_idx}")
            stats["skipped"].append(op_name)
            continue

        direction = lens[key]  # (512,) float32
        assert direction.shape == (d_model,), \
            f"Direction shape mismatch: {direction.shape} vs ({d_model},)"

        # Convert to ternary mirror weight
        new_weight = build_mirror_weight(direction, d_model)
        mx.eval(new_weight)

        # Write into the mirror
        mirrors[comb_idx].weight = new_weight

        # Compute angular info
        mag = float(np.linalg.norm(direction))
        n_nonzero = int(np.count_nonzero(np.sign(direction)))

        if verbose:
            print(f"  ✓ {op_name} (idx={comb_idx}): burned from pass {pass_idx} "
                  f"(|d|={mag:.3f}, nonzero={n_nonzero}/{d_model})")
        stats["burned"].append(op_name)

    # Remaining mirrors (D=4, Y=5, W=6, WHNF=7) stay at random init
    for idx in range(N_COMBINATORS):
        if idx not in BURN_MAP:
            name = COMBINATOR_NAMES[idx]
            if verbose:
                print(f"  ○ {name} (idx={idx}): no lens data, keeping random init")
            stats["skipped"].append(name)

    # Restore ternary state
    freeze_ternary_weights(model)
    restore_ternary(model)
    mx.eval(model.parameters())

    return stats


def verify_burn(model: V12Model, lens_path: str, pass_idx: int = 3) -> dict:
    """Verify that mirror signs correlate with lens directions.

    After burning, the mirror's sign pattern should correlate with
    the teacher's direction. This checks that the burn was effective.
    """
    lens = np.load(lens_path)
    mirrors = model.stride_stack.combinator_mirrors
    d_model = model.cfg.d_model

    results = {}
    for comb_idx, op_name in BURN_MAP.items():
        key = f"pass_{pass_idx}_dir_{op_name}"
        if key not in lens:
            continue

        direction = lens[key]
        # Get mirror's effective direction (diagonal of the outer product)
        w = unpack_ternary_mlx(mirrors[comb_idx].weight)  # (d_model, d_model) int8
        mx.eval(w)
        w_np = np.array(w)

        # The mirror's "preferred direction" is its principal axis
        # For outer-product initialization: row_sums ∝ direction
        row_sums = w_np.sum(axis=1).astype(np.float32)
        row_sums_norm = row_sums / (np.linalg.norm(row_sums) + 1e-8)

        # Cosine similarity with original direction
        dir_norm = direction / (np.linalg.norm(direction) + 1e-8)
        cos_sim = float(np.dot(row_sums_norm, dir_norm))
        results[op_name] = cos_sim

    return results


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Lens burn — initialize combinator mirrors from teacher directions"
    )
    parser.add_argument("--lens", default="lens/warped_lens.npz",
                        help="Path to warped lens .npz file")
    parser.add_argument("--pass-idx", type=int, default=3,
                        help="Which pass's directions to use (default: 3=apex)")
    parser.add_argument("--checkpoint-dir", default="checkpoints/v12-holo-8op",
                        help="Where to save the burned model")
    parser.add_argument("--verify", action="store_true",
                        help="Run verification after burn")

    args = parser.parse_args()

    # ── Create model ──────────────────────────────────────────
    cfg = V12Config()
    print("Lens Burn — Initializing combinator mirrors from teacher", file=sys.stderr)
    print(f"  Lens: {args.lens}", file=sys.stderr)
    print(f"  Pass index: {args.pass_idx} (0=shallow, 3=apex, 6=output)", file=sys.stderr)
    print(file=sys.stderr)

    print("Creating model...", file=sys.stderr)
    model = create_model(cfg)
    mx.eval(model.parameters())
    params = count_parameters(model)
    print(f"  Parameters: {params['total']:,}", file=sys.stderr)
    print(file=sys.stderr)

    # ── Burn ──────────────────────────────────────────────────
    print("Burning lens directions into combinator mirrors...", file=sys.stderr)
    stats = burn_lens_into_model(
        model, lens_path=args.lens, pass_idx=args.pass_idx
    )
    print(file=sys.stderr)
    print(f"  Burned: {', '.join(stats['burned'])}", file=sys.stderr)
    print(f"  Skipped: {', '.join(stats['skipped'])}", file=sys.stderr)

    # ── Verify ────────────────────────────────────────────────
    if args.verify:
        print("\nVerifying burn (mirror ↔ lens cosine)...", file=sys.stderr)
        cos_sims = verify_burn(model, args.lens, args.pass_idx)
        for op, cos in cos_sims.items():
            status = "✓" if cos > 0.5 else "⚠️"
            print(f"  {status} {op}: cos={cos:.3f}", file=sys.stderr)

    # ── Save ──────────────────────────────────────────────────
    ckpt_dir = Path(args.checkpoint_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving burned model to {ckpt_dir}...", file=sys.stderr)
    flat = dict(tree_flatten(model.trainable_parameters()))
    mx.savez(str(ckpt_dir / "weights_burned.npz"), **flat)

    import json
    state = {
        "stage": "lens_burn",
        "lens_path": args.lens,
        "pass_idx": args.pass_idx,
        "burned_ops": stats["burned"],
        "skipped_ops": stats["skipped"],
    }
    with open(ckpt_dir / "burn_state.json", "w") as f:
        json.dump(state, f, indent=2)

    print(f"  💾 Saved: {ckpt_dir / 'weights_burned.npz'}", file=sys.stderr)
    print(f"  💾 State: {ckpt_dir / 'burn_state.json'}", file=sys.stderr)
    print("\n✓ Lens burn complete. Ready for holographic recording.", file=sys.stderr)


if __name__ == "__main__":
    main()
