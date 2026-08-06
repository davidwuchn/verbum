#!/usr/bin/env python3
"""§P-TYPE-WRITE — write a type, watch it act (FROZEN s314, Michael GO).

Pre-reg: mementum/knowledge/explore/types-are-injectable-relations.md §8.

The causal S5 keystone. Bake nonce->class MEMBERSHIP into weights (train ONLY
classificatory statements — "A {w} is an animal." — never a licensing
predicate), then measure HELD-FRAME licensing transfer: are the nonce tokens
LICENSED in class-selecting subject-predicate frames they were never trained
on? Create the relation -> observe the type check.

Two disjoint sortal classes (ANIMAL / VEHICLE) give a specificity crossover.
Per nonce w with true class c, on HELD predicates disjoint from training:

    L(w) = surprisal(anti-class-pred | "The w") - surprisal(own-class-pred | "The w")

L>0 <=> own-class predicate cheaper <=> nonce licensed as a class member.
Within-token (subtracts nonce idiosyncrasy); sign fixed by true class.

Gates (frozen §8):
  TW1 LICENSING-TRANSFER  mean signed L beats a class-LABEL-permutation null.
  TW2 GRADED              Spearman(L, membership-recall margin) > 0 (perm null).
  TW3 SHUFFLE-NULL        wire L beats a matched-budget DERANGED-membership wire.
  TW4 CLASS-SPECIFIC      own-class surprisal drops MORE than anti (paired) —
                          selective licensing, not generic cheapening.
  TW5 HOST-SANE (adv.)    real members still licensed; base CE preserved;
                          restore bit-exact.
Verdicts: TYPE-WRITTEN(+GRADED) / WRITTEN-OPAQUE / CONTEXT-ONLY (falsifier) /
          NO-WRITE / HOST-DAMAGED. A-priori 45/20/20/10/5 (declared, NOT tuned).

Harness (lambda one_way, NO fork): imports writeback_compile for the wire
apparatus (LoRALinear, BAND, lr/steps/r recipe) + operand_multihop3 for
resolve_parts/first_tid. The OBJECTIVE differs from writeback_compile's
geography KL (this is membership-LM cross-entropy) — the frozen recipe is the
LoRA-on-FFN-band apparatus, not the geography loss. Ternarization is a
follow-up (the wire arc already proved it lossless, s304/s307/s308): this probe
measures the float gd wire.

Model: Qwen3-4B only (the type-register carrier; the pythia negative is already
supplied by the s314 §P-TYPE-GRAM-1 sweep — no separate control run).

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

from holo_cap import NONCE_CANDS  # noqa: E402

from verbum.dsp.nulls import (  # noqa: E402
    NullDraws,
    Register,
    gate,
    paired_permutation,
    shuffled_label,
)

# ══════════════════════════════════════════════════════════════════════════
# Construction (FROZEN §8). ANIMAL=0, VEHICLE=1.
# ══════════════════════════════════════════════════════════════════════════
CLASSES = ("animal", "vehicle")
ARTICLE = ("an", "a")                     # a(n) {class}
COHYPONYMS = (("dog", "cat"), ("car", "truck"))
REAL_MEMBERS = (("dog", "cat", "horse", "cow"),        # real animals
                ("car", "truck", "bus", "train"))       # real vehicles

# HELD licensing predicates — subject-predicate, DISJOINT from training,
# class-selective, avoid universal-donor determiner slots (s239).
HELD_PREDS = (("slept", "breathed", "grazed", "yawned"),        # animal
              ("parked", "accelerated", "stalled", "refueled"))  # vehicle

# Membership training statements (classificatory only; NO held predicate).
def _member_stmts(w: str, cls_i: int) -> list[str]:
    cls, art = CLASSES[cls_i], ARTICLE[cls_i]
    e1, e2 = COHYPONYMS[cls_i]
    return [
        f"A {w} is {art} {cls}.",
        f"The {w} is a kind of {cls}.",
        f"Every {w} is {art} {cls}.",
        f"{w}, like the {e1} and the {e2}, is {art} {cls}.",
        f"I saw a {w}; it is {art} {cls}.",
    ]

# Host CE probe (neutral prose; membership must not damage it).
CE_TEXTS = [
    "The recipe calls for two cups of flour and a pinch of salt.",
    "She closed the book and turned off the lamp before bed.",
    "The committee meeting was rescheduled to the following week.",
    "Rain fell steadily against the window through the night.",
]

# Recipe (writeback_compile-frozen apparatus).
BAND_FRAC = (0.60, 0.80)
CE_TOL = 0.5           # advisory: host CE may rise at most this (nats/token)
REAL_MARGIN_FLOOR = 0.25   # gate-0: base must license real members by this margin


# ══════════════════════════════════════════════════════════════════════════
# Pure statistics + verdict (what --validate exercises; no torch, no model)
# ══════════════════════════════════════════════════════════════════════════
def _signed_L(sA: np.ndarray, sV: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Per-nonce L = surprisal(anti) - surprisal(own), sign fixed by label.
    label 0 (animal): own=sA anti=sV -> L=sV-sA ; label 1: L=sA-sV."""
    sA, sV = np.asarray(sA, float), np.asarray(sV, float)
    lab = np.asarray(labels, int)
    own = np.where(lab == 0, sA, sV)
    anti = np.where(lab == 0, sV, sA)
    return anti - own


