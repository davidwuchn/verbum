#!/usr/bin/env python3
"""P-TYPE-QK — is the type lattice pre-shaped for the QK bilinear? (geometry only)

Pre-reg: mementum/knowledge/explore/type-check-is-the-qk-bilinear.md (#p-type-qk,
DRAFT s284 — the 32B verdict run only after the pre-reg is approved/frozen).

HYPOTHESIS (draft-frozen). If the type-check IS the QK bilinear
(query(functor)·key(argument) >= threshold == licensed), the model's own read-in
map for attention (input_layernorm -> W_Q/W_K) preferentially amplifies the
type-lattice role subspaces within the low-rank band. The 1a residual lattice is
then the SHADOW of QK-native type structure. Mechanism-shaped refinement: functor
subspaces load the QUERY side, the ENTITY/argument direction loads the KEY side
(the name_pen edge: a predicate queries for its subject).

MEASUREMENT (register-matched; RoPE-invariant by construction)
  1. Capture labeled Montague-type residuals every decoder layer (reuses
     probe_type_qwen3_32b capture; residual index L = output of layers[L],
     embed = -1). Attention of decoder layer M reads
     input_layernorm_M(residual_{M-1}) -> band residual layer L pairs with the
     W_Q/W_K of layer L+1.
  2. Per layer: layer_geometry (standardize -> centroid SVD -> PR +
     shuffled-label null) -> find_band (1b v4 procedure verbatim, falsy-zero
     fixed). In-run band detection, procedure identical to 1b.
  3. Role subspaces from class centroids in std space (1b v3 lesson — centroid
     construction, NOT raw SVD axes; robust to the 4B axis tie-flip):
     bind = span{c_QUANT, c_DET}, comp = span{c_MOD},
     rolenull = span{c_CONN, c_FUNC} (verbatim row, not gated),
     entity = span{c_ENTITY} (predicted KEY-side).
  4. Map each std-space basis into the space W_Q/W_K actually reads:
     v_attn prop-to (v_std * sd_L) * gamma_{L+1}   (capture std then the model's
     own input_layernorm weight; the RMSNorm scalar drops out of a direction),
     then re-orthonormalize (QR).
  5. Gain per head h:  rho = D * ||W_h v||^2 / ||W_h||^2_F   (rho = 1 is the
     analytic random-direction expectation). Subspace gain = mean over its
     orthonormal basis; aggregate = mean over heads (Q: all heads; K: KV heads,
     separate) then over band layers. RoPE = per-position orthogonal rotation
     -> norms invariant -> gain is RoPE-free.

NULL (mandatory, λ yardstick). N full shuffled-label pipelines per layer
(shuffle type labels -> centroids -> role_subspace -> identical mapping ->
identical gain), band-aggregated per iteration; p = frac(null_agg >= real_agg).
"Looks amplified" != "is": rho>1 counts ONLY against this matched null.

VERDICT (per the draft pre-reg; advisory until the pre-reg is frozen):
  QK-ALIGNED       <=> bind AND comp Q-side band-aggregate beat null, p<0.05.
  MECHANISM-SHAPED <=> QK-ALIGNED and A(bind)>0 and A(comp)>0 and A(entity)<0
                       where A = rho_Q - rho_K (side asymmetry, verbatim signs).
  P3 band-vs-out-of-band profile reported verbatim, never gated.
  rolenull reported verbatim, never gated.

λ measure: claim = routing-register geometry (the check's input map); probe =
value-register lattice projected through the routing register's own read-in
weights = exactly the claimed interface. No behaviour, no causation — the cheap
geometric leg; P-ATT-DIFF/P-ATT-MED carry the behavioural/causal registers.
No single-head claims either direction (C2: 0/128 pre-refuted) — aggregates only.

Usage:
    uv run python scripts/explore/type_qk_alignment.py --validate     # no model
    uv run python scripts/explore/type_qk_alignment.py \
        --model Qwen/Qwen3-0.6B --device mps --layer-stride 2 --n-null 50   # smoke
    uv run python scripts/explore/type_qk_alignment.py \
        --model Qwen/Qwen3-32B --device mps                            # verdict host

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

from probe_type_qwen3_32b import (  # noqa: E402
    LABELED_DATA,
    build_probing_dataset,
    get_transformer_layers,
    load_model,
)
from type_lattice_geometry import TYPE_ORDER, centroids  # noqa: E402
from type_zone_ablation import (  # noqa: E402
    ROLES,
    find_band,
    layer_geometry,
    role_subspace,
)

CONDS = ["bind", "comp", "rolenull", "entity"]
COND_TYPES = {**ROLES, "entity": ["ENTITY"]}


# ── measurement core (model-free; unit-validated by --validate) ────────────────
def map_basis(basis_std: np.ndarray, sd: np.ndarray, gamma: np.ndarray) -> np.ndarray:
    """Std-space orthonormal basis (k,D) -> attention-input-space orthonormal basis.

    A std-space direction v corresponds to raw displacement v * sd; RMSNorm maps
    a displacement to (delta/rms) * gamma and the scalar rms drops out of a
    direction, so v_attn prop-to (v * sd) * gamma. Rows mapped then QR'd."""
    m = basis_std * (sd * gamma)[None, :]
    q, _ = np.linalg.qr(m.T)                  # (D, k) orthonormal columns
    return np.ascontiguousarray(q.T)          # (k, D)


