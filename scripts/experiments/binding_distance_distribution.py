#!/usr/bin/env python3
"""Binding Distance Distribution: What distances do attention targets live at?

QUESTION: Do binding distances follow a power law? If so, what exponent?
And what stride spacing maximizes coverage of the actual distribution?

For each probe × layer × head × query position:
  1. Find the top-1, top-3, top-5 attention targets
  2. Compute the DISTANCE from query to each target
  3. Accumulate the distance distribution
  4. Fit power law, log-normal, exponential
  5. Design optimal stride positions that maximize mass capture

If d^(-α) is the law, then strides should be spaced as d_k = c^(k/α)
for some base c — NOT necessarily powers of 2.

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
from scipy import stats as sp_stats
from scipy.optimize import minimize_scalar

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


# ══════════════════════════════════════════════════════════════════════════════
# PROBES
# ══════════════════════════════════════════════════════════════════════════════

PROBES = [
    ("short", "The dog runs."),
    ("short", "The cat bit the dog."),
    ("short", "John gave Mary the book."),
    ("short", "She told herself the truth."),
    ("short", "Every student reads a book."),
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


# Head taxonomy from session 188
HEAD_TAXONOMY = {
    "very_sparse": [9, 25, 11, 8, 30, 27, 29, 26, 14, 10, 18],
    "sparse":      [31, 24, 4, 1, 21, 28, 12, 13, 2, 19, 15],
    "moderate":    [5, 3, 6, 23, 22, 0, 16],
    "semi_dense":  [7, 17],
    "dense":       [20],
}


def get_head_type(h: int) -> str:
    for ht, heads in HEAD_TAXONOMY.items():
        if h in heads:
            return ht
    return "unknown"


# ══════════════════════════════════════════════════════════════════════════════
# STRIDE COVERAGE OPTIMIZER
# ══════════════════════════════════════════════════════════════════════════════


def compute_coverage_for_strides(
    strides: list[int],
    window: int,
    distances: np.ndarray,
    weights: np.ndarray,
    radius: int = 0,
) -> float:
    """Compute what fraction of weighted attention mass falls on stride grid ± radius.

    For each distance d in `distances` (with corresponding attention weight),
    check if any stride grid point s*w (for s in strides, w in 0..window-1)
    is within `radius` of d. If so, that weight is "captured".
    """
    # Build the set of all reachable distances from stride grid
    reachable = set()
    for s in strides:
        for w in range(window):
            d = s * w
            for r in range(-radius, radius + 1):
                if d + r >= 0:
                    reachable.add(d + r)

    total_weight = weights.sum()
    if total_weight < 1e-10:
        return 0.0

    captured = 0.0
    for d, w in zip(distances, weights):
        if int(d) in reachable:
            captured += w

    return captured / total_weight


def design_optimal_strides(
    distances: np.ndarray,
    weights: np.ndarray,
    n_strides: int = 16,
    window: int = 8,
    radius: int = 0,
    max_stride: int = 32768,
) -> tuple[list[int], float]:
    """Find the set of n_strides stride values that maximizes weighted coverage.

    Uses a greedy algorithm: start with stride=1 (always needed),
    then greedily add the stride that captures the most uncovered mass.
    """
    # Stride 1 is always included (local attention)
    chosen = [1]

    # Track which distances are already covered
    covered = set()
    for w in range(window):
        d = 1 * w
        for r in range(-radius, radius + 1):
            if d + r >= 0:
                covered.add(d + r)

    for _ in range(n_strides - 1):
        best_stride = None
        best_gain = -1

        # Try candidate strides
        candidates = set()
        # Always try powers of 2
        for i in range(16):
            s = 2 ** i
            if s <= max_stride:
                candidates.add(s)
        # Try powers of phi
        for i in range(30):
            s = max(1, round(PHI ** i))
            if s <= max_stride:
                candidates.add(s)
        # Try Fibonacci numbers
        a, b = 1, 1
        while a <= max_stride:
            candidates.add(a)
            a, b = b, a + b
        # Try near-existing strides (multiplicative neighbors)
        for s in list(chosen):
            for mult in [2, 3, 5, 7]:
                if s * mult <= max_stride:
                    candidates.add(s * mult)
        # Remove already chosen
        candidates -= set(chosen)

        for s in sorted(candidates):
            # What new distances would this stride cover?
            new_covered = set()
            for w in range(window):
                d = s * w
                for r in range(-radius, radius + 1):
                    if d + r >= 0 and d + r not in covered:
                        new_covered.add(d + r)

            # How much new mass?
            gain = 0.0
            for d, wt in zip(distances, weights):
                if int(d) in new_covered:
                    gain += wt

            if gain > best_gain:
                best_gain = gain
                best_stride = s

        if best_stride is None or best_gain <= 0:
            break

        chosen.append(best_stride)
        # Update covered set
        for w in range(window):
            d = best_stride * w
            for r in range(-radius, radius + 1):
                if d + r >= 0:
                    covered.add(d + r)

    coverage = compute_coverage_for_strides(chosen, window, distances, weights, radius)
    return sorted(chosen), coverage


# ══════════════════════════════════════════════════════════════════════════════
# MAIN EXPERIMENT
# ══════════════════════════════════════════════════════════════════════════════


def run_experiment(
    model_id: str = "Qwen/Qwen3-8B",
    layer_indices: list[int] | None = None,
):
    log("=" * 72)
    log("BINDING DISTANCE DISTRIBUTION")
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
        layer_indices = [0, 12, 24, 27, 30, 33, 35]
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
    # COLLECT DISTANCE DISTRIBUTIONS
    # ══════════════════════════════════════════════════════════════

    # Accumulate (distance, weight) pairs per layer × head_type
    dist_weight_by = defaultdict(lambda: ([], []))  # key → (distances, weights)
    # Also accumulate globally per layer
    dist_weight_by_layer = defaultdict(lambda: ([], []))

    # Per-head accumulation
    dist_weight_by_head = defaultdict(lambda: ([], []))

    for probe_idx, (cat, prompt) in enumerate(PROBES):
        full_text = compile_gate + prompt
        inputs = tokenizer(full_text, return_tensors="pt")
        input_ids = inputs["input_ids"].to(model.device)
        seq_len = input_ids.shape[1]
        n_probe = seq_len - gate_len

        log(f"  [{probe_idx+1:2d}/{len(PROBES)}] [{cat:>6s}] {n_probe:3d} tok | {prompt[:55]}...")

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

        # Extract distances
        for li in layer_indices:
            if li not in captured:
                continue
            attn = captured[li].numpy()

            for h in range(n_q_heads):
                htype = get_head_type(h)

                for pos in range(gate_len, seq_len):
                    attn_row = attn[h, pos, :pos + 1]
                    attn_row = np.maximum(attn_row, 1e-10)
                    attn_row = attn_row / attn_row.sum()

                    # Record ALL (distance, weight) pairs with non-trivial weight
                    for key_pos in range(pos + 1):
                        w = float(attn_row[key_pos])
                        if w > 0.001:  # threshold for noise
                            d = pos - key_pos
                            dist_weight_by[(li, htype)][0].append(d)
                            dist_weight_by[(li, htype)][1].append(w)
                            dist_weight_by_layer[li][0].append(d)
                            dist_weight_by_layer[li][1].append(w)
                            dist_weight_by_head[(li, h)][0].append(d)
                            dist_weight_by_head[(li, h)][1].append(w)

    # ══════════════════════════════════════════════════════════════
    # ANALYSIS
    # ══════════════════════════════════════════════════════════════

    log("\n" + "=" * 72)
    log("DISTANCE DISTRIBUTION ANALYSIS")
    log("=" * 72)

    # ── 1. Weighted distance distribution at L30 ──
    log("\n── 1. Weighted distance percentiles at binding layers ──")
    log(f"{'Layer':>6s} | {'p10':>6s} {'p25':>6s} {'p50':>6s} {'p75':>6s} {'p90':>6s} {'p99':>6s} | {'mean':>6s} {'std':>6s}")
    log("-" * 72)
    for li in layer_indices:
        dists, weights = dist_weight_by_layer[li]
        if not dists:
            continue
        d_arr = np.array(dists, dtype=float)
        w_arr = np.array(weights, dtype=float)

        # Weighted percentiles
        sorted_idx = np.argsort(d_arr)
        d_sorted = d_arr[sorted_idx]
        w_sorted = w_arr[sorted_idx]
        w_cumsum = np.cumsum(w_sorted) / w_sorted.sum()

        percs = {}
        for p in [10, 25, 50, 75, 90, 99]:
            idx = np.searchsorted(w_cumsum, p / 100.0)
            idx = min(idx, len(d_sorted) - 1)
            percs[p] = d_sorted[idx]

        wmean = np.average(d_arr, weights=w_arr)
        wstd = np.sqrt(np.average((d_arr - wmean)**2, weights=w_arr))
        log(f"L{li:<5d} | {percs[10]:6.0f} {percs[25]:6.0f} {percs[50]:6.0f} {percs[75]:6.0f} {percs[90]:6.0f} {percs[99]:6.0f} | {wmean:6.1f} {wstd:6.1f}")

    # ── 2. By head type at L30 ──
    log("\n── 2. Weighted distance percentiles by head type at L30 ──")
    log(f"{'Type':>12s} | {'p10':>6s} {'p25':>6s} {'p50':>6s} {'p75':>6s} {'p90':>6s} | {'mean':>6s}")
    log("-" * 72)
    for htype in ["very_sparse", "sparse", "moderate", "semi_dense", "dense"]:
        dists, weights = dist_weight_by[(30, htype)]
        if not dists:
            continue
        d_arr = np.array(dists, dtype=float)
        w_arr = np.array(weights, dtype=float)

        sorted_idx = np.argsort(d_arr)
        d_sorted = d_arr[sorted_idx]
        w_sorted = w_arr[sorted_idx]
        w_cumsum = np.cumsum(w_sorted) / w_sorted.sum()

        percs = {}
        for p in [10, 25, 50, 75, 90]:
            idx = np.searchsorted(w_cumsum, p / 100.0)
            idx = min(idx, len(d_sorted) - 1)
            percs[p] = d_sorted[idx]

        wmean = np.average(d_arr, weights=w_arr)
        log(f"{htype:>12s} | {percs[10]:6.0f} {percs[25]:6.0f} {percs[50]:6.0f} {percs[75]:6.0f} {percs[90]:6.0f} | {wmean:6.1f}")

    # ── 3. Power law fit ──
    log("\n── 3. Distribution fitting (L30, all heads) ──")
    dists_30, weights_30 = dist_weight_by_layer[30]
    d_arr = np.array(dists_30, dtype=float)
    w_arr = np.array(weights_30, dtype=float)

    # Only non-zero distances for log fitting
    nonzero = d_arr > 0
    d_nz = d_arr[nonzero]
    w_nz = w_arr[nonzero]

    # Build weighted histogram (distance → total attention mass)
    max_d = int(d_nz.max()) + 1
    dist_histogram = np.zeros(max_d)
    for d, w in zip(d_nz, w_nz):
        dist_histogram[int(d)] += w

    # Normalize
    dist_histogram /= dist_histogram.sum()

    # Print histogram for first 40 distances
    log("\n  Distance histogram (L30, attention mass per distance):")
    log(f"  {'dist':>4s} {'mass':>8s} {'cum':>8s} {'bar'}")
    log("  " + "-" * 60)
    cumulative = 0.0
    for d in range(min(40, max_d)):
        mass = dist_histogram[d]
        cumulative += mass
        bar = "█" * int(mass * 200)
        if mass > 0.001:
            log(f"  {d:4d} {mass:8.4f} {cumulative:8.4f} {bar}")

    log(f"\n  Distances beyond 40: {1.0 - cumulative:.4f} remaining mass")

    # Fit: power law P(d) ∝ d^(-α) on weighted data
    if len(d_nz) > 10:
        log_d = np.log(d_nz)
        log_w = np.log(w_nz)
        # Weighted linear regression: log(weight) = -α·log(d) + const
        # Use weight itself as regression weight for emphasis on high-attention
        slope, intercept, r, p, se = sp_stats.linregress(log_d, log_w)
        alpha = -slope
        log(f"\n  Power law fit: weight ∝ d^(-{alpha:.3f}), R²={r**2:.4f}")

        # Also fit on the histogram (mass at each distance)
        hist_d = np.arange(1, max_d, dtype=float)
        hist_m = dist_histogram[1:]
        nonzero_hist = hist_m > 0
        if nonzero_hist.sum() > 5:
            slope_h, intercept_h, r_h, _, _ = sp_stats.linregress(
                np.log(hist_d[nonzero_hist]), np.log(hist_m[nonzero_hist])
            )
            alpha_h = -slope_h
            log(f"  Histogram fit: mass(d) ∝ d^(-{alpha_h:.3f}), R²={r_h**2:.4f}")

        # Fit exponential: P(d) ∝ exp(-λd)
        slope_e, intercept_e, r_e, _, _ = sp_stats.linregress(d_nz, log_w)
        lam = -slope_e
        log(f"  Exponential fit: weight ∝ exp(-{lam:.4f}·d), R²={r_e**2:.4f}")

    # ── 4. Optimal stride design ──
    log("\n── 4. Optimal stride design (greedy, L30) ──")

    d_all_30 = np.array(dists_30, dtype=np.int32)
    w_all_30 = np.array(weights_30, dtype=float)

    # Current design: powers of 2
    pow2_strides = [2**i for i in range(16)]
    cov_pow2 = compute_coverage_for_strides(pow2_strides, 8, d_all_30, w_all_30, radius=0)
    cov_pow2_r2 = compute_coverage_for_strides(pow2_strides, 8, d_all_30, w_all_30, radius=2)
    log(f"  Powers of 2 (current): {cov_pow2:.1%} exact, {cov_pow2_r2:.1%} with ±2")

    # Greedy optimal: exact
    opt_strides, opt_cov = design_optimal_strides(d_all_30, w_all_30, n_strides=16, window=8, radius=0)
    log(f"  Greedy optimal (exact): {opt_cov:.1%}")
    log(f"    Strides: {opt_strides}")

    # Greedy optimal: with ±2 neighbors
    opt_strides_r2, opt_cov_r2 = design_optimal_strides(d_all_30, w_all_30, n_strides=16, window=8, radius=2)
    log(f"  Greedy optimal (±2):   {opt_cov_r2:.1%}")
    log(f"    Strides: {opt_strides_r2}")

    # What about fewer strides?
    log("\n  Coverage vs number of strides (greedy optimal, exact):")
    for n in [4, 6, 8, 10, 12, 16]:
        s, c = design_optimal_strides(d_all_30, w_all_30, n_strides=n, window=8, radius=0)
        log(f"    {n:2d} strides: {c:.1%} — {s}")

    log("\n  Coverage vs number of strides (greedy optimal, ±2):")
    for n in [4, 6, 8, 10, 12, 16]:
        s, c = design_optimal_strides(d_all_30, w_all_30, n_strides=n, window=8, radius=2)
        log(f"    {n:2d} strides: {c:.1%} — {s}")

    # ── 5. Fibonacci strides ──
    log("\n── 5. Special stride patterns ──")

    # Fibonacci
    fib = [1, 1]
    while fib[-1] < 32768:
        fib.append(fib[-1] + fib[-2])
    fib = sorted(set(fib))[:16]
    cov_fib = compute_coverage_for_strides(fib, 8, d_all_30, w_all_30, radius=0)
    cov_fib_r2 = compute_coverage_for_strides(fib, 8, d_all_30, w_all_30, radius=2)
    log(f"  Fibonacci: {cov_fib:.1%} exact, {cov_fib_r2:.1%} ±2 — {fib}")

    # Powers of phi
    phi_strides = sorted(set(max(1, round(PHI**i)) for i in range(20)))[:16]
    cov_phi = compute_coverage_for_strides(phi_strides, 8, d_all_30, w_all_30, radius=0)
    cov_phi_r2 = compute_coverage_for_strides(phi_strides, 8, d_all_30, w_all_30, radius=2)
    log(f"  Powers of φ: {cov_phi:.1%} exact, {cov_phi_r2:.1%} ±2 — {phi_strides}")

    # Dense near, sparse far: 1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,1597
    dense_near = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597]
    cov_dn = compute_coverage_for_strides(dense_near, 8, d_all_30, w_all_30, radius=0)
    cov_dn_r2 = compute_coverage_for_strides(dense_near, 8, d_all_30, w_all_30, radius=2)
    log(f"  Dense-near:  {cov_dn:.1%} exact, {cov_dn_r2:.1%} ±2 — {dense_near}")

    # Consecutive (1-16) — maximum local density
    consec = list(range(1, 17))
    cov_con = compute_coverage_for_strides(consec, 8, d_all_30, w_all_30, radius=0)
    cov_con_r2 = compute_coverage_for_strides(consec, 8, d_all_30, w_all_30, radius=2)
    log(f"  Consecutive: {cov_con:.1%} exact, {cov_con_r2:.1%} ±2 — {consec}")

    # ── 6. Per head-type optimal strides at L30 ──
    log("\n── 6. Per head-type analysis at L30 ──")
    for htype in ["very_sparse", "sparse", "moderate", "semi_dense", "dense"]:
        dists, weights = dist_weight_by[(30, htype)]
        if not dists:
            continue
        d_arr = np.array(dists, dtype=np.int32)
        w_arr = np.array(weights, dtype=float)

        cov_p2 = compute_coverage_for_strides(pow2_strides, 8, d_arr, w_arr, radius=0)
        cov_p2_r2 = compute_coverage_for_strides(pow2_strides, 8, d_arr, w_arr, radius=2)
        opt_s, opt_c = design_optimal_strides(d_arr, w_arr, n_strides=16, window=8, radius=0)
        opt_s_r2, opt_c_r2 = design_optimal_strides(d_arr, w_arr, n_strides=16, window=8, radius=2)

        log(f"\n  {htype}:")
        log(f"    Powers of 2:    {cov_p2:.1%} exact, {cov_p2_r2:.1%} ±2")
        log(f"    Greedy optimal: {opt_c:.1%} exact, {opt_c_r2:.1%} ±2")
        log(f"    Optimal strides: {opt_s}")

        # Distance stats
        wmean = np.average(d_arr.astype(float), weights=w_arr)
        log(f"    Weighted mean distance: {wmean:.1f}")

    # ══════════════════════════════════════════════════════════════
    # SAVE RESULTS
    # ══════════════════════════════════════════════════════════════

    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "results", "binding-distance-distribution")
    os.makedirs(out_dir, exist_ok=True)

    # Save histogram
    hist_path = os.path.join(out_dir, "distance_histogram_L30.json")
    with open(hist_path, "w") as f:
        json.dump({
            "layer": 30,
            "histogram": dist_histogram.tolist(),
            "max_distance": max_d,
        }, f, indent=2)
    log(f"\n  Histogram: {hist_path}")

    # Save summary
    summary = {
        "model": model_id,
        "n_probes": len(PROBES),
        "layer_indices": layer_indices,
        "pow2_coverage_exact": cov_pow2,
        "pow2_coverage_r2": cov_pow2_r2,
        "optimal_strides_exact": opt_strides,
        "optimal_coverage_exact": opt_cov,
        "optimal_strides_r2": opt_strides_r2,
        "optimal_coverage_r2": opt_cov_r2,
        "fibonacci_coverage_exact": cov_fib,
        "fibonacci_coverage_r2": cov_fib_r2,
        "phi_coverage_exact": cov_phi,
        "phi_coverage_r2": cov_phi_r2,
    }

    # Per head-type summaries
    summary["per_head_type"] = {}
    for htype in HEAD_TAXONOMY:
        dists, weights = dist_weight_by[(30, htype)]
        if dists:
            d_arr = np.array(dists, dtype=np.int32)
            w_arr = np.array(weights, dtype=float)
            opt_s, opt_c = design_optimal_strides(d_arr, w_arr, n_strides=16, window=8, radius=0)
            summary["per_head_type"][htype] = {
                "optimal_strides": opt_s,
                "optimal_coverage": opt_c,
                "pow2_coverage": compute_coverage_for_strides(pow2_strides, 8, d_arr, w_arr, radius=0),
                "mean_distance": float(np.average(d_arr.astype(float), weights=w_arr)),
            }

    sum_path = os.path.join(out_dir, "summary.json")
    with open(sum_path, "w") as f:
        json.dump(summary, f, indent=2)
    log(f"  Summary: {sum_path}")

    log("\n" + "=" * 72)
    log("BINDING DISTANCE DISTRIBUTION COMPLETE")
    log("=" * 72)

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", type=str, default=None)
    args = parser.parse_args()

    layers = None
    if args.layers:
        layers = [int(x.strip()) for x in args.layers.split(",")]

    run_experiment(model_id=args.model, layer_indices=layers)
