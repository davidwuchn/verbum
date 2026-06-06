#!/usr/bin/env python3
"""Confidence-Gated Inference — the student knows when it's wrong.

The ternary classifier already computes logits to select a mode.
The MARGIN between top-1 and top-2 logits is a confidence signal:
  high margin → classifier is sure → ternary output is reliable
  low margin  → classifier is unsure → fall back to original MLP

This experiment measures the tradeoff: at each confidence threshold,
what % of positions take the slow path, and what PPL do we get?

The hook design is zero-overhead for measurement: the original MLP
has already run (its output is `out` in the hook), and the ternary
replacement is cheap. We just gate between them.

For deployment, only the slow-path positions would run the full MLP.
The rest use the 180KB ternary lookup. If 95% of positions are
confident, effective cost = 0.05 × full_MLP + 0.95 × ternary_lookup.

Experiments:
  1. Per-layer margin distribution: what does confidence look like?
  2. Threshold sweep: PPL vs % slow-path at various thresholds
  3. Per-combinator: do crystal probes show combinator-specific patterns?
  4. Sweet spot (L13-L21) vs binding-prep (L22-L26): where is gating needed?

Usage:
  uv run python scripts/experiments/confidence_gate.py \
    --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.cluster import MiniBatchKMeans
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from verbum.probes.library import crystal_probes


# ══════════════════════════════════════════════════════════════
# Texts
# ══════════════════════════════════════════════════════════════

CALIBRATION_TEXTS = [
    "The theory of general relativity describes gravity as"
    " the curvature of spacetime.",
    "Photosynthesis converts carbon dioxide and water into"
    " glucose and oxygen.",
    "DNA carries genetic information in a double helix"
    " structure discovered by Watson and Crick.",
    "Quantum mechanics describes the behavior of particles"
    " at the atomic and subatomic scale.",
    "The human brain contains approximately 86 billion"
    " neurons connected by trillions of synapses.",
    "Black holes form when massive stars collapse under"
    " their own gravitational force.",
    "She walked through the ancient forest, her footsteps"
    " muffled by fallen leaves.",
    "The old man sat quietly by the river, watching the"
    " fish jump at dawn.",
    "Three children ran laughing through the sunlit meadow"
    " while their dog chased butterflies.",
    "He opened the letter carefully, his hands trembling"
    " with anticipation.",
    "In a large mixing bowl, combine the flour, sugar,"
    " and baking powder.",
    "To solve this equation, first isolate the variable"
    " on one side.",
    "Install the software by running the setup wizard and"
    " following the prompts.",
    "The committee voted unanimously to approve the new"
    " environmental regulations.",
    "Democracy originated in ancient Greece, specifically"
    " in the city-state of Athens.",
    "The function takes two arguments and returns their"
    " composition as a new callable.",
    "Machine learning algorithms can be categorized as"
    " supervised or unsupervised.",
    "Arrays are contiguous blocks of memory that allow"
    " constant-time access by index.",
    "What time does the store close today?",
    "I think we should probably leave now before it gets"
    " too dark outside.",
    "The book that the professor recommended, which had"
    " been out of print for decades, was finally reissued.",
    "Although the experiment failed initially, the"
    " researchers persisted and eventually found"
    " the solution.",
    "The primary colors are red, blue, and yellow.",
    "The Fibonacci sequence begins with 1, 1, 2, 3, 5,"
    " 8, 13, 21.",
    "Pi is approximately equal to 3.14159265 and is an"
    " irrational number.",
    "The periodic table organizes elements by atomic"
    " number and electron configuration.",
    "Enzymes are biological catalysts that speed up"
    " chemical reactions in living organisms.",
    "The ship sailed slowly into the harbor as the storm"
    " clouds gathered on the horizon.",
    "The detective examined the crime scene, noting every"
    " detail with practiced precision.",
    "Birds sang in the treetops as morning light filtered"
    " through the canopy above.",
    "The Supreme Court ruled that the legislation was"
    " constitutional.",
]

EVAL_TEXTS = [
    "The theory of general relativity describes gravity"
    " as the curvature of spacetime caused by mass and"
    " energy.",
    "In a large mixing bowl, combine the flour, sugar,"
    " and baking powder. Make a well in the center.",
    "The committee voted unanimously to approve the new"
    " environmental regulations for manufacturing plants.",
    "She walked through the ancient forest, her footsteps"
    " muffled by centuries of fallen leaves.",
    "The function takes two arguments and returns their"
    " composition as a new callable object.",
    "During the Cambrian explosion, roughly 541 million"
    " years ago, most major animal phyla appeared.",
    "The patient was admitted with acute respiratory"
    " distress. Initial blood work showed elevated levels.",
    "To solve this equation, first isolate the variable"
    " on one side by subtracting three from both sides.",
]

FACT_PROMPTS = [
    {"prompt": "The capital of France is", "expected": "Paris"},
    {"prompt": "The capital of Japan is", "expected": "Tokyo"},
    {"prompt": "Water boils at", "expected": "100"},
    {"prompt": "The speed of light is approximately",
     "expected": "300"},
    {"prompt": "The first president of the United States was",
     "expected": "George Washington"},
    {"prompt": "The year World War II ended was",
     "expected": "1945"},
    {"prompt": "The chemical symbol for gold is",
     "expected": "Au"},
    {"prompt": "The largest planet in our solar system is",
     "expected": "Jupiter"},
    {"prompt": "The author of Romeo and Juliet is",
     "expected": "Shakespeare"},
    {"prompt": "Pi is approximately equal to",
     "expected": "3.14"},
    {"prompt": "The Great Wall of China is located in",
     "expected": "China"},
    {"prompt": "The human body has", "expected": "206"},
    {"prompt": "Einstein's famous equation is E equals",
     "expected": "mc"},
    {"prompt": "The freezing point of water in Celsius is",
     "expected": "0"},
    {"prompt": "The currency of the United Kingdom is the",
     "expected": "pound"},
]


def log(msg=""):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


def get_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise RuntimeError(f"Can't find layers in {type(model)}")


def measure_ppl(model, tokenizer, texts, device):
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        enc = tokenizer(
            text, return_tensors="pt",
            truncation=True, max_length=256,
        )
        enc = {k: v.to(device) for k, v in enc.items()}
        labels = enc["input_ids"].clone()
        with torch.no_grad():
            out = model(**enc, labels=labels)
            total_loss += out.loss.item() * labels.numel()
            total_tokens += labels.numel()
    return float(np.exp(total_loss / total_tokens))


def generate_text(model, tokenizer, prompt, device, max_new=30):
    enc = tokenizer(prompt, return_tensors="pt")
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        out = model.generate(
            **enc, max_new_tokens=max_new,
            do_sample=False, temperature=1.0,
            pad_token_id=tokenizer.pad_token_id,
        )
    return tokenizer.decode(
        out[0][enc["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )


def measure_facts(model, tokenizer, device):
    correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(model, tokenizer, fp["prompt"], device)
        if fp["expected"].lower() in gen.lower():
            correct += 1
    return correct, len(FACT_PROMPTS)


# ══════════════════════════════════════════════════════════════
# Ternary classifier (captures margin for gating)
# ══════════════════════════════════════════════════════════════

class TernaryWithConfidence(torch.nn.Module):
    """Ternary FFN replacement that also records confidence margins."""

    def __init__(self, cls_w, ternary_signs, gamma):
        super().__init__()
        self.register_buffer(
            "classifier",
            torch.tensor(cls_w, dtype=torch.float32),
        )
        self.register_buffer(
            "ternary",
            torch.tensor(ternary_signs, dtype=torch.float32),
        )
        self.register_buffer(
            "gamma",
            torch.tensor(gamma, dtype=torch.float32),
        )
        # Diagnostics — populated during forward
        self.last_margins = None
        self.last_modes = None

    def forward(self, x):
        shape = x.shape
        xf = x.reshape(-1, x.shape[-1]).float()
        logits = xf @ self.classifier.T
        logits = logits.clamp(-20.0, 20.0)

        # Top-2 for confidence margin
        top2 = logits.topk(2, dim=-1)
        self.last_margins = (
            top2.values[:, 0] - top2.values[:, 1]
        ).detach()  # (n_positions,)
        self.last_modes = top2.indices[:, 0].detach()

        mode = logits.argmax(dim=-1)
        out = self.ternary[mode] * self.gamma[mode]
        return out.to(x.dtype).reshape(shape)


def collect_mlp_data(model, tokenizer, layer_idx, device,
                     texts, n_crystal=100):
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp
    captured = {}

    def pre_hook(module, inp):
        x = inp[0] if isinstance(inp, tuple) else inp
        captured["input"] = x.detach().float()

    def post_hook(module, inp, out):
        captured["output"] = out.detach().float()

    h1 = mlp.register_forward_pre_hook(pre_hook)
    h2 = mlp.register_forward_hook(post_hook)

    all_prompts = list(texts)
    probes = crystal_probes()
    all_prompts.extend([p.prompt for p in probes[:n_crystal]])

    all_in, all_out = [], []
    for prompt in all_prompts:
        captured.clear()
        enc = tokenizer(
            prompt, return_tensors="pt",
            truncation=True, max_length=128,
        )
        enc = {k: v.to(device) for k, v in enc.items()}
        with torch.no_grad():
            model(**enc)
        if "input" in captured and "output" in captured:
            inp = captured["input"][0].cpu().numpy()
            out = captured["output"][0].cpu().numpy()
            if len(inp) > 32:
                idx = np.linspace(
                    0, len(inp) - 1, 32, dtype=int,
                )
                inp, out = inp[idx], out[idx]
            all_in.append(inp)
            all_out.append(out)

    h1.remove()
    h2.remove()
    return (
        np.concatenate(all_in, axis=0),
        np.concatenate(all_out, axis=0),
    )


def train_classifier(inputs, labels, n_modes,
                     n_epochs=100, lr=0.01):
    d = inputs.shape[1]
    X = torch.tensor(inputs, dtype=torch.float32)
    Y = torch.tensor(labels, dtype=torch.long)
    W = torch.randn(n_modes, d) * 0.01
    W.requires_grad_(True)
    opt = torch.optim.Adam([W], lr=lr)
    best_acc, best_W = 0.0, None
    for _ in range(n_epochs):
        logits = X @ W.T
        loss = F.cross_entropy(logits, Y)
        opt.zero_grad()
        loss.backward()
        opt.step()
        with torch.no_grad():
            acc = float((logits.argmax(-1) == Y).float().mean())
            if acc > best_acc:
                best_acc = acc
                best_W = W.detach().clone()
    return best_W.numpy(), best_acc


def build_ternary(model, tokenizer, layer_idx, device,
                  d_model, n_modes=9):
    """Build ternary replacement for one layer. Returns module + acc."""
    mlp_in, mlp_out = collect_mlp_data(
        model, tokenizer, layer_idx, device,
        CALIBRATION_TEXTS,
    )
    km = MiniBatchKMeans(
        n_clusters=n_modes, random_state=42,
        batch_size=min(256, len(mlp_out)), n_init=5,
    )
    labels = km.fit_predict(mlp_out)

    ternary_signs = np.zeros((n_modes, d_model))
    gamma = np.zeros((n_modes, d_model))
    for i in range(n_modes):
        mask = labels == i
        if mask.sum() == 0:
            continue
        c = mlp_out[mask].mean(axis=0)
        ternary_signs[i] = np.sign(c)
        gamma[i] = np.abs(c)

    cls_W, cls_acc = train_classifier(mlp_in, labels, n_modes)
    replacement = TernaryWithConfidence(
        cls_W, ternary_signs, gamma,
    ).to(device)

    return replacement, cls_acc


# ══════════════════════════════════════════════════════════════
# Confidence-gated hook
# ══════════════════════════════════════════════════════════════

class GatedHook:
    """Hook that routes between ternary and original MLP by confidence.

    The hook intercepts MLP output. The original MLP has already run
    (output = `out`). We also compute the ternary output. Then gate:
      confidence > threshold → ternary (fast path)
      confidence ≤ threshold → original (slow path)

    Records routing statistics.
    """

    def __init__(self, replacement, threshold=0.0):
        self.replacement = replacement
        self.threshold = threshold
        # Accumulators
        self.total_positions = 0
        self.fast_positions = 0
        self.all_margins = []

    def reset_stats(self):
        self.total_positions = 0
        self.fast_positions = 0
        self.all_margins = []

    def __call__(self, module, inp, out):
        x = inp[0] if isinstance(inp, tuple) else inp

        # Compute ternary output + margins
        ternary_out = self.replacement(x)
        margins = self.replacement.last_margins  # (n_positions,)

        # Record margins
        self.all_margins.append(margins.cpu().numpy())

        if self.threshold <= 0:
            # Pure ternary mode (no gating)
            self.total_positions += margins.numel()
            self.fast_positions += margins.numel()
            return ternary_out

        # Gate: per-position routing
        shape = x.shape
        n_pos = margins.numel()
        mask = (margins > self.threshold)  # True = fast (ternary)

        self.total_positions += n_pos
        self.fast_positions += int(mask.sum().item())

        if mask.all():
            return ternary_out
        if not mask.any():
            return out  # all slow path

        # Mix: reshape for broadcasting
        # out shape: (batch, seq, d_model) or (seq, d_model)
        flat_ternary = ternary_out.reshape(-1, shape[-1])
        flat_orig = out.reshape(-1, shape[-1])
        mask_expanded = mask.unsqueeze(-1).expand_as(flat_ternary)

        result = torch.where(mask_expanded, flat_ternary, flat_orig)
        return result.reshape(shape)

    @property
    def fast_ratio(self):
        if self.total_positions == 0:
            return 0.0
        return self.fast_positions / self.total_positions


# ══════════════════════════════════════════════════════════════
# Experiments
# ══════════════════════════════════════════════════════════════

def run_threshold_sweep(model, tokenizer, device, layer_idx,
                        replacement, baseline_ppl,
                        thresholds, label=""):
    """Sweep confidence thresholds for one layer."""
    log(f"\n{'─'*60}")
    log(f"  Layer {layer_idx} ({label})")
    log(f"{'─'*60}")

    layers = get_layers(model)
    mlp = layers[layer_idx].mlp

    results = []

    for threshold in thresholds:
        gate = GatedHook(replacement, threshold)
        handle = mlp.register_forward_hook(gate)

        ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
        ppl_ratio = ppl / baseline_ppl
        fast_pct = gate.fast_ratio * 100

        # Margin statistics
        all_margins = np.concatenate(gate.all_margins)
        margin_stats = {
            "mean": float(np.mean(all_margins)),
            "std": float(np.std(all_margins)),
            "median": float(np.median(all_margins)),
            "p5": float(np.percentile(all_margins, 5)),
            "p25": float(np.percentile(all_margins, 25)),
            "p75": float(np.percentile(all_margins, 75)),
            "p95": float(np.percentile(all_margins, 95)),
        }

        marker = ""
        if ppl_ratio < 1.02:
            marker = " ★★"
        elif ppl_ratio < 1.05:
            marker = " ★"
        elif ppl_ratio < 1.10:
            marker = " ✓"

        log(f"    θ={threshold:>5.1f}: PPL={ppl:>8.2f}"
            f" ({ppl_ratio:>5.2f}x)"
            f"  fast={fast_pct:>5.1f}%"
            f"  slow={100-fast_pct:>5.1f}%{marker}")

        handle.remove()

        results.append({
            "threshold": threshold,
            "ppl": round(ppl, 4),
            "ppl_ratio": round(ppl_ratio, 4),
            "fast_pct": round(fast_pct, 2),
            "slow_pct": round(100 - fast_pct, 2),
            "total_positions": gate.total_positions,
            "margin_stats": margin_stats,
        })

    return results, all_margins


def run_margin_analysis(model, tokenizer, device, layer_idx,
                        replacement, label=""):
    """Analyze margin distribution for one layer."""
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp

    # Run with threshold=0 (pure ternary) to collect all margins
    gate = GatedHook(replacement, threshold=0.0)
    handle = mlp.register_forward_hook(gate)

    # Run on eval texts
    for text in EVAL_TEXTS:
        enc = tokenizer(
            text, return_tensors="pt",
            truncation=True, max_length=256,
        )
        enc = {k: v.to(device) for k, v in enc.items()}
        with torch.no_grad():
            model(**enc)

    handle.remove()

    all_margins = np.concatenate(gate.all_margins)
    return all_margins


def run_crystal_probe_margins(model, tokenizer, device,
                              layer_idx, replacement):
    """Run crystal probes and collect per-combinator margin stats."""
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp

    probes = crystal_probes()
    combinator_margins = defaultdict(list)

    gate = GatedHook(replacement, threshold=0.0)
    handle = mlp.register_forward_hook(gate)

    for probe in probes:
        gate.reset_stats()
        enc = tokenizer(
            probe.prompt, return_tensors="pt",
            truncation=True, max_length=128,
        )
        enc = {k: v.to(device) for k, v in enc.items()}
        with torch.no_grad():
            model(**enc)

        if gate.all_margins:
            margins = np.concatenate(gate.all_margins)
            combinator_margins[probe.combinator].append(
                float(np.mean(margins))
            )

    handle.remove()
    return dict(combinator_margins)


# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--n-modes", type=int, default=9)
    args = p.parse_args()

    log(f"\n{'='*70}")
    log("  CONFIDENCE-GATED INFERENCE")
    log("  The student knows when it's wrong")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")

    # ── Load ──────────────────────────────────────────────
    dtype = (
        torch.float16
        if any(s in args.model for s in ["8B", "14B", "32B"])
        else torch.float32
    )
    log(f"\n  Loading {args.model} ({dtype})...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device,
    )
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    d_model = model.config.hidden_size
    log(f"  d_model: {d_model}")

    # ── Baseline ──────────────────────────────────────────
    log("\n  Measuring baseline...")
    baseline_ppl = measure_ppl(
        model, tokenizer, EVAL_TEXTS, args.device,
    )
    base_correct, base_total = measure_facts(
        model, tokenizer, args.device,
    )
    log(f"  Baseline PPL: {baseline_ppl:.2f}")
    log(f"  Baseline facts: {base_correct}/{base_total}")

    # ── Build ternary replacements for target layers ──────
    target_layers = [
        (15, "sweet-spot"),
        (17, "sweet-spot"),
        (20, "sweet-spot (S/O crystal)"),
        (22, "binding-prep"),
        (23, "binding-prep (high rank)"),
        (24, "binding-prep"),
        (25, "binding-prep"),
        (26, "binding-prep (high rank)"),
    ]

    replacements = {}
    log("\n  Building ternary replacements...")
    for li, label in target_layers:
        repl, acc = build_ternary(
            model, tokenizer, li, args.device, d_model,
            args.n_modes,
        )
        replacements[li] = repl
        log(f"    L{li} ({label}): cls_acc={acc:.1%}")

    # ══════════════════════════════════════════════════════
    # Exp 1: Margin distribution per layer
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  EXP 1: MARGIN DISTRIBUTIONS")
    log(f"{'═'*70}")

    margin_data = {}
    for li, label in target_layers:
        margins = run_margin_analysis(
            model, tokenizer, args.device, li,
            replacements[li], label,
        )
        margin_data[li] = margins
        log(f"  L{li:>2d} ({label:>25s}):"
            f"  mean={np.mean(margins):>6.2f}"
            f"  std={np.std(margins):>6.2f}"
            f"  p5={np.percentile(margins, 5):>6.2f}"
            f"  p50={np.median(margins):>6.2f}"
            f"  p95={np.percentile(margins, 95):>6.2f}"
            f"  n={len(margins)}")

    # ══════════════════════════════════════════════════════
    # Exp 2: Threshold sweep per layer
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  EXP 2: THRESHOLD SWEEP")
    log(f"{'═'*70}")

    # Thresholds based on margin distributions
    thresholds = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 20.0]

    sweep_results = {}
    for li, label in target_layers:
        results, _ = run_threshold_sweep(
            model, tokenizer, args.device, li,
            replacements[li], baseline_ppl,
            thresholds, label,
        )
        sweep_results[li] = results

    # ── Find optimal operating point per layer ────────────
    log(f"\n  Optimal operating points (PPL < 1.02x):")
    log(f"  {'Layer':>6s}  {'θ':>5s}  {'PPL':>7s}  {'Fast%':>6s}"
        f"  {'Slow%':>6s}  {'Verdict':>10s}")
    log(f"  {'─'*6}  {'─'*5}  {'─'*7}  {'─'*6}  {'─'*6}  {'─'*10}")

    optimal_points = {}
    for li, label in target_layers:
        # Find lowest threshold that gives < 1.02x PPL
        best = None
        for r in sweep_results[li]:
            if r["ppl_ratio"] < 1.02:
                if best is None or r["fast_pct"] > best["fast_pct"]:
                    best = r
                break  # thresholds are ordered, take first good one

        # Also find < 1.05x
        best_05 = None
        for r in sweep_results[li]:
            if r["ppl_ratio"] < 1.05:
                if best_05 is None or r["fast_pct"] > best_05["fast_pct"]:
                    best_05 = r
                break

        if best:
            verdict = "EXCELLENT" if best["fast_pct"] > 95 else (
                "GOOD" if best["fast_pct"] > 80 else "MODERATE"
            )
            log(f"  L{li:>3d}  {best['threshold']:>5.1f}"
                f"  {best['ppl_ratio']:>5.2f}x"
                f"  {best['fast_pct']:>5.1f}%"
                f"  {best['slow_pct']:>5.1f}%"
                f"  {verdict:>10s}")
            optimal_points[li] = best
        elif best_05:
            log(f"  L{li:>3d}  {best_05['threshold']:>5.1f}"
                f"  {best_05['ppl_ratio']:>5.2f}x"
                f"  {best_05['fast_pct']:>5.1f}%"
                f"  {best_05['slow_pct']:>5.1f}%"
                f"  {'<1.05x only':>10s}")
            optimal_points[li] = best_05
        else:
            # Pure ternary result
            pure = sweep_results[li][0]  # threshold=0
            log(f"  L{li:>3d}  {'N/A':>5s}"
                f"  {pure['ppl_ratio']:>5.2f}x"
                f"  {'100.0':>5s}%"
                f"  {'0.0':>5s}%"
                f"  {'NO GATE OK':>10s}")
            optimal_points[li] = pure

    # ══════════════════════════════════════════════════════
    # Exp 3: Crystal probe margins
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  EXP 3: CRYSTAL PROBE MARGINS BY COMBINATOR")
    log(f"{'═'*70}")

    # Test on two contrasting layers
    probe_layers = [15, 23]  # sweet spot vs hardest binding-prep
    crystal_results = {}

    for li in probe_layers:
        comb_margins = run_crystal_probe_margins(
            model, tokenizer, args.device, li, replacements[li],
        )
        crystal_results[li] = comb_margins

        log(f"\n  L{li}:")
        combs = sorted(comb_margins.keys())
        for c in combs:
            vals = comb_margins[c]
            mean_m = np.mean(vals)
            std_m = np.std(vals)
            log(f"    {c:>6s}: mean_margin={mean_m:>6.2f}"
                f"  std={std_m:>5.2f}  n={len(vals)}")

    # ══════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  FINAL SUMMARY")
    log(f"{'='*70}")
    log(f"  Baseline: PPL={baseline_ppl:.2f}")

    log(f"\n  Per-layer: at optimal threshold for <1.05x PPL")
    log(f"  {'Layer':>6s}  {'Zone':>15s}  {'θ':>5s}  {'PPL':>7s}"
        f"  {'Fast':>6s}  {'Slow':>6s}")
    log(f"  {'─'*6}  {'─'*15}  {'─'*5}  {'─'*7}  {'─'*6}  {'─'*6}")

    total_fast = 0
    total_positions = 0
    for li, label in target_layers:
        if li in optimal_points:
            op = optimal_points[li]
            log(f"  L{li:>3d}  {label:>15s}"
                f"  {op.get('threshold', 0):>5.1f}"
                f"  {op['ppl_ratio']:>5.2f}x"
                f"  {op['fast_pct']:>5.1f}%"
                f"  {op['slow_pct']:>5.1f}%")

    log(f"\n  If 95% of positions take the fast path:")
    log(f"    Effective compute per layer = "
        f"0.95 × ternary_lookup + 0.05 × full_MLP")
    log(f"    Effective size per layer ≈ "
        f"0.95 × 180KB + 0.05 × 288MB = ~14.4MB")
    log(f"    vs full MLP: 288MB (20x effective compression)")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "confidence-gate"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    # Convert margin data to serializable format
    margin_summary = {}
    for li in margin_data:
        m = margin_data[li]
        margin_summary[str(li)] = {
            "mean": round(float(np.mean(m)), 4),
            "std": round(float(np.std(m)), 4),
            "p5": round(float(np.percentile(m, 5)), 4),
            "p25": round(float(np.percentile(m, 25)), 4),
            "median": round(float(np.median(m)), 4),
            "p75": round(float(np.percentile(m, 75)), 4),
            "p95": round(float(np.percentile(m, 95)), 4),
            "n": len(m),
        }

    # Convert crystal results
    crystal_summary = {}
    for li in crystal_results:
        crystal_summary[str(li)] = {
            c: {
                "mean_margin": round(float(np.mean(v)), 4),
                "std_margin": round(float(np.std(v)), 4),
                "n": len(v),
            }
            for c, v in crystal_results[li].items()
        }

    result = {
        "model": args.model,
        "n_modes": args.n_modes,
        "baseline_ppl": baseline_ppl,
        "baseline_facts": base_correct,
        "margin_distributions": margin_summary,
        "threshold_sweeps": {
            str(li): sweep_results[li]
            for li in sweep_results
        },
        "optimal_points": {
            str(li): optimal_points[li]
            for li in optimal_points
        },
        "crystal_probe_margins": crystal_summary,
    }

    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Results saved to {out_path}")
    log(f"\n{'='*70}")
    log("  DONE")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
