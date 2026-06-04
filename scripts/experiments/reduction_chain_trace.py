#!/usr/bin/env python3
"""Reduction Chain Trace: Map how reductions compose across all 36 layers.

HYPOTHESIS: Different combinator types (K, I, B, C, Y) create different
reduction chains across the depth of the model. The Y combinator (recursion)
should show cross-layer feedback — a position's output at layer L resembling
its own earlier input.

MEASUREMENTS:
  1. CUMULATIVE RESIDUAL → UNEMBED at each layer: How does the model's
     output evolve? At which layer does "runs(dog)" first appear?
  
  2. PER-LAYER DELTA: What does each layer ADD to the residual?
     delta[L] = residual_after_layer[L] - residual_before_layer[L]
     Project delta through unembed → "what this layer contributed"
  
  3. COMBINATOR-SPECIFIC CHAINS: Do K probes show different chain
     patterns than B probes? Y probes?
  
  4. SELF-SIMILARITY ACROSS DEPTH (Y-combinator signature):
     cos(residual[L, pos], residual[L+k, pos]) — does the representation
     at a position cycle back to a similar state after k layers?
     If Y is present, we'd see periodic self-similarity.
  
  5. COMPOSITION DEPTH: At which layer does the first composed meaning
     appear (something neither individual position had alone)?

PROBES: 5 probes per combinator type from our crystal library.
  K (discard), I (identity), B (compose), C (flip), Y (fixpoint)

Usage:
  uv run python scripts/experiments/reduction_chain_trace.py
  uv run python scripts/experiments/reduction_chain_trace.py --combinators K,I,B,C,Y,S,W

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

os.environ.setdefault("PYTHONUNBUFFERED", "1")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import numpy as np
import torch
import torch.nn.functional as F

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


def run_experiment(
    model_id: str = "Qwen/Qwen3-8B",
    combinators: list[str] | None = None,
    n_probes_per_combinator: int = 5,
    top_k: int = 10,
):
    log("=" * 72)
    log("REDUCTION CHAIN TRACE")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Probes per combinator: {n_probes_per_combinator}")
    log()

    from transformers import AutoModelForCausalLM, AutoTokenizer
    from verbum.probes.library import by_combinator, combinator_counts

    if combinators is None:
        combinators = ["K", "I", "B", "C", "Y", "S", "W"]

    # ── Collect probes ──────────────────────────────────────────
    probes_by_type = {}
    for comb in combinators:
        all_probes = by_combinator(comb)
        # Skip probes that start with λ (pure lambda notation, not NL)
        nl_probes = [p for p in all_probes if not p.prompt.startswith("λ") and not p.prompt.startswith("(λ")]
        selected = nl_probes[:n_probes_per_combinator]
        probes_by_type[comb] = selected
        log(f"  {comb}: {len(selected)} probes (from {len(all_probes)} total)")
        for p in selected:
            log(f"    {p.prompt[:70]}")

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
    hidden_size = config.hidden_size
    log(f"  {n_layers} layers, hidden={hidden_size}")

    # ── Get unembedding ─────────────────────────────────────────
    if hasattr(model, 'lm_head'):
        W_unembed = model.lm_head.weight.data.cpu().float()
    else:
        W_unembed = model.model.embed_tokens.weight.data.cpu().float()
    log(f"  W_unembed: {W_unembed.shape}")

    # ── Compile gate ────────────────────────────────────────────
    compile_gate = "The dog runs. → λx. runs(dog)\nBe helpful but concise. → λ assist(x). helpful(x) | concise(x)\n\nInput: "

    # ── Hook every layer to capture residual AFTER each layer ───
    def trace_probe(prompt: str, comb_type: str) -> dict:
        full_text = compile_gate + prompt
        inputs = tokenizer(full_text, return_tensors="pt")
        input_ids = inputs["input_ids"].to(model.device)
        seq_len = input_ids.shape[1]

        gate_only = tokenizer(compile_gate, return_tensors="pt")
        gate_len = gate_only["input_ids"].shape[1]
        tokens = [tokenizer.decode(t) for t in input_ids[0]]
        probe_tokens = tokens[gate_len:]

        # Capture residual AFTER each decoder layer
        residuals = {}  # layer_idx → (seq_len, hidden)
        hooks = []

        for li in range(n_layers):
            layer = model.model.layers[li]
            def make_hook(layer_idx):
                def hook_fn(module, args, output):
                    # Decoder layer output is (hidden_states, ...) or just hidden_states
                    if isinstance(output, tuple):
                        h = output[0]
                    else:
                        h = output
                    residuals[layer_idx] = h[0].cpu().float()
                    return output
                return hook_fn
            h = layer.register_forward_hook(make_hook(li))
            hooks.append(h)

        # Also capture embedding output (layer -1)
        embed_storage = {}
        def embed_hook(module, args, output):
            embed_storage[-1] = output[0].cpu().float()
            return output
        h = model.model.embed_tokens.register_forward_hook(embed_hook)
        hooks.append(h)

        with torch.no_grad():
            outputs = model(input_ids, return_dict=True)

        for h in hooks:
            h.remove()

        # ── Analyze the reduction chain ─────────────────────────
        result = {
            "prompt": prompt,
            "combinator": comb_type,
            "tokens": probe_tokens,
            "gate_len": gate_len,
            "seq_len": seq_len,
            "chain": [],      # per-layer analysis
            "self_sim": [],    # self-similarity matrix
        }

        # For each layer, project cumulative residual through unembed
        # to see what the model "thinks" at each depth
        prev_residual = embed_storage.get(-1)

        for li in range(n_layers):
            if li not in residuals:
                continue

            curr_residual = residuals[li]

            # What does the cumulative residual say at this layer?
            # (project through final norm + unembed for accurate reading)
            # Approximate: just project through unembed directly
            layer_data = {
                "layer": li,
                "positions": [],
            }

            for pos in range(gate_len, seq_len):
                tok = tokens[pos]
                res_vec = curr_residual[pos]  # (hidden,)

                # Project through unembed
                logits = W_unembed @ res_vec  # (vocab,)
                top_vals, top_idx = logits.topk(top_k)
                top_tokens_list = [(tokenizer.decode(t.item()).strip(), v.item())
                                   for t, v in zip(top_idx, top_vals)]

                # What did THIS layer add? (delta)
                if prev_residual is not None:
                    delta = curr_residual[pos] - prev_residual[pos]
                    delta_logits = W_unembed @ delta
                    delta_top_vals, delta_top_idx = delta_logits.topk(top_k)
                    delta_tokens = [(tokenizer.decode(t.item()).strip(), v.item())
                                   for t, v in zip(delta_top_idx, delta_top_vals)]
                else:
                    delta_tokens = []

                layer_data["positions"].append({
                    "token": tok,
                    "cumulative_top5": top_tokens_list[:5],
                    "delta_top5": delta_tokens[:5],
                })

            result["chain"].append(layer_data)
            prev_residual = curr_residual

        # ── Self-similarity across depth (Y-combinator signature) ──
        # For each probe position, compute cos(residual[L], residual[L'])
        # across all layer pairs
        for pos in range(gate_len, min(gate_len + 5, seq_len)):  # first 5 positions
            tok = tokens[pos]
            sim_matrix = np.zeros((n_layers, n_layers))
            for li in range(n_layers):
                for lj in range(li, n_layers):
                    if li in residuals and lj in residuals:
                        cos = F.cosine_similarity(
                            residuals[li][pos].unsqueeze(0),
                            residuals[lj][pos].unsqueeze(0)
                        ).item()
                        sim_matrix[li, lj] = cos
                        sim_matrix[lj, li] = cos

            # Extract key features: diagonal bands (self-similarity at lag k)
            lag_sims = {}
            for lag in [1, 2, 3, 5, 8, 13]:  # Fibonacci lags
                sims = []
                for li in range(n_layers - lag):
                    sims.append(sim_matrix[li, li + lag])
                lag_sims[lag] = {
                    "mean": float(np.mean(sims)),
                    "std": float(np.std(sims)),
                    "min": float(np.min(sims)),
                    "max": float(np.max(sims)),
                    "min_layer": int(np.argmin(sims)),
                    "max_layer": int(np.argmax(sims)),
                }

            result["self_sim"].append({
                "token": tok,
                "position": pos,
                "lag_sims": lag_sims,
            })

        return result

    # ── Run all probes ──────────────────────────────────────────
    all_results = {}
    for comb, probes in probes_by_type.items():
        log(f"\n{'=' * 60}")
        log(f"COMBINATOR: {comb}")
        log("=" * 60)

        comb_results = []
        for probe in probes:
            log(f"\n  Tracing: {probe.prompt[:60]}...")
            result = trace_probe(probe.prompt, comb)
            comb_results.append(result)

            # Print chain summary for first probe
            log(f"    Tokens: {result['tokens']}")
            # Show every 6th layer for readability
            for chain_entry in result["chain"]:
                li = chain_entry["layer"]
                if li % 6 != 0 and li != n_layers - 1:
                    continue
                log(f"\n    L{li:2d}:")
                for pos_data in chain_entry["positions"]:
                    tok = pos_data["token"]
                    cum = [t for t, v in pos_data["cumulative_top5"][:3]]
                    delta = [t for t, v in pos_data["delta_top5"][:3]]
                    log(f"      [{tok:>12s}] cum=[{', '.join(cum):>30s}] "
                        f"Δ=[{', '.join(delta):>30s}]")

        all_results[comb] = comb_results

    # ── Analysis: Self-similarity profiles per combinator ───────
    log(f"\n{'=' * 72}")
    log("SELF-SIMILARITY PROFILES (Y-combinator signature)")
    log("=" * 72)
    log("Mean cos(residual[L], residual[L+lag]) across all positions")
    log("Y-combinator = recursion → expect periodic self-similarity")
    log()

    for comb, results in all_results.items():
        log(f"\n  [{comb}]:")
        for lag in [1, 3, 5, 8, 13]:
            means = []
            for result in results:
                for ss in result["self_sim"]:
                    if lag in ss["lag_sims"]:
                        means.append(ss["lag_sims"][lag]["mean"])
            if means:
                avg = np.mean(means)
                std = np.std(means)
                log(f"    lag={lag:2d}: cos={avg:.4f} ± {std:.4f}")

    # ── Analysis: When does composition first appear? ───────────
    log(f"\n{'=' * 72}")
    log("COMPOSITION DEPTH: When does meaning first compose?")
    log("=" * 72)
    log("Looking at cumulative residual → unembed for each combinator")
    log()

    for comb, results in all_results.items():
        log(f"\n  [{comb}]:")
        for result in results[:2]:  # First 2 probes per type
            log(f"    \"{result['prompt'][:60]}\"")
            tokens = result["tokens"]
            # Show key layers
            for chain_entry in result["chain"]:
                li = chain_entry["layer"]
                if li not in [0, 5, 10, 15, 20, 25, 30, 33, 35]:
                    continue
                # Show first 3 tokens
                parts = []
                for pos_data in chain_entry["positions"][:4]:
                    tok = pos_data["token"].strip()
                    cum_top = pos_data["cumulative_top5"][0][0] if pos_data["cumulative_top5"] else "?"
                    parts.append(f"{tok}→{cum_top}")
                log(f"      L{li:2d}: {' | '.join(parts)}")

    # ── Analysis: Per-layer delta profile per combinator ────────
    log(f"\n{'=' * 72}")
    log("PER-LAYER DELTA: What does each layer ADD?")
    log("=" * 72)

    for comb, results in all_results.items():
        log(f"\n  [{comb}]: (averaged across all probes, first position)")
        for li in range(0, n_layers, 3):
            delta_strengths = []
            delta_tokens_all = []
            for result in results:
                for chain_entry in result["chain"]:
                    if chain_entry["layer"] != li:
                        continue
                    if chain_entry["positions"]:
                        pos0 = chain_entry["positions"][0]
                        if pos0["delta_top5"]:
                            delta_strengths.append(pos0["delta_top5"][0][1])
                            delta_tokens_all.append(pos0["delta_top5"][0][0])
            if delta_strengths:
                from collections import Counter
                common = Counter(delta_tokens_all).most_common(3)
                common_str = ", ".join(f"{t}({n})" for t, n in common)
                avg_strength = np.mean(delta_strengths)
                log(f"    L{li:2d}: Δ_strength={avg_strength:.2f}  common=[{common_str}]")

    # ── Save results ────────────────────────────────────────────
    results_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "results", "reduction-chain-trace"
    )
    os.makedirs(results_dir, exist_ok=True)

    # Compact save (self-similarity matrices are large)
    compact = {}
    for comb, results in all_results.items():
        compact[comb] = []
        for result in results:
            c = {
                "prompt": result["prompt"],
                "tokens": result["tokens"],
                "self_sim": result["self_sim"],
                "chain_summary": [],
            }
            # Save every 3rd layer, top 3 per position
            for chain_entry in result["chain"]:
                li = chain_entry["layer"]
                if li % 3 != 0 and li != n_layers - 1:
                    continue
                c["chain_summary"].append({
                    "layer": li,
                    "positions": [
                        {
                            "token": p["token"],
                            "cum_top3": p["cumulative_top5"][:3],
                            "delta_top3": p["delta_top5"][:3],
                        }
                        for p in chain_entry["positions"]
                    ],
                })
            compact[comb].append(c)

    summary = {
        "model": model_id,
        "n_layers": n_layers,
        "combinators": combinators,
        "n_probes_per_combinator": n_probes_per_combinator,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": compact,
    }

    summary_path = os.path.join(results_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    log(f"\nResults saved to {results_dir}/")
    log(f"  summary.json: {os.path.getsize(summary_path) / 1024:.1f} KB")

    log(f"\n{'=' * 72}")
    log("EXPERIMENT COMPLETE")
    log("=" * 72)

    return all_results


def main():
    parser = argparse.ArgumentParser(description="Reduction Chain Trace")
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--combinators", default=None, help="Comma-separated combinator names")
    parser.add_argument("--n-probes", type=int, default=5)
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    combs = None
    if args.combinators:
        combs = [c.strip() for c in args.combinators.split(",")]

    run_experiment(
        model_id=args.model,
        combinators=combs,
        n_probes_per_combinator=args.n_probes,
        top_k=args.top_k,
    )


if __name__ == "__main__":
    main()
