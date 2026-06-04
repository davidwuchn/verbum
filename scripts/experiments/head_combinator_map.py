#!/usr/bin/env python3
"""Head→Combinator Mapping: Build the ISA of the attention executor.

QUESTION: Which attention heads implement which combinator reductions?

Session 187 found 5 head types at L30/L33 on 5 probes. This experiment
scales to ALL 535 crystal probes (9 combinator types × 50-71 probes each)
to build a statistical head→combinator assignment table.

METHODOLOGY:
  For each crystal probe, run a forward pass with the compile gate.
  At layers L27/L30/L33 (the reduction resolution layers from s187),
  measure each head's contribution to the residual stream:

    head_contrib[h] = W_o[:, h*d:(h+1)*d] @ (softmax(QK^T) @ V)[h]

  The NORM of this contribution = how much this head is "active" for
  this input. Aggregating norms by combinator type reveals which heads
  specialise for which operations.

MEASUREMENTS (per probe, per layer):
  1. Per-head residual contribution norm: ||head_contrib[h]||₂
     → scalar per (head, layer, probe). Very compact.
  2. Per-head top-1 unembed token at last probe position
     → which vocabulary item each head promotes at the prediction point.
  3. Per-head gate attention fraction
     → how much each head reads the compile gate vs probe content.

AGGREGATION:
  For each (head, layer): mean activation norm grouped by combinator.
  Result: matrix[head, combinator] at each layer.
  Selectivity = max(combinator_means) / mean(combinator_means).
  High selectivity = head specialises for one combinator type.

ARCHITECTURE (Qwen3-8B):
  GQA: 32 Q heads, 8 KV groups (4 Q heads share each KV pair)
  head_dim=128, hidden=4096, 36 layers

Usage:
  uv run python scripts/experiments/head_combinator_map.py
  uv run python scripts/experiments/head_combinator_map.py --layers 27,30,33
  uv run python scripts/experiments/head_combinator_map.py --max-probes 20

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
import torch.nn.functional as F

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


def run_experiment(
    model_id: str = "Qwen/Qwen3-8B",
    layer_indices: list[int] | None = None,
    max_probes_per_combinator: int | None = None,
    top_k: int = 5,
):
    log("=" * 72)
    log("HEAD → COMBINATOR MAPPING")
    log("=" * 72)
    log(f"Model: {model_id}")
    log()

    from transformers import AutoModelForCausalLM, AutoTokenizer
    from verbum.probes.library import crystal_probes, by_combinator

    # ── Collect probes by combinator ────────────────────────────
    CRYSTAL_COMBINATORS = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
    probes_by_comb: dict[str, list] = {}
    for comb in CRYSTAL_COMBINATORS:
        all_comb = by_combinator(comb)
        # Filter to crystal set and skip pure lambda notation
        crystal = [p for p in all_comb
                   if p.combinator in set(CRYSTAL_COMBINATORS)
                   and not p.prompt.startswith("λ")
                   and not p.prompt.startswith("(λ")]
        if max_probes_per_combinator is not None:
            crystal = crystal[:max_probes_per_combinator]
        probes_by_comb[comb] = crystal
        log(f"  {comb:5s}: {len(crystal)} probes")

    total_probes = sum(len(v) for v in probes_by_comb.values())
    log(f"  Total: {total_probes} probes")

    # ── Load model ──────────────────────────────────────────────
    log("\nLoading model...")
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
    n_kv_heads = config.num_key_value_heads
    head_dim = config.hidden_size // n_q_heads
    hidden_size = config.hidden_size
    q_per_kv = n_q_heads // n_kv_heads
    log(f"  {n_layers} layers, {n_q_heads} Q heads, {n_kv_heads} KV groups")
    log(f"  GQA ratio: {q_per_kv} Q heads per KV group, head_dim={head_dim}")

    if layer_indices is None:
        layer_indices = [27, 30, 33]
    layer_indices = [l for l in layer_indices if l < n_layers]
    log(f"  Target layers: {layer_indices}")

    # ── Get unembedding matrix ──────────────────────────────────
    if hasattr(model, "lm_head"):
        W_unembed = model.lm_head.weight.data.cpu().float()  # (vocab, hidden)
    else:
        W_unembed = model.model.embed_tokens.weight.data.cpu().float()
    log(f"  W_unembed: {W_unembed.shape}")

    # ── Pre-extract O projection slices per head per layer ──────
    # W_o_heads[layer][head] = (hidden, head_dim) slice
    W_o_heads: dict[int, list[torch.Tensor]] = {}
    for li in layer_indices:
        W_o = model.model.layers[li].self_attn.o_proj.weight.data.cpu().float()
        W_o_heads[li] = [
            W_o[:, h * head_dim : (h + 1) * head_dim]
            for h in range(n_q_heads)
        ]
    log("  O projection slices pre-extracted.")

    # ── Compile gate ────────────────────────────────────────────
    compile_gate = (
        "The dog runs. → λx. runs(dog)\n"
        "Be helpful but concise. → λ assist(x). helpful(x) | concise(x)\n"
        "\nInput: "
    )
    gate_only = tokenizer(compile_gate, return_tensors="pt")
    gate_len = gate_only["input_ids"].shape[1]
    log(f"  Gate length: {gate_len} tokens")

    # ── Storage ─────────────────────────────────────────────────
    # Per-probe records: list of dicts
    # Each record: {probe_id, combinator, prompt, layer→{head→{norm, top1_token, gate_frac}}}
    all_records: list[dict] = []

    # ── Measurement loop ────────────────────────────────────────
    log(f"\n{'─' * 72}")
    log("RUNNING PROBES")
    log("─" * 72)

    probe_count = 0
    t_start = time.time()

    for comb, probes in probes_by_comb.items():
        log(f"\n  [{comb}] {len(probes)} probes...")

        for pi, probe in enumerate(probes):
            probe_count += 1
            if probe_count % 25 == 0 or probe_count == 1:
                elapsed = time.time() - t_start
                rate = probe_count / elapsed if elapsed > 0 else 0
                eta = (total_probes - probe_count) / rate if rate > 0 else 0
                log(f"    [{probe_count}/{total_probes}] "
                    f"{elapsed:.0f}s elapsed, {rate:.1f} probes/s, "
                    f"ETA {eta:.0f}s")

            full_text = compile_gate + probe.prompt
            inputs = tokenizer(full_text, return_tensors="pt")
            input_ids = inputs["input_ids"].to(model.device)
            seq_len = input_ids.shape[1]
            tokens = [tokenizer.decode(t) for t in input_ids[0]]

            # ── Hook attention layers ───────────────────────────
            captured: dict[int, dict] = {}  # layer → {head_outputs, attn_weights}
            hooks = []

            for li in layer_indices:
                attn_module = model.model.layers[li].self_attn

                def make_hook(layer_idx):
                    def hook_fn(module, args, kwargs, output):
                        if args:
                            hidden_states = args[0]
                        else:
                            hidden_states = kwargs.get("hidden_states")
                        input_shape = hidden_states.shape[:-1]
                        hidden_shape = (*input_shape, -1, head_dim)

                        with torch.no_grad():
                            # V computation
                            v = module.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)
                            # v: (batch, n_kv_heads, seq, head_dim)

                            # Attention weights from output
                            attn_weights = output[1]  # (batch, n_q_heads, seq, seq)

                            if attn_weights is not None:
                                # Expand V for GQA
                                v_expanded = v.repeat_interleave(q_per_kv, dim=1)
                                # Per-head output: (batch, n_q_heads, seq, head_dim)
                                per_head = torch.matmul(attn_weights, v_expanded)

                                captured[layer_idx] = {
                                    "head_outputs": per_head[0].cpu().float(),
                                    "attn_weights": attn_weights[0].cpu().float(),
                                }
                        return output
                    return hook_fn

                h = attn_module.register_forward_hook(make_hook(li), with_kwargs=True)
                hooks.append(h)

            # ── Forward pass ────────────────────────────────────
            with torch.no_grad():
                model(input_ids, output_attentions=True, return_dict=True)

            for h in hooks:
                h.remove()

            # ── Extract measurements ────────────────────────────
            record = {
                "probe_id": probe.id,
                "combinator": comb,
                "prompt": probe.prompt[:80],
                "n_probe_tokens": seq_len - gate_len,
                "layers": {},
            }

            for li in layer_indices:
                if li not in captured:
                    continue

                head_out = captured[li]["head_outputs"]   # (n_q_heads, seq, head_dim)
                attn_w = captured[li]["attn_weights"]      # (n_q_heads, seq, seq)

                layer_data = {}

                for h in range(n_q_heads):
                    # ── 1. Contribution norm (averaged over probe positions) ──
                    # Project head output through O projection slice → residual contribution
                    h_out = head_out[h]  # (seq, head_dim)
                    W_o_h = W_o_heads[li][h]  # (hidden, head_dim)

                    # Head contribution at each position: W_o_h @ h_out[pos]
                    # = (hidden, head_dim) @ (head_dim,) → (hidden,)
                    # Norm over hidden dim, mean over probe positions
                    probe_out = h_out[gate_len:]  # (n_probe, head_dim)
                    contrib = (W_o_h @ probe_out.T).T  # (n_probe, hidden)
                    norms = contrib.norm(dim=1)  # (n_probe,)
                    mean_norm = norms.mean().item()
                    max_norm = norms.max().item()

                    # ── 2. Top-1 unembed at last probe position ──
                    last_pos = seq_len - 1
                    last_contrib = W_o_h @ h_out[last_pos]  # (hidden,)
                    logits = W_unembed @ last_contrib  # (vocab,)
                    top_val, top_idx = logits.topk(1)
                    top1_token = tokenizer.decode(top_idx[0].item()).strip()
                    top1_logit = top_val[0].item()

                    # ── 3. Gate attention fraction ──
                    # Average over probe positions: how much does this head
                    # attend to the gate prefix vs probe content?
                    attn_probe_rows = attn_w[h, gate_len:]  # (n_probe, seq)
                    gate_mass = attn_probe_rows[:, :gate_len].sum(dim=1)  # (n_probe,)
                    probe_mass = attn_probe_rows[:, gate_len:].sum(dim=1)
                    gate_frac = (gate_mass / (gate_mass + probe_mass + 1e-8)).mean().item()

                    layer_data[h] = {
                        "mean_norm": round(mean_norm, 4),
                        "max_norm": round(max_norm, 4),
                        "top1_token": top1_token,
                        "top1_logit": round(top1_logit, 2),
                        "gate_frac": round(gate_frac, 4),
                    }

                record["layers"][li] = layer_data

            all_records.append(record)

            # Free memory
            del captured
            if probe_count % 50 == 0:
                torch.mps.empty_cache() if hasattr(torch, "mps") else None

    elapsed_total = time.time() - t_start
    log(f"\n  Done: {probe_count} probes in {elapsed_total:.0f}s "
        f"({probe_count / elapsed_total:.1f} probes/s)")

    # ══════════════════════════════════════════════════════════════
    # ANALYSIS
    # ══════════════════════════════════════════════════════════════

    log(f"\n{'=' * 72}")
    log("ANALYSIS: HEAD → COMBINATOR ACTIVATION MATRIX")
    log("=" * 72)

    for li in layer_indices:
        log(f"\n{'─' * 60}")
        log(f"LAYER {li}")
        log("─" * 60)

        # Build activation matrix: head × combinator
        # activation[h][comb] = list of mean_norm values
        activation: dict[int, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

        for rec in all_records:
            comb = rec["combinator"]
            if li not in rec["layers"]:
                continue
            layer_data = rec["layers"][li]
            for h in range(n_q_heads):
                if h in layer_data:
                    activation[h][comb].append(layer_data[h]["mean_norm"])

        # Compute mean per (head, combinator)
        mean_activation = {}  # head → {combinator → mean_norm}
        for h in range(n_q_heads):
            mean_activation[h] = {}
            for comb in CRYSTAL_COMBINATORS:
                vals = activation[h].get(comb, [])
                mean_activation[h][comb] = float(np.mean(vals)) if vals else 0.0

        # ── Selectivity: which heads specialise? ────────────────
        # selectivity[h] = max(comb_means) / mean(comb_means)
        # Also: preferred_comb[h] = argmax
        selectivity = {}
        preferred = {}
        for h in range(n_q_heads):
            vals = [mean_activation[h][c] for c in CRYSTAL_COMBINATORS]
            mean_all = np.mean(vals)
            max_val = np.max(vals)
            selectivity[h] = max_val / mean_all if mean_all > 0 else 0
            preferred[h] = CRYSTAL_COMBINATORS[int(np.argmax(vals))]

        # ── Print activation matrix ─────────────────────────────
        header = f"{'Head':>6s}"
        for c in CRYSTAL_COMBINATORS:
            header += f" {c:>6s}"
        header += f" {'Select':>8s} {'Pref':>6s}"
        log(f"\n  {header}")
        log(f"  {'─' * len(header)}")

        # Sort by selectivity (most selective first)
        sorted_heads = sorted(range(n_q_heads), key=lambda h: selectivity[h], reverse=True)

        for h in sorted_heads:
            row = f"  H{h:02d}  "
            vals = [mean_activation[h][c] for c in CRYSTAL_COMBINATORS]
            max_val = max(vals)
            for v in vals:
                if v == max_val and max_val > 0:
                    row += f" {v:6.2f}*"  # mark the max
                else:
                    row += f" {v:6.2f} "
            row += f" {selectivity[h]:8.3f} {preferred[h]:>6s}"
            log(row)

        # ── Top selective heads ─────────────────────────────────
        log(f"\n  TOP 10 MOST SELECTIVE HEADS (L{li}):")
        for rank, h in enumerate(sorted_heads[:10]):
            vals = [mean_activation[h][c] for c in CRYSTAL_COMBINATORS]
            max_val = max(vals)
            mean_all = np.mean(vals)
            log(f"    #{rank+1} H{h:02d}: prefers {preferred[h]}, "
                f"selectivity={selectivity[h]:.3f}, "
                f"max_norm={max_val:.3f}, mean_norm={mean_all:.3f}")

        # ── Combinator → best heads ─────────────────────────────
        log(f"\n  COMBINATOR → BEST HEADS (L{li}):")
        for comb in CRYSTAL_COMBINATORS:
            # Rank heads by activation for this combinator
            head_vals = [(h, mean_activation[h][comb]) for h in range(n_q_heads)]
            head_vals.sort(key=lambda x: x[1], reverse=True)
            top5 = head_vals[:5]
            top_str = ", ".join(f"H{h:02d}({v:.3f})" for h, v in top5)
            log(f"    {comb:>5s}: {top_str}")

    # ── Cross-layer analysis: consistent head assignments ───────
    log(f"\n{'=' * 72}")
    log("CROSS-LAYER CONSISTENCY")
    log("=" * 72)

    if len(layer_indices) > 1:
        # For each head, check if it prefers the same combinator across layers
        for h in range(n_q_heads):
            prefs = []
            for li in layer_indices:
                # Recompute preferred for this layer
                activation_h = defaultdict(list)
                for rec in all_records:
                    if li in rec["layers"] and h in rec["layers"][li]:
                        activation_h[rec["combinator"]].append(
                            rec["layers"][li][h]["mean_norm"])
                means = {c: float(np.mean(activation_h.get(c, [0])))
                         for c in CRYSTAL_COMBINATORS}
                best = max(means, key=lambda c: means[c])
                prefs.append((li, best, means[best]))
            # Print only if consistent or notably inconsistent
            unique_prefs = set(p[1] for p in prefs)
            if len(unique_prefs) == 1:
                log(f"  H{h:02d}: consistent → {prefs[0][1]} across all layers")

    # ── Gate attention analysis: which heads read the gate? ─────
    log(f"\n{'=' * 72}")
    log("GATE ATTENTION ANALYSIS")
    log("=" * 72)
    log("Heads that read the compile gate (instruction followers):")

    for li in layer_indices:
        gate_fracs = defaultdict(list)
        for rec in all_records:
            if li not in rec["layers"]:
                continue
            for h in range(n_q_heads):
                if h in rec["layers"][li]:
                    gate_fracs[h].append(rec["layers"][li][h]["gate_frac"])

        log(f"\n  L{li}:")
        head_gate = [(h, float(np.mean(gate_fracs[h])))
                     for h in range(n_q_heads) if gate_fracs[h]]
        head_gate.sort(key=lambda x: x[1], reverse=True)
        for h, frac in head_gate[:10]:
            log(f"    H{h:02d}: gate_frac={frac:.3f}")

    # ── Top-1 token consensus per head ──────────────────────────
    log(f"\n{'=' * 72}")
    log("TOKEN CONSENSUS: What does each head consistently produce?")
    log("=" * 72)

    for li in layer_indices:
        from collections import Counter
        log(f"\n  L{li}:")
        for h in range(n_q_heads):
            tokens_by_comb = defaultdict(list)
            for rec in all_records:
                if li in rec["layers"] and h in rec["layers"][li]:
                    tokens_by_comb[rec["combinator"]].append(
                        rec["layers"][li][h]["top1_token"])

            # Find most common token overall
            all_tokens = []
            for v in tokens_by_comb.values():
                all_tokens.extend(v)
            if not all_tokens:
                continue
            counter = Counter(all_tokens)
            top_token, top_count = counter.most_common(1)[0]
            consensus = top_count / len(all_tokens)

            if consensus > 0.3:  # Only print heads with notable consensus
                # Per-combinator breakdown for consensus heads
                per_comb = {}
                for c in CRYSTAL_COMBINATORS:
                    if c in tokens_by_comb:
                        cc = Counter(tokens_by_comb[c])
                        top_c = cc.most_common(1)[0]
                        per_comb[c] = f"{top_c[0]}({top_c[1]})"
                comb_str = " | ".join(f"{c}:{per_comb.get(c, '?')}"
                                      for c in CRYSTAL_COMBINATORS[:5])
                log(f"    H{h:02d}: \"{top_token}\" {consensus:.0%} consensus | {comb_str}")

    # ══════════════════════════════════════════════════════════════
    # SAVE RESULTS
    # ══════════════════════════════════════════════════════════════

    results_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "results", "head-combinator-map"
    )
    os.makedirs(results_dir, exist_ok=True)

    # ── Save compact activation matrix (the key artifact) ───────
    matrix = {}
    for li in layer_indices:
        layer_matrix = {}
        for h in range(n_q_heads):
            head_data = {}
            for comb in CRYSTAL_COMBINATORS:
                vals = []
                for rec in all_records:
                    if li in rec["layers"] and h in rec["layers"][li]:
                        if rec["combinator"] == comb:
                            vals.append(rec["layers"][li][h]["mean_norm"])
                head_data[comb] = {
                    "mean": round(float(np.mean(vals)), 4) if vals else 0,
                    "std": round(float(np.std(vals)), 4) if vals else 0,
                    "n": len(vals),
                }
            layer_matrix[f"H{h:02d}"] = head_data
        matrix[f"L{li}"] = layer_matrix

    # ── Selectivity scores ──────────────────────────────────────
    selectivity_scores = {}
    for li in layer_indices:
        layer_sel = {}
        for h in range(n_q_heads):
            vals = [matrix[f"L{li}"][f"H{h:02d}"][c]["mean"]
                    for c in CRYSTAL_COMBINATORS]
            mean_all = np.mean(vals)
            max_val = np.max(vals)
            best_comb = CRYSTAL_COMBINATORS[int(np.argmax(vals))]
            layer_sel[f"H{h:02d}"] = {
                "selectivity": round(max_val / mean_all, 4) if mean_all > 0 else 0,
                "preferred": best_comb,
                "max_norm": round(float(max_val), 4),
                "mean_norm": round(float(mean_all), 4),
            }
        selectivity_scores[f"L{li}"] = layer_sel

    # ── Gate attention summary ──────────────────────────────────
    gate_summary = {}
    for li in layer_indices:
        layer_gate = {}
        for h in range(n_q_heads):
            fracs = []
            for rec in all_records:
                if li in rec["layers"] and h in rec["layers"][li]:
                    fracs.append(rec["layers"][li][h]["gate_frac"])
            layer_gate[f"H{h:02d}"] = round(float(np.mean(fracs)), 4) if fracs else 0
        gate_summary[f"L{li}"] = layer_gate

    summary = {
        "model": model_id,
        "layers": layer_indices,
        "n_q_heads": n_q_heads,
        "n_kv_heads": n_kv_heads,
        "combinators": CRYSTAL_COMBINATORS,
        "probes_per_combinator": {c: len(probes_by_comb[c]) for c in CRYSTAL_COMBINATORS},
        "total_probes": total_probes,
        "elapsed_seconds": round(elapsed_total, 1),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "activation_matrix": matrix,
        "selectivity": selectivity_scores,
        "gate_attention": gate_summary,
    }

    summary_path = os.path.join(results_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    # ── Also save per-probe records (JSONL for analysis) ────────
    records_path = os.path.join(results_dir, "records.jsonl")
    with open(records_path, "w") as f:
        for rec in all_records:
            # Convert layer keys to strings for JSON
            rec_out = dict(rec)
            rec_out["layers"] = {str(k): v for k, v in rec["layers"].items()}
            f.write(json.dumps(rec_out, default=str) + "\n")

    log(f"\n{'=' * 72}")
    log(f"RESULTS SAVED to {results_dir}/")
    log(f"  summary.json: {os.path.getsize(summary_path) / 1024:.1f} KB")
    log(f"  records.jsonl: {os.path.getsize(records_path) / 1024:.1f} KB")
    log(f"  ({total_probes} probes × {len(layer_indices)} layers × {n_q_heads} heads)")
    log("=" * 72)

    return summary


def main():
    parser = argparse.ArgumentParser(description="Head→Combinator Mapping")
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", default=None,
                        help="Comma-separated layer indices (default: 27,30,33)")
    parser.add_argument("--max-probes", type=int, default=None,
                        help="Max probes per combinator (default: all)")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    layer_indices = None
    if args.layers:
        layer_indices = [int(l) for l in args.layers.split(",")]

    run_experiment(
        model_id=args.model,
        layer_indices=layer_indices,
        max_probes_per_combinator=args.max_probes,
        top_k=args.top_k,
    )


if __name__ == "__main__":
    main()
