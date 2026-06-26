#!/usr/bin/env python3
"""VibeThinker lambda-compiler test (reasoning-model gated generation).

VibeThinker-3B (qwen2 arch, RL-tuned reasoner) on llama.cpp HTTP cannot do
bare few-shot completion (degenerates to repetition) and COLLAPSES when its
<think> chain is suppressed. So the honest "lambda compiler" probe lets the
model reason, then parses the post-</think> final answer and grades its
well-formedness on two registers (AGENTS.md S5 λ measure / λ yardstick):

  - LENIENT  P(λ): the final answer emits lambda/FOL notation
                   (λ-binder OR ∀/∃ quantifier with predicate application).
                   This is the ROUTING register — "did the compiler fire."
  - STRICT   kernel-valid: verbum.lambda_surface.to_kernel parses it.
                   This is the VALUE register — "is it canonically well-formed."

Records results/vibethinker-compiler/<run_id>/{results.jsonl,meta.json} with
full provenance (AGENTS.md S2 λ run_provenance).

Usage:
  uv run python scripts/experiments/vibethinker_compiler_test.py \
      --server http://localhost:5102 --n-predict 10000 --limit 0
  (--limit N smoke-tests the first N probes; 0 = all)

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_ROOT = _SCRIPT_DIR.parent.parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from verbum.client import Client  # noqa: E402
from verbum.lambda_surface import to_kernel  # noqa: E402
from verbum.results import collect_provenance  # noqa: E402

PROBES_PATH = _ROOT / "probes" / "compile-gradient.json"
OUT_ROOT = _ROOT / "results" / "vibethinker-compiler"

SYSTEM = (
    "You are a lambda-calculus compiler. Translate the input sentence into a "
    "single lambda-calculus / first-order-logic expression using the notation: "
    "λ ∀ ∃ . → ∧ ∨ ¬ and predicate application f(a,b). Preserve the predicate "  # noqa: RUF001
    "and entity names from the sentence. Output ONLY the final expression on one line."
)

# Lenient P(λ): a λ-binder, OR a quantifier, with at least one predicate-style
# application f(...). "did the compiler fire" — routing register.
_LAMBDA_TOK = re.compile(r"[λ∀∃ιⲗ\\]")
_PRED_APP = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\s*\(")


def _chat_prompt(sentence: str) -> str:
    return (
        f"<|im_start|>system\n{SYSTEM}<|im_end|>\n"
        f"<|im_start|>user\n{sentence}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


def _final_answer(text: str) -> str:
    """Post-</think> answer, first non-empty content line."""
    tail = text.split("</think>")[-1] if "</think>" in text else text
    for line in tail.strip().splitlines():
        s = line.strip().strip("`").strip()
        if s:
            return s
    return tail.strip()


def _lenient_lambda(expr: str) -> bool:
    return bool(_LAMBDA_TOK.search(expr) and _PRED_APP.search(expr))


def _kernel_valid(expr: str) -> bool:
    try:
        to_kernel(expr)
        return True
    except Exception:
        return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://localhost:5102")
    ap.add_argument("--n-predict", type=int, default=10000)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--limit", type=int, default=0, help="0=all probes")
    ap.add_argument("--model", default="vibethinker-3b-q8_0")
    ap.add_argument("--quant", default="Q8_0")
    args = ap.parse_args()

    ps = json.loads(PROBES_PATH.read_text())
    probes = ps["probes"]
    if args.limit > 0:
        probes = probes[: args.limit]

    run_id = "vibethinker-compiler-" + time.strftime("%Y%m%d-%H%M%S")
    run_dir = OUT_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    prov = collect_provenance(project_root=_ROOT)

    meta = {
        "run_id": run_id,
        "model": args.model,
        "quant": args.quant,
        "gguf": "/Users/mwhitford/localai/models/vibethinker/vibethinker-3b-q8_0.gguf",
        "server": args.server,
        "probe_set_id": ps.get("id"),
        "probe_set_version": ps.get("version"),
        "n_probes": len(probes),
        "system_prompt": SYSTEM,
        "sampling": {
            "temperature": args.temperature,
            "n_predict": args.n_predict,
            "greedy": args.temperature == 0.0,
        },
        **prov,
    }
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    client = Client(base_url=args.server)
    rows = []
    n_lenient = n_kernel = n_closed = n_budget = 0
    t_run = time.perf_counter()
    try:
        with (run_dir / "results.jsonl").open("w") as fh:
            for i, p in enumerate(probes):
                sentence = p["prompt"]
                prompt = _chat_prompt(sentence)
                t0 = time.perf_counter()
                try:
                    r = client.complete(
                        prompt,
                        n_predict=args.n_predict,
                        temperature=args.temperature,
                        stop=["<|im_end|>"],
                    )
                    gen = r.content
                    err = r.error
                    toks = r.tokens_predicted
                except Exception as exc:
                    gen, err, toks = "", repr(exc), None
                dt = time.perf_counter() - t0

                closed = "</think>" in gen
                final = _final_answer(gen)
                lenient = _lenient_lambda(final)
                kernel = _kernel_valid(final)
                budget_hit = toks is not None and toks >= args.n_predict

                n_closed += closed
                n_lenient += lenient
                n_kernel += kernel
                n_budget += budget_hit

                row = {
                    "probe_id": p["id"],
                    "category": p.get("category"),
                    "sentence": sentence,
                    "final": final,
                    "lenient_lambda": lenient,
                    "kernel_valid": kernel,
                    "closed_think": closed,
                    "budget_hit": budget_hit,
                    "tokens_predicted": toks,
                    "elapsed_s": round(dt, 2),
                    "error": err,
                    "generation": gen,
                }
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
                rows.append(row)
                print(
                    f"[{i + 1}/{len(probes)}] {p['id']:<14} "
                    f"λ={'Y' if lenient else '.'} k={'Y' if kernel else '.'} "
                    f"think={'closed' if closed else 'OPEN'} "
                    f"tok={toks} {dt:.1f}s :: {final[:70]}",
                    flush=True,
                )
    finally:
        client.close()

    n = len(rows)
    summary = {
        "n": n,
        "p_lambda_lenient": round(n_lenient / n, 4) if n else 0.0,
        "p_kernel_valid": round(n_kernel / n, 4) if n else 0.0,
        "frac_think_closed": round(n_closed / n, 4) if n else 0.0,
        "frac_budget_hit": round(n_budget / n, 4) if n else 0.0,
        "mean_tokens": round(
            sum(r["tokens_predicted"] or 0 for r in rows) / n, 1
        )
        if n
        else 0,
        "total_elapsed_s": round(time.perf_counter() - t_run, 1),
        "nucleus_reference_p_lambda": 0.907,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print("run_dir:", run_dir)


if __name__ == "__main__":
    main()
