"""C Rotation Probe — Is C a Q rotation + delta?

Hypothesis: Each combinator is a geometric operation (rotation + displacement)
in representation space, not a symbolic rewriting rule. C is the ground state
rotation. The other combinators are angular offsets from C.

Measurement protocol:
  For each combinator C_type ∈ {K, I, B, C}:
    For each probe (reduction example):
      Run through teacher model, capture hidden state at each layer boundary
      h_before[L] = hidden state entering layer L
      h_after[L]  = hidden state leaving layer L

      Total rotation:     θ_total[L] = arccos(cos(h_before, h_after))
      Attention rotation: θ_attn[L]  = arccos(cos(h_before, h_mid))
        where h_mid = h_before + attn(norm(h_before))
      FFN displacement:   θ_ffn[L]   = arccos(cos(h_mid, h_after))

  Then compare:
    - Per-combinator rotation profiles across depth
    - Cross-combinator angle differences (is C the base?)
    - Match rotation angles to CCA harmonic peaks (25°, 45°, 53°, 61°, 67°, 77°)

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/c_rotation_probe_exp.py 2>&1 | tee results/c-rotation-probe/run.log

License: MIT
"""

from __future__ import annotations

import json, sys, time, gc
from pathlib import Path
import numpy as np
import mlx.core as mx
import mlx.nn as nn

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, PAD_ID, EQ_ID, TOK2ID,
    Comb, Var, App,
    GDModel,
    masked_ce_loss, eval_model,
    generate_batch,
)
import mlx.optimizers as optim


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "c-rotation-probe"
D_MODEL = 256; N_LAYERS = 3
BATCH_SIZE = 32; LR = 0.003; MAX_DEPTH = 4
COMBINATORS = ["K", "I", "B", "C"]


# ══════════════════════════════════════════════════════════════════════
# Probe generation — diverse examples per combinator
# ══════════════════════════════════════════════════════════════════════

def gen_probes(n=50, seed=42):
    """Generate diverse reduction probes per combinator."""
    rng = np.random.RandomState(seed)
    vs = ["a", "b", "c", "d", "e", "x", "y", "z"]
    fs = ["f", "g", "h", "p", "q"]
    probes = {}

    for c in COMBINATORS:
        ps = []
        for _ in range(n * 5):
            if len(ps) >= n:
                break
            v1, v2 = Var(rng.choice(vs)), Var(rng.choice(vs))
            f1, f2 = Var(rng.choice(fs)), Var(rng.choice(fs))
            if c == "K":
                e = App(App(Comb("K"), v1), v2)
            elif c == "I":
                e = App(Comb("I"), v1)
            elif c == "B":
                e = App(App(App(Comb("B"), f1), f2), v1)
            elif c == "C":
                e = App(App(App(Comb("C"), f1), v1), v2)
            t = ["<bos>"] + e.to_tokens() + ["="]
            if not all(x in TOK2ID for x in t):
                continue
            ids = [TOK2ID[x] for x in t]
            ids = ids[:20] + [PAD_ID] * max(0, 20 - len(ids))
            ps.append({"ids": ids, "combinator": c, "expr": str(e)})
        probes[c] = ps[:n]

    return probes


# ══════════════════════════════════════════════════════════════════════
# Rotation measurement
# ══════════════════════════════════════════════════════════════════════

def cosine_angle(a, b):
    """Angle in degrees between two vectors."""
    a_np = np.array(a).flatten().astype(np.float64)
    b_np = np.array(b).flatten().astype(np.float64)
    na = np.linalg.norm(a_np)
    nb = np.linalg.norm(b_np)
    if na < 1e-10 or nb < 1e-10:
        return 90.0
    cos = np.clip(np.dot(a_np, b_np) / (na * nb), -1, 1)
    return float(np.degrees(np.arccos(cos)))


