"""Ternary Fact Recall Experiment — Do facts survive ternarization?

Tests whether ternary weight quantization (sign + zeros) preserves
factual knowledge stored in FFN layers. The hypothesis: computation
(strong interference fringes) survives, but facts (weak distributed
fringes) may not.

Architecture:
  1. Load model (default: Qwen3-0.6B for fast iteration)
  2. Run factual recall probes → record predictions
  3. Ternarize FFN weights at multiple zero thresholds
  4. Re-run probes → compare predictions
  5. Report: what survived, what died, by category

Ternarization schemes:
  - sign(W): pure ternary {-1, 0, +1}, zeros where |W| < threshold
  - Threshold by percentile of |W| per-layer: 0%, 10%, 30%, 50%
  - FFN-only vs all-weights variants

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/ternary_fact_recall.py
    uv run python scripts/experiments/ternary_fact_recall.py --model Qwen/Qwen3-4B
    uv run python scripts/experiments/ternary_fact_recall.py --model Qwen/Qwen3-8B

License: MIT
"""

from __future__ import annotations

import argparse
import copy
import gc
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PROBES_FILE = Path(__file__).parent.parent.parent / "probes" / "fact_recall.json"
RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "ternary-fact-recall"


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def load_probes() -> list[dict]:
    """Load probe set from JSON."""
    data = json.load(open(PROBES_FILE))
    return data["probes"]


def run_probes(
    model,
    tokenizer,
    probes: list[dict],
    device: str,
    label: str = "baseline",
) -> list[dict]:
    """Run all probes through model, return per-probe results."""
    results = []
    model.eval()

    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model(input_ids)
            logits = outputs.logits[0, -1, :]  # last token logits

        # Top-k predictions
        probs = torch.softmax(logits, dim=-1)
        top_k = 10
        top_probs, top_ids = torch.topk(probs, top_k)
        top_logprobs = torch.log(top_probs)

        top_tokens = []
        for j in range(top_k):
            tok_id = top_ids[j].item()
            tok_str = tokenizer.decode([tok_id])
            top_tokens.append({
                "token": tok_str,
                "token_id": tok_id,
                "prob": top_probs[j].item(),
                "logprob": top_logprobs[j].item(),
            })

        # Check expected answer
        expected = probe["expected"]
        expected_id = tokenizer.encode(expected, add_special_tokens=False)
        if expected_id:
            expected_first_id = expected_id[0]
        else:
            expected_first_id = -1

        top1_correct = top_tokens[0]["token_id"] == expected_first_id
        top5_correct = any(t["token_id"] == expected_first_id for t in top_tokens[:5])
        top10_correct = any(t["token_id"] == expected_first_id for t in top_tokens[:10])

        # Get expected token's rank and logprob
        expected_logprob = None
        expected_rank = None
        if expected_first_id >= 0:
            expected_prob_val = probs[expected_first_id].item()
            expected_logprob = torch.log(probs[expected_first_id]).item() if expected_prob_val > 0 else -float("inf")
            # Rank: how many tokens have higher probability?
            expected_rank = (probs > probs[expected_first_id]).sum().item() + 1

        results.append({
            "id": probe["id"],
            "category": probe["category"],
            "prompt": probe["prompt"][:80],
            "expected": expected,
            "expected_id": expected_first_id,
            "top1_token": top_tokens[0]["token"],
            "top1_correct": top1_correct,
            "top5_correct": top5_correct,
            "top10_correct": top10_correct,
            "top1_prob": top_tokens[0]["prob"],
            "top1_logprob": top_tokens[0]["logprob"],
            "expected_logprob": expected_logprob,
            "expected_rank": expected_rank,
            "top5": top_tokens[:5],
            "label": label,
        })

    return results


