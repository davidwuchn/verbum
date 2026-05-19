"""Build Binding Lattice — fine-grained depth exploration of binding mechanisms.

Extends build_lattice_map.py with:
  1. 10% depth increments (0%, 10%, 20%, ..., 90%) to find binding pipeline handoffs
  2. Binding chain probes designed to isolate the C→B/S→WHNF cascade
  3. Per-model RDM export for model-specific analysis

The key question: at which model depth does C (argument routing) hand off
to B/S (composition/substitution), and where does WHNF (terminal form)
take over? The handoff pattern should be consistent across models if
binding is a universal pipeline of beta reductions.

Usage:
    uv run python scripts/v12/build_binding_lattice.py

    # Specific models
    uv run python scripts/v12/build_binding_lattice.py --models qwen3-14b mistral-7b

    # Quick test
    uv run python scripts/v12/build_binding_lattice.py --models pythia-2.8b pythia-1.4b

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

# ══════════════════════════════════════════════════════════════════════
# Model registry (shared with build_lattice_map.py)
# ══════════════════════════════════════════════════════════════════════

MODELS = {
    "qwen3.6-27b":  ("Qwen/Qwen3.6-27B",             64, 5120),
    "qwen3-14b":    ("Qwen/Qwen3-14B",                40, 5120),
    "llama-3-8b":   ("meta-llama/Llama-3.1-8B",       32, 4096),
    "mistral-7b":   ("mistralai/Mistral-7B-v0.3",     32, 4096),
    "olmo-2-13b":   ("allenai/OLMo-2-1124-13B",       40, 5120),
    "olmo-2-7b":    ("allenai/OLMo-2-1124-7B",        32, 4096),
    "pythia-6.9b":  ("EleutherAI/pythia-6.9b",         32, 4096),
    "pythia-2.8b":  ("EleutherAI/pythia-2.8b-deduped", 32, 2560),
    "pythia-1.4b":  ("EleutherAI/pythia-1.4b-deduped",  24, 2048),
    "smollm3-3b":   ("HuggingFaceTB/SmolLM3-3B",      36, 2560),
    "phi-4-mini":   ("microsoft/Phi-4-mini-instruct",  32, 3072),
}

DEFAULT_MODELS = ["qwen3-14b", "mistral-7b", "olmo-2-13b", "pythia-2.8b"]

# Fine-grained depth: 10% increments for binding pipeline mapping
BINDING_DEPTH_FRACTIONS = [i / 10 for i in range(10)]  # 0.0, 0.1, ..., 0.9


# ══════════════════════════════════════════════════════════════════════
# Probe loading
# ══════════════════════════════════════════════════════════════════════

def load_probes(probe_path: str | None = None) -> list[dict]:
    """Load binding chain probes from JSON."""
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "binding_chain_probes.json")

    path = Path(probe_path)
    if not path.exists():
        print(f"ERROR: Probe file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        probes = json.load(f)

    # Count categories
    cats: dict[str, int] = {}
    for p in probes:
        cat = p["axis"].split("/")[0]
        cats[cat] = cats.get(cat, 0) + 1

    print(f"  Loaded {len(probes)} probes from {path.name}:", file=sys.stderr, flush=True)
    for c, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"    {c:12s}: {n:3d}", file=sys.stderr, flush=True)

    return probes


# ══════════════════════════════════════════════════════════════════════
# Depth mapping
# ══════════════════════════════════════════════════════════════════════

def get_target_layers(n_layers: int, depth_fractions: list[float]) -> list[int]:
    """Map relative depth fractions to absolute layer indices."""
    layers = []
    for frac in depth_fractions:
        layer = int(round(frac * (n_layers - 1)))
        layer = min(layer, n_layers - 1)
        layers.append(layer)
    seen = set()
    unique = []
    for l in layers:
        if l not in seen:
            seen.add(l)
            unique.append(l)
    return unique


# ══════════════════════════════════════════════════════════════════════
# RDM extraction — per model
# ══════════════════════════════════════════════════════════════════════

def extract_rdm(
    model_key: str,
    probes: list[dict],
    depth_fractions: list[float],
    device: str = "mps",
) -> dict[float, np.ndarray]:
    """Extract cosine-similarity RDM from one model at each depth fraction."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model = MODELS[model_key]
    target_layers = get_target_layers(n_layers, depth_fractions)

    layer_to_frac: dict[int, float] = {}
    for frac in depth_fractions:
        layer = int(round(frac * (n_layers - 1)))
        layer = min(layer, n_layers - 1)
        layer_to_frac[layer] = frac

    print(f"\n  ─── {model_key} ({model_name}) ───", file=sys.stderr, flush=True)
    print(f"  Layers: {n_layers}, d_model: {d_model}", file=sys.stderr, flush=True)
    print(f"  Target layers ({len(target_layers)}): {target_layers}",
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

    # Find transformer layers
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
    elif hasattr(model, 'transformer') and hasattr(model.transformer, 'h'):
        layers = model.transformer.h
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
    else:
        raise ValueError(f"Cannot find transformer layers for {model_key}")

    hidden_captures: dict[int, list] = {li: [] for li in target_layers}
    hooks = []

    for li in target_layers:
        def make_hook(layer_idx):
            def hook_fn(module, input, output):
                if isinstance(output, tuple):
                    h = output[0]
                else:
                    h = output
                hidden_captures[layer_idx].append(
                    h[:, -1, :].detach().cpu().float()
                )
            return hook_fn
        h = layers[li].register_forward_hook(make_hook(li))
        hooks.append(h)

    print(f"  Running {len(probes)} probes...", file=sys.stderr, flush=True)
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(
            probe["prompt"], return_tensors="pt"
        ).to(device)
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 50 == 0:
            print(f"    {i+1}/{len(probes)} probes done...",
                  file=sys.stderr, flush=True)
    dt = time.time() - t0
    print(f"  Done in {dt:.1f}s ({dt/len(probes)*1000:.1f}ms/probe)",
          file=sys.stderr, flush=True)

    for h in hooks:
        h.remove()

    # Build RDMs
    rdms = {}
    for li in target_layers:
        hs = torch.cat(hidden_captures[li], dim=0).numpy()
        norms = np.linalg.norm(hs, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-8)
        hs_norm = hs / norms
        rdm = hs_norm @ hs_norm.T
        frac = layer_to_frac.get(li, li / (n_layers - 1))
        rdms[frac] = rdm
        print(f"  L{li} (depth={frac:.0%}): RDM {rdm.shape}, "
              f"mean_sim={rdm.mean():.4f}", file=sys.stderr, flush=True)

    del model, tokenizer
    gc.collect()
    try:
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        elif torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        pass

    return rdms


# ══════════════════════════════════════════════════════════════════════
# Consensus building
# ══════════════════════════════════════════════════════════════════════

def build_consensus(
    all_rdms: dict[str, dict[float, np.ndarray]],
    depth_fractions: list[float],
) -> dict[float, dict]:
    """Build cross-model consensus RDM at each depth."""
    results = {}

    for frac in depth_fractions:
        model_rdms = []
        model_keys = []
        for model_key, rdms in all_rdms.items():
            if frac in rdms:
                model_rdms.append(rdms[frac])
                model_keys.append(model_key)

        if len(model_rdms) < 2:
            print(f"  Depth {frac:.0%}: only {len(model_rdms)} models, skipping",
                  file=sys.stderr, flush=True)
            continue

        stacked = np.stack(model_rdms)
        n_models = stacked.shape[0]
        n_probes = stacked.shape[1]

        consensus_rdm = stacked.mean(axis=0)
        consensus_rdm_centered = consensus_rdm - consensus_rdm.mean()
        np.fill_diagonal(consensus_rdm_centered, 0.0)

        cross_std = stacked.std(axis=0)
        max_std = cross_std.max() if cross_std.max() > 0 else 1.0
        agreement_mask = 1.0 - (cross_std / max_std)

        triu_idx = np.triu_indices(n_probes, k=1)
        model_correlations = {}
        for i in range(n_models):
            for j in range(i + 1, n_models):
                v1 = stacked[i][triu_idx]
                v2 = stacked[j][triu_idx]
                corr = np.corrcoef(v1, v2)[0, 1]
                model_correlations[f"{model_keys[i]}_vs_{model_keys[j]}"] = float(corr)

        mean_agreement = float(agreement_mask[triu_idx].mean())
        mean_model_corr = float(np.mean(list(model_correlations.values())))

        stats = {
            "n_models": n_models,
            "n_probes": n_probes,
            "model_keys": model_keys,
            "mean_agreement": mean_agreement,
            "mean_model_correlation": mean_model_corr,
            "model_correlations": model_correlations,
        }

        print(f"  Depth {frac:.0%}: {n_models} models, "
              f"agreement={mean_agreement:.4f}, "
              f"model_corr={mean_model_corr:.4f}",
              file=sys.stderr, flush=True)

        results[frac] = {
            "consensus_rdm": consensus_rdm_centered,
            "consensus_rdm_raw": consensus_rdm,
            "agreement_mask": agreement_mask,
            "stats": stats,
        }

    return results


# ══════════════════════════════════════════════════════════════════════
# SVD — discover universal dimensions per depth
# ══════════════════════════════════════════════════════════════════════

def discover_dimensions(
    consensus_rdm: np.ndarray,
    agreement_mask: np.ndarray,
    min_explained_variance: float = 0.02,
) -> dict:
    """SVD on agreement-weighted consensus RDM."""
    weighted_rdm = consensus_rdm * agreement_mask
    U, S, Vt = np.linalg.svd(weighted_rdm, full_matrices=False)
    explained = (S ** 2) / (S ** 2).sum()
    n_dims = max(int((explained >= min_explained_variance).sum()), 1)
    cumvar = np.cumsum(explained)

    print(f"  SVD: {n_dims} dims (cum var: {cumvar[n_dims-1]:.1%})",
          file=sys.stderr, flush=True)

    return {
        "n_dimensions": n_dims,
        "components": U[:, :n_dims],
        "singular_values": S[:n_dims],
        "explained_variance_ratio": explained[:n_dims],
        "cumulative_variance": cumvar[:n_dims],
    }


# ══════════════════════════════════════════════════════════════════════
# Binding cascade analysis — the core new analysis
# ══════════════════════════════════════════════════════════════════════

def analyze_binding_cascade(
    consensus_results: dict[float, dict],
    probes: list[dict],
) -> dict:
    """Analyze the C→B/S→WHNF cascade across depth fractions.

    For each depth fraction, measures:
      - Which combinator dominates for each binding depth level
      - Agreement scores for the binding→combinator links
      - Where the WHNF transition occurs
      - Chain probe activation patterns
    """

    def get_sub(axis: str) -> str:
        return axis.split("/", 1)[1] if "/" in axis else axis

    # Index probes by category
    pure_idx: dict[str, int] = {}
    for i, p in enumerate(probes):
        if p["axis"].startswith("pure/"):
            pure_idx[get_sub(p["axis"])] = i

    combinator_order = ["K", "I", "B", "C", "D", "S", "W", "Y", "WHNF"]

    # Group chain probes by type
    chain_groups: dict[str, list[int]] = {}
    for i, p in enumerate(probes):
        ax = p["axis"]
        if ax.startswith("chain/"):
            sub = get_sub(ax)
            # Group by prefix
            if sub.startswith("I_"): key = "chain_I"
            elif sub.startswith("K_") or sub == "K_after_I": key = "chain_K"
            elif sub.startswith("C_route") or sub.startswith("C_flip") or sub == "C_mechanism_explicit" or sub == "C_as_router_prose": key = "chain_C"
            elif sub.startswith("B_compose") or sub.startswith("B_carry") or sub == "B_as_threading_prose": key = "chain_B"
            elif sub.startswith("S_") or sub == "S_as_fork_prose" or sub == "S_carry_and_fork": key = "chain_S"
            elif sub.startswith("reduce_") or sub.startswith("trace_"): key = "chain_reduce"
            elif sub.startswith("whnf_") or sub == "WHNF_by_exhaustion_prose": key = "chain_WHNF"
            elif sub.startswith("depth"): key = "chain_depth"
            elif sub.startswith("shadow") or sub.startswith("closure") or sub.startswith("mutual"): key = "chain_scope"
            elif sub.startswith("let_"): key = "chain_let"
            elif sub.startswith("map_") or sub.startswith("fold_") or sub.startswith("filter_"): key = "chain_hof"
            elif sub.startswith("substitution") or sub.startswith("capture") or sub.startswith("debruijn"): key = "chain_mechanism"
            elif sub.startswith("mechanism"): key = "chain_mechanism"
            else: key = f"chain_{sub}"
            chain_groups.setdefault(key, []).append(i)
        elif ax.startswith("existing/bind_depth_"):
            # Existing binding depth probes — group by depth level
            # axis format: existing/bind_depth_1a, existing/bind_depth_2b, etc.
            sub = get_sub(ax)  # "bind_depth_1a"
            parts = sub.split("_")  # ["bind", "depth", "1a"]
            if len(parts) >= 3 and parts[2][0].isdigit():
                level = parts[2][0]  # "1" from "1a"
                chain_groups.setdefault(f"bind_depth_{level}", []).append(i)

    analysis = {
        "combinator_order": combinator_order,
        "depth_fractions": sorted(consensus_results.keys()),
        "cascade": {},  # depth_frac → binding_depth → combinator_profile
        "chain_activation": {},  # depth_frac → chain_group → combinator_profile
        "whnf_transition": {},  # binding_depth → depth_frac where WHNF > all others
        "handoff_points": {},  # C→B handoff, B→WHNF handoff per depth fraction
    }

    for frac in sorted(consensus_results.keys()):
        rdm = consensus_results[frac]["consensus_rdm"]
        agr = consensus_results[frac]["agreement_mask"]

        # ── Binding depth → combinator profile ────────────────
        cascade_at_depth = {}
        for level in range(1, 6):
            group_key = f"bind_depth_{level}"
            indices = chain_groups.get(group_key, [])
            if not indices:
                continue

            profile = {}
            for c in combinator_order:
                if c not in pure_idx:
                    continue
                ci = pure_idx[c]
                sims = [float(rdm[bi, ci]) for bi in indices]
                agrs = [float(agr[bi, ci]) for bi in indices]
                profile[c] = {
                    "sim": float(np.mean(sims)),
                    "agree": float(np.mean(agrs)),
                }

            # Find winner
            if profile:
                winner = max(profile.keys(), key=lambda c: profile[c]["sim"])
                profile["_winner"] = winner
                profile["_winner_sim"] = profile[winner]["sim"]
                profile["_winner_agree"] = profile[winner]["agree"]

            cascade_at_depth[level] = profile

        analysis["cascade"][f"{frac:.2f}"] = cascade_at_depth

        # ── Chain group → combinator profile ──────────────────
        chain_at_depth = {}
        for group_name, indices in sorted(chain_groups.items()):
            if not group_name.startswith("chain_"):
                continue
            if not indices:
                continue

            profile = {}
            for c in combinator_order:
                if c not in pure_idx:
                    continue
                ci = pure_idx[c]
                sims = [float(rdm[bi, ci]) for bi in indices]
                agrs = [float(agr[bi, ci]) for bi in indices]
                profile[c] = {
                    "sim": float(np.mean(sims)),
                    "agree": float(np.mean(agrs)),
                }

            if profile:
                winner = max(profile.keys(), key=lambda c: profile[c]["sim"])
                profile["_winner"] = winner

            chain_at_depth[group_name] = profile

        analysis["chain_activation"][f"{frac:.2f}"] = chain_at_depth

    # ── Find handoff points ───────────────────────────────────
    # For each binding depth, track where C drops below B/S and where WHNF rises
    for level in range(1, 6):
        transitions = []
        for frac in sorted(consensus_results.keys()):
            frac_key = f"{frac:.2f}"
            cascade = analysis["cascade"].get(frac_key, {})
            if level not in cascade:
                continue
            profile = cascade[level]
            c_sim = profile.get("C", {}).get("sim", 0)
            b_sim = profile.get("B", {}).get("sim", 0)
            s_sim = profile.get("S", {}).get("sim", 0)
            whnf_sim = profile.get("WHNF", {}).get("sim", 0)
            winner = profile.get("_winner", "?")
            transitions.append({
                "depth_frac": frac,
                "C": c_sim,
                "B": b_sim,
                "S": s_sim,
                "WHNF": whnf_sim,
                "winner": winner,
            })
        analysis["handoff_points"][f"bind_depth_{level}"] = transitions

    return analysis


def print_cascade_analysis(analysis: dict, probes: list[dict]) -> None:
    """Print human-readable cascade analysis."""
    combinator_order = analysis["combinator_order"]

    print("\n" + "=" * 90, file=sys.stderr, flush=True)
    print("  BINDING CASCADE ANALYSIS: C → B/S → WHNF", file=sys.stderr, flush=True)
    print("=" * 90, file=sys.stderr, flush=True)

    # ── Table: binding depth × model depth → winner ──────────
    print("\n  Binding Depth × Model Depth → Dominant Combinator", file=sys.stderr, flush=True)
    print(f"  {'bind':>6s}", end='', file=sys.stderr)
    for frac in analysis["depth_fractions"]:
        print(f"  {frac:>6.0%}", end='', file=sys.stderr)
    print(file=sys.stderr, flush=True)
    print("  " + "-" * (8 + 8 * len(analysis["depth_fractions"])), file=sys.stderr, flush=True)

    for level in range(1, 6):
        print(f"  d={level:3d} ", end='', file=sys.stderr)
        for frac in analysis["depth_fractions"]:
            frac_key = f"{frac:.2f}"
            cascade = analysis["cascade"].get(frac_key, {})
            if level in cascade:
                winner = cascade[level].get("_winner", "?")
                sim = cascade[level].get("_winner_sim", 0)
                print(f"  {winner:>4s}{sim:+.1f}"[:8].ljust(8), end='', file=sys.stderr)
            else:
                print(f"  {'?':>6s}", end='', file=sys.stderr)
        print(file=sys.stderr, flush=True)

    # ── Handoff points ────────────────────────────────────────
    print("\n\n  Handoff Trajectories (sim to C, B, S, WHNF across depth):", file=sys.stderr, flush=True)
    for level in range(1, 6):
        transitions = analysis["handoff_points"].get(f"bind_depth_{level}", [])
        if not transitions:
            continue
        print(f"\n  bind_depth={level}:", file=sys.stderr, flush=True)
        print(f"    {'depth':>6s}  {'C':>7s}  {'B':>7s}  {'S':>7s}  {'WHNF':>7s}  {'winner':>6s}",
              file=sys.stderr, flush=True)
        for t in transitions:
            print(f"    {t['depth_frac']:>6.0%}  {t['C']:+.4f}  {t['B']:+.4f}  "
                  f"{t['S']:+.4f}  {t['WHNF']:+.4f}  {t['winner']:>6s}",
                  file=sys.stderr, flush=True)

    # ── Chain probe activation ────────────────────────────────
    print("\n\n  Chain Probe Groups → Dominant Combinator (at depth 50%):", file=sys.stderr, flush=True)
    mid_key = None
    for fk in analysis["depth_fractions"]:
        if abs(fk - 0.5) < 0.05:
            mid_key = f"{fk:.2f}"
            break
    if mid_key and mid_key in analysis["chain_activation"]:
        chain_at_mid = analysis["chain_activation"][mid_key]
        print(f"    {'group':>20s}  {'winner':>6s}  {'K':>6s}  {'C':>6s}  {'B':>6s}  {'S':>6s}  {'WHNF':>6s}",
              file=sys.stderr, flush=True)
        print("    " + "-" * 70, file=sys.stderr, flush=True)
        for group_name in sorted(chain_at_mid.keys()):
            profile = chain_at_mid[group_name]
            winner = profile.get("_winner", "?")
            k = profile.get("K", {}).get("sim", 0)
            c = profile.get("C", {}).get("sim", 0)
            b = profile.get("B", {}).get("sim", 0)
            s = profile.get("S", {}).get("sim", 0)
            w = profile.get("WHNF", {}).get("sim", 0)
            print(f"    {group_name:>20s}  {winner:>6s}  {k:+.3f}  {c:+.3f}  "
                  f"{b:+.3f}  {s:+.3f}  {w:+.3f}",
                  file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════════════

def save_lattice(
    consensus_results: dict[float, dict],
    dimension_results: dict[float, dict],
    analysis: dict,
    probes: list[dict],
    all_rdms: dict[str, dict[float, np.ndarray]],
    output_dir: Path,
    model_keys: list[str],
) -> None:
    """Save binding lattice results."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── NPZ: consensus data ───────────────────────────────────
    npz_data = {}
    for frac, result in consensus_results.items():
        key = f"depth_{frac:.2f}"
        npz_data[f"{key}_consensus_rdm"] = result["consensus_rdm"].astype(np.float32)
        npz_data[f"{key}_agreement_mask"] = result["agreement_mask"].astype(np.float32)
        if frac in dimension_results:
            dims = dimension_results[frac]
            npz_data[f"{key}_components"] = dims["components"].astype(np.float32)
            npz_data[f"{key}_singular_values"] = dims["singular_values"].astype(np.float32)
            npz_data[f"{key}_explained_variance"] = dims["explained_variance_ratio"].astype(np.float32)

    npz_path = output_dir / "universal_lattice.npz"
    np.savez_compressed(str(npz_path), **npz_data)
    print(f"\n  💾 NPZ: {npz_path} ({npz_path.stat().st_size / 1024:.1f} KB)",
          file=sys.stderr, flush=True)

    # ── Per-model RDMs (for debugging / model-specific analysis) ──
    for model_key, rdms in all_rdms.items():
        model_npz = {}
        for frac, rdm in rdms.items():
            model_npz[f"depth_{frac:.2f}_rdm"] = rdm.astype(np.float32)
        model_path = output_dir / f"rdm_{model_key}.npz"
        np.savez_compressed(str(model_path), **model_npz)
        print(f"  💾 Per-model: {model_path} ({model_path.stat().st_size / 1024:.1f} KB)",
              file=sys.stderr, flush=True)

    # ── JSON: metadata + analysis ─────────────────────────────
    json_data = {
        "description": "Binding lattice — fine-grained depth exploration of C→B/S→WHNF cascade",
        "n_probes": len(probes),
        "n_models": len(model_keys),
        "model_keys": model_keys,
        "models": {k: MODELS[k][0] for k in model_keys if k in MODELS},
        "depth_fractions": sorted(consensus_results.keys()),
        "probes": [{k: v for k, v in p.items() if k != "note"} for p in probes],
        "depths": {},
        "binding_cascade_analysis": analysis,
    }

    for frac in sorted(consensus_results.keys()):
        stats = consensus_results[frac]["stats"]
        depth_info = {"stats": stats}
        if frac in dimension_results:
            dims = dimension_results[frac]
            depth_info["n_dimensions"] = dims["n_dimensions"]
            depth_info["explained_variance_ratio"] = [
                float(v) for v in dims["explained_variance_ratio"]
            ]
        json_data["depths"][f"{frac:.2f}"] = depth_info

    json_path = output_dir / "universal_lattice.json"
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)
    print(f"  💾 JSON: {json_path}", file=sys.stderr, flush=True)

    # ── Also save v12-compat format ───────────────────────────
    compat_data = {
        "n_probes": len(probes),
        "probes": [{k: v for k, v in p.items() if k != "note"} for p in probes],
        "targets": {},
        "source": "binding lattice — cross-model consensus",
        "n_models": len(model_keys),
        "model_keys": model_keys,
    }
    for frac, result in consensus_results.items():
        approx_layer = int(round(frac * 39))
        compat_data["targets"][str(approx_layer)] = {
            "rdm": result["consensus_rdm"].tolist(),
            "agreement_mask": result["agreement_mask"].tolist(),
            "n_probes": len(probes),
            "depth_fraction": frac,
        }
    compat_path = output_dir / "lattice_relational_target.json"
    with open(compat_path, "w") as f:
        json.dump(compat_data, f)
    print(f"  💾 Compat: {compat_path}", file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Build binding lattice — fine-grained depth exploration"
    )
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()),
                        help=f"Models to use (default: {DEFAULT_MODELS})")
    parser.add_argument("--probes", type=str, default=None,
                        help="Path to probe JSON (default: lattice/binding_chain_probes.json)")
    parser.add_argument("--output-dir", type=str, default="lattice/binding-v1",
                        help="Output directory (default: lattice/binding-v1/)")
    parser.add_argument("--device", type=str, default="mps",
                        help="Device for model inference")
    parser.add_argument("--depth-fractions", nargs="+", type=float,
                        default=None,
                        help="Override depth fractions (default: 0%% to 90%% by 10%%)")

    args = parser.parse_args()
    depth_fractions = args.depth_fractions or BINDING_DEPTH_FRACTIONS

    print("=" * 72, file=sys.stderr, flush=True)
    print("  Binding Lattice — C→B/S→WHNF Cascade Exploration", file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print(f"  Depths: {[f'{d:.0%}' for d in depth_fractions]}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t_start = time.time()

    # ── Load probes ───────────────────────────────────────────
    print("\n1. Loading probes...", file=sys.stderr, flush=True)
    probes = load_probes(args.probes)

    # ── Extract RDMs ──────────────────────────────────────────
    print("\n2. Extracting per-model RDMs...", file=sys.stderr, flush=True)
    all_rdms: dict[str, dict[float, np.ndarray]] = {}
    for model_key in args.models:
        if model_key not in MODELS:
            print(f"  WARNING: Unknown model {model_key}, skipping",
                  file=sys.stderr, flush=True)
            continue
        rdms = extract_rdm(model_key, probes, depth_fractions, args.device)
        all_rdms[model_key] = rdms

    if len(all_rdms) < 2:
        print("ERROR: Need at least 2 models for consensus.",
              file=sys.stderr, flush=True)
        sys.exit(1)

    # ── Build consensus ───────────────────────────────────────
    print("\n3. Building cross-model consensus...", file=sys.stderr, flush=True)
    consensus_results = build_consensus(all_rdms, depth_fractions)

    # ── SVD ────────────────────────────────────────────────────
    print("\n4. Discovering universal dimensions...", file=sys.stderr, flush=True)
    dimension_results = {}
    for frac, result in sorted(consensus_results.items()):
        print(f"\n  Depth {frac:.0%}:", file=sys.stderr, flush=True)
        dims = discover_dimensions(
            result["consensus_rdm"],
            result["agreement_mask"],
        )
        dimension_results[frac] = dims

    # ── Binding cascade analysis ──────────────────────────────
    print("\n5. Analyzing binding cascade...", file=sys.stderr, flush=True)
    analysis = analyze_binding_cascade(consensus_results, probes)

    # ── Save first (expensive data already computed) ──────────
    print("\n6. Saving results...", file=sys.stderr, flush=True)
    output_dir = Path(args.output_dir)
    save_lattice(
        consensus_results, dimension_results, analysis,
        probes, all_rdms, output_dir, list(all_rdms.keys()),
    )

    # ── Print analysis (after save, so crash here doesn't lose data)
    print_cascade_analysis(analysis, probes)

    elapsed = time.time() - t_start
    print(f"\n{'='*72}", file=sys.stderr, flush=True)
    print(f"  Binding Lattice Complete", file=sys.stderr, flush=True)
    print(f"  Models: {len(all_rdms)}", file=sys.stderr, flush=True)
    print(f"  Probes: {len(probes)}", file=sys.stderr, flush=True)
    print(f"  Depths: {len(consensus_results)} ({len(depth_fractions)} requested)",
          file=sys.stderr, flush=True)
    for frac in sorted(consensus_results.keys()):
        s = consensus_results[frac]["stats"]
        d = dimension_results.get(frac, {})
        print(f"    {frac:.0%}: agreement={s['mean_agreement']:.4f}, "
              f"model_corr={s['mean_model_correlation']:.4f}, "
              f"dims={d.get('n_dimensions', '?')}",
              file=sys.stderr, flush=True)
    print(f"  Elapsed: {elapsed:.0f}s", file=sys.stderr, flush=True)
    print(f"  Output: {output_dir}/", file=sys.stderr, flush=True)
    print(f"{'='*72}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
