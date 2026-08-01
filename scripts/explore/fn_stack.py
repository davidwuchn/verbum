"""P-STACK-1 — the seam test: do two INJECTED keys compose h(g(X)) in-context?

Pre-reg: mementum/knowledge/explore/program-plates-and-the-function-index.md
§P-STACK-1 (FROZEN s293, Michael GO). Rung 2 of the program-plates ladder,
unlocked by P-FN-INDEX INDEXED-DISPATCH. A program is a depth-ordered stack
of indexed exposures (program ≡ depth_ordered_stack | PC ≡ window). Minimal
case: over a FIXED operand X (a landmark), inject key(g=country-of) at an
EARLY window and key(h=country→continent) at a LATER window; verify the
COMPOSED product continent = h(g(X)). h alone is ill-typed on a landmark
(expects a country) so composition does observable work; g alone yields the
COUNTRY (wrong register). Native 3-hop is KNOWN to work (mh3) and single
dispatch is KNOWN to work (fn_index) — this asks whether injected keys
ASSEMBLE the 2-hop over a NEUTRAL prompt.

Chain (mh3 ground truth): landmark --country-of--> country
--country→continent--> continent = CONT_OF[landmark].

8 arms/cell: stack / g-alone / h-alone / wrong-window (order reversed) /
mismatch-near (g'=city-of) / mismatch-far (g'=animal class-of) /
random-both / no-key. Readout = first-token margin of CONT_OF[X] over the
UNION set (continents + countries + cities + animal-products); argmax on
the intermediate country = "stopped at g". 4 ordered window-pairs
w_g in {.3,.45} by w_h in {.6,.75}, selection-corrected alpha/4.

Gates: G1 stack > best-single-part (paired perm); G2 flip (stack acc >
best-single acc ∧ > no-key); G3 graded type discipline (well > near > far >
random). Verdicts: TYPED-STACKABLE / STACKABLE (untyped) / ORDER-FREE/BAG /
NOT-STACKABLE / inconclusive.

License: MIT (`λ provenance`).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

# fn_index = canonical home of the map keys (reuse, no fork)
from fn_index import ANIMALS, KEY_EXEMPLARS
from holo_cap import NONCE_CANDS
from holo_frag import _json_safe

from verbum.dsp import gate, paired_permutation

_WRAP = Path(__file__).resolve().parents[2] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

# ordered window pairs (w_g < w_h): early composition band, late readout band
PAIRS = ((0.3, 0.6), (0.3, 0.75), (0.45, 0.6), (0.45, 0.75))
DEPTHS = sorted({d for pr in PAIRS for d in pr})  # {.3,.45,.6,.75}

NONCE_PROMPT = "Consider the {x}. The answer is"

# NEW held-out key: country -> continent (the h map). Exemplars are the mh3
# held-out countries (Portugal/Japan/Kenya), disjoint from test landmarks.
COUNTRY2CONT_EXEMPLARS = [
    ("Portugal", "The country of {x} is located on the continent of"),
    ("Japan", "The country of {x} is located on the continent of"),
    ("Kenya", "The country of {x} is located on the continent of"),
]

# ── §P-STACK-1b shortcut-free chain: country -> capital (the h map) ──
# Composed target (capital) is NOT a direct landmark attribute (its city is a
# NON-capital city) -> genuinely 2-hop-only. Held-out exemplars share mh3's
# Portugal/Japan/Kenya. Test countries' capitals below (all city != capital).
COUNTRY_CAP = {
    "Spain": "Madrid", "India": "New Delhi", "Saudi Arabia": "Riyadh",
    "Cambodia": "Phnom Penh", "UAE": "Abu Dhabi", "Egypt": "Cairo",
    "Morocco": "Rabat", "Zambia": "Lusaka",
    # held-out key exemplars (never test countries)
    "Portugal": "Lisbon", "Japan": "Tokyo", "Kenya": "Nairobi",
}
COUNTRY2CAP_EXEMPLARS = [
    ("Portugal", "The capital of {x} is"),
    ("Japan", "The capital of {x} is"),
    ("Kenya", "The capital of {x} is"),
]
CAP_PREFIX = ("The capital of Portugal is Lisbon.\n"
              "The capital of Japan is Tokyo.\n"
              "The capital of Kenya is Nairobi.\n")
CAP_QUERY = "The capital of {x} is"


# ══════════════════════════════════════════════════════════════════════════
# Frozen verdict logic (pure; --validate exercises it)
# ══════════════════════════════════════════════════════════════════════════
def score_pair(stack, best_single, wrong, mnear, mfar, rand,
               rng, alpha_sel) -> dict:
    """All args: per-cell margin arrays. Returns the frozen gate set."""
    def g(a, b, name):
        return gate(float(np.mean(a - b)), paired_permutation(a, b, rng),
                    "greater", alpha_sel, name=name)
    g1 = g(stack, best_single, "compose_vs_parts")   # primary
    g_ww = g(stack, wrong, "order_matters")          # stack >> wrong-window
    g_rand = g(stack, rand, "vs_random")
    g_typed = g(stack, mnear, "type_discipline")     # well-typed > near-mismatch
    # graded (JOIN-TYPED shape): well > near > far > random, monotone
    m = (float(stack.mean()), float(mnear.mean()),
         float(mfar.mean()), float(rand.mean()))
    graded = bool(m[0] > m[1] > m[2] >= m[3])
    return {"compose_vs_parts": g1, "order_matters": g_ww,
            "vs_random": g_rand, "type_discipline": g_typed,
            "graded": graded, "means": {"stack": m[0], "near": m[1],
                                        "far": m[2], "random": m[3]},
            "stack_mean": float(stack.mean())}


def stack_verdict(gate0: bool, sc: dict, g2_flip: bool) -> str:
    if not gate0:
        return "negative/inconclusive (gate-0)"
    g1 = sc["compose_vs_parts"].verdict
    g_rand = sc["vs_random"].verdict
    if not (g1 and g2_flip and g_rand):
        return "NOT-STACKABLE"
    if not sc["order_matters"].verdict:   # wrong-window composes too
        return "ORDER-FREE/BAG"
    if sc["type_discipline"].verdict and sc["graded"]:
        return "TYPED-STACKABLE"
    return "STACKABLE (untyped)"


def run_validate(alpha: float) -> int:
    rng = np.random.default_rng(0)
    alpha_sel = alpha / len(PAIRS)
    print("── P-STACK-1 --validate (planted worlds, no model) ──")
    n, noise = 60, 0.5
    ok = True

    def arr(mu):
        return mu + rng.normal(0, noise, n)

    def world(stack_mu, single_mu, wrong_mu, near_mu, far_mu, rand_mu, flip):
        sc = score_pair(arr(stack_mu), arr(single_mu), arr(wrong_mu),
                        arr(near_mu), arr(far_mu), arr(rand_mu), rng, alpha_sel)
        return stack_verdict(True, sc, flip)

    calls = {
        # stack high, parts low, order matters, mismatch graded -> TYPED
        "composes": (world(1.6, 0.0, 0.0, 0.6, 0.2, 0.0, True),
                     "TYPED-STACKABLE"),
        # h-alone already works: stack ≈ best single -> NOT
        "single-only": (world(1.0, 1.0, 0.0, 0.4, 0.2, 0.0, True),
                        "NOT-STACKABLE"),
        # wrong-window composes just as well -> ORDER-FREE
        "order-free": (world(1.6, 0.0, 1.6, 0.6, 0.2, 0.0, True),
                       "ORDER-FREE/BAG"),
        # mismatch composes as well as match -> untyped
        "untyped": (world(1.6, 0.0, 0.0, 1.6, 1.5, 0.0, True),
                    "STACKABLE (untyped)"),
        # no flip -> NOT
        "no-flip": (world(1.6, 0.0, 0.0, 0.6, 0.2, 0.0, False),
                    "NOT-STACKABLE"),
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
    alpha_sel = args.alpha / len(PAIRS)
    print(f"[stk] {args.model_id} L_ref={L} scale={S} key_scale={args.key_scale} "
          f"dev={dev} n_layers={n_layers} pairs={pair_layers}")

    nonce = NONCE_CANDS[0]
    nonce_tid = tok(" " + nonce, add_special_tokens=False).input_ids[-1]

    def first_tid(w):
        return mh3.first_tid(tok, w)

    # ── chain config (continent = frozen P-STACK-1; capital = §P-STACK-1b) ──
    is_cap = args.chain == "capital"
    h_key = "country2cap" if is_cap else "country2cont"
    cap_labels = sorted({COUNTRY_CAP[mh3.COUNTRY_OF[lm]] for lm in mh3.LM_LIST
                         if mh3.COUNTRY_OF[lm] in COUNTRY_CAP}) if is_cap else []

    def target_of(lm):
        return COUNTRY_CAP[mh3.COUNTRY_OF[lm]] if is_cap else mh3.CONT_OF[lm]

    def shortcut_of(lm):
        return mh3.CITY_OF[lm] if is_cap else None

    print(f"[stk] chain={args.chain} h_key={h_key}")

    # ── union candidate set (continents + countries + cities + animal prods) ──
    covers = sorted({v[1] for v in ANIMALS.values()})
    classes = sorted({v[0] for v in ANIMALS.values()})
    vocab = (set(mh3.CONTINENTS) | set(mh3.COUNTRIES) | set(mh3.CITIES)
             | set(classes) | set(covers))
    if is_cap:
        vocab |= set(cap_labels)   # composed answers (capitals)
    tid_map, drop = {}, set()
    for w in sorted(vocab):
        t = first_tid(w)
        clash = [x for x, tt in tid_map.items() if tt == t]
        if clash:
            drop.add(w)
            drop.update(clash)
        tid_map[w] = t
    union = {w: tid_map[w] for w in sorted(vocab - drop)}
    print(f"[stk] union candidates: {len(union)} (dropped: {sorted(drop)})")

    # ── ceilings (gate-0): landmark→country, country→continent, composed ──
    def real_pred(prefix, query, word, labels):
        ids = tok(prefix + query.format(x=word), return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        return max(labels, key=lambda k: lo[first_tid(k)])

    valid = []
    for lm in mh3.LM_LIST:
        c = mh3.COUNTRY_OF[lm]
        g_ok = real_pred(mh3.COUNTRY_PREFIX, mh3.COUNTRY_QUERY, lm,
                         mh3.COUNTRIES) == c
        if is_cap:
            if c not in COUNTRY_CAP:
                continue
            cap = COUNTRY_CAP[c]
            if mh3.CITY_OF[lm] == cap:        # shortcut-free filter: city != capital
                continue
            h_ok = real_pred(CAP_PREFIX, CAP_QUERY, c, cap_labels) == cap
            comp_ok = True                    # landmark->capital is not a single query
        else:
            h_ok = real_pred(mh3.COUNTRY2CONT_PREFIX, mh3.COUNTRY2CONT_QUERY, c,
                             mh3.CONTINENTS) == mh3.COUNTRY_CONT[c]
            comp_ok = real_pred(mh3.CONT_PREFIX, mh3.CONT_QUERY, lm,
                                mh3.CONTINENTS) == mh3.CONT_OF[lm]
        if g_ok and h_ok and comp_ok:
            valid.append(lm)
    print(f"[stk] ceilings: valid landmarks {len(valid)}/{len(mh3.LM_LIST)}")
    gate0 = bool(len(valid) >= 10)
    if args.n_cells:
        valid = valid[:args.n_cells]

    # ── operand directions (landmarks), pooled build @ L_ref ──────────────
    def build_dirs(items):
        per = {e: [] for e in items}
        for fr in mh3.FRAMES:
            for e in items:
                store: dict[int, np.ndarray] = {}
                h = dec[L].register_forward_hook(mh3.cap_hook(store, L))
                ids = tok(fr.format(x=e), return_tensors="pt").to(dev)
                with torch.no_grad():
                    model(**ids)
                h.remove()
                per[e].append(store[L][0, -2, :])
        em = {e: np.mean(per[e], axis=0) for e in items}
        gm = np.mean([em[e] for e in items], axis=0)
        return {e: em[e] - gm for e in items}

    d_lm = build_dirs(mh3.LM_LIST)
    dim = d_lm[mh3.LM_LIST[0]].shape[0]

    # ── keys: country(g) / city(g'-near) / class(g'-far) / country2cont(h) ─
    # captured last-token residual per key layer, mean over held-out exemplars,
    # minus grand mean across the 4 maps (fn_index convention).
    key_specs = {
        "country": KEY_EXEMPLARS["country"],
        "city": KEY_EXEMPLARS["city"],
        "class": KEY_EXEMPLARS["class"],
        h_key: (COUNTRY2CAP_EXEMPLARS if is_cap else COUNTRY2CONT_EXEMPLARS),
    }

    def capture_last(prompt):
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            out = model(**ids, output_hidden_states=True)
        return {li: out.hidden_states[li + 1][0, -1, :].float().cpu().numpy()
                for li in key_layers}

    raw = {m: {li: [] for li in key_layers} for m in key_specs}
    for m, exs in key_specs.items():
        for word, tpl in exs:
            caps = capture_last(tpl.format(x=word))
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
    print(f"[stk] key norms @L{key_layers[0]}: "
          f"{ {m: round(v, 1) for m, v in key_norms.items()} }")

    def rand_like(vec):
        v = rng.standard_normal(dim)
        return v / (np.linalg.norm(v) + 1e-9) * float(np.linalg.norm(vec))

    # ── one forward: operand @ nonce slot (L_ref); keys @ final token ──────
    def cell_logits(lm, key_adds):
        prompt = NONCE_PROMPT.format(x=nonce)
        ids = tok(prompt, return_tensors="pt").to(dev)
        toks = ids.input_ids[0].tolist()
        occ = [i for i, t in enumerate(toks) if t == nonce_tid][-1]
        last = len(toks) - 1
        handles = []
        vt = torch.tensor(d_lm[lm] * S, dtype=torch.float32, device=dev)
        handles.append(dec[L].register_forward_hook(mh3.add_hook_at(vt, occ)))
        for (li, vec) in key_adds:
            kt = torch.tensor(vec * args.key_scale, dtype=torch.float32,
                              device=dev)
            handles.append(dec[li].register_forward_hook(
                mh3.add_hook_at(kt, last)))
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        for hd in handles:
            hd.remove()
        return lo

    def margin_hit(lo, prod):
        if prod not in union:
            return None, None, None
        others = [t for w, t in union.items() if w != prod]
        marg = float(lo[union[prod]] - max(lo[t] for t in others))
        argw = max(union, key=lambda w: lo[union[w]])
        return marg, bool(marg > 0), argw

    cells = [lm for lm in valid if target_of(lm) in union]
    print(f"[stk] cells: {len(cells)}")

    per_pair = {}
    records = []
    for (lg, lh) in pair_layers:
        arms = {k: [] for k in ("stack", "galone", "halone", "wrong",
                                "mnear", "mfar", "rand", "nokey")}
        hit = {"stack": [], "best": [], "nokey": []}
        stop_g = 0
        stack_city = 0        # advisory: stack argmax = direct city (shortcut)
        halone_city = 0       # advisory: h-alone argmax = direct city (shortcut)
        for lm in cells:
            prod = target_of(lm)             # composed answer (continent | capital)
            country = mh3.COUNTRY_OF[lm]      # g's intermediate output
            city = shortcut_of(lm)           # the direct shortcut token (or None)
            kg, kh = keys[("country", lg)], keys[(h_key, lh)]
            kcity, kclass = keys[("city", lg)], keys[("class", lg)]
            lo_s = cell_logits(lm, [(lg, kg), (lh, kh)])
            lo_g = cell_logits(lm, [(lg, kg)])
            lo_h = cell_logits(lm, [(lh, kh)])
            lo_w = cell_logits(lm, [(lg, kh), (lh, kg)])   # order reversed
            lo_mn = cell_logits(lm, [(lg, kcity), (lh, kh)])
            lo_mf = cell_logits(lm, [(lg, kclass), (lh, kh)])
            lo_r = cell_logits(lm, [(lg, rand_like(kg)), (lh, rand_like(kh))])
            lo_0 = cell_logits(lm, [])
            ms, hs, aw = margin_hit(lo_s, prod)
            mg, _, _ = margin_hit(lo_g, prod)
            mh_, _, aw_h = margin_hit(lo_h, prod)
            mw, _, _ = margin_hit(lo_w, prod)
            mmn, _, _ = margin_hit(lo_mn, prod)
            mmf, _, _ = margin_hit(lo_mf, prod)
            mr, _, _ = margin_hit(lo_r, prod)
            m0, h0, _ = margin_hit(lo_0, prod)
            arms["stack"].append(ms)
            arms["galone"].append(mg)
            arms["halone"].append(mh_)
            arms["wrong"].append(mw)
            arms["mnear"].append(mmn)
            arms["mfar"].append(mmf)
            arms["rand"].append(mr)
            arms["nokey"].append(m0)
            best_single = max(mg, mh_)
            hit["stack"].append(hs)
            hit["best"].append(bool(best_single > 0))
            hit["nokey"].append(h0)
            if aw == country:
                stop_g += 1
            if city is not None and aw == city:
                stack_city += 1
            if city is not None and aw_h == city:
                halone_city += 1
            records.append({"pair": [lg, lh], "landmark": lm, "truth": prod,
                            "country": country, "city": city, "stack": ms,
                            "galone": mg, "halone": mh_, "wrong": mw,
                            "mnear": mmn, "mfar": mmf, "random": mr,
                            "nokey": m0, "stack_arg": aw, "halone_arg": aw_h})
        A = {k: np.asarray(v, dtype=float) for k, v in arms.items()}
        best = np.maximum(A["galone"], A["halone"])
        sc = score_pair(A["stack"], best, A["wrong"], A["mnear"], A["mfar"],
                        A["rand"], rng, alpha_sel)
        acc_s = float(np.mean(hit["stack"]))
        acc_b = float(np.mean(hit["best"]))
        acc_0 = float(np.mean(hit["nokey"]))
        g2_flip = bool(acc_s > acc_b and acc_s > acc_0)
        per_pair[f"{lg}-{lh}"] = {
            "gates": {k: (asdict(v) if hasattr(v, "p") else v)
                      for k, v in sc.items()},
            "acc_stack": acc_s, "acc_best_single": acc_b, "acc_nokey": acc_0,
            "g2_flip": g2_flip, "stopped_at_g": stop_g / max(len(cells), 1),
            "stack_landed_on_city": stack_city / max(len(cells), 1),
            "halone_landed_on_city": halone_city / max(len(cells), 1),
            "_raw": (sc, g2_flip)}
        print(f"[stk] L{lg}->L{lh}: stack={sc['stack_mean']:.3f} "
              f"g1={sc['compose_vs_parts'].value:+.3f} "
              f"(p={sc['compose_vs_parts'].p:.4f}) "
              f"order={sc['order_matters'].value:+.3f} "
              f"typed={sc['type_discipline'].value:+.3f} graded={sc['graded']} "
              f"acc {acc_s:.2f} vs best {acc_b:.2f} flip={g2_flip} "
              f"stopG={stop_g / max(len(cells), 1):.2f} "
              f"h->city={halone_city / max(len(cells), 1):.2f}")

    best_pair = max(per_pair,
                    key=lambda k: per_pair[k]["_raw"][0]["compose_vs_parts"].value)
    sc, g2_flip = per_pair[best_pair]["_raw"]
    verdict = stack_verdict(gate0, sc, g2_flip)
    for k in per_pair:
        del per_pair[k]["_raw"]
    print(f"[stk] best pair {best_pair} (alpha_sel={alpha_sel}) -> "
          f"VERDICT: {verdict}")

    result = {
        "model_id": args.model_id, "chain": args.chain, "seed": args.seed,
        "scale": S, "key_scale": args.key_scale, "ref_layer": L,
        "n_layers": n_layers,
        "pairs": pair_layers, "alpha": args.alpha,
        "alpha_selection_corrected": alpha_sel, "valid": valid,
        "union_size": len(union), "dropped_collisions": sorted(drop),
        "key_norms": key_norms, "n_cells": len(cells), "gate0": gate0,
        "per_pair": per_pair, "best_pair": best_pair, "verdict": verdict,
        "cells": records}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "fn_stack.json").write_text(
        json.dumps(_json_safe(result), indent=2, allow_nan=False))
    print(f"[stk] wrote {out}/fn_stack.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="P-STACK-1 in-context composition")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--chain", default="continent",
                    choices=["continent", "capital"],
                    help="continent = frozen P-STACK-1; capital = §P-STACK-1b")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--ref-layer", type=int, default=9)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--key-scale", type=float, default=2.0)
    ap.add_argument("--n-cells", type=int, default=0,
                    help="cap landmarks (0 = all valid; smoke uses ~8)")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/fn-stack/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
