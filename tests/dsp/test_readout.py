"""tests/dsp — L2 boundary: array adapters, logit lens, surprisal.

No model, no weights download. torch used only if importable (as_array path).
"""
import numpy as np
import pytest

from verbum.dsp.readout import (
    as_array,
    logit_lens,
    rmsnorm_np,
    surprisal_from_logits,
)


def test_l0_l1_import_without_touching_torch():
    """import verbum.dsp must not import torch at module level (L2 lazy)."""
    # structural check on the module source: torch only inside function bodies
    import verbum.dsp.readout as r
    head = open(r.__file__).read().split("def ")[0]
    assert "import torch" not in head


def test_as_array_numpy_passthrough():
    x = np.arange(6, dtype=np.float64).reshape(2, 3)
    out = as_array(x)
    assert out.dtype == np.float32 and out.shape == (2, 3)


def test_as_array_torch_tensor():
    torch = pytest.importorskip("torch")
    t = torch.arange(6, dtype=torch.float16).reshape(2, 3)
    out = as_array(t)
    assert isinstance(out, np.ndarray) and out.dtype == np.float32
    assert np.allclose(out, np.arange(6).reshape(2, 3))


def test_rmsnorm_matches_definition():
    rng = np.random.default_rng(0)
    h = rng.standard_normal((4, 16)).astype(np.float32)
    gamma = np.abs(rng.standard_normal(16)).astype(np.float32) + 0.5
    out = rmsnorm_np(h, gamma)
    rms = np.sqrt((h.astype(np.float64) ** 2).mean(-1, keepdims=True) + 1e-6)
    assert np.allclose(out, (h / rms) * gamma, atol=1e-5)


def test_logit_lens_recovers_planted_token():
    rng = np.random.default_rng(1)
    d, v = 32, 100
    w_u = rng.standard_normal((v, d)).astype(np.float32)
    gamma = np.ones(d, dtype=np.float32)
    h = w_u[42] * 5                                # aligned with token 42
    logits = logit_lens(h, w_u, gamma)
    assert logits.shape == (v,)
    assert int(np.argmax(logits)) == 42


def test_surprisal_from_logits_stable_and_correct():
    logits = np.array([0.0, 1.0, 2.0, 3.0])
    p = np.exp(logits) / np.exp(logits).sum()
    for i in range(4):
        assert surprisal_from_logits(logits, i) == pytest.approx(-np.log(p[i]))
    big = logits + 1e4                                     # overflow guard
    assert np.isfinite(surprisal_from_logits(big, 0))
