#!/usr/bin/env python3
"""Hybrid ternarization: crystal neuron budget + magnitude weight selection.

The hybrid strategy:
  - Dead neurons (gate rarely positive) → 100% zeros (all 4096 weights)
  - Alive neurons → magnitude-based zeros at a LOWER rate
  - Total zero budget matches pure magnitude baseline

This tests whether concentrating zeros on truly-dead neurons (crystal)
while preserving more weights in alive neurons (magnitude) beats
spreading zeros uniformly across all neurons.

Usage:
  uv run python scripts/experiments/crystal_hybrid_ternarize.py --model Qwen/Qwen3-8B
"""

from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))
from verbum.probes.library import by_combinator  # noqa: E402

CRYSTAL_COMBINATORS = ["K", "I", "B", "C", "D", "W", "Y", "WHNF"]

CORPUS = [
    "The speed of light is approximately 299792458 meters per second.",
    "Tokyo is the capital city of Japan with about 14 million people.",
    "She opened the door slowly, not knowing what she would find.",
    "The old man sat on the bench feeding pigeons every morning.",
    "def quicksort(arr): return [] if not arr else quicksort([x for x in arr[1:] if x <= arr[0]]) + [arr[0]]",
    "If all mammals are warm-blooded and whales are mammals, then whales are warm-blooded.",
    "NaCl is the chemical formula for table salt, sodium chloride.",
    "He packed his bags and left the empty apartment one last time.",
    "SELECT u.name, COUNT(o.id) FROM users u JOIN orders o ON u.id = o.user_id",
    "The pattern is 2, 6, 18, 54 so the next number is 162.",
    "Mount Everest stands at 8849 meters above sea level.",
    "Thunder rolled across the valley as rain began to fall.",
    "import numpy as np; X = np.random.randn(100, 10)",
    "Summarize the following text in three bullet points.",
    "The Earth orbits the Sun at about 150 million kilometers.",
    "Compare and contrast the two approaches listed above.",
    "DNA was first identified by Friedrich Miescher in 1869.",
    "The Amazon River is the largest by discharge volume in the world.",
    "Assume for contradiction that the square root of 2 is rational.",
    "Extract all dates and amounts from the following document.",
    "Among the candidates, the committee chose the most experienced.",
    "After washing the dishes, she dried them carefully.",
    "The book that the student read was difficult to understand.",
    "The mirror reflected the mirror reflecting the mirror endlessly.",
    "Despite everything else, the only thing that matters is the result.",
    "First sort the list, then reverse it to get descending order.",
    "The letter was written by the diplomat during the conference.",
    "He himself admitted that he himself was wrong about the claim.",
    "The capital of France is Paris, located on the Seine River.",
    "Water boils at 100 degrees Celsius at standard atmospheric pressure.",
]


def get_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    raise RuntimeError("Cannot find layers")


def silu(x):
    return x / (1 + np.exp(-np.clip(x, -20, 20)))


def ternarize_row(row, zero_frac):
    """Ternarize a single weight row: zero smallest |w|, sign rest."""
    if zero_frac <= 0:
        t = np.sign(row)
    elif zero_frac >= 1:
        return np.zeros_like(row), 0.0
    else:
        thresh = np.percentile(np.abs(row), zero_frac * 100)
        t = np.where(np.abs(row) >= thresh, np.sign(row), 0)
    gamma = np.dot(row, t) / (np.dot(t, t) + 1e-12)
    return t, gamma


