"""
v12 — Training Script

V12 dual-layer architecture (KIBC composition + M retrieval, 5-pass bidirectional VSM,
9 strides, Qwen3 tokenizer) trained on Dolma prose for next-token prediction.

  • Causal LM cross-entropy loss
  • Relational loss r = (CE - E) / (log(V) - E) for phase awareness
  • Shared-weight gradient normalization (÷5 for 5-pass components)
  • Ternary topology evolved via tournament selection (mixed-data-aware)
  • Adam on continuous parameters (gamma, norms, embeddings, pos_embed)
  • Cosine LR with linear warmup
  • Retrieval metrics (gate means, register norms, write gates) logged to metrics_log.jsonl

Usage:
    uv run python scripts/v12/train.py
    uv run python scripts/v12/train.py --total-steps 5000
    uv run python scripts/v12/train.py --seq-len 512 --batch-size 4
    uv run python scripts/v12/train.py --resume

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import deque
from pathlib import Path

os.environ["PYTHONUNBUFFERED"] = "1"

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map

sys.path.insert(0, str(Path(__file__).parent))

from config import V12Config
from data import ShardedDataLoader, MixedDataLoader
from model import V12Model, create_model, count_parameters, compute_crystal_diagnostics
from ternary import (
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    count_ternary_weights,
    bios_mutation_budget,
    save_topology,
    load_topology,
    mutate_topology,
    propose_mutations,
    find_consensus,
    apply_consensus,
    _walk_ternary_modules,
    TernaryLinear,
    # Etching (gradient-directed ternary topology shaping)
    init_etch_states,
    accumulate_etch_heat,
    update_signal_planes,
    etch_check,
    save_etch_states,
    load_etch_states,
    surgical_adam_decay_for_etch,
)


# ══════════════════════════════════════════════════════════════════════════════
# § 1  Constants
# ══════════════════════════════════════════════════════════════════════════════

# Irreducible entropy of natural language (Chinchilla: E ≈ 1.82 nats)
E_IRREDUCIBLE = 1.82
# log(vocab_size) — the "knows nothing" ceiling
LOG_V = math.log(151936)  # ≈ 11.93


# ══════════════════════════════════════════════════════════════════════════════
# § 2  Loss function — relational loss
# ══════════════════════════════════════════════════════════════════════════════

def loss_fn(
    model: V12Model,
    input_ids: mx.array,
    targets: mx.array,
) -> mx.array:
    """Relational loss: r = (CE - E) / (log(V) - E).

    Normalizes cross-entropy into phase-aware [0,1] space:
      r=1.0  → model knows nothing (CE = log(V))
      r=0.0  → model matches irreducible entropy (CE = E)
      r<0.0  → model beats irreducible (overfitting or better estimate of E)

    Same gradient direction as CE (monotonic transform), but compressed
    into a range where evolution can see structural progress — a 0.01
    improvement in r means the same thing at loss=10 or loss=5.

    The denominator (log(V) - E) is constant, so grad(r) = grad(CE) / const.
    This scales the learning rate implicitly but the optimizer adapts.
    """
    _, total_loss = model(input_ids, targets)
    r = (total_loss - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE)
    return r


# ══════════════════════════════════════════════════════════════════════════════
# § 3  Shared-weight gradient normalization
# ══════════════════════════════════════════════════════════════════════════════

# Ascending components: shared across L0↑, L1↑, L2_apex (3 passes)
ASC_SHARED = ("stride_stack", "mod_projs", "s4")
# Descending components: shared across descending passes
DESC_SHARED = ("combinator_dispatch", "combinator_integrate", "mod_projs_desc", "s4_desc")
# Universal shared: stride_stack + dispatch/integrate are used in ALL 7 passes
UNIVERSAL_SHARED = ("stride_stack", "combinator_dispatch", "combinator_integrate")

N_ASC_PASSES = 4   # L0↑ L1↑ L2↑ L3_apex
N_DESC_PASSES = 3  # L2↓ L1↓ L0↓
N_ALL_PASSES = 7


def normalize_shared_grads(grads: dict) -> dict:
    """Divide gradients of shared components by their pass count.

    stride_stack, combinator_dispatch, combinator_integrate are shared
    across ALL 7 passes (universal architecture).
    s4 (ascending) and s4_desc (descending) have their respective counts.
    Normalizing stabilizes Adam's running statistics.
    """
    asc_scale = 1.0 / N_ASC_PASSES
    desc_scale = 1.0 / N_DESC_PASSES

    all_scale = 1.0 / N_ALL_PASSES

    def _walk(tree, keys):
        if isinstance(tree, dict):
            out = {}
            for k, v in tree.items():
                new_keys = keys + [k]
                if len(new_keys) >= 1 and new_keys[0] in UNIVERSAL_SHARED:
                    # Used in all 7 passes
                    out[k] = tree_map(lambda g: g * all_scale, v)
                elif len(new_keys) >= 1 and new_keys[0] in ASC_SHARED:
                    out[k] = tree_map(lambda g: g * asc_scale, v)
                elif len(new_keys) >= 1 and new_keys[0] in DESC_SHARED:
                    out[k] = tree_map(lambda g: g * desc_scale, v)
                else:
                    out[k] = _walk(v, new_keys)
            return out
        elif isinstance(tree, list):
            return [_walk(v, keys + [str(i)]) for i, v in enumerate(tree)]
        return tree

    return _walk(grads, [])


# ══════════════════════════════════════════════════════════════════════════════
# § 4  LR schedule
# ══════════════════════════════════════════════════════════════════════════════

def cosine_lr(step, warmup_steps, total_steps, lr_max, lr_floor_ratio=0.01):
    if step < warmup_steps:
        return lr_max * step / max(warmup_steps, 1)
    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
    floor = lr_max * lr_floor_ratio
    return floor + (lr_max - floor) * 0.5 * (1.0 + math.cos(math.pi * progress))


def holo_schedule(step: int, cfg: V12Config) -> float:
    """Holographic loss weight schedule.

    With default warmup=0, ramp=0: returns holo_lambda from step 1.
    With warmup>0: delays activation. With ramp>0: linear ramp after warmup.
    When holo_lambda=0.0, always returns 0.0 (zero overhead).
    """
    if cfg.holo_lambda <= 0:
        return 0.0
    if step < cfg.holo_warmup_steps:
        return 0.0
    if cfg.holo_ramp_steps <= 0:
        return cfg.holo_lambda
    ramp_progress = min(1.0, (step - cfg.holo_warmup_steps) / cfg.holo_ramp_steps)
    return cfg.holo_lambda * ramp_progress


# ══════════════════════════════════════════════════════════════════════════════
# § 4b  JSONL metrics logging
# ══════════════════════════════════════════════════════════════════════════════

def _sanitize_for_json(obj):
    """Recursively sanitize a value for JSON: NaN/Inf → null, mx/np scalars → Python."""
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(v) for v in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if hasattr(obj, 'item'):  # mx.array scalar, np scalar
        v = obj.item()
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return None
        return v
    if isinstance(obj, set):
        return sorted(obj)
    return obj


def _append_jsonl(path: Path, record: dict) -> None:
    """Append one JSON line to a JSONL file. Creates if missing."""
    clean = _sanitize_for_json(record)
    with open(path, "a") as f:
        f.write(json.dumps(clean) + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# § 5  Evaluation
# ══════════════════════════════════════════════════════════════════════════════

def evaluate(model: V12Model, cfg: V12Config) -> dict:
    """Evaluate on held-out shards. Returns loss, perplexity, and compressor metrics."""
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
    target_tokens = 50_000
    tokens_seen = 0

    while tokens_seen < target_tokens:
        input_ids_np, targets_np = next(eval_loader)
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

    # Instrumented forward on one batch for compressor metrics
    input_ids_np, _ = next(eval_loader)
    input_ids = mx.array(input_ids_np)
    _, compressor_metrics = model.forward_instrumented(input_ids)

    # Print compressor metrics
    pass_names = ("L0↑", "L1↑", "L2↑", "L3", "L2↓", "L1↓", "L0↓")
    n_asc = 4  # passes 0-3 are ascending (L0↑, L1↑, L2↑, L3_apex)

    print("  ┌─ S3 gates ──────────────────────────────────────┐", file=sys.stderr)
    for pi, pname in enumerate(pass_names):
        gates = compressor_metrics["s3_gates"][pi]
        print(f"  │ {pname:4s}: disp={gates[0]:.3f}  conv={gates[1]:.3f}  "
              f"intg={gates[2]:.3f}", file=sys.stderr)
    print("  ├─ S5 reweight ───────────────────────────────────┤", file=sys.stderr)
    mg = compressor_metrics["s5_reweight"]
    print(f"  │ {' '.join(f'{pn}={g:.3f}' for pn, g in zip(pass_names, mg))}",
          file=sys.stderr)
    print("  ├─ S2 coordination ───────────────────────────────┤", file=sys.stderr)
    s2_conflict = compressor_metrics.get("s2_conflict", [])
    s2_scales = compressor_metrics.get("s2_scales", [])
    s2_names = ("L0↑→L1↑", "L1↑→L2↑", "L2↑→L3", "L3→L2↓", "L2↓→L1↓", "L1↓→L0↓")
    for ti in range(len(s2_conflict)):
        cs = s2_conflict[ti]
        sc = s2_scales[ti] if ti < len(s2_scales) else 0.0
        warn = "  ⚠" if cs < 0 else ""
        print(f"  │ {s2_names[ti]:8s}: cos={cs:+.3f}  scale={sc:.4f}{warn}",
              file=sys.stderr)
    print("  ├─ Compression ───────────────────────────────────┤", file=sys.stderr)
    cr = compressor_metrics["pass_compression"]
    pd = compressor_metrics["pass_phi_dev"]
    for pi, pname in enumerate(pass_names):
        phi_mark = "←φ" if pd[pi] < 0.05 else "   "
        print(f"  │ {pname:4s}: ratio={cr[pi]:.3f}  φ-dev={pd[pi]:.3f} {phi_mark}",
              file=sys.stderr)
    print("  ├─ Register norms ────────────────────────────────┤", file=sys.stderr)
    for bname, norms in compressor_metrics["register_norms"].items():
        print(f"  │ {bname:12s}: {' '.join(f'{n:.2f}' for n in norms)}",
              file=sys.stderr)
    print("  └─────────────────────────────────────────────────┘", file=sys.stderr)

    # Compute gate stats (kernel pathway)
    if "compute_gate_mean" in compressor_metrics:
        cg_mean = compressor_metrics["compute_gate_mean"]
        cg_max = compressor_metrics["compute_gate_max"]
        cg_active = compressor_metrics["compute_gate_active"]
        print(f"  🔧 Compute gate: mean={cg_mean:.4f}  max={cg_max:.4f}  "
              f"active(>0.5)={cg_active:.1%}", file=sys.stderr)

    # Algedonic alert (Beer's fire alarm)
    alarm_factors = compressor_metrics.get("alarm_factors")
    eff_s5 = compressor_metrics.get("effective_s5_gates")
    if alarm_factors:
        pass_names_alarm = ("L0↑", "L1↑", "L2↑", "L3", "L2↓", "L1↓", "L0↓")
        # Detect any non-neutral alarm (factor != 1.0)
        any_alarm = any(abs(f - 1.0) > 0.01 for f in alarm_factors)
        symbol = "🚨" if any_alarm else "🔕"
        parts = [f"{pn}={f:.3f}" for pn, f in zip(pass_names_alarm, alarm_factors)]
        print(f"  {symbol} Algedonic: {' '.join(parts)}"
              f"  {'(active)' if any_alarm else '(silent)'}",
              file=sys.stderr)
        if eff_s5:
            parts2 = [f"{pn}={g:.3f}" for pn, g in zip(pass_names_alarm, eff_s5)]
            print(f"     effective gates: {' '.join(parts2)}",
                  file=sys.stderr)
    # Holographic intermediate losses
    holo = compressor_metrics.get("holo_losses")
    if holo:
        pass_names_h = ("L0↑", "L1↑", "L2↑", "L3", "L2↓", "L1↓", "L0↓")
        parts = [f"{pn}={h:.3f}" for pn, h in zip(pass_names_h, holo)]
        print(f"  🔮 Holographic: {' '.join(parts)}", file=sys.stderr)

    # Crystal lattice diagnostics
    cmc = compressor_metrics.get("combinator_mirror_cosines")
    if cmc:
        kbc_cos = compressor_metrics.get("crystal_kbc_plate_cos", 0)
        i_sep = compressor_metrics.get("crystal_i_separation_cos", 0)
        score = compressor_metrics.get("crystal_formation_score", 0)
        print(f"  💎 Crystal: K/B/C plate={kbc_cos:.3f}  I separation={i_sep:.3f}"
              f"  score={score:.3f}", file=sys.stderr)
        pairs = " ".join(f"{k}={v:.3f}" for k, v in cmc.items())
        print(f"     mirrors: {pairs}", file=sys.stderr)
    dm_cos = compressor_metrics.get("dispatch_mirror_mean_cos")
    if dm_cos is not None:
        dm_min = compressor_metrics.get("dispatch_mirror_min_cos", 0)
        dm_max = compressor_metrics.get("dispatch_mirror_max_cos", 0)
        print(f"  🔭 Dispatch mirrors: mean={dm_cos:.3f}  "
              f"range=[{dm_min:.3f}, {dm_max:.3f}]", file=sys.stderr)
    dc = compressor_metrics.get("dispatch_conditioned_angles_deg")
    if dc:
        parts = " ".join(f"{k}={v:.0f}°" for k, v in dc.items())
        print(f"  📐 Conditioned angles: {parts}", file=sys.stderr)

    # Retrieval summary (v12)
    retrieval_gate_means = compressor_metrics.get("retrieval_gate_means")
    retrieval_register_norms = compressor_metrics.get("retrieval_register_norms")
    retrieval_write_gates = compressor_metrics.get("retrieval_write_gates")
    if retrieval_gate_means or retrieval_register_norms or retrieval_write_gates:
        parts = []
        if retrieval_gate_means:
            # retrieval_gate_means is a list of dicts (one per ascending pass)
            for pi, gm_dict in enumerate(retrieval_gate_means):
                if gm_dict:
                    avg_gate = sum(gm_dict.values()) / len(gm_dict)
                    parts.append(f"pass{pi}_gate={avg_gate:.3f}")
        if retrieval_register_norms:
            norms_str = " ".join(f"reg{i}={n:.2f}"
                                 for i, n in enumerate(retrieval_register_norms))
            parts.append(f"reg_norms=[{norms_str}]")
        if retrieval_write_gates:
            wg_str = " ".join(f"{g:.3f}" for g in retrieval_write_gates)
            parts.append(f"write_gates=[{wg_str}]")
        print(f"  🔍 Retrieval: {' '.join(parts)}", file=sys.stderr)

    # Log alarm raw metrics for offline threshold analysis
    alarm_metrics_raw = compressor_metrics.get("alarm_metrics")
    if alarm_metrics_raw:
        # Named sections matching AlgedonicAlert.INPUT_DIM (7 passes, 6 transitions, 8 banks)
        alarm_named = {}
        idx = 0
        for section, count in [
            ("s3_gate_means", 7), ("s3_gate_mins", 7),
            ("s2_conflicts", 6), ("dispatch_weights", 4),
            ("dispatch_entropy", 1), ("compute_gate", 2),
            ("cycle_continue", 6), ("effective_cycles", 3),
            ("raw_delta_norms", 7), ("gated_delta_norms", 7),
            ("suppression_ratios", 7), ("register_norms", 8),
        ]:
            alarm_named[section] = alarm_metrics_raw[idx:idx+count]
            idx += count
        compressor_metrics["alarm_metrics_named"] = alarm_named

    result = {
        "loss": avg_loss,
        "ppl": ppl,
        "r": r,
    }
    result.update(compressor_metrics)
    return result


# ══════════════════════════════════════════════════════════════════════════════
# § 6  Tournament evolution
# ══════════════════════════════════════════════════════════════════════════════

MUTANT_STRATEGIES = {
    "conservative": 0.25,
    "explorer":     1.0,
    "targeted":     2.0,
    "random":       4.0,
    "intelligence": 0.5,   # S4→S5: Beer's intelligence proposal channel
}

# Vote weights: intelligence gets 2 votes in consensus (others get 1).
# With threshold=3: S4 needs only 1 ally, not 2.
STRATEGY_VOTE_WEIGHTS = [1, 1, 1, 1, 2]  # matches MUTANT_STRATEGIES order

# S4 module path fragments — intelligence strategy amplifies these
S4_MODULES = ('s4.', 's4_desc.', 'meta_s4.')

# ── Module → pass mapping for alarm-targeted mutation budget ──
# Each module is used in one or more passes. Alarm-targeting weights
# the mutation budget toward passes that are struggling (alarm < 1.0).
#
# Ascending: passes 0, 1, 2 (L0↑, L1↑, L2_apex)
# Descending: passes 3, 4 (L1↓, L0↓)
MODULE_PASS_MAP = {
    # Ascending shared (3 passes)
    "prep":             [0, 1, 2],
    "stride_stack":     [0, 1, 2],
    "s4":               [0, 1, 2, 3],
    "mod_projs":        [0, 1, 2, 3],
    # Universal shared (all 7 passes)
    "stride_stack":         [0, 1, 2, 3, 4, 5, 6],
    "combinator_dispatch":  [0, 1, 2, 3, 4, 5, 6],
    "combinator_integrate": [0, 1, 2, 3, 4, 5, 6],
    # Descending shared (3 desc passes)
    "s4_desc":              [4, 5, 6],
    "mod_projs_desc":       [4, 5, 6],
    # Per-pass S3
    "s3_passes.0":      [0],
    "s3_passes.1":      [1],
    "s3_passes.2":      [2],
    "s3_passes.3":      [3],
    "s3_passes.4":      [4],
    "s3_passes.5":      [5],
    "s3_passes.6":      [6],
}
# Modules not in the map get mean alarm need (S5, S2, meta, embed, etc.)


def _compute_alarm_depth_weights(
    alarm_factors: list[float] | None,
    model_modules: list[tuple[str, object]],
) -> dict[str, float] | None:
    """Compute per-module depth weights from alarm factors.

    alarm_need = max(0, 2.0 - alarm_factor):
      alarm=0.75 → need=1.25 (high priority — system is in pain)
      alarm=1.0  → need=1.0  (neutral)
      alarm=2.0  → need=0.0  (system is healthy, don't touch)

    Returns depth_weights dict for propose_mutations, or None if
    no alarm data available.
    """
    if not alarm_factors or len(alarm_factors) < 5:
        return None

    alarm_need = [max(0.0, 2.0 - af) for af in alarm_factors]
    mean_need = sum(alarm_need) / len(alarm_need)
    if mean_need < 1e-6:
        return None  # everything healthy, no targeting needed

    depth_weights = {}
    for path, _mod in model_modules:
        # Find which passes this module serves
        passes = None
        for prefix, pass_indices in MODULE_PASS_MAP.items():
            if path == prefix or path.startswith(prefix + "."):
                passes = pass_indices
                break

        if passes is not None:
            # Module weight = mean alarm_need across its passes
            mod_need = sum(alarm_need[p] for p in passes) / len(passes)
        else:
            # Modules not mapped to a specific pass get mean need
            mod_need = mean_need

        # Scale: 1.0 + need ensures no module gets zero budget
        # Cap at 4.0 to prevent extreme concentration
        depth_weights[path] = min(4.0, 1.0 + mod_need)

    return depth_weights


def _compute_etch_threshold_multipliers(
    cfg,
    model_modules: list[tuple[str, object]],
) -> dict[str, float]:
    """Compute per-module etch threshold multipliers from the depth map.

    Uses MODULE_PASS_MAP to find which passes each module serves,
    then averages the per-pass multiplier from cfg.pass_etch_multiplier.

    Shallow passes (low multiplier) → lower percentile threshold → more votes.
    Deep passes (multiplier=1.0) → standard threshold.
    """
    multipliers = cfg.pass_etch_multiplier
    if not multipliers or len(multipliers) < 2:
        return {}

    result = {}
    for path, _mod in model_modules:
        passes = None
        for prefix, pass_indices in MODULE_PASS_MAP.items():
            if path == prefix or path.startswith(prefix + "."):
                passes = pass_indices
                break

        if passes is not None:
            # Average multiplier across the passes this module serves
            result[path] = sum(multipliers[p] for p in passes if p < len(multipliers)) / len(passes)
        else:
            result[path] = 1.0  # unmapped modules get standard threshold

    return result


def run_tournament(
    model, cfg, step, total_ternary, eval_loader,
    base_pct, rng,
    row_importance, col_importance, grad_direction,
    structured_eval_loader=None,
    alarm_factors=None,
) -> dict:
    """One evolutionary generation via S4-guided consensus mutation.

    S4-guided evolution (session 082): three improvements over blind
    consensus:

    1. Alarm-targeted budget: mutation budget concentrates on modules
       whose passes are struggling (alarm < 1.0 = pain). Healthy
       modules get baseline budget; stressed modules get up to 4×.

    2. S4 2-vote consensus: the intelligence strategy gets 2 votes
       instead of 1 in the 3/5 consensus. S4 only needs one ally,
       not two, because it has contextual awareness the random
       strategies lack.

    3. Alarm-improvement fitness: accept if alarm health improves
       OR loss improves. Structural improvements (resolving conflicts,
       opening suppressed passes) are valuable even before they
       reduce loss.

    Flow:
      1. Compute alarm-targeted depth weights from alarm_factors
      2. Each strategy proposes mutations (alarm-weighted budgets)
      3. Find consensus with S4's 2× votes (threshold=3)
      4. Apply consensus flips
      5. Accept if loss improves OR alarm health improves
    """
    # Get fixed eval batches
    prose_ids_np, prose_tgts_np = next(eval_loader)
    prose_ids = mx.array(prose_ids_np)
    prose_tgts = mx.array(prose_tgts_np)

    has_structured = structured_eval_loader is not None
    if has_structured:
        struct_ids_np, struct_tgts_np = next(structured_eval_loader)
        struct_ids = mx.array(struct_ids_np)
        struct_tgts = mx.array(struct_tgts_np)

    def _eval_loss():
        """Evaluate relational loss r on all data types."""
        _, loss_prose = model(prose_ids, prose_tgts)
        mx.eval(loss_prose)
        r_prose = (float(loss_prose.item()) - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE)

        if has_structured:
            _, loss_struct = model(struct_ids, struct_tgts)
            mx.eval(loss_struct)
            r_struct = (float(loss_struct.item()) - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE)
            return max(r_prose, r_struct), r_prose, r_struct
        else:
            return r_prose, r_prose, None

    def _eval_alarm_health():
        """Evaluate alarm health score via forward_instrumented.

        Health = mean(alarm_factors). Higher = healthier.
        Returns (health_score, alarm_factors_list) or (None, None)
        if instrumented forward fails.
        """
        try:
            _, metrics = model.forward_instrumented(prose_ids)
            af = metrics.get("alarm_factors")
            if af:
                health = sum(af) / len(af)
                return health, af
        except Exception:
            pass
        return None, None

    champion_loss, champion_prose, champion_struct = _eval_loss()
    champion_health, champion_alarm = _eval_alarm_health()
    champion_snapshot = save_topology(model)

    base_budget = bios_mutation_budget(step, cfg.total_steps, total_ternary, base_pct)
    if base_budget == 0:
        return {"champion_loss": champion_loss, "budget": 0,
                "accepted": None, "accepted_loss": champion_loss, "frozen": True,
                "prose_loss": champion_prose, "struct_loss": champion_struct,
                "actual_flips": 0, "n_rows_mutated": 0, "mutation_map": None,
                "consensus_stats": None,
                "alarm_health_before": champion_health,
                "alarm_health_after": champion_health}

    # ── Alarm-targeted depth weights ─────────────────────────
    # Use alarm_factors to concentrate mutations on struggling passes.
    # alarm_factors come from the last eval (cached by training loop).
    modules = list(_walk_ternary_modules(model))
    depth_weights = _compute_alarm_depth_weights(alarm_factors, modules)

    # ── Phase 1: Each strategy proposes mutations independently ──
    proposals = []
    strategy_budgets = []
    for strategy_name, scale in MUTANT_STRATEGIES.items():
        strategy_budget = max(1, int(base_budget * scale))
        strategy_budgets.append(strategy_budget)

        strategy_rng = np.random.RandomState(
            int(rng.randint(0, 2**31)) ^ (hash(strategy_name) & 0x7FFFFFFF))

        guided_frac = cfg.guided_fraction if strategy_name != "random" else 0.0

        # Intelligence strategy: S4→S5 proposal channel (Beer's VSM).
        # 2 votes in consensus. Fully gradient-guided with S4 module
        # amplification. Gets alarm-targeted depth weights like everyone
        # else, PLUS S4-specific boosting.
        if strategy_name == "intelligence":
            guided_frac = 1.0
            ri_use = {}
            gd_use = {}
            for path in (row_importance or {}):
                is_s4 = any(s in path for s in S4_MODULES)
                boost = cfg.s4_boost if is_s4 else (1.0 / cfg.s4_boost)
                ri_use[path] = row_importance[path] * boost
                if path in (grad_direction or {}):
                    gd_use[path] = grad_direction[path]
            prop = propose_mutations(
                model, strategy_budget, strategy_rng,
                sign_flip_rate=cfg.sign_flip_rate,
                row_importance=ri_use if ri_use else None,
                col_importance=col_importance if col_importance else None,
                grad_direction=gd_use if gd_use else None,
                guided_fraction=guided_frac,
                depth_weights=depth_weights,
            )
        else:
            prop = propose_mutations(
                model, strategy_budget, strategy_rng,
                sign_flip_rate=cfg.sign_flip_rate,
                row_importance=row_importance if row_importance else None,
                col_importance=col_importance if col_importance else None,
                grad_direction=grad_direction if grad_direction else None,
                guided_fraction=guided_frac,
                depth_weights=depth_weights,
            )
        proposals.append(prop)

    # ── Phase 2: Find consensus — S4 gets 2 votes ───────────
    consensus, consensus_stats = find_consensus(
        proposals, threshold=3,
        vote_weights=STRATEGY_VOTE_WEIGHTS)

    if not consensus or consensus_stats["consensus_flips"] == 0:
        return {
            "champion_loss": champion_loss,
            "budget": base_budget,
            "accepted": None,
            "accepted_loss": champion_loss,
            "frozen": False,
            "prose_loss": champion_prose,
            "struct_loss": champion_struct,
            "actual_flips": 0,
            "n_rows_mutated": 0,
            "mutation_map": None,
            "consensus_stats": consensus_stats,
            "alarm_health_before": champion_health,
            "alarm_health_after": champion_health,
        }

    # ── Phase 3: Apply consensus flips ──
    actual_flips, mutation_map = apply_consensus(model, consensus)

    # ── Phase 4: Accept if loss improves OR alarm health improves ──
    mutant_loss, mutant_prose, mutant_struct = _eval_loss()
    mutant_health, mutant_alarm = _eval_alarm_health()

    # Acceptance criteria (AND on loss direction, OR on signal source):
    #   1. Loss path: loss improved by at least min_delta (noise floor)
    #   2. Alarm path: alarm health improved by at least alarm_min_delta
    #      AND loss didn't get worse.
    #
    # Both paths enforce noise floors. Without them, measurement noise
    # from a single eval batch (~0.001) gets accepted, and the resulting
    # sign flips cause routing ripple effects that accumulate silently.
    # (v11-holo 10K collapse: alarm accepted +0.0003 to +0.0024 loss
    #  deltas — small regressions accumulated into catastrophe.)
    #
    # The alarm noise floor is separately configurable because alarm
    # health ∈ [0, 2] has different scale than relational loss ∈ [0, 1].
    loss_improved = (champion_loss - mutant_loss) >= cfg.evolution_min_delta
    alarm_improved = (champion_health is not None
                      and mutant_health is not None
                      and (mutant_health - champion_health) >= cfg.evolution_alarm_min_delta
                      and mutant_loss <= champion_loss)  # loss must not get worse

    if loss_improved or alarm_improved:
        reason = "loss" if loss_improved else "alarm"
        accepted = f"consensus_{reason}"
    else:
        # Revert
        load_topology(model, champion_snapshot)
        accepted = None
        mutant_loss = champion_loss
        mutant_prose = champion_prose
        mutant_struct = champion_struct
        mutant_health = champion_health
        mutation_map = None
        actual_flips = 0

    n_rows_mutated = sum(len(v) for v in mutation_map.values()) if mutation_map else 0

    return {
        "champion_loss": champion_loss,
        "budget": base_budget,
        "accepted": accepted,
        "accepted_loss": mutant_loss,
        "frozen": False,
        "prose_loss": mutant_prose,
        "struct_loss": mutant_struct,
        "actual_flips": actual_flips,
        "n_rows_mutated": n_rows_mutated,
        "mutation_map": mutation_map,
        "consensus_stats": consensus_stats,
        "alarm_health_before": champion_health,
        "alarm_health_after": mutant_health,
    }


# ══════════════════════════════════════════════════════════════════════════════
# § 6b  Adam accumulator decay after accepted mutations
# ══════════════════════════════════════════════════════════════════════════════

def decay_adam_state(optimizer, model, decay: float = 0.1,
                     mutation_map: dict[str, set[int]] | None = None) -> int:
    """Surgically decay Adam m/v accumulators for mutated gamma entries only.

    After an accepted topology mutation, the ternary weights have changed
    but Adam's running mean (m) and variance (v) still reflect gradients
    from the old topology. This creates a tug-of-war: the momentum points
    in the old direction while the gradient now points differently.

    The key insight: only rows that were actually mutated need their Adam
    state reset. A mutation touching 26K weights out of 131M affects maybe
    a few hundred unique rows per module. Decaying ALL gamma entries
    (the old behavior) cold-starts the entire model's optimizer state —
    causing the CE spike. Surgical decay leaves untouched rows with full
    momentum, so only the ~0.02% of the model that changed needs to
    re-adapt.

    Args:
        optimizer:    the AdamW optimizer
        model:        the model (for walking ternary modules)
        decay:        scale factor for m/v (0.0 = full reset, 1.0 = no change)
        mutation_map: dict mapping module_path → set of mutated row indices.
                      If None, falls back to decaying ALL gamma entries
                      (legacy behavior — still a sledgehammer, but safe).

    Returns:
        Number of gamma entries (rows) that were decayed.
    """
    if decay >= 1.0 or not optimizer.state:
        return 0

    # Build map: gamma_path → set of row indices to decay
    gamma_decay_map: dict[str, set[int] | None] = {}
    for path, mod in _walk_ternary_modules(model):
        if isinstance(mod, TernaryLinear):
            gamma_path = f"{path}.gamma"
            if mutation_map is not None:
                # Only decay rows that were mutated in this module
                if path in mutation_map:
                    gamma_decay_map[gamma_path] = mutation_map[path]
                # If this module wasn't mutated, skip it entirely
            else:
                # Legacy fallback: decay all rows
                gamma_decay_map[gamma_path] = None  # None = all rows

    if not gamma_decay_map:
        return 0

    n_decayed = 0

    # Navigate optimizer state tree and decay m/v for targeted gamma entries
    def _decay_tree(state_node, param_path_parts, depth=0):
        nonlocal n_decayed
        if isinstance(state_node, dict):
            for key, val in state_node.items():
                current_path = ".".join(param_path_parts + [key])
                if current_path in gamma_decay_map and isinstance(val, dict):
                    rows = gamma_decay_map[current_path]
                    for moment_key in ("m", "v"):
                        if moment_key in val and isinstance(val[moment_key], mx.array):
                            if rows is None:
                                # Legacy: decay entire vector
                                val[moment_key] = val[moment_key] * decay
                                n_decayed += val[moment_key].size
                            else:
                                # Surgical: only decay specific row indices
                                arr = val[moment_key]
                                row_indices = mx.array(sorted(rows))
                                updates = arr[row_indices] * decay
                                arr = arr.at[row_indices].add(updates - arr[row_indices])
                                val[moment_key] = arr
                                n_decayed += len(rows)
                else:
                    _decay_tree(val, param_path_parts + [key], depth + 1)
        elif isinstance(state_node, list):
            for i, val in enumerate(state_node):
                _decay_tree(val, param_path_parts + [str(i)], depth + 1)

    if isinstance(optimizer.state, list):
        for group in optimizer.state:
            _decay_tree(group, [], 0)
    elif isinstance(optimizer.state, dict):
        _decay_tree(optimizer.state, [], 0)

    mx.eval(optimizer.state)
    return n_decayed


# ══════════════════════════════════════════════════════════════════════════════
# § 7  Checkpointing
# ══════════════════════════════════════════════════════════════════════════════

def save_checkpoint(model, optimizer, step, cfg, checkpoint_dir,
                    train_losses, total_generations, total_accepted,
                    eval_metrics, row_importance, col_importance,
                    grad_direction, mutation_rng,
                    etch_states=None, total_etched=0,
                    train_loader=None):
    step_dir = checkpoint_dir / f"step_{step:06d}"
    step_dir.mkdir(parents=True, exist_ok=True)

    flat = tree_flatten(model.parameters())
    mx.savez(str(step_dir / "model.npz"), **{k: v for k, v in flat})

    opt_flat = tree_flatten(optimizer.state)
    mx.savez(str(step_dir / "optimizer.npz"), **{k: v for k, v in opt_flat})

    imp_data = {}
    for path, arr in row_importance.items():
        imp_data[f"row.{path}"] = arr
    for path, arr in col_importance.items():
        imp_data[f"col.{path}"] = arr
    for path, arr in grad_direction.items():
        imp_data[f"dir.{path}"] = arr
    if imp_data:
        np.savez_compressed(str(step_dir / "importance.npz"), **imp_data)

    rng_state = mutation_rng.get_state()
    np.savez_compressed(str(step_dir / "rng.npz"),
                        state_array=rng_state[1],
                        pos=np.array([rng_state[2]], dtype=np.int64))

    # Save etch states
    if etch_states is not None:
        save_etch_states(etch_states, str(step_dir / "etch_states.npz"))

    # Capture dispatch EMA for analysis
    dispatch_ema = None
    if hasattr(model, '_last_dispatch_ema'):
        ema = model._last_dispatch_ema
        if ema is not None:
            from kernel import COMBINATOR_NAMES
            dispatch_ema = {
                COMBINATOR_NAMES[i]: float(ema[i])
                for i in range(min(len(COMBINATOR_NAMES), len(ema)))
            }

    # Crystal formation diagnostics (mirror geometry)
    crystal_state = compute_crystal_diagnostics(model)

    state = {
        "step": step,
        "total_generations": total_generations,
        "total_accepted": total_accepted,
        "total_etched": total_etched,
        "train_losses_last50": train_losses[-50:],
        "eval_metrics": eval_metrics or {},
        "dispatch_ema": dispatch_ema,
        "crystal": crystal_state,
        "data_loader": train_loader.save_state() if train_loader else {},
        "config": {
            "d_model": cfg.d_model, "vocab_size": cfg.vocab_size,
            "batch_size": cfg.batch_size, "total_steps": cfg.total_steps,
            "lr": cfg.lr, "seq_len": cfg.seq_len,
            "mix_ratio": cfg.mix_ratio,
            "holo_lambda": cfg.holo_lambda,
            "holo_warmup_steps": cfg.holo_warmup_steps,
            "holo_ramp_steps": cfg.holo_ramp_steps,
            "desc_stride_reverse": cfg.desc_stride_reverse,
            "fractal_stride_bands": cfg.fractal_stride_bands,
            "etch_max_flips_per_event": cfg.etch_max_flips_per_event,
            "rel_lambda": cfg.rel_lambda,
        },
    }
    (step_dir / "state.json").write_text(json.dumps(state, indent=2))
    print(f"💾 Checkpoint saved: {step_dir}", file=sys.stderr, flush=True)


def find_latest_checkpoint(checkpoint_dir):
    if not checkpoint_dir.exists():
        return None
    step_dirs = sorted(checkpoint_dir.glob("step_*"))
    for d in reversed(step_dirs):
        if (d / "state.json").exists() and (d / "model.npz").exists():
            return d
    return None


def load_checkpoint(checkpoint_dir, model, optimizer):
    weights = dict(mx.load(str(checkpoint_dir / "model.npz")))
    model.load_weights(list(weights.items()), strict=False)
    mx.eval(model.parameters())
    freeze_ternary_weights(model)
    restore_ternary(model)

    opt_path = checkpoint_dir / "optimizer.npz"
    if opt_path.exists():
        from mlx.utils import tree_unflatten
        opt_state = dict(mx.load(str(opt_path)))
        optimizer.state = tree_unflatten(list(opt_state.items()))
        mx.eval(optimizer.state)

    row_imp, col_imp, grad_dir = {}, {}, {}
    imp_path = checkpoint_dir / "importance.npz"
    if imp_path.exists():
        data = dict(np.load(str(imp_path)))
        for key, arr in data.items():
            if key.startswith("row."): row_imp[key[4:]] = arr
            elif key.startswith("col."): col_imp[key[4:]] = arr
            elif key.startswith("dir."): grad_dir[key[4:]] = arr

    mutation_rng = np.random.RandomState()
    rng_path = checkpoint_dir / "rng.npz"
    if rng_path.exists():
        rng_data = np.load(str(rng_path))
        mutation_rng.set_state(("MT19937", rng_data["state_array"],
                                int(rng_data["pos"][0]), 0, 0.0))

    state = json.loads((checkpoint_dir / "state.json").read_text())
    print(f"📂 Loaded: {checkpoint_dir} (step {state['step']})", file=sys.stderr)
    return state["step"], state, row_imp, col_imp, grad_dir, mutation_rng, state.get("data_loader", {})


# ══════════════════════════════════════════════════════════════════════════════
# § 8  Main training loop
# ══════════════════════════════════════════════════════════════════════════════

def train(cfg: V12Config, args: argparse.Namespace) -> None:
    checkpoint_dir = Path(cfg.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # ── Banner ────────────────────────────────────────────────
    print("=" * 72, file=sys.stderr)
    print("  v12 — KIBC + M Retrieval VSM (5-pass, 9 strides) on Dolma Prose", file=sys.stderr)
    print("  Qwen3 BBPE tokenizer, next-token prediction", file=sys.stderr)
    print("=" * 72, file=sys.stderr)

    # ── Model ─────────────────────────────────────────────────
    model = create_model(cfg)
    freeze_ternary_weights(model)

    param_counts = count_parameters(model)
    total_ternary = count_ternary_weights(model)

    print(f"\n  d_model={cfg.d_model}  n_heads={cfg.n_heads}  "
          f"strides={cfg.strides}", file=sys.stderr)
    print(f"  d_ff={cfg.d_ff}  n_passes={cfg.n_passes}  "
          f"d_register={cfg.d_register}  alpha={cfg.alpha}", file=sys.stderr)
    print(f"  params: total={param_counts['total']:,}  "
          f"trainable={param_counts['trainable']:,}  "
          f"ternary={total_ternary:,}", file=sys.stderr)
    print(f"  vocab={cfg.vocab_size}  seq_len={cfg.seq_len}  "
          f"tokens/step={cfg.tokens_per_step:,}", file=sys.stderr)

    # ── Optimizer ─────────────────────────────────────────────
    optimizer = optim.Adam(learning_rate=cfg.lr, betas=[0.9, 0.999])

    # ── value_and_grad ────────────────────────────────────────
    loss_and_grad = nn.value_and_grad(model, loss_fn)

    # ── Data ──────────────────────────────────────────────────
    prose_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=0,
        shard_end=cfg.n_train_shards,
    )

    if cfg.mix_ratio > 0 and Path(cfg.structured_shard).exists():
        train_loader = MixedDataLoader(
            prose_loader=prose_loader,
            structured_path=cfg.structured_shard,
            mix_ratio=cfg.mix_ratio,
            seq_len=cfg.seq_len,
            batch_size=cfg.batch_size,
        )
        print(f"  🔀 Mixed data: {cfg.mix_ratio:.0%} structured, "
              f"{1-cfg.mix_ratio:.0%} prose", file=sys.stderr)
    else:
        train_loader = prose_loader
    eval_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=cfg.n_train_shards,
        shard_end=cfg.n_train_shards + cfg.n_eval_shards,
        seed=8888,
    )

    # Structured eval loader for mixed-data-aware evolution.
    # Mutations must help BOTH prose and structured data to be accepted.
    structured_eval_loader = None
    if cfg.mix_ratio > 0 and Path(cfg.structured_shard).exists():
        structured_eval_loader = MixedDataLoader(
            prose_loader=ShardedDataLoader(
                data_dir=cfg.data_dir,
                batch_size=cfg.batch_size,
                seq_len=cfg.seq_len,
                shard_start=cfg.n_train_shards,
                shard_end=cfg.n_train_shards + cfg.n_eval_shards,
                seed=7777,
            ),
            structured_path=cfg.structured_shard,
            mix_ratio=1.0,  # always structured for this loader
            seq_len=cfg.seq_len,
            batch_size=cfg.batch_size,
            seed=7777,
        )

    # ── EMA importance maps (for legacy evolution) ──────────────
    row_importance: dict[str, np.ndarray] = {}
    col_importance: dict[str, np.ndarray] = {}
    grad_direction: dict[str, np.ndarray] = {}
    imp_alpha = 0.1
    mutation_rng = np.random.RandomState(42)

    # ── Etch states (gradient-directed topology shaping) ──────
    etch_states: dict | None = None
    if cfg.use_etching:
        etch_states = init_etch_states(model)
        n_etch_modules = len(etch_states)
        n_signal_params = sum(
            s.out_features * s.in_features * 3 for s in etch_states.values()
        )
        print(f"  etch: {n_etch_modules} modules, "
              f"signal_planes={n_signal_params:,} ternary values "
              f"({n_signal_params * 2 / 8 / 1024:.0f} KB)",
              file=sys.stderr)
    total_etched = 0

    # ── State ─────────────────────────────────────────────────
    start_step = 0
    train_losses: list[float] = []
    last_eval = None
    total_generations = 0
    total_accepted = 0
    loss_window: deque[float] = deque(maxlen=50)

    # ── Resume ────────────────────────────────────────────────
    if args.resume:
        if args.resume is True:
            # --resume with no argument: find latest
            ckpt = find_latest_checkpoint(checkpoint_dir)
        else:
            # --resume step_003000 or --resume /full/path/step_003000
            resume_path = Path(args.resume)
            if not resume_path.is_absolute():
                resume_path = checkpoint_dir / resume_path
            ckpt = resume_path if resume_path.exists() else None
        if ckpt:
            start_step, state, row_importance, col_importance, \
                grad_direction, mutation_rng, dl_state = load_checkpoint(ckpt, model, optimizer)
            train_losses = state.get("train_losses_last50", [])
            total_generations = state.get("total_generations", 0)
            total_accepted = state.get("total_accepted", 0)
            total_etched = state.get("total_etched", 0)
            last_eval = state.get("eval_metrics")
            loss_window.extend(train_losses[-50:])
            if dl_state:
                train_loader.load_state(dl_state)
            # Restore etch states from checkpoint
            if etch_states is not None:
                etch_path = ckpt / "etch_states.npz"
                load_etch_states(etch_states, str(etch_path))
                print(f"  etch: loaded signal planes from {etch_path}",
                      file=sys.stderr)
        else:
            print("  ⚠  No checkpoint found, starting fresh.", file=sys.stderr)

    # ── Warm-up optimizer ─────────────────────────────────────
    if not args.resume or not optimizer.state:
        ids_np, tgts_np = next(train_loader)
        ids = mx.array(ids_np)
        tgts = mx.array(tgts_np)
        lv, grads = loss_and_grad(model, ids, tgts)
        mx.eval(lv, grads)
        grads = normalize_shared_grads(grads)
        grads = zero_ternary_grads(model, grads)
        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state)
        restore_ternary(model)

    print(f"\n  lr={cfg.lr}  warmup={cfg.warmup_steps}  "
          f"total_steps={cfg.total_steps}", file=sys.stderr)
    print(f"  gen_interval={cfg.gen_interval}  base_pct={cfg.base_pct}  "
          f"grad_accum={cfg.grad_accum}", file=sys.stderr)
    desc_dir = "coarse→fine" if cfg.desc_stride_reverse else "fine→coarse (legacy)"
    fractal = " + fractal bands" if cfg.fractal_stride_bands else ""
    print(f"  🔄 Descending stride: {desc_dir}{fractal}", file=sys.stderr)
    if cfg.holo_lambda > 0:
        print(f"  🔮 Holographic loss: λ={cfg.holo_lambda}  "
              f"warmup={cfg.holo_warmup_steps}  ramp={cfg.holo_ramp_steps}",
              file=sys.stderr)
    print(f"  data: {cfg.data_dir}", file=sys.stderr)
    if start_step > 0:
        print(f"  Resuming from step {start_step}", file=sys.stderr)

    # ── Crystal lattice geometry loss setup (constant-target) ──
    # Session 119: 8×8 combinator embedding cosines → MSE vs measured constants.
    # No probe forwarding. Targets are fixed-point numbers from 4-model consensus.
    crystal_target = None
    crystal_weight = None
    if cfg.use_relational_loss:
        _tgt = np.array(cfg.crystal_cosine_targets, dtype=np.float32)
        _agr = np.array(cfg.crystal_cosine_agreements, dtype=np.float32)
        n_comb = _tgt.shape[0]
        # Extract upper triangle indices (28 unique pairs for 8 combinators)
        _triu_r, _triu_c = np.triu_indices(n_comb, k=1)
        crystal_target = mx.array(_tgt[_triu_r, _triu_c])  # (28,)
        crystal_weight = mx.array(_agr[_triu_r, _triu_c])   # (28,)
        # Normalize weights to sum to 1 for stable loss scale
        crystal_weight = crystal_weight / mx.sum(crystal_weight)
        _crystal_triu_r = mx.array(_triu_r.astype(np.int32))
        _crystal_triu_c = mx.array(_triu_c.astype(np.int32))
        print(f"  🔬 Crystal lattice loss: 8×8 embedding geometry, "
              f"λ={cfg.rel_lambda}, {len(_triu_r)} pairs, every step",
              file=sys.stderr)

    print("", file=sys.stderr, flush=True)

    # ══════════════════════════════════════════════════════════
    # Main loop
    # ══════════════════════════════════════════════════════════

    t_start = time.time()

    for step in range(start_step + 1, cfg.total_steps + 1):
        t0 = time.time()

        lr = cosine_lr(step, cfg.warmup_steps, cfg.total_steps,
                       cfg.lr, cfg.lr_floor_ratio)
        optimizer.learning_rate = lr

        # ── Holographic loss schedule ─────────────────────────
        holo_eff = holo_schedule(step, cfg)
        model._holo_lambda_effective = holo_eff

        # ── Gradient accumulation ─────────────────────────────
        accum_loss = 0.0
        accum_grads = None

        for _micro in range(cfg.grad_accum):
            ids_np, tgts_np = next(train_loader)
            ids = mx.array(ids_np)
            tgts = mx.array(tgts_np)

            lv, grads = loss_and_grad(model, ids, tgts)
            mx.eval(lv, grads)
            accum_loss += float(lv.item())

            if accum_grads is None:
                accum_grads = grads
            else:
                accum_grads = tree_map(lambda a, b: a + b, accum_grads, grads)

        # Average over micro-batches
        step_loss = accum_loss / cfg.grad_accum
        accum_grads = tree_map(lambda g: g / cfg.grad_accum, accum_grads)

        # ── Crystal lattice geometry loss (every step, cheap) ────
        # Agreement-weighted MSE between combinator embedding cosines
        # and measured cross-model consensus constants. No probe forwarding.
        rel_loss_val = 0.0
        if (crystal_target is not None
                and crystal_weight is not None
                and step > cfg.warmup_steps):

            def _crystal_loss_fn(model_inner):
                """Combinator embedding cosine MSE vs measured constants."""
                emb = model_inner.combinator_dispatch.combinator_embeddings  # (8, d_model)
                norms = mx.sqrt(mx.sum(emb * emb, axis=-1, keepdims=True) + 1e-8)
                emb_norm = emb / norms  # (8, d_model)
                cos_matrix = emb_norm @ emb_norm.T  # (8, 8)
                # Extract upper triangle (28 pairs)
                student_flat = cos_matrix[_crystal_triu_r, _crystal_triu_c]
                # Agreement-weighted MSE
                diff = student_flat - crystal_target
                return mx.sum(crystal_weight * diff * diff)

            rel_loss_grad_fn = nn.value_and_grad(model, _crystal_loss_fn)
            rel_lv, rel_grads = rel_loss_grad_fn(model)
            mx.eval(rel_lv, rel_grads)
            rel_loss_val = float(rel_lv.item())

            # Add scaled crystal lattice gradients to accumulated gradients
            accum_grads = tree_map(
                lambda a, b: a + cfg.rel_lambda * b,
                accum_grads, rel_grads)

        train_losses.append(step_loss)
        loss_window.append(step_loss)

        # ── EMA importance from gamma grads ───────────────────
        for path, mod in _walk_ternary_modules(model):
            if not isinstance(mod, TernaryLinear):
                continue
            parts = path.split(".")
            g_node = accum_grads
            for p in parts:
                if isinstance(g_node, dict):
                    g_node = g_node.get(p, {})
                elif isinstance(g_node, list) and p.isdigit():
                    g_node = g_node[int(p)]
                else:
                    g_node = {}; break
            gamma_grad = g_node.get("gamma") if isinstance(g_node, dict) else None
            if gamma_grad is not None:
                gg = np.array(mx.abs(gamma_grad))
                gs = np.array(gamma_grad)
                # Skip this step's EMA update if gradients contain NaN/Inf
                # (preserves prior importance rather than poisoning it)
                if np.all(np.isfinite(gg)):
                    if path in row_importance:
                        row_importance[path] = imp_alpha * gg + (1 - imp_alpha) * row_importance[path]
                        grad_direction[path] = imp_alpha * gs + (1 - imp_alpha) * grad_direction[path]
                    else:
                        row_importance[path] = gg
                        grad_direction[path] = gs
            if hasattr(mod, "_x_abs_mean"):
                xm = np.array(mod._x_abs_mean)
                if np.all(np.isfinite(xm)):
                    if path in col_importance:
                        col_importance[path] = imp_alpha * xm + (1 - imp_alpha) * col_importance[path]
                    else:
                        col_importance[path] = xm

        # ── Etch heat accumulation (every step, cheap) ─────────
        if etch_states is not None:
            accumulate_etch_heat(model, accum_grads, etch_states,
                                alpha=cfg.etch_heat_alpha)

        # ── Normalize shared + zero ternary ───────────────────
        accum_grads = normalize_shared_grads(accum_grads)
        accum_grads = zero_ternary_grads(model, accum_grads)

        # ── Gradient clipping ─────────────────────────────────
        grad_sq = [mx.sum(g * g) for _, g in tree_flatten(accum_grads)]
        mx.eval(*grad_sq)
        grad_norm = sum(float(g) for g in grad_sq) ** 0.5
        if cfg.grad_clip > 0 and grad_norm > cfg.grad_clip:
            s = cfg.grad_clip / (grad_norm + 1e-8)
            accum_grads = tree_map(lambda g: g * s, accum_grads)

        # ── Optimizer step ────────────────────────────────────
        optimizer.update(model, accum_grads)
        mx.eval(model.parameters(), optimizer.state)
        restore_ternary(model)

        dt = time.time() - t0

        # step_loss is r (relational loss) — recover total loss for display.
        # When holo is active, total_loss = CE + holo_lambda * Σ(intermediate CEs),
        # so the recovered value is NOT raw CE.
        total_loss = step_loss * (LOG_V - E_IRREDUCIBLE) + E_IRREDUCIBLE

        # Read raw CE from model cache (set during forward, before holo/reg terms)
        raw_ce = None
        if hasattr(model, '_last_ce'):
            mx.eval(model._last_ce)
            raw_ce = float(model._last_ce.item())

        # ── Log ───────────────────────────────────────────────
        if step % cfg.log_interval == 0 or step == start_step + 1:
            avg50 = sum(loss_window) / max(len(loss_window), 1)
            elapsed = time.time() - t_start
            tps = cfg.tokens_per_step / dt
            evo_str = ""
            if total_generations > 0:
                pct = total_accepted / total_generations * 100
                evo_str = f" | evo {total_accepted}/{total_generations} ({pct:.0f}%)"

            if holo_eff > 0 and raw_ce is not None:
                loss_str = f"CE={raw_ce:.3f} loss={total_loss:.3f}"
            else:
                loss_str = f"CE={total_loss:.3f}"

            # Dispatch summary for live monitoring
            dispatch_str = ""
            if hasattr(model, 'combinator_dispatch') and hasattr(model.combinator_dispatch, '_dispatch_weights'):
                dw = model.combinator_dispatch._dispatch_weights
                if dw is not None:
                    dw_mean = dw.mean(axis=(0, 1))
                    mx.eval(dw_mean)
                    from kernel import COMBINATOR_NAMES, N_COMBINATORS as N_COMB
                    dw_vals = [float(dw_mean[i].item()) for i in range(min(N_COMB, dw_mean.shape[0]))]
                    dispatch_parts = [f"{COMBINATOR_NAMES[i]}={dw_vals[i]:.2f}"
                                      for i in range(len(dw_vals))]
                    dispatch_str = " | " + " ".join(dispatch_parts)

            print(
                f"step {step:>6d} | r={step_loss:.4f} (avg50: {avg50:.4f})"
                f" | {loss_str} | lr {lr:.2e}"
                f" | {tps:.0f} tok/s"
                f"{dispatch_str}"
                f"{evo_str}"
                f" | {elapsed:.0f}s",
                file=sys.stderr, flush=True,
            )

            # Append lightweight training metrics to JSONL log
            train_record = {
                "step": step,
                "timestamp": time.time(),
                "r": step_loss,
                "total_loss": total_loss,
                "r_avg50": avg50,
                "lr": lr,
                "grad_norm": grad_norm,
                "tok_per_sec": tps,
                "elapsed": elapsed,
            }
            if raw_ce is not None:
                train_record["ce"] = raw_ce
            if holo_eff > 0:
                train_record["holo_lambda_effective"] = holo_eff
            # KL loss diagnostic
            if hasattr(model, '_last_kl_loss'):
                mx.eval(model._last_kl_loss)
                train_record["kl_loss"] = float(model._last_kl_loss.item())
            # Add retrieval gate means cached by HybridStrideStack during forward (v12)
            if hasattr(model, 'stride_stack') and hasattr(model.stride_stack, '_retrieval_gate_means'):
                rgm = model.stride_stack._retrieval_gate_means
                if rgm:
                    train_record["retrieval_gate_means_last"] = {
                        str(k): float(v) for k, v in rgm.items()
                    }

            # ── NEW: Dedicated plate + dispatch coordination metrics ──

            # Per-combinator dispatch weights (from last forward pass)
            if hasattr(model, 'combinator_dispatch') and hasattr(model.combinator_dispatch, '_dispatch_weights'):
                dw = model.combinator_dispatch._dispatch_weights
                if dw is not None:
                    dw_mean = dw.mean(axis=(0, 1))  # (n_comb,)
                    mx.eval(dw_mean)
                    dw_list = [float(dw_mean[i].item()) for i in range(min(4, dw_mean.shape[0]))]
                    train_record["dispatch_K"] = dw_list[0] if len(dw_list) > 0 else 0
                    train_record["dispatch_I"] = dw_list[1] if len(dw_list) > 1 else 0
                    train_record["dispatch_B"] = dw_list[2] if len(dw_list) > 2 else 0
                    train_record["dispatch_C"] = dw_list[3] if len(dw_list) > 3 else 0

            # EMA-smoothed dispatch weights (anti-oscillation diagnostic)
            if hasattr(model, '_last_dispatch_ema'):
                mx.eval(model._last_dispatch_ema)
                ema = model._last_dispatch_ema
                from kernel import COMBINATOR_NAMES
                for i, name in enumerate(COMBINATOR_NAMES):
                    if i < len(ema):
                        train_record[f"dispatch_ema_{name}"] = float(ema[i].item())

            # Relational loss (lambda kernel probes)
            if rel_loss_val > 0:
                train_record["rel_loss"] = rel_loss_val

            _append_jsonl(checkpoint_dir / "train_log.jsonl", train_record)

        # ── Signal plane update (etch) ─────────────────────────
        if (etch_states is not None
                and step >= cfg.etch_warmup
                and step % cfg.etch_signal_interval == 0):
            # S4 modulation: alarm factors weight the heat per module
            # Struggling passes → amplified heat → more etching
            _alarm_for_etch = (last_eval.get("alarm_factors")
                               if last_eval else None)
            etch_alarm_weights = None
            if _alarm_for_etch:
                modules = list(_walk_ternary_modules(model))
                dw = _compute_alarm_depth_weights(_alarm_for_etch, modules)
                if dw:
                    etch_alarm_weights = dw

            # Per-pass etch threshold multipliers (depth-selective etching)
            etch_thresh_mults = None
            if hasattr(cfg, 'pass_etch_multiplier') and cfg.pass_etch_multiplier:
                modules = list(_walk_ternary_modules(model))
                etch_thresh_mults = _compute_etch_threshold_multipliers(cfg, modules)

            sig_stats = update_signal_planes(
                etch_states, model,
                heat_thresholds=cfg.etch_heat_thresholds,
                alarm_weights=etch_alarm_weights,
                etch_threshold_multipliers=etch_thresh_mults,
            )
            # Brief log for active modules
            if sig_stats and step % cfg.log_interval == 0:
                active = sum(1 for s in sig_stats.values()
                             if sum(s.get("votes_per_plane", [])) > 0)
                print(f"  🔥 signal update: {active}/{len(sig_stats)} modules active",
                      file=sys.stderr, flush=True)

        # ── Etch check (topology shaping) ─────────────────────
        # Consensus mechanism + per-event ceiling govern flip rate.
        # Early: many wrong signs → aggressive etching.
        # Late: signs aligned → few/no flips. Natural convergence.
        if (etch_states is not None
                and step >= cfg.etch_warmup
                and step % cfg.etch_interval == 0):
            max_flips_this_event = getattr(cfg, 'etch_max_flips_per_event', None)
            etch_result = etch_check(
                etch_states, model,
                consensus_required=cfg.etch_consensus,
                max_flips=max_flips_this_event,
            )
            n_flipped = etch_result["total_flipped"]
            total_etched += n_flipped

            if n_flipped > 0:
                # Surgical Adam decay for etched rows
                affected = etch_result.get("affected_rows", {})
                if cfg.etch_adam_decay < 1.0 and affected:
                    surgical_adam_decay_for_etch(
                        optimizer, model, affected,
                        decay=cfg.etch_adam_decay,
                    )
                # Re-freeze ternary weights after etching
                freeze_ternary_weights(model)
                restore_ternary(model)

                # Reset signal accumulators after successful etch
                # (heat planes should restart from current gradient signal
                # rather than carry stale pre-flip consensus votes)
                if getattr(cfg, 'etch_reset_after_flip', False):
                    for es in etch_states.values():
                        if hasattr(es, 'reset_heat'):
                            es.reset_heat()

            # Log etch event
            per_mod_summary = {
                p: d["n_flipped"]
                for p, d in etch_result.get("per_module", {}).items()
                if d["n_flipped"] > 0
            }

            # Aggregate per-mirror/plate etch counts
            other_flips = sum(per_mod_summary.values())

            # Etch tempo: candidates / total ternary positions
            # High = crystal still forming. Near-zero = crystal stabilized.
            etch_tempo = (etch_result.get("total_candidates", 0) / max(total_ternary, 1))

            print(
                f"  ⚡ etch step {step}: {n_flipped:,} flips"
                f" ({total_etched:,} total)"
                f"  modules: {len(per_mod_summary)}"
                f"  tempo: {etch_tempo:.6f}",
                file=sys.stderr, flush=True,
            )
            if per_mod_summary:
                top3 = sorted(per_mod_summary.items(), key=lambda x: -x[1])[:3]
                for p, nf in top3:
                    print(f"       {p}: {nf:,}", file=sys.stderr, flush=True)

            # Per-pass flip aggregation for depth-selective logging
            per_pass_flips = [0] * cfg.n_passes
            for p, d in etch_result.get("per_module", {}).items():
                nf = d.get("n_flipped", 0)
                if nf > 0:
                    for prefix, pass_indices in MODULE_PASS_MAP.items():
                        if p == prefix or p.startswith(prefix + "."):
                            for pi in pass_indices:
                                if pi < len(per_pass_flips):
                                    per_pass_flips[pi] += nf
                            break

            _append_jsonl(checkpoint_dir / "etch_log.jsonl", {
                "step": step,
                "timestamp": time.time(),
                "per_pass_flips": per_pass_flips,
                "total_flipped": n_flipped,
                "total_candidates": etch_result.get("total_candidates", 0),
                "total_etched": total_etched,
                "etch_tempo": etch_tempo,
                "flips_by_type": etch_result.get("flips_by_type", {}),
                "per_module": {
                    p: d for p, d in etch_result.get("per_module", {}).items()
                },
            })

        # ── Evolution (legacy, disabled by default) ───────────
        if cfg.use_evolution and step % cfg.gen_interval == 0:
            # Pass alarm factors from last eval for targeted mutation
            _alarm = (last_eval.get("alarm_factors")
                      if last_eval else None)
            gen_result = run_tournament(
                model, cfg, step, total_ternary, eval_loader,
                cfg.base_pct, mutation_rng,
                row_importance, col_importance, grad_direction,
                structured_eval_loader=structured_eval_loader,
                alarm_factors=_alarm,
            )
            total_generations += 1
            if gen_result["accepted"]:
                total_accepted += 1
                # Surgical Adam decay — only reset m/v for gamma entries
                # whose rows were actually mutated. Untouched rows keep
                # full momentum, preventing the CE spike.
                if cfg.mutation_adam_decay < 1.0:
                    n_decayed = decay_adam_state(
                        optimizer, model, decay=cfg.mutation_adam_decay,
                        mutation_map=gen_result.get("mutation_map"),
                    )

            accepted_str = gen_result["accepted"] or "rejected"
            delta = gen_result["accepted_loss"] - gen_result["champion_loss"]
            # Log alarm health delta for noise floor diagnostics
            ah_before = gen_result.get("alarm_health_before")
            ah_after = gen_result.get("alarm_health_after")
            alarm_delta = (ah_after - ah_before) if (ah_before is not None and ah_after is not None) else 0.0
            n_rows = gen_result.get("n_rows_mutated", 0)
            actual_flips = gen_result.get("actual_flips", 0)
            cs = gen_result.get("consensus_stats") or {}
            sampled = cs.get("positions_sampled", 0)
            decay_str = (f"  adam_decay={cfg.mutation_adam_decay} ({n_decayed} rows)"
                         if gen_result["accepted"] and cfg.mutation_adam_decay < 1.0 else "")
            # Show per-type losses when using mixed data
            type_str = ""
            if gen_result.get("struct_loss") is not None:
                type_str = (f"  prose={gen_result['prose_loss']:.4f}"
                            f"  struct={gen_result['struct_loss']:.4f}")
            # Show alarm health delta
            alarm_str = ""
            ah_before = gen_result.get("alarm_health_before")
            ah_after = gen_result.get("alarm_health_after")
            if ah_before is not None and ah_after is not None:
                ah_delta = ah_after - ah_before
                alarm_str = f"  alarm={ah_before:.3f}→{ah_after:.3f}"
                if ah_delta > 0.001:
                    alarm_str += " ↑"
            print(
                f"  🧬 gen {total_generations}: {accepted_str}"
                f"  Δ={delta:+.4f}"
                f"  flips={actual_flips:,}/{sampled:,}"
                f"  rows={n_rows:,}"
                f"  {total_accepted}/{total_generations}"
                f"{type_str}{alarm_str}"
                f"{decay_str}",
                file=sys.stderr, flush=True,
            )

            # Log evolution event
            _append_jsonl(checkpoint_dir / "evolution_log.jsonl", {
                "step": step,
                "timestamp": time.time(),
                "generation": total_generations,
                "accepted": gen_result["accepted"],
                "champion_loss": gen_result["champion_loss"],
                "accepted_loss": gen_result["accepted_loss"],
                "delta": delta,
                "budget": gen_result["budget"],
                "actual_flips": actual_flips,
                "n_rows_mutated": n_rows,
                "prose_loss": gen_result.get("prose_loss"),
                "struct_loss": gen_result.get("struct_loss"),
                "consensus_stats": gen_result.get("consensus_stats"),
                "alarm_health_before": gen_result.get("alarm_health_before"),
                "alarm_health_after": gen_result.get("alarm_health_after"),
            })

        # ── Evaluation ────────────────────────────────────────
        if step % cfg.eval_interval == 0:
            last_eval = evaluate(model, cfg)
            print(
                f"📊 Eval @ {step}: loss={last_eval['loss']:.3f}"
                f"  ppl={last_eval['ppl']:.0f}  r={last_eval['r']:.3f}",
                file=sys.stderr, flush=True,
            )
            # Append full instrumentation to JSONL log (v12: includes retrieval metrics)
            metrics_record = {
                "step": step,
                "timestamp": time.time(),
                "total_generations": total_generations,
                "total_accepted": total_accepted,
                **last_eval,
            }
            # Add retrieval metrics from forward_instrumented (v12)
            if last_eval.get("retrieval_gate_means") is not None:
                metrics_record["retrieval_gate_means"] = last_eval["retrieval_gate_means"]
            if last_eval.get("retrieval_register_norms") is not None:
                metrics_record["retrieval_register_norms"] = last_eval["retrieval_register_norms"]
            if last_eval.get("retrieval_write_gates") is not None:
                metrics_record["retrieval_write_gates"] = last_eval["retrieval_write_gates"]
            _append_jsonl(checkpoint_dir / "metrics_log.jsonl", metrics_record)

        # ── Checkpoint ────────────────────────────────────────
        if step % cfg.checkpoint_interval == 0:
            save_checkpoint(model, optimizer, step, cfg, checkpoint_dir,
                            train_losses, total_generations, total_accepted,
                            last_eval, row_importance, col_importance,
                            grad_direction, mutation_rng,
                            etch_states=etch_states,
                            total_etched=total_etched,
                            train_loader=train_loader)

    # ── Final ─────────────────────────────────────────────────
    elapsed = time.time() - t_start
    final_eval = evaluate(model, cfg)
    print(
        f"\n{'='*72}\n"
        f"Training complete: {cfg.total_steps - start_step} steps in {elapsed:.0f}s\n"
        f"Final: loss={final_eval['loss']:.3f}  ppl={final_eval['ppl']:.0f}"
        f"  r={final_eval['r']:.3f}",
        file=sys.stderr,
    )

    save_checkpoint(model, optimizer, cfg.total_steps, cfg, checkpoint_dir,
                    train_losses, total_generations, total_accepted,
                    final_eval, row_importance, col_importance,
                    grad_direction, mutation_rng,
                    etch_states=etch_states,
                    total_etched=total_etched,
                    train_loader=train_loader)


# ══════════════════════════════════════════════════════════════════════════════
# § 9  CLI
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="v12 — KIBC + M Retrieval VSM on Dolma prose (Qwen3 tokenizer)")
    parser.add_argument("--total-steps", type=int, default=None)
    parser.add_argument("--checkpoint-dir", type=str, default=None)
    parser.add_argument("--resume", nargs="?", const=True, default=False,
                        help="Resume training. No arg = latest checkpoint. "
                             "Arg = step dir name (e.g. step_003000) or full path.")
    parser.add_argument("--d-model", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--grad-accum", type=int, default=None)
    parser.add_argument("--seq-len", type=int, default=None)
    parser.add_argument("--gen-interval", type=int, default=None)
    parser.add_argument("--base-pct", type=float, default=None)
    parser.add_argument("--lr", type=float, default=None)
    parser.add_argument("--eval-interval", type=int, default=None)
    parser.add_argument("--log-interval", type=int, default=None)
    parser.add_argument("--checkpoint-interval", type=int, default=None)
    parser.add_argument("--mix-ratio", type=float, default=None,
                        help="Fraction of structured data (0.0=prose only, 0.1=10%% structured)")
    parser.add_argument("--structured-shard", type=str, default=None,
                        help="Path to structured data shard (.npy)")
    parser.add_argument("--holo-lambda", type=float, default=None,
                        help="Holographic loss weight (0.0=disabled, 0.1=recommended)")
    parser.add_argument("--holo-warmup-steps", type=int, default=None,
                        help="Steps before holographic loss activates")
    parser.add_argument("--holo-ramp-steps", type=int, default=None,
                        help="Steps to ramp holographic loss from 0 to holo-lambda")
    parser.add_argument("--no-desc-stride-reverse", action="store_true", default=False,
                        help="Disable coarse→fine descending stride (force fine→coarse like ascending)")
    parser.add_argument("--no-fractal-stride-bands", action="store_true", default=False,
                        help="Disable fractal stride bands (all passes use all 9 strides)")
    # Etching overrides
    parser.add_argument("--etch-warmup", type=int, default=None,
                        help="Steps before etching begins (default: 500)")
    parser.add_argument("--etch-interval", type=int, default=None,
                        help="Steps between etch checks (default: 200)")
    parser.add_argument("--etch-signal-interval", type=int, default=None,
                        help="Steps between signal plane updates (default: 50)")
    parser.add_argument("--etch-consensus", type=int, default=None,
                        help="Signal planes required for consensus (2 or 3, default: 3)")
    parser.add_argument("--etch-max-pct", type=float, default=None,
                        help="Max fraction of weights to flip per cycle (default: 0.001 = 0.1%%)")
    parser.add_argument("--no-etching", action="store_true", default=False,
                        help="Disable etching, use legacy evolution")
    parser.add_argument("--use-evolution", action="store_true", default=False,
                        help="Enable legacy consensus evolution")

    args = parser.parse_args()
    cfg = V12Config()

    if args.total_steps is not None: cfg.total_steps = args.total_steps
    if args.checkpoint_dir is not None: cfg.checkpoint_dir = args.checkpoint_dir
    if args.d_model is not None:
        cfg.d_model = args.d_model
        cfg.d_ff = args.d_model * 3
    if args.batch_size is not None: cfg.batch_size = args.batch_size
    if args.grad_accum is not None: cfg.grad_accum = args.grad_accum
    if args.seq_len is not None:
        cfg.seq_len = args.seq_len
        cfg.max_seq_len = args.seq_len
    if args.gen_interval is not None: cfg.gen_interval = args.gen_interval
    if args.base_pct is not None: cfg.base_pct = args.base_pct
    if args.lr is not None: cfg.lr = args.lr
    if args.eval_interval is not None: cfg.eval_interval = args.eval_interval
    if args.log_interval is not None: cfg.log_interval = args.log_interval
    if args.checkpoint_interval is not None: cfg.checkpoint_interval = args.checkpoint_interval
    if args.mix_ratio is not None: cfg.mix_ratio = args.mix_ratio
    if args.structured_shard is not None: cfg.structured_shard = args.structured_shard
    if args.holo_lambda is not None: cfg.holo_lambda = args.holo_lambda
    if args.holo_warmup_steps is not None: cfg.holo_warmup_steps = args.holo_warmup_steps
    if args.holo_ramp_steps is not None: cfg.holo_ramp_steps = args.holo_ramp_steps
    if args.no_desc_stride_reverse: cfg.desc_stride_reverse = False
    if args.no_fractal_stride_bands: cfg.fractal_stride_bands = False
    if args.etch_warmup is not None: cfg.etch_warmup = args.etch_warmup
    if args.etch_interval is not None: cfg.etch_interval = args.etch_interval
    if args.etch_signal_interval is not None: cfg.etch_signal_interval = args.etch_signal_interval
    if args.etch_consensus is not None: cfg.etch_consensus = args.etch_consensus
    if args.etch_max_pct is not None: cfg.etch_max_pct = args.etch_max_pct
    if args.no_etching: cfg.use_etching = False
    if args.use_evolution: cfg.use_evolution = True
    cfg.__post_init__()

    train(cfg, args)


if __name__ == "__main__":
    main()
