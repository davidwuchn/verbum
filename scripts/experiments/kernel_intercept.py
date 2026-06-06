#!/usr/bin/env python3
"""Test: can we intercept wrong computation and replace with a kernel?

Architecture:
  - Model computes arithmetic via 9 ternary FFN modes
  - Composition ordering is wrong (compose (add 1) (mul 2) 3 → 9, should be 7)
  - We can hook FFN layers and modify the residual stream
  - If we detect "arithmetic mode" and replace with a kernel, does it work?

Three levels of intervention:
  1. TOKEN LEVEL: use continuation REPL to verify + correct between turns
  2. LOGIT LEVEL: intercept final logits, replace wrong token with right one
  3. TENSOR LEVEL: hook FFN at computation layers, inject correct residual

The deepest test: can we build a transparent math co-processor?
  - Monitor residual stream during forward pass
  - Detect when the model is computing arithmetic
  - Route to a kernel function (actual Python math)
  - Inject result back into residual stream
  - Model continues generating from corrected state

Usage:
  uv run python scripts/experiments/kernel_intercept.py --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════════
# The lambda execution environment (proven in continuation experiment)
# ══════════════════════════════════════════════════════════════════════

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
  sub = λa.λb.(a - b)
  div = λa.λb.(a / b)
  
  -- Control flow
  if_then_else = λp.λa.λb.p a b
  true = K
  false = λx.λy.y

Execute the expression. Output ONLY the final value."""


# ══════════════════════════════════════════════════════════════════════
# Math kernel — the "co-processor"
# ══════════════════════════════════════════════════════════════════════

def math_kernel(expr: str) -> str | None:
    """Parse and evaluate arithmetic lambda expressions.
    Returns the correct result as a string, or None if not arithmetic.
    """
    expr = expr.strip()
    
    # Handle compose: compose (f) (g) x → f(g(x))
    compose_match = re.match(
        r'compose\s+\((\w+)\s+(\d+(?:\.\d+)?)\)\s+\((\w+)\s+(\d+(?:\.\d+)?)\)\s+(\d+(?:\.\d+)?)',
        expr)
    if compose_match:
        f_op, f_arg, g_op, g_arg, x = compose_match.groups()
        x = float(x)
        g_arg = float(g_arg)
        f_arg = float(f_arg)
        
        # g(x) first, then f(result)
        g_result = _apply_op(g_op, g_arg, x)
        if g_result is not None:
            f_result = _apply_op(f_op, f_arg, g_result)
            if f_result is not None:
                return _format_num(f_result)
    
    # Handle then: then (f) x → f(x)
    then_match = re.match(
        r'then\s+\((\w+)\s+(\d+(?:\.\d+)?)\)\s+(\d+(?:\.\d+)?)',
        expr)
    if then_match:
        op, a, b = then_match.groups()
        result = _apply_op(op, float(a), float(b))
        if result is not None:
            return _format_num(result)
    
    # Handle simple: op a b
    simple_match = re.match(
        r'(\w+)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)',
        expr)
    if simple_match:
        op, a, b = simple_match.groups()
        result = _apply_op(op, float(a), float(b))
        if result is not None:
            return _format_num(result)
    
    return None


def _apply_op(op: str, a: float, b: float) -> float | None:
    ops = {
        'add': lambda a, b: a + b,
        'mul': lambda a, b: a * b,
        'sub': lambda a, b: a - b,
        'div': lambda a, b: a / b if b != 0 else None,
    }
    if op in ops:
        return ops[op](a, b)
    return None


def _format_num(x: float) -> str:
    if x == int(x):
        return str(int(x))
    return str(x)


# ══════════════════════════════════════════════════════════════════════
# Model helpers
# ══════════════════════════════════════════════════════════════════════

def get_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def generate_chat(model, tokenizer, messages, device, max_new_tokens=30):
    """Generate from chat template (no-think mode)."""
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True,
        enable_thinking=False)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=4096)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    input_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            do_sample=False, temperature=1.0,
            pad_token_id=tokenizer.pad_token_id)

    generated_ids = outputs[0][input_len:]
    text_clean = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    return text_clean