def ternarize_ffn_weights(model, zero_percentile: float = 0.0, scale: bool = True) -> dict:
    """Ternarize FFN (MLP) weights in-place. Returns stats.

    For SwiGLU: gate_proj, up_proj, down_proj get ternarized.
    Attention weights (q/k/v/o) left untouched.

    zero_percentile: what fraction of smallest-magnitude weights become 0.
                     0.0 = pure sign (no zeros), 0.3 = 30% zeros, etc.
    scale: if True, apply per-row gamma scaling (gamma = ||w_row|| / sqrt(d))
           so that the output magnitude is preserved. Without this, ternary
           outputs are ~30x too large and the model collapses.
    """
    stats = {"total_params": 0, "ternary_params": 0, "zeros": 0, "pos": 0, "neg": 0}
    ffn_names = ("gate_proj", "up_proj", "down_proj")

    for name, param in model.named_parameters():
        stats["total_params"] += param.numel()

        # Only ternarize FFN weights (not biases, not attention, not norms)
        if not any(fn in name for fn in ffn_names):
            continue
        if param.dim() < 2:
            continue

        stats["ternary_params"] += param.numel()

        with torch.no_grad():
            w = param.data
            abs_w = w.abs()

            # Compute per-row scaling factor BEFORE ternarizing
            if scale:
                row_norms = w.float().norm(dim=1)
                d_in = w.shape[1]

            # Compute threshold for zeros
            if zero_percentile > 0:
                threshold = torch.quantile(abs_w.float().flatten(), zero_percentile)
            else:
                threshold = 0.0

            # Ternarize: sign where |w| > threshold, else 0
            ternary = torch.sign(w)
            if zero_percentile > 0:
                ternary[abs_w <= threshold] = 0.0

            # Apply per-row scaling: gamma * sign(W)
            # gamma = ||w_row|| / sqrt(n_nonzero_per_row)
            # This preserves the expected output magnitude
            if scale:
                n_nonzero = (ternary != 0).float().sum(dim=1).clamp(min=1)
                gamma = row_norms / n_nonzero.sqrt()
                ternary = ternary * gamma.unsqueeze(1).to(ternary.dtype)

            zeros = (ternary == 0).sum().item()
            pos = (ternary > 0).sum().item()
            neg = (ternary < 0).sum().item()
            stats["zeros"] += zeros
            stats["pos"] += pos
            stats["neg"] += neg

            # Write back
            param.data.copy_(ternary)

    stats["zero_frac"] = stats["zeros"] / max(stats["ternary_params"], 1)
    stats["pos_frac"] = stats["pos"] / max(stats["ternary_params"], 1)
    stats["neg_frac"] = stats["neg"] / max(stats["ternary_params"], 1)
    stats["scaled"] = scale
    return stats


def ternarize_all_weights(model, zero_percentile: float = 0.0, scale: bool = True) -> dict:
    """Ternarize ALL linear weights in-place (FFN + attention). Returns stats."""
    stats = {"total_params": 0, "ternary_params": 0, "zeros": 0, "pos": 0, "neg": 0}

    for name, param in model.named_parameters():
        stats["total_params"] += param.numel()

        # Skip norms, biases, embeddings
        if param.dim() < 2:
            continue
        if "norm" in name or "embed" in name or "lm_head" in name:
            continue

        stats["ternary_params"] += param.numel()

        with torch.no_grad():
            w = param.data
            abs_w = w.abs()

            # Per-row scaling
            if scale:
                row_norms = w.float().norm(dim=1)

            if zero_percentile > 0:
                threshold = torch.quantile(abs_w.float().flatten(), zero_percentile)
            else:
                threshold = 0.0

            ternary = torch.sign(w)
            if zero_percentile > 0:
                ternary[abs_w <= threshold] = 0.0

            if scale:
                n_nonzero = (ternary != 0).float().sum(dim=1).clamp(min=1)
                gamma = row_norms / n_nonzero.sqrt()
                ternary = ternary * gamma.unsqueeze(1).to(ternary.dtype)

            stats["zeros"] += (ternary == 0).sum().item()
            stats["pos"] += (ternary > 0).sum().item()
            stats["neg"] += (ternary < 0).sum().item()

            param.data.copy_(ternary)

    stats["zero_frac"] = stats["zeros"] / max(stats["ternary_params"], 1)
    stats["scaled"] = scale
    return stats


