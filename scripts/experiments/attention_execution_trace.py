#!/usr/bin/env python3
"""Attention Execution Trace: What does each attention head compute?

HYPOTHESIS: The FFN compiles context-dependent V vectors (the program).
Attention executes the program via softmax over V — the weighted
combination IS β-reduction. This experiment reads the execution:

  Per-head output = softmax(QK^T) @ V → project through unembed
  → "what did this head decide to produce?"

If the model is doing β-reduction:
  1. Some heads should produce COMPOSITIONAL outputs — combining meanings
     from multiple positions into something neither position had alone
  2. The attention weights show the BINDING DECISION — which positions
     are being combined (function applied to argument)
  3. Compile vs null should show different ROUTING — same V values,
     different attention patterns → different execution

ARCHITECTURE (Qwen3-8B):
  GQA: 32 Q heads, 8 KV groups (4 Q heads share each KV pair)
  head_dim=128, hidden=4096, 36 layers
  
  Attention flow:
    Q = q_norm(q_proj(x))   shape: (batch, 32, seq, 128)
    K = k_norm(k_proj(x))   shape: (batch, 8, seq, 128)  — shared across 4 Q heads
    V = v_proj(x)            shape: (batch, 8, seq, 128)  — shared across 4 Q heads
    attn_weights = softmax(Q @ K^T / sqrt(128))  shape: (batch, 32, seq, seq)
    per_head_output = attn_weights @ V_expanded   shape: (batch, 32, seq, 128)
    combined = reshape → o_proj → residual

  For GQA: Q heads 0-3 share KV group 0, Q heads 4-7 share KV group 1, etc.

MEASUREMENTS:
  1. Per-head output → unembed: what each head "computes" in token space
  2. Attention weights: which positions does each head bind?
  3. Compositionality test: is head output > max(individual V values)?
     i.e., does the combination produce something new?
  4. Head specialization: do different heads at the same layer do
     different types of composition?

Usage:
  uv run python scripts/experiments/attention_execution_trace.py
  uv run python scripts/experiments/attention_execution_trace.py --layers 1,24,26,30,33,35

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from collections import defaultdict

os.environ.setdefault("PYTHONUNBUFFERED", "1")

import numpy as np
import torch
import torch.nn.functional as F

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


def run_experiment(
    model_id: str = "Qwen/Qwen3-8B",
    layer_indices: list[int] | None = None,
    top_k: int = 10,
):
    log("=" * 72)
    log("ATTENTION EXECUTION TRACE")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Top-K tokens: {top_k}")
    log()

    from transformers import AutoModelForCausalLM, AutoTokenizer

    # ── Load model ──────────────────────────────────────────────
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
    n_kv_heads = config.num_key_value_heads
    head_dim = config.hidden_size // n_q_heads
    hidden_size = config.hidden_size
    q_per_kv = n_q_heads // n_kv_heads
    log(f"  {n_layers} layers, {n_q_heads} Q heads, {n_kv_heads} KV groups")
    log(f"  GQA ratio: {q_per_kv} Q heads per KV group, head_dim={head_dim}")

    if layer_indices is None:
        # 3-head circuit layers + semantic + collapse
        layer_indices = [0, 1, 3, 10, 18, 22, 24, 26, 28, 30, 33, 35]
        layer_indices = [l for l in layer_indices if l < n_layers]
    log(f"  Tracing layers: {layer_indices}")

    # ── Get unembedding and O projection matrices ───────────────
    if hasattr(model, 'lm_head'):
        W_unembed = model.lm_head.weight.data.cpu().float()  # (vocab, hidden)
    else:
        W_unembed = model.model.embed_tokens.weight.data.cpu().float()
    log(f"  W_unembed: {W_unembed.shape}")

    # ── Define probes ───────────────────────────────────────────
    compile_gate = "The dog runs. → λx. runs(dog)\nBe helpful but concise. → λ assist(x). helpful(x) | concise(x)\n\nInput: "
    null_gate = "You are a helpful assistant. Respond naturally and concisely.\n\nInput: "

    probes = [
        "The dog runs.",
        "Every student reads a book.",
        "The cat that sat on the mat is black.",
        "If it rains, the ground is wet.",
        "Someone believes that the earth is flat.",
    ]

    # ── Hook setup ──────────────────────────────────────────────
    # For each target layer, we need:
    #   1. V vectors (pre-attention, post v_proj)
    #   2. Attention weights (softmax(QK^T))
    #   3. Per-head output (attn_weights @ V, before o_proj)
    #
    # With eager attention and output_attentions=True, we get attn_weights.
    # But we also need V and the per-head output BEFORE o_proj.
    # Strategy: hook the attention module to capture V and compute per-head outputs.

    def trace_one(prompt: str, gate_name: str, gate_text: str) -> dict:
        full_text = gate_text + prompt
        inputs = tokenizer(full_text, return_tensors="pt")
        input_ids = inputs["input_ids"].to(model.device)
        seq_len = input_ids.shape[1]

        gate_only = tokenizer(gate_text, return_tensors="pt")
        gate_len = gate_only["input_ids"].shape[1]
        tokens = [tokenizer.decode(t) for t in input_ids[0]]
        probe_tokens = tokens[gate_len:]

        log(f"\n  [{gate_name}] \"{prompt}\"")
        log(f"    Tokens ({len(probe_tokens)}): {probe_tokens}")

        # Storage for hook captures
        captured_v = {}        # layer_idx → (batch, n_kv_heads, seq, head_dim)
        captured_attn = {}     # layer_idx → (batch, n_q_heads, seq, seq)
        captured_head_out = {} # layer_idx → (batch, n_q_heads, seq, head_dim)

        hooks = []

        for li in layer_indices:
            attn_module = model.model.layers[li].self_attn

            def make_hook(layer_idx):
                def hook_fn(module, args, kwargs, output):
                    # output = (attn_output, attn_weights)
                    # We need to also capture V and per-head output
                    # hidden_states may be positional or keyword depending on caller
                    if args:
                        hidden_states = args[0]
                    else:
                        hidden_states = kwargs.get("hidden_states")
                    input_shape = hidden_states.shape[:-1]
                    hidden_shape = (*input_shape, -1, head_dim)

                    with torch.no_grad():
                        # V computation (matching the forward pass)
                        v = module.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)
                        # v shape: (batch, n_kv_heads, seq, head_dim)
                        captured_v[layer_idx] = v[0].cpu().float()

                        # Attention weights from output
                        attn_weights = output[1]  # (batch, n_q_heads, seq, seq)
                        if attn_weights is not None:
                            captured_attn[layer_idx] = attn_weights[0].cpu().float()

                            # Compute per-Q-head output: attn_weights @ V_expanded
                            # For GQA, expand V to match Q heads
                            v_expanded = v.repeat_interleave(q_per_kv, dim=1)
                            # v_expanded: (batch, n_q_heads, seq, head_dim)
                            # attn_weights: (batch, n_q_heads, seq, seq)
                            per_head = torch.matmul(attn_weights, v_expanded)
                            # per_head: (batch, n_q_heads, seq, head_dim)
                            captured_head_out[layer_idx] = per_head[0].cpu().float()

                    return output
                return hook_fn

            h = attn_module.register_forward_hook(make_hook(li), with_kwargs=True)
            hooks.append(h)

        # Forward pass
        with torch.no_grad():
            outputs = model(input_ids, output_attentions=True, return_dict=True)

        for h in hooks:
            h.remove()

        # ── Analyze per-head outputs ────────────────────────────
        result = {
            "prompt": prompt,
            "gate": gate_name,
            "tokens": tokens,
            "probe_tokens": probe_tokens,
            "gate_len": gate_len,
            "seq_len": seq_len,
            "layers": {},
        }

        # Get O projection matrices for converting per-head output to residual space
        # o_proj: (hidden, hidden) — maps concatenated heads back to residual
        # For head h, its slice is o_proj[:, h*head_dim:(h+1)*head_dim]

        for li in layer_indices:
            if li not in captured_head_out:
                log(f"    L{li}: no data captured")
                continue

            W_o = model.model.layers[li].self_attn.o_proj.weight.data.cpu().float()
            # W_o shape: (hidden, hidden)
            # For head h: contribution = W_o[:, h*head_dim:(h+1)*head_dim] @ head_output[h]

            head_outputs = captured_head_out[li]  # (n_q_heads, seq, head_dim)
            attn_weights = captured_attn.get(li)   # (n_q_heads, seq, seq)
            v_vectors = captured_v.get(li)          # (n_kv_heads, seq, head_dim)

            layer_result = {
                "layer": li,
                "heads": [],
            }

            for h in range(n_q_heads):
                head_out = head_outputs[h]  # (seq, head_dim)

                # Project this head's output through o_proj slice, then through unembed
                W_o_head = W_o[:, h * head_dim:(h + 1) * head_dim]  # (hidden, head_dim)
                # head contribution to residual: W_o_head @ head_out.T → (hidden, seq)
                head_residual = (W_o_head @ head_out.T).T  # (seq, hidden)

                # Project through unembed
                head_logits = head_residual @ W_unembed.T  # (seq, vocab)

                head_result = {
                    "head": h,
                    "kv_group": h // q_per_kv,
                    "positions": [],
                }

                for pos in range(gate_len, seq_len):
                    rel_pos = pos - gate_len
                    tok = tokens[pos]

                    # What does this head produce at this position?
                    pos_logits = head_logits[pos]
                    top_vals, top_idx = pos_logits.topk(top_k)
                    top_tokens = [(tokenizer.decode(t.item()).strip(), v.item())
                                  for t, v in zip(top_idx, top_vals)]

                    # Where did this head attend FROM this position?
                    if attn_weights is not None:
                        attn_row = attn_weights[h, pos]  # (seq,)
                        # Top attended positions (within probe tokens)
                        attn_probe = attn_row[gate_len:]
                        top_attn_vals, top_attn_idx = attn_probe.topk(
                            min(5, len(attn_probe)))
                        attended = [
                            (tokens[gate_len + i.item()].strip(),
                             gate_len + i.item(),
                             v.item())
                            for i, v in zip(top_attn_idx, top_attn_vals)
                        ]
                        # Also: how much attention goes to gate prefix vs probe?
                        gate_attn = attn_row[:gate_len].sum().item()
                        probe_attn = attn_row[gate_len:].sum().item()
                    else:
                        attended = []
                        gate_attn = 0
                        probe_attn = 0

                    # Compositionality test: compare head output to individual V values
                    # The head output at this position = weighted sum of V at all positions
                    # If it's compositional, the head output should differ from any single V
                    kv_group = h // q_per_kv
                    if v_vectors is not None:
                        v_at_pos = v_vectors[kv_group, pos]  # (head_dim,)
                        head_at_pos = head_out[pos]  # (head_dim,)
                        # Cosine between head output and the V at the attended position
                        cos_self = F.cosine_similarity(
                            head_at_pos.unsqueeze(0),
                            v_at_pos.unsqueeze(0)
                        ).item()

                        # Cosine with top-attended position's V
                        if attended:
                            top_attended_pos = attended[0][1]
                            v_top = v_vectors[kv_group, top_attended_pos]
                            cos_top = F.cosine_similarity(
                                head_at_pos.unsqueeze(0),
                                v_top.unsqueeze(0)
                            ).item()
                        else:
                            cos_top = 0.0

                        # Entropy of attention distribution (how spread out)
                        if attn_weights is not None:
                            attn_dist = attn_row[attn_row > 0]
                            entropy = -(attn_dist * attn_dist.log()).sum().item()
                        else:
                            entropy = 0.0
                    else:
                        cos_self = 0.0
                        cos_top = 0.0
                        entropy = 0.0

                    head_result["positions"].append({
                        "position": pos,
                        "token": tok,
                        "output_promotes": top_tokens[:5],
                        "attended_to": attended[:3],
                        "gate_attn_frac": gate_attn,
                        "probe_attn_frac": probe_attn,
                        "cos_self_v": cos_self,
                        "cos_top_v": cos_top,
                        "attn_entropy": entropy,
                    })

                layer_result["heads"].append(head_result)

            result["layers"][li] = layer_result

        return result

    # ── Run probes ──────────────────────────────────────────────
    all_results = []
    for probe in probes:
        log(f"\n{'─' * 60}")
        log(f"PROBE: {probe}")

        compile_result = trace_one(probe, "compile", compile_gate)
        all_results.append(compile_result)

        null_result = trace_one(probe, "null", null_gate)
        all_results.append(null_result)

    # ── Analysis 1: Per-head output at semantic layers ──────────
    log(f"\n{'=' * 72}")
    log("WHAT DOES EACH HEAD COMPUTE? (per-head output → unembed)")
    log("=" * 72)
    log("Showing heads with strongest/most-interpretable outputs")

    for result in all_results:
        if result["gate"] != "compile":
            continue
        log(f"\n  \"{result['prompt']}\"")
        probe_tokens = result["probe_tokens"]

        for li in [26, 30, 33, 35]:
            if li not in result["layers"]:
                continue
            layer = result["layers"][li]
            log(f"\n    L{li}:")

            # For each probe position, find the head that produces the
            # strongest signal (highest max logit)
            for pos_offset, tok in enumerate(probe_tokens):
                pos = result["gate_len"] + pos_offset

                # Collect all heads' outputs at this position
                head_outputs = []
                for head_data in layer["heads"]:
                    for pd in head_data["positions"]:
                        if pd["position"] == pos:
                            max_logit = pd["output_promotes"][0][1] if pd["output_promotes"] else 0
                            head_outputs.append((
                                head_data["head"],
                                max_logit,
                                pd["output_promotes"][:3],
                                pd["attended_to"][:2],
                                pd["cos_self_v"],
                                pd["cos_top_v"],
                                pd["attn_entropy"],
                            ))

                # Sort by absolute max logit and show top 3 heads
                head_outputs.sort(key=lambda x: abs(x[1]), reverse=True)
                top3 = head_outputs[:3]

                log(f"      [{tok:>10s}]")
                for h, logit, promotes, attended, cos_s, cos_t, ent in top3:
                    promo_str = ", ".join(f"{t}" for t, v in promotes)
                    attn_str = ", ".join(f"{t}({w:.2f})" for t, _, w in attended)
                    log(f"        H{h:02d}: [{promo_str:>30s}] "
                        f"attends=[{attn_str:>25s}] "
                        f"cos_self={cos_s:.2f} cos_top={cos_t:.2f} ent={ent:.2f}")

    # ── Analysis 2: Compositionality — heads that COMBINE ──────
    log(f"\n{'=' * 72}")
    log("COMPOSITIONALITY: Heads that combine multiple positions' values")
    log("=" * 72)
    log("A head is compositional if:")
    log("  - It attends to multiple positions (high entropy)")
    log("  - Its output differs from any single V (low cos_top_v)")
    log("  - Its output is interpretable (high max logit)")

    for result in all_results:
        if result["gate"] != "compile":
            continue
        log(f"\n  \"{result['prompt']}\"")

        for li in [26, 30, 33]:
            if li not in result["layers"]:
                continue
            layer = result["layers"][li]

            # Find compositional heads: high entropy + low cos_top + high logit
            compositional = []
            for head_data in layer["heads"]:
                for pd in head_data["positions"]:
                    if pd["position"] < result["gate_len"]:
                        continue
                    entropy = pd["attn_entropy"]
                    cos_top = pd["cos_top_v"]
                    max_logit = abs(pd["output_promotes"][0][1]) if pd["output_promotes"] else 0
                    # Compositional = spread attention + output differs from input
                    score = entropy * (1 - cos_top) * max_logit
                    if score > 0.1:
                        compositional.append((
                            head_data["head"],
                            pd["token"],
                            pd["position"],
                            score,
                            entropy,
                            cos_top,
                            pd["output_promotes"][:3],
                            pd["attended_to"][:3],
                        ))

            compositional.sort(key=lambda x: x[3], reverse=True)
            if compositional:
                log(f"\n    L{li}: top compositional head-positions:")
                for h, tok, pos, score, ent, cos_t, promotes, attended in compositional[:8]:
                    promo_str = ", ".join(f"{t}" for t, v in promotes)
                    attn_str = ", ".join(f"{t}({w:.2f})" for t, _, w in attended)
                    log(f"      H{h:02d} [{tok:>10s}] score={score:.2f} "
                        f"ent={ent:.2f} cos_top={cos_t:.2f} "
                        f"→ [{promo_str:>25s}] attends=[{attn_str}]")

    # ── Analysis 3: Compile vs Null — routing differences ──────
    log(f"\n{'=' * 72}")
    log("COMPILE vs NULL: Where does attention route differently?")
    log("=" * 72)

    for probe in probes:
        compile_r = next((r for r in all_results
                         if r["gate"] == "compile" and r["prompt"] == probe), None)
        null_r = next((r for r in all_results
                      if r["gate"] == "null" and r["prompt"] == probe), None)
        if not compile_r or not null_r:
            continue

        log(f"\n  \"{probe}\"")

        for li in [24, 30, 33]:
            if li not in compile_r["layers"] or li not in null_r["layers"]:
                continue

            c_layer = compile_r["layers"][li]
            n_layer = null_r["layers"][li]

            # For each head and position, compare what the head outputs
            diffs = []
            for c_head, n_head in zip(c_layer["heads"], n_layer["heads"]):
                h = c_head["head"]
                # Match positions by token (they have different absolute positions)
                for c_pd in c_head["positions"]:
                    c_tok = c_pd["token"].strip()
                    for n_pd in n_head["positions"]:
                        n_tok = n_pd["token"].strip()
                        if c_tok == n_tok:
                            # Compare outputs
                            c_top = c_pd["output_promotes"][0] if c_pd["output_promotes"] else ("", 0)
                            n_top = n_pd["output_promotes"][0] if n_pd["output_promotes"] else ("", 0)
                            if c_top[0] != n_top[0]:
                                diffs.append((
                                    h, c_tok,
                                    c_top[0], c_top[1],
                                    n_top[0], n_top[1],
                                    abs(c_top[1] - n_top[1]),
                                ))
                            break

            diffs.sort(key=lambda x: x[6], reverse=True)
            if diffs:
                log(f"    L{li}: top routing differences:")
                for h, tok, c_out, c_val, n_out, n_val, delta in diffs[:5]:
                    log(f"      H{h:02d} [{tok:>10s}] compile→{c_out:>12s}({c_val:.1f}) "
                        f"null→{n_out:>12s}({n_val:.1f}) Δ={delta:.1f}")

    # ── Analysis 4: Head specialization at L30 ──────────────────
    log(f"\n{'=' * 72}")
    log("HEAD SPECIALIZATION AT L30: What does each head do?")
    log("=" * 72)

    # Aggregate across all compile probes
    head_profiles = defaultdict(lambda: defaultdict(list))
    for result in all_results:
        if result["gate"] != "compile" or 30 not in result["layers"]:
            continue
        layer = result["layers"][30]
        for head_data in layer["heads"]:
            h = head_data["head"]
            for pd in head_data["positions"]:
                if pd["position"] < result["gate_len"]:
                    continue
                if pd["output_promotes"]:
                    head_profiles[h]["max_logit"].append(abs(pd["output_promotes"][0][1]))
                    head_profiles[h]["top_tokens"].append(pd["output_promotes"][0][0])
                head_profiles[h]["entropy"].append(pd["attn_entropy"])
                head_profiles[h]["cos_self"].append(pd["cos_self_v"])
                head_profiles[h]["cos_top"].append(pd["cos_top_v"])
                head_profiles[h]["gate_frac"].append(pd["gate_attn_frac"])

    log(f"\n  Head profiles (averaged across all compile probes at L30):")
    log(f"  {'Head':>6s} {'MaxLogit':>10s} {'Entropy':>10s} {'CosSelf':>10s} "
        f"{'CosTop':>10s} {'GateFrac':>10s} {'TopTokens'}")

    head_summaries = []
    for h in range(n_q_heads):
        if h not in head_profiles:
            continue
        p = head_profiles[h]
        avg_logit = np.mean(p["max_logit"])
        avg_ent = np.mean(p["entropy"])
        avg_cos_s = np.mean(p["cos_self"])
        avg_cos_t = np.mean(p["cos_top"])
        avg_gate = np.mean(p["gate_frac"])
        # Most common top tokens
        from collections import Counter
        token_counts = Counter(p["top_tokens"])
        common = token_counts.most_common(3)
        common_str = ", ".join(f"{t}({n})" for t, n in common)

        head_summaries.append((h, avg_logit, avg_ent, avg_cos_s, avg_cos_t, avg_gate, common_str))

    # Sort by max logit (strongest signal)
    head_summaries.sort(key=lambda x: x[1], reverse=True)
    for h, logit, ent, cos_s, cos_t, gate, common in head_summaries:
        log(f"  H{h:02d}    {logit:10.2f} {ent:10.2f} {cos_s:10.3f} "
            f"{cos_t:10.3f} {gate:10.3f}   {common}")

    # ── Save results ────────────────────────────────────────────
    results_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "results", "attention-execution-trace"
    )
    os.makedirs(results_dir, exist_ok=True)

    # Save compact results (full attention matrices are too large)
    compact = []
    for result in all_results:
        c = {
            "prompt": result["prompt"],
            "gate": result["gate"],
            "probe_tokens": result["probe_tokens"],
            "layers": {},
        }
        for li, layer_data in result["layers"].items():
            heads_compact = []
            for head_data in layer_data["heads"]:
                h_c = {
                    "head": head_data["head"],
                    "kv_group": head_data["kv_group"],
                    "positions": [
                        {
                            "token": pd["token"],
                            "output_top3": pd["output_promotes"][:3],
                            "attended_top2": [(t, w) for t, _, w in pd["attended_to"][:2]],
                            "cos_self_v": round(pd["cos_self_v"], 3),
                            "cos_top_v": round(pd["cos_top_v"], 3),
                            "attn_entropy": round(pd["attn_entropy"], 3),
                            "gate_attn_frac": round(pd["gate_attn_frac"], 3),
                        }
                        for pd in head_data["positions"]
                    ],
                }
                heads_compact.append(h_c)
            c["layers"][str(li)] = {"heads": heads_compact}
        compact.append(c)

    summary = {
        "model": model_id,
        "layers_traced": layer_indices,
        "n_probes": len(probes),
        "probes": probes,
        "n_q_heads": n_q_heads,
        "n_kv_heads": n_kv_heads,
        "q_per_kv": q_per_kv,
        "head_dim": head_dim,
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
    parser = argparse.ArgumentParser(description="Attention Execution Trace")
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", default=None, help="Comma-separated layer indices")
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    layer_indices = None
    if args.layers:
        layer_indices = [int(l) for l in args.layers.split(",")]

    run_experiment(
        model_id=args.model,
        layer_indices=layer_indices,
        top_k=args.top_k,
    )


if __name__ == "__main__":
    main()
