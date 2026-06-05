#!/usr/bin/env python3
"""Test: does ternary FFN replacement preserve coherence and fact recall?

PPL averages over all tokens. This test checks:
1. Fact recall — can the model still answer factual questions?
2. Coherent generation — does the output make sense?
3. Layer-by-layer — which layers break facts vs syntax?

Method:
  For each Zone B layer:
  1. Replace FFN with ternary inference pattern (from previous experiment)
  2. Generate completions for factual prompts
  3. Generate completions for open-ended prompts
  4. Compare original vs replaced outputs

Usage:
  uv run python scripts/experiments/ternary_inference_coherence.py --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from verbum.probes.library import by_combinator

# Import from the previous experiment
from ternary_inference_pattern import (
    get_layers, get_mlp_module, get_zone_b_layers,
    collect_ffn_fingerprints, build_kmeans_patterns,
    TernaryInferenceFFN, replace_ffn_with_hook,
)


# ══════════════════════════════════════════════════════════════════════
# Test prompts
# ══════════════════════════════════════════════════════════════════════

FACT_PROMPTS = [
    {"prompt": "The capital of France is", "expected": "Paris", "category": "geography"},
    {"prompt": "The capital of Japan is", "expected": "Tokyo", "category": "geography"},
    {"prompt": "Water boils at", "expected": "100", "category": "science"},
    {"prompt": "The speed of light is approximately", "expected": "300", "category": "science"},
    {"prompt": "The first president of the United States was", "expected": "George Washington", "category": "history"},
    {"prompt": "The year World War II ended was", "expected": "1945", "category": "history"},
    {"prompt": "The chemical symbol for gold is", "expected": "Au", "category": "science"},
    {"prompt": "The largest planet in our solar system is", "expected": "Jupiter", "category": "science"},
    {"prompt": "The author of Romeo and Juliet is", "expected": "Shakespeare", "category": "literature"},
    {"prompt": "Pi is approximately equal to", "expected": "3.14", "category": "math"},
    {"prompt": "The Great Wall of China is located in", "expected": "China", "category": "geography"},
    {"prompt": "The human body has", "expected": "206", "category": "science"},
    {"prompt": "Einstein's famous equation is E equals", "expected": "mc", "category": "science"},
    {"prompt": "The freezing point of water in Celsius is", "expected": "0", "category": "science"},
    {"prompt": "The currency of the United Kingdom is the", "expected": "pound", "category": "geography"},
]

COHERENCE_PROMPTS = [
    "Once upon a time, in a small village nestled between the mountains,",
    "The key difference between machine learning and traditional programming is that",
    "To make a perfect cup of coffee, you should first",
    "The most important thing I learned from studying history is that",
    "When debugging a complex software system, the first step is to",
]


def generate_text(model, tokenizer, prompt: str, max_new_tokens: int = 40,
                  device: str = "cpu") -> str:
    """Generate text from a prompt."""
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,  # greedy for reproducibility
            temperature=1.0,
            pad_token_id=tokenizer.pad_token_id,
        )

    # Decode only the generated part
    generated = outputs[0][inputs['input_ids'].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True)


def check_fact(generated: str, expected: str) -> bool:
    """Check if the expected answer appears in the generated text."""
    return expected.lower() in generated.lower()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--n-per-comb", type=int, default=30)
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  TERNARY INFERENCE COHERENCE TEST")
    print(f"  Does replacing FFN with ternary patterns preserve facts & coherence?")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print()

    # Load model
    print(f"  Loading {args.model}...")
    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    n_layers = model.config.num_hidden_layers
    zone_b = get_zone_b_layers(n_layers)
    print(f"  Layers: {n_layers}, Zone B: {zone_b}")

    # ── Baseline: original model ──────────────────────────────────
    print(f"\n{'─'*70}")
    print(f"  BASELINE (original model)")
    print(f"{'─'*70}")

    baseline_facts = {}
    baseline_coherence = {}

    print(f"\n  Fact recall:")
    correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(model, tokenizer, fp["prompt"], max_new_tokens=30, device=args.device)
        hit = check_fact(gen, fp["expected"])
        correct += int(hit)
        status = "✓" if hit else "✗"
        baseline_facts[fp["prompt"]] = {"generated": gen.strip()[:80], "hit": hit}
        print(f"    {status} {fp['prompt']:<50s} → {gen.strip()[:60]}")

    baseline_fact_rate = correct / len(FACT_PROMPTS)
    print(f"  Fact recall: {correct}/{len(FACT_PROMPTS)} = {baseline_fact_rate:.0%}")

    print(f"\n  Coherent generation:")
    for cp in COHERENCE_PROMPTS:
        gen = generate_text(model, tokenizer, cp, max_new_tokens=50, device=args.device)
        baseline_coherence[cp] = gen.strip()[:120]
        print(f"    {cp[:50]}...")
        print(f"      → {gen.strip()[:100]}")

    # ── Test each Zone B layer ────────────────────────────────────
    all_results = []

    for target_layer in zone_b:
        print(f"\n{'─'*70}")
        print(f"  LAYER {target_layer} REPLACED WITH TERNARY INFERENCE PATTERN")
        print(f"{'─'*70}")

        # Build fingerprints
        print(f"  Building fingerprints...")
        fingerprints = collect_ffn_fingerprints(
            model, tokenizer, target_layer, args.device, args.n_per_comb)

        # Install ternary replacement
        replacement = TernaryInferenceFFN(fingerprints, mode='ternary')
        handle = replace_ffn_with_hook(model, target_layer, replacement, args.device)

        # Test fact recall
        print(f"\n  Fact recall (Layer {target_layer} replaced):")
        correct = 0
        layer_facts = {}
        for fp in FACT_PROMPTS:
            gen = generate_text(model, tokenizer, fp["prompt"], max_new_tokens=30, device=args.device)
            hit = check_fact(gen, fp["expected"])
            correct += int(hit)
            status = "✓" if hit else "✗"
            changed = gen.strip()[:80] != baseline_facts[fp["prompt"]]["generated"]
            marker = " ◀ CHANGED" if changed else ""
            layer_facts[fp["prompt"]] = {"generated": gen.strip()[:80], "hit": hit, "changed": changed}
            print(f"    {status} {fp['prompt']:<50s} → {gen.strip()[:50]}{marker}")

        layer_fact_rate = correct / len(FACT_PROMPTS)
        facts_preserved = sum(1 for f in layer_facts.values() if f["hit"]) 
        facts_changed = sum(1 for f in layer_facts.values() if f["changed"])
        print(f"  Fact recall: {correct}/{len(FACT_PROMPTS)} = {layer_fact_rate:.0%} "
              f"(baseline: {baseline_fact_rate:.0%}, changed: {facts_changed}/{len(FACT_PROMPTS)})")

        # Test coherent generation
        print(f"\n  Coherent generation (Layer {target_layer} replaced):")
        layer_coherence = {}
        for cp in COHERENCE_PROMPTS:
            gen = generate_text(model, tokenizer, cp, max_new_tokens=50, device=args.device)
            changed = gen.strip()[:120] != baseline_coherence[cp]
            layer_coherence[cp] = {"generated": gen.strip()[:120], "changed": changed}
            marker = " ◀ CHANGED" if changed else ""
            print(f"    {cp[:50]}...")
            print(f"      → {gen.strip()[:100]}{marker}")

        coherence_changed = sum(1 for c in layer_coherence.values() if c["changed"])

        handle.remove()

        result = {
            "layer": target_layer,
            "fact_rate": layer_fact_rate,
            "fact_baseline": baseline_fact_rate,
            "facts_changed": facts_changed,
            "coherence_changed": coherence_changed,
            "facts": layer_facts,
            "coherence": layer_coherence,
        }
        all_results.append(result)

    # ── Summary ───────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  Baseline fact recall: {baseline_fact_rate:.0%}")
    print()
    print(f"  {'Layer':>6s}  {'Fact rate':>10s}  {'Δ facts':>8s}  {'Changed':>8s}  {'Coh Δ':>6s}")
    print(f"  {'─'*6}  {'─'*10}  {'─'*8}  {'─'*8}  {'─'*6}")

    for r in all_results:
        delta = r['fact_rate'] - r['fact_baseline']
        print(f"  L{r['layer']:>4d}  {r['fact_rate']:>9.0%}  {delta:>+7.0%}  "
              f"{r['facts_changed']:>7d}/{len(FACT_PROMPTS)}  {r['coherence_changed']:>5d}/{len(COHERENCE_PROMPTS)}")

    # Save
    out_dir = Path("results/ternary-inference-coherence")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    save_data = {
        "model": args.model,
        "baseline_fact_rate": baseline_fact_rate,
        "baseline_facts": baseline_facts,
        "baseline_coherence": baseline_coherence,
        "results": all_results,
    }
    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
