#!/usr/bin/env python3
"""P-DELTA-QUANT — is base-weight MAGNITUDE algebraically separable (delta-vs-base)?

Pre-reg: mementum/knowledge/explore/ratio-gradient-quantization.md
§P-DELTA-QUANT (FROZEN s307, Michael-approved). Post-hoc WEIGHT quantization of
Qwen3-4B FFN. §P-COMPANDING-QUANT (s306) found base-weight outliers MAGNITUDE-SALIENT
-> routing⊥magnitude does NOT extend from trained deltas to raw matrices; the register
theory (register-theory-of-quantization.md) was scoped "quantize the delta, keep the
base." The mechanism blames SUPERPOSITION: "a base matrix superposes routing AND value
in the same magnitudes." This test asks whether that superposition is ALGEBRAICALLY
separable: decompose each FFN matrix W = B + D (B = value base kept fp16, D = residual),
ternarize the RESIDUAL. If the residual ternarizes losslessly-for-routing where raw-W
did not, the register split reaches base weights VIA decomposition. (= the LoftQ /
LQ-LoRA init move, register-interpreted and NULL-GATED — those methods assume the
residual is quantizable but never null-test the register.)

Register (lambda measure): the claim is ROUTING, so the metric is DOWNSTREAM CE on held
text (+ advisory factual task acc), NEVER ||W-Q(W)|| / mag_cos. Gated against a
matched-rank RANDOM-BASE null (lambda yardstick).

Base constructions (the structural knob):
  lowrank-k   : B = SVD rank-k truncation (top-energy value directions), fp16. PRIMARY.
  mean        : B = per-output-row mean (rank-1 DC), fp16. cheap floor.
  coherence-k : B = SVD rank-k of the LOW-coherence content W*(1-c_hat) (incoherent =
                value/noise magnitude, s171), fp16. the literal register test (routing=
                coherent -> absorbing incoherent value leaves a purer routing residual).
  random-k    : B = random rank-k subspace, spectrum matched to the SVD base. YARDSTICK.
Delta quantizer: per-row TWN FULL ternary (no body-int tiering) — the sharpest "does
the residual live in the routing register" test.

Arms: twn / int_uniform / companding_mag (s306 no-decomposition reproductions) +
  delta_lowrank (PRIMARY, k-sweep) / delta_mean / delta_coherence (selector) /
  delta_random (yardstick, >=3 seeds).

Gates (verbum.dsp paired_permutation on per-chunk CE; lower CE = better):
  D1 SCHEME-WORKS    : delta_lowrank(best k) beats raw twn.
  D2 VALUE-SEPARABLE : delta_lowrank SIG beats delta_random at same k (>=1 k) [register
                       primary + lambda yardstick — the SPECIFIC value subspace, not
                       just more fp16 bits].
  D3 HOLDS-vs-SALIENT: delta_lowrank(best k) within HOST_TOL of int_uniform@b3 (floors
                       compared at b3 >= any delta budget = conservative) AND beats
                       companding_mag@b3.
  D4 HOST-SANE       : int_uniform@b4 (NEUTRAL anchor, fixes s306 C5 mis-anchor) within
                       HOST_TOL of the unquantized ref.
Selector sub-tag (advisory): sign(delta_coherence - delta_lowrank) -> +ENERGY-BASE /
  +COHERENCE-BASE. Does NOT gate.
Verdicts: VALUE-SEPARABLE (+ENERGY-BASE/+COHERENCE-BASE) / STILL-SALIENT /
  DECOMP-INERT / HOST-DAMAGED.

Reuse (no fork): companding_quant for rtn_int/ternary_all/tail_quant/EVAL_TEXTS/
CALIB_TEXTS/effective_bits + writeback_compile (BANK/CE) + operand_multihop3
(resolve_parts/first_tid) + verbum.dsp (gate). Base decomposition + residual arms are
inline. torch.svd_lowrank for the randomized truncated SVD.

Cadence: --validate (no model) -> smoke (--n-layers, mechanics only, s297) ->
Michael GO -> run.

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

import companding_quant as cq  # noqa: E402  (quantizers, texts, effective_bits reuse)
import writeback_compile as wb  # noqa: E402  (BANK / first_word reuse)
from holo_frag import _json_safe  # noqa: E402

from verbum.dsp import gate, paired_permutation  # noqa: E402

LOG2_3 = cq.LOG2_3
HOST_TOL = cq.HOST_TOL             # 0.10 (reuse the frozen companding tolerance)
K_SWEEP = (16, 64, 128)            # FROZEN rank sweep
FLOOR_BITS = (2, 3, 4)             # int_uniform / companding_mag body sweep
FLOOR_CMP_BB = 3                   # D3: floors compared at b3 (>= any delta budget)
TAU = cq.TAU                       # 1% tail for the reproduced companding_mag arm
DELTA_BASES = ("lowrank", "mean", "coherence", "random")
FLOOR_ARMS = ("twn", "int_uniform", "companding_mag")


# ══════════════════════════════════════════════════════════════════════════
# Base decompositions (pure numpy / torch; W is (out,in) float32)
# ══════════════════════════════════════════════════════════════════════════
def _svd_lowrank(w: np.ndarray, k: int):
    """Randomized truncated SVD -> (B ~= U diag(S) V^T, S[:k]). torch.svd_lowrank,
    seeded for determinism (run reproducibility + exact re-decomposition)."""
    import torch
    q = int(min(k, min(w.shape) - 1))
    t = torch.from_numpy(np.ascontiguousarray(w, dtype=np.float32))
    torch.manual_seed(0)
    U, S, V = torch.svd_lowrank(t, q=q, niter=4)
    B = (U * S) @ V.transpose(-2, -1)
    return B.numpy().astype(np.float32), S.numpy().astype(np.float32)


def lowrank_base(w: np.ndarray, k: int):
    return _svd_lowrank(w, k)


def mean_base(w: np.ndarray):
    """Per-output-row mean, broadcast (rank-1 DC)."""
    b = np.broadcast_to(w.mean(axis=1, keepdims=True), w.shape).astype(np.float32)
    return np.ascontiguousarray(b), None


def coherence_base(w: np.ndarray, coh: np.ndarray, k: int):
    """SVD rank-k of the LOW-coherence content W*(1-c_hat) (c_hat in [0,1])."""
    return _svd_lowrank(w * (1.0 - coh), k)


def random_base(w: np.ndarray, k: int, spectrum: np.ndarray,
                rng: np.random.Generator) -> np.ndarray:
    """Random rank-k subspace with the SVD spectrum (matched Frobenius energy,
    random directions = the budget-matched null for lowrank_base)."""
    m, n = w.shape
    kk = int(min(k, min(m, n) - 1, spectrum.size))
    u = np.linalg.qr(rng.standard_normal((m, kk)).astype(np.float32))[0][:, :kk]
    v = np.linalg.qr(rng.standard_normal((n, kk)).astype(np.float32))[0][:, :kk]
    s = spectrum[:kk]
    return ((u * s) @ v.T).astype(np.float32)


def delta_quant_matrix(w: np.ndarray, base: str, k: int,
                       coh: np.ndarray | None,
                       spec: np.ndarray | None,
                       rng: np.random.Generator | None) -> np.ndarray:
    """W = B + D ; B fp16, D -> per-row TWN full ternary. Returns B + ternary(D)."""
    if base == "mean":
        b, _ = mean_base(w)
    elif base == "lowrank":
        b, _ = lowrank_base(w, k)
    elif base == "coherence":
        assert coh is not None
        b, _ = coherence_base(w, coh, k)
    elif base == "random":
        assert spec is not None and rng is not None
        b = random_base(w, k, spec, rng)
    else:
        raise ValueError(base)
    d = (w - b).astype(np.float32)
    dq = cq.ternary_all(d)
    return (b + dq).astype(np.float32)


def delta_effective_bits(k: int, m: int, n: int) -> float:
    """rank-k base fp16 + ternary residual: [16*k*(m+n) + log2(3)*m*n] / (m*n)."""
    return float((16.0 * k * (m + n) + LOG2_3 * m * n) / (m * n))


def mean_effective_bits(m: int, n: int) -> float:
    """row-mean base (m fp16 scalars) + ternary residual."""
    return float((16.0 * m + LOG2_3 * m * n) / (m * n))


# ══════════════════════════════════════════════════════════════════════════
# Scoring + verdict (pure; per-chunk CE, lower=better; --validate plants worlds)
# ══════════════════════════════════════════════════════════════════════════
def ce_better(a_ce, b_ce, rng, alpha, name):
    """Gate: arm A's CE significantly LOWER than B's (A better)? paired over chunks."""
    a = np.asarray(a_ce, float)
    b = np.asarray(b_ce, float)
    return gate(float(np.mean(b - a)), paired_permutation(b, a, rng),
                "greater", alpha, name=name)


def score(ce: dict, ref_ce: float, rng, alpha: float) -> dict:
    """ce[arm][knob] = per-chunk CE vector. knob = k for delta_*, body_bits for floors.
    Frozen D1-D4 + selector sub-tag + verdict."""
    r: dict = {}
    lr = ce["delta_lowrank"]
    best_k = min(K_SWEEP, key=lambda kk: float(np.mean(lr[kk])))
    r["best_k"] = best_k

    # D1 scheme-works: delta_lowrank(best k) beats raw twn
    g1 = ce_better(lr[best_k], ce["twn"]["_"], rng, alpha, "lowrank<twn")
    r["D1"] = bool(g1.verdict)
    r["D1_detail"] = {"effect": g1.value, "p": g1.p}

    # D2 value-separable: delta_lowrank SIG beats delta_random at same k (>=1 k)
    d2 = {}
    for kk in K_SWEEP:
        g = ce_better(lr[kk], ce["delta_random"][kk], rng, alpha, f"lr<rand@{kk}")
        d2[kk] = {"beats_random": bool(g.verdict), "effect": g.value, "p": g.p}
    r["D2"] = bool(any(v["beats_random"] for v in d2.values()))
    r["D2_detail"] = d2

    # D3 holds-vs-salient: reach int_uniform@b3 (within tol) AND beat companding_mag@b3
    ce_lr = float(np.mean(lr[best_k]))
    ce_int_b3 = float(np.mean(ce["int_uniform"][FLOOR_CMP_BB]))
    d3a = bool(ce_lr <= ce_int_b3 * (1.0 + HOST_TOL))
    g3b = ce_better(lr[best_k], ce["companding_mag"][FLOOR_CMP_BB], rng, alpha,
                    "lr<companding_mag@b3")
    d3b = bool(g3b.verdict)
    r["D3"] = bool(d3a and d3b)
    r["D3_detail"] = {"ce_lr_bestk": ce_lr, "ce_int_b3": ce_int_b3,
                      "reaches_int": d3a, "beats_companding_mag": d3b,
                      "companding_effect": g3b.value, "companding_p": g3b.p}

    # D4 host-sane: int_uniform@b4 (NEUTRAL anchor) within HOST_TOL of ref
    ce_int_b4 = float(np.mean(ce["int_uniform"][4]))
    r["D4"] = bool(ce_int_b4 <= ref_ce * (1.0 + HOST_TOL))
    r["D4_detail"] = {"ce_int_b4": ce_int_b4, "ref_ce": ref_ce, "tol": HOST_TOL}

    # selector sub-tag (advisory): coherence-base vs energy-base at their best k
    coh = ce["delta_coherence"]
    best_k_coh = min(K_SWEEP, key=lambda kk: float(np.mean(coh[kk])))
    coh_better = float(np.mean(coh[best_k_coh])) < ce_lr
    r["selector"] = "COHERENCE-BASE" if coh_better else "ENERGY-BASE"
    r["selector_detail"] = {"best_k_coh": best_k_coh,
                            "ce_coh_bestk": float(np.mean(coh[best_k_coh])),
                            "ce_lr_bestk": ce_lr}
    return r


def verdict_of(r: dict) -> str:
    if not r["D4"]:
        return "HOST-DAMAGED"
    if not r["D1"]:
        return "DECOMP-INERT"
    if r["D2"] and r["D3"]:
        return f"VALUE-SEPARABLE (+{r['selector']})"
    return "STILL-SALIENT"


# ══════════════════════════════════════════════════════════════════════════
# --validate (no model)
# ══════════════════════════════════════════════════════════════════════════
def run_validate(alpha: float) -> int:
    ok = True
    print("── §P-DELTA-QUANT --validate (no model) ──")
    rng = np.random.default_rng(0)

    # 1. lowrank_base of a rank-r matrix (r<=k) reconstructs exactly (residual ~ 0)
    m, n, r_true, k = 40, 96, 8, 16
    u = rng.standard_normal((m, r_true)).astype(np.float32)
    v = rng.standard_normal((r_true, n)).astype(np.float32)
    w_lr = (u @ v).astype(np.float32)
    b, s = lowrank_base(w_lr, k)
    resid = float(np.abs(w_lr - b).max())
    good = resid < 1e-2 and s.size >= r_true
    print(f"[V] lowrank exact: rank-{r_true} residual max {resid:.4e} "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 2. mean_base: rows constant = row mean; residual is zero-mean per row
    w = rng.normal(size=(32, 128)).astype(np.float32)
    bm, _ = mean_base(w)
    rowconst = float(np.abs(bm - bm[:, :1]).max())
    rowmean = float(np.abs((w - bm).mean(axis=1)).max())
    good = rowconst < 1e-6 and rowmean < 1e-5
    print(f"[V] mean base: row-const {rowconst:.2e} residual-rowmean {rowmean:.2e} "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 3. random_base: matched Frobenius energy to the SVD base, different subspace
    b_svd, s_svd = lowrank_base(w, k)
    b_rnd = random_base(w, k, s_svd, np.random.default_rng(1))
    e_svd = float(np.linalg.norm(b_svd))
    e_rnd = float(np.linalg.norm(b_rnd))
    cos = float((b_svd.ravel() @ b_rnd.ravel())
                / (e_svd * e_rnd + 1e-9))
    good = abs(e_rnd - e_svd) / e_svd < 0.15 and abs(cos) < 0.3
    print(f"[V] random base: energy svd {e_svd:.2f} rnd {e_rnd:.2f} align {cos:.3f} "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 4. delta_quant = B + ternary(D) with ONE (deterministic) B; residual ternary
    wq = delta_quant_matrix(w, "lowrank", k, None, None, None)
    b_lr, _ = lowrank_base(w, k)                      # deterministic -> same B
    d = w - b_lr
    dq = cq.ternary_all(d)
    good = float(np.abs(wq - (b_lr + dq)).max()) < 1e-4
    signs_ok = bool(np.all(np.sign(dq[dq != 0]) == np.sign(d[dq != 0])))
    print(f"[V] delta quant: B+ternary(D) consistent, signs_ok={signs_ok} "
          f"{'OK' if good and signs_ok else 'FAIL'}")
    ok &= good and signs_ok

    # 5. coherence base: uses (1-coh) weighting -> differs from plain lowrank
    coh = rng.uniform(0, 1, size=w.shape).astype(np.float32)
    bc, _ = coherence_base(w, coh, k)
    diff = float(np.abs(bc - b_svd).mean())
    good = diff > 1e-4
    print(f"[V] coherence base: differs from energy base (mean|Δ| {diff:.4f}) "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 6. effective bits: delta increases with k; mean ~ ternary floor; k128 < int3
    m2, n2 = 2560, 9728
    eb16 = delta_effective_bits(16, m2, n2)
    eb64 = delta_effective_bits(64, m2, n2)
    eb128 = delta_effective_bits(128, m2, n2)
    ebm = mean_effective_bits(m2, n2)
    good = (eb16 < eb64 < eb128 < 3.0 and abs(ebm - LOG2_3) < 0.05
            and eb16 > LOG2_3)
    print(f"[V] bits: mean {ebm:.3f} k16 {eb16:.3f} k64 {eb64:.3f} k128 {eb128:.3f} "
          f"(<int3) {'OK' if good else 'FAIL'}")
    ok &= good

    # 7. verdict planted worlds
    def world(name, want, lr, rand, twn_, intu, cmag, coh_arm, ref, nchunk=40):
        def vecs_k(means):
            return {kk: (means[kk] + rng.normal(0, 0.02, nchunk)).astype(float)
                    for kk in K_SWEEP}

        def vecs_b(means):
            return {bb: (means[bb] + rng.normal(0, 0.02, nchunk)).astype(float)
                    for bb in FLOOR_BITS}
        ce = {"delta_lowrank": vecs_k(lr), "delta_random": vecs_k(rand),
              "delta_coherence": vecs_k(coh_arm),
              "delta_mean": vecs_k(lr),
              "twn": {"_": (twn_ + rng.normal(0, 0.02, nchunk)).astype(float)},
              "int_uniform": vecs_b(intu), "companding_mag": vecs_b(cmag)}
        rr = score(ce, ref, np.random.default_rng(7), alpha)
        v = verdict_of(rr)
        hit = want in v
        print(f"[V] {name} -> {v} (want {want}) {'OK' if hit else 'FAIL'}")
        return hit

    # value-separable: lowrank beats random + reaches int_b3 + beats companding_mag_b3
    lr_good = {16: 3.15, 64: 3.02, 128: 3.00}
    rand_bad = {16: 3.55, 64: 3.50, 128: 3.48}
    coh_tie = {16: 3.18, 64: 3.05, 128: 3.03}       # slightly worse than lr -> ENERGY
    intu = {2: 3.30, 3: 3.05, 4: 2.98}
    cmag = {2: 3.60, 3: 3.40, 4: 3.20}
    ok &= world("value-sep-energy", "VALUE-SEPARABLE (+ENERGY-BASE)",
                lr_good, rand_bad, 3.60, intu, cmag, coh_tie, ref=2.98)
    coh_win = {16: 3.05, 64: 2.95, 128: 2.93}       # coherence beats lr -> COHERENCE
    ok &= world("value-sep-coherence", "VALUE-SEPARABLE (+COHERENCE-BASE)",
                lr_good, rand_bad, 3.60, intu, cmag, coh_win, ref=2.98)
    # still-salient: lowrank ~ random (¬D2)
    ok &= world("still-salient-null", "STILL-SALIENT",
                lr_good, lr_good, 3.60, intu, cmag,   # random ties lowrank -> ¬D2
                coh_tie, ref=2.98)
    # still-salient: doesn't reach int_b3 (¬D3), but beats random (D2)
    ok &= world("still-salient-far", "STILL-SALIENT",
                {16: 4.0, 64: 3.9, 128: 3.85}, {16: 4.6, 64: 4.5, 128: 4.45},
                4.9, intu, cmag, {16: 4.1, 64: 4.0, 128: 3.95}, ref=2.98)
    # decomp-inert: lowrank does not beat twn (¬D1)
    ok &= world("decomp-inert", "DECOMP-INERT",
                {16: 3.62, 64: 3.61, 128: 3.60}, rand_bad, 3.60, intu, cmag,
                coh_tie, ref=2.98)
    # host-damaged: int_uniform@b4 far from ref (¬D4)
    ok &= world("host-damaged", "HOST-DAMAGED",
                lr_good, rand_bad, 3.60, {2: 4.0, 3: 3.9, 4: 3.8}, cmag, coh_tie,
                ref=2.98)

    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


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
    print(f"[dq] {args.model_id} dev={dev} N={n_layers} band={layers[0]}..{layers[-1]} "
          f"k_sweep={K_SWEEP} floors={FLOOR_BITS}", flush=True)

    mats = {}
    for li in layers:
        for name in ("gate_proj", "up_proj", "down_proj"):
            mats[(li, name)] = getattr(dec[li].mlp, name).weight

    # ── coherence calibration (only needed for delta_coherence) ──
    def calibrate() -> dict:
        for w in mats.values():
            w.requires_grad_(True)
        sum_g = {k: np.zeros(tuple(w.shape), np.float32) for k, w in mats.items()}
        sum_a = {k: np.zeros(tuple(w.shape), np.float32) for k, w in mats.items()}
        texts = (cq.CALIB_TEXTS * ((args.calib_batches // len(cq.CALIB_TEXTS)) + 1))[
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
                print(f"[dq]   calib {i+1}/{len(texts)} "
                      f"loss {float(out.loss.detach()):.3f}", flush=True)
        model.zero_grad(set_to_none=True)
        for w in mats.values():
            w.requires_grad_(False)
        return {k: np.abs(sum_g[k]) / (sum_a[k] + 1e-12) for k in mats}  # c_hat[0,1]

    print("[dq] calibrating coherence (grad sign-consistency)…", flush=True)
    coherence = calibrate()

    # ── precompute numpy weights + per-matrix SVD spectra (for the matched null) ──
    w_np, spec = {}, {}
    for k, w in mats.items():
        arr = w.detach().float().cpu().numpy()
        w_np[k] = arr
        # spectrum per k: cache the largest-k SVD once, slice down
    max_k = max(K_SWEEP)
    for k in mats:
        _, s = lowrank_base(w_np[k], max_k)
        spec[k] = s
    dims = {k: w_np[k].shape for k in mats}

    shuf_seeds = list(range(args.shuffle_seeds))
    originals = {k: w.detach().clone() for k, w in mats.items()}

    def set_mats(fn):
        for k, w in mats.items():
            wq = fn(k)
            with torch.no_grad():
                w.data.copy_(torch.tensor(wq, dtype=w.dtype, device=w.device))

    def restore():
        for k, w in mats.items():
            with torch.no_grad():
                w.data.copy_(originals[k])

    # ── metrics: per-chunk CE + advisory task acc ──
    caps = sorted({cap for cap, _ in wb.BANK.values()})

    def chunk_ce() -> np.ndarray:
        out = []
        for t in cq.EVAL_TEXTS:
            ids = tok(t, return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits
            lp = F.log_softmax(lo[0, :-1].float(), dim=-1)
            tgt = ids.input_ids[0, 1:]
            out.append(float(-lp[torch.arange(len(tgt)), tgt].mean()))
        return np.array(out)

    def task_acc() -> float:
        hits = []
        for co, (cap, _) in wb.BANK.items():
            ids = tok(f"The capital of {co} is", return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
            pred = max(caps, key=lambda c: lo[mh3.first_tid(tok, c)])
            hits.append(wb.first_word(pred) == wb.first_word(cap))
        return float(np.mean(hits))

    ref_ce_vec = chunk_ce()
    ref_ce = float(ref_ce_vec.mean())
    ref_task = task_acc()
    print(f"[dq] unquantized ref: CE {ref_ce:.4f} task_acc {ref_task:.3f}", flush=True)

    ce: dict = {}
    task: dict = {}
    ebits: dict = {}

    def eval_arm(fn):
        set_mats(fn)
        cev = chunk_ce()
        ta = task_acc()
        restore()
        return cev, ta

    # ── floor arms (no decomposition; reuse companding quantizers) ──
    ce["twn"], task["twn"], ebits["twn"] = {}, {}, {}
    cev, ta = eval_arm(lambda k: cq.ternary_all(w_np[k]))
    ce["twn"]["_"], task["twn"]["_"], ebits["twn"]["_"] = cev, ta, LOG2_3
    print(f"[dq]   {'twn':22s} eff{LOG2_3:.2f} CE {float(cev.mean()):.4f} "
          f"task {ta:.3f}", flush=True)

    for arm in ("int_uniform", "companding_mag"):
        ce[arm], task[arm], ebits[arm] = {}, {}, {}
        for bb in FLOOR_BITS:
            if arm == "int_uniform":
                cev, ta = eval_arm(lambda k, b=bb: cq.rtn_int(w_np[k], b))
                eb = float(bb)
            else:  # companding_mag: top-tau |w| -> ternary sign, body int-b
                cev, ta = eval_arm(lambda k, b=bb: cq.tier_quant(
                    w_np[k], cq.tail_mask(w_np[k], TAU), b, "ternary"))
                eb = cq.effective_bits("companding_mag", bb)
            ce[arm][bb], task[arm][bb], ebits[arm][bb] = cev, ta, eb
            lbl = f"{arm} b{bb}"
            print(f"[dq]   {lbl:22s} eff{eb:.2f} CE {float(cev.mean()):.4f} "
                  f"task {ta:.3f}", flush=True)

    # ── delta arms (base + ternary residual) ──
    for base in DELTA_BASES:
        arm = f"delta_{base}"
        ce[arm], task[arm], ebits[arm] = {}, {}, {}
        ks = (max_k,) if base == "mean" else K_SWEEP     # mean is k-independent
        for kk in ks:
            if base == "random":
                vs = []
                for s in shuf_seeds:
                    rng = np.random.default_rng(2000 + s)
                    cev, ta = eval_arm(lambda k, kk=kk, rng=rng: (
                        delta_quant_matrix(w_np[k], "random", kk, None,
                                           spec[k], rng)))
                    vs.append(cev)
                cev = np.mean(vs, axis=0)
            elif base == "coherence":
                cev, ta = eval_arm(lambda k, kk=kk: delta_quant_matrix(
                    w_np[k], "coherence", kk, coherence[k], None, None))
            elif base == "mean":
                cev, ta = eval_arm(lambda k: delta_quant_matrix(
                    w_np[k], "mean", 0, None, None, None))
            else:  # lowrank
                cev, ta = eval_arm(lambda k, kk=kk: delta_quant_matrix(
                    w_np[k], "lowrank", kk, None, None, None))
            m, n = dims[next(iter(mats))]
            eb = (mean_effective_bits(m, n) if base == "mean"
                  else delta_effective_bits(kk, m, n))
            ce[arm][kk], task[arm][kk], ebits[arm][kk] = cev, ta, eb
            lbl = f"{arm} k{kk}"
            print(f"[dq]   {lbl:22s} eff{eb:.2f} CE {float(cev.mean()):.4f} "
                  f"task {ta:.3f}", flush=True)
        if base == "mean":                               # broadcast to K_SWEEP keys
            v = ce[arm][max_k]
            t0 = task[arm][max_k]
            e0 = ebits[arm][max_k]
            for kk in K_SWEEP:
                ce[arm].setdefault(kk, v)
                task[arm].setdefault(kk, t0)
                ebits[arm].setdefault(kk, e0)

    max_dev = max(float((mats[k].detach() - originals[k]).abs().max()) for k in mats)
    print(f"[dq] restore check: max|W-W0| = {max_dev:.2e}", flush=True)

    # ── frozen scoring ──
    sc = score(ce, ref_ce, np.random.default_rng(args.seed + 999), args.alpha)
    v = verdict_of(sc)
    print(f"\n[dq] ════ VERDICT: {v} ════")
    print(f"  D1={sc['D1']} D2={sc['D2']} D3={sc['D3']} D4={sc['D4']} "
          f"selector={sc['selector']} best_k={sc['best_k']}")
    for kk in K_SWEEP:
        print(f"  k{kk}: lowrank {float(ce['delta_lowrank'][kk].mean()):.4f} "
              f"random {float(ce['delta_random'][kk].mean()):.4f} "
              f"coherence {float(ce['delta_coherence'][kk].mean()):.4f}")
    print(f"  floors b3: int {float(ce['int_uniform'][3].mean()):.4f} "
          f"companding_mag {float(ce['companding_mag'][3].mean()):.4f} "
          f"twn {float(ce['twn']['_'].mean()):.4f}")

    payload = {"model_id": args.model_id, "config": vars(args),
               "n_layers": n_layers, "band": [layers[0], layers[-1]],
               "k_sweep": list(K_SWEEP), "ref_ce": ref_ce, "ref_task": ref_task,
               "restore_max_dev": max_dev,
               "arms": {a: {"ce_mean": {str(kk): float(np.mean(ce[a][kk]))
                                        for kk in ce[a]},
                            "task": {str(kk): task[a][kk] for kk in task[a]},
                            "ebits": {str(kk): ebits[a][kk] for kk in ebits[a]}}
                        for a in ce},
               "ce_per_chunk": {a: {str(kk): np.asarray(ce[a][kk]).tolist()
                                    for kk in ce[a]} for a in ce},
               "scoring": {"gates": sc, "verdict": v}}
    (out_dir / "results.json").write_text(json.dumps(_json_safe(payload), indent=2))
    print(f"[dq] wrote {out_dir}/results.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--calib-batches", type=int, default=48)
    ap.add_argument("--shuffle-seeds", type=int, default=3)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-layers", type=int, default=0,
                    help="smoke: cap FFN layers (mechanics only)")
    ap.add_argument("--out", default="results/delta-quant/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
