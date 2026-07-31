#!/usr/bin/env python3
"""P-TYPE-OV — is the type lattice in the joins' TRANSMISSION passband? (geometry)

Pre-reg: mementum/knowledge/explore/types-are-compiled-probabilities.md
(#p-type-ov, DRAFTED s288 — 32B verdict run only after freeze on GO).

HYPOTHESIS. The JOIN-TYPED filter (P-TYPE-SWAP: edges fixed, the OV/content
channel delivers well-typed displacement preferentially) is implemented in the
composite per-head OV map: the write-out geometry preferentially transmits the
type-lattice role subspaces within the low-rank band. The QK mirror — what the
read-in (aim) geometry does not do (P-TYPE-QK dead-on-null), the write-out
(content) geometry should. entity (the payload type) is the a-priori focus.

MEASUREMENT (no RoPE concern — V is unrotated).
  1. Capture labeled Montague-type residuals per decoder layer (probe_type
     capture verbatim). Residual L pairs with attention of decoder layer L+1.
  2. layer_geometry -> find_band (verbum.dsp; stride-aware fix #1 — smoke may
     legitimately stride).
  3. Role subspaces from std-space centroids: bind{QUANT,DET}, comp{MOD},
     rolenull{CONN,FUNC} (verbatim), entity{ENTITY}.
  4. map_basis: v_attn prop-to (v_std * sd_L) * gamma_{L+1}, QR.
  5. rho_ov(h, v) = D * ||W_O_h (W_V_kv(h) v)||^2 / ||W_O_h W_V_kv(h)||^2_F
     (rho=1 == analytic random expectation; Frobenius via tr(G_h C_kv), no DxD
     materialization). MLP read-in row (advisory): rho through concat(gate,up)
     reading post_attention_layernorm_{L+1}.

NULL. N full shuffled-label pipelines per band layer (shuffle -> centroids ->
role_subspace -> same mapping -> same gains), band-aggregated per paired
iteration; p = frac(null_agg >= real_agg).

VERDICT (advisory until frozen on GO):
  OV-TRANSMITTING    <=> entity OV band-aggregate beats null p<0.05.
  LATTICE-IN-PASSBAND <=> entity AND bind AND comp beat null.
  NOT-IN-OV          <=> all dead-on-null (fifth location null; distributed
                         implementation — pre-committed, counts fully).

First consumer of verbum.dsp (map_basis, layer_geometry, role_subspace,
find_band, head_gain_ratios) — no sys.path wrapper hacks for the measurement
core; only the model-capture helpers remain script-imported.

Usage:
    uv run python scripts/explore/type_ov_alignment.py --validate     # no model
    uv run python scripts/explore/type_ov_alignment.py \
        --model Qwen/Qwen3-4B --device mps --layer-stride 2 --n-null 50  # smoke
    uv run python scripts/explore/type_ov_alignment.py \
        --model Qwen/Qwen3-32B --device mps                       # verdict host

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

from verbum.dsp import (
    find_band,
    head_gain_ratios,
    layer_geometry,
    map_basis,
    role_subspace,
)

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "explore"))

TYPE_ORDER = ["ENTITY", "PRED", "REL", "QUANT", "DET", "MOD", "CONN", "FUNC"]
ROLES = {"bind": ["QUANT", "DET"], "comp": ["MOD"], "rolenull": ["CONN", "FUNC"]}
CONDS = ["bind", "comp", "rolenull", "entity"]
COND_TYPES = {**ROLES, "entity": ["ENTITY"]}


# ── measurement core (model-free; unit-validated by --validate) ────────────────
def centroids(x: np.ndarray, y: np.ndarray, labels: list[str]):
    """Per-label mean rows (>=2 items). Local mirror of dsp.centroids with the
    QK instrument's exact semantics (kept for null-pipeline parity)."""
    rows, present = [], []
    for lab in labels:
        m = y == lab
        if m.sum() >= 2:
            rows.append(x[m].mean(axis=0))
            present.append(lab)
    return np.array(rows), present


