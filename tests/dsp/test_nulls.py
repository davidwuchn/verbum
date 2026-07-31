"""tests/dsp — L1 yardstick: constructors, gate, sign discipline, registers.

The structural claims under test:
- no p without a declared null AND direction (λ yardstick, by shape)
- wrong-sign extremity is verdict=False, never flipped
- register mismatch warns, NEVER mutates value/p/verdict inputs
- null calibration: null data -> p uniform-ish, planted signal -> small p
"""
import dataclasses

import numpy as np
import pytest

from verbum.dsp import (
    Gated,
    NullDraws,
    Register,
    centroid_pr,
    gate,
    matched_random,
    matched_range,
    paired_permutation,
    shuffled_label,
    sign_flip,
)


# ── gate: structural yardstick ─────────────────────────────────────────────────
def _null(vals):
    return NullDraws("test", np.asarray(vals, float), {})


def test_gate_requires_nulldraws_and_direction():
    with pytest.raises(TypeError):
        gate(1.0, np.array([0.0, 0.1]), "greater")       # raw array is not a null
    with pytest.raises(TypeError):
        gate(1.0, None, "greater")
    with pytest.raises(ValueError):
        gate(1.0, _null([0, 0.1]), "two-sided")           # a prediction has a sign
    with pytest.raises(TypeError):
        gate(1.0, _null([0, 0.1]))                        # direction mandatory


def test_gate_pass_and_addone_p():
    g = gate(10.0, _null(np.zeros(99)), "greater")
    assert g.verdict and g.sign_ok
    assert g.p == pytest.approx(1 / 100)                  # add-one smoothing
    assert isinstance(g, Gated)


def test_gate_sign_discipline_no_rescue():
    """Value extreme in the WRONG direction: p(greater) ~ 1, verdict False —
    never flipped to a two-sided 'significant'."""
    g = gate(-10.0, _null(np.zeros(99)), "greater")
    assert not g.sign_ok and not g.verdict
    assert g.p > 0.9


def test_gate_null_zero_draws_refused():
    with pytest.raises(ValueError):
        NullDraws("empty", np.array([]), {})


def test_gated_is_frozen():
    g = gate(1.0, _null([0.0, 0.5]), "greater")
    with pytest.raises(dataclasses.FrozenInstanceError):
        g.p = 0.001


def test_register_mismatch_warns_but_never_mutates():
    n = _null(np.zeros(199))
    clean = gate(5.0, n, "greater", name="clean",
                 claim_register=Register.routing, probe_register=Register.routing)
    warned = gate(5.0, n, "greater", name="warned",
                  claim_register=Register.routing, probe_register=Register.value)
    assert clean.warnings == ()
    assert len(warned.warnings) == 1 and "register mismatch" in warned.warnings[0]
    # data identical: warnings never alter values (decision 2)
    for f in ("value", "p", "null_mean", "null_std", "sign_ok", "verdict"):
        assert getattr(warned, f) == getattr(clean, f)


# ── constructors ───────────────────────────────────────────────────────────────
def test_shuffled_label_planted_structure_beats_null():
    rng = np.random.default_rng(0)
    axis = rng.standard_normal(16)
    x = np.concatenate([i * 5 * axis + rng.standard_normal((25, 16)) * 0.3
                        for i in range(4)])
    y = np.array([f"C{i}" for i in range(4) for _ in range(25)])
    labels = [f"C{i}" for i in range(4)]

    def stat(lab):                                        # full pipeline rerun
        return -centroid_pr(x, lab, labels)               # low-rank -> high stat

    n = shuffled_label(stat, y, np.random.default_rng(1), n_iter=100)
    g = gate(stat(y), n, "greater", name="planted_lowrank")
    assert g.verdict and g.p < 0.05
    assert n.provenance["n_kept"] > 0


def test_shuffled_label_no_structure_is_null():
    rng = np.random.default_rng(2)
    x = rng.standard_normal((100, 16))
    y = np.array([f"C{i}" for i in range(4) for _ in range(25)])
    labels = [f"C{i}" for i in range(4)]

    def stat(lab):
        return -centroid_pr(x, lab, labels)

    n = shuffled_label(stat, y, np.random.default_rng(3), n_iter=100)
    g = gate(stat(y), n, "greater")
    assert g.p > 0.05                                     # random labels: no claim


def test_matched_random_norm_matched():
    rng = np.random.default_rng(4)
    target = rng.standard_normal(32)
    target /= np.linalg.norm(target)

    def stat(v):
        return float(np.abs(v @ target))

    n = matched_random(stat, dim=32, norm=2.0, rng=np.random.default_rng(5),
                       n_iter=200)
    assert n.provenance["norm"] == 2.0
    aligned = stat(2.0 * target)                          # perfectly aligned edit
    assert gate(aligned, n, "greater").verdict


def test_paired_permutation_recovers_planted_shift():
    rng = np.random.default_rng(6)
    b = rng.standard_normal(18)
    a = b + 1.0 + rng.standard_normal(18) * 0.3           # planted +1 pairwise
    n = paired_permutation(a, b, np.random.default_rng(7), n_iter=5000)
    g = gate(float(np.mean(a - b)), n, "greater")
    assert g.verdict and g.p < 0.01
    # no shift -> null
    a2 = b + rng.standard_normal(18) * 0.3
    n2 = paired_permutation(a2, b, np.random.default_rng(8), n_iter=5000)
    assert gate(float(np.mean(a2 - b)), n2, "greater").p > 0.05


def test_sign_flip_symmetric_is_null():
    rng = np.random.default_rng(9)
    v = rng.standard_normal(30)                            # symmetric about 0
    n = sign_flip(v, np.random.default_rng(10), n_iter=5000)
    assert gate(float(v.mean()), n, "greater").p > 0.05
    shifted = v + 1.0
    n2 = sign_flip(shifted, np.random.default_rng(11), n_iter=5000)
    assert gate(float(shifted.mean()), n2, "greater").verdict


def test_matched_range_exposes_forced_fit():
    """The s247 φ-ladder lesson: describable != discovered. Genuine on-grid
    structure beats the matched-range null; arbitrary same-range values must
    NOT beat it beyond the alpha rate (calibration, not a single lucky draw)."""
    grid = 1.0 + np.arange(0, 1.01, 0.25)                 # candidate ratio ladder

    def fit_quality(vals):                                # mean dist to nearest rung
        return -float(np.mean(np.min(np.abs(vals[:, None] - grid[None, :]), axis=1)))

    rng = np.random.default_rng(12)
    # (a) genuinely grid-locked spectrum -> detected
    on_grid = np.repeat(grid, 2)[:8] + rng.standard_normal(8) * 0.005
    n = matched_range(fit_quality, on_grid, np.random.default_rng(13), n_iter=200)
    g = gate(fit_quality(on_grid), n, "greater", name="grid_locked")
    assert g.verdict
    assert n.provenance["lo"] >= 0.9 and n.provenance["hi"] <= 2.1
    # (b) calibration: random same-range spectra fire at ~alpha, not freely
    fires = 0
    for i in range(40):
        t = np.random.default_rng(100 + i).uniform(1.0, 2.0, size=8)
        nn = matched_range(fit_quality, t, np.random.default_rng(200 + i),
                           n_iter=100)
        if gate(fit_quality(t), nn, "greater").verdict:
            fires += 1
    assert fires <= 6                                      # ~alpha, not "always fits"
