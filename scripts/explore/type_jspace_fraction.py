#!/usr/bin/env python3
"""P-TYPE-JS — is the type-lattice exhaust the J-space workspace? (fractions)

Pre-reg: mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md
(#p-type-js, FROZEN s284 on Michael GO). Positive-identification complement to
the 1b/1c/QK negatives: the lattice profiles like a J-space resident (readable,
broadcast, causally decoupled); the type-check like a K-class operator.

MEASUREMENT
  1. Capture labeled Montague-type residuals at the s270 canonical depth layers
     {16, 32, 48} (all inside the measured band L6-L50).
  2. Role subspaces per depth layer (1b construction, std space):
     bind = span{c_QUANT, c_DET}, comp = span{c_MOD},
     rolenull = span{c_CONN, c_FUNC}, entity = span{c_ENTITY}.
     Transport std -> RAW residual space (v_raw prop-to v_std * sd; the space
     the Jacobian reads; no layernorm map), re-orthonormalize (QR).
  3. J-space bases via opcodes/projector.py::jspace_bases with the s270 config
     (k=32, m=64, target_layer=62, seed 270) so lattice fractions are directly
     comparable to the opcode fractions in
     results/opcode-trace/qwen3-32b/jspace_projector.json.
     Basis prompts = the LABELED_DATA sentences (same distribution as capture).
  4. Fraction per condition = mean over subspace basis rows of
     workspace_fraction(V, x) = ||V x||^2 / ||x||^2.

NULLS (mandatory, pre-committed)
  (1) matched-random unit vectors (analytic E = k/d ~ 0.006).
  (2) full shuffled-label pipelines (shuffle -> centroids -> subspace ->
      identical transport -> identical fraction; N=200, paired across layers).

VERDICT (FROZEN): JS-RESIDENT <=> bind, comp, rolenull, entity EACH beat
matched-random p<0.05 pooled over the 3 depth layers. JS-SPECIFIC (secondary)
<=> roles additionally beat the shuffled-label null p<0.05. Family ordering vs
artifact opcode fractions (content Y/WHNF/S vs operator K/I/B) verbatim, never
gated; ENTITY predicted highest. Negative (~k/d) -> exhaust != workspace.

lambda measure: J-space membership = readout/value-register geometry; the
lattice is a readout object -> register-matched. Occupancy != consultation
(1b settled consultation, negative).

Usage:
    uv run python scripts/explore/type_jspace_fraction.py --validate  # no model
    uv run python scripts/explore/type_jspace_fraction.py \
        --model Qwen/Qwen3-32B --device mps                # verdict host

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "explore"))
sys.path.insert(0, str(_ROOT / "wrapper"))
sys.path.insert(0, str(_ROOT / "opcodes"))

from probe_type_qwen3_32b import (  # noqa: E402
    LABELED_DATA,
    build_probing_dataset,
    load_model,
)
from projector import (  # noqa: E402
    jspace_bases,
    random_vector_fractions,
    workspace_fraction,
)
from type_lattice_geometry import TYPE_ORDER, centroids  # noqa: E402
from type_zone_ablation import ROLES, layer_geometry, role_subspace  # noqa: E402

CONDS = ["bind", "comp", "rolenull", "entity"]
COND_TYPES = {**ROLES, "entity": ["ENTITY"]}
DEPTH_LAYERS = [16, 32, 48]          # s270 canonical (k=32, m=64, target L62)
S270 = {"k": 32, "m": 64, "target_layer": 62, "seed": 270}
ARTIFACT = _ROOT / "results" / "opcode-trace" / "qwen3-32b" / "jspace_projector.json"


# ── measurement core (model-free; --validate covers it) ────────────────────────
def raw_subspace(basis_std: np.ndarray, sd: np.ndarray) -> np.ndarray:
    """Std-space orthonormal rows -> RAW-residual-space orthonormal rows (QR)."""
    m = basis_std * sd[None, :]
    q, _ = np.linalg.qr(m.T)
    return np.ascontiguousarray(q.T)


def subspace_fraction(jbasis: np.ndarray, sub: np.ndarray) -> float:
    """Mean workspace fraction over the subspace's orthonormal rows."""
    return float(np.mean([workspace_fraction(jbasis, r) for r in sub]))


