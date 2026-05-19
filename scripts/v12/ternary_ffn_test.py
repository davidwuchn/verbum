"""Ternary FFN Test — how much teacher FFN survives ternary quantization?

Extract Mistral's FFN weights, SVD-project to d_model=512, ternary
quantize, and measure how much of the original activation pattern
is preserved. This tests the holographic FFN viability.

Pipeline:
  1. Extract W_up from teacher at multiple layers
  2. SVD → project to d_target dimensions (512)
  3. Ternary quantize: sign(projected) with threshold
  4. Run probes through teacher, capture FFN activations
  5. Simulate: what would the ternary version produce?
  6. Compare: cosine between teacher activations and ternary reconstruction

Usage:
    uv run python scripts/v12/ternary_ffn_test.py

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
    "mistral-7b": ("mistralai/Mistral-7B-v0.3", 32, 4096),
    "pythia-2.8b": ("EleutherAI/pythia-2.8b-deduped", 32, 2560),
}

DEFAULT_MODELS = ["mistral-7b", "pythia-2.8b"]
DEPTH_FRACTIONS = [0.1, 0.3, 0.5, 0.7, 0.9]
D_TARGETS = [64, 128, 256, 512]


def load_probes(probe_path=None):
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json")
    with open(probe_path) as f:
        probes = json.load(f)
    print(f"  Loaded {len(probes)} probes", file=sys.stderr, flush=True)
    return probes


def ternary_quantize(W, threshold=0.0):
    """Quantize to {-1, 0, +1}. Elements near zero → 0."""
    if threshold > 0:
        result = np.zeros_like(W)
        result[W > threshold] = 1.0
        result[W < -threshold] = -1.0
        return result
    else:
        return np.sign(W)


def run_test(model_key, probes, depth_fractions, d_targets, device="mps"):
    """Extract FFN weights, ternary-quantize, measure activation preservation."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model = MODELS[model_key]
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

    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
    else:
        raise ValueError("Unknown arch")

    results_per_depth = {}

    for li, frac in target_layers:
        print(f"\n  Layer {li} (depth {frac:.0%}):", file=sys.stderr, flush=True)

        # Extract W_up weights
        mlp = layers[li].mlp if hasattr(layers[li], 'mlp') else layers[li].feed_forward
        if hasattr(mlp, 'up_proj'):
            w_up = mlp.up_proj.weight.detach().cpu().float().numpy()  # (d_ffn, d_model)
        elif hasattr(mlp, 'dense_h_to_4h'):
            w_up = mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()
        else:
            continue

        d_ffn, d_orig = w_up.shape
        print(f"    W_up shape: ({d_ffn}, {d_orig})", file=sys.stderr, flush=True)

        # Capture actual FFN activations from probes
        ffn_captures = []
        hidden_captures = []
        hooks = []

        up_mod = getattr(mlp, 'up_proj', None) or getattr(mlp, 'dense_h_to_4h', None)
        if up_mod:
            def make_ffn_hook():
                def hook(m, inp, out):
                    ffn_captures.append(out[:, -1, :].detach().cpu().float())
                return hook
            hooks.append(up_mod.register_forward_hook(make_ffn_hook()))

        layer_mod = layers[li]
        def make_hidden_hook():
            def hook(m, inp, out):
                h_in = inp[0] if isinstance(inp, tuple) else inp
                hidden_captures.append(h_in[:, -1, :].detach().cpu().float())
            return hook
        hooks.append(layer_mod.register_forward_hook(make_hidden_hook()))

        for probe in probes:
            ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
            with torch.no_grad():
                _ = model(ids)

        for h in hooks:
            h.remove()

        teacher_ffn = torch.cat(ffn_captures, dim=0).numpy()  # (n_probes, d_ffn)
        teacher_hidden = torch.cat(hidden_captures, dim=0).numpy()  # (n_probes, d_orig)

        n_probes = teacher_ffn.shape[0]
        print(f"    Teacher FFN activations: {teacher_ffn.shape}", file=sys.stderr, flush=True)

        # SVD of W_up for dimensionality reduction
        U, S, Vt = np.linalg.svd(w_up, full_matrices=False)
        total_energy = (S ** 2).sum()

        depth_results = {}

        for d_target in d_targets:
            if d_target > d_orig:
                continue

            # Project W_up to d_target dimensions
            # W_up = U @ diag(S) @ Vt
            # Projected: U[:, :k] @ diag(S[:k]) @ Vt[:k, :]
            # But we want W_up in the reduced space:
            # W_up_proj = U[:, :k] @ diag(S[:k])  (d_ffn × k)
            # The input projection: Vt[:k, :] (k × d_orig)

            k = d_target
            svd_energy = (S[:k] ** 2).sum() / total_energy

            # Method 1: Project hidden states, then ternary W_up
            # hidden_proj = teacher_hidden @ Vt[:k, :].T  # (n_probes, k)
            # ternary_w = ternary_quantize(U[:, :k] * S[:k])  # (d_ffn, k)
            # ternary_ffn = hidden_proj @ ternary_w.T  # (n_probes, d_ffn)

            # Input projection matrix
            V_proj = Vt[:k, :].T  # (d_orig, k)
            hidden_proj = teacher_hidden @ V_proj  # (n_probes, k)

            # Full-precision projected FFN
            w_up_proj = U[:, :k] * S[:k]  # (d_ffn, k)
            float_ffn = hidden_proj @ w_up_proj.T  # (n_probes, d_ffn)

            # Ternary quantized projected FFN
            for threshold_name, threshold in [("sign", 0.0), ("thresh_10pct", None), ("thresh_median", None)]:
                if threshold is None:
                    abs_vals = np.abs(w_up_proj)
                    if threshold_name == "thresh_10pct":
                        threshold = np.percentile(abs_vals, 10)
                    elif threshold_name == "thresh_median":
                        threshold = np.median(abs_vals) * 0.1

                ternary_w = ternary_quantize(w_up_proj, threshold)
                ternary_ffn = hidden_proj @ ternary_w.T  # (n_probes, d_ffn)

                # Measure preservation
                # 1. Per-probe cosine between teacher and ternary FFN activations
                t_norms = np.maximum(np.linalg.norm(teacher_ffn, axis=1, keepdims=True), 1e-8)
                r_norms = np.maximum(np.linalg.norm(ternary_ffn, axis=1, keepdims=True), 1e-8)
                per_probe_cos = np.sum(
                    (teacher_ffn / t_norms) * (ternary_ffn / r_norms), axis=1
                )
                mean_cos = float(per_probe_cos.mean())

                # 2. RDM preservation: does the relational pattern survive?
                teacher_rdm = (teacher_ffn / t_norms) @ (teacher_ffn / t_norms).T
                ternary_rdm = (ternary_ffn / r_norms) @ (ternary_ffn / r_norms).T
                triu = np.triu_indices(n_probes, k=1)
                rdm_corr = float(np.corrcoef(teacher_rdm[triu], ternary_rdm[triu])[0, 1])

                # 3. Binary activation pattern preservation
                teacher_binary = (teacher_ffn > 0).astype(float)
                ternary_binary = (ternary_ffn > 0).astype(float)
                binary_agreement = float((teacher_binary == ternary_binary).mean())

                # 4. Sparsity of ternary weights
                sparsity = float((ternary_w == 0).mean())

                # 5. Also compare float-projected (SVD only, no ternary)
                f_norms = np.maximum(np.linalg.norm(float_ffn, axis=1, keepdims=True), 1e-8)
                float_cos = float(np.sum(
                    (teacher_ffn / t_norms) * (float_ffn / f_norms), axis=1
                ).mean())
                float_rdm = (float_ffn / f_norms) @ (float_ffn / f_norms).T
                float_rdm_corr = float(np.corrcoef(teacher_rdm[triu], float_rdm[triu])[0, 1])

                key = f"d{d_target}_{threshold_name}"
                depth_results[key] = {
                    "d_target": d_target,
                    "threshold": threshold_name,
                    "svd_energy": float(svd_energy),
                    "mean_cosine": mean_cos,
                    "rdm_correlation": rdm_corr,
                    "binary_agreement": binary_agreement,
                    "sparsity": sparsity,
                    "float_cosine": float_cos,
                    "float_rdm_corr": float_rdm_corr,
                }

        # Print results for this depth
        print(f"\n    {'config':>20s}  {'SVD%':>5s}  {'cos':>6s}  {'RDM':>6s}  "
              f"{'binary':>6s}  {'sparse':>6s}  {'|float_cos':>10s}  {'float_RDM':>9s}",
              file=sys.stderr, flush=True)
        print(f"    {'-'*76}", file=sys.stderr, flush=True)

        for key in sorted(depth_results.keys()):
            r = depth_results[key]
            print(f"    {key:>20s}  {r['svd_energy']:>4.1%}  {r['mean_cosine']:>+5.3f}  "
                  f"{r['rdm_correlation']:>+5.3f}  {r['binary_agreement']:>5.1%}  "
                  f"{r['sparsity']:>5.1%}  {r['float_cosine']:>+9.3f}  "
                  f"{r['float_rdm_corr']:>+8.3f}",
                  file=sys.stderr, flush=True)

        results_per_depth[f"{frac:.2f}"] = depth_results

    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available(): _t.mps.empty_cache()
    except: pass

    return results_per_depth


