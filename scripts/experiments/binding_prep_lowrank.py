#!/usr/bin/env python3
"""Binding-Prep Low-Rank — SVD rank sweep for L22-L26.

Session 196 lambda tracer proved: L22-L26 ternary damage is UNIFORM
across all combinators. The failure is approximation quality, not a
circuit-specific break. These layers need continuous compression.

L0 has functional rank 750 (18% of 4096). The sweet spot (L13-L21)
survives 9-mode ternary. Where do L22-L26 fall? This experiment
finds their functional rank via SVD sweep.

Experiments:
  1. Per-layer SVD rank sweep: L22-L26 individually, ranks 100-4096
  2. Control layers: L15 (sweet spot) and L30 (binding)
  3. Combined: all 5 layers at functional rank simultaneously
  4. Integrated: L0 SVD + L10-L21 ternary + L22-L26 SVD (the full
     Stage 2+3 replacement with SVD instead of ternary for L22-L26)

Usage:
  uv run python scripts/experiments/binding_prep_lowrank.py \
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

EVAL_TEXTS = [
    "The theory of general relativity describes gravity as"
    " the curvature of spacetime caused by mass and energy.",
    "In a large mixing bowl, combine the flour, sugar, and"
    " baking powder. Make a well in the center.",
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
    "To solve this equation, first isolate the variable on"
    " one side by subtracting three from both sides.",
]

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
        inputs = tokenizer(
            text, return_tensors="pt",
            truncation=True, max_length=256,
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        labels = inputs["input_ids"].clone()
        with torch.no_grad():
            out = model(**inputs, labels=labels)
            total_loss += out.loss.item() * labels.numel()
            total_tokens += labels.numel()
    return float(np.exp(total_loss / total_tokens))


def generate_text(model, tokenizer, prompt, device,
                  max_new_tokens=30):
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            do_sample=False, temperature=1.0,
            pad_token_id=tokenizer.pad_token_id,
        )
    generated = outputs[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True)


def measure_facts(model, tokenizer, device):
    correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(
            model, tokenizer, fp["prompt"], device,
        )
        if fp["expected"].lower() in gen.lower():
            correct += 1
    return correct, len(FACT_PROMPTS)


# ══════════════════════════════════════════════════════════════
# Low-rank replacement (from l0_lowrank.py)
# ══════════════════════════════════════════════════════════════

class LowRankLinear(torch.nn.Module):
    """W ≈ A @ B where A=(out,r), B=(r,in)."""

    def __init__(self, A, B, bias=None):
        super().__init__()
        self.register_buffer("A", A)
        self.register_buffer("B", B)
        if bias is not None:
            self.register_buffer("bias", bias)
        else:
            self.bias = None

    def forward(self, x):
        out = x.float() @ self.B.T @ self.A.T
        out = out.clamp(-65000, 65000)
        if self.bias is not None:
            out = out + self.bias.float()
        return out.to(x.dtype)


def svd_factorize(weight, rank):
    """SVD-factorize weight to given rank. Returns A, B, stats."""
    W = weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))

    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)

    W_approx = A @ B
    cos = F.cosine_similarity(
        W.reshape(1, -1), W_approx.reshape(1, -1),
    ).item()

    total_energy = (S ** 2).sum()
    captured = (S[:r] ** 2).sum()
    energy_frac = (captured / total_energy).item()

    return A, B, {
        "rank": r,
        "cos": round(cos, 6),
        "energy_fraction": round(energy_frac, 6),
        "orig_params": W.shape[0] * W.shape[1],
        "lr_params": r * (W.shape[0] + W.shape[1]),
        "compression": round(
            W.shape[0] * W.shape[1]
            / (r * (W.shape[0] + W.shape[1])), 2,
        ),
    }


def replace_ffn_lowrank(model, layer_idx, rank, device):
    """Replace one layer's FFN with low-rank. Returns originals + stats."""
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp

    originals = {}
    stats = {}
    for name in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp, name)
        bias = (
            proj.bias.detach().float()
            if hasattr(proj, "bias") and proj.bias is not None
            else None
        )
        A, B, s = svd_factorize(proj.weight, rank)
        lr_mod = LowRankLinear(
            A.to(device), B.to(device), bias,
        )
        originals[name] = proj
        setattr(mlp, name, lr_mod)
        stats[name] = s

    return originals, stats


