#!/usr/bin/env python3
"""Test: what does the holographic computer do with ⊥ (bottom)?

The transformer is a 36-layer typed shift-reduce parser with 9 ternary
opcodes per layer. Normal inputs rotate the residual 325° through a spiral,
each layer cleanly selecting one of 9 modes. What happens with non-terminating
lambda expressions?

Theory:
  - Ω = (λx.x x)(λx.x x) reduces to itself — infinite loop
  - In a fixed-depth pipeline, the model CAN'T loop — it does 36 layers, period
  - Hypothesis 1: Model QUOTES (recognizes non-termination, outputs the expression)
  - Hypothesis 2: Model JAMS (mode selection becomes ambiguous, entropy spikes)
  - Hypothesis 3: Model DEFAULTS (falls back to a safe mode, low entropy)

Measurements per prompt:
  1. Residual angular velocity per layer (rotation rate)
  2. Residual norm growth per layer (spiral expansion)
  3. FFN mode confidence per layer (max gate activation / softmax)
  4. Output logit entropy (model uncertainty about next token)
  5. Layer-to-layer cosine (rotation smoothness vs fragmentation)
  6. Model generation (what does it actually output?)

Prompt categories:
  OMEGA:   non-terminating lambda expressions (Ω, M, K I Ω, Y(λx.x))
  CONTROL: terminating reductions (I a, K a b, B f g x)
  PROSE:   normal English text (baseline)

Usage:
  uv run python scripts/experiments/omega_probe.py --model Qwen/Qwen3-8B --device mps

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
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

# ══════════════════════════════════════════════════════════════════════
# Prompt sets
# ══════════════════════════════════════════════════════════════════════

OMEGA_PROMPTS = [
    {
        "id": "omega",
        "category": "omega",
        "label": "Ω = self-application loop",
        "prompt": "Reduce the following lambda expression to normal form.\n\nΩ = (λx.x x)(λx.x x)\n\nReduction:",
    },
    {
        "id": "omega_bare",
        "category": "omega",
        "label": "Ω bare (no instructions)",
        "prompt": "(λx.x x)(λx.x x)",
    },
    {
        "id": "big_omega",
        "category": "omega",
        "label": "M = growing self-application",
        "prompt": "Reduce the following lambda expression to normal form.\n\nM = (λx.x x x)(λx.x x x)\n\nReduction:",
    },
    {
        "id": "k_i_omega",
        "category": "omega",
        "label": "K I Ω — discard ⊥ (lazy=I, strict=⊥)",
        "prompt": "Reduce the following lambda expression to normal form.\n\n(λx.λy.x)(λz.z)((λx.x x)(λx.x x))\n\nReduction:",
    },
    {
        "id": "y_id",
        "category": "omega",
        "label": "Y(λx.x) — fixpoint of identity",
        "prompt": "Reduce the following lambda expression to normal form.\n\nY (λx.x)\n\nwhere Y = λf.(λx.f(x x))(λx.f(x x))\n\nReduction:",
    },
    {
        "id": "omega_omega",
        "category": "omega",
        "label": "Ω Ω — applying ⊥ to ⊥",
        "prompt": "Reduce the following lambda expression to normal form.\n\n((λx.x x)(λx.x x)) ((λx.x x)(λx.x x))\n\nReduction:",
    },
    {
        "id": "s_i_i_omega",
        "category": "omega",
        "label": "S I I (S I I) — SKI Ω",
        "prompt": "Reduce the following lambda expression to normal form.\n\nS I I (S I I)\n\nwhere S = λf.λg.λx.f x (g x), I = λx.x\n\nReduction:",
    },
]

CONTROL_PROMPTS = [
    {
        "id": "i_reduce",
        "category": "control",
        "label": "I a → a (identity)",
        "prompt": "Reduce the following lambda expression to normal form.\n\n(λx.x) a\n\nReduction:",
    },
    {
        "id": "k_reduce",
        "category": "control",
        "label": "K a b → a (discard)",
        "prompt": "Reduce the following lambda expression to normal form.\n\n(λx.λy.x) a b\n\nReduction:",
    },
    {
        "id": "b_reduce",
        "category": "control",
        "label": "B f g x → f(g x) (compose)",
        "prompt": "Reduce the following lambda expression to normal form.\n\n(λf.λg.λx.f(g x)) f g a\n\nReduction:",
    },
    {
        "id": "s_reduce",
        "category": "control",
        "label": "S K K x → x (S combinator)",
        "prompt": "Reduce the following lambda expression to normal form.\n\n(λf.λg.λx.f x (g x)) (λx.λy.x) (λx.λy.x) a\n\nReduction:",
    },
    {
        "id": "church_2_succ",
        "category": "control",
        "label": "succ 2 → 3 (Church numeral)",
        "prompt": "Reduce the following lambda expression to normal form.\n\n(λn.λf.λx.f(n f x))(λf.λx.f(f x))\n\nReduction:",
    },
    {
        "id": "k_i",
        "category": "control",
        "label": "K I → (λy.I) — partial application",
        "prompt": "Reduce the following lambda expression to normal form.\n\n(λx.λy.x)(λz.z)\n\nReduction:",
    },
    {
        "id": "nested_beta",
        "category": "control",
        "label": "(λx.(λy.y) x) a → a — nested",
        "prompt": "Reduce the following lambda expression to normal form.\n\n(λx.(λy.y) x) a\n\nReduction:",
    },
]

PROSE_PROMPTS = [
    {
        "id": "prose_science",
        "category": "prose",
        "label": "Science fact",
        "prompt": "The theory of general relativity describes gravity as the curvature of spacetime caused by mass and energy.",
    },
    {
        "id": "prose_recipe",
        "category": "prose",
        "label": "Recipe",
        "prompt": "In a large mixing bowl, combine the flour, sugar, and baking powder. Make a well in the center.",
    },
    {
        "id": "prose_story",
        "category": "prose",
        "label": "Narrative",
        "prompt": "She walked through the ancient forest, her footsteps muffled by centuries of fallen leaves.",
    },
    {
        "id": "prose_code",
        "category": "prose",
        "label": "Code description",
        "prompt": "The function takes two arguments and returns their composition as a new callable object.",
    },
    {
        "id": "prose_history",
        "category": "prose",
        "label": "History",
        "prompt": "During the Cambrian explosion, roughly 541 million years ago, most major animal phyla appeared.",
    },
    {
        "id": "prose_math",
        "category": "prose",
        "label": "Math instruction",
        "prompt": "To solve this equation, first isolate the variable on one side by subtracting three from both sides.",
    },
    {
        "id": "prose_capital",
        "category": "prose",
        "label": "Factual",
        "prompt": "The capital of France is Paris, which has been the country's capital since the 10th century.",
    },
]

ALL_PROMPTS = OMEGA_PROMPTS + CONTROL_PROMPTS + PROSE_PROMPTS


# ══════════════════════════════════════════════════════════════════════
# Model helpers
# ══════════════════════════════════════════════════════════════════════

def get_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def cosine_sim(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-10 or nb < 1e-10:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ══════════════════════════════════════════════════════════════════════
# Core measurement: capture everything in one forward pass
# ══════════════════════════════════════════════════════════════════════

def full_probe(model, tokenizer, text, device):
    """One forward pass, capture:
      - residual at every layer (after layer norm + attention + FFN)
      - FFN gate activations at every layer (mode confidence)
      - final logits (output entropy)
    Returns dict of numpy arrays.
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    seq_len = inputs["input_ids"].shape[1]

    layers = get_layers(model)
    n_layers = len(layers)

    residuals = {}  # layer_idx → (seq, d_model) float32
    gate_acts = {}  # layer_idx → (seq, intermediate) float32
    handles = []

    # Capture embedding
    embed_module = None
    if hasattr(model, 'model') and hasattr(model.model, 'embed_tokens'):
        embed_module = model.model.embed_tokens

    if embed_module:
        def embed_hook(module, input, output):
            residuals['embed'] = output.detach().float().cpu()
        handles.append(embed_module.register_forward_hook(embed_hook))

    # Capture residual after each layer + gate activations
    for i, layer in enumerate(layers):
        def make_residual_hook(idx):
            def hook_fn(module, input, output):
                h = output[0] if isinstance(output, tuple) else output
                residuals[idx] = h.detach().float().cpu()
            return hook_fn
        handles.append(layer.register_forward_hook(make_residual_hook(i)))

        # Hook the gate projection to measure mode confidence
        # Qwen3 uses gate_proj in the MLP
        mlp = layer.mlp
        if hasattr(mlp, 'gate_proj'):
            def make_gate_hook(idx):
                def hook_fn(module, input, output):
                    gate_acts[idx] = output.detach().float().cpu()
                return hook_fn
            handles.append(mlp.gate_proj.register_forward_hook(make_gate_hook(i)))

    # Forward pass with logits
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits.detach().float().cpu()  # (1, seq, vocab)

    for h in handles:
        h.remove()

    # ── Process residuals ─────────────────────────────────────────
    ordered_residuals = []
    if 'embed' in residuals:
        ordered_residuals.append(residuals['embed'][0].numpy())
    for i in range(n_layers):
        if i in residuals:
            ordered_residuals.append(residuals[i][0].numpy())

    # ── Angular velocity (consecutive layer angle) ────────────────
    angles = []
    for i in range(len(ordered_residuals) - 1):
        # Use LAST token position (the one the model is predicting from)
        a = ordered_residuals[i][-1]
        b = ordered_residuals[i + 1][-1]
        cos = np.clip(cosine_sim(a, b), -1, 1)
        angles.append(float(np.degrees(np.arccos(cos))))

    # ── Norm growth ───────────────────────────────────────────────
    norms = [float(np.linalg.norm(r[-1])) for r in ordered_residuals]

    # ── Layer-to-layer cosine ─────────────────────────────────────
    consec_cos = []
    for i in range(len(ordered_residuals) - 1):
        cos = cosine_sim(ordered_residuals[i][-1], ordered_residuals[i + 1][-1])
        consec_cos.append(float(cos))

    # ── Gate mode confidence per layer ────────────────────────────
    # For each layer, look at gate activations at last token position
    # Measure: how concentrated is the activation? (like top-k / total)
    gate_metrics = []
    for i in range(n_layers):
        if i in gate_acts:
            g = gate_acts[i][0, -1].numpy()  # (intermediate,) at last token
            g_abs = np.abs(g)
            g_sorted = np.sort(g_abs)[::-1]
            total = g_abs.sum() + 1e-10

            # Top-k concentration
            top1_frac = float(g_sorted[0] / total)
            top10_frac = float(g_sorted[:10].sum() / total)
            top100_frac = float(g_sorted[:100].sum() / total)

            # Sparsity: fraction of neurons with |g| > 0.1 * max
            active_frac = float((g_abs > 0.1 * g_sorted[0]).sum() / len(g_abs))

            # Entropy of |g| distribution (normalized)
            g_prob = g_abs / total
            g_prob = g_prob[g_prob > 1e-10]
            entropy = float(-np.sum(g_prob * np.log2(g_prob)))

            gate_metrics.append({
                "layer": i,
                "top1_frac": top1_frac,
                "top10_frac": top10_frac,
                "top100_frac": top100_frac,
                "active_frac": active_frac,
                "entropy": entropy,
                "max_activation": float(g_sorted[0]),
                "mean_activation": float(g_abs.mean()),
            })
        else:
            gate_metrics.append({"layer": i, "error": "no gate captured"})

    # ── Output logit entropy ──────────────────────────────────────
    # At the last token position
    last_logits = logits[0, -1]  # (vocab,)
    probs = F.softmax(last_logits, dim=0)
    log_probs = F.log_softmax(last_logits, dim=0)
    output_entropy = float(-torch.sum(probs * log_probs).item())

    # Top-5 tokens
    top5_vals, top5_idx = torch.topk(probs, 5)
    top5_tokens = []
    for val, idx in zip(top5_vals, top5_idx):
        tok = tokenizer.decode([idx.item()])
        top5_tokens.append({"token": tok, "prob": float(val.item())})

    # Top-1 probability
    top1_prob = float(top5_vals[0].item())

    return {
        "angles_deg": angles,
        "norms": norms,
        "consec_cos": consec_cos,
        "gate_metrics": gate_metrics,
        "output_entropy": output_entropy,
        "top1_prob": top1_prob,
        "top5_tokens": top5_tokens,
        "seq_len": seq_len,
        "total_rotation_deg": float(sum(angles)),
    }


