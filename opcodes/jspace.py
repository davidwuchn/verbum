#!/usr/bin/env python3
"""J-space operand register — logit-lens readout on any detected topology.

The OPERAND read, complementary to the opcode (operator) registers. Anthropic's
J-lens ("Verbalizable Representations Form a Global Workspace", 2026) reads
what the model is *thinking about* — the verbalizable image of the residual
stream. This module provides that read for the opcode tracer:

  - ``capture_residuals``  per-layer post-block residual states ``[T, d]``
  - ``logit_lens``         residual STATE -> logits (final norm + unembed)
  - ``verbalize``          residual DIRECTION -> top-k tokens (affine-gain read)

HONEST SCOPE (s263 EXP1, null-gated): the J-space/operand register does NOT
identify combinator opcodes — broadcast responses are generic, not
combinator-selective. It reports WHAT is being routed, never WHICH opcode
routes it. The tracer therefore shows it as a side-by-side operand column,
and it must never feed the opcode classifier.

Model-agnostic via :mod:`topology` (``layers_path`` + ``final_norm_path`` +
``unembed_path``) — works on nested containers (Gemma ``language_model``),
hybrid stacks, GPT-NeoX. Plain forward hooks; depends only on topology,
torch, numpy. License: MIT.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from topology import ModelTopology, detect_topology  # noqa: E402

__all__ = [
    "capture_residuals",
    "logit_lens",
    "self_test",
    "verbalize",
    "verbalize_state",
]


def _hidden(out: Any) -> torch.Tensor:
    return out[0] if isinstance(out, tuple) else out


def _norm_unembed(
    model: nn.Module, topo: ModelTopology
) -> tuple[nn.Module, nn.Module]:
    if topo.final_norm_path is None or topo.unembed_path is None:
        raise ValueError(
            f"{topo.arch}: no final-norm/unembed path detected "
            "(extend _NORM_PATHS/_UNEMBED_PATHS in topology.py)."
        )
    return (
        model.get_submodule(topo.final_norm_path),
        model.get_submodule(topo.unembed_path),
    )


# ── residual capture (post-block, all positions) ─────────────────────────────


@torch.no_grad()
def capture_residuals(
    model: nn.Module,
    tokenizer: Any,
    text: str | None = None,
    *,
    input_ids: torch.Tensor | None = None,
    topo: ModelTopology | None = None,
    layers: list[int] | None = None,
) -> dict[int, np.ndarray]:
    """One forward pass -> ``{layer: [T, d]}`` post-block residual states.

    float32 numpy on CPU. Provide ``text`` or pre-tokenized ``input_ids``.
    """
    topo = topo if topo is not None else detect_topology(model, model.config)
    layer_ids = list(layers) if layers is not None else list(range(topo.n_layers))
    dev = next(model.parameters()).device
    if input_ids is not None:
        ids = input_ids if input_ids.dim() == 2 else input_ids.unsqueeze(0)
        inputs = {"input_ids": ids.to(dev)}
    elif text is not None:
        inputs = tokenizer(text, return_tensors="pt").to(dev)
    else:
        raise ValueError("capture_residuals needs `text` or `input_ids`")

    store: dict[int, np.ndarray] = {}

    def _mk(i: int):
        def hook(_m: nn.Module, _inp: Any, out: Any) -> None:
            store[i] = _hidden(out)[0].detach().float().cpu().numpy()

        return hook

    handles = []
    try:
        for i in layer_ids:
            mod = model.get_submodule(f"{topo.layers_path}.{i}")
            handles.append(mod.register_forward_hook(_mk(i)))
        model(**inputs)
    finally:
        for h in handles:
            h.remove()
    return store


# ── logit-lens readouts ──────────────────────────────────────────────────────


@torch.no_grad()
def logit_lens(
    model: nn.Module, topo: ModelTopology, resid: np.ndarray | torch.Tensor
) -> torch.Tensor:
    """Residual STATE(s) ``(..., d)`` -> logits ``(..., vocab)`` (full norm)."""
    norm, unembed = _norm_unembed(model, topo)
    dtype = next(model.parameters()).dtype
    dev = next(model.parameters()).device
    t = torch.as_tensor(np.asarray(resid)) if not torch.is_tensor(resid) else resid
    return unembed(norm(t.to(dtype).to(dev)))


@torch.no_grad()
def verbalize(
    model: nn.Module,
    tokenizer: Any,
    direction: np.ndarray | torch.Tensor,
    *,
    topo: ModelTopology | None = None,
    top_k: int = 8,
) -> list[str]:
    """Top-``k`` tokens a residual DIRECTION points toward.

    Standard direction readout: ``unembed_weight @ (direction * norm.weight)``
    (LayerNorm/RMSNorm affine gain only, no re-centering).
    """
    topo = topo if topo is not None else detect_topology(model, model.config)
    norm, unembed = _norm_unembed(model, topo)
    dev = unembed.weight.device
    d = torch.as_tensor(np.asarray(direction)) if not torch.is_tensor(direction) \
        else direction
    d = d.to(unembed.weight.dtype).to(dev)
    gain = getattr(norm, "weight", None)
    if gain is not None:
        d = d * gain.to(d.dtype)
    col = unembed.weight @ d  # (vocab,)
    idx = torch.topk(col, top_k).indices.tolist()
    return [tokenizer.decode([i]) for i in idx]


@torch.no_grad()
def verbalize_state(
    model: nn.Module,
    tokenizer: Any,
    resid_state: np.ndarray | torch.Tensor,
    *,
    topo: ModelTopology | None = None,
    top_k: int = 8,
) -> list[str]:
    """Top-``k`` tokens for a residual STATE (full logit-lens, with norm)."""
    topo = topo if topo is not None else detect_topology(model, model.config)
    logits = logit_lens(model, topo, resid_state)
    idx = torch.topk(logits.float(), top_k, dim=-1).indices
    return [tokenizer.decode([int(i)]) for i in idx.reshape(-1).tolist()[:top_k]]


# ── self-test (tiny model, CPU) ──────────────────────────────────────────────


def self_test(model_name: str = "EleutherAI/pythia-14m-deduped") -> dict:
    """Ground-truth gate: the logit lens at the FINAL layer must reproduce the
    model's own logits exactly (same norm + unembed applied to the same state).
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, dtype=torch.float32, attn_implementation="eager"
    ).eval()
    topo = detect_topology(model, model.config)

    text = "The cat, not the dog, chased the"
    resids = capture_residuals(model, tok, text, topo=topo)
    with torch.no_grad():
        true_logits = model(**tok(text, return_tensors="pt")).logits[0]

    last = topo.n_layers - 1
    lens_logits = logit_lens(model, topo, resids[last])
    exact = torch.allclose(lens_logits, true_logits, atol=1e-4)

    # mid-stack lens diverges from final (the lens shows REFINEMENT, not noise)
    mid = logit_lens(model, topo, resids[topo.n_layers // 2])
    diverges = not torch.allclose(mid, true_logits, atol=1e-2)

    words = verbalize_state(model, tok, resids[last][-1], topo=topo)
    dwords = verbalize(model, tok, resids[last][-1], topo=topo)

    checks = {
        "residual_shapes": all(
            v.shape == (resids[last].shape[0], topo.hidden_size)
            for v in resids.values()
        ),
        "all_layers_captured": len(resids) == topo.n_layers,
        "final_lens_exact": bool(exact),
        "mid_lens_diverges": bool(diverges),
        "verbalize_k": len(words) == 8 and len(dwords) == 8,
        "finite": all(np.isfinite(v).all() for v in resids.values()),
    }
    return {
        "model": model_name,
        "arch": topo.arch,
        "n_layers": topo.n_layers,
        "norm_path": topo.final_norm_path,
        "unembed_path": topo.unembed_path,
        "last_token_state_verbalize": words,
        "checks": checks,
        "all_pass": all(checks.values()),
    }


if __name__ == "__main__":
    import json

    out = self_test()
    print(json.dumps(out, indent=2, default=str))
    if not out["all_pass"]:
        raise SystemExit(1)
