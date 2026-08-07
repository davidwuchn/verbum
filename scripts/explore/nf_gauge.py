"""§P-NF-GAUGE — sign-resolution: register reads remaining WORK or DONE-ness?

Pre-reg FROZEN s318 (Michael-approved GO) + AMENDMENT (s318, pre-build,
Michael-approved: added the MATCH-padded family for NG1 decoupling power):
mementum/knowledge/explore/normal-forms-are-eigenmodes.md §P-NF-GAUGE.

§P-FUEL and §P-TRACE-FUEL both killed the INCREASING fuel-accumulator reading
but left a re-signed hook: the register may be a DECREASING distance-to-NF
coordinate. Two committed measurements DISAGREE on the sign — §P-FUEL MATCH
(token-controlled, static) says NF=HIGH (ρ=−0.538); §P-TRACE-FUEL decay
(uncontrolled, per-step) says NF=LOW. The confound masking which is LOCAL TOKEN
LENGTH. This probe pins the sign PER-FRAME under a proper local-token control.

Unlike §P-TRACE-FUEL (which INTEGRATED S=Σs_j vs total ℓ → found S counts `=`
boundaries), this stays PER-FRAME: at the j-th `=` boundary the most-recently-
completed term is t_j → remaining steps r_j=ℓ−j (kernel-certified), current-term
tokens ct_j (the local surface control). NG1 = partial ρ(s_j, r_j | ct_j); the
SIGN of that partial ρ selects the verdict.

AMENDMENT rationale: LIN/DUP alone have ct~r collinear (each β-step shrinks the
term ~fixed tokens) → the matched-ct null has no power → NG1 fails by
construction. The MATCH family (h (C..)×k (Z..)×P; k active redexes reduce, P
inert Z pads ride verbatim) holds ct~const across a trace while r=k−j sweeps →
decoupling. Varying (k,P) fills the (ct,r) plane so the matched-ct null gets
real power. Exactly how §P-FUEL's MATCH enabled FU4.

Register (λ measure): Y reused VERBATIM from §P-FUEL/§P-TRACE-FUEL
(§P-TYPE-GRAM-1 kind subspace, held-out fit, band L18-31, value register).
Controls s_norm (y_norm), s_rand (matched-dim random subspace).

Gates (α=0.05): NG1 LOCAL-DECODE+sign (partial ρ(s,r|ct) ≠ 0 two-sided vs
matched-ct null; sign picks verdict) · NG2 TYPE-SPECIFIC (|partial_type| >
|partial_norm| AND > random-subspace null) · NG3 ENGAGEMENT (REQUIRED — real
reduction frames > inert NULL frames; the reduction-driven precondition) · NG4
CROSS-GRAIN (advisory — first-frame ρ(s,ℓ) sign vs MATCH −0.538) · NG5 SANE.
Verdicts REMAINING-WORK-GAUGE(ρ>0) / DONENESS-DETECTOR(ρ<0) /
LENGTH-DECREASE-ONLY (falsifier) / VOID. A-priori 20/35/35/10.

Reuse (λ one_way, no fork): fuel_theorem (fit_type_subspace/y_project/y_norm/
kind_margin_heldout/_orthonormal/_load_type_probes/band_layers/spearman/
partial_spearman/_perm_within_bins/_atoms/_redex/_inert/TYPE_SUBSPACE_DIM/
N_RAND_SUBSPACES/N_PERM) + trace_fuel (_render_trace/eq_positions/_null_chain) +
verbum.lambda_ast + verbum.jlens. New code = MATCH-padded family + per-frame
(r,ct) extraction + signed partial-Spearman + matched-ct null + three-way gate.

License: MIT (lambda provenance).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import fuel_theorem as ff  # noqa: E402  (§P-FUEL harness — stats + geometry library)
import trace_fuel as tf  # noqa: E402   (§P-TRACE-FUEL harness — trace rendering)

from verbum.lambda_ast import parse, reduce  # noqa: E402

# ══════════════════════════════════════════════════════════════════════════
# Construction (FROZEN §P-NF-GAUGE + MATCH amendment)
# ══════════════════════════════════════════════════════════════════════════
N_LENS = (1, 2, 3, 4, 5, 6, 8, 10)     # ℓ ladder for LIN / DUP / NULL
MATCH_K = (2, 4, 6, 8, 10)             # MATCH active-redex count = ℓ
MATCH_P = (2, 8, 14)                   # MATCH inert-pad count → ct plateaus
N_ATOM_SEEDS = 5
_ALPHA = 0.05


def _match_term(rng: np.random.Generator, k: int, pad: int) -> str:
    """MATCH-padded term: k active C-redexes + `pad` inert Z-pads.

    Only the k C-redexes fire (ℓ=k); the Z pads ride along verbatim in every
    rendered frame → ct held ~const across the trace while r=k−j sweeps k→1.
    Per-frame analog of §P-FUEL's MATCH (the decoupling instrument)."""
    ats = ff._atoms(rng, 3 * (k + pad))
    parts = [ff._redex(ats[3 * i], ats[3 * i + 1], ats[3 * i + 2]) for i in range(k)]
    parts += [ff._inert(ats[3 * i], ats[3 * i + 1], ats[3 * i + 2])
              for i in range(k, k + pad)]
    return "h " + " ".join(parts)


