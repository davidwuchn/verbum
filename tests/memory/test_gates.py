"""tests/memory — the frozen gates for the ternary holographic store.

G-DET     same seed + op-sequence → identical sha256; write-order within a
          timestep irrelevant (associativity witnessed at the hash level)
G-UNDO    write → undo restores the EXACT prior hash
G-REPLAY  replay fidelity flat vs chain length in vote space (prediction
          from ternary-holographic-memory.md §6a)
G-COMPOSE fold(concat(logs)) ≡ rf-chain of parts (closure theorem as pytest)

Plus: round-trip reads, exact erasure semantics, integer-register boundary
(floats rejected — the no-float invariant is topology, not discipline).
Pure numpy, no model, seconds.
"""
import numpy as np
import pytest

from verbum.memory import (
    DeltaLog,
    bind,
    collapse,
    correlate,
    encode,
    fold,
    keygen,
    recover,
    state_hash,
    timeshift,
    unbind,
)

DIM = 512
SEED = 1234


def ternary_vals(seed: int, n: int, dim: int = DIM) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(-1, 2, size=(n, dim), dtype=np.int8).astype(np.int64)


def build_log(n_items: int, seed: int = SEED, dim: int = DIM) -> tuple:
    keys = keygen(seed, dim, n=max(n_items, 2))
    vals = ternary_vals(seed + 1, n_items, dim)
    log = DeltaLog(dim)
    for t in range(n_items):
        log.append(encode(keys[t], vals[t], t=t))
    return log, keys, vals


# ── G-DET ──────────────────────────────────────────────────────────────────────
def test_gdet_same_seed_same_hash():
    """Two independent builds of the same op-sequence → identical sha256."""
    log_a, _, _ = build_log(16)
    log_b, _, _ = build_log(16)
    assert state_hash(log_a.state()) == state_hash(log_b.state())


def test_gdet_write_order_within_timestep_irrelevant():
    """Associativity at the hash level: permuting the append order of a
    delta batch leaves the folded state bit-identical."""
    keys = keygen(SEED, DIM, n=8)
    vals = ternary_vals(SEED + 1, 8)
    deltas = [encode(keys[i], vals[i], t=0) for i in range(8)]
    order = np.random.default_rng(99).permutation(8)
    fwd = fold(deltas, np.zeros(DIM, dtype=np.int64))
    perm = fold([deltas[i] for i in order], np.zeros(DIM, dtype=np.int64))
    assert state_hash(fwd) == state_hash(perm)


def test_gdet_crosstalk_is_deterministic():
    """Superposition noise is the SAME integer every run."""
    log_a, keys, _ = build_log(12)
    log_b, _, _ = build_log(12)
    ua = unbind(log_a.state(), keys[3], t=3)
    ub = unbind(log_b.state(), keys[3], t=3)
    assert np.array_equal(ua, ub)


# ── G-UNDO ─────────────────────────────────────────────────────────────────────
def test_gundo_exact_erasure():
    """write → undo restores the exact prior hash (undo = −Δ ≡ git revert)."""
    log, keys, vals = build_log(4)
    before = state_hash(log.state())
    i = log.append(encode(keys[1], vals[2], t=7))
    assert state_hash(log.state()) != before
    log.undo(i)
    assert state_hash(log.state()) == before
    # history preserved: the log grew, the state returned
    assert len(log) == 6


def test_gundo_solves_k_by_construction():
    """K-erasure: after undo, the erased item is GONE from the read, the
    surviving item reads back exactly (single remaining exposure)."""
    keys = keygen(SEED, DIM, n=2)
    vals = ternary_vals(SEED + 1, 2)
    log = DeltaLog(DIM)
    log.append(encode(keys[0], vals[0], t=0))
    i = log.append(encode(keys[1], vals[1], t=1))
    log.undo(i)
    assert np.array_equal(unbind(log.state(), keys[0], t=0), vals[0])


