"""tests/dsp — no-model validation of L0 (the --validate pattern promoted).

Planted-signal detection, calibration ~1, orthonormality/span, stride-aware
bands, gain-law interp. Pure numpy, seconds to run.
"""
import numpy as np
import pytest

from verbum.dsp import (
    Chain,
    centroid_pr,
    centroids,
    find_band,
    g_of,
    gain_law,
    head_gain_ratios,
    layer_geometry,
    map_basis,
    nearest_centroid_acc,
    participation_ratio,
    role_subspace,
    standardize,
    standardize_stats,
    subspace_energy,
    whiten_cov,
)

RNG = np.random.default_rng(0)


# ── whiten ─────────────────────────────────────────────────────────────────────
def test_standardize_zero_mean_unit_var():
    x = RNG.standard_normal((500, 32)) * 7 + 3
    z = standardize(x)
    assert np.allclose(z.mean(axis=0), 0, atol=1e-6)
    assert np.allclose(z.std(axis=0), 1, atol=1e-3)


def test_standardize_kills_rogue_dimension():
    """The 1a massive-activation lesson: one rogue dim must not dominate PR."""
    x = RNG.standard_normal((400, 16))
    x[:, 0] *= 1e4                                   # rogue dimension
    sv_raw = np.linalg.svd(x - x.mean(0), compute_uv=False)
    sv_std = np.linalg.svd(standardize(x), compute_uv=False)
    assert participation_ratio(sv_raw) < 1.5         # collapsed by the rogue dim
    assert participation_ratio(sv_std) > 10          # restored after standardize


def test_standardize_stats_roundtrip():
    x = RNG.standard_normal((200, 8)) * 2 + 1
    z, mu, sd = standardize_stats(x)
    assert np.allclose(z * sd + mu, x, atol=1e-4)


def test_whiten_cov_identity_covariance():
    x = RNG.standard_normal((5000, 6)) @ np.diag([5, 4, 3, 2, 1, 0.5])
    w = whiten_cov(x)
    cov = np.cov(w.T)
    assert np.allclose(cov, np.eye(6), atol=0.15)


def test_map_basis_orthonormal_rows():
    b = np.linalg.qr(RNG.standard_normal((32, 3)))[0].T      # (3, 32) orthonormal
    sd = np.abs(RNG.standard_normal(32)) + 0.5
    gamma = np.abs(RNG.standard_normal(32)) + 0.5
    m = map_basis(b, sd, gamma)
    assert m.shape == (3, 32)
    assert np.allclose(m @ m.T, np.eye(3), atol=1e-8)


# ── subspace ───────────────────────────────────────────────────────────────────
def _clustered(n_per=30, k=4, d=24, sep=6.0):
    rng = np.random.default_rng(1)
    cents = rng.standard_normal((k, d)) * sep
    x = np.concatenate([cents[i] + rng.standard_normal((n_per, d))
                        for i in range(k)])
    y = np.array([f"C{i}" for i in range(k) for _ in range(n_per)])
    return x, y, [f"C{i}" for i in range(k)]


def test_participation_ratio_known_values():
    assert participation_ratio(np.array([1.0, 1.0, 1.0, 1.0])) == pytest.approx(4.0)
    assert participation_ratio(np.array([1.0, 0.0])) == pytest.approx(1.0)
    assert participation_ratio(np.array([])) == 0.0


def test_centroids_and_nearest_centroid():
    x, y, labels = _clustered()
    c, present = centroids(x, y, labels)
    assert present == labels and c.shape == (4, 24)
    assert nearest_centroid_acc(x, y, labels) > 0.95


def test_centroid_pr_low_rank_detected():
    """Centroids on a 1-D line -> PR ~1-2 even in high ambient dim."""
    rng = np.random.default_rng(2)
    axis = rng.standard_normal(24)
    x = np.concatenate([i * 4 * axis + rng.standard_normal((30, 24)) * 0.1
                        for i in range(4)])
    y = np.array([f"C{i}" for i in range(4) for _ in range(30)])
    assert centroid_pr(x, y, [f"C{i}" for i in range(4)]) < 2.0


def test_role_subspace_orthonormal_and_spans():
    x, y, labels = _clustered()
    z, _mu, _sd = standardize_stats(x)
    c, present = centroids(z, y, labels)
    geo = {"present": present, "centroids": c}
    q = role_subspace(geo, ["C0", "C1"])
    assert q.shape == (2, 24)
    assert np.allclose(q @ q.T, np.eye(2), atol=1e-8)
    grand = c.mean(axis=0)
    v = c[0] - grand                                  # in-span vector survives
    assert np.linalg.norm((v @ q.T) @ q) == pytest.approx(np.linalg.norm(v), rel=1e-6)
    assert role_subspace(geo, ["C0", "MISSING"]) is None


def test_subspace_energy_accounting():
    """Removed energy == direct computation (realized-not-planned lesson)."""
    rng = np.random.default_rng(3)
    z = rng.standard_normal((100, 12))
    sd = np.abs(rng.standard_normal(12)) + 0.5
    q = np.linalg.qr(rng.standard_normal((12, 2)))[0].T
    direct = np.mean(np.sum((((z @ q.T) @ q) * sd) ** 2, axis=1))
    assert subspace_energy(z, sd, q) == pytest.approx(direct, rel=1e-9)


