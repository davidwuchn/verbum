"""FFN Subspace Alignment — test if crystal subspace = FFN key subspace.

If PCA(Q_vectors) ≈ PCA(W_up rows), the crystal and FFN share the same
addressing basis. This means:
  1. Etch the crystal once → FFN keys are automatically aligned
  2. FFN lookup can be elevated to a kernel function (same subspace)
  3. The FFN "database" (W_down values) can potentially be extracted
     and etched into ternary plates

Tests:
  1. Subspace alignment: PCA(Q) vs PCA(W_up) — canonical correlations
  2. Domain-selective key extraction: W_up rows for selective neurons
  3. Do selective keys live in the crystal subspace?
  4. Value extraction: W_down columns for selective neurons
  5. Cross-model: do different models store keys in the same subspace?

Usage:
    uv run python scripts/v12/ffn_subspace_exp.py
    uv run python scripts/v12/ffn_subspace_exp.py --models mistral-7b pythia-2.8b

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
    "qwen3-14b":    ("Qwen/Qwen3-14B",                40, 5120),
    "mistral-7b":   ("mistralai/Mistral-7B-v0.3",     32, 4096),
    "olmo-2-13b":   ("allenai/OLMo-2-1124-13B",       40, 5120),
    "pythia-2.8b":  ("EleutherAI/pythia-2.8b-deduped", 32, 2560),
}

DEFAULT_MODELS = ["mistral-7b", "pythia-2.8b"]
DEPTH_FRACTIONS = [0.1, 0.3, 0.5, 0.7, 0.9]

SKILL_DOMAINS = [
    "lambda", "arithmetic", "coding", "tool", "retrieval",
    "analogy", "reasoning", "narrative", "instruction",
]


def load_probes(probe_path: str | None = None) -> list[dict]:
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json")
    with open(probe_path) as f:
        probes = json.load(f)
    print(f"  Loaded {len(probes)} probes", file=sys.stderr, flush=True)
    return probes


def get_domain_indices(probes: list[dict]) -> dict[str, list[int]]:
    domain_idx: dict[str, list[int]] = {}
    for i, p in enumerate(probes):
        d = p["axis"].split("/")[0]
        domain_idx.setdefault(d, []).append(i)
    return domain_idx


def canonical_correlations(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Compute canonical correlations between two subspaces.

    A: (n, k1) — basis vectors for subspace 1
    B: (n, k2) — basis vectors for subspace 2

    Returns: array of canonical correlations (cosines of principal angles)
    """
    # QR decomposition for numerical stability
    Qa, _ = np.linalg.qr(A)
    Qb, _ = np.linalg.qr(B)
    k = min(Qa.shape[1], Qb.shape[1])
    Qa = Qa[:, :k]
    Qb = Qb[:, :k]
    # SVD of cross-product
    M = Qa.T @ Qb
    _, S, _ = np.linalg.svd(M)
    return np.clip(S[:k], 0, 1)


def subspace_similarity(A: np.ndarray, B: np.ndarray) -> float:
    """Mean canonical correlation between two subspaces."""
    cc = canonical_correlations(A, B)
    return float(cc.mean()) if len(cc) > 0 else 0.0


