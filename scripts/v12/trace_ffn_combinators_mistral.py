"""FFN Combinator Tracer — Mistral-7B cross-model normal form search.

Run the same combinator trace protocol on Mistral-7B to find
normal forms: combinator programs that are identical across models.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/trace_ffn_combinators_mistral.py 2>&1 | tee results/ffn-trace-mistral/run.log

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
from transformers import AutoTokenizer, AutoModelForCausalLM

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "ffn-trace-mistral"
MODEL_NAME = "mistralai/Mistral-7B-v0.3"
N_LAYERS = 32
DEVICE = "mps"

# Trace at all layers for full program visibility
ALL_LAYERS = list(range(N_LAYERS))

# For fingerprinting, use a subset for speed
FINGERPRINT_LAYERS = list(range(N_LAYERS))


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Model loading
# ══════════════════════════════════════════════════════════════════════

COMPILE_GATE = """You are a lambda calculus compiler. Convert natural language to typed lambda calculus.
Input a combinator expression. Output its beta-normal form.
Be terse. Output ONLY the reduced expression."""


def load_model():
    log(f"  Loading {MODEL_NAME}...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.bfloat16,
        device_map=DEVICE, trust_remote_code=True,
    )
    model.eval()
    log(f"  Loaded in {time.time()-t0:.1f}s")
    return model, tokenizer


# ══════════════════════════════════════════════════════════════════════
# FFN activation capture
# ══════════════════════════════════════════════════════════════════════

def capture_ffn_at_layers(model, tokenizer, text: str, layers: list[int]) -> dict:
    """Capture FFN down_proj output at specified layers, last token position."""
    ids = tokenizer.encode(text, return_tensors="pt").to(DEVICE)
    captures = {}
    hooks = []

    for li in layers:
        def make_hook(layer_idx):
            def hook(m, inp, out):
                captures[layer_idx] = out[0, -1, :].detach().cpu().float().numpy()
            return hook
        hooks.append(model.model.layers[li].mlp.down_proj.register_forward_hook(make_hook(li)))

    with torch.no_grad():
        _ = model(ids)

    for h in hooks:
        h.remove()

    return captures


# ══════════════════════════════════════════════════════════════════════
# Phase 1: Build combinator fingerprints
# ══════════════════════════════════════════════════════════════════════

def build_fingerprints(model, tokenizer) -> dict:
    """Compute mean FFN delta vectors per combinator per layer.

    These are the "opcodes" — the characteristic FFN signature of each
    combinator reduction operation.
    """
    log("\n═══ Phase 1: Building combinator fingerprints ═══")

    # Minimal pairs for each combinator
    pairs = {
        "K": [
            (f"K {v1} {v2}", f"{v1}")
            for v1 in ["x", "y", "a", "b", "c"]
            for v2 in ["z", "d", "e"] if v1 != v2
        ][:8],
        "I": [
            (f"I {v}", f"{v}")
            for v in ["x", "y", "a", "b", "z"]
        ],
        "B": [
            (f"B {f} {g} {v}", f"{f} ({g} {v})")
            for f in ["f", "g", "h"]
            for g in ["p", "q"] if f != g
            for v in ["x", "a"]
        ][:8],
        "C": [
            (f"C {f} {v1} {v2}", f"{f} {v2} {v1}")
            for f in ["f", "g", "h"]
            for v1 in ["x", "a"]
            for v2 in ["y", "b"] if v1 != v2
        ][:8],
        "S": [
            (f"S {f} {g} {v}", f"{f} {v} ({g} {v})")
            for f in ["f", "g"]
            for g in ["h", "p"] if f != g
            for v in ["x", "a"]
        ][:6],
        "beta_K": [
            (f"(λx. λy. x) {v1} {v2}", f"{v1}")
            for v1 in ["a", "b", "x"]
            for v2 in ["c", "y", "z"] if v1 != v2
        ][:6],
        "beta_apply": [
            (f"(λx. {f} x) {v}", f"{f} {v}")
            for f in ["f", "g", "h"]
            for v in ["a", "x"]
        ][:6],
        "beta_identity": [
            (f"(λx. x) {v}", f"{v}")
            for v in ["a", "b", "x", "y", "z"]
        ],
    }

    fingerprints = {}  # {combinator: {layer: mean_delta_vector}}

    for comb, comb_pairs in pairs.items():
        log(f"  {comb}: {len(comb_pairs)} pairs")
        layer_deltas = {li: [] for li in FINGERPRINT_LAYERS}

        for pre_expr, post_expr in comb_pairs:
            pre_text = f"{COMPILE_GATE}\n\n{pre_expr} ="
            post_text = f"{COMPILE_GATE}\n\n{post_expr} ="

            pre_caps = capture_ffn_at_layers(model, tokenizer, pre_text, FINGERPRINT_LAYERS)
            post_caps = capture_ffn_at_layers(model, tokenizer, post_text, FINGERPRINT_LAYERS)

            for li in FINGERPRINT_LAYERS:
                if li in pre_caps and li in post_caps:
                    delta = pre_caps[li] - post_caps[li]
                    layer_deltas[li].append(delta)

        fingerprints[comb] = {}
        for li in FINGERPRINT_LAYERS:
            vecs = np.array(layer_deltas[li])
            if len(vecs) > 0:
                mean_delta = np.mean(vecs, axis=0)
                # Normalize to unit vector for cosine projection
                norm = np.linalg.norm(mean_delta)
                if norm > 1e-10:
                    fingerprints[comb][li] = mean_delta / norm
                else:
                    fingerprints[comb][li] = mean_delta

        log(f"    ✓ {comb} fingerprints computed")

    return fingerprints


# ══════════════════════════════════════════════════════════════════════
# Phase 2: Trace complex inputs
# ══════════════════════════════════════════════════════════════════════

def trace_input(model, tokenizer, fingerprints: dict, text: str,
                label: str = "") -> dict:
    """Feed an input through the model and project FFN against fingerprints.

    Returns per-layer combinator activation scores.
    """
    captures = capture_ffn_at_layers(model, tokenizer, text, ALL_LAYERS)

    combinator_names = sorted(fingerprints.keys())
    trace = {}

    for li in ALL_LAYERS:
        if li not in captures:
            continue

        ffn_vec = captures[li]
        ffn_norm = np.linalg.norm(ffn_vec)
        if ffn_norm < 1e-10:
            trace[li] = {c: 0.0 for c in combinator_names}
            continue

        ffn_unit = ffn_vec / ffn_norm

        scores = {}
        for comb in combinator_names:
            if li in fingerprints[comb]:
                cos = float(np.dot(ffn_unit, fingerprints[comb][li]))
                scores[comb] = cos
            else:
                scores[comb] = 0.0

        trace[li] = scores

    return trace


def format_trace(trace: dict, label: str = "", top_n: int = 3) -> str:
    """Format a trace as a readable layer-by-layer combinator activation map."""
    lines = []
    if label:
        lines.append(f"\n  ┌─ {label}")
        lines.append(f"  │")

    combinator_names = sorted(next(iter(trace.values())).keys()) if trace else []

    for li in sorted(trace.keys()):
        scores = trace[li]
        # Sort by absolute cosine similarity
        ranked = sorted(scores.items(), key=lambda x: abs(x[1]), reverse=True)
        top = ranked[:top_n]

        # Build bar visualization
        bar = ""
        for comb, score in top:
            if abs(score) > 0.1:
                strength = "█" * int(abs(score) * 10)
                sign = "+" if score > 0 else "-"
                bar += f" {comb}:{sign}{abs(score):.2f}{strength}"

        dominant = ranked[0][0] if ranked[0][1] > 0.15 else "---"
        lines.append(f"  │ L{li:2d}  {dominant:>14s}  {bar}")

    lines.append(f"  └─")
    return "\n".join(lines)


def decode_trace_to_combinators(trace: dict, threshold: float = 0.15) -> list[dict]:
    """Extract the combinator program from a trace.

    Returns list of {layer, combinator, score} for each layer where
    a combinator is clearly active (above threshold).
    """
    program = []
    for li in sorted(trace.keys()):
        scores = trace[li]
        ranked = sorted(scores.items(), key=lambda x: abs(x[1]), reverse=True)

        # Take all above threshold
        active = [(c, s) for c, s in ranked if abs(s) > threshold]
        if active:
            program.append({
                "layer": li,
                "primary": active[0][0],
                "primary_score": active[0][1],
                "active": {c: s for c, s in active},
            })

    return program


# ══════════════════════════════════════════════════════════════════════
# Phase 3: Probe suite — trace diverse operations
# ══════════════════════════════════════════════════════════════════════

def build_trace_probes() -> list[dict]:
    """Build diverse probes for tracing."""
    probes = []

    # ── Known lambda reductions (validation) ──
    probes.append({
        "category": "validation",
        "label": "K a b = a (simple selection)",
        "text": f"{COMPILE_GATE}\n\nK a b =",
    })
    probes.append({
        "category": "validation",
        "label": "B f g x = f(gx) (composition)",
        "text": f"{COMPILE_GATE}\n\nB f g x =",
    })
    probes.append({
        "category": "validation",
        "label": "S f g x = fx(gx) (distribution)",
        "text": f"{COMPILE_GATE}\n\nS f g x =",
    })
    probes.append({
        "category": "validation",
        "label": "K (I a) b = a (nested K∘I)",
        "text": f"{COMPILE_GATE}\n\nK (I a) b =",
    })
    probes.append({
        "category": "validation",
        "label": "B K I x = K(Ix) = Ix = x (B∘K∘I)",
        "text": f"{COMPILE_GATE}\n\nB K I x =",
    })

    # ── Arithmetic (where are the beta reduction piles?) ──
    probes.append({
        "category": "arithmetic",
        "label": "2 + 3 = 5",
        "text": "Calculate: 2 + 3 =",
    })
    probes.append({
        "category": "arithmetic",
        "label": "17 * 23 = 391",
        "text": "Calculate: 17 * 23 =",
    })
    probes.append({
        "category": "arithmetic",
        "label": "144 / 12 = 12",
        "text": "Calculate: 144 / 12 =",
    })
    probes.append({
        "category": "arithmetic",
        "label": "sqrt(169) = 13",
        "text": "Calculate: sqrt(169) =",
    })

    # ── Date/time (Fourier approximation chains?) ──
    probes.append({
        "category": "date",
        "label": "What day is Jan 1 2025?",
        "text": "What day of the week is January 1, 2025?",
    })
    probes.append({
        "category": "date",
        "label": "Days between dates",
        "text": "How many days between March 15 and June 20?",
    })

    # ── Reasoning (pure composition?) ──
    probes.append({
        "category": "reasoning",
        "label": "Syllogism: All A are B, all B are C",
        "text": "All dogs are animals. All animals are living things. Therefore, all dogs are",
    })
    probes.append({
        "category": "reasoning",
        "label": "Contrapositive",
        "text": "If it rains, the ground is wet. The ground is not wet. Therefore,",
    })

    # ── String/pattern (what operations?) ──
    probes.append({
        "category": "string",
        "label": "Reverse word",
        "text": "Reverse the letters in 'hello': ",
    })
    probes.append({
        "category": "string",
        "label": "Count letters",
        "text": "How many letters in 'strawberry'? Count carefully:",
    })

    # ── Factual retrieval (FFN key-value lookup?) ──
    probes.append({
        "category": "retrieval",
        "label": "Capital of France",
        "text": "The capital of France is",
    })
    probes.append({
        "category": "retrieval",
        "label": "Water formula",
        "text": "The chemical formula for water is",
    })

    # ── Lambda with gate (compiler circuit active) ──
    probes.append({
        "category": "lambda_gate",
        "label": "NL → lambda (the compiler itself)",
        "text": f"{COMPILE_GATE}\n\nEvery student read a book =",
    })
    probes.append({
        "category": "lambda_gate",
        "label": "NL → lambda (simple)",
        "text": f"{COMPILE_GATE}\n\nThe cat sat on the mat =",
    })

    return probes


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log("═══════════════════════════════════════════════════════")
    log("  FFN Combinator Tracer — Mistral-7B Normal Form Search")
    log("  32 layers, d_model=4096, d_intermediate=14336")
    log("═══════════════════════════════════════════════════════")

    t0 = time.time()
    model, tokenizer = load_model()

    # ── Phase 1: Build fingerprints ────────────────────────────
    fingerprints = build_fingerprints(model, tokenizer)

    # Save fingerprints for reuse
    fp_data = {}
    for comb, layers in fingerprints.items():
        fp_data[comb] = {str(li): v.tolist() for li, v in layers.items()}
    with open(RESULTS_DIR / "fingerprints.json", "w") as f:
        json.dump(fp_data, f)
    log(f"\n  Fingerprints saved to {RESULTS_DIR / 'fingerprints.json'}")

    # ── Phase 2: Trace probes ──────────────────────────────────
    log("\n═══ Phase 2: Tracing complex operations ═══")
    probes = build_trace_probes()

    all_traces = []
    for probe in probes:
        log(f"\n  Tracing: {probe['label']}")
        trace = trace_input(model, tokenizer, fingerprints, probe["text"], probe["label"])
        formatted = format_trace(trace, probe["label"])
        log(formatted)

        # Decode to combinator program
        program = decode_trace_to_combinators(trace, threshold=0.15)
        dominant_sequence = [p["primary"] for p in program]

        log(f"  Program: {' → '.join(dominant_sequence[:20])}")

        all_traces.append({
            "category": probe["category"],
            "label": probe["label"],
            "text": probe["text"][:100],
            "trace": {str(k): v for k, v in trace.items()},
            "program": program,
            "dominant_sequence": dominant_sequence,
        })

    # ── Phase 3: Cross-category analysis ──────────────────────
    log("\n═══ Phase 3: Cross-Category Comparison ═══")

    categories = sorted(set(p["category"] for p in probes))
    for cat in categories:
        cat_traces = [t for t in all_traces if t["category"] == cat]
        log(f"\n  {cat.upper()} ({len(cat_traces)} probes):")

        # Compute average combinator activation per layer for this category
        combinator_names = sorted(fingerprints.keys())
        n_layers_traced = len(ALL_LAYERS)

        cat_matrix = np.zeros((n_layers_traced, len(combinator_names)))
        for t in cat_traces:
            for li_idx, li in enumerate(ALL_LAYERS):
                if str(li) in t["trace"]:
                    for ci, comb in enumerate(combinator_names):
                        cat_matrix[li_idx, ci] += t["trace"][str(li)].get(comb, 0)
        cat_matrix /= max(len(cat_traces), 1)

        # Find which combinators dominate at each depth region (32 layers)
        early = cat_matrix[:8].mean(axis=0)     # L0-L7
        mid = cat_matrix[8:24].mean(axis=0)     # L8-L23
        late = cat_matrix[24:].mean(axis=0)     # L24-L31

        log(f"    Early layers (L0-L7):")
        for ci, comb in enumerate(combinator_names):
            if abs(early[ci]) > 0.05:
                log(f"      {comb:>14s}: {early[ci]:+.3f}")

        log(f"    Mid layers (L8-L23):")
        for ci, comb in enumerate(combinator_names):
            if abs(mid[ci]) > 0.05:
                log(f"      {comb:>14s}: {mid[ci]:+.3f}")

        log(f"    Late layers (L24-L31):")
        for ci, comb in enumerate(combinator_names):
            if abs(late[ci]) > 0.05:
                log(f"      {comb:>14s}: {late[ci]:+.3f}")

    # ── Save results ───────────────────────────────────────────
    elapsed = time.time() - t0

    results = {
        "experiment": "ffn_combinator_trace_mistral",
        "model": MODEL_NAME,
        "n_layers": N_LAYERS,
        "d_model": 4096,
        "elapsed_s": elapsed,
        "n_probes": len(probes),
        "categories": categories,
        "traces": all_traces,
    }

    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    log(f"\n═══════════════════════════════════════════════════════")
    log(f"  Done in {elapsed:.1f}s")
    log(f"  Results: {RESULTS_DIR / 'results.json'}")
    log(f"═══════════════════════════════════════════════════════")

    del model, tokenizer
    gc.collect()
    torch.mps.empty_cache()


if __name__ == "__main__":
    main()
