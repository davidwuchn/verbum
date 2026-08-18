#!/usr/bin/env python
"""§P-AMBIGUITY-GATE — Arm B stage 0 of §P-CYCLE-CARRIER (cycle-carrier-signal.md §2b).

Calibration gate: do disambiguated readings (D1, D2) of an ambiguity separate in
any (layer x register) cell? Each pole is a PARAPHRASE POOL (k=6 frames, same
meaning, varied surface — the fixed-point operationalization). Read-only prefill.

FROZEN s337 (Michael GO, pre-data):
  gates    AG0 void (det-repeat + battery integrity: median pole word-length
           delta <= 2.0) | AG1 make-or-break (median per-item pole silhouette,
           MAX-OVER-CELLS permutation null, p<0.05 AND floor >= 0.05) |
           AG2 classifier tier (leave-one-item-out class-axis transfer at the
           AG1 cell, perm p<0.05 -> GENERIC) | AG3 advisory (leave-one-frame-out)
  verdicts SEPARABLE-GENERIC 25 / SEPARABLE-LOCAL 30 (favored) /
           NO-GEOMETRY 25 / CONFOUNDED-STYLE 15 / VOID 5
  tree     VOID -> NO-GEOMETRY -> CONFOUNDED-STYLE -> AG2 split
  confound CONFOUNDED-STYLE fires iff AG1 pass AND anaphora-class median sil at
           the AG1 cell fails its perm null (p>=0.05). The anaphora class is the
           frame/cue-immune canary (frames pole-SHARED by construction): a
           pole-level cue-style component exists only where pole frame sets
           differ (scope/att), so "separates everywhere except the canary" is
           the template-collapse signature. AG3 (frame transfer) is ADVISORY.
  amendments (pre-data, instrument-side, --validate-forced; s322 precedent —
           gates/verdicts/a-priori masses UNCHANGED):
           (1) silhouette excludes self from the own-pole centroid (planted
               NO-GEOMETRY world exposed a +0.42 self-inclusion baseline that
               made the frozen 0.05 floor vacuous);
           (2) CONFOUNDED-STYLE operationalized as the anaphora-canary rule
               above (the draft's extra AG3 conjunct let a pole-level cue-style
               world through: cue axes TRANSFER across frames, so AG3 cannot
               veto them; the canary can);
           (3) canary made RELATIVE + floored (fires iff AG1 pass AND
               ana_median < floor AND gap = median(scope,att) - median(ana)
               beats its perm null p<0.05): the absolute-only ana_p rule was
               fragile to 12-item median luck (planted noise sweep showed
               per-cell class medians scattering to +-0.06).
  bound    D1/D2 cue-word residue is ineliminable at this stage (banked): the
           gate is INSTRUMENT CALIBRATION, not a substrate claim; the collapse
           stage (one bit-identical ambiguous string) kills the residue.
Nothing below is tuned to data.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from combinator_relationship_map import (
    cmr,
    find_gate_modules,
    git_sha,
    log,
    pick_layers,
)

PROBE = "P-AMBIGUITY-GATE"
FROZEN = (
    "s337 pre-data freeze (Michael GO): AG0-AG3, max-over-cells null, "
    "AG1 floor 0.05, verdict tree VOID->NO-GEOMETRY->CONFOUNDED-STYLE->AG2, "
    "masses G25/L30/N25/C15/V5"
)
AG1_FLOOR = 0.05
LEN_TOL_WORDS = 2.0
DET_SIGN_TOL = 0.01
DET_VALUE_TOL = 0.01
ALPHA = 0.05

# ---------------------------------------------------------------------------
# Battery (design-certified grade — semantic construction, marked; s337)
# ---------------------------------------------------------------------------

SCOPE_ITEMS = [
    # (subj, subj_pl, obj, obj_pl, verb_past, verb_pp)
    ("student", "students", "book", "books", "read", "read"),
    ("teacher", "teachers", "poem", "poems", "recited", "recited"),
    ("child", "children", "kite", "kites", "flew", "flown"),
    ("chef", "chefs", "cake", "cakes", "baked", "baked"),
    ("lawyer", "lawyers", "contract", "contracts", "signed", "signed"),
    ("painter", "painters", "portrait", "portraits", "painted", "painted"),
    ("farmer", "farmers", "field", "fields", "plowed", "plowed"),
    ("reporter", "reporters", "article", "articles", "wrote", "written"),
    ("engineer", "engineers", "bridge", "bridges", "designed", "designed"),
    ("gardener", "gardeners", "rose", "roses", "planted", "planted"),
    ("musician", "musicians", "tune", "tunes", "played", "played"),
    ("sailor", "sailors", "knot", "knots", "tied", "tied"),
]
SCOPE_D1 = [  # one particular object for all (exists > forall)
    "There is one particular {obj} that every {subj} {verb_past}.",
    "A single {obj} was {verb_pp} by all of the {subj_pl}.",
    "The same {obj} was {verb_pp} by each of the {subj_pl}.",
    "All of the {subj_pl} {verb_past} one and the same {obj}.",
    "Just one {obj} exists that all the {subj_pl} {verb_past}.",
    "Every one of the {subj_pl} {verb_past} the very same {obj}.",
]
SCOPE_D2 = [  # each their own (forall > exists)
    "Each {subj} {verb_past} a {obj} of their own.",
    "Every {subj} {verb_past} some {obj} or other, not necessarily the same one.",
    "The {subj_pl} each {verb_past} a different {obj}.",
    "For each {subj}, there was some {obj} that they {verb_past}.",
    "Every {subj} {verb_past} their own separate {obj}.",
    "Different {subj_pl} {verb_past} different {obj_pl}.",
]

ANA_ITEMS = [
    # (n1, n2, pred)  — "... that {ref} had {pred}."
    ("John", "Mark", "won the race"),
    ("Sarah", "Emma", "missed the deadline"),
    ("Peter", "James", "broken the window"),
    ("Alice", "Karen", "failed the test"),
    ("David", "Brian", "lost the keys"),
    ("Laura", "Nina", "burned the toast"),
    ("Tom", "Henry", "forgotten the meeting"),
    ("Rachel", "Diana", "crashed the car"),
    ("Kevin", "Frank", "spilled the coffee"),
    ("Megan", "Julia", "found the wallet"),
    ("Oliver", "Simon", "booked the flight"),
    ("Grace", "Helen", "signed the form"),
]
ANA_FRAMES = [  # identical frames across poles; only {ref} differs (n1 vs n2)
    "{n1} told {n2} that {ref} had {pred}.",
    "{n1} said to {n2} that {ref} had {pred}.",
    "While talking to {n2}, {n1} mentioned that {ref} had {pred}.",
    "{n1} informed {n2} that {ref} had {pred}.",
    "In the conversation with {n2}, {n1} claimed that {ref} had {pred}.",
    "{n1} admitted to {n2} that {ref} had {pred}.",
]

ATT_ITEMS = [
    # (agent, person, instr, verb_base, verb_past, verb_pp)
    ("detective", "suspect", "binoculars", "watch", "watched", "watched"),
    ("guard", "visitor", "flashlight", "spot", "spotted", "spotted"),
    ("photographer", "dancer", "camera", "photograph", "photographed", "photographed"),
    ("hunter", "poacher", "telescope", "track", "tracked", "tracked"),
    ("teacher", "student", "ruler", "tap", "tapped", "tapped"),
    ("doctor", "patient", "stethoscope", "examine", "examined", "examined"),
    ("spy", "courier", "monocular", "observe", "observed", "observed"),
    ("ranger", "hiker", "whistle", "signal", "signaled", "signaled"),
    ("coach", "player", "megaphone", "call", "called", "called"),
    ("nurse", "toddler", "thermometer", "check", "checked", "checked"),
    ("clerk", "shopper", "scanner", "scan", "scanned", "scanned"),
    ("fisherman", "swimmer", "spyglass", "sight", "sighted", "sighted"),
]
ATT_D1 = [  # instrumental attachment (agent used instrument)
    "Using the {instr}, the {agent} {verb_past} the {person}.",
    "The {agent} {verb_past} the {person} by means of the {instr}.",
    "With the help of the {instr}, the {agent} {verb_past} the {person}.",
    "The {agent} used the {instr} to {verb_base} the {person}.",
    "It was with the {instr} that the {agent} {verb_past} the {person}.",
    "The {agent}, {instr} in hand, {verb_past} the {person}.",
]
ATT_D2 = [  # NP-modifier attachment (person has instrument)
    "The {agent} {verb_past} the {person} who had the {instr}.",
    "The {agent} {verb_past} the {person} carrying the {instr}.",
    "The {person} with the {instr} was {verb_pp} by the {agent}.",
    "The {agent} {verb_past} the {person} who was holding the {instr}.",
    "The {person} holding the {instr} was the one the {agent} {verb_past}.",
    "The {agent} {verb_past} that {person}, the one with the {instr}.",
]

CLASSES = ("scope", "ana", "att")
N_FRAMES = 6


def _scope_prompt(item, pole: int, f: int) -> str:
    s, spl, o, opl, vp, vpp = item
    frame = (SCOPE_D1 if pole == 0 else SCOPE_D2)[f]
    return frame.format(subj=s, subj_pl=spl, obj=o, obj_pl=opl,
                        verb_past=vp, verb_pp=vpp)


def _ana_prompt(item, pole: int, f: int) -> str:
    n1, n2, pred = item
    ref = n1 if pole == 0 else n2
    return ANA_FRAMES[f].format(n1=n1, n2=n2, ref=ref, pred=pred)


def _att_prompt(item, pole: int, f: int) -> str:
    ag, pe, ins, vb, vp, vpp = item
    frame = (ATT_D1 if pole == 0 else ATT_D2)[f]
    return frame.format(agent=ag, person=pe, instr=ins, verb_base=vb,
                        verb_past=vp, verb_pp=vpp)


def build_battery(smoke: bool = False) -> list[dict]:
    """Records: {idx, id, cls, item, pole, frame, prompt}. pole 0=D1, 1=D2."""
    n_items = 2 if smoke else 12
    gens = {"scope": (_scope_prompt, SCOPE_ITEMS), "ana": (_ana_prompt, ANA_ITEMS),
            "att": (_att_prompt, ATT_ITEMS)}
    recs = []
    for cls in CLASSES:
        fn, items = gens[cls]
        for i in range(n_items):
            for pole in (0, 1):
                for f in range(N_FRAMES):
                    recs.append({
                        "idx": len(recs),
                        "id": f"{cls}-{i:02d}-D{pole + 1}-f{f}",
                        "cls": cls, "item": i, "pole": pole, "frame": f,
                        "prompt": fn(items[i], pole, f),
                    })
    return recs


def battery_stats(recs: list[dict]) -> dict:
    """AG0 battery integrity: per-item pole word-length balance."""
    deltas = []
    keys = sorted({(r["cls"], r["item"]) for r in recs})
    for cls, i in keys:
        w = {0: [], 1: []}
        for r in recs:
            if r["cls"] == cls and r["item"] == i:
                w[r["pole"]].append(len(r["prompt"].split()))
        deltas.append(abs(float(np.mean(w[0])) - float(np.mean(w[1]))))
    return {
        "n_prompts": len(recs),
        "n_items": len(keys),
        "median_pole_len_delta_words": float(np.median(deltas)),
        "max_pole_len_delta_words": float(np.max(deltas)),
        "len_ok": bool(np.median(deltas) <= LEN_TOL_WORDS),
    }


def battery_hash(recs: list[dict]) -> str:
    blob = json.dumps([r["prompt"] for r in recs], sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Analysis (shared by real + planted paths — s331 law)
# ---------------------------------------------------------------------------

def _norm_rows(X: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.maximum(n, 1e-12)


def item_grams(data: dict, recs: list[dict]) -> dict:
    """Per cell, per (cls,item): normalized-row 12x12 Gram + pole labels.

    data: {register: {layer: X (N x d)}} (already CMR'd).
    Returns {cell_key: {(cls,item): (G, labels)}}, cell_key = f"{reg}:L{li}".
    """
    keys = sorted({(r["cls"], r["item"]) for r in recs})
    rows = {k: [r["idx"] for r in recs if (r["cls"], r["item"]) == k] for k in keys}
    labels = {k: np.array([recs[i]["pole"] for i in rows[k]]) for k in keys}
    out = {}
    for reg, by_layer in data.items():
        for li, X in by_layer.items():
            cell = f"{reg}:L{li}"
            Xn = _norm_rows(X.astype(np.float64))
            out[cell] = {k: (Xn[rows[k]] @ Xn[rows[k]].T, labels[k]) for k in keys}
    return out


def sil_from_gram(G: np.ndarray, labels: np.ndarray) -> float:
    """Two-pool silhouette from a normalized-row Gram.

    Own-pole centroid EXCLUDES self (amendment 1: self-inclusion put a +0.42
    baseline under pure noise, voiding the frozen floor)."""
    vals = []
    for i in range(len(labels)):
        own = (labels == labels[i]).copy()
        own[i] = False
        oth = labels != labels[i]
        s_own = G[i, own].sum() / max(np.sqrt(G[np.ix_(own, own)].sum()), 1e-12)
        s_oth = G[i, oth].sum() / max(np.sqrt(G[np.ix_(oth, oth)].sum()), 1e-12)
        vals.append(s_own - s_oth)
    return float(np.mean(vals))


def ag1_max_null(grams: dict, recs: list[dict], n_perm: int, seed: int) -> dict:
    """AG1: max-over-cells median item silhouette vs max-statistic perm null.

    Same per-item permutation reused across cells within a draw (frozen).
    Also returns the anaphora-class null at the best cell (CONFOUNDED input).
    """
    rng = np.random.default_rng(seed)
    cells = sorted(grams.keys())
    keys = sorted(next(iter(grams.values())).keys())
    ana_keys = [k for k in keys if k[0] == "ana"]

    obs_med = {}
    obs_item = {}
    for c in cells:
        sils = {k: sil_from_gram(*grams[c][k]) for k in keys}
        obs_item[c] = sils
        obs_med[c] = float(np.median(list(sils.values())))
    best_cell = max(obs_med, key=obs_med.get)
    obs_max = obs_med[best_cell]
    non_ana = [k for k in keys if k[0] != "ana"]
    obs_ana = (float(np.median([obs_item[best_cell][k] for k in ana_keys]))
               if ana_keys else 0.0)
    obs_gap = (float(np.median([obs_item[best_cell][k] for k in non_ana]) - obs_ana)
               if ana_keys else 0.0)

    null_max = np.empty(n_perm)
    null_gap = np.empty(n_perm)
    for p in range(n_perm):
        perms = {k: rng.permutation(len(grams[cells[0]][k][1])) for k in keys}
        meds = {}
        for c in cells:
            sils = {k: sil_from_gram(grams[c][k][0], grams[c][k][1][perms[k]])
                    for k in keys}
            meds[c] = np.median(list(sils.values()))
            if c == best_cell and ana_keys:
                null_gap[p] = (np.median([sils[k] for k in non_ana])
                               - np.median([sils[k] for k in ana_keys]))
        null_max[p] = max(meds.values())
    p_max = float(np.mean(null_max >= obs_max))
    p_gap = float(np.mean(null_gap >= obs_gap)) if ana_keys else 1.0
    return {
        "best_cell": best_cell, "obs_max_median_sil": obs_max, "p": p_max,
        "floor": AG1_FLOOR, "pass": bool(p_max < ALPHA and obs_max >= AG1_FLOOR),
        "per_cell_median": obs_med, "per_item_best_cell": {
            f"{k[0]}-{k[1]:02d}": v for k, v in obs_item[best_cell].items()},
        "ana_median_best_cell": obs_ana, "canary_gap": obs_gap, "gap_p": p_gap,
        "null_max_q95": float(np.quantile(null_max, 0.95)),
    }


def _cell_matrix(data: dict, cell: str) -> np.ndarray:
    reg, ls = cell.split(":L")
    return data[reg][int(ls)].astype(np.float64)


def _pole_axis(X: np.ndarray, labels: np.ndarray) -> np.ndarray:
    return X[labels == 0].mean(axis=0) - X[labels == 1].mean(axis=0)


def _loio_acc(X_items: list[np.ndarray], lab_items: list[np.ndarray]) -> float:
    """Leave-one-item-out pole classification (median-centered sign rule)."""
    axes = [_pole_axis(X, lab) for X, lab in zip(X_items, lab_items, strict=True)]
    total, correct = 0, 0
    n = len(X_items)
    for i in range(n):
        axis = np.mean([axes[j] for j in range(n) if j != i], axis=0)
        proj = X_items[i] @ axis
        pred = (proj - np.median(proj) < 0).astype(int)  # D1 projects positive
        correct += int((pred == lab_items[i]).sum())
        total += len(lab_items[i])
    return correct / max(total, 1)


def ag2_loio(data: dict, recs: list[dict], cell: str, n_perm: int, seed: int) -> dict:
    """AG2 at the AG1 cell: LOIO class-axis transfer, perm null on accuracy."""
    rng = np.random.default_rng(seed + 1)
    X = _cell_matrix(data, cell)
    per_class = {}
    accs_obs = []
    null = np.zeros(n_perm)
    for cls in CLASSES:
        keys = sorted({r["item"] for r in recs if r["cls"] == cls})
        rows = {i: [r["idx"] for r in recs if r["cls"] == cls and r["item"] == i]
                for i in keys}
        Xi = [X[rows[i]] for i in keys]
        Li = [np.array([recs[j]["pole"] for j in rows[i]]) for i in keys]
        acc = _loio_acc(Xi, Li)
        per_class[cls] = acc
        accs_obs.append(acc)
        for p in range(n_perm):
            Lp = [rng.permutation(lab) for lab in Li]
            null[p] += _loio_acc(Xi, Lp)
    obs = float(np.mean(accs_obs))
    null /= len(CLASSES)
    pv = float(np.mean(null >= obs))
    return {"cell": cell, "acc": obs, "per_class": per_class, "p": pv,
            "generic": bool(pv < ALPHA and obs > 0.5)}


def ag3_lofo(data: dict, recs: list[dict], cell: str, n_perm: int, seed: int) -> dict:
    """AG3 advisory at the AG1 cell: leave-one-frame-out transfer."""
    rng = np.random.default_rng(seed + 2)
    X = _cell_matrix(data, cell)

    def lofo_acc(labels_by_idx: dict[int, int]) -> float:
        total, correct = 0, 0
        for cls in CLASSES:
            crecs = [r for r in recs if r["cls"] == cls]
            for f in range(N_FRAMES):
                train = [r["idx"] for r in crecs if r["frame"] != f]
                test = [r["idx"] for r in crecs if r["frame"] == f]
                lt = np.array([labels_by_idx[i] for i in train])
                axis = _pole_axis(X[train], lt)
                proj = X[test] @ axis
                pred = (proj - np.median(proj) < 0).astype(int)
                lab = np.array([labels_by_idx[i] for i in test])
                correct += int((pred == lab).sum())
                total += len(test)
        return correct / max(total, 1)

    true_lab = {r["idx"]: r["pole"] for r in recs}
    obs = lofo_acc(true_lab)
    null = np.empty(n_perm)
    keys = sorted({(r["cls"], r["item"]) for r in recs})
    rows = {k: [r["idx"] for r in recs if (r["cls"], r["item"]) == k] for k in keys}
    for p in range(n_perm):
        lab = dict(true_lab)
        for k in keys:
            idxs = rows[k]
            vals = [true_lab[i] for i in idxs]
            for i, v in zip(idxs, rng.permutation(vals), strict=True):
                lab[i] = int(v)
        null[p] = lofo_acc(lab)
    pv = float(np.mean(null >= obs))
    return {"cell": cell, "acc": obs, "p": pv, "pass": bool(pv < ALPHA and obs > 0.5)}


def decide(g: dict) -> str:
    if not g["ag0"]["pass"]:
        return "VOID"
    if not g["ag1"]["pass"]:
        return "NO-GEOMETRY"
    if g["confounded_style"]["fires"]:
        return "CONFOUNDED-STYLE"
    return "SEPARABLE-GENERIC" if g["ag2"]["generic"] else "SEPARABLE-LOCAL"


def analyze(data: dict, recs: list[dict], n_perm: int, seed: int,
            det: dict | None) -> dict:
    """Full frozen gate tree. data = {register: {layer: X}} (CMR'd)."""
    bstats = battery_stats(recs)
    det = det or {"sign_flip_frac": 0.0, "value_rel_dev": 0.0, "planted": True}
    ag0 = {
        **bstats, **det,
        "det_ok": bool(det["sign_flip_frac"] < DET_SIGN_TOL
                       and det["value_rel_dev"] < DET_VALUE_TOL),
    }
    ag0["pass"] = bool(ag0["len_ok"] and ag0["det_ok"])

    grams = item_grams(data, recs)
    ag1 = ag1_max_null(grams, recs, n_perm=n_perm, seed=seed)
    cell = ag1["best_cell"]
    ag2 = ag2_loio(data, recs, cell, n_perm=max(200, n_perm // 5), seed=seed)
    ag3 = ag3_lofo(data, recs, cell, n_perm=200, seed=seed)
    conf = {"ana_median": ag1["ana_median_best_cell"], "canary_gap": ag1["canary_gap"],
            "gap_p": ag1["gap_p"], "ag3_pass": ag3["pass"],
            "fires": bool(ag1["pass"]
                          and ag1["ana_median_best_cell"] < AG1_FLOOR
                          and ag1["gap_p"] < ALPHA)}
    g = {"ag0": ag0, "ag1": ag1, "ag2": ag2, "ag3": ag3, "confounded_style": conf}
    g["verdict"] = decide(g)
    return g


# ---------------------------------------------------------------------------
# Planted worlds (--validate; real battery + real analysis path — s331 law)
# ---------------------------------------------------------------------------

PLANT_D = 96
PLANT_LAYERS = list(range(6))
PLANT_CELL = ("route", 3)
PLANT_S = 4.0


def _plant(world: str, seed: int) -> tuple[dict, list[dict]]:
    rng = np.random.default_rng(seed)
    recs = build_battery(smoke=False)
    n = len(recs)

    def u() -> np.ndarray:
        v = rng.normal(size=PLANT_D)
        return v / np.linalg.norm(v)

    axes_cls = {c: u() for c in CLASSES}
    axes_item = {(r["cls"], r["item"]): None for r in recs}
    axes_item = {k: u() for k in axes_item}
    axes_pole_style = {(c, pole): u() for c in ("scope", "att") for pole in (0, 1)}
    axes_frame_shared = {(c, f): u() for c in CLASSES for f in range(N_FRAMES)}

    data = {reg: {li: rng.normal(size=(n, PLANT_D)) for li in PLANT_LAYERS}
            for reg in ("route", "value")}
    reg, li = PLANT_CELL
    X = data[reg][li]
    for r in recs:
        sgn = 1.0 if r["pole"] == 0 else -1.0
        if world == "generic":
            X[r["idx"]] += PLANT_S * sgn * axes_cls[r["cls"]]
        elif world == "local":
            X[r["idx"]] += PLANT_S * sgn * axes_item[(r["cls"], r["item"])]
        elif world == "style":
            # cue-style world: pole-level style axes exist only where pole frame
            # sets differ (scope/att); the anaphora canary (pole-shared frames)
            # carries frame style but NO pole-separating component
            if r["cls"] == "ana":
                X[r["idx"]] += PLANT_S * axes_frame_shared[(r["cls"], r["frame"])]
            else:
                X[r["idx"]] += PLANT_S * axes_pole_style[(r["cls"], r["pole"])]
        elif world == "nogeom":
            pass
        else:
            raise ValueError(world)
    data = {reg: {li: cmr(M) for li, M in by.items()} for reg, by in data.items()}
    return data, recs


def run_validate(n_perm: int, seed: int) -> int:
    want = {
        "generic": "SEPARABLE-GENERIC",
        "local": "SEPARABLE-LOCAL",
        "nogeom": "NO-GEOMETRY",
        "style": "CONFOUNDED-STYLE",
    }
    recs = build_battery(smoke=False)
    bs = battery_stats(recs)
    log(f"[ag] battery: {bs['n_prompts']} prompts / {bs['n_items']} items | "
        f"median pole len delta {bs['median_pole_len_delta_words']:.2f} words "
        f"(tol {LEN_TOL_WORDS}) {'OK' if bs['len_ok'] else 'FAIL'}")
    ok = bs["len_ok"]
    for world, expect in want.items():
        data, recs = _plant(world, seed=42)
        g = analyze(data, recs, n_perm=n_perm, seed=seed, det=None)
        hit = g["verdict"] == expect
        ok &= hit
        log(f"[ag] world={world!r}: verdict={g['verdict']} (want {expect}) "
            f"{'OK' if hit else 'FAIL'} | AG1 {g['ag1']['obs_max_median_sil']:.3f} "
            f"p={g['ag1']['p']:.3f} cell={g['ag1']['best_cell']} | "
            f"AG2 acc={g['ag2']['acc']:.3f} p={g['ag2']['p']:.3f} | "
            f"AG3 acc={g['ag3']['acc']:.3f} p={g['ag3']['p']:.3f} | "
            f"ana_med={g['ag1']['ana_median_best_cell']:.3f} "
            f"gap_p={g['ag1']['gap_p']:.3f}")
    log(f"[ag] {'ALL PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Real collection (both registers, per-layer, last token)
# ---------------------------------------------------------------------------

def collect_both(model, tokenizer, device, prompts, max_length, want_layers):
    """Returns (gate {li: (N,d_ff)}, hid {li: (N,d_model)}, plen (N,))."""
    import torch

    gate_mods = find_gate_modules(model)
    n_layers = len(gate_mods)
    want = set(want_layers)
    buf: dict[int, np.ndarray] = {}

    def mk_hook(li):
        def hook(_m, _inp, out):
            buf[li] = out[0, -1].detach().float().cpu().numpy().astype(np.float32)
        return hook

    handles = [mod.register_forward_hook(mk_hook(li))
               for (li, _nm, mod) in gate_mods if li in want]
    gate = {li: [] for li in want_layers}
    hid = {li: [] for li in want_layers}
    plen = []
    try:
        with torch.no_grad():
            for i, p in enumerate(prompts):
                enc = tokenizer(p, return_tensors="pt", truncation=True,
                                max_length=max_length).to(device)
                out = model(**enc, output_hidden_states=True)
                for li in want_layers:
                    gate[li].append(buf[li])
                    h = out.hidden_states[li + 1][0, -1]
                    hid[li].append(h.detach().float().cpu().numpy().astype(np.float32))
                plen.append(int(enc["input_ids"].shape[1]))
                if (i + 1) % 50 == 0:
                    log(f"[ag] collected {i + 1}/{len(prompts)}")
    finally:
        for hd in handles:
            hd.remove()
    return ({li: np.stack(v) for li, v in gate.items()},
            {li: np.stack(v) for li, v in hid.items()},
            np.array(plen, dtype=np.int32), n_layers)


def _json_native(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


def run_real(args) -> int:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    recs = build_battery(smoke=args.smoke)
    prompts = [r["prompt"] for r in recs]
    out = Path(args.out or f"results/p_ambiguity_gate_s337/"
                           f"{'smoke_4b' if args.smoke else 'run_14b'}")
    out.mkdir(parents=True, exist_ok=True)

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    log(f"[ag] loading {args.model_id} ({args.dtype}, {args.device})")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(args.model_id, torch_dtype=dtype)
    model.to(args.device).eval()

    n_layers_probe = len(find_gate_modules(model))
    want_layers = pick_layers(n_layers_probe)
    log(f"[ag] {n_layers_probe} layers -> capture {want_layers}")

    # det-repeat: first prompt appended again; compared then dropped
    gate, hid, plen, _ = collect_both(model, tok, args.device,
                                      [*prompts, prompts[0]], args.max_length,
                                      want_layers)
    flips, rdevs = [], []
    for li in want_layers:
        a, b = np.sign(gate[li][0]), np.sign(gate[li][-1])
        flips.append(float(np.mean(a != b)))
        ha, hb = hid[li][0], hid[li][-1]
        rdevs.append(float(np.linalg.norm(ha - hb) / max(np.linalg.norm(ha), 1e-9)))
        gate[li], hid[li] = gate[li][:-1], hid[li][:-1]
    plen = plen[:-1]
    det = {"sign_flip_frac": float(np.max(flips)),
           "value_rel_dev": float(np.max(rdevs)), "planted": False}
    log(f"[ag] det-repeat: sign_flip {det['sign_flip_frac']:.4f} "
        f"value_rel {det['value_rel_dev']:.4f}")

    data = {
        "route": {li: cmr(np.sign(gate[li]).astype(np.float64)) for li in want_layers},
        "value": {li: cmr(hid[li].astype(np.float64)) for li in want_layers},
    }
    if args.device == "mps":
        del model
        gc.collect()
        torch.mps.empty_cache()

    g = analyze(data, recs, n_perm=args.n_perm, seed=args.seed, det=det)
    log(f"[ag] VERDICT: {g['verdict']} | AG1 {g['ag1']['obs_max_median_sil']:.4f} "
        f"p={g['ag1']['p']:.4f} cell={g['ag1']['best_cell']} | "
        f"AG2 acc={g['ag2']['acc']:.3f} p={g['ag2']['p']:.4f} | "
        f"ana_med={g['ag1']['ana_median_best_cell']:.3f} "
        f"gap_p={g['ag1']['gap_p']:.3f}")

    with (out / "results.jsonl").open("w") as fh:
        for r, pl in zip(recs, plen, strict=True):
            fh.write(json.dumps({**r, "plen": int(pl)}, default=_json_native) + "\n")
    (out / "gates.json").write_text(json.dumps(g, indent=2, default=_json_native))
    np.savez_compressed(out / "route_signs.npz",
                        **{f"L{li}": np.sign(gate[li]).astype(np.int8)
                           for li in want_layers})
    np.savez_compressed(out / "value_hidden.npz",
                        **{f"L{li}": hid[li].astype(np.float16) for li in want_layers})
    meta = {
        "run_id": out.name, "probe": PROBE, "frozen": FROZEN,
        "pre_data_instantiations": {
            "ag1_floor": AG1_FLOOR, "alpha": ALPHA, "len_tol_words": LEN_TOL_WORDS,
            "det_tols": [DET_SIGN_TOL, DET_VALUE_TOL], "n_perm": args.n_perm,
            "masses": {"SEPARABLE-GENERIC": 25, "SEPARABLE-LOCAL": 30,
                       "NO-GEOMETRY": 25, "CONFOUNDED-STYLE": 15, "VOID": 5},
        },
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "model_id": args.model_id, "device": args.device, "dtype": args.dtype,
        "seed": args.seed, "smoke": bool(args.smoke),
        "n_variants": len(recs), "battery_hash": battery_hash(recs),
        "git_sha": git_sha(), "python": platform.python_version(),
        "platform": platform.platform(),
        "lib_versions": {"torch": torch.__version__,
                         "numpy": np.__version__},
        "gates": g,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))
    log(f"[ag] wrote {out}/")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--max-length", type=int, default=64)
    ap.add_argument("--out", default=None)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.validate:
        return run_validate(n_perm=min(args.n_perm, 300), seed=args.seed)
    return run_real(args)


if __name__ == "__main__":
    raise SystemExit(main())
