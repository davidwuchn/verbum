"""Loom Implant Test — Which plate subset carries the most teacher signal?

Phase 4 of the etch pipeline. Tests 5 conditions:

  A: FULL_ETCH   — all ternary plates etched + melted
  B: FFN_ONLY    — only prep/consolidate FFN plates etched
  C: ATTN_ONLY   — only stride_stack Q/K/V/O plates etched
  D: S3_ONLY     — only S3 proj_align/proj_delta plates etched
  E: BASELINE    — original v6 checkpoint (no etch)

For each condition:
  1. Start from v6 step_032500 checkpoint
  2. Apply selective etch (only the target plate subset)
  3. Run 500-step melt with crystal loss (shorter than full melt)
  4. Measure: loss, crystal agreement, gamma stats

This answers the key question: which plate subset (FFN vs attention
vs S3 control) carries the most information from the teacher's crystal
structure?

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/loom_implant_test.py

License: MIT
"""

from __future__ import annotations

import json
import sys
import time
import shutil
from pathlib import Path

import numpy as np

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Config
# ══════════════════════════════════════════════════════════════════════

ORIGINAL_CHECKPOINT = Path("checkpoints/vsm-lm-v6/step_032500")
EXTRACTION_DIR = Path("results/v6-etch")
RESULTS_DIR = Path("results/v6-loom-implant")

MELT_STEPS = 500      # shorter per condition since we test 5
BATCH_SIZE = 4
SEQ_LEN = 512
LR = 1e-4
CRYSTAL_LAMBDA = 0.5
EVAL_BATCHES = 10

# Plate subsets by category
PLATE_CATEGORIES = {
    "FULL": None,  # all plates
    "FFN_ONLY": ["prep", "consolidate"],
    "ATTN_ONLY": ["stride_stack"],
    "S3_ONLY": ["s3_passes"],
}


# ══════════════════════════════════════════════════════════════════════
# Selective etch
# ══════════════════════════════════════════════════════════════════════

def selective_etch(
    model,
    signs_data: dict,
    plate_meta: dict,
    categories: list[str] | None,
) -> dict:
    """Apply teacher signs to a subset of v6 plates.

    Args:
        model: v6 model with loaded weights
        signs_data: npz dict of teacher sign patterns
        plate_meta: extraction metadata per plate
        categories: list of plate category prefixes to etch, or None for all

    Returns: stats dict with etch counts
    """
    from etch_v6_360 import (
        build_plate_mapping, unpack_ternary, pack_ternary, etch_plate,
    )

    plate_mapping = build_plate_mapping()
    total_flips = 0
    total_etchable = 0
    plates_etched = 0

    for ext_key, sf_key in plate_mapping.items():
        # Category filter
        if categories is not None:
            if not any(ext_key.startswith(cat) for cat in categories):
                continue

        npz_key = ext_key.replace(".", "_")
        if npz_key not in signs_data:
            continue

        # Check vote strength
        if ext_key in plate_meta:
            vs = plate_meta[ext_key]["vote_strength"]
            if vs < 0.4:
                continue

        teacher_signs = signs_data[npz_key]

        # Navigate model to find the ternary weight
        # Parse sf_key to get model attribute path
        parts = sf_key.replace(".ternary_weight", "").split(".")
        obj = model
        try:
            for part in parts:
                if part.isdigit():
                    obj = obj[int(part)] if isinstance(obj, (list, nn.Module)) else getattr(obj, part)
                else:
                    obj = getattr(obj, part)
        except (AttributeError, IndexError, TypeError):
            continue

        if not hasattr(obj, "ternary_weight"):
            continue

        # Get current ternary weight
        current = np.array(obj.ternary_weight)
        if current.dtype == np.uint8:
            K = current.shape[1] * 4
            current_unpacked = unpack_ternary(current, K)
        else:
            current_unpacked = current.astype(np.int8)

        # Etch
        new_signs, stats = etch_plate(current_unpacked, teacher_signs, preserve_zeros=True)

        # Write back
        if current.dtype == np.uint8:
            obj.ternary_weight = mx.array(pack_ternary(new_signs))
        else:
            obj.ternary_weight = mx.array(new_signs)
        mx.eval(obj.ternary_weight)

        total_flips += stats["n_flipped"]
        total_etchable += stats["total_etchable"]
        if stats["n_flipped"] > 0:
            plates_etched += 1

    return {
        "total_flips": total_flips,
        "total_etchable": total_etchable,
        "plates_etched": plates_etched,
        "flip_fraction": float(total_flips / total_etchable) if total_etchable > 0 else 0,
    }


# ══════════════════════════════════════════════════════════════════════
# Eval + melt (reuse from melt_v6)
# ══════════════════════════════════════════════════════════════════════

def quick_eval(model, tokenizer, texts, n_batches=10):
    """Quick evaluation."""
    from melt_v6 import get_batches_tokenized, ce_loss

    rng = np.random.RandomState(999)
    total = 0
    for _ in range(n_batches):
        ids, tgt = get_batches_tokenized(tokenizer, texts, BATCH_SIZE, SEQ_LEN, rng)
        loss = ce_loss(model, ids, tgt)
        mx.eval(loss)
        total += loss.item()
    return total / n_batches


