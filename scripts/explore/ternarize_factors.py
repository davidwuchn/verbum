#!/usr/bin/env python3
"""§TERNARIZE-FACTORS-1 — does the gd_cd wire survive ternarizing the FACTORS?

Pre-reg: mementum/knowledge/explore/write-not-train-ternary-routing-deltas.md
§TERNARIZE-FACTORS-1 (FROZEN s307, Michael-approved). §Result-ternarize-delta
SURVIVES-TERNARY on the EXPANDED PRODUCT scale*B*A, but the product plate (~370M
trits, ~73 MB) is LARGER than the float factored form (~5M params, ~10 MB) — a
lambda-smallest tension. This ternarizes the low-rank FACTORS B and A SEPARATELY
(per rank-component TWN), forms Delta = scale*B_hat*A_hat, and re-scores the frozen
gates. If the wire survives, the genuinely small portable artifact exists:
~16*(out+in) trits/matrix ≈ 100x smaller than the product plate, ~10x over float
factors (~1 MB wire). Harder than TERNARIZE-DELTA-1: both factors are quantized
independently and errors compound in the product (no central-limit smoothing).

Reuse (no fork, lambda one_way): imports ternarize_delta's PURE helpers
(ternarize_twn / shuffle_plate / plate_stats) and writeback_compile as a module for
BANK / Cell / prompts / LoRALinear / constants. Loads the frozen gate-0 valid cells
and the construct_lookup B2 baseline from the committed s303 record so cells are
IDENTICAL to the gd_cd score. Does NOT modify the frozen s304 generator
(ternarize_delta.py; its cb73ad5 result must stand).

Ternarize factors (FROZEN, per rank-component TWN, thr 0.7):
  A (r,in)  -> per-ROW    (each row = one rank direction's input pattern)
  B (out,r) -> per-COLUMN (each col = one rank direction's output pattern)
  Delta = scale * B_hat @ A_hat, merged onto the frozen base, eval, restore.

Arms (one process, per-seed factors -> ternary + shuffle):
  base                   : frozen host (reproduce 0.200 / 0.125 / 0.545).
  gd_cd_float            : float LoRA delta (ANCHOR: reproduce ~1.0/0.938/1.0).
  gd_cd_product_ternary  : s304 arm (ternarize the EXPANDED product) — contrast.
  gd_cd_factors_ternary  : PRIMARY — ternarize B and A separately.
  gd_cd_factors_shuffle  : null (per-component sign*mask shuffle each factor) MUST fail.
  construct_lookup       : frozen materialized-view null, TF2 baseline.

Gates (verbum.dsp, paired permutation 10k, primaries Bonferroni alpha/3):
  TF1 WIRE-SURVIVES : factors_ternary > base, flip on B1 AND B2.
  TF2 NOT-LOOKUP    : factors_ternary > construct_lookup on B2.
  TF3 SPECIFICITY   : factors_ternary > factors_shuffle on held-out (B1+B2).
  TF5 SURVIVE       : innocent CE <= 2% rel base; native g/h within 0.10 abs.
  TF4 FACTORING-COST (advisory sub-tag): retention(factors) vs retention(product)
      -> +FACTORING-FREE / +FACTORING-COSTS.
Verdicts: FACTORS-SURVIVE(+FACTORING-FREE/+COSTS) / FACTORS-DEGRADE / FACTORS-DIE /
  HOST-DAMAGED.

Cadence: --validate (no model) -> smoke (--n-cells, mechanics only) ->
Michael GO -> full run tmux main:1 -> frozen scoring.

License: MIT (`lambda provenance`).
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

import ternarize_delta as td  # noqa: E402  (pure helpers reuse; frozen generator untouched)
import writeback_compile as wb  # noqa: E402  (module reuse, no fork)
from holo_frag import _json_safe  # noqa: E402

from verbum.dsp import gate, paired_permutation  # noqa: E402

SPLITS = wb.SPLITS
LOG2_3 = td.LOG2_3


# ══════════════════════════════════════════════════════════════════════════
# Factor ternarization (per rank-component TWN) + per-component shuffle null
# ══════════════════════════════════════════════════════════════════════════
def ternarize_factors(b: np.ndarray, a: np.ndarray, scale: float):
    """B (out,r) per-COLUMN TWN; A (r,in) per-ROW TWN (= per-column of A.T).
    Returns (delta = scale*B_hat@A_hat, B_hat, A_hat)."""
    b_hat = td.ternarize_twn(b)[0]                 # per-column (per rank dir on B)
    a_hat = td.ternarize_twn(a.T)[0].T             # per-row (per rank dir on A)
    delta = (scale * (b_hat @ a_hat)).astype(np.float32)
    return delta, b_hat.astype(np.float32), a_hat.astype(np.float32)


def shuffle_factors(b_hat: np.ndarray, a_hat: np.ndarray, scale: float,
                    rng: np.random.Generator) -> np.ndarray:
    """Per-component sign*mask shuffle of each ternary factor (matched trit count +
    matched per-component gamma), destroying the routing geometry; returns the
    shuffled product delta = scale*B_s@A_s."""
    b_s = td.shuffle_plate(b_hat, rng)             # permute rows within each B column
    a_s = td.shuffle_plate(a_hat.T, rng).T         # permute cols within each A row
    return (scale * (b_s @ a_s)).astype(np.float32)


def factor_stats(fac_f: dict, fac_t: dict) -> dict:
    """Artifact size for the FACTORS themselves (not the expanded product)."""
    trits, total = 0, 0
    for key in fac_t:
        b_t, a_t = fac_t[key]
        trits += int((b_t != 0).sum()) + int((a_t != 0).sum())
        total += b_t.size + a_t.size
    return {"factor_trits": trits, "factor_bits": trits * LOG2_3,
            "factor_params": total,
            "factor_sparsity": 1.0 - trits / max(total, 1)}


# ══════════════════════════════════════════════════════════════════════════
# Frozen scoring + verdict (pure; --validate exercises planted worlds)
# ══════════════════════════════════════════════════════════════════════════
def _g(a, b, rng, alpha, name):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    return gate(float(np.mean(a - b)), paired_permutation(a, b, rng),
                "greater", alpha, name=name)


def score(acc: dict, ce: dict, gh: dict, rng, alpha: float) -> dict:
    """acc[arm][split] = per-cell mean-over-seed correctness (aligned).
    Frozen TF1-TF3-TF5 for gd_cd_factors_ternary."""
    a3 = alpha / 3.0
    fac, base = "gd_cd_factors_ternary", "base"
    r = {}
    # TF1 wire-survives: factors > base, flip, both B1 and B2
    g1 = {}
    for sp in ("B1", "B2"):
        gg = _g(acc[fac][sp], acc[base][sp], rng, a3, f"TF1-{sp}")
        g1[sp] = {"gate": gg, "flip": bool(acc[fac][sp].mean()
                                           > acc[base][sp].mean())}
    r["TF1"] = bool(all(g1[sp]["gate"].verdict and g1[sp]["flip"]
                        for sp in ("B1", "B2")))
    r["TF1_detail"] = g1
    # TF2 not-lookup
    g2 = _g(acc[fac]["B2"], acc["construct_lookup"]["B2"], rng, a3, "TF2-B2")
    r["TF2"] = bool(g2.verdict)
    r["TF2_detail"] = g2
    # TF3 specificity: factors > factors_shuffle on held-out (B1+B2)
    held_f = np.concatenate([acc[fac]["B1"], acc[fac]["B2"]])
    held_s = np.concatenate([acc["gd_cd_factors_shuffle"]["B1"],
                             acc["gd_cd_factors_shuffle"]["B2"]])
    g3 = _g(held_f, held_s, rng, a3, "TF3-heldout")
    r["TF3"] = bool(g3.verdict)
    r["TF3_detail"] = g3
    # TF5 survive
    ce_ok = ce[fac] <= ce[base] * 1.02
    g_ok = gh[fac][0] >= gh[base][0] - 0.10
    h_ok = gh[fac][1] >= gh[base][1] - 0.10
    r["TF5"] = bool(ce_ok and g_ok and h_ok)
    r["TF5_detail"] = {"ce": ce[fac], "ce_base": ce[base],
                       "g_acc": gh[fac][0], "h_acc": gh[fac][1]}
    r["flip"] = bool(held_f.mean() > np.concatenate(
        [acc[base]["B1"], acc[base]["B2"]]).mean())
    return r


def verdict_of(gate0_ok: bool, r: dict, subtag: str = "") -> str:
    if not gate0_ok:
        return "VOID (gate-0)"
    if not r["TF5"]:
        return "HOST-DAMAGED"
    if r["TF1"] and r["TF2"] and r["TF3"]:
        return f"FACTORS-SURVIVE (+{subtag})" if subtag else "FACTORS-SURVIVE"
    if r["TF1"] and (not r["TF3"] or not r["TF2"]):
        return "FACTORS-DEGRADE"
    if not r["TF1"]:
        return "FACTORS-DIE"
    return "inconclusive"


# ══════════════════════════════════════════════════════════════════════════
# --validate (no model)
# ══════════════════════════════════════════════════════════════════════════
def run_validate(alpha: float) -> int:
    ok = True
    print("── §TERNARIZE-FACTORS-1 --validate (no model) ──")
    rng = np.random.default_rng(0)

    dout, din, r = 64, 48, 16
    b = rng.normal(size=(dout, r)).astype(np.float32)
    a = rng.normal(size=(r, din)).astype(np.float32)
    scale = 2.0

    # 1. factor ternarize: per-component signs preserved, sane sparsity, delta finite
    delta, b_hat, a_hat = ternarize_factors(b, a, scale)
    b_sign = float((np.sign(b_hat[b_hat != 0]) == np.sign(b[b_hat != 0])).mean())
    a_sign = float((np.sign(a_hat[a_hat != 0]) == np.sign(a[a_hat != 0])).mean())
    b_levels = {round(x, 6) for col in range(r)
                for x in np.unique(np.abs(b_hat[:, col][b_hat[:, col] != 0]))}
    good = (b_sign == 1.0 and a_sign == 1.0 and np.isfinite(delta).all()
            and (b_hat != 0).any() and (a_hat != 0).any())
    print(f"[V] factor twn: B_sign {b_sign:.2f} A_sign {a_sign:.2f} "
          f"B_percol_levels~{len(b_levels)} {'OK' if good else 'FAIL'}")
    ok &= good

    # 2. per-component gamma: each B col has a single |value| (one gamma per rank dir)
    percol_single = all(
        len(np.unique(np.round(np.abs(b_hat[:, j][b_hat[:, j] != 0]), 6))) <= 1
        for j in range(r) if (b_hat[:, j] != 0).any())
    perrow_single = all(
        len(np.unique(np.round(np.abs(a_hat[i, :][a_hat[i, :] != 0]), 6))) <= 1
        for i in range(r) if (a_hat[i, :] != 0).any())
    good = percol_single and perrow_single
    print(f"[V] per-component gamma: B per-col {percol_single} A per-row "
          f"{perrow_single} {'OK' if good else 'FAIL'}")
    ok &= good

    # 3. factor size ≪ expanded product size (the lambda-smallest win)
    fac_trits = int((b_hat != 0).sum()) + int((a_hat != 0).sum())
    prod = td.ternarize_twn(scale * (b @ a))[0]
    prod_trits = int((prod != 0).sum())
    # at REAL FFN dims the ratio is ~100x; here (toy) just require strictly fewer
    good = fac_trits < prod_trits
    # sanity: at real dims factors are ~100x smaller
    real = 16 * (9728 + 2560)
    real_prod = 9728 * 2560
    ratio = real_prod / real
    print(f"[V] size: factor_trits {fac_trits} < product_trits {prod_trits}; "
          f"real-dim ratio ~{ratio:.0f}x {'OK' if good and ratio > 50 else 'FAIL'}")
    ok &= good and ratio > 50

    # 4. shuffle null: matched factor trit budget, destroys the product correlation
    d_sh = shuffle_factors(b_hat, a_hat, scale, np.random.default_rng(1))
    b_s = td.shuffle_plate(b_hat, np.random.default_rng(1))
    budget_ok = int((b_s != 0).sum()) == int((b_hat != 0).sum())
    corr = float(delta.ravel() @ d_sh.ravel()
                 / ((np.linalg.norm(delta) * np.linalg.norm(d_sh)) + 1e-12))
    good = budget_ok and abs(corr) < 0.5
    print(f"[V] shuffle: matched_budget={budget_ok} product_corr {corr:.3f} "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 5. factor_stats accounting
    st = factor_stats({(0, "g"): (b, a)}, {(0, "g"): (b_hat, a_hat)})
    good = (st["factor_trits"] == fac_trits
            and abs(st["factor_bits"] - fac_trits * LOG2_3) < 1e-6
            and 0.0 <= st["factor_sparsity"] <= 1.0)
    print(f"[V] stats: trits {st['factor_trits']} bits {st['factor_bits']:.0f} "
          f"sparsity {st['factor_sparsity']:.2f} {'OK' if good else 'FAIL'}")
    ok &= good

    # 6. verdict planted worlds (wide gaps -> logic, not power)
    def world(name, want, fac, base, shuf, lookup, ce_bad=False, gh_bad=False,
              subtag=""):
        rngw = np.random.default_rng(hash(name) & 0xFFFF)

        def arr(p, n=64):
            return (rngw.random(n) < p).astype(float)

        acc = {
            "base": {"TRAIN": arr(base[0]), "B1": arr(base[1]), "B2": arr(base[2])},
            "gd_cd_factors_ternary": {"TRAIN": arr(fac[0]), "B1": arr(fac[1]),
                                      "B2": arr(fac[2])},
            "gd_cd_factors_shuffle": {"TRAIN": arr(shuf[0]), "B1": arr(shuf[1]),
                                      "B2": arr(shuf[2])},
            "construct_lookup": {"TRAIN": arr(lookup[0]), "B1": arr(lookup[1]),
                                 "B2": arr(lookup[2])},
        }
        ce = {a: (1.10 if (ce_bad and a == "gd_cd_factors_ternary") else 1.0)
              for a in acc}
        gh = {a: ((0.5, 0.5) if (gh_bad and a == "gd_cd_factors_ternary")
                  else (0.95, 0.95)) for a in acc}
        rr = score(acc, ce, gh, np.random.default_rng(3), alpha)
        v = verdict_of(True, rr, subtag)
        hit = want in v
        print(f"[V] {name}-world -> {v} (want {want}) {'OK' if hit else 'FAIL'}")
        return hit

    ok &= world("survive", "FACTORS-SURVIVE",
                fac=(.95, .92, .95), base=(.2, .12, .3),
                shuf=(.2, .12, .2), lookup=(.27, .12, .35))
    ok &= world("degrade", "FACTORS-DEGRADE",
                fac=(.95, .92, .95), base=(.2, .12, .3),
                shuf=(.9, .9, .92), lookup=(.27, .12, .35))
    ok &= world("die", "FACTORS-DIE",
                fac=(.2, .12, .3), base=(.2, .12, .3),
                shuf=(.2, .12, .28), lookup=(.27, .12, .35))
    ok &= world("host-damaged", "HOST-DAMAGED",
                fac=(.95, .92, .95), base=(.2, .12, .3),
                shuf=(.2, .12, .2), lookup=(.27, .12, .35), ce_bad=True)

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
    band = list(range(round(wb.BAND[0] * n_layers),
                      round(wb.BAND[1] * n_layers) + 1))
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
    ns = {sp: sum(1 for c in valid if c.split == sp) for sp in SPLITS}
    res_frozen = json.loads((rec / "results.json").read_text())
    lookup_b2 = {x["landmark"]: x["correct"]
                 for x in res_frozen["arms"]["construct_lookup"]["seeds"][0]
                 if x["split"] == "B2"}
    print(f"[tf] {args.model_id} dev={dev} n_layers={n_layers} "
          f"band=L{band[0]}..L{band[-1]} valid={len(valid)} splits={ns} "
          f"seeds={args.seeds} steps={args.steps} gate0_ok={gate0_ok}", flush=True)

    if args.n_cells:                       # smoke cap (mechanics only)
        by = {sp: [c for c in valid if c.split == sp] for sp in SPLITS}
        valid = [c for sp in SPLITS for c in by[sp][:args.n_cells]]
        lookup_b2 = {c.landmark: lookup_b2.get(c.landmark, 0.0)
                     for c in valid if c.split == "B2"}
        print(f"[tf] SMOKE cap {args.n_cells}/split -> {len(valid)} cells")
    train_cells = [c for c in valid if c.split == "TRAIN"]

    countries = sorted(wb.BANK)
    caps = sorted({cap for cap, _ in wb.BANK.values()})
    tid_map, drop = {}, set()
    for w in wb.union_words():
        t = first_tid(w)
        clash = [x for x, tt in tid_map.items() if tt == t]
        if clash:
            drop.add(w)
            drop.update(clash)
        tid_map[w] = t
    union = {w: tid_map[w] for w in sorted(set(wb.union_words()) - drop)}

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
        tot, n = 0.0, 0
        for t in wb.CE_TEXTS:
            ids = tok(t, return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits
            lp = F.log_softmax(lo[0, :-1].float(), dim=-1)
            tgt = ids.input_ids[0, 1:]
            tot += float(-lp[torch.arange(len(tgt)), tgt].sum())
            n += len(tgt)
        return tot / max(n, 1)

    def gh_accs():
        g = [max(countries, key=lambda w: logits_last(
            wb.G_QUERY_PREFIX + wb.G_QUERY.format(lm=c.landmark))[first_tid(w)])
            == c.country for c in valid]
        h = [wb.first_word(max(caps, key=lambda w: logits_last(
            wb.CAP_PREFIX + wb.CAP_QUERY.format(x=co))[first_tid(w)]))
            == wb.first_word(wb.BANK[co][0]) for co in sorted(wb.BANK)]
        return float(np.mean(g)), float(np.mean(h))

    def teacher_probs() -> dict:
        out = {}
        for c in train_cells:
            lo = logits_last(wb.TEACHER_PROMPT.format(lm=c.landmark, c=c.country))
            out[c.landmark] = torch.softmax(
                torch.tensor(lo, dtype=torch.float32), dim=-1)
        return out

    # ── train gd_cd, extract the FACTORS {(layer,proj): (B, A, scale)} ──
    def train_extract_factors(tp, seed) -> dict:
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
        for step in range(args.steps):
            opt.zero_grad()
            lo = model(**batch).logits[:, -1, :].float()
            loss = -(tpv * F.log_softmax(lo, dim=-1)).sum(-1).mean()
            loss.backward()
            opt.step()
            if step % max(args.steps // 5, 1) == 0 or step == args.steps - 1:
                print(f"    step {step:4d} loss {float(loss.detach()):.4f}",
                      flush=True)
        fac = {}
        for (m, name, orig, lw, li) in wrapped:
            with torch.no_grad():
                fac[(li, name)] = (lw.B.float().cpu().numpy(),
                                   lw.A.float().cpu().numpy(),
                                   float(lw.scale))
            setattr(m, name, orig)      # unwrap
        return fac

    # saved originals -> apply/restore via copy_ (bit-exact, no bf16 add/sub drift,
    # no cross-arm contamination: every arm applies to the SAME clean base)
    orig_w = {(li, name): getattr(dec[li].mlp, name).weight.detach().clone()
              for li in band for name in ("gate_proj", "up_proj", "down_proj")}

    def apply_plate(deltas: dict):
        for (li, name), d in deltas.items():
            w = getattr(dec[li].mlp, name).weight
            add = torch.tensor(d, dtype=w.dtype, device=w.device)
            with torch.no_grad():
                w.copy_(orig_w[(li, name)] + add)

    def restore_plate():
        for (li, name), w0 in orig_w.items():
            with torch.no_grad():
                getattr(dec[li].mlp, name).weight.copy_(w0)

    def eval_arm(deltas):
        apply_plate(deltas)
        rows = eval_cells()
        ce = ce_innocents()
        gh = gh_accs()
        restore_plate()
        return rows, ce, gh

    # ══ run arms ══
    print("[tf] ── base ──", flush=True)
    base_rows = eval_cells()
    base_ce = ce_innocents()
    base_gh = gh_accs()
    for sp in SPLITS:
        print(f"    {sp}: acc "
              f"{np.mean([r['correct'] for r in base_rows if r['split']==sp]):.3f}")

    tp = teacher_probs()
    labels = ("gd_cd_float", "gd_cd_product_ternary",
              "gd_cd_factors_ternary", "gd_cd_factors_shuffle")
    arms = {"base": {"seeds": [base_rows], "ce": base_ce, "gh": base_gh}}
    for label in labels:
        arms[label] = {"seeds": [], "ce": [], "gh": []}
    prod_stats_seed, fac_stats_seed = [], []

    for s in range(args.seeds):
        seed = args.seed + s
        print(f"[tf] ── seed {s} (train gd_cd) ──", flush=True)
        fac = train_extract_factors(tp, seed)
        d_float = {k: (sc * (b_ @ a_)).astype(np.float32)
                   for k, (b_, a_, sc) in fac.items()}
        d_product = {k: td.ternarize_twn(d_float[k])[0] for k in fac}
        d_factors, bt, at = {}, {}, {}
        for k, (b_, a_, sc) in fac.items():
            dl, b_hat, a_hat = ternarize_factors(b_, a_, sc)
            d_factors[k] = dl
            bt[k], at[k] = b_hat, a_hat
        rng_sh = np.random.default_rng(1000 + seed)
        d_fshuf = {k: shuffle_factors(bt[k], at[k], fac[k][2], rng_sh)
                   for k in fac}
        prod_stats_seed.append(td.plate_stats(d_float, d_product))
        fac_stats_seed.append({
            **factor_stats({k: (fac[k][0], fac[k][1]) for k in fac},
                           {k: (bt[k], at[k]) for k in fac}),
            "mag_cos_factors": float(td.plate_stats(d_float, d_factors)
                                     ["mag_cos_pooled"])})
        for label, deltas in (("gd_cd_float", d_float),
                              ("gd_cd_product_ternary", d_product),
                              ("gd_cd_factors_ternary", d_factors),
                              ("gd_cd_factors_shuffle", d_fshuf)):
            rows, ce, gh = eval_arm(deltas)
            arms[label]["seeds"].append(rows)
            arms[label]["ce"].append(ce)
            arms[label]["gh"].append(gh)
            for sp in SPLITS:
                acc = np.mean([r["correct"] for r in rows if r["split"] == sp])
                print(f"    {label:24s} {sp}: acc {acc:.3f}", flush=True)
    for label in labels:
        arms[label]["ce"] = float(np.mean(arms[label]["ce"]))
        arms[label]["gh"] = tuple(np.mean(arms[label]["gh"], axis=0))
    arms["construct_lookup"] = {"b2": lookup_b2}

    # verify bit-exact restore
    max_dev = max(float((getattr(dec[li].mlp, name).weight.detach()
                         - orig_w[(li, name)]).abs().max())
                  for (li, name) in orig_w)
    print(f"[tf] restore check: max|W-W0| = {max_dev:.2e}", flush=True)

    # ══ frozen scoring ══
    order = {sp: [c.landmark for c in valid if c.split == sp] for sp in SPLITS}

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

    acc = {a: acc_arrays(a) for a in
           ("base", "gd_cd_float", "gd_cd_product_ternary",
            "gd_cd_factors_ternary", "gd_cd_factors_shuffle")}
    acc["construct_lookup"] = {
        "B2": np.array([lookup_b2[lm] for lm in order["B2"]]),
        "B1": np.zeros(len(order["B1"])), "TRAIN": np.zeros(len(order["TRAIN"])),
    }
    ce = {"base": base_ce, "gd_cd_factors_ternary": arms["gd_cd_factors_ternary"]["ce"]}
    gh = {"base": base_gh, "gd_cd_factors_ternary": arms["gd_cd_factors_ternary"]["gh"]}
    r = score(acc, ce, gh, np.random.default_rng(args.seed + 999), args.alpha)

    # advisory: retention factors vs product -> TF4 sub-tag
    def retention(label):
        out = {}
        for sp in SPLITS:
            f = acc["gd_cd_float"][sp].mean()
            out[sp] = float(acc[label][sp].mean() / f) if f > 1e-9 else None
        return out
    ret_fac = retention("gd_cd_factors_ternary")
    ret_prod = retention("gd_cd_product_ternary")
    held_fac = np.concatenate([acc["gd_cd_factors_ternary"]["B1"],
                               acc["gd_cd_factors_ternary"]["B2"]]).mean()
    held_prod = np.concatenate([acc["gd_cd_product_ternary"]["B1"],
                                acc["gd_cd_product_ternary"]["B2"]]).mean()
    subtag = "FACTORING-FREE" if held_fac >= held_prod - 1e-9 else "FACTORING-COSTS"
    v = verdict_of(gate0_ok, r, subtag if (r["TF1"] and r["TF2"] and r["TF3"])
                   else "")

    fstats = {k: float(np.mean([s[k] for s in fac_stats_seed]))
              for k in fac_stats_seed[0]}
    pstats = {k: float(np.mean([s[k] for s in prod_stats_seed]))
              for k in ("trits", "bits", "mag_cos_pooled", "sparsity")}
    fstats["size_ratio_product_over_factors"] = (
        pstats["trits"] / max(fstats["factor_trits"], 1))
    anchor = {sp: {a: float(acc[a][sp].mean()) for a in
                   ("base", "gd_cd_float", "gd_cd_product_ternary",
                    "gd_cd_factors_ternary", "gd_cd_factors_shuffle")}
              for sp in SPLITS}

    print(f"\n[tf] ════ VERDICT: {v} ════")
    print(f"  TF1={r['TF1']} TF2={r['TF2']} TF3={r['TF3']} TF5={r['TF5']} "
          f"subtag={subtag}")
    print(f"  retention factors={ret_fac} product={ret_prod}")
    print(f"  factor_trits={fstats['factor_trits']:.0f} "
          f"product_trits={pstats['trits']:.0f} "
          f"ratio={fstats['size_ratio_product_over_factors']:.0f}x "
          f"mag_cos_factors={fstats['mag_cos_factors']:.3f}")
    for sp in SPLITS:
        print(f"  {sp}: base {anchor[sp]['base']:.3f} float "
              f"{anchor[sp]['gd_cd_float']:.3f} product "
              f"{anchor[sp]['gd_cd_product_ternary']:.3f} factors "
              f"{anchor[sp]['gd_cd_factors_ternary']:.3f} shuf "
              f"{anchor[sp]['gd_cd_factors_shuffle']:.3f}")

    def _degate(o):
        if is_dataclass(o) and not isinstance(o, type):
            return asdict(o)
        if isinstance(o, dict):
            return {k: _degate(x) for k, x in o.items()}
        if isinstance(o, (list, tuple)):
            return [_degate(x) for x in o]
        return o

    scoring = {"gates": r, "verdict": v, "subtag": subtag,
               "retention_factors": ret_fac, "retention_product": ret_prod,
               "factor_stats": fstats, "product_stats": pstats, "anchor": anchor,
               "restore_max_dev": max_dev}
    payload = {"model_id": args.model_id, "config": vars(args), "band": band,
               "gate0": {"ok": gate0_ok, "splits": ns}, "arms": arms,
               "scoring": scoring}
    (out_dir / "results.json").write_text(
        json.dumps(_json_safe(_degate(payload)), indent=2))
    print(f"[tf] wrote {out_dir}/results.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-cells", type=int, default=0,
                    help="smoke: cap cells per split (mechanics only)")
    ap.add_argument("--record-dir", default="results/writeback-compile/qwen3-4b",
                    help="frozen s303 record: gate0.json + results.json")
    ap.add_argument("--out", default="results/ternarize-factors/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
