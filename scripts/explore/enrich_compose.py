#!/usr/bin/env python3
"""§P-ENRICH-1 — hop enrichment in-context (SuperBake §3.8 as a pure hook).

Drafted s295 (Michael GO "proceed with these refining experiments"). The s295
SuperBake DSP audit found the §3.8 composition operation UNTRIED by our rung-3
instruments: place the INTERMEDIATE ENTITY'S OWN REPRESENTATION (the country's
d_ct, built exactly like the operand directions) at the SUBJECT (nonce) position
at 0.16x depth, and ask whether the resident hop-2 map (country->capital)
completes the composition one-shot. Content register (place the product) after
s293-s294 falsified the routing register (select the function).

Arms (operand @ nonce slot @ L_ref in ALL arms; readout = capital first-token
margin over the union + argmax classified by stack_error_domain):
  base        : operand only
  enrich      : + d_ct(correct country) @ subject pos @ L_e = round(0.16*n)
  wrong       : + d_ct(deranged country) @ subject @ L_e   (specificity + swap)
  random      : + norm-matched random    @ subject @ L_e   (energy control)
  pos_ctl     : + d_ct(correct) @ FINAL token @ L_e        (subject-token law)
  depth_ctl   : + d_ct(correct) @ subject @ round(0.6*n)   (early-band law)
  enrich_hkey : enrich + country2cap key @ final @ 0.6n    (linker w/ product placed)

Frozen gates: G1 margin(enrich)>margin(base) AND acc flip (primary);
G2 margin_true(enrich)>margin_true(wrong) + advisory SWAP-COHERENT flag;
G3 enrich>random; G4 advisory laws (pos/depth/hkey, never gated); secondary
operand-domain error shift. Verdicts: ENRICH-COMPOSES / UNSPECIFIC-PRIMING /
ENERGY-ARTIFACT / ENRICH-FAILS. Single pre-registered depth -> no selection
correction. Reuses fn_stack chain + bake_stack conventions + the s294
classifier + verbum.dsp (no fork).
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
from fn_index import KEY_EXEMPLARS  # noqa: E402
from fn_stack import COUNTRY2CAP_EXEMPLARS, COUNTRY_CAP, NONCE_PROMPT  # noqa: E402
from holo_cap import NONCE_CANDS  # noqa: E402
from holo_frag import _json_safe  # noqa: E402
from stack_error_domain import build_categories, classify, first_token  # noqa: E402

from verbum.dsp import gate, paired_permutation  # noqa: E402

OPERAND_DOMAIN = {"CITY", "COUNTRY", "CONTINENT"}
ENRICH_DEPTH = 0.16          # pre-registered single depth (SuperBake §3.8 band)
DEPTH_CTL = 0.6              # the old h-window (P-STACK-1b regime) as depth law
ARMS = ("base", "enrich", "wrong", "random", "pos_ctl", "depth_ctl",
        "enrich_hkey")


# ══════════════════════════════════════════════════════════════════════════
# Frozen verdict logic (pure; --validate exercises it)
# ══════════════════════════════════════════════════════════════════════════
def score_enrich(m: dict[str, np.ndarray], acc: dict[str, float],
                 op_err: dict[str, np.ndarray], swap_hits: int, true_hits: int,
                 rng, alpha: float) -> dict:
    """m[arm]: per-cell TRUE-capital margin arrays. acc[arm]: scalar accuracy.
    op_err[arm]: per-cell operand-domain error booleans. swap/true_hits: wrong-arm
    argmax counts (capital of injected vs true country)."""
    def g(a, b, name):
        return gate(float(np.mean(m[a] - m[b])),
                    paired_permutation(m[a], m[b], rng), "greater", alpha,
                    name=name)
    g1 = g("enrich", "base", "enrich_vs_base")            # primary
    flip = bool(acc["enrich"] > acc["base"])
    g2 = g("enrich", "wrong", "specificity")
    g3 = g("enrich", "random", "content_not_energy")
    swap_coherent = bool(swap_hits > true_hits)           # advisory, never gated
    # secondary: errors move OUT of the operand domain under enrichment
    sec = gate(float(np.mean(op_err["base"] - op_err["enrich"])),
               paired_permutation(op_err["base"], op_err["enrich"], rng),
               "greater", alpha, name="operand_err_shift")
    # G4 advisory laws (values + p, NEVER gated)
    laws = {"position": g("enrich", "pos_ctl", "position_law"),
            "depth": g("enrich", "depth_ctl", "depth_law"),
            "hkey": g("enrich_hkey", "enrich", "hkey_helps")}
    return {"g1": g1, "flip": flip, "g2": g2, "g3": g3,
            "swap_coherent": swap_coherent, "swap_hits": swap_hits,
            "true_hits": true_hits, "secondary": sec, "laws": laws,
            "acc": dict(acc),
            "means": {a: float(np.mean(m[a])) for a in m}}


def verdict_enrich(gate0: bool, sc: dict) -> str:
    if not gate0:
        return "negative/inconclusive (gate-0)"
    if not (sc["g1"].verdict and sc["flip"]):
        return "ENRICH-FAILS"           # tape/backprop rung STRENGTHENED
    if not sc["g3"].verdict:
        return "ENERGY-ARTIFACT"
    if not sc["g2"].verdict:
        return "UNSPECIFIC-PRIMING"     # capital-class amplification, content-side
    return "ENRICH-COMPOSES"            # construction path opens for rung 3


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
def run_validate(alpha: float) -> int:
    rng = np.random.default_rng(0)
    n, noise = 10, 0.3
    print("── P-ENRICH-1 --validate (planted worlds, no model) ──")
    ok = True

    def world(mu: dict[str, float], accs: dict[str, float], flip: bool,
              swap=(6, 1)):
        m = {a: mu[a] + rng.normal(0, noise, n) for a in ARMS}
        op = {"base": np.array([1.0] * 8 + [0.0] * 2),
              "enrich": np.array([1.0] * (2 if flip else 8) + [0.0] *
                                 (8 if flip else 2))}
        acc = {a: accs.get(a, 0.0) for a in ARMS}
        sc = score_enrich(m, acc, op, swap[0], swap[1], rng, alpha)
        return verdict_enrich(True, sc)

    base_mu = {a: 0.0 for a in ARMS}
    calls = {
        # enrichment composes: big margin, specific, content-not-energy
        "composes": (world({**base_mu, "enrich": 1.5, "enrich_hkey": 1.6,
                            "wrong": 0.2, "random": 0.1},
                           {"enrich": 0.7, "base": 0.1}, True),
                     "ENRICH-COMPOSES"),
        # wrong-country enriches just as well -> priming not composition
        "priming": (world({**base_mu, "enrich": 1.5, "wrong": 1.4,
                           "random": 0.1},
                          {"enrich": 0.7, "base": 0.1}, True),
                    "UNSPECIFIC-PRIMING"),
        # norm-matched random reproduces the gain -> energy artifact
        "energy": (world({**base_mu, "enrich": 1.5, "wrong": 0.2,
                          "random": 1.4},
                         {"enrich": 0.7, "base": 0.1}, True),
                   "ENERGY-ARTIFACT"),
        # no margin movement -> fails
        "fails": (world(base_mu, {"enrich": 0.1, "base": 0.1}, False),
                  "ENRICH-FAILS"),
        # margin moves but accuracy does not flip -> fails (argmax must move)
        "no-flip": (world({**base_mu, "enrich": 1.5, "wrong": 0.2,
                           "random": 0.1},
                          {"enrich": 0.1, "base": 0.1}, False),
                    "ENRICH-FAILS"),
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
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    dec, _norm, _u = mh3.resolve_parts(model)
    n_layers = len(dec)
    L, S = args.ref_layer, args.scale
    L_e = round(ENRICH_DEPTH * n_layers)
    L_dc = round(DEPTH_CTL * n_layers)
    L_h = L_dc                                     # h-key window (old regime)
    print(f"[enr] {args.model_id} L_ref={L} L_enrich={L_e} L_depthctl={L_dc} "
          f"scale={S} enrich_scale={args.enrich_scale} dev={dev} "
          f"n_layers={n_layers}")

    nonce = NONCE_CANDS[0]
    nonce_tid = tok(" " + nonce, add_special_tokens=False).input_ids[-1]

    def first_tid(w):
        return mh3.first_tid(tok, w)

    # ── union candidate set (capital chain, bake_stack convention) ────────────
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
    print(f"[enr] union candidates: {len(union)} (dropped: {sorted(drop)})")

    # ── ceilings (gate-0): resident capital map, shortcut-free (bake_stack) ──
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
        if c not in COUNTRY_CAP:
            continue
        cap = COUNTRY_CAP[c]
        if mh3.CITY_OF[lm] == cap:                 # shortcut-free: city != capital
            continue
        cap_ok = first_token(real_pred(pref, "The capital of {x} is", c,
                                       list(COUNTRY_CAP.values()))) == first_token(cap)
        if cap_ok:
            valid.append(lm)
    gate0 = len(valid) >= 6
    print(f"[enr] ceilings: valid landmarks {len(valid)}/{len(mh3.LM_LIST)} "
          f"gate0={gate0}")
    if args.n_cells:
        valid = valid[:args.n_cells]

    # ── directions: operands (landmarks @ L_ref) + entities (countries) ──────
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
    d_ct = {li: build_dirs(test_countries, li) for li in (L_e, L_dc)}
    dim = d_lm[mh3.LM_LIST[0]].shape[0]
    ct_norms = {c: round(float(np.linalg.norm(d_ct[L_e][c])), 1)
                for c in test_countries}
    print(f"[enr] d_ct norms @L{L_e}: {ct_norms}")

    # ── h-key (country2cap) @ L_h, fn_stack/bake_stack convention ────────────
    def capture_hidden(prompt, layers):
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            out = model(**ids, output_hidden_states=True)
        return {li: out.hidden_states[li + 1][0, -1, :].float().cpu().numpy()
                for li in layers}

    key_specs = {"country": KEY_EXEMPLARS["country"],
                 "country2cap": COUNTRY2CAP_EXEMPLARS}
    raw = {m: [] for m in key_specs}
    for m, exs in key_specs.items():
        for word, tpl in exs:
            raw[m].append(capture_hidden(tpl.format(x=word), [L_h])[L_h])
    means = {m: np.mean(raw[m], axis=0) for m in key_specs}
    gm_k = np.mean(list(means.values()), axis=0)
    h_key = means["country2cap"] - gm_k

    # ── derangement for the wrong arm (fixed, seeded) ─────────────────────────
    def derange(cs):
        n = len(cs)
        return {cs[i]: cs[(i + 1) % n] for i in range(n)} if n > 1 else {}

    wrong_of = derange(test_countries)

    def rand_matched(vec):
        v = rng.standard_normal(dim)
        return v / (np.linalg.norm(v) + 1e-9) * float(np.linalg.norm(vec))

    # ── one forward: operand @ nonce slot; additions per arm ─────────────────
    def cell_logits(lm, adds):
        """adds: list of (layer, vec, where) with where in {'subject','final'}."""
        prompt = NONCE_PROMPT.format(x=nonce)
        ids = tok(prompt, return_tensors="pt").to(dev)
        toks = ids.input_ids[0].tolist()
        occ = [i for i, t in enumerate(toks) if t == nonce_tid][-1]
        last = len(toks) - 1
        handles = []
        vt = torch.tensor(d_lm[lm] * S, dtype=torch.float32, device=dev)
        handles.append(dec[L].register_forward_hook(mh3.add_hook_at(vt, occ)))
        for (li, vec, where) in adds:
            kt = torch.tensor(vec * args.enrich_scale, dtype=torch.float32,
                              device=dev)
            pos = occ if where == "subject" else last
            handles.append(dec[li].register_forward_hook(mh3.add_hook_at(kt, pos)))
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        for hd in handles:
            hd.remove()
        return lo

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
    print(f"[enr] cells: {len(cells)}")

    margins = {a: [] for a in ARMS}
    op_err = {a: [] for a in ("base", "enrich")}
    swap_hits = true_hits = 0
    records = []
    for lm in cells:
        c = mh3.COUNTRY_OF[lm]
        truth = COUNTRY_CAP[c]
        cw = wrong_of[c]
        swap_target = COUNTRY_CAP[cw]
        e_vec = d_ct[L_e][c]
        arm_adds = {
            "base": [],
            "enrich": [(L_e, e_vec, "subject")],
            "wrong": [(L_e, d_ct[L_e][cw], "subject")],
            "random": [(L_e, rand_matched(e_vec), "subject")],
            "pos_ctl": [(L_e, e_vec, "final")],
            "depth_ctl": [(L_dc, d_ct[L_dc][c], "subject")],
            "enrich_hkey": [(L_e, e_vec, "subject"), (L_h, h_key, "final")],
        }
        row = {"landmark": lm, "truth": truth, "country": c,
               "wrong_country": cw, "swap_target": swap_target,
               "city": mh3.CITY_OF[lm]}
        for a in ARMS:
            lo = cell_logits(lm, arm_adds[a])
            margins[a].append(margin_true(lo, truth))
            aw = argmax_word(lo)
            row[f"{a}_arg"] = aw
            row[f"{a}_margin"] = margins[a][-1]
            if a in op_err:
                op_err[a].append(1.0 if classify(aw, truth, cats)
                                 in OPERAND_DOMAIN else 0.0)
            if a == "wrong":
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
    sc = score_enrich(m_arr, acc, op_arr, swap_hits, true_hits, rng, args.alpha)
    v = verdict_enrich(gate0, sc)

    print(f"[enr] means: { {a: round(sc['means'][a], 3) for a in ARMS} }")
    print(f"[enr] acc:   { {a: round(acc[a], 2) for a in ARMS} }")
    print(f"[enr] G1 Δ={sc['g1'].value:+.3f} (p={sc['g1'].p:.4f}) flip={sc['flip']} "
          f"| G2 Δ={sc['g2'].value:+.3f} (p={sc['g2'].p:.4f}) "
          f"swap {swap_hits}/{len(cells)} vs true {true_hits} "
          f"| G3 Δ={sc['g3'].value:+.3f} (p={sc['g3'].p:.4f})")
    print(f"[enr] laws: pos Δ={sc['laws']['position'].value:+.3f} "
          f"depth Δ={sc['laws']['depth'].value:+.3f} "
          f"hkey Δ={sc['laws']['hkey'].value:+.3f} (advisory)")
    print(f"[enr] secondary operand-err shift Δ={sc['secondary'].value:+.3f} "
          f"(p={sc['secondary'].p:.4f})")
    print(f"[enr] VERDICT: {v}")

    result = {
        "model_id": args.model_id, "probe": "P-ENRICH-1", "seed": args.seed,
        "scale": S, "enrich_scale": args.enrich_scale, "ref_layer": L,
        "n_layers": n_layers, "enrich_layer": L_e, "depth_ctl_layer": L_dc,
        "h_key_layer": L_h, "alpha": args.alpha, "valid": valid,
        "union_size": len(union), "dropped_collisions": sorted(drop),
        "n_cells": len(cells), "gate0": gate0, "wrong_of": wrong_of,
        "gates": {"g1": asdict(sc["g1"]), "flip": sc["flip"],
                  "g2": asdict(sc["g2"]), "g3": asdict(sc["g3"]),
                  "secondary": asdict(sc["secondary"]),
                  "laws": {k: asdict(g) for k, g in sc["laws"].items()},
                  "swap_hits": swap_hits, "true_hits": true_hits,
                  "swap_coherent": sc["swap_coherent"]},
        "means": sc["means"], "acc": acc, "verdict": v, "cells": records}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "enrich_compose.json").write_text(
        json.dumps(_json_safe(result), indent=2, allow_nan=False))
    print(f"[enr] wrote {out}/enrich_compose.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="P-ENRICH-1 hop enrichment in-context")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--ref-layer", type=int, default=9)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--enrich-scale", type=float, default=2.0)
    ap.add_argument("--n-cells", type=int, default=0)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/enrich-compose/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
