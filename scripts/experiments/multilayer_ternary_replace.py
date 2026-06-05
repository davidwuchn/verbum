#!/usr/bin/env python3
"""Test: replace ALL zone-B FFN layers simultaneously with tiny classifiers.

Single-layer replacement (psi s192) achieved 1638× compression with PPL
improvement. This test answers: does it hold when replacing MULTIPLE layers
at once, or do errors cascade?

Test matrix:
  1. Individual layers (confirm psi results)
  2. Cumulative: add one layer at a time (detect cascade threshold)
  3. All zone-B at once (the make-or-break test)
  4. Zone-B + EXPAND layers (how far can we push?)
  5. ALL layers (the limit test)

Method per layer:
  - Collect FFN (input, output) pairs from calibration data
  - Cluster outputs into 9 modes via K-means
  - Train tiny linear classifier: mlp_input → mode_id
  - Replacement: classify(x) → ternary[mode] × gamma

Usage:
  uv run python scripts/experiments/multilayer_ternary_replace.py \
    --model Qwen/Qwen3-8B --device mps

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

from verbum.probes.library import crystal_probes


# ══════════════════════════════════════════════════════════════════════
# Prompts
# ══════════════════════════════════════════════════════════════════════

FACT_PROMPTS = [
    {"prompt": "The capital of France is", "expected": "Paris"},
    {"prompt": "The capital of Japan is", "expected": "Tokyo"},
    {"prompt": "Water boils at", "expected": "100"},
    {"prompt": "The speed of light is approximately", "expected": "300"},
    {"prompt": "The first president of the United States was", "expected": "George Washington"},
    {"prompt": "The year World War II ended was", "expected": "1945"},
    {"prompt": "The chemical symbol for gold is", "expected": "Au"},
    {"prompt": "The largest planet in our solar system is", "expected": "Jupiter"},
    {"prompt": "The author of Romeo and Juliet is", "expected": "Shakespeare"},
    {"prompt": "Pi is approximately equal to", "expected": "3.14"},
    {"prompt": "The Great Wall of China is located in", "expected": "China"},
    {"prompt": "The human body has", "expected": "206"},
    {"prompt": "Einstein's famous equation is E equals", "expected": "mc"},
    {"prompt": "The freezing point of water in Celsius is", "expected": "0"},
    {"prompt": "The currency of the United Kingdom is the", "expected": "pound"},
]

CALIBRATION_TEXTS = [
    "The theory of general relativity describes gravity as the curvature of spacetime.",
    "In a large mixing bowl, combine the flour, sugar, and baking powder.",
    "The committee voted unanimously to approve the new environmental regulations.",
    "She walked through the ancient forest, her footsteps muffled by fallen leaves.",
    "The function takes two arguments and returns their composition.",
    "During the Cambrian explosion, most major animal phyla appeared in the fossil record.",
    "The patient was admitted with acute respiratory distress and fever.",
    "To solve this equation, first isolate the variable on one side.",
    "The Renaissance began in Italy in the 14th century and spread across Europe.",
    "Photosynthesis converts carbon dioxide and water into glucose and oxygen.",
    "The stock market experienced significant volatility during the trading session.",
    "Machine learning algorithms can be categorized as supervised or unsupervised.",
    "The Amazon rainforest produces approximately 20 percent of the world's oxygen.",
    "Shakespeare wrote 37 plays and 154 sonnets during his literary career.",
    "The Pythagorean theorem states that a squared plus b squared equals c squared.",
    "Climate change is caused primarily by the burning of fossil fuels.",
    "The human brain contains approximately 86 billion neurons.",
    "Democracy originated in ancient Greece, specifically in the city-state of Athens.",
    "DNA carries genetic information in a double helix structure.",
    "The Industrial Revolution began in Britain in the late 18th century.",
    "Quantum mechanics describes the behavior of particles at the atomic scale.",
    "The Nile is the longest river in Africa, flowing through eleven countries.",
    "Mozart composed his first symphony at the age of eight.",
    "The periodic table organizes chemical elements by atomic number.",
    "Gravity on the Moon is about one-sixth of Earth's gravitational pull.",
    "The French Revolution began in 1789 with the storming of the Bastille.",
    "Antibiotics were discovered by Alexander Fleming in 1928.",
    "The speed of sound in air is approximately 343 meters per second.",
    "Venus is the hottest planet in our solar system despite not being closest to the Sun.",
    "The Great Barrier Reef is the world's largest coral reef system.",
    "The Eiffel Tower was built for the 1889 World's Fair in Paris.",
    "The mitochondria is often called the powerhouse of the cell.",
    "Abraham Lincoln delivered the Gettysburg Address in 1863.",
    "The Pacific Ocean is the largest and deepest ocean on Earth.",
    "Beethoven composed his Ninth Symphony while completely deaf.",
    "The Magna Carta was signed in 1215 by King John of England.",
    "Insulin was first used to treat diabetes in 1922.",
    "Mount Everest is the tallest mountain above sea level at 8,849 meters.",
    "The printing press was invented by Johannes Gutenberg around 1440.",
    "Mars is known as the Red Planet due to iron oxide on its surface.",
]

EVAL_TEXTS = [
    "The theory of general relativity describes gravity as the curvature of spacetime caused by mass and energy. Einstein published this theory in 1915, fundamentally changing our understanding of the universe.",
    "In a large mixing bowl, combine the flour, sugar, and baking powder. Make a well in the center and add the eggs, milk, and melted butter.",
    "The committee voted unanimously to approve the new environmental regulations for manufacturing plants.",
    "She walked through the ancient forest, her footsteps muffled by centuries of fallen leaves.",
    "The function takes two arguments and returns their composition as a new callable object.",
    "During the Cambrian explosion, roughly 541 million years ago, most major animal phyla appeared.",
    "The patient was admitted with acute respiratory distress. Initial blood work showed elevated levels.",
    "To solve this equation, first isolate the variable on one side by subtracting three from both sides.",
]


# ══════════════════════════════════════════════════════════════════════
# Architecture helpers
# ══════════════════════════════════════════════════════════════════════

def get_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def get_zone_layers(n_layers: int) -> dict:
    """Return layer indices for each zone.
    
    EXPAND:  0 to 0.17n  (type assignment, feature building)
    ORTHO:   0.17n to 0.61n  (composition in null space)
    ZONE_B:  0.28n to 0.69n  (middle 30-70%, overlaps ORTHO + early ALIGN)
    ALIGN:   0.61n to 0.94n  (binding + final reductions)
    COLLAPSE: last layer
    """
    return {
        'expand': list(range(0, max(1, int(n_layers * 0.17)))),
        'ortho_early': list(range(int(n_layers * 0.17), int(n_layers * 0.28))),
        'zone_b': sorted(set(
            np.linspace(int(n_layers * 0.28), int(n_layers * 0.69),
                        min(4, int(n_layers * 0.41) + 1), dtype=int).tolist()
        )),
        'align': list(range(int(n_layers * 0.69), int(n_layers * 0.94))),
        'collapse': [n_layers - 1],
    }


# ══════════════════════════════════════════════════════════════════════
# Tiny classifier FFN replacement
# ══════════════════════════════════════════════════════════════════════

class TinyClassifierFFN(torch.nn.Module):
    """FFN replaced by: tiny linear classifier → ternary lookup."""

    def __init__(self, classifier_weight, ternary_patterns, gamma_patterns):
        super().__init__()
        self.register_buffer('classifier', torch.tensor(classifier_weight, dtype=torch.float32))
        self.register_buffer('ternary', torch.tensor(ternary_patterns, dtype=torch.float32))
        self.register_buffer('gamma', torch.tensor(gamma_patterns, dtype=torch.float32))

    def forward(self, x):
        orig_shape = x.shape
        x_flat = x.reshape(-1, x.shape[-1]).float()
        logits = x_flat @ self.classifier.T
        mode = logits.argmax(dim=-1)
        output = self.ternary[mode] * self.gamma[mode]
        return output.to(x.dtype).reshape(orig_shape)


def collect_layer_data(model, tokenizer, target_layer, device, texts, n_crystal=150):
    """Collect (mlp_input, mlp_output) pairs for one layer."""
    layers = get_layers(model)
    mlp = layers[target_layer].mlp
    captured = {}

    def pre_hook(module, input):
        x = input[0] if isinstance(input, tuple) else input
        captured['input'] = x.detach().float()

    def post_hook(module, input, output):
        captured['output'] = output.detach().float()

    h_pre = mlp.register_forward_pre_hook(pre_hook)
    h_post = mlp.register_forward_hook(post_hook)

    all_inputs = []
    all_outputs = []

    all_prompts = texts.copy()
    probes = crystal_probes()
    all_prompts.extend([p.prompt for p in probes[:n_crystal]])
    all_prompts.extend([f["prompt"] for f in FACT_PROMPTS])

    for prompt in all_prompts:
        captured.clear()
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            model(**inputs)
        if 'input' in captured and 'output' in captured:
            inp = captured['input'][0].cpu().numpy()
            out = captured['output'][0].cpu().numpy()
            if len(inp) > 32:
                idx = np.linspace(0, len(inp) - 1, 32, dtype=int)
                inp, out = inp[idx], out[idx]
            all_inputs.append(inp)
            all_outputs.append(out)

    h_pre.remove()
    h_post.remove()
    return np.concatenate(all_inputs), np.concatenate(all_outputs)


def train_classifier(inputs, labels, n_modes, n_epochs=100, lr=0.01):
    """Train a linear classifier: input → mode_id."""
    d_model = inputs.shape[1]
    X = torch.tensor(inputs, dtype=torch.float32)
    Y = torch.tensor(labels, dtype=torch.long)

    W = torch.randn(n_modes, d_model) * 0.01
    W.requires_grad_(True)
    optimizer = torch.optim.Adam([W], lr=lr)

    best_acc = 0
    best_W = None
    for epoch in range(n_epochs):
        logits = X @ W.T
        loss = F.cross_entropy(logits, Y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        with torch.no_grad():
            acc = (logits.argmax(dim=-1) == Y).float().mean().item()
            if acc > best_acc:
                best_acc = acc
                best_W = W.detach().clone()

    return best_W.numpy(), best_acc


def build_layer_replacement(mlp_inputs, mlp_outputs, n_modes=9):
    """Build a TinyClassifierFFN for one layer."""
    from sklearn.cluster import MiniBatchKMeans

    kmeans = MiniBatchKMeans(
        n_clusters=n_modes, random_state=42,
        batch_size=min(64, len(mlp_outputs)))
    labels = kmeans.fit_predict(mlp_outputs)

    d_model = mlp_outputs.shape[1]
    ternary_patterns = np.zeros((n_modes, d_model))
    gamma_patterns = np.zeros((n_modes, d_model))
    for i in range(n_modes):
        mask = labels == i
        if mask.sum() == 0:
            continue
        centroid = mlp_outputs[mask].mean(axis=0)
        ternary_patterns[i] = np.sign(centroid)
        gamma_patterns[i] = np.abs(centroid)

    classifier_W, train_acc = train_classifier(mlp_inputs, labels, n_modes)
    return TinyClassifierFFN(classifier_W, ternary_patterns, gamma_patterns), train_acc


# ══════════════════════════════════════════════════════════════════════
# Measurement
# ══════════════════════════════════════════════════════════════════════

def measure_ppl(model, tokenizer, texts, device):
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        labels = inputs["input_ids"].clone()
        with torch.no_grad():
            outputs = model(**inputs, labels=labels)
            total_loss += outputs.loss.item() * labels.numel()
            total_tokens += labels.numel()
    return np.exp(total_loss / total_tokens)


def generate_text(model, tokenizer, prompt, max_new_tokens=30, device="cpu"):
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            do_sample=False, temperature=1.0,
            pad_token_id=tokenizer.pad_token_id)
    generated = outputs[0][inputs['input_ids'].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True)


def check_fact(generated, expected):
    return expected.lower() in generated.lower()


def measure_facts(model, tokenizer, device):
    correct = 0
    details = {}
    for fp in FACT_PROMPTS:
        gen = generate_text(model, tokenizer, fp["prompt"], device=device)
        hit = check_fact(gen, fp["expected"])
        correct += int(hit)
        details[fp["prompt"]] = {"generated": gen[:80], "hit": hit}
    return correct / len(FACT_PROMPTS), details


def install_hooks(model, replacements, device):
    """Install replacement hooks for multiple layers. Returns list of handles."""
    layers = get_layers(model)
    handles = []
    for layer_idx, replacement in replacements.items():
        repl = replacement.to(device)
        mlp = layers[layer_idx].mlp

        def make_hook(r):
            def hook_fn(module, input, output):
                x = input[0] if isinstance(input, tuple) else input
                return r(x)
            return hook_fn

        handle = mlp.register_forward_hook(make_hook(repl))
        handles.append(handle)
    return handles


def remove_hooks(handles):
    for h in handles:
        h.remove()


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--n-modes", type=int, default=9,
                   help="Number of ternary modes per layer")
    p.add_argument("--skip-individual", action="store_true",
                   help="Skip individual layer tests (jump to multi-layer)")
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  MULTI-LAYER TERNARY REPLACEMENT TEST")
    print(f"  If the system is holographic, the core seed works at any scale")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print(f"  Modes per layer: {args.n_modes}")
    print()

    # Load model
    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    print(f"  Loading {args.model}...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    intermediate = model.config.intermediate_size
    zones = get_zone_layers(n_layers)

    print(f"  Layers: {n_layers}, d_model: {d_model}, intermediate: {intermediate}")
    print(f"  Zone B layers: {zones['zone_b']}")
    print(f"  EXPAND layers: {zones['expand']}")
    print(f"  All zones: {zones}")

    # Per-layer FFN size
    orig_layer_params = d_model * intermediate * 3
    orig_layer_mb = orig_layer_params * 2 / 1024 / 1024
    classifier_params = d_model * args.n_modes
    repl_kb = (classifier_params * 2 + args.n_modes * d_model * 3) / 1024  # approx

    # ── Baseline ──────────────────────────────────────────────────
    print(f"\n  Measuring baseline...")
    baseline_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    baseline_fact_rate, baseline_facts = measure_facts(model, tokenizer, args.device)
    print(f"  Baseline PPL: {baseline_ppl:.4f}")
    print(f"  Baseline facts: {baseline_fact_rate:.0%} ({int(baseline_fact_rate * len(FACT_PROMPTS))}/{len(FACT_PROMPTS)})")

    # ── Phase 1: Build all replacements ───────────────────────────
    # We build replacements for zone_b + expand + a few more
    # Important: collect data from the UNMODIFIED model (no hooks active)
    # so each layer's classifier sees the original distribution.

    test_layers = sorted(set(zones['zone_b'] + zones['expand']))
    # Also add layers just outside zone B for boundary testing
    zone_b_min = min(zones['zone_b'])
    zone_b_max = max(zones['zone_b'])
    for extra in [zone_b_min - 1, zone_b_max + 1, zone_b_max + 2]:
        if 0 <= extra < n_layers - 1:  # skip last layer (collapse)
            test_layers.append(extra)
    test_layers = sorted(set(test_layers))

    print(f"\n  Building replacements for {len(test_layers)} layers: {test_layers}")
    layer_replacements = {}
    layer_accuracies = {}

    for li in test_layers:
        t0 = time.time()
        print(f"\n    Layer {li}: collecting data...", end="", flush=True)
        mlp_in, mlp_out = collect_layer_data(
            model, tokenizer, li, args.device, CALIBRATION_TEXTS, n_crystal=150)
        print(f" {len(mlp_in)} samples...", end="", flush=True)

        repl, acc = build_layer_replacement(mlp_in, mlp_out, n_modes=args.n_modes)
        layer_replacements[li] = repl
        layer_accuracies[li] = acc
        elapsed = time.time() - t0
        print(f" acc={acc:.1%} ({elapsed:.1f}s)")

    # ── Phase 2: Individual layer tests ───────────────────────────
    results = {
        "model": args.model,
        "n_layers": n_layers,
        "d_model": d_model,
        "intermediate": intermediate,
        "n_modes": args.n_modes,
        "baseline_ppl": float(baseline_ppl),
        "baseline_fact_rate": float(baseline_fact_rate),
        "orig_layer_mb": float(orig_layer_mb),
        "repl_layer_kb": float(repl_kb),
        "zones": {k: v for k, v in zones.items()},
        "layer_accuracies": {str(k): v for k, v in layer_accuracies.items()},
        "individual": [],
        "cumulative": [],
        "combinations": [],
    }

    if not args.skip_individual:
        print(f"\n{'='*70}")
        print(f"  PHASE 2: INDIVIDUAL LAYER REPLACEMENT")
        print(f"{'='*70}")

        for li in test_layers:
            handles = install_hooks(model, {li: layer_replacements[li]}, args.device)
            ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
            fact_rate, facts = measure_facts(model, tokenizer, args.device)
            remove_hooks(handles)

            ratio = ppl / baseline_ppl
            zone = ("EXPAND" if li in zones['expand'] else
                    "ZONE_B" if li in zones['zone_b'] else
                    "ALIGN" if li in zones['align'] else
                    "OTHER")
            status = "✓" if ratio <= 1.05 else "⚠" if ratio <= 1.20 else "✗"

            print(f"    {status} L{li:>2d} [{zone:>6s}]  PPL={ppl:>8.4f} ({ratio:>5.2f}×)  "
                  f"Facts={fact_rate:.0%}  ClsAcc={layer_accuracies[li]:.1%}")

            results["individual"].append({
                "layer": li,
                "zone": zone,
                "ppl": float(ppl),
                "ppl_ratio": float(ratio),
                "fact_rate": float(fact_rate),
                "classifier_acc": float(layer_accuracies[li]),
            })

    # ── Phase 3: Cumulative replacement ───────────────────────────
    print(f"\n{'='*70}")
    print(f"  PHASE 3: CUMULATIVE REPLACEMENT (add one layer at a time)")
    print(f"{'='*70}")

    # Zone B cumulative
    cumul_layers = []
    for li in zones['zone_b']:
        cumul_layers.append(li)
        active = {l: layer_replacements[l] for l in cumul_layers}
        handles = install_hooks(model, active, args.device)
        ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
        fact_rate, facts = measure_facts(model, tokenizer, args.device)
        remove_hooks(handles)

        ratio = ppl / baseline_ppl
        n_replaced = len(cumul_layers)
        total_orig_mb = n_replaced * orig_layer_mb
        total_repl_kb = n_replaced * repl_kb
        compression = (total_orig_mb * 1024) / total_repl_kb if total_repl_kb > 0 else 0
        status = "✓" if ratio <= 1.10 else "⚠" if ratio <= 1.50 else "✗"

        label = "+".join(f"L{l}" for l in cumul_layers)
        print(f"    {status} {label:<30s}  PPL={ppl:>8.4f} ({ratio:>5.2f}×)  "
              f"Facts={fact_rate:.0%}  {total_orig_mb:.0f}MB→{total_repl_kb:.0f}KB ({compression:.0f}×)")

        results["cumulative"].append({
            "layers": list(cumul_layers),
            "label": label,
            "n_layers_replaced": n_replaced,
            "ppl": float(ppl),
            "ppl_ratio": float(ratio),
            "fact_rate": float(fact_rate),
            "orig_mb": float(total_orig_mb),
            "repl_kb": float(total_repl_kb),
            "compression": float(compression),
        })

    # ── Phase 4: Expand + Zone B ──────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  PHASE 4: EXPAND + ZONE B (push the boundary)")
    print(f"{'='*70}")

    # All zone B first
    combo_tests = [
        ("all_zone_b", zones['zone_b']),
        ("all_expand", zones['expand']),
        ("expand+zone_b", sorted(zones['expand'] + zones['zone_b'])),
    ]

    # Also test all layers we have replacements for
    combo_tests.append(("all_prepared", sorted(test_layers)))

    for label, layer_list in combo_tests:
        active = {l: layer_replacements[l] for l in layer_list if l in layer_replacements}
        if not active:
            continue

        handles = install_hooks(model, active, args.device)
        ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
        fact_rate, facts = measure_facts(model, tokenizer, args.device)
        remove_hooks(handles)

        ratio = ppl / baseline_ppl
        n_replaced = len(active)
        total_orig_mb = n_replaced * orig_layer_mb
        total_repl_kb = n_replaced * repl_kb
        compression = (total_orig_mb * 1024) / total_repl_kb if total_repl_kb > 0 else 0
        status = "✓" if ratio <= 1.10 else "⚠" if ratio <= 1.50 else "✗"

        layers_str = ",".join(f"L{l}" for l in sorted(active.keys()))
        print(f"    {status} {label:<20s} [{layers_str}]")
        print(f"      PPL={ppl:>8.4f} ({ratio:>5.2f}×)  Facts={fact_rate:.0%}")
        print(f"      {n_replaced} layers: {total_orig_mb:.0f}MB → {total_repl_kb:.0f}KB ({compression:.0f}×)")

        results["combinations"].append({
            "label": label,
            "layers": sorted(active.keys()),
            "n_layers_replaced": n_replaced,
            "ppl": float(ppl),
            "ppl_ratio": float(ratio),
            "fact_rate": float(fact_rate),
            "orig_mb": float(total_orig_mb),
            "repl_kb": float(total_repl_kb),
            "compression": float(compression),
            "fact_details": {k: {"hit": v["hit"]} for k, v in facts.items()},
        })

    # ── Phase 5: Extended scan (all remaining layers) ─────────────
    print(f"\n{'='*70}")
    print(f"  PHASE 5: FULL-DEPTH SCAN (one layer at a time, all layers)")
    print(f"{'='*70}")

    # Build replacements for ALL layers we haven't already done
    all_layers_to_scan = [l for l in range(n_layers) if l not in layer_replacements]
    if all_layers_to_scan:
        print(f"  Building replacements for {len(all_layers_to_scan)} remaining layers...")
        for li in all_layers_to_scan:
            t0 = time.time()
            print(f"    Layer {li}: ", end="", flush=True)
            mlp_in, mlp_out = collect_layer_data(
                model, tokenizer, li, args.device, CALIBRATION_TEXTS, n_crystal=100)
            repl, acc = build_layer_replacement(mlp_in, mlp_out, n_modes=args.n_modes)
            layer_replacements[li] = repl
            layer_accuracies[li] = acc
            elapsed = time.time() - t0
            print(f"acc={acc:.1%} ({elapsed:.1f}s)")

        results["layer_accuracies"] = {str(k): v for k, v in layer_accuracies.items()}

    # Individual scan of remaining layers
    full_scan = []
    for li in sorted(layer_replacements.keys()):
        # Skip if already measured individually
        if any(r["layer"] == li for r in results["individual"]):
            existing = [r for r in results["individual"] if r["layer"] == li][0]
            full_scan.append(existing)
            continue

        handles = install_hooks(model, {li: layer_replacements[li]}, args.device)
        ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
        fact_rate, _ = measure_facts(model, tokenizer, args.device)
        remove_hooks(handles)

        ratio = ppl / baseline_ppl
        zone = ("EXPAND" if li in zones['expand'] else
                "ZONE_B" if li in zones['zone_b'] else
                "ORTHO" if li in zones['ortho_early'] else
                "ALIGN" if li in zones['align'] else
                "COLLAPSE" if li in zones['collapse'] else
                "OTHER")
        status = "✓" if ratio <= 1.05 else "⚠" if ratio <= 1.20 else "✗"

        print(f"    {status} L{li:>2d} [{zone:>8s}]  PPL={ppl:>8.4f} ({ratio:>5.2f}×)  "
              f"Facts={fact_rate:.0%}  ClsAcc={layer_accuracies[li]:.1%}")

        entry = {
            "layer": li,
            "zone": zone,
            "ppl": float(ppl),
            "ppl_ratio": float(ratio),
            "fact_rate": float(fact_rate),
            "classifier_acc": float(layer_accuracies[li]),
        }
        full_scan.append(entry)

    results["full_scan"] = full_scan

    # ── Phase 6: All-layer replacement ────────────────────────────
    print(f"\n{'='*70}")
    print(f"  PHASE 6: ALL-LAYER REPLACEMENT (the ultimate test)")
    print(f"{'='*70}")

    all_active = {l: layer_replacements[l] for l in range(n_layers)
                  if l in layer_replacements}
    handles = install_hooks(model, all_active, args.device)
    ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    fact_rate, facts = measure_facts(model, tokenizer, args.device)
    remove_hooks(handles)

    ratio = ppl / baseline_ppl
    n_all = len(all_active)
    total_orig_mb = n_all * orig_layer_mb
    total_repl_kb = n_all * repl_kb
    compression = (total_orig_mb * 1024) / total_repl_kb if total_repl_kb > 0 else 0

    print(f"    ALL {n_all} LAYERS REPLACED")
    print(f"    PPL: {ppl:.4f} ({ratio:.2f}× baseline)")
    print(f"    Facts: {fact_rate:.0%}")
    print(f"    {total_orig_mb:.0f}MB → {total_repl_kb:.0f}KB ({compression:.0f}×)")

    results["all_layers"] = {
        "layers": sorted(all_active.keys()),
        "n_layers_replaced": n_all,
        "ppl": float(ppl),
        "ppl_ratio": float(ratio),
        "fact_rate": float(fact_rate),
        "orig_mb": float(total_orig_mb),
        "repl_kb": float(total_repl_kb),
        "compression": float(compression),
        "fact_details": {k: {"hit": v["hit"], "generated": v["generated"]} for k, v in facts.items()},
    }

    # ── Summary ───────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"  Baseline: PPL={baseline_ppl:.4f}, Facts={baseline_fact_rate:.0%}")
    print(f"  Per-layer FFN: {orig_layer_mb:.0f}MB → {repl_kb:.0f}KB ({orig_layer_mb*1024/repl_kb:.0f}×)")
    print()

    if results["cumulative"]:
        print(f"  Cumulative zone-B replacement:")
        for c in results["cumulative"]:
            print(f"    {c['label']:<30s}  {c['ppl_ratio']:>5.2f}×  Facts={c['fact_rate']:.0%}")
        print()

    if results["combinations"]:
        print(f"  Combination tests:")
        for c in results["combinations"]:
            print(f"    {c['label']:<20s} ({c['n_layers_replaced']:>2d} layers)  "
                  f"{c['ppl_ratio']:>5.2f}×  Facts={c['fact_rate']:.0%}  "
                  f"{c['orig_mb']:.0f}MB→{c['repl_kb']:.0f}KB")
        print()

    if "all_layers" in results:
        a = results["all_layers"]
        print(f"  ALL LAYERS ({a['n_layers_replaced']}):  {a['ppl_ratio']:.2f}×  "
              f"Facts={a['fact_rate']:.0%}  "
              f"{a['orig_mb']:.0f}MB→{a['repl_kb']:.0f}KB ({a['compression']:.0f}×)")

    # ── Save ──────────────────────────────────────────────────────
    out_dir = Path("results/multilayer-ternary-replace")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