# ── G-REPLAY ───────────────────────────────────────────────────────────────────
def test_greplay_time_travel_exact():
    """state(t') from partial fold ≡ state built by only the prefix, for
    every prefix — replay fidelity FLAT vs chain length in vote space."""
    n = 32
    log, keys, vals = build_log(n)
    for t_prime in (0, 1, 7, 16, n):
        prefix = DeltaLog(DIM)
        for t in range(t_prime):
            prefix.append(encode(keys[t], vals[t], t=t))
        assert state_hash(log.state(upto=t_prime)) == state_hash(prefix.state())


def test_greplay_squash_preserves_head_state():
    """Compaction (s262): squashed log has bit-identical head state and
    identical time-travel for t ≥ squash point."""
    log, _keys, _vals = build_log(20)
    sq = log.squash(10)
    assert state_hash(sq.state()) == state_hash(log.state())
    assert state_hash(sq.state(upto=5)) == state_hash(log.state(upto=15))
    assert len(sq) == 10  # history before the squash point is paid to Shannon


# ── G-COMPOSE ──────────────────────────────────────────────────────────────────
def test_gcompose_fold_of_concat_is_fold_of_parts():
    """Closure witnessed end-to-end: fold(a ++ b) ≡ fold(b, base=fold(a))."""
    log, _keys, _vals = build_log(24)
    part_a = log.deltas[:11]
    part_b = log.deltas[11:]
    base = np.zeros(DIM, dtype=np.int64)
    whole = fold(part_a + part_b, base)
    piecewise = fold(part_b, fold(part_a, base))
    assert state_hash(whole) == state_hash(piecewise)


# ── round-trip reads ───────────────────────────────────────────────────────────
def test_single_item_roundtrip_exact():
    key = keygen(SEED, DIM)
    val = ternary_vals(SEED + 1, 1)[0]
    state = encode(key, val, t=5)
    assert np.array_equal(unbind(state, key, t=5), val)
    assert np.array_equal(recover(state, key, t=5).astype(np.int64), val)


def test_superposed_recover_beats_wrong_key_null():
    """Under k=8 superposition, recover() with the TRUE key must beat a
    size-matched wrong-key null (λ yardstick: matched null, no magic
    threshold). Absolute fidelity vs k is P-CAPACITY-LAW's business, not a
    unit test's. Crosstalk is noise, not destruction — and deterministic,
    so this comparison is stable, not flaky."""
    log, keys, vals = build_log(8)
    state = log.state()
    mask = vals[0] != 0

    def agreement(key: np.ndarray) -> float:
        got = recover(state, key, t=0).astype(np.int64)
        return float((got[mask] == vals[0][mask]).mean())

    true_agree = agreement(keys[0])
    null_agree = agreement(keygen(777, DIM))
    assert true_agree > null_agree + 0.05, (
        f"true {true_agree:.2f} !> null {null_agree:.2f} + 0.05"
    )


def test_correlate_present_vs_absent():
    """Matched filter: present (probe, t) exposures score far above absent
    ones and above wrong-time probes (Bragg-style selectivity, time axis)."""
    log, keys, vals = build_log(8)
    state = log.state()
    present = correlate(state, encode(keys[2], vals[2], t=2))
    wrong_time = correlate(state, encode(keys[2], vals[2], t=5))
    absent = correlate(state, encode(keygen(777, DIM), ternary_vals(778, 1)[0], t=2))
    assert present > 2 * abs(wrong_time)
    assert present > 2 * abs(absent)


# ── register boundary ──────────────────────────────────────────────────────────
def test_floats_rejected_everywhere():
    fkey = np.ones(DIM, dtype=np.float32)
    ikey = keygen(SEED, DIM)
    ival = ternary_vals(SEED + 1, 1)[0]
    fstate = np.zeros(DIM, dtype=np.float64)
    with pytest.raises(TypeError):
        bind(fkey, ival)
    with pytest.raises(TypeError):
        timeshift(fkey, 1)
    with pytest.raises(TypeError):
        fold([encode(ikey, ival)], fstate)
    with pytest.raises(TypeError):
        collapse(fstate)
    with pytest.raises(TypeError):
        correlate(fstate, ikey)


def test_collapse_is_ternary_snapshot():
    log, _, _ = build_log(8)
    snap = collapse(log.state())
    assert snap.dtype == np.int8
    assert set(np.unique(snap)).issubset({-1, 0, 1})