def ov_gain_ratios(wv: np.ndarray, wo: np.ndarray, bases: list[np.ndarray],
                   head_dim: int, n_kv: int) -> list[float]:
    """Composite OV transmission gain, one scalar per basis.

    wv: (n_kv*dh, D) value read-in. wo: (D, H*dh) output write-out.
    rho(h, v) = D * ||A_h (B_kv v)||^2 / tr(G_h C_kv), A_h = wo[:, h-slice],
    B_kv = wv[kv-slice], G_h = A_h^T A_h, C_kv = B_kv B_kv^T.
    rho = 1 == analytic random-direction expectation. Mean over Q-heads AND
    basis rows. No DxD materialization."""
    d = wv.shape[1]
    dh = head_dim
    n_heads = wo.shape[1] // dh
    group = n_heads // n_kv
    stack = np.concatenate(bases, axis=0)                      # (K, D)
    bv = (wv @ stack.T).reshape(n_kv, dh, -1)                  # (n_kv, dh, K)
    wv3 = wv.reshape(n_kv, dh, d)
    c_kv = np.einsum("kid,kjd->kij", wv3, wv3)                 # (n_kv, dh, dh)
    rho = np.zeros((n_heads, stack.shape[0]))
    for h in range(n_heads):
        a = wo[:, h * dh:(h + 1) * dh]                         # (D, dh)
        g = a.T @ a                                            # (dh, dh)
        kv = h // group
        x = bv[kv]                                             # (dh, K)
        num = np.einsum("ik,ij,jk->k", x, g, x)                # (K,)
        fro = float(np.trace(g @ c_kv[kv])) + 1e-12
        rho[h] = d * num / fro
    rho_mean = rho.mean(axis=0)
    out, i = [], 0
    for b in bases:
        k = b.shape[0]
        out.append(float(rho_mean[i:i + k].mean()))
        i += k
    return out


def cond_bases(geo_like: dict, sd: np.ndarray, gamma: np.ndarray
               ) -> list[np.ndarray]:
    """The four condition subspaces, mapped to the given read-in space."""
    bases = []
    for cnd in CONDS:
        b = role_subspace(geo_like, COND_TYPES[cnd])
        if b is None:
            raise RuntimeError(f"missing class for condition {cnd}")
        bases.append(map_basis(b, sd, gamma))
    return bases


def process_layer(wv: np.ndarray, wo: np.ndarray, w_mlp: np.ndarray | None,
                  head_dim: int, n_kv: int, gamma_attn: np.ndarray,
                  gamma_mlp: np.ndarray | None, geo: dict, y: np.ndarray,
                  rng, n_iter: int, n_iter_mlp: int) -> dict:
    """Real + shuffled-label-null OV (and advisory MLP read-in) gains for one
    (residual L, block L+1) pair. Null iterations paired across channels."""
    sd = geo["sd"]
    nc = len(CONDS)

    real_ov = cond_bases(geo, sd, gamma_attn)
    null_ov: list[np.ndarray] = []
    real_mlp = (cond_bases(geo, sd, gamma_mlp)
                if w_mlp is not None and gamma_mlp is not None else None)
    null_mlp: list[np.ndarray] = []
    for i in range(n_iter):
        yp = rng.permutation(y)
        c, present = centroids(geo["z"], yp, TYPE_ORDER)
        gl = {"present": present, "centroids": c}
        null_ov.extend(cond_bases(gl, sd, gamma_attn))
        if real_mlp is not None and i < n_iter_mlp:
            null_mlp.extend(cond_bases(gl, sd, gamma_mlp))

    r_ov = ov_gain_ratios(wv, wo, real_ov + null_ov, head_dim, n_kv)
    out = {"real": {}, "null": {}}
    for j, cnd in enumerate(CONDS):
        out["real"][cnd] = {"ov": r_ov[j]}
        out["null"][cnd] = {"ov": np.array(
            [r_ov[nc + i * nc + j] for i in range(n_iter)])}

    if real_mlp is not None:
        r_mlp = head_gain_ratios(w_mlp, real_mlp + null_mlp,
                                 head_dim=w_mlp.shape[0])   # 1 "head" = whole map
        n_kept = len(null_mlp) // nc
        for j, cnd in enumerate(CONDS):
            out["real"][cnd]["mlp"] = r_mlp[j]
            out["null"][cnd]["mlp"] = np.array(
                [r_mlp[nc + i * nc + j] for i in range(n_kept)])
    return out


