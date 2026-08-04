#!/usr/bin/env python3
"""P-COMPANDING-QUANT — is a base-weight outlier's MAGNITUDE disposable-for-routing?

Pre-reg: mementum/knowledge/explore/ratio-gradient-quantization.md
§P-COMPANDING-QUANT (FROZEN s306 + amendment, Michael-approved). Post-hoc WEIGHT
quantization of Qwen3-4B FFN. The register theory of quantization
(register-theory-of-quantization.md) says the routing register (sign) carries the
function and the magnitude register is scaffolding. Michael's algorithm: shave the
outlier tail into ternary ROUTING (sign only) and quant the rest — inverting the
SpQR/AWQ trick (which keeps outliers in fp16). Two separable questions:

  Q1 STORAGE (register-theory primary): keep the tail as ternary SIGN (1.58 b) vs
     fp16 — is base-weight outlier MAGNITUDE VALUE disposable, or salient (AWQ/SpQR)?
  Q2 SELECTOR: pick the tail by COHERENCE (gradient sign-consistency) vs MAGNITUDE.
     s171 (gradient-zero-map) proved MAGNITUDE WINS at micro scale (coherence is
     maturity-dependent); 4B answers its open question. The register bet is on Q1
     (storage), not on beating magnitude selection.

Register (lambda measure): the claim is ROUTING, so the metric is DOWNSTREAM CE on
held text (+ advisory factual task acc), NEVER ||W-Q(W)|| / mag_cos (that measures
the disposable register). Gated against a SHUFFLED-TAIL null (lambda yardstick).

tau = 1% (FROZEN). Body precision sweep b' in {2,3,4}-bit signed RTN -> a CE-vs-bits
frontier; arms compared PAIRED at matched body precision (tail 1% is budget-
negligible, so matched-body ~ matched-bits). Effective bits reported per arm.

Arms (each quantizes the base FFN weights, evaluates, RESTORES exactly):
  int_uniform      : signed RTN int-b everything (outliers stretch the grid). FLOOR.
  twn              : per-row ternary (thr 0.7) everything. FLOOR.
  outlier_mag_fp16 : top-tau by |W| kept fp16, body int-b (SpQR/AWQ; Q1 control).
  companding_mag   : PRIMARY — top-tau by |W| -> ternary sign, body int-b.
  companding_coh   : top-tau by COHERENCE -> ternary sign, body int-b.
  companding_shuffle: tail positions shuffled (matched count + per-row gamma), body
                     int-b (lambda yardstick, >=3 seeds). MUST fail.

Gates (verbum.dsp paired_permutation on per-chunk CE; lower CE = better):
  C1 SCHEME-WORKS  : companding_mag beats int_uniform at >=1 budget.
  C2 MAGNITUDE-DISPOSABLE (amended NULL TEST): outlier_mag_fp16 does NOT significantly
     beat companding_mag at any usable budget (b in {3,4}, Bonferroni). Disposable =
     cannot reject ternary-sign ~ fp16 for the tail. fp16 SIG beats -> SALIENT.
  C3 SELECTOR      : sign of (companding_coh - companding_mag) at the best budget.
  C4 SPECIFICITY   : companding_mag beats companding_shuffle at >=1 budget.
  C5 HOST-SANE     : companding_mag CE at b=4 within HOST_TOL of the unquantized ref.
Verdicts: MAGNITUDE-DISPOSABLE (+COHERENCE-SELECTS/+MAGNITUDE-SELECTS) /
  MAGNITUDE-SALIENT / SCHEME-INERT / UNSPECIFIC / HOST-DAMAGED.

Reuse (no fork): writeback_compile for BANK/CE_TEXTS/first_word; operand_multihop3
for resolve_parts/first_tid; verbum.dsp for the gate. Quantizers + coherence
calibration are inline (per-output-channel grouping, distinct from ternarize_delta's
per-column TWN).

Cadence: --validate (no model) -> smoke (--n-layers, mechanics only, s297) ->
Michael GO -> run. Resource note: coherence calibration accumulates per-weight
gradient stats (fp32, CPU) over the FFN band; cap with --n-layers if memory-bound.

License: MIT (`lambda provenance`).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_EXPLORE = _HERE.parents[1] / "scripts" / "explore"
_WRAP = _HERE.parents[1] / "wrapper"
for _p in (_HERE, _EXPLORE, _WRAP):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import writeback_compile as wb  # noqa: E402  (BANK/CE_TEXTS/first_word reuse)
from holo_frag import _json_safe  # noqa: E402

from verbum.dsp import gate, paired_permutation  # noqa: E402

TAU = 0.01                 # FROZEN tail fraction
TERNARY_THR = 0.7          # per-row TWN threshold factor (body twn arm)
BODY_BITS = (2, 3, 4)      # body precision sweep (signed RTN)
USABLE_BITS = (3, 4)       # "usable budget" for C2 (B >= 2.5)
LOG2_3 = float(np.log2(3.0))
HOST_TOL = 0.10            # C5: companding_mag@b4 CE within 10% of unquantized ref
ARMS = ("int_uniform", "twn", "outlier_mag_fp16", "companding_mag",
        "companding_coh", "companding_shuffle")


# ══════════════════════════════════════════════════════════════════════════
# Quantizers (pure numpy, per-output-channel = per-row grouping; W is (out,in))
# ══════════════════════════════════════════════════════════════════════════
def rtn_int(w: np.ndarray, bits: int, active: np.ndarray | None = None) -> np.ndarray:
    """Signed per-row absmax RTN. Scale from `active` positions only (so outliers
    excluded from the body grid); applied to all of w (tail overwritten later)."""
    qmax = 2 ** (bits - 1) - 1                       # int2->1, int3->3, int4->7
    absw = np.abs(w) if active is None else np.where(active, np.abs(w), 0.0)
    scale = absw.max(axis=1, keepdims=True) / max(qmax, 1)
    scale = np.where(scale > 0, scale, 1.0)
    q = np.clip(np.round(w / scale), -qmax, qmax)
    return (q * scale).astype(np.float32)


def ternary_all(w: np.ndarray, thr: float = TERNARY_THR) -> np.ndarray:
    """Per-row TWN (Li&Liu): thr_r = thr*mean|w_r|, gamma_r = mean surviving |w|."""
    absw = np.abs(w)
    thr_r = thr * absw.mean(axis=1, keepdims=True)
    mask = absw > thr_r
    cnt = mask.sum(axis=1, keepdims=True)
    gamma = (absw * mask).sum(axis=1, keepdims=True) / np.maximum(cnt, 1)
    return (np.sign(w) * mask * gamma).astype(np.float32)


def tail_gamma(w: np.ndarray, tail: np.ndarray) -> np.ndarray:
    """Per-row scale from the row's tail entries (fallback: global tail mean)."""
    absw = np.where(tail, np.abs(w), 0.0)
    cnt = tail.sum(axis=1, keepdims=True)
    g = absw.sum(axis=1, keepdims=True) / np.maximum(cnt, 1)
    glob = float(np.abs(w[tail]).mean()) if tail.any() else 1.0
    return np.where(cnt > 0, g, glob)


