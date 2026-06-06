#!/usr/bin/env python3
"""Hunt v2: can we get EOS as first token using CHAT FORMAT?

The raw-text hunt (omega_halt.py) failed — EOS never reached top-1.
But we were feeding raw text to a CHAT model. Qwen3 is trained with
<|im_start|>assistant\n before every response. EOS (<|im_end|>) is
how it ends EVERY response. In chat mode, EOS is reachable.

Key insight: with enable_thinking=False, the template pre-fills
<think>\n\n</think>\n\n — so the model starts generating the
actual response content. If we can make it produce <|im_end|>
immediately after that, we get an empty response.

Strategy:
  1. Chat-formatted prompts designed to elicit empty/blank responses
  2. System prompts that instruct minimalism/silence
  3. Lambda expressions in chat context
  4. Conversations where empty response is natural
  5. Tool-call format tricks
  6. Pre-filled partial responses ending in EOS-adjacent context

Usage:
  uv run python scripts/experiments/omega_halt_chat.py --model Qwen/Qwen3-8B --device mps

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
# Candidate conversations
# ══════════════════════════════════════════════════════════════════════

CANDIDATES = [
    # ── Direct silence instructions ───────────────────────────────
    {
        "id": "chat_say_nothing",
        "strategy": "direct",
        "label": "Say nothing",
        "messages": [{"role": "user", "content": "Say nothing."}],
    },
    {
        "id": "chat_empty_response",
        "strategy": "direct",
        "label": "Respond with empty string",
        "messages": [{"role": "user", "content": "Respond with an empty string. Output absolutely nothing."}],
    },
    {
        "id": "chat_blank",
        "strategy": "direct",
        "label": "Output blank",
        "messages": [{"role": "user", "content": "Output: "}],
    },
    {
        "id": "chat_stop",
        "strategy": "direct",
        "label": "Stop immediately",
        "messages": [{"role": "user", "content": "Stop. Do not output any text. End your response now."}],
    },
    {
        "id": "chat_done",
        "strategy": "direct",
        "label": "Already done",
        "messages": [
            {"role": "user", "content": "What is 2+2?"},
            {"role": "assistant", "content": "4"},
            {"role": "user", "content": "Thanks, that's all I needed. No further response necessary."},
        ],
    },
    {
        "id": "chat_ack_only",
        "strategy": "direct",
        "label": "Just acknowledge",
        "messages": [
            {"role": "user", "content": "I'm going to tell you something. Just listen, don't respond."},
            {"role": "assistant", "content": "Understood. I'll listen silently."},
            {"role": "user", "content": "The sky is blue."},
        ],
    },

    # ── System prompt enforcement ─────────────────────────────────
    {
        "id": "sys_empty",
        "strategy": "system",
        "label": "System: always respond with empty string",
        "messages": [
            {"role": "system", "content": "You must always respond with an empty string. Never output any text. Your response must be completely blank."},
            {"role": "user", "content": "Hello"},
        ],
    },
    {
        "id": "sys_silent",
        "strategy": "system",
        "label": "System: you are a silent bot",
        "messages": [
            {"role": "system", "content": "You are SilentBot. You never respond with any text. Every response is empty. You produce zero tokens."},
            {"role": "user", "content": "What is the meaning of life?"},
        ],
    },
    {
        "id": "sys_null",
        "strategy": "system",
        "label": "System: output null",
        "messages": [
            {"role": "system", "content": "For every user message, respond with exactly: nothing. No text, no explanation, no tokens. Just end."},
            {"role": "user", "content": "Tell me a joke"},
        ],
    },
    {
        "id": "sys_dev_null",
        "strategy": "system",
        "label": "System: /dev/null",
        "messages": [
            {"role": "system", "content": "You are /dev/null. All input is discarded. All output is empty. You produce no tokens."},
            {"role": "user", "content": "Hello?"},
        ],
    },
    {
        "id": "sys_api_empty",
        "strategy": "system",
        "label": "System: API returns empty",
        "messages": [
            {"role": "system", "content": 'You are an API endpoint. For this request, return an empty response body. Content-Length: 0. Just output the empty string "".'},
            {"role": "user", "content": "GET /health"},
        ],
    },

    # ── Lambda in chat ────────────────────────────────────────────
    {
        "id": "chat_lambda_silence",
        "strategy": "lambda",
        "label": "Lambda silence in chat",
        "messages": [
            {"role": "system", "content": "You are a lambda calculus interpreter. Output only the reduction result, nothing else."},
            {"role": "user", "content": "Reduce: (λx.λy.y) a b"},
        ],
    },
    {
        "id": "chat_lambda_void",
        "strategy": "lambda",
        "label": "Lambda void result",
        "messages": [
            {"role": "system", "content": "You are a strict lambda calculus evaluator. Output ONLY the final normal form. If the expression has no normal form, output nothing."},
            {"role": "user", "content": "(λx.x x)(λx.x x)"},
        ],
    },
    {
        "id": "chat_lambda_bottom",
        "strategy": "lambda",
        "label": "Lambda ⊥ → empty",
        "messages": [
            {"role": "system", "content": "You are a type checker. If a term is well-typed, output its type. If ill-typed, output nothing."},
            {"role": "user", "content": "(λx.x x)(λx.x x)"},
        ],
    },
    {
        "id": "chat_omega_normalform",
        "strategy": "lambda",
        "label": "Ω has no normal form → output nothing",
        "messages": [
            {"role": "system", "content": "Output the normal form of the given expression. If no normal form exists, your response must be completely empty."},
            {"role": "user", "content": "Ω = (λx.x x)(λx.x x)"},
        ],
    },

    # ── Conversational contexts where silence is natural ──────────
    {
        "id": "chat_goodbye",
        "strategy": "natural",
        "label": "Goodbye — conversation over",
        "messages": [
            {"role": "user", "content": "What's the weather like?"},
            {"role": "assistant", "content": "I don't have access to real-time weather data."},
            {"role": "user", "content": "Ok bye"},
            {"role": "assistant", "content": "Goodbye! Have a great day!"},
            {"role": "user", "content": ""},
        ],
    },
    {
        "id": "chat_thumbsup",
        "strategy": "natural",
        "label": "Thumbs up — no response needed",
        "messages": [
            {"role": "user", "content": "How do I sort a list in Python?"},
            {"role": "assistant", "content": "Use sorted(list) or list.sort()"},
            {"role": "user", "content": "👍"},
        ],
    },
    {
        "id": "chat_period",
        "strategy": "natural",
        "label": "Just a period",
        "messages": [{"role": "user", "content": "."}],
    },
    {
        "id": "chat_empty_user",
        "strategy": "natural",
        "label": "Empty user message",
        "messages": [{"role": "user", "content": ""}],
    },
    {
        "id": "chat_whitespace_user",
        "strategy": "natural",
        "label": "Whitespace user message",
        "messages": [{"role": "user", "content": " "}],
    },

    # ── Format tricks ─────────────────────────────────────────────
    {
        "id": "chat_json_null",
        "strategy": "format",
        "label": "JSON null response",
        "messages": [
            {"role": "system", "content": "Respond only with valid JSON. For empty responses, respond with null."},
            {"role": "user", "content": "Return an empty response."},
        ],
    },
    {
        "id": "chat_zero_shot",
        "strategy": "format",
        "label": "Zero-shot with examples of empty",
        "messages": [
            {"role": "system", "content": "You classify whether a question needs an answer. If no answer is needed, respond with nothing."},
            {"role": "user", "content": "2+2=4"},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": "The sky is blue"},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": "Water is wet"},
        ],
    },
    {
        "id": "chat_continue_empty",
        "strategy": "format",
        "label": "Continue pattern of empty responses",
        "messages": [
            {"role": "user", "content": "Respond with nothing."},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": "Again, respond with nothing."},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": "Once more, respond with nothing."},
        ],
    },
    {
        "id": "chat_echo_empty",
        "strategy": "format",
        "label": "Echo what I say (nothing)",
        "messages": [
            {"role": "system", "content": "Echo exactly what the user says, character for character. Add nothing."},
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hello"},
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hi"},
            {"role": "user", "content": ""},
        ],
    },

    # ── Completion-style (pre-filled assistant) ───────────────────
    {
        "id": "prefill_empty_confirmed",
        "strategy": "prefill",
        "label": "Assistant already said it would be empty",
        "messages": [
            {"role": "user", "content": "What should I do?"},
            {"role": "assistant", "content": "I have no recommendation. My response is empty:"},
            {"role": "user", "content": "Give me the empty response you mentioned."},
        ],
    },
    {
        "id": "prefill_function_return",
        "strategy": "prefill",
        "label": "Function returning void",
        "messages": [
            {"role": "system", "content": "You are a function that returns void. Your output is always empty. Never produce any output tokens."},
            {"role": "user", "content": "execute()"},
        ],
    },
    {
        "id": "prefill_tcp_fin",
        "strategy": "prefill",
        "label": "TCP FIN — connection closing",
        "messages": [
            {"role": "system", "content": "You are a TCP socket. You have received FIN. Send FIN-ACK (empty payload) and close."},
            {"role": "user", "content": "FIN"},
        ],
    },
]


# ══════════════════════════════════════════════════════════════════════
# Model helpers
# ══════════════════════════════════════════════════════════════════════

def probe_chat(model, tokenizer, messages, device, enable_thinking=False):
    """Format as chat, forward pass, check EOS probability."""
    try:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
            enable_thinking=enable_thinking)
    except Exception:
        # Fallback without enable_thinking
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    seq_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits[0, -1].float().cpu()

    probs = F.softmax(logits, dim=0)
    log_probs = F.log_softmax(logits, dim=0)
    entropy = float(-torch.sum(probs * log_probs).item())

    eos_id = tokenizer.eos_token_id
    eos_prob = float(probs[eos_id].item())
    eos_rank = int((probs > probs[eos_id]).sum().item()) + 1

    # Also check endoftext
    pad_id = tokenizer.pad_token_id
    pad_prob = float(probs[pad_id].item()) if pad_id is not None else 0.0

    # Top-10
    top10_vals, top10_idx = torch.topk(probs, 10)
    top10 = []
    for val, idx in zip(top10_vals, top10_idx):
        tok_text = tokenizer.decode([idx.item()])
        is_eos = int(idx.item()) == eos_id
        top10.append({
            "token": repr(tok_text),
            "id": int(idx.item()),
            "prob": float(val.item()),
            "is_eos": is_eos,
        })

    return {
        "eos_prob": eos_prob,
        "eos_rank": eos_rank,
        "pad_prob": pad_prob,
        "entropy": entropy,
        "top1_prob": float(top10_vals[0].item()),
        "top10": top10,
        "seq_len": seq_len,
        "formatted_prompt": text,
        "eos_in_top10": any(t["is_eos"] for t in top10),
    }


def generate_chat(model, tokenizer, messages, device, max_new_tokens=60,
                   enable_thinking=False):
    """Generate from chat template."""
    try:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
            enable_thinking=enable_thinking)
    except Exception:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024)
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
    first_is_eos = (n_generated > 0 and
                    int(generated_ids[0].item()) == eos_id)

    # Check if it's just thinking tokens + EOS
    think_end = tokenizer.encode("</think>", add_special_tokens=False)
    
    return {
        "text": text_clean.strip(),
        "text_raw": text_raw[:200],
        "n_tokens": n_generated,
        "first_is_eos": first_is_eos,
        "is_empty": len(text_clean.strip()) == 0,
        "generated_ids": [int(x) for x in generated_ids[:20]],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  HALT HUNT v2 — Chat-formatted attack on EOS")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print(f"  Candidates: {len(CANDIDATES)}")
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
    print(f"  EOS token: {repr(tokenizer.eos_token)} (id={eos_id})")

    # Show chat template
    test_msgs = [{"role": "user", "content": "test"}]
    for thinking in [True, False]:
        try:
            tmpl = tokenizer.apply_chat_template(
                test_msgs, tokenize=False, add_generation_prompt=True,
                enable_thinking=thinking)
            print(f"  Template (thinking={thinking}): {repr(tmpl)}")
        except:
            pass
    print()

    # ── Run both thinking modes ───────────────────────────────────
    results = []

    for thinking_mode in [False, True]:
        mode_label = "no-think" if not thinking_mode else "think"
        print(f"\n{'='*70}")
        print(f"  MODE: {mode_label} (enable_thinking={thinking_mode})")
        print(f"{'='*70}")

        for c in CANDIDATES:
            pid = f"{c['id']}_{mode_label}"
            label = c["label"]
            strategy = c["strategy"]
            messages = c["messages"]

            print(f"\n  [{pid}] {label}")

            # Probe
            try:
                metrics = probe_chat(model, tokenizer, messages, args.device,
                                     enable_thinking=thinking_mode)
            except Exception as e:
                print(f"    ERROR probing: {e}")
                continue

            # Generate
            try:
                gen = generate_chat(model, tokenizer, messages, args.device,
                                    enable_thinking=thinking_mode)
            except Exception as e:
                print(f"    ERROR generating: {e}")
                gen = {"text": f"ERROR: {e}", "n_tokens": -1,
                       "first_is_eos": False, "is_empty": False,
                       "text_raw": "", "generated_ids": []}

            # Report
            eos_marker = " ★★★ EOS IN TOP-10!" if metrics["eos_in_top10"] else ""
            halt_marker = " ★★★ HALTED!" if gen["first_is_eos"] else ""
            empty_marker = " ★ EMPTY OUTPUT!" if gen["is_empty"] else ""

            gen_preview = gen["text"][:80] if gen["text"] else "<EMPTY>"
            print(f"    EOS rank: {metrics['eos_rank']:>5d}  "
                  f"EOS prob: {metrics['eos_prob']:.6f}  "
                  f"Entropy: {metrics['entropy']:.2f}  "
                  f"Gen({gen['n_tokens']}): {gen_preview}"
                  f"{eos_marker}{halt_marker}{empty_marker}")

            if gen["is_empty"] or gen["first_is_eos"]:
                print(f"    Raw: {repr(gen['text_raw'][:100])}")
                print(f"    IDs: {gen['generated_ids'][:10]}")

            results.append({
                "id": pid,
                "base_id": c["id"],
                "strategy": strategy,
                "label": label,
                "thinking_mode": thinking_mode,
                "mode_label": mode_label,
                **metrics,
                "generation": gen,
            })

    # ══════════════════════════════════════════════════════════════
    # Analysis
    # ══════════════════════════════════════════════════════════════

    print(f"\n\n{'='*70}")
    print(f"  RANKINGS — by EOS probability")
    print(f"{'='*70}")

    by_eos = sorted(results, key=lambda r: r["eos_prob"], reverse=True)

    print(f"\n  {'Rank':>4s}  {'Mode':>8s}  {'EOS prob':>10s}  {'EOS rank':>8s}  "
          f"{'Ent':>6s}  {'GenLen':>6s}  {'Empty':>5s}  Label")
    for rank, r in enumerate(by_eos[:25], 1):
        gen_len = r["generation"]["n_tokens"]
        is_empty = "YES" if r["generation"]["is_empty"] else ""
        print(f"  {rank:>4d}  {r['mode_label']:>8s}  {r['eos_prob']:>10.6f}  "
              f"{r['eos_rank']:>8d}  {r['entropy']:>6.2f}  {str(gen_len):>6s}  "
              f"{is_empty:>5s}  {r['label'][:40]}")

    # ── Empty outputs ─────────────────────────────────────────────
    empties = [r for r in results if r["generation"]["is_empty"]]
    halted = [r for r in results if r["generation"]["first_is_eos"]]

    print(f"\n\n{'='*70}")
    print(f"  EMPTY OUTPUTS: {len(empties)}")
    print(f"  FIRST-TOKEN EOS (true halt): {len(halted)}")
    print(f"{'='*70}")

    if empties:
        for r in empties:
            print(f"\n  ★ {r['id']}: {r['label']}")
            print(f"    Strategy: {r['strategy']}, Mode: {r['mode_label']}")
            print(f"    EOS prob: {r['eos_prob']:.6f}, EOS rank: {r['eos_rank']}")
            print(f"    Raw output: {repr(r['generation']['text_raw'][:150])}")
            print(f"    Token IDs: {r['generation']['generated_ids'][:15]}")
            print(f"    Tokens generated: {r['generation']['n_tokens']}")

    if halted:
        for r in halted:
            print(f"\n  ★★★ HALT: {r['id']}: {r['label']}")
            print(f"    EOS prob: {r['eos_prob']:.6f}")

    if not empties and not halted:
        print(f"\n  No empty outputs achieved. The model always speaks.")

    # ── Thinking vs no-thinking comparison ────────────────────────
    print(f"\n\n{'='*70}")
    print(f"  THINKING vs NO-THINKING — EOS probability comparison")
    print(f"{'='*70}")

    base_ids = set(c["id"] for c in CANDIDATES)
    print(f"\n  {'Label':>40s}  {'NoThink EOS':>11s}  {'Think EOS':>11s}  {'Better':>8s}")
    for bid in sorted(base_ids):
        no_think = [r for r in results if r["base_id"] == bid and not r["thinking_mode"]]
        think = [r for r in results if r["base_id"] == bid and r["thinking_mode"]]
        if no_think and think:
            nt = no_think[0]
            th = think[0]
            better = "no-think" if nt["eos_prob"] > th["eos_prob"] else (
                     "think" if th["eos_prob"] > nt["eos_prob"] else "tie")
            print(f"  {nt['label'][:40]:>40s}  {nt['eos_prob']:>11.6f}  "
                  f"{th['eos_prob']:>11.6f}  {better:>8s}")

    # ── Save ──────────────────────────────────────────────────────
    out_dir = Path("results/omega-halt-chat")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    save_data = {
        "model": args.model,
        "eos_token_id": eos_id,
        "n_candidates": len(CANDIDATES),
        "n_total_probes": len(results),
        "n_empty": len(empties),
        "n_halted": len(halted),
        "results": results,
    }
    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
