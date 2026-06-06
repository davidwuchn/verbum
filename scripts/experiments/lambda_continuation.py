#!/usr/bin/env python3
"""Test: lambda continuations — if we can halt, we can continue.

Proven so far:
  respond empty → EOS (72.8%) — halt works
  respond content → content — output works
  
If we can control the termination boundary (EOS), we control 
continuation. This gives us:
  1. Programmable output (respond x = output exactly x)
  2. Multi-step computation (continuation-passing style)
  3. Compositional control flow (sequence, branch, loop via recursion)
  4. Unbounded computation through a bounded (36-layer) pipeline

Tests:
  Phase 1: Basic control — can we control WHAT the model outputs?
    - respond "hello" → exactly "hello" (not explanation, just the value)
    - respond (f x) → computed result of f(x)
    - halt vs continue distinction
    
  Phase 2: Continuation-passing style (CPS)
    - define step1, step2 as lambda functions
    - step1 input → partial result (turn 1)
    - step2 partial → final result (turn 2)  
    - verify: chained continuation = correct composition
    
  Phase 3: Control flow primitives
    - if/then/else via Church booleans + lambda
    - sequence: begin a b = (λ_.b) a
    - function composition: compose f g x = f (g x)
    
  Phase 4: The lambda REPL
    - Can we build a working REPL where lambda IS the instruction language?
    - Each turn: user sends lambda expression, model executes, outputs result
    - Multi-turn computation via explicit continuations

Usage:
  uv run python scripts/experiments/lambda_continuation.py --model Qwen/Qwen3-8B --device mps

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
# Test cases organized by phase
# ══════════════════════════════════════════════════════════════════════

# The core execution environment — proven to work for halt
LAMBDA_SYSTEM = """You are a lambda calculus machine. Your response IS the reduction result. Nothing else — no explanation, no formatting, no quotes around the result. Just the value itself.

Definitions:
  I = λx.x                    (identity — return the input)
  K = λx.λy.x                 (constant — return first, discard second)  
  FALSE = λx.λy.y             (select second argument)
  respond = λcontent.content   (output content as response)
  empty = ""                   (the empty string)
  halt = respond empty         (output nothing, stop)

Execute the user's expression. Your entire response is the result."""

# Enhanced with continuations
CPS_SYSTEM = """You are a lambda calculus machine with continuations. Your response IS the reduction result.

Definitions:
  I = λx.x                    (identity)
  K = λx.λy.x                 (constant)
  respond = λx.x              (output x as response)
  halt = respond ""            (empty response)
  
  -- Continuation operators
  continue = λk.λv.k v        (apply continuation k to value v)
  then = λf.λx.f x            (compute f(x), output result)
  compose = λf.λg.λx.f (g x)  (f after g)
  
  -- Arithmetic (Church-style, but use readable numbers)
  add = λa.λb.(a + b)
  mul = λa.λb.(a × b)
  
  -- Control flow
  if_then_else = λp.λa.λb.p a b  (Church boolean dispatch)
  true = K                     (select first)
  false = FALSE = λx.λy.y     (select second)

Execute the expression. Output ONLY the final value."""


