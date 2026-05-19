"""Basin Whitened Experiment — decode the universal crystal by cancelling model-specific Q rotation.

Finding from basin_qkv_exp: Q amplifies basin separation WITHIN each model,
but the amplification is model-specific, so cross-model consensus is WEAKER
in Q-space than in hidden-space.

Hypothesis: the model-specific component is a learned covariance structure
(scaling + rotation). Whitening (zero mean, unit spherical covariance)
cancels the model-specific part, revealing the universal crystal underneath.

Test:
  1. Extract raw Q, K, V, hidden vectors from multiple models
  2. Apply per-model whitening to each space
  3. Build RDMs from whitened vectors
  4. Compare basin separation: raw → whitened → cross-model consensus
  5. If whitened-Q consensus > raw-Q consensus → model-specific part decoded
  6. If whitened-Q consensus > hidden consensus → crystal SHARPER in Q after decoding

Also test PCA alignment (project to shared dimensionality) and CKA.

Usage:
    uv run python scripts/v12/basin_whitened_exp.py
    uv run python scripts/v12/basin_whitened_exp.py --models mistral-7b pythia-2.8b

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
    "llama-3-8b":   ("meta-llama/Llama-3.1-8B",       32, 4096),
    "mistral-7b":   ("mistralai/Mistral-7B-v0.3",     32, 4096),
    "olmo-2-13b":   ("allenai/OLMo-2-1124-13B",       40, 5120),
    "olmo-2-7b":    ("allenai/OLMo-2-1124-7B",        32, 4096),
    "pythia-2.8b":  ("EleutherAI/pythia-2.8b-deduped", 32, 2560),
    "pythia-1.4b":  ("EleutherAI/pythia-1.4b-deduped", 24, 2048),
    "smollm3-3b":   ("HuggingFaceTB/SmolLM3-3B",      36, 2560),
}

DEFAULT_MODELS = ["mistral-7b", "pythia-2.8b"]
DEPTH_FRACTIONS = [0.2, 0.5, 0.8]
SKILL_DOMAINS = [
    "lambda", "arithmetic", "coding", "tool", "retrieval",
    "analogy", "reasoning", "narrative", "instruction",
]
SPACES = ["hidden", "Q", "K", "V"]


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


def extract_raw_vectors(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[float, dict[str, np.ndarray]]:
    """Extract raw hidden, Q, K, V vectors (not RDMs) from one model.
    
    Returns: {depth_frac: {"hidden": (n_probes, d), "Q": (n_probes, d_q), ...}}
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model = MODELS[model_key]
    target_layers = []
    frac_to_layer = {}
    for frac in depth_fractions:
        layer = min(int(round(frac * (n_layers - 1))), n_layers - 1)
        if layer not in [l for l, _ in target_layers]:
            target_layers.append((layer, frac))
            frac_to_layer[frac] = layer

    print(f"\n  ─── {model_key} ({model_name}) ───", file=sys.stderr, flush=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device, trust_remote_code=True,
    )
    model.eval()

    # Find architecture
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
        get_attn = lambda l: l.self_attn
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
        get_attn = lambda l: l.attention
    else:
        raise ValueError(f"Unknown architecture for {model_key}")

    test_attn = get_attn(layers[0])
    is_fused = hasattr(test_attn, 'query_key_value')
    print(f"  QKV: {'fused' if is_fused else 'separate'}, d_model={d_model}",
          file=sys.stderr, flush=True)

    captures: dict[int, dict[str, list]] = {}
    hooks = []

    for layer_idx, frac in target_layers:
        captures[layer_idx] = {"hidden": [], "Q": [], "K": [], "V": []}
        layer_mod = layers[layer_idx]
        attn_mod = get_attn(layer_mod)

        # Hidden state hook
        def make_hidden_hook(li):
            def hook_fn(module, input, output):
                h = output[0] if isinstance(output, tuple) else output
                captures[li]["hidden"].append(h[:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(layer_mod.register_forward_hook(make_hidden_hook(layer_idx)))

        if is_fused:
            fused = attn_mod.query_key_value
            out_features = fused.weight.shape[0]
            if out_features == 3 * d_model:
                q_size = k_size = v_size = d_model
            else:
                q_size = d_model
                k_size = v_size = (out_features - d_model) // 2

            def make_fused_hook(li, qs, ks, vs):
                def hook_fn(module, input, output):
                    out = output[:, -1, :].detach().cpu().float()
                    captures[li]["Q"].append(out[:, :qs])
                    captures[li]["K"].append(out[:, qs:qs+ks])
                    captures[li]["V"].append(out[:, qs+ks:qs+ks+vs])
                return hook_fn
            hooks.append(fused.register_forward_hook(
                make_fused_hook(layer_idx, q_size, k_size, v_size)))
        else:
            for proj_name, space_name in [('q_proj', 'Q'), ('k_proj', 'K'), ('v_proj', 'V')]:
                proj = getattr(attn_mod, proj_name)
                def make_proj_hook(li, sn):
                    def hook_fn(module, input, output):
                        captures[li][sn].append(output[:, -1, :].detach().cpu().float())
                    return hook_fn
                hooks.append(proj.register_forward_hook(make_proj_hook(layer_idx, space_name)))

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

    import torch as _t

    results = {}
    for layer_idx, frac in target_layers:
        space_vecs = {}
        for space in SPACES:
            vecs = captures[layer_idx][space]
            if vecs:
                mat = _t.cat(vecs, dim=0).numpy()
                space_vecs[space] = mat
                print(f"  L{layer_idx} {space:>6s}: {mat.shape}",
                      file=sys.stderr, flush=True)
        results[frac] = space_vecs

    del model, tokenizer
    gc.collect()
    try:
        if _t.backends.mps.is_available():
            _t.mps.empty_cache()
        elif _t.cuda.is_available():
            _t.cuda.empty_cache()
    except Exception:
        pass

    return results


# ══════════════════════════════════════════════════════════════════════
# Whitening and alignment transforms
# ══════════════════════════════════════════════════════════════════════

def whiten(X: np.ndarray, reg: float = 1e-6) -> np.ndarray:
    """ZCA whitening: zero mean, unit spherical covariance.
    
    X: (n_probes, d)
    Returns: (n_probes, d) whitened
    """
    X_centered = X - X.mean(axis=0, keepdims=True)
    cov = X_centered.T @ X_centered / X_centered.shape[0]
    U, S, Vt = np.linalg.svd(cov, full_matrices=False)
    # Truncate to remove near-zero singular values
    k = np.sum(S > reg * S[0])
    W = U[:, :k] @ np.diag(1.0 / np.sqrt(S[:k] + reg)) @ U[:, :k].T
    return X_centered @ W


def pca_project(X: np.ndarray, n_components: int = 64) -> np.ndarray:
    """PCA projection to fixed dimensionality.
    
    X: (n_probes, d)
    Returns: (n_probes, n_components)
    """
    X_centered = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    k = min(n_components, U.shape[1])
    return U[:, :k] * S[:k]


def whiten_and_pca(X: np.ndarray, n_components: int = 64) -> np.ndarray:
    """Whiten then PCA to fixed dim."""
    X_w = whiten(X)
    return pca_project(X_w, n_components)


def cosine_rdm(X: np.ndarray) -> np.ndarray:
    """Build cosine similarity RDM from vectors."""
    norms = np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-8)
    X_norm = X / norms
    return X_norm @ X_norm.T


def compute_basin_gaps(
    rdm: np.ndarray,
    domain_indices: dict[str, list[int]],
) -> dict[str, dict]:
    """Per-domain basin gap (intra - inter)."""
    domains = [d for d in SKILL_DOMAINS if d in domain_indices]
    gaps = {}
    for d in domains:
        idx = domain_indices[d]
        intra = [float(rdm[i, j]) for ii, i in enumerate(idx)
                 for j in idx[ii+1:]]
        inter = []
        for d2 in domains:
            if d2 == d:
                continue
            for pi in idx:
                for pj in domain_indices[d2]:
                    inter.append(float(rdm[pi, pj]))
        intra_m = float(np.mean(intra)) if intra else 0
        inter_m = float(np.mean(inter)) if inter else 0
        gaps[d] = {"intra": intra_m, "inter": inter_m, "gap": intra_m - inter_m}
    return gaps


def cross_model_rdm_correlation(
    rdm_a: np.ndarray, rdm_b: np.ndarray
) -> float:
    """Correlation between upper-triangular elements of two RDMs."""
    n = rdm_a.shape[0]
    triu = np.triu_indices(n, k=1)
    va = rdm_a[triu]
    vb = rdm_b[triu]
    return float(np.corrcoef(va, vb)[0, 1])


# ══════════════════════════════════════════════════════════════════════
# Main analysis
# ══════════════════════════════════════════════════════════════════════

def analyze(
    all_vectors: dict[str, dict[float, dict[str, np.ndarray]]],
    probes: list[dict],
    pca_dim: int = 64,
) -> dict:
    """Full analysis: raw vs whitened vs PCA-aligned across spaces and models."""
    domain_indices = get_domain_indices(probes)
    model_keys = list(all_vectors.keys())
    depth_fractions = sorted(next(iter(all_vectors.values())).keys())

    transforms = {
        "raw":     lambda X: X,
        "whiten":  lambda X: whiten(X),
        "pca":     lambda X: pca_project(X, pca_dim),
        "w+pca":   lambda X: whiten_and_pca(X, pca_dim),
    }

    full_results = {}

    for frac in depth_fractions:
        print(f"\n{'='*90}", file=sys.stderr, flush=True)
        print(f"  DEPTH {frac:.0%}", file=sys.stderr, flush=True)
        print(f"{'='*90}", file=sys.stderr, flush=True)

        depth_results = {}

        for space in SPACES:
            # Check all models have this space
            model_vecs = {}
            for mk in model_keys:
                if frac in all_vectors[mk] and space in all_vectors[mk][frac]:
                    model_vecs[mk] = all_vectors[mk][frac][space]
            if len(model_vecs) < 2:
                continue

            space_results = {}

            for t_name, t_fn in transforms.items():
                # Apply transform to each model's vectors
                transformed = {}
                for mk, vecs in model_vecs.items():
                    try:
                        transformed[mk] = t_fn(vecs)
                    except Exception as e:
                        print(f"  WARNING: {t_name} failed for {mk}/{space}: {e}",
                              file=sys.stderr, flush=True)
                        continue

                if len(transformed) < 2:
                    continue

                # Build per-model RDMs
                model_rdms = {}
                for mk, tvecs in transformed.items():
                    model_rdms[mk] = cosine_rdm(tvecs)

                # Cross-model RDM correlation
                mk_list = list(model_rdms.keys())
                corrs = []
                for i in range(len(mk_list)):
                    for j in range(i+1, len(mk_list)):
                        c = cross_model_rdm_correlation(
                            model_rdms[mk_list[i]], model_rdms[mk_list[j]])
                        corrs.append(c)
                mean_corr = float(np.mean(corrs))

                # Consensus RDM (average of per-model RDMs)
                consensus_rdm = np.mean(list(model_rdms.values()), axis=0)

                # Basin gaps on consensus
                gaps = compute_basin_gaps(consensus_rdm, domain_indices)
                mean_gap = float(np.mean([g["gap"] for g in gaps.values()]))

                # Per-model basin gaps (then average)
                per_model_gaps = []
                for mk, rdm in model_rdms.items():
                    mg = compute_basin_gaps(rdm, domain_indices)
                    per_model_gaps.append(float(np.mean([g["gap"] for g in mg.values()])))
                mean_per_model_gap = float(np.mean(per_model_gaps))

                space_results[t_name] = {
                    "cross_model_corr": mean_corr,
                    "consensus_gap": mean_gap,
                    "per_model_gap": mean_per_model_gap,
                    "per_domain_gaps": {d: g["gap"] for d, g in gaps.items()},
                }

            depth_results[space] = space_results

        # ── Print results ─────────────────────────────────────
        print(f"\n  {'space':>8s}  {'transform':>8s}  {'xmodel_corr':>11s}  "
              f"{'consensus':>10s}  {'per_model':>10s}  {'decoded?':>8s}",
              file=sys.stderr, flush=True)
        print(f"  {'-'*66}", file=sys.stderr, flush=True)

        # Get hidden/raw as baseline
        hidden_raw_gap = None
        hidden_raw_corr = None
        if "hidden" in depth_results and "raw" in depth_results["hidden"]:
            hidden_raw_gap = depth_results["hidden"]["raw"]["consensus_gap"]
            hidden_raw_corr = depth_results["hidden"]["raw"]["cross_model_corr"]

        for space in SPACES:
            if space not in depth_results:
                continue
            for t_name in transforms.keys():
                if t_name not in depth_results[space]:
                    continue
                r = depth_results[space][t_name]
                # Is this "decoded"? Better than hidden/raw consensus?
                decoded = ""
                if hidden_raw_gap is not None:
                    if r["consensus_gap"] > hidden_raw_gap * 1.05:
                        decoded = "★ YES"
                    elif r["consensus_gap"] > hidden_raw_gap:
                        decoded = "~ maybe"

                print(f"  {space:>8s}  {t_name:>8s}  {r['cross_model_corr']:>+11.4f}  "
                      f"{r['consensus_gap']:>+10.4f}  {r['per_model_gap']:>+10.4f}  "
                      f"{decoded:>8s}",
                      file=sys.stderr, flush=True)

        # ── Key comparison: best whitened Q vs raw hidden ─────
        if "Q" in depth_results and "hidden" in depth_results:
            q_results = depth_results["Q"]
            h_raw = depth_results["hidden"].get("raw", {})
            
            best_q_transform = max(
                q_results.keys(),
                key=lambda t: q_results[t].get("consensus_gap", -999)
            )
            best_q = q_results[best_q_transform]

            print(f"\n  ★ CRYSTAL DECODE TEST (depth {frac:.0%}):",
                  file=sys.stderr, flush=True)
            print(f"    Hidden raw:      consensus gap = {h_raw.get('consensus_gap', 0):+.4f}, "
                  f"xmodel corr = {h_raw.get('cross_model_corr', 0):+.4f}",
                  file=sys.stderr, flush=True)
            print(f"    Q {best_q_transform:>8s}:   consensus gap = {best_q['consensus_gap']:+.4f}, "
                  f"xmodel corr = {best_q['cross_model_corr']:+.4f}",
                  file=sys.stderr, flush=True)

            gap_diff = best_q["consensus_gap"] - h_raw.get("consensus_gap", 0)
            corr_diff = best_q["cross_model_corr"] - h_raw.get("cross_model_corr", 0)

            if gap_diff > 0 and corr_diff > 0:
                print(f"    → DECODED: {best_q_transform} Q shows stronger consensus "
                      f"(gap +{gap_diff:.4f}, corr +{corr_diff:.4f})",
                      file=sys.stderr, flush=True)
                print(f"    → Universal crystal is SHARPER in whitened Q than in hidden state",
                      file=sys.stderr, flush=True)
            elif corr_diff > 0:
                print(f"    → PARTIAL: cross-model correlation improved (+{corr_diff:.4f}) "
                      f"but gap {'improved' if gap_diff > 0 else 'not improved'} ({gap_diff:+.4f})",
                      file=sys.stderr, flush=True)
            else:
                print(f"    → NOT DECODED: {best_q_transform} Q did not improve consensus "
                      f"(gap {gap_diff:+.4f}, corr {corr_diff:+.4f})",
                      file=sys.stderr, flush=True)

            # Also check V (was strongest at 20%)
            if "V" in depth_results:
                v_results = depth_results["V"]
                best_v_transform = max(
                    v_results.keys(),
                    key=lambda t: v_results[t].get("consensus_gap", -999)
                )
                best_v = v_results[best_v_transform]
                print(f"    V {best_v_transform:>8s}:   consensus gap = {best_v['consensus_gap']:+.4f}, "
                      f"xmodel corr = {best_v['cross_model_corr']:+.4f}",
                      file=sys.stderr, flush=True)

            # Per-domain comparison for best transform
            print(f"\n    Per-domain (hidden raw vs Q {best_q_transform}):",
                  file=sys.stderr, flush=True)
            h_domains = h_raw.get("per_domain_gaps", {})
            q_domains = best_q.get("per_domain_gaps", {})
            q_wins = 0
            for d in SKILL_DOMAINS:
                hg = h_domains.get(d, 0)
                qg = q_domains.get(d, 0)
                marker = "★" if qg > hg else " "
                if qg > hg:
                    q_wins += 1
                print(f"      {marker} {d:>12s}: hidden={hg:+.4f}  Q={qg:+.4f}  delta={qg-hg:+.4f}",
                      file=sys.stderr, flush=True)
            print(f"    Q wins {q_wins}/{len(SKILL_DOMAINS)} domains",
                  file=sys.stderr, flush=True)

        full_results[f"{frac:.2f}"] = depth_results

    return full_results


def main():
    parser = argparse.ArgumentParser(description="Basin whitened experiment")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--pca-dim", type=int, default=64)
    parser.add_argument("--output-dir", type=str, default="results/basin-whitened")

    args = parser.parse_args()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  Basin Whitened Experiment — Crystal Decode Test",
          file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print(f"  PCA dim: {args.pca_dim}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t_start = time.time()
    probes = load_probes(args.probes)

    all_vectors: dict[str, dict[float, dict[str, np.ndarray]]] = {}
    for mk in args.models:
        vecs = extract_raw_vectors(mk, probes, DEPTH_FRACTIONS, args.device)
        all_vectors[mk] = vecs

    results = analyze(all_vectors, probes, args.pca_dim)

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "analysis.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    elapsed = time.time() - t_start
    print(f"\n  Total: {elapsed:.0f}s", file=sys.stderr, flush=True)
    print(f"  Output: {output_dir}/", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
