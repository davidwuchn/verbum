#!/usr/bin/env python3
# register: topological/routing (FFN gate) + value/depth (attention o_proj)
"""FFN program-decode along `fired_sequence` — the §7 open experiment (s248).

THE CLAIM (explore/attention-as-beta-reduction.md §7, the stored-program normal form):
the transformer is a bounded soft-β-reduction machine — **FFN = the fixed β-program
(ISA/ROM) that compiles WHICH reduction to do; attention = the one-instruction CPU that
EXECUTES it, advancing reduction DEPTH (WHNF↔D) via softmax-over-V.** The splice program
(s242–s244) read/wrote the program GEOMETRY in place and closed (`fires ∩ spliceable =
∅`); its own notes left one door open: *"a richer multi-position program-decode
read along `fired_sequence`."* This script walks through it.

THE SHARP, FALSIFIABLE PREDICTIONS:
  (A) TRACKING — the FFN routing register (gate_proj, the VALIDATED opcode crystal,
      relational_opcode.py) decodes the combinator the corpus item actually FIRES
      (`lambda_ast.fired_sequence` on the SATURATED corpus, s244) BETTER than the
      attention register (o_proj) does. FFN_acc > Attn_acc, vs a permutation null AND
      the always-most-common-combinator baseline (two-sided, λ measure).
  (B) LEAD-LAG — the FFN opcode-lock LEADS the attention depth-advance by ~1 layer
      (select → execute). Per item: the layer where the FFN gate z locks the dominant
      fired combinator vs the layer where the attention o_proj z(WHNF) peaks.
      Prediction: attention-depth peaks ~1 layer AFTER the FFN opcode (positive lead),
      tested by the per-item peak-difference distribution AND a cross-correlation lag.
  (C) RESCUE — count tokens/items where the attention register OVER-READS (decodes the
      wrong combinator) but the FFN register decodes the RIGHT one. rescue > anti-rescue
      ⇒ "FFN tracks even where attention geometry over-reads."

WHY THIS REGISTER SPLIT (grounded, not arbitrary):
  • FFN gate register = where the combinator crystal is decodable (relational_opcode.py:
    sign(gate)-CMR, the routing register; s203/s231). → WHICH combinator (opcode).
  • attention o_proj register = head-combinator-isa: ALL 9 combinators drive the SAME
    head pattern (r=0.944); attention varies on WHNF↔deeply-nested = reduction DEPTH, a
    program counter NOT an opcode. → decode reduction DEPTH via z(WHNF).
  So (A)/(C) read combinator-identity in both registers (the over-read test); (B) pairs
  the FFN opcode-lock against the attention DEPTH-advance (the executor's job).

METHOD (reuses validated instruments — opcode_monitor_v2 + corpus_firing_survey):
  1. Calibrate TWO RelationalCrystalClassifiers (gate register, attn register), each on
     the crystal-probe centroids with a matched-prefix (gateneutral) null.
  2. Build the FIRING corpus: saturate every quantifier with a fresh witness (s244),
     reduce, keep items whose `fired_sequence != []` (behavioral register). GT per
     item = the fired multiset + dominant fired combinator + reduction length.
  3. For each firing item: ONE forward pass over the gate-prefixed prose, capturing BOTH
     registers at every layer; classify each content token in both registers.
  4. Metrics A/B/C + nulls + a non-firing specificity control.

Usage:
    uv run python scripts/experiments/ffn_program_decode.py --smoke
    uv run python scripts/experiments/ffn_program_decode.py --model Qwen/Qwen3-8B
    uv run python scripts/experiments/ffn_program_decode.py --model Qwen/Qwen3-8B \
        --max-items 120 --zone-lo 0.70 --zone-hi 0.86

License: MIT. AGENTS.md S5 λ provenance (written from this project's instruments).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))

from corpus_firing_survey import _Fresh, saturate  # noqa: E402
from opcode_monitor_v2 import (  # noqa: E402
    COMPILE_GATE,
    _git_sha,
    _hook_module,
    _json_safe,
    _make_hook,
    _transformers_version,
    calibrate_v2,
    gate_prefix_len,
    load_model_and_tokenizer,
)

from verbum.lambda_ast import fired_sequence, parse  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "ffn-program-decode"
CORPUS = {
    "train": _ROOT / "data" / "compile-train.canonical.jsonl",
    "test": _ROOT / "data" / "compile-test.canonical.jsonl",
    "eval": _ROOT / "data" / "compile-eval.canonical.jsonl",
}
FIRING_SET = ["B", "C", "S"]  # the only combinators the corpus ever fires (s244)


# ═══════════════════════════════════════════════════════════════════════════════
# Firing corpus (saturate → fired_sequence ground truth)
# ═══════════════════════════════════════════════════════════════════════════════
def build_firing_corpus() -> tuple[list[dict], list[dict]]:
    """Return (firing_items, nonfiring_items). Each firing item carries the certified
    ground-truth reduction trace from the saturated term."""
    firing: list[dict] = []
    nonfiring: list[dict] = []
    for path in CORPUS.values():
        for line in open(path, encoding="utf-8"):
            r = json.loads(line)
            t = parse(r["kernel_term"])
            seq = fired_sequence(saturate(t, _Fresh()))
            rec = {
                "input": r["input"],
                "category": r["category"],
                "kernel_term": r["kernel_term"],
                "fired_sequence": seq,
            }
            if seq:
                mult = Counter(seq)
                rec["fired_multiset"] = dict(mult)
                rec["dominant_fired"] = mult.most_common(1)[0][0]
                rec["reduction_len"] = len(seq)
                firing.append(rec)
            else:
                nonfiring.append(rec)
    return firing, nonfiring


# ═══════════════════════════════════════════════════════════════════════════════
# Dual-register forward (capture FFN gate + attention o_proj in ONE pass)
# ═══════════════════════════════════════════════════════════════════════════════
def forward_dual(prompt, model, tok, torch_mod, layers):
    """Return (store_gate, store_attn, n_tokens). store_*[li] = [T, d] float64."""
    store_gate: dict[int, np.ndarray] = {}
    store_attn: dict[int, np.ndarray] = {}
    handles = []
    for li in layers:
        handles.append(
            _hook_module(model, li, "gate").register_forward_hook(
                _make_hook(store_gate, li)))
        handles.append(
            _hook_module(model, li, "attn").register_forward_hook(
                _make_hook(store_attn, li)))
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            model(**inputs)
    finally:
        for h in handles:
            h.remove()
    n_tokens = int(inputs["input_ids"].shape[1])
    return store_gate, store_attn, n_tokens


def classify_positions(rcc, store, layers, positions):
    """[positions] → list of per_layer {op: z} dicts (one per content token)."""
    reads = []
    for pos in positions:
        feat = {li: store[li][pos] for li in layers}
        reads.append(rcc.classify(feat).per_layer)
    return reads


# ═══════════════════════════════════════════════════════════════════════════════
# Per-item aggregation
# ═══════════════════════════════════════════════════════════════════════════════
def zone_layers(crystal_layers, n_layers, zone_lo, zone_hi):
    """Crystal-bearing layers whose depth ∈ [zone_lo, zone_hi] (the L26-30 zone,
    expressed as a depth fraction so it transfers across model sizes)."""
    denom = max(n_layers - 1, 1)
    z = [li for li in crystal_layers if zone_lo <= li / denom <= zone_hi]
    return z or crystal_layers  # fall back to all crystal layers if zone empty


def op_layer_profile(reads, layers, op):
    """Mean z(op) per layer across content tokens → {li: mean_z}."""
    prof = {}
    for li in layers:
        vals = [r[li][op] for r in reads if li in r]
        prof[li] = float(np.mean(vals)) if vals else float("nan")
    return prof


def dominant_in_set(reads, layers, op_set):
    """Argmax over op_set of the total positive z summed across (tokens × layers).
    Returns (dominant_op, score_by_op)."""
    score = dict.fromkeys(op_set, 0.0)
    for r in reads:
        for li in layers:
            if li not in r:
                continue
            for op in op_set:
                z = r[li][op]
                if z > 0:
                    score[op] += z
    dom = max(score, key=score.get) if any(v > 0 for v in score.values()) else "·"
    return dom, score


def peak_layer(profile, layers):
    """Layer of max mean-z in `profile` over `layers` (ignoring NaN)."""
    best_li, best_v = None, -np.inf
    for li in layers:
        v = profile.get(li, float("nan"))
        if not np.isnan(v) and v > best_v:
            best_li, best_v = li, v
    return best_li, best_v


def crosscorr_lag(f_ffn, f_attn, layers, max_lag):
    """Lag k∈[-max_lag, max_lag] maximizing corr(f_ffn[L], f_attn[L+k]).
    Positive k ⇒ FFN leads attention. Returns (best_lag, best_corr) or (None, None)."""
    xs = np.array([f_ffn.get(li, np.nan) for li in layers])
    ys = np.array([f_attn.get(li, np.nan) for li in layers])
    best_lag, best_c = None, -np.inf
    for k in range(-max_lag, max_lag + 1):
        if k >= 0:
            a, b = xs[: len(xs) - k], ys[k:]
        else:
            a, b = xs[-k:], ys[: len(ys) + k]
        m = ~(np.isnan(a) | np.isnan(b))
        if m.sum() < 3 or np.nanstd(a[m]) < 1e-9 or np.nanstd(b[m]) < 1e-9:
            continue
        c = float(np.corrcoef(a[m], b[m])[0, 1])
        if c > best_c:
            best_lag, best_c = k, c
    return best_lag, (None if best_c == -np.inf else best_c)


# ═══════════════════════════════════════════════════════════════════════════════
# Stats helpers
# ═══════════════════════════════════════════════════════════════════════════════
def perm_null_accuracy(decoded, truth, n_perm, seed=0):
    """Permutation null for accuracy: shuffle the truth labels against decoded preds.
    Returns (obs_acc, null_mean, p_value)."""
    decoded = np.array(decoded)
    truth = np.array(truth)
    obs = float(np.mean(decoded == truth))
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = np.mean(decoded == rng.permutation(truth))
    p = float((np.sum(null >= obs) + 1) / (n_perm + 1))
    return obs, float(null.mean()), p


def wilcoxon_sign(values):
    """Sign test: frac>0, frac<0, median, two-sided sign-test p (binomial)."""
    v = np.array([x for x in values if x is not None and not np.isnan(x)])
    if v.size == 0:
        return {"n": 0}
    npos = int(np.sum(v > 0))
    nneg = int(np.sum(v < 0))
    nz = npos + nneg
    # two-sided exact binomial sign-test p (k = min(npos,nneg), n = nz, p0=0.5)
    from math import comb

    if nz == 0:
        p = 1.0
    else:
        k = min(npos, nneg)
        tail = sum(comb(nz, i) for i in range(k + 1)) / (2**nz)
        p = float(min(1.0, 2 * tail))
    return {
        "n": int(v.size), "n_pos": npos, "n_neg": nneg, "n_zero": int(np.sum(v == 0)),
        "median": float(np.median(v)), "mean": float(np.mean(v)),
        "frac_positive": float(npos / nz) if nz else 0.0, "sign_test_p": p,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Main experiment
# ═══════════════════════════════════════════════════════════════════════════════
def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
        n_perm_calib, ppc, null_cap, n_perm_stat, n_nonfiring, seed):
    print("═" * 78)
    print("FFN PROGRAM-DECODE ALONG fired_sequence (§7, s248)")
    print("═" * 78)

    firing, nonfiring = build_firing_corpus()
    print(f"[corpus] firing items={len(firing)}  nonfiring={len(nonfiring)}")
    if max_items is not None:
        firing = firing[:max_items]
    rng = np.random.default_rng(seed)
    nf_sample = (list(rng.choice(len(nonfiring), size=min(n_nonfiring, len(nonfiring)),
                                 replace=False))
                 if nonfiring else [])
    nf_items = [nonfiring[i] for i in nf_sample]

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))
    print(f"[model] {model_name}  layers={n_layers}")

    # ── calibrate two registers (matched-prefix null) ───────────────────────────
    print("\n[calib] FFN gate register ...")
    rcc_ffn, calib_ffn = calibrate_v2(
        model, tok, torch_mod, layers, n_perm_calib, ppc, null_cap,
        null_mode="gateneutral", hook="gate")
    print("[calib] attention o_proj register ...")
    rcc_attn, calib_attn = calibrate_v2(
        model, tok, torch_mod, layers, n_perm_calib, ppc, null_cap,
        null_mode="gateneutral", hook="attn")
    cl_ffn = rcc_ffn.crystal_layers
    cl_attn = rcc_attn.crystal_layers
    zl_ffn = zone_layers(cl_ffn, n_layers, zone_lo, zone_hi)
    zl_attn = zone_layers(cl_attn, n_layers, zone_lo, zone_hi)
    print(f"[calib] FFN  crystal layers={len(cl_ffn)} zone={zl_ffn}")
    print(f"[calib] attn crystal layers={len(cl_attn)} zone={zl_attn}")

    gate_n = gate_prefix_len(tok)

    # ── decode every firing item in both registers ──────────────────────────────
    per_item = []
    ffn_pred, attn_pred, truth = [], [], []
    leads_peak, leads_xcorr = [], []
    rescue = anti_rescue = 0
    print(f"\n[decode] {len(firing)} firing items ...")
    for i, item in enumerate(firing):
        if i % 20 == 0:
            print(f"[decode]   item {i}/{len(firing)} ...")
        prompt = COMPILE_GATE + item["input"]
        sg, sa, n = forward_dual(prompt, model, tok, torch_mod, layers)
        positions = list(range(min(gate_n, n - 1), n))
        reads_ffn = classify_positions(rcc_ffn, sg, layers, positions)
        reads_attn = classify_positions(rcc_attn, sa, layers, positions)

        c_true = item["dominant_fired"]
        dom_ffn, score_ffn = dominant_in_set(reads_ffn, zl_ffn, FIRING_SET)
        dom_attn, score_attn = dominant_in_set(reads_attn, zl_attn, FIRING_SET)
        ffn_pred.append(dom_ffn)
        attn_pred.append(dom_attn)
        truth.append(c_true)
        if dom_attn != c_true and dom_ffn == c_true:
            rescue += 1
        if dom_ffn != c_true and dom_attn == c_true:
            anti_rescue += 1

        # (B) lead-lag: FFN opcode-lock(c_true) vs attn depth-advance z(WHNF)
        prof_ffn_op = op_layer_profile(reads_ffn, zl_ffn, c_true)
        prof_attn_whnf = op_layer_profile(reads_attn, zl_attn, "WHNF")
        pk_ffn, _ = peak_layer(prof_ffn_op, zl_ffn)
        pk_attn, _ = peak_layer(prof_attn_whnf, zl_attn)
        lead_peak = (pk_attn - pk_ffn) if (pk_ffn is not None
                                           and pk_attn is not None) else None
        leads_peak.append(lead_peak)
        # cross-corr lag over the SHARED crystal layers in the zone
        shared = sorted(set(zl_ffn) | set(zl_attn))
        prof_ffn_full = op_layer_profile(reads_ffn, shared, c_true)
        prof_attn_full = op_layer_profile(reads_attn, shared, "WHNF")
        lag, lag_c = crosscorr_lag(prof_ffn_full, prof_attn_full, shared, max_lag)
        leads_xcorr.append(lag)

        per_item.append({
            "input": item["input"], "category": item["category"],
            "dominant_fired": c_true, "fired_multiset": item["fired_multiset"],
            "reduction_len": item["reduction_len"],
            "ffn_dominant": dom_ffn, "attn_dominant": dom_attn,
            "ffn_correct": dom_ffn == c_true, "attn_correct": dom_attn == c_true,
            "lead_peak": lead_peak, "lead_xcorr": lag, "xcorr": lag_c,
            "ffn_score": {k: round(v, 3) for k, v in score_ffn.items()},
            "attn_score": {k: round(v, 3) for k, v in score_attn.items()},
        })

    # ── (A) tracking accuracy + nulls ───────────────────────────────────────────
    ffn_acc, ffn_null, ffn_p = perm_null_accuracy(ffn_pred, truth, n_perm_stat, seed)
    attn_acc, attn_null, attn_p = perm_null_accuracy(
        attn_pred, truth, n_perm_stat, seed)
    maj = Counter(truth).most_common(1)[0][0]
    maj_acc = float(np.mean(np.array(truth) == maj))

    # B-vs-S discrimination — the contamination-resistant tracking metric. B and S are
    # the two dominant fired combinators (s244: 55 vs 54 items); C is the common-mode
    # ground state (s211/s240) and swamps the summed-z dominant. Restricting to the B/S
    # contrast removes the C common-mode and asks the sharp question: when the corpus
    # fires B vs S, does the register's z(B)−z(S) sign track it?
    bs_idx = [i for i, c in enumerate(truth) if c in ("B", "S")]
    bs_truth = [truth[i] for i in bs_idx]
    bs_ffn = [("B" if per_item[i]["ffn_score"]["B"] > per_item[i]["ffn_score"]["S"]
               else "S") for i in bs_idx]
    bs_attn = [("B" if per_item[i]["attn_score"]["B"] > per_item[i]["attn_score"]["S"]
                else "S") for i in bs_idx]
    if bs_truth:
        bs_ffn_acc, bs_ffn_null, bs_ffn_p = perm_null_accuracy(
            bs_ffn, bs_truth, n_perm_stat, seed)
        bs_attn_acc, bs_attn_null, bs_attn_p = perm_null_accuracy(
            bs_attn, bs_truth, n_perm_stat, seed)
        bs_maj = Counter(bs_truth).most_common(1)[0][0]
        bs_maj_acc = float(np.mean(np.array(bs_truth) == bs_maj))
    else:
        bs_ffn_acc = bs_ffn_null = bs_ffn_p = 0.0
        bs_attn_acc = bs_attn_null = bs_attn_p = 0.0
        bs_maj, bs_maj_acc = "·", 0.0

    # ── non-firing specificity control (FFN register max z over firing set) ─────
    nf_maxz = []
    for item in nf_items:
        prompt = COMPILE_GATE + item["input"]
        sg, _sa, n = forward_dual(prompt, model, tok, torch_mod, layers)
        positions = list(range(min(gate_n, n - 1), n))
        reads = classify_positions(rcc_ffn, sg, layers, positions)
        _dom, score = dominant_in_set(reads, zl_ffn, FIRING_SET)
        nf_maxz.append(max(score.values()) if score else 0.0)
    fire_maxz = [max(p["ffn_score"].values()) for p in per_item]

    verdict = {
        "model": model_name, "n_layers": n_layers,
        "n_firing_items": len(firing), "n_nonfiring_control": len(nf_items),
        "zone_depth": [zone_lo, zone_hi],
        "ffn_zone_layers": zl_ffn, "attn_zone_layers": zl_attn,
        "ffn_crystal_layers": cl_ffn, "attn_crystal_layers": cl_attn,
        "truth_distribution": dict(Counter(truth)),
        # (A) tracking
        "A_tracking": {
            "ffn_acc": round(ffn_acc, 4), "ffn_null_mean": round(ffn_null, 4),
            "ffn_perm_p": round(ffn_p, 4),
            "attn_acc": round(attn_acc, 4), "attn_null_mean": round(attn_null, 4),
            "attn_perm_p": round(attn_p, 4),
            "majority_baseline_acc": round(maj_acc, 4), "majority_label": maj,
            "ffn_beats_attn": bool(ffn_acc > attn_acc),
            "ffn_beats_majority": bool(ffn_acc > maj_acc),
        },
        # (A') B-vs-S discrimination — the C-common-mode-resistant tracking metric
        "A_bs_discrimination": {
            "n": len(bs_truth), "bs_truth": dict(Counter(bs_truth)),
            "ffn_acc": round(bs_ffn_acc, 4), "ffn_null_mean": round(bs_ffn_null, 4),
            "ffn_perm_p": round(bs_ffn_p, 4),
            "attn_acc": round(bs_attn_acc, 4), "attn_null_mean": round(bs_attn_null, 4),
            "attn_perm_p": round(bs_attn_p, 4),
            "majority_baseline_acc": round(bs_maj_acc, 4), "majority_label": bs_maj,
            "ffn_beats_attn": bool(bs_ffn_acc > bs_attn_acc),
            "ffn_beats_majority": bool(bs_ffn_acc > bs_maj_acc),
        },
        # (B) lead-lag
        "B_lead_lag": {
            "peak_diff": wilcoxon_sign(leads_peak),
            "xcorr_lag": wilcoxon_sign(leads_xcorr),
            "xcorr_lag_hist": dict(Counter(x for x in leads_xcorr if x is not None)),
            "peak_diff_hist": dict(Counter(x for x in leads_peak if x is not None)),
        },
        # (C) rescue
        "C_rescue": {
            "rescue": rescue, "anti_rescue": anti_rescue,
            "rescue_gt_anti": bool(rescue > anti_rescue),
        },
        # specificity control
        "specificity": {
            "firing_mean_maxz_BSC": round(float(np.mean(fire_maxz)), 4) if fire_maxz
            else None,
            "nonfiring_mean_maxz_BSC": round(float(np.mean(nf_maxz)), 4) if nf_maxz
            else None,
        },
        "calib_ffn": calib_ffn, "calib_attn": calib_attn,
    }

    _report(verdict)
    _write(verdict, per_item, model_name, locals())
    return verdict


def _report(v):
    a, b, c = v["A_tracking"], v["B_lead_lag"], v["C_rescue"]
    print("\n" + "═" * 78)
    print("VERDICT")
    print("═" * 78)
    print(f"items={v['n_firing_items']}  truth={v['truth_distribution']}")
    print("\n(A) TRACKING fired_sequence (decode the dominant fired combinator):")
    print(f"  FFN_acc ={a['ffn_acc']}  (null {a['ffn_null_mean']}, "
          f"p={a['ffn_perm_p']})")
    print(f"  Attn_acc={a['attn_acc']}  (null {a['attn_null_mean']}, "
          f"p={a['attn_perm_p']})")
    print(f"  majority-baseline={a['majority_baseline_acc']} ('{a['majority_label']}')")
    print(f"  ⇒ FFN beats attn: {a['ffn_beats_attn']}  | FFN beats majority: "
          f"{a['ffn_beats_majority']}")
    bs = v["A_bs_discrimination"]
    print(f"\n(A') B-vs-S discrimination (C-common-mode-resistant; n={bs['n']} "
          f"{bs['bs_truth']}):")
    print(f"  FFN_acc ={bs['ffn_acc']}  (null {bs['ffn_null_mean']}, "
          f"p={bs['ffn_perm_p']})")
    print(f"  Attn_acc={bs['attn_acc']}  (null {bs['attn_null_mean']}, "
          f"p={bs['attn_perm_p']})")
    print(f"  majority-baseline={bs['majority_baseline_acc']} "
          f"⇒ FFN beats attn: {bs['ffn_beats_attn']} | beats majority: "
          f"{bs['ffn_beats_majority']}")
    print("\n(B) LEAD-LAG (FFN opcode-lock vs attention WHNF depth-advance):")
    pk, xc = b["peak_diff"], b["xcorr_lag"]
    print(f"  peak-diff: median={pk.get('median')} frac+={pk.get('frac_positive')} "
          f"n={pk.get('n')} sign-p={pk.get('sign_test_p')}  hist={b['peak_diff_hist']}")
    print(f"  xcorr-lag: median={xc.get('median')} frac+={xc.get('frac_positive')} "
          f"n={xc.get('n')} sign-p={xc.get('sign_test_p')}  hist={b['xcorr_lag_hist']}")
    print("  (positive ⇒ FFN leads attention; prediction ≈ +1)")
    print(f"\n(C) RESCUE: rescue={c['rescue']} anti-rescue={c['anti_rescue']} "
          f"⇒ {c['rescue_gt_anti']}")
    s = v["specificity"]
    print(f"\nspecificity: firing max-z(BSC)={s['firing_mean_maxz_BSC']} "
          f"vs nonfiring={s['nonfiring_mean_maxz_BSC']}")
    print("═" * 78)


def _write(verdict, per_item, model_name, ns):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    (RESULTS_DIR / f"verdict_{slug}.json").write_text(
        json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
    (RESULTS_DIR / f"per_item_{slug}.json").write_text(
        json.dumps(_json_safe(per_item), indent=2, ensure_ascii=False),
        encoding="utf-8")
    meta = {
        "model": model_name, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "corpus": {k: str(p.relative_to(_ROOT)) for k, p in CORPUS.items()},
        "params": {k: ns[k] for k in (
            "max_items", "zone_lo", "zone_hi", "onset_tau", "max_lag",
            "n_perm_calib", "ppc", "null_cap", "n_perm_stat", "n_nonfiring", "seed")},
        "method": "saturate quantifiers → fired_sequence ground truth; dual-register "
                  "decode (gate=opcode, attn o_proj=WHNF depth); A track + B lead-lag "
                  "+ C rescue, matched-prefix null calibration.",
    }
    (RESULTS_DIR / f"meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"\n[write] {RESULTS_DIR}/verdict_{slug}.json (+ per_item, meta)")


def main():
    ap = argparse.ArgumentParser(description="FFN program-decode along fired_sequence")
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    ap.add_argument("--max-items", type=int, default=None)
    ap.add_argument("--zone-lo", type=float, default=0.70,
                    help="readable-zone depth fraction lo (L26/36≈0.72 for 8B)")
    ap.add_argument("--zone-hi", type=float, default=0.86,
                    help="readable-zone depth fraction hi (L30/36≈0.83 for 8B)")
    ap.add_argument("--onset-tau", type=float, default=2.0)
    ap.add_argument("--max-lag", type=int, default=4)
    ap.add_argument("--n-perm-stat", type=int, default=2000)
    ap.add_argument("--n-nonfiring", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true",
                    help="Qwen3-0.6B, few probes/items, fast wiring check")
    args = ap.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-8B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm_calib, ppc, null_cap, max_items, n_nonfiring = 80, 4, 200, 12, 6
        print("[smoke] mode")
    else:
        n_perm_calib, ppc, null_cap = 300, None, None
        max_items, n_nonfiring = args.max_items, args.n_nonfiring

    run(model_name, max_items, args.zone_lo, args.zone_hi, args.onset_tau,
        args.max_lag, n_perm_calib, ppc, null_cap, args.n_perm_stat,
        n_nonfiring, args.seed)


if __name__ == "__main__":
    main()