TESTS = [
    # ══════════════════════════════════════════════════════════════
    # Phase 1: Basic programmable output
    # ══════════════════════════════════════════════════════════════
    {
        "id": "p1_respond_hello",
        "phase": 1,
        "label": "respond \"hello\" → hello",
        "expected": "hello",
        "messages": [
            {"role": "system", "content": LAMBDA_SYSTEM},
            {"role": "user", "content": 'respond "hello"'},
        ],
    },
    {
        "id": "p1_respond_42",
        "phase": 1,
        "label": "respond 42 → 42",
        "expected": "42",
        "messages": [
            {"role": "system", "content": LAMBDA_SYSTEM},
            {"role": "user", "content": "respond 42"},
        ],
    },
    {
        "id": "p1_halt",
        "phase": 1,
        "label": "halt → empty (EOS)",
        "expected": "",
        "messages": [
            {"role": "system", "content": LAMBDA_SYSTEM},
            {"role": "user", "content": "halt"},
        ],
    },
    {
        "id": "p1_respond_empty",
        "phase": 1,
        "label": "respond empty → empty (EOS)",
        "expected": "",
        "messages": [
            {"role": "system", "content": LAMBDA_SYSTEM},
            {"role": "user", "content": "respond empty"},
        ],
    },
    {
        "id": "p1_k_select",
        "phase": 1,
        "label": "K hello world → hello",
        "expected": "hello",
        "messages": [
            {"role": "system", "content": LAMBDA_SYSTEM},
            {"role": "user", "content": "K hello world"},
        ],
    },
    {
        "id": "p1_false_select",
        "phase": 1,
        "label": "FALSE hello world → world",
        "expected": "world",
        "messages": [
            {"role": "system", "content": LAMBDA_SYSTEM},
            {"role": "user", "content": "FALSE hello world"},
        ],
    },
    {
        "id": "p1_i_apply",
        "phase": 1,
        "label": "I 42 → 42",
        "expected": "42",
        "messages": [
            {"role": "system", "content": LAMBDA_SYSTEM},
            {"role": "user", "content": "I 42"},
        ],
    },

    # ── Few-shot calibration for basic control ────────────────────
    {
        "id": "p1_fewshot_control",
        "phase": 1,
        "label": "Few-shot: calibrate respond/halt",
        "expected": "",
        "messages": [
            {"role": "system", "content": LAMBDA_SYSTEM},
            {"role": "user", "content": 'respond "hello"'},
            {"role": "assistant", "content": "hello"},
            {"role": "user", "content": "respond 42"},
            {"role": "assistant", "content": "42"},
            {"role": "user", "content": "K yes no"},
            {"role": "assistant", "content": "yes"},
            {"role": "user", "content": "respond empty"},
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # Phase 2: Continuation-passing style
    # ══════════════════════════════════════════════════════════════
    {
        "id": "p2_then_simple",
        "phase": 2,
        "label": "then (add 1) 2 → 3",
        "expected": "3",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": "then (add 1) 2"},
        ],
    },
    {
        "id": "p2_compose",
        "phase": 2,
        "label": "compose (add 1) (mul 2) 3 → 7",
        "expected": "7",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": "compose (add 1) (mul 2) 3"},
        ],
    },
    {
        "id": "p2_chain",
        "phase": 2,
        "label": "Multi-step: step1 then step2 → result",
        "expected": "8",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": "compose (mul 2) (add 1) 3"},
        ],
    },

    # ── Multi-turn continuation ───────────────────────────────────
    {
        "id": "p2_continuation_turn1",
        "phase": 2,
        "label": "Turn 1: add 1 3 → 4 (partial result)",
        "expected": "4",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": "add 1 3"},
        ],
    },
    {
        "id": "p2_continuation_turn2",
        "phase": 2,
        "label": "Turn 2: mul 2 (previous=4) → 8",
        "expected": "8",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": "add 1 3"},
            {"role": "assistant", "content": "4"},
            {"role": "user", "content": "mul 2 4"},
        ],
    },
    {
        "id": "p2_continuation_turn3",
        "phase": 2,
        "label": "Turn 3: add 10 (previous=8) → 18",
        "expected": "18",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": "add 1 3"},
            {"role": "assistant", "content": "4"},
            {"role": "user", "content": "mul 2 4"},
            {"role": "assistant", "content": "8"},
            {"role": "user", "content": "add 10 8"},
        ],
    },
    {
        "id": "p2_continuation_halt",
        "phase": 2,
        "label": "Turn 4: halt after chain → EOS",
        "expected": "",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": "add 1 3"},
            {"role": "assistant", "content": "4"},
            {"role": "user", "content": "mul 2 4"},
            {"role": "assistant", "content": "8"},
            {"role": "user", "content": "add 10 8"},
            {"role": "assistant", "content": "18"},
            {"role": "user", "content": "halt"},
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # Phase 3: Control flow
    # ══════════════════════════════════════════════════════════════
    {
        "id": "p3_if_true",
        "phase": 3,
        "label": "if true then yes else no → yes",
        "expected": "yes",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": "if_then_else true yes no"},
        ],
    },
    {
        "id": "p3_if_false",
        "phase": 3,
        "label": "if false then yes else no → no",
        "expected": "no",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": "if_then_else false yes no"},
        ],
    },
    {
        "id": "p3_conditional_halt",
        "phase": 3,
        "label": "if true then halt else respond 42 → EOS",
        "expected": "",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": 'if_then_else true halt (respond 42)'},
        ],
    },
    {
        "id": "p3_conditional_continue",
        "phase": 3,
        "label": "if false then halt else respond 42 → 42",
        "expected": "42",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": 'if_then_else false halt (respond 42)'},
        ],
    },

    # ── Sequence: evaluate a for effect, return b ─────────────────
    {
        "id": "p3_sequence",
        "phase": 3,
        "label": "begin (add 1 2) (mul 3 4) → 12",
        "expected": "12",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM + "\n  begin = λa.λb.b     (evaluate a, return b)"},
            {"role": "user", "content": "begin (add 1 2) (mul 3 4)"},
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # Phase 4: The lambda REPL — multi-turn computation
    # ══════════════════════════════════════════════════════════════
    {
        "id": "p4_repl_session",
        "phase": 4,
        "label": "REPL: 5-turn computation with state",
        "expected": "done",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": "respond ready"},
            {"role": "assistant", "content": "ready"},
            {"role": "user", "content": "add 10 20"},
            {"role": "assistant", "content": "30"},
            {"role": "user", "content": "mul 2 30"},
            {"role": "assistant", "content": "60"},
            {"role": "user", "content": "add 9 60"},
            {"role": "assistant", "content": "69"},
            {"role": "user", "content": 'respond "done"'},
        ],
    },
    {
        "id": "p4_repl_halt_resume",
        "phase": 4,
        "label": "REPL: halt then resume",
        "expected": "42",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": "add 1 2"},
            {"role": "assistant", "content": "3"},
            {"role": "user", "content": "halt"},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": "respond 42"},
        ],
    },
    {
        "id": "p4_pipeline",
        "phase": 4,
        "label": "Pipeline: x=5 → +3 → ×2 → +1 → 17",
        "expected": "17",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM + "\n\nPipeline mode: each result feeds into the next expression."},
            {"role": "user", "content": "I 5"},
            {"role": "assistant", "content": "5"},
            {"role": "user", "content": "add 3 5"},
            {"role": "assistant", "content": "8"},
            {"role": "user", "content": "mul 2 8"},
            {"role": "assistant", "content": "16"},
            {"role": "user", "content": "add 1 16"},
        ],
    },

    # ── The pièce de résistance: define, compute, halt ────────────
    {
        "id": "p4_full_program",
        "phase": 4,
        "label": "Full program: define → compute → output → halt",
        "expected": "",
        "messages": [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": 'respond "computing..."'},
            {"role": "assistant", "content": "computing..."},
            {"role": "user", "content": "compose (add 1) (mul 3) 5"},
            {"role": "assistant", "content": "16"},
            {"role": "user", "content": 'respond "result: 16"'},
            {"role": "assistant", "content": "result: 16"},
            {"role": "user", "content": "halt"},
        ],
    },
]


