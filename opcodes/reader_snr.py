#!/usr/bin/env python3
# register: online reader z-response (crystal readers on a live host)
"""P-CTL-6 — reader online SNR: do model_vsm readers detect LIVE REDEXES?

THE tier-1 feasibility gate for the control-plane path (control-plane-path.md
Section 3). The control plane ships crystal-frame READERS (per-layer
per-combinator centroids — the calibrated ``RelationalCrystalClassifier``)
bolted onto a frozen host. Everything above tier-1 (halt head, driver,
writers) assumes the readers can see the datapath's state ONLINE. Minimal
question, cleanest ground truth:

    Run the kernel-certified saturated/inert battery through the host with the
    readers attached. On a SATURATED program (``K a b`` — a live redex the
    kernel FIRES) can a reader tell it from the matched INERT program (``K a``
    — same symbol, under-applied = a NORMAL FORM)?

Ground truth = kernel ``fired_sequence`` (verbum.probes.kernel_reference):
saturated => ``fired == [c]``; inert => ``fired == []``.

============================================================================
THE LENGTH CONFOUND (s273 — why the raw halt read is not trusted)
  A saturated program is exactly ONE token longer than its inert pair
  (saturation adds an argument). At 160M the raw WHNF halt gap (inert>sat) was
  +0.207 but corr(WHNF, token-count)=-0.59 and it collapsed to +0.034 after
  removing linear length — 84% was length. Worse, WHNF is the crystal's HALT
  POLE (PC0: B,C,D neg / WHNF pos; WHNF Gram row ~ KIBC halt probs r=0.85-1.00,
  s269), so ANY "looks settled" signal (length included) sinks onto WHNF and
  fools a WHNF-specificity guard. The tell: a genuine live-redex signal is
  ANTI-PHASE (fire pole up, halt pole down); a length common-mode is IN-PHASE
  (both move together). At 160M both poles moved the SAME way (in-phase) and
  the in-battery corr(WHNF, KIBC-agg) was +0.78 — the crystal's own
  anti-correlation REVERSED by the shared length driver.

THE FIX — reducibility score, common-mode immune
  redscore(p) = z_target(p) - z_WHNF(p)     (fire pole minus halt pole)
  A signal hitting both channels equally (length as common-mode) cancels in
  the difference; only ANTI-PHASE divergence (fire up while halt down) moves
  it. Residual DIFFERENTIAL length is killed by stratifying on token count.
============================================================================
PRE-REGISTRATION (fixed BEFORE verdict — lambda measure/yardstick; scar
tissue s206, s247/s251. Smoke checks plumbing, NEVER verdicts.)

REGISTER
  reader z ``z_op(p, op)`` = classify z for ``op`` at the LAST-TOKEN crystal
  locus, meaned over crystal-bearing layers. Calibrated on the crystal LIBRARY
  vs natural-text null (trace.calibrate_register, unchanged); battery DISJOINT
  held-out (overlap reported). Run in BOTH registers (pythia crystal is attn;
  2.8b gate=0/32).

PRIMARY GATE — reducibility, length-stratified
  redscore = z_target - z_WHNF. Group programs by token count; keep strata with
  both sat and inert (length matched by construction). Statistic = mean over
  strata of [mean(redscore|sat) - mean(redscore|inert)]; within-stratum
  sat/inert label-permutation null; one-sided p<0.05 and obs>0.

ROBUSTNESS — reducibility, length-residualized
  Regress redscore on token count (linear); gate the residual sat-inert diff;
  sat-label permutation null. Cross-check on the stratified verdict.

ANTI-PHASE DIAGNOSTIC (interpretation, reported)
  fire_gap = mean(z_target|sat) - mean(z_target|inert)   (>0 = fire up on live)
  halt_gap = mean(z_WHNF|inert) - mean(z_WHNF|sat)        (>0 = halt up on NF)
  Genuine liveness => BOTH > 0 (opposite poles). Length confound => same sign.
  Plus corr(WHNF,ntok), corr(target,ntok), corr(target,WHNF): the crystal
  predicts corr(target,WHNF) < 0; a length-dominated read flips it positive.

RAW REFERENCE MODES (reported, NOT the verdict — length-confounded)
  opcode-identity (target channel sat-inert) and halt/WHNF (WHNF inert-sat),
  each with the earlier within-comb permutation + specificity gates. Kept to
  show the confound the reducibility gate corrects.

FLEET UNIVERSALITY (--fleet-scan)
  Sign test across swept models on the per-model reducibility stratified obs>0,
  plus count individually gated. Mirrors dup-register --sweep-scan.

VERDICT RULE
  Per host: usable SNR <=> reducibility STRATIFIED gate passes (mean
  aggregator). Fleet: the fleet sign test. Anti-phase must be consistent for a
  clean read. Negative = a CHEAP redirect of the control-plane tier stack.
============================================================================

Output: results/pctl6/<slug>/reader_snr.json
Fleet:  results/pctl6/fleet_summary.json (via --fleet-scan)

Usage:
  uv run python opcodes/reader_snr.py --smoke                    # plumbing (pythia-14m)
  uv run python opcodes/reader_snr.py --model EleutherAI/pythia-160m-deduped
  uv run python opcodes/reader_snr.py --model Qwen/Qwen3.6-27B --device mps   # verdict
  uv run python opcodes/reader_snr.py --fleet-scan results/pctl6     # universality

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from datetime import UTC, datetime
from math import comb
from pathlib import Path
from typing import Any

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_HERE))

import trace as TR  # noqa: E402

import capture as C  # noqa: E402
import topology as T  # noqa: E402
from classify import CRYSTAL, RelationalCrystalClassifier  # noqa: E402

from verbum.probes import kernel_reference as KR  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "pctl6"

# the 7 combinators with a clean single-fire saturated/inert pair
BATTERY_COMBINATORS = ["K", "I", "B", "C", "S", "D", "W"]
WHNF = "WHNF"


def sign_test_one_sided(n_pos: int, n: int) -> float:
    if n == 0:
        return 1.0
    return sum(comb(n, k) for k in range(n_pos, n + 1)) / 2**n


def _dprime(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    pooled = np.sqrt(0.5 * (a.var(ddof=1) + b.var(ddof=1)))
    if pooled < 1e-12:
        return float("nan")
    return float((a.mean() - b.mean()) / pooled)


def _finite(vals: list[float]) -> np.ndarray:
    a = np.asarray(vals, dtype=float)
    return a[np.isfinite(a)]


def _sel(rows: list[dict], c: str, sat: bool) -> list[dict]:
    return [r for r in rows if r["target"] == c and r["saturated"] == sat]


def _col(rows: list[dict], c: str, sat: bool, op: str, agg: str) -> np.ndarray:
    return _finite([r[agg][op] for r in _sel(rows, c, sat)])


def _col_layer(rows: list[dict], c: str, sat: bool, op: str, li: int) -> np.ndarray:
    return _finite([r["z_by_layer"][li][op] for r in _sel(rows, c, sat)
                    if li in r["z_by_layer"]])


def _tok(r: dict) -> int:
    return len(r["program"].split())


def _redscore(r: dict, agg: str) -> float:
    """Fire pole minus halt pole = z_target - z_WHNF (common-mode immune)."""
    return float(r[agg][r["target"]] - r[agg][WHNF])


def _emp_p(null: np.ndarray, obs: float) -> float:
    return (1 + int((null >= obs).sum())) / (1 + len(null))


# ── capture ──────────────────────────────────────────────────────────────────


def battery_reader_z(
    model: Any, tok: Any, topo: T.ModelTopology, register: str,
    rcc: RelationalCrystalClassifier, battery: list[KR.KernelRefProbe],
    crystal_layers: list[int], layers: list[int],
) -> list[dict]:
    agg_layers = crystal_layers if crystal_layers else list(layers)
    rows: list[dict] = []
    for i, p in enumerate(battery):
        if i % 20 == 0:
            print(f"[pctl6] [{register}]   battery {i}/{len(battery)}")
        cap = C.capture_gate(model, tok, p.program_text, topo=topo,
                             layers=layers, register=register)
        last = {li: cap.gate[li][-1] for li in layers}
        res = rcc.classify(last)
        by_layer = {li: {op: float(z) for op, z in zmap.items()}
                    for li, zmap in res.per_layer.items()}
        zmat = {op: [by_layer[li][op] for li in agg_layers if li in by_layer]
                for op in CRYSTAL}
        rows.append({
            "id": p.id, "program": p.program_text,
            "target": p.target_combinator, "saturated": p.saturated,
            "fired": p.certified_fired_seq,
            "z_mean": {op: (float(np.mean(v)) if v else float("nan"))
                       for op, v in zmat.items()},
            "z_max": {op: (float(np.max(v)) if v else float("nan"))
                      for op, v in zmat.items()},
            "z_by_layer": by_layer,
        })
    return rows


# ── raw within-comb permutation gates (confounded reference) ──────────────────


def _within_comb_perm(cells: dict, n_perm: int, rng: np.random.Generator) -> dict:
    if not cells:
        return {"observed": float("nan"), "p": 1.0, "gated": False, "n_comb": 0}
    obs = float(np.mean([a.mean() - b.mean() for a, b in cells.values()]))
    pooled = {c: (np.concatenate([a, b]), len(a)) for c, (a, b) in cells.items()}
    null = np.empty(n_perm)
    for k in range(n_perm):
        diffs = []
        for v, na in pooled.values():
            perm = rng.permutation(v)
            diffs.append(perm[:na].mean() - perm[na:].mean())
        null[k] = float(np.mean(diffs))
    return {"observed": round(obs, 5), "p": round(_emp_p(null, obs), 5),
            "gated": bool(_emp_p(null, obs) < 0.05 and obs > 0),
            "n_comb": len(cells), "n_perm": n_perm}


def _target_cells(rows: list[dict], agg: str) -> dict:
    out = {}
    for c in BATTERY_COMBINATORS:
        a, b = _col(rows, c, True, c, agg), _col(rows, c, False, c, agg)
        if len(a) and len(b):
            out[c] = (a, b)
    return out


def _whnf_cells(rows: list[dict], agg: str) -> dict:
    out = {}
    for c in BATTERY_COMBINATORS:
        inert, sat = _col(rows, c, False, WHNF, agg), _col(rows, c, True, WHNF, agg)
        if len(inert) and len(sat):
            out[c] = (inert, sat)
    return out


def _redscore_cells(rows: list[dict], agg: str) -> dict:
    """WITHIN-COMBINATOR redscore cells: per combinator (redscore | redex,
    redscore | inert). Clean minimal pair when the battery is length-matched
    (position battery) — obs>0 means the redex reads as more reducible."""
    out = {}
    for c in BATTERY_COMBINATORS:
        a = _finite([_redscore(r, agg) for r in _sel(rows, c, True)])
        b = _finite([_redscore(r, agg) for r in _sel(rows, c, False)])
        if len(a) and len(b):
            out[c] = (a, b)
    return out


# ── length-controlled reducibility gate (PRIMARY) ─────────────────────────────


def reducibility_stratified(
    rows: list[dict], agg: str, n_perm: int, rng: np.random.Generator
) -> dict:
    """redscore sat-vs-inert within token-length strata (length matched by
    construction); within-stratum label-permutation null."""
    strata: dict[int, dict[str, list[float]]] = defaultdict(
        lambda: {"sat": [], "inert": []})
    for r in rows:
        red = _redscore(r, agg)
        if np.isfinite(red):
            strata[_tok(r)]["sat" if r["saturated"] else "inert"].append(red)
    use = {L: v for L, v in strata.items() if v["sat"] and v["inert"]}
    if not use:
        return {"observed": float("nan"), "p": 1.0, "gated": False, "strata": {}}
    obs = float(np.mean([np.mean(v["sat"]) - np.mean(v["inert"])
                         for v in use.values()]))
    pooled = {L: (np.array(v["sat"] + v["inert"]), len(v["sat"]))
              for L, v in use.items()}
    null = np.empty(n_perm)
    for k in range(n_perm):
        diffs = []
        for vals, ns in pooled.values():
            perm = rng.permutation(vals)
            diffs.append(perm[:ns].mean() - perm[ns:].mean())
        null[k] = float(np.mean(diffs))
    p = _emp_p(null, obs)
    return {"observed": round(obs, 5), "p": round(p, 5),
            "gated": bool(p < 0.05 and obs > 0),
            "null_mean": round(float(null.mean()), 5),
            "n_strata": len(use), "n_perm": n_perm,
            "strata": {int(L): {"n_sat": len(v["sat"]), "n_inert": len(v["inert"]),
                                "delta": round(float(np.mean(v["sat"])
                                                     - np.mean(v["inert"])), 4)}
                       for L, v in sorted(use.items())}}


def reducibility_residualized(
    rows: list[dict], agg: str, n_perm: int, rng: np.random.Generator
) -> dict:
    """redscore with linear token-count regressed out; sat-inert diff on the
    residual; sat-label permutation null."""
    red = np.array([_redscore(r, agg) for r in rows])
    ntok = np.array([_tok(r) for r in rows], dtype=float)
    sat = np.array([r["saturated"] for r in rows])
    ok = np.isfinite(red)
    red, ntok, sat = red[ok], ntok[ok], sat[ok]
    if len(red) < 4 or sat.sum() == 0 or (~sat).sum() == 0:
        return {"observed": float("nan"), "p": 1.0, "gated": False, "slope": None}
    b = np.polyfit(ntok, red, 1)
    resid = red - np.polyval(b, ntok)
    obs = float(resid[sat].mean() - resid[~sat].mean())
    n_sat = int(sat.sum())
    idx = np.arange(len(resid))
    null = np.empty(n_perm)
    for k in range(n_perm):
        s = rng.permutation(idx)[:n_sat]
        mask = np.zeros(len(resid), bool)
        mask[s] = True
        null[k] = resid[mask].mean() - resid[~mask].mean()
    p = _emp_p(null, obs)
    return {"observed": round(obs, 5), "p": round(p, 5),
            "gated": bool(p < 0.05 and obs > 0),
            "length_slope": round(float(b[0]), 5), "n_perm": n_perm}


def antiphase_and_length(rows: list[dict], agg: str) -> dict:
    """The load-bearing interpretation: are the poles anti-phase, and how
    length-driven is the raw read?"""
    def tgt(r: dict) -> float:
        return r[agg][r["target"]]

    sat = [r for r in rows if r["saturated"]]
    inert = [r for r in rows if not r["saturated"]]
    fire_sat = _finite([tgt(r) for r in sat])
    fire_inert = _finite([tgt(r) for r in inert])
    halt_sat = _finite([r[agg][WHNF] for r in sat])
    halt_inert = _finite([r[agg][WHNF] for r in inert])
    fire_gap = float(fire_sat.mean() - fire_inert.mean())
    halt_gap = float(halt_inert.mean() - halt_sat.mean())
    tv = _finite([tgt(r) for r in rows])
    wv = _finite([r[agg][WHNF] for r in rows])
    nv = np.array([_tok(r) for r in rows], dtype=float)

    def _corr(a: np.ndarray, b: np.ndarray) -> float:
        if len(a) != len(b) or len(a) < 3 or a.std() < 1e-9 or b.std() < 1e-9:
            return float("nan")
        return round(float(np.corrcoef(a, b)[0, 1]), 3)

    return {
        "fire_gap": round(fire_gap, 4), "halt_gap": round(halt_gap, 4),
        "antiphase_consistent": bool(fire_gap > 0 and halt_gap > 0),
        "corr_target_whnf": _corr(tv, wv),
        "corr_whnf_ntok": _corr(wv, nv),
        "corr_target_ntok": _corr(tv, nv),
    }


# ── opcode / halt specificity (raw reference) ─────────────────────────────────


def opcode_specificity_perm(rows, agg, n_perm, rng):
    sat_rows = [r for r in rows if r["saturated"]]

    def adv(r, ch):
        z = r[agg]
        others = [z[o] for o in CRYSTAL if o != ch and np.isfinite(z[o])]
        return (z[ch] - float(np.mean(others))
                if np.isfinite(z[ch]) and others else float("nan"))

    obs_vals = _finite([adv(r, r["target"]) for r in sat_rows])
    if not len(obs_vals):
        return {"observed": float("nan"), "p": 1.0, "gated": False}
    obs = float(obs_vals.mean())
    null = np.empty(n_perm)
    for k in range(n_perm):
        vals = []
        for r in sat_rows:
            cand = [o for o in CRYSTAL if o != r["target"]]
            v = adv(r, cand[int(rng.integers(len(cand)))])
            if np.isfinite(v):
                vals.append(v)
        null[k] = float(np.mean(vals)) if vals else np.nan
    return {"observed": round(obs, 5), "p": round(_emp_p(null, obs), 5),
            "gated": bool(_emp_p(null, obs) < 0.05 and obs > 0)}


def per_combinator_table(rows: list[dict], agg: str) -> dict:
    tbl = {}
    for c in BATTERY_COMBINATORS:
        sat, inert = _col(rows, c, True, c, agg), _col(rows, c, False, c, agg)
        wsat, winert = _col(rows, c, True, WHNF, agg), _col(rows, c, False, WHNF, agg)
        rs = _finite([_redscore(r, agg) for r in _sel(rows, c, True)])
        ri = _finite([_redscore(r, agg) for r in _sel(rows, c, False)])
        have = len(sat) and len(inert)
        tbl[c] = {
            "opcode_delta": float(sat.mean() - inert.mean()) if have else float("nan"),
            "opcode_dprime": _dprime(sat, inert),
            "halt_gap_whnf": (float(winert.mean() - wsat.mean())
                              if len(wsat) and len(winert) else float("nan")),
            "redscore_delta": (float(rs.mean() - ri.mean())
                               if len(rs) and len(ri) else float("nan")),
            "n_tok_sat": _tok(satr[0]) if (satr := _sel(rows, c, True)) else None,
            "n_tok_inert": _tok(inr[0]) if (inr := _sel(rows, c, False)) else None,
        }
    return tbl


def per_layer_profile(rows, layers, crystal_layers):
    prof = []
    for li in layers:
        live, halt, red = [], [], []
        for c in BATTERY_COMBINATORS:
            sat = _col_layer(rows, c, True, c, li)
            inert = _col_layer(rows, c, False, c, li)
            if len(sat) and len(inert):
                live.append(sat.mean() - inert.mean())
            wsat = _col_layer(rows, c, True, WHNF, li)
            winert = _col_layer(rows, c, False, WHNF, li)
            if len(wsat) and len(winert):
                halt.append(winert.mean() - wsat.mean())
            rs = _finite([r["z_by_layer"][li][c] - r["z_by_layer"][li][WHNF]
                          for r in _sel(rows, c, True) if li in r["z_by_layer"]])
            ri = _finite([r["z_by_layer"][li][c] - r["z_by_layer"][li][WHNF]
                          for r in _sel(rows, c, False) if li in r["z_by_layer"]])
            if len(rs) and len(ri):
                red.append(rs.mean() - ri.mean())
        prof.append({
            "layer": li, "crystal": li in crystal_layers,
            "liveness_delta": round(float(np.mean(live)), 4) if live else None,
            "halt_delta": round(float(np.mean(halt)), 4) if halt else None,
            "redscore_delta": round(float(np.mean(red)), 4) if red else None,
        })
    return prof


def compute_modes(rows: list[dict], n_perm: int, seed: int, battery: str) -> dict:
    rng = np.random.default_rng(seed)
    within = _within_comb_perm(_redscore_cells(rows, "z_mean"), n_perm, rng)
    strat = reducibility_stratified(rows, "z_mean", n_perm, rng)
    resid = reducibility_residualized(rows, "z_mean", n_perm, rng)
    anti = antiphase_and_length(rows, "z_mean")
    op_live = _within_comb_perm(_target_cells(rows, "z_mean"), n_perm, rng)
    op_spec = opcode_specificity_perm(rows, "z_mean", n_perm, rng)
    ht_live = _within_comb_perm(_whnf_cells(rows, "z_mean"), n_perm, rng)
    # PRIMARY = within-combinator redscore (clean minimal pair for the
    # length-matched position battery); stratified/residualized guard the
    # length-CONFOUNDED saturation battery.
    primary = within if battery == "position" else strat
    return {
        "reducibility_mode": {
            "battery": battery,
            "within_combinator": within, "stratified": strat,
            "residualized": resid, "antiphase": anti,
            "primary_gate": "within_combinator" if battery == "position"
                            else "stratified",
            "verdict": bool(primary["gated"]),
            "clean": bool(primary["gated"] and anti["antiphase_consistent"]),
        },
        "raw_opcode_mode": {"liveness": op_live, "specificity": op_spec},
        "raw_halt_mode": {"liveness": ht_live},
        "per_combinator": per_combinator_table(rows, "z_mean"),
    }


def run_register(
    model, tok, topo, register, battery, layers, *,
    battery_kind, ppc, n_perm, z_thresh, gate_perms, seed,
) -> dict:
    rcc, calib_summ, _feats = TR.calibrate_register(
        model, tok, topo, register, layers, ppc, n_perm, z_thresh)
    crystal_layers = rcc.crystal_layers
    print(f"[pctl6] [{register}] crystal-bearing layers: "
          f"{len(crystal_layers)}/{topo.n_layers} -> {crystal_layers}")
    rows = battery_reader_z(model, tok, topo, register, rcc, battery,
                            crystal_layers, layers)
    modes = compute_modes(rows, gate_perms, seed, battery_kind)
    profile = per_layer_profile(rows, layers, set(crystal_layers))
    verdict = bool(modes["reducibility_mode"]["verdict"])
    for r in rows:
        r.pop("z_by_layer", None)
    red = modes["reducibility_mode"]
    prim = red[red["primary_gate"]]
    return {
        "register": register,
        "calibration": {
            "n_crystal_layers": len(crystal_layers),
            "crystal_layers": crystal_layers, "n_probes": calib_summ.get("n_probes"),
            "used_all_layers_fallback": not crystal_layers,
        },
        "reducibility_mode": red,
        "raw_opcode_mode": modes["raw_opcode_mode"],
        "raw_halt_mode": modes["raw_halt_mode"],
        "per_combinator": modes["per_combinator"],
        "per_layer_profile": profile,
        "verdict_usable_snr": verdict,
        "fleet_contribution": {
            "primary_gate": red["primary_gate"],
            "primary_obs": prim["observed"], "primary_p": prim["p"],
            "antiphase_consistent": red["antiphase"]["antiphase_consistent"],
            "clean": red["clean"], "gated": verdict,
        },
        "rows": rows,
    }


def _preregistration() -> dict:
    return {
        "register": "z at last-token crystal locus, meaned over crystal-bearing "
                    "layers; run in gate AND attn",
        "core_statistic": "redscore = z_target - z_WHNF (fire pole minus halt "
                          "pole; common-mode / length immune by construction)",
        "battery": "position (default): SAME tokens + length, combinator in "
                   "HEAD (redex, fires) vs ARGUMENT (normal form) position — "
                   "isolates liveness from symbol-presence AND length. "
                   "saturation: under-applied inert (length-confounded, guarded "
                   "by stratified/residualized gates).",
        "primary_gate": "position battery: WITHIN-COMBINATOR redscore redex-vs-"
                        "argpos (true minimal pair, length+token matched); "
                        "within-comb label-perm null; p<0.05 and obs>0. "
                        "saturation battery: length-STRATIFIED redscore.",
        "robustness_gates": "length-stratified + length-residualized redscore "
                            "(guard the saturation battery; corroborate position)",
        "antiphase_diagnostic": "fire_gap (z_target redex-inert)>0 AND halt_gap "
                                "(z_WHNF inert-redex)>0 = genuine anti-phase; "
                                "same-sign = common-mode; corr(target,WHNF)<0 "
                                "expected (crystal PC0)",
        "raw_reference_modes": "opcode-identity + halt/WHNF within-comb (raw)",
        "fleet_universality": "sign test across swept models on the per-model "
                              "primary obs>0 (--fleet-scan)",
        "verdict_rule": "per host: primary gate passes; 'clean' also requires "
                        "anti-phase consistent",
    }


def fleet_scan(root: Path) -> dict:
    models = []
    for jp in sorted(root.glob("*/reader_snr.json")):
        d = json.loads(jp.read_text(encoding="utf-8"))
        if d.get("smoke"):
            continue
        for reg, gate in d.get("registers", {}).items():
            fc = gate.get("fleet_contribution", {})
            models.append({"model": d.get("model"), "register": reg,
                           "primary_obs": fc.get("primary_obs"),
                           "antiphase_consistent": fc.get("antiphase_consistent"),
                           "clean": bool(fc.get("clean")),
                           "gated": bool(fc.get("gated"))})
    obs = [m["primary_obs"] for m in models
           if isinstance(m["primary_obs"], (int, float))
           and np.isfinite(m["primary_obs"])]
    npos = sum(1 for v in obs if v > 0)
    p = sign_test_one_sided(npos, len(obs))
    return {
        "instrument": "P-CTL-6 fleet universality (reducibility)",
        "n_entries": len(models), "n": len(obs), "n_pos": npos,
        "sign_p": round(p, 6), "fleet_gated": bool(p < 0.05),
        "n_individually_gated": sum(1 for m in models if m["gated"]),
        "n_clean": sum(1 for m in models if m["clean"]),
        "models": models, "timestamp_utc": datetime.now(UTC).isoformat(),
    }


def _print_register(reg: str, d: dict, n_layers: int, smoke: bool) -> None:
    red = d["reducibility_mode"]
    wc, st, rs, an = (red["within_combinator"], red["stratified"],
                      red["residualized"], red["antiphase"])
    prim = red["primary_gate"]
    print(f"-- {reg}: crystal={d['calibration']['n_crystal_layers']}/{n_layers} "
          f"| battery={red['battery']} primary={prim}")
    star = "*" if prim == "within_combinator" else " "
    print(f"  {star}REDUCIBILITY within-comb : obs={wc['observed']:+.4f} p={wc['p']} "
          f"{'PASS' if wc['gated'] else 'fail'}  ({wc.get('n_comb', 0)} comb)")
    star = "*" if prim == "stratified" else " "
    print(f"  {star}REDUCIBILITY stratified  : obs={st['observed']:+.4f} p={st['p']} "
          f"{'PASS' if st['gated'] else 'fail'}  ({st.get('n_strata', 0)} strata)")
    print(f"   REDUCIBILITY residualized: obs={rs['observed']:+.4f} p={rs['p']} "
          f"{'PASS' if rs['gated'] else 'fail'}  (len_slope={rs.get('length_slope')})")
    print(f"   anti-phase: fire={an['fire_gap']:+.3f} halt={an['halt_gap']:+.3f} "
          f"consistent={an['antiphase_consistent']} | "
          f"corr(tgt,WHNF)={an['corr_target_whnf']} "
          f"corr(WHNF,tok)={an['corr_whnf_ntok']}")
    ro, rh = d["raw_opcode_mode"], d["raw_halt_mode"]
    print(f"   [raw ref] opcode obs={ro['liveness']['observed']:+.4f} "
          f"p={ro['liveness']['p']} | halt obs={rh['liveness']['observed']:+.4f} "
          f"p={rh['liveness']['p']}")
    print(f"   VERDICT usable-SNR: {'YES' if d['verdict_usable_snr'] else 'NO'}"
          f"  (clean={red['clean']})"
          + ("  PROVISIONAL smoke" if smoke else ""))
    for c in BATTERY_COMBINATORS:
        pc = d["per_combinator"][c]
        print(f"     {c}: redscore_Delta={pc['redscore_delta']:+.3f} "
              f"(op={pc['opcode_delta']:+.3f} halt={pc['halt_gap_whnf']:+.3f})")


def main() -> None:
    ap = argparse.ArgumentParser(description="P-CTL-6 reader online SNR")
    ap.add_argument("--model", default="Qwen/Qwen3.6-27B")
    ap.add_argument("--device", default="mps", choices=["cpu", "mps", "cuda"])
    ap.add_argument("--registers", default="gate,attn")
    ap.add_argument("--battery", default="position",
                    choices=["position", "saturation"],
                    help="position: length+token-matched redex-vs-argpos "
                         "(clean, default); saturation: under-applied inert "
                         "(length-confounded reference)")
    ap.add_argument("--n-fillers", type=int, default=4)
    ap.add_argument("--probes-per-comb", type=int, default=None)
    ap.add_argument("--n-perm", type=int, default=300)
    ap.add_argument("--gate-perms", type=int, default=2000)
    ap.add_argument("--z", type=float, default=3.0)
    ap.add_argument("--seed", type=int, default=273)
    ap.add_argument("--fleet-scan", metavar="DIR", default=None)
    ap.add_argument("--smoke", action="store_true",
                    help="pythia-14m on cpu; PLUMBING ONLY, no verdicts")
    args = ap.parse_args()

    if args.fleet_scan is not None:
        root = Path(args.fleet_scan)
        summary = fleet_scan(root)
        (root / "fleet_summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2))
        print(f"[pctl6] wrote {root / 'fleet_summary.json'}")
        return

    if args.smoke:
        args.model, args.device = "EleutherAI/pythia-14m-deduped", "cpu"
    ppc = 15 if args.smoke else args.probes_per_comb
    n_perm = 120 if args.smoke else args.n_perm
    gate_perms = 500 if args.smoke else args.gate_perms
    want = [r.strip() for r in args.registers.split(",") if r.strip()]

    t0 = time.time()
    model, tok = TR.load(args.model, args.device)
    topo = T.detect_topology(model, model.config)
    print(f"[pctl6] {topo.summary()}")
    layers = list(range(topo.n_layers))

    battery = (KR.position_battery(args.n_fillers) if args.battery == "position"
               else KR.saturated_inert_battery(args.n_fillers))
    lib_texts = {p.prompt.strip() for p in TR.crystal_probes()
                 if p.combinator in CRYSTAL}
    overlap = sorted(lib_texts & {p.program_text.strip() for p in battery})
    print(f"[pctl6] battery={args.battery} n={len(battery)} "
          f"(redex={sum(p.saturated for p in battery)}, "
          f"inert={sum(not p.saturated for p in battery)}) | "
          f"calib-overlap={len(overlap)} (held-out)")

    registers = []
    for r in want:
        if r == "gate" and not topo.traceable:
            print(f"[pctl6] gate register unavailable ({topo.read_register}); skip.")
            continue
        if r == "attn" and not topo.attn_traceable:
            print("[pctl6] attn register unavailable; skip.")
            continue
        registers.append(r)
    if not registers:
        print(f"[pctl6] REFUSED: no traceable register on {topo.arch}.")
        sys.exit(2)

    per_register = {}
    for reg in registers:
        per_register[reg] = run_register(
            model, tok, topo, reg, battery, layers,
            battery_kind=args.battery, ppc=ppc, n_perm=n_perm, z_thresh=args.z,
            gate_perms=gate_perms, seed=args.seed)

    elapsed = round(time.time() - t0, 1)
    out = {
        "instrument": "P-CTL-6 reader online SNR",
        "model": args.model, "device": args.device, "smoke": args.smoke,
        "note": ("SMOKE: pythia-14m plumbing only — gates PROVISIONAL, NOT the "
                 "P-CTL-6 answer." if args.smoke else "verdict run"),
        "topology": {"arch": topo.arch, "n_layers": topo.n_layers,
                     "register_kind": topo.register},
        "battery_kind": args.battery,
        "n_fillers": args.n_fillers, "battery_combinators": BATTERY_COMBINATORS,
        "disjointness": {"n_calib_prompts": len(lib_texts),
                         "n_battery": len(battery), "overlap": len(overlap),
                         "overlapping_texts": overlap},
        "preregistration": _preregistration(),
        "calibration": {"probes_per_comb": ppc, "n_perm": n_perm,
                        "gate_perms": gate_perms, "z_thresh": args.z,
                        "seed": args.seed},
        "registers": {reg: {k: v for k, v in d.items() if k != "rows"}
                      for reg, d in per_register.items()},
        "battery_rows": {reg: d["rows"] for reg, d in per_register.items()},
        "elapsed_s": elapsed, "timestamp_utc": datetime.now(UTC).isoformat(),
    }
    slug = args.model.split("/")[-1].lower().replace(".", "-")
    out_dir = RESULTS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "reader_snr.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8")

    print("=" * 72)
    print(f"P-CTL-6 READER SNR — {args.model}"
          + ("  [SMOKE — PROVISIONAL]" if args.smoke else ""))
    print("=" * 72)
    for reg, d in per_register.items():
        _print_register(reg, d, topo.n_layers, args.smoke)
    print("=" * 72)
    print(f"[pctl6] wrote {out_dir / 'reader_snr.json'} ({elapsed}s)")


if __name__ == "__main__":
    main()
