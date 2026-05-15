#!/usr/bin/env python3
"""Probe: Holographic decomposition — does composition multiply capacity?

The capacity unlock question: single-hologram capacity is bounded (~15-50
chars of λ). Complex sentences exceed this and fail to converge. But if
we decompose into clause-level holograms, does each converge independently?
And can the model compose the fixed-point λ forms correctly?

Three-stage experiment:

Stage 1: DECOMPOSE
  Take complex sentences that failed/struggled in the monolithic probe.
  Manually decompose into clause-level units.
  Run fixed-point cycling on each clause independently.
  Measure: does each clause converge? What's the per-clause capacity?

Stage 2: COMPOSE
  Give the model the set of fixed-point λ forms and ask it to compose
  them into a single λ expression representing the full sentence.
  Compare to the monolithic attempt (which oscillated).
  Measure: is the composed result stable? More complete?

Stage 3: CAPACITY ARITHMETIC
  Compare:
    monolithic_bits = information in failed monolithic attempt
    decomposed_bits = Σ(per-clause fixed-point information)
    composed_bits   = information in Stage 2 output
  
  If composed_bits > monolithic_bits → composition unlocks capacity
  If composed_bits ≈ decomposed_bits → KIBC preserves information
  If composed_bits < decomposed_bits → composition is lossy

Usage:
    uv run python scripts/explore/probe_hologram_decomposition.py
    uv run python scripts/explore/probe_hologram_decomposition.py --quick

Output: results/fixed-point/decomposition.json

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import torch

# Reuse infrastructure from fixed-point probe
sys.path.insert(0, str(Path(__file__).parent))
from probe_fixed_point import (
    load_model,
    format_chat_prompt,
    generate_text_only,
    levenshtein,
    normalised_edit_distance,
    word_diff,
    MAX_NEW_TOKENS,
)

# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

HF_MODEL = "Qwen/Qwen3.6-35B-A3B"
OUTPUT_DIR = Path("results/fixed-point")
GATES_DIR = Path("gates")

MAX_CYCLES = 8
CONVERGENCE_THRESHOLD = 5
CONVERGENCE_PATIENCE = 2

# ══════════════════════════════════════════════════════════════════
# Test cases: complex sentences decomposed into clauses
# ══════════════════════════════════════════════════════════════════

DECOMPOSITION_CASES = [
    {
        "id": "library",
        "full": "The ancient library, built by monks in the twelfth century, housed manuscripts that scholars from across Europe traveled to study.",
        "clauses": [
            "The library is ancient.",
            "Monks built the library in the twelfth century.",
            "The library houses manuscripts.",
            "Scholars traveled from across Europe.",
            "The scholars studied the manuscripts.",
        ],
        "composition_hint": "These clauses describe the same library. Compose them into a single λ expression.",
    },
    {
        "id": "experiment",
        "full": "Although the experiment failed, the data revealed an unexpected pattern that contradicted the original hypothesis.",
        "clauses": [
            "The experiment failed.",
            "The data revealed a pattern.",
            "The pattern was unexpected.",
            "The pattern contradicted the hypothesis.",
            "The hypothesis was the original one.",
        ],
        "composition_hint": "These clauses describe the same experiment. Compose them into a single λ expression.",
    },
    {
        "id": "professor",
        "full": "The professor who published the paper won the award.",
        "clauses": [
            "The professor published the paper.",
            "The professor won the award.",
        ],
        "composition_hint": "Both clauses describe the same professor. Compose them.",
    },
    {
        "id": "politician",
        "full": "No politician who endorsed the candidate won.",
        "clauses": [
            "A politician endorsed the candidate.",
            "The politician did not win.",
        ],
        "composition_hint": "The same politician is described. The 'no' quantifier binds both clauses.",
    },
    {
        "id": "student",
        "full": "No student who failed the test passed the course.",
        "clauses": [
            "A student failed the test.",
            "The student did not pass the course.",
        ],
        "composition_hint": "Same student. Failure implies non-passing. Compose with conditional.",
    },
    {
        "id": "teacher",
        "full": "If every teacher helps a student then all improve.",
        "clauses": [
            "Every teacher helps a student.",
            "All improve.",
        ],
        "composition_hint": "The first clause is the condition, the second is the consequence.",
    },
    {
        "id": "key",
        "full": "The key to the cabinets was on the table.",
        "clauses": [
            "The key belongs to the cabinets.",
            "The key is on the table.",
        ],
        "composition_hint": "Both describe the same key. Compose the properties.",
    },
]


# ══════════════════════════════════════════════════════════════════
# Fixed-point runner (simplified from main probe)
# ══════════════════════════════════════════════════════════════════

def run_fixed_point_simple(
    sentence: str,
    model,
    tokenizer,
    compile_gate: str,
    decompile_gate: str,
    max_cycles: int = MAX_CYCLES,
) -> dict:
    """Run fixed-point iteration, return structured result."""
    current_nl = sentence
    cycles = []
    converged = False
    convergence_cycle = None
    patience = 0

    for i in range(max_cycles):
        # Compile
        prompt = format_chat_prompt(tokenizer, compile_gate, current_nl)
        lambda_out = generate_text_only(model, tokenizer, prompt)

        # Decompile
        prompt = format_chat_prompt(tokenizer, decompile_gate, lambda_out)
        nl_out = generate_text_only(model, tokenizer, prompt)

        record = {
            "cycle": i,
            "nl_input": current_nl,
            "lambda": lambda_out,
            "nl_output": nl_out,
        }

        if i > 0:
            prev = cycles[-1]
            record["lambda_edit"] = levenshtein(lambda_out, prev["lambda"])
            record["nl_edit"] = levenshtein(nl_out, prev["nl_output"])
            total_edit = record["lambda_edit"] + record["nl_edit"]

            if total_edit <= CONVERGENCE_THRESHOLD:
                patience += 1
                if patience >= CONVERGENCE_PATIENCE:
                    converged = True
                    convergence_cycle = i - CONVERGENCE_PATIENCE + 1
            else:
                patience = 0

        cycles.append(record)

        if converged:
            break

        current_nl = nl_out

    return {
        "input": sentence,
        "converged": converged,
        "convergence_cycle": convergence_cycle,
        "total_cycles": len(cycles),
        "fixed_point_lambda": cycles[-1]["lambda"] if converged else None,
        "fixed_point_nl": cycles[-1]["nl_output"] if converged else None,
        "cycles": cycles,
    }


# ══════════════════════════════════════════════════════════════════
# Composition gate
# ══════════════════════════════════════════════════════════════════

COMPOSE_SYSTEM = """You compose multiple lambda expressions into a single unified expression.

