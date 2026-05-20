"""Lambda Proof — do the two beams form a lambda term?

If the plate IS a lambda term, then:
  beam_Q  = the binder (λx. ...)
  beam_up = the body   (... M ...)
  dispatch = the combinator (which reduction rule)

The binder and body are NOT independent — they're coupled by the
combinator's reduction rule. Given combinator + binder, body is predicted.

Test hierarchy:
  1. Can combinator profile alone predict beam_up RDM? (baseline: ~40-54%)
  2. Can beam_Q alone predict beam_up RDM? (binding without type label)
  3. Can combinator + beam_Q predict beam_up RDM? (full lambda term)
  4. Is #3 significantly better than #1 or #2 alone?

If #3 >> #1 and #3 >> #2, the two beams form a COUPLED pair (lambda term),
not independent signals.

Usage:
    uv run python scripts/v12/lambda_proof.py --quick
    uv run python scripts/v12/lambda_proof.py

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
}

DEPTH_FRACTIONS = [0.1, 0.3, 0.5, 0.7, 0.9]
COMBINATOR_ORDER = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]


def load_probes(probe_path: str | None = None) -> list[dict]:
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json")
    with open(probe_path) as f:
        probes = json.load(f)
    print(f"  Loaded {len(probes)} probes", file=sys.stderr, flush=True)
    return probes


def find_combinator_indices(probes: list[dict]) -> dict[str, int]:
    comb_idx = {}
    for i, p in enumerate(probes):
        if p["axis"].startswith("pure/"):
            name = p["axis"].split("/")[1]
            comb_idx[name] = i
    return comb_idx


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


def extract_all(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[float, dict[str, np.ndarray]]:
    """Extract Q and up activations."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model, d_ffn = MODELS[model_key]

    target_layers = []
    for frac in depth_fractions:
        layer = min(int(round(frac * (n_layers - 1))), n_layers - 1)
        if layer not in [l for l, _ in target_layers]:
            target_layers.append((layer, frac))

    print(f"\n  ─── {model_key} ───", file=sys.stderr, flush=True)

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
        raise ValueError(f"Unknown arch")

    captures: dict[int, dict[str, list]] = {}
    for li, _ in target_layers:
        captures[li] = {'q': [], 'up': []}

    hooks = []
    for layer_idx, frac in target_layers:
        layer_mod = layers[layer_idx]

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


def compute_combinator_profiles(q_pca: np.ndarray, comb_indices: list[int]) -> np.ndarray:
    """Compute combinator profile for each probe: cosine similarity to each anchor.

    Returns (n_probes, n_combinators) profile matrix.
    """
    # Get anchor vectors
    anchors = q_pca[comb_indices]  # (n_comb, k)
    # Normalize
    a_norms = np.maximum(np.linalg.norm(anchors, axis=1, keepdims=True), 1e-8)
    anchors_norm = anchors / a_norms
    p_norms = np.maximum(np.linalg.norm(q_pca, axis=1, keepdims=True), 1e-8)
    probes_norm = q_pca / p_norms
    # Cosine similarity: (n_probes, n_comb)
    return probes_norm @ anchors_norm.T


