#!/usr/bin/env python3
"""RelationalCrystalClassifier — the validated, null-gated opcode reader.

Canonical home (promoted from ``scripts/instruments/relational_opcode.py``,
which now re-exports from here). Reads combinator OPCODES from a routing
register (sign-of-gate features) via:

  1. SIGN     — routing register = sign(gate features) (the topological read)
  2. CMR      — common-mode removal (the shared lambda-mode gauge)
  3. RELATION — per-combinator centroids; the frame-invariant 9x9 Gram is
     compared to the bundled 10-model consensus crystal
  4. NULL     — every per-op energy is a z-score vs a null; a token emits an
     opcode ONLY if z>thresh, else NO-OP (kills "argmax always picks winner")

DESIGN: model-AGNOSTIC. ``calibrate()`` and ``classify()`` take per-layer gate
FEATURE matrices (the caller runs the model + captures the register — see
``capture.py``); the numpy science is unit-testable on synthetic data with
planted structure, no model load.

Bridge to the tree (``vsm.py``): ``layer_nodes()`` converts a calibration into
leaf VSM nodes; ``register_node()`` stacks them into a register-level node —
the unit that model/family/root trees are built from.

Consensus data: bundled at ``data/consensus_gram.json`` (10-model routing
consensus, order K I B C S D W Y WHNF). License: MIT.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))  # peer modules (vsm) when run as a script

from vsm import (  # noqa: E402
    CRYSTAL,
    VSMNode,
    gram_from_centroids,
    layer_node,
    offdiag_corr,
    stack,
)

__all__ = [
    "CRYSTAL",
    "LayerCalib",
    "RelationalCrystalClassifier",
    "TokenOpcodes",
    "layer_nodes",
    "load_consensus_gram",
    "register_node",
]

CONSENSUS_PATH = _HERE / "data" / "consensus_gram.json"


# ── numpy crystal instruments ────────────────────────────────────────────────


def _unit_rows(X: np.ndarray) -> np.ndarray:
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)


def _centroids(X: np.ndarray, labels: np.ndarray) -> np.ndarray:
    C = np.zeros((len(CRYSTAL), X.shape[1]), np.float64)
    for j, c in enumerate(CRYSTAL):
        m = labels == c
        if m.any():
            C[j] = X[m].mean(axis=0)
    return C


def _silhouette(X: np.ndarray, labels: np.ndarray) -> float:
    U = _unit_rows(_centroids(X, labels))
    Xu = _unit_rows(X)
    sims = Xu @ U.T
    li = np.array([CRYSTAL.index(c) for c in labels])
    rows = np.arange(len(labels))
    own = sims[rows, li]
    other = sims.copy()
    other[rows, li] = -np.inf
    return float(np.mean(own - other.max(axis=1)))


def _silhouette_z(
    X: np.ndarray, labels: np.ndarray, n_perm: int, rng: np.random.Generator
) -> float:
    obs = _silhouette(X, labels)
    null = np.array(
        [_silhouette(X, rng.permutation(labels)) for _ in range(n_perm)]
    )
    return float((obs - null.mean()) / (null.std() + 1e-30))


def load_consensus_gram(path: str | Path | None = None) -> np.ndarray | None:
    """Load the bundled 10-model consensus Gram (or an override file)."""
    p = Path(path) if path is not None else CONSENSUS_PATH
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    if list(d.get("crystal_order", [])) != CRYSTAL:
        return None
    return np.array(d["consensus_gram"], dtype=np.float64)


# ── calibration / classification dataclasses ─────────────────────────────────


@dataclass
class LayerCalib:
    """Per-layer calibration: the common-mode, centroids, and the null."""

    common_mode: np.ndarray            # [d] mean sign(gate) over calib probes
    centroids: np.ndarray              # [9, d] unit per-combinator centroids
    null_mean: np.ndarray              # [9] null projection mean per op
    null_std: np.ndarray               # [9] null projection std per op
    silhouette_z: float                # crystal significance at this layer
    gc_consensus: float                # Gram alignment to consensus (or nan)
    crystal_bearing: bool              # sil_z>thresh (and gc>0 if consensus)
    null_kind: str = "offtarget"       # "offtarget"(crystal) | "crosstask"


@dataclass
class TokenOpcodes:
    """One token's per-layer opcode read."""

    per_layer: dict = field(default_factory=dict)   # li -> {op: z}
    emitted: dict = field(default_factory=dict)     # li -> [significant ops]
    dominant: str = "·"                             # max-z op (crystal) or no-op


