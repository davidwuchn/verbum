"""
probe_hologram.py — V12 holographic pattern probe

Asks: is V12 at 4K steps forming the same KIBC holographic sign patterns
observed in Qwen3/Pythia attention weights?

Usage:
    uv run python scripts/v12/probe_hologram.py checkpoints/v12-run1/step_004000
    uv run python scripts/v12/probe_hologram.py checkpoints/v12-run1/step_001000 \
        checkpoints/v12-run1/step_002000 checkpoints/v12-run1/step_003000 \
        checkpoints/v12-run1/step_004000
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJ_TYPES = ("q_proj", "k_proj", "v_proj", "out_proj")
COMBINATOR_NAMES = ["K", "I", "B", "C"]          # order in combinator_embeddings

# Reference thresholds from production LLM findings
REF_PLATE_SPARSITY = 0.75          # ~75% zeros — ternary-safe "plate" regime
REF_CLUSTER_COS    = 0.90          # K/B/C clustering threshold
REF_I_COS_LO       = 0.60          # I vs cluster — lower bound
REF_I_COS_HI       = 0.75          # I vs cluster — upper bound
N_SINGULAR_DISPLAY = 5             # top-N singular values to print

# ---------------------------------------------------------------------------
# Ternary unpacking
# ---------------------------------------------------------------------------

def unpack_ternary_np(packed: np.ndarray, n_elements: int) -> np.ndarray:
    """Unpack uint32 packed ternary → int8 array.

    Encoding: 2 bits per value, 16 values per uint32.
        00 → 0,  01 → +1,  10 → -1,  11 → unused
    Args:
        packed:     (out_features, in_features_packed) uint32
        n_elements: actual in_features (= in_features_packed * 16 normally)
    Returns:
        (out_features, n_elements) int8
    """
    flat = packed.reshape(-1)
    out = np.zeros(flat.shape[0] * 16, dtype=np.int8)
    for bit in range(16):
        val = (flat >> (bit * 2)) & 0x3
        out[bit::16] = np.where(val == 1, np.int8(1),
                        np.where(val == 2, np.int8(-1), np.int8(0)))
    rows = packed.shape[0]
    return out.reshape(rows, -1)[:, :n_elements]


# ---------------------------------------------------------------------------
# Weight stats
# ---------------------------------------------------------------------------

class WeightStats(NamedTuple):
    key: str
    shape: tuple
    sparsity: float        # fraction of zeros
    balance: float         # +1 count / -1 count  (1.0 = balanced, >1 = pos-biased)
    eff_rank: float        # nuclear norm² / Frobenius norm²  (= effective rank)
    sv_top: list[float]    # top-N singular values (normalised by sv[0])
    sv_entropy: float      # normalised entropy of singular value distribution


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return float("nan")
    return float(np.dot(a.ravel(), b.ravel()) / (na * nb))


def compute_weight_stats(key: str, w: np.ndarray) -> WeightStats:
    """Compute hologram-relevant statistics for a ternary sign matrix."""
    total = w.size
    n_zero = int(np.sum(w == 0))
    n_pos  = int(np.sum(w == 1))
    n_neg  = int(np.sum(w == -1))

    sparsity = n_zero / total
    balance  = n_pos / n_neg if n_neg > 0 else float("inf")

    # SVD on float32 sign matrix — truncated to min(rows, cols, 64)
    W_f = w.astype(np.float32)
    k   = min(w.shape[0], w.shape[1], 64)
    try:
        sv = np.linalg.svd(W_f, compute_uv=False)[:k]
    except np.linalg.LinAlgError:
        sv = np.ones(k, dtype=np.float32)

    # Effective rank = exp(entropy of normalised sv²)
    sv2   = sv ** 2
    sv2_s = sv2.sum()
    if sv2_s > 0:
        p        = sv2 / sv2_s
        p        = p[p > 1e-12]
        entropy  = -float(np.sum(p * np.log(p)))
        eff_rank = float(np.exp(entropy))
    else:
        eff_rank = 1.0
        entropy  = 0.0

    # Normalised entropy (0=rank-1, 1=full-rank uniform)
    max_entropy = float(np.log(len(sv)))
    sv_entropy  = entropy / max_entropy if max_entropy > 0 else 0.0

    # Top singular values, normalised by sv[0]
    sv0 = float(sv[0]) if len(sv) > 0 else 1.0
    sv_top = [float(s / sv0) for s in sv[:N_SINGULAR_DISPLAY]] if sv0 > 0 else []

    return WeightStats(
        key=key,
        shape=tuple(w.shape),
        sparsity=sparsity,
        balance=balance,
        eff_rank=eff_rank,
        sv_top=sv_top,
        sv_entropy=sv_entropy,
    )


# ---------------------------------------------------------------------------
# Checkpoint loading
# ---------------------------------------------------------------------------

class CheckpointData(NamedTuple):
    step: int
    path: Path
    # stride_stack per-layer attention weights: {layer_idx: {proj: int8 array}}
    stride_layers: dict[int, dict[str, np.ndarray]]
    # extra top-level attention: meta_s4, s4, s4_desc
    extra_attn: dict[str, dict[str, np.ndarray]]
    # combinator embeddings (4, 512)
    combinator_embeddings: np.ndarray


def _infer_step(path: Path) -> int:
    name = path.name
    if name.startswith("step_"):
        try:
            return int(name.split("_")[1])
        except (IndexError, ValueError):
            pass
    return -1


def load_checkpoint(ckpt_dir: str | Path) -> CheckpointData:
    p = Path(ckpt_dir)
    npz_path = p / "model.npz"
    if not npz_path.exists():
        sys.exit(f"ERROR: {npz_path} not found")

    ck   = np.load(str(npz_path))
    keys = set(ck.files)
    step = _infer_step(p)

    # --- stride_stack layers ---
    stride_layers: dict[int, dict[str, np.ndarray]] = {}
    layer_idx = 0
    while True:
        prefix = f"stride_stack.layers.{layer_idx}"
        if f"{prefix}.q_proj.weight" not in keys:
            break
        layer: dict[str, np.ndarray] = {}
        for proj in PROJ_TYPES:
            wk = f"{prefix}.{proj}.weight"
            if wk in keys:
                packed = ck[wk]                    # (out, in_packed) uint32
                n_in   = packed.shape[1] * 16
                layer[proj] = unpack_ternary_np(packed, n_in)
        stride_layers[layer_idx] = layer
        layer_idx += 1

    # --- extra top-level attention blocks ---
    extra_attn: dict[str, dict[str, np.ndarray]] = {}
    for block in ("meta_s4", "s4", "s4_desc"):
        blk: dict[str, np.ndarray] = {}
        for proj in ("q_proj", "k_proj", "v_proj", "out_proj"):
            wk = f"{block}.{proj}.weight"
            if wk in keys:
                packed = ck[wk]
                n_in   = packed.shape[1] * 16
                blk[proj] = unpack_ternary_np(packed, n_in)
        if blk:
            extra_attn[block] = blk

    # --- combinator embeddings ---
    comb_key = "combinator_dispatch.combinator_embeddings"
    comb_emb = ck[comb_key] if comb_key in keys else np.zeros((4, 512))

    return CheckpointData(
        step=step,
        path=p,
        stride_layers=stride_layers,
        extra_attn=extra_attn,
        combinator_embeddings=comb_emb,
    )


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------

def analyse_stride_stack(ckpt: CheckpointData) -> dict:
    """Per-layer, per-projection ternary statistics."""
    results: dict[str, dict] = {}
    for layer_idx, layer in sorted(ckpt.stride_layers.items()):
        for proj, w in layer.items():
            key    = f"stride_stack.layers.{layer_idx}.{proj}"
            stats  = compute_weight_stats(key, w)
            results[key] = stats._asdict()
    # also extra blocks
    for block, layer in ckpt.extra_attn.items():
        for proj, w in layer.items():
            key   = f"{block}.{proj}"
            stats = compute_weight_stats(key, w)
            results[key] = stats._asdict()
    return results


def analyse_combinator_embeddings(ckpt: CheckpointData) -> dict:
    """Pairwise cosine similarity of K, I, B, C embeddings."""
    emb  = ckpt.combinator_embeddings      # (4, 512)
    n    = len(COMBINATOR_NAMES)
    sims = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            sims[i, j] = _cosine_sim(emb[i], emb[j])

    # Cluster check: does K/B/C cluster (cos > 0.9)?  Is I distinct?
    cluster_pairs = [(0, 2), (0, 3), (2, 3)]   # K-B, K-C, B-C
    i_pairs       = [(1, 0), (1, 2), (1, 3)]   # I-K, I-B, I-C

    cluster_cos   = [float(sims[a, b]) for a, b in cluster_pairs]
    i_cos         = [float(sims[a, b]) for a, b in i_pairs]

    kibc_cluster_signal = float(np.mean(cluster_cos)) >= REF_CLUSTER_COS
    i_distinct_signal   = all(REF_I_COS_LO <= c <= REF_I_COS_HI for c in i_cos)

    return {
        "names": COMBINATOR_NAMES,
        "sim_matrix": sims.tolist(),
        "cluster_cos_KBC": cluster_cos,
        "i_cos_vs_KBC": i_cos,
        "mean_cluster_cos_KBC": float(np.mean(cluster_cos)),
        "mean_i_cos": float(np.mean(i_cos)),
        "kibc_cluster_signal": kibc_cluster_signal,
        "i_distinct_signal": i_distinct_signal,
        # norms (proxy for embedding magnitude)
        "embedding_norms": [float(np.linalg.norm(emb[i])) for i in range(n)],
    }


def cross_layer_diversity(ckpt: CheckpointData) -> dict:
    """Cross-layer cosine similarity of sign patterns per projection type.

    Beam hypothesis: Q projections should be MORE diverse (lower cross-layer cos)
    than K/V/O which are 'plate' (more uniform across layers).
    """
    n_layers = len(ckpt.stride_layers)
    results  = {}

    for proj in PROJ_TYPES:
        rows = []
        for li in sorted(ckpt.stride_layers.keys()):
            w = ckpt.stride_layers[li].get(proj)
            if w is not None:
                rows.append(w.ravel().astype(np.float32))

        if len(rows) < 2:
            continue

        # All pairs of layers
        pair_cos = []
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                pair_cos.append(_cosine_sim(rows[i], rows[j]))

        results[proj] = {
            "n_layers":    len(rows),
            "mean_cos":    float(np.mean(pair_cos)),
            "min_cos":     float(np.min(pair_cos)),
            "max_cos":     float(np.max(pair_cos)),
            "std_cos":     float(np.std(pair_cos)),
        }

    # Q vs plate summary
    q_mean   = results.get("q_proj", {}).get("mean_cos", float("nan"))
    kvo_mean = float(np.nanmean([
        results.get(p, {}).get("mean_cos", float("nan"))
        for p in ("k_proj", "v_proj", "out_proj")
    ]))
    results["summary"] = {
        "q_mean_cross_cos":    q_mean,
        "kvo_mean_cross_cos":  kvo_mean,
        "q_more_diverse":      q_mean < kvo_mean,
        "diversity_gap":       kvo_mean - q_mean,
    }
    return results


# ---------------------------------------------------------------------------
# Multi-checkpoint stability analysis
# ---------------------------------------------------------------------------

def sign_pattern_stability(ckpts: list[CheckpointData]) -> dict:
    """How much do sign patterns change between consecutive checkpoints?

    Cosine sim of 1 if identical, ~0 if orthogonal (random drift).
    Converging toward 1 = crystallising.
    """
    if len(ckpts) < 2:
        return {}

    stability: dict[str, list] = {}   # key → list of (step_a, step_b, cos)
    pairs = list(zip(ckpts[:-1], ckpts[1:]))

    for a, b in pairs:
        label = f"{a.step}→{b.step}"
        # stride_stack layers
        for li in sorted(a.stride_layers.keys()):
            if li not in b.stride_layers:
                continue
            for proj in PROJ_TYPES:
                wa = a.stride_layers[li].get(proj)
                wb = b.stride_layers[li].get(proj)
                if wa is None or wb is None:
                    continue
                if wa.shape != wb.shape:
                    continue
                key = f"stride_stack.layers.{li}.{proj}"
                cos = _cosine_sim(wa.ravel().astype(np.float32),
                                  wb.ravel().astype(np.float32))
                stability.setdefault(key, []).append(
                    {"transition": label, "cos": cos}
                )

    # Per projection type: average stability curve
    type_curves: dict[str, dict[str, list]] = {p: {} for p in PROJ_TYPES}
    for key, entries in stability.items():
        proj = next((p for p in PROJ_TYPES if key.endswith(p)), None)
        if proj is None:
            continue
        for e in entries:
            type_curves[proj].setdefault(e["transition"], []).append(e["cos"])

    proj_summary = {}
    for proj, transitions in type_curves.items():
        proj_summary[proj] = {
            t: float(np.mean(vs)) for t, vs in transitions.items()
        }

    return {
        "per_weight": stability,
        "per_proj_type": proj_summary,
    }


# ---------------------------------------------------------------------------
# Printing helpers
# ---------------------------------------------------------------------------

def _bar(val: float, lo: float = 0.0, hi: float = 1.0, width: int = 20) -> str:
    frac  = max(0.0, min(1.0, (val - lo) / (hi - lo))) if hi > lo else 0.0
    filled = int(round(frac * width))
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def print_section(title: str) -> None:
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def print_layer_table(stats: dict, step: int) -> None:
    print_section(f"STEP {step} — Per-layer attention weight statistics")
    header = f"{'Key':<52} {'Spar':>5} {'Bal':>5} {'EffRk':>6} {'SvEnt':>6}  Top-SV"
    print(header)
    print("-" * 90)
    for key, s in sorted(stats.items()):
        spar  = s["sparsity"]
        bal   = s["balance"] if s["balance"] != float("inf") else 999.9
        erk   = s["eff_rank"]
        sent  = s["sv_entropy"]
        svs   = " ".join(f"{v:.3f}" for v in s["sv_top"][:N_SINGULAR_DISPLAY])
        flag  = ""
        if spar >= 0.70:
            flag += " ✓sparse"
        if 0.90 <= bal <= 1.10:
            flag += " ✓bal"
        print(f"{key:<52} {spar:>5.3f} {bal:>5.2f} {erk:>6.1f} {sent:>6.3f}  {svs}{flag}")


def print_combinator_table(comb: dict, step: int) -> None:
    print_section(f"STEP {step} — Combinator embedding similarity (KIBC)")
    names = comb["names"]
    sims  = comb["sim_matrix"]
    norms = comb["embedding_norms"]

    # Header
    print(f"  {'':8}", end="")
    for n in names:
        print(f"  {n:>7}", end="")
    print(f"   norm")
    print("  " + "-" * (8 + 8 * len(names) + 8))
    for i, n in enumerate(names):
        print(f"  {n:8}", end="")
        for j in range(len(names)):
            print(f"  {sims[i][j]:>7.4f}", end="")
        print(f"  {norms[i]:>6.2f}")

    print()
    print(f"  Mean K/B/C cluster cos : {comb['mean_cluster_cos_KBC']:.4f}  "
          f"(target >{REF_CLUSTER_COS}) "
          f"{'✅ CLUSTER' if comb['kibc_cluster_signal'] else '❌ no cluster'}")
    print(f"  Mean I vs K/B/C cos    : {comb['mean_i_cos']:.4f}  "
          f"(target {REF_I_COS_LO}–{REF_I_COS_HI}) "
          f"{'✅ DISTINCT' if comb['i_distinct_signal'] else '❌ not distinct'}")


def print_diversity_table(div: dict, step: int) -> None:
    print_section(f"STEP {step} — Cross-layer sign pattern diversity (beam vs plate)")
    print(f"  {'Proj':<12} {'N':>4} {'MeanCos':>8} {'MinCos':>8} {'MaxCos':>8} {'StdCos':>8}  Beam?")
    print("  " + "-" * 62)
    for proj in PROJ_TYPES:
        d = div.get(proj, {})
        if not d:
            continue
        is_q = proj == "q_proj"
        flag = ""
        if is_q and div.get("summary", {}).get("q_more_diverse"):
            flag = " ← beam ✅"
        elif is_q:
            flag = " ← beam ❌"
        print(f"  {proj:<12} {d['n_layers']:>4} {d['mean_cos']:>8.4f} "
              f"{d['min_cos']:>8.4f} {d['max_cos']:>8.4f} {d['std_cos']:>8.4f}{flag}")

    s = div.get("summary", {})
    print()
    print(f"  Q mean cross-cos  : {s.get('q_mean_cross_cos', float('nan')):.4f}")
    print(f"  K/V/O mean cos    : {s.get('kvo_mean_cross_cos', float('nan')):.4f}")
    print(f"  Diversity gap     : {s.get('diversity_gap', float('nan')):.4f}  "
          f"{'(Q more diverse = beam pattern ✅)' if s.get('q_more_diverse') else '(Q not more diverse ❌)'}")


def print_stability_table(stab: dict, steps: list[int]) -> None:
    print_section("Multi-checkpoint sign pattern stability")
    per_proj = stab.get("per_proj_type", {})
    transitions = sorted({
        t for d in per_proj.values() for t in d.keys()
    })
    if not transitions:
        print("  (no transitions to display)")
        return

    print(f"  {'Proj':<12}", end="")
    for t in transitions:
        print(f"  {t:>12}", end="")
    print()
    print("  " + "-" * (14 + 14 * len(transitions)))
    for proj in PROJ_TYPES:
        d = per_proj.get(proj, {})
        print(f"  {proj:<12}", end="")
        for t in transitions:
            v = d.get(t, float("nan"))
            bar = _bar(v, lo=0.5, hi=1.0, width=6)
            print(f"  {v:>6.4f}{bar}", end="")
        print()

    print()
    # Per-layer fastest crystallisation
    per_weight = stab.get("per_weight", {})
    if transitions:
        last_t = transitions[-1]
        layer_stab = []
        for key, entries in per_weight.items():
            for e in entries:
                if e["transition"] == last_t:
                    layer_stab.append((key, e["cos"]))
        layer_stab.sort(key=lambda x: x[1])
        if layer_stab:
            print(f"  Most changed at {last_t} (lowest cos):")
            for key, cos in layer_stab[:5]:
                print(f"    {key:<52}  cos={cos:.4f}")
            print(f"  Most stable at {last_t} (highest cos):")
            for key, cos in layer_stab[-5:]:
                print(f"    {key:<52}  cos={cos:.4f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Probe V12 checkpoints for holographic sign patterns."
    )
    parser.add_argument(
        "checkpoints",
        nargs="+",
        help="One or more checkpoint directories (e.g. checkpoints/v12-run1/step_004000)",
    )
    parser.add_argument(
        "--out-dir",
        default="results/v12-hologram",
        help="Output directory for JSON results (default: results/v12-hologram)",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------------------
    # Load all checkpoints
    # ---------------------------------------------------------------------------
    ckpts: list[CheckpointData] = []
    for ckpt_path in args.checkpoints:
        print(f"Loading {ckpt_path} ...", flush=True)
        ckpts.append(load_checkpoint(ckpt_path))
    ckpts.sort(key=lambda c: c.step)

    all_results = {}

    # ---------------------------------------------------------------------------
    # Per-checkpoint analysis
    # ---------------------------------------------------------------------------
    for ckpt in ckpts:
        label = f"step_{ckpt.step:06d}"
        print(f"\n{'▶' * 3} Analysing step {ckpt.step}", flush=True)

        weight_stats  = analyse_stride_stack(ckpt)
        comb_analysis = analyse_combinator_embeddings(ckpt)
        diversity     = cross_layer_diversity(ckpt)

        print_layer_table(weight_stats, ckpt.step)
        print_combinator_table(comb_analysis, ckpt.step)
        print_diversity_table(diversity, ckpt.step)

        all_results[label] = {
            "step":           ckpt.step,
            "weight_stats":   weight_stats,
            "combinator":     comb_analysis,
            "diversity":      diversity,
        }

    # ---------------------------------------------------------------------------
    # Multi-checkpoint stability
    # ---------------------------------------------------------------------------
    if len(ckpts) >= 2:
        stab = sign_pattern_stability(ckpts)
        print_stability_table(stab, [c.step for c in ckpts])
        all_results["stability"] = stab

    # ---------------------------------------------------------------------------
    # Hologram summary verdict
    # ---------------------------------------------------------------------------
    print_section("HOLOGRAM VERDICT")

    last_result = all_results.get(f"step_{ckpts[-1].step:06d}", {})
    comb        = last_result.get("combinator", {})
    div         = last_result.get("diversity", {})
    ws          = last_result.get("weight_stats", {})

    # 1. Sparsity check
    all_spar    = [s["sparsity"] for s in ws.values()]
    mean_spar   = float(np.mean(all_spar)) if all_spar else 0.0
    spar_ok     = mean_spar >= REF_PLATE_SPARSITY

    # 2. Combinator cluster
    cluster_ok  = comb.get("kibc_cluster_signal", False)
    i_ok        = comb.get("i_distinct_signal", False)

    # 3. Beam vs plate
    beam_ok     = div.get("summary", {}).get("q_more_diverse", False)

    signals = {
        "mean_sparsity >= 75%":           spar_ok,
        "K/B/C cluster (cos > 0.90)":     cluster_ok,
        "I distinct (cos 0.60–0.75)":     i_ok,
        "Q more diverse than K/V/O":      beam_ok,
    }
    for desc, ok in signals.items():
        mark = "✅" if ok else "❌"
        print(f"  {mark}  {desc}")

    n_ok = sum(signals.values())
    print()
    if n_ok == len(signals):
        verdict = "STRONG holographic signal — all 4 patterns present"
    elif n_ok >= 2:
        verdict = f"PARTIAL signal ({n_ok}/{len(signals)}) — formation underway"
    else:
        verdict = f"WEAK/NO signal ({n_ok}/{len(signals)}) — patterns not yet formed"
    print(f"  → {verdict}")
    all_results["verdict"] = {"signals": {k: bool(v) for k, v in signals.items()},
                               "n_signals": n_ok, "verdict": verdict}

    # ---------------------------------------------------------------------------
    # Save JSON
    # ---------------------------------------------------------------------------
    run_id  = f"v12-hologram-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    out_path = out_dir / f"{run_id}.json"

    # JSON-serialise: convert numpy types
    def to_python(obj):
        if isinstance(obj, (np.integer,)):    return int(obj)
        if isinstance(obj, (np.floating,)):   return float(obj)
        if isinstance(obj, np.ndarray):       return obj.tolist()
        if isinstance(obj, dict):             return {k: to_python(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):    return [to_python(v) for v in obj]
        return obj

    with open(out_path, "w") as fh:
        json.dump(to_python(all_results), fh, indent=2)

    print()
    print(f"  Results saved → {out_path}")


if __name__ == "__main__":
    main()
