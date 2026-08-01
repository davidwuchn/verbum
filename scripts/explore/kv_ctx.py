#!/usr/bin/env python3
"""§P-KV-1b — the co-encoding term (kv_ctx).

Drafted s295 (Michael "let's proceed with a"). P-KV-1 measured address ⊕
re-encoding = 0.20 acc; CoT = 0.90. Candidate third term: CoT's intermediate
attends the QUESTION while being encoded; P-KV-1's donor was encoded blind.
Isolate that single term with a paired control at FIXED positions.

Layout (one forward, 4D mask, self-checked): A = question ("Consider the
{nonce}." — operand injected at nonce @ L_ref) → B = donor ("It is located in
the country of {x}", padded; with A visible, "It" binds the operand) → C =
readout (" The answer is").
  A rows: causal within A.  B rows: kv_ctx = attend A + causal-in-B;
  kv_blind = causal-in-B ONLY (same donor, same positions, encoded blind).
  C rows: all of A + selected B columns (country tokens) + causal-in-C.

Arms: ctx_base / kv_ctx / kv_blind / kv_ctx_wrong / kv_ctx_rand.
Gates: G1 co-encoding term (kv_ctx>kv_blind margin AND acc); G2
composition-in-layout (kv_ctx>ctx_base + flip); G3 specificity; advisory
yardstick rows (fraction of CoT anchor 0.90; kv_blind vs P-KV-1 kv_nat 0.20).
Verdicts: CO-ENCODING-LOADED / CO-ENCODING-NULL / UNSPECIFIC-CTX /
LAYOUT-BREAKS.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# reuse (no fork)
from fn_stack import COUNTRY_CAP  # noqa: E402
from holo_cap import NONCE_CANDS  # noqa: E402
from holo_frag import _json_safe  # noqa: E402
from kv_splice import OPERAND_DOMAIN, PROSE_DONOR  # noqa: E402
from stack_error_domain import build_categories, classify, first_token  # noqa: E402

from verbum.dsp import gate, paired_permutation  # noqa: E402

CTX_FRAME = "It is located in the country of"      # + " {country}"
A_TEXT = "Consider the {x}."
C_TEXT = " The answer is"
COT_ANCHOR = 0.90                                  # s294 native cot (advisory)
KVNAT_ANCHOR = 0.20                                # P-KV-1 kv_nat (advisory)
ARMS = ("ctx_base", "kv_ctx", "kv_blind", "kv_ctx_wrong", "kv_ctx_rand")


# ══════════════════════════════════════════════════════════════════════════
# Frozen verdict logic (pure; --validate exercises it)
# ══════════════════════════════════════════════════════════════════════════
def score_ctx(m: dict[str, np.ndarray], acc: dict[str, float],
              op_err: dict[str, np.ndarray], swap_hits: int, true_hits: int,
              rng, alpha: float) -> dict:
    def g(a, b, name):
        return gate(float(np.mean(m[a] - m[b])),
                    paired_permutation(m[a], m[b], rng), "greater", alpha,
                    name=name)
    g1 = g("kv_ctx", "kv_blind", "co_encoding_term")     # primary
    flip1 = bool(acc["kv_ctx"] > acc["kv_blind"])
    g2 = g("kv_ctx", "ctx_base", "composition_in_layout")
    flip2 = bool(acc["kv_ctx"] > acc["ctx_base"])
    g3 = g("kv_ctx", "kv_ctx_wrong", "specificity")
    swap_coherent = bool(swap_hits > true_hits)          # advisory
    sec = gate(float(np.mean(op_err["ctx_base"] - op_err["kv_ctx"])),
               paired_permutation(op_err["ctx_base"], op_err["kv_ctx"], rng),
               "greater", alpha, name="operand_err_shift")
    return {"g1": g1, "flip1": flip1, "g2": g2, "flip2": flip2, "g3": g3,
            "swap_coherent": swap_coherent, "swap_hits": swap_hits,
            "true_hits": true_hits, "secondary": sec, "acc": dict(acc),
            "cot_fraction": float(acc["kv_ctx"] / COT_ANCHOR),
            "means": {a: float(np.mean(m[a])) for a in m}}


def verdict_ctx(gate0: bool, sc: dict) -> str:
    if not gate0:
        return "negative/inconclusive (gate-0)"
    if not (sc["g2"].verdict and sc["flip2"]):
        return "LAYOUT-BREAKS"          # P-KV-1 effect lost in A-first layout
    if not (sc["g1"].verdict and sc["flip1"]):
        return "CO-ENCODING-NULL"       # address+re-encoding was the whole story
    if not sc["g3"].verdict:
        return "UNSPECIFIC-CTX"
    return "CO-ENCODING-LOADED"


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
def run_validate(alpha: float) -> int:
    rng = np.random.default_rng(0)
    n, noise = 10, 0.3
    print("── P-KV-1b --validate (planted worlds, no model) ──")
    ok = True

    def world(mu: dict[str, float], accs: dict[str, float], swap=(0, 0)):
        m = {a: mu.get(a, 0.0) + rng.normal(0, noise, n) for a in ARMS}
        op = {"ctx_base": np.array([1.0] * 8 + [0.0] * 2),
              "kv_ctx": np.array([1.0] * 2 + [0.0] * 8)}
        acc = {a: accs.get(a, 0.0) for a in ARMS}
        sc = score_ctx(m, acc, op, swap[0], swap[1], rng, alpha)
        return verdict_ctx(True, sc)

    calls = {
        # co-encoding adds a real term over blind, specific
        "loaded": (world({"kv_ctx": 2.4, "kv_blind": 1.2, "kv_ctx_wrong": 0.4,
                          "kv_ctx_rand": 0.2},
                         {"kv_ctx": 0.7, "kv_blind": 0.2}),
                   "CO-ENCODING-LOADED"),
        # ctx == blind: the address+re-encoding term was everything
        "null": (world({"kv_ctx": 1.2, "kv_blind": 1.2, "kv_ctx_wrong": 0.3},
                       {"kv_ctx": 0.2, "kv_blind": 0.2}),
                 "CO-ENCODING-NULL"),
        # ctx beats blind but wrong-country co-encodes just as well
        "unspecific": (world({"kv_ctx": 2.4, "kv_blind": 1.2,
                              "kv_ctx_wrong": 2.3},
                             {"kv_ctx": 0.7, "kv_blind": 0.2}),
                       "UNSPECIFIC-CTX"),
        # nothing composes in this layout at all
        "layout-breaks": (world({}, {}), "LAYOUT-BREAKS"),
        # margins move over blind but argmax does not -> NULL (flip1 required)
        "no-flip": (world({"kv_ctx": 2.4, "kv_blind": 1.2, "kv_ctx_wrong": 0.4},
                          {"kv_ctx": 0.3, "kv_blind": 0.3, "ctx_base": 0.0}),
                    "CO-ENCODING-NULL"),
    }
    for w, (call, want) in calls.items():
        good = call == want
        print(f"[V] {w}-world -> {call} (want {want}) {'OK' if good else 'FAIL'}")
        ok &= good
    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import operand_multihop3 as mh3
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    rng = np.random.default_rng(args.seed)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype),
        attn_implementation="eager").to(dev).eval()
    dec, _norm, _u = mh3.resolve_parts(model)
    n_layers = len(dec)
    L, S = args.ref_layer, args.scale
    print(f"[kvc] {args.model_id} L_ref={L} scale={S} dev={dev} "
          f"n_layers={n_layers} eager")

    nonce = NONCE_CANDS[0]
    nonce_tid = tok(" " + nonce, add_special_tokens=False).input_ids[-1]

    def first_tid(w):
        return mh3.first_tid(tok, w)

    NEG = torch.finfo(getattr(torch, args.dtype)).min

    def forward_logits(ids_list, mask4d=None, hooks=()):
        ids = torch.tensor([ids_list], device=dev)
        handles = [dec[li].register_forward_hook(mh3.add_hook_at(v, p))
                   for (li, v, p) in hooks]
        with torch.no_grad():
            if mask4d is None:
                lo = model(input_ids=ids).logits
            else:
                lo = model(input_ids=ids, attention_mask=mask4d).logits
        for h in handles:
            h.remove()
        return lo[0, -1, :].float().cpu().numpy()

    # ── mask self-check (gate on instrument) ─────────────────────────────────
    chk_ids = tok("The capital of Portugal is", return_tensors="pt"
                  ).input_ids[0].tolist()
    nchk = len(chk_ids)
    full = torch.full((nchk, nchk), NEG)
    full[torch.tril(torch.zeros(nchk, nchk) == 0)] = 0.0
    full = full[None, None, :, :].to(dtype=getattr(torch, args.dtype), device=dev)
    lo_a, lo_b = forward_logits(chk_ids), forward_logits(chk_ids, mask4d=full)
    dmax = float(np.max(np.abs(lo_a - lo_b)))
    same_arg = bool(np.argmax(lo_a) == np.argmax(lo_b))
    mask_ok = same_arg and dmax < args.mask_tol
    print(f"[kvc] mask self-check: max|dlogit|={dmax:.5f} argmax_same={same_arg} "
          f"-> {'PASS' if mask_ok else 'FAIL'}")
    if not mask_ok:
        print("[kvc] ABORT: unverified mask path")
        return 2

    # ── union / ceilings (inherited) ─────────────────────────────────────────
    cap_labels = sorted({COUNTRY_CAP[mh3.COUNTRY_OF[lm]] for lm in mh3.LM_LIST
                         if mh3.COUNTRY_OF[lm] in COUNTRY_CAP})
    vocab = (set(mh3.CONTINENTS) | set(mh3.COUNTRIES) | set(mh3.CITIES)
             | set(cap_labels))
    tid_map, drop = {}, set()
    for w in sorted(vocab):
        t = first_tid(w)
        clash = [x for x, tt in tid_map.items() if tt == t]
        if clash:
            drop.add(w)
            drop.update(clash)
        tid_map[w] = t
    union = {w: tid_map[w] for w in sorted(vocab - drop)}
    print(f"[kvc] union candidates: {len(union)} (dropped: {sorted(drop)})")

    def real_pred(prefix, query, word, labels):
        ids = tok(prefix + query.format(x=word), return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        return max(labels, key=lambda w: lo[first_tid(w)])

    pref = ("The capital of Portugal is Lisbon.\nThe capital of Japan is Tokyo.\n"
            "The capital of Kenya is Nairobi.\n")
    valid = []
    for lm in mh3.LM_LIST:
        c = mh3.COUNTRY_OF[lm]
        if c not in COUNTRY_CAP or mh3.CITY_OF[lm] == COUNTRY_CAP[c]:
            continue
        if first_token(real_pred(pref, "The capital of {x} is", c,
                                 list(COUNTRY_CAP.values()))
                       ) == first_token(COUNTRY_CAP[c]):
            valid.append(lm)
    gate0 = mask_ok and len(valid) >= 6
    print(f"[kvc] ceilings: valid landmarks {len(valid)}/{len(mh3.LM_LIST)} "
          f"gate0={gate0}")
    if args.n_cells:
        valid = valid[:args.n_cells]

    # ── operand directions @ L_ref ───────────────────────────────────────────
    def build_dirs(items, cap_L):
        per = {e: [] for e in items}
        for fr in mh3.FRAMES:
            for e in items:
                store: dict[int, np.ndarray] = {}
                h = dec[cap_L].register_forward_hook(mh3.cap_hook(store, cap_L))
                ids = tok(fr.format(x=e), return_tensors="pt").to(dev)
                with torch.no_grad():
                    model(**ids)
                h.remove()
                per[e].append(store[cap_L][0, -2, :])
        em = {e: np.mean(per[e], axis=0) for e in items}
        gm = np.mean([em[e] for e in items], axis=0)
        return {e: em[e] - gm for e in items}

    d_lm = build_dirs(mh3.LM_LIST, L)
    test_countries = sorted({mh3.COUNTRY_OF[lm] for lm in valid})

    def derange(cs):
        n = len(cs)
        return {cs[i]: cs[(i + 1) % n] for i in range(n)} if n > 1 else {}

    wrong_of = derange(test_countries)

    # ── segments ─────────────────────────────────────────────────────────────
    a_ids = tok(A_TEXT.format(x=nonce), return_tensors="pt").input_ids[0].tolist()
    c_ids = tok(C_TEXT, add_special_tokens=False).input_ids
    occ = [i for i, t in enumerate(a_ids) if t == nonce_tid][-1]
    pad_ids = tok(" and so on", add_special_tokens=False).input_ids

    def donor_ids(text, n_sel):
        ids = tok(" " + text, add_special_tokens=False).input_ids
        sel_rel = list(range(len(ids) - n_sel, len(ids))) if n_sel else []
        return ids, sel_rel

    def pad_to(ids, b_fix):
        out = list(ids)
        while len(out) < b_fix:
            out.append(pad_ids[len(out) % len(pad_ids)])
        return out[:b_fix]

    def country_donor(c):
        n_ct = len(tok(" " + c, add_special_tokens=False).input_ids)
        return donor_ids(f"{CTX_FRAME} {c}", n_ct)

    b_fix = max([len(country_donor(c)[0]) for c in test_countries]
                + [len(donor_ids(PROSE_DONOR, 0)[0])]) + 2
    a_len, c_len = len(a_ids), len(c_ids)
    print(f"[kvc] A={a_len} B(fixed)={b_fix} C={c_len} | nonce pos {occ}")

    def build_mask(sel_abs: list[int], b_sees_a: bool):
        n = a_len + b_fix + c_len
        m = torch.full((n, n), NEG)
        m[torch.tril(torch.zeros(n, n) == 0)] = 0.0     # causal base
        b0, c0 = a_len, a_len + b_fix
        if not b_sees_a:
            m[b0:c0, :b0] = NEG                          # blind donor
        m[c0:, b0:c0] = NEG                              # C blocks B ...
        for col in sel_abs:
            m[c0:, col] = 0.0                            # ... except selected
        return m[None, None, :, :].to(dtype=getattr(torch, args.dtype),
                                      device=dev)

    def cell_logits(lm, arm, c, cw):
        n_ct = len(tok(" " + c, add_special_tokens=False).input_ids)
        if arm == "ctx_base":
            b, sel_rel, sees = donor_ids(PROSE_DONOR, 0)[0], [], False
        elif arm == "kv_ctx":
            b, sel_rel = country_donor(c)
            sees = True
        elif arm == "kv_blind":
            b, sel_rel = country_donor(c)
            sees = False
        elif arm == "kv_ctx_wrong":
            b, sel_rel = country_donor(cw)
            sees = True
        elif arm == "kv_ctx_rand":
            b, sel_rel = donor_ids(PROSE_DONOR, n_ct)
            sees = True
        b = pad_to(b, b_fix)
        ids = a_ids + b + c_ids
        sel_abs = [a_len + r for r in sel_rel]
        mask = build_mask(sel_abs, sees)
        hooks = [(L, torch.tensor(d_lm[lm] * S, dtype=torch.float32,
                                  device=dev), occ)]
        return forward_logits(ids, mask4d=mask, hooks=hooks)

    def margin_true(lo, target):
        others = [t for w, t in union.items() if w != target]
        return float(lo[union[target]] - max(lo[t] for t in others))

    def argmax_word(lo):
        return max(union, key=lambda w: lo[union[w]])

    cells = [lm for lm in valid
             if COUNTRY_CAP[mh3.COUNTRY_OF[lm]] in union
             and mh3.COUNTRY_OF[lm] in wrong_of]
    cats = build_categories([{"country": mh3.COUNTRY_OF[lm],
                              "city": mh3.CITY_OF[lm]} for lm in cells])
    print(f"[kvc] cells: {len(cells)}")

    margins = {a: [] for a in ARMS}
    op_err = {a: [] for a in ("ctx_base", "kv_ctx")}
    swap_hits = true_hits = 0
    records = []
    for lm in cells:
        c = mh3.COUNTRY_OF[lm]
        cw = wrong_of[c]
        truth = COUNTRY_CAP[c]
        swap_target = COUNTRY_CAP[cw]
        row = {"landmark": lm, "truth": truth, "country": c,
               "wrong_country": cw, "swap_target": swap_target,
               "city": mh3.CITY_OF[lm]}
        for a in ARMS:
            lo = cell_logits(lm, a, c, cw)
            margins[a].append(margin_true(lo, truth))
            aw = argmax_word(lo)
            row[f"{a}_arg"] = aw
            row[f"{a}_margin"] = margins[a][-1]
            if a in op_err:
                op_err[a].append(1.0 if classify(aw, truth, cats)
                                 in OPERAND_DOMAIN else 0.0)
            if a == "kv_ctx_wrong":
                if first_token(aw) == first_token(swap_target):
                    swap_hits += 1
                if first_token(aw) == first_token(truth):
                    true_hits += 1
        records.append(row)

    m_arr = {a: np.asarray(v) for a, v in margins.items()}
    acc = {a: float(np.mean([1.0 if classify(r[f"{a}_arg"], r["truth"], cats)
                             == "CORRECT" else 0.0 for r in records]))
           for a in ARMS}
    op_arr = {a: np.asarray(v) for a, v in op_err.items()}
    sc = score_ctx(m_arr, acc, op_arr, swap_hits, true_hits, rng, args.alpha)
    v = verdict_ctx(gate0, sc)

    print(f"[kvc] means: { {a: round(sc['means'][a], 3) for a in ARMS} }")
    print(f"[kvc] acc:   { {a: round(acc[a], 2) for a in ARMS} }")
    print(f"[kvc] G1 co-encoding Δ={sc['g1'].value:+.3f} (p={sc['g1'].p:.4f}) "
          f"flip={sc['flip1']} | G2 Δ={sc['g2'].value:+.3f} "
          f"(p={sc['g2'].p:.4f}) flip={sc['flip2']} | G3 Δ={sc['g3'].value:+.3f} "
          f"(p={sc['g3'].p:.4f}) swap {swap_hits}/{len(cells)} vs true {true_hits}")
    print(f"[kvc] advisory: CoT fraction {sc['cot_fraction']:.2f} "
          f"(kv_ctx {acc['kv_ctx']:.2f}/{COT_ANCHOR}) | kv_blind {acc['kv_blind']:.2f} "
          f"vs P-KV-1 kv_nat {KVNAT_ANCHOR} | secondary "
          f"Δ={sc['secondary'].value:+.3f} (p={sc['secondary'].p:.4f})")
    print(f"[kvc] VERDICT: {v}")

    result = {
        "model_id": args.model_id, "probe": "P-KV-1b", "seed": args.seed,
        "scale": S, "ref_layer": L, "n_layers": n_layers,
        "a_len": a_len, "b_fix": b_fix, "c_len": c_len,
        "mask_check": {"max_dlogit": dmax, "argmax_same": same_arg},
        "alpha": args.alpha, "valid": valid, "union_size": len(union),
        "dropped_collisions": sorted(drop), "n_cells": len(cells),
        "gate0": gate0, "wrong_of": wrong_of,
        "gates": {"g1": asdict(sc["g1"]), "flip1": sc["flip1"],
                  "g2": asdict(sc["g2"]), "flip2": sc["flip2"],
                  "g3": asdict(sc["g3"]), "secondary": asdict(sc["secondary"]),
                  "swap_hits": swap_hits, "true_hits": true_hits,
                  "swap_coherent": sc["swap_coherent"]},
        "advisory": {"cot_fraction": sc["cot_fraction"],
                     "cot_anchor": COT_ANCHOR, "kvnat_anchor": KVNAT_ANCHOR},
        "means": sc["means"], "acc": acc, "verdict": v, "cells": records}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "kv_ctx.json").write_text(
        json.dumps(_json_safe(result), indent=2, allow_nan=False))
    print(f"[kvc] wrote {out}/kv_ctx.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="P-KV-1b co-encoding term (kv_ctx)")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--ref-layer", type=int, default=9)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--mask-tol", type=float, default=0.05)
    ap.add_argument("--n-cells", type=int, default=0)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/kv-ctx/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
