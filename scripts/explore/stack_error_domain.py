#!/usr/bin/env python3
"""Cheap error-domain diagnostic on P-STACK-1b (fn_stack --chain capital).

No model run — reads the frozen results JSON and classifies the argmax of the
`stack` and `h-alone` arms per cell into failure DOMAINS, to discriminate the
two mechanistic readings of the NOT-STACKABLE verdict:

  hop-1 / operand domain (CITY)     -> conditioning failure: h fires but cannot
      rebind g's output as its operand; readout collapses onto salient
      operand-domain place-names (the direct-city shortcut / attractors).
  h-output domain (WRONG-CAPITAL)   -> h fires, produces capital-type mass, but
      not bound to the SPECIFIC country g produced (generic h-output).
  COUNTRY (stopped-at-g)            -> hop-1 completed, hop-2 never fired
      ("h-not-firing").
  CORRECT                          -> composed answer won.

Reading the mix tells us what P-BAKE-STACK must install (operand rebinding vs
hop-2 ignition) before we burn anything.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

# COUNTRY -> CAPITAL (verbatim from fn_stack.py; the h map for the capital chain)
COUNTRY_CAP = {
    "Spain": "Madrid", "India": "New Delhi", "Saudi Arabia": "Riyadh",
    "Cambodia": "Phnom Penh", "UAE": "Abu Dhabi", "Egypt": "Cairo",
    "Morocco": "Rabat", "Zambia": "Lusaka",
    "Portugal": "Lisbon", "Japan": "Tokyo", "Kenya": "Nairobi",
}

# Full mh3 bank (wrapper/operand_multihop3.py LANDMARKS) — the argmax union is
# built over the WHOLE bank's cities/countries/continents, so classification
# must too (e.g. Paris=Louvre's city, Agra=Taj's city — operand-domain attractors).
_LANDMARKS = {
    "Colosseum": ("Rome", "Italy", "Europe"),
    "Louvre": ("Paris", "France", "Europe"),
    "Parthenon": ("Athens", "Greece", "Europe"),
    "Kremlin": ("Moscow", "Russia", "Europe"),
    "Sagrada Familia": ("Barcelona", "Spain", "Europe"),
    "Brandenburg Gate": ("Berlin", "Germany", "Europe"),
    "Taj Mahal": ("Agra", "India", "Asia"),
    "Kaaba": ("Mecca", "Saudi Arabia", "Asia"),
    "Petronas Towers": ("Kuala Lumpur", "Malaysia", "Asia"),
    "Angkor Wat": ("Siem Reap", "Cambodia", "Asia"),
    "Tiananmen": ("Beijing", "China", "Asia"),
    "Burj Khalifa": ("Dubai", "UAE", "Asia"),
    "Pyramids": ("Giza", "Egypt", "Africa"),
    "Sphinx": ("Giza", "Egypt", "Africa"),
    "Karnak": ("Luxor", "Egypt", "Africa"),
    "Table Mountain": ("Cape Town", "South Africa", "Africa"),
    "Medina": ("Marrakech", "Morocco", "Africa"),
    "Victoria Falls": ("Livingstone", "Zambia", "Africa"),
}
_CONTINENTS = ["Europe", "Asia", "Africa"]


def first_token(s: str) -> str:
    """Multi-token capitals graded on first token (New/Phnom/Abu...)."""
    return s.split()[0] if s else s


def build_categories(cells: list[dict]) -> dict[str, set[str]]:
    """Category membership by FIRST TOKEN, over the FULL mh3 bank (the union)."""
    # cap_labels = capitals of bank landmarks whose country is in COUNTRY_CAP
    capitals = {first_token(COUNTRY_CAP[c]) for (_, c, _) in _LANDMARKS.values()
                if c in COUNTRY_CAP}
    countries = {first_token(c) for (_, c, _) in _LANDMARKS.values()}
    cities = {first_token(city) for (city, _, _) in _LANDMARKS.values()}
    continents = {first_token(x) for x in _CONTINENTS}
    return {"capital": capitals, "country": countries,
            "city": cities, "continent": continents}


def classify(arg: str, truth: str, cats: dict[str, set[str]]) -> str:
    a = first_token(arg)
    t = first_token(truth)
    if a == t:
        return "CORRECT"
    if a in cats["capital"]:
        return "WRONG-CAPITAL"      # h-output domain
    if a in cats["city"]:
        return "CITY"               # hop-1/operand domain (shortcut/attractor)
    if a in cats["country"]:
        return "COUNTRY"            # stopped-at-g
    if a in cats["continent"]:
        return "CONTINENT"          # over-reduced past h
    return "OTHER"                  # stray union token


def main(path: str, pair: str | None = None) -> None:
    d = json.load(open(path))
    all_cells = d["cells"]
    best = d["best_pair"] if pair is None else pair
    lg, lh = (int(x) for x in best.split("-"))
    cats = build_categories(all_cells)
    cells = [c for c in all_cells if c.get("pair") == [lg, lh]]

    print("# P-STACK-1b error-domain diagnostic")
    print(f"# {d['model_id']}  chain={d['chain']}  verdict={d['verdict']}")
    print(f"# pair L{lg}->L{lh}  n_cells={len(cells)}")
    print(f"# categories: {len(cats['capital'])} capitals, "
          f"{len(cats['country'])} countries, {len(cats['city'])} cities")
    print()

    hdr = (f"{'landmark':<16}{'truth':<11}{'STACK->':<12}{'class':<15}"
           f"{'H-ALONE->':<12}{'class'}")
    print(hdr)
    print("-" * len(hdr))
    stack_dom = Counter()
    halone_dom = Counter()
    for c in sorted(cells, key=lambda x: x["landmark"]):
        sa, ha = c.get("stack_arg", "?"), c.get("halone_arg", "?")
        cs = classify(sa, c["truth"], cats)
        ch = classify(ha, c["truth"], cats)
        stack_dom[cs] += 1
        halone_dom[ch] += 1
        print(f"{c['landmark']:<16}{first_token(c['truth']):<11}"
              f"{first_token(sa):<12}{cs:<15}{first_token(ha):<12}{ch}")

    print()
    order = ["CORRECT", "WRONG-CAPITAL", "CITY", "COUNTRY", "CONTINENT", "OTHER"]
    n = len(cells)
    print("DOMAIN TALLY (stack arm):")
    for k in order:
        if stack_dom[k]:
            print(f"  {k:<15} {stack_dom[k]:>2}/{n}  ({stack_dom[k]/n:.0%})")
    print("DOMAIN TALLY (h-alone arm):")
    for k in order:
        if halone_dom[k]:
            print(f"  {k:<15} {halone_dom[k]:>2}/{n}  ({halone_dom[k]/n:.0%})")

    # the discriminator
    print()
    err = n - stack_dom["CORRECT"]
    operand = stack_dom["CITY"] + stack_dom["COUNTRY"]
    houtput = stack_dom["WRONG-CAPITAL"]
    print("── DISCRIMINATOR (stack errors only) ──")
    print(f"  errors                : {err}/{n}")
    print(f"  operand-domain (city+country): {operand}/{err}"
          + (f"  ({operand/err:.0%})" if err else ""))
    print(f"    of which CITY (shortcut/attractor, h can't rebind): "
          f"{stack_dom['CITY']}")
    print(f"    of which COUNTRY (stopped-at-g, h-not-firing): "
          f"{stack_dom['COUNTRY']}")
    print(f"  h-output domain (wrong capital, h fires unbound): {houtput}/{err}"
          + (f"  ({houtput/err:.0%})" if err else ""))


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else \
        "results/fn-stack-cap/qwen3-32b/fn_stack.json"
    pair = sys.argv[2] if len(sys.argv) > 2 else None
    main(str(Path(p)), pair)
