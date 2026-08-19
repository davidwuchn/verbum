#!/usr/bin/env python3
"""P-SCHEDULE-READ-C - the register-complete co-extensional test (frozen s343,
Michael GO). Do terms that COMPUTE THE SAME FUNCTION but are SPELLED DIFFERENTLY
(SKK vs I, ...) look alike inside the model (it tracks MEANING) or not (it tracks
the LETTERS) - read in EVERY gauge we can capture in ONE pass?

The faithful successor to arm A (s343, 🚫 MODEL-SPECIFIC: the route-schedule is a
static level ladder, no universal timetable). Arm A showed the literal SKK≈I test
is per-model and must not be limited to the route register; Michael: "look at ALL
the registers." One 14B capture reuses the EXACT s339 co-extensional anchors and
reads three registers at 11 depths:

  routing  = sign(FFN gate pre-activation)   -- PRIMARY, the s342 "station map"
                                                substrate (universal switch gauge)
  value    = last-token d_model residual     -- re-confirms s317/s339
  magnitude= ||residual|| per layer          -- re-confirms s335 on these anchors

(operator/DMD already answered LEXICAL at s339 - cited, not re-run; the 17x17
FATE register is DEFERRED - needs separate outcome-pole machinery - a declared
bound.)

THE TEST (reuses the s339 nested control ladder EXACTLY, at the GROUP=spelling
level with the s339 length-partial). Three anchor sets:
  operator (I:8 spellings, W:2, B:1)  -- CONFOUNDED (function == arity == length)
  arity    (multi-function per arity) -- LENGTH-CONTROLLED (same-arity strata)
  alpha    (all {S,K} alphabet)       -- ALPHABET + LENGTH controlled (residualize
                                         pairwise similarity on |Δtoken-length|,
                                         s339 _length_partial_matrix)
Per (set, register): centroid each spelling group, D = mean within-function -
across-function group-centroid similarity (same-arity pairs for arity/alpha;
unstratified for the confounded operator set), shuffled-function null (within
arity where stratified), effect floor. Ladder verdict per register:
  EXTENSIONAL  D survives the ALPHABET+LENGTH control (alpha passes)   -> meaning
  LEXICAL      D present (operator/arity) but VANISHES at constant alphabet -> surface
  ABSENT       no D anywhere
  VOID         instrument invalid (degenerate / too few groups / det fail)

FROZEN verdict tree + a-priori mass (on the PRIMARY routing register):
  LEXICAL 45 (the s321/s336/s339 prior) / ABSENT 25 / EXTENSIONAL 20 (the lead:
  routing is the UNIVERSAL register, the one gauge that might uniquely hold
  meaning) / VOID 10.  value + magnitude carry the same machinery as confirms.

Honest prediction: LEXICAL across the board (s339 already showed value/operator).
The payoff is the ROUTING gauge specifically - the universal station-map substrate,
never before tested for meaning-collapse at the item level. If even it is lexical,
that is the capstone on "meaning is tape-resident, never in the weights," across
every gauge we can read. EXTENSIONAL on routing would be a real lead.

`--validate` drives 5 planted worlds (EXTENSIONAL / LEXICAL / LENGTH-CONFOUND /
ABSENT / VOID) through the REAL analyse path (s331: planted plumbing == data
plumbing). LENGTH-CONFOUND is the s343-smoke guard: a purely length-driven signal
must NOT read EXTENSIONAL (the alpha length-partial catches it).

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
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_SCRIPT_DIR.parents[1] / "src"))

import cl_collapse_3_alpha as s339_alpha  # noqa: E402
import cl_collapse_3_arity as s339_arity  # noqa: E402
import cl_collapse_3_operator as s339_operator  # noqa: E402
from combinator_relationship_map import (  # noqa: E402
    LAYER_FRACS,
    find_gate_modules,
    git_sha,
    log,
)

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (s343 pre-data freeze, Michael GO)
# ---------------------------------------------------------------------------
REGISTERS = ("routing", "value", "magnitude")
PRIMARY = "routing"
SETS = ("operator", "arity", "alpha")
N_PER = 20             # atom instantiations per clean spelling (run)
N_PER_SMOKE = 6
N_NULL = 5000          # shuffled-function-label permutations
ALPHA = 0.05
FLOOR_D = 0.01         # min meaningful similarity gap (yardstick effect floor)
SEED = 0
DET_CHECK_N = 8
DET_TOL = 5e-3         # last-token value max-abs repeat dev (bf16 greedy fwd)

APRIORI = {"LEXICAL": 45, "ABSENT": 25, "EXTENSIONAL": 20, "VOID": 10}
VERDICTS = ("EXTENSIONAL", "LEXICAL", "ABSENT", "VOID")


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


# ---------------------------------------------------------------------------
# Unified co-extensional corpus (reuse the EXACT s339 kernel-certified anchors)
# ---------------------------------------------------------------------------
def build_unified_corpus(n_per: int, seed: int) -> list[dict]:
    """Each item: {set, text, function, group, arity}. Extensional equality is
    kernel-certified inside each s339 build_corpus (assert reduce==anchor)."""
    items: list[dict] = []
    for p in s339_operator.build_corpus(n_per, seed):
        items.append({"set": "operator", "text": p["text"],
                      "function": p["nf"], "group": p["group"],
                      "arity": int(p["arity"])})
    for p in s339_arity.build_corpus(n_per, seed + 1000):
        items.append({"set": "arity", "text": p["text"],
                      "function": p["function"], "group": p["group"],
                      "arity": int(p["arity"])})
    for p in s339_alpha.build_corpus(n_per, seed + 2000):
        items.append({"set": "alpha", "text": p["text"],
                      "function": p["function"], "group": p["group"],
                      "arity": int(p["arity"])})
    return items


def _corpus_arrays(items: list[dict]) -> dict:
    return {
        "set": np.array([it["set"] for it in items]),
        # namespaced function so labels never collide across sets
        "function": np.array([f"{it['set']}:{it['function']}" for it in items]),
        "arity": np.array([it["arity"] for it in items]),
        "group": np.array([it["group"] for it in items]),
        "text": np.array([it["text"] for it in items]),
    }


# ---------------------------------------------------------------------------
# Capture: hidden (all want-layers) + gate pre-activation (per want-layer)
# ---------------------------------------------------------------------------
def pick_layers(n_layers: int) -> list[int]:
    return sorted({min(n_layers - 1, max(0, round(f * (n_layers - 1))))
                   for f in LAYER_FRACS})


def capture(be, texts: list[str], want: list[int], max_length: int = 64) -> dict:
    """Return register feature dict:
       value     (n, L, d_model) float32
       routing   (n, L, d_ff)    float32(= sign(gate pre-activation))
       magnitude (n, L, 1)       float32(= ||hidden|| per layer, pre-CMR)
    plus plen. want = transformer-layer indices; hidden read at hidden_states[li+1].
    """
    import torch

    model, tok, device = be.model, be.tok, be.device
    gate_mods = find_gate_modules(model)
    want_set = set(want)
    buf: dict[int, np.ndarray] = {}

    def mk_hook(li):
        def hook(_m, _inp, out):
            buf[li] = out[0, -1].detach().float().cpu().numpy().astype(np.float32)
        return hook

    handles = [mod.register_forward_hook(mk_hook(li))
               for (li, _nm, mod) in gate_mods if li in want_set]

    n, ell = len(texts), len(want)
    value = routing = magnitude = None
    plen = np.empty(n, np.int32)
    try:
        with torch.no_grad():
            for i, text in enumerate(texts):
                buf.clear()
                enc = tok(text, return_tensors="pt", truncation=True,
                          max_length=max_length)
                enc = {k: v.to(device) for k, v in enc.items()}
                out = model(**enc, output_hidden_states=True)
                hs = out.hidden_states  # tuple len n_layers+1
                plen[i] = int(enc["input_ids"].shape[1])
                if value is None:
                    dmod = hs[0].shape[-1]
                    dff = buf[want[0]].shape[0]
                    value = np.empty((n, ell, dmod), np.float32)
                    routing = np.empty((n, ell, dff), np.float32)
                    magnitude = np.empty((n, ell, 1), np.float32)
                for k, li in enumerate(want):
                    h = hs[li + 1][0, -1].float().cpu().numpy().astype(np.float32)
                    value[i, k] = h
                    magnitude[i, k, 0] = float(np.linalg.norm(h))
                    routing[i, k] = np.sign(buf[li])
                del out
                if (i + 1) % 100 == 0:
                    log(f"    {i + 1}/{n}")
    finally:
        for hd in handles:
            hd.remove()
    return {"value": value, "routing": routing, "magnitude": magnitude,
            "plen": plen}


# ---------------------------------------------------------------------------
# Statistics: per-layer CMR -> group centroids -> similarity -> ladder D + null
# ---------------------------------------------------------------------------
def _cmr_perlayer(f: np.ndarray) -> np.ndarray:
    """Common-mode removal per layer (subtract per-feature mean across items)."""
    return f - f.mean(axis=0, keepdims=True)


def _group_centroids(f: np.ndarray, groups: np.ndarray,
                     order: list[str]) -> np.ndarray:
    """(n,L,dim) -> (G,L,dim): mean over each spelling group's items."""
    return np.stack([f[groups == g].mean(axis=0) for g in order])


