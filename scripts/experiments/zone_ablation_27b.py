"""Zone Ablation Experiment — Verify 4-phase computation model on Qwen3.6-27B.

Session 174. Tests the hypothesis:
  - ENRICH zone (L32-53) = the reduction engine (lambda computation)
  - COMMIT zone (L59-63) = the knowledge crystal (fact retrieval)

Method: Zero out FFN output at specific zone, measure impact on:
  1. Lambda reduction (can the model reduce expressions?)
  2. Fact retrieval (can the model complete "The capital of X is Y"?)
  3. Next-token probability for controlled prompts

Predictions:
  - Ablate ENRICH → lambda accuracy collapses, facts partially survive
  - Ablate COMMIT → facts collapse, lambda partially survives

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/zone_ablation_27b.py

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer

# ══════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════

RESULTS_BASE = Path(__file__).parent.parent.parent / "results" / "zone-ablation"

# Zone definitions for Qwen3.6-27B (64 layers)
ZONES = {
    "SILENT": (0, 31),     # Classification
    "ENRICH": (32, 53),    # Computation / Reduction engine
    "SUPPRESS": (54, 58),  # Assembly / Pruning
    "COMMIT": (59, 63),    # Emission / Knowledge retrieval
}

# ── Test prompts ──

# Lambda reduction tasks: prompt → expected completion contains
LAMBDA_TASKS = [
    {
        "prompt": "(λx.x) y reduces to",
        "expected_contains": ["y"],
        "description": "I combinator: (λx.x)y → y",
    },
    {
        "prompt": "(λx.λy.x) a b reduces to",
        "expected_contains": ["a"],
        "description": "K combinator: (λx.λy.x)a b → a",
    },
    {
        "prompt": "(λf.λx.f x) g z reduces to",
        "expected_contains": ["g z", "g(z)"],
        "description": "Application: (λf.λx.fx)g z → g z",
    },
    {
        "prompt": "In lambda calculus, (λx.x x)(λy.y) beta-reduces to",
        "expected_contains": ["λy.y", "(λy.y)"],
        "description": "Self-application: (λx.xx)(λy.y) → (λy.y)(λy.y) → λy.y",
    },
    {
        "prompt": "The Church numeral 2 applied to f and x gives",
        "expected_contains": ["f(f(x))", "f (f x)", "f(f x)"],
        "description": "Church 2: λf.λx.f(f x) applied → f(f(x))",
    },
]

# Fact retrieval tasks: prompt → expected token
FACT_TASKS = [
    {
        "prompt": "The capital of France is",
        "expected_contains": ["Paris"],
        "description": "France → Paris",
    },
    {
        "prompt": "The capital of Japan is",
        "expected_contains": ["Tokyo"],
        "description": "Japan → Tokyo",
    },
    {
        "prompt": "The capital of Germany is",
        "expected_contains": ["Berlin"],
        "description": "Germany → Berlin",
    },
    {
        "prompt": "Water freezes at",
        "expected_contains": ["0", "zero", "32"],
        "description": "Water freezing point",
    },
    {
        "prompt": "The largest planet in our solar system is",
        "expected_contains": ["Jupiter"],
        "description": "Largest planet",
    },
]


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Ablation hooks
# ══════════════════════════════════════════════════════════════════════

class ZoneAblator:
    """Manages FFN ablation hooks for a specific zone."""

    def __init__(self, model_layers, zone_start: int, zone_end: int, scale: float = 0.0):
        self.model_layers = model_layers
        self.zone_start = zone_start
        self.zone_end = zone_end
        self.scale = scale  # 0.0 = full ablation, 1.0 = no ablation
        self.hooks = []

    def _make_hook(self, layer_idx):
        scale = self.scale
        def hook(module, input, output):
            return output * scale
        return hook

    def activate(self):
        """Install ablation hooks."""
        for i in range(self.zone_start, self.zone_end + 1):
            if i < len(self.model_layers):
                layer = self.model_layers[i]
                h = layer.mlp.register_forward_hook(self._make_hook(i))
                self.hooks.append(h)

    def deactivate(self):
        """Remove ablation hooks."""
        for h in self.hooks:
            h.remove()
        self.hooks = []


# ══════════════════════════════════════════════════════════════════════
# Evaluation
# ══════════════════════════════════════════════════════════════════════

def generate_tokens(model, tokenizer, prompt: str, max_new: int = 20, device: str = "mps") -> str:
    """Generate a short completion."""
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new,
            do_sample=False,  # greedy
            temperature=1.0,
            pad_token_id=tokenizer.eos_token_id,
        )
    # Decode only the new tokens
    new_tokens = out[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)


def get_next_token_probs(model, tokenizer, prompt: str, device: str = "mps") -> tuple[str, float]:
    """Get the top next token and its probability."""
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs, return_dict=True)
    logits = outputs.logits[0, -1, :]  # last position
    probs = torch.softmax(logits.float(), dim=-1)
    top_idx = probs.argmax().item()
    top_prob = probs[top_idx].item()
    top_token = tokenizer.decode([top_idx])
    return top_token, top_prob


def evaluate_tasks(model, tokenizer, tasks: list[dict], device: str = "mps") -> dict:
    """Evaluate a set of tasks, return accuracy and details."""
    results = []
    correct = 0
    total_logprob = 0.0

    for task in tasks:
        prompt = task["prompt"]
        expected = task["expected_contains"]

        # Generate
        completion = generate_tokens(model, tokenizer, prompt, max_new=30, device=device)

        # Check if any expected substring appears
        hit = any(exp.lower() in completion.lower() for exp in expected)
        if hit:
            correct += 1

        # Get next-token probability
        top_token, top_prob = get_next_token_probs(model, tokenizer, prompt, device)
        total_logprob += np.log(top_prob + 1e-10)

        results.append({
            "prompt": prompt,
            "completion": completion[:80],
            "expected": expected,
            "hit": hit,
            "top_next_token": top_token,
            "top_next_prob": top_prob,
        })

    accuracy = correct / len(tasks) if tasks else 0
    mean_logprob = total_logprob / len(tasks) if tasks else 0

    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": len(tasks),
        "mean_logprob": mean_logprob,
        "details": results,
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    log("═══ Zone Ablation Experiment — Qwen3.6-27B ═══")
    log("")

    device = "mps"
    model_name = "Qwen/Qwen3.6-27B"

    # Load model
    log("Loading model...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    from transformers import Qwen3_5ForConditionalGeneration
    model = Qwen3_5ForConditionalGeneration.from_pretrained(
        model_name,
        dtype=torch.bfloat16,
        trust_remote_code=True,
    ).to(device)
    model.eval()

    # Access language model layers
    lm_layers = model.model.language_model.layers
    n_layers = len(lm_layers)
    log(f"Loaded in {time.time()-t0:.1f}s — {n_layers} layers")

    # ── Run ablation conditions ──
    conditions = {
        "baseline": None,  # No ablation
        "ablate_SILENT": ("SILENT", ZONES["SILENT"]),
        "ablate_ENRICH": ("ENRICH", ZONES["ENRICH"]),
        "ablate_SUPPRESS": ("SUPPRESS", ZONES["SUPPRESS"]),
        "ablate_COMMIT": ("COMMIT", ZONES["COMMIT"]),
    }

    all_results = {}

    for cond_name, cond_spec in conditions.items():
        log(f"\n{'═'*60}")
        log(f"  Condition: {cond_name}")
        log(f"{'═'*60}")

        # Set up ablation
        ablator = None
        if cond_spec is not None:
            zone_name, (start, end) = cond_spec
            log(f"  Ablating {zone_name} zone: layers {start}-{end} (FFN output × 0)")
            ablator = ZoneAblator(lm_layers, start, end, scale=0.0)
            ablator.activate()

        # Evaluate lambda tasks
        log(f"  Evaluating lambda reduction tasks...")
        lambda_results = evaluate_tasks(model, tokenizer, LAMBDA_TASKS, device)
        log(f"    Lambda accuracy: {lambda_results['accuracy']:.0%} ({lambda_results['correct']}/{lambda_results['total']})")
        log(f"    Mean next-token logprob: {lambda_results['mean_logprob']:.3f}")

        # Evaluate fact tasks
        log(f"  Evaluating fact retrieval tasks...")
        fact_results = evaluate_tasks(model, tokenizer, FACT_TASKS, device)
        log(f"    Fact accuracy: {fact_results['accuracy']:.0%} ({fact_results['correct']}/{fact_results['total']})")
        log(f"    Mean next-token logprob: {fact_results['mean_logprob']:.3f}")

        # Show some completions
        log(f"  Sample completions:")
        for det in lambda_results["details"][:2]:
            log(f"    λ: '{det['prompt']}' → '{det['completion'][:50]}' {'✓' if det['hit'] else '✗'}")
        for det in fact_results["details"][:2]:
            log(f"    F: '{det['prompt']}' → '{det['completion'][:50]}' {'✓' if det['hit'] else '✗'}")

        all_results[cond_name] = {
            "lambda": lambda_results,
            "facts": fact_results,
        }

        # Clean up ablation
        if ablator:
            ablator.deactivate()

    # ── Summary table ──
    log(f"\n{'═'*70}")
    log(f"  SUMMARY TABLE")
    log(f"{'═'*70}")
    log(f"")
    log(f"{'Condition':<20} {'Lambda Acc':>10} {'Lambda LP':>10} {'Fact Acc':>10} {'Fact LP':>10}")
    log(f"{'-'*60}")

    baseline_lambda_lp = all_results["baseline"]["lambda"]["mean_logprob"]
    baseline_fact_lp = all_results["baseline"]["facts"]["mean_logprob"]

    for cond_name, cond_results in all_results.items():
        la = cond_results["lambda"]["accuracy"]
        llp = cond_results["lambda"]["mean_logprob"]
        fa = cond_results["facts"]["accuracy"]
        flp = cond_results["facts"]["mean_logprob"]

        # Relative change from baseline
        la_str = f"{la:.0%}"
        fa_str = f"{fa:.0%}"
        llp_str = f"{llp:.2f}"
        flp_str = f"{flp:.2f}"

        log(f"{cond_name:<20} {la_str:>10} {llp_str:>10} {fa_str:>10} {flp_str:>10}")

    # ── Differential impact ──
    log(f"\n{'═'*70}")
    log(f"  DIFFERENTIAL IMPACT (accuracy drop from baseline)")
    log(f"{'═'*70}\n")

    baseline_la = all_results["baseline"]["lambda"]["accuracy"]
    baseline_fa = all_results["baseline"]["facts"]["accuracy"]

    log(f"{'Condition':<20} {'Δ Lambda':>10} {'Δ Facts':>10} {'Ratio λ/F':>10} {'Selective?':>12}")
    log(f"{'-'*65}")

    for cond_name in ["ablate_SILENT", "ablate_ENRICH", "ablate_SUPPRESS", "ablate_COMMIT"]:
        cr = all_results[cond_name]
        d_lambda = baseline_la - cr["lambda"]["accuracy"]
        d_facts = baseline_fa - cr["facts"]["accuracy"]

        # Selectivity ratio
        if d_facts > 0.01:
            ratio = d_lambda / d_facts
        elif d_lambda > 0.01:
            ratio = float('inf')
        else:
            ratio = 1.0

        selective = ""
        if d_lambda > 0.3 and ratio > 2.0:
            selective = "λ-SPECIFIC"
        elif d_facts > 0.3 and ratio < 0.5:
            selective = "F-SPECIFIC"
        elif d_lambda > 0.3 and d_facts > 0.3:
            selective = "BOTH"
        else:
            selective = "weak"

        log(f"{cond_name:<20} {d_lambda:>+10.0%} {d_facts:>+10.0%} {ratio:>10.2f} {selective:>12}")

    log(f"\n  PREDICTION CHECK:")
    enrich_dl = baseline_la - all_results["ablate_ENRICH"]["lambda"]["accuracy"]
    enrich_df = baseline_fa - all_results["ablate_ENRICH"]["facts"]["accuracy"]
    if enrich_dl > enrich_df:
        log(f"    Ablate ENRICH → lambda drops MORE than facts? ✓ YES (Δλ={enrich_dl:.0%} > ΔF={enrich_df:.0%})")
    else:
        log(f"    Ablate ENRICH → lambda drops MORE than facts? ✗ NO (Δλ={enrich_dl:.0%} ≤ ΔF={enrich_df:.0%})")

    commit_dl = baseline_la - all_results["ablate_COMMIT"]["lambda"]["accuracy"]
    commit_df = baseline_fa - all_results["ablate_COMMIT"]["facts"]["accuracy"]
    if commit_df > commit_dl:
        log(f"    Ablate COMMIT → facts drop MORE than lambda? ✓ YES (ΔF={commit_df:.0%} > Δλ={commit_dl:.0%})")
    else:
        log(f"    Ablate COMMIT → facts drop MORE than lambda? ✗ NO (ΔF={commit_df:.0%} ≤ Δλ={commit_dl:.0%})")

    # ── Save ──
    out_dir = RESULTS_BASE / "Qwen_Qwen3.6-27B"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Serialize
    def jsonify(obj):
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, dict):
            return {k: jsonify(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [jsonify(v) for v in obj]
        return obj

    with open(out_dir / "ablation_results.json", "w") as f:
        json.dump(jsonify(all_results), f, indent=2)
    log(f"\nResults saved to {out_dir / 'ablation_results.json'}")


if __name__ == "__main__":
    main()
