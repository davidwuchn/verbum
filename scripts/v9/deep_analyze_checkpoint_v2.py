"""
Deep analysis of basin projector v2 checkpoint — per-word, per-type, operator dispatch.

Adapted from deep_analyze_checkpoint.py for v2 (d=512, gamma-only, no evolution).

Usage:
    uv run python scripts/v9/deep_analyze_checkpoint_v2.py checkpoints/basin-v2-d512/step_016000
    uv run python scripts/v9/deep_analyze_checkpoint_v2.py checkpoints/basin-v2-d512/step_016000 \
        --d-model 512 --d-basin 512 --n-heads 16

Produces: results/basin-analysis/v2_step_NNNNNN.json + human-readable summary.

License: MIT
"""

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

# ── constants ────────────────────────────────────────────────────
STRATA = ["sexpr", "math", "prose", "behavioral", "complex", "mixed"]

# Eval shards: last 8 of 160
N_SHARDS = 160
EVAL_SHARDS = 8
SHARD_DIR = Path(__file__).parent.parent.parent / "results" / "oracle-data"

# Kernel ops (from session 056 probe_kernel_basins.py)
KERNEL_OP_WORDS = {
    "add": ["add", "plus", "sum", "addition", "+"],
    "sub": ["subtract", "minus", "difference", "-"],
    "mul": ["multiply", "times", "product", "*", "×"],
    "div": ["divide", "quotient", "÷", "/", "//"],
    "mod": ["modulo", "remainder", "mod", "%"],
    "abs": ["absolute", "abs", "magnitude"],
    "neg": ["negate", "negation", "negative"],
    "eq":  ["equals", "equal", "=", "=="],
    "lt":  ["less", "<"],
    "gt":  ["greater", ">"],
    "min": ["minimum", "min", "smallest", "least"],
    "max": ["maximum", "max", "largest", "greatest"],
    "and": ["and", "both", "conjunction"],
    "or":  ["or", "either", "disjunction"],
    "not": ["not", "negation", "complement"],
    "if":  ["if", "then", "condition", "conditional"],
    "apply": ["apply", "call", "invoke"],
    "compose": ["compose", "composition", "chain"],
    "partial": ["partial", "bind", "curry"],
}

# Semantic type categories for basin separation analysis
WORD_TYPE_CATEGORIES = {
    "number": lambda w: w.strip(".,;:!?").replace("-", "").replace("+", "").isdigit(),
    "operator": lambda w: w.strip() in {"+", "-", "*", "/", "×", "÷", "=", "==",
                                          "<", ">", "<=", ">=", "%", "//", "(", ")"},
    "parenthesis": lambda w: w.strip() in {"(", ")"},
    "article": lambda w: w.lower().strip(".,;:!?") in {"the", "a", "an"},
    "preposition": lambda w: w.lower().strip(".,;:!?") in {
        "of", "in", "to", "for", "with", "by", "from", "at", "on", "as", "into"},
    "verb": lambda w: w.lower().strip(".,;:!?") in {
        "is", "are", "was", "were", "be", "have", "has", "had", "do", "does",
        "calculate", "compute", "evaluate", "find", "determine", "analyze",
        "summarize", "add", "subtract", "multiply", "divide", "compare",
        "apply", "compose", "combine", "transform", "reduce", "map"},
    "sexpr_keyword": lambda w: w.strip() in {
        "+", "-", "*", "/", "//", "%", "abs", "neg", "min", "max",
        "and", "or", "not", "if", "eq", "lt", "gt", "le", "ge",
        "apply", "compose", "partial", "lambda"},
}


