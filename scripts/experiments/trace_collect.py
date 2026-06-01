#!/usr/bin/env python3
"""Trace Collector — Batch opcode tracing for trace-guided etching.

Runs diverse inputs through a model, captures per-layer combinator
projections (opcode traces), and saves them as the functional
specification that a student model must reproduce.

Output: teacher_traces.npz containing:
  - traces: (n_inputs, n_layers, n_ops) — opcode energy per layer per input
  - gate_survival: (n_inputs, n_layers) — fraction of FFN neurons that fired
  - total_energy: (n_inputs, n_layers) — FFN output L2 norm
  - importance: (n_layers, d_ff) — per-neuron firing frequency across inputs
  - fingerprint_ops: list of op names matching the n_ops axis
  - input_texts: the input strings used

Usage:
    uv run python scripts/experiments/trace_collect.py --model Qwen/Qwen3-0.6B
    uv run python scripts/experiments/trace_collect.py --model Qwen/Qwen3-0.6B --n-inputs 200

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
from transformers import AutoModelForCausalLM, AutoTokenizer

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
RESULTS_BASE = PROJECT_ROOT / "results" / "hologram-reader"
PROBES_DIR = PROJECT_ROOT / "probes"

TOP4_OPS = ["K", "I", "B", "C"]
ALL_OPS = ["K", "I", "B", "C", "D", "Y", "W", "WHNF",
           "beta_K", "beta_I", "beta_apply", "beta_compose"]


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# ── Diverse input corpus ─────────────────────────────────────

def build_input_corpus(n_target: int) -> list[str]:
    """Build a diverse set of inputs for tracing."""
    corpus = []

    # Prose — diverse sentence structures
    prose = [
        "The cat sat on the mat and looked out the window at the birds.",
        "Every student who passed the final exam received a certificate.",
        "The man who the dog that the cat chased bit ran away quickly.",
        "In a quiet village nestled between rolling hills the old baker opened his shop.",
        "She believed that he thought that the answer was obviously wrong.",
        "The key that opened the door that led to the garden was lost.",
        "The mouse was chased by the cat through the garden quickly.",
        "Either the president or the minister signed the treaty last week.",
        "The gradient of the loss with respect to the weights is computed via backpropagation.",
        "Water flows downhill following the path of least resistance always.",
        "The temperature is rising and the wind keeps shifting every day.",
        "If every teacher who knows a student that failed helps them all improve.",
        "The old house unlike the new building survived the earthquake without damage.",
        "Birds flew south for the winter as the leaves began to fall.",
        "The clock on the wall showed that it was nearly midnight already.",
        "He said hello and then she also said hello to everyone present.",
        "The result was five and the answer is five so five is correct.",
        "First he ate the apple then he ate another apple after that.",
        "The company that hired the lawyer who won the case prospered greatly.",
        "Clouds gathered in the sky promising rain by the afternoon today.",
    ]
    corpus.extend(prose)

    # Factual — knowledge retrieval
    facts = [
        "The capital of France is",
        "The largest planet in our solar system is",
        "Water boils at a temperature of",
        "The speed of light in a vacuum is approximately",
        "Shakespeare was born in the year",
        "The chemical symbol for gold is",
        "Mount Everest is located in",
        "The human heart has how many chambers:",
        "Einstein published his theory of relativity in",
        "The Great Wall of China was built to",
        "Photosynthesis converts sunlight into",
        "The Amazon River flows through",
        "DNA stands for",
        "The periodic table was created by",
        "Gravity pulls objects toward the center of",
    ]
    corpus.extend(facts)

    # Compositional — nested structures requiring reduction
    compositional = [
        "The student who read the book that the professor who taught the class recommended passed.",
        "If every person who knows someone that failed helps them then everyone improves.",
        "The letter that was written by the woman who lived in the house was lost.",
        "No politician who endorsed the candidate that lost the election won their race.",
        "The scientist whose paper that the journal rejected was later proved correct.",
        "A program that calls a function that calls another function must manage the stack.",
        "The theory which predicts that energy equals mass times the speed of light squared.",
        "Every dog that chased a cat that scratched a mouse was punished by its owner.",
        "The building where the meeting that decided the policy was held burned down.",
        "She told him that she thought that he believed that they would win.",
    ]
    corpus.extend(compositional)

    # Lambda / formal — compile-mode inputs
    formal = [
        "K x y = x",
        "B f g x = f (g x)",
        "S f g x = f x (g x)",
        "C f x y = f y x",
        "The function that maps x to x squared is lambda x dot x times x.",
        "Apply the identity function to any argument and get that argument back.",
        "Compose two functions: first apply g then apply f to the result.",
        "For all x in the real numbers x squared is greater than or equal to zero.",
        "The fixed point combinator Y satisfies Y f = f (Y f) for all f.",
        "Beta reduction: (lambda x. f x) a reduces to f a.",
    ]
    corpus.extend(formal)

    # Code
    code = [
        "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
        "for i in range(10): print(i * i)",
        "SELECT name FROM users WHERE age > 21 ORDER BY name",
        "git commit -m 'fix: resolve null pointer in parser'",
        "import torch; model = torch.nn.Linear(768, 768)",
    ]
    corpus.extend(code)

    # Repeat/extend to reach target
    while len(corpus) < n_target:
        corpus.extend(corpus[:n_target - len(corpus)])

    return corpus[:n_target]


# ── Architecture-agnostic helpers ─────────────────────────────

def get_layers(model) -> list:
    for attr_path in ["model.layers", "transformer.h", "gpt_neox.layers"]:
        obj = model
        try:
            for part in attr_path.split("."):
                obj = getattr(obj, part)
            return list(obj)
        except AttributeError:
            continue
    raise RuntimeError(f"Cannot find transformer layers in {type(model)}")


def get_gate_and_down(layer):
    mlp = layer.mlp if hasattr(layer, "mlp") else layer
    if hasattr(mlp, "gate_proj"):
        return mlp.gate_proj, mlp.down_proj, "swiglu"
    if hasattr(mlp, "dense_h_to_4h"):
        return mlp.dense_h_to_4h, mlp.dense_4h_to_h, "gpt_neox"
    raise RuntimeError(f"Cannot find MLP in {type(mlp)}")


# ── Core tracing ─────────────────────────────────────────────

def trace_single_input(
    model, tokenizer, text: str, layers: list,
    fingerprints: dict[str, np.ndarray], ops: list[str],
    n_layers: int,
) -> dict:
    """Trace one input through the model, return opcode projections."""
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    device = next(model.parameters()).device
    input_ids = input_ids.to(device)

    # Storage
    gate_caps = {}
    ffn_caps = {}
    hooks = []

    for li in range(n_layers):
        layer = layers[li]
        try:
            gate_mod, down_mod, mlp_type = get_gate_and_down(layer)
        except RuntimeError:
            continue

        def make_gate_hook(idx, mtype):
            def hook(m, inp, out):
                t = out.detach()
                if mtype == "gpt_neox":
                    half = t.shape[-1] // 2
                    gate_caps[idx] = t[0, -1, :half].cpu().float().numpy()
                else:
                    gate_caps[idx] = t[0, -1, :].cpu().float().numpy()
            return hook

        def make_down_hook(idx):
            def hook(m, inp, out):
                ffn_caps[idx] = out[0, -1, :].detach().cpu().float().numpy()
            return hook

        hooks.append(gate_mod.register_forward_hook(make_gate_hook(li, mlp_type)))
        hooks.append(down_mod.register_forward_hook(make_down_hook(li)))

    with torch.no_grad():
        _ = model(input_ids=input_ids)

    for h in hooks:
        h.remove()

    # Project onto fingerprints
    n_ops = len(ops)
    opcode_energy = np.zeros((n_layers, n_ops), dtype=np.float32)
    gate_survival = np.zeros(n_layers, dtype=np.float32)
    total_energy = np.zeros(n_layers, dtype=np.float32)
    gate_activations = {}  # for importance computation

    for li in range(n_layers):
        if li not in ffn_caps:
            continue
        ffn_vec = ffn_caps[li]
        ffn_norm = float(np.linalg.norm(ffn_vec))
        total_energy[li] = ffn_norm

        if ffn_norm > 1e-10:
            ffn_unit = ffn_vec / ffn_norm
            for oi, op in enumerate(ops):
                fp = fingerprints.get(op)
                if fp is not None and li < fp.shape[0]:
                    fp_vec = fp[li]
                    fp_norm = np.linalg.norm(fp_vec)
                    if fp_norm > 1e-10:
                        opcode_energy[li, oi] = float(np.dot(ffn_unit, fp_vec / fp_norm))

        if li in gate_caps:
            gate = gate_caps[li]
            sig = 1.0 / (1.0 + np.exp(-np.clip(gate, -20, 20)))
            gate_survival[li] = float(np.mean(sig > 0.5))
            gate_activations[li] = (sig > 0.5).astype(np.float32)

    return {
        "opcode_energy": opcode_energy,
        "gate_survival": gate_survival,
        "total_energy": total_energy,
        "gate_activations": gate_activations,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--n-inputs", type=int, default=100)
    parser.add_argument("--ops", default="top4", choices=["top4", "all12"])
    parser.add_argument("--output", type=str, default=None,
                        help="Output path (default: results/trace-etching/{slug}/teacher_traces.npz)")
    args = parser.parse_args()

    ops = TOP4_OPS if args.ops == "top4" else ALL_OPS
    slug = args.model.replace("/", "_")

    # Output directory
    if args.output:
        out_path = Path(args.output)
    else:
        out_dir = PROJECT_ROOT / "results" / "trace-etching" / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "teacher_traces.npz"

    # Load model
    log(f"\n  Loading {args.model}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.float32, device_map=args.device)
    model.eval()
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    layers = get_layers(model)
    n_layers = len(layers)
    d_model = model.config.hidden_size
    d_ff = getattr(model.config, "intermediate_size", d_model * 4)
    log(f"  {n_layers} layers, d_model={d_model}, d_ff={d_ff}")

    # Load fingerprints
    fp_path = RESULTS_BASE / slug / f"fingerprints_{slug}.npz"
    if not fp_path.exists():
        log(f"  ❌ No fingerprints at {fp_path}")
        log(f"     Run hologram_reader.py on this model first.")
        sys.exit(1)

    data = np.load(fp_path)
    fingerprints = {op: data[op] for op in ops if op in data}
    log(f"  Loaded {len(fingerprints)} fingerprints")

    # Build corpus
    corpus = build_input_corpus(args.n_inputs)
    log(f"\n  Tracing {len(corpus)} inputs...")

    # Collect traces
    all_opcode = []
    all_gate = []
    all_energy = []
    importance_acc = np.zeros((n_layers, d_ff), dtype=np.float64)
    n_importance = 0

    t0 = time.time()
    for i, text in enumerate(corpus):
        result = trace_single_input(
            model, tokenizer, text, layers, fingerprints, ops, n_layers)
        all_opcode.append(result["opcode_energy"])
        all_gate.append(result["gate_survival"])
        all_energy.append(result["total_energy"])

        # Accumulate neuron importance (gate firing frequency)
        for li, gate_act in result["gate_activations"].items():
            if gate_act.shape[0] <= d_ff:
                importance_acc[li, :gate_act.shape[0]] += gate_act
        n_importance += 1

        if (i + 1) % 20 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            eta = (len(corpus) - i - 1) / rate
            log(f"    {i+1}/{len(corpus)} ({rate:.1f}/s, ETA {eta:.0f}s)")

    elapsed = time.time() - t0

    # Stack into arrays
    traces = np.stack(all_opcode)      # (n_inputs, n_layers, n_ops)
    gate_surv = np.stack(all_gate)     # (n_inputs, n_layers)
    energies = np.stack(all_energy)    # (n_inputs, n_layers)
    importance = importance_acc / max(n_importance, 1)  # (n_layers, d_ff)

    # Save
    np.savez_compressed(
        out_path,
        traces=traces,
        gate_survival=gate_surv,
        total_energy=energies,
        importance=importance,
        op_names=np.array(ops),
        input_texts=np.array(corpus, dtype=object),
        model_name=args.model,
        n_layers=n_layers,
        d_model=d_model,
        d_ff=d_ff,
    )

    # Summary
    log(f"\n{'='*60}")
    log(f"  Teacher traces collected: {out_path}")
    log(f"  Inputs: {len(corpus)}  Layers: {n_layers}  Ops: {len(ops)}")
    log(f"  Traces shape: {traces.shape}")
    log(f"  Time: {elapsed:.1f}s ({len(corpus)/elapsed:.1f} inputs/s)")
    log(f"{'='*60}")

    # Per-layer opcode profile
    mean_traces = np.mean(np.abs(traces), axis=0)  # (n_layers, n_ops)
    log(f"\n  Mean |opcode energy| per layer (top-4):")
    log(f"  {'Layer':<8} " + "  ".join(f"{op:>7}" for op in ops[:4]))
    log(f"  {'─'*8} " + "  ".join("─" * 7 for _ in ops[:4]))
    for li in range(0, n_layers, max(1, n_layers // 10)):
        vals = "  ".join(f"{mean_traces[li, oi]:>7.4f}" for oi in range(min(4, len(ops))))
        log(f"  L{li:<6} {vals}")

    # Neuron importance summary
    log(f"\n  Neuron importance (firing frequency):")
    for li in range(0, n_layers, max(1, n_layers // 5)):
        imp = importance[li]
        active = float(np.mean(imp > 0.1))
        log(f"    L{li:02d}: {active*100:.1f}% neurons fire on >10% of inputs")

    log(f"\n  ✅ Ready for trace-guided etching")


if __name__ == "__main__":
    main()
