"""§P-CL-COLLAPSE late-layer re-read — EXPLORATORY (post-hoc, NOT pre-registered).

s322 audit finding: the s321 gates (CL1/CL2) were evaluated ONLY at the
anchor-silhouette best layer (L4, frac 0.10) — a depth where multi-step
reduction cannot be complete — and the clean/dirty decomposition (NF-symbol
absent/present in the spelling) was computed post-hoc at that layer only.
The persisted gate_signs.npz is lossless for the routing metric (analyze()
uses np.sign only), so the full clean/dirty x layer decomposition is
computable offline with zero model compute.

Question: does CLEAN-spelling nf_align (the genuine dissociation) RISE with
depth? If yes, extensional routing may be alive late and the s321 read
("routing tracks symbol presence") under-claimed; if it stays ~0/negative at
all depths, the s321 verdict survives the audit at every layer.

Reuses cl_collapse machinery verbatim (lambda one_way, no fork). Output:
per-layer table + JSON sidecar next to the original results.

Usage:
  uv run python scripts/experiments/cl_collapse_reread.py \
      --results results/cl-collapse/qwen3-14b
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from cl_collapse import (  # noqa: E402
    _alphabet,
    alignments,
    build_probes,
    cl1_shuffle_null,
    cmr,
    group_centroids,
    unit,
)


def spelling_is_dirty(probes: list[dict], gid: str) -> bool:
    """Dirty iff the NF-target symbol literally appears in the spelling."""
    p = next(p for p in probes if p["group"] == gid)
    return p["nf"] in _alphabet(p["text"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results/cl-collapse/qwen3-14b")
    ap.add_argument("--n-per", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-perm", type=int, default=1000)
    args = ap.parse_args()

    rdir = Path(args.results)
    npz = np.load(rdir / "gate_signs.npz", allow_pickle=False)
    res = json.loads((rdir / "results.json").read_text())

    # rebuild probes deterministically; verify against persisted groups
    probes = build_probes(args.n_per, args.seed)
    groups_npz = [str(g) for g in npz["groups"]]
    groups_re = [p["group"] for p in probes]
    assert groups_re == groups_npz, (
        f"probe rebuild mismatch: {len(groups_re)} vs {len(groups_npz)}; "
        "n-per/seed must match the original run")
    print(f"probe rebuild VERIFIED: {len(probes)} probes, groups identical",
          file=sys.stderr)

    layer_keys = sorted(k for k in npz.files if k.startswith("gate_L"))
    layers = [int(k[6:]) for k in layer_keys]
    n_layers = max(layers) + 1  # best_frac in results.json uses li/(n_layers-1)

    # classify collapse groups clean/dirty
    gids = sorted({p["group"] for p in probes if p["kind"] == "collapse"})
    dirty = {g for g in gids if spelling_is_dirty(probes, g)}
    clean = [g for g in gids if g not in dirty]
    print(f"dirty (NF-symbol present): {sorted(dirty)}", file=sys.stderr)
    print(f"clean (NF-symbol absent):  {clean}", file=sys.stderr)

    per_layer = []
    print("\n layer  frac | clean: nf     op     d      | dirty: nf     op     d")
    for k, li in zip(layer_keys, layers, strict=True):
        sign = npz[k].astype(np.float64)  # already np.sign'd int8
        signc = cmr(sign)
        rows = alignments(signc, probes)["rows"]
        by = {r["group"]: r for r in rows}

        def _mean(sub: list[str], field: str, _by: dict = by) -> float:
            vals = [_by[g][field] for g in sub if np.isfinite(_by[g][field])]
            return float(np.mean(vals)) if vals else float("nan")

        c_nf, c_op = _mean(clean, "nf_align"), _mean(clean, "op_align")
        d_nf, d_op = _mean(sorted(dirty), "nf_align"), _mean(sorted(dirty), "op_align")
        rec = {
            "layer": li, "frac": round(li / (n_layers - 1), 3),
            "clean_nf": c_nf, "clean_op": c_op, "clean_delta": c_nf - c_op,
            "dirty_nf": d_nf, "dirty_op": d_op, "dirty_delta": d_nf - d_op,
            "clean_rows": {g: {f: by[g][f] for f in
                               ("nf_align", "op_align", "head_align")}
                           for g in clean},
        }
        per_layer.append(rec)
        print(f"  L{li:02d}  {rec['frac']:.2f} |"
              f"  {c_nf:+.3f} {c_op:+.3f} {c_nf - c_op:+.3f} |"
              f"  {d_nf:+.3f} {d_op:+.3f} {d_nf - d_op:+.3f}")

    # exploratory stats at the layer maximizing CLEAN delta (and at the last layer)
    best = max(per_layer, key=lambda r: r["clean_delta"])
    stats = {}
    for tag, rec in (("clean_delta_max", best), ("last_layer", per_layer[-1])):
        li = rec["layer"]
        sign = npz[f"gate_L{li:02d}"].astype(np.float64)
        signc = cmr(sign)
        rows = [r for r in alignments(signc, probes)["rows"] if r["group"] in clean]
        cents = group_centroids(signc, [p["group"] for p in probes])
        anch_prims = sorted(p["prim"] for p in probes
                            if p["kind"] == "anchor")
        anch_prims = sorted(set(anch_prims))
        cents_unit = {p: unit(cents[f"A:{p}"]) for p in anch_prims}
        spell_unit = {g: unit(cents[g]) for g in clean}
        deltas = np.array([r["nf_align"] - r["op_align"] for r in rows])
        rng = np.random.default_rng(args.seed)
        boot = np.array([rng.choice(deltas, size=len(deltas), replace=True).mean()
                         for _ in range(2000)])
        p_boot = float((np.sum(boot <= 0.0) + 1) / (len(boot) + 1))
        obs_nf = float(np.mean([r["nf_align"] for r in rows]))
        shuf = cl1_shuffle_null(rows, anch_prims, cents_unit, spell_unit,
                                obs_nf=obs_nf, n_perm=args.n_perm, seed=args.seed)
        stats[tag] = {
            "layer": li, "frac": rec["frac"], "n_clean_groups": len(rows),
            "clean_mean_nf": obs_nf,
            "clean_mean_delta": float(deltas.mean()),
            "p_boot_delta_gt0": p_boot,
            "clean_shuffle_null": shuf,
        }
        print(f"\n [{tag}] L{li:02d} frac={rec['frac']:.2f}  n={len(rows)} clean groups"
              f"\n   mean nf_align {obs_nf:+.3f}  mean delta {deltas.mean():+.3f}"
              f"  p_boot(delta>0)={p_boot:.4f}"
              f"\n   shuffle null: mean {shuf['null_mean']:+.3f}"
              f"  p={shuf['p_value']:.4f}")

    out = {
        "note": "EXPLORATORY post-hoc re-read (s322 audit); NOT a pre-registered "
                "gate. Source measurement: s321 gate_signs.npz (lossless for the "
                "sign/CMR routing metric).",
        "source_git_sha": res.get("git_sha"),
        "model": res.get("model"),
        "dirty_groups": sorted(dirty), "clean_groups": clean,
        "per_layer": [{k: v for k, v in r.items() if k != "clean_rows"}
                      for r in per_layer],
        "clean_rows_by_layer": {str(r["layer"]): r["clean_rows"]
                                for r in per_layer},
        "exploratory_stats": stats,
    }
    out_path = rdir / "reread_late_layer.json"
    out_path.write_text(json.dumps(out, indent=2, default=float))
    print(f"\nwrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
