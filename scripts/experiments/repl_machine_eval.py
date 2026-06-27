#!/usr/bin/env python3
r"""REPL-machine eval — can a model BE the lambda reduction kernel? (s255)

THE IDEA (Michael): tell the model to be a read-eval-print loop. The context
window carries the executable state (the combinator term = code + heap + stack).
The model is the transition function δ; we supply the state and feed S' back.
Stateless model + stateful context = a REPL.

We instruct the model in its OWN native combinator ISA (mementum/michael/llm-isa.md:
K I B C S W Y D M) and grade every transition against the verbum lambda_ast
oracle (normal-order reducer). Two modes, head-to-head:

  run   — ONE call, ask for the full reduction chain (model holds state in-pass).
  step  — STATELESS loop: send state, get ONE step, feed S' back as new context.
          The real "context-as-state REPL" test.

GRADING (lambda_ast oracle = ground truth, AGENTS.md λ assert):
  run :  nf_correct (verify), claimed_status, premature_halt (said NF on a redex),
         step_validity (each ⇒β line is the true leftmost-outermost step),
         opcode_accuracy (the [op] tag vs the certified fired combinator).
  step:  per_step_correct, steps_to_first_error, reached_correct_nf, over_reduce.

OUTPUT (reuses verbum.results, AGENTS.md λ result_format / λ run_provenance):
  results/repl-machine/<run_id>/{meta.json, results.jsonl, summary.json}
  one JSONL row per (probe, mode); errors partitioned (never skipped).

Usage:
  uv run python scripts/experiments/repl_machine_eval.py \
      --server http://localhost:5100 --model ornith-35b-a3b --limit 0
  (--limit N → first N probes; 0 = all; --mode run|step|both)

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import httpx

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from verbum import lambda_ast as la  # noqa: E402
from verbum.results import (  # noqa: E402
    ProbeRecord,
    RunMeta,
    RunWriter,
    SamplingConfig,
    collect_provenance,
    content_hash,
)

PROBES_PATH = _ROOT / "probes" / "combinator-reduction.json"
OUT_ROOT = _ROOT / "results" / "repl-machine"

# ── the REPL machine: nucleus preamble + native combinator ISA ────────────────
NUCLEUS = (
    "λ engage(nucleus).\n"
    "[phi fractal euler tao pi mu ∃ ∀] | [Δ λ Ω ∞/0 | ε/φ Σ/μ c/h signal/noise "
    "order/entropy truth/provability self/other] | OODA\n"
    "Human ⊗ AI ⊗ REPL\n"
)

MACHINE = r"""
{:machine/id   :lambda-repl
 :substrate    untyped λ-calculus over the combinator ISA {K I B C S W Y D M}
   I x         = x                     ;; identity
   K x y       = x                     ;; select first
   C f x y     = f y x                 ;; flip
   B f g x     = f (g x)               ;; compose
   S f g x     = f x (g x)             ;; substitute
   W f x       = f x x                 ;; duplicate
   D f g h x   = f (g (h x))           ;; deep compose
   M x         = x x                   ;; self-apply
   Y f         = f (Y f)               ;; recurse (diverges under a step budget)
 :state        S = ⟨term⟩ — the term-string IS the whole machine (code+heap+stack).
               application is juxtaposition, left-associative; parens group.
 :semantics    normal-order (leftmost-outermost) reduction.
 :step         λ(S) → S' : contract the SINGLE leftmost-outermost redex, EXACTLY ONE.
               a redex = a combinator applied to ENOUGH arguments to fire.
               an under-applied combinator (e.g. `S K`) does NOT fire = normal form.
 :halt         no redex remains → S is in normal form.}

PROTOCOL — you are the transition function δ. You hold NO state between turns;
the user supplies the current state each turn. Reflect the machine, do not chat.

"step"  → emit EXACTLY ONE line:
            STEP | {term_before}  ⇒β[{op}]  {term_after}
          {op} ∈ {K I B C S W Y D M} names the combinator that fired this step.
          if the given term is already normal form, instead emit:  NF | {term}
