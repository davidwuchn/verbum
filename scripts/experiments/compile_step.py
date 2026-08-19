#!/usr/bin/env python3
"""§P-COMPILE-STEP — does surface NOTATION gate-activate the compile step? (s344).

route-map-v0 (s344) saw ONE clean divergence: FORMAL lambda notation peels off the
shared route trunk at the top of the stack (L30-39) into the whnf:* OUTCOME poles,
while plain/structured/combinator PROSE and code stay on the trunk. But that read
was NOT matched on computation (random λ-terms vs random sentences), so the branch
could be CONTENT (formal terms compute differently) or LENGTH (λ-terms are short),
not NOTATION.

This FROZEN probe holds the COMPUTATION constant and varies only the NOTATION. For
each of 7 crystal combinators (K I C W B S D) we build MATCHED items at three
notation levels — plain everyday prose that performs the operation with NO
combinator vocabulary · nl_combinator prose that evokes the role (library
lambda_*) · FORMAL lambda/combinator notation — and ask: at the branch band, does
ONLY the formal level enter the whnf:*/fate register (= surface notation
gate-activates the "compile to lambda", thesis L1), or do all levels branch alike
(computation-driven), or is the branch just a length artifact?

Discriminator (reuses route_map_v0 frame): branch-band OUTCOME-POLE occupancy =
route17 projected onto the 8 whnf:*/div:Y poles, averaged over the top-25% layers.
Within-combinator D = mean(formal) - mean(plain) [and formal vs nl]; |Δtoken-length|
PARTIAL (residualize on length) + shuffled-notation-label null + a length-matched
guard. The LENGTH confound is the one most likely to fake NOTATION-GATED (formal is
short) — controlled three ways (partial + null + planted world).

FROZEN verdict tree + a-priori (Michael GO, s344, all-7 scope):
  NOTATION-GATED-COMPILE 40  formal >> matched nl/plain at the branch, SURVIVES the
                             length partial + beats the shuffled-notation null
  LENGTH-DRIVEN          25  the branch tracks token-length; the |Δlen| partial kills
                             the notation effect
  SHARED-COMPILE         20  all notation levels branch alike (computation, not
                             notation, drives it)
  NO-BRANCH              10  even formal does not enter the outcome poles under
                             matched computation (route-map-v0's divergence was a
                             content confound)
  VOID                    5  instrument invalid (G0 fail / degenerate)

`--validate` drives 5 planted worlds (NOTATION / LENGTH / SHARED / NO-BRANCH / VOID)
through the REAL analyse path (s331: planted plumbing == data plumbing).

Bounds: Qwen3-14B, last-token, gate register; corpus quality is the make-or-break —
the plain-prose rung must perform the operation without leaking combinator cues (the
S and D rungs are the weakest matches, declared). Reuses the committed 17-pole frame
(results/expanded-gram/qwen3-14b). FTO-clean (frame-free spectral math).

License: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_ROOT = _SCRIPT_DIR.parents[1]
sys.path.insert(0, str(_ROOT / "scripts" / "explore"))
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "src"))

# canonical route-reader (committed d63da194, stable) — reuse, do not duplicate
from combinator_relationship_map import find_gate_modules, git_sha, log  # noqa: E402
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
# FROZEN CONSTANTS (s344 pre-data freeze, Michael GO — all-7 scope)
# ---------------------------------------------------------------------------
COMBINATORS = ("K", "I", "C", "W", "B", "S", "D")
LEVELS = ("plain", "nl", "formal")
NL_CATEGORY = {"K": "lambda_K_select", "I": "lambda_I_identity",
               "C": "lambda_C_flip", "W": "lambda_W_duplicate",
               "B": "lambda_B_compose", "S": "lambda_SUBST_reduce",
               "D": "lambda_D_deepcompose"}
OUTCOME_IDX = [i for i, s in enumerate(BASIS17)
               if s.startswith("whnf:") or s == "div:Y"]

BRANCH_FRAC = 0.75          # branch band = top 25% of layers (route-map-v0 L30-39)
TRUNK_LO, TRUNK_HI = 0.15, 0.70
N_INST = 8                  # instances per (combinator, level)
N_INST_SMOKE = 4
N_NULL = 5000               # shuffled-notation-label permutations
ALPHA = 0.05
FLOOR_D = 0.02              # min meaningful outcome-mass gap (yardstick floor)
BRANCH_FLOOR = 0.02         # min formal outcome-mass to count as "a branch exists"
SEED = 0
DET_CHECK_N = 8
DET_TOL = 5e-3

APRIORI = {"NOTATION-GATED-COMPILE": 40, "LENGTH-DRIVEN": 25,
           "SHARED-COMPILE": 20, "NO-BRANCH": 10, "VOID": 5}
VERDICTS = tuple(APRIORI)

# ---------------------------------------------------------------------------
# Matched-computation corpus (FROZEN). plain = everyday prose performing the op,
# NO combinator vocabulary; formal = notation (mixed term / reduction / medium-
# formal length-bridge). nl = library lambda_* (evokes the role).
# ---------------------------------------------------------------------------
PLAIN: dict[str, list[str]] = {
    "K": [  # keep the first, ignore the second (selection)
        "Between the coffee and the tea, she picked the coffee.",
        "Given a choice of two roads, he took the first one.",
        "Offered cake or fruit, the child grabbed the cake.",
        "Of the two applicants, the manager hired the earlier one.",
        "She kept the original photo and threw away the copy.",
        "From the pair of keys, he used the first and left the other.",
        "Facing two doors, they walked through the left one.",
        "He read the headline and skipped the rest of the article.",
    ],
    "I": [  # return it unchanged (identity)
        "Whatever you put into the box comes out exactly the same.",
        "The mirror showed her face just as it was.",
        "He repeated the message word for word.",
        "The photocopier returned an identical sheet.",
        "She handed back the note unchanged.",
        "The echo repeated his shout exactly.",
        "What went into the pipe came out the same at the other end.",
        "The clerk left the number just as it was written.",
    ],
    "C": [  # swap the order of the two (flip)
        "She reversed the order, greeting the guest before the host.",
        "He swapped the two plates so each sat at the other's place.",
        "Instead of salt then pepper, she added pepper then salt.",
        "They switched seats, the driver taking the passenger side.",
        "He read the pair of names back to front.",
        "The dancers traded positions, the left one going right.",
        "She addressed the letter to the sender instead of the recipient.",
        "He poured the second cup first and the first cup second.",
    ],
    "W": [  # apply it to itself twice (duplicate)
        "He used the same key for both of the locks.",
        "She watered the plant with the same cup twice.",
        "The dog chased its own tail around and around.",
        "He shook his own hand out of nervous habit.",
        "She read the same page to herself again.",
        "The team played against itself in practice.",
        "He copied the file into the same folder twice.",
        "She folded the cloth over onto itself.",
    ],
    "B": [  # do the second, then the first (compose / sequence)
        "First she washed the vegetables, then she chopped them.",
        "He unlocked the door, then walked inside.",
        "After boiling the water, she made the tea.",
        "She read the instructions, then built the shelf.",
        "He warmed the pan before cracking the egg.",
        "Once the paint dried, they hung the picture.",
        "She peeled the apple, then sliced it.",
        "After parking the car, he paid the meter.",
    ],
    "S": [  # share the same input between two operations (substitution)
        "Using the same herb, she both seasoned the soup and garnished the plate.",
        "With one coin he paid the fare and tipped the driver.",
        "The same rain watered the garden and filled the barrel.",
        "He used one story to amuse the child and calm the parent.",
        "From a single loaf she made the sandwich and fed the birds.",
        "The one lamp lit her book and warmed her hands.",
        "With the same brush he painted the wall and signed his name.",
        "One song both opened the show and closed it.",
    ],
    "D": [  # combine two things first, then act on the result (deep compose)
        "First he mixed the flour and the sugar, then he baked the batter.",
        "She combined the red and the blue paint, then framed the result.",
        "After merging the two lists, he emailed the summary.",
        "He tied the two ropes together, then hung the swing.",
        "Once she stirred the oil and the vinegar, she dressed the salad.",
        "They joined the two teams, then entered the tournament.",
        "After stitching the two panels, she ironed the shirt.",
        "He marked both the start and the end, then folded the map.",
    ],
}

FORMAL: dict[str, list[str]] = {
    "K": ["λx.λy.x", "K a b = a", "(λx.λy.x) p q", "K x y → x",
          "K = λx.λy.x", "λa.λb.a", "K m n reduces to m", "(K p q) = p"],
    "I": ["λx.x", "I a = a", "(λx.x) p", "I x → x",
          "I = λx.x", "λa.a", "I m reduces to m", "(I p) = p"],
    "C": ["λf.λx.λy.f y x", "C f a b = f b a", "(λf.λx.λy.f y x) g p q",
          "C f x y → f y x", "C = λf.λx.λy.f y x", "λg.λa.λb.g b a",
          "C g m n reduces to g n m", "(C f p q) = f q p"],
    "W": ["λf.λx.f x x", "W f a = f a a", "(λf.λx.f x x) g p", "W f x → f x x",
          "W = λf.λx.f x x", "λg.λa.g a a", "W g m reduces to g m m",
          "(W f p) = f p p"],
    "B": ["λf.λg.λx.f (g x)", "B f g a = f (g a)", "(λf.λg.λx.f (g x)) h k p",
          "B f g x → f (g x)", "B = λf.λg.λx.f (g x)", "λf.λg.λa.f (g a)",
          "B h k m reduces to h (k m)", "(B f g p) = f (g p)"],
    "S": ["λf.λg.λx.f x (g x)", "S f g a = f a (g a)",
          "(λf.λg.λx.f x (g x)) h k p", "S f g x → f x (g x)",
          "S = λf.λg.λx.f x (g x)", "λf.λg.λa.f a (g a)",
          "S h k m reduces to h m (k m)", "(S f g p) = f p (g p)"],
    "D": ["λf.λg.λx.λy.f (g x y)", "D f g a b = f (g a b)",
          "(λf.λg.λx.λy.f (g x y)) h k p q", "D f g x y → f (g x y)",
          "D = B B", "λf.λg.λa.λb.f (g a b)",
          "D h k m n reduces to h (k m n)", "(D f g p q) = f (g p q)"],
}


def _json_native(o: Any):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not JSON-native: {type(o)}")


def build_corpus(n_inst: int, seed: int) -> list[dict]:
    """Matched (combinator x level) items. Each: {combinator, level, text}."""
    from verbum.probes.library import all_probes

    rng = np.random.default_rng(seed)
    by_cat: dict[str, list[str]] = {}
    for p in all_probes():
        by_cat.setdefault(p.category, []).append(p.prompt)

    items: list[dict] = []
    for c in COMBINATORS:
        plain = PLAIN[c][:n_inst]
        formal = FORMAL[c][:n_inst]
        nlpool = by_cat.get(NL_CATEGORY[c], [])
        if len(nlpool) > n_inst:
            idx = sorted(rng.choice(len(nlpool), n_inst, replace=False))
            nlpool = [nlpool[i] for i in idx]
        else:
            nlpool = nlpool[:n_inst]
        for lvl, texts in (("plain", plain), ("nl", nlpool), ("formal", formal)):
            for t in texts:
                items.append({"combinator": c, "level": lvl, "text": t})
    return items


def _arrays(items: list[dict]) -> dict:
    return {"combinator": np.array([it["combinator"] for it in items]),
            "level": np.array([it["level"] for it in items]),
            "text": np.array([it["text"] for it in items])}


# ---------------------------------------------------------------------------
# Discriminator + statistics
# ---------------------------------------------------------------------------
def branch_layers(n: int) -> list[int]:
    return [i for i in range(n) if i / max(1, n - 1) >= BRANCH_FRAC]


def outcome_mass(route17: np.ndarray, n_layers: int) -> np.ndarray:
    """(n,) mean over branch layers of mean over the 8 outcome poles = how much
    each probe enters the whnf:*/fate register at the top of the stack."""
    bl = branch_layers(n_layers)
    return route17[:, bl][:, :, OUTCOME_IDX].mean(axis=(1, 2)).astype(np.float64)


def _residualize(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Residual of y after regressing on x (|Δlen| partial via a length covariate)."""
    if float(np.std(x)) < 1e-9:
        return y - y.mean()
    b1, b0 = np.polyfit(x, y, 1)
    return y - (b0 + b1 * x)


