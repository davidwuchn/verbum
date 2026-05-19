"""Basin Q/K/V Experiment — test whether Q rotation mediates basin routing.

Hypothesis: models dedicate Q rotation to routing into skill-specific basins.
If true, domain separation should be STRONGER in Q-space than in hidden-state
space. K-space and V-space may show different basin structure.

Test:
  1. Run domain probes through models
  2. Capture hidden states AND Q, K, V projections at multiple depths
  3. Build per-domain RDMs in each space (hidden, Q, K, V)
  4. Compare basin separation (intra-inter gap) across spaces
  5. If Q-space gap > hidden-space gap → Q rotation IS basin routing

Usage:
    uv run python scripts/v12/basin_qkv_exp.py
    uv run python scripts/v12/basin_qkv_exp.py --models mistral-7b pythia-2.8b

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


def load_probes(probe_path: str | None = None) -> list[dict]:
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json")
    with open(probe_path) as f:
        probes = json.load(f)
    cats: dict[str, int] = {}
    for p in probes:
        cat = p["axis"].split("/")[0]
        cats[cat] = cats.get(cat, 0) + 1
    print(f"  Loaded {len(probes)} probes", file=sys.stderr, flush=True)
    return probes


def get_domain_indices(probes: list[dict]) -> dict[str, list[int]]:
    domain_idx: dict[str, list[int]] = {}
    for i, p in enumerate(probes):
        domain = p["axis"].split("/")[0]
        domain_idx.setdefault(domain, []).append(i)
    return domain_idx


def find_attn_module(model, layer_idx: int):
    """Find the attention module for a given layer, handling different architectures."""
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layer = model.model.layers[layer_idx]
    elif hasattr(model, 'transformer') and hasattr(model.transformer, 'h'):
        layer = model.transformer.h[layer_idx]
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layer = model.gpt_neox.layers[layer_idx]
    else:
        raise ValueError("Cannot find transformer layers")

    # Find attention submodule
    if hasattr(layer, 'self_attn'):
        return layer, layer.self_attn
    elif hasattr(layer, 'attention'):
        return layer, layer.attention
    elif hasattr(layer, 'attn'):
        return layer, layer.attn
    else:
        raise ValueError(f"Cannot find attention module in layer {layer_idx}")


def find_qkv_projections(attn_module):
    """Find Q, K, V projection modules, handling different architectures.
    
    Returns dict with keys 'q', 'k', 'v' pointing to nn.Linear modules,
    or 'qkv' if they're fused.
    """
    projections = {}
    
    # Separate Q, K, V (most common: Mistral, Llama, OLMo, Qwen)
    if hasattr(attn_module, 'q_proj'):
        projections['q'] = attn_module.q_proj
        projections['k'] = attn_module.k_proj
        projections['v'] = attn_module.v_proj
        projections['type'] = 'separate'
    # Fused QKV (GPT-NeoX / Pythia)
    elif hasattr(attn_module, 'query_key_value'):
        projections['qkv'] = attn_module.query_key_value
        projections['type'] = 'fused_qkv'
    # Other fused patterns
    elif hasattr(attn_module, 'c_attn'):
        projections['qkv'] = attn_module.c_attn
        projections['type'] = 'fused_c_attn'
    else:
        raise ValueError(f"Cannot find Q/K/V projections in {type(attn_module).__name__}")
    
    return projections


def extract_qkv_rdms(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[float, dict[str, np.ndarray]]:
    """Extract RDMs in hidden, Q, K, V spaces at each depth.
    
    Returns: {depth_frac: {"hidden": rdm, "Q": rdm, "K": rdm, "V": rdm}}
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model = MODELS[model_key]

    # Map fractions to layer indices
    target_layers = []
    frac_to_layer = {}
    for frac in depth_fractions:
        layer = min(int(round(frac * (n_layers - 1))), n_layers - 1)
        if layer not in [l for l, _ in target_layers]:
            target_layers.append((layer, frac))
            frac_to_layer[frac] = layer

    print(f"\n  ─── {model_key} ({model_name}) ───", file=sys.stderr, flush=True)
    print(f"  Layers: {n_layers}, d_model: {d_model}", file=sys.stderr, flush=True)
    print(f"  Targets: {[(l, f'{f:.0%}') for l, f in target_layers]}",
          file=sys.stderr, flush=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map=device,
        trust_remote_code=True,
    )
    model.eval()

    # Discover architecture once
    test_layer, test_attn = find_attn_module(model, target_layers[0][0])
    proj_info = find_qkv_projections(test_attn)
    print(f"  QKV type: {proj_info['type']}", file=sys.stderr, flush=True)

    # Set up captures: hidden state + Q, K, V
    captures: dict[int, dict[str, list]] = {}
    hooks = []

    for layer_idx, frac in target_layers:
        captures[layer_idx] = {"hidden": [], "Q": [], "K": [], "V": []}
        layer_mod, attn_mod = find_attn_module(model, layer_idx)
        proj = find_qkv_projections(attn_mod)

        # Hook on the layer for hidden states
        def make_hidden_hook(li):
            def hook_fn(module, input, output):
                h = output[0] if isinstance(output, tuple) else output
                captures[li]["hidden"].append(h[:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(layer_mod.register_forward_hook(make_hidden_hook(layer_idx)))

        if proj['type'] == 'separate':
            # Hook each projection separately
            def make_proj_hook(li, space_name):
                def hook_fn(module, input, output):
                    captures[li][space_name].append(
                        output[:, -1, :].detach().cpu().float()
                    )
                return hook_fn
            hooks.append(proj['q'].register_forward_hook(make_proj_hook(layer_idx, "Q")))
            hooks.append(proj['k'].register_forward_hook(make_proj_hook(layer_idx, "K")))
            hooks.append(proj['v'].register_forward_hook(make_proj_hook(layer_idx, "V")))

        elif proj['type'] in ('fused_qkv', 'fused_c_attn'):
            # Fused: output is [Q, K, V] concatenated along last dim
            # Need to split based on model dimensions
            fused_mod = proj.get('qkv') or proj.get('c_attn')
            
            # Determine split sizes
            # For GPT-NeoX: Q, K, V each have d_model dimensions
            # Some models have GQA where K, V are smaller
            out_features = fused_mod.out_features if hasattr(fused_mod, 'out_features') else fused_mod.weight.shape[0]
            
            # Try to figure out the split
            # Most fused QKV: Q=d_model, K=d_kv, V=d_kv
            # For Pythia: all equal (d_model each, total 3*d_model)
            if out_features == 3 * d_model:
                q_size = k_size = v_size = d_model
            else:
                # GQA: guess based on output size
                # total = d_model + 2 * d_kv
                # Assume num_kv_heads can be derived
                q_size = d_model
                remaining = out_features - d_model
                k_size = v_size = remaining // 2

            def make_fused_hook(li, qs, ks, vs):
                def hook_fn(module, input, output):
                    out = output[:, -1, :].detach().cpu().float()
                    captures[li]["Q"].append(out[:, :qs])
                    captures[li]["K"].append(out[:, qs:qs+ks])
                    captures[li]["V"].append(out[:, qs+ks:qs+ks+vs])
                return hook_fn
            hooks.append(fused_mod.register_forward_hook(
                make_fused_hook(layer_idx, q_size, k_size, v_size)
            ))

    # Run probes
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

    # Build cosine RDMs per space
    results = {}
    for layer_idx, frac in target_layers:
        space_rdms = {}
        for space in ["hidden", "Q", "K", "V"]:
            vecs = captures[layer_idx][space]
            if not vecs:
                print(f"  WARNING: no captures for {space} at layer {layer_idx}",
                      file=sys.stderr, flush=True)
                continue
            hs = torch.cat(vecs, dim=0).numpy()
            norms = np.maximum(np.linalg.norm(hs, axis=1, keepdims=True), 1e-8)
            hs_norm = hs / norms
            rdm = hs_norm @ hs_norm.T
            space_rdms[space] = rdm
            print(f"  L{layer_idx} {space:>6s}: shape={hs.shape}, "
                  f"mean_sim={rdm.mean():.4f}", file=sys.stderr, flush=True)
        results[frac] = space_rdms

    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available():
            _t.mps.empty_cache()
        elif _t.cuda.is_available():
            _t.cuda.empty_cache()
    except Exception:
        pass

    return results


def compute_basin_gaps(
    rdm: np.ndarray,
    domain_indices: dict[str, list[int]],
    domains: list[str],
) -> dict[str, dict]:
    """Compute per-domain basin gap (intra - mean_inter similarity)."""
    gaps = {}
    for d in domains:
        if d not in domain_indices or d == "pure":
            continue
        idx = domain_indices[d]
        
        # Intra-domain similarity
        intra_sims = []
        for i in range(len(idx)):
            for j in range(i + 1, len(idx)):
                intra_sims.append(float(rdm[idx[i], idx[j]]))
        intra = float(np.mean(intra_sims)) if intra_sims else 0.0

        # Inter-domain similarity (this domain vs all others)
        inter_sims = []
        for d2 in domains:
            if d2 == d or d2 == "pure" or d2 not in domain_indices:
                continue
            for pi in idx:
                for pj in domain_indices[d2]:
                    inter_sims.append(float(rdm[pi, pj]))
        inter = float(np.mean(inter_sims)) if inter_sims else 0.0

        gaps[d] = {
            "intra": intra,
            "inter": inter,
            "gap": intra - inter,
            "ratio": intra / inter if inter > 1e-8 else 0.0,
        }

    return gaps


def analyze_and_print(
    all_results: dict[str, dict[float, dict[str, np.ndarray]]],
    probes: list[dict],
) -> dict:
    """Cross-model consensus analysis of Q/K/V basin separation."""
    domain_indices = get_domain_indices(probes)
    model_keys = list(all_results.keys())
    depth_fractions = sorted(next(iter(all_results.values())).keys())
    spaces = ["hidden", "Q", "K", "V"]

    full_analysis = {}

    for frac in depth_fractions:
        print(f"\n{'='*90}", file=sys.stderr, flush=True)
        print(f"  DEPTH {frac:.0%} — Basin Separation by Representation Space",
              file=sys.stderr, flush=True)
        print(f"{'='*90}", file=sys.stderr, flush=True)

        # Per-model gaps, then average
        space_gaps: dict[str, dict[str, list[float]]] = {
            s: {d: [] for d in SKILL_DOMAINS} for s in spaces
        }
        space_model_gaps: dict[str, list[dict]] = {s: [] for s in spaces}

        for model_key in model_keys:
            if frac not in all_results[model_key]:
                continue
            for space in spaces:
                if space not in all_results[model_key][frac]:
                    continue
                rdm = all_results[model_key][frac][space]
                gaps = compute_basin_gaps(rdm, domain_indices, SKILL_DOMAINS)
                space_model_gaps[space].append(gaps)
                for d, g in gaps.items():
                    space_gaps[space][d].append(g["gap"])

        # Build consensus RDMs for cross-model analysis
        consensus_gaps: dict[str, dict[str, dict]] = {}
        for space in spaces:
            model_rdms = []
            for mk in model_keys:
                if frac in all_results[mk] and space in all_results[mk][frac]:
                    model_rdms.append(all_results[mk][frac][space])
            if len(model_rdms) < 2:
                continue
            consensus_rdm = np.mean(model_rdms, axis=0)
            gaps = compute_basin_gaps(consensus_rdm, domain_indices, SKILL_DOMAINS)
            consensus_gaps[space] = gaps

        # ── Print: per-space mean gap across domains ──────────
        print(f"\n  Mean Basin Gap by Space (consensus of {len(model_keys)} models):",
              file=sys.stderr, flush=True)
        print(f"  {'space':>8s}  {'mean_gap':>8s}  {'max_gap':>8s}  {'strongest':>12s}  "
              f"{'weakest':>12s}",
              file=sys.stderr, flush=True)
        print(f"  {'-'*56}", file=sys.stderr, flush=True)

        space_mean_gaps = {}
        for space in spaces:
            if space not in consensus_gaps:
                continue
            gaps = consensus_gaps[space]
            gap_vals = [g["gap"] for g in gaps.values()]
            mean_gap = np.mean(gap_vals)
            space_mean_gaps[space] = mean_gap
            strongest = max(gaps.keys(), key=lambda d: gaps[d]["gap"])
            weakest = min(gaps.keys(), key=lambda d: gaps[d]["gap"])
            print(f"  {space:>8s}  {mean_gap:+.4f}  {max(gap_vals):+.4f}  "
                  f"{strongest:>12s}  {weakest:>12s}",
                  file=sys.stderr, flush=True)

        # ── Print: per-domain gaps in each space ──────────────
        print(f"\n  Per-Domain Basin Gap by Space:", file=sys.stderr, flush=True)
        print(f"  {'domain':>12s}", end='', file=sys.stderr)
        for space in spaces:
            print(f"  {space:>8s}", end='', file=sys.stderr)
        print(f"  {'best_space':>10s}  {'Q>hidden':>8s}", file=sys.stderr, flush=True)
        print(f"  {'-'*72}", file=sys.stderr, flush=True)

        for d in SKILL_DOMAINS:
            print(f"  {d:>12s}", end='', file=sys.stderr)
            gaps_by_space = {}
            for space in spaces:
                if space in consensus_gaps and d in consensus_gaps[space]:
                    g = consensus_gaps[space][d]["gap"]
                    gaps_by_space[space] = g
                    print(f"  {g:+.4f}", end='', file=sys.stderr)
                else:
                    print(f"  {'n/a':>8s}", end='', file=sys.stderr)
            
            if gaps_by_space:
                best = max(gaps_by_space.keys(), key=lambda s: gaps_by_space[s])
                q_better = ""
                if "Q" in gaps_by_space and "hidden" in gaps_by_space:
                    diff = gaps_by_space["Q"] - gaps_by_space["hidden"]
                    q_better = f"{diff:+.4f}"
                print(f"  {best:>10s}  {q_better:>8s}", end='', file=sys.stderr)
            print(file=sys.stderr, flush=True)

        # ── Key test: is Q gap > hidden gap? ──────────────────
        if "Q" in space_mean_gaps and "hidden" in space_mean_gaps:
            q_gap = space_mean_gaps["Q"]
            h_gap = space_mean_gaps["hidden"]
            diff = q_gap - h_gap
            print(f"\n  ★ KEY TEST: Q mean gap ({q_gap:+.4f}) vs hidden mean gap ({h_gap:+.4f})",
                  file=sys.stderr, flush=True)
            if diff > 0:
                print(f"    → Q shows STRONGER basin separation by {diff:+.4f}",
                      file=sys.stderr, flush=True)
                print(f"    → SUPPORTS hypothesis: Q rotation mediates basin routing",
                      file=sys.stderr, flush=True)
            elif diff < -0.01:
                print(f"    → Q shows WEAKER basin separation by {diff:.4f}",
                      file=sys.stderr, flush=True)
                print(f"    → CHALLENGES hypothesis: basin routing is NOT primarily in Q",
                      file=sys.stderr, flush=True)
            else:
                print(f"    → Q and hidden are similar ({diff:+.4f})",
                      file=sys.stderr, flush=True)
                print(f"    → INCONCLUSIVE: basin separation is already in hidden state",
                      file=sys.stderr, flush=True)

        # Check V and K too
        for space in ["K", "V"]:
            if space in space_mean_gaps and "hidden" in space_mean_gaps:
                s_gap = space_mean_gaps[space]
                diff = s_gap - space_mean_gaps["hidden"]
                if abs(diff) > 0.01:
                    direction = "stronger" if diff > 0 else "weaker"
                    print(f"    {space} gap is {direction} than hidden by {diff:+.4f}",
                          file=sys.stderr, flush=True)

        # ── Per-model consistency ─────────────────────────────
        print(f"\n  Per-Model Consistency (do models agree on Q > hidden?):",
              file=sys.stderr, flush=True)
        for mk_idx, mk in enumerate(model_keys):
            if frac not in all_results[mk]:
                continue
            q_gaps_model = []
            h_gaps_model = []
            for d in SKILL_DOMAINS:
                for space, gap_list in [("Q", q_gaps_model), ("hidden", h_gaps_model)]:
                    if space in all_results[mk][frac]:
                        rdm = all_results[mk][frac][space]
                        g = compute_basin_gaps(rdm, domain_indices, [d])
                        if d in g:
                            gap_list.append(g[d]["gap"])
            if q_gaps_model and h_gaps_model:
                q_mean = np.mean(q_gaps_model)
                h_mean = np.mean(h_gaps_model)
                print(f"    {mk:>12s}: Q gap={q_mean:+.4f}, hidden gap={h_mean:+.4f}, "
                      f"Q-hidden={q_mean-h_mean:+.4f}",
                      file=sys.stderr, flush=True)

        full_analysis[f"{frac:.2f}"] = {
            "space_mean_gaps": {s: float(v) for s, v in space_mean_gaps.items()},
            "consensus_gaps": {
                space: {d: g for d, g in gaps.items()}
                for space, gaps in consensus_gaps.items()
            },
        }

    return full_analysis


def main():
    parser = argparse.ArgumentParser(description="Basin Q/K/V experiment")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--output-dir", type=str, default="results/basin-qkv")

    args = parser.parse_args()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  Basin Q/K/V Experiment — Q Rotation Basin Routing Test",
          file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print(f"  Depths: {[f'{d:.0%}' for d in DEPTH_FRACTIONS]}",
          file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t_start = time.time()

    probes = load_probes(args.probes)

    all_results: dict[str, dict[float, dict[str, np.ndarray]]] = {}
    for mk in args.models:
        results = extract_qkv_rdms(mk, probes, DEPTH_FRACTIONS, args.device)
        all_results[mk] = results

    analysis = analyze_and_print(all_results, probes)

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save per-model RDMs
    for mk in all_results:
        npz_data = {}
        for frac, space_rdms in all_results[mk].items():
            for space, rdm in space_rdms.items():
                npz_data[f"depth_{frac:.2f}_{space}"] = rdm.astype(np.float32)
        np.savez_compressed(str(output_dir / f"rdm_{mk}.npz"), **npz_data)

    # Save analysis JSON
    with open(output_dir / "analysis.json", "w") as f:
        json.dump(analysis, f, indent=2, default=str)

    elapsed = time.time() - t_start
    print(f"\n  Total: {elapsed:.0f}s", file=sys.stderr, flush=True)
    print(f"  Output: {output_dir}/", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
