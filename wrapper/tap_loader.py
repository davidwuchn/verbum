"""Load vsm_tap dumps into the [T, d] per-layer feature matrices that
``opcodes/classify.py`` consumes.

vsm_tap (the pristine llama.cpp residual/register tap) writes, per prompt:
  <dir>/manifest.json          — model, prompt, tokens, tensor index (ne + nb)
  <dir>/<register>-<layer>.bin — raw tensor bytes (the ggml buffer)

Most registers are contiguous (ffn_gate, ffn_moe_gate, l_out), so reading raw as
(n_tokens, feature) is exactly the [T, d] the classifier wants. Some are ggml
VIEWS / argsort results (ffn_moe_topk = a view_4d of the 256-wide argsort with the
parent row stride), so we de-stride using the byte strides ``nb`` recorded in the
manifest. ``_load_token_major`` handles both uniformly. The projection science is
unchanged (opcodes/classify.py).
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


def _load_token_major(dump_dir: Path, t: dict) -> np.ndarray:
    """Load one tensor as C-order axes [.., n_tok, .., feature], squeezing leading
    size-1 dims. Respects ggml byte strides ``nb`` (handles views/argsort). ne[0]
    is the fastest ggml axis, so numpy axes are ne[::-1] with strides nb[::-1]."""
    ne = [int(x) for x in t["ne"]]
    dt = _DTYPE.get(t["dtype"])
    if dt is None:
        raise ValueError(f"unhandled dtype {t['dtype']!r} for {t['name']}")
    raw = np.fromfile(dump_dir / t["file"], dtype=np.uint8)
    typed = raw.view(dt)
    nb = t.get("nb")
    if nb is not None:
        arr = np.lib.stride_tricks.as_strided(
            typed, shape=tuple(ne[::-1]), strides=tuple(int(x) for x in nb[::-1])
        )
        arr = np.ascontiguousarray(arr)
    else:  # legacy dump without strides: assume contiguous
        arr = typed.reshape(tuple(ne[::-1]))
    while arr.ndim > 1 and arr.shape[0] == 1:
        arr = arr[0]
    return arr


def _tensor(man: dict, register: str, layer: int) -> dict | None:
    for t in man["tensors"]:
        if t["register"] == register and int(t["layer"]) == layer:
            return t
    return None


# ── dense register (ffn_gate / l_out): {layer: [T, d]} ──────────────────────


def load_register(dump_dir: str | Path, register: str = "ffn_gate") -> dict[int, np.ndarray]:
    """Return ``{layer: [T, d]}`` (float64) for one register."""
    dump_dir = Path(dump_dir)
    man = load_manifest(dump_dir)
    out: dict[int, np.ndarray] = {}
    for t in man["tensors"]:
        if t["register"] != register:
            continue
        out[int(t["layer"])] = _load_token_major(dump_dir, t).astype(np.float64)
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
# ne=[n_ff, n_expert_used, n_tok] — one gate vector PER SELECTED EXPERT. We combine
# the selected experts by their router weights (ffn_moe_weights) into the effective
# gate the MoE actually computes:
#
#     gate_eff[t, :] = Σ_e  weights[e, t] * ffn_moe_gate[:, e, t]


def load_moe_gate_effective(dump_dir: str | Path) -> dict[int, np.ndarray]:
    """Return ``{layer: [T, n_ff]}`` — router-weighted effective gate per token.
    Falls back to an unweighted mean if ffn_moe_weights is absent."""
    dump_dir = Path(dump_dir)
    man = load_manifest(dump_dir)
    layers = sorted({int(t["layer"]) for t in man["tensors"]
                     if t["register"] == "ffn_moe_gate"})
    out: dict[int, np.ndarray] = {}
    for li in layers:
        tg = _tensor(man, "ffn_moe_gate", li)
        gate = _load_token_major(dump_dir, tg).astype(np.float64)   # (n_tok, n_exp, n_ff)
        tw = _tensor(man, "ffn_moe_weights", li)
        if tw is not None:
            w = _load_token_major(dump_dir, tw).astype(np.float64)  # (n_tok, n_exp)
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


def load_moe_topk(dump_dir: str | Path) -> dict[int, np.ndarray]:
    """Return ``{layer: [T, n_expert_used]}`` int — which experts fired per token.
    ffn_moe_topk is a view of the 256-wide argsort; nb de-striding recovers it."""
    dump_dir = Path(dump_dir)
    man = load_manifest(dump_dir)
    out: dict[int, np.ndarray] = {}
    for t in man["tensors"]:
        if t["register"] != "ffn_moe_topk":
            continue
        out[int(t["layer"])] = np.atleast_2d(_load_token_major(dump_dir, t))
    return out