def load_model_and_eval_data(d_model: int, d_basin: int, n_heads: int):
    """Load the basin projector v2 model infrastructure."""
    sys.path.insert(0, str(Path(__file__).parent))
    sys.path.insert(0, str(Path(__file__).parent.parent / "v8"))

    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim

    from basin_model import BasinProjector, BasinConfig
    from train_basin_v2 import (
        PCAProjector, OracleDataLoader, load_checkpoint,
        cosine_loss,
    )
    from ternary import zero_ternary_grads, restore_ternary, freeze_ternary_weights

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-32B")

    pca_path = SHARD_DIR / f"pca_projector_{d_basin}.npz"
    if not pca_path.exists():
        # Fall back to default name
        pca_path = SHARD_DIR / "pca_projector.npz"
    pca = PCAProjector(pca_path)
    print(f"  PCA: {pca_path.name}, d_basin={pca.d_basin}")

    eval_shards = list(range(N_SHARDS - EVAL_SHARDS, N_SHARDS))
    eval_loader = OracleDataLoader(
        SHARD_DIR, pca, tokenizer, eval_shards,
        batch_size=32, max_seq_len=128, seed=99,
    )

    config = BasinConfig(
        d_model=d_model,
        d_basin=d_basin,
        n_heads=n_heads,
        max_seq_len=128,
    )
    model = BasinProjector(config)
    print(f"  Config: d_model={d_model}, d_basin={d_basin}, n_heads={n_heads}")

    # Freeze ternary weights before optimizer interaction
    n_frozen = freeze_ternary_weights(model)

    optimizer = optim.AdamW(learning_rate=3e-4)

    # Dummy init
    def loss_fn(m, ids, spans, targets, mask):
        pred, pred_mask = m(ids, spans)
        return cosine_loss(pred, targets, mask)

    _lfg = nn.value_and_grad(model, loss_fn)
    d = eval_loader.next_batch()
    _lv, _g = _lfg(model, d[0], d[1], d[2], d[3])
    mx.eval(_lv, _g)
    _g = zero_ternary_grads(model, _g)
    optimizer.update(model, _g)
    mx.eval(model.parameters(), optimizer.state)
    restore_ternary(model)
    eval_loader.reset()

    return model, optimizer, eval_loader, pca, tokenizer, mx, freeze_ternary_weights, load_checkpoint


def collect_with_word_texts(model, eval_loader, pca, tokenizer, mx, n_batches: int = 32):
    """Collect predictions WITH word texts by loading shards directly."""
    eval_loader.reset()

    results = []
    for batch_idx in range(n_batches):
        data = eval_loader.next_batch()
        token_ids, word_spans, target_basins, word_mask, strata = data

        pred_basins, pred_mask = model(token_ids, word_spans)
        mx.eval(pred_basins)

        pred_np = np.array(pred_basins)
        target_np = np.array(target_basins)
        mask_np = np.array(word_mask)

        B = token_ids.shape[0]
        token_ids_np = np.array(token_ids)

        for b in range(B):
            n_words = int(mask_np[b].sum())
            if n_words == 0:
                continue

            spans_b = word_spans[b]
            ids_b = token_ids_np[b]

            for w in range(min(n_words, len(spans_b))):
                span = spans_b[w]
                span_ids = [int(ids_b[i]) for i in span if i < len(ids_b)]
                word_text = tokenizer.decode(span_ids, skip_special_tokens=True).strip()

                p = pred_np[b, w]
                t = target_np[b, w]
                # L2-normalize before dot for cosine sim (should already be normed, but safe)
                p_norm = np.linalg.norm(p)
                t_norm = np.linalg.norm(t)
                if p_norm > 0 and t_norm > 0:
                    sim = float(np.dot(p / p_norm, t / t_norm))
                else:
                    sim = 0.0

                results.append({
                    "word": word_text,
                    "stratum": strata[b],
                    "pred_basin": p,
                    "target_basin": t,
                    "cosine_sim": sim,
                })

    return results