def head_gain_ratios(w: np.ndarray, bases: list[np.ndarray],
                     head_dim: int) -> list[float]:
    """Frobenius-normalized per-head gain, one scalar per basis.

    w: (H*head_dim, D). Each basis: (k, D) orthonormal rows in the space w reads.
    rho(head, vec) = D*||w_h v||^2/||w_h||^2_F; mean over heads AND basis rows
    (rho = 1 == analytic random-direction expectation). One stacked GEMM."""
    n_out, d = w.shape
    h = n_out // head_dim
    stack = np.concatenate(bases, axis=0)                       # (K, D)
    proj = (w @ stack.T).reshape(h, head_dim, -1)               # (H, dh, K)
    ph = (proj ** 2).sum(axis=1)                                # (H, K)
    fro = (w.reshape(h, head_dim, d) ** 2).sum(axis=(1, 2)) + 1e-12
    rho = (d * ph / fro[:, None]).mean(axis=0)                  # (K,) mean over heads
    out, i = [], 0
    for b in bases:
        k = b.shape[0]
        out.append(float(rho[i:i + k].mean()))
        i += k
    return out


def cond_bases(geo_like: dict, sd: np.ndarray, gamma: np.ndarray) -> list[np.ndarray]:
    """The four condition subspaces, mapped to attention-input space. Order=CONDS."""
    bases = []
    for cnd in CONDS:
        b = role_subspace(geo_like, COND_TYPES[cnd])
        if b is None:
            raise RuntimeError(f"missing class for condition {cnd}")
        bases.append(map_basis(b, sd, gamma))
    return bases


def process_layer(wq: np.ndarray, wk: np.ndarray, head_dim: int, gamma: np.ndarray,
                  geo: dict, y: np.ndarray, rng, n_iter: int) -> dict:
    """Real + shuffled-label-null gain ratios for one (residual L, attn L+1) pair."""
    sd = geo["sd"]
    real_bases = cond_bases(geo, sd, gamma)
    null_bases: list[np.ndarray] = []
    for _ in range(n_iter):
        yp = rng.permutation(y)
        c, present = centroids(geo["z"], yp, TYPE_ORDER)
        null_bases.extend(cond_bases({"present": present, "centroids": c}, sd, gamma))
    all_bases = real_bases + null_bases
    rq = head_gain_ratios(wq, all_bases, head_dim)
    rk = head_gain_ratios(wk, all_bases, head_dim)
    nc = len(CONDS)
    out = {"real": {}, "null": {}}
    for j, cnd in enumerate(CONDS):
        out["real"][cnd] = {"q": rq[j], "k": rk[j]}
        out["null"][cnd] = {
            "q": np.array([rq[nc + i * nc + j] for i in range(n_iter)]),
            "k": np.array([rk[nc + i * nc + j] for i in range(n_iter)]),
        }
    return out


