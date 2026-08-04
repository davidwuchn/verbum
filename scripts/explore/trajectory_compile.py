#!/usr/bin/env python3
"""§P-TRAJECTORY-COMPILE — make gd_cd's wire legible and portable (GTSM + SuperBake).

Pre-reg: mementum/knowledge/explore/trajectory-compile-gtsm-superbake.md
§P-TRAJECTORY-COMPILE (FROZEN s305, Michael-approved; G4 promoted to GATING).

The s303 gd_cd wire (a LoRA delta on a frozen base) generalized behaviorally but
its G4 pin-mechanism was UNMET — an answer-shortcut, not a materialized country.
Three lines converge on a fix (see the page):
  - s305 depth-timing: the country materializes on the one-shot prompt only LATE
    (L*=24), after the native h-hop has consumed its input → the two hops overlap;
  - SuperBake (refs/superbake.txt): "the network is the kernel, and it is upstream"
    — write composition enrichment EARLY (~0.16xdepth ≈ L6); late writes attenuate;
  - GTSM (gtsm-search-space.md, Thm 3.2): endpoint losses admit compensating-error
    (correct output, wrong internals) → a depth-DENSE trajectory loss removes it.

Design: take the one thing that WIRED (gd_cd gradient), (a) widen its LoRA band to
the enrichment band so gradient reshapes the EARLY layers, (b) replace endpoint KL
with a GTSM depth-dense trajectory loss to the teacher's own CoT, SuperBake-weighted.

Loss (FROZEN):
  L = KL_answer(student || teacher)                                 # gd_cd anchor
    + lambda * sum_L w(L) * (1 - cos(student_last[L], teacher_last[L]))  # trajectory
  teacher = frozen base on its own committed CoT (TEACHER_PROMPT, gate-0 country);
  student = the one-shot DIRECT_PROMPT (LoRA-adapted). *_last[L] = last-token
  residual at decoder-layer L output (output_hidden_states[L+1]).
  w(L) = SuperBake schedule: floor 0.2 + Gaussian bumps at enrichment L6 (0.16*N)
  and readout L25 (0.7*N), sigma=2, normalized to sum(w)=1. lambda = 1.0 (not tuned).

Structural change (forced by s305 + SuperBake): LoRA band widened from gd_cd's late
L22-29 to L5-L27 (~0.14-0.75 depth, FFN-only, r=16, alpha=32). lr 1e-4, <=500 steps.

Arms (trained on TRAIN cells; scored on the frozen splits):
  base             : frozen host (floor).
  traj_compile     : PRIMARY — wide band, KL + λ·trajectory.
  gd_cd_wide       : CONTROL (isolates the loss) — same wide band, endpoint KL only.
  traj_shuffle     : λ-yardstick — trajectory loss to a deranged-country teacher.
  construct_lookup : inherited materialized-view null (loaded), F2 baseline (fails B2).

Gates (verbum.dsp paired-perm 10k; F1-F3 Bonferroni alpha/3; G4 GATING; F5 determ.;
primary arm = traj_compile):
  F1 WIRE       : traj_compile > base, flip on B1 AND B2.
  F2 NOT-LOOKUP : traj_compile > construct_lookup on B2.
  F3 SPECIFICITY: traj_compile > traj_shuffle on held-out (B1 + B2).
  G4 PIN (GATING, Michael): mechanism must be legible on held cells. Whitened country
                  key at enrichment L6 (shared-Σ, as build_keys). BOTH required:
                  G4a RISES — mean L6 country readout (traj_compile) > base;
                  G4b TRACKS — readout(correct) > readout(incorrect) held means.
  F5 SURVIVE    : innocent CE ≤ 2% rel base; native g/h within 0.10 abs.
Causal control: gd_cd_wide FAILS G4 while traj_compile passes → the LOSS closed the pin.

Verdicts: TRAJECTORY-COMPILES(+PIN-LEGIBLE,+LOSS-CAUSAL / +PIN-LEGIBLE,BAND-SUFFICES) /
  WIRES-BUT-OPAQUE / NO-WIRE / UNSPECIFIC / HOST-DAMAGED.

Reports (advisory, NEVER gate; wrapped so a failure cannot corrupt the verdict):
  per-layer country-readout trajectory (money plot) · ternarize-retention (TWN the
  traj_compile delta, s304) · G4 at the s303 install layer L23 · KL/trajectory loss
  curves · trit-count of the ternarized delta (λ smallest).

Reuse (no fork, λ one_way): imports writeback_compile as a module for BANK / Cell /
prompts / LoRALinear / constants; loads the frozen gate-0 valid cells and the
construct_lookup B2 baseline from results/writeback-compile/qwen3-4b/ so cells are
IDENTICAL to the gd_cd score. ternarize_delta reused for the advisory TWN plate.

Cadence: --validate (no model) → smoke (--n-cells, mechanics only, s297) →
  Michael GO -> run tmux main:1 (~1-3h MPS) -> frozen scoring.

License: MIT (`λ provenance`).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_WRAP = _HERE.parents[1] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

import ternarize_delta as td  # noqa: E402  (advisory TWN reuse, no fork)
import writeback_compile as wb  # noqa: E402  (module reuse, no fork)
from holo_frag import _json_safe  # noqa: E402

from verbum.dsp import gate, paired_permutation  # noqa: E402

SPLITS = wb.SPLITS

# ── frozen schedule / structure constants (§P-TRAJECTORY-COMPILE) ──
WIDE_BAND = (0.14, 0.75)   # LoRA band fractions → L5..L27 @ N=36 (SuperBake early)
ENRICH_FRAC = 0.16         # enrichment bump (0.16·36 ≈ L6)
READOUT_FRAC = 0.70        # readout bump   (0.70·36 = L25)
INSTALL_FRAC = wb.INSTALL_DEPTH   # 0.65 → L23 (s303 install; advisory G4 continuity)
TRAJ_SIGMA = 2.0           # Gaussian bump width
TRAJ_FLOOR = 0.2           # uniform floor before normalization
TRAJ_LAMBDA = 1.0          # trajectory term weight (FROZEN, not tuned)


# ══════════════════════════════════════════════════════════════════════════
# SuperBake trajectory weighting + band arithmetic (pure)
# ══════════════════════════════════════════════════════════════════════════
def superbake_weights(n_layers: int, enrich_l: int, readout_l: int,
                      sigma: float = TRAJ_SIGMA,
                      floor: float = TRAJ_FLOOR) -> np.ndarray:
    """w(L) over decoder layers 0..n_layers-1: uniform floor + unit-height
    Gaussian bumps at the enrichment and readout layers, normalized to Σ=1.
    GTSM: cover everywhere; spike where it matters (SuperBake supplies where)."""
    ls = np.arange(n_layers, dtype=float)
    w = (floor
         + np.exp(-((ls - enrich_l) ** 2) / (2.0 * sigma ** 2))
         + np.exp(-((ls - readout_l) ** 2) / (2.0 * sigma ** 2)))
    return w / w.sum()


def band_layers(n_layers: int, frac: tuple[float, float] = WIDE_BAND) -> list[int]:
    return list(range(round(frac[0] * n_layers), round(frac[1] * n_layers) + 1))


def enrich_layer(n_layers: int) -> int:
    return round(ENRICH_FRAC * n_layers)


def readout_layer(n_layers: int) -> int:
    return round(READOUT_FRAC * n_layers)


# ══════════════════════════════════════════════════════════════════════════
# G4 legibility gate (pure) — rises ∧ tracks
# ══════════════════════════════════════════════════════════════════════════
def g4_gate(readout_arm, readout_base, correct_arm) -> dict:
    """G4a RISES: mean(arm readout) > mean(base readout) on held cells.
    G4b TRACKS: readout(correct) > readout(incorrect) held means (both classes
    must be present, else legibility is untestable → not-passed, conservative)."""
    ra = np.asarray(readout_arm, float)
    rb = np.asarray(readout_base, float)
    cc = np.asarray(correct_arm, float)
    g4a = bool(ra.mean() > rb.mean())
    pos = ra[cc >= 0.5]
    neg = ra[cc < 0.5]
    if pos.size and neg.size:
        sep = float(pos.mean() - neg.mean())
        g4b = bool(sep > 0.0)
    else:
        sep = float("nan")
        g4b = False
    return {"g4a": g4a, "g4b": g4b, "g4": bool(g4a and g4b),
            "arm_mean": float(ra.mean()), "base_mean": float(rb.mean()),
            "sep": sep, "n_correct": int((cc >= 0.5).sum()),
            "n_incorrect": int((cc < 0.5).sum())}


# ══════════════════════════════════════════════════════════════════════════
# Frozen scoring + verdict (pure; --validate exercises planted worlds)
# ══════════════════════════════════════════════════════════════════════════
def _g(a, b, rng, alpha, name):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    return gate(float(np.mean(a - b)), paired_permutation(a, b, rng),
                "greater", alpha, name=name)


def score(acc: dict, ce: dict, gh: dict, g4in: dict, rng, alpha: float) -> dict:
    """acc[arm][split] = per-cell mean-over-seed correctness (aligned order);
    ce[arm], gh[arm]=(g,h) for traj_compile+base; g4in[arm] =
    {'readout': held-array, 'correct': held-array} for base/traj_compile/
    gd_cd_wide. Returns frozen F1-F5 + G4 for the primary arm traj_compile."""
    a3 = alpha / 3.0
    P, B = "traj_compile", "base"
    r = {}
    # F1 WIRE : traj_compile > base, flip on B1 AND B2
    g1 = {}
    for sp in ("B1", "B2"):
        gg = _g(acc[P][sp], acc[B][sp], rng, a3, f"F1-{sp}")
        g1[sp] = {"gate": gg, "flip": bool(acc[P][sp].mean() > acc[B][sp].mean())}
    r["F1"] = bool(all(g1[sp]["gate"].verdict and g1[sp]["flip"]
                       for sp in ("B1", "B2")))
    r["F1_detail"] = g1
    # F2 NOT-LOOKUP : traj_compile > construct_lookup on B2
    g2 = _g(acc[P]["B2"], acc["construct_lookup"]["B2"], rng, a3, "F2-B2")
    r["F2"] = bool(g2.verdict)
    r["F2_detail"] = g2
    # F3 SPECIFICITY : traj_compile > traj_shuffle on held-out (B1 + B2)
    held_p = np.concatenate([acc[P]["B1"], acc[P]["B2"]])
    held_s = np.concatenate([acc["traj_shuffle"]["B1"], acc["traj_shuffle"]["B2"]])
    g3 = _g(held_p, held_s, rng, a3, "F3-heldout")
    r["F3"] = bool(g3.verdict)
    r["F3_detail"] = g3
    # F5 SURVIVE
    ce_ok = ce[P] <= ce[B] * 1.02
    g_ok = gh[P][0] >= gh[B][0] - 0.10
    h_ok = gh[P][1] >= gh[B][1] - 0.10
    r["F5"] = bool(ce_ok and g_ok and h_ok)
    r["F5_detail"] = {"ce": ce[P], "ce_base": ce[B],
                      "g_acc": gh[P][0], "h_acc": gh[P][1]}
    # G4 PIN (GATING) for the primary arm + the causal control
    g4t = g4_gate(g4in[P]["readout"], g4in[B]["readout"], g4in[P]["correct"])
    r["G4_traj"] = bool(g4t["g4"])
    r["G4_traj_detail"] = g4t
    if "gd_cd_wide" in g4in:
        g4w = g4_gate(g4in["gd_cd_wide"]["readout"], g4in[B]["readout"],
                      g4in["gd_cd_wide"]["correct"])
        r["G4_wide"] = bool(g4w["g4"])
        r["G4_wide_detail"] = g4w
    else:
        r["G4_wide"] = False
    # lookup null guard (must FAIL B2; if it moves, the task has a shortcut)
    lk = _g(acc["construct_lookup"]["B2"], acc[B]["B2"], rng, alpha, "lookup-B2")
    r["lookup_b2_moves"] = bool(lk.verdict)
    r["held_up"] = bool(held_p.mean()
                        > np.concatenate([acc[B]["B1"], acc[B]["B2"]]).mean())
    return r


def verdict_of(gate0_ok: bool, r: dict) -> str:
    if not gate0_ok:
        return "VOID (gate-0)"
    if r.get("lookup_b2_moves"):
        return "VOID (lookup null moves B2 — task has a shortcut)"
    if not r["F5"]:
        return "HOST-DAMAGED"
    if not r["F1"]:
        return "NO-WIRE"
    if not r["F3"]:
        return "UNSPECIFIC"
    if r["F1"] and r["F2"] and r["F3"]:
        if r["G4_traj"]:
            if not r["G4_wide"]:
                return "TRAJECTORY-COMPILES (+PIN-LEGIBLE, +LOSS-CAUSAL)"
            return "TRAJECTORY-COMPILES (+PIN-LEGIBLE, BAND-SUFFICES)"
        return "WIRES-BUT-OPAQUE"
    return "inconclusive (F1∧F3 but F2 unresolved — wire vs lookup)"


# ══════════════════════════════════════════════════════════════════════════
# --validate (no model)
# ══════════════════════════════════════════════════════════════════════════
def run_validate(alpha: float) -> int:
    ok = True
    print("── §P-TRAJECTORY-COMPILE --validate (no model) ──")

    # 1. SuperBake weight schedule
    n = 36
    el, rl = enrich_layer(n), readout_layer(n)
    w = superbake_weights(n, el, rl)
    good = (abs(w.sum() - 1.0) < 1e-9 and (w > 0).all()
            and el in (6,) and rl == 25
            and w[el] > w[15] and w[rl] > w[15]
            and set(np.argsort(w)[-2:]) == {el, rl})
    print(f"[V] w-schedule: Σ={w.sum():.6f} enrich=L{el} readout=L{rl} "
          f"peaks={sorted(np.argsort(w)[-2:].tolist())} floor_min={w.min():.4f} "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 2. wide-band arithmetic (L5..L27 @ N=36, contains enrich + readout)
    band = band_layers(n)
    old = band_layers(n, wb.BAND)
    good = (band[0] == 5 and band[-1] == 27 and el in band and rl in band
            and band[0] < old[0] and band[-1] < old[-1])
    print(f"[V] wide-band: L{band[0]}..L{band[-1]} (old L{old[0]}..L{old[-1]}) "
          f"contains enrich∧readout={el in band and rl in band} "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 3. trajectory cosine loss descends → student aligns to teacher
    import torch
    import torch.nn.functional as F
    torch.manual_seed(0)
    d, nl = 8, 6
    teacher = torch.randn(nl, d)
    student = torch.nn.Parameter(torch.randn(nl, d))
    wt = torch.tensor(superbake_weights(nl, 1, 4), dtype=torch.float32)
    opt = torch.optim.Adam([student], lr=0.1)
    with torch.no_grad():
        cos0 = float(F.cosine_similarity(student, teacher, dim=-1).mean())
    for _ in range(60):
        opt.zero_grad()
        cos = F.cosine_similarity(student, teacher, dim=-1)
        (wt * (1.0 - cos)).sum().backward()
        opt.step()
    with torch.no_grad():
        cos1 = float(F.cosine_similarity(student, teacher, dim=-1).mean())
    good = cos1 > cos0 + 0.2 and cos1 > 0.8
    print(f"[V] trajectory: cos {cos0:.3f} → {cos1:.3f} {'OK' if good else 'FAIL'}")
    ok &= good

    # 4. G4 gate logic (rises ∧ tracks)
    corr = np.array([1, 1, 1, 1, 1, 0, 0, 0, 0, 0], float)
    legible = g4_gate(np.array([2, 2, 2, 2, 2, .1, .1, .1, .1, .1]),
                      np.zeros(10), corr)
    not_rise = g4_gate(np.zeros(10), np.zeros(10) + 0.5, corr)
    rise_no_track = g4_gate(np.ones(10), np.zeros(10),
                            np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0], float))
    good = (legible["g4"] and not not_rise["g4"] and not_rise["g4a"] is False
            and rise_no_track["g4a"] and not rise_no_track["g4b"])
    print(f"[V] G4: legible={legible['g4']} not-rise={not_rise['g4']} "
          f"rise-no-track={rise_no_track['g4']} {'OK' if good else 'FAIL'}")
    ok &= good

    # 5. LoRA reuse (init identity + grad isolation) — from wb
    dm = 16
    lin = torch.nn.Linear(dm, dm, bias=False)
    lo = wb.LoRALinear(lin, r=4, alpha=8)
    x = torch.randn(3, dm)
    with torch.no_grad():
        ident = float((lo(x) - lin(x)).abs().max())
    lo(x).sum().backward()
    good = ident < 1e-6 and lo.A.grad is not None and lin.weight.grad is None
    print(f"[V] lora: init-identity {ident:.1e} base-frozen="
          f"{lin.weight.grad is None} {'OK' if good else 'FAIL'}")
    ok &= good

    # 6. verdict logic — pure boolean planted worlds (all 7 verdicts)
    def vworld(name, want, **flags):
        base = {"F1": True, "F2": True, "F3": True, "F5": True,
                "G4_traj": True, "G4_wide": False, "lookup_b2_moves": False,
                "held_up": True}
        base.update(flags)
        v = verdict_of(True, base)
        hit = want in v
        print(f"[V] {name} -> {v} (want {want}) {'OK' if hit else 'FAIL'}")
        return hit
    ok &= vworld("loss-causal", "+LOSS-CAUSAL")
    ok &= vworld("band-suffices", "BAND-SUFFICES", G4_wide=True)
    ok &= vworld("wires-opaque", "WIRES-BUT-OPAQUE", G4_traj=False, G4_wide=False)
    ok &= vworld("no-wire", "NO-WIRE", F1=False)
    ok &= vworld("unspecific", "UNSPECIFIC", F3=False)
    ok &= vworld("host-damaged", "HOST-DAMAGED", F5=False)
    ok &= vworld("void-shortcut", "VOID (lookup", lookup_b2_moves=True)

    # 7. score() integration — plant acc + g4 arrays for +LOSS-CAUSAL
    rng = np.random.default_rng(2)

    def arr(p, k=16):
        return (rng.random(k) < p).astype(float)
    acc = {
        "base": {"TRAIN": arr(.15), "B1": arr(.12), "B2": arr(.30)},
        "traj_compile": {"TRAIN": arr(.95), "B1": arr(.92), "B2": arr(.95)},
        "gd_cd_wide": {"TRAIN": arr(.95), "B1": arr(.9), "B2": arr(.95)},
        "traj_shuffle": {"TRAIN": arr(.2), "B1": arr(.12), "B2": arr(.2)},
    }
    # a real lookup fails B2 (materialized view; held countries absent) — plant
    # it == base so the shortcut guard does not fire in this +LOSS-CAUSAL world
    acc["construct_lookup"] = {"B2": acc["base"]["B2"].copy()}
    n_held = len(acc["traj_compile"]["B1"]) + len(acc["traj_compile"]["B2"])
    corr_held = np.concatenate([acc["traj_compile"]["B1"],
                                acc["traj_compile"]["B2"]])
    g4in = {
        "base": {"readout": np.zeros(n_held), "correct": np.zeros(n_held)},
        # traj readout rises + tracks correctness; wide rises but does NOT track
        "traj_compile": {"readout": 1.0 + 2.0 * corr_held, "correct": corr_held},
        "gd_cd_wide": {"readout": np.ones(n_held), "correct": corr_held},
    }
    r = score(acc, {"traj_compile": 1.0, "base": 1.0},
              {"traj_compile": (.95, .95), "base": (.95, .95)}, g4in,
              np.random.default_rng(3), alpha)
    v = verdict_of(True, r)
    good = "+LOSS-CAUSAL" in v
    print(f"[V] score-integration -> {v} "
          f"(F1={r['F1']} F2={r['F2']} F3={r['F3']} G4t={r['G4_traj']} "
          f"G4w={r['G4_wide']} F5={r['F5']}) {'OK' if good else 'FAIL'}")
    ok &= good

    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


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
    tok = AutoTokenizer.from_pretrained(args.model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    dec, _norm, _lm_head = mh3.resolve_parts(model)
    n_layers = len(dec)
    band = band_layers(n_layers)
    enrich_l = enrich_layer(n_layers)
    readout_l = readout_layer(n_layers)
    install_l = round(INSTALL_FRAC * n_layers)
    w_sched = superbake_weights(n_layers, enrich_l, readout_l)
    w_t = torch.tensor(w_sched, dtype=torch.float32, device=dev)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rec = Path(args.record_dir)

    def first_tid(w: str) -> int:
        return mh3.first_tid(tok, w)

    # ── valid cells + construct_lookup baseline from the FROZEN s303 record ──
    g0 = json.loads((rec / "gate0.json").read_text())
    gate0_ok = bool(g0["gate0_ok"])
    fields = ("landmark", "city", "country", "capital", "split")
    valid = [wb.Cell(**{k: c[k] for k in fields}) for c in g0["cells"]
             if c.get("g_ok") and c.get("h_ok") and c.get("cot_ok")]
    res_frozen = json.loads((rec / "results.json").read_text())
    lookup_b2 = {x["landmark"]: x["correct"]
                 for x in res_frozen["arms"]["construct_lookup"]["seeds"][0]
                 if x["split"] == "B2"}
    ns = {sp: sum(1 for c in valid if c.split == sp) for sp in SPLITS}
    print(f"[tc] {args.model_id} dev={dev} N={n_layers} "
          f"band=L{band[0]}..L{band[-1]} enrich=L{enrich_l} readout=L{readout_l} "
          f"install=L{install_l} valid={len(valid)} splits={ns} "
          f"seeds={args.seeds} steps={args.steps} λ={TRAJ_LAMBDA} gate0={gate0_ok}",
          flush=True)

    if args.n_cells:                       # smoke cap (mechanics only, s297)
        by = {sp: [c for c in valid if c.split == sp] for sp in SPLITS}
        valid = [c for sp in SPLITS for c in by[sp][:args.n_cells]]
        lookup_b2 = {c.landmark: lookup_b2.get(c.landmark, 0.0)
                     for c in valid if c.split == "B2"}
        print(f"[tc] SMOKE cap {args.n_cells}/split -> {len(valid)} cells")
    train_cells = [c for c in valid if c.split == "TRAIN"]
    held_cells = [c for c in valid if c.split in ("B1", "B2")]

    # ── union candidate set (recompute; warn on drift vs frozen) ──
    tid_map, drop = {}, set()
    for w in wb.union_words():
        t = first_tid(w)
        clash = [x for x, tt in tid_map.items() if tt == t]
        if clash:
            drop.add(w)
            drop.update(clash)
        tid_map[w] = t
    union = {w: tid_map[w] for w in sorted(set(wb.union_words()) - drop)}
    if sorted(drop) != g0.get("union_dropped", sorted(drop)):
        print(f"[tc] WARN union drop drift: {sorted(drop)} vs frozen "
              f"{g0.get('union_dropped')}")
    countries = sorted(wb.BANK)
    caps = sorted({cap for cap, _ in wb.BANK.values()})

    # ── forward helpers ──
    def logits_last(prompt: str) -> np.ndarray:
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            return model(**ids).logits[0, -1, :].float().cpu().numpy()

    def argmax_union(lo):
        return max(union, key=lambda w: lo[union[w]])

    def margin(lo, truth):
        return float(lo[union[truth]]
                     - max(lo[union[w]] for w in union if w != truth))

    def eval_cells() -> list[dict]:
        rows = []
        for c in valid:
            lo = logits_last(wb.DIRECT_PROMPT.format(lm=c.landmark))
            arg = argmax_union(lo)
            rows.append({"landmark": c.landmark, "country": c.country,
                         "split": c.split, "truth": c.capital, "arg": arg,
                         "correct": float(wb.first_word(arg)
                                          == wb.first_word(c.capital)),
                         "margin": margin(lo, c.capital)})
        return rows

    def ce_innocents() -> float:
        tot, k = 0.0, 0
        for t in wb.CE_TEXTS:
            ids = tok(t, return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits
            lp = F.log_softmax(lo[0, :-1].float(), dim=-1)
            tgt = ids.input_ids[0, 1:]
            tot += float(-lp[torch.arange(len(tgt)), tgt].sum())
            k += len(tgt)
        return tot / max(k, 1)

    def gh_accs():
        g = [max(countries, key=lambda w: logits_last(
            wb.G_QUERY_PREFIX + wb.G_QUERY.format(lm=c.landmark))[first_tid(w)])
            == c.country for c in valid]
        h = [wb.first_word(max(caps, key=lambda w: logits_last(
            wb.CAP_PREFIX + wb.CAP_QUERY.format(x=co))[first_tid(w)]))
            == wb.first_word(wb.BANK[co][0]) for co in sorted(wb.BANK)]
        return float(np.mean(g)), float(np.mean(h))

    # ── whitened country keys (shared-Σ) at an arbitrary layer, via
    #    post_attention_layernorm — the build_keys convention (s295 law) ──
    def capture_postnorm_at(layer: int, prompts: list[str]) -> np.ndarray:
        vecs = []
        for p in prompts:
            store = {}
            hnd = dec[layer].post_attention_layernorm.register_forward_hook(
                lambda m, i, o, s=store: s.__setitem__("v", o))
            ids = tok(p, return_tensors="pt").to(dev)
            with torch.no_grad():
                model(**ids)
            hnd.remove()
            vecs.append(store["v"][0, -1, :].float().cpu().numpy())
        return np.stack(vecs)

    def build_keys_at(layer: int) -> dict:
        inn_prompts = list(wb.PROSE_INNOCENTS) + [
            wb.DIRECT_PROMPT.format(lm=nc) for nc in wb.NONCE_CANDS[:3]]
        inn = capture_postnorm_at(layer, inn_prompts)
        owns = {c: capture_postnorm_at(layer, [f.format(x=c) for f in wb.CC_FRAMES])
                for c in sorted(wb.BANK)}
        pop = np.vstack([*owns.values(), inn])
        mu = pop.mean(axis=0)
        xc = pop - mu
        cov = (xc.T @ xc) / max(len(pop) - 1, 1)
        d = cov.shape[0]
        cov += args.whiten_eps * (np.trace(cov) / d) * np.eye(d)
        keys = {}
        for c, own in owns.items():
            k = np.linalg.solve(cov, own.mean(axis=0) - mu)
            keys[c] = k / (np.linalg.norm(k) + 1e-9)
        return keys

    def country_readout(layer: int, keys: dict, cells) -> np.ndarray:
        """Per-cell L-country readout on the one-shot DIRECT prompt (arm's
        current weights). readout = postnorm@layer · whitened country key."""
        out = []
        for c in cells:
            v = capture_postnorm_at(layer, [wb.DIRECT_PROMPT.format(lm=c.landmark)])[0]
            out.append(float(v @ keys[c.country]))
        return np.array(out)

    # ── teacher: KL target (last-token) + trajectory (per-layer last-token) ──
    def teacher_kl(country_of: dict) -> dict:
        out = {}
        for c in train_cells:
            lo = logits_last(wb.TEACHER_PROMPT.format(lm=c.landmark,
                                                      c=country_of[c.landmark]))
            out[c.landmark] = torch.softmax(
                torch.tensor(lo, dtype=torch.float32), dim=-1)
        return out

    def teacher_traj(country_of: dict) -> torch.Tensor:
        """(n_train, n_layers, d) last-token residuals of the frozen base on
        each cell's committed CoT. Precomputed once (no grad, no LoRA)."""
        rows = []
        for c in train_cells:
            ids = tok(wb.TEACHER_PROMPT.format(lm=c.landmark,
                                               c=country_of[c.landmark]),
                      return_tensors="pt").to(dev)
            with torch.no_grad():
                hs = model(**ids, output_hidden_states=True).hidden_states
            rows.append(torch.stack([hs[li + 1][0, -1, :].float()
                                     for li in range(n_layers)]))
        return torch.stack(rows).to(dev)          # (B, n_layers, d)

    # ── GD arm: wide-band FFN LoRA; kind ∈ {"traj","kl"} ──
    def train_arm(kind: str, country_of: dict, seed: int):
        tp = teacher_kl(country_of)
        ttraj = teacher_traj(country_of) if kind == "traj" else None
        torch.manual_seed(seed)
        wrapped, params = [], []
        for li in band:
            m = dec[li].mlp
            for name in ("gate_proj", "up_proj", "down_proj"):
                orig = getattr(m, name)
                lw = wb.LoRALinear(orig, r=args.lora_r, alpha=2 * args.lora_r)
                setattr(m, name, lw)
                wrapped.append((m, name, orig, lw, li))
                params += [lw.A, lw.B]
        opt = torch.optim.Adam(params, lr=args.lr)
        prompts = [wb.DIRECT_PROMPT.format(lm=c.landmark) for c in train_cells]
        batch = tok(prompts, return_tensors="pt", padding=True).to(dev)
        tpv = torch.stack([tp[c.landmark] for c in train_cells]).to(dev)
        curve = []
        for step in range(args.steps):
            opt.zero_grad()
            out = model(**batch, output_hidden_states=(kind == "traj"))
            lo = out.logits[:, -1, :].float()
            loss_kl = -(tpv * F.log_softmax(lo, dim=-1)).sum(-1).mean()
            loss_tr = torch.tensor(0.0, device=dev)
            if kind == "traj":
                student = torch.stack(
                    [out.hidden_states[li + 1][:, -1, :].float()
                     for li in range(n_layers)], dim=1)      # (B, n_layers, d)
                cos = F.cosine_similarity(student, ttraj, dim=-1)  # (B, n_layers)
                loss_tr = (w_t * (1.0 - cos)).sum(-1).mean()
            loss = loss_kl + TRAJ_LAMBDA * loss_tr
            loss.backward()
            opt.step()
            if step % max(args.steps // 5, 1) == 0 or step == args.steps - 1:
                curve.append({"step": step, "kl": float(loss_kl.detach()),
                              "traj": float(loss_tr.detach())})
                print(f"    step {step:4d} kl {float(loss_kl.detach()):.4f} "
                      f"traj {float(loss_tr.detach()):.4f}", flush=True)
        deltas = {}
        for (_m, name, _orig, lw, li) in wrapped:
            with torch.no_grad():
                deltas[(li, name)] = (lw.scale * (lw.B @ lw.A)).float().cpu().numpy()

        def unwrap():
            for (m, name, orig, _lw, _li) in wrapped:
                setattr(m, name, orig)
        return unwrap, deltas, curve

    # ══ run arms ══
    print(f"[tc] building whitened country keys (base, L{enrich_l})...",
          flush=True)
    keys_enrich = build_keys_at(enrich_l)
    keys_install = None
    try:
        keys_install = build_keys_at(install_l)      # advisory G4@L23 continuity
    except Exception as e:                            # pragma: no cover
        print(f"[tc] (advisory) keys@L{install_l} failed: {e}")

    def held_readout(keys) -> np.ndarray:
        return country_readout(enrich_l, keys, held_cells)

    order = {sp: [c.landmark for c in valid if c.split == sp] for sp in SPLITS}
    held_order = [c.landmark for c in held_cells]
    arms: dict = {}
    g4in: dict = {}
    curves: dict = {}

    def correct_held(rows) -> np.ndarray:
        by = {r["landmark"]: r["correct"] for r in rows if r["split"] in ("B1", "B2")}
        return np.array([by[lm] for lm in held_order])

    # base
    print("[tc] ── base ──", flush=True)
    base_rows = eval_cells()
    base_ce = ce_innocents()
    base_gh = gh_accs()
    base_ro = held_readout(keys_enrich)
    arms["base"] = {"seeds": [base_rows], "ce": base_ce, "gh": base_gh}
    g4in["base"] = {"readout": base_ro, "correct": correct_held(base_rows)}
    for sp in SPLITS:
        print(f"    {sp}: acc "
              f"{np.mean([r['correct'] for r in base_rows if r['split']==sp]):.3f}")

    # gd arms (seed-looped)
    gd_specs = {
        "traj_compile": ("traj", {c.landmark: c.country for c in train_cells}),
        "gd_cd_wide": ("kl", {c.landmark: c.country for c in train_cells}),
    }
    rng = np.random.default_rng(args.seed)
    for arm, (kind, country_of) in gd_specs.items():
        print(f"[tc] ── {arm} ({kind}, wide band) ──", flush=True)
        seed_rows, ces, ghs, ros = [], [], [], []
        arm_deltas = None
        arm_curve = None
        for s in range(args.seeds):
            print(f"[tc]   seed {s}", flush=True)
            unwrap, deltas, curve = train_arm(kind, country_of, args.seed + s)
            seed_rows.append(eval_cells())
            ces.append(ce_innocents())
            ghs.append(gh_accs())
            ros.append(held_readout(keys_enrich))
            if s == 0:
                arm_deltas, arm_curve = deltas, curve
            unwrap()
        arms[arm] = {"seeds": seed_rows, "ce": float(np.mean(ces)),
                     "gh": tuple(np.mean(ghs, axis=0))}
        g4in[arm] = {"readout": np.mean(ros, axis=0),
                     "correct": np.mean([correct_held(r) for r in seed_rows], axis=0)}
        curves[arm] = arm_curve
        if arm == "traj_compile":
            traj_deltas = arm_deltas
        for sp in SPLITS:
            accs = [np.mean([r["correct"] for r in rows if r["split"] == sp])
                    for rows in seed_rows]
            print(f"    {sp}: acc {float(np.mean(accs)):.3f}")

    # traj_shuffle (λ-yardstick): trajectory loss to a deranged-country teacher
    print("[tc] ── traj_shuffle (deranged-country teacher) ──", flush=True)
    sh_rows = []
    for s in range(args.seeds):
        dc = wb.derangement(sorted(wb.BANK), rng)
        country_of = {c.landmark: dc[c.country] for c in train_cells}
        print(f"[tc]   shuffle seed {s}", flush=True)
        unwrap, _deltas, _curve = train_arm("traj", country_of, args.seed + 100 + s)
        sh_rows.append(eval_cells())
        unwrap()
    arms["traj_shuffle"] = {"seeds": sh_rows}
    for sp in SPLITS:
        accs = [np.mean([r["correct"] for r in rows if r["split"] == sp])
                for rows in sh_rows]
        print(f"    {sp}: acc {float(np.mean(accs)):.3f}")

    # construct_lookup (frozen, single record)
    arms["construct_lookup"] = {"b2": lookup_b2}

    # ══ frozen scoring ══
    def acc_arrays(label) -> dict:
        per = {}
        for sp in SPLITS:
            mat = []
            for rows in arms[label]["seeds"]:
                by = {r["landmark"]: r["correct"] for r in rows
                      if r["split"] == sp}
                mat.append([by[lm] for lm in order[sp]])
            per[sp] = np.mean(np.array(mat), axis=0)
        return per

    acc = {a: acc_arrays(a) for a in ("base", "traj_compile", "gd_cd_wide",
                                      "traj_shuffle")}
    acc["construct_lookup"] = {
        "B2": np.array([lookup_b2[lm] for lm in order["B2"]]),
        "B1": np.zeros(len(order["B1"])), "TRAIN": np.zeros(len(order["TRAIN"]))}
    ce = {"traj_compile": arms["traj_compile"]["ce"], "base": base_ce}
    gh = {"traj_compile": arms["traj_compile"]["gh"], "base": base_gh}
    r = score(acc, ce, gh, g4in, np.random.default_rng(args.seed + 999), args.alpha)
    v = verdict_of(gate0_ok, r)

    # ══ advisory reports (NEVER gate; isolated so a failure can't corrupt) ══
    reports: dict = {"loss_curves": curves}
    try:                                   # money plot: per-layer readout traj
        probe = sorted(set(range(2, n_layers, 4)) | {enrich_l, readout_l, install_l})
        keys_by_layer = {li: build_keys_at(li) for li in probe}

        def readout_traj(cells) -> dict:
            return {li: float(np.mean(country_readout(li, keys_by_layer[li], cells)))
                    for li in probe}
        money = {"base": readout_traj(held_cells)}
        # only the traj_compile seed-0 delta is retained (the money arm)
        merged = _apply_delta(dec, traj_deltas, torch)
        money["traj_compile"] = readout_traj(held_cells)
        _restore_delta(dec, merged, torch)
        reports["money_plot"] = money
    except Exception as e:                 # pragma: no cover
        print(f"[tc] (advisory) money_plot failed: {e}")
        reports["money_plot"] = None
    try:                                   # G4 @ install layer L23 (continuity)
        if keys_install is not None:
            g4_23 = {}
            base23 = country_readout(install_l, keys_install, held_cells)
            merged = _apply_delta(dec, traj_deltas, torch)
            traj23 = country_readout(install_l, keys_install, held_cells)
            _restore_delta(dec, merged, torch)
            g4_23 = g4_gate(traj23, base23,
                            correct_held(arms["traj_compile"]["seeds"][0]))
            reports[f"g4_at_install_L{install_l}"] = g4_23
    except Exception as e:                 # pragma: no cover
        print(f"[tc] (advisory) g4@install failed: {e}")
    try:                                   # ternarize-retention (λ smallest)
        d_tern = {k: td.ternarize_twn(vv)[0] for k, vv in traj_deltas.items()}
        stats = td.plate_stats(traj_deltas, d_tern)
        merged = _apply_delta(dec, d_tern, torch)
        tern_rows = eval_cells()
        _restore_delta(dec, merged, torch)
        tern_acc = {sp: float(np.mean([x["correct"] for x in tern_rows
                                       if x["split"] == sp])) for sp in SPLITS}
        float_acc = {sp: float(acc["traj_compile"][sp].mean()) for sp in SPLITS}
        reports["ternarize"] = {
            "float_acc": float_acc, "ternary_acc": tern_acc,
            "retention": {sp: (tern_acc[sp] / float_acc[sp]
                               if float_acc[sp] > 1e-9 else None) for sp in SPLITS},
            "mag_cos_pooled": stats["mag_cos_pooled"], "trits": stats["trits"],
            "bits": stats["bits"], "sparsity": stats["sparsity"]}
    except Exception as e:                 # pragma: no cover
        print(f"[tc] (advisory) ternarize failed: {e}")
        reports["ternarize"] = None

    print(f"\n[tc] ════ VERDICT: {v} ════")
    print(f"  F1={r['F1']} F2={r['F2']} F3={r['F3']} "
          f"G4_traj={r['G4_traj']} G4_wide={r['G4_wide']} F5={r['F5']}")
    print(f"  G4a rise: traj {r['G4_traj_detail']['arm_mean']:.4f} vs base "
          f"{r['G4_traj_detail']['base_mean']:.4f}; G4b sep "
          f"{r['G4_traj_detail']['sep']}")
    for sp in SPLITS:
        print(f"  {sp}: base {acc['base'][sp].mean():.3f} traj "
              f"{acc['traj_compile'][sp].mean():.3f} wide "
              f"{acc['gd_cd_wide'][sp].mean():.3f} shuf "
              f"{acc['traj_shuffle'][sp].mean():.3f}")

    def _degate(o):
        if is_dataclass(o) and not isinstance(o, type):
            return asdict(o)
        if isinstance(o, dict):
            return {k: _degate(x) for k, x in o.items()}
        if isinstance(o, (list, tuple)):
            return [_degate(x) for x in o]
        return o

    scoring = {"gates": r, "verdict": v, "reports": reports}
    payload = {"model_id": args.model_id, "config": vars(args),
               "n_layers": n_layers, "band": band, "enrich_layer": enrich_l,
               "readout_layer": readout_l, "w_schedule": w_sched.tolist(),
               "gate0": {"ok": gate0_ok, "splits": ns}, "arms": arms,
               "scoring": scoring}
    (out_dir / "results.json").write_text(
        json.dumps(_json_safe(_degate(payload)), indent=2))
    print(f"[tc] wrote {out_dir}/results.json")
    return 0


# ── delta-plate merge helpers (advisory reports reuse; real add/sub) ──
def _apply_delta(dec, deltas: dict, torch) -> dict:
    added = {}
    for (li, name), d in deltas.items():
        w = getattr(dec[li].mlp, name).weight
        add = torch.tensor(d, dtype=w.dtype, device=w.device)
        with torch.no_grad():
            w.add_(add)
        added[(li, name)] = add
    return added


def _restore_delta(dec, added: dict, torch):
    for (li, name), add in added.items():
        with torch.no_grad():
            getattr(dec[li].mlp, name).weight.sub_(add)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--whiten-eps", type=float, default=0.1)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-cells", type=int, default=0,
                    help="smoke: cap cells per split (mechanics only)")
    ap.add_argument("--record-dir",
                    default="results/writeback-compile/qwen3-4b",
                    help="frozen s303 record: gate0.json + results.json")
    ap.add_argument("--out", default="results/trajectory-compile/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