def test_layer_geometry_planted_vs_shuffled():
    """Planted low-rank clustering beats its shuffled-label null; the geo dict
    feeds role_subspace downstream (the 1b pipeline shape)."""
    rng = np.random.default_rng(4)
    axis = rng.standard_normal(24)
    x = np.concatenate([i * 4 * axis + rng.standard_normal((30, 24)) * 0.3
                        for i in range(4)])
    y = np.array([f"C{i}" for i in range(4) for _ in range(30)])
    geo = layer_geometry(x, y, np.random.default_rng(5), n_null=100,
                         label_order=[f"C{i}" for i in range(4)])
    assert geo["p_lowrank"] < 0.05                     # real structure detected
    assert geo["pr_real"] < geo["pr_null_mean"]        # low-rank direction
    assert role_subspace(geo, ["C0", "C1"]) is not None


# ── bands (fix #1: stride-aware) ───────────────────────────────────────────────
def _pl(pmap):
    return {L: {"p_lowrank": p} for L, p in pmap.items()}


def test_find_band_stride1_contiguous_run():
    per = _pl({L: (0.01 if 6 <= L <= 12 else 0.5) for L in range(0, 20)})
    assert find_band(per, 20) == list(range(6, 13))


def test_find_band_stride2_contiguous_run():
    """The s284 smoke caveat: stride-2 probing must detect the run, not fall
    through to the interior fallback."""
    per = _pl({L: (0.01 if 8 <= L <= 16 else 0.5) for L in range(0, 32, 2)})
    assert find_band(per, 32) == [8, 10, 12, 14, 16]


def test_find_band_stride2_fallback_window_scales():
    """No run -> +/- 3 PROBED layers around min-p interior layer (stride-aware)."""
    per = _pl({L: 0.5 for L in range(0, 32, 2)})
    per[10]["p_lowrank"] = 0.2                          # interior minimum, not sig
    band = find_band(per, 32)
    assert band == [4, 6, 8, 10, 12, 14, 16]            # 10 +/- 3*stride


def test_find_band_stride2_with_appended_tail_layer():
    """FIX #2 (s288, caught live by the P-TYPE-OV 4B smoke): a stride-2 capture
    with the final layer appended (diff 1 at the tail) must still infer
    stride 2 and find the strided run — not collapse to min(diff)=1."""
    pmap = {L: (0.01 if 8 <= L <= 24 else 0.5) for L in range(0, 36, 2)}
    pmap[35] = 0.5                                       # appended tail layer
    per = _pl(pmap)
    assert find_band(per, 36) == [8, 10, 12, 14, 16, 18, 20, 22, 24]


def test_find_band_p_zero_counts_and_none_is_insignificant():
    per = _pl({L: (0.0 if 5 <= L <= 9 else 0.9) for L in range(0, 16)})
    per[12]["p_lowrank"] = None                          # None -> 1.0 (v3 fix)
    assert find_band(per, 16) == [5, 6, 7, 8, 9]


# ── gain ───────────────────────────────────────────────────────────────────────
def test_head_gain_ratios_planted_and_calibrated():
    """Planted read-direction -> rho >> 1; random basis -> rho ~ 1 (the QK
    --validate pattern: planted p=0.0, unplanted null, calibration ~1)."""
    rng = np.random.default_rng(6)
    d, head_dim, h = 64, 8, 4
    planted = np.linalg.qr(rng.standard_normal((d, 1)))[0].T      # (1, d)
    w = rng.standard_normal((h * head_dim, d)) * 0.1
    w += 3.0 * rng.standard_normal((h * head_dim, 1)) @ planted   # heads read it
    random_basis = np.linalg.qr(rng.standard_normal((d, 1)))[0].T
    rho_planted, rho_random = head_gain_ratios(w, [planted, random_basis], head_dim)
    assert rho_planted > 5.0
    assert 0.2 < rho_random < 3.0
    # calibration: isotropic w reads any direction at rho ~ 1
    w_iso = rng.standard_normal((h * head_dim, d))
    rhos = head_gain_ratios(w_iso, [random_basis], head_dim)
    assert 0.5 < rhos[0] < 2.0


def test_gain_law_interp_exact_and_clamped():
    e = np.array([10.0, 100.0, 1000.0])
    r = np.array([1.0, 0.7, 0.2])
    log_e, ret = gain_law(e[::-1], r[::-1])              # unsorted input ok
    for ei, ri in zip(e, r, strict=True):
        assert g_of(log_e, ret, ei) == pytest.approx(ri)
    assert g_of(log_e, ret, 1.0) == pytest.approx(1.0)    # clamped below
    assert g_of(log_e, ret, 1e6) == pytest.approx(0.2)    # clamped above
    mid = g_of(log_e, ret, 300.0)
    assert 0.2 < mid < 0.7                                # monotone between


# ── chain (exploration-only) ───────────────────────────────────────────────────
def test_chain_composes_left_to_right():
    c = Chain(standardize).then(lambda z: z[:, :2])
    x = RNG.standard_normal((50, 8)) * 3 + 1
    out = c.run(x)
    assert out.shape == (50, 2)
    assert np.allclose(out, standardize(x)[:, :2])
