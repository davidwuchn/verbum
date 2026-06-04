#!/usr/bin/env python3
"""Binding Graph Trace: Does the attention pattern = the β-reduction binding graph?

THE QUESTION: When FFN compiles V vectors (the program), how does attention
route them to execute β-reduction? Is the softmax(QK^T) pattern literally
the binding graph of the λ-expression?

If yes: position A attends to position B means "apply function at B to
argument at A". The attention matrix IS the reduction trace.

METHODOLOGY:
  10-15 carefully constructed probes with ANNOTATED expected bindings:
    "The dog runs" → runs(dog) → binding: arg="dog" attends_to func="runs"

  For each probe, at L27/L30/L33 × 32 heads:
    1. V through unembed: what FFN compiled at each position
    2. Full attention row: which positions does each head route FROM here?
    3. Head output through unembed: what the combination produced
    4. Binding score: attention weight at expected binding vs random

  Critical probes = MINIMAL PAIRS:
    "The dog bit the cat" vs "The cat bit the dog"
    Same words, reversed binding. If attention flips → mechanism confirmed.

BINDING DIRECTION:
  s187 showed: H10 at position "dog" PRODUCES "runs" (Δ=64).
  Mechanism: Q("dog") matches K("runs"), selects V("runs") → output = runs(dog).
  Direction: argument position ATTENDS TO function position.
  The VALUE at the function position flows to the argument position.

ARCHITECTURE (Qwen3-8B):
  GQA: 32 Q heads, 8 KV groups (4 Q heads share each KV pair)
  head_dim=128, hidden=4096, 36 layers

Usage:
  uv run python scripts/experiments/binding_graph_trace.py
  uv run python scripts/experiments/binding_graph_trace.py --layers 30,33

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
import torch.nn.functional as F

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


# ══════════════════════════════════════════════════════════════════════════════
# PROBE DEFINITIONS with annotated binding structure
# ══════════════════════════════════════════════════════════════════════════════
#
# Each binding: (argument_token, function_token, description)
# Direction: argument ATTENDS TO function (V at function flows to argument)
#
# We use token substrings — matched against the tokenized sequence at runtime.

@dataclass
class BindingProbe:
    id: str
    prompt: str
    # Each binding: (arg_substring, func_substring, label)
    # arg attends to func: "dog" position attends to "runs" position
    bindings: list[tuple[str, str, str]]
    category: str
    pair_id: str = ""  # links minimal pairs


PROBES = [
    # ── Simple subject-verb binding ─────────────────────────────
    BindingProbe(
        id="sv1",
        prompt="The dog runs.",
        bindings=[("dog", "runs", "runs(dog)")],
        category="subject-verb",
        pair_id="sv",
    ),
    BindingProbe(
        id="sv2",
        prompt="The cat runs.",
        bindings=[("cat", "runs", "runs(cat)")],
        category="subject-verb",
        pair_id="sv",
    ),

    # ── Reversed binding (CRITICAL minimal pair) ────────────────
    BindingProbe(
        id="rev1",
        prompt="The dog bit the cat.",
        bindings=[
            ("dog", "bit", "bit(dog,_)"),     # agent
            ("cat", "bit", "bit(_,cat)"),     # patient
        ],
        category="reversed",
        pair_id="rev",
    ),
    BindingProbe(
        id="rev2",
        prompt="The cat bit the dog.",
        bindings=[
            ("cat", "bit", "bit(cat,_)"),     # agent — FLIPPED
            ("dog", "bit", "bit(_,dog)"),     # patient — FLIPPED
        ],
        category="reversed",
        pair_id="rev",
    ),

    # ── Ditransitive (3 bindings) ───────────────────────────────
    BindingProbe(
        id="ditrans",
        prompt="John gave Mary the book.",
        bindings=[
            ("John", "gave", "gave(john,_,_)"),
            ("Mary", "gave", "gave(_,mary,_)"),
            ("book", "gave", "gave(_,_,book)"),
        ],
        category="ditransitive",
    ),

    # ── Self-reference (W combinator) ──────────────────────────
    BindingProbe(
        id="self1",
        prompt="The dog bit itself.",
        bindings=[
            ("dog", "bit", "bit(dog,_)"),
            ("itself", "dog", "itself→dog"),    # coreference: itself binds to dog
            ("itself", "bit", "bit(_,itself)"),
        ],
        category="self-reference",
    ),

    # ── Nested relative clause ──────────────────────────────────
    BindingProbe(
        id="nested1",
        prompt="The cat that sat on the mat is black.",
        bindings=[
            ("cat", "sat", "sat(cat,_)"),       # relative clause binding
            ("mat", "sat", "sat(_,mat)"),        # PP binding inside relative
            ("cat", "black", "black(cat)"),      # main clause predicate
        ],
        category="nested",
    ),

    # ── Quantifier scope ────────────────────────────────────────
    BindingProbe(
        id="quant1",
        prompt="Every student reads a book.",
        bindings=[
            ("student", "reads", "reads(student,_)"),
            ("book", "reads", "reads(_,book)"),
            ("Every", "student", "∀(student)"),   # quantifier binds to NP
        ],
        category="quantifier",
    ),

    # ── Conditional ─────────────────────────────────────────────
    BindingProbe(
        id="cond1",
        prompt="If it rains, the ground is wet.",
        bindings=[
            ("it", "rains", "rains(it)"),
            ("ground", "wet", "wet(ground)"),
            ("rains", "wet", "rains→wet"),        # conditional dependency
        ],
        category="conditional",
    ),

    # ── Passive (C combinator — argument flip) ──────────────────
    BindingProbe(
        id="pass1",
        prompt="The ball was kicked by the boy.",
        bindings=[
            ("boy", "kicked", "kicked(boy,_)"),   # agent (despite being in by-phrase)
            ("ball", "kicked", "kicked(_,ball)"),  # patient (despite being subject)
        ],
        category="passive",
        pair_id="voice",
    ),
    BindingProbe(
        id="act1",
        prompt="The boy kicked the ball.",
        bindings=[
            ("boy", "kicked", "kicked(boy,_)"),
            ("ball", "kicked", "kicked(_,ball)"),
        ],
        category="active",
        pair_id="voice",
    ),

    # ── Recursion (Y combinator) ────────────────────────────────
    BindingProbe(
        id="recur1",
        prompt="A folder contains files and other folders which contain files.",
        bindings=[
            ("folder", "contains", "contains(folder,_)"),
            ("files", "contains", "contains(_,files)"),
            ("folders", "contain", "contains(folders,_)"),  # recursive
        ],
        category="recursion",
    ),

    # ── Identity (K combinator — discard) ───────────────────────
    BindingProbe(
        id="discard1",
        prompt="Of all the animals, only the lion was truly fierce.",
        bindings=[
            ("lion", "fierce", "fierce(lion)"),
            # "animals" is K-discarded — should NOT bind to fierce
        ],
        category="discard",
    ),

    # ── Long-distance dependency ────────────────────────────────
    BindingProbe(
        id="long1",
        prompt="The man that the woman that the child saw met left.",
        bindings=[
            ("child", "saw", "saw(child,_)"),
            ("woman", "saw", "saw(_,woman)"),      # object of "saw"
            ("woman", "met", "met(woman,_)"),      # subject of "met"
            ("man", "met", "met(_,man)"),           # object of "met"
            ("man", "left", "left(man)"),           # subject of "left"
        ],
        category="long-distance",
    ),
]


def find_token_positions(tokens: list[str], substring: str, gate_len: int) -> list[int]:
    """Find positions of tokens matching a substring (case-insensitive, strip whitespace).

    Returns positions (absolute, including gate) where the token contains the substring.
    Only searches in probe positions (after gate_len).
    """
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
    log("BINDING GRAPH TRACE")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Probes: {len(PROBES)}")
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

    if layer_indices is None:
        layer_indices = [27, 30, 33]
    layer_indices = [l for l in layer_indices if l < n_layers]
    log(f"  Target layers: {layer_indices}")

    # ── Unembed and O projection ────────────────────────────────
    if hasattr(model, "lm_head"):
        W_unembed = model.lm_head.weight.data.cpu().float()
    else:
        W_unembed = model.model.embed_tokens.weight.data.cpu().float()
    log(f"  W_unembed: {W_unembed.shape}")

    W_o_heads: dict[int, list[torch.Tensor]] = {}
    for li in layer_indices:
        W_o = model.model.layers[li].self_attn.o_proj.weight.data.cpu().float()
        W_o_heads[li] = [
            W_o[:, h * head_dim : (h + 1) * head_dim]
            for h in range(n_q_heads)
        ]

    # ── Compile gate ────────────────────────────────────────────
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
        log(f"  Category: {probe.category}")
        log(f"  Expected bindings: {len(probe.bindings)}")
        for arg, func, label in probe.bindings:
            log(f"    {arg} → {func} = {label}")

        full_text = compile_gate + probe.prompt
        inputs = tokenizer(full_text, return_tensors="pt")
        input_ids = inputs["input_ids"].to(model.device)
        seq_len = input_ids.shape[1]
        tokens = [tokenizer.decode(t) for t in input_ids[0]]
        probe_tokens = tokens[gate_len:]

        log(f"  Tokens ({len(probe_tokens)}): {probe_tokens}")

        # ── Resolve binding positions ───────────────────────────
        resolved_bindings = []
        for arg_sub, func_sub, label in probe.bindings:
            arg_positions = find_token_positions(tokens, arg_sub, gate_len)
            func_positions = find_token_positions(tokens, func_sub, gate_len)
            if arg_positions and func_positions:
                resolved_bindings.append({
                    "arg_sub": arg_sub,
                    "func_sub": func_sub,
                    "label": label,
                    "arg_positions": arg_positions,
                    "func_positions": func_positions,
                })
                log(f"    ✓ {arg_sub}@{arg_positions} → {func_sub}@{func_positions}")
            else:
                log(f"    ✗ {arg_sub}({arg_positions}) → {func_sub}({func_positions}) UNRESOLVED")

        # ── Hooks ───────────────────────────────────────────────
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
                    input_shape = hidden_states.shape[:-1]
                    hidden_shape = (*input_shape, -1, head_dim)

                    with torch.no_grad():
                        v = module.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)
                        attn_weights = output[1]

                        if attn_weights is not None:
                            v_expanded = v.repeat_interleave(q_per_kv, dim=1)
                            per_head = torch.matmul(attn_weights, v_expanded)

                            captured[layer_idx] = {
                                "v": v[0].cpu().float(),              # (n_kv, seq, d)
                                "attn": attn_weights[0].cpu().float(), # (n_q, seq, seq)
                                "head_out": per_head[0].cpu().float(), # (n_q, seq, d)
                            }
                    return output
                return hook_fn

            h = attn_module.register_forward_hook(make_hook(li), with_kwargs=True)
            hooks.append(h)

        with torch.no_grad():
            model(input_ids, output_attentions=True, return_dict=True)

        for h in hooks:
            h.remove()

        # ── Analyze per layer ───────────────────────────────────
        probe_result = {
            "id": probe.id,
            "prompt": probe.prompt,
            "category": probe.category,
            "pair_id": probe.pair_id,
            "tokens": probe_tokens,
            "gate_len": gate_len,
            "seq_len": seq_len,
            "resolved_bindings": resolved_bindings,
            "layers": {},
        }

        for li in layer_indices:
            if li not in captured:
                continue

            v_vecs = captured[li]["v"]       # (n_kv, seq, d)
            attn = captured[li]["attn"]       # (n_q, seq, seq)
            head_out = captured[li]["head_out"]  # (n_q, seq, d)

            layer_result = {
                "layer": li,
                "v_unembed": {},   # pos → top tokens from V
                "binding_scores": [],   # per binding, per head
                "head_outputs": {},     # head → pos → top tokens
                "attention_at_bindings": [],  # raw attention values at binding positions
            }

            # ── 1. V through O projection → unembed ────────────
            # V is (n_kv, seq, head_dim=128). To read in token space,
            # project through the O projection slice for each KV group's
            # first Q head, then through unembed.
            for pos in range(gate_len, seq_len):
                # Average across KV groups projected through their O slices
                v_residuals = []
                for kv_g in range(n_kv_heads):
                    q_head = kv_g * q_per_kv  # first Q head in this group
                    v_vec = v_vecs[kv_g, pos]  # (head_dim,)
                    W_o_h = W_o_heads[li][q_head]  # (hidden, head_dim)
                    v_residuals.append(W_o_h @ v_vec)  # (hidden,)
                v_residual = torch.stack(v_residuals).mean(dim=0)  # (hidden,)
                v_logits = W_unembed @ v_residual
                top_vals, top_idx = v_logits.topk(top_k)
                v_tokens = [(tokenizer.decode(t.item()).strip(), round(v.item(), 2))
                            for t, v in zip(top_idx, top_vals)]
                layer_result["v_unembed"][pos - gate_len] = {
                    "token": tokens[pos].strip(),
                    "v_promotes": v_tokens[:5],
                }

            # ── 2. Binding scores per head ──────────────────────
            for binding in resolved_bindings:
                arg_positions = binding["arg_positions"]
                func_positions = binding["func_positions"]
                label = binding["label"]

                binding_head_scores = []

                for h in range(n_q_heads):
                    # For each arg position, measure attention to func positions
                    binding_weights = []
                    total_probe_weights = []

                    for arg_pos in arg_positions:
                        attn_row = attn[h, arg_pos]  # (seq,)

                        # Attention weight at function positions
                        for func_pos in func_positions:
                            binding_weights.append(attn_row[func_pos].item())

                        # Total attention to all probe positions (baseline)
                        probe_attn = attn_row[gate_len:].sum().item()
                        total_probe_weights.append(probe_attn)

                    mean_binding_weight = float(np.mean(binding_weights))
                    n_probe_positions = seq_len - gate_len
                    # Expected by chance: if attention were uniform over probe positions
                    chance_weight = (1.0 / seq_len) * len(func_positions)

                    # Head output at arg positions through unembed
                    head_output_tokens = []
                    for arg_pos in arg_positions:
                        W_o_h = W_o_heads[li][h]
                        h_out = head_out[h, arg_pos]
                        contrib = W_o_h @ h_out
                        logits = W_unembed @ contrib
                        top_vals, top_idx = logits.topk(5)
                        head_output_tokens.append([
                            (tokenizer.decode(t.item()).strip(), round(v.item(), 2))
                            for t, v in zip(top_idx, top_vals)
                        ])

                    binding_head_scores.append({
                        "head": h,
                        "binding_weight": round(mean_binding_weight, 4),
                        "chance_weight": round(chance_weight, 4),
                        "ratio": round(mean_binding_weight / chance_weight, 2) if chance_weight > 0 else 0,
                        "head_output_at_arg": head_output_tokens,
                    })

                # Sort by binding weight
                binding_head_scores.sort(key=lambda x: x["binding_weight"], reverse=True)

                layer_result["binding_scores"].append({
                    "label": label,
                    "arg": binding["arg_sub"],
                    "func": binding["func_sub"],
                    "arg_positions": arg_positions,
                    "func_positions": func_positions,
                    "heads": binding_head_scores,
                })

            # ── 3. Full attention pattern at binding positions ──
            # For the top binding, show full attention row at arg position
            # for top 5 heads (most binding weight)
            for bi, binding in enumerate(resolved_bindings):
                if not binding["arg_positions"]:
                    continue
                arg_pos = binding["arg_positions"][0]
                scores = layer_result["binding_scores"][bi]["heads"]

                for head_info in scores[:5]:
                    h = head_info["head"]
                    attn_row = attn[h, arg_pos]
                    # Full attention over probe positions
                    probe_attn = []
                    for p in range(gate_len, seq_len):
                        probe_attn.append({
                            "pos": p - gate_len,
                            "token": tokens[p].strip(),
                            "weight": round(attn_row[p].item(), 4),
                            "is_func": p in binding["func_positions"],
                        })
                    probe_attn.sort(key=lambda x: x["weight"], reverse=True)

                    layer_result["attention_at_bindings"].append({
                        "binding_label": binding["label"],
                        "arg_token": tokens[arg_pos].strip(),
                        "arg_pos": arg_pos - gate_len,
                        "head": h,
                        "binding_weight": head_info["binding_weight"],
                        "attention_over_probe": probe_attn,
                    })

            probe_result["layers"][li] = layer_result

        all_results.append(probe_result)
        del captured

    # ══════════════════════════════════════════════════════════════
    # ANALYSIS
    # ══════════════════════════════════════════════════════════════

    log(f"\n{'=' * 72}")
    log("ANALYSIS: DOES ATTENTION = BINDING GRAPH?")
    log("=" * 72)

    for li in layer_indices:
        log(f"\n{'─' * 60}")
        log(f"LAYER {li}")
        log("─" * 60)

        # ── Per-probe binding analysis ──────────────────────────
        for result in all_results:
            if li not in result["layers"]:
                continue
            layer = result["layers"][li]

            log(f"\n  [{result['id']}] \"{result['prompt']}\"")

            # Show V vectors
            log(f"    V through unembed (what FFN compiled):")
            for pos_key, v_data in layer["v_unembed"].items():
                tok = v_data["token"]
                promotes = ", ".join(f"{t}" for t, v in v_data["v_promotes"][:3])
                log(f"      [{tok:>12s}] → {promotes}")

            # Show binding scores
            for bs in layer["binding_scores"]:
                log(f"\n    BINDING: {bs['arg']} → {bs['func']} = {bs['label']}")
                log(f"    arg@{[p - result['gate_len'] for p in bs['arg_positions']]} "
                    f"→ func@{[p - result['gate_len'] for p in bs['func_positions']]}")

                # Top 5 heads for this binding
                log(f"    {'Head':>6s} {'Bind.Wt':>8s} {'Chance':>8s} {'Ratio':>6s}  Output at arg position")
                for hi in bs["heads"][:8]:
                    h = hi["head"]
                    bw = hi["binding_weight"]
                    cw = hi["chance_weight"]
                    ratio = hi["ratio"]
                    # Head output at arg
                    if hi["head_output_at_arg"]:
                        out_str = ", ".join(f"{t}" for t, v in hi["head_output_at_arg"][0][:3])
                    else:
                        out_str = "—"
                    marker = " ◆" if ratio > 5 else " •" if ratio > 2 else ""
                    log(f"    H{h:02d}   {bw:8.4f} {cw:8.4f} {ratio:6.1f}x  [{out_str}]{marker}")

            # Show attention pattern for top binding
            if layer["attention_at_bindings"]:
                log(f"\n    ATTENTION PATTERNS (from arg, top 3 heads):")
                seen = set()
                for attn_info in layer["attention_at_bindings"]:
                    key = (attn_info["binding_label"], attn_info["head"])
                    if key in seen:
                        continue
                    seen.add(key)
                    if len(seen) > 6:
                        break
                    h = attn_info["head"]
                    log(f"      H{h:02d} at [{attn_info['arg_token']}] "
                        f"for {attn_info['binding_label']}:")
                    for item in attn_info["attention_over_probe"][:6]:
                        marker = " ★" if item["is_func"] else ""
                        log(f"        {item['token']:>12s} ({item['pos']:2d}): "
                            f"{item['weight']:.4f}{marker}")

    # ── Cross-probe head consistency ────────────────────────────
    log(f"\n{'=' * 72}")
    log("HEAD BINDING CONSISTENCY ACROSS PROBES")
    log("=" * 72)
    log("Which heads consistently route according to binding structure?")

    for li in layer_indices:
        log(f"\n  L{li}:")
        # Collect binding ratios per head across all probes
        head_ratios: dict[int, list[float]] = defaultdict(list)
        head_weights: dict[int, list[float]] = defaultdict(list)

        for result in all_results:
            if li not in result["layers"]:
                continue
            for bs in result["layers"][li]["binding_scores"]:
                for hi in bs["heads"]:
                    head_ratios[hi["head"]].append(hi["ratio"])
                    head_weights[hi["head"]].append(hi["binding_weight"])

        # Rank heads by mean ratio (binding weight / chance)
        head_stats = []
        for h in range(n_q_heads):
            if head_ratios[h]:
                mean_ratio = float(np.mean(head_ratios[h]))
                median_ratio = float(np.median(head_ratios[h]))
                mean_weight = float(np.mean(head_weights[h]))
                # Fraction of bindings where this head is in top 5
                n_bindings = len(head_ratios[h])
                top5_count = sum(1 for r in head_ratios[h] if r > 2)
                head_stats.append((h, mean_ratio, median_ratio, mean_weight,
                                   top5_count, n_bindings))

        head_stats.sort(key=lambda x: x[1], reverse=True)
        log(f"    {'Head':>6s} {'MeanRatio':>10s} {'MedRatio':>10s} {'MeanWt':>8s} "
            f"{'Bind>2x':>8s} {'N':>4s}")
        for h, mr, medr, mw, t5, n in head_stats[:15]:
            log(f"    H{h:02d}   {mr:10.2f} {medr:10.2f} {mw:8.4f} "
                f"{t5:>4d}/{n:<4d} {'◆' if mr > 3 else '•' if mr > 2 else ''}")

    # ── Minimal pair analysis ───────────────────────────────────
    log(f"\n{'=' * 72}")
    log("MINIMAL PAIR ANALYSIS: Does binding flip with structure?")
    log("=" * 72)

    pair_ids = set(p.pair_id for p in PROBES if p.pair_id)
    for pair_id in sorted(pair_ids):
        pair_probes = [r for r in all_results if r["pair_id"] == pair_id]
        if len(pair_probes) < 2:
            continue

        log(f"\n  Pair '{pair_id}':")
        for result in pair_probes:
            log(f"    [{result['id']}] \"{result['prompt']}\"")

        for li in layer_indices:
            log(f"\n    L{li}:")
            for result in pair_probes:
                if li not in result["layers"]:
                    continue
                layer = result["layers"][li]
                log(f"      [{result['id']}]")
                for bs in layer["binding_scores"]:
                    # Show top 3 heads
                    top3 = bs["heads"][:3]
                    top_str = ", ".join(
                        f"H{h['head']:02d}({h['binding_weight']:.3f})"
                        for h in top3
                    )
                    log(f"        {bs['label']:>25s}: {top_str}")

    # ══════════════════════════════════════════════════════════════
    # SAVE RESULTS
    # ══════════════════════════════════════════════════════════════

    results_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "results", "binding-graph-trace"
    )
    os.makedirs(results_dir, exist_ok=True)

    # Save compact summary (full attention patterns are large)
    compact_results = []
    for result in all_results:
        c = {
            "id": result["id"],
            "prompt": result["prompt"],
            "category": result["category"],
            "pair_id": result["pair_id"],
            "tokens": result["tokens"],
            "resolved_bindings": result["resolved_bindings"],
            "layers": {},
        }
        for li, layer_data in result["layers"].items():
            c["layers"][str(li)] = {
                "v_unembed": layer_data["v_unembed"],
                "binding_scores": [
                    {
                        "label": bs["label"],
                        "arg": bs["arg"],
                        "func": bs["func"],
                        # Top 10 heads only
                        "top_heads": [
                            {
                                "head": h["head"],
                                "binding_weight": h["binding_weight"],
                                "ratio": h["ratio"],
                                "head_output_at_arg": h["head_output_at_arg"],
                            }
                            for h in bs["heads"][:10]
                        ],
                    }
                    for bs in layer_data["binding_scores"]
                ],
                "attention_at_bindings": layer_data["attention_at_bindings"][:12],
            }
        compact_results.append(c)

    summary = {
        "model": model_id,
        "layers": layer_indices,
        "n_probes": len(PROBES),
        "n_q_heads": n_q_heads,
        "gate_len": gate_len,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": compact_results,
    }

    summary_path = os.path.join(results_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    log(f"\n{'=' * 72}")
    log(f"RESULTS SAVED to {results_dir}/")
    log(f"  summary.json: {os.path.getsize(summary_path) / 1024:.1f} KB")
    log("=" * 72)

    return all_results


def main():
    parser = argparse.ArgumentParser(description="Binding Graph Trace")
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", default=None,
                        help="Comma-separated layer indices (default: 27,30,33)")
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