def test_lambda_coupling(
    q_raw: np.ndarray,     # (n_probes, d_q)
    up_raw: np.ndarray,    # (n_probes, d_ffn)
    comb_indices: list[int],
    pca_dim: int = 64,
) -> dict:
    """Test whether beam_Q and beam_up are coupled by combinator structure."""
    n_probes = q_raw.shape[0]

    # PCA both beams
    q_pca = pca_project(q_raw, pca_dim)
    up_pca = pca_project(up_raw, pca_dim)

    # Ground truth RDMs
    rdm_q = cosine_rdm(q_pca)
    rdm_up = cosine_rdm(up_pca)

    # ── Test 1: Combinator profile alone → predict FFN RDM ──
    # Combinator profile: cosine of each probe to each combinator anchor in Q space
    comb_profile = compute_combinator_profiles(q_pca, comb_indices)  # (n_probes, 8)
    rdm_comb = cosine_rdm(comb_profile)
    comb_predicts_up = rdm_correlation(rdm_up, rdm_comb)

    # ── Test 2: beam_Q alone → predict FFN RDM ──
    # Direct: RDM similarity between Q and up crystals
    q_predicts_up = rdm_correlation(rdm_up, rdm_q)

    # ── Test 3: Combinator + beam_Q → predict FFN RDM ──
    # Concatenate combinator profile with Q PCA scores
    combined_features = np.hstack([comb_profile, q_pca])  # (n_probes, 8+k)
    rdm_combined = cosine_rdm(combined_features)
    combined_predicts_up = rdm_correlation(rdm_up, rdm_combined)

    # ── Test 4: Linear regression — can we RECONSTRUCT up_pca from q_pca + comb? ──
    # This tests whether beam_Q + dispatch → beam_up via a linear map
    # (which would be the case if they're coupled by a reduction rule)

    # 4a: up from Q only
    from numpy.linalg import lstsq
    q_design = np.hstack([q_pca, np.ones((n_probes, 1))])  # add bias
    coeffs_q, residuals_q, _, _ = lstsq(q_design, up_pca, rcond=None)
    up_predicted_q = q_design @ coeffs_q
    r2_q = 1.0 - np.sum((up_pca - up_predicted_q)**2) / max(np.sum((up_pca - up_pca.mean(0))**2), 1e-10)

    # 4b: up from combinator only
    comb_design = np.hstack([comb_profile, np.ones((n_probes, 1))])
    coeffs_comb, _, _, _ = lstsq(comb_design, up_pca, rcond=None)
    up_predicted_comb = comb_design @ coeffs_comb
    r2_comb = 1.0 - np.sum((up_pca - up_predicted_comb)**2) / max(np.sum((up_pca - up_pca.mean(0))**2), 1e-10)

    # 4c: up from Q + combinator
    full_design = np.hstack([q_pca, comb_profile, np.ones((n_probes, 1))])
    coeffs_full, _, _, _ = lstsq(full_design, up_pca, rcond=None)
    up_predicted_full = full_design @ coeffs_full
    r2_full = 1.0 - np.sum((up_pca - up_predicted_full)**2) / max(np.sum((up_pca - up_pca.mean(0))**2), 1e-10)

    # 4d: RDM of predictions
    rdm_pred_q = cosine_rdm(up_predicted_q)
    rdm_pred_comb = cosine_rdm(up_predicted_comb)
    rdm_pred_full = cosine_rdm(up_predicted_full)

    pred_q_corr = rdm_correlation(rdm_up, rdm_pred_q)
    pred_comb_corr = rdm_correlation(rdm_up, rdm_pred_comb)
    pred_full_corr = rdm_correlation(rdm_up, rdm_pred_full)

    # ── Test 5: Cross-validated RDM prediction ──
    # Leave-one-out: for each probe, predict its up_pca from all others
    n_folds = min(10, n_probes)
    fold_size = n_probes // n_folds
    cv_corrs = []
    rng = np.random.RandomState(42)
    indices = rng.permutation(n_probes)

    for fold in range(n_folds):
        test_idx = indices[fold * fold_size:(fold + 1) * fold_size]
        train_idx = np.setdiff1d(indices, test_idx)

        X_train = full_design[train_idx]
        y_train = up_pca[train_idx]
        X_test = full_design[test_idx]
        y_test = up_pca[test_idx]

        coeffs_cv, _, _, _ = lstsq(X_train, y_train, rcond=None)
        y_pred = X_test @ coeffs_cv

        if len(test_idx) > 2:
            rdm_true = cosine_rdm(y_test)
            rdm_pred = cosine_rdm(y_pred)
            cv_corrs.append(rdm_correlation(rdm_true, rdm_pred))

    cv_mean = float(np.mean(cv_corrs)) if cv_corrs else 0.0

    return {
        # RDM prediction (geometry preservation)
        "comb_predicts_up_rdm": comb_predicts_up,
        "q_predicts_up_rdm": q_predicts_up,
        "combined_predicts_up_rdm": combined_predicts_up,
        # Linear regression R² (reconstruction)
        "r2_q_only": float(r2_q),
        "r2_comb_only": float(r2_comb),
        "r2_q_plus_comb": float(r2_full),
        # RDM of linear predictions
        "pred_rdm_q_only": pred_q_corr,
        "pred_rdm_comb_only": pred_comb_corr,
        "pred_rdm_q_plus_comb": pred_full_corr,
        # Cross-validated
        "cv_rdm_correlation": cv_mean,
        # Coupling strength: how much does adding beam_Q improve over comb alone?
        "coupling_rdm_boost": combined_predicts_up - comb_predicts_up,
        "coupling_r2_boost": float(r2_full - r2_comb),
        "coupling_pred_boost": pred_full_corr - pred_comb_corr,
    }