def build_gauge_battery(rng: np.random.Generator) -> list[dict]:
    """LIN / DUP / MATCH / NULL traces with kernel-certified labels."""
    battery: list[dict] = []

    def emit_real(term: str, family: str, k: int = 0, pad: int = 0):
        chain, ell = tf._render_trace(term)
        r = reduce(parse(term))
        battery.append({"chain": chain, "family": family, "ell": ell,
                        "is_nf": r.status.value == "normal_form", "k": k, "pad": pad})

    for _ in range(N_ATOM_SEEDS):
        for n in N_LENS:
            # LIN — n distinct single-step redexes
            ats = ff._atoms(rng, 3 * n)
            lin = [ff._redex(ats[3 * i], ats[3 * i + 1], ats[3 * i + 2])
                   for i in range(n)]
            emit_real("h " + " ".join(lin), "LIN")

            # DUP — the SAME redex n times
            a, b, c = ff._atoms(rng, 3)
            emit_real("h " + " ".join([ff._redex(a, b, c)] * n), "DUP")

            # NULL — inert restatement chain (ℓ=0, n `=` boundaries)
            ats = ff._atoms(rng, 3)
            inert = "h " + " ".join([ff._inert(ats[0], ats[1], ats[2])] * n)
            battery.append({"chain": tf._null_chain(inert, n), "family": "NULL",
                            "ell": 0, "is_nf": True, "k": 0, "pad": 0})

        # MATCH — k active redexes + pad inert Z-pads (the decoupling instrument)
        for k in MATCH_K:
            for pad in MATCH_P:
                emit_real(_match_term(rng, k, pad), "MATCH", k, pad)
    return battery


REAL_FAMILIES = ("LIN", "DUP", "MATCH")   # reduction-bearing frames


# ══════════════════════════════════════════════════════════════════════════
# Gates + verdict — PURE (no torch; what --validate exercises)
# ══════════════════════════════════════════════════════════════════════════
def _two_sided_p(obs: float, null: np.ndarray) -> float:
    null = np.asarray(null, float)
    return float((1 + np.sum(np.abs(null) >= abs(obs))) / (1 + null.size))