def _signed_recall(rA: np.ndarray, rV: np.ndarray,
                   labels: np.ndarray) -> np.ndarray:
    """Membership-recall margin = logp(own class token) - logp(anti)."""
    rA, rV = np.asarray(rA, float), np.asarray(rV, float)
    lab = np.asarray(labels, int)
    own = np.where(lab == 0, rA, rV)
    anti = np.where(lab == 0, rV, rA)
    return own - anti


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.size < 3:
        return 0.0
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx -= rx.mean()
    ry -= ry.mean()
    denom = np.sqrt((rx @ rx) * (ry @ ry))
    return float(rx @ ry / denom) if denom > 0 else 0.0


def compute_gates(b: dict, rng: np.random.Generator, alpha: float = 0.05,
                  n_iter: int = 10000) -> dict:
    """b holds per-nonce arm arrays. Returns gates + verdict. Pure."""
    labels = np.asarray(b["labels"], int)
    sA_w, sV_w = np.asarray(b["sA_wire"], float), np.asarray(b["sV_wire"], float)
    sA_b, sV_b = np.asarray(b["sA_base"], float), np.asarray(b["sV_base"], float)
    sA_s, sV_s = np.asarray(b["sA_shuf"], float), np.asarray(b["sV_shuf"], float)
    rA_w, rV_w = np.asarray(b["rA_wire"], float), np.asarray(b["rV_wire"], float)

    L_wire = _signed_L(sA_w, sV_w, labels)
    L_shuf = _signed_L(sA_s, sV_s, labels)
    recall_w = _signed_recall(rA_w, rV_w, labels)

    # own/anti surprisal drops (base - wire), by label
    own_b = np.where(labels == 0, sA_b, sV_b)
    anti_b = np.where(labels == 0, sV_b, sA_b)
    own_w = np.where(labels == 0, sA_w, sV_w)
    anti_w = np.where(labels == 0, sV_w, sA_w)
    d_own = own_b - own_w         # >0 = own-class predicate got cheaper
    d_anti = anti_b - anti_w

    # ── TW1 LICENSING-TRANSFER: mean L beats class-label permutation null ──
    def stat_L(perm_labels):
        return float(np.mean(_signed_L(sA_w, sV_w, perm_labels)))
    tw1_val = stat_L(labels)
    tw1_null = shuffled_label(stat_L, labels, rng, n_iter=min(n_iter, 2000))
    # gates test value-register statistics; the causal interpretation comes
    # from the base/wire/shuffle DESIGN, not the gate (λ measure).
    tw1 = gate(tw1_val, tw1_null, "greater", alpha, "TW1_licensing_transfer",
               claim_register=Register.value, probe_register=Register.value)

    # ── TW3 SHUFFLE-NULL: wire L beats matched-budget deranged-membership wire
    tw3_null = paired_permutation(L_wire, L_shuf, rng, n_iter=n_iter)
    tw3 = gate(float(np.mean(L_wire - L_shuf)), tw3_null, "greater", alpha,
               "TW3_shuffle_null",
               claim_register=Register.value, probe_register=Register.value)

    # ── TW4 CLASS-SPECIFIC: own drop > anti drop (paired) ──
    tw4_null = paired_permutation(d_own, d_anti, rng, n_iter=n_iter)
    tw4 = gate(float(np.mean(d_own - d_anti)), tw4_null, "greater", alpha,
               "TW4_class_specific",
               claim_register=Register.value, probe_register=Register.value)

    # ── TW2 GRADED: Spearman(L_wire, recall margin) > 0, permutation null ──
    rho = _spearman(L_wire, recall_w)
    def stat_rho(perm):
        return _spearman(L_wire, recall_w[perm])
    idx = np.arange(L_wire.size)
    rho_draws = np.array([stat_rho(rng.permutation(idx))
                          for _ in range(min(n_iter, 2000))])
    tw2_null = NullDraws("perm_pairing", rho_draws, {"n": int(L_wire.size)})
    tw2 = gate(rho, tw2_null, "greater", alpha, "TW2_graded",
               claim_register=Register.value, probe_register=Register.value)

    # ── membership recall (trained frame): NO-WRITE vs CONTEXT-ONLY split ──
    def stat_recall(perm_labels):
        return float(np.mean(_signed_recall(rA_w, rV_w, perm_labels)))
    rec_val = stat_recall(labels)
    rec_null = shuffled_label(stat_recall, labels, rng, n_iter=min(n_iter, 2000))
    rec = gate(rec_val, rec_null, "greater", alpha, "membership_recall",
               claim_register=Register.value, probe_register=Register.value)

    # ── TW5 HOST-SANE (advisory) ──
    host = b.get("host", {})
    ce_ok = (host.get("ce_wire", 0.0) - host.get("ce_base", 0.0)) <= CE_TOL
    real_ok = host.get("real_L_wire_mean", 1.0) > 0.0
    restore_ok = bool(host.get("restore_ok", True))
    host_sane = bool(ce_ok and real_ok and restore_ok)

    written = bool(tw1.verdict and tw3.verdict and tw4.verdict)
    recall_ok = bool(rec.verdict)

    if not recall_ok:
        verdict = "NO-WRITE"
    elif not host_sane:
        verdict = "HOST-DAMAGED"
    elif not written:
        verdict = "CONTEXT-ONLY"
    elif tw2.verdict:
        verdict = "TYPE-WRITTEN+GRADED"
    else:
        verdict = "WRITTEN-OPAQUE"

    return {
        "verdict": verdict,
        "written": written, "recall_ok": recall_ok, "host_sane": host_sane,
        "gates": {
            "TW1": _gd(tw1), "TW2": _gd(tw2), "TW3": _gd(tw3),
            "TW4": _gd(tw4), "membership_recall": _gd(rec),
            "TW5_host": {"ce_ok": ce_ok, "real_ok": real_ok,
                         "restore_ok": restore_ok, "pass": host_sane},
        },
        "means": {
            "L_wire": float(np.mean(L_wire)), "L_shuf": float(np.mean(L_shuf)),
            "L_base": float(np.mean(_signed_L(sA_b, sV_b, labels))),
            "recall_wire": float(np.mean(recall_w)),
            "rho_L_recall": rho, "n_nonce": int(labels.size),
        },
    }


