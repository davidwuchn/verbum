#!/usr/bin/env python3
"""RLVR cold-start reward-density probe — the §8 decider (session 241).

THE QUESTION (spliced-reward-vsm-kernel.md §8). RLVR learns from CONTRAST between
rollouts: per prompt, sample k candidates, the kernel scores each (1 if it reduces to
the gold normal form, else 0), policy-gradient climbs the variance. The cold-start
failure mode is ZERO reward density — if every sample for a prompt scores 0, the batch
is all-zeros, no gradient, no foothold. RL amplifies success it stumbles into; it
cannot manufacture the first success. So the whole SFT-seed-vs-RLVR-from-base decision
reduces to ONE measured number: when the BASE MODEL samples on our corpus prompts, what
fraction of prompts get >=1 kernel-certified sample (the RL FOOTHOLD rate)?

  high density (most prompts have a foothold)  ->  RLVR from base (cleaner, diverse)
  sparse / many all-zero prompts               ->  SFT-seed first (lift density first)

This MEASURES it rather than guessing (AGENTS.md λ observation). It is a SAMPLING pass
(no training); it reuses the reward built this session (`verbum.reward`). The §1/smoke
"100% density" graded the GOLD outputs — this grades the BASE MODEL, the number §8
actually needs.

Usage:
  uv run python scripts/experiments/rlvr_coldstart_density.py --dry-run   # CPU only
  uv run python scripts/experiments/rlvr_coldstart_density.py \
      --model Qwen/Qwen3-8B --k 8 --temp 0.8

License: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from verbum.compile_prompt import (  # noqa: E402
    build_prompt,
    clean_output,
    load_corpus_rows,
)
from verbum.reward import RewardConfig, reward  # noqa: E402

CFG = RewardConfig(parse="surface")


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT
        ).decode().strip()
    except Exception:
        return "unknown"


def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def summarise(records: list[dict], k: int) -> dict:
    n = len(records)
    n_foothold = sum(1 for r in records if r["n_correct"] >= 1)
    mean_reward = (
        sum(s for r in records for s in r["rewards"]) / max(n * k, 1)
    )
    any_parse = sum(1 for r in records if r["n_parsed"] >= 1)
    return {
        "n_prompts": n,
        "k": k,
        "foothold_rate": round(n_foothold / max(n, 1), 4),  # >=1 correct sample
        "mean_sample_reward": round(mean_reward, 4),        # reward density
        "any_parse_rate": round(any_parse / max(n, 1), 4),
        "n_all_zero": n - n_foothold,                       # the RL dead prompts
    }


def grade_samples(samples: list[str], gold_nf: str) -> dict:
    rewards, parsed = [], 0
    for s in samples:
        res = reward(s, gold_nf, CFG)
        rewards.append(res.reward)
        parsed += int(res.channels.parsed)
    return {
        "rewards": rewards,
        "n_correct": int(sum(rewards)),
        "n_parsed": parsed,
    }


def run_dry(args) -> None:
    """CPU wiring check: build prompts, grade the GOLD output (density must be 1.0)."""
    rows = load_corpus_rows(args.split, args.limit or 5)
    log(f"[dry-run] {len(rows)} prompts (few-shot excluded); model NOT loaded\n")
    log("[dry-run] example built prompt (first row):")
    log(build_prompt(rows[0]["input"]))
    log("")
    records = []
    for r in rows:
        graded = grade_samples([r["output"]], r["normal_form"])  # gold as the sample
        records.append({"input": r["input"], **graded})
        log(f"  {r['input']}")
        log(f"    -> gold {r['output']!r}  reward={graded['rewards'][0]}")
    summ = summarise(
        [{**rec, "rewards": rec["rewards"]} for rec in records], k=1
    )
    log(f"\n[dry-run] gold foothold_rate={summ['foothold_rate']} "
        f"(must be 1.0) mean_reward={summ['mean_sample_reward']}")
    log("[dry-run] wiring OK; run without --dry-run on GPU to measure the base model.")


def run_model(args) -> None:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    t0 = time.time()
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    rows = load_corpus_rows(args.split, args.limit)
    log(f"[{args.model}] {len(rows)} prompts × k={args.k} @ temp={args.temp}")

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()

    records = []
    with torch.no_grad():
        for i, r in enumerate(rows):
            prompt = build_prompt(r["input"])
            try:
                text = tok.apply_chat_template(
                    [{"role": "user", "content": prompt}],
                    tokenize=False, add_generation_prompt=True,
                    enable_thinking=False)
            except (TypeError, ValueError):
                text = tok.apply_chat_template(
                    [{"role": "user", "content": prompt}],
                    tokenize=False, add_generation_prompt=True)
            enc = tok(text, return_tensors="pt").to(args.device)
            out = model.generate(
                **enc, max_new_tokens=40, do_sample=True,
                temperature=args.temp, top_p=args.top_p,
                num_return_sequences=args.k,
                pad_token_id=tok.pad_token_id or tok.eos_token_id)
            gen = [
                clean_output(tok.decode(
                    out[j][enc["input_ids"].shape[1]:], skip_special_tokens=True))
                for j in range(args.k)
            ]
            graded = grade_samples(gen, r["normal_form"])
            records.append({
                "input": r["input"], "gold": r["output"],
                "gold_nf": r["normal_form"], "category": r.get("category"),
                "samples": gen, **graded,
            })
            if (i + 1) % 25 == 0:
                log(f"    {i + 1}/{len(rows)}")

    summ = summarise(records, args.k)

    out_dir = ROOT / "results" / "rlvr-coldstart-density" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "run_id": run_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "model": args.model,
        "quant": args.dtype,
        "model_revision": args.revision,
        "device": args.device,
        "git_sha": git_sha(),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "transformers": __import__("transformers").__version__,
        "probe_set": args.split,
        "probe_set_hash": file_hash(ROOT / "data" / args.split),
        "sampling": {
            "k": args.k, "temperature": args.temp, "top_p": args.top_p,
            "seed": args.seed, "max_new_tokens": 40,
        },
        "summary": summ,
        "elapsed_s": round(time.time() - t0, 1),
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    (out_dir / "results.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n"
    )

    log("")
    log(f"  === COLD-START DENSITY — {args.model} ({summ['n_prompts']} prompts, "
        f"k={args.k}, temp={args.temp}) ===")
    log(f"  FOOTHOLD rate (>=1 correct sample): {summ['foothold_rate']:.1%}  "
        f"({summ['n_prompts'] - summ['n_all_zero']}/{summ['n_prompts']})")
    log(f"  mean sample reward (density):        {summ['mean_sample_reward']:.3f}")
    log(f"  any-parse rate:                      {summ['any_parse_rate']:.1%}")
    log(f"  all-zero (RL-dead) prompts:          {summ['n_all_zero']}")
    verdict = (
        "high → RLVR-from-base viable" if summ["foothold_rate"] >= 0.5
        else "sparse → SFT-seed first"
    )
    log(f"\n  VERDICT: {verdict}")
    log(f"  wrote {out_dir}/meta.json + results.jsonl  ({meta['elapsed_s']}s)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="compile-train.canonical.jsonl")
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    ap.add_argument("--revision", default=None)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--temp", type=float, default=0.8)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--dry-run", action="store_true",
                    help="CPU wiring check: build prompts + grade gold, no model load")
    args = ap.parse_args()
    if args.dry_run:
        run_dry(args)
    else:
        import torch
        torch.manual_seed(args.seed)
        run_model(args)


if __name__ == "__main__":
    main()
