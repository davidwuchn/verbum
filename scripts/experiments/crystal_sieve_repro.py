#!/usr/bin/env python3
"""Crystal-Sieve Reproducibility — is 1.03x the center or a lucky tail?

# register: functional (reproducibility — seed variance on a PPL measurement)

Audit-registry claim #7: "crystal-sieve + 4 continuation residuals = 1.03x
PPL across 29 sieved layers (Qwen3-8B)." s196 itself noted a rerun gave 3.23x
and called training "sensitive to initialization/batch order."

This control re-runs the EXACT s196 beta_expansion pipeline under N controlled
seeds and reports mean +/- std. The discriminating question: is 1.03x the
distribution's center, or its lucky tail?

Decomposition (no extra runs needed):
  - pre_melt_ratio  : sieve mask ONLY (no continuations, no training).
                      Its across-seed std = the MASK-subsampling variance
                      (the FFN projections are >10M elems -> torch.randperm
                      subsamples 5M for the quantile threshold -> mask varies).
  - post_melt_ratio : sieve + continuation init + 100-step CE melt.
                      Its across-seed std = mask + init + training variance.
  If pre std ~ 0 and post std large  -> variance is in continuation training.
  If pre std large                    -> the mask subsampling itself is unstable.

NB: batch order in the original melt is RandomState(step) -> DETERMINISTIC
across reruns; it is NOT a variance source (the s196 note is wrong on that).
The real unseeded sources are (a) continuation torch.randn init and (b) the
sieve mask randperm subsample. Both are now seeded per run.

Usage:
  uv run python scripts/experiments/crystal_sieve_repro.py \
    --model Qwen/Qwen3-8B --device mps --seeds 5

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
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))


# ══════════════════════════════════════════════════════════════
# Texts (identical to beta_expansion.py — same protocol)
# ══════════════════════════════════════════════════════════════

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
    {"prompt": "The speed of light is approximately", "expected": "300"},
    {"prompt": "The first president of the United States was",
     "expected": "George Washington"},
    {"prompt": "The year World War II ended was", "expected": "1945"},
    {"prompt": "The chemical symbol for gold is", "expected": "Au"},
    {"prompt": "The largest planet in our solar system is",
     "expected": "Jupiter"},
    {"prompt": "The author of Romeo and Juliet is", "expected": "Shakespeare"},
    {"prompt": "Pi is approximately equal to", "expected": "3.14"},
    {"prompt": "The Great Wall of China is located in", "expected": "China"},
    {"prompt": "The human body has", "expected": "206"},
    {"prompt": "Einstein's famous equation is E equals", "expected": "mc"},
    {"prompt": "The freezing point of water in Celsius is", "expected": "0"},
    {"prompt": "The currency of the United Kingdom is the", "expected": "pound"},
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
    "She walked through the ancient forest, her footsteps"
    " muffled by fallen leaves.",
    "The old man sat quietly by the river, watching the"
    " fish jump at dawn.",
    "In a large mixing bowl, combine the flour, sugar,"
    " and baking powder.",
    "To solve this equation, first isolate the variable"
    " on one side.",
    "The committee voted unanimously to approve the new"
    " environmental regulations.",
    "The function takes two arguments and returns their"
    " composition as a new callable.",
    "What time does the store close today?",
    "I think we should probably leave now before it gets"
    " too dark outside.",
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
        enc = tokenizer(text, return_tensors="pt",
                        truncation=True, max_length=256)
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


# ══════════════════════════════════════════════════════════════
# Crystal Sieve (identical to beta_expansion.py)
# ══════════════════════════════════════════════════════════════

class FrozenSieveLinear(nn.Module):
    def __init__(self, weight, zero_rate=0.5):
        super().__init__()
        W = weight.detach().float().cpu()
        abs_W = W.abs()
        if zero_rate > 0:
            flat = abs_W.flatten()
            if flat.numel() > 10_000_000:
                # NOTE: torch.randperm here is the MASK-subsampling RNG.
                # Seeded per run by torch.manual_seed in run_one_seed().
                idx = torch.randperm(flat.numel())[:5_000_000]
                threshold = torch.quantile(flat[idx], zero_rate)
            else:
                threshold = torch.quantile(flat, zero_rate)
            mask = (abs_W >= threshold).float()
        else:
            mask = torch.ones_like(W)
        W_sieve = torch.sign(W) * abs_W * mask
        self.register_buffer("W_sieve", W_sieve.half())

    def forward(self, x):
        out = x.float() @ self.W_sieve.float().T
        return out.clamp(-65000, 65000).to(x.dtype)


class TrainableLowRankLinear(nn.Module):
    def __init__(self, A, B):
        super().__init__()
        self.register_buffer("A", A)
        self.register_buffer("B", B)

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


class ContinuationResidual(nn.Module):
    """Small learned correction at a layer boundary (identical to s196).

    NOTE: torch.randn here is the continuation-INIT RNG. Seeded per run.
    """

    def __init__(self, d_model, rank=32):
        super().__init__()
        self.W_down = nn.Parameter(torch.randn(d_model, rank) * 0.001)
        self.W_up = nn.Parameter(torch.randn(rank, d_model) * 0.001)

    def forward(self, x):
        correction = x.float() @ self.W_down @ self.W_up
        return (x.float() + correction).to(x.dtype)


# ══════════════════════════════════════════════════════════════
# One seeded run of the full pipeline
# ══════════════════════════════════════════════════════════════

def run_one_seed(args, seed, base_facts_cached=None):
    """Load fresh, seed, sieve, melt — return per-seed metrics."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.backends.mps.is_available():
        torch.mps.manual_seed(seed)

    SIEVE_LAYERS = [*range(1, 27), 32, 33, 34]
    RESIDUAL_LAYERS = [0, 9, 21, 26]

    dtype = (torch.float16
             if any(s in args.model for s in ["8B", "14B", "32B"])
             else torch.float32)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device,
        attn_implementation="eager")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()
    d_model = model.config.hidden_size

    # Baseline (deterministic; measured per-seed as a sanity check)
    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    if args.skip_facts:
        base_facts = -1
    elif base_facts_cached is None:
        base_facts, _ = measure_facts(model, tokenizer, args.device)
    else:
        base_facts = base_facts_cached

    # Install sieve (L0 SVD + 29 sieved layers)
    layers = get_layers(model)
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, 750)
        setattr(mlp0, pname,
                TrainableLowRankLinear(A.to(args.device), B.to(args.device)))
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)
            setattr(mlp, pname,
                    FrozenSieveLinear(proj.weight,
                                      zero_rate=args.zero_rate).to(args.device))

    pre_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    pre_facts = (-1 if args.skip_facts
                 else measure_facts(model, tokenizer, args.device)[0])

    # Install continuation residuals
    continuations = {}
    cont_hooks = []
    trainable_params = []
    for li in RESIDUAL_LAYERS:
        cont = ContinuationResidual(d_model, rank=args.residual_rank).to(args.device)
        continuations[li] = cont
        trainable_params.extend([cont.W_down, cont.W_up])

        def make_cont_hook(c):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                corrected = c(h)
                if isinstance(out, tuple):
                    return (corrected, *out[1:])
                return corrected
            return hook_fn
        cont_hooks.append(layers[li].register_forward_hook(make_cont_hook(cont)))

    n_trainable = sum(p.numel() for p in trainable_params)

    # Melt — CE loss, batch order RandomState(step) (deterministic, as s196)
    optimizer = torch.optim.Adam(trainable_params, lr=args.lr)
    model.train()
    history = []
    for step in range(args.melt_steps):
        optimizer.zero_grad()
        rng = np.random.RandomState(step)
        batch_idx = rng.choice(len(CALIBRATION_TEXTS),
                               min(4, len(CALIBRATION_TEXTS)), replace=False)
        total_loss = 0.0
        total_tokens = 0
        for idx in batch_idx:
            enc = tokenizer(CALIBRATION_TEXTS[idx], return_tensors="pt",
                            truncation=True, max_length=128)
            enc = {k: v.to(args.device) for k, v in enc.items()}
            labels = enc["input_ids"].clone()
            out = model(**enc, labels=labels)
            if not (np.isnan(out.loss.item()) or np.isinf(out.loss.item())):
                out.loss.backward()
                total_loss += out.loss.item() * labels.numel()
                total_tokens += labels.numel()
        if total_tokens == 0:
            continue
        torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=0.5)
        optimizer.step()
        history.append(total_loss / total_tokens)
    model.eval()

    post_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    post_facts = (-1 if args.skip_facts
                  else measure_facts(model, tokenizer, args.device)[0])

    for h in cont_hooks:
        h.remove()
    del model
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    return {
        "seed": seed,
        "base_ppl": round(base_ppl, 4),
        "base_facts": base_facts,
        "pre_melt_ppl": round(pre_ppl, 4),
        "pre_melt_ratio": round(pre_ppl / base_ppl, 4),
        "pre_facts": pre_facts,
        "post_melt_ppl": round(post_ppl, 4),
        "post_melt_ratio": round(post_ppl / base_ppl, 4),
        "post_facts": post_facts,
        "continuation_params": n_trainable,
        "final_loss": round(history[-1], 4) if history else None,
    }