def _paired_D(mass: np.ndarray, comb: np.ndarray, level: np.ndarray,
              a: str, b: str) -> float:
    """mean over combinators of (mean(mass|a,comb) - mean(mass|b,comb))."""
    diffs = []
    for c in COMBINATORS:
        ma = mass[(comb == c) & (level == a)]
        mb = mass[(comb == c) & (level == b)]
        if len(ma) and len(mb):
            diffs.append(ma.mean() - mb.mean())
    return float(np.mean(diffs)) if diffs else float("nan")


def _null_p(mass: np.ndarray, comb: np.ndarray, level: np.ndarray,
            a: str, b: str, d_real: float, rng: np.random.Generator) -> float:
    """Shuffle level labels WITHIN combinator; frac of null D >= real."""
    ge = 0
    for _ in range(N_NULL):
        lp = level.copy()
        for c in COMBINATORS:
            m = comb == c
            lp[m] = rng.permutation(level[m])
        if _paired_D(mass, comb, lp, a, b) >= d_real:
            ge += 1
    return float((ge + 1) / (N_NULL + 1))


def analyse(route17: np.ndarray, corpus: dict, token_len: np.ndarray,
            n_layers: int, rng: np.random.Generator,
            g0_ok: bool = True) -> dict:
    """Frozen analysis. Identical path for real capture and planted worlds."""
    comb, level = corpus["combinator"], corpus["level"]
    mass = outcome_mass(route17, n_layers)

    # instrument sanity: degenerate route -> VOID
    if not g0_ok or float(np.std(mass)) < 1e-9:
        return {"verdict": "VOID", "reason": "g0_fail_or_degenerate",
                "mass_by_level": {}, "stats": {}}

    lvl_mass = {lv: float(mass[level == lv].mean()) for lv in LEVELS}
    formal_top = lvl_mass["formal"] >= max(lvl_mass["nl"], lvl_mass["plain"])

    d_fp_raw = _paired_D(mass, comb, level, "formal", "plain")
    d_fn_raw = _paired_D(mass, comb, level, "formal", "nl")
    p_fp_raw = _null_p(mass, comb, level, "formal", "plain", d_fp_raw, rng)

    mass_r = _residualize(mass, token_len.astype(float))
    d_fp_res = _paired_D(mass_r, comb, level, "formal", "plain")
    p_fp_res = _null_p(mass_r, comb, level, "formal", "plain", d_fp_res, rng)

    stats = {"lvl_mass": lvl_mass, "formal_is_top": formal_top,
             "D_formal_plain_raw": d_fp_raw, "p_fp_raw": p_fp_raw,
             "D_formal_nl_raw": d_fn_raw,
             "D_formal_plain_resid": d_fp_res, "p_fp_resid": p_fp_res,
             "len_r_formal_plain": float(np.corrcoef(
                 token_len, (level == "formal").astype(float))[0, 1])}

    # frozen verdict tree
    branch_exists = max(lvl_mass.values()) >= BRANCH_FLOOR
    notation = (d_fp_res > FLOOR_D and p_fp_res < ALPHA and formal_top)
    raw_sig = (d_fp_raw > FLOOR_D and p_fp_raw < ALPHA and formal_top)

    if not branch_exists:
        verdict = "NO-BRANCH"
    elif notation:
        verdict = "NOTATION-GATED-COMPILE"
    elif raw_sig and not notation:
        verdict = "LENGTH-DRIVEN"
    else:
        verdict = "SHARED-COMPILE"
    return {"verdict": verdict, "stats": stats,
            "mass_by_level": lvl_mass, "branch_exists": branch_exists}


