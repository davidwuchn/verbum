#!/usr/bin/env python3
"""§P-PLATE-LINKER-1 — do two ternary wires compose on one frozen base, and does
key-subspace angle PREDICT the retention loss? (device A + contract C keystone).

Pre-reg: mementum/knowledge/explore/optical-design-laws.md §P-PLATE-LINKER-1
(FROZEN s311, Michael-approved). The artifact-track keystone: git-for-weights with
a type checker. Two independently-baked ternary wires on ONE frozen base compose
additively (each retains its own frozen gate set) IFF their KEY (A/input) subspaces
are angularly separated, and retention-under-merge degrades as a MONOTONE function
of measured key-subspace principal-angle collision c -> near-perfect at
orthogonality. The measured angle PREDICTS the retention loss => the linker is a
predictor, not try-and-see.

Wire-1 = the existing gd_cd wire (writeback_compile default BANK, landmark->country
->capital hop-2, LoRA r=16 FFN L22-L29, KL-on-CoT teacher, ternary factors per
§TERNARIZE-FACTORS-1 retention ~1.0). Wire-2 = SAME recipe on the DISJOINT
country/landmark bank baked clean in s311 (bake_wire2.WIRE2_BANK, verdict
WIRE-COMPILES +GD-REQUIRED). Same relation, disjoint entities => low A-collision
(different country-key filters) but high B-collision (both write the capital
region) — the discriminating case.

Reuse (NO FORK, lambda one_way): imports writeback_compile (LoRALinear, BANK, Cell,
prompts, BAND, constants, gd_cd training shape), ternarize_factors (per-component
TWN + shuffle null), bake_wire2 (WIRE2_BANK). Frozen generators UNTOUCHED — both
wires bit-reproduce their standalone results on their own banks.

Geometry (pure numpy, --validate-covered):
  row_basis(A)            : orthonormal basis (in x r) of A's row space (top-r RSV).
  collision(A1,A2)        : ||Q1^T Q2||_F^2 / r  in [0,1] (sum cos^2 principal angles).
  slerp_rotate(A1,A2,th)  : rotate A2's row space toward A1's by fraction th on the
                            Grassmann geodesic (principal-vector slerp), PRESERVING
                            Frobenius norm; th=0 -> natural, th=1 -> aligned (c->1).

Arms (one process, per-seed factors -> ternary):
  base                  : frozen host (floor).
  wire1 / wire2         : each installed ALONE (reproduce standalone gates).
  merge                 : base + D1 + D2 (the NATURAL additive linker merge).
  merge_shuf_self       : base + shuffle(D_self) + D_other (G3 specificity of the
                          RETAINED wire — is retention wire-geometry, not mass?).
  rot(th)               : base + D1 + D2_rot(th) (COLLISION SWEEP; wire-1 retention;
                          matched Frobenius norm, FIXED B2 — a geometry control).
  shuffle2              : base + D1 + shuffle(D2) at matched norm (mass floor).

Gates (verbum.dsp, paired-permutation, primaries Bonferroni alpha/3):
  PL1 COMPOSES (primary)       : under merge BOTH wires pass own frozen G1 (wire,
                                 flip B1 AND B2) + G3 (specificity vs merge_shuf_self).
  PL2 ANGLE-PREDICTS (KEYSTONE): th-sweep degradation-vs-c is monotone (corr>0,
                                 p<0.05 vs shuffled-c null) AND the natural pair's
                                 degradation falls in the fit CI at MEASURED c_nat.
  PL3 COLLISION-CAUSAL         : rot(max-c) degrades wire-1 MORE than shuffle2 at
                                 MATCHED added norm (p<0.05) AND more than merge
                                 => degradation is collision, not mass.
  PL4 HOST-SANE (advisory)     : innocent CE within 2% rel base under merge; native
                                 g/h within 0.10 absolute.

Verdicts: LINKS(+ANGLE-PREDICTIVE) (PL1 & PL2 & PL3) / COLLISION-BLIND (PL1 & ~PL3)
  / LINKS-OPAQUE (PL1 & ~PL2 & PL3) / NO-COMPOSE (~PL1) / HOST-DAMAGED (~PL4).

A-priori (NOT tuned): ~55% LINKS(+ANGLE-PREDICTIVE) / ~25% LINKS-OPAQUE / ~12%
  COLLISION-BLIND / ~6% NO-COMPOSE / ~2% HOST-DAMAGED.

Cadence (s222): --validate (no model) -> smoke (--n-cells, direction NOT read) ->
Michael GO -> full run tmux main:1 -> frozen scoring.

License: MIT (lambda provenance).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_WRAP = _HERE.parents[1] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

import bake_wire2 as w2  # noqa: E402  (WIRE2_BANK; frozen bake generator untouched)
import ternarize_delta as td  # noqa: E402  (pure helpers: ternarize_twn, plate_stats)
import ternarize_factors as tf  # noqa: E402  (ternarize_factors / shuffle_factors)
import writeback_compile as wb  # noqa: E402  (module reuse, no fork)
from holo_frag import _json_safe  # noqa: E402

from verbum.dsp import gate, paired_permutation  # noqa: E402

SPLITS = wb.SPLITS
HELD = ("B1", "B2")


# ══════════════════════════════════════════════════════════════════════════
# Geometry — principal-angle collision + norm-preserving Grassmann rotation
# ══════════════════════════════════════════════════════════════════════════
def row_basis(a: np.ndarray, r: int | None = None) -> np.ndarray:
    """Orthonormal basis (in, r) of A's row space = top-r right singular vectors.
    A is (r_rank, in). Defaults r = min(A.shape)."""
    a = np.asarray(a, dtype=np.float64)
    _, _, vt = np.linalg.svd(a, full_matrices=False)
    k = a.shape[0] if r is None else r
    k = min(k, vt.shape[0])
    return vt[:k].T                                    # (in, k)


def collision(a1: np.ndarray, a2: np.ndarray) -> float:
    """c = ||Q1^T Q2||_F^2 / r in [0,1] = mean over the r directions of cos^2 of the
    principal angles between the two A row spaces (0 orthogonal, 1 identical)."""
    q1 = row_basis(a1)
    q2 = row_basis(a2)
    r = min(q1.shape[1], q2.shape[1])
    m = q1[:, :r].T @ q2[:, :r]                        # (r, r)
    return float((m * m).sum() / r)


def slerp_rotate(a1: np.ndarray, a2: np.ndarray, theta: float) -> np.ndarray:
    """Rotate A2's row space toward A1's by fraction theta on the Grassmann geodesic
    (principal-vector slerp). theta=0 -> A2 unchanged (subspace); theta=1 -> A2's row
    space aligned with A1's principal directions (collision -> 1). Frobenius norm of
    A2 is PRESERVED (coefficients kept in the principal basis, orthonormal target)."""
    a2 = np.asarray(a2, dtype=np.float64)
    q1 = row_basis(a1)
    q2 = row_basis(a2)
    r = min(q1.shape[1], q2.shape[1])
    q1, q2 = q1[:, :r], q2[:, :r]
    y, s, zt = np.linalg.svd(q1.T @ q2)                # principal alignment
    s = np.clip(s, -1.0, 1.0)
    p1 = q1 @ y                                        # principal dirs in subspace 1
    p2 = q2 @ zt.T                                     # principal dirs in subspace 2
    phi = np.arccos(s)                                 # principal angles
    cols = []
    for i in range(r):
        f = np.sin(phi[i])
        if f > 1e-9:
            w = (np.sin((1.0 - theta) * phi[i]) * p2[:, i]
                 + np.sin(theta * phi[i]) * p1[:, i]) / f
        else:
            w = p2[:, i]
        cols.append(w)
    w_mat = np.stack(cols, axis=1)                     # (in, r)
    q_rot, _ = np.linalg.qr(w_mat)                     # orthonormalize span
    coeff = a2 @ p2                                    # (r_rank, r) coeffs in p2 basis
    a2_rot = coeff @ q_rot.T                           # (r_rank, in), ||.||_F preserved
    return a2_rot.astype(np.float32)


def match_frob(delta: np.ndarray, target_norm: float) -> np.ndarray:
    """Scale delta to a target Frobenius norm (matched added mass)."""
    n = float(np.linalg.norm(delta))
    if n < 1e-12:
        return delta.astype(np.float32)
    return (delta * (target_norm / n)).astype(np.float32)


def band_collision(fac1: dict, fac2: dict) -> float:
    """Mean over shared band matrices of collision(A1, A2) (float A factors)."""
    keys = [k for k in fac1 if k in fac2]
    return float(np.mean([collision(fac1[k][1], fac2[k][1]) for k in keys]))


# ══════════════════════════════════════════════════════════════════════════
# Frozen scoring + verdict (pure; --validate exercises planted worlds)
# ══════════════════════════════════════════════════════════════════════════
def _g(a, b, rng, alpha, name):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    return gate(float(np.mean(a - b)), paired_permutation(a, b, rng),
                "greater", alpha, name=name)


def _held(d: dict) -> np.ndarray:
    return np.concatenate([np.asarray(d["B1"], float), np.asarray(d["B2"], float)])


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    if x.std() < 1e-12 or y.std() < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def pl1_compose(acc: dict, rng, alpha: float) -> dict:
    """For each wire: G1 (merge > base, flip B1 AND B2) + G3 (merge held >
    merge_shuf_self held). acc[wire] has conds base/merge/merge_shuf_self."""
    a3 = alpha / 3.0
    out = {}
    for w in ("wire1", "wire2"):
        c = acc[w]
        g1 = {}
        for sp in HELD:
            gg = _g(c["merge"][sp], c["base"][sp], rng, a3, f"{w}-PL1-G1-{sp}")
            g1[sp] = {"gate": gg, "flip": bool(np.mean(c["merge"][sp])
                                               > np.mean(c["base"][sp]))}
        g1_ok = all(g1[sp]["gate"].verdict and g1[sp]["flip"] for sp in HELD)
        g3 = _g(_held(c["merge"]), _held(c["merge_shuf_self"]), rng, a3,
                f"{w}-PL1-G3")
        out[w] = {"G1": bool(g1_ok), "G1_detail": g1,
                  "G3": bool(g3.verdict), "G3_detail": g3}
    out["ok"] = bool(all(out[w]["G1"] and out[w]["G3"]
                         for w in ("wire1", "wire2")))
    return out


def pl2_predicts(sweep: dict, c_nat: float, deg_natural: np.ndarray,
                 rng, alpha: float) -> dict:
    """sweep: {"c": [c(th)], "deg": [per-cell degradation array at each th]} for
    wire-1 (degradation = solo_held - rot(th)_held). Monotone corr(c, deg)>0 vs
    shuffled-c null; natural degradation within linear-fit bootstrap CI at c_nat."""
    a3 = alpha / 3.0
    cs = np.asarray(sweep["c"], float)
    deg_mean = np.array([np.mean(d) for d in sweep["deg"]], float)
    corr = _pearson(cs, deg_mean)
    # shuffled-c null: permute the c labels among th points
    null = []
    for _ in range(5000):
        null.append(_pearson(rng.permutation(cs), deg_mean))
    null = np.asarray(null)
    p = float(np.mean(null >= corr))
    mono_ok = bool(corr > 0 and p < a3)
    # Natural-within-fit: PAIRED cell-bootstrap of (natural - predicted@c_nat) over
    # the SAME held cells (sweep degradation and natural degradation are per-cell
    # arrays over wire-1's held cells). This accounts for BOTH the fit uncertainty
    # and the natural point's own sampling noise; within-CI <=> the diff CI holds 0.
    deg = [np.asarray(d, float) for d in sweep["deg"]]
    dnat = np.asarray(deg_natural, float)
    n_cells = len(deg[0])
    diffs = []
    for _ in range(2000):
        idx = rng.integers(0, n_cells, n_cells)
        ym = np.array([d[idx].mean() for d in deg])
        b, a = np.polyfit(cs, ym, 1)
        diffs.append(float(dnat[idx].mean() - (a + b * c_nat)))
    diffs = np.asarray(diffs)
    lo, hi = float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))
    within = bool(lo <= 0.0 <= hi)
    return {"PL2": bool(mono_ok and within), "corr": corr, "p": p,
            "mono_ok": mono_ok, "within_ci": within,
            "diff_ci": [lo, hi], "nat_deg": float(dnat.mean()),
            "c_nat": float(c_nat), "c_grid": cs.tolist(),
            "deg_grid": deg_mean.tolist()}


def pl3_causal(deg_rot_maxc: np.ndarray, deg_shuffle: np.ndarray,
               deg_natural: np.ndarray, rng, alpha: float) -> dict:
    """rot(max-c) degrades wire-1 MORE than shuffle2 (matched mass) => collision,
    not mass; AND more than the natural merge."""
    a3 = alpha / 3.0
    g = _g(deg_rot_maxc, deg_shuffle, rng, a3, "PL3-rot>shuffle")
    more_than_nat = bool(np.mean(deg_rot_maxc) > np.mean(deg_natural))
    return {"PL3": bool(g.verdict and more_than_nat), "detail": g,
            "rot_deg": float(np.mean(deg_rot_maxc)),
            "shuffle_deg": float(np.mean(deg_shuffle)),
            "nat_deg": float(np.mean(deg_natural)),
            "more_than_nat": more_than_nat}


def pl4_host(ce: dict, gh: dict) -> dict:
    ce_ok = ce["merge"] <= ce["base"] * 1.02
    g_ok = gh["merge"][0] >= gh["base"][0] - 0.10
    h_ok = gh["merge"][1] >= gh["base"][1] - 0.10
    return {"PL4": bool(ce_ok and g_ok and h_ok),
            "ce": ce["merge"], "ce_base": ce["base"],
            "g_acc": gh["merge"][0], "h_acc": gh["merge"][1]}


def verdict_of(gate0_ok: bool, pl1: dict, pl2: dict, pl3: dict,
               pl4: dict) -> str:
    if not gate0_ok:
        return "VOID (gate-0)"
    if not pl4["PL4"]:
        return "HOST-DAMAGED"
    if not pl1["ok"]:
        return "NO-COMPOSE"
    if pl2["PL2"] and pl3["PL3"]:
        return "LINKS (+ANGLE-PREDICTIVE)"
    if not pl3["PL3"]:
        return "COLLISION-BLIND"
    return "LINKS-OPAQUE"


def score(gate0_ok: bool, acc: dict, sweep: dict, c_nat: float,
          ce: dict, gh: dict, rng, alpha: float) -> dict:
    """Full frozen scoring. acc[wire][cond][split]; sweep for wire-1; deg = per-cell
    (held) solo - cond. Returns gates + verdict."""
    solo = _held(acc["wire1"]["solo"])
    deg_natural = solo - _held(acc["wire1"]["merge"])
    deg_shuffle = solo - _held(acc["wire1"]["shuffle2"])
    deg_rot_maxc = solo - _held(acc["wire1"]["rot_maxc"])
    pl1 = pl1_compose(acc, rng, alpha)
    pl2 = pl2_predicts(sweep, c_nat, deg_natural, rng, alpha)
    pl3 = pl3_causal(deg_rot_maxc, deg_shuffle, deg_natural, rng, alpha)
    pl4 = pl4_host(ce, gh)
    v = verdict_of(gate0_ok, pl1, pl2, pl3, pl4)
    return {"PL1": pl1, "PL2": pl2, "PL3": pl3, "PL4": pl4, "verdict": v}


# ══════════════════════════════════════════════════════════════════════════
# --validate (no model)
# ══════════════════════════════════════════════════════════════════════════
def _rand_subspace_A(rng, r=16, din=64):
    return rng.normal(size=(r, din)).astype(np.float32)


def run_validate(alpha: float) -> int:
    ok = True
    print("── §P-PLATE-LINKER-1 --validate (no model) ──")
    rng = np.random.default_rng(0)

    # 1. collision: orthogonal -> 0, identical -> 1, known 1-D angle -> cos^2
    din = 32
    a_ident = _rand_subspace_A(rng, r=8, din=din)
    c_id = collision(a_ident, a_ident.copy())
    # orthogonal row spaces via disjoint coordinate blocks
    a_o1 = np.zeros((4, din), np.float32)
    a_o1[np.arange(4), np.arange(4)] = 1
    a_o2 = np.zeros((4, din), np.float32)
    a_o2[np.arange(4), np.arange(4) + 4] = 1
    c_orth = collision(a_o1, a_o2)
    # known 1-D principal angle
    phi = 0.6
    u = np.zeros((1, din), np.float32)
    u[0, 0] = 1.0
    v = np.zeros((1, din), np.float32)
    v[0, 0] = np.cos(phi)
    v[0, 1] = np.sin(phi)
    c_ang = collision(u, v)
    good = (abs(c_id - 1.0) < 1e-6 and c_orth < 1e-6
            and abs(c_ang - np.cos(phi) ** 2) < 1e-4)
    print(f"[V] collision: identical {c_id:.4f} orthogonal {c_orth:.2e} "
          f"angle(cos^2={np.cos(phi) ** 2:.4f}) {c_ang:.4f} "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 2. slerp_rotate: norm preserved; c(0)=c_nat; c(1)~1; monotone in theta
    a1 = _rand_subspace_A(rng, r=16, din=64)
    a2 = _rand_subspace_A(rng, r=16, din=64)
    c_nat = collision(a1, a2)
    n2 = float(np.linalg.norm(a2))
    thetas = [0.0, 0.25, 0.5, 0.75, 1.0]
    cs, norms = [], []
    for th in thetas:
        a2r = slerp_rotate(a1, a2, th)
        cs.append(collision(a1, a2r))
        norms.append(float(np.linalg.norm(a2r)))
    norm_ok = all(abs(n - n2) < 1e-3 for n in norms)
    ends_ok = abs(cs[0] - c_nat) < 1e-3 and cs[-1] > 0.95
    mono_ok = all(cs[i + 1] >= cs[i] - 1e-6 for i in range(len(cs) - 1))
    good = norm_ok and ends_ok and mono_ok
    print(f"[V] slerp: norm_preserved={norm_ok} c(0)={cs[0]:.3f}(nat {c_nat:.3f}) "
          f"c(1)={cs[-1]:.3f} monotone={mono_ok} {'OK' if good else 'FAIL'}")
    ok &= good

    # 3. additive merge accounting: (B+D1+D2) - D2 - D1 == B exactly (float32 add)
    b = rng.normal(size=(48, 64)).astype(np.float32)
    d1 = rng.normal(size=(48, 64)).astype(np.float32) * 0.1
    d2 = rng.normal(size=(48, 64)).astype(np.float32) * 0.1
    merged = b + d1 + d2
    back = merged - d2 - d1
    # bit-exact restore comes from copy_ of saved originals in the model path; here
    # we only assert the additive identity holds to float32 tolerance.
    good = float(np.abs(back - b).max()) < 1e-4
    print(f"[V] additive merge: max|restore-B| {np.abs(back - b).max():.2e} "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 4. match_frob: scaled delta hits the target norm
    d = rng.normal(size=(48, 64)).astype(np.float32)
    dm = match_frob(d, 3.0)
    good = abs(float(np.linalg.norm(dm)) - 3.0) < 1e-4
    print(f"[V] match_frob: ||scaled|| {np.linalg.norm(dm):.4f} (want 3.0) "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 5. band_collision aggregates over matrices
    f1 = {(0, "g"): (None, a1), (1, "g"): (None, a_ident)}
    f2 = {(0, "g"): (None, a2), (1, "g"): (None, a_ident.copy())}
    bc = band_collision(f1, f2)
    good = abs(bc - 0.5 * (collision(a1, a2) + 1.0)) < 1e-4
    print(f"[V] band_collision: {bc:.4f} {'OK' if good else 'FAIL'}")
    ok &= good

    # 6. verdict planted worlds (wide gaps -> logic, not power)
    def mk_acc(w1_merge, w2_merge, base=(.2, .12, .3), shuf_self=(.2, .12, .2),
               solo=(.98, .95, .98), rot_maxc=(.5, .3, .5), shuffle2=(.9, .85, .9),
               n=80):
        rw = np.random.default_rng(7)

        def arr(p):
            return (rw.random(n) < p).astype(float)

        def sp(t):
            return {"TRAIN": arr(t[0]), "B1": arr(t[1]), "B2": arr(t[2])}
        acc = {}
        for w, mg in (("wire1", w1_merge), ("wire2", w2_merge)):
            acc[w] = {"base": sp(base), "solo": sp(solo), "merge": sp(mg),
                      "merge_shuf_self": sp(shuf_self)}
        acc["wire1"]["rot_maxc"] = sp(rot_maxc)
        acc["wire1"]["shuffle2"] = sp(shuffle2)
        return acc

    def mk_sweep(cs, deg_lo, deg_hi, n=160, noise=0.01, flat=False):
        rw = np.random.default_rng(11)
        cs = np.asarray(cs, float)
        degs = []
        for c in cs:
            base_deg = (deg_lo if flat else deg_lo + (deg_hi - deg_lo) * c)
            degs.append(np.clip(base_deg + rw.normal(0, noise, n), 0, 1))
        return {"c": cs.tolist(), "deg": degs}

    cs = [0.05, 0.2, 0.35, 0.5, 0.65, 0.8, 0.95]

    def world(name, want, acc, sweep, c_nat, deg_nat, ce_bad=False):
        ce = {"base": 1.0, "merge": 1.10 if ce_bad else 1.0}
        gh = {"base": (0.95, 0.95), "merge": (0.95, 0.95)}
        rr = score(True, acc, sweep, c_nat, ce, gh, np.random.default_rng(3), alpha)
        hit = want in rr["verdict"]
        print(f"[V] {name}-world -> {rr['verdict']} (want {want}) "
              f"{'OK' if hit else 'FAIL'} "
              f"[PL1={rr['PL1']['ok']} PL2={rr['PL2']['PL2']} "
              f"PL3={rr['PL3']['PL3']} PL4={rr['PL4']['PL4']}]")
        return hit

    # LINKS(+ANGLE-PREDICTIVE): compose OK, strong monotone sweep, rot>>shuffle,
    # and the natural pair (deg ~0.075 from solo-merge) sits ON the fitted line at
    # its measured c_nat (line 0.02+0.7c -> 0.076 at c_nat=0.08).
    ok &= world(
        "links-predictive", "LINKS (+ANGLE-PREDICTIVE)",
        mk_acc((.9, .88, .9), (.9, .88, .9),
               rot_maxc=(.35, .2, .35), shuffle2=(.92, .9, .92)),
        mk_sweep(cs, 0.02, 0.7, noise=0.10), c_nat=0.08,
        deg_nat=np.full(160, 0.076))
    # LINKS-OPAQUE: compose OK, sweep FLAT (no prediction), but rot still > shuffle
    ok &= world(
        "links-opaque", "LINKS-OPAQUE",
        mk_acc((.9, .88, .9), (.9, .88, .9),
               rot_maxc=(.35, .2, .35), shuffle2=(.92, .9, .92)),
        mk_sweep(cs, 0.4, 0.4, flat=True, noise=0.15), c_nat=0.12,
        deg_nat=np.full(160, 0.06))
    # COLLISION-BLIND: compose OK, monotone sweep, but rot ~ shuffle (mass, not angle)
    ok &= world(
        "collision-blind", "COLLISION-BLIND",
        mk_acc((.9, .88, .9), (.9, .88, .9),
               rot_maxc=(.5, .35, .5), shuffle2=(.5, .35, .5)),
        mk_sweep(cs, 0.02, 0.7), c_nat=0.12,
        deg_nat=np.full(160, 0.06))
    # NO-COMPOSE: wire-2 dies under merge (retention gone)
    ok &= world(
        "no-compose", "NO-COMPOSE",
        mk_acc((.9, .88, .9), (.25, .13, .3)),
        mk_sweep(cs, 0.02, 0.7), c_nat=0.12,
        deg_nat=np.full(160, 0.06))
    # HOST-DAMAGED: PL4 fails
    ok &= world(
        "host-damaged", "HOST-DAMAGED",
        mk_acc((.9, .88, .9), (.9, .88, .9)),
        mk_sweep(cs, 0.02, 0.7), c_nat=0.12,
        deg_nat=np.full(160, 0.06), ce_bad=True)

    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path
# ══════════════════════════════════════════════════════════════════════════
def _load_valid(record_dir: str) -> tuple[list, bool]:
    """Frozen gate-0 valid cells from a committed bake record (wire-1 or wire-2)."""
    g0 = json.loads((Path(record_dir) / "gate0.json").read_text())
    fields = ("landmark", "city", "country", "capital", "split")
    valid = [wb.Cell(**{k: c[k] for k in fields}) for c in g0["cells"]
             if c.get("g_ok") and c.get("h_ok") and c.get("cot_ok")]
    return valid, bool(g0["gate0_ok"])


def run_model(args) -> int:
    import operand_multihop3 as mh3
    import torch
    import torch.nn.functional as F
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps"
                           or torch.backends.mps.is_available()) else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    dec, _norm, _lm_head = mh3.resolve_parts(model)
    n_layers = len(dec)
    band = list(range(round(wb.BAND[0] * n_layers),
                      round(wb.BAND[1] * n_layers) + 1))
    projs = ("gate_proj", "up_proj", "down_proj")
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    thetas = [float(x) for x in args.theta_grid.split(",")]

    def first_tid(w: str) -> int:
        return mh3.first_tid(tok, w)

    # ── two wires, two banks: build an eval context per bank (captures its union) ──
    wire1_valid, g0_1 = _load_valid(args.wire1_record)
    wire2_valid, g0_2 = _load_valid(args.wire2_record)
    gate0_ok = g0_1 and g0_2

    def cap_smoke(valid):
        if not args.n_cells:
            return valid
        by = {sp: [c for c in valid if c.split == sp] for sp in SPLITS}
        return [c for sp in SPLITS for c in by[sp][:args.n_cells]]

    wire1_valid = cap_smoke(wire1_valid)
    wire2_valid = cap_smoke(wire2_valid)

    wb_default_bank = dict(wb.BANK)      # snapshot wire-1's default bank

    def make_eval(bank: dict, valid: list):
        prev = dict(wb.BANK)
        w2._install(bank)
        tid_map, drop = {}, set()
        for w in wb.union_words():
            t = first_tid(w)
            clash = [x for x, tt in tid_map.items() if tt == t]
            if clash:
                drop.add(w)
                drop.update(clash)
            tid_map[w] = t
        union = {w: tid_map[w] for w in sorted(set(wb.union_words()) - drop)}
        countries = sorted(bank)
        caps = sorted({cap for cap, _ in bank.values()})
        w2._install(prev)

        def logits_last(prompt: str) -> np.ndarray:
            ids = tok(prompt, return_tensors="pt").to(dev)
            with torch.no_grad():
                return model(**ids).logits[0, -1, :].float().cpu().numpy()

        def argmax_union(lo):
            return max(union, key=lambda w: lo[union[w]])

        def margin(lo, truth):
            return float(lo[union[truth]]
                         - max(lo[union[w]] for w in union if w != truth))

        def eval_cells() -> list[dict]:
            rows = []
            for c in valid:
                lo = logits_last(wb.DIRECT_PROMPT.format(lm=c.landmark))
                arg = argmax_union(lo)
                rows.append({"landmark": c.landmark, "split": c.split,
                             "correct": float(wb.first_word(arg)
                                              == wb.first_word(c.capital)),
                             "margin": margin(lo, c.capital)})
            return rows

        def gh_accs():
            g = [max(countries, key=lambda w: logits_last(
                wb.G_QUERY_PREFIX + wb.G_QUERY.format(lm=c.landmark))[first_tid(w)])
                == c.country for c in valid]
            h = [wb.first_word(max(caps, key=lambda w: logits_last(
                wb.CAP_PREFIX + wb.CAP_QUERY.format(x=co))[first_tid(w)]))
                == wb.first_word(bank[co][0]) for co in countries]
            return float(np.mean(g)), float(np.mean(h))

        return eval_cells, gh_accs

    def ce_innocents() -> float:
        tot, n = 0.0, 0
        for t in wb.CE_TEXTS:
            ids = tok(t, return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits
            lp = F.log_softmax(lo[0, :-1].float(), dim=-1)
            tgt = ids.input_ids[0, 1:]
            tot += float(-lp[torch.arange(len(tgt)), tgt].sum())
            n += len(tgt)
        return tot / max(n, 1)

    eval1, gh1 = make_eval(wb_default_bank, wire1_valid)
    eval2, _gh2 = make_eval(w2.WIRE2_BANK, wire2_valid)
    ns1 = {sp: sum(1 for c in wire1_valid if c.split == sp) for sp in SPLITS}
    ns2 = {sp: sum(1 for c in wire2_valid if c.split == sp) for sp in SPLITS}
    print(f"[pl] {args.model_id} dev={dev} n_layers={n_layers} "
          f"band=L{band[0]}..L{band[-1]} wire1={ns1} wire2={ns2} "
          f"seeds={args.seeds} steps={args.steps} thetas={thetas} "
          f"gate0_ok={gate0_ok}", flush=True)

    # ── teacher probs + gd_cd train/extract factors (per bank's TRAIN cells) ──
    def teacher_probs(valid):
        tps = {}
        for c in [x for x in valid if x.split == "TRAIN"]:
            ids = tok(wb.TEACHER_PROMPT.format(lm=c.landmark, c=c.country),
                      return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits[0, -1, :].float().cpu()
            tps[c.landmark] = torch.softmax(lo, dim=-1)
        return tps

    def train_extract(valid, tp, seed) -> dict:
        torch.manual_seed(seed)
        train_cells = [c for c in valid if c.split == "TRAIN"]
        wrapped, params = [], []
        for li in band:
            m = dec[li].mlp
            for name in projs:
                orig = getattr(m, name)
                lw = wb.LoRALinear(orig, r=args.lora_r, alpha=2 * args.lora_r)
                setattr(m, name, lw)
                wrapped.append((m, name, orig, lw, li))
                params += [lw.A, lw.B]
        opt = torch.optim.Adam(params, lr=args.lr)
        prompts = [wb.DIRECT_PROMPT.format(lm=c.landmark) for c in train_cells]
        batch = tok(prompts, return_tensors="pt", padding=True).to(dev)
        tpv = torch.stack([tp[c.landmark] for c in train_cells]).to(dev)
        for step in range(args.steps):
            opt.zero_grad()
            lo = model(**batch).logits[:, -1, :].float()
            loss = -(tpv * F.log_softmax(lo, dim=-1)).sum(-1).mean()
            loss.backward()
            opt.step()
            if step % max(args.steps // 5, 1) == 0 or step == args.steps - 1:
                print(f"    step {step:4d} loss {float(loss.detach()):.4f}",
                      flush=True)
        fac = {}
        for (m, name, orig, lw, li) in wrapped:
            with torch.no_grad():
                fac[(li, name)] = (lw.B.float().cpu().numpy(),
                                   lw.A.float().cpu().numpy(), float(lw.scale))
            setattr(m, name, orig)
        return fac

    # saved originals over the shared band (apply/restore via copy_ = bit-exact)
    orig_w = {(li, name): getattr(dec[li].mlp, name).weight.detach().clone()
              for li in band for name in projs}

    def apply_plate(deltas: dict):
        for (li, name), d in deltas.items():
            w = getattr(dec[li].mlp, name).weight
            add = torch.tensor(d, dtype=w.dtype, device=w.device)
            with torch.no_grad():
                w.copy_(orig_w[(li, name)] + add)

    def restore_plate():
        for (li, name), w0 in orig_w.items():
            with torch.no_grad():
                getattr(dec[li].mlp, name).weight.copy_(w0)

    def eval_arm(deltas, eval_cells):
        apply_plate(deltas)
        rows = eval_cells()
        restore_plate()
        return rows

    def to_arrays(rows_by_seed, order):
        per = {}
        for sp in SPLITS:
            mat = []
            for rows in rows_by_seed:
                by = {r["landmark"]: r["correct"] for r in rows
                      if r["split"] == sp}
                mat.append([by[lm] for lm in order[sp]])
            per[sp] = np.mean(np.array(mat), axis=0)
        return per

    order1 = {sp: [c.landmark for c in wire1_valid if c.split == sp]
              for sp in SPLITS}
    order2 = {sp: [c.landmark for c in wire2_valid if c.split == sp]
              for sp in SPLITS}

    # ── base eval (both banks) ──
    print("[pl] ── base ──", flush=True)
    base1_seed = [eval1()]
    base2_seed = [eval2()]
    base_ce = ce_innocents()
    base_gh = gh1()

    tp1 = teacher_probs(wire1_valid)
    tp2 = teacher_probs(wire2_valid)

    # per-seed accumulation of every arm's rows (both banks where relevant)
    acc_rows = {"wire1": {k: [] for k in
                          ("solo", "merge", "merge_shuf_self", "shuffle2",
                           "rot_maxc")},
                "wire2": {k: [] for k in ("solo", "merge", "merge_shuf_self")}}
    rot_sweep_rows = {th: [] for th in thetas}       # wire-1 eval per theta
    c_nat_seed, c_theta_seed = [], {th: [] for th in thetas}
    merge_ce_seed, merge_gh_seed = [], []
    mag_cos_seed = []

    for s in range(args.seeds):
        seed = args.seed + s
        print(f"[pl] ── seed {s}: train wire-1 ──", flush=True)
        fac1 = train_extract(wire1_valid, tp1, seed)
        print(f"[pl] ── seed {s}: train wire-2 ──", flush=True)
        fac2 = train_extract(wire2_valid, tp2, seed + 500)

        # ternary factor deltas (the real artifacts)
        d1, d2 = {}, {}
        b2t, a2t = {}, {}
        for k, (b_, a_, sc) in fac1.items():
            d1[k] = tf.ternarize_factors(b_, a_, sc)[0]
        for k, (b_, a_, sc) in fac2.items():
            dl, bh, ah = tf.ternarize_factors(b_, a_, sc)
            d2[k], b2t[k], a2t[k] = dl, bh, ah
        merge = {k: d1[k] + d2[k] for k in d1}

        # per-wire self-shuffle for G3 (shuffle the RETAINED wire, keep the other)
        rsh1 = np.random.default_rng(2000 + seed)
        rsh2 = np.random.default_rng(3000 + seed)
        d1_shuf = {}
        for k, (b_, a_, sc) in fac1.items():
            _, bh, ah = tf.ternarize_factors(b_, a_, sc)
            d1_shuf[k] = tf.shuffle_factors(bh, ah, sc, rsh1)
        d2_shuf = {k: tf.shuffle_factors(b2t[k], a2t[k], fac2[k][2], rsh2)
                   for k in d2}
        merge_shuf1 = {k: d1_shuf[k] + d2[k] for k in d1}   # wire-1 G3
        merge_shuf2 = {k: d1[k] + d2_shuf[k] for k in d1}   # wire-2 G3

        # wire-1 mass floor: base + D1 + shuffle(D2) at matched norm
        shuffle2 = {k: d1[k] + match_frob(d2_shuf[k], float(np.linalg.norm(d2[k])))
                    for k in d1}

        # collision axis (float A factors); rotate wire-2 A toward wire-1 A
        c_nat_seed.append(band_collision(fac1, fac2))
        rot_deltas = {th: {} for th in thetas}
        for th in thetas:
            cths = []
            for k in d1:
                a1f = fac1[k][1]
                a2f = fac2[k][1]
                a2r = slerp_rotate(a1f, a2f, th)
                cths.append(collision(a1f, a2r))
                b2f, sc2 = fac2[k][0], fac2[k][2]
                draw = (sc2 * (b2f @ a2r)).astype(np.float32)
                d2r = match_frob(draw, float(np.linalg.norm(d2[k])))
                rot_deltas[th][k] = d1[k] + d2r
            c_theta_seed[th].append(float(np.mean(cths)))

        th_max = thetas[int(np.argmax([c_theta_seed[t][-1] for t in thetas]))]

        # magnitude cosine (routing ⊥ magnitude datum, reporting)
        mc = td.plate_stats(
            {k: (fac1[k][2] * (fac1[k][0] @ fac1[k][1])).astype(np.float32)
             for k in fac1}, d1)["mag_cos_pooled"]
        mag_cos_seed.append(float(mc))

        # ── eval arms ──
        acc_rows["wire1"]["solo"].append(eval_arm(d1, eval1))
        acc_rows["wire2"]["solo"].append(eval_arm(d2, eval2))
        acc_rows["wire1"]["merge"].append(eval_arm(merge, eval1))
        acc_rows["wire2"]["merge"].append(eval_arm(merge, eval2))
        acc_rows["wire1"]["merge_shuf_self"].append(eval_arm(merge_shuf1, eval1))
        acc_rows["wire2"]["merge_shuf_self"].append(eval_arm(merge_shuf2, eval2))
        acc_rows["wire1"]["shuffle2"].append(eval_arm(shuffle2, eval1))
        acc_rows["wire1"]["rot_maxc"].append(eval_arm(rot_deltas[th_max], eval1))
        for th in thetas:
            rot_sweep_rows[th].append(eval_arm(rot_deltas[th], eval1))

        apply_plate(merge)
        merge_ce_seed.append(ce_innocents())
        merge_gh_seed.append(gh1())
        restore_plate()

        for w, order in (("wire1", order1), ("wire2", order2)):
            for k in acc_rows[w]:
                a = to_arrays([acc_rows[w][k][-1]], order)
                print(f"    {w}/{k:16s} "
                      + " ".join(f"{sp} {a[sp].mean():.3f}" for sp in SPLITS),
                      flush=True)

    # bit-exact restore check
    max_dev = max(float((getattr(dec[li].mlp, name).weight.detach()
                         - orig_w[(li, name)]).abs().max())
                  for (li, name) in orig_w)
    print(f"[pl] restore check: max|W-W0| = {max_dev:.2e}", flush=True)

    # ── assemble accuracy dict (mean over seeds) ──
    acc = {"wire1": {}, "wire2": {}}
    acc["wire1"]["base"] = to_arrays(base1_seed, order1)
    acc["wire2"]["base"] = to_arrays(base2_seed, order2)
    for k, rows in acc_rows["wire1"].items():
        acc["wire1"][k] = to_arrays(rows, order1)
    for k, rows in acc_rows["wire2"].items():
        acc["wire2"][k] = to_arrays(rows, order2)

    c_nat = float(np.mean(c_nat_seed))
    c_grid = [float(np.mean(c_theta_seed[th])) for th in thetas]
    # sweep degradation per theta: solo_held - rot(theta)_held (per cell, seed-mean)
    solo_held = _held(acc["wire1"]["solo"])
    sweep = {"c": c_grid, "deg": []}
    for th in thetas:
        arr = to_arrays(rot_sweep_rows[th], order1)
        sweep["deg"].append(solo_held - _held(arr))

    ce = {"base": base_ce, "merge": float(np.mean(merge_ce_seed))}
    gh = {"base": base_gh, "merge": tuple(np.mean(merge_gh_seed, axis=0))}

    r = score(gate0_ok, acc, sweep, c_nat, ce, gh,
              np.random.default_rng(args.seed + 999), args.alpha)

    # ── report ──
    print(f"\n[pl] ════ VERDICT: {r['verdict']} ════")
    print(f"  PL1={r['PL1']['ok']} PL2={r['PL2']['PL2']} "
          f"PL3={r['PL3']['PL3']} PL4={r['PL4']['PL4']}")
    print(f"  c_nat={c_nat:.4f}  c_grid={[round(c, 3) for c in c_grid]}")
    print(f"  PL2 corr={r['PL2']['corr']:.3f} p={r['PL2']['p']:.4f} "
          f"within_ci={r['PL2']['within_ci']} nat_deg={r['PL2']['nat_deg']:.3f} "
          f"diff_ci={[round(x, 3) for x in r['PL2']['diff_ci']]}")
    print(f"  PL3 rot_deg={r['PL3']['rot_deg']:.3f} "
          f"shuffle_deg={r['PL3']['shuffle_deg']:.3f} "
          f"nat_deg={r['PL3']['nat_deg']:.3f}")
    print(f"  mag_cos={float(np.mean(mag_cos_seed)):.3f}")
    for w in ("wire1", "wire2"):
        for sp in SPLITS:
            print(f"  {w}/{sp}: base {acc[w]['base'][sp].mean():.3f} "
                  f"solo {acc[w]['solo'][sp].mean():.3f} "
                  f"merge {acc[w]['merge'][sp].mean():.3f} "
                  f"shuf_self {acc[w]['merge_shuf_self'][sp].mean():.3f}")

    def _degate(o):
        if is_dataclass(o) and not isinstance(o, type):
            return asdict(o)
        if isinstance(o, dict):
            return {k: _degate(x) for k, x in o.items()}
        if isinstance(o, (list, tuple)):
            return [_degate(x) for x in o]
        if isinstance(o, np.ndarray):
            return o.tolist()
        return o

    anchor = {w: {k: {sp: float(acc[w][k][sp].mean()) for sp in SPLITS}
                  for k in acc[w]} for w in ("wire1", "wire2")}
    payload = {"model_id": args.model_id, "config": vars(args), "band": band,
               "gate0": {"ok": gate0_ok, "wire1": ns1, "wire2": ns2},
               "collision": {"c_nat": c_nat, "c_grid": c_grid,
                             "thetas": thetas},
               "mag_cos": float(np.mean(mag_cos_seed)),
               "restore_max_dev": max_dev,
               "anchor": anchor, "scoring": r}
    (out_dir / "results.json").write_text(
        json.dumps(_json_safe(_degate(payload)), indent=2))
    print(f"[pl] wrote {out_dir}/results.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-cells", type=int, default=0,
                    help="smoke: cap cells per split per wire (mechanics only)")
    ap.add_argument("--theta-grid", default="0,0.15,0.3,0.5,0.7,0.85,1.0",
                    help="collision-sweep rotation fractions (frozen grid)")
    ap.add_argument("--wire1-record",
                    default="results/writeback-compile/qwen3-4b",
                    help="frozen wire-1 bake record (gate0.json)")
    ap.add_argument("--wire2-record",
                    default="results/plate-linker/wire2-bake/qwen3-4b",
                    help="frozen wire-2 bake record (gate0.json)")
    ap.add_argument("--out", default="results/plate-linker/link/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
