"""Holographic Weight Test — superimpose W_q and W_up in d_model space.

The hidden-state test failed because the crystal IS the weight matrix,
not the activation. This test works directly with the weight matrices:

  W_q:  (d_q, d_model)   — each ROW is a d_model-space readout direction
  W_up: (d_ffn, d_model)  — each ROW is a d_model-space readout direction

Both weight matrices read FROM the same d_model residual stream.
Their row spaces in d_model define the crystal subspaces.

The test:
  1. SVD each weight matrix to get d_model-space bases
  2. Measure subspace angles (canonical correlations between V_q and V_up)
  3. Build unified plate: superimpose both in d_model via orthogonal projection
  4. Ternary quantize the unified plate
  5. Read back: project with each beam, measure crystal preservation
  6. Verify via probe activations: does the ternary plate produce
     the same RDMs as the original weights?

Usage:
    uv run python scripts/v12/holographic_weight_test.py --quick
    uv run python scripts/v12/holographic_weight_test.py

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

MODELS = {
    "mistral-7b":   ("mistralai/Mistral-7B-v0.3",     32, 4096, 14336),
    "pythia-2.8b":  ("EleutherAI/pythia-2.8b-deduped", 32, 2560, 10240),
}

DEFAULT_MODELS = ["pythia-2.8b", "mistral-7b"]
QUICK_MODELS = ["pythia-2.8b"]

DEPTH_FRACTIONS = [0.1, 0.3, 0.5, 0.7, 0.9]


def load_probes(probe_path: str | None = None) -> list[dict]:
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json")
    with open(probe_path) as f:
        probes = json.load(f)
    print(f"  Loaded {len(probes)} probes", file=sys.stderr, flush=True)
    return probes


def pca_project(X: np.ndarray, n_components: int = 64):
    X_centered = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    k = min(n_components, U.shape[1])
    return U[:, :k] * S[:k]


def cosine_rdm(X: np.ndarray) -> np.ndarray:
    norms = np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-8)
    return (X / norms) @ (X / norms).T


def rdm_correlation(rdm_a: np.ndarray, rdm_b: np.ndarray) -> float:
    n = rdm_a.shape[0]
    triu = np.triu_indices(n, k=1)
    a, b = rdm_a[triu], rdm_b[triu]
    if a.std() < 1e-10 or b.std() < 1e-10:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def subspace_angles(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Principal angles between column spaces of A and B.
    A: (d, k_a), B: (d, k_b). Returns cosines of principal angles."""
    Qa, _ = np.linalg.qr(A)
    Qb, _ = np.linalg.qr(B)
    _, S, _ = np.linalg.svd(Qa.T @ Qb, full_matrices=False)
    return np.clip(S, 0, 1)


