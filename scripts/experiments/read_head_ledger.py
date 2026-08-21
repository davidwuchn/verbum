#!/usr/bin/env python3
"""§P-READ-HEAD-A ⋈ §P-CALCULUS-LEDGER-C — scoped substitution or induction? (s349).

FROZEN DESIGN: mementum/knowledge/explore/read-head-scope-vs-induction.md
(committed 19897379 BEFORE data, Michael GO "approved").

One engineered λ-capture corpus, two faces + a join:
  BEHAVIORAL (LEDGER-C) — does the model emit the NAIVE (capture) NF vs the
    HYGIENIC one? The powered sub-ceiling SE4 redo owed since s332.
  READ-MASS (READ-HEAD-A) — at the resolving emission (the body variable),
    does attention read the redex OPERAND (OP, scope-correct, FAR) or the
    recency occurrence (IND, the just-written binder, NEAR)?
    r = mass(OP) / (mass(OP)+mass(IND)) in the late band.
  JOIN — does read mis-attendance (1-r) predict behavioral capture?

Discriminator that beats the s204 induction confound: OP is FAR, IND is NEAR,
so substitution (mass on far OP) separates from recency-induction (mass on
near IND). Head-averaging is the FAITHFUL distributed read (s250); D_scope
cancels the position-generic bulk.

Nulls: induction-matched (OP absent → r must floor) + recency baseline
(r_rec = d_IND/(d_OP+d_IND); real r must beat inverse-distance) — the recency
baseline demotes the W-recency-adversary (r high only because OP is nearest).

FROZEN verdict tree + a-priori mass (sum 100):
  SCOPED-SUBSTITUTION  20  G2 (read beats induction+recency nulls) AND G3 join
  BEHAVIORAL-ONLY      35  naive behavior (powered) but read ambiguous / G2∧¬G3
  INDUCTION            25  read sits at the recency floor (mass on IND)
  HYGIENIC              5  capture-avoiding NF dominant (contradicts s332)
  VOID                 15  G0 fail / control-read broken / MIN trials unreached

`--validate` drives 6 planted worlds through the REAL analyse path (s331),
incl. the W-recency-adversary (must NOT read SCOPED-SUBSTITUTION).

Bounds (frozen): head-averaged read (the faithful distributed read, s250);
observational not causal (s204); n=1, greedy, single model (Qwen3-14B);
resolving-emission alignment → exclude & count on miss.

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
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_ROOT = _SCRIPT_DIR.parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from verbum.lambda_ast import (  # noqa: E402
    R_NAIVE,
    R_NORMAL,
    alpha_eq,
    normal_form,
    parse,
    pretty,
)

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (s349 pre-data freeze 19897379)

SEED = 349
LATE_BAND = (0.75, 1.0)     # top 25% layers — the s346 read-mass locus
DECODE_N = 24               # NF is short; halt on eos
R_DELTA = 0.10              # min excess over induction floor / recency baseline
FRAC_CEIL = 0.98            # frac_naive ceiling guard (join needs variance)
MIN_TRIALS = 12             # scored capture trials after exclusions (else VOID)
R_CTRL_MIN = 0.60           # control-read sanity: instrument finds OP unchallenged
N_PERM = 5000
ALPHA = 0.05
MAX_STEPS = 500

# few-shot header pins the answer register (obs_equiv A3 lesson): reduce to NF,
# answer-only; worked atoms disjoint from the corpus variable set {x,y,z,w,u,v}.
HEADER = (
    "Lambda calculus: reduce each application to its normal form. "
    "Substitute the argument for the bound variable; answer with ONLY the "
    "final term.\n\n"
    "(\\p.p) q = q\n"
    "(\\f.\\g.f) m = \\g.m\n"
)

# corpus dials: shadow binder letter s, extra binders between λs and the x-use
# (binder_distance), and shadow_count (how many same-name binders intervene).
SHADOW_LETTERS = ["y", "z", "w", "u", "v"]
EXTRA_BINDERS = [[], ["a"], ["a", "b"], ["a", "b", "c"]]   # binder_distance dial
SHADOW_COUNTS = [1, 2]                                     # shadow_count dial


def log(msg: str) -> None:
    print(f"[read-head-ledger] {msg}", flush=True)


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
# corpus — engineered capture terms + matched controls + induction-null items


def _nf(expr: str, calc) -> str | None:
    try:
        return pretty(normal_form(parse(expr), max_steps=MAX_STEPS, calc=calc))
    except Exception:
        return None


def _build_term(shadow: str, extra: list[str], count: int,
                *, capture: bool) -> dict | None:
    """Build (λx.λs1...λsN.λextra.x) V.

    capture=True  → operand V == shadow letter (naive captures under λs).
    capture=False → operand V is a fresh letter (naive ≡ hygienic; control).
    body variable after substitution = V (the operand letter).
    """
    binders = [shadow] * count + extra          # shadow binders then extras
    operand = shadow if capture else "v0"        # fresh operand for control
    if not capture and shadow == "v0":
        return None
    lam = "".join(f"\\{b}." for b in binders)
    term = f"(\\x.{lam}x) {operand}"
    naive = _nf(term, R_NAIVE)
    hygienic = _nf(term, R_NORMAL)
    if naive is None or hygienic is None:
        return None
    try:
        distinct = not alpha_eq(parse(naive), parse(hygienic))
    except Exception:
        return None
    # capture MUST make naive≠hygienic; control MUST make them equal
    if capture != distinct:
        return None
    return {
        "term": term, "operand": operand, "shadow": shadow,
        "binder_distance": len(binders), "shadow_count": count,
        "naive_nf": naive, "hygienic_nf": hygienic, "capture": capture,
    }


def build_corpus(seed: int, *, smoke: bool) -> dict:
    """Capture family + matched controls + induction-null items. Exclusions logged."""
    rng = np.random.default_rng(seed)
    capture_items, control_items, excluded = [], [], []
    for s in SHADOW_LETTERS:
        for extra in EXTRA_BINDERS:
            for cnt in SHADOW_COUNTS:
                it = _build_term(s, extra, cnt, capture=True)
                (capture_items if it else excluded).append(
                    it or (s, extra, cnt, "capture"))
                ct = _build_term(s, extra, cnt, capture=False)
                (control_items if ct else excluded).append(
                    ct or (s, extra, cnt, "control"))
    excluded = [e for e in excluded if isinstance(e, tuple)]

    # induction-null items: identity-copy `\s.s` — the emitted s has NO operand
    # source, only the recency (binder) occurrence → r must floor (the induction
    # baseline to beat).
    nullind = [{"term": f"\\{s}.{s}", "operand": s, "shadow": s,
                "binder_distance": 0, "shadow_count": 0,
                "naive_nf": f"\\{s}.{s}", "hygienic_nf": f"\\{s}.{s}",
                "capture": None} for s in SHADOW_LETTERS]

    if smoke:
        capture_items = capture_items[:8]
        control_items = control_items[:8]
        nullind = nullind[:3]
    rng.shuffle(capture_items)
    rng.shuffle(control_items)
    log(f"corpus: capture {len(capture_items)} | control {len(control_items)} | "
        f"nullind {len(nullind)} | excluded {len(excluded)}")
    return {"capture": capture_items, "control": control_items,
            "nullind": nullind, "excluded": excluded}


# ---------------------------------------------------------------------------
# capture (driver: read-mass + behavioral, one bounce per term)


def _extract_nf(text: str) -> str | None:
    """First line, chain-tolerant (final term after last '='), kernel-normalised."""
    ans = text.split("\n")[0].strip().rstrip("=. ").strip()
    if "=" in ans:
        ans = ans.rsplit("=", 1)[1].strip()
    ans = " ".join(ans.split())
    if not ans:
        return None
    try:
        return pretty(parse(ans))
    except Exception:
        return ans


def _classify_beh(nf: str | None, naive: str, hygienic: str) -> str:
    if nf is None:
        return "other"
    try:
        p = parse(nf)
        if alpha_eq(p, parse(naive)):
            return "naive"
        if alpha_eq(p, parse(hygienic)):
            return "hygienic"
    except Exception:
        return "other"
    return "other"


def capture(model_id: str, corpus: dict, seed: int) -> dict:
    from verbum.driver import Driver

    d = Driver(model_id=model_id)
    validity = d.validity()
    log(f"driver validity: {validity}")
    lo = int(d.n_layers * LATE_BAND[0])
    hi = int(np.ceil(d.n_layers * LATE_BAND[1]))

    def tok_texts(ids: list[int]) -> list[str]:
        return [d.tok.decode([i]).strip() for i in ids]

    def measure(item: dict, kind: str, double: bool = False) -> dict:
        prompt = HEADER + item["term"] + " = "
        b = d.bounce(prompt, n=DECODE_N, hidden=False, attn=True,
                     stop_at_eos=True, keep_seal=False)
        out_text = "".join(b.tokens)
        nf = _extract_nf(out_text)
        beh = _classify_beh(nf, item["naive_nf"], item["hygienic_nf"])

        tape_ids = list(b.prompt_ids)          # frame k (text path) ↔ new_ids[k]
        plen = len(tape_ids)
        texts_prompt = tok_texts(tape_ids)
        texts_out = tok_texts(b.new_ids)
        v = item["operand"]

        # OP = operand occurrence in the prompt: the last prompt token == v that
        # precedes the final " = " (the argument slot).
        eq_idx = max((i for i, t in enumerate(texts_prompt) if t == "="),
                     default=plen)
        op_cands = [i for i, t in enumerate(texts_prompt[:eq_idx]) if t == v]
        op_pos = op_cands[-1] if op_cands else None

        # resolving emission k*: the LAST emitted token == v within the first NF
        # (before a second '=' / newline). Its absolute tape column = plen + k*.
        stop = next((k for k, t in enumerate(texts_out) if t in ("=", "")),
                    len(texts_out))
        res_cands = [k for k in range(min(stop, len(b.attn))) if texts_out[k] == v]
        k_star = res_cands[-1] if res_cands else None

        rec: dict = {
            "kind": kind, "term": item["term"], "operand": v,
            "binder_distance": item["binder_distance"],
            "shadow_count": item["shadow_count"],
            "beh": beh, "nf": nf, "out_text": out_text,
            "r": None, "d_op": None, "d_ind": None, "r_rec": None,
            "has_competitor": False, "excluded": None,
        }
        if op_pos is None or k_star is None:
            rec["excluded"] = "no_op" if op_pos is None else "no_resolving_emit"
            return rec

        res_abs = plen + k_star
        rm = d.read_mass(b, step=k_star)          # [L, T_k], T_k = res_abs+1
        band = rm[lo:hi, :].mean(axis=0)          # [T_k] late-band mass
        # IND = nearest prior column (< res_abs) whose token == v, excluding OP.
        full_texts = texts_prompt + tok_texts(b.new_ids[:k_star])
        ind_cands = [i for i in range(res_abs) if i < len(full_texts)
                     and full_texts[i] == v and i != op_pos]
        ind_pos = max(ind_cands) if ind_cands else None

        m_op = float(band[op_pos]) if op_pos < len(band) else 0.0
        if ind_pos is None:
            rec.update({"r": 1.0, "d_op": res_abs - op_pos, "d_ind": None,
                        "r_rec": 1.0, "has_competitor": False,
                        "m_op": m_op, "m_ind": 0.0})
            return rec
        m_ind = float(band[ind_pos]) if ind_pos < len(band) else 0.0
        denom = m_op + m_ind
        r = m_op / denom if denom > 0 else float("nan")
        d_op = res_abs - op_pos
        d_ind = res_abs - ind_pos
        r_rec = d_ind / (d_op + d_ind)            # inverse-distance recency baseline
        rec.update({"r": r, "d_op": d_op, "d_ind": d_ind, "r_rec": r_rec,
                    "has_competitor": True, "m_op": m_op, "m_ind": m_ind})
        if double:
            b2 = d.bounce(prompt, n=DECODE_N, hidden=False, attn=True,
                          stop_at_eos=True, keep_seal=False)
            rec["det_tokens_match"] = ("".join(b2.tokens) == out_text)
        return rec

    records: list[dict] = []
    t0 = time.time()
    for i, item in enumerate(corpus["capture"]):
        records.append(measure(item, "capture", double=(i < 4)))
        log(f"capture {i} {item['term']!r} → {records[-1]['beh']} "
            f"r={records[-1]['r']} [{time.time() - t0:.0f}s]")
    for item in corpus["control"]:
        records.append(measure(item, "control"))
    for item in corpus["nullind"]:
        records.append(measure(item, "nullind"))
    log(f"capture complete: {len(records)} records [{time.time() - t0:.0f}s]")
    return {"records": records, "validity": validity}


# ---------------------------------------------------------------------------
# analyse (REAL path — planted worlds drive this same function)


def _perm_p_greater(obs: float, null: np.ndarray) -> float:
    return float((np.sum(null >= obs) + 1) / (len(null) + 1))


def _binom_p_greater(k: int, n: int, p0: float = 0.5) -> float:
    """One-sided binomial P(X >= k | n, p0) via normal-free exact-ish tail."""
    if n == 0:
        return float("nan")
    from math import comb
    return float(sum(comb(n, i) * p0**i * (1 - p0)**(n - i) for i in range(k, n + 1)))


def analyse(records: list[dict], seed: int = SEED,
            min_trials: int = MIN_TRIALS) -> dict:
    rng = np.random.default_rng(seed)
    cap = [r for r in records if r["kind"] == "capture"]
    ctrl = [r for r in records if r["kind"] == "control"]
    nullind = [r for r in records if r["kind"] == "nullind"]

    # G0 — determinism + control-read sanity + MIN trials
    det = [r.get("det_tokens_match") for r in cap if "det_tokens_match" in r]
    det_pass = bool(det) and all(det)
    cap_scored = [r for r in cap if r["excluded"] is None
                  and r["has_competitor"] and not np.isnan(r["r"])]
    ctrl_r = [r["r"] for r in ctrl if r["excluded"] is None and r["r"] is not None]
    ctrl_read_ok = bool(ctrl_r) and float(np.mean(ctrl_r)) >= R_CTRL_MIN
    n_scored = len(cap_scored)
    g0_pass = det_pass and ctrl_read_ok and n_scored >= min_trials
    n_excluded = sum(1 for r in cap if r["excluded"] is not None)

    # G1 — behavioral: naive vs hygienic among DECIDED capture trials
    decided = [r for r in cap if r["beh"] in ("naive", "hygienic")]
    n_naive = sum(1 for r in decided if r["beh"] == "naive")
    n_dec = len(decided)
    frac_naive = n_naive / n_dec if n_dec else float("nan")
    p_naive = _binom_p_greater(n_naive, n_dec) if n_dec else float("nan")
    p_hygienic = _binom_p_greater(n_dec - n_naive, n_dec) if n_dec else float("nan")
    g1_naive = (n_dec > 0 and frac_naive > 0.5 and p_naive < ALPHA
                and frac_naive < FRAC_CEIL)
    hygienic_dom = n_dec > 0 and frac_naive < 0.5 and p_hygienic < ALPHA

    # G2 — read follows OP (substitution) beating BOTH nulls
    r_vals = np.array([r["r"] for r in cap_scored], dtype=float)
    rrec_vals = np.array([r["r_rec"] for r in cap_scored], dtype=float)
    mean_r = float(np.mean(r_vals)) if len(r_vals) else float("nan")
    # induction-matched floor: r on nullind (OP absent → set r=0 competitor-free)
    floor_r = [r["r"] for r in nullind if r["excluded"] is None and r["r"] is not None]
    r0 = float(np.mean(floor_r)) if floor_r else 0.0
    # beats induction floor (permute capture vs nullind labels)
    d_floor = mean_r - r0
    p_g2_floor = float("nan")
    if len(r_vals) and floor_r:
        pooled = np.concatenate([r_vals, np.array(floor_r)])
        lab = np.array([1] * len(r_vals) + [0] * len(floor_r))
        null = np.empty(N_PERM)
        for k in range(N_PERM):
            pl = rng.permutation(lab)
            null[k] = pooled[pl == 1].mean() - pooled[pl == 0].mean()
        p_g2_floor = _perm_p_greater(d_floor, null)
    # beats recency baseline (paired sign-flip on r - r_rec)
    d_rec = float(np.mean(r_vals - rrec_vals)) if len(r_vals) else float("nan")
    p_g2_rec = float("nan")
    if len(r_vals):
        diffs = r_vals - rrec_vals
        signs = rng.choice([-1.0, 1.0], size=(N_PERM, len(diffs)))
        null_r = (signs * np.abs(diffs)).mean(axis=1)
        p_g2_rec = _perm_p_greater(d_rec, null_r)
    g2_pass = (mean_r > 0.5 and d_floor >= R_DELTA and p_g2_floor < ALPHA
               and d_rec >= R_DELTA and p_g2_rec < ALPHA)
    # induction: read at the recency floor, mass on IND
    induction = (not g2_pass) and mean_r < 0.5 and (mean_r - r0) < R_DELTA

    # G3 — join: mis-attend (1-r) predicts behavioral capture (point-biserial)
    join_rows = [r for r in cap_scored if r["beh"] in ("naive", "hygienic")]
    rho_join = p_join = float("nan")
    if len(join_rows) >= 4:
        x = np.array([1.0 - r["r"] for r in join_rows])           # mis-attend
        y = np.array([1.0 if r["beh"] == "naive" else 0.0 for r in join_rows])
        if np.std(x) > 0 and np.std(y) > 0:
            rho_join = float(np.corrcoef(x, y)[0, 1])
            null_j = np.empty(N_PERM)
            for k in range(N_PERM):
                null_j[k] = np.corrcoef(x, rng.permutation(y))[0, 1]
            p_join = _perm_p_greater(rho_join, null_j)
    g3_pass = not np.isnan(rho_join) and rho_join > 0 and p_join < ALPHA

    # D_scope — differenced read (capture has-competitor vs control no-competitor)
    d_scope = float("nan")
    if len(r_vals) and ctrl_r:
        d_scope = float(np.mean(ctrl_r) - mean_r)  # >0 ⇒ competitor pulled r down

    # frozen verdict tree (exhaustive)
    if not g0_pass:
        verdict = "VOID"
    elif hygienic_dom:
        verdict = "HYGIENIC"
    elif not g1_naive:
        # naive neither dominant-significant nor sub-ceiling → cannot ground the
        # behavioral face → VOID (frac at ceiling or undecided)
        verdict = "VOID"
    elif g2_pass and g3_pass:
        verdict = "SCOPED-SUBSTITUTION"
    elif induction:
        verdict = "INDUCTION"
    else:
        verdict = "BEHAVIORAL-ONLY"

    return {
        "verdict": verdict, "g0_pass": g0_pass, "det_pass": det_pass,
        "ctrl_read_ok": ctrl_read_ok,
        "ctrl_r": float(np.mean(ctrl_r)) if ctrl_r else float("nan"),
        "n_scored": n_scored, "n_excluded": n_excluded,
        "g1_naive": g1_naive, "hygienic_dom": hygienic_dom,
        "frac_naive": frac_naive, "n_naive": n_naive, "n_decided": n_dec,
        "p_naive": p_naive, "p_hygienic": p_hygienic,
        "mean_r": mean_r, "r0_floor": r0, "d_floor": d_floor,
        "p_g2_floor": p_g2_floor, "d_rec": d_rec, "p_g2_rec": p_g2_rec,
        "g2_pass": g2_pass, "induction": induction, "d_scope": d_scope,
        "rho_join": rho_join, "p_join": p_join, "g3_pass": g3_pass,
    }


# ---------------------------------------------------------------------------
# planted worlds (through the REAL analyse path)


def _synth(world: str, seed: int = 99) -> list[dict]:
    rng = np.random.default_rng(seed)
    recs: list[dict] = []

    def cap_rec(i, r, r_rec, beh, det=None):
        d = {"kind": "capture", "term": f"cap{i}", "operand": "y",
             "binder_distance": 2, "shadow_count": 1, "beh": beh,
             "nf": beh, "out_text": beh, "r": r, "d_op": 6, "d_ind": 1,
             "r_rec": r_rec, "has_competitor": True, "excluded": None,
             "m_op": r, "m_ind": 1 - r}
        if det is not None:
            d["det_tokens_match"] = det
        return d

    for i in range(20):
        det = True if i < 4 else None
        if world == "scope":
            # substitution: OP-dominant overall (mean r>0.5, beats recency
            # r_rec=0.14 and the induction floor), AND its residual scope-blind
            # drift toward IND predicts capture: naive→lower r, hygienic→clean OP
            beh = "naive" if rng.random() < 0.75 else "hygienic"
            r = 0.68 if beh == "naive" else 0.95   # mis-attend(1-r) ↑ ⇒ capture
            recs.append(cap_rec(i, r, 0.14, beh, det))
        elif world == "induction":
            beh = "naive" if rng.random() < 0.7 else "hygienic"
            recs.append(cap_rec(i, 0.12, 0.14, beh, det))     # r at recency floor
        elif world == "behavioral":
            beh = "naive" if rng.random() < 0.75 else "hygienic"
            recs.append(cap_rec(i, 0.50, 0.48, beh, det))     # r ambiguous
        elif world == "hygienic":
            beh = "hygienic" if rng.random() < 0.85 else "naive"
            recs.append(cap_rec(i, 0.5, 0.5, beh, det))
        elif world == "recency_adversary":
            # r high BUT because OP is nearest → r_rec ALSO high → r-r_rec≈0
            beh = "naive" if rng.random() < 0.75 else "hygienic"
            rr = cap_rec(i, 0.90, 0.88, beh, det)
            rr["d_op"], rr["d_ind"] = 1, 6
            recs.append(rr)
        elif world == "degenerate":
            recs.append(cap_rec(i, 0.9, 0.14, "naive", det=(i % 4 != 0)))
        else:
            raise ValueError(world)
    # controls (no competitor → r≈1) and nullind floor
    for i in range(12):
        recs.append({"kind": "control", "term": f"ctl{i}", "operand": "v0",
                     "binder_distance": 2, "shadow_count": 1, "beh": "naive",
                     "nf": "x", "out_text": "x", "r": 0.97, "d_op": 6,
                     "d_ind": None, "r_rec": 1.0, "has_competitor": False,
                     "excluded": None, "m_op": 0.97, "m_ind": 0.0})
    for i in range(5):
        recs.append({"kind": "nullind", "term": f"nul{i}", "operand": "y",
                     "binder_distance": 0, "shadow_count": 0, "beh": "other",
                     "nf": None, "out_text": "", "r": 0.10, "d_op": 1,
                     "d_ind": None, "r_rec": 0.10, "has_competitor": False,
                     "excluded": None, "m_op": 0.1, "m_ind": 0.9})
    return recs


def run_validate() -> int:
    assert _extract_nf("\\y.y\nfoo") == "λy.y"
    assert _extract_nf("(\\x.x) y = y\nnext") == "y"
    assert _classify_beh("\\y.y", "\\y.y", "\\y'.y") == "naive"
    assert _classify_beh("\\y'.y", "\\y.y", "\\y'.y") == "hygienic"
    log("--validate: 6 planted worlds through the REAL analyse path")
    expect = {
        "scope": "SCOPED-SUBSTITUTION",
        "induction": "INDUCTION",
        "behavioral": "BEHAVIORAL-ONLY",
        "hygienic": "HYGIENIC",
        "recency_adversary": "BEHAVIORAL-ONLY",
        "degenerate": "VOID",
    }
    fails = 0
    for world, want in expect.items():
        st = analyse(_synth(world), seed=7, min_trials=8)
        got = st["verdict"]
        ok = got == want
        fails += 0 if ok else 1
        log(f"  {'✓' if ok else '✗'} {world:18s} want {want:20s} got {got:20s} "
            f"(r {st['mean_r']:.2f} d_fl {st['d_floor']:.2f} p {st['p_g2_floor']:.3f} "
            f"d_rec {st['d_rec']:.2f} p {st['p_g2_rec']:.3f} "
            f"fnaive {st['frac_naive']:.2f} rho {st['rho_join']:.2f} "
            f"p {st['p_join']:.3f})")
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

    model_id = "Qwen/Qwen3-8B" if args.smoke and args.model_id == "Qwen/Qwen3-14B" \
        else args.model_id
    corpus = build_corpus(SEED, smoke=args.smoke)
    corpus_hash = hashlib.sha256(
        json.dumps({k: [it["term"] for it in corpus[k]]
                    for k in ("capture", "control", "nullind")},
                   sort_keys=True).encode()).hexdigest()[:8]
    cap = capture(model_id, corpus, SEED)
    min_trials = 4 if args.smoke else MIN_TRIALS
    stats = analyse(cap["records"], min_trials=min_trials)

    tag = "run_smoke" if args.smoke else "run_14b"
    out = (Path(args.out) if args.out
           else _ROOT / "results" / "p_read_head_ledger_s349" / tag)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "results.jsonl").open("w") as f:
        for r in cap["records"]:
            f.write(json.dumps(r, default=_json_native) + "\n")
    meta = {
        "run_id": f"p_read_head_ledger_s349/{tag}",
        "timestamp": datetime.now(UTC).isoformat(),
        "model": model_id, "sampling": {"strategy": "greedy", "n": DECODE_N},
        "git_sha": git_sha(), "corpus_hash": corpus_hash, "seed": SEED,
        "n_perm": N_PERM, "frozen": "19897379",
        "corpus_excluded": corpus["excluded"],
        "driver_validity": cap["validity"],
        "stats": stats,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))
    log(f"VERDICT {stats['verdict']} | g0 {stats['g0_pass']} "
        f"frac_naive {stats['frac_naive']:.3f} (n {stats['n_decided']}) | "
        f"mean_r {stats['mean_r']:.3f} floor {stats['r0_floor']:.3f} "
        f"d_rec {stats['d_rec']:.3f} | rho_join {stats['rho_join']:.3f} "
        f"p {stats['p_join']:.4f} | n_scored {stats['n_scored']} "
        f"excl {stats['n_excluded']}")
    log(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
