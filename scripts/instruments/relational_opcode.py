#!/usr/bin/env python3
# register: topological/routing
"""Relational crystal opcode classifier — the VALIDATED upgrade (s231, audit-aware).

THE OVER-READ THIS FIXES (audit-meta-pattern.md, s202→s206):
  "combinator opcodes: prose fires opcodes AFTER common-mode removal (p=0.001) — REAL;
   raw argmax 'tracer' = common mode = false signal."
The legacy opcode_instrument projects the FFN down-proj output onto per-op fingerprints
with RAW cosine + argmax — no register discipline, no common-mode removal, no null. It
MANUFACTURES crisp opcodes (the instrument that found the structure also faked its
crispness). This classifier replaces that with the validated read:

  1. REGISTER  — classify in the GATE routing register (sign(gate)-CMR), where the
     combinator crystal actually lives (s203 sign-topology ONLY in gate_proj; s231 the
     routing register = sign(gate)-CMR). Requires a GATED MLP (SwiGLU/GeGLU).
  2. COMMON-MODE — subtract the per-layer calibration common-mode before projecting
     (the s202 fix; the gauge that inflates every raw cosine).
  3. RELATIONAL — project onto per-combinator centroids built from the crystal probes;
     report which layers are crystal-bearing by Gram alignment to the CONSENSUS crystal
     (results/combinator-map-consensus/consensus.json, the s219 universal target).
  4. NULL — every per-op energy is a z-score vs an off-target permutation null; a token
     emits an opcode ONLY if z>thresh, else NO-OP (kills "argmax always picks winner").

DESIGN: model-AGNOSTIC. calibrate() and classify() take per-layer gate FEATURE matrices
(the caller runs the model + captures gate); the numpy science is unit-testable on
synthetic data with planted structure, no model load. The instrument (which already
hooks the gate) feeds it; the validation harness feeds it from a real HF forward pass.

CRYSTAL-9 = K I B C S D W Y WHNF (aligns with the consensus Gram order).

License: MIT
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONSENSUS_PATH = (_PROJECT_ROOT / "results" / "combinator-map-consensus"
                  / "consensus.json")


# --------------------------------------------------------------------------- #
# numpy crystal instruments (inlined; mirror relational_loss_distillation)      #
# --------------------------------------------------------------------------- #
def _unit_rows(X: np.ndarray) -> np.ndarray:
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)


def _centroids(X: np.ndarray, labels: np.ndarray) -> np.ndarray:
    C = np.zeros((len(CRYSTAL), X.shape[1]), np.float64)
    for j, c in enumerate(CRYSTAL):
        m = labels == c
        if m.any():
            C[j] = X[m].mean(axis=0)
    return C


def _gram(C: np.ndarray) -> np.ndarray:
    U = _unit_rows(C)
    return np.clip(U @ U.T, -1, 1)


def _offdiag_corr(a: np.ndarray, b: np.ndarray) -> float:
    off = ~np.eye(len(CRYSTAL), dtype=bool)
    x, y = a[off], b[off]
    if x.std() < 1e-9 or y.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


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


def _silhouette_z(X: np.ndarray, labels: np.ndarray, n_perm: int,
                  rng: np.random.Generator) -> float:
    obs = _silhouette(X, labels)
    null = np.array([_silhouette(X, rng.permutation(labels)) for _ in range(n_perm)])
    return float((obs - null.mean()) / (null.std() + 1e-30))


def load_consensus_gram() -> np.ndarray | None:
    if not CONSENSUS_PATH.exists():
        return None
    d = json.loads(CONSENSUS_PATH.read_text())
    if list(d.get("crystal_order", [])) != CRYSTAL:
        return None
    return np.array(d["consensus_gram"], dtype=np.float64)


# --------------------------------------------------------------------------- #
@dataclass
class LayerCalib:
    """Per-layer calibration: the common-mode, centroids, and the null."""
    common_mode: np.ndarray                 # [d] mean sign(gate) over calib probes
    centroids: np.ndarray                   # [9, d] unit per-combinator centroids (CMR)
    null_mean: np.ndarray                   # [9] null projection mean per op
    null_std: np.ndarray                    # [9] null projection std per op
    silhouette_z: float                     # crystal significance at this layer
    gc_consensus: float                     # Gram alignment to consensus (or nan)
    crystal_bearing: bool                   # sil_z>thresh (∧ gc>0 if consensus present)
    null_kind: str = "offtarget"            # "offtarget"(crystal) | "crosstask"


@dataclass
class TokenOpcodes:
    """One token's per-layer opcode read."""
    per_layer: dict = field(default_factory=dict)   # li -> {op: z}
    emitted: dict = field(default_factory=dict)      # li -> [significant ops]
    dominant: str = "·"                              # max-z op (crystal) or no-op


