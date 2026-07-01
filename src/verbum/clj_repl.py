r"""clj_repl — a REPL where the MODEL evaluates and the KERNEL verifies.

THE ROLE (session 259, Michael: "run the clojure compiler as a repl running from a
chat" → "Model IS the evaluator, kernel verifies"). This is the s255 *model-as-REPL*
design (the LLM as the transition function δ, context as machine state) with the
*oracle-in-the-loop* upgrade s255 concluded was the winning shape — applied to the
`clj_lambda` Clojure subset:

    user form ──▶ CHAT MODEL evaluates (δ)         ──▶ proposes  => <value>
                 clj_lambda KERNEL reduces (oracle) ──▶ exact     => <value>
                 verify(model, oracle) ──▶ ✓ | ✗ → feed correction back → retry

The model is the *evaluator*; the kernel (`clj_lambda` over `lambda_ast`) is the
*judge*. On a mismatch the exact reduction (value + step count + normal form) is fed
back as the teaching signal — verify ≪ generate (checking is bounded+local, S5
`λ self_improve` VERIFY gate; `λ assert`: runtime ≡ truth).

Reuses the canonical fleet (`harness.ModelConfig`, `models.REGISTRY`) and its
`reasoning_extract_fn`; adds only a thin *multi-turn* chat caller (the run loop in
`harness.run_compiler_probe` is single-turn — a correction REPL needs history). No
fork of grading or the HTTP client (S2 `λ one_way` / `λ compose`).

License: MIT. AGENTS.md S5 λ provenance.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from verbum import clj_lambda as clj
from verbum.lambda_ast import Status, pretty
from verbum.probes.harness import ModelConfig
from verbum.probes.models import REGISTRY
from verbum.results import collect_provenance

_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = _ROOT / "results"

# The evaluator (δ) system prompt. Pins the tiny-Clojure semantics so the model and
# the kernel agree on the language, and fixes the answer contract we parse.
EVALUATOR_SYSTEM = (
    "You are the evaluator (the reduction function) of a tiny Clojure-like Lisp. "
    "Evaluate the given expression to a single value.\n\n"
    "Language:\n"
    "- non-negative integers; booleans `true` / `false`.\n"
    "- `(fn [params] body)` anonymous function; `(let [name val ...] body)`.\n"
    "- application `(f a b)` is left-associative.\n"
    "- arithmetic on non-negative integers: `+`, `*`, and `-` is MONUS "
    "(truncated: `(- 3 5)` = 0). `inc`; `dec` with `(dec 0)` = 0.\n"
    "- `zero?`; `if`; `not`, `and`, `or`.\n"
    "- pairs: `(cons a b)`, `first`, `rest`.\n"
    "- `Y` is the fixed-point combinator: `(Y f)` = `(f (Y f))` (recursion).\n\n"
    "Reduce step by step. Then, on the FINAL line, output exactly:\n"
    "=> <value>\n"
    "where <value> is an integer, or `true` / `false`, or `(cons a b)` for a pair."
)

CORRECTION_TEMPLATE = (
    "Incorrect. A trusted reference reducer evaluated it to `{value}` in {steps} "
    "reduction steps (normal form: `{nf}`). Re-evaluate carefully and end with the "
    "final line `=> <value>`."
)

_ANSWER_RE = re.compile(r"=>\s*(.+?)\s*$", re.MULTILINE)
_INT_RE = re.compile(r"-?\d+")


# --------------------------------------------------------------------------- #
# Oracle — the kernel is ground truth                                          #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class OracleResult:
    """The exact evaluation of a form by the clj_lambda kernel.

    `acceptable` holds ALL normalized strings a correct answer may take. It is
    usually `{value}`, but untyped Church encoding makes `false ≡ 0` (both are the
    term `K I`) — so a predicate/zero result accepts BOTH. This ambiguity is the
    type-directedness thesis in miniature: with types they differ, without types
    they are the same value (S5 λ types)."""

    value: str          # primary display value ("5" | "true" | pretty(nf))
    acceptable: frozenset[str]
    status: Status
    steps: int
    trace_len: int
    whnf_step: int | None
    normal_form: str


def oracle(form: str, max_steps: int = clj.DEFAULT_STEPS,
           max_size: int = clj.DEFAULT_SIZE) -> OracleResult:
    """Reduce `form` in the kernel and decode the ground-truth value."""
    red = clj.reduce_clj(form, max_steps=max_steps, max_size=max_size)
    nf = red.normal_form
    if red.status is not Status.NORMAL_FORM:
        value = f"<{red.status.value}>"
        acceptable = frozenset({value})
    else:
        value = _decode_value(nf, max_steps, max_size)
        acceptable = _acceptable(value)
    return OracleResult(
        value=value,
        acceptable=acceptable,
        status=red.status,
        steps=red.steps,
        trace_len=len(red.trace),
        whnf_step=red.whnf_step,
        normal_form=pretty(nf),
    )


def _acceptable(value: str) -> frozenset[str]:
    """Church `false` and `0` are the same term (`K I`) — accept both."""
    if value == "0":
        return frozenset({"0", "false"})
    return frozenset({value})


def _decode_value(nf: Any, max_steps: int, max_size: int) -> str:
    for kind, fmt in (("int", str), ("bool", lambda b: "true" if b else "false")):
        try:
            return fmt(clj.decode(nf, kind=kind, max_steps=max_steps,
                                  max_size=max_size))
        except ValueError:
            continue
    return pretty(nf)  # e.g. a pair — no scalar decoding


# --------------------------------------------------------------------------- #
# Answer parsing + normalisation                                              #
# --------------------------------------------------------------------------- #
def parse_answer(content: str) -> str | None:
    """Extract the LAST `=> <value>` the model emitted, else None."""
    matches = _ANSWER_RE.findall(content or "")
    return matches[-1].strip() if matches else None


def normalize(s: str | None) -> str:
    """Canonicalise a value string for comparison (int, bool, or trimmed raw)."""
    if s is None:
        return ""
    s = s.strip().strip("`").strip().rstrip(".").strip()
    low = s.lower()
    if low in ("true", "false"):
        return low
    m = _INT_RE.fullmatch(s)
    if m:
        return str(int(s))
    # a bare integer embedded in noise (e.g. "the answer is 6")
    found = _INT_RE.findall(s)
    if len(found) == 1:
        return str(int(found[0]))
    return s


# --------------------------------------------------------------------------- #
# Multi-turn chat transport (thin; reuses ModelConfig + reasoning_extract_fn)   #
# --------------------------------------------------------------------------- #
def _chat(
    client: httpx.Client,
    cfg: ModelConfig,
    messages: list[dict[str, str]],
    n_predict: int,
    *,
    no_think: bool = False,
) -> tuple[str, str, int | None, str | None]:
    body: dict[str, Any] = {
        "model": cfg.name,
        "messages": messages,
        "temperature": cfg.sampling.temperature,
        "max_tokens": n_predict,
        "stream": False,
    }
    if no_think:
        body["chat_template_kwargs"] = {"enable_thinking": False}
    try:
        r = client.post("/v1/chat/completions", json=body)
        r.raise_for_status()
        msg = r.json()["choices"][0]["message"]
        reasoning, content = cfg.reasoning_extract_fn(msg)
        toks = (r.json().get("usage") or {}).get("completion_tokens")
        return reasoning, content, toks, None
    except Exception as exc:  # surface transport errors as data, never raise
        return "", "", None, repr(exc)


# --------------------------------------------------------------------------- #
# One verified REPL turn (model evaluates, kernel judges, correct once)         #
# --------------------------------------------------------------------------- #
@dataclass
class Attempt:
    role: str            # "eval" | "retry"
    answer: str | None
    normalized: str
    correct: bool
    content: str
    reasoning_chars: int
    tokens: int | None
    elapsed_s: float
    error: str | None


@dataclass
class TurnRecord:
    form: str
    oracle: OracleResult
    attempts: list[Attempt] = field(default_factory=list)

    @property
    def solved(self) -> bool:
        return any(a.correct for a in self.attempts)

    @property
    def solved_first_try(self) -> bool:
        return bool(self.attempts) and self.attempts[0].correct


def verify_turn(
    client: httpx.Client,
    cfg: ModelConfig,
    form: str,
    *,
    n_predict: int = 8000,
    no_think: bool = False,
    max_retries: int = 1,
) -> TurnRecord:
    """Run one REPL turn: model evaluates `form`, kernel verifies, correct once.

    The kernel oracle is computed FIRST (it is the ground truth). The model answer
    is graded against it; on a mismatch the exact reduction is fed back and the
    model retries up to `max_retries` times (oracle-in-the-loop)."""
    orc = oracle(form)
    acceptable = orc.acceptable
    rec = TurnRecord(form=form, oracle=orc)

    messages = [
        {"role": "system", "content": EVALUATOR_SYSTEM},
        {"role": "user", "content": form},
    ]
    role = "eval"
    for attempt_i in range(max_retries + 1):
        t0 = time.perf_counter()
        reasoning, content, toks, err = _chat(
            client, cfg, messages, n_predict, no_think=no_think
        )
        dt = time.perf_counter() - t0
        ans = parse_answer(content)
        norm = normalize(ans)
        correct = norm in acceptable and norm != ""
        rec.attempts.append(
            Attempt(role, ans, norm, correct, content, len(reasoning), toks, dt, err)
        )
        if correct or attempt_i == max_retries or err is not None:
            break
        # oracle-in-the-loop correction
        messages.append({"role": "assistant", "content": content})
        messages.append({
            "role": "user",
            "content": CORRECTION_TEMPLATE.format(
                value=orc.value, steps=orc.steps, nf=orc.normal_form
            ),
        })
        role = "retry"
    return rec


# --------------------------------------------------------------------------- #
# Session — a batch of forms, reproducible record (λ record)                    #
# --------------------------------------------------------------------------- #
DEMO_FORMS = [
    "(+ 2 3)",
    "(* 4 5)",
    "(- 3 5)",                                   # monus → 0
    "(if (zero? 0) 10 20)",
    "(let [x 4 y (* x 3)] (+ x y))",
    "((fn [f] (f (f 2))) (fn [n] (+ n 3)))",     # higher-order apply-twice → 8
    "(first (cons 7 9))",
    "(and true (not false))",
    "(Y (fn [self] (fn [n] (if (zero? n) 1 (* n (self (dec n)))))) 4)",  # 4! = 24
    "(let [sq (fn [n] (* n n))] (sq (+ 3 4)))",  # 49 — a common miss
]


def repl_session(
    cfg: ModelConfig | str,
    forms: list[str] | None = None,
    *,
    n_predict: int = 8000,
    no_think: bool = False,
    max_retries: int = 1,
    out_root: Path | None = None,
    verbose: bool = True,
) -> Path:
    """Evaluate `forms` with model-as-δ + kernel-as-oracle; write a run record.

    Writes results/clj-repl/<run_id>/{meta.json, transcript.jsonl, summary.json}
    with full provenance. `cfg` may be a REGISTRY short-name (e.g. "ornith")."""
    if isinstance(cfg, str):
        cfg = REGISTRY[cfg]
    if cfg.transport != "chat":
        raise ValueError("clj_repl needs the chat transport (multi-turn correction)")
    forms = forms if forms is not None else DEMO_FORMS

    out_root = out_root or (RESULTS_DIR / "clj-repl")
    run_id = f"{cfg.short()}-clj-repl-" + time.strftime("%Y%m%d-%H%M%S")
    run_dir = out_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "meta.json").write_text(json.dumps({
        "run_id": run_id, "model": cfg.name, "endpoint": cfg.endpoint,
        "transport": cfg.transport, "system_prompt": EVALUATOR_SYSTEM,
        "n_forms": len(forms), "max_retries": max_retries, "no_think": no_think,
        "sampling": {"temperature": cfg.sampling.temperature, "max_tokens": n_predict},
        **collect_provenance(project_root=_ROOT),
    }, indent=2))

    records: list[TurnRecord] = []
    client = httpx.Client(base_url=cfg.endpoint, timeout=600.0)
    try:
        with (run_dir / "transcript.jsonl").open("w") as fh:
            for i, form in enumerate(forms):
                rec = verify_turn(
                    client, cfg, form, n_predict=n_predict,
                    no_think=no_think, max_retries=max_retries,
                )
                fh.write(json.dumps(_row(rec), ensure_ascii=False) + "\n")
                fh.flush()
                records.append(rec)
                if verbose:
                    _print_turn(i, len(forms), rec)
    finally:
        client.close()

    summary = _summarize(records)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    if verbose:
        print("\n=== SUMMARY ===")
        print(json.dumps(summary, indent=2))
        print("run_dir:", run_dir)
    return run_dir


def _row(rec: TurnRecord) -> dict[str, Any]:
    return {
        "form": rec.form,
        "oracle_value": rec.oracle.value,
        "oracle_status": rec.oracle.status.value,
        "oracle_steps": rec.oracle.steps,
        "solved": rec.solved,
        "solved_first_try": rec.solved_first_try,
        "attempts": [
            {
                "role": a.role, "answer": a.answer, "normalized": a.normalized,
                "correct": a.correct, "reasoning_chars": a.reasoning_chars,
                "tokens": a.tokens, "elapsed_s": round(a.elapsed_s, 2),
                "error": a.error,
            }
            for a in rec.attempts
        ],
    }


def _summarize(records: list[TurnRecord]) -> dict[str, Any]:
    n = len(records)
    return {
        "n": n,
        "solved": sum(r.solved for r in records),
        "solved_first_try": sum(r.solved_first_try for r in records),
        "fixed_by_correction": sum(
            r.solved and not r.solved_first_try for r in records
        ),
        "unsolved": [r.form for r in records if not r.solved],
        "acc_first_try": round(sum(r.solved_first_try for r in records) / n, 4)
        if n else 0.0,
        "acc_after_correction": round(sum(r.solved for r in records) / n, 4)
        if n else 0.0,
    }


def _print_turn(i: int, total: int, rec: TurnRecord) -> None:
    first = rec.attempts[0] if rec.attempts else None
    got = first.normalized if first else "?"
    if rec.solved_first_try:
        mark = "✓"
    elif rec.solved:
        mark = "✓(after correction)"
    else:
        mark = "✗"
    kern = rec.oracle.value
    if len(rec.oracle.acceptable) > 1:
        kern += " (≡ false)" if kern == "0" else ""
    print(
        f"[{i + 1}/{total}] {rec.form:<58} "
        f"model={got!r:>8} kernel={kern!r:>12} "
        f"({rec.oracle.steps} steps)  {mark}",
        flush=True,
    )


# --------------------------------------------------------------------------- #
# Interactive REPL (for live use from a terminal / chat)                        #
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    """`python -m verbum.clj_repl [--model ornith] [--no-think]` — a live REPL.

    Type a Clojure form; the model evaluates it and the kernel verifies. `:quit`
    to exit, `:oracle <form>` to see only the kernel's exact reduction."""
    import argparse

    ap = argparse.ArgumentParser(description="Model-evaluates, kernel-verifies REPL")
    ap.add_argument("--model", default="qwen36", help="REGISTRY short name")
    ap.add_argument("--no-think", action="store_true", help="disable model reasoning")
    ap.add_argument("--n-predict", type=int, default=8000)
    ap.add_argument("--retries", type=int, default=1)
    args = ap.parse_args(argv)

    cfg = REGISTRY[args.model]
    if cfg.transport != "chat":
        print(f"{args.model} is not a chat model; clj_repl needs chat transport.")
        return 2
    print(f"clj_repl — {cfg.name} @ {cfg.endpoint} | model evaluates, kernel verifies")
    print("type a Clojure form, ':oracle <form>' for kernel-only, ':quit' to exit\n")

    client = httpx.Client(base_url=cfg.endpoint, timeout=600.0)
    try:
        while True:
            try:
                line = input("clj> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not line:
                continue
            if line in (":quit", ":q"):
                break
            if line.startswith(":oracle "):
                _repl_oracle(line[len(":oracle "):].strip())
                continue
            try:
                rec = verify_turn(
                    client, cfg, line, n_predict=args.n_predict,
                    no_think=args.no_think, max_retries=args.retries,
                )
            except (SyntaxError, NameError, ValueError) as exc:
                print(f"  parse/compile error: {exc}")
                continue
            _print_turn(0, 1, rec)
    finally:
        client.close()
    return 0


def _repl_oracle(form: str) -> None:
    try:
        orc = oracle(form)
    except (SyntaxError, NameError, ValueError) as exc:
        print(f"  parse/compile error: {exc}")
        return
    print(f"  kernel => {orc.value}  ({orc.status.value}, {orc.steps} steps, "
          f"nf={orc.normal_form})")


if __name__ == "__main__":
    raise SystemExit(main())
