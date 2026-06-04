#!/usr/bin/env python3
"""Reverse Binding Trace: Does the verb attend back to the subject?

THE GAP: Session 188's binding graph trace showed object→verb binding
is concentrated attention (0.78 weight via H03/H13/H15 at L30). But
subject→verb binding is blocked by the causal mask (subject precedes verb).

THIS EXPERIMENT: Measure attention in the REVERSE direction —
FROM the verb/function position TO the subject/argument positions.
This is causal-allowed (verb comes after subject). If the verb attends
back to the subject, this completes the β-reduction mechanism:

  Subject-verb: verb attends BACK to subject (func→arg)
  Object-verb:  object attends BACK to verb  (arg→func)

Both are backward attention (later position → earlier position).
Both are β-reduction. The causal mask just means the LATER token
always does the attending.

MEASUREMENTS:
  For each probe, at L27/L30/L33 × 32 heads:
  1. Attention FROM verb TO subject positions (func→arg weight)
  2. Head output at verb position through unembed (what does the verb
     "become" when it reads the subject?)
  3. V vectors at subject and verb through unembed

  Also measures the forward direction (arg→func) for comparison,
  and captures BOTH directions for every binding.

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
from dataclasses import dataclass

os.environ.setdefault("PYTHONUNBUFFERED", "1")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import numpy as np
import torch

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


# ══════════════════════════════════════════════════════════════════════════════
# PROBES — same structure as binding_graph_trace, with both directions
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class BindingProbe:
    id: str
    prompt: str
    # Each binding: (subject_substr, verb_substr, label)
    # We measure BOTH directions:
    #   subject→verb (forward, may be causal-blocked)
    #   verb→subject (reverse, causal-allowed when subject precedes verb)
    bindings: list[tuple[str, str, str]]
    category: str
    pair_id: str = ""


PROBES = [
    # ── Subject-verb (the key case) ─────────────────────────────
    BindingProbe("sv1", "The dog runs.",
                 [("dog", "runs", "runs(dog)")],
                 "subject-verb", "sv"),
    BindingProbe("sv2", "The cat runs.",
                 [("cat", "runs", "runs(cat)")],
                 "subject-verb", "sv"),

    # ── Transitive (subject AND object) ─────────────────────────
    BindingProbe("rev1", "The dog bit the cat.",
                 [("dog", "bit", "bit(dog,_)"),
                  ("cat", "bit", "bit(_,cat)")],
                 "transitive", "rev"),
    BindingProbe("rev2", "The cat bit the dog.",
                 [("cat", "bit", "bit(cat,_)"),
                  ("dog", "bit", "bit(_,dog)")],
                 "transitive", "rev"),

    # ── Ditransitive ────────────────────────────────────────────
    BindingProbe("ditrans", "Mary gave John the book.",
                 [("Mary", "gave", "gave(mary,_,_)"),
                  ("John", "gave", "gave(_,john,_)"),
                  ("book", "gave", "gave(_,_,book)")],
                 "ditransitive"),

    # ── Self-reference ──────────────────────────────────────────
    BindingProbe("self1", "The dog bit itself.",
                 [("dog", "bit", "bit(dog,_)"),
                  ("itself", "bit", "bit(_,itself)"),
                  ("itself", "dog", "itself→dog")],
                 "self-reference"),

    # ── Nested ──────────────────────────────────────────────────
    BindingProbe("nested1", "The cat that sat on the mat is black.",
                 [("cat", "sat", "sat(cat,_)"),
                  ("mat", "sat", "sat(_,mat)"),
                  ("cat", "black", "black(cat)")],
                 "nested"),

    # ── Active/Passive ──────────────────────────────────────────
    BindingProbe("act1", "The boy kicked the ball.",
                 [("boy", "kicked", "kicked(boy,_)"),
                  ("ball", "kicked", "kicked(_,ball)")],
                 "active", "voice"),
    BindingProbe("pass1", "The ball was kicked by the boy.",
                 [("boy", "kicked", "kicked(boy,_)"),
                  ("ball", "kicked", "kicked(_,ball)")],
                 "passive", "voice"),

    # ── Longer sentences ────────────────────────────────────────
    BindingProbe("long1", "The tall boy quickly kicked the red ball.",
                 [("boy", "kicked", "kicked(boy,_)"),
                  ("ball", "kicked", "kicked(_,ball)")],
                 "modified"),

    BindingProbe("coord1", "The dog ran and the cat jumped.",
                 [("dog", "ran", "ran(dog)"),
                  ("cat", "jumped", "jumped(cat)")],
                 "coordination"),
]


def find_token_positions(tokens: list[str], substring: str, gate_len: int) -> list[int]:
    positions = []
    sub_lower = substring.lower().strip()
    for i in range(gate_len, len(tokens)):
        tok = tokens[i].strip().lower()
        if tok and sub_lower in tok:
            positions.append(i)
    return positions


def run_experiment(
    model_id: str = "Qwen/Qwen3-8B",
    layer_indices: list[int] | None = None,
    top_k: int = 10,
):
    log("=" * 72)
    log("REVERSE BINDING TRACE")
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
    n_kv_heads = config.num_key_value_heads
    head_dim = config.hidden_size // n_q_heads
    hidden_size = config.hidden_size
    q_per_kv = n_q_heads // n_kv_heads
    log(f"  {n_layers} layers, {n_q_heads} Q heads, {n_kv_heads} KV groups")

    if layer_indices is None:
        layer_indices = [27, 30, 33]
    layer_indices = [l for l in layer_indices if l < n_layers]
    log(f"  Target layers: {layer_indices}")

    if hasattr(model, "lm_head"):
        W_unembed = model.lm_head.weight.data.cpu().float()
    else:
        W_unembed = model.model.embed_tokens.weight.data.cpu().float()

    W_o_heads: dict[int, list[torch.Tensor]] = {}
    for li in layer_indices:
        W_o = model.model.layers[li].self_attn.o_proj.weight.data.cpu().float()
        W_o_heads[li] = [
            W_o[:, h * head_dim : (h + 1) * head_dim]
            for h in range(n_q_heads)
        ]

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

    all_results = []

    for probe in PROBES:
        log(f"\n{'─' * 60}")
        log(f"[{probe.id}] {probe.prompt}")

        full_text = compile_gate + probe.prompt
        inputs = tokenizer(full_text, return_tensors="pt")
        input_ids = inputs["input_ids"].to(model.device)
        seq_len = input_ids.shape[1]
        tokens = [tokenizer.decode(t) for t in input_ids[0]]
        probe_tokens = tokens[gate_len:]
        log(f"  Tokens: {probe_tokens}")

        # Resolve bindings
        resolved = []
        for sub_sub, verb_sub, label in probe.bindings:
            sub_pos = find_token_positions(tokens, sub_sub, gate_len)
            verb_pos = find_token_positions(tokens, verb_sub, gate_len)
            if sub_pos and verb_pos:
                # Determine direction
                sub_first = sub_pos[0] < verb_pos[0]
                resolved.append({
                    "sub": sub_sub, "verb": verb_sub, "label": label,
                    "sub_positions": sub_pos, "verb_positions": verb_pos,
                    "sub_before_verb": sub_first,
                })
                direction = "sub<verb (verb→sub = REVERSE)" if sub_first else "sub>verb (sub→verb = FORWARD)"
                log(f"  ✓ {sub_sub}@{[p-gate_len for p in sub_pos]} ↔ "
                    f"{verb_sub}@{[p-gate_len for p in verb_pos]} [{direction}]")
            else:
                log(f"  ✗ {sub_sub} ↔ {verb_sub} UNRESOLVED")

        # Hooks
        captured: dict[int, dict] = {}
        hooks = []
        for li in layer_indices:
            attn_module = model.model.layers[li].self_attn

            def make_hook(layer_idx):
                def hook_fn(module, args, kwargs, output):
                    if args:
                        hidden_states = args[0]
                    else:
                        hidden_states = kwargs.get("hidden_states")
                    hidden_shape = (*hidden_states.shape[:-1], -1, head_dim)
                    with torch.no_grad():
                        v = module.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)
                        attn_weights = output[1]
                        if attn_weights is not None:
                            v_expanded = v.repeat_interleave(q_per_kv, dim=1)
                            per_head = torch.matmul(attn_weights, v_expanded)
                            captured[layer_idx] = {
                                "v": v[0].cpu().float(),
                                "attn": attn_weights[0].cpu().float(),
                                "head_out": per_head[0].cpu().float(),
                            }
                    return output
                return hook_fn

            h = attn_module.register_forward_hook(make_hook(li), with_kwargs=True)
            hooks.append(h)

        with torch.no_grad():
            model(input_ids, output_attentions=True, return_dict=True)
        for h in hooks:
            h.remove()

        # ── Analyze both directions ─────────────────────────────
        probe_result = {
            "id": probe.id, "prompt": probe.prompt,
            "category": probe.category, "pair_id": probe.pair_id,
            "tokens": probe_tokens, "gate_len": gate_len,
            "resolved": resolved, "layers": {},
        }

        for li in layer_indices:
            if li not in captured:
                continue
            attn = captured[li]["attn"]
            head_out = captured[li]["head_out"]

            layer_data = {"bindings": []}

            for binding in resolved:
                sub_positions = binding["sub_positions"]
                verb_positions = binding["verb_positions"]
                label = binding["label"]

                binding_result = {
                    "label": label,
                    "sub": binding["sub"],
                    "verb": binding["verb"],
                    "sub_before_verb": binding["sub_before_verb"],
                    "forward": [],   # sub→verb (arg→func)
                    "reverse": [],   # verb→sub (func→arg)
                }

                for h in range(n_q_heads):
                    # ── FORWARD: sub → verb ─────────────────────
                    fwd_weights = []
                    for sp in sub_positions:
                        for vp in verb_positions:
                            fwd_weights.append(attn[h, sp, vp].item())
                    fwd_mean = float(np.mean(fwd_weights)) if fwd_weights else 0

                    # Head output at sub position through unembed
                    fwd_output_tokens = []
                    for sp in sub_positions:
                        W_o_h = W_o_heads[li][h]
                        contrib = W_o_h @ head_out[h, sp]
                        logits = W_unembed @ contrib
                        top_vals, top_idx = logits.topk(5)
                        fwd_output_tokens.append([
                            (tokenizer.decode(t.item()).strip(), round(v.item(), 2))
                            for t, v in zip(top_idx, top_vals)
                        ])

                    # ── REVERSE: verb → sub ─────────────────────
                    rev_weights = []
                    for vp in verb_positions:
                        for sp in sub_positions:
                            rev_weights.append(attn[h, vp, sp].item())
                    rev_mean = float(np.mean(rev_weights)) if rev_weights else 0

                    # Head output at verb position through unembed
                    rev_output_tokens = []
                    for vp in verb_positions:
                        W_o_h = W_o_heads[li][h]
                        contrib = W_o_h @ head_out[h, vp]
                        logits = W_unembed @ contrib
                        top_vals, top_idx = logits.topk(5)
                        rev_output_tokens.append([
                            (tokenizer.decode(t.item()).strip(), round(v.item(), 2))
                            for t, v in zip(top_idx, top_vals)
                        ])

                    chance = 1.0 / seq_len

                    binding_result["forward"].append({
                        "head": h,
                        "weight": round(fwd_mean, 4),
                        "ratio": round(fwd_mean / chance, 1) if chance > 0 else 0,
                        "output_at_sub": fwd_output_tokens,
                    })
                    binding_result["reverse"].append({
                        "head": h,
                        "weight": round(rev_mean, 4),
                        "ratio": round(rev_mean / chance, 1) if chance > 0 else 0,
                        "output_at_verb": rev_output_tokens,
                    })

                # Sort both by weight
                binding_result["forward"].sort(key=lambda x: x["weight"], reverse=True)
                binding_result["reverse"].sort(key=lambda x: x["weight"], reverse=True)

                layer_data["bindings"].append(binding_result)

            # ── Also capture full attention row at verb for top bindings ──
            layer_data["verb_attention_rows"] = []
            for binding in resolved:
                if not binding["verb_positions"]:
                    continue
                vp = binding["verb_positions"][0]
                # Find the reverse binding's top head
                for bd in layer_data["bindings"]:
                    if bd["label"] != binding["label"]:
                        continue
                    for head_info in bd["reverse"][:3]:
                        h = head_info["head"]
                        attn_row = attn[h, vp]
                        probe_attn = []
                        for p in range(gate_len, seq_len):
                            probe_attn.append({
                                "pos": p - gate_len,
                                "token": tokens[p].strip(),
                                "weight": round(attn_row[p].item(), 4),
                                "is_sub": p in binding["sub_positions"],
                            })
                        probe_attn.sort(key=lambda x: x["weight"], reverse=True)
                        layer_data["verb_attention_rows"].append({
                            "label": binding["label"],
                            "verb_token": tokens[vp].strip(),
                            "head": h,
                            "rev_weight": head_info["weight"],
                            "attention_over_probe": probe_attn,
                        })

            probe_result["layers"][li] = layer_data

        all_results.append(probe_result)
        del captured

    # ══════════════════════════════════════════════════════════════
    # ANALYSIS
    # ══════════════════════════════════════════════════════════════

    log(f"\n{'=' * 72}")
    log("ANALYSIS: FORWARD vs REVERSE BINDING")
    log("=" * 72)

    for li in layer_indices:
        log(f"\n{'━' * 60}")
        log(f"LAYER {li}")
        log("━" * 60)

        for result in all_results:
            if li not in result["layers"]:
                continue
            layer = result["layers"][li]

            log(f"\n  [{result['id']}] \"{result['prompt']}\"")

            for bd in layer["bindings"]:
                sub_first = bd["sub_before_verb"]
                direction_note = "(sub BEFORE verb)" if sub_first else "(sub AFTER verb)"

                log(f"\n    BINDING: {bd['label']} {direction_note}")
                log(f"      {'':>8s} {'── FORWARD (sub→verb) ──':>30s}   {'── REVERSE (verb→sub) ──':>30s}")
                log(f"      {'Head':>8s} {'Weight':>8s} {'Ratio':>6s}   {'Weight':>8s} {'Ratio':>6s}   Output@verb (what verb becomes)")

                # Interleave forward and reverse for top heads
                # Use reverse ranking (the new measurement)
                for rev_info in bd["reverse"][:8]:
                    h = rev_info["head"]
                    # Find matching forward entry
                    fwd_info = next((f for f in bd["forward"] if f["head"] == h), None)
                    fwd_w = fwd_info["weight"] if fwd_info else 0
                    fwd_r = fwd_info["ratio"] if fwd_info else 0
                    rev_w = rev_info["weight"]
                    rev_r = rev_info["ratio"]

                    # Head output at verb
                    if rev_info["output_at_verb"]:
                        out_str = ", ".join(f"{t}" for t, v in rev_info["output_at_verb"][0][:3])
                    else:
                        out_str = "—"

                    fwd_marker = " ◆" if fwd_r > 5 else " •" if fwd_r > 2 else ""
                    rev_marker = " ◆" if rev_r > 5 else " •" if rev_r > 2 else ""

                    log(f"      H{h:02d}   {fwd_w:8.4f} {fwd_r:5.1f}x{fwd_marker}  "
                        f"{rev_w:8.4f} {rev_r:5.1f}x{rev_marker}  [{out_str}]")

            # Show verb attention rows
            for var in layer.get("verb_attention_rows", [])[:6]:
                log(f"\n    VERB ATTENTION: H{var['head']:02d} at [{var['verb_token']}] "
                    f"for {var['label']}:")
                for item in var["attention_over_probe"][:6]:
                    marker = " ★ SUB" if item["is_sub"] else ""
                    log(f"      {item['token']:>12s} ({item['pos']:2d}): "
                        f"{item['weight']:.4f}{marker}")

    # ── Summary: forward vs reverse binding strength ────────────
    log(f"\n{'=' * 72}")
    log("SUMMARY: FORWARD vs REVERSE BINDING BY POSITION ORDER")
    log("=" * 72)

    for li in layer_indices:
        log(f"\n  L{li}:")
        fwd_sub_before = []  # forward binding when sub comes first (causal-blocked)
        rev_sub_before = []  # reverse binding when sub comes first (the mechanism)
        fwd_sub_after = []   # forward binding when sub comes after (already confirmed)
        rev_sub_after = []   # reverse binding when sub comes after

        for result in all_results:
            if li not in result["layers"]:
                continue
            for bd in result["layers"][li]["bindings"]:
                fwd_max = bd["forward"][0]["weight"] if bd["forward"] else 0
                rev_max = bd["reverse"][0]["weight"] if bd["reverse"] else 0
                fwd_top_h = bd["forward"][0]["head"] if bd["forward"] else -1
                rev_top_h = bd["reverse"][0]["head"] if bd["reverse"] else -1

                if bd["sub_before_verb"]:
                    fwd_sub_before.append((bd["label"], fwd_max, fwd_top_h, result["prompt"]))
                    rev_sub_before.append((bd["label"], rev_max, rev_top_h, result["prompt"]))
                else:
                    fwd_sub_after.append((bd["label"], fwd_max, fwd_top_h, result["prompt"]))
                    rev_sub_after.append((bd["label"], rev_max, rev_top_h, result["prompt"]))

        log(f"\n    SUBJECT BEFORE VERB (sub→verb blocked by causal mask):")
        log(f"      Forward (sub→verb): {len([x for x in fwd_sub_before if x[1]>0.05])}/{len(fwd_sub_before)} with weight>0.05")
        log(f"      Reverse (verb→sub): {len([x for x in rev_sub_before if x[1]>0.05])}/{len(rev_sub_before)} with weight>0.05")
        if rev_sub_before:
            log(f"      Top reverse bindings:")
            for label, w, h, prompt in sorted(rev_sub_before, key=lambda x: x[1], reverse=True)[:10]:
                marker = "◆" if w > 0.2 else "•" if w > 0.1 else ""
                log(f"        {label:>25s}: H{h:02d} w={w:.4f} {marker} ({prompt})")

        if fwd_sub_after:
            log(f"\n    SUBJECT AFTER VERB (sub→verb already confirmed):")
            log(f"      Forward (sub→verb): {len([x for x in fwd_sub_after if x[1]>0.05])}/{len(fwd_sub_after)} with weight>0.05")
            log(f"      Reverse (verb→sub): {len([x for x in rev_sub_after if x[1]>0.05])}/{len(rev_sub_after)} with weight>0.05")

    # ── Head consistency for reverse binding ────────────────────
    log(f"\n{'=' * 72}")
    log("REVERSE BINDING HEADS (verb→subject, across all probes)")
    log("=" * 72)

    for li in layer_indices:
        head_scores: dict[int, list[float]] = defaultdict(list)
        for result in all_results:
            if li not in result["layers"]:
                continue
            for bd in result["layers"][li]["bindings"]:
                if not bd["sub_before_verb"]:
                    continue  # only count sub-before-verb (the forward-blocked cases)
                for rev in bd["reverse"]:
                    head_scores[rev["head"]].append(rev["weight"])

        log(f"\n  L{li} (only subject-before-verb bindings):")
        head_stats = [(h, float(np.mean(ws)), float(np.max(ws)), len(ws))
                      for h, ws in head_scores.items()]
        head_stats.sort(key=lambda x: x[1], reverse=True)
        log(f"    {'Head':>6s} {'MeanWt':>8s} {'MaxWt':>8s} {'N':>4s}")
        for h, mean_w, max_w, n in head_stats[:15]:
            marker = " ◆" if mean_w > 0.1 else " •" if mean_w > 0.05 else ""
            log(f"    H{h:02d}   {mean_w:8.4f} {max_w:8.4f} {n:4d}{marker}")

    # ══════════════════════════════════════════════════════════════
    # SAVE
    # ══════════════════════════════════════════════════════════════

    results_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "results", "reverse-binding-trace"
    )
    os.makedirs(results_dir, exist_ok=True)

    compact = []
    for result in all_results:
        c = {
            "id": result["id"], "prompt": result["prompt"],
            "category": result["category"], "pair_id": result["pair_id"],
            "tokens": result["tokens"],
            "resolved": result["resolved"],
            "layers": {},
        }
        for li, ld in result["layers"].items():
            c["layers"][str(li)] = {
                "bindings": [
                    {
                        "label": bd["label"],
                        "sub": bd["sub"], "verb": bd["verb"],
                        "sub_before_verb": bd["sub_before_verb"],
                        "forward_top10": [
                            {"head": f["head"], "weight": f["weight"],
                             "ratio": f["ratio"], "output_at_sub": f["output_at_sub"]}
                            for f in bd["forward"][:10]
                        ],
                        "reverse_top10": [
                            {"head": r["head"], "weight": r["weight"],
                             "ratio": r["ratio"], "output_at_verb": r["output_at_verb"]}
                            for r in bd["reverse"][:10]
                        ],
                    }
                    for bd in ld["bindings"]
                ],
                "verb_attention_rows": ld.get("verb_attention_rows", [])[:12],
            }
        compact.append(c)

    summary = {
        "model": model_id,
        "layers": layer_indices,
        "n_probes": len(PROBES),
        "n_q_heads": n_q_heads,
        "gate_len": gate_len,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": compact,
    }

    summary_path = os.path.join(results_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    log(f"\n{'=' * 72}")
    log(f"RESULTS SAVED to {results_dir}/")
    log(f"  summary.json: {os.path.getsize(summary_path) / 1024:.1f} KB")
    log("=" * 72)


def main():
    parser = argparse.ArgumentParser(description="Reverse Binding Trace")
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", default=None)
    args = parser.parse_args()

    layer_indices = None
    if args.layers:
        layer_indices = [int(l) for l in args.layers.split(",")]

    run_experiment(model_id=args.model, layer_indices=layer_indices)


if __name__ == "__main__":
    main()