class RelationalCrystalClassifier:
    """Validated FFN-routing opcode reader: gate register, sign-CMR,
    consensus-relational, null-calibrated. Model-agnostic (gate feature matrices in)."""

    def __init__(self, layers: list[int], *, n_perm: int = 300, z_thresh: float = 3.0,
                 sil_z_thresh: float = 2.0, seed: int = 0,
                 consensus_gram: np.ndarray | str | None = "auto"):
        self.layers = list(layers)
        self.n_perm = n_perm
        self.z_thresh = z_thresh
        self.sil_z_thresh = sil_z_thresh
        self.seed = seed
        # "auto" -> load the project consensus; None -> disable (synthetic/no-target);
        # ndarray -> use as given.
        self.consensus_gram = (load_consensus_gram()
                               if isinstance(consensus_gram, str)
                               else consensus_gram)
        self.calib: dict[int, LayerCalib] = {}

    # -- S5 calibration: build the per-layer crystal from the probe activations -- #
    def calibrate(self, gate_by_layer: dict[int, np.ndarray],
                  labels: np.ndarray,
                  null_gate_by_layer: dict[int, np.ndarray] | None = None,
                  ) -> dict[int, LayerCalib]:
        """gate_by_layer[li] = [N, d] gate last-token features for the N crystal probes;
        labels [N] in CRYSTAL. Build per-layer common-mode, CMR centroids, the null,
        silhouette-z, and consensus Gram alignment.

        NULL (s231 v2 — the over-read-killer that no longer under-reads):
          - null_gate_by_layer=None (default, BACK-COMPAT): off-target null — per op j
            the null is the projection of NON-j crystal probes onto j's centroid. But
            every crystal probe is lambda-mode, so "looks more like B than K/I/C?" has
            LOW POWER (the s231 under-read: the C→B arc no-ops at z=3).
          - null_gate_by_layer[li] = [M, d] NON-combinator baseline gate features (e.g.
            natural-text / retrieval tokens where no β-reduction happens): CROSS-TASK
            null — per op j the null is the projection of BASELINE tokens onto j's
            centroid (through the SAME sign-CMR transform). Then z asks "does this token
            look more like op j than a typical natural-text token does?" — recovers the
            lambda compose-arc while keeping retrieval silent."""
        labels = np.asarray(labels)
        rng = np.random.default_rng(self.seed)
        null_kind = "crosstask" if null_gate_by_layer is not None else "offtarget"
        for li in self.layers:
            G = np.asarray(gate_by_layer[li], dtype=np.float64)
            S = np.sign(G)
            common = S.mean(axis=0)                       # the common-mode (gauge)
            X = S - common                                # sign-CMR routing features
            cents = _centroids(X, labels)
            ucents = _unit_rows(cents)
            Xu = _unit_rows(X)
            sims = Xu @ ucents.T                          # [N, 9] cos to each centroid
            li_idx = np.array([CRYSTAL.index(c) for c in labels])
            nmean = np.zeros(len(CRYSTAL))
            nstd = np.ones(len(CRYSTAL))
            if null_gate_by_layer is not None:
                # CROSS-TASK null: project baseline (non-combinator) tokens through the
                # SAME sign-CMR transform onto each centroid; the per-op population is
                # the natural-text baseline distribution.
                B = np.asarray(null_gate_by_layer[li], dtype=np.float64)  # [M, d]
                Vb = np.sign(B) - common                                  # CMR baseline
                Vbu = _unit_rows(Vb)
                bsims = Vbu @ ucents.T                                    # [M, 9]
                for j in range(len(CRYSTAL)):
                    col = bsims[:, j]
                    nmean[j] = col.mean()
                    nstd[j] = col.std() + 1e-9
            else:
                # off-target null per op: projection of NON-op probes onto op centroid
                for j in range(len(CRYSTAL)):
                    off = sims[li_idx != j, j]
                    if off.size:
                        nmean[j] = off.mean()
                        nstd[j] = off.std() + 1e-9
            sil_z = _silhouette_z(X, labels, self.n_perm, rng)
            gc = (_offdiag_corr(_gram(cents), self.consensus_gram)
                  if self.consensus_gram is not None else float("nan"))
            bearing = sil_z > self.sil_z_thresh and (np.isnan(gc) or gc > 0.0)
            self.calib[li] = LayerCalib(
                common_mode=common, centroids=ucents, null_mean=nmean, null_std=nstd,
                silhouette_z=round(sil_z, 3),
                gc_consensus=(round(gc, 3) if not np.isnan(gc) else float("nan")),
                crystal_bearing=bool(bearing), null_kind=null_kind)
        return self.calib

    @property
    def crystal_layers(self) -> list[int]:
        return [li for li, c in self.calib.items() if c.crystal_bearing]

    # -- S1 classify: token gate -> null-calibrated per-op z, emit if significant -- #
    def classify(self, gate_by_layer_token: dict[int, np.ndarray]) -> TokenOpcodes:
        """gate_by_layer_token[li] = [d] one token's gate at layer li. Returns per-layer
        op z-scores, the significant (z>thresh) opcodes, and the dominant op across
        crystal-bearing layers (or '·' no-op if none significant)."""
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
            sims = cal.centroids @ (v / nv)               # [9] cos to each centroid
            z = (sims - cal.null_mean) / cal.null_std     # null-calibrated per op
            zmap = {op: round(float(zz), 3) for op, zz in zip(CRYSTAL, z, strict=True)}
            out.per_layer[li] = zmap
            sig = [op for op, zz in zmap.items() if zz > self.z_thresh]
            if sig:
                out.emitted[li] = sig
            if cal.crystal_bearing:                       # dominant: crystal only
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
            "per_layer": {li: {"sil_z": c.silhouette_z, "gc_consensus": c.gc_consensus,
                               "crystal_bearing": c.crystal_bearing}
                          for li, c in self.calib.items()},
            "z_thresh": self.z_thresh, "sil_z_thresh": self.sil_z_thresh,
            "has_consensus": self.consensus_gram is not None,
            "null_kind": (next(iter(null_kinds)) if len(null_kinds) == 1
                          else sorted(null_kinds)),
        }


