"""FFN Map — partition neurons by combinator, rank by magnitude, extract values.

Builds a complete map of the FFN organized by the lambda compiler's
combinator addressing system. Each neuron gets assigned to a combinator
department based on its activation correlation with combinator probes.

Output per layer:
  - Department sizes (how many neurons per combinator)
  - Magnitude distribution per department (hierarchy levels)
  - Value space dimensionality per department
  - Cross-model agreement on departmental assignment
  - Domain routing: which departments serve which skill domains

Usage:
    uv run python scripts/v12/ffn_map.py
    uv run python scripts/v12/ffn_map.py --models mistral-7b pythia-2.8b

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
    idx = {}
    for i, p in enumerate(probes):
        if p["axis"].startswith("pure/"):
            idx[p["axis"].split("/")[1]] = i
    return idx


def get_domain_indices(probes):
    idx = {}
    for i, p in enumerate(probes):
        d = p["axis"].split("/")[0]
        idx.setdefault(d, []).append(i)
    return idx


def pca_project(X, k=64):
    X_c = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_c, full_matrices=False)
    k = min(k, U.shape[1])
    return U[:, :k] * S[:k]


def extract_model(model_key, probes, depth_fractions, device="mps"):
    """Extract Q vectors, FFN activations, W_up, W_down."""
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
        # Extract weights
        mlp = layers[li].mlp if hasattr(layers[li], 'mlp') else getattr(layers[li], 'feed_forward', None)
        w_up = w_down = None
        if mlp:
            if hasattr(mlp, 'up_proj'):
                w_up = mlp.up_proj.weight.detach().cpu().float().numpy()
                w_down = mlp.down_proj.weight.detach().cpu().float().numpy()
            elif hasattr(mlp, 'dense_h_to_4h'):
                w_up = mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()
                w_down = mlp.dense_4h_to_h.weight.detach().cpu().float().numpy()

        # Hook Q and FFN activations
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

        if mlp:
            up_mod = getattr(mlp, 'up_proj', None) or getattr(mlp, 'dense_h_to_4h', None)
            if up_mod:
                def make_ffn():
                    def hook(m, inp, out):
                        captures["FFN"].append(out[:, -1, :].detach().cpu().float())
                    return hook
                hooks.append(up_mod.register_forward_hook(make_ffn()))

        for probe in probes:
            ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
            with torch.no_grad():
                _ = model(ids)

        for h in hooks:
            h.remove()

        q_vecs = torch.cat(captures["Q"], dim=0).numpy() if captures["Q"] else None
        ffn_acts = torch.cat(captures["FFN"], dim=0).numpy() if captures["FFN"] else None

        results[frac] = {
            "q_vecs": q_vecs,
            "ffn_acts": ffn_acts,
            "ffn_binary": (ffn_acts > 0).astype(np.float32) if ffn_acts is not None else None,
            "w_up": w_up,
            "w_down": w_down,
            "w_up_norms": np.linalg.norm(w_up, axis=1) if w_up is not None else None,
        }

    print(f"  Done ({len(target_layers)} layers)", file=sys.stderr, flush=True)

    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available(): _t.mps.empty_cache()
    except: pass

    return results


def build_ffn_map(model_key, data, probes, frac):
    """Build the FFN map for one model at one depth."""
    pure_idx = get_pure_indices(probes)
    domain_indices = get_domain_indices(probes)

    r = data[frac]
    q_vecs = r["q_vecs"]
    ffn_binary = r["ffn_binary"]
    w_up = r["w_up"]
    w_down = r["w_down"]
    w_up_norms = r["w_up_norms"]

    if q_vecs is None or ffn_binary is None or w_up is None:
        return None

    n_neurons = ffn_binary.shape[1]
    comb_indices = [pure_idx[c] for c in COMBINATOR_ORDER if c in pure_idx]

    # PCA-Q combinator profiles
    q_pca = pca_project(q_vecs, 64)
    q_norms = np.maximum(np.linalg.norm(q_pca, axis=1, keepdims=True), 1e-8)
    q_norm = q_pca / q_norms
    anchor_vecs = q_norm[comb_indices]
    comb_profiles = q_norm @ anchor_vecs.T  # (n_probes, 8)

    # Per-neuron combinator correlation
    comb_corr = np.zeros((len(COMBINATOR_ORDER), n_neurons))
    for ci in range(len(COMBINATOR_ORDER)):
        for ni in range(n_neurons):
            if ffn_binary[:, ni].std() < 1e-8:
                continue
            comb_corr[ci, ni] = np.corrcoef(comb_profiles[:, ci], ffn_binary[:, ni])[0, 1]

    # Assign dominant combinator (by absolute correlation)
    dominant_idx = np.argmax(np.abs(comb_corr), axis=0)
    dominant_sign = np.array([comb_corr[dominant_idx[ni], ni] for ni in range(n_neurons)])
    dominant_strength = np.abs(dominant_sign)

    # Build department map
    departments = {}
    for ci, comb in enumerate(COMBINATOR_ORDER):
        mask = dominant_idx == ci
        dept_neurons = np.where(mask)[0]
        n_dept = len(dept_neurons)

        if n_dept == 0:
            departments[comb] = {"n_neurons": 0}
            continue

        # Magnitude distribution
        dept_norms = w_up_norms[dept_neurons]
        dept_strengths = dominant_strength[dept_neurons]

        # Strong neurons (|r| > 0.2)
        strong_mask = dept_strengths > 0.2
        n_strong = int(strong_mask.sum())

        # Value space dimensionality (SVD of W_down for this department)
        if w_down.shape[0] < w_down.shape[1]:
            dept_values = w_down[:, dept_neurons]  # (d_model, n_dept)
        else:
            dept_values = w_down[dept_neurons, :].T  # (d_model, n_dept)

        if n_dept >= 3:
            U, S, Vt = np.linalg.svd(dept_values, full_matrices=False)
            ev = (S ** 2) / max((S ** 2).sum(), 1e-8)
            cumvar = np.cumsum(ev)
            dims_50 = int(np.searchsorted(cumvar, 0.5)) + 1
            dims_80 = int(np.searchsorted(cumvar, 0.8)) + 1
            dims_95 = int(np.searchsorted(cumvar, 0.95)) + 1
            top3_ev = ev[:3].tolist()
        else:
            dims_50 = dims_80 = dims_95 = n_dept
            top3_ev = []

        # Domain routing: which domains activate this department most?
        domain_activation = {}
        for d in SKILL_DOMAINS:
            if d not in domain_indices:
                continue
            d_idx = domain_indices[d]
            dept_activation = ffn_binary[d_idx][:, dept_neurons].mean()
            domain_activation[d] = float(dept_activation)

        top_domains = sorted(domain_activation.items(), key=lambda x: -x[1])[:3]

        # Magnitude hierarchy bins
        if n_dept >= 10:
            q25, q50, q75 = np.percentile(dept_norms, [25, 50, 75])
            mag_profile = {
                "min": float(dept_norms.min()),
                "q25": float(q25),
                "median": float(q50),
                "q75": float(q75),
                "max": float(dept_norms.max()),
                "mean": float(dept_norms.mean()),
            }
        else:
            mag_profile = {"mean": float(dept_norms.mean()) if n_dept > 0 else 0}

        departments[comb] = {
            "n_neurons": n_dept,
            "n_strong": n_strong,
            "pct_of_total": float(n_dept / n_neurons),
            "mean_strength": float(dept_strengths.mean()),
            "magnitude": mag_profile,
            "value_dims_50": dims_50,
            "value_dims_80": dims_80,
            "value_dims_95": dims_95,
            "top3_explained_var": top3_ev,
            "top_domains": top_domains,
            "domain_activation": domain_activation,
        }

    return {
        "n_neurons_total": n_neurons,
        "departments": departments,
    }


def print_map(model_key, frac, ffn_map):
    """Print the FFN map."""
    if ffn_map is None:
        return

    n_total = ffn_map["n_neurons_total"]
    depts = ffn_map["departments"]

    print(f"\n{'='*90}", file=sys.stderr, flush=True)
    print(f"  FFN MAP — {model_key} depth {frac:.0%} ({n_total} neurons)",
          file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)

    # Department summary
    print(f"\n  {'dept':>6s}  {'neurons':>7s}  {'%total':>6s}  {'strong':>6s}  "
          f"{'strength':>8s}  {'val_50d':>7s}  {'val_80d':>7s}  {'top_domains':>30s}",
          file=sys.stderr, flush=True)
    print(f"  {'-'*82}", file=sys.stderr, flush=True)

    for comb in COMBINATOR_ORDER:
        d = depts[comb]
        if d["n_neurons"] == 0:
            continue
        top_d = ", ".join(f"{name[:5]}({rate:.2f})" for name, rate in d["top_domains"])
        print(f"  {comb:>6s}  {d['n_neurons']:>7d}  {d['pct_of_total']:>5.1%}  "
              f"{d['n_strong']:>6d}  {d['mean_strength']:>8.3f}  "
              f"{d['value_dims_50']:>7d}  {d['value_dims_80']:>7d}  {top_d:>30s}",
              file=sys.stderr, flush=True)

    # Department detail
    for comb in COMBINATOR_ORDER:
        d = depts[comb]
        if d["n_neurons"] < 10:
            continue

        print(f"\n  ── {comb} Department ({d['n_neurons']} neurons, "
              f"{d['n_strong']} strong) ──", file=sys.stderr, flush=True)

        mag = d["magnitude"]
        print(f"    Magnitude: [{mag.get('min',0):.3f} | {mag.get('q25',0):.3f} | "
              f"{mag.get('median',0):.3f} | {mag.get('q75',0):.3f} | {mag.get('max',0):.3f}]",
              file=sys.stderr, flush=True)

        if d["top3_explained_var"]:
            print(f"    Value space: {d['value_dims_50']}d (50%), "
                  f"{d['value_dims_80']}d (80%), {d['value_dims_95']}d (95%)",
                  file=sys.stderr, flush=True)
            print(f"    Top-3 explained var: {', '.join(f'{v:.1%}' for v in d['top3_explained_var'])}",
                  file=sys.stderr, flush=True)

        print(f"    Domain routing:", file=sys.stderr, flush=True)
        for domain, rate in sorted(d["domain_activation"].items(), key=lambda x: -x[1]):
            bar = "█" * int(rate * 60)
            print(f"      {domain:>12s}: {rate:.3f} {bar}", file=sys.stderr, flush=True)


def cross_model_comparison(all_maps, frac):
    """Compare departmental structure across models."""
    model_keys = [mk for mk in all_maps if frac in all_maps[mk] and all_maps[mk][frac] is not None]
    if len(model_keys) < 2:
        return

    print(f"\n{'='*90}", file=sys.stderr, flush=True)
    print(f"  CROSS-MODEL COMPARISON — depth {frac:.0%}", file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)

    print(f"\n  Department sizes (% of total):", file=sys.stderr, flush=True)
    print(f"  {'comb':>6s}", end='', file=sys.stderr)
    for mk in model_keys:
        print(f"  {mk[:10]:>10s}", end='', file=sys.stderr)
    print(f"  {'agree':>6s}", file=sys.stderr, flush=True)
    print(f"  {'-'*(8 + 12*len(model_keys) + 8)}", file=sys.stderr, flush=True)

    for comb in COMBINATOR_ORDER:
        print(f"  {comb:>6s}", end='', file=sys.stderr)
        pcts = []
        for mk in model_keys:
            pct = all_maps[mk][frac]["departments"][comb]["pct_of_total"]
            pcts.append(pct)
            print(f"  {pct:>9.1%}", end='', file=sys.stderr)
        # Agreement: how similar are the percentages?
        if len(pcts) >= 2:
            spread = max(pcts) - min(pcts)
            agree = "✓" if spread < 0.05 else "~" if spread < 0.10 else "✗"
        else:
            agree = "?"
        print(f"  {agree:>6s}", file=sys.stderr, flush=True)

    # Domain routing agreement
    print(f"\n  Domain → Top Combinator:", file=sys.stderr, flush=True)
    print(f"  {'domain':>12s}", end='', file=sys.stderr)
    for mk in model_keys:
        print(f"  {mk[:10]:>10s}", end='', file=sys.stderr)
    print(f"  {'agree':>6s}", file=sys.stderr, flush=True)
    print(f"  {'-'*(14 + 12*len(model_keys) + 8)}", file=sys.stderr, flush=True)

    for domain in SKILL_DOMAINS:
        print(f"  {domain:>12s}", end='', file=sys.stderr)
        top_combs = []
        for mk in model_keys:
            depts = all_maps[mk][frac]["departments"]
            best_comb = max(COMBINATOR_ORDER,
                           key=lambda c: depts[c]["domain_activation"].get(domain, 0)
                           if depts[c]["n_neurons"] > 0 else -1)
            top_combs.append(best_comb)
            print(f"  {best_comb:>10s}", end='', file=sys.stderr)
        agree = "✓" if len(set(top_combs)) == 1 else "✗"
        print(f"  {agree:>6s}", file=sys.stderr, flush=True)


def main():
    parser = argparse.ArgumentParser(description="FFN Map")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--output-dir", type=str, default="results/ffn-map")

    args = parser.parse_args()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  FFN Map — Combinator-Indexed Neuron Database", file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t0 = time.time()
    probes = load_probes(args.probes)

    all_maps = {}
    for mk in args.models:
        data = extract_model(mk, probes, DEPTH_FRACTIONS, args.device)
        all_maps[mk] = {}
        for frac in DEPTH_FRACTIONS:
            if frac in data:
                ffn_map = build_ffn_map(mk, data, probes, frac)
                all_maps[mk][frac] = ffn_map
                print_map(mk, frac, ffn_map)

    # Cross-model comparison
    for frac in DEPTH_FRACTIONS:
        cross_model_comparison(all_maps, frac)

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Convert to JSON-serializable
    json_data = {}
    for mk in all_maps:
        json_data[mk] = {}
        for frac in all_maps[mk]:
            m = all_maps[mk][frac]
            if m is None:
                continue
            json_data[mk][f"{frac:.2f}"] = {
                "n_neurons_total": m["n_neurons_total"],
                "departments": {
                    c: {k: v for k, v in d.items() if k != "neuron_indices"}
                    for c, d in m["departments"].items()
                },
            }

    with open(output_dir / "ffn_map.json", "w") as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"\n  💾 {output_dir}/ffn_map.json", file=sys.stderr, flush=True)
    print(f"  Total: {time.time()-t0:.0f}s", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
