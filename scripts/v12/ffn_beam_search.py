"""FFN Beam Search — hunt for the FFN crystal's reference beam.

The attention crystal has PCA-Q as its reference beam (0.91-0.94 agreement).
The FFN is 77% self-similar across depths — it IS a crystal. But we don't
know how to read it yet. This script searches for the FFN beam by testing
multiple hook points as PCA candidates:

  1. up_proj output         — raw key match (pre-gate)
  2. gate × up_proj         — gated activation (SwiGLU only)
  3. FFN delta              — what the FFN adds to the residual stream
  4. Binary activation      — thresholded gate×up (which neurons fire)

For each hook point, we run the full PCA-Q protocol:
  - PCA project to k dimensions
  - Build cosine RDMs per model per depth
  - Measure cross-model agreement (the key metric)
  - Measure cross-depth self-similarity
  - Compare to PCA-Q baseline (0.91-0.94)

If any hook point yields agreement ≥ 0.85, we've found the FFN beam.

Usage:
    uv run python scripts/v12/ffn_beam_search.py --quick          # 2 models
    uv run python scripts/v12/ffn_beam_search.py                  # 4 models
    uv run python scripts/v12/ffn_beam_search.py --pca-dim 128    # wider PCA

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

# Hook points to test
HOOK_POINTS = ["up_proj", "gate_x_up", "ffn_delta", "binary"]

ZONE_DEPTHS = {
    "A": [0.1],
    "B": [0.3, 0.5],
    "C": [0.7, 0.9],
}


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


def pca_project(X: np.ndarray, n_components: int = 64) -> np.ndarray:
    """Center + SVD, return score matrix U*S."""
    X_centered = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    k = min(n_components, U.shape[1])
    return U[:, :k] * S[:k]


def cosine_rdm(X: np.ndarray) -> np.ndarray:
    """Cosine similarity matrix (n_probes × n_probes)."""
    norms = np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-8)
    return (X / norms) @ (X / norms).T


def rdm_correlation(rdm_a: np.ndarray, rdm_b: np.ndarray) -> float:
    """Pearson correlation of upper-triangular RDM entries."""
    n = rdm_a.shape[0]
    triu = np.triu_indices(n, k=1)
    a, b = rdm_a[triu], rdm_b[triu]
    if a.std() < 1e-10 or b.std() < 1e-10:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def find_ffn_parts(layer_mod):
    """Detect FFN architecture and return (mlp, arch_type, modules_dict).

    Returns a dict of hookable modules for each architecture.
    """
    mlp = getattr(layer_mod, 'mlp', None) or getattr(layer_mod, 'feed_forward', None)
    if mlp is None:
        raise ValueError(f"Cannot find MLP in {type(layer_mod)}")

    if hasattr(mlp, 'gate_proj'):
        # SwiGLU: Mistral, Qwen, OLMo, LLaMA
        return mlp, 'swiglu', {
            'up_proj': mlp.up_proj,
            'gate_proj': mlp.gate_proj,
            'down_proj': mlp.down_proj,
        }
    elif hasattr(mlp, 'dense_h_to_4h'):
        # GPT-NeoX / Pythia
        return mlp, 'gptneox', {
            'up_proj': mlp.dense_h_to_4h,
            'down_proj': mlp.dense_4h_to_h,
        }
    else:
        raise ValueError(f"Unknown MLP architecture: {type(mlp)}")


def extract_ffn_vectors(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[str, dict[float, np.ndarray]]:
    """Extract FFN activations from one model at multiple hook points.

    Returns {hook_point: {depth: (n_probes, d_ffn_or_d_model)}}.
    Also extracts Q vectors for comparison baseline.
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model, d_ffn = MODELS[model_key]

    # Map depth fractions to layer indices
    target_layers = []
    for frac in depth_fractions:
        layer = min(int(round(frac * (n_layers - 1))), n_layers - 1)
        if layer not in [l for l, _ in target_layers]:
            target_layers.append((layer, frac))

    print(f"\n  ─── {model_key} ({model_name}) ───", file=sys.stderr, flush=True)
    print(f"  Layers: {[(li, f'{f:.0%}') for li, f in target_layers]}", file=sys.stderr, flush=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device, trust_remote_code=True,
    )
    model.eval()

    # Get layers
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
        get_attn = lambda l: l.self_attn
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
        get_attn = lambda l: l.attention
    else:
        raise ValueError(f"Unknown arch for {model_key}")

    # Detect attention architecture
    test_attn = get_attn(layers[0])
    is_fused_qkv = hasattr(test_attn, 'query_key_value')

    # Detect FFN architecture
    _, arch_type, _ = find_ffn_parts(layers[0])
    is_swiglu = (arch_type == 'swiglu')
    print(f"  FFN arch: {arch_type}, SwiGLU: {is_swiglu}", file=sys.stderr, flush=True)

    # Storage: {layer_idx: {signal_name: [per-probe tensors]}}
    captures: dict[int, dict[str, list]] = {}
    for li, _ in target_layers:
        captures[li] = {
            'up_proj': [],
            'gate_proj': [],     # SwiGLU only
            'pre_ffn': [],       # hidden state before FFN (for delta)
            'post_ffn': [],      # hidden state after FFN (for delta)
            'q_proj': [],        # Q baseline
        }

    hooks = []

    for layer_idx, frac in target_layers:
        layer_mod = layers[layer_idx]
        mlp, _, ffn_mods = find_ffn_parts(layer_mod)
        attn_mod = get_attn(layer_mod)

        # Hook 1: up_proj output
        def make_up_hook(li):
            def hook_fn(module, input, output):
                captures[li]['up_proj'].append(output[:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(ffn_mods['up_proj'].register_forward_hook(make_up_hook(layer_idx)))

        # Hook 2: gate_proj output (SwiGLU only)
        if is_swiglu:
            def make_gate_hook(li):
                def hook_fn(module, input, output):
                    captures[li]['gate_proj'].append(output[:, -1, :].detach().cpu().float())
                return hook_fn
            hooks.append(ffn_mods['gate_proj'].register_forward_hook(make_gate_hook(layer_idx)))

        # Hook 3: MLP module itself (for pre/post delta)
        # We hook the whole MLP module to get input and output
        def make_mlp_hook(li):
            def hook_fn(module, input, output):
                # input[0] is the hidden state entering MLP
                captures[li]['pre_ffn'].append(input[0][:, -1, :].detach().cpu().float())
                captures[li]['post_ffn'].append(output[:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(mlp.register_forward_hook(make_mlp_hook(layer_idx)))

        # Hook 4: Q projection (for comparison baseline)
        if is_fused_qkv:
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

    # Forward all probes
    print(f"  Running {len(probes)} probes...", file=sys.stderr, flush=True)
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 50 == 0:
            print(f"    {i+1}/{len(probes)}...", file=sys.stderr, flush=True)
    dt = time.time() - t0
    print(f"  Done in {dt:.1f}s ({dt/len(probes):.2f}s/probe)", file=sys.stderr, flush=True)

    for h in hooks:
        h.remove()

    # Assemble results by hook point
    results: dict[str, dict[float, np.ndarray]] = {
        'up_proj': {},
        'gate_x_up': {},
        'ffn_delta': {},
        'binary': {},
        'q_proj': {},  # baseline
    }

    for layer_idx, frac in target_layers:
        c = captures[layer_idx]

        # up_proj: raw
        if c['up_proj']:
            up = torch.cat(c['up_proj'], dim=0).numpy()
            results['up_proj'][frac] = up

            # gate × up (SwiGLU) or just up (GPT-NeoX applies GELU internally)
            if c['gate_proj']:
                gate = torch.cat(c['gate_proj'], dim=0).numpy()
                import torch.nn.functional as F
                # SwiGLU: silu(gate) * up
                gate_act = 1.0 / (1.0 + np.exp(-gate)) * gate  # silu = x * sigmoid(x)
                gated = gate_act * up
                results['gate_x_up'][frac] = gated
                # Binary: which neurons fire after gating?
                results['binary'][frac] = (gated > 0).astype(np.float32)
            else:
                # GPT-NeoX: use GELU of up_proj output
                # up_proj already includes the full d_h→4d_h transform
                gelu = up * 0.5 * (1.0 + np.tanh(np.sqrt(2.0/np.pi) * (up + 0.044715 * up**3)))
                results['gate_x_up'][frac] = gelu
                results['binary'][frac] = (gelu > 0).astype(np.float32)

        # FFN delta
        if c['pre_ffn'] and c['post_ffn']:
            pre = torch.cat(c['pre_ffn'], dim=0).numpy()
            post = torch.cat(c['post_ffn'], dim=0).numpy()
            results['ffn_delta'][frac] = post - pre

        # Q baseline
        if c['q_proj']:
            results['q_proj'][frac] = torch.cat(c['q_proj'], dim=0).numpy()

    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available(): _t.mps.empty_cache()
        elif _t.cuda.is_available(): _t.cuda.empty_cache()
    except Exception:
        pass

    return results


def analyze_hook_point(
    hook_name: str,
    all_vectors: dict[str, dict[float, np.ndarray]],
    probes: list[dict],
    pca_dim: int = 64,
) -> dict:
    """Run full PCA crystal analysis for one hook point across all models."""
    model_keys = list(all_vectors.keys())
    n_probes = len(probes)

    # PCA project and build RDMs per model per depth
    per_model_rdms: dict[str, dict[float, np.ndarray]] = {}
    pca_explained: dict[str, dict[float, list]] = {}  # track explained variance

    for mk in model_keys:
        per_model_rdms[mk] = {}
        pca_explained[mk] = {}
        for frac in DEPTH_FRACTIONS:
            if frac not in all_vectors[mk]:
                continue
            raw = all_vectors[mk][frac]
            if raw.shape[0] != n_probes:
                print(f"    WARN: {hook_name} {mk} {frac:.0%}: got {raw.shape[0]} probes, expected {n_probes}",
                      file=sys.stderr)
                continue

            # PCA project
            pca = pca_project(raw, pca_dim)

            # Track explained variance (for diagnostics)
            X_c = raw - raw.mean(axis=0, keepdims=True)
            _, S_full, _ = np.linalg.svd(X_c, full_matrices=False)
            total_var = (S_full ** 2).sum()
            k = min(pca_dim, len(S_full))
            captured_var = (S_full[:k] ** 2).sum()
            pca_explained[mk][frac] = float(captured_var / max(total_var, 1e-10))

            # Build RDM
            rdm = cosine_rdm(pca)
            per_model_rdms[mk][frac] = rdm

    # Consensus and agreement per depth
    consensus_rdms: dict[float, np.ndarray] = {}
    agreement_per_depth: dict[float, float] = {}

    for frac in DEPTH_FRACTIONS:
        model_rdms = []
        for mk in model_keys:
            if frac in per_model_rdms[mk]:
                model_rdms.append(per_model_rdms[mk][frac])
        if len(model_rdms) < 2:
            continue

        stacked = np.stack(model_rdms)
        consensus = stacked.mean(axis=0)
        consensus_rdms[frac] = consensus

        # Cross-model agreement
        corrs = []
        for i in range(len(model_rdms)):
            for j in range(i + 1, len(model_rdms)):
                corrs.append(rdm_correlation(model_rdms[i], model_rdms[j]))
        agreement_per_depth[frac] = float(np.mean(corrs))

    # Self-similarity: cross-depth RDM correlation
    depth_keys = sorted(consensus_rdms.keys())
    n_depths = len(depth_keys)
    self_sim = np.zeros((n_depths, n_depths))
    for i, di in enumerate(depth_keys):
        for j, dj in enumerate(depth_keys):
            self_sim[i, j] = rdm_correlation(consensus_rdms[di], consensus_rdms[dj])

    mean_self_sim = float(self_sim[np.triu_indices(n_depths, k=1)].mean()) if n_depths > 1 else 0.0

    # Zone-level agreement
    zone_agreement = {}
    for zone_name, zone_depths in ZONE_DEPTHS.items():
        zone_vals = [agreement_per_depth[d] for d in zone_depths if d in agreement_per_depth]
        zone_agreement[zone_name] = float(np.mean(zone_vals)) if zone_vals else 0.0

    # Overall metrics
    all_agreements = list(agreement_per_depth.values())
    mean_agreement = float(np.mean(all_agreements)) if all_agreements else 0.0
    best_depth = max(agreement_per_depth, key=agreement_per_depth.get) if agreement_per_depth else 0.5
    best_agreement = agreement_per_depth.get(best_depth, 0.0)

    # PCA explained variance summary
    mean_pca_explained = {}
    for frac in DEPTH_FRACTIONS:
        vals = [pca_explained[mk].get(frac, 0) for mk in model_keys if frac in pca_explained[mk]]
        if vals:
            mean_pca_explained[f"{frac:.1f}"] = float(np.mean(vals))

    # Per-domain agreement at best depth (diagnostic)
    domain_idx = get_domain_indices(probes)
    domain_agreement = {}
    for domain, indices in domain_idx.items():
        if domain == 'pure':
            continue
        if len(indices) < 3:
            continue
        domain_rdms = []
        for mk in model_keys:
            if best_depth in per_model_rdms[mk]:
                full_rdm = per_model_rdms[mk][best_depth]
                # Extract sub-RDM for this domain
                sub_rdm = full_rdm[np.ix_(indices, indices)]
                domain_rdms.append(sub_rdm)
        if len(domain_rdms) >= 2:
            corrs = []
            for i in range(len(domain_rdms)):
                for j in range(i + 1, len(domain_rdms)):
                    corrs.append(rdm_correlation(domain_rdms[i], domain_rdms[j]))
            domain_agreement[domain] = float(np.mean(corrs))

    return {
        "hook_point": hook_name,
        "n_models": len(model_keys),
        "model_keys": model_keys,
        "pca_dim": pca_dim,
        "mean_agreement": mean_agreement,
        "best_agreement": best_agreement,
        "best_depth": best_depth,
        "mean_self_similarity": mean_self_sim,
        "agreement_per_depth": {f"{f:.1f}": a for f, a in sorted(agreement_per_depth.items())},
        "zone_agreement": zone_agreement,
        "self_similarity_matrix": self_sim.tolist(),
        "self_similarity_depths": [f"{d:.1f}" for d in depth_keys],
        "mean_pca_explained": mean_pca_explained,
        "domain_agreement": domain_agreement,
    }


def print_results(all_results: dict[str, dict]) -> None:
    """Print comparison table across hook points."""
    print(f"\n{'='*100}", file=sys.stderr, flush=True)
    print(f"  FFN BEAM SEARCH — Cross-Model Agreement by Hook Point", file=sys.stderr, flush=True)
    print(f"{'='*100}", file=sys.stderr, flush=True)

    # ── Summary table ─────────────────────────────────────────
    print(f"\n  {'hook_point':>15s}  {'mean_agr':>8s}  {'best_agr':>8s}  {'best_d':>6s}  "
          f"{'self_sim':>8s}  {'zone_A':>6s}  {'zone_B':>6s}  {'zone_C':>6s}  {'verdict':>10s}",
          file=sys.stderr, flush=True)
    print(f"  {'─'*85}", file=sys.stderr, flush=True)

    for hook in ['q_proj'] + HOOK_POINTS:
        if hook not in all_results:
            continue
        r = all_results[hook]
        verdict = "★★★ BEAM" if r['mean_agreement'] >= 0.85 else \
                  "★★ strong" if r['mean_agreement'] >= 0.70 else \
                  "★ weak" if r['mean_agreement'] >= 0.50 else \
                  "✗ none"
        za = r['zone_agreement']
        print(f"  {hook:>15s}  {r['mean_agreement']:>+8.4f}  {r['best_agreement']:>+8.4f}  "
              f"{r['best_depth']:>6.0%}  {r['mean_self_similarity']:>+8.4f}  "
              f"{za.get('A', 0):>+6.3f}  {za.get('B', 0):>+6.3f}  {za.get('C', 0):>+6.3f}  "
              f"{verdict:>10s}",
              file=sys.stderr, flush=True)

    # ── Per-hook detail ─────────────────────────────────────
    for hook in ['q_proj'] + HOOK_POINTS:
        if hook not in all_results:
            continue
        r = all_results[hook]

        print(f"\n  ═══ {hook.upper()} ═══", file=sys.stderr, flush=True)

        # Agreement profile across depths
        print(f"  Agreement per depth:", file=sys.stderr, flush=True)
        for dk, av in sorted(r["agreement_per_depth"].items()):
            bar = "█" * int(max(0, av) * 50)
            print(f"    depth {dk}: {av:+.4f} {bar}", file=sys.stderr, flush=True)

        # PCA explained variance
        if r.get("mean_pca_explained"):
            print(f"  PCA captured variance:", file=sys.stderr, flush=True)
            for dk, ev in sorted(r["mean_pca_explained"].items()):
                print(f"    depth {dk}: {ev:.1%}", file=sys.stderr, flush=True)

        # Self-similarity
        print(f"  Mean cross-depth self-similarity: {r['mean_self_similarity']:+.4f}",
              file=sys.stderr, flush=True)

        # Per-domain agreement at best depth
        if r.get("domain_agreement"):
            print(f"  Per-domain agreement (depth {r['best_depth']:.0%}):", file=sys.stderr, flush=True)
            for domain, agr in sorted(r["domain_agreement"].items(), key=lambda x: -x[1]):
                bar = "█" * int(max(0, agr) * 40)
                print(f"    {domain:>12s}: {agr:+.4f} {bar}", file=sys.stderr, flush=True)

    # ── Verdict ─────────────────────────────────────────────
    print(f"\n{'='*100}", file=sys.stderr, flush=True)
    ffn_hooks = {h: all_results[h] for h in HOOK_POINTS if h in all_results}
    if ffn_hooks:
        best_hook = max(ffn_hooks, key=lambda h: ffn_hooks[h]['mean_agreement'])
        best = ffn_hooks[best_hook]
        q_agr = all_results.get('q_proj', {}).get('mean_agreement', 0)
        print(f"  BEST FFN HOOK: {best_hook}", file=sys.stderr, flush=True)
        print(f"    Mean agreement: {best['mean_agreement']:+.4f} "
              f"(Q baseline: {q_agr:+.4f}, ratio: {best['mean_agreement']/max(q_agr, 1e-8):.1%})",
              file=sys.stderr, flush=True)
        print(f"    Self-similarity: {best['mean_self_similarity']:+.4f}", file=sys.stderr, flush=True)

        if best['mean_agreement'] >= 0.85:
            print(f"  ★★★ FFN BEAM FOUND — {best_hook} reads the FFN crystal!", file=sys.stderr, flush=True)
        elif best['mean_agreement'] >= 0.70:
            print(f"  ★★ STRONG SIGNAL — {best_hook} partially reads the FFN crystal", file=sys.stderr, flush=True)
        elif best['mean_agreement'] >= 0.50:
            print(f"  ★ WEAK SIGNAL — some structure but not a clean beam", file=sys.stderr, flush=True)
        else:
            print(f"  ✗ NO BEAM FOUND at these hook points", file=sys.stderr, flush=True)

    print(f"{'='*100}", file=sys.stderr, flush=True)


def main():
    parser = argparse.ArgumentParser(description="FFN Beam Search")
    parser.add_argument("--models", nargs="+", default=None,
                        choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--pca-dim", type=int, default=64)
    parser.add_argument("--quick", action="store_true",
                        help="Use only 2 models (Mistral + Pythia)")
    parser.add_argument("--output-dir", type=str, default="results/ffn-beam")

    args = parser.parse_args()
    model_keys = args.models or (QUICK_MODELS if args.quick else DEFAULT_MODELS)

    print("=" * 80, file=sys.stderr, flush=True)
    print("  FFN Beam Search — Hunting the FFN Crystal's Reference Beam", file=sys.stderr, flush=True)
    print(f"  Models: {model_keys}", file=sys.stderr, flush=True)
    print(f"  Hook points: {['q_proj (baseline)'] + HOOK_POINTS}", file=sys.stderr, flush=True)
    print(f"  Depths: {DEPTH_FRACTIONS}", file=sys.stderr, flush=True)
    print(f"  PCA dim: {args.pca_dim}", file=sys.stderr, flush=True)
    print("=" * 80, file=sys.stderr, flush=True)

    t_start = time.time()
    probes = load_probes(args.probes)

    # Extract all vectors from all models
    # {model: {hook_point: {depth: (n_probes, d)}}}
    all_model_vectors: dict[str, dict[str, dict[float, np.ndarray]]] = {}
    for mk in model_keys:
        vectors = extract_ffn_vectors(mk, probes, DEPTH_FRACTIONS, args.device)
        all_model_vectors[mk] = vectors

    # Reorganize: {hook_point: {model: {depth: array}}}
    hook_to_model_vectors: dict[str, dict[str, dict[float, np.ndarray]]] = {}
    for hook in ['q_proj'] + HOOK_POINTS:
        hook_to_model_vectors[hook] = {}
        for mk in model_keys:
            if hook in all_model_vectors[mk]:
                hook_to_model_vectors[hook][mk] = all_model_vectors[mk][hook]

    # Analyze each hook point
    all_results: dict[str, dict] = {}
    for hook in ['q_proj'] + HOOK_POINTS:
        if not hook_to_model_vectors[hook]:
            print(f"  SKIP {hook}: no data", file=sys.stderr, flush=True)
            continue
        print(f"\n  Analyzing {hook}...", file=sys.stderr, flush=True)
        all_results[hook] = analyze_hook_point(
            hook, hook_to_model_vectors[hook], probes, args.pca_dim
        )

    # Print results
    print_results(all_results)

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_data = {
        "description": "FFN beam search — hunting the FFN crystal reference beam",
        "n_models": len(model_keys),
        "model_keys": model_keys,
        "pca_dim": args.pca_dim,
        "depth_fractions": DEPTH_FRACTIONS,
        "hook_points": ['q_proj'] + HOOK_POINTS,
        "results": all_results,
    }
    json_path = output_dir / "ffn_beam_results.json"
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"\n  💾 {json_path}", file=sys.stderr, flush=True)

    elapsed = time.time() - t_start
    print(f"  Total: {elapsed:.0f}s ({elapsed/60:.1f}min)", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
