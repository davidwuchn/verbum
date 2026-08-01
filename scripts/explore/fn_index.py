"""P-FN-INDEX — cross-family dispatch: do injected keys select WHICH map runs?

Pre-reg: mementum/knowledge/explore/program-plates-and-the-function-index.md
§P-FN-INDEX (FROZEN s292, Michael GO). The keystone of the program-plates
ladder: function choice is content-addressable iff an injected KEY selects
which resident map executes over a FIXED operand. Negative -> the ladder
stops honestly (function selection stays query-text-only).

Maps (5, two domains): geography city-of / country-of / continent-of (mh3
bank) + animals class-of / covering-of (the SECOND BANK, canonical home =
this file). Keys = mean last-token residual over 3 HELD-OUT exemplar
prompts per map minus the grand mean across maps (the "about to apply f"
state, map-level, item-independent). Dispatch cell: operand d_E installed
at its nonce slot (L_ref=9), NEUTRAL prompt naming no map, key injected at
the final token at L_inj; readout = first-token margin of f(X)'s product
over the UNION candidate set.

Conditions per cell: key_f / 4 other keys (shuffled-key null, includes
other-DOMAIN keys = the cross-family test) / matched random vector /
no-key. G1: paired permutation diagonal-vs-shuffled at 4 pre-declared
relative depths {.3,.45,.6,.75}, selection-corrected alpha/4, scored for
WITHIN-domain and UNION null scopes. G2: diagonal acc > no-key acc (the
key must FLIP the answer). Verdicts: INDEXED-DISPATCH /
PARTIAL-WITHIN-DOMAIN / NOT-DISPATCHABLE / inconclusive.

License: MIT (`λ provenance`).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
from holo_cap import NONCE_CANDS
from holo_frag import _json_safe

from verbum.dsp import gate, paired_permutation

_WRAP = Path(__file__).resolve().parents[2] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

DEPTHS = (0.3, 0.45, 0.6, 0.75)

# ── SECOND BANK — animals (canonical home; census/P-TYPE-PROB import here) ──
ANIMALS: dict[str, tuple[str, str]] = {
    # mammal -> fur
    "dog": ("mammal", "fur"), "cat": ("mammal", "fur"),
    "tiger": ("mammal", "fur"), "horse": ("mammal", "fur"),
    "bear": ("mammal", "fur"), "rabbit": ("mammal", "fur"),
    # bird -> feathers
    "eagle": ("bird", "feathers"), "sparrow": ("bird", "feathers"),
    "owl": ("bird", "feathers"), "duck": ("bird", "feathers"),
    "crow": ("bird", "feathers"), "penguin": ("bird", "feathers"),
    # fish -> scales
    "salmon": ("fish", "scales"), "shark": ("fish", "scales"),
    "trout": ("fish", "scales"), "tuna": ("fish", "scales"),
    "cod": ("fish", "scales"), "herring": ("fish", "scales"),
}
AN_LIST = list(ANIMALS)
CLASS_OF = {a: v[0] for a, v in ANIMALS.items()}
COVER_OF = {a: v[1] for a, v in ANIMALS.items()}
CLASSES = ["mammal", "bird", "fish"]
COVERS = ["fur", "feathers", "scales"]

CLASS_PREFIX = ("The wolf is classified as a mammal.\n"
                "The parrot is classified as a bird.\n"
                "The carp is classified as a fish.\n")
COVER_PREFIX = ("The wolf is covered in fur.\n"
                "The parrot is covered in feathers.\n"
                "The carp is covered in scales.\n")
CLASS_QUERY = "The {x} is classified as a"
COVER_QUERY = "The {x} is covered in"

# held-out key exemplars per map: (word, template) — never bank items
KEY_EXEMPLARS = {
    "city": [("Alhambra", "The {x} is located in the city of"),
             ("Great Wall", "The {x} is located in the city of"),
             ("Serengeti", "The {x} is located in the city of")],
    "country": [("Alhambra", "The {x} is located in the country of"),
                ("Great Wall", "The {x} is located in the country of"),
                ("Serengeti", "The {x} is located in the country of")],
    "continent": [("Alhambra", "The {x} is located on the continent of"),
                  ("Great Wall", "The {x} is located on the continent of"),
                  ("Serengeti", "The {x} is located on the continent of")],
    "class": [("wolf", "The {x} is classified as a"),
              ("parrot", "The {x} is classified as a"),
              ("carp", "The {x} is classified as a")],
    "cover": [("wolf", "The {x} is covered in"),
              ("parrot", "The {x} is covered in"),
              ("carp", "The {x} is covered in")],
}
GEO_MAPS = ("city", "country", "continent")
AN_MAPS = ("class", "cover")
ALL_MAPS = (*GEO_MAPS, *AN_MAPS)
DOMAIN_OF = {m: ("geo" if m in GEO_MAPS else "animal") for m in ALL_MAPS}

NEUTRAL = "Consider the {x}. The answer is"


# ══════════════════════════════════════════════════════════════════════════
# Frozen verdict logic (pure; --validate exercises it)
# ══════════════════════════════════════════════════════════════════════════
def score_layer(diag: np.ndarray, within: np.ndarray, union: np.ndarray,
                rng: np.random.Generator, alpha_sel: float) -> dict:
    """diag/within/union: per-cell margins (diag) and null-mean margins."""
    g_within = gate(float(np.mean(diag - within)),
                    paired_permutation(diag, within, rng), "greater",
                    alpha_sel, name="dispatch_within")
    g_union = gate(float(np.mean(diag - union)),
                   paired_permutation(diag, union, rng), "greater",
                   alpha_sel, name="dispatch_union")
    return {"contrast_within": g_within, "contrast_union": g_union,
            "diag_mean": float(diag.mean())}


def fn_index_verdict(gate0: bool, best: dict, g2_flip: bool,
                     rand_ok: bool) -> str:
    if not gate0:
        return "negative/inconclusive (gate-0)"
    w = best["contrast_within"].verdict
    u = best["contrast_union"].verdict
    if w and u and g2_flip and rand_ok:
        return "INDEXED-DISPATCH"
    if w and not u:
        return "PARTIAL-WITHIN-DOMAIN"
    if w and u and not (g2_flip and rand_ok):
        return "PARTIAL-WITHIN-DOMAIN"  # dispatch contrast w/o flip: partial
    return "NOT-DISPATCHABLE"


def run_validate(alpha: float) -> int:
    rng = np.random.default_rng(0)
    alpha_sel = alpha / len(DEPTHS)
    print("── P-FN-INDEX --validate (planted worlds, no model) ──")
    n, noise = 90, 0.6
    ok = True

    def world(diag_mu, within_mu, union_mu, flip=True, rand_flat=True):
        diag = diag_mu + rng.normal(0, noise, n)
        within = within_mu + rng.normal(0, noise, n)
        union = union_mu + rng.normal(0, noise, n)
        best = score_layer(diag, within, union, rng, alpha_sel)
        return fn_index_verdict(True, best, flip, rand_flat)

    calls = {
        "indexed": (world(1.5, 0.0, 0.0), "INDEXED-DISPATCH"),
        "within-only": (world(1.5, 0.0, 1.4), "PARTIAL-WITHIN-DOMAIN"),
        "flat": (world(0.0, 0.0, 0.0), "NOT-DISPATCHABLE"),
        "no-flip": (world(1.5, 0.0, 0.0, flip=False), "PARTIAL-WITHIN-DOMAIN"),
    }
    for w, (call, want) in calls.items():
        good = call == want
        print(f"[G1] {w}-world -> {call} (want {want}) {'OK' if good else 'FAIL'}")
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
    dec, _n, _u = mh3.resolve_parts(model)
    n_layers = len(dec)
    L, S = args.ref_layer, args.scale
    inj_layers = [round(d * n_layers) for d in DEPTHS]
    alpha_sel = args.alpha / len(DEPTHS)
    print(f"[fni] {args.model_id} L_ref={L} scale={S} key_scale="
          f"{args.key_scale} dev={dev} n_layers={n_layers} "
          f"inj_layers={inj_layers}")

    nonce = NONCE_CANDS[0]
    nonce_tid = tok(" " + nonce, add_special_tokens=False).input_ids[-1]

    def first_tid(w):
        return mh3.first_tid(tok, w)

    # product vocabularies + union candidate set (collisions dropped)
    product_of = {}
    for lm in mh3.LM_LIST:
        product_of[("city", lm)] = mh3.CITY_OF[lm]
        product_of[("country", lm)] = mh3.COUNTRY_OF[lm]
        product_of[("continent", lm)] = mh3.CONT_OF[lm]
    for a in AN_LIST:
        product_of[("class", a)] = CLASS_OF[a]
        product_of[("cover", a)] = COVER_OF[a]
    vocab = (set(mh3.CITIES) | set(mh3.COUNTRIES) | set(mh3.CONTINENTS)
             | set(CLASSES) | set(COVERS))
    tid_map, drop = {}, set()
    for w in sorted(vocab):
        t = first_tid(w)
        clash = [x for x, tt in tid_map.items() if tt == t]
        if clash:
            drop.add(w)
            drop.update(clash)
        tid_map[w] = t
    union = {w: tid_map[w] for w in sorted(vocab - drop)}
    print(f"[fni] union candidates: {len(union)} (dropped collisions: "
          f"{sorted(drop)})")

    # ── ceilings ───────────────────────────────────────────────────────────
    def real_pred(prefix, query, word, labels):
        ids = tok(prefix + query.format(x=word), return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        return max(labels, key=lambda k: lo[first_tid(k)])

    valid_geo = []
    for lm in mh3.LM_LIST:
        if (real_pred(mh3.CITY_PREFIX, mh3.CITY_QUERY, lm, mh3.CITIES)
                == mh3.CITY_OF[lm]
                and real_pred(mh3.COUNTRY_PREFIX, mh3.COUNTRY_QUERY, lm,
                              mh3.COUNTRIES) == mh3.COUNTRY_OF[lm]
                and real_pred(mh3.CONT_PREFIX, mh3.CONT_QUERY, lm,
                              mh3.CONTINENTS) == mh3.CONT_OF[lm]):
            valid_geo.append(lm)
    valid_an = []
    for a in AN_LIST:
        if (real_pred(CLASS_PREFIX, CLASS_QUERY, a, CLASSES) == CLASS_OF[a]
                and real_pred(COVER_PREFIX, COVER_QUERY, a, COVERS)
                == COVER_OF[a]):
            valid_an.append(a)
    print(f"[fni] ceilings: geo {len(valid_geo)}/18 animal {len(valid_an)}/18")
    gate0 = bool(len(valid_geo) >= 10 and len(valid_an) >= 10)
    if args.n_per_domain:
        valid_geo = valid_geo[:args.n_per_domain]
        valid_an = valid_an[:args.n_per_domain]

    # ── operand directions (both domains, one pooled build per domain) ─────
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

    d_geo = build_dirs(mh3.LM_LIST)
    d_an = build_dirs(AN_LIST)
    d_of = {**{("geo", x): d_geo[x] for x in mh3.LM_LIST},
            **{("animal", x): d_an[x] for x in AN_LIST}}
    dim = d_geo[mh3.LM_LIST[0]].shape[0]

    # ── keys: held-out exemplars, last-token residual per inj layer ────────
    def capture_last(prompt):
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            out = model(**ids, output_hidden_states=True)
        return {li: out.hidden_states[li + 1][0, -1, :].float().cpu().numpy()
                for li in inj_layers}

    raw_keys = {m: {li: [] for li in inj_layers} for m in ALL_MAPS}
    for m in ALL_MAPS:
        for word, tpl in KEY_EXEMPLARS[m]:
            caps = capture_last(tpl.format(x=word))
            for li in inj_layers:
                raw_keys[m][li].append(caps[li])
    keys = {}
    for li in inj_layers:
        means = {m: np.mean(raw_keys[m][li], axis=0) for m in ALL_MAPS}
        gm = np.mean(list(means.values()), axis=0)
        for m in ALL_MAPS:
            keys[(m, li)] = means[m] - gm
    key_norms = {m: float(np.linalg.norm(keys[(m, inj_layers[0])]))
                 for m in ALL_MAPS}
    print(f"[fni] key norms @L{inj_layers[0]}: "
          f"{ {m: round(v, 1) for m, v in key_norms.items()} }")

    def rand_like(vec):
        v = rng.standard_normal(dim)
        return v / (np.linalg.norm(v) + 1e-9) * float(np.linalg.norm(vec))

    # ── one dispatch forward ───────────────────────────────────────────────
    def cell_logits(domain, item, key_vec, li):
        prompt = NEUTRAL.format(x=nonce)
        ids = tok(prompt, return_tensors="pt").to(dev)
        toks = ids.input_ids[0].tolist()
        occ = [i for i, t in enumerate(toks) if t == nonce_tid]
        handles = []
        vt = torch.tensor(d_of[(domain, item)] * S, dtype=torch.float32,
                          device=dev)
        handles.append(dec[L].register_forward_hook(
            mh3.add_hook_at(vt, occ[-1])))
        if key_vec is not None:
            kt = torch.tensor(key_vec * args.key_scale, dtype=torch.float32,
                              device=dev)
            handles.append(dec[li].register_forward_hook(
                mh3.add_hook_at(kt, len(toks) - 1)))
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        for hd in handles:
            hd.remove()
        return lo

    def margin_and_hit(lo, m, item):
        prod = product_of[(m, item)]
        if prod not in union:
            return None, None
        others = [t for w, t in union.items() if w != prod]
        marg = float(lo[union[prod]] - max(lo[t] for t in others))
        return marg, bool(marg > 0)

    cells = ([("geo", lm, m) for lm in valid_geo for m in GEO_MAPS]
             + [("animal", a, m) for a in valid_an for m in AN_MAPS])
    cells = [(d, i, m) for (d, i, m) in cells
             if product_of[(m, i)] in union]
    print(f"[fni] cells: {len(cells)}")

    per_layer = {}
    records = []
    for li in inj_layers:
        diag, within, uni, rand_m, nokey_m = [], [], [], [], []
        diag_hit, nokey_hit = [], []
        for (dom, item, m) in cells:
            lo_d = cell_logits(dom, item, keys[(m, li)], li)
            mg_d, hit_d = margin_and_hit(lo_d, m, item)
            others_w, others_u = [], []
            for m2 in ALL_MAPS:
                if m2 == m:
                    continue
                lo_o = cell_logits(dom, item, keys[(m2, li)], li)
                mg_o, _ = margin_and_hit(lo_o, m, item)
                others_u.append(mg_o)
                if DOMAIN_OF[m2] == DOMAIN_OF[m]:
                    others_w.append(mg_o)
            lo_r = cell_logits(dom, item, rand_like(keys[(m, li)]), li)
            mg_r, _ = margin_and_hit(lo_r, m, item)
            lo_0 = cell_logits(dom, item, None, li)
            mg_0, hit_0 = margin_and_hit(lo_0, m, item)
            diag.append(mg_d)
            within.append(float(np.mean(others_w)) if others_w else mg_d)
            uni.append(float(np.mean(others_u)))
            rand_m.append(mg_r)
            nokey_m.append(mg_0)
            diag_hit.append(hit_d)
            nokey_hit.append(hit_0)
            records.append({"layer": li, "domain": dom, "item": item,
                            "map": m, "diag": mg_d,
                            "within_null": within[-1], "union_null": uni[-1],
                            "random": mg_r, "nokey": mg_0})
        diag = np.asarray(diag)
        sc = score_layer(diag, np.asarray(within), np.asarray(uni), rng,
                         alpha_sel)
        g_rand = gate(float(np.mean(diag - np.asarray(rand_m))),
                      paired_permutation(diag, np.asarray(rand_m), rng),
                      "greater", alpha_sel, name="vs_random")
        acc_d = float(np.mean(diag_hit))
        acc_0 = float(np.mean(nokey_hit))
        per_layer[str(li)] = {
            "score": {k: (asdict(v) if hasattr(v, "p") else v)
                      for k, v in sc.items()},
            "vs_random": asdict(g_rand), "diag_acc": acc_d,
            "nokey_acc": acc_0,
            "_g": (sc, g_rand, acc_d, acc_0)}
        print(f"[fni] L{li}: diag={sc['diag_mean']:.3f} "
              f"d_within={sc['contrast_within'].value:+.3f} "
              f"(p={sc['contrast_within'].p:.4f}) "
              f"d_union={sc['contrast_union'].value:+.3f} "
              f"(p={sc['contrast_union'].p:.4f}) "
              f"acc {acc_d:.2f} vs nokey {acc_0:.2f}")

    best_li = max(per_layer,
                  key=lambda k: per_layer[k]["_g"][0]["contrast_union"].value)
    sc, g_rand, acc_d, acc_0 = per_layer[best_li]["_g"]
    g2_flip = bool(acc_d > acc_0)
    rand_ok = bool(g_rand.verdict)
    verdict = fn_index_verdict(gate0, sc, g2_flip, rand_ok)
    for k in per_layer:
        del per_layer[k]["_g"]
    print(f"[fni] best layer L{best_li} (selection-corrected "
          f"alpha={alpha_sel}) -> VERDICT: {verdict}")

    result = {
        "model_id": args.model_id, "seed": args.seed, "scale": S,
        "key_scale": args.key_scale, "ref_layer": L,
        "inj_layers": inj_layers, "alpha": args.alpha,
        "alpha_selection_corrected": alpha_sel,
        "valid_geo": valid_geo, "valid_animal": valid_an,
        "union_size": len(union), "dropped_collisions": sorted(drop),
        "key_norms": key_norms, "n_cells": len(cells),
        "gate0": gate0, "per_layer": per_layer, "best_layer": int(best_li),
        "g2_flip": g2_flip, "vs_random_ok": rand_ok, "verdict": verdict,
        "cells": records}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "fn_index.json").write_text(
        json.dumps(_json_safe(result), indent=2, allow_nan=False))
    print(f"[fni] wrote {out}/fn_index.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="P-FN-INDEX cross-family dispatch")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--ref-layer", type=int, default=9)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--key-scale", type=float, default=2.0)
    ap.add_argument("--n-per-domain", type=int, default=0,
                    help="cap items per domain (0 = all valid; smoke uses 6)")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/fn-index/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
