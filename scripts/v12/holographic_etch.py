"""Holographic Etch — record both crystals into new ternary plates.

Not compression. Not weight approximation. CRYSTAL RECORDING.

Protocol:
  1. Read beam_Q from teacher: PCA-Q loadings per layer (the attention crystal)
  2. Read beam_up from teacher: PCA-up loadings per layer (the FFN crystal)
  3. The lens: combine both beam readings into unified crystal description
  4. Create new ternary plates with capacity to hold both
  5. Etch: write the combined crystal into the plates
  6. Verify: illuminate plates with each beam, confirm crystal reconstruction

The plates store what the beams SAW, not the weights that produced it.
At inference, beam_Q reads the attention facet, beam_up reads the FFN facet.

Usage:
    uv run python scripts/v12/holographic_etch.py --quick       # Pythia only
    uv run python scripts/v12/holographic_etch.py               # Pythia + Mistral
    uv run python scripts/v12/holographic_etch.py --model qwen3-14b

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

DEPTH_FRACTIONS = [0.1, 0.3, 0.5, 0.7, 0.9]


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


def read_beams(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    pca_dim: int = 64,
    device: str = "mps",
) -> dict[float, dict]:
    """Read both beams from the teacher at each layer.

    Returns {depth: {
        'q_scores': (n_probes, pca_dim),       # what beam_Q sees
        'q_loadings': (pca_dim, d_q),           # the beam_Q lens
        'q_mean': (d_q,),                       # centering
        'up_scores': (n_probes, pca_dim),       # what beam_up sees
        'up_loadings': (pca_dim, d_ffn),        # the beam_up lens
        'up_mean': (d_ffn,),                    # centering
        'hidden': (n_probes, d_model),          # the residual stream
        'rdm_q': (n_probes, n_probes),          # ground truth attention crystal
        'rdm_up': (n_probes, n_probes),         # ground truth FFN crystal
    }}
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model, d_ffn = MODELS[model_key]

    target_layers = []
    for frac in depth_fractions:
        layer = min(int(round(frac * (n_layers - 1))), n_layers - 1)
        if layer not in [l for l, _ in target_layers]:
            target_layers.append((layer, frac))

    print(f"\n  ─── Reading beams: {model_key} ───", file=sys.stderr, flush=True)

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

        # Hidden state
        def make_h_hook(li):
            def hook_fn(module, input, output):
                captures[li]['hidden'].append(input[0][:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(layer_mod.register_forward_hook(make_h_hook(layer_idx)))

        # Q
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

        # up_proj
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

    # PCA each beam's readings
    results = {}
    for layer_idx, frac in target_layers:
        import torch as _t
        hidden = _t.cat(captures[layer_idx]['hidden'], dim=0).numpy()
        q_raw = _t.cat(captures[layer_idx]['q'], dim=0).numpy()
        up_raw = _t.cat(captures[layer_idx]['up'], dim=0).numpy()

        # PCA for beam_Q
        q_mean = q_raw.mean(axis=0)
        q_centered = q_raw - q_mean
        U_q, S_q, Vt_q = np.linalg.svd(q_centered, full_matrices=False)
        k = min(pca_dim, U_q.shape[1])
        q_scores = U_q[:, :k] * S_q[:k]
        q_loadings = Vt_q[:k]  # (k, d_q)

        # PCA for beam_up
        up_mean = up_raw.mean(axis=0)
        up_centered = up_raw - up_mean
        U_up, S_up, Vt_up = np.linalg.svd(up_centered, full_matrices=False)
        k_up = min(pca_dim, U_up.shape[1])
        up_scores = U_up[:, :k_up] * S_up[:k_up]
        up_loadings = Vt_up[:k_up]

        results[frac] = {
            'hidden': hidden,
            'q_scores': q_scores,
            'q_loadings': q_loadings,
            'q_mean': q_mean,
            'q_singular_values': S_q[:k],
            'up_scores': up_scores,
            'up_loadings': up_loadings,
            'up_mean': up_mean,
            'up_singular_values': S_up[:k_up],
            'rdm_q': cosine_rdm(q_scores),
            'rdm_up': cosine_rdm(up_scores),
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


def build_lens_and_etch(beam_data: dict, plate_dim: int = 128) -> dict:
    """Build the lens and etch both crystals into a unified plate.

    The lens:
      1. Takes beam_Q scores (n_probes, k) and beam_up scores (n_probes, k)
      2. These ARE the crystal readings — what the beams saw
      3. Combines into a unified representation
      4. Creates a ternary plate that, when read by each beam, reconstructs the crystal

    The plate is a (d_model, plate_dim) ternary matrix.
    At inference: h @ plate → plate_coords → beam_Q reads first half, beam_up reads second half.
    """
    hidden = beam_data['hidden']          # (n_probes, d_model)
    q_scores = beam_data['q_scores']      # (n_probes, k_q) — the attention crystal
    up_scores = beam_data['up_scores']    # (n_probes, k_up) — the FFN crystal
    rdm_q = beam_data['rdm_q']
    rdm_up = beam_data['rdm_up']

    n_probes, d_model = hidden.shape
    k_q = q_scores.shape[1]
    k_up = up_scores.shape[1]

    # ═══ Step 1: The combined crystal target ═══
    # What the plate needs to encode: both sets of scores concatenated
    # (n_probes, k_q + k_up) — the full crystal reading
    target_scores = np.hstack([q_scores, up_scores])  # (n_probes, k_q + k_up)
    k_total = target_scores.shape[1]

    # ═══ Step 2: Find the d_model directions that best predict the crystal ═══
    # We need: hidden @ plate ≈ target_scores
    # This is a regression: plate = pinv(hidden) @ target_scores
    # But plate must be TERNARY.

    # First, solve the continuous version (optimal linear map)
    # plate_continuous = (H^T H)^{-1} H^T @ target = pinv(H) @ target
    # Use truncated SVD of hidden for numerical stability
    U_h, S_h, Vt_h = np.linalg.svd(hidden, full_matrices=False)
    # Effective rank: use top components where S > threshold
    threshold = S_h[0] * 1e-6
    effective_k = min(plate_dim, np.sum(S_h > threshold))
    print(f"    Effective rank of hidden states: {effective_k} (of {len(S_h)})",
          file=sys.stderr, flush=True)

    # Pseudoinverse via truncated SVD
    S_inv = np.zeros_like(S_h)
    S_inv[:effective_k] = 1.0 / S_h[:effective_k]
    H_pinv = (Vt_h.T * S_inv) @ U_h.T  # (d_model, n_probes)

    # Optimal continuous plate: (d_model, k_total)
    plate_continuous = H_pinv @ target_scores

    # How well does the continuous solution work?
    reconstructed_continuous = hidden @ plate_continuous
    q_recon_cont = reconstructed_continuous[:, :k_q]
    up_recon_cont = reconstructed_continuous[:, k_q:]
    rdm_q_cont = cosine_rdm(q_recon_cont)
    rdm_up_cont = cosine_rdm(up_recon_cont)
    q_cont_corr = rdm_correlation(rdm_q, rdm_q_cont)
    up_cont_corr = rdm_correlation(rdm_up, rdm_up_cont)

    # ═══ Step 3: Ternary etch ═══
    # Ternary quantize the plate
    plate_ternary = np.sign(plate_continuous)  # (d_model, k_total)

    # Read back through ternary plate
    reconstructed_ternary = hidden @ plate_ternary
    q_recon_tern = reconstructed_ternary[:, :k_q]
    up_recon_tern = reconstructed_ternary[:, k_q:]
    rdm_q_tern = cosine_rdm(q_recon_tern)
    rdm_up_tern = cosine_rdm(up_recon_tern)
    q_tern_corr = rdm_correlation(rdm_q, rdm_q_tern)
    up_tern_corr = rdm_correlation(rdm_up, rdm_up_tern)

    # ═══ Step 4: Iterative etch refinement ═══
    # Greedy bit-flip: for each position in the plate, test if flipping improves
    # the combined crystal reconstruction. This is the etch loop.
    plate_refined = plate_ternary.copy()
    best_q_corr = q_tern_corr
    best_up_corr = up_tern_corr
    best_combined = best_q_corr + best_up_corr

    n_flips = 0
    n_tested = 0
    # Sample random positions to flip (full sweep is too expensive)
    n_samples = min(5000, d_model * k_total)
    rng = np.random.RandomState(42)

    for _ in range(n_samples):
        i = rng.randint(0, d_model)
        j = rng.randint(0, k_total)

        old_val = plate_refined[i, j]
        # Try each ternary value
        for new_val in [-1.0, 0.0, 1.0]:
            if new_val == old_val:
                continue
            n_tested += 1

            # Efficient update: only the i-th row of hidden matters
            # reconstructed changes by: hidden[:, i] * (new_val - old_val) in column j
            delta = hidden[:, i] * (new_val - old_val)
            if j < k_q:
                q_recon_trial = q_recon_tern.copy()
                q_recon_trial[:, j] += delta
                rdm_q_trial = cosine_rdm(q_recon_trial)
                q_trial_corr = rdm_correlation(rdm_q, rdm_q_trial)
                up_trial_corr = best_up_corr
            else:
                up_recon_trial = up_recon_tern.copy()
                up_recon_trial[:, j - k_q] += delta
                rdm_up_trial = cosine_rdm(up_recon_trial)
                up_trial_corr = rdm_correlation(rdm_up, rdm_up_trial)
                q_trial_corr = best_q_corr

            combined = q_trial_corr + up_trial_corr
            if combined > best_combined:
                plate_refined[i, j] = new_val
                best_q_corr = q_trial_corr
                best_up_corr = up_trial_corr
                best_combined = combined
                n_flips += 1

                # Update the running reconstruction
                if j < k_q:
                    q_recon_tern = q_recon_trial
                    rdm_q_tern = rdm_q_trial
                else:
                    up_recon_tern = up_recon_trial
                    rdm_up_tern = rdm_up_trial

    q_refined_corr = best_q_corr
    up_refined_corr = best_up_corr

    # ═══ Step 5: Size and metrics ═══
    plate_bytes = (d_model * k_total * 2) // 8
    zero_frac = float((plate_refined == 0).mean())

    # Cross-talk
    rdm_q_final = cosine_rdm(q_recon_tern)
    rdm_up_final = cosine_rdm(up_recon_tern)
    q_crosstalk = rdm_correlation(rdm_up, rdm_q_final)
    up_crosstalk = rdm_correlation(rdm_q, rdm_up_final)

    return {
        "d_model": d_model,
        "k_q": k_q,
        "k_up": k_up,
        "k_total": k_total,
        "effective_rank": int(effective_k),
        "plate_bytes": plate_bytes,
        "plate_kb": plate_bytes / 1024,
        "zero_fraction": zero_frac,
        # Continuous upper bound
        "continuous_q": q_cont_corr,
        "continuous_up": up_cont_corr,
        # Ternary (direct sign)
        "ternary_q": q_tern_corr,
        "ternary_up": up_tern_corr,
        # Refined (greedy bit-flip)
        "refined_q": q_refined_corr,
        "refined_up": up_refined_corr,
        "n_flips": n_flips,
        "n_tested": n_tested,
        # Cross-talk
        "q_crosstalk": q_crosstalk,
        "up_crosstalk": up_crosstalk,
        # The plate itself (for saving)
        "plate": plate_refined,
    }


def main():
    parser = argparse.ArgumentParser(description="Holographic Etch")
    parser.add_argument("--model", default="pythia-2.8b", choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--pca-dim", type=int, default=64)
    parser.add_argument("--quick", action="store_true",
                        help="Use Pythia only, fewer depths")
    parser.add_argument("--output-dir", default="results/holographic-etch")

    args = parser.parse_args()
    model_key = args.model if not args.quick else "pythia-2.8b"

    print("=" * 90, file=sys.stderr, flush=True)
    print(f"  Holographic Etch — Record Both Crystals into New Plates", file=sys.stderr, flush=True)
    print(f"  Model: {model_key}", file=sys.stderr, flush=True)
    print(f"  PCA dim: {args.pca_dim}", file=sys.stderr, flush=True)
    print("=" * 90, file=sys.stderr, flush=True)

    t_start = time.time()
    probes = load_probes(args.probes)

    # Step 1: Read both beams from teacher
    beam_data = read_beams(model_key, probes, DEPTH_FRACTIONS, args.pca_dim, args.device)

    # Step 2+3+4: Build lens and etch at each depth
    print(f"\n  ─── Etching plates ───", file=sys.stderr, flush=True)
    etch_results = {}
    for frac in sorted(beam_data.keys()):
        print(f"\n  Depth {frac:.0%}:", file=sys.stderr, flush=True)
        result = build_lens_and_etch(beam_data[frac])

        # Don't save the plate array in JSON
        plate = result.pop('plate')
        etch_results[frac] = result

        print(f"    Continuous: Q={result['continuous_q']:+.3f}, FFN={result['continuous_up']:+.3f}",
              file=sys.stderr, flush=True)
        print(f"    Ternary:    Q={result['ternary_q']:+.3f}, FFN={result['ternary_up']:+.3f}",
              file=sys.stderr, flush=True)
        print(f"    Refined:    Q={result['refined_q']:+.3f}, FFN={result['refined_up']:+.3f} "
              f"({result['n_flips']} flips / {result['n_tested']} tested)",
              file=sys.stderr, flush=True)
        print(f"    Crosstalk:  Q→FFN={result['q_crosstalk']:+.3f}, FFN→Q={result['up_crosstalk']:+.3f}",
              file=sys.stderr, flush=True)
        print(f"    Size: {result['plate_kb']:.0f} KB  "
              f"(d_model={result['d_model']}, k={result['k_total']})",
              file=sys.stderr, flush=True)

    # Summary
    print(f"\n{'='*90}", file=sys.stderr, flush=True)
    print(f"  HOLOGRAPHIC ETCH SUMMARY", file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)

    print(f"\n  {'depth':>5s}  {'cont_Q':>7s}  {'cont_up':>7s}  "
          f"{'tern_Q':>7s}  {'tern_up':>7s}  "
          f"{'ref_Q':>7s}  {'ref_up':>7s}  {'flips':>6s}  {'size':>6s}",
          file=sys.stderr, flush=True)
    print(f"  {'─'*70}", file=sys.stderr, flush=True)

    for frac in sorted(etch_results.keys()):
        r = etch_results[frac]
        print(f"  {frac:>5.0%}  {r['continuous_q']:>+7.3f}  {r['continuous_up']:>+7.3f}  "
              f"{r['ternary_q']:>+7.3f}  {r['ternary_up']:>+7.3f}  "
              f"{r['refined_q']:>+7.3f}  {r['refined_up']:>+7.3f}  "
              f"{r['n_flips']:>6d}  {r['plate_kb']:>5.0f}K",
              file=sys.stderr, flush=True)

    # Verdict
    mean_ref_q = np.mean([r['refined_q'] for r in etch_results.values()])
    mean_ref_up = np.mean([r['refined_up'] for r in etch_results.values()])
    mean_cont_q = np.mean([r['continuous_q'] for r in etch_results.values()])
    mean_cont_up = np.mean([r['continuous_up'] for r in etch_results.values()])

    print(f"\n  Mean refined:    Q={mean_ref_q:+.3f}, FFN={mean_ref_up:+.3f}", file=sys.stderr, flush=True)
    print(f"  Mean continuous: Q={mean_cont_q:+.3f}, FFN={mean_cont_up:+.3f} (upper bound)",
          file=sys.stderr, flush=True)
    print(f"  Ternary retention: Q={mean_ref_q/max(mean_cont_q,1e-8):.0%}, "
          f"FFN={mean_ref_up/max(mean_cont_up,1e-8):.0%}",
          file=sys.stderr, flush=True)

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"etch_{model_key}.json"
    with open(json_path, "w") as f:
        json.dump({
            "description": "Holographic etch — record crystals into new ternary plates",
            "model": model_key,
            "pca_dim": args.pca_dim,
            "results": {str(f): r for f, r in etch_results.items()},
        }, f, indent=2, default=str)
    print(f"\n  💾 {json_path}", file=sys.stderr, flush=True)

    elapsed = time.time() - t_start
    print(f"  Total: {elapsed:.0f}s ({elapsed/60:.1f}min)", file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
