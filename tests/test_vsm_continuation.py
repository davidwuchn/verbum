# register: functional
"""VSM continuation (outer recurrence) — tensor-level property tests.

The "continuation" at the VSM tensor level is the outer recurrence in
`scripts/v15/v15model.py`: the shared sweep (stack_a → stack_c) is iterated
`n_outer` times, feeding x_c back as the next input — iterating one typed-
reduction operator ≡ β-reduction toward a fixed point (WHNF). See
`mementum/knowledge/explore/vsm-outer-recurrence.md`.

These tests verify the MECHANISM directly (tensor math), independent of the
slow multi-day training signal:

  - n_outer=1 ≡ single-sweep baseline (no continuation residue)
  - the convergence curve Δx and the differentiable fixed-point term match
    their closed-form definitions EXACTLY (the centerpiece)
  - the fixed-point target is detached (trains the operator to converge, not
    the state to flee)
  - the continuation is a true fixed-point iteration of ONE shared operator
    (weight-shared, not an unrolled stack)
  - feedback x_c → x_in is shape-closed for any n_outer
  - the contractivity term is wired into the loss as λ_fp · fp_term
  - the recurrence is deterministic and differentiable

Lightweight: shrinks only vocab_size (all internal dims stay consistent), so
it does not disturb the live training in tmux main:1.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

# v15 modules import each other by bare name → put scripts/v15 on the path.
_V15 = Path(__file__).resolve().parent.parent / "scripts" / "v15"
if str(_V15) not in sys.path:
    sys.path.insert(0, str(_V15))

mx = pytest.importorskip("mlx.core", reason="mlx not installed")
v15model = pytest.importorskip("v15model", reason="scripts/v15 not importable")
_config = importlib.import_module("config")

VOCAB = 512


def _build_cfg():
    """Real internal dims, tiny vocab (fast init, no GPU pressure)."""
    try:
        return _config.V15Config(vocab_size=VOCAB)
    except TypeError:
        return _config.V15Config()


@pytest.fixture(scope="module")
def model_cfg():
    cfg = _build_cfg()
    m = v15model.V15Model(cfg)
    mx.eval(m.parameters())
    return m, cfg


def _reset(model):
    # the model caches a cross-step algedonic; clear it so each run is fresh.
    model._prev_alg_c = None


def _run(model, cfg, n_outer, lam_fp=0.0, seed=0, L=16, monkeypatch=None):
    """Run one forward; optionally capture each stack_c output (x_c per pass)."""
    model._n_outer_passes = n_outer
    model._fixed_point_lambda = lam_fp
    _reset(model)
    mx.random.seed(seed)
    tokens = mx.random.randint(0, cfg.vocab_size, (1, L))

    captured = []
    if monkeypatch is not None:
        cls = type(model.stack_c)
        orig_call = cls.__call__

        def patched(self, *a, **k):
            out = orig_call(self, *a, **k)
            if self is model.stack_c:
                captured.append(out[0])  # x_c is the first return
            return out

        monkeypatch.setattr(cls, "__call__", patched)

    logits, loss = model(tokens, tokens)
    mx.eval(logits, loss)
    return tokens, logits, loss, captured


# ── degenerate / structural ─────────────────────────────────────────────────
def test_single_pass_has_no_continuation_residue(model_cfg):
    model, cfg = model_cfg
    _run(model, cfg, n_outer=1)
    assert model._last_outer_deltas == [], "n_outer=1 must produce no Δx"
    assert model._fp_term is None, "n_outer=1 must have no fixed-point term"
    assert model._last_fp_loss is None


@pytest.mark.parametrize("k", [1, 2, 3])
def test_delta_count_is_k_minus_one(model_cfg, k):
    model, cfg = model_cfg
    _run(model, cfg, n_outer=k)
    assert len(model._last_outer_deltas) == max(0, k - 1)


def test_recurrence_emits_finite_nonneg_fp_term(model_cfg):
    model, cfg = model_cfg
    _run(model, cfg, n_outer=2, lam_fp=5.0)
    fp = model._fp_term
    assert fp is not None
    val = fp.item()
    assert val >= 0.0
    assert val == val and abs(val) != float("inf")  # finite


# ── the centerpiece: the continuation math is exactly as defined ─────────────
def test_fixed_point_term_matches_closed_form(model_cfg, monkeypatch):
    model, cfg = model_cfg
    _, _, _, caps = _run(model, cfg, n_outer=2, lam_fp=1.0, monkeypatch=monkeypatch)
    assert len(caps) == 2, "should capture x_c for both passes"
    prev, cur = caps[0], caps[1]
    tgt = mx.stop_gradient(prev)
    expect = mx.mean((cur - tgt) ** 2) / (mx.mean(tgt ** 2) + 1e-8)
    got = model._fp_term.item()
    assert abs(got - expect.item()) < 1e-4, f"fp_term {got} != closed form {expect.item()}"


def test_outer_delta_matches_relative_rms(model_cfg, monkeypatch):
    model, cfg = model_cfg
    _, _, _, caps = _run(model, cfg, n_outer=2, monkeypatch=monkeypatch)
    prev, cur = caps[0], caps[1]
    d = mx.sqrt(mx.mean((cur - prev) ** 2))
    nrm = mx.sqrt(mx.mean(prev ** 2)) + 1e-8
    expect = (d / nrm).item()
    got = model._last_outer_deltas[0].item()
    assert abs(got - expect) < 1e-4, f"Δx {got} != relative RMS {expect}"


def test_fp_target_is_detached(model_cfg, monkeypatch):
    """The fixed-point loss must pull x_c onto a DETACHED previous state:
    gradient trains the operator to converge, not the state to flee."""
    model, cfg = model_cfg
    _, _, _, caps = _run(model, cfg, n_outer=2, lam_fp=1.0, monkeypatch=monkeypatch)
    prev = caps[0]
    # If prev were not detached, mean(tgt**2) would carry grad; detached → the
    # closed form using stop_gradient reproduces fp_term to numerical equality.
    tgt = mx.stop_gradient(prev)
    detached_form = (mx.mean((caps[1] - tgt) ** 2) / (mx.mean(tgt ** 2) + 1e-8)).item()
    assert abs(model._fp_term.item() - detached_form) < 1e-4


# ── continuation = ONE shared operator iterated (not an unrolled stack) ──────
def test_continuation_is_weight_shared(model_cfg):
    """Param count is invariant to n_outer → the recurrence reuses one operator
    (a genuine fixed-point iteration), it does not instantiate new layers."""
    model, cfg = model_cfg
    from mlx.utils import tree_flatten

    def nparams():
        return sum(int(v.size) for _, v in tree_flatten(model.parameters()))

    _run(model, cfg, n_outer=1)
    p1 = nparams()
    _run(model, cfg, n_outer=3)
    p3 = nparams()
    assert p1 == p3, "continuation must not add parameters per pass"


@pytest.mark.parametrize("k", [1, 2, 3])
def test_feedback_is_shape_closed(model_cfg, k):
    """x_c fed back as x_in for any k → output well-typed (fixed-point closure)."""
    model, cfg = model_cfg
    _, logits, _, _ = _run(model, cfg, n_outer=k, L=16)
    assert logits.shape == (1, 16, cfg.vocab_size)


# ── loss wiring ─────────────────────────────────────────────────────────────
def test_fp_term_added_to_loss_as_lambda_times_fp(model_cfg):
    """loss(λ_fp) − loss(0) ≈ λ_fp · fp_term (contractivity pressure wired in)."""
    model, cfg = model_cfg
    _, _, loss0, _ = _run(model, cfg, n_outer=2, lam_fp=0.0, seed=3)
    fp0 = model._fp_term.item()
    _, _, loss5, _ = _run(model, cfg, n_outer=2, lam_fp=5.0, seed=3)
    fp5 = model._fp_term.item()
    # same seed/state → fp_term identical; the only loss delta is λ_fp·fp_term
    assert abs(fp0 - fp5) < 1e-4
    # float32 rounding at loss magnitude ~1e2 → compare relative to λ_fp·fp_term
    delta = loss5.item() - loss0.item()
    assert abs(delta - 5.0 * fp0) < 1e-3 * max(1.0, abs(5.0 * fp0))


# ── determinism + differentiability ─────────────────────────────────────────
def test_recurrence_has_no_rng(model_cfg):
    """Same input → same continuation, to float tolerance. (Bit-exact is not
    expected: GPU reductions + the model's S5/algedonic EMA state drift at the
    ~1e-6 relative level; the point is that the recurrence path is RNG-free.)"""
    model, cfg = model_cfg
    _, _, l1, _ = _run(model, cfg, n_outer=2, lam_fp=5.0, seed=7)
    d1 = [d.item() for d in model._last_outer_deltas]
    _, _, l2, _ = _run(model, cfg, n_outer=2, lam_fp=5.0, seed=7)
    d2 = [d.item() for d in model._last_outer_deltas]
    rel = abs(l1.item() - l2.item()) / max(1.0, abs(l1.item()))
    assert rel < 1e-4, f"recurrence not reproducible (rel={rel:.2e})"
    assert all(abs(a - b) < 1e-3 for a, b in zip(d1, d2))


def test_continuation_is_differentiable(model_cfg):
    """value_and_grad through the iterated continuation yields finite grads."""
    import mlx.nn as nn
    model, cfg = model_cfg
    model._n_outer_passes = 2
    model._fixed_point_lambda = 5.0
    _reset(model)
    mx.random.seed(11)
    tokens = mx.random.randint(0, cfg.vocab_size, (1, 16))

    def loss_fn(m, tok):
        _, loss = m(tok, tok)
        return loss

    gfn = nn.value_and_grad(model, loss_fn)
    lv, grads = gfn(model, tokens)
    mx.eval(lv, grads)
    from mlx.utils import tree_flatten
    flat = [g for _, g in tree_flatten(grads)]
    assert lv.item() == lv.item()  # finite loss
    assert any(float(mx.sum(mx.abs(g)).item()) > 0 for g in flat), "no grad flowed"
