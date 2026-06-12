#!/usr/bin/env python3
# register: topological/routing
"""Combinator-map CONSENSUS — where do open models AGREE on the function shape?

THE QUESTION (session 219, Michael):
  "Find these functions in open models to see where the models all agree.
   Getting those out for our base plate is leverage."

  This is the REVERSE direction of consensus-delta-folding.md: every open-weight
  model is a FINISHED distributed-training contributor. Instead of soliciting
  deltas, MINE the ecosystem and harvest what the models agree on. The agreement
  is the leverage — it is pre-computed structure we can fold into the base plate.

THE FRAME PROBLEM (why this is the right register):
  You CANNOT average raw weights across models — independently-initialised models
  live in different coordinate frames (cross-init sign-corr 0.000, gradient-voting).
  But the per-model 9x9 combinator GRAM (cosine between the routing-register
  centroids of K I B C S D W Y WHNF, after common-mode removal) is a RELATIONAL
  object in shared combinator-label space ⇒ FRAME-INVARIANT ⇒ directly comparable
  across models of any architecture / scale. The Gram is "the map of the functions"
  (combinator_relationship_map.py, s217). This script measures whether the MAPS
  agree across the ecosystem.

THE INSTRUMENT (this script, gradient-free, NO GPU — reads saved Grams):
  inputs : results/combinator-relationship-map/<model>.{json,npz}
           (each npz has gram_route_cmr_L{li} 9x9; json gives n_layers, crystal_order)
  align  : by DEPTH-FRACTION (models differ in depth) — pick each model's Gram at
           the nearest layer-fraction to a target on a fraction grid.
  agree  : pairwise cross-model GramCorr = Pearson of the 36 off-diagonal edges.
  null   : LABEL-PERMUTATION — shuffle the 9 combinator labels of one model's Gram
           (a relabelling symmetry the real shape must break), recompute corr.
           Per-pair z/p + aggregate.
  harvest: CONSENSUS Gram = mean across models; per-EDGE mean (agreement) and
           cross-model std (disagreement). Rank edges:
             UNIVERSAL      = high |mean|, low std  → fold into base (leverage)
             MODEL-SPECIFIC = high std               → stays per-model content
  outputs: results/combinator-map-consensus/consensus.json + stdout summary.

Usage:
  uv run python scripts/experiments/combinator_map_consensus.py
  uv run python scripts/experiments/combinator_map_consensus.py --fracs 0.2,0.3,0.4

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
IN_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"
OUT_DIR = _PROJECT_ROOT / "results" / "combinator-map-consensus"

CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
_IU = np.triu_indices(9, 1)  # 36 off-diagonal edges


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_PROJECT_ROOT,
            text=True).strip()
    except Exception:
        return "unknown"


def load_model(safe: str):
    """Return (name, n_layers, {frac: Gram9x9}, crystal_order, best_frac, sil_z)."""
    npz = np.load(IN_DIR / f"{safe}.npz")
    j = json.loads((IN_DIR / f"{safe}.json").read_text())
    nl = int(j["n_layers"])
    order = j.get("crystal_order", CRYSTAL)
    grams = {}
    for k in npz.keys():
        if k.startswith("gram_route_cmr_L"):
            li = int(k.split("L")[1])
            grams[li / nl] = np.asarray(npz[k], dtype=np.float64)
    best_frac = float(j.get("best_routing_frac", float("nan")))
    sil = j.get("per_layer", {}).get(str(j.get("best_routing_layer")), {})
    sil_z = float(sil.get("route_cmr_silhouette", {}).get("z", float("nan")))
    return j.get("model", safe), nl, grams, order, best_frac, sil_z


def gram_at(grams: dict, target_frac: float) -> tuple[np.ndarray, float]:
    f = min(grams, key=lambda x: abs(x - target_frac))
    return grams[f], f


def edges(G: np.ndarray) -> np.ndarray:
    return G[_IU]


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if a.std() < 1e-12 or b.std() < 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def gram_corr(GA: np.ndarray, GB: np.ndarray) -> float:
    return corr(edges(GA), edges(GB))


def perm_null(GA: np.ndarray, GB: np.ndarray, n_perm: int, rng) -> np.ndarray:
    """Shuffle B's 9 combinator labels (rows+cols), recompute GramCorr."""
    eA = edges(GA)
    out = np.empty(n_perm)
    for i in range(n_perm):
        p = rng.permutation(9)
        out[i] = corr(eA, edges(GB[np.ix_(p, p)]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fracs", type=str, default="0.1,0.2,0.3,0.4,0.5",
                    help="target depth-fractions to align models at")
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--universal-t", type=float, default=2.5,
                    help="UNIVERSAL if reliability_t=|mean|*sqrt(n)/std >= this")
    ap.add_argument("--universal-mean", type=float, default=0.05)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    target_fracs = [float(x) for x in args.fracs.split(",")]

    safes = sorted(p.stem for p in IN_DIR.glob("*.npz")
                   if (IN_DIR / f"{p.stem}.json").exists())
    if len(safes) < 2:
        raise SystemExit(f"need >=2 models in {IN_DIR}, found {len(safes)}")

    models = []
    for s in safes:
        try:
            models.append((s, *load_model(s)))
        except Exception as e:
            log(f"  skip {s}: {e}")
    log(f"loaded {len(models)} models: " + ", ".join(m[1] for m in models))

    rng = np.random.default_rng(args.seed)
    per_frac = {}
    for tf in target_fracs:
        picks, used_fracs = [], []
        for (_safe, name, _nl, grams, order, _bf, _sz) in models:
            if order != CRYSTAL:
                log(f"  WARN {name}: crystal_order != canonical; reorder skipped")
            G, uf = gram_at(grams, tf)
            picks.append(G)
            used_fracs.append(uf)
        n = len(picks)
        # pairwise cross-model GramCorr + per-pair null
        pair_r, pair_z, pair_p = [], [], []
        for i in range(n):
            for k in range(i + 1, n):
                r = gram_corr(picks[i], picks[k])
                null = perm_null(picks[i], picks[k], args.n_perm, rng)
                z = (r - null.mean()) / (null.std() + 1e-12)
                p = (np.sum(null >= r) + 1) / (len(null) + 1)
                pair_r.append(r)
                pair_z.append(z)
                pair_p.append(p)
        pair_r = np.array(pair_r)
        # consensus Gram (mean) + per-edge agreement / disagreement
        stack = np.stack(picks)  # (n,9,9)
        consensus = stack.mean(0)
        edge_mean = consensus[_IU]
        edge_std = stack.std(0)[_IU]
        per_frac[f"{tf:.2f}"] = {
            "target_frac": tf,
            "used_fracs": [round(u, 3) for u in used_fracs],
            "mean_pair_gramcorr": float(pair_r.mean()),
            "min_pair_gramcorr": float(pair_r.min()),
            "max_pair_gramcorr": float(pair_r.max()),
            "mean_pair_z": float(np.mean(pair_z)),
            "median_pair_p": float(np.median(pair_p)),
            "frac_pairs_p_lt_05": float(np.mean(np.array(pair_p) < 0.05)),
        }

    # choose the fraction with the strongest mean agreement for the harvest report
    best_tf = max(per_frac, key=lambda k: per_frac[k]["mean_pair_gramcorr"])
    btf = float(best_tf)
    picks = [gram_at(m[3], btf)[0] for m in models]
    stack = np.stack(picks)
    consensus = stack.mean(0)
    edge_mean = consensus[_IU]
    edge_std = stack.std(0)[_IU]

    n_models = stack.shape[0]
    edge_std_all = stack.std(0)
    # per-edge cross-model RELIABILITY t = |mean|·sqrt(n)/std (high = reliably nonzero
    # = a function relationship every model is forced into = harvest candidate).
    edge_rows = []
    for e, (i, k) in enumerate(zip(*_IU, strict=False)):
        m_, s_ = float(edge_mean[e]), float(edge_std[e])
        t_ = abs(m_) * np.sqrt(n_models) / (s_ + 1e-9)
        edge_rows.append({
            "edge": f"{CRYSTAL[i]}-{CRYSTAL[k]}",
            "consensus": round(m_, 4),
            "cross_model_std": round(s_, 4),
            "reliability_t": round(float(t_), 2),
            "per_model": [round(float(g[i, k]), 4) for g in picks],
            "universal": bool(t_ >= args.universal_t
                              and abs(m_) >= args.universal_mean),
        })
    universal = sorted([r for r in edge_rows if r["universal"]],
                       key=lambda r: -r["reliability_t"])
    model_specific = sorted(edge_rows, key=lambda r: -r["cross_model_std"])[:6]

    # ── per-FAMILY universality, null-calibrated (s219 prediction) ──
    # PREDICTION (Michael): the architecture has ONE structural op (attention=apply) →
    # models cannot innovate at the op level, only at composition → the FORCED
    # map-skeleton families (composition B, selection C/K/I) are UNIVERSAL across
    # models; the recursion family {Y,W,WHNF} is the MODEL-SPECIFIC residual (a
    # transformer never learns Y — attention-over-positions IS the fold; map=B(CB)(CB)
    # needs no recursion combinator). Test each family's internal binding + stability
    # against a RANDOM-NODE-TRIPLE null (the relabelling symmetry the shape must break).
    idx = {c: n for n, c in enumerate(CRYSTAL)}
    families = {
        "composition_BDS": ["B", "D", "S"],
        "selection_KIC": ["K", "I", "C"],
        "recursion_YWWHNF": ["Y", "W", "WHNF"],
    }

    def internal_edges(node_idx):
        return [(node_idx[a], node_idx[b])
                for a in range(len(node_idx)) for b in range(a + 1, len(node_idx))]

    def triple_null(size, stat_fn, n_perm, rng_):
        out = np.empty(n_perm)
        for t in range(n_perm):
            sub = rng_.choice(9, size=size, replace=False)
            out[t] = stat_fn(internal_edges(list(sub)))
        return out

    rng2 = np.random.default_rng(args.seed + 7)
    family_report = {}
    for fam, nodes in families.items():
        ie = internal_edges([idx[c] for c in nodes])
        # mean internal binding / cross-model disagreement over the family's edges
        cons = float(np.mean([consensus[a, b] for a, b in ie]))
        std = float(np.mean([edge_std_all[a, b] for a, b in ie]))
        nb = triple_null(len(nodes),
                         lambda ie_: np.mean([consensus[a, b] for a, b in ie_]),
                         args.n_perm, rng2)
        z_bind = (cons - nb.mean()) / (nb.std() + 1e-12)   # >0 = bound vs random triple
        p_bind = (np.sum(nb >= cons) + 1) / (len(nb) + 1)
        ns = triple_null(len(nodes),
                         lambda ie_: np.mean([edge_std_all[a, b] for a, b in ie_]),
                         args.n_perm, rng2)
        z_stab = (std - ns.mean()) / (ns.std() + 1e-12)    # <0 = more stable
        family_report[fam] = {
            "internal_consensus": round(cons, 4),
            "cross_model_std": round(std, 4),
            "z_bind_vs_random_triple": round(float(z_bind), 2),
            "p_bind": round(float(p_bind), 4),
            "z_stability_vs_random": round(float(z_stab), 2),
            "edges": {f"{CRYSTAL[a]}-{CRYSTAL[b]}": round(float(consensus[a, b]), 4)
                      for a, b in ie},
        }
    skel_z = float(np.mean([family_report["composition_BDS"]["z_bind_vs_random_triple"],
                            family_report["selection_KIC"]["z_bind_vs_random_triple"]]))
    rec_z = family_report["recursion_YWWHNF"]["z_bind_vs_random_triple"]
    skeleton_verdict = {
        "skeleton_mean_z_bind": round(skel_z, 2),
        "recursion_z_bind": round(rec_z, 2),
        "prediction": ("skeleton (comp+sel) universal (z_bind>0) AND "
                       "recursion residual (z_bind <= skeleton)"),
        "supported": bool(skel_z > 2.0 and rec_z < skel_z),
    }

    out = {
        "register": "topological/routing",
        "git_sha": git_sha(),
        "question": ("where do open models agree on the combinator function "
                     "shape (harvest leverage)"),
        "n_models": len(models),
        "models": [m[1] for m in models],
        "model_meta": [{"name": m[1], "n_layers": m[2], "best_frac": round(m[5], 3),
                        "silhouette_z": round(m[6], 3)} for m in models],
        "crystal_order": CRYSTAL,
        "n_perm": args.n_perm,
        "per_frac": per_frac,
        "harvest_frac": btf,
        "consensus_gram": [[round(float(x), 4) for x in row] for row in consensus],
        "universal_edges": universal,
        "model_specific_edges": model_specific,
        "family_internal_consensus": family_report,
        "skeleton_vs_recursion_verdict": skeleton_verdict,
        "elapsed_s": round(time.time() - t0, 1),
    }
    (OUT_DIR / "consensus.json").write_text(json.dumps(out, indent=2))

    # ── summary ──
    log("")
    log("  ════════ COMBINATOR-MAP CONSENSUS — where the ecosystem agrees ════════")
    log(f"  models ({len(models)}): " + ", ".join(m[1] for m in models))
    log(f"  {'frac':<6}{'meanGramCorr':>14}{'meanZ':>8}{'%pairs p<.05':>14}")
    for k, v in per_frac.items():
        log(f"  {k:<6}{v['mean_pair_gramcorr']:>+14.3f}{v['mean_pair_z']:>+8.2f}"
            f"{v['frac_pairs_p_lt_05']*100:>13.0f}%")
    log(f"  ▶ harvest fraction (max agreement): {btf:.2f}")
    log("  per-FAMILY universality (null=random node-triple; "
        "z_bind>0 bound, z_stab<0 stable):")
    for fam, fr in family_report.items():
        log(f"    {fam:<18} cons={fr['internal_consensus']:+.3f} "
            f"z_bind={fr['z_bind_vs_random_triple']:+.2f} "
            f"p={fr['p_bind']:.3f} std={fr['cross_model_std']:.3f} "
            f"z_stab={fr['z_stability_vs_random']:+.2f}")
    sv = skeleton_verdict
    _ok = "SUPPORTED" if sv["supported"] else "not (yet) supported"
    log(f"  ▶ SKELETON vs RECURSION: skeleton z_bind={sv['skeleton_mean_z_bind']:+.2f} "
        f"recursion z_bind={sv['recursion_z_bind']:+.2f}  →  {_ok}")
    log(f"  ▶ UNIVERSAL edges (reliability_t>={args.universal_t}) = harvest:")
    for r in universal:
        log(f"    {r['edge']:<10} consensus={r['consensus']:+.3f}  "
            f"std={r['cross_model_std']:.3f}  t={r['reliability_t']:.2f}")
    if not universal:
        log("    (none cleared the threshold — agreement diffuse, not localised)")
    log("  ▶ MOST MODEL-SPECIFIC edges (high cross-model std):")
    for r in model_specific[:4]:
        log(f"    {r['edge']:<10} consensus={r['consensus']:+.3f}  "
            f"std={r['cross_model_std']:.3f}")
    log(f"  wrote {OUT_DIR/'consensus.json'}  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