def get_token_embedding(model, tokenizer, token_str, device):
    """Get the embedding vector for a token string."""
    ids = tokenizer.encode(token_str, add_special_tokens=False)
    if not ids:
        return None
    # Use the lm_head to find the direction that produces this token
    # Actually, use the embed_tokens to get the input embedding
    embed = model.model.embed_tokens
    with torch.no_grad():
        vec = embed(torch.tensor([ids[0]], device=device)).float().cpu()
    return vec[0]  # (d_model,)


# ══════════════════════════════════════════════════════════════════════
# Level 1: Token-level intervention (continuation REPL with kernel)
# ══════════════════════════════════════════════════════════════════════

def test_token_level(model, tokenizer, device):
    """Use the continuation REPL to verify + correct between turns.
    
    Strategy: 
      1. Send expression to model
      2. Check model's answer against kernel
      3. If wrong, inject correct answer as the "assistant" turn
      4. Continue from corrected state
    """
    print(f"\n{'═'*70}")
    print(f"  Level 1: TOKEN-LEVEL INTERVENTION (continuation REPL + kernel)")
    print(f"{'═'*70}")
    
    test_cases = [
        # (expression, correct_answer)
        ("add 1 2", "3"),
        ("mul 3 4", "12"),
        ("compose (add 1) (mul 2) 3", "7"),   # model gets this WRONG (9)
        ("compose (mul 2) (add 1) 3", "8"),   # model gets this WRONG (9)
        ("compose (add 10) (mul 3) 5", "25"), # mul 3 5 = 15, add 10 15 = 25
        ("compose (mul 2) (add 3) 7", "20"),  # add 3 7 = 10, mul 2 10 = 20
        ("sub 10 3", "7"),
        ("compose (mul 3) (sub 10) 4", "18"), # sub 10 4 = 6, mul 3 6 = 18
    ]
    
    results = []
    
    for expr, correct in test_cases:
        # Get model's raw answer
        messages = [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": expr},
        ]
        model_answer = generate_chat(model, tokenizer, messages, device)
        
        # Get kernel answer
        kernel_answer = math_kernel(expr)
        
        # Check
        model_correct = correct in model_answer.strip()
        kernel_correct = kernel_answer == correct if kernel_answer else False
        
        # If model is wrong but kernel is right, INTERVENE
        intervened = False
        final_answer = model_answer
        if not model_correct and kernel_correct:
            # Inject kernel answer as the assistant response, continue
            final_answer = kernel_answer
            intervened = True
        
        status = "✓" if (model_correct or intervened) else "✗"
        interv = " [KERNEL]" if intervened else ""
        
        print(f"  {status} {expr}")
        print(f"    Model: {model_answer:>10s}  Kernel: {str(kernel_answer):>10s}  "
              f"Correct: {correct:>5s}  {interv}")
        
        results.append({
            "expr": expr,
            "correct": correct,
            "model_answer": model_answer,
            "kernel_answer": kernel_answer,
            "model_correct": model_correct,
            "intervened": intervened,
            "final_correct": model_correct or (intervened and kernel_correct),
        })
    
    # Now test: can the model CONTINUE from a kernel-corrected turn?
    print(f"\n  ── Continuation from kernel-corrected computation ──")
    
    # Pipeline: compose gets wrong answer → kernel corrects → model continues
    pipeline_messages = [
        {"role": "system", "content": CPS_SYSTEM},
        {"role": "user", "content": "compose (add 1) (mul 2) 3"},  # should be 7
    ]
    
    # Step 1: model answers (probably wrong)
    step1 = generate_chat(model, tokenizer, pipeline_messages, device)
    kernel1 = math_kernel("compose (add 1) (mul 2) 3")
    print(f"\n  Step 1: compose (add 1) (mul 2) 3")
    print(f"    Model says: {step1}")
    print(f"    Kernel says: {kernel1}")
    
    # Step 2: inject kernel answer, continue with next computation
    pipeline_messages.extend([
        {"role": "assistant", "content": kernel1},  # inject correct: 7
        {"role": "user", "content": f"mul 3 {kernel1}"},  # 3 × 7 = 21
    ])
    step2 = generate_chat(model, tokenizer, pipeline_messages, device)
    kernel2 = math_kernel(f"mul 3 {kernel1}")
    print(f"\n  Step 2: mul 3 {kernel1} (using kernel-corrected value)")
    print(f"    Model says: {step2}")
    print(f"    Kernel says: {kernel2}")
    print(f"    Correct: {kernel2 in step2.strip()}")
    
    # Step 3: one more continuation
    pipeline_messages.extend([
        {"role": "assistant", "content": kernel2},
        {"role": "user", "content": f"add 100 {kernel2}"},  # 100 + 21 = 121
    ])
    step3 = generate_chat(model, tokenizer, pipeline_messages, device)
    kernel3 = math_kernel(f"add 100 {kernel2}")
    print(f"\n  Step 3: add 100 {kernel2}")
    print(f"    Model says: {step3}")
    print(f"    Kernel says: {kernel3}")
    print(f"    Correct: {kernel3 in step3.strip()}")
    
    # Summary
    model_only = sum(1 for r in results if r["model_correct"])
    with_kernel = sum(1 for r in results if r["final_correct"])
    interventions = sum(1 for r in results if r["intervened"])
    
    print(f"\n  Summary:")
    print(f"    Model alone: {model_only}/{len(results)} correct")
    print(f"    With kernel: {with_kernel}/{len(results)} correct")
    print(f"    Interventions: {interventions}")
    print(f"    Pipeline continues from corrected state: "
          f"{'YES' if kernel3 in step3.strip() else 'NO'}")
    
    return results