def magnitude_ratio(a, b):
    """Ratio of magnitudes |b| / |a|."""
    na = np.linalg.norm(np.array(a).flatten())
    nb = np.linalg.norm(np.array(b).flatten())
    if na < 1e-10:
        return 0.0
    return float(nb / na)


def measure_layer_rotation(model, input_ids, target_pos=-1):
    """Run one probe, capture per-layer rotation decomposition.

    For each layer L:
      h_before = input to layer (residual stream before)
      h_mid    = after attention only (residual + attn)
      h_after  = after attention + FFN (residual + attn + ffn)

    Returns per-layer dict with:
      - total_angle: angle between h_before and h_after
      - attn_angle:  angle between h_before and h_mid (attention rotation)
      - ffn_angle:   angle between h_mid and h_after (FFN displacement)
      - attn_magnitude: |attn_contribution| / |h_before|
      - ffn_magnitude:  |ffn_contribution| / |h_mid|
      - total_magnitude: |h_after| / |h_before|
    """
    x = model.embed(mx.array(np.array([input_ids], dtype=np.int32)))
    mx.eval(x)

    layer_data = []
    for li, layer in enumerate(model.layers):
        h_before = np.array(x[0, target_pos, :]).copy()

        # Attention step: x + attn(norm(x))
        attn_input = layer.attn_norm(x)
        attn_out = layer.attn(attn_input)
        h_mid_full = x + attn_out
        mx.eval(h_mid_full)
        h_mid = np.array(h_mid_full[0, target_pos, :]).copy()

        # FFN step: h_mid + ffn(norm(h_mid))
        ffn_input = layer.ffn_norm(h_mid_full)
        ffn_out = layer.ffn(ffn_input)
        h_after_full = h_mid_full + ffn_out
        mx.eval(h_after_full)
        h_after = np.array(h_after_full[0, target_pos, :]).copy()

        # Decompose
        attn_contrib = h_mid - h_before
        ffn_contrib = h_after - h_mid

        layer_data.append({
            "total_angle": cosine_angle(h_before, h_after),
            "attn_angle": cosine_angle(h_before, h_mid),
            "ffn_angle": cosine_angle(h_mid, h_after),
            "attn_magnitude": float(np.linalg.norm(attn_contrib) /
                                    max(np.linalg.norm(h_before), 1e-10)),
            "ffn_magnitude": float(np.linalg.norm(ffn_contrib) /
                                   max(np.linalg.norm(h_mid), 1e-10)),
            "total_magnitude": magnitude_ratio(h_before, h_after),
            # Raw vectors for cross-combinator comparison
            "h_before": h_before,
            "h_after": h_after,
            "attn_contrib": attn_contrib,
            "ffn_contrib": ffn_contrib,
        })

        x = h_after_full

    return layer_data


def measure_combinator_rotations(model, probes):
    """Measure rotation angles for all probes, aggregate per combinator."""
    results = {}

    for comb_name in COMBINATORS:
        comb_probes = probes[comb_name]
        all_layers = [[] for _ in range(N_LAYERS)]

        for probe in comb_probes:
            layer_data = measure_layer_rotation(model, probe["ids"])
            for li, ld in enumerate(layer_data):
                all_layers[li].append(ld)

        # Aggregate per layer
        layer_stats = []
        for li in range(N_LAYERS):
            lds = all_layers[li]
            stats = {}
            for key in ["total_angle", "attn_angle", "ffn_angle",
                        "attn_magnitude", "ffn_magnitude", "total_magnitude"]:
                vals = [ld[key] for ld in lds]
                stats[key] = {
                    "mean": float(np.mean(vals)),
                    "std": float(np.std(vals)),
                    "min": float(np.min(vals)),
                    "max": float(np.max(vals)),
                }
            # Mean direction vectors for cross-combinator comparison
            stats["mean_attn_dir"] = np.mean([ld["attn_contrib"] for ld in lds], axis=0)
            stats["mean_ffn_dir"] = np.mean([ld["ffn_contrib"] for ld in lds], axis=0)
            stats["mean_h_before"] = np.mean([ld["h_before"] for ld in lds], axis=0)
            stats["mean_h_after"] = np.mean([ld["h_after"] for ld in lds], axis=0)
            layer_stats.append(stats)

        results[comb_name] = layer_stats

    return results


