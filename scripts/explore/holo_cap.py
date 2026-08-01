"""P-HOLO-CAP — the superposition capacity law: overexpose the plate.

Pre-reg: mementum/knowledge/explore/geometry-holography-signals-convergence.md
§P-HOLO-CAP (s292, GO-BY-DIRECTIVE — gates frozen before any model run).
FRAG certified the medium ADDRESS-FREE (no cliff, LDI in-noise); CAP is the
POSITIVE claim the frame owes: superposed operands should show HRR/Hopfield
crosstalk — retrieval SNR ∝ sqrt(D/k), graceful — not a slot limit
(flat-then-cliff at k*).

Design (multiple exposures, cued retrieval):
  - k distinct nonces listed in a preamble; each DISTRACTOR nonce gets its
    landmark operand (d_lm * S, frozen mh3 build) installed at its preamble
    slot at L_ref; the QUERIED component installed harness-identically at the
    query-line nonce slot. Readout = frozen 3-hop continent cloze margin.
  - Every component of every draw is queried in turn (k forwards per draw).
  - k in {1,2,3,4,6,8,12,16} (a priori, capped at n_valid); R draws per k.
  - Arms: content (superposed exposures) / random (matched-norm energy
    control) / bare (prompt-shape floor). Same landmark draws across arms.

Gates (frozen):
  Gate-0     : m_content(k=1) expressed (mean > 3*SE, > 0).
  Materiality: decline m(1)->m(k_max) > material_frac * m(1) (FRAG FIX#1).
  G1 (PRIMARY, the SLOT test): (a) cliff_stat on the content curve
     (holo_frag verbatim); (b) CCI = LDI analog at each k>=2 — across-draw
     variance of the bank-mean margin AFTER per-landmark k=1 baseline
     removal, vs the component-resampling noise floor.
     CCI ~= 1 -> only HOW MANY matters -> unaddressed crosstalk.
     CCI >> 1 or cliff -> slot/structure -> SLOT-LIMITED.
  G2 (secondary, HRR form): log-log slope beta of the content curve vs the
     a-priori beta = -0.5; |beta+0.5| gated predict=less against a
     matched-range null (dsp.matched_range; s247 phi-ladder discipline).
     Scored only if materiality passes and >=4 positive-mean points.
  G3 (advisory, NEVER gated): width leg — normalized curves across hosts.

Verdict (frozen):
  SLOT-LIMITED          <=> G1 cliff (material) OR CCI beats null (majority k)
  NO-LIMIT-IN-RANGE     <=> gate-0 AND no material decline
  SUPERPOSITION-CAPACITY<=> gate-0 AND material AND G1 graceful
                            (+ " with HRR-FORM" if G2 passes)
  negative/inconclusive <=> gate-0 fails.

`λ measure`: claim = value-register storage capacity under superposition;
probe = behavioral margin under causal k-operand install load. The cued
retrieval IS the Hopfield/holographic readout (theorem bridge #2).

License: MIT (`λ provenance`).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

# same-directory import (sys.path[0] = scripts/explore when run as a script):
# holo_frag's frozen statistics are reused verbatim (no fork).
from holo_frag import _json_safe, ldi_at_f

from verbum.dsp import gate, matched_range

# Reuse the FROZEN 3-hop geography bank (import the data, not a copy).
_WRAP = Path(__file__).resolve().parents[2] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

K_GRID_DEFAULT = (1, 2, 3, 4, 6, 8, 12, 16)

# nonce vocabulary (candidates; runtime keeps those with unique last tokens)
NONCE_CANDS = [
    "zorp", "flim", "drax", "quop", "blint", "snerp", "glark", "trazz",
    "vonk", "plaff", "dworp", "snib", "yerm", "clazz", "frub", "norp",
    "skell", "twib", "grelm", "zint",
]


# ══════════════════════════════════════════════════════════════════════════
# Pure-numpy statistics (what --validate exercises)
# ══════════════════════════════════════════════════════════════════════════
def cliff_stat_logk(ks: list[int], curve: list[float],
                    material_frac: float = 0.15) -> dict:
    """G1a cliff detector in slope-per-Δlog(k) units (FIX #1, caught by
    --validate BEFORE any model run): a power law is CONSTANT-slope in log k,
    but on a geometric k-grid its first linear step is the largest — the
    uniform-step FRAG cliff_stat misreads a smooth k^(-1/2) plant as a cliff
    (ratio 2.79). Normalizing each step by its Δlog k makes the smooth plant
    read ~1.7 and leaves a slot collapse (one dominant interval) >> thresh.
    Materiality gate (FRAG FIX#1 semantics) retained: no material total drop
    -> cliff_ratio = NaN (no cliff to detect)."""
    ys = list(curve)
    m1 = ys[0]
    dlogk = [np.log(ks[i + 1]) - np.log(ks[i]) for i in range(len(ks) - 1)]
    steps = [(ys[i] - ys[i + 1]) / dlogk[i] for i in range(len(ys) - 1)]
    total = ys[0] - ys[-1]
    mean_step = float(np.mean(steps)) if steps else 0.0
    max_step = max(steps) if steps else 0.0
    material = bool(total > material_frac * abs(m1)) if m1 else False
    ratio = (max_step / mean_step) if (material and mean_step > 1e-9) \
        else float("nan")
    return {"cliff_ratio": float(ratio),
            "steps_per_dlogk": [float(s) for s in steps],
            "total_drop": float(total), "max_step": float(max_step),
            "material": material}


def fit_loglog_slope(ks: np.ndarray, ms: np.ndarray) -> float:
    """Slope of log(m) vs log(k) over points with m > 0 (>=2 required)."""
    mask = ms > 0
    if mask.sum() < 2:
        return float("nan")
    return float(np.polyfit(np.log(ks[mask]), np.log(ms[mask]), 1)[0])


def g2_form(ks: list[int], ms: list[float], rng: np.random.Generator,
            n_iter: int, alpha: float, material: bool):
    """|beta_hat + 0.5| vs matched-range null (predict=less). None if unscorable."""
    ks_a = np.asarray(ks, dtype=float)
    ms_a = np.asarray(ms, dtype=float)
    pos = ms_a > 0
    if not material or pos.sum() < 4:
        return None, float("nan")
    beta = fit_loglog_slope(ks_a[pos], ms_a[pos])

    def stat(curve: np.ndarray) -> float:
        b = fit_loglog_slope(ks_a[pos], np.abs(curve))
        return abs(b + 0.5) if np.isfinite(b) else np.nan

    null = matched_range(stat, ms_a[pos], rng, n_iter=n_iter)
    g = gate(abs(beta + 0.5), null, predict="less", alpha=alpha,
             name="g2_hrr_form")
    return g, beta


def cci_at_k(margins: np.ndarray, baselines: np.ndarray,
             rng: np.random.Generator) -> dict:
    """Crosstalk-Composition Index at one k (LDI analog, baseline-centered).

    margins:   (R, k) per-component margins per draw.
    baselines: (R, k) each queried landmark's own k=1 margin (heterogeneity
               across landmark subsets must not masquerade as
               composition-dependence).
    """
    return ldi_at_f(margins - baselines, rng)


def aggregate_verdict_cap(gate0: bool, material: bool, cliff: dict,
                          per_k_cci: dict, g2, alpha: float,
                          cliff_thresh: float) -> dict:
    slot_by_cliff = bool(np.isfinite(cliff["cliff_ratio"])
                         and cliff["cliff_ratio"] >= cliff_thresh)
    ps = [c["p"] for c in per_k_cci.values() if c["p"] is not None]
    n_sig = sum(1 for p in ps if p < alpha)
    slot_by_cci = bool(ps and n_sig > len(ps) / 2)
    ccis = [c["ldi"] for c in per_k_cci.values() if np.isfinite(c["ldi"])]
    med_cci = float(np.median(ccis)) if ccis else float("nan")
    if not gate0:
        call = "negative/inconclusive (gate-0)"
    elif slot_by_cliff or slot_by_cci:
        call = "SLOT-LIMITED"
    elif not material:
        call = "NO-LIMIT-IN-RANGE"
    else:
        call = "SUPERPOSITION-CAPACITY"
        if g2 is not None and g2.verdict:
            call += " with HRR-FORM"
    return {"gate0": gate0, "material": material,
            "slot_by_cliff": slot_by_cliff, "slot_by_cci": slot_by_cci,
            "n_cci_sig": n_sig, "n_cci_tested": len(ps),
            "median_cci": med_cci, "call": call}


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted media exercise the detectors before any model run
# ══════════════════════════════════════════════════════════════════════════
def _synth_medium(kind: str, k_grid, r: int, rng: np.random.Generator,
                  m1: float = 4.0, noise: float = 0.3, slots: int = 4) -> dict:
    """Per-draw, per-component margins under a planted capacity structure.

    kind: 'superposition' — m(k) = m1/sqrt(k) + noise (HRR crosstalk)
          'slot'          — flat to k*=slots, then thrash-collapse (cliff)
          'composition'   — superposition + designated BAD PAIR of components
                            that annihilates a draw's margins (CCI must fire)
    """
    n_items = 24
    bad = (0, 1)  # the structured pair for 'composition'
    per_k = {}
    for k in k_grid:
        margins = np.zeros((r, k))
        baselines = np.full((r, k), m1)
        for ri in range(r):
            items = rng.choice(n_items, size=k, replace=False)
            if kind == "superposition":
                mu = m1 / np.sqrt(k)
            elif kind == "slot":
                mu = m1 if k <= slots else 0.15 * m1
            elif kind == "composition":
                mu = m1 / np.sqrt(k)
                if bad[0] in items and bad[1] in items:
                    mu = 0.1 * m1
            else:
                raise ValueError(kind)
            margins[ri] = mu + rng.normal(0.0, noise, size=k)
        # synth items are homogeneous (no per-landmark heterogeneity to
        # remove) -> zero baselines; CCI reads raw across-draw variance.
        del baselines
        per_k[k] = {"margins": margins, "baselines": np.zeros((r, k))}
    return per_k


def run_validate(alpha: float, cliff_thresh: float, material_frac: float) -> int:
    rng = np.random.default_rng(0)
    kg = [k for k in K_GRID_DEFAULT]
    print("── P-HOLO-CAP --validate (planted media, no model) ──")
    ok = True

    def score(kind):
        med = _synth_medium(kind, kg, 100, rng)
        curve = [float(med[k]["margins"].mean()) for k in kg]
        m1 = curve[0]
        material = bool((m1 - curve[-1]) > material_frac * abs(m1))
        cliff = cliff_stat_logk(kg, curve, material_frac=material_frac)
        cci = {k: cci_at_k(med[k]["margins"], med[k]["baselines"], rng)
               for k in kg if k >= 2}
        g2, beta = g2_form(kg, curve, rng, 500, alpha, material)
        v = aggregate_verdict_cap(True, material, cliff, cci, g2,
                                  alpha, cliff_thresh)
        return curve, cliff, cci, g2, beta, v

    # (i) planted superposition: graceful, CCI~1, beta ~ -0.5
    curve, cliff, cci, g2, beta, v = score("superposition")
    cci_sig = sum(1 for c in cci.values() if c["p"] is not None and c["p"] < alpha)
    print(f"[sup ] curve {curve[0]:.2f}->{curve[-1]:.2f} "
          f"cliff={cliff['cliff_ratio']:.2f} cci_sig={cci_sig}/{len(cci)} "
          f"beta={beta:.3f} g2={'PASS' if g2 and g2.verdict else 'fail'} "
          f"-> {v['call']}")
    # <=1 chance CCI hit tolerated across 7 nulls-true tests (alpha=.05);
    # the verdict criterion is the MAJORITY rule, exercised by 'composition'.
    sup_ok = bool(v["call"].startswith("SUPERPOSITION-CAPACITY")
                  and g2 is not None and g2.verdict and cci_sig <= 1)
    ok &= sup_ok

    # (ii) planted slot machine: cliff fires -> SLOT-LIMITED
    curve, cliff, cci, g2, beta, v = score("slot")
    print(f"[slot] curve {curve[0]:.2f}->{curve[-1]:.2f} "
          f"cliff={cliff['cliff_ratio']:.2f} -> {v['call']}")
    slot_ok = bool(v["slot_by_cliff"] and v["call"] == "SLOT-LIMITED")
    ok &= slot_ok

    # (iii) planted structured composition: CCI fires -> SLOT-LIMITED
    curve, cliff, cci, g2, beta, v = score("composition")
    cci_sig = sum(1 for c in cci.values() if c["p"] is not None and c["p"] < alpha)
    print(f"[comp] curve {curve[0]:.2f}->{curve[-1]:.2f} "
          f"cci_sig={cci_sig}/{len(cci)} -> {v['call']}")
    comp_ok = bool(v["slot_by_cci"] and v["call"] == "SLOT-LIMITED")
    ok &= comp_ok

    print(f"[detectors] sup={sup_ok} slot={slot_ok} comp={comp_ok}")
    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path (4B smoke / 32B verdict)
# ══════════════════════════════════════════════════════════════════════════
def build_preamble(nonces: list[str]) -> str:
    if len(nonces) == 1:
        return f"The {nonces[0]} is a famous landmark.\n"
    if len(nonces) == 2:
        return f"The {nonces[0]} and the {nonces[1]} are famous landmarks.\n"
    head = ", the ".join(nonces[:-1])
    return f"The {head}, and the {nonces[-1]} are famous landmarks.\n"


def run_model(args) -> int:
    import operand_multihop3 as mh3  # frozen bank + helpers (no fork)
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    rng = np.random.default_rng(args.seed)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    dec, _norm, _unembed = mh3.resolve_parts(model)
    L, S = args.ref_layer, args.scale
    print(f"[cap] {args.model_id} L_ref={L} scale={S} dev={dev} "
          f"n_layers={len(dec)}")

    cont_ids = {c: mh3.first_tid(tok, c) for c in mh3.CONTINENTS}

    # nonces with unique last tokens (slot addressing requires uniqueness)
    nonce_tid, nonces = {}, []
    for n in NONCE_CANDS:
        t = tok(" " + n, add_special_tokens=False).input_ids[-1]
        if t not in nonce_tid.values():
            nonce_tid[n] = t
            nonces.append(n)
    print(f"[cap] nonces usable: {len(nonces)}/{len(NONCE_CANDS)}")

    # ── knowledge ceiling (holo_frag pattern): full real-word chain holds ──
    def real_pred(prefix, query, word, label_ids):
        prompt = prefix + query.format(x=word)
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        return max(label_ids, key=lambda k: lo[label_ids[k]])

    city_ids = {c: mh3.first_tid(tok, c) for c in mh3.CITIES}
    country_ids = {c: mh3.first_tid(tok, c) for c in mh3.COUNTRIES}
    valid = []
    for lm in mh3.LM_LIST:
        c_city = real_pred(mh3.CITY_PREFIX, mh3.CITY_QUERY, lm, city_ids)
        c_cnty = real_pred(mh3.CITY2COUNTRY_PREFIX, mh3.CITY2COUNTRY_QUERY,
                           mh3.CITY_OF[lm], country_ids)
        c_cont = real_pred(mh3.COUNTRY2CONT_PREFIX, mh3.COUNTRY2CONT_QUERY,
                           mh3.COUNTRY_OF[lm], cont_ids)
        if (c_city == mh3.CITY_OF[lm]
                and c_cnty == mh3.CITY_COUNTRY[mh3.CITY_OF[lm]]
                and c_cont == mh3.COUNTRY_CONT[mh3.COUNTRY_OF[lm]]):
            valid.append(lm)
    print(f"[cap] valid landmarks (ceiling): {len(valid)}/{len(mh3.LM_LIST)}")

    # ── operand directions d_lm at L (frozen mh3 build) ────────────────────
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

    d_lm = build_dirs(mh3.LM_LIST)
    dim = d_lm[valid[0]].shape[0]

    def rand_like(vec):
        v = rng.standard_normal(dim)
        return v / (np.linalg.norm(v) + 1e-9) * float(np.linalg.norm(vec))

    def margins_for_draw(lms: list[str], arm: str) -> list[float]:
        """Query every component of one draw under one arm; return margins."""
        k = len(lms)
        ns = nonces[:k]
        out = []
        for qi in range(k):
            prompt = (mh3.CONT_PREFIX + build_preamble(ns)
                      + mh3.CONT_QUERY.format(x=ns[qi]))
            ids = tok(prompt, return_tensors="pt").to(dev)
            toks = ids.input_ids[0].tolist()

            def slot_of(n, _toks=tuple(toks)):
                occ = [i for i, t in enumerate(_toks) if t == nonce_tid[n]]
                return occ[-1] if occ else None

            adds = []
            q_slot = slot_of(ns[qi])
            adds.append((d_lm[lms[qi]] * S, q_slot))          # target: query slot
            for di in range(k):
                if di == qi:
                    continue
                d_slot = slot_of(ns[di])
                if d_slot is None:
                    continue
                if arm == "content":
                    adds.append((d_lm[lms[di]] * S, d_slot))
                elif arm == "random":
                    adds.append((rand_like(d_lm[lms[di]] * S), d_slot))
                # bare: no distractor install
            handles = []
            for vec, pos in adds:
                if pos is None:
                    continue
                vt = torch.tensor(vec, dtype=torch.float32, device=dev)
                handles.append(dec[L].register_forward_hook(
                    mh3.add_hook_at(vt, pos)))
            with torch.no_grad():
                lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
            for hd in handles:
                hd.remove()
            truth = mh3.CONT_OF[lms[qi]]
            others = [c for c in mh3.CONTINENTS if c != truth]
            out.append(float(lo[cont_ids[truth]]
                             - max(lo[cont_ids[c]] for c in others)))
        return out

    k_grid = [k for k in args.k_grid if k <= min(len(valid), len(nonces))]
    if k_grid != list(args.k_grid):
        print(f"[cap] k_grid capped to {k_grid} (n_valid={len(valid)})")

    # ── k=1: full pass over valid landmarks = gate-0 + per-landmark baseline ──
    base_margin = {lm: margins_for_draw([lm], "content")[0] for lm in valid}
    m1_vals = np.array([base_margin[lm] for lm in valid])
    m1 = float(m1_vals.mean())
    m1_se = float(m1_vals.std(ddof=1) / np.sqrt(len(m1_vals)))
    gate0 = bool(m1 > 3 * m1_se and m1 > 0)
    print(f"[cap] gate-0: m(1)={m1:.3f} SE={m1_se:.3f} expressed={gate0} "
          f"acc={float(np.mean(m1_vals > 0)):.2f}")

    # ── k sweep: same landmark draws across arms (paired) ──────────────────
    arms = list(args.arms)
    draws_by_k = {k: [sorted(rng.choice(valid, size=k, replace=False).tolist())
                      for _ in range(args.draws)] for k in k_grid if k >= 2}
    result_arms = {a: {"curve": {}, "acc": {}, "cci": {}, "raw": {}}
                   for a in arms}
    for a in arms:
        result_arms[a]["curve"]["1"] = m1
        result_arms[a]["acc"]["1"] = float(np.mean(m1_vals > 0))
        result_arms[a]["raw"]["1"] = {lm: base_margin[lm] for lm in valid}

    for k in [k for k in k_grid if k >= 2]:
        for a in arms:
            mat = np.zeros((args.draws, k))
            bas = np.zeros((args.draws, k))
            for ri, lms in enumerate(draws_by_k[k]):
                mat[ri] = margins_for_draw(lms, a)
                bas[ri] = [base_margin[lm] for lm in lms]
            cci = cci_at_k(mat, bas, rng)
            result_arms[a]["curve"][str(k)] = float(mat.mean())
            result_arms[a]["acc"][str(k)] = float(np.mean(mat > 0))
            result_arms[a]["cci"][str(k)] = cci
            result_arms[a]["raw"][str(k)] = {
                "margins": mat.tolist(),
                "draws": draws_by_k[k]}
            print(f"  [{a}] k={k} m={mat.mean():.3f} "
                  f"acc={float(np.mean(mat > 0)):.2f} "
                  f"CCI={cci['ldi']:.2f} p={cci['p']}")

    # ── score frozen gates on the CONTENT arm ──────────────────────────────
    curve = [result_arms["content"]["curve"][str(k)] for k in k_grid]
    material = bool((m1 - curve[-1]) > args.material_frac * abs(m1))
    cliff = cliff_stat_logk(k_grid, curve, material_frac=args.material_frac)
    per_k_cci = {k: result_arms["content"]["cci"][str(k)]
                 for k in k_grid if k >= 2}
    g2, beta = g2_form(k_grid, curve, rng, args.n_null, args.alpha, material)
    verdict = aggregate_verdict_cap(gate0, material, cliff, per_k_cci, g2,
                                    args.alpha, args.cliff_thresh)
    print("\n[cap] content curve: "
          + " ".join(f"k{k}={m:.2f}"
                     for k, m in zip(k_grid, curve, strict=True)))
    print(f"[cap] material={material} cliff={cliff['cliff_ratio']:.2f} "
          f"median_CCI={verdict['median_cci']:.2f} beta={beta:.3f} "
          f"g2={'PASS' if g2 and g2.verdict else ('n/a' if g2 is None else 'fail')}")
    print(f"[cap] VERDICT -> {verdict['call']}")

    result = {
        "model_id": args.model_id, "seed": args.seed, "scale": S,
        "ref_layer": L, "k_grid": k_grid, "draws": args.draws,
        "alpha": args.alpha, "cliff_thresh": args.cliff_thresh,
        "material_frac": args.material_frac, "arms": arms,
        "nonces": nonces, "valid_landmarks": valid,
        "gate0": {"m1": m1, "m1_se": m1_se, "expressed": gate0},
        "content_gates": {
            "material": material, "cliff": cliff,
            "g2": (asdict(g2) if g2 is not None else None),
            "beta_hat": beta},
        "verdict": verdict,
        "arms_data": result_arms}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "holo_cap.json").write_text(
        json.dumps(_json_safe(result), indent=2, allow_nan=False))
    print(f"[cap] wrote {out}/holo_cap.json")
    if not gate0:
        print("[cap] ⚠ gate-0 FAILED — verdict INCONCLUSIVE")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="P-HOLO-CAP capacity law")
    ap.add_argument("--validate", action="store_true",
                    help="no-model self-test of the capacity detectors")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--ref-layer", type=int, default=9)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--draws", type=int, default=12)
    ap.add_argument("--k-grid", type=int, nargs="+", default=list(K_GRID_DEFAULT))
    ap.add_argument("--arms", nargs="+", default=["content", "random", "bare"],
                    choices=["content", "random", "bare"])
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--cliff-thresh", type=float, default=2.5)
    ap.add_argument("--material-frac", type=float, default=0.15)
    ap.add_argument("--n-null", type=int, default=500)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/holo-cap/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha, args.cliff_thresh, args.material_frac)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
