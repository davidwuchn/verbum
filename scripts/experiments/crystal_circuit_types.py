#!/usr/bin/env python3
"""Crystal signs predict circuit types?

THE HYPOTHESIS: The crystal sign structure T = sign(W) determines the
circuit type distribution across depth. If cos(sign(W_up[j]), sign(W_down[:, j]))
shows the same depth profile as cos(W_up[j], W_down[:, j]), then the ternary
topology — before any magnitude training — predicts which layers do
computation (transforms/inverters) and which do lookup (projectors).

This would mean the phase structure (EXPAND → ORTHO → ALIGN → COLLAPSE)
is a property of the crystal, not just of the trained weights.

MEASUREMENTS:
  1. cos(W_up[j], W_down[:, j])           — full weight circuit types (from s186)
  2. cos(sign(W_up[j]), sign(W_down[:, j]))— ternary sign circuit types
  3. sign(W_up[j]) · sign(W_down[:, j])    — sign agreement fraction per neuron
  4. Cross-model: do independently trained models have the same sign-circuit profile?
  5. Random baseline: what does a random sign matrix produce?

Usage:
  uv run python scripts/experiments/crystal_circuit_types.py
  uv run python scripts/experiments/crystal_circuit_types.py --model EleutherAI/pythia-160m

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time

os.environ.setdefault("PYTHONUNBUFFERED", "1")

import numpy as np
import torch
import torch.nn.functional as F
from scipy import stats as scipy_stats

PHI = (1 + math.sqrt(5)) / 2

CIRCUIT_TYPES = {
    "identity":   (0.5, 1.0),
    "transform":  (0.2, 0.5),
    "projector":  (-0.2, 0.2),
    "suppressor": (-0.5, -0.2),
    "inverter":   (-1.0, -0.5),
}


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


def classify_circuit(cos_val: float) -> str:
    for name, (lo, hi) in CIRCUIT_TYPES.items():
        if lo <= cos_val < hi or (name == "identity" and cos_val >= hi):
            return name
        if name == "inverter" and cos_val < lo:
            return name
    return "projector"


def circuit_distribution(cos_vals: np.ndarray) -> dict:
    """Compute circuit type percentages from an array of cosine values."""
    counts = {name: 0 for name in CIRCUIT_TYPES}
    for c in cos_vals:
        counts[classify_circuit(float(c))] += 1
    total = len(cos_vals)
    return {name: round(count / total * 100, 2) for name, count in counts.items()}


def run_experiment(model_id: str):
    log("=" * 72)
    log("CRYSTAL SIGNS → CIRCUIT TYPES")
    log("=" * 72)
    log(f"Model: {model_id}")
    log()

    from transformers import AutoModelForCausalLM

    # ── Load model ──────────────────────────────────────────────
    log("Loading model...")
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float32, device_map="cpu",
        low_cpu_mem_usage=True,
    )
    model.eval()
    log(f"  Loaded in {time.time() - t0:.1f}s")

    config = model.config
    n_layers = config.num_hidden_layers
    hidden_size = config.hidden_size
    intermediate_size = config.intermediate_size
    log(f"  {n_layers} layers, hidden={hidden_size}, intermediate={intermediate_size}")

    # Detect architecture
    is_gpt_neox = hasattr(model, 'gpt_neox')
    is_qwen = hasattr(model, 'model') and hasattr(model.model, 'layers')
    log(f"  Architecture: {'GPT-NeoX' if is_gpt_neox else 'Qwen/Llama-like' if is_qwen else 'unknown'}")

    # ── Per-layer analysis ──────────────────────────────────────
    all_results = []

    for layer_idx in range(n_layers):
        log(f"\n{'─' * 72}")
        log(f"LAYER {layer_idx}")
        log(f"{'─' * 72}")

        # Get FFN weights
        if is_gpt_neox:
            mlp = model.gpt_neox.layers[layer_idx].mlp
            W_up = mlp.dense_h_to_4h.weight.data.float()    # (intermediate, hidden)
            W_down = mlp.dense_4h_to_h.weight.data.float()   # (hidden, intermediate)
        else:
            mlp = model.model.layers[layer_idx].mlp
            W_up = mlp.gate_proj.weight.data.float()          # (intermediate, hidden)
            W_down = mlp.down_proj.weight.data.float()        # (hidden, intermediate)

        n_features = W_up.shape[0]

        # ── 1. Full-weight cosines ──────────────────────────────
        up_rows = W_up                     # (intermediate, hidden)
        down_cols = W_down.T               # (intermediate, hidden)

        up_norm = F.normalize(up_rows, dim=1)
        down_norm = F.normalize(down_cols, dim=1)
        cos_full = (up_norm * down_norm).sum(dim=1).numpy()

        dist_full = circuit_distribution(cos_full)

        # ── 2. Sign-only cosines ────────────────────────────────
        # T_up = sign(W_up), T_down = sign(W_down)
        # cos(sign(up_row), sign(down_col)) for each feature
        T_up = torch.sign(W_up)       # (intermediate, hidden) ∈ {-1, 0, 1}
        T_down = torch.sign(W_down.T) # (intermediate, hidden) ∈ {-1, 0, 1}

        # Normalize sign vectors (they're already unit-ish but norm varies with zeros)
        T_up_norm = F.normalize(T_up.float(), dim=1)
        T_down_norm = F.normalize(T_down.float(), dim=1)
        cos_sign = (T_up_norm * T_down_norm).sum(dim=1).numpy()

        dist_sign = circuit_distribution(cos_sign)

        # ── 3. Sign agreement fraction ─────────────────────────
        # For each neuron j: what fraction of dimensions have
        # sign(W_up[j, k]) == sign(W_down[k, j])?
        sign_agree = (T_up == T_down).float().mean(dim=1).numpy()

        # ── 4. Random baseline ──────────────────────────────────
        # Random signs: each entry ±1 with p=0.5
        torch.manual_seed(42 + layer_idx)
        R_up = torch.sign(torch.randn_like(W_up))
        R_down = torch.sign(torch.randn_like(W_down.T))
        R_up_norm = F.normalize(R_up.float(), dim=1)
        R_down_norm = F.normalize(R_down.float(), dim=1)
        cos_random = (R_up_norm * R_down_norm).sum(dim=1).numpy()

        dist_random = circuit_distribution(cos_random)

        # ── 5. Correlation: sign-cos vs full-cos ────────────────
        rho_sign_full, p_sign_full = scipy_stats.spearmanr(cos_sign, cos_full)

        # ── 6. Zero-aware sign analysis ─────────────────────────
        # How many entries are exactly zero in W_up, W_down?
        up_zero_rate = (W_up == 0).float().mean().item()
        down_zero_rate = (W_down == 0).float().mean().item()

        # ── Report ──────────────────────────────────────────────
        log(f"\n  CIRCUIT TYPE DISTRIBUTIONS:")
        log(f"  {'':>12s}  {'ident':>7s}  {'trans':>7s}  {'proj':>7s}  {'supp':>7s}  {'inv':>7s}  {'cosMean':>8s}")
        log(f"  {'─'*12}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*8}")
        log(f"  {'full weight':>12s}  {dist_full['identity']:6.1f}%  {dist_full['transform']:6.1f}%  "
            f"{dist_full['projector']:6.1f}%  {dist_full['suppressor']:6.1f}%  {dist_full['inverter']:6.1f}%  "
            f"{cos_full.mean():7.4f}")
        log(f"  {'signs only':>12s}  {dist_sign['identity']:6.1f}%  {dist_sign['transform']:6.1f}%  "
            f"{dist_sign['projector']:6.1f}%  {dist_sign['suppressor']:6.1f}%  {dist_sign['inverter']:6.1f}%  "
            f"{cos_sign.mean():7.4f}")
        log(f"  {'random':>12s}  {dist_random['identity']:6.1f}%  {dist_random['transform']:6.1f}%  "
            f"{dist_random['projector']:6.1f}%  {dist_random['suppressor']:6.1f}%  {dist_random['inverter']:6.1f}%  "
            f"{cos_random.mean():7.4f}")

        log(f"\n  SIGN AGREEMENT: mean={sign_agree.mean():.4f}  std={sign_agree.std():.4f}")
        log(f"    (0.5 = random, >0.5 = same-sign bias, <0.5 = opposite-sign bias)")

        log(f"\n  CORRELATION: ρ(cos_sign, cos_full) = {rho_sign_full:.4f}  p={p_sign_full:.2e}")
        log(f"  ZEROS: W_up={up_zero_rate:.4f}  W_down={down_zero_rate:.4f}")

        # ── Does sign distribution track full distribution? ─────
        # The key test: does the sign-only profile look like the full profile
        # or like the random baseline?
        # Distance from full vs distance from random
        full_vec = np.array([dist_full[k] for k in CIRCUIT_TYPES])
        sign_vec = np.array([dist_sign[k] for k in CIRCUIT_TYPES])
        rand_vec = np.array([dist_random[k] for k in CIRCUIT_TYPES])

        dist_sign_to_full = np.linalg.norm(sign_vec - full_vec)
        dist_sign_to_random = np.linalg.norm(sign_vec - rand_vec)
        dist_full_to_random = np.linalg.norm(full_vec - rand_vec)

        log(f"\n  DISTRIBUTION DISTANCES (L2 norm of percentage vectors):")
        log(f"    |sign - full|   = {dist_sign_to_full:7.2f}  ← does sign predict full?")
        log(f"    |sign - random| = {dist_sign_to_random:7.2f}  ← is sign different from random?")
        log(f"    |full - random| = {dist_full_to_random:7.2f}  ← is full different from random?")

        if dist_sign_to_full < dist_sign_to_random:
            verdict = "SIGN TRACKS FULL (closer to full than random)"
        else:
            verdict = "SIGN LOOKS RANDOM (closer to random than full)"
        log(f"    VERDICT: {verdict}")

        all_results.append({
            "layer": layer_idx,
            "dist_full": dist_full,
            "dist_sign": dist_sign,
            "dist_random": dist_random,
            "cos_full_mean": round(float(cos_full.mean()), 4),
            "cos_sign_mean": round(float(cos_sign.mean()), 4),
            "cos_random_mean": round(float(cos_random.mean()), 4),
            "sign_agree_mean": round(float(sign_agree.mean()), 4),
            "rho_sign_full": round(float(rho_sign_full), 4),
            "p_sign_full": float(p_sign_full),
            "dist_sign_to_full": round(float(dist_sign_to_full), 2),
            "dist_sign_to_random": round(float(dist_sign_to_random), 2),
            "dist_full_to_random": round(float(dist_full_to_random), 2),
        })

    # ── Summary table ───────────────────────────────────────────
    log(f"\n\n{'═' * 72}")
    log("DEPTH PROFILE COMPARISON")
    log(f"{'═' * 72}")

    log(f"\n  FULL WEIGHTS — cos(W_up, W_down):")
    log(f"  {'Layer':>5s}  {'Proj%':>6s}  {'Trans%':>7s}  {'Supp%':>6s}  "
        f"{'Ident%':>7s}  {'Inv%':>6s}  {'cosMean':>8s}")
    log(f"  {'─'*5}  {'─'*6}  {'─'*7}  {'─'*6}  {'─'*7}  {'─'*6}  {'─'*8}")
    for r in all_results:
        d = r["dist_full"]
        log(f"  L{r['layer']:2d}   {d['projector']:5.1f}   {d['transform']:6.1f}   "
            f"{d['suppressor']:5.1f}   {d['identity']:6.1f}   {d['inverter']:5.1f}   "
            f"{r['cos_full_mean']:7.4f}")

    log(f"\n  SIGNS ONLY — cos(sign(W_up), sign(W_down)):")
    log(f"  {'Layer':>5s}  {'Proj%':>6s}  {'Trans%':>7s}  {'Supp%':>6s}  "
        f"{'Ident%':>7s}  {'Inv%':>6s}  {'cosMean':>8s}  {'ρ':>6s}  Verdict")
    log(f"  {'─'*5}  {'─'*6}  {'─'*7}  {'─'*6}  {'─'*7}  {'─'*6}  {'─'*8}  {'─'*6}  {'─'*20}")
    for r in all_results:
        d = r["dist_sign"]
        verdict = "TRACKS" if r["dist_sign_to_full"] < r["dist_sign_to_random"] else "RANDOM"
        log(f"  L{r['layer']:2d}   {d['projector']:5.1f}   {d['transform']:6.1f}   "
            f"{d['suppressor']:5.1f}   {d['identity']:6.1f}   {d['inverter']:5.1f}   "
            f"{r['cos_sign_mean']:7.4f}  {r['rho_sign_full']:5.3f}  {verdict}")

    log(f"\n  RANDOM BASELINE — cos(random_signs, random_signs):")
    log(f"  {'Layer':>5s}  {'Proj%':>6s}  {'Trans%':>7s}  {'Supp%':>6s}  "
        f"{'Ident%':>7s}  {'Inv%':>6s}  {'cosMean':>8s}")
    log(f"  {'─'*5}  {'─'*6}  {'─'*7}  {'─'*6}  {'─'*7}  {'─'*6}  {'─'*8}")
    for r in all_results:
        d = r["dist_random"]
        log(f"  L{r['layer']:2d}   {d['projector']:5.1f}   {d['transform']:6.1f}   "
            f"{d['suppressor']:5.1f}   {d['identity']:6.1f}   {d['inverter']:5.1f}   "
            f"{r['cos_random_mean']:7.4f}")

    # ── Sign agreement depth profile ────────────────────────────
    log(f"\n\n{'═' * 72}")
    log("SIGN AGREEMENT DEPTH PROFILE")
    log(f"{'═' * 72}")
    log(f"\n  sign_agree = fraction of dims where sign(W_up[j,k]) == sign(W_down[k,j])")
    log(f"  0.5 = random (independent signs), >0.5 = correlated, <0.5 = anti-correlated")
    log()
    for r in all_results:
        agree = r["sign_agree_mean"]
        bar_len = int((agree - 0.3) * 100)  # center around 0.5
        bar = "█" * max(0, bar_len)
        bias = "ANTI-CORR" if agree < 0.48 else "NEUTRAL" if agree < 0.52 else "CORRELATED"
        log(f"  L{r['layer']:2d}: {agree:.4f}  {bar}  {bias}")

    # ── The key question ────────────────────────────────────────
    log(f"\n\n{'═' * 72}")
    log("THE KEY QUESTION: Do crystal signs predict depth phases?")
    log(f"{'═' * 72}")

    tracking_count = sum(1 for r in all_results
                        if r["dist_sign_to_full"] < r["dist_sign_to_random"])
    total_layers = len(all_results)
    log(f"\n  Layers where sign distribution tracks full: {tracking_count}/{total_layers}")

    mean_rho = np.mean([r["rho_sign_full"] for r in all_results])
    log(f"  Mean ρ(cos_sign, cos_full) across layers: {mean_rho:.4f}")

    # Check if the SHAPE of the profile matches even if shifted
    full_means = np.array([r["cos_full_mean"] for r in all_results])
    sign_means = np.array([r["cos_sign_mean"] for r in all_results])
    rho_profile, p_profile = scipy_stats.spearmanr(full_means, sign_means)
    log(f"  ρ(full_mean_profile, sign_mean_profile) across depth: {rho_profile:.4f}  p={p_profile:.2e}")
    log(f"    (tests whether the SHAPE of the depth curve matches)")

    if rho_profile > 0.7 and p_profile < 0.05:
        log(f"\n  ✅ SIGNS PREDICT DEPTH PHASES. The crystal topology determines")
        log(f"     which layers do computation vs lookup.")
    elif rho_profile > 0.4:
        log(f"\n  🔶 PARTIAL. Signs capture some but not all of the depth structure.")
        log(f"     Magnitudes add information beyond what signs provide.")
    else:
        log(f"\n  ❌ SIGNS DO NOT PREDICT DEPTH PHASES. The depth profile emerges")
        log(f"     from magnitude structure, not sign topology.")

    # ── Save ────────────────────────────────────────────────────
    results_dir = os.path.join(os.path.dirname(__file__), "..", "..",
                              "results", "crystal-circuit-types")
    os.makedirs(results_dir, exist_ok=True)

    summary = {
        "model": model_id,
        "n_layers": n_layers,
        "hidden_size": hidden_size,
        "intermediate_size": intermediate_size,
        "layers": all_results,
        "profile_rho": round(float(rho_profile), 4),
        "profile_p": float(p_profile),
        "mean_per_neuron_rho": round(float(mean_rho), 4),
        "tracking_layers": tracking_count,
        "total_layers": total_layers,
    }

    summary_path = os.path.join(results_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    log(f"\n  Results saved to {summary_path}")

    log(f"\n{'═' * 72}")
    log("DONE")
    log(f"{'═' * 72}")

    return all_results


def main():
    parser = argparse.ArgumentParser(description="Crystal signs → circuit types")
    parser.add_argument("--model", default="EleutherAI/pythia-160m",
                       help="HuggingFace model ID")
    args = parser.parse_args()

    run_experiment(args.model)


if __name__ == "__main__":
    main()
