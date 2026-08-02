"""verbum.memory.fold — the rf and its drivers. The log IS the source of truth.

state(t) = reduce(rf, deltas[0..t], base)          — exact, linear, Z^D

The ENTIRE determinism proof obligation localizes in rf: signed-integer
addition is associative and commutative, so any fold order over any prefix
yields bit-identical state on every platform. Drivers (write / replay /
squash / undo) are thin — they only choose WHICH prefix to fold; they never
touch the arithmetic (Hickey rf→rf: transducer separated from transport).

Register discipline: this module is the LINEAR register only. sign() lives in
readout.py at completion — it cannot appear mid-chain by construction.
"""
from __future__ import annotations

from collections.abc import Iterable

import numpy as np

__all__ = ["DeltaLog", "fold", "rf"]


def _as_vote(x: np.ndarray, name: str) -> np.ndarray:
    a = np.asarray(x)
    if a.dtype.kind != "i":
        raise TypeError(
            f"{name} must have a signed-integer dtype (linear vote register), "
            f"got {a.dtype}"
        )
    return a.astype(np.int64)


def rf(acc: np.ndarray, delta: np.ndarray) -> np.ndarray:
    """The reducing function: acc + Δ in Z^D. Associative → order-free."""
    return _as_vote(acc, "acc") + _as_vote(delta, "delta")


def fold(deltas: Iterable[np.ndarray], base: np.ndarray) -> np.ndarray:
    """reduce(rf, deltas, base). Returns a fresh int64 vote state."""
    acc = _as_vote(base, "base").copy()
    for d in deltas:
        acc = rf(acc, d)
    return acc


class DeltaLog:
    """Append-only Δ-log with a base — git semantics in the tensor medium.

    - append(Δ)      — commit
    - state(upto)    — checkout: fold of base + deltas[:upto] (time travel)
    - undo(i)        — revert: append -Δ_i (history preserved)
    - squash(upto)   — s262 compaction: new DeltaLog whose base absorbs the
                       prefix; the remaining suffix carries on. Lossy for
                       history BEFORE upto, exact for state at and after.
    """

    def __init__(self, dim: int, base: np.ndarray | None = None):
        self.dim = int(dim)
        if base is None:
            self.base = np.zeros(self.dim, dtype=np.int64)
        else:
            b = _as_vote(base, "base")
            if b.shape != (self.dim,):
                raise ValueError(f"base shape {b.shape} != ({self.dim},)")
            self.base = b.copy()
        self.deltas: list[np.ndarray] = []

    def __len__(self) -> int:
        return len(self.deltas)

    def append(self, delta: np.ndarray) -> int:
        """Commit a Δ; returns its index."""
        d = _as_vote(delta, "delta")
        if d.shape != (self.dim,):
            raise ValueError(f"delta shape {d.shape} != ({self.dim},)")
        self.deltas.append(d)
        return len(self.deltas) - 1

    def state(self, upto: int | None = None) -> np.ndarray:
        """Fold base + deltas[:upto]. upto=None → full head; upto=k → time
        travel to just after the k-th commit (upto=0 → base)."""
        sl = self.deltas if upto is None else self.deltas[:upto]
        return fold(sl, self.base)

    def undo(self, i: int) -> int:
        """Exact erasure of commit i by appending its negation (git revert)."""
        return self.append(-self.deltas[i])

    def squash(self, upto: int) -> DeltaLog:
        """Compact the prefix into a new base (trade history for space —
        Shannon's rent). Returns a NEW log; self is untouched."""
        new = DeltaLog(self.dim, base=self.state(upto))
        new.deltas = [d.copy() for d in self.deltas[upto:]]
        return new