def analyze_sim_distribution(results: list[dict]) -> dict:
    """1. Per-word cosine similarity distribution."""
    sims = np.array([r["cosine_sim"] for r in results])

    bins = {
        "above_0.9": int(np.sum(sims > 0.9)),
        "0.8_to_0.9": int(np.sum((sims > 0.8) & (sims <= 0.9))),
        "0.7_to_0.8": int(np.sum((sims > 0.7) & (sims <= 0.8))),
        "0.6_to_0.7": int(np.sum((sims > 0.6) & (sims <= 0.7))),
        "0.4_to_0.6": int(np.sum((sims > 0.4) & (sims <= 0.6))),
        "0.2_to_0.4": int(np.sum((sims > 0.2) & (sims <= 0.4))),
        "below_0.2": int(np.sum(sims <= 0.2)),
    }

    return {
        "n_words": len(sims),
        "mean": float(sims.mean()),
        "std": float(sims.std()),
        "median": float(np.median(sims)),
        "p10": float(np.percentile(sims, 10)),
        "p25": float(np.percentile(sims, 25)),
        "p75": float(np.percentile(sims, 75)),
        "p90": float(np.percentile(sims, 90)),
        "min": float(sims.min()),
        "max": float(sims.max()),
        "histogram": bins,
    }


def analyze_per_stratum(results: list[dict]) -> dict:
    """2. Per-stratum word-level breakdown."""
    by_stratum = defaultdict(list)
    for r in results:
        by_stratum[r["stratum"]].append(r["cosine_sim"])

    analysis = {}
    for s in STRATA:
        if s not in by_stratum:
            continue
        sims = np.array(by_stratum[s])
        analysis[s] = {
            "n_words": len(sims),
            "mean": float(sims.mean()),
            "std": float(sims.std()),
            "median": float(np.median(sims)),
            "p10": float(np.percentile(sims, 10)),
            "p90": float(np.percentile(sims, 90)),
            "above_0.8": int(np.sum(sims > 0.8)),
            "below_0.4": int(np.sum(sims < 0.4)),
        }
    return analysis


def analyze_best_worst_words(results: list[dict], top_n: int = 15) -> dict:
    """3. Best/worst words per stratum."""
    by_stratum = defaultdict(list)
    for r in results:
        by_stratum[r["stratum"]].append((r["word"], r["cosine_sim"]))

    analysis = {}
    for s in STRATA:
        if s not in by_stratum:
            continue
        pairs = by_stratum[s]
        pairs.sort(key=lambda x: x[1], reverse=True)

        seen_best = set()
        best = []
        for word, sim in pairs:
            wl = word.lower().strip(".,;:!?")
            if wl not in seen_best:
                seen_best.add(wl)
                best.append({"word": word, "sim": round(sim, 4)})
            if len(best) >= top_n:
                break

        seen_worst = set()
        worst = []
        for word, sim in reversed(pairs):
            wl = word.lower().strip(".,;:!?")
            if wl not in seen_worst:
                seen_worst.add(wl)
                worst.append({"word": word, "sim": round(sim, 4)})
            if len(worst) >= top_n:
                break

        analysis[s] = {"best": best, "worst": worst}

    return analysis


