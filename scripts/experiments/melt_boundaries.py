#!/usr/bin/env python3
"""Melt Boundaries — GD fuses the compressed pieces together.

The hologram is there in each piece. The seams are wrong.
GD melts the boundaries so the pieces learn to talk.

Architecture:
  FROZEN (topology):
    L0:       SVD factor directions (signs/structure)
    L13-L21:  ternary program patterns (9 discrete programs)
    L1-L12, L22-L35: all original weights

  TRAINABLE (continuous):
    L0:       SVD factors A, B (magnitude/rotation)
    L13-L21:  classifier weights + gamma scaling

  GD adjusts the trainable params so compressed layers
  produce representations compatible with their neighbors.

Usage:
  uv run python scripts/experiments/melt_boundaries.py \
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
                  max_new=40):
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new,
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
# TRAINABLE Low-Rank module (for L0)
# ══════════════════════════════════════════════════════════════

class TrainableLowRankLinear(torch.nn.Module):
    """Low-rank W = A @ B with trainable A, B."""

    def __init__(self, A, B):
        super().__init__()
        # These are nn.Parameter so GD can train them
        self.A = torch.nn.Parameter(A.clone())
        self.B = torch.nn.Parameter(B.clone())

    def forward(self, x):
        return (x.float() @ self.B.T @ self.A.T).to(x.dtype)


def svd_factorize(weight, rank):
    """SVD-factorize weight to rank r. Returns A, B tensors."""
    W = weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))
    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)
    return A, B


# ══════════════════════════════════════════════════════════════
# TRAINABLE Ternary module (for sweet-spot layers)
# ══════════════════════════════════════════════════════════════

class TrainableTernaryFFN(torch.nn.Module):
    """Ternary FFN with trainable classifier + gamma.

    FROZEN: ternary sign patterns (the topology)
    TRAINABLE: classifier weights, gamma scaling
    """

    def __init__(self, cls_w, ternary_signs, gamma):
        super().__init__()
        # Trainable
        self.classifier = torch.nn.Parameter(
            torch.tensor(cls_w, dtype=torch.float32),
        )
        self.gamma = torch.nn.Parameter(
            torch.tensor(gamma, dtype=torch.float32),
        )
        # Frozen topology
        self.register_buffer(
            "ternary",
            torch.tensor(ternary_signs, dtype=torch.float32),
        )

    def forward(self, x):
        shape = x.shape
        xf = x.reshape(-1, x.shape[-1]).float()
        logits = xf @ self.classifier.T

        # Soft selection during training (Gumbel-softmax-like)
        # Hard argmax during eval
        if self.training:
            # Soft weighting — differentiable
            weights = F.softmax(logits * 5.0, dim=-1)
            programs = self.ternary * self.gamma  # (n, d)
            out = weights @ programs  # (batch, d)
        else:
            mode = logits.argmax(dim=-1)
            out = self.ternary[mode] * self.gamma[mode]

        return out.to(x.dtype).reshape(shape)


def collect_mlp_data(model, tokenizer, layer_idx, device,
                     texts, n_crystal=100):
    """Collect (mlp_input, mlp_output) from model."""
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


# ══════════════════════════════════════════════════════════════
# Training loop — melt the boundaries
# ══════════════════════════════════════════════════════════════

def training_step(model, tokenizer, texts, device):
    """One training step: forward pass + loss + backward."""
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        inputs = tokenizer(
            text, return_tensors="pt",
            truncation=True, max_length=128,
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        labels = inputs["input_ids"].clone()
        out = model(**inputs, labels=labels)
        loss = out.loss
        loss.backward()
        total_loss += loss.item() * labels.numel()
        total_tokens += labels.numel()
    return total_loss / total_tokens


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
    p.add_argument("--n-steps", type=int, default=50)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument(
        "--sweet-spot-only", action="store_true",
        help="Only ternarize L13-L21 (conservative)",
    )
    args = p.parse_args()

    log(f"\n{'='*60}")
    log("  MELT BOUNDARIES")
    log("  GD fuses the compressed pieces together")
    log(f"{'='*60}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  L0 rank: {args.l0_rank}")
    log(f"  Ternary modes: {args.n_modes}")
    log(f"  Training steps: {args.n_steps}")
    log(f"  Learning rate: {args.lr}")
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

    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    log(f"  Layers: {n_layers}, d={d_model}")

    if args.sweet_spot_only:
        ternary_layers = list(range(13, 22))  # L13-L21
    else:
        ternary_layers = list(range(1, 27)) + [32, 33, 34]

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

    # ══════════════════════════════════════════════════════
    # Phase 1: Collect calibration data + build replacements
    # ══════════════════════════════════════════════════════
    log(f"\n{'─'*60}")
    log("  PHASE 1: Build compressed model")
    log(f"{'─'*60}")

    layers = get_layers(model)
    trainable_params = []

    # ── L0: Trainable low-rank ────────────────────────────
    log("  L0: SVD factorize...")
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, args.l0_rank)
        lr_mod = TrainableLowRankLinear(
            A.to(args.device), B.to(args.device),
        )
        setattr(mlp0, pname, lr_mod)
        trainable_params.extend([lr_mod.A, lr_mod.B])
        log(f"    {pname}: A={tuple(A.shape)}, B={tuple(B.shape)}")

    # ── L13-L21: Trainable ternary ────────────────────────
    log("  Collecting calibration data...")
    hooks = []
    for li in ternary_layers:
        log(f"    L{li}: collecting...")
        mlp_in, mlp_out = collect_mlp_data(
            model, tokenizer, li, args.device,
            CALIBRATION_TEXTS,
        )
        log(f"    L{li}: {len(mlp_in)} samples, clustering...")

        km = MiniBatchKMeans(
            n_clusters=args.n_modes, random_state=42,
            batch_size=min(256, len(mlp_out)), n_init=5,
        )
        labels = km.fit_predict(mlp_out)

        ternary_signs = np.zeros((args.n_modes, d_model))
        gamma = np.zeros((args.n_modes, d_model))
        for i in range(args.n_modes):
            mask = labels == i
            if mask.sum() == 0:
                continue
            c = mlp_out[mask].mean(axis=0)
            ternary_signs[i] = np.sign(c)
            gamma[i] = np.abs(c)

        cls_W, cls_acc = train_classifier(
            mlp_in, labels, args.n_modes,
        )

        replacement = TrainableTernaryFFN(
            cls_W, ternary_signs, gamma,
        ).to(args.device)

        trainable_params.extend([
            replacement.classifier,
            replacement.gamma,
        ])

        mlp = layers[li].mlp

        def make_hook(repl):
            def hook_fn(module, inp, out):
                x = inp[0] if isinstance(inp, tuple) else inp
                return repl(x)
            return hook_fn

        h = mlp.register_forward_hook(make_hook(replacement))
        hooks.append((h, replacement))

        log(f"    L{li}: cls_acc={cls_acc:.1%}")

    # ── Freeze everything except our params ───────────────
    log("\n  Freezing all original parameters...")
    for param in model.parameters():
        param.requires_grad = False

    # Unfreeze our trainable params
    for param in trainable_params:
        param.requires_grad = True

    n_trainable = sum(p.numel() for p in trainable_params)
    n_total = sum(p.numel() for p in model.parameters())
    log(f"  Trainable: {n_trainable:,} / {n_total:,}"
        f" ({n_trainable/n_total:.2%})")

    # ══════════════════════════════════════════════════════
    # Phase 2: Measure BEFORE training
    # ══════════════════════════════════════════════════════
    log(f"\n{'─'*60}")
    log("  PHASE 2: Measure before melting")
    log(f"{'─'*60}")

    model.eval()
    for _, repl in hooks:
        repl.eval()

    pre_ppl = measure_ppl(
        model, tokenizer, EVAL_TEXTS, args.device,
    )
    pre_correct, _ = measure_facts(
        model, tokenizer, args.device,
    )
    log(f"  Pre-melt PPL: {pre_ppl:.2f}"
        f" ({pre_ppl/base_ppl:.2f}x)")
    log(f"  Pre-melt facts: {pre_correct}/{base_total}"
        f" = {pre_correct/base_total:.0%}")

    # ── Test generation ───────────────────────────────────
    log("\n  Pre-melt generation:")
    for prompt in [
        "The capital of France is",
        "To make a good cup of coffee, you should",
    ]:
        gen = generate_text(
            model, tokenizer, prompt, args.device,
        )
        log(f"    {prompt} → {gen.strip()[:60]}")

    # ══════════════════════════════════════════════════════
    # Phase 3: MELT — train the boundaries
    # ══════════════════════════════════════════════════════
    log(f"\n{'─'*60}")
    log("  PHASE 3: MELTING (GD on compressed params)")
    log(f"{'─'*60}")

    optimizer = torch.optim.Adam(trainable_params, lr=args.lr)

    # Prepare training texts — use calibration + extra
    train_texts = list(CALIBRATION_TEXTS)

    model.train()
    for _, repl in hooks:
        repl.train()

    history = []
    t0 = time.time()

    for step in range(args.n_steps):
        optimizer.zero_grad()

        # Mini-batch from train texts
        batch_idx = np.random.RandomState(step).choice(
            len(train_texts), args.batch_size, replace=False,
        )
        batch = [train_texts[i] for i in batch_idx]

        avg_loss = training_step(
            model, tokenizer, batch, args.device,
        )
        optimizer.step()

        history.append(avg_loss)

        if (step + 1) % 5 == 0 or step == 0:
            elapsed = time.time() - t0
            log(f"    step {step+1:>3d}/{args.n_steps}:"
                f" loss={avg_loss:.4f}"
                f" ({elapsed:.0f}s)")

    # ══════════════════════════════════════════════════════
    # Phase 4: Measure AFTER training
    # ══════════════════════════════════════════════════════
    log(f"\n{'─'*60}")
    log("  PHASE 4: Measure after melting")
    log(f"{'─'*60}")

    model.eval()
    for _, repl in hooks:
        repl.eval()

    post_ppl = measure_ppl(
        model, tokenizer, EVAL_TEXTS, args.device,
    )
    post_correct, _ = measure_facts(
        model, tokenizer, args.device,
    )
    log(f"  Post-melt PPL: {post_ppl:.2f}"
        f" ({post_ppl/base_ppl:.2f}x)")
    log(f"  Post-melt facts: {post_correct}/{base_total}"
        f" = {post_correct/base_total:.0%}")

    # ── Test generation ───────────────────────────────────
    log("\n  Post-melt generation:")
    for prompt in [
        "The capital of France is",
        "To make a good cup of coffee, you should",
        "The most important thing about science is",
        "In the beginning, there was",
    ]:
        gen = generate_text(
            model, tokenizer, prompt, args.device,
        )
        log(f"    {prompt} → {gen.strip()[:60]}")

    # ══════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*60}")
    log("  RESULT")
    log(f"{'='*60}")
    log(f"  Baseline:   PPL={base_ppl:.2f},"
        f" facts={base_correct}/{base_total}")
    log(f"  Pre-melt:   PPL={pre_ppl:.2f}"
        f" ({pre_ppl/base_ppl:.2f}x),"
        f" facts={pre_correct}/{base_total}")
    log(f"  Post-melt:  PPL={post_ppl:.2f}"
        f" ({post_ppl/base_ppl:.2f}x),"
        f" facts={post_correct}/{base_total}")
    log(f"  Improvement: {pre_ppl/base_ppl:.2f}x"
        f" → {post_ppl/base_ppl:.2f}x")
    log(f"  Trainable params: {n_trainable:,}"
        f" ({n_trainable/n_total:.2%})")
    log(f"  Training: {args.n_steps} steps,"
        f" lr={args.lr}")
    log(f"  Loss: {history[0]:.4f} → {history[-1]:.4f}")

    verdict = "PASS" if post_ppl / base_ppl < 1.5 else "FAIL"
    log(f"\n  VERDICT: {verdict}")
    log(f"{'='*60}\n")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "melt-boundaries"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")
    result = {
        "model": args.model,
        "l0_rank": args.l0_rank,
        "n_modes": args.n_modes,
        "ternary_layers": ternary_layers,
        "n_steps": args.n_steps,
        "lr": args.lr,
        "baseline_ppl": base_ppl,
        "pre_melt_ppl": pre_ppl,
        "post_melt_ppl": post_ppl,
        "pre_melt_ratio": round(pre_ppl / base_ppl, 4),
        "post_melt_ratio": round(post_ppl / base_ppl, 4),
        "pre_facts": pre_correct,
        "post_facts": post_correct,
        "total_facts": base_total,
        "trainable_params": n_trainable,
        "total_params": n_total,
        "loss_history": [round(l, 4) for l in history],
        "verdict": verdict,
    }
    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    log(f"  Results saved to {out_path}")


if __name__ == "__main__":
    main()