def _simmat(f: np.ndarray) -> np.ndarray:
    """Mean-over-layers cosine similarity. f (G,L,dim) already per-layer CMR'd.
    dim==1 (magnitude) -> per-layer sign-agreement of the deviation, mean over L."""
    nrm = np.linalg.norm(f, axis=2, keepdims=True)
    fn = f / np.where(nrm < 1e-12, 1.0, nrm)
    ell = f.shape[1]
    return np.einsum("ild,jld->ij", fn, fn) / ell


def _length_partial(sim: np.ndarray, g_len: np.ndarray,
                    g_ar: np.ndarray) -> np.ndarray:
    """Residual similarity after regressing pairwise sim on |Δtoken-length| over
    same-arity pairs (s339 _length_partial_matrix). Removes the residual length
    effect; alphabet is already constant in the alpha set."""
    n = sim.shape[0]
    iu, ju = np.triu_indices(n, k=1)
    same = g_ar[iu] == g_ar[ju]
    d = sim[iu, ju]
    dl = np.abs(g_len[iu] - g_len[ju]).astype(float)
    r = sim.copy()
    if int(same.sum()) >= 3 and float(np.std(dl[same])) > 0:
        b1, b0 = np.polyfit(dl[same], d[same], 1)
        for k in np.where(same)[0]:
            i, j = iu[k], ju[k]
            resid = sim[i, j] - (b0 + b1 * dl[k])
            r[i, j] = r[j, i] = resid
    return r


