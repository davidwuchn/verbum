"""FFN Mechanism Probe — Real Model (Qwen3-14B).

Session 127. Port of probe_ffn_mechanism.py from the mini holo toy model
to a real model with a fully formed crystal. Uses Qwen3-14B via
transformers + hooks on the MLP layers to capture FFN activations.

Minimal-pair probes: NL sentences that include lambda reduction expressions.
The model sees the full compile gate prompt with pre-reduction and
post-reduction expressions. We capture FFN activations at every layer
and compute deltas to find the reduction mechanism.

Probes use the nucleus compile gate format:
  "<gate>\n{expression} ="

This activates the lambda compiler circuit. We compare the FFN activation
when the expression is pre-reduction vs post-reduction.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/probe_ffn_mechanism_real.py 2>&1 | tee results/ffn-mechanism-real/run.log

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "ffn-mechanism-real"
MODEL_NAME = "Qwen/Qwen3-14B"
N_LAYERS = 40
D_MODEL = 5120
DEVICE = "mps"

# Sample depths across the 40-layer model
DEPTH_LAYERS = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 39]


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Compile gate — activates the lambda compiler circuit
# ══════════════════════════════════════════════════════════════════════

COMPILE_GATE = """You are a lambda calculus compiler. Convert natural language to typed lambda calculus.
Input a combinator expression. Output its beta-normal form.
Be terse. Output ONLY the reduced expression."""


def make_prompt(expression: str) -> str:
    """Wrap an expression in the compile gate format."""
    return f"{COMPILE_GATE}\n\n{expression} ="


# ══════════════════════════════════════════════════════════════════════
# Minimal-pair probes — combinator expressions pre/post reduction
# ══════════════════════════════════════════════════════════════════════

def make_minimal_pairs() -> list[dict]:
    """Generate minimal pairs: combinator expression vs its reduction.

    Uses string-form expressions (not AST) since the real model works
    with text tokens, not the toy tokenizer.
    """
    pairs = []
    vars_list = ["x", "y", "z", "a", "b"]
    fvars_list = ["f", "g", "h"]

    # K x y = x
    for v1 in vars_list:
        for v2 in vars_list:
            if v1 == v2:
                continue
            pairs.append({
                "combinator": "K",
                "pre_expr": f"K {v1} {v2}",
                "post_expr": f"{v1}",
                "args": {"kept": v1, "discarded": v2},
            })

    # I x = x
    for v1 in vars_list:
        pairs.append({
            "combinator": "I",
            "pre_expr": f"I {v1}",
            "post_expr": f"{v1}",
            "args": {"identity": v1},
        })

    # B f g x = f (g x)
    for f in fvars_list:
        for g in fvars_list:
            if f == g:
                continue
            for v in vars_list[:3]:
                pairs.append({
                    "combinator": "B",
                    "pre_expr": f"B {f} {g} {v}",
                    "post_expr": f"{f} ({g} {v})",
                    "args": {"f": f, "g": g, "x": v},
                })

    # C f x y = f y x
    for f in fvars_list:
        for v1 in vars_list[:3]:
            for v2 in vars_list[:3]:
                if v1 == v2:
                    continue
                pairs.append({
                    "combinator": "C",
                    "pre_expr": f"C {f} {v1} {v2}",
                    "post_expr": f"{f} {v2} {v1}",
                    "args": {"f": f, "x": v1, "y": v2},
                })

    # S combinator (if model knows it): S f g x = f x (g x)
    for f in fvars_list[:2]:
        for g in fvars_list[:2]:
            if f == g:
                continue
            for v in vars_list[:2]:
                pairs.append({
                    "combinator": "S",
                    "pre_expr": f"S {f} {g} {v}",
                    "post_expr": f"{f} {v} ({g} {v})",
                    "args": {"f": f, "g": g, "x": v},
                })

    # Lambda reductions (beta reduction proper)
    # (λx. x) a = a
    for v in vars_list[:3]:
        pairs.append({
            "combinator": "beta_identity",
            "pre_expr": f"(λx. x) {v}",
            "post_expr": f"{v}",
            "args": {"var": v},
        })

    # (λx. f x) a = f a
    for f in fvars_list[:2]:
        for v in vars_list[:3]:
            pairs.append({
                "combinator": "beta_apply",
                "pre_expr": f"(λx. {f} x) {v}",
                "post_expr": f"{f} {v}",
                "args": {"f": f, "var": v},
            })

    # (λx. λy. x) a b = a  (K as lambda)
    for v1 in vars_list[:3]:
        for v2 in vars_list[:3]:
            if v1 == v2:
                continue
            pairs.append({
                "combinator": "beta_K",
                "pre_expr": f"(λx. λy. x) {v1} {v2}",
                "post_expr": f"{v1}",
                "args": {"kept": v1, "discarded": v2},
            })

    return pairs


def make_nested_pairs() -> list[dict]:
    """Nested reduction chains for a real model."""
    pairs = []

    # K (I a) b → I a → a
    for v1 in ["x", "y", "a"]:
        for v2 in ["z", "b", "c"]:
            pairs.append({
                "type": "nested_KI",
                "chain": [
                    {"step": "K_outer", "pre_expr": f"K (I {v1}) {v2}", "post_expr": f"I {v1}"},
                    {"step": "I_inner", "pre_expr": f"I {v1}", "post_expr": f"{v1}"},
                ],
                "args": {"v1": v1, "v2": v2},
            })

    # B f g (I x) → f (g (I x)) → ...
    for f in ["f", "g"]:
        for g2 in ["h", "p"]:
            for v in ["x", "a"]:
                pairs.append({
                    "type": "nested_BI",
                    "chain": [
                        {"step": "B_outer", "pre_expr": f"B {f} {g2} (I {v})",
                         "post_expr": f"{f} ({g2} (I {v}))"},
                        {"step": "I_inner", "pre_expr": f"I {v}", "post_expr": f"{v}"},
                    ],
                    "args": {"f": f, "g": g2, "v": v},
                })

    return pairs


# ══════════════════════════════════════════════════════════════════════
# Model loading and activation capture
# ══════════════════════════════════════════════════════════════════════

def load_model():
    """Load Qwen3-14B with tokenizer."""
    log(f"  Loading {MODEL_NAME}...")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16,
        device_map=DEVICE,
        trust_remote_code=True,
    )
    model.eval()

    log(f"  Loaded in {time.time()-t0:.1f}s")
    return model, tokenizer


def capture_ffn_activations(model, tokenizer, text: str, target_layers: list[int]) -> dict:
    """Run text through model, capture FFN (MLP up_proj) activations at target layers.

    Returns dict[layer_idx] → {
        "up_proj": (seq_len, d_intermediate) — MLP up_proj output
        "down_proj": (seq_len, d_model) — MLP final output (the FFN contribution)
    }

    We capture at the last token position for efficiency, plus the full
    sequence for positional analysis.
    """
    ids = tokenizer.encode(text, return_tensors="pt").to(DEVICE)
    seq_len = ids.shape[1]

    captures = {}
    hooks = []

    layers = model.model.layers

    for li in target_layers:
        captures[li] = {}
        mlp = layers[li].mlp

        # Hook up_proj: the "key" that activates FFN neurons
        def make_up_hook(layer_idx):
            def hook(m, inp, out):
                captures[layer_idx]["up_proj"] = out.detach().cpu().float().numpy()[0]
            return hook
        hooks.append(mlp.up_proj.register_forward_hook(make_up_hook(li)))

        # Hook down_proj: the final FFN output (the "value" contributed to residual)
        def make_down_hook(layer_idx):
            def hook(m, inp, out):
                captures[layer_idx]["down_proj"] = out.detach().cpu().float().numpy()[0]
            return hook
        hooks.append(mlp.down_proj.register_forward_hook(make_down_hook(li)))

    with torch.no_grad():
        _ = model(ids)

    for h in hooks:
        h.remove()

    return captures, seq_len


# ══════════════════════════════════════════════════════════════════════
# Analysis
# ══════════════════════════════════════════════════════════════════════

def compute_deltas(model, tokenizer, pairs: list[dict], target_layers: list[int]) -> dict:
    """Compute FFN activation deltas between pre/post reduction pairs.

    For each pair, we compare the FFN output at the LAST token position
    (right before "="), which is where the model decides the output.
    """
    results = {}

    for combinator in sorted(set(p["combinator"] for p in pairs)):
        comb_pairs = [p for p in pairs if p["combinator"] == combinator]
        log(f"\n  {combinator}: {len(comb_pairs)} pairs")

        # Limit to 15 pairs per combinator for speed on 14B model
        if len(comb_pairs) > 15:
            rng = np.random.RandomState(42)
            indices = rng.choice(len(comb_pairs), 15, replace=False)
            comb_pairs = [comb_pairs[i] for i in indices]
            log(f"    (sampled 15 for speed)")

        deltas_by_layer = {li: {"last_token": [], "mean_seq": []} for li in target_layers}

        for pi, pair in enumerate(comb_pairs):
            pre_text = make_prompt(pair["pre_expr"])
            post_text = make_prompt(pair["post_expr"])

            pre_caps, pre_len = capture_ffn_activations(model, tokenizer, pre_text, target_layers)
            post_caps, post_len = capture_ffn_activations(model, tokenizer, post_text, target_layers)

            for li in target_layers:
                if li not in pre_caps or li not in post_caps:
                    continue
                if "down_proj" not in pre_caps[li] or "down_proj" not in post_caps[li]:
                    continue

                pre_ffn = pre_caps[li]["down_proj"]   # (pre_len, d_model)
                post_ffn = post_caps[li]["down_proj"]  # (post_len, d_model)

                # Delta at last token (the prediction point)
                delta_last = pre_ffn[-1] - post_ffn[-1]
                deltas_by_layer[li]["last_token"].append(delta_last)

                # Delta of mean activation across sequence
                delta_mean = np.mean(pre_ffn, axis=0) - np.mean(post_ffn, axis=0)
                deltas_by_layer[li]["mean_seq"].append(delta_mean)

            if (pi + 1) % 5 == 0:
                log(f"    {pi+1}/{len(comb_pairs)} pairs done")

        # Aggregate
        results[combinator] = {}
        for li in target_layers:
            layer_result = {}
            for pos_name in ["last_token", "mean_seq"]:
                vecs = np.array(deltas_by_layer[li][pos_name])
                if len(vecs) == 0:
                    continue

                mean_delta = np.mean(vecs, axis=0)
                mean_magnitude = np.mean(np.abs(vecs), axis=0)

                # Pairwise cosine consistency
                if len(vecs) > 1:
                    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
                    normed = vecs / (norms + 1e-10)
                    cos_matrix = normed @ normed.T
                    n = len(vecs)
                    mask = ~np.eye(n, dtype=bool)
                    mean_cos = float(cos_matrix[mask].mean())
                else:
                    mean_cos = 1.0

                # Top active dimensions
                mag = np.mean(np.abs(vecs), axis=0)
                top_dims = np.argsort(mag)[-30:][::-1]

                layer_result[pos_name] = {
                    "mean_delta_norm": float(np.linalg.norm(mean_delta)),
                    "mean_magnitude": float(np.mean(mean_magnitude)),
                    "mean_pairwise_cosine": mean_cos,
                    "top_dims": top_dims.tolist(),
                    "top_dims_magnitude": mag[top_dims].tolist(),
                    "n_pairs": len(vecs),
                }

            results[combinator][li] = layer_result

    return results


def key_value_separation(model, tokenizer, pairs: list[dict], target_layers: list[int]) -> dict:
    """Key vs value analysis: common mechanism vs argument-specific content."""
    log("\n═══ Key vs Value Separation ═══")

    results = {}
    for combinator in sorted(set(p["combinator"] for p in pairs)):
        comb_pairs = [p for p in pairs if p["combinator"] == combinator]
        if len(comb_pairs) < 3:
            continue

        # Limit for speed
        if len(comb_pairs) > 15:
            rng = np.random.RandomState(42)
            indices = rng.choice(len(comb_pairs), 15, replace=False)
            comb_pairs = [comb_pairs[i] for i in indices]

        log(f"\n  {combinator}: {len(comb_pairs)} argument variations")
        deltas_by_layer = {li: [] for li in target_layers}

        for pair in comb_pairs:
            pre_text = make_prompt(pair["pre_expr"])
            post_text = make_prompt(pair["post_expr"])

            pre_caps, _ = capture_ffn_activations(model, tokenizer, pre_text, target_layers)
            post_caps, _ = capture_ffn_activations(model, tokenizer, post_text, target_layers)

            for li in target_layers:
                if li in pre_caps and li in post_caps:
                    if "down_proj" in pre_caps[li] and "down_proj" in post_caps[li]:
                        delta = pre_caps[li]["down_proj"][-1] - post_caps[li]["down_proj"][-1]
                        deltas_by_layer[li].append(delta)

        results[combinator] = {}
        for li in target_layers:
            vecs = np.array(deltas_by_layer[li])
            if len(vecs) < 3:
                continue

            key_component = np.mean(vecs, axis=0)
            residuals = vecs - key_component[np.newaxis, :]

            key_norm = np.linalg.norm(key_component)
            total_norm = float(np.mean(np.linalg.norm(vecs, axis=1)))
            key_fraction = key_norm / (total_norm + 1e-10)

            results[combinator][li] = {
                "key_norm": float(key_norm),
                "total_delta_norm": total_norm,
                "key_fraction": float(key_fraction),
                "n_pairs": len(vecs),
            }

            log(f"    L{li:2d}: key_frac={key_fraction:.3f} "
                f"key_norm={key_norm:.4f} total={total_norm:.4f}")

    return results


def cross_combinator_comparison(model, tokenizer, pairs: list[dict],
                                 target_layers: list[int]) -> dict:
    """Cross-combinator cosine similarity of FFN deltas per layer."""
    log("\n═══ Cross-Combinator FFN Delta Comparison ═══")

    # Collect mean deltas per combinator per layer
    combinator_types = sorted(set(p["combinator"] for p in pairs))
    mean_deltas = {}

    for combinator in combinator_types:
        comb_pairs = [p for p in pairs if p["combinator"] == combinator]
        if len(comb_pairs) > 10:
            rng = np.random.RandomState(42)
            indices = rng.choice(len(comb_pairs), 10, replace=False)
            comb_pairs = [comb_pairs[i] for i in indices]

        layer_deltas = {li: [] for li in target_layers}

        for pair in comb_pairs:
            pre_text = make_prompt(pair["pre_expr"])
            post_text = make_prompt(pair["post_expr"])

            pre_caps, _ = capture_ffn_activations(model, tokenizer, pre_text, target_layers)
            post_caps, _ = capture_ffn_activations(model, tokenizer, post_text, target_layers)

            for li in target_layers:
                if li in pre_caps and li in post_caps:
                    if "down_proj" in pre_caps[li] and "down_proj" in post_caps[li]:
                        delta = pre_caps[li]["down_proj"][-1] - post_caps[li]["down_proj"][-1]
                        layer_deltas[li].append(delta)

        mean_deltas[combinator] = {}
        for li in target_layers:
            if layer_deltas[li]:
                mean_deltas[combinator][li] = np.mean(layer_deltas[li], axis=0)

    # Cosine similarity matrices per layer
    results = {}
    for li in target_layers:
        combs_with_data = [c for c in combinator_types if li in mean_deltas.get(c, {})]
        n = len(combs_with_data)
        if n < 2:
            continue

        cos_matrix = np.zeros((n, n))
        for i, c1 in enumerate(combs_with_data):
            for j, c2 in enumerate(combs_with_data):
                v1 = mean_deltas[c1][li]
                v2 = mean_deltas[c2][li]
                cos = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10))
                cos_matrix[i, j] = cos

        results[li] = {
            "labels": combs_with_data,
            "cos_matrix": cos_matrix.tolist(),
        }

        log(f"\n  L{li:2d} cross-combinator cosine:")
        header = "    " + " ".join(f"{c:>8s}" for c in combs_with_data)
        log(header)
        for i, c1 in enumerate(combs_with_data):
            row = " ".join(f"{cos_matrix[i,j]:8.3f}" for j in range(n))
            log(f"    {c1:>8s} {row}")

    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

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


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log("═══════════════════════════════════════════════════════")
    log("  FFN Mechanism Probe — Qwen3-14B (Real Model)")
    log("  Session 127 — Discovering beta reduction in FFN")
    log("═══════════════════════════════════════════════════════")

    t0 = time.time()

    # ── Load model ─────────────────────────────────────────────
    model, tokenizer = load_model()

    # ── Generate probes ────────────────────────────────────────
    log("\n═══ Generating minimal-pair probes ═══")
    pairs = make_minimal_pairs()
    nested_pairs = make_nested_pairs()

    comb_counts = {}
    for p in pairs:
        c = p["combinator"]
        comb_counts[c] = comb_counts.get(c, 0) + 1
    log(f"  Single-reduction pairs: {len(pairs)}")
    for c, n in sorted(comb_counts.items()):
        log(f"    {c}: {n}")
    log(f"  Nested chain pairs: {len(nested_pairs)}")

    # ── Experiment 1: Reduction signatures ─────────────────────
    log("\n═══ Experiment 1: FFN Reduction Signatures ═══")
    delta_results = compute_deltas(model, tokenizer, pairs, DEPTH_LAYERS)

    for comb in sorted(delta_results.keys()):
        log(f"\n  {comb} reduction FFN deltas:")
        for li in DEPTH_LAYERS:
            if li not in delta_results[comb]:
                continue
            data = delta_results[comb][li].get("last_token", {})
            if data:
                log(f"    L{li:2d}: norm={data.get('mean_delta_norm', 0):.4f} "
                    f"cos={data.get('mean_pairwise_cosine', 0):.3f} "
                    f"n={data.get('n_pairs', 0)}")

    # ── Experiment 2: Key vs Value ─────────────────────────────
    kv_results = key_value_separation(model, tokenizer, pairs, DEPTH_LAYERS)

    # ── Experiment 3: Cross-combinator comparison ──────────────
    cross_results = cross_combinator_comparison(model, tokenizer, pairs, DEPTH_LAYERS)

    # ── Save results ───────────────────────────────────────────
    elapsed = time.time() - t0

    all_results = {
        "experiment": "ffn_mechanism_probe_real",
        "session": 127,
        "model": MODEL_NAME,
        "n_layers": N_LAYERS,
        "d_model": D_MODEL,
        "depth_layers": DEPTH_LAYERS,
        "elapsed_s": elapsed,
        "probes": {
            "single_pairs": len(pairs),
            "nested_pairs": len(nested_pairs),
            "per_combinator": comb_counts,
        },
        "exp1_reduction_signatures": numpy_safe(delta_results),
        "exp2_key_value_separation": numpy_safe(kv_results),
        "exp3_cross_combinator": numpy_safe(cross_results),
    }

    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    log(f"\n═══════════════════════════════════════════════════════")
    log(f"  Done in {elapsed:.1f}s")
    log(f"  Results: {RESULTS_DIR / 'results.json'}")
    log(f"═══════════════════════════════════════════════════════")

    # Cleanup
    del model, tokenizer
    gc.collect()
    torch.mps.empty_cache()


if __name__ == "__main__":
    main()
