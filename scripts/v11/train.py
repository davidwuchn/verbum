"""
v10 — Training Script

V6 compressor (5-pass bidirectional VSM, 9 strides, Qwen3 tokenizer)
trained on Dolma prose for next-token prediction.

  • Causal LM cross-entropy loss
  • Relational loss r = (CE - E) / (log(V) - E) for phase awareness
  • Shared-weight gradient normalization (÷5 for 5-pass components)
  • Ternary topology evolved via tournament selection (mixed-data-aware)
  • Adam on continuous parameters (gamma, norms, embeddings, pos_embed)
  • Cosine LR with linear warmup

Usage:
    uv run python scripts/v10/train.py
    uv run python scripts/v10/train.py --total-steps 5000
    uv run python scripts/v10/train.py --seq-len 512 --batch-size 4
    uv run python scripts/v10/train.py --resume

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

from config import V11Config
from data import ShardedDataLoader, MixedDataLoader
from model import V11Model, create_model, count_parameters
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
    model: V11Model,
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
ASC_SHARED = ("prep", "stride_stack", "consolidate", "mod_projs", "s4")
# Descending components: shared across L1↓, L0↓ (2 passes)
# Kernel dispatch/integrate replace prep_desc/consolidate_desc
DESC_SHARED = ("combinator_dispatch", "stride_stack_desc", "combinator_integrate", "mod_projs_desc", "s4_desc")

N_ASC_PASSES = 3
N_DESC_PASSES = 2


def normalize_shared_grads(grads: dict) -> dict:
    """Divide gradients of shared components by their pass count.

    Ascending components (prep, stride_stack, consolidate, mod_projs, s4)
    are traversed 3× per forward (L0↑, L1↑, L2_apex).
    Descending components (*_desc) are traversed 2× (L1↓, L0↓).
    Normalizing stabilizes Adam's running statistics.
    """
    asc_scale = 1.0 / N_ASC_PASSES
    desc_scale = 1.0 / N_DESC_PASSES

    def _walk(tree, keys):
        if isinstance(tree, dict):
            out = {}
            for k, v in tree.items():
                new_keys = keys + [k]
                if len(new_keys) >= 1 and new_keys[0] in ASC_SHARED:
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


def holo_schedule(step: int, cfg: V11Config) -> float:
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

def evaluate(model: V11Model, cfg: V11Config) -> dict:
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
    pass_names = ("L0↑", "L1↑", "L2", "L1↓", "L0↓")
    desc_max_cycles = compressor_metrics.get("desc_max_cycles", 1)

    print("  ┌─ S3 gates ──────────────────────────────────────┐", file=sys.stderr)
    for pi, pname in enumerate(pass_names):
        gates = compressor_metrics["s3_gates"][pi]
        if pi >= 3 and desc_max_cycles > 1:
            # Descending pass: show per-cycle gates
            for cy in range(desc_max_cycles):
                base = cy * 3
                cyname = f"{pname}c{cy}"
                print(f"  │ {cyname:6s}: disp={gates[base]:.3f}  "
                      f"conv={gates[base+1]:.3f}  intg={gates[base+2]:.3f}",
                      file=sys.stderr)
        else:
            print(f"  │ {pname:4s}: prep={gates[0]:.3f}  conv={gates[1]:.3f}  "
                  f"cons={gates[2]:.3f}", file=sys.stderr)
    print("  ├─ S5 reweight ───────────────────────────────────┤", file=sys.stderr)
    mg = compressor_metrics["s5_reweight"]
    print(f"  │ {' '.join(f'{pn}={g:.3f}' for pn, g in zip(pass_names, mg))}",
          file=sys.stderr)
    print("  ├─ S2 coordination ───────────────────────────────┤", file=sys.stderr)
    s2_conflict = compressor_metrics.get("s2_conflict", [])
    s2_scales = compressor_metrics.get("s2_scales", [])
    s2_names = ("L0↑→L1↑", "L1↑→L2", "L2→L1↓", "L1↓→L0↓")
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

    # Combinator emphasis (S4→dispatch modulation)
    comb_emph = compressor_metrics.get("combinator_emphasis")
    if comb_emph:
        from kernel import COMBINATOR_NAMES
        indexed = sorted(enumerate(comb_emph), key=lambda x: x[1], reverse=True)
        parts = [f"{COMBINATOR_NAMES[i]}={v:.2f}" for i, v in indexed]
        print(f"  🎯 Combinator emphasis: {' '.join(parts)}",
              file=sys.stderr)

    # Compute gate stats (kernel pathway)
    if "compute_gate_mean" in compressor_metrics:
        cg_mean = compressor_metrics["compute_gate_mean"]
        cg_max = compressor_metrics["compute_gate_max"]
        cg_active = compressor_metrics["compute_gate_active"]
        print(f"  🔧 Compute gate: mean={cg_mean:.4f}  max={cg_max:.4f}  "
              f"active(>0.5)={cg_active:.1%}", file=sys.stderr)

    # Multi-cycle stats
    if desc_max_cycles > 1:
        cig = compressor_metrics.get("cycle_inject_gate", 0.0)
        eff_cycles = compressor_metrics.get("effective_cycles", [])
        cont_gates = compressor_metrics.get("cycle_continue_gates", [])
        desc_pass_names = ("L1↓", "L0↓")
        parts = [f"max={desc_max_cycles}", f"inject={cig:.4f}"]
        for di, dpn in enumerate(desc_pass_names):
            if di < len(eff_cycles):
                parts.append(f"{dpn}={eff_cycles[di]:.2f}eff")
            if di < len(cont_gates) and cont_gates[di]:
                cg_str = ",".join(f"{g:.2f}" for g in cont_gates[di])
                parts.append(f"cont=[{cg_str}]")
        print(f"  🔄 Cycles: {' '.join(parts)}", file=sys.stderr)

    # Algedonic alert (Beer's fire alarm)
    alarm_factors = compressor_metrics.get("alarm_factors")
    eff_s5 = compressor_metrics.get("effective_s5_gates")
    if alarm_factors:
        pass_names_alarm = ("L0↑", "L1↑", "L2", "L1↓", "L0↓")
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
        pass_names_h = ("L0↑", "L1↑", "L2", "L1↓", "L0↓")
        parts = [f"{pn}={h:.3f}" for pn, h in zip(pass_names_h, holo)]
        print(f"  🔮 Holographic: {' '.join(parts)}", file=sys.stderr)

    # Log alarm raw metrics for offline threshold analysis
    alarm_metrics_raw = compressor_metrics.get("alarm_metrics")
    if alarm_metrics_raw:
        # Named sections for the 48 metrics
        alarm_named = {}
        idx = 0
        for section, count in [
            ("s3_gate_means", 5), ("s3_gate_mins", 5),
            ("s2_conflicts", 4), ("dispatch_weights", 4),
            ("dispatch_entropy", 1), ("compute_gate", 2),
            ("cycle_continue", 4), ("effective_cycles", 2),
            ("raw_delta_norms", 5), ("gated_delta_norms", 5),
            ("suppression_ratios", 5), ("register_norms", 6),
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
    "consolidate":      [0, 1, 2],
    "s4":               [0, 1, 2],
    "mod_projs":        [0, 1, 2],
    # Descending shared (2 passes)
    "combinator_dispatch":  [3, 4],
    "stride_stack_desc":    [3, 4],
    "combinator_integrate": [3, 4],
    "s4_desc":              [3, 4],
    "mod_projs_desc":       [3, 4],
    # Per-pass S3
    "s3_passes.0":      [0],
    "s3_passes.1":      [1],
    "s3_passes.2":      [2],
    "s3_passes.3":      [3],
    "s3_passes.4":      [4],
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

    # Acceptance criteria (OR gate):
    #   1. Loss improved (original criterion)
    #   2. Alarm health improved (structural improvement)
    # Safety bound: alarm-only acceptance requires loss didn't degrade
    # by more than 0.005 (prevents accepting structurally "better"
    # mutations that catastrophically hurt prediction).
    loss_improved = mutant_loss < champion_loss
    alarm_improved = (champion_health is not None
                      and mutant_health is not None
                      and mutant_health > champion_health
                      and (mutant_loss - champion_loss) < 0.005)

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

    state = {
        "step": step,
        "total_generations": total_generations,
        "total_accepted": total_accepted,
        "train_losses_last50": train_losses[-50:],
        "eval_metrics": eval_metrics or {},
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

def train(cfg: V11Config, args: argparse.Namespace) -> None:
    checkpoint_dir = Path(cfg.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # ── Banner ────────────────────────────────────────────────
    print("=" * 72, file=sys.stderr)
    print("  v11 — KIBC Combinator VSM (5-pass, 9 strides) on Dolma Prose", file=sys.stderr)
    print("  Qwen3 BBPE tokenizer, next-token prediction", file=sys.stderr)
    print("=" * 72, file=sys.stderr)

    # ── Model ─────────────────────────────────────────────────
    model = create_model(cfg)
    freeze_ternary_weights(model)

    param_counts = count_parameters(model)
    total_ternary = count_ternary_weights(model)

    print(f"\n  d_model={cfg.d_model}  n_heads={cfg.n_heads}  "
          f"strides={cfg.strides}", file=sys.stderr)
    print(f"  d_ff={cfg.d_ff}  d_ff_consolidate={cfg.d_ff_consolidate}  "
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

    # ── EMA importance maps ───────────────────────────────────
    row_importance: dict[str, np.ndarray] = {}
    col_importance: dict[str, np.ndarray] = {}
    grad_direction: dict[str, np.ndarray] = {}
    imp_alpha = 0.1
    mutation_rng = np.random.RandomState(42)

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
            last_eval = state.get("eval_metrics")
            loss_window.extend(train_losses[-50:])
            if dl_state:
                train_loader.load_state(dl_state)
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
            print(
                f"step {step:>6d} | r={step_loss:.4f} (avg50: {avg50:.4f})"
                f" | {loss_str} | lr {lr:.2e}"
                f" | {tps:.0f} tok/s"
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
            _append_jsonl(checkpoint_dir / "train_log.jsonl", train_record)

        # ── Evolution ─────────────────────────────────────────
        if step % cfg.gen_interval == 0:
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
            # Append full instrumentation to JSONL log
            _append_jsonl(checkpoint_dir / "metrics_log.jsonl", {
                "step": step,
                "timestamp": time.time(),
                "total_generations": total_generations,
                "total_accepted": total_accepted,
                **last_eval,
            })

        # ── Checkpoint ────────────────────────────────────────
        if step % cfg.checkpoint_interval == 0:
            save_checkpoint(model, optimizer, step, cfg, checkpoint_dir,
                            train_losses, total_generations, total_accepted,
                            last_eval, row_importance, col_importance,
                            grad_direction, mutation_rng, train_loader)

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
                    grad_direction, mutation_rng, train_loader)


# ══════════════════════════════════════════════════════════════════════════════
# § 9  CLI
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="v10 — V6 compressor on Dolma prose (Qwen3 tokenizer)")
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

    args = parser.parse_args()
    cfg = V11Config()

    if args.total_steps is not None: cfg.total_steps = args.total_steps
    if args.checkpoint_dir is not None: cfg.checkpoint_dir = args.checkpoint_dir
    if args.d_model is not None:
        cfg.d_model = args.d_model
        cfg.d_ff = args.d_model * 3
        cfg.d_ff_consolidate = args.d_model * 4
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
    cfg.__post_init__()

    train(cfg, args)


if __name__ == "__main__":
    main()
