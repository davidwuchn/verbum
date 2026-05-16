#!/usr/bin/env python3
"""Factual Recall Probe — Do extracted holographic plates know world facts?

Tests whether ternary sign matrices extracted from Qwen3-14B contain
factual world knowledge that a trained beam (Q) can access.

Method:
  1. Build two models: extracted plates (from Qwen3-14B) vs random plates
  2. Train both for N steps (same data, same hyperparams)
  3. Probe: for each factual prompt, measure log-probability of correct answer
  4. Compare: does extracted assign higher probability to correct facts?

The probe measures RELATIVE signal — we don't expect the small model to
get facts right as top-1 (it's undertrained), but we expect extracted plates
to give the correct answer HIGHER probability than random plates.

Usage:
    uv run python scripts/explore/probe_factual_recall.py
    uv run python scripts/explore/probe_factual_recall.py --train-steps 500

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

# Import the model architecture from the extraction script
sys.path.insert(0, str(Path(__file__).parent))
from extract_and_train import (
    ExtractedModel, TernaryFrozen, SimpleDataLoader, extract_signs,
    D_MODEL, N_HEADS, N_KV_HEADS, HEAD_DIM, VOCAB_SIZE,
)

DATA_DIR = Path("/Users/mwhitford/data/fractal-bitnet/shards-qwen3")
OUTPUT_DIR = Path("results/holographic-extraction")

# ══════════════════════════════════════════════════════════════════
# Factual prompts — things a 14B model definitely knows
# ══════════════════════════════════════════════════════════════════

FACTUAL_PROBES = [
    # Geography
    {"prompt": "The capital of France is", "answer": " Paris"},
    {"prompt": "The capital of Japan is", "answer": " Tokyo"},
    {"prompt": "The capital of Germany is", "answer": " Berlin"},
    {"prompt": "The capital of Italy is", "answer": " Rome"},
    {"prompt": "The capital of Spain is", "answer": " Madrid"},
    {"prompt": "The capital of Russia is", "answer": " Moscow"},
    {"prompt": "The capital of China is", "answer": " Beijing"},
    {"prompt": "The capital of Brazil is", "answer": " Bras"},
    {"prompt": "The capital of Australia is", "answer": " Canberra"},
    {"prompt": "The capital of Canada is", "answer": " Ottawa"},
    {"prompt": "The largest ocean is the", "answer": " Pacific"},
    {"prompt": "The longest river in the world is the", "answer": " Nile"},
    {"prompt": "The highest mountain in the world is Mount", "answer": " Everest"},
    {"prompt": "The largest continent is", "answer": " Asia"},
    {"prompt": "The smallest country in the world is", "answer": " Vatican"},

    # Science
    {"prompt": "Water freezes at zero degrees", "answer": " Celsius"},
    {"prompt": "The speed of light is approximately 300,000 kilometers per", "answer": " second"},
    {"prompt": "The chemical symbol for gold is", "answer": " Au"},
    {"prompt": "The chemical symbol for water is H", "answer": "2"},
    {"prompt": "DNA stands for deoxyribonucleic", "answer": " acid"},
    {"prompt": "The closest star to Earth is the", "answer": " Sun"},
    {"prompt": "Gravity was described by Isaac", "answer": " Newton"},
    {"prompt": "The theory of relativity was developed by Albert", "answer": " Einstein"},
    {"prompt": "The periodic table was created by", "answer": " Dmitri"},
    {"prompt": "Photosynthesis converts sunlight into", "answer": " energy"},

    # Language/Culture
    {"prompt": "Shakespeare wrote Romeo and", "answer": " Juliet"},
    {"prompt": "The Mona Lisa was painted by Leonardo da", "answer": " Vinci"},
    {"prompt": "The Great Wall is located in", "answer": " China"},
    {"prompt": "The Eiffel Tower is in", "answer": " Paris"},
    {"prompt": "The Colosseum is in", "answer": " Rome"},

    # Math/Logic
    {"prompt": "Two plus two equals", "answer": " four"},
    {"prompt": "The square root of 144 is", "answer": " 12"},
    {"prompt": "Pi is approximately 3.14", "answer": "15"},
    {"prompt": "A triangle has three", "answer": " sides"},
    {"prompt": "A hexagon has six", "answer": " sides"},

    # Common knowledge
    {"prompt": "The Earth orbits the", "answer": " Sun"},
    {"prompt": "There are 24 hours in a", "answer": " day"},
    {"prompt": "There are 365 days in a", "answer": " year"},
    {"prompt": "The human body has 206", "answer": " bones"},
    {"prompt": "Oxygen is essential for", "answer": " breathing"},
]


def probe_factual_recall(model, tokenizer, device: str) -> dict:
    """Probe model's factual recall via log-probability of correct answer.

    Returns per-probe results and summary statistics.
    """
    model.eval()
    results = []

    for probe in FACTUAL_PROBES:
        prompt = probe["prompt"]
        answer = probe["answer"]

        # Tokenize prompt
        input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

        # Tokenize answer (first token only)
        answer_ids = tokenizer.encode(answer, add_special_tokens=False)
        if not answer_ids:
            continue
        target_token_id = answer_ids[0]

        # Get logits for next token
        with torch.no_grad():
            logits = model(input_ids)
            if hasattr(logits, 'logits'):
                logits = logits.logits
            # Last position logits
            next_logits = logits[0, -1, :]  # (vocab_size,)

        # Log probability of correct answer
        log_probs = F.log_softmax(next_logits, dim=-1)
        correct_log_prob = log_probs[target_token_id].item()

        # Rank of correct answer
        sorted_indices = torch.argsort(next_logits, descending=True)
        rank = (sorted_indices == target_token_id).nonzero(as_tuple=True)[0].item() + 1

        # Top-1 prediction
        top1_id = sorted_indices[0].item()
        top1_token = tokenizer.decode([top1_id])

        results.append({
            "prompt": prompt,
            "expected": answer,
            "expected_token_id": target_token_id,
            "log_prob": correct_log_prob,
            "rank": rank,
            "top1": top1_token,
            "top1_correct": (top1_id == target_token_id),
        })

    # Summary
    log_probs = [r["log_prob"] for r in results]
    ranks = [r["rank"] for r in results]
    top1_correct = sum(1 for r in results if r["top1_correct"])

    summary = {
        "n_probes": len(results),
        "mean_log_prob": float(np.mean(log_probs)),
        "median_log_prob": float(np.median(log_probs)),
        "mean_rank": float(np.mean(ranks)),
        "median_rank": float(np.median(ranks)),
        "top1_accuracy": top1_correct / len(results) if results else 0,
        "top10_accuracy": sum(1 for r in results if r["rank"] <= 10) / len(results),
        "top100_accuracy": sum(1 for r in results if r["rank"] <= 100) / len(results),
    }

    return {"results": results, "summary": summary}


def train_model_quick(
    model, train_loader, n_steps: int, lr: float, device: str, label: str,
) -> None:
    """Quick training — no eval, just get the model to a reasonable state."""
    model = model.to(device)
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=lr, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_steps)

    t0 = time.time()
    for step in range(1, n_steps + 1):
        model.train()
        input_ids, targets = train_loader.next_batch()
        input_ids = input_ids.to(device)
        targets = targets.to(device)

        logits = model(input_ids)
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
        optimizer.step()
        scheduler.step()

        if step % 100 == 0 or step == 1:
            elapsed = time.time() - t0
            tok_per_sec = step * 2 * 256 / elapsed
            print(f"  [{label}] step {step:>4} | loss {loss.item():.4f} | "
                  f"{tok_per_sec:.0f} tok/s", file=sys.stderr)

    print(f"  [{label}] Training done: {n_steps} steps, {time.time()-t0:.1f}s",
          file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Factual recall probe")
    parser.add_argument("--source", default="Qwen/Qwen3-14B")
    parser.add_argument("--train-steps", type=int, default=500)
    parser.add_argument("--n-layers", type=int, default=4)
    parser.add_argument("--layer-stride", type=int, default=10)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    layer_indices = list(range(0, 40, args.layer_stride))[:args.n_layers]

    # Load tokenizer for probing
    tokenizer = AutoTokenizer.from_pretrained(args.source)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  FACTUAL RECALL PROBE", file=sys.stderr)
    print(f"  Source: {args.source}", file=sys.stderr)
    print(f"  Layers: {layer_indices}", file=sys.stderr)
    print(f"  Train steps: {args.train_steps}", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)

    # ── Extract signs ─────────────────────────────────────
    print("Phase 1: Extracting signs...", file=sys.stderr)
    extracted_signs = extract_signs(args.source, layer_indices, device=args.device)

    intermediate = extracted_signs[0]["gate"].shape[0]

    # ── Build models ──────────────────────────────────────
    print("\nPhase 2: Building models...", file=sys.stderr)

    model_extracted = ExtractedModel(
        n_layers=len(layer_indices),
        d_model=D_MODEL, n_heads=N_HEADS, n_kv_heads=N_KV_HEADS,
        head_dim=HEAD_DIM, intermediate=intermediate,
        vocab_size=VOCAB_SIZE, layer_signs=extracted_signs,
    )

    model_random = ExtractedModel(
        n_layers=len(layer_indices),
        d_model=D_MODEL, n_heads=N_HEADS, n_kv_heads=N_KV_HEADS,
        head_dim=HEAD_DIM, intermediate=intermediate,
        vocab_size=VOCAB_SIZE, layer_signs=None,
    )

    params = model_extracted.count_params()
    print(f"  Params: {params['trainable']/1e6:.0f}M trainable, "
          f"{params['frozen_ternary']/1e6:.0f}M frozen", file=sys.stderr)

    # ── Train both models ─────────────────────────────────
    print("\nPhase 3: Training...", file=sys.stderr)

    train_loader_a = SimpleDataLoader(DATA_DIR, 2, 256, shard_start=0, shard_end=4, seed=42)
    train_model_quick(model_extracted, train_loader_a, args.train_steps,
                      args.lr, args.device, "EXTRACTED")

    # Free memory
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    train_loader_b = SimpleDataLoader(DATA_DIR, 2, 256, shard_start=0, shard_end=4, seed=42)
    train_model_quick(model_random, train_loader_b, args.train_steps,
                      args.lr, args.device, "RANDOM")

    # ── Probe factual recall ──────────────────────────────
    print(f"\nPhase 4: Factual recall probe ({len(FACTUAL_PROBES)} facts)...",
          file=sys.stderr)

    print("\n  Probing EXTRACTED model...", file=sys.stderr)
    results_extracted = probe_factual_recall(model_extracted, tokenizer, args.device)

    print("  Probing RANDOM model...", file=sys.stderr)
    results_random = probe_factual_recall(model_random, tokenizer, args.device)

    # ── Compare ───────────────────────────────────────────
    se = results_extracted["summary"]
    sr = results_random["summary"]

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  FACTUAL RECALL RESULTS", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"\n  {'Metric':<25} {'Extracted':>12} {'Random':>12} {'Δ':>10}", file=sys.stderr)
    print(f"  {'─'*25} {'─'*12} {'─'*12} {'─'*10}", file=sys.stderr)
    print(f"  {'Mean log-prob':<25} {se['mean_log_prob']:>12.4f} {sr['mean_log_prob']:>12.4f} "
          f"{se['mean_log_prob']-sr['mean_log_prob']:>+10.4f}", file=sys.stderr)
    print(f"  {'Median log-prob':<25} {se['median_log_prob']:>12.4f} {sr['median_log_prob']:>12.4f} "
          f"{se['median_log_prob']-sr['median_log_prob']:>+10.4f}", file=sys.stderr)
    print(f"  {'Mean rank':<25} {se['mean_rank']:>12.1f} {sr['mean_rank']:>12.1f} "
          f"{se['mean_rank']-sr['mean_rank']:>+10.1f}", file=sys.stderr)
    print(f"  {'Median rank':<25} {se['median_rank']:>12.1f} {sr['median_rank']:>12.1f} "
          f"{se['median_rank']-sr['median_rank']:>+10.1f}", file=sys.stderr)
    print(f"  {'Top-1 accuracy':<25} {se['top1_accuracy']:>11.1%} {sr['top1_accuracy']:>11.1%} "
          f"{se['top1_accuracy']-sr['top1_accuracy']:>+10.1%}", file=sys.stderr)
    print(f"  {'Top-10 accuracy':<25} {se['top10_accuracy']:>11.1%} {sr['top10_accuracy']:>11.1%} "
          f"{se['top10_accuracy']-sr['top10_accuracy']:>+10.1%}", file=sys.stderr)
    print(f"  {'Top-100 accuracy':<25} {se['top100_accuracy']:>11.1%} {sr['top100_accuracy']:>11.1%} "
          f"{se['top100_accuracy']-sr['top100_accuracy']:>+10.1%}", file=sys.stderr)

    # Show some individual results
    print(f"\n  Sample results (Extracted):", file=sys.stderr)
    for r in results_extracted["results"][:10]:
        marker = "✓" if r["top1_correct"] else f"✗ (got '{r['top1']}')"
        print(f"    \"{r['prompt']}\" → rank {r['rank']:>5}, "
              f"logp={r['log_prob']:.3f} {marker}", file=sys.stderr)

    print(f"\n  Sample results (Random):", file=sys.stderr)
    for r in results_random["results"][:10]:
        marker = "✓" if r["top1_correct"] else f"✗ (got '{r['top1']}')"
        print(f"    \"{r['prompt']}\" → rank {r['rank']:>5}, "
              f"logp={r['log_prob']:.3f} {marker}", file=sys.stderr)

    # Verdict
    print(f"\n  ═══ VERDICT ═══", file=sys.stderr)
    logprob_better = se["mean_log_prob"] > sr["mean_log_prob"]
    rank_better = se["mean_rank"] < sr["mean_rank"]

    if logprob_better:
        delta_pct = (se["mean_log_prob"] - sr["mean_log_prob"]) / abs(sr["mean_log_prob"]) * 100
        print(f"  ✅ EXTRACTED plates assign {delta_pct:.1f}% higher log-prob to correct facts",
              file=sys.stderr)
        print(f"     The holographic plate carries world knowledge!", file=sys.stderr)
    else:
        print(f"  ⚠️  Random plates match or beat extracted on factual recall", file=sys.stderr)
        print(f"     May need more training steps or more layers", file=sys.stderr)

    if rank_better:
        print(f"  ✅ EXTRACTED ranks correct answers {sr['mean_rank']-se['mean_rank']:.0f} "
              f"positions higher on average", file=sys.stderr)

    # Per-fact comparison
    n_extracted_wins = 0
    n_random_wins = 0
    for re, rr in zip(results_extracted["results"], results_random["results"]):
        if re["log_prob"] > rr["log_prob"]:
            n_extracted_wins += 1
        elif rr["log_prob"] > re["log_prob"]:
            n_random_wins += 1

    print(f"\n  Per-fact wins: Extracted={n_extracted_wins}, "
          f"Random={n_random_wins}, Tied={len(FACTUAL_PROBES)-n_extracted_wins-n_random_wins}",
          file=sys.stderr)

    # Save results
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_model": args.source,
        "layer_indices": layer_indices,
        "train_steps": args.train_steps,
        "n_probes": len(FACTUAL_PROBES),
        "summary_extracted": se,
        "summary_random": sr,
        "per_fact_wins": {
            "extracted": n_extracted_wins,
            "random": n_random_wins,
        },
        "extracted_better_logprob": logprob_better,
        "extracted_better_rank": rank_better,
        "results_extracted": results_extracted["results"],
        "results_random": results_random["results"],
    }

    json_path = args.output_dir / "factual_recall_results.json"
    json_path.write_text(json.dumps(output, indent=2))
    print(f"\n  💾 Results: {json_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