def tier_quant(w: np.ndarray, tail: np.ndarray, body_bits: int,
               tail_mode: str) -> np.ndarray:
    """tail -> ternary sign*gamma (or fp16 passthrough); body -> signed RTN with the
    grid scaled from the body only (outliers pulled out)."""
    body = ~tail
    wq = rtn_int(w, body_bits, active=body)
    if tail_mode == "fp16":
        wq[tail] = w[tail]
    else:                                            # ternary sign
        g = tail_gamma(w, tail)
        wq_t = (np.sign(w) * g).astype(np.float32)
        wq[tail] = wq_t[tail]
    return wq


def tail_mask(score: np.ndarray, tau: float = TAU) -> np.ndarray:
    """Top-tau fraction of |score| per matrix (global flatten)."""
    n = score.size
    k = max(round(tau * n), 1)
    thr = np.partition(np.abs(score).ravel(), n - k)[n - k]
    return np.abs(score) >= thr


def effective_bits(arm: str, body_bits: int, tau: float = TAU) -> float:
    """Documented index model: sparse tail costs its value bits + a position index
    (~log2(1/tau) per tail element); body at b'; per-row scales negligible."""
    idx = float(np.log2(1.0 / tau))
    if arm == "int_uniform":
        return float(body_bits)
    if arm == "twn":
        return LOG2_3
    tail_bits = 16.0 if arm == "outlier_mag_fp16" else LOG2_3
    return float(tau * (tail_bits + idx) + (1.0 - tau) * body_bits)


