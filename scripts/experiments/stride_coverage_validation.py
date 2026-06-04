#!/usr/bin/env python3
"""Stride Coverage Validation: Does stride geometry capture real attention targets?

HYPOTHESIS: StrideStack's geometric candidate positions (16 strides × W=8 = 128
positions) cover the positions that full attention actually selects. If stride
candidates capture ≥88% of attention mass (matching session 188's top-3 coverage),
then sparse stride attention is viable without a content-based indexer.

EXPERIMENT DESIGN:
  For each probe × layer × head × query position:
    1. Capture full attention distribution (ground truth from Qwen3-8B)
    2. Compute stride candidate sets:
       a. STRIDE-EXACT: positions at stride-s × w for each stride s, window w
       b. STRIDE-NBRS:  stride positions ± 1-2 (neighborhood expansion)
       c. LOCAL-8:       last 8 positions (stride-1 window)
       d. COMBINED:      LOCAL-8 ∪ STRIDE-EXACT (the actual proposed design)
       e. COMBINED-NBRS: LOCAL-8 ∪ STRIDE-NBRS (expanded design)
    3. Measure recall: attention mass falling on each candidate set
    4. Measure "best-k within candidates": top-k from candidates vs top-k from all
    5. Compare to ORACLE top-k (session 188 data: top-3 captures 88%+)

METRICS:
  - Mass recall: Σ attn[candidates] / Σ attn[all]
  - Top-k recall: best-k-from-candidates vs oracle-top-k
  - Coverage gap: oracle_top_k - best_k_from_candidates
  - Miss rate: fraction of positions where the binding target is NOT in candidates

LICENSE: MIT
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
# STRIDE GEOMETRY — matches v14 config
# ══════════════════════════════════════════════════════════════════════════════

# v14: 16 strides, powers of 2 from s1 to s32768
STRIDES = tuple(2**i for i in range(16))  # s1..s32768
WINDOW = 8  # positions per stride
NEIGHBOR_RADIUS = 2  # ±2 positions around each stride grid point


def compute_stride_candidates(
    query_pos: int,
    seq_len: int,
    strides: tuple[int, ...] = STRIDES,
    window: int = WINDOW,
) -> set[int]:
    """Compute exact stride grid positions for a query.

    For stride s, window w: candidates = {query_pos - s*w for w in 0..W-1}
    Only includes positions that exist (≥ 0, < seq_len).
    """
    candidates = set()
    for s in strides:
        for w in range(window):
            pos = query_pos - s * w
            if 0 <= pos < seq_len:
                candidates.add(pos)
    return candidates


def compute_stride_candidates_with_neighbors(
    query_pos: int,
    seq_len: int,
    strides: tuple[int, ...] = STRIDES,
    window: int = WINDOW,
    radius: int = NEIGHBOR_RADIUS,
) -> set[int]:
    """Stride grid positions expanded by ±radius neighbors."""
    base = compute_stride_candidates(query_pos, seq_len, strides, window)
    expanded = set()
    for pos in base:
        for delta in range(-radius, radius + 1):
            p = pos + delta
            if 0 <= p < seq_len:
                expanded.add(p)
    return expanded


def compute_local_window(
    query_pos: int,
    window: int = WINDOW,
) -> set[int]:
    """Last `window` positions (stride-1 equivalent)."""
    return {max(0, query_pos - w) for w in range(window)}


# ══════════════════════════════════════════════════════════════════════════════
# PROBES — same set as attention_sparsity.py for comparability
# ══════════════════════════════════════════════════════════════════════════════

PROBES = [
    # Short (3-5 probe tokens)
    ("short", "The dog runs."),
    ("short", "The cat bit the dog."),
    ("short", "John gave Mary the book."),
    ("short", "She told herself the truth."),
    ("short", "Every student reads a book."),

    # Medium (8-15 probe tokens)
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

    # Long (20-40+ probe tokens)
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

    # Very long (paragraph)
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


# ══════════════════════════════════════════════════════════════════════════════
# HEAD TAXONOMY — from session 188 head-combinator-isa findings
# ══════════════════════════════════════════════════════════════════════════════

# Classified by effective positions at L30
HEAD_TAXONOMY = {
    "very_sparse": [9, 25, 11, 8, 30, 27, 29, 26, 14, 10, 18],  # eff_pos 1.4-1.9
    "sparse":      [31, 24, 4, 1, 21, 28, 12, 13, 2, 19, 15],   # eff_pos 2.1-2.7
    "moderate":    [5, 3, 6, 23, 22, 0, 16],                     # eff_pos 3.0-4.9
    "semi_dense":  [7, 17],                                       # eff_pos 5.9-6.0
    "dense":       [20],                                          # eff_pos 11.3
}


def get_head_type(head_idx: int) -> str:
    for htype, heads in HEAD_TAXONOMY.items():
        if head_idx in heads:
            return htype
    return "unknown"


# ══════════════════════════════════════════════════════════════════════════════
# MEASUREMENT
# ══════════════════════════════════════════════════════════════════════════════


def measure_coverage(
    attn_row: np.ndarray,
    candidates: set[int],
    query_pos: int,
) -> dict:
    """Measure how well a candidate set covers the attention distribution.

    Args:
        attn_row: attention weights for one head at one query position, shape (pos+1,)
        candidates: set of candidate key positions
        query_pos: the query position (for context)

    Returns:
        dict with mass_recall, top_k metrics, etc.
    """
    n_positions = len(attn_row)

    # Candidate mask
    cand_mask = np.zeros(n_positions, dtype=bool)
    for c in candidates:
        if c < n_positions:
            cand_mask[c] = True

    n_candidates = int(cand_mask.sum())

    # Mass recall: total attention mass on candidates
    mass_on_candidates = float(attn_row[cand_mask].sum())

    # Oracle top-k: best k positions from ALL positions
    sorted_all = np.sort(attn_row)[::-1]

    # Best-k within candidates: sort candidate weights, take top-k
    cand_weights = attn_row[cand_mask]
    sorted_cand = np.sort(cand_weights)[::-1] if len(cand_weights) > 0 else np.array([0.0])

    result = {
        "n_candidates": n_candidates,
        "mass_recall": mass_on_candidates,
    }

    # Top-k comparison: candidates vs oracle
    for k in [1, 3, 5, 10]:
        oracle_k = float(sorted_all[:k].sum()) if k <= len(sorted_all) else 1.0
        cand_k = float(sorted_cand[:k].sum()) if k <= len(sorted_cand) else mass_on_candidates
        result[f"oracle_top{k}"] = oracle_k
        result[f"cand_top{k}"] = cand_k
        result[f"gap_top{k}"] = oracle_k - cand_k

    # Does the #1 target fall in candidates?
    top1_pos = int(np.argmax(attn_row))
    result["top1_in_candidates"] = bool(top1_pos in candidates)

    # Do the top-3 targets all fall in candidates?
    top3_pos = set(np.argsort(attn_row)[-3:].tolist())
    result["top3_all_in_candidates"] = bool(top3_pos.issubset(candidates))
    result["top3_count_in_candidates"] = len(top3_pos & candidates)

    return result


def run_experiment(
    model_id: str = "Qwen/Qwen3-8B",
    layer_indices: list[int] | None = None,
    stride_configs: dict | None = None,
):
    log("=" * 72)
    log("STRIDE COVERAGE VALIDATION")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Probes: {len(PROBES)}")
    log(f"Strides: {len(STRIDES)} (s{STRIDES[0]}..s{STRIDES[-1]})")
    log(f"Window: {WINDOW}, Neighbor radius: {NEIGHBOR_RADIUS}")
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
        # Focus on binding layers + a few others for context
        layer_indices = [0, 12, 24, 27, 30, 33, 35]
    layer_indices = [l for l in layer_indices if l < n_layers]
    log(f"  Target layers: {layer_indices}")

    # Compile gate (same as session 188 experiments)
    compile_gate = (
        "The dog runs. → λx. runs(dog)\n"
        "Be helpful but concise. → λ assist(x). helpful(x) | concise(x)\n"
        "\nInput: "
    )
    gate_only = tokenizer(compile_gate, return_tensors="pt")
    gate_len = gate_only["input_ids"].shape[1]
    log(f"  Gate length: {gate_len} tokens")

    # Define candidate generation strategies
    strategies = {
        "local_8": lambda qp, sl: compute_local_window(qp, window=8),
        "stride_exact": lambda qp, sl: compute_stride_candidates(qp, sl),
        "stride_nbrs": lambda qp, sl: compute_stride_candidates_with_neighbors(qp, sl),
        "combined": lambda qp, sl: compute_local_window(qp, 8) | compute_stride_candidates(qp, sl),
        "combined_nbrs": lambda qp, sl: compute_local_window(qp, 8) | compute_stride_candidates_with_neighbors(qp, sl),
    }

    # Also test reduced stride sets to find the minimum
    strategies["stride_4"] = lambda qp, sl: compute_stride_candidates(
        qp, sl, strides=tuple(2**i for i in range(4)), window=8,  # s1..s8 only
    )
    strategies["stride_8"] = lambda qp, sl: compute_stride_candidates(
        qp, sl, strides=tuple(2**i for i in range(8)), window=8,  # s1..s128
    )

    log(f"  Strategies: {list(strategies.keys())}")

    # ══════════════════════════════════════════════════════════════
    # RUN PROBES
    # ══════════════════════════════════════════════════════════════

    all_records = []

    for probe_idx, (cat, prompt) in enumerate(PROBES):
        full_text = compile_gate + prompt
        inputs = tokenizer(full_text, return_tensors="pt")
        input_ids = inputs["input_ids"].to(model.device)
        seq_len = input_ids.shape[1]
        n_probe = seq_len - gate_len

        log(f"\n  [{probe_idx+1:2d}/{len(PROBES)}] [{cat:>6s}] {n_probe:3d} tok | {prompt[:55]}...")

        # Capture attention weights
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

        # ── Measure coverage for each layer × head × position ──
        for li in layer_indices:
            if li not in captured:
                continue
            attn = captured[li].numpy()  # (n_q_heads, seq, seq)

            for h in range(n_q_heads):
                htype = get_head_type(h)

                # Aggregate coverage across probe positions
                strat_aggregates = {s: defaultdict(list) for s in strategies}

                for pos in range(gate_len, seq_len):
                    attn_row = attn[h, pos, :pos + 1]
                    # Normalize
                    attn_row = np.maximum(attn_row, 1e-10)
                    attn_row = attn_row / attn_row.sum()

                    for strat_name, strat_fn in strategies.items():
                        candidates = strat_fn(pos, seq_len)
                        # Only include candidates within causal range
                        candidates = {c for c in candidates if c <= pos}
                        cov = measure_coverage(attn_row, candidates, pos)

                        for k, v in cov.items():
                            strat_aggregates[strat_name][k].append(v)

                # Build per-head record
                record = {
                    "probe_idx": probe_idx,
                    "category": cat,
                    "prompt": prompt[:80],
                    "n_probe_tokens": n_probe,
                    "layer": li,
                    "head": h,
                    "head_type": htype,
                    "strategies": {},
                }

                for strat_name, agg in strat_aggregates.items():
                    strat_summary = {}
                    for k, vals in agg.items():
                        if isinstance(vals[0], bool):
                            strat_summary[k] = round(float(np.mean(vals)), 4)
                        elif isinstance(vals[0], (int, np.integer)):
                            strat_summary[k] = round(float(np.mean(vals)), 1)
                        else:
                            strat_summary[k] = round(float(np.mean(vals)), 4)
                    record["strategies"][strat_name] = strat_summary

                all_records.append(record)

    # ══════════════════════════════════════════════════════════════
    # AGGREGATE ANALYSIS
    # ══════════════════════════════════════════════════════════════

    log("\n" + "=" * 72)
    log("AGGREGATE RESULTS")
    log("=" * 72)

    # Group by strategy × head_type × layer
    def aggregate_by(records, group_keys, strat_name, metric):
        groups = defaultdict(list)
        for r in records:
            key = tuple(r[k] for k in group_keys)
            val = r["strategies"].get(strat_name, {}).get(metric)
            if val is not None:
                groups[key].append(val)
        return {k: float(np.mean(v)) for k, v in groups.items()}

    # ── Table 1: Strategy comparison (all heads, binding layers) ──
    log("\n── Table 1: Strategy × Layer (all heads averaged) ──")
    log(f"{'Strategy':<20s} | {'L0':>6s} {'L12':>6s} {'L24':>6s} {'L27':>6s} {'L30':>6s} {'L33':>6s} {'L35':>6s}")
    log("-" * 72)
    for strat in ["local_8", "stride_exact", "stride_nbrs", "combined", "combined_nbrs"]:
        by_layer = aggregate_by(all_records, ["layer"], strat, "mass_recall")
        vals = []
        for li in layer_indices:
            v = by_layer.get((li,), 0)
            vals.append(f"{v:6.1%}")
        log(f"{strat:<20s} | {' '.join(vals)}")

    # ── Table 2: Strategy × Head Type at L30 ──
    log("\n── Table 2: Strategy × Head Type at L30 (mass recall) ──")
    l30_records = [r for r in all_records if r["layer"] == 30]
    log(f"{'Strategy':<20s} | {'v.sparse':>8s} {'sparse':>8s} {'moderate':>8s} {'s.dense':>8s} {'dense':>8s}")
    log("-" * 72)
    for strat in ["local_8", "stride_exact", "combined", "combined_nbrs"]:
        by_ht = aggregate_by(l30_records, ["head_type"], strat, "mass_recall")
        vals = []
        for ht in ["very_sparse", "sparse", "moderate", "semi_dense", "dense"]:
            v = by_ht.get((ht,), 0)
            vals.append(f"{v:8.1%}")
        log(f"{strat:<20s} | {' '.join(vals)}")

    # ── Table 3: Top-1 hit rate (does the primary target fall in candidates?) ──
    log("\n── Table 3: Top-1 target in candidates (% of positions, L30) ──")
    log(f"{'Strategy':<20s} | {'v.sparse':>8s} {'sparse':>8s} {'moderate':>8s} {'s.dense':>8s} {'dense':>8s}")
    log("-" * 72)
    for strat in ["local_8", "stride_exact", "combined", "combined_nbrs"]:
        by_ht = aggregate_by(l30_records, ["head_type"], strat, "top1_in_candidates")
        vals = []
        for ht in ["very_sparse", "sparse", "moderate", "semi_dense", "dense"]:
            v = by_ht.get((ht,), 0)
            vals.append(f"{v:8.1%}")
        log(f"{strat:<20s} | {' '.join(vals)}")

    # ── Table 4: Coverage gap (oracle top-3 minus candidate top-3, at L30) ──
    log("\n── Table 4: Gap: oracle top-3 minus candidate top-3 (L30) ──")
    log(f"{'Strategy':<20s} | {'v.sparse':>8s} {'sparse':>8s} {'moderate':>8s} {'s.dense':>8s} {'dense':>8s}")
    log("-" * 72)
    for strat in ["local_8", "stride_exact", "combined", "combined_nbrs"]:
        by_ht = aggregate_by(l30_records, ["head_type"], strat, "gap_top3")
        vals = []
        for ht in ["very_sparse", "sparse", "moderate", "semi_dense", "dense"]:
            v = by_ht.get((ht,), 0)
            vals.append(f"{v:8.4f}")
        log(f"{strat:<20s} | {' '.join(vals)}")

    # ── Table 5: Coverage by sequence length category ──
    log("\n── Table 5: Mass recall by sequence length (combined strategy, L30) ──")
    log(f"{'Category':<10s} | {'N tokens':>8s} {'mass_recall':>12s} {'top1_hit':>10s} {'gap_top3':>10s}")
    log("-" * 56)
    for cat in ["short", "medium", "long", "vlong"]:
        cat_records = [r for r in l30_records if r["category"] == cat]
        if not cat_records:
            continue
        mass = np.mean([r["strategies"]["combined"]["mass_recall"] for r in cat_records])
        hit = np.mean([r["strategies"]["combined"]["top1_in_candidates"] for r in cat_records])
        gap = np.mean([r["strategies"]["combined"]["gap_top3"] for r in cat_records])
        n_tok = np.mean([r["n_probe_tokens"] for r in cat_records])
        log(f"{cat:<10s} | {n_tok:8.0f} {mass:12.1%} {hit:10.1%} {gap:10.4f}")

    # ── Table 6: Number of candidates per strategy at different seq lengths ──
    log("\n── Table 6: Mean candidates per strategy ──")
    log(f"{'Strategy':<20s} | {'short':>8s} {'medium':>8s} {'long':>8s} {'vlong':>8s}")
    log("-" * 56)
    for strat in ["local_8", "stride_exact", "stride_nbrs", "combined", "combined_nbrs"]:
        vals = []
        for cat in ["short", "medium", "long", "vlong"]:
            cat_recs = [r for r in all_records if r["category"] == cat and r["layer"] == 30]
            if cat_recs:
                nc = np.mean([r["strategies"][strat]["n_candidates"] for r in cat_recs])
                vals.append(f"{nc:8.1f}")
            else:
                vals.append(f"{'—':>8s}")
        log(f"{strat:<20s} | {' '.join(vals)}")

    # ── Table 7: Stride count sweep (how many strides needed?) ──
    log("\n── Table 7: Stride count sweep (mass recall, L30, all heads) ──")
    for strat in ["stride_4", "stride_8", "stride_exact"]:
        l30_mass = aggregate_by(l30_records, [], strat, "mass_recall")
        val = l30_mass.get((), 0)
        n_strides = {"stride_4": 4, "stride_8": 8, "stride_exact": 16}[strat]
        log(f"  {n_strides} strides: mass_recall = {val:.1%}")

    # ══════════════════════════════════════════════════════════════
    # SAVE RESULTS
    # ══════════════════════════════════════════════════════════════

    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "results", "stride-coverage-validation")
    os.makedirs(out_dir, exist_ok=True)

    # Save full per-head records
    full_path = os.path.join(out_dir, "full_results.json")
    with open(full_path, "w") as f:
        json.dump(all_records, f, indent=2)
    log(f"\nFull results: {full_path}")

    # Save summary
    summary = {
        "model": model_id,
        "n_probes": len(PROBES),
        "n_layers": len(layer_indices),
        "layer_indices": layer_indices,
        "n_heads": n_q_heads,
        "strides": list(STRIDES),
        "window": WINDOW,
        "neighbor_radius": NEIGHBOR_RADIUS,
        "strategies": list(strategies.keys()),
        "head_taxonomy": {k: v for k, v in HEAD_TAXONOMY.items()},
    }

    # L30 combined strategy — the key number
    l30_combined = aggregate_by(l30_records, [], "combined", "mass_recall")
    summary["L30_combined_mass_recall"] = l30_combined.get((), 0)
    l30_comb_nbrs = aggregate_by(l30_records, [], "combined_nbrs", "mass_recall")
    summary["L30_combined_nbrs_mass_recall"] = l30_comb_nbrs.get((), 0)

    # Per head-type at L30
    summary["L30_by_head_type"] = {}
    for strat in ["combined", "combined_nbrs"]:
        by_ht = aggregate_by(l30_records, ["head_type"], strat, "mass_recall")
        summary["L30_by_head_type"][strat] = {
            ht: by_ht.get((ht,), 0) for ht in HEAD_TAXONOMY
        }

    sum_path = os.path.join(out_dir, "summary.json")
    with open(sum_path, "w") as f:
        json.dump(summary, f, indent=2)
    log(f"Summary: {sum_path}")

    log("\n" + "=" * 72)
    log("STRIDE COVERAGE VALIDATION COMPLETE")
    log("=" * 72)

    return all_records, summary


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stride Coverage Validation")
    parser.add_argument("--model", default="Qwen/Qwen3-8B", help="Model ID")
    parser.add_argument("--layers", type=str, default=None,
                        help="Comma-separated layer indices (default: 0,12,24,27,30,33,35)")
    args = parser.parse_args()

    layers = None
    if args.layers:
        layers = [int(x.strip()) for x in args.layers.split(",")]

    run_experiment(model_id=args.model, layer_indices=layers)