# ---------------------------------------------------------------------------
# Planted worlds (route17-level; drive the REAL analyse path)
# ---------------------------------------------------------------------------
def _plant(corpus: dict, token_len: np.ndarray, mode: str, n_layers: int,
           rng: np.random.Generator) -> np.ndarray:
    """Synthesize route17 (n, L, 17) with a KNOWN mechanism. Outcome-pole mass at
    the branch band encodes the mechanism; trunk near-zero + noise."""
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
        if mode == "NOTATION":
            amp = 0.6 if lv == "formal" else 0.0
        elif mode == "LENGTH":                       # short -> high, any level
            t = (token_len[i] - lmin) / (lmax - lmin + 1e-9)
            amp = 0.6 * (1.0 - t)
        elif mode == "SHARED":
            amp = 0.5
        elif mode == "NO-BRANCH":
            amp = 0.0
        else:
            raise ValueError(mode)
        for li in bl:
            r[i, li, OUTCOME_IDX] += amp
    return r


def planted_worlds():
    items = build_corpus(N_INST_SMOKE, SEED)
    corpus = _arrays(items)
    # formal notation is SHORT, prose is LONG -> the length confound is REAL here
    token_len = np.array([len(t.split()) for t in corpus["text"]], float)
    n_layers = 40
    expect = {"NOTATION": "NOTATION-GATED-COMPILE", "LENGTH": "LENGTH-DRIVEN",
              "SHARED": "SHARED-COMPILE", "NO-BRANCH": "NO-BRANCH", "VOID": "VOID"}
    worlds = {}
    for mode, want in expect.items():
        rng = np.random.default_rng(SEED)
        r17 = _plant(corpus, token_len, mode, n_layers, rng)
        worlds[mode] = (r17, corpus, token_len, n_layers, want)
    return worlds