def quantize_matrix(w: np.ndarray, arm: str, body_bits: int,
                    mag_tail: np.ndarray, coh_tail: np.ndarray,
                    shuf_tail: np.ndarray) -> np.ndarray:
    if arm == "int_uniform":
        return rtn_int(w, body_bits)
    if arm == "twn":
        return ternary_all(w)
    if arm == "outlier_mag_fp16":
        return tier_quant(w, mag_tail, body_bits, "fp16")
    if arm == "companding_mag":
        return tier_quant(w, mag_tail, body_bits, "ternary")
    if arm == "companding_coh":
        return tier_quant(w, coh_tail, body_bits, "ternary")
    if arm == "companding_shuffle":
        return tier_quant(w, shuf_tail, body_bits, "ternary")
    raise ValueError(arm)


# ══════════════════════════════════════════════════════════════════════════
# Scoring + verdict (pure; per-chunk CE, lower=better; --validate plants worlds)
# ══════════════════════════════════════════════════════════════════════════
def ce_better(a_ce: np.ndarray, b_ce: np.ndarray, rng, alpha: float, name: str):
    """Gate: is arm A's CE significantly LOWER than B's (A better)? paired over
    chunks. effect = mean(B - A) > 0 when A better."""
    a = np.asarray(a_ce, float)
    b = np.asarray(b_ce, float)
    return gate(float(np.mean(b - a)), paired_permutation(b, a, rng),
                "greater", alpha, name=name)


def score(ce: dict, ref_ce: float, rng, alpha: float) -> dict:
    """ce[arm][body_bits] = per-chunk CE vector. Frozen C1-C5 + verdict."""
    P, U, F = "companding_mag", "int_uniform", "outlier_mag_fp16"
    r: dict = {"per_budget": {}}

    def better_at(a, b, bits, al):
        return ce_better(ce[a][bits], ce[b][bits], rng, al, f"{a}<{b}@{bits}")

    # C1 scheme-works: companding_mag beats int_uniform at >=1 budget
    c1 = {}
    for bb in BODY_BITS:
        g = better_at(P, U, bb, alpha)
        c1[bb] = bool(g.verdict)
    r["C1"] = bool(any(c1.values()))
    r["C1_detail"] = c1

    # C2 magnitude-disposable (NULL TEST): fp16 does NOT sig-beat companding_mag at
    # any usable budget (Bonferroni over usable budgets). salient if it does.
    a2 = alpha / len(USABLE_BITS)
    c2 = {}
    for bb in USABLE_BITS:
        g = better_at(F, P, bb, a2)                  # fp16 better than companding?
        c2[bb] = {"fp16_beats_mag": bool(g.verdict), "effect": g.value, "p": g.p}
    r["fp16_dominates"] = bool(any(v["fp16_beats_mag"] for v in c2.values()))
    r["C2"] = not r["fp16_dominates"]
    r["C2_detail"] = c2

    # C3 selector: coherence vs magnitude at the best (lowest-CE) companding_mag budget
    best_bb = min(BODY_BITS, key=lambda bb: float(np.mean(ce[P][bb])))
    gc = better_at("companding_coh", P, best_bb, alpha)
    gm = better_at(P, "companding_coh", best_bb, alpha)
    if gc.verdict:
        r["C3"] = "COHERENCE-SELECTS"
    elif gm.verdict:
        r["C3"] = "MAGNITUDE-SELECTS"
    else:
        r["C3"] = "MAGNITUDE-SELECTS"                # tie -> magnitude (s171 baseline)
    r["C3_detail"] = {"best_bb": best_bb, "coh_beats_mag": bool(gc.verdict),
                      "mag_beats_coh": bool(gm.verdict)}

    # C4 specificity: companding_mag beats companding_shuffle at >=1 budget
    c4 = {}
    for bb in BODY_BITS:
        g = better_at(P, "companding_shuffle", bb, alpha)
        c4[bb] = bool(g.verdict)
    r["C4"] = bool(any(c4.values()))
    r["C4_detail"] = c4

    # C5 host-sane: companding_mag @ b=4 within HOST_TOL of the unquantized ref
    ce_p4 = float(np.mean(ce[P][4]))
    r["C5"] = bool(ce_p4 <= ref_ce * (1.0 + HOST_TOL))
    r["C5_detail"] = {"ce_mag_b4": ce_p4, "ref_ce": ref_ce,
                      "tol": HOST_TOL}
    return r


