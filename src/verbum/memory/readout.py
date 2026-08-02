"""verbum.memory.readout — completion steps only. The nonlinearity lives here.

sign(a+b) ≠ sign(a) + sign(b): collapse is NOT an rf transform and never
appears mid-chain. Reads are integer correlations — crosstalk from
superposition exists but is DETERMINISTIC noise (the same integer every run).

state_hash is the determinism gate: sha256 over a canonical little-endian
int64 byte layout (platform- and endianness-independent) — commit SHA for
the tensor log.
"""
from __future__ import annotations

import hashlib

import numpy as np

from verbum.memory.encode import bind, timeshift

__all__ = ["collapse", "correlate", "recover", "state_hash", "unbind"]


def unbind(state: np.ndarray, key: np.ndarray, t: int = 0) -> np.ndarray:
    """Invert the encoder: shift back by t, multiply by the ±1 key.

    For state = encode(key, val, t) + noise this returns val + key∘noise —
    the stored value plus deterministic crosstalk. Integer throughout.
    """
    return bind(key, timeshift(np.asarray(state), -t))


def recover(state: np.ndarray, key: np.ndarray, t: int = 0) -> np.ndarray:
    """Ternary estimate of a stored value: sign(unbind(state, key, t)).

    Exact when the item is alone in the medium; under superposition the
    error pattern is deterministic crosstalk (quantify, don't fear)."""
    return np.sign(unbind(state, key, t)).astype(np.int8)


def correlate(state: np.ndarray, probe: np.ndarray, t: int = 0) -> int:
    """Integer matched-filter score: <state, timeshift(probe, t)>.

    High when the (probe, t) exposure is present in the superposition.
    Returns a Python int — exact, no float ever touched.
    """
    s = np.asarray(state)
    p = timeshift(np.asarray(probe), t)
    if s.dtype.kind != "i" or p.dtype.kind != "i":
        raise TypeError("correlate operates on the integer register only")
    return int(np.dot(s.astype(np.int64), p.astype(np.int64)))


def collapse(state: np.ndarray) -> np.ndarray:
    """Ternary snapshot: sign(vote) ∈ {-1, 0, +1} — the lossy checkpoint
    (state.md of the tensor log). Exact history stays in the Δ-log."""
    s = np.asarray(state)
    if s.dtype.kind != "i":
        raise TypeError("collapse operates on the integer register only")
    return np.sign(s).astype(np.int8)


def state_hash(state: np.ndarray) -> str:
    """sha256 of the canonical byte layout: shape header + little-endian
    int64 values. Bit-identical across platforms iff states are equal."""
    s = np.ascontiguousarray(np.asarray(state), dtype="<i8")
    h = hashlib.sha256()
    h.update(np.asarray(s.shape, dtype="<i8").tobytes())
    h.update(s.tobytes())
    return h.hexdigest()
