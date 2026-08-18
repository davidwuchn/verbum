#!/usr/bin/env python3
# register: operator/orbit - ARITY-STRATIFIED length control (s339 shadow re-run)
"""P-CL-COLLAPSE-3-arity - is the s339 positional whisper LENGTH or a real SHADOW?

FROZEN spec (s339, Michael GO). Follow-up to P-CL-COLLAPSE-3-operator
(NO-ORBITAL-CONVERGENCE, but a marginal positional whisper within<across p=0.0498).
That whisper is confounded: in s339 each function lived at its OWN arity (identity=1
atom, W=2, B=3), so "same-function" == "same-length" by construction -> longer
co-intensional prompts inflate across-distances.

THE FIX. Break the function=arity=length confound: put MULTIPLE functions at the
SAME arity, then compare same-function vs different-function ONLY WITHIN a fixed
arity (length matched). Fixed-arity pools (kernel-certified, giveaway-primitive
excluded, globally-distinct spellings):
  arity 1: identity(->x) / double(->x x) / triple(->x x x)
  arity 2: apply(->f x)  / dup(->f x x)  / second(->x)

TWO make-or-breaks (stratified: same-arity pairs only; shuffled-FUNCTION-label null
run INSIDE each arity stratum) + a mechanism check:
  AM1 POSITIONAL (the whisper, length-controlled): within-function cosine-distance <
      across-function, within each arity, beats the in-stratum null, p<0.05, effect
      > FLOOR_POS. Direct re-test of the s339 whisper with length held fixed.
  AM2 DECAY-RATE (robust operator test, stratified): co-extensional differences ride
      faster-decaying modes (s339's statistic), floor FLOOR_D_DECAY.
  MECHANISM (advisory): corr(cosine-distance, |token-length diff|) over same-arity
      pairs - if the s339 whisper was length, this is strong and AM1 goes null.

FROZEN verdict tree:
  G0 INSTRUMENT (void) operator-exists + det 0.0 + >=2 arity strata each >=2 funcs
                       with >=2 spellings -> else VOID
  AM2 fires            -> CONVERGENCE (strong; compositionality S5 cell reopens)
  AM1 fires, AM2 null  -> OPERATOR-SHADOW (faint positional signal survives length-
                          matching but no dynamical convergence - the shadow)
  both null            -> LENGTH-ARTIFACT (s339 whisper was length; NO-CONVERGE clean)

Verdicts + a-priori (favored LENGTH-ARTIFACT; SHADOW given real weight per Michael):
  LENGTH-ARTIFACT 50 / OPERATOR-SHADOW 30 / CONVERGENCE 5 / VOID 15.

Reuses the P-CL-COLLAPSE-3-operator analysis machinery (DMD modes, decay-rate,
cosdist, non-normal diagnostics) + sec 5a capture. `--validate` drives 4 planted
worlds (LENGTH-ARTIFACT / OPERATOR-SHADOW / CONVERGENCE / VOID).

License: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_SCRIPT_DIR.parents[1] / "src"))

import cl_collapse_3_operator as op  # noqa: E402  (reuse the s339 analysis machinery)
import dmd_transport as dt  # noqa: E402
from cl_collapse_3_operator import (  # noqa: E402
    ALPHA,
    DET_CHECK_N,
    DET_TOL,
    FLOOR_D_DECAY,
    LATE_LAYERS,
    P_PCA,
    PRIMARY_RANK,
    SEED,
    _cosdist_matrix,
    _diff_decay_matrix,
    _dmd_modes,
    _group_centroids,
    _json_native,
)
from combinator_relationship_map import git_sha, log  # noqa: E402

from verbum.lambda_ast import normal_form, parse, pretty  # noqa: E402
from verbum.operator_dmd import pca_basis, reduced_dmd  # noqa: E402

N_NULL = 5000
FLOOR_POS = 0.02       # min meaningful positional (cosine-distance) gap
N_PER = 30

# fixed-arity function pools (kernel-verified s339; giveaway-primitive excluded,
# globally-distinct spellings). key = (arity_str, function_name).
FAMILIES: dict[tuple[str, str], list[str]] = {
    ("1", "identity"): ["W K", "C K B", "C K C", "C K K", "C K S"],
    ("1", "double"): ["W I", "I W I", "S I I", "W S I", "B I W I"],
    ("1", "triple"): ["W W", "I W W", "S W I", "W I W", "B I W W"],
    ("2", "apply"): ["B W K", "C K W", "S K B", "S K C", "S K K"],
    ("2", "dup"): ["C S I", "B S C I", "C C I S", "I C S I", "B C I S I"],
    ("2", "second"): ["C K", "K I", "S K", "I C K", "I K I"],
}
ARITY_ATOMS = {"1": ["x"], "2": ["f", "x"]}
# expected normal form per function (kernel-certified at build)
TARGET_NF = {"identity": "x", "double": "x x", "triple": "x x x",
             "apply": "f x", "dup": "f x x", "second": "x"}
ATOMS = list("abcdefghmnpqrtuvxz")


def _reduce(text: str) -> str:
    return pretty(normal_form(parse(text)))


def _atom_tuples(n_slots: int, n: int, seed: int) -> list[tuple[str, ...]]:
    rng = np.random.default_rng(seed)
    seen: set[tuple[str, ...]] = set()
    out: list[tuple[str, ...]] = []
    tries = 0
    while len(out) < n and tries < n * 100:
        tries += 1
        pick = tuple(rng.choice(ATOMS, size=n_slots, replace=False))
        if pick not in seen:
            seen.add(pick)
            out.append(pick)
    return out


def build_corpus(n_per: int, seed: int) -> list[dict]:
    """Kernel-certified fixed-arity pools. Each probe carries arity + function +
    group + token-length. group = arity:function:spelling_idx."""
    probes: list[dict] = []
    sd = seed
    for (ar, fn), spellings in FAMILIES.items():
        atoms_slots = ARITY_ATOMS[ar]
        n_slots = len(atoms_slots)
        for si, spell in enumerate(spellings):
            tmpl = spell + " " + " ".join("{" + str(k) + "}" for k in range(n_slots))
            tok_len = len(spell.replace("(", " ").replace(")", " ").split())
            group = f"{ar}:{fn}:{si}"
            # canonical reference spelling per function (certify equivalence on
            # the SAME atoms - the extensional-equality certificate)
            canon = {"identity": "I {0}", "double": "W I {0}",
                     "triple": "W (W I) {0}", "apply": "I {0} {1}",
                     "dup": "W {0} {1}", "second": "K I {0} {1}"}[fn]
            for atoms in _atom_tuples(n_slots, n_per, sd):
                sd += 1
                text = tmpl.format(*atoms)
                got = _reduce(text)
                want = _reduce(canon.format(*atoms))
                assert got == want, f"{text}->{got} != {fn}->{want}"
                probes.append({"id": f"{group}:{'-'.join(atoms)}", "arity": ar,
                               "function": fn, "group": group, "text": text,
                               "tok_len": tok_len})
    return probes


# ---------------------------------------------------------------------------
# Stratified statistics (same-arity pairs only; null shuffles function WITHIN arity)
# ---------------------------------------------------------------------------
def _strat_within_across(M: np.ndarray, func: np.ndarray,
                         arity: np.ndarray) -> tuple[float, float]:
    """Mean within-function and across-function distance over SAME-ARITY pairs
    only (cross-arity pairs excluded = the length control)."""
    n = M.shape[0]
    iu, ju = np.triu_indices(n, k=1)
    same_ar = arity[iu] == arity[ju]
    same_fn = func[iu] == func[ju]
    d = M[iu, ju]
    fin = np.isfinite(d)
    wmask = fin & same_ar & same_fn
    amask = fin & same_ar & ~same_fn
    within = float(d[wmask].mean()) if np.any(wmask) else float("nan")
    across = float(d[amask].mean()) if np.any(amask) else float("nan")
    return within, across


def _strat_null(M: np.ndarray, func: np.ndarray, arity: np.ndarray, n_null: int,
                rng: np.random.Generator, floor: float) -> dict:
    """Shuffle FUNCTION labels WITHIN each arity stratum (preserves arity + the
    same-arity pair sets + per-arity function-class sizes). Observed = across -
    within (>0 = same-function closer at matched arity)."""
    within, across = _strat_within_across(M, func, arity)
    obs = across - within
    arities = np.unique(arity)
    null = np.empty(n_null)
    fperm = func.copy()
    idx_by_ar = {a: np.where(arity == a)[0] for a in arities}
    for i in range(n_null):
        for a in arities:
            ix = idx_by_ar[a]
            fperm[ix] = rng.permutation(func[ix])
        w, ac = _strat_within_across(M, fperm, arity)
        null[i] = ac - w
    p = float((np.sum(null >= obs) + 1) / (n_null + 1))
    return {"within": within, "across": across, "obs": float(obs), "floor": floor,
            "null_mean": float(np.mean(null)), "null_std": float(np.std(null)),
            "p_value": p, "pass": bool(obs > floor and p < ALPHA)}


def _length_covariate(M: np.ndarray, tok_len: np.ndarray,
                      arity: np.ndarray) -> dict:
    """Pearson corr of pairwise cosine-distance with |token-length diff| over
    same-arity pairs (mechanism: is distance driven by length?)."""
    n = M.shape[0]
    iu, ju = np.triu_indices(n, k=1)
    same_ar = arity[iu] == arity[ju]
    d = M[iu, ju]
    dl = np.abs(tok_len[iu] - tok_len[ju]).astype(float)
    fin = np.isfinite(d) & same_ar
    if np.sum(fin) < 3 or np.std(dl[fin]) == 0:
        return {"pearson_r": float("nan"), "n_pairs": int(np.sum(fin))}
    r = float(np.corrcoef(d[fin], dl[fin])[0, 1])
    return {"pearson_r": r, "n_pairs": int(np.sum(fin))}


# ---------------------------------------------------------------------------
# Analysis + gate path
# ---------------------------------------------------------------------------
def analyse(H: np.ndarray, arity: np.ndarray, func: np.ndarray, groups: np.ndarray,
            tok_len_by_group: dict[str, int], det_ok: bool = True) -> dict:
    n, lp1, d = H.shape
    L = lp1 - 1

    dt_gates = dt.analyse(H, np.random.default_rng(SEED))
    op_exists = bool(dt_gates["g2"]["pass"])

    # family structure: >=2 arity strata each with >=2 functions with >=2 spellings
    strata_ok = 0
    ar_fn_groups: dict[str, dict[str, set]] = {}
    for a, f, g in zip(arity.tolist(), func.tolist(), groups.tolist(), strict=False):
        ar_fn_groups.setdefault(a, {}).setdefault(f, set()).add(g)
    for fns in ar_fn_groups.values():
        if sum(1 for gs in fns.values() if len(gs) >= 2) >= 2:
            strata_ok += 1
    family_ok = strata_ok >= 2
    g0_pass = op_exists and family_ok and det_ok

    snaps = H.reshape(n * lp1, -1)
    comps, mean, var_explained = pca_basis(snaps, P_PCA, seed=SEED)
    Z = (H - mean) @ comps
    P = Z.shape[2]
    X = Z[:, :L, :].reshape(n * L, P).T
    Xp = Z[:, 1:, :].reshape(n * L, P).T
    dmd = reduced_dmd(X, Xp, PRIMARY_RANK)
    dmd_m = _dmd_modes(dmd)
    Bn, lam = dmd_m["Bn"], dmd_m["lam"]

    order = sorted(set(groups.tolist()))
    g_ar = np.array([arity[groups == g][0] for g in order])
    g_fn = np.array([func[groups == g][0] for g in order])
    g_len = np.array([tok_len_by_group[g] for g in order])

    zbar = Z[:, -LATE_LAYERS:, :].mean(axis=1)
    zbar = zbar - zbar.mean(axis=0, keepdims=True)
    hbar = H[:, -LATE_LAYERS:, :].mean(axis=1)
    hbar = hbar - hbar.mean(axis=0, keepdims=True)
    Cz = _group_centroids(zbar, groups, order)
    Ch = _group_centroids(hbar, groups, order)

    # AM1 positional (raw d_model cosine, the s339 whisper) - stratified
    D_pos = _cosdist_matrix(Ch)
    am1 = _strat_null(D_pos, g_fn, g_ar, N_NULL, np.random.default_rng(SEED + 1),
                      FLOOR_POS)
    # AM2 decay-rate (operator) - stratified
    M_decay = _diff_decay_matrix(Cz, Bn, lam)
    am2 = _strat_null(M_decay, g_fn, g_ar, N_NULL, np.random.default_rng(SEED + 2),
                      FLOOR_D_DECAY)
    # mechanism: length covariate on the positional matrix
    lengthcov = _length_covariate(D_pos, g_len, g_ar)

    # per-arity breakdown (advisory)
    per_arity = {}
    for a in np.unique(g_ar):
        amask = g_ar == a
        idx = np.where(amask)[0]
        subpos = D_pos[np.ix_(idx, idx)]
        w, ac = _strat_within_across(subpos, g_fn[idx],
                                     np.array([a] * len(idx)))
        per_arity[a] = {"n_groups": int(amask.sum()),
                        "within_pos": w, "across_pos": ac, "D_pos": float(ac - w)}

    if not g0_pass:
        verdict = "VOID"
    elif am2["pass"]:
        verdict = "CONVERGENCE"
    elif am1["pass"]:
        verdict = "OPERATOR-SHADOW"
    else:
        verdict = "LENGTH-ARTIFACT"

    return {
        "n_probes": n, "L": L, "d": d, "P": P, "var_explained": var_explained,
        "g0": {"op_exists": op_exists, "family_ok": family_ok, "det_ok": det_ok,
               "pass": g0_pass, "strata_ok": strata_ok,
               "op_exists_gap": dt_gates["g2"]["gap"]},
        "spectrum": {"mean_abs_lam": float(np.mean(lam)) if lam.size else 0.0,
                     "departure_from_normality": dmd_m["departure"],
                     "eigvec_cond": dmd_m["eigvec_cond"]},
        "am1_positional": am1,
        "am2_decay": am2,
        "mechanism_length_cov": lengthcov,
        "per_arity": per_arity,
        "n_groups": len(order), "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Planted worlds
# ---------------------------------------------------------------------------
def _planted(kind: str, lp1: int = 41, d: int = 120, n_mid: int = 40,
             n_per: int = 15, n_func: int = 3, n_spell: int = 4) -> tuple:
    """(arity, function) structured trajectories engineered to hit `kind`.
    Two arities x n_func functions x n_spell spellings x n_per instances."""
    rng = np.random.default_rng({"LENGTH-ARTIFACT": 11, "OPERATOR-SHADOW": 22,
                                 "CONVERGENCE": 33, "VOID": 44}[kind])
    ns = nf_ = (d - n_mid) // 2
    Q, T = op._op(rng, d, (0.985, 0.995), (0.965, 0.975), (0.55, 0.70), ns, nf_)
    slow_ax, fast_ax = Q[:, :ns], Q[:, -nf_:]
    mid_ax = Q[:, ns:d - nf_]
    n_midm = mid_ax.shape[1]

    arities = ["1"] if kind == "VOID" else ["1", "2"]
    # per-arity coherent offset (the "length" proxy: cross-arity distance)
    arity_off = {a: rng.standard_normal(n_midm) for a in arities}
    # per-function offset (positional, in SLOW modes) for SHADOW/CONVERGE
    fn_slow = {f: rng.standard_normal(ns) for f in range(n_func)}

    H, AR, FN, GR = [], [], [], []
    for a in arities:
        for fi in range(n_func):
            for si in range(n_spell):
                sp_fast = rng.standard_normal(nf_)
                sp_slow = rng.standard_normal(ns)
                for _ in range(n_per):
                    h0 = mid_ax @ (arity_off[a] * 4.0)  # arity/length offset
                    if kind == "LENGTH-ARTIFACT":
                        # NO function structure: only arity offset + per-spelling
                        h0 += slow_ax @ (sp_slow * 1.5)
                        h0 += fast_ax @ (sp_fast * 1.5)
                    elif kind == "OPERATOR-SHADOW":
                        # function offset in SLOW (positional close, persists ->
                        # AM1 fires); spelling small in SLOW (no faster decay ->
                        # AM2 null)
                        h0 += slow_ax @ (fn_slow[fi] * 3.0 + sp_slow * 0.4)
                        h0 += fast_ax @ (sp_fast * 0.3)
                    elif kind == "CONVERGENCE":
                        # function offset in SLOW; spelling in FAST -> same-func
                        # differences decay faster -> AM2 fires
                        h0 += slow_ax @ (fn_slow[fi] * 2.0)
                        h0 += fast_ax @ (sp_fast * 3.0)
                    else:  # VOID single arity
                        h0 += slow_ax @ (sp_slow * 1.5)
                        h0 += fast_ax @ (sp_fast * 1.5)
                    traj = np.empty((lp1, d))
                    traj[0] = h0
                    for e in range(lp1 - 1):
                        traj[e + 1] = T @ traj[e] + 0.01 * rng.standard_normal(d)
                    H.append(traj)
                    AR.append(a)
                    FN.append(f"f{fi}")
                    GR.append(f"{a}:f{fi}:{si}")
    return (np.stack(H), np.array(AR), np.array(FN), np.array(GR))


def run_validate() -> int:
    log("[cl3a] --validate: driving planted worlds through the real gate path")
    expect = {"LENGTH-ARTIFACT": "LENGTH-ARTIFACT",
              "OPERATOR-SHADOW": "OPERATOR-SHADOW",
              "CONVERGENCE": "CONVERGENCE", "VOID": "VOID"}
    ok = True
    for kind, want in expect.items():
        H, ar, fn, gr = _planted(kind)
        tl = {g: 3 for g in set(gr.tolist())}
        res = analyse(H, ar, fn, gr, tl, det_ok=True)
        got = res["verdict"]
        passed = got == want
        ok = ok and passed
        a1, a2 = res["am1_positional"], res["am2_decay"]
        log(f"[cl3a]   {kind:16s} -> {got:16s} (want {want:16s}) "
            f"AM1_pos D={a1['obs']:+.3f}(p={a1['p_value']:.3f},pass={a1['pass']}) "
            f"AM2_decay D={a2['obs']:+.4f}(p={a2['p_value']:.3f},pass={a2['pass']}) "
            f"{'OK' if passed else 'FAIL'}")
    log(f"[cl3a] validate {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--n-per", type=int, default=N_PER)
    ap.add_argument("--out", default="results/p_cl_collapse_3_arity_s339/run")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    corpus = build_corpus(args.n_per, SEED)
    log(f"[cl3a] corpus: {len(corpus)} probes | "
        f"{len({c['group'] for c in corpus})} spellings | "
        f"arities {sorted({c['arity'] for c in corpus})} | "
        f"functions {sorted({c['function'] for c in corpus})}")

    be = dt.RealBackend(args.model_id, args.device, args.dtype)
    trajs = []
    for i, item in enumerate(corpus):
        trajs.append(be.trajectory(item["text"]))
        if (i + 1) % 50 == 0:
            log(f"[cl3a] captured {i + 1}/{len(corpus)}")
    H = np.stack(trajs)
    log(f"[cl3a] H shape {H.shape}")

    rep = np.stack([be.trajectory(corpus[i]["text"])
                    for i in range(min(DET_CHECK_N, len(corpus)))])
    value_dev = float(np.max(np.abs(rep - H[: rep.shape[0]])))
    det_ok = value_dev <= DET_TOL
    log(f"[cl3a] det-repeat value_dev={value_dev} ok={det_ok}")

    if args.device == "mps":
        try:
            torch = be.torch
            del be.model
            torch.mps.empty_cache()
        except Exception:
            pass

    arity = np.array([c["arity"] for c in corpus])
    func = np.array([c["function"] for c in corpus])
    groups = np.array([c["group"] for c in corpus])
    tl = {c["group"]: c["tok_len"] for c in corpus}
    res = analyse(H, arity, func, groups, tl, det_ok=det_ok)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    corpus_hash = hashlib.sha256(
        json.dumps([c["text"] for c in corpus], sort_keys=True).encode()
    ).hexdigest()[:16]
    meta = {
        "probe": "P-CL-COLLAPSE-3-arity",
        "frozen": "s339 pre-data freeze (Michael GO): arity-matched length control "
                  "for the P-CL-COLLAPSE-3-operator positional whisper",
        "pre_data_instantiations": {
            "P_PCA": P_PCA, "PRIMARY_RANK": PRIMARY_RANK, "LATE_LAYERS": LATE_LAYERS,
            "N_PER": args.n_per, "N_NULL": N_NULL, "ALPHA": ALPHA,
            "FLOOR_POS": FLOOR_POS, "FLOOR_D_DECAY": FLOOR_D_DECAY, "SEED": SEED,
            "families": {f"{a}:{f}": len(s) for (a, f), s in FAMILIES.items()},
            "apriori_masses": {"LENGTH-ARTIFACT": 50, "OPERATOR-SHADOW": 30,
                               "CONVERGENCE": 5, "VOID": 15},
        },
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "model_id": args.model_id, "device": args.device, "dtype": args.dtype,
        "smoke": args.smoke, "n_probes": len(corpus),
        "corpus_hash": corpus_hash, "git_sha": git_sha(),
        "det_value_dev": value_dev, "det_ok": det_ok,
        "global_verdict": res["verdict"], "gates": res,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))
    with (out / "results.jsonl").open("w") as fh:
        for c in corpus:
            fh.write(json.dumps({"id": c["id"], "arity": c["arity"],
                                 "function": c["function"], "group": c["group"],
                                 "tok_len": c["tok_len"], "text_len": len(c["text"])},
                                default=_json_native) + "\n")
    np.savez_compressed(out / "trajectories.npz", H=H.astype(np.float16))

    a1, a2, mc = res["am1_positional"], res["am2_decay"], res["mechanism_length_cov"]
    log(f"[cl3a] === VERDICT: {res['verdict']} ===")
    log(f"[cl3a] G0 pass={res['g0']['pass']} "
        f"strata={res['g0']['strata_ok']} det={det_ok}")
    log(f"[cl3a] AM1 pos D={a1['obs']:+.4f} (w={a1['within']:.3f} a={a1['across']:.3f} "
        f"p={a1['p_value']:.3f} pass={a1['pass']}) | AM2 decay D={a2['obs']:+.4f} "
        f"(p={a2['p_value']:.3f} pass={a2['pass']}) | length_r={mc['pearson_r']:.3f}")
    log(f"[cl3a] wrote {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