def _D_stat(sim: np.ndarray, func: np.ndarray, arity: np.ndarray,
            stratify: bool, rng: np.random.Generator, n_null: int) -> dict:
    """D = mean within-function - across-function similarity over eligible group
    pairs (same-arity if stratify). Null shuffles function among groups (within
    arity where stratified)."""
    g = len(func)
    iu, ju = np.triu_indices(g, k=1)
    elig = (arity[iu] == arity[ju]) if stratify else np.ones(len(iu), bool)
    iu, ju = iu[elig], ju[elig]
    nan = {"D": float("nan"), "p": float("nan"), "n_within": 0, "n_across": 0,
           "within_mean": float("nan"), "across_mean": float("nan")}
    if len(iu) == 0:
        return nan
    simp = sim[iu, ju]
    within = func[iu] == func[ju]
    if within.sum() == 0 or (~within).sum() == 0:
        return {**nan, "n_within": int(within.sum()),
                "n_across": int((~within).sum())}
    d_real = float(simp[within].mean() - simp[~within].mean())

    strata = ([np.where(arity == a)[0] for a in np.unique(arity)]
              if stratify else [np.arange(g)])
    ge = 0
    for _ in range(n_null):
        fp = func.copy()
        for grp in strata:
            fp[grp] = rng.permutation(func[grp])
        wn = fp[iu] == fp[ju]
        if wn.sum() == 0 or (~wn).sum() == 0:
            continue
        if (simp[wn].mean() - simp[~wn].mean()) >= d_real:
            ge += 1
    return {"D": d_real, "p": float((ge + 1) / (n_null + 1)),
            "n_within": int(within.sum()), "n_across": int((~within).sum()),
            "within_mean": float(simp[within].mean()),
            "across_mean": float(simp[~within].mean())}


def _verdict_for_register(per_set: dict) -> str:
    def _valid(s):
        return s is not None and s["D"] == s["D"] and s["p"] == s["p"]

    op, ar, al = per_set.get("operator"), per_set.get("arity"), per_set.get("alpha")
    if not (_valid(ar) and _valid(al)):
        return "VOID"

    def _pass(s):
        return _valid(s) and s["D"] > FLOOR_D and s["p"] < ALPHA

    if _pass(al):                       # survives alphabet + length control
        return "EXTENSIONAL"
    if _pass(ar) or _pass(op):          # signal present but killed by alphabet
        return "LEXICAL"
    return "ABSENT"


