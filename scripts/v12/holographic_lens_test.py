"""Holographic Lens Test — can one ternary plate encode both crystals?

We proved two beams read two crystals at 0.94+ agreement:
  PCA-Q   reads the attention crystal
  PCA-up  reads the FFN crystal

Both crystals live in the same residual stream (CC=0.10-0.14, nearly
orthogonal). The hypothesis: the hidden state IS a holographic plate
that encodes both crystals simultaneously. Ternary quantization should
preserve both because the two crystal subspaces don't interfere.

The test:
  1. Capture hidden states H at each layer for all probes
  2. Ground truth: Q crystal (H @ W_q → PCA → RDM) and FFN crystal (H @ W_up → PCA → RDM)
  3. The lens: PCA(H, k) → captures shared structure in residual stream
  4. The etch: sign(PCA(H, k)) → ternary plate
  5. Read back: does cosine_rdm(ternary_plate) correlate with BOTH crystal RDMs?
  6. Beam separation: project ternary plate through PCA loadings aligned with Q vs up
  7. Sweep k to find minimum plate dimension
  8. Cross-model agreement on the unified plate

If this works, the entire model is a stack of holographic plates.
One plate per layer. Two beams. All ternary. mmap-able.

Usage:
    uv run python scripts/v12/holographic_lens_test.py --quick    # Pythia only
    uv run python scripts/v12/holographic_lens_test.py            # Pythia + Mistral

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
PLATE_DIMS = [16, 32, 64, 128, 256, 512]


def load_probes(probe_path: str | None = None) -> list[dict]:
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json")
    with open(probe_path) as f:
        probes = json.load(f)
    print(f"  Loaded {len(probes)} probes", file=sys.stderr, flush=True)
    return probes


def pca_project(X: np.ndarray, n_components: int = 64):
    """Returns (scores, loadings, singular_values, explained_variance_ratio)."""
    X_centered = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    k = min(n_components, U.shape[1])
    scores = U[:, :k] * S[:k]  # (n_probes, k)
    loadings = Vt[:k]           # (k, d_original)
    total_var = (S ** 2).sum()
    explained = (S[:k] ** 2).sum() / max(total_var, 1e-10)
    return scores, loadings, S[:k], float(explained)


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


def canonical_correlations(A: np.ndarray, B: np.ndarray, k: int = 10) -> np.ndarray:
    """Canonical correlations between two subspaces (via QR + SVD)."""
    Qa, _ = np.linalg.qr(A.T)  # (d, k_a)
    Qb, _ = np.linalg.qr(B.T)  # (d, k_b)
    _, S, _ = np.linalg.svd(Qa.T @ Qb, full_matrices=False)
    return S[:k]


def extract_all_vectors(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[float, dict[str, np.ndarray]]:
    """Extract hidden states, Q activations, and up_proj activations.

    Returns {depth: {'hidden': (n, d_model), 'q': (n, d_q), 'up': (n, d_ffn)}}.
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
    print(f"  Layers: {[(li, f'{f:.0%}') for li, f in target_layers]}", file=sys.stderr, flush=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device, trust_remote_code=True,
    )
    model.eval()

    # Detect architecture
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
        get_attn = lambda l: l.self_attn
        get_mlp = lambda l: l.mlp
        is_fused = False
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
        get_attn = lambda l: l.attention
        get_mlp = lambda l: l.mlp
        is_fused = True
    else:
        raise ValueError(f"Unknown arch for {model_key}")

    # Storage
    captures: dict[int, dict[str, list]] = {}
    for li, _ in target_layers:
        captures[li] = {'hidden': [], 'q': [], 'up': []}

    hooks = []

    for layer_idx, frac in target_layers:
        layer_mod = layers[layer_idx]
        attn_mod = get_attn(layer_mod)
        mlp_mod = get_mlp(layer_mod)

        # Hook the layer input (hidden state entering this layer)
        def make_layer_hook(li):
            def hook_fn(module, input, output):
                # input[0] is the hidden state
                h = input[0]
                captures[li]['hidden'].append(h[:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(layer_mod.register_forward_hook(make_layer_hook(layer_idx)))

        # Hook Q
        if is_fused:
            fused_mod = attn_mod.query_key_value
            def make_q_hook(li, qs=d_model):
                def hook_fn(module, input, output):
                    captures[li]['q'].append(output[:, -1, :qs].detach().cpu().float())
                return hook_fn
            hooks.append(fused_mod.register_forward_hook(make_q_hook(layer_idx)))
        else:
            q_proj = attn_mod.q_proj
            def make_q_hook(li):
                def hook_fn(module, input, output):
                    captures[li]['q'].append(output[:, -1, :].detach().cpu().float())
                return hook_fn
            hooks.append(q_proj.register_forward_hook(make_q_hook(layer_idx)))

        # Hook up_proj
        if hasattr(mlp_mod, 'gate_proj'):
            up_mod = mlp_mod.up_proj
        elif hasattr(mlp_mod, 'dense_h_to_4h'):
            up_mod = mlp_mod.dense_h_to_4h
        else:
            raise ValueError(f"Unknown MLP for {model_key}")

        def make_up_hook(li):
            def hook_fn(module, input, output):
                captures[li]['up'].append(output[:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(up_mod.register_forward_hook(make_up_hook(layer_idx)))

    # Forward all probes
    print(f"  Running {len(probes)} probes...", file=sys.stderr, flush=True)
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 50 == 0:
            print(f"    {i+1}/{len(probes)}...", file=sys.stderr, flush=True)
    dt = time.time() - t0
    print(f"  Done in {dt:.1f}s", file=sys.stderr, flush=True)

    for h in hooks:
        h.remove()

    # Assemble
    results = {}
    for layer_idx, frac in target_layers:
        import torch as _t
        results[frac] = {
            'hidden': _t.cat(captures[layer_idx]['hidden'], dim=0).numpy(),
            'q': _t.cat(captures[layer_idx]['q'], dim=0).numpy(),
            'up': _t.cat(captures[layer_idx]['up'], dim=0).numpy(),
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


def test_holographic_plate(
    hidden: np.ndarray,   # (n_probes, d_model)
    q_acts: np.ndarray,   # (n_probes, d_q)
    up_acts: np.ndarray,  # (n_probes, d_ffn)
    plate_dims: list[int],
    crystal_pca_dim: int = 64,
) -> dict:
    """Test whether a ternary plate from hidden states preserves both crystals.

    Returns metrics for each plate dimension.
    """
    n_probes = hidden.shape[0]

    # ── Ground truth: crystal RDMs from raw activations ──────
    q_pca, q_loadings, q_sv, q_ev = pca_project(q_acts, crystal_pca_dim)
    up_pca, up_loadings, up_sv, up_ev = pca_project(up_acts, crystal_pca_dim)

    rdm_q = cosine_rdm(q_pca)
    rdm_up = cosine_rdm(up_pca)

    # Cross-crystal correlation (should be low — they're different crystals)
    cross_crystal = rdm_correlation(rdm_q, rdm_up)

    # ── Canonical correlations between Q and up PCA subspaces in d_model ──
    # Project PCA loadings back to d_model via the weight matrices?
    # Actually: Q and up activations come from the same hidden state via
    # different projections. The CC between the PCA SCORES tells us how
    # much the probe representations overlap in each crystal.
    cc_scores = canonical_correlations(q_pca, up_pca, k=10)

    # ── Ground truth: hidden state RDM ──────
    max_k = min(max(plate_dims), n_probes - 1, hidden.shape[1])
    h_pca_full, h_loadings_full, h_sv, h_ev = pca_project(hidden, max_k)
    actual_dims = h_pca_full.shape[1]  # may be < max_k
    rdm_h_full = cosine_rdm(h_pca_full)

    # How well does the full hidden-state RDM correlate with each crystal?
    h_vs_q_full = rdm_correlation(rdm_q, rdm_h_full)
    h_vs_up_full = rdm_correlation(rdm_up, rdm_h_full)

    # ── Test each plate dimension ──────
    dim_results = []
    for k in plate_dims:
        if k > actual_dims:
            continue

        # The lens: PCA(hidden, k) → captures shared residual stream structure
        h_pca_k = h_pca_full[:, :k]  # reuse the SVD, just truncate

        # The etch: ternary quantization
        h_ternary = np.sign(h_pca_k)  # {-1, 0, +1}

        # Zero fraction (how many positions are exactly 0?)
        zero_frac = float((h_ternary == 0).mean())

        # Read back: RDM of ternary plate
        rdm_ternary = cosine_rdm(h_ternary)

        # Preservation: does the ternary plate encode both crystals?
        attn_preservation = rdm_correlation(rdm_q, rdm_ternary)
        ffn_preservation = rdm_correlation(rdm_up, rdm_ternary)

        # Continuous plate (for comparison — PCA without ternary)
        rdm_continuous = cosine_rdm(h_pca_k)
        attn_continuous = rdm_correlation(rdm_q, rdm_continuous)
        ffn_continuous = rdm_correlation(rdm_up, rdm_continuous)

        # Beam separation test: split PCA dims into Q-aligned vs up-aligned
        # For each PCA dimension, check whether it correlates more with Q or up
        q_dim_corrs = []
        up_dim_corrs = []
        for d in range(k):
            dim_vec = h_pca_k[:, d:d+1]  # (n_probes, 1)
            dim_rdm = cosine_rdm(dim_vec)
            q_dim_corrs.append(rdm_correlation(rdm_q, dim_rdm))
            up_dim_corrs.append(rdm_correlation(rdm_up, dim_rdm))

        q_dim_corrs = np.array(q_dim_corrs)
        up_dim_corrs = np.array(up_dim_corrs)

        # Classify each dim as Q-aligned, up-aligned, or shared
        q_aligned = np.sum(q_dim_corrs > up_dim_corrs + 0.05)
        up_aligned = np.sum(up_dim_corrs > q_dim_corrs + 0.05)
        shared = k - q_aligned - up_aligned

        # Beam-separated read: use only Q-aligned dims for Q, up-aligned for up
        q_mask = q_dim_corrs > up_dim_corrs
        up_mask = ~q_mask

        if q_mask.sum() > 0:
            rdm_q_beam = cosine_rdm(h_ternary[:, q_mask])
            q_beam_preservation = rdm_correlation(rdm_q, rdm_q_beam)
            # Cross-talk: how much FFN crystal leaks into Q beam?
            q_beam_crosstalk = rdm_correlation(rdm_up, rdm_q_beam)
        else:
            q_beam_preservation = 0.0
            q_beam_crosstalk = 0.0

        if up_mask.sum() > 0:
            rdm_up_beam = cosine_rdm(h_ternary[:, up_mask])
            up_beam_preservation = rdm_correlation(rdm_up, rdm_up_beam)
            # Cross-talk: how much attention crystal leaks into up beam?
            up_beam_crosstalk = rdm_correlation(rdm_q, rdm_up_beam)
        else:
            up_beam_preservation = 0.0
            up_beam_crosstalk = 0.0

        # Plate size in bytes (2 bits per ternary value)
        plate_bytes = (n_probes * k * 2) // 8  # 2 bits per value
        # For a model plate (d_model × k), it would be:
        plate_bytes_model = (hidden.shape[1] * k * 2) // 8

        dim_results.append({
            "plate_dim": k,
            "plate_bytes_probes": plate_bytes,
            "plate_bytes_model": plate_bytes_model,
            "zero_fraction": zero_frac,
            # Unified plate (all dims, ternary)
            "attn_preservation_ternary": attn_preservation,
            "ffn_preservation_ternary": ffn_preservation,
            # Unified plate (all dims, continuous — upper bound)
            "attn_preservation_continuous": attn_continuous,
            "ffn_preservation_continuous": ffn_continuous,
            # Beam-separated (ternary)
            "q_beam_preservation": q_beam_preservation,
            "q_beam_crosstalk": q_beam_crosstalk,
            "up_beam_preservation": up_beam_preservation,
            "up_beam_crosstalk": up_beam_crosstalk,
            # Dimension allocation
            "q_aligned_dims": int(q_aligned),
            "up_aligned_dims": int(up_aligned),
            "shared_dims": int(shared),
        })

    return {
        "cross_crystal_correlation": cross_crystal,
        "canonical_correlations_top5": cc_scores[:5].tolist(),
        "hidden_vs_q_full": h_vs_q_full,
        "hidden_vs_up_full": h_vs_up_full,
        "q_explained_var": q_ev,
        "up_explained_var": up_ev,
        "dim_results": dim_results,
    }


def print_results(all_results: dict[str, dict[float, dict]]) -> None:
    """Print holographic lens test results."""
    print(f"\n{'='*110}", file=sys.stderr, flush=True)
    print(f"  HOLOGRAPHIC LENS TEST — Can One Ternary Plate Encode Both Crystals?", file=sys.stderr, flush=True)
    print(f"{'='*110}", file=sys.stderr, flush=True)

    for model_key in all_results:
        model_data = all_results[model_key]
        print(f"\n  ╔══ {model_key.upper()} ══╗", file=sys.stderr, flush=True)

        # Cross-crystal and CC summary per depth
        for frac in sorted(model_data.keys()):
            r = model_data[frac]
            cc = r["canonical_correlations_top5"]
            print(f"\n  Depth {frac:.0%}:  cross_crystal={r['cross_crystal_correlation']:+.3f}  "
                  f"hidden→Q={r['hidden_vs_q_full']:+.3f}  hidden→FFN={r['hidden_vs_up_full']:+.3f}  "
                  f"CC_top3=[{cc[0]:.3f}, {cc[1]:.3f}, {cc[2]:.3f}]",
                  file=sys.stderr, flush=True)

        # Main results table
        print(f"\n  {'depth':>5s}  {'k':>4s}  {'plate':>7s}  "
              f"{'attn_t':>6s}  {'ffn_t':>6s}  "
              f"{'attn_c':>6s}  {'ffn_c':>6s}  "
              f"{'q_beam':>6s}  {'q_xtk':>6s}  {'up_bm':>6s}  {'up_xt':>6s}  "
              f"{'q_d':>3s}  {'up_d':>4s}  {'sh':>3s}",
              file=sys.stderr, flush=True)
        print(f"  {'─'*100}", file=sys.stderr, flush=True)

        for frac in sorted(model_data.keys()):
            for dr in model_data[frac]["dim_results"]:
                plate_kb = dr['plate_bytes_model'] / 1024
                print(f"  {frac:>5.0%}  {dr['plate_dim']:>4d}  {plate_kb:>6.0f}K  "
                      f"{dr['attn_preservation_ternary']:>+6.3f}  "
                      f"{dr['ffn_preservation_ternary']:>+6.3f}  "
                      f"{dr['attn_preservation_continuous']:>+6.3f}  "
                      f"{dr['ffn_preservation_continuous']:>+6.3f}  "
                      f"{dr['q_beam_preservation']:>+6.3f}  "
                      f"{dr['q_beam_crosstalk']:>+6.3f}  "
                      f"{dr['up_beam_preservation']:>+6.3f}  "
                      f"{dr['up_beam_crosstalk']:>+6.3f}  "
                      f"{dr['q_aligned_dims']:>3d}  "
                      f"{dr['up_aligned_dims']:>4d}  "
                      f"{dr['shared_dims']:>3d}",
                      file=sys.stderr, flush=True)

    # ── Verdict ──────
    print(f"\n{'='*110}", file=sys.stderr, flush=True)
    print(f"  VERDICT:", file=sys.stderr, flush=True)

    # Collect best results across models and depths
    best_attn = 0
    best_ffn = 0
    best_k = 0
    for model_key in all_results:
        for frac in all_results[model_key]:
            for dr in all_results[model_key][frac]["dim_results"]:
                combined = dr['attn_preservation_ternary'] + dr['ffn_preservation_ternary']
                if combined > best_attn + best_ffn:
                    best_attn = dr['attn_preservation_ternary']
                    best_ffn = dr['ffn_preservation_ternary']
                    best_k = dr['plate_dim']

    print(f"    Best unified plate: k={best_k}, attn={best_attn:+.3f}, ffn={best_ffn:+.3f}",
          file=sys.stderr, flush=True)

    if best_attn >= 0.7 and best_ffn >= 0.7:
        print(f"  ★★★ HOLOGRAPHIC PLATE WORKS — both crystals preserved in one ternary medium",
              file=sys.stderr, flush=True)
    elif best_attn >= 0.5 and best_ffn >= 0.5:
        print(f"  ★★ PARTIAL — both crystals partially readable from unified plate",
              file=sys.stderr, flush=True)
    elif best_attn >= 0.3 or best_ffn >= 0.3:
        print(f"  ★ WEAK — some signal but not strong holographic encoding",
              file=sys.stderr, flush=True)
    else:
        print(f"  ✗ FAILED — ternary plate does not preserve crystal structure",
              file=sys.stderr, flush=True)

    print(f"{'='*110}", file=sys.stderr, flush=True)


def main():
    parser = argparse.ArgumentParser(description="Holographic Lens Test")
    parser.add_argument("--models", nargs="+", default=None, choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--crystal-pca-dim", type=int, default=64)
    parser.add_argument("--output-dir", type=str, default="results/holographic-lens")

    args = parser.parse_args()
    model_keys = args.models or (QUICK_MODELS if args.quick else DEFAULT_MODELS)

    print("=" * 90, file=sys.stderr, flush=True)
    print("  Holographic Lens Test — Unified Ternary Plate for Both Crystals", file=sys.stderr, flush=True)
    print(f"  Models: {model_keys}", file=sys.stderr, flush=True)
    print(f"  Plate dims: {PLATE_DIMS}", file=sys.stderr, flush=True)
    print(f"  Crystal PCA dim: {args.crystal_pca_dim}", file=sys.stderr, flush=True)
    print("=" * 90, file=sys.stderr, flush=True)

    t_start = time.time()
    probes = load_probes(args.probes)

    all_results: dict[str, dict[float, dict]] = {}

    for model_key in model_keys:
        vectors = extract_all_vectors(model_key, probes, DEPTH_FRACTIONS, args.device)

        model_results = {}
        for frac in sorted(vectors.keys()):
            v = vectors[frac]
            print(f"\n  Testing depth {frac:.0%}: H={v['hidden'].shape}, "
                  f"Q={v['q'].shape}, up={v['up'].shape}",
                  file=sys.stderr, flush=True)

            result = test_holographic_plate(
                v['hidden'], v['q'], v['up'],
                PLATE_DIMS, args.crystal_pca_dim,
            )
            model_results[frac] = result

        all_results[model_key] = model_results

    # Print
    print_results(all_results)

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_data = {
        "description": "Holographic lens test — unified ternary plate for both crystals",
        "model_keys": list(all_results.keys()),
        "plate_dims": PLATE_DIMS,
        "crystal_pca_dim": args.crystal_pca_dim,
        "results": {mk: {str(f): r for f, r in model_results.items()}
                    for mk, model_results in all_results.items()},
    }
    json_path = output_dir / "holographic_lens_results.json"
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"\n  💾 {json_path}", file=sys.stderr, flush=True)

    elapsed = time.time() - t_start
    print(f"  Total: {elapsed:.0f}s ({elapsed/60:.1f}min)", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
