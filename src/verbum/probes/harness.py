"""Canonical compiler-probe harness — a model is a config, not a fork.

One run loop for the lambda-compiler P(λ) experiment, shared by every model.
A new model becomes a :class:`ModelConfig` (~15 lines); the harness loads the
canonical gated probe set (``probes/<set>.json``), calls the model via the
configured **transport**, grades the final answer with the four canonical
registers (:mod:`verbum.probes.grading`), and writes the canonical
``results/<short>-compiler/<run_id>/{meta.json,results.jsonl,summary.json}``
with full provenance (AGENTS.md S2 ``λ run_provenance``).

No grading or aggregation logic ever lives in a per-model script again
(S2 ``λ one_way`` / S5 ``λ simplify``). Two transports cover everything seen:

  - ``chat``       POST ``/v1/chat/completions``; server applies the template;
                   ``reasoning_extract_fn`` reads ``(reasoning, content)`` from
                   the response ``message`` dict (ornith, qwythos: the server
                   splits ``reasoning_content``).
  - ``completion`` ``verbum.client.Client`` ``/completion``; ``template_fn``
                   builds the ``<|im_start|>…`` prompt; ``reasoning_extract_fn``
                   parses ``(reasoning, content)`` from the raw generation
                   string (vibethinker: manual ``</think>`` parse).

License: MIT.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import httpx

from verbum.client import Client
from verbum.probes import grading
from verbum.results import collect_provenance

# Repo root: src/verbum/probes/harness.py → parents[3]
_ROOT = Path(__file__).resolve().parents[3]
PROBES_DIR = _ROOT / "probes"
RESULTS_DIR = _ROOT / "results"

# The canonical compiler system prompt (identical across all models — part of
# meta.json provenance; do not vary per model or the P(λ) is not comparable).
SYSTEM = (
    "You are a lambda-calculus compiler. Translate the input sentence into a "
    "single lambda-calculus / first-order-logic expression using the notation: "
    "λ ∀ ∃ . → ∧ ∨ ¬ and predicate application f(a,b). Preserve the predicate "  # noqa: RUF001
    "and entity names from the sentence. Output ONLY the final expression on one line."
)

Transport = Literal["chat", "completion"]


@dataclass(frozen=True)
class SamplingCfg:
    """Sampling configuration. Default is greedy (temperature 0.0)."""

    temperature: float = 0.0

    @property
    def greedy(self) -> bool:
        return self.temperature == 0.0


@dataclass(frozen=True)
class ModelConfig:
    """A model the harness can probe. A new model = one of these.

    Fields
    ------
    name        Model alias the server answers to (``"model"`` field).
    endpoint    ``http://host:port``.
    transport   ``"chat"`` (server-templated) or ``"completion"`` (manual).
    reasoning_extract_fn
                Maps the transport-specific raw response to
                ``(reasoning, content)``. For ``chat`` the input is the
                response ``message`` dict; for ``completion`` it is the raw
                generation string.
    template_fn ``(system, sentence) -> prompt`` for ``completion`` transport;
                ``None`` for ``chat`` (server applies its own template).
    gguf_path   For meta.json provenance.
    arch        Human-readable architecture note for provenance.
    quant       Quantization label for provenance.
    sampling    :class:`SamplingCfg` (default greedy).
    """

    name: str
    endpoint: str
    transport: Transport
    reasoning_extract_fn: Callable[[Any], tuple[str, str]]
    template_fn: Callable[[str, str], str] | None = None
    gguf_path: str | None = None
    arch: str = ""
    quant: str = "Q8_0"
    sampling: SamplingCfg = field(default_factory=SamplingCfg)

    def short(self) -> str:
        """Short slug for the results directory (``ornith-35b-a3b`` → ``ornith``)."""
        return self.name.split("-")[0]


# ── transport-specific reasoning extractors (reused by models.py) ────────────


def split_reasoning_field(message: dict[str, Any]) -> tuple[str, str]:
    """chat transport: server already split ``reasoning_content`` from ``content``."""
    return (
        message.get("reasoning_content", "") or "",
        message.get("content", "") or "",
    )


def parse_think_tag(raw: str) -> tuple[str, str]:
    """completion transport: split a single generation on ``</think>``."""
    if "</think>" in raw:
        head, _, tail = raw.partition("</think>")
        return head, tail
    return "", raw


# ── per-transport single-probe call ─────────────────────────────────────────


def _call_chat(
    client: httpx.Client,
    cfg: ModelConfig,
    sentence: str,
    n_predict: int,
    *,
    system: str = SYSTEM,
    no_think: bool = False,
) -> tuple[str, str, int | None, str | None]:
    body: dict[str, Any] = {
        "model": cfg.name,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": sentence},
        ],
        "temperature": cfg.sampling.temperature,
        "max_tokens": n_predict,
        "stream": False,
    }
    if no_think:
        # The switch that actually disables thinking on llama.cpp (s255):
        # chat_template_kwargs.enable_thinking=false. reasoning_budget=0 and
        # /no_think do NOT work.
        body["chat_template_kwargs"] = {"enable_thinking": False}
    try:
        r = client.post("/v1/chat/completions", json=body)
        r.raise_for_status()
        d = r.json()
        msg = d["choices"][0]["message"]
        reasoning, content = cfg.reasoning_extract_fn(msg)
        toks = (d.get("usage") or {}).get("completion_tokens")
        return reasoning, content, toks, None
    except Exception as exc:
        return "", "", None, repr(exc)


def _call_completion(
    client: Client,
    cfg: ModelConfig,
    sentence: str,
    n_predict: int,
    *,
    system: str = SYSTEM,
) -> tuple[str, str, int | None, str | None]:
    if cfg.template_fn is None:
        return "", "", None, "completion transport requires template_fn"
    prompt = cfg.template_fn(system, sentence)
    try:
        r = client.complete(
            prompt,
            n_predict=n_predict,
            temperature=cfg.sampling.temperature,
            stop=["<|im_end|>"],
        )
        reasoning, content = cfg.reasoning_extract_fn(r.content)
        return reasoning, content, r.tokens_predicted, r.error
    except Exception as exc:
        return "", "", None, repr(exc)


# ── the run loop ────────────────────────────────────────────────────────────


def run_compiler_probe(
    cfg: ModelConfig,
    *,
    probe_set: str = "compile-gradient",
    n_predict: int = 12000,
    limit: int = 0,
    no_think: bool = False,
    out_root: Path | None = None,
    verbose: bool = True,
) -> Path:
    """Run ``cfg`` against ``probes/<probe_set>.json``; write canonical results.

    Returns the run directory. ``limit > 0`` smoke-tests the first N probes.
    ``no_think=True`` disables the model's reasoning chain (chat transport only;
    s255: bypasses the fine-tune's halt-failure / overthink-collapse).
    """
    if no_think and cfg.transport != "chat":
        raise ValueError("no_think is only supported for the chat transport")
    ps_path = PROBES_DIR / f"{probe_set}.json"
    ps = json.loads(ps_path.read_text())
    probes = ps["probes"]
    if limit > 0:
        probes = probes[:limit]

    out_root = out_root or (RESULTS_DIR / f"{cfg.short()}-compiler")
    run_id = f"{cfg.short()}-compiler-" + time.strftime("%Y%m%d-%H%M%S")
    run_dir = out_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    prov = collect_provenance(project_root=_ROOT)

    meta = {
        "run_id": run_id,
        "model": cfg.name,
        "quant": cfg.quant,
        "gguf": cfg.gguf_path,
        "arch": cfg.arch,
        "server": cfg.endpoint,
        "transport": cfg.transport,
        "endpoint": (
            "/v1/chat/completions" if cfg.transport == "chat" else "/completion"
        ),
        "probe_set_id": ps.get("id"),
        "probe_set_version": ps.get("version"),
        "n_probes": len(probes),
        "system_prompt": SYSTEM,
        "sampling": {
            "temperature": cfg.sampling.temperature,
            "max_tokens": n_predict,
            "greedy": cfg.sampling.greedy,
            "no_think": no_think,
        },
        **prov,
    }
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    http_client = httpx.Client(base_url=cfg.endpoint, timeout=600.0)
    comp_client = (
        Client(base_url=cfg.endpoint) if cfg.transport == "completion" else None
    )

    rows: list[dict[str, Any]] = []
    t_run = time.perf_counter()
    try:
        with (run_dir / "results.jsonl").open("w") as fh:
            for i, p in enumerate(probes):
                sentence = p["prompt"]
                cat = p.get("category", "?")
                t0 = time.perf_counter()
                if cfg.transport == "chat":
                    reasoning, content, toks, err = _call_chat(
                        http_client, cfg, sentence, n_predict, no_think=no_think
                    )
                else:
                    reasoning, content, toks, err = _call_completion(
                        comp_client, cfg, sentence, n_predict
                    )
                dt = time.perf_counter() - t0

                final = grading.final_answer(content)
                reg = grading.grade(final)
                budget_hit = toks is not None and toks >= n_predict

                row = {
                    "probe_id": p["id"],
                    "category": cat,
                    "sentence": sentence,
                    "final": final,
                    "content": content,
                    "reasoning": reasoning,
                    "reasoning_chars": len(reasoning),
                    **reg,
                    "budget_hit": budget_hit,
                    "completion_tokens": toks,
                    "elapsed_s": round(dt, 2),
                    "error": err,
                }
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
                rows.append(row)
                if verbose:
                    flags = "".join(
                        ("Y" if reg[r] else ".") for r in grading.REGISTERS
                    )
                    print(
                        f"[{i + 1}/{len(probes)}] {p['id']:<14} {cat:<15} "
                        f"[{flags}] tok={toks} rc={len(reasoning)} "
                        f"{dt:.1f}s :: {final[:55]}",
                        flush=True,
                    )
    finally:
        http_client.close()
        if comp_client is not None:
            comp_client.close()

    agg = grading.aggregate_by_category(rows)
    n = agg["n"]
    overall = agg["overall"]
    summary = {
        "n": n,
        "registers": overall,
        # legacy aliases (per-register, for cross-run/back-compat comparison)
        "p_emits_formal": overall["emits_formal"],
        "p_lambda_binder_any_style": overall["lambda_binder_any_style"],
        "p_lambda_lenient": overall["lenient_lambda"],
        "p_kernel_valid": overall["kernel_valid"],
        "by_category": agg["by_category"],
        "frac_budget_hit": round(sum(r["budget_hit"] for r in rows) / n, 4)
        if n
        else 0.0,
        # overthink-collapse: empty committed final AND hit the token budget.
        "frac_collapsed": round(
            sum(1 for r in rows if not r["final"].strip() and r["budget_hit"]) / n, 4
        )
        if n
        else 0.0,
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
        "total_elapsed_s": round(time.perf_counter() - t_run, 1),
        "nucleus_reference_p_lambda": grading.NUCLEUS_REFERENCE_P_LAMBDA,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    if verbose:
        print("\n=== SUMMARY ===")
        print(json.dumps(summary, indent=2))
        print("run_dir:", run_dir)
    return run_dir


# ── reasoning experiment: is lambda compilation "pre-thinking"? ──────────────
# Three reasoning FORMATS over the same checkable tasks (s256). Held at no-think
# so the reasoning happens in CONTENT (controlled by the prompt), isolating the
# format effect from the model's native think channel.

ReasoningMode = Literal["direct", "cot", "lambda"]

REASONING_SYSTEM: dict[ReasoningMode, str] = {
    "direct": (
        "You are solving a reasoning problem. Output ONLY the final answer, on "
        "one line, prefixed exactly with 'ANSWER:'. Do not show any working."
    ),
    "cot": (
        "You are solving a reasoning problem. Reason step by step in plain "
        "prose. Then, on the last line, write your final answer prefixed "
        "exactly with 'ANSWER:'."
    ),
    "lambda": (
        "You are solving a reasoning problem. First translate the problem into "
        "a lambda-calculus / first-order-logic expression using λ ∀ ∃ . → ∧ ∨ ¬ "  # noqa: RUF001
        "and predicate application f(a,b). Then evaluate that expression step "
        "by step. Then, on the last line, write your final answer prefixed "
        "exactly with 'ANSWER:'."
    ),
}


def run_reasoning_probe(
    cfg: ModelConfig,
    *,
    mode: ReasoningMode = "direct",
    probe_set: str = "reasoning-check",
    n_predict: int = 4000,
    limit: int = 0,
    no_think: bool = True,
    out_root: Path | None = None,
    verbose: bool = True,
) -> Path:
    """Run ``cfg`` on a checkable reasoning set in one of three FORMATS.

    Tests whether lambda compilation acts as "pre-thinking" (S5 λ types): does
    reasoning *in lambda* (``mode="lambda"``) beat *prose* CoT and/or *direct*
    on accuracy / tokens / collapse? Grades with ``grading.check_answer`` on the
    probe's ``metadata.answer_type``. Default ``no_think=True`` so the reasoning
    format is the only varying factor.
    """
    if no_think and cfg.transport != "chat":
        raise ValueError("no_think is only supported for the chat transport")
    system = REASONING_SYSTEM[mode]

    ps_path = PROBES_DIR / f"{probe_set}.json"
    ps = json.loads(ps_path.read_text())
    probes = ps["probes"]
    if limit > 0:
        probes = probes[:limit]

    out_root = out_root or (RESULTS_DIR / f"{cfg.short()}-reasoning")
    run_id = f"{cfg.short()}-reasoning-{mode}-" + time.strftime("%Y%m%d-%H%M%S")
    run_dir = out_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    prov = collect_provenance(project_root=_ROOT)

    meta = {
        "run_id": run_id,
        "model": cfg.name,
        "quant": cfg.quant,
        "gguf": cfg.gguf_path,
        "arch": cfg.arch,
        "server": cfg.endpoint,
        "transport": cfg.transport,
        "mode": mode,
        "probe_set_id": ps.get("id"),
        "probe_set_version": ps.get("version"),
        "n_probes": len(probes),
        "system_prompt": system,
        "sampling": {
            "temperature": cfg.sampling.temperature,
            "max_tokens": n_predict,
            "greedy": cfg.sampling.greedy,
            "no_think": no_think,
        },
        **prov,
    }
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    http_client = httpx.Client(base_url=cfg.endpoint, timeout=600.0)
    comp_client = (
        Client(base_url=cfg.endpoint) if cfg.transport == "completion" else None
    )

    rows: list[dict[str, Any]] = []
    t_run = time.perf_counter()
    try:
        with (run_dir / "results.jsonl").open("w") as fh:
            for i, p in enumerate(probes):
                prompt = p["prompt"]
                cat = p.get("category", "?")
                gt = p["ground_truth"]
                atype = p.get("metadata", {}).get("answer_type", "token")
                t0 = time.perf_counter()
                if cfg.transport == "chat":
                    reasoning, content, toks, err = _call_chat(
                        http_client, cfg, prompt, n_predict,
                        system=system, no_think=no_think,
                    )
                else:
                    reasoning, content, toks, err = _call_completion(
                        comp_client, cfg, prompt, n_predict, system=system
                    )
                dt = time.perf_counter() - t0

                final = grading.extract_final(content)
                correct = grading.check_answer(final, gt, atype)
                budget_hit = toks is not None and toks >= n_predict

                row = {
                    "probe_id": p["id"],
                    "category": cat,
                    "answer_type": atype,
                    "prompt": prompt,
                    "ground_truth": gt,
                    "final": final,
                    "correct": correct,
                    "content": content,
                    "reasoning": reasoning,
                    "reasoning_chars": len(reasoning),
                    "budget_hit": budget_hit,
                    "completion_tokens": toks,
                    "elapsed_s": round(dt, 2),
                    "error": err,
                }
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
                rows.append(row)
                if verbose:
                    print(
                        f"[{i + 1}/{len(probes)}] {p['id']:<7} {cat:<11} "
                        f"{'OK ' if correct else ' . '} tok={toks} "
                        f"{dt:.1f}s :: {final[:40]!r} (gt {gt})",
                        flush=True,
                    )
    finally:
        http_client.close()
        if comp_client is not None:
            comp_client.close()

    n = len(rows)
    by_cat: dict[str, dict[str, int]] = {}
    for r in rows:
        c = by_cat.setdefault(r["category"], {"n": 0, "correct": 0})
        c["n"] += 1
        c["correct"] += int(r["correct"])
    summary = {
        "n": n,
        "mode": mode,
        "accuracy": round(sum(r["correct"] for r in rows) / n, 4) if n else 0.0,
        "by_category": {
            c: {"n": v["n"], "accuracy": round(v["correct"] / v["n"], 4)}
            for c, v in sorted(by_cat.items())
        },
        "frac_collapsed": round(
            sum(1 for r in rows if not r["final"].strip() and r["budget_hit"]) / n, 4
        )
        if n
        else 0.0,
        "frac_budget_hit": round(sum(r["budget_hit"] for r in rows) / n, 4)
        if n
        else 0.0,
        "mean_completion_tokens": round(
            sum(r["completion_tokens"] or 0 for r in rows) / n, 1
        )
        if n
        else 0,
        "total_elapsed_s": round(time.perf_counter() - t_run, 1),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    if verbose:
        print("\n=== SUMMARY ===")
        print(json.dumps(summary, indent=2))
        print("run_dir:", run_dir)
    return run_dir
