"""§P-CL-COLLAPSE-2 — prose-anchored extensional routing (FROZEN s322, Michael GO).

Pre-reg: mementum/knowledge/explore/combinator-function-shape.md §P-CL-COLLAPSE-2.

The v1 instrument could not see extensional routing (lexical symbolic anchors +
early-layer gate; §Re-read s322). V2 anchors function-ness in PROSE (the s217
crystal probes) and asks two independent questions:

  Plane A (cross-style): do CLEAN symbolic compounds (NF-symbol absent, kernel-
    certified) align with the PROSE anchor of their normal form? Prose anchors
    contain zero combinator tokens -> token overlap impossible by construction.
  Plane B (within-prose): do prose ROUND-TRIP compounds (wrap/unwrap = I;
    one-filler-two-slots = W; explicit argument swap = C) route like the
    primitive they COMPUTE (extensional) or like the construction they SPELL
    (operational)? Scored per-target as difference-in-differences on contrast
    axes d_T with structure-matched controls; 3x3 cross-cut kills confounds.

Gates: G0 register-forms (void) / G1 axis-separation pre-gate (VOID-BY-DESIGN
per pair) / G2 Plane-A cross-style / G3 Plane-B per-target / G4 cross-cut
selectivity (make-or-break) / G5 lexical disjointness (build-time, enforced).
Verdicts + a-priori (NOT tuned): OPERATIONAL-CONFIRMED 40 / PROSE-EXTENSIONAL
25 / BOTH-EXTENSIONAL 10 / SYMBOLIC-ONLY 5 / MIXED 15 / VOID 5.

Register: routing (sign gate_proj pre-act, CMR, last token) — v1 machinery
verbatim. Primary read = LATE band (frac >= 0.6) mean; full per-layer
trajectory + raw signs persisted (s322 re-read lesson).

License: MIT (lambda provenance).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from cl_collapse import (  # noqa: E402  (v1 apparatus, verbatim reuse)
    _alphabet,
    build_probes,
)
from combinator_relationship_map import (  # noqa: E402
    cmr,
    collect,
    find_gate_modules,
    git_sha,
    pick_layers,
    unit,
)

from verbum.probes.library import crystal_probes  # noqa: E402

RESULTS_DIR = _PROJECT_ROOT / "results" / "cl-collapse2"

ANCHOR_POOLS = ("I", "K", "W", "C", "B", "S")   # prose crystal pools
TARGETS = ("I", "W", "C")                        # Plane B targets
LATE_FRAC = 0.60                                 # primary read band

# ---------------------------------------------------------------------------- #
# Plane B — prose families (compound computes T; control matches syntax, not T) #
# ---------------------------------------------------------------------------- #
FAMILIES: dict[str, dict[str, list[str]]] = {
    "I": {   # round trip: do then undo -> referent unchanged (computes I)
        "compound": [
            "She wrapped the parcel and then unwrapped it.",
            "He zipped the archive and then unzipped it.",
            "They raised the flag and then lowered it.",
            "She locked the drawer and then unlocked it.",
            "He inflated the balloon and then deflated it.",
            "She buttoned the coat and then unbuttoned it.",
            "He plugged in the cable and then unplugged it.",
            "The diver descended to the reef and then surfaced.",
            "She folded the map and then unfolded it.",
            "He tied the knot and then untied it.",
            "The teller deposited the coins and then withdrew them.",
            "He coiled the hose and then uncoiled it.",
        ],
        "control": [
            "She wrapped the parcel and then shipped it.",
            "He zipped the archive and then emailed it.",
            "They raised the flag and then saluted it.",
            "She locked the drawer and then painted it.",
            "He inflated the balloon and then released it.",
            "She buttoned the coat and then brushed it.",
            "He plugged in the cable and then routed it.",
            "The diver descended to the reef and then photographed it.",
            "She folded the map and then framed it.",
            "He tied the knot and then trimmed it.",
            "The teller deposited the coins and then counted them.",
            "He coiled the hose and then stowed it.",
        ],
    },
    "W": {   # one filler, two slots: f x x (NO reflexive pronouns)
        "compound": [
            "He gauged the plank against the plank.",
            "She matched the fabric with the fabric.",
            "The critic judged the novel against the novel.",
            "They bundled the glove with the glove.",
            "He aligned the beam with the beam.",
            "The referee pitted the boxer against the boxer.",
            "She blended the batter into the batter.",
            "He stacked the tile onto the tile.",
            "The analyst plotted the curve against the curve.",
            "She fastened the strap to the strap.",
            "He spliced the rope into the rope.",
            "The baker layered the crust over the crust.",
        ],
        "control": [
            "He gauged the plank against the rail.",
            "She matched the fabric with the trim.",
            "The critic judged the novel against the memoir.",
            "They bundled the glove with the mitten.",
            "He aligned the beam with the post.",
            "The referee pitted the boxer against the wrestler.",
            "She blended the batter into the icing.",
            "He stacked the tile onto the slab.",
            "The analyst plotted the curve against the baseline.",
            "She fastened the strap to the buckle.",
            "He spliced the rope into the cable.",
            "The baker layered the crust over the filling.",
        ],
    },
    "C": {   # explicit argument swap: C f y x
        "compound": [
            "He whisked the syrup into the batter, not the batter into the syrup.",
            "She poured the broth into the kettle, not the kettle into the broth.",
            "They bolted the bracket to the girder, not the girder to the bracket.",
            "He fitted the lens into the housing, not the housing into the lens.",
            "She clipped the badge onto the lanyard, not the lanyard onto the badge.",
            "The porter swung the pack onto the barrow, not the barrow onto the pack.",
            "He glued the emblem to the visor, not the visor to the emblem.",
            "She moored the skiff at the jetty, not the jetty at the skiff.",
            "The mason perched the lintel on the pillar, not the pillar on the lintel.",
            "He hitched the caravan to the lorry, not the lorry to the caravan.",
            "She riveted the hinge to the shutter, not the shutter to the hinge.",
            "The nurse lashed the splint to the wrist, not the wrist to the splint.",
        ],
        "control": [
            "He whisked the syrup into the batter, not the molasses.",
            "She poured the broth into the kettle, not the stockpot.",
            "They bolted the bracket to the girder, not the joist.",
            "He fitted the lens into the housing, not the adapter.",
            "She clipped the badge onto the lanyard, not the cord.",
            "The porter swung the pack onto the barrow, not the pallet.",
            "He glued the emblem to the visor, not the brim.",
            "She moored the skiff at the jetty, not the quay.",
            "The mason perched the lintel on the pillar, not the buttress.",
            "He hitched the caravan to the lorry, not the tractor.",
            "She riveted the hinge to the shutter, not the casing.",
            "The nurse lashed the splint to the wrist, not the ankle.",
        ],
    },
}

# ---------------------------------------------------------------------------- #
# G5 — lexical disjointness (build-time certification, code-enforced)          #
# ---------------------------------------------------------------------------- #
_STOP = {
    "a", "an", "the", "and", "or", "but", "then", "not", "no", "nor",
    "to", "of", "in", "into", "on", "onto", "at", "by", "with", "from",
    "for", "against", "over", "under", "up", "down", "off", "out", "again",
    "he", "she", "it", "they", "them", "him", "her", "his", "its", "their",
    "is", "was", "were", "be", "been", "would", "could", "will", "had",
    "has", "have", "that", "this", "if", "before", "after", "afterward",
    "as", "so", "than", "about", "who", "which", "you", "your", "i", "we",
}
# reflexives are deliberately CONTENT (they are the I/W anchor confound)


def _lemmas(text: str) -> set[str]:
    out = set()
    for raw in text.lower().split():
        w = "".join(c for c in raw if c.isalpha())
        if not w or w in _STOP:
            continue
        for suf in ("ing", "ed", "es", "s"):
            if w.endswith(suf) and len(w) - len(suf) >= 3:
                w = w[: -len(suf)]
                break
        out.add(w)
    return out


def check_disjointness(anchor_texts: list[str]) -> dict:
    """G5: family lemmas ∩ anchor lemmas == ∅ (hard); cross-family overlap
    <= 3 lemmas per pair (frozen soft bound). Returns report; raises on fail."""
    anchor_lem = set()
    for t in anchor_texts:
        anchor_lem |= _lemmas(t)
    fam_lem = {}
    for t_name, fam in FAMILIES.items():
        fl = set()
        for s in fam["compound"] + fam["control"]:
            fl |= _lemmas(s)
        fam_lem[t_name] = fl
    report = {"anchor_overlap": {}, "cross_family_overlap": {}}
    for t_name, fl in fam_lem.items():
        ov = sorted(fl & anchor_lem)
        report["anchor_overlap"][t_name] = ov
        assert not ov, f"G5 FAIL: family {t_name} shares lemmas w/ anchors: {ov}"
    names = list(fam_lem)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            ov = sorted(fam_lem[names[i]] & fam_lem[names[j]])
            report["cross_family_overlap"][f"{names[i]}x{names[j]}"] = ov
            assert len(ov) <= 3, \
                f"G5 FAIL: families {names[i]}/{names[j]} overlap: {ov}"
    return report


# ---------------------------------------------------------------------------- #
# probe assembly                                                                #
# ---------------------------------------------------------------------------- #
def clean_symbolic_probes(n_per: int, seed: int) -> list[dict]:
    """v1 collapse compounds, CLEAN subset only (NF-symbol absent; kernel-
    certified by build_probes). group=C:{nf}:{i}, plus nf/fired metadata."""
    out = []
    for p in build_probes(n_per, seed):
        if p["kind"] != "collapse":
            continue
        if p["nf"] in _alphabet(p["text"]):
            continue   # dirty — excluded at DESIGN time (v1 method lesson)
        out.append(p)
    return out


def assemble(n_per: int, seed: int, cap_anchor: int = 0) -> list[dict]:
    """Full pool: prose anchors + clean symbolic + prose families."""
    probes: list[dict] = []
    for pool in ANCHOR_POOLS:
        ps = [p for p in crystal_probes() if p.combinator == pool]
        if cap_anchor:
            ps = ps[:cap_anchor]
        for p in ps:
            probes.append({"text": p.prompt, "kind": "anchor_prose",
                           "group": f"P:{pool}", "pool": pool})
    probes += clean_symbolic_probes(n_per, seed)
    for t_name, fam in FAMILIES.items():
        for role in ("compound", "control"):
            for s in fam[role]:
                probes.append({"text": s, "kind": f"prose_{role}",
                               "group": f"F:{t_name}:{role}", "target": t_name})
    return probes


# ---------------------------------------------------------------------------- #
# pure analysis (validate-shared; X = per-layer routing matrix, sign at collect) #
# ---------------------------------------------------------------------------- #
def _centroid(X: np.ndarray, mask: np.ndarray) -> np.ndarray:
    return X[mask].mean(axis=0)


def _silhouette(X: np.ndarray, labels: np.ndarray) -> float:
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


def contrast_axes(X: np.ndarray, probes: list[dict]) -> dict[str, np.ndarray]:
    """d_T = unit(centroid(A_T) - mean_{T'!=T} centroid(A_T')) over prose pools."""
    pools = {}
    g = np.array([p.get("pool", "") for p in probes])
    for pool in ANCHOR_POOLS:
        pools[pool] = _centroid(X, g == pool)
    axes = {}
    for t in TARGETS:
        others = np.mean([pools[p] for p in ANCHOR_POOLS if p != t], axis=0)
        axes[t] = unit(pools[t] - others)
    return axes


def g1_axis_separation(X: np.ndarray, probes: list[dict], n_perm: int,
                       seed: int) -> dict:
    """Pre-gate: per-pair POOL SEPARABILITY — silhouette of the two anchor
    pools vs label-permutation null; pass iff obs > null at p < 0.05.
    Fail -> pair VOID-BY-DESIGN (instrument cannot separate the functions).

    AMENDMENT (s322, --validate-forced, pre-run, instrument-side only): the
    frozen |cos(d_T,d_T')|-vs-split-null statistic is register-mismatched —
    the mean-of-others axis construction mechanically couples axes (shared
    -1/(P-1) term) so obs |cos| exceeds a noise-dominated split null even for
    perfectly separable pools. Pool separability is the quantity VOID-BY-
    DESIGN actually needs; axis coupling is shared across targets and is
    handled by the G4 cross-cut. Gates/verdicts/a-priori UNCHANGED."""
    rng = np.random.default_rng(seed)
    g = np.array([p.get("pool", "") for p in probes])
    out = {}
    for i, t1 in enumerate(TARGETS):
        for t2 in TARGETS[i + 1:]:
            mask = (g == t1) | (g == t2)
            Xp, lab = X[mask], g[mask]
            obs = _silhouette(Xp, lab)
            null = np.empty(n_perm)
            for k in range(n_perm):
                null[k] = _silhouette(Xp, rng.permutation(lab))
            p = float((np.sum(null >= obs) + 1) / (n_perm + 1))
            out[f"{t1}x{t2}"] = {"obs_sil": float(obs),
                                 "null_mean": float(null.mean()),
                                 "p_value": p, "pass": bool(p < 0.05)}
    live = {t: all(v["pass"] for k, v in out.items() if t in k.split("x"))
            for t in TARGETS}
    return {"pairs": out, "live": live}


def plane_b_scores(X: np.ndarray, probes: list[dict],
                   axes: dict[str, np.ndarray]) -> np.ndarray:
    """M[s,t] = DiD score of family s on axis d_t (3x3)."""
    g = np.array([p["group"] for p in probes])
    Xu = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)
    M = np.zeros((len(TARGETS), len(TARGETS)))
    for si, s in enumerate(TARGETS):
        comp = Xu[g == f"F:{s}:compound"]
        ctrl = Xu[g == f"F:{s}:control"]
        for ti, t in enumerate(TARGETS):
            M[si, ti] = float((comp @ axes[t]).mean()
                              - (ctrl @ axes[t]).mean())
    return M


def g3_g4(X: np.ndarray, probes: list[dict], axes: dict[str, np.ndarray],
          live: dict[str, bool], n_perm: int, seed: int) -> dict:
    """G3 per-target diagonal vs shuffled compound/control labels; G4 cross-cut
    (row+column diagonal dominance) vs the same label-shuffle null."""
    rng = np.random.default_rng(seed)
    g = np.array([p["group"] for p in probes])
    Xu = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)
    M = plane_b_scores(X, probes, axes)

    def shuffled_M() -> np.ndarray:
        Ms = np.zeros_like(M)
        for si, s in enumerate(TARGETS):
            idx = np.where((g == f"F:{s}:compound") | (g == f"F:{s}:control"))[0]
            lab = rng.permutation(np.array(
                [1 if g[i] == f"F:{s}:compound" else 0 for i in idx]))
            comp = Xu[idx[lab == 1]]
            ctrl = Xu[idx[lab == 0]]
            for ti, t in enumerate(TARGETS):
                Ms[si, ti] = float((comp @ axes[t]).mean()
                                   - (ctrl @ axes[t]).mean())
        return Ms

    null_M = np.stack([shuffled_M() for _ in range(n_perm)])
    res = {"M": M.tolist(), "per_target": {}}
    for ti, t in enumerate(TARGETS):
        diag = M[ti, ti]
        p3 = float((np.sum(null_M[:, ti, ti] >= diag) + 1) / (n_perm + 1))
        row_dom = diag - max(M[ti, tj] for tj in range(len(TARGETS)) if tj != ti)
        col_dom = diag - max(M[sj, ti] for sj in range(len(TARGETS)) if sj != ti)
        null_row = null_M[:, ti, ti] - np.max(
            np.delete(null_M[:, ti, :], ti, axis=1), axis=1)
        null_col = null_M[:, ti, ti] - np.max(
            np.delete(null_M[:, :, ti], ti, axis=1), axis=1)
        p_row = float((np.sum(null_row >= row_dom) + 1) / (n_perm + 1))
        p_col = float((np.sum(null_col >= col_dom) + 1) / (n_perm + 1))
        g3 = bool(diag > 0 and p3 < 0.05)
        g4 = bool(row_dom > 0 and col_dom > 0 and p_row < 0.05 and p_col < 0.05)
        res["per_target"][t] = {
            "live": bool(live[t]), "score": float(diag), "p_score": p3,
            "row_dom": float(row_dom), "p_row": p_row,
            "col_dom": float(col_dom), "p_col": p_col,
            "g3_pass": g3, "g4_pass": g4,
            "sub_verdict": ("VOID-BY-DESIGN" if not live[t]
                            else "EXTENSIONAL" if (g3 and g4)
                            else "OPERATIONAL"),
        }
    return res


def plane_a(X: np.ndarray, probes: list[dict], n_perm: int, seed: int) -> dict:
    """G2: clean symbolic compounds vs PROSE anchors — mean(nf-op) beats the
    shuffled-NF-assignment null."""
    rng = np.random.default_rng(seed)
    g = np.array([p["group"] for p in probes])
    pool_cent = {p: unit(_centroid(
        X, np.array([q.get("pool", "") for q in probes]) == p))
        for p in ANCHOR_POOLS}
    meta = {}
    for p in probes:
        if p["kind"] == "collapse":
            meta.setdefault(p["group"], p)
    rows, deltas = [], []
    spell_unit = {}
    for gid, m in sorted(meta.items()):
        c = unit(_centroid(X, g == gid))
        spell_unit[gid] = c
        nf_a = float(np.dot(c, pool_cent[m["nf"]]))
        ops = [pool_cent[f] for f in m["fired"] if f in pool_cent]
        op_a = float(np.mean([np.dot(c, o) for o in ops])) if ops else np.nan
        rows.append({"group": gid, "nf": m["nf"], "fired": m["fired"],
                     "nf_align": nf_a, "op_align": op_a})
        if np.isfinite(op_a):
            deltas.append(nf_a - op_a)
    obs = float(np.mean([r["nf_align"] for r in rows]))
    null = np.empty(n_perm)
    gids = list(spell_unit)
    for k in range(n_perm):
        assign = rng.choice(list(ANCHOR_POOLS), size=len(gids), replace=True)
        null[k] = np.mean([float(np.dot(spell_unit[gid], pool_cent[a]))
                           for gid, a in zip(gids, assign, strict=True)])
    p = float((np.sum(null >= obs) + 1) / (n_perm + 1))
    delta = float(np.mean(deltas)) if deltas else float("nan")
    return {"rows": rows, "mean_nf": obs, "mean_delta_nf_op": delta,
            "shuffle_null_mean": float(null.mean()), "p_value": p,
            "pass": bool(obs > 0 and delta > 0 and p < 0.05)}


def analyze(X_by_layer: dict[int, np.ndarray], probes: list[dict],
            n_layers: int, n_perm: int, seed: int) -> dict:
    """Full pre-registered analysis. X_by_layer = CMR'd routing matrices."""
    pool_lab = np.array([p.get("pool", "") for p in probes])
    anchor_mask = pool_lab != ""
    layers = sorted(X_by_layer)
    late = [li for li in layers if li / max(n_layers - 1, 1) >= LATE_FRAC]
    if not late:
        late = layers[-2:]

    # G0 per-layer silhouette; void unless ANY layer forms + late band forms
    sil = {li: _silhouette(X_by_layer[li][anchor_mask], pool_lab[anchor_mask])
           for li in layers}
    rng = np.random.default_rng(seed)
    sil_null = []
    for li in late:
        Xa = X_by_layer[li][anchor_mask]
        la = pool_lab[anchor_mask]
        for _ in range(min(n_perm, 200)):
            sil_null.append(_silhouette(Xa, rng.permutation(la)))
    sil_late = float(np.mean([sil[li] for li in late]))
    sn = np.array(sil_null)
    g0_p = float((np.sum(sn >= sil_late) + 1) / (len(sn) + 1))
    g0_pass = bool(np.isfinite(sil_late) and g0_p < 0.05)

    # late-band mean matrix (primary read; pre-registered)
    X_late = np.mean([X_by_layer[li] for li in late], axis=0)

    g1 = g1_axis_separation(X_late, probes, min(n_perm, 300), seed)
    axes = contrast_axes(X_late, probes)
    b = g3_g4(X_late, probes, axes, g1["live"], n_perm, seed)
    a = plane_a(X_late, probes, n_perm, seed)

    # depth trajectory (report only): diagonal scores per layer
    traj = {}
    for li in layers:
        ax_l = contrast_axes(X_by_layer[li], probes)
        M_l = plane_b_scores(X_by_layer[li], probes, ax_l)
        traj[str(li)] = {"frac": round(li / max(n_layers - 1, 1), 3),
                         "diag": [float(M_l[i, i]) for i in range(len(TARGETS))],
                         "silhouette": sil[li]}

    live_targets = [t for t in TARGETS if g1["live"][t]]
    ext_targets = [t for t in live_targets
                   if b["per_target"][t]["sub_verdict"] == "EXTENSIONAL"]
    a_pass = a["pass"]

    if not g0_pass:
        verdict = "VOID"
    elif a_pass and ext_targets:
        verdict = "BOTH-EXTENSIONAL"
    elif ext_targets:
        verdict = "PROSE-EXTENSIONAL"
    elif a_pass:
        verdict = "SYMBOLIC-ONLY"
    elif len(live_targets) >= 2:
        verdict = "OPERATIONAL-CONFIRMED"
    else:
        verdict = "MIXED"

    return {
        "verdict": verdict,
        "late_layers": late,
        "gates": {
            "G0_REGISTER_FORMS": {"pass": g0_pass, "sil_late": sil_late,
                                  "p_value": g0_p},
            "G1_AXIS_SEPARATION": g1,
            "G2_PLANE_A": a,
            "G3_G4_PLANE_B": b,
        },
        "live_targets": live_targets, "extensional_targets": ext_targets,
        "trajectory": traj,
    }


# ---------------------------------------------------------------------------- #
# --validate: planted worlds (no model)                                        #
# ---------------------------------------------------------------------------- #
def _plant(world: str, seed: int, d: int = 256) -> tuple[dict, list[dict], int]:
    rng = np.random.default_rng(seed)
    probes = assemble(n_per=3, seed=seed, cap_anchor=12)
    n = len(probes)
    dirs = {p: rng.normal(0, 1, d) for p in ANCHOR_POOLS}
    for k in dirs:
        dirs[k] = unit(dirs[k])
    style_prose = unit(rng.normal(0, 1, d))
    style_sym = unit(rng.normal(0, 1, d))
    two_step = unit(rng.normal(0, 1, d))     # shared spelled-construction dir

    if world == "g1_void":                    # I and W pools identical
        dirs["W"] = dirs["I"]

    X = rng.normal(0, 0.6, (n, d))
    for i, p in enumerate(probes):
        if p["kind"] == "anchor_prose":
            if world != "void":
                X[i] += 3.0 * dirs[p["pool"]] + 1.0 * style_prose
        elif p["kind"] == "collapse":
            X[i] += 1.0 * style_sym
            if world in ("both", "symbolic_only"):
                X[i] += 2.0 * dirs[p["nf"]]
        else:   # prose families
            X[i] += 1.0 * style_prose + 1.5 * two_step
            t = p["target"]
            if p["kind"] == "prose_compound" and world in (
                    "prose_ext", "both") and t == "I":
                X[i] += 2.0 * dirs["I"]
    n_layers = 4
    Xc = cmr(X)
    X_by_layer = {0: Xc, 3: Xc}   # late layer 3/3 = frac 1.0
    return X_by_layer, probes, n_layers


def run_validate() -> int:
    print("── §P-CL-COLLAPSE-2 --validate (planted worlds, no model) ──")
    ok = True
    # G5 runs against the REAL anchor pools (library import, no model)
    anchor_texts = [p.prompt for p in crystal_probes()
                    if p.combinator in ANCHOR_POOLS]
    rep = check_disjointness(anchor_texts)
    print(f"  G5 disjointness vs {len(anchor_texts)} anchor prompts   ✓ "
          f"(cross-family max "
          f"{max(len(v) for v in rep['cross_family_overlap'].values())} lemmas)")
    want = {
        "operational": "OPERATIONAL-CONFIRMED",
        "prose_ext": "PROSE-EXTENSIONAL",
        "both": "BOTH-EXTENSIONAL",
        "symbolic_only": "SYMBOLIC-ONLY",
        "void": "VOID",
    }
    for world, expect in want.items():
        X_by_layer, probes, n_layers = _plant(world, seed=42)
        res = analyze(X_by_layer, probes, n_layers, n_perm=200, seed=0)
        got = res["verdict"]
        good = got == expect
        ok &= good
        print(f"  {world:14s} -> {got:22s} expect {expect:22s} "
              f"{'✓' if good else '✗ FAIL'}")
    # g1_void: I/W collapse -> both voided; C alone live -> MIXED path
    X_by_layer, probes, n_layers = _plant("g1_void", seed=42)
    res = analyze(X_by_layer, probes, n_layers, n_perm=200, seed=0)
    live = res["gates"]["G1_AXIS_SEPARATION"]["live"]
    good = (not live["I"]) and (not live["W"]) and res["verdict"] == "MIXED"
    ok &= good
    print(f"  g1_void        -> live={live} verdict={res['verdict']:14s} "
          f"expect I,W void + MIXED {'✓' if good else '✗ FAIL'}")
    # primitives
    n_fam = {t: (len(FAMILIES[t]["compound"]), len(FAMILIES[t]["control"]))
             for t in TARGETS}
    prim = all(c >= 12 and k >= 12 for c, k in n_fam.values())
    ok &= prim
    print(f"  primitive family sizes >=12         {'✓' if prim else '✗ FAIL'}")
    refl = not any(w in " ".join(
        s for f in FAMILIES.values() for r in f.values() for s in r).lower()
        for w in ("itself", "herself", "himself", "themselves"))
    ok &= refl
    print(f"  primitive no reflexives in Plane B  {'✓' if refl else '✗ FAIL'}")
    clean = clean_symbolic_probes(3, 0)
    groups = sorted({p["group"] for p in clean})
    prim3 = len(groups) == 7 and all(
        p["nf"] not in _alphabet(p["text"]) for p in clean)
    ok &= prim3
    print(f"  primitive 7 clean symbolic groups   {'✓' if prim3 else '✗ FAIL'}")
    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
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
    ap.add_argument("--n-per", type=int, default=20)
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true",
                    help="small pools, verdict NOT read")
    ap.add_argument("--out", default=None)
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    n_per = 3 if args.smoke else args.n_per
    cap = 8 if args.smoke else 0
    probes = assemble(n_per=n_per, seed=args.seed, cap_anchor=cap)
    anchor_texts = [p["text"] for p in probes if p["kind"] == "anchor_prose"]
    g5 = check_disjointness(anchor_texts)   # hard gate at build time
    kinds = {}
    for p in probes:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    prompts = [p["text"] for p in probes]
    print(f"[{args.model}] {len(probes)} probes {kinds} (G5 pass)",
          file=sys.stderr)

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

    X_by_layer = {li: cmr(np.sign(gate[li]).astype(np.float64))
                  for li in want_layers}
    res = analyze(X_by_layer, probes, n_layers,
                  n_perm=args.n_perm, seed=args.seed)
    res["model"] = args.model
    res["register"] = "topological/routing"
    res["git_sha"] = git_sha()
    res["n_probes"] = len(probes)
    res["kinds"] = kinds
    res["g5_report"] = g5
    res["elapsed_s"] = round(time.time() - t0, 1)
    res["smoke"] = args.smoke

    out_dir = (Path(args.out) if args.out
               else RESULTS_DIR / args.model.replace("/", "_"))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(res, indent=2,
                                                     default=float))
    np.savez_compressed(out_dir / "gate_signs.npz",
                        **{f"gate_L{li:02d}": np.sign(gate[li]).astype(np.int8)
                           for li in want_layers},
                        groups=np.array([p["group"] for p in probes]),
                        prompt_len=plen)

    g = res["gates"]
    print(f"\n  === {args.model} §P-CL-COLLAPSE-2 ===", file=sys.stderr)
    print(f"  G0 sil_late={g['G0_REGISTER_FORMS']['sil_late']:.4f} "
          f"p={g['G0_REGISTER_FORMS']['p_value']:.4f}", file=sys.stderr)
    for pair, v in g["G1_AXIS_SEPARATION"]["pairs"].items():
        print(f"  G1 {pair}: sil={v['obs_sil']:.3f} null={v['null_mean']:.3f} "
              f"p={v['p_value']:.4f} {'PASS' if v['pass'] else 'VOID-PAIR'}",
              file=sys.stderr)
    a = g["G2_PLANE_A"]
    print(f"  G2 planeA mean_nf={a['mean_nf']:+.4f} "
          f"delta={a['mean_delta_nf_op']:+.4f} p={a['p_value']:.4f} "
          f"pass={a['pass']}", file=sys.stderr)
    for t, v in g["G3_G4_PLANE_B"]["per_target"].items():
        print(f"  B[{t}] score={v['score']:+.4f} p={v['p_score']:.4f} "
              f"row_p={v['p_row']:.4f} col_p={v['p_col']:.4f} "
              f"-> {v['sub_verdict']}", file=sys.stderr)
    print(f"  VERDICT: {res['verdict']}"
          + ("  (SMOKE — verdict NOT read)" if args.smoke else ""),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
