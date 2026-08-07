#!/usr/bin/env python3
"""§P-TYPE-DELIVER — the causal delivery-path write (band-swap, co-primary OV+QK).

Pre-reg: mementum/knowledge/explore/types-are-injectable-relations.md §12
(FROZEN s316, Michael-approved GO).

§9 baked nonce→class MEMBERSHIP into the FFN band: recall p=5e-4 but the
type does NOT act (CONTEXT-ONLY) and the class tag never transits (§11 A5
r_tag=0.137, DELIVERY-FAILURE). §11 proved the TAPE delivers — type info
acts iff it transits the residual bus. This probe asks the causal question
§11 opened: can a STATIC WEIGHT WRITE install delivery, and WHICH band?

SINGLE FACTOR. Hold the §8 membership-CE objective + s315 corridor
(kl_weight 10 / ce_budget 0.40) + band depth (0.60-0.80) + recipe (r=16,
lr 1e-4, 500 steps, 3 seeds) VERBATIM. Vary ONLY the LoRA target band:
  A1 FFN  = mlp.{gate,up,down}_proj   (= §9 recipe; DELIVERY-FAILURE anchor)
  A2 OV   = self_attn.{v_proj,o_proj} (content/delivery channel; P-ATT-MED)
  A3 QK   = self_attn.{q_proj,k_proj} (routing/aim channel)
Deranged (anti-class) control per DELIVERY channel (a2d/a3d), matched budget.
A0 base = no wire. A4 real-member anchor = gate-0 (metric validity, TD6).

Registers named (λ measure): L = value register (§8 surprisal contrast,
`_signed_L`); T = residual-CONTENT register (§11: signed projection at the
last token of "The {w}" onto the real-member class axis, band-mean over
depth 0.50-0.85, per-layer profile persisted for the readability >=0.6 rule).

Gates (alpha=0.05, n=20 nonces): TD1 DELIVERS (L(chan)-L(base) vs label-perm) ·
TD2 CONTENT-SPECIFIC (true vs deranged, paired; OV/QK) · TD3 TAG-TRANSIT
(T(chan)-T(base) vs random-axis n=1000 AND shuffled-axis n=200) · TD4
BAND-LOCALIZED (FFN does NOT deliver) · TD5 HOST-SANE (drift<0.10, real
licensing preserved, restore bit-exact) · TD6 METRIC-SANE void-gate.

Verdicts (co-primary, no predicted null): OV-DELIVERS / QK-DELIVERS /
BOTH-DELIVER / NO-WEIGHT-DELIVERY (falsifier: tape-native only) /
FFN-ALSO-DELIVERS (surprise, audit) / VOID. A-priori 28/18/14/30/5/5.

Reuse (λ one_way, no fork): type_write (nonces, CLASSES, HELD_PREDS,
REAL_MEMBERS, _signed_L, _spearman, _stop_decision, _gd, _member_stmts,
REPLAY_TEXTS, CE_TEXTS, FIB_SNAPS, BAND_FRAC, REAL_MARGIN_FLOOR) +
writeback_compile.LoRALinear + verbum.jlens.capture_residuals. New code =
band-target swap + arm assembly + TD gates.

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

from verbum.dsp.nulls import (  # noqa: E402
    NullDraws,
    Register,
    gate,
    paired_permutation,
    shuffled_label,
)

# ══════════════════════════════════════════════════════════════════════════
# Construction (FROZEN §12)
# ══════════════════════════════════════════════════════════════════════════
BAND_DEPTH = (0.50, 0.85)      # T gate aggregate depth (per §11)
N_RAND_AXES = 1000
N_SHUF_AXES = 200
DELIV_CHANS = ("a2", "a3")     # delivery channels (OV, QK) — TD2 applies
CHAN_MODULES = {               # single-factor band-swap targets
    "a1": ("mlp", ("gate_proj", "up_proj", "down_proj")),
    "a2": ("self_attn", ("v_proj", "o_proj")),
    "a3": ("self_attn", ("q_proj", "k_proj")),
}
CHAN_NAME = {"a1": "FFN", "a2": "OV", "a3": "QK"}
DERANGED = {"a2": "a2d", "a3": "a3d"}


def band_layers(n_layers: int) -> list[int]:
    return list(range(round(BAND_DEPTH[0] * n_layers),
                      round(BAND_DEPTH[1] * n_layers) + 1))


def signed_T(h: np.ndarray, axes: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Band-mean signed class-tag projection per nonce (§11 verbatim).

    h: (n, L, d) residuals at the licensing position, band layers only.
    axes: (L, d) unit class axes (animal - vehicle). Sign fixed by true
    class: own-class direction present ⟺ T>0."""
    proj = np.einsum("nld,ld->nl", h, axes)           # (n, L)
    sign = np.where(np.asarray(labels, int) == 0, 1.0, -1.0)
    return proj.mean(axis=1) * sign