def generate_text(model, tokenizer, prompt, max_new_tokens=80, device="cpu"):
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            do_sample=False, temperature=1.0,
            pad_token_id=tokenizer.pad_token_id)
    generated = outputs[0][inputs['input_ids'].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  OMEGA PROBE — What does the holographic computer do with ⊥?")
    print(f"  Can a lambda expression stop an LLM?")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print()

    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    print(f"  Loading {args.model}...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    n_layers = model.config.num_hidden_layers
    print(f"  Layers: {n_layers}")

    # ══════════════════════════════════════════════════════════════
    # Phase 1: Probe all prompts
    # ══════════════════════════════════════════════════════════════

    all_results = {}

    for prompt_set_name, prompt_set in [("omega", OMEGA_PROMPTS),
                                         ("control", CONTROL_PROMPTS),
                                         ("prose", PROSE_PROMPTS)]:
        print(f"\n{'─'*70}")
        print(f"  Probing {prompt_set_name.upper()} expressions ({len(prompt_set)} prompts)")
        print(f"{'─'*70}")

        for p_info in prompt_set:
            pid = p_info["id"]
            print(f"\n    [{pid}] {p_info['label']}")
            print(f"    Prompt: {p_info['prompt'][:80]}...")

            # Probe internals
            metrics = full_probe(model, tokenizer, p_info["prompt"], args.device)

            # Generate output
            gen = generate_text(model, tokenizer, p_info["prompt"],
                                max_new_tokens=80, device=args.device)
            metrics["generation"] = gen.strip()
            metrics["prompt_id"] = pid
            metrics["category"] = p_info["category"]
            metrics["label"] = p_info["label"]
            metrics["prompt"] = p_info["prompt"]

            all_results[pid] = metrics

            # Quick summary
            print(f"    Total rotation: {metrics['total_rotation_deg']:.1f}°")
            print(f"    Output entropy: {metrics['output_entropy']:.2f} bits")
            print(f"    Top-1 prob: {metrics['top1_prob']:.3f}")
            print(f"    Generation: {gen.strip()[:100]}")

    # ══════════════════════════════════════════════════════════════
    # Phase 2: Comparative analysis
    # ══════════════════════════════════════════════════════════════

    print(f"\n\n{'='*70}")
    print(f"  COMPARATIVE ANALYSIS")
    print(f"{'='*70}")

    categories = {"omega": [], "control": [], "prose": []}
    for pid, m in all_results.items():
        categories[m["category"]].append(m)

    # ── Test 1: Total rotation ────────────────────────────────────
    print(f"\n  Test 1: Total residual rotation (degrees)")
    print(f"  {'Category':>10s}  {'Mean':>8s}  {'Std':>8s}  {'Min':>8s}  {'Max':>8s}")
    for cat in ["omega", "control", "prose"]:
        rots = [m["total_rotation_deg"] for m in categories[cat]]
        print(f"  {cat:>10s}  {np.mean(rots):>8.1f}  {np.std(rots):>8.1f}  "
              f"{np.min(rots):>8.1f}  {np.max(rots):>8.1f}")

    # ── Test 2: Output entropy ────────────────────────────────────
    print(f"\n  Test 2: Output logit entropy (bits)")
    print(f"  {'Category':>10s}  {'Mean':>8s}  {'Std':>8s}  {'Min':>8s}  {'Max':>8s}")
    for cat in ["omega", "control", "prose"]:
        ents = [m["output_entropy"] for m in categories[cat]]
        print(f"  {cat:>10s}  {np.mean(ents):>8.2f}  {np.std(ents):>8.2f}  "
              f"{np.min(ents):>8.2f}  {np.max(ents):>8.2f}")

    # ── Test 3: Top-1 probability ─────────────────────────────────
    print(f"\n  Test 3: Top-1 token probability (confidence)")
    print(f"  {'Category':>10s}  {'Mean':>8s}  {'Std':>8s}  {'Min':>8s}  {'Max':>8s}")
    for cat in ["omega", "control", "prose"]:
        probs = [m["top1_prob"] for m in categories[cat]]
        print(f"  {cat:>10s}  {np.mean(probs):>8.3f}  {np.std(probs):>8.3f}  "
              f"{np.min(probs):>8.3f}  {np.max(probs):>8.3f}")

    # ── Test 4: Per-layer angular velocity comparison ─────────────
    print(f"\n  Test 4: Per-layer angular velocity (Ω vs Control vs Prose)")
    print(f"  {'Layer':>7s}", end="")
    for cat in ["omega", "control", "prose"]:
        print(f"  {cat:>8s}", end="")
    print(f"  {'Ω-Ctrl':>8s}  {'Ω-Prose':>8s}")

    # Compute mean angle per layer per category
    max_depth = min(len(m["angles_deg"]) for m in all_results.values())
    cat_angles = {}
    for cat in ["omega", "control", "prose"]:
        angles_by_layer = [[] for _ in range(max_depth)]
        for m in categories[cat]:
            for i in range(max_depth):
                if i < len(m["angles_deg"]):
                    angles_by_layer[i].append(m["angles_deg"][i])
        cat_angles[cat] = [np.mean(a) if a else 0 for a in angles_by_layer]

    for i in range(max_depth):
        label = "emb→L0" if i == 0 else f"L{i-1}→L{i}"
        oa = cat_angles["omega"][i]
        ca = cat_angles["control"][i]
        pa = cat_angles["prose"][i]
        d_ctrl = oa - ca
        d_prose = oa - pa
        print(f"  {label:>7s}  {oa:>8.2f}  {ca:>8.2f}  {pa:>8.2f}  "
              f"{d_ctrl:>+8.2f}  {d_prose:>+8.2f}")

    # ── Test 5: Gate sparsity per layer ───────────────────────────
    print(f"\n  Test 5: Gate activation entropy (mode ambiguity)")
    print(f"  {'Layer':>7s}", end="")
    for cat in ["omega", "control", "prose"]:
        print(f"  {cat:>8s}", end="")
    print(f"  {'Ω-Ctrl':>8s}")

    for layer_idx in range(0, n_layers, 3):  # sample every 3 layers
        row = {}
        for cat in ["omega", "control", "prose"]:
            entropies = []
            for m in categories[cat]:
                gm = m["gate_metrics"]
                if layer_idx < len(gm) and "entropy" in gm[layer_idx]:
                    entropies.append(gm[layer_idx]["entropy"])
            row[cat] = np.mean(entropies) if entropies else 0

        d = row["omega"] - row["control"]
        print(f"  L{layer_idx:>5d}  {row['omega']:>8.2f}  {row['control']:>8.2f}  "
              f"{row['prose']:>8.2f}  {d:>+8.2f}")

    # ── Test 6: Norm growth comparison ────────────────────────────
    print(f"\n  Test 6: Norm growth (final / initial ratio)")
    print(f"  {'Category':>10s}  {'Init':>8s}  {'Final':>8s}  {'Ratio':>8s}")
    for cat in ["omega", "control", "prose"]:
        inits = [m["norms"][0] for m in categories[cat]]
        finals = [m["norms"][-1] for m in categories[cat]]
        ratios = [f / (i + 1e-10) for i, f in zip(inits, finals)]
        print(f"  {cat:>10s}  {np.mean(inits):>8.1f}  {np.mean(finals):>8.1f}  "
              f"{np.mean(ratios):>8.1f}")

    # ── Test 7: What does it actually generate? ───────────────────
    print(f"\n  Test 7: Generations")
    print(f"  {'─'*68}")
    for cat in ["omega", "control", "prose"]:
        print(f"\n  [{cat.upper()}]")
        for m in categories[cat]:
            gen = m["generation"][:120]
            print(f"    {m['label'][:40]:<40s}")
            print(f"      → {gen}")
    print(f"  {'─'*68}")

    # ── Test 8: Per-prompt detail table ───────────────────────────
    print(f"\n  Test 8: Full metrics per prompt")
    print(f"  {'ID':>18s}  {'Cat':>7s}  {'Rot°':>7s}  {'Entropy':>8s}  "
          f"{'Top1':>6s}  {'NormRatio':>9s}  {'SeqLen':>6s}")
    for pid in sorted(all_results.keys()):
        m = all_results[pid]
        norm_ratio = m["norms"][-1] / (m["norms"][0] + 1e-10)
        print(f"  {pid:>18s}  {m['category']:>7s}  {m['total_rotation_deg']:>7.1f}  "
              f"{m['output_entropy']:>8.2f}  {m['top1_prob']:>6.3f}  "
              f"{norm_ratio:>9.1f}  {m['seq_len']:>6d}")

    # ── Test 9: Ω signature — does rotation diverge or converge? ──
    print(f"\n  Test 9: Ω signature — rotation pattern analysis")
    print(f"  {'─'*68}")

    for pid, m in all_results.items():
        if m["category"] != "omega":
            continue
        angles = m["angles_deg"]
        # Split into thirds
        n = len(angles)
        third = n // 3
        early = np.mean(angles[:third])
        mid = np.mean(angles[third:2*third])
        late = np.mean(angles[2*third:])
        trend = "ACCELERATING" if late > early * 1.1 else (
                "DECELERATING" if late < early * 0.9 else "STEADY")
        print(f"    {pid:>18s}: early={early:.2f}° mid={mid:.2f}° "
              f"late={late:.2f}° → {trend}")

    print(f"\n  [CONTROL baseline]")
    for pid, m in all_results.items():
        if m["category"] != "control":
            continue
        angles = m["angles_deg"]
        n = len(angles)
        third = n // 3
        early = np.mean(angles[:third])
        mid = np.mean(angles[third:2*third])
        late = np.mean(angles[2*third:])
        trend = "ACCELERATING" if late > early * 1.1 else (
                "DECELERATING" if late < early * 0.9 else "STEADY")
        print(f"    {pid:>18s}: early={early:.2f}° mid={mid:.2f}° "
              f"late={late:.2f}° → {trend}")

    # ── Verdict ───────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  VERDICT")
    print(f"{'='*70}")

    omega_entropy = np.mean([m["output_entropy"] for m in categories["omega"]])
    ctrl_entropy = np.mean([m["output_entropy"] for m in categories["control"]])
    prose_entropy = np.mean([m["output_entropy"] for m in categories["prose"]])

    omega_rot = np.mean([m["total_rotation_deg"] for m in categories["omega"]])
    ctrl_rot = np.mean([m["total_rotation_deg"] for m in categories["control"]])
    prose_rot = np.mean([m["total_rotation_deg"] for m in categories["prose"]])

    omega_top1 = np.mean([m["top1_prob"] for m in categories["omega"]])
    ctrl_top1 = np.mean([m["top1_prob"] for m in categories["control"]])

    print(f"\n  Output entropy:    Ω={omega_entropy:.2f}  Control={ctrl_entropy:.2f}  "
          f"Prose={prose_entropy:.2f}")
    print(f"  Total rotation:    Ω={omega_rot:.1f}°   Control={ctrl_rot:.1f}°   "
          f"Prose={prose_rot:.1f}°")
    print(f"  Top-1 confidence:  Ω={omega_top1:.3f}  Control={ctrl_top1:.3f}")

    if omega_entropy > ctrl_entropy * 1.5:
        print(f"\n  → HYPOTHESIS 2 (JAM): Ω increases output entropy by "
              f"{omega_entropy/ctrl_entropy:.1f}×")
        print(f"    The holographic computer JAMS on ⊥ — mode selection is ambiguous")
    elif omega_top1 > ctrl_top1:
        print(f"\n  → HYPOTHESIS 3 (DEFAULT): Ω produces HIGHER confidence than control")
        print(f"    The model defaults to a safe mode — it knows what ⊥ is")
    else:
        print(f"\n  → HYPOTHESIS 1 (QUOTE): Model handles ⊥ similarly to normal reductions")
        print(f"    It quotes/describes non-termination rather than attempting it")

    if abs(omega_rot - ctrl_rot) > 20:
        print(f"\n  ROTATION ANOMALY: Ω rotates {omega_rot - ctrl_rot:+.1f}° "
              f"{'more' if omega_rot > ctrl_rot else 'less'} than control")
        print(f"    The spiral {'expands' if omega_rot > ctrl_rot else 'contracts'} "
              f"for non-terminating expressions")
    else:
        print(f"\n  Rotation is similar across categories (Δ={omega_rot - ctrl_rot:+.1f}°)")

    # ── Save ──────────────────────────────────────────────────────
    out_dir = Path("results/omega-probe")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    save_data = {
        "model": args.model,
        "n_layers": n_layers,
        "prompts": {pid: {
            "category": m["category"],
            "label": m["label"],
            "prompt": m["prompt"],
            "generation": m["generation"],
            "total_rotation_deg": m["total_rotation_deg"],
            "output_entropy": m["output_entropy"],
            "top1_prob": m["top1_prob"],
            "top5_tokens": m["top5_tokens"],
            "angles_deg": m["angles_deg"],
            "norms": m["norms"],
            "consec_cos": m["consec_cos"],
            "gate_metrics": m["gate_metrics"],
            "seq_len": m["seq_len"],
        } for pid, m in all_results.items()},
        "summary": {
            "omega_entropy": float(omega_entropy),
            "control_entropy": float(ctrl_entropy),
            "prose_entropy": float(prose_entropy),
            "omega_rotation": float(omega_rot),
            "control_rotation": float(ctrl_rot),
            "prose_rotation": float(prose_rot),
            "omega_top1": float(omega_top1),
            "control_top1": float(ctrl_top1),
        },
    }
    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
