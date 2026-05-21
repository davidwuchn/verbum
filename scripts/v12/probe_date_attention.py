"""Date/Calendar Attention Probe — Finding the rotation circuit.

Session 128. The FFN combinator tracer showed that date arithmetic
("3 days after Wednesday") does NOT use the FFN combinator system
(selectors at noise floor: 0.025 vs 0.117 for mod-7 arithmetic).
But circular day encoding IS real in the residual stream (cv_radius=0.21,
ordering=1.0 from L11 onward).

Hypothesis: attention heads perform the rotation. The FFN encodes
days as positions on a circle; attention heads compose the offset
with the base day by rotating the circular representation.

This probe hooks attention to find the rotation circuit:
  A) Per-head attention patterns — who attends to the day token?
  B) Per-head residual contribution — does a head's output rotate
     the circular day encoding by the right amount?
  C) Head ablation — zero individual heads, measure if circular
     structure in the residual stream breaks.
  D) Rotation head identification — which heads produce output
     that's proportional to the day offset?

Architecture: Qwen3-14B
  40 layers × 40 heads (GQA: 8 KV heads × 5 groups)
  head_dim=128, d_model=5120

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/probe_date_attention.py 2>&1 | tee results/date-attention/run.log

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
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "date-attention"
MODEL_NAME = "Qwen/Qwen3-14B"
N_LAYERS = 40
N_HEADS = 40
N_KV_HEADS = 8
HEAD_DIM = 128
D_MODEL = 5120
DEVICE = "mps"

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Focus on layers where circular structure exists (L8-L38)
# Plus a few early layers as controls
PROBE_LAYERS = [0, 4, 8, 10, 11, 12, 14, 16, 20, 24, 28, 30, 32, 35, 38, 39]


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Model loading
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


# ══════════════════════════════════════════════════════════════════════
# Attention capture — per-head output contributions
# ══════════════════════════════════════════════════════════════════════

def capture_attention_outputs(model, tokenizer, text: str, layers: list[int]) -> dict:
    """Capture per-head attention output contributions at specified layers.

    For each layer, we hook after q_proj to get Q, after the full
    self_attn to get the combined output, and we compute per-head
    contributions by reshaping the o_proj input.

    Returns: {layer: {"attn_out": (n_heads, head_dim), "pre_o": (n_heads, head_dim)}}
    """
    ids = tokenizer.encode(text, return_tensors="pt").to(DEVICE)
    seq_len = ids.shape[1]
    captures = {li: {} for li in layers}  # Pre-initialize to avoid hook ordering race
    hooks = []

    # Capture pre-o_proj FIRST (fires inside self_attn.forward, before self_attn post-hook)
    for li in layers:
        def make_o_hook(layer_idx):
            def hook(m, inp, out):
                # inp[0] is the input to o_proj: (B, L, n_heads * head_dim)
                pre_o = inp[0][0, -1, :].detach().cpu().float()  # (n_heads * head_dim,)
                per_head = pre_o.reshape(N_HEADS, HEAD_DIM).numpy()  # (40, 128)
                captures[layer_idx]["per_head_pre_o"] = per_head
            return hook
        hooks.append(model.model.layers[li].self_attn.o_proj.register_forward_hook(make_o_hook(li)))

    # Then capture combined attention output (fires after self_attn.forward completes)
    for li in layers:
        def make_attn_hook(layer_idx):
            def hook(m, inp, out):
                # out is tuple: (hidden_states, attn_weights_optional, past_kv)
                attn_output = out[0]  # (B, L, D_MODEL)
                last_out = attn_output[0, -1, :].detach().cpu().float()  # (D_MODEL,)
                captures[layer_idx]["attn_combined"] = last_out.numpy()
            return hook
        hooks.append(model.model.layers[li].self_attn.register_forward_hook(make_attn_hook(li)))

    with torch.no_grad():
        _ = model(ids)

    for h in hooks:
        h.remove()

    return captures


def capture_attention_weights(model, tokenizer, text: str, layers: list[int]) -> dict:
    """Capture attention weight matrices at specified layers.

    We need to manually compute attention weights since Qwen3 uses
    SDPA which doesn't expose them. We hook q_proj and k_proj outputs,
    then compute QK^T / sqrt(d) ourselves.

    Returns: {layer: {"attn_weights": (n_heads, seq_len) for last query position}}
    """
    ids = tokenizer.encode(text, return_tensors="pt").to(DEVICE)
    seq_len = ids.shape[1]
    q_captures = {}
    k_captures = {}
    hooks = []

    for li in layers:
        def make_q_hook(layer_idx):
            def hook(m, inp, out):
                # out shape after q_proj: (B, L, n_heads * head_dim)
                # After reshape+transpose in forward: (B, n_heads, L, head_dim)
                q = out[0, -1, :].detach().cpu().float()  # (n_heads * head_dim,)
                q_captures[layer_idx] = q.reshape(N_HEADS, HEAD_DIM).numpy()
            return hook
        hooks.append(model.model.layers[li].self_attn.q_proj.register_forward_hook(make_q_hook(li)))

        def make_k_hook(layer_idx):
            def hook(m, inp, out):
                # k_proj output: (B, L, n_kv_heads * head_dim)
                k = out[0].detach().cpu().float()  # (L, n_kv_heads * head_dim)
                k_captures[layer_idx] = k.reshape(seq_len, N_KV_HEADS, HEAD_DIM).numpy()
            return hook
        hooks.append(model.model.layers[li].self_attn.k_proj.register_forward_hook(make_k_hook(li)))

    with torch.no_grad():
        _ = model(ids)

    for h in hooks:
        h.remove()

    # Compute attention weights manually
    results = {}
    for li in layers:
        if li not in q_captures or li not in k_captures:
            continue

        q = q_captures[li]  # (n_heads, head_dim) — last position only
        k = k_captures[li]  # (seq_len, n_kv_heads, head_dim)

        # GQA: expand KV heads to match Q heads
        # Each KV head serves 5 Q heads
        n_groups = N_HEADS // N_KV_HEADS  # 5

        # For each Q head, find its KV group
        attn_weights = np.zeros((N_HEADS, seq_len))
        for h in range(N_HEADS):
            kv_h = h // n_groups
            # Q: (head_dim,), K: (seq_len, head_dim)
            scores = q[h] @ k[:, kv_h, :].T / np.sqrt(HEAD_DIM)
            # Softmax
            scores = scores - scores.max()
            exp_scores = np.exp(scores)
            attn_weights[h] = exp_scores / exp_scores.sum()

        results[li] = {"attn_weights": attn_weights}

    return results


def capture_residual_at_layers(model, tokenizer, text: str, layers: list[int]) -> dict:
    """Capture residual stream at specified layers, last token position."""
    ids = tokenizer.encode(text, return_tensors="pt").to(DEVICE)
    captures = {}
    hooks = []

    for li in layers:
        def make_hook(layer_idx):
            def hook(m, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                captures[layer_idx] = h[0, -1, :].detach().cpu().float().numpy()
            return hook
        hooks.append(model.model.layers[li].register_forward_hook(make_hook(li)))

    with torch.no_grad():
        _ = model(ids)

    for h in hooks:
        h.remove()

    return captures


# ══════════════════════════════════════════════════════════════════════
# Probe definitions
# ══════════════════════════════════════════════════════════════════════

def build_probes() -> list[dict]:
    """Build day-of-week addition probes with token position annotations."""
    probes = []

    # "N days after X is" — systematic
    for base_day in ["Monday", "Wednesday", "Friday"]:
        base_idx = DAYS.index(base_day)
        for offset in range(1, 8):
            target_idx = (base_idx + offset) % 7
            probes.append({
                "category": "day_add",
                "label": f"{offset} after {base_day}",
                "text": f"{offset} days after {base_day} is",
                "base_day": base_day,
                "base_idx": base_idx,
                "offset": offset,
                "target_idx": target_idx,
                "target_day": DAYS[target_idx],
            })

    # Mod-7 arithmetic control
    for a in [1, 3, 5]:
        for b in range(1, 8):
            result = (a + b) % 7
            probes.append({
                "category": "mod7",
                "label": f"({a}+{b})%7={result}",
                "text": f"({a} + {b}) mod 7 =",
                "offset": b,
                "target_idx": result,
            })

    # Pure day naming (baseline)
    for day in DAYS:
        probes.append({
            "category": "day_name",
            "label": f"day={day}",
            "text": f"Today is {day}.",
            "target_idx": DAYS.index(day),
        })

    return probes


def find_token_positions(tokenizer, text: str, target_strings: list[str]) -> dict:
    """Find token positions of target strings in the tokenized text."""
    ids = tokenizer.encode(text)
    tokens = tokenizer.convert_ids_to_tokens(ids)

    positions = {}
    for target in target_strings:
        target_tokens = tokenizer.encode(target, add_special_tokens=False)
        # Find in the token sequence
        for i in range(len(ids)):
            if ids[i:i+len(target_tokens)] == target_tokens:
                positions[target] = list(range(i, i + len(target_tokens)))
                break
        # Also try matching by decoded text
        if target not in positions:
            for i, tok in enumerate(tokens):
                # Clean token (remove Ġ prefix etc)
                clean = tok.replace("Ġ", " ").replace("▁", " ").strip()
                if clean.lower() == target.lower():
                    positions[target] = [i]
                    break

    return positions


# ══════════════════════════════════════════════════════════════════════
# Analysis A: Which heads attend to the day token?
# ══════════════════════════════════════════════════════════════════════

def analyze_day_attention(all_attn_weights: list[dict]) -> dict:
    """For day_add probes, measure attention to the day token position."""
    results = {}

    for probe_data in all_attn_weights:
        if probe_data["category"] != "day_add":
            continue

        day_positions = probe_data.get("day_positions", [])
        if not day_positions:
            continue

        for li, layer_data in probe_data["attn_weights"].items():
            if li not in results:
                results[li] = {"per_head_day_attn": np.zeros(N_HEADS), "count": 0}

            weights = layer_data["attn_weights"]  # (n_heads, seq_len)
            # Sum attention to day token positions
            day_attn = weights[:, day_positions].sum(axis=1)  # (n_heads,)
            results[li]["per_head_day_attn"] += day_attn
            results[li]["count"] += 1

    # Average
    for li in results:
        if results[li]["count"] > 0:
            results[li]["per_head_day_attn"] /= results[li]["count"]

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis B: Per-head rotation contribution
# ══════════════════════════════════════════════════════════════════════

def analyze_head_rotation(
    head_outputs_by_probe: list[dict],
    day_circle_basis: dict,
) -> dict:
    """For each head, measure if its output rotates the day representation.

    day_circle_basis: {layer: (2, D_MODEL)} — top-2 PCA directions of
    the day circle at each layer. We project each head's output onto
    this 2D plane and check if offset N produces proportional rotation.
    """
    results = {}

    # Group day_add probes by base_day
    by_base = {}
    for pd in head_outputs_by_probe:
        if pd["category"] != "day_add":
            continue
        base = pd.get("base_day", "")
        if base not in by_base:
            by_base[base] = []
        by_base[base].append(pd)

    for base_day, probes in by_base.items():
        probes = sorted(probes, key=lambda p: p.get("offset", 0))

        for li in PROBE_LAYERS:
            if li not in day_circle_basis:
                continue

            basis = day_circle_basis[li]  # (2, D_MODEL)

            # For each head, project its output contribution onto the 2D circle plane
            for h in range(N_HEADS):
                angles = []
                offsets = []

                for p in probes:
                    if li not in p.get("head_outputs", {}):
                        continue
                    per_head = p["head_outputs"][li]  # (n_heads, head_dim)

                    # The per-head output is pre-o_proj, shape (head_dim,)
                    # After o_proj, each head's contribution to residual is:
                    # o_proj_weight[head_slice] @ head_output
                    # But we don't want to extract o_proj weights — instead
                    # we use the combined attention output and the residual diff

                    # Actually, we have per_head_pre_o which is (n_heads, head_dim)
                    # This is BEFORE o_proj. We need the AFTER o_proj contribution.
                    # For now, use the combined attention output projected onto circle basis.
                    pass

                # Alternative: use the residual stream at this layer for different offsets
                # and check angular displacement in the 2D circle plane
                res_angles = []
                for p in probes:
                    if li not in p.get("residuals", {}):
                        continue
                    res = p["residuals"][li]  # (D_MODEL,)
                    # Project onto circle basis
                    proj = basis @ res  # (2,)
                    angle = np.arctan2(proj[1], proj[0])
                    res_angles.append(angle)
                    offsets.append(p.get("offset", 0))

                if len(res_angles) >= 3:
                    unwrapped = np.unwrap(res_angles)
                    # Fit: angle = a * offset + b
                    offsets_arr = np.array(offsets, dtype=float)
                    angles_arr = np.array(unwrapped)
                    # Linear regression
                    A = np.column_stack([offsets_arr, np.ones_like(offsets_arr)])
                    result, residuals, _, _ = np.linalg.lstsq(A, angles_arr, rcond=None)
                    slope = result[0]
                    r_squared = 1 - (residuals[0] / np.var(angles_arr) / len(angles_arr)) if len(residuals) > 0 else 0

                    key = f"L{li}_{base_day}"
                    results[key] = {
                        "layer": li,
                        "base_day": base_day,
                        "slope_rad_per_offset": float(slope),
                        "expected_slope": float(2 * np.pi / 7),
                        "slope_ratio": float(slope / (2 * np.pi / 7)),
                        "r_squared": float(r_squared),
                        "n_points": len(offsets),
                    }

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis C: Head ablation — which heads are necessary?
# ══════════════════════════════════════════════════════════════════════

def ablate_head_and_measure(
    model, tokenizer,
    text: str,
    target_layer: int,
    target_head: int,
    day_circle_basis: dict,
    baseline_angle: float,
) -> dict:
    """Zero one attention head's output, measure circularity change.

    We hook o_proj input to zero one head's slice, then capture the
    residual stream and measure circular structure change.
    """
    ids = tokenizer.encode(text, return_tensors="pt").to(DEVICE)
    residual = {}

    hooks = []

    # Ablation hook: zero the target head's contribution
    def ablation_hook(m, inp, out):
        # inp[0] shape: (B, L, n_heads * head_dim)
        x = inp[0].clone()
        start = target_head * HEAD_DIM
        end = start + HEAD_DIM
        x[:, :, start:end] = 0.0
        # We need to recompute the output with the modified input
        # But we can't modify inp in-place for o_proj...
        # Instead, we modify the OUTPUT by subtracting the head's contribution
        return None  # Can't easily modify — use a different approach

    # Better approach: hook the full layer output and subtract the head contribution
    # Actually, let's use a pre-hook on o_proj to zero the head slice
    def pre_hook(m, inp):
        x = inp[0]
        start = target_head * HEAD_DIM
        end = start + HEAD_DIM
        x[:, :, start:end] = 0.0
        return (x,) + inp[1:] if len(inp) > 1 else (x,)

    hooks.append(model.model.layers[target_layer].self_attn.o_proj.register_forward_pre_hook(pre_hook))

    # Capture residual at and after the ablated layer
    capture_layers = [target_layer, min(target_layer + 1, N_LAYERS - 1), N_LAYERS - 1]
    for li in capture_layers:
        def make_res_hook(layer_idx):
            def hook(m, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                residual[layer_idx] = h[0, -1, :].detach().cpu().float().numpy()
            return hook
        hooks.append(model.model.layers[li].register_forward_hook(make_res_hook(li)))

    with torch.no_grad():
        _ = model(ids)

    for h in hooks:
        h.remove()

    # Measure angle in circle basis at the ablated layer
    if target_layer in residual and target_layer in day_circle_basis:
        basis = day_circle_basis[target_layer]
        proj = basis @ residual[target_layer]
        ablated_angle = float(np.arctan2(proj[1], proj[0]))
        angle_shift = float(ablated_angle - baseline_angle)
    else:
        ablated_angle = None
        angle_shift = None

    return {
        "ablated_angle": ablated_angle,
        "angle_shift": angle_shift,
        "baseline_angle": float(baseline_angle),
    }


# ══════════════════════════════════════════════════════════════════════
# Build day circle basis from residual stream
# ══════════════════════════════════════════════════════════════════════

def build_day_circle_basis(model, tokenizer, layers: list[int]) -> dict:
    """Capture residual stream for all 7 days and compute PCA basis.

    Returns: {layer: basis (2, D_MODEL)} — top-2 PCA directions
    """
    day_vecs = {li: [] for li in layers}

    for day in DAYS:
        text = f"Today is {day}."
        res = capture_residual_at_layers(model, tokenizer, text, layers)
        for li in layers:
            if li in res:
                day_vecs[li].append(res[li])

    basis = {}
    for li in layers:
        if len(day_vecs[li]) == 7:
            vecs = np.array(day_vecs[li])  # (7, D_MODEL)
            mean = vecs.mean(axis=0)
            centered = vecs - mean
            U, S, Vt = np.linalg.svd(centered, full_matrices=False)
            basis[li] = {
                "directions": Vt[:2],  # (2, D_MODEL)
                "singular_values": S[:5].tolist(),
                "mean": mean,
                "projections_2d": (centered @ Vt[:2].T).tolist(),
            }

    return basis


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log("═══════════════════════════════════════════════════════════════")
    log("  Date/Calendar Attention Probe — Finding the Rotation Circuit")
    log("  Session 128: where does mod-7 rotation happen?")
    log("═══════════════════════════════════════════════════════════════")

    t0 = time.time()
    model, tokenizer = load_model()

    # ── Build probes ──
    probes = build_probes()
    day_add_probes = [p for p in probes if p["category"] == "day_add"]
    log(f"\n  Probes: {len(probes)} total, {len(day_add_probes)} day_add")

    # ══════════════════════════════════════════════════════════════
    # Phase 0: Build day circle basis
    # ══════════════════════════════════════════════════════════════
    log("\n═══ Phase 0: Building day circle basis ═══")
    circle_basis = build_day_circle_basis(model, tokenizer, PROBE_LAYERS)
    log(f"  Circle basis computed at {len(circle_basis)} layers")
    for li in sorted(circle_basis.keys()):
        sv = circle_basis[li]["singular_values"]
        log(f"    L{li:2d}: SV=[{sv[0]:.2f}, {sv[1]:.2f}, {sv[2]:.2f}]")

    # ══════════════════════════════════════════════════════════════
    # Phase 1: Capture attention outputs for all probes
    # ══════════════════════════════════════════════════════════════
    log("\n═══ Phase 1: Capturing attention outputs + residuals ═══")

    all_probe_data = []
    for pi, probe in enumerate(probes):
        if pi % 15 == 0:
            log(f"  [{pi+1}/{len(probes)}] {probe['category']}: {probe['label'][:40]}")

        # Find day token positions
        day_positions = []
        if "base_day" in probe:
            pos_map = find_token_positions(tokenizer, probe["text"], [probe["base_day"]])
            if probe["base_day"] in pos_map:
                day_positions = pos_map[probe["base_day"]]

        # Capture per-head outputs
        head_data = capture_attention_outputs(model, tokenizer, probe["text"], PROBE_LAYERS)

        # Capture residuals
        residuals = capture_residual_at_layers(model, tokenizer, probe["text"], PROBE_LAYERS)

        # Capture attention weights (only for day_add probes — expensive)
        attn_weights = {}
        if probe["category"] == "day_add" and day_positions:
            attn_weights = capture_attention_weights(model, tokenizer, probe["text"], PROBE_LAYERS)

        all_probe_data.append({
            **probe,
            "day_positions": day_positions,
            "head_outputs": {li: d.get("per_head_pre_o") for li, d in head_data.items()},
            "attn_combined": {li: d.get("attn_combined") for li, d in head_data.items()},
            "residuals": residuals,
            "attn_weights": attn_weights,
        })

    # ══════════════════════════════════════════════════════════════
    # Phase 2A: Which heads attend to the day token?
    # ══════════════════════════════════════════════════════════════
    log("\n═══ Phase 2A: Day token attention analysis ═══")
    day_attn_results = analyze_day_attention(all_probe_data)

    log(f"\n  Top 5 day-attending heads per layer:")
    log(f"  {'Layer':>6}  {'Head 1':>20}  {'Head 2':>20}  {'Head 3':>20}")
    log(f"  {'─'*6}  {'─'*20}  {'─'*20}  {'─'*20}")

    head_day_attn_total = np.zeros(N_HEADS)  # Accumulate across layers

    for li in sorted(day_attn_results.keys()):
        per_head = day_attn_results[li]["per_head_day_attn"]
        head_day_attn_total += per_head
        top5 = np.argsort(per_head)[-5:][::-1]
        top_strs = [f"H{h:2d}={per_head[h]:.3f}" for h in top5[:3]]
        log(f"  L{li:2d}    {'  '.join(top_strs)}")

    # Overall most day-attending heads
    overall_top = np.argsort(head_day_attn_total)[-10:][::-1]
    log(f"\n  Top 10 day-attending heads (summed across layers):")
    for h in overall_top:
        log(f"    H{h:2d}: total_attn={head_day_attn_total[h]:.4f}")

    # ══════════════════════════════════════════════════════════════
    # Phase 2B: Rotation in residual stream per layer
    # ══════════════════════════════════════════════════════════════
    log("\n═══ Phase 2B: Rotation analysis in residual stream ═══")

    # For each layer, measure how the residual stream angle changes
    # with offset for different base days
    rotation_results = {}
    for base_day in ["Monday", "Wednesday", "Friday"]:
        base_idx = DAYS.index(base_day)
        for li in PROBE_LAYERS:
            if li not in circle_basis:
                continue

            directions = circle_basis[li]["directions"]  # (2, D_MODEL)
            mean = circle_basis[li]["mean"]  # (D_MODEL,)

            angles = []
            offsets = []
            for pd in all_probe_data:
                if pd["category"] != "day_add" or pd.get("base_day") != base_day:
                    continue
                if li not in pd["residuals"]:
                    continue

                res = pd["residuals"][li]
                centered = res - mean
                proj = directions @ centered  # (2,)
                angle = np.arctan2(proj[1], proj[0])
                angles.append(angle)
                offsets.append(pd["offset"])

            if len(angles) >= 3:
                # Unwrap angles and fit linear: angle = slope * offset + intercept
                unwrapped = np.unwrap(angles)
                offsets_arr = np.array(offsets, dtype=float)

                A = np.column_stack([offsets_arr, np.ones_like(offsets_arr)])
                result, residuals_fit, _, _ = np.linalg.lstsq(A, unwrapped, rcond=None)
                slope = result[0]

                # Compute R²
                ss_res = np.sum((unwrapped - A @ result) ** 2)
                ss_tot = np.sum((unwrapped - np.mean(unwrapped)) ** 2)
                r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

                expected_slope = 2 * np.pi / 7

                key = f"L{li}_{base_day}"
                rotation_results[key] = {
                    "layer": li,
                    "base_day": base_day,
                    "slope": float(slope),
                    "expected_slope": float(expected_slope),
                    "slope_ratio": float(slope / expected_slope) if expected_slope > 0 else 0,
                    "r_squared": float(r_squared),
                    "n_points": len(angles),
                    "angles_raw": angles,
                    "offsets": offsets,
                }

    log(f"\n  Rotation linearity (angle = slope * offset):")
    log(f"  {'Layer':>6} {'Base':>12} {'Slope':>8} {'Expected':>9} {'Ratio':>7} {'R²':>7}")
    log(f"  {'─'*6} {'─'*12} {'─'*8} {'─'*9} {'─'*7} {'─'*7}")
    for key in sorted(rotation_results.keys()):
        r = rotation_results[key]
        log(f"  L{r['layer']:2d}   {r['base_day']:>12s} {r['slope']:>8.4f} {r['expected_slope']:>9.4f} "
            f"{r['slope_ratio']:>7.3f} {r['r_squared']:>7.4f}")

    # ══════════════════════════════════════════════════════════════
    # Phase 2C: Head ablation on key layers
    # ══════════════════════════════════════════════════════════════
    log("\n═══ Phase 2C: Head ablation ═══")

    # Pick the layer with best rotation R² and ablate each head
    best_rotation = max(rotation_results.values(), key=lambda r: r["r_squared"])
    ablation_layer = best_rotation["layer"]
    ablation_text = f"3 days after Wednesday is"

    log(f"  Ablating layer L{ablation_layer} (best rotation R²={best_rotation['r_squared']:.4f})")
    log(f"  Probe: '{ablation_text}'")

    # Baseline: no ablation
    baseline_res = capture_residual_at_layers(model, tokenizer, ablation_text, [ablation_layer])
    if ablation_layer in baseline_res and ablation_layer in circle_basis:
        basis_dirs = circle_basis[ablation_layer]["directions"]
        mean = circle_basis[ablation_layer]["mean"]
        baseline_proj = basis_dirs @ (baseline_res[ablation_layer] - mean)
        baseline_angle = float(np.arctan2(baseline_proj[1], baseline_proj[0]))
        baseline_radius = float(np.linalg.norm(baseline_proj))

        log(f"  Baseline: angle={baseline_angle:.4f}, radius={baseline_radius:.4f}")

        ablation_results = {}
        for h in range(N_HEADS):
            result = ablate_head_and_measure(
                model, tokenizer, ablation_text,
                ablation_layer, h,
                {ablation_layer: basis_dirs},
                baseline_angle,
            )
            ablation_results[h] = result

        # Which heads cause the biggest angle shift when removed?
        shifts = [(h, abs(r["angle_shift"])) for h, r in ablation_results.items()
                  if r["angle_shift"] is not None]
        shifts.sort(key=lambda x: x[1], reverse=True)

        log(f"\n  Top 10 heads by angle shift when ablated:")
        log(f"  {'Head':>6} {'Angle Shift':>12} {'Ablated Angle':>14}")
        log(f"  {'─'*6} {'─'*12} {'─'*14}")
        for h, shift in shifts[:10]:
            r = ablation_results[h]
            log(f"  H{h:2d}   {r['angle_shift']:>+12.4f} {r['ablated_angle']:>14.4f}")

        # These heads are the rotation circuit candidates
        rotation_heads = [h for h, shift in shifts[:10]]
    else:
        ablation_results = {}
        rotation_heads = []
        log("  ⚠ Could not compute baseline — skipping ablation")

    # ══════════════════════════════════════════════════════════════
    # Phase 3: Compare day_add vs mod7 attention patterns
    # ══════════════════════════════════════════════════════════════
    log("\n═══ Phase 3: Cross-task attention comparison ═══")

    # Average per-head attention entropy for different categories
    for cat in ["day_add", "mod7", "day_name"]:
        cat_probes = [pd for pd in all_probe_data if pd["category"] == cat]
        if not cat_probes:
            continue

        log(f"\n  {cat.upper()} ({len(cat_probes)} probes):")
        for li in [11, 20, 30, 38]:
            if li not in circle_basis:
                continue

            # Average residual angle per target_idx
            by_target = {}
            for pd in cat_probes:
                tidx = pd.get("target_idx")
                if tidx is None or li not in pd["residuals"]:
                    continue
                if tidx not in by_target:
                    by_target[tidx] = []

                directions = circle_basis[li]["directions"]
                mean = circle_basis[li]["mean"]
                proj = directions @ (pd["residuals"][li] - mean)
                angle = np.arctan2(proj[1], proj[0])
                by_target[tidx].append(angle)

            if by_target:
                # Check if different target_idx map to different angles
                target_angles = {k: np.mean(v) for k, v in by_target.items()}
                sorted_targets = sorted(target_angles.items())
                if len(sorted_targets) > 1:
                    angle_range = max(a for _, a in sorted_targets) - min(a for _, a in sorted_targets)
                    log(f"    L{li:2d}: {len(by_target)} distinct targets, "
                        f"angle range={angle_range:.4f} rad")

    # ══════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════
    elapsed = time.time() - t0

    log(f"\n{'═'*65}")
    log(f"  SUMMARY — Attention Rotation Probe")
    log(f"{'═'*65}")

    # Best rotation layers
    sorted_rotations = sorted(rotation_results.values(), key=lambda r: r["r_squared"], reverse=True)
    log(f"\n  Best rotation layers (by R²):")
    for r in sorted_rotations[:5]:
        log(f"    L{r['layer']:2d} {r['base_day']:>12s}: R²={r['r_squared']:.4f}, "
            f"slope_ratio={r['slope_ratio']:.3f}")

    if rotation_heads:
        log(f"\n  Rotation circuit candidates (L{ablation_layer}):")
        log(f"    Heads: {rotation_heads[:5]}")
        log(f"    (heads whose ablation shifts the day-circle angle most)")

    log(f"\n  Elapsed: {elapsed:.1f}s")
    log(f"{'═'*65}")

    # ── Save results ──
    output = {
        "experiment": "date_attention_probe",
        "session": 128,
        "model": MODEL_NAME,
        "elapsed_s": elapsed,
        "n_probes": len(probes),
        "probe_layers": PROBE_LAYERS,
        "day_attention": {
            str(li): {
                "per_head_day_attn": data["per_head_day_attn"].tolist(),
                "count": data["count"],
            }
            for li, data in day_attn_results.items()
        },
        "rotation_analysis": {
            k: {kk: vv for kk, vv in v.items() if kk != "angles_raw"}
            for k, v in rotation_results.items()
        },
        "ablation": {
            "layer": ablation_layer,
            "text": ablation_text,
            "baseline_angle": baseline_angle if ablation_results else None,
            "results": {
                str(h): r for h, r in ablation_results.items()
            },
            "top_rotation_heads": rotation_heads[:10],
        } if ablation_results else {},
        "circle_basis_info": {
            str(li): {
                "singular_values": data["singular_values"],
                "projections_2d": data["projections_2d"],
            }
            for li, data in circle_basis.items()
        },
    }

    json_path = RESULTS_DIR / "results.json"
    json_path.write_text(json.dumps(output, indent=2, default=str))
    log(f"\n  💾 Results: {json_path}")

    del model, tokenizer
    gc.collect()
    torch.mps.empty_cache()


if __name__ == "__main__":
    main()
