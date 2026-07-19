#!/usr/bin/env python3
"""Uniform gate/up-proj capture across architectures — feeds the crystal reader.

This is the plumbing that :mod:`topology` makes model-agnostic. Given any model,
:func:`capture_gate`:

  1. auto-detects the routing register (``topology.detect_topology``);
  2. hooks *every* layer's routing module -- the SwiGLU/GeGLU ``gate_proj``, the
     un-gated up-projection proxy (``dense_h_to_4h`` etc.), or the gate half of a
     fused ``gate_up_proj`` -- via plain forward hooks;
  3. runs ONE forward pass;
  4. returns per-layer ``[T, d]`` sign-ready feature matrices (all positions),
     plus the input ids and decoded tokens.

The output feeds the validated ``RelationalCrystalClassifier`` unchanged: it
consumes exactly these per-layer gate feature matrices (sign + common-mode
removal happen there). Capture stays pure -- it does not slice positions, remove
the common-mode, or take the sign; downstream owns the science.

Refuses (raises) for non-traceable topologies (MoE: the register is undecided).

Self-contained: depends only on :mod:`topology`, torch, and numpy. License: MIT.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
from topology import ModelTopology, detect_topology, find_attn_out, gate_path
from torch import nn

__all__ = ["GateCapture", "capture_gate", "self_test"]


@dataclass
class GateCapture:
    """One forward pass' worth of routing-register features.

    Attributes
    ----------
    gate
        ``{layer_index: ndarray[T, d]}`` -- the routing module output at every
        captured layer, float32, on CPU. ``d == topo.gate_width``.
    input_ids
        The token ids fed to the model (length ``T``).
    tokens
        Decoded per-position token strings (length ``T``).
    topo
        The detected :class:`ModelTopology` (records the read register).
    """

    gate: dict[int, np.ndarray]
    input_ids: list[int]
    tokens: list[str]
    topo: ModelTopology
    register: str = "gate"    # which register was captured: "gate" | "attn"

    @property
    def n_tokens(self) -> int:
        return len(self.input_ids)

    @property
    def layers(self) -> list[int]:
        return sorted(self.gate)


def _hidden(out: Any) -> torch.Tensor:
    """Extract the tensor from a module's (possibly tuple) output."""
    return out[0] if isinstance(out, tuple) else out


@torch.no_grad()
def capture_gate(
    model: nn.Module,
    tokenizer: Any,
    text: str | None = None,
    *,
    input_ids: torch.Tensor | None = None,
    topo: ModelTopology | None = None,
    layers: list[int] | None = None,
    register: str = "gate",
) -> GateCapture:
    """Capture a routing register at every (or selected) layer in one forward.

    ``register`` selects which module to read:
      - ``"gate"``  the FFN routing register (gate_proj / up-proj proxy / fused
        gate half) — where selection/recursion/share opcodes live.
      - ``"attn"``  the attention write (o_proj) — the value/attention register
        where composition {B,C} is expected to live (s127).

    Provide ``text`` (tokenized here) or pre-tokenized ``input_ids`` (shape
    ``(seq,)`` or ``(1, seq)``). ``topo`` defaults to auto-detection; ``layers``
    defaults to all layers.
    """
    topo = topo if topo is not None else detect_topology(model, model.config)
    if register == "gate":
        if not topo.traceable:
            raise ValueError(
                f"{topo.arch}: register={topo.register!r} is not traceable "
                f"(read_register={topo.read_register!r}); no gate capture available."
            )
        width = topo.gate_width
        fused = topo.register == "gated-fused"

        def _module_for(i: int) -> nn.Module:
            return model.get_submodule(gate_path(topo, i))
    elif register == "attn":
        width, fused = topo.attn_width, False

        def _module_for(i: int) -> nn.Module:
            # per-layer resolution — hybrid stacks mix o_proj / out_proj writes
            layer_mod = model.get_submodule(f"{topo.layers_path}.{i}")
            fa = find_attn_out(layer_mod)
            if fa is None:
                raise ValueError(
                    f"{topo.arch}: layer {i} has no resolvable attention output "
                    "projection (add its name to _ATTN_OUT_ATTRS)."
                )
            return fa[1]
    else:
        raise ValueError(f"register must be 'gate' or 'attn', got {register!r}")
    layer_ids = list(layers) if layers is not None else list(range(topo.n_layers))

    dev = next(model.parameters()).device
    if input_ids is not None:
        ids = input_ids if input_ids.dim() == 2 else input_ids.unsqueeze(0)
        inputs = {"input_ids": ids.to(dev)}
    elif text is not None:
        inputs = tokenizer(text, return_tensors="pt").to(dev)
    else:
        raise ValueError("capture_gate needs `text` or `input_ids`")

    store: dict[int, np.ndarray] = {}

    def _mk(i: int):
        def hook(_m: nn.Module, _inp: Any, out: Any) -> None:
            h = _hidden(out)          # [B, T, D]
            v = h[0]                  # [T, D]  (single sequence)
            if fused and width:
                v = v[:, :width]      # gate half of the fused gate‖up projection
            store[i] = v.detach().float().cpu().numpy()

        return hook

    handles = []
    try:
        for i in layer_ids:
            handles.append(_module_for(i).register_forward_hook(_mk(i)))
        model(**inputs)
    finally:
        for h in handles:
            h.remove()

    ids_list = inputs["input_ids"][0].detach().cpu().tolist()
    toks = [tokenizer.decode([t]) for t in ids_list]
    return GateCapture(
        gate=store, input_ids=ids_list, tokens=toks, topo=topo, register=register
    )


# ── self-test (tiny model, CPU) ──────────────────────────────────────────────


def self_test(model_name: str = "EleutherAI/pythia-14m-deduped") -> dict:
    """End-to-end capture on a tiny model — exercises the un-gated up-proj path.

    pythia-14m is GPT-NeoX (un-gated) → the capture must route through the
    ``dense_h_to_4h`` up-projection proxy register.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, dtype=torch.float32, attn_implementation="eager"
    ).eval()

    text = "Every student reads a book."
    cap = capture_gate(model, tok, text, register="gate")
    acap = capture_gate(model, tok, text, register="attn")

    d, ad = cap.topo.gate_width, acap.topo.attn_width
    checks = {
        "gate_all_layers": len(cap.gate) == cap.topo.n_layers,
        "gate_shapes_T_d": all(v.shape == (cap.n_tokens, d) for v in cap.gate.values()),
        "gate_finite": all(np.isfinite(v).all() for v in cap.gate.values()),
        "gate_is_upproj": cap.topo.register == "ungated",
        "attn_all_layers": len(acap.gate) == acap.topo.n_layers,
        "attn_shapes_T_d": all(
            v.shape == (acap.n_tokens, ad) for v in acap.gate.values()
        ),
        "attn_finite": all(np.isfinite(v).all() for v in acap.gate.values()),
        "attn_register_tag": acap.register == "attn",
    }
    return {
        "model": model_name,
        "arch": cap.topo.arch,
        "read_register": cap.topo.read_register,
        "n_layers": cap.topo.n_layers,
        "n_tokens": cap.n_tokens,
        "gate_width": d,
        "attn_suffix": cap.topo.attn_suffix,
        "attn_width": ad,
        "gate_shape": next(iter(cap.gate.values())).shape,
        "attn_shape": next(iter(acap.gate.values())).shape,
        "tokens": cap.tokens,
        "checks": checks,
        "all_pass": all(checks.values()),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(self_test(), indent=2, default=str))
