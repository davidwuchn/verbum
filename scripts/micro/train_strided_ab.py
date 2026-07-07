"""Strided-attention A/B on micro — does the v15 stride geometry work?

s262. The v15 Fibonacci-stride bet was never isolated (strides + ternary +
TD + VSM controllers changed together; the s191 assessment found relay
collapse but couldn't attribute it). This bench isolates the geometry on
the float microscope: 4 arms, identical seeded init, identical batches,
attention SUPPORT is the only variable.

  dense    full causal attention            (control)
  local    stride-1 only                    (locality null — must be beaten)
  fib      interleaved Fibonacci ladder     (the fair strided arm)
  fibband  ascending/descending bands       (v15-faithful sole-provider)

Reads (two-sided, λ measure):
  1. eval CE per arm — does strided match dense? does it beat local?
  2. relay diagnostic cos(attn_out, V_self) — does the s191 relay collapse
     appear in FLOAT? (if yes: geometry starves composition; if no: v15's
     collapse was ternary/TD, not strides)
  3. compile exact-match on held-out eval+test examples (greedy generation)

Writes results/micro-strided-ab/<run_id>/{meta.json,summary.json}.

Usage:
    uv run python scripts/micro/train_strided_ab.py --steps 2500 --seed 262
    uv run python scripts/micro/train_strided_ab.py --smoke   # 60 steps

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import MicroConfig
from micro_strided import (
    ARM_STRIDES,
    ARMS,
    attention_diagnostics,
    build_strided_micro,
)
from train_micro import (
    CompileDataLoader,
    generate,
    load_compile_examples,
    tokenize_examples,
)

TRAIN = "data/compile-train.canonical.jsonl"  # s261 reference corpus
EVAL = "data/compile-eval.canonical.jsonl"
TEST = "data/compile-test.canonical.jsonl"
OUT_ROOT = Path("results/micro-strided-ab")


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


# ══════════════════════════════════════════════════════════════════════
# Compile exact-match (held-out generation check)
# ══════════════════════════════════════════════════════════════════════


def compile_exact_match(model, examples, tokenizer, max_new: int = 64) -> dict:
    """Greedy-generate the FOL output for each example; exact-match rate."""
    n_exact = 0
    rows = []
    for ex in examples:
        prompt_tokens = tokenizer.encode(
            ex["input"] + "\n", add_special_tokens=False
        )
        gen = generate(model, prompt_tokens, tokenizer, max_new=max_new)
        text = tokenizer.decode(gen).split("\n")[0].strip()
        truth = ex["output"].strip()
        exact = text == truth
        n_exact += int(exact)
        rows.append({"input": ex["input"], "truth": truth,
                     "gen": text, "exact": exact})
    return {"exact_match": n_exact / max(len(examples), 1),
            "n": len(examples), "rows": rows}


# ══════════════════════════════════════════════════════════════════════
# One arm
# ══════════════════════════════════════════════════════════════════════


def train_arm(
    arm: str,
    cfg: MicroConfig,
    steps: int,
    seed: int,
    tokenizer,
    train_seqs,
    eval_batches,
    diag_tokens,
    eval_examples,
    test_examples,
    log_every: int = 100,
) -> dict:
    print(f"\n{'=' * 60}\nARM {arm}  (steps={steps}, seed={seed})\n{'=' * 60}")
    mx.random.seed(seed)
    np.random.seed(seed)
    model, _mods = build_strided_micro(cfg, arm)

    # Identical data order per arm
    loader = CompileDataLoader(
        train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id, seed=seed
    )

    lr_sched = optim.cosine_decay(cfg.lr, steps, cfg.lr * 0.01)
    warm = optim.linear_schedule(1e-7, cfg.lr, cfg.warmup_steps)

    def lr_fn(step):
        return warm(step) if step < cfg.warmup_steps else lr_sched(step)

    opt = optim.AdamW(learning_rate=lr_fn, weight_decay=cfg.weight_decay)

    def loss_fn(m, tok, tgt):
        _, loss = m(tok, tgt)
        return loss

    lgrad = nn.value_and_grad(model, loss_fn)

    def eval_ce() -> float:
        vals = []
        for inp, tgt in eval_batches:
            model(inp, tgt)
            vals.append(float(model._last_ce_loss.item()))
        return float(np.mean(vals))

    curve = []
    relay_traj = []
    t0 = time.time()
    for step in range(1, steps + 1):
        model._training_step = step
        inp, tgt = loader.next_batch()
        lv, grads = lgrad(model, mx.array(inp), mx.array(tgt))
        grads, gnorm = optim.clip_grad_norm(grads, cfg.grad_clip)
        opt.update(model, grads)
        mx.eval(model.parameters(), opt.state, lv, gnorm)

        if step % log_every == 0 or step == 1:
            ce = float(model._last_ce_loss.item())
            ev = eval_ce()
            curve.append({"step": step, "train_ce": round(ce, 4),
                          "eval_ce": round(ev, 4)})
            print(f"  step {step:5d} | train CE {ce:.4f} | eval CE {ev:.4f} "
                  f"| {time.time() - t0:.0f}s")
        if step % (log_every * 5) == 0 or step == 1:
            diags = attention_diagnostics(model, diag_tokens)
            mean_relay = float(np.mean([d["relay"] for d in diags]))
            relay_traj.append({"step": step,
                               "mean_relay": round(mean_relay, 4)})

    final_eval_ce = eval_ce()
    final_diags = attention_diagnostics(model, diag_tokens)
    em_eval = compile_exact_match(model, eval_examples, tokenizer)
    em_test = compile_exact_match(model, test_examples, tokenizer)
    elapsed = time.time() - t0

    max_relay = max(r for d in final_diags for r in d["relay"])
    n_relay_heads = sum(
        1 for d in final_diags for r in d["relay"] if r > 0.9
    )
    print(f"  FINAL | eval CE {final_eval_ce:.4f} | "
          f"exact eval {em_eval['exact_match']:.2f} "
          f"test {em_test['exact_match']:.2f} | "
          f"relay>0.9 heads {n_relay_heads}/16 (max {max_relay:.3f}) | "
          f"{elapsed:.0f}s")

    return {
        "arm": arm,
        "strides": ARM_STRIDES.get(arm),
        "final_eval_ce": round(final_eval_ce, 4),
        "exact_match_eval": em_eval["exact_match"],
        "exact_match_test": em_test["exact_match"],
        "n_relay_heads": n_relay_heads,
        "max_relay": round(max_relay, 4),
        "final_diagnostics": final_diags,
        "relay_trajectory": relay_traj,
        "curve": curve,
        "elapsed_s": round(elapsed, 1),
        "generations_test": em_test["rows"][:10],
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", nargs="+", default=list(ARMS), choices=ARMS)
    ap.add_argument("--steps", type=int, default=2500)
    ap.add_argument("--seed", type=int, default=262)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    steps = 60 if args.smoke else args.steps

    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")

    cfg = MicroConfig()
    train_ex = load_compile_examples(TRAIN)
    eval_ex = load_compile_examples(EVAL)
    test_ex = load_compile_examples(TEST)
    train_seqs = tokenize_examples(train_ex, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_seqs = tokenize_examples(eval_ex, tokenizer, cfg.max_seq_len, cfg.eod_id)
    lens = [len(s) for s in train_seqs]
    print(f"train {len(train_seqs)} ex | tok len mean {np.mean(lens):.1f} "
          f"p95 {np.percentile(lens, 95):.0f} max {max(lens)}")

    # FIXED eval batches — identical across arms. The eval set is tiny
    # (10 ex ≈ 190 tok): B=1 at a seq_len that fits the packed stream.
    eval_total = sum(len(s) for s in eval_seqs)
    eval_len = min(cfg.max_seq_len, eval_total - 2)
    ev_loader = CompileDataLoader(eval_seqs, 1, eval_len, cfg.eod_id, seed=99)
    eval_batches = []
    for _ in range(2):
        inp, tgt = ev_loader.next_batch()
        eval_batches.append((mx.array(inp), mx.array(tgt)))

    # FIXED diagnostic batch: full-length packed TRAIN stream (256 tok)
    # so long strides are exercised; identical across arms.
    diag_loader = CompileDataLoader(
        train_seqs, 2, cfg.max_seq_len, cfg.eod_id, seed=777
    )
    diag_tokens = mx.array(diag_loader.next_batch()[0])

    run_id = f"strided-ab-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"
    out_dir = OUT_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "run_id": run_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "git_sha": _git_sha(),
        "seed": args.seed,
        "steps": steps,
        "arms": args.arms,
        "arm_strides": {a: ARM_STRIDES.get(a) for a in args.arms},
        "window": 8, "radius": 2,
        "config": {"d_model": cfg.d_model, "n_layers": cfg.n_layers,
                   "n_heads": cfg.n_heads, "d_ff": cfg.d_ff,
                   "max_seq_len": cfg.max_seq_len,
                   "batch_size": cfg.batch_size, "lr": cfg.lr},
        "data": {"train": TRAIN, "eval": EVAL, "test": TEST,
                 "n_train": len(train_ex), "n_eval": len(eval_ex),
                 "n_test": len(test_ex)},
        "mlx_version": mx.__version__,
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"run {run_id} → {out_dir}")

    results = {}
    for arm in args.arms:
        results[arm] = train_arm(
            arm, cfg, steps, args.seed, tokenizer, train_seqs,
            eval_batches, diag_tokens, eval_ex, test_ex,
        )
        (out_dir / "summary.json").write_text(
            json.dumps(results, indent=2))  # incremental

    print(f"\n{'=' * 60}\nVERDICT TABLE (seed {args.seed}, {steps} steps)\n{'=' * 60}")
    print(f"{'arm':9s} {'eval_CE':>8s} {'em_eval':>8s} {'em_test':>8s} "
          f"{'relay>0.9':>10s} {'max_relay':>10s}")
    for arm, r in results.items():
        print(f"{arm:9s} {r['final_eval_ce']:8.4f} "
              f"{r['exact_match_eval']:8.2f} {r['exact_match_test']:8.2f} "
              f"{r['n_relay_heads']:>7d}/16 {r['max_relay']:10.3f}")
    print(f"\nwritten: {out_dir}/summary.json")


if __name__ == "__main__":
    main()
