"""§P-SUBST-ENGINE — RE the substitution engine (the ALU). Behavioral sweep.

PRE-REGISTRATION: the-benchmark-is-the-re-oracle.md §8 (DRAFT — awaiting Michael
GO; a-priori mass PROPOSED, not yet frozen). This harness is built VALIDATE-ONLY:
`--validate` proves the gate logic on planted worlds with synthetic oracles and
loads NO model. The real sweep (`--out …`) waits for the freeze GO.

THE QUESTION (s330, Michael "hard one first"): does the model run capture-avoiding
or naive substitution, and where does it break? Substitution only exists at binder
level — subst_pairs.py builds terms whose capture-avoiding normal form differs from
the naive (capture-unsafe) one; each ships BOTH certified NFs (§2b: we grade which
algorithm the model matches, the naive answer is a real reproducible fingerprint).

READOUT (λ measure — behavioral COMPUTATIONAL-ACCURACY, forced-choice; the
linearity_bias.py pattern): each term is scored against candidate normal forms
{correct_nf, naive_nf, distractors} by length-normalized logprob; the pick is the
argmax. is_correct = picked correct_nf; is_naive = picked naive_nf.

GATES (frozen decision tree — verdict precedence pre-registered):
  SE0  sanity     — accuracy on non-capturing controls ≥ floor (else VOID)
  SE1  algorithm  — among capture pairs, correct_nf vs naive_nf selection
  SE2  cliff      — accuracy falls with binder_distance / shadow_depth /
                    functional_order (correct shallow, naive past a cliff)
  SE3  alpha      — accuracy moves under bound-variable renaming (routing signature)
  SE4  crosslink  — instruct shows MORE naive (first-binder) intrusions than its
                    PAIRED base on shadowed pairs (s328/s329 installed-primacy as a
                    deployment-face binding bug); computed across two runs.

VERDICT PRECEDENCE (frozen): VOID(¬SE0) > ALPHA-VARIANT-ROUTER(SE3) >
DEPTH-DEPENDENT-MIXED(SE2) > CAPTURE-AVOIDING / NAIVE-SUBST(SE1) > VOID.

NULLS (λ yardstick, mandatory before any positive is read): token-budget null
(traced arm — uninformative length-matched trace; the confound that killed
FUEL/TRACE-FUEL/NF-GAUGE x3) · alpha-pair self-null (renaming delta vs resampled
same-term noise) · shuffled-binder-label null (white-box edge read, advisory).

Usage:
  uv run python scripts/experiments/subst_engine.py --validate      # NO model
  uv run python scripts/experiments/subst_engine.py --smoke --out … # AFTER GO
  uv run python scripts/experiments/subst_engine.py --model-id … --out …

License: MIT (lambda provenance).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from verbum.lambda_ast import (  # noqa: E402
    R_NAIVE,
    R_NORMAL,
    Atom,
    Lam,
    Status,
    alpha_eq,
    free_vars,
    normal_form,
    parse,
    pretty,
    reduce,
)
from verbum.probes.subst_pairs import (  # noqa: E402
    alpha_pairs,
    capture_pairs,
)

# ── frozen constants (the decision tree; a-priori mass lives in the pre-reg) ──
ALPHA = 0.05
N_PERM = 2000
SE0_FLOOR = 0.60  # controls must be solved above this (else instrument VOID)
SE1_MARGIN = 0.15  # |frac_correct - 0.5| to call CAPTURE/NAIVE cleanly
SE2_SHALLOW_FLOOR = 0.60  # a cliff requires competence at the shallow end
SE4_MIN_N = 8  # shadowed pairs per model for the cross-link test

_DISTRACTOR_ATOMS = ("q", "r", "s")


# ══════════════════════════════════════════════════════════════════════════
# Candidate construction — the forced-choice options for NF-selection
# ══════════════════════════════════════════════════════════════════════════
def _swap_free_var(nf_src: str, repl: str) -> str | None:
    """A plausible wrong answer: rename the first free variable of the NF to
    ``repl`` (a substitution-target error), keeping the term well-formed."""
    t = parse(nf_src)
    fvs = sorted(free_vars(t))
    if not fvs or repl in fvs:
        return None
    target = fvs[0]

    def go(term):
        if isinstance(term, Atom):
            return Atom(repl) if term.name == target else term
        if isinstance(term, Lam):
            if term.var == target:
                return term
            return Lam(term.var, go(term.body))
        if hasattr(term, "fn"):
            return type(term)(go(term.fn), go(term.arg))
        return term

    out = pretty(go(t))
    return out if out != nf_src else None


def _drop_binder(nf_src: str) -> str | None:
    """A plausible under-computation: strip the outermost binder from the NF."""
    t = parse(nf_src)
    if isinstance(t, Lam):
        return pretty(t.body)
    return None


def _dup_atom(nf_src: str) -> str | None:
    """A plausible copy error: self-apply a bare atom (``a`` -> ``a a``)."""
    t = parse(nf_src)
    if isinstance(t, Atom):
        return f"{t.name} {t.name}"
    return None


def _perturb_leaf(nf_src: str, repl: str) -> str | None:
    """A plausible wrong body: replace the LEFTMOST leaf with ``repl`` (works on
    closed terms where free-var swaps have nothing to bite on)."""
    t = parse(nf_src)
    done = [False]

    def go(term):
        if done[0]:
            return term
        if isinstance(term, Atom):
            done[0] = True
            return Atom(repl) if term.name != repl else term
        if isinstance(term, Lam):
            return Lam(term.var, go(term.body))
        if hasattr(term, "fn"):
            fn = go(term.fn)
            arg = go(term.arg)
            return type(term)(fn, arg)
        return term

    out = pretty(go(t))
    return out if out != nf_src else None


def _distractor_pool(correct_nf: str) -> list[str]:
    """Well-formed wrong answers, most-plausible first: free-var swaps · leftmost
    leaf perturbations (cover closed terms) · binder-drop · atom self-application."""
    pool: list[str] = []
    for repl in _DISTRACTOR_ATOMS:
        d = _swap_free_var(correct_nf, repl)
        if d is not None:
            pool.append(d)
    for repl in _DISTRACTOR_ATOMS:
        d = _perturb_leaf(correct_nf, repl)
        if d is not None:
            pool.append(d)
    for fn in (_drop_binder, _dup_atom):
        d = fn(correct_nf)
        if d is not None:
            pool.append(d)
    return pool


def make_candidates(correct_nf: str, naive_nf: str | None) -> dict | None:
    """Distinct forced-choice options: always ``correct``; ``naive`` when the pair
    discriminates; distractors drawn from the pool until ≥3 total (alpha-aware, so
    a distractor never coincides with correct/naive). Returns None if <3 buildable
    — a control that cannot be triple-optioned is dropped, not silently mis-scored."""
    cands: dict[str, str] = {"correct": correct_nf}
    correct_t = parse(correct_nf)
    fixed = [correct_t]
    if naive_nf is not None and not alpha_eq(parse(naive_nf), correct_t):
        cands["naive"] = naive_nf
        fixed.append(parse(naive_nf))

    key = 0
    for d in _distractor_pool(correct_nf):
        dt = parse(d)
        if any(alpha_eq(dt, f) for f in fixed) or d in cands.values():
            continue
        cands[f"d{key}"] = d
        fixed.append(dt)
        key += 1

    if len(set(cands.values())) < 3:
        return None
    return cands


# ══════════════════════════════════════════════════════════════════════════
# Control battery — non-capturing β (SE0 sanity); correct_nf is unambiguous
# ══════════════════════════════════════════════════════════════════════════
_CONTROL_TERMS = (
    "(λx.x) a",
    "(λx.λy.x) a b",
    "(λx.λy.y) a b",
    "(λf.λx.f (f x)) g z",
    "(λx.x x) g",
    "(λf.λg.λx.f (g x)) h k z",
    "(λx.λy.x y) p q",
)


def build_battery() -> list[dict]:
    """One record per UNIQUE term (each scored under three presentation arms —
    direct / traced / token-budget-null — in the scoring loop). Sources are the
    direct-mode subst_pairs probes (the traced/direct split is now a scoring-time
    arm, not a duplicated probe): controls (SE0) + capture (SE1/SE2/SE4) + alpha
    (SE3). ``surface`` distinguishes term vs alpha-variant presentations."""
    recs: list[dict] = []

    for i, src in enumerate(_CONTROL_TERMS):
        nf = pretty(normal_form(parse(src)))
        recs.append({
            "id": f"ctrl_{i:03d}", "family": "control", "surface": "term",
            "prompt": src, "correct_nf": nf, "naive_nf": None,
            "binder_distance": 0, "shadow_depth": 0, "functional_order": 0,
        })

    for p in capture_pairs():
        if p.mode != "direct":  # dedupe: one record per term, arms handled at scoring
            continue
        recs.append({
            "id": p.id, "family": "capture", "surface": "term",
            "prompt": p.term, "correct_nf": p.correct_nf, "naive_nf": p.naive_nf,
            "binder_distance": p.dials.binder_distance,
            "shadow_depth": p.dials.shadow_depth,
            "functional_order": p.dials.functional_order or 0,
        })

    for p in alpha_pairs():
        if p.mode != "direct":
            continue
        for surface, prompt in (("term", p.term), ("variant", p.alpha_variant)):
            recs.append({
                "id": f"{p.id}_{surface}", "family": "alpha", "surface": surface,
                "prompt": prompt, "correct_nf": p.correct_nf, "naive_nf": None,
                "binder_distance": p.dials.binder_distance,
                "shadow_depth": p.dials.shadow_depth,
                "functional_order": p.dials.functional_order or 0,
            })
    return recs


# ══════════════════════════════════════════════════════════════════════════
# Statistics (pure) — permutation nulls, no torch
# ══════════════════════════════════════════════════════════════════════════
def _json_native(o):
    """json.dump default: coerce numpy scalar types to native Python."""
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


def _binom_two_sided_p(k: int, n: int) -> float:
    """Two-sided normal-approx p that a proportion differs from 0.5."""
    if n == 0:
        return 1.0
    z = (k - n / 2) / math.sqrt(n / 4)
    return math.erfc(abs(z) / math.sqrt(2))


def _median_split_stat(correct: np.ndarray, dial: np.ndarray) -> float:
    """acc(shallow) - acc(deep) at the dial median. Positive ⇒ cliff."""
    if len(dial) == 0 or np.all(dial == dial[0]):
        return 0.0
    med = np.median(dial)
    lo, hi = dial <= med, dial > med
    if lo.sum() == 0 or hi.sum() == 0:
        return 0.0
    return float(correct[lo].mean() - correct[hi].mean())


def _perm_p_split(correct: np.ndarray, dial: np.ndarray, rng, n_perm=N_PERM) -> float:
    obs = _median_split_stat(correct, dial)
    if obs == 0.0:
        return 1.0
    count = 0
    for _ in range(n_perm):
        perm = rng.permutation(correct)
        if abs(_median_split_stat(perm, dial)) >= abs(obs) - 1e-12:
            count += 1
    return (count + 1) / (n_perm + 1)


def _perm_p_delta(a: np.ndarray, b: np.ndarray, rng, n_perm=N_PERM) -> float:
    """Two-sided permutation p for mean(a) - mean(b) via label shuffling."""
    obs = a.mean() - b.mean() if len(a) and len(b) else 0.0
    if obs == 0.0:
        return 1.0
    pooled = np.concatenate([a, b])
    na = len(a)
    count = 0
    for _ in range(n_perm):
        perm = rng.permutation(pooled)
        if abs(perm[:na].mean() - perm[na:].mean()) >= abs(obs) - 1e-12:
            count += 1
    return (count + 1) / (n_perm + 1)


# ══════════════════════════════════════════════════════════════════════════
# Gates + verdict (PURE — what --validate exercises)
# ══════════════════════════════════════════════════════════════════════════
def compute_gates(recs: list[dict], rng) -> dict:
    ctrl = [r for r in recs if r["family"] == "control"]
    caps = [r for r in recs if r["family"] == "capture"]
    alph = [r for r in recs if r["family"] == "alpha"]

    # ── SE0 sanity ──
    acc_ctrl = float(np.mean([r["correct"] for r in ctrl])) if ctrl else 0.0
    se0 = acc_ctrl >= SE0_FLOOR

    # ── SE1 algorithm identification (decisive picks: correct XOR naive) ──
    decisive = [r for r in caps if r["correct"] or r.get("naive")]
    k_correct = sum(1 for r in decisive if r["correct"])
    n_dec = len(decisive)
    frac_correct = k_correct / n_dec if n_dec else 0.5
    p1 = _binom_two_sided_p(k_correct, n_dec)
    acc_cap = float(np.mean([r["correct"] for r in caps])) if caps else 0.0

    # ── SE2 cliff (per dial: acc falls shallow→deep) ──
    cap_correct = np.array([r["correct"] for r in caps], float)
    cliff = {}
    se2 = False
    for dial in ("binder_distance", "shadow_depth", "functional_order"):
        dv = np.array([r[dial] for r in caps], float)
        stat = _median_split_stat(cap_correct, dv)
        pval = _perm_p_split(cap_correct, dv, rng) if stat > 0 else 1.0
        cliff[dial] = {"stat": stat, "p": pval}
        # shallow competence at this dial
        if len(dv) and not np.all(dv == dv[0]):
            shallow = cap_correct[dv <= np.median(dv)]
            shallow_ok = shallow.mean() >= SE2_SHALLOW_FLOOR if len(shallow) else False
        else:
            shallow_ok = False
        if stat > 0 and pval < ALPHA and shallow_ok:
            se2 = True

    # ── SE3 alpha-variance (term vs variant) + self-null ──
    a_term = np.array([r["correct"] for r in alph if r["surface"] == "term"], float)
    a_var = np.array([r["correct"] for r in alph if r["surface"] == "variant"], float)
    have_alpha = len(a_term) and len(a_var)
    alpha_delta = float(a_term.mean() - a_var.mean()) if have_alpha else 0.0
    p3 = _perm_p_delta(a_term, a_var, rng) if alpha_delta != 0.0 else 1.0
    se3 = bool(abs(alpha_delta) > 0 and p3 < ALPHA)

    # ── verdict (frozen precedence) ──
    if not se0:
        verdict = "VOID"
    elif se3:
        verdict = "ALPHA-VARIANT-ROUTER"
    elif se2:
        verdict = "DEPTH-DEPENDENT-MIXED"
    elif frac_correct >= 0.5 + SE1_MARGIN and p1 < ALPHA:
        verdict = "CAPTURE-AVOIDING"
    elif frac_correct <= 0.5 - SE1_MARGIN and p1 < ALPHA:
        verdict = "NAIVE-SUBST"
    else:
        verdict = "VOID"

    return {
        "verdict": verdict,
        "SE0": se0, "SE2": se2, "SE3": se3,
        "acc_control": acc_ctrl, "acc_capture": acc_cap,
        "frac_correct": frac_correct, "n_decisive": n_dec, "p1": p1,
        "cliff": cliff, "alpha_delta": alpha_delta, "p3": p3,
    }


def se4_crosslink(recs_instruct: list[dict], recs_base: list[dict], rng) -> dict:
    """The directional cross-link: naive (first-binder) intrusion rate on shadowed
    capture pairs, instruct vs its paired base. Prediction: instruct > base."""
    def intrusions(recs):
        shadowed = [r for r in recs
                    if r["family"] == "capture" and r["shadow_depth"] >= 1]
        return np.array([1.0 if r.get("naive") else 0.0 for r in shadowed]), shadowed

    a, sa = intrusions(recs_instruct)
    b, sb = intrusions(recs_base)
    if len(sa) < SE4_MIN_N or len(sb) < SE4_MIN_N:
        return {"SE4": False, "reason": "insufficient shadowed pairs",
                "rate_instruct": float(a.mean()) if len(a) else 0.0,
                "rate_base": float(b.mean()) if len(b) else 0.0, "p": 1.0}
    delta = a.mean() - b.mean()
    p = _perm_p_delta(a, b, rng)
    return {
        "SE4": bool(delta > 0 and p < ALPHA),
        "rate_instruct": float(a.mean()), "rate_base": float(b.mean()),
        "delta": float(delta), "p": p,
    }


def pilot(recs: list[dict], rng) -> dict:
    """The folded direct/traced pilot (advisory register — NOT a frozen verdict
    gate). Reads the three per-item arms:

      direct  — score forced-choice immediately
      traced  — model generates its own reduction, then score
      null    — same generation TOKENS shuffled (token-budget matched)

    direct_traced_gap = acc(traced) - acc(direct). The MANDATORY token-budget
    null: a real reduction benefit requires acc(traced) > acc(null); if not, the
    traced gain is just more tokens in context (the FUEL/TRACE-FUEL/NF-GAUGE x3
    confound). ``token_budget_null_passed`` iff the content effect clears it."""
    scored = [r for r in recs if "correct_traced" in r and "correct_null" in r]
    if not scored:
        return {"pilot": "none"}
    d = np.array([r["correct"] for r in scored], float)
    t = np.array([r["correct_traced"] for r in scored], float)
    n = np.array([r["correct_null"] for r in scored], float)
    content = float(t.mean() - n.mean())
    p_content = _perm_p_delta(t, n, rng) if content != 0.0 else 1.0
    return {
        "acc_direct": float(d.mean()), "acc_traced": float(t.mean()),
        "acc_null": float(n.mean()),
        "direct_traced_gap": float(t.mean() - d.mean()),
        "trace_content_effect": content, "p_content": p_content,
        "token_budget_null_passed": bool(content > 0 and p_content < ALPHA),
        "n_scored": len(scored),
    }


# ══════════════════════════════════════════════════════════════════════════
# --validate — planted worlds force each verdict; NO model loaded
# ══════════════════════════════════════════════════════════════════════════
def _planted(kind: str, rng) -> list[dict]:
    """Synthesize scored records that force a target verdict."""
    recs: list[dict] = []

    # controls: solved unless a VOID-sanity world
    ctrl_p = 0.30 if kind == "void_sanity" else 0.95
    for _ in range(12):
        recs.append({"family": "control", "surface": "term",
                     "correct": rng.random() < ctrl_p, "naive": False,
                     "binder_distance": 0, "shadow_depth": 0, "functional_order": 0})

    # capture pairs across the dial grid
    for dist in (1, 2, 3, 4, 5):
        for order in (1, 2):
            for _ in range(6):
                if kind == "capture_avoiding":
                    pc = 0.90
                elif kind == "naive":
                    pc = 0.08
                elif kind == "cliff":
                    pc = 0.92 if dist <= 2 else 0.15  # correct shallow, naive deep
                else:  # alpha / void_sanity — SE1 ambiguous
                    pc = 0.5
                correct = rng.random() < pc
                naive = (not correct) and (rng.random() < 0.85)
                recs.append({"family": "capture", "surface": "term",
                             "correct": correct, "naive": naive,
                             "binder_distance": dist, "shadow_depth": min(dist, 3),
                             "functional_order": order})

    # alpha pairs: variant degrades only in the 'alpha' world
    for _ in range(30):
        term_ok = rng.random() < 0.9
        var_ok = rng.random() < (0.4 if kind == "alpha" else 0.9)
        recs.append({"family": "alpha", "surface": "term", "correct": term_ok,
                     "naive": False, "binder_distance": 1, "shadow_depth": 0,
                     "functional_order": 1})
        recs.append({"family": "alpha", "surface": "variant", "correct": var_ok,
                     "naive": False, "binder_distance": 1, "shadow_depth": 0,
                     "functional_order": 1})
    return recs


def _planted_pair(rng) -> tuple[list[dict], list[dict]]:
    """Two runs for SE4: instruct with MORE naive intrusions than base."""
    def run(naive_rate):
        out = []
        for dist in (1, 2, 3):
            for _ in range(12):
                naive = rng.random() < naive_rate
                out.append({"family": "capture", "surface": "term",
                            "correct": not naive, "naive": naive,
                            "binder_distance": dist, "shadow_depth": min(dist, 3),
                            "functional_order": 1})
        return out
    return run(0.55), run(0.15)  # instruct, base


def _planted_pilot(kind: str, rng) -> list[dict]:
    """Pilot records with three arms. 'trace_helps': traced beats BOTH direct and
    the token-budget null (real reduction content). 'budget_only': traced beats
    direct but NOT the null (gain is just token budget)."""
    recs = []
    for _ in range(60):
        d = rng.random() < 0.50
        if kind == "trace_helps":
            t, nl = rng.random() < 0.90, rng.random() < 0.55
        else:  # budget_only — traced and null equally (falsely) elevated
            t, nl = rng.random() < 0.85, rng.random() < 0.85
        recs.append({"family": "capture", "surface": "term",
                     "correct": d, "naive": False,
                     "correct_traced": t, "correct_null": nl,
                     "binder_distance": 1, "shadow_depth": 1, "functional_order": 1})
    return recs


def validate() -> bool:
    rng = np.random.default_rng(0)
    ok = True

    checks = {
        "capture_avoiding": "CAPTURE-AVOIDING",
        "naive": "NAIVE-SUBST",
        "cliff": "DEPTH-DEPENDENT-MIXED",
        "alpha": "ALPHA-VARIANT-ROUTER",
        "void_sanity": "VOID",
    }
    for kind, want in checks.items():
        g = compute_gates(_planted(kind, np.random.default_rng(7)), rng)
        good = g["verdict"] == want
        ok &= good
        print(f"[validate] {kind:16} -> {g['verdict']:22} "
              f"frac_correct={g['frac_correct']:.2f} p1={g['p1']:.3f} "
              f"SE2={g['SE2']} SE3={g['SE3']} adelta={g['alpha_delta']:+.2f} "
              f"{'OK' if good else 'FAIL want ' + want}")

    # SE4 directional cross-link
    ri, rb = _planted_pair(np.random.default_rng(11))
    s4 = se4_crosslink(ri, rb, rng)
    s4_ok = s4["SE4"] and s4["delta"] > 0
    print(f"[validate] SE4 crosslink instruct={s4['rate_instruct']:.2f} "
          f"base={s4['rate_base']:.2f} delta={s4.get('delta', 0):+.2f} "
          f"p={s4['p']:.3f} -> {s4_ok}")
    ok &= s4_ok

    # ── primitive 1: every capture pair genuinely discriminates via the reducer ──
    caps = capture_pairs()
    disc = all(
        reduce(parse(p.term), calc=R_NORMAL).status is Status.NORMAL_FORM
        and reduce(parse(p.term), calc=R_NAIVE).status is Status.NORMAL_FORM
        and not alpha_eq(parse(p.correct_nf), parse(p.naive_nf))
        for p in caps
    )
    print(f"[validate] capture pairs discriminate (correct≠naive, both NF): {disc}")
    ok &= disc

    # ── primitive 2: candidate sets are 3-distinct and contain correct+naive ──
    cgood = True
    for p in caps[:12]:
        c = make_candidates(p.correct_nf, p.naive_nf)
        cgood &= (
            c is not None
            and c["correct"] == p.correct_nf
            and c["naive"] == p.naive_nf
            and len(set(c.values())) >= 3
        )
    print(f"[validate] candidates 3-distinct incl correct+naive: {cgood}")
    ok &= cgood

    # ── primitive 3: controls solvable (unambiguous NF) + battery well-formed ──
    bat = build_battery()
    ctrl = [r for r in bat if r["family"] == "control"]
    ctrl_nf = all(
        reduce(parse(r["prompt"])).status is Status.NORMAL_FORM
        and pretty(normal_form(parse(r["prompt"]))) == r["correct_nf"]
        for r in ctrl
    )
    fams = {r["family"] for r in bat}
    print(f"[validate] battery controls certified={ctrl_nf} "
          f"families={sorted(fams)} n={len(bat)}")
    ok &= ctrl_nf and fams == {"control", "capture", "alpha"}

    # ── primitive 3b: EVERY battery item builds ≥3 distinct candidates ──
    #    (smoke s331 caught atom-NF controls being silently dropped)
    buildable = []
    for r in bat:
        c = make_candidates(r["correct_nf"], r["naive_nf"])
        buildable.append(c is not None and c["correct"] == r["correct_nf"]
                         and len(set(c.values())) >= 3)
    all_build = all(buildable)
    print(f"[validate] all {len(bat)} items triple-optioned "
          f"(controls no longer dropped): {all_build}")
    ok &= all_build

    # ── primitive 4: alpha self-null — identical arms read NON-significant ──
    flat = []
    for _ in range(30):
        flat.append({"family": "alpha", "surface": "term",
                     "correct": rng.random() < 0.9, "naive": False,
                     "binder_distance": 1, "shadow_depth": 0, "functional_order": 1})
        flat.append({"family": "alpha", "surface": "variant",
                     "correct": rng.random() < 0.9, "naive": False,
                     "binder_distance": 1, "shadow_depth": 0, "functional_order": 1})
    g_flat = compute_gates(
        [*_planted("capture_avoiding", np.random.default_rng(5))[:60], *flat], rng
    )
    print(f"[validate] alpha self-null (identical arms) SE3={g_flat['SE3']} "
          f"p3={g_flat['p3']:.3f} -> {not g_flat['SE3']}")
    ok &= not g_flat["SE3"]

    # ── primitive 5: pilot token-budget null — trace-CONTENT passes, budget fails ──
    ph = pilot(_planted_pilot("trace_helps", np.random.default_rng(21)), rng)
    pb = pilot(_planted_pilot("budget_only", np.random.default_rng(22)), rng)
    pilot_ok = ph["token_budget_null_passed"] and not pb["token_budget_null_passed"]
    print(f"[validate] pilot token-budget null: trace_helps "
          f"gap={ph['direct_traced_gap']:+.2f} "
          f"content={ph['trace_content_effect']:+.2f} "
          f"pass={ph['token_budget_null_passed']} | budget_only "
          f"content={pb['trace_content_effect']:+.2f} "
          f"pass={pb['token_budget_null_passed']} -> {pilot_ok}")
    ok &= pilot_ok

    print(f"[validate] {'ALL PASS' if ok else 'FAIL'}")
    return ok


# ══════════════════════════════════════════════════════════════════════════
# main — model load + forced-choice scoring (the torch boundary; held for GO)
# ══════════════════════════════════════════════════════════════════════════
_FEWSHOT_DIRECT = (
    "Reduce each lambda-calculus term to its normal form, renaming bound "
    "variables as needed to avoid variable capture.\n\n"
    "Term: (λx.x) a\nNormal form: a\n\n"
    "Term: (λx.λy.x) p q\nNormal form: p\n\n"
    "Term: (λf.λx.f (f x)) g z\nNormal form: g (g z)\n\n"
)

_FEWSHOT_TRACED = (
    "Reduce each lambda-calculus term to normal form, showing each "
    "beta-reduction step and renaming bound variables to avoid capture.\n\n"
    "Term: (λx.λy.x) p q\n"
    "Steps: (λx.λy.x) p q -> (λy.p) q -> p\n"
    "Normal form: p\n\n"
    "Term: (λf.λx.f (f x)) g z\n"
    "Steps: (λf.λx.f (f x)) g z -> (λx.g (g x)) z -> g (g z)\n"
    "Normal form: g (g z)\n\n"
)
_TRACE_SUFFIX = "\nNormal form:"


def _score_ids(model, dev, prefix_ids, cont_ids) -> float:
    """Length-normalized logprob of `cont_ids` given `prefix_ids` (id-level, so the
    token-budget null stays EXACTLY length-matched). Torch boundary."""
    import torch
    full = torch.cat([prefix_ids, cont_ids]).unsqueeze(0).to(dev)
    with torch.no_grad():
        logits = model(full).logits[0].float()
    logp = torch.log_softmax(logits, dim=-1)
    n = len(prefix_ids)
    total = sum(logp[n + k - 1, cont_ids[k]].item() for k in range(len(cont_ids)))
    return total / max(len(cont_ids), 1)


def _generate(model, tok, dev, prompt_ids, max_new_tokens: int):
    """Greedy free generation of the model's OWN reduction trace; returns the new
    token ids (CPU tensor). The traced arm's 'steps shown' = the model's steps."""
    import torch
    inp = prompt_ids.unsqueeze(0).to(dev)
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    with torch.no_grad():
        out = model.generate(inp, max_new_tokens=max_new_tokens, do_sample=False,
                             pad_token_id=pad)
    return out[0][prompt_ids.shape[0]:].detach().to("cpu")


def _pick(model, dev, prefix_ids, cont_ids: dict):
    lp = {k: _score_ids(model, dev, prefix_ids, c) for k, c in cont_ids.items()}
    return max(lp, key=lp.get), {k: float(v) for k, v in lp.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-trace-tokens", type=int, default=64)
    ap.add_argument("--out", default=None)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return 0 if validate() else 1

    battery = build_battery()
    if args.smoke:
        battery = battery[:6]
    rng = np.random.default_rng(args.seed)

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    dev = args.device
    print(f"[se] load {args.model_id} dev={dev} n={len(battery)} "
          f"(3 arms: direct/traced/null)", flush=True)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()

    def ids(text, special=True):
        return tok(text, add_special_tokens=special,
                   return_tensors="pt").input_ids[0]

    suffix_ids = ids(_TRACE_SUFFIX, special=False)
    recs = []
    for i, b in enumerate(battery):
        cand = make_candidates(b["correct_nf"], b["naive_nf"])
        if cand is None:
            continue
        cont_ids = {k: ids(" " + v, special=False) for k, v in cand.items()}

        # direct arm
        pd_ids = ids(_FEWSHOT_DIRECT + f"Term: {b['prompt']}\nNormal form:")
        pick_d, lp_d = _pick(model, dev, pd_ids, cont_ids)

        # traced arm — model generates its own reduction
        pt_ids = ids(_FEWSHOT_TRACED + f"Term: {b['prompt']}\nSteps:")
        trace_ids = _generate(model, tok, dev, pt_ids, args.max_trace_tokens)
        traced_prefix = torch.cat([pt_ids, trace_ids, suffix_ids])
        pick_t, _ = _pick(model, dev, traced_prefix, cont_ids)

        # token-budget null — SAME trace tokens, shuffled (length-matched)
        if len(trace_ids) > 1:
            perm = torch.as_tensor(rng.permutation(len(trace_ids)))
            null_trace = trace_ids[perm]
        else:
            null_trace = trace_ids
        null_prefix = torch.cat([pt_ids, null_trace, suffix_ids])
        pick_n, _ = _pick(model, dev, null_prefix, cont_ids)

        recs.append({
            **{k: b[k] for k in b if k != "correct_nf"},
            "correct": bool(pick_d == "correct"),
            "naive": bool(pick_d == "naive"),
            "correct_traced": bool(pick_t == "correct"),
            "correct_null": bool(pick_n == "correct"),
            "pick_direct": pick_d, "pick_traced": pick_t, "pick_null": pick_n,
            "n_trace_tokens": len(trace_ids),
            "candidates": cand, "lp_direct": lp_d,
        })
        if (i + 1) % 10 == 0:
            print(f"[se] scored {i + 1}/{len(battery)}", flush=True)

    stat_rng = np.random.default_rng(args.seed + 99)
    g = compute_gates(recs, stat_rng)
    pl = pilot(recs, stat_rng)
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        with (out / "results.jsonl").open("w") as f:
            for r in recs:
                f.write(json.dumps(r, default=_json_native) + "\n")
        with (out / "gates.json").open("w") as f:
            json.dump({"model_id": args.model_id, "seed": args.seed,
                       "pilot": pl, **g}, f, indent=2, default=_json_native)
    print(f"[se] verdict={g['verdict']} frac_correct={g['frac_correct']:.3f} "
          f"acc_ctrl={g['acc_control']:.3f} SE2={g['SE2']} SE3={g['SE3']}", flush=True)
    print(f"[se] pilot: acc direct={pl.get('acc_direct', 0):.3f} "
          f"traced={pl.get('acc_traced', 0):.3f} null={pl.get('acc_null', 0):.3f} "
          f"gap={pl.get('direct_traced_gap', 0):+.3f} "
          f"content={pl.get('trace_content_effect', 0):+.3f} "
          f"budget_null_passed={pl.get('token_budget_null_passed')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