def analyze_context_dependent_words(results: list[dict]) -> dict:
    """3b. Specifically analyze words known to be context-dependent from v1 analysis.

    These words failed in v1 due to PCA d=64 collapsing their context spread.
    At d=512, 98% of context spread should be preserved.
    """
    # Words that failed systematically in v1 (from state.md session 060 analysis)
    context_dep_words = {
        "is": "copula vs identity — worst in v1 (0.22)",
        "a": "article vs variable — v1 (0.24)",
        "of": "preposition — v1 (0.33)",
        "product": "math op vs noun — v1 (0.26)",
        "range": "math op vs noun — v1 (0.23)",
        "that": "pronoun vs complementizer",
        "it": "pronoun — context-dependent",
    }
    # Words that excelled in v1
    context_inv_words = {
        "Every": "quantifier — v1 (>0.99)",
        "Some": "quantifier — v1 (>0.99)",
        "Each": "quantifier — v1 (>0.99)",
        "Translate": "imperative — v1 (>0.99)",
        "Compute": "imperative — v1 (>0.99)",
    }

    # Collect all instances
    dep_results = defaultdict(list)
    inv_results = defaultdict(list)

    for r in results:
        w = r["word"].lower().strip(".,;:!?")
        if w in context_dep_words:
            dep_results[w].append(r["cosine_sim"])
        # Case-insensitive match for invariant words
        w_orig = r["word"].strip(".,;:!?")
        if w_orig in context_inv_words or w in {k.lower() for k in context_inv_words}:
            inv_results[w].append(r["cosine_sim"])

    dep_analysis = {}
    for word, sims in dep_results.items():
        arr = np.array(sims)
        dep_analysis[word] = {
            "n": len(arr),
            "mean": round(float(arr.mean()), 4),
            "std": round(float(arr.std()), 4),
            "min": round(float(arr.min()), 4),
            "max": round(float(arr.max()), 4),
            "v1_note": context_dep_words[word],
        }

    inv_analysis = {}
    for word, sims in inv_results.items():
        arr = np.array(sims)
        inv_analysis[word] = {
            "n": len(arr),
            "mean": round(float(arr.mean()), 4),
            "std": round(float(arr.std()), 4),
            "min": round(float(arr.min()), 4),
            "max": round(float(arr.max()), 4),
        }

    return {
        "context_dependent": dep_analysis,
        "context_invariant": inv_analysis,
    }


def analyze_basin_separation(results: list[dict]) -> dict:
    """4. Do predicted basins separate word types?"""
    categorized = defaultdict(list)
    uncategorized = []

    for r in results:
        word = r["word"]
        assigned = False
        for cat_name, cat_fn in WORD_TYPE_CATEGORIES.items():
            try:
                if cat_fn(word):
                    categorized[cat_name].append(r["pred_basin"])
                    assigned = True
                    break
            except Exception:
                pass
        if not assigned:
            uncategorized.append(r["pred_basin"])

    type_centroids = {}
    within_sims = {}

    for cat, vecs in categorized.items():
        if len(vecs) < 5:
            continue
        vecs_np = np.array(vecs)
        # L2-normalize
        norms = np.linalg.norm(vecs_np, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-8)
        vecs_np = vecs_np / norms

        centroid = vecs_np.mean(axis=0)
        norm = np.linalg.norm(centroid)
        if norm > 0:
            centroid = centroid / norm
        type_centroids[cat] = centroid

        n = len(vecs_np)
        if n > 200:
            idx = np.random.choice(n, 200, replace=False)
            sample = vecs_np[idx]
        else:
            sample = vecs_np
        sim_matrix = sample @ sample.T
        mask = np.triu(np.ones(len(sample), dtype=bool), k=1)
        within_sims[cat] = float(sim_matrix[mask].mean())

    cats = sorted(type_centroids.keys())
    between = {}
    for i, c1 in enumerate(cats):
        for c2 in cats[i+1:]:
            sim = float(np.dot(type_centroids[c1], type_centroids[c2]))
            between[f"{c1}_vs_{c2}"] = round(sim, 4)

    # Compute separation ratios: within / |between| for each type
    separation_ratios = {}
    for cat in cats:
        if cat not in within_sims:
            continue
        # Mean |between| for this type
        btw_vals = []
        for pair, sim in between.items():
            if cat in pair:
                btw_vals.append(abs(sim))
        if btw_vals:
            mean_btw = np.mean(btw_vals)
            if mean_btw > 0.01:
                separation_ratios[cat] = round(within_sims[cat] / mean_btw, 2)

    return {
        "n_categorized": {cat: len(vecs) for cat, vecs in categorized.items() if len(vecs) >= 5},
        "n_uncategorized": len(uncategorized),
        "within_type_sim": {cat: round(v, 4) for cat, v in within_sims.items()},
        "between_type_sim": between,
        "separation_ratios": separation_ratios,
        "type_centroids_computed": cats,
    }


