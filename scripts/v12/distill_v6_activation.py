"""Activation-Space Distillation — Align v6 hidden states to teacher.

The weight-sign extraction approach failed: teacher weight signs across
layers are 50% correlated (random) regardless of projection method.
The crystal lives in ACTIVATION space, not weight space.

This script:
  1. Loads teacher hidden states from checkpoints/teacher-features-14b/
  2. Loads v6 student model
  3. For matching depth ranges (teacher depth → v6 pass):
     a. Run the same probe texts through the student
     b. Procrustes-align student hidden states → teacher hidden states
     c. Compute activation MSE between aligned representations
  4. Train student with distillation loss + CE loss
  5. The Procrustes rotation is recomputed periodically (not frozen)

The dimensional bridge:
  Teacher d_model = 5120, student d_model = 512.
  Procrustes finds the best rotation from student→teacher subspace.
  We use CCA: find the d_student-dimensional subspace of teacher space
  that maximally correlates with student space, then MSE in that subspace.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/distill_v6_activation.py

License: MIT
"""

from __future__ import annotations

import json
import sys
import time
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

V6_CHECKPOINT = Path("checkpoints/vsm-lm-v6/step_032500")
TEACHER_FEATURES = Path("checkpoints/teacher-features-14b")
RESULTS_DIR = Path("results/v6-activation-distill")
OUTPUT_DIR = Path("checkpoints/v6-distilled-activation")

# Teacher Qwen3-14B: 40 layers, depths at [8, 16, 24, 32, 40]
# v6: 5 passes [L0↑, L1↑, L2_apex, L1↓, L0↓]
# Mapping: teacher depth 8→L0↑, 16→L1↑, 24→L2_apex, 32→L1↓, 40→L0↓
DEPTH_TO_PASS = {8: 0, 16: 1, 24: 2, 32: 3, 40: 4}

DISTILL_STEPS = 500
BATCH_SIZE = 4
SEQ_LEN = 40           # match teacher extraction max_seq_len
LR = 1e-4
DISTILL_LAMBDA = 1.0   # weight on distillation loss vs CE
ALIGN_INTERVAL = 50    # recompute Procrustes every N steps
EVAL_INTERVAL = 50

D_STUDENT = 512
D_TEACHER = 5120


# ══════════════════════════════════════════════════════════════════════
# Procrustes alignment
# ══════════════════════════════════════════════════════════════════════

def procrustes_align(
    student_states: np.ndarray,  # (N, d_student)
    teacher_states: np.ndarray,  # (N, d_teacher)
) -> np.ndarray:
    """Find the best linear map from student space → teacher subspace.

    Uses CCA-style approach:
    1. PCA-reduce teacher to d_student dimensions
    2. Procrustes-align student to reduced teacher
    3. Return the combined projection matrix (d_student → d_student)

    The alignment captures the rotation that makes student hidden states
    look most like teacher hidden states in the shared subspace.

    Returns: (d_student, d_teacher) projection matrix
    """
    d_s = student_states.shape[1]
    d_t = teacher_states.shape[1]

    # Center both
    s_mean = student_states.mean(axis=0, keepdims=True)
    t_mean = teacher_states.mean(axis=0, keepdims=True)
    S = student_states - s_mean
    T = teacher_states - t_mean

    # PCA-reduce teacher to d_student dims
    # Use SVD of teacher to get top-d_student directions
    from sklearn.utils.extmath import randomized_svd
    U_t, Sigma_t, Vt_t = randomized_svd(T, n_components=d_s, n_iter=4, random_state=42)
    T_reduced = T @ Vt_t[:d_s, :].T  # (N, d_student) — teacher in reduced space

    # Procrustes: find rotation R such that S @ R ≈ T_reduced
    # SVD of S.T @ T_reduced = U @ Sigma @ Vt
    # Optimal R = U @ Vt
    M = S.T @ T_reduced  # (d_student, d_student)
    U_m, _, Vt_m = np.linalg.svd(M, full_matrices=False)
    R = U_m @ Vt_m  # (d_student, d_student) orthogonal rotation

    # Combined: student → rotate → project into teacher space
    # P = R @ Vt_t[:d_s, :] — but we return R for student-space alignment
    # and Vt_t for teacher-space projection separately
    return R, Vt_t[:d_s, :], s_mean, t_mean


def compute_distill_loss_aligned(
    student_states: mx.array,    # (B, L, d_student)
    teacher_reduced: mx.array,   # (B, L, d_student)  — already PCA-reduced
    R: mx.array,                 # (d_student, d_student) rotation
) -> mx.array:
    """MSE between rotated student and teacher in shared subspace."""
    B, L, D = student_states.shape
    # Rotate student
    rotated = student_states @ R  # (B, L, d_student)
    # MSE
    diff = rotated - teacher_reduced
    return mx.mean(diff * diff)


