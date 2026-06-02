#!/usr/bin/env python3
"""Crystal-guided ternarization — construct ternary weights from the crystal equation.

Compares three ternarization strategies for gate_proj:

  Method A: MAGNITUDE — zero if |w| < threshold, else sign(w)
            (standard RTN-style, per-row threshold)

  Method B: CRYSTAL NEURON — zero entire neuron if gate activation is
            dead (< 5% positive rate), else sign(w) for alive neurons
            (crystal Equation 1 for zeros, weight sign for ±1)

  Method C: CRYSTAL HYBRID — use crystal dead-neuron mask for zeros,
            AND within alive neurons, zero small-magnitude positions
            (combines both signals)

Quality is measured by:
  1. Weight reconstruction: ||W - γ·T||² / ||W||²  (γ = per-row scale)
  2. Activation reconstruction: ||FFN_float(h) - FFN_ternary(h)||² / ||FFN_float(h)||²
     across a diverse set of input hidden states

Usage:
  uv run python scripts/experiments/crystal_ternarize.py --model Qwen/Qwen3-8B

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
CRYSTAL_COMBINATORS = ["K", "I", "B", "C", "D", "W", "Y", "WHNF"]

# Corpus for measuring activation quality + gate sparsity
EVAL_CORPUS = [
    "The speed of light is approximately 299792458 meters per second.",
    "Tokyo is the capital city of Japan and has a population of about 14 million.",
    "She opened the door slowly, not knowing what she would find on the other side.",
    "The old man sat on the park bench feeding pigeons every morning at sunrise.",
    "def quicksort(arr): return [] if not arr else quicksort([x for x in arr[1:] if x <= arr[0]]) + [arr[0]]",
    "If all mammals are warm-blooded and whales are mammals, then whales must be warm-blooded.",
    "The chemical formula for table salt is NaCl, sodium chloride.",
    "He packed his bags, looked around the empty apartment one last time, and left.",
    "SELECT u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.name",
    "The pattern is 2, 6, 18, 54 so the next number in the sequence is 162.",
    "Mount Everest stands at 8849 meters above sea level.",
    "Thunder rolled across the valley as the first drops of rain began to fall.",
    "import numpy as np; X = np.random.randn(100, 10); y = X @ np.ones(10)",
    "Summarize the following text in three bullet points focusing on the main argument.",
    "The Earth orbits the Sun at an average distance of about 150 million kilometers.",
    "Compare and contrast the two approaches listed above.",
    "DNA was first identified by Friedrich Miescher in 1869.",
    "The Amazon River is the largest river by discharge volume in the world.",
    "Assume for contradiction that the square root of 2 is rational.",
    "Extract all dates and monetary amounts from the following document.",
    "Among the candidates, the committee chose the one who had the most experience.",
    "After washing the dishes, she dried them with a clean towel.",
    "The book that the student read was difficult to understand.",
    "The mirror reflected the mirror reflecting the mirror endlessly.",
]


def get_layers_container(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers")


def capture_activations(model, tokenizer, prompts, layer_idx, device, target='gate'):
    """Capture gate_proj or full MLP activations."""
    layers = get_layers_container(model)
    intermediate_size = getattr(model.config, 'intermediate_size', None)
    captured = {}

    if target == 'gate':
        module = getattr(layers[layer_idx].mlp, 'gate_proj', None)
    elif target == 'hidden':
        # Hook the input to the MLP to get hidden states
        module = layers[layer_idx].mlp
    else:
        module = getattr(layers[layer_idx].mlp, target, None)

    def hook_fn(mod, inp, out):
        if target == 'hidden':
            # MLP input is the hidden state
            captured['act'] = inp[0].detach().float() if isinstance(inp, tuple) else inp.detach().float()
        else:
            captured['act'] = out.detach().float()

    hook = module.register_forward_hook(hook_fn)
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
            if target == 'gate' and intermediate_size and act.shape[-1] > intermediate_size:
                act = act[..., :intermediate_size]
            # Mean pool over sequence
            all_acts.append(act.mean(dim=1).squeeze(0).cpu().numpy())

    hook.remove()
    return np.array(all_acts)


def ternarize_magnitude(W, zero_frac=0.3):
    """Method A: magnitude-based ternarization with per-row threshold."""
    T = np.zeros_like(W)
    gammas = np.zeros(W.shape[0])

    for i in range(W.shape[0]):
        row = W[i]
        abs_row = np.abs(row)
        threshold = np.percentile(abs_row, zero_frac * 100)
        mask = abs_row >= threshold
        T[i] = np.where(mask, np.sign(row), 0)
        # Optimal gamma: minimizes ||w - γ·t||²
        # γ = (w · t) / (t · t)
        if T[i].any():
            gammas[i] = np.dot(row, T[i]) / np.dot(T[i], T[i])
        else:
            gammas[i] = 0

    return T, gammas


def ternarize_crystal_neuron(W, dead_mask, zero_frac_alive=0.0):
    """Method B: crystal neuron-level zeros + weight signs."""
    T = np.zeros_like(W)
    gammas = np.zeros(W.shape[0])

    for i in range(W.shape[0]):
        if dead_mask[i]:
            # Dead neuron → all zeros
            T[i] = 0
            gammas[i] = 0
        else:
            row = W[i]
            if zero_frac_alive > 0:
                abs_row = np.abs(row)
                threshold = np.percentile(abs_row, zero_frac_alive * 100)
                mask = abs_row >= threshold
                T[i] = np.where(mask, np.sign(row), 0)
            else:
                T[i] = np.sign(row)
            if T[i].any():
                gammas[i] = np.dot(row, T[i]) / np.dot(T[i], T[i])

    return T, gammas


def eval_weight_quality(W, T, gammas):
    """Evaluate weight reconstruction: ||W - diag(γ)·T||² / ||W||²"""
    reconstructed = gammas[:, None] * T
    mse = np.mean((W - reconstructed) ** 2)
    norm = np.mean(W ** 2)
    return {
        "nmse": float(mse / norm),
        "mse": float(mse),
        "cosine": float(np.sum(W * reconstructed) /
                        (np.linalg.norm(W) * np.linalg.norm(reconstructed) + 1e-12)),
    }


def eval_activation_quality(W_float, T, gammas, hidden_states):
    """Evaluate FFN activation reconstruction quality.

    Computes gate_proj output for float vs ternary weights.
    """
    # Float output: W @ h for each hidden state
    float_out = hidden_states @ W_float.T  # (n, d_ff)

    # Ternary output: (γ·T) @ h
    W_ternary = gammas[:, None] * T
    ternary_out = hidden_states @ W_ternary.T  # (n, d_ff)

    # Per-sample NMSE
    diff = float_out - ternary_out
    nmse_per_sample = np.mean(diff ** 2, axis=1) / (np.mean(float_out ** 2, axis=1) + 1e-12)

    # Apply SiLU to see effect on actual gate activation
    def silu(x):
        return x / (1 + np.exp(-np.clip(x, -20, 20)))

    float_gated = silu(float_out)
    ternary_gated = silu(ternary_out)
    diff_gated = float_gated - ternary_gated
    nmse_gated = np.mean(diff_gated ** 2, axis=1) / (np.mean(float_gated ** 2, axis=1) + 1e-12)

    return {
        "nmse_linear": float(np.mean(nmse_per_sample)),
        "nmse_gated": float(np.mean(nmse_gated)),
        "cosine_linear": float(np.mean([
            np.dot(float_out[i], ternary_out[i]) /
            (np.linalg.norm(float_out[i]) * np.linalg.norm(ternary_out[i]) + 1e-12)
            for i in range(len(hidden_states))
        ])),
        "cosine_gated": float(np.mean([
            np.dot(float_gated[i], ternary_gated[i]) /
            (np.linalg.norm(float_gated[i]) * np.linalg.norm(ternary_gated[i]) + 1e-12)
            for i in range(len(hidden_states))
        ])),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Crystal-guided ternarization experiment")
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

    # Crystal probes
    rng = np.random.RandomState(42)
    probe_dict = {}
    for comb in CRYSTAL_COMBINATORS:
        probes = by_combinator(comb)
        prompts = [p.prompt for p in probes]
        if args.n_per_combinator and len(prompts) > args.n_per_combinator:
            idx = rng.choice(len(prompts), args.n_per_combinator, replace=False)
            prompts = [prompts[i] for i in sorted(idx)]
        probe_dict[comb] = prompts
    crystal_prompts = [p for c in CRYSTAL_COMBINATORS for p in probe_dict[c]]

    print(f"\n{'═'*70}")
    print(f"  Crystal-Guided Ternarization Experiment")
    print(f"{'═'*70}")
    print(f"  Model: {args.model}")
    print(f"  Crystal probes: {len(crystal_prompts)}")
    print(f"  Eval corpus: {len(EVAL_CORPUS)}")

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
    d_model = model.config.hidden_size
    layer_idx = args.layer if args.layer is not None else int(n_layers * 0.8)
    print(f"  Loaded: {n_layers} layers, d={d_model}, d_ff={d_ff}")
    print(f"  Target layer: {layer_idx} ({layer_idx/n_layers*100:.0f}%)")

    # ── Step 1: Determine dead neurons via gate activation ────────────
    print(f"\n  Step 1: Capturing gate activations for sparsity analysis...")
    t0 = time.time()
    all_prompts = crystal_prompts + EVAL_CORPUS
    gate_acts = capture_activations(
        model, tokenizer, all_prompts, layer_idx, device, target='gate')
    print(f"  Gate activations: {gate_acts.shape} in {time.time()-t0:.1f}s")

    # Per-neuron: fraction of times gate is positive (SiLU passes signal)
    positive_rate = np.mean(gate_acts > 0, axis=0)  # (d_ff,)

    # Dead neurons: positive rate < 5%
    dead_5pct = positive_rate < 0.05
    dead_10pct = positive_rate < 0.10
    dead_1pct = positive_rate < 0.01
    n_dead_5 = dead_5pct.sum()
    n_dead_10 = dead_10pct.sum()
    n_dead_1 = dead_1pct.sum()
    print(f"  Dead neurons (<1% positive): {n_dead_1} ({n_dead_1/d_ff*100:.1f}%)")
    print(f"  Dead neurons (<5% positive): {n_dead_5} ({n_dead_5/d_ff*100:.1f}%)")
    print(f"  Dead neurons (<10% positive): {n_dead_10} ({n_dead_10/d_ff*100:.1f}%)")

    # ── Step 2: Extract float weights ─────────────────────────────────
    print(f"\n  Step 2: Extracting gate_proj weights...")
    layers_container = get_layers_container(model)
    W = layers_container[layer_idx].mlp.gate_proj.weight.detach().float().cpu().numpy()
    print(f"  Weight shape: {W.shape}")

    # ── Step 3: Capture hidden states for activation quality eval ─────
    print(f"\n  Step 3: Capturing hidden states for evaluation...")
    t1 = time.time()
    hidden_states = capture_activations(
        model, tokenizer, EVAL_CORPUS, layer_idx, device, target='hidden')
    print(f"  Hidden states: {hidden_states.shape} in {time.time()-t1:.1f}s")

    # ── Step 4: Ternarize with each method ────────────────────────────
    print(f"\n{'═'*70}")
    print(f"  TERNARIZATION COMPARISON")
    print(f"{'═'*70}")

    # Compute actual zero fraction that crystal method would produce
    crystal_zero_frac = n_dead_5 / d_ff

    results_table = []

    for method_name, method_desc, method_fn in [
        # Method A variants: magnitude threshold
        ("mag_10%", "Magnitude, 10% zeros", lambda: ternarize_magnitude(W, 0.10)),
        ("mag_20%", "Magnitude, 20% zeros", lambda: ternarize_magnitude(W, 0.20)),
        ("mag_30%", "Magnitude, 30% zeros", lambda: ternarize_magnitude(W, 0.30)),
        (f"mag_{crystal_zero_frac*100:.0f}%", f"Magnitude, {crystal_zero_frac*100:.0f}% zeros (matched)",
         lambda: ternarize_magnitude(W, crystal_zero_frac)),
        # Method B: crystal neuron zeros + all signs
        ("crystal_neuron", f"Crystal neuron dead ({crystal_zero_frac*100:.0f}% zeros)",
         lambda: ternarize_crystal_neuron(W, dead_5pct, 0.0)),
        # Method C: crystal neuron zeros + magnitude zeros within alive
        ("crystal_hybrid_10%", "Crystal neuron + 10% mag in alive",
         lambda: ternarize_crystal_neuron(W, dead_5pct, 0.10)),
        ("crystal_hybrid_20%", "Crystal neuron + 20% mag in alive",
         lambda: ternarize_crystal_neuron(W, dead_5pct, 0.20)),
        # Baseline: random neuron zeros at same rate
        ("random_neuron", f"Random neuron dead ({crystal_zero_frac*100:.0f}%)",
         lambda: ternarize_crystal_neuron(W, rng.random(d_ff) < crystal_zero_frac, 0.0)),
    ]:
        T, gammas = method_fn()

        # Count actual zeros
        actual_zeros = (T == 0).sum()
        total = T.size
        zero_pct = actual_zeros / total * 100

        # Neuron-level zeros
        neuron_dead = np.all(T == 0, axis=1).sum()

        # Weight quality
        wq = eval_weight_quality(W, T, gammas)

        # Activation quality
        aq = eval_activation_quality(W, T, gammas, hidden_states)

        results_table.append({
            "method": method_name,
            "desc": method_desc,
            "zero_pct": zero_pct,
            "neuron_dead": neuron_dead,
            "weight_nmse": wq["nmse"],
            "weight_cosine": wq["cosine"],
            "act_nmse_linear": aq["nmse_linear"],
            "act_nmse_gated": aq["nmse_gated"],
            "act_cosine_linear": aq["cosine_linear"],
            "act_cosine_gated": aq["cosine_gated"],
        })

    # Print comparison table
    print(f"\n  {'Method':<28} {'Zeros%':>7} {'Dead N':>7} {'W cos':>7} {'A cos(g)':>9} {'A NMSE(g)':>10}")
    print(f"  {'─'*28} {'─'*7} {'─'*7} {'─'*7} {'─'*9} {'─'*10}")
    for r in results_table:
        print(f"  {r['method']:<28} {r['zero_pct']:>6.1f}% {r['neuron_dead']:>7} "
              f"{r['weight_cosine']:>7.4f} {r['act_cosine_gated']:>9.4f} {r['act_nmse_gated']:>10.6f}")

    # ── Analysis ──────────────────────────────────────────────────────
    print(f"\n{'═'*70}")
    print(f"  ANALYSIS")
    print(f"{'═'*70}")

    # Find crystal vs magnitude at matched zero rate
    crystal = [r for r in results_table if r['method'] == 'crystal_neuron'][0]
    matched = [r for r in results_table if 'matched' in r.get('desc', '')][0]
    random_n = [r for r in results_table if r['method'] == 'random_neuron'][0]

    print(f"\n  At matched zero rate ({crystal['zero_pct']:.0f}%):")
    print(f"    {'Metric':<25} {'Magnitude':>12} {'Crystal':>12} {'Random':>12} {'Crystal wins?':>14}")
    for metric in ['weight_cosine', 'act_cosine_gated', 'act_nmse_gated']:
        mv = matched[metric]
        cv = crystal[metric]
        rv = random_n[metric]
        if 'cosine' in metric:
            wins = "YES ✓" if cv > mv else "NO"
            print(f"    {metric:<25} {mv:>12.6f} {cv:>12.6f} {rv:>12.6f} {wins:>14}")
        else:
            wins = "YES ✓" if cv < mv else "NO"
            print(f"    {metric:<25} {mv:>12.6f} {cv:>12.6f} {rv:>12.6f} {wins:>14}")

    # ── Save ──────────────────────────────────────────────────────────
    model_slug = args.model.replace("/", "_")
    output_path = args.output or f"results/crystal-phi-verify/{model_slug}_ternarize.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def jsonable(obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, dict): return {k: jsonable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)): return [jsonable(v) for v in obj]
        return obj

    with open(output_path, 'w') as f:
        json.dump(jsonable({
            "model": args.model,
            "layer": layer_idx,
            "d_ff": d_ff,
            "d_model": d_model,
            "dead_neurons_5pct": int(n_dead_5),
            "dead_neurons_10pct": int(n_dead_10),
            "results": results_table,
        }), f, indent=2)

    print(f"\n  Saved to {output_path}")
    print(f"{'═'*70}\n")


if __name__ == "__main__":
    main()
