#!/usr/bin/env python3
# register: topological/routing
"""Cross-model consensus verdict for the tool-calling normal form.

Loads every results/tool-crystal-consensus/*.npz (one per model, written by
tool_crystal_consensus.py) and asks the question the single-model prior run
never asked: do INDEPENDENT model families AGREE on the tool-calling routing
structure above a shuffled-probe null?

Agreement metric (probe-aligned, like manifold_axis_topology_summary):
  for each register r and each model pair (a,b):
     agree = corr( upper(RDM_a^r), upper(RDM_b^r) )
  null: permute probe order of b (1000x) -> agreement under destroyed alignment.

A consensus normal form requires:  mean cross-family agree(route_cmr) >> null.
Contrast it with hidden_full (the prior 'STRONG SUPPORT' common-mode register),
which is expected to be high RAW (everything correlates) but should NOT exceed
its own shuffled-probe null by much once you realize the agreement is the
common mode (we report both; the null calibrates).

Usage:
  uv run python scripts/experiments/tool_crystal_consensus_summary.py \
      [--route-layer-frac 0.6] [--n-perm 1000]
License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "tool-crystal-consensus"


def log(m: str = "") -> None:
    print(m, file=sys.stderr, flush=True)


def upper(D):
    iu = np.triu_indices_from(D, k=1)
    return D[iu]


def agree(Da, Db):
    a, b = upper(Da), upper(Db)
    if a.std() < 1e-12 or b.std() < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def partial_agree(Da, Db, Z):
    """Cross-model agreement controlling for covariate RDM Z (e.g. length)."""
    x, y, z = upper(Da), upper(Db), upper(Z)
    if x.std() < 1e-12 or y.std() < 1e-12 or z.std() < 1e-12:
        return float("nan")
    rxy = np.corrcoef(x, y)[0, 1]
    rxz = np.corrcoef(x, z)[0, 1]
    ryz = np.corrcoef(y, z)[0, 1]
    denom = np.sqrt(max((1 - rxz**2) * (1 - ryz**2), 1e-30))
    return float((rxy - rxz * ryz) / denom)


def length_rdm(plen):
    L = np.abs(plen[:, None] - plen[None, :]).astype(np.float64)
    np.fill_diagonal(L, 0.0)
    return L


def sub_rdm(D, idx):
    return D[np.ix_(idx, idx)]


def agree_null(Da, Db, n_perm, seed):
    """Agreement with probe order of Db permuted (destroys alignment)."""
    n = Db.shape[0]
    rng = np.random.default_rng(seed)
    a = upper(Da)
    vals = []
    for _ in range(n_perm):
        perm = rng.permutation(n)
        Dp = Db[np.ix_(perm, perm)]
        b = upper(Dp)
        if b.std() < 1e-12:
            continue
        vals.append(np.corrcoef(a, b)[0, 1])
    return np.array(vals)


def family(model_name: str) -> str:
    s = model_name.lower()
    for fam in ["qwen3", "qwen2", "mistral", "smollm", "olmo", "pythia",
                "phi", "gpt-neox", "llama", "gemma"]:
        if fam in s:
            return fam
    return s.split("_")[0]


def pick_route_key(keys, frac):
    """Choose the route_sign_cmr layer whose fraction is nearest `frac`."""
    cand = []
    for k in keys:
        if k.startswith("route_sign_cmr_L"):
            li = int(k.split("_L")[1])
            cand.append((li, k))
    if not cand:
        return None
    return cand  # caller resolves frac vs n_layers using the json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--route-layer-frac", type=float, default=0.6)
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    npzs = sorted(RESULTS_DIR.glob("*.npz"))
    if len(npzs) < 2:
        log(f"need >=2 model npz in {RESULTS_DIR}, found {len(npzs)}")
        sys.exit(1)

    models = {}
    for p in npzs:
        safe = p.stem
        js = json.loads((RESULTS_DIR / f"{safe}.json").read_text())
        data = np.load(p, allow_pickle=True)
        n_layers = js["n_layers"]
        # resolve nearest captured layer to the requested fraction
        want = js["want_layers"]
        target = round(args.route_layer_frac * (n_layers - 1))
        li = min(want, key=lambda x: abs(x - target))
        models[safe] = {
            "family": family(safe),
            "n_layers": n_layers,
            "route_li": li,
            "domain": data["domain"],
            "prompt_len": data["prompt_len"].astype(np.float64),
            "rdm": {
                "hidden_full": data["hidden_full"],
                "hidden_cmr": data["hidden_cmr"],
                "route_sign_full": data[f"route_sign_full_L{li:02d}"],
                "route_sign_cmr": data[f"route_sign_cmr_L{li:02d}"],
            },
        }
        log(f"  loaded {safe:32s} fam={family(safe):8s} route L{li} (f~{args.route_layer_frac})")

    names = list(models)
    # alignment sanity: all models must share the probe order (no --limit)
    n0 = models[names[0]]["rdm"]["hidden_full"].shape[0]
    for n in names:
        assert models[n]["rdm"]["hidden_full"].shape[0] == n0, f"{n} probe count mismatch"
    dom0 = models[names[0]]["domain"]
    avg_len = np.mean([models[n]["prompt_len"] for n in names], axis=0)
    Lrdm = length_rdm(avg_len)
    dom_idx = {d: np.where(dom0 == d)[0] for d in sorted(set(dom0.tolist()))}
    within_domains = [d for d in ["schema_binding", "selection", "format"]
                      if d in dom_idx and len(dom_idx[d]) >= 8]

    out = {"models": {n: {"family": models[n]["family"],
                          "route_li": models[n]["route_li"],
                          "n_layers": models[n]["n_layers"]} for n in names},
           "route_layer_frac": args.route_layer_frac, "n_perm": args.n_perm,
           "within_domains": within_domains,
           "domain_counts": {d: int(len(i)) for d, i in dom_idx.items()},
           "registers": {}}

    for reg in ["hidden_full", "hidden_cmr", "route_sign_full", "route_sign_cmr"]:
        pair_rows = []
        cf_obs, cf_null, cf_partial = [], [], []
        cf_within = {d: [] for d in within_domains}
        for a, b in combinations(names, 2):
            Da, Db = models[a]["rdm"][reg], models[b]["rdm"][reg]
            obs = agree(Da, Db)
            null = agree_null(Da, Db, args.n_perm, args.seed)
            nmean = float(np.nanmean(null))
            nstd = float(np.nanstd(null)) + 1e-30
            partial = partial_agree(Da, Db, Lrdm)
            same_fam = models[a]["family"] == models[b]["family"]
            within = {d: agree(sub_rdm(Da, dom_idx[d]), sub_rdm(Db, dom_idx[d]))
                      for d in within_domains}
            pair_rows.append({"a": a, "b": b, "same_family": same_fam, "agree": obs,
                              "null_mean": nmean, "null_std": float(np.nanstd(null)),
                              "z": float((obs - nmean) / nstd),
                              "partial_len": partial, "within_domain": within})
            if not same_fam:
                cf_obs.append(obs)
                cf_null.append(nmean)
                cf_partial.append(partial)
                for d in within_domains:
                    cf_within[d].append(within[d])

        def m(x):
            return float(np.nanmean(x)) if len(x) else float("nan")
        out["registers"][reg] = {
            "pairs": pair_rows,
            "cross_family_mean_agree": m(cf_obs),
            "cross_family_mean_null": m(cf_null),
            "cross_family_excess": m(cf_obs) - m(cf_null),
            "cross_family_partial_len": m(cf_partial),
            "cross_family_within_domain": {d: m(cf_within[d]) for d in within_domains},
        }

    (RESULTS_DIR / "consensus_summary.json").write_text(json.dumps(out, indent=2))

    log("")
    log("  ===== CROSS-MODEL CONSENSUS (cross-family pairs) =====")
    wd_hdr = " ".join(f"{d[:6]:>7s}" for d in within_domains)
    log(f"  {'register':18s} {'agree':>7s} {'null':>7s} {'excess':>7s} {'dlen':>7s}  | within: {wd_hdr}")
    for reg, r in out["registers"].items():
        tag = "  <-- KEY" if reg == "route_sign_cmr" else ""
        wd = " ".join(f"{r['cross_family_within_domain'][d]:>7.3f}" for d in within_domains)
        log(f"  {reg:18s} {r['cross_family_mean_agree']:>7.3f} "
            f"{r['cross_family_mean_null']:>7.3f} {r['cross_family_excess']:>+7.3f} "
            f"{r['cross_family_partial_len']:>7.3f}  | {wd}{tag}")
    log("")
    log("  dlen = agreement after partialling out prompt LENGTH.")
    log("  within = agreement restricted to one domain (matched length/format).")
    log("  NORMAL FORM => route_sign_cmr keeps high dlen AND high within-domain agree.")
    log("  If those collapse toward 0 => consensus was a length/format axis, not a")
    log("  routing normal form (prior 'STRONG SUPPORT' = common mode).")
    log("  wrote consensus_summary.json")


if __name__ == "__main__":
    main()
