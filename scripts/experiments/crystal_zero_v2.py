#!/usr/bin/env python3
"""Crystal zero prediction v2 — gate activation analysis.

The crystal equation predicts which NEURONS are irreducible (dead/zero)
by measuring gate activation patterns across combinator probes AND
diverse corpus inputs.

A neuron is a zero candidate when:
  1. It has low crystal energy (low activation across all combinator modes)
  2. It has low corpus activation (rarely fires for any input)

The crystal equation predicts (1). If (1) and (2) correlate, the
crystal is predictive of zeros.

Key insight: in SwiGLU, the gate activation AFTER sigmoid determines
whether a neuron fires. We measure the POST-GATE activation magnitude
per neuron, not the raw weight norm.

Usage:
  uv run python scripts/experiments/crystal_zero_v2.py --model Qwen/Qwen3-8B

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
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from verbum.probes.library import by_combinator  # noqa: E402

PHI = (1 + np.sqrt(5)) / 2
S = 4 / 5
CRYSTAL_COMBINATORS = ["K", "I", "B", "C", "D", "W", "Y", "WHNF"]
PHASE_BOUNDARY = PHI ** (-S * (2 + PHI))  # ≈ 0.248

# Diverse non-crystal corpus (retrieval, narrative, code, etc.)
DIVERSE_CORPUS = [
    # Factual retrieval
    "The speed of light is approximately 299792458 meters per second.",
    "Tokyo is the capital city of Japan and has a population of about 14 million.",
    "The chemical formula for table salt is NaCl, sodium chloride.",
    "Mount Everest stands at 8849 meters above sea level.",
    "The human body contains approximately 206 bones in the adult skeleton.",
    "The Earth orbits the Sun at an average distance of about 150 million kilometers.",
    "DNA was first identified by Friedrich Miescher in 1869.",
    "The Amazon River is the largest river by discharge volume of water in the world.",
    # Narrative
    "She opened the door slowly, not knowing what she would find on the other side.",
    "The old man sat on the park bench feeding pigeons every morning at sunrise.",
    "Thunder rolled across the valley as the first drops of rain began to fall.",
    "He packed his bags, looked around the empty apartment one last time, and left.",
    # Code
    "def quicksort(arr): return [] if not arr else quicksort([x for x in arr[1:] if x <= arr[0]]) + [arr[0]] + quicksort([x for x in arr[1:] if x > arr[0]])",
    "SELECT u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.name",
    "const fibonacci = n => n <= 1 ? n : fibonacci(n-1) + fibonacci(n-2);",
    "import numpy as np; X = np.random.randn(100, 10); y = X @ np.ones(10) + np.random.randn(100) * 0.1",
    # Instruction
    "Summarize the following text in three bullet points focusing on the main argument.",
    "Translate this paragraph from English to Spanish maintaining the formal register.",
    "Compare and contrast the two approaches listed above.",
    "Extract all dates and monetary amounts from the following document.",
    # Reasoning
    "If all mammals are warm-blooded and whales are mammals, then whales must be warm-blooded.",
    "The pattern is 2, 6, 18, 54 so the next number in the sequence is 162.",
    "Assume for contradiction that the square root of 2 is rational.",
    "Given the constraints, there are exactly 120 possible arrangements.",
]


def get_layers_container(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def capture_gate_activations(model, tokenizer, prompts, layer_idx, device):
    """Capture gate_proj activations for a list of prompts.

    Returns: (n_prompts, d_ff) — mean-pooled over sequence positions.
    For SwiGLU, this is the activation BEFORE the sigmoid gate.
    """
    layers_container = get_layers_container(model)
    intermediate_size = getattr(model.config, 'intermediate_size', None)
    captured = {}

    def hook_fn(module, input, output):
        captured['act'] = output.detach().float()

    gate = getattr(layers_container[layer_idx].mlp, 'gate_proj', None)
    if gate is None:
        gate = getattr(layers_container[layer_idx].mlp, 'dense_h_to_4h', None)
    hook = gate.register_forward_hook(hook_fn)

    all_acts = []
    for prompt in prompts:
        captured.clear()
        inputs = tokenizer(prompt, return_tensors="pt", padding=False,
                           truncation=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            model(**inputs)
        if 'act' in captured:
            act = captured['act']
            if intermediate_size and act.shape[-1] > intermediate_size:
                act = act[..., :intermediate_size]
            all_acts.append(act.mean(dim=1).squeeze(0).cpu().numpy())

    hook.remove()
    return np.array(all_acts)


def main():
    parser = argparse.ArgumentParser(
        description="Crystal zero prediction v2 — gate activation analysis")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--n-per-combinator", type=int, default=25)
    parser.add_argument("--layer", type=int, default=None)
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    if args.device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    else:
        device = args.device

    # Probes
    rng = np.random.RandomState(42)
    probe_dict = {}
    for comb in CRYSTAL_COMBINATORS:
        probes = by_combinator(comb)
        prompts = [p.prompt for p in probes]
        if args.n_per_combinator and len(prompts) > args.n_per_combinator:
            idx = rng.choice(len(prompts), args.n_per_combinator, replace=False)
            prompts = [prompts[i] for i in sorted(idx)]
        probe_dict[comb] = prompts

    total_crystal = sum(len(v) for v in probe_dict.values())

    print(f"\n{'═'*70}")
    print(f"  Crystal Zero Prediction v2 — Gate Activation Analysis")
    print(f"{'═'*70}")
    print(f"  Model: {args.model}")
    print(f"  Crystal probes: {total_crystal}")
    print(f"  Diverse corpus: {len(DIVERSE_CORPUS)}")

    # Load model
    print(f"\n  Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.float16,
        device_map=device if device != "mps" else None,
        trust_remote_code=True,
    )
    if device == "mps":
        model = model.to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    d_ff = getattr(model.config, 'intermediate_size', model.config.hidden_size * 4)
    layer_idx = args.layer if args.layer is not None else int(n_layers * 0.8)
    print(f"  Loaded: {n_layers} layers, d_ff={d_ff}")
    print(f"  Analysis layer: {layer_idx} ({layer_idx/n_layers*100:.0f}%)")

    # ── Capture crystal activations ──────────────────────────────────
    print(f"\n  Capturing crystal gate activations...")
    t0 = time.time()
    crystal_acts = {}
    for comb in CRYSTAL_COMBINATORS:
        acts = capture_gate_activations(
            model, tokenizer, probe_dict[comb], layer_idx, device)
        crystal_acts[comb] = acts

    all_crystal = np.vstack([crystal_acts[c] for c in CRYSTAL_COMBINATORS])
    print(f"  Crystal: {all_crystal.shape} in {time.time()-t0:.1f}s")

    # ── Capture diverse corpus activations ───────────────────────────
    print(f"  Capturing diverse corpus gate activations...")
    t1 = time.time()
    diverse_acts = capture_gate_activations(
        model, tokenizer, DIVERSE_CORPUS, layer_idx, device)
    print(f"  Diverse: {diverse_acts.shape} in {time.time()-t1:.1f}s")

    # ── Per-neuron activation statistics ─────────────────────────────
    print(f"\n{'─'*70}")
    print(f"  PER-NEURON ACTIVATION ANALYSIS")
    print(f"{'─'*70}")

    # Per neuron: mean |activation| across each probe set
    crystal_mean_act = np.mean(np.abs(all_crystal), axis=0)  # (d_ff,)
    diverse_mean_act = np.mean(np.abs(diverse_acts), axis=0)  # (d_ff,)
    combined_mean_act = np.mean(np.abs(np.vstack([all_crystal, diverse_acts])), axis=0)

    # Per-combinator activation per neuron
    per_comb_act = {}
    for comb in CRYSTAL_COMBINATORS:
        per_comb_act[comb] = np.mean(np.abs(crystal_acts[comb]), axis=0)

    print(f"\n  Activation magnitude per neuron ({d_ff} neurons):")
    for label, arr in [("Crystal probes", crystal_mean_act),
                       ("Diverse corpus", diverse_mean_act),
                       ("Combined", combined_mean_act)]:
        print(f"    {label:>16}: mean={arr.mean():.4f}, std={arr.std():.4f}, "
              f"min={arr.min():.4f}, max={arr.max():.4f}")

    # ── Crystal PCA and energy ───────────────────────────────────────
    print(f"\n  Computing crystal PCA basis...")
    centered = all_crystal - all_crystal.mean(axis=0)
    U, S_vals, Vt = np.linalg.svd(centered, full_matrices=False)
    n_modes = min(16, len(S_vals))
    eigenvalues = (S_vals[:n_modes] ** 2) / (len(all_crystal) - 1)
    eigenvectors = Vt[:n_modes]

    # Crystal energy per neuron: how much crystal structure each neuron carries
    crystal_energy = np.zeros(d_ff)
    for k in range(n_modes):
        crystal_energy += eigenvalues[k] * eigenvectors[k] ** 2

    # ── Correlation: crystal energy vs activation magnitude ──────────
    print(f"\n{'─'*70}")
    print(f"  CORRELATION: CRYSTAL ENERGY vs ACTIVATION MAGNITUDE")
    print(f"{'─'*70}")

    from scipy import stats as sp_stats

    for label, act_mag in [("Crystal", crystal_mean_act),
                           ("Diverse", diverse_mean_act),
                           ("Combined", combined_mean_act)]:
        pearson = np.corrcoef(crystal_energy, act_mag)[0, 1]
        spearman, sp = sp_stats.spearmanr(crystal_energy, act_mag)
        print(f"  {label:>10} — Pearson: {pearson:.4f}, Spearman: {spearman:.4f} (p={sp:.2e})")

    # ── Key test: do low-crystal-energy neurons also have low diverse activation? ─
    print(f"\n{'─'*70}")
    print(f"  ZERO PREDICTION: CRYSTAL ENERGY → DEAD NEURONS")
    print(f"{'─'*70}")

    # Sort neurons by crystal energy
    ce_rank = np.argsort(crystal_energy)  # lowest crystal energy first

    # For each percentile of crystal energy, what is the mean activation?
    print(f"\n  {'CE percentile':>14} {'Mean crystal act':>17} {'Mean diverse act':>17} {'Mean combined':>14} {'Ratio div/cryst':>16}")
    print(f"  {'─'*14} {'─'*17} {'─'*17} {'─'*14} {'─'*16}")

    for pct in [1, 5, 10, 20, 30, 50, 70, 90, 100]:
        n = max(1, int(d_ff * pct / 100))
        neurons = ce_rank[:n]
        ca = crystal_mean_act[neurons].mean()
        da = diverse_mean_act[neurons].mean()
        co = combined_mean_act[neurons].mean()
        ratio = da / ca if ca > 1e-6 else float('inf')
        print(f"  Bottom {pct:>3}% CE {ca:>17.4f} {da:>17.4f} {co:>14.4f} {ratio:>16.2f}")

    # Flip: sort by diverse activation — do dead diverse neurons have low crystal energy?
    da_rank = np.argsort(diverse_mean_act)

    print(f"\n  {'DA percentile':>14} {'Mean crystal E':>15} {'Mean diverse act':>17} {'CE/mean CE':>11}")
    print(f"  {'─'*14} {'─'*15} {'─'*17} {'─'*11}")
    mean_ce = crystal_energy.mean()
    for pct in [1, 5, 10, 20, 30, 50, 70, 90, 100]:
        n = max(1, int(d_ff * pct / 100))
        neurons = da_rank[:n]
        ce = crystal_energy[neurons].mean()
        da = diverse_mean_act[neurons].mean()
        print(f"  Bottom {pct:>3}% DA {ce:>15.6f} {da:>17.4f} {ce/mean_ce:>11.3f}")

    # ── Activation sparsity ──────────────────────────────────────────
    print(f"\n{'─'*70}")
    print(f"  ACTIVATION SPARSITY ANALYSIS")
    print(f"{'─'*70}")

    # What fraction of neurons have activation below threshold?
    # In SwiGLU, the gate output goes through SiLU. Negative gate → near-zero output.
    # Count neurons where gate activation is predominantly negative (near-zero after SiLU)
    crystal_sign = np.mean(all_crystal > 0, axis=0)  # fraction of times neuron fires positive
    diverse_sign = np.mean(diverse_acts > 0, axis=0)
    combined_sign = np.mean(np.vstack([all_crystal, diverse_acts]) > 0, axis=0)

    print(f"\n  Neurons by positive-activation fraction:")
    for thresh in [0.01, 0.05, 0.1, 0.2, 0.5]:
        n_crystal = (crystal_sign < thresh).sum()
        n_diverse = (diverse_sign < thresh).sum()
        n_combined = (combined_sign < thresh).sum()
        print(f"    <{thresh:>4.0%} positive: crystal={n_crystal:>5} ({n_crystal/d_ff*100:.1f}%), "
              f"diverse={n_diverse:>5} ({n_diverse/d_ff*100:.1f}%), "
              f"combined={n_combined:>5} ({n_combined/d_ff*100:.1f}%)")

    # Dead neurons: rarely positive in BOTH crystal AND diverse
    dead_both = ((crystal_sign < 0.05) & (diverse_sign < 0.05)).sum()
    dead_crystal_only = ((crystal_sign < 0.05) & (diverse_sign >= 0.05)).sum()
    dead_diverse_only = ((crystal_sign >= 0.05) & (diverse_sign < 0.05)).sum()
    alive = ((crystal_sign >= 0.05) & (diverse_sign >= 0.05)).sum()

    print(f"\n  Neuron classification (5% positive threshold):")
    print(f"    Dead in both:        {dead_both:>5} ({dead_both/d_ff*100:.1f}%) ← zero candidates")
    print(f"    Dead crystal only:   {dead_crystal_only:>5} ({dead_crystal_only/d_ff*100:.1f}%) ← non-crystal neurons")
    print(f"    Dead diverse only:   {dead_diverse_only:>5} ({dead_diverse_only/d_ff*100:.1f}%) ← crystal-only neurons")
    print(f"    Alive in both:       {alive:>5} ({alive/d_ff*100:.1f}%)")

    # ── Crystal energy of dead vs alive neurons ──────────────────────
    dead_mask = (combined_sign < 0.05)
    alive_mask = ~dead_mask
    if dead_mask.sum() > 0 and alive_mask.sum() > 0:
        ce_dead = crystal_energy[dead_mask].mean()
        ce_alive = crystal_energy[alive_mask].mean()
        print(f"\n  Crystal energy: dead={ce_dead:.6f}, alive={ce_alive:.6f}")
        print(f"  Ratio alive/dead: {ce_alive/ce_dead:.2f}x")
        print(f"  The crystal equation predicts this ratio should be ≈ φ^(s·Δβ)")

    # ── Save results ─────────────────────────────────────────────────
    model_slug = args.model.replace("/", "_")
    output_path = args.output or f"results/crystal-phi-verify/{model_slug}_zero_v2.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def jsonable(obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, dict): return {k: jsonable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)): return [jsonable(v) for v in obj]
        return obj

    results = jsonable({
        "model": args.model,
        "layer": layer_idx,
        "d_ff": d_ff,
        "n_crystal_probes": total_crystal,
        "n_diverse_probes": len(DIVERSE_CORPUS),
        "dead_both": int(dead_both),
        "dead_crystal_only": int(dead_crystal_only),
        "dead_diverse_only": int(dead_diverse_only),
        "alive_both": int(alive),
        "dead_fraction": float(dead_both / d_ff),
        "crystal_energy_dead": float(ce_dead) if dead_mask.sum() > 0 else None,
        "crystal_energy_alive": float(ce_alive) if alive_mask.sum() > 0 else None,
        "correlations": {
            "crystal_energy_vs_crystal_act": float(np.corrcoef(crystal_energy, crystal_mean_act)[0,1]),
            "crystal_energy_vs_diverse_act": float(np.corrcoef(crystal_energy, diverse_mean_act)[0,1]),
            "crystal_act_vs_diverse_act": float(np.corrcoef(crystal_mean_act, diverse_mean_act)[0,1]),
        },
    })

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Saved to {output_path}")
    print(f"{'═'*70}\n")


if __name__ == "__main__":
    main()
