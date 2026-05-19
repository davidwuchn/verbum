"""FFN Hierarchy Tests — P2 (magnitude vs selectivity) and P3 (beam steering).

P2: High-magnitude W_up neurons should be domain-general (trunk),
    low-magnitude should be domain-specific (leaves).

P3: FFN output at layer n should predict Q shift at layer n+1.
    The FFN steers the beam to navigate the tree.

Usage:
    uv run python scripts/v12/ffn_hierarchy_test.py
    uv run python scripts/v12/ffn_hierarchy_test.py --models mistral-7b pythia-2.8b

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

# Use consecutive layer pairs for P3
# depth fractions → layer pairs (n, n+1)
DEPTH_FRACTIONS = [0.1, 0.3, 0.5, 0.7]

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


def get_domain_indices(probes):
    domain_idx = {}
    for i, p in enumerate(probes):
        d = p["axis"].split("/")[0]
        domain_idx.setdefault(d, []).append(i)
    return domain_idx


def run_model(model_key, probes, depth_fractions, device="mps"):
    """Extract W_up norms, FFN binary activations, FFN output deltas, and Q at consecutive layers."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model = MODELS[model_key]

    # Build layer pairs: for each depth fraction, get (layer_n, layer_n+1)
    layer_pairs = []
    for frac in depth_fractions:
        layer_n = min(int(round(frac * (n_layers - 1))), n_layers - 2)
        layer_pairs.append((layer_n, layer_n + 1, frac))

    all_layers = sorted(set(l for pair in layer_pairs for l in (pair[0], pair[1])))

    print(f"\n  ─── {model_key} ({model_name}) ───", file=sys.stderr, flush=True)
    print(f"  Layer pairs: {[(a, b) for a, b, _ in layer_pairs]}", file=sys.stderr, flush=True)

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
    is_fused_q = hasattr(test_attn, 'query_key_value')

    # ── Extract W_up row norms (P2) ──────────────────────────
    w_up_norms_per_layer = {}
    for li in all_layers:
        layer_mod = layers[li]
        mlp = layer_mod.mlp if hasattr(layer_mod, 'mlp') else getattr(layer_mod, 'feed_forward', None)
        if mlp is None:
            continue
        if hasattr(mlp, 'up_proj'):
            w_up = mlp.up_proj.weight.detach().cpu().float().numpy()
        elif hasattr(mlp, 'dense_h_to_4h'):
            w_up = mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()
        else:
            continue
        # Row norms = magnitude of each neuron's key
        norms = np.linalg.norm(w_up, axis=1)
        w_up_norms_per_layer[li] = norms

    # ── Hook Q, FFN activations, and FFN full output (the MLP module output) ──
    captures = {li: {"Q": [], "FFN_act": [], "hidden_pre": [], "hidden_post": []}
                for li in all_layers}
    hooks = []

    for li in all_layers:
        layer_mod = layers[li]
        attn_mod = get_attn(layer_mod)

        # Q hook
        if is_fused_q:
            fused = attn_mod.query_key_value
            q_size = d_model
            def make_q_hook(layer_idx, qs):
                def hook_fn(module, input, output):
                    captures[layer_idx]["Q"].append(output[:, -1, :qs].detach().cpu().float())
                return hook_fn
            hooks.append(fused.register_forward_hook(make_q_hook(li, q_size)))
        else:
            q_proj = attn_mod.q_proj
            def make_q_hook(layer_idx):
                def hook_fn(module, input, output):
                    captures[layer_idx]["Q"].append(output[:, -1, :].detach().cpu().float())
                return hook_fn
            hooks.append(q_proj.register_forward_hook(make_q_hook(li)))

        # FFN activation hook (up_proj output = key match)
        mlp = layer_mod.mlp if hasattr(layer_mod, 'mlp') else getattr(layer_mod, 'feed_forward', None)
        if mlp is not None:
            if hasattr(mlp, 'up_proj'):
                up = mlp.up_proj
            elif hasattr(mlp, 'dense_h_to_4h'):
                up = mlp.dense_h_to_4h
            else:
                up = None
            if up is not None:
                def make_ffn_hook(layer_idx):
                    def hook_fn(module, input, output):
                        captures[layer_idx]["FFN_act"].append(output[:, -1, :].detach().cpu().float())
                    return hook_fn
                hooks.append(up.register_forward_hook(make_ffn_hook(li)))

        # Layer input and output hooks (to get FFN delta = layer_output - pre_ffn)
        # We hook the full layer for hidden_post, and use hidden_pre from layer input
        def make_layer_hook(layer_idx):
            def hook_fn(module, input, output):
                h_out = output[0] if isinstance(output, tuple) else output
                captures[layer_idx]["hidden_post"].append(h_out[:, -1, :].detach().cpu().float())
                # Input to the layer
                h_in = input[0] if isinstance(input, tuple) else input
                captures[layer_idx]["hidden_pre"].append(h_in[:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(layer_mod.register_forward_hook(make_layer_hook(li)))

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

    # Stack captures
    result = {"w_up_norms": w_up_norms_per_layer, "layer_pairs": layer_pairs}
    for li in all_layers:
        layer_data = {}
        for key in ["Q", "FFN_act", "hidden_pre", "hidden_post"]:
            if captures[li][key]:
                layer_data[key] = torch.cat(captures[li][key], dim=0).numpy()
        result[li] = layer_data

    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available(): _t.mps.empty_cache()
        elif _t.cuda.is_available(): _t.cuda.empty_cache()
    except Exception: pass

    return result


def test_p2(model_key, result, probes):
    """P2: High-magnitude neurons are domain-general, low are domain-specific."""
    domain_indices = get_domain_indices(probes)

    print(f"\n{'='*80}", file=sys.stderr, flush=True)
    print(f"  P2: Magnitude vs Selectivity — {model_key}", file=sys.stderr, flush=True)
    print(f"{'='*80}", file=sys.stderr, flush=True)

    p2_results = {}

    for layer_n, layer_n1, frac in result["layer_pairs"]:
        norms = result["w_up_norms"].get(layer_n)
        layer_data = result.get(layer_n, {})
        ffn_act = layer_data.get("FFN_act")

        if norms is None or ffn_act is None:
            continue

        ffn_binary = (ffn_act > 0).astype(np.float32)
        n_neurons = norms.shape[0]

        # Compute per-neuron domain selectivity
        domain_rates = {}
        for d in SKILL_DOMAINS:
            if d not in domain_indices:
                continue
            idx = domain_indices[d]
            domain_rates[d] = ffn_binary[idx].mean(axis=0)

        all_rates = np.stack([domain_rates[d] for d in SKILL_DOMAINS if d in domain_rates])
        mean_rate = all_rates.mean(axis=0)
        max_rate = all_rates.max(axis=0)
        selectivity = max_rate - mean_rate  # high = domain-specific

        # Bin neurons by magnitude quintile
        percentiles = [0, 20, 40, 60, 80, 100]
        thresholds = np.percentile(norms, percentiles)

        print(f"\n  Layer {layer_n} (depth {frac:.0%}):", file=sys.stderr, flush=True)
        print(f"  {'mag_bin':>10s}  {'n_neurons':>9s}  {'mean_sel':>8s}  {'mean_rate':>9s}  "
              f"{'frac_sel>0.3':>11s}  {'norm_range':>14s}",
              file=sys.stderr, flush=True)
        print(f"  {'-'*64}", file=sys.stderr, flush=True)

        bin_data = []
        for b in range(len(percentiles) - 1):
            lo, hi = thresholds[b], thresholds[b + 1]
            if b == len(percentiles) - 2:
                mask = (norms >= lo) & (norms <= hi)
            else:
                mask = (norms >= lo) & (norms < hi)
            n_in_bin = int(mask.sum())
            if n_in_bin == 0:
                continue

            mean_sel = float(selectivity[mask].mean())
            mean_r = float(mean_rate[mask].mean())
            frac_selective = float((selectivity[mask] > 0.3).mean())
            label = f"Q{b+1} ({percentiles[b]}-{percentiles[b+1]}%)"

            print(f"  {label:>10s}  {n_in_bin:>9d}  {mean_sel:>+8.4f}  {mean_r:>9.3f}  "
                  f"{frac_selective:>11.1%}  [{lo:.3f}, {hi:.3f}]",
                  file=sys.stderr, flush=True)

            bin_data.append({
                "bin": label,
                "n": n_in_bin,
                "mean_selectivity": mean_sel,
                "mean_activation_rate": mean_r,
                "frac_selective": frac_selective,
            })

        # Correlation: norm vs selectivity
        corr = float(np.corrcoef(norms, selectivity)[0, 1])
        corr_rate = float(np.corrcoef(norms, mean_rate)[0, 1])
        print(f"\n  Correlation(|W_up row norm|, selectivity) = {corr:+.4f}",
              file=sys.stderr, flush=True)
        print(f"  Correlation(|W_up row norm|, activation rate) = {corr_rate:+.4f}",
              file=sys.stderr, flush=True)

        if corr < -0.05:
            print(f"  → SUPPORTS P2: high-magnitude neurons are LESS selective (trunk)",
                  file=sys.stderr, flush=True)
        elif corr > 0.05:
            print(f"  → CONTRADICTS P2: high-magnitude neurons are MORE selective",
                  file=sys.stderr, flush=True)
        else:
            print(f"  → INCONCLUSIVE: no clear relationship", file=sys.stderr, flush=True)

        p2_results[f"depth_{frac:.2f}"] = {
            "corr_norm_selectivity": corr,
            "corr_norm_rate": corr_rate,
            "bins": bin_data,
        }

    return p2_results


def test_p3(model_key, result, probes):
    """P3: FFN output at layer n predicts Q shift at layer n+1."""
    print(f"\n{'='*80}", file=sys.stderr, flush=True)
    print(f"  P3: FFN Beam Steering — {model_key}", file=sys.stderr, flush=True)
    print(f"{'='*80}", file=sys.stderr, flush=True)

    p3_results = {}

    for layer_n, layer_n1, frac in result["layer_pairs"]:
        data_n = result.get(layer_n, {})
        data_n1 = result.get(layer_n1, {})

        q_n = data_n.get("Q")
        q_n1 = data_n1.get("Q")
        h_pre = data_n.get("hidden_pre")
        h_post = data_n.get("hidden_post")

        if q_n is None or q_n1 is None:
            continue

        n_probes = q_n.shape[0]

        # FFN delta = what the layer added to the residual stream
        if h_pre is not None and h_post is not None:
            ffn_delta = h_post - h_pre  # (n_probes, d_model) — full layer delta
        else:
            ffn_delta = None

        # Q shift = how Q changed between layers
        # Q vectors may have different dimensions if GQA, so check
        d_q_n = q_n.shape[1]
        d_q_n1 = q_n1.shape[1]

        if d_q_n == d_q_n1:
            q_shift = q_n1 - q_n  # (n_probes, d_q)
        else:
            q_shift = None

        print(f"\n  Layer {layer_n}→{layer_n1} (depth {frac:.0%}):",
              file=sys.stderr, flush=True)

        depth_results = {}

        # Test 1: Per-probe cosine similarity between FFN delta and Q shift
        if ffn_delta is not None and q_shift is not None:
            # FFN delta is d_model, Q shift is d_q
            # For separate Q (Mistral): d_q = d_model, can compare directly
            # For fused (Pythia): d_q = d_model, same
            if ffn_delta.shape[1] == q_shift.shape[1]:
                # Per-probe cosine between FFN delta and Q shift
                fd_norms = np.maximum(np.linalg.norm(ffn_delta, axis=1, keepdims=True), 1e-8)
                qs_norms = np.maximum(np.linalg.norm(q_shift, axis=1, keepdims=True), 1e-8)
                per_probe_cos = np.sum(
                    (ffn_delta / fd_norms) * (q_shift / qs_norms), axis=1
                )
                mean_cos = float(per_probe_cos.mean())
                std_cos = float(per_probe_cos.std())
                print(f"    FFN_delta ↔ Q_shift cosine: mean={mean_cos:+.4f} ±{std_cos:.4f}",
                      file=sys.stderr, flush=True)
                depth_results["ffn_q_cosine_mean"] = mean_cos
                depth_results["ffn_q_cosine_std"] = std_cos

                if mean_cos > 0.1:
                    print(f"    → SUPPORTS P3: FFN output pushes Q in consistent direction",
                          file=sys.stderr, flush=True)
                elif mean_cos < -0.1:
                    print(f"    → ANTI-P3: FFN output pushes Q AWAY",
                          file=sys.stderr, flush=True)
                else:
                    print(f"    → WEAK: near-zero alignment",
                          file=sys.stderr, flush=True)

        # Test 2: RDM correlation — does the PATTERN of FFN deltas
        # match the PATTERN of Q shifts across probes?
        if ffn_delta is not None and q_shift is not None:
            fd_norms_all = np.maximum(np.linalg.norm(ffn_delta, axis=1, keepdims=True), 1e-8)
            qs_norms_all = np.maximum(np.linalg.norm(q_shift, axis=1, keepdims=True), 1e-8)
            ffn_rdm = (ffn_delta / fd_norms_all) @ (ffn_delta / fd_norms_all).T
            qs_rdm = (q_shift / qs_norms_all) @ (q_shift / qs_norms_all).T

            triu = np.triu_indices(n_probes, k=1)
            rdm_corr = float(np.corrcoef(ffn_rdm[triu], qs_rdm[triu])[0, 1])
            print(f"    FFN_delta RDM ↔ Q_shift RDM correlation: {rdm_corr:+.4f}",
                  file=sys.stderr, flush=True)
            depth_results["rdm_correlation"] = rdm_corr

            if rdm_corr > 0.3:
                print(f"    → SUPPORTS P3: probes that get similar FFN deltas also get similar Q shifts",
                      file=sys.stderr, flush=True)

        # Test 3: Does FFN delta magnitude predict Q shift magnitude?
        if ffn_delta is not None and q_shift is not None:
            fd_mags = np.linalg.norm(ffn_delta, axis=1)
            qs_mags = np.linalg.norm(q_shift, axis=1)
            mag_corr = float(np.corrcoef(fd_mags, qs_mags)[0, 1])
            print(f"    |FFN_delta| ↔ |Q_shift| correlation: {mag_corr:+.4f}",
                  file=sys.stderr, flush=True)
            depth_results["magnitude_correlation"] = mag_corr

        # Test 4: Per-domain — do domains with larger FFN deltas
        # show larger Q shifts?
        if ffn_delta is not None and q_shift is not None:
            domain_indices = get_domain_indices(probes)
            print(f"\n    Per-domain FFN→Q steering:", file=sys.stderr, flush=True)
            print(f"    {'domain':>12s}  {'|FFN_Δ|':>8s}  {'|Q_shift|':>9s}  {'cos':>6s}",
                  file=sys.stderr, flush=True)
            print(f"    {'-'*40}", file=sys.stderr, flush=True)
            for d in SKILL_DOMAINS:
                if d not in domain_indices:
                    continue
                idx = domain_indices[d]
                d_fd = float(np.linalg.norm(ffn_delta[idx], axis=1).mean())
                d_qs = float(np.linalg.norm(q_shift[idx], axis=1).mean())
                d_cos = float(per_probe_cos[idx].mean()) if 'per_probe_cos' in dir() else 0
                print(f"    {d:>12s}  {d_fd:>8.3f}  {d_qs:>9.3f}  {d_cos:>+6.3f}",
                      file=sys.stderr, flush=True)

        p3_results[f"depth_{frac:.2f}"] = depth_results

    return p3_results


def main():
    parser = argparse.ArgumentParser(description="FFN Hierarchy Tests P2+P3")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--output-dir", type=str, default="results/ffn-hierarchy")

    args = parser.parse_args()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  FFN Hierarchy Tests — P2 (magnitude) + P3 (beam steering)",
          file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t_start = time.time()
    probes = load_probes(args.probes)

    all_analysis = {}
    for mk in args.models:
        result = run_model(mk, probes, DEPTH_FRACTIONS, args.device)
        p2 = test_p2(mk, result, probes)
        p3 = test_p3(mk, result, probes)
        all_analysis[mk] = {"p2": p2, "p3": p3}

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "analysis.json", "w") as f:
        json.dump(all_analysis, f, indent=2, default=str)
    print(f"\n  💾 {output_dir}/analysis.json", file=sys.stderr, flush=True)

    elapsed = time.time() - t_start
    print(f"  Total: {elapsed:.0f}s", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
