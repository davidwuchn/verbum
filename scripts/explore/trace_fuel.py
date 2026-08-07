"""§P-TRACE-FUEL — the fuel theorem measured on the tape (dynamic converse of §P-FUEL).

Pre-reg FROZEN s317 (Michael-approved GO):
mementum/knowledge/explore/normal-forms-are-eigenmodes.md §P-TRACE-FUEL.

§P-FUEL found NO-FUEL-COORDINATE at STATIC-read grain → fuel is tape-resident
(de Carvalho's identity is about the DYNAMIC reduction derivation). This probe
feeds the kernel-certified reduction trace t0 = t1 = ... = t_ℓ (the tape
unfolding, in-distribution: the §P-TYPE-GRAM-1 probes ARE truncated chains),
captures the type-register signal at each `=` step-boundary (one spent fuel
unit), and asks whether integrated type signal S scales with ℓ and — the prize
— accumulates NON-IDEMPOTENTLY (a DUP trace reducing the SAME redex n times
shows no per-step decay beyond LIN's). Recovers the FU3 knife §P-FUEL couldn't
reach statically.

Register (λ measure): Y reused VERBATIM from §P-FUEL (§P-TYPE-GRAM-1 kind
subspace, held-out fit). Per-step s_j = ‖proj of the `=`-position residual onto
the type subspace‖, band L18-31. S = Σ s_j; trajectory {s_j} for the decay test.

Arms (teacher-forced, one qwen3-4b load, read-only): LIN (distinct redexes) /
DUP (same redex ×n = non-idempotence test bed) / NULL-CHAIN (inert restatements
T = T = ..., ℓ=0 fuel, matched `=` count = surface-length floor).

Gates (α=0.05): TF1 ACCUMULATES (S∝ℓ vs matched-trace-length null) · TF2
TYPE-SPECIFIC (> random-subspace ∧ > S_norm ∧ real-step > null-chain-step) · TF3
NON-IDEMPOTENT (DUP per-step slope not below LIN's — term-shrinkage matched;
idempotent decay = DUP decays faster) · TF4 STEP-LOCKED (advisory) · TF5 SANE.
Verdicts DYNAMIC-FUEL(+NON-IDEMPOTENT) / DYNAMIC-FUEL-IDEMPOTENT /
STATIC-CONFIRMED-NULL (falsifier) / LENGTH-ONLY (falsifier) / VOID.
A-priori 35/15/25/20/5.

Reuse (λ one_way, no fork): fuel_theorem (fit_type_subspace/y_project/y_norm/
spearman/_orthonormal/_load_type_probes/band_layers/certify/_atoms/_redex/
_inert/kind_margin_heldout/TYPE_SUBSPACE_DIM/N_RAND_SUBSPACES/N_PERM) +
verbum.lambda_ast (parse/reduce/pretty) + verbum.dsp.nulls + verbum.jlens.
New code = trace rendering + `=`-position mapping + per-step trajectory + TF gates.

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

from verbum.dsp.nulls import NullDraws, Register, gate  # noqa: E402
from verbum.lambda_ast import parse, pretty, reduce  # noqa: E402

# ══════════════════════════════════════════════════════════════════════════
# Construction (FROZEN §P-TRACE-FUEL)
# ══════════════════════════════════════════════════════════════════════════
N_LENS = (1, 2, 3, 4, 5, 6, 8, 10)     # ℓ ladder (DUP trace ~O(n²) → capped at 10)
N_ATOM_SEEDS = 6                        # replicate atom/structure draws per (family, n)
_ALPHA = 0.05


# ── trace rendering + `=`-position mapping ────────────────────────────────
def _render_trace(term_str: str) -> tuple[str, int]:
    """Kernel-certified reduction chain 't0 = t1 = ... = t_ℓ' + step count ℓ."""
    r = reduce(parse(term_str))
    chain = " = ".join(pretty(t) for t in r.trace)
    return chain, int(r.steps)


def _null_chain(inert_term: str, n_eq: int) -> str:
    """Inert restatement chain T = T = ... (n_eq boundaries, ℓ=0 fuel)."""
    return " = ".join([inert_term] * (n_eq + 1))


def eq_positions(tok, text: str) -> list[int]:
    """Token indices in tok(text) whose decoded piece is the '=' separator."""
    ids = tok(text, add_special_tokens=True).input_ids
    pos = []
    for i, tid in enumerate(ids):
        piece = tok.decode([tid])
        if piece.strip() == "=":
            pos.append(i)
    return pos


# ── trace battery ─────────────────────────────────────────────────────────
def build_trace_battery(rng: np.random.Generator) -> list[dict]:
    battery: list[dict] = []

    def emit(term: str, family: str, ell_expected: int | None = None):
        chain, ell = _render_trace(term)
        r = reduce(parse(term))
        battery.append({"chain": chain, "family": family, "ell": ell,
                        "is_nf": r.status.value == "normal_form",
                        "n": ell if ell_expected is None else ell_expected})

    for _ in range(N_ATOM_SEEDS):
        for n in N_LENS:
            # LIN — n distinct single-step redexes (each step a fresh judgment)
            ats = ff._atoms(rng, 3 * n)
            lin_args = [ff._redex(ats[3 * i], ats[3 * i + 1], ats[3 * i + 2])
                        for i in range(n)]
            emit("h " + " ".join(lin_args), "LIN", n)

            # DUP — the SAME redex n times (n identical spent-fuel events)
            a, b, c = ff._atoms(rng, 3)
            emit("h " + " ".join([ff._redex(a, b, c)] * n), "DUP", n)

            # NULL-CHAIN — inert restatement, ℓ=0 fuel, n `=` boundaries
            ats = ff._atoms(rng, 3)
            inert = "h " + " ".join([ff._inert(ats[0], ats[1], ats[2])] * n)
            chain = _null_chain(inert, n)
            battery.append({"chain": chain, "family": "NULL", "ell": 0,
                            "is_nf": True, "n": n})
    return battery


# ══════════════════════════════════════════════════════════════════════════
# Gates + verdict — PURE (no torch; what --validate exercises)
# ══════════════════════════════════════════════════════════════════════════
def _slope(y: np.ndarray) -> float:
    """Least-squares slope of y vs index (per-step trajectory decay/flat)."""
    y = np.asarray(y, float)
    if y.size < 2:
        return 0.0
    x = np.arange(y.size, dtype=float)
    x = x - x.mean()
    d = float(x @ x)
    return float(x @ (y - y.mean()) / d) if d > 1e-12 else 0.0


def compute_gates_trace(d: dict, rng: np.random.Generator,
                        alpha: float = _ALPHA) -> dict:
    S = np.asarray(d["S"], float)
    S_norm = np.asarray(d["S_norm"], float)
    ell = np.asarray(d["ell"], float)
    tok = np.asarray(d["tok"], float)
    rand_rhos = np.asarray(d["rand_rhos"], float)
    real_step = np.asarray(d["real_step"], float)
    null_step = np.asarray(d["null_step"], float)
    slope_lin = np.asarray(d["slope_lin"], float)
    slope_dup = np.asarray(d["slope_dup"], float)
    tok_bin = np.round(tok / 8.0).astype(int)

    # ── TF1 ACCUMULATES: ρ(S,ℓ) vs matched-trace-length null ──
    v1 = ff.spearman(S, ell)
    d1 = np.array([ff.spearman(S, ff._perm_within_bins(ell, tok_bin, rng))
                   for _ in range(ff.N_PERM)])
    tf1 = gate(v1, NullDraws("matched_trace_length", d1), "greater",
               alpha, "TF1", Register.value, Register.value)

    # ── TF2 TYPE-SPECIFIC: > random-subspace ∧ > S_norm ∧ real-step > null-step ──
    r_type = ff.spearman(S, ell)
    r_norm = ff.spearman(S_norm, ell)
    tf2_rand = gate(r_type, NullDraws("random_subspace", rand_rhos), "greater",
                    alpha, "TF2_rand", Register.value, Register.value)
    tf2_beats_norm = bool(r_type > r_norm)
    # real fuel-bearing steps carry more type signal than inert restatements
    obs_rn = float(real_step.mean() - null_step.mean())
    pooled = np.concatenate([real_step, null_step])
    lab = np.concatenate([np.ones(real_step.size), np.zeros(null_step.size)])
    dperm = np.array([
        (lambda L: pooled[L == 1].mean() - pooled[L == 0].mean())(rng.permutation(lab))
        for _ in range(ff.N_PERM)])
    tf2_step = gate(obs_rn, NullDraws("real_vs_null_step", dperm), "greater",
                    alpha, "TF2_step", Register.value, Register.value)
    tf2_pass = bool(tf2_rand.verdict and tf2_beats_norm and tf2_step.verdict)

    # ── TF3 NON-IDEMPOTENT: DUP per-step slope NOT below LIN's (shrinkage matched) ──
    obs_ds = float(slope_dup.mean() - slope_lin.mean())
    both = np.concatenate([slope_dup, slope_lin])
    labs = np.concatenate([np.ones(slope_dup.size), np.zeros(slope_lin.size)])
    d3 = np.array([
        (lambda L: both[L == 1].mean() - both[L == 0].mean())(rng.permutation(labs))
        for _ in range(ff.N_PERM)])
    # idempotent ⟺ DUP decays FASTER than LIN ⟺ Δslope significantly < 0
    p_idem = float((1 + np.sum(d3 <= obs_ds)) / (1 + d3.size))
    tf3_non_idem = bool(p_idem >= alpha)      # not significantly more decay → non-idem

    # ── TF4 STEP-LOCKED (advisory) ──
    tf4 = float(d.get("step_locked", 0.0))

    # ── TF5 SANE (void-gate) ──
    kind_margin = float(d["kind_margin"])
    all_nf = bool(d["all_nf"])
    tf5_pass = bool(kind_margin > 0.0 and all_nf)

    # ── verdict tree (frozen) ──
    if not tf5_pass:
        verdict = "VOID"
    elif not tf1.verdict:
        verdict = "STATIC-CONFIRMED-NULL"
    elif not tf2_pass:
        verdict = "LENGTH-ONLY"
    elif tf3_non_idem:
        verdict = "DYNAMIC-FUEL (+NON-IDEMPOTENT)"
    else:
        verdict = "DYNAMIC-FUEL-IDEMPOTENT"

    return {
        "verdict": verdict,
        "gates": {
            "TF1": _g(tf1) | {"pass": tf1.verdict},
            "TF2": {"r_type": r_type, "r_norm": r_norm, "p_rand": tf2_rand.p,
                    "beats_norm": tf2_beats_norm, "real_minus_null": obs_rn,
                    "p_step": tf2_step.p, "pass": tf2_pass},
            "TF3": {"slope_dup": float(slope_dup.mean()),
                    "slope_lin": float(slope_lin.mean()),
                    "delta_slope": obs_ds, "p_idem": p_idem,
                    "non_idem": tf3_non_idem},
            "TF4_step_locked": tf4,
            "TF5": {"kind_margin": kind_margin, "all_nf": all_nf, "pass": tf5_pass},
        },
    }


def _g(gt) -> dict:
    return {"value": gt.value, "null_mean": gt.null_mean, "p": gt.p,
            "sign_ok": gt.sign_ok, "null": gt.null_name}


# ══════════════════════════════════════════════════════════════════════════
# --validate — planted worlds exercise every verdict
# ══════════════════════════════════════════════════════════════════════════
def _planted(kind: str, rng: np.random.Generator) -> dict:
    lin_n = np.repeat(N_LENS, N_ATOM_SEEDS).astype(float)
    dup_n = np.repeat(N_LENS, N_ATOM_SEEDS).astype(float)
    null_n = np.repeat(N_LENS, N_ATOM_SEEDS).astype(float)
    ell = np.concatenate([lin_n, dup_n, np.zeros_like(null_n)])
    tok = np.concatenate([lin_n * 8, dup_n * 10, null_n * 8])
    noise = rng.normal(0, 0.05, ell.size)

    # per-step summaries
    real_step = rng.normal(1.0, 0.1, 400)
    null_step = rng.normal(1.0, 0.1, 400)          # default: real ≈ null
    slope_lin = rng.normal(-0.2, 0.05, 48)         # both families shrink → decay
    slope_dup = rng.normal(-0.2, 0.05, 48)         # non-idem: DUP ≈ LIN
    rand_rhos = rng.normal(0.0, 0.08, ff.N_RAND_SUBSPACES)
    S_norm = 0.02 * tok + rng.normal(0, 0.05, ell.size)

    if kind == "dynamic_nonidem":
        S = 0.1 * ell + noise
        real_step = rng.normal(1.3, 0.1, 400)      # fuel steps > inert
        null_step = rng.normal(0.6, 0.1, 400)
    elif kind == "dynamic_idem":
        S = 0.1 * ell + noise
        real_step = rng.normal(1.3, 0.1, 400)
        null_step = rng.normal(0.6, 0.1, 400)
        slope_dup = rng.normal(-0.6, 0.05, 48)     # DUP decays FASTER → idempotent
    elif kind == "static_null":
        S = noise                                   # no ℓ signal
    elif kind == "length_only":
        S = 0.1 * ell + rng.normal(0, 0.30, ell.size)
        S_norm = 0.1 * ell + rng.normal(0, 0.02, ell.size)   # norm tracks ℓ better
        real_step = rng.normal(1.0, 0.1, 400)      # real ≈ null (not type-specific)
        null_step = rng.normal(1.0, 0.1, 400)
    else:                                            # void
        S = 0.1 * ell + noise

    kind_margin = -1.0 if kind == "void" else 1.0
    return {"S": S, "S_norm": S_norm, "ell": ell, "tok": tok,
            "rand_rhos": rand_rhos, "real_step": real_step, "null_step": null_step,
            "slope_lin": slope_lin, "slope_dup": slope_dup,
            "kind_margin": kind_margin, "all_nf": kind != "void", "step_locked": 0.5}


def validate() -> bool:
    rng = np.random.default_rng(0)
    want = {
        "dynamic_nonidem": "DYNAMIC-FUEL (+NON-IDEMPOTENT)",
        "dynamic_idem": "DYNAMIC-FUEL-IDEMPOTENT",
        "static_null": "STATIC-CONFIRMED-NULL",
        "length_only": "LENGTH-ONLY",
        "void": "VOID",
    }
    ok = True
    for kind, exp in want.items():
        got = compute_gates_trace(_planted(kind, rng), rng)["verdict"]
        good = got == exp
        ok &= good
        print(f"  verdict[{kind:16s}] {got:32s} {'✓' if good else '✗ want ' + exp}")

    # primitive: trace rendering + `=` count = ℓ (kernel-certified)
    b = build_trace_battery(np.random.default_rng(1))
    lin = next(x for x in b if x["family"] == "LIN" and x["n"] == 8)
    dup = next(x for x in b if x["family"] == "DUP" and x["n"] == 8)
    nul = next(x for x in b if x["family"] == "NULL" and x["n"] == 8)
    p_eq = (lin["chain"].count(" = ") == 8 and dup["chain"].count(" = ") == 8
            and nul["chain"].count(" = ") == 8)
    p_ell = lin["ell"] == 8 and dup["ell"] == 8 and nul["ell"] == 0
    print(f"  primitive `=`-count==ℓ (LIN/DUP) ∧ NULL ℓ=0 w/ 8 `=` "
          f"{'✓' if p_eq and p_ell else '✗ FAIL'}")
    ok &= p_eq and p_ell

    p_nf = all(x["is_nf"] for x in b)
    print(f"  primitive all real traces NF {'✓' if p_nf else '✗ FAIL'}")
    ok &= p_nf

    print("validate:", "ALL PASS ✓" if ok else "FAIL ✗")
    return ok


# ══════════════════════════════════════════════════════════════════════════
# main — model load, per-step capture, gates
# ══════════════════════════════════════════════════════════════════════════
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-train", type=int, default=40)
    ap.add_argument("--n-test", type=int, default=15)
    ap.add_argument("--out", default="results/trace-fuel/qwen3-4b")
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
    print(f"[tf] {args.model_id} dev={dev} n_layers={nl} "
          f"band=L{tband[0]}..L{tband[-1]}", flush=True)

    def capture_all(text: str):
        resid, _ids = jlens.capture_residuals(model, tok, text)
        return resid  # dict[layer] -> (seq, d)

    def band_at(resid, pos: int) -> np.ndarray:
        return np.stack([resid[li][pos].float().cpu().numpy() for li in tband])

    # ── fit type subspace on held-out §P-TYPE-GRAM-1 probes (Y verbatim) ──
    tp_path = _ROOT / "opcodes" / "data" / "type_probes.json"
    n_train, n_test = (8, 4) if args.smoke else (args.n_train, args.n_test)
    train, test = ff._load_type_probes(tp_path, n_train, n_test)
    print(f"[tf] type probes: train={len(train)} test={len(test)}", flush=True)
    ops = sorted({o for _, o, _ in train})
    kinds = sorted({k for _, _, k in train})
    op_idx = {o: i for i, o in enumerate(ops)}
    kind_idx = {k: i for i, k in enumerate(kinds)}

    def cap_last(text: str) -> np.ndarray:
        resid = capture_all(text)
        last = next(iter(resid.values())).shape[0] - 1
        return band_at(resid, last)

    h_tr = np.stack([cap_last(p) for p, _, _ in train])
    op_ids = np.array([op_idx[o] for _, o, _ in train])
    kind_ids = np.array([kind_idx[k] for _, _, k in train])
    mu, U = ff.fit_type_subspace(h_tr, op_ids, kind_ids)
    h_te = np.stack([cap_last(p) for p, _, _ in test])
    kind_te = np.array([kind_idx[k] for _, _, k in test])
    kmargin = ff.kind_margin_heldout(h_te, kind_te, mu, U)
    print(f"[tf] held-out kind_margin={kmargin:.4f}", flush=True)

    dsz = h_tr.shape[2]
    R = [ff._orthonormal(rng.normal(size=(dsz, ff.TYPE_SUBSPACE_DIM)))
         for _ in range(ff.N_RAND_SUBSPACES)]

    # ── trace battery ──
    battery = build_trace_battery(rng)
    if args.smoke:
        battery = ([x for x in battery if x["family"] == "LIN"][:4]
                   + [x for x in battery if x["family"] == "DUP"][:4]
                   + [x for x in battery if x["family"] == "NULL"][:4])
    print(f"[tf] battery n={len(battery)} "
          f"(LIN {sum(x['family'] == 'LIN' for x in battery)} / "
          f"DUP {sum(x['family'] == 'DUP' for x in battery)} / "
          f"NULL {sum(x['family'] == 'NULL' for x in battery)})", flush=True)

    S, S_norm, S_rand, ell, tokn, fam = [], [], [], [], [], []
    slope_lin, slope_dup = [], []
    real_step, null_step = [], []
    for i, x in enumerate(battery):
        resid = capture_all(x["chain"])
        positions = eq_positions(tok, x["chain"])
        if not positions:                       # NF with 0 steps → no boundary
            continue
        hpos = [band_at(resid, p) for p in positions]
        sj = np.array([ff.y_project(h, mu, U) for h in hpos])
        snj = np.array([ff.y_norm(h, mu) for h in hpos])
        srj = np.array([[float(np.mean([np.linalg.norm(Rk.T @ (h[li] - mu[li]))
                                        for li in range(len(tband))]))
                         for h in hpos] for Rk in R])   # (N_RAND, n_steps)
        S.append(float(sj.sum()))
        S_norm.append(float(snj.sum()))
        S_rand.append(srj.sum(axis=1))          # (N_RAND,)
        ell.append(x["ell"])
        tokn.append(len(tok(x["chain"]).input_ids))
        fam.append(x["family"])
        if x["family"] == "LIN":
            slope_lin.append(_slope(sj))
            real_step.extend(sj.tolist())
        elif x["family"] == "DUP":
            slope_dup.append(_slope(sj))
            real_step.extend(sj.tolist())
        elif x["family"] == "NULL":
            null_step.extend(sj.tolist())
        if (i + 1) % 20 == 0:
            print(f"[tf]   captured {i + 1}/{len(battery)}", flush=True)

    S = np.array(S)
    ell = np.array(ell, float)
    S_rand = np.array(S_rand)                    # (n_traces, N_RAND)
    rand_rhos = np.array([ff.spearman(S_rand[:, j], ell)
                          for j in range(S_rand.shape[1])])

    dat = {"S": S, "S_norm": np.array(S_norm), "ell": ell, "tok": np.array(tokn, float),
           "rand_rhos": rand_rhos, "real_step": np.array(real_step),
           "null_step": np.array(null_step), "slope_lin": np.array(slope_lin),
           "slope_dup": np.array(slope_dup), "kind_margin": kmargin,
           "all_nf": all(x["is_nf"] for x in battery), "step_locked": 0.0}
    res = compute_gates_trace(dat, rng, _ALPHA)

    g = res["gates"]
    t1, t2, t3, t5 = g["TF1"], g["TF2"], g["TF3"], g["TF5"]
    print(f"[tf] TF1 rho={t1['value']:.3f} p={t1['p']:.4f} {t1['pass']} | "
          f"TF2 r_type={t2['r_type']:.3f} r_norm={t2['r_norm']:.3f} "
          f"real-null={t2['real_minus_null']:.3f} p_step={t2['p_step']:.4f} "
          f"{t2['pass']} | TF3 dup={t3['slope_dup']:.3f} lin={t3['slope_lin']:.3f} "
          f"delta={t3['delta_slope']:.3f} p_idem={t3['p_idem']:.4f} "
          f"non_idem={t3['non_idem']} | "
          f"TF5 margin={t5['kind_margin']:.3f} {t5['pass']}", flush=True)
    print(f"[tf] VERDICT: {res['verdict']}", flush=True)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"model_id": args.model_id, "n_layers": nl, "band": [tband[0], tband[-1]],
            "n_traces": len(S), "n_train": len(train), "n_test": len(test),
            "seed": args.seed, "smoke": args.smoke}
    json.dump({**res, "means": {"kind_margin": kmargin}, "meta": meta},
              open(out / "results.json", "w"), indent=1)
    np.savez_compressed(out / "trace_fuel.npz", S=S, S_norm=dat["S_norm"], ell=ell,
                        tok=dat["tok"], family=np.array(fam), rand_rhos=rand_rhos,
                        slope_lin=dat["slope_lin"], slope_dup=dat["slope_dup"])
    print(f"[tf] wrote {out}/results.json + trace_fuel.npz", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
