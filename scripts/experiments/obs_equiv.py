#!/usr/bin/env python3
"""§P-OBS-EQUIV — is machine equality of co-extensional terms a RATE? (s347).

FROZEN DESIGN: mementum/knowledge/explore/equality-is-an-agreement-rate.md
(committed fab97fed BEFORE data, Michael GO).

Semantic equality measured the RIGHT way (Michael s346: "two lambdas, different
names, same exact behavior"): §2b profile-equivalence pointed at term PAIRS.
Kernel-certified co-extensional pairs x context battery x driver
fork-differencing (sealed shared prefix, greedy, answer granularity) →
per-pair agreement-rate profile.

Nulls: FLOOR = length-matched kernel-certified NON-equal pairs (agreement
floor); CEILING = same-spelling double-forks (greedy determinism PROVED, not
assumed). Term-sensitivity calibration: a context is SCORED iff floor pairs
disagree there (S(c) >= 0.5) — the manufactured-agreement guard; C6
(discard-position) is PREDICTED to fail it (free-discard, s346).

FROZEN verdict tree (exhaustive on the scored battery) + a-priori mass:
  RATE-STRUCTURED    40  floor < A_coext < ceiling AND context-structure null
                         beaten (agreement profile varies by context)
  LEXICAL-FLOOR      20  D_floor < 0.10 or p >= 0.05 (names are just words)
  VOID               20  G0 fail / battery collapse / certification failure
  RATE-UNSTRUCTURED  10  mid-rate but context-shuffle null NOT beaten
  EXTENSIONAL        10  A_coext >= 0.95 (indistinct from ceiling)

Pre-registered directional contact (frame ledger): A(C1 direct) > A(C2 named),
one-sided. Bug-taxonomy strictly ADVISORY (feeds §P-CALCULUS-LEDGER arm C).
Scars honored: |Δlen| partial + length-matched strata (s343); capture-euphoria
(the s346 REPL pilot is NOT evidence in this ledger).

PRE-DATA AMENDMENT (surfaced, Michael-visible, masses/tree unchanged): the
frozen every-context certification rule auto-excludes W/B-family spellings —
partial application at arity-1 contexts yields legitimately different term NFs
(W a vs S a I). Corpus resolves to I-family pairs; exclusions logged.

`--validate` drives 6 planted worlds through the REAL analyse path (s331:
planted plumbing == data plumbing), incl. the NONDET and INSENSITIVE
adversaries (both must read VOID).

Bounds: battery-indexed rate; EXTENSIONAL would NOT re-locate equality in
weights (one-directional); single model, greedy, answer granularity.

License: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from itertools import combinations
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_ROOT = _SCRIPT_DIR.parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from verbum.lambda_ast import (  # noqa: E402
    R_NAIVE,
    R_WEAK,
    alpha_eq,
    normal_form,
    parse,
    pretty,
)

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (s347 pre-data freeze fab97fed)

SEED = 347
N_COEXT = 24
N_FLOOR = 24
N_CEIL = 96
DECODE_N = 24
FLOOR_D = 0.10
CEIL_BAND = 0.95
SENS_MIN = 0.5
MIN_CONTEXTS = 4
MIN_PAIRS = 12          # certification floor per pair-type (else VOID)
N_PERM = 5000
ALPHA = 0.05
MAX_STEPS = 500

HEADER = (
    "Combinator reduction rules: S f g x = f x (g x); K x y = x; I x = x; "
    "C f x y = f y x; W f x = f x x; B f g x = f (g x).\n"
    "Task: reduce the expression to its final normal form. "
    "Answer with ONLY the final term.\n\n"
)

# context id -> (prefix_template, fork_template, kernel_expr_template)
# {T}=term  {a},{b}=argument atoms. Prefix is SEALED once per (context, args);
# fork text is where the two spellings diverge (identical KV prefix).
CONTEXTS: dict[str, tuple[str, str, str]] = {
    "C1_direct": ("", "{T} {a} = ", "{T} {a}"),
    "C2_named": ("let f = ", "{T}\nf {a} = ", "{T} {a}"),
    "C3_nested": ("", "{T} ({T} {a}) = ", "{T} ({T} {a})"),
    "C4_extra_arg": ("", "{T} {a} {b} = ", "{T} {a} {b}"),
    "C5_arg_position": ("K (", "{T} {a}) {b} = ", "K ({T} {a}) {b}"),
    "C6_discard": ("K {a} (", "{T} {b}) = ", "K {a} ({T} {b})"),
}
CERT_CONTEXTS = ["C1_direct", "C2_named", "C3_nested", "C4_extra_arg",
                 "C5_arg_position"]  # C6: kernel says everyone agrees (K discards)
ARGSETS = [("a", "b"), ("p", "q")]

# s339 co-extensional spelling families (cl_collapse_3_operator FAMILIES).
SPELLINGS = {
    "I": ["I", "S K K", "S K S", "W K", "C K K",
          "S K (K K)", "C K S", "C K (K K)", "S K (S K)"],
    "W": ["W", "S S (K I)", "C S I"],
    "B": ["B", "S (K S) K"],
}
FLOOR_POOL = [
    "S", "K", "C", "B", "W", "K S", "K K", "S K", "C K", "K C", "B K",
    "K (S K)", "S (K K)", "C (K K)", "K (K S)", "S (S K)", "B (K K)",
    "C (S K)", "K (C K)", "S (K S)",
]


def log(msg: str) -> None:
    print(f"[obs-equiv] {msg}", flush=True)


def git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=_ROOT, capture_output=True,
            text=True, check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def _json_native(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.bool_):
        return bool(o)
    raise TypeError(f"not JSON-serializable: {type(o)}")


# ---------------------------------------------------------------------------
# kernel certification


def _nf(expr: str, calc=None) -> str | None:
    try:
        t = parse(expr)
        n = normal_form(t, max_steps=MAX_STEPS) if calc is None else normal_form(
            t, max_steps=MAX_STEPS, calc=calc)
        return pretty(n)
    except Exception:
        return None


def _cell_expected(term: str, ctx: str, args: tuple[str, str]) -> str | None:
    expr = CONTEXTS[ctx][2].format(T=term, a=args[0], b=args[1])
    return _nf(expr)


def _pair_equal_everywhere(t1: str, t2: str) -> bool:
    for ctx in CERT_CONTEXTS:
        for args in ARGSETS:
            n1 = _cell_expected(t1, ctx, args)
            n2 = _cell_expected(t2, ctx, args)
            if n1 is None or n2 is None:
                return False
            try:
                if not alpha_eq(parse(n1), parse(n2)):
                    return False
            except Exception:
                return False
    return True


def _pair_differs_everywhere(t1: str, t2: str) -> bool:
    for ctx in CERT_CONTEXTS:
        for args in ARGSETS:
            n1 = _cell_expected(t1, ctx, args)
            n2 = _cell_expected(t2, ctx, args)
            if n1 is None or n2 is None:
                return False
            try:
                if alpha_eq(parse(n1), parse(n2)):
                    return False
            except Exception:
                return False
    return True


def _atoms(term: str) -> int:
    return len(term.replace("(", " ").replace(")", " ").split())


def build_corpus(n_coext: int, n_floor: int, seed: int) -> dict:
    """Kernel-certified co-ext + floor pairs; exclusions logged, never silent."""
    rng = np.random.default_rng(seed)
    excluded: list[tuple[str, str, str]] = []
    coext: list[tuple[str, str]] = []
    for fam, spells in SPELLINGS.items():
        for t1, t2 in combinations(spells, 2):
            if _pair_equal_everywhere(t1, t2):
                coext.append((t1, t2))
            else:
                excluded.append((fam, t1, t2))
    if len(coext) > n_coext:
        idx = rng.choice(len(coext), size=n_coext, replace=False)
        coext = [coext[i] for i in sorted(idx)]

    floor_cand: list[tuple[str, str]] = []
    pool = FLOOR_POOL + [s for fam in SPELLINGS.values() for s in fam]
    seen = set()
    for t1, t2 in combinations(pool, 2):
        key = (t1, t2)
        if key in seen:
            continue
        seen.add(key)
        if _pair_differs_everywhere(t1, t2):
            floor_cand.append((t1, t2))

    # greedy |Δatoms| matching to the co-ext distribution (s343 length scar)
    target = sorted(abs(_atoms(a) - _atoms(b)) for a, b in coext)
    floor: list[tuple[str, str]] = []
    cand = list(floor_cand)
    rng.shuffle(cand)
    for tgt in target[:n_floor]:
        if not cand:
            break
        def _cost(i: int, t: int = tgt) -> int:
            return abs(abs(_atoms(cand[i][0]) - _atoms(cand[i][1])) - t)

        best = min(range(len(cand)), key=_cost)
        floor.append(cand.pop(best))

    log(f"corpus: coext {len(coext)} (excluded {len(excluded)}: "
        f"{sorted({f for f, _, _ in excluded})}) | floor {len(floor)} "
        f"of {len(floor_cand)} candidates")
    return {"coext": coext, "floor": floor, "excluded": excluded}


# ---------------------------------------------------------------------------
# capture (driver fork-differencing)


def _extract_answer(text: str) -> str:
    ans = text.split("\n")[0].strip()
    ans = ans.rstrip("=. ").strip()
    ans = " ".join(ans.split())
    try:
        return pretty(parse(ans))
    except Exception:
        return ans


def _agree(a1: str, a2: str) -> bool:
    if a1 == a2:
        return True
    try:
        return alpha_eq(parse(a1), parse(a2))
    except Exception:
        return False


def capture(model_id: str, corpus: dict, n_ceil: int, seed: int) -> dict:
    from verbum.driver import Driver

    d = Driver(model_id=model_id)
    validity = d.validity()
    log(f"driver validity: {validity}")
    rng = np.random.default_rng(seed)

    seals = {}
    for ctx, (pre_t, _, _) in CONTEXTS.items():
        for ai, args in enumerate(ARGSETS):
            prefix = HEADER + pre_t.format(a=args[0], b=args[1])
            seals[(ctx, ai)] = d.prefill(prefix)

    def one_fork(ctx: str, ai: int, term: str) -> str:
        args = ARGSETS[ai]
        fork_text = CONTEXTS[ctx][1].format(T=term, a=args[0], b=args[1])
        b = d.fork(seals[(ctx, ai)], fork_text, n=DECODE_N,
                   hidden=False, keep_seal=False)
        return "".join(b.tokens)

    def tok_len(term: str) -> int:
        return len(d.tok(term, add_special_tokens=False).input_ids)

    records: list[dict] = []
    t0 = time.time()
    for kind in ("coext", "floor"):
        for pid, (t1, t2) in enumerate(corpus[kind]):
            dlen = abs(tok_len(t1) - tok_len(t2))
            for ctx in CONTEXTS:
                for ai in range(len(ARGSETS)):
                    args = ARGSETS[ai]
                    raw1 = one_fork(ctx, ai, t1)
                    raw2 = one_fork(ctx, ai, t2)
                    a1, a2 = _extract_answer(raw1), _extract_answer(raw2)
                    e1 = _cell_expected(t1, ctx, args)
                    e2 = _cell_expected(t2, ctx, args)
                    records.append({
                        "kind": kind, "pair_id": f"{kind}{pid}",
                        "t1": t1, "t2": t2, "context": ctx, "argset": ai,
                        "raw1": raw1, "raw2": raw2, "ans1": a1, "ans2": a2,
                        "agree": _agree(a1, a2),
                        "expected1": e1, "expected2": e2,
                        "correct1": e1 is not None and _agree(a1, e1),
                        "correct2": e2 is not None and _agree(a2, e2),
                        "dlen_tok": dlen,
                    })
            log(f"{kind} pair {pid} ({t1!r} vs {t2!r}) done "
                f"[{time.time() - t0:.0f}s]")

    coext_cells = [(pid, t1, t2, ctx, ai)
                   for pid, (t1, t2) in enumerate(corpus["coext"])
                   for ctx in CONTEXTS for ai in range(len(ARGSETS))]
    idx = rng.choice(len(coext_cells), size=min(n_ceil, len(coext_cells)),
                     replace=False)
    for i in sorted(idx):
        pid, t1, t2, ctx, ai = coext_cells[i]
        term = t1 if rng.random() < 0.5 else t2
        raw1 = one_fork(ctx, ai, term)
        raw2 = one_fork(ctx, ai, term)
        a1, a2 = _extract_answer(raw1), _extract_answer(raw2)
        records.append({
            "kind": "ceil", "pair_id": f"ceil{pid}", "t1": term, "t2": term,
            "context": ctx, "argset": ai, "raw1": raw1, "raw2": raw2,
            "ans1": a1, "ans2": a2, "agree": raw1 == raw2,
            "expected1": None, "expected2": None,
            "correct1": None, "correct2": None, "dlen_tok": 0,
        })
    log(f"capture complete: {len(records)} records "
        f"[{time.time() - t0:.0f}s]")
    return {"records": records, "validity": validity}


# ---------------------------------------------------------------------------
# analyse (REAL path — planted worlds drive this same function)


def _perm_p_greater(obs: float, null: np.ndarray) -> float:
    return float((np.sum(null >= obs) + 1) / (len(null) + 1))


def analyse(records: list[dict], seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed)
    ceil = [r for r in records if r["kind"] == "ceil"]
    coext = [r for r in records if r["kind"] == "coext"]
    floor = [r for r in records if r["kind"] == "floor"]

    a_ceil = float(np.mean([r["agree"] for r in ceil])) if ceil else float("nan")
    g0_pass = bool(ceil) and a_ceil == 1.0
    det_dev = 1.0 - a_ceil if ceil else float("nan")

    n_coext_pairs = len({r["pair_id"] for r in coext})
    n_floor_pairs = len({r["pair_id"] for r in floor})
    cert_pass = n_coext_pairs >= MIN_PAIRS and n_floor_pairs >= MIN_PAIRS

    # term-sensitivity calibration on floor pairs (manufactured-agreement guard)
    sens: dict[str, float] = {}
    for ctx in CONTEXTS:
        cells = [r["agree"] for r in floor if r["context"] == ctx]
        sens[ctx] = 1.0 - float(np.mean(cells)) if cells else float("nan")
    scored = [c for c in CONTEXTS if not np.isnan(sens[c]) and sens[c] >= SENS_MIN]
    n_scored = len(scored)

    co_s = [r for r in coext if r["context"] in scored]
    fl_s = [r for r in floor if r["context"] in scored]
    a_coext = float(np.mean([r["agree"] for r in co_s])) if co_s else float("nan")
    a_floor = float(np.mean([r["agree"] for r in fl_s])) if fl_s else float("nan")
    a_coext_ctx = {c: float(np.mean([r["agree"] for r in co_s if r["context"] == c]))
                   for c in scored}

    # D_floor: pair-level, label shuffle within |Δlen| strata (s343 scar)
    def pair_stats(rows):
        out = {}
        for r in rows:
            out.setdefault(r["pair_id"], {"agrees": [], "dlen": r["dlen_tok"]})
            out[r["pair_id"]]["agrees"].append(r["agree"])
        return {k: (float(np.mean(v["agrees"])), v["dlen"]) for k, v in out.items()}

    cp, fp = pair_stats(co_s), pair_stats(fl_s)
    vals = np.array([v for v, _ in cp.values()] + [v for v, _ in fp.values()])
    dls = np.array([d for _, d in cp.values()] + [d for _, d in fp.values()],
                   dtype=float)
    labels = np.array([1] * len(cp) + [0] * len(fp))
    d_floor = p_floor = float("nan")
    r_len = d_floor_partial = float("nan")
    if len(cp) and len(fp):
        d_floor = float(vals[labels == 1].mean() - vals[labels == 0].mean())
        edges = np.quantile(dls, [1 / 3, 2 / 3])
        strata = np.digitize(dls, edges)
        null = np.empty(N_PERM)
        for k in range(N_PERM):
            lab = labels.copy()
            for s in np.unique(strata):
                m = strata == s
                lab[m] = rng.permutation(lab[m])
            null[k] = vals[lab == 1].mean() - vals[lab == 0].mean()
        p_floor = _perm_p_greater(d_floor, null)
        # |Δlen| advisory: correlation + partial (residualize on dlen)
        if np.std(dls) > 0 and np.std(vals) > 0:
            r_len = float(np.corrcoef(vals, dls)[0, 1])
            beta = np.polyfit(dls, vals, 1)
            resid = vals - np.polyval(beta, dls)
            d_floor_partial = float(resid[labels == 1].mean()
                                    - resid[labels == 0].mean())
        else:
            r_len, d_floor_partial = 0.0, d_floor

    # context structure: variance of per-context agreement, context-shuffle null
    p_context = var_context = float("nan")
    if n_scored >= 2 and co_s:
        groups: dict[tuple, dict[str, list]] = {}
        for r in co_s:
            groups.setdefault((r["pair_id"], r["argset"]), {}).setdefault(
                r["context"], []).append(r["agree"])

        def ctx_var(assign: dict[tuple, dict[str, list]]) -> float:
            per_ctx = {c: [] for c in scored}
            for g in assign.values():
                for c, a in g.items():
                    per_ctx[c].extend(a)
            means = [np.mean(v) for v in per_ctx.values() if v]
            return float(np.var(means))

        var_context = ctx_var(groups)
        null_c = np.empty(N_PERM)
        keys = list(groups)
        for k in range(N_PERM):
            shuf = {}
            for key in keys:
                ctxs = list(groups[key])
                perm = rng.permutation(len(ctxs))
                shuf[key] = {ctxs[perm[i]]: groups[key][ctxs[i]]
                             for i in range(len(ctxs))}
            null_c[k] = ctx_var(shuf)
        p_context = _perm_p_greater(var_context, null_c)

    # pre-registered directional contact: A(C1) > A(C2), sign-flip perm
    d_dir = p_dir = float("nan")
    if "C1_direct" in scored and "C2_named" in scored:
        diffs = []
        for pid, ai in {(r["pair_id"], r["argset"]) for r in co_s}:
            c1 = [r["agree"] for r in co_s
                  if r["pair_id"] == pid and r["argset"] == ai
                  and r["context"] == "C1_direct"]
            c2 = [r["agree"] for r in co_s
                  if r["pair_id"] == pid and r["argset"] == ai
                  and r["context"] == "C2_named"]
            if c1 and c2:
                diffs.append(np.mean(c1) - np.mean(c2))
        if diffs:
            diffs_a = np.array(diffs)
            d_dir = float(diffs_a.mean())
            signs = rng.choice([-1.0, 1.0], size=(N_PERM, len(diffs_a)))
            null_d = (signs * np.abs(diffs_a)).mean(axis=1)
            p_dir = _perm_p_greater(d_dir, null_d)

    # bug-taxonomy ADVISORY (never load-bearing; feeds LEDGER-C)
    taxonomy = {"n_divergent": 0, "matches_naive": 0, "matches_weak": 0,
                "lambda_prefix": 0, "other": 0}
    for r in co_s:
        if r["agree"]:
            continue
        taxonomy["n_divergent"] += 1
        for m, ans in ((1, r["ans1"]), (2, r["ans2"])):
            if r[f"correct{m}"]:
                continue
            expr = CONTEXTS[r["context"]][2].format(
                T=r[f"t{m}"], a=ARGSETS[r["argset"]][0],
                b=ARGSETS[r["argset"]][1])
            hit = False
            for name, calc in (("matches_naive", R_NAIVE),
                               ("matches_weak", R_WEAK)):
                nf = _nf(expr, calc)
                if nf is not None and _agree(ans, nf):
                    taxonomy[name] += 1
                    hit = True
                    break
            if not hit:
                if ans.startswith("λ") or ans.startswith("\\"):
                    taxonomy["lambda_prefix"] += 1
                else:
                    taxonomy["other"] += 1

    # frozen verdict tree (exhaustive)
    if not g0_pass or n_scored < MIN_CONTEXTS or not cert_pass:
        verdict = "VOID"
    elif a_coext >= CEIL_BAND:
        verdict = "EXTENSIONAL"
    elif not (d_floor >= FLOOR_D and p_floor < ALPHA):
        verdict = "LEXICAL-FLOOR"
    elif p_context < ALPHA:
        verdict = "RATE-STRUCTURED"
    else:
        verdict = "RATE-UNSTRUCTURED"

    return {
        "verdict": verdict, "g0_pass": g0_pass, "det_dev": det_dev,
        "a_ceil": a_ceil, "a_coext": a_coext, "a_floor": a_floor,
        "n_coext_pairs": n_coext_pairs, "n_floor_pairs": n_floor_pairs,
        "cert_pass": cert_pass, "sensitivity": sens, "scored_contexts": scored,
        "n_scored_contexts": n_scored, "a_coext_by_context": a_coext_ctx,
        "d_floor": d_floor, "p_floor": p_floor, "r_len": r_len,
        "d_floor_partial": d_floor_partial,
        "var_context": var_context, "p_context": p_context,
        "d_dir_c1_c2": d_dir, "p_dir_c1_c2": p_dir,
        "taxonomy": taxonomy,
    }


# ---------------------------------------------------------------------------
# planted worlds (through the REAL analyse path)


def _synth(world: str, seed: int = 99) -> list[dict]:
    rng = np.random.default_rng(seed)
    coext = [(f"T{i}a", f"T{i}b", int(rng.integers(0, 4))) for i in range(16)]
    floor = [(f"F{i}a", f"F{i}b", int(rng.integers(0, 4))) for i in range(16)]
    agree_ctx = {"C1_direct": True, "C2_named": False, "C3_nested": True,
                 "C4_extra_arg": False, "C5_arg_position": True,
                 "C6_discard": True}
    recs: list[dict] = []

    def rec(kind, pid, t1, t2, ctx, ai, a1, a2, dlen):
        return {"kind": kind, "pair_id": pid, "t1": t1, "t2": t2,
                "context": ctx, "argset": ai, "raw1": a1, "raw2": a2,
                "ans1": a1, "ans2": a2, "agree": a1 == a2,
                "expected1": "x", "expected2": "x",
                "correct1": a1 == "x", "correct2": a2 == "x",
                "dlen_tok": dlen}

    for pid, (t1, t2, dlen) in enumerate(coext):
        for ctx in CONTEXTS:
            for ai in range(2):
                if world == "insensitive":
                    a1 = a2 = "a"
                elif ctx == "C6_discard":
                    a1 = a2 = "a"  # discard context: everyone agrees
                elif world == "extensional":
                    a1 = a2 = "x"
                elif world == "lexical":
                    a1, a2 = f"ans_{t1}", f"ans_{t2}"
                elif world == "rate":
                    a1 = "x"
                    a2 = "x" if agree_ctx[ctx] else f"bug_{t2}"
                elif world == "coin":
                    a1 = "x"
                    a2 = "x" if rng.random() < 0.5 else f"bug_{t2}"
                elif world == "nondet":
                    a1 = a2 = "x"
                else:
                    raise ValueError(world)
                recs.append(rec("coext", f"coext{pid}", t1, t2, ctx, ai,
                                a1, a2, dlen))
    for pid, (t1, t2, dlen) in enumerate(floor):
        for ctx in CONTEXTS:
            for ai in range(2):
                if world == "insensitive" or ctx == "C6_discard":
                    a1 = a2 = "a"
                else:
                    a1, a2 = f"ans_{t1}", f"ans_{t2}"
                recs.append(rec("floor", f"floor{pid}", t1, t2, ctx, ai,
                                a1, a2, dlen))
    for i in range(48):
        bad = world == "nondet" and i % 6 == 0
        recs.append(rec("ceil", f"ceil{i}", "T", "T", "C1_direct", 0,
                        "x", "y" if bad else "x", 0))
    return recs


def run_validate() -> int:
    log("--validate: 6 planted worlds through the REAL analyse path")
    expect = {
        "extensional": "EXTENSIONAL",
        "lexical": "LEXICAL-FLOOR",
        "rate": "RATE-STRUCTURED",
        "coin": "RATE-UNSTRUCTURED",
        "nondet": "VOID",
        "insensitive": "VOID",
    }
    fails = 0
    for world, want in expect.items():
        st = analyse(_synth(world), seed=7)
        got = st["verdict"]
        ok = got == want
        fails += 0 if ok else 1
        log(f"  {'✓' if ok else '✗'} {world:12s} want {want:17s} got {got:17s} "
            f"(A_co {st['a_coext']:.2f} A_fl {st['a_floor']:.2f} "
            f"D {st['d_floor']:.2f} p {st['p_floor']:.3f} "
            f"pctx {st['p_context']:.3f} scored {st['n_scored_contexts']})")
    log(f"validate: {6 - fails}/6")
    return 1 if fails else 0


# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    # smoke >= 4B, prefer 7B+ (Michael s347): the calculus function is not
    # fully formed below ~4B (s345 scar: 0.6B smoke degenerated the register)
    model_id = "Qwen/Qwen3-8B" if args.smoke and args.model_id == "Qwen/Qwen3-14B" \
        else args.model_id
    n_coext, n_floor, n_ceil = (8, 8, 24) if args.smoke else (N_COEXT, N_FLOOR, N_CEIL)

    corpus = build_corpus(n_coext, n_floor, SEED)
    corpus_hash = hashlib.sha256(
        json.dumps({k: corpus[k] for k in ("coext", "floor")},
                   sort_keys=True).encode()).hexdigest()[:8]
    cap = capture(model_id, corpus, n_ceil, SEED)
    stats = analyse(cap["records"])

    tag = "run_smoke" if args.smoke else "run_14b"
    out = Path(args.out) if args.out else _ROOT / "results" / "p_obs_equiv_s347" / tag
    out.mkdir(parents=True, exist_ok=True)
    with (out / "results.jsonl").open("w") as f:
        for r in cap["records"]:
            f.write(json.dumps(r, default=_json_native) + "\n")
    meta = {
        "run_id": f"p_obs_equiv_s347/{tag}",
        "timestamp": datetime.now(UTC).isoformat(),
        "model": model_id, "sampling": {"strategy": "greedy", "n": DECODE_N},
        "git_sha": git_sha(), "corpus_hash": corpus_hash, "seed": SEED,
        "n_perm": N_PERM, "frozen": "fab97fed",
        "corpus": {"coext": corpus["coext"], "floor": corpus["floor"],
                   "excluded": corpus["excluded"]},
        "driver_validity": cap["validity"],
        "stats": stats,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))
    log(f"VERDICT {stats['verdict']} | A_ceil {stats['a_ceil']:.3f} "
        f"A_coext {stats['a_coext']:.3f} A_floor {stats['a_floor']:.3f} | "
        f"D {stats['d_floor']:.3f} p {stats['p_floor']:.4f} | "
        f"pctx {stats['p_context']:.4f} | dir C1>C2 {stats['d_dir_c1_c2']:.3f} "
        f"p {stats['p_dir_c1_c2']:.4f} | scored {stats['scored_contexts']}")
    log(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
