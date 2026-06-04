#!/usr/bin/env python3
"""MTP Self-Speculation: Can the model's own intermediate layers predict future tokens?

HYPOTHESIS: The FFN at L26-L30 already compiles multi-position semantic
predictions. Position N's residual at L30 contains information about what
tokens N+1, N+2, N+3 should be. This enables "self-speculative decoding"
— the early layers draft, the late layers verify — without a second model.

MEASUREMENTS:
  1. For each position N at each layer L (L20-L35):
     - Project residual[L][N] through final_norm + unembed → top-k predictions
     - Hit@k: does actual token at N+1 appear in top-k? (k=1,5,10,50,100)
     - Lookahead: same for N+2, N+3
     - Rank: what's the rank of the actual N+1 token?

  2. FFN delta vs cumulative:
     - delta[L][N] = residual[L][N] - residual[L-1][N]  (what this layer ADDED)
     - Does the delta predict future tokens better than cumulative?

  3. Theoretical acceptance rate:
     - If we draft from L30 and verify at L35, what fraction match?
     - Speculative speedup = tokens_accepted / tokens_drafted

  4. Layer-optimal early exit:
     - At which layer does future-token prediction peak?
     - Is there a layer where we can stop and already have multi-token answers?

Usage:
  uv run python scripts/experiments/mtp_self_speculation.py
  uv run python scripts/experiments/mtp_self_speculation.py --layers 24,26,28,30,32,33,35

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time

os.environ.setdefault("PYTHONUNBUFFERED", "1")

import numpy as np
import torch

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


def run_experiment(
    model_id: str = "Qwen/Qwen3-8B",
    layer_indices: list[int] | None = None,
    top_ks: list[int] | None = None,
    lookaheads: list[int] | None = None,
):
    log("=" * 72)
    log("MTP SELF-SPECULATION")
    log("=" * 72)
    log(f"Model: {model_id}")
    log()

    from transformers import AutoModelForCausalLM, AutoTokenizer

    if layer_indices is None:
        layer_indices = list(range(0, 36, 3)) + [33, 35]
        layer_indices = sorted(set(layer_indices))
    if top_ks is None:
        top_ks = [1, 5, 10, 50, 100]
    if lookaheads is None:
        lookaheads = [1, 2, 3, 4, 5]

    log(f"  Layers: {layer_indices}")
    log(f"  Top-k values: {top_ks}")
    log(f"  Lookaheads: {lookaheads}")

    # ── Probes: mix of short and longer text ────────────────────
    probes = [
        # Short (from existing set)
        "The dog runs quickly across the park and jumps over the fence.",
        "Every student reads a book about history before the exam begins.",
        "If it rains tomorrow, the ground will be wet and the flowers will grow.",
        "Someone believes that the earth is flat, but scientists disagree strongly.",
        "The cat that sat on the mat is black and white with green eyes.",
        # Longer / more complex
        "The professor explained that quantum mechanics describes the behavior of particles at very small scales, which contradicts our everyday intuition about how objects move and interact.",
        "After finishing the marathon in record time, the runner collapsed on the ground, breathing heavily while the crowd cheered and photographers captured the moment.",
        "In order to understand why birds migrate south for the winter, researchers have studied the genetic and environmental factors that influence seasonal movement patterns across continents.",
        "The ancient library contained thousands of scrolls written in languages that no living person could read, preserving knowledge from civilizations that had been forgotten for centuries.",
        "She told him that she would never forget the day they met at the coffee shop on the corner of Fifth Avenue and Broadway in the middle of a thunderstorm.",
    ]

    # ── Load model ──────────────────────────────────────────────
    log("\nLoading model...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="mps",
        low_cpu_mem_usage=True,
    )
    model.eval()
    log(f"  Loaded in {time.time() - t0:.1f}s")

    config = model.config
    n_layers = config.num_hidden_layers

    # ── Get final norm + unembed for proper logit computation ───
    # The model applies final norm before the lm_head
    final_norm = model.model.norm
    lm_head = model.lm_head
    log(f"  {n_layers} layers, final_norm + lm_head ready")

    # ── Process each probe ──────────────────────────────────────
    all_results = []

    for probe_idx, probe in enumerate(probes):
        log(f"\n{'─' * 60}")
        log(f"PROBE {probe_idx + 1}/{len(probes)}: {probe[:70]}...")

        inputs = tokenizer(probe, return_tensors="pt")
        input_ids = inputs["input_ids"].to(model.device)
        seq_len = input_ids.shape[1]
        tokens = [tokenizer.decode(t) for t in input_ids[0]]
        log(f"  Tokens ({seq_len}): {' '.join(t.strip() for t in tokens[:20])}...")

        # ── Hook layers to capture residuals ────────────────────
        residuals = {}
        hooks = []

        for li in layer_indices:
            if li >= n_layers:
                continue
            layer = model.model.layers[li]
            def make_hook(layer_idx):
                def hook_fn(module, args, output):
                    if isinstance(output, tuple):
                        h = output[0]
                    else:
                        h = output
                    residuals[layer_idx] = h[0].cpu().float()
                    return output
                return hook_fn
            h = layer.register_forward_hook(make_hook(li))
            hooks.append(h)

        with torch.no_grad():
            outputs = model(input_ids, return_dict=True)

        for h in hooks:
            h.remove()

        # Get the final output logits for ground truth
        final_logits = outputs.logits[0].cpu().float()  # (seq_len, vocab)
        final_predictions = final_logits.argmax(dim=-1)  # (seq_len,)

        # ── Measure hit rates at each layer ─────────────────────
        probe_result = {
            "probe": probe,
            "tokens": tokens,
            "seq_len": seq_len,
            "layers": {},
        }

        for li in sorted(residuals.keys()):
            res = residuals[li]  # (seq_len, hidden)

            # Project through final_norm + lm_head for proper logits
            with torch.no_grad():
                res_device = res.to(model.device).half()
                normed = final_norm(res_device)
                logits = lm_head(normed).cpu().float()  # (seq_len, vocab)

            layer_result = {
                "layer": li,
                "lookahead_hits": {la: {k: 0 for k in top_ks} for la in lookaheads},
                "lookahead_counts": {la: 0 for la in lookaheads},
                "lookahead_ranks": {la: [] for la in lookaheads},
                "final_match": 0,  # how often L[li] top-1 matches L[35] top-1
                "final_match_count": 0,
                "position_details": [],  # per-position for first probe only
            }

            for pos in range(seq_len):
                pos_logits = logits[pos]  # (vocab,)

                for la in lookaheads:
                    future_pos = pos + la
                    if future_pos >= seq_len:
                        continue

                    actual_token = input_ids[0, future_pos].item()
                    layer_result["lookahead_counts"][la] += 1

                    # Rank of actual future token
                    sorted_indices = pos_logits.argsort(descending=True)
                    rank = (sorted_indices == actual_token).nonzero(as_tuple=True)[0]
                    if len(rank) > 0:
                        rank_val = rank[0].item()
                        layer_result["lookahead_ranks"][la].append(rank_val)

                        # Hit@k
                        for k in top_ks:
                            if rank_val < k:
                                layer_result["lookahead_hits"][la][k] += 1

                # Does this layer's top-1 match the final layer's top-1?
                if pos < seq_len - 1:
                    layer_top1 = logits[pos].argmax().item()
                    final_top1 = final_predictions[pos].item()
                    layer_result["final_match_count"] += 1
                    if layer_top1 == final_top1:
                        layer_result["final_match"] += 1

                # Per-position details for first probe
                if probe_idx == 0 and pos < seq_len - 1:
                    actual_next = input_ids[0, pos + 1].item()
                    actual_next_tok = tokenizer.decode(actual_next).strip()
                    pred_top3 = logits[pos].topk(3)
                    pred_tokens = [tokenizer.decode(t.item()).strip() for t in pred_top3.indices]
                    rank_of_next = (logits[pos].argsort(descending=True) == actual_next).nonzero(as_tuple=True)[0]
                    rank_val = rank_of_next[0].item() if len(rank_of_next) > 0 else -1

                    layer_result["position_details"].append({
                        "pos": pos,
                        "token": tokens[pos],
                        "actual_next": actual_next_tok,
                        "predicted_top3": pred_tokens,
                        "rank_of_actual": rank_val,
                    })

            probe_result["layers"][li] = layer_result

        all_results.append(probe_result)

    # ── Aggregate analysis ──────────────────────────────────────
    log(f"\n{'=' * 72}")
    log("HIT RATES: Can layer L predict the token at position N+lookahead?")
    log("=" * 72)

    for la in lookaheads:
        log(f"\n  Lookahead = {la} (predicting N+{la} from position N):")
        log(f"  {'Layer':>6s}", end="")
        for k in top_ks:
            log(f"  Hit@{k:<4d}", end="")
        log(f"  {'MedRank':>8s}  {'L35match':>8s}")

        for li in sorted(layer_indices):
            if li >= n_layers:
                continue
            total_hits = {k: 0 for k in top_ks}
            total_count = 0
            all_ranks = []
            final_matches = 0
            final_match_count = 0

            for result in all_results:
                if li not in result["layers"]:
                    continue
                lr = result["layers"][li]
                total_count += lr["lookahead_counts"].get(la, 0)
                for k in top_ks:
                    total_hits[k] += lr["lookahead_hits"].get(la, {}).get(k, 0)
                all_ranks.extend(lr["lookahead_ranks"].get(la, []))
                final_matches += lr.get("final_match", 0)
                final_match_count += lr.get("final_match_count", 0)

            if total_count == 0:
                continue

            log(f"  L{li:2d}   ", end="")
            for k in top_ks:
                rate = total_hits[k] / total_count * 100
                log(f"  {rate:6.1f}%", end="")
            med_rank = np.median(all_ranks) if all_ranks else -1
            final_rate = final_matches / final_match_count * 100 if final_match_count > 0 else 0
            log(f"  {med_rank:8.0f}  {final_rate:7.1f}%")

    # ── Per-position trace for first probe ──────────────────────
    log(f"\n{'=' * 72}")
    log("PER-POSITION TRACE (first probe): What does each layer predict?")
    log("=" * 72)
    log(f"  \"{probes[0][:70]}\"")

    first = all_results[0]
    for li in [0, 12, 24, 27, 30, 33, 35]:
        if li not in first["layers"]:
            continue
        lr = first["layers"][li]
        if not lr["position_details"]:
            continue

        log(f"\n  L{li:2d}:")
        for pd in lr["position_details"][:15]:  # first 15 positions
            tok = pd["token"].strip()
            actual = pd["actual_next"]
            preds = pd["predicted_top3"]
            rank = pd["rank_of_actual"]
            hit = "✓" if rank == 0 else f"rank={rank}"
            log(f"    [{tok:>12s}] → actual=[{actual:>12s}] "
                f"pred=[{', '.join(preds):>35s}] {hit}")

    # ── Acceptance rate analysis ────────────────────────────────
    log(f"\n{'=' * 72}")
    log("ACCEPTANCE RATE: If we draft from L[X] and verify at L35")
    log("=" * 72)
    log("How often does layer L's top-1 prediction match L35's top-1?")
    log("This = theoretical acceptance rate for self-speculative decoding.")
    log()

    for li in sorted(layer_indices):
        if li >= n_layers:
            continue
        total_match = 0
        total_count = 0
        for result in all_results:
            if li not in result["layers"]:
                continue
            lr = result["layers"][li]
            total_match += lr.get("final_match", 0)
            total_count += lr.get("final_match_count", 0)
        if total_count > 0:
            rate = total_match / total_count * 100
            log(f"  L{li:2d}: {rate:.1f}% ({total_match}/{total_count})")

    # ── Multi-token acceptance chains ───────────────────────────
    log(f"\n{'=' * 72}")
    log("MULTI-TOKEN CHAINS: How many consecutive tokens can L30 draft?")
    log("=" * 72)

    # For each probe, at L30, count consecutive correct predictions
    target_layer = 30 if 30 in layer_indices else max(l for l in layer_indices if l < 33)
    chain_lengths = []

    for result in all_results:
        if target_layer not in result["layers"]:
            continue
        lr = result["layers"][target_layer]
        if not lr["position_details"]:
            # Recompute from hit data
            continue

        # Use hit@1 for lookahead=1 at each position
        # We need to check consecutive hits
        # For simplicity, use the position_details from the first probe
        if result == all_results[0]:
            chain = 0
            max_chain = 0
            chains = []
            for pd in lr["position_details"]:
                if pd["rank_of_actual"] == 0:
                    chain += 1
                else:
                    if chain > 0:
                        chains.append(chain)
                    chain = 0
            if chain > 0:
                chains.append(chain)

            if chains:
                log(f"\n  First probe chain lengths: {chains}")
                log(f"  Max chain: {max(chains)}")
                log(f"  Mean chain: {np.mean(chains):.1f}")
                log(f"  Total correct: {sum(chains)}/{len(lr['position_details'])}")

    # ── Save results ────────────────────────────────────────────
    results_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "results", "mtp-self-speculation"
    )
    os.makedirs(results_dir, exist_ok=True)

    summary = {
        "model": model_id,
        "n_layers": n_layers,
        "layers_traced": layer_indices,
        "top_ks": top_ks,
        "lookaheads": lookaheads,
        "n_probes": len(probes),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # Aggregate hit rates
    aggregate = {}
    for la in lookaheads:
        aggregate[f"lookahead_{la}"] = {}
        for li in sorted(layer_indices):
            total_hits = {k: 0 for k in top_ks}
            total_count = 0
            all_ranks = []
            for result in all_results:
                if li not in result["layers"]:
                    continue
                lr = result["layers"][li]
                total_count += lr["lookahead_counts"].get(la, 0)
                for k in top_ks:
                    total_hits[k] += lr["lookahead_hits"].get(la, {}).get(k, 0)
                all_ranks.extend(lr["lookahead_ranks"].get(la, []))
            if total_count > 0:
                aggregate[f"lookahead_{la}"][f"L{li}"] = {
                    "hit_rates": {f"top{k}": total_hits[k] / total_count for k in top_ks},
                    "median_rank": float(np.median(all_ranks)) if all_ranks else -1,
                    "count": total_count,
                }

    summary["aggregate"] = aggregate

    # Per-position details for first probe
    summary["first_probe_details"] = {}
    for li, lr in all_results[0]["layers"].items():
        summary["first_probe_details"][f"L{li}"] = lr["position_details"]

    summary_path = os.path.join(results_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    log(f"\nResults saved to {results_dir}/")
    log(f"  summary.json: {os.path.getsize(summary_path) / 1024:.1f} KB")

    log(f"\n{'=' * 72}")
    log("EXPERIMENT COMPLETE")
    log("=" * 72)


def main():
    parser = argparse.ArgumentParser(description="MTP Self-Speculation")
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", default=None, help="Comma-separated layer indices")
    args = parser.parse_args()

    layer_indices = None
    if args.layers:
        layer_indices = sorted(set(int(l) for l in args.layers.split(",")))

    run_experiment(model_id=args.model, layer_indices=layer_indices)


if __name__ == "__main__":
    main()