def compute_gates_gauge(d: dict, rng: np.random.Generator,
                        alpha: float = _ALPHA) -> dict:
    s = np.asarray(d["s"], float)              # real-frame type-register magnitude
    r = np.asarray(d["r"], float)              # remaining certified steps
    ct = np.asarray(d["ct"], float)            # current-term token length
    s_norm = np.asarray(d["s_norm"], float)
    rand_partials = np.asarray(d["rand_partials"], float)  # partial ρ / subspace
    real_step = np.asarray(d["real_step"], float)
    null_step = np.asarray(d["null_step"], float)
    first_s = np.asarray(d["first_s"], float)
    first_ell = np.asarray(d["first_ell"], float)
    ct_bin = np.round(ct / 4.0).astype(int)

    # ── NG1 LOCAL-DECODE (+ sign): partial ρ(s, r | ct) vs matched-ct null ──
    v1 = ff.partial_spearman(s, r, ct)
    d1 = np.array([ff.partial_spearman(s, ff._perm_within_bins(r, ct_bin, rng), ct)
                   for _ in range(ff.N_PERM)])
    p1 = _two_sided_p(v1, d1)
    ng1_pass = bool(p1 < alpha)

    # ── NG2 TYPE-SPECIFIC: |partial_type| > |partial_norm| AND > random null ──
    v_norm = ff.partial_spearman(s_norm, r, ct)
    p_rand = _two_sided_p(v1, rand_partials)
    ng2_pass = bool(abs(v1) > abs(v_norm) and p_rand < alpha)

    # ── NG3 ENGAGEMENT (REQUIRED): real reduction frames > inert NULL frames ──
    obs_rn = float(real_step.mean() - null_step.mean())
    pooled = np.concatenate([real_step, null_step])
    lab = np.concatenate([np.ones(real_step.size), np.zeros(null_step.size)])
    dperm = np.array([
        (lambda L: pooled[L == 1].mean() - pooled[L == 0].mean())(rng.permutation(lab))
        for _ in range(ff.N_PERM)])
    p3 = float((1 + np.sum(dperm >= obs_rn)) / (1 + dperm.size))
    ng3_pass = bool(p3 < alpha and obs_rn > 0)

    # ── NG4 CROSS-GRAIN (advisory): first-frame ρ(s,ℓ) sign vs MATCH −0.538 ──
    first_rho = ff.spearman(first_s, first_ell)
    ng4_agrees = bool(first_rho < 0)          # <0 ⇒ agrees with doneness (MATCH)

    # ── NG5 SANE (void-gate) ──
    kind_margin = float(d["kind_margin"])
    all_nf = bool(d["all_nf"])
    ng5_pass = bool(kind_margin > 0.0 and all_nf)

    # ── verdict tree (frozen) ──
    if not ng5_pass:
        verdict = "VOID"
    elif not ng3_pass:                        # not reduction-driven → surface
        verdict = "LENGTH-DECREASE-ONLY"
    elif not ng1_pass:                        # no signed coordinate survives control
        verdict = "LENGTH-DECREASE-ONLY"
    elif not ng2_pass:                        # generic magnitude, not the type register
        verdict = "LENGTH-DECREASE-ONLY"
    elif v1 > 0:
        verdict = "REMAINING-WORK-GAUGE"
    else:
        verdict = "DONENESS-DETECTOR"

    return {
        "verdict": verdict,
        "gates": {
            "NG1": {"partial_rho": v1, "p": p1, "null_mean": float(d1.mean()),
                    "sign": ("pos" if v1 > 0 else "neg"), "pass": ng1_pass},
            "NG2": {"partial_type": v1, "partial_norm": v_norm, "p_rand": p_rand,
                    "beats_norm": bool(abs(v1) > abs(v_norm)), "pass": ng2_pass},
            "NG3": {"real_minus_null": obs_rn, "p": p3,
                    "real_mean": float(real_step.mean()),
                    "null_mean": float(null_step.mean()), "pass": ng3_pass},
            "NG4": {"first_frame_rho": first_rho, "agrees_match": ng4_agrees},
            "NG5": {"kind_margin": kind_margin, "all_nf": all_nf, "pass": ng5_pass},
        },
    }