def analyze_operator_dispatch(results: list[dict]) -> dict:
    """5. Operator dispatch quality."""
    word_to_op = {}
    for op, words in KERNEL_OP_WORDS.items():
        for w in words:
            word_to_op[w.lower()] = op

    op_vecs = defaultdict(list)
    op_target_vecs = defaultdict(list)

    for r in results:
        w = r["word"].lower().strip(".,;:!?")
        if w in word_to_op:
            op = word_to_op[w]
            op_vecs[op].append(r["pred_basin"])
            op_target_vecs[op].append(r["target_basin"])

    op_centroids = {}
    within_op = {}

    for op, vecs in op_vecs.items():
        if len(vecs) < 2:
            continue
        vecs_np = np.array(vecs)
        norms = np.linalg.norm(vecs_np, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-8)
        vecs_np = vecs_np / norms

        centroid = vecs_np.mean(axis=0)
        norm = np.linalg.norm(centroid)
        if norm > 0:
            centroid = centroid / norm
        op_centroids[op] = centroid

        if len(vecs) >= 3:
            sim_matrix = vecs_np @ vecs_np.T
            mask = np.triu(np.ones(len(vecs_np), dtype=bool), k=1)
            within_op[op] = float(sim_matrix[mask].mean())

    ops = sorted(op_centroids.keys())
    between_op = {}
    for i, o1 in enumerate(ops):
        for o2 in ops[i+1:]:
            sim = float(np.dot(op_centroids[o1], op_centroids[o2]))
            between_op[f"{o1}_vs_{o2}"] = round(sim, 4)

    # Super-basin check
    super_basins = {
        "functional": ["add", "sub", "mul", "div", "and", "or", "not", "if",
                        "apply", "compose", "partial", "neg"],
        "comparison": ["eq", "lt", "gt"],
        "extremum": ["abs", "min", "max", "mod"],
    }
    super_within = {}
    super_centroids = {}
    for sb_name, sb_ops in super_basins.items():
        sb_vecs = []
        for op in sb_ops:
            if op in op_vecs:
                sb_vecs.extend(op_vecs[op])
        if len(sb_vecs) >= 3:
            vecs_np = np.array(sb_vecs)
            norms = np.linalg.norm(vecs_np, axis=1, keepdims=True)
            norms = np.maximum(norms, 1e-8)
            vecs_np = vecs_np / norms

            centroid = vecs_np.mean(axis=0)
            norm = np.linalg.norm(centroid)
            if norm > 0:
                centroid = centroid / norm
            super_centroids[sb_name] = centroid

            sim_matrix = vecs_np @ vecs_np.T
            mask = np.triu(np.ones(len(vecs_np), dtype=bool), k=1)
            super_within[sb_name] = float(sim_matrix[mask].mean())

    super_between = {}
    sb_names = sorted(super_centroids.keys())
    for i, s1 in enumerate(sb_names):
        for s2 in sb_names[i+1:]:
            sim = float(np.dot(super_centroids[s1], super_centroids[s2]))
            super_between[f"{s1}_vs_{s2}"] = round(sim, 4)

    return {
        "op_word_counts": {op: len(vecs) for op, vecs in op_vecs.items()},
        "within_op_sim": {op: round(v, 4) for op, v in within_op.items()},
        "between_op_sim_sample": dict(list(sorted(between_op.items(),
                                                   key=lambda x: x[1]))[:15]),
        "super_basin_within": {k: round(v, 4) for k, v in super_within.items()},
        "super_basin_between": super_between,
    }


