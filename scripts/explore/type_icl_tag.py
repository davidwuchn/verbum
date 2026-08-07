#!/usr/bin/env python3
"""§P-TYPE-ICL+TAG — tape-side converse of §P-TYPE-WRITE + tag-transit read.

Pre-reg: mementum/knowledge/explore/types-are-injectable-relations.md §10
(FROZEN s315, Michael-approved).

(a) Does TAPE-resident membership produce held-frame licensing transfer —
the exact §8 metric the baked FFN wire failed (§9 CONTEXT-ONLY)?
(b) WHERE does the class tag travel — T(w) = signed projection of the
residual at the last token of "The {w}" (the position feeding the check)
onto the real-member class axis. Registers named (λ measure): L = value
register (surprisal); T = residual-CONTENT register (loose bus) — NOT the
s270 workspace basis (P-TYPE-JS s286 negative stands, not re-tested).

Arms: A0 base | A1 ICL-true | A2 ICL-deranged | A3 mention | A4 real
anchor (TI5) | A5 wire-contrast (advisory; §8 recipe under the s315
corridor kl_weight 10 / ce_budget 0.40, eval-only capture).

Gates: TI1 TAPE-LICENSING (L(A1)-L(A0), label-perm null) · TI2
CONTENT-SPECIFIC (A1 vs A2 paired) · TI3 CLASS-NOT-MENTION (A1 vs A3
paired) · TI4 TAG-TRANSIT (T(A1)-T(A0) vs matched-random-axis n=1000 AND
member-label-shuffled-axis n=200; advisory Spearman(T,L)) · TI5
METRIC-SANE void-gate.

Verdicts: TAPE-TYPED(+TAG-TRANSIT) / TAPE-TYPED-OPAQUE / MENTION-ONLY /
NO-TAPE-TRANSFER / VOID.
⚠ BUILD AMENDMENT (validate-forced, pre-run, pending Michael at GO): the
frozen tree leaves the cell TI1∧TI3∧¬TI2 uncovered (licensing lifts vs
base and vs mention, but deranged statements license equally = class
content not read). Named CLASS-BLIND; a-priori mass carved from
TAPE-TYPED: 45/20/10/15/5 + 5 CLASS-BLIND. Wire-contrast subtag (declared
thresholds, ratio r_tag=(T_A5-T_A0)/(T_A1-T_A0), only when TI4 passes):
r≤0.25 DELIVERY-FAILURE / r≥0.75 TAG-INSUFFICIENT / else AMBIGUOUS.

Harness (λ one_way, no fork): imports type_write (CLASSES, HELD_PREDS,
_signed_L, _stop_decision, REPLAY_TEXTS, FIB_SNAPS, recipe constants) +
verbum.jlens (capture_residuals) + writeback_compile (LoRALinear). The A5
trainer re-expresses the amended type_write loop (~50 lines, closure not
importable — the s309 precedent).

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
    shuffled_label,
)

# ══════════════════════════════════════════════════════════════════════════
# Construction (FROZEN §10)
# ══════════════════════════════════════════════════════════════════════════
BAND_DEPTH = (0.50, 0.85)      # T gate aggregate: L18..L30 of 36
N_RAND_AXES = 1000
N_SHUF_AXES = 200
SUBTAG_LO, SUBTAG_HI = 0.25, 0.75   # declared pre-run (build amendment)


def icl_true_prefix(w: str, cls_i: int) -> str:
    return tw._member_stmts(w, cls_i)[0] + " "        # "A {w} is an animal. "


def icl_deranged_prefix(w: str, cls_i: int) -> str:
    return tw._member_stmts(w, 1 - cls_i)[0] + " "    # anti-class statement


def mention_prefix(w: str) -> str:
    return f"I saw a {w} yesterday. "


# ══════════════════════════════════════════════════════════════════════════
# Pure statistics + verdict (what --validate exercises; no torch, no model)
# ══════════════════════════════════════════════════════════════════════════
def band_layers(n_layers: int) -> list[int]:
    return list(range(round(BAND_DEPTH[0] * n_layers),
                      round(BAND_DEPTH[1] * n_layers) + 1))


def signed_T(h: np.ndarray, axes: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Band-mean signed class-tag projection per nonce.

    h: (n, L, d) residuals at the licensing position, band layers only.
    axes: (L, d) unit class axes (animal - vehicle direction).
    labels: (n,) 0=animal 1=vehicle. Sign fixed by true class: own-class
    direction present ⟺ T>0."""
    proj = np.einsum("nld,ld->nl", h, axes)           # (n, L)
    sign = np.where(np.asarray(labels, int) == 0, 1.0, -1.0)
    return proj.mean(axis=1) * sign