def extract_all(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    pca_dim: int = 64,
    device: str = "mps",
) -> dict:
    """Extract Q vectors, W_up weights, W_down weights, and FFN activations."""
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
        layers_list = model.model.layers
        get_attn = lambda l: l.self_attn
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers_list = model.gpt_neox.layers
        get_attn = lambda l: l.attention
    else:
        raise ValueError(f"Unknown arch for {model_key}")

    test_attn = get_attn(layers_list[0])
    is_fused_q = hasattr(test_attn, 'query_key_value')

    results = {}

    for layer_idx, frac in target_layers:
        layer_mod = layers_list[layer_idx]
        attn_mod = get_attn(layer_mod)

        # ── Extract W_up and W_down weights ───────────────────
        mlp = layer_mod.mlp if hasattr(layer_mod, 'mlp') else None
        if mlp is None and hasattr(layer_mod, 'feed_forward'):
            mlp = layer_mod.feed_forward

        w_up = None
        w_down = None
        w_gate = None
        if mlp is not None:
            if hasattr(mlp, 'gate_proj'):  # SwiGLU
                w_up = mlp.up_proj.weight.detach().cpu().float().numpy()    # (d_ffn, d_model)
                w_down = mlp.down_proj.weight.detach().cpu().float().numpy()  # (d_model, d_ffn)
                w_gate = mlp.gate_proj.weight.detach().cpu().float().numpy()  # (d_ffn, d_model)
            elif hasattr(mlp, 'dense_h_to_4h'):  # GPT-NeoX
                w_up = mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()
                w_down = mlp.dense_4h_to_h.weight.detach().cpu().float().numpy()

        d_ffn = w_up.shape[0] if w_up is not None else 0
        print(f"  L{layer_idx} (depth={frac:.0%}): d_model={d_model}, d_ffn={d_ffn}",
              file=sys.stderr, flush=True)

        # ── PCA of W_up rows (FFN key subspace) ──────────────
        w_up_pca_basis = None
        w_up_pca_explained = None
        if w_up is not None:
            # W_up rows are the keys (each row = one neuron's key pattern)
            # PCA to find the key subspace
            w_centered = w_up - w_up.mean(axis=0, keepdims=True)
            U, S, Vt = np.linalg.svd(w_centered, full_matrices=False)
            k = min(pca_dim, Vt.shape[0])
            w_up_pca_basis = Vt[:k].T  # (d_model, k) — basis vectors in d_model space
            explained = (S ** 2) / (S ** 2).sum()
            w_up_pca_explained = explained[:k]
            print(f"    W_up PCA: top-{k} explain {explained[:k].sum():.1%}",
                  file=sys.stderr, flush=True)

        # ── Also extract gate PCA if SwiGLU ───────────────────
        w_gate_pca_basis = None
        if w_gate is not None:
            g_centered = w_gate - w_gate.mean(axis=0, keepdims=True)
            Ug, Sg, Vgt = np.linalg.svd(g_centered, full_matrices=False)
            k = min(pca_dim, Vgt.shape[0])
            w_gate_pca_basis = Vgt[:k].T

        # ── Capture Q vectors via probe forwarding ────────────
        q_captures = []
        ffn_captures = []
        hooks = []

        if is_fused_q:
            fused = attn_mod.query_key_value
            q_size = d_model
            def make_q_hook(qs):
                def hook_fn(module, input, output):
                    q_captures.append(output[:, -1, :qs].detach().cpu().float())
                return hook_fn
            hooks.append(fused.register_forward_hook(make_q_hook(q_size)))
        else:
            q_proj = attn_mod.q_proj
            def make_q_hook():
                def hook_fn(module, input, output):
                    q_captures.append(output[:, -1, :].detach().cpu().float())
                return hook_fn
            hooks.append(q_proj.register_forward_hook(make_q_hook()))

        # FFN activation hook
        if mlp is not None:
            if hasattr(mlp, 'up_proj'):
                def make_ffn_hook():
                    def hook_fn(module, input, output):
                        ffn_captures.append(output[:, -1, :].detach().cpu().float())
                    return hook_fn
                hooks.append(mlp.up_proj.register_forward_hook(make_ffn_hook()))
            elif hasattr(mlp, 'dense_h_to_4h'):
                def make_ffn_hook():
                    def hook_fn(module, input, output):
                        ffn_captures.append(output[:, -1, :].detach().cpu().float())
                    return hook_fn
                hooks.append(mlp.dense_h_to_4h.register_forward_hook(make_ffn_hook()))

        for i, probe in enumerate(probes):
            input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
            with torch.no_grad():
                _ = model(input_ids)

        for h in hooks:
            h.remove()

        q_vecs = torch.cat(q_captures, dim=0).numpy() if q_captures else None
        ffn_acts = torch.cat(ffn_captures, dim=0).numpy() if ffn_captures else None

        # PCA of Q vectors
        q_pca_basis = None
        if q_vecs is not None:
            q_centered = q_vecs - q_vecs.mean(axis=0, keepdims=True)
            Uq, Sq, Vqt = np.linalg.svd(q_centered, full_matrices=False)
            k = min(pca_dim, Vqt.shape[0])
            q_pca_basis = Vqt[:k].T  # (d_q, k)
            q_explained = (Sq ** 2) / (Sq ** 2).sum()
            print(f"    Q PCA: top-{k} explain {q_explained[:k].sum():.1%}",
                  file=sys.stderr, flush=True)

        # FFN binary activations
        ffn_binary = (ffn_acts > 0).astype(np.float32) if ffn_acts is not None else None

        results[frac] = {
            "w_up": w_up,
            "w_down": w_down,
            "w_gate": w_gate,
            "w_up_pca_basis": w_up_pca_basis,
            "w_up_pca_explained": w_up_pca_explained,
            "w_gate_pca_basis": w_gate_pca_basis,
            "q_vecs": q_vecs,
            "q_pca_basis": q_pca_basis,
            "ffn_acts": ffn_acts,
            "ffn_binary": ffn_binary,
            "d_model": d_model,
            "d_ffn": d_ffn,
        }

    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available(): _t.mps.empty_cache()
        elif _t.cuda.is_available(): _t.cuda.empty_cache()
    except Exception: pass

    return results