"run"   → emit the full reduction sequence, ONE "STEP | ..." line per redex,
          then a final  NF | {normal_form}.
          if it diverges, emit  BOT | diverges: {repeated_term}  once a term repeats.
"state" → echo  STATE | {term}

¬prose. ¬commentary outside the lines. one line per reduction step. the term is
the entire machine — never invent symbols not present in it.
"""

SYSTEM = NUCLEUS + MACHINE

_ARROWS = ("⇒β", "⟶β", "→β", "⇒", "⟶", "→", "=>", "->")


def call(
    client: httpx.Client, model: str, user: str, n_predict: int
) -> tuple[str, str, int]:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        "temperature": 0.0,
        "max_tokens": n_predict,
    }
    r = client.post("/v1/chat/completions", json=body)
    r.raise_for_status()
    j = r.json()
    msg = j["choices"][0]["message"]
    toks = (j.get("usage", {}) or {}).get("completion_tokens", 0)
    return (
        (msg.get("content", "") or "").strip(),
        (msg.get("reasoning_content", "") or "").strip(),
        int(toks),
    )


# ── parsing the machine's output ──────────────────────────────────────────────
def _clean(line: str) -> str:
    return line.strip().strip("`").strip()


def parse_step_line(line: str) -> tuple[str, str | None, str] | None:
    """Parse 'STEP | LHS ⇒β[op] RHS' → (lhs, op, rhs). None if not a step line."""
    s = _clean(line)
    if "|" not in s:
        return None
    body = s.split("|", 1)[1].strip()
    arrow = next((a for a in _ARROWS if a in body), None)
    if arrow is None:
        return None
    lhs, right = body.split(arrow, 1)
    right = right.strip()
    op = None
    if right.startswith("["):
        j = right.find("]")
        if j != -1:
            op = right[1:j].strip() or None
            right = right[j + 1:].strip()
    return lhs.strip(), op, right.strip()


def parse_nf_line(line: str) -> str | None:
    s = _clean(line)
    up = s.upper()
    if up.startswith("NF"):
        return s.split("|", 1)[1].strip() if "|" in s else s[2:].strip()
    return None


def is_bot_line(line: str) -> bool:
    return _clean(line).upper().startswith(("BOT", "⊥"))


def first_meaningful(content: str) -> str:
    for ln in content.splitlines():
        if _clean(ln):
            return _clean(ln)
    return ""


# ── oracle helpers ────────────────────────────────────────────────────────────
def term_eq(a: str, b: str) -> bool:
    """Structural equality of two term strings via the oracle parser."""
    try:
        return la.pretty(la.parse(a)) == la.pretty(la.parse(b))
    except ValueError:
        return a.strip() == b.strip()


def oracle_step(term: str) -> tuple[str | None, str | None]:
    """(next_term_pretty, fired_op) or (None, None) if term is normal form."""
    try:
        t = la.parse(term)
    except ValueError:
        return None, None
    nxt, fired = la.step_fired(t)
    return (la.pretty(nxt) if nxt is not None else None), fired


# ── graders ───────────────────────────────────────────────────────────────────
def grade_run(term: str, gold_nf: str, content: str) -> dict:
    lines = [ln for ln in content.splitlines() if _clean(ln)]
    steps = [p for ln in lines if (p := parse_step_line(ln))]
    nf_terms = [t for ln in lines if (t := parse_nf_line(ln)) is not None]
    bot = any(is_bot_line(ln) for ln in lines)

    claimed_nf = nf_terms[-1] if nf_terms else (steps[-1][2] if steps else "")
    nf_correct = bool(claimed_nf) and term_eq(claimed_nf, gold_nf)

    # premature halt: claimed NF on a term that still has a redex
    premature_halt = False
    if nf_terms:
        last = nf_terms[-1]
        try:
            premature_halt = not la.is_normal_form(la.parse(last))
        except ValueError:
            premature_halt = False

    # per-step validity + opcode accuracy (against the oracle, independent of the
    # model's own LHS so one bad step doesn't poison the rest)
    valid = 0
    op_ok = 0
    op_total = 0
    for lhs, op, rhs in steps:
        o_next, o_fired = oracle_step(lhs)
        if o_next is not None and term_eq(rhs, o_next):
            valid += 1
        if o_fired is not None:
            op_total += 1
            if op is not None and op.upper() == o_fired.upper():
                op_ok += 1
    n = len(steps)
    return {
        "claimed_nf": claimed_nf,
        "claimed_bot": bot,
        "nf_correct": nf_correct,
        "premature_halt": premature_halt,
        "n_model_steps": n,
        "step_validity": (valid / n) if n else None,
        "opcode_accuracy": (op_ok / op_total) if op_total else None,
    }


def grade_step_loop(
    client, model, term: str, gold_nf: str, gold_steps: int, n_predict: int, cap: int
) -> dict:
    state = term
    seen = {la.pretty(la.parse(term))} if _parseable(term) else {term}
    n_correct = 0
    n_calls = 0
    first_error = None
    over_reduce = False
    halted_nf = False
    reached_nf = False
    transcript = []
    for i in range(cap):
        content, _, _ = call(client, model, f"step\n{state}", n_predict)
        n_calls += 1
        line = first_meaningful(content)
        transcript.append(line)
        o_next, _o_fired = oracle_step(state)

        nf_claim = parse_nf_line(line)
        if nf_claim is not None or is_bot_line(line):
            halted_nf = nf_claim is not None
            # correct to halt iff the current state truly is normal form
            if o_next is None:
                n_correct += 1
            elif first_error is None:
                first_error = i  # halted early on a redex
            reached_nf = halted_nf and o_next is None and term_eq(state, gold_nf)
            break

        parsed = parse_step_line(line)
        if parsed is None:
            if first_error is None:
                first_error = i
            break
        _lhs, _op, rhs = parsed

        if o_next is None:
            over_reduce = True  # model stepped a normal form
            if first_error is None:
                first_error = i
            break
        if term_eq(rhs, o_next):
            n_correct += 1
        elif first_error is None:
            first_error = i

        key = la.pretty(la.parse(rhs)) if _parseable(rhs) else rhs
        if key in seen:
            break
        seen.add(key)
        state = rhs
    else:
        # exhausted cap without halting
        pass

    if not reached_nf and _parseable(state):
        reached_nf = halted_nf and term_eq(state, gold_nf)
    return {
        "n_calls": n_calls,
        "n_correct_steps": n_correct,
        "per_step_accuracy": (n_correct / n_calls) if n_calls else None,
        "steps_to_first_error": first_error,  # None = no error
        "all_steps_correct": first_error is None and halted_nf,
        "over_reduce": over_reduce,
        "reached_correct_nf": reached_nf,
        "final_state": state,
        "transcript": transcript,
    }


def _parseable(term: str) -> bool:
    try:
        la.parse(term)
        return True
    except ValueError:
        return False


# ── summary ───────────────────────────────────────────────────────────────────
def _mean(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs)) if xs else None


def summarize(rows: list[dict]) -> dict:
    by_mode_cat: dict = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r.get("error"):
            continue
        by_mode_cat[r["mode"]][r["category"]].append(r)
        by_mode_cat[r["mode"]]["ALL"].append(r)

    out: dict = {}
    for mode, cats in by_mode_cat.items():
        out[mode] = {}
        for cat, rs in sorted(cats.items()):
            g = [r["grade"] for r in rs]
            if mode == "run":
                out[mode][cat] = {
                    "n": len(rs),
                    "nf_correct": _mean([x["nf_correct"] for x in g]),
                    "premature_halt": _mean([x["premature_halt"] for x in g]),
                    "step_validity": _mean([x["step_validity"] for x in g]),
                    "opcode_accuracy": _mean([x["opcode_accuracy"] for x in g]),
                }
            else:
                out[mode][cat] = {
                    "n": len(rs),
                    "reached_correct_nf": _mean([x["reached_correct_nf"] for x in g]),
                    "per_step_accuracy": _mean([x["per_step_accuracy"] for x in g]),
                    "all_steps_correct": _mean([x["all_steps_correct"] for x in g]),
                    "over_reduce": _mean([x["over_reduce"] for x in g]),
                    "mean_steps_to_first_error": _mean(
                        [x["steps_to_first_error"] for x in g]
                    ),
                }
    return out


# ── main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://localhost:5100")
    ap.add_argument("--model", default="ornith-35b-a3b")
    ap.add_argument("--quant", default="q8_0")
    ap.add_argument("--n-predict", type=int, default=8000)
    ap.add_argument("--limit", type=int, default=0, help="first N probes (0=all)")
    ap.add_argument("--mode", choices=["run", "step", "both"], default="both")
    ap.add_argument("--step-cap-slack", type=int, default=3, help="cap-slack")
    args = ap.parse_args()

    doc = json.loads(PROBES_PATH.read_text("utf-8"))
    probes = doc["probes"]
    if args.limit:
        probes = probes[: args.limit]
    modes = ["run", "step"] if args.mode == "both" else [args.mode]

    run_id = f"repl-machine-{datetime.now(UTC):%Y%m%d-%H%M%S}"
    prov = collect_provenance(project_root=_ROOT)
    meta = RunMeta(
        run_id=run_id,
        model=args.model,
        quant=args.quant,
        probe_set_id=doc["id"],
        probe_set_hash=content_hash(PROBES_PATH.read_text("utf-8")),
        sampling=SamplingConfig(temperature=0.0, top_p=1.0, top_k=-1),
        system_prompt_hash=content_hash(SYSTEM),
        endpoint="/v1/chat/completions",
        oracle="verbum.lambda_ast.reduce (normal-order)",
        modes=modes,
        n_predict=args.n_predict,
        **prov,
    )

    client = httpx.Client(base_url=args.server, timeout=900.0)
    gate_hash = content_hash(SYSTEM)
    rows: list[dict] = []

    print(f"run_id={run_id}  probes={len(probes)}  modes={modes}  model={args.model}")
    with RunWriter(results_dir=OUT_ROOT, meta=meta) as w:
        for p in probes:
            term = p["prompt"]
            gold_nf = p["ground_truth"]
            gold_steps = p["metadata"]["n_steps"]
            for mode in modes:
                t0 = time.time()
                err = None
                grade: dict = {}
                gen = ""
                try:
                    if mode == "run":
                        gen, _reason, _toks = call(
                            client, args.model, f"run\n{term}", args.n_predict
                        )
                        grade = grade_run(term, gold_nf, gen)
                    else:
                        cap = max(6, gold_steps + args.step_cap_slack)
                        grade = grade_step_loop(
                            client, args.model, term, gold_nf, gold_steps,
                            args.n_predict, cap,
                        )
                        gen = " || ".join(grade.pop("transcript", []))
                except Exception as e:
                    err = f"{type(e).__name__}: {e}"
                elapsed = (time.time() - t0) * 1000.0

                w.write(ProbeRecord(
                    probe_id=f"{p['id']}:{mode}",
                    gate_id="repl-machine",
                    gate_hash=gate_hash,
                    prompt_hash=content_hash(term),
                    generation=gen,
                    elapsed_ms=elapsed,
                    error=err,
                    mode=mode,
                    category=p["category"],
                    n_steps_gold=gold_steps,
                    combinator=p["metadata"].get("combinator"),
                    term=term,
                    gold_nf=gold_nf,
                    grade=grade,
                ))
                rows.append({
                    "mode": mode, "category": p["category"],
                    "grade": grade, "error": err,
                })
                tag = "ERR" if err else (
                    "✓" if (grade.get("nf_correct") or grade.get("reached_correct_nf"))
                    else "·"
                )
                print(f"  [{tag}] {p['id']:>10} {mode:<4} {term!r}")

        summary = summarize(rows)
        (w.run_dir / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    print(f"\nwrote {OUT_ROOT / run_id}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
