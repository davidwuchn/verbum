#!/usr/bin/env python3
"""FFN Decomposition: LARQL-style analysis applied to Pythia-160M.

BACKGROUND: LARQL (github.com/chrishayuk/larql) treats each FFN feature as
a key-value pair:
  - key   = row of W_up (what input pattern triggers this feature)
  - value = column of W_down (what this feature contributes to the residual)
  - label = W_embed @ W_down[:, j] → which token this feature "means"
  - circuit type = cos(key, value) → identity/transform/projector/suppressor/inverter

They found a striking depth profile on Gemma 3 4B (34 layers):
  L0-L6:   97% projector (passive embedding transformation)
  L7-L18:  40% transform+suppress (active computation)
  L19-L29: 85-95% projector (knowledge bridges)
  L30-L33: 11% identity+inverter (format gate)

THIS EXPERIMENT: Apply the same decomposition to Pythia-160M (12 layers,
non-gated FFN with GELU) and compare with our existing KIBC/crystal analysis.

NOTE ON ARCHITECTURE:
  Pythia uses a standard (non-gated) FFN:
    h = GELU(x @ W_up.T + b_up) @ W_down.T + b_down
  Where W_up = dense_h_to_4h (3072 × 768), W_down = dense_4h_to_h (768 × 3072)
  
  LARQL's Gemma uses a gated FFN:
    h = (SiLU(x @ W_gate.T) * (x @ W_up.T)) @ W_down.T
  Where W_gate is the "key" for their analysis.
  
  For Pythia, W_up plays both roles (gate AND up). Each row of W_up is both
  the trigger pattern and the projection direction. This makes the cos(key, value)
  analysis directly applicable: key = W_up row, value = W_down column.

Measurements:
  1. cos(W_up[j, :], W_down[:, j]) for each feature j → circuit type
  2. W_embed @ W_down[:, j] → top-K token labels per feature
  3. Per-layer circuit type distribution → depth profile
  4. "Dark space" analysis: what fraction of features don't align with any token?

Usage:
  uv run python scripts/experiments/ffn_decomposition.py
  uv run python scripts/experiments/ffn_decomposition.py --model EleutherAI/pythia-160m

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
from scipy import stats as scipy_stats

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


# ─── Circuit type classification (from LARQL) ──────────────────

CIRCUIT_TYPES = {
    "identity":   (0.5, 1.0),     # cos > 0.5: reads X, writes X back
    "transform":  (0.2, 0.5),     # cos 0.2-0.5: partial rotation
    "projector":  (-0.2, 0.2),    # cos near 0: orthogonal (factual bridge)
    "suppressor": (-0.5, -0.2),   # weak flip
    "inverter":   (-1.0, -0.5),   # strong flip
}


def classify_circuit(cos_val: float) -> str:
    """Classify a feature by its cos(up, down) into LARQL circuit types."""
    for name, (lo, hi) in CIRCUIT_TYPES.items():
        if lo <= cos_val < hi or (name == "identity" and cos_val >= hi):
            return name
        if name == "inverter" and cos_val < lo:
            return name
    return "projector"  # fallback


def run_experiment(model_id: str, top_k: int = 10):
    log("=" * 72)
    log("FFN DECOMPOSITION: LARQL-STYLE ANALYSIS")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Top-K tokens per feature: {top_k}")
    log()

    from transformers import AutoModelForCausalLM, AutoTokenizer

    # ── Load model ──────────────────────────────────────────────
    log("Loading model...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float32, device_map="cpu",
        low_cpu_mem_usage=True,
    )
    model.eval()
    log(f"  Loaded in {time.time() - t0:.1f}s")

    config = model.config
    n_layers = config.num_hidden_layers
    hidden_size = config.hidden_size
    intermediate_size = config.intermediate_size
    vocab_size = config.vocab_size
    log(f"  {n_layers} layers, hidden={hidden_size}, intermediate={intermediate_size}, vocab={vocab_size}")

    # ── Get embedding matrix ────────────────────────────────────
    # Pythia has untied embeddings: embed_in for input, embed_out for output
    W_embed = model.gpt_neox.embed_in.weight.data.float()  # (vocab, hidden)
    W_lm_head = model.embed_out.weight.data.float()  # (vocab, hidden)
    log(f"  W_embed: {W_embed.shape}")
    log(f"  W_lm_head: {W_lm_head.shape}")

    # For LARQL-style "what does this feature mean", we project down columns
    # against the LM head (output embedding), since that's what determines
    # the logit contribution. For tied-embedding models these are the same.
    # For Pythia they differ, so we use the LM head for semantic meaning.

    # ── Per-layer analysis ──────────────────────────────────────
    all_results = []

    for layer_idx in range(n_layers):
        log(f"\n{'─' * 72}")
        log(f"LAYER {layer_idx}")
        log(f"{'─' * 72}")
        t_layer = time.time()

        mlp = model.gpt_neox.layers[layer_idx].mlp
        W_up = mlp.dense_h_to_4h.weight.data.float()    # (intermediate, hidden)
        W_down = mlp.dense_4h_to_h.weight.data.float()   # (hidden, intermediate)

        log(f"  W_up: {W_up.shape}, W_down: {W_down.shape}")

        # ── 1. Circuit type via cos(up_row[j], down_col[j]) ────
        # W_up[j, :] is the j-th feature's "key" (what triggers it)
        # W_down[:, j] is the j-th feature's "value" (what it outputs)
        up_rows = W_up  # (intermediate, hidden) — each row is one feature
        down_cols = W_down.T  # (intermediate, hidden) — each row is one feature's output dir

        # Normalize for cosine
        up_norm = torch.nn.functional.normalize(up_rows, dim=1)
        down_norm = torch.nn.functional.normalize(down_cols, dim=1)

        # Per-feature cosine: dot product of normalized vectors
        cos_up_down = (up_norm * down_norm).sum(dim=1).numpy()  # (intermediate,)

        # Classify
        circuit_counts = {name: 0 for name in CIRCUIT_TYPES}
        for cos_val in cos_up_down:
            ct = classify_circuit(float(cos_val))
            circuit_counts[ct] += 1

        total = len(cos_up_down)
        log(f"\n  CIRCUIT TYPE DISTRIBUTION:")
        for name in ["identity", "transform", "projector", "suppressor", "inverter"]:
            count = circuit_counts[name]
            pct = count / total * 100
            bar = "█" * int(pct / 2)
            log(f"    {name:12s}: {count:5d} ({pct:5.1f}%) {bar}")

        log(f"\n  cos(up, down) stats: mean={cos_up_down.mean():.4f}, "
            f"std={cos_up_down.std():.4f}, "
            f"min={cos_up_down.min():.4f}, max={cos_up_down.max():.4f}")

        # ── 2. Token labels via W_lm_head @ down_col ───────────
        # For each feature j, compute logits = W_lm_head @ W_down[:, j]
        # This tells us what token this feature's output direction points toward.
        # We do this in batches to avoid OOM.
        log(f"\n  Computing feature → token labels...")

        batch_size = 512
        top_tokens = []
        c_scores = []
        dark_count = 0
        dark_threshold = 0.85  # LARQL's threshold for "dark" features

        for batch_start in range(0, intermediate_size, batch_size):
            batch_end = min(batch_start + batch_size, intermediate_size)
            down_batch = W_down[:, batch_start:batch_end]  # (hidden, batch)

            # logits = W_lm_head @ down_batch → (vocab, batch)
            logits = W_lm_head @ down_batch

            for j_in_batch in range(batch_end - batch_start):
                j = batch_start + j_in_batch
                col_logits = logits[:, j_in_batch]

                # Get top-K
                topk_vals, topk_ids = torch.topk(col_logits, top_k)

                # Decode tokens
                entries = []
                for rank in range(top_k):
                    tok_id = topk_ids[rank].item()
                    logit_val = topk_vals[rank].item()
                    tok_str = tokenizer.decode([tok_id]).strip()
                    entries.append({
                        "token": tok_str,
                        "token_id": tok_id,
                        "logit": round(logit_val, 3),
                    })

                # c_score = top logit magnitude (how strongly this feature points to a token)
                c_score = topk_vals[0].item()
                c_scores.append(c_score)

                # Compute "darkness" — how far is down_col from nearest embedding?
                down_col_norm = down_cols[j]  # already normalized above
                # Max cosine with any embedding
                embed_cos = (W_lm_head @ down_cols[j].unsqueeze(1)).squeeze()
                embed_norms = W_lm_head.norm(dim=1)
                down_col_actual_norm = down_cols[j].norm()
                # Cosine similarity with each embedding row
                cos_with_embed = embed_cos / (embed_norms * down_col_actual_norm + 1e-10)
                max_cos = cos_with_embed.abs().max().item()

                is_dark = max_cos < (1.0 - dark_threshold)
                if is_dark:
                    dark_count += 1

                top_tokens.append({
                    "feature": j,
                    "top_token": entries[0]["token"] if entries else "",
                    "c_score": round(c_score, 3),
                    "max_embed_cos": round(max_cos, 4),
                    "top_k": entries[:5],  # store top-5 for results
                })

        c_scores = np.array(c_scores)
        log(f"  Feature → token c_scores: mean={c_scores.mean():.3f}, "
            f"median={np.median(c_scores):.3f}, "
            f"max={c_scores.max():.3f}")
        log(f"  Dark features (max_embed_cos < {1-dark_threshold:.2f}): "
            f"{dark_count}/{intermediate_size} ({dark_count/intermediate_size:.1%})")

        # Show some example labels
        log(f"\n  TOP FEATURES BY c_score:")
        sorted_feats = sorted(top_tokens, key=lambda x: -x["c_score"])
        for feat in sorted_feats[:15]:
            tokens_str = ", ".join(f"{e['token']!r}({e['logit']:.1f})" for e in feat["top_k"][:3])
            cos_val = cos_up_down[feat["feature"]]
            ct = classify_circuit(float(cos_val))
            log(f"    F{feat['feature']:04d}: {tokens_str}  "
                f"[cos={cos_val:.3f}, {ct}]")

        # ── 3. Collect per-layer results ────────────────────────
        layer_result = {
            "layer": layer_idx,
            "circuit_counts": circuit_counts,
            "circuit_pcts": {name: round(count / total * 100, 2)
                           for name, count in circuit_counts.items()},
            "cos_stats": {
                "mean": round(float(cos_up_down.mean()), 4),
                "std": round(float(cos_up_down.std()), 4),
                "min": round(float(cos_up_down.min()), 4),
                "max": round(float(cos_up_down.max()), 4),
            },
            "c_score_stats": {
                "mean": round(float(c_scores.mean()), 3),
                "median": round(float(np.median(c_scores)), 3),
                "max": round(float(c_scores.max()), 3),
            },
            "dark_count": dark_count,
            "dark_pct": round(dark_count / intermediate_size * 100, 1),
            "top_features": sorted_feats[:50],
            "cos_values": cos_up_down.tolist(),
        }
        all_results.append(layer_result)

        log(f"\n  Layer {layer_idx} done in {time.time() - t_layer:.1f}s")

    # ── Summary depth profile ───────────────────────────────────
    log(f"\n\n{'═' * 72}")
    log("DEPTH PROFILE SUMMARY")
    log(f"{'═' * 72}")
    log(f"\n{'Layer':>5s}  {'Proj%':>6s}  {'Trans%':>7s}  {'Supp%':>6s}  "
        f"{'Ident%':>7s}  {'Inv%':>6s}  {'Dark%':>6s}  {'cosMean':>8s}  Role")
    log(f"{'─'*5}  {'─'*6}  {'─'*7}  {'─'*6}  {'─'*7}  {'─'*6}  {'─'*6}  {'─'*8}  {'─'*15}")

    for r in all_results:
        p = r["circuit_pcts"]

        # Heuristic role assignment based on LARQL's taxonomy
        active = p["transform"] + p["suppressor"]
        gate = p["identity"] + p["inverter"]

        if p["projector"] > 85:
            role = "KNOWLEDGE" if r["layer"] >= 6 else "passive"
        elif active > 25:
            role = "ACTIVE"
        elif gate > 8:
            role = "FORMAT GATE"
        else:
            role = ""

        log(f"  L{r['layer']:2d}   {p['projector']:5.1f}   {p['transform']:6.1f}   "
            f"{p['suppressor']:5.1f}   {p['identity']:6.1f}   {p['inverter']:5.1f}   "
            f"{r['dark_pct']:5.1f}   {r['cos_stats']['mean']:7.4f}  {role}")

    # ── Verbum phase comparison ─────────────────────────────────
    log(f"\n\n{'═' * 72}")
    log("COMPARISON: LARQL CIRCUIT TYPES vs VERBUM PHASES")
    log(f"{'═' * 72}")
    log("""
  Verbum phases (from residual covariance, session 185):
    EXPAND  (L0-2):   high-rank, V reads residual
    ORTHO   (L3-8):   rank-1, V in null space, invisible computation
    ALIGN   (L9-10):  rank growth, V transitions to residual space
    COLLAPSE (L11):   destructive interference, cos(h,f) ≈ -1

  LARQL phases (from cos(gate,down) on Gemma 3 4B):
    Passive     (L0-6):   97% projector
    Active      (L7-18):  40% transform+suppress
    Knowledge   (L19-29): 85-95% projector
    Format gate (L30-33): 11% identity+inverter

  Hypothesis mapping (scaled 34→12 layers):
    EXPAND  (L0-2)  ↔ Passive (cos(up,down)≈0, projector dominated)
    ORTHO   (L3-8)  ↔ Active (higher transform+suppress — computation)
    ALIGN   (L9-10) ↔ Knowledge (projector rises — factual bridges)
    COLLAPSE(L11)   ↔ Format gate (identity+inverter spike)
    """)

    # Compute phase averages
    phase_map = {
        "EXPAND (L0-2)": list(range(0, 3)),
        "ORTHO (L3-8)": list(range(3, 9)),
        "ALIGN (L9-10)": list(range(9, 11)),
        "COLLAPSE (L11)": [11],
    }

    for phase_name, layers in phase_map.items():
        phase_results = [all_results[l] for l in layers]
        avg_proj = np.mean([r["circuit_pcts"]["projector"] for r in phase_results])
        avg_active = np.mean([r["circuit_pcts"]["transform"] + r["circuit_pcts"]["suppressor"]
                            for r in phase_results])
        avg_gate = np.mean([r["circuit_pcts"]["identity"] + r["circuit_pcts"]["inverter"]
                          for r in phase_results])
        avg_dark = np.mean([r["dark_pct"] for r in phase_results])
        log(f"  {phase_name:20s}: proj={avg_proj:5.1f}%  active(T+S)={avg_active:5.1f}%  "
            f"gate(I+Inv)={avg_gate:5.1f}%  dark={avg_dark:5.1f}%")

    # ── Save results ────────────────────────────────────────────
    results_dir = os.path.join(os.path.dirname(__file__), "..", "..", "results", "ffn-decomposition")
    os.makedirs(results_dir, exist_ok=True)

    # Summary without the large cos_values arrays
    summary = {
        "model": model_id,
        "n_layers": n_layers,
        "hidden_size": hidden_size,
        "intermediate_size": intermediate_size,
        "vocab_size": vocab_size,
        "layers": [{k: v for k, v in r.items() if k != "cos_values"} for r in all_results],
        "phase_summary": {},
    }
    for phase_name, layers in phase_map.items():
        phase_results = [all_results[l] for l in layers]
        summary["phase_summary"][phase_name] = {
            "avg_projector": round(np.mean([r["circuit_pcts"]["projector"] for r in phase_results]), 2),
            "avg_transform": round(np.mean([r["circuit_pcts"]["transform"] for r in phase_results]), 2),
            "avg_suppressor": round(np.mean([r["circuit_pcts"]["suppressor"] for r in phase_results]), 2),
            "avg_identity": round(np.mean([r["circuit_pcts"]["identity"] for r in phase_results]), 2),
            "avg_inverter": round(np.mean([r["circuit_pcts"]["inverter"] for r in phase_results]), 2),
            "avg_dark_pct": round(np.mean([r["dark_pct"] for r in phase_results]), 2),
        }

    summary_path = os.path.join(results_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    log(f"\n  Summary saved to {summary_path}")

    # Per-feature cos values (for cross-reference with KIBC)
    cos_path = os.path.join(results_dir, "cos_values.npz")
    cos_arrays = {f"layer_{r['layer']}": np.array(r["cos_values"]) for r in all_results}
    np.savez_compressed(cos_path, **cos_arrays)
    log(f"  cos(up,down) arrays saved to {cos_path}")

    log(f"\n{'═' * 72}")
    log("DONE")
    log(f"{'═' * 72}")

    return all_results


def main():
    parser = argparse.ArgumentParser(description="FFN Decomposition: LARQL-style analysis")
    parser.add_argument("--model", default="EleutherAI/pythia-160m",
                       help="HuggingFace model ID")
    parser.add_argument("--top-k", type=int, default=10,
                       help="Top-K tokens per feature for labeling")
    args = parser.parse_args()

    run_experiment(args.model, args.top_k)


if __name__ == "__main__":
    main()