def analyse(features: dict, corpus: dict, length: np.ndarray,
            rng: np.random.Generator) -> dict:
    """Frozen analysis (group-centroid level, s339 ladder). Identical path for
    real capture and planted worlds (s331)."""
    setarr, func = corpus["set"], corpus["function"]
    arity, group = corpus["arity"], corpus["group"]

    out: dict[str, Any] = {"registers": {}}
    for reg in REGISTERS:
        f_all = features[reg]
        per_set: dict[str, Any] = {}
        for sname in SETS:
            m = setarr == sname
            if m.sum() < 4:
                per_set[sname] = None
                continue
            f = _cmr_perlayer(f_all[m])
            if float(np.abs(f).max()) < 1e-9:      # degenerate: no variance
                per_set[sname] = None
                continue
            grp = group[m]
            order = sorted(set(grp.tolist()))
            if len(order) < 3:
                per_set[sname] = None
                continue
            cent = _group_centroids(f, grp, order)
            sim = _simmat(cent)
            g_fn = np.array([func[m][grp == gg][0] for gg in order])
            g_ar = np.array([arity[m][grp == gg][0] for gg in order])
            g_len = np.array([float(np.mean(length[m][grp == gg])) for gg in order])
            if sname == "alpha":
                sim = _length_partial(sim, g_len, g_ar)
            stat = _D_stat(sim, g_fn, g_ar, sname != "operator", rng, N_NULL)
            stat["n_groups"] = len(order)
            per_set[sname] = stat
        out["registers"][reg] = {"verdict": _verdict_for_register(per_set),
                                 "per_set": per_set}
    out["verdict"] = out["registers"][PRIMARY]["verdict"]
    out["primary"] = PRIMARY
    return out


# ---------------------------------------------------------------------------
# Planted worlds (feature-level; drive the REAL analyse path)
# ---------------------------------------------------------------------------
def _plant_features(corpus: dict, length: np.ndarray, mode: str, ell: int,
                    d: int, rng: np.random.Generator) -> dict:
    """Synthesize routing/value/magnitude features with a KNOWN mechanism.
    validate checks the PRIMARY (routing) verdict; value/magnitude mirror it."""
    n = len(corpus["set"])
    funcs = sorted(set(corpus["function"].tolist()))
    base = {f: rng.standard_normal(d) for f in funcs}
    lu = rng.standard_normal(d)                       # length direction
    lo, hi = float(length.min()), float(length.max())

    feat = np.empty((n, ell, d), np.float32)
    for i in range(n):
        sset, f = corpus["set"][i], corpus["function"][i]
        if mode == "VOID":
            feat[i] = 1.0                             # degenerate: zero variance
            continue
        if mode == "EXTENSIONAL":
            v = base[f]                               # function-driven, all sets
        elif mode == "LEXICAL":
            v = base[f] if sset != "alpha" else rng.standard_normal(d)
        elif mode == "LENGTH":                        # length-driven, all sets
            t = (length[i] - lo) / (hi - lo + 1e-9)
            v = t * lu
        elif mode == "ABSENT":
            v = rng.standard_normal(d)
        else:
            raise ValueError(mode)
        feat[i] = v[None, :] + 0.15 * rng.standard_normal((ell, d)).astype(np.float32)
    mag = np.linalg.norm(feat, axis=2, keepdims=True).astype(np.float32)
    return {"routing": feat, "value": feat.copy(), "magnitude": mag}


def planted_worlds():
    items = build_unified_corpus(N_PER_SMOKE, SEED)
    corpus = _corpus_arrays(items)
    length = np.array([len(t) for t in corpus["text"]], float)
    ell = len(pick_layers(41))
    expect = {"EXTENSIONAL": "EXTENSIONAL", "LEXICAL": "LEXICAL",
              "LENGTH": {"LEXICAL", "ABSENT"}, "ABSENT": "ABSENT", "VOID": "VOID"}
    worlds = {}
    for mode, want in expect.items():
        rng = np.random.default_rng(SEED)
        feats = _plant_features(corpus, length, mode, ell=ell, d=48, rng=rng)
        worlds[mode] = (feats, corpus, length, want)
    return worlds


