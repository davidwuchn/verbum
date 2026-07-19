#!/usr/bin/env python3
"""OpcodeVSM — the recursive, stackable tensor node of the opcode crystal tree.

Tree-of-VSM (Beer 1972, per verbum v14/v15 ``stack_vsm.py``) applied to
MEASUREMENT rather than training: every node in the tree is a viable system
with the same shape, so nodes stack — layers into registers, registers into
models, models into families, families into the universal crystal.

The stackable tensor is the **9x9 relational Gram** over the crystal
combinators (K I B C S D W Y WHNF): the cosine structure between per-combinator
routing centroids after sign + common-mode removal. It is *frame-invariant* —
it lives in combinator-label space, not weight space — so it has the same
shape for every layer, register, model, architecture, and scale. That is what
makes a cross-model tree possible at all.

Node anatomy (fractal — identical at every level)::

    S5  identity      node.gram          the node's crystal (9x9 consensus)
    S4  intelligence  node.meta          cross-child agreement / dissent stats
    S3  control       node.gated         null-gate: only passing nodes propagate UP
    S2  coordination  node.children      sibling registers/models kept comparable
    S1  operations    leaf arrays        per-layer centroids (model-dim-bound)
    algedonic UP      node.health        {sil_z, gc_consensus,
                                          crystal_bearing_frac, null_floor_z}

Standard level ladder (levels are free strings; this is the convention)::

    layer -> register -> model -> family -> root

Discipline (inherited from the verbum project):
  - Null-gate every claim: a node's Gram propagates upward only if it passed
    its significance gate (``gated``). Ungated nodes remain in the tree —
    visible, honest — but contribute nothing to the parent consensus.
  - Elevated null floors (``null_floor_z``) propagate as the WORST child:
    a caveat never disappears by aggregation.
  - Model-dimension-bound arrays (centroids ``[9, d]``) stay at the leaves;
    only the frame-invariant Gram + health vector climb the tree.

Pure numpy — no torch, no model, unit-testable on synthetic data.
License: MIT.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

__all__ = [
    "CRYSTAL",
    "STATECHART",
    "TYPES16",
    "VSMNode",
    "gram_from_centroids",
    "layer_node",
    "load_tree",
    "offdiag_corr",
    "save_tree",
    "self_test",
    "stack",
]

# ── bases ────────────────────────────────────────────────────────────────────
# The tree is parametric over its combinator BASIS. Three registers, three bases
# (crystal-phi-derivation.md, crystal-multi-tree.md, consensus.json):
#
#   CRYSTAL   (9)  — the MEASUREMENT basis: 4 fire states + 3 named paths/
#                    bridges (D=B→B path; W,Y bridges) + WHNF (halt). This is
#                    the promptable shadow of the statechart — the 10-model
#                    routing-register consensus order. Default.
#   STATECHART(8)  — the DYNAMICS basis: the absorbing Markov chain,
#                    4 transient fire states + 4 absorbing WHNF states.
#                    8 = |{K,I,B,C}| x {fire, whnf} is forced.
#   TYPES16  (16)  — the EXTRACTION basis: 8 combinator types + 8 anti-types
#                    (weight-space register; M₁₆ = S⊗J + D⊗F). Anti-types are
#                    not promptable — this basis is fed from extraction data,
#                    not probes.
#
# A Gram is only stackable against Grams in the SAME basis; ``stack`` enforces
# this. Cross-basis comparison is an analysis step, not a tree operation.

CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
STATECHART = [
    "fire:K", "fire:I", "fire:B", "fire:C",
    "whnf:K", "whnf:I", "whnf:B", "whnf:C",
]
TYPES16 = [
    "K", "I", "B", "C", "S", "D", "W", "Y",
    "~K", "~I", "~B", "~C", "~S", "~D", "~W", "~Y",
]

HEALTH_KEYS = ("sil_z", "gc_consensus", "crystal_bearing_frac", "null_floor_z")


# ── gram utilities (canonical home; classify.py imports these) ───────────────


def _unit_rows(X: np.ndarray) -> np.ndarray:
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)


def gram_from_centroids(
    centroids: np.ndarray, basis: list[str] = CRYSTAL
) -> np.ndarray:
    """``[n, d]`` per-combinator centroids -> ``[n, n]`` relational Gram."""
    if centroids.shape[0] != len(basis):
        raise ValueError(
            f"expected {len(basis)} centroid rows (basis order {basis}), "
            f"got {centroids.shape[0]}"
        )
    U = _unit_rows(np.asarray(centroids, dtype=np.float64))
    return np.clip(U @ U.T, -1.0, 1.0)


def offdiag_corr(a: np.ndarray, b: np.ndarray) -> float:
    """Pearson correlation of the off-diagonal entries of two same-size Grams."""
    a, b = np.asarray(a), np.asarray(b)
    if a.shape != b.shape:
        raise ValueError(f"gram shape mismatch: {a.shape} vs {b.shape}")
    off = ~np.eye(a.shape[0], dtype=bool)
    x, y = np.asarray(a)[off], np.asarray(b)[off]
    if x.std() < 1e-9 or y.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


# ── the node ─────────────────────────────────────────────────────────────────


@dataclass
class VSMNode:
    """One node of the opcode crystal tree — same shape at every level."""

    level: str                                  # "layer"|"register"|"model"|...
    name: str
    gram: np.ndarray | None = None              # [n, n] Gram in basis order
    basis: list[str] = field(default_factory=lambda: list(CRYSTAL))
    health: dict[str, float] = field(default_factory=dict)
    gated: bool = False                         # S3: passes its null gate
    meta: dict[str, Any] = field(default_factory=dict)
    children: list[VSMNode] = field(default_factory=list)
    arrays: dict[str, np.ndarray] = field(default_factory=dict)  # leaf-only, npz

    # -- convenience -------------------------------------------------------- #

    def child(self, name: str) -> VSMNode | None:
        for c in self.children:
            if c.name == name:
                return c
        return None

    def walk(self, _path: tuple[str, ...] = ()) -> Any:
        """Yield ``(path_tuple, node)`` depth-first."""
        p = (*_path, self.name)
        yield p, self
        for c in self.children:
            yield from c.walk(p)

    def summary(self, indent: int = 0) -> str:
        """Human-readable tree rendering (gate state + health per node)."""
        h = self.health
        mark = "+" if self.gated else "-"
        parts = [f"{'  ' * indent}[{mark}] {self.level}:{self.name}"]
        if h:
            parts.append(
                "  sil_z={:.2f} gc={:.3f} bearing={:.2f} null_floor={:.2f}".format(
                    h.get("sil_z", float("nan")),
                    h.get("gc_consensus", float("nan")),
                    h.get("crystal_bearing_frac", float("nan")),
                    h.get("null_floor_z", float("nan")),
                )
            )
        lines = ["".join(parts)]
        lines.extend(c.summary(indent + 1) for c in self.children)
        return "\n".join(lines)


# ── leaf construction (from a classifier LayerCalib) ─────────────────────────


def layer_node(
    name: str,
    centroids: np.ndarray,
    *,
    sil_z: float,
    gc_consensus: float = float("nan"),
    null_floor_z: float = float("nan"),
    sil_z_thresh: float = 2.0,
    keep_centroids: bool = True,
    basis: list[str] = CRYSTAL,
    meta: dict[str, Any] | None = None,
) -> VSMNode:
    """Build a leaf (layer-level) node from per-combinator centroids.

    The S3 gate at a leaf is the crystal-bearing rule used everywhere in this
    project: ``sil_z > thresh`` and, when a consensus alignment is available,
    ``gc_consensus > 0``.
    """
    gram = gram_from_centroids(centroids, basis)
    gated = bool(
        sil_z > sil_z_thresh
        and (np.isnan(gc_consensus) or gc_consensus > 0.0)
    )
    node = VSMNode(
        level="layer",
        name=name,
        gram=gram,
        basis=list(basis),
        health={
            "sil_z": float(sil_z),
            "gc_consensus": float(gc_consensus),
            "crystal_bearing_frac": 1.0 if gated else 0.0,
            "null_floor_z": float(null_floor_z),
        },
        gated=gated,
        meta=dict(meta or {}),
    )
    if keep_centroids:
        node.arrays["centroids"] = np.asarray(centroids, dtype=np.float32)
    return node


# ── stacking (children -> parent consensus) ──────────────────────────────────


def stack(
    children: list[VSMNode],
    *,
    level: str,
    name: str,
    reference_gram: np.ndarray | None = None,
    meta: dict[str, Any] | None = None,
) -> VSMNode:
    """Stack child VSM nodes into a parent node (mechanical, no model).

    - parent Gram   = mean of the GATED children's Grams (S3: ungated children
      stay in the tree but contribute nothing upward);
    - agreement     = pairwise off-diagonal correlation among gated children
      (S4: mean/min + a dissent flag when any pair anti-correlates);
    - health rollup = median sil_z (gated), gc vs ``reference_gram`` (if
      given), fraction gated, and the WORST child null floor.

    All children must share one basis (a Gram is only comparable within its
    basis); the parent inherits it.
    """
    if not children:
        raise ValueError("stack() needs at least one child")
    basis = children[0].basis
    for c in children[1:]:
        if c.basis != basis:
            raise ValueError(
                f"basis mismatch under {level}:{name} — "
                f"{children[0].name}:{basis} vs {c.name}:{c.basis}"
            )
    passing = [c for c in children if c.gated and c.gram is not None]
    gram = (
        np.mean(np.stack([c.gram for c in passing]), axis=0) if passing else None
    )

    pairs = [
        offdiag_corr(a.gram, b.gram) for a, b in combinations(passing, 2)
    ]
    agreement = {
        "n_children": len(children),
        "n_gated": len(passing),
        "gated_children": [c.name for c in passing],
        "agreement_mean": float(np.mean(pairs)) if pairs else float("nan"),
        "agreement_min": float(np.min(pairs)) if pairs else float("nan"),
        "dissent": bool(pairs and min(pairs) < 0.0),
    }

    sil = [c.health.get("sil_z", np.nan) for c in passing]
    floors = [c.health.get("null_floor_z", np.nan) for c in children]
    gc = (
        offdiag_corr(gram, reference_gram)
        if gram is not None and reference_gram is not None
        else float("nan")
    )
    health = {
        "sil_z": float(np.nanmedian(sil)) if sil else float("nan"),
        "gc_consensus": float(gc),
        "crystal_bearing_frac": (
            len(passing) / len(children) if children else 0.0
        ),
        "null_floor_z": (
            float(np.nanmax(floors))
            if floors and not np.all(np.isnan(floors))
            else float("nan")
        ),
    }
    gated = bool(
        passing
        and (np.isnan(health["gc_consensus"]) or health["gc_consensus"] > 0.0)
    )
    return VSMNode(
        level=level,
        name=name,
        gram=gram,
        basis=list(basis),
        health=health,
        gated=gated,
        meta={**agreement, **(meta or {})},
        children=list(children),
    )


# ── serialization (tree -> JSON + one sidecar npz for leaf arrays) ───────────


def _node_dict(node: VSMNode, path: str, store: dict[str, np.ndarray]) -> dict:
    for k, v in node.arrays.items():
        store[f"{path}/{k}"] = v
    return {
        "level": node.level,
        "name": node.name,
        "gram": None if node.gram is None else np.asarray(node.gram).tolist(),
        "health": node.health,
        "gated": node.gated,
        "meta": node.meta,
        "array_keys": sorted(node.arrays),
        "children": [
            _node_dict(c, f"{path}/{c.name}", store) for c in node.children
        ],
    }


def save_tree(node: VSMNode, path: str | Path) -> Path:
    """Write ``<path>.json`` (tree + inline Grams) and ``<path>.npz`` (arrays).

    Grams are 81 floats — they live inline in the JSON. Model-dimension-bound
    arrays (leaf centroids) go to the sidecar npz keyed by node path.
    """
    path = Path(path)
    store: dict[str, np.ndarray] = {}
    d = {
        "format": "opcode-vsm-tree",
        "version": 1,
        "basis": node.basis,
        "root": _node_dict(node, node.name, store),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    jp = path.with_suffix(".json")
    jp.write_text(json.dumps(d, indent=2, allow_nan=True), encoding="utf-8")
    if store:
        np.savez_compressed(path.with_suffix(".npz"), **store)
    return jp


def _node_from(
    d: dict, path: str, store: dict[str, np.ndarray], basis: list[str]
) -> VSMNode:
    node = VSMNode(
        level=d["level"],
        name=d["name"],
        gram=None if d["gram"] is None else np.asarray(d["gram"], np.float64),
        basis=list(basis),
        health=dict(d["health"]),
        gated=bool(d["gated"]),
        meta=dict(d["meta"]),
        children=[
            _node_from(c, f"{path}/{c['name']}", store, basis)
            for c in d["children"]
        ],
        arrays={
            k: store[f"{path}/{k}"]
            for k in d.get("array_keys", [])
            if f"{path}/{k}" in store
        },
    )
    return node


def load_tree(path: str | Path) -> VSMNode:
    path = Path(path)
    d = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    if d.get("format") != "opcode-vsm-tree":
        raise ValueError(f"{path}: not an opcode-vsm-tree file")
    basis = list(d.get("basis", CRYSTAL))
    npz = path.with_suffix(".npz")
    store: dict[str, np.ndarray] = {}
    if npz.exists():
        with np.load(npz) as z:
            store = {k: z[k] for k in z.files}
    return _node_from(d["root"], d["root"]["name"], store, basis)


# ── self-test (synthetic — planted consensus, noise, and a dissenter) ────────


def self_test(tmp_dir: str | Path | None = None) -> dict[str, Any]:
    """Verify gating, stacking, agreement, dissent, and round-trip — no model."""
    rng = np.random.default_rng(0)
    d = 64

    def _noisy_centroids(base: np.ndarray, noise: float) -> np.ndarray:
        return base + noise * rng.standard_normal(base.shape)

    planted = rng.standard_normal((len(CRYSTAL), d))       # the "true" crystal
    target = gram_from_centroids(planted)
    dissenter = rng.standard_normal((len(CRYSTAL), d))     # unrelated structure

    def _model(name: str, *, crystal: bool, n_layers: int = 6) -> VSMNode:
        base = planted if crystal else dissenter
        layers = []
        for li in range(n_layers):
            bearing = li in (2, 3, 4)                      # planted crystal zone
            cents = _noisy_centroids(base, 0.35 if bearing else 8.0)
            layers.append(
                layer_node(
                    f"L{li}",
                    cents,
                    sil_z=6.0 if bearing else 0.3,          # gate on sil_z
                    null_floor_z=1.2 if name == "m-attn" else 0.0,
                )
            )
        reg = stack(layers, level="register", name="gate")
        return stack([reg], level="model", name=name, reference_gram=target)

    m1 = _model("m1", crystal=True)
    m2 = _model("m2", crystal=True)
    m_attn = _model("m-attn", crystal=True)
    m_diss = _model("m-dissent", crystal=False)

    fam = stack(
        [m1, m2, m_attn], level="family", name="fam", reference_gram=target
    )
    root = stack(
        [fam, m_diss], level="root", name="universal", reference_gram=target
    )

    reg1 = m1.children[0]
    gc_child = offdiag_corr(m1.children[0].children[2].gram, target)
    gc_fam = offdiag_corr(fam.gram, target)

    # dissenting model: its layers pass their own sil_z gate but its structure
    # disagrees with the reference -> visible as low/negative gc at model level
    gc_diss = offdiag_corr(m_diss.gram, target)

    checks = {
        # S3 gating: noise layers excluded from the register consensus
        "leaf_gate_excludes_noise": reg1.meta["n_gated"] == 3
        and reg1.health["crystal_bearing_frac"] == 0.5,
        # stacking denoises: family Gram closer to target than a single layer
        "stack_denoises": gc_fam > gc_child,
        "family_gc_high": gc_fam > 0.9,
        # agreement among crystal models high, dissent flag off at family
        "family_agreement": fam.meta["agreement_mean"] > 0.8
        and not fam.meta["dissent"],
        # the dissenter is un-aligned with the reference; if it is not
        # anti-aligned (gc>0) the S3 gate rightly keeps it — but S4 must
        # expose it: root agreement_min collapses vs the clean family's
        "dissenter_visible": gc_diss < 0.3
        and m_diss.health["gc_consensus"] < 0.3,
        "dissenter_exposed_by_s4": (not m_diss.gated)
        or root.meta["dissent"]
        or root.meta["agreement_min"] < 0.3 < fam.meta["agreement_min"],
        # worst-child null floor propagates to the root (caveats never vanish)
        "null_floor_propagates": root.health["null_floor_z"] >= 1.2,
    }

    # basis discipline: grams only stack within one basis
    sc_leaf = layer_node(
        "sc",
        rng.standard_normal((len(STATECHART), d)),
        sil_z=6.0,
        basis=STATECHART,
    )
    try:
        stack([m1, sc_leaf], level="model", name="bad")
        checks["basis_mismatch_raises"] = False
    except ValueError:
        checks["basis_mismatch_raises"] = True
    checks["basis_shapes"] = (
        sc_leaf.gram.shape == (8, 8) and root.gram.shape == (9, 9)
    )

    # round-trip
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        base_dir = Path(tmp_dir) if tmp_dir else Path(td)
        p = base_dir / "tree_selftest"
        save_tree(root, p)
        back = load_tree(p)
        paths = [pp for pp, _ in root.walk()]
        bpaths = [pp for pp, _ in back.walk()]
        leaf = m1.children[0].children[2]
        bleaf = back.child("fam").child("m1").child("gate").child("L2")
        checks["roundtrip_structure"] = paths == bpaths
        checks["roundtrip_gram"] = bool(
            np.allclose(back.gram, root.gram, atol=1e-12)
        )
        checks["roundtrip_arrays"] = bool(
            np.allclose(bleaf.arrays["centroids"], leaf.arrays["centroids"])
        )

    return {
        "gc_single_layer": round(gc_child, 4),
        "gc_family": round(gc_fam, 4),
        "gc_dissenter": round(gc_diss, 4),
        "family_agreement_mean": round(fam.meta["agreement_mean"], 4),
        "root_bearing_frac": root.health["crystal_bearing_frac"],
        "root_null_floor": root.health["null_floor_z"],
        "checks": checks,
        "all_pass": all(checks.values()),
    }


if __name__ == "__main__":
    out = self_test()
    print(json.dumps(out, indent=2))
    if not out["all_pass"]:
        raise SystemExit(1)
