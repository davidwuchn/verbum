#!/usr/bin/env python3
"""L0 Low-Rank Factorization — Can SVD Rescue the Lexer?

Session 195 showed L0 is genuinely continuous: ternary modes fail because
they replace the matrix multiply with a lookup table, destroying the rank.
Q4 works because it preserves the full-rank matrix structure.

This experiment tests the middle ground: SVD low-rank approximation.
Replace W with U_r @ S_r @ Vt_r at various ranks. This preserves the
matrix multiply (every input gets a unique output) but with fewer params.

For gate_proj (12288 x 4096):
  Full:     50.3M params
  Rank-r:   r * (12288 + 4096) = r * 16384 params
  r=1000:   16.4M params (3.1x compression)
  r=500:    8.2M params  (6.1x compression)
  r=100:    1.6M params  (31x compression)

Instruments:
  1. SVD rank sweep: PPL + facts at r=100..4096
  2. Per-projection analysis: which of gate/up/down is most sensitive?
  3. Quantized factors: SVD then round U,V to int8 (further compression)
  4. L0 vs L15 comparison (control)

Usage:
  uv run python scripts/experiments/l0_lowrank.py \
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
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))


# ══════════════════════════════════════════════════════════════════
# Texts and prompts (same as l0_characterization.py)
# ══════════════════════════════════════════════════════════════════

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
    raise RuntimeError(
        f"Cannot find layers in {type(model).__name__}"
    )


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


def check_fact(generated, expected):
    return expected.lower() in generated.lower()


def measure_facts(model, tokenizer, device):
    correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(
            model, tokenizer, fp["prompt"], device,
        )
        correct += int(check_fact(gen, fp["expected"]))
    return correct, len(FACT_PROMPTS)


# ══════════════════════════════════════════════════════════════════
# Low-rank replacement module
# ══════════════════════════════════════════════════════════════════

class LowRankLinear(torch.nn.Module):
    """W approximated as U @ V where U=(out,r), V=(r,in).

    SVD: W = U_full @ diag(S) @ Vt_full
    Truncated to rank r: U_r @ diag(S_r) @ Vt_r
    We absorb sqrt(S) into both factors for numerical balance:
      A = U_r @ diag(sqrt(S_r))   shape (out, r)
      B = diag(sqrt(S_r)) @ Vt_r  shape (r, in)
      W_approx = A @ B
    """

    def __init__(self, A, B, bias=None, quantize=False):
        super().__init__()
        if quantize:
            # Quantize to int8 with per-column scaling
            A_scale = A.abs().amax(dim=0, keepdim=True)
            A_scale = A_scale.clamp(min=1e-8)
            A_q = (A / A_scale * 127).round().clamp(-128, 127)
            self.register_buffer("A_q", A_q.to(torch.int8))
            self.register_buffer("A_scale", A_scale)

            B_scale = B.abs().amax(dim=0, keepdim=True)
            B_scale = B_scale.clamp(min=1e-8)
            B_q = (B / B_scale * 127).round().clamp(-128, 127)
            self.register_buffer("B_q", B_q.to(torch.int8))
            self.register_buffer("B_scale", B_scale)
            self.quantized = True
        else:
            self.register_buffer("A", A)
            self.register_buffer("B", B)
            self.quantized = False

        if bias is not None:
            self.register_buffer("bias", bias)
        else:
            self.bias = None

    def forward(self, x):
        orig_dtype = x.dtype
        if self.quantized:
            A = self.A_q.float() * self.A_scale
            B = self.B_q.float() * self.B_scale
        else:
            A = self.A
            B = self.B
        # x: (..., in_features) -> (..., out_features)
        out = x.float() @ B.T @ A.T
        if self.bias is not None:
            out = out + self.bias.float()
        return out.to(orig_dtype)


def svd_factorize(weight, rank, quantize=False):
    """SVD-factorize a weight matrix to given rank.

    Returns LowRankLinear module + reconstruction cosine.
    """
    W = weight.detach().float().cpu()
    # W shape: (out_features, in_features) for nn.Linear
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)

    # Truncate to rank r
    r = min(rank, len(S))
    U_r = U[:, :r]       # (out, r)
    S_r = S[:r]           # (r,)
    Vt_r = Vt[:r, :]      # (r, in)

    # Absorb sqrt(S) into both factors
    sqrt_S = S_r.sqrt()
    A = U_r * sqrt_S.unsqueeze(0)   # (out, r)
    B = Vt_r * sqrt_S.unsqueeze(1)  # (r, in)

    # Reconstruction quality
    W_approx = A @ B
    cos = torch.nn.functional.cosine_similarity(
        W.reshape(1, -1), W_approx.reshape(1, -1),
    ).item()
    frob_ratio = (
        torch.norm(W - W_approx) / torch.norm(W)
    ).item()

    # Energy captured
    total_energy = (S ** 2).sum()
    captured_energy = (S_r ** 2).sum()
    energy_frac = (captured_energy / total_energy).item()

    module = LowRankLinear(A, B, quantize=quantize)

    return module, {
        "rank": r,
        "cos": round(cos, 6),
        "frob_error": round(frob_ratio, 6),
        "energy_fraction": round(energy_frac, 6),
        "orig_params": W.shape[0] * W.shape[1],
        "lr_params": r * (W.shape[0] + W.shape[1]),
        "compression": round(
            W.shape[0] * W.shape[1]
            / (r * (W.shape[0] + W.shape[1])),
            2,
        ),
    }


# ══════════════════════════════════════════════════════════════════
# Experiment: replace one layer's FFN projections with low-rank
# ══════════════════════════════════════════════════════════════════

def replace_ffn_lowrank(model, layer_idx, rank, quantize=False):
    """Replace gate_proj, up_proj, down_proj with low-rank SVD.

    Returns handles to restore originals, plus stats dict.
    """
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp
    device = next(mlp.parameters()).device

    originals = {}
    stats = {}

    for name in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp, name)
        W = proj.weight
        bias = proj.bias if hasattr(proj, "bias") and proj.bias is not None else None

        lr_module, s = svd_factorize(W, rank, quantize=quantize)
        lr_module = lr_module.to(device)
        if bias is not None:
            lr_module.bias = bias.detach().float().to(device)

        originals[name] = proj
        setattr(mlp, name, lr_module)
        stats[name] = s

    return originals, stats


def restore_ffn(model, layer_idx, originals):
    """Restore original FFN projections."""
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp
    for name, orig in originals.items():
        setattr(mlp, name, orig)


# ══════════════════════════════════════════════════════════════════
# Main sweep
# ══════════════════════════════════════════════════════════════════

def run_layer_sweep(model, tokenizer, layer_idx, device,
                    baseline_ppl, baseline_facts, ranks,
                    layer_name, do_quantized=True):
    """Sweep ranks for one layer. Returns list of result dicts."""
    log(f"\n{'='*60}")
    log(f"  LAYER {layer_idx} ({layer_name})")
    log(f"{'='*60}")

    results = []

    for rank in ranks:
        log(f"\n  rank={rank}:")

        # ── Float low-rank ────────────────────────────────
        originals, stats = replace_ffn_lowrank(
            model, layer_idx, rank, quantize=False,
        )

        # Summary of SVD quality
        for pname, s in stats.items():
            log(f"    {pname}: cos={s['cos']:.4f}"
                f"  energy={s['energy_fraction']:.4f}"
                f"  compress={s['compression']:.1f}x")

        ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
        correct, total = measure_facts(model, tokenizer, device)
        ppl_ratio = ppl / baseline_ppl
        fact_rate = correct / total

        log(f"    float: PPL={ppl:.2f} ({ppl_ratio:.2f}x)"
            f"  facts={correct}/{total}={fact_rate:.0%}")

        result = {
            "rank": rank,
            "ppl": ppl,
            "ppl_ratio": round(ppl_ratio, 4),
            "fact_rate": fact_rate,
            "facts_correct": correct,
            "quantized": False,
            "svd_stats": stats,
        }

        # Total compression across all 3 projections
        orig_total = sum(
            s["orig_params"] for s in stats.values()
        )
        lr_total = sum(
            s["lr_params"] for s in stats.values()
        )
        result["total_orig_params"] = orig_total
        result["total_lr_params"] = lr_total
        result["total_compression"] = round(
            orig_total / lr_total, 2,
        )
        orig_mb = orig_total * 2 / 1024 / 1024
        lr_mb = lr_total * 2 / 1024 / 1024
        result["orig_mb"] = round(orig_mb, 1)
        result["lr_mb"] = round(lr_mb, 1)
        log(f"    size: {lr_mb:.1f}MB vs {orig_mb:.1f}MB"
            f" ({result['total_compression']:.1f}x)")

        restore_ffn(model, layer_idx, originals)
        results.append(result)

        # ── Quantized low-rank ────────────────────────────
        if do_quantized and rank <= 2000:
            originals_q, stats_q = replace_ffn_lowrank(
                model, layer_idx, rank, quantize=True,
            )

            ppl_q = measure_ppl(
                model, tokenizer, EVAL_TEXTS, device,
            )
            correct_q, _ = measure_facts(
                model, tokenizer, device,
            )
            ppl_ratio_q = ppl_q / baseline_ppl
            fact_rate_q = correct_q / total

            # int8 factors = 1 byte per param + scales
            lr_bytes = lr_total * 1  # int8
            scale_overhead = rank * 2 * 3  # per-col scales
            q_mb = (lr_bytes + scale_overhead) / 1024 / 1024

            log(f"    int8:  PPL={ppl_q:.2f}"
                f" ({ppl_ratio_q:.2f}x)"
                f"  facts={correct_q}/{total}"
                f"={fact_rate_q:.0%}"
                f"  size={q_mb:.1f}MB")

            results.append({
                "rank": rank,
                "ppl": ppl_q,
                "ppl_ratio": round(ppl_ratio_q, 4),
                "fact_rate": fact_rate_q,
                "facts_correct": correct_q,
                "quantized": True,
                "total_compression": round(
                    orig_total * 2 / (lr_bytes + scale_overhead),
                    2,
                ),
                "q_mb": round(q_mb, 1),
            })

            restore_ffn(model, layer_idx, originals_q)

    return results


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    log(f"\n{'='*60}")
    log("  L0 LOW-RANK FACTORIZATION")
    log("  Can SVD rescue the lexer?")
    log(f"{'='*60}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log()

    # ── Load model ────────────────────────────────────────
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
    log(f"  Layers: {n_layers}, d_model: {d_model},"
        f" intermediate: {intermediate}")

    # Max rank = min(d_model, intermediate) = d_model = 4096
    max_rank = min(d_model, intermediate)
    log(f"  Max SVD rank: {max_rank}")

    # ── Baseline ──────────────────────────────────────────
    log("\n  Measuring baseline...")
    baseline_ppl = measure_ppl(
        model, tokenizer, EVAL_TEXTS, args.device,
    )
    baseline_correct, baseline_total = measure_facts(
        model, tokenizer, args.device,
    )
    baseline_fact_rate = baseline_correct / baseline_total
    log(f"  Baseline PPL: {baseline_ppl:.2f}")
    log(f"  Baseline facts: {baseline_correct}/{baseline_total}"
        f" = {baseline_fact_rate:.0%}")

    # ── Rank sweep ────────────────────────────────────────
    ranks = [
        100, 250, 500, 750, 1000,
        1500, 2000, 2500, 3000, 3500,
        max_rank,
    ]

    all_results = {
        "model": args.model,
        "baseline_ppl": baseline_ppl,
        "baseline_fact_rate": baseline_fact_rate,
        "d_model": d_model,
        "intermediate_size": intermediate,
        "max_rank": max_rank,
        "layers": {},
    }

    for layer_idx, layer_name in [
        (0, "LEXER"),
        (15, "OPTIMIZER (control)"),
    ]:
        layer_results = run_layer_sweep(
            model, tokenizer, layer_idx, args.device,
            baseline_ppl, baseline_correct, ranks,
            layer_name,
        )
        all_results["layers"][str(layer_idx)] = layer_results

    # ══════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*60}")
    log("  SUMMARY")
    log(f"{'='*60}")
    log(f"  Baseline: PPL={baseline_ppl:.2f},"
        f" facts={baseline_fact_rate:.0%}")

    for layer_key, layer_name in [
        ("0", "L0 (LEXER)"),
        ("15", "L15 (OPTIMIZER)"),
    ]:
        log(f"\n  {layer_name}:")
        log(f"  {'rank':>5s}  {'PPL':>7s}  {'ratio':>6s}"
            f"  {'facts':>5s}  {'size':>7s}  {'compress':>8s}"
            f"  {'type':>5s}")
        log(f"  {'---':>5s}  {'---':>7s}  {'---':>6s}"
            f"  {'---':>5s}  {'---':>7s}  {'---':>8s}"
            f"  {'---':>5s}")

        for r in all_results["layers"][layer_key]:
            q = "int8" if r.get("quantized") else "fp16"
            sz = r.get("q_mb") or r.get("lr_mb", "?")
            comp = r.get("total_compression", "?")
            marker = ""
            if isinstance(r["ppl_ratio"], (int, float)):
                if r["ppl_ratio"] < 1.5:
                    marker = " <--"
                elif r["ppl_ratio"] > 10:
                    marker = " !!!"
            log(f"  {r['rank']:>5d}  {r['ppl']:>7.2f}"
                f"  {r['ppl_ratio']:>5.2f}x"
                f"  {r['fact_rate']:>4.0%}"
                f"  {sz:>6}MB"
                f"  {comp:>7}x  {q:>5s}{marker}")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "l0-lowrank"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")
    out_path = out_dir / f"{slug}.json"

    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    log(f"\n  Results saved to {out_path}")
    log(f"\n{'='*60}")
    log("  DONE")
    log(f"{'='*60}\n")


if __name__ == "__main__":
    main()