class RelationalCrystalClassifier:
    """Validated FFN-routing opcode reader: gate register, sign-CMR,
    consensus-relational, null-calibrated. Model-agnostic (feature matrices in).
    """

    def __init__(
        self,
        layers: list[int],
        *,
        n_perm: int = 300,
        z_thresh: float = 3.0,
        sil_z_thresh: float = 2.0,
        seed: int = 0,
        consensus_gram: np.ndarray | str | None = "auto",
    ):
        self.layers = list(layers)
        self.n_perm = n_perm
        self.z_thresh = z_thresh
        self.sil_z_thresh = sil_z_thresh
        self.seed = seed
        # "auto" -> bundled consensus; None -> disable (synthetic/no-target);
        # ndarray -> use as given.
        self.consensus_gram = (
            load_consensus_gram()
            if isinstance(consensus_gram, str)
            else consensus_gram
        )
        self.calib: dict[int, LayerCalib] = {}

    # -- S5 calibration: build the per-layer crystal from probe activations - #
    def calibrate(
        self,
        gate_by_layer: dict[int, np.ndarray],
        labels: np.ndarray,
        null_gate_by_layer: dict[int, np.ndarray] | None = None,
    ) -> dict[int, LayerCalib]:
        """``gate_by_layer[li] = [N, d]`` last-token gate features for the N
        crystal probes; ``labels [N]`` in CRYSTAL. Build per-layer common-mode,
        CMR centroids, the null, silhouette-z, and consensus Gram alignment.

        NULL (s231 v2 — the over-read-killer that no longer under-reads):
          - ``null_gate_by_layer=None`` (default): off-target null — per op j
            the null is the projection of NON-j crystal probes onto j's
            centroid. Every crystal probe is lambda-mode, so this has LOW
            POWER for the compose arc (the s231 under-read).
          - ``null_gate_by_layer[li] = [M, d]`` NON-combinator baseline gate
            features (natural-text / retrieval tokens): CROSS-TASK null — z
            asks "does this token look more like op j than a typical
            natural-text token does?" — recovers the lambda compose-arc while
            keeping retrieval silent.
        """
        labels = np.asarray(labels)
        rng = np.random.default_rng(self.seed)
        null_kind = "crosstask" if null_gate_by_layer is not None else "offtarget"
        for li in self.layers:
            G = np.asarray(gate_by_layer[li], dtype=np.float64)
            S = np.sign(G)
            common = S.mean(axis=0)                  # the common-mode (gauge)
            X = S - common                           # sign-CMR routing features
            cents = _centroids(X, labels)
            ucents = _unit_rows(cents)
            Xu = _unit_rows(X)
            sims = Xu @ ucents.T                     # [N, 9] cos to centroids
            li_idx = np.array([CRYSTAL.index(c) for c in labels])
            nmean = np.zeros(len(CRYSTAL))
            nstd = np.ones(len(CRYSTAL))
            if null_gate_by_layer is not None:
                # CROSS-TASK null: baseline tokens through the SAME sign-CMR
                # transform onto each centroid.
                B = np.asarray(null_gate_by_layer[li], dtype=np.float64)
                Vb = np.sign(B) - common
                Vbu = _unit_rows(Vb)
                bsims = Vbu @ ucents.T               # [M, 9]
                for j in range(len(CRYSTAL)):
                    col = bsims[:, j]
                    nmean[j] = col.mean()
                    nstd[j] = col.std() + 1e-9
            else:
                # off-target null: NON-op probes projected onto op centroid
                for j in range(len(CRYSTAL)):
                    off = sims[li_idx != j, j]
                    if off.size:
                        nmean[j] = off.mean()
                        nstd[j] = off.std() + 1e-9
            sil_z = _silhouette_z(X, labels, self.n_perm, rng)
            gc = (
                offdiag_corr(gram_from_centroids(cents), self.consensus_gram)
                if self.consensus_gram is not None
                else float("nan")
            )
            bearing = sil_z > self.sil_z_thresh and (np.isnan(gc) or gc > 0.0)
            self.calib[li] = LayerCalib(
                common_mode=common,
                centroids=ucents,
                null_mean=nmean,
                null_std=nstd,
                silhouette_z=round(sil_z, 3),
                gc_consensus=(
                    round(gc, 3) if not np.isnan(gc) else float("nan")
                ),
                crystal_bearing=bool(bearing),
                null_kind=null_kind,
            )
        return self.calib

    @property
    def crystal_layers(self) -> list[int]:
        return [li for li, c in self.calib.items() if c.crystal_bearing]

    # -- S1 classify: token gate -> null-calibrated per-op z ----------------- #
    def classify(self, gate_by_layer_token: dict[int, np.ndarray]) -> TokenOpcodes:
        """``gate_by_layer_token[li] = [d]`` one token's gate at layer li.
        Returns per-layer op z-scores, the significant (z>thresh) opcodes, and
        the dominant op across crystal-bearing layers ('·' no-op if none).
        """
        out = TokenOpcodes()
        best_op, best_z = "·", self.z_thresh
        for li in self.layers:
            cal = self.calib.get(li)
            if cal is None:
                continue
            g = np.asarray(gate_by_layer_token[li], dtype=np.float64)
            v = np.sign(g) - cal.common_mode
            nv = np.linalg.norm(v)
            if nv < 1e-12:
                continue
            sims = cal.centroids @ (v / nv)          # [9] cos to each centroid
            z = (sims - cal.null_mean) / cal.null_std
            zmap = {
                op: round(float(zz), 3)
                for op, zz in zip(CRYSTAL, z, strict=True)
            }
            out.per_layer[li] = zmap
            sig = [op for op, zz in zmap.items() if zz > self.z_thresh]
            if sig:
                out.emitted[li] = sig
            if cal.crystal_bearing:                  # dominant: crystal only
                j = int(np.argmax(z))
                if z[j] > best_z:
                    best_op, best_z = CRYSTAL[j], float(z[j])
        out.dominant = best_op
        return out

    def calibration_summary(self) -> dict:
        null_kinds = {c.null_kind for c in self.calib.values()}
        return {
            "n_layers": len(self.calib),
            "crystal_layers": self.crystal_layers,
            "per_layer": {
                li: {
                    "sil_z": c.silhouette_z,
                    "gc_consensus": c.gc_consensus,
                    "crystal_bearing": c.crystal_bearing,
                }
                for li, c in self.calib.items()
            },
            "z_thresh": self.z_thresh,
            "sil_z_thresh": self.sil_z_thresh,
            "has_consensus": self.consensus_gram is not None,
            "null_kind": (
                next(iter(null_kinds))
                if len(null_kinds) == 1
                else sorted(null_kinds)
            ),
        }


