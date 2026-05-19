"""Combinator→FFN Index Test — do combinators predict which FFN neurons fire?

Hypothesis: the combinator dispatch profile IS the FFN addressing function.
K-heavy dispatch → retrieval neuron population. C-heavy → routing population.
B-heavy → composition population. The lambda compiler indexes the FFN.

Test: for each probe, correlate its combinator profile (PCA-Q similarity to
K, I, B, C, D, Y, W, WHNF anchors) with its FFN activation pattern.

Usage:
    uv run python scripts/v12/combinator_ffn_index_test.py

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
    "mistral-7b":   ("mistralai/Mistral-7B-v0.3",     32, 4096),
    "pythia-2.8b":  ("EleutherAI/pythia-2.8b-deduped", 32, 2560),
}

DEFAULT_MODELS = ["mistral-7b", "pythia-2.8b"]
DEPTH_FRACTIONS = [0.1, 0.3, 0.5, 0.7]
COMBINATOR_ORDER = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]

SKILL_DOMAINS = [
    "lambda", "arithmetic", "coding", "tool", "retrieval",
    "analogy", "reasoning", "narrative", "instruction",
]


def load_probes(probe_path=None):
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json")
    with open(probe_path) as f:
        probes = json.load(f)
    print(f"  Loaded {len(probes)} probes", file=sys.stderr, flush=True)
    return probes


def get_pure_indices(probes):
    pure_idx = {}
    for i, p in enumerate(probes):
        if p["axis"].startswith("pure/"):
            pure_idx[p["axis"].split("/")[1]] = i
    return pure_idx


def get_domain_indices(probes):
    domain_idx = {}
    for i, p in enumerate(probes):
        d = p["axis"].split("/")[0]
        domain_idx.setdefault(d, []).append(i)
    return domain_idx


def pca_project(X, k=64):
    X_c = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_c, full_matrices=False)
    k = min(k, U.shape[1])
    return U[:, :k] * S[:k]


def extract_q_and_ffn(model_key, probes, depth_fractions, device="mps"):
    """Extract Q vectors and FFN activations."""
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
        raise ValueError(f"Unknown arch")

    is_fused = hasattr(get_attn(layers[0]), 'query_key_value')

    captures = {li: {"Q": [], "FFN": []} for li, _ in target_layers}
    hooks = []

    for li, frac in target_layers:
        attn = get_attn(layers[li])
        if is_fused:
            fused = attn.query_key_value
            def make_q(layer_idx, qs=d_model):
                def hook(m, inp, out):
                    captures[layer_idx]["Q"].append(out[:, -1, :qs].detach().cpu().float())
                return hook
            hooks.append(fused.register_forward_hook(make_q(li)))
        else:
            def make_q(layer_idx):
                def hook(m, inp, out):
                    captures[layer_idx]["Q"].append(out[:, -1, :].detach().cpu().float())
                return hook
            hooks.append(attn.q_proj.register_forward_hook(make_q(li)))

        mlp = layers[li].mlp if hasattr(layers[li], 'mlp') else None
        if mlp and hasattr(mlp, 'up_proj'):
            def make_ffn(layer_idx):
                def hook(m, inp, out):
                    captures[layer_idx]["FFN"].append(out[:, -1, :].detach().cpu().float())
                return hook
            hooks.append(mlp.up_proj.register_forward_hook(make_ffn(li)))
        elif mlp and hasattr(mlp, 'dense_h_to_4h'):
            def make_ffn(layer_idx):
                def hook(m, inp, out):
                    captures[layer_idx]["FFN"].append(out[:, -1, :].detach().cpu().float())
                return hook
            hooks.append(mlp.dense_h_to_4h.register_forward_hook(make_ffn(li)))

    print(f"  Running {len(probes)} probes...", file=sys.stderr, flush=True)
    t0 = time.time()
    for i, probe in enumerate(probes):
        ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        with torch.no_grad():
            _ = model(ids)
    print(f"  Done in {time.time()-t0:.1f}s", file=sys.stderr, flush=True)

    for h in hooks:
        h.remove()

    results = {}
    for li, frac in target_layers:
        r = {}
        for k in ["Q", "FFN"]:
            if captures[li][k]:
                r[k] = torch.cat(captures[li][k], dim=0).numpy()
        results[frac] = r

    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available(): _t.mps.empty_cache()
    except: pass

    return results


def analyze(all_results, probes):
    pure_idx = get_pure_indices(probes)
    domain_indices = get_domain_indices(probes)
    model_keys = list(all_results.keys())

    comb_indices = [pure_idx[c] for c in COMBINATOR_ORDER if c in pure_idx]

    for frac in DEPTH_FRACTIONS:
        print(f"\n{'='*90}", file=sys.stderr, flush=True)
        print(f"  DEPTH {frac:.0%} — Combinator Profile → FFN Activation",
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
            n_probes = q_vecs.shape[0]
            n_neurons = ffn_acts.shape[1]

            # PCA-Q space
            q_pca = pca_project(q_vecs, 64)
            q_norms = np.maximum(np.linalg.norm(q_pca, axis=1, keepdims=True), 1e-8)
            q_norm = q_pca / q_norms

            # Combinator anchor vectors in PCA-Q
            anchor_vecs = q_norm[comb_indices]  # (8, k)

            # Per-probe combinator profile: cosine to each anchor
            comb_profiles = q_norm @ anchor_vecs.T  # (n_probes, 8)

            # ── Test 1: Does combinator profile predict FFN activation? ──
            # For each neuron, correlate its activation across probes with
            # each combinator similarity score
            # This gives an 8-dimensional "combinator signature" per neuron

            # Efficient: comb_profiles.T @ ffn_binary = (8, n_neurons)
            # Each entry = sum of combinator similarity for probes where neuron fires
            comb_ffn_corr = np.zeros((len(COMBINATOR_ORDER), n_neurons))
            for ci in range(len(COMBINATOR_ORDER)):
                for ni in range(n_neurons):
                    if ffn_binary[:, ni].std() < 1e-8:
                        continue
                    comb_ffn_corr[ci, ni] = np.corrcoef(
                        comb_profiles[:, ci], ffn_binary[:, ni]
                    )[0, 1]

            # Per-combinator: how many neurons are strongly correlated?
            print(f"\n  {mk}: Neurons correlated with each combinator (|r|>0.3):",
                  file=sys.stderr, flush=True)
            print(f"  {'combinator':>12s}  {'n_positive':>10s}  {'n_negative':>10s}  "
                  f"{'mean_corr':>9s}  {'max_corr':>8s}",
                  file=sys.stderr, flush=True)
            print(f"  {'-'*54}", file=sys.stderr, flush=True)

            comb_neuron_counts = {}
            for ci, comb in enumerate(COMBINATOR_ORDER):
                row = comb_ffn_corr[ci]
                n_pos = int((row > 0.3).sum())
                n_neg = int((row < -0.3).sum())
                mean_c = float(row.mean())
                max_c = float(row.max())
                print(f"  {comb:>12s}  {n_pos:>10d}  {n_neg:>10d}  "
                      f"{mean_c:>+9.4f}  {max_c:>+8.4f}",
                      file=sys.stderr, flush=True)
                comb_neuron_counts[comb] = {"pos": n_pos, "neg": n_neg}

            # ── Test 2: Do neurons have a "dominant combinator"? ──
            # For each neuron, which combinator has the highest correlation?
            dominant_comb = np.argmax(np.abs(comb_ffn_corr), axis=0)
            dominant_sign = np.array([
                comb_ffn_corr[dominant_comb[ni], ni] for ni in range(n_neurons)
            ])

            # Count neurons per dominant combinator
            print(f"\n  {mk}: Dominant combinator per neuron:", file=sys.stderr, flush=True)
            for ci, comb in enumerate(COMBINATOR_ORDER):
                n_dom = int((dominant_comb == ci).sum())
                n_strong = int(((dominant_comb == ci) & (np.abs(dominant_sign) > 0.2)).sum())
                print(f"    {comb:>6s}: {n_dom:5d} neurons ({n_strong:4d} strong |r|>0.2)",
                      file=sys.stderr, flush=True)

            # ── Test 3: Per-domain combinator→FFN mapping ──
            # For each domain, what's its combinator profile, and does that
            # predict which FFN neurons fire?
            print(f"\n  {mk}: Domain combinator profiles (PCA-Q) → FFN activation:",
                  file=sys.stderr, flush=True)
            print(f"  {'domain':>12s}  {'dom_comb':>8s}  {'K':>6s}  {'B':>6s}  {'C':>6s}  "
                  f"{'W':>6s}  {'WHNF':>6s}  {'ffn_rate':>8s}",
                  file=sys.stderr, flush=True)
            print(f"  {'-'*66}", file=sys.stderr, flush=True)

            for d in SKILL_DOMAINS:
                if d not in domain_indices:
                    continue
                idx = domain_indices[d]
                # Mean combinator profile for this domain
                mean_profile = comb_profiles[idx].mean(axis=0)
                dom_comb = COMBINATOR_ORDER[np.argmax(mean_profile)]
                # Mean FFN activation rate
                mean_ffn_rate = float(ffn_binary[idx].mean())

                k_val = mean_profile[COMBINATOR_ORDER.index("K")] if "K" in COMBINATOR_ORDER else 0
                b_val = mean_profile[COMBINATOR_ORDER.index("B")] if "B" in COMBINATOR_ORDER else 0
                c_val = mean_profile[COMBINATOR_ORDER.index("C")] if "C" in COMBINATOR_ORDER else 0
                w_val = mean_profile[COMBINATOR_ORDER.index("W")] if "W" in COMBINATOR_ORDER else 0
                whnf_val = mean_profile[COMBINATOR_ORDER.index("WHNF")] if "WHNF" in COMBINATOR_ORDER else 0

                print(f"  {d:>12s}  {dom_comb:>8s}  {k_val:+.3f}  {b_val:+.3f}  "
                      f"{c_val:+.3f}  {w_val:+.3f}  {whnf_val:+.3f}  {mean_ffn_rate:>8.3f}",
                      file=sys.stderr, flush=True)

            # ── Test 4: Combinator profile predicts FFN pattern (full RDM) ──
            # Build RDM from combinator profiles, compare to FFN RDM
            cp_norms = np.maximum(np.linalg.norm(comb_profiles, axis=1, keepdims=True), 1e-8)
            cp_rdm = (comb_profiles / cp_norms) @ (comb_profiles / cp_norms).T

            ffn_pca = pca_project(ffn_acts, 64)
            fn_norms = np.maximum(np.linalg.norm(ffn_pca, axis=1, keepdims=True), 1e-8)
            ffn_rdm = (ffn_pca / fn_norms) @ (ffn_pca / fn_norms).T

            triu = np.triu_indices(n_probes, k=1)
            rdm_corr = float(np.corrcoef(cp_rdm[triu], ffn_rdm[triu])[0, 1])

            print(f"\n  {mk}: Combinator profile RDM ↔ FFN RDM correlation: {rdm_corr:+.4f}",
                  file=sys.stderr, flush=True)
            if rdm_corr > 0.5:
                print(f"  → STRONG: 8 combinator numbers predict FFN activation pattern",
                      file=sys.stderr, flush=True)
            elif rdm_corr > 0.3:
                print(f"  → MODERATE: combinators partially predict FFN",
                      file=sys.stderr, flush=True)

            # Also compare to binary FFN RDM (Jaccard)
            # Quick version: cosine of binary patterns
            fb_norms = np.maximum(np.linalg.norm(ffn_binary, axis=1, keepdims=True), 1e-8)
            ffn_bin_rdm = (ffn_binary / fb_norms) @ (ffn_binary / fb_norms).T
            bin_corr = float(np.corrcoef(cp_rdm[triu], ffn_bin_rdm[triu])[0, 1])
            print(f"  {mk}: Combinator profile RDM ↔ FFN binary RDM correlation: {bin_corr:+.4f}",
                  file=sys.stderr, flush=True)


def main():
    parser = argparse.ArgumentParser(description="Combinator→FFN Index Test")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")

    args = parser.parse_args()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  Combinator → FFN Index Test", file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t0 = time.time()
    probes = load_probes(args.probes)

    all_results = {}
    for mk in args.models:
        all_results[mk] = extract_q_and_ffn(mk, probes, DEPTH_FRACTIONS, args.device)

    analyze(all_results, probes)
    print(f"\n  Total: {time.time()-t0:.0f}s", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
