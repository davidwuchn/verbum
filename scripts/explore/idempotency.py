#!/usr/bin/env python3
"""§P-IDEMPOTENCY — idempotent vs non-idempotent intersection (SKI-control #3).

Pre-reg: mementum/knowledge/explore/type-systems-under-llm-constraints.md
§P-IDEMPOTENCY (FROZEN s320, Michael-approved GO).

The pinned type name is *non-idempotent* intersection: A∧A ≠ A, membership
ACCUMULATES with use (de Carvalho / quantitative semantics). Idempotent
intersection — the pre-committed death — predicts membership SATURATES at
first exposure (A∧A = A). A2 coherent gain (s292 CAP) measured
non-idempotence on the frozen WEIGHT plate; this re-aims it at the tape/ICL
LICENSING face (s315 §P-TYPE-ICL+TAG register — the one that LANDED).

Register (λ measure) = LICENSING, NOT kind-magnitude (heeds the s319 caveat
+ the 3× magnitude-null): L(w,prefix) = mean surprisal(anti preds) −
mean surprisal(own preds), sign fixed by w's true class (tw._signed_L).

Construction: nonce w, class c; prefix carries k∈{0..5} membership exposures.
  COHERENT   arm — k distinct paraphrases of w's TRUE membership (A2 coherent
                   superposition; tw._member_stmts).
  INCOHERENT arm — k length/form-matched NON-membership statements about w
                   (energy-matched A2 null; same token budget, no class edge).
Read L(k) per arm; discriminator = slope_coherent − slope_incoherent.

⚠ BUILD AMENDMENT (s320, runtime/build-forced, pre-run — instrument-side
ONLY; register / verdict-tree / a-priori UNCHANGED, pending Michael at GO).
Reading the construction against the runtime exposed a coherence gap: the
k=0→1 first-exposure jump licenses under BOTH idempotent and non-idempotent
intersection (both establish the type at first exposure). A literal
"ρ(L,k)>0 over all k" IB1 therefore PASSES for an idempotent step-function
(flat after k=1) → IDEMPOTENT would be nearly unreachable, contradicting the
frozen 15% a-priori. Fix: the accumulation gates IB1/IB2/IB3 operate on
**k≥1** (does the license keep growing AFTER the first exposure — the actual
non-idempotence signature A∧A vs A); **k=0 feeds IB4 SANE only** (L(0)≈0,
L(1)>0 = register works). The frozen INTENT ("idempotent saturates after
first exposure" vs "non-idempotent keeps accumulating") is exactly preserved;
this makes IDEMPOTENT genuinely reachable, as the a-priori assumed.

Gates: IB1 ACCUMULATION (slope>0 over k≥1, k-perm null) · IB2
COHERENT-SPECIFIC (slope_coh>slope_inc paired, make-or-break) · IB3
NON-SATURATING (increments k≥2 >0, non-gating corroboration) · IB4 SANE
(void-gate). Verdicts NON-IDEMPOTENT(+NON-SATURATING) / EVIDENCE-ONLY /
IDEMPOTENT / VOID.

Reuse (λ one_way, no fork): type_write (_member_stmts, HELD_PREDS, CLASSES,
REAL_MEMBERS, _signed_L, REAL_MARGIN_FLOOR) + holo_cap (NONCE_CANDS) +
verbum.dsp.nulls (gate, NullDraws, paired_permutation, sign_flip).

License: MIT (lambda provenance).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_WRAP = _HERE.parents[1] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

import type_write as tw  # noqa: E402  (frozen §8 harness — constants + pure fns)
from holo_cap import NONCE_CANDS  # noqa: E402

from verbum.dsp.nulls import (  # noqa: E402
    NullDraws,
    Register,
    gate,
    paired_permutation,
    sign_flip,
)

# ══════════════════════════════════════════════════════════════════════════
# Construction (FROZEN §P-IDEMPOTENCY)
# ══════════════════════════════════════════════════════════════════════════
K_VALUES = (0, 1, 2, 3, 4, 5)          # exposure counts (5 = all paraphrases)

# INCOHERENT arm — length/form-matched to tw._member_stmts but MEMBERSHIP-FREE:
# no class word (animal/vehicle), no held predicate, no cohyponym class. Same
# surface skeleton so the token budget matches the coherent arm exposure-by-
# exposure (the A2 energy-matched null: same exposures, no coherent edge).
_INCOHERENT_TEMPLATES = (
    "A {w} is nearby.",
    "The {w} is on the table.",
    "Every {w} was counted.",
    "{w}, like the box and the lamp, is here.",
    "I saw a {w}; it is over there.",
)


def incoherent_stmts(w: str) -> list[str]:
    return [t.format(w=w) for t in _INCOHERENT_TEMPLATES]


def coherent_prefix(w: str, cls_i: int, k: int) -> str:
    if k <= 0:
        return ""
    return " ".join(tw._member_stmts(w, cls_i)[:k]) + " "


def incoherent_prefix(w: str, cls_i: int, k: int) -> str:
    if k <= 0:
        return ""
    return " ".join(incoherent_stmts(w)[:k]) + " "


# words that must NOT appear in the incoherent arm (membership-free guard)
def _forbidden_words() -> set[str]:
    forbidden = set(tw.CLASSES)                          # animal, vehicle
    for preds in tw.HELD_PREDS:
        forbidden.update(preds)
    for members in tw.REAL_MEMBERS:
        forbidden.update(members)
    return forbidden


# ══════════════════════════════════════════════════════════════════════════
# Pure statistics + verdict (what --validate exercises; no torch, no model)
# ══════════════════════════════════════════════════════════════════════════
def _ols_slope(y: np.ndarray, x: np.ndarray) -> float:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    xm, ym = x.mean(), y.mean()
    denom = float(((x - xm) ** 2).sum())
    return float(((x - xm) * (y - ym)).sum() / denom) if denom > 1e-12 else 0.0


def per_nonce_slopes(L: np.ndarray, k_fit: np.ndarray) -> np.ndarray:
    """L: (n, len(k_fit)) — accumulation region (k≥1). Slope per nonce."""
    return np.array([_ols_slope(L[n], k_fit) for n in range(L.shape[0])])


def _slope_perm_null(L: np.ndarray, k_fit: np.ndarray,
                     rng: np.random.Generator, n_iter: int) -> np.ndarray:
    """k-label permutation null: permute k within each nonce (independently),
    recompute mean slope. Breaks L~k while preserving each nonce's L marginal."""
    n = L.shape[0]
    draws = np.empty(n_iter)
    for it in range(n_iter):
        slopes = np.empty(n)
        for i in range(n):
            slopes[i] = _ols_slope(L[i], rng.permutation(k_fit))
        draws[it] = slopes.mean()
    return draws