# ══════════════════════════════════════════════════════════════════════════
# --validate — planted worlds exercise every verdict + primitives
# ══════════════════════════════════════════════════════════════════════════
def _planted(kind: str, rng: np.random.Generator) -> dict:
    n = 240
    r = rng.integers(1, 11, n).astype(float)
    ct = 4.0 * r + rng.normal(0, 3.0, n)          # correlated but NOT collinear
    noise = rng.normal(0, 0.05, n)

    s_norm = 0.10 * ct + rng.normal(0, 0.05, n)   # generic norm ∝ length (default)
    rand_partials = rng.normal(0.0, 0.05, ff.N_RAND_SUBSPACES)  # random ⊥ r|ct
    real_step = rng.normal(1.3, 0.1, 200)          # engaged (default)
    null_step = rng.normal(0.6, 0.1, 200)
    first_s = rng.normal(0, 0.1, 40)               # advisory only
    first_ell = rng.integers(1, 11, 40).astype(float)

    if kind == "remaining_work":                   # partial ρ(s,r|ct) > 0
        s = 0.6 * r + 0.1 * ct + noise
    elif kind == "doneness":                        # partial ρ(s,r|ct) < 0
        s = -0.6 * r + 0.1 * ct + noise
    elif kind == "length_no_decode":                # s ∝ ct only → partial ≈ 0
        s = 0.5 * ct + rng.normal(0, 0.05, n)
    elif kind == "not_type":                        # norm tracks r ≥ type → ¬NG2
        # same r|ct structure in both, but the type read is noisier (rank-
        # corrupted) than the generic norm → |partial_type| < |partial_norm|
        s = 0.6 * r + 0.1 * ct + rng.normal(0, 0.5, n)
        s_norm = 0.6 * r + 0.1 * ct + rng.normal(0, 0.01, n)
    elif kind == "not_engaged":                     # real ≈ null → ¬NG3
        s = 0.6 * r + 0.1 * ct + noise
        real_step = rng.normal(1.0, 0.1, 200)
        null_step = rng.normal(1.0, 0.1, 200)
    else:                                            # void
        s = 0.6 * r + noise
    kind_margin = -1.0 if kind == "void" else 1.0
    return {"s": s, "r": r, "ct": ct, "s_norm": s_norm,
            "rand_partials": rand_partials, "real_step": real_step,
            "null_step": null_step, "first_s": first_s, "first_ell": first_ell,
            "kind_margin": kind_margin, "all_nf": kind != "void"}


def _frame_ct_r(item: dict) -> tuple[np.ndarray, np.ndarray]:
    """Word-count ct proxy + remaining-steps r per `=` frame (model-free)."""
    terms = item["chain"].split(" = ")
    ell = item["ell"]
    nb = ell if item["family"] != "NULL" else (len(terms) - 1)
    cts = np.array([len(terms[k].split()) for k in range(nb)], float)
    rs = np.array([(ell - k) if item["family"] != "NULL" else 0 for k in range(nb)],
                  float)
    return cts, rs


def validate() -> bool:
    rng = np.random.default_rng(0)
    want = {
        "remaining_work": "REMAINING-WORK-GAUGE",
        "doneness": "DONENESS-DETECTOR",
        "length_no_decode": "LENGTH-DECREASE-ONLY",
        "not_type": "LENGTH-DECREASE-ONLY",
        "not_engaged": "LENGTH-DECREASE-ONLY",
        "void": "VOID",
    }
    ok = True
    for kind, exp in want.items():
        got = compute_gates_gauge(_planted(kind, rng), rng)["verdict"]
        good = got == exp
        ok &= good
        print(f"  verdict[{kind:16s}] {got:24s} {'✓' if good else '✗ want ' + exp}")

    b = build_gauge_battery(np.random.default_rng(1))

    # primitive: MATCH ℓ==k, all real traces NF, `=`-count==ℓ
    match = [x for x in b if x["family"] == "MATCH"]
    p_mk = all(x["ell"] == x["k"] for x in match)
    p_nf = all(x["is_nf"] for x in b if x["family"] in REAL_FAMILIES)
    lin8 = next(x for x in b if x["family"] == "LIN" and x["ell"] == 8)
    p_eq = lin8["chain"].count(" = ") == 8
    print(f"  primitive MATCH ℓ==k {'✓' if p_mk else '✗'} · real all-NF "
          f"{'✓' if p_nf else '✗'} · `=`-count==ℓ {'✓' if p_eq else '✗'}")
    ok &= p_mk and p_nf and p_eq

    # primitive (the amendment): MATCH holds ct steadier than LIN across frames
    m = next(x for x in match if x["ell"] >= 6 and x["pad"] >= 8)
    lin = next(x for x in b if x["family"] == "LIN" and x["ell"] >= 6)
    mct, mr = _frame_ct_r(m)
    lct, _lr = _frame_ct_r(lin)
    cv_m = float(mct.std() / mct.mean())
    cv_l = float(lct.std() / lct.mean())
    p_decouple = cv_m < cv_l and mr.max() > mr.min()   # MATCH ct flatter, r sweeps
    print(f"  primitive DECOUPLE cv_ct(MATCH)={cv_m:.3f} < cv_ct(LIN)={cv_l:.3f} "
          f"∧ r sweeps {'✓' if p_decouple else '✗ FAIL'}")
    ok &= p_decouple

    print("validate:", "ALL PASS ✓" if ok else "FAIL ✗")
    return ok