def analyze_cross_stratum(results: list[dict]) -> dict:
    """6. Cross-stratum basin agreement for same words."""
    word_stratum_vecs = defaultdict(lambda: defaultdict(list))
    for r in results:
        w = r["word"].lower().strip(".,;:!?")
        word_stratum_vecs[w][r["stratum"]].append(r["pred_basin"])

    cross_words = {}
    for word, stratum_vecs in word_stratum_vecs.items():
        strata_present = sorted(stratum_vecs.keys())
        if len(strata_present) >= 2:
            centroids = {}
            for s in strata_present:
                vecs = np.array(stratum_vecs[s])
                norms = np.linalg.norm(vecs, axis=1, keepdims=True)
                norms = np.maximum(norms, 1e-8)
                vecs = vecs / norms
                c = vecs.mean(axis=0)
                norm = np.linalg.norm(c)
                if norm > 0:
                    c = c / norm
                centroids[s] = c

            sims = {}
            for i, s1 in enumerate(strata_present):
                for s2 in strata_present[i+1:]:
                    sims[f"{s1}_vs_{s2}"] = round(
                        float(np.dot(centroids[s1], centroids[s2])), 4)

            cross_words[word] = {
                "strata": strata_present,
                "counts": {s: len(stratum_vecs[s]) for s in strata_present},
                "cross_sim": sims,
            }

    pair_sims = defaultdict(list)
    for word, info in cross_words.items():
        for pair, sim in info["cross_sim"].items():
            pair_sims[pair].append(sim)

    pair_summary = {}
    for pair, sims in sorted(pair_sims.items()):
        arr = np.array(sims)
        pair_summary[pair] = {
            "mean": round(float(arr.mean()), 4),
            "std": round(float(arr.std()), 4),
            "n_words": len(arr),
        }

    sexpr_math_words = []
    for word, info in cross_words.items():
        sim = info["cross_sim"].get("math_vs_sexpr") or info["cross_sim"].get("sexpr_vs_math")
        if sim is not None:
            sexpr_math_words.append((word, sim))
    sexpr_math_words.sort(key=lambda x: x[1], reverse=True)

    return {
        "n_cross_words": len(cross_words),
        "pair_summary": pair_summary,
        "sexpr_math_best": [{"word": w, "sim": s} for w, s in sexpr_math_words[:10]],
        "sexpr_math_worst": [{"word": w, "sim": s} for w, s in sexpr_math_words[-10:]],
    }