def cross_combinator_analysis(rotation_data):
    """Compare rotation directions across combinators.

    For each layer, compute:
    - Pairwise angles between combinator attention directions
    - Pairwise angles between combinator FFN directions
    - Is C the "center" (smallest mean angle to all others)?
    """
    cross = {}

    for li in range(N_LAYERS):
        layer_cross = {}

        # Pairwise attention direction angles
        attn_angles = {}
        ffn_angles = {}
        for i, c1 in enumerate(COMBINATORS):
            for j, c2 in enumerate(COMBINATORS):
                if j <= i:
                    continue
                d1_attn = rotation_data[c1][li]["mean_attn_dir"]
                d2_attn = rotation_data[c2][li]["mean_attn_dir"]
                d1_ffn = rotation_data[c1][li]["mean_ffn_dir"]
                d2_ffn = rotation_data[c2][li]["mean_ffn_dir"]

                attn_angles[f"{c1}↔{c2}"] = cosine_angle(d1_attn, d2_attn)
                ffn_angles[f"{c1}↔{c2}"] = cosine_angle(d1_ffn, d2_ffn)

        # C-centrality: mean angle from C to all others
        c_attn_angles = [v for k, v in attn_angles.items() if "C" in k]
        c_ffn_angles = [v for k, v in ffn_angles.items() if "C" in k]

        k_attn_angles = [v for k, v in attn_angles.items() if "K" in k]
        b_attn_angles = [v for k, v in attn_angles.items() if "B" in k]
        i_attn_angles = [v for k, v in attn_angles.items() if "I" in k]

        layer_cross["attn_pairwise"] = attn_angles
        layer_cross["ffn_pairwise"] = ffn_angles
        layer_cross["c_attn_centrality"] = float(np.mean(c_attn_angles)) if c_attn_angles else 0
        layer_cross["k_attn_centrality"] = float(np.mean(k_attn_angles)) if k_attn_angles else 0
        layer_cross["b_attn_centrality"] = float(np.mean(b_attn_angles)) if b_attn_angles else 0
        layer_cross["i_attn_centrality"] = float(np.mean(i_attn_angles)) if i_attn_angles else 0

        cross[f"layer_{li}"] = layer_cross

    return cross


# ══════════════════════════════════════════════════════════════════════
# CCA comparison
# ══════════════════════════════════════════════════════════════════════

