"""Direct Crystal Write — one-shot ternary plate programming via reference beam.

Instead of iterative etch (100+ rounds of accumulate→confidence→flip),
this computes the interference pattern analytically from a teacher model's
crystal and writes ternary signs in a single pass.

The algorithm:
  1. Load teacher model (any HF model) + student (V12)
  2. Run backbone probes through teacher → extract hidden states
  3. Run backbone probes through student → extract hidden states
  4. Procrustes alignment on universal fixed points (landmarks)
  5. Forward ALL probes through student, backward through alignment loss
  6. For each TernaryLinear: accumulate outer product signs across all probes
  7. Majority vote → write ternary signs directly

This collapses the etch phase from hours to minutes. The reference beam
from the teacher + Procrustes lens provides enough information to compute
the plate pattern analytically. With 667 backbone probes at 67% pairwise
sign agreement, majority vote gives >99.97% correct positions.

Usage:
    # Direct write from Qwen3-14B teacher
    uv run python scripts/v12/direct_crystal_write.py \\
        --teacher qwen3-14b \\
        --student-weights checkpoints/v12-holo-focused/round_0050/weights.npz \\
        --backbone lattice/backbone_seed.npz \\
        --corpus lattice/diverse_corpus.json \\
        --output checkpoints/v12-crystal-write/

    # Dry run (compute signs but don't write, show stats)
    uv run python scripts/v12/direct_crystal_write.py \\
        --teacher qwen3-14b --dry-run

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

# ── Ensure local imports work ──────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

import mlx.core as mx
import mlx.nn as nn

from config import V12Config
from model import V12Model, create_model, count_parameters
from ternary import (
    TernaryLinear,
    _walk_ternary_modules,
    _is_beam_module,
    _unpack_signal_plane_np,
    _pack_signal_plane_np,
    freeze_ternary_weights,
    restore_ternary,
    DirectionAccumulator,
    init_direction_accumulators,
)

# ── Teacher model registry (same as build_lattice_map.py) ─────────

TEACHERS = {
    "qwen3-14b":   ("Qwen/Qwen3-14B",               40, 5120),
    "mistral-7b":  ("mistralai/Mistral-7B-v0.3",     32, 4096),
    "olmo-2-13b":  ("allenai/OLMo-2-1124-13B",       40, 5120),
    "pythia-2.8b": ("EleutherAI/pythia-2.8b-deduped", 32, 2560),
    "smollm3-3b":  ("HuggingFaceTB/SmolLM3-3B",      36, 2560),
}


# ══════════════════════════════════════════════════════════════════════
# Step 1: Extract teacher hidden states
# ══════════════════════════════════════════════════════════════════════

def extract_teacher_states(
    teacher_key: str,
    probes: list[dict],
    depth_fraction: float = 0.50,
    device: str = "mps",
) -> np.ndarray:
    """Forward probes through teacher, return hidden states at target depth.

    Returns: (n_probes, d_teacher) float32 array of last-token hidden states.
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model = TEACHERS[teacher_key]
    target_layer = int(round(depth_fraction * (n_layers - 1)))
    target_layer = min(target_layer, n_layers - 1)

    print(f"\n  Teacher: {teacher_key} ({model_name})", file=sys.stderr, flush=True)
    print(f"  Target layer: L{target_layer} ({depth_fraction:.0%} depth), d={d_model}",
          file=sys.stderr, flush=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16,
        device_map=device, trust_remote_code=True,
    )
    model.eval()

    # Find transformer layers (handle architectures)
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
    elif hasattr(model, 'transformer') and hasattr(model.transformer, 'h'):
        layers = model.transformer.h
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
    else:
        raise ValueError(f"Cannot find transformer layers for {teacher_key}")

    # Hook target layer
    captured = []

    def hook_fn(module, input, output):
        h = output[0] if isinstance(output, tuple) else output
        captured.append(h[:, -1, :].detach().cpu().float())

    hook = layers[target_layer].register_forward_hook(hook_fn)

    # Forward all probes
    print(f"  Running {len(probes)} probes...", file=sys.stderr, flush=True)
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 100 == 0:
            print(f"    {i+1}/{len(probes)} probes", file=sys.stderr, flush=True)
    dt = time.time() - t0
    print(f"  Done: {dt:.1f}s ({dt/len(probes)*1000:.0f}ms/probe)", file=sys.stderr, flush=True)

    hook.remove()
    states = torch.cat(captured, dim=0).numpy()  # (n_probes, d_teacher)

    # Cleanup
    del model, tokenizer
    gc.collect()
    try:
        import torch as _torch
        if _torch.backends.mps.is_available():
            _torch.mps.empty_cache()
    except Exception:
        pass

    return states


