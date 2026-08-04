#!/usr/bin/env python3
"""§P-FAST-PLATE — the last construction door: in-forward cleanup-and-reinject.

Pre-reg: mementum/knowledge/explore/write-not-train-ternary-routing-deltas.md
§P-FAST-PLATE (FROZEN s305, Michael-approved; mechanization = cleanup-and-reinject
over the delta-rule capital-relay). The s304 triangulation closed STATIC
construction in BOTH registers (construct magnitude INERT + routing_write routing
INERT; only gd_cd gradient WIRE). The one untested door (§5c of
holographic-reduction-machine.md): a plate written BY the forward pass — the only
mechanism with access to the intermediate the pass materializes.

routing_write read at L23 in NAMED-country geometry (where the one-shot landmark
prompt does NOT materialize the country) and wrote the CAPITAL directly → INERT.
P-FAST-PLATE inverts both moves: READ where the country is materialized-from-
landmark, argmax-COLLAPSE to the nearest of 16 name-frame country keys
(confidence-floored), REINJECT the country in named geometry, and let the host's
OWN h-hop produce the capital. Two static-plate-impossible operations: (1)
nonlinear winner-take-all collapse (the s300 pin / §4 internal-collapse organ);
(2) read-geometry != write-geometry. The plate stores only COUNTRY (not capital)
→ B2 (held-country) generalizes free (host knows all capitals via native h-hop).

MATERIALIZATION SCAN — read-only pre-gate M (TRAIN-only, FROZEN, hard stop):
  on TRAIN landmark DIRECT prompts, per layer L build shared-Sigma name-frame
  country keys, classify each TRAIN landmark activation (argmax over 16 keys),
  decodability(L) = mean(pred == true country). Null = permuted-label accuracy,
  max over the candidate layers (multiple-comparison safe). M passes iff the best
  layer beats the null at alpha.
    ¬M -> STILL-EXTERNAL-BY-MEASUREMENT (the country is never linearly
          materialized one-shot; the s295 exhaustion law is MECHANICAL). STOP.
    M  -> L* = highest-decodability layer in the LOWER 2/3 of the stack (h-hop
          room downstream); ties -> lowest layer.

THE PLATE (single forward hook on dec[L*], all positions, residual space):
  recognize c* = argmax_c (a - mu) @ k_c ; fire iff proj > inn_max_{c*} (floor,
  built from PROSE_INNOCENTS + NONCE -> no fire on innocents, protects F5) ;
  reinject S * proto_{c*} into the residual, proto_c = unit(mu_own_c - mu_pop)
  (population-centered named prototype = the country-specific named direction),
  S = median native down_proj column L2-norm at L* (register-matched, no loop).

Arms (re-scored on the FROZEN 53 gate-0 cells from the s303 record):
  base              : floor (0.200 / 0.125 / 0.545).
  fast_plate        : the cleanup-reinject (hard argmax collapse + confidence floor).
  fast_plate_shuffle: recognize c*, reinject proto_{derange(c*)} — the null
                      (lambda yardstick); matched strength/geometry. >=3 seeds.
  static_reinject   : soft always-on Sum_c softmax(a.k_c) * S * proto_c (same
                      read/write geometry, NO hard collapse, NO floor) —
                      collapse-isolation.
  construct_lookup  : inherited materialized-view null (loaded), F2 baseline.

Gates (verbum.dsp paired-perm 10k, primaries Bonferroni alpha/3):
  F1 WIRE       : fast_plate > base, flip on B1 AND B2.
  F2 NOT-LOOKUP : fast_plate > construct_lookup on B2.
  F3 SPECIFICITY: fast_plate > fast_plate_shuffle on held-out (B1+B2).
  F5 SURVIVE    : innocent CE <= 2% rel base; native g/h within 0.10 abs.
Reports (advisory, NOT gates): collapse_delta (fast_plate - static_reinject on
  held-out; the COLLAPSE-LOAD-BEARING vs GEOMETRY-SUFFICES fork), decodability
  curve + L*, landmark-vs-name cosine at L*, TRAIN recognition acc, reinject_landed
  (did the write move the correct-capital logit? weak-write vs no-routing).
Verdicts: STILL-EXTERNAL-BY-MEASUREMENT (¬M) / FAST-PLATE-WIRES
  (+COLLAPSE-LOAD-BEARING | +GEOMETRY-SUFFICES) / FAST-PLATE-INERT (M∧¬F1) /
  UNSPECIFIC (F1∧¬(F2∧F3)) / HOST-DAMAGED (¬F5).

Cadence: --validate (no model) -> smoke (--n-cells, mechanics only) -> Michael GO
-> run -> frozen scoring.

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

import operand_multihop3 as mh3  # noqa: E402
import writeback_compile as wb  # noqa: E402  (module reuse, no fork)
from holo_frag import _json_safe  # noqa: E402

from verbum.dsp import gate, paired_permutation, shuffled_label  # noqa: E402

SPLITS = wb.SPLITS
LOWER_FRAC = 2.0 / 3.0     # L* selection band: lower 2/3 of the stack (frozen)
N_LABEL_PERM = 2000        # scan null: permuted-label draws (frozen)


def unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


# ══════════════════════════════════════════════════════════════════════════
# Shared-Sigma multi-class key builder (the routing_register build_keys pattern,
# multi-layer reusable): pop = all owns + innocents, single mu/cov, per-country
# k_c = Sigma^-1(mu_own_c - mu). Returns (mu, keys{c: k, ref, inn_max, proto}).
# ══════════════════════════════════════════════════════════════════════════
def build_keys_shared(owns: dict[str, np.ndarray], inn: np.ndarray, eps: float):
    pop = np.vstack([*owns.values(), inn])
    mu = pop.mean(axis=0)
    xc = pop - mu
    cov = (xc.T @ xc) / max(len(pop) - 1, 1)
    d = cov.shape[0]
    cov += eps * (np.trace(cov) / d) * np.eye(d)
    keys = {}
    for c, own in owns.items():
        k = unit(np.linalg.solve(cov, own.mean(axis=0) - mu))
        proj_own = (own - mu) @ k
        proj_inn = (inn - mu) @ k
        keys[c] = {"k": k.astype(np.float32),
                   "ref": float(proj_own.mean()),
                   "inn_max": float(proj_inn.max()),
                   "proto": unit(own.mean(axis=0) - mu).astype(np.float32)}
    return mu.astype(np.float32), keys


def decodability(mu, keys, lm_acts: np.ndarray, true_idx: np.ndarray,
                 countries: list[str]) -> tuple[float, np.ndarray]:
    """argmax-over-keys recognition accuracy of landmark activations. Returns
    (acc, pred_idx). pred is FIXED wrt any label permutation (keys are name-built)."""
    kmat = np.stack([keys[c]["k"] for c in countries])       # (C, D)
    pred = ((lm_acts - mu) @ kmat.T).argmax(axis=1)          # (n,)
    return float(np.mean(pred == true_idx)), pred


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
    arm, base = "fast_plate", "base"
    r = {}
    g1 = {}
    for sp in ("B1", "B2"):
        gg = _g(acc[arm][sp], acc[base][sp], rng, a3, f"F1-{sp}")
        g1[sp] = {"gate": gg,
                  "flip": bool(acc[arm][sp].mean() > acc[base][sp].mean())}
    r["F1"] = bool(all(g1[sp]["gate"].verdict and g1[sp]["flip"]
                       for sp in ("B1", "B2")))
    r["F1_detail"] = g1
    g2 = _g(acc[arm]["B2"], acc["construct_lookup"]["B2"], rng, a3, "F2-B2")
    r["F2"] = bool(g2.verdict)
    r["F2_detail"] = g2
    held = np.concatenate([acc[arm]["B1"], acc[arm]["B2"]])
    held_s = np.concatenate([acc["fast_plate_shuffle"]["B1"],
                             acc["fast_plate_shuffle"]["B2"]])
    g3 = _g(held, held_s, rng, a3, "F3-heldout")
    r["F3"] = bool(g3.verdict)
    r["F3_detail"] = g3
    # advisory (NOT a gate): collapse load-bearing? fast_plate vs static_reinject
    held_st = np.concatenate([acc["static_reinject"]["B1"],
                              acc["static_reinject"]["B2"]])
    gc = _g(held, held_st, rng, alpha, "collapse-heldout")
    r["collapse_delta"] = float(held.mean() - held_st.mean())
    r["collapse_sig"] = bool(gc.verdict)
    r["collapse_detail"] = gc
    ce_ok = ce[arm] <= ce[base] * 1.02
    g_ok = gh[arm][0] >= gh[base][0] - 0.10
    h_ok = gh[arm][1] >= gh[base][1] - 0.10
    r["F5"] = bool(ce_ok and g_ok and h_ok)
    r["F5_detail"] = {"ce": ce[arm], "ce_base": ce[base],
                      "g_acc": gh[arm][0], "h_acc": gh[arm][1]}
    r["held_up"] = bool(held.mean() > np.concatenate(
        [acc[base]["B1"], acc[base]["B2"]]).mean())
    return r


def verdict_of(gate0_ok: bool, m_pass: bool, r: dict) -> str:
    if not gate0_ok:
        return "VOID (gate-0)"
    if not m_pass:
        return "STILL-EXTERNAL-BY-MEASUREMENT"
    if not r["F5"]:
        return "HOST-DAMAGED"
    if r["F1"] and r["F2"] and r["F3"]:
        return ("FAST-PLATE-WIRES (+COLLAPSE-LOAD-BEARING)" if r["collapse_sig"]
                else "FAST-PLATE-WIRES (+GEOMETRY-SUFFICES)")
    if r["F1"]:
        return "UNSPECIFIC"
    return "FAST-PLATE-INERT"


# ══════════════════════════════════════════════════════════════════════════
# --validate (no model)
# ══════════════════════════════════════════════════════════════════════════
def run_validate(alpha: float) -> int:
    ok = True
    print("── §P-FAST-PLATE --validate (no model) ──")
    rng = np.random.default_rng(0)
    D = 128
    countries = [f"C{i}" for i in range(8)]

    # 1. shared-key build + decodability: planted-separable owns classify; a
    #    random layer does not; the label-permutation null sits at chance.
    protos = {c: unit(rng.normal(size=D)) for c in countries}
    inn = rng.normal(size=(12, D)) * 0.3
    owns_good = {c: protos[c][None, :] * 3.0 + rng.normal(size=(4, D)) * 0.2
                 for c in countries}
    mu_g, keys_g = build_keys_shared(owns_good, inn, 0.1)
    # landmark acts near their own proto (materialized layer)
    tl_true = np.repeat(np.arange(8), 2)
    tl_acts = np.stack([protos[countries[i]] * 3.0 + rng.normal(size=D) * 0.3
                        for i in tl_true])
    acc_g, _ = decodability(mu_g, keys_g, tl_acts, tl_true, countries)
    owns_rand = {c: rng.normal(size=(4, D)) for c in countries}
    mu_r, keys_r = build_keys_shared(owns_rand, inn, 0.1)
    acc_r, _ = decodability(mu_r, keys_r, rng.normal(size=(16, D)),
                            tl_true, countries)
    # permuted-label null on the good layer (shuffled_label idiom)
    _, preds_g = decodability(mu_g, keys_g, tl_acts, tl_true, countries)
    null = shuffled_label(lambda perm: float(np.mean(preds_g == perm)),
                          tl_true, rng, n_iter=300)
    m_gate = gate(acc_g, null, "greater", alpha, name="M")
    good = acc_g > 0.8 and acc_r < 0.5 and m_gate.verdict
    print(f"[V] scan: decodable acc {acc_g:.2f} random acc {acc_r:.2f} "
          f"M(p={m_gate.p:.3f}) {'OK' if good else 'FAIL'}")
    ok &= good

    # 2. plate hook mechanics (tiny torch): fast fires+adds correct proto on an
    #    on-country activation, is silent on an innocent; shuffle adds deranged;
    #    static adds a softmax mix.
    import torch
    Kmat = torch.tensor(np.stack([keys_g[c]["k"] for c in countries]),
                        dtype=torch.float32)
    innmax = torch.tensor([keys_g[c]["inn_max"] for c in countries],
                          dtype=torch.float32)
    proto_t = torch.tensor(np.stack([keys_g[c]["proto"] for c in countries]),
                           dtype=torch.float32)
    mu_t = torch.tensor(mu_g, dtype=torch.float32)
    S = 1.0

    def apply(mode, a_np, proto_mat):
        h = torch.tensor(a_np, dtype=torch.float32)[None, None, :]  # (1,1,D)
        A = h[0].float()
        P = (A - mu_t) @ Kmat.T
        if mode == "static":
            W = torch.softmax(P, dim=1)
            delta = S * (W @ proto_mat)
        else:
            pmax, cstar = P.max(dim=1)
            fired = pmax > innmax[cstar]
            delta = S * proto_mat[cstar] * fired[:, None].float()
        return (h[0] + delta).numpy()[0], delta

    on = protos[countries[3]] * 3.0
    out_fast, _d_fast = apply("fast", on, proto_t)
    exp = on + S * keys_g[countries[3]]["proto"]
    e_on = float(np.abs(out_fast - exp).max())
    inn_vec = inn[0]
    _, d_inn = apply("fast", inn_vec, proto_t)
    silent = float(np.abs(d_inn.numpy()).max())
    derange = wb.derangement(countries, np.random.default_rng(2))
    proto_shuf = torch.tensor(
        np.stack([keys_g[derange[c]]["proto"] for c in countries]),
        dtype=torch.float32)
    out_shuf, _ = apply("shuf", on, proto_shuf)
    exp_s = on + S * keys_g[derange[countries[3]]]["proto"]
    e_shuf = float(np.abs(out_shuf - exp_s).max())
    _, d_stat = apply("static", on, proto_t)
    stat_ok = float(np.linalg.norm(d_stat.numpy())) > 0
    good = e_on < 1e-4 and silent < 1e-6 and e_shuf < 1e-4 and stat_ok
    print(f"[V] plate: fast-err {e_on:.2e} innocent-silent {silent:.2e} "
          f"shuffle-err {e_shuf:.2e} static-nonzero {stat_ok} "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    # 3. derangement no fixed point
    d = wb.derangement(sorted(wb.BANK), np.random.default_rng(1))
    good = all(k != x for k, x in d.items()) and set(d.values()) == set(wb.BANK)
    print(f"[V] derangement: {'OK' if good else 'FAIL'}")
    ok &= good

    # 4. S = median native column norm
    w = rng.normal(size=(D, 32))
    s = float(np.median(np.linalg.norm(w, axis=0)))
    print(f"[V] S median col-norm {s:.3f} {'OK' if s > 0 else 'FAIL'}")
    ok &= s > 0

    # 5. verdict planted worlds
    def world(name, want, m_pass, fp, base, shuf, stat, lookup,
              ce_bad=False, gh_bad=False):
        rngw = np.random.default_rng(hash(name) & 0xFFFF)

        def arr(p, n=64):
            return (rngw.random(n) < p).astype(float)

        acc = {
            "base": {"TRAIN": arr(base[0]), "B1": arr(base[1]),
                     "B2": arr(base[2])},
            "fast_plate": {"TRAIN": arr(fp[0]), "B1": arr(fp[1]),
                           "B2": arr(fp[2])},
            "fast_plate_shuffle": {"TRAIN": arr(shuf[0]), "B1": arr(shuf[1]),
                                   "B2": arr(shuf[2])},
            "static_reinject": {"TRAIN": arr(stat[0]), "B1": arr(stat[1]),
                                "B2": arr(stat[2])},
            "construct_lookup": {"TRAIN": arr(lookup[0]), "B1": arr(lookup[1]),
                                 "B2": arr(lookup[2])},
        }
        ce = {a: (1.10 if (ce_bad and a == "fast_plate") else 1.0) for a in acc}
        gh = {a: ((0.5, 0.5) if (gh_bad and a == "fast_plate")
                  else (0.95, 0.95)) for a in acc}
        r = score(acc, ce, gh, np.random.default_rng(3), alpha)
        v = verdict_of(True, m_pass, r)
        hit = want in v
        print(f"[V] {name}-world -> {v} (want {want}) {'OK' if hit else 'FAIL'}")
        return hit

    ok &= world("still-external", "STILL-EXTERNAL-BY-MEASUREMENT", False,
                fp=(.2, .12, .3), base=(.2, .12, .3), shuf=(.2, .12, .3),
                stat=(.2, .12, .3), lookup=(.27, .12, .35))
    ok &= world("collapse", "COLLAPSE-LOAD-BEARING", True,
                fp=(.95, .92, .95), base=(.2, .12, .3), shuf=(.2, .12, .2),
                stat=(.4, .3, .35), lookup=(.27, .12, .35))
    ok &= world("geometry", "GEOMETRY-SUFFICES", True,
                fp=(.95, .92, .95), base=(.2, .12, .3), shuf=(.2, .12, .2),
                stat=(.93, .90, .93), lookup=(.27, .12, .35))
    ok &= world("inert", "FAST-PLATE-INERT", True,
                fp=(.2, .12, .3), base=(.2, .12, .3), shuf=(.2, .12, .28),
                stat=(.2, .12, .3), lookup=(.27, .12, .35))
    ok &= world("unspecific", "UNSPECIFIC", True,
                fp=(.95, .92, .95), base=(.2, .12, .3), shuf=(.96, .93, .96),
                stat=(.4, .3, .35), lookup=(.27, .12, .35))
    ok &= world("host-damaged", "HOST-DAMAGED", True,
                fp=(.95, .92, .95), base=(.2, .12, .3), shuf=(.2, .12, .2),
                stat=(.4, .3, .35), lookup=(.27, .12, .35), ce_bad=True)

    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
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
    print(f"[fp] {args.model_id} dev={dev} n_layers={n_layers} valid={len(valid)} "
          f"splits={ns} shuffle_seeds={args.seeds} gate0_ok={gate0_ok}")

    if args.n_cells:                       # smoke cap (mechanics only)
        by = {sp: [c for c in valid if c.split == sp] for sp in SPLITS}
        valid_eval = [c for sp in SPLITS for c in by[sp][:args.n_cells]]
        lookup_b2 = {c.landmark: lookup_b2.get(c.landmark, 0.0)
                     for c in valid_eval if c.split == "B2"}
        print(f"[fp] SMOKE cap {args.n_cells}/split -> {len(valid_eval)} cells")
    else:
        valid_eval = valid

    countries = sorted(wb.BANK)
    caps = sorted({cap for cap, _ in wb.BANK.values()})

    # ── union candidate set (rr pattern) ──
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
        for c in valid_eval:
            lo = logits_last(wb.DIRECT_PROMPT.format(lm=c.landmark))
            arg = argmax_union(lo)
            rows.append({"landmark": c.landmark, "country": c.country,
                         "split": c.split, "truth": c.capital, "arg": arg,
                         "correct": float(wb.first_word(arg)
                                          == wb.first_word(c.capital)),
                         "margin": margin(lo, c.capital),
                         "cap_logit": float(lo[union[c.capital]])})
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
            == c.country for c in valid_eval]
        h = [wb.first_word(max(caps, key=lambda w: logits_last(
            wb.CAP_PREFIX + wb.CAP_QUERY.format(x=co))[first_tid(w)]))
            == wb.first_word(wb.BANK[co][0]) for co in sorted(wb.BANK)]
        return float(np.mean(g)), float(np.mean(h))

    # ── capture last-token residual at EVERY layer for a prompt list ──
    def capture_all(prompts: list[str]) -> dict[int, np.ndarray]:
        tmp: dict[int, np.ndarray] = {}
        handles = [dec[L].register_forward_hook(mh3.cap_hook(tmp, L))
                   for L in range(n_layers)]
        acc = {L: [] for L in range(n_layers)}
        for p in prompts:
            ids = tok(p, return_tensors="pt").to(dev)
            with torch.no_grad():
                model(**ids)
            for L in range(n_layers):
                acc[L].append(tmp[L][0, -1, :])
        for h in handles:
            h.remove()
        return {L: np.stack(acc[L]) for L in range(n_layers)}

    # ══ MATERIALIZATION SCAN (pre-gate M; TRAIN-only, no held peeking) ══
    inn_prompts = list(wb.PROSE_INNOCENTS) + [
        wb.DIRECT_PROMPT.format(lm=nc) for nc in wb.NONCE_CANDS[:3]]
    name_prompts, name_owner = [], []
    for c in countries:
        for f in wb.CC_FRAMES:
            name_prompts.append(f.format(x=c))
            name_owner.append(c)
    train_cells = [c for c in valid if c.split == "TRAIN"]  # full TRAIN (scan)
    tl_prompts = [wb.DIRECT_PROMPT.format(lm=c.landmark) for c in train_cells]
    tl_true = np.array([countries.index(c.country) for c in train_cells])

    print(f"[fp] scan: {len(name_prompts)} name frames, {len(inn_prompts)} "
          f"innocents, {len(tl_prompts)} TRAIN landmarks across {n_layers} layers")
    name_caps = capture_all(name_prompts)
    inn_caps = capture_all(inn_prompts)
    tl_caps = capture_all(tl_prompts)

    cand_layers = [L for L in range(n_layers) if L <= round(LOWER_FRAC * n_layers)]
    dec_curve, preds_by_L, keys_by_L, mu_by_L = {}, {}, {}, {}
    for L in range(n_layers):
        owns = {c: name_caps[L][np.array(name_owner) == c] for c in countries}
        mu_L, keys_L = build_keys_shared(owns, inn_caps[L], args.whiten_eps)
        acc_L, pred_L = decodability(mu_L, keys_L, tl_caps[L], tl_true, countries)
        dec_curve[L] = acc_L
        preds_by_L[L] = pred_L
        keys_by_L[L] = keys_L
        mu_by_L[L] = mu_L

    # L* = best decodability in the lower 2/3 (ties -> lowest layer)
    best_acc = max(dec_curve[L] for L in cand_layers)
    li = min(L for L in cand_layers if dec_curve[L] == best_acc)
    # multiple-comparison-safe null: per label-permutation, max acc over cands
    rng_scan = np.random.default_rng(args.seed + 7)
    null_max = shuffled_label(
        lambda perm: max(float(np.mean(preds_by_L[L] == perm))
                         for L in cand_layers),
        tl_true, rng_scan, n_iter=N_LABEL_PERM)
    m_gate = gate(best_acc, null_max, "greater", args.alpha, name="M")
    m_pass = bool(m_gate.verdict)
    lm_name_cos = float(np.mean([  # advisory: landmark-vs-name geometry at L*
        float(np.dot(unit(tl_caps[li][tl_true == i].mean(axis=0)
                          - mu_by_L[li]), keys_by_L[li][countries[i]]["proto"]))
        for i in range(len(countries)) if (tl_true == i).any()]))
    print(f"[fp] scan: L*={li} decodability={best_acc:.3f} (p={m_gate.p:.4f}) "
          f"M={'PASS' if m_pass else 'FAIL'} lm-name-cos={lm_name_cos:.3f}")
    print("[fp] decodability curve (cand layers): "
          + " ".join(f"L{L}:{dec_curve[L]:.2f}" for L in cand_layers))

    scan = {"L_star": li, "decodability": best_acc, "m_pass": m_pass,
            "m_p": float(m_gate.p), "lm_name_cos": lm_name_cos,
            "curve": {str(L): dec_curve[L] for L in range(n_layers)},
            "cand_layers": cand_layers, "train_recognition_acc": best_acc}

    # ── register scale S = median native down_proj column L2-norm at L* ──
    mlp = dec[li].mlp
    dn_w = mlp.down_proj.weight.float().cpu().numpy()
    S = float(np.median(np.linalg.norm(dn_w, axis=0)))
    keys, mu = keys_by_L[li], mu_by_L[li]
    print(f"[fp] register scale S = median native down col-norm at L{li} = {S:.4f}")

    # ── the in-forward plate hook (all positions, residual space) ──
    kmat_t = torch.tensor(np.stack([keys[c]["k"] for c in countries]),
                          dtype=torch.float32, device=dev)
    innmax_t = torch.tensor([keys[c]["inn_max"] for c in countries],
                            dtype=torch.float32, device=dev)
    mu_t = torch.tensor(mu, dtype=torch.float32, device=dev)
    proto_np = np.stack([keys[c]["proto"] for c in countries])

    def make_hook(mode: str, proto_mat: np.ndarray):
        proto_t = torch.tensor(proto_mat, dtype=torch.float32, device=dev)

        def hook(_m, _i, out):
            h = out[0] if isinstance(out, tuple) else out
            A = h[0].float()                          # (seq, D)
            P = (A - mu_t) @ kmat_t.T                 # (seq, C)
            if mode == "static":
                W = torch.softmax(P, dim=1)
                delta = S * (W @ proto_t)
            else:                                     # fast / shuffle
                pmax, cstar = P.max(dim=1)
                fired = (pmax > innmax_t[cstar]).float()
                delta = S * proto_t[cstar] * fired[:, None]
            h[0].add_(delta.to(h.dtype))
            return out
        return hook

    def run_arm(hook_fn):
        hnd = dec[li].register_forward_hook(hook_fn) if hook_fn else None
        rows = eval_cells()
        ce = ce_innocents()
        gh = gh_accs()
        if hnd:
            hnd.remove()
        return rows, ce, gh

    # ══ base always (anchor) ══
    print("[fp] ── base ──")
    base_rows, base_ce, base_gh = run_arm(None)
    for sp in SPLITS:
        print(f"    {sp}: acc "
              f"{np.mean([r['correct'] for r in base_rows if r['split']==sp]):.3f}")

    arms = {"base": {"seeds": [base_rows], "ce": base_ce, "gh": base_gh},
            "construct_lookup": {"b2": lookup_b2}}
    stats = {"S": S, "scan": scan,
             "key_sep_min": float(min(keys[c]["ref"] - keys[c]["inn_max"]
                                      for c in countries)),
             "key_sep_median": float(np.median(
                 [keys[c]["ref"] - keys[c]["inn_max"] for c in countries]))}

    if not m_pass:
        # HARD STOP: the country is never materialized one-shot (pre-gate M).
        r = {"F1": False, "F2": False, "F3": False, "F5": True,
             "collapse_sig": False, "collapse_delta": 0.0}
        v = verdict_of(gate0_ok, m_pass, r)
        print(f"\n[fp] ════ VERDICT: {v} ════  (pre-gate M FAILED; plate arms "
              f"not run — the exhaustion law is mechanical)")
        scoring = {"gates": r, "verdict": v, "stats": stats, "m_pass": m_pass}
        payload = {"model_id": args.model_id, "config": vars(args),
                   "install_layer": li, "gate0": {"ok": gate0_ok, "splits": ns},
                   "arms": arms, "scoring": scoring}
        (out_dir / "results.json").write_text(
            json.dumps(_json_safe(_degate(payload)), indent=2))
        print(f"[fp] wrote {out_dir}/results.json")
        return 0

    # ══ plate arms (M passed) ══
    print("[fp] ── fast_plate ──")
    fp_rows, fp_ce, fp_gh = run_arm(make_hook("fast", proto_np))
    for sp in SPLITS:
        print(f"    {sp}: acc "
              f"{np.mean([r['correct'] for r in fp_rows if r['split']==sp]):.3f}")

    print("[fp] ── static_reinject ──")
    st_rows, st_ce, st_gh = run_arm(make_hook("static", proto_np))
    for sp in SPLITS:
        print(f"    {sp}: acc "
              f"{np.mean([r['correct'] for r in st_rows if r['split']==sp]):.3f}")

    print(f"[fp] ── fast_plate_shuffle ({args.seeds} derangement seeds) ──")
    shuf_seed_rows, shuf_ce, shuf_gh = [], [], []
    for s in range(args.seeds):
        d = wb.derangement(countries, np.random.default_rng(1000 + s))
        proto_shuf = np.stack([keys[d[c]]["proto"] for c in countries])
        rows, ce, gh = run_arm(make_hook("fast", proto_shuf))
        shuf_seed_rows.append(rows)
        shuf_ce.append(ce)
        shuf_gh.append(gh)
        for sp in SPLITS:
            print(f"    seed {s} {sp}: acc "
                  f"{np.mean([r['correct'] for r in rows if r['split']==sp]):.3f}")

    # advisory: reinject_landed = mean correct-capital-logit shift on held-out
    def held_cap(rows):
        return np.array([r["cap_logit"] for r in rows if r["split"] in ("B1", "B2")])
    reinject_landed = float(held_cap(fp_rows).mean() - held_cap(base_rows).mean())
    print(f"[fp] reinject_landed (held-out correct-capital logit shift) "
          f"= {reinject_landed:.3f}")

    arms.update({
        "fast_plate": {"seeds": [fp_rows], "ce": fp_ce, "gh": fp_gh},
        "static_reinject": {"seeds": [st_rows], "ce": st_ce, "gh": st_gh},
        "fast_plate_shuffle": {"seeds": shuf_seed_rows,
                               "ce": float(np.mean(shuf_ce)),
                               "gh": tuple(np.mean(shuf_gh, axis=0))},
    })
    stats["reinject_landed"] = reinject_landed

    # ══ frozen scoring ══
    order = {sp: [c.landmark for c in valid_eval if c.split == sp]
             for sp in SPLITS}

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

    acc = {a: acc_arrays(a) for a in ("base", "fast_plate", "static_reinject",
                                      "fast_plate_shuffle")}
    acc["construct_lookup"] = {
        "B2": np.array([lookup_b2[lm] for lm in order["B2"]]),
        "B1": np.zeros(len(order["B1"])),
        "TRAIN": np.zeros(len(order["TRAIN"])),
    }
    ce = {"base": base_ce, "fast_plate": fp_ce}
    gh = {"base": base_gh, "fast_plate": fp_gh}
    r = score(acc, ce, gh, np.random.default_rng(args.seed + 999), args.alpha)
    v = verdict_of(gate0_ok, m_pass, r)

    anchor = {sp: {a: float(acc[a][sp].mean())
                   for a in ("base", "fast_plate", "static_reinject",
                             "fast_plate_shuffle")} for sp in SPLITS}
    stats["anchor"] = anchor

    print(f"\n[fp] ════ VERDICT: {v} ════")
    print(f"  F1={r['F1']} F2={r['F2']} F3={r['F3']} F5={r['F5']} "
          f"collapse_sig={r['collapse_sig']} (Δ={r['collapse_delta']:+.3f})")
    print(f"  L*={li} decodability={best_acc:.3f} lm-name-cos={lm_name_cos:.3f} "
          f"reinject_landed={reinject_landed:.3f} S={S:.3f}")
    for sp in SPLITS:
        print(f"  {sp}: base {anchor[sp]['base']:.3f} fast "
              f"{anchor[sp]['fast_plate']:.3f} static "
              f"{anchor[sp]['static_reinject']:.3f} shuffle "
              f"{anchor[sp]['fast_plate_shuffle']:.3f}")

    scoring = {"gates": r, "verdict": v, "stats": stats, "m_pass": m_pass}
    payload = {"model_id": args.model_id, "config": vars(args),
               "install_layer": li, "gate0": {"ok": gate0_ok, "splits": ns},
               "arms": arms, "scoring": scoring}
    (out_dir / "results.json").write_text(
        json.dumps(_json_safe(_degate(payload)), indent=2))
    print(f"[fp] wrote {out_dir}/results.json")
    return 0


def _degate(o):
    if is_dataclass(o) and not isinstance(o, type):
        return asdict(o)
    if isinstance(o, dict):
        return {k: _degate(x) for k, x in o.items()}
    if isinstance(o, (list, tuple)):
        return [_degate(x) for x in o]
    return o


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--seeds", type=int, default=3,
                    help="derangement seeds for the fast_plate_shuffle null")
    ap.add_argument("--whiten-eps", type=float, default=0.1)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-cells", type=int, default=0,
                    help="smoke: cap eval cells per split (mechanics only)")
    ap.add_argument("--record-dir",
                    default="results/writeback-compile/qwen3-4b")
    ap.add_argument("--out", default="results/fast-plate/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
