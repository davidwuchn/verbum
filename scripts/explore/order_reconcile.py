#!/usr/bin/env python3
"""§P-ORDER-RECONCILE — locate the s328 L-vs-T order-sign split.

Pre-reg: mementum/knowledge/explore/types-are-a-modulation-scheme.md
§P-ORDER-RECONCILE (FROZEN s329, Michael GO).

s328 §P-TAPE-SUBTRACTION found PRIMACY on the behavioral licensing L
(order_diff +0.478) and RECENCY on the class-axis T (-1.30) on the SAME
prefixes. The position mismatch is nearly nil (L's first-pred surprisal
reads the logits AT `w` — the same token T reads), so the instrument gap
is exactly a 2x2 crossing {readout: unembed-surprisal vs class-axis} x
{depth: final vs band}. This probe fills the two missing cells:

  cell A = LL(band)  — logit-lens L (per-layer residual -> final norm +
                       unembed -> held-pred surprisal -> _signed_L),
                       aggregated over the same band T uses
  cell B = T(final)  — class-axis projection at the final layer,
                       per-layer axes from the same real members

Identity anchor: LL(final) == L (same computation; checked vs the direct
logits path on the own-only arm).

Gates: OR0 SANE/replicate (anchor + identity + s328 endpoint signs on the
same 20 nonces) . OR1 CROSSING make-or-break (A<0 ∧ B>0 -> DEPTH-COMMITMENT
· A>0 ∧ B<0 -> REGISTER-DISSOCIATION · else ENTANGLED-PARTIAL) . OR2 depth
profiles + commitment depth l* (advisory) . OR3 RECENCY KERNEL secondary
(single-anti slot sweep [a,o,o,o]..[o,o,o,a] at 3:1 own-dominance;
stat = L(anti@slot1) - L(anti@slot4), >0 = trailing hurts most).

A-priori (NOT tuned): DEPTH-COMMITMENT 30 / ENTANGLED-PARTIAL 30 /
REGISTER-DISSOCIATION 20 / SPLIT-NOT-REPLICATED 10 / VOID 10.

Reuse (λ one_way, no fork): tape_subtraction (arm builders, K_OWN) ·
type_write (_signed_L, HELD_PREDS, REAL_MEMBERS, REAL_MARGIN_FLOOR) ·
type_icl_tag (class_axes, band_layers, signed_T sign convention) ·
holo_cap (NONCE_CANDS, same deterministic selection) · verbum.jlens
(capture_residuals, logit_lens) · verbum.dsp.nulls (gate,
paired_permutation).

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

import tape_subtraction as ts  # noqa: E402  (frozen s328 — arm builders)
import type_icl_tag as ti  # noqa: E402  (frozen §10 — axes + band)
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
K_OWN = ts.K_OWN                 # 3 (s328)
N_SLOTS = K_OWN + 1              # single-anti slot sweep positions
N_NULL = 10_000
ALPHA = 0.05
IDENT_MEAN_TOL = 0.05            # LL(final) vs direct-L fidelity (nats)
IDENT_MAX_TOL = 0.25
APRIORI = {"DEPTH-COMMITMENT": 30, "ENTANGLED-PARTIAL": 30,
           "REGISTER-DISSOCIATION": 20, "SPLIT-NOT-REPLICATED": 10,
           "VOID": 10}


# ══════════════════════════════════════════════════════════════════════════
# Arm construction (pure) — balanced arms are literal s328 reuse
# ══════════════════════════════════════════════════════════════════════════
def slot_stmts(w: str, c: int, slot: int) -> list[str]:
    """[own x3] with ONE anti inserted at `slot` (0..3)."""
    seq = ts.own_stmts(w, c, K_OWN)
    seq.insert(slot, ts.anti_stmts(w, c, 1)[0])
    return seq


def slot_prefix(w: str, c: int, slot: int) -> str:
    """Slot arm prefix. slot=3 is the trailing-anti arm ==
    ts.mix_ownfirst_prefix(w, c, 1)."""
    return ts._join(slot_stmts(w, c, slot))


ARM_BUILDERS = {
    "own_only": lambda w, c: ts.own_only_prefix(w, c),
    "filler_bal": lambda w, c: ts.own_filler_prefix(w, c, K_OWN),
    "ownfirst_bal": lambda w, c: ts.mix_ownfirst_prefix(w, c, K_OWN),
    "antifirst": lambda w, c: ts.mix_antifirst_prefix(w, c),
    "interleaved": lambda w, c: ts.mix_interleaved_prefix(w, c),
}


# ══════════════════════════════════════════════════════════════════════════
# Gates (pure — --validate plants the bundle; no torch, no model)
#
# Bundle b keys (n = nonces, nl = layers):
#   LL_own_only/LL_filler/LL_ownfirst/LL_antifirst/LL_inter : (n, nl)
#   T_ownfirst/T_antifirst : (n, nl)
#   LL_slot/T_slot : (n, N_SLOTS, nl)
#   band_idx : list[int] (band layer indices) | metric : dict
# ══════════════════════════════════════════════════════════════════════════
def _band_mean(a: np.ndarray, band_idx: list[int]) -> np.ndarray:
    return np.asarray(a, float)[..., band_idx].mean(axis=-1)


def _or0(b: dict, rng: np.random.Generator, n_null: int = N_NULL) -> dict:
    """SANE/replicate: anchor + LL(final)==L identity + s328 endpoint signs."""
    m = b.get("metric", {})
    band = b["band_idx"]
    standing = float(np.asarray(b["LL_own_only"], float)[:, -1].mean())
    anchor_ok = bool(
        m.get("real_margin", 0.0) >= tw.REAL_MARGIN_FLOOR
        and m.get("per_class_ok", False)
        and standing > 0.0
        and m.get("ident_mean", np.inf) <= IDENT_MEAN_TOL
        and m.get("ident_max", np.inf) <= IDENT_MAX_TOL)

    d_l_final = (np.asarray(b["LL_ownfirst"], float)[:, -1]
                 - np.asarray(b["LL_antifirst"], float)[:, -1])
    null_l = paired_permutation(
        np.asarray(b["LL_ownfirst"], float)[:, -1],
        np.asarray(b["LL_antifirst"], float)[:, -1], rng, n_iter=n_null)
    g_l = gate(float(d_l_final.mean()), null_l, "greater", ALPHA,
               "OR0_L_final_primacy",
               claim_register=Register.value, probe_register=Register.value)

    t_own_b = _band_mean(b["T_ownfirst"], band)
    t_anti_b = _band_mean(b["T_antifirst"], band)
    null_t = paired_permutation(t_own_b, t_anti_b, rng, n_iter=n_null)
    g_t = gate(float((t_own_b - t_anti_b).mean()), null_t, "less", ALPHA,
               "OR0_T_band_recency",
               claim_register=Register.value, probe_register=Register.value)

    return {"gate": "OR0", "anchor_ok": anchor_ok, "standing_LL": standing,
            "D_L_final": float(d_l_final.mean()), "L_final_p": g_l.p,
            "L_final_primacy": bool(g_l.verdict),
            "D_T_band": float((t_own_b - t_anti_b).mean()), "T_band_p": g_t.p,
            "T_band_recency": bool(g_t.verdict),
            "replication_ok": bool(g_l.verdict and g_t.verdict),
            "pass": bool(anchor_ok and g_l.verdict and g_t.verdict)}


def _or1(b: dict, rng: np.random.Generator, n_null: int = N_NULL) -> dict:
    """CROSSING make-or-break: cell A = LL(band), cell B = T(final)."""
    band = b["band_idx"]
    a_own = _band_mean(b["LL_ownfirst"], band)
    a_anti = _band_mean(b["LL_antifirst"], band)
    obs_a = float((a_own - a_anti).mean())
    null_a = paired_permutation(a_own, a_anti, rng, n_iter=n_null)
    g_a_neg = gate(obs_a, null_a, "less", ALPHA, "OR1_A_LL_band_recency",
                   claim_register=Register.value, probe_register=Register.value)
    g_a_pos = gate(obs_a, null_a, "greater", ALPHA, "OR1_A_LL_band_primacy",
                   claim_register=Register.value, probe_register=Register.value)

    b_own = np.asarray(b["T_ownfirst"], float)[:, -1]
    b_anti = np.asarray(b["T_antifirst"], float)[:, -1]
    obs_b = float((b_own - b_anti).mean())
    null_b = paired_permutation(b_own, b_anti, rng, n_iter=n_null)
    g_b_pos = gate(obs_b, null_b, "greater", ALPHA, "OR1_B_T_final_primacy",
                   claim_register=Register.value, probe_register=Register.value)
    g_b_neg = gate(obs_b, null_b, "less", ALPHA, "OR1_B_T_final_recency",
                   claim_register=Register.value, probe_register=Register.value)

    return {"gate": "OR1",
            "A_LL_band": obs_a, "A_neg_p": g_a_neg.p, "A_pos_p": g_a_pos.p,
            "A_neg": bool(g_a_neg.verdict), "A_pos": bool(g_a_pos.verdict),
            "B_T_final": obs_b, "B_pos_p": g_b_pos.p, "B_neg_p": g_b_neg.p,
            "B_pos": bool(g_b_pos.verdict), "B_neg": bool(g_b_neg.verdict)}


def _or2(b: dict) -> dict:
    """Depth profiles (advisory): per-layer order diffs + commitment depth."""
    d_ll = (np.asarray(b["LL_ownfirst"], float)
            - np.asarray(b["LL_antifirst"], float)).mean(axis=0)
    d_t = (np.asarray(b["T_ownfirst"], float)
           - np.asarray(b["T_antifirst"], float)).mean(axis=0)

    def commit_layer(prof: np.ndarray) -> int | None:
        pos = prof > 0
        for li in range(len(prof)):
            if pos[li:].all():
                return li
        return None

    return {"gate": "OR2", "advisory": True,
            "D_LL_profile": [round(float(x), 4) for x in d_ll],
            "D_T_profile": [round(float(x), 4) for x in d_t],
            "commit_layer_LL": commit_layer(d_ll),
            "commit_layer_T": commit_layer(d_t)}


def _or3(b: dict, rng: np.random.Generator, n_null: int = N_NULL) -> dict:
    """RECENCY KERNEL secondary: L(anti@slot0) - L(anti@slot3) at final.
    >0 sig = trailing contradiction hurts most (within-arm recency)."""
    band = b["band_idx"]
    early = np.asarray(b["LL_slot"], float)[:, 0, -1]
    late = np.asarray(b["LL_slot"], float)[:, -1, -1]
    obs = float((early - late).mean())
    null = paired_permutation(early, late, rng, n_iter=n_null)
    g = gate(obs, null, "greater", ALPHA, "OR3_recency_kernel",
             claim_register=Register.value, probe_register=Register.value)
    slot_curve = [float(np.asarray(b["LL_slot"], float)[:, j, -1].mean())
                  for j in range(np.asarray(b["LL_slot"]).shape[1])]
    t_early = _band_mean(np.asarray(b["T_slot"], float)[:, 0, :], band)
    t_late = _band_mean(np.asarray(b["T_slot"], float)[:, -1, :], band)
    return {"gate": "OR3", "secondary": True, "kernel": obs, "p": g.p,
            "pass": bool(g.verdict),
            "slot_curve_L_final": slot_curve,
            "T_band_kernel_advisory": float((t_early - t_late).mean())}


def verdict(or0: dict, or1: dict) -> str:
    if not or0["anchor_ok"]:
        return "VOID"
    if not or0["replication_ok"]:
        return "SPLIT-NOT-REPLICATED"
    if or1["A_neg"] and or1["B_pos"]:
        return "DEPTH-COMMITMENT"
    if or1["A_pos"] and or1["B_neg"]:
        return "REGISTER-DISSOCIATION"
    return "ENTANGLED-PARTIAL"


def compute_gates(b: dict, rng: np.random.Generator,
                  n_null: int = N_NULL) -> dict:
    or0 = _or0(b, rng, n_null)
    or1 = _or1(b, rng, n_null)
    or2 = _or2(b)
    or3 = _or3(b, rng, n_null)
    return {"verdict": verdict(or0, or1), "a_priori": APRIORI,
            "gates": {"OR0": or0, "OR1": or1, "OR2": or2, "OR3": or3}}


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
_NL, _N = 36, 24


def _world(rng, kind: str) -> dict:
    nl, n = _NL, _N
    band = ti.band_layers(nl)
    metric = {"real_margin": 2.5, "per_class_ok": True,
              "ident_mean": 0.005, "ident_max": 0.02}

    def base(level=0.5):
        return level + rng.normal(0.0, 0.08, (n, nl))

    def with_profile(anti: np.ndarray, prof: np.ndarray) -> np.ndarray:
        return anti + prof[None, :] + rng.normal(0.0, 0.06, (n, nl))

    flat = lambda v: np.full(nl, float(v))                    # noqa: E731
    late_flip = np.where(np.arange(nl) >= int(0.90 * nl), 0.9, -0.8)

    # kernel slots: recency (trailing hurts most) unless overridden
    slot_levels = np.array([1.5, 0.8, 0.3, -0.1])

    if kind == "depth_commitment":
        d_ll, d_t = late_flip, late_flip
    elif kind == "register_dissociation":
        d_ll, d_t = flat(0.8), flat(-0.8)
        slot_levels = np.array([0.5, 0.5, 0.5, 0.5])          # flat kernel
    elif kind == "entangled":
        d_ll = np.where(np.arange(nl) >= int(0.90 * nl), 0.9, 0.0)  # A ns
        d_t = flat(-0.8)                                       # B neg
    elif kind == "split_not_replicated":
        d_ll, d_t = flat(0.8), flat(0.5)                       # T band wrong sign
    elif kind == "void":
        d_ll, d_t = late_flip, late_flip
        metric = {"real_margin": -0.3, "per_class_ok": False,
                  "ident_mean": 0.4, "ident_max": 2.0}
    else:
        raise ValueError(kind)

    ll_anti, t_anti = base(0.2), base(-0.2)
    ll_slot = np.stack([1.0 + lv + rng.normal(0.0, 0.06, (n, nl))
                        for lv in slot_levels], axis=1)
    t_slot = np.stack([0.5 * lv + rng.normal(0.0, 0.06, (n, nl))
                       for lv in slot_levels], axis=1)
    return {"LL_own_only": base(2.0), "LL_filler": base(1.8),
            "LL_inter": base(0.8),
            "LL_ownfirst": with_profile(ll_anti, d_ll), "LL_antifirst": ll_anti,
            "T_ownfirst": with_profile(t_anti, d_t), "T_antifirst": t_anti,
            "LL_slot": ll_slot, "T_slot": t_slot,
            "band_idx": band, "metric": metric}


def run_validate() -> int:
    print("── §P-ORDER-RECONCILE --validate (planted worlds, no model) ──")
    want = {"depth_commitment": "DEPTH-COMMITMENT",
            "register_dissociation": "REGISTER-DISSOCIATION",
            "entangled": "ENTANGLED-PARTIAL",
            "split_not_replicated": "SPLIT-NOT-REPLICATED",
            "void": "VOID"}
    kernel_want = {"depth_commitment": True, "register_dissociation": False}
    ok = True
    for kind, expect_v in want.items():
        rng = np.random.default_rng(hash(kind) % (2**31))
        res = compute_gates(_world(rng, kind), rng, n_null=2000)
        good = res["verdict"] == expect_v
        if kind in kernel_want:
            good &= res["gates"]["OR3"]["pass"] == kernel_want[kind]
        ok &= good
        g = res["gates"]
        print(f"  {kind:22s} -> {res['verdict']:22s} expect {expect_v:22s} "
              f"[A={g['OR1']['A_LL_band']:+.2f} B={g['OR1']['B_T_final']:+.2f} "
              f"OR3={g['OR3']['pass']}] {'✓' if good else '✗ FAIL'}")

    # ── construction primitives ──
    w, c = "wug", 0
    # (1) slot arms are content-matched multisets (only slot differs)
    slot_lists = [slot_stmts(w, c, s) for s in range(N_SLOTS)]
    prim1 = (len({tuple(sorted(sl)) for sl in slot_lists}) == 1
             and len({tuple(sl) for sl in slot_lists}) == N_SLOTS)
    ok &= prim1
    print(f"  primitive slot content-match      {'✓' if prim1 else '✗ FAIL'}")

    # (2) trailing-anti slot == s328 ownfirst k_anti=1 (construction identity)
    prim2 = slot_prefix(w, c, K_OWN) == ts.mix_ownfirst_prefix(w, c, 1)
    ok &= prim2
    print(f"  primitive slot3 ≡ ownfirst(k=1)   {'✓' if prim2 else '✗ FAIL'}")

    # (3) balanced arms are the literal s328 builders (content-matched pair)
    of_l = ts.own_stmts(w, c, K_OWN) + ts.anti_stmts(w, c, K_OWN)
    af_l = ts.anti_stmts(w, c, K_OWN) + ts.own_stmts(w, c, K_OWN)
    prim3 = (sorted(of_l) == sorted(af_l) and of_l != af_l
             and ARM_BUILDERS["ownfirst_bal"](w, c) == ts._join(of_l)
             and ARM_BUILDERS["antifirst"](w, c) == ts._join(af_l))
    ok &= prim3
    print(f"  primitive balanced content-match  {'✓' if prim3 else '✗ FAIL'}")

    # (4) band excludes the final layer (the crossing has two depths)
    band = ti.band_layers(_NL)
    prim4 = max(band) < _NL - 1 and min(band) > 0
    ok &= prim4
    print(f"  primitive band ≠ final depth      {'✓' if prim4 else '✗ FAIL'}")

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
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    nl = jlens.n_layers(model)
    band = ti.band_layers(nl)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[or] {args.model_id} dev={dev} n_layers={nl} "
          f"band=L{band[0]}..L{band[-1]} final=L{nl - 1} "
          f"slots={N_SLOTS}", flush=True)

    # ── direct-logits surprisal (s328 instrument, for anchor + identity) ──
    def surprisal_direct(prefix: str, cont: str) -> float:
        pre = tok(prefix, return_tensors="pt").to(dev)
        full = tok(prefix + cont, return_tensors="pt").to(dev)
        n_pre = pre.input_ids.shape[1]
        with torch.no_grad():
            lo = model(**full).logits[0].float()
        lp = F.log_softmax(lo, dim=-1)
        tgt = full.input_ids[0]
        return -sum(float(lp[pos - 1, tgt[pos]])
                    for pos in range(n_pre, tgt.shape[0]))

    def L_direct(prefix: str, w: str, c: int) -> float:
        pre = prefix + f"The {w}"
        sA = np.mean([surprisal_direct(pre, " " + p) for p in tw.HELD_PREDS[0]])
        sV = np.mean([surprisal_direct(pre, " " + p) for p in tw.HELD_PREDS[1]])
        return float(tw._signed_L(np.array([sA]), np.array([sV]),
                                  np.array([c]))[0])

    # ── per-layer instruments (one capture per pred continuation) ──
    def t_layers(h_w: np.ndarray, axes: np.ndarray, c: int) -> np.ndarray:
        """Per-layer signed axis projection (ti.signed_T sans band mean)."""
        proj = np.einsum("ld,ld->l", h_w, axes)
        return proj * (1.0 if c == 0 else -1.0)

    def ll_t_at(prefix: str, w: str, c: int,
                axes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Returns (LL per layer (nl,), T per layer (nl,)) for one arm."""
        pre_text = prefix + f"The {w}"
        n_pre = len(tok(pre_text).input_ids)
        s_cls = np.zeros((2, nl))
        t_vec: np.ndarray | None = None
        for cls_j, preds in enumerate(tw.HELD_PREDS):
            for p in preds:
                resid, ids = jlens.capture_residuals(
                    model, tok, pre_text + " " + p)
                n_full = ids.shape[0]
                tgt = ids[n_pre:n_full]
                states = torch.stack(
                    [resid[li][n_pre - 1:n_full - 1] for li in range(nl)])
                logits = jlens.logit_lens(model, states)      # (nl, t, vocab)
                lp = torch.log_softmax(logits.float(), dim=-1).cpu()
                s_l = -lp[:, torch.arange(tgt.shape[0]), tgt].sum(dim=1)
                s_cls[cls_j] += s_l.numpy() / len(preds)
                if t_vec is None:
                    h_w = np.stack([resid[li][n_pre - 1].numpy()
                                    for li in range(nl)])
                    t_vec = t_layers(h_w, axes, c)
        ll = tw._signed_L(s_cls[0], s_cls[1], np.full(nl, c, int))
        assert t_vec is not None
        return np.asarray(ll, float), t_vec

    # ── nonce selection (identical to s328 tape_subtraction) ──
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
    print(f"[or] nonces={len(nonces)} (animal {int((labels == 0).sum())} "
          f"vehicle {int((labels == 1).sum())})", flush=True)

    # ── real members: anchor (direct L) + per-layer class axes ──
    real_members = list(tw.REAL_MEMBERS[0]) + list(tw.REAL_MEMBERS[1])
    real_labels = np.array([0] * len(tw.REAL_MEMBERS[0])
                           + [1] * len(tw.REAL_MEMBERS[1]))
    print("[or] real-member anchor + per-layer axes …", flush=True)
    rA, rV, h_members = [], [], []
    for w in real_members:
        pre = f"The {w}"
        rA.append(np.mean([surprisal_direct(pre, " " + p)
                           for p in tw.HELD_PREDS[0]]))
        rV.append(np.mean([surprisal_direct(pre, " " + p)
                           for p in tw.HELD_PREDS[1]]))
        resid, ids = jlens.capture_residuals(model, tok, pre)
        h_members.append(np.stack([resid[li][ids.shape[0] - 1].numpy()
                                   for li in range(nl)]))
    L_real = tw._signed_L(np.array(rA), np.array(rV), real_labels)
    metric = {
        "real_margin": float(np.mean(L_real)),
        "per_class_ok": bool(np.mean(L_real[real_labels == 0]) > 0
                             and np.mean(L_real[real_labels == 1]) > 0),
    }
    axes = ti.class_axes(np.stack(h_members), real_labels)    # (nl, d)
    print(f"[or] real margin={metric['real_margin']:.3f} "
          f"per_class_ok={metric['per_class_ok']}", flush=True)

    # ── sweep: per-layer LL + T on every arm ──
    n = len(nonces)
    named = {k: np.zeros((n, nl)) for k in
             ["LL_own_only", "LL_filler", "LL_ownfirst", "LL_antifirst",
              "LL_inter", "T_own_only", "T_filler", "T_ownfirst",
              "T_antifirst", "T_inter"]}
    LL_slot = np.zeros((n, N_SLOTS, nl))
    T_slot = np.zeros((n, N_SLOTS, nl))
    ident_diffs = np.zeros(n)
    arm_keys = {"own_only": "own_only", "filler_bal": "filler",
                "ownfirst_bal": "ownfirst", "antifirst": "antifirst",
                "interleaved": "inter"}
    t0 = time.time()
    for ni, (w, lb) in enumerate(zip(nonces, labels, strict=True)):
        c = int(lb)
        for arm, key in arm_keys.items():
            ll, tv = ll_t_at(ARM_BUILDERS[arm](w, c), w, c, axes)
            named[f"LL_{key}"][ni] = ll
            named[f"T_{key}"][ni] = tv
        for s in range(N_SLOTS):
            ll, tv = ll_t_at(slot_prefix(w, c, s), w, c, axes)
            LL_slot[ni, s] = ll
            T_slot[ni, s] = tv
        # identity: LL(final) vs the direct s328 instrument, own-only arm
        ident_diffs[ni] = abs(named["LL_own_only"][ni, -1]
                              - L_direct(ARM_BUILDERS["own_only"](w, c), w, c))
        if (ni + 1) % 2 == 0:
            print(f"[or] swept {ni + 1}/{n} ({time.time() - t0:.0f}s)",
                  flush=True)
    metric["ident_mean"] = float(ident_diffs.mean())
    metric["ident_max"] = float(ident_diffs.max())
    print(f"[or] identity LL(final)≡L: mean={metric['ident_mean']:.4f} "
          f"max={metric['ident_max']:.4f}", flush=True)

    b = {**{k: v for k, v in named.items()},
         "LL_slot": LL_slot, "T_slot": T_slot,
         "band_idx": band, "metric": metric}
    res = compute_gates(b, rng, n_null=args.n_null)
    res["meta"] = {
        "model_id": args.model_id, "n_nonce": n, "nonces": nonces,
        "labels": labels.tolist(), "k_own": K_OWN, "n_slots": N_SLOTS,
        "band": [band[0], band[-1]], "final_layer": nl - 1,
        "metric": metric, "n_null": args.n_null, "seed": args.seed,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_s": round(time.time() - t0, 1),
    }
    (out_dir / "results.json").write_text(json.dumps(res, indent=2))
    np.savez_compressed(out_dir / "curves.npz",
                        **named, LL_slot=LL_slot, T_slot=T_slot,
                        labels=labels, band_idx=np.array(band))

    g = res["gates"]
    print(f"[or] wrote {out_dir}/results.json")
    print(f"[or] OR0 pass={g['OR0']['pass']} anchor={g['OR0']['anchor_ok']} "
          f"D_L_final={g['OR0']['D_L_final']:+.3f} (p={g['OR0']['L_final_p']:.4f}) "
          f"D_T_band={g['OR0']['D_T_band']:+.3f} (p={g['OR0']['T_band_p']:.4f})")
    print(f"[or] OR1 A_LL_band={g['OR1']['A_LL_band']:+.3f} "
          f"(neg_p={g['OR1']['A_neg_p']:.4f} pos_p={g['OR1']['A_pos_p']:.4f}) "
          f"B_T_final={g['OR1']['B_T_final']:+.3f} "
          f"(pos_p={g['OR1']['B_pos_p']:.4f} neg_p={g['OR1']['B_neg_p']:.4f})")
    print(f"[or] OR2 commit_layer_LL={g['OR2']['commit_layer_LL']} "
          f"commit_layer_T={g['OR2']['commit_layer_T']}")
    print(f"[or] OR3 kernel={g['OR3']['kernel']:+.3f} p={g['OR3']['p']:.4f} "
          f"pass={g['OR3']['pass']} "
          f"slot_curve={[round(x, 3) for x in g['OR3']['slot_curve_L_final']]}")
    print(f"[or] VERDICT: {res['verdict']}")
    print(f"VERDICT: {res['verdict']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--n-nonce", type=int, default=20)
    ap.add_argument("--n-null", type=int, default=N_NULL)
    ap.add_argument("--seed", type=int, default=329)
    ap.add_argument("--out", default="results/order-reconcile/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate()
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
