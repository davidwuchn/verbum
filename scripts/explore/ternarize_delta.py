#!/usr/bin/env python3
"""§TERNARIZE-DELTA-1 (EXP-1, STORAGE half) — does the gd_cd wire survive ternary?

Pre-reg: mementum/knowledge/explore/write-not-train-ternary-routing-deltas.md
§TERNARIZE-DELTA-1 (FROZEN s304, Michael-approved). Crush the s303 gd_cd linker
wire — a float rank-16 LoRA delta on a frozen base — to a per-column TWN ternary
plate {-1,0,+1}xgamma, merge it into the frozen base weights (a real delta-plate,
NOT a LoRA wrapper), and re-score the frozen G1-G5. If the wire survives, the
portable artifact exists: the wire = one small ternary plate on a frozen
evaluator (map-and-swap resident Lisp, training side).

Reuse (no fork, lambda one_way): imports writeback_compile as a module for
BANK / Cell / prompts / LoRALinear / constants; loads the frozen gate-0 valid
cells and the construct_lookup B2 baseline from the committed s303 record
(results/writeback-compile/qwen3-4b/) so cells are IDENTICAL to the gd_cd score.

Arms (one process, per-seed float delta -> its own ternary plate -> its shuffle):
  base                  : frozen host (must reproduce 0.200 / 0.125 / 0.545).
  gd_cd_float           : the float LoRA delta merged (ANCHOR: must reproduce
                          the frozen gd_cd ~1.000 / 0.938 / 1.000; else halt).
  gd_cd_ternary         : the SAME delta, TWN per-column ternarized, merged.
  gd_cd_ternary_shuffle : per-column row-permuted ternary plate (matched trit
                          count + matched per-column gamma) — the null, must fail.
  construct_lookup      : frozen materialized-view null (loaded), G2 baseline.

Ternarize (FROZEN, TWN Li&Liu 2016, per input column j of W_delta=scale*B*A):
  thr_j = 0.7 * mean_i |W[i,j]| ; trit = +-1 where |W[i,j]|>thr_j else 0 ;
  gamma_j = mean_{surviving} |W[i,j]| ; T[i,j] = gamma_j * sign(W) * mask.

Gates (verbum.dsp, paired permutation 10k, primaries Bonferroni alpha/3;
T1-T3 routing register, T5 value register):
  T1 WIRE-SURVIVES : gd_cd_ternary > base, flip on B1 AND B2.
  T2 NOT-LOOKUP    : gd_cd_ternary > construct_lookup on B2.
  T3 SPECIFICITY   : gd_cd_ternary > gd_cd_ternary_shuffle on held-out (B1+B2).
  T5 SURVIVE       : innocent CE <= 2% rel base; native g/h within 0.10 abs.
Reports (advisory): mag_cos(float,ternary) (expect LOW ~0.7); retention
  (ternary/float acc per split); trits / bits / sparsity (artifact size).
Verdicts: SURVIVES-TERNARY (T1&T2&T3&T5) / DEGRADES-TERNARY (T1, ~T3 or ~T2) /
  DIES-TERNARY (~T1) / HOST-DAMAGED (~T5).

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

import writeback_compile as wb  # noqa: E402  (module reuse, no fork)
from holo_frag import _json_safe  # noqa: E402

from verbum.dsp import gate, paired_permutation  # noqa: E402

SPLITS = wb.SPLITS
TERN_THR = 0.7          # frozen TWN threshold factor
LOG2_3 = float(np.log2(3.0))


# ══════════════════════════════════════════════════════════════════════════
# Ternarize (TWN, per input column) + matched-sparsity shuffle null
# ══════════════════════════════════════════════════════════════════════════
def ternarize_twn(w: np.ndarray, thr: float = TERN_THR):
    """w: (d_out, d_in) float delta. Returns (T, mask, gamma) with per-column
    (axis=0 over output rows i, for fixed input column j) threshold+scale."""
    absw = np.abs(w)
    thr_j = thr * absw.mean(axis=0, keepdims=True)         # (1, d_in)
    mask = absw > thr_j                                    # (d_out, d_in) bool
    col_sum = (absw * mask).sum(axis=0)                    # (d_in,)
    col_cnt = mask.sum(axis=0)                             # (d_in,)
    gamma = np.where(col_cnt > 0, col_sum / np.maximum(col_cnt, 1), 0.0)
    t = np.sign(w) * mask * gamma[None, :]
    return t.astype(np.float32), mask, gamma.astype(np.float32)


def shuffle_plate(t: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Per-column row-permutation: preserves each column's ternary multiset
    exactly (matched trit count AND matched per-column gamma), destroys the
    output-row routing geometry. The lambda-yardstick null."""
    out = np.empty_like(t)
    d_out = t.shape[0]
    for j in range(t.shape[1]):
        out[:, j] = t[rng.permutation(d_out), j]
    return out