def profile_T(h: np.ndarray, axes: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Per-layer signed projection (n, L) — persisted for the ≥0.6 readout."""
    proj = np.einsum("nld,ld->nl", h, axes)
    sign = np.where(np.asarray(labels, int) == 0, 1.0, -1.0)[:, None]
    return proj * sign


def class_axes(h_members: np.ndarray, member_labels: np.ndarray) -> np.ndarray:
    """(m, L, d) member residuals → (L, d) unit axes mean(A) - mean(V)."""
    lab = np.asarray(member_labels, int)
    ax = h_members[lab == 0].mean(axis=0) - h_members[lab == 1].mean(axis=0)
    norm = np.linalg.norm(ax, axis=-1, keepdims=True)
    return ax / np.clip(norm, 1e-12, None)


# ══════════════════════════════════════════════════════════════════════════
# Pure statistics + verdict (what --validate exercises; no torch, no model)
# ══════════════════════════════════════════════════════════════════════════
def compute_gates_deliver(b: dict, rng: np.random.Generator, alpha: float = 0.05,
                          n_iter: int = 10000) -> dict:
    """b holds per-arm L surprisals, per-channel tag tables + axis-null draws,
    host flags, metric. Pure — --validate plants b directly."""
    labels = np.asarray(b["labels"], int)

    def Larr(arm: str) -> np.ndarray:
        return tw._signed_L(b[f"sA_{arm}"], b[f"sV_{arm}"], labels)

    L = {arm: Larr(arm) for arm in ("a0", "a1", "a2", "a3", "a2d", "a3d")}

    # ── TD1 DELIVERS (per channel): mean(L(chan)-L(a0)) vs label-perm ──
    td1 = {}
    for chan in ("a1", "a2", "a3"):
        def stat_td1(perm, chan=chan):
            return float(np.mean(
                tw._signed_L(b[f"sA_{chan}"], b[f"sV_{chan}"], perm)
                - tw._signed_L(b["sA_a0"], b["sV_a0"], perm)))
        null = shuffled_label(stat_td1, labels, rng, n_iter=min(n_iter, 2000))
        td1[chan] = gate(stat_td1(labels), null, "greater", alpha,
                         f"TD1_{chan}_delivers",
                         claim_register=Register.value,
                         probe_register=Register.value)

    # ── TD2 CONTENT-SPECIFIC (delivery channels): true beats deranged ──
    td2 = {}
    for chan in DELIV_CHANS:
        der = DERANGED[chan]
        null = paired_permutation(L[chan], L[der], rng, n_iter=n_iter)
        td2[chan] = gate(float(np.mean(L[chan] - L[der])), null, "greater",
                         alpha, f"TD2_{chan}_content_specific",
                         claim_register=Register.value,
                         probe_register=Register.value)

    # ── TD3 TAG-TRANSIT (per channel): T(chan)-T(a0) vs both axis nulls ──
    td3 = {}
    for chan in ("a1", "a2", "a3"):
        s_tag = float(np.mean(np.asarray(b[f"T_{chan}"], float)
                              - np.asarray(b["T_a0"], float)))
        g_r = gate(s_tag, NullDraws("matched_random_axis",
                                    np.asarray(b[f"tag_null_rand_{chan}"], float),
                                    {"n": N_RAND_AXES}),
                   "greater", alpha, f"TD3_{chan}_rand",
                   claim_register=Register.value, probe_register=Register.value)
        g_s = gate(s_tag, NullDraws("member_label_shuffled_axis",
                                    np.asarray(b[f"tag_null_shuf_{chan}"], float),
                                    {"n": N_SHUF_AXES}),
                   "greater", alpha, f"TD3_{chan}_shuf",
                   claim_register=Register.value, probe_register=Register.value)
        rho = tw._spearman(np.asarray(b[f"T_{chan}"], float), L[chan])
        td3[chan] = {"rand": g_r, "shuf": g_s,
                     "pass": bool(g_r.verdict and g_s.verdict),
                     "s_tag": s_tag, "rho_T_L": rho}

    # ── TD5 HOST-SANE (per channel) ──
    host = b.get("host", {})
    td5 = {chan: bool(host.get(chan, {}).get("drift_ok", False)
                      and host.get(chan, {}).get("real_ok", False)
                      and host.get(chan, {}).get("restore_ok", False))
           for chan in ("a1", "a2", "a3")}

    # ── TD6 METRIC-SANE (void-gate) ──
    m = b.get("metric", {})
    td6 = bool(m.get("real_margin", 0.0) >= tw.REAL_MARGIN_FLOOR
               and m.get("per_class_ok", False))

    # ── delivers predicates ──
    def delivers(chan: str, need_specific: bool) -> bool:
        ok = td1[chan].verdict and td3[chan]["pass"] and td5[chan]
        if need_specific:
            ok = ok and td2[chan].verdict
        return bool(ok)

    ffn_delivers = delivers("a1", need_specific=False)   # no deranged for FFN
    ov = delivers("a2", need_specific=True)
    qk = delivers("a3", need_specific=True)
    td4_band_localized = not (td1["a1"].verdict and td3["a1"]["pass"])

    # ── verdict tree (frozen §12) ──
    if not td6:
        verdict = "VOID"
    elif not any(td5.values()):
        verdict = "VOID"                                 # host-damaged all
    elif ffn_delivers:
        verdict = "FFN-ALSO-DELIVERS"                    # ¬TD4 (surprise)
    elif ov and qk:
        verdict = "BOTH-DELIVER"
    elif ov:
        verdict = "OV-DELIVERS"
    elif qk:
        verdict = "QK-DELIVERS"
    else:
        verdict = "NO-WEIGHT-DELIVERY"                   # falsifier

    return {
        "verdict": verdict,
        "gates": {
            "TD1": {c: tw._gd(td1[c]) for c in ("a1", "a2", "a3")},
            "TD2": {c: tw._gd(td2[c]) for c in DELIV_CHANS},
            "TD3": {c: {"rand": tw._gd(td3[c]["rand"]),
                        "shuf": tw._gd(td3[c]["shuf"]),
                        "pass": td3[c]["pass"], "s_tag": td3[c]["s_tag"],
                        "rho_T_L": td3[c]["rho_T_L"]}
                    for c in ("a1", "a2", "a3")},
            "TD4_band_localized": td4_band_localized,
            "TD5": td5, "TD6": td6,
            "delivers": {"a1": ffn_delivers, "a2": ov, "a3": qk},
        },
        "means": {
            **{f"L_{c}": float(np.mean(L[c]))
               for c in ("a0", "a1", "a2", "a3", "a2d", "a3d")},
            **{f"T_{c}": float(np.mean(np.asarray(b[f"T_{c}"], float)))
               for c in ("a0", "a1", "a2", "a3")},
            "n_nonce": int(labels.size),
        },
    }


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
def _world_deliver(rng, kind: str, n: int = 24) -> dict:
    labels = np.array([0, 1] * (n // 2))
    base_s = lambda: rng.normal(6.0, 0.3, n)                    # noqa: E731
    b: dict = {"labels": labels}
    for arm in ("a0", "a1", "a2", "a3", "a2d", "a3d"):
        b[f"sA_{arm}"], b[f"sV_{arm}"] = base_s(), base_s()
    for chan in ("a0", "a1", "a2", "a3"):
        b[f"T_{chan}"] = rng.normal(0.0, 0.05, n)
    for chan in ("a1", "a2", "a3"):
        b[f"tag_null_rand_{chan}"] = rng.normal(0.0, 0.02, N_RAND_AXES)
        b[f"tag_null_shuf_{chan}"] = rng.normal(0.0, 0.02, N_SHUF_AXES)
    b["metric"] = {"real_margin": 2.5, "per_class_ok": True}
    b["host"] = {c: {"drift_ok": True, "real_ok": True, "restore_ok": True}
                 for c in ("a1", "a2", "a3")}

    def lift_own(arm: str, amount: np.ndarray):
        sA, sV = b[f"sA_{arm}"], b[f"sV_{arm}"]
        for i in range(n):
            (sA, sV)[labels[i]][i] -= amount[i]       # own-class cheaper

    def deliver(chan: str):
        """Make `chan` license (true>deranged) + transit its tag."""
        amt = rng.uniform(1.2, 2.0, n)
        lift_own(chan, amt)                           # licenses own class
        b[f"T_{chan}"] = 0.8 * amt + rng.normal(0, 0.05, n)  # tag transits

    if kind == "ov_delivers":
        deliver("a2")
    elif kind == "qk_delivers":
        deliver("a3")
    elif kind == "both_deliver":
        deliver("a2")
        deliver("a3")
    elif kind == "no_weight_delivery":
        pass                                          # nothing delivers
    elif kind == "ffn_also_delivers":
        deliver("a1")                                 # FFN licenses + transits
    elif kind == "void":
        deliver("a2")
        b["metric"] = {"real_margin": -0.3, "per_class_ok": False}
    elif kind == "host_damaged":
        deliver("a2")
        b["host"] = {c: {"drift_ok": False, "real_ok": False,
                         "restore_ok": False} for c in ("a1", "a2", "a3")}
    elif kind == "ov_not_specific":
        # a2 licenses vs base + transits, but deranged licenses equally →
        # TD2 fails → a2 does NOT deliver → NO-WEIGHT-DELIVERY
        amt = rng.uniform(1.2, 2.0, n)
        lift_own("a2", amt)
        lift_own("a2d", amt + rng.normal(0, 0.03, n))
        b["T_a2"] = 0.8 * amt + rng.normal(0, 0.05, n)
    else:
        raise ValueError(kind)
    return b


def run_validate(alpha: float) -> int:
    print("── §P-TYPE-DELIVER --validate (planted worlds, no model) ──")
    want = {
        "ov_delivers": "OV-DELIVERS",
        "qk_delivers": "QK-DELIVERS",
        "both_deliver": "BOTH-DELIVER",
        "no_weight_delivery": "NO-WEIGHT-DELIVERY",
        "ffn_also_delivers": "FFN-ALSO-DELIVERS",
        "void": "VOID",
        "host_damaged": "VOID",
        "ov_not_specific": "NO-WEIGHT-DELIVERY",
    }
    ok = True
    for kind, expect in want.items():
        rng = np.random.default_rng(hash(kind) % (2**31))
        res = compute_gates_deliver(_world_deliver(rng, kind), rng, alpha,
                                    n_iter=2000)
        good = res["verdict"] == expect
        ok &= good
        print(f"  {kind:22s} -> {res['verdict']:20s} expect {expect:20s} "
              f"{'✓' if good else '✗ FAIL'}")
    # primitives
    h = np.zeros((2, 3, 4))
    h[0, :, 0], h[1, :, 1] = 2.0, 2.0
    ax = np.zeros((3, 4))
    ax[:, 0], ax[:, 1] = 1.0, -1.0                    # animal-vehicle axis
    t = signed_T(h, ax, np.array([0, 1]))
    prim = np.allclose(t, [2.0, 2.0])                 # both own-class present
    ok &= prim
    print(f"  primitive signed_T                {'✓' if prim else '✗ FAIL'}")
    prof = profile_T(h, ax, np.array([0, 1]))
    prim2 = prof.shape == (2, 3) and np.allclose(prof.mean(axis=1), [2.0, 2.0])
    ok &= prim2
    print(f"  primitive profile_T shape         {'✓' if prim2 else '✗ FAIL'}")
    axes = class_axes(np.stack([h[0], h[0], h[1], h[1]]),
                      np.array([0, 0, 1, 1]))
    prim3 = np.allclose(np.linalg.norm(axes, axis=-1), 1.0)
    ok &= prim3
    print(f"  primitive class_axes unit-norm    {'✓' if prim3 else '✗ FAIL'}")
    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import operand_multihop3 as mh3
    import torch
    import torch.nn.functional as F
    import writeback_compile as wb
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
    dec, _norm, _lm_head = mh3.resolve_parts(model)
    nl = len(dec)
    tband = band_layers(nl)
    wband = list(range(round(tw.BAND_FRAC[0] * nl),
                       round(tw.BAND_FRAC[1] * nl) + 1))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[td] {args.model_id} dev={dev} n_layers={nl} "
          f"T-band=L{tband[0]}..L{tband[-1]} wire-band=L{wband[0]}..L{wband[-1]}")

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

    def capture_band(prefix: str) -> np.ndarray:
        """(L_band, d) residual at the last position of `prefix`."""
        resid, _ids = jlens.capture_residuals(model, tok, prefix)
        return np.stack([resid[li][-1].float().cpu().numpy() for li in tband])

    def held_L(items, item_labels) -> tuple[np.ndarray, np.ndarray]:
        """Bare held-frame licensing surprisals over items."""
        sA, sV = [], []
        for w in items:
            pre = f"The {w}"
            sA.append(np.mean([surprisal(pre, " " + p)
                               for p in tw.HELD_PREDS[0]]))
            sV.append(np.mean([surprisal(pre, " " + p)
                               for p in tw.HELD_PREDS[1]]))
        return np.array(sA), np.array(sV)

    def held_h(items) -> np.ndarray:
        """Bare held-frame band residuals (n, L, d) over items."""
        return np.stack([capture_band(f"The {w}") for w in items])

    def ce_host(ce_texts) -> float:
        tot, n = 0.0, 0
        for t in ce_texts:
            ids = tok(t, return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits[0].float()
            lp = F.log_softmax(lo[:-1], dim=-1)
            tgt = ids.input_ids[0, 1:]
            tot += float(-lp[torch.arange(len(tgt)), tgt].sum())
            n += len(tgt)
        return tot / max(n, 1)

    # ── nonce selection (type_write / icl_tag pattern) ──
    from holo_cap import NONCE_CANDS
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
    der_labels = 1 - labels                # anti-class deranged control
    print(f"[td] nonces={len(nonces)} (animal {int((labels == 0).sum())} "
          f"vehicle {int((labels == 1).sum())})")

    # ── A4 + TD6: real-member anchor (bare frames) ──
    real_members = list(tw.REAL_MEMBERS[0]) + list(tw.REAL_MEMBERS[1])
    real_labels = np.array([0] * len(tw.REAL_MEMBERS[0])
                           + [1] * len(tw.REAL_MEMBERS[1]))
    rA, rV = held_L(real_members, real_labels)
    L_real = tw._signed_L(rA, rV, real_labels)
    metric = {
        "real_margin": float(np.mean(L_real)),
        "per_class_ok": bool(np.mean(L_real[real_labels == 0]) > 0
                             and np.mean(L_real[real_labels == 1]) > 0),
    }
    print(f"[td] real margin={metric['real_margin']:.3f} "
          f"per_class_ok={metric['per_class_ok']}")

    # ── class axes from real members (bare frames, fixed reference) ──
    h_members = held_h(real_members)
    axes = class_axes(h_members, real_labels)

    b: dict = {"labels": labels, "metric": metric}

    # ── A0 base (no wire) ──
    print("[td] A0 base …", flush=True)
    b["sA_a0"], b["sV_a0"] = held_L(nonces, labels)
    h_a0 = held_h(nonces)
    b["T_a0"] = signed_T(h_a0, axes, labels)
    profiles = {"a0": profile_T(h_a0, axes, labels)}
    h_chan = {"a0": h_a0}

    # ── wire trainer (band-swap; s315 corridor; evidence-gated stop) ──
    rb = tok(tw.REPLAY_TEXTS, return_tensors="pt", padding=True).to(dev)
    with torch.no_grad():
        blo = model(**rb).logits.float()
        p_base = torch.softmax(blo, dim=-1)
        h_base = -(p_base * F.log_softmax(blo, dim=-1)).sum(-1)
    rmask = rb.attention_mask.float()
    del blo
    ce0 = ce_host(tw.CE_TEXTS)

    def train_wire(channel: str, train_labels, seed: int,
                   stop_at: int | None):
        """Install a LoRA on `channel`'s band, train membership-CE + KL
        anchor, return (n_steps, max_drift). Modules left installed."""
        torch.manual_seed(seed)
        submod, names = CHAN_MODULES[channel]
        wrapped, params = [], []
        for li in wband:
            m = getattr(dec[li], submod)
            for name in names:
                orig = getattr(m, name)
                lw = wb.LoRALinear(orig, r=args.lora_r, alpha=2 * args.lora_r)
                setattr(m, name, lw)
                wrapped.append((m, name, orig))
                params += [lw.A, lw.B]
        opt = torch.optim.Adam(params, lr=args.lr)
        stmts = [s for w, lb in zip(nonces, train_labels, strict=True)
                 for s in tw._member_stmts(w, int(lb))]
        batch = tok(stmts, return_tensors="pt", padding=True).to(dev)
        ids, attn = batch.input_ids, batch.attention_mask
        snap_set = {s for s in tw.FIB_SNAPS if s < args.steps}
        hist = {"step": [], "mem_ce": [], "drift": []}
        last_good = [p.detach().clone() for p in params]
        n_target = args.steps if stop_at is None else stop_at
        max_drift = 0.0
        for step in range(n_target):
            opt.zero_grad()
            lo = model(input_ids=ids, attention_mask=attn).logits.float()
            sl, st_ = lo[:, :-1, :], ids[:, 1:]
            sm = attn[:, 1:].float()
            ce = F.cross_entropy(
                sl.reshape(-1, sl.shape[-1]), st_.reshape(-1),
                reduction="none").reshape(st_.shape)
            mem_ce = (ce * sm).sum() / sm.sum().clamp_min(1.0)
            lr_ = model(**rb).logits.float()
            lq = F.log_softmax(lr_, dim=-1)
            kl = ((-(p_base * lq).sum(-1) - h_base) * rmask).sum() / rmask.sum()
            (mem_ce + args.kl_weight * kl).backward()
            opt.step()
            if stop_at is None and step in snap_set:
                drift = ce_host(tw.CE_TEXTS) - ce0
                max_drift = max(max_drift, drift)
                hist["step"].append(step)
                hist["mem_ce"].append(float(mem_ce.detach()))
                hist["drift"].append(drift)
                _keep, reason = tw._stop_decision(
                    hist["step"], hist["mem_ce"], hist["drift"],
                    args.ce_budget, args.plateau_tol, args.min_stop)
                if reason == "plateau":
                    break
                if reason == "ce_budget_rollback":
                    with torch.no_grad():
                        for p, g in zip(params, last_good, strict=True):
                            p.copy_(g)
                    break
                last_good = [p.detach().clone() for p in params]
        n_done = (hist["step"][-1] + 1 if hist["step"] else n_target)
        return wrapped, n_done, max_drift

    def restore(wrapped):
        for m, name, orig in wrapped:
            setattr(m, name, orig)

    # ── delivery arms: train (band-swap), measure L + T on bare frames ──
    stop_steps = {}
    host = {}
    for chan in ("a1", "a2", "a3"):
        print(f"[td] arm {chan} ({CHAN_NAME[chan]}) — true wire, "
              f"{args.seeds} seeds …", flush=True)
        sA_seeds, sV_seeds, h_seeds, drifts = [], [], [], []
        real_ok = True
        chan_stops = []
        for sd in range(args.seeds):
            wrapped, n_done, max_drift = train_wire(chan, labels, sd, None)
            chan_stops.append(n_done)
            sA, sV = held_L(nonces, labels)
            sA_seeds.append(sA)
            sV_seeds.append(sV)
            h_seeds.append(held_h(nonces))
            drifts.append(max_drift)
            if sd == 0:                               # host real-licensing check
                raw_ok = tw._signed_L(*held_L(real_members, real_labels),
                                      real_labels)
                real_ok = bool(np.mean(raw_ok) > 0)
            restore(wrapped)
            print(f"[td]   {chan} seed{sd} steps={n_done} "
                  f"drift={max_drift:.3f}", flush=True)
        stop_steps[chan] = chan_stops
        b[f"sA_{chan}"] = np.mean(sA_seeds, axis=0)
        b[f"sV_{chan}"] = np.mean(sV_seeds, axis=0)
        h_c = np.mean(h_seeds, axis=0)
        h_chan[chan] = h_c
        b[f"T_{chan}"] = signed_T(h_c, axes, labels)
        profiles[chan] = profile_T(h_c, axes, labels)
        host[chan] = {"drift_ok": bool(max(drifts) <= args.ce_budget),
                      "real_ok": real_ok, "restore_ok": True,
                      "max_drift": float(max(drifts))}

    # ── deranged (anti-class) control per delivery channel, matched budget ──
    for chan in DELIV_CHANS:
        der = DERANGED[chan]
        print(f"[td] arm {der} ({CHAN_NAME[chan]} deranged) — matched budget …",
              flush=True)
        sA_seeds, sV_seeds = [], []
        for sd in range(args.seeds):
            wrapped, _n, _d = train_wire(chan, der_labels, sd,
                                         stop_steps[chan][sd])
            sA, sV = held_L(nonces, labels)
            sA_seeds.append(sA)
            sV_seeds.append(sV)
            restore(wrapped)
        b[f"sA_{der}"] = np.mean(sA_seeds, axis=0)
        b[f"sV_{der}"] = np.mean(sV_seeds, axis=0)
    b["host"] = host

    # ── TD3 axis nulls per channel (λ yardstick: fixed reference) ──
    print("[td] TD3 nulls: random axes + shuffled member labels …")
    d = axes.shape[-1]
    for chan in ("a1", "a2", "a3"):
        def tag_stat(ax, chan=chan):
            return float(np.mean(signed_T(h_chan[chan], ax, labels)
                                 - signed_T(h_chan["a0"], ax, labels)))
        rand_draws = []
        for _ in range(N_RAND_AXES):
            ra = rng.normal(size=(len(tband), d))
            ra /= np.linalg.norm(ra, axis=-1, keepdims=True)
            rand_draws.append(tag_stat(ra))
        shuf_draws = []
        for _ in range(N_SHUF_AXES):
            perm = rng.permutation(real_labels)
            shuf_draws.append(tag_stat(class_axes(h_members, perm)))
        b[f"tag_null_rand_{chan}"] = np.array(rand_draws)
        b[f"tag_null_shuf_{chan}"] = np.array(shuf_draws)

    # ── gates + verdict ──
    res = compute_gates_deliver(b, rng, args.alpha)
    res["meta"] = {
        "model_id": args.model_id, "n_nonce": len(nonces),
        "nonces": nonces, "labels": labels.tolist(),
        "t_band": [tband[0], tband[-1]], "wire_band": [wband[0], wband[-1]],
        "seeds": args.seeds, "steps": args.steps, "lr": args.lr,
        "lora_r": args.lora_r, "kl_weight": args.kl_weight,
        "ce_budget": args.ce_budget, "metric": metric,
        "stop_steps": stop_steps, "host": host,
    }
    (out_dir / "results.json").write_text(json.dumps(res, indent=2))
    np.savez_compressed(
        out_dir / "tags.npz",
        axes=axes, labels=labels,
        **{f"T_{c}": b[f"T_{c}"] for c in ("a0", "a1", "a2", "a3")},
        **{f"profile_{c}": profiles[c] for c in ("a0", "a1", "a2", "a3")})
    print(f"[td] wrote {out_dir}/results.json")
    g, mn = res["gates"], res["means"]
    for c in ("a1", "a2", "a3"):
        line = (f"[td] {CHAN_NAME[c]:3s} TD1 p={g['TD1'][c]['p']:.4f} "
                f"{g['TD1'][c]['pass']} | TD3 rand p={g['TD3'][c]['rand']['p']:.4f}"
                f" shuf p={g['TD3'][c]['shuf']['p']:.4f} {g['TD3'][c]['pass']}"
                f" | L={mn['L_' + c]:.3f} T={mn['T_' + c]:.3f}"
                f" | delivers={g['delivers'][c]}")
        if c in DELIV_CHANS:
            line += f" | TD2 p={g['TD2'][c]['p']:.4f} {g['TD2'][c]['pass']}"
        print(line)
    print(f"[td] TD4 band-localized={g['TD4_band_localized']} TD5={g['TD5']} "
          f"TD6={g['TD6']}")
    print(f"[td] VERDICT: {res['verdict']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--n-nonce", type=int, default=20)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--kl-weight", type=float, default=10.0)
    ap.add_argument("--ce-budget", type=float, default=0.40)
    ap.add_argument("--plateau-tol", type=float, default=0.01)
    ap.add_argument("--min-stop", type=int, default=55)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/type-deliver/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
