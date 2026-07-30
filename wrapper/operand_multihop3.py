"""(3-hop capacity) chained h(f(g(X))) over ONE installed operand — depth-as-fuel.

Pre-reg: mementum/knowledge/explore/three-hop-capacity-prereg.md (APPROVED s282,
geography chain FROZEN). Successor to the 2-hop wrapper/operand_multihop.py (s279).

Chain (geography): landmark --g--> city --f--> country --h--> continent.
  X = a nonce carrying a LANDMARK's content d_E (built like the 2-hop d_E, last-token
  capture of a multi-token phrase). Two UNSTATED bridges (city, country) never appear in
  the readout prompt. Final readout = closed 3-way continent {Europe, Asia, Africa}.

Framing (s280 depth-budget): this is a CAPACITY experiment, not a capability rung. A
full-chain failure counts as DEPTH-limited ONLY IF the pieces work on the same model
(Gate-2 sub-chain controls). Pre-registered predictions: Qwen3-4B -> FAIL-BY-CAPACITY
(controls pass, full chain fails); Qwen3-32B -> PASS (full + mediation). The double
dissociation across scale, pieces held constant, is the strongest C8 evidence available.

Gates (frozen in the pre-reg):
  Gate 1  FULL CHAIN    : install landmark, "The {nonce} ... continent of __"
                          -> continent; nulls = random install, baseline, content-spec.
  Gate 2  SUB-CHAINS    : (the capacity discriminator)
            S1 links     : landmark->city, city->country, country->continent at ceiling.
            2-hop g.f    : install landmark -> its COUNTRY.
            2-hop f.h    : install CITY -> its CONTINENT (the s279-style 2-hop).
  Gate 3  MEDIATION     : (only where Gate-1 passes)
            3a depth-order : logit-lens peaks ordered city < country < continent.
            3b country-swap: late country-axis swap flips continent (random does not).
            3c city-swap   : mid city-axis swap flips country+continent (random not).

`λ measure`: operand = VALUE (d_E, centroids); g,f,h = ROUTING; readout = logits;
bridges localized by DEPTH (3a) + zone-steer (3b/3c), never single-head (0/128 heads).
`λ yardstick`: nulls beside every number; real-word ceiling gates each cell; predict
a-priori, gate on nulls, no forced fit. A RUNG (capacity mapping), hook-not-weight.
Architecture-robust via resolve_parts (dense Qwen3 4B/32B; hybrid 27B follow-on).

License: MIT (`λ provenance`; SuperBake method-reference only).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ── geography ladder: landmark -> (city, country, continent). Balanced 3-way. ──────
# Multi-token landmarks/cities handled by last-token capture (d_E) and first-token
# grading (closed candidate sets). Obscure cells are pruned by the real-word ceiling.
LANDMARKS: dict[str, tuple[str, str, str]] = {
    # Europe
    "Colosseum":      ("Rome",         "Italy",        "Europe"),
    "Louvre":         ("Paris",        "France",       "Europe"),
    "Parthenon":      ("Athens",       "Greece",       "Europe"),
    "Kremlin":        ("Moscow",       "Russia",       "Europe"),
    "Sagrada Familia":("Barcelona",    "Spain",        "Europe"),
    "Brandenburg Gate":("Berlin",      "Germany",      "Europe"),
    # Asia
    "Taj Mahal":      ("Agra",         "India",        "Asia"),
    "Kaaba":          ("Mecca",        "Saudi Arabia", "Asia"),
    "Petronas Towers":("Kuala Lumpur", "Malaysia",     "Asia"),
    "Angkor Wat":     ("Siem Reap",    "Cambodia",     "Asia"),
    "Tiananmen":      ("Beijing",      "China",        "Asia"),
    "Burj Khalifa":   ("Dubai",        "UAE",          "Asia"),
    # Africa
    "Pyramids":       ("Giza",         "Egypt",        "Africa"),
    "Sphinx":         ("Giza",         "Egypt",        "Africa"),
    "Karnak":         ("Luxor",        "Egypt",        "Africa"),
    "Table Mountain": ("Cape Town",    "South Africa", "Africa"),
    "Medina":         ("Marrakech",    "Morocco",      "Africa"),
    "Victoria Falls": ("Livingstone",  "Zambia",       "Africa"),
}

CONTINENTS = ["Europe", "Asia", "Africa"]
LM_LIST = list(LANDMARKS)
CITY_OF = {lm: v[0] for lm, v in LANDMARKS.items()}
COUNTRY_OF = {lm: v[1] for lm, v in LANDMARKS.items()}
CONT_OF = {lm: v[2] for lm, v in LANDMARKS.items()}
CITIES = sorted(set(CITY_OF.values()))
COUNTRIES = sorted(set(COUNTRY_OF.values()))
# city -> country/continent (deterministic; Giza collision is consistent)
CITY_COUNTRY = {v[0]: v[1] for v in LANDMARKS.values()}
CITY_CONT = {v[0]: v[2] for v in LANDMARKS.values()}
COUNTRY_CONT = {v[1]: v[2] for v in LANDMARKS.values()}
NONCE = "zorp"

# held-out exemplars (disjoint from the test landmarks/cities/countries)
CONT_PREFIX = (
    "The Alhambra is located on the continent of Europe.\n"
    "The Great Wall is located on the continent of Asia.\n"
    "The Serengeti is located on the continent of Africa.\n"
)
COUNTRY_PREFIX = (
    "The Alhambra is located in the country of Spain.\n"
    "The Great Wall is located in the country of China.\n"
    "The Serengeti is located in the country of Tanzania.\n"
)
CITY_PREFIX = (
    "The Alhambra is located in the city of Granada.\n"
    "The Great Wall is located in the city of Beijing.\n"
    "The Colosseum is located in the city of Rome.\n"
)
CITY2COUNTRY_PREFIX = (
    "The city of Lisbon is located in the country of Portugal.\n"
    "The city of Nairobi is located in the country of Kenya.\n"
    "The city of Osaka is located in the country of Japan.\n"
)
COUNTRY2CONT_PREFIX = (
    "The country of Portugal is located on the continent of Europe.\n"
    "The country of Japan is located on the continent of Asia.\n"
    "The country of Kenya is located on the continent of Africa.\n"
)

CONT_QUERY = "The {x} is located on the continent of"
COUNTRY_QUERY = "The {x} is located in the country of"
CITY_QUERY = "The {x} is located in the city of"
CITY2COUNTRY_QUERY = "The city of {x} is located in the country of"
COUNTRY2CONT_QUERY = "The country of {x} is located on the continent of"

# d_E build: cross-task declaratives (entity at END, before period -> capture -2)
FRAMES = [
    "The travelers admired {x}.",
    "A postcard showed {x}.",
    "The documentary featured {x}.",
    "The guidebook described {x}.",
    "Tourists photographed {x}.",
    "The lecture mentioned {x}.",
    "A painting depicted {x}.",
    "The article discussed {x}.",
]


def first_tid(tok, w):
    return tok(" " + w, add_special_tokens=False).input_ids[0]


def cap_hook(store, li):
    def hook(_m, _i, out):
        h = out[0] if isinstance(out, tuple) else out
        store[li] = h.detach().float().cpu().numpy()
    return hook


def add_hook_at(vec_t, pos):
    def hook(_m, _i, out):
        h = out[0] if isinstance(out, tuple) else out
        if 0 <= pos < h.shape[1]:
            h[0, pos, :] = h[0, pos, :] + vec_t.to(h.dtype)
        return out
    return hook


def resolve_parts(model):
    """(decoder-layers, final-norm, lm_head) across architectures (dense + hybrid)."""
    inner = model.model
    lm = inner if hasattr(inner, "layers") else inner.language_model
    return lm.layers, lm.norm, model.lm_head


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--ref-layer", type=int, default=9)          # install layer
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--swap-layers", type=int, nargs="+", default=[11, 15, 20])
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--device", default="mps")
    ap.add_argument("--mode", default="full", choices=["ceiling", "full"])
    ap.add_argument("--out", default="results/ffn-bake/operand-multihop3-qwen3-4b")
    args = ap.parse_args()

    L = args.ref_layer
    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    rng = np.random.default_rng(0)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    dec, norm_f, unembed = resolve_parts(model)
    S = args.scale

    cont_ids = {c: first_tid(tok, c) for c in CONTINENTS}
    country_ids = {c: first_tid(tok, c) for c in COUNTRIES}
    city_ids = {c: first_tid(tok, c) for c in CITIES}
    nonce_last = tok(" " + NONCE, add_special_tokens=False).input_ids[-1]
    print(f"[mh3] {args.model_id} L={L} scale={S} dev={dev} "
          f"n={NONCE!r} mode={args.mode}")

    def find_slot(ids_list):
        idx = [i for i, t in enumerate(ids_list) if t == nonce_last]
        return idx[-1] if idx else len(ids_list) - 1

    def pred_over(prefix, query, word, label_ids, adds=None):
        """argmax over a CLOSED candidate set (first-token logits) at nonce slot."""
        prompt = prefix + query.format(x=word)
        ids = tok(prompt, return_tensors="pt").to(dev)
        slot = find_slot(ids.input_ids[0].tolist())
        handles = []
        for (li, vec) in (adds or []):
            vt = torch.tensor(vec, dtype=torch.float32, device=dev)
            handles.append(dec[li].register_forward_hook(add_hook_at(vt, slot)))
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        for hd in handles:
            hd.remove()
        return max(label_ids, key=lambda k: lo[label_ids[k]])

    def cont_pred(word, adds=None):
        return pred_over(CONT_PREFIX, CONT_QUERY, word, cont_ids, adds)

    def country_pred(word, adds=None):
        return pred_over(COUNTRY_PREFIX, COUNTRY_QUERY, word, country_ids, adds)

    def city_pred(word, adds=None):
        return pred_over(CITY_PREFIX, CITY_QUERY, word, city_ids, adds)

    # ── S1 links (real word, no install) = the knowledge ceiling ──────────────────
    link_lm_city = {lm: int(city_pred(lm) == CITY_OF[lm]) for lm in LM_LIST}
    link_city_country = {
        c: int(pred_over(CITY2COUNTRY_PREFIX, CITY2COUNTRY_QUERY, c, country_ids)
               == CITY_COUNTRY[c]) for c in CITIES}
    link_country_cont = {
        c: int(pred_over(COUNTRY2CONT_PREFIX, COUNTRY2CONT_QUERY, c, cont_ids)
               == COUNTRY_CONT[c]) for c in COUNTRIES}

    def links_ok(lm):
        return (link_lm_city[lm]
                and link_city_country[CITY_OF[lm]]
                and link_country_cont[COUNTRY_OF[lm]])

    valid = [lm for lm in LM_LIST if links_ok(lm)]
    s1_lm_city = round(float(np.mean(list(link_lm_city.values()))), 3)
    s1_city_country = round(float(np.mean(list(link_city_country.values()))), 3)
    s1_country_cont = round(float(np.mean(list(link_country_cont.values()))), 3)
    by_cont = {c: sum(CONT_OF[lm] == c for lm in valid) for c in CONTINENTS}
    print(f"[mh3] S1 links: lm->city={s1_lm_city} city->country={s1_city_country} "
          f"country->cont={s1_country_cont}")
    print(f"[mh3] valid landmarks: {len(valid)}/{len(LM_LIST)} "
          f"per-continent={by_cont}  {valid}")

    if args.mode == "ceiling":
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "ceiling.json").write_text(json.dumps(
            {"s1_lm_city": s1_lm_city, "s1_city_country": s1_city_country,
             "s1_country_cont": s1_country_cont, "valid": valid,
             "per_continent": by_cont, "link_lm_city": link_lm_city,
             "link_city_country": link_city_country,
             "link_country_cont": link_country_cont}, indent=2))
        print(f"[mh3] ceiling mode: wrote {out}/ceiling.json")
        return

    # ── content directions: d_landmark, d_city, d_country (per-pool mean removed) ──
    def build_dirs(items, cap_L):
        per = {e: [] for e in items}
        for fr in FRAMES:
            for e in items:
                store: dict[int, np.ndarray] = {}
                h = dec[cap_L].register_forward_hook(cap_hook(store, cap_L))
                ids = tok(fr.format(x=e), return_tensors="pt").to(dev)
                with torch.no_grad():
                    model(**ids)
                h.remove()
                per[e].append(store[cap_L][0, -2, :])   # entity last subtoken
        em = {e: np.mean(per[e], axis=0) for e in items}
        gm = np.mean([em[e] for e in items], axis=0)
        return {e: em[e] - gm for e in items}, gm.shape[0]

    d_lm, dim = build_dirs(LM_LIST, L)
    d_city, _ = build_dirs(CITIES, L)
    d_country, _ = build_dirs(COUNTRIES, L)

    def rand_vec(norm):
        v = rng.standard_normal(dim)
        return v / (np.linalg.norm(v) + 1e-9) * norm

    # ══ GATE 1 — FULL CHAIN (install landmark -> continent) ══════════════════════
    def full_acc(use_rand=False):
        hits, cells = 0, {}
        for lm in valid:
            dv = (rand_vec(np.linalg.norm(d_lm[lm]) * S) if use_rand else d_lm[lm] * S)
            pred = cont_pred(NONCE, adds=[(L, dv)])
            ok = int(pred == CONT_OF[lm])
            cells[lm] = {"pred": pred, "truth": CONT_OF[lm], "ok": ok}
            hits += ok
        return (hits / len(valid) if valid else 0.0), cells

    g1_acc, g1_cells = full_acc()
    g1_rand, _ = full_acc(use_rand=True)
    g1_base = (sum(int(cont_pred(NONCE) == CONT_OF[lm]) for lm in valid) / len(valid)
               if valid else 0.0)
    print(f"\n[GATE1] full-chain install acc={g1_acc:.3f} (rand {g1_rand:.3f}, "
          f"baseline {g1_base:.3f}, n={len(valid)})")

    # content-specificity: install two landmarks of DIFFERENT continents -> both follow
    spec = []
    for lm in valid:
        for lp in valid:
            if CONT_OF[lm] == CONT_OF[lp]:
                continue
            pe = cont_pred(NONCE, adds=[(L, d_lm[lm] * S)])
            pp = cont_pred(NONCE, adds=[(L, d_lm[lp] * S)])
            spec.append(int(pe == CONT_OF[lm] and pp == CONT_OF[lp]))
    g1_spec = round(float(np.mean(spec)), 3) if spec else None
    print(f"[GATE1] content-specificity={g1_spec} (n={len(spec)})")

    # ══ GATE 2 — 2-HOP SUB-CHAINS (the capacity discriminator) ════════════════════
    # g.f : install landmark -> its COUNTRY
    def gof_acc(use_rand=False):
        hits, cells = 0, {}
        for lm in valid:
            dv = (rand_vec(np.linalg.norm(d_lm[lm]) * S) if use_rand else d_lm[lm] * S)
            pred = country_pred(NONCE, adds=[(L, dv)])
            ok = int(pred == COUNTRY_OF[lm])
            cells[lm] = {"pred": pred, "truth": COUNTRY_OF[lm], "ok": ok}
            hits += ok
        return (hits / len(valid) if valid else 0.0), cells

    gof, gof_cells = gof_acc()
    gof_rand, _ = gof_acc(use_rand=True)
    gof_base = (sum(int(country_pred(NONCE) == COUNTRY_OF[lm]) for lm in valid)
                / len(valid) if valid else 0.0)
    gof_pass = bool(gof > 0.66 and gof > gof_rand + 0.20 and gof > gof_base + 0.20)
    print(f"[GATE2] 2-hop g.f (landmark->country) acc={gof:.3f} "
          f"(rand {gof_rand:.3f}, base {gof_base:.3f}) pass={gof_pass}")

    # f.h : install CITY -> its CONTINENT (only cities whose city->cont link holds)
    valid_cities = [c for c in CITIES
                    if link_city_country[c] and link_country_cont[CITY_COUNTRY[c]]]

    def fh_acc(use_rand=False):
        hits, cells = 0, {}
        for c in valid_cities:
            dv = (rand_vec(np.linalg.norm(d_city[c]) * S)
                  if use_rand else d_city[c] * S)
            pred = cont_pred(NONCE, adds=[(L, dv)])
            ok = int(pred == CITY_CONT[c])
            cells[c] = {"pred": pred, "truth": CITY_CONT[c], "ok": ok}
            hits += ok
        return (hits / len(valid_cities) if valid_cities else 0.0), cells

    fh, fh_cells = fh_acc()
    fh_rand, _ = fh_acc(use_rand=True)
    fh_base = (sum(int(cont_pred(NONCE) == CITY_CONT[c]) for c in valid_cities)
               / len(valid_cities) if valid_cities else 0.0)
    fh_pass = bool(fh > 0.66 and fh > fh_rand + 0.20 and fh > fh_base + 0.20)
    print(f"[GATE2] 2-hop f.h (city->continent) acc={fh:.3f} "
          f"(rand {fh_rand:.3f}, base {fh_base:.3f}, n={len(valid_cities)}) "
          f"pass={fh_pass}")

    s1_pass = bool(s1_lm_city >= 0.8 and s1_city_country >= 0.8
                   and s1_country_cont >= 0.8)
    gate2_controls = bool(s1_pass and gof_pass and fh_pass)
    print(f"[GATE2] S1-links>=0.8={s1_pass} | controls_pass={gate2_controls}")

    # ══ GATE 3 — MEDIATION (only meaningful where Gate-1 passes) ══════════════════
    # 3a DEPTH ORDER: logit-lens peaks city < country < continent (installed landmark)
    def lens_order(lm):
        prompt = CONT_PREFIX + CONT_QUERY.format(x=NONCE)
        ids = tok(prompt, return_tensors="pt").to(dev)
        slot = find_slot(ids.input_ids[0].tolist())
        vt = torch.tensor(d_lm[lm] * S, dtype=torch.float32, device=dev)
        hd = dec[L].register_forward_hook(add_hook_at(vt, slot))
        with torch.no_grad():
            out = model(**ids, output_hidden_states=True)
        hd.remove()
        city, country, cont = CITY_OF[lm], COUNTRY_OF[lm], CONT_OF[lm]
        cty_i, cnt_i, con_i = city_ids[city], country_ids[country], cont_ids[cont]
        oth_city = [city_ids[c] for c in CITIES if c != city]
        oth_ctry = [country_ids[c] for c in COUNTRIES if c != country]
        oth_cont = [cont_ids[c] for c in CONTINENTS if c != cont]
        cm, ctm, com = [], [], []
        for h in out.hidden_states:
            last = h[0, -1, :]
            with torch.no_grad():
                lg = unembed(norm_f(last.unsqueeze(0))).float().cpu().numpy()[0]
            cm.append(lg[cty_i] - max(lg[j] for j in oth_city))
            ctm.append(lg[cnt_i] - max(lg[j] for j in oth_ctry))
            com.append(lg[con_i] - max(lg[j] for j in oth_cont))
        return int(np.argmax(cm)), int(np.argmax(ctm)), int(np.argmax(com))

    city_pk, ctry_pk, cont_pk = [], [], []
    for lm in valid:
        a, b, c = lens_order(lm)
        city_pk.append(a)
        ctry_pk.append(b)
        cont_pk.append(c)
    med_city = float(np.median(city_pk)) if city_pk else 0.0
    med_ctry = float(np.median(ctry_pk)) if ctry_pk else 0.0
    med_cont = float(np.median(cont_pk)) if cont_pk else 0.0
    order_ok = bool(med_city < med_ctry < med_cont)
    # shuffled-label null: random assignment of the three peak-lists
    shuf = [med_city, med_ctry, med_cont]
    rng.shuffle(shuf)
    shuf_ok = bool(shuf[0] < shuf[1] < shuf[2])
    g3a = bool(order_ok and not shuf_ok)
    print(f"\n[GATE3a] median peaks city={med_city} country={med_ctry} "
          f"continent={med_cont} order_ok={order_ok} (shuf_ok={shuf_ok}) pass={g3a}")

    # 3b LATE COUNTRY-SWAP: install landmark; add (d_country[c'] - d_country[c]) at a
    #    late layer -> continent flips to continent(c'). random matched-norm must not.
    def swap_bridge(kind, layers):
        """kind='country' (expect continent flip) or 'city' (country+continent flip)."""
        results = {}
        for lb in layers:
            flips, rflips, n = [], [], 0
            for lm in valid:
                if kind == "country":
                    src, dbank, keyfn = COUNTRY_OF[lm], d_country, COUNTRY_CONT
                    others = [c for c in COUNTRIES if COUNTRY_CONT[c] != CONT_OF[lm]]
                    tgt_of = keyfn
                else:
                    src, dbank, keyfn = CITY_OF[lm], d_city, CITY_CONT
                    others = [c for c in CITIES if CITY_CONT[c] != CONT_OF[lm]]
                    tgt_of = keyfn
                for tgt in others:
                    swap = (dbank[tgt] - dbank[src]) * S
                    pred = cont_pred(NONCE, adds=[(L, d_lm[lm] * S), (lb, swap)])
                    flips.append(int(pred == tgt_of[tgt]))
                    rnd = rand_vec(np.linalg.norm(swap))
                    rpred = cont_pred(NONCE, adds=[(L, d_lm[lm] * S), (lb, rnd)])
                    rflips.append(int(rpred == tgt_of[tgt]))
                    n += 1
            results[str(lb)] = {"flip_to_swapped": round(float(np.mean(flips)), 3),
                                "random_flip": round(float(np.mean(rflips)), 3), "n": n}
            r = results[str(lb)]
            print(f"[GATE3-{kind}] L_b={lb}: flip={r['flip_to_swapped']} "
                  f"(random {r['random_flip']}, n={n})")
        return results

    print("[GATE3b] country-axis swap (expect continent flip):")
    swap_country = swap_bridge("country", args.swap_layers)
    print("[GATE3c] city-axis swap (expect continent flip):")
    swap_city = swap_bridge("city", args.swap_layers)
    best_country = max(swap_country.values(), key=lambda r: r["flip_to_swapped"])
    best_city = max(swap_city.values(), key=lambda r: r["flip_to_swapped"])
    g3b = bool(best_country["flip_to_swapped"] >= 0.5
               and best_country["random_flip"] < 0.34)
    g3c = bool(best_city["flip_to_swapped"] >= 0.5 and best_city["random_flip"] < 0.34)
    print(f"[GATE3] 3b(country)={g3b} 3c(city)={g3c}")

    # ══ VERDICT (pre-registered, frozen) ═════════════════════════════════════════
    gate1 = bool(g1_acc > 0.66 and g1_acc > g1_rand + 0.20
                 and g1_acc > g1_base + 0.20 and (g1_spec or 0) > 0.5)
    gate3 = bool(g3a and (g3b or g3c)) if gate1 else False
    if gate2_controls and not gate1:
        capacity = "FAIL_BY_CAPACITY"       # pieces work, full fails -> depth-limited
    elif gate1 and gate3:
        capacity = "PASS"                    # full chain + mediation
    elif gate1 and not gate3:
        capacity = "PASS_NO_MEDIATION"
    elif not gate2_controls:
        capacity = "VOID_CONTENT"            # a piece failed -> not a depth verdict
    else:
        capacity = "AMBIGUOUS"
    print(f"\n[VERDICT] Gate1(full)={gate1} | Gate2(controls)={gate2_controls} "
          f"| Gate3(mediation)={gate3}")
    print(f"[VERDICT] CAPACITY PATTERN = {capacity}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {
        "model": args.model_id, "device": dev, "ref_layer": L, "scale": S,
        "nonce": NONCE, "landmarks": {lm: list(v) for lm, v in LANDMARKS.items()},
        "s1_links": {"lm_city": s1_lm_city, "city_country": s1_city_country,
                     "country_cont": s1_country_cont, "pass": s1_pass,
                     "link_lm_city": link_lm_city,
                     "link_city_country": link_city_country,
                     "link_country_cont": link_country_cont},
        "valid": valid, "per_continent": by_cont,
        "gate1_full": {"install_acc": round(g1_acc, 3), "random": round(g1_rand, 3),
                       "baseline": round(g1_base, 3), "content_specificity": g1_spec,
                       "n": len(valid), "cells": g1_cells, "pass": gate1},
        "gate2_controls": {
            "gof_landmark_country": {"acc": round(gof, 3), "random": round(gof_rand, 3),
                                     "baseline": round(gof_base, 3), "pass": gof_pass,
                                     "cells": gof_cells},
            "fh_city_continent": {"acc": round(fh, 3), "random": round(fh_rand, 3),
                                  "baseline": round(fh_base, 3), "n": len(valid_cities),
                                  "pass": fh_pass, "cells": fh_cells},
            "s1_pass": s1_pass, "controls_pass": gate2_controls},
        "gate3_mediation": {
            "depth_order": {"median_city_peak": med_city,
                            "median_country_peak": med_ctry,
                            "median_continent_peak": med_cont, "order_ok": order_ok,
                            "shuffled_ok": shuf_ok, "pass": g3a,
                            "city_peaks": city_pk, "country_peaks": ctry_pk,
                            "continent_peaks": cont_pk},
            "country_swap": {"by_layer": swap_country, "best": best_country,
                             "pass": g3b},
            "city_swap": {"by_layer": swap_city, "best": best_city, "pass": g3c},
            "gate3_pass": gate3},
        "verdict": {"gate1": gate1, "gate2_controls": gate2_controls, "gate3": gate3,
                    "capacity_pattern": capacity}}
    (out / "operand_multihop3.json").write_text(json.dumps(res, indent=2))
    print(f"[mh3] wrote {out}/operand_multihop3.json")


if __name__ == "__main__":
    main()