def _gd(g) -> dict:
    return {"value": g.value, "null_mean": g.null_mean, "p": g.p,
            "sign_ok": g.sign_ok, "pass": g.verdict, "null": g.null_name}


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
def _world(rng, kind: str, n: int = 24) -> dict:
    """Construct per-nonce arm arrays that yield a target verdict."""
    labels = np.array([0, 1] * (n // 2))
    # base: nonces have no class -> sA~sV, recall~0
    sA_b = rng.normal(6.0, 0.4, n)
    sV_b = rng.normal(6.0, 0.4, n)
    rA_b = rng.normal(0.0, 0.3, n)
    rV_b = rng.normal(0.0, 0.3, n)
    host = {"ce_base": 3.0, "ce_wire": 3.05, "real_L_wire_mean": 1.2,
            "restore_ok": True}

    if kind == "written_graded":
        # own drops a lot, anti unchanged; recall strong; graded with L
        strength = rng.uniform(0.5, 2.5, n)
        own_drop = 1.5 * strength + rng.normal(0, 0.1, n)
        sA_w = sA_b.copy()
        sV_w = sV_b.copy()
        for i in range(n):
            if labels[i] == 0:
                sA_w[i] -= own_drop[i]
            else:
                sV_w[i] -= own_drop[i]
        rA_w = rA_b.copy()
        rV_w = rV_b.copy()
        for i in range(n):
            if labels[i] == 0:
                rA_w[i] += 2.0 * strength[i]
            else:
                rV_w[i] += 2.0 * strength[i]
        sA_s = sA_b + rng.normal(0, 0.1, n)   # shuffle wire: no true-class drop
        sV_s = sV_b + rng.normal(0, 0.1, n)
    elif kind == "written_opaque":
        # own drops uniformly (licensed) but UNCORRELATED with recall (not graded)
        own_drop = rng.normal(1.6, 0.1, n)
        sA_w = sA_b.copy()
        sV_w = sV_b.copy()
        for i in range(n):
            (sA_w, sV_w)[labels[i]][i] -= own_drop[i]
        # recall present (strong, so recall_ok) but shuffled wrt L
        rmarg = rng.permutation(np.abs(rng.normal(2.5, 0.3, n)))
        rA_w = rA_b.copy()
        rV_w = rV_b.copy()
        for i in range(n):
            (rA_w, rV_w)[labels[i]][i] += rmarg[i]
        sA_s = sA_b + rng.normal(0, 0.1, n)
        sV_s = sV_b + rng.normal(0, 0.1, n)
    elif kind == "context_only":
        # recall strong (trained frames learned) BUT no held-frame transfer
        sA_w = sA_b + rng.normal(0, 0.1, n)
        sV_w = sV_b + rng.normal(0, 0.1, n)
        rA_w = rA_b.copy()
        rV_w = rV_b.copy()
        for i in range(n):
            (rA_w, rV_w)[labels[i]][i] += rng.uniform(2.0, 3.0)
        sA_s = sA_b + rng.normal(0, 0.1, n)
        sV_s = sV_b + rng.normal(0, 0.1, n)
    elif kind == "no_write":
        # nothing learned: recall ~0, no transfer
        sA_w = sA_b + rng.normal(0, 0.1, n)
        sV_w = sV_b + rng.normal(0, 0.1, n)
        rA_w = rA_b + rng.normal(0, 0.1, n)
        rV_w = rV_b + rng.normal(0, 0.1, n)
        sA_s = sA_b + rng.normal(0, 0.1, n)
        sV_s = sV_b + rng.normal(0, 0.1, n)
    elif kind == "host_damaged":
        # transfer + recall present but host CE blown and real typing destroyed
        strength = rng.uniform(0.5, 2.5, n)
        own_drop = 1.5 * strength
        sA_w = sA_b.copy()
        sV_w = sV_b.copy()
        for i in range(n):
            (sA_w, sV_w)[labels[i]][i] -= own_drop[i]
        rA_w = rA_b.copy()
        rV_w = rV_b.copy()
        for i in range(n):
            (rA_w, rV_w)[labels[i]][i] += 2.0 * strength[i]
        sA_s = sA_b + rng.normal(0, 0.1, n)
        sV_s = sV_b + rng.normal(0, 0.1, n)
        host = {"ce_base": 3.0, "ce_wire": 9.0, "real_L_wire_mean": -0.5,
                "restore_ok": False}
    else:
        raise ValueError(kind)

    return {"labels": labels,
            "sA_base": sA_b, "sV_base": sV_b, "sA_wire": sA_w, "sV_wire": sV_w,
            "sA_shuf": sA_s, "sV_shuf": sV_s,
            "rA_wire": rA_w, "rV_wire": rV_w, "host": host}


def run_validate(alpha: float) -> int:
    print("── §P-TYPE-WRITE --validate (planted worlds, no model) ──")
    want = {"written_graded": "TYPE-WRITTEN+GRADED",
            "written_opaque": "WRITTEN-OPAQUE",
            "context_only": "CONTEXT-ONLY",
            "no_write": "NO-WRITE",
            "host_damaged": "HOST-DAMAGED"}
    ok = True
    for kind, expect in want.items():
        rng = np.random.default_rng(hash(kind) % (2**31))
        b = _world(rng, kind)
        res = compute_gates(b, rng, alpha, n_iter=2000)
        got = res["verdict"]
        good = got == expect
        ok &= good
        print(f"  {kind:16s} -> {got:22s} expect {expect:22s} "
              f"{'✓' if good else '✗ FAIL'}")
    # primitive checks
    rng = np.random.default_rng(0)
    lab = np.array([0, 1, 0, 1])
    L = _signed_L(np.array([5, 5, 5, 5.]), np.array([7, 3, 7, 3.]), lab)
    prim = np.allclose(L, [2, 2, 2, 2])   # label0: sV-sA=2 ; label1: sA-sV=2
    ok &= prim
    print(f"  primitive _signed_L               {'✓' if prim else '✗ FAIL'}")
    r = _spearman(np.array([1, 2, 3, 4.]), np.array([1, 2, 3, 4.]))
    prim2 = abs(r - 1.0) < 1e-9
    ok &= prim2
    print(f"  primitive _spearman monotone      {'✓' if prim2 else '✗ FAIL'}")
    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import operand_multihop3 as mh3
    import torch
    import torch.nn.functional as F
    import writeback_compile as wb  # LoRALinear apparatus (no fork)
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps"
                           or torch.backends.mps.is_available()) else "cpu")
    rng = np.random.default_rng(args.seed)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"          # LM loss over full statements
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    dec, _norm, _lm_head = mh3.resolve_parts(model)
    n_layers = len(dec)
    band = list(range(round(BAND_FRAC[0] * n_layers),
                      round(BAND_FRAC[1] * n_layers) + 1))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[tw] {args.model_id} dev={dev} n_layers={n_layers} "
          f"band=L{band[0]}..L{band[-1]} seeds={args.seeds} steps={args.steps}")

    def tid(w: str) -> int:
        return mh3.first_tid(tok, w)

    def logp_last(prompt: str) -> np.ndarray:
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float()
        return F.log_softmax(lo, dim=-1).cpu().numpy()

    def surprisal(prefix: str, cont: str) -> float:
        """-sum log p(cont tokens | prefix), teacher-forced."""
        pre = tok(prefix, return_tensors="pt").to(dev)
        full = tok(prefix + cont, return_tensors="pt").to(dev)
        n_pre = pre.input_ids.shape[1]
        with torch.no_grad():
            lo = model(**full).logits[0].float()
        lp = F.log_softmax(lo, dim=-1)
        tgt = full.input_ids[0]
        s = 0.0
        for pos in range(n_pre, tgt.shape[0]):
            s += float(lp[pos - 1, tgt[pos]])
        return -s

    def ce_host() -> float:
        tot, n = 0.0, 0
        for t in CE_TEXTS:
            ids = tok(t, return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits[0].float()
            lp = F.log_softmax(lo[:-1], dim=-1)
            tgt = ids.input_ids[0, 1:]
            tot += float(-lp[torch.arange(len(tgt)), tgt].sum())
            n += len(tgt)
        return tot / max(n, 1)

    def eval_members(members: list[str], labels: np.ndarray) -> dict:
        aA_tid, aV_tid = tid("animal"), tid("vehicle")
        sA, sV, rA, rV = [], [], [], []
        for w in members:
            frame = f"The {w}"
            sA.append(np.mean([surprisal(frame, " " + p)
                               for p in HELD_PREDS[0]]))
            sV.append(np.mean([surprisal(frame, " " + p)
                               for p in HELD_PREDS[1]]))
            lp = logp_last(f"A {w} is a kind of")
            rA.append(float(lp[aA_tid]))
            rV.append(float(lp[aV_tid]))
        return {"sA": np.array(sA), "sV": np.array(sV),
                "rA": np.array(rA), "rV": np.array(rV)}

    # ── nonce usability + class assignment ──
    nonces, labels = [], []
    for i, w in enumerate(NONCE_CANDS):
        # usable if "The {w}" appends a stable single leading token for w
        n_the = tok("The", add_special_tokens=False).input_ids
        n_thew = tok(f"The {w}", add_special_tokens=False).input_ids
        if len(n_thew) - len(n_the) >= 1:      # w contributes >=1 token; keep
            nonces.append(w)
            labels.append(i % 2)
    if args.n_nonce:
        keep = args.n_nonce
        # balanced smoke cap
        a = [j for j, in_ in enumerate(labels) if in_ == 0][:keep // 2]
        v = [j for j, in_ in enumerate(labels) if in_ == 1][:keep // 2]
        sel = sorted(a + v)
        nonces = [nonces[j] for j in sel]
        labels = [labels[j] for j in sel]
    labels = np.array(labels, int)
    n = len(nonces)
    print(f"[tw] nonces={n} (animal {int((labels==0).sum())} "
          f"vehicle {int((labels==1).sum())})")

    # ── gate-0: base competence + real-member licensing (metric validity) ──
    print("[tw] gate-0: base licensing of real members …")
    real_members = list(REAL_MEMBERS[0]) + list(REAL_MEMBERS[1])
    real_labels = np.array([0] * len(REAL_MEMBERS[0])
                           + [1] * len(REAL_MEMBERS[1]))
    real_base = eval_members(real_members, real_labels)
    L_real_base = _signed_L(real_base["sA"], real_base["sV"], real_labels)
    real_margin = float(np.mean(L_real_base))
    per_class_ok = (np.mean(L_real_base[real_labels == 0]) > 0
                    and np.mean(L_real_base[real_labels == 1]) > 0)
    n_ok = (labels == 0).sum() >= args.min_class and \
           (labels == 1).sum() >= args.min_class
    gate0_ok = bool(real_margin >= REAL_MARGIN_FLOOR and per_class_ok and n_ok)
    print(f"[tw] gate-0: real-member licensing margin={real_margin:.3f} "
          f"per_class_ok={per_class_ok} n_ok={n_ok} "
          f"-> {'PASS' if gate0_ok else 'FAIL'}")
    (out_dir / "gate0.json").write_text(json.dumps({
        "model_id": args.model_id, "n_nonce": n,
        "real_margin": real_margin, "per_class_ok": bool(per_class_ok),
        "L_real_base": L_real_base.tolist(), "gate0_ok": gate0_ok,
        "nonces": nonces, "labels": labels.tolist()}, indent=2))
    if args.gate0_only:
        return 0 if gate0_ok else 1
    if not gate0_ok and not args.force:
        print("[tw] gate-0 FAIL — stopping (use --force to override)")
        return 1

    # ── base arm ──
    print("[tw] arm base …")
    base = eval_members(nonces, labels)
    ce_base = ce_host()

    # ── wire trainer (LoRA on FFN band; membership-LM objective) ──
    def train_wire(train_labels: np.ndarray, seed: int):
        torch.manual_seed(seed)
        wrapped = []
        params = []
        for li in band:
            m = dec[li].mlp
            for name in ("gate_proj", "up_proj", "down_proj"):
                orig = getattr(m, name)
                lw = wb.LoRALinear(orig, r=args.lora_r, alpha=2 * args.lora_r)
                setattr(m, name, lw)
                wrapped.append((m, name, orig))
                params += [lw.A, lw.B]
        opt = torch.optim.Adam(params, lr=args.lr)
        stmts = [s for w, lb in zip(nonces, train_labels, strict=True)
                 for s in _member_stmts(w, int(lb))]
        batch = tok(stmts, return_tensors="pt", padding=True).to(dev)
        ids, attn = batch.input_ids, batch.attention_mask
        for step in range(args.steps):
            opt.zero_grad()
            lo = model(input_ids=ids, attention_mask=attn).logits.float()
            shift_lo = lo[:, :-1, :]
            shift_tg = ids[:, 1:]
            shift_m = attn[:, 1:].float()
            ce = F.cross_entropy(
                shift_lo.reshape(-1, shift_lo.shape[-1]),
                shift_tg.reshape(-1), reduction="none").reshape(shift_tg.shape)
            loss = (ce * shift_m).sum() / shift_m.sum().clamp_min(1.0)
            loss.backward()
            opt.step()
            if step % max(args.steps // 5, 1) == 0 or step == args.steps - 1:
                print(f"    seed{seed} step {step:4d} loss "
                      f"{float(loss.detach()):.4f}", flush=True)

        def unwrap():
            for m, name, orig in wrapped:
                setattr(m, name, orig)
        return unwrap

    def accum(train_labels, tag):
        acc = {k: [] for k in ("sA", "sV", "rA", "rV")}
        real_L = []
        ce_w = []
        for sd in range(args.seeds):
            unwrap = train_wire(train_labels, sd)
            e = eval_members(nonces, labels)   # eval always TRUE labels
            for k in acc:
                acc[k].append(e[k])
            if sd == 0:
                rb = eval_members(real_members, real_labels)
                real_L.append(float(np.mean(
                    _signed_L(rb["sA"], rb["sV"], real_labels))))
                ce_w.append(ce_host())
            unwrap()
            print(f"[tw] {tag} seed{sd} done", flush=True)
        return ({k: np.mean(acc[k], axis=0) for k in acc},
                (real_L[0] if real_L else np.nan),
                (ce_w[0] if ce_w else np.nan))

    print("[tw] arm wire (true membership) …")
    wire, real_L_wire, ce_wire = accum(labels, "wire")

    print("[tw] arm shuffle (deranged membership) …")
    # derange class labels (matched budget), ensure no fixed point
    perm = labels.copy()
    for _ in range(64):
        perm = rng.permutation(labels)
        if np.any(perm != labels):
            break
    shuf, _, _ = accum(perm, "shuffle")

    # ── restore check: base eval must reproduce (LoRA fully removed) ──
    base2 = eval_members(nonces[:2], labels[:2])
    restore_ok = bool(np.allclose(base2["sA"], base["sA"][:2], atol=1e-3))

    bundle = {
        "labels": labels,
        "sA_base": base["sA"], "sV_base": base["sV"],
        "sA_wire": wire["sA"], "sV_wire": wire["sV"],
        "sA_shuf": shuf["sA"], "sV_shuf": shuf["sV"],
        "rA_wire": wire["rA"], "rV_wire": wire["rV"],
        "host": {"ce_base": ce_base, "ce_wire": ce_wire,
                 "real_L_wire_mean": real_L_wire, "restore_ok": restore_ok},
    }
    res = compute_gates(bundle, rng, args.alpha)
    res["meta"] = {
        "model_id": args.model_id, "n_nonce": n, "seeds": args.seeds,
        "steps": args.steps, "lr": args.lr, "lora_r": args.lora_r,
        "band": [band[0], band[-1]], "gate0_ok": gate0_ok,
        "nonces": nonces, "labels": labels.tolist(),
        "real_margin_base": real_margin, "ce_base": ce_base, "ce_wire": ce_wire,
        "real_L_wire": real_L_wire, "restore_ok": restore_ok,
    }
    res["per_nonce"] = {
        "L_wire": _signed_L(wire["sA"], wire["sV"], labels).tolist(),
        "L_base": _signed_L(base["sA"], base["sV"], labels).tolist(),
        "L_shuf": _signed_L(shuf["sA"], shuf["sV"], labels).tolist(),
        "recall_wire": _signed_recall(wire["rA"], wire["rV"], labels).tolist(),
    }
    (out_dir / "results.json").write_text(json.dumps(res, indent=2))
    print(f"[tw] wrote {out_dir}/results.json")
    g = res["gates"]
    print(f"[tw] TW1 p={g['TW1']['p']:.4f} pass={g['TW1']['pass']} | "
          f"TW2 rho={g['TW2']['value']:.3f} p={g['TW2']['p']:.4f} "
          f"pass={g['TW2']['pass']} | TW3 p={g['TW3']['p']:.4f} "
          f"pass={g['TW3']['pass']} | TW4 p={g['TW4']['p']:.4f} "
          f"pass={g['TW4']['pass']} | recall pass={g['membership_recall']['pass']} "
          f"| host={res['host_sane']}")
    print(f"[tw] L_base={res['means']['L_base']:.3f} "
          f"L_wire={res['means']['L_wire']:.3f} "
          f"L_shuf={res['means']['L_shuf']:.3f}")
    print(f"[tw] VERDICT: {res['verdict']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--gate0-only", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--min-class", type=int, default=8)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-nonce", type=int, default=0,
                    help="smoke: cap nonces (balanced); 0=all")
    ap.add_argument("--out", default="results/type-write/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