def run_validate() -> int:
    log("[coext] --validate: planted worlds through the real analyse path")
    ok = True
    for name, (feats, corpus, length, want) in planted_worlds().items():
        rng = np.random.default_rng(SEED)
        res = analyse(feats, corpus, length, rng)
        got = res["verdict"]
        want_set = want if isinstance(want, set) else {want}
        passed = got in want_set
        ok = ok and passed
        rr = res["registers"]["routing"]["per_set"]

        def _s(per_set, k):
            s = per_set.get(k)
            return f"{s['D']:+.3f}/p{s['p']:.3f}" if s and s["D"] == s["D"] else "nan"

        log(f"[coext]   {name:12s} -> routing {got:12s} "
            f"(want {'|'.join(sorted(want_set)):16s}) op={_s(rr, 'operator')} "
            f"ar={_s(rr, 'arity')} al={_s(rr, 'alpha')} {'OK' if passed else 'FAIL'}")
    log(f"[coext] validate {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Real backend
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--out", default="results/p_coext_registers_s343/run")
    ap.add_argument("--n-per", type=int, default=N_PER)
    ap.add_argument("--max-length", type=int, default=64)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    from dmd_transport import RealBackend

    n_per = N_PER_SMOKE if args.smoke else args.n_per
    items = build_unified_corpus(n_per, SEED)
    corpus = _corpus_arrays(items)
    texts = corpus["text"].tolist()
    counts = {s: int((corpus["set"] == s).sum()) for s in SETS}
    log(f"[coext] corpus {len(items)} items {counts}")

    be = RealBackend(args.model_id, args.device, args.dtype)
    n_layers = len(find_gate_modules(be.model))
    want = pick_layers(n_layers)
    log(f"[coext] {args.model_id}: {n_layers} layers, capturing {len(want)} "
        f"depths {want}")

    feats = capture(be, texts, want, args.max_length)
    length = feats["plen"].astype(float)

    chk = capture(be, texts[:DET_CHECK_N], want, args.max_length)
    det_dev = float(np.abs(feats["value"][:DET_CHECK_N] - chk["value"]).max())
    det_ok = det_dev <= DET_TOL

    rng = np.random.default_rng(SEED)
    res = analyse(feats, corpus, length, rng)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    corpus_hash = hashlib.sha256(
        json.dumps(sorted(texts), sort_keys=True).encode()).hexdigest()[:16]
    meta = {
        "probe": "P-SCHEDULE-READ-C",
        "frozen": "s343 pre-data freeze (Michael GO): register-complete "
                  "co-extensional test; operator-geometry-la-toolkit.md §5f "
                  "successor + cycle-carrier-signal.md",
        "pre_data": {
            "REGISTERS": list(REGISTERS), "PRIMARY": PRIMARY, "SETS": list(SETS),
            "N_NULL": N_NULL, "ALPHA": ALPHA, "FLOOR_D": FLOOR_D, "SEED": SEED,
            "apriori_routing": APRIORI,
            "ladder": "group-centroid level; operator(confounded) -> "
                      "arity(same-arity) -> alpha(same-arity + |Δlen| partial, "
                      "s339); EXTENSIONAL iff alpha passes; LEXICAL iff signal "
                      "vanishes at constant alphabet; primary = routing",
            "deferred": "17x17 fate register (needs outcome-pole machinery)",
        },
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "model_id": args.model_id, "device": args.device, "dtype": args.dtype,
        "smoke": bool(args.smoke), "n_per": n_per, "n_items": len(items),
        "counts": counts, "want_layers": want, "corpus_hash": corpus_hash,
        "git_sha": git_sha(), "det_value_dev": det_dev, "det_ok": det_ok,
        "verdict": res["verdict"], "primary": PRIMARY, "registers": res["registers"],
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))
    np.savez_compressed(
        out / "features.npz",
        value=feats["value"].astype(np.float16),
        routing=feats["routing"].astype(np.int8),
        magnitude=feats["magnitude"].astype(np.float16),
        plen=feats["plen"], set=corpus["set"], function=corpus["function"],
        arity=corpus["arity"], group=corpus["group"], want=np.array(want),
    )

    log(f"[coext] det_value_dev={det_dev:.2e} ok={det_ok}")
    for reg in REGISTERS:
        rv = res["registers"][reg]
        star = " *PRIMARY*" if reg == PRIMARY else ""
        log(f"[coext] {reg:9s} -> {rv['verdict']:12s}{star}")
        for s in SETS:
            st = rv["per_set"].get(s)
            if st and st["D"] == st["D"]:
                log(f"[coext]     {s:9s} D={st['D']:+.4f} p={st['p']:.4f} "
                    f"(within {st['within_mean']:+.3f} / across "
                    f"{st['across_mean']:+.3f}, groups {st.get('n_groups')})")
    log(f"[coext] === VERDICT ({PRIMARY}): {res['verdict']} "
        f"(a-priori {APRIORI.get(res['verdict'])}) ===")
    log(f"[coext] wrote {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
