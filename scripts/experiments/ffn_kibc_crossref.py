#!/usr/bin/env python3
"""Cross-reference LARQL circuit types with KIBC opcode profiles on Pythia-160M.

Since the existing neuron_opcode_classifier.py was written for gated FFNs (Qwen),
this script adapts the approach for Pythia's non-gated FFN architecture:
  h = GELU(x @ W_up.T + b) @ W_down.T + b

For each neuron j in each layer:
  1. Run KIBC probes through the model
  2. Capture the activation at neuron j (post-GELU, pre-down projection)
  3. Build a [K, I, B, C] profile for each neuron
  4. Cross-tabulate with LARQL circuit type (from cos(up_row, down_col))

The key question: do KIBC opcodes predict circuit types?
  - K (constant) neurons → identity circuit? (preserve direction)
  - I (identity) neurons → transform circuit? (partial rotation)
  - B (compose) neurons → projector circuit? (orthogonal bridge)
  - C (flip-compose) neurons → inverter/suppressor? (direction flip)

Usage:
  uv run python scripts/experiments/ffn_kibc_crossref.py
  uv run python scripts/experiments/ffn_kibc_crossref.py --layers 0,3,6,9,11

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

os.environ.setdefault("PYTHONUNBUFFERED", "1")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import numpy as np
import torch
import torch.nn.functional as F
from scipy import stats as scipy_stats

COMBINATORS = ["K", "I", "B", "C"]
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


def run_experiment(model_id: str, layer_indices: list[int], n_probes: int):
    log("=" * 72)
    log("FFN KIBC ↔ CIRCUIT TYPE CROSS-REFERENCE")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Layers: {layer_indices}")
    log(f"Probes per combinator: {n_probes}")
    log()

    from verbum.probes.library import by_combinator
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # ── Load model ──────────────────────────────────────────────
    log("Loading model...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float32, device_map="cpu",
        low_cpu_mem_usage=True,
    )
    model.eval()
    log(f"  Loaded in {time.time() - t0:.1f}s")

    config = model.config
    n_layers = config.num_hidden_layers
    intermediate_size = config.intermediate_size
    hidden_size = config.hidden_size
    log(f"  {n_layers} layers, hidden={hidden_size}, intermediate={intermediate_size}")

    # ── Load precomputed cos(up, down) from FFN decomposition ──
    cos_path = os.path.join(os.path.dirname(__file__), "..", "..", "results",
                           "ffn-decomposition", "cos_values.npz")
    if os.path.exists(cos_path):
        cos_data = np.load(cos_path)
        log(f"  Loaded precomputed cos values from {cos_path}")
    else:
        log(f"  WARNING: No precomputed cos values at {cos_path}")
        log(f"  Run ffn_decomposition.py first!")
        cos_data = None

    # ── Collect probes ──────────────────────────────────────────
    probes_by_type = {}
    for comb in COMBINATORS:
        all_probes = by_combinator(comb)
        probes_by_type[comb] = all_probes[:n_probes]
        log(f"  {comb}: {len(probes_by_type[comb])} probes")

    # ── Run probes and capture post-GELU activations ────────────
    # Pythia FFN: dense_h_to_4h → GELU → dense_4h_to_h
    # We capture the output of GELU (before down projection).
    # This is the "activation" of each neuron for this input.
    profiles = {l: torch.zeros(intermediate_size, len(COMBINATORS))
                for l in layer_indices}
    counts = {l: torch.zeros(len(COMBINATORS)) for l in layer_indices}

    log(f"\n  Running KIBC probes...")
    t0 = time.time()
    total_probes = sum(len(v) for v in probes_by_type.values())
    probe_num = 0

    for comb_idx, comb in enumerate(COMBINATORS):
        for probe in probes_by_type[comb]:
            probe_num += 1
            ids = tokenizer.encode(probe.prompt, return_tensors="pt")

            captured = {}
            hooks = []
            for layer_idx in layer_indices:
                layer = model.gpt_neox.layers[layer_idx]

                def make_hook(lidx):
                    def hook_fn(module, input, output):
                        # For Pythia, the MLP applies:
                        #   dense_h_to_4h → act → dense_4h_to_h
                        # We hook the whole MLP and capture intermediate
                        # But actually we need to hook dense_h_to_4h output
                        # and apply GELU ourselves
                        captured[lidx] = output.detach().float().cpu()
                    return hook_fn

                # Hook the up projection (dense_h_to_4h) to get pre-activation
                h = layer.mlp.dense_h_to_4h.register_forward_hook(make_hook(layer_idx))
                hooks.append(h)

            with torch.no_grad():
                _ = model(ids)

            for h in hooks:
                h.remove()

            # Accumulate per-neuron activation for this combinator type
            for layer_idx in layer_indices:
                if layer_idx in captured:
                    pre_act = captured[layer_idx].squeeze(0)  # (seq_len, intermediate)
                    # Apply GELU to get actual neuron activation
                    act = F.gelu(pre_act)
                    # Mean absolute activation per neuron across sequence
                    neuron_act = act.abs().mean(dim=0)  # (intermediate,)
                    profiles[layer_idx][:, comb_idx] += neuron_act
                    counts[layer_idx][comb_idx] += 1

            captured.clear()

            if probe_num % 20 == 0:
                log(f"    probe {probe_num}/{total_probes}")

    elapsed = time.time() - t0
    log(f"  Done: {total_probes} probes in {elapsed:.1f}s")

    # Normalize
    for layer_idx in layer_indices:
        for c_idx in range(len(COMBINATORS)):
            if counts[layer_idx][c_idx] > 0:
                profiles[layer_idx][:, c_idx] /= counts[layer_idx][c_idx]

    # ── Cross-reference: KIBC profiles × circuit types ──────────
    results = {}

    for layer_idx in layer_indices:
        log(f"\n{'═' * 72}")
        log(f"LAYER {layer_idx}")
        log(f"{'═' * 72}")

        prof = profiles[layer_idx].numpy()  # (intermediate, 4)

        # KIBC classification per neuron
        dominant_opcode = np.argmax(prof, axis=1)  # which combinator dominates
        profile_magnitude = np.linalg.norm(prof, axis=1)
        purity = np.max(prof, axis=1) / (np.sum(prof, axis=1) + 1e-10)

        # Circuit type per neuron
        if cos_data is not None and f"layer_{layer_idx}" in cos_data:
            cos_vals = cos_data[f"layer_{layer_idx}"]
            circuit_types = np.array([classify_circuit(float(c)) for c in cos_vals])
        else:
            # Compute on the fly
            W_up = model.gpt_neox.layers[layer_idx].mlp.dense_h_to_4h.weight.data.float()
            W_down = model.gpt_neox.layers[layer_idx].mlp.dense_4h_to_h.weight.data.float()
            up_norm = F.normalize(W_up, dim=1)
            down_norm = F.normalize(W_down.T, dim=1)
            cos_vals = (up_norm * down_norm).sum(dim=1).numpy()
            circuit_types = np.array([classify_circuit(float(c)) for c in cos_vals])

        # ── Cross-tabulation ────────────────────────────────────
        opcode_names = COMBINATORS
        ct_names = ["identity", "transform", "projector", "suppressor", "inverter"]

        log(f"\n  CROSS-TABULATION: KIBC opcode (rows) × circuit type (cols)")
        log(f"\n  {'':>8s}  {'ident':>7s}  {'trans':>7s}  {'proj':>7s}  {'supp':>7s}  {'inv':>7s}  {'total':>7s}")
        log(f"  {'─'*8}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}")

        cross_tab = {}
        for opc_idx, opc in enumerate(opcode_names):
            opc_mask = dominant_opcode == opc_idx
            opc_total = opc_mask.sum()
            row = {}
            for ct in ct_names:
                ct_mask = circuit_types == ct
                both = (opc_mask & ct_mask).sum()
                row[ct] = int(both)
            cross_tab[opc] = row
            log(f"  {opc:>8s}  {row['identity']:>7d}  {row['transform']:>7d}  "
                f"{row['projector']:>7d}  {row['suppressor']:>7d}  {row['inverter']:>7d}  "
                f"{opc_total:>7d}")

        # Totals
        log(f"  {'total':>8s}  ", end="")
        for ct in ct_names:
            log(f"{(circuit_types == ct).sum():>7d}  ", end="")
        log(f"{len(circuit_types):>7d}")

        # ── Percentages within each opcode ──────────────────────
        log(f"\n  PERCENTAGES within each KIBC opcode:")
        log(f"\n  {'':>8s}  {'ident':>7s}  {'trans':>7s}  {'proj':>7s}  {'supp':>7s}  {'inv':>7s}")
        log(f"  {'─'*8}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}")

        for opc in opcode_names:
            total = sum(cross_tab[opc].values())
            if total > 0:
                log(f"  {opc:>8s}  ", end="")
                for ct in ct_names:
                    pct = cross_tab[opc][ct] / total * 100
                    log(f"{pct:6.1f}%  ", end="")
                log()

        # ── Profile magnitude by circuit type ───────────────────
        log(f"\n  KIBC PROFILE MAGNITUDE by circuit type:")
        for ct in ct_names:
            ct_mask = circuit_types == ct
            if ct_mask.sum() > 0:
                ct_mag = profile_magnitude[ct_mask]
                log(f"    {ct:12s}: mean={ct_mag.mean():.4f}  "
                    f"std={ct_mag.std():.4f}  n={ct_mask.sum()}")

        # ── Dominant opcode by circuit type ──────────────────────
        log(f"\n  DOMINANT OPCODE by circuit type:")
        for ct in ct_names:
            ct_mask = circuit_types == ct
            if ct_mask.sum() > 10:
                ct_opcodes = dominant_opcode[ct_mask]
                counts_per_opc = [(ct_opcodes == i).sum() for i in range(4)]
                total_ct = ct_mask.sum()
                pcts = [c / total_ct * 100 for c in counts_per_opc]
                log(f"    {ct:12s}: K={pcts[0]:5.1f}%  I={pcts[1]:5.1f}%  "
                    f"B={pcts[2]:5.1f}%  C={pcts[3]:5.1f}%  (n={total_ct})")

        # ── Correlation: cos(up,down) vs KIBC profile features ──
        log(f"\n  CORRELATIONS: cos(up,down) vs KIBC metrics:")
        rho_mag, p_mag = scipy_stats.spearmanr(cos_vals, profile_magnitude)
        rho_pur, p_pur = scipy_stats.spearmanr(cos_vals, purity)
        log(f"    ρ(cos, profile_magnitude) = {rho_mag:.4f}  p={p_mag:.2e}")
        log(f"    ρ(cos, purity)            = {rho_pur:.4f}  p={p_pur:.2e}")

        # Per-combinator correlations
        for c_idx, comb in enumerate(COMBINATORS):
            rho, p = scipy_stats.spearmanr(cos_vals, prof[:, c_idx])
            log(f"    ρ(cos, {comb}_activation)   = {rho:.4f}  p={p:.2e}")

        results[layer_idx] = {
            "cross_tab": cross_tab,
            "n_features": int(intermediate_size),
            "cos_profile_mag_rho": round(float(rho_mag), 4),
            "cos_purity_rho": round(float(rho_pur), 4),
        }

    # ── Save ────────────────────────────────────────────────────
    results_dir = os.path.join(os.path.dirname(__file__), "..", "..", "results", "ffn-decomposition")
    os.makedirs(results_dir, exist_ok=True)
    crossref_path = os.path.join(results_dir, "kibc_crossref.json")
    with open(crossref_path, "w") as f:
        json.dump({str(k): v for k, v in results.items()}, f, indent=2)
    log(f"\n  Cross-reference saved to {crossref_path}")

    # ── Cleanup ─────────────────────────────────────────────────
    del model
    import gc; gc.collect()

    log(f"\n{'═' * 72}")
    log("DONE")
    log(f"{'═' * 72}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="EleutherAI/pythia-160m")
    parser.add_argument("--layers", default="0,3,6,8,11")
    parser.add_argument("--n-probes", type=int, default=20,
                       help="Probes per combinator (20 = ~80 total, ~2 min)")
    args = parser.parse_args()

    layer_indices = [int(x) for x in args.layers.split(",")]
    run_experiment(args.model, layer_indices, args.n_probes)


if __name__ == "__main__":
    main()