# --------------------------------------------------------------------------- #
# Synthetic smoke — verify the numpy science with planted per-combinator structure #
# --------------------------------------------------------------------------- #
def _smoke() -> None:
    rng = np.random.default_rng(0)
    d, per = 64, 40
    layers = [0, 1, 2]
    # layer 1 = crystal-bearing (planted combinator directions); 0,2 = noise
    dirs = rng.standard_normal((len(CRYSTAL), d))
    labels = np.array([c for c in CRYSTAL for _ in range(per)])
    common = rng.standard_normal(d) * 3.0                 # a strong common-mode (gauge)
    gate_cal = {}
    for li in layers:
        rows = []
        for c in CRYSTAL:
            base = dirs[CRYSTAL.index(c)] if li == 1 else np.zeros(d)
            sig = 2.5 if li == 1 else 0.0
            rows.append(common + sig * base + rng.standard_normal((per, d)))
        gate_cal[li] = np.concatenate(rows, axis=0)
    clf = RelationalCrystalClassifier(layers, n_perm=120, z_thresh=3.0, seed=0,
                                      consensus_gram=None)
    clf.calibrate(gate_cal, labels)
    summ = clf.calibration_summary()
    print("calibration:", json.dumps(summ, indent=2))
    assert 1 in clf.crystal_layers, "planted crystal layer 1 not detected"
    assert 0 not in clf.crystal_layers and 2 not in clf.crystal_layers, \
        "noise layers wrongly flagged crystal-bearing"
    # a 'B' token: common-mode + B direction at layer 1
    tok = {li: (common + (3.0 * dirs[CRYSTAL.index("B")] if li == 1 else 0.0)
                + rng.standard_normal(d) * 0.5) for li in layers}
    res = clf.classify(tok)
    print("B-token dominant:", res.dominant, "| emitted:", res.emitted)
    assert res.dominant == "B", f"expected B, got {res.dominant}"
    # a pure common-mode token (no combinator) -> NO-OP (the over-read killer)
    noop = {li: common + rng.standard_normal(d) * 0.5 for li in layers}
    rn = clf.classify(noop)
    print("common-mode-only token dominant:", rn.dominant, "| emitted:", rn.emitted)
    assert rn.dominant == "·", f"common-mode token should be no-op, got {rn.dominant}"
    print("\n✅ smoke (offtarget null) passed: crystal layer detected, B fires, "
          "common-mode -> no-op")

    # -- CROSS-TASK null (s231 v2): baseline = common-mode-only "natural-text" -- #
    base = {li: np.stack([common + rng.standard_normal(d) * 0.5 for _ in range(per)])
            for li in layers}
    clf2 = RelationalCrystalClassifier(layers, n_perm=120, z_thresh=3.0, seed=0,
                                       consensus_gram=None)
    clf2.calibrate(gate_cal, labels, null_gate_by_layer=base)
    summ2 = clf2.calibration_summary()
    assert summ2["null_kind"] == "crosstask", "cross-task null not recorded"
    assert 1 in clf2.crystal_layers, "planted crystal layer 1 not detected (crosstask)"
    res2 = clf2.classify(tok)
    print("cross-task B-token dominant:", res2.dominant, "| emitted:", res2.emitted)
    assert res2.dominant == "B", f"expected B (crosstask), got {res2.dominant}"
    rn2 = clf2.classify(noop)
    print("cross-task common-mode token dominant:", rn2.dominant)
    assert rn2.dominant == "·", \
        f"common-mode token should be no-op (crosstask), got {rn2.dominant}"
    print("✅ smoke (crosstask null) passed: B fires vs natural-text baseline, "
          "common-mode -> no-op")


if __name__ == "__main__":
    _smoke()