# ── bridge: calibration -> VSM tree nodes ────────────────────────────────────


def layer_nodes(
    clf: RelationalCrystalClassifier,
    *,
    keep_centroids: bool = False,
    null_floor_z: float = float("nan"),
) -> list[VSMNode]:
    """One leaf VSM node per calibrated layer (gate rule = crystal_bearing)."""
    nodes = []
    for li in sorted(clf.calib):
        c = clf.calib[li]
        nodes.append(
            layer_node(
                f"L{li}",
                c.centroids,
                sil_z=c.silhouette_z,
                gc_consensus=c.gc_consensus,
                null_floor_z=null_floor_z,
                sil_z_thresh=clf.sil_z_thresh,
                keep_centroids=keep_centroids,
                meta={"layer": li, "null_kind": c.null_kind},
            )
        )
    return nodes


def register_node(
    clf: RelationalCrystalClassifier,
    name: str,
    *,
    keep_centroids: bool = False,
    null_floor_z: float = float("nan"),
    meta: dict | None = None,
) -> VSMNode:
    """Stack a calibration into a register-level VSM node (e.g. 'gate', 'attn').

    ``null_floor_z`` records a register-level elevated-null caveat (s264: the
    attn-write register's shuffled-label null floor is elevated vs gate's) —
    it propagates up the tree as the worst child, never disappearing.
    """
    return stack(
        layer_nodes(
            clf, keep_centroids=keep_centroids, null_floor_z=null_floor_z
        ),
        level="register",
        name=name,
        reference_gram=clf.consensus_gram,
        meta={"n_perm": clf.n_perm, "z_thresh": clf.z_thresh, **(meta or {})},
    )


