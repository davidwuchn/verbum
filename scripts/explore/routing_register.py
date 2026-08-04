#!/usr/bin/env python3
"""§ROUTING-REGISTER-1 (EXP-2, the FINDING half) — write the wire, no gradient.

Pre-reg: mementum/knowledge/explore/write-not-train-ternary-routing-deltas.md
§ROUTING-REGISTER-1 (FROZEN s304, Michael-approved). Can the operand→capital
linker be WRITTEN (closed-form, no gradient, no calibration loop) as a ternary
bind-plate on the frozen base, installing a WIRE (generalizes to held-out
landmarks AND held-out countries)?

`construct` went INERT (byte-identical to base) because it wrote the MAGNITUDE
register: a continuous product-keyed neuron with a calibrated gain that throttled
to ≈0.3. The country key FIRED (s294: the landmark's latent country-ness triggers
the whitened filter); the throttled value write never installed the edge. Fix:
keep the MEASURED key as a faithful address, write the value in the ROUTING
register — ternary sign, register-matched full strength (S = median native
down_proj column norm at L23), NO gain calibration.

Write recipe (FROZEN, no gradient): at install layer L23 (INSTALL_DEPTH 0.65 * 36;
Qwen3-4B = 36 layers, band L22-L29), append one FFN neuron per country c (all 16;
the sum of key-bind-value realized as parallel FFN neurons; the bind is the FFN
key->value neuron structure, NOT literal circular convolution):
  address (gate/up rows) = measured whitened country filter k_c (build_keys,
    shared-Sigma; normalized gate=(4/ref)k, up=(1/ref)k, the proven firing rule)
  content (down col)     = S * ternary(v_c)/norm(ternary(v_c)) ; v_c = capital
    unembed direction; ternary = per-element TWN {-1,0,+1} thr 0.7; S = median
    native down_proj column L2-norm at L23 (host-register scale, NOT a tuned target)

Arms (deterministic write; re-scored on the frozen s303 gate-0 valid cells):
  base             : floor (0.200 / 0.125 / 0.545).
  routing_write    : the ternary bind-plate, all 16 countries.
  routing_shuffle  : deranged capital values (v_c → v_{π(c)}), same keys+S+sparsity
                     — the null (λ yardstick); must fail. ≥3 derangement seeds.
  construct_lookup : frozen materialized-view null (loaded), G2 baseline.

Gates (verbum.dsp paired-perm 10k, primaries Bonferroni alpha/3):
  G1 WIRE       : routing_write > base, flip on B1 AND B2.
  G2 NOT-LOOKUP : routing_write > construct_lookup on B2.
  G3 SPECIFICITY: routing_write > routing_shuffle on held-out (B1+B2).
  G5 SURVIVE    : innocent CE <= 2% rel base; native g/h within 0.10 abs.
Reports (advisory): achieved capital-logit boost on country frames (did the write
  LAND vs construct's 0.3 throttle?); trits/bits/sparsity (λ smallest); per-country
  key separation own_ref - inn_max (attribute an INERT verdict: weak-write vs
  no-routing).
Verdicts: WRITE-SUFFICES (G1∧G2∧G3∧G5 → thesis confirmed, never train the parent)
  / WRITE-DEGRADES (G1, ¬G3 or ¬G2) / WRITE-INERT (¬G1 → gradient-finds/
  ternary-stores) / HOST-DAMAGED (¬G5).

Cadence: --validate (no model) → smoke (--n-cells, mechanics only) → Michael GO
→ run → frozen scoring.

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

import writeback_compile as wb  # noqa: E402  (module reuse, no fork)
from holo_frag import _json_safe  # noqa: E402

from verbum.dsp import gate, paired_permutation  # noqa: E402

SPLITS = wb.SPLITS
TERN_THR = 0.7
LOG2_3 = float(np.log2(3.0))


# ══════════════════════════════════════════════════════════════════════════
# Ternarize a VALUE vector (per-element TWN) + derangement
# ══════════════════════════════════════════════════════════════════════════
def ternarize_vec(v: np.ndarray, thr: float = TERN_THR):
    """Per-element TWN ternary on a vector. Returns (t, mask, gamma)."""
    absv = np.abs(v)
    theta = thr * absv.mean()
    mask = absv > theta
    gamma = float(absv[mask].mean()) if mask.any() else 0.0
    t = np.sign(v) * mask * gamma
    return t.astype(np.float32), mask, gamma


def unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


# ══════════════════════════════════════════════════════════════════════════
# Frozen scoring + verdict (pure; --validate exercises planted worlds)
# ══════════════════════════════════════════════════════════════════════════
def _g(a, b, rng, alpha, name):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    return gate(float(np.mean(a - b)), paired_permutation(a, b, rng),
                "greater", alpha, name=name)


def score(acc: dict, ce: dict, gh: dict, rng, alpha: float) -> dict:
    a3 = alpha / 3.0
    arm, base = "routing_write", "base"
    r = {}
    g1 = {}
    for sp in ("B1", "B2"):
        gg = _g(acc[arm][sp], acc[base][sp], rng, a3, f"G1-{sp}")
        g1[sp] = {"gate": gg, "flip": bool(acc[arm][sp].mean()
                                           > acc[base][sp].mean())}
    r["G1"] = bool(all(g1[sp]["gate"].verdict and g1[sp]["flip"]
                       for sp in ("B1", "B2")))
    r["G1_detail"] = g1
    g2 = _g(acc[arm]["B2"], acc["construct_lookup"]["B2"], rng, a3, "G2-B2")
    r["G2"] = bool(g2.verdict)
    r["G2_detail"] = g2
    held = np.concatenate([acc[arm]["B1"], acc[arm]["B2"]])
    held_s = np.concatenate([acc["routing_shuffle"]["B1"],
                             acc["routing_shuffle"]["B2"]])
    g3 = _g(held, held_s, rng, a3, "G3-heldout")
    r["G3"] = bool(g3.verdict)
    r["G3_detail"] = g3
    ce_ok = ce[arm] <= ce[base] * 1.02
    g_ok = gh[arm][0] >= gh[base][0] - 0.10
    h_ok = gh[arm][1] >= gh[base][1] - 0.10
    r["G5"] = bool(ce_ok and g_ok and h_ok)
    r["G5_detail"] = {"ce": ce[arm], "ce_base": ce[base],
                      "g_acc": gh[arm][0], "h_acc": gh[arm][1]}
    r["held_up"] = bool(held.mean() > np.concatenate(
        [acc[base]["B1"], acc[base]["B2"]]).mean())
    return r


def verdict_of(gate0_ok: bool, r: dict) -> str:
    if not gate0_ok:
        return "VOID (gate-0)"
    if not r["G5"]:
        return "HOST-DAMAGED"
    if r["G1"] and r["G2"] and r["G3"]:
        return "WRITE-SUFFICES"
    if r["G1"] and (not r["G3"] or not r["G2"]):
        return "WRITE-DEGRADES"
    if not r["G1"]:
        return "WRITE-INERT"
    return "inconclusive"


# ══════════════════════════════════════════════════════════════════════════
# --validate (no model)
# ══════════════════════════════════════════════════════════════════════════
def run_validate(alpha: float) -> int:
    ok = True
    print("── §ROUTING-REGISTER-1 --validate (no model) ──")
    rng = np.random.default_rng(0)

    # 1. ternarize_vec: sane sparsity, sign preserved
    v = rng.normal(size=2560)
    t, mask, gamma = ternarize_vec(v)
    sign_ok = float((np.sign(t[mask]) == np.sign(v[mask])).mean())
    spars = 1.0 - mask.mean()
    good = mask.any() and 0.0 < spars < 1.0 and sign_ok == 1.0 and gamma > 0
    print(f"[V] ternarize_vec: sparsity {spars:.2f} sign_ok {sign_ok:.2f} "
          f"gamma {gamma:.3f} {'OK' if good else 'FAIL'}")
    ok &= good

    # 2. neuron surgery equivalence (tiny SwiGLU) — append/restore correctness
    import torch
    import torch.nn.functional as F
    torch.manual_seed(0)
    dm, ff = 16, 32
    gp = torch.nn.Linear(dm, ff, bias=False)
    up = torch.nn.Linear(dm, ff, bias=False)
    dn = torch.nn.Linear(ff, dm, bias=False)

    def mlp(x):
        return dn(F.silu(gp(x)) * up(x))

    key = unit(rng.normal(size=dm).astype(np.float32))
    val = rng.normal(size=dm).astype(np.float32)
    ref = 2.0
    x_on = torch.tensor(ref * key)
    x_off = x_on - float(x_on @ torch.tensor(key)) * torch.tensor(key)
    base_on, base_off = mlp(x_on), mlp(x_off)
    kt = torch.tensor(key)
    with torch.no_grad():
        gp.weight = torch.nn.Parameter(torch.cat(
            [gp.weight, ((4.0 / ref) * kt)[None, :]]))
        up.weight = torch.nn.Parameter(torch.cat(
            [up.weight, ((1.0 / ref) * kt)[None, :]]))
        dn.weight = torch.nn.Parameter(torch.cat(
            [dn.weight, torch.tensor(val)[:, None]], dim=1))
    r = float(x_on @ kt)
    want = base_on + F.silu(torch.tensor(4.0 * r / ref)) * (r / ref) \
        * torch.tensor(val)
    with torch.no_grad():
        e_on = float((mlp(x_on) - want).abs().max())
        e_off = float((mlp(x_off) - base_off).abs().max())
    good = e_on < 1e-4 and e_off < 1e-4
    print(f"[V] surgery: on-err {e_on:.2e} off-err {e_off:.2e} "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 3. derangement no fixed point
    d = wb.derangement(sorted(wb.BANK), np.random.default_rng(1))
    good = all(k != x for k, x in d.items()) and set(d.values()) == set(wb.BANK)
    print(f"[V] derangement: {'OK' if good else 'FAIL'}")
    ok &= good

    # 4. S = median native column norm
    w = rng.normal(size=(dm, ff))
    s = float(np.median(np.linalg.norm(w, axis=0)))
    good = s > 0 and abs(s - np.median(np.linalg.norm(w, axis=0))) < 1e-9
    print(f"[V] S median col-norm {s:.3f} {'OK' if good else 'FAIL'}")
    ok &= good

    # 5. verdict planted worlds
    def world(name, want, wr, base, shuf, lookup, ce_bad=False, gh_bad=False):
        rngw = np.random.default_rng(hash(name) & 0xFFFF)

        def arr(p, n=64):
            return (rngw.random(n) < p).astype(float)

        acc = {
            "base": {"TRAIN": arr(base[0]), "B1": arr(base[1]),
                     "B2": arr(base[2])},
            "routing_write": {"TRAIN": arr(wr[0]), "B1": arr(wr[1]),
                              "B2": arr(wr[2])},
            "routing_shuffle": {"TRAIN": arr(shuf[0]), "B1": arr(shuf[1]),
                                "B2": arr(shuf[2])},
            "construct_lookup": {"TRAIN": arr(lookup[0]), "B1": arr(lookup[1]),
                                 "B2": arr(lookup[2])},
        }
        ce = {a: (1.10 if (ce_bad and a == "routing_write") else 1.0)
              for a in acc}
        gh = {a: ((0.5, 0.5) if (gh_bad and a == "routing_write")
                  else (0.95, 0.95)) for a in acc}
        r = score(acc, ce, gh, np.random.default_rng(3), alpha)
        v = verdict_of(True, r)
        hit = want in v
        print(f"[V] {name}-world -> {v} (want {want}) {'OK' if hit else 'FAIL'}")
        return hit

    ok &= world("suffices", "WRITE-SUFFICES",
                wr=(.95, .92, .95), base=(.2, .12, .3),
                shuf=(.2, .12, .2), lookup=(.27, .12, .35))
    ok &= world("degrades", "WRITE-DEGRADES",
                wr=(.95, .92, .95), base=(.2, .12, .3),
                shuf=(.9, .9, .92), lookup=(.27, .12, .35))
    ok &= world("inert", "WRITE-INERT",
                wr=(.2, .12, .3), base=(.2, .12, .3),
                shuf=(.2, .12, .28), lookup=(.27, .12, .35))
    ok &= world("host-damaged", "HOST-DAMAGED",
                wr=(.95, .92, .95), base=(.2, .12, .3),
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
    dec, _norm, lm_head = mh3.resolve_parts(model)
    n_layers = len(dec)
    li = round(wb.INSTALL_DEPTH * n_layers)
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
    print(f"[rr] {args.model_id} dev={dev} n_layers={n_layers} install=L{li} "
          f"valid={len(valid)} splits={ns} shuffle_seeds={args.seeds} "
          f"gate0_ok={gate0_ok}")

    if args.n_cells:                       # smoke cap (mechanics only)
        by = {sp: [c for c in valid if c.split == sp] for sp in SPLITS}
        valid = [c for sp in SPLITS for c in by[sp][:args.n_cells]]
        lookup_b2 = {c.landmark: lookup_b2.get(c.landmark, 0.0)
                     for c in valid if c.split == "B2"}
        print(f"[rr] SMOKE cap {args.n_cells}/split -> {len(valid)} cells")

    # ── union candidate set ──
    tid_map, drop = {}, set()
    for w in wb.union_words():
        t = first_tid(w)
        clash = [x for x, tt in tid_map.items() if tt == t]
        if clash:
            drop.add(w)
            drop.update(clash)
        tid_map[w] = t
    union = {w: tid_map[w] for w in sorted(set(wb.union_words()) - drop)}

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

    # ── post-norm capture + whitened country keys (build_keys, re-impl) ──
    def capture_postnorm(prompts: list[str]) -> np.ndarray:
        vecs = []
        for p in prompts:
            store = {}
            hnd = dec[li].post_attention_layernorm.register_forward_hook(
                lambda m, i, o, s=store: s.__setitem__("v", o))
            ids = tok(p, return_tensors="pt").to(dev)
            with torch.no_grad():
                model(**ids)
            hnd.remove()
            vecs.append(store["v"][0, -1, :].float().cpu().numpy())
        return np.stack(vecs)

    def build_keys(specs: dict[str, list[str]]) -> dict:
        inn_prompts = list(wb.PROSE_INNOCENTS) + [
            wb.DIRECT_PROMPT.format(lm=nc) for nc in wb.NONCE_CANDS[:3]]
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
            k = unit(k)
            keys[name] = {"k": k, "ref": float(np.mean(own @ k)),
                          "inn_max": float(np.max(inn @ k))}
            seps.append(keys[name]["ref"] - keys[name]["inn_max"])
        print(f"[rr] keys({len(keys)}): own-inn separation min {min(seps):.2f} "
              f"median {float(np.median(seps)):.2f}")
        return keys

    def unembed_dir(word: str) -> np.ndarray:
        v = lm_head.weight[first_tid(word)].float().cpu().numpy()
        return unit(v)

    # ── neuron surgery (append/restore; validated pattern) ──
    mlp = dec[li].mlp
    ff_orig = mlp.gate_proj.weight.shape[0]

    def append_neurons(neurons):
        """neurons: list of (k_unit, ref, down_col_vec)."""
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
                mlp.up_proj.weight[:ff_orig].contiguous(), requires_grad=False)
            mlp.down_proj.weight = torch.nn.Parameter(
                mlp.down_proj.weight[:, :ff_orig].contiguous(),
                requires_grad=False)
        mlp.gate_proj.out_features = ff_orig
        mlp.up_proj.out_features = ff_orig
        mlp.down_proj.in_features = ff_orig

    # ── register scale S = median native down_proj column L2-norm at L23 ──
    dn_w = mlp.down_proj.weight[:, :ff_orig].float().cpu().numpy()
    S = float(np.median(np.linalg.norm(dn_w, axis=0)))
    print(f"[rr] register scale S = median native down col-norm = {S:.4f}")

    # ── build country keys (from country-name frames) + capital values ──
    country_specs = {c: [f.format(x=c) for f in wb.CC_FRAMES]
                     for c in countries}
    keys = build_keys(country_specs)
    tern_val = {}      # ternary unit capital direction per country
    trit_report = {"trits": 0, "params": 0}
    for c in countries:
        t, mask, _ = ternarize_vec(unembed_dir(wb.BANK[c][0]))
        tern_val[c] = unit(t)             # unit ternary direction
        trit_report["trits"] += int(mask.sum())
        trit_report["params"] += int(t.size)

    # advisory: capital-logit boost on country frames (did the write land?)
    def boost_on_country_frames(cap_of: dict) -> float:
        neurons = [(keys[c]["k"], keys[c]["ref"], S * tern_val[cap_of[c]])
                   for c in countries]
        base_vals, plate_vals = [], []
        frames = {c: [f.format(x=c) for f in wb.CC_FRAMES] for c in countries}
        for c in countries:
            for p in frames[c]:
                base_vals.append(logits_last(p)[first_tid(wb.BANK[c][0])])
        append_neurons(neurons)
        for c in countries:
            for p in frames[c]:
                plate_vals.append(logits_last(p)[first_tid(wb.BANK[c][0])])
        restore_neurons()
        return float(np.mean(np.array(plate_vals) - np.array(base_vals)))

    # ── eval an arm given a country->capital map (identity = routing_write) ──
    def eval_write(cap_of: dict):
        neurons = [(keys[c]["k"], keys[c]["ref"], S * tern_val[cap_of[c]])
                   for c in countries]
        append_neurons(neurons)
        rows = eval_cells()
        ce = ce_innocents()
        gh = gh_accs()
        restore_neurons()
        return rows, ce, gh

    # ══ run arms ══
    print("[rr] ── base ──")
    base_rows = eval_cells()
    base_ce = ce_innocents()
    base_gh = gh_accs()
    for sp in SPLITS:
        print(f"    {sp}: acc "
              f"{np.mean([r['correct'] for r in base_rows if r['split']==sp]):.3f}")

    print("[rr] ── routing_write ──")
    ident = {c: c for c in countries}
    wr_rows, wr_ce, wr_gh = eval_write(ident)
    landed = boost_on_country_frames(ident)
    print(f"[rr] achieved capital-logit boost on country frames = {landed:.3f} "
          f"(construct throttled to ~0.3)")
    for sp in SPLITS:
        print(f"    {sp}: acc "
              f"{np.mean([r['correct'] for r in wr_rows if r['split']==sp]):.3f}")

    print(f"[rr] ── routing_shuffle ({args.seeds} derangement seeds) ──")
    shuf_seed_rows, shuf_ce, shuf_gh = [], [], []
    for s in range(args.seeds):
        dc = wb.derangement(countries, np.random.default_rng(1000 + s))
        rows, ce, gh = eval_write(dc)          # cap_of[c] = BANK-cap of dc[c]
        # dc maps country->country; capital value = tern_val[dc[c]]
        shuf_seed_rows.append(rows)
        shuf_ce.append(ce)
        shuf_gh.append(gh)
        for sp in SPLITS:
            print(f"    seed {s} {sp}: acc "
                  f"{np.mean([r['correct'] for r in rows if r['split']==sp]):.3f}")

    arms = {
        "base": {"seeds": [base_rows], "ce": base_ce, "gh": base_gh},
        "routing_write": {"seeds": [wr_rows], "ce": wr_ce, "gh": wr_gh,
                          "boost": landed},
        "routing_shuffle": {"seeds": shuf_seed_rows,
                            "ce": float(np.mean(shuf_ce)),
                            "gh": tuple(np.mean(shuf_gh, axis=0))},
        "construct_lookup": {"b2": lookup_b2},
    }

    # ══ frozen scoring ══
    order = {sp: [c.landmark for c in valid if c.split == sp] for sp in SPLITS}

    def acc_arrays(label) -> dict:
        per = {}
        for sp in SPLITS:
            mat = []
            for rows in arms[label]["seeds"]:
                bym = {r["landmark"]: r["correct"] for r in rows
                       if r["split"] == sp}
                mat.append([bym[lm] for lm in order[sp]])
            per[sp] = np.mean(np.array(mat), axis=0)
        return per

    acc = {a: acc_arrays(a) for a in ("base", "routing_write",
                                      "routing_shuffle")}
    acc["construct_lookup"] = {
        "B2": np.array([lookup_b2[lm] for lm in order["B2"]]),
        "B1": np.zeros(len(order["B1"])),
        "TRAIN": np.zeros(len(order["TRAIN"])),
    }
    ce = {"base": base_ce, "routing_write": wr_ce}
    gh = {"base": base_gh, "routing_write": wr_gh}
    r = score(acc, ce, gh, np.random.default_rng(args.seed + 999), args.alpha)
    v = verdict_of(gate0_ok, r)

    stats = {"trits": trit_report["trits"], "params": trit_report["params"],
             "bits": trit_report["trits"] * LOG2_3,
             "sparsity": 1.0 - trit_report["trits"]
             / max(trit_report["params"], 1),
             "boost": landed, "S": S,
             "key_sep_min": float(min(keys[c]["ref"] - keys[c]["inn_max"]
                                      for c in countries)),
             "key_sep_median": float(np.median(
                 [keys[c]["ref"] - keys[c]["inn_max"] for c in countries]))}
    anchor = {sp: {"routing_write": float(acc["routing_write"][sp].mean()),
                   "routing_shuffle": float(acc["routing_shuffle"][sp].mean()),
                   "base": float(acc["base"][sp].mean())} for sp in SPLITS}

    print(f"\n[rr] ════ VERDICT: {v} ════")
    print(f"  G1={r['G1']} G2={r['G2']} G3={r['G3']} G5={r['G5']}")
    print(f"  boost={landed:.3f} key_sep_min={stats['key_sep_min']:.2f} "
          f"trits={stats['trits']} sparsity={stats['sparsity']:.3f}")
    for sp in SPLITS:
        print(f"  {sp}: base {anchor[sp]['base']:.3f} write "
              f"{anchor[sp]['routing_write']:.3f} shuffle "
              f"{anchor[sp]['routing_shuffle']:.3f}")

    def _degate(o):
        if is_dataclass(o) and not isinstance(o, type):
            return asdict(o)
        if isinstance(o, dict):
            return {k: _degate(x) for k, x in o.items()}
        if isinstance(o, (list, tuple)):
            return [_degate(x) for x in o]
        return o

    scoring = {"gates": r, "verdict": v, "stats": stats, "anchor": anchor}
    payload = {"model_id": args.model_id, "config": vars(args),
               "install_layer": li, "gate0": {"ok": gate0_ok, "splits": ns},
               "arms": arms, "scoring": scoring}
    (out_dir / "results.json").write_text(
        json.dumps(_json_safe(_degate(payload)), indent=2))
    print(f"[rr] wrote {out_dir}/results.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--seeds", type=int, default=3,
                    help="derangement seeds for the routing_shuffle null")
    ap.add_argument("--whiten-eps", type=float, default=0.1)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-cells", type=int, default=0,
                    help="smoke: cap cells per split (mechanics only)")
    ap.add_argument("--record-dir",
                    default="results/writeback-compile/qwen3-4b")
    ap.add_argument("--out", default="results/routing-register/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
