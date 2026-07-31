"""verbum.dsp.readout — the ONLY torch boundary (thin adapters, lazy import).

L2: converts model-world to arrays; L0/L1 own everything downstream.
dsp never loads a model — instruments own their model, items, and pre-reg.
torch is imported lazily inside functions so `import verbum.dsp` works in a
numpy-only environment (L0/L1 unaffected).
"""
from __future__ import annotations

import numpy as np

__all__ = [
    "as_array",
    "logit_lens",
    "make_capture_hook",
    "rmsnorm_np",
    "surprisal_from_logits",
]


def as_array(x) -> np.ndarray:
    """torch.Tensor (any device/dtype) | array-like -> float32 numpy array."""
    if isinstance(x, np.ndarray):
        return x.astype(np.float32, copy=False)
    try:
        import torch  # lazy: the only torch touchpoint in verbum.dsp
        if isinstance(x, torch.Tensor):
            return x.detach().to(torch.float32).cpu().numpy()
    except ImportError:
        pass
    return np.asarray(x, dtype=np.float32)


def rmsnorm_np(h: np.ndarray, gamma: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """RMSNorm in numpy (the norm_f lesson, s286: hidden_states[-1] is
    POST-final-norm — when you capture the pre-norm residual, apply this
    explicitly so representation matches reality)."""
    rms = np.sqrt(np.mean(h.astype(np.float64) ** 2, axis=-1, keepdims=True) + eps)
    return ((h / rms) * gamma).astype(np.float32)


def logit_lens(h: np.ndarray, w_unembed: np.ndarray,
               gamma: np.ndarray | None = None) -> np.ndarray:
    """Project residual states onto the vocabulary: (RMSNorm(h) if gamma) @ W_U^T.

    h: (..., D); w_unembed: (V, D); returns (..., V) float32 logits."""
    x = rmsnorm_np(h, gamma) if gamma is not None else h
    return x @ w_unembed.T


def surprisal_from_logits(logits: np.ndarray, token_id: int) -> float:
    """-log P(token) from a single logit row, numerically stable, natural log."""
    row = logits.astype(np.float64)
    row = row - row.max()
    return float(np.log(np.exp(row).sum()) - row[token_id])


def make_capture_hook(store: dict, key: str, position: int | None = -1):
    """Forward-hook factory: store[key] = float32 numpy copy of the output
    residual (tuple-unwrapped), at `position` (None = all positions).

    Register on a decoder layer (or via forward-PRE-hook on norm_f for the
    pre-final-norm residual — the s286 recon lesson lives with the caller)."""
    def hook(_module, _inp, out):
        h = out[0] if isinstance(out, tuple) else out
        sl = h if position is None else h[:, position]
        store[key] = as_array(sl)
    return hook
