"""Load vsm_tap dumps into the [T, d] per-layer feature matrices that
``opcodes/classify.py`` consumes.

vsm_tap (the pristine llama.cpp residual/register tap) writes, per prompt:
  <dir>/manifest.json         — model, prompt, tokens, tensor index
  <dir>/<register>-<layer>.bin — raw tensor bytes, ne=[d0, d1, ...] (d0 fastest)

ggml is contiguous in ne[0], so a gate tensor ne=[n_ff, n_tokens] read row-major
as (n_tokens, n_ff) is EXACTLY the [T, d] matrix the classifier wants — no
transpose. This module is the only new glue on the read path; the projection
science is unchanged (opcodes/classify.py).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_DTYPE = {
    "f32": np.float32,
    "f16": np.float16,
    "i32": np.int32,
    "i64": np.int64,
    "i16": np.int16,
    "i8": np.int8,
}


def load_manifest(dump_dir: str | Path) -> dict:
    return json.loads((Path(dump_dir) / "manifest.json").read_text())


def load_register(dump_dir: str | Path, register: str = "ffn_gate") -> dict[int, np.ndarray]:
    """Return ``{layer: [T, d]}`` for one register from a tap dump directory.

    ``[T, d]`` = (n_tokens, feature_dim), float64, matching classify.py.
    """
    dump_dir = Path(dump_dir)
    man = load_manifest(dump_dir)
    out: dict[int, np.ndarray] = {}
    for t in man["tensors"]:
        if t["register"] != register:
            continue
        dt = _DTYPE.get(t["dtype"])
        if dt is None:
            raise ValueError(f"unhandled dtype {t['dtype']!r} for {t['name']}")
        raw = np.fromfile(dump_dir / t["file"], dtype=dt)
        ne = t["ne"]  # [d0(fast), d1, d2, d3]
        n_feat, n_tok = int(ne[0]), int(ne[1])
        # ggml contiguous in ne[0] -> token-major blocks -> (n_tok, n_feat)
        arr = raw.reshape(n_tok, n_feat).astype(np.float64)
        out[int(t["layer"])] = arr
    if not out:
        raise ValueError(f"no tensors for register={register!r} in {dump_dir}")
    return out


def last_token(dump_dir: str | Path, register: str = "ffn_gate") -> dict[int, np.ndarray]:
    """Return ``{layer: [d]}`` — the last-token feature per layer (crystal locus)."""
    return {li: m[-1] for li, m in load_register(dump_dir, register).items()}


def stack_last_token(
    dump_root: str | Path, n_probes: int, register: str = "ffn_gate"
) -> dict[int, np.ndarray]:
    """From a batch dump (``<root>/<idx>/``), stack last-token features across
    probes into ``{layer: [N, d]}`` — the calibrate() input."""
    dump_root = Path(dump_root)
    per_probe = [last_token(dump_root / str(i), register) for i in range(n_probes)]
    layers = sorted(per_probe[0].keys())
    return {li: np.stack([p[li] for p in per_probe], axis=0) for li in layers}
