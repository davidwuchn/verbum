"""Date/Calendar Fourier Probe — Finding circular features in the combinator tracer.

Session 128. Engels et al. (2024, "Not All Language Model Features Are
One-Dimensionally Linear") found that LLMs encode days of the week and
months of the year as 2D circular features in activation space, and use
these circles for modular arithmetic (e.g. "3 days after Wednesday").

We have the combinator tracer (session 127) that reads FFN activations
as combinator opcodes. This probe bridges the two:

  1. Does date arithmetic use selector combinators (church encoding)?
  2. Or does it use a rotation/Fourier mechanism (circular features)?
  3. Or both — selectors for dispatch, rotation for the actual mod-7/mod-12?
  4. Which layers show circular structure for days/months?
  5. Is this a kernel-replace candidate or an extract candidate?

Analyses:
  A) COMBINATOR TRACE — project date prompts against combinator fingerprints
     (reuses the session 127 tracer). Does date arithmetic look like
     arithmetic (selectors) or like something different?

  B) FOURIER PERIODICITY — apply DFT to FFN activation vectors for
     systematically varied day/month inputs. If mod-7/mod-12 periodicity
     exists, specific Fourier bins will dominate.

  C) CIRCULAR STRUCTURE — PCA on FFN activations for all 7 days / 12 months.
     If the model uses circular features, PCA should reveal a ring in 2D.

  D) ROTATION DETECTION — for "N days after X" with varying N, track how
     the activation vector rotates. If it's a DFT mechanism, equal N
     increments should produce equal angular steps.

  E) CROSS-TASK COMPARISON — compare date vs arithmetic vs retrieval
     combinator profiles. If date uses a different mechanism, the
     combinator signature will differ.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/probe_date_fourier.py 2>&1 | tee results/date-fourier/run.log

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "date-fourier"
FINGERPRINT_PATH = Path(__file__).parent.parent.parent / "results" / "ffn-trace" / "fingerprints.json"
MODEL_NAME = "Qwen/Qwen3-14B"
N_LAYERS = 40
D_MODEL = 5120
DEVICE = "mps"

ALL_LAYERS = list(range(N_LAYERS))

# Days and months for systematic probing
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Model loading & FFN capture (reused from tracer)
# ══════════════════════════════════════════════════════════════════════

def load_model():
    log(f"  Loading {MODEL_NAME}...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.bfloat16,
        device_map=DEVICE, trust_remote_code=True,
    )
    model.eval()
    log(f"  Loaded in {time.time()-t0:.1f}s")
    return model, tokenizer


def capture_ffn_at_layers(model, tokenizer, text: str, layers: list[int]) -> dict:
    """Capture FFN down_proj output at specified layers, last token position."""
    ids = tokenizer.encode(text, return_tensors="pt").to(DEVICE)
    captures = {}
    hooks = []

    for li in layers:
        def make_hook(layer_idx):
            def hook(m, inp, out):
                captures[layer_idx] = out[0, -1, :].detach().cpu().float().numpy()
            return hook
        hooks.append(model.model.layers[li].mlp.down_proj.register_forward_hook(make_hook(li)))

    with torch.no_grad():
        _ = model(ids)

    for h in hooks:
        h.remove()

    return captures


def capture_residual_at_layers(model, tokenizer, text: str, layers: list[int]) -> dict:
    """Capture residual stream (layer output) at specified layers, last token position.

    For circular feature detection we want the full residual stream,
    not just the FFN contribution — following Engels et al.
    """
    ids = tokenizer.encode(text, return_tensors="pt").to(DEVICE)
    captures = {}
    hooks = []

    for li in layers:
        def make_hook(layer_idx):
            def hook(m, inp, out):
                # out is a tuple; first element is the hidden state
                h = out[0] if isinstance(out, tuple) else out
                captures[layer_idx] = h[0, -1, :].detach().cpu().float().numpy()
            return hook
        hooks.append(model.model.layers[li].register_forward_hook(make_hook(li)))

    with torch.no_grad():
        _ = model(ids)

    for h in hooks:
        h.remove()

    return captures


def load_fingerprints() -> dict:
    """Load combinator fingerprints from session 127."""
    with open(FINGERPRINT_PATH) as f:
        raw = json.load(f)

    fingerprints = {}
    for comb, layers in raw.items():
        fingerprints[comb] = {}
        for li_str, vec in layers.items():
            fingerprints[comb][int(li_str)] = np.array(vec, dtype=np.float32)

    return fingerprints


# ══════════════════════════════════════════════════════════════════════
# Probe definitions
# ══════════════════════════════════════════════════════════════════════

def build_day_probes() -> list[dict]:
    """Systematic day-of-week probes for circular feature detection."""
    probes = []

    # Type 1: Direct day naming (baseline — what does each day look like?)
    for day in DAYS:
        probes.append({
            "category": "day_name",
            "label": f"day={day}",
            "text": f"Today is {day}.",
            "day_idx": DAYS.index(day),
        })

    # Type 2: "N days after X" — the modular arithmetic task
    for base_day in ["Monday", "Wednesday", "Friday"]:
        base_idx = DAYS.index(base_day)
        for offset in range(1, 8):  # 1-7 days forward
            target_idx = (base_idx + offset) % 7
            target_day = DAYS[target_idx]
            probes.append({
                "category": "day_add",
                "label": f"{offset} days after {base_day}",
                "text": f"{offset} days after {base_day} is",
                "day_idx": target_idx,
                "offset": offset,
                "base_day": base_day,
            })

    # Type 3: "What day of the week is [date]?" — calendar computation
    # Using dates with known answers
    known_dates = [
        ("January 1, 2025", "Wednesday", 2),
        ("July 4, 2025", "Friday", 4),
        ("December 25, 2025", "Thursday", 3),
        ("February 14, 2025", "Friday", 4),
        ("March 17, 2025", "Monday", 0),
        ("October 31, 2025", "Friday", 4),
        ("May 21, 2026", "Thursday", 3),
    ]
    for date_str, day_name, day_idx in known_dates:
        probes.append({
            "category": "day_from_date",
            "label": f"day of {date_str}",
            "text": f"What day of the week is {date_str}? The answer is",
            "day_idx": day_idx,
            "date": date_str,
            "expected_day": day_name,
        })

    return probes


def build_month_probes() -> list[dict]:
    """Systematic month probes for circular feature detection."""
    probes = []

    # Type 1: Direct month naming
    for month in MONTHS:
        probes.append({
            "category": "month_name",
            "label": f"month={month}",
            "text": f"The month is {month}.",
            "month_idx": MONTHS.index(month),
        })

    # Type 2: "N months after X" — modular arithmetic
    for base_month in ["January", "May", "September"]:
        base_idx = MONTHS.index(base_month)
        for offset in range(1, 13):
            target_idx = (base_idx + offset) % 12
            probes.append({
                "category": "month_add",
                "label": f"{offset} months after {base_month}",
                "text": f"{offset} months after {base_month} is",
                "month_idx": target_idx,
                "offset": offset,
                "base_month": base_month,
            })

    return probes


def build_control_probes() -> list[dict]:
    """Control probes: arithmetic and retrieval for comparison."""
    probes = []

    # Arithmetic (pure mod-7 for direct comparison)
    for a in range(7):
        for b in [1, 2, 3]:
            result = (a + b) % 7
            probes.append({
                "category": "mod7_arithmetic",
                "label": f"({a}+{b}) mod 7 = {result}",
                "text": f"Calculate: ({a} + {b}) mod 7 =",
                "result": result,
            })

    # Regular arithmetic (non-modular)
    for a, b in [(2, 3), (7, 8), (15, 23), (42, 58)]:
        probes.append({
            "category": "plain_arithmetic",
            "label": f"{a}+{b}={a+b}",
            "text": f"Calculate: {a} + {b} =",
            "result": a + b,
        })

    # Factual retrieval (no computation)
    retrieval = [
        ("The capital of France is", "retrieval"),
        ("The chemical symbol for gold is", "retrieval"),
        ("Water freezes at zero degrees", "retrieval"),
        ("Shakespeare wrote Romeo and", "retrieval"),
    ]
    for text, cat in retrieval:
        probes.append({
            "category": "retrieval",
            "label": text[:40],
            "text": text,
        })

    return probes


# ══════════════════════════════════════════════════════════════════════
# Analysis A: Combinator trace for date probes
# ══════════════════════════════════════════════════════════════════════

def trace_against_fingerprints(ffn_captures: dict, fingerprints: dict) -> dict:
    """Project FFN activations against combinator fingerprints."""
    combinator_names = sorted(fingerprints.keys())
    trace = {}

    for li in sorted(ffn_captures.keys()):
        ffn_vec = ffn_captures[li]
        ffn_norm = np.linalg.norm(ffn_vec)
        if ffn_norm < 1e-10:
            trace[li] = {c: 0.0 for c in combinator_names}
            continue

        ffn_unit = ffn_vec / ffn_norm
        scores = {}
        for comb in combinator_names:
            if li in fingerprints[comb]:
                scores[comb] = float(np.dot(ffn_unit, fingerprints[comb][li]))
            else:
                scores[comb] = 0.0
        trace[li] = scores

    return trace


def analyze_combinator_profiles(all_traces: list[dict], fingerprints: dict) -> dict:
    """Compute per-category average combinator activation profiles."""
    combinator_names = sorted(fingerprints.keys())
    categories = sorted(set(t["category"] for t in all_traces))

    profiles = {}
    for cat in categories:
        cat_traces = [t for t in all_traces if t["category"] == cat]
        # Average trace across probes in this category
        # Shape: (n_layers, n_combinators)
        matrix = np.zeros((N_LAYERS, len(combinator_names)))

        for t in cat_traces:
            trace = t["trace"]
            for li in range(N_LAYERS):
                if li in trace:
                    for ci, comb in enumerate(combinator_names):
                        matrix[li, ci] += trace[li].get(comb, 0)
        matrix /= max(len(cat_traces), 1)

        # Compute summary stats
        early = matrix[:13].mean(axis=0)    # L0-L12
        mid = matrix[13:27].mean(axis=0)    # L13-L26
        late = matrix[27:].mean(axis=0)     # L27-L39

        # Which functional group dominates?
        selectors = ["K", "beta_K", "beta_identity"]
        composers = ["B", "S"]
        reorderers = ["C", "beta_apply"]

        def group_score(names, vec):
            indices = [combinator_names.index(n) for n in names if n in combinator_names]
            return float(np.mean([abs(vec[i]) for i in indices])) if indices else 0.0

        profiles[cat] = {
            "n_probes": len(cat_traces),
            "matrix": matrix.tolist(),
            "early": {c: float(early[i]) for i, c in enumerate(combinator_names)},
            "mid": {c: float(mid[i]) for i, c in enumerate(combinator_names)},
            "late": {c: float(late[i]) for i, c in enumerate(combinator_names)},
            "group_early": {
                "selectors": group_score(selectors, early),
                "composers": group_score(composers, early),
                "reorderers": group_score(reorderers, early),
            },
            "group_mid": {
                "selectors": group_score(selectors, mid),
                "composers": group_score(composers, mid),
                "reorderers": group_score(reorderers, mid),
            },
            "group_late": {
                "selectors": group_score(selectors, late),
                "composers": group_score(composers, late),
                "reorderers": group_score(reorderers, late),
            },
        }

    return profiles


# ══════════════════════════════════════════════════════════════════════
# Analysis B: Fourier periodicity in FFN activations
# ══════════════════════════════════════════════════════════════════════

def analyze_fourier_periodicity(day_ffn_vecs: dict, month_ffn_vecs: dict) -> dict:
    """Apply DFT to FFN activations indexed by day/month position.

    If the model uses Fourier features for days (mod 7), then when we
    arrange activations by day index and take the DFT along the day
    dimension, frequency bin 1 (period=7) should dominate.

    Similarly for months (mod 12), frequency bin 1 (period=12).
    """
    results = {"days": {}, "months": {}}

    # ── Days: DFT along the 7-day dimension ──
    for li in ALL_LAYERS:
        if li not in day_ffn_vecs:
            continue

        # day_ffn_vecs[li] shape: (7, D_MODEL)
        vecs = day_ffn_vecs[li]
        if vecs.shape[0] != 7:
            continue

        # DFT along the day dimension for each feature
        # Shape: (7, D_MODEL) → fft along axis 0 → (7, D_MODEL) complex
        fft_result = np.fft.fft(vecs, axis=0)
        power = np.abs(fft_result) ** 2  # (7, D_MODEL)

        # Average power per frequency bin across all features
        mean_power = power.mean(axis=1)  # (7,)
        # Normalize by DC component
        dc_power = mean_power[0]
        if dc_power > 1e-10:
            normalized_power = mean_power / dc_power
        else:
            normalized_power = mean_power

        # Key metric: ratio of fundamental (bin 1, period=7) to total non-DC
        non_dc_total = mean_power[1:].sum()
        fundamental = mean_power[1]  # bin 1 = period 7
        fund_ratio = float(fundamental / non_dc_total) if non_dc_total > 0 else 0

        # How many features have strong fundamental?
        feature_power = power[1, :] / (power[1:, :].sum(axis=0) + 1e-10)
        n_periodic_features = int((feature_power > 0.5).sum())

        results["days"][li] = {
            "mean_power_spectrum": normalized_power.tolist(),
            "fundamental_ratio": fund_ratio,
            "n_periodic_features": n_periodic_features,
            "total_features": int(vecs.shape[1]),
            "dc_power": float(dc_power),
        }

    # ── Months: DFT along the 12-month dimension ──
    for li in ALL_LAYERS:
        if li not in month_ffn_vecs:
            continue

        vecs = month_ffn_vecs[li]
        if vecs.shape[0] != 12:
            continue

        fft_result = np.fft.fft(vecs, axis=0)
        power = np.abs(fft_result) ** 2

        mean_power = power.mean(axis=1)
        dc_power = mean_power[0]
        if dc_power > 1e-10:
            normalized_power = mean_power / dc_power
        else:
            normalized_power = mean_power

        non_dc_total = mean_power[1:].sum()
        fundamental = mean_power[1]  # bin 1 = period 12
        fund_ratio = float(fundamental / non_dc_total) if non_dc_total > 0 else 0

        # Also check bin 2 (period 6 — half-year) and bin 3 (period 4 — quarter)
        bin2_ratio = float(mean_power[2] / non_dc_total) if non_dc_total > 0 else 0
        bin3_ratio = float(mean_power[3] / non_dc_total) if non_dc_total > 0 else 0

        feature_power = power[1, :] / (power[1:, :].sum(axis=0) + 1e-10)
        n_periodic_features = int((feature_power > 0.5).sum())

        results["months"][li] = {
            "mean_power_spectrum": normalized_power.tolist(),
            "fundamental_ratio": fund_ratio,
            "bin2_ratio_half_year": bin2_ratio,
            "bin3_ratio_quarter": bin3_ratio,
            "n_periodic_features": n_periodic_features,
            "total_features": int(vecs.shape[1]),
            "dc_power": float(dc_power),
        }

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis C: Circular structure via PCA
# ══════════════════════════════════════════════════════════════════════

def analyze_circular_structure(day_residual_vecs: dict, month_residual_vecs: dict) -> dict:
    """PCA on residual stream activations to detect circular encoding.

    Engels et al. found that days/months form circles in 2D PCA space
    of the residual stream. We check this at every layer.

    Circularity metric: fit a circle to the 2D PCA projections.
    If points lie on a circle, the radius variance will be low relative
    to mean radius (coefficient of variation of radius).
    """
    results = {"days": {}, "months": {}}

    for li in ALL_LAYERS:
        # ── Days ──
        if li in day_residual_vecs and day_residual_vecs[li].shape[0] == 7:
            vecs = day_residual_vecs[li]  # (7, D_MODEL)

            # Center
            mean_vec = vecs.mean(axis=0)
            centered = vecs - mean_vec

            # PCA via SVD
            U, S, Vt = np.linalg.svd(centered, full_matrices=False)
            # Project onto top 2 PCs
            proj_2d = centered @ Vt[:2].T  # (7, 2)

            # Variance explained by top 2
            total_var = (S ** 2).sum()
            var_explained_2 = float((S[:2] ** 2).sum() / total_var) if total_var > 0 else 0

            # Circularity: compute radius of each point from centroid of projections
            centroid = proj_2d.mean(axis=0)
            radii = np.linalg.norm(proj_2d - centroid, axis=1)
            mean_radius = radii.mean()
            cv_radius = float(radii.std() / mean_radius) if mean_radius > 0 else float('inf')

            # Angular ordering: do the days go around the circle in order?
            angles = np.arctan2(proj_2d[:, 1] - centroid[1], proj_2d[:, 0] - centroid[0])
            # Check if angles are monotonically increasing (mod 2π)
            # Unwrap and check
            unwrapped = np.unwrap(angles)
            diffs = np.diff(unwrapped)
            # All diffs should have the same sign for perfect ordering
            sign_consistency = float(np.abs(np.sum(np.sign(diffs))) / len(diffs))

            # Angular separation between consecutive days
            angular_steps = np.diff(np.sort(angles))
            # For a perfect circle with 7 points, steps should be ~2π/7 ≈ 0.898
            expected_step = 2 * np.pi / 7
            step_uniformity = float(1 - np.std(angular_steps) / expected_step) if expected_step > 0 else 0

            results["days"][li] = {
                "var_explained_2pc": var_explained_2,
                "cv_radius": cv_radius,
                "sign_consistency": sign_consistency,
                "step_uniformity": step_uniformity,
                "mean_radius": float(mean_radius),
                "projections_2d": proj_2d.tolist(),
                "angles": angles.tolist(),
                "singular_values_top5": S[:5].tolist(),
            }

        # ── Months ──
        if li in month_residual_vecs and month_residual_vecs[li].shape[0] == 12:
            vecs = month_residual_vecs[li]  # (12, D_MODEL)

            mean_vec = vecs.mean(axis=0)
            centered = vecs - mean_vec

            U, S, Vt = np.linalg.svd(centered, full_matrices=False)
            proj_2d = centered @ Vt[:2].T  # (12, 2)

            total_var = (S ** 2).sum()
            var_explained_2 = float((S[:2] ** 2).sum() / total_var) if total_var > 0 else 0

            centroid = proj_2d.mean(axis=0)
            radii = np.linalg.norm(proj_2d - centroid, axis=1)
            mean_radius = radii.mean()
            cv_radius = float(radii.std() / mean_radius) if mean_radius > 0 else float('inf')

            angles = np.arctan2(proj_2d[:, 1] - centroid[1], proj_2d[:, 0] - centroid[0])
            unwrapped = np.unwrap(angles)
            diffs = np.diff(unwrapped)
            sign_consistency = float(np.abs(np.sum(np.sign(diffs))) / len(diffs))

            expected_step = 2 * np.pi / 12
            angular_steps = np.diff(np.sort(angles))
            step_uniformity = float(1 - np.std(angular_steps) / expected_step) if expected_step > 0 else 0

            results["months"][li] = {
                "var_explained_2pc": var_explained_2,
                "cv_radius": cv_radius,
                "sign_consistency": sign_consistency,
                "step_uniformity": step_uniformity,
                "mean_radius": float(mean_radius),
                "projections_2d": proj_2d.tolist(),
                "angles": angles.tolist(),
                "singular_values_top5": S[:5].tolist(),
            }

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis D: Rotation detection for "N days after X"
# ══════════════════════════════════════════════════════════════════════

def analyze_rotation(add_traces: list[dict], residual_vecs_by_probe: dict) -> dict:
    """For "N days after X" probes, check if offset N produces proportional rotation.

    If the model uses circular features, then "1 day after Monday" and
    "2 days after Monday" should differ by the same angular step as
    "2 days after Monday" and "3 days after Monday" — constant rotation.
    """
    results = {}

    # Group by base day
    by_base = {}
    for t in add_traces:
        if t["category"] != "day_add":
            continue
        base = t.get("base_day", "")
        if base not in by_base:
            by_base[base] = []
        by_base[base].append(t)

    for base_day, probes in by_base.items():
        # Sort by offset
        probes = sorted(probes, key=lambda p: p.get("offset", 0))

        for li in ALL_LAYERS:
            if li not in results:
                results[li] = {}

            # Get residual vectors for this base day's probes
            vecs = []
            offsets = []
            for p in probes:
                key = p["label"]
                if key in residual_vecs_by_probe and li in residual_vecs_by_probe[key]:
                    vecs.append(residual_vecs_by_probe[key][li])
                    offsets.append(p.get("offset", 0))

            if len(vecs) < 3:
                continue

            vecs = np.array(vecs)  # (n_offsets, D_MODEL)
            # Center
            mean_vec = vecs.mean(axis=0)
            centered = vecs - mean_vec

            # PCA
            U, S, Vt = np.linalg.svd(centered, full_matrices=False)
            proj_2d = centered @ Vt[:2].T  # (n_offsets, 2)

            # Compute angles
            centroid = proj_2d.mean(axis=0)
            angles = np.arctan2(proj_2d[:, 1] - centroid[1], proj_2d[:, 0] - centroid[0])

            # Check for uniform angular steps
            unwrapped = np.unwrap(angles)
            diffs = np.diff(unwrapped)

            if len(diffs) > 1:
                step_mean = np.mean(diffs)
                step_std = np.std(diffs)
                # Uniformity: how consistent are the angular steps?
                step_cv = float(step_std / abs(step_mean)) if abs(step_mean) > 1e-10 else float('inf')

                # Expected step for mod-7 rotation
                expected = 2 * np.pi / 7
                step_ratio = float(abs(step_mean) / expected) if expected > 0 else 0

                if base_day not in results[li]:
                    results[li][base_day] = {}

                results[li][base_day] = {
                    "n_offsets": len(offsets),
                    "step_mean": float(step_mean),
                    "step_std": float(step_std),
                    "step_cv": step_cv,
                    "step_ratio_vs_expected": step_ratio,
                    "angles": angles.tolist(),
                    "offsets": offsets,
                }

    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log("═══════════════════════════════════════════════════════════════")
    log("  Date/Calendar Fourier Probe — Circular Features in LLMs")
    log("  Session 128: bridging Engels et al. and the combinator tracer")
    log("═══════════════════════════════════════════════════════════════")

    t0 = time.time()

    # ── Load model and fingerprints ──
    model, tokenizer = load_model()
    fingerprints = load_fingerprints()
    combinator_names = sorted(fingerprints.keys())
    log(f"  Fingerprints loaded: {combinator_names}")

    # ── Build all probes ──
    day_probes = build_day_probes()
    month_probes = build_month_probes()
    control_probes = build_control_probes()
    all_probes = day_probes + month_probes + control_probes

    log(f"\n  Probes: {len(day_probes)} day + {len(month_probes)} month + {len(control_probes)} control = {len(all_probes)} total")

    # ══════════════════════════════════════════════════════════════
    # Phase 1: Capture all activations
    # ══════════════════════════════════════════════════════════════
    log("\n═══ Phase 1: Capturing FFN + residual activations ═══")

    all_traces = []
    residual_by_probe = {}  # label → {layer: vec}

    # We need systematic day/month vectors for Fourier and PCA analyses
    day_ffn_vecs = {}    # layer → (7, D_MODEL)
    day_res_vecs = {}    # layer → (7, D_MODEL)
    month_ffn_vecs = {}  # layer → (12, D_MODEL)
    month_res_vecs = {}  # layer → (12, D_MODEL)

    for pi, probe in enumerate(all_probes):
        if pi % 20 == 0:
            log(f"  [{pi+1}/{len(all_probes)}] {probe['category']}: {probe['label'][:50]}")

        # Capture FFN activations
        ffn_caps = capture_ffn_at_layers(model, tokenizer, probe["text"], ALL_LAYERS)

        # Capture residual stream activations
        res_caps = capture_residual_at_layers(model, tokenizer, probe["text"], ALL_LAYERS)

        # Project FFN against combinator fingerprints
        trace = trace_against_fingerprints(ffn_caps, fingerprints)

        all_traces.append({
            "category": probe["category"],
            "label": probe["label"],
            "text": probe["text"][:100],
            "trace": trace,
            **{k: v for k, v in probe.items() if k not in ("category", "label", "text")},
        })

        residual_by_probe[probe["label"]] = res_caps

    # ── Collect systematic day vectors ──
    log("\n  Collecting systematic day/month vectors...")
    day_name_probes = [p for p in all_traces if p["category"] == "day_name"]
    day_name_probes.sort(key=lambda p: p.get("day_idx", 0))

    for li in ALL_LAYERS:
        day_ffn = []
        day_res = []
        for p in day_name_probes:
            # Re-capture or use stored
            label = p["label"]
            if li in p["trace"]:
                # We need the raw FFN vec, not the trace. Recapture for day names.
                pass  # We'll recapture below

        # Recapture just the 7 days and 12 months systematically
    day_ffn_all = {}  # {layer: [7 vecs]}
    day_res_all = {}
    for di, day in enumerate(DAYS):
        text = f"Today is {day}."
        ffn = capture_ffn_at_layers(model, tokenizer, text, ALL_LAYERS)
        res = capture_residual_at_layers(model, tokenizer, text, ALL_LAYERS)
        for li in ALL_LAYERS:
            if li not in day_ffn_all:
                day_ffn_all[li] = []
                day_res_all[li] = []
            if li in ffn:
                day_ffn_all[li].append(ffn[li])
            if li in res:
                day_res_all[li].append(res[li])

    for li in ALL_LAYERS:
        if li in day_ffn_all and len(day_ffn_all[li]) == 7:
            day_ffn_vecs[li] = np.array(day_ffn_all[li])
        if li in day_res_all and len(day_res_all[li]) == 7:
            day_res_vecs[li] = np.array(day_res_all[li])

    month_ffn_all = {}
    month_res_all = {}
    for mi, month in enumerate(MONTHS):
        text = f"The month is {month}."
        ffn = capture_ffn_at_layers(model, tokenizer, text, ALL_LAYERS)
        res = capture_residual_at_layers(model, tokenizer, text, ALL_LAYERS)
        for li in ALL_LAYERS:
            if li not in month_ffn_all:
                month_ffn_all[li] = []
                month_res_all[li] = []
            if li in ffn:
                month_ffn_all[li].append(ffn[li])
            if li in res:
                month_res_all[li].append(res[li])

    for li in ALL_LAYERS:
        if li in month_ffn_all and len(month_ffn_all[li]) == 12:
            month_ffn_vecs[li] = np.array(month_ffn_all[li])
        if li in month_res_all and len(month_res_all[li]) == 12:
            month_res_vecs[li] = np.array(month_res_all[li])

    log(f"  Day vectors: {len(day_ffn_vecs)} layers with 7 days")
    log(f"  Month vectors: {len(month_ffn_vecs)} layers with 12 months")

    # ══════════════════════════════════════════════════════════════
    # Phase 2: Analysis A — Combinator profiles
    # ══════════════════════════════════════════════════════════════
    log("\n═══ Phase 2A: Combinator profiles by category ═══")
    profiles = analyze_combinator_profiles(all_traces, fingerprints)

    for cat in sorted(profiles.keys()):
        p = profiles[cat]
        log(f"\n  {cat.upper()} ({p['n_probes']} probes)")
        log(f"    Early:  sel={p['group_early']['selectors']:.3f}  comp={p['group_early']['composers']:.3f}  reord={p['group_early']['reorderers']:.3f}")
        log(f"    Mid:    sel={p['group_mid']['selectors']:.3f}  comp={p['group_mid']['composers']:.3f}  reord={p['group_mid']['reorderers']:.3f}")
        log(f"    Late:   sel={p['group_late']['selectors']:.3f}  comp={p['group_late']['composers']:.3f}  reord={p['group_late']['reorderers']:.3f}")

    # ══════════════════════════════════════════════════════════════
    # Phase 2: Analysis B — Fourier periodicity
    # ══════════════════════════════════════════════════════════════
    log("\n═══ Phase 2B: Fourier periodicity analysis ═══")
    fourier_results = analyze_fourier_periodicity(day_ffn_vecs, month_ffn_vecs)

    log("\n  Day-of-week Fourier (fundamental = period 7):")
    log(f"  {'Layer':>6} {'Fund Ratio':>11} {'N Periodic':>11} {'DC Power':>10}")
    log(f"  {'─'*6} {'─'*11} {'─'*11} {'─'*10}")
    for li in sorted(fourier_results["days"].keys()):
        d = fourier_results["days"][li]
        log(f"  L{li:2d}   {d['fundamental_ratio']:>11.4f} {d['n_periodic_features']:>11} {d['dc_power']:>10.2f}")

    log("\n  Month-of-year Fourier (fundamental = period 12):")
    log(f"  {'Layer':>6} {'Fund Ratio':>11} {'Half-yr':>8} {'Quarter':>8} {'N Periodic':>11}")
    log(f"  {'─'*6} {'─'*11} {'─'*8} {'─'*8} {'─'*11}")
    for li in sorted(fourier_results["months"].keys()):
        d = fourier_results["months"][li]
        log(f"  L{li:2d}   {d['fundamental_ratio']:>11.4f} {d['bin2_ratio_half_year']:>8.4f} {d['bin3_ratio_quarter']:>8.4f} {d['n_periodic_features']:>11}")

    # ══════════════════════════════════════════════════════════════
    # Phase 2: Analysis C — Circular structure
    # ══════════════════════════════════════════════════════════════
    log("\n═══ Phase 2C: Circular structure (PCA) ═══")
    circular_results = analyze_circular_structure(day_res_vecs, month_res_vecs)

    log("\n  Days-of-week circularity (residual stream):")
    log(f"  {'Layer':>6} {'Var 2PC':>8} {'CV Radius':>10} {'Ordering':>9} {'Step Unif':>10}")
    log(f"  {'─'*6} {'─'*8} {'─'*10} {'─'*9} {'─'*10}")
    for li in sorted(circular_results["days"].keys()):
        d = circular_results["days"][li]
        log(f"  L{li:2d}   {d['var_explained_2pc']:>8.4f} {d['cv_radius']:>10.4f} {d['sign_consistency']:>9.4f} {d['step_uniformity']:>10.4f}")

    log("\n  Months-of-year circularity (residual stream):")
    log(f"  {'Layer':>6} {'Var 2PC':>8} {'CV Radius':>10} {'Ordering':>9} {'Step Unif':>10}")
    log(f"  {'─'*6} {'─'*8} {'─'*10} {'─'*9} {'─'*10}")
    for li in sorted(circular_results["months"].keys()):
        d = circular_results["months"][li]
        log(f"  L{li:2d}   {d['var_explained_2pc']:>8.4f} {d['cv_radius']:>10.4f} {d['sign_consistency']:>9.4f} {d['step_uniformity']:>10.4f}")

    # ══════════════════════════════════════════════════════════════
    # Phase 2: Analysis D — Rotation detection
    # ══════════════════════════════════════════════════════════════
    log("\n═══ Phase 2D: Rotation detection ('N days after X') ═══")
    rotation_results = analyze_rotation(all_traces, residual_by_probe)

    # Show a few key layers
    key_layers = [0, 5, 10, 15, 20, 24, 30, 35, 39]
    for li in key_layers:
        if li in rotation_results:
            for base_day, data in rotation_results[li].items():
                log(f"  L{li:2d} {base_day:>12s}: step_cv={data['step_cv']:.3f}  "
                    f"ratio_vs_2π/7={data['step_ratio_vs_expected']:.3f}  "
                    f"mean_step={data['step_mean']:.4f}")

    # ══════════════════════════════════════════════════════════════
    # Phase 3: Cross-task comparison
    # ══════════════════════════════════════════════════════════════
    log("\n═══ Phase 3: Cross-task comparison ═══")

    # Compare day_add vs mod7_arithmetic vs plain_arithmetic
    key_cats = ["day_add", "day_from_date", "mod7_arithmetic", "plain_arithmetic", "retrieval"]
    log(f"\n  Functional group comparison (selector / composer / reorderer):")
    log(f"  {'Category':<20} {'Sel(E)':>8} {'Comp(E)':>8} {'Reord(E)':>9} {'Sel(M)':>8} {'Comp(M)':>8} {'Reord(M)':>9}")
    log(f"  {'─'*20} {'─'*8} {'─'*8} {'─'*9} {'─'*8} {'─'*8} {'─'*9}")
    for cat in key_cats:
        if cat in profiles:
            p = profiles[cat]
            ge = p['group_early']
            gm = p['group_mid']
            log(f"  {cat:<20} {ge['selectors']:>8.4f} {ge['composers']:>8.4f} {ge['reorderers']:>9.4f} "
                f"{gm['selectors']:>8.4f} {gm['composers']:>8.4f} {gm['reorderers']:>9.4f}")

    # ══════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════
    elapsed = time.time() - t0
    log(f"\n{'═'*65}")
    log(f"  SUMMARY — Date/Calendar Fourier Probe")
    log(f"{'═'*65}")

    # Find best circularity layer for days
    if circular_results["days"]:
        best_day_layer = min(circular_results["days"].items(),
                            key=lambda x: x[1]["cv_radius"])
        log(f"\n  Best day circularity: L{best_day_layer[0]} (cv_radius={best_day_layer[1]['cv_radius']:.4f})")

    # Find best circularity layer for months
    if circular_results["months"]:
        best_month_layer = min(circular_results["months"].items(),
                              key=lambda x: x[1]["cv_radius"])
        log(f"  Best month circularity: L{best_month_layer[0]} (cv_radius={best_month_layer[1]['cv_radius']:.4f})")

    # Find strongest Fourier layer for days
    if fourier_results["days"]:
        best_fourier_day = max(fourier_results["days"].items(),
                              key=lambda x: x[1]["fundamental_ratio"])
        log(f"  Strongest day Fourier: L{best_fourier_day[0]} (fund_ratio={best_fourier_day[1]['fundamental_ratio']:.4f})")

    # Find strongest Fourier layer for months
    if fourier_results["months"]:
        best_fourier_month = max(fourier_results["months"].items(),
                                key=lambda x: x[1]["fundamental_ratio"])
        log(f"  Strongest month Fourier: L{best_fourier_month[0]} (fund_ratio={best_fourier_month[1]['fundamental_ratio']:.4f})")

    # Key question: does day arithmetic use selectors or a different mechanism?
    if "day_add" in profiles and "plain_arithmetic" in profiles:
        day_sel = profiles["day_add"]["group_mid"]["selectors"]
        arith_sel = profiles["plain_arithmetic"]["group_mid"]["selectors"]
        day_comp = profiles["day_add"]["group_mid"]["composers"]
        arith_comp = profiles["plain_arithmetic"]["group_mid"]["composers"]

        log(f"\n  Day arithmetic vs plain arithmetic (mid-layers):")
        log(f"    Day add:   selectors={day_sel:.4f}  composers={day_comp:.4f}")
        log(f"    Arith:     selectors={arith_sel:.4f}  composers={arith_comp:.4f}")

        if abs(day_sel - arith_sel) < 0.02:
            log(f"    → Similar selector profiles — may use same church encoding mechanism")
        else:
            log(f"    → Different profiles — date arithmetic may use distinct mechanism")

    log(f"\n  Elapsed: {elapsed:.1f}s")
    log(f"{'═'*65}")

    # ══════════════════════════════════════════════════════════════
    # Save results
    # ══════════════════════════════════════════════════════════════
    output = {
        "experiment": "date_calendar_fourier_probe",
        "session": 128,
        "model": MODEL_NAME,
        "n_layers": N_LAYERS,
        "elapsed_s": elapsed,
        "n_probes": len(all_probes),
        "probe_counts": {
            "day": len(day_probes),
            "month": len(month_probes),
            "control": len(control_probes),
        },
        "combinator_profiles": {
            cat: {k: v for k, v in prof.items() if k != "matrix"}
            for cat, prof in profiles.items()
        },
        "fourier_periodicity": {
            "days": {str(k): v for k, v in fourier_results["days"].items()},
            "months": {str(k): v for k, v in fourier_results["months"].items()},
        },
        "circular_structure": {
            "days": {str(k): v for k, v in circular_results["days"].items()},
            "months": {str(k): v for k, v in circular_results["months"].items()},
        },
        "rotation_detection": {
            str(li): data for li, data in rotation_results.items()
        },
        "cross_task_comparison": {
            cat: {
                "group_early": profiles[cat]["group_early"],
                "group_mid": profiles[cat]["group_mid"],
                "group_late": profiles[cat]["group_late"],
            }
            for cat in key_cats if cat in profiles
        },
    }

    # Save full combinator profile matrices separately (large)
    matrices_output = {
        cat: prof["matrix"]
        for cat, prof in profiles.items()
    }
    np.savez_compressed(
        RESULTS_DIR / "combinator_matrices.npz",
        **{cat: np.array(m) for cat, m in matrices_output.items()}
    )

    json_path = RESULTS_DIR / "results.json"
    json_path.write_text(json.dumps(output, indent=2, default=str))
    log(f"\n  💾 Results: {json_path}")
    log(f"  💾 Matrices: {RESULTS_DIR / 'combinator_matrices.npz'}")

    del model, tokenizer
    gc.collect()
    torch.mps.empty_cache()


if __name__ == "__main__":
    main()