def band_aggregate(rows: dict[int, dict]) -> dict:
    """Aggregate real/null over band layers, pairing null iterations across layers."""
    agg = {}
    layers = sorted(rows)
    for cnd in CONDS:
        agg[cnd] = {}
        for side in ("q", "k"):
            real = float(np.mean([rows[L]["real"][cnd][side] for L in layers]))
            null = np.mean(np.stack(
                [rows[L]["null"][cnd][side] for L in layers]), axis=0)
            agg[cnd][side] = {
                "rho": round(real, 4),
                "null_mean": round(float(null.mean()), 4),
                "null_std": round(float(null.std()), 4),
                "p": float(np.mean(null >= real)),
            }
        # side asymmetry A = rho_q - rho_k, with paired-iteration null
        real_a = (np.mean([rows[L]["real"][cnd]["q"] for L in layers])
                  - np.mean([rows[L]["real"][cnd]["k"] for L in layers]))
        nq = np.mean(np.stack([rows[L]["null"][cnd]["q"] for L in layers]), axis=0)
        nk = np.mean(np.stack([rows[L]["null"][cnd]["k"] for L in layers]), axis=0)
        null_a = nq - nk
        agg[cnd]["asym"] = {
            "a": round(float(real_a), 4),
            "p_pos": float(np.mean(null_a >= real_a)),
            "p_neg": float(np.mean(null_a <= real_a)),
        }
    return agg


def verdict_block(agg: dict) -> dict:
    """Draft pre-reg verdict (advisory until the pre-reg is frozen on GO)."""
    p_bind = agg["bind"]["q"]["p"]
    p_comp = agg["comp"]["q"]["p"]
    qk_aligned = bool(p_bind < 0.05 and p_comp < 0.05)
    a_bind = agg["bind"]["asym"]["a"]
    a_comp = agg["comp"]["asym"]["a"]
    a_ent = agg["entity"]["asym"]["a"]
    mech = bool(qk_aligned and a_bind > 0 and a_comp > 0 and a_ent < 0)
    return {"qk_aligned": qk_aligned, "mechanism_shaped": mech,
            "p_bind_q": p_bind, "p_comp_q": p_comp,
            "asym_signs": {"bind": a_bind, "comp": a_comp, "entity": a_ent},
            "note": "advisory until #p-type-qk pre-reg is frozen (Michael GO)"}


