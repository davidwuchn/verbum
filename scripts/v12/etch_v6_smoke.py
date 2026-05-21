"""Smoke test: Etcher module with v6 student + Qwen3-14B teacher.

1-round etch with 10 probes to verify the pipeline works end-to-end.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/etch_v6_smoke.py

License: MIT
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import mlx.core as mx
from verbum.v6.model import VSMLMV6
from verbum.etcher import Etcher, TeacherFeatures, EtchConfig

def log(msg):
    print(msg, flush=True)

# ── v6 pass function ──
def v6_pass_fn(model: VSMLMV6, x: mx.array, pass_idx: int) -> mx.array:
    """Run x through one v6 pass. Model-specific callback for the etcher."""
    is_desc = pass_idx >= 3  # v6: passes 0,1,2 ascending, 3,4 descending

    # Build minimal readable banks
    bank_0 = model._init_bank0()
    n_readable = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}[pass_idx]
    readable = [bank_0]
    for _ in range(n_readable - 1):
        readable.append(model._fresh_bank())
    target_bank = model._fresh_bank()

    x_out, _, _, _ = model._run_level_pass(
        x, pass_idx, is_desc, readable, target_bank)
    return x_out


def main():
    t0 = time.time()
    log("=" * 60)
    log("  Etcher Smoke Test: v6 + Qwen3-14B")
    log("=" * 60)

    # ── Load teacher features ──
    teacher_dir = Path("checkpoints/teacher-features-14b")
    if not teacher_dir.exists():
        log(f"ERROR: {teacher_dir} not found. Run extract_teacher.py first.")
        sys.exit(1)

    teacher = TeacherFeatures(teacher_dir)
    log(f"Teacher: {teacher.d_teacher}D, {teacher.n_probes} probes, "
        f"depths {teacher.depth_indices}")

    # ── Load v6 model ──
    log("Loading v6 model...")
    ckpt = Path("checkpoints/vsm-lm-v6/step_032500")
    with open(ckpt / "meta.json") as f:
        meta = json.load(f)
    cfg = meta["config"]
    model = VSMLMV6(
        vocab_size=cfg["vocab_size"], d_model=cfg["d_model"],
        d_register=cfg["d_register"], max_len=cfg["seq_len"],
        n_heads=cfg["n_heads"], d_ff=cfg["d_ff"],
        d_ff_consolidate=cfg["d_ff_consolidate"], window=cfg["window"],
        strides=tuple(cfg["strides"]),
    )
    weights = mx.load(str(ckpt / "weights.safetensors"))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())

    # ── Depth mapping ──
    # Teacher depths: [8, 16, 24, 32, 40] (indices 0-4)
    # v6 passes: [L0↑, L1↑, L2_apex, L1↓, L0↓] (indices 0-4)
    depth_mapping = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}

    # ── Configure smoke test ──
    config = EtchConfig(
        d_teacher=teacher.d_teacher,
        d_student=cfg["d_model"],
        depth_mapping=depth_mapping,
        n_rounds=1,
        probes_per_round=10,
        beam_steps_per_round=20,
        confidence_start=0.3,
        confidence_end=0.5,
        beam_lr=1e-4,
    )

    # ── Run etcher ──
    log("\nRunning etcher...")
    etcher = Etcher(model, teacher, config, pass_fn=v6_pass_fn)
    results = etcher.run(log_fn=log)

    # ── Summary ──
    log(f"\n{'='*60}")
    log(f"  Smoke test complete in {time.time()-t0:.1f}s")
    for r in results:
        log(f"  R{r['round']}: loss={r['distill_loss']:.6f} "
            f"flips={r['flips']:,}/{r['candidates']:,} "
            f"beam={r['beam_loss']:.6f}")
    log(f"{'='*60}")

    teacher.close()


if __name__ == "__main__":
    main()