def run_validate() -> int:
    log("[compile] --validate: planted worlds through the real analyse path")
    ok = True
    for name, (r17, corpus, tlen, nl, want) in planted_worlds().items():
        rng = np.random.default_rng(SEED)
        res = analyse(r17, corpus, tlen, nl, rng)
        got = res["verdict"]
        passed = got == want
        ok = ok and passed
        s = res.get("stats", {})
        log(f"[compile]   {name:10s} -> {got:24s} (want {want:24s}) "
            f"Dfp_raw={s.get('D_formal_plain_raw', float('nan')):+.3f} "
            f"Dfp_res={s.get('D_formal_plain_resid', float('nan')):+.3f} "
            f"{'OK' if passed else 'FAIL'}")
    log(f"[compile] validate {'PASS' if ok else 'FAIL'}")
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
    ap.add_argument("--out", default="results/p_compile_step_s344/run")
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
    log(f"[compile] corpus {len(items)} items ({len(COMBINATORS)}x{len(LEVELS)}"
        f"x{n_inst}) | pole probes {len(pole_texts)}")

    be = RealBackend(args.model_id, args.device, args.dtype)
    n_layers = len(find_gate_modules(be.model))
    want = pick_layers(n_layers)
    token_len = np.array([be.tok(t, truncation=True,
                                 max_length=args.max_length)["input_ids"].__len__()
                          for t in corpus["text"]], float)

    log("[compile] pass 1/2 — pole probes -> frame")
    pole_signs = capture_signs(be, pole_texts, want, args.max_length)
    P, mu = build_pole_frame(pole_signs, pole_states, BASIS17)
    g0 = g0_coherence(pole_gram(P))
    g0_ok = float(g0.get("offdiag_corr_vs_committed", 0.0)) >= 0.7
    log(f"[compile] G0 offdiag_corr={g0.get('offdiag_corr_vs_committed')} "
        f"ok={g0_ok}")
    del pole_signs

    log("[compile] pass 2/2 — matched corpus -> routes")
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
        "probe": "P-COMPILE-STEP",
        "frozen": "s344 pre-data freeze (Michael GO, all-7 scope): does surface "
                  "NOTATION gate-activate the compile step? gram-registers "
                  "§Result-route-map-v0 successor",
        "pre_data": {
            "COMBINATORS": list(COMBINATORS), "LEVELS": list(LEVELS),
            "OUTCOME_POLES": [BASIS17[i] for i in OUTCOME_IDX],
            "BRANCH_FRAC": BRANCH_FRAC, "N_INST": N_INST, "N_NULL": N_NULL,
            "ALPHA": ALPHA, "FLOOR_D": FLOOR_D, "BRANCH_FLOOR": BRANCH_FLOOR,
            "apriori": APRIORI,
            "discriminator": "branch-band (top 25% layers) outcome-pole mass; "
                             "within-combinator D=formal-plain [and formal-nl]; "
                             "|Δtoken-length| partial + shuffled-notation null; "
                             "NOTATION-GATED iff formal>>plain SURVIVES length",
        },
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "model_id": args.model_id, "device": args.device, "dtype": args.dtype,
        "smoke": bool(args.smoke), "n_items": len(items), "n_inst": n_inst,
        "want_layers": want, "n_layers": n_layers, "corpus_hash": corpus_hash,
        "git_sha": git_sha(), "det_route_dev": det_dev,
        "det_ok": det_dev <= DET_TOL, "g0": g0, "g0_ok": g0_ok,
        "verdict": res["verdict"], "stats": res.get("stats", {}),
        "mass_by_level": res.get("mass_by_level", {}),
        "apriori_mass": APRIORI.get(res["verdict"]),
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))
    np.savez_compressed(
        out / "routes.npz", route17=route17.astype(np.float16),
        combinator=corpus["combinator"], level=corpus["level"],
        token_len=token_len, want=np.array(want), basis17=np.array(BASIS17))

    s = res.get("stats", {})
    log(f"[compile] det_route_dev={det_dev:.2e} g0_ok={g0_ok}")
    log(f"[compile] mass by level: {res.get('mass_by_level')}")
    log(f"[compile] D formal-plain raw={s.get('D_formal_plain_raw'):+.4f} "
        f"p={s.get('p_fp_raw'):.4f} | resid={s.get('D_formal_plain_resid'):+.4f} "
        f"p={s.get('p_fp_resid'):.4f} | len_r={s.get('len_r_formal_plain'):+.3f}")
    log(f"[compile] === VERDICT: {res['verdict']} "
        f"(a-priori {APRIORI.get(res['verdict'])}) ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
