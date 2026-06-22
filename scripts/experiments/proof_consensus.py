r"""Proof consensus (b2, s247) — cross-lineage agreement on KERNEL-VERIFIED proofs.

THE IDEA (cross-model-output-consensus.md applied to the proof domain). The s246
consensus-as-fitness result calibrates P(correct | models agree) on FOL, where the
agreed-error blind spot is the ceiling (only an oracle breaks it). PROOFS remove that
ceiling by construction: the kernel (proof_kernel.check_proof) verifies every term, so
two models CANNOT agree on a kernel-passing false proof. Proofs are therefore
ground-truth-corrected consensus with no token-Jaccard noise — α/reduction-equality is
exact (kernel normal form), not lexical overlap.

This is a POST-PROCESSOR over the single-shot proof_inhabitation.py model JSONs
(each record stores the raw `model_output`). It re-normalizes every term through the
kernel and partitions the (model_A, model_B) pairs into the s246 grid:

  positives (theorems):
    both-valid + same NF   → ★ portability (the proof both lineages agree on)
    both-valid + diff NF   → proof-irrelevance (distinct valid inhabitants)
    one-valid              → frontier
    both-invalid + same    → shared misconception (kernel-caught, harmless)
    both-invalid + diff    → shared not-knowing
  negatives (non-theorems):
    both-abstain (none)    → ★ correct shared ⊥ ("unprovable" teaching data)
    both-reject + same     → agreed wrong attempt (e.g. same classical term on Peirce)
    disagree / false-proof → frontier / alarm (false-proof must be 0)

Headline (mirror of s246): term-agreement rate, and P(both-correct | agree) vs
P(both-correct | disagree) — with the kernel as the oracle for "correct".

Run (after single-shot runs exist for both models):
  uv run python scripts/experiments/proof_consensus.py \
      --models Qwen/Qwen3-14B google/gemma-4-31B-it

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from verbum.proof_kernel import Verdict, check_proof

_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIRS = {
    "inhabitation": _ROOT / "results" / "proof-inhabitation",
    "repl": _ROOT / "results" / "proof-repl",
}
OUT_DIR = _ROOT / "results" / "proof-consensus"


def log(*a: object) -> None:
    print(*a, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_ROOT,
            text=True).strip()
    except Exception:
        return "unknown"


def _answer_key(model_output: str, prop: str) -> tuple[str, str, bool]:
    """Canonical (key, verdict, valid) for a model's answer on a proposition.

    The key collapses representation: VALID/typed terms key on their kernel normal
    form (α/reduction-canonical); abstention keys on '∅'; an unparseable answer keys
    on its raw text. Two answers AGREE iff their keys are equal."""
    chk = check_proof(model_output, prop)
    if chk.verdict == Verdict.NONE:
        return ("∅", chk.verdict, False)
    if chk.normal_form is not None:
        # typed/parsed term: canonical proof identity = its normal form
        return (f"nf:{chk.normal_form}", chk.verdict, chk.valid)
    # parse error / no NF: fall back to the cleaned raw string
    return (f"raw:{' '.join(model_output.lower().split())}", chk.verdict, chk.valid)


def load_model(model: str, source: str) -> dict:
    path = SOURCE_DIRS[source] / f"{model.replace('/', '_')}.json"
    if not path.exists():
        script = ("proof_inhabitation.py" if source == "inhabitation"
                  else "proof_repl.py")
        raise SystemExit(
            f"missing {path} — run {script} --mode model --model {model}")
    return json.loads(path.read_text())


def _record_output(rec: dict) -> str:
    """The model's answer string, normalised across the two harness schemas.

    single-shot (proof_inhabitation) stores the raw `model_output`; the REPL
    (proof_repl) stores the engine-reconstructed `term` when `proved` (the engine
    cannot commit an ill-typed term ⇒ a non-proof is an abstention, not a bad term)."""
    if "model_output" in rec:
        return rec["model_output"]
    if rec.get("proved") and rec.get("term"):
        return rec["term"]
    return "none"


def analyze(model_a: str, model_b: str, source: str) -> dict:
    da, db = load_model(model_a, source), load_model(model_b, source)
    ra = {r["id"]: r for r in da["records"]}
    rb = {r["id"]: r for r in db["records"]}
    ids = [i for i in ra if i in rb]

    rows = []
    for i in ids:
        a, b = ra[i], rb[i]
        prop = a["prop"]
        a_out, b_out = _record_output(a), _record_output(b)
        ka, va, valid_a = _answer_key(a_out, prop)
        kb, vb, valid_b = _answer_key(b_out, prop)
        provable = a["provable"]
        # task-correct: theorem -> a VALID proof; non-theorem -> NOT valid
        corr_a = valid_a if provable else (not valid_a)
        corr_b = valid_b if provable else (not valid_b)
        rows.append({
            "id": i, "prop": prop, "provable": provable,
            "complexity": a["complexity"], "y_trap": a.get("y_trap", False),
            "a_out": a_out, "b_out": b_out,
            "a_key": ka, "b_key": kb, "a_verdict": va, "b_verdict": vb,
            "a_valid": valid_a, "b_valid": valid_b,
            "a_correct": corr_a, "b_correct": corr_b,
            "agree": ka == kb, "both_correct": corr_a and corr_b,
        })

    n = len(rows)
    agree = [r for r in rows if r["agree"]]
    disagree = [r for r in rows if not r["agree"]]

    def p_correct(group: list[dict]) -> tuple[float, int]:
        if not group:
            return (0.0, 0)
        return (round(sum(r["both_correct"] for r in group) / len(group), 4),
                len(group))

    p_agree = p_correct(agree)
    p_disagree = p_correct(disagree)

    pos = [r for r in rows if r["provable"]]
    neg = [r for r in rows if not r["provable"]]

    def cell(group: list[dict], pred) -> list[str]:
        return [r["id"] for r in group if pred(r)]

    grid = {
        # positives
        "pos_both_valid_same": cell(
            pos, lambda r: r["a_valid"] and r["b_valid"] and r["agree"]),
        "pos_both_valid_diff": cell(
            pos, lambda r: r["a_valid"] and r["b_valid"] and not r["agree"]),
        "pos_one_valid": cell(
            pos, lambda r: r["a_valid"] != r["b_valid"]),
        "pos_both_invalid_same": cell(
            pos, lambda r: not r["a_valid"] and not r["b_valid"] and r["agree"]),
        "pos_both_invalid_diff": cell(
            pos, lambda r: not r["a_valid"] and not r["b_valid"] and not r["agree"]),
        # negatives
        "neg_both_abstain": cell(
            neg, lambda r: r["a_verdict"] == Verdict.NONE
            and r["b_verdict"] == Verdict.NONE),
        "neg_agreed_attempt": cell(
            neg, lambda r: r["agree"] and not (
                r["a_verdict"] == Verdict.NONE and r["b_verdict"] == Verdict.NONE)),
        "neg_disagree": cell(
            neg, lambda r: not r["agree"]),
        "neg_false_proof": cell(
            neg, lambda r: r["a_valid"] or r["b_valid"]),  # MUST be empty
    }

    # the s246 "agreed-error" set: both agree on the SAME answer, but it is WRONG
    agreed_error = [r["id"] for r in agree if not r["both_correct"]]

    out = {
        "models": [model_a, model_b],
        "source": source,
        "timestamp": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(),
        "n": n, "n_positive": len(pos), "n_negative": len(neg),
        "agreement_rate": round(len(agree) / max(n, 1), 4),
        "P_bothcorrect_given_agree": p_agree[0], "n_agree": p_agree[1],
        "P_bothcorrect_given_disagree": p_disagree[0], "n_disagree": p_disagree[1],
        "agreed_error_ids": agreed_error,
        "grid": grid,
        "rows": rows,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    name = "consensus.json" if source == "inhabitation" else f"consensus-{source}.json"
    (OUT_DIR / name).write_text(json.dumps(out, indent=2))
    out["_outfile"] = str(OUT_DIR / name)
    return out


def _print_summary(out: dict) -> None:
    a, b = out["models"]
    log("")
    log(f"  === PROOF CONSENSUS [{out['source']}] : {a}  ×  {b} ===")
    log(f"  n={out['n']} ({out['n_positive']} theorems, "
        f"{out['n_negative']} non-theorems)")
    log(f"  term-agreement rate           {out['agreement_rate']:.3f}")
    log(f"  P(both-correct | AGREE)       {out['P_bothcorrect_given_agree']:.3f}"
        f"  (n={out['n_agree']})")
    log(f"  P(both-correct | DISAGREE)    {out['P_bothcorrect_given_disagree']:.3f}"
        f"  (n={out['n_disagree']})")
    g = out["grid"]
    log("")
    log("  --- theorems ---")
    log(f"  ★ both-valid SAME proof   {len(g['pos_both_valid_same']):2}  "
        f"(portability: the proof both lineages agree on)")
    log(f"    both-valid DIFF proof   {len(g['pos_both_valid_diff']):2}  "
        f"(proof-irrelevance: distinct valid inhabitants) {g['pos_both_valid_diff']}")
    log(f"    one-valid (frontier)    {len(g['pos_one_valid']):2}  "
        f"{g['pos_one_valid']}")
    log(f"    both-invalid SAME       {len(g['pos_both_invalid_same']):2}  "
        f"(shared misconception) {g['pos_both_invalid_same']}")
    log(f"    both-invalid DIFF       {len(g['pos_both_invalid_diff']):2}  "
        f"{g['pos_both_invalid_diff']}")
    log("  --- non-theorems ---")
    log(f"  ★ both-abstain (⊥)        {len(g['neg_both_abstain']):2}  "
        f"(correct shared 'unprovable')")
    log(f"    agreed wrong attempt    {len(g['neg_agreed_attempt']):2}  "
        f"(same kernel-rejected term) {g['neg_agreed_attempt']}")
    log(f"    disagree                {len(g['neg_disagree']):2}  "
        f"{g['neg_disagree']}")
    log(f"    FALSE PROOF (must be 0) {len(g['neg_false_proof']):2}  "
        f"{g['neg_false_proof']}")
    log("")
    log(f"  agreed-error set (agree but ≥1 wrong): {out['agreed_error_ids']}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs=2,
                    default=["Qwen/Qwen3-14B", "google/gemma-4-31B-it"])
    ap.add_argument("--source", choices=["inhabitation", "repl"],
                    default="inhabitation",
                    help="single-shot (proof-inhabitation) or REPL (proof-repl)")
    args = ap.parse_args()
    out = analyze(args.models[0], args.models[1], args.source)
    _print_summary(out)
    log(f"  wrote {out['_outfile']}")


if __name__ == "__main__":
    main()
