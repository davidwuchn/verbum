#!/usr/bin/env python3
"""Verify the crystal φ structure directly in a model.

Measures the crystal cosine matrix from a model's FFN gate_proj
activations, eigendecomposes it, and checks whether eigenvalues follow
φ^(p/q).

Now uses the unified probe library (verbum.probes.library) for dense
combinator coverage — 50+ probes per combinator vs the original 4.

Method:
  1. Load model (HuggingFace CausalLM)
  2. Load crystal probes from unified library (KIBC + DWYS + WHNF)
  3. Extract gate_proj activations at Zone B layers (middle depth)
  4. PCA of gate activations → principal components
  5. Compute N×N cosine matrix between combinator directions
  6. Eigendecompose and check φ^(p/q) structure

Usage:
  uv run python scripts/experiments/verify_crystal_phi.py --model Qwen/Qwen3-8B
  uv run python scripts/experiments/verify_crystal_phi.py --model Qwen/Qwen3-14B --n-per-combinator 20
  uv run python scripts/experiments/verify_crystal_phi.py --model EleutherAI/pythia-2.8b-deduped

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

# ── Probe library import ─────────────────────────────────────────────────────
# Add project root to path so we can import verbum
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from verbum.probes.library import (  # noqa: E402
    Probe as CrystalProbe,
    by_combinator,
    combinator_counts,
    crystal_probes,
)

# ══════════════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2

# Crystal combinators in canonical order
CRYSTAL_COMBINATORS = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]

# Consensus 8×8 crystal (KIBC + DYW + WHNF) from cross-model derivation
# Order: K, I, B, C, D, Y, W, WHNF
CONSENSUS_8x8 = np.array([
    [+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862],
    [+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448],
    [+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227],
    [+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027],
    [+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729],
    [+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840],
    [+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379],
    [-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000],
])

# Consensus order (without S, which wasn't in the original 8×8)
_CONSENSUS_ORDER = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]


# ══════════════════════════════════════════════════════════════════════════════
# Probe selection
# ══════════════════════════════════════════════════════════════════════════════


def select_probes(
    combinators: list[str],
    n_per_combinator: int | None = None,
    seed: int = 42,
) -> dict[str, list[str]]:
    """Select probes from the unified library.

    Returns dict[combinator → list[prompt_text]].
    If n_per_combinator is None, uses all available probes.
    """
    rng = np.random.RandomState(seed)
    result: dict[str, list[str]] = {}

    for comb in combinators:
        probes = by_combinator(comb)
        prompts = [p.prompt for p in probes]

        if n_per_combinator is not None and len(prompts) > n_per_combinator:
            indices = rng.choice(len(prompts), n_per_combinator, replace=False)
            prompts = [prompts[i] for i in sorted(indices)]

        result[comb] = prompts

    return result


# ══════════════════════════════════════════════════════════════════════════════
# Zone B layer selection
# ══════════════════════════════════════════════════════════════════════════════


def get_zone_b_layers(n_layers: int, n_sample: int = 4) -> list[int]:
    """Get Zone B (middle 30-70%) layer indices, evenly spaced."""
    start = int(n_layers * 0.3)
    end = int(n_layers * 0.7)
    layers = np.linspace(start, end, min(n_sample, end - start + 1), dtype=int).tolist()
    return sorted(set(layers))


# ══════════════════════════════════════════════════════════════════════════════
# Activation extraction
# ══════════════════════════════════════════════════════════════════════════════


def find_layers_container(model):
    """Locate the decoder-layer ModuleList across architectures.

    Standard paths first (Qwen/LLaMA/Mistral, GPTNeoX/Pythia, GPT-2), then
    nested multimodal / ForConditionalGeneration paths (Gemma4 wraps the text
    decoder under model.model.language_model.layers), then a generic
    longest-ModuleList fallback. Returns the container or None.
    """
    candidates = [
        lambda m: m.model.layers,
        lambda m: m.gpt_neox.layers,
        lambda m: m.transformer.h,
        lambda m: m.model.language_model.layers,
        lambda m: m.language_model.model.layers,
        lambda m: m.language_model.layers,
    ]
    for getter in candidates:
        try:
            c = getter(model)
        except AttributeError:
            continue
        if c is not None and len(c) > 0:
            return c
    import torch.nn as nn
    best = None
    for _name, mod in model.named_modules():
        if isinstance(mod, nn.ModuleList) and (best is None or len(mod) > len(best)):
            best = mod
    return best


def find_gate_proj(layer_module):
    """Find the gate_proj (or equivalent) in a transformer layer.

    Handles multiple architectures:
    - Qwen/LLaMA/Mistral: layer.mlp.gate_proj
    - GPTNeoX/Pythia: layer.mlp.dense_h_to_4h (single linear, no gating)
    - Fused: layer.mlp.gate_up_proj

    Returns (module, is_fused) or (None, False).
    """
    mlp = getattr(layer_module, 'mlp', None)
    if mlp is None:
        return None, False

    if hasattr(mlp, 'gate_proj'):
        return mlp.gate_proj, False
    elif hasattr(mlp, 'gate_up_proj'):
        return mlp.gate_up_proj, True
    elif hasattr(mlp, 'dense_h_to_4h'):
        # GPTNeoX/Pythia — single linear projection (no separate gate)
        return mlp.dense_h_to_4h, False
    return None, False


def extract_gate_activations(
    model,
    tokenizer,
    prompts: list[str],
    layers: list[int],
    device: str,
    max_length: int = 128,
) -> np.ndarray:
    """Extract gate_proj activations, mean-pooled over sequence.

    Returns: (n_prompts, d_ff) array.
    """
    captured: dict[int, torch.Tensor] = {}
    hooks = []

    intermediate_size = getattr(model.config, 'intermediate_size', None)
    if intermediate_size is None:  # nested multimodal config (e.g. Gemma4)
        tc = getattr(model.config, 'text_config', None)
        intermediate_size = getattr(tc, 'intermediate_size', None)

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            captured[layer_idx] = output.detach().float()
        return hook_fn

    # Find the layers container (architecture-agnostic)
    layers_container = find_layers_container(model)
    if layers_container is None:
        raise RuntimeError(f"Cannot find layers in model {type(model).__name__}")

    # Register hooks
    for layer_idx in layers:
        layer = layers_container[layer_idx]
        gate_module, is_fused = find_gate_proj(layer)
        if gate_module is not None:
            hooks.append(gate_module.register_forward_hook(make_hook(layer_idx)))

    all_acts = []
    for prompt in prompts:
        captured.clear()
        inputs = tokenizer(
            prompt, return_tensors="pt",
            padding=False, truncation=True, max_length=max_length,
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            model(**inputs)

        # Mean-pool across layers and sequence positions
        layer_acts = []
        for layer_idx in layers:
            if layer_idx in captured:
                act = captured[layer_idx]
                # If fused gate_up_proj, take only the gate half
                if intermediate_size and act.shape[-1] > intermediate_size:
                    act = act[..., :intermediate_size]
                # Mean over sequence, squeeze batch
                mean_act = act.mean(dim=1).squeeze(0).cpu().numpy()
                layer_acts.append(mean_act)

        if layer_acts:
            all_acts.append(np.mean(layer_acts, axis=0))

    for hook in hooks:
        hook.remove()

    return np.array(all_acts)


# ══════════════════════════════════════════════════════════════════════════════
# Crystal measurement
# ══════════════════════════════════════════════════════════════════════════════


def compute_crystal_matrix(
    model,
    tokenizer,
    probe_dict: dict[str, list[str]],
    layers: list[int],
    device: str,
    combinators: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Compute N×N crystal cosine matrix from activation PCA.

    Returns: (cosine_matrix, eigenvalues, eigenvectors, stats)
    """
    n_combs = len(combinators)

    # Collect all activations
    all_activations = []
    probe_labels = []
    per_comb_counts: dict[str, int] = {}

    for comb in combinators:
        prompts = probe_dict.get(comb, [])
        if not prompts:
            print(f"  WARNING: no probes for {comb}, skipping")
            continue

        acts = extract_gate_activations(model, tokenizer, prompts, layers, device)
        per_comb_counts[comb] = len(acts)
        for act in acts:
            all_activations.append(act)
            probe_labels.append(comb)

    all_acts = np.array(all_activations)
    n_probes, d_ff = all_acts.shape
    print(f"  Total activations: {n_probes} probes × {d_ff} dims")
    print(f"  Per combinator: {per_comb_counts}")

    # Center
    mean_act = all_acts.mean(axis=0)
    centered = all_acts - mean_act

    # PCA via SVD
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    n_pcs = min(n_combs * 2, len(S))
    pcs = Vt[:n_pcs]

    total_var = (S ** 2).sum()
    cumulative = 0.0
    print(f"\n  PCA variance explained (top {min(10, n_pcs)}):")
    for i in range(min(10, n_pcs)):
        var_pct = S[i] ** 2 / total_var * 100
        cumulative += var_pct
        print(f"    PC{i}: {var_pct:.1f}%  (cum: {cumulative:.1f}%)")

    # Project each combinator's mean activation onto PCs
    projections = []
    for comb in combinators:
        indices = [i for i, l in enumerate(probe_labels) if l == comb]
        if not indices:
            projections.append(np.zeros(n_pcs))
            continue
        comb_acts = centered[indices]
        mean_comb = comb_acts.mean(axis=0)
        proj = pcs @ mean_comb
        projections.append(proj)

    projections = np.array(projections)  # (n_combs, n_pcs)

    # Cosine similarity matrix
    norms = np.linalg.norm(projections, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normed = projections / norms
    cosine = normed @ normed.T

    # Eigendecompose
    eigvals, eigvecs = np.linalg.eigh(cosine)
    idx = np.argsort(-eigvals)
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    stats = {
        "n_probes": n_probes,
        "d_ff": d_ff,
        "per_comb_counts": per_comb_counts,
        "pca_variance_explained": [(S[i] ** 2 / total_var * 100) for i in range(min(20, len(S)))],
    }

    return cosine, eigvals, eigvecs, stats


# ══════════════════════════════════════════════════════════════════════════════
# Analysis
# ══════════════════════════════════════════════════════════════════════════════


def print_cosine_matrix(cosine: np.ndarray, combinators: list[str]):
    """Pretty-print the cosine matrix."""
    n = len(combinators)
    short = [c[:4] for c in combinators]

    header = '         ' + '  '.join(f'{s:>6}' for s in short)
    print(f"  {header}")
    for i in range(n):
        vals = '  '.join(f'{cosine[i,j]:>6.3f}' for j in range(n))
        print(f"    {short[i]:>4}: {vals}")


def check_phi_structure(eigvals: np.ndarray, label: str = ""):
    """Check if eigenvalues follow φ^(p/q) structure."""
    C = eigvals[0]
    if C <= 0:
        print("  WARNING: leading eigenvalue ≤ 0, cannot check phi structure")
        return

    print(f"\n{'='*70}")
    print(f"  PHI STRUCTURE CHECK{' — ' + label if label else ''}")
    print(f"{'='*70}")
    print(f"\n  C = λ₀ = {C:.6f}")
    print(f"  φ = {PHI:.6f}")
    print()

    print(f"  {'PC':>4} {'Eigenvalue':>12} {'log_φ':>10} {'Best p/q':>10} {'Predicted':>12} {'Error':>8}")
    print(f"  {'─'*4} {'─'*12} {'─'*10} {'─'*10} {'─'*12} {'─'*8}")

    for i in range(len(eigvals)):
        ev = eigvals[i]
        if ev > 0.001:
            log_phi_val = np.log(ev / C) / np.log(PHI)

            best_err = float('inf')
            best_frac = (0, 1)
            for d in range(1, 13):
                for n in range(-8 * d, 1):
                    predicted = C * PHI ** (n / d)
                    err = abs(predicted - ev) / ev
                    if err < best_err:
                        best_err = err
                        best_frac = (n, d)

            nn, dd = best_frac
            predicted = C * PHI ** (nn / dd)
            print(f"  {i:>4} {ev:>12.6f} {log_phi_val:>10.4f}  {nn:>3}/{dd:<5} {predicted:>12.6f} {best_err*100:>7.2f}%")
        elif ev > -0.1:
            print(f"  {i:>4} {ev:>12.6f}  (near zero)")
        else:
            print(f"  {i:>4} {ev:>12.6f}  (negative)")

    # Key ratio
    if len(eigvals) >= 2 and eigvals[1] > 0.01:
        ratio = eigvals[0] / eigvals[1]
        target = PHI ** (4 / 5)
        err = abs(ratio - target) / target * 100
        print(f"\n  λ₀/λ₁ = {ratio:.4f}  (target φ^(4/5) = {target:.4f}, error = {err:.1f}%)")


def compare_with_consensus(
    cosine: np.ndarray,
    eigvals: np.ndarray,
    combinators: list[str],
) -> dict[str, float]:
    """Compare measured crystal with consensus 8×8.

    Maps the measured combinators to the consensus order and computes
    correlation metrics.
    """
    # Build index mapping: which measured combinators are in consensus?
    consensus_indices = []
    measured_indices = []
    matched_names = []

    for ci, cname in enumerate(_CONSENSUS_ORDER):
        if cname in combinators:
            mi = combinators.index(cname)
            consensus_indices.append(ci)
            measured_indices.append(mi)
            matched_names.append(cname)

    n_matched = len(matched_names)
    if n_matched < 4:
        print(f"\n  Only {n_matched} combinators match consensus — skipping comparison")
        return {"n_matched": n_matched}

    # Extract submatrices
    measured_sub = cosine[np.ix_(measured_indices, measured_indices)]
    consensus_sub = CONSENSUS_8x8[np.ix_(consensus_indices, consensus_indices)]

    # Matrix correlation
    corr = np.corrcoef(measured_sub.ravel(), consensus_sub.ravel())[0, 1]

    # Eigenvalue ratio correlation
    eigvals_consensus = np.linalg.eigvalsh(consensus_sub)[::-1]
    eigvals_measured = np.linalg.eigvalsh(measured_sub)[::-1]

    if eigvals_consensus[0] > 0 and eigvals_measured[0] > 0:
        ratios_consensus = eigvals_consensus / eigvals_consensus[0]
        ratios_measured = eigvals_measured / eigvals_measured[0]
        ratio_corr = np.corrcoef(ratios_measured, ratios_consensus)[0, 1]
    else:
        ratio_corr = float('nan')

    print(f"\n{'='*70}")
    print(f"  CONSENSUS COMPARISON ({n_matched} combinators: {', '.join(matched_names)})")
    print(f"{'='*70}")
    print(f"  Cosine matrix correlation:    {corr:.6f}")
    print(f"  Eigenvalue ratio correlation: {ratio_corr:.6f}")

    # Per-pair comparison (top deviations)
    diffs = []
    for i in range(n_matched):
        for j in range(i + 1, n_matched):
            diff = measured_sub[i, j] - consensus_sub[i, j]
            diffs.append((matched_names[i], matched_names[j], measured_sub[i, j], consensus_sub[i, j], diff))

    diffs.sort(key=lambda x: -abs(x[4]))
    print(f"\n  Top cosine deviations from consensus:")
    print(f"  {'Pair':>10} {'Measured':>10} {'Consensus':>10} {'Δ':>8}")
    for name1, name2, m, c, d in diffs[:8]:
        print(f"  {name1+'-'+name2:>10} {m:>10.3f} {c:>10.3f} {d:>+8.3f}")

    # Key structural signatures
    if "B" in matched_names and "D" in matched_names:
        bi, di = matched_names.index("B"), matched_names.index("D")
        bd_meas = measured_sub[bi, di]
        bd_cons = consensus_sub[consensus_indices[bi] if bi < len(consensus_indices) else 0,
                                consensus_indices[di] if di < len(consensus_indices) else 0]
        # Recompute from consensus directly
        bd_cons = CONSENSUS_8x8[2, 4]  # B=2, D=4 in consensus order
        print(f"\n  B-D similarity: {bd_meas:.3f} (consensus: {bd_cons:.3f})")
        print(f"    D=BB compound structure {'visible' if bd_meas > 0.7 else 'weak'}")

    if "K" in matched_names and "I" in matched_names:
        ki, ii = matched_names.index("K"), matched_names.index("I")
        ki_meas = measured_sub[ki, ii]
        print(f"  K-I similarity: {ki_meas:.3f} (consensus: {CONSENSUS_8x8[0,1]:.3f})")
        print(f"    Selection cluster {'visible' if ki_meas > 0.5 else 'weak'}")

    return {
        "n_matched": n_matched,
        "matched_combinators": matched_names,
        "cosine_correlation": float(corr),
        "eigenvalue_ratio_correlation": float(ratio_corr),
    }


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="Verify crystal φ structure in a model using unified probe library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --model Qwen/Qwen3-8B                       # default (lambda fully formed)
  %(prog)s --model Qwen/Qwen3-14B --n-per-combinator 30  # medium run
  %(prog)s --model EleutherAI/pythia-2.8b-deduped      # cross-family test
        """,
    )
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B",
                        help="HuggingFace model ID (default: Qwen/Qwen3-8B)")
    parser.add_argument("--device", type=str, default="auto",
                        help="Device: auto, cpu, cuda, mps (default: auto)")
    parser.add_argument("--n-per-combinator", type=int, default=None,
                        help="Max probes per combinator (default: all available)")
    parser.add_argument("--combinators", type=str, default=None,
                        help="Comma-separated combinator list (default: all 9 crystal)")
    parser.add_argument("--n-layers", type=int, default=4,
                        help="Number of Zone B layers to sample (default: 4)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSON path (default: results/crystal-phi-verify/<model>.json)")
    args = parser.parse_args()

    # ── Device selection ──────────────────────────────────────────────────
    if args.device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    else:
        device = args.device

    # ── Combinator selection ──────────────────────────────────────────────
    if args.combinators:
        combinators = [c.strip() for c in args.combinators.split(",")]
    else:
        combinators = list(CRYSTAL_COMBINATORS)

    # ── Probe selection ───────────────────────────────────────────────────
    print(f"\n{'═'*70}")
    print(f"  Crystal φ Verification — Unified Probe Library")
    print(f"{'═'*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {device}")
    print(f"  Combinators: {', '.join(combinators)}")

    probe_dict = select_probes(combinators, args.n_per_combinator)
    total_probes = sum(len(v) for v in probe_dict.values())
    print(f"  Probes per combinator:")
    for comb in combinators:
        n = len(probe_dict.get(comb, []))
        print(f"    {comb:6s}: {n}")
    print(f"  Total probes: {total_probes}")

    # ── Load model ────────────────────────────────────────────────────────
    print(f"\n  Loading {args.model}...")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        dtype=torch.float16,
        device_map=device if device != "mps" else None,
        trust_remote_code=True,
    )
    if device == "mps":
        model = model.to(device)
    model.eval()

    cfg = model.config
    tcfg = getattr(cfg, 'text_config', None)  # nested multimodal (Gemma4)

    def _cfg(name, default=None):
        v = getattr(cfg, name, None)
        if v is None and tcfg is not None:
            v = getattr(tcfg, name, None)
        return default if v is None else v

    n_layers = _cfg('num_hidden_layers')
    d_model = _cfg('hidden_size')
    d_ff = _cfg('intermediate_size', d_model * 4)
    load_time = time.time() - t0
    print(f"  Loaded in {load_time:.1f}s: {n_layers} layers, d={d_model}, d_ff={d_ff}")

    # ── Zone B layers ─────────────────────────────────────────────────────
    layers = get_zone_b_layers(n_layers, args.n_layers)
    print(f"  Zone B layers: {layers}")

    # ── Compute crystal ───────────────────────────────────────────────────
    print(f"\n  Running {total_probes} combinator probes...")
    t1 = time.time()
    cosine, eigvals, eigvecs, stats = compute_crystal_matrix(
        model, tokenizer, probe_dict, layers, device, combinators,
    )
    probe_time = time.time() - t1
    print(f"  Done in {probe_time:.1f}s ({total_probes / probe_time:.1f} probes/s)")

    # ── Print results ─────────────────────────────────────────────────────
    print(f"\n  {len(combinators)}×{len(combinators)} cosine matrix:")
    print_cosine_matrix(cosine, combinators)

    check_phi_structure(eigvals, label=args.model)
    comparison = compare_with_consensus(cosine, eigvals, combinators)

    # ── Save results ──────────────────────────────────────────────────────
    model_slug = args.model.replace("/", "_")
    output_path = args.output or f"results/crystal-phi-verify/{model_slug}.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def _jsonable(obj):
        """Recursively convert numpy types to native Python for JSON."""
        if isinstance(obj, dict):
            return {k: _jsonable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_jsonable(v) for v in obj]
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    results = _jsonable({
        "model": args.model,
        "n_layers": n_layers,
        "d_model": d_model,
        "d_ff": d_ff,
        "zone_b_layers": layers,
        "combinators": combinators,
        "n_per_combinator": args.n_per_combinator,
        "total_probes": total_probes,
        "per_combinator_counts": stats["per_comb_counts"],
        "eigenvalues": eigvals.tolist(),
        "cosine_matrix": cosine.tolist(),
        "pca_variance_explained": stats["pca_variance_explained"],
        "consensus_comparison": comparison,
        "timing": {
            "model_load_s": round(load_time, 1),
            "probe_run_s": round(probe_time, 1),
            "probes_per_s": round(total_probes / probe_time, 1),
        },
    })

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {output_path}")
    print(f"{'═'*70}\n")


if __name__ == "__main__":
    main()