def print_summary(analysis: dict, d_basin: int):
    """Print human-readable summary."""
    noise_floor = 1.0 / np.sqrt(d_basin)
    ceiling = analysis.get("ceiling", 0.952)

    print(f"\n{'═' * 70}")
    print(f"  DEEP ANALYSIS v2 — Step {analysis['step']}  (d_basin={d_basin})")
    print(f"  noise_floor={noise_floor:.4f}  ceiling={ceiling}")
    print(f"{'═' * 70}")

    # 1. Distribution
    dist = analysis["sim_distribution"]
    h = dist["histogram"]
    total = dist["n_words"]
    print(f"\n  ① Cosine Similarity Distribution ({total} words)")
    print(f"     mean={dist['mean']:.3f}  std={dist['std']:.3f}  "
          f"median={dist['median']:.3f}  [p10={dist['p10']:.3f}, p90={dist['p90']:.3f}]")
    print(f"     min={dist['min']:.3f}  max={dist['max']:.3f}")
    pct_of_ceiling = dist['mean'] / ceiling * 100 if ceiling > 0 else 0
    print(f"     mean/ceiling = {pct_of_ceiling:.1f}%")
    print()
    for label, count in h.items():
        pct = count / total * 100
        bar = "█" * int(pct / 2)
        print(f"     {label:>12s}: {count:5d} ({pct:5.1f}%) {bar}")

    # 2. Per-stratum
    print(f"\n  ② Per-Stratum Breakdown")
    ps = analysis["per_stratum"]
    for s in STRATA:
        if s not in ps:
            continue
        d = ps[s]
        print(f"     {s:12s}: mean={d['mean']:.3f}  std={d['std']:.3f}  "
              f"[p10={d['p10']:.3f}, p90={d['p90']:.3f}]  "
              f">0.8: {d['above_0.8']:3d}  <0.4: {d['below_0.4']:3d}")

    # 3. Best/worst words
    print(f"\n  ③ Best/Worst Words per Stratum")
    bw = analysis["best_worst_words"]
    for s in STRATA:
        if s not in bw:
            continue
        best = bw[s]["best"][:8]
        worst = bw[s]["worst"][:8]
        best_str = "  ".join(f"{w['word']}({w['sim']:.2f})" for w in best)
        worst_str = "  ".join(f"{w['word']}({w['sim']:.2f})" for w in worst)
        print(f"     {s}:")
        print(f"       BEST:  {best_str}")
        print(f"       WORST: {worst_str}")

    # 3b. Context-dependent words
    print(f"\n  ③b Context-Dependent Words (v1 bottleneck)")
    cdw = analysis["context_dependent_words"]
    print(f"     Context-DEPENDENT (should improve with d=512):")
    for word, info in sorted(cdw["context_dependent"].items(), key=lambda x: x[1]["mean"]):
        print(f"       {word:12s}: mean={info['mean']:.3f} ±{info['std']:.3f}  "
              f"[{info['min']:.3f}, {info['max']:.3f}]  n={info['n']}  |  {info['v1_note']}")
    print(f"     Context-INVARIANT (should remain high):")
    for word, info in sorted(cdw["context_invariant"].items(), key=lambda x: -x[1]["mean"]):
        print(f"       {word:12s}: mean={info['mean']:.3f} ±{info['std']:.3f}  "
              f"[{info['min']:.3f}, {info['max']:.3f}]  n={info['n']}")

    # 4. Basin separation
    print(f"\n  ④ Predicted Basin Type Separation")
    sep = analysis["basin_separation"]
    print(f"     Categorized types: {sep['n_categorized']}")
    print(f"     Uncategorized words: {sep['n_uncategorized']}")
    print(f"\n     Within-type similarity (higher = tighter clusters):")
    for cat, sim in sorted(sep["within_type_sim"].items(), key=lambda x: -x[1]):
        ratio = sep["separation_ratios"].get(cat, "—")
        print(f"       {cat:15s}: {sim:+.4f}  sep_ratio={ratio}")
    print(f"\n     Between-type similarity (lower = better separation):")
    between = sorted(sep["between_type_sim"].items(), key=lambda x: x[1])
    for pair, sim in between[:10]:
        print(f"       {pair:30s}: {sim:+.4f}")
    if len(between) > 15:
        print(f"       ...")
    for pair, sim in between[-5:]:
        print(f"       {pair:30s}: {sim:+.4f}")

    # 5. Operator dispatch
    print(f"\n  ⑤ Operator Dispatch Quality")
    od = analysis["operator_dispatch"]
    print(f"     Op word counts: {od['op_word_counts']}")
    if od["within_op_sim"]:
        print(f"\n     Within-op similarity:")
        for op, sim in sorted(od["within_op_sim"].items(), key=lambda x: -x[1]):
            print(f"       {op:12s}: {sim:+.4f}")
    if od["super_basin_within"]:
        print(f"\n     Super-basin within (session 056 hierarchy):")
        for sb, sim in od["super_basin_within"].items():
            print(f"       {sb:12s}: {sim:+.4f}")
    if od["super_basin_between"]:
        print(f"     Super-basin between:")
        for pair, sim in od["super_basin_between"].items():
            print(f"       {pair:30s}: {sim:+.4f}")

    # 6. Cross-stratum
    print(f"\n  ⑥ Cross-Stratum Agreement")
    cs = analysis["cross_stratum"]
    print(f"     Words appearing in ≥2 strata: {cs['n_cross_words']}")
    if cs["pair_summary"]:
        print(f"\n     Pair-wise mean similarity (same word, different stratum):")
        for pair, info in sorted(cs["pair_summary"].items(), key=lambda x: -x[1]["mean"]):
            print(f"       {pair:30s}: {info['mean']:+.4f} ±{info['std']:.3f}  (n={info['n_words']})")

    if cs.get("sexpr_math_best"):
        print(f"\n     S-expr ↔ Math best agreement:")
        for w in cs["sexpr_math_best"][:5]:
            print(f"       {w['word']:15s}: {w['sim']:+.4f}")
    if cs.get("sexpr_math_worst"):
        print(f"     S-expr ↔ Math worst agreement:")
        for w in cs["sexpr_math_worst"][:5]:
            print(f"       {w['word']:15s}: {w['sim']:+.4f}")

    print(f"\n{'═' * 70}")