def plate_stats(deltas_f: dict, deltas_t: dict) -> dict:
    """Advisory reports: pooled + per-proj magnitude cosine, trit count/bits,
    sparsity."""
    cos_pp, trits, total = {}, 0, 0
    fv, tv = [], []
    for key in deltas_f:
        f = deltas_f[key].ravel()
        t = deltas_t[key].ravel()
        nz = int((t != 0).sum())
        trits += nz
        total += t.size
        denom = (np.linalg.norm(f) * np.linalg.norm(t)) + 1e-12
        cos_pp[f"{key[0]}:{key[1]}"] = float(f @ t / denom)
        fv.append(f)
        tv.append(t)
    fa = np.concatenate(fv)
    ta = np.concatenate(tv)
    pooled = float(fa @ ta / ((np.linalg.norm(fa) * np.linalg.norm(ta)) + 1e-12))
    return {"mag_cos_pooled": pooled, "mag_cos_per_proj": cos_pp,
            "trits": trits, "bits": trits * LOG2_3,
            "params": total, "sparsity": 1.0 - trits / max(total, 1)}


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
    ce[arm], gh[arm]=(g,h). Frozen T1-T3-T5 for gd_cd_ternary."""
    a3 = alpha / 3.0
    tern, base = "gd_cd_ternary", "base"
    r = {}
    # T1 wire-survives: tern > base, flip, both B1 and B2
    g1 = {}
    for sp in ("B1", "B2"):
        gg = _g(acc[tern][sp], acc[base][sp], rng, a3, f"T1-{sp}")
        g1[sp] = {"gate": gg, "flip": bool(acc[tern][sp].mean()
                                           > acc[base][sp].mean())}
    r["T1"] = bool(all(g1[sp]["gate"].verdict and g1[sp]["flip"]
                       for sp in ("B1", "B2")))
    r["T1_detail"] = g1
    # T2 not-lookup: tern > construct_lookup on B2
    g2 = _g(acc[tern]["B2"], acc["construct_lookup"]["B2"], rng, a3, "T2-B2")
    r["T2"] = bool(g2.verdict)
    r["T2_detail"] = g2
    # T3 specificity: tern > shuffle on held-out (B1+B2)
    held_t = np.concatenate([acc[tern]["B1"], acc[tern]["B2"]])
    held_s = np.concatenate([acc["gd_cd_ternary_shuffle"]["B1"],
                             acc["gd_cd_ternary_shuffle"]["B2"]])
    g3 = _g(held_t, held_s, rng, a3, "T3-heldout")
    r["T3"] = bool(g3.verdict)
    r["T3_detail"] = g3
    # T5 survive
    ce_ok = ce[tern] <= ce[base] * 1.02
    g_ok = gh[tern][0] >= gh[base][0] - 0.10
    h_ok = gh[tern][1] >= gh[base][1] - 0.10
    r["T5"] = bool(ce_ok and g_ok and h_ok)
    r["T5_detail"] = {"ce": ce[tern], "ce_base": ce[base],
                      "g_acc": gh[tern][0], "h_acc": gh[tern][1]}
    r["flip"] = bool(held_t.mean() > np.concatenate(
        [acc[base]["B1"], acc[base]["B2"]]).mean())
    return r


def verdict_of(gate0_ok: bool, r: dict) -> str:
    if not gate0_ok:
        return "VOID (gate-0)"
    if not r["T5"]:
        return "HOST-DAMAGED"
    if r["T1"] and r["T2"] and r["T3"]:
        return "SURVIVES-TERNARY"
    if r["T1"] and (not r["T3"] or not r["T2"]):
        return "DEGRADES-TERNARY"
    if not r["T1"]:
        return "DIES-TERNARY"
    return "inconclusive"


# ══════════════════════════════════════════════════════════════════════════
# --validate (no model)
# ══════════════════════════════════════════════════════════════════════════
def run_validate(alpha: float) -> int:
    ok = True
    print("── §TERNARIZE-DELTA-1 --validate (no model) ──")

    rng = np.random.default_rng(0)

    # 1. TWN: a strong-signal low-rank matrix ternarizes with a sane sparsity
    #    and preserves sign structure; mag_cos is moderate (<1, >0).
    dout, din, r = 64, 48, 16
    b = rng.normal(size=(dout, r))
    a = rng.normal(size=(r, din))
    w = 2.0 * (b @ a)                                      # scale*B*A shape
    t, mask, gamma = ternarize_twn(w)
    sign_match = float((np.sign(t[mask]) == np.sign(w[mask])).mean())
    spars = 1.0 - mask.mean()
    cos = float(w.ravel() @ t.ravel()
                / ((np.linalg.norm(w) * np.linalg.norm(t)) + 1e-12))
    good = (mask.any() and 0.0 < spars < 1.0 and sign_match == 1.0
            and 0.0 < cos < 1.0 and (gamma[mask.any(axis=0)] > 0).all())
    print(f"[V] twn: sparsity {spars:.2f} sign_match {sign_match:.2f} "
          f"mag_cos {cos:.3f} {'OK' if good else 'FAIL'}")
    ok &= good

    # 2. shuffle preserves per-column ternary multiset (matched trits+gamma),
    #    changes arrangement, and destroys correlation with the original.
    sh = shuffle_plate(t, rng)
    col_ok = all(sorted(t[:, j].tolist()) == sorted(sh[:, j].tolist())
                 for j in range(t.shape[1]))
    moved = float((sh != t).any(axis=0).mean())            # cols that changed
    corr = float(t.ravel() @ sh.ravel()
                 / ((np.linalg.norm(t) * np.linalg.norm(sh)) + 1e-12))
    good = col_ok and moved > 0.5 and corr < 0.5
    print(f"[V] shuffle: col_multiset_preserved={col_ok} moved_frac {moved:.2f} "
          f"corr {corr:.3f} {'OK' if good else 'FAIL'}")
    ok &= good

    # 3. plate_stats: trit count = nonzeros, bits = trits*log2(3).
    st = plate_stats({(0, "gate_proj"): w}, {(0, "gate_proj"): t})
    good = (st["trits"] == int((t != 0).sum())
            and abs(st["bits"] - st["trits"] * LOG2_3) < 1e-6
            and 0.0 <= st["sparsity"] <= 1.0)
    print(f"[V] stats: trits {st['trits']} bits {st['bits']:.0f} "
          f"sparsity {st['sparsity']:.2f} {'OK' if good else 'FAIL'}")
    ok &= good

    # 4. verdict planted worlds (n large + clean separation: this tests
    #    verdict LOGIC, not statistical power — the real run has base B2=0.545
    #    vs ternary~1.0, a wide gap)
    def world(name, want, tern, base, shuf, lookup, ce_bad=False, gh_bad=False):
        rngw = np.random.default_rng(hash(name) & 0xFFFF)

        def arr(p, n=64):
            return (rngw.random(n) < p).astype(float)

        acc = {
            "base": {"TRAIN": arr(base[0]), "B1": arr(base[1]),
                     "B2": arr(base[2])},
            "gd_cd_ternary": {"TRAIN": arr(tern[0]), "B1": arr(tern[1]),
                              "B2": arr(tern[2])},
            "gd_cd_ternary_shuffle": {"TRAIN": arr(shuf[0]), "B1": arr(shuf[1]),
                                      "B2": arr(shuf[2])},
            "construct_lookup": {"TRAIN": arr(lookup[0]), "B1": arr(lookup[1]),
                                 "B2": arr(lookup[2])},
        }
        ce = {a: (1.10 if (ce_bad and a == "gd_cd_ternary") else 1.0)
              for a in acc}
        gh = {a: ((0.5, 0.5) if (gh_bad and a == "gd_cd_ternary")
                  else (0.95, 0.95)) for a in acc}
        r = score(acc, ce, gh, np.random.default_rng(3), alpha)
        v = verdict_of(True, r)
        hit = want in v
        print(f"[V] {name}-world -> {v} (want {want}) "
              f"{'OK' if hit else 'FAIL'}")
        return hit

    # (TRAIN, B1, B2) success probs (wide gaps → logic, not power)
    ok &= world("survives", "SURVIVES-TERNARY",
                tern=(.95, .92, .95), base=(.2, .12, .3),
                shuf=(.2, .12, .2), lookup=(.27, .12, .35))
    ok &= world("degrades", "DEGRADES-TERNARY",
                tern=(.95, .92, .95), base=(.2, .12, .3),
                shuf=(.9, .9, .92), lookup=(.27, .12, .35))
    ok &= world("dies", "DIES-TERNARY",
                tern=(.2, .12, .3), base=(.2, .12, .3),
                shuf=(.2, .12, .28), lookup=(.27, .12, .35))
    ok &= world("host-damaged", "HOST-DAMAGED",
                tern=(.95, .92, .95), base=(.2, .12, .3),
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
    print(f"[td] {args.model_id} dev={dev} n_layers={n_layers} "
          f"band=L{band[0]}..L{band[-1]} valid={len(valid)} splits={ns} "
          f"seeds={args.seeds} steps={args.steps} gate0_ok={gate0_ok}")

    if args.n_cells:                       # smoke cap (mechanics only)
        by = {sp: [c for c in valid if c.split == sp] for sp in SPLITS}
        valid = [c for sp in SPLITS for c in by[sp][:args.n_cells]]
        lookup_b2 = {c.landmark: lookup_b2.get(c.landmark, 0.0)
                     for c in valid if c.split == "B2"}
        print(f"[td] SMOKE cap {args.n_cells}/split -> {len(valid)} cells")
    train_cells = [c for c in valid if c.split == "TRAIN"]

    # ── union candidate set (recompute; assert == frozen drop) ──
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
        print(f"[td] WARN union drop drift: {sorted(drop)} vs frozen "
              f"{g0.get('union_dropped')}")

    countries = sorted(wb.BANK)
    caps = sorted({cap for cap, _ in wb.BANK.values()})

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

    # ── train gd_cd, extract the float delta {(layer,proj): scale*B*A} ──
    def teacher_probs() -> dict:
        out = {}
        for c in train_cells:
            lo = logits_last(wb.TEACHER_PROMPT.format(lm=c.landmark,
                                                      c=c.country))
            out[c.landmark] = torch.softmax(
                torch.tensor(lo, dtype=torch.float32), dim=-1)
        return out

    def train_extract(tp, seed) -> dict:
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
        deltas = {}
        for (m, name, orig, lw, li) in wrapped:
            with torch.no_grad():
                deltas[(li, name)] = (lw.scale * (lw.B @ lw.A)
                                      ).float().cpu().numpy()
            setattr(m, name, orig)      # unwrap
        return deltas

    # ── merge a delta-plate into the frozen base, then restore exactly ──
    def apply_plate(deltas: dict) -> dict:
        added = {}
        for (li, name), d in deltas.items():
            w = getattr(dec[li].mlp, name).weight
            add = torch.tensor(d, dtype=w.dtype, device=w.device)
            with torch.no_grad():
                w.add_(add)
            added[(li, name)] = add
        return added

    def restore_plate(added: dict):
        for (li, name), add in added.items():
            with torch.no_grad():
                getattr(dec[li].mlp, name).weight.sub_(add)

    def eval_arm(deltas):
        added = apply_plate(deltas)
        rows = eval_cells()
        ce = ce_innocents()
        gh = gh_accs()
        restore_plate(added)
        return rows, ce, gh

    # ══ run arms ══
    print("[td] ── base ──")
    base_rows = eval_cells()
    base_ce = ce_innocents()
    base_gh = gh_accs()
    for sp in SPLITS:
        print(f"    {sp}: acc "
              f"{np.mean([r['correct'] for r in base_rows if r['split']==sp]):.3f}")

    tp = teacher_probs()
    arms = {"base": {"seeds": [base_rows], "ce": base_ce, "gh": base_gh}}
    for label in ("gd_cd_float", "gd_cd_ternary", "gd_cd_ternary_shuffle"):
        arms[label] = {"seeds": [], "ce": [], "gh": []}
    stats_per_seed = []
    for s in range(args.seeds):
        seed = args.seed + s
        print(f"[td] ── seed {s} (train gd_cd) ──")
        d_float = train_extract(tp, seed)
        d_tern = {k: ternarize_twn(v)[0] for k, v in d_float.items()}
        rng_sh = np.random.default_rng(1000 + seed)
        d_shuf = {k: shuffle_plate(v, rng_sh) for k, v in d_tern.items()}
        stats_per_seed.append(plate_stats(d_float, d_tern))
        for label, deltas in (("gd_cd_float", d_float),
                              ("gd_cd_ternary", d_tern),
                              ("gd_cd_ternary_shuffle", d_shuf)):
            rows, ce, gh = eval_arm(deltas)
            arms[label]["seeds"].append(rows)
            arms[label]["ce"].append(ce)
            arms[label]["gh"].append(gh)
            for sp in SPLITS:
                acc = np.mean([r["correct"] for r in rows if r["split"] == sp])
                print(f"    {label:22s} {sp}: acc {acc:.3f}")
    for label in ("gd_cd_float", "gd_cd_ternary", "gd_cd_ternary_shuffle"):
        arms[label]["ce"] = float(np.mean(arms[label]["ce"]))
        arms[label]["gh"] = tuple(np.mean(arms[label]["gh"], axis=0))

    # construct_lookup (frozen, single "seed" = the committed record)
    arms["construct_lookup"] = {"b2": lookup_b2}

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

    acc = {a: acc_arrays(a) for a in ("base", "gd_cd_float", "gd_cd_ternary",
                                      "gd_cd_ternary_shuffle")}
    acc["construct_lookup"] = {
        "B2": np.array([lookup_b2[lm] for lm in order["B2"]]),
        "B1": np.zeros(len(order["B1"])), "TRAIN": np.zeros(len(order["TRAIN"])),
    }
    ce = {"base": base_ce, "gd_cd_ternary": arms["gd_cd_ternary"]["ce"]}
    gh = {"base": base_gh, "gd_cd_ternary": arms["gd_cd_ternary"]["gh"]}
    r = score(acc, ce, gh, np.random.default_rng(args.seed + 999), args.alpha)
    v = verdict_of(gate0_ok, r)

    # advisory reports
    retention = {}
    for sp in SPLITS:
        f = acc["gd_cd_float"][sp].mean()
        retention[sp] = float(acc["gd_cd_ternary"][sp].mean()
                              / f) if f > 1e-9 else None
    stats = {k: float(np.mean([s[k] for s in stats_per_seed]))
             for k in ("mag_cos_pooled", "trits", "bits", "params", "sparsity")}
    anchor = {sp: {"float": float(acc["gd_cd_float"][sp].mean()),
                   "ternary": float(acc["gd_cd_ternary"][sp].mean()),
                   "base": float(acc["base"][sp].mean())} for sp in SPLITS}

    print(f"\n[td] ════ VERDICT: {v} ════")
    print(f"  T1={r['T1']} T2={r['T2']} T3={r['T3']} T5={r['T5']}")
    print(f"  mag_cos_pooled={stats['mag_cos_pooled']:.3f} "
          f"trits={stats['trits']:.0f} sparsity={stats['sparsity']:.3f}")
    print(f"  retention={retention}")
    for sp in SPLITS:
        print(f"  {sp}: base {anchor[sp]['base']:.3f} float "
              f"{anchor[sp]['float']:.3f} ternary {anchor[sp]['ternary']:.3f}")

    def _degate(o):
        """Recursively convert Gated (and any dataclass) for JSON dump."""
        if is_dataclass(o) and not isinstance(o, type):
            return asdict(o)
        if isinstance(o, dict):
            return {k: _degate(x) for k, x in o.items()}
        if isinstance(o, (list, tuple)):
            return [_degate(x) for x in o]
        return o

    scoring = {"gates": r, "verdict": v, "retention": retention,
               "plate_stats": stats, "anchor": anchor}
    payload = {"model_id": args.model_id, "config": vars(args),
               "band": band, "gate0": {"ok": gate0_ok, "splits": ns},
               "arms": arms, "scoring": scoring}
    (out_dir / "results.json").write_text(
        json.dumps(_json_safe(_degate(payload)), indent=2))
    print(f"[td] wrote {out_dir}/results.json")
    return 0


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
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-cells", type=int, default=0,
                    help="smoke: cap cells per split (mechanics only)")
    ap.add_argument("--record-dir",
                    default="results/writeback-compile/qwen3-4b",
                    help="frozen s303 record: gate0.json + results.json")
    ap.add_argument("--out", default="results/ternarize-delta/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