# ── validation (no model; λ assert: prove the instrument before trusting it) ──
def validate() -> int:
    rng = np.random.default_rng(7)
    d, dh, hq, hk, n_per = 64, 8, 8, 2, 40
    fails = []

    def check(name: str, ok: bool, detail: str) -> None:
        print(f"[qk][validate] {'PASS' if ok else 'FAIL'} {name}: {detail}",
              file=sys.stderr)
        if not ok:
            fails.append(name)

    # 1. map_basis: orthonormal + spans (b * sd * gamma) under nonuniform scales
    b = np.linalg.qr(rng.standard_normal((d, 2)))[0].T
    sd = rng.uniform(0.5, 2.0, d)
    gamma = rng.uniform(0.5, 1.5, d)
    m = map_basis(b, sd, gamma)
    ortho = np.allclose(m @ m.T, np.eye(2), atol=1e-8)
    raw = b * (sd * gamma)[None, :]
    qr_raw = np.linalg.qr(raw.T)[0]
    span_ok = np.allclose(qr_raw @ qr_raw.T, m.T @ m, atol=1e-8)
    check("map_basis", ortho and span_ok, f"ortho={ortho} span={span_ok}")

    # 2. planted alignment: W_Q amplifies span{p1,p2}; QUANT/DET centroids on p1/p2
    p1 = rng.standard_normal(d)
    p1 /= np.linalg.norm(p1)
    p2 = rng.standard_normal(d)
    p2 -= (p2 @ p1) * p1
    p2 /= np.linalg.norm(p2)
    wq = rng.standard_normal((hq * dh, d)) / np.sqrt(d)
    for h in range(hq):
        u1 = rng.standard_normal(dh)
        u1 /= np.linalg.norm(u1)
        u2 = rng.standard_normal(dh)
        u2 /= np.linalg.norm(u2)
        wq[h * dh:(h + 1) * dh] += 1.5 * (np.outer(u1, p1) + np.outer(u2, p2))
    wk = rng.standard_normal((hk * dh, d)) / np.sqrt(d)

    means = {}
    for t in TYPE_ORDER:
        v = rng.standard_normal(d)
        v -= (v @ p1) * p1 + (v @ p2) * p2
        means[t] = 3.0 * v / np.linalg.norm(v)
    means["QUANT"], means["DET"] = 3.0 * p1, 3.0 * p2
    means["ENTITY"] = np.zeros(d)
    x = np.concatenate([means[t] + rng.standard_normal((n_per, d))
                        for t in TYPE_ORDER])
    y = np.array([t for t in TYPE_ORDER for _ in range(n_per)])

    geo = layer_geometry(x, y, rng, 50)
    res = process_layer(wq, wk, dh, np.ones(d), geo, y, rng, 200)
    agg = band_aggregate({0: res})

    null_q = agg["rolenull"]["q"]
    check("null_calibration", 0.5 < null_q["null_mean"] < 1.6,
          f"rolenull null_mean={null_q['null_mean']} (expect ~1)")
    bq = agg["bind"]["q"]
    check("planted_bind", bq["p"] < 0.05 and bq["rho"] > 2.0,
          f"rho={bq['rho']} p={bq['p']}")
    cq = agg["comp"]["q"]
    check("unplanted_comp", cq["p"] > 0.05, f"rho={cq['rho']} p={cq['p']}")
    asym = agg["bind"]["asym"]
    check("side_asymmetry", asym["a"] > 0 and asym["p_pos"] < 0.05,
          f"A={asym['a']} p_pos={asym['p_pos']}")
    v = verdict_block(agg)
    check("verdict_plumbing", v["p_bind_q"] == bq["p"], f"verdict={v}")

    print(f"[qk][validate] {'ALL PASS' if not fails else f'FAILURES: {fails}'}",
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


def attn_weights(layer) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sa = layer.self_attn
    wq = sa.q_proj.weight.detach().float().cpu().numpy()
    wk = sa.k_proj.weight.detach().float().cpu().numpy()
    gamma = layer.input_layernorm.weight.detach().float().cpu().numpy()
    return wq, wk, gamma


def main() -> None:
    ap = argparse.ArgumentParser(description="P-TYPE-QK QK-bilinear lattice alignment")
    ap.add_argument("--model", default="Qwen/Qwen3-32B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--layer-stride", type=int, default=1,
                    help="capture stride (verdict host MUST be 1; smoke may use 2)")
    ap.add_argument("--n-null", type=int, default=200,
                    help="shuffled-label pipelines per band layer")
    ap.add_argument("--n-null-profile", type=int, default=50,
                    help="null pipelines per out-of-band layer (P3, verbatim-only)")
    ap.add_argument("--n-null-geom", type=int, default=200,
                    help="shuffled-label PR nulls for band detection (1b procedure)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--output", default=None)
    ap.add_argument("--validate", action="store_true",
                    help="no-model synthetic validation of the measurement core")
    args = ap.parse_args()

    if args.validate:
        sys.exit(validate())

    rng = np.random.default_rng(args.seed)
    model, tok, config = load_model(args.model, device=args.device)
    n_layers = config.num_hidden_layers
    head_dim = getattr(config, "head_dim", None) or (
        config.hidden_size // config.num_attention_heads)
    cap_layers = [-1, *range(0, n_layers, args.layer_stride)]
    if (n_layers - 1) not in cap_layers:
        cap_layers.append(n_layers - 1)

    data, n_lab, n_skip = build_probing_dataset(
        model, tok, cap_layers, LABELED_DATA, verbose=True)
    print(f"[qk] labeled={n_lab} skipped={n_skip} layers={len(data)}",
          file=sys.stderr)
    tlayers = get_transformer_layers(model)

    # geometry + band (1b v4 procedure verbatim; band on decoder-layer residuals)
    geos: dict[int, dict] = {}
    for L in sorted(data):
        x, y = data[L]
        geos[L] = layer_geometry(x, y, rng, args.n_null_geom)
        lab = "embed" if L == -1 else f"L{L}"
        print(f"[qk] geom {lab:6s} PR={geos[L]['pr_real']:.2f} "
              f"p={geos[L]['p_lowrank']}", file=sys.stderr)
    band = find_band({L: geos[L] for L in geos if L >= 0}, n_layers)
    print(f"[qk] BAND (residual layers) = L{band[0]}..L{band[-1]} "
          f"({len(band)} layers)", file=sys.stderr)

    # per-layer gains: residual L feeds attention of decoder layer L+1
    rows_band: dict[int, dict] = {}
    profile: dict[str, dict] = {}
    for L in sorted(data):
        m_idx = L + 1
        if m_idx >= n_layers:
            continue
        in_band = L in band
        n_iter = args.n_null if in_band else args.n_null_profile
        wq, wk, gamma = attn_weights(tlayers[m_idx])
        x, y = data[L]
        res = process_layer(wq, wk, head_dim, gamma, geos[L], y, rng, n_iter)
        del wq, wk
        one = band_aggregate({L: res})
        profile[str(L)] = {
            "attn_layer": m_idx, "in_band": in_band, "n_null": n_iter,
            **{c: {"q": one[c]["q"], "k": one[c]["k"], "asym": one[c]["asym"]}
               for c in CONDS}}
        if in_band:
            rows_band[L] = res
        lab = "embed" if L == -1 else f"L{L}"
        print(f"[qk] {'BAND ' if in_band else '     '}{lab:6s}->attn L{m_idx:2d} "
              f"bind_q={one['bind']['q']['rho']:.3f}(p={one['bind']['q']['p']:.3f}) "
              f"comp_q={one['comp']['q']['rho']:.3f}(p={one['comp']['q']['p']:.3f}) "
              f"rolenull_q={one['rolenull']['q']['rho']:.3f}",
              file=sys.stderr)

    agg = band_aggregate(rows_band)
    verdict = verdict_block(agg)
    print(f"[qk] BAND AGGREGATE: "
          f"bind_q rho={agg['bind']['q']['rho']} p={agg['bind']['q']['p']} | "
          f"comp_q rho={agg['comp']['q']['rho']} p={agg['comp']['q']['p']} | "
          f"rolenull_q rho={agg['rolenull']['q']['rho']} "
          f"p={agg['rolenull']['q']['p']}", file=sys.stderr)
    print(f"[qk] ASYM (q-k): bind={agg['bind']['asym']['a']} "
          f"comp={agg['comp']['asym']['a']} entity={agg['entity']['asym']['a']}",
          file=sys.stderr)
    print(f"[qk] VERDICT (advisory until pre-reg frozen): {verdict}",
          file=sys.stderr)

    slug = args.model.split("/")[-1].lower().replace(".", "-")
    out = (Path(args.output) if args.output
           else _ROOT / "results" / "type-qk" / slug)
    out.mkdir(parents=True, exist_ok=True)
    res = {
        "experiment": "P-TYPE-QK",
        "prereg": ("mementum/knowledge/explore/"
                   "type-check-is-the-qk-bilinear.md#p-type-qk"),
        "model": args.model, "device": args.device,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(),
        "seed": args.seed, "layer_stride": args.layer_stride,
        "n_null": args.n_null, "n_null_profile": args.n_null_profile,
        "n_null_geom": args.n_null_geom,
        "n_layers": n_layers, "head_dim": head_dim,
        "n_heads_q": config.num_attention_heads,
        "n_heads_kv": getattr(config, "num_key_value_heads",
                              config.num_attention_heads),
        "n_labeled": n_lab, "type_order": TYPE_ORDER,
        "conds": {c: COND_TYPES[c] for c in CONDS},
        "band_residual_layers": [int(L) for L in band],
        "band_aggregate": agg,
        "verdict": verdict,
        "per_layer": profile,
        "geometry": {str(L): {"pr_real": round(geos[L]["pr_real"], 3),
                              "p_lowrank": geos[L]["p_lowrank"]}
                     for L in sorted(geos)},
    }
    (out / "qk_alignment.json").write_text(json.dumps(res, indent=2))
    print(f"[qk] wrote {out}/qk_alignment.json", file=sys.stderr)


if __name__ == "__main__":
    main()
