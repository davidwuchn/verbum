#!/usr/bin/env python3
"""Predict weight zeros from the crystal equation and compare to actual weights.

The crystal equation λ_k = C · φ^(-s·β_k) predicts which neurons are
"irreducible" — below the compute/no-compute phase boundary. This script
tests whether that prediction matches the actual weight magnitude pattern
in a pretrained model.

Method:
  1. Load model, extract gate_proj weights at ~80% depth (best crystal layer)
  2. Run crystal probes → PCA → crystal basis (eigenvectors)
  3. For each neuron: compute crystal_energy from mode projections
  4. For each neuron: compute weight magnitude (L2 norm of weight row)
  5. Correlate crystal_energy with weight_magnitude
  6. Apply crystal threshold → predict zero/nonzero
  7. Compare predicted zeros vs actual small-weight neurons

Usage:
  uv run python scripts/experiments/crystal_zero_prediction.py --model Qwen/Qwen3-8B

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
S = 4 / 5  # computing fraction
CRYSTAL_COMBINATORS = ["K", "I", "B", "C", "D", "W", "Y", "WHNF"]

# Crystal eigenvalue ratios from the equation
BETA = [0, 1, 1 + PHI, 2 + PHI]
CRYSTAL_RATIOS = [PHI ** (-S * b) for b in BETA]
# Phase boundary: below this ratio, the mode is terminal
PHASE_BOUNDARY = CRYSTAL_RATIOS[-1]  # φ^(-s·β_max) ≈ 0.248


def get_layers_container(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def extract_crystal_basis(model, tokenizer, probe_dict, layer_idx, device):
    """Extract crystal PCA basis from gate_proj activations at one layer.

    Returns: (eigenvectors, eigenvalues, mean_activation)
      eigenvectors: (n_modes, d_ff) — crystal mode directions
      eigenvalues:  (n_modes,) — variance per mode
      mean_act:     (d_ff,) — mean activation for centering
    """
    layers_container = get_layers_container(model)
    intermediate_size = getattr(model.config, 'intermediate_size', None)
    captured = {}

    def hook_fn(module, input, output):
        captured['act'] = output.detach().float()

    layer = layers_container[layer_idx]
    mlp = layer.mlp
    gate = getattr(mlp, 'gate_proj', None) or getattr(mlp, 'dense_h_to_4h', None)
    hook = gate.register_forward_hook(hook_fn)

    all_acts = []
    labels = []
    for comb in CRYSTAL_COMBINATORS:
        for prompt in probe_dict[comb]:
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
                labels.append(comb)

    hook.remove()

    all_acts = np.array(all_acts)  # (n_probes, d_ff)
    mean_act = all_acts.mean(axis=0)
    centered = all_acts - mean_act

    # PCA via SVD
    U, S_vals, Vt = np.linalg.svd(centered, full_matrices=False)
    n_modes = min(len(CRYSTAL_COMBINATORS) * 2, len(S_vals))

    eigenvalues = (S_vals[:n_modes] ** 2) / (len(all_acts) - 1)
    eigenvectors = Vt[:n_modes]  # (n_modes, d_ff)

    return eigenvectors, eigenvalues, mean_act, labels, centered


def compute_crystal_energy(eigenvectors, eigenvalues, weight_rows):
    """Compute crystal energy for each neuron (weight row).

    crystal_energy(i) = Σ_k eigenvalue_k · (V_k · w_i)²

    This measures how much of neuron i's weight direction aligns
    with crystal modes, weighted by mode strength.

    Args:
        eigenvectors: (n_modes, d_ff)
        eigenvalues: (n_modes,)
        weight_rows: (d_ff, d_model) — each column is a neuron's weight vector

    Returns: (d_ff,) crystal energy per neuron
    """
    # Project each neuron's weight row onto crystal modes
    # weight_rows is (d_ff, d_model), eigenvectors is (n_modes, d_ff)
    # We want: for each of d_ff neurons, project its d_model-dim weight vector
    # But eigenvectors live in d_ff space (activation space), not d_model space (weight space)
    #
    # The connection: neuron i's activation a_i = gate_proj[i,:] · hidden_state
    # The crystal basis is in activation space (d_ff).
    # The "crystal energy" of neuron i is how much its ACTIVATION participates in crystal modes.
    #
    # So crystal_energy(i) = Σ_k eigenvalue_k · eigenvector_k[i]²
    # This is just the i-th diagonal element of V^T · diag(λ) · V

    energies = np.zeros(eigenvectors.shape[1])  # (d_ff,)
    for k in range(len(eigenvalues)):
        energies += eigenvalues[k] * eigenvectors[k] ** 2

    return energies


def main():
    parser = argparse.ArgumentParser(
        description="Predict weight zeros from the crystal equation")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--n-per-combinator", type=int, default=25)
    parser.add_argument("--layer", type=int, default=None,
                        help="Layer to analyze (default: ~80%% depth)")
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

    # Select probes
    rng = np.random.RandomState(42)
    probe_dict = {}
    for comb in CRYSTAL_COMBINATORS:
        probes = by_combinator(comb)
        prompts = [p.prompt for p in probes]
        if args.n_per_combinator and len(prompts) > args.n_per_combinator:
            idx = rng.choice(len(prompts), args.n_per_combinator, replace=False)
            prompts = [prompts[i] for i in sorted(idx)]
        probe_dict[comb] = prompts

    total = sum(len(v) for v in probe_dict.values())

    # Load model
    print(f"\n{'═'*70}")
    print(f"  Crystal Zero Prediction")
    print(f"{'═'*70}")
    print(f"  Model: {args.model}")
    print(f"  Probes: {total} ({args.n_per_combinator} per combinator)")
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
    d_model = model.config.hidden_size
    d_ff = getattr(model.config, 'intermediate_size', d_model * 4)

    # Select layer (~80% depth)
    layer_idx = args.layer if args.layer is not None else int(n_layers * 0.8)
    print(f"  Loaded: {n_layers} layers, d={d_model}, d_ff={d_ff}")
    print(f"  Analysis layer: {layer_idx} ({layer_idx/n_layers*100:.0f}% depth)")

    # ── Step 1: Extract crystal basis ─────────────────────────────────
    print(f"\n  Step 1: Extracting crystal basis ({total} probes)...")
    t0 = time.time()
    eigenvectors, eigenvalues, mean_act, labels, centered = extract_crystal_basis(
        model, tokenizer, probe_dict, layer_idx, device
    )
    print(f"  Done in {time.time()-t0:.1f}s")
    print(f"  Crystal modes: {len(eigenvalues)}")
    total_var = eigenvalues.sum()
    cum = 0
    for i in range(min(8, len(eigenvalues))):
        cum += eigenvalues[i]
        print(f"    Mode {i}: variance={eigenvalues[i]:.4f} ({eigenvalues[i]/total_var*100:.1f}%, cum {cum/total_var*100:.1f}%)")

    # ── Step 2: Extract weight magnitudes ─────────────────────────────
    print(f"\n  Step 2: Extracting gate_proj weights...")
    layers_container = get_layers_container(model)
    layer = layers_container[layer_idx]
    gate_proj = layer.mlp.gate_proj if hasattr(layer.mlp, 'gate_proj') else layer.mlp.dense_h_to_4h
    W = gate_proj.weight.detach().float().cpu().numpy()  # (d_ff, d_model)
    print(f"  Weight shape: {W.shape}")

    # Per-neuron weight magnitude
    weight_norms = np.linalg.norm(W, axis=1)  # (d_ff,)
    print(f"  Weight norm stats: mean={weight_norms.mean():.4f}, "
          f"std={weight_norms.std():.4f}, "
          f"min={weight_norms.min():.4f}, max={weight_norms.max():.4f}")

    # ── Step 3: Compute crystal energy per neuron ─────────────────────
    print(f"\n  Step 3: Computing crystal energy per neuron...")
    crystal_energy = compute_crystal_energy(eigenvectors, eigenvalues, W)
    print(f"  Crystal energy stats: mean={crystal_energy.mean():.6f}, "
          f"std={crystal_energy.std():.6f}, "
          f"min={crystal_energy.min():.6f}, max={crystal_energy.max():.6f}")

    # ── Step 4: Correlate crystal energy with weight magnitude ────────
    print(f"\n  Step 4: Correlation analysis...")

    # Raw correlation
    corr = np.corrcoef(crystal_energy, weight_norms)[0, 1]
    print(f"  Pearson correlation (crystal_energy vs weight_norm): {corr:.4f}")

    # Rank correlation (more robust)
    from scipy import stats as sp_stats
    rank_corr, rank_p = sp_stats.spearmanr(crystal_energy, weight_norms)
    print(f"  Spearman rank correlation: {rank_corr:.4f} (p={rank_p:.2e})")

    # ── Step 5: Threshold analysis — predict zeros ────────────────────
    print(f"\n  Step 5: Zero prediction from crystal equation...")

    # Normalize crystal energy to [0, 1]
    ce_normalized = crystal_energy / crystal_energy.max()

    # The crystal phase boundary
    threshold = PHASE_BOUNDARY  # φ^(-s·β_max) ≈ 0.248
    print(f"  Crystal phase boundary: {threshold:.4f}")

    # Predict zeros: neurons with low crystal energy
    predicted_zero = ce_normalized < threshold

    # Compare with actual small-weight neurons at various percentiles
    print(f"\n  {'Percentile':>12} {'Weight thresh':>13} {'Actual zeros':>13} {'Predicted':>10} {'Overlap':>8} {'Precision':>10} {'Recall':>8}")
    print(f"  {'─'*12} {'─'*13} {'─'*13} {'─'*10} {'─'*8} {'─'*10} {'─'*8}")

    for pct in [1, 2, 5, 10, 15, 20, 25, 30, 50]:
        thresh = np.percentile(weight_norms, pct)
        actual_zero = weight_norms < thresh
        n_actual = actual_zero.sum()

        # Also try crystal-energy-based prediction at matching rate
        ce_thresh = np.percentile(crystal_energy, pct)
        pred_at_rate = crystal_energy < ce_thresh
        n_pred = pred_at_rate.sum()

        overlap = (actual_zero & pred_at_rate).sum()
        precision = overlap / n_pred if n_pred > 0 else 0
        recall = overlap / n_actual if n_actual > 0 else 0

        print(f"  {pct:>11}% {thresh:>13.4f} {n_actual:>13} {n_pred:>10} {overlap:>8} {precision:>10.3f} {recall:>8.3f}")

    # ── Step 6: Per-mode analysis ─────────────────────────────────────
    print(f"\n  Step 6: Which crystal modes predict zeros best?")
    print(f"\n  {'Mode':>6} {'Eigenvalue':>11} {'Corr w/ |W|':>12} {'Rank corr':>10}")

    mode_corrs = []
    for k in range(min(8, len(eigenvalues))):
        mode_projection = eigenvectors[k] ** 2  # per-neuron projection onto mode k
        mode_corr = np.corrcoef(mode_projection, weight_norms)[0, 1]
        mode_rank, _ = sp_stats.spearmanr(mode_projection, weight_norms)
        mode_corrs.append((k, eigenvalues[k], mode_corr, mode_rank))
        print(f"  {k:>6} {eigenvalues[k]:>11.4f} {mode_corr:>12.4f} {mode_rank:>10.4f}")

    # ── Step 7: The equation ──────────────────────────────────────────
    print(f"\n{'═'*70}")
    print(f"  THE ZERO EQUATION")
    print(f"{'═'*70}")
    print()

    # Try fitting: ||W_i|| ≈ f(crystal_energy_i)
    # Linear fit
    from numpy.polynomial import polynomial as P
    coeffs = np.polyfit(crystal_energy, weight_norms, 1)
    predicted_norms = np.polyval(coeffs, crystal_energy)
    residuals = weight_norms - predicted_norms
    r_squared = 1 - (residuals**2).sum() / ((weight_norms - weight_norms.mean())**2).sum()
    print(f"  Linear fit: ||W_i|| ≈ {coeffs[0]:.2f} · E_crystal(i) + {coeffs[1]:.4f}")
    print(f"  R² = {r_squared:.4f}")

    # Power-law fit: ||W_i|| ≈ a · E_crystal^b
    log_ce = np.log(crystal_energy + 1e-12)
    log_wn = np.log(weight_norms + 1e-12)
    mask = (crystal_energy > 1e-10) & (weight_norms > 1e-10)
    if mask.sum() > 10:
        pf = np.polyfit(log_ce[mask], log_wn[mask], 1)
        b_power = pf[0]
        a_power = np.exp(pf[1])
        predicted_log = np.polyval(pf, log_ce[mask])
        r2_power = 1 - ((log_wn[mask] - predicted_log)**2).sum() / ((log_wn[mask] - log_wn[mask].mean())**2).sum()
        print(f"  Power-law fit: ||W_i|| ≈ {a_power:.4f} · E_crystal(i)^{b_power:.4f}")
        print(f"  R² (log-log) = {r2_power:.4f}")

        # Is the exponent related to phi?
        print(f"\n  Power-law exponent: {b_power:.4f}")
        print(f"  φ^(-1) = {1/PHI:.4f}")
        print(f"  s = {S:.4f}")
        print(f"  1/φ² = {1/PHI**2:.4f}")
        print(f"  s/2 = {S/2:.4f}")

    # ── Save results ──────────────────────────────────────────────────
    model_slug = args.model.replace("/", "_")
    output_path = args.output or f"results/crystal-phi-verify/{model_slug}_zero_prediction.json"
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
        "depth_pct": round(layer_idx / n_layers * 100, 1),
        "d_ff": d_ff,
        "d_model": d_model,
        "n_probes": total,
        "crystal_eigenvalues": eigenvalues.tolist(),
        "correlation_pearson": corr,
        "correlation_spearman": rank_corr,
        "r_squared_linear": r_squared,
        "r_squared_power_log": r2_power if mask.sum() > 10 else None,
        "power_law_exponent": b_power if mask.sum() > 10 else None,
        "phase_boundary": PHASE_BOUNDARY,
        "weight_norm_percentiles": {
            str(p): float(np.percentile(weight_norms, p))
            for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]
        },
        "crystal_energy_percentiles": {
            str(p): float(np.percentile(crystal_energy, p))
            for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]
        },
    })

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {output_path}")
    print(f"{'═'*70}\n")


if __name__ == "__main__":
    main()