def band_aggregate(rows: dict[int, dict]) -> dict:
    """Aggregate real/null over band layers, pairing null iterations."""
    agg = {}
    layers = sorted(rows)
    sides = [s for s in ("ov", "mlp") if s in rows[layers[0]]["real"][CONDS[0]]]
    for cnd in CONDS:
        agg[cnd] = {}
        for side in sides:
            real = float(np.mean([rows[L]["real"][cnd][side] for L in layers]))
            null = np.mean(np.stack(
                [rows[L]["null"][cnd][side] for L in layers]), axis=0)
            agg[cnd][side] = {
                "rho": round(real, 4),
                "null_mean": round(float(null.mean()), 4),
                "null_std": round(float(null.std()), 4),
                "p": float(np.mean(null >= real)),
            }
    return agg


def verdict_block(agg: dict) -> dict:
    """Draft pre-reg verdict (advisory until frozen on GO)."""
    p_ent = agg["entity"]["ov"]["p"]
    p_bind = agg["bind"]["ov"]["p"]
    p_comp = agg["comp"]["ov"]["p"]
    ov_transmitting = bool(p_ent < 0.05)
    lattice = bool(ov_transmitting and p_bind < 0.05 and p_comp < 0.05)
    return {"ov_transmitting": ov_transmitting,
            "lattice_in_passband": lattice,
            "p_entity_ov": p_ent, "p_bind_ov": p_bind, "p_comp_ov": p_comp,
            "note": "advisory until #p-type-ov pre-reg is frozen (Michael GO)"}