def cond_subspaces(geo_like: dict, sd: np.ndarray) -> dict[str, np.ndarray]:
    out = {}
    for cnd in CONDS:
        b = role_subspace(geo_like, COND_TYPES[cnd])
        if b is None:
            raise RuntimeError(f"missing class for condition {cnd}")
        out[cnd] = raw_subspace(b, sd)
    return out


def layer_fractions(jbasis: np.ndarray, geo: dict, y: np.ndarray,
                    rng, n_null: int) -> dict:
    """Real + shuffled-label-null fractions for one depth layer."""
    sd = geo["sd"]
    real = {c: subspace_fraction(jbasis, s)
            for c, s in cond_subspaces(geo, sd).items()}
    null: dict[str, list[float]] = {c: [] for c in CONDS}
    for _ in range(n_null):
        yp = rng.permutation(y)
        c, present = centroids(geo["z"], yp, TYPE_ORDER)
        subs = cond_subspaces({"present": present, "centroids": c}, sd)
        for cnd in CONDS:
            null[cnd].append(subspace_fraction(jbasis, subs[cnd]))
    return {"real": real, "null": {c: np.array(v) for c, v in null.items()}}


def aggregate(rows: dict[int, dict], rand_frac: np.ndarray) -> dict:
    """Pool over depth layers (paired null iterations); p vs both nulls."""
    layers = sorted(rows)
    agg = {}
    for cnd in CONDS:
        real = float(np.mean([rows[L]["real"][cnd] for L in layers]))
        null = np.mean(np.stack([rows[L]["null"][cnd] for L in layers]), axis=0)
        agg[cnd] = {
            "fraction": round(real, 5),
            "null_shufflabel_mean": round(float(null.mean()), 5),
            "null_shufflabel_std": round(float(null.std()), 5),
            "p_vs_shufflabel": float(np.mean(null >= real)),
            "p_vs_random": float(np.mean(rand_frac >= real)),
        }
    return agg


def verdict_block(agg: dict, k_over_d: float) -> dict:
    js_resident = all(agg[c]["p_vs_random"] < 0.05 for c in CONDS)
    js_specific = all(agg[c]["p_vs_shufflabel"] < 0.05
                      for c in ("bind", "comp", "rolenull"))
    return {"js_resident": bool(js_resident),
            "js_specific": bool(js_specific),
            "k_over_d_baseline": round(k_over_d, 5),
            "fractions": {c: agg[c]["fraction"] for c in CONDS}}


