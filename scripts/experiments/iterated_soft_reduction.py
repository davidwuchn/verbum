#!/usr/bin/env python3
"""FROZEN §P-ITERATED-SOFT-REDUCTION — does reduction WORK scale with the COUNT
in BOTH math engines? (s345, Michael GO; freeze commit 078af23f, BEFORE data.)

H1 (unification): one iterated-soft-β engine, two encodings — rotation-by-Nδ =
N soft-β steps; work ∝ count in BOTH the linear/FFN engine and the circular/
attention engine. H0 (audit-favored): rotation is a single learned map (angle ∝ N,
work FLAT); the S/Y arith read is categorical, not graded.

Discriminators (register named per claim, λ measure):
  D1 linear arm (FFN gate register = routing/count ✓): work = S∪Y recruitment
     share over crystal-bearing layers (audited opcodes/ reader). Count ladder,
     single-token operands, length-matched within template. ρ_lin = mean
     per-template Spearman(SY-share, N); shuffled-N perm null; gate ρ≥0.3 ∧ p<.05.
  D2 circular arm (residual trajectory; depth-like observable on purpose):
     work = accumulation depth L50 — day-circle basis RE-DERIVED IN-RUN (s128
     method; instrument gate: circular ordering == 1.0 at some L ≤ gate-layer),
     per-item angular progress from base-day anchor toward answer-day anchor,
     L50 = first (fractional) layer where normalized monotone progress ≥ 0.5.
     Iterated-β ⇒ L50 rises with N; learned matrix ⇒ trajectories COLLAPSE,
     L50 flat. ρ_circ = Spearman(L50, N); nulls = shuffled-N AND explicit
     shape-collapse (matrix) null; gates ρ≥0.3 ∧ p<.05 ∧ ΔL50(NmaxvsNmin)≥1 ∧
     matrix-null beaten p<.05. Secondary (non-gating): logit-lens resolution
     depth; gate-register read of the circular battery (expect FFN-silent, s344).
  D3 V-patch at day-token positions, band-swept early/zone/late (route-early
     guard, s252) = β-QUALIFIER, not a gate. Classes: V-CARRIED-IN-ZONE /
     V-CARRIED-EARLY-ONLY / V-INERT. Operationalized (frozen here, before data):
     a band CARRIES iff donor-answer adoption ≥ 0.3 ∧ (adoption − noop) ≥ 0.2.

Verdict tree (frozen a-priori mass):
  TWO-ENGINES (LINEAR-ONLY) 35 (modal) | NO-SCALING 25 | ONE-ENGINE 20 |
  CIRCULAR-ONLY 5 | VOID 15 (circle never forms / calibration fails / det ≠ 0).

Honesty bounds (frozen): depth-scaling is ONE-DIRECTIONAL (flat kills iterated-β;
scaling is consistent-with, not proof); gate register blind to {B,C}; attn soft;
small ladders; shuffled-N is the confound guard.

--validate runs 6 planted worlds through the REAL analyse path (s331 lesson).

Usage:
  uv run python scripts/experiments/iterated_soft_reduction.py --validate
  uv run python scripts/experiments/iterated_soft_reduction.py --smoke \
      --model Qwen/Qwen3-0.6B
  uv run python scripts/experiments/iterated_soft_reduction.py --model Qwen/Qwen3-14B

License: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "opcodes"))

RESULTS_DIR = _ROOT / "results" / "p_iterated_soft_reduction_s345"

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ---------------------------------------------------------------------------
# Frozen corpus
# ---------------------------------------------------------------------------
LIN_TEMPLATES: dict[str, str] = {
    "add_sym": "{n} + {m} =",
    "add_nl": "{n} plus {m} equals",
    "mul_sym": "{n} * {m} =",
    "mul_nl": "{n} times {m} equals",
    "succ_a": "One more than {n} is",
    "succ_b": "The number after {n} is",
}
LIN_N = list(range(2, 10))          # single-token operands, length-matched
LIN_M = [2, 3]                      # fixed second operand (succ ignores m)
CIRC_N = list(range(1, 7))          # 1..6 (mod-7 nontrivial)
CIRC_TEMPLATE = "{n} days after {day} is"
ANCHOR_TEMPLATE = "Today is {day}"

# Frozen gates
RHO_FLOOR = 0.3
P_FLOOR = 0.05
L50_SLOPE_FLOOR = 1.0
CIRCLE_GATE_FRAC = 0.40             # circle must form by this fraction of depth
ADOPT_CARRY = 0.30                  # D3 qualifier thresholds (frozen pre-data)
ADOPT_MARGIN = 0.20


def build_lin_items() -> list[dict]:
    items = []
    for tname, tmpl in LIN_TEMPLATES.items():
        for m in LIN_M:
            for n in LIN_N:
                if tname.startswith("succ") and m != LIN_M[0]:
                    continue  # succ has no second operand; one copy only
                items.append({"template": tname, "n": n, "m": m,
                              "prompt": tmpl.format(n=n, m=m)})
    return items


def build_circ_items() -> list[dict]:
    items = []
    for n in CIRC_N:
        for di, day in enumerate(DAYS):
            items.append({"n": n, "base": day, "answer": DAYS[(di + n) % 7],
                          "prompt": CIRC_TEMPLATE.format(n=n, day=day)})
    return items


# ---------------------------------------------------------------------------
# Pure statistics (no model) — the REAL analyse path
# ---------------------------------------------------------------------------
def _rankdata(x: np.ndarray) -> np.ndarray:
    """Average ranks (ties averaged)."""
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=float)
    sx = x[order]
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and sx[j + 1] == sx[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = _rankdata(np.asarray(x, float)), _rankdata(np.asarray(y, float))
    rx -= rx.mean()
    ry -= ry.mean()
    den = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / den) if den > 0 else 0.0


def perm_p(stat_fn, labels: np.ndarray, obs: float, n_perm: int,
           rng: np.random.Generator) -> float:
    """One-sided p: fraction of label-shuffled stats >= observed."""
    hits = 1
    for _ in range(n_perm):
        if stat_fn(rng.permutation(labels)) >= obs:
            hits += 1
    return hits / (n_perm + 1)


def normalized_monotone(traj: np.ndarray) -> np.ndarray:
    """Monotone (cummax) progress normalized by its final value."""
    m = np.maximum.accumulate(np.asarray(traj, float))
    final = m[-1]
    if final <= 1e-9:
        return np.zeros_like(m)
    return np.clip(m / final, 0.0, 1.0)


def l50_of(traj: np.ndarray) -> float:
    """First fractional index where normalized monotone progress >= 0.5."""
    nm = normalized_monotone(traj)
    idx = np.argmax(nm >= 0.5)
    if nm[idx] < 0.5:
        return float(len(nm) - 1)
    if idx == 0:
        return 0.0
    lo, hi = nm[idx - 1], nm[idx]
    frac = (0.5 - lo) / (hi - lo) if hi > lo else 0.0
    return float(idx - 1 + frac)


def shape_collapse_p(trajs: np.ndarray, ns: np.ndarray, n_perm: int,
                     rng: np.random.Generator) -> tuple[float, float]:
    """Explicit matrix (shape-collapse) null. Statistic = mean over N-groups of
    mean |group-mean normalized trajectory − pooled mean trajectory|. Under the
    learned-matrix world all N share one shape → statistic ~ its shuffled-N
    distribution; iterated-β diverges beyond it."""
    nm = np.stack([normalized_monotone(t) for t in trajs])
    pooled = nm.mean(axis=0)

    def stat(labels: np.ndarray) -> float:
        vals = []
        for n in np.unique(labels):
            g = nm[labels == n]
            if len(g):
                vals.append(float(np.abs(g.mean(axis=0) - pooled).mean()))
        return float(np.mean(vals))

    obs = stat(ns)
    p = perm_p(stat, ns, obs, n_perm, rng)
    return obs, p


def analyse(data: dict, n_perm: int = 5000, seed: int = 0) -> dict:
    """The frozen analyse path. `data` schema (all plain python/numpy):
      lin_items:  [{template, n, sy_share}]
      circ_items: [{n, traj: [progress per layer]}]
      circle:     {formed: bool, circle_layer: int|None, n_layers: int}
      determinism:{dev: float}
      calibration:{ok: bool}
      patch:      {noop: float, bands: {early: float, zone: float, late: float}}
                  | None  (adoption rates)
      secondary:  passthrough dict (non-gating)
    """
    rng = np.random.default_rng(seed)
    out: dict[str, Any] = {}

    # --- VOID gates -------------------------------------------------------
    void_reasons = []
    if not data.get("calibration", {}).get("ok", True):
        void_reasons.append("gate-register calibration failed")
    if not data.get("circle", {}).get("formed", False):
        void_reasons.append("day circle never forms")
    if data.get("determinism", {}).get("dev", 0.0) != 0.0:
        void_reasons.append(f"determinism dev {data['determinism']['dev']}")

    # --- D1 linear --------------------------------------------------------
    lin = data["lin_items"]
    templates = sorted({it["template"] for it in lin})
    per_t = {}
    all_pairs: list[tuple[np.ndarray, np.ndarray]] = []
    for t in templates:
        ns = np.array([it["n"] for it in lin if it["template"] == t], float)
        sy = np.array([it["sy_share"] for it in lin if it["template"] == t], float)
        per_t[t] = spearman(sy, ns)
        all_pairs.append((ns, sy))
    rho_lin = float(np.mean(list(per_t.values())))

    def lin_stat(perm_ns_concat: np.ndarray) -> float:
        # permute N labels WITHIN template strata
        vals, off = [], 0
        for ns, sy in all_pairs:
            k = len(ns)
            vals.append(spearman(sy, perm_ns_concat[off:off + k]))
            off += k
        return float(np.mean(vals))

    # stratified permutation: shuffle within each template block
    def lin_perm_p() -> float:
        hits = 1
        for _ in range(n_perm):
            shuffled = np.concatenate([rng.permutation(ns) for ns, _ in all_pairs])
            if lin_stat(shuffled) >= rho_lin:
                hits += 1
        return hits / (n_perm + 1)

    p_lin = lin_perm_p()
    d1_pass = (rho_lin >= RHO_FLOOR) and (p_lin < P_FLOOR)
    out["d1"] = {"rho_lin": round(rho_lin, 4), "p_lin": round(p_lin, 5),
                 "per_template_rho": {k: round(v, 4) for k, v in per_t.items()},
                 "pass": bool(d1_pass)}

    # --- D2 circular ------------------------------------------------------
    circ = data["circ_items"]
    ns_c = np.array([it["n"] for it in circ], float)
    trajs = np.stack([np.asarray(it["traj"], float) for it in circ])
    l50s = np.array([l50_of(t) for t in trajs])
    rho_circ = spearman(l50s, ns_c)
    p_circ = perm_p(lambda lab: spearman(l50s, lab), ns_c, rho_circ, n_perm, rng)
    lo_mean = float(l50s[ns_c == ns_c.min()].mean())
    hi_mean = float(l50s[ns_c == ns_c.max()].mean())
    slope = hi_mean - lo_mean
    shape_obs, shape_p = shape_collapse_p(trajs, ns_c, n_perm, rng)
    d2_pass = ((rho_circ >= RHO_FLOOR) and (p_circ < P_FLOOR)
               and (slope >= L50_SLOPE_FLOOR) and (shape_p < P_FLOOR))
    out["d2"] = {"rho_circ": round(rho_circ, 4), "p_circ": round(p_circ, 5),
                 "l50_mean_by_n": {int(n): round(float(l50s[ns_c == n].mean()), 3)
                                   for n in np.unique(ns_c)},
                 "slope_l50": round(slope, 3),
                 "shape_divergence": round(shape_obs, 5),
                 "shape_collapse_null_p": round(shape_p, 5),
                 "pass": bool(d2_pass)}

    # --- D3 qualifier -----------------------------------------------------
    patch = data.get("patch")
    qualifier = "UNRESOLVED"
    if patch is not None:
        noop = patch.get("noop", 0.0)
        carries = {b: (v >= ADOPT_CARRY and (v - noop) >= ADOPT_MARGIN)
                   for b, v in patch["bands"].items()}
        if carries.get("zone"):
            qualifier = "V-CARRIED-IN-ZONE"
        elif carries.get("early"):
            qualifier = "V-CARRIED-EARLY-ONLY"
        else:
            qualifier = "V-INERT"
        out["d3"] = {"noop": noop, "bands": patch["bands"], "carries": carries,
                     "qualifier": qualifier}
    else:
        out["d3"] = {"qualifier": qualifier}

    # --- Frozen verdict tree ---------------------------------------------
    if void_reasons:
        verdict = "VOID"
    elif d1_pass and d2_pass:
        verdict = ("ONE-ENGINE(beta-confirmed)"
                   if qualifier == "V-CARRIED-IN-ZONE" else "ONE-ENGINE(qualified)")
    elif d1_pass and not d2_pass:
        verdict = "TWO-ENGINES(LINEAR-ONLY)"
    elif d2_pass and not d1_pass:
        verdict = "CIRCULAR-ONLY"
    else:
        verdict = "NO-SCALING"
    out["void_reasons"] = void_reasons
    out["verdict"] = verdict
    out["secondary"] = data.get("secondary", {})
    return out


# ---------------------------------------------------------------------------
# Planted worlds (--validate) — synthetic data through the REAL analyse path
# ---------------------------------------------------------------------------
def _plant_common(rng: np.random.Generator, n_layers: int = 24) -> dict:
    return {"circle": {"formed": True, "circle_layer": 8, "n_layers": n_layers},
            "determinism": {"dev": 0.0}, "calibration": {"ok": True}}


def _plant_lin(rng: np.random.Generator, scaling: bool,
               nuisance: bool = False) -> list[dict]:
    items = []
    for it in build_lin_items():
        base = 0.25
        if scaling:
            base += 0.04 * it["n"]
        if nuisance:
            base += 0.30 * rng.random()      # strong non-N driver
        items.append({"template": it["template"], "n": it["n"],
                      "sy_share": max(0.0, base + rng.normal(0, 0.01))})
    return items


def _plant_circ(rng: np.random.Generator, world: str, n_layers: int = 24) -> list[dict]:
    """world: 'iterated' (depth ∝ N) | 'matrix' (one shape, all N) | 'noise'."""
    items = []
    ls = np.arange(n_layers, dtype=float)
    for it in build_circ_items():
        if world == "iterated":
            mid = 6.0 + 1.6 * it["n"]
        elif world == "matrix":
            mid = 10.0
        else:
            mid = rng.uniform(4, 18)
        traj = 1.0 / (1.0 + np.exp(-(ls - mid) / 1.5))
        traj += rng.normal(0, 0.01, size=n_layers)
        items.append({"n": it["n"], "traj": traj.tolist()})
    return items


def run_validate(n_perm: int = 800) -> int:
    rng = np.random.default_rng(7)
    worlds: list[tuple[str, dict, Any]] = []

    w = _plant_common(rng)
    w["lin_items"] = _plant_lin(rng, scaling=True)
    w["circ_items"] = _plant_circ(rng, "iterated")
    w["patch"] = {"noop": 0.02, "bands": {"early": 0.10, "zone": 0.85, "late": 0.05}}
    worlds.append(("ITERATED→ONE-ENGINE(beta-confirmed)", w,
                   lambda v: v == "ONE-ENGINE(beta-confirmed)"))

    w = _plant_common(rng)
    w["lin_items"] = _plant_lin(rng, scaling=False)
    w["circ_items"] = _plant_circ(rng, "matrix")
    worlds.append(("MATRIX→NO-SCALING", w, lambda v: v == "NO-SCALING"))

    w = _plant_common(rng)
    w["lin_items"] = _plant_lin(rng, scaling=True)
    w["circ_items"] = _plant_circ(rng, "matrix")
    w["patch"] = {"noop": 0.02, "bands": {"early": 0.60, "zone": 0.05, "late": 0.02}}
    worlds.append(("LINEAR-ONLY→TWO-ENGINES", w,
                   lambda v: v == "TWO-ENGINES(LINEAR-ONLY)"))

    # CONFOUND adversary: strong non-N nuisance drives work; N carries nothing.
    w = _plant_common(rng)
    w["lin_items"] = _plant_lin(rng, scaling=False, nuisance=True)
    w["circ_items"] = _plant_circ(rng, "noise")
    worlds.append(("CONFOUND→must NOT pass", w, lambda v: v == "NO-SCALING"))

    w = _plant_common(rng)
    w["lin_items"] = _plant_lin(rng, scaling=False)
    w["circ_items"] = _plant_circ(rng, "noise")
    worlds.append(("NOISE→NO-SCALING", w, lambda v: v == "NO-SCALING"))

    w = _plant_common(rng)
    w["circle"] = {"formed": False, "circle_layer": None, "n_layers": 24}
    w["lin_items"] = _plant_lin(rng, scaling=True)
    w["circ_items"] = _plant_circ(rng, "iterated")
    worlds.append(("NO-CIRCLE→VOID", w, lambda v: v == "VOID"))

    n_pass = 0
    for name, data, check in worlds:
        res = analyse(data, n_perm=n_perm, seed=11)
        ok = check(res["verdict"])
        n_pass += ok
        extra = ""
        if "CONFOUND" in name:
            extra = (f" | lin p={res['d1']['p_lin']} (want ≥{P_FLOOR})"
                     f" circ pass={res['d2']['pass']} (want False)")
            ok = ok and res["d1"]["p_lin"] >= P_FLOOR and not res["d2"]["pass"]
        print(f"[validate] {'✅' if ok else '❌'} {name}: verdict={res['verdict']}"
              f" (ρ_lin={res['d1']['rho_lin']} p={res['d1']['p_lin']} |"
              f" ρ_circ={res['d2']['rho_circ']} p={res['d2']['p_circ']}"
              f" slope={res['d2']['slope_l50']}"
              f" shape_p={res['d2']['shape_collapse_null_p']}){extra}")
    print(f"[validate] {n_pass}/{len(worlds)} planted worlds pass")
    return 0 if n_pass == len(worlds) else 1


# ---------------------------------------------------------------------------
# Model capture
# ---------------------------------------------------------------------------
def circular_ordering(points: np.ndarray) -> float:
    """PCA-2 the 7 anchors; fraction of days in correct cyclic order (best
    alignment over rotation × reflection). 1.0 = perfect circle order."""
    x = points - points.mean(axis=0)
    _, _, vt = np.linalg.svd(x, full_matrices=False)
    p2 = x @ vt[:2].T
    ang = np.arctan2(p2[:, 1], p2[:, 0])
    order = list(np.argsort(ang))
    best = 0
    n = len(order)
    for direction in (order, order[::-1]):
        for shift in range(n):
            seq = direction[shift:] + direction[:shift]
            best = max(best, sum(1 for i, d in enumerate(seq) if d == i))
    return best / n


def _wrap(a: float) -> float:
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def capture_all(args) -> tuple[dict, dict]:
    from trace import calibrate_register  # opcodes/

    import capture as C  # opcodes/ (sys.path)
    import topology as T  # opcodes/
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.bfloat16, low_cpu_mem_usage=True).eval()
    if args.device != "cpu":
        model = model.to(args.device)
    topo = T.detect_topology(model, model.config)
    n_layers = topo.n_layers
    print(f"[isr] {args.model} | {topo.summary()}")

    meta: dict[str, Any] = {
        "probe": "P-ITERATED-SOFT-REDUCTION", "freeze_commit": "078af23f",
        "model": args.model, "device": args.device,
        "model_revision": getattr(model.config, "_commit_hash", None),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=_ROOT,
                                  capture_output=True, text=True).stdout.strip(),
        "n_perm": args.n_perm, "z_thresh": args.z, "smoke": bool(args.smoke),
        "lib_versions": {"torch": torch.__version__,
                         "numpy": np.__version__},
        "sampling": "greedy/argmax readout only; no generation",
    }
    lin_items = build_lin_items()
    circ_items = build_circ_items()
    meta["corpus_hash"] = hashlib.sha256(json.dumps(
        [lin_items, circ_items], sort_keys=True).encode()).hexdigest()[:8]

    data: dict[str, Any] = {"secondary": {}}

    # ---- D1: gate-register calibration + SY-share ------------------------
    calibration_ok = True
    if topo.traceable:
        layers = list(range(n_layers))
        ppc = 15 if args.smoke else args.probes_per_comb
        cal_perm = 120 if args.smoke else 300
        try:
            rcc, _summ, _ = calibrate_register(
                model, tok, topo, "gate", layers, ppc, cal_perm, args.z)
            crystal = sorted(rcc.crystal_layers)
            calibration_ok = len(crystal) > 0
        except Exception as e:  # calibration failure → VOID, not crash
            print(f"[isr] calibration FAILED: {e}")
            calibration_ok, crystal, rcc = False, [], None
    else:
        calibration_ok, crystal, rcc = False, [], None
    print(f"[isr] crystal-bearing layers: {len(crystal)}/{n_layers}")

    def sy_share_of(prompt: str) -> tuple[float, int]:
        cap = C.capture_gate(model, tok, prompt, topo=topo,
                             layers=list(range(n_layers)), register="gate")
        sy = tot = 0
        for pos in range(1, cap.n_tokens):
            gate_tok = {li: cap.gate[li][pos] for li in range(n_layers)}
            res = rcc.classify(gate_tok)
            for li in crystal:
                zmap = res.per_layer.get(li)
                if not zmap:
                    continue
                op = max(zmap, key=zmap.get)
                if zmap[op] > args.z:
                    tot += 1
                    if op in ("S", "Y"):
                        sy += 1
        return (sy / tot if tot else 0.0), tot

    d1_items = []
    if calibration_ok:
        for i, it in enumerate(lin_items):
            share, fires = sy_share_of(it["prompt"])
            d1_items.append({**it, "sy_share": share, "fires": fires})
            if i % 20 == 0:
                print(f"[isr] D1 {i}/{len(lin_items)}")
        # secondary: circular battery on the gate register (expect FFN-silent)
        circ_sy = [sy_share_of(it["prompt"]) for it in circ_items[:14]]
        data["secondary"]["circ_gate_sy_share"] = round(
            float(np.mean([s for s, _ in circ_sy])), 4)
        data["secondary"]["circ_gate_mean_fires"] = round(
            float(np.mean([f for _, f in circ_sy])), 2)
    else:
        d1_items = [{**it, "sy_share": 0.0, "fires": 0} for it in lin_items]
    data["lin_items"] = d1_items
    data["calibration"] = {"ok": bool(calibration_ok),
                           "n_crystal_layers": len(crystal)}

    # ---- D2: day-circle anchors + item trajectories ----------------------
    torch.manual_seed(0)

    def hiddens(prompt: str) -> np.ndarray:
        ids = tok(prompt, return_tensors="pt").input_ids.to(model.device)
        with torch.no_grad():
            out = model(ids, output_hidden_states=True)
        # (n_layers+1, d) last token, skip embedding row
        return np.stack([h[0, -1].float().cpu().numpy()
                         for h in out.hidden_states[1:]])

    anchors = {d: hiddens(ANCHOR_TEMPLATE.format(day=d)) for d in DAYS}
    ordering_by_layer, sv_top2_by_layer, planes = {}, {}, {}
    for li in range(n_layers):
        pts = np.stack([anchors[d][li] for d in DAYS])
        ordering_by_layer[li] = circular_ordering(pts)
        c = pts - pts.mean(axis=0)
        _, sv, vt = np.linalg.svd(c, full_matrices=False)
        tot = float((sv ** 2).sum())
        sv_top2_by_layer[li] = float((sv[:2] ** 2).sum() / tot) if tot > 0 else 0.0
        planes[li] = (pts.mean(axis=0), vt[:2])
    gate_layer = int(np.ceil(CIRCLE_GATE_FRAC * n_layers))
    formed_layers = [li for li in range(gate_layer + 1)
                     if ordering_by_layer[li] == 1.0]
    formed = len(formed_layers) > 0
    circle_layer = formed_layers[0] if formed else None
    data["circle"] = {"formed": bool(formed), "circle_layer": circle_layer,
                      "n_layers": n_layers,
                      "ordering_by_layer": {str(k): round(v, 3)
                                            for k, v in ordering_by_layer.items()},
                      # s128 SNAP diagnostic: lexical circle at L0 vs
                      # computational crystallization (SV top-2 share jump)
                      "sv_top2_share_by_layer": {str(k): round(v, 4)
                                                 for k, v in
                                                 sv_top2_by_layer.items()}}
    print(f"[isr] day circle formed={formed} at L{circle_layer} "
          f"(gate ≤ L{gate_layer})")

    def angle_at(vec: np.ndarray, li: int) -> float:
        mean, basis = planes[li]
        p = (vec - mean) @ basis.T
        return float(np.arctan2(p[1], p[0]))

    day_first_tok = [tok.encode(" " + d)[0] for d in DAYS]

    def traj_of(prompt: str, base: str, answer: str) -> tuple[list[float], list[int]]:
        h = hiddens(prompt)
        prog, reso = [], []
        for li in range(circle_layer or 0, n_layers):
            th = angle_at(h[li], li)
            tb = angle_at(anchors[base][li], li)
            ta = angle_at(anchors[answer][li], li)
            denom = _wrap(ta - tb)
            num = _wrap(th - tb)
            prog.append(float(np.clip(num / denom, -0.5, 1.5))
                        if abs(denom) > 1e-6 else 0.0)
        # secondary logit-lens: rank of answer among 7 day tokens per layer
        with torch.no_grad():
            ids = tok(prompt, return_tensors="pt").input_ids.to(model.device)
            out = model(ids, output_hidden_states=True)
            norm = model.model.norm
            for li in range(n_layers):
                z = norm(out.hidden_states[li + 1][:, -1])
                logits = model.lm_head(z)[0, day_first_tok].float().cpu().numpy()
                reso.append(int(np.argmax(logits)))
        return prog, reso

    d2_items = []
    if formed:
        ans_idx = {d: i for i, d in enumerate(DAYS)}
        reso_layers = []
        for i, it in enumerate(circ_items):
            prog, reso = traj_of(it["prompt"], it["base"], it["answer"])
            d2_items.append({**it, "traj": prog})
            correct = ans_idx[it["answer"]]
            first = next((li for li, r in enumerate(reso) if r == correct
                          and all(x == correct for x in reso[li:])), n_layers)
            reso_layers.append((it["n"], first))
            if i % 10 == 0:
                print(f"[isr] D2 {i}/{len(circ_items)}")
        ns = np.array([n for n, _ in reso_layers], float)
        rs = np.array([r for _, r in reso_layers], float)
        data["secondary"]["logit_lens_reso_rho"] = round(spearman(rs, ns), 4)
        data["secondary"]["logit_lens_reso_by_n"] = {
            int(n): round(float(rs[ns == n].mean()), 2) for n in np.unique(ns)}
        # determinism: re-capture 5 items
        dev = 0.0
        for it in circ_items[:5]:
            p2, _ = traj_of(it["prompt"], it["base"], it["answer"])
            first = next(d for d in d2_items if d["prompt"] == it["prompt"])
            dev = max(dev, float(np.max(np.abs(
                np.array(p2) - np.array(first["traj"])))))
        data["determinism"] = {"dev": dev}
        print(f"[isr] determinism dev = {dev}")
    else:
        d2_items = [{**it, "traj": [0.0] * (n_layers - (circle_layer or 0))}
                    for it in circ_items]
        data["determinism"] = {"dev": 0.0}
    data["circ_items"] = d2_items

    # ---- D3: V-patch band sweep (qualifier) ------------------------------
    if formed and not args.skip_patch:
        # ZONE = the measured ACCUMULATION BAND (s345 pre-14B instrument
        # amendment, Michael GO): the 6-layer window maximizing the mean
        # per-layer increment of normalized angular progress across items.
        # (The 0.6B smoke exposed the old circle-formation proxy as degenerate:
        # a lexical circle at L0 collapsed zone into the early band, destroying
        # the s252 route-early dissociation. Circle-formation layer ≠ rotation
        # layer — s128: circle at L10-11, rotation at L12-16.)
        offset = circle_layer or 0
        nm = np.stack([normalized_monotone(np.asarray(it["traj"]))
                       for it in d2_items])
        inc = np.diff(nm, axis=1).mean(axis=0)          # mean increment/layer
        win = 6
        if len(inc) >= win:
            sums = np.convolve(inc, np.ones(win), mode="valid")
            z0 = offset + int(np.argmax(sums)) + 1       # diff idx i → layer i+1
        else:
            z0 = offset
        zone = list(range(z0, min(z0 + win, n_layers)))
        bands = {"early": list(range(0, min(7, n_layers))),
                 "zone": zone,
                 "late": list(range(max(0, n_layers - 6), n_layers))}
        data["zone_band"] = {"layers": zone,
                             "mean_increment_by_layer": {
                                 str(offset + i + 1): round(float(v), 5)
                                 for i, v in enumerate(inc)}}
        print(f"[isr] D3 accumulation-band zone = L{zone[0]}-L{zone[-1]}")
        pairs = []
        for it in circ_items[:: max(1, len(circ_items) // 14)]:
            donor_base = DAYS[(DAYS.index(it["base"]) + 3) % 7]
            di = DAYS.index(donor_base)
            pairs.append((it, {"base": donor_base,
                               "answer": DAYS[(di + it["n"]) % 7],
                               "prompt": CIRC_TEMPLATE.format(
                                   n=it["n"], day=donor_base)}))

        def day_pos(prompt: str, day: str) -> int | None:
            ids = tok(prompt).input_ids
            t = tok.encode(" " + day)[0]
            return ids.index(t) if t in ids else None

        v_store: dict[int, Any] = {}

        def capture_v(prompt: str, band: list[int]) -> dict[int, Any]:
            store: dict[int, Any] = {}
            hooks = []
            for li in band:
                def mk(li_):
                    def hook(_m, _i, out):
                        store[li_] = out.detach()
                    return hook
                hooks.append(model.model.layers[li].self_attn.v_proj
                             .register_forward_hook(mk(li)))
            ids = tok(prompt, return_tensors="pt").input_ids.to(model.device)
            with torch.no_grad():
                model(ids)
            for h in hooks:
                h.remove()
            return store

        def patched_pred(prompt: str, pos: int, band: list[int],
                         donor_v: dict[int, Any]) -> int:
            hooks = []
            for li in band:
                def mk(li_):
                    def hook(_m, _i, out):
                        out = out.clone()
                        out[0, pos] = donor_v[li_][0, pos]
                        return out
                    return hook
                hooks.append(model.model.layers[li].self_attn.v_proj
                             .register_forward_hook(mk(li)))
            ids = tok(prompt, return_tensors="pt").input_ids.to(model.device)
            with torch.no_grad():
                logits = model(ids).logits[0, -1, day_first_tok]
            for h in hooks:
                h.remove()
            return int(logits.float().cpu().numpy().argmax())

        adoption = {b: [] for b in bands}
        noop_adopt = []
        ans_idx = {d: i for i, d in enumerate(DAYS)}
        for it, donor in pairs:
            pos = day_pos(it["prompt"], it["base"])
            dpos = day_pos(donor["prompt"], donor["base"])
            if pos is None or dpos is None or pos != dpos:
                continue
            for bname, band in bands.items():
                donor_v = capture_v(donor["prompt"], band)
                pred = patched_pred(it["prompt"], pos, band, donor_v)
                adoption[bname].append(int(pred == ans_idx[donor["answer"]]))
            own_v = capture_v(it["prompt"], bands["zone"])
            noop = patched_pred(it["prompt"], pos, bands["zone"], own_v)
            noop_adopt.append(int(noop == ans_idx[donor["answer"]]))
        v_store.clear()
        if noop_adopt:
            data["patch"] = {
                "noop": round(float(np.mean(noop_adopt)), 3),
                "bands": {b: round(float(np.mean(v)), 3) if v else 0.0
                          for b, v in adoption.items()},
                "n_pairs": len(noop_adopt)}
            print(f"[isr] D3 patch: {data['patch']}")
    return data, meta


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps", choices=["cpu", "mps", "cuda"])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--skip-patch", action="store_true")
    ap.add_argument("--probes-per-comb", type=int, default=None)
    ap.add_argument("--n-perm", type=int, default=5000)
    ap.add_argument("--z", type=float, default=3.0)
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    data, meta = capture_all(args)
    n_perm = 800 if args.smoke else args.n_perm
    res = analyse(data, n_perm=n_perm, seed=11)

    slug = args.model.split("/")[-1].lower().replace(".", "-")
    out_dir = RESULTS_DIR / ("smoke_" + slug if args.smoke else "run_" + slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2, default=str))
    (out_dir / "verdict.json").write_text(json.dumps(res, indent=2, default=str))
    (out_dir / "per_item.json").write_text(json.dumps(
        {"lin_items": data["lin_items"],
         "circ_items": [{k: v for k, v in it.items() if k != "traj"}
                        | {"l50": l50_of(np.array(it["traj"]))}
                        for it in data["circ_items"]],
         "circle": data["circle"]},
        indent=2, default=str))
    np.savez_compressed(out_dir / "trajectories.npz",
                        **{f"item_{i}": np.array(it["traj"])
                           for i, it in enumerate(data["circ_items"])})
    print("=" * 64)
    print(f"[isr] VERDICT: {res['verdict']}")
    print(f"[isr] D1 ρ_lin={res['d1']['rho_lin']} p={res['d1']['p_lin']} "
          f"pass={res['d1']['pass']}")
    print(f"[isr] D2 ρ_circ={res['d2']['rho_circ']} p={res['d2']['p_circ']} "
          f"slope={res['d2']['slope_l50']} "
          f"shape_p={res['d2']['shape_collapse_null_p']} pass={res['d2']['pass']}")
    print(f"[isr] D3 qualifier: {res['d3'].get('qualifier')}")
    print(f"[isr] secondary: {res['secondary']}")
    print(f"[isr] wrote {out_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