# ── validation (no model; λ assert: prove the instrument before trusting it) ──
def validate() -> int:
    rng = np.random.default_rng(11)
    d, dh, n_heads, n_kv, n_per = 64, 8, 8, 2, 40
    group = n_heads // n_kv
    fails = []

    def check(name: str, ok: bool, detail: str) -> None:
        print(f"[ov][validate] {'PASS' if ok else 'FAIL'} {name}: {detail}",
              file=sys.stderr)
        if not ok:
            fails.append(name)

    # planted transmission: composite OV amplifies p1; ENTITY centroid on p1
    p1 = rng.standard_normal(d)
    p1 /= np.linalg.norm(p1)
    wv = rng.standard_normal((n_kv * dh, d)) / np.sqrt(d)
    wo = rng.standard_normal((d, n_heads * dh)) / np.sqrt(d)
    u = {}
    for kv in range(n_kv):
        u[kv] = rng.standard_normal(dh)
        u[kv] /= np.linalg.norm(u[kv])
        wv[kv * dh:(kv + 1) * dh] += 2.0 * np.outer(u[kv], p1)
    for h in range(n_heads):
        wdir = rng.standard_normal(d)
        wdir /= np.linalg.norm(wdir)
        wo[:, h * dh:(h + 1) * dh] += 2.0 * np.outer(wdir, u[h // group])

    means = {}
    for t in TYPE_ORDER:
        v = rng.standard_normal(d)
        v -= (v @ p1) * p1
        means[t] = 3.0 * v / np.linalg.norm(v)
    means["ENTITY"] = 3.0 * p1                       # payload type ON the passband
    x = np.concatenate([means[t] + rng.standard_normal((n_per, d))
                        for t in TYPE_ORDER])
    y = np.array([t for t in TYPE_ORDER for _ in range(n_per)])

    w_mlp = rng.standard_normal((4 * d, d)) / np.sqrt(d)
    geo = layer_geometry(x, y, rng, 50, label_order=TYPE_ORDER)
    res = process_layer(wv, wo, w_mlp, dh, n_kv, np.ones(d), np.ones(d),
                        geo, y, rng, n_iter=200, n_iter_mlp=50)
    agg = band_aggregate({0: res})

    nn = agg["rolenull"]["ov"]
    check("null_calibration", 0.4 < nn["null_mean"] < 1.8,
          f"rolenull null_mean={nn['null_mean']} (expect ~1)")
    ent = agg["entity"]["ov"]
    check("planted_entity", ent["p"] < 0.05 and ent["rho"] > 2.0,
          f"rho={ent['rho']} p={ent['p']}")
    cq = agg["comp"]["ov"]
    check("unplanted_comp", cq["p"] > 0.05, f"rho={cq['rho']} p={cq['p']}")
    mlp = agg["entity"]["mlp"]
    check("mlp_row_calibrated", 0.2 < mlp["null_mean"] < 2.5 and mlp["p"] > 0.05,
          f"mlp rho={mlp['rho']} null={mlp['null_mean']} p={mlp['p']} "
          f"(unplanted MLP must not fire)")
    # linearity/normalization: isotropic wv/wo -> rho ~ 1 on any basis
    wv0 = rng.standard_normal((n_kv * dh, d))
    wo0 = rng.standard_normal((d, n_heads * dh))
    b = np.linalg.qr(rng.standard_normal((d, 2)))[0].T
    r0 = ov_gain_ratios(wv0, wo0, [b], dh, n_kv)[0]
    check("iso_calibration", 0.5 < r0 < 2.0, f"rho={r0} (expect ~1)")
    v = verdict_block(agg)
    check("verdict_plumbing", v["p_entity_ov"] == ent["p"], f"verdict={v}")

    print(f"[ov][validate] {'ALL PASS' if not fails else f'FAILURES: {fails}'}",
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


def block_weights(layer):
    sa = layer.self_attn
    wv = sa.v_proj.weight.detach().float().cpu().numpy()
    wo = sa.o_proj.weight.detach().float().cpu().numpy()
    gamma_attn = layer.input_layernorm.weight.detach().float().cpu().numpy()
    w_gate = layer.mlp.gate_proj.weight.detach().float().cpu().numpy()
    w_up = layer.mlp.up_proj.weight.detach().float().cpu().numpy()
    w_mlp = np.concatenate([w_gate, w_up], axis=0)
    gamma_mlp = layer.post_attention_layernorm.weight.detach().float().cpu().numpy()
    return wv, wo, gamma_attn, w_mlp, gamma_mlp


def main() -> None:
    ap = argparse.ArgumentParser(
        description="P-TYPE-OV composite-OV lattice transmission")
    ap.add_argument("--model", default="Qwen/Qwen3-32B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--layer-stride", type=int, default=1,
                    help="capture stride (verdict host MUST be 1; smoke may use 2)")
    ap.add_argument("--n-null", type=int, default=200,
                    help="shuffled-label pipelines per band layer (OV)")
    ap.add_argument("--n-null-mlp", type=int, default=50,
                    help="null pipelines for the advisory MLP read-in row")
    ap.add_argument("--n-null-profile", type=int, default=50,
                    help="null pipelines per out-of-band layer (verbatim row)")
    ap.add_argument("--n-null-geom", type=int, default=200,
                    help="shuffled-label PR nulls for band detection")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--output", default=None)
    ap.add_argument("--validate", action="store_true",
                    help="no-model synthetic validation of the measurement core")
    args = ap.parse_args()

    if args.validate:
        sys.exit(validate())

    from probe_type_qwen3_32b import (
        LABELED_DATA,
        build_probing_dataset,
        get_transformer_layers,
        load_model,
    )

    rng = np.random.default_rng(args.seed)
    model, tok, config = load_model(args.model, device=args.device)
    n_layers = config.num_hidden_layers
    head_dim = getattr(config, "head_dim", None) or (
        config.hidden_size // config.num_attention_heads)
    n_kv = getattr(config, "num_key_value_heads", config.num_attention_heads)
    cap_layers = [-1, *range(0, n_layers, args.layer_stride)]
    if (n_layers - 1) not in cap_layers:
        cap_layers.append(n_layers - 1)

    data, n_lab, n_skip = build_probing_dataset(
        model, tok, cap_layers, LABELED_DATA, verbose=True)
    print(f"[ov] labeled={n_lab} skipped={n_skip} layers={len(data)}",
          file=sys.stderr)
    tlayers = get_transformer_layers(model)

    geos: dict[int, dict] = {}
    for L in sorted(data):
        x, y = data[L]
        geos[L] = layer_geometry(x, y, rng, args.n_null_geom,
                                 label_order=TYPE_ORDER)
        lab = "embed" if L == -1 else f"L{L}"
        print(f"[ov] geom {lab:6s} PR={geos[L]['pr_real']:.2f} "
              f"p={geos[L]['p_lowrank']}", file=sys.stderr)
    band = find_band({L: geos[L] for L in geos if L >= 0}, n_layers)
    print(f"[ov] BAND (residual layers) = L{band[0]}..L{band[-1]} "
          f"({len(band)} probed layers)", file=sys.stderr)

    rows_band: dict[int, dict] = {}
    profile: dict[str, dict] = {}
    for L in sorted(data):
        m_idx = L + 1
        if m_idx >= n_layers:
            continue
        in_band = L in band
        n_iter = args.n_null if in_band else args.n_null_profile
        n_iter_mlp = args.n_null_mlp if in_band else 0
        wv, wo, gamma_attn, w_mlp, gamma_mlp = block_weights(tlayers[m_idx])
        if n_iter_mlp == 0:
            w_mlp, gamma_mlp = None, None
        x, y = data[L]
        res = process_layer(wv, wo, w_mlp, head_dim, n_kv, gamma_attn,
                            gamma_mlp, geos[L], y, rng, n_iter, n_iter_mlp)
        del wv, wo, w_mlp
        one = band_aggregate({L: res})
        profile[str(L)] = {
            "block_layer": m_idx, "in_band": in_band, "n_null": n_iter,
            **{c: one[c] for c in CONDS}}
        if in_band:
            rows_band[L] = res
        lab = "embed" if L == -1 else f"L{L}"
        print(f"[ov] {'BAND ' if in_band else '     '}{lab:6s}->blk L{m_idx:2d} "
              f"ent_ov={one['entity']['ov']['rho']:.3f}"
              f"(p={one['entity']['ov']['p']:.3f}) "
              f"bind_ov={one['bind']['ov']['rho']:.3f}"
              f"(p={one['bind']['ov']['p']:.3f}) "
              f"rolenull_ov={one['rolenull']['ov']['rho']:.3f}",
              file=sys.stderr)

    agg = band_aggregate(rows_band)
    verdict = verdict_block(agg)
    print(f"[ov] BAND AGGREGATE: "
          f"entity_ov rho={agg['entity']['ov']['rho']} "
          f"p={agg['entity']['ov']['p']} | "
          f"bind_ov rho={agg['bind']['ov']['rho']} p={agg['bind']['ov']['p']} | "
          f"comp_ov rho={agg['comp']['ov']['rho']} p={agg['comp']['ov']['p']} | "
          f"rolenull_ov rho={agg['rolenull']['ov']['rho']} "
          f"p={agg['rolenull']['ov']['p']}", file=sys.stderr)
    if "mlp" in agg["entity"]:
        print(f"[ov] MLP row (advisory): "
              f"entity rho={agg['entity']['mlp']['rho']} "
              f"p={agg['entity']['mlp']['p']} | "
              f"bind rho={agg['bind']['mlp']['rho']} "
              f"p={agg['bind']['mlp']['p']}", file=sys.stderr)
    print(f"[ov] VERDICT (advisory until pre-reg frozen): {verdict}",
          file=sys.stderr)

    slug = args.model.split("/")[-1].lower().replace(".", "-")
    out = (Path(args.output) if args.output
           else _ROOT / "results" / "type-ov" / slug)
    out.mkdir(parents=True, exist_ok=True)
    res = {
        "experiment": "P-TYPE-OV",
        "prereg": ("mementum/knowledge/explore/"
                   "types-are-compiled-probabilities.md#p-type-ov"),
        "model": args.model, "device": args.device,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(),
        "seed": args.seed, "layer_stride": args.layer_stride,
        "n_null": args.n_null, "n_null_mlp": args.n_null_mlp,
        "n_null_profile": args.n_null_profile,
        "n_null_geom": args.n_null_geom,
        "n_layers": n_layers, "head_dim": head_dim,
        "n_heads_q": config.num_attention_heads, "n_heads_kv": n_kv,
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
    (out / "ov_alignment.json").write_text(json.dumps(res, indent=2))
    print(f"[ov] wrote {out}/ov_alignment.json", file=sys.stderr)


if __name__ == "__main__":
    main()