# ── validation (no model) ─────────────────────────────────────────────────────
def validate() -> int:
    rng = np.random.default_rng(11)
    d, k, n_per = 96, 8, 40
    fails: list[str] = []

    def check(name: str, ok: bool, detail: str) -> None:
        print(f"[js][validate] {'PASS' if ok else 'FAIL'} {name}: {detail}",
              file=sys.stderr)
        if not ok:
            fails.append(name)

    jbasis = np.linalg.qr(rng.standard_normal((d, k)))[0].T      # (k, d)

    # 1. planted-inside subspace -> fraction ~1; random -> ~k/d
    inside = np.linalg.qr((rng.standard_normal((2, k)) @ jbasis).T)[0].T
    f_in = subspace_fraction(jbasis, inside)
    rand = random_vector_fractions(jbasis, n=500, rng=rng)
    check("planted_inside", f_in > 0.999, f"fraction={f_in:.4f}")
    check("random_baseline", abs(rand.mean() - k / d) < 0.02,
          f"mean={rand.mean():.4f} expect~{k / d:.4f}")

    # 2. raw_subspace transport: orthonormal + span of (b * sd)
    b = np.linalg.qr(rng.standard_normal((d, 2)))[0].T
    sd = rng.uniform(0.5, 2.0, d)
    m = raw_subspace(b, sd)
    ortho = np.allclose(m @ m.T, np.eye(2), atol=1e-8)
    qr_raw = np.linalg.qr((b * sd[None, :]).T)[0]
    span_ok = np.allclose(qr_raw @ qr_raw.T, m.T @ m, atol=1e-8)
    check("raw_subspace", ortho and span_ok, f"ortho={ortho} span={span_ok}")

    # 3. end-to-end: QUANT/DET centroids planted INSIDE J-space -> bind
    #    resident+specific; others built from directions outside the span.
    means = {}
    for t in TYPE_ORDER:
        v = rng.standard_normal(d)
        v -= jbasis.T @ (jbasis @ v)               # push outside span
        means[t] = 3.0 * v / np.linalg.norm(v)
    means["QUANT"] = 3.0 * jbasis[0]
    means["DET"] = 3.0 * jbasis[1]
    means["ENTITY"] = np.zeros(d)
    x = np.concatenate([means[t] + 0.3 * rng.standard_normal((n_per, d))
                        for t in TYPE_ORDER])
    y = np.array([t for t in TYPE_ORDER for _ in range(n_per)])
    geo = layer_geometry(x, y, rng, 50)
    rows = {0: layer_fractions(jbasis, geo, y, rng, 200)}
    agg = aggregate(rows, rand)
    bq = agg["bind"]
    check("planted_bind_resident",
          bq["p_vs_random"] < 0.05 and bq["fraction"] > 0.5,
          f"frac={bq['fraction']} p_rand={bq['p_vs_random']}")
    check("planted_bind_specific", bq["p_vs_shufflabel"] < 0.05,
          f"p_shuf={bq['p_vs_shufflabel']}")
    cq = agg["comp"]
    check("unplanted_comp_low", cq["fraction"] < 0.2,
          f"frac={cq['fraction']}")
    print(f"[js][validate] {'ALL PASS' if not fails else f'FAILURES: {fails}'}",
          file=sys.stderr)
    return 0 if not fails else 1


