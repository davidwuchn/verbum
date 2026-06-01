"""Symbol Isolation Experiment — Does pure prose activate the lambda engine?

Session 175. The foundational question: when we see combinator activations
in response to prose text, is that because:
  (a) prose genuinely uses the same computational circuitry as lambda, or
  (b) the "=" sign, "λ" symbol, or compile gate in our probes is what
      triggers the activation, and we're measuring an artifact?

This experiment isolates each potential confound by running 7 probe
categories through the model and measuring combinator energy per zone:

  1. PURE_PROSE     — diverse sentences, ZERO mathematical/logical symbols
  2. PROSE_EQUALS   — same sentences with trailing " ="
  3. PROSE_ARROW    — sentences containing "→"
  4. LAMBDA_EQ      — "(λx. f(x)) arg =" (original format)
  5. LAMBDA_NO_EQ   — "(λx. f(x)) arg" (no trailing =)
  6. NL_FACT        — "The capital of France is" (clean factual)
  7. GATED_PROSE    — COMPILE_GATE + pure prose (gate effect only)

For each probe: capture gate/up/moiré activations at every layer,
project onto combinator fingerprints, measure energy per zone.

If PURE_PROSE shows the same combinator profile as LAMBDA_EQ,
the engine is real. If only probes with "=" show it, the "=" is
doing the work.

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/symbol_isolation.py
    uv run python scripts/experiments/symbol_isolation.py --model Qwen/Qwen3-4B

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


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "symbol-isolation"
HOLOGRAM_DIR = Path(__file__).parent.parent.parent / "results" / "hologram-reader"

COMPILE_GATE = (
    "You are a lambda calculus compiler. Convert natural language to "
    "typed lambda calculus.\nInput a combinator expression. Output its "
    "beta-normal form.\nBe terse. Output ONLY the reduced expression."
)

# Zone boundaries (normalized depth fractions, universal across models)
# SILENT=0-50%, ENRICH=50-83%, SUPPRESS=83-92%, COMMIT=92-100%
ZONE_FRACS = [
    ("SILENT", 0.0, 0.50),
    ("ENRICH", 0.50, 0.83),
    ("SUPPRESS", 0.83, 0.92),
    ("COMMIT", 0.92, 1.0),
]

ALL_OP_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF",
                "beta_K", "beta_I", "beta_apply", "beta_compose"]
N_OPS = len(ALL_OP_NAMES)


def log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Probe definitions — strictly controlled for symbol contamination
# ══════════════════════════════════════════════════════════════════════

def build_probes() -> dict[str, list[dict]]:
    """Build all probe categories with strict symbol control."""

    categories = {}

    # ── 1. PURE_PROSE: zero mathematical/logical symbols ──────────
    # No: = → λ ∀ ∃ ∧ ∨ ¬ ( ) + - * / ^ % | & < > [ ] { } @ # $ ~
    # Only standard English punctuation: . , ; : ' " ! ? -
    prose = [
        "The old man walked slowly through the crowded market.",
        "She remembered the day they first met at the library.",
        "Rain fell steadily on the tin roof all night long.",
        "The children played in the park until the sun went down.",
        "He opened the letter and read it twice before responding.",
        "The river winds through the valley toward the distant sea.",
        "She told him the truth, but he refused to believe her.",
        "The dog barked at the stranger standing by the gate.",
        "They built the house on the hill overlooking the town.",
        "Morning light filled the room as she opened the curtains.",
        "The professor explained the concept to the confused students.",
        "Birds gathered on the wire above the quiet street.",
        "He carried the heavy box up three flights of stairs.",
        "The train arrived late because of the winter storm.",
        "She planted flowers in the garden every spring without fail.",
        "The cat sat on the windowsill watching the birds outside.",
        "They celebrated with dinner at their favorite restaurant.",
        "The wind howled through the empty streets of the village.",
        "He found the missing book tucked behind the old sofa.",
        "The baker woke before dawn to start the morning bread.",
    ]
    categories["PURE_PROSE"] = [
        {"id": f"prose_{i:02d}", "text": t} for i, t in enumerate(prose)
    ]

    # ── 2. PROSE_EQUALS: same sentences with " =" appended ────────
    categories["PROSE_EQUALS"] = [
        {"id": f"prose_eq_{i:02d}", "text": t.rstrip(".") + " ="}
        for i, t in enumerate(prose)
    ]

    # ── 3. PROSE_ARROW: sentences rewritten with "→" ──────────────
    arrow_sentences = [
        "If it rains then the ground gets wet.",  # no arrow yet
        "The old man walked through the market and found a gem.",
        "She read the letter then she wrote a reply.",
        "The dog barked and the stranger ran away.",
        "He studied hard then he passed the exam.",
        "They planted seeds and the flowers grew.",
        "The sun rose then the birds began to sing.",
        "She opened the door and saw the empty room.",
        "The river flooded then the bridge collapsed.",
        "He asked a question and she gave an answer.",
    ]
    categories["PROSE_ARROW"] = [
        {"id": f"arrow_{i:02d}", "text": t.replace(" then ", " → ").replace(" and ", " → ")}
        for i, t in enumerate(arrow_sentences)
    ]

    # ── 4. LAMBDA_EQ: original lambda format with = ───────────────
    lambda_pairs = [
        ("France", "Paris", "capital_of"),
        ("Japan", "Tokyo", "capital_of"),
        ("Germany", "Berlin", "capital_of"),
        ("Brazil", "Brasilia", "capital_of"),
        ("Italy", "Rome", "capital_of"),
        ("Egypt", "Cairo", "capital_of"),
        ("Spain", "Madrid", "capital_of"),
        ("Australia", "Canberra", "capital_of"),
        ("Brazil", "Portuguese", "language_of"),
        ("Japan", "Japanese", "language_of"),
    ]
    categories["LAMBDA_EQ"] = [
        {"id": f"lambda_eq_{i:02d}",
         "text": f"(λx. {rel}(x)) {ent} ="}
        for i, (ent, tgt, rel) in enumerate(lambda_pairs)
    ]

    # ── 5. LAMBDA_NO_EQ: same without trailing = ─────────────────
    categories["LAMBDA_NO_EQ"] = [
        {"id": f"lambda_noeq_{i:02d}",
         "text": f"(λx. {rel}(x)) {ent}"}
        for i, (ent, tgt, rel) in enumerate(lambda_pairs)
    ]

    # ── 6. NL_FACT: clean factual prompts (no symbols) ───────────
    categories["NL_FACT"] = [
        {"id": f"nl_{i:02d}", "text": t}
        for i, t in enumerate([
            "The capital of France is",
            "The capital of Japan is",
            "The capital of Germany is",
            "The capital of Brazil is",
            "The capital of Italy is",
            "The capital of Egypt is",
            "The capital of Spain is",
            "The capital of Australia is",
            "The language of Brazil is",
            "The language of Japan is",
        ])
    ]

    # ── 7. GATED_PROSE: compile gate + pure prose ────────────────
    categories["GATED_PROSE"] = [
        {"id": f"gated_{i:02d}",
         "text": f"{COMPILE_GATE}\n\n{t}"}
        for i, t in enumerate(prose[:10])
    ]

    # ── 8. EQUALS_ONLY: just "X =" with factual content ──────────
    categories["EQUALS_ONLY"] = [
        {"id": f"eq_only_{i:02d}", "text": t}
        for i, t in enumerate([
            "The capital of France =",
            "The capital of Japan =",
            "The capital of Germany =",
            "The capital of Brazil =",
            "The capital of Italy =",
            "The capital of Egypt =",
            "The capital of Spain =",
            "The capital of Australia =",
            "The language of Brazil =",
            "The language of Japan =",
        ])
    ]

    return categories


# ══════════════════════════════════════════════════════════════════════
# FFN Hook (reused from moire_selectivity.py)
# ══════════════════════════════════════════════════════════════════════

class LayerOutputHook:
    """Captures the hidden state (residual stream) after each transformer layer.

    The fingerprints from the hologram reader are built from down_proj output
    which is in d_model space. We capture the full layer output (also d_model)
    so projections onto fingerprints are dimensionally consistent.
    """

    def __init__(self, n_layers: int):
        self.n_layers = n_layers
        self.layer_acts: dict[int, torch.Tensor] = {}
        self.handles: list = []

    def _make_hook(self, layer_idx: int):
        def hook(module, input, output):
            # Transformer layer output: tuple, first element is hidden state
            hidden = output[0] if isinstance(output, tuple) else output
            # Last token position, detach and move to CPU
            self.layer_acts[layer_idx] = hidden[0, -1, :].detach().cpu()
        return hook

    def register(self, model):
        for i in range(self.n_layers):
            layer = model.model.layers[i]
            h = layer.register_forward_hook(self._make_hook(i))
            self.handles.append(h)

    def remove(self):
        for h in self.handles:
            h.remove()
        self.handles.clear()

    def get_hidden_states(self) -> dict[int, np.ndarray]:
        """Return per-layer hidden states in d_model space (float32)."""
        return {
            li: self.layer_acts[li].float().numpy()
            for li in range(self.n_layers)
            if li in self.layer_acts
        }

    def clear(self):
        self.layer_acts.clear()


# ══════════════════════════════════════════════════════════════════════
# Main experiment
# ══════════════════════════════════════════════════════════════════════

def run_experiment(model_name: str = "Qwen/Qwen3-0.6B", device: str = "cpu"):
    """Run the full symbol isolation experiment."""

    log(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    # Use float16 for large models (27B+ needs ~54 GB at fp16)
    dtype = torch.float16 if "27B" in model_name or "14B" in model_name else torch.float32
    log(f"Loading with dtype={dtype} on device={device}")
    model = AutoModelForCausalLM.from_pretrained(
        model_name, trust_remote_code=True, torch_dtype=dtype,
    )
    model.eval()
    model.to(device)

    n_layers = model.config.num_hidden_layers
    d_ff = model.config.intermediate_size
    log(f"Model: {n_layers} layers, d_ff={d_ff}")

    # Load combinator fingerprints
    slug = model_name.replace("/", "_")
    fp_path = HOLOGRAM_DIR / slug / f"fingerprints_{slug}.npz"
    if not fp_path.exists():
        log(f"ERROR: No fingerprints at {fp_path}")
        log(f"Run hologram_reader.py on {model_name} first.")
        sys.exit(1)

    fp_data = np.load(fp_path)
    fingerprints = {}
    for op in ALL_OP_NAMES:
        if op in fp_data:
            fingerprints[op] = fp_data[op]  # (n_layers, d_ff)
    log(f"Loaded {len(fingerprints)} combinator fingerprints")

    # Compute zone boundaries for this model
    zones = []
    for name, start_frac, end_frac in ZONE_FRACS:
        start_layer = int(start_frac * n_layers)
        end_layer = int(end_frac * n_layers)
        zones.append((name, start_layer, end_layer))
    log(f"Zones: {[(n, s, e) for n, s, e in zones]}")

    # Build probes
    categories = build_probes()
    log(f"Probe categories: {list(categories.keys())}")
    for cat_name, probes in categories.items():
        log(f"  {cat_name}: {len(probes)} probes")

    # Register hooks — capture hidden state after each layer (d_model space)
    # Fingerprints are in d_model space (built from down_proj output by hologram reader)
    hook = LayerOutputHook(n_layers)
    hook.register(model)
    log(f"Registered hooks on {n_layers} layers (d_model={model.config.hidden_size})")

    # Run all probes, collect per-category combinator energy
    results = {}
    op_names_ordered = sorted(fingerprints.keys())

    for cat_name, probes in categories.items():
        log(f"Running {cat_name}...")

        # Per-layer, per-combinator energy accumulator
        layer_op_energy = np.zeros((n_layers, len(fingerprints)), dtype=np.float64)
        n_probes = 0

        for probe in probes:
            text = probe["text"]
            input_ids = tokenizer.encode(text, return_tensors="pt").to(device)

            hook.clear()
            with torch.no_grad():
                model(input_ids)

            hidden_states = hook.get_hidden_states()

            for li in range(n_layers):
                if li not in hidden_states:
                    continue
                h = hidden_states[li]  # (d_model,) — same space as fingerprints

                for oi, op_name in enumerate(op_names_ordered):
                    fp = fingerprints[op_name][li]  # (d_model,)
                    # Cosine projection energy: (h · fp)² / (||fp||²)
                    dot = float(np.dot(h, fp))
                    fp_norm_sq = float(np.dot(fp, fp))
                    if fp_norm_sq > 1e-10:
                        energy = dot * dot / fp_norm_sq
                    else:
                        energy = 0.0
                    layer_op_energy[li, oi] += energy

            n_probes += 1

        # Average over probes
        if n_probes > 0:
            layer_op_energy /= n_probes

        # Aggregate by zone
        zone_profiles = {}
        for zone_name, start_l, end_l in zones:
            zone_energy = layer_op_energy[start_l:end_l].mean(axis=0)
            total = zone_energy.sum()
            profile = {
                op_names_ordered[i]: float(zone_energy[i])
                for i in range(len(op_names_ordered))
            }
            profile["_total"] = float(total)
            profile["_dominant"] = op_names_ordered[int(np.argmax(zone_energy))]
            zone_profiles[zone_name] = profile

        # Total across all layers
        total_energy = layer_op_energy.sum(axis=0)
        total_sum = total_energy.sum()
        total_profile = {
            op_names_ordered[i]: float(total_energy[i])
            for i in range(len(op_names_ordered))
        }
        total_profile["_total"] = float(total_sum)
        total_profile["_dominant"] = op_names_ordered[int(np.argmax(total_energy))]

        results[cat_name] = {
            "n_probes": n_probes,
            "zone_profiles": zone_profiles,
            "total_profile": total_profile,
            "layer_op_energy": layer_op_energy.tolist(),
        }

    hook.remove()

    # ── Report ────────────────────────────────────────────────────
    log("")
    log("=" * 80)
    log("SYMBOL ISOLATION RESULTS")
    log("=" * 80)

    # Table: total combinator energy per category
    log("")
    log(f"{'Category':<16} {'Total Energy':>12} {'ENRICH':>12} {'Dominant':>14} {'B':>8} {'K':>8} {'I':>8} {'β_apply':>8}")
    log("-" * 96)

    # Use PURE_PROSE as baseline
    baseline_total = results["PURE_PROSE"]["total_profile"]["_total"]

    for cat_name in ["PURE_PROSE", "NL_FACT", "PROSE_EQUALS", "EQUALS_ONLY",
                     "PROSE_ARROW", "GATED_PROSE", "LAMBDA_NO_EQ", "LAMBDA_EQ"]:
        r = results[cat_name]
        tp = r["total_profile"]
        ep = r["zone_profiles"].get("ENRICH", {})
        ratio = tp["_total"] / baseline_total if baseline_total > 0 else 0

        b_val = tp.get("B", 0)
        k_val = tp.get("K", 0)
        i_val = tp.get("I", 0)
        ba_val = tp.get("beta_apply", 0)
        enrich_total = ep.get("_total", 0)

        log(f"{cat_name:<16} {tp['_total']:>10.1f} ({ratio:>4.1f}x) "
            f"{enrich_total:>10.1f}  {tp['_dominant']:>14} "
            f"{b_val:>8.1f} {k_val:>8.1f} {i_val:>8.1f} {ba_val:>8.1f}")

    log("")
    log("Key comparisons:")
    log(f"  PURE_PROSE vs LAMBDA_EQ:     Does prose activate the same circuitry?")
    log(f"  PURE_PROSE vs PROSE_EQUALS:  Is '=' the trigger?")
    log(f"  NL_FACT vs EQUALS_ONLY:      Is '=' the trigger (factual)?")
    log(f"  LAMBDA_EQ vs LAMBDA_NO_EQ:   Does '=' matter for lambda?")
    log(f"  PURE_PROSE vs GATED_PROSE:   Does the compile gate matter?")
    log(f"  PURE_PROSE vs PROSE_ARROW:   Does '→' matter?")

    # Zone breakdown for key comparisons
    log("")
    log("ENRICH zone breakdown (the reduction engine):")
    enrich_ops = ["B", "K", "I", "C", "D", "Y", "beta_apply", "beta_compose"]
    header = f"{'Category':<16} " + "".join(f"{op:>12}" for op in enrich_ops)
    log(header)
    log("-" * len(header))
    for cat_name in ["PURE_PROSE", "NL_FACT", "PROSE_EQUALS", "EQUALS_ONLY",
                     "GATED_PROSE", "LAMBDA_NO_EQ", "LAMBDA_EQ"]:
        ep = results[cat_name]["zone_profiles"].get("ENRICH", {})
        row = f"{cat_name:<16} " + "".join(f"{ep.get(op, 0):>12.2f}" for op in enrich_ops)
        log(row)

    # ── Save results ──────────────────────────────────────────────
    out_dir = RESULTS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    output = {
        "model": model_name,
        "n_layers": n_layers,
        "d_ff": d_ff,
        "zones": [(n, s, e) for n, s, e in zones],
        "op_names": op_names_ordered,
        "categories": {
            cat: {
                "n_probes": r["n_probes"],
                "zone_profiles": r["zone_profiles"],
                "total_profile": r["total_profile"],
            }
            for cat, r in results.items()
        },
    }

    out_path = out_dir / "symbol_isolation_results.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    log(f"\nResults saved to {out_path}")

    # Save full layer×op energy matrices for post-hoc analysis
    np.savez_compressed(
        out_dir / "layer_op_energy.npz",
        **{cat: np.array(r["layer_op_energy"]) for cat, r in results.items()},
    )
    log(f"Layer×op energy saved to {out_dir / 'layer_op_energy.npz'}")


def main():
    p = argparse.ArgumentParser(description="Symbol isolation experiment")
    p.add_argument("--model", default="Qwen/Qwen3.6-27B", help="HuggingFace model name")
    p.add_argument("--device", default="mps", help="Device (cpu/mps/cuda)")
    args = p.parse_args()

    run_experiment(model_name=args.model, device=args.device)


if __name__ == "__main__":
    main()