def quick_melt(model, tokenizer, texts, steps, crystal_lambda):
    """Short melt with crystal loss, return final loss."""
    from melt_v6 import (
        get_batches_tokenized, ce_loss, crystal_lattice_loss,
        freeze_ternary_plates,
    )

    freeze_ternary_plates(model)
    optimizer = optim.Adam(learning_rate=LR)

    def loss_fn(model, ids, tgt):
        ce = ce_loss(model, ids, tgt)
        cl = crystal_lattice_loss(model)
        return ce + crystal_lambda * cl

    lag = nn.value_and_grad(model, loss_fn)
    rng = np.random.RandomState(42)

    losses = []
    for step in range(steps):
        ids, tgt = get_batches_tokenized(tokenizer, texts, BATCH_SIZE, SEQ_LEN, rng)
        lv, gr = lag(model, ids, tgt)
        mx.eval(lv, gr)
        model.update(optimizer.apply_gradients(gr, model))
        mx.eval(model.parameters())
        del gr

        if (step + 1) % 100 == 0:
            losses.append(float(lv.item()))
            log(f"      step {step+1}: loss={lv.item():.4f}")
            mx.clear_cache()

    final_loss = quick_eval(model, tokenizer, texts, n_batches=EVAL_BATCHES)
    return final_loss, losses


def crystal_metrics(model):
    """Quick crystal measurement."""
    from melt_v6 import measure_crystal_agreement
    return measure_crystal_agreement(model, 0)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    log("=" * 60)
    log("  Loom Implant Test: Which plates carry the signal?")
    log(f"  Original: {ORIGINAL_CHECKPOINT}")
    log(f"  Melt steps per condition: {MELT_STEPS}")
    log("=" * 60)

    # ── Load extraction data ──
    log("\nLoading extraction data...")
    meta_path = EXTRACTION_DIR / "extraction_meta.json"
    if not meta_path.exists():
        log("ERROR: Run extract_teacher_v6.py first")
        sys.exit(1)

    with open(meta_path) as f:
        extraction_meta = json.load(f)
    signs_data = dict(np.load(EXTRACTION_DIR / "plate_signs.npz"))
    plate_meta = extraction_meta["plate_meta"]

    # ── Load tokenizer ──
    log("\nLoading tokenizer...")
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-410m")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # ── Load training data ──
    from melt_v6 import load_training_data, DATA_PATH
    texts = load_training_data(DATA_PATH)
    log(f"  {len(texts)} training examples")

    # ── Load base model ──
    from melt_v6 import load_v6_model

    results = {}

    # ── Condition E: BASELINE (no etch, just eval) ──
    log(f"\n{'═' * 60}")
    log("  CONDITION E: BASELINE (no etch)")
    log(f"{'═' * 60}")

    model, _ = load_v6_model(ORIGINAL_CHECKPOINT)
    baseline_loss = quick_eval(model, tokenizer, texts, EVAL_BATCHES)
    baseline_crystal = crystal_metrics(model)
    log(f"  Loss: {baseline_loss:.4f}")
    results["E_BASELINE"] = {
        "pre_etch_loss": baseline_loss,
        "post_melt_loss": baseline_loss,
        "etch_stats": {"total_flips": 0},
        "crystal": baseline_crystal,
    }
    del model
    mx.clear_cache()

    # ── Conditions A-D: Selective etch + melt ──
    for condition, categories in PLATE_CATEGORIES.items():
        log(f"\n{'═' * 60}")
        log(f"  CONDITION {condition}: {categories or 'ALL plates'}")
        log(f"{'═' * 60}")

        # Fresh model from original checkpoint
        model, _ = load_v6_model(ORIGINAL_CHECKPOINT)

        # Etch
        log(f"  Etching...")
        etch_stats = selective_etch(model, signs_data, plate_meta, categories)
        log(f"    Flips: {etch_stats['total_flips']:,} "
            f"({etch_stats['flip_fraction']:.1%})")

        # Pre-melt eval
        pre_loss = quick_eval(model, tokenizer, texts, EVAL_BATCHES)
        pre_crystal = crystal_metrics(model)
        log(f"  Pre-melt loss: {pre_loss:.4f}")

        # Melt
        log(f"  Melting ({MELT_STEPS} steps)...")
        post_loss, loss_curve = quick_melt(
            model, tokenizer, texts, MELT_STEPS, CRYSTAL_LAMBDA
        )
        post_crystal = crystal_metrics(model)
        log(f"  Post-melt loss: {post_loss:.4f}")
        log(f"  Δ from baseline: {post_loss - baseline_loss:+.4f}")

        results[condition] = {
            "pre_etch_loss": pre_loss,
            "post_melt_loss": post_loss,
            "delta_from_baseline": post_loss - baseline_loss,
            "etch_stats": etch_stats,
            "pre_crystal": pre_crystal,
            "post_crystal": post_crystal,
            "loss_curve": loss_curve,
        }

        del model
        mx.clear_cache()

    # ── Summary ──
    log(f"\n{'═' * 60}")
    log(f"  SUMMARY")
    log(f"{'═' * 60}")
    log(f"  {'Condition':<14s} {'Pre-etch':>10s} {'Post-melt':>10s} {'Δ baseline':>10s} {'Flips':>8s}")
    log(f"  {'-'*14} {'-'*10} {'-'*10} {'-'*10} {'-'*8}")
    for cond in ["E_BASELINE", "FULL", "FFN_ONLY", "ATTN_ONLY", "S3_ONLY"]:
        r = results[cond]
        log(f"  {cond:<14s} {r['pre_etch_loss']:10.4f} {r['post_melt_loss']:10.4f} "
            f"{r.get('delta_from_baseline', 0):+10.4f} "
            f"{r['etch_stats']['total_flips']:8,}")

    # ── Save ──
    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    log(f"\n  Elapsed: {time.time()-t0:.1f}s")
    log(f"  Results: {RESULTS_DIR}/results.json")


if __name__ == "__main__":
    main()