def restore_ffn(model, layer_idx, originals):
    """Restore original FFN projections."""
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp
    for name, orig in originals.items():
        setattr(mlp, name, orig)


# ══════════════════════════════════════════════════════════════
# Ternary replacement (for integrated test, from staged_melt.py)
# ══════════════════════════════════════════════════════════════

class TrainableTernaryFFN(torch.nn.Module):
    def __init__(self, cls_w, ternary_signs, gamma):
        super().__init__()
        self.classifier = torch.nn.Parameter(
            torch.tensor(cls_w, dtype=torch.float32),
        )
        self.gamma = torch.nn.Parameter(
            torch.tensor(gamma, dtype=torch.float32),
        )
        self.register_buffer(
            "ternary",
            torch.tensor(ternary_signs, dtype=torch.float32),
        )

    def forward(self, x):
        shape = x.shape
        xf = x.reshape(-1, x.shape[-1]).float()
        logits = xf @ self.classifier.T
        logits = logits.clamp(-20.0, 20.0)
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


def install_ternary_layer(model, tokenizer, layer_idx, device,
                          d_model, n_modes=9):
    """Install ternary hook. Returns (hook_handle, replacement)."""
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
    replacement = TrainableTernaryFFN(
        cls_W, ternary_signs, gamma,
    ).to(device)

    layers = get_layers(model)
    mlp = layers[layer_idx].mlp

    def make_hook(repl):
        def hook_fn(module, inp, out):
            x = inp[0] if isinstance(inp, tuple) else inp
            return repl(x)
        return hook_fn

    h = mlp.register_forward_hook(make_hook(replacement))
    return h, replacement, cls_acc


# ══════════════════════════════════════════════════════════════
# Experiments
# ══════════════════════════════════════════════════════════════

def run_layer_sweep(model, tokenizer, layer_idx, device,
                    baseline_ppl, ranks, label=""):
    """SVD rank sweep for a single layer."""
    log(f"\n{'─'*60}")
    log(f"  Layer {layer_idx} ({label})")
    log(f"{'─'*60}")

    results = []
    for rank in ranks:
        originals, stats = replace_ffn_lowrank(
            model, layer_idx, rank, device,
        )

        ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
        ppl_ratio = ppl / baseline_ppl

        # Compute total compression
        orig_total = sum(s["orig_params"] for s in stats.values())
        lr_total = sum(s["lr_params"] for s in stats.values())
        compression = orig_total / lr_total
        orig_mb = orig_total * 2 / 1024 / 1024
        lr_mb = lr_total * 2 / 1024 / 1024

        # Quick energy summary
        mean_energy = np.mean(
            [s["energy_fraction"] for s in stats.values()]
        )

        marker = ""
        if ppl_ratio < 1.05:
            marker = " ★"
        elif ppl_ratio < 1.20:
            marker = " ✓"
        elif ppl_ratio > 5.0:
            marker = " ✗"

        log(f"    r={rank:>4d}: PPL={ppl:>8.2f}"
            f" ({ppl_ratio:>5.2f}x)"
            f"  energy={mean_energy:.4f}"
            f"  {lr_mb:.1f}MB ({compression:.1f}x){marker}")

        restore_ffn(model, layer_idx, originals)

        results.append({
            "rank": rank,
            "ppl": round(ppl, 4),
            "ppl_ratio": round(ppl_ratio, 4),
            "compression": round(compression, 2),
            "orig_mb": round(orig_mb, 1),
            "lr_mb": round(lr_mb, 1),
            "mean_energy": round(mean_energy, 6),
            "svd_stats": stats,
        })

    return results