def summarize_results(results: list[dict], label: str) -> dict:
    """Compute per-category and overall accuracy."""
    by_cat = defaultdict(lambda: {"total": 0, "top1": 0, "top5": 0, "top10": 0,
                                  "logprobs": [], "ranks": []})

    for r in results:
        cat = r["category"]
        by_cat[cat]["total"] += 1
        if r["top1_correct"]:
            by_cat[cat]["top1"] += 1
        if r["top5_correct"]:
            by_cat[cat]["top5"] += 1
        if r["top10_correct"]:
            by_cat[cat]["top10"] += 1
        if r["expected_logprob"] is not None:
            by_cat[cat]["logprobs"].append(r["expected_logprob"])
        if r["expected_rank"] is not None:
            by_cat[cat]["ranks"].append(r["expected_rank"])

    summary = {"label": label, "categories": {}}
    total_t1, total_t5, total_n = 0, 0, 0

    for cat in sorted(by_cat):
        d = by_cat[cat]
        avg_lp = sum(d["logprobs"]) / len(d["logprobs"]) if d["logprobs"] else float("-inf")
        med_rank = sorted(d["ranks"])[len(d["ranks"]) // 2] if d["ranks"] else -1
        avg_rank = sum(d["ranks"]) / len(d["ranks"]) if d["ranks"] else -1

        summary["categories"][cat] = {
            "n": d["total"],
            "top1_acc": d["top1"] / d["total"],
            "top5_acc": d["top5"] / d["total"],
            "top10_acc": d["top10"] / d["total"],
            "avg_logprob": round(avg_lp, 4),
            "avg_rank": round(avg_rank, 1),
            "median_rank": med_rank,
        }
        total_t1 += d["top1"]
        total_t5 += d["top5"]
        total_n += d["total"]

    summary["overall"] = {
        "n": total_n,
        "top1_acc": total_t1 / total_n if total_n > 0 else 0,
        "top5_acc": total_t5 / total_n if total_n > 0 else 0,
    }
    return summary


def print_comparison(baseline_summary: dict, ternary_summary: dict):
    """Print side-by-side comparison."""
    log("\n" + "=" * 80)
    log(f"{'Category':15s} | {'Baseline top1':>13s} | {'Ternary top1':>12s} | {'Δ':>6s} | {'Base rank':>9s} | {'Tern rank':>9s}")
    log("-" * 80)

    for cat in sorted(baseline_summary["categories"]):
        b = baseline_summary["categories"][cat]
        t = ternary_summary["categories"].get(cat, {"top1_acc": 0, "avg_rank": -1})
        delta = t["top1_acc"] - b["top1_acc"]
        log(f"{cat:15s} | {b['top1_acc']:12.1%}  | {t['top1_acc']:11.1%}  | {delta:+5.1%} | {b['avg_rank']:8.1f}  | {t['avg_rank']:8.1f}")

    b_all = baseline_summary["overall"]
    t_all = ternary_summary["overall"]
    delta_all = t_all["top1_acc"] - b_all["top1_acc"]
    log("-" * 80)
    log(f"{'OVERALL':15s} | {b_all['top1_acc']:12.1%}  | {t_all['top1_acc']:11.1%}  | {delta_all:+5.1%} |")
    log("=" * 80)


def print_probe_detail(baseline_results: list[dict], ternary_results: list[dict]):
    """Print per-probe comparison showing what survived and what died."""
    # Build lookup
    ternary_by_id = {r["id"]: r for r in ternary_results}

    survived = []
    died = []
    gained = []

    for b in baseline_results:
        t = ternary_by_id.get(b["id"])
        if not t:
            continue

        if b["top1_correct"] and t["top1_correct"]:
            survived.append((b, t))
        elif b["top1_correct"] and not t["top1_correct"]:
            died.append((b, t))
        elif not b["top1_correct"] and t["top1_correct"]:
            gained.append((b, t))

    if died:
        log(f"\n--- DIED ({len(died)} facts lost to ternarization) ---")
        for b, t in died:
            log(f"  {b['id']:10s} [{b['category']:12s}] expected={b['expected']!r:8s}  "
                f"base={b['top1_token']!r:8s}✓  tern={t['top1_token']!r:8s}✗  "
                f"rank: {b['expected_rank']}→{t['expected_rank']}")

    if survived:
        log(f"\n--- SURVIVED ({len(survived)} facts preserved) ---")
        for b, t in survived[:10]:
            lp_delta = (t["expected_logprob"] or 0) - (b["expected_logprob"] or 0)
            log(f"  {b['id']:10s} [{b['category']:12s}] {b['expected']!r:8s}  "
                f"logprob: {b['expected_logprob']:.2f}→{t['expected_logprob']:.2f} ({lp_delta:+.2f})")
        if len(survived) > 10:
            log(f"  ... and {len(survived) - 10} more")

    if gained:
        log(f"\n--- GAINED ({len(gained)} facts emerged from ternarization) ---")
        for b, t in gained:
            log(f"  {b['id']:10s} [{b['category']:12s}] expected={b['expected']!r:8s}  "
                f"base={b['top1_token']!r:8s}✗  tern={t['top1_token']!r:8s}✓")


def main():
    parser = argparse.ArgumentParser(description="Ternary Fact Recall Experiment")
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B", help="HuggingFace model name")
    parser.add_argument("--device", default="mps", help="Device (mps, cuda, cpu)")
    parser.add_argument("--zero-pcts", default="0.0,0.1,0.3,0.5",
                        help="Comma-separated zero percentiles to test")
    parser.add_argument("--ffn-only", action="store_true", default=True,
                        help="Only ternarize FFN weights (default)")
    parser.add_argument("--all-weights", action="store_true",
                        help="Ternarize all linear weights including attention")
    parser.add_argument("--dtype", default="float32", choices=["float16", "bfloat16", "float32"],
                        help="Model dtype")
    args = parser.parse_args()

    zero_pcts = [float(x) for x in args.zero_pcts.split(",")]
    dtype_map = {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}
    dtype = dtype_map[args.dtype]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log(f"=== Ternary Fact Recall Experiment ===")
    log(f"Model: {args.model}")
    log(f"Device: {args.device}")
    log(f"Dtype: {args.dtype}")
    log(f"Zero percentiles: {zero_pcts}")
    log(f"Ternarize: {'all weights' if args.all_weights else 'FFN only'}")

    # Load probes
    probes = load_probes()
    log(f"Loaded {len(probes)} probes")

    # Load tokenizer
    log("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Verify expected tokens can be encoded
    log("Verifying probe expected tokens...")
    for probe in probes:
        ids = tokenizer.encode(probe["expected"], add_special_tokens=False)
        if not ids:
            log(f"  WARNING: {probe['id']} expected={probe['expected']!r} encodes to empty!")

    all_results = {}

    # === BASELINE ===
    log("\n--- Loading model for baseline ---")
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=dtype,
        device_map=args.device,
        trust_remote_code=True,
    )
    # Disable thinking for Qwen3 models
    if hasattr(model, 'generation_config'):
        model.generation_config.do_sample = False
    log(f"Model loaded in {time.time() - t0:.1f}s")

    # Count params
    total_params = sum(p.numel() for p in model.parameters())
    log(f"Total parameters: {total_params:,}")

    log("\n--- Running baseline probes ---")
    t0 = time.time()
    baseline_results = run_probes(model, tokenizer, probes, args.device, "baseline")
    log(f"Baseline probes: {time.time() - t0:.1f}s")

    baseline_summary = summarize_results(baseline_results, "baseline")
    all_results["baseline"] = {
        "summary": baseline_summary,
        "probes": baseline_results,
    }

    log("\n--- Baseline Results ---")
    for cat, s in sorted(baseline_summary["categories"].items()):
        log(f"  {cat:15s}  top1={s['top1_acc']:.1%}  top5={s['top5_acc']:.1%}  avg_rank={s['avg_rank']:.1f}")
    log(f"  {'OVERALL':15s}  top1={baseline_summary['overall']['top1_acc']:.1%}")

    # === TERNARY RUNS ===
    for zero_pct in zero_pcts:
        label = f"ternary_z{int(zero_pct * 100):02d}"
        ternarize_mode = "all" if args.all_weights else "ffn"
        label_full = f"{label}_{ternarize_mode}"

        log(f"\n{'='*60}")
        log(f"--- Ternarizing: {label_full} (zero_pct={zero_pct:.0%}) ---")

        # Reload model fresh each time
        del model
        gc.collect()
        if args.device == "mps":
            torch.mps.empty_cache()
        elif args.device == "cuda":
            torch.cuda.empty_cache()

        model = AutoModelForCausalLM.from_pretrained(
            args.model,
            torch_dtype=dtype,
            device_map=args.device,
            trust_remote_code=True,
        )

        # Ternarize
        t0 = time.time()
        if args.all_weights:
            tern_stats = ternarize_all_weights(model, zero_pct)
        else:
            tern_stats = ternarize_ffn_weights(model, zero_pct)
        log(f"Ternarized in {time.time() - t0:.1f}s")
        log(f"  Ternary params: {tern_stats['ternary_params']:,} / {tern_stats['total_params']:,} "
            f"({tern_stats['ternary_params']/tern_stats['total_params']:.1%})")
        log(f"  Zeros: {tern_stats['zero_frac']:.1%}  +1: {tern_stats['pos_frac']:.1%}  -1: {tern_stats['neg_frac']:.1%}")

        # Run probes
        t0 = time.time()
        ternary_results = run_probes(model, tokenizer, probes, args.device, label_full)
        log(f"Probes: {time.time() - t0:.1f}s")

        ternary_summary = summarize_results(ternary_results, label_full)

        # Compare
        print_comparison(baseline_summary, ternary_summary)
        print_probe_detail(baseline_results, ternary_results)

        all_results[label_full] = {
            "summary": ternary_summary,
            "stats": tern_stats,
            "probes": ternary_results,
        }

    # === SAVE ===
    model_slug = args.model.replace("/", "_")
    output_file = RESULTS_DIR / f"{model_slug}.json"

    output = {
        "model": args.model,
        "dtype": args.dtype,
        "device": args.device,
        "ternarize_mode": "all" if args.all_weights else "ffn",
        "zero_percentiles": zero_pcts,
        "n_probes": len(probes),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": all_results,
    }

    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)
    log(f"\nResults saved to {output_file}")

    # === FINAL SUMMARY ===
    log("\n" + "=" * 80)
    log("FINAL SUMMARY")
    log("=" * 80)

    # Fact categories vs computation categories
    fact_cats = {"capital", "creator", "science", "history", "geography"}
    compute_cats = {"computation", "arithmetic"}

    for label, data in all_results.items():
        s = data["summary"]
        fact_correct = sum(1 for r in data["probes"] if r["category"] in fact_cats and r["top1_correct"])
        fact_total = sum(1 for r in data["probes"] if r["category"] in fact_cats)
        comp_correct = sum(1 for r in data["probes"] if r["category"] in compute_cats and r["top1_correct"])
        comp_total = sum(1 for r in data["probes"] if r["category"] in compute_cats)

        fact_acc = fact_correct / fact_total if fact_total > 0 else 0
        comp_acc = comp_correct / comp_total if comp_total > 0 else 0

        log(f"{label:30s}  facts={fact_acc:.1%} ({fact_correct}/{fact_total})  "
            f"compute={comp_acc:.1%} ({comp_correct}/{comp_total})  "
            f"overall={s['overall']['top1_acc']:.1%}")

    log("\nKey question: do facts die faster than computation under ternarization?")


if __name__ == "__main__":
    main()
