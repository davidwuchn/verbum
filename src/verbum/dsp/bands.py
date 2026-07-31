"""verbum.dsp.bands — band detection over per-layer statistics.

L0: pure numpy. No torch, no I/O, no model, no experiment logic.

Harvested:
- find_band <- wrapper/type_zone_ablation.py (1b-v4), with FIX #1 (s284 smoke
  caveat): the original assumed layer stride 1 — contiguity was `L == prev + 1`
  and the interior fallback window `lo +/- 3` — so stride-2 probing silently
  fell through to the fallback. This version infers the stride from the probed
  layer keys; stride-1 behavior is IDENTICAL (byte-equivalence gate).
"""
from __future__ import annotations

import numpy as np

__all__ = ["find_band"]


def find_band(per_layer: dict[int, dict], n_layers: int,
              p_key: str = "p_lowrank", alpha: float = 0.05,
              min_len: int = 3) -> list[int]:
    """Longest stride-contiguous run of probed layers with p < alpha.

    per_layer: {layer_index: {p_key: p_value_or_None, ...}}. Layers may be
    probed at any regular stride; contiguity means adjacent PROBED layers.
    Fallback (fewer than min_len significant in a run): a +/- 3-probed-layer
    window around the minimum-p layer in the interior 15-65% of the stack.
    """
    layers = sorted(per_layer)

    def pval(L: int) -> float:
        p = per_layer[L][p_key]
        return 1.0 if p is None else p

    if len(layers) > 1:
        # FIX #2 (s288, caught by the P-TYPE-OV 4B smoke): capture lists often
        # append the final layer to a strided set (e.g. stride 2 + L_last),
        # making min(diff)=1 collapse the inferred stride. Use the MODE of the
        # diffs (ties -> smaller); stride-1 behavior identical.
        diffs = np.diff(layers)
        vals, counts = np.unique(diffs, return_counts=True)
        stride = int(vals[counts.argmax()])
    else:
        stride = 1

    sig = [L for L in layers if pval(L) < alpha]
    best: list[int] = []
    cur: list[int] = []
    for L in sig:
        cur = [*cur, L] if (cur and L == cur[-1] + stride) else [L]
        if len(cur) > len(best):
            best = cur
    if len(best) >= min_len:
        return best
    interior = [L for L in layers
                if n_layers * 0.15 <= L <= n_layers * 0.65]
    if not interior:
        return sig or layers[:min_len]
    lo = min(interior, key=pval)
    return [L for L in layers if lo - 3 * stride <= L <= lo + 3 * stride]
