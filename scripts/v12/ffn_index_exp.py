"""FFN Index Experiment — how does the crystal index into FFN storage?

Hypothesis: attention (shaped by the crystal) generates content-addressable
keys that index into FFN storage. The FFN up-projection reads the post-
attention residual as a key, the activation function thresholds, and the
down-projection retrieves the value.

Tests:
  1. Are FFN activation patterns domain-specific? (different domains → different neurons)
  2. Are FFN activations self-similar across layers? (prediction: NO, unlike Q)
  3. Does Q-space geometry predict FFN activation patterns? (crystal → index mapping)
  4. What fraction of FFN neurons are domain-selective vs shared?
  5. Does PCA of FFN activations reveal domain structure?

Setup: Hook into FFN intermediate layer (after up_proj + activation fn)
to capture the "key match" pattern. Compare to Q-space geometry.

Usage:
    uv run python scripts/v12/ffn_index_exp.py
    uv run python scripts/v12/ffn_index_exp.py --models mistral-7b pythia-2.8b

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
DEPTH_FRACTIONS = [0.1, 0.2, 0.3, 0.5, 0.7, 0.9]

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


def find_ffn_module(layer_mod):
    """Find the FFN/MLP module and its components."""
    # Most architectures: layer.mlp with gate_proj/up_proj/down_proj or fc1/fc2
    if hasattr(layer_mod, 'mlp'):
        mlp = layer_mod.mlp
    elif hasattr(layer_mod, 'feed_forward'):
        mlp = layer_mod.feed_forward
    else:
        return None, None, None

    # SwiGLU (Mistral, Llama, Qwen, OLMo): gate_proj * up_proj → act → down_proj
    if hasattr(mlp, 'gate_proj'):
        return mlp, 'swiglu', mlp.gate_proj
    # GPT-NeoX / Pythia: dense_h_to_4h → act → dense_4h_to_h
    elif hasattr(mlp, 'dense_h_to_4h'):
        return mlp, 'gptneox', mlp.dense_h_to_4h
    # Generic: fc1 → act → fc2
    elif hasattr(mlp, 'fc1'):
        return mlp, 'generic', mlp.fc1
    else:
        return mlp, 'unknown', None


def extract_ffn_and_q(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[float, dict[str, np.ndarray]]:
    """Extract Q vectors AND FFN intermediate activations.

    Returns: {depth: {"Q": (n_probes, d_q), "FFN": (n_probes, d_ffn), "FFN_binary": (n_probes, d_ffn)}}
    """
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
        get_attn = lambda l: l.self_attn
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
        get_attn = lambda l: l.attention
    else:
        raise ValueError(f"Unknown arch for {model_key}")

    # Detect FFN architecture
    test_mlp, ffn_type, _ = find_ffn_module(layers[0])
    print(f"  FFN type: {ffn_type}, d_model: {d_model}",
          file=sys.stderr, flush=True)

    # Detect Q architecture
    test_attn = get_attn(layers[0])
    is_fused_q = hasattr(test_attn, 'query_key_value')

    captures: dict[int, dict[str, list]] = {}
    hooks = []

    for layer_idx, frac in target_layers:
        captures[layer_idx] = {"Q": [], "FFN": []}
        layer_mod = layers[layer_idx]
        attn_mod = get_attn(layer_mod)

        # Q hook
        if is_fused_q:
            fused = attn_mod.query_key_value
            q_size = d_model
            def make_q_hook(li, qs):
                def hook_fn(module, input, output):
                    captures[li]["Q"].append(output[:, -1, :qs].detach().cpu().float())
                return hook_fn
            hooks.append(fused.register_forward_hook(make_q_hook(layer_idx, q_size)))
        else:
            q_proj = attn_mod.q_proj
            def make_q_hook(li):
                def hook_fn(module, input, output):
                    captures[li]["Q"].append(output[:, -1, :].detach().cpu().float())
                return hook_fn
            hooks.append(q_proj.register_forward_hook(make_q_hook(layer_idx)))

        # FFN hook — capture AFTER up-projection (the key matching step)
        mlp, ft, up_proj = find_ffn_module(layer_mod)
        if up_proj is not None:
            def make_ffn_hook(li):
                def hook_fn(module, input, output):
                    # After up_proj: this is the raw key match before gating
                    captures[li]["FFN"].append(output[:, -1, :].detach().cpu().float())
                return hook_fn
            hooks.append(up_proj.register_forward_hook(make_ffn_hook(layer_idx)))

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

    results = {}
    for layer_idx, frac in target_layers:
        space_vecs = {}
        for space in ["Q", "FFN"]:
            vecs = captures[layer_idx][space]
            if vecs:
                mat = torch.cat(vecs, dim=0).numpy()
                space_vecs[space] = mat
                # Also compute binary activation pattern (>0)
                if space == "FFN":
                    space_vecs["FFN_binary"] = (mat > 0).astype(np.float32)
                    active_frac = space_vecs["FFN_binary"].mean()
                    print(f"  L{layer_idx} FFN: {mat.shape}, "
                          f"active={active_frac:.1%}",
                          file=sys.stderr, flush=True)
        results[frac] = space_vecs

    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available(): _t.mps.empty_cache()
        elif _t.cuda.is_available(): _t.cuda.empty_cache()
    except Exception: pass

    return results


def pca_project(X: np.ndarray, n_components: int = 64) -> np.ndarray:
    X_centered = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    k = min(n_components, U.shape[1])
    return U[:, :k] * S[:k]


def cosine_rdm(X: np.ndarray) -> np.ndarray:
    norms = np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-8)
    return (X / norms) @ (X / norms).T


def jaccard_rdm(X_binary: np.ndarray) -> np.ndarray:
    """Jaccard similarity between binary activation patterns."""
    n = X_binary.shape[0]
    rdm = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            intersection = np.sum(X_binary[i] * X_binary[j])
            union = np.sum(np.maximum(X_binary[i], X_binary[j]))
            sim = intersection / max(union, 1e-8)
            rdm[i, j] = rdm[j, i] = sim
    return rdm


def rdm_correlation(rdm_a: np.ndarray, rdm_b: np.ndarray) -> float:
    n = rdm_a.shape[0]
    triu = np.triu_indices(n, k=1)
    va = rdm_a[triu]
    vb = rdm_b[triu]
    if np.std(va) < 1e-8 or np.std(vb) < 1e-8:
        return 0.0
    return float(np.corrcoef(va, vb)[0, 1])


def compute_domain_selectivity(
    ffn_binary: np.ndarray,
    domain_indices: dict[str, list[int]],
) -> dict:
    """Measure which FFN neurons are domain-selective."""
    n_neurons = ffn_binary.shape[1]
    domains = [d for d in SKILL_DOMAINS if d in domain_indices]

    # Per-neuron: what fraction of probes in each domain activate it?
    domain_activation_rates = {}
    for d in domains:
        idx = domain_indices[d]
        rates = ffn_binary[idx].mean(axis=0)  # (n_neurons,)
        domain_activation_rates[d] = rates

    # Neuron selectivity: max(domain_rate) - mean(other_domain_rates)
    all_rates = np.stack([domain_activation_rates[d] for d in domains])  # (n_domains, n_neurons)
    max_rate = all_rates.max(axis=0)
    mean_rate = all_rates.mean(axis=0)

    # A neuron is "selective" if its max-domain rate >> mean rate
    selectivity = max_rate - mean_rate
    selective_neurons = np.sum(selectivity > 0.3)  # >30% above mean
    shared_neurons = np.sum((mean_rate > 0.3) & (selectivity < 0.1))  # active for all, low selectivity

    # Which domain "owns" most selective neurons?
    dominant_domain = all_rates.argmax(axis=0)  # (n_neurons,)
    domain_neuron_counts = {}
    for di, d in enumerate(domains):
        selective_for_d = np.sum((dominant_domain == di) & (selectivity > 0.3))
        domain_neuron_counts[d] = int(selective_for_d)

    # Dead neurons (never active)
    dead_neurons = int(np.sum(max_rate < 0.01))

    return {
        "n_neurons": n_neurons,
        "selective_neurons": int(selective_neurons),
        "shared_neurons": int(shared_neurons),
        "dead_neurons": dead_neurons,
        "selective_pct": float(selective_neurons / n_neurons),
        "shared_pct": float(shared_neurons / n_neurons),
        "dead_pct": float(dead_neurons / n_neurons),
        "domain_selective_counts": domain_neuron_counts,
        "mean_selectivity": float(selectivity.mean()),
        "mean_activation_rate": float(mean_rate.mean()),
    }


def analyze_and_print(
    all_results: dict[str, dict[float, dict[str, np.ndarray]]],
    probes: list[dict],
    pca_dim: int = 64,
) -> dict:
    """Full FFN index analysis."""
    domain_indices = get_domain_indices(probes)
    model_keys = list(all_results.keys())
    depth_fractions = sorted(next(iter(all_results.values())).keys())

    analysis = {}

    for frac in depth_fractions:
        print(f"\n{'='*90}", file=sys.stderr, flush=True)
        print(f"  DEPTH {frac:.0%}", file=sys.stderr, flush=True)
        print(f"{'='*90}", file=sys.stderr, flush=True)

        depth_analysis = {}

        # ── Per-model: Q→FFN correlation (does Q predict FFN?) ──
        q_ffn_corrs = []
        q_ffn_binary_corrs = []
        for mk in model_keys:
            if frac not in all_results[mk]:
                continue
            r = all_results[mk][frac]
            if "Q" not in r or "FFN" not in r:
                continue

            q_pca = pca_project(r["Q"], pca_dim)
            q_rdm = cosine_rdm(q_pca)

            ffn_pca = pca_project(r["FFN"], pca_dim)
            ffn_rdm = cosine_rdm(ffn_pca)

            # Correlation between Q-space and FFN-space RDMs
            corr = rdm_correlation(q_rdm, ffn_rdm)
            q_ffn_corrs.append(corr)
            print(f"  {mk}: Q↔FFN RDM correlation = {corr:+.4f}",
                  file=sys.stderr, flush=True)

            # Binary activation pattern
            if "FFN_binary" in r:
                ffn_binary_rdm = jaccard_rdm(r["FFN_binary"])
                corr_b = rdm_correlation(q_rdm, ffn_binary_rdm)
                q_ffn_binary_corrs.append(corr_b)
                print(f"  {mk}: Q↔FFN_binary Jaccard correlation = {corr_b:+.4f}",
                      file=sys.stderr, flush=True)

        if q_ffn_corrs:
            mean_qf = float(np.mean(q_ffn_corrs))
            print(f"\n  ★ Q→FFN mapping: mean correlation = {mean_qf:+.4f}",
                  file=sys.stderr, flush=True)
            if mean_qf > 0.5:
                print(f"    → STRONG: crystal geometry PREDICTS FFN activation",
                      file=sys.stderr, flush=True)
            elif mean_qf > 0.3:
                print(f"    → MODERATE: crystal partially predicts FFN",
                      file=sys.stderr, flush=True)
            else:
                print(f"    → WEAK: FFN activation has independent structure",
                      file=sys.stderr, flush=True)
            depth_analysis["q_ffn_correlation"] = mean_qf

        # ── FFN self-similarity across depths ─────────────────
        # (compare FFN RDMs at this depth vs other depths for each model)

        # ── Domain selectivity of FFN neurons ─────────────────
        for mk in model_keys:
            if frac not in all_results[mk]:
                continue
            r = all_results[mk][frac]
            if "FFN_binary" not in r:
                continue

            sel = compute_domain_selectivity(r["FFN_binary"], domain_indices)
            print(f"\n  {mk} FFN neuron selectivity:", file=sys.stderr, flush=True)
            print(f"    {sel['n_neurons']} neurons: "
                  f"{sel['selective_pct']:.1%} selective, "
                  f"{sel['shared_pct']:.1%} shared, "
                  f"{sel['dead_pct']:.1%} dead",
                  file=sys.stderr, flush=True)
            print(f"    Domain-selective counts:", file=sys.stderr, flush=True)
            for d, c in sorted(sel["domain_selective_counts"].items(), key=lambda x: -x[1]):
                if c > 0:
                    print(f"      {d:>12s}: {c:4d} neurons",
                          file=sys.stderr, flush=True)

            depth_analysis[f"selectivity_{mk}"] = sel

        # ── Domain basin gaps in FFN space vs Q space ─────────
        print(f"\n  Basin gaps: FFN vs Q (PCA-{pca_dim}):", file=sys.stderr, flush=True)
        print(f"  {'domain':>12s}  {'Q_gap':>8s}  {'FFN_gap':>8s}  {'FFN_bin':>8s}  "
              f"{'Q>FFN?':>6s}", file=sys.stderr, flush=True)
        print(f"  {'-'*50}", file=sys.stderr, flush=True)

        for mk in model_keys:
            if frac not in all_results[mk]:
                continue
            r = all_results[mk][frac]
            if "Q" not in r or "FFN" not in r:
                continue

            q_rdm = cosine_rdm(pca_project(r["Q"], pca_dim))
            ffn_rdm = cosine_rdm(pca_project(r["FFN"], pca_dim))

            for d in SKILL_DOMAINS:
                if d not in domain_indices or d == "pure":
                    continue
                idx = domain_indices[d]

                # Q gap
                q_intra = np.mean([q_rdm[i, j] for ii, i in enumerate(idx) for j in idx[ii+1:]])
                q_inter = np.mean([q_rdm[i, j] for i in idx
                                   for d2 in SKILL_DOMAINS if d2 != d and d2 in domain_indices
                                   for j in domain_indices[d2]])
                q_gap = q_intra - q_inter

                # FFN gap
                f_intra = np.mean([ffn_rdm[i, j] for ii, i in enumerate(idx) for j in idx[ii+1:]])
                f_inter = np.mean([ffn_rdm[i, j] for i in idx
                                   for d2 in SKILL_DOMAINS if d2 != d and d2 in domain_indices
                                   for j in domain_indices[d2]])
                f_gap = f_intra - f_inter

                # Binary FFN gap
                b_gap = 0.0
                if "FFN_binary" in r:
                    b_rdm = jaccard_rdm(r["FFN_binary"])
                    b_intra = np.mean([b_rdm[i, j] for ii, i in enumerate(idx) for j in idx[ii+1:]])
                    b_inter = np.mean([b_rdm[i, j] for i in idx
                                       for d2 in SKILL_DOMAINS if d2 != d and d2 in domain_indices
                                       for j in domain_indices[d2]])
                    b_gap = b_intra - b_inter

                marker = "Q" if q_gap > f_gap else "FFN"
                print(f"  {d:>12s}  {q_gap:+.4f}  {f_gap:+.4f}  {b_gap:+.4f}  "
                      f"{marker:>6s}",
                      file=sys.stderr, flush=True)
            break  # Just first model for readability

        # ── FFN cross-depth self-similarity ───────────────────
        # Compare FFN RDMs across depths for each model
        for mk in model_keys:
            print(f"\n  {mk} FFN self-similarity across depths:",
                  file=sys.stderr, flush=True)
            ffn_rdms_by_depth = {}
            q_rdms_by_depth = {}
            for f2 in depth_fractions:
                if f2 in all_results[mk] and "FFN" in all_results[mk][f2]:
                    ffn_rdms_by_depth[f2] = cosine_rdm(
                        pca_project(all_results[mk][f2]["FFN"], pca_dim))
                if f2 in all_results[mk] and "Q" in all_results[mk][f2]:
                    q_rdms_by_depth[f2] = cosine_rdm(
                        pca_project(all_results[mk][f2]["Q"], pca_dim))

            if len(ffn_rdms_by_depth) >= 2:
                ffn_corrs = []
                q_corrs = []
                for fi, di in enumerate(sorted(ffn_rdms_by_depth.keys())):
                    for fj, dj in enumerate(sorted(ffn_rdms_by_depth.keys())):
                        if fi >= fj:
                            continue
                        fc = rdm_correlation(ffn_rdms_by_depth[di], ffn_rdms_by_depth[dj])
                        ffn_corrs.append(fc)
                        if di in q_rdms_by_depth and dj in q_rdms_by_depth:
                            qc = rdm_correlation(q_rdms_by_depth[di], q_rdms_by_depth[dj])
                            q_corrs.append(qc)

                mean_ffn_ss = float(np.mean(ffn_corrs))
                mean_q_ss = float(np.mean(q_corrs)) if q_corrs else 0
                print(f"    FFN cross-depth correlation: {mean_ffn_ss:+.4f}",
                      file=sys.stderr, flush=True)
                print(f"    Q   cross-depth correlation: {mean_q_ss:+.4f}",
                      file=sys.stderr, flush=True)
                print(f"    → FFN {'IS' if mean_ffn_ss > 0.5 else 'is NOT'} self-similar "
                      f"(Q {'IS' if mean_q_ss > 0.5 else 'is NOT'})",
                      file=sys.stderr, flush=True)

                depth_analysis[f"ffn_self_similarity_{mk}"] = mean_ffn_ss
                depth_analysis[f"q_self_similarity_{mk}"] = mean_q_ss
            break

        analysis[f"{frac:.2f}"] = depth_analysis

    return analysis


def main():
    parser = argparse.ArgumentParser(description="FFN Index Experiment")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--pca-dim", type=int, default=64)
    parser.add_argument("--output-dir", type=str, default="results/ffn-index")

    args = parser.parse_args()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  FFN Index Experiment — Crystal → FFN Addressing", file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t_start = time.time()
    probes = load_probes(args.probes)

    all_results = {}
    for mk in args.models:
        results = extract_ffn_and_q(mk, probes, DEPTH_FRACTIONS, args.device)
        all_results[mk] = results

    analysis = analyze_and_print(all_results, probes, args.pca_dim)

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
