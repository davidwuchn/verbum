"""Generic forward-hook intervention engine — the reusable substrate.

One model-agnostic way to *capture* activations and *intervene* on a forward
pass, so the interpretability zoo (ablation, knockout, patching, survival)
stops re-implementing ``register_forward_hook`` ad hoc (AGENTS.md S5 ``λ
one_way`` / ``λ simplify``; the "too many independent probes" debt).

It owns exactly two primitives plus an attribute patch — the minimum the MoE
expert-ablation probe needs (AGENTS.md ``λ build``: extract the shape, don't
speculatively frame), shaped as open slots so new ops compose:

  - **capture**   record a module's input (pre) or output (post).
  - **apply**     transform the input (pre) or output (post) via a callable;
                  the caller supplies the semantics (e.g. an adapter's MoE
                  router mask), so the engine never learns any architecture.
  - **attr**      temporarily set-and-restore a module attribute (e.g. a
                  router's ``top_k`` for a k-sweep).

Everything is a :class:`Intervention`; :func:`intervene` is a context manager
that installs the hooks/patches, yields a :class:`HookSession` whose
``captured`` dict holds the readouts, and *always* removes every hook and
restores every attribute on exit.

Composes with :mod:`verbum.instrument` (which owns model loading and the
architecture helpers) — it does not load models or know module paths.

License: MIT.
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from typing import Any, Literal

import torch
from torch import nn

__all__ = [
    "HookSession",
    "Intervention",
    "apply_post",
    "apply_pre",
    "capture",
    "intervene",
    "set_attr",
    "zero_output",
]

When = Literal["pre", "post", "attr"]


@dataclass(frozen=True)
class Intervention:
    """One hook or attribute patch on a named submodule.

    Parameters
    ----------
    target
        Dotted submodule path resolvable by ``model.get_submodule`` (e.g.
        ``"language_model.layers.0.mlp.gate"``). For ``when="attr"`` it is the
        module *owning* the attribute.
    when
        ``"post"`` (forward output), ``"pre"`` (forward input), or ``"attr"``
        (set-and-restore a Python attribute around the ``with`` block).
    capture
        If true, store the module's output (post) / input (pre) in
        :attr:`HookSession.captured` under :attr:`name` (default ``target``).
    transform
        Optional callable. For ``post``: ``(module, inputs, output) -> new_output``
        (return ``None`` to leave unchanged). For ``pre``: ``(module, inputs)
        -> new_inputs`` (return ``None`` to leave unchanged). The caller owns
        the semantics; the engine stays architecture-agnostic.
    attr, value
        For ``when="attr"`` only: the attribute name and the value to set
        (the original is restored on exit).
    name
        Key for :attr:`HookSession.captured`. Defaults to ``target``.
    """

    target: str
    when: When = "post"
    capture: bool = False
    transform: Callable[..., Any] | None = None
    attr: str | None = None
    value: Any = None
    name: str | None = None

    @property
    def key(self) -> str:
        return self.name or self.target


class HookSession:
    """Live handle for an :func:`intervene` block; ``captured`` holds readouts."""

    def __init__(self) -> None:
        self.captured: dict[str, Any] = {}


def _detach(obj: Any) -> Any:
    """Recursively detach tensors to CPU; pass tuples/lists/dicts through."""
    if isinstance(obj, torch.Tensor):
        return obj.detach().to("cpu")
    if isinstance(obj, tuple):
        return tuple(_detach(o) for o in obj)
    if isinstance(obj, list):
        return [_detach(o) for o in obj]
    if isinstance(obj, dict):
        return {k: _detach(v) for k, v in obj.items()}
    return obj


@contextlib.contextmanager
def intervene(
    model: nn.Module, interventions: Sequence[Intervention]
) -> Iterator[HookSession]:
    """Install ``interventions`` on ``model`` for the duration of the block.

    Yields a :class:`HookSession`. On exit every forward hook is removed and
    every patched attribute restored — even if the body raises.
    """
    session = HookSession()
    handles: list[Any] = []
    saved_attrs: list[tuple[nn.Module, str, Any]] = []

    def _make_post(iv: Intervention) -> Callable[..., Any]:
        def hook(module: nn.Module, inputs: Any, output: Any) -> Any:
            if iv.capture:
                session.captured[iv.key] = _detach(output)
            if iv.transform is not None:
                return iv.transform(module, inputs, output)
            return None

        return hook

    def _make_pre(iv: Intervention) -> Callable[..., Any]:
        def hook(module: nn.Module, inputs: Any) -> Any:
            if iv.capture:
                session.captured[iv.key] = _detach(inputs)
            if iv.transform is not None:
                return iv.transform(module, inputs)
            return None

        return hook

    try:
        for iv in interventions:
            mod = model.get_submodule(iv.target)
            if iv.when == "attr":
                if iv.attr is None:
                    raise ValueError(f"attr intervention on {iv.target!r} needs `attr`")
                saved_attrs.append((mod, iv.attr, getattr(mod, iv.attr)))
                setattr(mod, iv.attr, iv.value)
            elif iv.when == "post":
                handles.append(mod.register_forward_hook(_make_post(iv)))
            elif iv.when == "pre":
                handles.append(mod.register_forward_pre_hook(_make_pre(iv)))
            else:  # pragma: no cover - exhaustive
                raise ValueError(f"unknown `when`: {iv.when!r}")
        yield session
    finally:
        for h in handles:
            h.remove()
        for mod, attr, old in reversed(saved_attrs):
            setattr(mod, attr, old)


# ── convenience constructors (built on the two primitives) ───────────────────


def capture(
    target: str, *, when: When = "post", name: str | None = None
) -> Intervention:
    """Capture a module's output (``post``) or input (``pre``)."""
    return Intervention(target=target, when=when, capture=True, name=name)


def apply_post(
    target: str, fn: Callable[[nn.Module, Any, Any], Any], *, name: str | None = None
) -> Intervention:
    """Transform a module's *output*: ``fn(module, inputs, output) -> new_output``."""
    return Intervention(target=target, when="post", transform=fn, name=name)


def apply_pre(
    target: str, fn: Callable[[nn.Module, Any], Any], *, name: str | None = None
) -> Intervention:
    """Transform a module's *input*: ``fn(module, inputs) -> new_inputs``."""
    return Intervention(target=target, when="pre", transform=fn, name=name)


def set_attr(target: str, attr: str, value: Any) -> Intervention:
    """Temporarily set ``target.attr = value``, restoring the original on exit."""
    return Intervention(target=target, when="attr", attr=attr, value=value)


def _zero_like(obj: Any) -> Any:
    if isinstance(obj, torch.Tensor):
        return torch.zeros_like(obj)
    if isinstance(obj, tuple):
        return tuple(_zero_like(o) for o in obj)
    if isinstance(obj, list):
        return [_zero_like(o) for o in obj]
    return obj


def zero_output(target: str, *, name: str | None = None) -> Intervention:
    """Replace a module's output with zeros (tensor or tuple-of-tensors)."""
    return apply_post(target, lambda _m, _i, out: _zero_like(out), name=name)
