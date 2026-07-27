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


# ── MoE: the one genuinely new bit of loader logic ──────────────────────────
#
# A dense model has one gate vector per token (ffn_gate ne=[n_ff, n_tok]). A MoE
# routes each token through n_expert_used experts, so ffn_moe_gate is 3D
# ne=[n_ff, n_expert_used, n_tok] — one gate vector PER SELECTED EXPERT. To get a
# single per-token gate comparable to the dense register (and thus usable by the
# frame-invariant crystal projection), we combine the selected experts by their
# router weights (ffn_moe_weights ne=[1, n_expert_used, n_tok]) — the effective
# gate contribution the MoE actually computes:
#
#     gate_eff[t, :] = Σ_e  weights[e, t] * ffn_moe_gate[:, e, t]
#
# This answers the C2/A2 MoE-register question: does the router route the crystal?


def _reshape_token_major(raw: np.ndarray, ne: list[int]) -> np.ndarray:
    """Reshape a ggml dump (ne[0] fastest) to C-order axes [.., n_tok, .., n_ff]
    then squeeze leading size-1 dims. ffn_gate [n_ff,n_tok]->(n_tok,n_ff);
    ffn_moe_gate [n_ff,n_exp,n_tok]->(n_tok,n_exp,n_ff)."""
    dims = [int(x) for x in ne]
    arr = raw.reshape(tuple(dims[::-1]))  # axes [d3, d2, d1, d0]
    while arr.ndim > 1 and arr.shape[0] == 1:
        arr = arr[0]
    return arr


def _tensor(man: dict, register: str, layer: int) -> dict | None:
    for t in man["tensors"]:
        if t["register"] == register and int(t["layer"]) == layer:
            return t
    return None


def load_moe_gate_effective(dump_dir: str | Path) -> dict[int, np.ndarray]:
    """Return ``{layer: [T, n_ff]}`` — the router-weighted effective gate per
    token, aggregated over the selected experts. Falls back to an unweighted mean
    if ffn_moe_weights is absent."""
    dump_dir = Path(dump_dir)
    man = load_manifest(dump_dir)
    layers = sorted({int(t["layer"]) for t in man["tensors"]
                     if t["register"] == "ffn_moe_gate"})
    out: dict[int, np.ndarray] = {}
    for li in layers:
        tg = _tensor(man, "ffn_moe_gate", li)
        dt = _DTYPE[tg["dtype"]]
        gate = _reshape_token_major(
            np.fromfile(dump_dir / tg["file"], dtype=dt), tg["ne"]
        ).astype(np.float64)                       # (n_tok, n_exp, n_ff)
        tw = _tensor(man, "ffn_moe_weights", li)
        if tw is not None:
            w = _reshape_token_major(
                np.fromfile(dump_dir / tw["file"], dtype=_DTYPE[tw["dtype"]]), tw["ne"]
            ).astype(np.float64)                   # (n_tok, n_exp)
            w = w.reshape(gate.shape[0], gate.shape[1])
            out[li] = np.einsum("te,tef->tf", w, gate)
        else:
            out[li] = gate.mean(axis=1)
    return out


def moe_gate_last_token(dump_dir: str | Path) -> dict[int, np.ndarray]:
    return {li: m[-1] for li, m in load_moe_gate_effective(dump_dir).items()}


def stack_moe_last_token(dump_root: str | Path, n_probes: int) -> dict[int, np.ndarray]:
    dump_root = Path(dump_root)
    per_probe = [moe_gate_last_token(dump_root / str(i)) for i in range(n_probes)]
    layers = sorted(per_probe[0].keys())
    return {li: np.stack([p[li] for p in per_probe], axis=0) for li in layers}