def find_functional_rank(results, threshold=1.05):
    """Find the minimum rank where PPL ratio < threshold."""
    for r in results:
        if r["ppl_ratio"] < threshold:
            return r["rank"]
    return None


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    log(f"\n{'='*70}")
    log("  BINDING-PREP LOW-RANK — SVD Rank Sweep for L22-L26")
    log("  Can SVD rescue the binding preparation layers?")
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
    n_layers = model.config.num_hidden_layers
    intermediate = model.config.intermediate_size
    log(f"  d_model={d_model}, n_layers={n_layers},"
        f" intermediate={intermediate}")

    max_rank = min(d_model, intermediate)
    log(f"  Max SVD rank: {max_rank}")

    # ── Baseline ──────────────────────────────────────────
    log("\n  Measuring baseline...")
    baseline_ppl = measure_ppl(
        model, tokenizer, EVAL_TEXTS, args.device,
    )
    base_correct, base_total = measure_facts(
        model, tokenizer, args.device,
    )
    log(f"  Baseline PPL: {baseline_ppl:.2f}")
    log(f"  Baseline facts: {base_correct}/{base_total}"
        f" = {base_correct/base_total:.0%}")

    # ══════════════════════════════════════════════════════
    # Experiment 1: Per-layer SVD rank sweep
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  EXP 1: PER-LAYER SVD RANK SWEEP")
    log(f"{'='*70}")

    ranks = [100, 250, 500, 750, 1000, 1500, 2000, 3000, max_rank]

    # Target layers: L22-L26 (binding prep)
    # Control layers: L15 (sweet spot), L30 (binding)
    sweep_layers = [
        (15, "sweet-spot control"),
        (22, "binding-prep"),
        (23, "binding-prep"),
        (24, "binding-prep"),
        (25, "binding-prep"),
        (26, "binding-prep"),
        (30, "binding control"),
    ]

    all_sweeps = {}
    for li, label in sweep_layers:
        results = run_layer_sweep(
            model, tokenizer, li, args.device,
            baseline_ppl, ranks, label,
        )
        all_sweeps[str(li)] = results

    # ── Functional rank summary ───────────────────────────
    log(f"\n{'='*70}")
    log("  FUNCTIONAL RANK SUMMARY (PPL < 1.05x)")
    log(f"{'='*70}")
    log()
    functional_ranks = {}
    for li, label in sweep_layers:
        fr = find_functional_rank(all_sweeps[str(li)])
        functional_ranks[li] = fr
        # Also find 1.10x and 1.20x thresholds
        fr10 = find_functional_rank(all_sweeps[str(li)], 1.10)
        fr20 = find_functional_rank(all_sweeps[str(li)], 1.20)
        fr_s = str(fr) if fr else ">max"
        fr10_s = str(fr10) if fr10 else ">max"
        fr20_s = str(fr20) if fr20 else ">max"
        log(f"  L{li:>2d} ({label:>18s}):"
            f"  <1.05x @ r={fr_s:>5s}"
            f"  <1.10x @ r={fr10_s:>5s}"
            f"  <1.20x @ r={fr20_s:>5s}")

    # ══════════════════════════════════════════════════════
    # Experiment 2: Combined L22-L26 low-rank
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  EXP 2: COMBINED L22-L26 LOW-RANK")
    log(f"{'='*70}")

    # Test at several rank levels simultaneously
    combined_ranks = [500, 750, 1000, 1500, 2000]
    combined_results = []

    for rank in combined_ranks:
        log(f"\n  All L22-L26 at rank={rank}:")

        all_originals = {}
        total_lr_params = 0
        total_orig_params = 0
        for li in range(22, 27):
            originals, stats = replace_ffn_lowrank(
                model, li, rank, args.device,
            )
            all_originals[li] = originals
            total_lr_params += sum(
                s["lr_params"] for s in stats.values()
            )
            total_orig_params += sum(
                s["orig_params"] for s in stats.values()
            )

        ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
        correct, _ = measure_facts(model, tokenizer, args.device)
        ppl_ratio = ppl / baseline_ppl
        compression = total_orig_params / total_lr_params
        lr_mb = total_lr_params * 2 / 1024 / 1024
        orig_mb = total_orig_params * 2 / 1024 / 1024

        marker = "★" if ppl_ratio < 1.05 else (
            "✓" if ppl_ratio < 1.20 else "✗"
        )

        log(f"    PPL={ppl:.2f} ({ppl_ratio:.2f}x)"
            f"  facts={correct}/{base_total}"
            f"  {lr_mb:.1f}MB vs {orig_mb:.1f}MB"
            f" ({compression:.1f}x) {marker}")

        for li in range(22, 27):
            restore_ffn(model, li, all_originals[li])

        combined_results.append({
            "rank": rank,
            "ppl": round(ppl, 4),
            "ppl_ratio": round(ppl_ratio, 4),
            "facts": correct,
            "compression": round(compression, 2),
            "lr_mb": round(lr_mb, 1),
            "orig_mb": round(orig_mb, 1),
        })

    # ══════════════════════════════════════════════════════
    # Experiment 3: Integrated — L0 SVD + L10-L21 ternary
    #   + L22-L26 SVD (the full compression pipeline)
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  EXP 3: INTEGRATED (L0 SVD + L10-L21 ternary + L22-L26 SVD)")
    log(f"{'='*70}")

    # Install L0 SVD rank-750
    log("\n  Installing L0 SVD rank-750...")
    l0_originals, l0_stats = replace_ffn_lowrank(
        model, 0, 750, args.device,
    )
    log("  L0 installed ✓")

    # Install ternary L13-L21 (core first, calibrated through L0)
    log("\n  Installing ternary L13-L21 (core)...")
    ternary_hooks = []
    for li in range(13, 22):
        h, repl, acc = install_ternary_layer(
            model, tokenizer, li, args.device, d_model,
        )
        ternary_hooks.append(h)
        log(f"    L{li}: acc={acc:.1%}")

    # Install ternary L10-L12 (inward, calibrated through compressed model)
    log("\n  Installing ternary L10-L12 (inward)...")
    for li in range(10, 13):
        h, repl, acc = install_ternary_layer(
            model, tokenizer, li, args.device, d_model,
        )
        ternary_hooks.append(h)
        log(f"    L{li}: acc={acc:.1%}")

    # Measure Stage 2 baseline
    ppl_s2 = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    log(f"\n  Stage 2 PPL: {ppl_s2:.2f}"
        f" ({ppl_s2/baseline_ppl:.2f}x)")

    # Now add L22-L26 SVD at various ranks
    integrated_results = []
    for rank in [750, 1000, 1500, 2000]:
        log(f"\n  +L22-L26 SVD rank={rank}:")
        all_originals = {}
        for li in range(22, 27):
            originals, stats = replace_ffn_lowrank(
                model, li, rank, args.device,
            )
            all_originals[li] = originals

        ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
        correct, _ = measure_facts(model, tokenizer, args.device)
        ppl_ratio = ppl / baseline_ppl

        marker = "★" if ppl_ratio < 1.20 else (
            "✓" if ppl_ratio < 2.0 else "✗"
        )

        log(f"    PPL={ppl:.2f} ({ppl_ratio:.2f}x)"
            f"  facts={correct}/{base_total} {marker}")

        for li in range(22, 27):
            restore_ffn(model, li, all_originals[li])

        integrated_results.append({
            "rank": rank,
            "ppl": round(ppl, 4),
            "ppl_ratio": round(ppl_ratio, 4),
            "facts": correct,
        })

    # Clean up ternary hooks + L0
    for h in ternary_hooks:
        h.remove()
    restore_ffn(model, 0, l0_originals)

    # ══════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  FINAL SUMMARY")
    log(f"{'='*70}")
    log(f"  Baseline: PPL={baseline_ppl:.2f},"
        f" facts={base_correct}/{base_total}")

    log(f"\n  Functional ranks (PPL < 1.05x):")
    for li, label in sweep_layers:
        fr = functional_ranks[li]
        log(f"    L{li}: r={fr or 'N/A'} ({label})")

    log(f"\n  Combined L22-L26:")
    for r in combined_results:
        log(f"    r={r['rank']:>4d}: {r['ppl_ratio']:.2f}x"
            f"  facts={r['facts']}/{base_total}"
            f"  {r['lr_mb']:.1f}MB ({r['compression']:.1f}x)")

    log(f"\n  Integrated (L0 SVD + L10-L21 ternary + L22-L26 SVD):")
    log(f"    Stage 2 alone: {ppl_s2:.2f}"
        f" ({ppl_s2/baseline_ppl:.2f}x)")
    for r in integrated_results:
        log(f"    +L22-L26 r={r['rank']:>4d}: {r['ppl_ratio']:.2f}x"
            f"  facts={r['facts']}/{base_total}")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "binding-prep-lowrank"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    result = {
        "model": args.model,
        "baseline_ppl": baseline_ppl,
        "baseline_facts": base_correct,
        "d_model": d_model,
        "intermediate_size": intermediate,
        "per_layer_sweeps": all_sweeps,
        "functional_ranks": {
            str(k): v for k, v in functional_ranks.items()
        },
        "combined_l22_l26": combined_results,
        "integrated": {
            "stage2_ppl": round(ppl_s2, 4),
            "stage2_ratio": round(ppl_s2 / baseline_ppl, 4),
            "with_l22_l26_svd": integrated_results,
        },
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
