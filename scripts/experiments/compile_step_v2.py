#!/usr/bin/env python3
"""§P-COMPILE-STEP-V2 — does VALID formal notation route into whnf:*, or does
SCRAMBLED formal (same atoms, no valid computation) route there too? (s344).

§P-COMPILE-STEP (s344) → NOTATION-GATED-COMPILE: only FORMAL notation routes into
the whnf:*/fate OUTCOME register at the branch band (L30-39); the SAME computation
in prose (plain AND combinator-evoking) does not (D formal-plain +0.377, p=0.0002,
survives the |Δlen| partial, consistent across all 7 combinators). BUT the whnf:*
poles are themselves built from FORMAL reduction-chain probes → "formal→whnf:*"
carries a SURFACE-SIMILARITY component. formal-K hit ALL whnf:* poles ~uniformly
(generic notation→halt routing, not whnf:K-specific) → the verdict shows
notation→outcome-register but does NOT separate:
  · "recognized formal SYNTAX as reducible"  (lexical recognition), from
  · "COMPILED the actual computation"         (real compilation).

This V2 adds a 4th notation level — FORMAL_SCRAMBLE — that holds the surface tokens
constant and destroys the VALID computation: each frozen s344 formal item is atom-
shuffled (same multiset of lambda-syntactic atoms — λx, vars, parens, dots, →, =
— reordered so no valid reduction exists). The decisive comparison is FORMAL vs
FORMAL_SCRAMBLE, which is LENGTH-MATCHED BY CONSTRUCTION (identical atom multiset).

Question: does scrambling the formal tokens COLLAPSE the branch (validity required
⇒ COMPILATION) or PRESERVE it (formal-notation tokens alone suffice ⇒ lexical
RECOGNITION)?

THE ALGEBRAIC SPINE (rep = ds + dsp, an exact identity of paired means):
  rep = D(formal, plain)            the s344 notation effect (must replicate)
  ds  = D(formal, formal_scramble)  the VALIDITY increment (length-clean by
                                    construction)
  dsp = D(formal_scramble, plain)   the RECOGNITION floor (invalid-but-formal-token
                                    routing above prose; length-controlled by
                                    partial)
  D(formal,plain) ≡ D(formal,scramble) + D(scramble,plain)  →  rep = ds + dsp.
So under a replicated notation branch (rep significant), the branch is carried by
ds (validity), dsp (recognition), or both — the tree below is exhaustive.

Discriminator (reuses route_map_v0 frame): branch-band OUTCOME-POLE occupancy =
route17 projected onto the 8 whnf:*/div:Y poles, averaged over the top-25% layers.
All primary D on the |Δtoken-length|-RESIDUALIZED mass (mass_r); shuffled-notation-
label null within combinator; raw-rep kept only to detect a length-driven branch.

FROZEN verdict tree + a-priori (Michael GO pending, s344):
  RECOGNITION   35  rep replicates AND ds NOT sig (formal ≈ scramble) AND dsp sig
                    (scramble >> plain, survives length) — invalid formal tokens
                    route like valid ones ⇒ lexical syntax recognition, not compile
  MIXED         25  rep replicates AND ds sig AND dsp sig — a recognition floor plus
                    a validity increment (formal > scramble > plain)
  COMPILATION   20  rep replicates AND ds sig AND dsp NOT sig (scramble ≈ plain) —
                    scrambling collapses the branch to prose ⇒ VALID computation
                    required to enter the outcome register (real compile step)
  LENGTH-DRIVEN  8  rep does NOT survive the length partial but IS raw-significant —
                    the branch tracked token length, not notation or validity
  SHARED-COMPILE 5  a branch exists but rep null even raw — all levels alike
                    (computation/constant, no notation gate; s344 non-replication)
  NO-BRANCH      4  nothing reaches the outcome poles under matched computation
  VOID           3  instrument invalid (G0 fail / degenerate route)

`--validate` drives 7 planted worlds (one per verdict) through the REAL analyse path
(s331: planted plumbing == data plumbing). The LENGTH world is the adversary — a
pure length mechanism makes formal ≈ scramble (both short/high) and must NOT read
RECOGNITION; the length partial on rep must demote it to LENGTH-DRIVEN.

Bounds: Qwen3-14B, last-token, gate register. The scramble is an ATOM-order shuffle
(regex atoms: λx | word | symbol) rejoined with spaces — recognizable formal tokens
survive (recognition CAN fire), only their order is destroyed (validity cannot); the
spacing normalizes, so scramble runs a hair LONGER than formal in model tokens — the
|Δlen| partial + the LENGTH planted world guard this. Reuses the committed 17-pole
frame (results/expanded-gram/qwen3-14b) and the FROZEN s344 formal/plain corpus
(imported, not re-authored — replication is exact). FTO-clean (frame-free spectral).

License: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_ROOT = _SCRIPT_DIR.parents[1]
sys.path.insert(0, str(_ROOT / "scripts" / "explore"))
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "src"))

# canonical route-reader (committed d63da194, stable) — reuse, do not duplicate
from combinator_relationship_map import find_gate_modules, git_sha, log  # noqa: E402

# FROZEN s344 corpus + reusable stats — import, do NOT re-author (exact replication)
from compile_step import (  # noqa: E402
    ALPHA,
    BRANCH_FLOOR,
    COMBINATORS,
    DET_CHECK_N,
    DET_TOL,
    FLOOR_D,
    FORMAL,
    N_INST,
    N_INST_SMOKE,
    NL_CATEGORY,
    OUTCOME_IDX,
    PLAIN,
    SEED,
    _arrays,
    _json_native,
    _null_p,
    _paired_D,
    _residualize,
    branch_layers,
    outcome_mass,
)
from route_map_v0 import (  # noqa: E402
    BASIS17,
    build_pole_frame,
    build_pole_probes,
    capture_signs,
    g0_coherence,
    pick_layers,
    pole_gram,
    project_routes,
)

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (s344 pre-data freeze, Michael GO pending)
# ---------------------------------------------------------------------------
LEVELS = ("plain", "nl", "formal", "formal_scramble")

APRIORI = {"RECOGNITION": 35, "MIXED": 25, "COMPILATION": 20,
           "LENGTH-DRIVEN": 8, "SHARED-COMPILE": 5, "NO-BRANCH": 4, "VOID": 3}
VERDICTS = tuple(APRIORI)
assert sum(APRIORI.values()) == 100

# atom tokenizer for the scramble: λ+letter | word | single non-space symbol
_ATOM = re.compile(r"λ[a-zA-Z]|[A-Za-z]+|\d+|[^\sλ]")


def _scramble(text: str, rng: np.random.Generator) -> str:
    """Atom-order shuffle: same lexical atoms, order destroyed → no valid reduction.
    Recognizable formal tokens survive so lexical RECOGNITION can still fire; the
    computation cannot (rejoined with spaces). Guaranteed != source atom order."""
    atoms = _ATOM.findall(text)
    if len(atoms) < 2:
        return text
    order = list(range(len(atoms)))
    for _ in range(64):
        perm = list(rng.permutation(len(atoms)))
        if perm != order:
            order = perm
            break
    return " ".join(atoms[i] for i in order)


def build_corpus(n_inst: int, seed: int) -> list[dict]:
    """Matched (combinator x level) items with the 4th formal_scramble level.
    plain/nl/formal are the FROZEN s344 items (exact replication); formal_scramble
    is a deterministic atom-shuffle of each formal item (1:1 length pairing)."""
    from verbum.probes.library import all_probes

    rng = np.random.default_rng(seed)
    by_cat: dict[str, list[str]] = {}
    for p in all_probes():
        by_cat.setdefault(p.category, []).append(p.prompt)

    items: list[dict] = []
    for c in COMBINATORS:
        plain = PLAIN[c][:n_inst]
        formal = FORMAL[c][:n_inst]
        scramble = [_scramble(t, rng) for t in formal]  # deterministic, item order
        nlpool = by_cat.get(NL_CATEGORY[c], [])
        if len(nlpool) > n_inst:
            idx = sorted(rng.choice(len(nlpool), n_inst, replace=False))
            nlpool = [nlpool[i] for i in idx]
        else:
            nlpool = nlpool[:n_inst]
        for lvl, texts in (("plain", plain), ("nl", nlpool),
                           ("formal", formal), ("formal_scramble", scramble)):
            for t in texts:
                items.append({"combinator": c, "level": lvl, "text": t})
    return items


# ---------------------------------------------------------------------------
# Frozen analysis (identical path for real capture and planted worlds)
# ---------------------------------------------------------------------------
def _sig(d: float, p: float) -> bool:
    return (d > FLOOR_D) and (p < ALPHA)


def analyse(route17: np.ndarray, corpus: dict, token_len: np.ndarray,
            n_layers: int, rng: np.random.Generator, g0_ok: bool = True) -> dict:
    comb, level = corpus["combinator"], corpus["level"]
    mass = outcome_mass(route17, n_layers)

    if not g0_ok or float(np.std(mass)) < 1e-9:
        return {"verdict": "VOID", "reason": "g0_fail_or_degenerate",
                "mass_by_level": {}, "stats": {}}

    lvl_mass = {lv: float(mass[level == lv].mean()) for lv in LEVELS}
    branch_exists = max(lvl_mass.values()) >= BRANCH_FLOOR

    # primary: length-residualized paired D (formal vs scramble is length-matched by
    # construction; scramble vs plain is length-controlled by this partial)
    mass_r = _residualize(mass, token_len.astype(float))
    rep = _paired_D(mass_r, comb, level, "formal", "plain")
    ds = _paired_D(mass_r, comb, level, "formal", "formal_scramble")
    dsp = _paired_D(mass_r, comb, level, "formal_scramble", "plain")
    p_rep = _null_p(mass_r, comb, level, "formal", "plain", rep, rng)
    p_ds = _null_p(mass_r, comb, level, "formal", "formal_scramble", ds, rng)
    p_dsp = _null_p(mass_r, comb, level, "formal_scramble", "plain", dsp, rng)

    # raw rep only for the length-driven / shared distinction
    rep_raw = _paired_D(mass, comb, level, "formal", "plain")
    p_rep_raw = _null_p(mass, comb, level, "formal", "plain", rep_raw, rng)

    stats = {
        "lvl_mass": lvl_mass,
        "rep_formal_plain_resid": rep, "p_rep_resid": p_rep,
        "ds_formal_scramble_resid": ds, "p_ds_resid": p_ds,
        "dsp_scramble_plain_resid": dsp, "p_dsp_resid": p_dsp,
        "rep_formal_plain_raw": rep_raw, "p_rep_raw": p_rep_raw,
        "identity_rep_minus_ds_dsp": float(rep - (ds + dsp)),
        "len_r_formal_scramble": float(np.corrcoef(
            token_len, (level == "formal_scramble").astype(float))[0, 1]),
    }

    rep_sig, ds_sig, dsp_sig = _sig(rep, p_rep), _sig(ds, p_ds), _sig(dsp, p_dsp)

    if not branch_exists:
        verdict = "NO-BRANCH"
    elif not rep_sig:
        verdict = "LENGTH-DRIVEN" if _sig(rep_raw, p_rep_raw) else "SHARED-COMPILE"
    elif ds_sig and dsp_sig:
        verdict = "MIXED"
    elif ds_sig and not dsp_sig:
        verdict = "COMPILATION"
    elif dsp_sig and not ds_sig:
        verdict = "RECOGNITION"
    else:
        # rep = ds + dsp: rep_sig with neither sub-gap sig is near-degenerate; the
        # ambiguous middle → MIXED (documented, effectively unreachable).
        verdict = "MIXED"

    return {"verdict": verdict, "stats": stats,
            "mass_by_level": lvl_mass, "branch_exists": branch_exists,
            "flags": {"rep_sig": rep_sig, "ds_sig": ds_sig, "dsp_sig": dsp_sig}}


# ---------------------------------------------------------------------------
# Planted worlds (route17-level; drive the REAL analyse path)
# ---------------------------------------------------------------------------
def _plant(corpus: dict, token_len: np.ndarray, mode: str, n_layers: int,
           rng: np.random.Generator) -> np.ndarray:
    n = len(corpus["level"])
    level = corpus["level"]
    r = 0.05 * rng.standard_normal((n, n_layers, 17)).astype(np.float64)
    bl = branch_layers(n_layers)
    lmin, lmax = float(token_len.min()), float(token_len.max())
    for i in range(n):
        lv = level[i]
        if mode == "VOID":
            r[i] = 1.0
            continue
        if mode == "COMPILATION":               # only VALID formal reaches poles
            amp = 0.6 if lv == "formal" else 0.0
        elif mode == "RECOGNITION":              # any formal-token level reaches
            amp = 0.6 if lv in ("formal", "formal_scramble") else 0.0
        elif mode == "MIXED":                    # scramble partway between
            amp = 0.6 if lv == "formal" else (0.32 if lv == "formal_scramble"
                                              else 0.0)
        elif mode == "LENGTH":                   # short -> high, any level
            t = (token_len[i] - lmin) / (lmax - lmin + 1e-9)
            amp = 0.6 * (1.0 - t)
        elif mode == "SHARED":                   # all levels alike
            amp = 0.5
        elif mode == "NO-BRANCH":
            amp = 0.0
        else:
            raise ValueError(mode)
        for li in bl:
            r[i, li, OUTCOME_IDX] += amp
    return r


def planted_worlds() -> dict:
    items = build_corpus(N_INST_SMOKE, SEED)
    corpus = _arrays(items)
    token_len = np.array([len(t.split()) for t in corpus["text"]], float)
    n_layers = 40
    expect = {"COMPILATION": "COMPILATION", "RECOGNITION": "RECOGNITION",
              "MIXED": "MIXED", "LENGTH": "LENGTH-DRIVEN",
              "SHARED": "SHARED-COMPILE", "NO-BRANCH": "NO-BRANCH", "VOID": "VOID"}
    worlds = {}
    for mode, want in expect.items():
        rng = np.random.default_rng(SEED)
        r17 = _plant(corpus, token_len, mode, n_layers, rng)
        worlds[mode] = (r17, corpus, token_len, n_layers, want)
    return worlds


def run_validate() -> int:
    log("[compile-v2] --validate: planted worlds through the real analyse path")
    ok = True
    for name, (r17, corpus, tlen, nl, want) in planted_worlds().items():
        rng = np.random.default_rng(SEED)
        res = analyse(r17, corpus, tlen, nl, rng)
        got = res["verdict"]
        passed = got == want
        ok = ok and passed
        s = res.get("stats", {})
        log(f"[compile-v2]   {name:11s} -> {got:14s} (want {want:14s}) "
            f"rep={s.get('rep_formal_plain_resid', float('nan')):+.3f} "
            f"ds={s.get('ds_formal_scramble_resid', float('nan')):+.3f} "
            f"dsp={s.get('dsp_scramble_plain_resid', float('nan')):+.3f} "
            f"{'OK' if passed else 'FAIL'}")
    log(f"[compile-v2] validate {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--out", default="results/p_compile_step_v2_s344/run")
    ap.add_argument("--max-length", type=int, default=64)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    from dmd_transport import RealBackend

    n_inst = N_INST_SMOKE if args.smoke else N_INST
    items = build_corpus(n_inst, SEED)
    corpus = _arrays(items)
    pole_texts, pole_states = build_pole_probes()
    log(f"[compile-v2] corpus {len(items)} items ({len(COMBINATORS)}x{len(LEVELS)}"
        f"x{n_inst}) | pole probes {len(pole_texts)}")

    be = RealBackend(args.model_id, args.device, args.dtype)
    n_layers = len(find_gate_modules(be.model))
    want = pick_layers(n_layers)
    token_len = np.array([be.tok(t, truncation=True,
                                 max_length=args.max_length)["input_ids"].__len__()
                          for t in corpus["text"]], float)

    log("[compile-v2] pass 1/2 — pole probes -> frame")
    pole_signs = capture_signs(be, pole_texts, want, args.max_length)
    P, mu = build_pole_frame(pole_signs, pole_states, BASIS17)
    g0 = g0_coherence(pole_gram(P))
    g0_ok = float(g0.get("offdiag_corr_vs_committed", 0.0)) >= 0.7
    log(f"[compile-v2] G0 offdiag_corr={g0.get('offdiag_corr_vs_committed')} "
        f"ok={g0_ok}")
    del pole_signs

    log("[compile-v2] pass 2/2 — matched corpus -> routes")
    signs = capture_signs(be, corpus["text"].tolist(), want, args.max_length)
    route17 = project_routes(signs, P, mu)

    chk = capture_signs(be, corpus["text"].tolist()[:DET_CHECK_N], want,
                        args.max_length)
    det_dev = float(np.abs(route17[:DET_CHECK_N] - project_routes(chk, P, mu)).max())

    rng = np.random.default_rng(SEED)
    res = analyse(route17, corpus, token_len, n_layers, rng, g0_ok=g0_ok)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    corpus_hash = hashlib.sha256(
        json.dumps(sorted(corpus["text"].tolist()), sort_keys=True).encode()
    ).hexdigest()[:16]
    meta = {
        "probe": "P-COMPILE-STEP-V2",
        "frozen": "s344 pre-data freeze (Michael GO pending): does VALID formal "
                  "notation route into whnf:*, or does SCRAMBLED formal (same "
                  "atoms, no valid computation) route there too? resolves the "
                  "§P-COMPILE-STEP surface-similarity bound",
        "pre_data": {
            "COMBINATORS": list(COMBINATORS), "LEVELS": list(LEVELS),
            "OUTCOME_POLES": [BASIS17[i] for i in OUTCOME_IDX],
            "N_INST": N_INST, "ALPHA": ALPHA, "FLOOR_D": FLOOR_D,
            "BRANCH_FLOOR": BRANCH_FLOOR, "apriori": APRIORI,
            "identity": "rep(formal-plain) = ds(formal-scramble) + "
                        "dsp(scramble-plain)",
            "discriminator": "branch-band outcome-pole mass, length-residualized; "
                             "COMPILATION iff scrambling collapses branch to plain "
                             "(ds sig, dsp null); RECOGNITION iff scramble routes "
                             "like formal (ds null, dsp sig); MIXED iff both",
        },
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "model_id": args.model_id, "device": args.device, "dtype": args.dtype,
        "smoke": bool(args.smoke), "n_items": len(items), "n_inst": n_inst,
        "want_layers": want, "n_layers": n_layers, "corpus_hash": corpus_hash,
        "git_sha": git_sha(), "det_route_dev": det_dev,
        "det_ok": det_dev <= DET_TOL, "g0": g0, "g0_ok": g0_ok,
        "verdict": res["verdict"], "stats": res.get("stats", {}),
        "mass_by_level": res.get("mass_by_level", {}),
        "flags": res.get("flags", {}),
        "apriori_mass": APRIORI.get(res["verdict"]),
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))
    np.savez_compressed(
        out / "routes.npz", route17=route17.astype(np.float16),
        combinator=corpus["combinator"], level=corpus["level"],
        text=corpus["text"], token_len=token_len,
        want=np.array(want), basis17=np.array(BASIS17))

    s = res.get("stats", {})
    log(f"[compile-v2] det_route_dev={det_dev:.2e} g0_ok={g0_ok}")
    log(f"[compile-v2] mass by level: {res.get('mass_by_level')}")
    log(f"[compile-v2] rep(f-p)={s.get('rep_formal_plain_resid'):+.4f} "
        f"p={s.get('p_rep_resid'):.4f}")
    log(f"[compile-v2] ds(f-scr)={s.get('ds_formal_scramble_resid'):+.4f} "
        f"p={s.get('p_ds_resid'):.4f} | "
        f"dsp(scr-p)={s.get('dsp_scramble_plain_resid'):+.4f} "
        f"p={s.get('p_dsp_resid'):.4f}")
    log(f"[compile-v2] === VERDICT: {res['verdict']} "
        f"(a-priori {APRIORI.get(res['verdict'])}) ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
