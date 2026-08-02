"""verbum.memory.encode — the stateless map transducer: (key, val, t) -> Δ.

encode = timeshift(bind(key, val), t)

- bind: elementwise multiply with a dense ±1 key (self-inverse: k∘k = 1,
  exact unbind). Ternary val ∘ ±1 key stays ternary.
- timeshift: cyclic permutation by t — the DISCRETE mirror angle. Exact,
  invertible, integer-preserving; the deterministic substitute for float
  angular multiplexing (temporal axis of ternary-holographic-memory.md §4).
- undo is not special: encode(key, -val, t) == -encode(key, val, t).

Integer-only boundary: float dtypes are rejected here, so no float can enter
the write path anywhere downstream (λ shape: unreachable > forbidden).
"""
from __future__ import annotations

import numpy as np

__all__ = ["bind", "encode", "keygen", "timeshift"]


def _as_int(x: np.ndarray, name: str) -> np.ndarray:
    """Enforce the integer register. Rejects float/complex/bool dtypes."""
    a = np.asarray(x)
    if a.dtype.kind != "i":
        raise TypeError(
            f"{name} must have a signed-integer dtype (integer register only), "
            f"got {a.dtype}"
        )
    return a


def keygen(seed: int, dim: int, n: int = 1) -> np.ndarray:
    """n dense ±1 keys of length dim from an EXPLICIT integer seed (PCG64).

    Deterministic cross-platform by numpy's Generator bit-stream contract.
    Never derive seeds from Python hash() (s296 salted-hash lesson).
    Returns int8 array of shape (n, dim); squeeze to (dim,) when n == 1.
    """
    rng = np.random.default_rng(seed)
    keys = (rng.integers(0, 2, size=(n, dim), dtype=np.int8) * 2 - 1).astype(np.int8)
    return keys[0] if n == 1 else keys


def bind(key: np.ndarray, val: np.ndarray) -> np.ndarray:
    """key ∘ val — elementwise product in the integer register.

    With ±1 keys this is an involution: bind(key, bind(key, val)) == val.
    """
    k = _as_int(key, "key")
    v = _as_int(val, "val")
    if k.shape != v.shape:
        raise ValueError(f"shape mismatch: key {k.shape} vs val {v.shape}")
    return (k.astype(np.int64) * v.astype(np.int64)).astype(np.int64)


def timeshift(delta: np.ndarray, t: int) -> np.ndarray:
    """Cyclic shift by t — the discrete time-address (permutation ≡ exact
    rotation). Inverse is timeshift(x, -t). t = 0 is the identity."""
    d = _as_int(delta, "delta")
    return np.roll(d, int(t))


def encode(key: np.ndarray, val: np.ndarray, t: int = 0) -> np.ndarray:
    """(key, val, t) -> Δ. The full stateless encoder: timeshift(bind(k, v), t).

    Appending -encode(key, val, t) to the log is exact erasure (undo = -Δ).
    """
    return timeshift(bind(key, val), t)
