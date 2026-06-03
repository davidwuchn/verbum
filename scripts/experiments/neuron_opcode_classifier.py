#!/usr/bin/env python3
"""Per-neuron KIBC opcode classifier.

THE INSTRUMENT: For each FFN neuron, measure its combinator profile
by running KIBC probes and recording gate activations.

neuron_profile[i] = [K_activation, I_activation, B_activation, C_activation]

This tells us: what opcode does this neuron implement?

Then test: does the opcode assignment predict the zero mask?
  - Opcode neurons (strong profile) → always non-zero
  - Data neurons (weak profile) → zeroed based on knowledge content

Usage:
  uv run python scripts/experiments/neuron_opcode_classifier.py --model Qwen/Qwen3-8B
  uv run python scripts/experiments/neuron_opcode_classifier.py --model Qwen/Qwen3-8B --n-probes 30

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import math
import os
import sys
import time

os.environ.setdefault('PYTHONUNBUFFERED', '1')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import numpy as np
import torch
import torch.nn.functional as F
from scipy import stats as scipy_stats

PHI = (1 + math.sqrt(5)) / 2
COMBINATORS = ['K', 'I', 'B', 'C']


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


def run_experiment(model_id: str, layer_indices: list[int], n_probes_per_combinator: int = 30):
    log("=" * 72)
    log("PER-NEURON KIBC OPCODE CLASSIFIER")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Layers: {layer_indices}")
    log(f"Probes per combinator: {n_probes_per_combinator}")
    log()

    from verbum.probes.library import by_combinator
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="cpu",
        low_cpu_mem_usage=True)
    model.eval()

    config = model.config
    n_layers = config.num_hidden_layers
    intermediate_size = config.intermediate_size
    log(f"Loaded {model_id}: {n_layers} layers, {intermediate_size} intermediate")

    # ── Collect probes ──────────────────────────────────────────
    probes_by_type = {}
    for comb in COMBINATORS:
        all_probes = by_combinator(comb)
        probes_by_type[comb] = all_probes[:n_probes_per_combinator]
        log(f"  {comb}: {len(probes_by_type[comb])} probes")

    # ── Run probes and capture gate activations ─────────────────
    # Per-layer, per-neuron, per-combinator: mean |gate activation|
    # Shape: profiles[layer_idx] = (intermediate_size, 4)  [K, I, B, C]

    profiles = {l: torch.zeros(intermediate_size, len(COMBINATORS))
                for l in layer_indices}
    counts = {l: torch.zeros(len(COMBINATORS)) for l in layer_indices}

    log(f"\n  Running probes...")
    t0 = time.time()

    total_probes = sum(len(v) for v in probes_by_type.values())
    probe_num = 0

    for comb_idx, comb in enumerate(COMBINATORS):
        for probe in probes_by_type[comb]:
            probe_num += 1

            # Tokenize
            ids = tokenizer.encode(probe.prompt, return_tensors='pt')

            # Hook gate activations for target layers
            captured = {}

            hooks = []
            for layer_idx in layer_indices:
                layer = model.model.layers[layer_idx]

                def make_hook(lidx):
                    def hook_fn(module, input, output):
                        # For SwiGLU: gate_proj output before SiLU
                        # We need the gate activation. In Qwen, mlp.gate_proj
                        # is called first, then SiLU is applied.
                        # The hook on gate_proj captures its output.
                        captured[lidx] = output.detach().float().cpu()
                    return hook_fn

                h = layer.mlp.gate_proj.register_forward_hook(make_hook(layer_idx))
                hooks.append(h)

            with torch.no_grad():
                _ = model(ids)

            for h in hooks:
                h.remove()

            # Accumulate per-neuron activation for this combinator type
            for layer_idx in layer_indices:
                if layer_idx in captured:
                    gate_out = captured[layer_idx].squeeze(0)  # (seq_len, intermediate)
                    # Apply SiLU to get actual gate activation
                    gate_act = F.silu(gate_out)
                    # Mean absolute activation per neuron across sequence
                    neuron_act = gate_act.abs().mean(dim=0)  # (intermediate,)
                    profiles[layer_idx][:, comb_idx] += neuron_act
                    counts[layer_idx][comb_idx] += 1

            captured.clear()

            if probe_num % 20 == 0:
                log(f"    probe {probe_num}/{total_probes}")

    elapsed = time.time() - t0
    log(f"  Done: {total_probes} probes in {elapsed:.1f}s")

    # Normalize by count
    for layer_idx in layer_indices:
        for c_idx in range(len(COMBINATORS)):
            if counts[layer_idx][c_idx] > 0:
                profiles[layer_idx][:, c_idx] /= counts[layer_idx][c_idx]

    # ── Analysis per layer ──────────────────────────────────────
    for layer_idx in layer_indices:
        log(f"\n{'═' * 72}")
        log(f"LAYER {layer_idx}")
        log(f"{'═' * 72}")

        prof = profiles[layer_idx].numpy()  # (intermediate, 4)

        # Get weight magnitudes for this layer
        W_gate = model.model.layers[layer_idx].mlp.gate_proj.weight.data.float().cpu()
        W_up = model.model.layers[layer_idx].mlp.up_proj.weight.data.float().cpu()

        gate_row_norms = W_gate.norm(dim=1).numpy()  # (intermediate,)
        up_row_norms = W_up.norm(dim=1).numpy()

        # ── Neuron profile statistics ───────────────────────────
        profile_magnitude = np.linalg.norm(prof, axis=1)  # how "opcode-like"
        dominant_opcode = np.argmax(prof, axis=1)  # which combinator dominates
        purity = np.max(prof, axis=1) / (np.sum(prof, axis=1) + 1e-10)  # how pure

        log(f"\n  NEURON PROFILE STATISTICS:")
        log(f"    Profile magnitude: mean={profile_magnitude.mean():.4f} "
            f"std={profile_magnitude.std():.4f}")
        log(f"    Purity (max/sum):  mean={purity.mean():.4f} "
            f"std={purity.std():.4f}")

        for c_idx, comb in enumerate(COMBINATORS):
            n_dominant = (dominant_opcode == c_idx).sum()
            log(f"    Dominant {comb}: {n_dominant} neurons ({n_dominant/len(dominant_opcode):.1%})")

        # ── Correlation: profile magnitude vs weight magnitude ──
        log(f"\n  PROFILE MAGNITUDE vs WEIGHT MAGNITUDE:")
        rho_gate, p_gate = scipy_stats.spearmanr(profile_magnitude, gate_row_norms)
        rho_up, p_up = scipy_stats.spearmanr(profile_magnitude, up_row_norms)
        log(f"    ρ(profile_mag, gate_row_norm) = {rho_gate:.4f}  p={p_gate:.2e}")
        log(f"    ρ(profile_mag, up_row_norm)   = {rho_up:.4f}  p={p_up:.2e}")

        # ── THE KEY TEST: does profile predict zeros? ───────────
        log(f"\n  PROFILE MAGNITUDE vs ZERO MASK:")

        abs_gate = W_gate.abs()
        abs_up = W_up.abs()

        for target_label, abs_W in [("gate", abs_gate), ("up", abs_up)]:
            # Per-row mean magnitude (proxy for zero/non-zero importance)
            row_mean_mag = abs_W.mean(dim=1).numpy()

            # At 50% zero rate, which rows get zeroed more?
            row_zero_rate = (abs_W < abs_W.median(dim=1, keepdim=True).values).float().mean(dim=1).numpy()

            rho_zero, p_zero = scipy_stats.spearmanr(profile_magnitude, row_mean_mag)
            log(f"    {target_label:5s}: ρ(profile_mag, row_mean_mag) = {rho_zero:.4f}  p={p_zero:.2e}")

        # ── Opcode neurons vs data neurons ──────────────────────
        log(f"\n  OPCODE vs DATA NEURON ANALYSIS:")

        # Split neurons into terciles by profile magnitude
        tercile_lo = np.percentile(profile_magnitude, 33)
        tercile_hi = np.percentile(profile_magnitude, 67)

        data_neurons = profile_magnitude < tercile_lo
        mixed_neurons = (profile_magnitude >= tercile_lo) & (profile_magnitude < tercile_hi)
        opcode_neurons = profile_magnitude >= tercile_hi

        for label, mask in [("DATA (bottom 33%)", data_neurons),
                            ("MIXED (middle 33%)", mixed_neurons),
                            ("OPCODE (top 33%)", opcode_neurons)]:
            gate_mag_group = gate_row_norms[mask]
            up_mag_group = up_row_norms[mask]
            prof_mag_group = profile_magnitude[mask]

            log(f"    {label}:")
            log(f"      N={mask.sum()}, profile_mag={prof_mag_group.mean():.4f}")
            log(f"      gate_row_norm: {gate_mag_group.mean():.4f} ± {gate_mag_group.std():.4f}")
            log(f"      up_row_norm:   {up_mag_group.mean():.4f} ± {up_mag_group.std():.4f}")
            log(f"      gate_norm ratio (vs overall mean): "
                f"{gate_mag_group.mean() / gate_row_norms.mean():.4f}")

        # ── Per-combinator magnitude patterns ───────────────────
        log(f"\n  PER-COMBINATOR WEIGHT MAGNITUDES:")
        log(f"    {'Type':>8s} {'N':>6s} {'gate_norm':>12s} {'up_norm':>12s} {'purity':>8s}")
        for c_idx, comb in enumerate(COMBINATORS):
            mask = dominant_opcode == c_idx
            if mask.sum() == 0:
                continue
            log(f"    {comb:>8s} {mask.sum():6d} "
                f"{gate_row_norms[mask].mean():12.4f} "
                f"{up_row_norms[mask].mean():12.4f} "
                f"{purity[mask].mean():8.4f}")

        # ── Zero mask prediction from profile ───────────────────
        log(f"\n  ZERO MASK PREDICTION FROM OPCODE PROFILE:")

        # Use profile magnitude as importance score for zero mask
        # High profile = important (opcode neuron) = don't zero
        # Low profile = unimportant (data neuron) = zero

        W_up_full = model.model.layers[layer_idx].mlp.up_proj.weight.data.float().cpu()

        # Profile-based mask: zero neurons with lowest profile magnitude
        for zero_frac in [0.35, 0.50]:
            k_zero = int(intermediate_size * zero_frac)
            _, low_profile_idx = torch.tensor(profile_magnitude).topk(k_zero, largest=False)

            # Zero entire rows of up_proj for low-profile neurons
            mask_profile = torch.zeros(intermediate_size, W_up_full.shape[1], dtype=torch.bool)
            mask_profile[low_profile_idx, :] = True

            T_up = torch.sign(W_up_full)
            T_up_masked = T_up.clone()
            T_up_masked[mask_profile] = 0
            wt = (W_up_full * T_up_masked).sum(dim=1)
            tt = (T_up_masked * T_up_masked).sum(dim=1).clamp(min=1)
            gamma = wt / tt
            W_recon = gamma.unsqueeze(1) * T_up_masked
            w_flat = W_up_full.flatten()
            cos = (torch.dot(w_flat, W_recon.flatten()) /
                   (torch.norm(w_flat) * torch.norm(W_recon.flatten()) + 1e-10)).item()

            # Baseline: zero by magnitude
            abs_up_full = W_up_full.abs()
            row_norms_sorted = up_row_norms.copy()
            _, low_mag_idx = torch.tensor(up_row_norms).topk(k_zero, largest=False)
            mask_mag = torch.zeros_like(mask_profile)
            mask_mag[low_mag_idx, :] = True
            T_up_mag = T_up.clone()
            T_up_mag[mask_mag] = 0
            wt2 = (W_up_full * T_up_mag).sum(dim=1)
            tt2 = (T_up_mag * T_up_mag).sum(dim=1).clamp(min=1)
            gamma2 = wt2 / tt2
            W_recon2 = gamma2.unsqueeze(1) * T_up_mag
            cos_mag = (torch.dot(w_flat, W_recon2.flatten()) /
                       (torch.norm(w_flat) * torch.norm(W_recon2.flatten()) + 1e-10)).item()

            # Overlap
            overlap = (mask_profile == mask_mag).float().mean().item()

            log(f"    Zero {zero_frac:.0%} neurons by profile: cos={cos:.6f}  "
                f"(by magnitude: {cos_mag:.6f})  overlap={overlap:.4f}")

    del model
    gc.collect()

    log(f"\n{'═' * 72}")
    log("DONE")
    log(f"{'═' * 72}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", type=str, default="0,5,10,17,25,35")
    parser.add_argument("--n-probes", type=int, default=30,
                        help="Probes per combinator type")
    args = parser.parse_args()

    layer_indices = [int(x) for x in args.layers.split(",")]
    run_experiment(args.model, layer_indices, args.n_probes)


if __name__ == "__main__":
    main()
