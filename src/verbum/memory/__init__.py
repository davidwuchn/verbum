"""verbum.memory — ternary holographic memory (standalone, model-free, deterministic).

Second implementation of the mementum protocol, in a tensor medium
(ternary-holographic-memory.md §4b): Δ-log ≡ commit log, sign-collapse ≡
state.md, squash ≡ s262 compaction, undo = -Δ ≡ git revert.

Transducer decomposition (the s299 transducer math applied to its own artifact):
  encode  — bind ∘ time-permute, stateless map        [encode.py]
  rf      — integer add in Z^D; ALL determinism lives here  [fold.py]
  drivers — write / replay(t') / squash / undo        [fold.py]
  readout — correlate, sign() collapse, at COMPLETION only  [readout.py]

Determinism by construction: integer arithmetic end-to-end (associative add →
order-independent, platform-exact), PCG64 explicit-seed keys, permutations in
place of float mirror angles. sign() is unreachable mid-chain (λ shape:
unreachable > forbidden).
"""
from verbum.memory.encode import bind, encode, keygen, timeshift
from verbum.memory.fold import DeltaLog, fold, rf
from verbum.memory.readout import collapse, correlate, recover, state_hash, unbind

__all__ = [
    "DeltaLog",
    "bind",
    "collapse",
    "correlate",
    "encode",
    "fold",
    "keygen",
    "recover",
    "rf",
    "state_hash",
    "timeshift",
    "unbind",
]
