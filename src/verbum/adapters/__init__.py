"""Architecture adapters over the generic :mod:`verbum.hooks` engine.

Each adapter knows one model family's module structure and re-expresses
interventions as :class:`verbum.hooks.Intervention` specs. The engine stays
architecture-agnostic; the adapter is the only thing that learns paths
(AGENTS.md ``λ one_way`` / ``λ compose``). A dense-FFN adapter would live here
beside :mod:`verbum.adapters.moe` — the bbf92f2 "dense instrument ⊥ MoE"
incompatibility dissolves into "two adapters on one engine".

License: MIT.
"""

from __future__ import annotations

from verbum.adapters.moe import MoEAdapter

__all__ = ["MoEAdapter"]
