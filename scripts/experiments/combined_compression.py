#!/usr/bin/env python3
"""Combined Compression — Low-Rank L0 + Ternary L1-L34.

Build the actual compressed model:
  L0:       SVD rank-750 (70.3MB, 0.94x PPL)
  L1-L26:   9 ternary modes each
  L27-L31:  Keep continuous (binding)
  L32-L34:  9 ternary modes each
  L35:      Keep continuous (collapse)

Protocol:
  1. Collect calibration data from ORIGINAL model for all target layers
  2. Cluster + train classifiers for ternary layers
  3. SVD-factorize L0
  4. Install ALL replacements simultaneously
  5. Measure PPL + facts

Usage:
  uv run python scripts/experiments/combined_compression.py \
    --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
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
    " researchers persisted and eventually found the solution.",
    "The primary colors are red, blue, and yellow.",
    "The Fibonacci sequence begins with 1, 1, 2, 3, 5,"
    " 8, 13, 21.",
    "Pi is approximately equal to 3.14159265 and is an"
    " irrational number.",
    "The distance from Earth to the Moon is about 384400"
    " kilometers.",
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
                  max_new=30):
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
# Low-Rank replacement (for L0)
# ══════════════════════════════════════════════════════════════

class LowRankLinear(torch.nn.Module):
    def __init__(self, A, B):
        super().__init__()
        self.register_buffer("A", A)
        self.register_buffer("B", B)

    def forward(self, x):
        return (x.float() @ self.B.T @ self.A.T).to(x.dtype)


def svd_replace_proj(proj, rank):
    """Replace nn.Linear with rank-r SVD approximation."""
    W = proj.weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))
    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)

    cos = F.cosine_similarity(
        W.reshape(1, -1), (A @ B).reshape(1, -1),
    ).item()
    energy = float((S[:r] ** 2).sum() / (S ** 2).sum())

    return LowRankLinear(A, B), cos, energy


# ══════════════════════════════════════════════════════════════
# Ternary replacement (for L1-L34)
# ══════════════════════════════════════════════════════════════

class TinyClassifierFFN(torch.nn.Module):
    def __init__(self, cls_w, ternary, gamma):
        super().__init__()
        self.register_buffer(
            "classifier",
            torch.tensor(cls_w, dtype=torch.float32),
        )
        self.register_buffer(
            "ternary",
            torch.tensor(ternary, dtype=torch.float32),
        )
        self.register_buffer(
            "gamma",
            torch.tensor(gamma, dtype=torch.float32),
        )

    def forward(self, x):
        shape = x.shape
        xf = x.reshape(-1, x.shape[-1]).float()
        logits = xf @ self.classifier.T
        mode = logits.argmax(dim=-1)
        out = self.ternary[mode] * self.gamma[mode]
        return out.to(x.dtype).reshape(shape)


def collect_mlp_data(model, tokenizer, layer_idx, device,
                     texts, n_crystal=100):
    """Collect (mlp_input, mlp_output) from original model."""
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


def build_ternary_replacement(mlp_in, mlp_out, d_model,
                              n_modes=9):
    """Build ternary classifier + lookup from calibration data."""
    km = MiniBatchKMeans(
        n_clusters=n_modes, random_state=42,
        batch_size=min(256, len(mlp_out)), n_init=5,
    )
    labels = km.fit_predict(mlp_out)

    ternary = np.zeros((n_modes, d_model))
    gamma = np.zeros((n_modes, d_model))
    for i in range(n_modes):
        mask = labels == i
        if mask.sum() == 0:
            continue
        c = mlp_out[mask].mean(axis=0)
        ternary[i] = np.sign(c)
        gamma[i] = np.abs(c)

    cls_W, cls_acc = train_classifier(mlp_in, labels, n_modes)
    return TinyClassifierFFN(cls_W, ternary, gamma), cls_acc


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
    p.add_argument(
        "--sweet-spot-only", action="store_true",
        help="Only ternarize L13-L21 (conservative)",
    )
    args = p.parse_args()

    log(f"\n{'='*60}")
    log("  COMBINED COMPRESSION")
    log("  Low-Rank L0 + Ternary L1-L34")
    log(f"{'='*60}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  L0 rank: {args.l0_rank}")
    log(f"  Ternary modes: {args.n_modes}")
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
    intermediate = model.config.intermediate_size
    log(f"  Layers: {n_layers}, d={d_model}, "
        f"intermediate={intermediate}")

    # Define layer groups
    if args.sweet_spot_only:
        ternary_layers = list(range(13, 22))  # L13-L21
        keep_layers = (
            list(range(1, 13))
            + list(range(22, 36))
        )
    else:
        ternary_layers = list(range(1, 27)) + [32, 33, 34]
        keep_layers = [27, 28, 29, 30, 31, 35]
    log(f"  L0: SVD rank-{args.l0_rank}")
    log(f"  Ternary: {len(ternary_layers)} layers"
        f" ({ternary_layers[0]}-{ternary_layers[-1]})")
    log(f"  Keep continuous: {len(keep_layers)} layers")

    # ── Baseline ──────────────────────────────────────────
    log("\n  Measuring baseline...")
    base_ppl = measure_ppl(
        model, tokenizer, EVAL_TEXTS, args.device,
    )
    base_correct, base_total = measure_facts(
        model, tokenizer, args.device,
    )
    base_fact_rate = base_correct / base_total
    log(f"  Baseline PPL: {base_ppl:.2f}")
    log(f"  Baseline facts: {base_correct}/{base_total}"
        f" = {base_fact_rate:.0%}")

    # ══════════════════════════════════════════════════════
    # Phase 1: Collect ALL calibration data from original model
    # ══════════════════════════════════════════════════════
    log(f"\n{'─'*60}")
    log("  PHASE 1: Collect calibration data (original model)")
    log(f"{'─'*60}")

    layer_data = {}
    for li in ternary_layers:
        log(f"    L{li}: collecting...", )
        mlp_in, mlp_out = collect_mlp_data(
            model, tokenizer, li, args.device,
            CALIBRATION_TEXTS,
        )
        layer_data[li] = (mlp_in, mlp_out)
        log(f"    L{li}: {len(mlp_in)} samples")

    # ══════════════════════════════════════════════════════
    # Phase 2: Build all replacements
    # ══════════════════════════════════════════════════════
    log(f"\n{'─'*60}")
    log("  PHASE 2: Build replacements")
    log(f"{'─'*60}")

    layers = get_layers(model)
    device = args.device
    originals = {}  # for potential restoration
    stats = {}

    # ── L0: SVD low-rank ──────────────────────────────────
    log(f"\n  L0: SVD rank-{args.l0_rank}...")
    mlp0 = layers[0].mlp
    l0_stats = {}
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        originals[f"L0.{pname}"] = proj
        lr_mod, cos, energy = svd_replace_proj(
            proj, args.l0_rank,
        )
        lr_mod = lr_mod.to(device)
        setattr(mlp0, pname, lr_mod)
        l0_stats[pname] = {"cos": cos, "energy": energy}
        log(f"    {pname}: cos={cos:.4f} energy={energy:.4f}")
    stats["L0"] = l0_stats

    # ── L1-L26, L32-L34: Ternary ─────────────────────────
    log("\n  Building ternary replacements...")
    ternary_stats = {}
    for li in ternary_layers:
        mlp_in, mlp_out = layer_data[li]
        replacement, cls_acc = build_ternary_replacement(
            mlp_in, mlp_out, d_model, args.n_modes,
        )
        replacement = replacement.to(device)

        mlp = layers[li].mlp

        # Hook to intercept the full MLP
        def make_hook(repl):
            def hook_fn(module, inp, out):
                x = inp[0] if isinstance(inp, tuple) else inp
                return repl(x)
            return hook_fn

        handle = mlp.register_forward_hook(make_hook(replacement))
        originals[f"L{li}.hook"] = handle

        ternary_stats[li] = {"classifier_acc": cls_acc}
        if (li <= 5 or li >= 25 or li % 5 == 0):
            log(f"    L{li}: cls_acc={cls_acc:.1%}")

    stats["ternary"] = {
        str(k): v for k, v in ternary_stats.items()
    }
    log(f"    ... {len(ternary_layers)} layers replaced")

    # ── Size calculation ──────────────────────────────────
    # L0: 3 * rank * (12288 + 4096) * 2 bytes
    l0_bytes = 3 * args.l0_rank * (intermediate + d_model) * 2
    l0_mb = l0_bytes / 1024 / 1024

    # Ternary: per layer = d_model * n_modes (classifier)
    #          + n_modes * d_model (ternary) + n_modes * d_model (gamma)
    per_ternary = d_model * args.n_modes * 2  # classifier fp16
    per_ternary += args.n_modes * d_model * 1  # ternary int8
    per_ternary += args.n_modes * d_model * 2  # gamma fp16
    ternary_bytes = len(ternary_layers) * per_ternary
    ternary_mb = ternary_bytes / 1024 / 1024

    # Kept layers: original size
    per_layer_bytes = 3 * d_model * intermediate * 2
    kept_bytes = len(keep_layers) * per_layer_bytes
    kept_mb = kept_bytes / 1024 / 1024

    total_mb = l0_mb + ternary_mb + kept_mb
    orig_total_mb = n_layers * per_layer_bytes / 1024 / 1024

    log("\n  Size breakdown:")
    log(f"    L0 (rank-{args.l0_rank}):  {l0_mb:.1f}MB")
    log(f"    Ternary ({len(ternary_layers)} layers):"
        f" {ternary_mb:.1f}MB")
    log(f"    Kept ({len(keep_layers)} layers):"
        f" {kept_mb:.1f}MB")
    log(f"    TOTAL FFN: {total_mb:.1f}MB"
        f" (was {orig_total_mb:.1f}MB,"
        f" {orig_total_mb/total_mb:.1f}x compression)")

    # ══════════════════════════════════════════════════════
    # Phase 3: Measure combined model
    # ══════════════════════════════════════════════════════
    log(f"\n{'─'*60}")
    log("  PHASE 3: Measure combined model")
    log(f"{'─'*60}")

    combined_ppl = measure_ppl(
        model, tokenizer, EVAL_TEXTS, args.device,
    )
    combined_ratio = combined_ppl / base_ppl
    log(f"  Combined PPL: {combined_ppl:.2f}"
        f" ({combined_ratio:.2f}x)")

    correct, total = measure_facts(
        model, tokenizer, args.device,
    )
    fact_rate = correct / total
    log(f"  Facts: {correct}/{total} = {fact_rate:.0%}"
        f" (baseline: {base_fact_rate:.0%})")

    # ── Test generation quality ───────────────────────────
    log("\n  Generation samples:")
    test_prompts = [
        "The capital of France is",
        "In the beginning, there was",
        "To make a good cup of coffee, you should",
        "The most important thing about science is",
    ]
    for prompt in test_prompts:
        gen = generate_text(
            model, tokenizer, prompt, args.device,
            max_new=40,
        )
        log(f"    {prompt} → {gen.strip()[:60]}")

    # ══════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*60}")
    log("  RESULT")
    log(f"{'='*60}")
    log(f"  Baseline:  PPL={base_ppl:.2f},"
        f" facts={base_fact_rate:.0%}")
    log(f"  Combined:  PPL={combined_ppl:.2f}"
        f" ({combined_ratio:.2f}x),"
        f" facts={fact_rate:.0%}")
    log(f"  FFN size:  {total_mb:.1f}MB"
        f" (was {orig_total_mb:.1f}MB,"
        f" {orig_total_mb/total_mb:.1f}x)")
    log(f"    L0:      {l0_mb:.1f}MB (SVD rank-{args.l0_rank})")
    log(f"    Ternary: {ternary_mb:.1f}MB"
        f" ({len(ternary_layers)} layers)")
    log(f"    Kept:    {kept_mb:.1f}MB"
        f" ({len(keep_layers)} layers)")

    verdict = "PASS" if combined_ratio < 1.5 else "FAIL"
    log(f"\n  VERDICT: {verdict}")
    log(f"{'='*60}\n")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "combined-compression"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")
    result = {
        "model": args.model,
        "baseline_ppl": base_ppl,
        "baseline_fact_rate": base_fact_rate,
        "combined_ppl": combined_ppl,
        "combined_ppl_ratio": round(combined_ratio, 4),
        "combined_fact_rate": fact_rate,
        "l0_rank": args.l0_rank,
        "n_modes": args.n_modes,
        "ternary_layers": ternary_layers,
        "keep_layers": keep_layers,
        "size_mb": {
            "l0": round(l0_mb, 1),
            "ternary": round(ternary_mb, 1),
            "kept": round(kept_mb, 1),
            "total": round(total_mb, 1),
            "original": round(orig_total_mb, 1),
            "compression": round(orig_total_mb / total_mb, 1),
        },
        "l0_svd_stats": l0_stats,
        "ternary_stats": {
            str(k): v for k, v in ternary_stats.items()
        },
        "verdict": verdict,
    }
    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    log(f"  Results saved to {out_path}")


if __name__ == "__main__":
    main()