def main():
    parser = argparse.ArgumentParser(description="Lambda Proof")
    parser.add_argument("--models", nargs="+", default=None, choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--pca-dim", type=int, default=64)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output-dir", default="results/lambda-proof")

    args = parser.parse_args()
    model_keys = args.models or (["pythia-2.8b"] if args.quick else list(MODELS.keys()))

    print("=" * 90, file=sys.stderr, flush=True)
    print("  Lambda Proof — Are the Two Beams a Lambda Term?", file=sys.stderr, flush=True)
    print(f"  Models: {model_keys}", file=sys.stderr, flush=True)
    print("=" * 90, file=sys.stderr, flush=True)

    t_start = time.time()
    probes = load_probes(args.probes)

    comb_idx_map = find_combinator_indices(probes)
    comb_indices = [comb_idx_map[name] for name in COMBINATOR_ORDER if name in comb_idx_map]
    comb_names = [name for name in COMBINATOR_ORDER if name in comb_idx_map]
    print(f"  Combinator anchors: {comb_names} at indices {comb_indices}",
          file=sys.stderr, flush=True)

    all_results = {}
    for mk in model_keys:
        data = extract_all(mk, probes, DEPTH_FRACTIONS, args.device)

        model_results = {}
        for frac in sorted(data.keys()):
            print(f"\n  {mk} depth {frac:.0%}:", file=sys.stderr, flush=True)
            result = test_lambda_coupling(
                data[frac]['q'], data[frac]['up'], comb_indices, args.pca_dim,
            )
            model_results[frac] = result

            print(f"    RDM prediction:  comb={result['comb_predicts_up_rdm']:+.3f}  "
                  f"Q={result['q_predicts_up_rdm']:+.3f}  "
                  f"Q+comb={result['combined_predicts_up_rdm']:+.3f}",
                  file=sys.stderr, flush=True)
            print(f"    R² regression:   comb={result['r2_comb_only']:.3f}  "
                  f"Q={result['r2_q_only']:.3f}  "
                  f"Q+comb={result['r2_q_plus_comb']:.3f}",
                  file=sys.stderr, flush=True)
            print(f"    Pred RDM:        comb={result['pred_rdm_comb_only']:+.3f}  "
                  f"Q={result['pred_rdm_q_only']:+.3f}  "
                  f"Q+comb={result['pred_rdm_q_plus_comb']:+.3f}",
                  file=sys.stderr, flush=True)
            print(f"    CV RDM:          {result['cv_rdm_correlation']:+.3f}",
                  file=sys.stderr, flush=True)
            print(f"    Coupling boost:  RDM={result['coupling_rdm_boost']:+.3f}  "
                  f"R²={result['coupling_r2_boost']:+.3f}  "
                  f"pred={result['coupling_pred_boost']:+.3f}",
                  file=sys.stderr, flush=True)

        all_results[mk] = model_results

    # Summary
    print(f"\n{'='*90}", file=sys.stderr, flush=True)
    print(f"  LAMBDA PROOF SUMMARY", file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)

    print(f"\n  {'model':>12s}  {'depth':>5s}  "
          f"{'comb→up':>7s}  {'Q→up':>6s}  {'Q+c→up':>7s}  "
          f"{'R²_c':>5s}  {'R²_Q':>5s}  {'R²_QC':>6s}  "
          f"{'CV':>6s}  {'boost':>6s}",
          file=sys.stderr, flush=True)
    print(f"  {'─'*80}", file=sys.stderr, flush=True)

    for mk in all_results:
        for frac in sorted(all_results[mk].keys()):
            r = all_results[mk][frac]
            print(f"  {mk:>12s}  {frac:>5.0%}  "
                  f"{r['comb_predicts_up_rdm']:>+7.3f}  {r['q_predicts_up_rdm']:>+6.3f}  "
                  f"{r['combined_predicts_up_rdm']:>+7.3f}  "
                  f"{r['r2_comb_only']:>5.3f}  {r['r2_q_only']:>5.3f}  "
                  f"{r['r2_q_plus_comb']:>6.3f}  "
                  f"{r['cv_rdm_correlation']:>+6.3f}  "
                  f"{r['coupling_r2_boost']:>+6.3f}",
                  file=sys.stderr, flush=True)

    # Verdict
    all_boosts = [r['coupling_r2_boost'] for mk in all_results
                  for r in all_results[mk].values()]
    all_r2_full = [r['r2_q_plus_comb'] for mk in all_results
                   for r in all_results[mk].values()]
    all_pred_full = [r['pred_rdm_q_plus_comb'] for mk in all_results
                     for r in all_results[mk].values()]

    mean_boost = float(np.mean(all_boosts))
    mean_r2 = float(np.mean(all_r2_full))
    mean_pred = float(np.mean(all_pred_full))

    print(f"\n  Mean R²(Q+comb→up): {mean_r2:.3f}", file=sys.stderr, flush=True)
    print(f"  Mean RDM pred:      {mean_pred:+.3f}", file=sys.stderr, flush=True)
    print(f"  Mean coupling boost: {mean_boost:+.3f}", file=sys.stderr, flush=True)

    if mean_r2 >= 0.8:
        print(f"  ★★★ STRONG EVIDENCE — beam_Q + combinator linearly predicts beam_up",
              file=sys.stderr, flush=True)
        print(f"       The two beams ARE a lambda term (binder + body coupled by reduction rule)",
              file=sys.stderr, flush=True)
    elif mean_r2 >= 0.5:
        print(f"  ★★ MODERATE — significant coupling, partial lambda structure",
              file=sys.stderr, flush=True)
    elif mean_boost > 0.05:
        print(f"  ★ WEAK — some coupling, combinator adds information",
              file=sys.stderr, flush=True)
    else:
        print(f"  ✗ NOT PROVEN — beams may be independent signals",
              file=sys.stderr, flush=True)

    print(f"{'='*90}", file=sys.stderr, flush=True)

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "lambda_proof.json"
    with open(json_path, "w") as f:
        json.dump({
            "description": "Lambda proof — are the two beams a coupled lambda term?",
            "models": list(all_results.keys()),
            "combinator_order": comb_names,
            "results": {mk: {str(f): r for f, r in mr.items()}
                        for mk, mr in all_results.items()},
        }, f, indent=2, default=str)
    print(f"\n  💾 {json_path}", file=sys.stderr, flush=True)

    elapsed = time.time() - t_start
    print(f"  Total: {elapsed:.0f}s ({elapsed/60:.1f}min)", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
