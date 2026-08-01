#!/usr/bin/env python3
"""§P-BAKE-STACK rung 3a — the PRODUCT-KEYED HOOK (cheap go/no-go; no weight write).

Frozen s294 (Michael GO "recommended bundle"). Tests the load-bearing contrast the
s294 error-domain diagnostic isolated: in-context stacking (§P-STACK-1b) fails
because hop-2 (h = country->capital) is NOT conditioned on hop-1's product — the
readout collapses onto operand-domain place-names (cities). Hypothesis: conditioning
h's injection on the PRESENCE of g's product (country-ness in the running residual)
installs the operand-rebinding linker `product(g) in key_passband(h)` and moves the
argmax OFF the operand domain onto the composed capital.

The isolation (two arms differ ONLY in h's key):
  stack_NONCE   : g@w_g + h@w_h added UNCONDITIONALLY  (= the §P-STACK-1b regime).
  stack_PRODUCT : g@w_g + h@w_h added with GAIN ∝ <residual, country-class dir>
                  (h fires ON g's product, not at a fixed window).
The difference between the arms IS the linker wire.

3a scores G1 (rebinding: operand-domain error PRODUCT << NONCE), G2 (composition:
composed-capital acc PRODUCT > NONCE/baseline/g-alone), G3 (conditioning: g-ablated
PRODUCT does not fire — acc≈0 and gain≈0). G4 fact-form is a WEIGHT null → deferred
to 3b (this hook cannot serialize a lookup). 3a FIRES gates the dear weight rung 3b.

Readout classification reuses scripts/explore/stack_error_domain.py 1:1.
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

# reuse (no fork): chain data + keys + nonce + json-safe + dsp + classifier
from fn_index import KEY_EXEMPLARS  # noqa: E402
from fn_stack import COUNTRY2CAP_EXEMPLARS, COUNTRY_CAP, NONCE_PROMPT  # noqa: E402
from holo_cap import NONCE_CANDS  # noqa: E402
from holo_frag import _json_safe  # noqa: E402
from stack_error_domain import build_categories, classify, first_token  # noqa: E402

from verbum.dsp import gate, paired_permutation  # noqa: E402

# operand-domain (hop-1 / attractor) error classes — the s294 diagnostic's finding
OPERAND_DOMAIN = {"CITY", "COUNTRY", "CONTINENT"}

# window pairs (w_g < w_h) — same grid as fn_stack (early composition / late readout)
PAIRS = ((0.3, 0.6), (0.3, 0.75), (0.45, 0.6), (0.45, 0.75))
DEPTHS = sorted({d for pr in PAIRS for d in pr})

# calibration countries for the country-class direction (held-out from the g→h test
# landmarks; a mix so d_cc is generic "a country is present", not one nation)
CC_CALIB = ["France", "Germany", "Japan", "Brazil", "Kenya", "Canada",
            "Portugal", "Thailand", "Norway", "Chile"]
CC_FRAME = "The landmark is located in the country of {x}"  # ends on the country


# ══════════════════════════════════════════════════════════════════════════
# Frozen verdict logic (pure; --validate exercises it)
# ══════════════════════════════════════════════════════════════════════════
def score_3a(op_err_nonce, op_err_product, acc_product, acc_nonce, acc_base,
             acc_galone, acc_gablate, gain_stack, gain_gablate, rng, alpha) -> dict:
    """All *_err/*_arr: per-cell arrays. acc_*: scalars. gain_*: per-cell arrays."""
    # G1 (primary, REBINDING): NONCE operand-error > PRODUCT operand-error (paired)
    g1 = gate(float(np.mean(op_err_nonce - op_err_product)),
              paired_permutation(op_err_nonce, op_err_product, rng),
              "greater", alpha, name="rebinding")
    # G2 (flip, COMPOSITION): product acc beats every non-composed arm
    g2 = bool(acc_product > acc_nonce and acc_product > acc_base
              and acc_product > acc_galone)
    # G3 (conditioning): g-ablated product does not fire, and its gain collapses
    gain_s, gain_a = float(np.mean(gain_stack)), float(np.mean(gain_gablate))
    g3 = bool(acc_gablate <= 0.10 and gain_a < 0.5 * max(gain_s, 1e-9))
    return {
        "rebinding": g1,
        "g2_flip": g2,
        "g3_conditioning": g3,
        "acc": {"product": acc_product, "nonce": acc_nonce, "base": acc_base,
                "galone": acc_galone, "gablate": acc_gablate},
        "operand_frac": {"product": float(np.mean(op_err_product)),
                         "nonce": float(np.mean(op_err_nonce))},
        "gain": {"stack": gain_s, "gablate": gain_a},
    }


def verdict_3a(gate0: bool, sc: dict) -> str:
    if not gate0:
        return "negative/inconclusive (gate-0)"
    if sc["rebinding"].verdict and sc["g2_flip"] and sc["g3_conditioning"]:
        return "LINKER-FIRES"          # → 3b weight-serialize unlocks
    if sc["rebinding"].verdict and sc["g2_flip"]:
        return "REBINDS-UNCONDITIONED"  # composes but g-ablation fires too
    return "LINKER-FAILS"               # product ~ nonce; conditioning no help


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
def run_validate(alpha: float) -> int:
    rng = np.random.default_rng(0)
    n = 10
    print("── P-BAKE-STACK 3a --validate (planted worlds, no model) ──")
    ok = True

    def world(op_nonce, op_prod, acc_p, acc_n, acc_b, acc_g, acc_ab,
              gain_s, gain_ab):
        # per-cell operand-error boolean arrays with the target fractions
        kn, kp = round(op_nonce * n), round(op_prod * n)
        en = np.array([1.0] * kn + [0.0] * (n - kn))
        ep = np.array([1.0] * kp + [0.0] * (n - kp))
        gs = np.full(n, gain_s)
        ga = np.full(n, gain_ab)
        sc = score_3a(en, ep, acc_p, acc_n, acc_b, acc_g, acc_ab, gs, ga, rng, alpha)
        return verdict_3a(True, sc)

    calls = {
        # linker installs: operand-error 0.8→0.1, product composes, g-ablation dead
        "linker-fires": (world(0.8, 0.1, 0.70, 0.10, 0.00, 0.00, 0.00, 1.0, 0.05),
                         "LINKER-FIRES"),
        # product moves errors + composes but g-ablated ALSO fires (gain unconditioned)
        "unconditioned": (world(0.8, 0.1, 0.70, 0.10, 0.00, 0.00, 0.60, 1.0, 0.9),
                          "REBINDS-UNCONDITIONED"),
        # product ≈ nonce (conditioning does nothing) -> fails
        "no-help": (world(0.8, 0.8, 0.10, 0.10, 0.00, 0.00, 0.00, 1.0, 0.05),
                    "LINKER-FAILS"),
        # product moves errors a bit but does not out-compose nonce -> fails (G2)
        "no-flip": (world(0.8, 0.3, 0.20, 0.30, 0.00, 0.00, 0.00, 1.0, 0.05),
                    "LINKER-FAILS"),
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
    depth_layer = {d: round(d * n_layers) for d in DEPTHS}
    pair_layers = [(depth_layer[a], depth_layer[b]) for (a, b) in PAIRS]
    key_layers = sorted(set(depth_layer.values()))
    alpha = args.alpha
    print(f"[bake3a] {args.model_id} L_ref={L} scale={S} key_scale={args.key_scale} "
          f"gain_cap={args.gain_cap} dev={dev} n_layers={n_layers} pairs={pair_layers}")

    nonce = NONCE_CANDS[0]
    nonce_tid = tok(" " + nonce, add_special_tokens=False).input_ids[-1]

    def first_tid(w):
        return mh3.first_tid(tok, w)

    # ── union candidate set (capital chain: continents+countries+cities+capitals) ─
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
    print(f"[bake3a] union candidates: {len(union)} (dropped: {sorted(drop)})")

    def target_of(lm):
        return COUNTRY_CAP[mh3.COUNTRY_OF[lm]]

    def shortcut_of(lm):
        return mh3.CITY_OF[lm]

    # ── ceilings (gate-0): landmark→country, country→capital (resident), composed ─
    def real_pred(prefix, query, word, labels):
        ids = tok(prefix + query.format(x=word), return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        return max(labels, key=lambda w: lo[first_tid(w)])

    valid = []
    for lm in mh3.LM_LIST:
        c = mh3.COUNTRY_OF[lm]
        if c not in COUNTRY_CAP:
            continue
        cap = COUNTRY_CAP[c]
        if mh3.CITY_OF[lm] == cap:                 # shortcut-free: city != capital
            continue
        # resident capital map must exist (we route INTO it, per s276)
        pref = ("The capital of Portugal is Lisbon.\nThe capital of Japan is Tokyo.\n"
                "The capital of Kenya is Nairobi.\n")
        cap_ok = first_token(real_pred(pref, "The capital of {x} is", c,
                                       list(COUNTRY_CAP.values()))) == first_token(cap)
        if cap_ok:
            valid.append(lm)
    gate0 = len(valid) >= 6
    print(f"[bake3a] ceilings: valid landmarks {len(valid)}/{len(mh3.LM_LIST)} "
          f"(resident capital map ok) gate0={gate0}")
    if args.n_cells:
        valid = valid[:args.n_cells]

    # ── operand (landmark) directions @ L_ref, pooled over FRAMES ─────────────
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
        return {e: em[e] - gm for e in items}, em

    d_lm, _ = build_dirs(mh3.LM_LIST, L)

    # ── keys: country(g) and country2cap(h), fn_stack convention ──────────────
    key_specs = {"country": KEY_EXEMPLARS["country"],
                 "country2cap": COUNTRY2CAP_EXEMPLARS}

    def capture_hidden(prompt, layers):
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            out = model(**ids, output_hidden_states=True)
        return {li: out.hidden_states[li + 1][0, -1, :].float().cpu().numpy()
                for li in layers}

    raw = {m: {li: [] for li in key_layers} for m in key_specs}
    for m, exs in key_specs.items():
        for word, tpl in exs:
            caps = capture_hidden(tpl.format(x=word), key_layers)
            for li in key_layers:
                raw[m][li].append(caps[li])
    keys = {}
    for li in key_layers:
        means = {m: np.mean(raw[m][li], axis=0) for m in key_specs}
        gm = np.mean(list(means.values()), axis=0)
        for m in key_specs:
            keys[(m, li)] = means[m] - gm
    key_norms = {m: float(np.linalg.norm(keys[(m, key_layers[0])]))
                 for m in key_specs}
    print(f"[bake3a] key norms @L{key_layers[0]}: "
          f"{ {m: round(v, 1) for m, v in key_norms.items()} }")

    # ── country-class product direction d_cc @ each h-layer + gain calibration ─
    #    d_cc = unit(mean_country residual minus mean_city residual) at h-layer;
    #    ref_proj = typical country-present projection (the gain=1 reference).
    h_layers = sorted({lh for (_, lh) in pair_layers})
    d_cc, ref_proj = {}, {}
    city_calib = [mh3.CITY_OF[lm] for lm in mh3.LM_LIST]
    for lh in h_layers:
        c_res = [capture_hidden(CC_FRAME.format(x=c), [lh])[lh] for c in CC_CALIB]
        city_res = [capture_hidden(f"The traveler visited {ct}", [lh])[lh]
                    for ct in city_calib]
        city_mu_np = np.mean(city_res, axis=0)
        cc_raw = np.mean(c_res, axis=0) - city_mu_np
        u = cc_raw / (np.linalg.norm(cc_raw) + 1e-9)
        d_cc[lh] = u
        # reference = mean country-present projection (city-mean subtracted)
        proj = [float(np.dot(r - city_mu_np, u)) for r in c_res]
        ref_proj[lh] = max(float(np.mean(proj)), 1e-6)
    print(f"[bake3a] d_cc ref_proj: "
          f"{ {lh: round(v, 2) for lh, v in ref_proj.items()} }")

    # ── hooks ─────────────────────────────────────────────────────────────────
    def gain_hook(vec_t, lh, city_mu_t):
        """Add vec_t at the FINAL token scaled by country-ness gain (product-keyed)."""
        u_t = torch.tensor(d_cc[lh], dtype=torch.float32, device=dev)

        def hook(_m, _i, out):
            h = out[0] if isinstance(out, tuple) else out
            last = h.shape[1] - 1
            r = h[0, last, :].detach().float() - city_mu_t
            proj = float(torch.dot(r, u_t).item())
            gain = float(np.clip(proj / ref_proj[lh], 0.0, args.gain_cap))
            h[0, last, :] = h[0, last, :] + (vec_t * gain).to(h.dtype)
            hook.gain = gain
            return out
        hook.gain = 0.0
        return hook

    city_mu = {lh: torch.tensor(
        np.mean([capture_hidden(f"The traveler visited {ct}", [lh])[lh]
                 for ct in city_calib], axis=0), dtype=torch.float32, device=dev)
        for lh in h_layers}

    def cell_logits(lm, adds):
        """adds: (layer, vec, mode), mode in {fixed,gain}. Returns (logits, gain)."""
        prompt = NONCE_PROMPT.format(x=nonce)
        ids = tok(prompt, return_tensors="pt").to(dev)
        toks = ids.input_ids[0].tolist()
        occ = [i for i, t in enumerate(toks) if t == nonce_tid][-1]
        handles, gain_hooks = [], []
        vt = torch.tensor(d_lm[lm] * S, dtype=torch.float32, device=dev)
        handles.append(dec[L].register_forward_hook(mh3.add_hook_at(vt, occ)))
        for (li, vec, mode) in adds:
            kt = torch.tensor(vec * args.key_scale, dtype=torch.float32, device=dev)
            if mode == "gain":
                hk = gain_hook(kt, li, city_mu[li])
                handles.append(dec[li].register_forward_hook(hk))
                gain_hooks.append(hk)
            else:
                handles.append(dec[li].register_forward_hook(
                    mh3.add_hook_at(kt, len(toks) - 1)))
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        g = float(np.mean([hk.gain for hk in gain_hooks])) if gain_hooks else 0.0
        for hd in handles:
            hd.remove()
        return lo, g

    def argmax_word(lo):
        return max(union, key=lambda w: lo[union[w]])

    cells = [lm for lm in valid if target_of(lm) in union]
    cats = build_categories([{"country": mh3.COUNTRY_OF[lm], "city": shortcut_of(lm)}
                             for lm in cells])
    print(f"[bake3a] cells: {len(cells)}")

    def dom(a, truth):
        return classify(a, truth, cats)

    def acc(rows, argkey):
        return float(np.mean([1.0 if dom(r[argkey], r["truth"]) == "CORRECT"
                              else 0.0 for r in rows]))

    def operr(rows, argkey):
        return np.array([1.0 if dom(r[argkey], r["truth"]) in OPERAND_DOMAIN
                         else 0.0 for r in rows])

    per_pair, records = {}, []
    for (lg, lh) in pair_layers:
        kg, kh = keys[("country", lg)], keys[("country2cap", lh)]
        rows = []
        for lm in cells:
            truth = target_of(lm)
            lo_base, _ = cell_logits(lm, [])
            lo_g, _ = cell_logits(lm, [(lg, kg, "fixed")])
            lo_n, _ = cell_logits(lm, [(lg, kg, "fixed"), (lh, kh, "fixed")])
            lo_p, gain_s = cell_logits(lm, [(lg, kg, "fixed"), (lh, kh, "gain")])
            lo_ab, gain_ab = cell_logits(lm, [(lh, kh, "gain")])   # g ablated
            row = {"landmark": lm, "truth": truth, "country": mh3.COUNTRY_OF[lm],
                   "city": shortcut_of(lm),
                   "base_arg": argmax_word(lo_base), "galone_arg": argmax_word(lo_g),
                   "nonce_arg": argmax_word(lo_n), "product_arg": argmax_word(lo_p),
                   "gablate_arg": argmax_word(lo_ab),
                   "gain_stack": gain_s, "gain_gablate": gain_ab, "pair": [lg, lh]}
            rows.append(row)
            records.append(row)

        sc = score_3a(operr(rows, "nonce_arg"), operr(rows, "product_arg"),
                      acc(rows, "product_arg"), acc(rows, "nonce_arg"),
                      acc(rows, "base_arg"), acc(rows, "galone_arg"),
                      acc(rows, "gablate_arg"),
                      np.array([r["gain_stack"] for r in rows]),
                      np.array([r["gain_gablate"] for r in rows]), rng, alpha)
        v = verdict_3a(gate0, sc)
        per_pair[f"{lg}-{lh}"] = {
            "rebinding": asdict(sc["rebinding"]), "g2_flip": sc["g2_flip"],
            "g3_conditioning": sc["g3_conditioning"], "acc": sc["acc"],
            "operand_frac": sc["operand_frac"], "gain": sc["gain"], "verdict": v,
            "_rb": sc["rebinding"].value}
        print(f"[bake3a] L{lg}->L{lh}: rebind Δop={sc['rebinding'].value:+.3f} "
              f"(p={sc['rebinding'].p:.4f}) acc_prod={sc['acc']['product']:.2f} "
              f"acc_nonce={sc['acc']['nonce']:.2f} g3={sc['g3_conditioning']} "
              f"gain s/ab={sc['gain']['stack']:.2f}/{sc['gain']['gablate']:.2f} -> {v}")

    best_pair = max(per_pair, key=lambda k: per_pair[k]["_rb"])
    verdict = per_pair[best_pair]["verdict"]
    for k in per_pair:
        del per_pair[k]["_rb"]
    print(f"[bake3a] best pair {best_pair} -> VERDICT: {verdict}")

    result = {
        "model_id": args.model_id, "stage": "3a-product-keyed-hook",
        "seed": args.seed, "scale": S, "key_scale": args.key_scale,
        "gain_cap": args.gain_cap, "ref_layer": L, "n_layers": n_layers,
        "pairs": pair_layers, "alpha": alpha, "valid": valid,
        "union_size": len(union), "dropped_collisions": sorted(drop),
        "key_norms": key_norms, "ref_proj": {str(k): v for k, v in ref_proj.items()},
        "n_cells": len(cells), "gate0": gate0, "per_pair": per_pair,
        "best_pair": best_pair, "verdict": verdict, "cells": records}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "bake_stack.json").write_text(
        json.dumps(_json_safe(result), indent=2, allow_nan=False))
    print(f"[bake3a] wrote {out}/bake_stack.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="P-BAKE-STACK 3a product-keyed hook")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--ref-layer", type=int, default=9)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--key-scale", type=float, default=2.0)
    ap.add_argument("--gain-cap", type=float, default=1.5)
    ap.add_argument("--n-cells", type=int, default=0)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/bake-stack/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