# ── main ───────────────────────────────────────────────────────────────────────
def git_sha() -> str | None:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                           text=True, cwd=_ROOT, timeout=10)
        return r.stdout.strip() or None
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="P-TYPE-JS lattice workspace fraction")
    ap.add_argument("--model", default="Qwen/Qwen3-32B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--n-null", type=int, default=200)
    ap.add_argument("--n-rand", type=int, default=1000)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--output", default=None)
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        sys.exit(validate())

    rng = np.random.default_rng(args.seed)
    model, tok, config = load_model(args.model, device=args.device)
    n_layers = config.num_hidden_layers
    print(f"[js] host={args.model} layers={n_layers} "
          f"depth_layers={DEPTH_LAYERS} s270_config={S270}", file=sys.stderr)

    # 1. capture + geometry at the canonical depth layers
    data, n_lab, n_skip = build_probing_dataset(
        model, tok, DEPTH_LAYERS, LABELED_DATA, verbose=True)
    print(f"[js] labeled={n_lab} skipped={n_skip}", file=sys.stderr)
    geos = {}
    for L in DEPTH_LAYERS:
        x, y = data[L]
        geos[L] = layer_geometry(x, y, rng, 200)
        print(f"[js] geom L{L} PR={geos[L]['pr_real']:.2f} "
              f"p={geos[L]['p_lowrank']}", file=sys.stderr)

    # 2. J-space bases (heavy step): s270 config, basis prompts = the labeled
    #    sentences themselves (same distribution as capture; pre-reg choice)
    prompts = [s for s, _ in LABELED_DATA]
    print(f"[js] building J-space bases on {len(prompts)} prompts "
          f"(k={S270['k']} m={S270['m']} target=L{S270['target_layer']})...",
          file=sys.stderr)
    bases = jspace_bases(
        model, tok, prompts,
        layers=DEPTH_LAYERS, target_layer=S270["target_layer"],
        k=S270["k"], m=S270["m"], batch_size=args.batch_size,
        seed=S270["seed"])
    for L, b in bases.items():
        print(f"[js] jbasis L{L}: k={b.k} d={b.d} "
              f"strength0={float(b.strengths[0]):.2f}", file=sys.stderr)

    # 3. fractions + nulls (numpy from here)
    rows = {}
    rand_frac = None
    for L in DEPTH_LAYERS:
        jb = bases[L].basis
        if rand_frac is None:
            rand_frac = random_vector_fractions(jb, n=args.n_rand, rng=rng)
        x, y = data[L]
        rows[L] = layer_fractions(jb, geos[L], y, rng, args.n_null)
        r = rows[L]["real"]
        print(f"[js] L{L} fractions: " +
              " ".join(f"{c}={r[c]:.4f}" for c in CONDS), file=sys.stderr)

    k_over_d = bases[DEPTH_LAYERS[0]].k / bases[DEPTH_LAYERS[0]].d
    agg = aggregate(rows, rand_frac)
    verdict = verdict_block(agg, k_over_d)

    # 4. family comparison rows from the s270 artifact (verbatim, not gated)
    family = None
    if ARTIFACT.exists():
        art = json.loads(ARTIFACT.read_text())
        family = {L: art["layers"][str(L)]["fractions"]
                  for L in DEPTH_LAYERS if str(L) in art["layers"]}

    for c in CONDS:
        a = agg[c]
        print(f"[js] AGG {c:9s} frac={a['fraction']:.4f} "
              f"shuf_null={a['null_shufflabel_mean']:.4f} "
              f"p_shuf={a['p_vs_shufflabel']:.3f} "
              f"p_rand={a['p_vs_random']:.4f}", file=sys.stderr)
    print(f"[js] baseline k/d={k_over_d:.5f} "
          f"rand_mean={float(rand_frac.mean()):.5f}", file=sys.stderr)
    print(f"[js] VERDICT: {verdict}", file=sys.stderr)

    slug = args.model.split("/")[-1].lower().replace(".", "-")
    out = (Path(args.output) if args.output
           else _ROOT / "results" / "type-jspace" / slug)
    out.mkdir(parents=True, exist_ok=True)
    res = {
        "experiment": "P-TYPE-JS",
        "prereg": ("mementum/knowledge/explore/"
                   "types-are-the-well-formedness-of-reduction.md#p-type-js"),
        "model": args.model, "device": args.device,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(),
        "seed": args.seed, "n_null": args.n_null, "n_rand": args.n_rand,
        "s270_config": S270, "depth_layers": DEPTH_LAYERS,
        "n_labeled": n_lab, "conds": {c: COND_TYPES[c] for c in CONDS},
        "basis_prompts": "LABELED_DATA sentences (pre-reg documented choice)",
        "geometry": {str(L): {"pr_real": round(geos[L]["pr_real"], 3),
                              "p_lowrank": geos[L]["p_lowrank"]}
                     for L in DEPTH_LAYERS},
        "jspace_strengths": {str(L): [round(float(s), 2)
                                      for s in bases[L].strengths]
                             for L in DEPTH_LAYERS},
        "per_layer_fractions": {str(L): {c: round(rows[L]["real"][c], 5)
                                         for c in CONDS}
                                for L in DEPTH_LAYERS},
        "aggregate": agg,
        "random_baseline": {"k_over_d": round(k_over_d, 5),
                            "mean": round(float(rand_frac.mean()), 5),
                            "std": round(float(rand_frac.std()), 5)},
        "opcode_family_fractions_s270": family,
        "verdict": verdict,
    }
    (out / "type_jspace.json").write_text(json.dumps(res, indent=2))
    print(f"[js] wrote {out}/type_jspace.json", file=sys.stderr)


if __name__ == "__main__":
    main()