# ══════════════════════════════════════════════════════════════════════
# Step 2: Extract student hidden states
# ══════════════════════════════════════════════════════════════════════

def extract_student_states(
    model: V12Model,
    probe_tokens: list[mx.array],
) -> np.ndarray:
    """Forward probes through student, return last-token hidden states.

    Uses model._last_hidden (cached during forward pass).
    Returns: (n_probes, d_student) float32 array.
    """
    hidden_states = []
    for i, tokens in enumerate(probe_tokens):
        logits, aux = model(tokens.reshape(1, -1))
        if hasattr(model, '_last_hidden'):
            h = model._last_hidden[:, -1, :]  # (1, d_model)
            hidden_states.append(np.array(h))
        else:
            raise RuntimeError("Model does not cache _last_hidden")
        if (i + 1) % 100 == 0:
            print(f"    {i+1}/{len(probe_tokens)} student probes",
                  file=sys.stderr, flush=True)
    return np.concatenate(hidden_states, axis=0)  # (n_probes, d_student)


# ══════════════════════════════════════════════════════════════════════
# Step 3: Procrustes alignment
# ══════════════════════════════════════════════════════════════════════

def procrustes_align(
    teacher_states: np.ndarray,
    student_states: np.ndarray,
    backbone_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float, dict]:
    """Compute Procrustes transform from teacher to student space.

    Uses backbone probes (universal fixed points) as landmarks.

    Steps:
      1. Select backbone probes (those with any backbone connections)
      2. PCA both to shared dimensionality
      3. Orthogonal Procrustes: find R such that T @ R ≈ S

    Returns: (teacher_pca_basis, student_pca_basis, scale, stats)
    Where the full transform is:
      translated = (teacher_hidden @ teacher_pca.T @ R * s) @ student_pca
    """
    from scipy.linalg import orthogonal_procrustes

    # Backbone probe indices (any probe with at least one backbone connection)
    backbone_idx = np.where(backbone_mask.sum(axis=1) > 0)[0]
    n_landmarks = len(backbone_idx)
    print(f"  Procrustes: {n_landmarks} landmark probes", file=sys.stderr, flush=True)

    T = teacher_states[backbone_idx]  # (n_landmarks, d_teacher)
    S = student_states[backbone_idx]  # (n_landmarks, d_student)

    # Center
    T_mean = T.mean(axis=0, keepdims=True)
    S_mean = S.mean(axis=0, keepdims=True)
    T_c = T - T_mean
    S_c = S - S_mean

    # PCA to shared dimensionality
    d_shared = min(T.shape[1], S.shape[1], n_landmarks - 1)
    print(f"  Shared dimensionality: {d_shared}", file=sys.stderr, flush=True)

    # Teacher PCA
    U_t, s_t, Vt_t = np.linalg.svd(T_c, full_matrices=False)
    T_pca = U_t[:, :d_shared] * s_t[:d_shared]  # (n_landmarks, d_shared)
    teacher_pca_basis = Vt_t[:d_shared, :]        # (d_shared, d_teacher)

    # Student PCA
    U_s, s_s, Vt_s = np.linalg.svd(S_c, full_matrices=False)
    S_pca = U_s[:, :d_shared] * s_s[:d_shared]   # (n_landmarks, d_shared)
    student_pca_basis = Vt_s[:d_shared, :]         # (d_shared, d_student)

    # Orthogonal Procrustes: T_pca @ R ≈ S_pca
    R, sval = orthogonal_procrustes(T_pca, S_pca)

    # Scale: ratio of norms
    scale = np.linalg.norm(S_pca) / (np.linalg.norm(T_pca @ R) + 1e-8)

    # Quality check: cosine similarity after alignment
    aligned = T_pca @ R * scale
    cos_sims = []
    for i in range(n_landmarks):
        a = aligned[i]
        s = S_pca[i]
        cos = np.dot(a, s) / (np.linalg.norm(a) * np.linalg.norm(s) + 1e-8)
        cos_sims.append(cos)
    mean_cos = np.mean(cos_sims)

    stats = {
        "n_landmarks": n_landmarks,
        "d_shared": d_shared,
        "scale": float(scale),
        "mean_cosine": float(mean_cos),
        "p10_cosine": float(np.percentile(cos_sims, 10)),
        "p50_cosine": float(np.percentile(cos_sims, 50)),
        "p90_cosine": float(np.percentile(cos_sims, 90)),
    }
    print(f"  Alignment quality: cos={mean_cos:.4f} "
          f"(p10={stats['p10_cosine']:.4f}, p90={stats['p90_cosine']:.4f})",
          file=sys.stderr, flush=True)

    return R, teacher_pca_basis, student_pca_basis, T_mean, S_mean, scale, stats