# ══════════════════════════════════════════════════════════════════════════
# main — model load, per-frame capture, gates
# ══════════════════════════════════════════════════════════════════════════
def _rand_proj_norms(diff: np.ndarray, Rstack: np.ndarray) -> np.ndarray:
    """Band-mean ‖Rkᵀ diff_l‖ over random subspaces. diff (band,d),
    Rstack (N_RAND,d,k) → (N_RAND,)."""
    acc = np.zeros(Rstack.shape[0])
    for li in range(diff.shape[0]):
        pr = np.einsum("rdk,d->rk", Rstack, diff[li])
        acc += np.linalg.norm(pr, axis=1)
    return acc / diff.shape[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-train", type=int, default=40)
    ap.add_argument("--n-test", type=int, default=15)
    ap.add_argument("--out", default="results/nf-gauge/qwen3-4b")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return 0 if validate() else 1

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    import verbum.jlens as jlens

    rng = np.random.default_rng(args.seed)
    dev = (args.device if (args.device != "mps"
                           or torch.backends.mps.is_available()) else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    nl = jlens.n_layers(model)
    tband = ff.band_layers(nl)
    print(f"[nfg] {args.model_id} dev={dev} n_layers={nl} "
          f"band=L{tband[0]}..L{tband[-1]}", flush=True)

    def capture_all(text: str):
        resid, _ids = jlens.capture_residuals(model, tok, text)
        return resid

    def band_at(resid, pos: int) -> np.ndarray:
        return np.stack([resid[li][pos].float().cpu().numpy() for li in tband])

    def cap_last(text: str) -> np.ndarray:
        resid = capture_all(text)
        last = next(iter(resid.values())).shape[0] - 1
        return band_at(resid, last)

    # ── fit type subspace on held-out §P-TYPE-GRAM-1 probes (Y verbatim) ──
    tp_path = _ROOT / "opcodes" / "data" / "type_probes.json"
    n_train, n_test = (8, 4) if args.smoke else (args.n_train, args.n_test)
    train, test = ff._load_type_probes(tp_path, n_train, n_test)
    print(f"[nfg] type probes: train={len(train)} test={len(test)}", flush=True)
    ops = sorted({o for _, o, _ in train})
    kinds = sorted({k for _, _, k in train})
    op_idx = {o: i for i, o in enumerate(ops)}
    kind_idx = {k: i for i, k in enumerate(kinds)}
    h_tr = np.stack([cap_last(p) for p, _, _ in train])
    op_ids = np.array([op_idx[o] for _, o, _ in train])
    kind_ids = np.array([kind_idx[k] for _, _, k in train])
    mu, U = ff.fit_type_subspace(h_tr, op_ids, kind_ids)
    h_te = np.stack([cap_last(p) for p, _, _ in test])
    kind_te = np.array([kind_idx[k] for _, _, k in test])
    kmargin = ff.kind_margin_heldout(h_te, kind_te, mu, U)
    print(f"[nfg] held-out kind_margin={kmargin:.4f}", flush=True)

    dsz = h_tr.shape[2]
    Rstack = np.stack([ff._orthonormal(rng.normal(size=(dsz, ff.TYPE_SUBSPACE_DIM)))
                       for _ in range(ff.N_RAND_SUBSPACES)])       # (N_RAND,d,k)

    # ── trace battery ──
    battery = build_gauge_battery(rng)
    if args.smoke:
        battery = ([x for x in battery if x["family"] == "LIN"][:3]
                   + [x for x in battery if x["family"] == "DUP"][:3]
                   + [x for x in battery if x["family"] == "MATCH"][:4]
                   + [x for x in battery if x["family"] == "NULL"][:3])
    print(f"[nfg] battery n={len(battery)} "
          f"(LIN {sum(x['family'] == 'LIN' for x in battery)} / "
          f"DUP {sum(x['family'] == 'DUP' for x in battery)} / "
          f"MATCH {sum(x['family'] == 'MATCH' for x in battery)} / "
          f"NULL {sum(x['family'] == 'NULL' for x in battery)})", flush=True)

    # per-frame accumulators (real = LIN/DUP/MATCH; null = NULL)
    s_real, r_real, ct_real, sn_real = [], [], [], []
    rand_real: list[np.ndarray] = []
    null_step: list[float] = []
    first_s, first_ell = [], []
    for i, x in enumerate(battery):
        resid = capture_all(x["chain"])
        positions = tf.eq_positions(tok, x["chain"])
        if not positions:
            continue
        terms = x["chain"].split(" = ")
        real = x["family"] in REAL_FAMILIES
        for k, pos in enumerate(positions):
            if k >= len(terms):
                break
            h = band_at(resid, pos)
            sj = ff.y_project(h, mu, U)
            if real:
                r_j = float(x["ell"] - k)
                ct_j = float(len(tok(terms[k]).input_ids))
                s_real.append(sj)
                r_real.append(r_j)
                ct_real.append(ct_j)
                sn_real.append(ff.y_norm(h, mu))
                rand_real.append(_rand_proj_norms(h - mu, Rstack))
                if k == 0:
                    first_s.append(sj)
                    first_ell.append(float(x["ell"]))
            else:
                null_step.append(sj)
        if (i + 1) % 20 == 0:
            print(f"[nfg]   captured {i + 1}/{len(battery)} "
                  f"(real frames {len(s_real)}, null {len(null_step)})", flush=True)

    s_real = np.array(s_real)
    r_real = np.array(r_real)
    ct_real = np.array(ct_real)
    rand_real = np.array(rand_real)                 # (n_real, N_RAND)
    rand_partials = np.array([ff.partial_spearman(rand_real[:, j], r_real, ct_real)
                              for j in range(rand_real.shape[1])])

    dat = {"s": s_real, "r": r_real, "ct": ct_real, "s_norm": np.array(sn_real),
           "rand_partials": rand_partials, "real_step": s_real,
           "null_step": np.array(null_step), "first_s": np.array(first_s),
           "first_ell": np.array(first_ell), "kind_margin": kmargin,
           "all_nf": all(x["is_nf"] for x in battery if x["family"] in REAL_FAMILIES)}
    res = compute_gates_gauge(dat, rng, _ALPHA)

    g = res["gates"]
    print(f"[nfg] NG1 partial_rho={g['NG1']['partial_rho']:.3f} "
          f"p={g['NG1']['p']:.4f} sign={g['NG1']['sign']} {g['NG1']['pass']} | "
          f"NG2 t={g['NG2']['partial_type']:.3f} n={g['NG2']['partial_norm']:.3f} "
          f"p_rand={g['NG2']['p_rand']:.4f} {g['NG2']['pass']} | "
          f"NG3 real-null={g['NG3']['real_minus_null']:.3f} p={g['NG3']['p']:.4f} "
          f"{g['NG3']['pass']} | NG4 first_rho={g['NG4']['first_frame_rho']:.3f} "
          f"agrees={g['NG4']['agrees_match']} | "
          f"NG5 margin={g['NG5']['kind_margin']:.3f} {g['NG5']['pass']}", flush=True)
    print(f"[nfg] VERDICT: {res['verdict']}", flush=True)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"model_id": args.model_id, "n_layers": nl, "band": [tband[0], tband[-1]],
            "n_real_frames": int(s_real.size), "n_null_frames": len(null_step),
            "n_traces": len(battery), "n_train": len(train), "n_test": len(test),
            "seed": args.seed, "smoke": args.smoke}
    json.dump({**res, "means": {"kind_margin": kmargin}, "meta": meta},
              open(out / "results.json", "w"), indent=1)
    np.savez_compressed(out / "nf_gauge.npz", s=s_real, r=r_real, ct=ct_real,
                        s_norm=np.array(sn_real), null_step=np.array(null_step),
                        rand_partials=rand_partials, first_s=np.array(first_s),
                        first_ell=np.array(first_ell))
    print(f"[nfg] wrote {out}/results.json + nf_gauge.npz", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
