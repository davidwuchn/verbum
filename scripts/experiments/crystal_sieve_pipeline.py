#!/usr/bin/env python3
"""Crystal Sieve Pipeline v2 — frozen sieve + trainable interface scales.

v1 failed: per-weight trainable gamma = 4.4B params = no compression.
v2: the sieve (sign * |W| * mask) is FROZEN. Only per-row output
scales are trainable — one scalar per row per projection. This is
tiny (~85K params total) but gives the melt just enough control to
fix the interface mismatch between layers.

The sieve provides the computation. The interface scales fix the
magnitude mismatch at layer boundaries. Multi-projection melt
optimizes the scales at functional boundaries.

Pre-melt result from v1: 2.12x PPL with frozen sieve alone.
The question: can ~85K trainable interface scales push this below 1.5x?

Usage:
  uv run python scripts/experiments/crystal_sieve_pipeline.py \
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
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))


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

TEST_PROMPTS = [
    "The capital of France is",
    "To make a good cup of coffee, you should",
    "The most important thing about science is",
    "In the beginning, there was",
]

CHECKPOINTS = {
    "lexer": 0,
    "composition": 21,
    "type_crystal": 26,
    "binding": 30,
}

PROJECTION_WEIGHTS = {
    "lexer": 0.1,
    "composition": 0.2,
    "type_crystal": 0.5,
    "binding": 0.2,
    "output_ce": 1.0,
}


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
        enc = tokenizer(text, return_tensors="pt",
                        truncation=True, max_length=256)
        enc = {k: v.to(device) for k, v in enc.items()}
        labels = enc["input_ids"].clone()
        with torch.no_grad():
            out = model(**enc, labels=labels)
            total_loss += out.loss.item() * labels.numel()
            total_tokens += labels.numel()
    return float(np.exp(total_loss / total_tokens))


def generate_text(model, tokenizer, prompt, device, max_new=40):
    enc = tokenizer(prompt, return_tensors="pt")
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=max_new,
                             do_sample=False, temperature=1.0,
                             pad_token_id=tokenizer.pad_token_id)
    return tokenizer.decode(out[0][enc["input_ids"].shape[1]:],
                            skip_special_tokens=True)


def measure_facts(model, tokenizer, device):
    correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(model, tokenizer, fp["prompt"], device)
        if fp["expected"].lower() in gen.lower():
            correct += 1
    return correct, len(FACT_PROMPTS)


def show_generation(model, tokenizer, device, label=""):
    if label:
        log(f"\n  {label} generation:")
    for prompt in TEST_PROMPTS:
        gen = generate_text(model, tokenizer, prompt, device)
        log(f"    {prompt} → {gen.strip()[:60]}")


# ══════════════════════════════════════════════════════════════
# Crystal Sieve — frozen sieve + trainable output scale
# ══════════════════════════════════════════════════════════════

class FrozenSieveLinear(nn.Module):
    """W_eff = W_sieve * output_scale (broadcast per row).

    W_sieve is FROZEN: sign(W) * |W| * mask (precomputed, float16).
    output_scale is TRAINABLE: one scalar per output row, init=1.0.
    """

    def __init__(self, weight, zero_rate=0.5):
        super().__init__()
        W = weight.detach().float().cpu()
        out_features, in_features = W.shape

        # Build sieve: sign(W) * |W| * mask
        abs_W = W.abs()
        if zero_rate > 0:
            flat = abs_W.flatten()
            if flat.numel() > 10_000_000:
                idx = torch.randperm(flat.numel())[:5_000_000]
                threshold = torch.quantile(flat[idx], zero_rate)
            else:
                threshold = torch.quantile(flat, zero_rate)
            mask = (abs_W >= threshold).float()
        else:
            mask = torch.ones_like(W)

        W_sieve = torch.sign(W) * abs_W * mask
        self.register_buffer("W_sieve", W_sieve.half())

        # Trainable: per-output-row scale, initialized to 1.0
        self.output_scale = nn.Parameter(
            torch.ones(out_features, dtype=torch.float32)
        )

        self.out_features = out_features
        self.in_features = in_features
        self.zero_rate = float((mask == 0).float().mean().item())
        self.n_nonzero = int(mask.sum().item())

    def forward(self, x):
        # W_eff = W_sieve * output_scale[:, None]
        W_eff = self.W_sieve.float() * self.output_scale.unsqueeze(1)
        out = x.float() @ W_eff.T
        return out.clamp(-65000, 65000).to(x.dtype)

    @property
    def compressed_bytes(self):
        """Storage: W_sieve needs signs(1bit) + mask(1bit) + scale per nonzero."""
        # Practical: int2 signs + binary mask + per-row float16 scale
        sign_bits = self.out_features * self.in_features  # 1 bit each
        mask_bits = self.out_features * self.in_features  # 1 bit each
        scale_bytes = self.out_features * 2  # float16 per row
        return (sign_bits + mask_bits) // 8 + scale_bytes


class TrainableLowRankLinear(nn.Module):
    def __init__(self, A, B):
        super().__init__()
        self.A = nn.Parameter(A.clone())
        self.B = nn.Parameter(B.clone())

    def forward(self, x):
        out = x.float() @ self.B.T @ self.A.T
        return out.clamp(-65000, 65000).to(x.dtype)


def svd_factorize(weight, rank):
    W = weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))
    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)
    return A, B


# ══════════════════════════════════════════════════════════════
# Teacher state caching
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def cache_teacher_states(model, tokenizer, texts, device, checkpoints):
    layers = get_layers(model)
    all_cached = []
    for text in texts:
        enc = tokenizer(text, return_tensors="pt",
                        truncation=True, max_length=128)
        enc = {k: v.to(device) for k, v in enc.items()}
        captured = {}
        hooks = []

        def make_hook(name):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                captured[name] = h.detach().cpu().float()
            return hook_fn

        for name, layer_idx in checkpoints.items():
            hooks.append(layers[layer_idx].register_forward_hook(
                make_hook(name)))
        model(**enc)
        for h in hooks:
            h.remove()
        all_cached.append({name: captured[name][0]
                           for name in checkpoints if name in captured})
    return all_cached


# ══════════════════════════════════════════════════════════════
# Melt step
# ══════════════════════════════════════════════════════════════

def melt_step(model, tokenizer, texts, device, batch_indices,
              teacher_cache, checkpoints, weights):
    layers = get_layers(model)
    total_ce = 0.0
    total_tokens = 0

    for global_idx in batch_indices:
        text = texts[global_idx]
        enc = tokenizer(text, return_tensors="pt",
                        truncation=True, max_length=128)
        enc = {k: v.to(device) for k, v in enc.items()}
        labels = enc["input_ids"].clone()

        student_captured = {}
        hooks = []

        def make_hook(name):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                student_captured[name] = h
            return hook_fn

        for name, layer_idx in checkpoints.items():
            hooks.append(layers[layer_idx].register_forward_hook(
                make_hook(name)))

        out = model(**enc, labels=labels)
        for h in hooks:
            h.remove()

        ce_val = out.loss.item()
        if np.isnan(ce_val) or np.isinf(ce_val):
            continue

        proj_loss = torch.tensor(0.0, device=device)
        teacher_states = teacher_cache[global_idx]

        for name in checkpoints:
            if name not in student_captured or name not in teacher_states:
                continue
            s = student_captured[name][0].float()
            t = teacher_states[name].to(device).float()
            min_seq = min(s.shape[0], t.shape[0])
            cos = F.cosine_similarity(s[:min_seq], t[:min_seq], dim=-1)
            proj_loss = proj_loss + weights[name] * (1.0 - cos).mean()

        total_loss = weights["output_ce"] * out.loss + proj_loss
        total_loss.backward()
        total_ce += ce_val * labels.numel()
        total_tokens += labels.numel()

    return total_ce / total_tokens if total_tokens > 0 else float("nan")


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
    p.add_argument("--zero-rate", type=float, default=0.5)
    p.add_argument("--melt-steps", type=int, default=100)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--batch-size", type=int, default=4)
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]

    log(f"\n{'='*70}")
    log("  CRYSTAL SIEVE PIPELINE v2")
    log("  Frozen sieve + trainable per-row output scales")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  Zero rate: {args.zero_rate:.0%}")
    log(f"  Melt steps: {args.melt_steps}")
    log(f"  LR: {args.lr}")
    log(f"  Sieve layers: {len(SIEVE_LAYERS)}")

    # ── Load ──────────────────────────────────────────────
    dtype = (torch.float16
             if any(s in args.model for s in ["8B", "14B", "32B"])
             else torch.float32)
    log(f"\n  Loading {args.model} ({dtype})...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    d_model = model.config.hidden_size
    log(f"  d_model={d_model}")

    # ── Baseline ──────────────────────────────────────────
    log("\n  Measuring baseline...")
    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    base_facts, base_total = measure_facts(
        model, tokenizer, args.device)
    log(f"  Baseline PPL: {base_ppl:.2f}, facts: {base_facts}/{base_total}")

    # ── Cache teacher states ──────────────────────────────
    log("\n  Caching teacher states...")
    teacher_cache = cache_teacher_states(
        model, tokenizer, CALIBRATION_TEXTS, args.device, CHECKPOINTS)
    log(f"  Cached {len(teacher_cache)} texts")

    # ══════════════════════════════════════════════════════
    # Install sieve
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  INSTALLING CRYSTAL SIEVE")
    log(f"{'═'*70}")

    layers = get_layers(model)
    trainable_params = []

    # L0: SVD
    log(f"\n  L0: SVD rank-{args.l0_rank}...")
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, args.l0_rank)
        lr_mod = TrainableLowRankLinear(
            A.to(args.device), B.to(args.device))
        setattr(mlp0, pname, lr_mod)
        trainable_params.extend([lr_mod.A, lr_mod.B])
    log("  L0 ✓")

    # Sieve layers
    total_scale_params = 0
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        layer_scales = 0
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)
            sieve = FrozenSieveLinear(
                proj.weight, zero_rate=args.zero_rate,
            ).to(args.device)
            setattr(mlp, pname, sieve)
            trainable_params.append(sieve.output_scale)
            layer_scales += sieve.output_scale.numel()
        total_scale_params += layer_scales

        if li <= 3 or li >= 24 or li % 5 == 0:
            log(f"  L{li:>2d}: sieve installed"
                f" ({layer_scales:,} scale params)")

    # Freeze all, enable trainable
    for param in model.parameters():
        param.requires_grad = False
    for param in trainable_params:
        param.requires_grad = True

    n_trainable = sum(p.numel() for p in trainable_params)
    log(f"\n  Trainable params: {n_trainable:,}"
        f" ({total_scale_params:,} scales + L0 SVD)")

    # ══════════════════════════════════════════════════════
    # Pre-melt
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PRE-MELT")
    log(f"{'═'*70}")

    pre_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    pre_facts, _ = measure_facts(model, tokenizer, args.device)
    pre_ratio = pre_ppl / base_ppl
    log(f"  PPL: {pre_ppl:.2f} ({pre_ratio:.2f}x)"
        f"  facts: {pre_facts}/{base_total}")
    show_generation(model, tokenizer, args.device, "Pre-melt")

    # ══════════════════════════════════════════════════════
    # Melt
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  MULTI-PROJECTION MELT")
    log(f"{'═'*70}")

    optimizer = torch.optim.Adam(trainable_params, lr=args.lr)
    model.train()
    history = []
    t0 = time.time()
    nan_count = 0

    for step in range(args.melt_steps):
        optimizer.zero_grad()
        rng = np.random.RandomState(step)
        batch_idx = rng.choice(
            len(CALIBRATION_TEXTS), args.batch_size, replace=False)

        avg_loss = melt_step(
            model, tokenizer, CALIBRATION_TEXTS, args.device,
            batch_idx, teacher_cache, CHECKPOINTS, PROJECTION_WEIGHTS)

        grad_norm = torch.nn.utils.clip_grad_norm_(
            trainable_params, max_norm=0.1)

        if np.isnan(avg_loss) or np.isinf(avg_loss):
            nan_count += 1
            optimizer.zero_grad()
            if nan_count > 10:
                log(f"    Too many NaNs ({nan_count}), stopping")
                break
            continue

        optimizer.step()
        history.append(avg_loss)

        if (step + 1) % 10 == 0 or step == 0:
            elapsed = time.time() - t0
            log(f"    step {step+1:>3d}/{args.melt_steps}:"
                f" loss={avg_loss:.4f}"
                f" grad={grad_norm:.4f}"
                f" ({elapsed:.0f}s)")

    model.eval()

    # ══════════════════════════════════════════════════════
    # Post-melt
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  POST-MELT")
    log(f"{'═'*70}")

    post_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    post_facts, _ = measure_facts(model, tokenizer, args.device)
    post_ratio = post_ppl / base_ppl
    log(f"  PPL: {post_ppl:.2f} ({post_ratio:.2f}x)"
        f"  facts: {post_facts}/{base_total}")
    show_generation(model, tokenizer, args.device, "Post-melt")

    # ══════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  RESULTS")
    log(f"{'='*70}")
    log(f"  Baseline:   PPL={base_ppl:.2f}  facts={base_facts}/{base_total}")
    log(f"  Pre-melt:   PPL={pre_ppl:.2f} ({pre_ratio:.2f}x)"
        f"  facts={pre_facts}/{base_total}")
    log(f"  Post-melt:  PPL={post_ppl:.2f} ({post_ratio:.2f}x)"
        f"  facts={post_facts}/{base_total}")
    log(f"  Trainable:  {n_trainable:,} params")
    log(f"  Melt steps: {len(history)}/{args.melt_steps}")

    verdict = ("PASS" if post_ratio < 1.5 else
               "MARGINAL" if post_ratio < 3.0 else "FAIL")
    log(f"  VERDICT: {verdict}")

    # Save
    out_dir = _PROJECT_ROOT / "results" / "crystal-sieve-pipeline"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")
    result = {
        "model": args.model,
        "version": 2,
        "zero_rate": args.zero_rate,
        "melt_steps": args.melt_steps,
        "lr": args.lr,
        "baseline_ppl": base_ppl,
        "baseline_facts": base_facts,
        "pre_melt_ppl": pre_ppl,
        "pre_melt_ratio": round(pre_ratio, 4),
        "pre_melt_facts": pre_facts,
        "post_melt_ppl": post_ppl,
        "post_melt_ratio": round(post_ratio, 4),
        "post_melt_facts": post_facts,
        "n_trainable": n_trainable,
        "n_scale_params": total_scale_params,
        "loss_history": [round(x, 4) for x in history],
        "verdict": verdict,
    }
    out_path = out_dir / f"{slug}_v2.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
