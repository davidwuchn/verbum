#!/usr/bin/env python3
"""S-as-duplicator test: does S crystallize like KIBC, or dissolve like W/Y?

    λ duplication_register(fp, rungs).
      partition:  AFFINE={K,I,B,C} (linear/affine, non-duplicating)
                  DUP   ={S,W,Y}   (self-application / duplication)
                  held  ={D,WHNF}  (exploratory: D=B->B "twice"; WHNF=halt)
      H1 geometry:     score(t) = mean_corr(t, DUP\\t) - mean_corr(t, AFFINE\\t)
                       | Free prediction: score(S) > 0 (S sits with duplicators)
      H2 quantization: per-vertex fidelity-drop FP->rung; S (and DUP group)
                       degrade MORE than AFFINE across the ternary/1-bit ladder
      H3 dispersion:   PR(S) > mean PR(KIBC)  [DEFERRED: needs centroid re-capture]

The honest re-do of s262 (KIBC-vs-SKI). That test used the attention-selectivity
register, which is BLIND to duplication — K, I, B, C, S all merely *route*, so it
returned void ("inconclusive-in-register", S-K corr 0.92 but B-K/C-K ~0.9 too).
These two registers can SEE the duplicator:
  - relational-geometry (H1): does S's Gram neighbourhood = {W,Y} or {K,I,B,C}?
  - quantization/magnitude (H2): duplication is magnitude-carried, so a real
    duplicator is quant-fragile (s269: W fragile 0.849/0.876 vs KIBC >=0.93;
    commit 48366f2 "W joins duplication family").

Pre-registered before reading swept data (s271). K/I/B/C -> AFFINE is
near-definitional; W/Y -> DUP are positive controls; **S is the one earned bit.**
Refute iff S clusters AFFINE *and* stays robust like KIBC. Null -> escalate to
the Mamba substrate-swap (a scan-state CAN copy, so S should crystallise there).

Decision rule (fixed now, lambda yardstick): "S is a duplicator absorbed
holographically, not a clean opcode" counts iff >=2 of {H1, H2(gate), H2(attn)}
beat null at p<0.05 in the predicted direction, AND H1 (geometry) is one of them.

Nulls are EXACT (full enumeration of same-size group labelings) where the count
is small; that is affordable here (9 vertices) and stronger than sampling.

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from math import comb
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from ladder import vertex_fidelity  # noqa: E402
from vsm import CRYSTAL, load_tree  # noqa: E402

AFFINE = ["K", "I", "B", "C"]
DUP = ["S", "W", "Y"]
HELDOUT = ["D", "WHNF"]
REGISTERS = ("gate", "attn")


# ── exact partition null ─────────────────────────────────────────────────────


def _exact_partition_p(
    values: np.ndarray, a_size: int, b_size: int, obs: float
) -> tuple[float, np.ndarray]:
    """Exact P(mean(A) - mean(B) >= obs) over ALL size-fixed labelings of
    ``values`` into disjoint groups A (size a_size) and B (size b_size).

    The observed labeling is one of the enumerated ones, so this is the exact
    permutation probability (no +1 correction needed)."""
    idx = list(range(len(values)))
    stats: list[float] = []
    for a_sel in combinations(idx, a_size):
        rest = [j for j in idx if j not in a_sel]
        for b_sel in combinations(rest, b_size):
            stats.append(
                float(values[list(a_sel)].mean() - values[list(b_sel)].mean())
            )
    arr = np.asarray(stats)
    p = float(np.sum(arr >= obs) / len(arr))
    return p, arr


# ── H1: relational-geometry register ─────────────────────────────────────────


def affinity_score(gram: np.ndarray, basis: list[str], target: str) -> dict:
    """score(t) = mean corr(t, DUP\\t) - mean corr(t, AFFINE\\t) with exact null.

    Positive score => target's Gram neighbourhood leans toward the duplicators.
    Null: all size-preserving relabelings of the 8 non-target vertices into
    (|DUP\\t| dup, |AFFINE\\t| affine, rest held-out)."""
    t = basis.index(target)
    row = np.asarray(gram, dtype=np.float64)[t]
    others = [j for j in range(len(basis)) if j != t]
    dup_idx = [basis.index(n) for n in DUP if n != target]
    aff_idx = [basis.index(n) for n in AFFINE if n != target]
    nd, na = len(dup_idx), len(aff_idx)

    obs = float(row[dup_idx].mean() - row[aff_idx].mean())

    # exact enumeration over the 8 others: choose nd dup, then na affine
    stats: list[float] = []
    for dup_sel in combinations(others, nd):
        rest = [j for j in others if j not in dup_sel]
        for aff_sel in combinations(rest, na):
            stats.append(
                float(row[list(dup_sel)].mean() - row[list(aff_sel)].mean())
            )
    arr = np.asarray(stats)
    p = float(np.sum(arr >= obs) / len(arr))
    return {
        "score": obs,
        "corr_to_dup": float(row[dup_idx].mean()),
        "corr_to_affine": float(row[aff_idx].mean()),
        "n_labelings": len(arr),
        "null_mean": float(arr.mean()),
        "null_std": float(arr.std()),
        "z": float((obs - arr.mean()) / (arr.std() + 1e-12)),
        "p_exact": p,
    }


def nearest_neighbours(gram: np.ndarray, basis: list[str], target: str) -> list:
    """Ranked (vertex, corr) neighbours of target — context for the score."""
    t = basis.index(target)
    row = np.asarray(gram)[t]
    order = sorted(
        (j for j in range(len(basis)) if j != t),
        key=lambda j: row[j],
        reverse=True,
    )
    return [(basis[j], round(float(row[j]), 3)) for j in order]


def h1_geometry(gram: np.ndarray, basis: list[str]) -> dict:
    out = {"per_vertex": {}, "nearest": {}}
    for v in basis:
        out["per_vertex"][v] = affinity_score(gram, basis, v)
    for v in ("S", "W", "Y", "K"):
        out["nearest"][v] = nearest_neighbours(gram, basis, v)
    return out


# ── H2: quantization / magnitude register ────────────────────────────────────


def h2_quantization(
    fp_gram: np.ndarray, rung_gram: np.ndarray, basis: list[str]
) -> dict:
    """Per-vertex fidelity FP->rung; is the DUP group (and S) more fragile?"""
    fid = vertex_fidelity(np.asarray(fp_gram), np.asarray(rung_gram))
    drop = 1.0 - fid  # positive = degraded
    dup_idx = [basis.index(n) for n in DUP]
    aff_idx = [basis.index(n) for n in AFFINE]
    s_idx = basis.index("S")

    # group-level: DUP vs AFFINE degradation
    obs_group = float(drop[dup_idx].mean() - drop[aff_idx].mean())
    p_group, _ = _exact_partition_p(drop, len(dup_idx), len(aff_idx), obs_group)

    # S-specific: S vs AFFINE degradation (A={S} size 1, B=AFFINE size 4)
    obs_s = float(drop[s_idx] - drop[aff_idx].mean())
    p_s, arr_s = _exact_partition_p(drop, 1, len(aff_idx), obs_s)

    return {
        "per_vertex_fidelity": {
            b: round(float(v), 4) for b, v in zip(basis, fid, strict=True)
        },
        "per_vertex_drop": {
            b: round(float(v), 4) for b, v in zip(basis, drop, strict=True)
        },
        "dup_vs_affine": {
            "obs_excess_drop": obs_group,
            "dup_mean_drop": float(drop[dup_idx].mean()),
            "affine_mean_drop": float(drop[aff_idx].mean()),
            "p_exact": p_group,
        },
        "S_vs_affine": {
            "obs_excess_drop": obs_s,
            "S_drop": float(drop[s_idx]),
            "affine_mean_drop": float(drop[aff_idx].mean()),
            "z": float((obs_s - arr_s.mean()) / (arr_s.std() + 1e-12)),
            "p_exact": p_s,
        },
    }


# ── driver ───────────────────────────────────────────────────────────────────


def _reg_gram(tree, register: str) -> np.ndarray | None:
    r = tree.child(register)
    return None if r is None or r.gram is None else np.asarray(r.gram)


def analyze(fp_dir: Path, rungs: dict[str, Path], out_path: Path) -> dict:
    fp = load_tree(fp_dir / "model_vsm.json")
    basis = list(fp.basis)
    assert basis == CRYSTAL, f"unexpected basis {basis}"

    report: dict = {
        "partition": {"AFFINE": AFFINE, "DUP": DUP, "HELDOUT": HELDOUT},
        "fp_parent": fp.name,
        "H1_geometry": {},
        "H2_quantization": {},
        "H3_dispersion": "DEFERRED: no centroid sidecar (needs a --keep-centroids "
        "re-trace); PR(S) vs PR(KIBC) cannot be computed from Gram alone.",
    }

    # H1 runs per tree (FP + each rung) — model-level and per-register
    def _geom_block(tree) -> dict:
        blk = {"model": h1_geometry(np.asarray(tree.gram), basis)}
        for reg in REGISTERS:
            g = _reg_gram(tree, reg)
            if g is not None:
                blk[reg] = h1_geometry(g, basis)
        return blk

    report["H1_geometry"][fp.name + " (FP)"] = _geom_block(fp)

    for rung_name, rung_dir in rungs.items():
        tree = load_tree(rung_dir / "model_vsm.json")
        report["H1_geometry"][f"{tree.name} ({rung_name})"] = _geom_block(tree)

        entry = {"model": h2_quantization(np.asarray(fp.gram),
                                          np.asarray(tree.gram), basis)}
        for reg in REGISTERS:
            gf, gr = _reg_gram(fp, reg), _reg_gram(tree, reg)
            if gf is not None and gr is not None:
                entry[reg] = h2_quantization(gf, gr, basis)
        report["H2_quantization"][rung_name] = {"model_name": tree.name, **entry}

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=1))
    return report


# ── reporting ────────────────────────────────────────────────────────────────


def _fmt_score(s: dict) -> str:
    return (f"score={s['score']:+.3f} (dup {s['corr_to_dup']:+.3f} vs "
            f"affine {s['corr_to_affine']:+.3f}) z={s['z']:+.2f} "
            f"p={s['p_exact']:.4f} [{s['n_labelings']} labelings]")


def _print_report(rep: dict) -> None:
    print("=" * 78)
    print("S-AS-DUPLICATOR TEST  —  partition:")
    print(f"  AFFINE (non-dup) = {rep['partition']['AFFINE']}")
    print(f"  DUP (self-app)   = {rep['partition']['DUP']}")
    print(f"  held-out         = {rep['partition']['HELDOUT']}")
    print("=" * 78)

    print("\n### H1  relational-geometry register  (score>0 => sits with duplicators)")
    for tree_name, blk in rep["H1_geometry"].items():
        print(f"\n  ── {tree_name}")
        for scope in ("model", "gate", "attn"):
            if scope not in blk:
                continue
            pv = blk[scope]["per_vertex"]
            print(f"    [{scope}]")
            for v in ("S", "W", "Y", "K", "I", "B", "C", "D", "WHNF"):
                tag = "  <<< S (earned bit)" if v == "S" else (
                    "  (dup control)" if v in ("W", "Y") else "")
                print(f"      {v:5s} {_fmt_score(pv[v])}{tag}")
            print(f"      S nearest: {blk[scope]['nearest']['S']}")

    print("\n### H2  quantization/magnitude register  (excess drop>0 => more fragile)")
    for rung, e in rep["H2_quantization"].items():
        print(f"\n  ── rung: {rung} ({e['model_name']})")
        for scope in ("model", "gate", "attn"):
            if scope not in e:
                continue
            q = e[scope]
            g = q["dup_vs_affine"]
            s = q["S_vs_affine"]
            print(f"    [{scope}]")
            print("      per-vertex fidelity: " + " ".join(
                f"{b}={q['per_vertex_fidelity'][b]:.3f}" for b in CRYSTAL))
            print(f"      DUP vs AFFINE excess drop {g['obs_excess_drop']:+.4f} "
                  f"(dup {g['dup_mean_drop']:.4f} vs affine "
                  f"{g['affine_mean_drop']:.4f})  p={g['p_exact']:.4f}")
            print(f"      S   vs AFFINE excess drop {s['obs_excess_drop']:+.4f} "
                  f"(S {s['S_drop']:.4f})  z={s['z']:+.2f}  p={s['p_exact']:.4f}")

    print("\n" + "=" * 78)
    print("H3 dispersion:", rep["H3_dispersion"])
    print("=" * 78)


# ── H1 across the whole sweep: does score(S)>0 replicate across the family? ──


def _binom_p_ge(k: int, n: int, p: float) -> float:
    """Exact upper-tail binomial P(X >= k), X ~ Binom(n, p)."""
    return float(sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1)))


def sweep_scan(root: Path, out_path: Path) -> dict:
    """Glob every ``<model>/model_vsm.json`` under ``root``; compute the H1
    duplication-affinity score(S) per model (model/gate/attn scopes) and the
    cross-model binomial replication test.

    Two nulls per scope:
      - SIGN test  (direction): #{score(S)>0} vs Binom(n, 0.5)
      - GATE test  (strength):  #{score(S)>0 AND p<0.05} vs Binom(n, 0.05)

    This is the decisive s271 read: a stable per-model effect that is only
    marginal on single quantized models becomes decisive across the family
    (11/11 positive => sign-test p = 2^-11)."""
    trees = sorted(root.glob("*/model_vsm.json"))
    per_model: list[dict] = []
    for tp in trees:
        try:
            t = load_tree(tp.parent / "model_vsm.json")
        except Exception as exc:  # skip half-written / bad trees
            per_model.append({"dir": tp.parent.name, "error": str(exc)})
            continue
        if t.gram is None or list(t.basis) != CRYSTAL:
            continue
        row: dict = {"model": t.name, "dir": tp.parent.name, "scopes": {}}
        scopes = [("model", np.asarray(t.gram))]
        scopes += [(r, _reg_gram(t, r)) for r in REGISTERS]
        for scope, g in scopes:
            if g is None:
                continue
            sc = affinity_score(g, CRYSTAL, "S")
            row["scopes"][scope] = {
                "score": round(sc["score"], 4),
                "p_exact": round(sc["p_exact"], 4),
                "positive": sc["score"] > 0,
                "gated": bool(sc["p_exact"] < 0.05 and sc["score"] > 0),
            }
        per_model.append(row)

    good = [m for m in per_model if "scopes" in m]
    binom: dict = {}
    for scope in ("model", "gate", "attn"):
        vals = [m["scopes"][scope] for m in good if scope in m["scopes"]]
        n = len(vals)
        if n == 0:
            continue
        n_pos = sum(v["positive"] for v in vals)
        n_gated = sum(v["gated"] for v in vals)
        binom[scope] = {
            "n_models": n,
            "n_score_positive": n_pos,
            "sign_test_p": round(_binom_p_ge(n_pos, n, 0.5), 6),
            "n_gated": n_gated,
            "gate_test_p": round(_binom_p_ge(n_gated, n, 0.05), 6),
            "mean_score": round(float(np.mean([v["score"] for v in vals])), 4),
        }

    report = {
        "mode": "sweep_scan",
        "root": str(root),
        "n_trees_found": len(trees),
        "n_usable": len(good),
        "partition": {"AFFINE": AFFINE, "DUP": DUP, "HELDOUT": HELDOUT},
        "binomial": binom,
        "per_model": per_model,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=1))
    return report


def _print_sweep(rep: dict) -> None:
    print("=" * 78)
    print("H1 SWEEP SCAN — score(S)>0 replication across the family")
    print(f"  {rep['n_usable']} usable trees / {rep['n_trees_found']} found "
          f"under {rep['root']}")
    print("=" * 78)
    print("\n  per-model score(S) [model scope]:")
    for m in rep["per_model"]:
        if "scopes" not in m:
            print(f"    {m['dir']:28s}  (skipped: {m.get('error','no gram')})")
            continue
        s = m["scopes"].get("model")
        if s:
            mark = "OK" if s["gated"] else ("+" if s["positive"] else "-")
            print(f"    {m['dir']:28s}  score={s['score']:+.3f} "
                  f"p={s['p_exact']:.4f}  [{mark}]")
    print("\n  BINOMIAL (does the effect replicate?):")
    for scope, b in rep["binomial"].items():
        print(f"    [{scope}] {b['n_score_positive']}/{b['n_models']} positive "
              f"(sign-test p={b['sign_test_p']:.2e}) | "
              f"{b['n_gated']}/{b['n_models']} gated "
              f"(gate-test p={b['gate_test_p']:.2e}) | "
              f"mean score {b['mean_score']:+.3f}")
    print("=" * 78)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="S-as-duplicator: geometry + quantization registers")
    ap.add_argument("--fp", help="FP parent trace dir (per-model H1+H2 mode)")
    ap.add_argument(
        "--rung", action="append", default=[],
        help="name=dir (e.g. ternary=results/opcode-trace/bonsai27b-unpacked)")
    ap.add_argument(
        "--sweep-scan", metavar="DIR",
        help="glob DIR/*/model_vsm.json → cross-model H1 binomial (s271 read)")
    ap.add_argument(
        "--out", default="results/opcode-trace/duplication_register.json")
    args = ap.parse_args()

    if args.sweep_scan:
        out = Path(args.out)
        if out.name == "duplication_register.json":
            out = out.with_name("duplication_register_sweep.json")
        rep = sweep_scan(Path(args.sweep_scan), out)
        _print_sweep(rep)
        print(f"\n[dup-register] wrote {out}")
        return

    if not args.fp:
        ap.error("need --fp (per-model mode) or --sweep-scan DIR (family mode)")
    rungs = {}
    for spec in args.rung:
        name, _, d = spec.partition("=")
        rungs[name] = Path(d)
    rep = analyze(Path(args.fp), rungs, Path(args.out))
    _print_report(rep)
    print(f"\n[dup-register] wrote {args.out}")


if __name__ == "__main__":
    main()
