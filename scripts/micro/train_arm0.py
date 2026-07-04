"""Arm 0 — reproduce + instrument the ternary sign flip-flop on micro.

Hypothesis under test (Michael, s261): TernaryDescent oscillated because GD
wants the weight to output differently depending on the input — an
"overloading" of the function. In s257 terms: a float weight holographically
multiplexes several functions (read at different angles); a ternary weight
({-1,0,+1}) can't hold that superposition, so the sign oscillates trying to
serve each angle in turn, never reaching a normal form.

This run makes the overloading VISIBLE and MEASURABLE:

  1. Train a ternary-FFN micro (mode=td by default) on the compile corpus,
     tracking per-weight sign FLIPS every step (the oscillation).
  2. Run a per-CATEGORY gradient-sign-demand diagnostic: for each input
     category (quantified, transitive, negation, ...) compute the gradient
     each ternary FFN weight receives. A weight is CONTESTED if some
     categories pull its sign + and others pull it - (irreconcilable demand).
  3. THE TEST: are the oscillating (high-flip) weights the contested ones?
     If mean-flips(contested) >> mean-flips(uncontested), overloading is
     confirmed — the flip-flop is a superposition collision, not a bug.

Compare `--mode td` (reproduce), `--mode st` (does relaxation hide it?),
`--mode none` (float baseline loss curve).

Writes results/micro-ternary-arm0/<mode>-<run_id>/{meta,summary}.json.

Usage:
    uv run python scripts/micro/train_arm0.py --mode td --steps 2500
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
from micro_ternary import (
    anneal_all,
    build_ternary_micro,
    flip_summary_all,
    observe_all,
    ternary_stats_all,
)
from ternary_st import TernaryConfig
from train_micro import (
    CompileDataLoader,
    load_compile_examples,
    tokenize_examples,
)

CANON = "data/compile-train.canonical.jsonl"
EVAL = "data/compile-eval.jsonl"


# ══════════════════════════════════════════════════════════════════════
# Provenance
# ══════════════════════════════════════════════════════════════════════


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


# ══════════════════════════════════════════════════════════════════════
# Per-category batches (for the sign-demand diagnostic)
# ══════════════════════════════════════════════════════════════════════


def per_example_batches(
    examples: list[dict],
    tokenizer,
    cfg: MicroConfig,
) -> list[tuple[str, mx.array, mx.array]]:
    """One (category, input_ids, targets) per example — batch dim 1.

    Per-example gradients are the atoms of the ANOVA: the FFN gradient comes
    only from the CE term (crystal/parity losses touch embeddings, not FFN),
    so each is a clean per-input signal.
    """
    out: list[tuple[str, mx.array, mx.array]] = []
    for ex in examples:
        seq = tokenize_examples([ex], tokenizer, cfg.max_seq_len, cfg.eod_id)[0]
        if len(seq) < 2:
            continue
        inp = mx.array(seq[:-1].reshape(1, -1))
        tgt = mx.array(seq[1:].reshape(1, -1))
        out.append((ex["category"], inp, tgt))
    return out


def anova_overloading(
    model,
    mods,
    examples: list[dict],
    tokenizer,
    cfg: MicroConfig,
    loss_and_grad_fn,
    seed: int,
) -> dict:
    """Magnitude-INVARIANT overloading test: per-weight ANOVA F-ratio.

    For each ternary FFN weight, treat the per-example gradient it receives as
    a sample and the input CATEGORY as the grouping factor. Genuine overloading
    = the gradient a weight wants depends on the category (signs cluster by
    category) → between-category variance ≫ within-category variance → F ≫ 1.
    F is a variance RATIO, so gradient magnitude cancels — the confound that
    sank the previous diagnostic.

    Both real labels and a SHUFFLED-LABEL null are accumulated in ONE pass
    (totals are label-independent; only the per-category sums differ). Under
    the null F ≈ 1 by construction. The headline: do high-F (category-driven)
    weights oscillate more than the null says they should?
    """
    per_ex = per_example_batches(examples, tokenizer, cfg)
    cats = sorted({c for c, _, _ in per_ex})
    cidx = {c: i for i, c in enumerate(cats)}
    real_lab = np.array([cidx[c] for c, _, _ in per_ex])
    shuf_lab = real_lab.copy()
    np.random.RandomState(seed + 7).shuffle(shuf_lab)
    n_total = len(per_ex)
    C = len(cats)

    def _dig(tree, li, name):
        return tree["blocks"][li]["ffn"][name]["weight"]

    # Per-module accumulators: totals + per-category sums (real & shuffled).
    acc: dict[str, dict] = {}
    for path, _m in mods:
        shp = _m.weight.shape
        acc[path] = {
            "sum": np.zeros(shp, np.float64),
            "sq": np.zeros(shp, np.float64),
            "cs_real": np.zeros((C, *shp), np.float64),
            "cs_shuf": np.zeros((C, *shp), np.float64),
        }
    n_real = np.zeros(C, np.int64)
    n_shuf = np.zeros(C, np.int64)

    for e, (_, inp, tgt) in enumerate(per_ex):
        _, grads = loss_and_grad_fn(model, inp, tgt)
        cr, cs = int(real_lab[e]), int(shuf_lab[e])
        n_real[cr] += 1
        n_shuf[cs] += 1
        for path, _m in mods:
            _, li_s, _f, name = path.split(".")
            g = np.array(_dig(grads, int(li_s), name), dtype=np.float64)
            a = acc[path]
            a["sum"] += g
            a["sq"] += g * g
            a["cs_real"][cr] += g
            a["cs_shuf"][cs] += g

    def _f_ratio(a, cs, counts):
        # SS_between = sum_c S_c^2/n_c - grand ; SS_within = SS_total - SS_between
        gt = a["sum"]
        grand = (gt * gt) / n_total
        nz = counts > 0
        ss_between = np.zeros_like(gt)
        for c in range(C):
            if nz[c]:
                ss_between += (cs[c] * cs[c]) / counts[c]
        ss_between -= grand
        ss_total = a["sq"] - grand
        ss_within = np.maximum(ss_total - ss_between, 0.0)
        df_b = max(1, C - 1)
        df_w = max(1, n_total - C)
        return (ss_between / df_b) / (ss_within / df_w + 1e-12)

    out: dict[str, dict] = {}
    for path, mod in mods:
        a = acc[path]
        f_real = _f_ratio(a, a["cs_real"], n_real).reshape(-1)
        f_shuf = _f_ratio(a, a["cs_shuf"], n_shuf).reshape(-1)
        fl = np.array(mod._flip_count).reshape(-1).astype(np.float64)

        # Do high-F weights oscillate more? Top-decile-F mean flips / overall.
        def _enrich(fvals, flips):
            k = max(1, fvals.size // 10)
            top = np.argpartition(fvals, -k)[-k:]
            overall = flips.mean() + 1e-12
            return float(flips[top].mean() / overall)

        out[path] = {
            "mean_F_real": float(f_real.mean()),
            "mean_F_null": float(f_shuf.mean()),
            "frac_F_real_gt2": float((f_real > 2.0).mean()),
            "frac_F_null_gt2": float((f_shuf > 2.0).mean()),
            "flip_enrichment_topF_real": _enrich(f_real, fl),
            "flip_enrichment_topF_null": _enrich(f_shuf, fl),
        }
    return {"categories": cats, "n_examples": n_total, "per_module": out}


# ══════════════════════════════════════════════════════════════════════
# Train
# ══════════════════════════════════════════════════════════════════════


def run(mode: str, steps: int, seed: int, out_root: Path) -> dict:
    mx.random.seed(seed)
    np.random.seed(seed)

    cfg = MicroConfig(total_steps=steps, checkpoint_dir="checkpoints/arm0")

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")

    train_examples = load_compile_examples(CANON)
    train_seqs = tokenize_examples(
        train_examples, tokenizer, cfg.max_seq_len, cfg.eod_id
    )
    loader = CompileDataLoader(train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id)

    tcfg = TernaryConfig(mode=mode if mode != "none" else "st")
    model, mods = build_ternary_micro(cfg, mode=mode, tcfg=tcfg)
    print(f"[arm0] mode={mode} ternary_mods={len(mods)} steps={steps}")



    lr_sched = optim.cosine_decay(cfg.lr, steps, cfg.lr * 0.01)
    warm = optim.linear_schedule(1e-7, cfg.lr, cfg.warmup_steps)

    def lr_fn(s):
        return warm(s) if s < cfg.warmup_steps else lr_sched(s)

    opt = optim.AdamW(learning_rate=lr_fn, weight_decay=cfg.weight_decay)

    def loss_fn(m, inp, tgt):
        _, loss = m(inp, tgt)
        return loss

    lag = nn.value_and_grad(model, loss_fn)

    ce_curve: list[tuple[int, float]] = []
    flip_curve: list[tuple[int, float]] = []
    t0 = time.time()

    for step in range(1, steps + 1):
        model._training_step = step
        anneal_all(mods, step, steps)

        inp, tgt = loader.next_batch()
        inp, tgt = mx.array(inp), mx.array(tgt)
        lv, grads = lag(model, inp, tgt)
        grads, gnorm = optim.clip_grad_norm(grads, cfg.grad_clip)
        opt.update(model, grads)
        mx.eval(model.parameters(), opt.state, lv)

        snap = observe_all(mods) if mods else {}

        if step % 100 == 0 or step == 1:
            ce = float(model._last_ce_loss.item())
            flipped = snap.get("flipped_this_step", 0.0)
            ce_curve.append((step, ce))
            flip_curve.append((step, flipped))
            print(
                f"step {step:5d} | CE {ce:.4f} | flip/step {flipped:.4f} | "
                f"sparsity {snap.get('frac_zero', 0.0):.3f} | "
                f"gnorm {float(gnorm.item()):.2f} | {time.time()-t0:.0f}s"
            )

    # ── End-of-run diagnostics ──
    summary: dict = {
        "mode": mode,
        "steps": steps,
        "seed": seed,
        "final_ce": ce_curve[-1][1] if ce_curve else None,
        "ce_curve": ce_curve,
        "flip_curve": flip_curve,
    }
    if mods:
        summary["flip_summary"] = flip_summary_all(mods)
        summary["ternary_stats"] = ternary_stats_all(mods)
        print("[arm0] running ANOVA F-ratio overloading diagnostic...")
        summary["overloading"] = anova_overloading(
            model, mods, train_examples, tokenizer, cfg, lag, seed
        )
        pm = summary["overloading"]["per_module"].values()
        summary["headline"] = {
            "mean_F_real": float(np.mean([m["mean_F_real"] for m in pm])),
            "mean_F_null": float(np.mean([m["mean_F_null"] for m in pm])),
            "flip_enrichment_topF_real": float(
                np.mean([m["flip_enrichment_topF_real"] for m in pm])
            ),
            "flip_enrichment_topF_null": float(
                np.mean([m["flip_enrichment_topF_null"] for m in pm])
            ),
        }

    # ── Write record ──
    run_id = f"{mode}-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"
    out_dir = out_root / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "experiment": "micro-ternary-arm0",
        "mode": mode,
        "git_sha": _git_sha(),
        "mlx_version": getattr(mx, "__version__", "unknown"),
        "seed": seed,
        "config": {
            "d_model": cfg.d_model, "d_ff": cfg.d_ff, "n_layers": cfg.n_layers,
            "n_heads": cfg.n_heads, "steps": steps, "lr": cfg.lr,
            "ternary": {
                "mode": tcfg.mode, "sharpness_start": tcfg.sharpness_start,
                "sharpness_end": tcfg.sharpness_end,
                "anneal_frac": tcfg.anneal_frac,
                "delta_ratio_init": tcfg.delta_ratio_init,
                "learn_delta": tcfg.learn_delta,
            },
        },
        "data": {"train": CANON, "eval": EVAL},
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"[arm0] wrote {out_dir}")

    if "headline" in summary:
        h = summary["headline"]
        print("\n" + "=" * 60)
        print(f"HEADLINE (mode={mode}):")
        print(f"  final CE: {summary['final_ce']:.4f}")
        print(f"  mean F (category structure): {h['mean_F_real']:.3f}  "
              f"(null {h['mean_F_null']:.3f})")
        print(f"  flip enrichment top-F weights: "
              f"{h['flip_enrichment_topF_real']:.3f}  "
              f"(null {h['flip_enrichment_topF_null']:.3f})")
        print("=" * 60)
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["td", "st", "none"], default="td")
    ap.add_argument("--steps", type=int, default=2500)
    ap.add_argument("--seed", type=int, default=261)
    ap.add_argument("--out", default="results/micro-ternary-arm0")
    args = ap.parse_args()
    run(args.mode, args.steps, args.seed, Path(args.out))


if __name__ == "__main__":
    main()