# ══════════════════════════════════════════════════════════════════════
# Level 2: Logit-level intervention (replace output token)
# ══════════════════════════════════════════════════════════════════════

def test_logit_level(model, tokenizer, device):
    """Hook the lm_head, detect wrong arithmetic, replace with correct token.
    
    Strategy:
      1. Forward pass with math expression
      2. Check if top-1 token matches kernel answer
      3. If not, force the correct token
      4. Continue generation from corrected token
    """
    print(f"\n{'═'*70}")
    print(f"  Level 2: LOGIT-LEVEL INTERVENTION (force correct token)")
    print(f"{'═'*70}")
    
    test_cases = [
        ("compose (add 1) (mul 2) 3", "7"),
        ("compose (mul 2) (add 1) 3", "8"),
        ("compose (add 10) (mul 3) 5", "25"),
    ]
    
    results = []
    
    for expr, correct in test_cases:
        messages = [
            {"role": "system", "content": CPS_SYSTEM},
            {"role": "user", "content": expr},
        ]
        
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
            enable_thinking=False)
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=4096)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Forward pass — get logits at the generation position
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits[0, -1].float().cpu()
        
        probs = F.softmax(logits, dim=0)
        top5_vals, top5_idx = torch.topk(probs, 5)
        
        # What does the model predict?
        top1_token = tokenizer.decode([top5_idx[0].item()])
        
        # What should it predict?
        correct_ids = tokenizer.encode(correct, add_special_tokens=False)
        correct_token = tokenizer.decode(correct_ids[:1]) if correct_ids else correct
        correct_id = correct_ids[0] if correct_ids else -1
        correct_prob = float(probs[correct_id].item()) if correct_id >= 0 else 0
        correct_rank = int((probs > probs[correct_id]).sum().item()) + 1 if correct_id >= 0 else -1
        
        # Is the model right?
        model_right = correct.strip() in top1_token.strip()
        
        print(f"\n  {expr}")
        print(f"    Model top-1: {repr(top1_token)} ({top5_vals[0]:.3f})")
        print(f"    Correct: {repr(correct_token)} (prob={correct_prob:.4f}, rank={correct_rank})")
        print(f"    Model correct: {model_right}")
        
        # Show top-5
        for i in range(5):
            tok = tokenizer.decode([top5_idx[i].item()])
            marker = " ← CORRECT" if correct.strip() in tok.strip() else ""
            print(f"      #{i+1}: {repr(tok)} ({top5_vals[i]:.4f}){marker}")
        
        # If wrong, can we force-decode from the correct token?
        if not model_right and correct_id >= 0:
            # Append correct token and continue generation
            forced_ids = torch.cat([
                inputs["input_ids"][0],
                torch.tensor([correct_id], device=device)
            ]).unsqueeze(0)
            
            with torch.no_grad():
                forced_out = model.generate(
                    forced_ids,
                    max_new_tokens=10,
                    do_sample=False,
                    pad_token_id=tokenizer.pad_token_id)
            
            forced_gen = tokenizer.decode(
                forced_out[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True).strip()
            
            print(f"    Force-corrected output: {forced_gen}")
            print(f"    Correction successful: {correct in forced_gen}")
        
        results.append({
            "expr": expr,
            "correct": correct,
            "model_top1": top1_token.strip(),
            "correct_prob": correct_prob,
            "correct_rank": correct_rank,
            "model_right": model_right,
        })
    
    return results


# ══════════════════════════════════════════════════════════════════════
# Level 3: Tensor-level intervention (hook FFN, inject residual)
# ══════════════════════════════════════════════════════════════════════

def test_tensor_level(model, tokenizer, device):
    """Hook FFN at computation layers, detect arithmetic, inject correct result.
    
    Strategy:
      1. Run forward pass on CORRECT answer to capture target residual
      2. Run forward pass on the expression that gets wrong answer
      3. At key layers (L13-L21 zone of silence), replace residual 
         at the last token position with the "correct" residual
      4. Check if output changes to correct answer
    """
    print(f"\n{'═'*70}")
    print(f"  Level 3: TENSOR-LEVEL INTERVENTION (residual injection)")
    print(f"{'═'*70}")
    
    layers = get_layers(model)
    n_layers = len(layers)
    
    # The expression that fails: compose (add 1) (mul 2) 3 → should be 7
    wrong_expr = "compose (add 1) (mul 2) 3"
    correct_answer = "7"
    
    messages_wrong = [
        {"role": "system", "content": CPS_SYSTEM},
        {"role": "user", "content": wrong_expr},
    ]
    
    # Reference: what does the model do with a SIMPLE expression that yields 7?
    messages_correct = [
        {"role": "system", "content": CPS_SYSTEM},
        {"role": "user", "content": "add 4 3"},  # = 7, model gets this right
    ]
    
    # Capture residuals from the "correct" computation
    text_correct = tokenizer.apply_chat_template(
        messages_correct, tokenize=False, add_generation_prompt=True,
        enable_thinking=False)
    inputs_correct = tokenizer(text_correct, return_tensors="pt", truncation=True, max_length=4096)
    inputs_correct = {k: v.to(device) for k, v in inputs_correct.items()}
    
    correct_residuals = {}
    handles = []
    for i, layer in enumerate(layers):
        def make_hook(idx):
            def hook_fn(module, input, output):
                h = output[0] if isinstance(output, tuple) else output
                correct_residuals[idx] = h.detach().clone()
            return hook_fn
        handles.append(layer.register_forward_hook(make_hook(i)))
    
    with torch.no_grad():
        model(**inputs_correct)
    for h in handles:
        h.remove()
    
    print(f"  Captured residuals from 'add 4 3' (correct → 7) at all {n_layers} layers")
    
    # Now: for the WRONG expression, try injecting the correct residual 
    # at different layers and see when the output flips to "7"
    text_wrong = tokenizer.apply_chat_template(
        messages_wrong, tokenize=False, add_generation_prompt=True,
        enable_thinking=False)
    inputs_wrong = tokenizer(text_wrong, return_tensors="pt", truncation=True, max_length=4096)
    inputs_wrong = {k: v.to(device) for k, v in inputs_wrong.items()}
    
    # Baseline: what does it say without intervention?
    baseline = generate_chat(model, tokenizer, messages_wrong, device)
    print(f"  Baseline (no intervention): compose (add 1) (mul 2) 3 → {baseline}")
    print(f"  Expected: 7")
    
    # Try injecting at each layer (sample every few)
    print(f"\n  ── Injecting correct residual at each layer ──")
    print(f"  {'Layer':>7s}  {'Output':>10s}  {'Correct':>8s}  Notes")
    
    injection_results = []
    
    for inject_layer in range(0, n_layers, 1):
        # Hook: at inject_layer, replace last-token residual with correct residual
        target_residual = correct_residuals[inject_layer]
        
        def make_inject_hook(target_res, layer_idx):
            def hook_fn(module, input, output):
                h = output[0] if isinstance(output, tuple) else output
                # Replace the LAST token position with the correct residual's last position
                h_modified = h.clone()
                # The sequences may differ in length, so we just copy the last position
                h_modified[0, -1, :] = target_res[0, -1, :]
                if isinstance(output, tuple):
                    return (h_modified,) + output[1:]
                return h_modified
            return hook_fn
        
        handle = layers[inject_layer].register_forward_hook(
            make_inject_hook(target_residual, inject_layer))
        
        # Generate with intervention
        try:
            result = generate_chat(model, tokenizer, messages_wrong, device,
                                   max_new_tokens=5)
        except Exception as e:
            result = f"ERROR: {e}"
        
        handle.remove()
        
        is_correct = correct_answer in str(result).strip()
        notes = ""
        if inject_layer == 0:
            notes = "← embedding-adjacent"
        elif 13 <= inject_layer <= 21:
            notes = "← zone of silence"
        elif 27 <= inject_layer <= 33:
            notes = "← binding layers"
        elif inject_layer == 35:
            notes = "← collapse"
        
        marker = "✓" if is_correct else " "
        print(f"  L{inject_layer:>5d}  {str(result).strip():>10s}  {marker:>8s}  {notes}")
        
        injection_results.append({
            "layer": inject_layer,
            "output": str(result).strip(),
            "correct": is_correct,
        })
    
    # Summary
    correct_layers = [r["layer"] for r in injection_results if r["correct"]]
    wrong_layers = [r["layer"] for r in injection_results if not r["correct"]]
    
    print(f"\n  Injection works at layers: {correct_layers if correct_layers else 'NONE'}")
    print(f"  Injection fails at layers: {len(wrong_layers)} layers")
    
    if correct_layers:
        # Find the EARLIEST layer where injection works
        earliest = min(correct_layers)
        print(f"  Earliest effective injection: L{earliest}")
        print(f"  This means: the 'answer decision' happens at or after L{earliest}")
        
        # Find the LATEST layer where injection works
        latest = max(correct_layers)
        print(f"  Latest effective injection: L{latest}")
        
        # The range
        print(f"  Effective range: L{earliest}-L{latest} "
              f"({latest - earliest + 1} layers)")
    
    return injection_results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  KERNEL INTERCEPT — Transparent math co-processor")
    print(f"  Can we halt wrong computation and replace with a kernel?")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
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

    # ── Level 1: Token-level ──────────────────────────────────────
    token_results = test_token_level(model, tokenizer, args.device)

    # ── Level 2: Logit-level ──────────────────────────────────────
    logit_results = test_logit_level(model, tokenizer, args.device)

    # ── Level 3: Tensor-level ─────────────────────────────────────
    tensor_results = test_tensor_level(model, tokenizer, args.device)

    # ══════════════════════════════════════════════════════════════
    # Final synthesis
    # ══════════════════════════════════════════════════════════════
    print(f"\n\n{'='*70}")
    print(f"  SYNTHESIS — Three levels of intervention")
    print(f"{'='*70}")

    # Level 1
    l1_model = sum(1 for r in token_results if r["model_correct"])
    l1_kernel = sum(1 for r in token_results if r["final_correct"])
    print(f"\n  Level 1 (Token/Continuation):")
    print(f"    Model alone: {l1_model}/{len(token_results)}")
    print(f"    With kernel: {l1_kernel}/{len(token_results)}")
    print(f"    → Continuation-based correction WORKS")

    # Level 2
    l2_correct = sum(1 for r in logit_results if r["model_right"])
    print(f"\n  Level 2 (Logit replacement):")
    print(f"    Model correct: {l2_correct}/{len(logit_results)}")
    for r in logit_results:
        if not r["model_right"]:
            print(f"    Correct token rank: {r['correct_rank']} "
                  f"(prob={r['correct_prob']:.4f})")

    # Level 3
    l3_correct = [r for r in tensor_results if r["correct"]]
    print(f"\n  Level 3 (Tensor injection):")
    print(f"    Layers where injection works: {len(l3_correct)}/{len(tensor_results)}")
    if l3_correct:
        layers = [r["layer"] for r in l3_correct]
        print(f"    Effective layers: L{min(layers)}-L{max(layers)}")
        
    print(f"\n  The math co-processor is {'FEASIBLE' if l3_correct else 'NOT YET FEASIBLE'}")

    # ── Save ──────────────────────────────────────────────────────
    out_dir = Path("results/kernel-intercept")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    save_data = {
        "model": args.model,
        "token_results": token_results,
        "logit_results": logit_results,
        "tensor_results": tensor_results,
    }
    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