def main():
    parser = argparse.ArgumentParser(description="Ternary FFN Test")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--output-dir", type=str, default="results/ternary-ffn")

    args = parser.parse_args()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  Ternary FFN Test — Teacher Quantization Viability", file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print(f"  d_targets: {D_TARGETS}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t0 = time.time()
    probes = load_probes(args.probes)

    all_results = {}
    for mk in args.models:
        all_results[mk] = run_test(mk, probes, DEPTH_FRACTIONS, D_TARGETS, args.device)

    # Summary
    print(f"\n{'='*80}", file=sys.stderr, flush=True)
    print(f"  SUMMARY — Ternary FFN Viability", file=sys.stderr, flush=True)
    print(f"{'='*80}", file=sys.stderr, flush=True)

    for mk in all_results:
        print(f"\n  {mk}:", file=sys.stderr, flush=True)
        print(f"  {'depth':>6s}  {'d_target':>8s}  {'cos':>6s}  {'RDM':>6s}  "
              f"{'binary':>6s}  {'verdict':>10s}",
              file=sys.stderr, flush=True)
        print(f"  {'-'*46}", file=sys.stderr, flush=True)

        for frac_key in sorted(all_results[mk].keys()):
            # Best ternary config at each depth
            best_key = max(
                all_results[mk][frac_key].keys(),
                key=lambda k: all_results[mk][frac_key][k]["rdm_correlation"]
            )
            r = all_results[mk][frac_key][best_key]
            verdict = "★ VIABLE" if r["rdm_correlation"] > 0.5 else "~ partial" if r["rdm_correlation"] > 0.3 else "✗ weak"
            print(f"  {frac_key:>6s}  {best_key:>8s}  {r['mean_cosine']:>+5.3f}  "
                  f"{r['rdm_correlation']:>+5.3f}  {r['binary_agreement']:>5.1%}  "
                  f"{verdict:>10s}",
                  file=sys.stderr, flush=True)

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "analysis.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n  💾 {output_dir}/analysis.json", file=sys.stderr, flush=True)
    print(f"  Total: {time.time()-t0:.0f}s", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
