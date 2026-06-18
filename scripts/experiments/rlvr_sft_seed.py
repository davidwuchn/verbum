#!/usr/bin/env python3
"""SFT-seed — token-CE fine-tune the compile front-end before RLVR (s241).

WHY (spliced-reward-vsm-kernel.md §8, settled by measurement). The §8 cold-start probe
+ temperature sweep (s241) showed the base-model reward is BIMODAL and temperature-
robust: ~25/36 dead-category prompts stay 0/8 at every temperature (relative_clause
0/11, quantified perfectly bimodal). The dead prompts are ZERO-probability — the base
model does not know the target logical form — so RLVR-from-base has no foothold and no
amount of sampling creates one. The fix is to TEACH the target form first: a short
supervised fine-tune on the certified canonical corpus (prose→surface-FOL) lifts the
dead categories into a learnable regime, THEN GRPO refines and frees the realisation
diversity (the reward is representation-invariant, so RL is not pinned to the SFT form).

THIS IS THE SEED, NOT THE WHOLE LOOP. Output `<checkpoint-dir>/final` is the policy the
GRPO trainer consumes:  rlvr_grpo_train.py --model <checkpoint-dir>/final

Loss = completion-only token-CE: the prompt (instruction + few-shot + the sentence) is
MASKED; the loss is computed only on the gold logical form. The prompt is the chat-
formatted `verbum.compile_prompt.to_chat` — the SAME prompt the density probe measured
and the GRPO loop uses (single source; no train/measure distribution mismatch).

API pinned to trl 1.6.0 (read from .venv): SFTTrainer(model, args=SFTConfig,
train_dataset, peft_config); a prompt-completion dataset auto-sets completion_only_loss.

Usage:
  uv run --group rl python scripts/experiments/rlvr_sft_seed.py --dry-run   # CPU wiring
  uv run --group rl python scripts/experiments/rlvr_sft_seed.py \
      --model Qwen/Qwen3-8B --epochs 2 --checkpoint-dir results/rlvr-sft/run1

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

from verbum.compile_prompt import build_prompt, load_corpus_rows  # noqa: E402


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT
        ).decode().strip()
    except Exception:
        return "unknown"


def build_records(tok, split: str, limit: int | None) -> list[dict]:
    """Prompt-completion records: prompt = chat-formatted; completion = gold form.

    `tok` may be None in --dry-run, in which case the raw build_prompt is used (the
    completion masking + chat template are exercised only in the real run).
    """
    from verbum.compile_prompt import to_chat  # local: tok-dependent

    rows = load_corpus_rows(split, limit)
    out = []
    for r in rows:
        prompt = (
            to_chat(tok, r["input"]) if tok is not None
            else build_prompt(r["input"])
        )
        out.append({"prompt": prompt, "completion": " " + r["output"]})
    return out


def run_dry(args) -> None:
    """CPU wiring check: build the prompt-completion dataset, no torch/trl load."""
    recs = build_records(None, args.split, args.limit or 4)
    log(f"[dry-run] {len(recs)} prompt-completion records; model/trl NOT loaded\n")
    ex = recs[0]
    log("[dry-run] example record (completion-only loss masks the prompt):")
    log(f"  PROMPT (masked, raw build_prompt shown; real run applies chat template):\n"
        f"{ex['prompt']}")
    log(f"  COMPLETION (loss here): {ex['completion']!r}")
    log("\n[dry-run] all completions are certified gold forms (100% certify, s240).")
    log("[dry-run] wiring OK; run with --group rl on GPU to SFT-seed.")


def run_train(args) -> None:
    import torch
    import transformers
    import trl
    from datasets import Dataset
    from transformers import AutoTokenizer
    from trl import SFTConfig, SFTTrainer

    ckpt = Path(args.checkpoint_dir)
    ckpt.mkdir(parents=True, exist_ok=True)

    tok = AutoTokenizer.from_pretrained(args.model)
    records = build_records(tok, args.split, args.limit)
    dataset = Dataset.from_list(records)
    log(f"[{args.model}] SFT-seed on {len(records)} prompt-completion pairs, "
        f"epochs={args.epochs}, lr={args.lr}")

    peft_config = None
    if args.lora:
        from peft import LoraConfig
        peft_config = LoraConfig(
            r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        )

    cfg = SFTConfig(
        output_dir=str(ckpt),
        max_length=args.max_length,
        completion_only_loss=True,      # mask the prompt; loss only on the gold form
        packing=False,
        learning_rate=args.lr,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch,
        gradient_accumulation_steps=args.grad_accum,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        bf16=(args.dtype == "bfloat16"),
        report_to="none",
        seed=args.seed,
    )

    (ckpt / "run_meta.json").write_text(json.dumps({
        "timestamp": datetime.now(UTC).isoformat(),
        "stage": "sft-seed", "model": args.model, "git_sha": git_sha(),
        "torch": torch.__version__, "transformers": transformers.__version__,
        "trl": trl.__version__,
        "split": args.split, "n_pairs": len(records),
        "loss": "completion-only token-CE (prompt masked)",
        "sft": {
            "max_length": args.max_length, "lr": args.lr, "epochs": args.epochs,
            "per_device_train_batch_size": args.batch, "grad_accum": args.grad_accum,
            "lora": args.lora, "seed": args.seed,
        },
        "next": f"rlvr_grpo_train.py --model {ckpt}/final",
    }, indent=2), encoding="utf-8")

    trainer = SFTTrainer(
        model=args.model,
        args=cfg,
        train_dataset=dataset,
        peft_config=peft_config,
    )
    trainer.train()
    trainer.save_model(str(ckpt / "final"))
    tok.save_pretrained(str(ckpt / "final"))
    log(f"  done; SFT seed saved to {ckpt}/final")
    log(f"  next: rlvr_grpo_train.py --model {ckpt}/final")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="compile-train.canonical.jsonl")
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    ap.add_argument("--max-length", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--epochs", type=float, default=2.0)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--grad-accum", type=int, default=4)
    ap.add_argument("--logging-steps", type=int, default=5)
    ap.add_argument("--save-steps", type=int, default=200)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--lora", action="store_true", help="parameter-efficient (LoRA)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--checkpoint-dir", default="results/rlvr-sft/run1")
    ap.add_argument("--dry-run", action="store_true",
                    help="CPU wiring check: build dataset, no model load")
    args = ap.parse_args()
    if args.dry_run:
        run_dry(args)
    else:
        run_train(args)


if __name__ == "__main__":
    main()
