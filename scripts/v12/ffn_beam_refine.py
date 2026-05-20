"""FFN Beam Refinement — sharpen the FFN beam with PCA dim sweep + combinator targets.

Follow-up to ffn_beam_search.py which found up_proj beats Q (0.748 vs 0.728).
Two questions:
  1. Does wider PCA (128, 256) improve agreement? (FFN captures only 76-86% at k=64)
  2. What's the 8×8 combinator cosine agreement in FFN space? (direct comparison to PCA-Q's 0.91)

Usage:
    uv run python scripts/v12/ffn_beam_refine.py --quick
    uv run python scripts/v12/ffn_beam_refine.py

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
    "qwen3-14b":    ("Qwen/Qwen3-14B",                40, 5120, 17920),
    "mistral-7b":   ("mistralai/Mistral-7B-v0.3",     32, 4096, 14336),
    "olmo-2-13b":   ("allenai/OLMo-2-1124-13B",       40, 5120, 13824),
    "pythia-2.8b":  ("EleutherAI/pythia-2.8b-deduped", 32, 2560, 10240),
}

DEFAULT_MODELS = ["qwen3-14b", "mistral-7b", "olmo-2-13b", "pythia-2.8b"]
QUICK_MODELS = ["mistral-7b", "pythia-2.8b"]

DEPTH_FRACTIONS = [0.1, 0.3, 0.5, 0.7, 0.9]
PCA_DIMS = [32, 64, 128, 256]

ZONE_DEPTHS = {
    "A": [0.1],
    "B": [0.3, 0.5],
    "C": [0.7, 0.9],
}

COMBINATOR_ORDER = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]


def load_probes(probe_path: str | None = None) -> list[dict]:
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json")
    with open(probe_path) as f:
        probes = json.load(f)
    print(f"  Loaded {len(probes)} probes", file=sys.stderr, flush=True)
    return probes


def find_combinator_indices(probes: list[dict]) -> dict[str, int]:
    """Find probe indices for pure combinator anchors."""
    comb_idx = {}
    for i, p in enumerate(probes):
        if p["axis"].startswith("pure/"):
            comb_name = p["axis"].split("/")[1]
            comb_idx[comb_name] = i
    return comb_idx


def pca_project(X: np.ndarray, n_components: int = 64) -> np.ndarray:
    X_centered = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    k = min(n_components, U.shape[1])
    return U[:, :k] * S[:k]


def pca_explained_variance(X: np.ndarray, n_components: int) -> float:
    X_centered = X - X.mean(axis=0, keepdims=True)
    _, S, _ = np.linalg.svd(X_centered, full_matrices=False)
    total = (S ** 2).sum()
    k = min(n_components, len(S))
    captured = (S[:k] ** 2).sum()
    return float(captured / max(total, 1e-10))


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


def cosine_matrix_8x8(X: np.ndarray, indices: list[int]) -> np.ndarray:
    """Extract 8×8 cosine similarity matrix for combinator anchors."""
    sub = X[indices]
    norms = np.maximum(np.linalg.norm(sub, axis=1, keepdims=True), 1e-8)
    return (sub / norms) @ (sub / norms).T


def find_ffn_parts(layer_mod):
    mlp = getattr(layer_mod, 'mlp', None) or getattr(layer_mod, 'feed_forward', None)
    if mlp is None:
        raise ValueError(f"Cannot find MLP in {type(layer_mod)}")
    if hasattr(mlp, 'gate_proj'):
        return mlp, 'swiglu', {'up_proj': mlp.up_proj}
    elif hasattr(mlp, 'dense_h_to_4h'):
        return mlp, 'gptneox', {'up_proj': mlp.dense_h_to_4h}
    else:
        raise ValueError(f"Unknown MLP architecture: {type(mlp)}")


def extract_vectors(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[str, dict[float, np.ndarray]]:
    """Extract up_proj and Q vectors from one model.

    Returns {'up_proj': {depth: (n_probes, d_ffn)}, 'q_proj': {depth: (n_probes, d_q)}}.
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

    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
        get_attn = lambda l: l.self_attn
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
        get_attn = lambda l: l.attention
    else:
        raise ValueError(f"Unknown arch for {model_key}")

    test_attn = get_attn(layers[0])
    is_fused = hasattr(test_attn, 'query_key_value')

    captures: dict[int, dict[str, list]] = {li: {'up_proj': [], 'q_proj': []} for li, _ in target_layers}
    hooks = []

    for layer_idx, frac in target_layers:
        layer_mod = layers[layer_idx]
        _, _, ffn_mods = find_ffn_parts(layer_mod)
        attn_mod = get_attn(layer_mod)

        # up_proj hook
        def make_up_hook(li):
            def hook_fn(module, input, output):
                captures[li]['up_proj'].append(output[:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(ffn_mods['up_proj'].register_forward_hook(make_up_hook(layer_idx)))

        # Q hook
        if is_fused:
            fused = attn_mod.query_key_value
            def make_q_hook(li, qs=d_model):
                def hook_fn(module, input, output):
                    captures[li]['q_proj'].append(output[:, -1, :qs].detach().cpu().float())
                return hook_fn
            hooks.append(fused.register_forward_hook(make_q_hook(layer_idx)))
        else:
            q_proj = attn_mod.q_proj
            def make_q_hook(li):
                def hook_fn(module, input, output):
                    captures[li]['q_proj'].append(output[:, -1, :].detach().cpu().float())
                return hook_fn
            hooks.append(q_proj.register_forward_hook(make_q_hook(layer_idx)))

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

    results = {'up_proj': {}, 'q_proj': {}}
    for layer_idx, frac in target_layers:
        for key in ['up_proj', 'q_proj']:
            if captures[layer_idx][key]:
                import torch as _torch
                results[key][frac] = _torch.cat(captures[layer_idx][key], dim=0).numpy()

    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available(): _t.mps.empty_cache()
        elif _t.cuda.is_available(): _t.cuda.empty_cache()
    except Exception:
        pass

    return results


def main():
    parser = argparse.ArgumentParser(description="FFN Beam Refinement")
    parser.add_argument("--models", nargs="+", default=None, choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output-dir", type=str, default="results/ffn-beam")

    args = parser.parse_args()
    model_keys = args.models or (QUICK_MODELS if args.quick else DEFAULT_MODELS)

    print("=" * 90, file=sys.stderr, flush=True)
    print("  FFN Beam Refinement — PCA Dim Sweep + 8×8 Combinator Targets", file=sys.stderr, flush=True)
    print(f"  Models: {model_keys}", file=sys.stderr, flush=True)
    print(f"  PCA dims: {PCA_DIMS}", file=sys.stderr, flush=True)
    print("=" * 90, file=sys.stderr, flush=True)

    t_start = time.time()
    probes = load_probes(args.probes)
    comb_idx = find_combinator_indices(probes)
    print(f"  Combinator anchors: {comb_idx}", file=sys.stderr, flush=True)

    # Check we have all 8 combinators (or at least the ones present)
    comb_indices = []
    comb_names = []
    for name in COMBINATOR_ORDER:
        if name in comb_idx:
            comb_indices.append(comb_idx[name])
            comb_names.append(name)
    print(f"  Found {len(comb_names)} combinator anchors: {comb_names}", file=sys.stderr, flush=True)

    # Extract raw vectors from all models (once — then re-PCA at different dims)
    all_raw: dict[str, dict[str, dict[float, np.ndarray]]] = {}
    for mk in model_keys:
        all_raw[mk] = extract_vectors(mk, probes, DEPTH_FRACTIONS, args.device)

    # ═══════════════════════════════════════════════════════════
    # PART 1: PCA Dim Sweep (full-RDM agreement)
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*90}", file=sys.stderr, flush=True)
    print(f"  PART 1: PCA Dimension Sweep — Full-RDM Agreement", file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)

    dim_sweep_results = {}
    for pca_dim in PCA_DIMS:
        for hook in ['q_proj', 'up_proj']:
            key = f"{hook}_k{pca_dim}"

            # Build RDMs per model per depth
            per_model_rdms: dict[str, dict[float, np.ndarray]] = {}
            explained_vars: dict[str, dict[float, float]] = {}

            for mk in model_keys:
                per_model_rdms[mk] = {}
                explained_vars[mk] = {}
                for frac in DEPTH_FRACTIONS:
                    if frac not in all_raw[mk][hook]:
                        continue
                    raw = all_raw[mk][hook][frac]
                    pca = pca_project(raw, pca_dim)
                    rdm = cosine_rdm(pca)
                    per_model_rdms[mk][frac] = rdm
                    explained_vars[mk][frac] = pca_explained_variance(raw, pca_dim)

            # Agreement per depth
            agreement_per_depth = {}
            for frac in DEPTH_FRACTIONS:
                model_rdms = [per_model_rdms[mk][frac] for mk in model_keys
                              if frac in per_model_rdms[mk]]
                if len(model_rdms) < 2:
                    continue
                corrs = []
                for i in range(len(model_rdms)):
                    for j in range(i + 1, len(model_rdms)):
                        corrs.append(rdm_correlation(model_rdms[i], model_rdms[j]))
                agreement_per_depth[frac] = float(np.mean(corrs))

            mean_agr = float(np.mean(list(agreement_per_depth.values()))) if agreement_per_depth else 0
            best_agr = max(agreement_per_depth.values()) if agreement_per_depth else 0
            mean_ev = float(np.mean([v for mk in explained_vars for v in explained_vars[mk].values()]))

            dim_sweep_results[key] = {
                "hook": hook,
                "pca_dim": pca_dim,
                "mean_agreement": mean_agr,
                "best_agreement": best_agr,
                "mean_explained_variance": mean_ev,
                "agreement_per_depth": {f"{f:.1f}": a for f, a in sorted(agreement_per_depth.items())},
            }

    # Print dim sweep
    print(f"\n  {'hook':>10s}  {'k':>4s}  {'mean_agr':>8s}  {'best_agr':>8s}  {'expl_var':>8s}  "
          f"{'d=0.1':>6s}  {'d=0.3':>6s}  {'d=0.5':>6s}  {'d=0.7':>6s}  {'d=0.9':>6s}",
          file=sys.stderr, flush=True)
    print(f"  {'─'*88}", file=sys.stderr, flush=True)
    for key in sorted(dim_sweep_results.keys()):
        r = dim_sweep_results[key]
        agr = r["agreement_per_depth"]
        print(f"  {r['hook']:>10s}  {r['pca_dim']:>4d}  {r['mean_agreement']:>+8.4f}  "
              f"{r['best_agreement']:>+8.4f}  {r['mean_explained_variance']:>8.1%}  "
              f"{agr.get('0.1', 0):>+6.3f}  {agr.get('0.3', 0):>+6.3f}  "
              f"{agr.get('0.5', 0):>+6.3f}  {agr.get('0.7', 0):>+6.3f}  "
              f"{agr.get('0.9', 0):>+6.3f}",
              file=sys.stderr, flush=True)

    # ═══════════════════════════════════════════════════════════
    # PART 2: 8×8 Combinator Cosine Targets (direct PCA-Q comparison)
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*90}", file=sys.stderr, flush=True)
    print(f"  PART 2: 8×8 Combinator Targets — Direct PCA-Q Comparison", file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)

    combinator_results = {}
    for pca_dim in [64, 128]:
        for hook in ['q_proj', 'up_proj']:
            key = f"{hook}_k{pca_dim}_8x8"

            # For each model × depth: PCA project, extract 8×8 cosine
            per_model_matrices: dict[str, dict[float, np.ndarray]] = {}
            for mk in model_keys:
                per_model_matrices[mk] = {}
                for frac in DEPTH_FRACTIONS:
                    if frac not in all_raw[mk][hook]:
                        continue
                    raw = all_raw[mk][hook][frac]
                    pca = pca_project(raw, pca_dim)
                    cos8 = cosine_matrix_8x8(pca, comb_indices)
                    per_model_matrices[mk][frac] = cos8

            # Agreement per depth (on 8×8 upper triangle)
            agreement_per_depth = {}
            consensus_per_depth = {}
            for frac in DEPTH_FRACTIONS:
                mats = [per_model_matrices[mk][frac] for mk in model_keys
                        if frac in per_model_matrices[mk]]
                if len(mats) < 2:
                    continue
                # Agreement: pairwise correlation of upper-tri
                triu = np.triu_indices(len(comb_names), k=1)
                corrs = []
                for i in range(len(mats)):
                    for j in range(i + 1, len(mats)):
                        a, b = mats[i][triu], mats[j][triu]
                        if a.std() > 1e-10 and b.std() > 1e-10:
                            corrs.append(float(np.corrcoef(a, b)[0, 1]))
                agreement_per_depth[frac] = float(np.mean(corrs)) if corrs else 0
                consensus_per_depth[frac] = np.mean(np.stack(mats), axis=0)

            mean_agr = float(np.mean(list(agreement_per_depth.values()))) if agreement_per_depth else 0

            # Zone-averaged consensus matrices
            zone_consensus = {}
            zone_agreement = {}
            for zone_name, zone_depths in ZONE_DEPTHS.items():
                zone_mats = [consensus_per_depth[d] for d in zone_depths if d in consensus_per_depth]
                zone_agrs = [agreement_per_depth[d] for d in zone_depths if d in agreement_per_depth]
                if zone_mats:
                    zone_consensus[zone_name] = np.mean(np.stack(zone_mats), axis=0)
                    zone_agreement[zone_name] = float(np.mean(zone_agrs))

            combinator_results[key] = {
                "hook": hook,
                "pca_dim": pca_dim,
                "mean_agreement": mean_agr,
                "agreement_per_depth": {f"{f:.1f}": a for f, a in sorted(agreement_per_depth.items())},
                "zone_agreement": zone_agreement,
                "zone_consensus": {z: m.tolist() for z, m in zone_consensus.items()},
                "combinator_order": comb_names,
            }

    # Print combinator results
    print(f"\n  {'hook':>10s}  {'k':>4s}  {'mean_8x8':>8s}  {'zone_A':>6s}  {'zone_B':>6s}  {'zone_C':>6s}  "
          f"{'d=0.1':>6s}  {'d=0.3':>6s}  {'d=0.5':>6s}  {'d=0.7':>6s}  {'d=0.9':>6s}",
          file=sys.stderr, flush=True)
    print(f"  {'─'*82}", file=sys.stderr, flush=True)
    for key in sorted(combinator_results.keys()):
        r = combinator_results[key]
        za = r["zone_agreement"]
        agr = r["agreement_per_depth"]
        print(f"  {r['hook']:>10s}  {r['pca_dim']:>4d}  {r['mean_agreement']:>+8.4f}  "
              f"{za.get('A', 0):>+6.3f}  {za.get('B', 0):>+6.3f}  {za.get('C', 0):>+6.3f}  "
              f"{agr.get('0.1', 0):>+6.3f}  {agr.get('0.3', 0):>+6.3f}  "
              f"{agr.get('0.5', 0):>+6.3f}  {agr.get('0.7', 0):>+6.3f}  "
              f"{agr.get('0.9', 0):>+6.3f}",
              file=sys.stderr, flush=True)

    # Print zone C consensus matrix for the best FFN result
    best_ffn_key = max(
        [k for k in combinator_results if 'up_proj' in k],
        key=lambda k: combinator_results[k]['mean_agreement']
    )
    best_q_key = max(
        [k for k in combinator_results if 'q_proj' in k],
        key=lambda k: combinator_results[k]['mean_agreement']
    )

    for label, key in [("Q (attention)", best_q_key), ("up_proj (FFN)", best_ffn_key)]:
        r = combinator_results[key]
        print(f"\n  ═══ {label} — Zone C consensus 8×8 (k={r['pca_dim']}) ═══", file=sys.stderr, flush=True)
        if 'C' in r['zone_consensus']:
            mat = np.array(r['zone_consensus']['C'])
            print(f"  {'':>6s}  " + "  ".join(f"{n:>6s}" for n in comb_names), file=sys.stderr, flush=True)
            for i, name in enumerate(comb_names):
                row = "  ".join(f"{mat[i,j]:>+6.3f}" for j in range(len(comb_names)))
                print(f"  {name:>6s}  {row}", file=sys.stderr, flush=True)

    # ═══════════════════════════════════════════════════════════
    # VERDICT
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'='*90}", file=sys.stderr, flush=True)
    best_ffn_agr = combinator_results[best_ffn_key]['mean_agreement']
    best_q_agr = combinator_results[best_q_key]['mean_agreement']
    print(f"  8×8 COMBINATOR AGREEMENT:", file=sys.stderr, flush=True)
    print(f"    Q (attention):  {best_q_agr:+.4f}  (PCA-Q baseline: 0.91-0.94)", file=sys.stderr, flush=True)
    print(f"    up_proj (FFN):  {best_ffn_agr:+.4f}", file=sys.stderr, flush=True)
    print(f"    Ratio:          {best_ffn_agr/max(best_q_agr, 1e-8):.1%}", file=sys.stderr, flush=True)

    if best_ffn_agr >= 0.85:
        print(f"  ★★★ FFN BEAM CONFIRMED — up_proj reads the FFN crystal at 0.85+", file=sys.stderr, flush=True)
    elif best_ffn_agr >= 0.70:
        print(f"  ★★ STRONG — up_proj partially reads the FFN crystal", file=sys.stderr, flush=True)
    else:
        print(f"  ★ More work needed", file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)

    # Save everything
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_data = {
        "description": "FFN beam refinement — PCA dim sweep + 8×8 combinator targets",
        "model_keys": model_keys,
        "pca_dims": PCA_DIMS,
        "combinator_order": comb_names,
        "dim_sweep": dim_sweep_results,
        "combinator_8x8": combinator_results,
    }
    json_path = output_dir / "ffn_beam_refine.json"
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"\n  💾 {json_path}", file=sys.stderr, flush=True)

    elapsed = time.time() - t_start
    print(f"  Total: {elapsed:.0f}s ({elapsed/60:.1f}min)", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