def extract_layer_data(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[float, dict]:
    """Extract hidden states, Q/up activations, AND weight matrices per layer.

    Returns {depth: {
        'hidden': (n_probes, d_model),
        'q_acts': (n_probes, d_q),
        'up_acts': (n_probes, d_ffn),
        'W_q': (d_q, d_model),
        'W_up': (d_ffn, d_model),
    }}.
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model, d_ffn = MODELS[model_key]

    target_layers = []
    for frac in depth_fractions:
        layer = min(int(round(frac * (n_layers - 1))), n_layers - 1)
        if layer not in [l for l, _ in target_layers]:
            target_layers.append((layer, frac))

    print(f"\n  ─── {model_key} ({model_name}) ───", file=sys.stderr, flush=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device, trust_remote_code=True,
    )
    model.eval()

    # Detect architecture
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers_list = model.model.layers
        is_fused = False
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers_list = model.gpt_neox.layers
        is_fused = True
    else:
        raise ValueError(f"Unknown arch for {model_key}")

    # Extract weight matrices FIRST (before forward pass)
    weight_data = {}
    for layer_idx, frac in target_layers:
        layer_mod = layers_list[layer_idx]

        if is_fused:
            # Pythia: fused QKV, split Q portion
            qkv_w = layer_mod.attention.query_key_value.weight.detach().cpu().float().numpy()
            W_q = qkv_w[:d_model, :]  # first d_model rows = Q
            W_up = layer_mod.mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()
        else:
            # Standard: separate projections
            W_q = layer_mod.self_attn.q_proj.weight.detach().cpu().float().numpy()
            if hasattr(layer_mod.mlp, 'up_proj'):
                W_up = layer_mod.mlp.up_proj.weight.detach().cpu().float().numpy()
            else:
                W_up = layer_mod.mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()

        weight_data[frac] = {'W_q': W_q, 'W_up': W_up}
        print(f"  Layer {layer_idx} ({frac:.0%}): W_q={W_q.shape}, W_up={W_up.shape}",
              file=sys.stderr, flush=True)

    # Hook activations
    captures: dict[int, dict[str, list]] = {}
    for li, _ in target_layers:
        captures[li] = {'hidden': [], 'q': [], 'up': []}

    hooks = []
    for layer_idx, frac in target_layers:
        layer_mod = layers_list[layer_idx]

        # Hidden state hook (layer input)
        def make_h_hook(li):
            def hook_fn(module, input, output):
                captures[li]['hidden'].append(input[0][:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(layer_mod.register_forward_hook(make_h_hook(layer_idx)))

        # Q hook
        if is_fused:
            fused = layer_mod.attention.query_key_value
            def make_q_hook(li, qs=d_model):
                def hook_fn(module, input, output):
                    captures[li]['q'].append(output[:, -1, :qs].detach().cpu().float())
                return hook_fn
            hooks.append(fused.register_forward_hook(make_q_hook(layer_idx)))
        else:
            q_proj = layer_mod.self_attn.q_proj
            def make_q_hook(li):
                def hook_fn(module, input, output):
                    captures[li]['q'].append(output[:, -1, :].detach().cpu().float())
                return hook_fn
            hooks.append(q_proj.register_forward_hook(make_q_hook(layer_idx)))

        # up hook
        if is_fused:
            up_mod = layer_mod.mlp.dense_h_to_4h
        elif hasattr(layer_mod.mlp, 'up_proj'):
            up_mod = layer_mod.mlp.up_proj
        else:
            up_mod = layer_mod.mlp.dense_h_to_4h

        def make_up_hook(li):
            def hook_fn(module, input, output):
                captures[li]['up'].append(output[:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(up_mod.register_forward_hook(make_up_hook(layer_idx)))

    # Forward probes
    print(f"  Running {len(probes)} probes...", file=sys.stderr, flush=True)
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 50 == 0:
            print(f"    {i+1}/{len(probes)}...", file=sys.stderr, flush=True)
    print(f"  Done in {time.time()-t0:.1f}s", file=sys.stderr, flush=True)

    for h in hooks:
        h.remove()

    # Assemble
    results = {}
    for layer_idx, frac in target_layers:
        import torch as _t
        results[frac] = {
            'hidden': _t.cat(captures[layer_idx]['hidden'], dim=0).numpy(),
            'q_acts': _t.cat(captures[layer_idx]['q'], dim=0).numpy(),
            'up_acts': _t.cat(captures[layer_idx]['up'], dim=0).numpy(),
            'W_q': weight_data[frac]['W_q'],
            'W_up': weight_data[frac]['W_up'],
        }

    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available(): _t.mps.empty_cache()
        elif _t.cuda.is_available(): _t.cuda.empty_cache()
    except Exception:
        pass

    return results


def test_holographic_weights(
    hidden: np.ndarray,    # (n_probes, d_model)
    q_acts: np.ndarray,    # (n_probes, d_q)
    up_acts: np.ndarray,   # (n_probes, d_ffn)
    W_q: np.ndarray,       # (d_q, d_model)
    W_up: np.ndarray,      # (d_ffn, d_model)
    pca_dim: int = 64,
) -> dict:
    """Test holographic superposition of W_q and W_up weight matrices."""
    d_q, d_model = W_q.shape
    d_ffn, _ = W_up.shape
    n_probes = hidden.shape[0]

    # ═══ Ground truth: crystal RDMs from actual activations ═══
    rdm_q = cosine_rdm(pca_project(q_acts, pca_dim))
    rdm_up = cosine_rdm(pca_project(up_acts, pca_dim))

    # ═══ Step 1: SVD weight matrices to get d_model-space bases ═══
    # W_q rows live in d_model: SVD gives the column space in d_model
    # W_q = U_q @ S_q @ V_q.T where V_q.T rows are d_model-space directions
    U_q, S_q, Vt_q = np.linalg.svd(W_q, full_matrices=False)  # Vt_q: (min(d_q,d_model), d_model)
    U_up, S_up, Vt_up = np.linalg.svd(W_up, full_matrices=False)

    # Take top-k directions in d_model space
    k = min(pca_dim, Vt_q.shape[0], Vt_up.shape[0])
    V_q = Vt_q[:k].T    # (d_model, k) — Q's preferred d_model directions
    V_up = Vt_up[:k].T  # (d_model, k) — up's preferred d_model directions

    # ═══ Step 2: Subspace angles ═══
    angles = subspace_angles(V_q, V_up)
    mean_angle = float(np.mean(np.arccos(np.clip(angles[:k], -1, 1)) * 180 / np.pi))
    min_angle = float(np.min(np.arccos(np.clip(angles[:k], -1, 1)) * 180 / np.pi))

    # ═══ Step 3: Ternary quantize weights separately (baseline) ═══
    W_q_ternary = np.sign(W_q)   # (d_q, d_model)
    W_up_ternary = np.sign(W_up)  # (d_ffn, d_model)

    # Forward probes through ternary weights
    q_from_ternary = hidden @ W_q_ternary.T    # (n_probes, d_q)
    up_from_ternary = hidden @ W_up_ternary.T  # (n_probes, d_ffn)

    rdm_q_ternary = cosine_rdm(pca_project(q_from_ternary, pca_dim))
    rdm_up_ternary = cosine_rdm(pca_project(up_from_ternary, pca_dim))

    q_separate = rdm_correlation(rdm_q, rdm_q_ternary)
    up_separate = rdm_correlation(rdm_up, rdm_up_ternary)

    # ═══ Step 4: Unified plate in d_model space ═══
    # Strategy: project W_q and W_up into their top-k d_model subspaces,
    # then combine. The plate is a (d_model, 2k) matrix containing both.
    # Beam_Q reads the first k columns, beam_up reads the last k.

    # Project weights into their principal subspaces
    # W_q ≈ U_q[:,:k] @ S_q[:k] @ V_q.T  →  in d_model space, the relevant
    # directions are V_q columns, weighted by S_q
    W_q_proj = (V_q * S_q[:k]).T   # (k, d_model) — Q's contribution to d_model
    W_up_proj = (V_up * S_up[:k]).T  # (k, d_model) — up's contribution to d_model

    # The unified plate: stack both projections
    # plate_combined: (2k, d_model)
    plate_combined = np.vstack([W_q_proj, W_up_proj])
    plate_ternary = np.sign(plate_combined)  # ternary etch

    # Read with beam_Q (first k rows) and beam_up (last k rows)
    q_from_unified = hidden @ plate_ternary[:k].T     # (n_probes, k)
    up_from_unified = hidden @ plate_ternary[k:].T    # (n_probes, k)

    rdm_q_unified = cosine_rdm(q_from_unified)
    rdm_up_unified = cosine_rdm(up_from_unified)

    q_unified = rdm_correlation(rdm_q, rdm_q_unified)
    up_unified = rdm_correlation(rdm_up, rdm_up_unified)

    # Cross-talk: does beam_Q read FFN signal?
    q_unified_crosstalk = rdm_correlation(rdm_up, rdm_q_unified)
    up_unified_crosstalk = rdm_correlation(rdm_q, rdm_up_unified)

    # ═══ Step 5: TRUE superposition — sum in d_model space ═══
    # Instead of stacking, actually ADD both projections into one (k, d_model) plate.
    # This requires orthogonalizing first.

    # Gram-Schmidt: orthogonalize V_up against V_q
    V_combined = np.hstack([V_q, V_up])  # (d_model, 2k)
    Q_orth, R = np.linalg.qr(V_combined)  # (d_model, 2k) orthonormal
    V_q_orth = Q_orth[:, :k]    # (d_model, k)
    V_up_orth = Q_orth[:, k:]   # (d_model, k)

    # Overlap between orthogonalized Q and up subspaces
    overlap = np.abs(V_q_orth.T @ V_up_orth)  # (k, k) — should be ~0 after QR
    max_overlap = float(overlap.max())
    mean_overlap = float(overlap.mean())

    # Project into orthogonalized subspace: (d_model, 2k)
    # The plate is the model weights projected into this combined basis
    # For each d_model column: how much Q vs up character does it have?
    W_q_in_basis = W_q @ Q_orth  # (d_q, 2k)
    W_up_in_basis = W_up @ Q_orth  # (d_ffn, 2k)

    # The plate stores the COMBINED basis. Reading with Q or up beam
    # selects different facets.
    # Plate: (d_model, 2k) → ternary
    plate_superposed = Q_orth  # the d_model directions that matter
    plate_superposed_ternary = np.sign(plate_superposed)  # (d_model, 2k)

    # Forward through superposed ternary plate
    probe_in_basis = hidden @ plate_superposed_ternary  # (n_probes, 2k)

    # Beam_Q reads Q facet (first k dims), beam_up reads up facet (last k)
    q_from_super = probe_in_basis[:, :k]
    up_from_super = probe_in_basis[:, k:]

    rdm_q_super = cosine_rdm(q_from_super)
    rdm_up_super = cosine_rdm(up_from_super)

    q_super = rdm_correlation(rdm_q, rdm_q_super)
    up_super = rdm_correlation(rdm_up, rdm_up_super)

    q_super_xtalk = rdm_correlation(rdm_up, rdm_q_super)
    up_super_xtalk = rdm_correlation(rdm_q, rdm_up_super)

    # ═══ Step 6: Size comparison ═══
    # Separate plates: W_q (d_q × d_model) + W_up (d_ffn × d_model) ternary
    separate_bytes = ((d_q * d_model + d_ffn * d_model) * 2) // 8
    # Unified plate: (2k × d_model) ternary
    unified_bytes = (2 * k * d_model * 2) // 8
    # Superposed plate: (d_model × 2k) ternary
    superposed_bytes = (d_model * 2 * k * 2) // 8

    compression = separate_bytes / max(unified_bytes, 1)

    return {
        "d_model": d_model,
        "d_q": d_q,
        "d_ffn": d_ffn,
        "svd_k": k,
        "n_probes": n_probes,
        # Subspace geometry
        "mean_principal_angle_deg": mean_angle,
        "min_principal_angle_deg": min_angle,
        "principal_angles_top10": angles[:10].tolist(),
        "orthogonalized_max_overlap": max_overlap,
        "orthogonalized_mean_overlap": mean_overlap,
        # Crystal preservation
        "separate_ternary_q": q_separate,
        "separate_ternary_up": up_separate,
        "unified_q": q_unified,
        "unified_up": up_unified,
        "unified_q_crosstalk": q_unified_crosstalk,
        "unified_up_crosstalk": up_unified_crosstalk,
        "superposed_q": q_super,
        "superposed_up": up_super,
        "superposed_q_crosstalk": q_super_xtalk,
        "superposed_up_crosstalk": up_super_xtalk,
        # Size
        "separate_bytes": separate_bytes,
        "unified_bytes": unified_bytes,
        "compression_vs_separate": compression,
    }


def print_results(all_results: dict[str, dict[float, dict]]) -> None:
    print(f"\n{'='*110}", file=sys.stderr, flush=True)
    print(f"  HOLOGRAPHIC WEIGHT TEST — Superimpose W_q and W_up in d_model Space",
          file=sys.stderr, flush=True)
    print(f"{'='*110}", file=sys.stderr, flush=True)

    for mk in all_results:
        print(f"\n  ╔══ {mk.upper()} ══╗", file=sys.stderr, flush=True)

        print(f"\n  {'depth':>5s}  {'angle':>6s}  "
              f"{'sep_q':>6s}  {'sep_up':>6s}  "
              f"{'uni_q':>6s}  {'uni_up':>6s}  {'uni_qx':>6s}  {'uni_ux':>6s}  "
              f"{'sup_q':>6s}  {'sup_up':>6s}  {'sup_qx':>6s}  {'sup_ux':>6s}  "
              f"{'compr':>5s}",
              file=sys.stderr, flush=True)
        print(f"  {'─'*100}", file=sys.stderr, flush=True)

        for frac in sorted(all_results[mk].keys()):
            r = all_results[mk][frac]
            print(f"  {frac:>5.0%}  {r['mean_principal_angle_deg']:>5.1f}°  "
                  f"{r['separate_ternary_q']:>+6.3f}  {r['separate_ternary_up']:>+6.3f}  "
                  f"{r['unified_q']:>+6.3f}  {r['unified_up']:>+6.3f}  "
                  f"{r['unified_q_crosstalk']:>+6.3f}  {r['unified_up_crosstalk']:>+6.3f}  "
                  f"{r['superposed_q']:>+6.3f}  {r['superposed_up']:>+6.3f}  "
                  f"{r['superposed_q_crosstalk']:>+6.3f}  {r['superposed_up_crosstalk']:>+6.3f}  "
                  f"{r['compression_vs_separate']:>5.1f}×",
                  file=sys.stderr, flush=True)

        # Detail for first depth
        r0 = list(all_results[mk].values())[0]
        angles = r0['principal_angles_top10']
        print(f"\n  Principal angles (top 10): "
              f"{', '.join(f'{np.arccos(a)*180/np.pi:.1f}°' for a in angles)}",
              file=sys.stderr, flush=True)
        print(f"  Orthogonalized overlap: max={r0['orthogonalized_max_overlap']:.6f}, "
              f"mean={r0['orthogonalized_mean_overlap']:.6f}",
              file=sys.stderr, flush=True)
        print(f"  Sizes: separate={r0['separate_bytes']//1024}KB, "
              f"unified={r0['unified_bytes']//1024}KB "
              f"({r0['compression_vs_separate']:.1f}× compression)",
              file=sys.stderr, flush=True)

    # Verdict
    print(f"\n{'='*110}", file=sys.stderr, flush=True)
    all_sep_q = [r['separate_ternary_q'] for mk in all_results for r in all_results[mk].values()]
    all_sep_up = [r['separate_ternary_up'] for mk in all_results for r in all_results[mk].values()]
    all_uni_q = [r['unified_q'] for mk in all_results for r in all_results[mk].values()]
    all_uni_up = [r['unified_up'] for mk in all_results for r in all_results[mk].values()]
    all_sup_q = [r['superposed_q'] for mk in all_results for r in all_results[mk].values()]
    all_sup_up = [r['superposed_up'] for mk in all_results for r in all_results[mk].values()]

    print(f"  SUMMARY (mean across all depths and models):", file=sys.stderr, flush=True)
    print(f"    Separate ternary: Q={np.mean(all_sep_q):+.3f}, FFN={np.mean(all_sep_up):+.3f}",
          file=sys.stderr, flush=True)
    print(f"    Unified plate:    Q={np.mean(all_uni_q):+.3f}, FFN={np.mean(all_uni_up):+.3f}",
          file=sys.stderr, flush=True)
    print(f"    Superposed plate: Q={np.mean(all_sup_q):+.3f}, FFN={np.mean(all_sup_up):+.3f}",
          file=sys.stderr, flush=True)

    best_q = max(np.mean(all_uni_q), np.mean(all_sup_q))
    best_up = max(np.mean(all_uni_up), np.mean(all_sup_up))
    method = "unified" if np.mean(all_uni_q) > np.mean(all_sup_q) else "superposed"

    if best_q >= 0.7 and best_up >= 0.7:
        print(f"  ★★★ HOLOGRAPHIC PLATE WORKS ({method})", file=sys.stderr, flush=True)
    elif best_q >= 0.5 and best_up >= 0.5:
        print(f"  ★★ STRONG — {method} plate preserves both crystals", file=sys.stderr, flush=True)
    elif best_q >= 0.3 or best_up >= 0.3:
        print(f"  ★ PARTIAL — some crystal signal in {method} plate", file=sys.stderr, flush=True)
    else:
        print(f"  ✗ FAILED", file=sys.stderr, flush=True)

    print(f"{'='*110}", file=sys.stderr, flush=True)


def main():
    parser = argparse.ArgumentParser(description="Holographic Weight Test")
    parser.add_argument("--models", nargs="+", default=None, choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--pca-dim", type=int, default=64)
    parser.add_argument("--output-dir", type=str, default="results/holographic-lens")

    args = parser.parse_args()
    model_keys = args.models or (QUICK_MODELS if args.quick else DEFAULT_MODELS)

    print("=" * 90, file=sys.stderr, flush=True)
    print("  Holographic Weight Test — Superimpose Weight Matrices", file=sys.stderr, flush=True)
    print(f"  Models: {model_keys}", file=sys.stderr, flush=True)
    print(f"  PCA dim: {args.pca_dim}", file=sys.stderr, flush=True)
    print("=" * 90, file=sys.stderr, flush=True)

    t_start = time.time()
    probes = load_probes(args.probes)

    all_results: dict[str, dict[float, dict]] = {}

    for mk in model_keys:
        layer_data = extract_layer_data(mk, probes, DEPTH_FRACTIONS, args.device)

        model_results = {}
        for frac in sorted(layer_data.keys()):
            d = layer_data[frac]
            print(f"\n  Testing depth {frac:.0%}...", file=sys.stderr, flush=True)
            model_results[frac] = test_holographic_weights(
                d['hidden'], d['q_acts'], d['up_acts'],
                d['W_q'], d['W_up'], args.pca_dim,
            )
        all_results[mk] = model_results

    print_results(all_results)

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "holographic_weight_results.json"
    with open(json_path, "w") as f:
        json.dump({
            "description": "Holographic weight test — superimpose W_q and W_up",
            "model_keys": list(all_results.keys()),
            "results": {mk: {str(f): r for f, r in mr.items()}
                        for mk, mr in all_results.items()},
        }, f, indent=2, default=str)
    print(f"\n  💾 {json_path}", file=sys.stderr, flush=True)

    elapsed = time.time() - t_start
    print(f"  Total: {elapsed:.0f}s ({elapsed/60:.1f}min)", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
