"""Analyze crystal structure and compression across V12 distill checkpoints.

Compares ternary plate topology, mirror differentiation, combinator
embedding geometry, and gamma statistics between checkpoints to understand
why φ-compression propagated while eval loss plateaued.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/analyze_crystal_compression.py

License: MIT
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.utils import tree_flatten

sys.path.insert(0, str(Path(__file__).parent))

from config import V12Config
from model import V12Model, create_model, compute_crystal_diagnostics
from ternary import TernaryLinear, TernaryMirror, TernaryEmbedding, unpack_ternary_mlx
from kernel_dispatch import N_COMBINATORS, COMBINATOR_NAMES


# ══════════════════════════════════════════════════════════════════════
# Plate topology analysis
# ══════════════════════════════════════════════════════════════════════

def analyze_ternary_plates(model: V12Model) -> dict:
    """Analyze all ternary weight matrices in the model.

    For each TernaryLinear / TernaryMirror:
      - sparsity: fraction of zeros (higher = more selective)
      - polarity: balance of +1 vs -1 (0 = balanced)
      - gamma stats: learned magnitude scaling

    Returns dict of per-module and aggregate statistics.
    """
    modules = {}
    all_sparsities = []
    all_polarities = []
    all_gamma_means = []
    all_gamma_stds = []
    all_sizes = []

    for name, module in model.named_modules():
        if isinstance(module, (TernaryLinear, TernaryMirror)):
            w = unpack_ternary_mlx(module.weight)  # int8 {-1, 0, +1}
            mx.eval(w)
            total = float(w.size)
            n_zero = float((w == 0).sum().item())
            n_pos = float((w == 1).sum().item())
            n_neg = float((w == -1).sum().item())

            sparsity = n_zero / total
            n_nonzero = n_pos + n_neg
            polarity = (n_pos - n_neg) / max(n_nonzero, 1)

            gamma_mean = gamma_std = None
            if hasattr(module, 'gamma'):
                g = module.gamma
                mx.eval(g)
                gamma_mean = float(mx.mean(g).item())
                gamma_std = float(mx.var(g).item() ** 0.5)
                all_gamma_means.append(gamma_mean)
                all_gamma_stds.append(gamma_std)

            modules[name] = {
                "shape": list(w.shape),
                "total_weights": int(total),
                "sparsity": sparsity,
                "polarity": polarity,
                "n_pos": int(n_pos),
                "n_neg": int(n_neg),
                "n_zero": int(n_zero),
                "gamma_mean": gamma_mean,
                "gamma_std": gamma_std,
            }
            all_sparsities.append(sparsity)
            all_polarities.append(abs(polarity))
            all_sizes.append(int(total))

            del w

    mx.clear_cache()

    return {
        "per_module": modules,
        "aggregate": {
            "n_ternary_modules": len(modules),
            "mean_sparsity": np.mean(all_sparsities),
            "std_sparsity": np.std(all_sparsities),
            "mean_abs_polarity": np.mean(all_polarities),
            "std_abs_polarity": np.std(all_polarities),
            "mean_gamma_mean": np.mean(all_gamma_means) if all_gamma_means else None,
            "mean_gamma_std": np.mean(all_gamma_stds) if all_gamma_stds else None,
            "total_ternary_weights": sum(all_sizes),
        },
    }


# ══════════════════════════════════════════════════════════════════════
# Combinator embedding analysis
# ══════════════════════════════════════════════════════════════════════

def analyze_combinator_embeddings(model: V12Model) -> dict:
    """Analyze the 8 combinator embeddings in dispatch.

    Measures:
    - Pairwise cosine matrix (the crystal lattice)
    - Norms (magnitude differentiation)
    - Cluster structure: {K,I,B,C} vs {D,Y,W,WHNF}
    """
    dispatch = model.combinator_dispatch
    if not hasattr(dispatch, 'combinator_embeddings'):
        return {}

    emb = dispatch.combinator_embeddings  # (n_comb, d_model)
    mx.eval(emb)

    n = emb.shape[0]
    norms = mx.sqrt(mx.sum(emb * emb, axis=-1) + 1e-8)
    mx.eval(norms)
    emb_normed = emb / norms[:, None]

    cosine = emb_normed @ emb_normed.T
    mx.eval(cosine)

    # Extract as numpy
    cos_np = np.array(cosine.tolist())
    norms_np = np.array([float(norms[i].item()) for i in range(n)])

    names = COMBINATOR_NAMES[:n]

    # Pairwise cosines (upper triangle)
    pairwise = {}
    for i in range(n):
        for j in range(i + 1, n):
            pairwise[f"{names[i]}_{names[j]}"] = float(cos_np[i, j])

    # Cluster analysis: compositional {K,I,B,C} vs reduction {D,Y,W,WHNF}
    comp_idx = [i for i, nm in enumerate(names) if nm in {"K", "I", "B", "C"}]
    red_idx = [i for i, nm in enumerate(names) if nm in {"D", "Y", "W", "WHNF"}]

    within_comp = []
    within_red = []
    between = []
    for i in range(n):
        for j in range(i + 1, n):
            val = cos_np[i, j]
            if i in comp_idx and j in comp_idx:
                within_comp.append(val)
            elif i in red_idx and j in red_idx:
                within_red.append(val)
            else:
                between.append(val)

    return {
        "pairwise_cosines": pairwise,
        "norms": {names[i]: float(norms_np[i]) for i in range(n)},
        "cluster_analysis": {
            "within_compositional_mean_cos": float(np.mean(within_comp)) if within_comp else None,
            "within_reduction_mean_cos": float(np.mean(within_red)) if within_red else None,
            "between_cluster_mean_cos": float(np.mean(between)) if between else None,
        },
        "full_cosine_matrix": cos_np.tolist(),
    }

    del emb, norms, emb_normed, cosine
    mx.clear_cache()


# ══════════════════════════════════════════════════════════════════════
# Plate-to-plate diff (topology change between checkpoints)
# ══════════════════════════════════════════════════════════════════════

def diff_ternary_plates(model_a: V12Model, model_b: V12Model) -> dict:
    """Compare ternary topology between two model checkpoints.

    For each shared TernaryLinear/TernaryMirror:
    - fraction of positions that changed sign
    - fraction that went zero→nonzero or nonzero→zero
    - fraction that flipped polarity (-1↔+1)
    """
    diffs = {}
    total_changed = 0
    total_weights = 0

    modules_a = {n: m for n, m in model_a.named_modules()
                 if isinstance(m, (TernaryLinear, TernaryMirror))}
    modules_b = {n: m for n, m in model_b.named_modules()
                 if isinstance(m, (TernaryLinear, TernaryMirror))}

    for name in modules_a:
        if name not in modules_b:
            continue

        wa = unpack_ternary_mlx(modules_a[name].weight)
        wb = unpack_ternary_mlx(modules_b[name].weight)
        mx.eval(wa, wb)

        total = float(wa.size)
        changed = float((wa != wb).sum().item())

        # Break down changes
        flip = float(((wa == 1) & (wb == -1)).sum().item()) + \
               float(((wa == -1) & (wb == 1)).sum().item())
        zero_to_nonzero = float(((wa == 0) & (wb != 0)).sum().item())
        nonzero_to_zero = float(((wa != 0) & (wb == 0)).sum().item())

        diffs[name] = {
            "total": int(total),
            "changed": int(changed),
            "frac_changed": changed / total,
            "polarity_flips": int(flip),
            "frac_polarity_flip": flip / total,
            "zero_to_nonzero": int(zero_to_nonzero),
            "nonzero_to_zero": int(nonzero_to_zero),
        }

        total_changed += changed
        total_weights += total

        del wa, wb

    mx.clear_cache()

    return {
        "per_module": diffs,
        "aggregate": {
            "total_weights": int(total_weights),
            "total_changed": int(total_changed),
            "frac_changed": total_changed / max(total_weights, 1),
        },
    }


# ══════════════════════════════════════════════════════════════════════
# Compression function analysis
# ══════════════════════════════════════════════════════════════════════

def analyze_compression_function(model: V12Model, data_dir: str, n_batches: int = 5) -> dict:
    """Run forward passes and measure per-pass entropy compression.

    Uses forward_instrumented to get pass_compression and pass_phi_dev
    plus crystal diagnostics from compute_crystal_diagnostics.
    """
    from data import ShardedDataLoader

    loader = ShardedDataLoader(
        data_dir=data_dir,
        batch_size=2,
        seq_len=512,  # shorter for analysis
        shard_start=54,  # eval shards
        shard_end=60,
        seed=123,
    )

    all_compression = []
    all_phi_dev = []
    all_s3_gates = []
    all_s5_reweight = []
    dispatch_accum = None

    for batch_idx in range(n_batches):
        ids_np, _ = loader.next_batch()
        ids = mx.array(ids_np)

        _, metrics = model.forward_instrumented(ids)
        mx.eval(model.parameters())

        all_compression.append(metrics["pass_compression"])
        all_phi_dev.append(metrics["pass_phi_dev"])

        if metrics.get("s3_gates"):
            all_s3_gates.append(metrics["s3_gates"])
        if metrics.get("s5_reweight"):
            all_s5_reweight.append(metrics["s5_reweight"])

        dw = metrics.get("combinator_dispatch_weights")
        if dw is not None:
            if dispatch_accum is None:
                dispatch_accum = np.array(dw)
            else:
                dispatch_accum += np.array(dw)

        del ids
        mx.clear_cache()

    pass_names = ["L0↑", "L1↑", "L2↑", "apex", "L2↓", "L1↓", "L0↓"]
    inv_phi = 1.0 / ((1 + 5 ** 0.5) / 2)

    compression = np.array(all_compression)  # (n_batches, 7)
    phi_dev = np.array(all_phi_dev)

    result = {
        "per_pass": {},
        "dispatch_weights": None,
    }

    for i, pname in enumerate(pass_names):
        result["per_pass"][pname] = {
            "mean_compression": float(compression[:, i].mean()),
            "std_compression": float(compression[:, i].std()),
            "mean_phi_dev": float(phi_dev[:, i].mean()),
            "at_phi": bool(phi_dev[:, i].mean() < 0.05),
            "target": inv_phi,
        }

    if dispatch_accum is not None:
        dispatch_mean = dispatch_accum / n_batches
        result["dispatch_weights"] = {
            COMBINATOR_NAMES[i]: float(dispatch_mean[i])
            for i in range(len(dispatch_mean))
        }

    if all_s3_gates:
        s3 = np.array(all_s3_gates)
        result["s3_gates_mean"] = {
            pass_names[i]: float(s3[:, i].mean())
            for i in range(min(s3.shape[1], 7))
        }

    if all_s5_reweight:
        s5 = np.array(all_s5_reweight)
        result["s5_reweight_mean"] = {
            pass_names[i]: float(s5[:, i].mean())
            for i in range(min(s5.shape[1], 7))
        }

    return result


# ══════════════════════════════════════════════════════════════════════
# Grouped analysis: which components changed most?
# ══════════════════════════════════════════════════════════════════════

def group_plate_analysis(plate_stats: dict) -> dict:
    """Group ternary plate stats by component type.

    Groups: stride_stack, combinator_dispatch, combinator_integrate,
    mod_projs, s4, embed/pos_embed, other
    """
    groups = {
        "stride_stack": [],
        "combinator_dispatch": [],
        "combinator_integrate": [],
        "mod_projs": [],
        "s4": [],
        "embed": [],
        "other": [],
    }

    for name, stats in plate_stats["per_module"].items():
        found = False
        for grp in groups:
            if grp in name:
                groups[grp].append((name, stats))
                found = True
                break
        if not found:
            groups["other"].append((name, stats))

    summary = {}
    for grp, entries in groups.items():
        if not entries:
            continue
        sparsities = [e[1]["sparsity"] for e in entries]
        polarities = [abs(e[1]["polarity"]) for e in entries]
        gammas = [e[1]["gamma_mean"] for e in entries if e[1]["gamma_mean"] is not None]
        summary[grp] = {
            "n_modules": len(entries),
            "total_weights": sum(e[1]["total_weights"] for e in entries),
            "mean_sparsity": float(np.mean(sparsities)),
            "mean_abs_polarity": float(np.mean(polarities)),
            "mean_gamma": float(np.mean(gammas)) if gammas else None,
            "std_gamma": float(np.std(gammas)) if gammas else None,
        }

    return summary


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def load_model_from_checkpoint(weights_path: str) -> V12Model:
    """Create V12Model and load weights from checkpoint."""
    cfg = V12Config()
    cfg.seq_len = 512
    model = create_model(cfg)
    weights = mx.load(weights_path)
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())
    return model


def main():
    base = Path("/Users/mwhitford/src/verbum")
    data_dir = "/Users/mwhitford/data/fractal-bitnet/shards-qwen3"
    output_dir = base / "results" / "crystal-compression-analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    checkpoints = {
        "best_step5000": base / "checkpoints/v12-distill-run2/best/weights.npz",
        "step_12000": base / "checkpoints/v12-distill-run2/step_012000/weights.npz",
    }

    # Also include step 2000 and step 8000 for trajectory
    for step in [2000, 8000]:
        p = base / f"checkpoints/v12-distill-run2/step_{step:06d}/weights.npz"
        if p.exists():
            checkpoints[f"step_{step}"] = p

    results = {}

    # ── Analyze each checkpoint ──────────────────────────────
    models = {}
    for label, path in sorted(checkpoints.items()):
        print(f"\n{'='*60}")
        print(f"  Analyzing: {label}")
        print(f"  Weights:   {path}")
        print(f"{'='*60}")

        model = load_model_from_checkpoint(str(path))
        models[label] = model

        # 1. Plate topology
        print("  ▸ Ternary plate topology...")
        plate_stats = analyze_ternary_plates(model)
        grouped = group_plate_analysis(plate_stats)

        # 2. Combinator embeddings
        print("  ▸ Combinator embedding geometry...")
        comb_stats = analyze_combinator_embeddings(model)

        # 3. Crystal diagnostics (mirror cosines, etc.)
        print("  ▸ Crystal diagnostics...")
        crystal = compute_crystal_diagnostics(model)

        # 4. Compression function (forward pass)
        print("  ▸ Compression function (5 batches)...")
        try:
            comp = analyze_compression_function(model, data_dir, n_batches=5)
        except Exception as e:
            print(f"    ⚠️  Compression analysis failed: {e}")
            comp = None

        results[label] = {
            "plate_aggregate": plate_stats["aggregate"],
            "plate_by_group": grouped,
            "combinator_embeddings": comb_stats,
            "crystal_diagnostics": crystal,
            "compression": comp,
        }

        # Print summary
        agg = plate_stats["aggregate"]
        print(f"\n  Plate topology:")
        print(f"    Modules: {agg['n_ternary_modules']}")
        print(f"    Weights: {agg['total_ternary_weights']:,}")
        print(f"    Sparsity: {agg['mean_sparsity']:.4f} ± {agg['std_sparsity']:.4f}")
        print(f"    |Polarity|: {agg['mean_abs_polarity']:.4f} ± {agg['std_abs_polarity']:.4f}")
        if agg['mean_gamma_mean'] is not None:
            print(f"    Gamma: {agg['mean_gamma_mean']:.4f} (std: {agg['mean_gamma_std']:.4f})")

        print(f"\n  Group breakdown:")
        for grp, gstats in sorted(grouped.items()):
            gamma_str = f", γ={gstats['mean_gamma']:.3f}±{gstats['std_gamma']:.3f}" \
                if gstats['mean_gamma'] is not None else ""
            print(f"    {grp:30s}: {gstats['n_modules']:3d} modules, "
                  f"sparse={gstats['mean_sparsity']:.3f}, "
                  f"|pol|={gstats['mean_abs_polarity']:.3f}"
                  f"{gamma_str}")

        if crystal:
            print(f"\n  Crystal formation:")
            if "crystal_formation_score" in crystal:
                print(f"    Score: {crystal['crystal_formation_score']:.4f}")
                print(f"    KBC plate cos: {crystal['crystal_kbc_plate_cos']:.4f}")
                print(f"    I separation: {crystal['crystal_i_separation_cos']:.4f}")
            if "dispatch_mirror_mean_cos" in crystal:
                print(f"    Dispatch mirror mean cos: {crystal['dispatch_mirror_mean_cos']:.4f} "
                      f"(range [{crystal['dispatch_mirror_min_cos']:.3f}, "
                      f"{crystal['dispatch_mirror_max_cos']:.3f}])")

        if comp:
            print(f"\n  Compression function (φ ≈ {1/((1+5**0.5)/2):.4f}):")
            for pname, pdata in comp["per_pass"].items():
                phi_mark = "←φ" if pdata["at_phi"] else "  "
                print(f"    {pname:6s}: {pdata['mean_compression']:.4f} "
                      f"± {pdata['std_compression']:.4f} "
                      f"(Δφ={pdata['mean_phi_dev']:.4f}) {phi_mark}")
            if comp.get("dispatch_weights"):
                dw = comp["dispatch_weights"]
                print(f"    Dispatch: " + " ".join(
                    f"{k}={v:.3f}" for k, v in dw.items()))

        mx.clear_cache()

    # ── Plate diff between checkpoints ────────────────────────
    print(f"\n{'='*60}")
    print(f"  Plate topology diffs")
    print(f"{'='*60}")

    diff_pairs = [
        ("step_2000", "best_step5000"),
        ("best_step5000", "step_8000"),
        ("step_8000", "step_12000"),
        ("best_step5000", "step_12000"),
    ]

    diff_results = {}
    for label_a, label_b in diff_pairs:
        if label_a in models and label_b in models:
            key = f"{label_a}_vs_{label_b}"
            print(f"\n  {label_a} → {label_b}:")
            diff = diff_ternary_plates(models[label_a], models[label_b])
            diff_results[key] = diff["aggregate"]

            agg = diff["aggregate"]
            print(f"    Changed: {agg['total_changed']:,} / {agg['total_weights']:,} "
                  f"({agg['frac_changed']*100:.2f}%)")

            # Group the diffs
            grp_changes = {}
            for name, d in diff["per_module"].items():
                found_grp = "other"
                for grp in ["stride_stack", "combinator_dispatch",
                            "combinator_integrate", "mod_projs", "s4", "embed"]:
                    if grp in name:
                        found_grp = grp
                        break
                if found_grp not in grp_changes:
                    grp_changes[found_grp] = {"changed": 0, "total": 0, "flips": 0}
                grp_changes[found_grp]["changed"] += d["changed"]
                grp_changes[found_grp]["total"] += d["total"]
                grp_changes[found_grp]["flips"] += d["polarity_flips"]

            for grp, gc in sorted(grp_changes.items()):
                pct = gc["changed"] / max(gc["total"], 1) * 100
                print(f"      {grp:30s}: {gc['changed']:7,} changed "
                      f"({pct:.2f}%), {gc['flips']:,} flips")

    results["plate_diffs"] = diff_results

    # ── Save results ─────────────────────────────────────────
    out_path = output_dir / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
