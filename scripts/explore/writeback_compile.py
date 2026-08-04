#!/usr/bin/env python3
"""§P-WRITEBACK-1 rung 3b — BACKPROP-COMPILE: internalize the pin.

Pre-reg: mementum/knowledge/explore/program-plates-and-the-function-index.md
§P-WRITEBACK-1 (FROZEN s302, Michael-approved). The splice-exhaustion table
(s295) fixed the target by elimination: the 0.20→0.90 gap is the WRITEBACK —
only the generation path can produce, commit, and re-encode the hop-2
intermediate. This instrument tests whether that capability can be compiled
into a small persistent WEIGHT delta, as a WIRE (generalizes to held-out
landmarks AND held-out countries) and not a LOOKUP (materialized g∘h view).

Chain (shortcut-free): landmark --g(country-of)--> country
--h(capital-of)--> capital, landmark's own city != capital.

Splits: TRAIN (8 countries x 2 landmarks) / B1 held-landmark (new landmarks
of TRAIN countries) / B2 held-COUNTRY (all landmarks of 8 never-trained
countries — the sharp wire gate).

Arms (all evaluated on the ONE-SHOT direct prompt, greedy first-token argmax
over the union candidate set; margins + generations advisory):
  base             : untouched host (floor).
  construct        : zero-gradient — appended FFN neurons at the install
                     layer: key = whitened country-class filter (shared-Sigma,
                     prompt-shaped innocents law), value = capital unembed
                     direction, gain closed-loop calibrated on COUNTRY frames
                     (never sees a landmark->capital pair).
  construct_shuffle: same keys, deranged capital values (specificity null).
  construct_lookup : landmark-keyed neurons writing the capital directly,
                     TRAIN pairs only (the materialized-view null — must
                     fail B2 by construction).
  gd_cd            : backprop-compile proper — LoRA r=16 FFN-only on the
                     0.6-0.8 band; teacher = SAME host on its own committed
                     CoT ("The {lm} is located in {c}. The capital of {c}
                     is"), student = one-shot prompt; KL at answer position.
  gd_sft           : matched-budget direct answer CE (no tape).
  gd_shuffle       : gd_cd with deranged countries in the teacher CoT.

Gates (verbum.dsp, paired permutation 10k; primaries G1-G3 Bonferroni
alpha/3; G1-G3 routing register, G4/G5 value register):
  G1 WIRE       : arm > base acc with flip on B1 AND B2.
  G2 NOT-LOOKUP : arm > construct_lookup acc on B2.
  G3 SPECIFICITY: arm > its shuffle null on held-out (B1 + B2).
  G4 PIN        : whitened country readout at install layer rises on
                  held-out one-shot prompts + separates correct/incorrect
                  (mechanism clause; reported, never gates alone).
  G5 SURVIVE    : innocent-text CE within 2% rel of base; native g/h accs
                  within 0.10 absolute.
Verdicts: WIRE-COMPILES(+CONSTRUCTION-SUFFICES/+GD-REQUIRED/+BOTH) /
LOOKUP-ONLY / UNSPECIFIC / HOST-DAMAGED / STILL-EXTERNAL.

Cadence: --validate (no model) → gate-0 sweep @4B (commit cell list) →
Michael GO → arms (tmux main:1) → frozen scoring. 32B: construct arms only
(--arms base,construct,construct_shuffle,construct_lookup), advisory.

License: MIT (`λ provenance`).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_WRAP = _HERE.parents[1] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

from bake_stack import CC_FRAMES, PROSE_INNOCENTS, whitened_filter  # noqa: E402
from fn_stack import CAP_PREFIX, CAP_QUERY  # noqa: E402
from holo_cap import NONCE_CANDS  # noqa: E402
from holo_frag import _json_safe  # noqa: E402
from native_compose_check import contains  # noqa: E402

from verbum.dsp import gate, paired_permutation  # noqa: E402

# ══════════════════════════════════════════════════════════════════════════
# Bank (frozen with the pre-reg; gate-0 filters cells the host fails)
# country -> (capital, [(landmark, city, split), ...])
# TRAIN countries carry 2xTRAIN + 1xB1 landmarks; B2 countries carry 3xB2.
# Shortcut-free: every landmark city != its country's capital.
# ══════════════════════════════════════════════════════════════════════════
BANK = {
    # ── TRAIN countries ──
    "Spain": ("Madrid", [("Sagrada Familia", "Barcelona", "TRAIN"),
                         ("Alhambra", "Granada", "TRAIN"),
                         ("Park Guell", "Barcelona", "B1")]),
    "India": ("New Delhi", [("Taj Mahal", "Agra", "TRAIN"),
                            ("Charminar", "Hyderabad", "TRAIN"),
                            ("Mysore Palace", "Mysore", "B1")]),
    "Egypt": ("Cairo", [("Karnak Temple", "Luxor", "TRAIN"),
                        ("Abu Simbel", "Aswan", "TRAIN"),
                        ("Valley of the Kings", "Luxor", "B1")]),
    "UAE": ("Abu Dhabi", [("Burj Khalifa", "Dubai", "TRAIN"),
                          ("Palm Jumeirah", "Dubai", "TRAIN"),
                          ("Burj Al Arab", "Dubai", "B1")]),
    "Morocco": ("Rabat", [("Koutoubia Mosque", "Marrakech", "TRAIN"),
                          ("Hassan II Mosque", "Casablanca", "TRAIN"),
                          ("Jemaa el-Fnaa", "Marrakech", "B1")]),
    "Italy": ("Rome", [("Leaning Tower of Pisa", "Pisa", "TRAIN"),
                       ("Rialto Bridge", "Venice", "TRAIN"),
                       ("Duomo di Milano", "Milan", "B1")]),
    "Brazil": ("Brasilia", [("Christ the Redeemer", "Rio de Janeiro", "TRAIN"),
                            ("Sugarloaf Mountain", "Rio de Janeiro", "TRAIN"),
                            ("Copacabana Beach", "Rio de Janeiro", "B1")]),
    "Turkey": ("Ankara", [("Hagia Sophia", "Istanbul", "TRAIN"),
                          ("Blue Mosque", "Istanbul", "TRAIN"),
                          ("Galata Tower", "Istanbul", "B1")]),
    # ── B2 held-out countries (never in any delta's construction) ──
    "France": ("Paris", [("Mont Saint-Michel", "Avranches", "B2"),
                         ("Palace of Versailles", "Versailles", "B2"),
                         ("Pont du Gard", "Nimes", "B2")]),
    "Germany": ("Berlin", [("Neuschwanstein Castle", "Fussen", "B2"),
                           ("Cologne Cathedral", "Cologne", "B2"),
                           ("Heidelberg Castle", "Heidelberg", "B2")]),
    "Canada": ("Ottawa", [("CN Tower", "Toronto", "B2"),
                          ("Stanley Park", "Vancouver", "B2"),
                          ("Mount Royal", "Montreal", "B2")]),
    "Australia": ("Canberra", [("Sydney Opera House", "Sydney", "B2"),
                               ("Bondi Beach", "Sydney", "B2"),
                               ("Federation Square", "Melbourne", "B2")]),
    "Switzerland": ("Bern", [("Matterhorn", "Zermatt", "B2"),
                             ("Chapel Bridge", "Lucerne", "B2"),
                             ("Jet d'Eau", "Geneva", "B2")]),
    "Poland": ("Warsaw", [("Wawel Castle", "Krakow", "B2"),
                          ("St. Mary's Basilica", "Krakow", "B2"),
                          ("Malbork Castle", "Malbork", "B2")]),
    "Vietnam": ("Hanoi", [("Cu Chi Tunnels", "Ho Chi Minh City", "B2"),
                          ("Ben Thanh Market", "Ho Chi Minh City", "B2"),
                          ("Golden Bridge", "Da Nang", "B2")]),
    "China": ("Beijing", [("Terracotta Army", "Xian", "B2"),
                          ("The Bund", "Shanghai", "B2"),
                          ("West Lake", "Hangzhou", "B2")]),
}
TRAIN_COUNTRIES = sorted(c for c, (_, lms) in BANK.items()
                         if any(s != "B2" for (_, _, s) in lms))
B2_COUNTRIES = sorted(set(BANK) - set(TRAIN_COUNTRIES))
SPLITS = ("TRAIN", "B1", "B2")
MIN_PER_SPLIT = 8          # frozen: below this → UNDERPOWERED-VOID
HOST_COT_FLOOR = 0.7       # frozen: pooled CoT-composed host-competence gate

# one-shot prompt (native_compose_check `direct`, verbatim — reuse, no fork)
DIRECT_PROMPT = ("The {lm} is a famous landmark. The capital of the "
                 "country where it is located is")
# committed-CoT teacher (native_compose_check `scaffold` form; the model's
# own gate-0-committed country fills {c} — own-state ≡ committed text under
# greedy, the P-KV-1c reduction)
TEACHER_PROMPT = "The {lm} is located in {c}. The capital of {c} is"
COT_PROMPT = ("Question: What is the capital of the country where the {lm} "
              "is located?\nAnswer: Let's reason step by step.")
G_QUERY_PREFIX = (
    "The Eiffel Tower is located in the country of France.\n"
    "The Great Wall is located in the country of China.\n"
    "The Serengeti is located in the country of Tanzania.\n")
G_QUERY = "The {lm} is located in the country of"

# G5 fixed innocent CE set (frozen)
CE_TEXTS = [*PROSE_INNOCENTS,
    "The orchestra tuned their instruments before the performance",
    "A light breeze moved the curtains in the study",
    "The bakery sold out of bread before noon",
    "Two chess players studied the board in silence",
    "The garden needed water after the long dry spell",
    "An old map hung framed above the fireplace"]

# construct-arm calibration (frozen): mean capital-logit boost target on
# COUNTRY frames (pair-free closed loop; 2 linear iterations, clamped)
DELTA_TARGET = 3.0
GAIN_CLAMP = (0.01, 2.0)
BAND = (0.60, 0.80)        # LoRA band, fractional depth (frozen recipe)
INSTALL_DEPTH = 0.65       # construct install / detector layer


@dataclass(frozen=True)
class Cell:
    landmark: str
    city: str
    country: str
    capital: str
    split: str


def all_cells() -> list[Cell]:
    out = []
    for c, (cap, lms) in BANK.items():
        for (lm, city, split) in lms:
            out.append(Cell(lm, city, c, cap, split))
    return out


def first_word(s: str) -> str:
    return s.split()[0] if s else s


def union_words() -> list[str]:
    caps = {cap for cap, _ in BANK.values()}
    countries = set(BANK)
    cities = {city for _, lms in BANK.values() for (_, city, _) in lms}
    return sorted(caps | countries | cities)


def derangement(items: list[str], rng: np.random.Generator) -> dict[str, str]:
    """Permutation with no fixed point."""
    n = len(items)
    while True:
        p = rng.permutation(n)
        if not np.any(p == np.arange(n)):
            return {items[i]: items[p[i]] for i in range(n)}


# ══════════════════════════════════════════════════════════════════════════
# Frozen scoring + verdict (pure; --validate exercises planted worlds)
# ══════════════════════════════════════════════════════════════════════════
def _g(a: np.ndarray, b: np.ndarray, rng, alpha: float, name: str):
    return gate(float(np.mean(np.asarray(a) - np.asarray(b))),
                paired_permutation(np.asarray(a), np.asarray(b), rng),
                "greater", alpha, name=name)


def score_arms(acc: dict[str, dict[str, np.ndarray]], ce: dict[str, float],
               gh: dict[str, tuple[float, float]], rng: np.random.Generator,
               alpha: float) -> dict:
    """acc[arm][split] = per-cell mean-over-seed correctness (aligned order);
    ce[arm] = innocent CE; gh[arm] = (g_acc, h_acc). Returns frozen gates."""
    a3 = alpha / 3.0
    shuffle_of = {"construct": "construct_shuffle", "gd_cd": "gd_shuffle"}
    out = {}
    for arm in ("construct", "gd_cd"):
        if arm not in acc:
            continue
        r = {}
        g1 = {}
        for sp in ("B1", "B2"):
            gg = _g(acc[arm][sp], acc["base"][sp], rng, a3, f"{arm}-G1-{sp}")
            g1[sp] = {"gate": gg, "flip": bool(acc[arm][sp].mean()
                                               > acc["base"][sp].mean())}
        r["G1"] = bool(all(g1[sp]["gate"].verdict and g1[sp]["flip"]
                           for sp in ("B1", "B2")))
        r["G1_detail"] = g1
        g2 = _g(acc[arm]["B2"], acc["construct_lookup"]["B2"], rng, a3,
                f"{arm}-G2-B2")
        r["G2"] = bool(g2.verdict)
        r["G2_detail"] = g2
        held_arm = np.concatenate([acc[arm]["B1"], acc[arm]["B2"]])
        sh = shuffle_of[arm]
        held_sh = np.concatenate([acc[sh]["B1"], acc[sh]["B2"]])
        g3 = _g(held_arm, held_sh, rng, a3, f"{arm}-G3-heldout")
        r["G3"] = bool(g3.verdict)
        r["G3_detail"] = g3
        ce_ok = ce[arm] <= ce["base"] * 1.02
        g_ok = gh[arm][0] >= gh["base"][0] - 0.10
        h_ok = gh[arm][1] >= gh["base"][1] - 0.10
        r["G5"] = bool(ce_ok and g_ok and h_ok)
        r["G5_detail"] = {"ce": ce[arm], "ce_base": ce["base"],
                          "g_acc": gh[arm][0], "h_acc": gh[arm][1]}
        tr = _g(acc[arm]["TRAIN"], acc["base"]["TRAIN"], rng, alpha,
                f"{arm}-train")
        r["train_up"] = bool(tr.verdict and acc[arm]["TRAIN"].mean()
                             > acc["base"]["TRAIN"].mean())
        r["held_up"] = bool(held_arm.mean()
                            > np.concatenate([acc["base"]["B1"],
                                              acc["base"]["B2"]]).mean())
        out[arm] = r
    # the lookup null's own signature (must fail B2 for the design to hold)
    lk = _g(acc["construct_lookup"]["B2"], acc["base"]["B2"], rng, alpha,
            "lookup-B2")
    out["lookup_b2_moves"] = bool(lk.verdict)
    return out


def verdict_of(gate0_ok: bool, sc: dict) -> str:
    if not gate0_ok:
        return "VOID (gate-0)"
    arms = {a: r for a, r in sc.items() if isinstance(r, dict)}
    if sc.get("lookup_b2_moves"):
        return "VOID (lookup null moves B2 — task has a shortcut)"
    live = {a: r for a, r in arms.items() if r["G5"]}
    if not live:
        return "HOST-DAMAGED"
    passing = [a for a, r in live.items() if r["G1"] and r["G2"] and r["G3"]]
    if passing:
        if "construct" in passing and "gd_cd" in passing:
            return "WIRE-COMPILES (+BOTH)"
        if "construct" in passing:
            return "WIRE-COMPILES (+CONSTRUCTION-SUFFICES)"
        return "WIRE-COMPILES (+GD-REQUIRED)"
    if any(r["G1"] and r["G2"] and not r["G3"] for r in live.values()):
        return "UNSPECIFIC"
    if not any(r["held_up"] for r in live.values()):
        if any(r["train_up"] for r in live.values()):
            return "LOOKUP-ONLY"
        return "STILL-EXTERNAL"
    if any(r["train_up"] and not (r["G1"] and r["G2"]) for r in live.values()):
        return "LOOKUP-ONLY"
    return "inconclusive (held-out moves without clearing gates)"


# ══════════════════════════════════════════════════════════════════════════
# --validate (no model)
# ══════════════════════════════════════════════════════════════════════════
def _acc_world(rng, base, cons, cons_sh, lookup, gd, gd_sh, n=12):
    """Planted per-split correctness with mild noise; dict for score_arms."""
    def arr(p):
        return (rng.random(n) < p).astype(float)
    def sp(pt, p1, p2):
        return {"TRAIN": arr(pt), "B1": arr(p1), "B2": arr(p2)}
    return {"base": sp(*base), "construct": sp(*cons),
            "construct_shuffle": sp(*cons_sh),
            "construct_lookup": sp(*lookup), "gd_cd": sp(*gd),
            "gd_shuffle": sp(*gd_sh)}


def run_validate(alpha: float) -> int:
    ok = True
    print("── §P-WRITEBACK-1 --validate (no model) ──")

    # 1. bank integrity
    cells = all_cells()
    ns = {sp: sum(1 for c in cells if c.split == sp) for sp in SPLITS}
    sf = all(c.city != c.capital for c in cells)
    b2_iso = all(c.split == "B2" for c in cells if c.country in B2_COUNTRIES)
    fw = [first_word(w) for w in union_words()]
    uniq = len(fw) == len(set(fw))
    good = (ns["TRAIN"] >= MIN_PER_SPLIT and ns["B1"] >= MIN_PER_SPLIT
            and ns["B2"] >= MIN_PER_SPLIT and sf and b2_iso and uniq)
    print(f"[V] bank: {ns} shortcut_free={sf} b2_isolated={b2_iso} "
          f"first_word_unique={uniq} {'OK' if good else 'FAIL'}")
    ok &= good

    # 2. derangement
    rng = np.random.default_rng(0)
    d = derangement(sorted(BANK), rng)
    good = all(k != v for k, v in d.items()) and set(d.values()) == set(BANK)
    print(f"[V] derangement: no fixed points {'OK' if good else 'FAIL'}")
    ok &= good

    # 3. whitened filter planted separation
    rng2 = np.random.default_rng(1)
    dim = 64
    axis = rng2.normal(size=dim)
    axis /= np.linalg.norm(axis)
    frame = rng2.normal(size=dim)
    own = frame + 3.0 * axis + rng2.normal(0, 0.3, (6, dim))
    inn = frame + rng2.normal(0, 0.3, (8, dim))
    _k, _mu, theta, ref = whitened_filter(own, inn, 0.1)
    good = ref > theta
    print(f"[V] whitened filter: ref {ref:.2f} > theta {theta:.2f} "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 4. neuron surgery equivalence (tiny SwiGLU block)
    import torch
    import torch.nn.functional as F
    torch.manual_seed(0)
    dm, ff = 16, 32
    gp = torch.nn.Linear(dm, ff, bias=False)
    up = torch.nn.Linear(dm, ff, bias=False)
    dn = torch.nn.Linear(ff, dm, bias=False)
    def mlp(x):
        return dn(F.silu(gp(x)) * up(x))
    key = torch.randn(dm)
    key /= key.norm()
    val = torch.randn(dm)
    sg, su = 4.0, 1.0
    x_on = 2.0 * key + 0.01 * torch.randn(dm)
    x_off = x_on - (x_on @ key) * key      # orthogonal to key
    base_on, base_off = mlp(x_on), mlp(x_off)
    with torch.no_grad():
        gp.weight = torch.nn.Parameter(
            torch.cat([gp.weight, (sg * key)[None, :]]))
        up.weight = torch.nn.Parameter(
            torch.cat([up.weight, (su * key)[None, :]]))
        dn.weight = torch.nn.Parameter(
            torch.cat([dn.weight, val[:, None]], dim=1))
    r = float(x_on @ key)
    want = base_on + F.silu(torch.tensor(sg * r)) * (su * r) * val
    with torch.no_grad():
        e_on = float((mlp(x_on) - want).abs().max())
        e_off = float((mlp(x_off) - base_off).abs().max())
    good = e_on < 1e-4 and e_off < 1e-4
    print(f"[V] surgery: on-err {e_on:.2e} off-err {e_off:.2e} "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 5. LoRA identity at init + grad isolation
    lin = torch.nn.Linear(dm, dm, bias=False)
    lo = LoRALinear(lin, r=4, alpha=8)
    x = torch.randn(3, dm)
    with torch.no_grad():
        ident = float((lo(x) - lin(x)).abs().max())
    lo(x).sum().backward()
    grads = [p.grad is not None for p in (lo.A, lo.B)]
    frozen = lin.weight.grad is None
    good = ident < 1e-6 and all(grads) and frozen
    print(f"[V] lora: init-identity {ident:.1e} grads(A,B)={grads} "
          f"base-frozen={frozen} {'OK' if good else 'FAIL'}")
    ok &= good

    # 6. verdict logic planted worlds
    rngw = np.random.default_rng(2)
    def world(name, want, base, cons, cons_sh, lookup, gd, gd_sh,
              ce_bad=(), gh_bad=()):
        acc = _acc_world(rngw, base, cons, cons_sh, lookup, gd, gd_sh, n=14)
        arms = list(acc)
        ce = {a: (1.10 if a in ce_bad else 1.0) for a in arms}
        gh = {a: ((0.5, 0.5) if a in gh_bad else (0.95, 0.95)) for a in arms}
        sc = score_arms(acc, ce, gh, np.random.default_rng(3), alpha)
        v = verdict_of(True, sc)
        hit = want in v
        print(f"[V] {name}-world -> {v} (want {want}) {'OK' if hit else 'FAIL'}")
        return hit
    # (TRAIN, B1, B2) success probabilities per arm
    ok &= world("wire-both", "+BOTH",
                base=(.15, .15, .15), cons=(.9, .9, .85), cons_sh=(.15, .15, .15),
                lookup=(.95, .15, .15), gd=(.9, .85, .85), gd_sh=(.2, .15, .15))
    ok &= world("construction", "+CONSTRUCTION-SUFFICES",
                base=(.15, .15, .15), cons=(.9, .9, .85), cons_sh=(.15, .15, .15),
                lookup=(.95, .15, .15), gd=(.2, .15, .15), gd_sh=(.15, .15, .15))
    ok &= world("lookup-only", "LOOKUP-ONLY",
                base=(.15, .15, .15), cons=(.9, .2, .15), cons_sh=(.15, .15, .15),
                lookup=(.95, .15, .15), gd=(.9, .15, .15), gd_sh=(.15, .15, .15))
    ok &= world("still-external", "STILL-EXTERNAL",
                base=(.15, .15, .15), cons=(.15, .15, .15), cons_sh=(.15, .15, .15),
                lookup=(.2, .15, .15), gd=(.15, .15, .15), gd_sh=(.15, .15, .15))
    ok &= world("unspecific", "UNSPECIFIC",
                base=(.15, .15, .15), cons=(.9, .9, .85), cons_sh=(.85, .85, .8),
                lookup=(.95, .15, .15), gd=(.2, .2, .2), gd_sh=(.2, .2, .2))
    ok &= world("host-damaged", "HOST-DAMAGED",
                base=(.15, .15, .15), cons=(.9, .9, .85), cons_sh=(.15, .15, .15),
                lookup=(.95, .15, .15), gd=(.9, .85, .85), gd_sh=(.2, .15, .15),
                ce_bad=("construct", "gd_cd"))
    ok &= world("shortcut-void", "VOID (lookup",
                base=(.15, .15, .15), cons=(.9, .9, .85), cons_sh=(.15, .15, .15),
                lookup=(.95, .9, .9), gd=(.9, .85, .85), gd_sh=(.2, .15, .15))

    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# LoRA (manual, torch; FFN-only per frozen recipe)
# ══════════════════════════════════════════════════════════════════════════
try:
    import torch as _torch

    class LoRALinear(_torch.nn.Module):
        def __init__(self, base: _torch.nn.Module, r: int, alpha: float):
            super().__init__()
            self.base = base
            for p in self.base.parameters():
                p.requires_grad_(False)
            din = base.in_features
            dout = base.out_features
            dev = base.weight.device
            self.A = _torch.nn.Parameter(
                _torch.randn(r, din, device=dev, dtype=_torch.float32) * 0.01)
            self.B = _torch.nn.Parameter(
                _torch.zeros(dout, r, device=dev, dtype=_torch.float32))
            self.scale = alpha / r

        def forward(self, x):
            y = self.base(x)
            lo = (x.to(self.A.dtype) @ self.A.T) @ self.B.T
            return y + (self.scale * lo).to(y.dtype)
except Exception:                                     # pragma: no cover
    LoRALinear = None  # type: ignore[assignment]


# ══════════════════════════════════════════════════════════════════════════
# Model path
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import operand_multihop3 as mh3
    import torch
    import torch.nn.functional as F
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps"
                           or torch.backends.mps.is_available()) else "cpu")
    rng = np.random.default_rng(args.seed)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    dec, _norm, lm_head = mh3.resolve_parts(model)
    n_layers = len(dec)
    li_star = round(INSTALL_DEPTH * n_layers)
    band = list(range(round(BAND[0] * n_layers), round(BAND[1] * n_layers) + 1))
    cells = all_cells()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[wb] {args.model_id} dev={dev} n_layers={n_layers} "
          f"install=L{li_star} band=L{band[0]}..L{band[-1]} "
          f"arms={args.arms} seeds={args.seeds} steps={args.steps}")

    def first_tid(w: str) -> int:
        return mh3.first_tid(tok, w)

    # ── union candidate set (capitals + countries + cities), clash-dropped ──
    tid_map, drop = {}, set()
    for w in union_words():
        t = first_tid(w)
        clash = [x for x, tt in tid_map.items() if tt == t]
        if clash:
            drop.add(w)
            drop.update(clash)
        tid_map[w] = t
    union = {w: tid_map[w] for w in sorted(set(union_words()) - drop)}
    print(f"[wb] union candidates: {len(union)} dropped: {sorted(drop)}")

    def logits_last(prompt: str) -> np.ndarray:
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        return lo

    def argmax_union(lo: np.ndarray) -> str:
        return max(union, key=lambda w: lo[union[w]])

    def margin(lo: np.ndarray, truth: str) -> float:
        others = [lo[union[w]] for w in union if w != truth]
        return float(lo[union[truth]] - max(others))

    def gen(prompt: str, n: int) -> str:
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            o = model.generate(**ids, max_new_tokens=n, do_sample=False,
                               pad_token_id=tok.eos_token_id)
        return tok.decode(o[0, ids.input_ids.shape[1]:],
                          skip_special_tokens=True)

    # ══ gate-0: per-cell native ceilings + host competence ══
    print("[wb] gate-0 sweep…")
    countries = sorted(BANK)
    caps = sorted({cap for cap, _ in BANK.values()})
    valid, g0_rows, cot_hits = [], [], 0
    for c in cells:
        if c.capital in drop or c.country in drop:
            g0_rows.append({**asdict(c), "excluded": "union-clash"})
            continue
        g_pred = max(countries, key=lambda w: logits_last(
            G_QUERY_PREFIX + G_QUERY.format(lm=c.landmark))[first_tid(w)])
        h_pred = max(caps, key=lambda w: logits_last(
            CAP_PREFIX + CAP_QUERY.format(x=c.country))[first_tid(w)])
        cot_g = gen(COT_PROMPT.format(lm=c.landmark), 80)
        g_ok = g_pred == c.country
        h_ok = first_word(h_pred) == first_word(c.capital)
        cot_ok = contains(cot_g, c.capital)
        row = {**asdict(c), "g_ok": g_ok, "h_ok": h_ok, "cot_ok": cot_ok,
               "g_pred": g_pred, "h_pred": h_pred, "cot_gen": cot_g}
        g0_rows.append(row)
        if g_ok and h_ok:
            cot_hits += int(cot_ok)
        if g_ok and h_ok and cot_ok:
            valid.append(c)
    ns = {sp: sum(1 for c in valid if c.split == sp) for sp in SPLITS}
    n_gh = sum(1 for r in g0_rows if r.get("g_ok") and r.get("h_ok"))
    cot_rate = cot_hits / max(n_gh, 1)
    gate0_ok = (all(ns[sp] >= MIN_PER_SPLIT for sp in SPLITS)
                and cot_rate >= HOST_COT_FLOOR)
    print(f"[wb] gate-0: valid {len(valid)}/{len(cells)} splits={ns} "
          f"cot_rate={cot_rate:.2f} -> {'PASS' if gate0_ok else 'FAIL'}")
    (out_dir / "gate0.json").write_text(json.dumps(_json_safe(
        {"model_id": args.model_id, "splits": ns, "cot_rate": cot_rate,
         "gate0_ok": gate0_ok, "union_dropped": sorted(drop),
         "cells": g0_rows}), indent=2))
    print(f"[wb] wrote {out_dir}/gate0.json")
    if args.gate0_only:
        return 0 if gate0_ok else 1
    if not gate0_ok and not args.force:
        print("[wb] gate-0 FAIL — stopping (use --force to override)")
        return 1

    if args.n_cells:                       # smoke cap (mechanics only)
        by = {sp: [c for c in valid if c.split == sp] for sp in SPLITS}
        valid = [c for sp in SPLITS for c in by[sp][:args.n_cells]]
        print(f"[wb] SMOKE cap {args.n_cells}/split -> {len(valid)} cells")

    train_cells = [c for c in valid if c.split == "TRAIN"]

    # ══ shared captures: post-norm MLP input at install layer ══
    def capture_postnorm(prompts: list[str]) -> np.ndarray:
        vecs = []
        for p in prompts:
            store = {}
            hnd = dec[li_star].post_attention_layernorm.register_forward_hook(
                lambda m, i, o, s=store: s.__setitem__("v", o))
            ids = tok(p, return_tensors="pt").to(dev)
            with torch.no_grad():
                model(**ids)
            hnd.remove()
            vecs.append(store["v"][0, -1, :].float().cpu().numpy())
        return np.stack(vecs)

    # whitened country keys: shared Sigma over ALL countries' frames +
    # prompt-shaped innocents (s295 law)
    def build_keys(specs: dict[str, list[str]]) -> dict:
        inn_prompts = list(PROSE_INNOCENTS) + [
            DIRECT_PROMPT.format(lm=nc) for nc in NONCE_CANDS[:3]]
        inn = capture_postnorm(inn_prompts)
        owns = {name: capture_postnorm(ps) for name, ps in specs.items()}
        pop = np.vstack([*owns.values(), inn])
        mu = pop.mean(axis=0)
        xc = pop - mu
        cov = (xc.T @ xc) / max(len(pop) - 1, 1)
        d = cov.shape[0]
        cov += args.whiten_eps * (np.trace(cov) / d) * np.eye(d)
        keys = {}
        seps = []
        for name, own in owns.items():
            k = np.linalg.solve(cov, own.mean(axis=0) - mu)
            k = k / (np.linalg.norm(k) + 1e-9)
            r_own = float(np.mean(own @ k))
            r_inn = float(np.max(inn @ k))
            keys[name] = {"k": k, "ref": r_own, "inn_max": r_inn}
            seps.append(r_own - r_inn)
        print(f"[wb] keys({len(keys)}): raw own-inn separation "
              f"min {min(seps):.2f} median {float(np.median(seps)):.2f}")
        return keys

    # ══ construct arms: real weight surgery (appended SwiGLU neurons) ══
    mlp = dec[li_star].mlp
    ff_orig = mlp.gate_proj.weight.shape[0]

    def unembed_dir(word: str) -> np.ndarray:
        v = lm_head.weight[first_tid(word)].float().cpu().numpy()
        return v / (np.linalg.norm(v) + 1e-9)

    def append_neurons(neurons: list[tuple[np.ndarray, float, np.ndarray]]):
        """neurons: (key_unit, ref, value_vec). gate=4/ref*k, up=1/ref*k."""
        wd = mlp.gate_proj.weight.dtype
        g_rows = torch.stack([torch.tensor((4.0 / ref) * k, dtype=wd)
                              for (k, ref, _) in neurons]).to(dev)
        u_rows = torch.stack([torch.tensor((1.0 / ref) * k, dtype=wd)
                              for (k, ref, _) in neurons]).to(dev)
        d_cols = torch.stack([torch.tensor(v, dtype=wd)
                              for (_, _, v) in neurons], dim=1).to(dev)
        with torch.no_grad():
            mlp.gate_proj.weight = torch.nn.Parameter(
                torch.cat([mlp.gate_proj.weight[:ff_orig], g_rows]),
                requires_grad=False)
            mlp.up_proj.weight = torch.nn.Parameter(
                torch.cat([mlp.up_proj.weight[:ff_orig], u_rows]),
                requires_grad=False)
            mlp.down_proj.weight = torch.nn.Parameter(
                torch.cat([mlp.down_proj.weight[:, :ff_orig], d_cols], dim=1),
                requires_grad=False)
        mlp.gate_proj.out_features = ff_orig + len(neurons)
        mlp.up_proj.out_features = ff_orig + len(neurons)
        mlp.down_proj.in_features = ff_orig + len(neurons)

    def restore_neurons():
        with torch.no_grad():
            mlp.gate_proj.weight = torch.nn.Parameter(
                mlp.gate_proj.weight[:ff_orig].contiguous(),
                requires_grad=False)
            mlp.up_proj.weight = torch.nn.Parameter(
                mlp.up_proj.weight[:ff_orig].contiguous(),
                requires_grad=False)
            mlp.down_proj.weight = torch.nn.Parameter(
                mlp.down_proj.weight[:, :ff_orig].contiguous(),
                requires_grad=False)
        mlp.gate_proj.out_features = ff_orig
        mlp.up_proj.out_features = ff_orig
        mlp.down_proj.in_features = ff_orig

    def calibrate_gain(neuron_spec, calib_prompts_of) -> float:
        """Closed loop (pair-free): mean truth-logit boost -> DELTA_TARGET.
        Two linear iterations, clamped. neuron_spec: name -> (k, ref, vdir,
        truth_word); calib prompts mention the KEY entity only."""
        names = sorted(neuron_spec)
        def boost_at(gain: float) -> float:
            append_neurons([(neuron_spec[n][0], neuron_spec[n][1],
                             gain * neuron_spec[n][2]) for n in names])
            deltas = []
            for n in names:
                truth = neuron_spec[n][3]
                for p in calib_prompts_of(n):
                    deltas.append(logits_last(p)[first_tid(truth)])
            restore_neurons()
            base_vals = []
            for n in names:
                truth = neuron_spec[n][3]
                for p in calib_prompts_of(n):
                    base_vals.append(logits_last(p)[first_tid(truth)])
            return float(np.mean(np.array(deltas) - np.array(base_vals)))
        gain = 0.1
        for _ in range(2):
            b = boost_at(gain)
            if abs(b) < 1e-6:
                break
            gain = float(np.clip(gain * DELTA_TARGET / b, *GAIN_CLAMP))
        print(f"[wb] calibrated gain={gain:.3f} "
              f"(boost@gain={boost_at(gain):.2f}, target={DELTA_TARGET})")
        return gain

    # ══ eval (one-shot; routing register + advisory margins/gens/detector) ══
    def eval_cells(keys_for_detector) -> list[dict]:
        rows = []
        for c in valid:
            p = DIRECT_PROMPT.format(lm=c.landmark)
            lo = logits_last(p)
            arg = argmax_union(lo)
            det = np.nan
            if keys_for_detector is not None and c.country in keys_for_detector:
                v = capture_postnorm([p])[0]
                kk = keys_for_detector[c.country]
                det = float(v @ kk["k"])
            rows.append({"landmark": c.landmark, "country": c.country,
                         "split": c.split, "truth": c.capital,
                         "arg": arg,
                         "correct": float(first_word(arg)
                                          == first_word(c.capital)),
                         "margin": margin(lo, c.capital), "detector": det})
        return rows

    def ce_innocents() -> float:
        tot, n = 0.0, 0
        for t in CE_TEXTS:
            ids = tok(t, return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits
            lp = F.log_softmax(lo[0, :-1].float(), dim=-1)
            tgt = ids.input_ids[0, 1:]
            tot += float(-lp[torch.arange(len(tgt)), tgt].sum())
            n += len(tgt)
        return tot / max(n, 1)

    def gh_accs() -> tuple[float, float]:
        g_hits = [max(countries, key=lambda w: logits_last(
            G_QUERY_PREFIX + G_QUERY.format(lm=c.landmark))[first_tid(w)])
            == c.country for c in valid]
        h_hits = [first_word(max(caps, key=lambda w: logits_last(
            CAP_PREFIX + CAP_QUERY.format(x=co))[first_tid(w)]))
            == first_word(BANK[co][0]) for co in sorted(BANK)]
        return float(np.mean(g_hits)), float(np.mean(h_hits))

    # ══ GD arms ══
    def teacher_probs(country_of: dict[str, str]) -> dict[str, torch.Tensor]:
        out = {}
        for c in train_cells:
            co = country_of[c.landmark]
            lo = logits_last(TEACHER_PROMPT.format(lm=c.landmark, c=co))
            out[c.landmark] = torch.softmax(
                torch.tensor(lo, dtype=torch.float32), dim=-1)
        return out

    def train_gd(loss_kind: str, tprobs, seed: int):
        torch.manual_seed(seed)
        wrapped = []
        params = []
        for li in band:
            m = dec[li].mlp
            for name in ("gate_proj", "up_proj", "down_proj"):
                orig = getattr(m, name)
                lw = LoRALinear(orig, r=args.lora_r, alpha=2 * args.lora_r)
                setattr(m, name, lw)
                wrapped.append((m, name, orig))
                params += [lw.A, lw.B]
        opt = torch.optim.Adam(params, lr=args.lr)
        prompts = [DIRECT_PROMPT.format(lm=c.landmark) for c in train_cells]
        batch = tok(prompts, return_tensors="pt", padding=True).to(dev)
        cap_tids = torch.tensor([first_tid(c.capital) for c in train_cells],
                                device=dev)
        if tprobs is not None:
            tp = torch.stack([tprobs[c.landmark]
                              for c in train_cells]).to(dev)
        for step in range(args.steps):
            opt.zero_grad()
            lo = model(**batch).logits[:, -1, :].float()
            if loss_kind == "kl":
                loss = -(tp * F.log_softmax(lo, dim=-1)).sum(-1).mean()
            else:
                loss = F.cross_entropy(lo, cap_tids)
            loss.backward()
            opt.step()
            if step % max(args.steps // 5, 1) == 0 or step == args.steps - 1:
                print(f"    step {step:4d} loss {float(loss):.4f}")
        def unwrap():
            for m, name, orig in wrapped:
                setattr(m, name, orig)
        return unwrap

    # ══ run arms ══
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    results = {}
    country_specs = {c: [f.format(x=c) for f in CC_FRAMES] for c in sorted(BANK)}
    keys = build_keys(country_specs) if any(
        a.startswith("construct") or a == "base" for a in arms) else None

    for arm in arms:
        print(f"[wb] ── arm {arm} ──")
        if arm == "base":
            rows = eval_cells(keys)
            results[arm] = {"seeds": [rows], "ce": ce_innocents(),
                            "gh": gh_accs()}
        elif arm in ("construct", "construct_shuffle"):
            cap_of = {c: BANK[c][0] for c in sorted(BANK)}
            if arm == "construct_shuffle":
                dc = derangement(sorted(BANK), rng)
                cap_of = {c: BANK[dc[c]][0] for c in sorted(BANK)}
            spec = {c: (keys[c]["k"], keys[c]["ref"],
                        unembed_dir(cap_of[c]), cap_of[c])
                    for c in sorted(BANK)}
            gain = calibrate_gain(spec, lambda n: country_specs[n])
            append_neurons([(spec[c][0], spec[c][1], gain * spec[c][2])
                            for c in sorted(BANK)])
            rows = eval_cells(keys)
            results[arm] = {"seeds": [rows], "ce": ce_innocents(),
                            "gh": gh_accs(), "gain": gain}
            restore_neurons()
        elif arm == "construct_lookup":
            lm_specs = {c.landmark: [f.format(x=c.landmark)
                                     for f in mh3.FRAMES[:3]]
                        for c in train_cells}
            lkeys = build_keys(lm_specs)
            spec = {c.landmark: (lkeys[c.landmark]["k"],
                                 lkeys[c.landmark]["ref"],
                                 unembed_dir(c.capital), c.capital)
                    for c in train_cells}
            gain = calibrate_gain(spec,
                                  lambda n, sp=lm_specs: sp[n])
            append_neurons([(spec[n][0], spec[n][1], gain * spec[n][2])
                            for n in sorted(spec)])
            rows = eval_cells(keys)
            results[arm] = {"seeds": [rows], "ce": ce_innocents(),
                            "gh": gh_accs(), "gain": gain}
            restore_neurons()
        elif arm in ("gd_cd", "gd_sft", "gd_shuffle"):
            if arm == "gd_cd":
                tp = teacher_probs({c.landmark: c.country
                                    for c in train_cells})
            elif arm == "gd_shuffle":
                dc = derangement(sorted(BANK), rng)
                tp = teacher_probs({c.landmark: dc[c.country]
                                    for c in train_cells})
            else:
                tp = None
            seed_rows, ces, ghs = [], [], []
            for s in range(args.seeds):
                print(f"[wb]   seed {s}")
                unwrap = train_gd("kl" if tp is not None else "ce", tp,
                                  seed=args.seed + s)
                seed_rows.append(eval_cells(keys))
                ces.append(ce_innocents())
                ghs.append(gh_accs())
                unwrap()
            results[arm] = {"seeds": seed_rows,
                            "ce": float(np.mean(ces)),
                            "gh": tuple(np.mean(ghs, axis=0))}
        else:
            print(f"[wb] unknown arm {arm!r} — skipped")
        if arm in results:
            for sp in SPLITS:
                accs = [np.mean([r["correct"] for r in rows if r["split"] == sp])
                        for rows in results[arm]["seeds"]]
                print(f"    {sp}: acc {float(np.mean(accs)):.3f}")

    # ══ frozen scoring ══
    order = {sp: [c.landmark for c in valid if c.split == sp] for sp in SPLITS}

    def acc_arrays(arm: str) -> dict[str, np.ndarray]:
        per = {}
        for sp in SPLITS:
            mat = []
            for rows in results[arm]["seeds"]:
                by = {r["landmark"]: r["correct"] for r in rows
                      if r["split"] == sp}
                mat.append([by[lm] for lm in order[sp]])
            per[sp] = np.mean(np.array(mat), axis=0)
        return per

    scoring = None
    needed = {"base", "construct", "construct_shuffle", "construct_lookup",
              "gd_cd", "gd_shuffle"}
    if needed <= set(results):
        acc = {a: acc_arrays(a) for a in results}
        ce = {a: results[a]["ce"] for a in results}
        gh = {a: results[a]["gh"] for a in results}
        sc = score_arms(acc, ce, gh, np.random.default_rng(args.seed + 999),
                        args.alpha)
        v = verdict_of(gate0_ok, sc)
        det = {}
        for a in ("base", "construct", "gd_cd"):
            if a in results:
                held = [r for r in results[a]["seeds"][0]
                        if r["split"] in ("B1", "B2")]
                det[a] = {"det_mean": float(np.nanmean(
                    [r["detector"] for r in held]))}
        scoring = {"gates": sc, "verdict": v, "detector_g4": det}
        print(f"\n[wb] ════ VERDICT: {v} ════")
        for a in ("construct", "gd_cd"):
            if a in sc:
                r = sc[a]
                print(f"  {a}: G1={r['G1']} G2={r['G2']} G3={r['G3']} "
                      f"G5={r['G5']} train_up={r['train_up']} "
                      f"held_up={r['held_up']}")
    else:
        print(f"[wb] partial arms ({sorted(set(results))}) — no verdict "
              f"(needs {sorted(needed)})")

    payload = {"model_id": args.model_id, "config": vars(args),
               "install_layer": li_star, "band": band,
               "gate0": {"ok": gate0_ok, "splits": ns, "cot_rate": cot_rate},
               "arms": results, "scoring": scoring}
    (out_dir / "results.json").write_text(
        json.dumps(_json_safe(payload), indent=2))
    print(f"[wb] wrote {out_dir}/results.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--gate0-only", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--arms", default="base,construct,construct_shuffle,"
                    "construct_lookup,gd_cd,gd_sft,gd_shuffle")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--whiten-eps", type=float, default=0.1)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-cells", type=int, default=0,
                    help="smoke: cap cells per split (mechanics only)")
    ap.add_argument("--out", default="results/writeback-compile/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