def class_axes(h_members: np.ndarray, member_labels: np.ndarray) -> np.ndarray:
    """(m, L, d) member residuals → (L, d) unit axes mean(A) - mean(V)."""
    lab = np.asarray(member_labels, int)
    ax = h_members[lab == 0].mean(axis=0) - h_members[lab == 1].mean(axis=0)
    norm = np.linalg.norm(ax, axis=-1, keepdims=True)
    return ax / np.clip(norm, 1e-12, None)


def subtag(t_a0: float, t_a1: float, t_a5: float, ti4_pass: bool) -> str:
    """Wire-contrast subtag (declared thresholds; AMBIGUOUS unless TI4)."""
    if not ti4_pass or not np.isfinite(t_a5):
        return "AMBIGUOUS"
    denom = t_a1 - t_a0
    if abs(denom) < 1e-12:
        return "AMBIGUOUS"
    r = (t_a5 - t_a0) / denom
    if r <= SUBTAG_LO:
        return "DELIVERY-FAILURE"
    if r >= SUBTAG_HI:
        return "TAG-INSUFFICIENT"
    return "AMBIGUOUS"


def compute_gates_icl(b: dict, rng: np.random.Generator, alpha: float = 0.05,
                      n_iter: int = 10000) -> dict:
    """b holds per-nonce arrays + tag tables + precomputed axis-null draws.
    Pure — --validate plants b directly."""
    labels = np.asarray(b["labels"], int)
    L = {arm: tw._signed_L(b[f"sA_{arm}"], b[f"sV_{arm}"], labels)
         for arm in ("a0", "a1", "a2", "a3")}

    # ── TI1 TAPE-LICENSING: mean(L(A1)-L(A0)) beats label-permutation ──
    def stat_ti1(perm_labels):
        return float(np.mean(
            tw._signed_L(b["sA_a1"], b["sV_a1"], perm_labels)
            - tw._signed_L(b["sA_a0"], b["sV_a0"], perm_labels)))
    ti1_null = shuffled_label(stat_ti1, labels, rng, n_iter=min(n_iter, 2000))
    ti1 = gate(stat_ti1(labels), ti1_null, "greater", alpha,
               "TI1_tape_licensing",
               claim_register=Register.value, probe_register=Register.value)

    # ── TI2 CONTENT-SPECIFIC: A1 beats deranged A2 (paired) ──
    ti2_null = paired_permutation(L["a1"], L["a2"], rng, n_iter=n_iter)
    ti2 = gate(float(np.mean(L["a1"] - L["a2"])), ti2_null, "greater", alpha,
               "TI2_content_specific",
               claim_register=Register.value, probe_register=Register.value)

    # ── TI3 CLASS-NOT-MENTION: A1 beats mention A3 (paired) ──
    ti3_null = paired_permutation(L["a1"], L["a3"], rng, n_iter=n_iter)
    ti3 = gate(float(np.mean(L["a1"] - L["a3"])), ti3_null, "greater", alpha,
               "TI3_class_not_mention",
               claim_register=Register.value, probe_register=Register.value)

    # ── TI4 TAG-TRANSIT: T(A1)-T(A0) beats both axis nulls ──
    t_a0, t_a1 = np.asarray(b["T_a0"], float), np.asarray(b["T_a1"], float)
    s_tag = float(np.mean(t_a1 - t_a0))
    ti4_rand = gate(s_tag, NullDraws("matched_random_axis",
                                     np.asarray(b["tag_null_rand"], float),
                                     {"n": N_RAND_AXES}),
                    "greater", alpha, "TI4_tag_vs_random_axis",
                    claim_register=Register.value,
                    probe_register=Register.value)
    ti4_shuf = gate(s_tag, NullDraws("member_label_shuffled_axis",
                                     np.asarray(b["tag_null_shuf"], float),
                                     {"n": N_SHUF_AXES}),
                    "greater", alpha, "TI4_tag_vs_shuffled_axis",
                    claim_register=Register.value,
                    probe_register=Register.value)
    ti4_pass = bool(ti4_rand.verdict and ti4_shuf.verdict)
    rho_tl = tw._spearman(t_a1, L["a1"])              # advisory

    # ── TI5 METRIC-SANE (void-gate) ──
    m = b.get("metric", {})
    real_ok = (m.get("real_margin", 0.0) >= tw.REAL_MARGIN_FLOOR
               and bool(m.get("per_class_ok", False)))
    icl_sane = m.get("real_icl_margin", 1.0) > 0.0
    ti5_pass = bool(real_ok and icl_sane)

    # ── verdict tree (frozen + CLASS-BLIND build amendment) ──
    if not ti5_pass:
        verdict = "VOID"
    elif not ti1.verdict:
        verdict = "NO-TAPE-TRANSFER"
    elif not ti3.verdict:
        verdict = "MENTION-ONLY"
    elif not ti2.verdict:
        verdict = "CLASS-BLIND"
    elif ti4_pass:
        verdict = "TAPE-TYPED+TAG-TRANSIT"
    else:
        verdict = "TAPE-TYPED-OPAQUE"

    t_a5 = float(np.mean(b["T_a5"])) if "T_a5" in b else float("nan")
    tag = subtag(float(np.mean(t_a0)), float(np.mean(t_a1)), t_a5, ti4_pass)

    return {
        "verdict": verdict, "subtag": tag,
        "gates": {
            "TI1": tw._gd(ti1), "TI2": tw._gd(ti2), "TI3": tw._gd(ti3),
            "TI4_rand": tw._gd(ti4_rand), "TI4_shuf": tw._gd(ti4_shuf),
            "TI4_pass": ti4_pass,
            "TI5": {"real_ok": real_ok, "icl_sane": icl_sane,
                    "pass": ti5_pass},
        },
        "means": {
            "L_a0": float(np.mean(L["a0"])), "L_a1": float(np.mean(L["a1"])),
            "L_a2": float(np.mean(L["a2"])), "L_a3": float(np.mean(L["a3"])),
            "T_a0": float(np.mean(t_a0)), "T_a1": float(np.mean(t_a1)),
            "T_a5": t_a5, "S_tag": s_tag, "rho_T_L": rho_tl,
            "n_nonce": int(labels.size),
        },
    }


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
def _world_icl(rng, kind: str, n: int = 24) -> dict:
    labels = np.array([0, 1] * (n // 2))
    base_s = lambda: rng.normal(6.0, 0.3, n)                    # noqa: E731
    b: dict = {"labels": labels}
    # default: no arm licenses (all L ~ 0)
    for arm in ("a0", "a1", "a2", "a3"):
        b[f"sA_{arm}"], b[f"sV_{arm}"] = base_s(), base_s()
    # default tags: nothing present, nulls centred at 0
    b["T_a0"] = rng.normal(0.0, 0.05, n)
    b["T_a1"] = rng.normal(0.0, 0.05, n)
    b["tag_null_rand"] = rng.normal(0.0, 0.02, N_RAND_AXES)
    b["tag_null_shuf"] = rng.normal(0.0, 0.02, N_SHUF_AXES)
    b["metric"] = {"real_margin": 2.5, "per_class_ok": True,
                   "real_icl_margin": 1.5}

    def lift_own(arm: str, amount: np.ndarray):
        sA, sV = b[f"sA_{arm}"], b[f"sV_{arm}"]
        for i in range(n):
            (sA, sV)[labels[i]][i] -= amount[i]       # own-class cheaper

    if kind == "tape_typed_transit":
        amt = rng.uniform(1.0, 2.0, n)
        lift_own("a1", amt)
        b["T_a1"] = 0.8 * amt + rng.normal(0, 0.05, n)
        b["T_a5"] = rng.normal(0.0, 0.05, n)          # wire tag absent
    elif kind == "tape_typed_opaque":
        lift_own("a1", rng.uniform(1.2, 1.8, n))      # licenses, tag flat
    elif kind == "mention_only":
        amt = rng.uniform(1.2, 1.8, n)
        lift_own("a1", amt)
        lift_own("a3", amt + rng.normal(0, 0.05, n))  # mention matches A1
        lift_own("a2", rng.uniform(0.0, 0.1, n))
    elif kind == "class_blind":
        amt = rng.uniform(1.2, 1.8, n)
        lift_own("a1", amt)
        lift_own("a2", amt + rng.normal(0, 0.05, n))  # deranged matches A1
    elif kind == "no_tape_transfer":
        pass                                          # defaults: nothing
    elif kind == "void":
        lift_own("a1", rng.uniform(1.2, 1.8, n))
        b["metric"] = {"real_margin": -0.3, "per_class_ok": False,
                       "real_icl_margin": 1.0}
    elif kind == "subtag_insufficient":
        amt = rng.uniform(1.0, 2.0, n)
        lift_own("a1", amt)
        b["T_a1"] = 0.8 * amt + rng.normal(0, 0.05, n)
        b["T_a5"] = b["T_a1"] + rng.normal(0, 0.02, n)  # wire tag ≈ ICL tag
    else:
        raise ValueError(kind)
    return b


def run_validate(alpha: float) -> int:
    print("── §P-TYPE-ICL+TAG --validate (planted worlds, no model) ──")
    want = {"tape_typed_transit": ("TAPE-TYPED+TAG-TRANSIT", "DELIVERY-FAILURE"),
            "tape_typed_opaque": ("TAPE-TYPED-OPAQUE", "AMBIGUOUS"),
            "mention_only": ("MENTION-ONLY", None),
            "class_blind": ("CLASS-BLIND", None),
            "no_tape_transfer": ("NO-TAPE-TRANSFER", None),
            "void": ("VOID", None),
            "subtag_insufficient": ("TAPE-TYPED+TAG-TRANSIT",
                                    "TAG-INSUFFICIENT")}
    ok = True
    for kind, (expect_v, expect_s) in want.items():
        rng = np.random.default_rng(hash(kind) % (2**31))
        res = compute_gates_icl(_world_icl(rng, kind), rng, alpha,
                                n_iter=2000)
        good = res["verdict"] == expect_v
        if expect_s is not None:
            good &= res["subtag"] == expect_s
        ok &= good
        print(f"  {kind:22s} -> {res['verdict']:24s} subtag "
              f"{res['subtag']:18s} expect {expect_v}"
              f"{('/' + expect_s) if expect_s else '':20s} "
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
    axes = class_axes(np.stack([h[0], h[0], h[1], h[1]]),
                      np.array([0, 0, 1, 1]))
    prim2 = np.allclose(np.linalg.norm(axes, axis=-1), 1.0)
    ok &= prim2
    print(f"  primitive class_axes unit-norm    {'✓' if prim2 else '✗ FAIL'}")
    prim3 = (subtag(0.0, 1.0, 0.1, True) == "DELIVERY-FAILURE"
             and subtag(0.0, 1.0, 0.9, True) == "TAG-INSUFFICIENT"
             and subtag(0.0, 1.0, 0.5, True) == "AMBIGUOUS"
             and subtag(0.0, 1.0, 0.9, False) == "AMBIGUOUS")
    ok &= prim3
    print(f"  primitive subtag thresholds       {'✓' if prim3 else '✗ FAIL'}")
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
    print(f"[ti] {args.model_id} dev={dev} n_layers={nl} "
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

    def arm_L(prefix_fn) -> tuple[np.ndarray, np.ndarray]:
        sA, sV = [], []
        for w, lb in zip(nonces, labels, strict=True):
            pre = prefix_fn(w, int(lb)) + f"The {w}"
            sA.append(np.mean([surprisal(pre, " " + p)
                               for p in tw.HELD_PREDS[0]]))
            sV.append(np.mean([surprisal(pre, " " + p)
                               for p in tw.HELD_PREDS[1]]))
        return np.array(sA), np.array(sV)

    def arm_T(prefix_fn) -> np.ndarray:
        return np.stack([capture_band(prefix_fn(w, int(lb)) + f"The {w}")
                         for w, lb in zip(nonces, labels, strict=True)])

    # ── nonce selection (type_write pattern) ──
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
    print(f"[ti] nonces={len(nonces)} (animal {int((labels == 0).sum())} "
          f"vehicle {int((labels == 1).sum())})")

    # ── A4 + TI5: real-member anchor, bare + own-class ICL prefix ──
    real_members = list(tw.REAL_MEMBERS[0]) + list(tw.REAL_MEMBERS[1])
    real_labels = np.array([0] * len(tw.REAL_MEMBERS[0])
                           + [1] * len(tw.REAL_MEMBERS[1]))
    print("[ti] A4 anchor: real-member licensing (bare + ICL prefix) …")
    rA, rV, riA, riV = [], [], [], []
    for w, lb in zip(real_members, real_labels, strict=True):
        pre = f"The {w}"
        rA.append(np.mean([surprisal(pre, " " + p) for p in tw.HELD_PREDS[0]]))
        rV.append(np.mean([surprisal(pre, " " + p) for p in tw.HELD_PREDS[1]]))
        prei = icl_true_prefix(w, int(lb)) + f"The {w}"
        riA.append(np.mean([surprisal(prei, " " + p)
                            for p in tw.HELD_PREDS[0]]))
        riV.append(np.mean([surprisal(prei, " " + p)
                            for p in tw.HELD_PREDS[1]]))
    L_real = tw._signed_L(np.array(rA), np.array(rV), real_labels)
    L_real_icl = tw._signed_L(np.array(riA), np.array(riV), real_labels)
    metric = {
        "real_margin": float(np.mean(L_real)),
        "per_class_ok": bool(np.mean(L_real[real_labels == 0]) > 0
                             and np.mean(L_real[real_labels == 1]) > 0),
        "real_icl_margin": float(np.mean(L_real_icl)),
    }
    print(f"[ti] real margin={metric['real_margin']:.3f} "
          f"icl_margin={metric['real_icl_margin']:.3f} "
          f"per_class_ok={metric['per_class_ok']}")

    # ── class axes from real members (bare frames, fixed reference) ──
    print("[ti] class axes from real members …")
    h_members = np.stack([capture_band(f"The {w}") for w in real_members])
    axes = class_axes(h_members, real_labels)

    # ── arms A0-A3: L + T ──
    prefix_fns = {"a0": lambda w, c: "",
                  "a1": lambda w, c: icl_true_prefix(w, c),
                  "a2": lambda w, c: icl_deranged_prefix(w, c),
                  "a3": lambda w, c: mention_prefix(w)}
    b: dict = {"labels": labels, "metric": metric}
    h_arm: dict = {}
    for arm, pf in prefix_fns.items():
        print(f"[ti] arm {arm} …", flush=True)
        b[f"sA_{arm}"], b[f"sV_{arm}"] = arm_L(pf)
        h_arm[arm] = arm_T(pf)
    b["T_a0"] = signed_T(h_arm["a0"], axes, labels)
    b["T_a1"] = signed_T(h_arm["a1"], axes, labels)
    T_a2 = signed_T(h_arm["a2"], axes, labels)        # advisory
    T_a3 = signed_T(h_arm["a3"], axes, labels)        # advisory

    # ── TI4 nulls (λ yardstick: fixed reference, matched nulls) ──
    print("[ti] TI4 nulls: random axes + shuffled member labels …")
    d = axes.shape[-1]
    def tag_stat(ax):
        return float(np.mean(signed_T(h_arm["a1"], ax, labels)
                             - signed_T(h_arm["a0"], ax, labels)))
    rand_draws = []
    for _ in range(N_RAND_AXES):
        ra = rng.normal(size=(len(tband), d))
        ra /= np.linalg.norm(ra, axis=-1, keepdims=True)
        rand_draws.append(tag_stat(ra))
    shuf_draws = []
    for _ in range(N_SHUF_AXES):
        perm = rng.permutation(real_labels)
        shuf_draws.append(tag_stat(class_axes(h_members, perm)))
    b["tag_null_rand"] = np.array(rand_draws)
    b["tag_null_shuf"] = np.array(shuf_draws)

    # ── A5 wire-contrast (advisory): §8 recipe, s315 corridor ──
    if args.with_wire:
        print("[ti] arm A5: wire (s315 corridor, 3 seeds) …")
        rb = tok(tw.REPLAY_TEXTS, return_tensors="pt", padding=True).to(dev)
        with torch.no_grad():
            blo = model(**rb).logits.float()
            p_base = torch.softmax(blo, dim=-1)
            h_base = -(p_base * F.log_softmax(blo, dim=-1)).sum(-1)
        rmask = rb.attention_mask.float()
        del blo

        def ce_host() -> float:
            tot, n = 0.0, 0
            for t in tw.CE_TEXTS:
                ids = tok(t, return_tensors="pt").to(dev)
                with torch.no_grad():
                    lo = model(**ids).logits[0].float()
                lp = F.log_softmax(lo[:-1], dim=-1)
                tgt = ids.input_ids[0, 1:]
                tot += float(-lp[torch.arange(len(tgt)), tgt].sum())
                n += len(tgt)
            return tot / max(n, 1)

        ce0 = ce_host()
        T5_seeds = []
        for sd in range(args.seeds):
            torch.manual_seed(sd)
            wrapped, params = [], []
            for li in wband:
                m = dec[li].mlp
                for name in ("gate_proj", "up_proj", "down_proj"):
                    orig = getattr(m, name)
                    lw = wb.LoRALinear(orig, r=args.lora_r,
                                       alpha=2 * args.lora_r)
                    setattr(m, name, lw)
                    wrapped.append((m, name, orig))
                    params += [lw.A, lw.B]
            opt = torch.optim.Adam(params, lr=args.lr)
            stmts = [s for w, lb in zip(nonces, labels, strict=True)
                     for s in tw._member_stmts(w, int(lb))]
            batch = tok(stmts, return_tensors="pt", padding=True).to(dev)
            ids, attn = batch.input_ids, batch.attention_mask
            snap_set = {s for s in tw.FIB_SNAPS if s < args.steps}
            hist: dict = {"step": [], "mem_ce": [], "drift": []}
            last_good = [p.detach().clone() for p in params]
            for step in range(args.steps):
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
                kl = ((-(p_base * lq).sum(-1) - h_base)
                      * rmask).sum() / rmask.sum()
                (mem_ce + args.kl_weight * kl).backward()
                opt.step()
                if step in snap_set:
                    drift = ce_host() - ce0
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
            T5_seeds.append(signed_T(arm_T(prefix_fns["a0"]), axes, labels))
            for m, name, orig in wrapped:
                setattr(m, name, orig)
            n_done = hist["step"][-1] + 1 if hist["step"] else 0
            print(f"[ti] A5 seed{sd} done (steps {n_done}+)", flush=True)
        b["T_a5"] = np.mean(T5_seeds, axis=0)

    # ── gates + verdict ──
    res = compute_gates_icl(b, rng, args.alpha)
    res["meta"] = {
        "model_id": args.model_id, "n_nonce": len(nonces),
        "nonces": nonces, "labels": labels.tolist(),
        "t_band": [tband[0], tband[-1]], "wire_band": [wband[0], wband[-1]],
        "with_wire": bool(args.with_wire), "seeds": args.seeds,
        "steps": args.steps, "lr": args.lr, "lora_r": args.lora_r,
        "kl_weight": args.kl_weight, "ce_budget": args.ce_budget,
        "metric": metric,
        "T_a2_mean": float(np.mean(T_a2)), "T_a3_mean": float(np.mean(T_a3)),
    }
    (out_dir / "results.json").write_text(json.dumps(res, indent=2))
    np.savez_compressed(
        out_dir / "tags.npz",
        T_a0=b["T_a0"], T_a1=b["T_a1"], T_a2=T_a2, T_a3=T_a3,
        T_a5=b.get("T_a5", np.array([])),
        axes=axes, labels=labels)
    print(f"[ti] wrote {out_dir}/results.json")
    g, mn = res["gates"], res["means"]
    print(f"[ti] TI1 p={g['TI1']['p']:.4f} {g['TI1']['pass']} | "
          f"TI2 p={g['TI2']['p']:.4f} {g['TI2']['pass']} | "
          f"TI3 p={g['TI3']['p']:.4f} {g['TI3']['pass']} | "
          f"TI4 rand p={g['TI4_rand']['p']:.4f} shuf p={g['TI4_shuf']['p']:.4f} "
          f"{g['TI4_pass']} | TI5 {g['TI5']['pass']}")
    print(f"[ti] L a0={mn['L_a0']:.3f} a1={mn['L_a1']:.3f} "
          f"a2={mn['L_a2']:.3f} a3={mn['L_a3']:.3f} | "
          f"T a0={mn['T_a0']:.3f} a1={mn['T_a1']:.3f} a5={mn['T_a5']:.3f} "
          f"rho={mn['rho_T_L']:.3f}")
    print(f"[ti] VERDICT: {res['verdict']} | subtag: {res['subtag']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--n-nonce", type=int, default=0)
    ap.add_argument("--with-wire", action=argparse.BooleanOptionalAction,
                    default=True, help="A5 wire-contrast arm")
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
    ap.add_argument("--out", default="results/type-icl-tag/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