def analyze_subspace_alignment(
    all_results: dict[str, dict[float, dict]],
    probes: list[dict],
    pca_dim: int = 64,
) -> dict:
    """Measure subspace alignment between PCA(Q) and PCA(W_up)."""
    domain_indices = get_domain_indices(probes)
    model_keys = list(all_results.keys())
    analysis = {}

    for frac in sorted(next(iter(all_results.values())).keys()):
        print(f"\n{'='*90}", file=sys.stderr, flush=True)
        print(f"  DEPTH {frac:.0%} — Subspace Alignment", file=sys.stderr, flush=True)
        print(f"{'='*90}", file=sys.stderr, flush=True)

        depth_analysis = {}

        for mk in model_keys:
            if frac not in all_results[mk]:
                continue
            r = all_results[mk][frac]

            q_basis = r.get("q_pca_basis")
            w_up_basis = r.get("w_up_pca_basis")
            w_gate_basis = r.get("w_gate_pca_basis")

            if q_basis is None or w_up_basis is None:
                continue

            # ── Test 1: Q subspace vs W_up subspace ───────────
            # Need same dimensionality for canonical correlations
            # Q may be d_q, W_up is d_model. For separate Q (Mistral), d_q = d_model
            # For fused (Pythia), d_q = d_model too (we sliced it)
            d_q = q_basis.shape[0]
            d_wup = w_up_basis.shape[0]

            if d_q == d_wup:
                cc = canonical_correlations(q_basis, w_up_basis)
                mean_cc = float(cc.mean())
                top5_cc = cc[:5].tolist()
                print(f"\n  {mk}: Q ↔ W_up subspace alignment:",
                      file=sys.stderr, flush=True)
                print(f"    Mean canonical correlation: {mean_cc:+.4f}",
                      file=sys.stderr, flush=True)
                print(f"    Top-5 canonical correlations: "
                      f"{', '.join(f'{c:.3f}' for c in top5_cc)}",
                      file=sys.stderr, flush=True)

                if mean_cc > 0.7:
                    print(f"    → STRONG ALIGNMENT: crystal subspace ≈ FFN key subspace",
                          file=sys.stderr, flush=True)
                elif mean_cc > 0.4:
                    print(f"    → MODERATE ALIGNMENT: partial overlap",
                          file=sys.stderr, flush=True)
                else:
                    print(f"    → WEAK ALIGNMENT: different subspaces",
                          file=sys.stderr, flush=True)

                depth_analysis[f"q_wup_cc_{mk}"] = {
                    "mean": mean_cc,
                    "top5": top5_cc,
                    "all": cc.tolist(),
                }

                # Also test Q vs W_gate if SwiGLU
                if w_gate_basis is not None and d_q == w_gate_basis.shape[0]:
                    cc_gate = canonical_correlations(q_basis, w_gate_basis)
                    print(f"    Q ↔ W_gate mean CC: {cc_gate.mean():+.4f}",
                          file=sys.stderr, flush=True)
                    depth_analysis[f"q_wgate_cc_{mk}"] = float(cc_gate.mean())
            else:
                print(f"  {mk}: dimension mismatch Q({d_q}) vs W_up({d_wup}), "
                      f"using projection", file=sys.stderr, flush=True)

            # ── Test 2: Domain-selective neuron keys in crystal subspace ──
            ffn_binary = r.get("ffn_binary")
            w_up = r.get("w_up")
            w_down = r.get("w_down")

            if ffn_binary is not None and w_up is not None:
                print(f"\n  {mk}: Domain-selective keys in crystal subspace:",
                      file=sys.stderr, flush=True)
                print(f"  {'domain':>12s}  {'n_selective':>11s}  {'key_in_crystal':>14s}  "
                      f"{'key_outside':>11s}  {'ratio':>6s}",
                      file=sys.stderr, flush=True)
                print(f"  {'-'*60}", file=sys.stderr, flush=True)

                for domain in SKILL_DOMAINS:
                    if domain not in domain_indices or domain == "pure":
                        continue
                    idx = domain_indices[domain]

                    # Find selective neurons for this domain
                    domain_rate = ffn_binary[idx].mean(axis=0)
                    other_idx = [i for d2 in SKILL_DOMAINS if d2 != domain and d2 in domain_indices
                                 for i in domain_indices[d2]]
                    if not other_idx:
                        continue
                    other_rate = ffn_binary[other_idx].mean(axis=0)
                    selectivity = domain_rate - other_rate
                    selective_mask = selectivity > 0.3
                    n_selective = int(selective_mask.sum())

                    if n_selective < 3:
                        print(f"  {domain:>12s}  {n_selective:>11d}  {'(too few)':>14s}",
                              file=sys.stderr, flush=True)
                        continue

                    # Extract keys for selective neurons
                    selective_keys = w_up[selective_mask]  # (n_selective, d_model)

                    # Project selective keys onto crystal subspace
                    # key_in_crystal = selective_keys @ q_basis @ q_basis.T
                    # The fraction of key variance explained by crystal subspace
                    key_projections = selective_keys @ q_basis  # (n_selective, k)
                    key_reconstructed = key_projections @ q_basis.T  # (n_selective, d_model)
                    key_residual = selective_keys - key_reconstructed

                    var_in = np.sum(key_reconstructed ** 2)
                    var_out = np.sum(key_residual ** 2)
                    var_total = var_in + var_out
                    frac_in = var_in / max(var_total, 1e-8)
                    frac_out = var_out / max(var_total, 1e-8)

                    print(f"  {domain:>12s}  {n_selective:>11d}  {frac_in:>14.1%}  "
                          f"{frac_out:>11.1%}  {frac_in/max(frac_out,0.01):>6.1f}x",
                          file=sys.stderr, flush=True)

                    depth_analysis[f"key_in_crystal_{domain}_{mk}"] = float(frac_in)

            # ── Test 3: W_up self-similarity across depths ────
            # (compare W_up PCA bases across layers)

        # ── Cross-model: do models share the same key subspace? ──
        if len(model_keys) >= 2:
            print(f"\n  Cross-model W_up subspace alignment:",
                  file=sys.stderr, flush=True)
            # W_up PCA gives basis in d_model space.
            # Different models have different d_model → can't directly compare.
            # But we CAN compare via the PROBE responses:
            # Project probes through each model's W_up PCA basis → get coefficients
            # Then compare coefficients across models (RDM correlation)

            model_ffn_rdms = {}
            model_q_rdms = {}
            for mk in model_keys:
                if frac not in all_results[mk]:
                    continue
                r = all_results[mk][frac]
                if r.get("ffn_acts") is not None:
                    # PCA of FFN activations
                    ffn_pca = pca_project(r["ffn_acts"], pca_dim)
                    model_ffn_rdms[mk] = cosine_rdm(ffn_pca)
                if r.get("q_vecs") is not None:
                    q_pca = pca_project(r["q_vecs"], pca_dim)
                    model_q_rdms[mk] = cosine_rdm(q_pca)

            if len(model_ffn_rdms) >= 2:
                mk_list = list(model_ffn_rdms.keys())
                for i in range(len(mk_list)):
                    for j in range(i+1, len(mk_list)):
                        ffn_corr = rdm_correlation(
                            model_ffn_rdms[mk_list[i]], model_ffn_rdms[mk_list[j]])
                        q_corr = rdm_correlation(
                            model_q_rdms.get(mk_list[i], np.eye(144)),
                            model_q_rdms.get(mk_list[j], np.eye(144)))
                        print(f"    {mk_list[i]} ↔ {mk_list[j]}: "
                              f"FFN_PCA corr={ffn_corr:+.4f}, Q_PCA corr={q_corr:+.4f}",
                              file=sys.stderr, flush=True)
                        depth_analysis[f"xmodel_ffn_{mk_list[i]}_{mk_list[j]}"] = ffn_corr
                        depth_analysis[f"xmodel_q_{mk_list[i]}_{mk_list[j]}"] = q_corr

        # ── Test 4: Can we extract the "database"? ────────────
        # For each domain, extract the mean value vector (W_down projection)
        for mk in model_keys:
            if frac not in all_results[mk]:
                continue
            r = all_results[mk][frac]
            w_down = r.get("w_down")
            ffn_binary = r.get("ffn_binary")
            if w_down is None or ffn_binary is None:
                continue

            print(f"\n  {mk}: Domain value extraction (W_down for selective neurons):",
                  file=sys.stderr, flush=True)
            print(f"  {'domain':>12s}  {'n_neurons':>9s}  {'value_norm':>10s}  "
                  f"{'value_dims':>10s}",
                  file=sys.stderr, flush=True)
            print(f"  {'-'*46}", file=sys.stderr, flush=True)

            for domain in SKILL_DOMAINS:
                if domain not in domain_indices:
                    continue
                idx = domain_indices[domain]
                domain_rate = ffn_binary[idx].mean(axis=0)
                other_idx = [i for d2 in SKILL_DOMAINS if d2 != domain and d2 in domain_indices
                             for i in domain_indices[d2]]
                if not other_idx:
                    continue
                other_rate = ffn_binary[other_idx].mean(axis=0)
                selective = (domain_rate - other_rate) > 0.3
                n_sel = int(selective.sum())
                if n_sel < 3:
                    continue

                # W_down columns for selective neurons
                # W_down shape: (d_model, d_ffn) for standard, but varies
                if w_down.shape[0] < w_down.shape[1]:
                    # (d_model, d_ffn) — columns are neuron values
                    values = w_down[:, selective]  # (d_model, n_sel)
                else:
                    # (d_ffn, d_model) — rows are neuron values
                    values = w_down[selective, :].T  # (d_model, n_sel)

                mean_value = values.mean(axis=1)  # (d_model,)
                value_norm = float(np.linalg.norm(mean_value))

                # How many dimensions does the value space need?
                if n_sel > 3:
                    U, S, Vt = np.linalg.svd(values.T, full_matrices=False)
                    ev = (S ** 2) / max((S ** 2).sum(), 1e-8)
                    cumvar = np.cumsum(ev)
                    dims_80 = int(np.searchsorted(cumvar, 0.8)) + 1
                else:
                    dims_80 = n_sel

                print(f"  {domain:>12s}  {n_sel:>9d}  {value_norm:>10.4f}  "
                      f"{dims_80:>10d}",
                      file=sys.stderr, flush=True)

            break  # First model only for readability

        analysis[f"{frac:.2f}"] = depth_analysis

    return analysis


