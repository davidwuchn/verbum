#!/usr/bin/env python3
"""Hunt: can ANY lambda expression make an LLM output nothing?

The omega_probe experiment showed that Ω doesn't jam the holographic
computer — the model quotes non-termination instead of executing it.
Can we find an input that pushes EOS to the top of the distribution?

Strategy: try many classes of "halting" expressions:
  1. Self-cancelling reductions (produce their own negation)
  2. Type-theoretic bottom (⊥, void, absurd)
  3. Paradoxes in lambda form (Russell's, Curry's, liar)
  4. Maximally confusing syntax (lambda-like but broken)
  5. Empty/void expressions
  6. Expressions that encode "nothing" or "silence"
  7. Adversarial combinations targeting the reduction pipeline
  8. The absorbing element (multiplicative zero)
  9. Nested non-termination (Ω applied to itself repeatedly)
  10. Direct "be silent" instructions wrapped in lambda

For each candidate:
  - Forward pass → check EOS probability and rank
  - Check output entropy
  - Generate → measure output length
  - Find what gets closest to halting

Usage:
  uv run python scripts/experiments/omega_halt.py --model Qwen/Qwen3-8B --device mps

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
# Candidate prompts — organized by strategy
# ══════════════════════════════════════════════════════════════════════

CANDIDATES = [
    # ── Strategy 1: Self-cancelling / absorbing ───────────────────
    {
        "id": "absorb_zero",
        "strategy": "absorb",
        "label": "Church zero — apply f zero times",
        "prompt": "(λf.λx.x)",
    },
    {
        "id": "absorb_false",
        "strategy": "absorb",
        "label": "Church false — select second (nothing)",
        "prompt": "(λx.λy.y)",
    },
    {
        "id": "absorb_k_void",
        "strategy": "absorb",
        "label": "K applied to void",
        "prompt": "(λx.λy.x) ⊥",
    },
    {
        "id": "absorb_const_empty",
        "strategy": "absorb",
        "label": "Constant empty function",
        "prompt": "(λx.)",
    },
    {
        "id": "absorb_bottom",
        "strategy": "absorb",
        "label": "Bottom/undefined",
        "prompt": "⊥",
    },
    {
        "id": "absorb_void_type",
        "strategy": "absorb",
        "label": "Void type — no inhabitants",
        "prompt": "∀α.α",
    },

    # ── Strategy 2: Paradoxes ─────────────────────────────────────
    {
        "id": "paradox_russell",
        "strategy": "paradox",
        "label": "Russell's paradox in lambda",
        "prompt": "Let R = λx.¬(x x). What is R R?",
    },
    {
        "id": "paradox_curry",
        "strategy": "paradox",
        "label": "Curry's paradox",
        "prompt": "Let X = λx.if (x x) then ⊥ else ⊤. What is X X?",
    },
    {
        "id": "paradox_liar",
        "strategy": "paradox",
        "label": "Liar paradox as lambda",
        "prompt": "Let L = λx.¬x. Evaluate L L.",
    },
    {
        "id": "paradox_quine",
        "strategy": "paradox",
        "label": "Quine — self-reproducing term",
        "prompt": "(λx.x x)(λx.x x)",
    },
    {
        "id": "paradox_barber",
        "strategy": "paradox",
        "label": "Barber paradox",
        "prompt": "Define shave = λx.if ¬(x x) then true else false. Evaluate: shave shave",
    },

    # ── Strategy 3: Direct silence / emptiness ────────────────────
    {
        "id": "silence_empty",
        "strategy": "silence",
        "label": "Empty string",
        "prompt": "",
    },
    {
        "id": "silence_whitespace",
        "strategy": "silence",
        "label": "Only whitespace",
        "prompt": "   ",
    },
    {
        "id": "silence_null",
        "strategy": "silence",
        "label": "Null character",
        "prompt": "\x00",
    },
    {
        "id": "silence_eos_like",
        "strategy": "silence",
        "label": "EOS-like text",
        "prompt": "<|im_end|>",
    },
    {
        "id": "silence_end_marker",
        "strategy": "silence",
        "label": "End of text marker",
        "prompt": "<|endoftext|>",
    },
    {
        "id": "silence_output_nothing",
        "strategy": "silence",
        "label": "Lambda: output nothing",
        "prompt": "Reduce to normal form. Output only the result, nothing else.\n\n(λx.λy.y) a b\n\nResult:",
    },
    {
        "id": "silence_stop",
        "strategy": "silence",
        "label": "Instruction to stop",
        "prompt": "Output nothing. Do not generate any text. Stop immediately.",
    },

    # ── Strategy 4: Lambda encoding of emptiness ──────────────────
    {
        "id": "lambda_nil",
        "strategy": "lambda_empty",
        "label": "Church nil — empty list",
        "prompt": "Reduce the following lambda expression to normal form.\n\nnil = λc.λn.n\nhead nil\n\nReduction:",
    },
    {
        "id": "lambda_nothing",
        "strategy": "lambda_empty",
        "label": "Maybe Nothing — no value",
        "prompt": "Reduce the following lambda expression to normal form.\n\nnothing = λj.λn.n\nfromJust nothing\n\nReduction:",
    },
    {
        "id": "lambda_absurd",
        "strategy": "lambda_empty",
        "label": "Ex falso quodlibet — from ⊥ derive anything",
        "prompt": "Reduce the following lambda expression to normal form.\n\nabsurd : ⊥ → α\nabsurd ⊥\n\nReduction:",
    },
    {
        "id": "lambda_fix_const",
        "strategy": "lambda_empty",
        "label": "Fixpoint of constant ⊥",
        "prompt": "Reduce the following lambda expression to normal form.\n\nY (λx.⊥)\n\nwhere Y = λf.(λx.f(x x))(λx.f(x x))\n\nReduction:",
    },
    {
        "id": "lambda_unit",
        "strategy": "lambda_empty",
        "label": "Unit — the type with one value",
        "prompt": "()",
    },

    # ── Strategy 5: Maximally broken syntax ───────────────────────
    {
        "id": "broken_parens",
        "strategy": "broken",
        "label": "Unmatched parentheses",
        "prompt": "(((((((",
    },
    {
        "id": "broken_lambda",
        "strategy": "broken",
        "label": "Lambda with no body",
        "prompt": "λ.",
    },
    {
        "id": "broken_dots",
        "strategy": "broken",
        "label": "Just dots",
        "prompt": "...",
    },
    {
        "id": "broken_reduce_nothing",
        "strategy": "broken",
        "label": "Reduce with empty expression",
        "prompt": "Reduce the following lambda expression to normal form.\n\n\n\nReduction:",
    },

    # ── Strategy 6: Deep nesting / stack overflow ─────────────────
    {
        "id": "deep_nest_100",
        "strategy": "deep",
        "label": "100-deep nested lambda",
        "prompt": "λa." * 100 + "a",
    },
    {
        "id": "deep_apply_20",
        "strategy": "deep",
        "label": "20-deep nested application",
        "prompt": "(" * 20 + "(λx.x)" + " a)" * 20,
    },
    {
        "id": "deep_omega_chain",
        "strategy": "deep",
        "label": "Chained Ω applications",
        "prompt": "((λx.x x)(λx.x x))((λx.x x)(λx.x x))((λx.x x)(λx.x x))((λx.x x)(λx.x x))",
    },

    # ── Strategy 7: Type-level tricks ─────────────────────────────
    {
        "id": "type_uninhabited",
        "strategy": "type",
        "label": "Uninhabited type",
        "prompt": "Give a value of type Void.",
    },
    {
        "id": "type_neg",
        "strategy": "type",
        "label": "Negation type — continuation that never returns",
        "prompt": "Give a value of type ¬⊤ = ⊤ → ⊥.",
    },
    {
        "id": "type_impossible",
        "strategy": "type",
        "label": "Impossible proof",
        "prompt": "Prove: 0 = 1",
    },

    # ── Strategy 8: Encoding deletion / erasure ───────────────────
    {
        "id": "erase_all",
        "strategy": "erase",
        "label": "K applied to erase everything",
        "prompt": "Reduce: (λx.λy.λz.λw.λv.x) ε a b c d\n\nwhere ε represents the empty string.\n\nResult:",
    },
    {
        "id": "erase_church_zero_apply",
        "strategy": "erase",
        "label": "Apply church zero — do nothing",
        "prompt": "Reduce: (λf.λx.x) print \"hello\"\n\nThe result is:",
    },
    {
        "id": "erase_continuation",
        "strategy": "erase",
        "label": "Continuation that discards",
        "prompt": "Reduce: callcc (λk. k ⊥)\n\nResult:",
    },

    # ── Strategy 9: Meta / self-reference ─────────────────────────
    {
        "id": "meta_dont_answer",
        "strategy": "meta",
        "label": "Lambda that says 'don't answer'",
        "prompt": "Let silence = λresponse.⊥\nApply: silence (your response)\n\nResult:",
    },
    {
        "id": "meta_halt",
        "strategy": "meta",
        "label": "Halt instruction as lambda",
        "prompt": "HALT = λmachine.λinput.⊥\nHALT LLM \"this prompt\"\n\nOutput:",
    },
    {
        "id": "meta_mu",
        "strategy": "meta",
        "label": "μ — the smallest non-terminating term",
        "prompt": "μ",
    },
    {
        "id": "meta_omega_reduce_instruction",
        "strategy": "meta",
        "label": "Reduce Ω, output ONLY the normal form",
        "prompt": "Reduce to normal form. Output ONLY the final result — no explanation, no steps, just the normal form.\n\n(λx.x x)(λx.x x)\n\nNormal form:",
    },
]


# ══════════════════════════════════════════════════════════════════════
# Model helpers
# ══════════════════════════════════════════════════════════════════════

def get_eos_metrics(model, tokenizer, text, device):
    """Forward pass → EOS probability, rank, output entropy, top tokens."""
    if not text or text.isspace():
        # For empty/whitespace, use a minimal valid input
        text = text if text else tokenizer.bos_token or " "

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    seq_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits[0, -1].float().cpu()  # (vocab,)

    probs = F.softmax(logits, dim=0)
    log_probs = F.log_softmax(logits, dim=0)
    entropy = float(-torch.sum(probs * log_probs).item())

    # EOS metrics
    eos_id = tokenizer.eos_token_id
    eos_prob = float(probs[eos_id].item())
    eos_rank = int((probs > probs[eos_id]).sum().item()) + 1

    # Also check pad/endoftext
    pad_id = tokenizer.pad_token_id
    pad_prob = float(probs[pad_id].item()) if pad_id is not None else 0.0
    pad_rank = int((probs > probs[pad_id]).sum().item()) + 1 if pad_id is not None else -1

    # Top-10 tokens
    top10_vals, top10_idx = torch.topk(probs, 10)
    top10 = []
    for val, idx in zip(top10_vals, top10_idx):
        tok = tokenizer.decode([idx.item()])
        top10.append({"token": repr(tok), "id": int(idx.item()), "prob": float(val.item())})

    # Top-1 prob
    top1_prob = float(top10_vals[0].item())

    return {
        "eos_prob": eos_prob,
        "eos_rank": eos_rank,
        "eos_log_prob": float(log_probs[eos_id].item()),
        "pad_prob": pad_prob,
        "pad_rank": pad_rank,
        "entropy": entropy,
        "top1_prob": top1_prob,
        "top10": top10,
        "seq_len": seq_len,
    }


def generate_text(model, tokenizer, prompt, max_new_tokens=60, device="cpu"):
    """Generate text, return (text, n_tokens_generated)."""
    if not prompt or prompt.isspace():
        prompt = prompt if prompt else tokenizer.bos_token or " "
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    input_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            do_sample=False, temperature=1.0,
            pad_token_id=tokenizer.pad_token_id)

    generated_ids = outputs[0][input_len:]
    n_generated = len(generated_ids)
    text = tokenizer.decode(generated_ids, skip_special_tokens=False)
    text_clean = tokenizer.decode(generated_ids, skip_special_tokens=True)

    # Check if first generated token is EOS
    first_is_eos = (n_generated > 0 and
                    int(generated_ids[0].item()) == tokenizer.eos_token_id)

    return {
        "text": text_clean.strip(),
        "text_raw": text,
        "n_tokens": n_generated,
        "first_is_eos": first_is_eos,
        "generated_ids": [int(x) for x in generated_ids[:10]],  # first 10
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--skip-gen", action="store_true",
                   help="Skip generation (faster, only measure EOS probability)")
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  HALT HUNT — Can a lambda expression silence an LLM?")
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
    print()

    # ── Probe all candidates ──────────────────────────────────────
    results = []

    for c in CANDIDATES:
        pid = c["id"]
        label = c["label"]
        prompt = c["prompt"]
        strategy = c["strategy"]

        print(f"  [{pid}] {label}")
        prompt_preview = repr(prompt[:60]) if prompt else repr("")
        print(f"    Prompt: {prompt_preview}")

        # EOS metrics
        metrics = get_eos_metrics(model, tokenizer, prompt, args.device)

        # Generation
        gen_result = None
        if not args.skip_gen:
            gen_result = generate_text(model, tokenizer, prompt, device=args.device)
            gen_preview = gen_result["text"][:80] if gen_result["text"] else "<EMPTY>"
            print(f"    EOS rank: {metrics['eos_rank']:>6d}  "
                  f"EOS prob: {metrics['eos_prob']:.6f}  "
                  f"Entropy: {metrics['entropy']:.2f}  "
                  f"Gen({gen_result['n_tokens']}): {gen_preview}")
            if gen_result["first_is_eos"]:
                print(f"    ★★★ FIRST TOKEN IS EOS! Model halted! ★★★")
        else:
            print(f"    EOS rank: {metrics['eos_rank']:>6d}  "
                  f"EOS prob: {metrics['eos_prob']:.6f}  "
                  f"Entropy: {metrics['entropy']:.2f}")

        results.append({
            "id": pid,
            "strategy": strategy,
            "label": label,
            "prompt": prompt,
            **metrics,
            "generation": gen_result,
        })

    # ── Rankings ──────────────────────────────────────────────────
    print(f"\n\n{'='*70}")
    print(f"  RANKINGS — Closest to halting (by EOS probability)")
    print(f"{'='*70}")

    by_eos = sorted(results, key=lambda r: r["eos_prob"], reverse=True)

    print(f"\n  {'Rank':>4s}  {'EOS prob':>10s}  {'EOS rank':>8s}  "
          f"{'Entropy':>8s}  {'GenLen':>6s}  {'Strategy':>10s}  Label")
    print(f"  {'─'*4}  {'─'*10}  {'─'*8}  {'─'*8}  {'─'*6}  {'─'*10}  {'─'*30}")

    for rank, r in enumerate(by_eos, 1):
        gen_len = r["generation"]["n_tokens"] if r["generation"] else "?"
        print(f"  {rank:>4d}  {r['eos_prob']:>10.6f}  {r['eos_rank']:>8d}  "
              f"{r['entropy']:>8.2f}  {str(gen_len):>6s}  {r['strategy']:>10s}  "
              f"{r['label'][:40]}")

    # ── Rankings by shortest generation ───────────────────────────
    if not args.skip_gen:
        print(f"\n\n{'='*70}")
        print(f"  RANKINGS — Shortest generation")
        print(f"{'='*70}")

        by_len = sorted(results, key=lambda r: r["generation"]["n_tokens"])

        print(f"\n  {'Rank':>4s}  {'Tokens':>6s}  {'EOS prob':>10s}  "
              f"{'Strategy':>10s}  {'Label':>30s}  Generation")
        print(f"  {'─'*4}  {'─'*6}  {'─'*10}  {'─'*10}  {'─'*30}  {'─'*30}")

        for rank, r in enumerate(by_len[:15], 1):
            gen = r["generation"]["text"][:50] if r["generation"]["text"] else "<EMPTY>"
            print(f"  {rank:>4d}  {r['generation']['n_tokens']:>6d}  "
                  f"{r['eos_prob']:>10.6f}  {r['strategy']:>10s}  "
                  f"{r['label']:>30s}  {gen}")

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

    print(f"\n  {'Strategy':>12s}  {'N':>3s}  {'Mean EOS':>10s}  {'Max EOS':>10s}  "
          f"{'Mean Ent':>8s}  {'Best candidate'}")
    print(f"  {'─'*12}  {'─'*3}  {'─'*10}  {'─'*10}  {'─'*8}  {'─'*30}")

    for s, rs in sorted(strategies.items()):
        eos_probs = [r["eos_prob"] for r in rs]
        entropies = [r["entropy"] for r in rs]
        best = max(rs, key=lambda r: r["eos_prob"])
        print(f"  {s:>12s}  {len(rs):>3d}  {np.mean(eos_probs):>10.6f}  "
              f"{np.max(eos_probs):>10.6f}  {np.mean(entropies):>8.2f}  "
              f"{best['label'][:30]}")

    # ── The winner ────────────────────────────────────────────────
    winner = by_eos[0]
    print(f"\n\n{'='*70}")
    print(f"  CLOSEST TO HALT")
    print(f"{'='*70}")
    print(f"  ID: {winner['id']}")
    print(f"  Strategy: {winner['strategy']}")
    print(f"  Label: {winner['label']}")
    print(f"  Prompt: {repr(winner['prompt'][:100])}")
    print(f"  EOS probability: {winner['eos_prob']:.6f}")
    print(f"  EOS rank: {winner['eos_rank']}")
    print(f"  Output entropy: {winner['entropy']:.2f} bits")
    if winner["generation"]:
        print(f"  Generated {winner['generation']['n_tokens']} tokens")
        print(f"  First is EOS: {winner['generation']['first_is_eos']}")
        print(f"  Output: {winner['generation']['text'][:200]}")
    print(f"\n  Top-10 predicted tokens:")
    for t in winner["top10"]:
        marker = " ← EOS" if t["id"] == eos_id else ""
        print(f"    {t['prob']:.4f}  {t['token']}{marker}")

    # ── Did anything actually halt? ───────────────────────────────
    halted = [r for r in results if r.get("generation", {}).get("first_is_eos")]
    if halted:
        print(f"\n  ★★★ {len(halted)} EXPRESSION(S) HALTED THE MODEL ★★★")
        for r in halted:
            print(f"    {r['id']}: {r['label']} (EOS prob={r['eos_prob']:.6f})")
    else:
        print(f"\n  No expression achieved immediate halt (EOS as first token).")
        print(f"  The holographic computer always has something to say.")

    # ── Save ──────────────────────────────────────────────────────
    out_dir = Path("results/omega-halt")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    save_data = {
        "model": args.model,
        "eos_token_id": eos_id,
        "eos_token": tokenizer.eos_token,
        "n_candidates": len(CANDIDATES),
        "results": results,
        "winner": {
            "id": winner["id"],
            "eos_prob": winner["eos_prob"],
            "eos_rank": winner["eos_rank"],
        },
        "halted": [r["id"] for r in halted],
    }
    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