def compute_cca_peaks(model):
    """Compute CCA angles between W_q and W_up for each layer."""
    peaks = []
    for layer in model.layers:
        Wk = np.array(layer.attn.k_proj.weight)
        Wf = np.array(layer.ffn.weight)
        _, _, Va = np.linalg.svd(Wk, full_matrices=False)
        _, _, Vb = np.linalg.svd(Wf, full_matrices=False)
        k = min(128, Va.shape[0], Vb.shape[0])
        A, B = Va[:k, :].T, Vb[:k, :].T
        Qa, _ = np.linalg.qr(A)
        Qb, _ = np.linalg.qr(B)
        _, S, _ = np.linalg.svd(Qa.T @ Qb, full_matrices=False)
        angles = np.degrees(np.arccos(np.clip(S, 0, 1)))
        peaks.append({
            "mean": float(angles.mean()),
            "median": float(np.median(angles)),
            "min": float(angles.min()),
            "max": float(angles.max()),
            "peaks": [float(a) for a in angles[:10]],  # top 10 CCA angles
        })
    return peaks


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    # Train teacher
    log(f"{'═'*60}")
    log(f"Training teacher d={D_MODEL}...")
    teacher = GDModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(teacher.parameters())
    opt = optim.Adam(learning_rate=LR)
    lag = nn.value_and_grad(teacher, masked_ce_loss)
    rng = np.random.RandomState(42)
    for s in range(5000):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(teacher, ids, tgt, msk); mx.eval(lv, gr)
        teacher.update(opt.apply_gradients(gr, teacher))
        mx.eval(teacher.parameters()); del lv, gr
        if (s + 1) % 100 == 0: mx.clear_cache()
        if (s + 1) % 1000 == 0:
            ev = eval_model(teacher, np.random.RandomState(999), max_depth=MAX_DEPTH)
            log(f"    Step {s+1}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")

    teacher_ev = eval_model(teacher, np.random.RandomState(999), max_depth=MAX_DEPTH)
    log(f"  Final: loss={teacher_ev['loss']:.4f}, acc={teacher_ev['accuracy']:.4f}")

    # Generate probes
    probes = gen_probes(n=50)
    for c in COMBINATORS:
        log(f"  {c}: {len(probes[c])} probes")

    # ══════════════════════════════════════════════════════════════
    # Measure per-combinator rotation angles
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("Measuring per-combinator rotation angles...")

    rotation_data = measure_combinator_rotations(teacher, probes)

    # Print rotation profiles
    log(f"\n  Per-combinator rotation angles (degrees):")
    log(f"  {'Comb':>4s}  {'Layer':>5s}  {'Total':>8s}  {'Attn':>8s}  {'FFN':>8s}  "
        f"{'|Attn|':>8s}  {'|FFN|':>8s}")
    log(f"  {'─'*4}  {'─'*5}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}")

    for c in COMBINATORS:
        for li in range(N_LAYERS):
            s = rotation_data[c][li]
            log(f"  {c:>4s}  L{li:>4d}  "
                f"{s['total_angle']['mean']:8.2f}  "
                f"{s['attn_angle']['mean']:8.2f}  "
                f"{s['ffn_angle']['mean']:8.2f}  "
                f"{s['attn_magnitude']['mean']:8.3f}  "
                f"{s['ffn_magnitude']['mean']:8.3f}")
        log("")

    # ══════════════════════════════════════════════════════════════
    # Cross-combinator direction comparison
    # ══════════════════════════════════════════════════════════════
    log(f"{'═'*60}")
    log("Cross-combinator direction analysis...")

    cross = cross_combinator_analysis(rotation_data)

    for li in range(N_LAYERS):
        lc = cross[f"layer_{li}"]
        log(f"\n  Layer {li} — attention direction pairwise angles:")
        for pair, angle in sorted(lc["attn_pairwise"].items()):
            bar = "█" * max(0, int(angle / 5))
            log(f"    {pair:>6s}: {angle:6.1f}° {bar}")

        log(f"\n  Layer {li} — FFN direction pairwise angles:")
        for pair, angle in sorted(lc["ffn_pairwise"].items()):
            bar = "█" * max(0, int(angle / 5))
            log(f"    {pair:>6s}: {angle:6.1f}° {bar}")

        log(f"\n  Centrality (mean angle to all others — lower = more central):")
        log(f"    C: {lc['c_attn_centrality']:5.1f}°  "
            f"K: {lc['k_attn_centrality']:5.1f}°  "
            f"B: {lc['b_attn_centrality']:5.1f}°  "
            f"I: {lc['i_attn_centrality']:5.1f}°")

        most_central = min(
            [(lc['c_attn_centrality'], 'C'),
             (lc['k_attn_centrality'], 'K'),
             (lc['b_attn_centrality'], 'B'),
             (lc['i_attn_centrality'], 'I')]
        )
        log(f"    Most central: {most_central[1]} ({most_central[0]:.1f}°) "
            f"{'← C IS the center!' if most_central[1] == 'C' else ''}")

    # ══════════════════════════════════════════════════════════════
    # CCA peak comparison
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("CCA angle peaks (Q↔FFN crossing angles)...")

    cca_peaks = compute_cca_peaks(teacher)
    for li, peaks in enumerate(cca_peaks):
        log(f"  Layer {li}: mean={peaks['mean']:.1f}° median={peaks['median']:.1f}° "
            f"range=[{peaks['min']:.1f}°, {peaks['max']:.1f}°]")
        log(f"    Top CCA angles: {', '.join(f'{a:.1f}°' for a in peaks['peaks'][:6])}")

    # Compare combinator rotation angles to CCA peaks
    log(f"\n  Combinator rotation angles vs CCA peaks:")
    for c in COMBINATORS:
        for li in range(N_LAYERS):
            total = rotation_data[c][li]["total_angle"]["mean"]
            attn = rotation_data[c][li]["attn_angle"]["mean"]
            cca_mean = cca_peaks[li]["mean"]
            log(f"    {c} L{li}: total={total:.1f}° attn={attn:.1f}° "
                f"CCA_mean={cca_mean:.1f}° "
                f"Δ(attn-CCA)={abs(attn - cca_mean):.1f}°")

    # ══════════════════════════════════════════════════════════════
    # Key questions
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("KEY FINDINGS:")

    # Is C the most central combinator?
    c_central_count = 0
    for li in range(N_LAYERS):
        lc = cross[f"layer_{li}"]
        centralities = {
            "C": lc["c_attn_centrality"],
            "K": lc["k_attn_centrality"],
            "B": lc["b_attn_centrality"],
            "I": lc["i_attn_centrality"],
        }
        if min(centralities, key=centralities.get) == "C":
            c_central_count += 1
    log(f"  C is most central combinator in {c_central_count}/{N_LAYERS} layers "
        f"{'✓ C IS THE CENTER' if c_central_count > N_LAYERS // 2 else '✗ C is NOT the center'}")

    # Do combinators have distinct rotation angles?
    for li in range(N_LAYERS):
        angles = {c: rotation_data[c][li]["total_angle"]["mean"] for c in COMBINATORS}
        spread = max(angles.values()) - min(angles.values())
        log(f"  L{li} rotation spread: {spread:.1f}° "
            f"(K={angles['K']:.1f}° I={angles['I']:.1f}° "
            f"B={angles['B']:.1f}° C={angles['C']:.1f}°)"
            f" {'← distinct' if spread > 5 else '← similar'}")

    # Is attention rotation or FFN displacement dominant?
    for li in range(N_LAYERS):
        attn_mean = np.mean([rotation_data[c][li]["attn_angle"]["mean"] for c in COMBINATORS])
        ffn_mean = np.mean([rotation_data[c][li]["ffn_angle"]["mean"] for c in COMBINATORS])
        log(f"  L{li}: attn={attn_mean:.1f}° vs ffn={ffn_mean:.1f}° "
            f"{'← attn dominates' if attn_mean > ffn_mean else '← FFN dominates'}")

    # Save results (strip numpy arrays for JSON)
    save_results = {
        "teacher": {"accuracy": teacher_ev["accuracy"], "loss": teacher_ev["loss"]},
        "cca_peaks": cca_peaks,
        "cross_combinator": {},
    }

    for c in COMBINATORS:
        save_results[f"rotation_{c}"] = []
        for li in range(N_LAYERS):
            s = rotation_data[c][li]
            save_results[f"rotation_{c}"].append({
                k: v for k, v in s.items()
                if k not in ["mean_attn_dir", "mean_ffn_dir",
                             "mean_h_before", "mean_h_after"]
            })

    for li in range(N_LAYERS):
        lc = cross[f"layer_{li}"]
        save_results["cross_combinator"][f"layer_{li}"] = {
            k: v for k, v in lc.items()
        }

    elapsed = time.time() - t_start
    save_results["meta"] = {"elapsed_seconds": elapsed}

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(save_results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"Results saved to {out_path} ({elapsed:.0f}s)")


if __name__ == "__main__":
    main()
