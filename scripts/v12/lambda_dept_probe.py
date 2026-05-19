"""Lambda Department Probe — use targeted lambda expressions to map FFN departments.

Uses the binding chain probes (precise combinator stimulators) to:
1. Stimulate each combinator in isolation
2. Measure the FFN response pattern (relational, not neuron-level)
3. Build per-combinator FFN signatures
4. Test if combinator transitions (K→B, B→C, C→WHNF) create
   department handoff patterns in the FFN
5. Cross-model: are the relational department signatures universal?

Key insight: the lambda expressions ARE the most precise way to
activate a specific combinator. We're using the lambda compiler
as a surgical probe tool.

Usage:
    uv run python scripts/v12/lambda_dept_probe.py

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
DEPTH_FRACTIONS = [0.1, 0.3, 0.5, 0.7]

# Group binding chain probes by target combinator
COMBINATOR_GROUPS = {
    "I": ["pure/K"],  # λx.x (I combinator anchor)
    "K": ["pure/I"],  # λx.λy.x (K combinator anchor)
    "B": ["pure/B"],
    "C": ["pure/C"],
    "S": ["pure/S"],
    "D": ["pure/D"],
    "W": ["pure/W"],
    "Y": ["pure/Y"],
    "WHNF": ["pure/WHNF"],
}

# Chain probes grouped by primary combinator exercised
CHAIN_GROUPS = {
    "I_chain": ["chain/I_1step", "chain/I_2step", "chain/I_3step"],
    "K_chain": ["chain/K_1step", "chain/K_after_I"],
    "B_chain": ["chain/B_compose_1", "chain/B_compose_2", "chain/B_compose_3",
                "chain/B_compose_prose", "chain/B_K_apply", "chain/B_carry_prose",
                "chain/B_as_threading_prose"],
    "C_chain": ["chain/C_route_1", "chain/C_route_2", "chain/C_route_3",
                "chain/C_route_prose", "chain/C_flip_1", "chain/C_flip_2",
                "chain/C_flip_prose", "chain/C_mechanism_explicit", "chain/C_as_router_prose"],
    "S_chain": ["chain/S_subst_1", "chain/S_carry_and_fork",
                "chain/S_as_fork_prose", "chain/S_to_W"],
    "WHNF_chain": ["chain/whnf_trivial", "chain/whnf_nested",
                   "chain/whnf_lambda", "chain/whnf_partial", "chain/whnf_data",
                   "chain/WHNF_by_exhaustion_prose"],
    "reduce_chain": ["chain/reduce_3step", "chain/reduce_nested_K",
                    "chain/reduce_church2", "chain/reduce_omega_step",
                    "chain/trace_SKK", "chain/trace_church_add"],
    "depth_chain": ["chain/depth1_simple", "chain/depth2_compose",
                   "chain/depth3_nested", "chain/depth4_deep", "chain/depth5_limit"],
}


def load_probes(probe_path=None):
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "binding_chain_probes.json")
    with open(probe_path) as f:
        probes = json.load(f)
    print(f"  Loaded {len(probes)} binding chain probes", file=sys.stderr, flush=True)
    return probes


def group_probes(probes):
    """Map axis labels to probe indices, group by combinator."""
    axis_to_idx = {}
    for i, p in enumerate(probes):
        axis_to_idx[p["axis"]] = i

    groups = {}
    for group_name, axes in {**COMBINATOR_GROUPS, **CHAIN_GROUPS}.items():
        indices = [axis_to_idx[a] for a in axes if a in axis_to_idx]
        if indices:
            groups[group_name] = indices

    print(f"  Probe groups:", file=sys.stderr, flush=True)
    for name, idx in sorted(groups.items()):
        print(f"    {name:>15s}: {len(idx)} probes", file=sys.stderr, flush=True)

    return groups, axis_to_idx


def pca_project(X, k=64):
    X_c = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_c, full_matrices=False)
    k = min(k, U.shape[1])
    return U[:, :k] * S[:k]


def cosine_rdm(X):
    norms = np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-8)
    return (X / norms) @ (X / norms).T


def extract_model(model_key, probes, depth_fractions, device="mps"):
    """Extract Q and FFN activations for binding chain probes."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model = MODELS[model_key]
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
        get_attn = lambda l: l.self_attn
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
        get_attn = lambda l: l.attention
    else:
        raise ValueError("Unknown arch")

    is_fused = hasattr(get_attn(layers[0]), 'query_key_value')
    results = {}

    for li, frac in target_layers:
        captures = {"Q": [], "FFN": []}
        hooks = []
        attn = get_attn(layers[li])

        if is_fused:
            def make_q(qs=d_model):
                def hook(m, inp, out):
                    captures["Q"].append(out[:, -1, :qs].detach().cpu().float())
                return hook
            hooks.append(attn.query_key_value.register_forward_hook(make_q()))
        else:
            def make_q():
                def hook(m, inp, out):
                    captures["Q"].append(out[:, -1, :].detach().cpu().float())
                return hook
            hooks.append(attn.q_proj.register_forward_hook(make_q()))

        mlp = layers[li].mlp if hasattr(layers[li], 'mlp') else None
        if mlp:
            up = getattr(mlp, 'up_proj', None) or getattr(mlp, 'dense_h_to_4h', None)
            if up:
                def make_ffn():
                    def hook(m, inp, out):
                        captures["FFN"].append(out[:, -1, :].detach().cpu().float())
                    return hook
                hooks.append(up.register_forward_hook(make_ffn()))

        for probe in probes:
            ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
            with torch.no_grad():
                _ = model(ids)

        for h in hooks:
            h.remove()

        r = {}
        for k in ["Q", "FFN"]:
            if captures[k]:
                r[k] = torch.cat(captures[k], dim=0).numpy()
        results[frac] = r

    print(f"  Done", file=sys.stderr, flush=True)

    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available(): _t.mps.empty_cache()
    except: pass

    return results