def pca_project(X, k=64):
    X_c = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_c, full_matrices=False)
    k = min(k, U.shape[1])
    return U[:, :k] * S[:k]


def cosine_rdm(X):
    norms = np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-8)
    return (X / norms) @ (X / norms).T


def rdm_correlation(a, b):
    n = a.shape[0]
    t = np.triu_indices(n, k=1)
    va, vb = a[t], b[t]
    if np.std(va) < 1e-8 or np.std(vb) < 1e-8:
        return 0.0
    return float(np.corrcoef(va, vb)[0, 1])


def main():
    parser = argparse.ArgumentParser(description="FFN Subspace Alignment")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--pca-dim", type=int, default=64)
    parser.add_argument("--output-dir", type=str, default="results/ffn-subspace")

    args = parser.parse_args()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  FFN Subspace Alignment — Crystal = FFN Keys?", file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print(f"  PCA dim: {args.pca_dim}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t_start = time.time()
    probes = load_probes(args.probes)

    all_results = {}
    for mk in args.models:
        results = extract_all(mk, probes, DEPTH_FRACTIONS, args.pca_dim, args.device)
        all_results[mk] = results

    analysis = analyze_subspace_alignment(all_results, probes, args.pca_dim)

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "analysis.json", "w") as f:
        json.dump(analysis, f, indent=2, default=str)
    print(f"\n  💾 {output_dir}/analysis.json", file=sys.stderr, flush=True)

    elapsed = time.time() - t_start
    print(f"  Total: {elapsed:.0f}s", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