def summarize(key, rows):
    vals = np.array([r[key] for r in rows], dtype=float)
    return {
        "mean": round(float(vals.mean()), 4),
        "std": round(float(vals.std(ddof=1)) if len(vals) > 1 else 0.0, 4),
        "min": round(float(vals.min()), 4),
        "max": round(float(vals.max()), 4),
        "values": [round(float(v), 4) for v in vals],
    }


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--zero-rate", type=float, default=0.5)
    p.add_argument("--residual-rank", type=int, default=32)
    p.add_argument("--melt-steps", type=int, default=100)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--seeds", type=int, default=5,
                   help="number of seeds 0..N-1")
    p.add_argument("--seed-list", type=str, default=None,
                   help="comma-separated explicit seeds (overrides --seeds)")
    p.add_argument("--skip-facts", action="store_true",
                   help="skip fact-retrieval generations (3x faster; PPL is "
                        "the headline metric for the reproducibility audit)")
    args = p.parse_args()

    if args.seed_list:
        seeds = [int(s) for s in args.seed_list.split(",")]
    else:
        seeds = list(range(args.seeds))

    log(f"\n{'='*70}")
    log("  CRYSTAL-SIEVE REPRODUCIBILITY — is 1.03x the center or the tail?")
    log(f"{'='*70}")
    log(f"  Model: {args.model}  Device: {args.device}")
    log(f"  Seeds: {seeds}")
    log("  register: functional (reproducibility — seed variance on PPL)")

    rows = []
    base_facts_cached = None
    t0 = time.time()
    for i, seed in enumerate(seeds):
        log(f"\n{'─'*70}")
        log(f"  SEED {seed}  ({i+1}/{len(seeds)})   [{time.time()-t0:.0f}s elapsed]")
        log(f"{'─'*70}")
        r = run_one_seed(args, seed, base_facts_cached)
        base_facts_cached = r["base_facts"]  # deterministic; cache after first
        rows.append(r)
        def _f(v):
            return "skip" if v == -1 else f"{v}/15"
        log(f"  base PPL={r['base_ppl']}  facts={_f(r['base_facts'])}")
        log(f"  pre-melt  ratio={r['pre_melt_ratio']:.3f}x "
            f"(PPL {r['pre_melt_ppl']}, facts {_f(r['pre_facts'])})")
        log(f"  post-melt ratio={r['post_melt_ratio']:.3f}x "
            f"(PPL {r['post_melt_ppl']}, facts {_f(r['post_facts'])}, "
            f"final_loss {r['final_loss']})")

    # Summaries
    pre_sum = summarize("pre_melt_ratio", rows)
    post_sum = summarize("post_melt_ratio", rows)
    base_sum = summarize("base_ppl", rows)

    log(f"\n{'='*70}")
    log("  SUMMARY")
    log(f"{'='*70}")
    log(f"  base PPL          : {base_sum['mean']} "
        f"(std {base_sum['std']}, should be ~0 = determinism check)")
    log(f"  pre-melt  (mask)  : {pre_sum['mean']:.3f}x "
        f"± {pre_sum['std']:.3f}  [{pre_sum['min']:.3f}, {pre_sum['max']:.3f}]")
    log(f"  post-melt (full)  : {post_sum['mean']:.3f}x "
        f"± {post_sum['std']:.3f}  [{post_sum['min']:.3f}, {post_sum['max']:.3f}]")
    log(f"  headline claim    : 1.03x  ->  observed mean {post_sum['mean']:.3f}x, "
        f"best-seed {post_sum['min']:.3f}x")

    out_dir = _PROJECT_ROOT / "results" / "crystal-sieve-repro"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")
    result = {
        "register": "functional (reproducibility — seed variance on PPL)",
        "model": args.model,
        "device": args.device,
        "zero_rate": args.zero_rate,
        "residual_rank": args.residual_rank,
        "melt_steps": args.melt_steps,
        "lr": args.lr,
        "seeds": seeds,
        "per_seed": rows,
        "summary": {
            "base_ppl": base_sum,
            "pre_melt_ratio": pre_sum,
            "post_melt_ratio": post_sum,
        },
        "headline_claim": 1.03,
        "elapsed_s": round(time.time() - t0, 1),
    }
    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
