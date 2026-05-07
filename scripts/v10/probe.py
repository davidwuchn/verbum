#!/usr/bin/env python3
"""v10 probe — checkpoint diagnostics for V6Compressor prose LM.

Probes a v10 checkpoint with stratified φ-compression analysis,
compressor metrics (S3 gates, meta-S3, registers, entropy), eval
loss, ternary topology statistics, and multi-checkpoint evolution.

Usage:
    uv run python scripts/v10/probe.py checkpoints/v10/step_001000

    # Multiple checkpoints — shows evolution table
    uv run python scripts/v10/probe.py checkpoints/v10/step_*

    # Quiet: summary tables only
    uv run python scripts/v10/probe.py checkpoints/v10/step_001000 --quiet

    # φ-only: skip eval, just measure compression
    uv run python scripts/v10/probe.py checkpoints/v10/step_001000 --phi-only

    # Verbose: per-sample φ detail
    uv run python scripts/v10/probe.py checkpoints/v10/step_* -v

    # Skip eval (faster — no data loader)
    uv run python scripts/v10/probe.py checkpoints/v10/step_001000 --no-eval

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.utils import tree_flatten

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import V10Config
from model import V6Compressor, create_model, count_parameters
from ternary import (
    freeze_ternary_weights,
    restore_ternary,
    count_ternary_weights,
    unpack_ternary_mlx,
    unpack_ternary,
    _walk_ternary_modules,
    TernaryLinear,
    TernaryEmbedding,
)


# ══════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════

E_IRREDUCIBLE = 1.82
LOG_V = math.log(151936)  # ≈ 11.93
PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI

PASS_NAMES = ("L0_asc", "L1_asc", "L2_apex", "L1_desc", "L0_desc")
PHASE_NAMES_ASC = ("prep", "conv", "cons")
PHASE_NAMES_DESC = ("disp", "intg", "conv")
PHASE_NAMES = ("prep", "conv", "cons")  # backward compat for evolution table

# Kernel op names (from kernel.py) for dispatch weight display
KERNEL_OP_NAMES = [
    "+", "-", "*", "//", "%", "min", "max",     # 0-6  arith binary
    "=", "<", ">", "<=", ">=",                   # 7-11 comparison
    "and", "or",                                 # 12-13 bool binary
    "not",                                       # 14    bool unary
    "abs", "neg",                                # 15-16 arith unary
    "if",                                        # 17    conditional
    "partial", "apply", "comp", "apply-c",       # 18-21 lambda
]

KERNEL_TYPE_NAMES = ["INT", "BOOL", "FN", "FN_COMP", "ERROR"]

RESULTS_DIR = Path("results/v10")


# ══════════════════════════════════════════════════════════════════════
# φ-compression sample strata
# ══════════════════════════════════════════════════════════════════════

PHI_STRATA = {
    "prose": [
        "The cat sat on the mat and looked out the window at the birds flying south for the winter.",
        "Every student who passed the final exam received a certificate of achievement from the dean.",
        "The quick brown fox jumps over the lazy dog near the river bank on a warm summer afternoon.",
        "In a quiet village nestled between rolling hills, the old baker opened his shop at dawn.",
    ],
    "compositional": [
        "The man who the dog that the cat chased bit ran away quickly.",
        "If every student reads a book then some teacher who knows the author is happy.",
        "No politician who endorsed the candidate that lost the election won their own race.",
        "Every lawyer who represents a client that a judge dismissed the case against appealed.",
    ],
    "technical": [
        "The gradient of the loss with respect to the weights is computed via backpropagation.",
        "Attention scores are computed as the softmax of the scaled dot product of queries and keys.",
        "The learning rate schedule uses cosine annealing with linear warmup over 500 steps.",
        "Each layer applies layer normalization before the self-attention and feed-forward blocks.",
    ],
    "math": [
        "∀x ∈ ℝ: x² ≥ 0 ∧ x² = 0 ↔ x = 0",
        "λx. λy. apply(x, y) → result",
        "P(A|B) = P(B|A) × P(A) / P(B)",
        "∑_{i=1}^{n} i = n(n+1)/2",
    ],
}


# ══════════════════════════════════════════════════════════════════════
# Checkpoint loading
# ══════════════════════════════════════════════════════════════════════


def load_checkpoint(ckpt_path: Path) -> tuple[V6Compressor, int, dict]:
    """Load a v10 checkpoint. Returns (model, step, state_dict)."""
    state_path = ckpt_path / "state.json"
    model_path = ckpt_path / "model.npz"

    if not state_path.exists() or not model_path.exists():
        raise FileNotFoundError(f"Missing state.json or model.npz in {ckpt_path}")

    state = json.loads(state_path.read_text())
    step = state["step"]
    config_data = state.get("config", {})

    cfg = V10Config()
    if "d_model" in config_data:
        cfg.d_model = config_data["d_model"]
        cfg.d_ff = cfg.d_model * 3
        cfg.d_ff_consolidate = cfg.d_model * 4
    if "vocab_size" in config_data:
        cfg.vocab_size = config_data["vocab_size"]
    if "seq_len" in config_data:
        cfg.seq_len = config_data["seq_len"]
        cfg.max_seq_len = config_data["seq_len"]

    model = create_model(cfg)

    # Load weights
    weights = dict(mx.load(str(model_path)))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())
    freeze_ternary_weights(model)
    restore_ternary(model)

    return model, step, state, cfg


# ══════════════════════════════════════════════════════════════════════
# Ternary statistics
# ══════════════════════════════════════════════════════════════════════


def ternary_stats(model: V6Compressor) -> dict:
    """Compute ternary topology statistics per module."""
    stats = {}
    for path, mod in _walk_ternary_modules(model):
        if isinstance(mod, TernaryLinear):
            w_int = unpack_ternary_mlx(mod.weight)
            mx.eval(w_int)
            w_np = np.array(w_int.astype(mx.int8))
            total = w_np.size
            n_zero = int(np.sum(w_np == 0))
            n_neg = int(np.sum(w_np == -1))
            n_pos = int(np.sum(w_np == 1))
            sparsity = n_zero / total

            gamma_np = np.array(mod.gamma)
            stats[path] = {
                "type": "linear",
                "shape": (mod.out_features, mod.in_features),
                "sparsity": sparsity,
                "n_neg": n_neg,
                "n_zero": n_zero,
                "n_pos": n_pos,
                "gamma_mean": float(np.mean(np.abs(gamma_np))),
                "gamma_std": float(np.std(gamma_np)),
                "gamma_min": float(np.min(np.abs(gamma_np))),
                "gamma_max": float(np.max(np.abs(gamma_np))),
            }

        elif isinstance(mod, TernaryEmbedding):
            w_int = unpack_ternary(mod.ternary_weight, mod.in_features)
            mx.eval(w_int)
            w_np = np.array(w_int.astype(mx.int8))
            total = w_np.size
            n_zero = int(np.sum(w_np == 0))
            sparsity = n_zero / total

            gamma_np = np.array(mod.gamma)
            stats[path] = {
                "type": "embedding",
                "shape": (mod.out_features, mod.in_features),
                "sparsity": sparsity,
                "gamma_mean": float(np.mean(np.abs(gamma_np))),
                "gamma_std": float(np.std(gamma_np)),
            }

    return stats


def print_ternary_stats(stats: dict) -> None:
    """Display ternary statistics grouped by component."""
    groups: dict[str, list] = {}
    for path, s in stats.items():
        # Group by top-level component
        parts = path.split(".")
        if len(parts) >= 1:
            group = parts[0]
        else:
            group = "other"
        groups.setdefault(group, []).append(s)

    print(f"\n  Ternary topology ({len(stats)} modules):")
    print(f"  {'Group':18s} {'#':>3} {'sparsity':>9} {'γ_mean':>8} {'γ_std':>7} {'shape':>16}")
    print(f"  {'─'*18} {'─'*3} {'─'*9} {'─'*8} {'─'*7} {'─'*16}")

    total_params = 0
    total_zeros = 0
    for grp in sorted(groups.keys()):
        mods = groups[grp]
        n = len(mods)
        sp = sum(m["sparsity"] for m in mods) / n
        gm = sum(m["gamma_mean"] for m in mods) / n
        gs = sum(m.get("gamma_std", 0) for m in mods) / n
        shapes = set(str(m["shape"]) for m in mods)
        shape_str = next(iter(shapes)) if len(shapes) == 1 else "mixed"

        for m in mods:
            total_params += m["shape"][0] * m["shape"][1]
            total_zeros += int(m["sparsity"] * m["shape"][0] * m["shape"][1])

        print(f"  {grp:18s} {n:>3} {sp:>9.3f} {gm:>8.4f} {gs:>7.4f} {shape_str:>16}")

    overall_sparsity = total_zeros / total_params if total_params else 0
    print(f"  {'─'*18} {'─'*3} {'─'*9}")
    print(f"  {'TOTAL':18s} {len(stats):>3} {overall_sparsity:>9.3f}  "
          f"({total_params:,} ternary params)")


# ══════════════════════════════════════════════════════════════════════
# Evaluation on held-out data
# ══════════════════════════════════════════════════════════════════════


def evaluate_on_data(model: V6Compressor, cfg: V10Config,
                     target_tokens: int = 50_000) -> dict:
    """Evaluate on held-out Dolma shards."""
    from data import ShardedDataLoader

    eval_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=cfg.n_train_shards,
        shard_end=cfg.n_train_shards + cfg.n_eval_shards,
        seed=9999,
    )

    total_loss = 0.0
    n_batches = 0
    tokens_seen = 0

    while tokens_seen < target_tokens:
        input_ids_np, targets_np = eval_loader.next_batch()
        input_ids = mx.array(input_ids_np)
        targets = mx.array(targets_np)

        _, loss = model(input_ids, targets)
        mx.eval(loss)
        total_loss += float(loss.item())
        n_batches += 1
        tokens_seen += input_ids_np.size

    avg_loss = total_loss / max(n_batches, 1)
    ppl = math.exp(min(avg_loss, 20.0))
    r = (avg_loss - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE)

    return {
        "loss": avg_loss,
        "ppl": ppl,
        "r": r,
        "tokens_evaluated": tokens_seen,
        "n_batches": n_batches,
    }


# ══════════════════════════════════════════════════════════════════════
# φ-Compression analysis (stratified)
# ══════════════════════════════════════════════════════════════════════


def _run_phi_samples(model: V6Compressor, tokenizer, samples: list[str]) -> dict:
    """Run forward_instrumented on text samples, collect compressor metrics."""
    all_metrics = {
        "s3_gates": [],
        "meta_s3": [],
        "register_norms": [],
        "pass_compression": [],
        "pass_phi_dev": [],
        "pass_entropy_in": [],
        "pass_entropy_out": [],
        "losses": [],
        "per_sample": [],
        "kernel_dispatch_weights": [],
        "kernel_type_weights": [],
    }

    for text in samples:
        ids = mx.array(tokenizer.encode(text)).reshape(1, -1)
        if ids.shape[1] > model.cfg.max_seq_len:
            ids = ids[:, -model.cfg.max_seq_len:]

        # Construct targets (shifted by 1)
        targets = mx.concatenate([ids[:, 1:], mx.zeros((1, 1), dtype=mx.int32)], axis=1)

        # Get compressor metrics
        hidden, metrics = model.forward_instrumented(ids)
        mx.eval(hidden)

        # Also compute loss
        logits = model.output_norm(hidden)
        logits = model.embed.output_proj(logits)
        loss = nn.losses.cross_entropy(
            logits.reshape(-1, model.cfg.vocab_size),
            targets.reshape(-1),
        ).mean()
        mx.eval(loss)

        all_metrics["s3_gates"].append(metrics["s3_gates"])
        all_metrics["meta_s3"].append(metrics["meta_s3"])
        all_metrics["register_norms"].append(metrics["register_norms"])
        all_metrics["pass_compression"].append(metrics["pass_compression"])
        all_metrics["pass_phi_dev"].append(metrics["pass_phi_dev"])
        all_metrics["pass_entropy_in"].append(metrics["pass_entropy_in"])
        all_metrics["pass_entropy_out"].append(metrics["pass_entropy_out"])
        all_metrics["losses"].append(float(loss.item()))

        if metrics.get("kernel_dispatch_weights"):
            all_metrics["kernel_dispatch_weights"].append(metrics["kernel_dispatch_weights"])
        if metrics.get("kernel_type_weights"):
            all_metrics["kernel_type_weights"].append(metrics["kernel_type_weights"])

        all_metrics["per_sample"].append({
            "text": text[:60],
            "loss": float(loss.item()),
            "pass_compression": metrics["pass_compression"],
            "pass_phi_dev": metrics["pass_phi_dev"],
        })

    return all_metrics


def _avg_nested(values: list, n_passes: int = 5) -> list[float]:
    """Average a list of per-pass float lists."""
    if not values:
        return [0.0] * n_passes
    result = [0.0] * n_passes
    for vals in values:
        for i in range(n_passes):
            result[i] += vals[i]
    return [v / len(values) for v in result]


def _avg_s3_gates(gate_lists: list) -> list[list[float]]:
    """Average S3 gates: list of [5 passes × 3 phases]."""
    if not gate_lists:
        return [[0.0] * 3 for _ in range(5)]
    n = len(gate_lists)
    result = [[0.0] * 3 for _ in range(5)]
    for gates in gate_lists:
        for pi in range(5):
            for ph in range(3):
                result[pi][ph] += gates[pi][ph]
    return [[v / n for v in row] for row in result]


def _avg_register_norms(norm_lists: list) -> dict[str, list[float]]:
    """Average register norms across samples."""
    if not norm_lists:
        return {}
    n = len(norm_lists)
    result: dict[str, list[float]] = {}
    for norms in norm_lists:
        for bank_name, vals in norms.items():
            if bank_name not in result:
                result[bank_name] = [0.0] * len(vals)
            for i, v in enumerate(vals):
                result[bank_name][i] += v
    return {k: [v / n for v in vals] for k, vals in result.items()}


def analyze_phi(model: V6Compressor, tokenizer, strata: dict | None = None) -> dict:
    """Stratified φ-compression analysis.

    Returns dict with:
      overall: averaged metrics across all strata
      strata: {stratum_name: averaged metrics}
      per_sample: list of per-sample detail
    """
    if strata is None:
        strata = PHI_STRATA

    # Collect all samples
    all_samples = []
    for samples in strata.values():
        all_samples.extend(samples)

    overall_raw = _run_phi_samples(model, tokenizer, all_samples)

    # Per-stratum
    strata_results = {}
    for sname, samples in strata.items():
        raw = _run_phi_samples(model, tokenizer, samples)
        strata_results[sname] = {
            "mean_loss": sum(raw["losses"]) / len(raw["losses"]) if raw["losses"] else 0,
            "pass_compression": _avg_nested(raw["pass_compression"]),
            "pass_phi_dev": _avg_nested(raw["pass_phi_dev"]),
        }

    # Overall
    overall = {
        "mean_loss": sum(overall_raw["losses"]) / len(overall_raw["losses"]) if overall_raw["losses"] else 0,
        "s3_gates": _avg_s3_gates(overall_raw["s3_gates"]),
        "meta_s3": _avg_nested(overall_raw["meta_s3"]),
        "register_norms": _avg_register_norms(overall_raw["register_norms"]),
        "pass_compression": _avg_nested(overall_raw["pass_compression"]),
        "pass_phi_dev": _avg_nested(overall_raw["pass_phi_dev"]),
        "pass_entropy_in": _avg_nested(overall_raw["pass_entropy_in"]),
        "pass_entropy_out": _avg_nested(overall_raw["pass_entropy_out"]),
    }

    # Kernel dispatch weights (average over samples)
    kdw_list = overall_raw.get("kernel_dispatch_weights", [])
    if kdw_list:
        n_ops = len(kdw_list[0])
        avg_kdw = [0.0] * n_ops
        for kdw in kdw_list:
            for i in range(n_ops):
                avg_kdw[i] += kdw[i]
        overall["kernel_dispatch_weights"] = [v / len(kdw_list) for v in avg_kdw]

    ktw_list = overall_raw.get("kernel_type_weights", [])
    if ktw_list:
        n_types = len(ktw_list[0])
        avg_ktw = [0.0] * n_types
        for ktw in ktw_list:
            for i in range(n_types):
                avg_ktw[i] += ktw[i]
        overall["kernel_type_weights"] = [v / len(ktw_list) for v in avg_ktw]

    # Aggregate phi stats
    agg_ratio = sum(overall["pass_compression"]) / 5
    agg_phi_dev = sum(overall["pass_phi_dev"]) / 5
    overall["aggregate"] = {
        "mean_ratio": agg_ratio,
        "mean_phi_dev": agg_phi_dev,
        "target": INV_PHI,
    }

    return {
        "overall": overall,
        "strata": strata_results,
        "per_sample": overall_raw["per_sample"],
    }


# ══════════════════════════════════════════════════════════════════════
# Display
# ══════════════════════════════════════════════════════════════════════


def print_banner(step: int, state: dict, model: V6Compressor):
    """Print checkpoint summary banner."""
    print(f"\n{'='*72}")
    print(f"  v10 Probe — step {step:,}")
    print(f"{'='*72}")

    cfg_data = state.get("config", {})
    print(f"  d_model={cfg_data.get('d_model', '?')}  "
          f"vocab={cfg_data.get('vocab_size', '?')}  "
          f"seq_len={cfg_data.get('seq_len', '?')}")

    params = count_parameters(model)
    n_ternary = count_ternary_weights(model)
    print(f"  params: total={params['total']:,}  "
          f"trainable={params['trainable']:,}  "
          f"ternary={n_ternary:,}")

    # Training state from checkpoint
    evo_gen = state.get("total_generations", 0)
    evo_acc = state.get("total_accepted", 0)
    if evo_gen > 0:
        pct = evo_acc / evo_gen * 100
        print(f"  evolution: {evo_acc}/{evo_gen} accepted ({pct:.0f}%)")

    losses = state.get("train_losses_last50", [])
    if losses:
        avg = sum(losses) / len(losses)
        # Detect whether losses are CE (>1) or relational r (<1 typically)
        if avg > 1.5:
            # Legacy: CE values
            r = (avg - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE)
            print(f"  train loss (last 50): CE={avg:.3f}  r={r:.3f}")
        else:
            # Current: relational r values
            ce = avg * (LOG_V - E_IRREDUCIBLE) + E_IRREDUCIBLE
            print(f"  train loss (last 50): r={avg:.4f}  CE={ce:.3f}")


def print_compressor_metrics(phi_result: dict):
    """Print compressor metrics from φ analysis."""
    overall = phi_result["overall"]

    # ── S3 gates ──────────────────────────────────────────
    print(f"\n  ┌─ S3 gates ──────────────────────────────────────┐")
    for pi, pname in enumerate(PASS_NAMES):
        gates = overall["s3_gates"][pi]
        print(f"  │ {pname:8s}: prep={gates[0]:.3f}  conv={gates[1]:.3f}  "
              f"cons={gates[2]:.3f}")

    # ── Meta-S3 ──────────────────────────────────────────
    print(f"  ├─ Meta-S3 ───────────────────────────────────────┤")
    mg = overall["meta_s3"]
    print(f"  │ {' '.join(f'{pn}={g:.3f}' for pn, g in zip(PASS_NAMES, mg))}")

    # ── Compression ──────────────────────────────────────
    print(f"  ├─ φ-Compression (1/φ = {INV_PHI:.4f}) ──────────────┤")
    cr = overall["pass_compression"]
    pd = overall["pass_phi_dev"]
    for pi, pname in enumerate(PASS_NAMES):
        phi_mark = " ←φ" if pd[pi] < 0.05 else "   "
        print(f"  │ {pname:8s}: ratio={cr[pi]:>7.3f}  φ-dev={pd[pi]:.3f}{phi_mark}")

    agg = overall["aggregate"]
    print(f"  │ {'MEAN':8s}: ratio={agg['mean_ratio']:>7.3f}  "
          f"φ-dev={agg['mean_phi_dev']:.3f}")

    # ── Entropy ──────────────────────────────────────────
    print(f"  ├─ Entropy (log variance proxy) ──────────────────┤")
    h_in = overall["pass_entropy_in"]
    h_out = overall["pass_entropy_out"]
    for pi, pname in enumerate(PASS_NAMES):
        print(f"  │ {pname:8s}: {h_in[pi]:>7.3f} → {h_out[pi]:>7.3f}")

    # ── Register norms ───────────────────────────────────
    reg_norms = overall["register_norms"]
    if reg_norms:
        print(f"  ├─ Register norms ────────────────────────────────┤")
        for bname in sorted(reg_norms.keys()):
            norms = reg_norms[bname]
            print(f"  │ {bname:12s}: {' '.join(f'{n:>7.2f}' for n in norms)}")

    # ── Kernel dispatch weights ──────────────────────────
    kdw = overall.get("kernel_dispatch_weights")
    if kdw:
        print(f"  ├─ Kernel dispatch (top ops) ─────────────────────┤")
        # Sort by weight, show top 8
        indexed = sorted(enumerate(kdw), key=lambda x: -x[1])
        for rank, (op_idx, weight) in enumerate(indexed[:8]):
            op_name = KERNEL_OP_NAMES[op_idx] if op_idx < len(KERNEL_OP_NAMES) else f"op{op_idx}"
            bar = "█" * int(weight * 100)
            print(f"  │ {op_name:>8s} ({op_idx:>2d}): {weight:.3f} {bar}")
        # Check uniformity: max/min ratio
        max_w, min_w = max(kdw), min(kdw)
        ratio = max_w / (min_w + 1e-8)
        if ratio < 1.5:
            print(f"  │ ≈ uniform (max/min={ratio:.2f}) — not specialized yet")
        else:
            print(f"  │ max/min={ratio:.2f} — specializing")

    # ── Kernel type weights ──────────────────────────────
    ktw = overall.get("kernel_type_weights")
    if ktw:
        print(f"  ├─ Kernel types ──────────────────────────────────┤")
        for ti, (tname, tw) in enumerate(zip(KERNEL_TYPE_NAMES, ktw)):
            bar = "█" * int(tw * 50)
            print(f"  │ {tname:>8s}: {tw:.3f} {bar}")

    print(f"  └─────────────────────────────────────────────────┘")


def print_strata(phi_result: dict):
    """Print per-stratum compression and loss."""
    strata = phi_result["strata"]
    if not strata:
        return

    print(f"\n  φ-Compression by content type:")
    print(f"  {'stratum':15s} {'loss':>8} {'mean_cr':>8} ", end="")
    for pn in PASS_NAMES:
        print(f" {pn:>7}", end="")
    print()
    print(f"  {'─'*15} {'─'*8} {'─'*8}", end="")
    for _ in PASS_NAMES:
        print(f" {'─'*7}", end="")
    print()

    means = []
    for sname in ["prose", "compositional", "technical", "math"]:
        if sname not in strata:
            continue
        s = strata[sname]
        cr = s["pass_compression"]
        mean_cr = sum(cr) / len(cr)
        means.append(mean_cr)
        print(f"  {sname:15s} {s['mean_loss']:>8.3f} {mean_cr:>8.3f}", end="")
        for v in cr:
            print(f" {v:>7.3f}", end="")
        print()

    if len(means) >= 2:
        spread = max(means) - min(means)
        print(f"  {'─'*15} {'─'*8} {'─'*8}")
        print(f"  spread: {spread:.4f}", end="")
        if spread < 0.05:
            print("  ✓ content-independent")
        elif spread < 0.15:
            print("  → converging")
        else:
            print("  ⚠ content-dependent (expected early)")
        print()


def print_phi_interpretation(phi_result: dict):
    """Interpret φ-compression results."""
    agg = phi_result["overall"]["aggregate"]
    mr = agg["mean_ratio"]
    pd = agg["mean_phi_dev"]

    if mr > 1.05:
        print(f"  ⚠ EXPANDING (ratio > 1). No compression yet.")
    elif mr > 0.95:
        print(f"  ≈ Near-identity (ratio ≈ 1). Minimal compression.")
    elif pd < 0.05:
        print(f"  ✓ Within 0.05 of 1/φ — convergence signal!")
    elif pd < 0.15:
        print(f"  → Compressing, φ-dev={pd:.3f}. In the neighborhood.")
    else:
        print(f"  → Compressing at {mr:.3f}, far from φ (dev={pd:.3f}).")

    # Ascending vs descending
    cr = phi_result["overall"]["pass_compression"]
    asc = cr[:3]
    desc = cr[3:]
    asc_m = sum(asc) / len(asc)
    desc_m = sum(desc) / len(desc)
    spread = max(cr) - min(cr)

    if spread < 0.05:
        print(f"  ≡ All passes at similar ratios (spread={spread:.3f}). Self-similar.")
    elif abs(asc_m - desc_m) > 0.03:
        direction = "ascending" if asc_m < desc_m else "descending"
        print(f"  ≠ {direction} compresses more "
              f"(asc={asc_m:.3f} desc={desc_m:.3f}).")


def print_per_sample(per_sample: list[dict]):
    """Print per-sample φ detail."""
    print(f"\n  Per-sample φ detail:")
    for sd in per_sample:
        print(f"    {sd['text']!r}  loss={sd['loss']:.3f}")
        cr = sd["pass_compression"]
        pd = sd["pass_phi_dev"]
        for pi, pn in enumerate(PASS_NAMES):
            marker = " ←φ" if pd[pi] < 0.05 else ""
            print(f"      {pn:8s}: ratio={cr[pi]:.4f}  φ-dev={pd[pi]:.4f}{marker}")


# ══════════════════════════════════════════════════════════════════════
# Multi-checkpoint evolution
# ══════════════════════════════════════════════════════════════════════


def print_evolution(all_results: list[dict]):
    """Print multi-checkpoint evolution table."""
    if len(all_results) < 2:
        return

    print(f"\n{'='*72}")
    print(f"  φ-Compression Evolution")
    print(f"{'='*72}")

    # ── Loss + r evolution ──────────────────────────────────
    print(f"\n  {'step':>8} {'loss':>8} {'ppl':>8} {'r':>8} {'evo%':>6}")
    print(f"  {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*6}")
    for r in all_results:
        loss = r.get("eval_loss", r.get("train_loss_avg", 0))
        ppl = math.exp(min(loss, 20.0)) if loss else 0
        rel_r = (loss - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE) if loss else 0
        evo_pct = r.get("evo_pct", "")
        evo_str = f"{evo_pct:.0f}%" if isinstance(evo_pct, (int, float)) else ""
        print(f"  {r['step']:>8} {loss:>8.3f} {ppl:>8.0f} {rel_r:>8.3f} {evo_str:>6}")

    # ── Per-pass compression evolution ──────────────────────
    print(f"\n  {'step':>8} {'mean':>8} {'φ-dev':>8}", end="")
    for pn in PASS_NAMES:
        print(f" {pn:>8}", end="")
    print()
    print(f"  {'─'*8} {'─'*8} {'─'*8}", end="")
    for _ in PASS_NAMES:
        print(f" {'─'*8}", end="")
    print()

    for r in all_results:
        phi = r.get("phi_overall", {})
        agg = phi.get("aggregate", {})
        cr = phi.get("pass_compression", [0]*5)
        print(f"  {r['step']:>8} {agg.get('mean_ratio', 0):>8.4f} "
              f"{agg.get('mean_phi_dev', 0):>8.4f}", end="")
        for v in cr:
            print(f" {v:>8.4f}", end="")
        print()

    print(f"  {'target':>8} {INV_PHI:>8.4f} {'0.0000':>8}")

    # ── Per-stratum evolution ───────────────────────────────
    strata_names = set()
    for r in all_results:
        if "phi_strata" in r:
            strata_names.update(r["phi_strata"].keys())

    if strata_names:
        ordered = [s for s in ["prose", "compositional", "technical", "math"]
                   if s in strata_names]
        print(f"\n  Per-stratum mean compression:")
        print(f"  {'step':>8}", end="")
        for sn in ordered:
            print(f" {sn:>14}", end="")
        print(f" {'spread':>8}")
        print(f"  {'─'*8}", end="")
        for _ in ordered:
            print(f" {'─'*14}", end="")
        print(f" {'─'*8}")

        for r in all_results:
            print(f"  {r['step']:>8}", end="")
            vals = []
            for sn in ordered:
                st = r.get("phi_strata", {}).get(sn, {})
                cr = st.get("pass_compression", [])
                if cr:
                    mean_cr = sum(cr) / len(cr)
                    print(f" {mean_cr:>14.4f}", end="")
                    vals.append(mean_cr)
                else:
                    print(f" {'—':>14}", end="")
            if vals:
                print(f" {max(vals) - min(vals):>8.4f}", end="")
            print()

    # ── S3 gate evolution ───────────────────────────────────
    print(f"\n  S3 Gate Evolution (pass 0 = L0↑, most informative early):")
    print(f"  {'step':>8}", end="")
    for ph in PHASE_NAMES:
        print(f" {ph:>8}", end="")
    print(f"  │ meta-S3")
    print(f"  {'─'*8}", end="")
    for _ in PHASE_NAMES:
        print(f" {'─'*8}", end="")
    print(f"  │ {'─'*30}")

    for r in all_results:
        phi = r.get("phi_overall", {})
        s3 = phi.get("s3_gates", [[0]*3]*5)
        ms3 = phi.get("meta_s3", [0]*5)
        print(f"  {r['step']:>8}", end="")
        for ph in range(3):
            print(f" {s3[0][ph]:>8.3f}", end="")
        print(f"  │ {' '.join(f'{g:.3f}' for g in ms3)}")

    print(f"{'='*72}\n")


# ══════════════════════════════════════════════════════════════════════
# JSON output
# ══════════════════════════════════════════════════════════════════════


def save_results(step: int, state: dict, phi_result: dict,
                 eval_result: dict | None, ternary: dict | None,
                 out_dir: Path) -> Path:
    """Save probe results to JSON."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"probe_step_{step:06d}.json"

    output = {
        "timestamp": datetime.now(UTC).isoformat(),
        "architecture": "v10-v6compressor-prose-lm",
        "step": step,
        "config": state.get("config", {}),
        "evolution": {
            "total_generations": state.get("total_generations", 0),
            "total_accepted": state.get("total_accepted", 0),
        },
        "phi_compression": {
            "overall": phi_result["overall"],
            "strata": phi_result["strata"],
        },
    }

    if eval_result:
        output["eval"] = eval_result

    if ternary:
        # Summarize — full per-module stats are too verbose for JSON
        n_mods = len(ternary)
        sparsities = [s["sparsity"] for s in ternary.values()]
        gammas = [s["gamma_mean"] for s in ternary.values()]
        output["ternary_summary"] = {
            "n_modules": n_mods,
            "mean_sparsity": sum(sparsities) / n_mods,
            "mean_gamma": sum(gammas) / n_mods,
            "min_sparsity": min(sparsities),
            "max_sparsity": max(sparsities),
        }

    out_path.write_text(json.dumps(output, indent=2))
    return out_path


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="v10 probe — checkpoint diagnostics for V6Compressor prose LM")
    parser.add_argument("checkpoints", type=Path, nargs="+",
                        help="Checkpoint directory/directories")
    parser.add_argument("--quiet", action="store_true",
                        help="Summary tables only")
    parser.add_argument("--phi-only", action="store_true",
                        help="Skip eval, just measure compression")
    parser.add_argument("--no-eval", action="store_true",
                        help="Skip data evaluation (faster)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Per-sample φ detail")
    parser.add_argument("--no-ternary", action="store_true",
                        help="Skip ternary statistics (faster)")
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR,
                        help="Output directory for JSON results")
    args = parser.parse_args()

    if args.phi_only:
        args.no_eval = True

    # ── Tokenizer ─────────────────────────────────────────
    print("  Loading Qwen3 tokenizer...", file=sys.stderr)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B", trust_remote_code=True)

    # ── Sort checkpoints by step ──────────────────────────
    ckpts = sorted(
        [p for p in args.checkpoints if p.is_dir()],
        key=lambda p: int(p.name.split("_")[-1]) if p.name.startswith("step_") else 0,
    )

    if not ckpts:
        print("  No checkpoint directories found.", file=sys.stderr)
        return

    all_results = []

    for ckpt_path in ckpts:
        t0 = time.time()

        # ── Load ──────────────────────────────────────────
        print(f"\n  Loading {ckpt_path}...", file=sys.stderr)
        model, step, state, cfg = load_checkpoint(ckpt_path)
        print_banner(step, state, model)

        # ── φ-compression ─────────────────────────────────
        print(f"\n  Running φ-compression analysis...", file=sys.stderr)
        phi_result = analyze_phi(model, tokenizer)
        print_compressor_metrics(phi_result)

        if not args.quiet:
            print_strata(phi_result)
            print_phi_interpretation(phi_result)

        if args.verbose:
            print_per_sample(phi_result["per_sample"])

        # ── Eval ──────────────────────────────────────────
        eval_result = None
        if not args.no_eval:
            print(f"\n  Evaluating on held-out data...", file=sys.stderr)
            eval_result = evaluate_on_data(model, cfg)
            print(f"\n  📊 Eval: loss={eval_result['loss']:.3f}  "
                  f"ppl={eval_result['ppl']:.0f}  r={eval_result['r']:.3f}  "
                  f"({eval_result['tokens_evaluated']:,} tokens)")

        # ── Ternary stats ─────────────────────────────────
        ternary = None
        if not args.no_ternary:
            ternary = ternary_stats(model)
            if not args.quiet:
                print_ternary_stats(ternary)

        # ── Save JSON ─────────────────────────────────────
        out_path = save_results(step, state, phi_result,
                                eval_result, ternary, args.results_dir)
        print(f"\n  💾 Saved: {out_path}")

        elapsed = time.time() - t0
        print(f"  ⏱  {elapsed:.1f}s", file=sys.stderr)

        # ── Collect for evolution table ───────────────────
        losses = state.get("train_losses_last50", [])
        train_loss_avg = sum(losses) / len(losses) if losses else 0
        evo_gen = state.get("total_generations", 0)
        evo_acc = state.get("total_accepted", 0)

        result_entry = {
            "step": step,
            "train_loss_avg": train_loss_avg,
            "eval_loss": eval_result["loss"] if eval_result else train_loss_avg,
            "evo_pct": (evo_acc / evo_gen * 100) if evo_gen > 0 else 0,
            "phi_overall": phi_result["overall"],
            "phi_strata": phi_result["strata"],
        }
        all_results.append(result_entry)

    # ── Multi-checkpoint evolution ────────────────────────
    print_evolution(all_results)


if __name__ == "__main__":
    main()
