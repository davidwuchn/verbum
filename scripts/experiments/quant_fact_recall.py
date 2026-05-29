"""Quantization Fact Recall — Find the bit-width cliff.

Q4 works. Ternary doesn't. Where's the cliff? What information
is lost between 4 bits and 1.58 bits?

Tests progressive quantization: float32 → Q8 → Q4 → Q3 → Q2 → ternary
using uniform per-channel quantization (group-wise with configurable
group size).

Also tests: ternary + per-group scale factors (effectively adding a
few calibration bits back to ternary).

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/quant_fact_recall.py
    uv run python scripts/experiments/quant_fact_recall.py --model Qwen/Qwen3-4B

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import math
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
    data = json.load(open(PROBES_FILE))
    return data["probes"]


def run_probes(model, tokenizer, probes, device, label="baseline"):
    results = []
    model.eval()
    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(input_ids)
            logits = outputs.logits[0, -1, :]

        probs = torch.softmax(logits, dim=-1)
        top_probs, top_ids = torch.topk(probs, 5)

        expected = probe["expected"]
        expected_id = tokenizer.encode(expected, add_special_tokens=False)
        expected_first_id = expected_id[0] if expected_id else -1

        top1_correct = top_ids[0].item() == expected_first_id
        top5_correct = any(top_ids[j].item() == expected_first_id for j in range(5))

        expected_rank = None
        expected_logprob = None
        if expected_first_id >= 0:
            ep = probs[expected_first_id].item()
            expected_logprob = math.log(ep) if ep > 0 else -float("inf")
            expected_rank = (probs > probs[expected_first_id]).sum().item() + 1

        results.append({
            "id": probe["id"],
            "category": probe["category"],
            "expected": expected,
            "top1_token": tokenizer.decode([top_ids[0].item()]),
            "top1_correct": top1_correct,
            "top5_correct": top5_correct,
            "expected_logprob": expected_logprob,
            "expected_rank": expected_rank,
            "label": label,
        })
    return results


def quantize_to_nbits(model, n_bits: int, group_size: int = 128,
                      ffn_only: bool = True) -> dict:
    """Quantize linear weights to n_bits using per-group symmetric quantization.

    For n_bits=2: 4 levels  (-1.5, -0.5, 0.5, 1.5) * scale
    For n_bits=1: ternary   (-1, 0, 1) * scale  (special case)

    Returns stats dict.
    """
    stats = {"total_params": 0, "quantized_params": 0, "n_bits": n_bits,
             "group_size": group_size}
    ffn_names = ("gate_proj", "up_proj", "down_proj")

    for name, param in model.named_parameters():
        stats["total_params"] += param.numel()

        if param.dim() < 2:
            continue
        if "norm" in name or "embed" in name or "lm_head" in name:
            continue
        if ffn_only and not any(fn in name for fn in ffn_names):
            continue

        stats["quantized_params"] += param.numel()

        with torch.no_grad():
            w = param.data.float()
            orig_shape = w.shape

            # Reshape for group quantization
            # Flatten to 2D, then split into groups along last dim
            w_flat = w.reshape(-1, orig_shape[-1])
            n_rows, n_cols = w_flat.shape

            if group_size > 0 and group_size < n_cols:
                # Pad if needed
                n_groups = (n_cols + group_size - 1) // group_size
                padded = n_groups * group_size
                if padded > n_cols:
                    w_flat = torch.nn.functional.pad(w_flat, (0, padded - n_cols))
                w_grouped = w_flat.reshape(n_rows, n_groups, group_size)
            else:
                # Per-row quantization
                w_grouped = w_flat.unsqueeze(1)  # (rows, 1, cols)
                group_size = n_cols

            if n_bits == 0:
                # Special: ternary with per-group scale
                # Levels: -1, 0, +1
                # Scale = mean(|w|) per group (for non-zero elements)
                scales = w_grouped.abs().mean(dim=-1, keepdim=True).clamp(min=1e-8)
                # Threshold for zeros: below 0.5 * scale
                threshold = 0.5 * scales
                q = torch.sign(w_grouped)
                q[w_grouped.abs() < threshold] = 0.0
                w_q = q * scales
            else:
                # Symmetric uniform quantization to n_bits
                n_levels = 2 ** n_bits
                qmax = n_levels // 2 - 1  # e.g., Q4: qmax=7
                qmin = -qmax - 1          # e.g., Q4: qmin=-8

                # Per-group scale: max(|w|) / qmax
                amax = w_grouped.abs().amax(dim=-1, keepdim=True).clamp(min=1e-8)
                scale = amax / qmax

                # Quantize
                q = (w_grouped / scale).round().clamp(qmin, qmax)

                # Dequantize
                w_q = q * scale

            # Reshape back
            w_q = w_q.reshape(n_rows, -1)[:, :n_cols].reshape(orig_shape)
            param.data.copy_(w_q.to(param.dtype))

    return stats


def summarize(results, label):
    fact_cats = {"capital", "creator", "science", "history", "geography"}
    compute_cats = {"computation", "arithmetic"}

    by_cat = defaultdict(lambda: {"total": 0, "top1": 0, "top5": 0,
                                  "logprobs": [], "ranks": []})
    for r in results:
        cat = r["category"]
        by_cat[cat]["total"] += 1
        if r["top1_correct"]:
            by_cat[cat]["top1"] += 1
        if r["top5_correct"]:
            by_cat[cat]["top5"] += 1
        if r["expected_logprob"] is not None:
            by_cat[cat]["logprobs"].append(r["expected_logprob"])
        if r["expected_rank"] is not None:
            by_cat[cat]["ranks"].append(r["expected_rank"])

    fact_correct = sum(1 for r in results if r["category"] in fact_cats and r["top1_correct"])
    fact_total = sum(1 for r in results if r["category"] in fact_cats)
    comp_correct = sum(1 for r in results if r["category"] in compute_cats and r["top1_correct"])
    comp_total = sum(1 for r in results if r["category"] in compute_cats)
    total_correct = sum(1 for r in results if r["top1_correct"])
    total = len(results)

    avg_rank_facts = []
    avg_rank_comp = []
    for r in results:
        if r["expected_rank"] is not None:
            if r["category"] in fact_cats:
                avg_rank_facts.append(r["expected_rank"])
            elif r["category"] in compute_cats:
                avg_rank_comp.append(r["expected_rank"])

    return {
        "label": label,
        "overall_acc": total_correct / total if total > 0 else 0,
        "fact_acc": fact_correct / fact_total if fact_total > 0 else 0,
        "compute_acc": comp_correct / comp_total if comp_total > 0 else 0,
        "fact_n": f"{fact_correct}/{fact_total}",
        "compute_n": f"{comp_correct}/{comp_total}",
        "avg_fact_rank": sum(avg_rank_facts) / len(avg_rank_facts) if avg_rank_facts else -1,
        "avg_compute_rank": sum(avg_rank_comp) / len(avg_rank_comp) if avg_rank_comp else -1,
        "by_category": {
            cat: {
                "top1_acc": d["top1"] / d["total"],
                "avg_rank": sum(d["ranks"]) / len(d["ranks"]) if d["ranks"] else -1,
                "avg_logprob": sum(d["logprobs"]) / len(d["logprobs"]) if d["logprobs"] else float("-inf"),
            }
            for cat, d in sorted(by_cat.items())
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--dtype", default="float32")
    parser.add_argument("--group-size", type=int, default=128,
                        help="Group size for quantization (0=per-row)")
    parser.add_argument("--ffn-only", action="store_true", default=True)
    parser.add_argument("--all-weights", action="store_true")
    args = parser.parse_args()

    dtype_map = {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}
    dtype = dtype_map[args.dtype]
    ffn_only = not args.all_weights

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    probes = load_probes()
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    log(f"=== Quantization Fact Recall — Finding the Cliff ===")
    log(f"Model: {args.model}  Device: {args.device}  Group size: {args.group_size}")
    log(f"Quantize: {'FFN only' if ffn_only else 'all weights'}")
    log(f"Probes: {len(probes)}")

    all_summaries = []
    all_results = {}

    # Bit widths to test: 8, 4, 3, 2, 1 (binary), 0 (ternary w/ scale)
    # n_bits=0 is special ternary-with-group-scale
    bit_configs = [
        ("float32", None),     # baseline
        ("Q8", 8),
        ("Q4", 4),
        ("Q3", 3),
        ("Q2", 2),
        ("Q1", 1),            # binary: {-1, +1} * scale (2 levels)
        ("ternary_gs", 0),    # ternary w/ per-group scale: {-1, 0, +1} * scale
    ]

    for label, n_bits in bit_configs:
        log(f"\n{'='*60}")
        log(f"--- {label} ---")

        # Load fresh model
        if label != "float32" and 'model' in dir():
            del model
            gc.collect()
            if args.device == "mps":
                torch.mps.empty_cache()

        model = AutoModelForCausalLM.from_pretrained(
            args.model, torch_dtype=dtype, device_map=args.device, trust_remote_code=True)

        if n_bits is not None:
            t0 = time.time()
            stats = quantize_to_nbits(model, n_bits, args.group_size, ffn_only)
            log(f"Quantized to {label} in {time.time()-t0:.1f}s  "
                f"({stats['quantized_params']:,} params)")

        t0 = time.time()
        results = run_probes(model, tokenizer, probes, args.device, label)
        log(f"Probes: {time.time()-t0:.1f}s")

        s = summarize(results, label)
        all_summaries.append(s)
        all_results[label] = results

        log(f"  Facts: {s['fact_acc']:.1%} ({s['fact_n']})  avg_rank={s['avg_fact_rank']:.1f}")
        log(f"  Compute: {s['compute_acc']:.1%} ({s['compute_n']})  avg_rank={s['avg_compute_rank']:.1f}")
        log(f"  Overall: {s['overall_acc']:.1%}")

    # Final comparison table
    log(f"\n{'='*80}")
    log(f"{'Bits':>12s} | {'Facts':>8s} | {'Compute':>8s} | {'Overall':>8s} | {'Fact Rank':>10s} | {'Comp Rank':>10s}")
    log(f"{'-'*80}")
    for s in all_summaries:
        log(f"{s['label']:>12s} | {s['fact_acc']:7.1%}  | {s['compute_acc']:7.1%}  | {s['overall_acc']:7.1%}  | "
            f"{s['avg_fact_rank']:9.1f}  | {s['avg_compute_rank']:9.1f}")
    log(f"{'='*80}")

    # Per-category detail
    log(f"\n--- Per-category top1 accuracy ---")
    cats = list(all_summaries[0]["by_category"].keys())
    header = f"{'Bits':>12s} | " + " | ".join(f"{c:>10s}" for c in cats)
    log(header)
    log("-" * len(header))
    for s in all_summaries:
        row = f"{s['label']:>12s} | "
        row += " | ".join(f"{s['by_category'][c]['top1_acc']:9.1%} " for c in cats)
        log(row)

    # Save
    model_slug = args.model.replace("/", "_")
    output_file = RESULTS_DIR / f"{model_slug}_quant_cliff.json"
    output = {
        "model": args.model, "group_size": args.group_size,
        "ffn_only": ffn_only,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summaries": all_summaries,
    }
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)
    log(f"\nSaved to {output_file}")


if __name__ == "__main__":
    main()
