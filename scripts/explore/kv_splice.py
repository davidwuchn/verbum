#!/usr/bin/env python3
"""§P-KV-1 — addressed content without the tape (KV splice, no tokens, no weights).

Drafted s295 (Michael GO "yes let's try P-KV-1"). The register fork: transient
unaddressed injection fails (P-STACK-1b/3a/P-ENRICH-1) while tape-addressed
content works (CoT 9/10, scaffold 10/10). A KV-cache entry is ALSO
tape-addressed — content at a RoPE position, attendable, never generated.
Deliver the intermediate (country) in the ADDRESSED register and ask whether
resident hop-2 (country->capital) completes one-shot.

Implementation: ONE forward per cell-arm — donor segment + test segment with an
additive 4D attention mask. Donor rows: plain causal (never see the test). Test
rows: causal within test + donor position 0 (sink parity, ALL arms) + the
selected donor columns only. Donors are padded to a fixed length so test-token
RoPE positions are identical across arms (padding appended AFTER the selected
columns; causal encoding leaves their KV untouched). Runtime self-check: the
4D mask path must reproduce plain-forward logits (abort otherwise — no verdict
from an unverified mask path).

Arms: base / kv_nat / kv_wrong / kv_rand / kv_synth / resid (see pre-reg).
kv_synth vs resid = the REGISTER FORK: identical injected content (d_ct @ L_e),
addressed vs unaddressed. Gates: G1 kv_nat>base + flip (primary); G2
specificity + SWAP flag; G3 vs kv_rand; G4 register fork (mechanism clause,
never decides the headline); secondary operand-error shift. Verdicts:
ADDRESSED-COMPOSES (+ADDRESS-SUFFICIENT | +RE-ENCODING-REQUIRED) / KV-PRIMING /
ANY-KV-ARTIFACT / ADDRESS-FAILS.
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

# reuse (no fork): chain data + prompts + classifier + dsp
from fn_stack import COUNTRY_CAP, NONCE_PROMPT  # noqa: E402
from holo_cap import NONCE_CANDS  # noqa: E402
from holo_frag import _json_safe  # noqa: E402
from stack_error_domain import build_categories, classify, first_token  # noqa: E402

from verbum.dsp import gate, paired_permutation  # noqa: E402

OPERAND_DOMAIN = {"CITY", "COUNTRY", "CONTINENT"}
ENRICH_DEPTH = 0.16                    # d_ct build/injection depth (P-ENRICH-1)
CC_FRAME_HEAD = "The landmark is located in the country of"
PROSE_DONOR = "The recipe calls for two cups of white wheat flour"
SYNTH_DONOR_HEAD = "Consider the"
ARMS = ("base", "kv_nat", "kv_wrong", "kv_rand", "kv_synth", "resid")


# ══════════════════════════════════════════════════════════════════════════
# Frozen verdict logic (pure; --validate exercises it)
# ══════════════════════════════════════════════════════════════════════════
def score_kv(m: dict[str, np.ndarray], acc: dict[str, float],
             op_err: dict[str, np.ndarray], swap_hits: int, true_hits: int,
             rng, alpha: float) -> dict:
    def g(a, b, name):
        return gate(float(np.mean(m[a] - m[b])),
                    paired_permutation(m[a], m[b], rng), "greater", alpha,
                    name=name)
    g1 = g("kv_nat", "base", "address_works")            # primary
    flip = bool(acc["kv_nat"] > acc["base"])
    g2 = g("kv_nat", "kv_wrong", "specificity")
    g3 = g("kv_nat", "kv_rand", "not_any_kv")
    g4 = g("kv_synth", "resid", "register_fork")         # mechanism clause
    synth_flip = bool(acc["kv_synth"] > acc["resid"])
    swap_coherent = bool(swap_hits > true_hits)          # advisory, never gated
    sec = gate(float(np.mean(op_err["base"] - op_err["kv_nat"])),
               paired_permutation(op_err["base"], op_err["kv_nat"], rng),
               "greater", alpha, name="operand_err_shift")
    return {"g1": g1, "flip": flip, "g2": g2, "g3": g3, "g4": g4,
            "synth_flip": synth_flip, "swap_coherent": swap_coherent,
            "swap_hits": swap_hits, "true_hits": true_hits, "secondary": sec,
            "acc": dict(acc), "means": {a: float(np.mean(m[a])) for a in m}}


def verdict_kv(gate0: bool, sc: dict) -> str:
    if not gate0:
        return "negative/inconclusive (gate-0)"
    if not (sc["g1"].verdict and sc["flip"]):
        return "ADDRESS-FAILS"          # tape power != addressability
    if not sc["g3"].verdict:
        return "ANY-KV-ARTIFACT"
    if not sc["g2"].verdict:
        return "KV-PRIMING"
    if sc["g4"].verdict and sc["synth_flip"]:
        return "ADDRESSED-COMPOSES (+ADDRESS-SUFFICIENT)"
    return "ADDRESSED-COMPOSES (+RE-ENCODING-REQUIRED)"


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
def run_validate(alpha: float) -> int:
    rng = np.random.default_rng(0)
    n, noise = 10, 0.3
    print("── P-KV-1 --validate (planted worlds, no model) ──")
    ok = True

    def world(mu: dict[str, float], accs: dict[str, float], swap=(0, 0)):
        m = {a: mu.get(a, 0.0) + rng.normal(0, noise, n) for a in ARMS}
        op = {"base": np.array([1.0] * 8 + [0.0] * 2),
              "kv_nat": np.array([1.0] * 2 + [0.0] * 8)}
        acc = {a: accs.get(a, 0.0) for a in ARMS}
        sc = score_kv(m, acc, op, swap[0], swap[1], rng, alpha)
        return verdict_kv(True, sc)

    calls = {
        # address works, specific, not-any-kv; synth also beats resid -> SUFFICIENT
        "sufficient": (world({"kv_nat": 1.6, "kv_synth": 1.2, "kv_wrong": 0.2,
                              "kv_rand": 0.1, "resid": 0.1},
                             {"kv_nat": 0.7, "kv_synth": 0.4}),
                       "ADDRESSED-COMPOSES (+ADDRESS-SUFFICIENT)"),
        # address works for donor-encoded content only -> RE-ENCODING-REQUIRED
        "reencode": (world({"kv_nat": 1.6, "kv_wrong": 0.2, "kv_rand": 0.1,
                            "kv_synth": 0.15, "resid": 0.1},
                           {"kv_nat": 0.7}),
                     "ADDRESSED-COMPOSES (+RE-ENCODING-REQUIRED)"),
        # wrong-country KV moves margins just as much -> priming
        "priming": (world({"kv_nat": 1.6, "kv_wrong": 1.5, "kv_rand": 0.1},
                          {"kv_nat": 0.7}),
                    "KV-PRIMING"),
        # any attendable KV reproduces the gain -> artifact
        "any-kv": (world({"kv_nat": 1.6, "kv_wrong": 0.2, "kv_rand": 1.5},
                         {"kv_nat": 0.7}),
                   "ANY-KV-ARTIFACT"),
        # nothing moves -> fails
        "fails": (world({}, {}), "ADDRESS-FAILS"),
        # margins move, argmax does not -> fails
        "no-flip": (world({"kv_nat": 1.6, "kv_wrong": 0.2, "kv_rand": 0.1}, {}),
                    "ADDRESS-FAILS"),
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
    L_e = round(ENRICH_DEPTH * n_layers)
    print(f"[kv1] {args.model_id} L_ref={L} L_enrich={L_e} scale={S} "
          f"kv_scale={args.enrich_scale} dev={dev} n_layers={n_layers} eager")

    nonce = NONCE_CANDS[0]
    nonce_tid = tok(" " + nonce, add_special_tokens=False).input_ids[-1]

    def first_tid(w):
        return mh3.first_tid(tok, w)

    def ids_of(text):
        return tok(text, return_tensors="pt").input_ids[0].tolist()

    # ── 4D additive mask builder ──────────────────────────────────────────────
    NEG = torch.finfo(getattr(torch, args.dtype)).min

    def build_mask(d_len: int, t_len: int, sel_cols: list[int]):
        n = d_len + t_len
        m = torch.full((n, n), NEG)
        tri = torch.tril(torch.zeros(n, n) == 0)
        m[tri] = 0.0                                   # causal base
        # test rows: block ALL donor cols, then re-open sink + selected
        m[d_len:, :d_len] = NEG
        allow = [0, *sel_cols]
        for c in allow:
            m[d_len:, c] = 0.0
        return m[None, None, :, :].to(dtype=getattr(torch, args.dtype),
                                      device=dev)

    # ── mask-path self-check (gate on instrument; abort on fail) ─────────────
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

    chk_ids = ids_of("The capital of Portugal is")
    nchk = len(chk_ids)
    full = torch.full((nchk, nchk), NEG)
    full[torch.tril(torch.zeros(nchk, nchk) == 0)] = 0.0
    full = full[None, None, :, :].to(dtype=getattr(torch, args.dtype), device=dev)
    lo_plain = forward_logits(chk_ids)
    lo_mask = forward_logits(chk_ids, mask4d=full)
    dmax = float(np.max(np.abs(lo_plain - lo_mask)))
    same_arg = bool(np.argmax(lo_plain) == np.argmax(lo_mask))
    mask_ok = same_arg and dmax < args.mask_tol
    print(f"[kv1] mask self-check: max|dlogit|={dmax:.5f} argmax_same={same_arg} "
          f"-> {'PASS' if mask_ok else 'FAIL'}")
    if not mask_ok:
        print("[kv1] ABORT: 4D mask path does not reproduce plain forward "
              "(no verdict from an unverified mask path)")
        return 2

    # ── union / ceilings / cells (bake_stack convention) ─────────────────────
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
    print(f"[kv1] union candidates: {len(union)} (dropped: {sorted(drop)})")

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
        cap = COUNTRY_CAP[c]
        if first_token(real_pred(pref, "The capital of {x} is", c,
                                 list(COUNTRY_CAP.values()))) == first_token(cap):
            valid.append(lm)
    gate0 = mask_ok and len(valid) >= 6
    print(f"[kv1] ceilings: valid landmarks {len(valid)}/{len(mh3.LM_LIST)} "
          f"gate0={gate0}")
    if args.n_cells:
        valid = valid[:args.n_cells]

    # ── directions: operands @ L_ref, countries @ L_e (P-ENRICH convention) ──
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
    d_ct = build_dirs(test_countries, L_e)

    def derange(cs):
        n = len(cs)
        return {cs[i]: cs[(i + 1) % n] for i in range(n)} if n > 1 else {}

    wrong_of = derange(test_countries)

    # ── donor construction (padded to fixed length; selection = tail tokens) ──
    pad_ids = tok(" and so on", add_special_tokens=False).input_ids

    def donor(text, n_sel):
        """Returns (ids, sel_cols) — sel = last n_sel content positions."""
        ids = ids_of(text)
        sel = list(range(len(ids) - n_sel, len(ids)))
        return ids, sel

    def pad_to(ids, d_fix):
        out = list(ids)
        while len(out) < d_fix:
            out.append(pad_ids[len(out) % len(pad_ids)])
        return out[:d_fix]

    def country_donor(c):
        n_ct = len(tok(" " + c, add_special_tokens=False).input_ids)
        return donor(f"{CC_FRAME_HEAD} {c}", n_ct)

    synth_text = f"{SYNTH_DONOR_HEAD} {nonce}"
    test_ids = ids_of(NONCE_PROMPT.format(x=nonce))
    occ = [i for i, t in enumerate(test_ids) if t == nonce_tid][-1]

    d_fix = max([len(country_donor(c)[0]) for c in test_countries]
                + [len(ids_of(PROSE_DONOR)), len(ids_of(synth_text))]) + 2
    print(f"[kv1] donor length (fixed): {d_fix} | test len: {len(test_ids)} "
          f"| test nonce abs pos: {d_fix} + {occ}")

    # ── per-cell arms ─────────────────────────────────────────────────────────
    def cell_logits(lm, arm, c, cw):
        n_ct = len(tok(" " + c, add_special_tokens=False).input_ids)
        if arm in ("base", "resid"):
            d_ids, sel = donor(PROSE_DONOR, 0)[0], []
        elif arm == "kv_nat":
            d_ids, sel = country_donor(c)
        elif arm == "kv_wrong":
            d_ids, sel = country_donor(cw)
        elif arm == "kv_rand":
            d_ids, sel = donor(PROSE_DONOR, n_ct)   # column-count matched
        elif arm == "kv_synth":
            d_ids, sel = donor(synth_text, 1)
        d_ids = pad_to(d_ids, d_fix)
        ids = d_ids + test_ids
        mask = build_mask(d_fix, len(test_ids), sel)
        hooks = [(L, torch.tensor(d_lm[lm] * S, dtype=torch.float32, device=dev),
                  d_fix + occ)]
        if arm == "kv_synth":
            hooks.append((L_e, torch.tensor(d_ct[c] * args.enrich_scale,
                                            dtype=torch.float32, device=dev),
                          sel[0]))
        if arm == "resid":
            hooks.append((L_e, torch.tensor(d_ct[c] * args.enrich_scale,
                                            dtype=torch.float32, device=dev),
                          d_fix + occ))
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
    print(f"[kv1] cells: {len(cells)}")

    margins = {a: [] for a in ARMS}
    op_err = {a: [] for a in ("base", "kv_nat")}
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
            if a == "kv_wrong":
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
    sc = score_kv(m_arr, acc, op_arr, swap_hits, true_hits, rng, args.alpha)
    v = verdict_kv(gate0, sc)

    print(f"[kv1] means: { {a: round(sc['means'][a], 3) for a in ARMS} }")
    print(f"[kv1] acc:   { {a: round(acc[a], 2) for a in ARMS} }")
    print(f"[kv1] G1 Δ={sc['g1'].value:+.3f} (p={sc['g1'].p:.4f}) "
          f"flip={sc['flip']} | G2 Δ={sc['g2'].value:+.3f} (p={sc['g2'].p:.4f}) "
          f"swap {swap_hits}/{len(cells)} vs true {true_hits} "
          f"| G3 Δ={sc['g3'].value:+.3f} (p={sc['g3'].p:.4f})")
    print(f"[kv1] G4 register fork Δ={sc['g4'].value:+.3f} (p={sc['g4'].p:.4f}) "
          f"synth_flip={sc['synth_flip']} | secondary "
          f"Δ={sc['secondary'].value:+.3f} (p={sc['secondary'].p:.4f})")
    print(f"[kv1] VERDICT: {v}")

    result = {
        "model_id": args.model_id, "probe": "P-KV-1", "seed": args.seed,
        "scale": S, "enrich_scale": args.enrich_scale, "ref_layer": L,
        "n_layers": n_layers, "enrich_layer": L_e, "donor_len": d_fix,
        "mask_check": {"max_dlogit": dmax, "argmax_same": same_arg},
        "alpha": args.alpha, "valid": valid, "union_size": len(union),
        "dropped_collisions": sorted(drop), "n_cells": len(cells),
        "gate0": gate0, "wrong_of": wrong_of,
        "gates": {"g1": asdict(sc["g1"]), "flip": sc["flip"],
                  "g2": asdict(sc["g2"]), "g3": asdict(sc["g3"]),
                  "g4": asdict(sc["g4"]), "synth_flip": sc["synth_flip"],
                  "secondary": asdict(sc["secondary"]),
                  "swap_hits": swap_hits, "true_hits": true_hits,
                  "swap_coherent": sc["swap_coherent"]},
        "means": sc["means"], "acc": acc, "verdict": v, "cells": records}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "kv_splice.json").write_text(
        json.dumps(_json_safe(result), indent=2, allow_nan=False))
    print(f"[kv1] wrote {out}/kv_splice.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="P-KV-1 addressed-content KV splice")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--ref-layer", type=int, default=9)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--enrich-scale", type=float, default=2.0)
    ap.add_argument("--mask-tol", type=float, default=0.05)
    ap.add_argument("--n-cells", type=int, default=0)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/kv-splice/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
