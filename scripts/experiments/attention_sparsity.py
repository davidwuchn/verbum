#!/usr/bin/env python3
"""Attention Sparsity Analysis: How many positions actually matter per head?

QUESTION: If binding is ~1 bit per position (near-deterministic routing),
can we avoid attending to every token in the context?

MEASUREMENTS per head, per layer, per query position:
  1. Shannon entropy of attention distribution → how many bits?
  2. Effective positions = exp(entropy) → how many positions matter?
  3. Top-k coverage: % of attention mass in top 1, 2, 3, 5, 10 positions
  4. Locality: attention weight as function of distance |query - key|
  5. Gate vs probe attention split

PROBES: Mix of short (3-5 tokens), medium (8-15), long (20-40+).
Tests whether sparsity holds at different sequence lengths.

DESIGN IMPLICATIONS:
  - If effective_positions ≤ 3 → top-k attention viable (only score 3 positions)
  - If attention decays with distance → sliding window viable
  - If specific positions dominate → structural routing (type-based) viable
  - If sparsity increases with seq length → efficient attention scales better

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict

os.environ.setdefault("PYTHONUNBUFFERED", "1")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import numpy as np
import torch

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


# ══════════════════════════════════════════════════════════════════════════════
# PROBES — varying lengths
# ══════════════════════════════════════════════════════════════════════════════

PROBES = [
    # ── Short (3-5 probe tokens) ────────────────────────────────
    ("short", "The dog runs."),
    ("short", "The cat bit the dog."),
    ("short", "John gave Mary the book."),
    ("short", "She told herself the truth."),
    ("short", "Every student reads a book."),

    # ── Medium (8-15 probe tokens) ──────────────────────────────
    ("medium", "The cat that sat on the mat is black."),
    ("medium", "If it rains tomorrow, the ground will be wet."),
    ("medium", "The tall boy quickly kicked the red ball across the field."),
    ("medium", "She believed that he had already finished the project."),
    ("medium", "The man who wrote the book also directed the movie."),
    ("medium", "A folder contains files and other folders which contain files."),
    ("medium", "The ball was kicked by the boy who lives next door."),
    ("medium", "After washing the dishes, she dried them with a clean towel."),
    ("medium", "Of all the animals in the zoo, only the lion was truly fierce."),
    ("medium", "The letter was written by the president and sent to congress."),

    # ── Long (20-40+ probe tokens) ──────────────────────────────
    ("long", "The professor who taught the class that the students in the back row "
             "found most difficult to follow had written several influential papers "
             "on the topic of quantum computing."),
    ("long", "When the storm finally passed and the sun came out from behind the "
             "thick grey clouds, the children ran outside to play in the puddles "
             "that had formed on the sidewalk."),
    ("long", "The old woman who lived in the small house at the end of the long "
             "winding road had a garden full of roses that bloomed every spring "
             "and attracted butterflies from miles around."),
    ("long", "Despite the fact that the evidence clearly pointed to a different "
             "conclusion, the detective insisted that his original theory about the "
             "crime was correct and refused to consider any alternative explanation."),
    ("long", "The company that had been struggling financially for several years "
             "finally announced that it would be merging with its largest competitor "
             "in a deal worth several billion dollars."),

    # ── Very long (paragraph) ───────────────────────────────────
    ("vlong", "The ancient library stood at the center of the university campus. "
              "Its stone walls had witnessed centuries of scholars coming and going. "
              "Inside, rows upon rows of wooden shelves held thousands of books on "
              "every subject imaginable. The head librarian, an elderly woman named "
              "Margaret, had worked there for over forty years. She knew the location "
              "of every book and could find any reference in minutes."),
    ("vlong", "The experiment began at dawn when the researchers arrived at the field "
              "station. They set up their equipment along the riverbank and waited for "
              "the first signs of activity. By midmorning, they had recorded dozens of "
              "observations. The data showed clear patterns that matched their predictions. "
              "The team leader documented everything carefully in her notebook, knowing "
              "that these findings would be significant for future studies."),
]


def run_experiment(
    model_id: str = "Qwen/Qwen3-8B",
    layer_indices: list[int] | None = None,
):
    log("=" * 72)
    log("ATTENTION SPARSITY ANALYSIS")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Probes: {len(PROBES)}")
    log()

    from transformers import AutoModelForCausalLM, AutoTokenizer

    log("Loading model...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="mps",
        low_cpu_mem_usage=True,
        attn_implementation="eager",
    )
    model.eval()
    log(f"  Loaded in {time.time() - t0:.1f}s")

    config = model.config
    n_layers = config.num_hidden_layers
    n_q_heads = config.num_attention_heads
    log(f"  {n_layers} layers, {n_q_heads} Q heads")

    if layer_indices is None:
        layer_indices = [0, 6, 12, 18, 24, 27, 30, 33, 35]
    layer_indices = [l for l in layer_indices if l < n_layers]
    log(f"  Target layers: {layer_indices}")

    compile_gate = (
        "The dog runs. → λx. runs(dog)\n"
        "Be helpful but concise. → λ assist(x). helpful(x) | concise(x)\n"
        "\nInput: "
    )
    gate_only = tokenizer(compile_gate, return_tensors="pt")
    gate_len = gate_only["input_ids"].shape[1]
    log(f"  Gate length: {gate_len} tokens")

    # ══════════════════════════════════════════════════════════════
    # MEASUREMENT
    # ══════════════════════════════════════════════════════════════

    all_records = []

    for cat, prompt in PROBES:
        full_text = compile_gate + prompt
        inputs = tokenizer(full_text, return_tensors="pt")
        input_ids = inputs["input_ids"].to(model.device)
        seq_len = input_ids.shape[1]
        n_probe = seq_len - gate_len

        log(f"\n  [{cat:>6s}] {n_probe:3d} tok | {prompt[:60]}...")

        # Hook
        captured: dict[int, torch.Tensor] = {}
        hooks = []
        for li in layer_indices:
            attn_module = model.model.layers[li].self_attn

            def make_hook(layer_idx):
                def hook_fn(module, args, kwargs, output):
                    attn_weights = output[1]
                    if attn_weights is not None:
                        captured[layer_idx] = attn_weights[0].cpu().float()
                    return output
                return hook_fn

            h = attn_module.register_forward_hook(make_hook(li), with_kwargs=True)
            hooks.append(h)

        with torch.no_grad():
            model(input_ids, output_attentions=True, return_dict=True)
        for h in hooks:
            h.remove()

        # ── Compute sparsity metrics ────────────────────────────
        record = {
            "category": cat,
            "prompt": prompt[:80],
            "n_probe_tokens": n_probe,
            "seq_len": seq_len,
            "layers": {},
        }

        for li in layer_indices:
            if li not in captured:
                continue
            attn = captured[li]  # (n_q_heads, seq, seq)

            layer_metrics = {
                "heads": [],
            }

            for h in range(n_q_heads):
                # Only analyze probe positions (skip gate)
                entropies = []
                eff_positions = []
                top_k_coverages = {1: [], 2: [], 3: [], 5: [], 10: []}
                locality_weights = []  # (distance, weight) pairs
                gate_fracs = []
                max_weights = []

                for pos in range(gate_len, seq_len):
                    attn_row = attn[h, pos, :pos + 1]  # causal: only up to pos
                    # Clamp for numerical stability
                    attn_row = attn_row.clamp(min=1e-10)
                    attn_row = attn_row / attn_row.sum()  # renormalize

                    # Shannon entropy
                    ent = -(attn_row * attn_row.log()).sum().item()
                    entropies.append(ent)
                    eff_positions.append(math.exp(ent))

                    # Top-k coverage
                    sorted_weights, _ = attn_row.sort(descending=True)
                    cumsum = sorted_weights.cumsum(0)
                    for k in top_k_coverages:
                        if k <= len(sorted_weights):
                            top_k_coverages[k].append(cumsum[k - 1].item())
                        else:
                            top_k_coverages[k].append(1.0)

                    # Max weight
                    max_weights.append(sorted_weights[0].item())

                    # Locality: weight vs distance from current position
                    for key_pos in range(pos + 1):
                        dist = pos - key_pos
                        w = attn_row[key_pos].item()
                        if w > 0.001:  # only track non-trivial weights
                            locality_weights.append((dist, w))

                    # Gate vs probe
                    gate_mass = attn_row[:gate_len].sum().item()
                    gate_fracs.append(gate_mass)

                head_metrics = {
                    "head": h,
                    "mean_entropy": round(float(np.mean(entropies)), 3),
                    "mean_eff_positions": round(float(np.mean(eff_positions)), 2),
                    "max_eff_positions": round(float(np.max(eff_positions)), 2),
                    "mean_max_weight": round(float(np.mean(max_weights)), 4),
                    "min_max_weight": round(float(np.min(max_weights)), 4),
                    "top_k_coverage": {
                        str(k): round(float(np.mean(v)), 4)
                        for k, v in top_k_coverages.items()
                    },
                    "mean_gate_frac": round(float(np.mean(gate_fracs)), 4),
                }

                # Locality: bin by distance
                if locality_weights:
                    dist_bins = defaultdict(list)
                    for dist, w in locality_weights:
                        if dist == 0:
                            bin_name = "0"
                        elif dist <= 2:
                            bin_name = "1-2"
                        elif dist <= 5:
                            bin_name = "3-5"
                        elif dist <= 10:
                            bin_name = "6-10"
                        elif dist <= 20:
                            bin_name = "11-20"
                        else:
                            bin_name = "21+"
                        dist_bins[bin_name].append(w)

                    head_metrics["locality"] = {
                        bin_name: {
                            "mean_weight": round(float(np.mean(weights)), 4),
                            "count": len(weights),
                        }
                        for bin_name, weights in sorted(dist_bins.items())
                    }

                layer_metrics["heads"].append(head_metrics)

            record["layers"][li] = layer_metrics

        all_records.append(record)
        del captured

    # ══════════════════════════════════════════════════════════════
    # ANALYSIS
    # ══════════════════════════════════════════════════════════════

    log(f"\n{'=' * 72}")
    log("ANALYSIS: ATTENTION SPARSITY")
    log("=" * 72)

    # ── Per-layer summary ───────────────────────────────────────
    for li in layer_indices:
        log(f"\n{'─' * 60}")
        log(f"LAYER {li}")
        log("─" * 60)

        # Aggregate across all probes
        head_entropies = defaultdict(list)
        head_eff_pos = defaultdict(list)
        head_max_w = defaultdict(list)
        head_top1 = defaultdict(list)
        head_top3 = defaultdict(list)
        head_top5 = defaultdict(list)
        head_top10 = defaultdict(list)
        head_gate = defaultdict(list)

        for rec in all_records:
            if li not in rec["layers"]:
                continue
            for hm in rec["layers"][li]["heads"]:
                h = hm["head"]
                head_entropies[h].append(hm["mean_entropy"])
                head_eff_pos[h].append(hm["mean_eff_positions"])
                head_max_w[h].append(hm["mean_max_weight"])
                head_top1[h].append(hm["top_k_coverage"]["1"])
                head_top3[h].append(hm["top_k_coverage"]["3"])
                head_top5[h].append(hm["top_k_coverage"]["5"])
                head_top10[h].append(hm["top_k_coverage"]["10"])
                head_gate[h].append(hm["mean_gate_frac"])

        log(f"\n  {'Head':>6s} {'Entropy':>8s} {'EffPos':>7s} {'MaxWt':>7s} "
            f"{'Top1':>6s} {'Top3':>6s} {'Top5':>6s} {'Top10':>6s} {'Gate%':>6s}")
        log(f"  {'─' * 68}")

        sorted_heads = sorted(range(n_q_heads),
                              key=lambda h: np.mean(head_eff_pos.get(h, [0])))

        for h in sorted_heads:
            ent = np.mean(head_entropies.get(h, [0]))
            eff = np.mean(head_eff_pos.get(h, [0]))
            mw = np.mean(head_max_w.get(h, [0]))
            t1 = np.mean(head_top1.get(h, [0]))
            t3 = np.mean(head_top3.get(h, [0]))
            t5 = np.mean(head_top5.get(h, [0]))
            t10 = np.mean(head_top10.get(h, [0]))
            gate = np.mean(head_gate.get(h, [0]))

            marker = " ◆" if eff < 3 else " •" if eff < 5 else ""
            log(f"  H{h:02d}   {ent:8.2f} {eff:7.1f} {mw:7.3f} "
                f"{t1:6.1%} {t3:6.1%} {t5:6.1%} {t10:6.1%} {gate:6.1%}{marker}")

    # ── Sparsity by sequence length ─────────────────────────────
    log(f"\n{'=' * 72}")
    log("SPARSITY BY SEQUENCE LENGTH")
    log("=" * 72)
    log("Does attention get sparser with longer sequences?")

    categories = ["short", "medium", "long", "vlong"]
    for li in [27, 30, 33]:
        if li not in layer_indices:
            continue
        log(f"\n  L{li}:")
        log(f"  {'Category':>10s} {'NTokens':>8s} {'MeanEnt':>8s} {'MeanEffPos':>10s} "
            f"{'Top3Cov':>8s} {'Top10Cov':>9s}")

        for cat in categories:
            cat_entropies = []
            cat_eff = []
            cat_top3 = []
            cat_top10 = []
            cat_ntok = []

            for rec in all_records:
                if rec["category"] != cat or li not in rec["layers"]:
                    continue
                cat_ntok.append(rec["n_probe_tokens"])
                for hm in rec["layers"][li]["heads"]:
                    cat_entropies.append(hm["mean_entropy"])
                    cat_eff.append(hm["mean_eff_positions"])
                    cat_top3.append(hm["top_k_coverage"]["3"])
                    cat_top10.append(hm["top_k_coverage"]["10"])

            if cat_entropies:
                log(f"  {cat:>10s} {np.mean(cat_ntok):8.0f} {np.mean(cat_entropies):8.2f} "
                    f"{np.mean(cat_eff):10.1f} {np.mean(cat_top3):8.1%} "
                    f"{np.mean(cat_top10):9.1%}")

    # ── How many KV slots does each head need? ──────────────────
    log(f"\n{'=' * 72}")
    log("KV SLOTS NEEDED PER HEAD (top-k to capture 90/95/99% of attention)")
    log("=" * 72)

    for li in [27, 30, 33]:
        if li not in layer_indices:
            continue
        log(f"\n  L{li}:")
        log(f"  {'Head':>6s} {'for 90%':>8s} {'for 95%':>8s} {'for 99%':>8s} {'EffPos':>8s}")

        for h in range(n_q_heads):
            # Compute how many positions needed for 90/95/99% coverage
            coverages_90 = []
            coverages_95 = []
            coverages_99 = []

            for rec in all_records:
                if li not in rec["layers"]:
                    continue
                hm = rec["layers"][li]["heads"][h]
                for k, cov_name in [(1, "1"), (2, "2"), (3, "3"), (5, "5"), (10, "10")]:
                    cov = hm["top_k_coverage"][cov_name]
                    if cov >= 0.90 and not coverages_90:
                        coverages_90.append(k)
                    if cov >= 0.95 and not coverages_95:
                        coverages_95.append(k)
                    if cov >= 0.99 and not coverages_99:
                        coverages_99.append(k)

                if not coverages_90:
                    coverages_90.append(11)
                if not coverages_95:
                    coverages_95.append(11)
                if not coverages_99:
                    coverages_99.append(11)

            eff = np.mean(head_eff_pos.get(h, [0]))
            k90 = np.mean(coverages_90) if coverages_90 else 11
            k95 = np.mean(coverages_95) if coverages_95 else 11
            k99 = np.mean(coverages_99) if coverages_99 else 11

            marker = " ◆" if k95 <= 3 else " •" if k95 <= 5 else ""
            log(f"  H{h:02d}   {k90:8.1f} {k95:8.1f} {k99:8.1f} {eff:8.1f}{marker}")

    # ── Overall design recommendation ───────────────────────────
    log(f"\n{'=' * 72}")
    log("DESIGN RECOMMENDATION")
    log("=" * 72)

    # Count heads by sparsity level across binding layers
    for li in [27, 30, 33]:
        if li not in layer_indices:
            continue
        very_sparse = 0  # eff_pos < 3
        sparse = 0       # eff_pos 3-5
        moderate = 0     # eff_pos 5-10
        dense = 0        # eff_pos > 10

        for h in range(n_q_heads):
            eff = np.mean(head_eff_pos.get(h, [0]))
            if eff < 3:
                very_sparse += 1
            elif eff < 5:
                sparse += 1
            elif eff < 10:
                moderate += 1
            else:
                dense += 1

        log(f"\n  L{li}: {very_sparse} very sparse (<3), {sparse} sparse (3-5), "
            f"{moderate} moderate (5-10), {dense} dense (>10)")

    # ══════════════════════════════════════════════════════════════
    # SAVE
    # ══════════════════════════════════════════════════════════════

    results_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "results", "attention-sparsity"
    )
    os.makedirs(results_dir, exist_ok=True)

    summary = {
        "model": model_id,
        "layers": layer_indices,
        "n_probes": len(PROBES),
        "n_q_heads": n_q_heads,
        "gate_len": gate_len,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "records": all_records,
    }

    summary_path = os.path.join(results_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    log(f"\n{'=' * 72}")
    log(f"RESULTS SAVED to {results_dir}/")
    log(f"  summary.json: {os.path.getsize(summary_path) / 1024:.1f} KB")
    log("=" * 72)


def main():
    parser = argparse.ArgumentParser(description="Attention Sparsity Analysis")
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", default=None)
    args = parser.parse_args()

    layer_indices = None
    if args.layers:
        layer_indices = [int(l) for l in args.layers.split(",")]

    run_experiment(model_id=args.model, layer_indices=layer_indices)


if __name__ == "__main__":
    main()