# ══════════════════════════════════════════════════════════════════════
# Model loading + feature extraction
# ══════════════════════════════════════════════════════════════════════

def load_v6_model(checkpoint_path: Path):
    """Load v6 model."""
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from verbum.v6.model import VSMLMV6

    with open(checkpoint_path / "meta.json") as f:
        meta = json.load(f)

    config = meta.get("config", {})
    model = VSMLMV6(
        vocab_size=config.get("vocab_size", 50277),
        d_model=config.get("d_model", 512),
        d_register=config.get("d_register", 128),
        max_len=config.get("seq_len", 4096),
        n_heads=config.get("n_heads", 8),
        d_ff=config.get("d_ff", 1536),
        d_ff_consolidate=config.get("d_ff_consolidate", 2048),
        window=config.get("window", 8),
        strides=tuple(config.get("strides", [1, 8, 16, 32, 64, 128, 256, 512, 1024])),
    )

    weights = mx.load(str(checkpoint_path / "weights.safetensors"))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())

    return model, meta


def load_teacher_features(features_dir: Path) -> dict:
    """Load teacher hidden states organized by depth."""
    with open(features_dir / "manifest.json") as f:
        manifest = json.load(f)

    features = {}
    for depth_idx in manifest["depth_indices"]:
        # Load output hidden states at this depth
        outputs_path = features_dir / f"layer_{depth_idx:03d}_outputs.npz"
        data = np.load(outputs_path)
        # Concatenate all probes' hidden states into one matrix
        all_states = []
        for key in sorted(data.keys()):
            all_states.append(data[key])
        features[depth_idx] = {
            "states": all_states,  # list of (seq_len_i, d_teacher) arrays
            "n_probes": len(all_states),
        }

    return features, manifest


