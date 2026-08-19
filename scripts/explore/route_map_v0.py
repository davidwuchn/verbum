#!/usr/bin/env python3
"""Route-map v0 — the DYNAMIC half of the statechart (s344 repoint, EXPLORATORY).

The grams are station maps — NO TRAINS (s308, never built). This instrument reads
the TRAINS: per probe, the per-layer reduction TRAJECTORY expressed in FRAME-
INVARIANT gram/pole coordinates (cosine onto the committed Qwen3-14B labeled pole
centroids). We point it at a DIVERSE, BANDED prompt set and LOOK at what routes the
model actually traces — plain prose vs symbolic lambda especially — to understand
what the model is really doing BEFORE designing special probes.

INSTRUMENT-ONLY / EXPLORATORY (Michael s344): NO verdict tree, NO a-priori mass —
pre-registering a claim about a phenomenon we have not LOOKED at yet is backwards.
QWEN3-14B ONLY (our designated model): understand ONE model deeply; it becomes the
reference frame for reading universal-vs-deviation across models LATER.

But exploration still owes VALIDITY (so we don't read noise as structure):
  - planted synthetic trajectory with a KNOWN route  -> reader recovers it
  - shuffled-layer null                              -> route-coherence collapses
  - determinism re-capture                           -> dev <= tol
  - G0 coherence                                     -> in-path 17x17 reproduces the
                                                        committed rank-3 outcome gram

A route (per probe), all frame-invariant:
  route17    (L, 17)   cosine onto the 9 identity + 8 outcome pole centroids
  route3     (L, 3)    rank-3 reduction = the fire/halt/diverge simplex path
  stations   (L,)      argmax pole per layer = the discrete statechart arrows

Register = gate (sign(gate_proj), the s342 universal station-map substrate, the
register the committed 17x17 lives in). Poles + probes are CO-REGISTERED by
re-capturing the 17-basis pole probes IN THE SAME PATH as the diverse probes (the
coext lesson: validate-plumbing == data-plumbing).

License: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_ROOT = _SCRIPT_DIR.parents[1]
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "src"))

from combinator_relationship_map import (  # noqa: E402
    find_gate_modules,
    git_sha,
    log,
)

# ---------------------------------------------------------------------------
# Basis (co-registered with the committed Qwen3-14B 17x17 outcome register)
# ---------------------------------------------------------------------------
CRYSTAL9 = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
WHNF_STATES = [f"whnf:{o}" for o in ["K", "I", "B", "C", "S", "D", "W"]]
BASIS17 = [*CRYSTAL9, *WHNF_STATES, "div:Y"]
WHNF_JSON = _ROOT / "opcodes" / "data" / "whnf_probes.json"
COMMITTED_XGRAM = _ROOT / "results" / "expanded-gram" / "qwen3-14b"

# The prose->symbolic gradient (the axis that tests "does the reducer run on ALL
# language, notation or not?"): plain everyday prose -> NL with logical/task
# structure -> prose that EVOKES a combinator role (no notation) -> FORMAL lambda/
# combinator notation. cross_domain (code/math/tool) is orthogonal.
BANDS = ("plain_prose", "prose_structured", "nl_combinator", "symbolic_formal",
         "cross_domain")

SEED = 0
DET_CHECK_N = 8
DET_TOL = 5e-3
CAP_PER_STATE = 60          # pole probes per basis state
N_PER_KIND = 16             # diverse probes per kind (subsample for balance)

# Curated PLAIN prose — genuinely non-computational everyday text (the band that
# tests "does the reducer run even here"). Kept short + concrete + varied topic.
CURATED_PLAIN_PROSE = [
    "The kettle whistled just as she walked into the kitchen.",
    "Rain tapped softly against the window all afternoon.",
    "He folded the last shirt and closed the suitcase.",
    "The old dog stretched and settled back down by the fire.",
    "Fresh bread was cooling on the counter near the window.",
    "They watched the tide come in from the edge of the pier.",
    "A single lamp lit the corner of the quiet room.",
    "The train pulled slowly out of the little country station.",
    "She wrote a short note and left it on the table.",
    "Morning fog drifted low across the empty field.",
    "The children ran ahead, laughing, toward the swings.",
    "He poured two cups of coffee and sat down to read.",
    "Snow began to fall gently over the sleeping town.",
    "The garden smelled of lavender after the light rain.",
    "A ferry crossed the harbor under a pale grey sky.",
    "The baker unlocked the door and turned on the lights.",
    "Leaves gathered in the corners of the courtyard.",
    "She hummed an old tune while washing the dishes.",
    "The market was busy with people buying fruit and flowers.",
    "A warm breeze moved the curtains in the open window.",
    "He tightened his scarf and stepped out into the cold.",
    "The cat curled up on the warmest chair in the house.",
    "Candles flickered on every table in the small cafe.",
    "The road wound gently between the hills toward the sea.",
    "Grandmother knitted quietly by the light of the window.",
    "The orchard was heavy with apples in late September.",
    "A boy skipped stones across the still surface of the pond.",
    "The clock in the hall chimed softly at midnight.",
    "They shared a pot of tea and talked until dark.",
    "The last bus of the evening rolled down the empty street.",
]


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
# Prompt sets
# ---------------------------------------------------------------------------
def build_pole_probes() -> tuple[list[str], list[str]]:
    """(texts, states) over the 17-basis (9 crystal opcodes + whnf:X + div:Y),
    the EXACT sources the committed centroids used (crystal_probes + whnf_probes)."""
    from verbum.probes.library import crystal_probes

    rng = np.random.default_rng(SEED)
    by: dict[str, list[str]] = {c: [] for c in CRYSTAL9}
    for p in crystal_probes():
        if p.combinator in by:
            by[p.combinator].append(p.prompt)
    texts, states = [], []
    for c in CRYSTAL9:
        sel = by[c]
        if len(sel) > CAP_PER_STATE:
            idx = sorted(rng.choice(len(sel), CAP_PER_STATE, replace=False))
            sel = [sel[i] for i in idx]
        texts += sel
        states += [c] * len(sel)
    d = json.loads(WHNF_JSON.read_text())["states"]
    for s in [*WHNF_STATES, "div:Y"]:
        sel = d[s][:CAP_PER_STATE]
        texts += sel
        states += [s] * len(sel)
    return texts, states


def _band_for_kind(kind: str) -> str:
    plain = {"null_baseline", "basin_narrative", "curated_plain_prose"}
    structured = {
        "fixedpoint_natural_language", "basin_reasoning", "basin_analogy",
        "basin_instruction", "fixedpoint_cross_domain", "reduction_natural",
    }
    cross = {"basin_coding", "basin_arithmetic", "basin_tool", "basin_retrieval",
             "reduction_code"}
    formal = {"reduction_formal", "reduction_redex", "reduction_chain",
              "reduction_meta", "reduction_value", "fixedpoint_combinator_pure"}
    if kind in plain:
        return "plain_prose"
    if kind in structured:
        return "prose_structured"
    if kind in cross:
        return "cross_domain"
    if kind in formal:
        return "symbolic_formal"
    # lambda_* kernel probes + fixedpoint_combinator_prose = prose evoking a
    # combinator role, NO notation (the thesis bridge band)
    if kind.startswith("lambda_") or kind == "fixedpoint_combinator_prose":
        return "nl_combinator"
    return "symbolic_formal"


def build_diverse_probes(n_per_kind: int) -> list[dict]:
    """Banded, tagged diverse prompt set. plain_prose / prose_structured /
    symbolic / cross_domain — so routes color by band AND kind."""
    from verbum.probes.library import all_probes

    rng = np.random.default_rng(SEED + 7)
    ps = all_probes()
    by_cat: dict[str, list[str]] = {}
    for p in ps:
        by_cat.setdefault(p.category, []).append(p.prompt)

    # symbolic kernel: sample per-opcode from lambda_* categories
    symbolic_cats = [c for c in by_cat if c.startswith("lambda_")]
    reduction_cats = [c for c in by_cat
                      if c.startswith("reduction_")
                      or c.startswith("fixedpoint_combinator")]
    want_cats = [
        # plain prose
        "null_baseline", "basin_narrative",
        # prose structured
        "fixedpoint_natural_language", "basin_reasoning", "basin_analogy",
        "basin_instruction", "fixedpoint_cross_domain",
        # cross domain
        "basin_coding", "basin_arithmetic", "basin_tool", "basin_retrieval",
        # symbolic
        *symbolic_cats, *reduction_cats,
    ]
    items: list[dict] = []
    seen: set[str] = set()

    def _take(kind: str, prompts: list[str], n: int):
        pool = [p for p in prompts if p not in seen]
        if len(pool) > n:
            idx = sorted(rng.choice(len(pool), n, replace=False))
            pool = [pool[i] for i in idx]
        for p in pool:
            seen.add(p)
            items.append({"prompt": p, "kind": kind, "band": _band_for_kind(kind)})

    for c in want_cats:
        if c in by_cat:
            _take(c, by_cat[c], n_per_kind)
    _take("curated_plain_prose", CURATED_PLAIN_PROSE, len(CURATED_PLAIN_PROSE))

    for i, it in enumerate(items):
        it["id"] = f"d{i:04d}"
    return items


# ---------------------------------------------------------------------------
# Capture (sign(gate_proj) last-token, all want-layers, one forward per text)
# ---------------------------------------------------------------------------
def pick_layers(n_layers: int) -> list[int]:
    return list(range(n_layers))          # ALL layers — routes want full depth


def capture_signs(be, texts: list[str], want: list[int],
                  max_length: int = 64) -> np.ndarray:
    """(n, L, d_ff) int8 sign(gate_proj) at the last token."""
    import torch

    model, tok, device = be.model, be.tok, be.device
    gate_mods = find_gate_modules(model)
    want_set = set(want)
    buf: dict[int, np.ndarray] = {}

    def mk_hook(li):
        def hook(_m, _inp, out):
            buf[li] = np.sign(out[0, -1].detach().float().cpu().numpy()).astype(np.int8)
        return hook

    handles = [mod.register_forward_hook(mk_hook(li))
               for (li, _nm, mod) in gate_mods if li in want_set]
    n, ell = len(texts), len(want)
    signs = None
    try:
        with torch.no_grad():
            for i, text in enumerate(texts):
                buf.clear()
                enc = tok(text, return_tensors="pt", truncation=True,
                          max_length=max_length)
                enc = {k: v.to(device) for k, v in enc.items()}
                model(**enc)
                if signs is None:
                    dff = buf[want[0]].shape[0]
                    signs = np.empty((n, ell, dff), np.int8)
                for k, li in enumerate(want):
                    signs[i, k] = buf[li]
                if (i + 1) % 200 == 0:
                    log(f"    captured {i + 1}/{n}")
    finally:
        for hd in handles:
            hd.remove()
    return signs


# ---------------------------------------------------------------------------
# Pole centroids + route projection (frame-invariant relational read)
# ---------------------------------------------------------------------------
def build_pole_frame(signs: np.ndarray, states: list[str],
                     order: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """(P, mu): P[S,L,d] CMR'd UNIT pole centroids; mu[L,d] common mode (mean over
    the S pole centroids). Sign-CMR pipeline matching the committed 17x17."""
    st = np.array(states)
    cent = np.stack([signs[st == s].mean(axis=0) for s in order]).astype(np.float32)
    mu = cent.mean(axis=0)                              # (L, d) common mode
    centc = cent - mu[None]                             # CMR
    nrm = np.linalg.norm(centc, axis=2, keepdims=True)
    P = centc / np.where(nrm < 1e-9, 1.0, nrm)
    return P, mu


def project_routes(signs: np.ndarray, P: np.ndarray, mu: np.ndarray) -> np.ndarray:
    """(n, L, S) cosine of each probe's CMR'd sign row onto each pole per layer."""
    x = signs.astype(np.float32) - mu[None]            # (n, L, d)
    nrm = np.linalg.norm(x, axis=2, keepdims=True)
    xn = x / np.where(nrm < 1e-9, 1.0, nrm)
    return np.einsum("nld,sld->nls", xn, P).astype(np.float32)


def pole_gram(P: np.ndarray) -> np.ndarray:
    """(S, S) mean-over-layers cosine gram of the pole centroids (already unit)."""
    ell = P.shape[1]
    return np.einsum("ild,jld->ij", P, P) / ell


def rank3_axes(gram: np.ndarray) -> np.ndarray:
    """(S, 3) top-3 eigenvectors of the 17x17 outcome gram = fire/halt/diverge."""
    _w, v = np.linalg.eigh(gram)
    return v[:, ::-1][:, :3].astype(np.float32)


def participation_ratio(gram: np.ndarray) -> float:
    w = np.clip(np.linalg.eigvalsh(gram), 0, None)
    return float((w.sum() ** 2) / (np.square(w).sum() + 1e-12))


def route_coherence(route17: np.ndarray) -> np.ndarray:
    """Per probe: mean cosine between CONSECUTIVE-layer route vectors = trajectory
    smoothness. Real routes are smooth; shuffled-layer destroys it."""
    a = route17[:, :-1]
    b = route17[:, 1:]
    an = a / (np.linalg.norm(a, axis=2, keepdims=True) + 1e-9)
    bn = b / (np.linalg.norm(b, axis=2, keepdims=True) + 1e-9)
    return (an * bn).sum(axis=2).mean(axis=1)


# ---------------------------------------------------------------------------
# Instrument validity (no verdict — just "are the routes structure not noise")
# ---------------------------------------------------------------------------
def run_validate() -> int:
    log("[route] --validate: instrument validity checks")
    rng = np.random.default_rng(SEED)
    ok = True

    # synthetic world: S poles as orthogonal-ish sign directions in d dims
    S, L, d = 17, 24, 256

    def _noisy(sign_rows):                       # flip ~5% of signs
        s = sign_rows.astype(np.int8)
        return (s + (rng.standard_normal(s.shape) > 1.6) * -2 * s).astype(np.int8)

    base = np.sign(rng.standard_normal((S, d))).astype(np.int8)
    states = [BASIS17[i] for i in range(S) for _ in range(30)]
    pole_signs = _noisy(np.stack(
        [base[i] for i in range(S) for _ in range(30)])[:, None, :].repeat(L, 1))
    P, mu = build_pole_frame(pole_signs, states, BASIS17)

    # a batch of structured multi-segment WALKS (real routes are smooth) + noise
    def _make_walk():
        segs = rng.choice(S, 4, replace=False)   # 4 poles, 4 segments
        bnds = sorted(rng.choice(range(1, L), 3, replace=False))
        route, si = [], 0
        for li in range(L):
            if si < 3 and li >= bnds[si]:
                si += 1
            route.append(segs[si])
        return np.array(route)

    walks = [_make_walk() for _ in range(40)]
    walk_signs = _noisy(np.stack(
        [np.stack([base[w[li]] for li in range(L)]) for w in walks]))

    # (1) planted KNOWN route: argmax stations recover the planted walk
    r_walk = project_routes(walk_signs, P, mu)
    stations = r_walk.argmax(axis=2)
    recov = float(np.mean([(stations[i] == walks[i]).mean()
                           for i in range(len(walks))]))
    p1 = recov >= 0.8
    ok &= p1
    tag1 = "OK" if p1 else "FAIL"
    log(f"[route]   planted-route recovery {recov:.2f} (want>=0.80) {tag1}")

    # (2) shuffled-layer null: structured walks are smooth; shuffling breaks it
    c_real = route_coherence(r_walk).mean()
    c_shuf = np.mean([route_coherence(r_walk[i:i + 1, rng.permutation(L)]).mean()
                      for i in range(len(walks))])
    p2 = c_real > c_shuf + 0.05
    ok &= p2
    log(f"[route]   coherence real {c_real:.3f} > shuffled-layer {c_shuf:.3f} "
        f"(+0.05) {'OK' if p2 else 'FAIL'}")

    # (3) rank-3 sanity on the synthetic pole gram (should be high-rank here — a
    #     sanity that PR is computed, not a claim; real G0 is on live data)
    g = pole_gram(P)
    pr = participation_ratio(g)
    log(f"[route]   synthetic pole-gram PR={pr:.2f} (diagnostic)")

    log(f"[route] validate {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# G0 coherence with the committed Qwen3-14B outcome register
# ---------------------------------------------------------------------------
def g0_coherence(my_gram17: np.ndarray) -> dict:
    """Compare the in-path 17x17 to the committed Qwen3-14B outcome gram: PR (want
    ~3) + off-diagonal correlation. Coherence, not a verdict."""
    out = {"my_pr": participation_ratio(my_gram17),
           "my_eigs_top6": np.sort(np.linalg.eigvalsh(my_gram17))[::-1][:6].tolist()}
    jf = COMMITTED_XGRAM / "expanded_gram.json"
    if jf.exists():
        d = json.loads(jf.read_text())
        b24 = d["basis"]
        g24 = np.array(d["consensus_gram_24"], float)
        idx = [b24.index(x) for x in BASIS17]
        ref17 = g24[np.ix_(idx, idx)]
        iu = np.triu_indices(17, k=1)
        out["committed_pr"] = participation_ratio(ref17)
        out["offdiag_corr_vs_committed"] = float(
            np.corrcoef(my_gram17[iu], ref17[iu])[0, 1])
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--out", default="results/route_map_v0_s344/run")
    ap.add_argument("--n-per-kind", type=int, default=N_PER_KIND)
    ap.add_argument("--max-length", type=int, default=64)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    from dmd_transport import RealBackend

    pole_texts, pole_states = build_pole_probes()
    diverse = build_diverse_probes(6 if args.smoke else args.n_per_kind)
    from collections import Counter
    log(f"[route] pole probes {len(pole_texts)} | diverse {len(diverse)} "
        f"bands {Counter(d['band'] for d in diverse)}")

    be = RealBackend(args.model_id, args.device, args.dtype)
    n_layers = len(find_gate_modules(be.model))
    want = pick_layers(n_layers)
    log(f"[route] {args.model_id}: {n_layers} layers (all), d captured per layer")

    # pass 1: pole frame
    log("[route] pass 1/2 — pole probes -> frame")
    pole_signs = capture_signs(be, pole_texts, want, args.max_length)
    P, mu = build_pole_frame(pole_signs, pole_states, BASIS17)
    gram17 = pole_gram(P)
    V3 = rank3_axes(gram17)
    g0 = g0_coherence(gram17)
    log(f"[route] G0: my PR={g0['my_pr']:.2f} committed PR={g0.get('committed_pr')} "
        f"offdiag_corr={g0.get('offdiag_corr_vs_committed')}")
    del pole_signs

    # pass 2: diverse routes (+ determinism sub-check)
    log("[route] pass 2/2 — diverse probes -> routes")
    dtexts = [d["prompt"] for d in diverse]
    dsigns = capture_signs(be, dtexts, want, args.max_length)
    route17 = project_routes(dsigns, P, mu)                 # (n, L, 17)
    route3 = np.einsum("nls,sk->nlk", route17, V3)          # (n, L, 3)
    stations = route17.argmax(axis=2).astype(np.int16)      # (n, L)

    chk = capture_signs(be, dtexts[:DET_CHECK_N], want, args.max_length)
    r17b = project_routes(chk, P, mu)
    det_dev = float(np.abs(route17[:DET_CHECK_N] - r17b).max())
    det_ok = det_dev <= DET_TOL

    # summary: per-band pole occupancy over depth + station-transition matrix
    bands = np.array([d["band"] for d in diverse])
    kinds = np.array([d["kind"] for d in diverse])
    occupancy = {b: route17[bands == b].mean(axis=0).tolist()
                 for b in BANDS if (bands == b).any()}
    coh = route_coherence(route17)
    trans = np.zeros((17, 17), int)
    for s in stations:
        for a, b in itertools.pairwise(s):
            trans[a, b] += 1

    out = Path(args.out)
    (out / "plots").mkdir(parents=True, exist_ok=True)
    corpus_hash = hashlib.sha256(
        json.dumps(sorted(dtexts + pole_texts), sort_keys=True).encode()
    ).hexdigest()[:16]
    meta = {
        "instrument": "route-map-v0 (s344, EXPLORATORY, instrument-only)",
        "note": "NO verdict / NO a-priori — observe routes on diverse prompts, "
                "then design special probes. Qwen3-14B only.",
        "basis17": BASIS17, "bands": list(BANDS),
        "register": "sign(gate_proj) last-token, all layers",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "model_id": args.model_id, "device": args.device, "dtype": args.dtype,
        "smoke": bool(args.smoke), "n_pole": len(pole_texts), "n_diverse": len(diverse),
        "n_layers": n_layers, "corpus_hash": corpus_hash, "git_sha": git_sha(),
        "det_route_dev": det_dev, "det_ok": det_ok, "g0_coherence": g0,
        "band_counts": {b: int((bands == b).sum()) for b in BANDS},
        "kind_counts": {k: int((kinds == k).sum()) for k in sorted(set(kinds))},
        "mean_route_coherence": float(coh.mean()),
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))
    (out / "summary.json").write_text(json.dumps({
        "occupancy_by_band": occupancy,
        "station_transitions": trans.tolist(),
        "coherence_by_band": {b: float(coh[bands == b].mean())
                              for b in BANDS if (bands == b).any()},
    }, indent=2, default=_json_native))
    np.savez_compressed(
        out / "routes.npz",
        route17=route17.astype(np.float16), route3=route3.astype(np.float16),
        stations=stations, band=bands, kind=kinds,
        probe_id=np.array([d["id"] for d in diverse]),
        basis17=np.array(BASIS17), V3=V3, gram17=gram17,
    )
    log(f"[route] det_route_dev={det_dev:.2e} ok={det_ok} | "
        f"mean coherence={coh.mean():.3f}")
    log(f"[route] wrote {out}/ (routes.npz, summary.json, meta.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
