#!/usr/bin/env python3
"""ornith-35b-a3b lambda-compiler test (reasoning MoE, chat-completions gated).

ornith (ornith-35b-a3b, Qwen-family-derived MoE, ~3B active of 35B, Q8_0 GGUF,
n_vocab 248320, n_ctx 262144) is a REASONING model served on llama.cpp whose
HTTP server cleanly SEPARATES the reasoning chain (`reasoning_content`) from the
final answer (`content`) via /v1/chat/completions. So unlike the VibeThinker
harness (which manually wrapped the chat template and parsed `</think>` out of a
single completion string), here we let the server apply its own template and read
the clean final answer directly from `content`.

Grades the final answer on two registers (AGENTS.md S5 λ measure / λ yardstick):

  - LENIENT  P(λ): the final answer emits lambda/FOL notation
                   (λ-binder OR ∀/∃ quantifier with predicate application).
                   ROUTING register — "did the compiler fire."
  - STRICT   kernel-valid: verbum.lambda_surface.to_kernel parses it.
                   VALUE register — "is it canonically well-formed."

Records results/ornith-compiler/<run_id>/{results.jsonl,meta.json,summary.json}
with full provenance (AGENTS.md S2 λ run_provenance).

Usage:
  uv run python scripts/experiments/ornith_compiler_test.py \
      --server http://localhost:5100 --n-predict 12000 --limit 0
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

import httpx

_SCRIPT_DIR = Path(__file__).resolve().parent
_ROOT = _SCRIPT_DIR.parent.parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from verbum.lambda_surface import to_kernel  # noqa: E402
from verbum.results import collect_provenance  # noqa: E402

PROBES_PATH = _ROOT / "probes" / "compile-gradient.json"
OUT_ROOT = _ROOT / "results" / "ornith-compiler"

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


def _final_answer(content: str) -> str:
    """First non-empty content line (the server already stripped reasoning)."""
    tail = content.split("</think>")[-1] if "</think>" in content else content
    for line in tail.strip().splitlines():
        s = line.strip().strip("`").strip()
        if s:
            return s
    return tail.strip()


def _lenient_lambda(expr: str) -> bool:
    return bool(_LAMBDA_TOK.search(expr) and _PRED_APP.search(expr))


def _emits_formal(expr: str) -> bool:
    """Any λ/∀/∃ binder OR predicate application — catches atomic predications
    (`runs(dog)`) the binder-requiring lenient register false-misses."""
    return bool(_LAMBDA_TOK.search(expr) or _PRED_APP.search(expr))


def _kernel_valid(expr: str) -> bool:
    try:
        to_kernel(expr)
        return True
    except Exception:
        return False


def _chat(
    client: httpx.Client, model: str, sentence: str, n_predict: int, temperature: float
) -> tuple[str, str, int | None, int | None, str | None]:
    """Return (content, reasoning, content_tokens, total_tokens, error)."""
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": sentence},
        ],
        "temperature": temperature,
        "max_tokens": n_predict,
        "stream": False,
    }
    try:
        r = client.post("/v1/chat/completions", json=body)
        r.raise_for_status()
        d = r.json()
        msg = d["choices"][0]["message"]
        content = msg.get("content", "") or ""
        reasoning = msg.get("reasoning_content", "") or ""
        usage = d.get("usage", {}) or {}
        total = usage.get("completion_tokens")
        return content, reasoning, None, total, None
    except Exception as exc:
        return "", "", None, None, repr(exc)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://localhost:5100")
    ap.add_argument("--n-predict", type=int, default=12000)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--limit", type=int, default=0, help="0=all probes")
    ap.add_argument("--model", default="ornith-35b-a3b")
    ap.add_argument("--quant", default="Q8_0")
    args = ap.parse_args()

    ps = json.loads(PROBES_PATH.read_text())
    probes = ps["probes"]
    if args.limit > 0:
        probes = probes[: args.limit]

    run_id = "ornith-compiler-" + time.strftime("%Y%m%d-%H%M%S")
    run_dir = OUT_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    prov = collect_provenance(project_root=_ROOT)

    meta = {
        "run_id": run_id,
        "model": args.model,
        "quant": args.quant,
        "gguf": "/Users/mwhitford/localai/models/ornith/ornith-1.0-35b-Q8_0.gguf",
        "arch": "35B-A3B MoE (n_vocab 248320, n_embd 2048, n_ctx 262144)",
        "server": args.server,
        "endpoint": "/v1/chat/completions",
        "probe_set_id": ps.get("id"),
        "probe_set_version": ps.get("version"),
        "n_probes": len(probes),
        "system_prompt": SYSTEM,
        "sampling": {
            "temperature": args.temperature,
            "max_tokens": args.n_predict,
            "greedy": args.temperature == 0.0,
        },
        **prov,
    }
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    client = httpx.Client(base_url=args.server, timeout=600.0)
    rows = []
    n_lenient = n_kernel = n_budget = n_formal = 0
    by_cat: dict[str, dict[str, int]] = {}
    t_run = time.perf_counter()
    try:
        with (run_dir / "results.jsonl").open("w") as fh:
            for i, p in enumerate(probes):
                sentence = p["prompt"]
                cat = p.get("category", "?")
                t0 = time.perf_counter()
                content, reasoning, _, toks, err = _chat(
                    client, args.model, sentence, args.n_predict, args.temperature
                )
                dt = time.perf_counter() - t0

                final = _final_answer(content)
                lenient = _lenient_lambda(final)
                formal = _emits_formal(final)
                kernel = _kernel_valid(final)
                budget_hit = toks is not None and toks >= args.n_predict
                reasoning_chars = len(reasoning)

                n_lenient += lenient
                n_formal += formal
                n_kernel += kernel
                n_budget += budget_hit
                c = by_cat.setdefault(
                    cat, {"n": 0, "lenient": 0, "formal": 0, "kernel": 0}
                )
                c["n"] += 1
                c["lenient"] += int(lenient)
                c["formal"] += int(formal)
                c["kernel"] += int(kernel)

                row = {
                    "probe_id": p["id"],
                    "category": cat,
                    "sentence": sentence,
                    "final": final,
                    "content": content,
                    "lenient_lambda": lenient,
                    "emits_formal": formal,
                    "kernel_valid": kernel,
                    "budget_hit": budget_hit,
                    "completion_tokens": toks,
                    "reasoning_chars": reasoning_chars,
                    "elapsed_s": round(dt, 2),
                    "error": err,
                    "reasoning": reasoning,
                }
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
                rows.append(row)
                print(
                    f"[{i + 1}/{len(probes)}] {p['id']:<14} {cat:<15} "
                    f"λ={'Y' if lenient else '.'} f={'Y' if formal else '.'} "
                    f"k={'Y' if kernel else '.'} "
                    f"tok={toks} rc={reasoning_chars} {dt:.1f}s :: {final[:55]}",
                    flush=True,
                )
    finally:
        client.close()

    n = len(rows)
    cat_summary = {
        k: {
            "n": v["n"],
            "p_lambda": round(v["lenient"] / v["n"], 4) if v["n"] else 0.0,
            "p_formal": round(v["formal"] / v["n"], 4) if v["n"] else 0.0,
            "p_kernel": round(v["kernel"] / v["n"], 4) if v["n"] else 0.0,
        }
        for k, v in sorted(by_cat.items())
    }
    summary = {
        "n": n,
        "p_lambda_lenient": round(n_lenient / n, 4) if n else 0.0,
        "p_emits_formal": round(n_formal / n, 4) if n else 0.0,
        "p_kernel_valid": round(n_kernel / n, 4) if n else 0.0,
        "frac_budget_hit": round(n_budget / n, 4) if n else 0.0,
        "mean_completion_tokens": round(
            sum(r["completion_tokens"] or 0 for r in rows) / n, 1
        )
        if n
        else 0,
        "mean_reasoning_chars": round(
            sum(r["reasoning_chars"] for r in rows) / n, 1
        )
        if n
        else 0,
        "by_category": cat_summary,
        "total_elapsed_s": round(time.perf_counter() - t_run, 1),
        "nucleus_reference_p_lambda": 0.907,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print("run_dir:", run_dir)


if __name__ == "__main__":
    main()
