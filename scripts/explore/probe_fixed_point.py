#!/usr/bin/env python3
"""Probe: Fixed-point convergence of the compile↔decompile cycle.

Hypothesis: Iterating compile(NL→λ) then decompile(λ→NL) converges to a
fixed point — the natural language expression that perfectly maps to its
lambda encoding and back. This fixed point IS the hologram: the
representation the model's sign-pattern plate actually stores, with all
ambiguity/style stripped and all semantic content preserved.

The things that change in early cycles are what the hologram DOESN'T store.
The things stable from cycle 1 are what it stores most faithfully.

Protocol:
  1. Start with natural language sentence S₀
  2. Compile: S₀ → λ₀
  3. Decompile: λ₀ → S₁
  4. Compile: S₁ → λ₁
  5. Repeat until Sₙ ≈ Sₙ₋₁ AND λₙ ≈ λₙ₋₁ (fixed point)

Metrics per cycle:
  - Edit distance (Levenshtein) between consecutive NL and λ outputs
  - Embedding cosine similarity (last hidden state at last token)
  - Token-level diff (what specifically changed)
  - Lambda structural comparison (normalised form)

Cross-analysis:
  - Convergence rate vs input complexity
  - Residual classification (what changes between cycles)
  - Fixed-point quality (vs ground truth from compile-gradient.json)
  - Cross-model fixed points (future: do different models converge to same?)

Usage:
    uv run python scripts/explore/probe_fixed_point.py
    uv run python scripts/explore/probe_fixed_point.py --max-cycles 15
    uv run python scripts/explore/probe_fixed_point.py --quick

Output: results/fixed-point/

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
import numpy as np


# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

HF_MODEL = "Qwen/Qwen3.6-35B-A3B"
OUTPUT_DIR = Path("results/fixed-point")
GATES_DIR = Path("gates")

MAX_CYCLES = 10            # Maximum compile↔decompile iterations
CONVERGENCE_THRESHOLD = 5  # Levenshtein chars — below this = converged
CONVERGENCE_PATIENCE = 2   # Must be below threshold this many times in a row
MAX_NEW_TOKENS = 256       # Max generation length per step
TEMPERATURE = 0.0          # Greedy decoding for reproducibility

# Input sentences: mix of compile-gradient entries + interesting test cases
DEFAULT_INPUTS = [
    # Simple predication
    "The dog runs.",
    "The cat sat on the mat.",
    # Quantification
    "Every student passed the exam.",
    "Every boy loves some girl.",
    # Relative clauses (composition territory)
    "The man who the dog chased ran away.",
    "The professor who published the paper won the award.",
    # Conditionals
    "If every teacher helps a student then all improve.",
    "If it rains, the ground gets wet.",
    # Binding / coreference
    "John gave Mary a book about himself.",
    "No politician who endorsed the candidate won.",
    # Complex scope
    "No student who failed the test passed the course.",
    "The key to the cabinets was on the table.",
    # Lambda-adjacent
    "The function applies its argument to the result.",
    "Composition chains two operations into one.",
    # Discourse-level
    "The ancient library, built by monks in the twelfth century, housed manuscripts that scholars from across Europe traveled to study.",
    "Although the experiment failed, the data revealed an unexpected pattern that contradicted the original hypothesis.",
]


# ══════════════════════════════════════════════════════════════════
# Levenshtein distance (pure Python, fine for short strings)
# ══════════════════════════════════════════════════════════════════

def levenshtein(s1: str, s2: str) -> int:
    """Compute character-level Levenshtein edit distance."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            cost = 0 if c1 == c2 else 1
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = curr
    return prev[-1]


def normalised_edit_distance(s1: str, s2: str) -> float:
    """Edit distance normalised by max length. 0 = identical, 1 = totally different."""
    if not s1 and not s2:
        return 0.0
    return levenshtein(s1, s2) / max(len(s1), len(s2))