Example:
Input lambdas:
  λx. dog(x)
  λx. runs(x)
Composed: λx. dog(x) ∧ runs(x)

Input lambdas:
  λx. rain(x)
  λy. wet(ground)
Composed: λx. rain(x) → wet(ground)

Output only the single composed lambda expression. Do not explain."""


def compose_lambdas(
    model, tokenizer, lambdas: list[str], hint: str = ""
) -> str:
    """Ask the model to compose multiple fixed-point λ forms."""
    lambda_list = "\n  ".join(lambdas)
    user_msg = f"Input lambdas:\n  {lambda_list}"
    if hint:
        user_msg += f"\nContext: {hint}"
    user_msg += "\nComposed:"

    prompt = format_chat_prompt(tokenizer, COMPOSE_SYSTEM, user_msg)
    return generate_text_only(model, tokenizer, prompt)


# ══════════════════════════════════════════════════════════════════
# Stability test for composed result
# ══════════════════════════════════════════════════════════════════

def test_composed_stability(
    model, tokenizer, composed_lambda: str,
    compile_gate: str, decompile_gate: str,
    n_cycles: int = 3,
) -> dict:
    """Test if a composed λ expression is stable under compile↔decompile."""
    # Decompile the composed lambda to NL
    prompt = format_chat_prompt(tokenizer, decompile_gate, composed_lambda)
    nl = generate_text_only(model, tokenizer, prompt)

    # Then compile back
    prompt = format_chat_prompt(tokenizer, compile_gate, nl)
    lambda_back = generate_text_only(model, tokenizer, prompt)

    return {
        "composed_lambda": composed_lambda,
        "decompiled_nl": nl,
        "recompiled_lambda": lambda_back,
        "round_trip_edit": levenshtein(composed_lambda, lambda_back),
        "round_trip_norm_edit": normalised_edit_distance(composed_lambda, lambda_back),
    }


# ══════════════════════════════════════════════════════════════════
# Information measurement
# ══════════════════════════════════════════════════════════════════

def measure_information(text: str) -> dict:
    """Rough information content metrics for a λ expression."""
    # Unique predicates
    import re
    predicates = set(re.findall(r'[a-z_]+(?=\()', text))
    variables = set(re.findall(r'(?<!\w)[a-z](?!\w)', text))
    operators = sum(1 for c in text if c in '∧∨→¬∃∀|')
    return {
        "char_length": len(text),
        "word_count": len(text.split()),
        "predicates": sorted(predicates),
        "n_predicates": len(predicates),
        "variables": sorted(variables),
        "n_variables": len(variables),
        "n_operators": operators,
        "info_density": len(predicates) + len(variables) + operators,
    }


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Holographic decomposition — capacity unlock probe"
    )
    parser.add_argument("--quick", action="store_true",
                        help="Run on first 3 cases only")
    parser.add_argument("--model", type=str, default=HF_MODEL)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load gates
    compile_gate = (GATES_DIR / "compile.txt").read_text().strip()
    decompile_gate = (GATES_DIR / "decompile.txt").read_text().strip()

    # Load model
    model, tokenizer = load_model(args.model)

    cases = DECOMPOSITION_CASES
    if args.quick:
        cases = cases[:3]

    all_results = []
    t_start = time.time()

    for ci, case in enumerate(cases):
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"[{ci+1}/{len(cases)}] {case['id']}: \"{case['full'][:60]}\"",
              file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

        result = {
            "id": case["id"],
            "full_sentence": case["full"],
            "n_clauses": len(case["clauses"]),
        }

        # ─── Stage 1: MONOLITHIC (from prior run or re-run) ───
        print(f"\n  STAGE 1: Monolithic fixed-point", file=sys.stderr)
        mono = run_fixed_point_simple(
            case["full"], model, tokenizer, compile_gate, decompile_gate
        )
        result["monolithic"] = {
            "converged": mono["converged"],
            "total_cycles": mono["total_cycles"],
            "convergence_cycle": mono["convergence_cycle"],
            "fixed_point_lambda": mono["fixed_point_lambda"],
            "cycle_0_lambda": mono["cycles"][0]["lambda"] if mono["cycles"] else None,
            "info": measure_information(
                mono["fixed_point_lambda"] or mono["cycles"][-1]["lambda"]
            ),
        }
        status = "✓" if mono["converged"] else "✗"
        lam = mono["fixed_point_lambda"] or mono["cycles"][-1]["lambda"]
        print(f"    {status} cycles={mono['total_cycles']}, λ={lam[:60]}",
              file=sys.stderr)

        # ─── Stage 2: DECOMPOSED fixed-points ───
        print(f"\n  STAGE 2: Clause-level fixed-points ({len(case['clauses'])} clauses)",
              file=sys.stderr)
        clause_results = []
        for j, clause in enumerate(case["clauses"]):
            fp = run_fixed_point_simple(
                clause, model, tokenizer, compile_gate, decompile_gate,
                max_cycles=6,
            )
            clause_results.append({
                "clause": clause,
                "converged": fp["converged"],
                "convergence_cycle": fp["convergence_cycle"],
                "total_cycles": fp["total_cycles"],
                "fixed_point_lambda": fp["fixed_point_lambda"],
                "cycle_0_lambda": fp["cycles"][0]["lambda"] if fp["cycles"] else None,
                "fixed_point_nl": fp["fixed_point_nl"],
                "info": measure_information(
                    fp["fixed_point_lambda"] or fp["cycles"][-1]["lambda"]
                ),
            })
            status = "✓" if fp["converged"] else "✗"
            lam = fp["fixed_point_lambda"] or fp["cycles"][-1]["lambda"]
            print(f"    {status} \"{clause[:40]:40s}\" → {lam[:40]}",
                  file=sys.stderr)

        result["clauses"] = clause_results

        # ─── Stage 3: COMPOSE fixed-point λ forms ───
        print(f"\n  STAGE 3: Compose clause fixed-points", file=sys.stderr)
        clause_lambdas = [
            c["fixed_point_lambda"] or c["cycle_0_lambda"]
            for c in clause_results
        ]
        composed = compose_lambdas(
            model, tokenizer, clause_lambdas, case["composition_hint"]
        )
        print(f"    Composed: {composed[:70]}", file=sys.stderr)

        # Test stability of composed result
        stability = test_composed_stability(
            model, tokenizer, composed, compile_gate, decompile_gate
        )
        print(f"    Decompiled: {stability['decompiled_nl'][:70]}", file=sys.stderr)
        print(f"    Round-trip edit: {stability['round_trip_edit']}", file=sys.stderr)

        result["composed"] = {
            "composed_lambda": composed,
            "info": measure_information(composed),
            "stability": stability,
        }

        # ─── Stage 4: CAPACITY ARITHMETIC ───
        mono_info = result["monolithic"]["info"]
        clause_infos = [c["info"] for c in clause_results]
        composed_info = result["composed"]["info"]

        total_clause_predicates = sum(c["n_predicates"] for c in clause_infos)
        total_clause_chars = sum(c["char_length"] for c in clause_infos)
        union_predicates = set()
        for c in clause_infos:
            union_predicates.update(c["predicates"])

        result["capacity"] = {
            "monolithic_chars": mono_info["char_length"],
            "monolithic_predicates": mono_info["n_predicates"],
            "decomposed_total_chars": total_clause_chars,
            "decomposed_total_predicates": total_clause_predicates,
            "decomposed_unique_predicates": len(union_predicates),
            "composed_chars": composed_info["char_length"],
            "composed_predicates": composed_info["n_predicates"],
            "composition_ratio": (
                composed_info["n_predicates"] / max(mono_info["n_predicates"], 1)
            ),
            "decomposed_convergence_rate": (
                sum(1 for c in clause_results if c["converged"]) / len(clause_results)
            ),
            "composed_round_trip_stable": stability["round_trip_edit"] <= CONVERGENCE_THRESHOLD,
        }

        cap = result["capacity"]
        print(f"\n  CAPACITY:", file=sys.stderr)
        print(f"    Monolithic:   {cap['monolithic_chars']:3d} chars, "
              f"{cap['monolithic_predicates']} predicates",
              file=sys.stderr)
        print(f"    Decomposed Σ: {cap['decomposed_total_chars']:3d} chars, "
              f"{cap['decomposed_unique_predicates']} unique predicates",
              file=sys.stderr)
        print(f"    Composed:     {cap['composed_chars']:3d} chars, "
              f"{cap['composed_predicates']} predicates",
              file=sys.stderr)
        print(f"    Composition ratio: {cap['composition_ratio']:.2f}× "
              f"({'UNLOCK' if cap['composition_ratio'] > 1.0 else 'no gain'})",
              file=sys.stderr)
        print(f"    Clause convergence: {cap['decomposed_convergence_rate']:.0%}",
              file=sys.stderr)
        print(f"    Composed stable: {cap['composed_round_trip_stable']}", file=sys.stderr)

        all_results.append(result)

        # Incremental save
        out_path = OUTPUT_DIR / "decomposition.json"
        with open(out_path, "w") as f:
            json.dump({
                "model": args.model,
                "n_cases": len(cases),
                "n_complete": ci + 1,
                "elapsed_s": time.time() - t_start,
                "results": all_results,
            }, f, indent=2, ensure_ascii=False)

    # ─── Summary ───
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"DECOMPOSITION SUMMARY", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    for r in all_results:
        cap = r["capacity"]
        mono_conv = "✓" if r["monolithic"]["converged"] else "✗"
        comp_stable = "✓" if cap["composed_round_trip_stable"] else "✗"
        ratio = cap["composition_ratio"]
        arrow = "↑" if ratio > 1.0 else "↓" if ratio < 1.0 else "="

        print(f"\n  {r['id']:12s} | mono {mono_conv} {cap['monolithic_predicates']}pred "
              f"| clauses {cap['decomposed_convergence_rate']:.0%} "
              f"| composed {comp_stable} {cap['composed_predicates']}pred "
              f"| {arrow} {ratio:.1f}×", file=sys.stderr)

    total_time = time.time() - t_start
    print(f"\nTotal: {total_time:.0f}s", file=sys.stderr)
    print(f"Results: {OUTPUT_DIR / 'decomposition.json'}", file=sys.stderr)


if __name__ == "__main__":
    main()