def ffn_cosine(W_gate, W_up, T_gate, gammas, hidden_states):
    """Compute mean cosine between float and ternary FFN outputs."""
    W_t = gammas[:, None] * T_gate
    cosines = []
    for h in hidden_states:
        y_float = silu(W_gate @ h) * (W_up @ h)
        y_ternary = silu(W_t @ h) * (W_up @ h)
        cos = np.dot(y_float, y_ternary) / (np.linalg.norm(y_float) * np.linalg.norm(y_ternary) + 1e-12)
        cosines.append(cos)
    return np.mean(cosines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--layer", type=int, default=None)
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else ("mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu")
    else:
        device = args.device

    # Crystal probes
    rng = np.random.RandomState(42)
    crystal_prompts = []
    for comb in CRYSTAL_COMBINATORS:
        probes = by_combinator(comb)
        prompts = [p.prompt for p in probes]
        if len(prompts) > 20:
            idx = rng.choice(len(prompts), 20, replace=False)
            prompts = [prompts[i] for i in sorted(idx)]
        crystal_prompts.extend(prompts)

    all_prompts = crystal_prompts + CORPUS

    print(f"\n{'═'*70}")
    print(f"  Hybrid Ternarization: Crystal Budget + Magnitude Selection")
    print(f"{'═'*70}")
    print(f"  Model: {args.model}")
    print(f"  Prompts: {len(all_prompts)} ({len(crystal_prompts)} crystal + {len(CORPUS)} corpus)")

    # Load
    print(f"\n  Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16, trust_remote_code=True)
    model = model.to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    d_ff = getattr(model.config, 'intermediate_size', model.config.hidden_size * 4)
    d_model = model.config.hidden_size
    layer_idx = args.layer if args.layer is not None else int(n_layers * 0.8)
    print(f"  {n_layers} layers, d={d_model}, d_ff={d_ff}, target layer={layer_idx}")

    layers = get_layers(model)
    W_gate = layers[layer_idx].mlp.gate_proj.weight.detach().float().cpu().numpy()
    W_up = layers[layer_idx].mlp.up_proj.weight.detach().float().cpu().numpy()

    # Capture gate activations + hidden states
    print(f"  Capturing activations ({len(all_prompts)} prompts)...")
    t0 = time.time()

    captured_gate = {}
    captured_hidden = {}

    def gate_hook(mod, inp, out):
        captured_gate['a'] = out.detach().float()

    def pre_mlp_hook(mod, inp):
        captured_hidden['h'] = inp[0].detach().float() if isinstance(inp, tuple) else inp.detach().float()

    h_gate = layers[layer_idx].mlp.gate_proj.register_forward_hook(gate_hook)
    h_pre = layers[layer_idx].mlp.register_forward_pre_hook(pre_mlp_hook)

    gate_acts = []  # for sparsity analysis
    hidden_states = []  # for FFN output quality
    for prompt in all_prompts:
        captured_gate.clear()
        captured_hidden.clear()
        inputs = tokenizer(prompt, return_tensors="pt", padding=False, truncation=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            model(**inputs)
        if 'a' in captured_gate:
            act = captured_gate['a']
            int_size = getattr(model.config, 'intermediate_size', None)
            if int_size and act.shape[-1] > int_size:
                act = act[..., :int_size]
            gate_acts.append(act.mean(dim=1).squeeze(0).cpu().numpy())
        if 'h' in captured_hidden:
            hidden_states.append(captured_hidden['h'].mean(dim=1).squeeze(0).cpu().numpy())

    h_gate.remove()
    h_pre.remove()

    gate_acts = np.array(gate_acts)
    hidden_states = np.array(hidden_states)
    print(f"  Done in {time.time()-t0:.1f}s: gate={gate_acts.shape}, hidden={hidden_states.shape}")

    # Per-neuron positive rate
    positive_rate = np.mean(gate_acts > 0, axis=0)

    # ═══════════════════════════════════════════════════════════════════
    # SWEEP: compare methods across total zero rates
    # ═══════════════════════════════════════════════════════════════════

    print(f"\n{'═'*70}")
    print(f"  SWEEP: Hybrid vs Magnitude vs Random at each zero rate")
    print(f"{'═'*70}")

    # For each dead threshold, compute crystal dead set + hybrid
    results = []

    print(f"\n  {'Total 0%':>8} {'Dead thr':>9} {'Dead N':>7} {'Alive 0%':>9}  "
          f"{'Magnitude':>10} {'Hybrid':>10} {'Random':>10} {'Δ hyb-mag':>10}")
    print(f"  {'─'*8} {'─'*9} {'─'*7} {'─'*9}  {'─'*10} {'─'*10} {'─'*10} {'─'*10}")

    for dead_threshold in [0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]:
        dead_mask = positive_rate < dead_threshold
        n_dead = dead_mask.sum()
        n_alive = d_ff - n_dead

        # Dead neurons contribute n_dead * d_model zeros
        dead_zeros = n_dead * d_model
        total_weights = d_ff * d_model
        dead_zero_frac = dead_zeros / total_weights

        # For total zero rates from dead_zero_frac up to 60%
        for target_total_zero in [0.10, 0.20, 0.30, 0.40, 0.50]:
            if dead_zero_frac > target_total_zero:
                continue  # can't hit this target, too many dead neurons

            # How many additional zeros needed in alive neurons?
            remaining_zeros_needed = target_total_zero * total_weights - dead_zeros
            alive_weights = n_alive * d_model
            alive_zero_frac = remaining_zeros_needed / alive_weights if alive_weights > 0 else 0

            if alive_zero_frac > 0.95:
                continue  # unreasonable

            # ── Hybrid: dead neurons 100% zero, alive use magnitude ──
            T_hybrid = np.zeros_like(W_gate)
            g_hybrid = np.zeros(d_ff)
            for i in range(d_ff):
                if dead_mask[i]:
                    continue  # already zero
                T_hybrid[i], g_hybrid[i] = ternarize_row(W_gate[i], alive_zero_frac)

            # ── Magnitude: uniform per-row threshold ──
            T_mag = np.zeros_like(W_gate)
            g_mag = np.zeros(d_ff)
            for i in range(d_ff):
                T_mag[i], g_mag[i] = ternarize_row(W_gate[i], target_total_zero)

            # ── Random neuron: random neurons zeroed, rest magnitude ──
            random_dead = rng.random(d_ff) < (n_dead / d_ff)
            T_rand = np.zeros_like(W_gate)
            g_rand = np.zeros(d_ff)
            for i in range(d_ff):
                if random_dead[i]:
                    continue
                n_alive_rand = (~random_dead).sum()
                rand_alive_frac = max(0, (target_total_zero * total_weights - random_dead.sum() * d_model)) / (n_alive_rand * d_model) if n_alive_rand > 0 else 0
                T_rand[i], g_rand[i] = ternarize_row(W_gate[i], rand_alive_frac)

            # ── Measure FFN output quality ──
            cos_mag = ffn_cosine(W_gate, W_up, T_mag, g_mag, hidden_states)
            cos_hybrid = ffn_cosine(W_gate, W_up, T_hybrid, g_hybrid, hidden_states)
            cos_random = ffn_cosine(W_gate, W_up, T_rand, g_rand, hidden_states)

            # Actual zero counts
            actual_mag_zeros = (T_mag == 0).sum() / total_weights
            actual_hybrid_zeros = (T_hybrid == 0).sum() / total_weights
            actual_random_zeros = (T_rand == 0).sum() / total_weights

            delta = cos_hybrid - cos_mag
            marker = " ✓" if delta > 0.001 else (" ≈" if abs(delta) < 0.001 else "")

            print(f"  {actual_hybrid_zeros*100:>7.1f}% {dead_threshold:>8.0%} {n_dead:>7} {alive_zero_frac*100:>8.1f}%  "
                  f"{cos_mag:>10.4f} {cos_hybrid:>10.4f} {cos_random:>10.4f} {delta:>+10.4f}{marker}")

            results.append({
                "total_zero_pct": round(actual_hybrid_zeros * 100, 1),
                "dead_threshold": dead_threshold,
                "n_dead": int(n_dead),
                "alive_zero_frac": round(alive_zero_frac, 4),
                "cos_magnitude": float(cos_mag),
                "cos_hybrid": float(cos_hybrid),
                "cos_random": float(cos_random),
                "delta_hybrid_mag": float(delta),
            })

    # Best hybrid advantage
    if results:
        best = max(results, key=lambda r: r['delta_hybrid_mag'])
        print(f"\n  Best hybrid advantage: Δ={best['delta_hybrid_mag']:+.4f} at "
              f"{best['total_zero_pct']:.0f}% zeros, dead_thr={best['dead_threshold']:.0%}, "
              f"n_dead={best['n_dead']}")

        # Summary
        print(f"\n{'═'*70}")
        print(f"  SUMMARY")
        print(f"{'═'*70}")
        wins = sum(1 for r in results if r['delta_hybrid_mag'] > 0.001)
        ties = sum(1 for r in results if abs(r['delta_hybrid_mag']) <= 0.001)
        losses = sum(1 for r in results if r['delta_hybrid_mag'] < -0.001)
        print(f"  Hybrid wins:  {wins}/{len(results)}")
        print(f"  Ties:         {ties}/{len(results)}")
        print(f"  Hybrid loses: {losses}/{len(results)}")

    # Save
    model_slug = args.model.replace("/", "_")
    output_path = args.output or f"results/crystal-phi-verify/{model_slug}_hybrid_ternarize.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump({"model": args.model, "layer": layer_idx, "results": results}, f, indent=2)
    print(f"\n  Saved to {output_path}")
    print(f"{'═'*70}\n")


if __name__ == "__main__":
    main()
