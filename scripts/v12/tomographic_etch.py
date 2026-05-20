"""Tomographic Etch — sweep Q rotations, accumulate all crystal facets.

Single-shot etch reads one PCA view and gets 0.69-0.78. But the crystal
has superpositions — patterns stored at different angles. Sweeping the
Q rotation reads ALL the superposed patterns and etches each one.

Like a CT scan: many projections from different angles → reconstruct
the full structure. Each angle reveals patterns invisible at other angles.

Protocol:
  1. Read both beams at angle 0 (standard PCA)
  2. Rotate Q by δ degrees in PCA space
  3. Read both beams at new angle — reveals different superpositions
  4. Solve for plate direction at this angle
  5. Accumulate direction signals (sign votes + confidence)
  6. Repeat for 360° / δ steps
  7. Final plate: flip where accumulated direction is confident

Usage:
    uv run python scripts/v12/tomographic_etch.py --quick
    uv run python scripts/v12/tomographic_etch.py --n-angles 360
    uv run python scripts/v12/tomographic_etch.py --model qwen3-14b

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
    "pythia-2.8b":  ("EleutherAI/pythia-2.8b-deduped", 32, 2560, 10240),
    "mistral-7b":   ("mistralai/Mistral-7B-v0.3",     32, 4096, 14336),
    "qwen3-14b":    ("Qwen/Qwen3-14B",                40, 5120, 17920),
}

DEPTH_FRACTIONS = [0.1, 0.5, 0.9]  # fewer depths, more angles


def load_probes(probe_path: str | None = None) -> list[dict]:
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json")
    with open(probe_path) as f:
        probes = json.load(f)
    print(f"  Loaded {len(probes)} probes", file=sys.stderr, flush=True)
    return probes


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


def random_rotation_matrix(dim: int, rng: np.random.RandomState) -> np.ndarray:
    """Generate a random rotation matrix via QR decomposition."""
    H = rng.randn(dim, dim)
    Q, R = np.linalg.qr(H)
    # Ensure proper rotation (det = +1)
    Q = Q @ np.diag(np.sign(np.diag(R)))
    return Q


def givens_rotation(dim: int, i: int, j: int, theta: float) -> np.ndarray:
    """Givens rotation in the (i,j) plane by angle theta."""
    G = np.eye(dim)
    c, s = np.cos(theta), np.sin(theta)
    G[i, i] = c
    G[j, j] = c
    G[i, j] = -s
    G[j, i] = s
    return G


def extract_raw_activations(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[float, dict[str, np.ndarray]]:
    """Extract hidden, Q, and up activations (raw, not PCA'd)."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model, d_ffn = MODELS[model_key]

    target_layers = []
    for frac in depth_fractions:
        layer = min(int(round(frac * (n_layers - 1))), n_layers - 1)
        if layer not in [l for l, _ in target_layers]:
            target_layers.append((layer, frac))

    print(f"\n  ─── Extracting: {model_key} ───", file=sys.stderr, flush=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device, trust_remote_code=True,
    )
    model.eval()

    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
        is_fused = False
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
        is_fused = True
    else:
        raise ValueError(f"Unknown arch for {model_key}")

    captures: dict[int, dict[str, list]] = {}
    for li, _ in target_layers:
        captures[li] = {'hidden': [], 'q': [], 'up': []}

    hooks = []
    for layer_idx, frac in target_layers:
        layer_mod = layers[layer_idx]

        def make_h_hook(li):
            def hook_fn(module, input, output):
                captures[li]['hidden'].append(input[0][:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(layer_mod.register_forward_hook(make_h_hook(layer_idx)))

        if is_fused:
            fused = layer_mod.attention.query_key_value
            def make_q_hook(li, qs=d_model):
                def hook_fn(module, input, output):
                    captures[li]['q'].append(output[:, -1, :qs].detach().cpu().float())
                return hook_fn
            hooks.append(fused.register_forward_hook(make_q_hook(layer_idx)))
            up_mod = layer_mod.mlp.dense_h_to_4h
        else:
            q_proj = layer_mod.self_attn.q_proj
            def make_q_hook(li):
                def hook_fn(module, input, output):
                    captures[li]['q'].append(output[:, -1, :].detach().cpu().float())
                return hook_fn
            hooks.append(q_proj.register_forward_hook(make_q_hook(layer_idx)))
            up_mod = getattr(layer_mod.mlp, 'up_proj', None) or layer_mod.mlp.dense_h_to_4h

        def make_up_hook(li):
            def hook_fn(module, input, output):
                captures[li]['up'].append(output[:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(up_mod.register_forward_hook(make_up_hook(layer_idx)))

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

    results = {}
    for layer_idx, frac in target_layers:
        import torch as _t
        results[frac] = {
            'hidden': _t.cat(captures[layer_idx]['hidden'], dim=0).numpy(),
            'q_raw': _t.cat(captures[layer_idx]['q'], dim=0).numpy(),
            'up_raw': _t.cat(captures[layer_idx]['up'], dim=0).numpy(),
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


def tomographic_etch(
    hidden: np.ndarray,    # (n_probes, d_model)
    q_raw: np.ndarray,     # (n_probes, d_q)
    up_raw: np.ndarray,    # (n_probes, d_ffn)
    pca_dim: int = 64,
    n_angles: int = 36,
    seed: int = 42,
) -> dict:
    """Tomographic etch: sweep rotations, accumulate direction signals.

    At each angle:
      1. Rotate PCA basis for Q and up
      2. Compute rotated crystal scores
      3. Solve: hidden @ direction ≈ rotated_scores
      4. Accumulate sign(direction) weighted by |direction|

    After all angles: plate = sign(accumulated_directions)
    """
    n_probes, d_model = hidden.shape
    rng = np.random.RandomState(seed)

    # ── Ground truth PCA (angle 0) ──
    q_mean = q_raw.mean(axis=0)
    q_centered = q_raw - q_mean
    U_q, S_q, Vt_q = np.linalg.svd(q_centered, full_matrices=False)
    k_q = min(pca_dim, U_q.shape[1])
    q_loadings = Vt_q[:k_q]  # (k_q, d_q)
    q_scores_0 = U_q[:, :k_q] * S_q[:k_q]

    up_mean = up_raw.mean(axis=0)
    up_centered = up_raw - up_mean
    U_up, S_up, Vt_up = np.linalg.svd(up_centered, full_matrices=False)
    k_up = min(pca_dim, U_up.shape[1])
    up_loadings = Vt_up[:k_up]
    up_scores_0 = U_up[:, :k_up] * S_up[:k_up]

    k_total = k_q + k_up

    # Ground truth RDMs
    rdm_q = cosine_rdm(q_scores_0)
    rdm_up = cosine_rdm(up_scores_0)

    # Precompute pseudoinverse of hidden states
    U_h, S_h, Vt_h = np.linalg.svd(hidden, full_matrices=False)
    threshold = S_h[0] * 1e-6
    effective_k = np.sum(S_h > threshold)
    S_inv = np.zeros_like(S_h)
    S_inv[:effective_k] = 1.0 / S_h[:effective_k]
    H_pinv = (Vt_h.T * S_inv) @ U_h.T  # (d_model, n_probes)

    # ── Tomographic accumulation ──
    # Accumulate direction signals across all rotation angles
    direction_sum = np.zeros((d_model, k_total))
    confidence_sum = np.zeros((d_model, k_total))
    n_rounds = 0

    print(f"    Sweeping {n_angles} angles...", file=sys.stderr, flush=True)
    t0 = time.time()

    for angle_idx in range(n_angles):
        # Generate rotation in PCA space
        # For Q: rotate within the k_q-dimensional PCA subspace
        # For up: rotate within the k_up-dimensional PCA subspace
        if angle_idx == 0:
            R_q = np.eye(k_q)
            R_up = np.eye(k_up)
        else:
            # Systematic Givens rotations: sweep through dimension pairs
            # Each angle rotates a different pair by a different amount
            pair_idx = angle_idx % (k_q * (k_q - 1) // 2)
            theta = (angle_idx / n_angles) * np.pi  # 0 to π

            # Map pair_idx to (i, j)
            ii, jj = 0, 1
            count = 0
            for _i in range(k_q):
                for _j in range(_i + 1, k_q):
                    if count == pair_idx:
                        ii, jj = _i, _j
                    count += 1

            R_q = givens_rotation(k_q, ii, jj, theta)

            # Same for up
            pair_idx_up = angle_idx % (k_up * (k_up - 1) // 2)
            ii_up, jj_up = 0, 1
            count = 0
            for _i in range(k_up):
                for _j in range(_i + 1, k_up):
                    if count == pair_idx_up:
                        ii_up, jj_up = _i, _j
                    count += 1

            R_up = givens_rotation(k_up, ii_up, jj_up, theta)

        # Rotated loadings
        q_loadings_rot = R_q @ q_loadings       # (k_q, d_q)
        up_loadings_rot = R_up @ up_loadings     # (k_up, d_ffn)

        # Rotated scores
        q_scores_rot = q_centered @ q_loadings_rot.T    # (n_probes, k_q)
        up_scores_rot = up_centered @ up_loadings_rot.T  # (n_probes, k_up)

        # Combined target for this angle
        target_rot = np.hstack([q_scores_rot, up_scores_rot])  # (n_probes, k_total)

        # Solve: hidden @ direction ≈ target_rot
        direction = H_pinv @ target_rot  # (d_model, k_total)

        # Accumulate sign votes weighted by confidence
        signs = np.sign(direction)
        magnitudes = np.abs(direction)

        direction_sum += signs * magnitudes
        confidence_sum += magnitudes
        n_rounds += 1

        if (angle_idx + 1) % 100 == 0:
            # Intermediate check
            plate_interim = np.sign(direction_sum)
            recon = hidden @ plate_interim
            q_recon = recon[:, :k_q]
            up_recon = recon[:, k_q:]
            q_corr = rdm_correlation(rdm_q, cosine_rdm(q_recon))
            up_corr = rdm_correlation(rdm_up, cosine_rdm(up_recon))
            print(f"      Angle {angle_idx+1}/{n_angles}: Q={q_corr:+.3f}, FFN={up_corr:+.3f}",
                  file=sys.stderr, flush=True)

    dt = time.time() - t0
    print(f"    Sweep done in {dt:.1f}s ({dt/n_angles*1000:.0f}ms/angle)",
          file=sys.stderr, flush=True)

    # ── Final plate: sign of accumulated directions ──
    plate_tomo = np.sign(direction_sum)
    zero_frac = float((plate_tomo == 0).mean())

    # ── Evaluate ──
    recon_tomo = hidden @ plate_tomo
    q_recon_tomo = recon_tomo[:, :k_q]
    up_recon_tomo = recon_tomo[:, k_q:]

    rdm_q_tomo = cosine_rdm(q_recon_tomo)
    rdm_up_tomo = cosine_rdm(up_recon_tomo)

    q_tomo_corr = rdm_correlation(rdm_q, rdm_q_tomo)
    up_tomo_corr = rdm_correlation(rdm_up, rdm_up_tomo)

    # Cross-talk
    q_xtalk = rdm_correlation(rdm_up, rdm_q_tomo)
    up_xtalk = rdm_correlation(rdm_q, rdm_up_tomo)

    # ── Comparison: single-shot etch (angle 0 only) ──
    target_0 = np.hstack([q_scores_0, up_scores_0])
    plate_single = np.sign(H_pinv @ target_0)
    recon_single = hidden @ plate_single
    q_single = rdm_correlation(rdm_q, cosine_rdm(recon_single[:, :k_q]))
    up_single = rdm_correlation(rdm_up, cosine_rdm(recon_single[:, k_q:]))

    # ── Continuous upper bound ──
    plate_continuous = H_pinv @ target_0
    recon_cont = hidden @ plate_continuous
    q_cont = rdm_correlation(rdm_q, cosine_rdm(recon_cont[:, :k_q]))
    up_cont = rdm_correlation(rdm_up, cosine_rdm(recon_cont[:, k_q:]))

    plate_bytes = (d_model * k_total * 2) // 8

    return {
        "d_model": d_model,
        "k_q": k_q,
        "k_up": k_up,
        "k_total": k_total,
        "n_angles": n_angles,
        "n_rounds": n_rounds,
        "plate_bytes": plate_bytes,
        "plate_kb": plate_bytes / 1024,
        "zero_fraction": zero_frac,
        # Continuous upper bound
        "continuous_q": q_cont,
        "continuous_up": up_cont,
        # Single-shot (angle 0 only)
        "single_shot_q": q_single,
        "single_shot_up": up_single,
        # Tomographic (all angles)
        "tomographic_q": q_tomo_corr,
        "tomographic_up": up_tomo_corr,
        # Cross-talk
        "q_crosstalk": q_xtalk,
        "up_crosstalk": up_xtalk,
        # Improvement
        "q_improvement": q_tomo_corr - q_single,
        "up_improvement": up_tomo_corr - up_single,
    }


def main():
    parser = argparse.ArgumentParser(description="Tomographic Etch")
    parser.add_argument("--model", default="pythia-2.8b", choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--pca-dim", type=int, default=64)
    parser.add_argument("--n-angles", type=int, default=360)
    parser.add_argument("--quick", action="store_true",
                        help="Fewer angles (36), Pythia only")
    parser.add_argument("--output-dir", default="results/tomographic-etch")

    args = parser.parse_args()
    model_key = args.model if not args.quick else "pythia-2.8b"
    n_angles = 36 if args.quick else args.n_angles

    print("=" * 90, file=sys.stderr, flush=True)
    print(f"  Tomographic Etch — Sweep Q Rotations, Accumulate All Crystal Facets",
          file=sys.stderr, flush=True)
    print(f"  Model: {model_key}", file=sys.stderr, flush=True)
    print(f"  Angles: {n_angles}", file=sys.stderr, flush=True)
    print(f"  PCA dim: {args.pca_dim}", file=sys.stderr, flush=True)
    print("=" * 90, file=sys.stderr, flush=True)

    t_start = time.time()
    probes = load_probes(args.probes)

    raw_data = extract_raw_activations(model_key, probes, DEPTH_FRACTIONS, args.device)

    results = {}
    for frac in sorted(raw_data.keys()):
        d = raw_data[frac]
        print(f"\n  Depth {frac:.0%}:", file=sys.stderr, flush=True)

        result = tomographic_etch(
            d['hidden'], d['q_raw'], d['up_raw'],
            pca_dim=args.pca_dim,
            n_angles=n_angles,
        )
        results[frac] = result

        print(f"    Continuous: Q={result['continuous_q']:+.3f}, FFN={result['continuous_up']:+.3f}",
              file=sys.stderr, flush=True)
        print(f"    Single-shot: Q={result['single_shot_q']:+.3f}, FFN={result['single_shot_up']:+.3f}",
              file=sys.stderr, flush=True)
        print(f"    Tomographic: Q={result['tomographic_q']:+.3f}, FFN={result['tomographic_up']:+.3f}",
              file=sys.stderr, flush=True)
        print(f"    Δ improvement: Q={result['q_improvement']:+.3f}, FFN={result['up_improvement']:+.3f}",
              file=sys.stderr, flush=True)
        print(f"    Crosstalk: Q→FFN={result['q_crosstalk']:+.3f}, FFN→Q={result['up_crosstalk']:+.3f}",
              file=sys.stderr, flush=True)

    # Summary
    print(f"\n{'='*90}", file=sys.stderr, flush=True)
    print(f"  TOMOGRAPHIC ETCH SUMMARY ({n_angles} angles)", file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)

    print(f"\n  {'depth':>5s}  {'cont_Q':>7s}  {'cont_up':>7s}  "
          f"{'ss_Q':>7s}  {'ss_up':>7s}  "
          f"{'tomo_Q':>7s}  {'tomo_up':>7s}  {'ΔQ':>6s}  {'Δup':>6s}",
          file=sys.stderr, flush=True)
    print(f"  {'─'*70}", file=sys.stderr, flush=True)

    for frac in sorted(results.keys()):
        r = results[frac]
        print(f"  {frac:>5.0%}  {r['continuous_q']:>+7.3f}  {r['continuous_up']:>+7.3f}  "
              f"{r['single_shot_q']:>+7.3f}  {r['single_shot_up']:>+7.3f}  "
              f"{r['tomographic_q']:>+7.3f}  {r['tomographic_up']:>+7.3f}  "
              f"{r['q_improvement']:>+6.3f}  {r['up_improvement']:>+6.3f}",
              file=sys.stderr, flush=True)

    mean_tomo_q = np.mean([r['tomographic_q'] for r in results.values()])
    mean_tomo_up = np.mean([r['tomographic_up'] for r in results.values()])
    mean_ss_q = np.mean([r['single_shot_q'] for r in results.values()])
    mean_ss_up = np.mean([r['single_shot_up'] for r in results.values()])

    print(f"\n  Mean single-shot:  Q={mean_ss_q:+.3f}, FFN={mean_ss_up:+.3f}",
          file=sys.stderr, flush=True)
    print(f"  Mean tomographic:  Q={mean_tomo_q:+.3f}, FFN={mean_tomo_up:+.3f}",
          file=sys.stderr, flush=True)
    print(f"  Mean improvement:  Q={mean_tomo_q-mean_ss_q:+.3f}, FFN={mean_tomo_up-mean_ss_up:+.3f}",
          file=sys.stderr, flush=True)

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"tomo_{model_key}_{n_angles}angles.json"
    with open(json_path, "w") as f:
        json.dump({
            "description": f"Tomographic etch — {n_angles} angle sweep",
            "model": model_key,
            "pca_dim": args.pca_dim,
            "n_angles": n_angles,
            "results": {str(f): r for f, r in results.items()},
        }, f, indent=2, default=str)
    print(f"\n  💾 {json_path}", file=sys.stderr, flush=True)

    elapsed = time.time() - t_start
    print(f"  Total: {elapsed:.0f}s ({elapsed/60:.1f}min)", file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
