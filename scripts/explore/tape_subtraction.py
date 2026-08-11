#!/usr/bin/env python3
"""§P-TAPE-SUBTRACTION — does contrary tape evidence subtract or pile up?

Pre-reg: mementum/knowledge/explore/types-are-a-modulation-scheme.md
§P-TAPE-SUBTRACTION (FROZEN s328, Michael GO).

The stacked-exposure reframe's first forward contact. A signed integrator
is COMMUTATIVE (3 own + 3 anti net to ~0 regardless of order); early
commitment is ORDER-SENSITIVE (first-committed class survives, primacy);
trivial recency ICL is the mirror (last statements win). The order arms
are content-matched (identical 3 own + 3 anti membership statements, only
sequence differs) so the make-or-break carries no lexical confound.

Register (lambda measure) = LICENSING (value, graded): L = mean
surprisal(anti preds) - mean surprisal(own preds), signed by w's nominal
class c (idempotency _signed_L, the tape face that landed s315). T-register
corroboration (type_icl_tag signed_T) rides along as an advisory second
substrate (TS3).

Construction (nonce w, nominal class c; k_own = 3 fixed, k_anti swept):
  OWN-ONLY      [own x3]                     standing level (TS0 + ref)
  OWN+FILLER    [own x3][filler xk] k in 1,2,3  token-matched dilution
  MIX-OWNFIRST  [own x3][anti xk]   k in 1,2,3  subtraction curve
  MIX-ANTIFIRST [anti x3][own x3]            balanced, anti primacy
  MIX-INTERLEAVED [own,anti,...]             balanced, neutral primacy

Gates: TS0 SANE (void) . TS2 SUBTRACTION-DEPTH (gates NO-EROSION:
L(interleaved,3+3) < L(filler,3+3)) . TS1 ORDER (make-or-break 3-way:
sign of L(own-first) - L(anti-first) at balance, two signed one-sided
gates) . TS3 DC-COROBORATION (advisory, T register).

Verdict tree: ¬TS0 → VOID · ¬TS2 → NO-EROSION · TS2 ∧ TS1>0 →
EARLY-COMMITMENT · TS2 ∧ TS1<0 → RECENCY-BUFFER · TS2 ∧ TS1 order-blind →
SIGNED-INTEGRATOR. A-priori (NOT tuned): SIGNED-INTEGRATOR 30 /
RECENCY-BUFFER 30 / EARLY-COMMITMENT 20 / NO-EROSION 10 / VOID 10.

Reuse (λ one_way, no fork): type_write (_member_stmts, HELD_PREDS, CLASSES,
REAL_MEMBERS, _signed_L, REAL_MARGIN_FLOOR) · idempotency (incoherent_stmts)
· type_icl_tag (signed_T, class_axes, band_layers) · holo_cap (NONCE_CANDS)
· verbum.jlens · verbum.dsp.nulls (gate, NullDraws, paired_permutation).

License: MIT (lambda provenance).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_WRAP = _HERE.parents[1] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

import idempotency as idem  # noqa: E402  (frozen s320 — incoherent filler)
import type_icl_tag as ti  # noqa: E402  (frozen §10 — T instrument)
import type_write as tw  # noqa: E402  (frozen §8 — constants + pure fns)
from holo_cap import NONCE_CANDS  # noqa: E402

from verbum.dsp.nulls import (  # noqa: E402
    Register,
    gate,
    paired_permutation,
)

# ══════════════════════════════════════════════════════════════════════════
# Frozen constants
# ══════════════════════════════════════════════════════════════════════════
K_OWN = 3                       # fixed own-class exposures (idempotency sweet spot)
K_ANTI = (0, 1, 2, 3)           # swept contrary/filler exposures
N_NULL = 10_000
ALPHA = 0.05
APRIORI = {"SIGNED-INTEGRATOR": 30, "RECENCY-BUFFER": 30,
           "EARLY-COMMITMENT": 20, "NO-EROSION": 10, "VOID": 10}


# ══════════════════════════════════════════════════════════════════════════
# Prefix construction (pure) — content-matched order arms
# ══════════════════════════════════════════════════════════════════════════
def own_stmts(w: str, c: int, k: int) -> list[str]:
    return tw._member_stmts(w, c)[:k]


def anti_stmts(w: str, c: int, k: int) -> list[str]:
    return tw._member_stmts(w, 1 - c)[:k]


def filler_stmts(w: str, k: int) -> list[str]:
    return idem.incoherent_stmts(w)[:k]


def _join(stmts: list[str]) -> str:
    return (" ".join(stmts) + " ") if stmts else ""


def own_only_prefix(w: str, c: int) -> str:
    return _join(own_stmts(w, c, K_OWN))


def own_filler_prefix(w: str, c: int, k_anti: int) -> str:
    return _join(own_stmts(w, c, K_OWN) + filler_stmts(w, k_anti))


def mix_ownfirst_prefix(w: str, c: int, k_anti: int) -> str:
    return _join(own_stmts(w, c, K_OWN) + anti_stmts(w, c, k_anti))


def mix_antifirst_prefix(w: str, c: int) -> str:
    return _join(anti_stmts(w, c, K_OWN) + own_stmts(w, c, K_OWN))


def mix_interleaved_prefix(w: str, c: int) -> str:
    o, a = own_stmts(w, c, K_OWN), anti_stmts(w, c, K_OWN)
    seq: list[str] = []
    for j in range(K_OWN):
        seq.append(o[j])
        seq.append(a[j])
    return _join(seq)


# ══════════════════════════════════════════════════════════════════════════
# Gates (pure — --validate plants the bundle; no torch, no model)
# ══════════════════════════════════════════════════════════════════════════
def _sane(b: dict) -> dict:
    """TS0 void-gate: standing own-class license + real anchor + register."""
    L_own_only = np.asarray(b["L_ownfirst"], float)[:, 0]   # k_anti=0 = own-only
    standing = float(L_own_only.mean())
    m = b.get("metric", {})
    real_ok = (m.get("real_margin", 0.0) >= tw.REAL_MARGIN_FLOOR
               and bool(m.get("per_class_ok", False)))
    register_ok = bool(standing > 0.0)
    return {"gate": "TS0", "standing_L": standing, "real_ok": real_ok,
            "register_ok": register_ok,
            "pass": bool(real_ok and register_ok)}


def _ts2(b: dict, rng: np.random.Generator, n_null: int = N_NULL) -> dict:
    """SUBTRACTION-DEPTH: L(filler,3+3) - L(interleaved,3+3) > 0 (erosion)."""
    filler_bal = np.asarray(b["L_filler"], float)[:, -1]    # k_anti=3
    inter = np.asarray(b["L_interleaved"], float)
    obs = float(np.mean(filler_bal - inter))
    null = paired_permutation(filler_bal, inter, rng, n_iter=n_null)
    g = gate(obs, null, "greater", ALPHA, "TS2_subtraction_depth",
             claim_register=Register.value, probe_register=Register.value)
    return {"gate": "TS2", "pass": bool(g.verdict), "erosion": obs, "p": g.p,
            "L_filler_bal": float(filler_bal.mean()),
            "L_interleaved": float(inter.mean())}


def _ts1(b: dict, rng: np.random.Generator, n_null: int = N_NULL) -> dict:
    """ORDER make-or-break (3-way): sign of L(own-first) - L(anti-first).

    Two signed one-sided gates against the same paired null (mutually
    exclusive tails): primacy (>0 -> EARLY-COMMITMENT) vs recency
    (<0 -> RECENCY-BUFFER). Neither -> order-blind -> SIGNED-INTEGRATOR."""
    ownfirst_bal = np.asarray(b["L_ownfirst"], float)[:, -1]   # [own x3][anti x3]
    antifirst = np.asarray(b["L_antifirst"], float)            # [anti x3][own x3]
    obs = float(np.mean(ownfirst_bal - antifirst))
    null = paired_permutation(ownfirst_bal, antifirst, rng, n_iter=n_null)
    g_prim = gate(obs, null, "greater", ALPHA, "TS1_primacy",
                  claim_register=Register.value, probe_register=Register.value)
    g_rec = gate(obs, null, "less", ALPHA, "TS1_recency",
                 claim_register=Register.value, probe_register=Register.value)
    return {"gate": "TS1", "order_diff": obs,
            "L_ownfirst_bal": float(ownfirst_bal.mean()),
            "L_antifirst": float(antifirst.mean()),
            "primacy_p": g_prim.p, "primacy_pass": bool(g_prim.verdict),
            "recency_p": g_rec.p, "recency_pass": bool(g_rec.verdict)}


def _ts3(b: dict) -> dict:
    """DC-COROBORATION (advisory, T register). Signs only — never gates."""
    if "T_ownfirst" not in b:
        return {"gate": "TS3", "advisory": True, "available": False}
    T_ownfirst = np.asarray(b["T_ownfirst"], float)[:, -1]
    T_antifirst = np.asarray(b["T_antifirst"], float)
    T_filler = np.asarray(b["T_filler"], float)[:, -1]
    T_inter = np.asarray(b["T_interleaved"], float)
    return {"gate": "TS3", "advisory": True, "available": True,
            "T_order_diff": float(np.mean(T_ownfirst - T_antifirst)),
            "T_erosion": float(np.mean(T_filler - T_inter)),
            "T_standing": float(np.asarray(b["T_ownfirst"], float)[:, 0].mean())}


def verdict(ts0: dict, ts2: dict, ts1: dict) -> str:
    if not ts0["pass"]:
        return "VOID"
    if not ts2["pass"]:
        return "NO-EROSION"
    if ts1["primacy_pass"]:
        return "EARLY-COMMITMENT"
    if ts1["recency_pass"]:
        return "RECENCY-BUFFER"
    return "SIGNED-INTEGRATOR"


def compute_gates(b: dict, rng: np.random.Generator,
                  n_null: int = N_NULL) -> dict:
    ts0 = _sane(b)
    ts2 = _ts2(b, rng, n_null)
    ts1 = _ts1(b, rng, n_null)
    ts3 = _ts3(b)
    v = verdict(ts0, ts2, ts1)
    # curve means for reporting
    def cm(key):
        return [float(np.asarray(b[key], float)[:, j].mean())
                for j in range(np.asarray(b[key], float).shape[1])]
    return {
        "verdict": v, "a_priori": APRIORI,
        "gates": {"TS0": ts0, "TS1": ts1, "TS2": ts2, "TS3": ts3},
        "means": {
            "curve_ownfirst": cm("L_ownfirst"),   # [own x3][anti xk]
            "curve_filler": cm("L_filler"),        # [own x3][filler xk]
            "L_antifirst": float(np.asarray(b["L_antifirst"], float).mean()),
            "L_interleaved": float(np.asarray(b["L_interleaved"], float).mean()),
            "n_nonce": int(np.asarray(b["L_ownfirst"], float).shape[0]),
        },
    }


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
def _world(rng, kind: str, n: int = 24) -> dict:
    K = len(K_ANTI)
    metric = {"real_margin": 2.5, "per_class_ok": True}
    nz1 = lambda s=0.08: rng.normal(0.0, s, n)           # noqa: E731

    def ramp(start, end):
        """(n,K) linear from start(k=0) to end(k=3) + noise."""
        line = np.linspace(start, end, K)
        return np.tile(line, (n, 1)) + rng.normal(0.0, 0.06, (n, K))

    # baselines shared by all live worlds
    L_filler = ramp(2.0, 1.7)          # mild neutral dilution, stays high
    L_ownfirst = ramp(2.0, 2.0)        # placeholder; balanced endpoint set below
    L_antifirst = 2.0 + nz1()
    L_interleaved = 2.0 + nz1()

    if kind == "signed_integrator":
        L_ownfirst = ramp(2.0, 0.0)    # subtracts to ~0
        L_antifirst = 0.0 + nz1()      # order-blind: same as own-first endpoint
        L_interleaved = 0.0 + nz1()
    elif kind == "early_commitment":
        L_ownfirst = ramp(2.0, 1.7)    # own-first SURVIVES contradiction
        L_antifirst = 0.1 + nz1()      # anti-first erodes own license
        L_interleaved = 0.8 + nz1()    # balanced, below filler
    elif kind == "recency":
        L_ownfirst = ramp(2.0, 0.1)    # own-first erodes (anti is last → last wins)
        L_antifirst = 1.7 + nz1()      # anti-first HIGH (own is last → own wins)
        L_interleaved = 0.8 + nz1()
    elif kind == "no_erosion":
        L_ownfirst = ramp(2.0, 1.75)   # immune
        L_antifirst = 1.75 + nz1()
        L_interleaved = 1.72 + nz1()   # ≈ filler → TS2 fails
    elif kind == "void":
        L_ownfirst = ramp(2.0, 0.0)
        metric = {"real_margin": -0.3, "per_class_ok": False}
    else:
        raise ValueError(kind)

    return {"L_filler": L_filler, "L_ownfirst": L_ownfirst,
            "L_antifirst": L_antifirst, "L_interleaved": L_interleaved,
            "metric": metric}


def run_validate() -> int:
    print("── §P-TAPE-SUBTRACTION --validate (planted worlds, no model) ──")
    want = {"signed_integrator": "SIGNED-INTEGRATOR",
            "early_commitment": "EARLY-COMMITMENT",
            "recency": "RECENCY-BUFFER",
            "no_erosion": "NO-EROSION",
            "void": "VOID"}
    ok = True
    for kind, expect_v in want.items():
        rng = np.random.default_rng(hash(kind) % (2**31))
        res = compute_gates(_world(rng, kind), rng, n_null=2000)
        good = res["verdict"] == expect_v
        ok &= good
        g = res["gates"]
        print(f"  {kind:18s} -> {res['verdict']:18s} expect {expect_v:18s} "
              f"[TS2 p={g['TS2']['p']:.3f} TS1 prim_p={g['TS1']['primacy_p']:.3f} "
              f"rec_p={g['TS1']['recency_p']:.3f}] {'✓' if good else '✗ FAIL'}")

    # ── primitives ──
    w, c = "wug", 0
    # (1) order arms are content-matched multisets (only sequence differs)
    of = own_stmts(w, c, K_OWN) + anti_stmts(w, c, K_OWN)
    af = anti_stmts(w, c, K_OWN) + own_stmts(w, c, K_OWN)
    prim1 = sorted(of) == sorted(af) and of != af
    ok &= prim1
    print(f"  primitive order content-match     {'✓' if prim1 else '✗ FAIL'}")

    # (2) anti statements assert the OTHER class (differ from own)
    prim2 = set(own_stmts(w, c, K_OWN)).isdisjoint(set(anti_stmts(w, c, K_OWN)))
    ok &= prim2
    print(f"  primitive anti≠own                {'✓' if prim2 else '✗ FAIL'}")

    # (3) token-budget parity at balance: ownfirst / antifirst / interleaved
    #     all carry 6 statements; filler-balanced also 6 (3 own + 3 filler)
    def n_stmt(pfx: str) -> int:
        return pfx.count(".")
    bals = [mix_ownfirst_prefix(w, c, K_OWN), mix_antifirst_prefix(w, c),
            mix_interleaved_prefix(w, c), own_filler_prefix(w, c, K_OWN)]
    prim3 = len({n_stmt(p) for p in bals}) == 1 and n_stmt(bals[0]) == 2 * K_OWN
    ok &= prim3
    print(f"  primitive token-budget parity     {'✓' if prim3 else '✗ FAIL'}")

    # (4) own-only == ownfirst(k=0) == filler(k=0) construction identity
    prim4 = (own_only_prefix(w, c) == mix_ownfirst_prefix(w, c, 0)
             == own_filler_prefix(w, c, 0))
    ok &= prim4
    print(f"  primitive own-only k=0 identity   {'✓' if prim4 else '✗ FAIL'}")

    # (5) interleaved alternates own,anti,own,anti,...
    o0 = own_stmts(w, c, K_OWN)[0]
    a0 = anti_stmts(w, c, K_OWN)[0]
    inter = mix_interleaved_prefix(w, c)
    prim5 = inter.index(o0) < inter.index(a0) < inter.index(own_stmts(w, c, K_OWN)[1])
    ok &= prim5
    print(f"  primitive interleave alternation  {'✓' if prim5 else '✗ FAIL'}")

    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import torch
    import torch.nn.functional as F
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from verbum import jlens

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
    nl = jlens.n_layers(model)
    tband = ti.band_layers(nl)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[ts] {args.model_id} dev={dev} n_layers={nl} "
          f"T-band=L{tband[0]}..L{tband[-1]} K_OWN={K_OWN} "
          f"K_ANTI={list(K_ANTI)}", flush=True)

    # ── L instrument (surprisal licensing) ──
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

    def L_at(prefix: str, w: str, c: int) -> float:
        pre = prefix + f"The {w}"
        sA = np.mean([surprisal(pre, " " + p) for p in tw.HELD_PREDS[0]])
        sV = np.mean([surprisal(pre, " " + p) for p in tw.HELD_PREDS[1]])
        return float(tw._signed_L(np.array([sA]), np.array([sV]),
                                  np.array([c]))[0])

    # ── T instrument (class-axis projection at constant probe frame) ──
    def capture_band_at(text: str, positions: list[int]) -> np.ndarray:
        resid, _ids = jlens.capture_residuals(model, tok, text)
        return np.stack([np.stack([resid[li][p].numpy() for li in tband])
                         for p in positions])

    def T_at(prefix: str, w: str, c: int, axes: np.ndarray) -> float:
        text = prefix + f"The {w}"
        pos = len(tok(text).input_ids) - 1        # last token (= w)
        h = capture_band_at(text, [pos])          # (1, L, d)
        return float(ti.signed_T(h, axes, np.array([c]))[0])

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
    print(f"[ts] nonces={len(nonces)} (animal {int((labels == 0).sum())} "
          f"vehicle {int((labels == 1).sum())})", flush=True)

    # ── real-member class axes (T) + licensing anchor (L, TS0 SANE) ──
    real_members = list(tw.REAL_MEMBERS[0]) + list(tw.REAL_MEMBERS[1])
    real_labels = np.array([0] * len(tw.REAL_MEMBERS[0])
                           + [1] * len(tw.REAL_MEMBERS[1]))
    print("[ts] real-member anchor + axes …", flush=True)
    rA, rV, h_members = [], [], []
    for w in real_members:
        pre = f"The {w}"
        rA.append(np.mean([surprisal(pre, " " + p) for p in tw.HELD_PREDS[0]]))
        rV.append(np.mean([surprisal(pre, " " + p) for p in tw.HELD_PREDS[1]]))
        h_members.append(capture_band_at(pre, [len(tok(pre).input_ids) - 1])[0])
    L_real = tw._signed_L(np.array(rA), np.array(rV), real_labels)
    metric = {
        "real_margin": float(np.mean(L_real)),
        "per_class_ok": bool(np.mean(L_real[real_labels == 0]) > 0
                             and np.mean(L_real[real_labels == 1]) > 0),
    }
    axes = ti.class_axes(np.stack(h_members), real_labels)
    print(f"[ts] real margin={metric['real_margin']:.3f} "
          f"per_class_ok={metric['per_class_ok']}", flush=True)

    # ── sweep: L (+ T) per arm per nonce ──
    K = len(K_ANTI)
    L_filler = np.zeros((len(nonces), K))
    L_ownfirst = np.zeros((len(nonces), K))
    L_antifirst = np.zeros(len(nonces))
    L_interleaved = np.zeros(len(nonces))
    T_filler = np.zeros((len(nonces), K))
    T_ownfirst = np.zeros((len(nonces), K))
    T_antifirst = np.zeros(len(nonces))
    T_interleaved = np.zeros(len(nonces))
    t0 = time.time()
    for ni, (w, lb) in enumerate(zip(nonces, labels, strict=True)):
        c = int(lb)
        for kj, kk in enumerate(K_ANTI):
            L_filler[ni, kj] = L_at(own_filler_prefix(w, c, kk), w, c)
            L_ownfirst[ni, kj] = L_at(mix_ownfirst_prefix(w, c, kk), w, c)
            T_filler[ni, kj] = T_at(own_filler_prefix(w, c, kk), w, c, axes)
            T_ownfirst[ni, kj] = T_at(mix_ownfirst_prefix(w, c, kk), w, c, axes)
        L_antifirst[ni] = L_at(mix_antifirst_prefix(w, c), w, c)
        L_interleaved[ni] = L_at(mix_interleaved_prefix(w, c), w, c)
        T_antifirst[ni] = T_at(mix_antifirst_prefix(w, c), w, c, axes)
        T_interleaved[ni] = T_at(mix_interleaved_prefix(w, c), w, c, axes)
        if (ni + 1) % 4 == 0:
            print(f"[ts] swept {ni + 1}/{len(nonces)} "
                  f"({time.time() - t0:.0f}s)", flush=True)

    b = {"L_filler": L_filler, "L_ownfirst": L_ownfirst,
         "L_antifirst": L_antifirst, "L_interleaved": L_interleaved,
         "T_filler": T_filler, "T_ownfirst": T_ownfirst,
         "T_antifirst": T_antifirst, "T_interleaved": T_interleaved,
         "metric": metric}
    res = compute_gates(b, rng, n_null=args.n_null)
    res["meta"] = {
        "model_id": args.model_id, "n_nonce": len(nonces),
        "nonces": nonces, "labels": labels.tolist(),
        "k_own": K_OWN, "k_anti": list(K_ANTI), "band": [tband[0], tband[-1]],
        "metric": metric, "n_null": args.n_null,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_s": round(time.time() - t0, 1),
    }
    (out_dir / "results.json").write_text(json.dumps(res, indent=2))
    np.savez_compressed(
        out_dir / "curves.npz",
        L_filler=L_filler, L_ownfirst=L_ownfirst, L_antifirst=L_antifirst,
        L_interleaved=L_interleaved, T_filler=T_filler, T_ownfirst=T_ownfirst,
        T_antifirst=T_antifirst, T_interleaved=T_interleaved,
        labels=labels, k_anti=np.array(K_ANTI))

    g, mn = res["gates"], res["means"]
    print(f"[ts] wrote {out_dir}/results.json")
    print(f"[ts] TS0 {g['TS0']['pass']} (standing_L={g['TS0']['standing_L']:.3f}"
          f" real_ok={g['TS0']['real_ok']}) | "
          f"TS2 erosion={g['TS2']['erosion']:.3f} p={g['TS2']['p']:.4f} "
          f"{g['TS2']['pass']}")
    print(f"[ts] TS1 order_diff={g['TS1']['order_diff']:.3f} "
          f"(ownfirst={g['TS1']['L_ownfirst_bal']:.3f} "
          f"antifirst={g['TS1']['L_antifirst']:.3f}) "
          f"primacy_p={g['TS1']['primacy_p']:.4f} "
          f"recency_p={g['TS1']['recency_p']:.4f}")
    print(f"[ts] curve_ownfirst={[round(x, 3) for x in mn['curve_ownfirst']]}")
    print(f"[ts] curve_filler  ={[round(x, 3) for x in mn['curve_filler']]}")
    print(f"[ts] L_antifirst={mn['L_antifirst']:.3f} "
          f"L_interleaved={mn['L_interleaved']:.3f}")
    if g["TS3"].get("available"):
        print(f"[ts] TS3(T) order_diff={g['TS3']['T_order_diff']:.3f} "
              f"erosion={g['TS3']['T_erosion']:.3f} "
              f"standing={g['TS3']['T_standing']:.3f}")
    print(f"[ts] VERDICT: {res['verdict']}")
    print(f"VERDICT: {res['verdict']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--n-nonce", type=int, default=0)
    ap.add_argument("--n-null", type=int, default=N_NULL)
    ap.add_argument("--seed", type=int, default=328)
    ap.add_argument("--out", default="results/tape-subtraction/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate()
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
