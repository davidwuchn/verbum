"""§P-LINEARITY-BIAS — the W/D cost-differential fingerprint (2nd discriminator
for SKI-control #4, Cartesian substrate).

FROZEN: type-systems-under-llm-constraints.md §P-LINEARITY-BIAS (s319, Michael GO).
Claim: at MATCHED FUEL, contraction (argument duplication) costs reduction-accuracy
that linear composition does not → affine core (KIBC-not-SKI).

Register (λ measure) — COMPUTATIONAL-ACCURACY (behavioral correctness), deliberately
fresh: independent of the 3×-nulled kind-magnitude (§P-FUEL/§P-TRACE-FUEL/§P-NF-GAUGE)
and the §P-DISJ-COST off-plane geometry.

Readout — forced-choice NF accuracy (read-only): each kernel-certified term is scored
against candidate normal forms {correct, under-reduce, atom-swap}; the model ranks each
by length-normalized logprob; accuracy = argmax picks the certified-correct NF.

Construction (matched, kernel-certified) — two arms from verbum.lambda_ast:
  LINEAR = {B, C, D}  (composition/exchange/triple-composition; NO argument duplicated;
            distinct == ℓ). NB: the kernel's D is `D f g h x → f (g (h x))` — a LINEAR
            3-fold composition, NOT the "f (f x)" of the page's table; runtime ≡ truth
            (λ assert). I/K excluded — NFs (size 3) can't be nf_size-matched to a
            contraction unit.
  DUP    = {W, M}  (W f x → f x x ; M x → x x — genuine contraction, an arg is copied).
  Arms matched on ell (fuel), nf_size, prompt token-length; the confound-control that
     separates "copying costs" from "longer is harder" (the §P-FUEL trap) — the game.

Instrument-side amendment banked at build (coherence fix, gates/verdicts/register/
a-priori UNCHANGED, Michael-flagged at GO): the frozen text cited D as a duplication
example; the runtime kernel implements D as linear composition, so DUP = {W, M} and D
joins LINEAR. Correcting the combinator inventory to match the kernel is representation
≟ reality (λ coherence), not a goalpost move.

Reuse (λ one_way, no fork): verbum.lambda_ast (parse/reduce/size/pretty/fired_sequence)
· fuel_theorem (partial_spearman/spearman/_perm_within_bins) · torch only at the scoring
boundary. New code = LINEAR/DUP term generation + distractor construction + choice
logprob accuracy + LB1–LB4 gates.

Usage:
  uv run python scripts/explore/linearity_bias.py --validate
  uv run python scripts/explore/linearity_bias.py --smoke
     uv run python -u scripts/explore/linearity_bias.py --out results/linearity-bias/q4b
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import fuel_theorem as ff  # noqa: E402  (partial_spearman / spearman / _perm_within_bins)

from verbum.lambda_ast import (  # noqa: E402
    App,
    Atom,
    Comb,
    Status,
    fired_sequence,
    parse,
    pretty,
    reduce,
    size,
)

# ── frozen constants ──────────────────────────────────────────────────────
LINEAR_UNITS = ("B", "C", "D")          # composition / exchange / triple-comp (linear)
DUP_UNITS = ("W", "M")                  # contraction — an argument is copied
UNIT_ARITY = {"B": 3, "C": 3, "D": 4, "W": 2, "M": 1}
CONTRACTION = frozenset({"W", "M"})     # opcodes that duplicate (LB3 counts these)
N_UNITS = (1, 2, 3, 4, 5, 6)            # units per term = ℓ ladder
N_PER_CELL = 6                          # terms per (arm, n_units) cell
_ALPHA = 0.05
_N_PERM = 2000
LB4_ACC_FLOOR = 0.45                    # LINEAR arm must be competent (off 1/3 chance)
LB4_ACC_CEIL = 0.97                     # …with headroom to fall (s311 bake lesson)
LB4_MARGIN_RATIO = (0.5, 2.0)           # distractor confusability parity across arms
MIN_MIXED_BINS = 3                      # (ell,nf_size) cells holding BOTH arms → power

_LETTERS = "abcdefghijklmnopqrstuvwxyz"


# ══════════════════════════════════════════════════════════════════════════
# Term generation — kernel-certified LINEAR vs DUP batteries
# ══════════════════════════════════════════════════════════════════════════
def _unit(op: str, atoms: list[str]) -> str:
    return "(" + " ".join([op, *atoms]) + ")"


DUP_FRAC = 0.6                          # per-unit P(contraction) in the DUP arm


def _make_term(rng: np.random.Generator, arm: str, n: int) -> str | None:
    """h u1 … un with fresh distinct atoms; each unit fires exactly once.

    LIN arm: all units linear {B,C,D} (n_contract == 0).
    DUP arm: each unit is a contraction {W,M} w.p. DUP_FRAC else linear {B,C,D},
    with ≥1 contraction guaranteed. Mixing decouples n_contract from ℓ (so LB3
    can vary contraction count at fixed fuel) and pulls DUP nf_size to overlap
    LIN (so ℓ-matched bins are populated by both arms)."""
    if arm == "LIN":
        ops = [str(rng.choice(LINEAR_UNITS)) for _ in range(n)]
    else:
        ops = [str(rng.choice(DUP_UNITS)) if rng.random() < DUP_FRAC
               else str(rng.choice(LINEAR_UNITS)) for _ in range(n)]
        if not any(o in CONTRACTION for o in ops):
            ops[int(rng.integers(n))] = str(rng.choice(DUP_UNITS))
    if sum(UNIT_ARITY[o] for o in ops) > len(_LETTERS):
        return None
    letters = list(rng.permutation(list(_LETTERS)))
    li = 0
    units = []
    for op in ops:
        k = UNIT_ARITY[op]
        units.append(_unit(op, letters[li:li + k]))
        li += k
    return "h " + " ".join(units)


def build_battery(rng: np.random.Generator) -> list[dict]:
    """Certified LIN/DUP terms; only NORMAL_FORM kept (all are, by construction)."""
    battery: list[dict] = []
    seen: set[str] = set()
    for arm in ("LIN", "DUP"):
        for n in N_UNITS:
            made = 0
            tries = 0
            while made < N_PER_CELL and tries < N_PER_CELL * 40:
                tries += 1
                p = _make_term(rng, arm, n)
                if p is None or p in seen:
                    continue
                r = reduce(parse(p))
                if r.status != Status.NORMAL_FORM:
                    continue
                fired = fired_sequence(parse(p))
                battery.append({
                    "arm": arm,
                    "prompt": p,
                    "ell": int(r.steps),
                    "nf_size": int(size(r.normal_form)),
                    "n_contract": sum(1 for f in fired if f in CONTRACTION),
                    "nf": pretty(r.normal_form),
                })
                seen.add(p)
                made += 1
    return battery


# ── distractor construction (kernel-derived, arm-symmetric) ───────────────
def _atoms_inorder(t) -> list[str]:
    if isinstance(t, Atom):
        return [t.name]
    if isinstance(t, Comb):
        return []
    return _atoms_inorder(t.fn) + _atoms_inorder(t.arg)


def _relabel(t, seq: list[str], idx: list[int]):
    if isinstance(t, Atom):
        name = seq[idx[0]]
        idx[0] += 1
        return Atom(name)
    if isinstance(t, Comb):
        return t
    return App(_relabel(t.fn, seq, idx), _relabel(t.arg, seq, idx))


def _atom_swap(nf_term, rng: np.random.Generator) -> str | None:
    """Transpose two distinct-named atom leaves in the NF → a plausible exchange
    error of IDENTICAL token length. None if <2 distinct atoms."""
    names = _atoms_inorder(nf_term)
    pos = [(i, j) for i in range(len(names)) for j in range(i + 1, len(names))
           if names[i] != names[j]]
    if not pos:
        return None
    i, j = pos[int(rng.integers(len(pos)))]
    swapped = list(names)
    swapped[i], swapped[j] = swapped[j], swapped[i]
    out = pretty(_relabel(nf_term, swapped, [0]))
    return out


def make_candidates(prompt: str, rng: np.random.Generator) -> dict | None:
    """{correct, under, swap} NF-string candidates. under = one step before NF
    (an unreduced redex remains); swap = atom transposition (same length)."""
    t = parse(prompt)
    r = reduce(t)
    correct = pretty(r.normal_form)
    ell = r.steps
    under = pretty(r.trace[ell - 1]) if ell >= 1 else pretty(t)
    nf_term = r.normal_form
    swap = _atom_swap(nf_term, rng)
    if swap is None or len({correct, under, swap}) < 3:
        return None
    return {"correct": correct, "under": under, "swap": swap}


# ══════════════════════════════════════════════════════════════════════════
# Gates + verdict — PURE (no torch; what --validate exercises)
# ══════════════════════════════════════════════════════════════════════════
def _two_sided_p(obs: float, null: np.ndarray) -> float:
    return float((np.abs(null) >= abs(obs) - 1e-12).mean())


def _arm_gap(correct: np.ndarray, is_dup: np.ndarray) -> float:
    lin = correct[is_dup == 0]
    dup = correct[is_dup == 1]
    if lin.size == 0 or dup.size == 0:
        return 0.0
    return float(lin.mean() - dup.mean())


def _partial_spearman2(x: np.ndarray, y: np.ndarray,
                       z1: np.ndarray, z2: np.ndarray) -> float:
    """Rank partial correlation of x,y controlling BOTH z1 and z2 (residualize
    rank(x),rank(y) on [rank(z1),rank(z2),1] by least squares, correlate residuals).
    Used for LB2: accuracy vs dup-ness controlling fuel ℓ AND output size nf_size."""
    rx = ff._rankdata(x)
    ry = ff._rankdata(y)
    zz = np.column_stack([ff._rankdata(z1), ff._rankdata(z2), np.ones(len(x))])
    bx, *_ = np.linalg.lstsq(zz, rx, rcond=None)
    by, *_ = np.linalg.lstsq(zz, ry, rcond=None)
    return ff._pearson(rx - zz @ bx, ry - zz @ by)


def compute_gates(recs: list[dict], rng: np.random.Generator,
                  n_perm: int = _N_PERM) -> dict:
    correct = np.array([r["correct"] for r in recs], float)
    is_dup = np.array([1 if r["arm"] == "DUP" else 0 for r in recs], int)
    ell = np.array([r["ell"] for r in recs], float)
    nf_size = np.array([r["nf_size"] for r in recs], float)
    n_contract = np.array([r["n_contract"] for r in recs], float)
    lp_correct = np.array([r["lp_correct"] for r in recs], float)
    lp_swap = np.array([r["lp_swap"] for r in recs], float)
    certified = bool(all(r.get("certified", True) for r in recs))

    acc_lin = float(correct[is_dup == 0].mean()) if (is_dup == 0).any() else 0.0
    acc_dup = float(correct[is_dup == 1].mean()) if (is_dup == 1).any() else 0.0

    # ── LB1 ACCURACY-GAP — unmatched (a gap EXISTS) ──
    gap = _arm_gap(correct, is_dup)
    null1 = np.array([_arm_gap(correct, rng.permutation(is_dup))
                      for _ in range(n_perm)])
    p1 = _two_sided_p(gap, null1)
    lb1 = bool(gap > 0 and p1 < _ALPHA)
    anti = bool(gap < 0 and p1 < _ALPHA)

    # ── LB2 FUEL-CONTROLLED — gap survives within ℓ bins AND under ℓ&nf_size partial ──
    # ℓ-bins are always mixed (both arms span the ℓ ladder); nf_size controlled via
    # the double partial (LIN runs larger at matched ℓ ⇒ nf_size confound conservative,
    # but controlled). Frozen LB2 = "partial | ℓ and/or matched-ℓ subsampling".
    bincode = ell.astype(int)
    n_mixed = int(sum(
        1 for b in np.unique(bincode)
        if (is_dup[bincode == b] == 0).any() and (is_dup[bincode == b] == 1).any()))
    gap_m = _arm_gap(correct, is_dup)  # recomputed under within-ℓ-bin permutation null
    null2 = np.array([
        _arm_gap(correct,
                 ff._perm_within_bins(is_dup.astype(float), bincode, rng).astype(int))
        for _ in range(n_perm)])
    p2 = _two_sided_p(gap_m, null2)
    partial_r = ff.partial_spearman(correct, is_dup.astype(float), ell)       # | ℓ
    partial_r2 = _partial_spearman2(
        correct, is_dup.astype(float), ell, nf_size)  # | ℓ, nf_size
    lb2 = bool(gap_m > 0 and p2 < _ALPHA and partial_r < 0 and partial_r2 < 0
               and n_mixed >= MIN_MIXED_BINS)

    # ── LB3 CONTRACTION-GRADED (corroboration, non-gating) — DUP arm, | ℓ ──
    dmask = is_dup == 1
    if dmask.sum() >= 4 and len(np.unique(n_contract[dmask])) >= 2:
        r3 = ff.partial_spearman(correct[dmask], n_contract[dmask], ell[dmask])
        null3 = np.array([
            ff.partial_spearman(rng.permutation(correct[dmask]),
                                n_contract[dmask], ell[dmask])
            for _ in range(n_perm)])
        p3 = _two_sided_p(r3, null3)
        lb3 = bool(r3 < 0 and p3 < _ALPHA)
    else:
        r3, p3, lb3 = 0.0, 1.0, False

    # ── LB4 SANE (void-gate) ──
    margin_lin = float((lp_correct - lp_swap)[is_dup == 0].mean()) \
        if (is_dup == 0).any() else 0.0
    margin_dup = float((lp_correct - lp_swap)[is_dup == 1].mean()) \
        if (is_dup == 1).any() else 0.0
    lo, _hi = LB4_MARGIN_RATIO
    # distractor confusability parity: smaller/larger arm margin magnitude ≥ lo (0.5)
    frac = (min(abs(margin_lin), abs(margin_dup)) /
            max(abs(margin_lin), abs(margin_dup), 1e-9))
    sym_ok = bool(frac >= lo)
    # headroom: VOID only when the model can't reduce at all (best arm at chance)
    # or both arms saturate (no discrimination room). Direction is LB1's job.
    competent = max(acc_lin, acc_dup) >= LB4_ACC_FLOOR
    room = min(acc_lin, acc_dup) <= LB4_ACC_CEIL
    headroom = bool(competent and room)
    lb4 = bool(headroom and sym_ok and certified and n_mixed >= MIN_MIXED_BINS)

    # ── verdict (frozen tree) ──
    if not lb4:
        verdict = "VOID"
    elif anti:
        verdict = "ANTI"
    elif not lb1:
        verdict = "CARTESIAN-CONSISTENT"
    elif lb2:
        verdict = "LINEARITY-BIASED" + ("+GRADED" if lb3 else "")
    else:
        verdict = "FUEL-ARTIFACT"

    return {
        "verdict": verdict,
        "acc_lin": acc_lin, "acc_dup": acc_dup,
        "LB1": lb1, "gap": gap, "p1": p1, "anti": anti,
        "LB2": lb2, "gap_matched": gap_m, "p2": p2,
        "partial_r": partial_r, "partial_r2": partial_r2,
        "n_mixed_bins": n_mixed,
        "LB3": lb3, "r3": r3, "p3": p3,
        "LB4": lb4, "headroom": headroom, "sym_ok": sym_ok, "certified": certified,
        "margin_lin": margin_lin, "margin_dup": margin_dup, "margin_frac": float(frac),
        "n": len(recs),
    }


# ══════════════════════════════════════════════════════════════════════════
# --validate — planted worlds exercise every verdict + primitives
# ══════════════════════════════════════════════════════════════════════════
def _planted(kind: str, rng: np.random.Generator) -> list[dict]:
    """Synthesize records forcing a target verdict. ℓ bins shared across arms
    (LB2 power); DUP n_contract drawn independently of ℓ so LB3 is non-degenerate."""
    recs = []
    # ℓ distribution per arm: 'fuel_artifact' skews DUP toward high ℓ (raw gap from
    # marginal imbalance, flat within bin); others share the same ℓ grid.
    if kind == "fuel_artifact":
        # marginal skew (LIN low-ℓ, DUP high-ℓ) but ≥3 shared bins {2,3,4}
        ells_lin = [1, 1, 1, 2, 2, 3, 3, 4]
        ells_dup = [2, 3, 4, 4, 4, 5, 5, 5]
    else:
        ells_lin = ells_dup = [1, 2, 3, 4, 5]

    def acc_prob(kind: str, arm: str, e: int, nc: int) -> float:
        if kind == "biased":
            return 0.88 if arm == "LIN" else 0.40
        if kind == "biased_graded":
            return 0.90 if arm == "LIN" else max(0.05, 0.92 - 0.24 * nc)
        if kind == "fuel_artifact":
            return 0.92 - 0.14 * e            # same fn of ℓ for BOTH arms
        if kind == "cartesian":
            return 0.80
        if kind == "anti":
            return 0.45 if arm == "LIN" else 0.85
        if kind == "void_floor":
            return 0.34
        if kind == "void_asym":
            return 0.88 if arm == "LIN" else 0.40
        raise ValueError(kind)

    for arm in ("LIN", "DUP"):
        ells = ells_lin if arm == "LIN" else ells_dup
        for e in ells:
            for _ in range(18):
                nfs = 2 * e + 5 + int(rng.integers(0, 3))
                if arm == "LIN":
                    nc = 0
                else:
                    nc = int(rng.integers(1, e + 1))   # 1..ℓ, independent draw
                p = acc_prob(kind, arm, e, nc)
                acc = rng.random() < p
                md = 0.05 if (kind == "void_asym" and arm == "DUP") else 2.0
                m = 2.0 if arm == "LIN" else md
                recs.append({
                    "arm": arm, "correct": bool(acc), "ell": e, "nf_size": nfs,
                    "n_contract": nc, "lp_correct": 0.0, "lp_swap": -m,
                    "certified": True,
                })
    return recs


def validate() -> bool:
    rng = np.random.default_rng(0)
    ok = True

    checks = {
        "biased": ("LINEARITY-BIASED", "LINEARITY-BIASED+GRADED"),
        "biased_graded": ("LINEARITY-BIASED+GRADED",),
        "fuel_artifact": ("FUEL-ARTIFACT",),
        "cartesian": ("CARTESIAN-CONSISTENT",),
        "anti": ("ANTI",),
        "void_floor": ("VOID",),
        "void_asym": ("VOID",),
    }
    for kind, want in checks.items():
        g = compute_gates(_planted(kind, np.random.default_rng(1)), rng, n_perm=800)
        good = g["verdict"] in want
        ok &= good
        print(f"[validate] {kind:16} -> {g['verdict']:24} "
              f"gap={g['gap']:+.2f} p1={g['p1']:.3f} p2={g['p2']:.3f} "
              f"pr={g['partial_r']:+.2f} r3={g['r3']:+.2f} p3={g['p3']:.3f} "
              f"acc={g['acc_lin']:.2f}/{g['acc_dup']:.2f} "
              f"{'OK' if good else 'FAIL want ' + str(want)}")

    # ── primitive 1: kernel — DUP arm duplicates (mult>distinct), LIN does not ──
    from fuel_theorem import certify
    lin_ok = certify("h (C a b c) (B d e f)")["distinct"] == \
        certify("h (C a b c) (B d e f)")["ell"]
    w = "h (W a b)"
    dup_fired = fired_sequence(parse(w))
    dup_ok = dup_fired == ["W"] and "b b" in pretty(reduce(parse(w)).normal_form)
    print(f"[validate] kernel LIN distinct==ell: {lin_ok} | W duplicates: {dup_ok}")
    ok &= lin_ok and dup_ok

    # ── primitive 2: matched pair — identical (ell, nf_size), differ in contraction ──
    lin_c = certify("h (C a b c) (B d e f)")
    dup_c = certify("h (W a b) (W c d)")
    matched = (lin_c["ell"] == dup_c["ell"] and lin_c["nf_size"] == dup_c["nf_size"])
    print(f"[validate] matched pair ell={lin_c['ell']}=={dup_c['ell']} "
          f"nf_size={lin_c['nf_size']}=={dup_c['nf_size']}: {matched}")
    ok &= matched

    # ── primitive 3: distractors well-formed, distinct, arm-symmetric types ──
    dgood = True
    for p in ("h (C a b c) (D d e f g)", "h (W a b) (M c)"):
        cand = make_candidates(p, np.random.default_rng(2))
        dgood &= cand is not None and \
            len({cand["correct"], cand["under"], cand["swap"]}) == 3
        # atom-swap preserves token length (exchange error)
        dgood &= len(cand["swap"].split()) == len(cand["correct"].split())
    print(f"[validate] distractors 3-distinct + length-preserving swap: {dgood}")
    ok &= dgood

    # ── primitive 4: LB2 fuel-control — planted flat-within-bin reads FUEL-ARTIFACT ──
    g_fa = compute_gates(_planted("fuel_artifact", np.random.default_rng(3)), rng, 800)
    fa_ok = (not g_fa["LB2"]) and g_fa["verdict"] == "FUEL-ARTIFACT"
    print(f"[validate] fuel-control isolates length: LB2={g_fa['LB2']} "
          f"partial_r={g_fa['partial_r']:+.3f} -> {fa_ok}")
    ok &= fa_ok

    # ── primitive 5: battery builds matched, certified, off-ceiling ──
    bat = build_battery(np.random.default_rng(7))
    nlin = sum(1 for b in bat if b["arm"] == "LIN")
    ndup = sum(1 for b in bat if b["arm"] == "DUP")
    allnf = all(reduce(parse(b["prompt"])).status == Status.NORMAL_FORM for b in bat)
    ncvar = len({b["n_contract"] for b in bat if b["arm"] == "DUP"}) >= 2
    ells = {b["ell"] for b in bat}
    mixedbins = sum(1 for e in ells
                    if any(b["arm"] == "LIN" and b["ell"] == e for b in bat)
                    and any(b["arm"] == "DUP" and b["ell"] == e for b in bat))
    bat_ok = nlin > 20 and ndup > 20 and allnf and ncvar and mixedbins >= MIN_MIXED_BINS
    print(f"[validate] battery LIN={nlin} DUP={ndup} certified={allnf} "
          f"nc_varies={ncvar} mixed_ell_bins={mixedbins}: {bat_ok}")
    ok &= bat_ok

    print(f"[validate] {'ALL PASS' if ok else 'FAIL'}")
    return ok


# ══════════════════════════════════════════════════════════════════════════
# main — model load, forced-choice scoring, gates
# ══════════════════════════════════════════════════════════════════════════
_FEWSHOT = (
    "Reduce each combinator term to normal form by applying these rules "
    "until no combinator remains:\n"
    "  B f g x = f (g x)\n"
    "  C f x y = f y x\n"
    "  D f g h x = f (g (h x))\n"
    "  W f x = f x x\n"
    "  M x = x x\n\n"
    "Term: h (B p q r)\nNormal form: h (p (q r))\n\n"
    "Term: h (W p q)\nNormal form: h (p q q)\n\n"
    "Term: h (C p q r)\nNormal form: h (p r q)\n\n"
    "Term: h (M p)\nNormal form: h (p p)\n\n"
)


def _score(model, tok, dev, prompt: str, continuation: str) -> float:
    """Length-normalized logprob of `continuation` given `prompt` (torch boundary)."""
    import torch
    p_ids = tok(prompt, return_tensors="pt").input_ids[0]
    c_ids = tok(continuation, add_special_tokens=False,
                return_tensors="pt").input_ids[0]
    full = torch.cat([p_ids, c_ids]).unsqueeze(0).to(dev)
    with torch.no_grad():
        logits = model(full).logits[0].float()
    logp = torch.log_softmax(logits, dim=-1)
    n = len(p_ids)
    total = 0.0
    for k in range(len(c_ids)):
        total += logp[n + k - 1, c_ids[k]].item()
    return total / max(len(c_ids), 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/linearity-bias/qwen3-4b")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return 0 if validate() else 1

    rng = np.random.default_rng(args.seed)
    battery = build_battery(rng)
    if args.smoke:
        battery = battery[:6] + [b for b in battery if b["arm"] == "DUP"][:6]

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    dev = args.device
    print(f"[lb] load {args.model_id} dev={dev} n_terms={len(battery)}", flush=True)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()

    recs = []
    for i, b in enumerate(battery):
        cand = make_candidates(b["prompt"], np.random.default_rng(1000 + i))
        if cand is None:
            continue
        prompt = _FEWSHOT + f"Term: {b['prompt']}\nNormal form:"
        lp = {k: _score(model, tok, dev, prompt, " " + v) for k, v in cand.items()}
        pick = max(lp, key=lp.get)
        recs.append({
            **b,
            "correct": bool(pick == "correct"),
            "pick": pick,
            "lp_correct": lp["correct"], "lp_under": lp["under"], "lp_swap": lp["swap"],
            "candidates": cand, "certified": True,
        })
        if (i + 1) % 12 == 0:
            print(f"[lb] scored {i + 1}/{len(battery)}", flush=True)

    g = compute_gates(recs, np.random.default_rng(args.seed + 99))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "results.jsonl").open("w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    with (out / "gates.json").open("w") as f:
        json.dump({"model_id": args.model_id, "seed": args.seed, **g}, f, indent=2)

    print(f"[lb] acc_lin={g['acc_lin']:.3f} acc_dup={g['acc_dup']:.3f} "
          f"gap={g['gap']:+.3f} p1={g['p1']:.3f} | matched={g['gap_matched']:+.3f} "
          f"p2={g['p2']:.3f} pr={g['partial_r']:+.3f} pr2={g['partial_r2']:+.3f} "
          f"mixed={g['n_mixed_bins']}", flush=True)
    print(f"[lb] LB1={g['LB1']} LB2={g['LB2']} LB3={g['LB3']} LB4={g['LB4']} "
          f"(headroom={g['headroom']} sym={g['sym_ok']} "
          f"frac={g['margin_frac']:.2f})", flush=True)
    if not args.smoke:
        print(f"[lb] VERDICT: {g['verdict']}", flush=True)
    else:
        print("[lb] smoke done (verdict NOT read)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
