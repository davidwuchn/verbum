#!/usr/bin/env python3
"""Staged Melt — Zone refining from the standing wave node.

Melt outward from L13-L21 (the node — most settled, lowest
oscillation). Each stage adds a few layers, collects calibration
data through the ALREADY-MELTED model, builds ternary replacements,
and re-melts. Like semiconductor zone refining — move the melt
zone through the crystal, don't melt it all at once.

Stages:
  1. L13-L21  (9 layers)   — the sweet spot core
  2. +L10-L12 (3 layers)   — expand inward
  3. +L22-L26 (5 layers)   — expand into binding prep
  4. +L1-L9   (9 layers)   — expand to parser/type-check
  5. +L32-L34 (3 layers)   — add late alignment

Each stage:
  1. Collect calibration through current compressed model
  2. Build ternary replacements for NEW layers
  3. Melt ALL compressed params (old stay near optimum)
  4. Measure PPL

L0: SVD rank-750 throughout (installed at start)
L27-L31, L35: always kept continuous (binding + collapse)

Usage:
  uv run python scripts/experiments/staged_melt.py \
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
# Texts (same corpus as prior experiments)
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

TEST_PROMPTS = [
    "The capital of France is",
    "To make a good cup of coffee, you should",
    "The most important thing about science is",
    "In the beginning, there was",
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


def generate_text(model, tokenizer, prompt, device,
                  max_new=40):
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
        gen = generate_text(
            model, tokenizer, fp["prompt"], device,
        )
        if fp["expected"].lower() in gen.lower():
            correct += 1
    return correct, len(FACT_PROMPTS)


def show_generation(model, tokenizer, device, label=""):
    if label:
        log(f"\n  {label} generation:")
    for prompt in TEST_PROMPTS:
        gen = generate_text(
            model, tokenizer, prompt, device,
        )
        log(f"    {prompt} → {gen.strip()[:60]}")


# ══════════════════════════════════════════════════════════════
# Modules (same as melt_boundaries.py)
# ══════════════════════════════════════════════════════════════

class TrainableLowRankLinear(torch.nn.Module):
    def __init__(self, A, B):
        super().__init__()
        self.A = torch.nn.Parameter(A.clone())
        self.B = torch.nn.Parameter(B.clone())

    def forward(self, x):
        out = x.float() @ self.B.T @ self.A.T
        # Clamp to prevent float16 overflow on cast back
        out = out.clamp(-65000, 65000)
        return out.to(x.dtype)


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
        # Clamp logits to prevent float16 overflow in softmax
        logits = logits.clamp(-20.0, 20.0)
        if self.training:
            weights = F.softmax(logits * 3.0, dim=-1)
            programs = self.ternary * self.gamma
            out = weights @ programs
        else:
            mode = logits.argmax(dim=-1)
            out = self.ternary[mode] * self.gamma[mode]
        return out.to(x.dtype).reshape(shape)


def svd_factorize(weight, rank):
    W = weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))
    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)
    return A, B


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
    all_prompts.extend([f["prompt"] for f in FACT_PROMPTS])

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


def training_step(model, tokenizer, texts, device):
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        enc = tokenizer(
            text, return_tensors="pt",
            truncation=True, max_length=128,
        )
        enc = {k: v.to(device) for k, v in enc.items()}
        labels = enc["input_ids"].clone()
        out = model(**enc, labels=labels)
        loss_val = out.loss.item()
        # Check BEFORE backward — NaN loss poisons all grads
        if np.isnan(loss_val) or np.isinf(loss_val):
            continue
        out.loss.backward()
        total_loss += loss_val * labels.numel()
        total_tokens += labels.numel()
    if total_tokens == 0:
        return float("nan")
    return total_loss / total_tokens


# ══════════════════════════════════════════════════════════════
# Staged melt engine
# ══════════════════════════════════════════════════════════════

def install_ternary_layer(model, tokenizer, layer_idx, device,
                          d_model, n_modes, trainable_params):
    """Collect data, build ternary, install hook. Returns hook."""
    log(f"      L{layer_idx}: collecting data"
        " (through current model)...")
    mlp_in, mlp_out = collect_mlp_data(
        model, tokenizer, layer_idx, device,
        CALIBRATION_TEXTS,
    )
    log(f"      L{layer_idx}: {len(mlp_in)} samples,"
        " clustering...")

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

    cls_W, cls_acc = train_classifier(
        mlp_in, labels, n_modes,
    )

    replacement = TrainableTernaryFFN(
        cls_W, ternary_signs, gamma,
    ).to(device)

    trainable_params.extend([
        replacement.classifier,
        replacement.gamma,
    ])

    layers = get_layers(model)
    mlp = layers[layer_idx].mlp

    def make_hook(repl):
        def hook_fn(module, inp, out):
            x = inp[0] if isinstance(inp, tuple) else inp
            return repl(x)
        return hook_fn

    h = mlp.register_forward_hook(make_hook(replacement))
    log(f"      L{layer_idx}: cls_acc={cls_acc:.1%} ✓")
    return h, replacement


def melt(model, tokenizer, device, trainable_params,
         replacements, n_steps, lr, batch_size):
    """Run GD on all trainable params."""
    optimizer = torch.optim.Adam(trainable_params, lr=lr)

    model.train()
    for _, repl in replacements:
        repl.train()

    history = []
    t0 = time.time()
    nan_count = 0

    for step in range(n_steps):
        optimizer.zero_grad()
        batch_idx = np.random.RandomState(step).choice(
            len(CALIBRATION_TEXTS), batch_size, replace=False,
        )
        batch = [CALIBRATION_TEXTS[i] for i in batch_idx]
        avg_loss = training_step(
            model, tokenizer, batch, device,
        )

        # Gradient clipping — prevent NaN from overflow
        grad_norm = torch.nn.utils.clip_grad_norm_(
            trainable_params, max_norm=1.0,
        )

        # Skip step if loss is NaN
        if np.isnan(avg_loss) or np.isinf(avg_loss):
            nan_count += 1
            optimizer.zero_grad()  # discard bad grads
            if nan_count > 10:
                log(f"      too many NaNs ({nan_count}),"
                    " stopping early")
                break
            continue

        optimizer.step()
        history.append(avg_loss)

        if (step + 1) % 10 == 0 or step == 0:
            elapsed = time.time() - t0
            log(f"      step {step+1:>3d}/{n_steps}:"
                f" loss={avg_loss:.4f}"
                f" grad={grad_norm:.2f}"
                f" ({elapsed:.0f}s)")

    model.eval()
    for _, repl in replacements:
        repl.eval()

    return history


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
    p.add_argument("--l0-rank", type=int, default=750)
    p.add_argument("--n-modes", type=int, default=9)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--batch-size", type=int, default=4)
    args = p.parse_args()

    # Stages: (name, new_layers, melt_steps)
    STAGES = [
        ("core",     list(range(13, 22)), 50),   # L13-21
        ("inward",   list(range(10, 13)),  30),   # L10-12
        ("outward",  list(range(22, 27)),  50),   # L22-26
        ("parser",   list(range(1, 10)),   50),   # L1-9
        ("late",     [32, 33, 34],         30),   # L32-34
    ]

    log(f"\n{'='*60}")
    log("  STAGED MELT — Zone Refining")
    log("  Melt outward from the standing wave node")
    log(f"{'='*60}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  L0 rank: {args.l0_rank}")
    log(f"  Ternary modes: {args.n_modes}")
    log(f"  Stages: {len(STAGES)}")
    for name, lyrs, steps in STAGES:
        log(f"    {name}: L{lyrs[0]}-L{lyrs[-1]}"
            f" ({len(lyrs)} layers, {steps} steps)")
    log()

    # ── Load ──────────────────────────────────────────────
    dtype = (
        torch.float16
        if any(s in args.model for s in ["8B", "14B", "32B"])
        else torch.float32
    )
    log(f"  Loading {args.model} ({dtype})...")
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
    base_ppl = measure_ppl(
        model, tokenizer, EVAL_TEXTS, args.device,
    )
    base_correct, base_total = measure_facts(
        model, tokenizer, args.device,
    )
    log(f"  Baseline PPL: {base_ppl:.2f}")
    log(f"  Baseline facts: {base_correct}/{base_total}"
        f" = {base_correct/base_total:.0%}")

    # ── Install L0 low-rank (stays for all stages) ────────
    log(f"\n  Installing L0 SVD rank-{args.l0_rank}...")
    layers = get_layers(model)
    trainable_params = []

    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, args.l0_rank)
        lr_mod = TrainableLowRankLinear(
            A.to(args.device), B.to(args.device),
        )
        setattr(mlp0, pname, lr_mod)
        trainable_params.extend([lr_mod.A, lr_mod.B])
    log("  L0 installed ✓")

    # Freeze all original params
    for param in model.parameters():
        param.requires_grad = False
    for param in trainable_params:
        param.requires_grad = True

    # ══════════════════════════════════════════════════════
    # Run stages
    # ══════════════════════════════════════════════════════

    all_replacements = []  # (hook, replacement) pairs
    all_ternary_layers = []
    stage_results = []

    for stage_idx, (stage_name, new_layers, n_steps) in \
            enumerate(STAGES):
        log(f"\n{'═'*60}")
        log(f"  STAGE {stage_idx+1}/{len(STAGES)}: {stage_name}")
        log(f"  Adding L{new_layers[0]}-L{new_layers[-1]}"
            f" ({len(new_layers)} layers)")
        log(f"  Melt steps: {n_steps}")
        log(f"  Total ternary so far:"
            f" {len(all_ternary_layers)} + {len(new_layers)}"
            f" = {len(all_ternary_layers) + len(new_layers)}")
        log(f"{'═'*60}")

        # ── Install new ternary layers ────────────────────
        log(f"\n    Installing {len(new_layers)} new layers"
            " (calibrated through current model):")
        for li in new_layers:
            h, repl = install_ternary_layer(
                model, tokenizer, li, args.device,
                d_model, args.n_modes, trainable_params,
            )
            all_replacements.append((h, repl))
            all_ternary_layers.append(li)

        # Ensure new params are trainable
        for param in trainable_params:
            param.requires_grad = True

        n_train = sum(p.numel() for p in trainable_params)
        log(f"\n    Trainable params: {n_train:,}")

        # ── Measure pre-melt ──────────────────────────────
        model.eval()
        for _, repl in all_replacements:
            repl.eval()

        pre_ppl = measure_ppl(
            model, tokenizer, EVAL_TEXTS, args.device,
        )
        pre_ratio = pre_ppl / base_ppl
        log(f"    Pre-melt PPL: {pre_ppl:.2f} ({pre_ratio:.2f}x)")

        # ── MELT ─────────────────────────────────────────
        log(f"\n    Melting ({n_steps} steps, lr={args.lr})...")
        history = melt(
            model, tokenizer, args.device,
            trainable_params, all_replacements,
            n_steps, args.lr, args.batch_size,
        )

        # ── Measure post-melt ─────────────────────────────
        post_ppl = measure_ppl(
            model, tokenizer, EVAL_TEXTS, args.device,
        )
        post_ratio = post_ppl / base_ppl
        post_correct, _ = measure_facts(
            model, tokenizer, args.device,
        )
        log(f"\n    Post-melt PPL: {post_ppl:.2f}"
            f" ({post_ratio:.2f}x)")
        log(f"    Post-melt facts: {post_correct}/{base_total}"
            f" = {post_correct/base_total:.0%}")

        show_generation(
            model, tokenizer, args.device,
            f"Stage {stage_idx+1}",
        )

        stage_results.append({
            "stage": stage_idx + 1,
            "name": stage_name,
            "new_layers": new_layers,
            "total_ternary": len(all_ternary_layers),
            "n_steps": n_steps,
            "pre_ppl": pre_ppl,
            "pre_ratio": round(pre_ratio, 4),
            "post_ppl": post_ppl,
            "post_ratio": round(post_ratio, 4),
            "post_facts": post_correct,
            "loss_start": round(history[0], 4),
            "loss_end": round(history[-1], 4),
            "trainable_params": n_train,
        })

    # ══════════════════════════════════════════════════════
    # Final summary
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*60}")
    log("  STAGED MELT SUMMARY")
    log(f"{'='*60}")
    log(f"  Baseline: PPL={base_ppl:.2f},"
        f" facts={base_correct}/{base_total}")
    log()
    log(f"  {'Stage':>5s}  {'Name':>8s}  {'Layers':>6s}"
        f"  {'Pre':>7s}  {'Post':>7s}"
        f"  {'Facts':>5s}  {'Loss':>12s}")
    log(f"  {'─'*5}  {'─'*8}  {'─'*6}"
        f"  {'─'*7}  {'─'*7}"
        f"  {'─'*5}  {'─'*12}")

    for r in stage_results:
        log(f"  {r['stage']:>5d}  {r['name']:>8s}"
            f"  {r['total_ternary']:>4d}+L0"
            f"  {r['pre_ratio']:>6.2f}x"
            f"  {r['post_ratio']:>6.2f}x"
            f"  {r['post_facts']:>3d}/15"
            f"  {r['loss_start']:.2f}→{r['loss_end']:.2f}")

    final = stage_results[-1]
    verdict = "PASS" if final["post_ratio"] < 1.5 else "FAIL"
    log(f"\n  Final: PPL={final['post_ppl']:.2f}"
        f" ({final['post_ratio']:.2f}x),"
        f" facts={final['post_facts']}/{base_total}")
    log(f"  VERDICT: {verdict}")
    log(f"{'='*60}\n")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "staged-melt"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")
    result = {
        "model": args.model,
        "l0_rank": args.l0_rank,
        "n_modes": args.n_modes,
        "lr": args.lr,
        "baseline_ppl": base_ppl,
        "baseline_facts": base_correct,
        "stages": stage_results,
        "final_ppl": final["post_ppl"],
        "final_ratio": final["post_ratio"],
        "final_facts": final["post_facts"],
        "verdict": verdict,
    }
    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    log(f"  Results saved to {out_path}")


if __name__ == "__main__":
    main()