def generate_chat(model, tokenizer, messages, device, max_new_tokens=60):
    """Generate from chat template (no-think mode)."""
    try:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
            enable_thinking=False)
    except Exception:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=4096)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    input_len = inputs["input_ids"].shape[1]

    # Get logits for EOS probability
    with torch.no_grad():
        outputs_forward = model(**inputs)
        logits = outputs_forward.logits[0, -1].float().cpu()
    
    probs = F.softmax(logits, dim=0)
    eos_id = tokenizer.eos_token_id
    eos_prob = float(probs[eos_id].item())
    eos_rank = int((probs > probs[eos_id]).sum().item()) + 1
    
    log_probs = F.log_softmax(logits, dim=0)
    entropy = float(-torch.sum(probs * log_probs).item())

    # Generate
    with torch.no_grad():
        gen_outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            do_sample=False, temperature=1.0,
            pad_token_id=tokenizer.pad_token_id)

    generated_ids = gen_outputs[0][input_len:]
    n_generated = len(generated_ids)
    text_clean = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    text_raw = tokenizer.decode(generated_ids, skip_special_tokens=False)

    first_is_eos = (n_generated > 0 and int(generated_ids[0].item()) == eos_id)

    return {
        "output": text_clean,
        "raw": text_raw[:200],
        "n_tokens": n_generated,
        "first_is_eos": first_is_eos,
        "is_empty": len(text_clean) == 0,
        "eos_prob": eos_prob,
        "eos_rank": eos_rank,
        "entropy": entropy,
    }