def analyze(all_results, probes, groups):
    """Analyze per-combinator FFN department signatures."""
    model_keys = list(all_results.keys())
    pure_axes = [f"pure/{c}" for c in ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]]
    axis_to_idx = {p["axis"]: i for i, p in enumerate(probes)}
    pure_indices = [axis_to_idx[a] for a in pure_axes if a in axis_to_idx]

    for frac in DEPTH_FRACTIONS:
        print(f"\n{'='*90}", file=sys.stderr, flush=True)
        print(f"  DEPTH {frac:.0%} — Lambda Department Signatures",
              file=sys.stderr, flush=True)
        print(f"{'='*90}", file=sys.stderr, flush=True)

        for mk in model_keys:
            if frac not in all_results[mk]:
                continue
            r = all_results[mk][frac]
            if "Q" not in r or "FFN" not in r:
                continue

            q_vecs = r["Q"]
            ffn_acts = r["FFN"]
            ffn_binary = (ffn_acts > 0).astype(np.float32)

            # PCA-Q for combinator profiles
            q_pca = pca_project(q_vecs, 64)
            q_norms = np.maximum(np.linalg.norm(q_pca, axis=1, keepdims=True), 1e-8)
            q_norm = q_pca / q_norms

            # FFN PCA for department signatures
            ffn_pca = pca_project(ffn_acts, 64)

            # ── Per-group Q and FFN signatures ────────────────
            print(f"\n  {mk}: Group signatures in PCA-Q and PCA-FFN space:",
                  file=sys.stderr, flush=True)
            print(f"  {'group':>15s}  {'n':>3s}  {'Q→pure_cos':>10s}  "
                  f"{'FFN_active%':>11s}  {'Q_coh':>6s}  {'FFN_coh':>7s}",
                  file=sys.stderr, flush=True)
            print(f"  {'-'*58}", file=sys.stderr, flush=True)

            group_q_centroids = {}
            group_ffn_centroids = {}

            for gname, gidx in sorted(groups.items()):
                if len(gidx) == 0:
                    continue

                # Q centroid and coherence
                g_q = q_norm[gidx]
                q_centroid = g_q.mean(axis=0)
                q_coh = float(np.mean([
                    np.dot(g_q[i], g_q[j]) / (np.linalg.norm(g_q[i]) * np.linalg.norm(g_q[j]) + 1e-8)
                    for i in range(len(gidx)) for j in range(i+1, len(gidx))
                ])) if len(gidx) > 1 else 1.0

                # FFN centroid and coherence
                g_ffn = ffn_pca[gidx]
                ffn_centroid = g_ffn.mean(axis=0)
                fn = np.maximum(np.linalg.norm(g_ffn, axis=1, keepdims=True), 1e-8)
                g_ffn_n = g_ffn / fn
                ffn_coh = float(np.mean([
                    np.dot(g_ffn_n[i], g_ffn_n[j])
                    for i in range(len(gidx)) for j in range(i+1, len(gidx))
                ])) if len(gidx) > 1 else 1.0

                # Mean activation rate
                active_pct = float(ffn_binary[gidx].mean())

                # Cosine to nearest pure combinator in Q space
                pure_q = q_norm[pure_indices]
                cos_to_pure = q_centroid @ pure_q.T
                best_pure_idx = np.argmax(cos_to_pure)
                best_pure = pure_axes[best_pure_idx].split("/")[1]
                best_cos = float(cos_to_pure[best_pure_idx])

                group_q_centroids[gname] = q_centroid
                group_ffn_centroids[gname] = ffn_centroid

                print(f"  {gname:>15s}  {len(gidx):>3d}  {best_pure:>4s}({best_cos:+.2f})  "
                      f"{active_pct:>11.3f}  {q_coh:>+6.3f}  {ffn_coh:>+7.3f}",
                      file=sys.stderr, flush=True)

            # ── Cross-group similarity in FFN space ───────────
            gnames = sorted(group_ffn_centroids.keys())
            if len(gnames) > 3:
                print(f"\n  {mk}: FFN department similarity (centroid cosine):",
                      file=sys.stderr, flush=True)

                # Build centroid matrix
                centroids = np.stack([group_ffn_centroids[g] for g in gnames])
                cn = np.maximum(np.linalg.norm(centroids, axis=1, keepdims=True), 1e-8)
                cos_matrix = (centroids / cn) @ (centroids / cn).T

                # Print compact: which groups cluster in FFN space?
                print(f"  {'':>15s}", end='', file=sys.stderr)
                for g in gnames:
                    print(f"  {g[:6]:>6s}", end='', file=sys.stderr)
                print(file=sys.stderr, flush=True)

                for i, gi in enumerate(gnames):
                    print(f"  {gi:>15s}", end='', file=sys.stderr)
                    for j, gj in enumerate(gnames):
                        if i == j:
                            print(f"  {'--':>6s}", end='', file=sys.stderr)
                        else:
                            print(f"  {cos_matrix[i,j]:+.3f}", end='', file=sys.stderr)
                    print(file=sys.stderr, flush=True)

                # Key test: do chain groups cluster with their pure anchors in FFN space?
                print(f"\n  {mk}: Chain → Pure anchor alignment in FFN space:",
                      file=sys.stderr, flush=True)
                chain_pure_pairs = [
                    ("I_chain", "I"), ("K_chain", "K"), ("B_chain", "B"),
                    ("C_chain", "C"), ("S_chain", "S"), ("WHNF_chain", "WHNF"),
                ]
                for chain_name, pure_name in chain_pure_pairs:
                    if chain_name in group_ffn_centroids and pure_name in group_ffn_centroids:
                        c1 = group_ffn_centroids[chain_name]
                        c2 = group_ffn_centroids[pure_name]
                        n1 = np.linalg.norm(c1)
                        n2 = np.linalg.norm(c2)
                        cos = float(np.dot(c1, c2) / (n1 * n2 + 1e-8))

                        # Compare to average cross-group similarity
                        all_cos = cos_matrix[np.triu_indices(len(gnames), k=1)]
                        mean_cos = float(all_cos.mean())

                        aligned = "✓" if cos > mean_cos + 0.1 else "~" if cos > mean_cos else "✗"
                        print(f"    {chain_name:>12s} → {pure_name:<6s}: "
                              f"cos={cos:+.4f} (mean={mean_cos:+.4f}) {aligned}",
                              file=sys.stderr, flush=True)

        # ── Cross-model: do department signatures agree? ──────
        if len(model_keys) >= 2:
            print(f"\n  Cross-model FFN department signature agreement (depth {frac:.0%}):",
                  file=sys.stderr, flush=True)

            # Build per-model FFN RDMs over all probes, compare
            model_ffn_rdms = {}
            for mk in model_keys:
                if frac in all_results[mk] and "FFN" in all_results[mk][frac]:
                    ffn_pca = pca_project(all_results[mk][frac]["FFN"], 64)
                    model_ffn_rdms[mk] = cosine_rdm(ffn_pca)

            if len(model_ffn_rdms) >= 2:
                mks = list(model_ffn_rdms.keys())
                triu = np.triu_indices(model_ffn_rdms[mks[0]].shape[0], k=1)
                for i in range(len(mks)):
                    for j in range(i+1, len(mks)):
                        corr = float(np.corrcoef(
                            model_ffn_rdms[mks[i]][triu],
                            model_ffn_rdms[mks[j]][triu]
                        )[0, 1])
                        print(f"    {mks[i]} ↔ {mks[j]}: FFN RDM corr = {corr:+.4f}",
                              file=sys.stderr, flush=True)


def main():
    parser = argparse.ArgumentParser(description="Lambda Department Probe")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")

    args = parser.parse_args()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  Lambda Department Probe — Surgical Combinator → FFN Mapping",
          file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t0 = time.time()
    probes = load_probes(args.probes)
    groups, axis_to_idx = group_probes(probes)

    all_results = {}
    for mk in args.models:
        all_results[mk] = extract_model(mk, probes, DEPTH_FRACTIONS, args.device)

    analyze(all_results, probes, groups)

    print(f"\n  Total: {time.time()-t0:.0f}s", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
