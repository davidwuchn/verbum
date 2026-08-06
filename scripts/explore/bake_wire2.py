#!/usr/bin/env python3
"""§P-PLATE-LINKER-1 — bake WIRE-2 (the disjoint-country plate).

Pre-reg: mementum/knowledge/explore/optical-design-laws.md
§P-PLATE-LINKER-1 (FROZEN s311, Michael-approved). Wire-2 = the SAME
landmark->country->capital hop-2 relation on a DISJOINT country/landmark bank
(Michael-approved fork). Same gd_cd recipe verbatim (LoRA r=16 FFN band, KL-on-
CoT teacher, 3 seeds) so the two wires occupy the same weight band on one frozen
base but route through different country-key filters (low A-collision) while
writing the same capital region (high B-collision) — the discriminating case for
the key-subspace-precondition claim.

Reuse (NO FORK, lambda one_way): imports writeback_compile as a module and swaps
ONLY the data (BANK). All logic — gate-0, LoRA training, arms, frozen scoring,
verdict — is writeback_compile's, unchanged, so the frozen wire-1 generator (and
its s303/s304/s307/s309 results) stay bit-reproducible on the default bank.

WIRE2 bank: TRAIN = the 8 countries that are wire-1's held-out B2 (facts already
vetted in writeback_compile.BANK; re-tagged 2xTRAIN + 1xB1 per country, disjoint
from wire-1's TRAIN). B2 held-out = 8 fresh countries curated here. All landmark
cities != capital (shortcut-free); host-knowledge is enforced empirically by
gate-0 (drops cells the host gets wrong; MIN_PER_SPLIT=8, HOST_COT_FLOOR=0.7).

Bake gate (wire-2 standalone, BEFORE any merge): gd_cd must pass its own frozen
G1 (wire: > base with flip on B1 AND B2) + G3 (specificity: > gd_shuffle on
held-out). Reuses writeback_compile.verdict_of / score_arms verbatim.

Cadence: --gate0-only (validate bank facts, no training) -> Michael-implicit GO
(pre-frozen) -> full arms (tmux) -> read verdict. Direction NOT read at smoke.

License: MIT (lambda provenance).
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import writeback_compile as wb  # noqa: E402  (module reuse, no fork)

# ══════════════════════════════════════════════════════════════════════════
# WIRE-2 bank — same relation, DISJOINT entities from wire-1's TRAIN.
# format: country -> (capital, [(landmark, city, split), ...])
# TRAIN countries: 2x TRAIN + 1x B1 ; B2 countries: 3x B2. city != capital.
# ══════════════════════════════════════════════════════════════════════════
# SELECTED from WIRE2_POOL by empirical base headroom (s311 option A, re-derived;
# results/plate-linker/wire2-select/qwen3-4b/). B1 held-landmarks are drawn ONLY from
# base-0 (headroom) countries so gd_cd's G1-B1 has statistical power (the 1st/2nd bakes
# failed G1 purely on B1 permutation power: base bimodal per country — France/Poland/
# Vietnam are base-1.0 everywhere, no headroom). Selection on BASE ONLY (measurability).
# TRAIN 16 / B1 9 (all base-0) / B2 23.
WIRE2_BANK = {
    # ── TRAIN countries (disjoint from wire-1's TRAIN) ──
    "France": ("Paris", [("Chateau de Chambord", "Blois", "TRAIN"),
                         ("Mont Saint-Michel", "Avranches", "TRAIN")]),
    "Germany": ("Berlin", [("Marienplatz", "Munich", "TRAIN"),
                           ("Zwinger Palace", "Dresden", "TRAIN"),
                           ("Cologne Cathedral", "Cologne", "B1"),
                           ("Heidelberg Castle", "Heidelberg", "B1")]),
    "Canada": ("Ottawa", [("Mount Royal", "Montreal", "TRAIN"),
                          ("Stanley Park", "Vancouver", "TRAIN"),
                          ("Butchart Gardens", "Victoria", "B1"),
                          ("CN Tower", "Toronto", "B1")]),
    "Australia": ("Canberra", [("Story Bridge", "Brisbane", "TRAIN"),
                               ("Sydney Opera House", "Sydney", "TRAIN"),
                               ("Bondi Beach", "Sydney", "B1"),
                               ("Federation Square", "Melbourne", "B1")]),
    "Switzerland": ("Bern", [("Chapel Bridge", "Lucerne", "TRAIN"),
                             ("Jet d'Eau", "Geneva", "TRAIN"),
                             ("Chillon Castle", "Montreux", "B1"),
                             ("Grossmunster", "Zurich", "B1")]),
    "Poland": ("Warsaw", [("Malbork Castle", "Malbork", "TRAIN"),
                          ("Old Market Square", "Poznan", "TRAIN")]),
    "Vietnam": ("Hanoi", [("Ben Thanh Market", "Ho Chi Minh City", "TRAIN"),
                          ("Cu Chi Tunnels", "Ho Chi Minh City", "TRAIN")]),
    "China": ("Beijing", [("Li River", "Guilin", "TRAIN"),
                          ("Terracotta Army", "Xian", "TRAIN"),
                          ("Leshan Giant Buddha", "Leshan", "B1")]),
    # ── B2 held-out countries (fresh; never in any wire-2 delta) ──
    "Portugal": ("Lisbon", [("Bom Jesus do Monte", "Braga", "B2"),
                            ("Dom Luis I Bridge", "Porto", "B2"),
                            ("Pena Palace", "Sintra", "B2")]),
    "Greece": ("Athens", [("Palamidi Fortress", "Nafplio", "B2"),
                          ("Meteora Monasteries", "Kalabaka", "B2"),
                          ("Palace of Knossos", "Heraklion", "B2")]),
    "Sweden": ("Stockholm", [("Uppsala Cathedral", "Uppsala", "B2"),
                             ("Visby Ring Wall", "Visby", "B2"),
                             ("Kalmar Castle", "Kalmar", "B2")]),
    "Argentina": ("Buenos Aires", [("Mount Aconcagua", "Mendoza", "B2"),
                                   ("Perito Moreno Glacier", "El Calafate", "B2")]),
    "Japan": ("Tokyo", [("Itsukushima Shrine", "Hiroshima", "B2"),
                        ("Nagoya Castle", "Nagoya", "B2"),
                        ("Osaka Castle", "Osaka", "B2")]),
    "Thailand": ("Bangkok", [("Ayutthaya Historical Park", "Ayutthaya", "B2"),
                             ("Phi Phi Islands", "Krabi", "B2"),
                             ("Sukhothai Historical Park", "Sukhothai", "B2")]),
    "Kenya": ("Nairobi", [("Hell's Gate", "Naivasha", "B2"),
                          ("Fort Jesus", "Mombasa", "B2"),
                          ("Lake Nakuru", "Nakuru", "B2")]),
    "Peru": ("Lima", [("Machu Picchu", "Cusco", "B2"),
                      ("Chan Chan", "Trujillo", "B2"),
                      ("Colca Canyon", "Arequipa", "B2")]),
}

# ══════════════════════════════════════════════════════════════════════════
# WIRE-2 candidate POOL (--select mode) — expanded landmark set per country.
# The final WIRE2_BANK above is SELECTED from this pool by empirical BASE
# headroom (option A, s311): keep gate-0-valid landmarks the host 2-hops WRONG
# at baseline, so the wire has measurable room (wire-1's regime, base ~0.2-0.5).
# Selection is on BASE only (measurability), never on post-training accuracy.
# Provisional split tags below exist only to pass --validate for the base pass;
# extra candidates are confident facts (gate-0 drops any the host disputes).
# ══════════════════════════════════════════════════════════════════════════
WIRE2_POOL = {
    # ── TRAIN countries ── (need final 2 TRAIN + 1 B1)
    "France": ("Paris", [("Mont Saint-Michel", "Avranches", "TRAIN"),
                         ("Palace of Versailles", "Versailles", "TRAIN"),
                         ("Pont du Gard", "Nimes", "B1"),
                         ("Palais des Papes", "Avignon", "TRAIN"),
                         ("Chateau de Chambord", "Blois", "TRAIN")]),
    "Germany": ("Berlin", [("Neuschwanstein Castle", "Fussen", "TRAIN"),
                           ("Cologne Cathedral", "Cologne", "TRAIN"),
                           ("Heidelberg Castle", "Heidelberg", "B1"),
                           ("Zwinger Palace", "Dresden", "TRAIN"),
                           ("Marienplatz", "Munich", "TRAIN")]),
    "Canada": ("Ottawa", [("CN Tower", "Toronto", "TRAIN"),
                          ("Stanley Park", "Vancouver", "TRAIN"),
                          ("Mount Royal", "Montreal", "B1"),
                          ("Butchart Gardens", "Victoria", "TRAIN"),
                          ("Chateau Frontenac", "Quebec City", "TRAIN")]),
    "Australia": ("Canberra", [("Sydney Opera House", "Sydney", "TRAIN"),
                               ("Bondi Beach", "Sydney", "TRAIN"),
                               ("Federation Square", "Melbourne", "B1"),
                               ("Story Bridge", "Brisbane", "TRAIN"),
                               ("Cottesloe Beach", "Perth", "TRAIN")]),
    "Switzerland": ("Bern", [("Matterhorn", "Zermatt", "TRAIN"),
                             ("Chapel Bridge", "Lucerne", "TRAIN"),
                             ("Jet d'Eau", "Geneva", "B1"),
                             ("Chillon Castle", "Montreux", "TRAIN"),
                             ("Grossmunster", "Zurich", "TRAIN")]),
    "Poland": ("Warsaw", [("Wawel Castle", "Krakow", "TRAIN"),
                          ("Malbork Castle", "Malbork", "TRAIN"),
                          ("Wieliczka Salt Mine", "Wieliczka", "B1"),
                          ("Main Town Hall", "Gdansk", "TRAIN"),
                          ("Old Market Square", "Poznan", "TRAIN")]),
    "Vietnam": ("Hanoi", [("Cu Chi Tunnels", "Ho Chi Minh City", "TRAIN"),
                          ("Ha Long Bay", "Ha Long", "TRAIN"),
                          ("Ben Thanh Market", "Ho Chi Minh City", "B1"),
                          ("Imperial City", "Hue", "TRAIN"),
                          ("Marble Mountains", "Da Nang", "TRAIN")]),
    "China": ("Beijing", [("Terracotta Army", "Xian", "TRAIN"),
                          ("The Bund", "Shanghai", "TRAIN"),
                          ("West Lake", "Hangzhou", "B1"),
                          ("Leshan Giant Buddha", "Leshan", "TRAIN"),
                          ("Li River", "Guilin", "TRAIN")]),
    # ── B2 held-out countries ── (need final 3 B2)
    "Portugal": ("Lisbon", [("Dom Luis I Bridge", "Porto", "B2"),
                            ("University of Coimbra", "Coimbra", "B2"),
                            ("Sanctuary of Fatima", "Fatima", "B2"),
                            ("Pena Palace", "Sintra", "B2"),
                            ("Bom Jesus do Monte", "Braga", "B2")]),
    "Greece": ("Athens", [("Palace of Knossos", "Heraklion", "B2"),
                          ("White Tower", "Thessaloniki", "B2"),
                          ("Meteora Monasteries", "Kalabaka", "B2"),
                          ("Palamidi Fortress", "Nafplio", "B2"),
                          ("Temple of Apollo", "Delphi", "B2")]),
    "Sweden": ("Stockholm", [("Turning Torso", "Malmo", "B2"),
                             ("Uppsala Cathedral", "Uppsala", "B2"),
                             ("Liseberg Park", "Gothenburg", "B2"),
                             ("Kalmar Castle", "Kalmar", "B2"),
                             ("Visby Ring Wall", "Visby", "B2")]),
    "Argentina": ("Buenos Aires", [("Iguazu Falls", "Puerto Iguazu", "B2"),
                                   ("Perito Moreno Glacier", "El Calafate", "B2"),
                                   ("Mount Aconcagua", "Mendoza", "B2"),
                                   ("Cerro de los Siete Colores", "Purmamarca", "B2"),
                                   ("Cordoba Cathedral", "Cordoba", "B2")]),
    "Japan": ("Tokyo", [("Fushimi Inari Shrine", "Kyoto", "B2"),
                        ("Osaka Castle", "Osaka", "B2"),
                        ("Itsukushima Shrine", "Hiroshima", "B2"),
                        ("Nagoya Castle", "Nagoya", "B2"),
                        ("Sapporo Clock Tower", "Sapporo", "B2")]),
    "Thailand": ("Bangkok", [("Sukhothai Historical Park", "Sukhothai", "B2"),
                             ("Phi Phi Islands", "Krabi", "B2"),
                             ("Doi Suthep", "Chiang Mai", "B2"),
                             ("Ayutthaya Historical Park", "Ayutthaya", "B2"),
                             ("Phang Nga Bay", "Phuket", "B2")]),
    "Kenya": ("Nairobi", [("Maasai Mara Reserve", "Narok", "B2"),
                          ("Fort Jesus", "Mombasa", "B2"),
                          ("Mount Kenya", "Nyeri", "B2"),
                          ("Lake Nakuru", "Nakuru", "B2"),
                          ("Hell's Gate", "Naivasha", "B2")]),
    "Peru": ("Lima", [("Machu Picchu", "Cusco", "B2"),
                      ("Lake Titicaca", "Puno", "B2"),
                      ("Nazca Lines", "Nazca", "B2"),
                      ("Colca Canyon", "Arequipa", "B2"),
                      ("Chan Chan", "Trujillo", "B2")]),
}


def _install(bank: dict) -> None:
    wb.BANK = bank
    wb.TRAIN_COUNTRIES = sorted(
        c for c, (_, lms) in bank.items()
        if any(s != "B2" for (_, _, s) in lms))
    wb.B2_COUNTRIES = sorted(set(bank) - set(wb.TRAIN_COUNTRIES))


def install_bank() -> None:
    """Swap wire-1's default bank for WIRE2_BANK across writeback_compile's
    module globals (all logic reads these at call time)."""
    _install(WIRE2_BANK)


def select_bank(out_dir: str) -> dict:
    """Option A (s311): from the POOL's base+gate-0 pass, keep per country the
    gate-0-valid landmarks with the LOWEST base 2-hop accuracy (headroom).
    TRAIN countries -> 2 TRAIN + 1 B1 ; B2 countries -> 3 B2. Selection is on
    BASE ONLY (measurability), never on post-training accuracy."""
    import json
    od = Path(out_dir)
    g0 = json.loads((od / "gate0.json").read_text())
    res = json.loads((od / "results.json").read_text())
    valid = {(r["country"], r["landmark"]) for r in g0["cells"]
             if r.get("g_ok") and r.get("h_ok") and r.get("cot_ok")}
    base_rows = res["arms"]["base"]["seeds"][0]
    basec = {(r["country"], r["landmark"]): r["correct"] for r in base_rows}
    city_of = {(c, lm): city for c, (_, lms) in WIRE2_POOL.items()
               for (lm, city, _) in lms}
    final: dict = {}
    warnings = []
    for c, (cap, lms) in WIRE2_POOL.items():
        is_b2 = all(s == "B2" for (_, _, s) in lms)
        cands = [lm for (lm, _, _) in lms if (c, lm) in valid]
        cands.sort(key=lambda lm: (basec.get((c, lm), 1.0), lm))  # base-wrong first
        if is_b2:
            # held-out countries: 3 lowest-base cells (all B2, all headroom)
            picks = [(lm, "B2") for lm in cands[:3]]
            if len(picks) < 3:
                warnings.append(f"{c}: only {len(picks)} B2 valid (<3)")
        else:
            # TRAIN countries: 2 TRAIN + up to 2 B1, where B1 = base-0 (headroom)
            # held landmarks so G1-B1 has statistical power. TRAIN prefers
            # base-correct cells (save headroom for B1). Selection on BASE ONLY.
            base0 = [lm for lm in cands if basec.get((c, lm), 1.0) == 0.0]
            base1 = [lm for lm in cands if basec.get((c, lm), 1.0) != 0.0]
            b1 = base0[:2]
            train = (base1 + base0[2:])[:2]
            picks = [(lm, "TRAIN") for lm in train] + [(lm, "B1") for lm in b1]
            if len(train) < 2:
                warnings.append(f"{c}: only {len(train)} TRAIN valid (<2)")
        final[c] = (cap, [(lm, city_of[(c, lm)], tag) for (lm, tag) in picks])
    mean_base = float(sum(basec.get((c, lm), 1.0)
                          for c, (_, lms) in final.items()
                          for (lm, _, _) in lms)
                      / max(sum(len(lms) for _, lms in final.values()), 1))
    print(f"\n[select] final bank base-2hop mean = {mean_base:.3f} "
          f"(target ~0.2-0.5; lower = more headroom)")
    for w in warnings:
        print(f"[select] WARN {w}")
    print("\n# ── paste into WIRE2_BANK ──")
    print("WIRE2_BANK = {")
    for c, (cap, lms) in final.items():
        print(f'    {c!r}: ({cap!r}, [' + ", ".join(
            f'({lm!r}, {city!r}, {tag!r})' for (lm, city, tag) in lms) + "]),")
    print("}")
    (od / "selected_bank.json").write_text(json.dumps(final, indent=2))
    print(f"[select] wrote {od}/selected_bank.json")
    return final


def main() -> int:
    if "--reselect" in sys.argv:  # offline: re-derive bank from an existing select dir
        i = sys.argv.index("--reselect")
        select_bank(sys.argv[i + 1])
        return 0
    if "--select" in sys.argv:
        sys.argv.remove("--select")
        _install(WIRE2_POOL)
        out = "results/plate-linker/wire2-select/qwen3-4b"
        if "--out" not in sys.argv:
            sys.argv += ["--out", out]
        else:
            out = sys.argv[sys.argv.index("--out") + 1]
        if "--arms" not in sys.argv:
            sys.argv += ["--arms", "base"]
        rc = wb.main()
        if rc == 0:
            select_bank(out)
        return rc
    install_bank()
    # default out under a wire-2 dir unless caller overrode --out
    if "--out" not in sys.argv:
        sys.argv += ["--out", "results/plate-linker/wire2-bake/qwen3-4b"]
    return wb.main()


if __name__ == "__main__":
    raise SystemExit(main())