def main():
    parser = argparse.ArgumentParser(description="Deep analysis of basin projector v2 checkpoint")
    parser.add_argument("checkpoint", type=str, help="Path to checkpoint directory")
    parser.add_argument("--d-model", type=int, default=512, help="d_model (default: 512)")
    parser.add_argument("--d-basin", type=int, default=512, help="d_basin (default: 512)")
    parser.add_argument("--n-heads", type=int, default=16, help="n_heads (default: 16)")
    parser.add_argument("--n-batches", type=int, default=32,
                        help="Number of eval batches (default: 32, ~1024 examples)")
    parser.add_argument("--top-n", type=int, default=15,
                        help="Number of best/worst words per stratum (default: 15)")
    args = parser.parse_args()

    checkpoint_path = Path(args.checkpoint)
    if not (checkpoint_path / "state.json").exists():
        print(f"Error: {checkpoint_path}/state.json not found")
        sys.exit(1)

    with open(checkpoint_path / "state.json") as f:
        state = json.load(f)
    step = state.get("step", 0)

    # Ceiling for d=512 PCA
    ceiling = 0.952

    print(f"Loading model and eval data (d_model={args.d_model}, d_basin={args.d_basin})...")
    t0 = time.time()
    model, optimizer, eval_loader, pca, tokenizer, mx, freeze_fn, load_ckpt = \
        load_model_and_eval_data(args.d_model, args.d_basin, args.n_heads)

    # Load checkpoint
    load_ckpt(checkpoint_path, model, optimizer)
    freeze_fn(model)
    t1 = time.time()
    print(f"  Model loaded in {t1-t0:.1f}s")

    print(f"Collecting per-word predictions ({args.n_batches} batches)...")
    results = collect_with_word_texts(model, eval_loader, pca, tokenizer, mx,
                                      n_batches=args.n_batches)
    t2 = time.time()
    print(f"  Collected {len(results)} words in {t2-t1:.1f}s")

    print(f"Running analyses...")

    analysis = {
        "step": step,
        "checkpoint": str(checkpoint_path),
        "n_words": len(results),
        "n_batches": args.n_batches,
        "d_model": args.d_model,
        "d_basin": args.d_basin,
        "n_heads": args.n_heads,
        "ceiling": ceiling,
    }

    analysis["sim_distribution"] = analyze_sim_distribution(results)
    analysis["per_stratum"] = analyze_per_stratum(results)
    analysis["best_worst_words"] = analyze_best_worst_words(results, top_n=args.top_n)
    analysis["context_dependent_words"] = analyze_context_dependent_words(results)
    analysis["basin_separation"] = analyze_basin_separation(results)
    analysis["operator_dispatch"] = analyze_operator_dispatch(results)
    analysis["cross_stratum"] = analyze_cross_stratum(results)

    t3 = time.time()
    print(f"  Analysis complete in {t3-t2:.1f}s")

    # Save results
    output_dir = Path(__file__).parent.parent.parent / "results" / "basin-analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"v2_step_{step:06d}.json"

    def make_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [make_serializable(v) for v in obj]
        return obj

    serializable = make_serializable(analysis)

    with open(output_path, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"\n  Saved: {output_path}")

    print_summary(analysis, args.d_basin)


if __name__ == "__main__":
    main()
