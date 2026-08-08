#!/usr/bin/env python3
"""§P-TYPE-WRITE-V2 — coverage-matched weight-write re-test (FROZEN s322).

Pre-reg: mementum/knowledge/explore/types-are-injectable-relations.md §15.

The s322 audit (§14) found §9/§13 COVERAGE-GAPPED: membership-CE gradients
concentrate at the class-word position while licensing is evaluated in a
bare-NP regime the LoRA never gradient-touched — recall-check/licensing-fail
follows even if weight-installable licensing exists. V2 closes the gap while
keeping generalization as the test:

SINGLE FACTOR changed vs §8: TRAINING COVERAGE.
  - training texts = §8's five classificatory statements (verbatim)
    + four bare-NP licensed frames "The {w} {train_pred}." (true class only)
  - TRAIN_PREDS disjoint from §8's HELD_PREDS; eval stays on HELD_PREDS
    verbatim (comparability with §9) + TRAIN_PREDS (the V4 contrast)
  - control fixed: TRUE derangement (1-labels; §14: v1 permutation left
    ~50% labels correct), matched budget (replays wire per-seed stop step)

Everything else verbatim §8/§9-r3: qwen3-4b, FFN band 0.60-0.80, LoRA r=16,
corridor recipe (kl_weight 10 / ce_budget 0.40 via CLI, evidence-gated stop,
fib snaps, REPLAY/CE texts), L(w) = surprisal(anti) - surprisal(own).

Gates (frozen §15):
  V1 HELD-TRANSFER      mean signed L on HELD preds beats label-perm null.
  V2 CLASS-SPECIFIC     own drop > anti drop on HELD preds (paired).
  V3 DERANGED-NULL      wire beats 1-labels wire on HELD L (paired).
  V4 COVERAGE-CONTRAST  TRAIN-pred licensing (label-perm null + deranged
                        paired) — train-lift without held-lift = MEMORIZED-ONLY.
  V5 HOST-SANE (adv.)   real members licensed; host CE in budget; restore.
Verdicts + a-priori (declared, NOT tuned):
  TYPE-WRITTEN 30 / MEMORIZED-ONLY 35 / CONTEXT-ONLY 20 / NO-WRITE 10 /
  HOST-DAMAGED 5.

Harness (lambda one_way, NO fork): imports type_write for the frozen
construction constants, metric, stop rule and recipe; writeback_compile for
LoRALinear; operand_multihop3 for resolve_parts/first_tid.

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

import type_write as tw  # noqa: E402  (frozen v1 apparatus, verbatim reuse)
from holo_cap import NONCE_CANDS  # noqa: E402

from verbum.dsp.nulls import (  # noqa: E402
    Register,
    gate,
    paired_permutation,
    shuffled_label,
)

# ══════════════════════════════════════════════════════════════════════════
# Construction delta (FROZEN §15). Everything else = tw.* verbatim.
# ══════════════════════════════════════════════════════════════════════════
# Class-selective TRAINING predicates — disjoint from tw.HELD_PREDS.
TRAIN_PREDS = (("ate", "drank", "wandered", "rested"),      # animal
               ("braked", "reversed", "idled", "honked"))    # vehicle

assert not (set(TRAIN_PREDS[0]) | set(TRAIN_PREDS[1])) \
    & (set(tw.HELD_PREDS[0]) | set(tw.HELD_PREDS[1])), \
    "TRAIN_PREDS must be disjoint from HELD_PREDS"


def _train_texts(w: str, cls_i: int) -> list[str]:
    """§8 classificatory statements + bare-NP licensed frames (true class).
    The bare-NP forward regime — nonce subject, loss reaching the predicate
    token — is gradient-touched on DIFFERENT predicates than eval."""
    return tw._member_stmts(w, cls_i) + \
        [f"The {w} {p}." for p in TRAIN_PREDS[cls_i]]


# ══════════════════════════════════════════════════════════════════════════
# Pure statistics + verdict (what --validate exercises; no torch, no model)
# ══════════════════════════════════════════════════════════════════════════
def compute_gates_v2(b: dict, rng: np.random.Generator, alpha: float = 0.05,
                     n_iter: int = 10000) -> dict:
    """b: per-nonce arrays for base/wire/deranged x held/train + recall/host."""
    labels = np.asarray(b["labels"], int)

    def L(tag: str, pool: str) -> np.ndarray:
        return tw._signed_L(b[f"sA_{tag}_{pool}"], b[f"sV_{tag}_{pool}"],
                            labels)

    L_wire_h, L_der_h = L("wire", "held"), L("der", "held")
    L_wire_t, L_der_t = L("wire", "train"), L("der", "train")
    L_base_h, L_base_t = L("base", "held"), L("base", "train")
    recall_w = tw._signed_recall(b["rA_wire"], b["rV_wire"], labels)

    # own/anti surprisal drops on HELD (base - wire), by label
    sA_b, sV_b = np.asarray(b["sA_base_held"], float), np.asarray(b["sV_base_held"], float)  # noqa: E501
    sA_w, sV_w = np.asarray(b["sA_wire_held"], float), np.asarray(b["sV_wire_held"], float)  # noqa: E501
    own_b = np.where(labels == 0, sA_b, sV_b)
    anti_b = np.where(labels == 0, sV_b, sA_b)
    own_w = np.where(labels == 0, sA_w, sV_w)
    anti_w = np.where(labels == 0, sV_w, sA_w)
    d_own, d_anti = own_b - own_w, anti_b - anti_w

    kw = {"claim_register": Register.value, "probe_register": Register.value}

    # ── V1 HELD-TRANSFER (≡ TW1 on held) ──
    def stat_Lh(perm_labels):
        return float(np.mean(tw._signed_L(sA_w, sV_w, perm_labels)))
    v1_null = shuffled_label(stat_Lh, labels, rng, n_iter=min(n_iter, 2000))
    v1 = gate(stat_Lh(labels), v1_null, "greater", alpha,
              "V1_held_transfer", **kw)

    # ── V2 CLASS-SPECIFIC (≡ TW4 on held) ──
    v2_null = paired_permutation(d_own, d_anti, rng, n_iter=n_iter)
    v2 = gate(float(np.mean(d_own - d_anti)), v2_null, "greater", alpha,
              "V2_class_specific", **kw)

    # ── V3 DERANGED-NULL (≡ TW3, control = 1-labels wire) ──
    v3_null = paired_permutation(L_wire_h, L_der_h, rng, n_iter=n_iter)
    v3 = gate(float(np.mean(L_wire_h - L_der_h)), v3_null, "greater", alpha,
              "V3_deranged_null", **kw)

    # ── V4 COVERAGE-CONTRAST: TRAIN-pred licensing (T1 label-perm, T3 paired)
    sA_wt = np.asarray(b["sA_wire_train"], float)
    sV_wt = np.asarray(b["sV_wire_train"], float)

    def stat_Lt(perm_labels):
        return float(np.mean(tw._signed_L(sA_wt, sV_wt, perm_labels)))
    t1_null = shuffled_label(stat_Lt, labels, rng, n_iter=min(n_iter, 2000))
    t1 = gate(stat_Lt(labels), t1_null, "greater", alpha,
              "V4_train_transfer", **kw)
    t3_null = paired_permutation(L_wire_t, L_der_t, rng, n_iter=n_iter)
    t3 = gate(float(np.mean(L_wire_t - L_der_t)), t3_null, "greater", alpha,
              "V4_train_vs_deranged", **kw)

    # ── membership recall (trained frame): NO-WRITE split (≡ v1) ──
    rA_w, rV_w = np.asarray(b["rA_wire"], float), np.asarray(b["rV_wire"], float)

    def stat_recall(perm_labels):
        return float(np.mean(tw._signed_recall(rA_w, rV_w, perm_labels)))
    rec_null = shuffled_label(stat_recall, labels, rng,
                              n_iter=min(n_iter, 2000))
    rec = gate(stat_recall(labels), rec_null, "greater", alpha,
               "membership_recall", **kw)

    # ── V5 HOST-SANE (≡ TW5) ──
    host = b.get("host", {})
    ce_ok = (host.get("ce_wire", 0.0) - host.get("ce_base", 0.0)) <= tw.CE_TOL
    real_ok = host.get("real_L_wire_mean", 1.0) > 0.0
    restore_ok = bool(host.get("restore_ok", True))
    host_sane = bool(ce_ok and real_ok and restore_ok)

    held_ok = bool(v1.verdict and v2.verdict and v3.verdict)
    train_lift = bool(t1.verdict and t3.verdict)
    recall_ok = bool(rec.verdict)

    if not recall_ok:
        verdict = "NO-WRITE"
    elif not host_sane:
        verdict = "HOST-DAMAGED"
    elif held_ok:
        verdict = "TYPE-WRITTEN"
    elif train_lift:
        verdict = "MEMORIZED-ONLY"
    else:
        verdict = "CONTEXT-ONLY"

    return {
        "verdict": verdict,
        "held_ok": held_ok, "train_lift": train_lift,
        "recall_ok": recall_ok, "host_sane": host_sane,
        "gates": {
            "V1": tw._gd(v1), "V2": tw._gd(v2), "V3": tw._gd(v3),
            "V4_train": tw._gd(t1), "V4_train_vs_der": tw._gd(t3),
            "membership_recall": tw._gd(rec),
            "V5_host": {"ce_ok": ce_ok, "real_ok": real_ok,
                        "restore_ok": restore_ok, "pass": host_sane},
        },
        "means": {
            "L_base_held": float(np.mean(L_base_h)),
            "L_wire_held": float(np.mean(L_wire_h)),
            "L_der_held": float(np.mean(L_der_h)),
            "L_base_train": float(np.mean(L_base_t)),
            "L_wire_train": float(np.mean(L_wire_t)),
            "L_der_train": float(np.mean(L_der_t)),
            "recall_wire": float(np.mean(recall_w)),
            "n_nonce": int(labels.size),
        },
    }


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
def _world(rng, kind: str, n: int = 24) -> dict:
    labels = np.array([0, 1] * (n // 2))
    host = {"ce_base": 3.0, "ce_wire": 3.05, "real_L_wire_mean": 1.2,
            "restore_ok": True}

    def base_pool():
        return rng.normal(6.0, 0.4, n), rng.normal(6.0, 0.4, n)

    def drop_own(sA, sV, amount):
        sA, sV = sA.copy(), sV.copy()
        for i in range(n):
            (sA, sV)[labels[i]][i] -= amount[i]
        return sA, sV

    def drop_anti(sA, sV, amount):
        sA, sV = sA.copy(), sV.copy()
        for i in range(n):
            (sA, sV)[1 - labels[i]][i] -= amount[i]
        return sA, sV

    sA_bh, sV_bh = base_pool()
    sA_bt, sV_bt = base_pool()
    big = rng.uniform(1.2, 2.2, n)
    noise = rng.normal(0, 0.1, n)

    # recall installs in every world except no_write
    rA_w = rng.normal(0.0, 0.3, n)
    rV_w = rng.normal(0.0, 0.3, n)
    if kind != "no_write":
        for i in range(n):
            (rA_w, rV_w)[labels[i]][i] += rng.uniform(2.0, 3.0)

    if kind == "type_written":       # held AND train lift; deranged lifts anti
        sA_wh, sV_wh = drop_own(sA_bh, sV_bh, big)
        sA_wt, sV_wt = drop_own(sA_bt, sV_bt, big)
        sA_dh, sV_dh = drop_anti(sA_bh, sV_bh, big)
        sA_dt, sV_dt = drop_anti(sA_bt, sV_bt, big)
    elif kind == "memorized_only":   # train lifts, held does NOT
        sA_wh, sV_wh = sA_bh + noise, sV_bh + noise
        sA_wt, sV_wt = drop_own(sA_bt, sV_bt, big)
        sA_dh, sV_dh = sA_bh + noise, sV_bh + noise
        sA_dt, sV_dt = drop_anti(sA_bt, sV_bt, big)
    elif kind in ("context_only", "no_write"):   # nothing licenses
        sA_wh, sV_wh = sA_bh + noise, sV_bh + noise
        sA_wt, sV_wt = sA_bt + noise, sV_bt + noise
        sA_dh, sV_dh = sA_bh + noise, sV_bh + noise
        sA_dt, sV_dt = sA_bt + noise, sV_bt + noise
    elif kind == "host_damaged":     # transfer present but host burned
        sA_wh, sV_wh = drop_own(sA_bh, sV_bh, big)
        sA_wt, sV_wt = drop_own(sA_bt, sV_bt, big)
        sA_dh, sV_dh = sA_bh + noise, sV_bh + noise
        sA_dt, sV_dt = sA_bt + noise, sV_bt + noise
        host = {"ce_base": 3.0, "ce_wire": 9.0, "real_L_wire_mean": -0.5,
                "restore_ok": False}
    else:
        raise ValueError(kind)

    return {"labels": labels,
            "sA_base_held": sA_bh, "sV_base_held": sV_bh,
            "sA_base_train": sA_bt, "sV_base_train": sV_bt,
            "sA_wire_held": sA_wh, "sV_wire_held": sV_wh,
            "sA_wire_train": sA_wt, "sV_wire_train": sV_wt,
            "sA_der_held": sA_dh, "sV_der_held": sV_dh,
            "sA_der_train": sA_dt, "sV_der_train": sV_dt,
            "rA_wire": rA_w, "rV_wire": rV_w, "host": host}


def run_validate(alpha: float) -> int:
    print("── §P-TYPE-WRITE-V2 --validate (planted worlds, no model) ──")
    want = {"type_written": "TYPE-WRITTEN",
            "memorized_only": "MEMORIZED-ONLY",
            "context_only": "CONTEXT-ONLY",
            "no_write": "NO-WRITE",
            "host_damaged": "HOST-DAMAGED"}
    ok = True
    for kind, expect in want.items():
        rng = np.random.default_rng(hash(kind) % (2**31))
        b = _world(rng, kind)
        res = compute_gates_v2(b, rng, alpha, n_iter=2000)
        got = res["verdict"]
        good = got == expect
        ok &= good
        print(f"  {kind:16s} -> {got:16s} expect {expect:16s} "
              f"{'✓' if good else '✗ FAIL'}")
    # primitives
    lab = np.array([0, 1, 0, 1])
    der = 1 - lab
    prim = bool(np.all(der != lab))
    ok &= prim
    print(f"  primitive 1-labels true derangement  {'✓' if prim else '✗ FAIL'}")
    disjoint = not (set(TRAIN_PREDS[0]) | set(TRAIN_PREDS[1])) \
        & (set(tw.HELD_PREDS[0]) | set(tw.HELD_PREDS[1]))
    ok &= disjoint
    print(f"  primitive TRAIN∩HELD = ∅             {'✓' if disjoint else '✗ FAIL'}")
    texts = _train_texts("wug", 0)
    cover = (len(texts) == 9 and sum(t.startswith("The wug ") for t in texts) >= 4
             and all(p not in " ".join(texts)
                     for p in tw.HELD_PREDS[0] + tw.HELD_PREDS[1]))
    ok &= cover
    print(f"  primitive train texts: 5 stmts + 4 bare-NP, no held preds  "
          f"{'✓' if cover else '✗ FAIL'}")
    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path (structure = v1 run_model; deltas: train texts, dual-pool eval,
# true derangement)
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import operand_multihop3 as mh3
    import torch
    import torch.nn.functional as F
    import writeback_compile as wb
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
    dec, _norm, _lm_head = mh3.resolve_parts(model)
    n_layers = len(dec)
    band = list(range(round(tw.BAND_FRAC[0] * n_layers),
                      round(tw.BAND_FRAC[1] * n_layers) + 1))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[tw2] {args.model_id} dev={dev} n_layers={n_layers} "
          f"band=L{band[0]}..L{band[-1]} seeds={args.seeds} steps={args.steps}")

    def tid(w: str) -> int:
        return mh3.first_tid(tok, w)

    def logp_last(prompt: str) -> np.ndarray:
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float()
        return F.log_softmax(lo, dim=-1).cpu().numpy()

    def surprisal(prefix: str, cont: str) -> float:
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
        for t in tw.CE_TEXTS:
            ids = tok(t, return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits[0].float()
            lp = F.log_softmax(lo[:-1], dim=-1)
            tgt = ids.input_ids[0, 1:]
            tot += float(-lp[torch.arange(len(tgt)), tgt].sum())
            n += len(tgt)
        return tot / max(n, 1)

    def eval_pool(members: list[str], preds) -> tuple[np.ndarray, np.ndarray]:
        sA, sV = [], []
        for w in members:
            frame = f"The {w}"
            sA.append(np.mean([surprisal(frame, " " + p) for p in preds[0]]))
            sV.append(np.mean([surprisal(frame, " " + p) for p in preds[1]]))
        return np.array(sA), np.array(sV)

    def eval_members(members: list[str]) -> dict:
        aA_tid, aV_tid = tid("animal"), tid("vehicle")
        sA_h, sV_h = eval_pool(members, tw.HELD_PREDS)
        sA_t, sV_t = eval_pool(members, TRAIN_PREDS)
        rA, rV = [], []
        for w in members:
            lp = logp_last(f"A {w} is a kind of")
            rA.append(float(lp[aA_tid]))
            rV.append(float(lp[aV_tid]))
        return {"sA_h": sA_h, "sV_h": sV_h, "sA_t": sA_t, "sV_t": sV_t,
                "rA": np.array(rA), "rV": np.array(rV)}

    # ── nonce usability + class assignment (≡ v1) ──
    nonces, labels = [], []
    for i, w in enumerate(NONCE_CANDS):
        n_the = tok("The", add_special_tokens=False).input_ids
        n_thew = tok(f"The {w}", add_special_tokens=False).input_ids
        if len(n_thew) - len(n_the) >= 1:
            nonces.append(w)
            labels.append(i % 2)
    if args.n_nonce:
        keep = args.n_nonce
        a = [j for j, in_ in enumerate(labels) if in_ == 0][:keep // 2]
        v = [j for j, in_ in enumerate(labels) if in_ == 1][:keep // 2]
        sel = sorted(a + v)
        nonces = [nonces[j] for j in sel]
        labels = [labels[j] for j in sel]
    labels = np.array(labels, int)
    n = len(nonces)
    print(f"[tw2] nonces={n} (animal {int((labels == 0).sum())} "
          f"vehicle {int((labels == 1).sum())})")

    # ── gate-0: base real-member licensing on BOTH pred pools ──
    print("[tw2] gate-0: base licensing of real members (held + train) …")
    real_members = list(tw.REAL_MEMBERS[0]) + list(tw.REAL_MEMBERS[1])
    real_labels = np.array([0] * len(tw.REAL_MEMBERS[0])
                           + [1] * len(tw.REAL_MEMBERS[1]))
    rb_e = eval_members(real_members)
    L_real_h = tw._signed_L(rb_e["sA_h"], rb_e["sV_h"], real_labels)
    L_real_t = tw._signed_L(rb_e["sA_t"], rb_e["sV_t"], real_labels)
    m_h, m_t = float(np.mean(L_real_h)), float(np.mean(L_real_t))
    per_class_ok = all(
        np.mean(Lr[real_labels == c]) > 0
        for Lr in (L_real_h, L_real_t) for c in (0, 1))
    n_ok = (labels == 0).sum() >= args.min_class and \
           (labels == 1).sum() >= args.min_class
    gate0_ok = bool(m_h >= tw.REAL_MARGIN_FLOOR
                    and m_t >= tw.REAL_MARGIN_FLOOR
                    and per_class_ok and n_ok)
    print(f"[tw2] gate-0: real margin held={m_h:.3f} train={m_t:.3f} "
          f"per_class_ok={per_class_ok} n_ok={n_ok} "
          f"-> {'PASS' if gate0_ok else 'FAIL'}")
    (out_dir / "gate0.json").write_text(json.dumps({
        "model_id": args.model_id, "n_nonce": n,
        "real_margin_held": m_h, "real_margin_train": m_t,
        "per_class_ok": bool(per_class_ok), "gate0_ok": gate0_ok,
        "nonces": nonces, "labels": labels.tolist()}, indent=2))
    if args.gate0_only:
        return 0 if gate0_ok else 1
    if not gate0_ok and not args.force:
        print("[tw2] gate-0 FAIL — stopping (use --force to override)")
        return 1

    # ── base arm ──
    print("[tw2] arm base …")
    base = eval_members(nonces)
    ce_base = ce_host()

    # ── replay anchor cache (≡ v1 s315 amendment) ──
    rb = tok(tw.REPLAY_TEXTS, return_tensors="pt", padding=True).to(dev)
    with torch.no_grad():
        base_lo = model(**rb).logits.float()
        p_base_replay = torch.softmax(base_lo, dim=-1)
        h_base_replay = -(p_base_replay
                          * F.log_softmax(base_lo, dim=-1)).sum(-1)
    replay_mask = rb.attention_mask.float()
    del base_lo
    print(f"[tw2] replay anchor cached: {len(tw.REPLAY_TEXTS)} texts, "
          f"{int(replay_mask.sum())} positions, kl_weight={args.kl_weight}")

    # ── wire trainer (≡ v1 except stmts = _train_texts) ──
    def train_wire(train_labels: np.ndarray, seed: int,
                   stop_at: int | None = None):
        torch.manual_seed(seed)
        wrapped, params = [], []
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
                 for s in _train_texts(w, int(lb))]
        batch = tok(stmts, return_tensors="pt", padding=True).to(dev)
        ids, attn = batch.input_ids, batch.attention_mask
        snap_set = {s for s in tw.FIB_SNAPS if s < args.steps}
        hist: dict = {"step": [], "mem_ce": [], "kl": [],
                      "host_ce": [], "drift": []}
        n_steps = args.steps if stop_at is None else stop_at
        stop_step, stop_reason = n_steps, ("max_steps" if stop_at is None
                                           else "matched_budget")
        last_good = [p.detach().clone() for p in params]
        last_good_step = -1
        for step in range(n_steps):
            opt.zero_grad()
            lo = model(input_ids=ids, attention_mask=attn).logits.float()
            shift_lo = lo[:, :-1, :]
            shift_tg = ids[:, 1:]
            shift_m = attn[:, 1:].float()
            ce = F.cross_entropy(
                shift_lo.reshape(-1, shift_lo.shape[-1]),
                shift_tg.reshape(-1), reduction="none").reshape(shift_tg.shape)
            mem_ce = (ce * shift_m).sum() / shift_m.sum().clamp_min(1.0)
            lo_r = model(**rb).logits.float()
            lq = F.log_softmax(lo_r, dim=-1)
            kl = ((-(p_base_replay * lq).sum(-1) - h_base_replay)
                  * replay_mask).sum() / replay_mask.sum()
            loss = mem_ce + args.kl_weight * kl
            loss.backward()
            opt.step()
            if step in snap_set:
                ce_h = ce_host()
                hist["step"].append(step)
                hist["mem_ce"].append(float(mem_ce.detach()))
                hist["kl"].append(float(kl.detach()))
                hist["host_ce"].append(ce_h)
                hist["drift"].append(ce_h - ce_base)
                print(f"    seed{seed} snap {step:4d} mem "
                      f"{hist['mem_ce'][-1]:.4f} kl {hist['kl'][-1]:.4f} "
                      f"host_ce {ce_h:.4f} drift {hist['drift'][-1]:+.4f}",
                      flush=True)
                if stop_at is None:
                    keep, reason = tw._stop_decision(
                        hist["step"], hist["mem_ce"], hist["drift"],
                        args.ce_budget, args.plateau_tol, args.min_stop)
                    if reason == "plateau":
                        stop_step, stop_reason = keep, reason
                        print(f"    seed{seed} STOP plateau @ step {step} "
                              f"(keep {keep})", flush=True)
                        break
                    if reason == "ce_budget_rollback":
                        with torch.no_grad():
                            for p, g in zip(params, last_good, strict=True):
                                p.copy_(g)
                        stop_step, stop_reason = keep, reason
                        print(f"    seed{seed} STOP ce-budget @ step {step} "
                              f"-> rollback to step {last_good_step} "
                              f"(keep {keep})", flush=True)
                        break
                    last_good = [p.detach().clone() for p in params]
                    last_good_step = step

        def unwrap():
            for m, name, orig in wrapped:
                setattr(m, name, orig)
        info = {"stop_step": int(stop_step), "stop_reason": stop_reason,
                "seed": seed, "history": hist}
        return unwrap, info

    def accum(train_labels, tag, stops=None):
        acc = {k: [] for k in ("sA_h", "sV_h", "sA_t", "sV_t", "rA", "rV")}
        real_L, ce_w, infos = [], [], []
        for sd in range(args.seeds):
            unwrap, info = train_wire(
                train_labels, sd,
                stop_at=None if stops is None else stops[sd])
            infos.append(info)
            e = eval_members(nonces)      # eval ALWAYS on the same frames
            for k in acc:
                acc[k].append(e[k])
            if sd == 0:
                rme = eval_members(real_members)
                real_L.append(float(np.mean(tw._signed_L(
                    rme["sA_h"], rme["sV_h"], real_labels))))
                ce_w.append(ce_host())
            unwrap()
            print(f"[tw2] {tag} seed{sd} done "
                  f"(stop {info['stop_step']} {info['stop_reason']})",
                  flush=True)
        return ({k: np.mean(acc[k], axis=0) for k in acc},
                (real_L[0] if real_L else np.nan),
                (ce_w[0] if ce_w else np.nan), infos)

    print("[tw2] arm wire (true membership + bare-NP coverage) …")
    wire, real_L_wire, ce_wire, wire_infos = accum(labels, "wire")
    wire_stops = [i["stop_step"] for i in wire_infos]

    # TRUE derangement (§15: every label flipped; matched budget)
    der_labels = 1 - labels
    assert np.all(der_labels != labels)
    print(f"[tw2] arm deranged (1-labels, matched budget {wire_stops}) …")
    der, _, _, der_infos = accum(der_labels, "deranged", stops=wire_stops)

    # ── restore check ──
    base2 = eval_members(nonces[:2])
    restore_ok = bool(np.allclose(base2["sA_h"], base["sA_h"][:2], atol=1e-3))

    bundle = {
        "labels": labels,
        "sA_base_held": base["sA_h"], "sV_base_held": base["sV_h"],
        "sA_base_train": base["sA_t"], "sV_base_train": base["sV_t"],
        "sA_wire_held": wire["sA_h"], "sV_wire_held": wire["sV_h"],
        "sA_wire_train": wire["sA_t"], "sV_wire_train": wire["sV_t"],
        "sA_der_held": der["sA_h"], "sV_der_held": der["sV_h"],
        "sA_der_train": der["sA_t"], "sV_der_train": der["sV_t"],
        "rA_wire": wire["rA"], "rV_wire": wire["rV"],
        "host": {"ce_base": ce_base, "ce_wire": ce_wire,
                 "real_L_wire_mean": real_L_wire, "restore_ok": restore_ok},
    }
    res = compute_gates_v2(bundle, rng, args.alpha)
    res["meta"] = {
        "model_id": args.model_id, "n_nonce": n, "seeds": args.seeds,
        "steps": args.steps, "lr": args.lr, "lora_r": args.lora_r,
        "band": [band[0], band[-1]], "gate0_ok": gate0_ok,
        "nonces": nonces, "labels": labels.tolist(),
        "real_margin_held": m_h, "real_margin_train": m_t,
        "ce_base": ce_base, "ce_wire": ce_wire,
        "real_L_wire": real_L_wire, "restore_ok": restore_ok,
        "kl_weight": args.kl_weight, "ce_budget": args.ce_budget,
        "plateau_tol": args.plateau_tol, "min_stop": args.min_stop,
        "train_preds": [list(TRAIN_PREDS[0]), list(TRAIN_PREDS[1])],
        "held_preds": [list(tw.HELD_PREDS[0]), list(tw.HELD_PREDS[1])],
        "wire_stops": wire_stops,
        "wire_stop_reasons": [i["stop_reason"] for i in wire_infos],
    }
    res["training"] = {"wire": wire_infos, "deranged": der_infos}
    res["per_nonce"] = {
        "L_wire_held": tw._signed_L(wire["sA_h"], wire["sV_h"], labels).tolist(),
        "L_base_held": tw._signed_L(base["sA_h"], base["sV_h"], labels).tolist(),
        "L_der_held": tw._signed_L(der["sA_h"], der["sV_h"], labels).tolist(),
        "L_wire_train": tw._signed_L(wire["sA_t"], wire["sV_t"], labels).tolist(),
        "L_base_train": tw._signed_L(base["sA_t"], base["sV_t"], labels).tolist(),
        "L_der_train": tw._signed_L(der["sA_t"], der["sV_t"], labels).tolist(),
        "recall_wire": tw._signed_recall(wire["rA"], wire["rV"], labels).tolist(),
    }
    (out_dir / "results.json").write_text(json.dumps(res, indent=2))
    print(f"[tw2] wrote {out_dir}/results.json")
    g = res["gates"]
    print(f"[tw2] V1 p={g['V1']['p']:.4f} pass={g['V1']['pass']} | "
          f"V2 p={g['V2']['p']:.4f} pass={g['V2']['pass']} | "
          f"V3 p={g['V3']['p']:.4f} pass={g['V3']['pass']} | "
          f"V4t p={g['V4_train']['p']:.4f} pass={g['V4_train']['pass']} | "
          f"V4d p={g['V4_train_vs_der']['p']:.4f} "
          f"pass={g['V4_train_vs_der']['pass']} | "
          f"recall pass={g['membership_recall']['pass']} | "
          f"host={res['host_sane']}")
    m = res["means"]
    print(f"[tw2] held: base={m['L_base_held']:.3f} wire={m['L_wire_held']:.3f} "
          f"der={m['L_der_held']:.3f} | train: base={m['L_base_train']:.3f} "
          f"wire={m['L_wire_train']:.3f} der={m['L_der_train']:.3f}")
    print(f"[tw2] VERDICT: {res['verdict']}")
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
    ap.add_argument("--kl-weight", type=float, default=10.0,
                    help="s315 corridor: KL(base||wire) replay anchor (r3)")
    ap.add_argument("--ce-budget", type=float, default=0.40,
                    help="s315 corridor: max host-CE drift before rollback (r3)")
    ap.add_argument("--plateau-tol", type=float, default=0.01)
    ap.add_argument("--min-stop", type=int, default=55)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-nonce", type=int, default=0,
                    help="smoke: cap nonces (balanced); 0=all")
    ap.add_argument("--out", default="results/type-write-v2/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
