#!/usr/bin/env python3
# register: operator/orbit - ALPHABET+LENGTH-matched control (s339 shadow, step 2)
"""P-CL-COLLAPSE-3-alpha - is the arity-run OPERATOR-SHADOW extensional or LEXICAL?

FROZEN (s339, Michael GO). The arity-matched control (P-CL-COLLAPSE-3-arity) found
the s339 positional whisper SURVIVES length-matching (AM1 within<across p=0.0002,
length_r 0.17) -> NOT length. BUT same-function spellings shared ~2x more combinator
letters than different-function ones (within-func alphabet-Jaccard 0.56-0.59 vs
across 0.26-0.30) -> the positional signal is likely the s321 OPERATIONAL/LEXICAL
register (residual tracks what is WRITTEN), not extensional equality.

THE CONTROL. Remove the alphabet confound BY CONSTRUCTION: every spelling uses the
SAME alphabet {S,K} (combinator-set-Jaccard = 1.0 for ALL pairs, within and across
function). Different functions computed from the same two letters. THEN partial out
residual token-length. If same-function is STILL closer -> the shadow is genuinely
function-driven (extensional). If it VANISHES -> it was surface form (lexical/length).

Pools (kernel-certified, combset=={S,K}, globally distinct):
  arity 1: identity(->x) / Kx(->K x) / Sx(->S x)
  arity 2: first(->f)   / apply(->f x) / second(->x)

Make-or-breaks (stratified same-arity; shuffled-FUNCTION null inside stratum):
  AM1p POSITIONAL, LENGTH-PARTIALLED (make-or-break): regress pairwise cosine-distance
       on |token-length diff| (same-arity), test residual within-function < across-
       function, beats in-stratum null p<0.05 AND effect > FLOOR_POS. Alphabet is
       already constant -> a pass here is NOT alphabet and NOT length.
  AM2 DECAY-RATE (robust operator test): as s339.
  Verify: within/across alphabet-Jaccard (must be ~1.0/1.0) + raw AM1 (un-partialled).

FROZEN verdict tree:
  G0 INSTRUMENT (void) operator-exists + det 0.0 + >=2 strata each >=2 funcs>=2 spell
  AM2 fires             -> CONVERGENCE
  AM1p fires, AM2 null  -> EXTENSIONAL-SHADOW (survives alphabet+length control)
  both null             -> LEXICAL-EXPLAINED (the arity shadow was surface form;
                           the fourth-register NO-CONVERGE finding is airtight)

A-priori (favored LEXICAL-EXPLAINED; SHADOW real weight per Michael):
  LEXICAL-EXPLAINED 55 / EXTENSIONAL-SHADOW 30 / CONVERGENCE 5 / VOID 10.

License: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from itertools import combinations
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_SCRIPT_DIR.parents[1] / "src"))

import dmd_transport as dt  # noqa: E402
from cl_collapse_3_arity import (  # noqa: E402
    _length_covariate,
    _strat_null,
)
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
FLOOR_POS = 0.02
N_PER = 30

# {S,K}-exact pools (kernel-verified s339; combset=={S,K}, globally distinct;
# alphabet-Jaccard within==across==1.0 by construction).
FAMILIES: dict[tuple[str, str], list[str]] = {
    ("1", "identity"): ["S K K", "S K S", "S S K K", "S S S K", "K S K K K"],
    ("1", "Kx"): ["K K S", "S K K K", "S K S K", "K K K K S", "K K S K K"],
    ("1", "Sx"): ["K S K", "K S S", "S K K S", "S K S S", "K K K S K"],
    ("2", "first"): ["K K S K S", "S S K K K", "S S S K K", "K S K K K K",
                     "K S K K S K"],
    ("2", "apply"): ["K S K K S", "K S S K K", "K S S K S", "S S K S K",
                     "S S S S K"],
    ("2", "second"): ["S K", "K S K K", "K S S K", "S K K S K", "S K S S K"],
}
ARITY_ATOMS = {"1": ["x"], "2": ["f", "x"]}
NF_TMPL = {"identity": "{0}", "Kx": "K {0}", "Sx": "S {0}",
           "first": "{0}", "apply": "{0} {1}", "second": "{1}"}
ATOMS = list("abcdefghmnpqrtuvxz")
_C = set("SKIBCWDYM")


def _reduce(text: str) -> str:
    return pretty(normal_form(parse(text)))


def _combset(sp: str) -> frozenset:
    return frozenset(t for t in sp.replace("(", " ").replace(")", " ").split()
                     if t in _C)


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
    probes: list[dict] = []
    sd = seed
    for (ar, fn), spellings in FAMILIES.items():
        atoms_slots = ARITY_ATOMS[ar]
        n_slots = len(atoms_slots)
        for si, spell in enumerate(spellings):
            assert _combset(spell) == frozenset("SK"), f"{spell} not {{S,K}}"
            tmpl = spell + " " + " ".join("{" + str(k) + "}" for k in range(n_slots))
            tok_len = len(spell.split())
            group = f"{ar}:{fn}:{si}"
            for atoms in _atom_tuples(n_slots, n_per, sd):
                sd += 1
                text = tmpl.format(*atoms)
                got = _reduce(text)
                want = _reduce(NF_TMPL[fn].format(*atoms))
                assert got == want, f"{text}->{got} != {fn}->{want}"
                probes.append({"id": f"{group}:{'-'.join(atoms)}", "arity": ar,
                               "function": fn, "group": group, "text": text,
                               "tok_len": tok_len})
    return probes


def _length_partial_matrix(D: np.ndarray, g_len: np.ndarray,
                           g_ar: np.ndarray) -> np.ndarray:
    """Residual distance after regressing pairwise distance on |token-length diff|
    over same-arity pairs (removes the residual length effect; alphabet is already
    constant). Same-arity entries -> residual; others left as-is (unused by the
    same-arity-only stratified null)."""
    n = D.shape[0]
    iu, ju = np.triu_indices(n, k=1)
    same_ar = g_ar[iu] == g_ar[ju]
    d = D[iu, ju]
    dl = np.abs(g_len[iu] - g_len[ju]).astype(float)
    fin = np.isfinite(d) & same_ar
    R = D.copy()
    if np.sum(fin) >= 3 and np.std(dl[fin]) > 0:
        b1, b0 = np.polyfit(dl[fin], d[fin], 1)
        for k in np.where(fin)[0]:
            i, j = iu[k], ju[k]
            resid = D[i, j] - (b0 + b1 * dl[k])
            R[i, j] = R[j, i] = resid
    return R


def _alpha_balance(groups: list[str], g_ar: np.ndarray,
                   spell_of: dict[str, str]) -> dict:
    """Within/across-function combinator-set Jaccard per arity (should be ~1/1)."""
    out = {}
    for a in np.unique(g_ar):
        items = [(g.split(":")[1], _combset(spell_of[g]))
                 for g, ar in zip(groups, g_ar, strict=False) if ar == a]
        wj, aj = [], []
        for (f1, s1), (f2, s2) in combinations(items, 2):
            j = len(s1 & s2) / len(s1 | s2) if (s1 | s2) else 1.0
            (wj if f1 == f2 else aj).append(j)
        out[str(a)] = {"within_jaccard": float(np.mean(wj)) if wj else None,
                       "across_jaccard": float(np.mean(aj)) if aj else None}
    return out


def analyse(H, arity, func, groups, tok_len_by_group, spell_by_group,
            det_ok=True) -> dict:
    n, lp1, _d = H.shape
    L = lp1 - 1
    dt_gates = dt.analyse(H, np.random.default_rng(SEED))
    op_exists = bool(dt_gates["g2"]["pass"])

    ar_fn: dict[str, dict[str, set]] = {}
    for a, f, g in zip(arity.tolist(), func.tolist(), groups.tolist(), strict=False):
        ar_fn.setdefault(a, {}).setdefault(f, set()).add(g)
    strata_ok = sum(1 for fns in ar_fn.values()
                    if sum(1 for gs in fns.values() if len(gs) >= 2) >= 2)
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

    D_pos = _cosdist_matrix(Ch)
    am1_raw = _strat_null(D_pos, g_fn, g_ar, N_NULL,
                          np.random.default_rng(SEED + 1), FLOOR_POS)
    R = _length_partial_matrix(D_pos, g_len, g_ar)
    am1_partial = _strat_null(R, g_fn, g_ar, N_NULL,
                              np.random.default_rng(SEED + 6), FLOOR_POS)
    M_decay = _diff_decay_matrix(Cz, Bn, lam)
    am2 = _strat_null(M_decay, g_fn, g_ar, N_NULL,
                      np.random.default_rng(SEED + 2), FLOOR_D_DECAY)
    lengthcov = _length_covariate(D_pos, g_len, g_ar)
    alpha_bal = _alpha_balance(order, g_ar, spell_by_group)

    if not g0_pass:
        verdict = "VOID"
    elif am2["pass"]:
        verdict = "CONVERGENCE"
    elif am1_partial["pass"]:
        verdict = "EXTENSIONAL-SHADOW"
    else:
        verdict = "LEXICAL-EXPLAINED"

    return {
        "n_probes": n, "L": L, "P": P, "var_explained": var_explained,
        "g0": {"op_exists": op_exists, "family_ok": family_ok, "det_ok": det_ok,
               "pass": g0_pass, "strata_ok": strata_ok},
        "spectrum": {"mean_abs_lam": float(np.mean(lam)) if lam.size else 0.0,
                     "departure_from_normality": dmd_m["departure"]},
        "am1_positional_raw": am1_raw,
        "am1_positional_length_partialled": am1_partial,
        "am2_decay": am2,
        "mechanism_length_cov": lengthcov,
        "alphabet_balance": alpha_bal,
        "n_groups": len(order), "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Planted worlds (reuse cl_collapse_3_arity structure; the verdict hinges on the
# LENGTH-PARTIALLED positional gate)
# ---------------------------------------------------------------------------
def _planted(kind: str, **kw):
    import cl_collapse_3_arity as ca
    m = {"LEXICAL-EXPLAINED": "LENGTH-ARTIFACT",
         "EXTENSIONAL-SHADOW": "OPERATOR-SHADOW",
         "CONVERGENCE": "CONVERGENCE", "VOID": "VOID"}[kind]
    return ca._planted(m, **kw)


def run_validate() -> int:
    log("[cl3x] --validate: driving planted worlds through the real gate path")
    expect = {"LEXICAL-EXPLAINED": "LEXICAL-EXPLAINED",
              "EXTENSIONAL-SHADOW": "EXTENSIONAL-SHADOW",
              "CONVERGENCE": "CONVERGENCE", "VOID": "VOID"}
    ok = True
    for kind, want in expect.items():
        H, ar, fn, gr = _planted(kind)
        tl = {g: 3 + (g.count("f") % 3) for g in set(gr.tolist())}
        sp = {g: "S K" for g in set(gr.tolist())}
        res = analyse(H, ar, fn, gr, tl, sp, det_ok=True)
        got = res["verdict"]
        passed = got == want
        ok = ok and passed
        a1p, a2 = res["am1_positional_length_partialled"], res["am2_decay"]
        log(f"[cl3x]   {kind:18s} -> {got:18s} (want {want:18s}) "
            f"AM1p D={a1p['obs']:+.3f}(p={a1p['p_value']:.3f},pass={a1p['pass']}) "
            f"AM2 D={a2['obs']:+.4f}(pass={a2['pass']}) {'OK' if passed else 'FAIL'}")
    log(f"[cl3x] validate {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--n-per", type=int, default=N_PER)
    ap.add_argument("--out", default="results/p_cl_collapse_3_alpha_s339/run")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    corpus = build_corpus(args.n_per, SEED)
    log(f"[cl3x] corpus: {len(corpus)} probes | "
        f"{len({c['group'] for c in corpus})} spellings | "
        f"arities {sorted({c['arity'] for c in corpus})} | "
        f"functions {sorted({c['function'] for c in corpus})} | alphabet {{S,K}}")

    be = dt.RealBackend(args.model_id, args.device, args.dtype)
    trajs = []
    for i, item in enumerate(corpus):
        trajs.append(be.trajectory(item["text"]))
        if (i + 1) % 50 == 0:
            log(f"[cl3x] captured {i + 1}/{len(corpus)}")
    H = np.stack(trajs)
    log(f"[cl3x] H shape {H.shape}")

    rep = np.stack([be.trajectory(corpus[i]["text"])
                    for i in range(min(DET_CHECK_N, len(corpus)))])
    value_dev = float(np.max(np.abs(rep - H[: rep.shape[0]])))
    det_ok = value_dev <= DET_TOL
    log(f"[cl3x] det-repeat value_dev={value_dev} ok={det_ok}")

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
    sp = {c["group"]: " ".join(c["text"].split()[:c["tok_len"]]) for c in corpus}
    res = analyse(H, arity, func, groups, tl, sp, det_ok=det_ok)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    corpus_hash = hashlib.sha256(
        json.dumps([c["text"] for c in corpus], sort_keys=True).encode()
    ).hexdigest()[:16]
    meta = {
        "probe": "P-CL-COLLAPSE-3-alpha",
        "frozen": "s339 pre-data freeze (Michael GO): alphabet({S,K})+length-matched "
                  "control for the P-CL-COLLAPSE-3-arity OPERATOR-SHADOW",
        "pre_data_instantiations": {
            "P_PCA": P_PCA, "PRIMARY_RANK": PRIMARY_RANK, "LATE_LAYERS": LATE_LAYERS,
            "N_PER": args.n_per, "N_NULL": N_NULL, "ALPHA": ALPHA,
            "FLOOR_POS": FLOOR_POS, "FLOOR_D_DECAY": FLOOR_D_DECAY, "SEED": SEED,
            "families": {f"{a}:{f}": len(s) for (a, f), s in FAMILIES.items()},
            "apriori_masses": {"LEXICAL-EXPLAINED": 55, "EXTENSIONAL-SHADOW": 30,
                               "CONVERGENCE": 5, "VOID": 10},
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
                                 "tok_len": c["tok_len"]},
                                default=_json_native) + "\n")
    np.savez_compressed(out / "trajectories.npz", H=H.astype(np.float16))

    a1r = res["am1_positional_raw"]
    a1p = res["am1_positional_length_partialled"]
    a2 = res["am2_decay"]
    log(f"[cl3x] === VERDICT: {res['verdict']} ===")
    log(f"[cl3x] alphabet_balance={res['alphabet_balance']}")
    log(f"[cl3x] AM1raw D={a1r['obs']:+.4f}(p={a1r['p_value']:.3f}) | "
        f"AM1_len-partialled D={a1p['obs']:+.4f} (w={a1p['within']:.3f} "
        f"a={a1p['across']:.3f} p={a1p['p_value']:.3f} pass={a1p['pass']}) | "
        f"AM2 D={a2['obs']:+.4f}(p={a2['p_value']:.3f}) | "
        f"length_r={res['mechanism_length_cov']['pearson_r']:.3f}")
    log(f"[cl3x] wrote {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
