#!/usr/bin/env python3
"""§P-KV-1c — the clause-width term (full-clause splice).

Drafted s295 (Michael "proceed with a"). REDUCTION: "own-state splice" under
greedy decoding is deterministically identical to a donor writing the same
text at matched visibility — the irreducible residue of the writeback
hypothesis in the splice register is CLAUSE WIDTH. 1b spliced a
question-visible true-country clause but let the readout attend ONLY the
entity columns (0.00). CoT's readout attends the WHOLE clause. P-KV-1c: does
composition consume the RELATION columns rather than the entity columns?

Layout = P-KV-1b (A question w/ operand@nonce -> B clause "It is located in
the country of {x}" padded -> C " The answer is"); same 4D-mask machinery +
self-check. Arms: base / kv_full (B sees A, C sees ALL clause cols) /
kv_entity (C sees country cols only = 1b kv_ctx reproduced) / kv_full_blind
(B blind, C sees all) / kv_full_wrong (deranged). Gates: G1 clause-width
(kv_full > kv_entity margin AND acc); G2 composition (kv_full > base + flip);
G3 specificity; G4 co-encoding at full width (mechanism clause). Verdicts:
CLAUSE-CARRIES (+CO-ENCODED | +BLIND-OK) / STILL-DEAD / WIDTH-IRRELEVANT /
UNSPECIFIC-CLAUSE.
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
from kv_ctx import A_TEXT, C_TEXT, COT_ANCHOR, CTX_FRAME  # noqa: E402
from kv_splice import OPERAND_DOMAIN, PROSE_DONOR  # noqa: E402
from stack_error_domain import build_categories, classify, first_token  # noqa: E402

from verbum.dsp import gate, paired_permutation  # noqa: E402

ARMS = ("base", "kv_full", "kv_entity", "kv_full_blind", "kv_full_wrong")


# ══════════════════════════════════════════════════════════════════════════
# Frozen verdict logic (pure; --validate exercises it)
# ══════════════════════════════════════════════════════════════════════════
def score_clause(m: dict[str, np.ndarray], acc: dict[str, float],
                 op_err: dict[str, np.ndarray], swap_hits: int, true_hits: int,
                 rng, alpha: float) -> dict:
    def g(a, b, name):
        return gate(float(np.mean(m[a] - m[b])),
                    paired_permutation(m[a], m[b], rng), "greater", alpha,
                    name=name)
    g1 = g("kv_full", "kv_entity", "clause_width")       # primary
    flip1 = bool(acc["kv_full"] > acc["kv_entity"])
    g2 = g("kv_full", "base", "composition")
    flip2 = bool(acc["kv_full"] > acc["base"])
    g3 = g("kv_full", "kv_full_wrong", "specificity")
    g4 = g("kv_full", "kv_full_blind", "co_encoding_full_width")
    swap_coherent = bool(swap_hits > true_hits)
    sec = gate(float(np.mean(op_err["base"] - op_err["kv_full"])),
               paired_permutation(op_err["base"], op_err["kv_full"], rng),
               "greater", alpha, name="operand_err_shift")
    return {"g1": g1, "flip1": flip1, "g2": g2, "flip2": flip2, "g3": g3,
            "g4": g4, "swap_coherent": swap_coherent, "swap_hits": swap_hits,
            "true_hits": true_hits, "secondary": sec, "acc": dict(acc),
            "cot_fraction": float(acc["kv_full"] / COT_ANCHOR),
            "means": {a: float(np.mean(m[a])) for a in m}}


def verdict_clause(gate0: bool, sc: dict) -> str:
    if not gate0:
        return "negative/inconclusive (gate-0)"
    if not (sc["g2"].verdict and sc["flip2"]):
        return "STILL-DEAD"             # writeback target maximally confirmed
    if not (sc["g1"].verdict and sc["flip1"]):
        return "WIDTH-IRRELEVANT"       # both widths compose (drift suspect)
    if not sc["g3"].verdict:
        return "UNSPECIFIC-CLAUSE"
    tail = "+CO-ENCODED" if sc["g4"].verdict else "+BLIND-OK"
    return f"CLAUSE-CARRIES ({tail})"


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
def run_validate(alpha: float) -> int:
    rng = np.random.default_rng(0)
    n, noise = 10, 0.3
    print("── P-KV-1c --validate (planted worlds, no model) ──")
    ok = True

    def world(mu: dict[str, float], accs: dict[str, float], swap=(0, 0)):
        m = {a: mu.get(a, 0.0) + rng.normal(0, noise, n) for a in ARMS}
        op = {"base": np.array([1.0] * 8 + [0.0] * 2),
              "kv_full": np.array([1.0] * 2 + [0.0] * 8)}
        acc = {a: accs.get(a, 0.0) for a in ARMS}
        sc = score_clause(m, acc, op, swap[0], swap[1], rng, alpha)
        return verdict_clause(True, sc)

    calls = {
        # full clause composes, entity doesn't; needs co-encoding
        "carries-co": (world({"kv_full": 2.6, "kv_entity": 1.0,
                              "kv_full_blind": 1.1, "kv_full_wrong": 0.4},
                             {"kv_full": 0.6}),
                       "CLAUSE-CARRIES (+CO-ENCODED)"),
        # full clause composes even blind (blind >= full -> G4 clearly null)
        "carries-blind": (world({"kv_full": 2.6, "kv_entity": 1.0,
                                 "kv_full_blind": 2.7, "kv_full_wrong": 0.4},
                                {"kv_full": 0.6}),
                          "CLAUSE-CARRIES (+BLIND-OK)"),
        # nothing flips even at full width
        "still-dead": (world({"kv_full": 1.2, "kv_entity": 1.0,
                              "kv_full_wrong": 0.4}, {}),
                       "STILL-DEAD"),
        # both widths compose equally
        "width-irrelevant": (world({"kv_full": 2.6, "kv_entity": 2.5,
                                    "kv_full_wrong": 0.4},
                                   {"kv_full": 0.6, "kv_entity": 0.6}),
                             "WIDTH-IRRELEVANT"),
        # wrong clause composes as well
        "unspecific": (world({"kv_full": 2.6, "kv_entity": 1.0,
                              "kv_full_wrong": 2.5},
                             {"kv_full": 0.6}),
                       "UNSPECIFIC-CLAUSE"),
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
    print(f"[kvf] {args.model_id} L_ref={L} scale={S} dev={dev} "
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

    # ── mask self-check ──────────────────────────────────────────────────────
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
    print(f"[kvf] mask self-check: max|dlogit|={dmax:.5f} argmax_same={same_arg} "
          f"-> {'PASS' if mask_ok else 'FAIL'}")
    if not mask_ok:
        print("[kvf] ABORT: unverified mask path")
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
    print(f"[kvf] union candidates: {len(union)} (dropped: {sorted(drop)})")

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
    print(f"[kvf] ceilings: valid landmarks {len(valid)}/{len(mh3.LM_LIST)} "
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

    # ── segments (P-KV-1b layout) ────────────────────────────────────────────
    a_ids = tok(A_TEXT.format(x=nonce), return_tensors="pt").input_ids[0].tolist()
    c_ids = tok(C_TEXT, add_special_tokens=False).input_ids
    occ = [i for i, t in enumerate(a_ids) if t == nonce_tid][-1]
    pad_ids = tok(" and so on", add_special_tokens=False).input_ids

    def donor_ids(text):
        return tok(" " + text, add_special_tokens=False).input_ids

    def pad_to(ids, b_fix):
        out = list(ids)
        while len(out) < b_fix:
            out.append(pad_ids[len(out) % len(pad_ids)])
        return out[:b_fix]

    def clause(c):
        ids = donor_ids(f"{CTX_FRAME} {c}")
        n_ct = len(tok(" " + c, add_special_tokens=False).input_ids)
        sel_full = list(range(len(ids)))                  # whole clause
        sel_ent = list(range(len(ids) - n_ct, len(ids)))  # country tail
        return ids, sel_full, sel_ent

    b_fix = max([len(clause(c)[0]) for c in test_countries]
                + [len(donor_ids(PROSE_DONOR))]) + 2
    a_len, c_len = len(a_ids), len(c_ids)
    print(f"[kvf] A={a_len} B(fixed)={b_fix} C={c_len} | nonce pos {occ}")

    def build_mask(sel_abs: list[int], b_sees_a: bool):
        n = a_len + b_fix + c_len
        m = torch.full((n, n), NEG)
        m[torch.tril(torch.zeros(n, n) == 0)] = 0.0
        b0, c0 = a_len, a_len + b_fix
        if not b_sees_a:
            m[b0:c0, :b0] = NEG
        m[c0:, b0:c0] = NEG
        for col in sel_abs:
            m[c0:, col] = 0.0
        return m[None, None, :, :].to(dtype=getattr(torch, args.dtype),
                                      device=dev)

    def cell_logits(lm, arm, c, cw):
        if arm == "base":
            b, sel, sees = donor_ids(PROSE_DONOR), [], False
        elif arm in ("kv_full", "kv_full_blind"):
            ids_b, sel_full, _ = clause(c)
            b, sel = ids_b, sel_full
            sees = arm == "kv_full"
        elif arm == "kv_entity":
            ids_b, _, sel_ent = clause(c)
            b, sel, sees = ids_b, sel_ent, True
        elif arm == "kv_full_wrong":
            ids_b, sel_full, _ = clause(cw)
            b, sel, sees = ids_b, sel_full, True
        b = pad_to(b, b_fix)
        ids = a_ids + b + c_ids
        sel_abs = [a_len + r for r in sel]
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
    print(f"[kvf] cells: {len(cells)}")

    margins = {a: [] for a in ARMS}
    op_err = {a: [] for a in ("base", "kv_full")}
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
            if a == "kv_full_wrong":
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
    sc = score_clause(m_arr, acc, op_arr, swap_hits, true_hits, rng, args.alpha)
    v = verdict_clause(gate0, sc)

    print(f"[kvf] means: { {a: round(sc['means'][a], 3) for a in ARMS} }")
    print(f"[kvf] acc:   { {a: round(acc[a], 2) for a in ARMS} }")
    print(f"[kvf] G1 clause-width Δ={sc['g1'].value:+.3f} (p={sc['g1'].p:.4f}) "
          f"flip={sc['flip1']} | G2 Δ={sc['g2'].value:+.3f} (p={sc['g2'].p:.4f}) "
          f"flip={sc['flip2']} | G3 Δ={sc['g3'].value:+.3f} (p={sc['g3'].p:.4f}) "
          f"swap {swap_hits}/{len(cells)} vs true {true_hits}")
    print(f"[kvf] G4 co-encoding@full Δ={sc['g4'].value:+.3f} "
          f"(p={sc['g4'].p:.4f}) | CoT fraction {sc['cot_fraction']:.2f} | "
          f"secondary Δ={sc['secondary'].value:+.3f} (p={sc['secondary'].p:.4f})")
    print(f"[kvf] VERDICT: {v}")

    result = {
        "model_id": args.model_id, "probe": "P-KV-1c", "seed": args.seed,
        "scale": S, "ref_layer": L, "n_layers": n_layers,
        "a_len": a_len, "b_fix": b_fix, "c_len": c_len,
        "mask_check": {"max_dlogit": dmax, "argmax_same": same_arg},
        "alpha": args.alpha, "valid": valid, "union_size": len(union),
        "dropped_collisions": sorted(drop), "n_cells": len(cells),
        "gate0": gate0, "wrong_of": wrong_of,
        "gates": {"g1": asdict(sc["g1"]), "flip1": sc["flip1"],
                  "g2": asdict(sc["g2"]), "flip2": sc["flip2"],
                  "g3": asdict(sc["g3"]), "g4": asdict(sc["g4"]),
                  "secondary": asdict(sc["secondary"]),
                  "swap_hits": swap_hits, "true_hits": true_hits,
                  "swap_coherent": sc["swap_coherent"]},
        "advisory": {"cot_fraction": sc["cot_fraction"],
                     "cot_anchor": COT_ANCHOR},
        "means": sc["means"], "acc": acc, "verdict": v, "cells": records}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "kv_clause.json").write_text(
        json.dumps(_json_safe(result), indent=2, allow_nan=False))
    print(f"[kvf] wrote {out}/kv_clause.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="P-KV-1c clause-width splice")
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
    ap.add_argument("--out", default="results/kv-clause/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