# ══════════════════════════════════════════════════════════════════
# Token-level diff
# ══════════════════════════════════════════════════════════════════

def word_diff(s1: str, s2: str) -> dict:
    """Compute word-level additions, removals, and changes."""
    w1 = s1.split()
    w2 = s2.split()
    set1 = set(w1)
    set2 = set(w2)
    return {
        "added": sorted(set2 - set1),
        "removed": sorted(set1 - set2),
        "shared": len(set1 & set2),
        "jaccard": len(set1 & set2) / max(len(set1 | set2), 1),
    }


# ══════════════════════════════════════════════════════════════════
# Lambda normalisation (light-touch, for structural comparison)
# ══════════════════════════════════════════════════════════════════

def normalise_lambda(lam: str) -> str:
    """Light normalisation: strip whitespace, lowercase variables, sort conjuncts."""
    s = lam.strip()
    # Normalise whitespace
    s = " ".join(s.split())
    return s


# ══════════════════════════════════════════════════════════════════
# Model loading + generation
# ══════════════════════════════════════════════════════════════════

def load_model(model_name: str = HF_MODEL):
    """Load model + tokenizer for generation and embedding extraction."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"Loading {model_name}...", file=sys.stderr, end="", flush=True)
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    t1 = time.time()

    n_layers = model.config.num_hidden_layers
    print(f" {t1-t0:.1f}s ({n_layers} layers)", file=sys.stderr)
    return model, tokenizer


def format_chat_prompt(tokenizer, gate_text: str, user_input: str) -> str:
    """Format a chat prompt using the model's chat template.

    The gates are few-shot exemplar pairs (e.g. "sentence → lambda").
    We place them in the system prompt as examples, and the user message
    is the actual input to transform. The gate's trailing "Input: " is
    stripped since we use structured chat instead.
    """
    # Strip trailing "Input: " or "Input:" if present (from completion-era gates)
    system = gate_text.strip()
    if system.endswith("Input:"):
        system = system[:-len("Input:")].strip()
    elif system.endswith("Input: "):
        system = system[:-len("Input: ")].strip()

    # Add instruction to only output the result (not echo input with arrow)
    system += "\n\nOutput only the result. Do not include the input or arrow notation."

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_input},
    ]
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,  # Qwen3.x: disable <think> tags
    )
    return prompt


@torch.no_grad()
def generate_with_embedding(
    model,
    tokenizer,
    prompt: str,
    max_new_tokens: int = MAX_NEW_TOKENS,
    temperature: float = TEMPERATURE,
) -> tuple[str, np.ndarray]:
    """Generate text and return (output_text, last_hidden_state_embedding).

    The embedding is the last hidden state at the final generated token,
    suitable for cosine similarity tracking across cycles.
    """
    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs["input_ids"].to(model.device)
    attention_mask = inputs["attention_mask"].to(model.device)
    prompt_len = input_ids.shape[1]

    # Generate (greedy, no sampling)
    # Explicitly clear all sampling params to suppress Qwen's default config warnings
    gen_config = model.generation_config
    gen_config.top_k = None
    gen_config.top_p = None
    gen_config.temperature = None
    outputs = model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
    )

    # Decode only the generated tokens
    gen_tokens = outputs[0, prompt_len:]
    text = tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

    # Get embedding from a forward pass on the completed sequence.
    # Use just the generated portion for efficiency — we care about
    # the model's representation of its own output.
    gen_ids = outputs[0:1]  # Keep batch dim
    fwd = model(gen_ids, output_hidden_states=True)
    # Last layer, last non-pad token
    last_hidden = fwd.hidden_states[-1][0, -1, :].float().cpu().numpy()

    return text, last_hidden


def generate_text_only(
    model,
    tokenizer,
    prompt: str,
    max_new_tokens: int = MAX_NEW_TOKENS,
) -> str:
    """Generate text without embedding extraction (faster for later cycles)."""
    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs["input_ids"].to(model.device)
    attention_mask = inputs["attention_mask"].to(model.device)
    prompt_len = input_ids.shape[1]

    gen_config = model.generation_config
    gen_config.top_k = None
    gen_config.top_p = None
    gen_config.temperature = None
    outputs = model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
    )

    gen_tokens = outputs[0, prompt_len:]
    return tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()


# ══════════════════════════════════════════════════════════════════
# Core: fixed-point iteration
# ══════════════════════════════════════════════════════════════════

@dataclass
class CycleRecord:
    """One compile→decompile cycle."""
    cycle: int
    nl_input: str           # Natural language going INTO compile
    lambda_output: str      # Lambda coming OUT of compile
    nl_output: str          # Natural language coming OUT of decompile

    # Metrics vs previous cycle
    nl_edit_dist: int = 0
    nl_norm_edit: float = 0.0
    lambda_edit_dist: int = 0
    lambda_norm_edit: float = 0.0
    nl_word_diff: dict = field(default_factory=dict)
    lambda_word_diff: dict = field(default_factory=dict)

    # Embedding cosine (compile output vs previous compile output)
    embedding_cosine: float = 1.0

    elapsed_s: float = 0.0

    def to_dict(self) -> dict:
        return {
            "cycle": self.cycle,
            "nl_input": self.nl_input,
            "lambda_output": self.lambda_output,
            "nl_output": self.nl_output,
            "nl_edit_dist": self.nl_edit_dist,
            "nl_norm_edit": self.nl_norm_edit,
            "lambda_edit_dist": self.lambda_edit_dist,
            "lambda_norm_edit": self.lambda_norm_edit,
            "nl_word_diff": self.nl_word_diff,
            "lambda_word_diff": self.lambda_word_diff,
            "embedding_cosine": self.embedding_cosine,
            "elapsed_s": self.elapsed_s,
        }


@dataclass
class FixedPointResult:
    """Full result for one input sentence."""
    input_sentence: str
    converged: bool
    convergence_cycle: int | None  # First cycle where convergence detected
    total_cycles: int
    fixed_point_nl: str | None     # The converged NL, if any
    fixed_point_lambda: str | None  # The converged lambda, if any
    cycles: list[CycleRecord] = field(default_factory=list)
    ground_truth_lambda: str | None = None  # From compile-gradient if available
    elapsed_total_s: float = 0.0

    def to_dict(self) -> dict:
        return {
            "input_sentence": self.input_sentence,
            "converged": self.converged,
            "convergence_cycle": self.convergence_cycle,
            "total_cycles": self.total_cycles,
            "fixed_point_nl": self.fixed_point_nl,
            "fixed_point_lambda": self.fixed_point_lambda,
            "ground_truth_lambda": self.ground_truth_lambda,
            "elapsed_total_s": self.elapsed_total_s,
            "cycles": [c.to_dict() for c in self.cycles],
        }


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def run_fixed_point(
    sentence: str,
    model,
    tokenizer,
    compile_gate: str,
    decompile_gate: str,
    *,
    max_cycles: int = MAX_CYCLES,
    convergence_threshold: int = CONVERGENCE_THRESHOLD,
    convergence_patience: int = CONVERGENCE_PATIENCE,
    extract_embeddings: bool = True,
    ground_truth_lambda: str | None = None,
) -> FixedPointResult:
    """Run the compile↔decompile fixed-point iteration for one sentence."""

    t_total_start = time.time()
    cycles: list[CycleRecord] = []
    converged = False
    convergence_cycle = None
    patience_count = 0

    current_nl = sentence
    prev_lambda = None
    prev_nl = None
    prev_compile_emb = None

    for cycle_idx in range(max_cycles):
        t_cycle = time.time()

        # ─── Compile: NL → λ ───
        compile_prompt = format_chat_prompt(tokenizer, compile_gate, current_nl)
        if extract_embeddings:
            lambda_out, compile_emb = generate_with_embedding(
                model, tokenizer, compile_prompt
            )
        else:
            lambda_out = generate_text_only(model, tokenizer, compile_prompt)
            compile_emb = None

        # ─── Decompile: λ → NL ───
        decompile_prompt = format_chat_prompt(tokenizer, decompile_gate, lambda_out)
        nl_out = generate_text_only(model, tokenizer, decompile_prompt)

        # ─── Metrics ───
        record = CycleRecord(
            cycle=cycle_idx,
            nl_input=current_nl,
            lambda_output=lambda_out,
            nl_output=nl_out,
        )

        if prev_lambda is not None:
            record.lambda_edit_dist = levenshtein(lambda_out, prev_lambda)
            record.lambda_norm_edit = normalised_edit_distance(lambda_out, prev_lambda)
            record.lambda_word_diff = word_diff(lambda_out, prev_lambda)

        if prev_nl is not None:
            record.nl_edit_dist = levenshtein(nl_out, prev_nl)
            record.nl_norm_edit = normalised_edit_distance(nl_out, prev_nl)
            record.nl_word_diff = word_diff(nl_out, prev_nl)

        if compile_emb is not None and prev_compile_emb is not None:
            record.embedding_cosine = cosine_sim(compile_emb, prev_compile_emb)

        record.elapsed_s = time.time() - t_cycle
        cycles.append(record)

        # ─── Report ───
        status = (
            f"  cycle {cycle_idx}: "
            f"λ_edit={record.lambda_edit_dist:3d} "
            f"nl_edit={record.nl_edit_dist:3d} "
            f"emb_cos={record.embedding_cosine:.4f} "
            f"({record.elapsed_s:.1f}s)"
        )
        print(status, file=sys.stderr)

        # ─── Convergence check ───
        if cycle_idx > 0:
            total_edit = record.lambda_edit_dist + record.nl_edit_dist
            if total_edit <= convergence_threshold:
                patience_count += 1
                if patience_count >= convergence_patience:
                    converged = True
                    convergence_cycle = cycle_idx - convergence_patience + 1
                    print(f"  → CONVERGED at cycle {convergence_cycle}", file=sys.stderr)
                    break
            else:
                patience_count = 0

        # ─── Advance ───
        prev_lambda = lambda_out
        prev_nl = nl_out
        prev_compile_emb = compile_emb
        current_nl = nl_out  # Feed decompiled NL back as next compile input

    return FixedPointResult(
        input_sentence=sentence,
        converged=converged,
        convergence_cycle=convergence_cycle,
        total_cycles=len(cycles),
        fixed_point_nl=cycles[-1].nl_output if converged else None,
        fixed_point_lambda=cycles[-1].lambda_output if converged else None,
        cycles=cycles,
        ground_truth_lambda=ground_truth_lambda,
        elapsed_total_s=time.time() - t_total_start,
    )


# ══════════════════════════════════════════════════════════════════
# Analysis helpers
# ══════════════════════════════════════════════════════════════════

def analyse_results(results: list[FixedPointResult]) -> dict:
    """Compute summary statistics across all inputs."""
    n_total = len(results)
    n_converged = sum(1 for r in results if r.converged)
    convergence_cycles = [r.convergence_cycle for r in results if r.converged and r.convergence_cycle is not None]

    # Residual analysis: what changes between cycle 0 and cycle 1?
    first_deltas = []
    for r in results:
        if len(r.cycles) >= 2:
            c0, c1 = r.cycles[0], r.cycles[1]
            first_deltas.append({
                "input": r.input_sentence[:60],
                "nl_edit": c1.nl_edit_dist,
                "lambda_edit": c1.lambda_edit_dist,
                "nl_words_added": c1.nl_word_diff.get("added", []),
                "nl_words_removed": c1.nl_word_diff.get("removed", []),
            })

    # Quality: compare fixed-point lambda to ground truth
    quality = []
    for r in results:
        if r.ground_truth_lambda and r.fixed_point_lambda:
            gt_norm = normalise_lambda(r.ground_truth_lambda)
            fp_norm = normalise_lambda(r.fixed_point_lambda)
            c0_norm = normalise_lambda(r.cycles[0].lambda_output) if r.cycles else ""
            quality.append({
                "input": r.input_sentence[:60],
                "ground_truth": r.ground_truth_lambda,
                "cycle_0_lambda": r.cycles[0].lambda_output if r.cycles else "",
                "fixed_point_lambda": r.fixed_point_lambda,
                "gt_vs_c0_edit": levenshtein(gt_norm, c0_norm),
                "gt_vs_fp_edit": levenshtein(gt_norm, fp_norm),
                "improved": levenshtein(gt_norm, fp_norm) < levenshtein(gt_norm, c0_norm),
            })

    # Embedding trajectory: cosine similarity curve
    emb_trajectories = []
    for r in results:
        trajectory = [c.embedding_cosine for c in r.cycles]
        emb_trajectories.append({
            "input": r.input_sentence[:60],
            "cosines": trajectory,
        })

    return {
        "summary": {
            "n_total": n_total,
            "n_converged": n_converged,
            "convergence_rate": n_converged / max(n_total, 1),
            "mean_convergence_cycle": (
                sum(convergence_cycles) / len(convergence_cycles)
                if convergence_cycles else None
            ),
            "median_convergence_cycle": (
                sorted(convergence_cycles)[len(convergence_cycles) // 2]
                if convergence_cycles else None
            ),
            "convergence_cycles": convergence_cycles,
        },
        "first_cycle_deltas": first_deltas,
        "quality_vs_ground_truth": quality,
        "embedding_trajectories": emb_trajectories,
    }


# ══════════════════════════════════════════════════════════════════
# Ground truth loading
# ══════════════════════════════════════════════════════════════════

def load_ground_truth(probe_path: Path = Path("probes/compile-gradient.json")) -> dict[str, str]:
    """Load ground truth lambdas from compile-gradient.json.

    Returns: {sentence: lambda} mapping
    """
    if not probe_path.exists():
        return {}
    with open(probe_path) as f:
        data = json.load(f)
    return {
        p["prompt"]: p["ground_truth"]
        for p in data.get("probes", [])
        if "prompt" in p and "ground_truth" in p
    }


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Fixed-point convergence probe for compile↔decompile cycle"
    )
    parser.add_argument("--max-cycles", type=int, default=MAX_CYCLES,
                        help=f"Maximum iterations (default: {MAX_CYCLES})")
    parser.add_argument("--quick", action="store_true",
                        help="Run on first 4 inputs only")
    parser.add_argument("--model", type=str, default=HF_MODEL,
                        help=f"HuggingFace model name (default: {HF_MODEL})")
    parser.add_argument("--no-embeddings", action="store_true",
                        help="Skip embedding extraction (faster)")
    parser.add_argument("--convergence-threshold", type=int,
                        default=CONVERGENCE_THRESHOLD,
                        help=f"Edit distance threshold for convergence (default: {CONVERGENCE_THRESHOLD})")
    parser.add_argument("--inputs", type=str, nargs="+",
                        help="Custom input sentences (overrides defaults)")
    args = parser.parse_args()

    # ─── Setup ───
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load gates
    compile_gate = (GATES_DIR / "compile.txt").read_text().strip()
    decompile_gate = (GATES_DIR / "decompile.txt").read_text().strip()

    print(f"Compile gate: {compile_gate[:80]}...", file=sys.stderr)
    print(f"Decompile gate: {decompile_gate[:80]}...", file=sys.stderr)

    # Load ground truth
    gt_map = load_ground_truth()
    print(f"Ground truth: {len(gt_map)} sentences", file=sys.stderr)

    # Select inputs
    if args.inputs:
        inputs = args.inputs
    else:
        inputs = DEFAULT_INPUTS
    if args.quick:
        inputs = inputs[:4]

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Fixed-Point Convergence Probe", file=sys.stderr)
    print(f"Model: {args.model}", file=sys.stderr)
    print(f"Inputs: {len(inputs)}", file=sys.stderr)
    print(f"Max cycles: {args.max_cycles}", file=sys.stderr)
    print(f"Convergence threshold: {args.convergence_threshold} chars", file=sys.stderr)
    print(f"Embeddings: {'yes' if not args.no_embeddings else 'no'}", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)

    # Load model
    model, tokenizer = load_model(args.model)

    # ─── Run ───
    results: list[FixedPointResult] = []
    t_start = time.time()

    for i, sentence in enumerate(inputs):
        gt = gt_map.get(sentence)
        print(f"\n[{i+1}/{len(inputs)}] \"{sentence[:60]}\"",
              file=sys.stderr)
        if gt:
            print(f"  ground truth: {gt}", file=sys.stderr)

        result = run_fixed_point(
            sentence,
            model,
            tokenizer,
            compile_gate,
            decompile_gate,
            max_cycles=args.max_cycles,
            convergence_threshold=args.convergence_threshold,
            extract_embeddings=not args.no_embeddings,
            ground_truth_lambda=gt,
        )
        results.append(result)

        # Incremental save
        out_path = OUTPUT_DIR / "convergence.json"
        with open(out_path, "w") as f:
            json.dump(
                {
                    "model": args.model,
                    "max_cycles": args.max_cycles,
                    "convergence_threshold": args.convergence_threshold,
                    "compile_gate": compile_gate,
                    "decompile_gate": decompile_gate,
                    "n_complete": i + 1,
                    "n_total": len(inputs),
                    "elapsed_s": time.time() - t_start,
                    "results": [r.to_dict() for r in results],
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

    # ─── Analysis ───
    analysis = analyse_results(results)
    analysis_path = OUTPUT_DIR / "analysis.json"
    with open(analysis_path, "w") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    # ─── Report ───
    s = analysis["summary"]
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"RESULTS", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"Converged: {s['n_converged']}/{s['n_total']} "
          f"({s['convergence_rate']:.0%})", file=sys.stderr)
    if s["mean_convergence_cycle"] is not None:
        print(f"Mean convergence cycle: {s['mean_convergence_cycle']:.1f}", file=sys.stderr)
        print(f"Median convergence cycle: {s['median_convergence_cycle']}", file=sys.stderr)

    # Show fixed points
    print(f"\nFixed Points:", file=sys.stderr)
    for r in results:
        marker = "✓" if r.converged else "✗"
        cyc = f"@{r.convergence_cycle}" if r.convergence_cycle is not None else f"/{r.total_cycles}"
        print(f"  {marker} {r.input_sentence[:50]:50s} {cyc}", file=sys.stderr)
        if r.converged:
            print(f"    λ: {r.fixed_point_lambda}", file=sys.stderr)
            print(f"    NL: {r.fixed_point_nl}", file=sys.stderr)

    # Quality vs ground truth
    if analysis["quality_vs_ground_truth"]:
        print(f"\nQuality vs Ground Truth:", file=sys.stderr)
        for q in analysis["quality_vs_ground_truth"]:
            arrow = "↑" if q["improved"] else "↓" if q["gt_vs_fp_edit"] > q["gt_vs_c0_edit"] else "="
            print(f"  {arrow} {q['input'][:40]:40s} "
                  f"c0={q['gt_vs_c0_edit']:3d} fp={q['gt_vs_fp_edit']:3d}",
                  file=sys.stderr)

    total_time = time.time() - t_start
    print(f"\nTotal time: {total_time:.1f}s", file=sys.stderr)
    print(f"Results: {OUTPUT_DIR / 'convergence.json'}", file=sys.stderr)
    print(f"Analysis: {analysis_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
