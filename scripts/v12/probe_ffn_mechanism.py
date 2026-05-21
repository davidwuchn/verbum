"""FFN Mechanism Probe — Discover how beta reductions are stored and activated.

Session 127. We know the crystal rotation geometry (L0=reset, L1=route,
L2=converge) and that routing/output circuits are separate. But we don't
know HOW individual FFN neurons implement specific beta reductions or
how the addressing mechanism selects them.

This probe uses minimal-pair inputs — expressions that differ by exactly
one beta reduction step — to reveal the FFN's mechanism:

  Experiment 1: Reduction signatures
    "K x y" vs "x" → the FFN delta IS the K-reduction signature
    Same for I, B, C → each combinator's reduction fingerprint

  Experiment 2: Key vs value separation
    Same reduction, different arguments:
      "K a b" vs "a", "K x y" vs "x", "K f g" vs "f"
    Common part = the key (K-reduction mechanism)
    Varying part = the value (argument-specific content)

  Experiment 3: Chain decomposition
    Nested: "K (I a) b" vs "I a" vs "a"
    Does the model compose signatures? Or use a separate "K∘I" function?

  Experiment 4: Position and layer analysis
    Which layers house which reduction types?
    Does the crystal rotation model predict the activation pattern?

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/probe_ffn_mechanism.py 2>&1 | tee results/ffn-mechanism/run.log

License: MIT
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, PAD_ID, BOS_ID, EOS_ID, EQ_ID,
    TOK2ID, ID2TOK,
    Expr, Var, App, Comb,
    reduce_one_step, full_reduce, count_reduction_steps,
    GDModel, HoloModel,
    generate_batch, masked_ce_loss, eval_model,
)

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "ffn-mechanism"
N_LAYERS = 3
MAX_SEQ = 40


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Tokenization helpers
# ══════════════════════════════════════════════════════════════════════

def expr_to_ids(expr: Expr, add_bos: bool = True, add_eq: bool = True) -> list[int]:
    """Convert expression to token IDs, padded to MAX_SEQ."""
    toks = expr.to_tokens()
    if not all(t in TOK2ID for t in toks):
        return None
    seq = []
    if add_bos:
        seq.append(BOS_ID)
    seq.extend(TOK2ID[t] for t in toks)
    if add_eq:
        seq.append(EQ_ID)
    # Pad
    if len(seq) > MAX_SEQ:
        return None
    seq = seq + [PAD_ID] * (MAX_SEQ - len(seq))
    return seq


def ids_to_str(ids: list[int]) -> str:
    """Convert token IDs back to readable string."""
    return " ".join(ID2TOK.get(i, "?") for i in ids if i != PAD_ID)


# ══════════════════════════════════════════════════════════════════════
# FFN activation capture — full layer-by-layer decomposition
# ══════════════════════════════════════════════════════════════════════

def capture_all_activations(model, ids: list[int]) -> dict:
    """Run forward pass, capture activations at every stage.

    Returns dict with:
      embedding: (MAX_SEQ, d_model)
      layers[i]:
        pre_attn_norm: (MAX_SEQ, d_model)
        attn_out: (MAX_SEQ, d_model)  — pure attention contribution (before residual)
        post_attn: (MAX_SEQ, d_model) — after residual add
        pre_ffn_norm: (MAX_SEQ, d_model)
        ffn_out: (MAX_SEQ, d_model)   — pure FFN contribution (before residual)
        post_ffn: (MAX_SEQ, d_model)  — after residual add (= layer output)
    """
    input_ids = mx.array(np.array([ids], dtype=np.int32))
    x = model.embed(input_ids)
    mx.eval(x)

    result = {"embedding": np.array(x[0]).copy(), "layers": {}}

    for li, layer in enumerate(model.layers):
        layer_data = {}

        # Pre-attention norm
        normed = layer.attn_norm(x)
        mx.eval(normed)
        layer_data["pre_attn_norm"] = np.array(normed[0]).copy()

        # Attention output (pure contribution)
        attn_out = layer.attn(normed)
        mx.eval(attn_out)
        layer_data["attn_out"] = np.array(attn_out[0]).copy()

        # Post-attention residual
        h_mid = x + attn_out
        mx.eval(h_mid)
        layer_data["post_attn"] = np.array(h_mid[0]).copy()

        # Pre-FFN norm
        ffn_normed = layer.ffn_norm(h_mid)
        mx.eval(ffn_normed)
        layer_data["pre_ffn_norm"] = np.array(ffn_normed[0]).copy()

        # FFN output (pure contribution) — handle GD and Holo models
        if hasattr(layer, "ffn"):
            ffn_out = layer.ffn(ffn_normed)
        elif hasattr(layer, "ffn_plate"):
            ffn_out = layer.ffn_plate(ffn_normed) * layer.ffn_scale + layer.ffn_bias
        else:
            ffn_out = mx.zeros_like(ffn_normed)
        mx.eval(ffn_out)
        layer_data["ffn_out"] = np.array(ffn_out[0]).copy()

        # Post-FFN residual (layer output)
        x = h_mid + ffn_out
        mx.eval(x)
        layer_data["post_ffn"] = np.array(x[0]).copy()

        result["layers"][li] = layer_data

    return result


# ══════════════════════════════════════════════════════════════════════
# Minimal-pair probe generation
# ══════════════════════════════════════════════════════════════════════

def make_minimal_pairs_single_reduction() -> list[dict]:
    """Generate minimal pairs: expression vs its one-step reduction.

    Each pair = (pre_reduction_expr, post_reduction_expr, combinator, args)
    """
    vars_list = ["a", "b", "c", "d", "e", "x", "y", "z"]
    fvars_list = ["f", "g", "h"]
    pairs = []

    # K x y = x — discard second argument
    for v1 in vars_list:
        for v2 in vars_list:
            if v1 == v2:
                continue
            pre = App(App(Comb("K"), Var(v1)), Var(v2))
            post = Var(v1)
            pre_ids = expr_to_ids(pre)
            post_ids = expr_to_ids(post)
            if pre_ids and post_ids:
                pairs.append({
                    "combinator": "K",
                    "pre_expr": str(pre),
                    "post_expr": str(post),
                    "pre_ids": pre_ids,
                    "post_ids": post_ids,
                    "args": {"kept": v1, "discarded": v2},
                })

    # I x = x — identity
    for v1 in vars_list:
        pre = App(Comb("I"), Var(v1))
        post = Var(v1)
        pre_ids = expr_to_ids(pre)
        post_ids = expr_to_ids(post)
        if pre_ids and post_ids:
            pairs.append({
                "combinator": "I",
                "pre_expr": str(pre),
                "post_expr": str(post),
                "pre_ids": pre_ids,
                "post_ids": post_ids,
                "args": {"identity": v1},
            })

    # B f g x = f (g x) — composition
    for f in fvars_list:
        for g in fvars_list:
            if f == g:
                continue
            for v in vars_list[:4]:  # limit to keep tractable
                pre = App(App(App(Comb("B"), Var(f)), Var(g)), Var(v))
                post = App(Var(f), App(Var(g), Var(v)))
                pre_ids = expr_to_ids(pre)
                post_ids = expr_to_ids(post)
                if pre_ids and post_ids:
                    pairs.append({
                        "combinator": "B",
                        "pre_expr": str(pre),
                        "post_expr": str(post),
                        "pre_ids": pre_ids,
                        "post_ids": post_ids,
                        "args": {"f": f, "g": g, "x": v},
                    })

    # C f x y = f y x — flip
    for f in fvars_list:
        for v1 in vars_list[:4]:
            for v2 in vars_list[:4]:
                if v1 == v2:
                    continue
                pre = App(App(App(Comb("C"), Var(f)), Var(v1)), Var(v2))
                post = App(App(Var(f), Var(v2)), Var(v1))
                pre_ids = expr_to_ids(pre)
                post_ids = expr_to_ids(post)
                if pre_ids and post_ids:
                    pairs.append({
                        "combinator": "C",
                        "pre_expr": str(pre),
                        "post_expr": str(post),
                        "pre_ids": pre_ids,
                        "post_ids": post_ids,
                        "args": {"f": f, "x": v1, "y": v2},
                    })

    return pairs


def make_minimal_pairs_nested() -> list[dict]:
    """Generate nested reduction pairs for chain decomposition.

    K (I a) b → I a → a  (two steps)
    Compare FFN deltas for the outer K step and inner I step.
    """
    vars_list = ["a", "b", "c", "x", "y"]
    fvars_list = ["f", "g", "h"]
    pairs = []

    # K (I v1) v2 → I v1 (outer K reduction)
    # I v1 → v1 (inner I reduction)
    for v1 in vars_list[:3]:
        for v2 in vars_list[:3]:
            if v1 == v2:
                continue
            full_expr = App(App(Comb("K"), App(Comb("I"), Var(v1))), Var(v2))
            after_k = App(Comb("I"), Var(v1))
            after_i = Var(v1)

            full_ids = expr_to_ids(full_expr)
            after_k_ids = expr_to_ids(after_k)
            after_i_ids = expr_to_ids(after_i)

            if full_ids and after_k_ids and after_i_ids:
                pairs.append({
                    "type": "nested_KI",
                    "chain": [
                        {"step": "K_outer", "pre_ids": full_ids, "post_ids": after_k_ids,
                         "pre_expr": str(full_expr), "post_expr": str(after_k)},
                        {"step": "I_inner", "pre_ids": after_k_ids, "post_ids": after_i_ids,
                         "pre_expr": str(after_k), "post_expr": str(after_i)},
                    ],
                    "args": {"v1": v1, "v2": v2},
                })

    # B f g (I x) → f (g (I x)) → ... (B reduction, then I inside)
    for f in fvars_list[:2]:
        for g in fvars_list[:2]:
            if f == g:
                continue
            for v in vars_list[:2]:
                inner = App(Comb("I"), Var(v))
                full_expr = App(App(App(Comb("B"), Var(f)), Var(g)), inner)
                after_b = App(Var(f), App(Var(g), inner))
                after_i = App(Var(f), App(Var(g), Var(v)))

                full_ids = expr_to_ids(full_expr)
                after_b_ids = expr_to_ids(after_b)
                after_i_ids = expr_to_ids(after_i)

                if full_ids and after_b_ids and after_i_ids:
                    pairs.append({
                        "type": "nested_BI",
                        "chain": [
                            {"step": "B_outer", "pre_ids": full_ids, "post_ids": after_b_ids,
                             "pre_expr": str(full_expr), "post_expr": str(after_b)},
                            {"step": "I_inner", "pre_ids": after_b_ids, "post_ids": after_i_ids,
                             "pre_expr": str(after_b), "post_expr": str(after_i)},
                        ],
                        "args": {"f": f, "g": g, "v": v},
                    })

    return pairs


# ══════════════════════════════════════════════════════════════════════
# Analysis: compute deltas and find patterns
# ══════════════════════════════════════════════════════════════════════

def compute_ffn_deltas(model, pairs: list[dict]) -> dict:
    """For each minimal pair, compute FFN activation deltas.

    For each pair (pre, post):
      Run both through the model
      At each layer, compute delta = ffn_out(pre) - ffn_out(post)
      The delta tells us what the FFN does differently for the unreduced
      vs reduced expression.

    We capture deltas at multiple token positions:
      - combinator position (where the combinator token is in pre)
      - last content token (the last non-pad, non-eq position)
      - "=" position (where the model decides the output)
    """
    results = {}

    for combinator in ["K", "I", "B", "C"]:
        comb_pairs = [p for p in pairs if p.get("combinator") == combinator]
        if not comb_pairs:
            continue

        log(f"\n  Processing {combinator}: {len(comb_pairs)} pairs")
        deltas_by_layer = {li: {"combinator_pos": [], "eq_pos": [], "full_seq": []}
                           for li in range(N_LAYERS)}

        for pair in comb_pairs:
            pre_acts = capture_all_activations(model, pair["pre_ids"])
            post_acts = capture_all_activations(model, pair["post_ids"])

            # Find key positions in pre expression
            comb_id = TOK2ID.get(combinator)
            comb_pos = None
            eq_pos = None
            for i, tok_id in enumerate(pair["pre_ids"]):
                if tok_id == comb_id and comb_pos is None:
                    comb_pos = i
                if tok_id == EQ_ID:
                    eq_pos = i
                    break

            if comb_pos is None:
                comb_pos = 1  # fallback: after <bos>
            if eq_pos is None:
                eq_pos = len([t for t in pair["pre_ids"] if t != PAD_ID]) - 1

            for li in range(N_LAYERS):
                pre_ffn = pre_acts["layers"][li]["ffn_out"]
                post_ffn = post_acts["layers"][li]["ffn_out"]

                # Delta at combinator position
                delta_comb = pre_ffn[comb_pos] - post_ffn[min(comb_pos, post_ffn.shape[0]-1)]
                deltas_by_layer[li]["combinator_pos"].append(delta_comb)

                # Delta at eq position
                post_eq = min(eq_pos, post_ffn.shape[0]-1)
                # Find eq in post
                post_eq_pos = None
                for i, tok_id in enumerate(pair["post_ids"]):
                    if tok_id == EQ_ID:
                        post_eq_pos = i
                        break
                if post_eq_pos is None:
                    post_eq_pos = len([t for t in pair["post_ids"] if t != PAD_ID]) - 1

                delta_eq = pre_ffn[eq_pos] - post_ffn[post_eq_pos]
                deltas_by_layer[li]["eq_pos"].append(delta_eq)

                # Full sequence delta (mean across all non-pad positions)
                pre_len = sum(1 for t in pair["pre_ids"] if t != PAD_ID)
                post_len = sum(1 for t in pair["post_ids"] if t != PAD_ID)
                delta_full = np.mean(pre_ffn[:pre_len], axis=0) - np.mean(post_ffn[:post_len], axis=0)
                deltas_by_layer[li]["full_seq"].append(delta_full)

        # Aggregate: compute mean delta, consistency, and identify hot dimensions
        results[combinator] = {}
        for li in range(N_LAYERS):
            layer_result = {}
            for pos_name in ["combinator_pos", "eq_pos", "full_seq"]:
                vecs = np.array(deltas_by_layer[li][pos_name])  # (n_pairs, d_model)
                if len(vecs) == 0:
                    continue

                mean_delta = np.mean(vecs, axis=0)
                std_delta = np.std(vecs, axis=0)
                mean_magnitude = np.mean(np.abs(vecs), axis=0)

                # Consistency: SNR = |mean| / std — high SNR = consistent direction
                snr = np.abs(mean_delta) / (std_delta + 1e-10)

                # Hot dimensions: high magnitude AND high consistency
                hot_score = mean_magnitude * snr
                top_dims = np.argsort(hot_score)[-20:][::-1]

                # Cosine similarity between all pairs of delta vectors
                # (measures if the delta is consistent across different arguments)
                if len(vecs) > 1:
                    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
                    normed = vecs / (norms + 1e-10)
                    cos_matrix = normed @ normed.T
                    # Mean pairwise cosine (excluding diagonal)
                    n = len(vecs)
                    mask = ~np.eye(n, dtype=bool)
                    mean_cos = float(cos_matrix[mask].mean())
                else:
                    mean_cos = 1.0

                layer_result[pos_name] = {
                    "mean_delta_norm": float(np.linalg.norm(mean_delta)),
                    "mean_magnitude": float(np.mean(mean_magnitude)),
                    "mean_snr": float(np.mean(snr)),
                    "mean_pairwise_cosine": mean_cos,
                    "top_dims": top_dims.tolist(),
                    "top_dims_snr": snr[top_dims].tolist(),
                    "top_dims_magnitude": mean_magnitude[top_dims].tolist(),
                    "n_pairs": len(vecs),
                }

            results[combinator][li] = layer_result

    return results


def analyze_key_value_separation(model, pairs: list[dict]) -> dict:
    """Experiment 2: Separate key (reduction mechanism) from value (arguments).

    For each combinator, group pairs by combinator type but vary arguments.
    The COMMON delta component across different arguments = the key.
    The VARYING component = the value.
    """
    log("\n═══ Experiment 2: Key vs Value Separation ═══")

    results = {}
    for combinator in ["K", "I", "B", "C"]:
        comb_pairs = [p for p in pairs if p.get("combinator") == combinator]
        if len(comb_pairs) < 3:
            continue

        log(f"\n  {combinator}: {len(comb_pairs)} argument variations")

        # Collect FFN deltas at eq position for each pair
        eq_deltas_by_layer = {li: [] for li in range(N_LAYERS)}

        for pair in comb_pairs:
            pre_acts = capture_all_activations(model, pair["pre_ids"])
            post_acts = capture_all_activations(model, pair["post_ids"])

            # Find eq positions
            eq_pos_pre = None
            for i, tok_id in enumerate(pair["pre_ids"]):
                if tok_id == EQ_ID:
                    eq_pos_pre = i
                    break
            eq_pos_post = None
            for i, tok_id in enumerate(pair["post_ids"]):
                if tok_id == EQ_ID:
                    eq_pos_post = i
                    break

            if eq_pos_pre is None or eq_pos_post is None:
                continue

            for li in range(N_LAYERS):
                delta = (pre_acts["layers"][li]["ffn_out"][eq_pos_pre] -
                         post_acts["layers"][li]["ffn_out"][eq_pos_post])
                eq_deltas_by_layer[li].append(delta)

        results[combinator] = {}
        for li in range(N_LAYERS):
            vecs = np.array(eq_deltas_by_layer[li])
            if len(vecs) < 3:
                continue

            # Key = mean delta (common across all argument variations)
            key_component = np.mean(vecs, axis=0)

            # Value = residual after removing key (argument-specific)
            residuals = vecs - key_component[np.newaxis, :]
            value_variance = np.var(residuals, axis=0)

            # Key strength: how much of the delta is the common key?
            key_norm = np.linalg.norm(key_component)
            residual_norms = np.linalg.norm(residuals, axis=1)
            mean_residual_norm = float(np.mean(residual_norms))
            total_norm = float(np.mean(np.linalg.norm(vecs, axis=1)))

            # Key fraction: what percentage of the delta is the shared key?
            key_fraction = key_norm / (total_norm + 1e-10)

            # Key dimensions: which dims carry the key signal?
            key_magnitude = np.abs(key_component)
            key_dims = np.argsort(key_magnitude)[-20:][::-1]

            # Value dimensions: which dims carry the argument signal?
            value_magnitude = np.sqrt(value_variance)
            value_dims = np.argsort(value_magnitude)[-20:][::-1]

            # Overlap: dims that are both key and value (entangled)
            key_set = set(key_dims.tolist()[:10])
            value_set = set(value_dims.tolist()[:10])
            overlap = key_set & value_set

            results[combinator][li] = {
                "key_norm": float(key_norm),
                "mean_residual_norm": mean_residual_norm,
                "total_delta_norm": total_norm,
                "key_fraction": float(key_fraction),
                "key_dims": key_dims.tolist(),
                "value_dims": value_dims.tolist(),
                "key_value_overlap": list(overlap),
                "overlap_fraction": len(overlap) / 10.0,
                "n_pairs": len(vecs),
            }

            log(f"    L{li}: key_frac={key_fraction:.3f} "
                f"key_norm={key_norm:.4f} "
                f"res_norm={mean_residual_norm:.4f} "
                f"overlap={len(overlap)}/10")

    return results


def analyze_chain_decomposition(model, nested_pairs: list[dict]) -> dict:
    """Experiment 3: Do nested reductions compose or have separate functions?

    Compare FFN delta for outer reduction in a chain vs the same reduction
    when applied alone. If the deltas are similar, the function is reused.
    If different, there's a specialized "nested" function.
    """
    log("\n═══ Experiment 3: Chain Decomposition ═══")

    results = {}

    for pair in nested_pairs:
        pair_type = pair["type"]
        if pair_type not in results:
            results[pair_type] = {"step_deltas": {}, "compositions": []}

        chain = pair["chain"]
        chain_deltas = {}

        for step in chain:
            pre_acts = capture_all_activations(model, step["pre_ids"])
            post_acts = capture_all_activations(model, step["post_ids"])

            step_name = step["step"]
            chain_deltas[step_name] = {}

            for li in range(N_LAYERS):
                # Delta at eq position
                eq_pre = None
                for i, t in enumerate(step["pre_ids"]):
                    if t == EQ_ID:
                        eq_pre = i
                        break
                eq_post = None
                for i, t in enumerate(step["post_ids"]):
                    if t == EQ_ID:
                        eq_post = i
                        break
                if eq_pre is None or eq_post is None:
                    continue

                delta = (pre_acts["layers"][li]["ffn_out"][eq_pre] -
                         post_acts["layers"][li]["ffn_out"][eq_post])
                chain_deltas[step_name][li] = delta

                if step_name not in results[pair_type]["step_deltas"]:
                    results[pair_type]["step_deltas"][step_name] = {l: [] for l in range(N_LAYERS)}
                results[pair_type]["step_deltas"][step_name][li].append(delta)

        results[pair_type]["compositions"].append(chain_deltas)

    # Analyze: compare nested reduction deltas to standalone deltas
    summary = {}
    for pair_type, data in results.items():
        summary[pair_type] = {}
        for step_name, layer_deltas in data["step_deltas"].items():
            summary[pair_type][step_name] = {}
            for li in range(N_LAYERS):
                vecs = np.array(layer_deltas.get(li, []))
                if len(vecs) < 2:
                    continue
                mean_delta = np.mean(vecs, axis=0)
                # Consistency across instances
                norms = np.linalg.norm(vecs, axis=1, keepdims=True)
                normed = vecs / (norms + 1e-10)
                cos_matrix = normed @ normed.T
                n = len(vecs)
                mask_m = ~np.eye(n, dtype=bool)
                mean_cos = float(cos_matrix[mask_m].mean()) if n > 1 else 1.0

                summary[pair_type][step_name][li] = {
                    "mean_delta_norm": float(np.linalg.norm(mean_delta)),
                    "mean_pairwise_cosine": mean_cos,
                    "n_samples": len(vecs),
                }

    log(f"\n  Chain types analyzed: {list(summary.keys())}")
    for pair_type, steps in summary.items():
        for step_name, layers in steps.items():
            for li, stats in layers.items():
                log(f"    {pair_type}/{step_name} L{li}: "
                    f"norm={stats['mean_delta_norm']:.4f} "
                    f"cos={stats['mean_pairwise_cosine']:.3f}")

    return summary


def analyze_layer_roles(delta_results: dict) -> dict:
    """Experiment 4: Map layer roles to crystal rotation model.

    Crystal model predicts:
      L0 = reset (90° rotation) — should show large deltas, all combinators similar
      L1 = route (43° rotation) — should show combinator-specific routing deltas
      L2 = converge (5° rotation) — should show small, output-focused deltas

    Test: does the actual FFN delta pattern match these predictions?
    """
    log("\n═══ Experiment 4: Layer Role Analysis ═══")

    predictions = {
        0: "reset: large uniform deltas (90° rotation, all combinators similar)",
        1: "route: combinator-specific deltas (43° rotation, K/B/C cluster, I diverges)",
        2: "converge: small output-focused deltas (5° rotation, settling)",
    }

    analysis = {}
    for li in range(N_LAYERS):
        log(f"\n  L{li} — predicted: {predictions[li]}")

        layer_norms = {}
        layer_cosines = {}

        for comb in ["K", "I", "B", "C"]:
            if comb not in delta_results:
                continue
            if li not in delta_results[comb]:
                continue
            eq_data = delta_results[comb][li].get("eq_pos", {})
            if not eq_data:
                continue
            layer_norms[comb] = eq_data.get("mean_delta_norm", 0)
            layer_cosines[comb] = eq_data.get("mean_pairwise_cosine", 0)

        if not layer_norms:
            continue

        # Cross-combinator similarity: do K/B/C cluster while I diverges?
        kbc_norms = [layer_norms.get(c, 0) for c in ["K", "B", "C"] if c in layer_norms]
        i_norm = layer_norms.get("I", 0)

        # Get mean deltas for cross-combinator cosine
        mean_deltas = {}
        for comb in ["K", "I", "B", "C"]:
            if comb in delta_results and li in delta_results[comb]:
                eq_data = delta_results[comb][li].get("eq_pos", {})
                if "mean_delta_norm" in eq_data:
                    # We need the actual mean delta vector — reconstruct from top dims
                    # For now, use the norm and cosine metrics we have
                    pass

        analysis[li] = {
            "norms": layer_norms,
            "kbc_mean_norm": float(np.mean(kbc_norms)) if kbc_norms else 0,
            "i_norm": i_norm,
            "kbc_i_ratio": float(np.mean(kbc_norms) / (i_norm + 1e-10)) if kbc_norms else 0,
            "within_comb_cosines": layer_cosines,
            "prediction": predictions[li],
        }

        log(f"    Norms: {' '.join(f'{c}={v:.4f}' for c, v in layer_norms.items())}")
        log(f"    KBC mean={analysis[li]['kbc_mean_norm']:.4f} I={i_norm:.4f} "
            f"ratio={analysis[li]['kbc_i_ratio']:.3f}")

    return analysis


# ══════════════════════════════════════════════════════════════════════
# Cross-combinator comparison
# ══════════════════════════════════════════════════════════════════════

def cross_combinator_analysis(model, pairs: list[dict]) -> dict:
    """Compare FFN delta signatures BETWEEN combinators.

    For each layer, compute the mean FFN delta per combinator at the eq position,
    then measure cosine similarity between combinators.

    Crystal model predicts: K/B/C should be similar (identical rotations),
    I should be different (32° offset).
    """
    log("\n═══ Cross-Combinator FFN Delta Comparison ═══")

    # Collect mean deltas per combinator per layer
    comb_mean_deltas = {}

    for combinator in ["K", "I", "B", "C"]:
        comb_pairs = [p for p in pairs if p.get("combinator") == combinator]
        if not comb_pairs:
            continue

        eq_deltas = {li: [] for li in range(N_LAYERS)}
        for pair in comb_pairs:
            pre_acts = capture_all_activations(model, pair["pre_ids"])
            post_acts = capture_all_activations(model, pair["post_ids"])

            eq_pre = next((i for i, t in enumerate(pair["pre_ids"]) if t == EQ_ID), None)
            eq_post = next((i for i, t in enumerate(pair["post_ids"]) if t == EQ_ID), None)
            if eq_pre is None or eq_post is None:
                continue

            for li in range(N_LAYERS):
                delta = (pre_acts["layers"][li]["ffn_out"][eq_pre] -
                         post_acts["layers"][li]["ffn_out"][eq_post])
                eq_deltas[li].append(delta)

        comb_mean_deltas[combinator] = {}
        for li in range(N_LAYERS):
            if eq_deltas[li]:
                comb_mean_deltas[combinator][li] = np.mean(eq_deltas[li], axis=0)

    # Compute cross-combinator cosine similarity matrix per layer
    results = {}
    combinators = ["K", "I", "B", "C"]

    for li in range(N_LAYERS):
        cos_matrix = np.zeros((4, 4))
        for i, c1 in enumerate(combinators):
            for j, c2 in enumerate(combinators):
                if c1 in comb_mean_deltas and c2 in comb_mean_deltas:
                    v1 = comb_mean_deltas[c1].get(li)
                    v2 = comb_mean_deltas[c2].get(li)
                    if v1 is not None and v2 is not None:
                        cos = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10))
                        cos_matrix[i, j] = cos

        # Extract KBC-internal vs KBC-I comparison
        kbc_idx = [0, 2, 3]  # K, B, C
        kbc_internal = []
        kbc_i = []
        for i in kbc_idx:
            for j in kbc_idx:
                if i != j:
                    kbc_internal.append(cos_matrix[i, j])
            kbc_i.append(cos_matrix[i, 1])  # vs I

        results[li] = {
            "cos_matrix": cos_matrix.tolist(),
            "labels": combinators,
            "kbc_internal_mean_cos": float(np.mean(kbc_internal)) if kbc_internal else 0,
            "kbc_i_mean_cos": float(np.mean(kbc_i)) if kbc_i else 0,
            "kbc_i_separation": (float(np.mean(kbc_internal)) - float(np.mean(kbc_i)))
                                if kbc_internal and kbc_i else 0,
        }

        log(f"\n  L{li} cross-combinator cosine matrix:")
        log(f"    {'':>4s} " + " ".join(f"{c:>6s}" for c in combinators))
        for i, c1 in enumerate(combinators):
            row = " ".join(f"{cos_matrix[i,j]:6.3f}" for j in range(4))
            log(f"    {c1:>4s} {row}")
        log(f"    KBC internal: {results[li]['kbc_internal_mean_cos']:.3f}")
        log(f"    KBC vs I:     {results[li]['kbc_i_mean_cos']:.3f}")
        log(f"    Separation:   {results[li]['kbc_i_separation']:.3f}")

    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def train_teacher(d_model: int = 256, n_steps: int = 3000) -> GDModel:
    """Train a GD teacher model to convergence."""
    log(f"\n  Training GD teacher (d={d_model}, {n_steps} steps)...")
    model = GDModel(d_model=d_model, n_layers=N_LAYERS)
    optimizer = optim.Adam(learning_rate=3e-3)
    rng = np.random.RandomState(42)

    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)

    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(32, rng, max_depth=4)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state)

        if (step + 1) % 500 == 0:
            metrics = eval_model(model, np.random.RandomState(99), n_batches=20)
            log(f"    Step {step+1}: loss={float(loss_val):.4f} "
                f"eval_acc={metrics['accuracy']:.3f}")

    metrics = eval_model(model, np.random.RandomState(99), n_batches=50)
    log(f"  Teacher final: acc={metrics['accuracy']:.3f} loss={metrics['loss']:.4f}")
    return model


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log("═══════════════════════════════════════════════════════")
    log("  FFN Mechanism Probe — Session 127")
    log("  Discovering how beta reductions are stored and activated")
    log("═══════════════════════════════════════════════════════")

    t0 = time.time()

    # ── Train teacher ──────────────────────────────────────────
    teacher = train_teacher(d_model=256, n_steps=3000)

    # ── Generate probe sets ────────────────────────────────────
    log("\n═══ Generating minimal-pair probes ═══")
    single_pairs = make_minimal_pairs_single_reduction()
    nested_pairs = make_minimal_pairs_nested()

    comb_counts = {}
    for p in single_pairs:
        c = p["combinator"]
        comb_counts[c] = comb_counts.get(c, 0) + 1
    log(f"  Single-reduction pairs: {len(single_pairs)}")
    for c, n in sorted(comb_counts.items()):
        log(f"    {c}: {n}")
    log(f"  Nested chain pairs: {len(nested_pairs)}")

    # ── Experiment 1: Reduction signatures ─────────────────────
    log("\n═══ Experiment 1: Reduction Signatures ═══")
    delta_results = compute_ffn_deltas(teacher, single_pairs)

    for comb in ["K", "I", "B", "C"]:
        if comb not in delta_results:
            continue
        log(f"\n  {comb} reduction FFN deltas:")
        for li in range(N_LAYERS):
            if li not in delta_results[comb]:
                continue
            for pos_name in ["combinator_pos", "eq_pos"]:
                data = delta_results[comb][li].get(pos_name, {})
                if not data:
                    continue
                log(f"    L{li} @{pos_name}: "
                    f"norm={data.get('mean_delta_norm', 0):.4f} "
                    f"cos={data.get('mean_pairwise_cosine', 0):.3f} "
                    f"snr={data.get('mean_snr', 0):.3f}")

    # ── Experiment 2: Key vs Value ─────────────────────────────
    kv_results = analyze_key_value_separation(teacher, single_pairs)

    # ── Experiment 3: Chain decomposition ──────────────────────
    chain_results = analyze_chain_decomposition(teacher, nested_pairs)

    # ── Experiment 4: Layer role analysis ──────────────────────
    layer_results = analyze_layer_roles(delta_results)

    # ── Cross-combinator comparison ────────────────────────────
    # Use a subset for speed (10 per combinator)
    subset = []
    for comb in ["K", "I", "B", "C"]:
        comb_pairs = [p for p in single_pairs if p.get("combinator") == comb]
        subset.extend(comb_pairs[:10])
    cross_results = cross_combinator_analysis(teacher, subset)

    # ── Save results ───────────────────────────────────────────
    elapsed = time.time() - t0

    # Convert numpy arrays to lists for JSON serialization
    def numpy_safe(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, dict):
            return {str(k): numpy_safe(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [numpy_safe(v) for v in obj]
        return obj

    all_results = {
        "experiment": "ffn_mechanism_probe",
        "session": 127,
        "elapsed_s": elapsed,
        "model": {"d_model": 256, "n_layers": N_LAYERS, "type": "GDModel"},
        "probes": {
            "single_pairs": len(single_pairs),
            "nested_pairs": len(nested_pairs),
            "per_combinator": comb_counts,
        },
        "exp1_reduction_signatures": numpy_safe(delta_results),
        "exp2_key_value_separation": numpy_safe(kv_results),
        "exp3_chain_decomposition": numpy_safe(chain_results),
        "exp4_layer_roles": numpy_safe(layer_results),
        "exp5_cross_combinator": numpy_safe(cross_results),
    }

    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    log(f"\n═══════════════════════════════════════════════════════")
    log(f"  Done in {elapsed:.1f}s")
    log(f"  Results: {RESULTS_DIR / 'results.json'}")
    log(f"═══════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