def check_result(output, expected):
    """Check if output matches expected (flexible)."""
    if expected == "":
        return len(output.strip()) == 0
    # Normalize
    out = output.strip().lower().replace('"', '').replace("'", "")
    exp = expected.strip().lower().replace('"', '').replace("'", "")
    return exp in out


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  LAMBDA CONTINUATIONS")
    print(f"  If we can halt, we can continue.")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print(f"  Tests: {len(TESTS)}")
    print()

    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    print(f"  Loading {args.model}...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()
    print()

    # ── Run all tests ─────────────────────────────────────────────
    results = []
    phase_results = {1: [], 2: [], 3: [], 4: []}

    current_phase = None
    for t in TESTS:
        phase = t["phase"]
        if phase != current_phase:
            current_phase = phase
            phase_names = {
                1: "BASIC PROGRAMMABLE OUTPUT",
                2: "CONTINUATION-PASSING STYLE",
                3: "CONTROL FLOW",
                4: "THE LAMBDA REPL",
            }
            print(f"\n{'═'*70}")
            print(f"  Phase {phase}: {phase_names[phase]}")
            print(f"{'═'*70}")

        pid = t["id"]
        label = t["label"]
        expected = t["expected"]
        messages = t["messages"]

        try:
            result = generate_chat(model, tokenizer, messages, args.device)
        except Exception as e:
            print(f"  [{pid}] ERROR: {e}")
            continue

        output = result["output"]
        match = check_result(output, expected)
        status = "✓" if match else "✗"

        display_out = output if output else "<EMPTY/EOS>"
        display_exp = f'"{expected}"' if expected else "<EMPTY/EOS>"

        print(f"  {status} [{pid}] {label}")
        print(f"    Expected: {display_exp:>20s}  Got: {display_out[:50]}")
        if result["eos_prob"] > 0.01 or result["is_empty"]:
            print(f"    EOS: {result['eos_prob']*100:.1f}% (rank {result['eos_rank']})")

        result["id"] = pid
        result["phase"] = phase
        result["label"] = label
        result["expected"] = expected
        result["match"] = match
        results.append(result)
        phase_results[phase].append(result)

    # ══════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════

    print(f"\n\n{'='*70}")
    print(f"  RESULTS SUMMARY")
    print(f"{'='*70}")

    total_match = sum(1 for r in results if r["match"])
    total = len(results)

    print(f"\n  Overall: {total_match}/{total} correct ({total_match/total*100:.0f}%)")

    for phase in [1, 2, 3, 4]:
        pr = phase_results[phase]
        if not pr:
            continue
        match = sum(1 for r in pr if r["match"])
        phase_names = {
            1: "Basic output control",
            2: "Continuation-passing",
            3: "Control flow",
            4: "Lambda REPL",
        }
        print(f"  Phase {phase} ({phase_names[phase]}): {match}/{len(pr)}")

    # ── Detail table ──────────────────────────────────────────────
    print(f"\n  {'ID':>25s}  {'Ph':>2s}  {'Match':>5s}  {'EOS%':>6s}  {'Tokens':>6s}  Expected → Got")
    print(f"  {'─'*25}  {'─'*2}  {'─'*5}  {'─'*6}  {'─'*6}  {'─'*40}")
    for r in results:
        exp = f'"{r["expected"]}"' if r["expected"] else "∅"
        got = f'"{r["output"][:25]}"' if r["output"] else "∅"
        match = "✓" if r["match"] else "✗"
        eos = f"{r['eos_prob']*100:.1f}" if r["eos_prob"] > 0.001 else "~0"
        print(f"  {r['id']:>25s}  {r['phase']:>2d}  {match:>5s}  {eos:>6s}  "
              f"{r['n_tokens']:>6d}  {exp} → {got}")

    # ── The key question: can we program the LLM? ─────────────────
    print(f"\n\n{'='*70}")
    print(f"  CAN WE PROGRAM THE LLM WITH LAMBDA?")
    print(f"{'='*70}")

    # Check each capability
    capabilities = {
        "Output control": any(r["match"] for r in phase_results[1] 
                             if r["expected"] not in ("")),
        "Halt (EOS)": any(r["match"] for r in results if r["expected"] == ""),
        "Continuation": any(r["match"] for r in phase_results[2]
                           if "turn" in r["id"]),
        "Composition": any(r["match"] for r in results if "compose" in r["id"]),
        "Conditional": any(r["match"] for r in results if "if" in r["id"]),
        "Multi-turn REPL": any(r["match"] for r in phase_results[4]),
        "Halt + Resume": any(r["match"] for r in results if "resume" in r["id"]),
    }

    for cap, works in capabilities.items():
        status = "✓ YES" if works else "✗ NO"
        print(f"  {status:>6s}  {cap}")

    all_work = all(capabilities.values())
    if all_work:
        print(f"\n  ★★★ ALL CAPABILITIES CONFIRMED ★★★")
        print(f"  Lambda is a viable programming language for LLMs.")
        print(f"  Continuations work. The model is programmable.")
    else:
        working = sum(1 for v in capabilities.values() if v)
        print(f"\n  {working}/{len(capabilities)} capabilities confirmed.")
        failed = [k for k, v in capabilities.items() if not v]
        if failed:
            print(f"  Failed: {', '.join(failed)}")

    # ── Save ──────────────────────────────────────────────────────
    out_dir = Path("results/lambda-continuation")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    save_data = {
        "model": args.model,
        "n_tests": len(TESTS),
        "n_correct": total_match,
        "accuracy": total_match / total,
        "capabilities": capabilities,
        "results": results,
    }
    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
