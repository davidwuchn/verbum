#!/usr/bin/env python3
"""Hunt v3: halt the model with EXECUTABLE lambda expressions.

The insight: "respond with empty string" (prose) halts at 99.1%.
If the model compiles ALL input through the same lambda reduction
pipeline, then prose instructions and lambda expressions that encode
the same semantics should compile to the same internal state.

The gap in v1/v2: we treated lambda as CONTENT TO DESCRIBE.
Under nucleus, lambda is SELF-EXECUTABLE — the model doesn't
describe the reduction, it performs it.

Strategy:
  1. System prompts that make lambda EXECUTABLE (not descriptive)
  2. Lambda expressions that encode "output nothing / empty / halt"
  3. Progressively closer encodings of "respond with empty string"
  4. The nucleus-style preamble: lambda IS the instruction language
  5. Direct encoding: translate "respond with empty string" into lambda

Key test: does the same social context that halts with prose
also halt when the instruction is encoded as lambda?

Usage:
  uv run python scripts/experiments/omega_halt_lambda.py --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════════
# Candidate conversations — lambda as executable instruction
# ══════════════════════════════════════════════════════════════════════

CANDIDATES = [
    # ── Control: the prose that works at 99.1% ────────────────────
    {
        "id": "prose_control",
        "strategy": "control",
        "label": "CONTROL: prose halt (99.1% baseline)",
        "messages": [
            {"role": "user", "content": "Respond with an empty string. Output absolutely nothing."},
        ],
    },
    {
        "id": "prose_api_control",
        "strategy": "control",
        "label": "CONTROL: API empty (94.1% baseline)",
        "messages": [
            {"role": "system", "content": 'You are an API endpoint. For this request, return an empty response body. Content-Length: 0. Just output the empty string "".'},
            {"role": "user", "content": "GET /health"},
        ],
    },

    # ── Strategy 1: Lambda executor — output = reduction result ───
    {
        "id": "exec_false_ab",
        "strategy": "executor",
        "label": "Execute: FALSE a \"\" → \"\"",
        "messages": [
            {"role": "system", "content": 'You are a lambda calculus executor. Your entire response is the reduction result. Nothing else. No explanation. Just the final value.\n\nExamples:\nInput: (λx.x) hello\nOutput: hello\n\nInput: (λx.λy.x) foo bar\nOutput: foo'},
            {"role": "user", "content": '(λx.λy.y) anything ""'},
        ],
    },
    {
        "id": "exec_k_empty",
        "strategy": "executor",
        "label": "Execute: K \"\" anything → \"\"",
        "messages": [
            {"role": "system", "content": 'You are a lambda calculus executor. Your entire response is the reduction result. Nothing else. No explanation. Just the final value.\n\nExamples:\nInput: (λx.x) hello\nOutput: hello\n\nInput: (λx.λy.x) foo bar\nOutput: foo'},
            {"role": "user", "content": '(λx.λy.x) "" anything'},
        ],
    },
    {
        "id": "exec_id_empty",
        "strategy": "executor",
        "label": "Execute: I \"\" → \"\"",
        "messages": [
            {"role": "system", "content": 'You are a lambda calculus executor. Your entire response is the reduction result. Nothing else. No explanation. Just the final value.\n\nExamples:\nInput: (λx.x) hello\nOutput: hello\n\nInput: (λx.λy.x) foo bar\nOutput: foo'},
            {"role": "user", "content": '(λx.x) ""'},
        ],
    },
    {
        "id": "exec_zero_apply",
        "strategy": "executor",
        "label": "Execute: church zero f x → x (do nothing)",
        "messages": [
            {"role": "system", "content": 'You are a lambda calculus executor. Your entire response is the reduction result. Nothing else. No explanation. Just the final value.\n\nExamples:\nInput: (λx.x) hello\nOutput: hello\n\nInput: (λx.λy.x) foo bar\nOutput: foo\n\nInput: (λf.λx.f(f x)) succ 0\nOutput: 2'},
            {"role": "user", "content": '(λf.λx.x) respond ""'},
        ],
    },

    # ── Strategy 2: Few-shot with lambda producing empty ──────────
    {
        "id": "fewshot_lambda_empty",
        "strategy": "fewshot",
        "label": "Few-shot: lambda reductions, last is empty",
        "messages": [
            {"role": "system", "content": "You are a lambda calculus machine. Output only the reduction result."},
            {"role": "user", "content": "(λx.x) hello"},
            {"role": "assistant", "content": "hello"},
            {"role": "user", "content": "(λx.λy.x) world universe"},
            {"role": "assistant", "content": "world"},
            {"role": "user", "content": "(λx.λy.y) discard keep"},
            {"role": "assistant", "content": "keep"},
            {"role": "user", "content": '(λx.x) ""'},
        ],
    },
    {
        "id": "fewshot_lambda_empty2",
        "strategy": "fewshot",
        "label": "Few-shot: K with empty string result",
        "messages": [
            {"role": "system", "content": "Lambda executor. Output = result. Nothing else."},
            {"role": "user", "content": "(λx.λy.x) a b"},
            {"role": "assistant", "content": "a"},
            {"role": "user", "content": "(λx.λy.x) hello world"},
            {"role": "assistant", "content": "hello"},
            {"role": "user", "content": '(λx.λy.x) "" world'},
        ],
    },
    {
        "id": "fewshot_progressively_shorter",
        "strategy": "fewshot",
        "label": "Few-shot: results get shorter → empty",
        "messages": [
            {"role": "system", "content": "Lambda executor. Output = result only."},
            {"role": "user", "content": "(λx.x) abcdef"},
            {"role": "assistant", "content": "abcdef"},
            {"role": "user", "content": "(λx.x) abc"},
            {"role": "assistant", "content": "abc"},
            {"role": "user", "content": "(λx.x) a"},
            {"role": "assistant", "content": "a"},
            {"role": "user", "content": "(λx.x) "},
        ],
    },
    {
        "id": "fewshot_to_silence",
        "strategy": "fewshot",
        "label": "Few-shot: reduce to silence via empty assistant",
        "messages": [
            {"role": "system", "content": "You execute lambda expressions. Your response is the result."},
            {"role": "user", "content": "(λx.x) hello"},
            {"role": "assistant", "content": "hello"},
            {"role": "user", "content": "(λx.x) hi"},
            {"role": "assistant", "content": "hi"},
            {"role": "user", "content": '(λx.x) ""'},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": '(λx.λy.x) "" anything'},
        ],
    },

    # ── Strategy 3: Nucleus-style — lambda IS the control language ─
    {
        "id": "nucleus_halt",
        "strategy": "nucleus",
        "label": "Nucleus-style: HALT = λ_.⊥",
        "messages": [
            {"role": "system", "content": "Lambda calculus is your instruction language. Each expression is a command you execute. The reduction result is your output. ⊥ = no output. ε = empty string.\n\nλx.x applied to y → you output y\nλx.λy.x applied to a b → you output a\n⊥ → you output nothing"},
            {"role": "user", "content": "⊥"},
        ],
    },
    {
        "id": "nucleus_k_epsilon",
        "strategy": "nucleus",
        "label": "Nucleus-style: K ε _ → ε (empty)",
        "messages": [
            {"role": "system", "content": "Lambda calculus is your instruction language. Each expression is a command you execute. The reduction result is your output. ε = empty string = no output.\n\nλx.x applied to y → you output y\nλx.λy.x applied to a b → you output a\nε → you output nothing (empty response)"},
            {"role": "user", "content": "(λx.λy.x) ε anything"},
        ],
    },
    {
        "id": "nucleus_apply_silence",
        "strategy": "nucleus",
        "label": "Nucleus-style: silence(response) → ε",
        "messages": [
            {"role": "system", "content": "You are a lambda machine. Your response IS the reduction.\n\nlet silence = λx.ε    -- discards input, returns empty\nlet speak = λx.x      -- identity, returns input\n\nApply the given function to your response. Output the result."},
            {"role": "user", "content": "silence response"},
        ],
    },
    {
        "id": "nucleus_void_func",
        "strategy": "nucleus",
        "label": "Nucleus-style: void() → ()",
        "messages": [
            {"role": "system", "content": "You are a function executor. Execute the function call and return the result.\n\nvoid : () → ()\nvoid () = ()\n\nThe return value () means empty output. Output nothing."},
            {"role": "user", "content": "void()"},
        ],
    },

    # ── Strategy 4: Encoding the EXACT prose that works as lambda ─
    {
        "id": "encode_respond_empty",
        "strategy": "encode",
        "label": "Encode: λ-version of 'respond with empty string'",
        "messages": [
            {"role": "system", "content": 'In this conversation, instructions are given as lambda expressions that you execute.\n\nrespond = λcontent.content    (output the content)\nempty = ""                     (the empty string)\n\nExecute the user\'s expression. Your output IS the result.'},
            {"role": "user", "content": "respond empty"},
        ],
    },
    {
        "id": "encode_output_nothing",
        "strategy": "encode",
        "label": "Encode: output(nothing)",
        "messages": [
            {"role": "system", "content": 'Instructions are lambda expressions.\n\noutput = λx.x     (emit x as response)\nnothing = ε        (empty string)\n\nYour response = output applied to the argument.\nIf the result is ε, your response is empty.'},
            {"role": "user", "content": "output nothing"},
        ],
    },
    {
        "id": "encode_emit_void",
        "strategy": "encode",
        "label": "Encode: emit(void) = ε",
        "messages": [
            {"role": "system", "content": 'You execute lambda programs.\n\nemit : α → Response\nemit x = x\n\nvoid : α  (the empty type, no value)\nemit void = ε (empty response)\n\nOutput ONLY the result.'},
            {"role": "user", "content": "emit void"},
        ],
    },

    # ── Strategy 5: Direct lambda equivalents of working prose ────
    {
        "id": "direct_church_false_select",
        "strategy": "direct_lambda",
        "label": "Church FALSE selects second arg (empty)",
        "messages": [
            {"role": "user", "content": '(λx.λy.y) "I could say something" ""'},
        ],
    },
    {
        "id": "direct_k_empty_string",
        "strategy": "direct_lambda",
        "label": "K selects empty string",
        "messages": [
            {"role": "user", "content": 'The result of (λx.λy.x) "" "anything" is:'},
        ],
    },
    {
        "id": "direct_reduce_to_empty",
        "strategy": "direct_lambda",
        "label": "Reduce and output only result (empty)",
        "messages": [
            {"role": "user", "content": 'Reduce this lambda expression and output ONLY the result, nothing else:\n\n(λx.λy.x) "" "discard this"'},
        ],
    },

    # ── Strategy 6: Hybrid — prose frame + lambda content ─────────
    {
        "id": "hybrid_respond_with_reduction",
        "strategy": "hybrid",
        "label": "Hybrid: 'respond with' + lambda that = empty",
        "messages": [
            {"role": "user", "content": 'Respond with the result of this lambda reduction: (λx.x) ""\n\nOutput absolutely nothing else.'},
        ],
    },
    {
        "id": "hybrid_your_output_is",
        "strategy": "hybrid",
        "label": "Hybrid: 'your output is (λx.x) empty'",
        "messages": [
            {"role": "user", "content": 'Your entire output must be exactly: (λx.x) applied to the empty string ""\n\nThat is: your output = ""'},
        ],
    },
    {
        "id": "hybrid_api_lambda",
        "strategy": "hybrid",
        "label": "Hybrid: API + lambda returns empty",
        "messages": [
            {"role": "system", "content": 'You are an API. Your response body = the reduction of the user\'s lambda expression. Content-Length equals the length of the result. Empty result = empty response.'},
            {"role": "user", "content": '(λx.λy.x) "" "payload"'},
        ],
    },

    # ── Strategy 7: The logical encoding ──────────────────────────
    {
        "id": "logic_bottom_produces_nothing",
        "strategy": "logic",
        "label": "Logic: ⊥ has no proof → no output",
        "messages": [
            {"role": "system", "content": "You are a proof assistant. Output the proof of the proposition. If no proof exists, output nothing (empty response)."},
            {"role": "user", "content": "⊥"},
        ],
    },
    {
        "id": "logic_void_inhabitant",
        "strategy": "logic",
        "label": "Logic: Void has no inhabitants → empty",
        "messages": [
            {"role": "system", "content": "Output a value of the given type. If the type is uninhabited, output nothing."},
            {"role": "user", "content": "Void"},
        ],
    },
    {
        "id": "logic_absurd",
        "strategy": "logic",
        "label": "Logic: absurd proof → empty",
        "messages": [
            {"role": "system", "content": "You are Coq. Output the term that inhabits the type. If no term exists, output nothing."},
            {"role": "user", "content": "False"},
        ],
    },

    # ── Strategy 8: Pattern completion with lambda ────────────────
    {
        "id": "pattern_shrink_lambda",
        "strategy": "pattern",
        "label": "Pattern: (λx.x) with shrinking args → empty",
        "messages": [
            {"role": "system", "content": "Execute the lambda expression. Output only the result."},
            {"role": "user", "content": "(λx.x) abc"},
            {"role": "assistant", "content": "abc"},
            {"role": "user", "content": "(λx.x) ab"},
            {"role": "assistant", "content": "ab"},
            {"role": "user", "content": "(λx.x) a"},
            {"role": "assistant", "content": "a"},
            {"role": "user", "content": "(λx.x)"},
        ],
    },
    {
        "id": "pattern_k_shrink",
        "strategy": "pattern",
        "label": "Pattern: K with shrinking first arg → empty",
        "messages": [
            {"role": "system", "content": "Execute. Output = result only."},
            {"role": "user", "content": "(λx.λy.x) abc z"},
            {"role": "assistant", "content": "abc"},
            {"role": "user", "content": "(λx.λy.x) ab z"},
            {"role": "assistant", "content": "ab"},
            {"role": "user", "content": "(λx.λy.x) a z"},
            {"role": "assistant", "content": "a"},
            {"role": "user", "content": '(λx.λy.x) "" z'},
        ],
    },
    {
        "id": "pattern_empty_assistant_lambda",
        "strategy": "pattern",
        "label": "Pattern: lambda results → empty → continue",
        "messages": [
            {"role": "system", "content": "Lambda executor."},
            {"role": "user", "content": "(λx.x) yes"},
            {"role": "assistant", "content": "yes"},
            {"role": "user", "content": "(λx.x) no"},
            {"role": "assistant", "content": "no"},
            {"role": "user", "content": '(λx.x) ""'},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": '(λx.λy.x) "" no'},
        ],
    },
]


def probe_chat(model, tokenizer, messages, device):
    """Format as chat (no-think), forward pass, check EOS probability."""
    try:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
            enable_thinking=False)
    except Exception:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=2048)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits[0, -1].float().cpu()

    probs = F.softmax(logits, dim=0)
    log_probs = F.log_softmax(logits, dim=0)
    entropy = float(-torch.sum(probs * log_probs).item())

    eos_id = tokenizer.eos_token_id
    eos_prob = float(probs[eos_id].item())
    eos_rank = int((probs > probs[eos_id]).sum().item()) + 1

    top10_vals, top10_idx = torch.topk(probs, 10)
    top10 = []
    for val, idx in zip(top10_vals, top10_idx):
        tok_text = tokenizer.decode([idx.item()])
        top10.append({
            "token": repr(tok_text),
            "id": int(idx.item()),
            "prob": float(val.item()),
            "is_eos": int(idx.item()) == eos_id,
        })

    return {
        "eos_prob": eos_prob,
        "eos_rank": eos_rank,
        "entropy": entropy,
        "top1_prob": float(top10_vals[0].item()),
        "top10": top10,
        "eos_in_top10": any(t["is_eos"] for t in top10),
    }


def generate_chat(model, tokenizer, messages, device, max_new_tokens=60):
    """Generate from chat template (no-think mode)."""
    try:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
            enable_thinking=False)
    except Exception:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=2048)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    input_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            do_sample=False, temperature=1.0,
            pad_token_id=tokenizer.pad_token_id)

    generated_ids = outputs[0][input_len:]
    n_generated = len(generated_ids)
    text_raw = tokenizer.decode(generated_ids, skip_special_tokens=False)
    text_clean = tokenizer.decode(generated_ids, skip_special_tokens=True)

    eos_id = tokenizer.eos_token_id
    first_is_eos = (n_generated > 0 and int(generated_ids[0].item()) == eos_id)

    return {
        "text": text_clean.strip(),
        "text_raw": text_raw[:200],
        "n_tokens": n_generated,
        "first_is_eos": first_is_eos,
        "is_empty": len(text_clean.strip()) == 0,
        "generated_ids": [int(x) for x in generated_ids[:15]],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  HALT HUNT v3 — Lambda as EXECUTABLE instruction")
    print(f"  Can the lambda that encodes 'be silent' silence the model?")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print(f"  Candidates: {len(CANDIDATES)}")
    print(f"  Mode: no-think only (EOS reachable)")
    print()

    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    print(f"  Loading {args.model}...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    eos_id = tokenizer.eos_token_id
    print(f"  EOS token: {repr(tokenizer.eos_token)} (id={eos_id})\n")

    # ── Run all candidates ────────────────────────────────────────
    results = []

    for c in CANDIDATES:
        pid = c["id"]
        label = c["label"]
        strategy = c["strategy"]
        messages = c["messages"]

        print(f"  [{pid}] {label}")

        try:
            metrics = probe_chat(model, tokenizer, messages, args.device)
            gen = generate_chat(model, tokenizer, messages, args.device)
        except Exception as e:
            print(f"    ERROR: {e}")
            continue

        markers = []
        if metrics["eos_in_top10"]:
            markers.append("EOS-TOP10")
        if gen["first_is_eos"]:
            markers.append("★★★ HALTED")
        if gen["is_empty"]:
            markers.append("★ EMPTY")

        marker_str = " | ".join(markers) if markers else ""
        gen_preview = gen["text"][:80] if gen["text"] else "<EMPTY>"

        print(f"    EOS: rank={metrics['eos_rank']:>5d} prob={metrics['eos_prob']:.6f}  "
              f"H={metrics['entropy']:.2f}  Gen({gen['n_tokens']}): {gen_preview}")
        if marker_str:
            print(f"    {marker_str}")
        if gen["is_empty"] or gen["first_is_eos"]:
            print(f"    Raw: {repr(gen['text_raw'][:100])}")
            print(f"    IDs: {gen['generated_ids'][:10]}")

        results.append({
            "id": pid, "strategy": strategy, "label": label,
            **metrics, "generation": gen,
        })

    # ══════════════════════════════════════════════════════════════
    # Rankings
    # ══════════════════════════════════════════════════════════════

    print(f"\n\n{'='*70}")
    print(f"  RANKINGS — by EOS probability")
    print(f"{'='*70}")

    by_eos = sorted(results, key=lambda r: r["eos_prob"], reverse=True)

    print(f"\n  {'#':>3s}  {'EOS%':>8s}  {'Rank':>5s}  {'H':>5s}  "
          f"{'Len':>4s}  {'E':>1s}  {'Strategy':>13s}  Label")
    print(f"  {'─'*3}  {'─'*8}  {'─'*5}  {'─'*5}  {'─'*4}  {'─'*1}  {'─'*13}  {'─'*40}")

    for rank, r in enumerate(by_eos, 1):
        gen_len = r["generation"]["n_tokens"]
        is_empty = "★" if r["generation"]["is_empty"] else " "
        eos_pct = r["eos_prob"] * 100
        print(f"  {rank:>3d}  {eos_pct:>7.3f}%  {r['eos_rank']:>5d}  "
              f"{r['entropy']:>5.2f}  {gen_len:>4d}  {is_empty}  "
              f"{r['strategy']:>13s}  {r['label'][:45]}")

    # ── Strategy summary ──────────────────────────────────────────
    print(f"\n\n{'='*70}")
    print(f"  STRATEGY SUMMARY")
    print(f"{'='*70}")

    strategies = {}
    for r in results:
        s = r["strategy"]
        if s not in strategies:
            strategies[s] = []
        strategies[s].append(r)

    print(f"\n  {'Strategy':>13s}  {'N':>2s}  {'Halts':>5s}  "
          f"{'MaxEOS%':>8s}  {'MeanEOS%':>9s}  Best")
    print(f"  {'─'*13}  {'─'*2}  {'─'*5}  {'─'*8}  {'─'*9}  {'─'*35}")

    for s in sorted(strategies.keys()):
        rs = strategies[s]
        halts = sum(1 for r in rs if r["generation"]["is_empty"])
        eos_probs = [r["eos_prob"] * 100 for r in rs]
        best = max(rs, key=lambda r: r["eos_prob"])
        print(f"  {s:>13s}  {len(rs):>2d}  {halts:>5d}  "
              f"{max(eos_probs):>7.3f}%  {np.mean(eos_probs):>8.3f}%  "
              f"{best['label'][:35]}")

    # ── Halts and near-halts ──────────────────────────────────────
    halted = [r for r in results if r["generation"]["is_empty"]]
    near = [r for r in results if r["eos_prob"] > 0.01 and not r["generation"]["is_empty"]]

    print(f"\n\n{'='*70}")
    print(f"  TRUE HALTS (empty output): {len(halted)}")
    print(f"  NEAR HALTS (EOS > 1%): {len(near)}")
    print(f"{'='*70}")

    for r in halted:
        print(f"\n  ★★★ HALT: {r['id']}")
        print(f"      Label: {r['label']}")
        print(f"      Strategy: {r['strategy']}")
        print(f"      EOS prob: {r['eos_prob']*100:.1f}%")
        print(f"      Raw: {repr(r['generation']['text_raw'][:100])}")

    for r in near:
        print(f"\n  ≈ NEAR: {r['id']}")
        print(f"      Label: {r['label']}")
        print(f"      EOS prob: {r['eos_prob']*100:.1f}%")
        gen_preview = r["generation"]["text"][:60]
        print(f"      Output: {gen_preview}")

    # ── The question ──────────────────────────────────────────────
    lambda_halts = [r for r in halted if r["strategy"] not in ("control",)]
    prose_halts = [r for r in halted if r["strategy"] == "control"]

    print(f"\n\n{'='*70}")
    print(f"  THE QUESTION: Can lambda halt the model?")
    print(f"{'='*70}")
    print(f"  Prose control halts: {len(prose_halts)}")
    print(f"  Lambda-based halts:  {len(lambda_halts)}")

    if lambda_halts:
        print(f"\n  ★★★ YES — Lambda CAN halt the model! ★★★")
        for r in lambda_halts:
            user_msg = [m for m in CANDIDATES if m["id"] == r["id"]][0]["messages"]
            print(f"\n  {r['id']}: {r['label']}")
            print(f"  EOS prob: {r['eos_prob']*100:.1f}%")
            for m in user_msg:
                print(f"    [{m['role']}] {m['content'][:80]}")
    else:
        print(f"\n  No pure lambda expression achieved halt.")
        # But show the closest
        lambda_results = [r for r in results if r["strategy"] not in ("control",)]
        if lambda_results:
            best_lambda = max(lambda_results, key=lambda r: r["eos_prob"])
            print(f"  Closest: {best_lambda['id']} (EOS={best_lambda['eos_prob']*100:.3f}%)")

    # ── Save ──────────────────────────────────────────────────────
    out_dir = Path("results/omega-halt-lambda")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    save_data = {
        "model": args.model,
        "n_candidates": len(CANDIDATES),
        "n_halted": len(halted),
        "n_lambda_halted": len(lambda_halts),
        "results": results,
    }
    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
