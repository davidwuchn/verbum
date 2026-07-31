#!/usr/bin/env python3
"""P-DUST-1 — is the crystal Gram the occupation measure of the reduction walk?

Pre-reg: mementum/knowledge/explore/dust-hypothesis-geometry-is-occupation.md
(#p-dust-1, FROZEN s284 incl. pre-run amendment; Michael GO). Data-only:
no model loads. Walk side computed HERE for the first time; geometry side =
the 13 committed crystal Grams (results/opcode-trace/*/model_vsm.json).

WALK SIDE (per the amended pre-reg)
  Ensemble: seeded uniform random applicative terms — random binary tree
  shapes (recursive uniform split), sizes 3-9 leaves, leaves uniform over the
  8 active combinators {K,I,B,C,S,D,W,Y} plus one generic atom class;
  N=100,000; seed=0; max_steps=100 (Y-capped).
  Reducer: normal-order tracing reducer over a minimal tuple term model.
  The v11 kernel's Combinator IntEnum cannot be extended, so "reuse" is
  honored SEMANTICALLY: --validate gates this reducer against
  scripts/v11/kernel.py on the shared K/I/B/C fragment (identical normal
  forms + step counts on random terms) before any ensemble run. Rules:
    K x y -> x | I x -> x | B f g x -> f (g x) | C f x y -> f y x
    S f g x -> f x (g x) | D f x -> f (f x) (s281 defn) | W f x -> f x x
    Y f -> f (Y f)
  WHNF = halt/absorption event, logged once per terminating trace.
  Instrument-safety bound (documented): term size cap 20,000 nodes -> counted
  as non-terminating (duplication blowup guard; a K-rescued giant is rare and
  would bias against halting, i.e. against P1 -- conservative).

STATISTICS (frozen before computation)
  pi_i    occupation = event frequency over all events (rules + WHNF)
  S_ij    presence PMI over traces, add-one smoothed:
          log[ (n_ij+1)/N / (((n_i+1)/N)((n_j+1)/N)) ]   (PRIMARY pairwise)
  h_i     P(next event is WHNF | event i)                (halt proximity)
  secondaries (verbatim, never gated): symmetrized transitions, raw co-occ.

GATES (frozen)
  P1  rank-corr( cos(WHNF,.), h ) > 0 over the 8 non-WHNF ops; label-perm
      null (10k); per-model rows; gate on median rho > 0 with pooled-median
      perm p < 0.05.
  P2  rank-corr( offdiag Gram cos, PMI ) over the 36 pairs, per model;
      label-perm null (10k, node relabeling on the walk side); gate: median
      rho > 0, median per-model p < 0.05, AND median rho_PMI > median
      rho_margins where margins model = rank-corr(gram, pi_i + pi_j).
  P3  P2 sign-positive in >= 11/13 models AND pooled-median perm p < 0.05.
  DUST-SUPPORTED <=> P1 & P2 & P3. Verbatim rows regardless.

Usage:
    uv run python opcodes/dust_walk.py --validate     # reducer + stats gates
    uv run python opcodes/dust_walk.py                # the verdict run

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from itertools import combinations
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "v11"))

OPS = ["K", "I", "B", "C", "S", "D", "W", "Y"]
ALL9 = [*OPS, "WHNF"]
ARITY = {"K": 2, "I": 1, "B": 3, "C": 3, "S": 3, "D": 2, "W": 2, "Y": 1}
ATOM = ("a",)
MAX_STEPS = 100
SIZE_CAP = 20_000
N_TERMS = 100_000
SIZES = (3, 9)          # leaves, inclusive
SEED = 0

# s269 statechart halt probabilities (EQUATIONS.md; KIBC only, model-derived)
S269_HALT = {"K": 0.716, "I": 0.508, "B": 0.345, "C": 0.216}

# P-DUST-1b arms (frozen): leaf label -> weight (None = uniform over labels)
ARMS = {
    "baseline": {"leaves": [*OPS, "atom"], "weights": None, "seed": 0},
    "y-excluded": {"leaves": ["K", "I", "B", "C", "S", "D", "W", "atom"],
                   "weights": None, "seed": 1},
    "y-downweighted": {"leaves": [*OPS, "atom"],
                       "weights": {"Y": 1 / 32}, "seed": 2},
}


# ── term model: ('a',) | ('c', name) | ('app', f, x) ──────────────────────────
def app(f, x):
    return ("app", f, x)


def spine(t):
    args = []
    while t[0] == "app":
        args.append(t[2])
        t = t[1]
    return t, args[::-1]


def rebuild(h, args):
    for a in args:
        h = ("app", h, a)
    return h


def apply_rule(name: str, args: list):
    """Result of firing `name` on its consumed args (len == ARITY[name])."""
    if name == "K":
        return args[0]
    if name == "I":
        return args[0]
    if name == "B":
        f, g, x = args
        return app(f, app(g, x))
    if name == "C":
        f, x, y = args
        return app(app(f, y), x)
    if name == "S":
        f, g, x = args
        return app(app(f, x), app(g, x))
    if name == "D":
        f, x = args
        return app(f, app(f, x))
    if name == "W":
        f, x = args
        return app(app(f, x), x)
    if name == "Y":
        (f,) = args
        return app(f, app(("c", "Y"), f))
    raise ValueError(name)


def step(t):
    """Leftmost-outermost step. Returns (term, rule_name | None)."""
    if t[0] != "app":
        return t, None
    h, args = spine(t)
    if h[0] == "c":
        k = ARITY[h[1]]
        if len(args) >= k:
            res = apply_rule(h[1], args[:k])
            return rebuild(res, args[k:]), h[1]
    nf, r = step(t[1])
    if r:
        return ("app", nf, t[2]), r
    na, r = step(t[2])
    if r:
        return ("app", t[1], na), r
    return t, None


def size(t) -> int:
    if t[0] != "app":
        return 1
    return size(t[1]) + size(t[2])


def trace(t, max_steps: int = MAX_STEPS) -> list[str]:
    """Event sequence: fired rules, + 'WHNF' iff halted within bounds."""
    ev = []
    for _ in range(max_steps):
        t, r = step(t)
        if r is None:
            ev.append("WHNF")
            return ev
        ev.append(r)
        if size(t) > SIZE_CAP:
            return ev            # blowup guard: non-terminating
    t, r = step(t)
    if r is None:
        ev.append("WHNF")
    return ev


def leaf_probs(arm: dict) -> tuple[list[str], np.ndarray]:
    """Leaf label distribution for an arm: fixed weights for named labels,
    remaining mass uniform over the rest (frozen 1b spec)."""
    labels = arm["leaves"]
    w = np.ones(len(labels)) / len(labels)
    if arm["weights"]:
        fixed = arm["weights"]
        rem = 1.0 - sum(fixed.values())
        others = [i for i, lab in enumerate(labels) if lab not in fixed]
        for lab, wt in fixed.items():
            w[labels.index(lab)] = wt
        for i in others:
            w[i] = rem / len(others)
    return labels, w / w.sum()


def gen_term(n_leaves: int, rng, labels: list[str], probs: np.ndarray) -> tuple:
    if n_leaves == 1:
        lab = labels[int(rng.choice(len(labels), p=probs))]
        return ATOM if lab == "atom" else ("c", lab)
    k = int(rng.integers(1, n_leaves))
    return app(gen_term(k, rng, labels, probs),
               gen_term(n_leaves - k, rng, labels, probs))


# ── walk statistics (frozen) ──────────────────────────────────────────────────
def walk_stats(traces: list[list[str]]) -> dict:
    n = len(traces)
    idx = {o: i for i, o in enumerate(ALL9)}
    pi_counts = np.zeros(9)
    pres = np.zeros(9)
    co = np.zeros((9, 9))
    trans = np.zeros((9, 9))
    h_num = np.zeros(9)
    h_den = np.zeros(9)
    for ev in traces:
        s = set(ev)
        for o in s:
            pres[idx[o]] += 1
        for a, b in combinations(sorted(s), 2):
            co[idx[a], idx[b]] += 1
            co[idx[b], idx[a]] += 1
        for i, e in enumerate(ev):
            pi_counts[idx[e]] += 1
            if e != "WHNF":
                h_den[idx[e]] += 1
                if i + 1 < len(ev):
                    trans[idx[e], idx[ev[i + 1]]] += 1
                    if ev[i + 1] == "WHNF":
                        h_num[idx[e]] += 1
    pi = pi_counts / max(pi_counts.sum(), 1)
    pmi = np.zeros((9, 9))
    for i in range(9):
        for j in range(9):
            if i != j:
                pmi[i, j] = np.log(((co[i, j] + 1) / n)
                                   / (((pres[i] + 1) / n) * ((pres[j] + 1) / n)))
    h = np.where(h_den > 0, h_num / np.maximum(h_den, 1), 0.0)
    t_sym = np.zeros((9, 9))
    row = trans.sum(axis=1, keepdims=True)
    tn = np.divide(trans, np.maximum(row, 1))
    t_sym = (tn + tn.T) / 2.0
    return {"n_traces": n, "pi": pi, "pres_frac": pres / n, "pmi": pmi,
            "h": h, "t_sym": t_sym,
            "halt_frac": float(pres[idx["WHNF"]] / n)}


# ── geometry side ─────────────────────────────────────────────────────────────
def load_grams() -> dict[str, tuple[list[str], np.ndarray]]:
    """root.gram from every model_vsm.json whose basis covers ALL9.
    (Loader per opcodes/d_is_i_test.py, absolute-path variant.)"""
    out = {}
    for p in sorted((_ROOT / "results" / "opcode-trace").glob("*/model_vsm.json")):
        try:
            d = json.loads(p.read_text())
            basis = d["basis"]
            g = np.array(d["root"]["gram"], float)
        except Exception:
            continue
        if set(ALL9) <= set(basis) and g.shape[0] == len(basis):
            out[p.parent.name] = (basis, g)
    return out


# ── rank correlation (numpy, average ties) ────────────────────────────────────
def rankdata(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x))
    sx = x[order]
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and sx[j + 1] == sx[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0
        i = j + 1
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = rankdata(x), rankdata(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    d = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / d) if d > 0 else 0.0


# ── verdict analysis ──────────────────────────────────────────────────────────
def offdiag_pairs(m: np.ndarray, order: list[int]) -> np.ndarray:
    n = len(order)
    return np.array([m[order[i], order[j]]
                     for i, j in combinations(range(n), 2)])


def exact_perms(n: int) -> list[np.ndarray]:
    from itertools import permutations
    return [np.array(p) for p in permutations(range(n))]


def analyze_1b(stats: dict, grams: dict, active_ops: list[str],
               n_perm: int, rng) -> dict:
    """P-DUST-1b gates: P1-KIBC (s269 verbatim, exact 24) + P1'-WALK (exact
    5040 over active non-Y ops) + P2/P3 replication on the sub-Gram."""
    models = sorted(grams)
    nodes = [*active_ops, "WHNF"]
    kibc = ["K", "I", "B", "C"]
    s269 = np.array([S269_HALT[o] for o in kibc])
    h = np.array([stats["h"][ALL9.index(o)] for o in active_ops])
    pmi_idx = [ALL9.index(o) for o in nodes]
    pi = stats["pi"]
    perms4 = exact_perms(4)
    perms_a = exact_perms(len(active_ops))      # exact up to 8 (40320) is cheap

    per_model = {}
    rk_all, rw_all, r2_all, r2m_all = [], [], [], []
    nullk_rows, nullw_rows = [], []
    perms_pair = [rng.permutation(len(nodes)) for _ in range(n_perm)]

    for name in models:
        basis, g = grams[name]
        w_i = basis.index("WHNF")
        # P1-KIBC: cos(WHNF, op) vs s269 constants, exact 24
        cos_k = np.array([g[w_i, basis.index(o)] for o in kibc])
        rk = spearman(cos_k, s269)
        nullk = np.array([spearman(cos_k, s269[p]) for p in perms4])
        pk = float(np.mean(nullk >= rk))
        # P1'-WALK: cos(WHNF, op) vs arm h over active ops, exact
        cos_a = np.array([g[w_i, basis.index(o)] for o in active_ops])
        rw = spearman(cos_a, h)
        nullw = np.array([spearman(cos_a, h[p]) for p in perms_a])
        pw = float(np.mean(nullw >= rw))
        # P2 replication on sub-Gram
        order = [basis.index(o) for o in nodes]
        gv = offdiag_pairs(g, order)
        sub_pmi = stats["pmi"][np.ix_(pmi_idx, pmi_idx)]
        sub_m = (pi[pmi_idx][:, None] + pi[pmi_idx][None, :])
        idn = list(range(len(nodes)))
        r2 = spearman(gv, offdiag_pairs(sub_pmi, idn))
        r2m = spearman(gv, offdiag_pairs(sub_m, idn))
        null2 = np.array([spearman(gv, offdiag_pairs(sub_pmi, list(p)))
                          for p in perms_pair])
        p2 = float(np.mean(null2 >= r2))
        per_model[name] = {"rho_kibc": round(rk, 4), "p_kibc_exact": pk,
                           "rho_walk": round(rw, 4), "p_walk_exact": pw,
                           "rho2_pmi": round(r2, 4), "p2": p2,
                           "rho2_margins": round(r2m, 4)}
        rk_all.append(rk)
        rw_all.append(rw)
        r2_all.append(r2)
        r2m_all.append(r2m)
        nullk_rows.append(nullk)
        nullw_rows.append(nullw)

    nullk_med = np.median(np.stack(nullk_rows), axis=0)
    nullw_med = np.median(np.stack(nullw_rows), axis=0)
    med_k, med_w = float(np.median(rk_all)), float(np.median(rw_all))
    med_2, med_2m = float(np.median(r2_all)), float(np.median(r2m_all))
    n13 = len(models)
    need = max(n13 - 2, int(np.ceil(n13 * 11 / 13)))
    pk_pool = float(np.mean(nullk_med >= med_k))
    pw_pool = float(np.mean(nullw_med >= med_w))
    n_pos_k = int(np.sum(np.array(rk_all) > 0))
    n_pos_2 = int(np.sum(np.array(r2_all) > 0))

    p1_kibc = bool(med_k > 0 and n_pos_k >= need and pk_pool < 0.05)
    p1_walk = bool(med_w > 0 and pw_pool < 0.05)
    p23_rep = bool(n_pos_2 >= need)
    return {"models": models, "active_ops": active_ops,
            "per_model": per_model,
            "median_rho_kibc": round(med_k, 4), "pooled_p_kibc": pk_pool,
            "n_models_kibc_positive": n_pos_k,
            "median_rho_walk": round(med_w, 4), "pooled_p_walk": pw_pool,
            "median_rho2_pmi": round(med_2, 4),
            "median_rho2_margins": round(med_2m, 4),
            "n_models_rho2_positive": n_pos_2,
            "gates": {"P1_KIBC": p1_kibc, "P1_WALK": p1_walk,
                      "P23_replication": p23_rep},
            "dust_halt_supported": bool(p1_kibc and p1_walk)}


def analyze(stats: dict, grams: dict, n_perm: int, rng) -> dict:
    models = sorted(grams)
    pmi, h, pi = stats["pmi"], stats["h"], stats["pi"]
    m_margin = pi[:, None] + pi[None, :]

    per_model = {}
    rho1_all, rho2_all, rhom_all, p2_all = [], [], [], []
    perms = [rng.permutation(9) for _ in range(n_perm)]
    perms8 = [rng.permutation(8) for _ in range(n_perm)]
    null1_rows = np.zeros((n_perm, len(models)))
    null2_rows = np.zeros((n_perm, len(models)))

    for mi, name in enumerate(models):
        basis, g = grams[name]
        order = [basis.index(o) for o in ALL9]      # gram indices in ALL9 order
        gw = g[np.ix_(order, order)]
        # P1: cos(WHNF, op) vs h_op over the 8 ops
        w = ALL9.index("WHNF")
        cosw = np.array([gw[w, ALL9.index(o)] for o in OPS])
        hv = np.array([h[ALL9.index(o)] for o in OPS])
        rho1 = spearman(cosw, hv)
        # P2: offdiag gram vs PMI (+ margins floor)
        gv = offdiag_pairs(gw, list(range(9)))
        sv = offdiag_pairs(pmi, list(range(9)))
        mv = offdiag_pairs(m_margin, list(range(9)))
        rho2 = spearman(gv, sv)
        rhom = spearman(gv, mv)
        null2 = np.array([
            spearman(gv, offdiag_pairs(pmi, list(p))) for p in perms])
        p2 = float(np.mean(null2 >= rho2))
        null1 = np.array([spearman(cosw, hv[p]) for p in perms8])
        p1 = float(np.mean(null1 >= rho1))
        null1_rows[:, mi] = null1
        null2_rows[:, mi] = null2
        per_model[name] = {"rho1": round(rho1, 4), "p1": p1,
                           "rho2_pmi": round(rho2, 4), "p2": p2,
                           "rho2_margins": round(rhom, 4)}
        rho1_all.append(rho1)
        rho2_all.append(rho2)
        rhom_all.append(rhom)
        p2_all.append(p2)

    med1, med2 = float(np.median(rho1_all)), float(np.median(rho2_all))
    medm = float(np.median(rhom_all))
    pooled_p1 = float(np.mean(np.median(null1_rows, axis=1) >= med1))
    pooled_p2 = float(np.mean(np.median(null2_rows, axis=1) >= med2))
    n_pos = int(np.sum(np.array(rho2_all) > 0))

    p1_pass = bool(med1 > 0 and pooled_p1 < 0.05)
    p2_pass = bool(med2 > 0 and float(np.median(p2_all)) < 0.05 and med2 > medm)
    p3_pass = bool(n_pos >= max(len(models) - 2, int(np.ceil(len(models) * 11 / 13)))
                   and pooled_p2 < 0.05)
    return {"models": models, "per_model": per_model,
            "median_rho1": round(med1, 4), "pooled_p1": pooled_p1,
            "median_rho2_pmi": round(med2, 4),
            "median_rho2_margins": round(medm, 4),
            "median_p2": round(float(np.median(p2_all)), 4),
            "pooled_p2": pooled_p2,
            "n_models_rho2_positive": n_pos,
            "gates": {"P1": p1_pass, "P2": p2_pass, "P3": p3_pass},
            "dust_supported": bool(p1_pass and p2_pass and p3_pass)}


# ── validation (reducer + kernel equivalence + stats sanity) ──────────────────
def to_kernel(t, kernel):
    if t == ATOM:
        return kernel.Atom("a")
    if t[0] == "c":
        return kernel.Comb(getattr(kernel.Combinator, t[1]))
    return kernel.App(to_kernel(t[1], kernel), to_kernel(t[2], kernel))


def from_kernel(t, kernel):
    if isinstance(t, kernel.Atom):
        return ATOM
    if isinstance(t, kernel.Comb):
        return ("c", t.which.name)
    return app(from_kernel(t.func, kernel), from_kernel(t.arg, kernel))


def reduce_full(t, max_steps=MAX_STEPS):
    for _ in range(max_steps):
        t2, r = step(t)
        if r is None:
            return t, True
        t = t2
    return t, False


def validate() -> int:
    import kernel  # scripts/v11
    fails: list[str] = []

    def check(name, ok, detail=""):
        print(f"[dust][validate] {'PASS' if ok else 'FAIL'} {name} {detail}",
              file=sys.stderr)
        if not ok:
            fails.append(name)

    a = ATOM
    cK, cI, cB, cC = ("c", "K"), ("c", "I"), ("c", "B"), ("c", "C")
    cS, cD, cW, cY = ("c", "S"), ("c", "D"), ("c", "W"), ("c", "Y")
    f, g, x, y = a, a, a, a  # generic atoms

    # hand-reduced single rules
    cases = [
        (app(app(cK, cI), a), cI, ["K", "WHNF"]),
        (app(cI, a), a, ["I", "WHNF"]),
        (app(app(app(cB, f), g), x), app(f, app(g, x)), ["B", "WHNF"]),
        (app(app(app(cC, f), x), y), app(app(f, y), x), ["C", "WHNF"]),
        (app(app(app(cS, f), g), x), app(app(f, x), app(g, x)), ["S", "WHNF"]),
        (app(app(cD, f), x), app(f, app(f, x)), ["D", "WHNF"]),
        (app(app(cW, f), x), app(app(f, x), x), ["W", "WHNF"]),
    ]
    ok = True
    for t, want_nf, want_ev in cases:
        nf, halted = reduce_full(t)
        ev = trace(t)
        ok &= (nf == want_nf and halted and ev == want_ev)
    check("hand_reduced_rules", ok)

    ev_y = trace(app(cY, f))
    check("y_nontermination", ev_y.count("Y") >= 1 and "WHNF" not in ev_y,
          f"(events={ev_y[:4]}...n={len(ev_y)})")

    # over-application: K fires at spine with remainder args
    t = app(app(app(cK, f), g), x)         # (K f g) x -> f x
    nf, _ = reduce_full(t)
    check("overapplied_spine", nf == app(f, x))

    # kernel equivalence on the K/I/B/C fragment
    rng = np.random.default_rng(42)
    frag = ["K", "I", "B", "C"]
    agree = 0
    n_eq = 300
    for _ in range(n_eq):
        n = int(rng.integers(3, 10))

        def gen_frag(m):
            if m == 1:
                i = int(rng.integers(0, 5))
                return ATOM if i == 4 else ("c", frag[i])
            k = int(rng.integers(1, m))
            return app(gen_frag(k), gen_frag(m - k))

        t = gen_frag(n)
        nf_ours, _ = reduce_full(t)
        kt, ksteps = kernel.reduce(to_kernel(t, kernel), max_steps=MAX_STEPS)
        n_ours = len([e for e in trace(t) if e != "WHNF"])
        if from_kernel(kt, kernel) == nf_ours and ksteps == n_ours:
            agree += 1
    check("kernel_equivalence_KIBC", agree == n_eq, f"({agree}/{n_eq})")

    # stats sanity: planted co-occurrence -> top PMI pair; spearman correctness
    tr = [["K", "S", "WHNF"]] * 50 + [["B", "WHNF"]] * 50 + [["K", "WHNF"]] * 10
    st = walk_stats(tr)
    iK, iS, iB = ALL9.index("K"), ALL9.index("S"), ALL9.index("B")
    check("pmi_planted", st["pmi"][iK, iS] > st["pmi"][iK, iB],
          f"(KS={st['pmi'][iK, iS]:.2f} KB={st['pmi'][iK, iB]:.2f})")
    check("h_planted", st["h"][iS] == 1.0 and st["h"][iK] < 0.2,
          f"(hS={st['h'][iS]} hK={st['h'][iK]:.2f})")
    check("spearman_exact",
          abs(spearman(np.array([1, 2, 3, 4.0]), np.array([2, 4, 6, 8.0])) - 1.0)
          < 1e-12 and
          abs(spearman(np.array([1, 2, 3, 4.0]), np.array([8, 6, 4, 2.0])) + 1.0)
          < 1e-12)

    # 1b arm machinery
    labels_b, probs_b = leaf_probs(ARMS["y-excluded"])
    labels_c, probs_c = leaf_probs(ARMS["y-downweighted"])
    check("arm_b_no_y", "Y" not in labels_b and abs(probs_b.sum() - 1) < 1e-12,
          f"(leaves={labels_b})")
    check("arm_c_y_downweight",
          abs(probs_c[labels_c.index("Y")] - 1 / 32) < 1e-12
          and abs(probs_c.sum() - 1) < 1e-12,
          f"(pY={probs_c[labels_c.index('Y')]:.4f})")
    # planted P1-KIBC: gram row perfectly ordered like s269 -> rho=1, p=1/24
    s269 = np.array([S269_HALT[o] for o in ["K", "I", "B", "C"]])
    rho = spearman(s269 * 0.5 + 0.1, s269)
    p24 = exact_perms(4)
    pex = float(np.mean([spearman((s269 * 0.5 + 0.1), s269[p]) for p in p24]
                        >= np.float64(rho)))
    check("p1_kibc_exact", abs(rho - 1) < 1e-12 and abs(pex - 1 / 24) < 1e-9,
          f"(rho={rho} p={pex:.4f})")

    print(f"[dust][validate] {'ALL PASS' if not fails else f'FAILURES: {fails}'}",
          file=sys.stderr)
    return 0 if not fails else 1


# ── main ──────────────────────────────────────────────────────────────────────
def git_sha():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                           text=True, cwd=_ROOT, timeout=10)
        return r.stdout.strip() or None
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="P-DUST-1/1b geometry = occupation?")
    ap.add_argument("--arm", choices=list(ARMS), default="baseline")
    ap.add_argument("--n-terms", type=int, default=N_TERMS)
    ap.add_argument("--n-perm", type=int, default=10_000)
    ap.add_argument("--seed", type=int, default=None,
                    help="default = the arm's frozen seed")
    ap.add_argument("--output", default=None)
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        sys.exit(validate())

    arm = ARMS[args.arm]
    seed = arm["seed"] if args.seed is None else args.seed
    labels, probs = leaf_probs(arm)
    sys.setrecursionlimit(200_000)
    rng = np.random.default_rng(seed)
    print(f"[dust] arm={args.arm} leaves={labels} "
          f"probs={[round(float(p), 4) for p in probs]} seed={seed}",
          file=sys.stderr)
    print(f"[dust] generating {args.n_terms} terms sizes {SIZES}",
          file=sys.stderr)
    traces = []
    for i in range(args.n_terms):
        n = int(rng.integers(SIZES[0], SIZES[1] + 1))
        traces.append(trace(gen_term(n, rng, labels, probs)))
        if (i + 1) % 20_000 == 0:
            print(f"[dust]   {i + 1}/{args.n_terms}", file=sys.stderr)
    stats = walk_stats(traces)
    pi_row = {o: round(float(stats["pi"][ALL9.index(o)]), 4) for o in ALL9}
    h_row = {o: round(float(stats["h"][ALL9.index(o)]), 4) for o in OPS}
    print(f"[dust] halt_frac={stats['halt_frac']:.4f} pi={pi_row}",
          file=sys.stderr)
    print(f"[dust] h={h_row}", file=sys.stderr)

    grams = load_grams()
    print(f"[dust] grams loaded: {len(grams)} models", file=sys.stderr)
    if not grams:
        print("[dust] FATAL: no 9-combinator grams found", file=sys.stderr)
        sys.exit(1)

    if args.arm == "baseline":
        res = analyze(stats, grams, args.n_perm, rng)
        for m in res["models"]:
            r = res["per_model"][m]
            print(f"[dust] {m:26s} rho1={r['rho1']:+.3f}(p={r['p1']:.3f}) "
                  f"rho2_pmi={r['rho2_pmi']:+.3f}(p={r['p2']:.3f}) "
                  f"rho2_margins={r['rho2_margins']:+.3f}", file=sys.stderr)
        print(f"[dust] MEDIANS: rho1={res['median_rho1']} "
              f"(pooled_p={res['pooled_p1']}) "
              f"| rho2_pmi={res['median_rho2_pmi']} (med_p={res['median_p2']}, "
              f"pooled_p={res['pooled_p2']}) vs margins="
              f"{res['median_rho2_margins']} "
              f"| sign+ {res['n_models_rho2_positive']}/{len(res['models'])}",
              file=sys.stderr)
        print(f"[dust] GATES: {res['gates']} -> "
              f"dust_supported={res['dust_supported']}", file=sys.stderr)
    else:
        active = [lab for lab in arm["leaves"] if lab != "atom"]
        res = analyze_1b(stats, grams, active, args.n_perm, rng)
        for m in res["models"]:
            r = res["per_model"][m]
            print(f"[dust] {m:26s} "
                  f"kibc={r['rho_kibc']:+.3f}(p={r['p_kibc_exact']:.3f}) "
                  f"walk={r['rho_walk']:+.3f}(p={r['p_walk_exact']:.3f}) "
                  f"pmi={r['rho2_pmi']:+.3f}(p={r['p2']:.3f})",
                  file=sys.stderr)
        print(f"[dust] MEDIANS: kibc={res['median_rho_kibc']} "
              f"(pooled_p={res['pooled_p_kibc']}, "
              f"sign+ {res['n_models_kibc_positive']}/{len(res['models'])}) | "
              f"walk={res['median_rho_walk']} "
              f"(pooled_p={res['pooled_p_walk']}) | "
              f"pmi={res['median_rho2_pmi']} vs margins="
              f"{res['median_rho2_margins']} "
              f"(sign+ {res['n_models_rho2_positive']}/{len(res['models'])})",
              file=sys.stderr)
        print(f"[dust] GATES: {res['gates']} -> "
              f"dust_halt_supported={res['dust_halt_supported']}",
              file=sys.stderr)

    out = (Path(args.output) if args.output
           else _ROOT / "results" / "dust-walk" /
           (args.arm if args.arm != "baseline" else ""))
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "experiment": "P-DUST-1" if args.arm == "baseline" else "P-DUST-1b",
        "arm": args.arm,
        "prereg": ("mementum/knowledge/explore/"
                   "dust-hypothesis-geometry-is-occupation.md#p-dust-1"),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(),
        "config": {"n_terms": args.n_terms, "sizes": SIZES, "seed": seed,
                   "leaves": labels,
                   "leaf_probs": [round(float(p), 5) for p in probs],
                   "max_steps": MAX_STEPS, "size_cap": SIZE_CAP,
                   "n_perm": args.n_perm},
        "walk_stats": {
            "halt_frac": stats["halt_frac"],
            "pi": {o: round(float(stats["pi"][ALL9.index(o)]), 5) for o in ALL9},
            "h": {o: round(float(stats["h"][ALL9.index(o)]), 5) for o in OPS},
            "pres_frac": {o: round(float(stats["pres_frac"][ALL9.index(o)]), 5)
                          for o in ALL9},
            "pmi": [[round(float(v), 4) for v in row] for row in stats["pmi"]],
            "t_sym": [[round(float(v), 4) for v in row] for row in stats["t_sym"]],
            "order": ALL9},
        "analysis": res,
    }
    (out / "dust_verdict.json").write_text(json.dumps(payload, indent=2))
    print(f"[dust] wrote {out}/dust_verdict.json", file=sys.stderr)


if __name__ == "__main__":
    main()
