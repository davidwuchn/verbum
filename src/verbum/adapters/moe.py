"""MoE adapter — expert ablation as :mod:`verbum.hooks` interventions.

Targets the Qwen3 MoE family (``qwen3_moe`` 30B, ``qwen3_5_moe`` 35B; the
sparse block exposes ``.gate`` router + fused ``.experts`` + optional
``.shared_expert``). The verified router contract (both families) is::

    Qwen3[_5]MoeTopKRouter.forward(h) -> (router_logits, router_scores, router_indices)
        router_logits  : (tokens, num_experts)  softmax over ALL experts
        router_scores  : (tokens, top_k)         normalised top-k weights
        router_indices : (tokens, top_k)         selected expert ids
    block.forward: `_, scores, idx = self.gate(h); experts(h, idx, scores)`

So the **architecture-robust ablation lever is a post-hook on the router**: it
masks the chosen experts out of ``router_logits`` and recomputes the top-k —
faithful to the router's own logic, and independent of whether experts are
stored fused (they are) or as a ``ModuleList``. ``top_k`` lives on the *router*
(``…mlp.gate.top_k``), so the k-sweep is a set-attr there.

Sparse blocks are found **structurally** (any submodule with both ``gate`` and
``experts``), so the adapter is robust to wrapper nesting — ``language_model.
layers`` (3.5) vs ``model.layers`` (3.0) vs a ``ForConditionalGeneration``
prefix — without hard-coded paths.

This module builds interventions; it does not run forwards or grade. The thin
``run_ablation_sweep`` driver (readout + null + provenance) composes this with
:mod:`verbum.probes.grading` and :mod:`verbum.results` (staged).

License: MIT.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import torch
from torch import nn

from verbum import hooks

__all__ = ["MoEAdapter", "SparseBlock"]

_LAYER_RE = re.compile(r"\.layers\.(\d+)\.")


@dataclass(frozen=True)
class SparseBlock:
    """One located MoE block: its module path and parsed layer index."""

    layer: int
    path: str  # dotted path to the sparse block (the `…mlp`)


def _is_sparse_block(module: nn.Module) -> bool:
    """Structural test: a sparse MoE block has both a router and experts."""
    return hasattr(module, "gate") and hasattr(module, "experts")


class MoEAdapter:
    """Expert-level interventions on a loaded Qwen3-family MoE model.

    Construct from an already-loaded model (so tests can use a meta-device
    instance) or via :meth:`from_pretrained` (reuses
    :func:`verbum.instrument.load_model`).
    """

    def __init__(self, model: nn.Module) -> None:
        self.model = model
        self.blocks: list[SparseBlock] = self._find_blocks(model)
        if not self.blocks:
            raise ValueError("no sparse MoE blocks found (gate+experts) in model")
        router = model.get_submodule(self.gate_path(self.blocks[0].layer))
        self.num_experts: int = int(router.num_experts)
        self.top_k: int = int(router.top_k)
        first = model.get_submodule(self.blocks[0].path)
        self.has_shared: bool = hasattr(first, "shared_expert")

    # ── construction ─────────────────────────────────────────────────────────

    @classmethod
    def from_pretrained(cls, model_name: str, **load_kwargs: Any) -> MoEAdapter:
        """Load via :func:`verbum.instrument.load_model` and wrap it."""
        from verbum.instrument import load_model

        model, _tok, _info = load_model(model_name, **load_kwargs)
        return cls(model)

    @staticmethod
    def _find_blocks(model: nn.Module) -> list[SparseBlock]:
        found: list[SparseBlock] = []
        for name, module in model.named_modules():
            if _is_sparse_block(module):
                m = _LAYER_RE.search(name + ".")
                layer = int(m.group(1)) if m else len(found)
                found.append(SparseBlock(layer=layer, path=name))
        found.sort(key=lambda b: b.layer)
        return found

    # ── path helpers ─────────────────────────────────────────────────────────

    def _block(self, layer: int) -> SparseBlock:
        for b in self.blocks:
            if b.layer == layer:
                return b
        raise KeyError(f"no MoE block at layer {layer}")

    def block_path(self, layer: int) -> str:
        return self._block(layer).path

    def gate_path(self, layer: int) -> str:
        return f"{self._block(layer).path}.gate"

    def shared_path(self, layer: int) -> str:
        return f"{self._block(layer).path}.shared_expert"

    @property
    def layers(self) -> list[int]:
        return [b.layer for b in self.blocks]

    # ── intervention builders ────────────────────────────────────────────────

    def route_capture(
        self, layers: Sequence[int] | None = None
    ) -> list[hooks.Intervention]:
        """Capture each layer's router output ``(logits, scores, indices)``.

        Read after a forward via ``session.captured[adapter.gate_path(layer)]``.
        ``router_logits`` (index 0) gives per-expert routing mass for ranking
        the top-mass experts; ``router_indices`` (index 2) gives selections.
        """
        layers = self.layers if layers is None else layers
        return [hooks.capture(self.gate_path(layer)) for layer in layers]

    def ablate_experts(self, layer: int, idxs: Sequence[int]) -> hooks.Intervention:
        """Mask experts ``idxs`` out of the router and recompute top-k.

        Faithful to the router: zeroes the experts in the (already-softmaxed)
        ``router_logits``, re-selects the top-k, and renormalises the weights —
        so the block routes as if those experts did not exist.
        """
        idx = torch.as_tensor(list(idxs), dtype=torch.long)

        def _mask(module: nn.Module, _inputs: Any, output: Any) -> Any:
            logits, _scores, _indices = output
            masked = logits.clone()
            masked[:, idx.to(masked.device)] = 0.0
            k = int(module.top_k)
            vals, sel = torch.topk(masked, k, dim=-1)
            vals = vals / vals.sum(dim=-1, keepdim=True).clamp_min(1e-9)
            return masked, vals.to(logits.dtype), sel

        return hooks.apply_post(self.gate_path(layer), _mask, name=f"ablate@{layer}")

    def force_k(self, layer: int, k: int) -> hooks.Intervention:
        """Set the router's active-expert count to ``k`` for the block (k-sweep)."""
        return hooks.set_attr(self.gate_path(layer), "top_k", int(k))

    def ablate_shared(self, layer: int) -> hooks.Intervention:
        """Zero the shared (always-on carrier) expert's contribution."""
        if not self.has_shared:
            raise ValueError("model has no shared_expert")
        return hooks.zero_output(self.shared_path(layer), name=f"shared@{layer}")