def get_student_hidden_states(model, input_ids: mx.array) -> list[mx.array]:
    """Run input through v6 model and capture hidden states at each pass.

    Returns list of 5 tensors, one per pass: (B, L, d_model)
    """
    # We need to hook into the model's pass structure
    # The v6 model runs 5 passes through _run_level_pass
    # We'll capture x after each pass by temporarily instrumenting
    captured = []

    # Save original forward
    original_call = model.__call__

    def instrumented_call(input_ids, targets=None):
        B, L = input_ids.shape
        positions = mx.arange(L)
        x = model.embed_norm(model.token_embed(input_ids) + model.pos_embed(positions))

        bank_0 = model._init_bank0()
        bank_1_asc = model._fresh_bank()
        bank_2_asc = model._fresh_bank()
        bank_3 = model._fresh_bank()
        bank_2_desc = model._fresh_bank()
        bank_1_desc = model._fresh_bank()

        # L0 ascending
        x, bank_1_asc, _, _ = model._run_level_pass(x, 0, False, [bank_0], bank_1_asc)
        captured.append(x)

        # L1 ascending
        x, bank_2_asc, _, _ = model._run_level_pass(x, 1, False, [bank_0, bank_1_asc], bank_2_asc)
        captured.append(x)

        # L2 apex
        x, bank_3, _, _ = model._run_level_pass(x, 2, False, [bank_0, bank_1_asc, bank_2_asc], bank_3)
        captured.append(x)

        # L1 descending
        x, bank_2_desc, _, _ = model._run_level_pass(x, 3, True, [bank_0, bank_1_asc, bank_2_asc, bank_3], bank_2_desc)
        captured.append(x)

        # L0 descending
        x, bank_1_desc, _, _ = model._run_level_pass(x, 4, True, [bank_0, bank_1_asc, bank_2_asc, bank_3, bank_2_desc], bank_1_desc)
        captured.append(x)

        # Output
        x = model.output_norm(x)
        logits = x @ model.token_embed.weight.T

        return logits, None, None, None

    # Run instrumented forward
    instrumented_call(input_ids)

    return captured


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    log("=" * 60)
    log("  Activation-Space Distillation: Qwen3-14B → v6")
    log(f"  Student: {V6_CHECKPOINT}")
    log(f"  Teacher: {TEACHER_FEATURES}")
    log("=" * 60)

    # ── Load teacher features ──
    log("\nLoading teacher features...")
    if not TEACHER_FEATURES.exists():
        log(f"ERROR: Teacher features not found at {TEACHER_FEATURES}")
        log("  Run: uv run python scripts/v12/extract_teacher.py --model Qwen/Qwen3-14B ...")
        sys.exit(1)

    teacher_features, manifest = load_teacher_features(TEACHER_FEATURES)
    log(f"  {manifest['model']}: {manifest['n_probes']} probes, "
        f"depths {manifest['depth_indices']}")
    for depth, feat in teacher_features.items():
        n_tokens = sum(s.shape[0] for s in feat["states"])
        log(f"    Depth {depth}: {feat['n_probes']} probes, {n_tokens:,} tokens, "
            f"d={feat['states'][0].shape[1]}")

    # ── Load student model ──
    log(f"\nLoading student model from {V6_CHECKPOINT}...")
    model, meta = load_v6_model(V6_CHECKPOINT)

    # ── Load tokenizer for probes ──
    log("\nLoading tokenizer...")
    from transformers import AutoTokenizer
    teacher_tokenizer = AutoTokenizer.from_pretrained(manifest["model"], trust_remote_code=True)
    if teacher_tokenizer.pad_token is None:
        teacher_tokenizer.pad_token = teacher_tokenizer.eos_token

    student_tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-410m")
    if student_tokenizer.pad_token is None:
        student_tokenizer.pad_token = student_tokenizer.eos_token

    # ── Get probe texts and tokenize for student ──
    # Use the same probe texts that were used for teacher extraction
    log("\nPreparing probe alignments...")

    # We need to run the same semantic content through both models
    # Teacher features are already extracted. For student, we re-tokenize
    # the probe texts using the Pythia tokenizer.
    probe_texts = manifest.get("probe_texts", [])
    if len(probe_texts) < 10:
        log("  WARNING: Only have first 10 probe texts from manifest")

    # For alignment, we'll use the first N probes' mean hidden states
    # (averaged over tokens) to compute Procrustes rotation
    N_ALIGN = min(50, teacher_features[list(teacher_features.keys())[0]]["n_probes"])

    log(f"  Using {N_ALIGN} probes for alignment")

    # ── Compute initial Procrustes alignment at each depth ──
    log("\nComputing initial Procrustes alignment...")

    # Get teacher mean hidden states per probe at each depth
    alignments = {}
    for depth_idx, pass_idx in DEPTH_TO_PASS.items():
        teacher_means = []
        for i in range(N_ALIGN):
            states = teacher_features[depth_idx]["states"][i]  # (seq_len, d_teacher)
            teacher_means.append(states.mean(axis=0))  # (d_teacher,)
        teacher_means = np.stack(teacher_means)  # (N_ALIGN, d_teacher)

        # For now, just use the teacher PCA reduction as the target
        # We'll align student states during training
        from sklearn.utils.extmath import randomized_svd
        T_centered = teacher_means - teacher_means.mean(axis=0, keepdims=True)
        _, _, Vt = randomized_svd(T_centered, n_components=D_STUDENT, n_iter=4, random_state=42)
        teacher_reduced = T_centered @ Vt[:D_STUDENT, :].T  # (N_ALIGN, d_student)

        alignments[pass_idx] = {
            "teacher_means": teacher_means,
            "teacher_reduced": teacher_reduced,
            "Vt": Vt[:D_STUDENT, :],
        }

        log(f"  Pass {pass_idx} (depth {depth_idx}): "
            f"teacher variance in {D_STUDENT}D: "
            f"{np.var(teacher_reduced):.4f}")

    # ── Summary of what we have ──
    log(f"\n{'=' * 60}")
    log(f"  Setup complete in {time.time()-t0:.1f}s")
    log(f"  Teacher: {manifest['model']}, d={D_TEACHER}")
    log(f"  Student: v6, d={D_STUDENT}")
    log(f"  Probes for alignment: {N_ALIGN}")
    log(f"  Depth mappings: {DEPTH_TO_PASS}")
    log(f"  Ready for distillation training.")
    log(f"{'=' * 60}")

    # Save alignment data for later use
    align_data = {
        "depth_to_pass": DEPTH_TO_PASS,
        "n_align_probes": N_ALIGN,
        "d_student": D_STUDENT,
        "d_teacher": D_TEACHER,
        "elapsed_setup": time.time() - t0,
    }
    with open(RESULTS_DIR / "alignment_setup.json", "w") as f:
        json.dump(align_data, f, indent=2)

    log(f"\n  Alignment data saved to {RESULTS_DIR}/alignment_setup.json")
    log(f"  Next: implement distillation training loop")
    log(f"  (The teacher hidden states are loaded and PCA-reduced)")


if __name__ == "__main__":
    main()
