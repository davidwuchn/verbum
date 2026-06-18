#!/usr/bin/env python3
"""RLVR GRPO trainer — fine-tune the compile front-end against the kernel reward (s241).

THE LOOP (spliced-reward-vsm-kernel.md, build-path step 2). GRPO = Group Relative Policy
Optimization: for each prompt, sample a GROUP of G completions, score each with the
VERIFIABLE reward (the kernel: 1 if the completion reduces to the gold normal form, else
0), and use the group's mean as the baseline — advantage_i = (r_i − mean)/std. No critic
network; the group is its own baseline. Learning concentrates on the FRONTIER (prompts
with mixed success); all-correct and all-wrong groups have zero advantage = zero
gradient (this is why the §8 foothold rate is load-bearing). The reward is
non-differentiable on purpose (the constructed kernel) — policy-gradient scores
rollouts, never backprops the reward, so the v12-v15 gradient-death is sidestepped.

THE REWARD is `verbum.reward.verifiable_reward` (R_parent, the exact terminal anchor,
representation-invariant). DECISION §7 = (a) timescale splice: the parent IS the
kernel's own pass. The inline Φ-shaping splice (§4) is NOT wired here yet — see the NOTE
below; a naive second reward_func returning Φ(terminal) would be the §4a TRAP (a raw
additive bonus has no invariance). The anchor stands alone first (build-path step 2);
the potential-based shaping is step 3 (per-token / actor-critic).

API pinned to trl 1.6.0 (read from .venv, runtime > docs): reward_funcs are called
`f(prompts=, completions=, completion_ids=, **cols)`; GRPOConfig.num_generations is G,
scale_rewards="group" is the group-relative baseline.

Usage:
  uv run --group rl python scripts/experiments/rlvr_grpo_train.py --dry-run  # CPU
  uv run --group rl python scripts/experiments/rlvr_grpo_train.py \
      --model Qwen/Qwen3-8B --k 8 --max-steps 200 --checkpoint-dir results/grpo/run1

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from verbum.compile_prompt import (  # noqa: E402
    build_prompt,
    clean_output,
    load_corpus_rows,
    to_chat,
)
from verbum.reward import RewardConfig, verifiable_reward  # noqa: E402

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


def kernel_reward(completions, normal_form, **kwargs):
    """The verifiable reward func (trl 1.6.0 signature).

    `completions` are the raw generated strings; `normal_form` is the gold-NF column
    forwarded from the dataset (one per completion). Returns one float per completion:
    R_parent = 1.0 iff the cleaned completion reduces to the gold normal form, else 0.0.
    Representation-invariant — any combinator path to the gold NF scores.
    """
    return [
        verifiable_reward(clean_output(c), nf, CFG)
        for c, nf in zip(completions, normal_form, strict=True)
    ]


def build_records(tok, split: str, limit: int | None) -> list[dict]:
    """Dataset records: prompt = chat-formatted (to_chat), gold NF carried as a column.

    `tok` may be None in --dry-run, falling back to the raw build_prompt; the real run
    routes through to_chat so the policy trains on the SAME prompt the density probe
    measured and the SFT seed taught (single source, no distribution mismatch).
    """
    rows = load_corpus_rows(split, limit)
    return [
        {
            "prompt": to_chat(tok, r["input"]) if tok is not None
            else build_prompt(r["input"]),
            "normal_form": r["normal_form"],
        }
        for r in rows
    ]


def run_dry(args) -> None:
    """CPU wiring check: build the dataset + score GOLD completions (must be 1.0)."""
    recs = build_records(None, args.split, args.limit or 6)
    rows = load_corpus_rows(args.split, args.limit or 6)
    golds = [r["output"] for r in rows]
    rewards = kernel_reward(
        completions=golds, normal_form=[r["normal_form"] for r in recs]
    )
    log(f"[dry-run] {len(recs)} records; model/trl NOT loaded")
    log(f"[dry-run] example prompt:\n{recs[0]['prompt']}\n")
    for r, gold, rew in zip(rows, golds, rewards, strict=True):
        log(f"  {r['input']!r}  gold={gold!r}  reward={rew}")
    dens = sum(rewards) / len(rewards)
    log(f"\n[dry-run] gold reward density={dens} (must be 1.0); reward_func wiring OK.")
    log("[dry-run] run with --group rl on GPU to train.")


def run_train(args) -> None:
    import torch
    import transformers
    import trl
    from datasets import Dataset
    from transformers import AutoTokenizer
    from trl import GRPOConfig, GRPOTrainer

    ckpt = Path(args.checkpoint_dir)
    ckpt.mkdir(parents=True, exist_ok=True)

    tok = AutoTokenizer.from_pretrained(args.model)
    records = build_records(tok, args.split, args.limit)
    dataset = Dataset.from_list(records)
    log(f"[{args.model}] GRPO on {len(records)} prompts, G={args.k}, "
        f"temp={args.temp}, lr={args.lr}")

    peft_config = None
    if args.lora:
        from peft import LoraConfig
        peft_config = LoraConfig(
            r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        )

    cfg = GRPOConfig(
        output_dir=str(ckpt),
        num_generations=args.k,
        per_device_train_batch_size=args.batch,
        gradient_accumulation_steps=args.grad_accum,
        max_completion_length=args.max_completion_length,
        temperature=args.temp,
        beta=args.beta,                 # KL-to-ref coeff (0.0 = off, GRPO default)
        learning_rate=args.lr,
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        log_completions=True,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        report_to="none",
        bf16=(args.dtype == "bfloat16"),
        seed=args.seed,
    )

    # run-provenance sidecar (AGENTS.md λ run_provenance)
    (ckpt / "run_meta.json").write_text(json.dumps({
        "timestamp": datetime.now(UTC).isoformat(),
        "model": args.model, "git_sha": git_sha(),
        "torch": torch.__version__, "transformers": transformers.__version__,
        "trl": trl.__version__,
        "split": args.split, "n_prompts": len(records),
        "reward": "verbum.reward.verifiable_reward (R_parent, surface register)",
        "grpo": {
            "num_generations": args.k, "per_device_train_batch_size": args.batch,
            "grad_accum": args.grad_accum, "temperature": args.temp,
            "beta": args.beta, "lr": args.lr, "max_steps": args.max_steps,
            "epochs": args.epochs, "lora": args.lora, "seed": args.seed,
        },
    }, indent=2), encoding="utf-8")

    trainer = GRPOTrainer(
        model=args.model,
        reward_funcs=[kernel_reward],
        args=cfg,
        train_dataset=dataset,
        peft_config=peft_config,
    )
    trainer.train()
    trainer.save_model(str(ckpt / "final"))
    log(f"  done; saved to {ckpt}/final")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="compile-train.canonical.jsonl")
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    ap.add_argument("--k", type=int, default=8, help="num_generations (group size G)")
    ap.add_argument("--batch", type=int, default=8,
                    help="per_device_train_batch_size (must be a multiple of --k)")
    ap.add_argument("--grad-accum", type=int, default=4)
    ap.add_argument("--max-completion-length", type=int, default=48)
    ap.add_argument("--temp", type=float, default=0.9)
    ap.add_argument("--beta", type=float, default=0.0, help="KL-to-ref coeff")
    ap.add_argument("--lr", type=float, default=1e-6)
    ap.add_argument("--epochs", type=float, default=1.0)
    ap.add_argument("--max-steps", type=int, default=-1)
    ap.add_argument("--logging-steps", type=int, default=1)
    ap.add_argument("--save-steps", type=int, default=100)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--lora", action="store_true", help="parameter-efficient (LoRA)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--checkpoint-dir", default="results/rlvr-grpo/run1")
    ap.add_argument("--dry-run", action="store_true",
                    help="CPU wiring check: build dataset + score gold, no model load")
    args = ap.parse_args()
    if args.batch % args.k != 0:
        ap.error(f"--batch ({args.batch}) must be a multiple of --k ({args.k})")
    if args.dry_run:
        run_dry(args)
    else:
        run_train(args)


if __name__ == "__main__":
    main()