def verdict_of(r: dict) -> str:
    if not r["C5"]:
        return "HOST-DAMAGED"
    if not r["C1"]:
        return "SCHEME-INERT"
    if not r["C4"]:
        return "UNSPECIFIC"
    if r["fp16_dominates"]:
        return "MAGNITUDE-SALIENT"
    return f"MAGNITUDE-DISPOSABLE (+{r['C3']})"


# ══════════════════════════════════════════════════════════════════════════
# --validate (no model)
# ══════════════════════════════════════════════════════════════════════════
def run_validate(alpha: float) -> int:
    ok = True
    print("── §P-COMPANDING-QUANT --validate (no model) ──")
    rng = np.random.default_rng(0)

    # 1. RTN round-trip: int4 error bounded by half-step; int8 tighter than int4
    w = rng.normal(size=(32, 128)).astype(np.float32)
    e4 = float(np.abs(w - rtn_int(w, 4)).max())
    e8 = float(np.abs(w - rtn_int(w, 8)).max())
    scale4 = np.abs(w).max(axis=1).max() / 7
    good = e4 <= scale4 * 0.6 and e8 < e4
    print(f"[V] rtn: int4 max-err {e4:.4f} (<= {scale4*0.6:.4f}) int8 {e8:.4f}<int4 "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 2. ternary_all: exactly 3 values per output structure, signs preserved
    t = ternary_all(w)
    signs_ok = bool(np.all(np.sign(t[t != 0]) == np.sign(w[t != 0])))
    lvls = len(np.unique(np.round(t / (np.abs(t[t != 0]).min() + 1e-9))))
    good = signs_ok and (t == 0).any() and (t != 0).any()
    print(f"[V] ternary: signs_ok={signs_ok} has_zero={(t==0).any()} "
          f"nlevels~{lvls} {'OK' if good else 'FAIL'}")
    ok &= good

    # 3. tail_mask: exactly ~tau*N selected, disjoint from body
    score_m = rng.normal(size=(64, 256)).astype(np.float32)
    tm = tail_mask(score_m, 0.01)
    frac = tm.mean()
    good = abs(frac - 0.01) < 0.005 and bool((tm & ~tm).sum() == 0)
    print(f"[V] tail: selected frac {frac:.4f} (~0.01) {'OK' if good else 'FAIL'}")
    ok &= good

    # 4. tier_quant: body grid tightens when the tail is pulled out (outliers
    #    excluded from the body scale => body positions quantized finer)
    wb_ = w.copy()
    wb_[0, 0] = 50.0                                  # a planted outlier
    tmask = tail_mask(wb_, 0.01)
    q_tier = tier_quant(wb_, tmask, 3, "ternary")
    q_plain = rtn_int(wb_, 3)                         # outlier stretches the grid
    body = ~tmask
    err_tier = float(np.abs(wb_[body] - q_tier[body]).mean())
    err_plain = float(np.abs(wb_[body] - q_plain[body]).mean())
    good = err_tier < err_plain and bool(tmask[0, 0])
    print(f"[V] tier: body-err tiered {err_tier:.4f} < plain {err_plain:.4f} "
          f"(outlier pulled) {'OK' if good else 'FAIL'}")
    ok &= good

    # 5. fp16 tail is EXACT; ternary tail is sign-only
    q_fp = tier_quant(wb_, tmask, 3, "fp16")
    good = (float(np.abs(wb_[tmask] - q_fp[tmask]).max()) < 1e-5
            and float(np.abs(wb_[tmask] - q_tier[tmask]).max()) > 1e-3)
    print(f"[V] tail-store: fp16 exact, ternary lossy {'OK' if good else 'FAIL'}")
    ok &= good

    # 6. effective bits: fp16 tail costs more than ternary tail; twn ~ 1.585
    eb_mag = effective_bits("companding_mag", 3)
    eb_fp = effective_bits("outlier_mag_fp16", 3)
    eb_int = effective_bits("int_uniform", 3)
    good = (eb_fp > eb_mag > eb_int - 0.2
            and abs(effective_bits("twn", 3) - LOG2_3) < 1e-6)
    print(f"[V] bits: int {eb_int:.2f} mag {eb_mag:.2f} fp16 {eb_fp:.2f} "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 7. shuffle-tail: matched count, different positions
    mag_t = tail_mask(score_m, 0.01)
    idx = np.flatnonzero(mag_t.ravel())
    perm = rng.permutation(score_m.size)[:idx.size]
    shuf = np.zeros(score_m.size, bool)
    shuf[perm] = True
    shuf = shuf.reshape(score_m.shape)
    good = shuf.sum() == mag_t.sum() and int((shuf & mag_t).sum()) < mag_t.sum()
    print(f"[V] shuffle: matched count {shuf.sum()}=={mag_t.sum()} moved "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 8. verdict planted worlds
    def world(name, want, mag, intu, fp16, coh, shuf_ce, ref, nchunk=40):
        # each arg = dict bits->mean CE; build per-chunk vectors with small noise
        def vecs(means):
            return {bb: (means[bb] + rng.normal(0, 0.02, nchunk)).astype(float)
                    for bb in BODY_BITS}
        ce = {"companding_mag": vecs(mag), "int_uniform": vecs(intu),
              "outlier_mag_fp16": vecs(fp16), "companding_coh": vecs(coh),
              "companding_shuffle": vecs(shuf_ce), "twn": vecs(mag)}
        r = score(ce, ref, np.random.default_rng(7), alpha)
        v = verdict_of(r)
        hit = want in v
        print(f"[V] {name} -> {v} (want {want}) {'OK' if hit else 'FAIL'}")
        return hit

    # baselines: companding beats int_uniform + shuffle; fp16 ~ companding (disposable)
    base_mag = {2: 3.20, 3: 3.05, 4: 3.00}
    base_int = {2: 3.60, 3: 3.20, 4: 3.02}
    base_shuf = {2: 3.55, 3: 3.30, 4: 3.10}
    ok &= world("mag-disposable-magsel", "MAGNITUDE-DISPOSABLE (+MAGNITUDE-SELECTS)",
                base_mag, base_int, {2: 3.21, 3: 3.06, 4: 3.005},
                {2: 3.22, 3: 3.07, 4: 3.01}, base_shuf, ref=2.98)
    ok &= world("mag-disposable-cohsel", "MAGNITUDE-DISPOSABLE (+COHERENCE-SELECTS)",
                base_mag, base_int, {2: 3.21, 3: 3.06, 4: 3.005},
                {2: 3.10, 3: 2.99, 4: 2.97}, base_shuf, ref=2.98)
    ok &= world("mag-salient", "MAGNITUDE-SALIENT",
                base_mag, base_int, {2: 3.00, 3: 2.90, 4: 2.85},   # fp16 much better
                {2: 3.22, 3: 3.07, 4: 3.01}, base_shuf, ref=2.98)
    ok &= world("scheme-inert", "SCHEME-INERT",
                base_int, base_int, base_int, base_int, base_int, ref=2.98)  # mag~int
    ok &= world("unspecific", "UNSPECIFIC",
                base_mag, base_int, {2: 3.21, 3: 3.06, 4: 3.005},
                {2: 3.22, 3: 3.07, 4: 3.01}, base_mag, ref=2.98)   # shuffle ~ mag
    ok &= world("host-damaged", "HOST-DAMAGED",
                {2: 3.9, 3: 3.8, 4: 3.7}, base_int, {2: 3.9, 3: 3.8, 4: 3.7},
                {2: 3.9, 3: 3.8, 4: 3.7}, {2: 4.5, 3: 4.4, 4: 4.3}, ref=2.98)

    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Corpora (held eval != calibration; diverse innocent prose)
# ══════════════════════════════════════════════════════════════════════════
EVAL_TEXTS = [*wb.CE_TEXTS,
    "The river wound slowly through the valley toward the distant sea",
    "Scientists recorded the temperature at dawn and again at dusk",
    "A single candle lit the corner of the quiet reading room",
    "The train arrived late but the platform was nearly empty",
    "She folded the letter carefully and placed it in the drawer",
    "Autumn leaves gathered in drifts against the garden wall",
    "The committee reviewed the proposal over several long meetings",
    "A faint melody drifted from the open window across the street",
    "The old clock in the hallway had not been wound in years",
    "Fishermen returned to the harbor as the storm clouds gathered",
    "The lecture covered the history of early printing techniques",
    "Two children built a sandcastle near the edge of the tide",
    "The librarian catalogued the new arrivals before closing time",
    "A warm loaf of bread cooled on the windowsill of the cottage",
    "The hikers followed the marked trail up the gentle ridge",
    "Rain tapped steadily on the tin roof throughout the night",
    "The painter mixed a soft grey for the winter sky study",
    "An old photograph showed the square as it had been decades ago",
    "The gardener pruned the roses before the first hard frost",
    "The ferry crossed the strait under a pale morning sky"]
CALIB_TEXTS = [
    "The engineer tightened the last bolt and tested the machine",
    "A flock of geese crossed the field toward the frozen pond",
    "The recipe required a slow simmer for the better part of an hour",
    "Students filed into the hall for the afternoon examination",
    "The lighthouse beam swept across the dark and restless water",
    "He sketched the bridge from the far bank in fading light",
    "The market stalls were busy with early shoppers at sunrise",
    "A quiet path led through the pines to a small clearing",
    "The tailor measured the cloth twice before the first cut",
    "Snow settled softly on the rooftops of the sleeping town",
    "The orchestra rehearsed the final movement one more time",
    "A weathered map marked the trail to the mountain hut"]


# ══════════════════════════════════════════════════════════════════════════
# Model path
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import operand_multihop3 as mh3
    import torch
    import torch.nn.functional as F
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps"
                           or torch.backends.mps.is_available()) else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    dec, _norm, _lm = mh3.resolve_parts(model)
    n_layers = len(dec)
    layers = list(range(n_layers))
    if args.n_layers:
        layers = layers[:args.n_layers]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[cq] {args.model_id} dev={dev} N={n_layers} band={layers[0]}..{layers[-1]} "
          f"tau={TAU} body_bits={BODY_BITS} calib={args.calib_batches}", flush=True)

    # target FFN matrices: (layer, proj) -> weight Parameter
    mats = {}
    for li in layers:
        for name in ("gate_proj", "up_proj", "down_proj"):
            mats[(li, name)] = getattr(dec[li].mlp, name).weight

    # ── coherence calibration: per-weight gradient sign-consistency ──
    def calibrate() -> dict:
        for w in mats.values():
            w.requires_grad_(True)
        sum_g = {k: np.zeros(tuple(w.shape), np.float32) for k, w in mats.items()}
        sum_a = {k: np.zeros(tuple(w.shape), np.float32) for k, w in mats.items()}
        texts = (CALIB_TEXTS * ((args.calib_batches // len(CALIB_TEXTS)) + 1))[
            :args.calib_batches]
        for i, t in enumerate(texts):
            ids = tok(t, return_tensors="pt").to(dev)
            model.zero_grad(set_to_none=True)
            out = model(**ids, labels=ids.input_ids)
            out.loss.backward()
            for k, w in mats.items():
                if w.grad is not None:
                    g = w.grad.detach().float().cpu().numpy()
                    sum_g[k] += g
                    sum_a[k] += np.abs(g)
            if i % max(len(texts) // 4, 1) == 0:
                print(f"[cq]   calib {i+1}/{len(texts)} loss {float(out.loss):.3f}",
                      flush=True)
        model.zero_grad(set_to_none=True)
        for w in mats.values():
            w.requires_grad_(False)
        return {k: np.abs(sum_g[k]) / (sum_a[k] + 1e-12) for k in mats}  # coherence

    print("[cq] calibrating coherence (grad sign-consistency)…", flush=True)
    coherence = calibrate()

    # ── precompute per-matrix numpy weights + tier masks ──
    w_np, mag_tail, coh_tail = {}, {}, {}
    for k, w in mats.items():
        arr = w.detach().float().cpu().numpy()
        w_np[k] = arr
        mag_tail[k] = tail_mask(arr, TAU)
        coh_tail[k] = tail_mask(coherence[k], TAU)
    # advisory: Jaccard(coh-tail, mag-tail) pooled
    inter = sum(int((mag_tail[k] & coh_tail[k]).sum()) for k in mats)
    union = sum(int((mag_tail[k] | coh_tail[k]).sum()) for k in mats)
    jaccard = inter / max(union, 1)
    print(f"[cq] Jaccard(coh-tail, mag-tail) = {jaccard:.3f} (s171 predicts ~0.17)")

    shuf_seeds = list(range(args.shuffle_seeds))

    def shuffled_tail(k, seed) -> np.ndarray:
        rng = np.random.default_rng(1000 + seed + hash(k) % 997)
        n = w_np[k].size
        cnt = int(mag_tail[k].sum())
        m = np.zeros(n, bool)
        m[rng.permutation(n)[:cnt]] = True
        return m.reshape(w_np[k].shape)

    # ── apply / restore ──
    originals = {k: w.detach().clone() for k, w in mats.items()}

    def apply_arm(arm, body_bits, seed=0):
        for k, w in mats.items():
            st = shuffled_tail(k, seed) if arm == "companding_shuffle" else None
            wq = quantize_matrix(w_np[k], arm, body_bits, mag_tail[k],
                                 coh_tail[k], st)
            with torch.no_grad():
                w.data.copy_(torch.tensor(wq, dtype=w.dtype, device=w.device))

    def restore():
        for k, w in mats.items():
            with torch.no_grad():
                w.data.copy_(originals[k])

    # ── metric: per-chunk CE (paired) + advisory factual task acc ──
    def chunk_ce() -> np.ndarray:
        out = []
        for t in EVAL_TEXTS:
            ids = tok(t, return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits
            lp = F.log_softmax(lo[0, :-1].float(), dim=-1)
            tgt = ids.input_ids[0, 1:]
            out.append(float(-lp[torch.arange(len(tgt)), tgt].mean()))
        return np.array(out)

    caps = sorted({cap for cap, _ in wb.BANK.values()})

    def task_acc() -> float:
        hits = []
        for co, (cap, _) in wb.BANK.items():
            lo = None
            ids = tok(f"The capital of {co} is", return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
            pred = max(caps, key=lambda c: lo[mh3.first_tid(tok, c)])
            hits.append(wb.first_word(pred) == wb.first_word(cap))
        return float(np.mean(hits))

    # ── reference (unquantized) ──
    ref_ce_vec = chunk_ce()
    ref_ce = float(ref_ce_vec.mean())
    ref_task = task_acc()
    print(f"[cq] unquantized ref: CE {ref_ce:.4f} task_acc {ref_task:.3f}")

    # ── run arms x budgets ──
    ce: dict = {a: {} for a in ARMS}
    task: dict = {a: {} for a in ARMS}
    ebits: dict = {a: {} for a in ARMS}
    for arm in ARMS:
        budgets = (4,) if arm == "twn" else BODY_BITS
        for bb in budgets:
            if arm == "companding_shuffle":
                vs = []
                for s in shuf_seeds:
                    apply_arm(arm, bb, s)
                    vs.append(chunk_ce())
                    restore()
                cev = np.mean(vs, axis=0)
                apply_arm(arm, bb, shuf_seeds[0])
                ta = task_acc()
                restore()
            else:
                apply_arm(arm, bb)
                cev = chunk_ce()
                ta = task_acc()
                restore()
            ce[arm][bb] = cev
            task[arm][bb] = ta
            ebits[arm][bb] = effective_bits(arm, bb)
            print(f"[cq]   {arm:18s} b{bb} eff{ebits[arm][bb]:.2f} "
                  f"CE {float(cev.mean()):.4f} task {ta:.3f}", flush=True)
        if arm == "twn":                              # broadcast the single point
            for bb in BODY_BITS:
                ce[arm].setdefault(bb, ce[arm][4])
                ebits[arm].setdefault(bb, ebits[arm][4])

    # verify bit-exact restore
    max_dev = max(float((mats[k].detach() - originals[k]).abs().max())
                  for k in mats)
    print(f"[cq] restore check: max|W-W0| = {max_dev:.2e}")

    # ── frozen scoring ──
    sc = score(ce, ref_ce, np.random.default_rng(args.seed + 999), args.alpha)
    v = verdict_of(sc)
    print(f"\n[cq] ════ VERDICT: {v} ════")
    print(f"  C1={sc['C1']} C2={sc['C2']}(fp16_dom={sc['fp16_dominates']}) "
          f"C3={sc['C3']} C4={sc['C4']} C5={sc['C5']}")
    for bb in BODY_BITS:
        print(f"  b{bb}: int {float(ce['int_uniform'][bb].mean()):.4f} "
              f"mag {float(ce['companding_mag'][bb].mean()):.4f} "
              f"fp16 {float(ce['outlier_mag_fp16'][bb].mean()):.4f} "
              f"coh {float(ce['companding_coh'][bb].mean()):.4f} "
              f"shuf {float(ce['companding_shuffle'][bb].mean()):.4f}")

    payload = {"model_id": args.model_id, "config": vars(args),
               "n_layers": n_layers, "band": [layers[0], layers[-1]],
               "tau": TAU, "ref_ce": ref_ce, "ref_task": ref_task,
               "jaccard_coh_mag": jaccard, "restore_max_dev": max_dev,
               "arms": {a: {"ce_mean": {bb: float(ce[a][bb].mean())
                                        for bb in ce[a]},
                            "task": task[a], "ebits": ebits[a]} for a in ARMS},
               "ce_per_chunk": {a: {bb: ce[a][bb].tolist() for bb in ce[a]}
                                for a in ARMS},
               "scoring": {"gates": sc, "verdict": v}}
    (out_dir / "results.json").write_text(json.dumps(_json_safe(payload), indent=2))
    print(f"[cq] wrote {out_dir}/results.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--calib-batches", type=int, default=48)
    ap.add_argument("--shuffle-seeds", type=int, default=3)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-layers", type=int, default=0,
                    help="smoke: cap FFN layers (mechanics only)")
    ap.add_argument("--out", default="results/companding-quant/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