def _sane(b: dict) -> dict:
    """IB4 void-gate. k=0 baseline + first-exposure register + real anchor."""
    L_coh = np.asarray(b["L_coh"], float)               # (n, K)
    l0 = float(L_coh[:, 0].mean())                       # license before exposure
    l1 = float(L_coh[:, 1].mean())                       # first-exposure license
    lmax = float(L_coh[:, -1].mean())
    m = b.get("metric", {})
    real_ok = (m.get("real_margin", 0.0) >= tw.REAL_MARGIN_FLOOR
               and bool(m.get("per_class_ok", False)))
    register_ok = bool(l1 > 0.0 and lmax > 0.0)          # first exposure licenses
    baseline_ok = bool(l0 < 0.5 * max(lmax, 1e-9))       # ~no license at k=0
    return {"L0": l0, "L1": l1, "Lmax": lmax,
            "real_ok": real_ok, "register_ok": register_ok,
            "baseline_ok": baseline_ok,
            "pass": bool(real_ok and register_ok and baseline_ok)}


def compute_gates_idem(b: dict, rng: np.random.Generator, alpha: float = 0.05,
                       n_iter: int = 5000) -> dict:
    """b holds L_coh/L_inc (n,K) + metric. Pure — --validate plants b."""
    k_all = np.asarray(b.get("k_values", K_VALUES), float)
    L_coh = np.asarray(b["L_coh"], float)
    L_inc = np.asarray(b["L_inc"], float)
    # accumulation region: k≥1 (build amendment — k=0 is SANE only)
    fit_mask = k_all >= 1.0
    k_fit = k_all[fit_mask]
    Lc = L_coh[:, fit_mask]
    Li = L_inc[:, fit_mask]

    coh_slopes = per_nonce_slopes(Lc, k_fit)
    inc_slopes = per_nonce_slopes(Li, k_fit)

    # ── IB1 ACCUMULATION: mean coherent slope > 0 (k-perm null) ──
    ib1_stat = float(coh_slopes.mean())
    ib1_null = NullDraws("k_perm",
                         _slope_perm_null(Lc, k_fit, rng,
                                          min(n_iter, 2000)),
                         {"n_iter": min(n_iter, 2000)})
    ib1 = gate(ib1_stat, ib1_null, "greater", alpha, "IB1_accumulation",
               claim_register=Register.value, probe_register=Register.value)

    # ── IB2 COHERENT-SPECIFIC (make-or-break): slope_coh > slope_inc ──
    ib2_stat = float(np.mean(coh_slopes - inc_slopes))
    ib2_null = paired_permutation(coh_slopes, inc_slopes, rng, n_iter=n_iter)
    ib2 = gate(ib2_stat, ib2_null, "greater", alpha, "IB2_coherent_specific",
               claim_register=Register.value, probe_register=Register.value)

    # ── IB3 NON-SATURATING (non-gating): increments over k≥2 > 0 ──
    # increments L(k)-L(k-1) within the coherent arm; k≥2 = post-first-exposure
    incs = np.diff(Lc, axis=1)                           # (n, len(k_fit)-1)
    per_nonce_inc = incs.mean(axis=1) if incs.shape[1] > 0 else np.zeros(Lc.shape[0])
    ib3_stat = float(per_nonce_inc.mean())
    ib3_null = sign_flip(per_nonce_inc, rng, n_iter=n_iter)
    ib3 = gate(ib3_stat, ib3_null, "greater", alpha, "IB3_non_saturating",
               claim_register=Register.value, probe_register=Register.value)

    # ── IB4 SANE (void-gate) ──
    sane = _sane(b)

    # ── verdict tree (frozen) ──
    if not sane["pass"]:
        verdict = "VOID"
    elif not ib1.verdict:
        verdict = "IDEMPOTENT"
    elif ib2.verdict:
        verdict = "NON-IDEMPOTENT"
    else:
        verdict = "EVIDENCE-ONLY"
    non_saturating = bool(verdict == "NON-IDEMPOTENT" and ib3.verdict)
    display = verdict + (" (+NON-SATURATING)" if non_saturating else "")

    # curve means for reporting
    curve_coh = [float(L_coh[:, j].mean()) for j in range(L_coh.shape[1])]
    curve_inc = [float(L_inc[:, j].mean()) for j in range(L_inc.shape[1])]
    # per-step increments (k=0→1 = first-exposure license; k≥2 = accumulation)
    step_inc = [float(curve_coh[j] - curve_coh[j - 1])
                for j in range(1, len(curve_coh))]

    return {
        "verdict": verdict, "display": display,
        "non_saturating": non_saturating,
        "gates": {
            "IB1": tw._gd(ib1), "IB2": tw._gd(ib2), "IB3": tw._gd(ib3),
            "IB4": sane,
        },
        "means": {
            "coh_slope": ib1_stat, "inc_slope": float(inc_slopes.mean()),
            "slope_gap": ib2_stat,
            "curve_coh": curve_coh, "curve_inc": curve_inc,
            "step_inc_coh": step_inc,
            "first_exposure_license": step_inc[0] if step_inc else 0.0,
            "n_nonce": int(L_coh.shape[0]),
        },
    }


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
def _world_idem(rng, kind: str, n: int = 24) -> dict:
    k = np.array(K_VALUES, float)
    K = len(k)
    labels = np.array([0, 1] * (n // 2))
    b: dict = {"labels": labels, "k_values": list(K_VALUES),
               "metric": {"real_margin": 2.5, "per_class_ok": True}}
    noise = lambda s=0.05: rng.normal(0.0, s, (n, K))    # noqa: E731
    L_coh = noise()
    L_inc = noise()

    def ramp(base: float, slope: float) -> np.ndarray:
        """(n,K): ~0 at k=0, base at k=1, +slope per extra exposure."""
        out = np.zeros((n, K))
        for j in range(1, K):
            out[:, j] = base + slope * (k[j] - 1.0)
        return out + rng.normal(0.0, 0.05, (n, K))

    if kind == "non_idempotent":
        L_coh = ramp(1.0, 0.4)          # licenses + keeps accumulating (k≥1)
        L_inc = noise()                 # incoherent never licenses (~0)
    elif kind == "idempotent":
        # licenses at first exposure, FLAT after (A∧A = A)
        L_coh = np.zeros((n, K))
        L_coh[:, 1:] = 1.0
        L_coh += rng.normal(0.0, 0.05, (n, K))
        L_inc = noise()
    elif kind == "evidence_only":
        # BOTH arms accumulate ~identically (token-budget confound)
        L_coh = ramp(1.0, 0.4)
        L_inc = ramp(1.0, 0.4)          # same slope → IB2 fails
    elif kind == "void":
        L_coh = ramp(1.0, 0.4)
        b["metric"] = {"real_margin": -0.3, "per_class_ok": False}
    else:
        raise ValueError(kind)
    b["L_coh"], b["L_inc"] = L_coh, L_inc
    return b


def run_validate(alpha: float) -> int:
    print("── §P-IDEMPOTENCY --validate (planted worlds, no model) ──")
    want = {"non_idempotent": "NON-IDEMPOTENT",
            "idempotent": "IDEMPOTENT",
            "evidence_only": "EVIDENCE-ONLY",
            "void": "VOID"}
    ok = True
    for kind, expect_v in want.items():
        rng = np.random.default_rng(hash(kind) % (2**31))
        res = compute_gates_idem(_world_idem(rng, kind), rng, alpha,
                                 n_iter=2000)
        good = res["verdict"] == expect_v
        ok &= good
        print(f"  {kind:16s} -> {res['display']:28s} "
              f"expect {expect_v:16s} {'✓' if good else '✗ FAIL'}")

    # ── primitives ──
    # (1) slope recovery
    kf = np.array([1, 2, 3, 4, 5], float)
    y = 2.0 + 0.7 * kf
    prim1 = abs(_ols_slope(y, kf) - 0.7) < 1e-9
    ok &= prim1
    print(f"  primitive ols_slope               {'✓' if prim1 else '✗ FAIL'}")

    # (2) k≥1 restriction: idempotent step-function must NOT pass IB1
    rng = np.random.default_rng(7)
    step = np.zeros((24, len(K_VALUES)))
    step[:, 1:] = 1.0                                    # jump at k=1, flat after
    b_step = {"L_coh": step + rng.normal(0, 0.02, step.shape),
              "L_inc": rng.normal(0, 0.05, step.shape),
              "k_values": list(K_VALUES),
              "metric": {"real_margin": 2.5, "per_class_ok": True}}
    res_step = compute_gates_idem(b_step, rng, alpha, n_iter=2000)
    prim2 = (not res_step["gates"]["IB1"]["pass"]
             and res_step["verdict"] == "IDEMPOTENT")
    ok &= prim2
    print(f"  primitive k≥1 step→IDEMPOTENT      {'✓' if prim2 else '✗ FAIL'}")

    # (3) incoherent arm is membership-free (no class/pred/member word)
    forb = _forbidden_words()
    leak = []
    for w in ("wug", "blicket", "fendle"):
        text = " ".join(incoherent_stmts(w)).lower()
        toks = {t.strip(".,;") for t in text.split()}
        hit = toks & {x.lower() for x in forb}
        if hit:
            leak.append((w, hit))
    prim3 = not leak
    ok &= prim3
    print(f"  primitive incoherent membership-free "
          f"{'✓' if prim3 else '✗ FAIL ' + str(leak)}")

    # (4) coherent/incoherent exposure counts match (token-budget parity)
    prim4 = all(
        coherent_prefix("wug", 0, kk).count(".")
        == incoherent_prefix("wug", 0, kk).count(".")
        for kk in K_VALUES)
    ok &= prim4
    print(f"  primitive exposure-count parity   {'✓' if prim4 else '✗ FAIL'}")

    # (5) non_saturating subtag off when IB3 fails (display omits it)
    rng = np.random.default_rng(11)
    # licenses + accumulates but with a single jump then flat → IB1 may pass,
    # IB3 (mean increment k≥2) near zero; assert display logic on a synthetic
    dsp = compute_gates_idem(_world_idem(np.random.default_rng(3),
                                         "non_idempotent"),
                             np.random.default_rng(3), alpha, n_iter=2000)
    prim5 = ("(+NON-SATURATING)" in dsp["display"]) == dsp["non_saturating"]
    ok &= prim5
    print(f"  primitive subtag display logic    {'✓' if prim5 else '✗ FAIL'}")

    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import torch
    import torch.nn.functional as F
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps"
                           or torch.backends.mps.is_available()) else "cpu")
    rng = np.random.default_rng(args.seed)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[ib] {args.model_id} dev={dev} k={list(K_VALUES)}")

    def surprisal(prefix: str, cont: str) -> float:
        pre = tok(prefix, return_tensors="pt").to(dev)
        full = tok(prefix + cont, return_tensors="pt").to(dev)
        n_pre = pre.input_ids.shape[1]
        with torch.no_grad():
            lo = model(**full).logits[0].float()
        lp = F.log_softmax(lo, dim=-1)
        tgt = full.input_ids[0]
        return -sum(float(lp[pos - 1, tgt[pos]])
                    for pos in range(n_pre, tgt.shape[0]))

    def L_at(prefix: str, w: str, cls_i: int) -> float:
        pre = prefix + f"The {w}"
        sA = np.mean([surprisal(pre, " " + p) for p in tw.HELD_PREDS[0]])
        sV = np.mean([surprisal(pre, " " + p) for p in tw.HELD_PREDS[1]])
        return float(tw._signed_L(np.array([sA]), np.array([sV]),
                                  np.array([cls_i]))[0])

    # ── nonce selection (type_write / type_icl_tag pattern) ──
    nonces, labels = [], []
    for i, w in enumerate(NONCE_CANDS):
        n_the = tok("The", add_special_tokens=False).input_ids
        n_thew = tok(f"The {w}", add_special_tokens=False).input_ids
        if len(n_thew) - len(n_the) >= 1:
            nonces.append(w)
            labels.append(i % 2)
    if args.n_nonce:
        a = [j for j, x in enumerate(labels) if x == 0][:args.n_nonce // 2]
        v = [j for j, x in enumerate(labels) if x == 1][:args.n_nonce // 2]
        sel = sorted(a + v)
        nonces = [nonces[j] for j in sel]
        labels = [labels[j] for j in sel]
    labels = np.array(labels, int)
    print(f"[ib] nonces={len(nonces)} (animal {int((labels == 0).sum())} "
          f"vehicle {int((labels == 1).sum())})")

    # ── real-member anchor (IB4 SANE, bare frames) ──
    real_members = list(tw.REAL_MEMBERS[0]) + list(tw.REAL_MEMBERS[1])
    real_labels = np.array([0] * len(tw.REAL_MEMBERS[0])
                           + [1] * len(tw.REAL_MEMBERS[1]))
    print("[ib] real-member anchor …", flush=True)
    rA, rV = [], []
    for w in real_members:
        pre = f"The {w}"
        rA.append(np.mean([surprisal(pre, " " + p) for p in tw.HELD_PREDS[0]]))
        rV.append(np.mean([surprisal(pre, " " + p) for p in tw.HELD_PREDS[1]]))
    L_real = tw._signed_L(np.array(rA), np.array(rV), real_labels)
    metric = {
        "real_margin": float(np.mean(L_real)),
        "per_class_ok": bool(np.mean(L_real[real_labels == 0]) > 0
                             and np.mean(L_real[real_labels == 1]) > 0),
    }
    print(f"[ib] real margin={metric['real_margin']:.3f} "
          f"per_class_ok={metric['per_class_ok']}")

    # ── exposure-count sweep: L(k) per arm per nonce ──
    K = len(K_VALUES)
    L_coh = np.zeros((len(nonces), K))
    L_inc = np.zeros((len(nonces), K))
    for ni, (w, lb) in enumerate(zip(nonces, labels, strict=True)):
        for kj, kk in enumerate(K_VALUES):
            L_coh[ni, kj] = L_at(coherent_prefix(w, int(lb), kk), w, int(lb))
            L_inc[ni, kj] = L_at(incoherent_prefix(w, int(lb), kk), w, int(lb))
        if (ni + 1) % 5 == 0:
            print(f"[ib] swept {ni + 1}/{len(nonces)} nonces", flush=True)

    b = {"L_coh": L_coh, "L_inc": L_inc, "labels": labels,
         "k_values": list(K_VALUES), "metric": metric}
    res = compute_gates_idem(b, rng, args.alpha)
    res["meta"] = {
        "model_id": args.model_id, "n_nonce": len(nonces),
        "nonces": nonces, "labels": labels.tolist(),
        "k_values": list(K_VALUES), "metric": metric,
        "incoherent_templates": list(_INCOHERENT_TEMPLATES),
    }
    (out_dir / "results.json").write_text(json.dumps(res, indent=2))
    np.savez_compressed(out_dir / "curves.npz",
                        L_coh=L_coh, L_inc=L_inc,
                        labels=labels, k_values=np.array(K_VALUES))
    print(f"[ib] wrote {out_dir}/results.json")
    g, mn = res["gates"], res["means"]
    print(f"[ib] IB1 p={g['IB1']['p']:.4f} {g['IB1']['pass']} | "
          f"IB2 p={g['IB2']['p']:.4f} {g['IB2']['pass']} | "
          f"IB3 p={g['IB3']['p']:.4f} {g['IB3']['pass']} | "
          f"IB4 {g['IB4']['pass']} "
          f"(L0={g['IB4']['L0']:.3f} L1={g['IB4']['L1']:.3f} "
          f"Lmax={g['IB4']['Lmax']:.3f})")
    print(f"[ib] coh_slope={mn['coh_slope']:.4f} inc_slope={mn['inc_slope']:.4f} "
          f"gap={mn['slope_gap']:.4f} | first-exp={mn['first_exposure_license']:.3f}")
    print(f"[ib] curve_coh={[round(x, 3) for x in mn['curve_coh']]}")
    print(f"[ib] curve_inc={[round(x, 3) for x in mn['curve_inc']]}")
    print(f"[ib] VERDICT: {res['display']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--n-nonce", type=int, default=0)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/idempotency/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
