#!/usr/bin/env python3
# register: topological/routing
"""§P-CL-COLLAPSE — do CL identities hold as routing-register geometry?

FROZEN spec: mementum/knowledge/explore/combinator-function-shape.md §P-CL-COLLAPSE
(Michael GO s321). The compositionality probe (open S5 cell).

THE CRUX (extensional vs operational routing):
  The CL identity  I = SKK  says the compound `S K K` IS the identity function.
  Does `SKK` ROUTE like `I`? The kernel certifies the tension: `S K K x -> x`
  BY FIRING [S, K] — `I` never fires. Two opposing priors:
    EXTENSIONAL  — routing sees the FUNCTION (normal form): SKK routes like I.
    OPERATIONAL  — routing tracks the REDUCTION (fired opcodes): SKK routes like
                   {S,K}, never I. FAVORED (head-combinator-isa + s317 tape-resident).

CONSTRUCTION — normal-form collapse: kernel-certified compound spellings that
share ONLY their normal form; head symbol + fired-opcodes VARY (the dissociation).

REGISTER: routing = sign(mlp.gate_proj pre-activation) at last token, common-mode
removed over the pooled probe set. The only register where combinator identity is
measurable (s217: route_cmr z=7.97 p=0.001; raw hidden z=-1.65 null).

BUILD AMENDMENT (s321, runtime-forced, pre-run, instrument-side ONLY — register /
gates / verdicts / a-priori UNCHANGED): the frozen spec named crystal_probes() as
the primitive anchors, but crystal primitive probes are ~entirely NATURAL LANGUAGE
("The cat cleaned itself" = I) whereas compounds are terse SYMBOLIC strings
("S K K x"). Comparing them confounds STYLE with FUNCTION — an asymmetric confound
that makes the favored OPERATIONAL verdict artificially easy (false-negative risk
on the surprising-positive EXTENSIONAL). FIX: STYLE-MATCHED symbolic saturated
primitive anchors (same style as compounds), kernel-certified. CL5 void-gate is
measured on these anchors IN the alignment pool (the pool that matters); the s217
crystal 9-way z=7.97 stands as the external register-forms reference.

Usage:
  uv run python scripts/experiments/cl_collapse.py --validate         # planted worlds
  uv run python scripts/experiments/cl_collapse.py --model Qwen/Qwen3-4B --smoke
  uv run python scripts/experiments/cl_collapse.py --model Qwen/Qwen3-14B \
      --out results/cl-collapse/qwen3-14b

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

# reuse the s217 routing machinery verbatim (lambda one_way)
from combinator_relationship_map import (  # noqa: E402
    cmr,
    collect,
    find_gate_modules,
    git_sha,
    pick_layers,
    unit,
)

from verbum.lambda_ast import fired_sequence, normal_form, parse, pretty  # noqa: E402

RESULTS_DIR = _PROJECT_ROOT / "results" / "cl-collapse"

# ---------------------------------------------------------------------------- #
# probe construction — kernel-certified                                        #
# ---------------------------------------------------------------------------- #
# style-matched symbolic saturated anchors (one combinator, fully applied)
ANCHOR_TEMPLATES: dict[str, str] = {
    "I": "I {0}",
    "K": "K {0} {1}",
    "W": "W {0} {1}",
    "C": "C {0} {1} {2}",
    "B": "B {0} {1} {2}",
    "S": "S {0} {1} {2}",
    "D": "D {0} {1} {2} {3}",
}
ANCHOR_ORDER = ["I", "K", "W", "C", "B", "S", "D"]

# normal-form collapse sets: spellings that reduce to the SAME normal form.
# each entry: template (with atom slots {0..}), verified this session by the kernel.
COLLAPSE: dict[str, list[str]] = {
    # identity applied to 1 atom -> that atom. heads {S,W,C,K}, fired-sets vary.
    "I": [
        "S K K {0}",
        "S K S {0}",
        "W K {0}",
        "C K K {0}",
        "K I I {0}",
        "S (K I) I {0}",
    ],
    # duplicator applied to f,x -> f x x. heads {S,C}.
    "W": [
        "S S (K I) {0} {1}",
        "C S I {0} {1}",
    ],
    # compositor applied to f,g,x -> f (g x). heads {S,B}.
    "B": [
        "S (K S) K {0} {1} {2}",
        "B I B {0} {1} {2}",
    ],
}
# arity (n atom slots) per normal-form target — how many atoms saturate it.
TARGET_ARITY = {"I": 1, "W": 2, "B": 3}

# token-matched distractors: same {S,K,C} alphabet, VARIED (non-collapse) NF.
# these carry the shared 'K' token but do NOT reduce to a single fixed function —
# the CL2 null that kills the "spellings cohere because they share K" confound.
DISTRACTORS: list[str] = [
    "K S {0} {1}",
    "S K {0} {1}",
    "K K {0} {1}",
    "C K {0} {1}",
    "K {0} {1}",
]

# lowercase atoms (all parse as atoms; combinators are uppercase). visually clean.
ATOMS = list("abcdefghmnpqrtuvxz")

_COMB_SET = set("SKIBCWDYM")


def _alphabet(text: str) -> set[str]:
    toks = text.replace("(", " ").replace(")", " ").split()
    return {t for t in toks if t in _COMB_SET}


def _head(text: str) -> str:
    for t in text.replace("(", " ").replace(")", " ").split():
        if t in _COMB_SET:
            return t
    return ""


def _atom_tuples(n_slots: int, n: int, seed: int) -> list[tuple[str, ...]]:
    """n distinct tuples of DISTINCT atoms for n_slots argument positions."""
    rng = np.random.default_rng(seed)
    seen: set[tuple[str, ...]] = set()
    out: list[tuple[str, ...]] = []
    tries = 0
    while len(out) < n and tries < n * 50:
        tries += 1
        pick = tuple(rng.choice(ATOMS, size=n_slots, replace=False))
        if pick not in seen:
            seen.add(pick)
            out.append(pick)
    return out


def _reduce_str(text: str) -> str:
    return pretty(normal_form(parse(text)))


def build_probes(n_per: int, seed: int) -> list[dict]:
    """Kernel-certified probe pool: anchors + collapse compounds + distractors.

    Every collapse compound is certified: reduce(compound) == reduce(anchor(nf))
    on the SAME atoms (the CL identity, proven per-instance). Returns metadata
    dicts; group = centroid grouping key; kind in {anchor,collapse,distractor}.
    """
    probes: list[dict] = []
    sd = seed

    # anchors (style-matched symbolic saturated)
    for prim in ANCHOR_ORDER:
        tmpl = ANCHOR_TEMPLATES[prim]
        n_slots = tmpl.count("{")
        for atoms in _atom_tuples(n_slots, n_per, sd):
            sd += 1
            text = tmpl.format(*atoms)
            probes.append({
                "text": text, "kind": "anchor", "group": f"A:{prim}",
                "prim": prim, "nf": None, "fired": [], "head": prim,
            })

    # collapse compounds — certified extensional equality to their NF-primitive
    for target, spellings in COLLAPSE.items():
        ar = TARGET_ARITY[target]
        anch_tmpl = ANCHOR_TEMPLATES[target]
        for si, tmpl in enumerate(spellings):
            n_slots = tmpl.count("{")
            assert n_slots == ar, f"{tmpl}: {n_slots} slots != target arity {ar}"
            fired = sorted(set(fired_sequence(parse(tmpl.format(*ATOMS[:n_slots])))))
            head = _head(tmpl)
            gid = f"C:{target}:{si}"
            for atoms in _atom_tuples(n_slots, n_per, sd):
                sd += 1
                text = tmpl.format(*atoms)
                # CERTIFY: compound and its NF-primitive reduce identically
                got = _reduce_str(text)
                want = _reduce_str(anch_tmpl.format(*atoms))
                assert got == want, f"NOT extensional: {text}->{got} != {target}->{want}"  # noqa: E501
                probes.append({
                    "text": text, "kind": "collapse", "group": gid,
                    "prim": None, "nf": target, "fired": fired, "head": head,
                })

    # distractors — same alphabet, varied NF (the CL2 token-matched null pool)
    for di, tmpl in enumerate(DISTRACTORS):
        n_slots = tmpl.count("{")
        gid = f"D:{di}"
        for atoms in _atom_tuples(n_slots, n_per, sd):
            sd += 1
            text = tmpl.format(*atoms)
            probes.append({
                "text": text, "kind": "distractor", "group": gid,
                "prim": None, "nf": None, "fired": [], "head": _head(tmpl),
                "reduces_to": _reduce_str(text),
            })
    # sanity: distractors carry K but are NOT all the target NFs
    dgroups = {p["group"] for p in probes if p["kind"] == "distractor"}
    assert dgroups, "no distractors built"
    return probes


# ---------------------------------------------------------------------------- #
# geometry                                                                      #
# ---------------------------------------------------------------------------- #
def group_centroids(X: np.ndarray, groups: list[str]) -> dict[str, np.ndarray]:
    """Mean vector per group id (raw, not unit-normalized)."""
    out: dict[str, np.ndarray] = {}
    g = np.array(groups)
    for gid in sorted(set(groups)):
        out[gid] = X[g == gid].mean(axis=0)
    return out


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(unit(a), unit(b)))


def _silhouette(X: np.ndarray, labels: np.ndarray) -> float:
    """Generic silhouette over ARBITRARY label sets (the imported one is locked to
    the 9-CRYSTAL order → nan on a subset). Mean over probes of
    [cos(x, own centroid) - max_other cos(x, centroid)]."""
    order = sorted(set(labels.tolist()))
    if len(order) < 2:
        return float("nan")
    idx = {c: i for i, c in enumerate(order)}
    cents = np.array([X[labels == c].mean(axis=0) for c in order])
    U = np.array([unit(c) for c in cents])
    Xu = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)
    sims = Xu @ U.T
    li = np.array([idx[c] for c in labels])
    own = sims[np.arange(len(labels)), li]
    other = sims.copy()
    other[np.arange(len(labels)), li] = -np.inf
    return float(np.mean(own - other.max(axis=1)))


def _sil_null(X: np.ndarray, labels: np.ndarray, n_perm: int, seed: int) -> dict:
    obs = _silhouette(X, labels)
    rng = np.random.default_rng(seed)
    null = np.array([_silhouette(X, rng.permutation(labels)) for _ in range(n_perm)])
    sd = null.std() + 1e-30
    return {"silhouette": obs, "null_mean": float(null.mean()),
            "null_std": float(null.std()),
            "z": float((obs - null.mean()) / sd),
            "p_value": float((np.sum(null >= obs) + 1) / (n_perm + 1))}


def _fired_mix(fired: list[str], anch: dict[str, np.ndarray]) -> np.ndarray | None:
    dirs = [unit(anch[f]) for f in fired if f in anch]
    if not dirs:
        return None
    return np.mean(dirs, axis=0)


def alignments(X: np.ndarray, probes: list[dict]) -> dict:
    """Per-spelling nf/op/head/token alignments in the (CMR'd sign) register X."""
    cents = group_centroids(X, [p["group"] for p in probes])
    anch = {prim: cents[f"A:{prim}"] for prim in ANCHOR_ORDER if f"A:{prim}" in cents}

    # per-target shared token (present in EVERY spelling's alphabet), if any
    shared_tok: dict[str, str] = {}
    for target, spellings in COLLAPSE.items():
        inter: set[str] | None = None
        for tmpl in spellings:
            a = _alphabet(tmpl)
            inter = a if inter is None else (inter & a)
        inter = inter or set()
        # prefer a shared token that is NOT the nf-primitive itself
        cands = [t for t in inter if t in anch and t != target]
        if cands:
            shared_tok[target] = sorted(cands)[0]

    rows = []
    spell_meta = {p["group"]: p for p in probes if p["kind"] == "collapse"}
    for gid, meta in spell_meta.items():
        c = cents[gid]
        target = meta["nf"]
        nf_a = _cos(c, anch[target]) if target in anch else float("nan")
        fm = _fired_mix(meta["fired"], anch)
        op_a = _cos(c, fm) if fm is not None else float("nan")
        hd_a = _cos(c, anch[meta["head"]]) if meta["head"] in anch else float("nan")
        tok = shared_tok.get(target)
        tok_a = _cos(c, anch[tok]) if tok else float("nan")
        rows.append({"group": gid, "target": target, "head": meta["head"],
                     "fired": meta["fired"], "nf_align": nf_a, "op_align": op_a,
                     "head_align": hd_a, "shared_tok": tok, "tok_align": tok_a})
    return {"rows": rows, "anch_prims": sorted(anch.keys()), "shared_tok": shared_tok}


def within_coherence(X: np.ndarray, probes: list[dict], target: str) -> float:
    """Mean pairwise cosine of per-spelling centroids within one NF target."""
    cents = group_centroids(X, [p["group"] for p in probes])
    gids = sorted({p["group"] for p in probes
                   if p["kind"] == "collapse" and p["nf"] == target})
    if len(gids) < 2:
        return float("nan")
    us = [unit(cents[g]) for g in gids]
    sims = [float(np.dot(us[i], us[j]))
            for i in range(len(us)) for j in range(i + 1, len(us))]
    return float(np.mean(sims))


def cl2_null(X: np.ndarray, probes: list[dict], obs: float,
             n_perm: int, seed: int) -> dict:
    """Token-matched null: coherence of random groups of same-alphabet, varied-NF
    distractor terms. If NF groups cohere MORE, coherence is NF- not token-driven."""
    cents = group_centroids(X, [p["group"] for p in probes])
    dgids = sorted({p["group"] for p in probes if p["kind"] == "distractor"})
    if len(dgids) < 2:
        return {"obs": obs, "null_mean": float("nan"), "p_value": float("nan")}
    us = {g: unit(cents[g]) for g in dgids}
    rng = np.random.default_rng(seed)
    # group size = mean collapse-target size (>=2)
    sizes = [len([g for g in {p["group"] for p in probes
                              if p["kind"] == "collapse" and p["nf"] == t}])
             for t in COLLAPSE]
    gsize = max(2, round(float(np.mean([s for s in sizes if s >= 2]))))
    null = np.empty(n_perm)
    for i in range(n_perm):
        pick = rng.choice(dgids, size=min(gsize, len(dgids)), replace=False)
        vs = [us[g] for g in pick]
        sims = [float(np.dot(vs[a], vs[b]))
                for a in range(len(vs)) for b in range(a + 1, len(vs))]
        null[i] = np.mean(sims) if sims else 0.0
    return {"obs": obs, "null_mean": float(null.mean()),
            "null_std": float(null.std()),
            "p_value": float((np.sum(null >= obs) + 1) / (n_perm + 1))}


def cl1_shuffle_null(rows: list[dict], anch_prims: list[str],
                     cents_unit: dict[str, np.ndarray],
                     spell_unit: dict[str, np.ndarray],
                     obs_nf: float, n_perm: int, seed: int) -> dict:
    """Shuffled-label null: permute which anchor is each spelling's 'nf', recompute
    mean nf_align. obs must beat it (nf-alignment is not generic anchor-proximity)."""
    rng = np.random.default_rng(seed)
    gids = [r["group"] for r in rows]
    prims = list(anch_prims)
    null = np.empty(n_perm)
    for i in range(n_perm):
        assign = rng.choice(prims, size=len(gids), replace=True)
        vals = [float(np.dot(spell_unit[g], cents_unit[p]))
                for g, p in zip(gids, assign, strict=False)]
        null[i] = np.mean(vals)
    return {"obs": obs_nf, "null_mean": float(null.mean()),
            "null_std": float(null.std()),
            "p_value": float((np.sum(null >= obs_nf) + 1) / (n_perm + 1))}


# ---------------------------------------------------------------------------- #
# analysis (pure — shared by run and --validate)                               #
# ---------------------------------------------------------------------------- #
def analyze(gate: dict[int, np.ndarray], probes: list[dict], want_layers: list[int],
            n_layers: int, n_perm: int, seed: int) -> dict:
    labels_prim = np.array(
        [p["prim"] if p["kind"] == "anchor" else "?" for p in probes])
    anchor_mask = labels_prim != "?"

    per_layer: dict[str, dict] = {}
    for li in want_layers:
        sign = np.sign(gate[li])
        signc = cmr(sign)
        # CL5: symbolic-anchor silhouette in the alignment pool (void-gate)
        sil = _sil_null(signc[anchor_mask], labels_prim[anchor_mask],
                        n_perm=min(n_perm, 500), seed=seed)
        al = alignments(signc, probes)
        rows = al["rows"]
        nf = float(np.nanmean([r["nf_align"] for r in rows]))
        op = float(np.nanmean([r["op_align"] for r in rows]))
        hd = float(np.nanmean([r["head_align"] for r in rows]))
        tok = float(np.nanmean([r["tok_align"] for r in rows]))
        per_layer[str(li)] = {
            "frac": round(li / max(n_layers - 1, 1), 3),
            "anchor_silhouette": sil,
            "nf_align": nf, "op_align": op, "head_align": hd, "tok_align": tok,
            "delta_nf_op": nf - op, "rows": rows, "shared_tok": al["shared_tok"],
            "anch_prims": al["anch_prims"],
        }

    # best layer = strongest anchor separability (register-forms best)
    best_li = max(want_layers,
                  key=lambda li: per_layer[str(li)]["anchor_silhouette"]["z"])
    bl = per_layer[str(best_li)]
    rows = bl["rows"]

    # CL1: paired NF>OP + shuffled-label null, at best layer
    signc = cmr(np.sign(gate[best_li]))
    cents = group_centroids(signc, [p["group"] for p in probes])
    cents_unit = {prim: unit(cents[f"A:{prim}"]) for prim in bl["anch_prims"]}
    spell_unit = {r["group"]: unit(cents[r["group"]]) for r in rows}
    deltas = np.array([r["nf_align"] - r["op_align"] for r in rows
                       if np.isfinite(r["nf_align"]) and np.isfinite(r["op_align"])])
    # paired sign/bootstrap p that mean(delta) > 0
    rng = np.random.default_rng(seed)
    boot = np.array([rng.choice(deltas, size=len(deltas), replace=True).mean()
                     for _ in range(2000)]) if len(deltas) else np.array([0.0])
    p_paired = float((np.sum(boot <= 0.0) + 1) / (len(boot) + 1))
    shuf = cl1_shuffle_null(rows, bl["anch_prims"], cents_unit, spell_unit,
                            obs_nf=bl["nf_align"], n_perm=n_perm, seed=seed)
    cl1_pass = bool(deltas.mean() > 0 and p_paired < 0.05 and shuf["p_value"] < 0.05) \
        if len(deltas) else False

    # CL2: within-NF coherence vs token-matched null (pooled over targets w/ >=2)
    cohs = {t: within_coherence(signc, probes, t) for t in COLLAPSE}
    obs_coh = float(np.nanmean([v for v in cohs.values() if np.isfinite(v)]))
    cl2 = cl2_null(signc, probes, obs_coh, n_perm=n_perm, seed=seed)
    cl2_pass = bool(np.isfinite(cl2["p_value"]) and obs_coh > cl2["null_mean"]
                    and cl2["p_value"] < 0.05)

    # CL4: depth trajectory of delta_nf_op
    traj = [(per_layer[str(li)]["frac"], per_layer[str(li)]["delta_nf_op"])
            for li in want_layers]
    shallow = [d for f, d in traj if f < 0.30]
    late = [d for f, d in traj if f > 0.60]
    rising = bool(shallow and late and np.mean(late) > np.mean(shallow)
                  and np.mean(late) > 0)

    # CL5 void (register not SIGNIFICANTLY formed => measurement void)
    anchor_z = bl["anchor_silhouette"]["z"]
    anchor_p = bl["anchor_silhouette"]["p_value"]
    void = not (np.isfinite(anchor_z) and anchor_z > 0 and anchor_p < 0.05)

    # verdict
    nf, op, hd, tok = bl["nf_align"], bl["op_align"], bl["head_align"], bl["tok_align"]
    if void:
        verdict = "VOID"
    elif cl1_pass and cl2_pass:
        verdict = "EXTENSIONAL-ROUTING"
    elif np.isfinite(tok) and tok >= max(nf, op, hd) and tok > 0:
        verdict = "SYNTACTIC-TOKEN"
    elif max(op, hd) >= nf:
        verdict = "OPERATIONAL-ROUTING"
    elif nf > op and (rising or not (cl1_pass and cl2_pass)):
        verdict = "MIXED-REDUCTION-VISIBLE"
    else:
        verdict = "OPERATIONAL-ROUTING"

    return {
        "verdict": verdict, "best_layer": int(best_li), "best_frac": bl["frac"],
        "gates": {
            "CL1_EXTENSIONAL_ALIGNMENT": {
                "pass": cl1_pass, "mean_nf": nf, "mean_op": op,
                "mean_delta": float(deltas.mean()) if len(deltas) else float("nan"),
                "p_paired": p_paired, "shuffle_null": shuf},
            "CL2_COLLAPSE_COHERENCE": {
                "pass": cl2_pass, "within_coh": cohs, "obs_mean": obs_coh, "null": cl2},
            "CL3_OPERATIONAL_BASELINE": {
                "mean_op": op, "mean_head": hd, "mean_tok": tok},
            "CL4_DEPTH_TRAJECTORY": {"rising": rising, "trajectory": traj},
            "CL5_COHERENCE_SANE": {
                "pass": not void, "anchor_silhouette_z": anchor_z,
                "anchor_silhouette_p": bl["anchor_silhouette"]["p_value"]},
        },
        "per_layer": {k: {kk: vv for kk, vv in v.items() if kk != "rows"}
                      for k, v in per_layer.items()},
        "best_rows": rows,
    }


# ---------------------------------------------------------------------------- #
# validate — planted worlds                                                    #
# ---------------------------------------------------------------------------- #
def _plant(probes: list[dict], world: str, d: int, seed: int,
           want_layers: list[int]) -> dict[int, np.ndarray]:
    """Synthesize sign-carrying gate activations that should land `world`."""
    rng = np.random.default_rng(seed)
    prims = ANCHOR_ORDER
    pdir = {p: rng.choice([-1.0, 1.0], size=d) for p in prims}
    n = len(probes)
    base = np.zeros((n, d))
    for i, p in enumerate(probes):
        if world == "void":
            base[i] = rng.normal(0, 1, d)
            continue
        if p["kind"] == "anchor":
            base[i] = pdir[p["prim"]]
        elif p["kind"] == "collapse":
            if world == "extensional":
                base[i] = pdir[p["nf"]]
            elif world == "operational":
                fs = [pdir[f] for f in p["fired"] if f in pdir]
                base[i] = np.mean(fs, axis=0) if fs else rng.normal(0, 1, d)
            elif world == "syntactic":
                base[i] = pdir.get("K", rng.normal(0, 1, d))
            else:
                base[i] = rng.normal(0, 1, d)
        else:  # distractor
            base[i] = rng.normal(0, 1, d)
    base = base + rng.normal(0, 0.35, (n, d))
    return {li: base.copy() for li in want_layers}


def run_validate() -> int:
    print("== §P-CL-COLLAPSE --validate ==", file=sys.stderr)
    probes = build_probes(n_per=8, seed=0)
    kinds = {k: sum(1 for p in probes if p["kind"] == k)
             for k in ("anchor", "collapse", "distractor")}
    print(f"  probes: {len(probes)}  {kinds}", file=sys.stderr)

    # primitive certification (extensional equality, alphabets, distractor variety)
    for p in probes:
        if p["kind"] == "collapse":
            assert p["nf"] in COLLAPSE, p
    ncol = [p for p in probes if p["kind"] == "collapse"]
    # per-instance extensional equality is asserted inside build_probes(); re-affirm
    print(f"  certified collapse instances: {len(ncol)} (extensional eq at build)",
          file=sys.stderr)
    # distractors reduce to VARIED (not a single fixed) NF
    dnfs = {p["reduces_to"] for p in probes if p["kind"] == "distractor"}
    assert len(dnfs) >= 2, f"distractors not varied: {dnfs}"
    print(f"  distractor NFs (varied): {sorted(dnfs)}", file=sys.stderr)

    want_layers = [0, 1, 2, 3]
    n_layers = 4
    d = 160
    cases = {
        "extensional": "EXTENSIONAL-ROUTING",
        "operational": "OPERATIONAL-ROUTING",
        "syntactic": "SYNTACTIC-TOKEN",
        "void": "VOID",
    }
    ok = True
    for world, expect in cases.items():
        gate = _plant(probes, world, d, seed=1, want_layers=want_layers)
        res = analyze(gate, probes, want_layers, n_layers, n_perm=400, seed=0)
        got = res["verdict"]
        g = res["gates"]
        mark = "PASS" if got == expect else "FAIL"
        if got != expect:
            ok = False
        print(f"  [{mark}] world={world:12s} -> {got:26s} (want {expect}) "
              f"nf={g['CL1_EXTENSIONAL_ALIGNMENT']['mean_nf']:+.3f} "
              f"op={g['CL1_EXTENSIONAL_ALIGNMENT']['mean_op']:+.3f} "
              f"CL5z={g['CL5_COHERENCE_SANE']['anchor_silhouette_z']:+.2f}",
              file=sys.stderr)
    print(f"  == {'ALL PASS' if ok else 'FAILURES'} ==", file=sys.stderr)
    return 0 if ok else 1


# ---------------------------------------------------------------------------- #
# main                                                                          #
# ---------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--max-length", type=int, default=64)
    ap.add_argument("--n-per", type=int, default=20, help="instantiations per spelling")
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true", help="tiny n_per, verdict NOT read")
    ap.add_argument("--out", default=None)
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    n_per = 3 if args.smoke else args.n_per
    probes = build_probes(n_per=n_per, seed=args.seed)
    kinds = {k: sum(1 for p in probes if p["kind"] == k)
             for k in ("anchor", "collapse", "distractor")}
    prompts = [p["text"] for p in probes]
    print(f"[{args.model}] {len(probes)} probes {kinds}", file=sys.stderr)

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()

    gate_mods = find_gate_modules(model)
    n_layers = len(gate_mods)
    want_layers = pick_layers(n_layers)
    print(f"  arch: {n_layers} layers; layers {want_layers}", file=sys.stderr)

    t0 = time.time()
    _hidden, gate, plen, n_layers = collect(
        model, tok, args.device, prompts, args.max_length, want_layers)
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    res = analyze(gate, probes, want_layers, n_layers,
                  n_perm=args.n_perm, seed=args.seed)
    res["model"] = args.model
    res["register"] = "topological/routing"
    res["git_sha"] = git_sha()
    res["n_probes"] = len(probes)
    res["kinds"] = kinds
    res["n_per"] = n_per
    res["elapsed_s"] = round(time.time() - t0, 1)
    res["smoke"] = args.smoke

    out_dir = (Path(args.out) if args.out
               else RESULTS_DIR / args.model.replace("/", "_"))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(res, indent=2, default=float))
    np.savez_compressed(out_dir / "gate_signs.npz",
                        **{f"gate_L{li:02d}": np.sign(gate[li]).astype(np.int8)
                           for li in want_layers},
                        groups=np.array([p["group"] for p in probes]),
                        prompt_len=plen)

    g = res["gates"]
    print("", file=sys.stderr)
    print(f"  === {args.model} §P-CL-COLLAPSE ===", file=sys.stderr)
    print(f"  best layer L{res['best_layer']} (f={res['best_frac']})  "
          f"CL5 anchor-sil z={g['CL5_COHERENCE_SANE']['anchor_silhouette_z']:+.2f}",
          file=sys.stderr)
    print(f"  CL1 nf={g['CL1_EXTENSIONAL_ALIGNMENT']['mean_nf']:+.4f} "
          f"op={g['CL1_EXTENSIONAL_ALIGNMENT']['mean_op']:+.4f} "
          f"delta={g['CL1_EXTENSIONAL_ALIGNMENT']['mean_delta']:+.4f} "
          f"p_paired={g['CL1_EXTENSIONAL_ALIGNMENT']['p_paired']:.4f} "
          f"p_shuf={g['CL1_EXTENSIONAL_ALIGNMENT']['shuffle_null']['p_value']:.4f} "
          f"pass={g['CL1_EXTENSIONAL_ALIGNMENT']['pass']}", file=sys.stderr)
    print(f"  CL2 within_coh={g['CL2_COLLAPSE_COHERENCE']['obs_mean']:+.4f} "
          f"null={g['CL2_COLLAPSE_COHERENCE']['null']['null_mean']:+.4f} "
          f"p={g['CL2_COLLAPSE_COHERENCE']['null']['p_value']:.4f} "
          f"pass={g['CL2_COLLAPSE_COHERENCE']['pass']}", file=sys.stderr)
    print(f"  CL3 op={g['CL3_OPERATIONAL_BASELINE']['mean_op']:+.4f} "
          f"head={g['CL3_OPERATIONAL_BASELINE']['mean_head']:+.4f} "
          f"tok={g['CL3_OPERATIONAL_BASELINE']['mean_tok']:+.4f}", file=sys.stderr)
    print(f"  CL4 depth rising={g['CL4_DEPTH_TRAJECTORY']['rising']}  "
          f"traj={[(f, round(dd, 3)) for f, dd in g['CL4_DEPTH_TRAJECTORY']['trajectory']]}",  # noqa: E501
          file=sys.stderr)
    tag = "  (SMOKE — verdict NOT read)" if args.smoke else ""
    print(f"  VERDICT: {res['verdict']}{tag}", file=sys.stderr)
    print(f"  wrote {out_dir}  ({res['elapsed_s']}s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
