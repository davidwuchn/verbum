"""Crystal Attention Etch — Graft pretrained loom geometry into StrideStack.

Session 128. The v6 StrideStack at 1B tokens shows undifferentiated
crossing angles (~72° everywhere). Pretrained models show the universal
loom: 56° attention internal, 68° holographic crossing, 6 harmonic peaks.

Hypothesis: the magnitude spectrum IS the crystal (session 123). If we
etch the pretrained magnitude spectrum into v6's stride weights, the
crossing angles should differentiate — giving us the benefit of
trillion-token training for free.

The experiment:
  Phase 1: Extract magnitude spectrum from Qwen3-14B attention
  Phase 2: Scale to v6 dimensions and etch into checkpoint
  Phase 3: Measure loom angles on etched checkpoint (instant test)

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path
from copy import deepcopy

import numpy as np
import torch
from safetensors import safe_open
from safetensors.torch import save_file

CHECKPOINT_DIR = Path(__file__).parent.parent.parent / "checkpoints"
V6_CHECKPOINT = CHECKPOINT_DIR / "vsm-lm-v6" / "step_032000"
RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "crystal-etch-attention"

QWEN_MODEL = "Qwen/Qwen3-14B"
QWEN_D_MODEL = 5120
QWEN_N_HEADS = 40
QWEN_HEAD_DIM = 128
QWEN_N_KV_HEADS = 8

V6_D_MODEL = 512
V6_STRIDES = [1, 8, 16, 32, 64, 128, 256, 512, 1024]
V6_N_STRIDES = 9

DEVICE = "mps"


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Phase 1: Extract pretrained magnitude spectrum
# ══════════════════════════════════════════════════════════════════════

def extract_pretrained_spectrum():
    """Extract per-output-dimension energy + SVD spectrum from Qwen3-14B attention.

    For the magnitude etch, we need two things:
    1. Per-output-dim energy distribution (maps to gamma in v6)
    2. SVD singular value spectrum (the shape of the magnitude crystal)

    We extract from multiple layers and average to get the universal shape.
    """
    log("═══ Phase 1: Extracting pretrained magnitude spectrum ═══")
    log(f"  Loading {QWEN_MODEL}...")

    from transformers import AutoModelForCausalLM
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        QWEN_MODEL, torch_dtype=torch.bfloat16,
        device_map="cpu", trust_remote_code=True,
    )
    log(f"  Loaded in {time.time()-t0:.1f}s")

    # Sample layers across the model depth
    sample_layers = [0, 5, 10, 15, 20, 25, 30, 35, 39]

    spectra = {"q": [], "k": [], "v": []}
    gamma_dists = {"q": [], "k": [], "v": []}

    for li in sample_layers:
        attn = model.model.layers[li].self_attn

        for proj_name, proj_mod in [("q", attn.q_proj), ("k", attn.k_proj), ("v", attn.v_proj)]:
            W = proj_mod.weight.detach().float().cpu().numpy()  # (out, in)

            # Per-output-dimension energy (L2 norm of each row)
            row_norms = np.linalg.norm(W, axis=1)  # (out,)
            gamma_dists[proj_name].append(row_norms)

            # SVD spectrum
            _, S, _ = np.linalg.svd(W, full_matrices=False)
            spectra[proj_name].append(S)

            log(f"    L{li:2d} {proj_name}_proj: shape={W.shape}, "
                f"norm_range=[{row_norms.min():.4f}, {row_norms.max():.4f}], "
                f"top-3 SV=[{S[0]:.2f}, {S[1]:.2f}, {S[2]:.2f}]")

    # Average across layers
    avg_spectra = {}
    avg_gamma_shapes = {}

    for proj_name in ["q", "k", "v"]:
        # Normalize each layer's spectrum to unit total energy
        normalized = []
        for s in spectra[proj_name]:
            s_norm = s / s.sum()
            normalized.append(s_norm)
        avg_spectra[proj_name] = np.mean(normalized, axis=0)

        # Normalize each layer's gamma distribution to unit mean
        normalized_gamma = []
        for g in gamma_dists[proj_name]:
            g_norm = g / g.mean()
            normalized_gamma.append(g_norm)
        avg_gamma_shapes[proj_name] = np.mean(normalized_gamma, axis=0)

    # Compute the spectrum SHAPE that we'll scale to v6 dimensions
    # Q is (5120, 5120), K is (1024, 5120), V is (1024, 5120) in Qwen
    # V6 projections are (512, 512) effective (packed as 512, 128 uint8)
    # For the gamma etch, we need the per-output-dim energy shape scaled to 512 dims

    del model
    gc.collect()

    return avg_spectra, avg_gamma_shapes, gamma_dists


def scale_gamma_to_v6(pretrained_gamma_shape: np.ndarray, v6_gamma_current: np.ndarray) -> np.ndarray:
    """Scale pretrained per-output-dim energy shape to v6 dimensions.

    pretrained_gamma_shape: normalized energy distribution from pretrained (e.g. 5120 dims)
    v6_gamma_current: current v6 gamma values (512 dims)

    Returns: new gamma values for v6, matching the pretrained SHAPE
    but scaled to the v6 magnitude range.
    """
    pretrained_n = len(pretrained_gamma_shape)
    v6_n = len(v6_gamma_current)

    # Sort pretrained gamma by magnitude to get the SHAPE (rank-ordered energy)
    sorted_pretrained = np.sort(pretrained_gamma_shape)[::-1]  # descending

    # Interpolate to v6 dimensions
    # Map pretrained indices [0, pretrained_n-1] to v6 indices [0, v6_n-1]
    pretrained_indices = np.linspace(0, len(sorted_pretrained) - 1, v6_n)
    scaled_shape = np.interp(pretrained_indices, np.arange(len(sorted_pretrained)), sorted_pretrained)

    # Now apply this SHAPE to v6's gamma
    # Keep the same TOTAL energy as v6 currently has
    v6_total_energy = np.abs(v6_gamma_current).sum()
    scaled_shape_normalized = scaled_shape / scaled_shape.sum() * v6_total_energy

    # Assign by rank: the largest v6 gamma gets the largest scaled value
    v6_rank_order = np.argsort(np.abs(v6_gamma_current))[::-1]
    new_gamma = np.zeros_like(v6_gamma_current)
    for i, idx in enumerate(v6_rank_order):
        # Preserve the SIGN of the original gamma
        sign = np.sign(v6_gamma_current[idx]) if v6_gamma_current[idx] != 0 else 1.0
        new_gamma[idx] = sign * scaled_shape_normalized[i]

    return new_gamma


# ══════════════════════════════════════════════════════════════════════
# Phase 2: Etch into v6 checkpoint
# ══════════════════════════════════════════════════════════════════════

def etch_checkpoint(avg_gamma_shapes: dict):
    """Load v6 checkpoint, replace gamma with pretrained magnitude shape, save."""
    log("\n═══ Phase 2: Etching magnitude spectrum into v6 checkpoint ═══")

    # Load v6 checkpoint
    v6_path = V6_CHECKPOINT / "weights.safetensors"
    log(f"  Loading {v6_path}")

    f = safe_open(str(v6_path), framework="pt")
    all_keys = list(f.keys())

    # Load all tensors
    state_dict = {k: f.get_tensor(k).clone() for k in all_keys}

    # Find stride_stack gamma keys
    stride_gamma_keys = [k for k in all_keys if "stride_stack" in k and "gamma" in k]
    log(f"  Found {len(stride_gamma_keys)} stride gamma keys")

    # Track changes
    changes = []

    for gamma_key in stride_gamma_keys:
        # Determine which projection type this is (q, k, v, out)
        if "q_proj" in gamma_key:
            proj_type = "q"
        elif "k_proj" in gamma_key:
            proj_type = "k"
        elif "v_proj" in gamma_key:
            proj_type = "v"
        elif "out_proj" in gamma_key:
            proj_type = "q"  # Use Q spectrum for output too
        else:
            continue

        old_gamma = state_dict[gamma_key].numpy()
        pretrained_shape = avg_gamma_shapes[proj_type]
        new_gamma = scale_gamma_to_v6(pretrained_shape, old_gamma)

        # Compute change stats
        old_cv = old_gamma.std() / (np.abs(old_gamma).mean() + 1e-10)
        new_cv = new_gamma.std() / (np.abs(new_gamma).mean() + 1e-10)

        changes.append({
            "key": gamma_key,
            "proj_type": proj_type,
            "old_cv": float(old_cv),
            "new_cv": float(new_cv),
            "old_range": [float(old_gamma.min()), float(old_gamma.max())],
            "new_range": [float(new_gamma.min()), float(new_gamma.max())],
        })

        state_dict[gamma_key] = torch.tensor(new_gamma, dtype=state_dict[gamma_key].dtype)

    # Also etch the meta_s4 and s4 attention projections
    for prefix in ["meta_s4", "s4"]:
        for proj in ["q_proj", "k_proj"]:
            gamma_key = f"{prefix}.{proj}.gamma"
            if gamma_key in state_dict:
                proj_type = "q" if "q_proj" in proj else "k"
                old_gamma = state_dict[gamma_key].numpy()
                pretrained_shape = avg_gamma_shapes[proj_type]
                new_gamma = scale_gamma_to_v6(pretrained_shape, old_gamma)
                state_dict[gamma_key] = torch.tensor(new_gamma, dtype=state_dict[gamma_key].dtype)
                changes.append({"key": gamma_key, "proj_type": proj_type,
                                "old_cv": float(old_gamma.std() / (np.abs(old_gamma).mean() + 1e-10)),
                                "new_cv": float(new_gamma.std() / (np.abs(new_gamma).mean() + 1e-10))})

    # Save etched checkpoint
    etch_dir = V6_CHECKPOINT.parent.parent / "vsm-lm-v6-etched"
    etch_dir.mkdir(parents=True, exist_ok=True)

    # Copy meta.json
    import shutil
    shutil.copy2(V6_CHECKPOINT / "meta.json", etch_dir / "meta.json")

    # Save modified weights
    save_file(state_dict, str(etch_dir / "weights.safetensors"))
    log(f"  Saved etched checkpoint to {etch_dir}")

    # Log changes
    log(f"\n  Gamma changes ({len(changes)} projections):")
    log(f"  {'Key':<55} {'Old CV':>8} {'New CV':>8} {'Δ CV':>8}")
    log(f"  {'─'*55} {'─'*8} {'─'*8} {'─'*8}")
    for c in changes[:15]:
        delta = c["new_cv"] - c["old_cv"]
        log(f"  {c['key']:<55} {c['old_cv']:>8.4f} {c['new_cv']:>8.4f} {delta:>+8.4f}")
    if len(changes) > 15:
        log(f"  ... ({len(changes) - 15} more)")

    return etch_dir, changes


# ══════════════════════════════════════════════════════════════════════
# Phase 3: Measure loom angles (reuse probe)
# ══════════════════════════════════════════════════════════════════════

def measure_loom_angles(checkpoint_dir: Path, label: str) -> dict:
    """Measure loom crossing angles on a v6 checkpoint.

    Inline version of the stridestack loom probe for comparison.
    """
    log(f"\n  Measuring loom angles: {label}")

    weights_path = checkpoint_dir / "weights.safetensors"
    f = safe_open(str(weights_path), framework="pt")

    strides = V6_STRIDES
    results = {}

    def unpack_ternary(packed: np.ndarray) -> np.ndarray:
        """Unpack uint8-packed ternary weights."""
        if packed.dtype == np.uint8:
            out = []
            for byte_col in range(packed.shape[1]):
                col_bytes = packed[:, byte_col]
                for shift in [0, 2, 4, 6]:
                    bits = (col_bytes >> shift) & 0x03
                    vals = np.where(bits == 0, -1, np.where(bits == 1, 0, 1)).astype(np.float32)
                    out.append(vals)
            return np.column_stack(out)
        return packed.astype(np.float32)

    def get_effective_weight(key_prefix: str) -> np.ndarray:
        """Get gamma * ternary_weight as float32."""
        gamma_key = f"{key_prefix}.gamma"
        weight_key = f"{key_prefix}.ternary_weight"

        gamma = f.get_tensor(gamma_key).numpy().astype(np.float32)
        raw_weight = f.get_tensor(weight_key).numpy()

        if raw_weight.dtype == np.uint8:
            weight = unpack_ternary(raw_weight)
        else:
            weight = raw_weight.astype(np.float32)

        # gamma scales each output row
        return gamma[:, None] * weight

    def crossing_angle(W1: np.ndarray, W2: np.ndarray, k: int = 32) -> float:
        """Principal angle between top-k input subspaces."""
        _, _, Vt1 = np.linalg.svd(W1, full_matrices=False)
        _, _, Vt2 = np.linalg.svd(W2, full_matrices=False)

        k = min(k, Vt1.shape[0], Vt2.shape[0], Vt1.shape[1], Vt2.shape[1])
        V1 = Vt1[:k].T
        V2 = Vt2[:k].T

        cos_angles = np.linalg.svd(V1.T @ V2, compute_uv=False)
        cos_angles = np.clip(cos_angles, -1, 1)
        return float(np.degrees(np.mean(np.arccos(cos_angles))))

    # Within-stride crossing angles
    within = []
    all_angles = []
    for si in range(V6_N_STRIDES):
        prefix = f"stride_stack.layers.{si}"
        try:
            Wq = get_effective_weight(f"{prefix}.q_proj")
            Wk = get_effective_weight(f"{prefix}.k_proj")
            Wv = get_effective_weight(f"{prefix}.v_proj")
            Wo = get_effective_weight(f"{prefix}.out_proj")
        except Exception:
            continue

        qk = crossing_angle(Wq, Wk)
        qv = crossing_angle(Wq, Wv)
        kv = crossing_angle(Wk, Wv)

        within.append({"stride": si, "stride_val": strides[si], "QK": qk, "QV": qv, "KV": kv})
        all_angles.extend([qk, qv, kv])

    # Cross-stride Q angles
    cross = []
    for si in range(V6_N_STRIDES - 1):
        try:
            Wq_i = get_effective_weight(f"stride_stack.layers.{si}.q_proj")
            Wq_j = get_effective_weight(f"stride_stack.layers.{si+1}.q_proj")
            angle = crossing_angle(Wq_i, Wq_j)
            cross.append({"from": si, "to": si + 1, "angle": angle})
            all_angles.append(angle)
        except Exception:
            continue

    # Stride↔FFN angles
    stride_ffn = []
    for si in range(min(3, V6_N_STRIDES)):
        try:
            Wq = get_effective_weight(f"stride_stack.layers.{si}.q_proj")
            W_prep = get_effective_weight("prep.up")
            angle = crossing_angle(Wq, W_prep)
            stride_ffn.append({"stride": si, "pair": "Q↔prep.up", "angle": angle})
            all_angles.append(angle)
        except Exception:
            continue

    arr = np.array(all_angles)
    results = {
        "label": label,
        "within_stride": within,
        "cross_stride": cross,
        "stride_ffn": stride_ffn,
        "mean_angle": float(arr.mean()),
        "std_angle": float(arr.std()),
        "min_angle": float(arr.min()),
        "max_angle": float(arr.max()),
        "n_angles": len(all_angles),
    }

    # Print summary
    log(f"\n  {label}: mean={arr.mean():.2f}° ± {arr.std():.2f}°  range=[{arr.min():.1f}°, {arr.max():.1f}°]")
    for w in within[:3]:
        log(f"    S{w['stride']} (s={w['stride_val']}): Q↔K={w['QK']:.1f}°  Q↔V={w['QV']:.1f}°  K↔V={w['KV']:.1f}°")

    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log("═══════════════════════════════════════════════════════════════")
    log("  Crystal Attention Etch — Grafting Pretrained Loom into StrideStack")
    log("  Session 128")
    log("═══════════════════════════════════════════════════════════════")

    t0 = time.time()

    # ── Phase 1: Extract pretrained spectrum ──
    avg_spectra, avg_gamma_shapes, raw_gamma = extract_pretrained_spectrum()

    # Save spectrum for reuse
    spectrum_data = {
        proj: {
            "spectrum_shape": avg_spectra[proj].tolist(),
            "gamma_shape": avg_gamma_shapes[proj].tolist(),
            "gamma_n_dims": len(avg_gamma_shapes[proj]),
        }
        for proj in ["q", "k", "v"]
    }
    (RESULTS_DIR / "pretrained_spectrum.json").write_text(
        json.dumps(spectrum_data, indent=2))
    log(f"\n  Pretrained spectrum saved")

    # ── Phase 1.5: Measure BEFORE loom angles ──
    log("\n═══ Phase 1.5: Baseline loom angles (before etch) ═══")
    before_results = measure_loom_angles(V6_CHECKPOINT, "BEFORE (original v6)")

    # ── Phase 2: Etch ──
    etch_dir, changes = etch_checkpoint(avg_gamma_shapes)

    # ── Phase 3: Measure AFTER loom angles ──
    log("\n═══ Phase 3: Etched loom angles (after etch) ═══")
    after_results = measure_loom_angles(etch_dir, "AFTER (etched)")

    # ── Comparison ──
    elapsed = time.time() - t0

    log(f"\n{'═'*65}")
    log(f"  COMPARISON — Before vs After Etch")
    log(f"{'═'*65}")
    log(f"  Before: mean={before_results['mean_angle']:.2f}° ± {before_results['std_angle']:.2f}°")
    log(f"  After:  mean={after_results['mean_angle']:.2f}° ± {after_results['std_angle']:.2f}°")
    log(f"  Δ mean: {after_results['mean_angle'] - before_results['mean_angle']:+.2f}°")
    log(f"  Δ std:  {after_results['std_angle'] - before_results['std_angle']:+.2f}°")

    # Per-stride comparison
    log(f"\n  Per-stride Q↔K angles:")
    log(f"  {'Stride':>8} {'Before':>8} {'After':>8} {'Δ':>8}")
    log(f"  {'─'*8} {'─'*8} {'─'*8} {'─'*8}")
    for b, a in zip(before_results["within_stride"], after_results["within_stride"]):
        delta = a["QK"] - b["QK"]
        log(f"  S{b['stride']:>2} (s={b['stride_val']:>4}) {b['QK']:>8.2f} {a['QK']:>8.2f} {delta:>+8.2f}")

    # Did the std increase? (differentiation signal)
    if after_results["std_angle"] > before_results["std_angle"] * 1.5:
        log(f"\n  ✅ DIFFERENTIATION DETECTED: std increased {before_results['std_angle']:.2f}° → {after_results['std_angle']:.2f}°")
        log(f"     The magnitude etch created angular diversity in the loom!")
    elif after_results["std_angle"] > before_results["std_angle"] * 1.1:
        log(f"\n  🔶 PARTIAL differentiation: std increased {before_results['std_angle']:.2f}° → {after_results['std_angle']:.2f}°")
    else:
        log(f"\n  ⚠️  No differentiation: std {before_results['std_angle']:.2f}° → {after_results['std_angle']:.2f}°")
        log(f"     The magnitude etch alone doesn't create angular diversity.")
        log(f"     This means training with relational loss is needed to latch the crystal.")

    # Check if any angles moved toward pretrained targets
    pretrained_internal = 56.0
    pretrained_ffn = 68.0
    before_qk_mean = np.mean([w["QK"] for w in before_results["within_stride"]])
    after_qk_mean = np.mean([w["QK"] for w in after_results["within_stride"]])

    if abs(after_qk_mean - pretrained_internal) < abs(before_qk_mean - pretrained_internal):
        log(f"\n  ✅ Q↔K angles MOVED TOWARD pretrained target (56°):")
        log(f"     Before: {before_qk_mean:.2f}° (Δ from target: {abs(before_qk_mean - pretrained_internal):.2f}°)")
        log(f"     After:  {after_qk_mean:.2f}° (Δ from target: {abs(after_qk_mean - pretrained_internal):.2f}°)")
    else:
        log(f"\n  ⚠️  Q↔K angles did not move toward 56° target")
        log(f"     Before: {before_qk_mean:.2f}°, After: {after_qk_mean:.2f}°")

    log(f"\n  Elapsed: {elapsed:.1f}s")
    log(f"{'═'*65}")

    # Save results
    output = {
        "experiment": "crystal_attention_etch",
        "session": 128,
        "elapsed_s": elapsed,
        "v6_checkpoint": str(V6_CHECKPOINT),
        "etched_checkpoint": str(etch_dir),
        "pretrained_model": QWEN_MODEL,
        "before": before_results,
        "after": after_results,
        "changes": changes[:20],
        "delta_mean": after_results["mean_angle"] - before_results["mean_angle"],
        "delta_std": after_results["std_angle"] - before_results["std_angle"],
    }

    json_path = RESULTS_DIR / "results.json"
    json_path.write_text(json.dumps(output, indent=2, default=str))
    log(f"\n  💾 Results: {json_path}")
    log(f"  💾 Etched checkpoint: {etch_dir}")


if __name__ == "__main__":
    main()