def translate_teacher_rdm(
    teacher_states: np.ndarray,
    R: np.ndarray,
    teacher_pca_basis: np.ndarray,
    student_pca_basis: np.ndarray,
    teacher_mean: np.ndarray,
    student_mean: np.ndarray,
    scale: float,
) -> np.ndarray:
    """Translate teacher's full crystal into student's coordinate system.

    Returns: (n_probes, n_probes) consensus RDM in student space.
    """
    # Project teacher into shared PCA space
    T_c = teacher_states - teacher_mean
    T_pca = T_c @ teacher_pca_basis.T   # (n_probes, d_shared)

    # Rotate + scale into student space
    translated = T_pca @ R * scale       # (n_probes, d_shared)

    # Compute RDM (cosine similarity, mean-subtracted)
    norms = np.linalg.norm(translated, axis=1, keepdims=True)
    translated_norm = translated / (norms + 1e-8)
    rdm = translated_norm @ translated_norm.T
    rdm_centered = rdm - rdm.mean()
    np.fill_diagonal(rdm_centered, 0.0)

    return rdm_centered


# ══════════════════════════════════════════════════════════════════════
# Step 4: Direct crystal write — one-shot ternary programming
# ══════════════════════════════════════════════════════════════════════

def direct_crystal_write(
    model: V12Model,
    probe_tokens: list[mx.array],
    target_rdm: np.ndarray,
    backbone_mask: np.ndarray,
    agreement_weights: np.ndarray,
    backbone_lambda: float = 1.0,
    growth_lambda: float = 0.1,
    dry_run: bool = False,
) -> dict:
    """One-shot crystal write using reference beam.

    For each probe: forward through student, backward through alignment loss.
    Accumulates outer product signs (gamma_grad ⊗ x_mean) across ALL probes.
    Majority vote → write ternary signs directly.

    This is the same math as the iterative etch, but done in a single pass
    with a known-good reference beam instead of iterating to convergence.

    Args:
        model: V12 student model (TernaryLinear weights will be written)
        probe_tokens: Tokenized probes for student
        target_rdm: Procrustes-translated RDM from teacher (n_probes, n_probes)
        backbone_mask: Binary mask of backbone pairs (n_probes, n_probes)
        agreement_weights: Continuous agreement weights (n_probes, n_probes)
        backbone_lambda: Weight for backbone (tier 1) loss
        growth_lambda: Weight for growth (tier 2) loss
        dry_run: If True, compute signs but don't write

    Returns: dict with stats (total_flipped, per_module, confidence, etc.)
    """
    n_probes = len(probe_tokens)

    # ── Initialize accumulators for ALL etchable modules ──────
    accumulators = init_direction_accumulators(model)
    print(f"  Etchable modules: {len(accumulators)}", file=sys.stderr, flush=True)

    # Pre-convert targets to MLX
    target_mx = mx.array(target_rdm.astype(np.float32))
    bb_mask_mx = mx.array(backbone_mask.astype(np.float32))
    agree_mx = mx.array(agreement_weights.astype(np.float32))

    # ── Batch probes through student and accumulate ───────────
    # We process in mini-batches of probes. For each batch:
    # 1. Forward all probes, collect hidden states
    # 2. Compute student RDM for this batch
    # 3. Backward through alignment loss
    # 4. Accumulate (gamma_grad, x_mean) into accumulators

    batch_size = 50  # probes per backward pass (memory limit)
    n_batches = (n_probes + batch_size - 1) // batch_size

    print(f"  Processing {n_probes} probes in {n_batches} batches...",
          file=sys.stderr, flush=True)
    t0 = time.time()

    for batch_idx in range(n_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, n_probes)
        probe_indices = np.arange(start, end)
        probe_indices_mx = mx.array(probe_indices)
        n = len(probe_indices)

        # ── Forward: collect hidden states ────────────────────
        def crystal_loss_fn(model):
            hidden_states = []
            for idx in probe_indices:
                tokens = probe_tokens[idx]
                logits, aux = model(tokens.reshape(1, -1))
                if hasattr(model, '_last_hidden'):
                    h = model._last_hidden[:, -1, :]
                else:
                    return mx.array(0.0)
                hidden_states.append(h)

            h_stack = mx.concatenate(hidden_states, axis=0)  # (n, d_model)

            # L2-normalize
            h_norm = h_stack / (mx.sqrt(mx.sum(h_stack * h_stack, axis=-1, keepdims=True)) + 1e-8)

            # Student RDM (cosine, mean-subtracted)
            student_rdm = h_norm @ h_norm.T
            student_rdm = student_rdm - mx.mean(student_rdm)

            # Target sub-matrix (use mx indices for MLX arrays)
            target_sub = target_mx[probe_indices_mx][:, probe_indices_mx]
            bb_sub = bb_mask_mx[probe_indices_mx][:, probe_indices_mx]
            agree_sub = agree_mx[probe_indices_mx][:, probe_indices_mx]

            # Upper triangle mask (vectorized)
            triu = mx.triu(mx.ones((n, n)), k=1)

            diff = (student_rdm - target_sub) ** 2

            # Two-tier loss
            bb_diff = diff * bb_sub * triu
            n_bb = mx.sum(bb_sub * triu)
            bb_loss = mx.sum(bb_diff) / (n_bb + 1e-8)

            growth_mask = agree_sub * (1.0 - bb_sub) * triu
            growth_diff = diff * growth_mask
            n_growth = mx.sum(growth_mask)
            growth_loss = mx.sum(growth_diff) / (n_growth + 1e-8)

            return backbone_lambda * bb_loss + growth_lambda * growth_loss

        # ── Backward: get gradients ───────────────────────────
        loss_and_grad = nn.value_and_grad(model, crystal_loss_fn)
        loss_val, grads = loss_and_grad(model)
        mx.eval(loss_val, grads)

        # ── Accumulate into direction accumulators ────────────
        from ternary import accumulate_direction
        accumulate_direction(model, grads, accumulators)

        del loss_val, grads
        mx.clear_cache()

        if (batch_idx + 1) % 5 == 0 or batch_idx == n_batches - 1:
            elapsed = time.time() - t0
            print(f"    Batch {batch_idx+1}/{n_batches} "
                  f"({elapsed:.1f}s elapsed)",
                  file=sys.stderr, flush=True)

    dt = time.time() - t0
    print(f"  Accumulation complete: {dt:.1f}s", file=sys.stderr, flush=True)

    # ── Majority vote: read accumulated directions ────────────
    total_flipped = 0
    total_positions = 0
    per_module = {}

    for path, mod in _walk_ternary_modules(model):
        if path not in accumulators:
            continue
        if not isinstance(mod, TernaryLinear):
            continue

        acc = accumulators[path]
        if acc.n_steps == 0:
            continue

        target_signs = acc.get_target_signs()    # (N, K) int8 {-1, 0, +1}
        confidence = acc.get_confidence()         # (N, K) float [0, 1]

        # Current plate signs
        current_signs = _unpack_signal_plane_np(
            np.array(mod.weight), mod.in_features
        )

        # Where target disagrees with current AND target is non-zero
        disagrees = (target_signs != 0) & (target_signs != current_signs)
        n_flipped = int(disagrees.sum())
        n_total = int(current_signs.size)
        mean_conf = float(confidence[disagrees].mean()) if n_flipped > 0 else 0.0

        if not dry_run and n_flipped > 0:
            # Write directly!
            new_signs = np.where(disagrees, target_signs, current_signs)
            mod.weight = mx.array(_pack_signal_plane_np(new_signs))
            mx.eval(mod.weight)

        per_module[path] = {
            "n_flipped": n_flipped,
            "total_positions": n_total,
            "flip_fraction": n_flipped / max(n_total, 1),
            "mean_confidence": mean_conf,
            "n_steps": acc.n_steps,
        }
        total_flipped += n_flipped
        total_positions += n_total

    # ── Summary ───────────────────────────────────────────────
    flip_frac = total_flipped / max(total_positions, 1)
    conf_all = []
    for path in accumulators:
        if accumulators[path].n_steps > 0:
            c = accumulators[path].get_confidence()
            conf_all.append(c.ravel())
    if conf_all:
        conf_flat = np.concatenate(conf_all)
        conf_stats = {
            "mean": float(conf_flat.mean()),
            "p25": float(np.percentile(conf_flat, 25)),
            "p50": float(np.percentile(conf_flat, 50)),
            "p75": float(np.percentile(conf_flat, 75)),
            "p90": float(np.percentile(conf_flat, 90)),
        }
    else:
        conf_stats = {}

    action = "DRY RUN" if dry_run else "WRITTEN"
    print(f"\n  ═══ Direct Crystal Write: {action} ═══",
          file=sys.stderr, flush=True)
    print(f"  Total positions: {total_positions:,}",
          file=sys.stderr, flush=True)
    print(f"  Positions flipped: {total_flipped:,} ({flip_frac:.1%})",
          file=sys.stderr, flush=True)
    print(f"  Confidence: mean={conf_stats.get('mean', 0):.4f} "
          f"p50={conf_stats.get('p50', 0):.4f} "
          f"p90={conf_stats.get('p90', 0):.4f}",
          file=sys.stderr, flush=True)

    return {
        "total_flipped": total_flipped,
        "total_positions": total_positions,
        "flip_fraction": flip_frac,
        "per_module": per_module,
        "confidence_stats": conf_stats,
        "dry_run": dry_run,
        "n_probes": n_probes,
        "elapsed_seconds": dt,
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Direct Crystal Write — one-shot ternary plate programming",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--teacher", type=str, required=True,
                        choices=list(TEACHERS.keys()),
                        help="Teacher model key")
    parser.add_argument("--teacher-depth", type=float, default=0.50,
                        help="Depth fraction for teacher hidden states (default: 0.50)")
    parser.add_argument("--student-weights", type=str, default=None,
                        help="Path to student weights .npz (e.g. from kernel etch)")
    parser.add_argument("--backbone", type=str, default="lattice/backbone_seed.npz",
                        help="Path to backbone_seed.npz")
    parser.add_argument("--corpus", type=str, default="lattice/diverse_corpus.json",
                        help="Path to diverse corpus JSON (probes)")
    parser.add_argument("--output", type=str, default="checkpoints/crystal-write/",
                        help="Output directory for weights + stats")
    parser.add_argument("--backbone-lambda", type=float, default=1.0,
                        help="Weight for backbone (tier 1) loss")
    parser.add_argument("--growth-lambda", type=float, default=0.1,
                        help="Weight for growth (tier 2) loss")
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute signs but don't write (show stats only)")
    parser.add_argument("--device", type=str, default="mps",
                        help="Device for teacher model (default: mps)")

    args = parser.parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("═" * 70, file=sys.stderr, flush=True)
    print("  Direct Crystal Write — One-Shot Plate Programming", file=sys.stderr, flush=True)
    print(f"  Teacher: {args.teacher}", file=sys.stderr, flush=True)
    print(f"  Backbone: {args.backbone}", file=sys.stderr, flush=True)
    print(f"  Corpus: {args.corpus}", file=sys.stderr, flush=True)
    print(f"  Dry run: {args.dry_run}", file=sys.stderr, flush=True)
    print("═" * 70, file=sys.stderr, flush=True)

    # ── Load probes ───────────────────────────────────────────
    print("\n1. Loading probes...", file=sys.stderr, flush=True)
    with open(args.corpus) as f:
        corpus = json.load(f)
    probes = [{"prompt": p["prompt"], "axis": p.get("axis", "unknown")} for p in corpus]
    print(f"  {len(probes)} probes loaded", file=sys.stderr, flush=True)

    # ── Load backbone ─────────────────────────────────────────
    print("\n2. Loading backbone...", file=sys.stderr, flush=True)
    bb = np.load(args.backbone)
    backbone_mask = bb['backbone_mask']
    agreement_weights = bb['agreement_weights']
    n_bb_pairs = int(backbone_mask.sum() / 2)
    n_bb_probes = int((backbone_mask.sum(axis=1) > 0).sum())
    print(f"  {n_bb_pairs} backbone pairs, {n_bb_probes} probes",
          file=sys.stderr, flush=True)

    # ── Extract teacher hidden states ─────────────────────────
    print("\n3. Extracting teacher hidden states...", file=sys.stderr, flush=True)
    teacher_states = extract_teacher_states(
        args.teacher, probes,
        depth_fraction=args.teacher_depth,
        device=args.device,
    )
    print(f"  Teacher states: {teacher_states.shape}", file=sys.stderr, flush=True)

    # ── Create and load student ───────────────────────────────
    print("\n4. Creating student model...", file=sys.stderr, flush=True)
    cfg = V12Config()
    student = create_model(cfg)
    mx.eval(student.parameters())
    n_params = count_parameters(student)
    print(f"  Parameters: {n_params['total']:,}", file=sys.stderr, flush=True)

    if args.student_weights:
        print(f"  Loading weights: {args.student_weights}", file=sys.stderr, flush=True)
        weights = mx.load(args.student_weights)
        student.load_weights(list(weights.items()), strict=False)
        mx.eval(student.parameters())
        print(f"  ✓ Loaded ({len(weights)} arrays)", file=sys.stderr, flush=True)

    # ── Tokenize probes for student ───────────────────────────
    print("\n5. Tokenizing probes for student...", file=sys.stderr, flush=True)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    probe_tokens = []
    for probe in probes:
        ids = tok.encode(probe["prompt"], add_special_tokens=False)
        if len(ids) > 128:
            ids = ids[:128]
        probe_tokens.append(mx.array(ids, dtype=mx.int32))
    del tok
    print(f"  {len(probe_tokens)} probes tokenized", file=sys.stderr, flush=True)

    # ── Extract student hidden states ─────────────────────────
    print("\n6. Extracting student hidden states...", file=sys.stderr, flush=True)
    student_states = extract_student_states(student, probe_tokens)
    print(f"  Student states: {student_states.shape}", file=sys.stderr, flush=True)

    # ── Procrustes alignment ──────────────────────────────────
    print("\n7. Procrustes alignment...", file=sys.stderr, flush=True)
    R, t_pca, s_pca, t_mean, s_mean, scale, proc_stats = procrustes_align(
        teacher_states, student_states, backbone_mask,
    )
    print(f"  ✓ Alignment: cos={proc_stats['mean_cosine']:.4f}",
          file=sys.stderr, flush=True)

    # ── Translate teacher RDM ─────────────────────────────────
    print("\n8. Translating teacher crystal...", file=sys.stderr, flush=True)
    target_rdm = translate_teacher_rdm(
        teacher_states, R, t_pca, s_pca, t_mean, s_mean, scale,
    )
    print(f"  Translated RDM: {target_rdm.shape}, "
          f"range=[{target_rdm.min():.4f}, {target_rdm.max():.4f}]",
          file=sys.stderr, flush=True)

    # ── Direct crystal write ──────────────────────────────────
    print("\n9. Direct crystal write...", file=sys.stderr, flush=True)
    result = direct_crystal_write(
        student, probe_tokens, target_rdm,
        backbone_mask, agreement_weights,
        backbone_lambda=args.backbone_lambda,
        growth_lambda=args.growth_lambda,
        dry_run=args.dry_run,
    )

    # ── Save ──────────────────────────────────────────────────
    if not args.dry_run:
        weights_path = output_dir / "weights.npz"
        print(f"\n10. Saving weights: {weights_path}", file=sys.stderr, flush=True)
        mx.savez(str(weights_path), **dict(student.parameters()))
        print(f"  ✓ Saved", file=sys.stderr, flush=True)

    # Save stats
    stats_path = output_dir / "crystal_write_stats.json"
    stats = {
        "teacher": args.teacher,
        "teacher_depth": args.teacher_depth,
        "n_probes": len(probes),
        "backbone_pairs": n_bb_pairs,
        "procrustes": proc_stats,
        "write": {k: v for k, v in result.items() if k != "per_module"},
        "per_module_summary": {
            path: {
                "n_flipped": info["n_flipped"],
                "total": info["total_positions"],
                "fraction": info["flip_fraction"],
                "confidence": info["mean_confidence"],
            }
            for path, info in result.get("per_module", {}).items()
            if info["n_flipped"] > 0
        },
    }
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"  Stats: {stats_path}", file=sys.stderr, flush=True)

    print(f"\n{'═' * 70}", file=sys.stderr, flush=True)
    print(f"  Done. {'DRY RUN' if args.dry_run else 'Crystal written.'}",
          file=sys.stderr, flush=True)
    print(f"{'═' * 70}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
