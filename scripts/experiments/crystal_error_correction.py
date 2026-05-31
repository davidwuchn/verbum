"""Crystal Error Correction — Use KIBC geometry to fix ternary sign errors.

Session 173. The crystal geometry (6+ PCs of combinator fingerprints) provides
an error-correcting code for ternary plates. Each weight row encodes a direction
in R^d_model. The combinator fingerprints define a low-dimensional subspace.
Sign errors inconsistent with the crystal projection can be detected and corrected.

Requires a fully-formed crystal (27B+, coherence >> 3×). At 0.6B the crystal
is too weak — fingerprint projections lack the signal to predict correct signs.

Strategy:
  1. Load ternary plates + combinator fingerprints (both per-layer)
  2. For each weight row in gate/up (R^d_model rows):
     a. Project onto crystal basis (12 combinator directions → orthonormal subspace)
     b. Reconstruct the crystal-component: C = basis^T @ (basis @ row)
     c. Where sign(C_j) != ternary_j AND ternary_j != 0: sign-error candidates
     d. Flip candidates where |C_j| > threshold (confident corrections)
  3. For down projections (shape [d_model, d_ff]):
     Columns are in R^d_model → same logic, operate column-wise
  4. Measure sign accuracy vs original float ground truth before/after

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/crystal_error_correction.py --model 27B
    uv run python scripts/experiments/crystal_error_correction.py --model 27B --sweep
    uv run python scripts/experiments/crystal_error_correction.py --model 27B --threshold 0.05

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import torch
from transformers import AutoModelForCausalLM

# ══════════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent.parent.parent
N_TEST_VECS = 32

MODEL_PRESETS = {
    "0.6B": {
        "model_name": "Qwen/Qwen3-0.6B",
        "n_layers": 28,
        "d_model": 1024,
        "d_ff": 3072,
        "plates_dir": "results/ternary-plates/Qwen_Qwen3-0.6B/plates",
        "fingerprints": "results/hologram-reader/Qwen_Qwen3-0.6B/fingerprints_Qwen_Qwen3-0.6B.npz",
        "results_dir": "results/crystal-error-correction/Qwen_Qwen3-0.6B",
    },
    "14B": {
        "model_name": "Qwen/Qwen3-14B",
        "n_layers": 40,
        "d_model": 5120,
        "d_ff": 17408,
        "plates_dir": "results/ternary-plates/Qwen_Qwen3-14B/plates",
        "fingerprints": "results/hologram-reader/Qwen_Qwen3-14B/fingerprints_Qwen_Qwen3-14B.npz",
        "results_dir": "results/crystal-error-correction/Qwen_Qwen3-14B",
    },
    "27B": {
        "model_name": "Qwen/Qwen3.6-27B",
        "n_layers": 64,
        "d_model": 5120,
        "d_ff": 17408,
        "plates_dir": "results/ternary-plates/Qwen_Qwen3.6-27B/plates",
        "fingerprints": "results/hologram-reader/Qwen_Qwen3.6-27B/fingerprints_Qwen_Qwen3.6-27B.npz",
        "results_dir": "results/crystal-error-correction/Qwen_Qwen3.6-27B",
    },
}


def get_config(preset: str) -> dict:
    cfg = MODEL_PRESETS[preset]
    return {
        "model_name": cfg["model_name"],
        "n_layers": cfg["n_layers"],
        "d_model": cfg["d_model"],
        "d_ff": cfg["d_ff"],
        "plates_dir": PROJECT_ROOT / cfg["plates_dir"],
        "fingerprints_path": PROJECT_ROOT / cfg["fingerprints"],
        "results_dir": PROJECT_ROOT / cfg["results_dir"],
    }


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Crystal Basis Construction
# ══════════════════════════════════════════════════════════════════════

def build_crystal_basis(fingerprints: dict, layer_idx: int, d_model: int) -> np.ndarray:
    """Build orthonormal crystal basis from combinator fingerprints for one layer.

    The fingerprints are 12 directions in R^d_model (one per combinator/operation).
    We use SVD to extract the principal crystal subspace (typically 6-10D).

    Returns:
        basis: (n_components, d_model) orthonormal basis vectors
    """
    vecs = []
    for name, arr in fingerprints.items():
        v = arr[layer_idx]  # (d_model,)
        norm = np.linalg.norm(v)
        if norm > 1e-8:
            vecs.append(v / norm)

    if not vecs:
        return np.zeros((1, d_model), dtype=np.float32)

    V = np.stack(vecs, axis=0).astype(np.float32)  # (n_combinators, d_model)

    # SVD to get orthonormal basis of the crystal subspace
    U, S, Vt = np.linalg.svd(V, full_matrices=False)

    # Keep components with singular value > 10% of max
    threshold = 0.10 * S[0]
    n_keep = max(1, int(np.sum(S > threshold)))

    return Vt[:n_keep]  # (n_keep, d_model)


# ══════════════════════════════════════════════════════════════════════
# Metrics
# ══════════════════════════════════════════════════════════════════════

def compute_metrics(ternary: np.ndarray, gamma: np.ndarray,
                    W_float: np.ndarray) -> tuple[float, float]:
    """Compute sign accuracy and reconstruction cosine.

    sign_accuracy: fraction of non-zero ternary positions where sign matches float.
    recon_cos: cosine sim of (ternary * gamma) @ x vs W_float @ x.
    """
    # Direct sign accuracy
    float_sign = np.sign(W_float).astype(np.int8)
    nonzero_mask = ternary != 0
    n_nonzero = int(np.sum(nonzero_mask))
    if n_nonzero > 0:
        matches = int(np.sum(ternary[nonzero_mask] == float_sign[nonzero_mask]))
        sign_accuracy = matches / n_nonzero
    else:
        sign_accuracy = 0.0

    # Reconstruction cosine via random test vectors
    d_out, d_in = W_float.shape
    rng = np.random.default_rng(42)
    test_vecs = rng.standard_normal((N_TEST_VECS, d_in)).astype(np.float32)

    Wx = W_float @ test_vecs.T
    recon = (ternary.astype(np.float32) * gamma[:, None]) @ test_vecs.T

    Wx_flat = Wx.ravel()
    r_flat = recon.ravel()
    recon_cos = float(np.dot(Wx_flat, r_flat) / (
        np.linalg.norm(Wx_flat) * np.linalg.norm(r_flat) + 1e-10))

    return float(sign_accuracy), recon_cos


# ══════════════════════════════════════════════════════════════════════
# Error Correction Engine
# ══════════════════════════════════════════════════════════════════════

@dataclass
class CorrectionResult:
    name: str
    shape: tuple
    n_nonzero: int
    sign_acc_before: float
    recon_cos_before: float
    sign_acc_after: float
    recon_cos_after: float
    n_candidates: int
    n_flipped: int
    flip_fraction: float
    improvement: float  # sign_acc_after - sign_acc_before

    def to_dict(self):
        return self.__dict__


@dataclass
class LayerResult:
    layer_idx: int
    zone: str
    crystal_dims: int = 0
    gate: Optional[CorrectionResult] = None
    up: Optional[CorrectionResult] = None
    down: Optional[CorrectionResult] = None

    def to_dict(self):
        d = {"layer_idx": self.layer_idx, "zone": self.zone, "crystal_dims": self.crystal_dims}
        if self.gate: d["gate"] = self.gate.to_dict()
        if self.up: d["up"] = self.up.to_dict()
        if self.down: d["down"] = self.down.to_dict()
        return d


def correct_weight_matrix(
    ternary: np.ndarray,
    gamma: np.ndarray,
    W_float: np.ndarray,
    basis: np.ndarray,
    beta_apply: Optional[np.ndarray],
    name: str,
    confidence_threshold: float = 0.02,
    transpose_for_basis: bool = False,
) -> tuple[np.ndarray, CorrectionResult]:
    """Apply crystal error correction to one ternary weight matrix.

    For gate/up [d_ff, d_model]: each ROW is in R^d_model → correct row-wise.
    For down [d_model, d_ff]: each COLUMN is in R^d_model → transpose, correct, transpose back.
    """
    # Measure before
    sign_acc_before, recon_cos_before = compute_metrics(ternary, gamma, W_float)

    # Work on a copy
    corrected = ternary.copy()

    if transpose_for_basis:
        work_matrix = corrected.T  # [d_ff, d_model]
    else:
        work_matrix = corrected    # [d_ff, d_model]

    n_rows, d = work_matrix.shape
    total_candidates = 0
    total_flipped = 0

    for i in range(n_rows):
        row = work_matrix[i].astype(np.float32)
        nonzero_mask = row != 0
        if not nonzero_mask.any():
            continue

        # Project onto crystal basis → crystal component
        coeffs = basis @ row            # (n_components,)
        crystal_comp = coeffs @ basis   # (d_model,)

        # Optionally add β_apply emphasis
        if beta_apply is not None:
            beta_proj = np.dot(row, beta_apply)
            crystal_comp = crystal_comp + 0.5 * beta_proj * beta_apply

        # Find sign disagreements at non-zero positions
        crystal_sign = np.sign(crystal_comp)
        candidates = nonzero_mask & (crystal_sign != row) & (crystal_sign != 0)
        n_cand = int(np.sum(candidates))
        total_candidates += n_cand

        if n_cand == 0:
            continue

        # Only flip where crystal projection is confident
        confident = candidates & (np.abs(crystal_comp) > confidence_threshold)
        n_flip = int(np.sum(confident))
        total_flipped += n_flip

        if n_flip > 0:
            work_matrix[i, confident] = -work_matrix[i, confident]

    if transpose_for_basis:
        corrected = work_matrix.T.copy()
    else:
        corrected = work_matrix

    # Measure after
    sign_acc_after, recon_cos_after = compute_metrics(corrected, gamma, W_float)

    n_nonzero = int(np.sum(ternary != 0))
    result = CorrectionResult(
        name=name,
        shape=tuple(ternary.shape),
        n_nonzero=n_nonzero,
        sign_acc_before=sign_acc_before,
        recon_cos_before=recon_cos_before,
        sign_acc_after=sign_acc_after,
        recon_cos_after=recon_cos_after,
        n_candidates=total_candidates,
        n_flipped=total_flipped,
        flip_fraction=total_flipped / max(1, n_nonzero),
        improvement=sign_acc_after - sign_acc_before,
    )

    return corrected, result


# ══════════════════════════════════════════════════════════════════════
# Main Experiment
# ══════════════════════════════════════════════════════════════════════

def run_experiment(
    preset: str = "27B",
    confidence_threshold: float = 0.02,
    beta_only: bool = False,
    layers_subset: Optional[list] = None,
):
    """Run crystal error correction."""

    cfg = get_config(preset)
    MODEL_NAME = cfg["model_name"]
    N_LAYERS = cfg["n_layers"]
    D_MODEL = cfg["d_model"]
    PLATES_DIR = cfg["plates_dir"]
    FINGERPRINTS_PATH = cfg["fingerprints_path"]
    RESULTS_DIR = cfg["results_dir"]

    t0 = time.time()
    log(f"\n{'═' * 70}")
    log(f"  Crystal Error Correction — {MODEL_NAME}")
    log(f"  Confidence threshold: {confidence_threshold}")
    log(f"  β_apply only: {beta_only}")
    log(f"  Crystal source: {FINGERPRINTS_PATH.name}")
    log(f"{'═' * 70}")

    # ── Load fingerprints ──
    log("\n  Loading combinator fingerprints...")
    fp_data = np.load(FINGERPRINTS_PATH)
    fingerprints = {k: fp_data[k] for k in fp_data.files}
    log(f"  Loaded {len(fingerprints)} directions, shape: {fingerprints[list(fingerprints.keys())[0]].shape}")

    beta_apply_all = fingerprints.get("beta_apply", None)

    # ── Load model for ground truth ──
    log(f"\n  Loading {MODEL_NAME} (bfloat16, convert per-layer)...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, dtype=torch.bfloat16,
        device_map="cpu", low_cpu_mem_usage=True,
        trust_remote_code=True,
    )
    model.eval()
    layers_list = list(model.model.layers)
    log(f"  Loaded {len(layers_list)} layers")

    # ── Verify plates exist ──
    if not PLATES_DIR.exists():
        log(f"\n  ⚠ Plates directory not found: {PLATES_DIR}")
        log(f"  Run extraction first: uv run python scripts/experiments/extract_ternary_plate.py --model {MODEL_NAME}")
        return None

    # ── Process layers ──
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    all_results = []

    layer_indices = layers_subset if layers_subset else list(range(N_LAYERS))

    for li in layer_indices:
        depth_frac = li / max(1, N_LAYERS - 1)
        if depth_frac < 0.50:
            zone = "SILENT"
        elif depth_frac < 0.85:
            zone = "ENRICH"
        elif depth_frac < 0.93:
            zone = "SUPPRESS"
        else:
            zone = "COMMIT"

        # Build crystal basis
        if beta_only:
            if beta_apply_all is not None:
                ba = beta_apply_all[li]
                ba = ba / (np.linalg.norm(ba) + 1e-8)
                basis = ba.reshape(1, -1)
            else:
                basis = np.zeros((1, D_MODEL), dtype=np.float32)
            crystal_dims = 1
        else:
            basis = build_crystal_basis(fingerprints, li, D_MODEL)
            crystal_dims = basis.shape[0]

        # β_apply vector (for additional emphasis beyond basis)
        beta_apply_vec = None
        if beta_apply_all is not None and not beta_only:
            ba = beta_apply_all[li]
            n = np.linalg.norm(ba)
            if n > 1e-8:
                beta_apply_vec = ba / n

        layer_result = LayerResult(layer_idx=li, zone=zone, crystal_dims=crystal_dims)
        mlp = layers_list[li].mlp

        for proj_name, weight_tensor, transpose in [
            ("gate", mlp.gate_proj.weight, False),
            ("up", mlp.up_proj.weight, False),
            ("down", mlp.down_proj.weight, True),
        ]:
            ternary_path = PLATES_DIR / f"L{li:02d}_{proj_name}_ternary.npy"
            gamma_path = PLATES_DIR / f"L{li:02d}_{proj_name}_gamma.npy"

            if not ternary_path.exists():
                log(f"    ⚠ Missing: {ternary_path.name}")
                continue

            ternary = np.load(ternary_path)
            gamma = np.load(gamma_path).astype(np.float32)
            W_float = weight_tensor.detach().cpu().float().numpy()

            corrected, result = correct_weight_matrix(
                ternary, gamma, W_float, basis, beta_apply_vec,
                f"L{li:02d}_{proj_name}", confidence_threshold, transpose)

            if proj_name == "gate": layer_result.gate = result
            elif proj_name == "up": layer_result.up = result
            elif proj_name == "down": layer_result.down = result

            del ternary, gamma, W_float, corrected

        all_results.append(layer_result)

        # Progress
        imps = [r.improvement for r in [layer_result.gate, layer_result.up, layer_result.down] if r]
        avg_imp = np.mean(imps) if imps else 0

        if li % 8 == 0 or li == layer_indices[-1]:
            gate_i = layer_result.gate.improvement if layer_result.gate else 0
            up_i = layer_result.up.improvement if layer_result.up else 0
            down_i = layer_result.down.improvement if layer_result.down else 0
            log(f"    L{li:02d} [{zone:>8}] dims={crystal_dims:2d}  "
                f"Δsign_acc: g={gate_i:+.5f} u={up_i:+.5f} d={down_i:+.5f}  "
                f"avg={avg_imp:+.5f}")

    # ── Aggregate ──
    log(f"\n{'═' * 70}")
    log("  AGGREGATE RESULTS")
    log(f"{'═' * 70}")

    all_improvements = []
    all_before = []
    all_after = []
    all_flips = []
    zone_results = {"SILENT": [], "ENRICH": [], "SUPPRESS": [], "COMMIT": []}

    for lr in all_results:
        for r in [lr.gate, lr.up, lr.down]:
            if r:
                all_improvements.append(r.improvement)
                all_before.append(r.sign_acc_before)
                all_after.append(r.sign_acc_after)
                all_flips.append(r.flip_fraction)
                zone_results[lr.zone].append(r.improvement)

    avg_before = np.mean(all_before) if all_before else 0
    avg_after = np.mean(all_after) if all_after else 0
    avg_imp = np.mean(all_improvements) if all_improvements else 0
    avg_flips = np.mean(all_flips) if all_flips else 0

    log(f"\n  Sign accuracy:     {avg_before:.5f} → {avg_after:.5f}  (Δ = {avg_imp:+.5f})")
    log(f"  Average flip rate: {avg_flips:.4%}")
    log(f"  Total matrices:    {len(all_improvements)}")

    log(f"\n  Per-zone improvement:")
    for zn in ["SILENT", "ENRICH", "SUPPRESS", "COMMIT"]:
        zi = zone_results[zn]
        if zi:
            log(f"    {zn:>8}: Δ = {np.mean(zi):+.5f}  (n={len(zi)}, max={np.max(zi):+.5f})")

    # ── Save ──
    elapsed = time.time() - t0
    output = {
        "model": MODEL_NAME,
        "preset": preset,
        "confidence_threshold": confidence_threshold,
        "beta_only": beta_only,
        "n_layers": len(layer_indices),
        "elapsed_s": elapsed,
        "aggregate": {
            "sign_acc_before": float(avg_before),
            "sign_acc_after": float(avg_after),
            "improvement": float(avg_imp),
            "avg_flip_fraction": float(avg_flips),
        },
        "per_zone": {
            zn: {"mean_improvement": float(np.mean(zi)) if zi else 0,
                 "max_improvement": float(np.max(zi)) if zi else 0,
                 "n_matrices": len(zi)}
            for zn, zi in zone_results.items()
        },
        "per_layer": [lr.to_dict() for lr in all_results],
    }

    results_path = RESULTS_DIR / "results.json"
    with open(results_path, "w") as f:
        json.dump(output, f, indent=2)
    log(f"\n  Results saved: {results_path}")
    log(f"  Elapsed: {elapsed:.1f}s")

    return output


# ══════════════════════════════════════════════════════════════════════
# Threshold Sweep (subset of layers for speed)
# ══════════════════════════════════════════════════════════════════════

def sweep_thresholds(preset: str = "27B"):
    """Sweep confidence thresholds on a sample of layers."""

    cfg = get_config(preset)
    MODEL_NAME = cfg["model_name"]
    N_LAYERS = cfg["n_layers"]
    D_MODEL = cfg["d_model"]
    PLATES_DIR = cfg["plates_dir"]
    FINGERPRINTS_PATH = cfg["fingerprints_path"]
    RESULTS_DIR = cfg["results_dir"]

    log(f"\n{'═' * 70}")
    log(f"  THRESHOLD SWEEP — {MODEL_NAME}")
    log(f"{'═' * 70}")

    thresholds = [0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50]

    fp_data = np.load(FINGERPRINTS_PATH)
    fingerprints = {k: fp_data[k] for k in fp_data.files}
    beta_apply_all = fingerprints.get("beta_apply", None)

    log("  Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, dtype=torch.bfloat16,
        device_map="cpu", low_cpu_mem_usage=True,
        trust_remote_code=True,
    )
    model.eval()
    layers_list = list(model.model.layers)

    # Sample layers evenly across zones
    step = max(1, N_LAYERS // 8)
    test_layers = list(range(0, N_LAYERS, step))
    log(f"  Testing on layers: {test_layers}")

    if not PLATES_DIR.exists():
        log(f"  ⚠ No plates at {PLATES_DIR}")
        return []

    sweep_results = []

    for thresh in thresholds:
        improvements = []
        flip_rates = []

        for li in test_layers:
            basis = build_crystal_basis(fingerprints, li, D_MODEL)
            beta_apply_vec = None
            if beta_apply_all is not None:
                ba = beta_apply_all[li]
                n = np.linalg.norm(ba)
                if n > 1e-8:
                    beta_apply_vec = ba / n

            mlp = layers_list[li].mlp
            for proj_name, wt, transpose in [
                ("gate", mlp.gate_proj.weight, False),
                ("up", mlp.up_proj.weight, False),
                ("down", mlp.down_proj.weight, True),
            ]:
                tp = PLATES_DIR / f"L{li:02d}_{proj_name}_ternary.npy"
                gp = PLATES_DIR / f"L{li:02d}_{proj_name}_gamma.npy"
                if not tp.exists():
                    continue

                ternary = np.load(tp)
                gamma = np.load(gp).astype(np.float32)
                W_float = wt.detach().cpu().float().numpy()

                _, result = correct_weight_matrix(
                    ternary, gamma, W_float, basis, beta_apply_vec,
                    f"L{li:02d}_{proj_name}", thresh, transpose)

                improvements.append(result.improvement)
                flip_rates.append(result.flip_fraction)

        avg_imp = float(np.mean(improvements)) if improvements else 0
        avg_flip = float(np.mean(flip_rates)) if flip_rates else 0
        sweep_results.append({"threshold": thresh, "avg_improvement": avg_imp, "avg_flip_rate": avg_flip})
        log(f"    thresh={thresh:.3f}  Δsign_acc={avg_imp:+.6f}  flip_rate={avg_flip:.4%}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / "threshold_sweep.json", "w") as f:
        json.dump(sweep_results, f, indent=2)

    best = max(sweep_results, key=lambda x: x["avg_improvement"])
    log(f"\n  Best: threshold={best['threshold']} → Δ={best['avg_improvement']:+.6f}")

    del model
    gc.collect()
    return sweep_results


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Crystal Error Correction")
    parser.add_argument("--model", type=str, default="27B",
                        choices=list(MODEL_PRESETS.keys()),
                        help="Model preset (default: 27B)")
    parser.add_argument("--threshold", type=float, default=0.02,
                        help="Confidence threshold for sign flips")
    parser.add_argument("--beta-only", action="store_true",
                        help="Only use β_apply direction (1D correction)")
    parser.add_argument("--sweep", action="store_true",
                        help="Sweep thresholds to find optimal")
    parser.add_argument("--layers", type=str, default=None,
                        help="Comma-separated layer indices to process (default: all)")
    args = parser.parse_args()

    layers_subset = None
    if args.layers:
        layers_subset = [int(x) for x in args.layers.split(",")]

    if args.sweep:
        sweep_thresholds(preset=args.model)
    else:
        run_experiment(
            preset=args.model,
            confidence_threshold=args.threshold,
            beta_only=args.beta_only,
            layers_subset=layers_subset,
        )