# ── synthetic smoke — planted per-combinator structure, no model ─────────────


def _smoke() -> None:
    rng = np.random.default_rng(0)
    d, per = 64, 40
    layers = [0, 1, 2]
    # layer 1 = crystal-bearing (planted combinator directions); 0,2 = noise
    dirs = rng.standard_normal((len(CRYSTAL), d))
    labels = np.array([c for c in CRYSTAL for _ in range(per)])
    common = rng.standard_normal(d) * 3.0            # a strong common-mode
    gate_cal = {}
    for li in layers:
        rows = []
        for c in CRYSTAL:
            base = dirs[CRYSTAL.index(c)] if li == 1 else np.zeros(d)
            sig = 2.5 if li == 1 else 0.0
            rows.append(common + sig * base + rng.standard_normal((per, d)))
        gate_cal[li] = np.concatenate(rows, axis=0)
    clf = RelationalCrystalClassifier(
        layers, n_perm=120, z_thresh=3.0, seed=0, consensus_gram=None
    )
    clf.calibrate(gate_cal, labels)
    summ = clf.calibration_summary()
    print("calibration:", json.dumps(summ, indent=2))
    assert 1 in clf.crystal_layers, "planted crystal layer 1 not detected"
    assert 0 not in clf.crystal_layers and 2 not in clf.crystal_layers, (
        "noise layers wrongly flagged crystal-bearing"
    )
    # a 'B' token: common-mode + B direction at layer 1
    tok = {
        li: (
            common
            + (3.0 * dirs[CRYSTAL.index("B")] if li == 1 else 0.0)
            + rng.standard_normal(d) * 0.5
        )
        for li in layers
    }
    res = clf.classify(tok)
    print("B-token dominant:", res.dominant, "| emitted:", res.emitted)
    assert res.dominant == "B", f"expected B, got {res.dominant}"
    # a pure common-mode token (no combinator) -> NO-OP
    noop = {li: common + rng.standard_normal(d) * 0.5 for li in layers}
    rn = clf.classify(noop)
    print("common-mode-only token dominant:", rn.dominant)
    assert rn.dominant == "·", f"common-mode token should be no-op, got {rn.dominant}"
    print("✅ smoke (offtarget null) passed")

    # cross-task null (s231 v2)
    base = {
        li: np.stack(
            [common + rng.standard_normal(d) * 0.5 for _ in range(per)]
        )
        for li in layers
    }
    clf2 = RelationalCrystalClassifier(
        layers, n_perm=120, z_thresh=3.0, seed=0, consensus_gram=None
    )
    clf2.calibrate(gate_cal, labels, null_gate_by_layer=base)
    assert clf2.calibration_summary()["null_kind"] == "crosstask"
    assert 1 in clf2.crystal_layers
    assert clf2.classify(tok).dominant == "B"
    assert clf2.classify(noop).dominant == "·"
    print("✅ smoke (crosstask null) passed")

    # bridge: calibration -> register VSM node
    reg = register_node(clf2, "gate", null_floor_z=0.0)
    assert reg.level == "register" and len(reg.children) == 3
    assert reg.meta["n_gated"] == 1 and reg.gated
    assert reg.child("L1").gated and not reg.child("L0").gated
    print("✅ register_node bridge passed:")
    print(reg.summary())

    # bundled consensus loads and is well-formed (order + shape)
    cg = load_consensus_gram()
    assert cg is not None and cg.shape == (9, 9), "bundled consensus missing"
    assert np.allclose(np.diag(cg), 1.0, atol=1e-6)
    print("✅ bundled consensus gram loaded:", cg.shape)


if __name__ == "__main__":
    _smoke()
