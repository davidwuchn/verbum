#!/usr/bin/env python3
"""Which Hessian? Reconstruction (XᵀX) vs contractivity-residual sensitivity.

Session 222 (register: functional). Design question for "superposition-aware GD"
(rung 2): when deciding which ternary signs to commit (concentrate) vs keep
superposed, is the right *interference* signal

  (a) the layer-local reconstruction Hessian XᵀX  (GPTQ/OBQ; exact-ΔL acceptance),
  (b) or the curvature of the GLOBAL contractivity residual Δx (the fp loss)?

These need not agree. The exact-ΔL acceptance optimizes (a); main:1's objective is
(b). If a row that matters for reconstruction does NOT match a row that matters
for the fixed point, then reconstruction-based concentration would actively hurt
contractivity, and rung 2 must use the contractivity curvature.

Method (no teacher needed, ablation-by-sign-flip)
-------------------------------------------------
Resume step_001000 (the contractive operator), n_outer=2, λ_fp=5.
For a sample of output rows in TD-trained attention projections:
  ΔFP(r)  = |fp_loss(flip row r) - fp_loss| ............ contractivity sensitivity
  ΔCE(r)  = |ce(flip row r) - ce| ..................... task sensitivity
From the captured layer input X (and output y):
  recon_power(r)   = g_r^2 * mean_t y[t,r]^2  ......... diagonal reconstruction weight
  interference(r)  = Σ_{r'≠r} |Sᵣ·XᵀX·Sᵣ'| (normalized)  off-diagonal entanglement
  osc_score(r)     from flip_map .................... superposition label

Verdict
-------
corr(ΔFP, recon_power|interference) HIGH  → XᵀX is a valid interference signal for
the fixed point → rung 2 can use GPTQ-style XᵀX.
corr LOW  → contractivity has its own curvature → rung 2 needs ∂²Δx/∂S²; and it
explains why reconstruction-optimal (exact-ΔL) acceptance need not help the
contractive objective.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "v15"))

import mlx.core as mx
import numpy as np

# train_td defines create_model_with_deltas
import train_td
from config import V15Config
from td_delta import (
    DeltaTernaryLinear,
    freeze_delta_architecture,
)
from ternary import (
    freeze_ternary_weights,
    pack_ternary_mlx,
    restore_ternary,
    unpack_ternary_mlx,
)


# ── rank-correlation helpers (no scipy dependency) ──────────────────────────
def _rank(a: np.ndarray) -> np.ndarray:
    order = np.argsort(a, kind="mergesort")
    r = np.empty_like(order, dtype=np.float64)
    r[order] = np.arange(len(a))
    return r


def pearson(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.size < 3 or a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def spearman(a, b):
    return pearson(_rank(np.asarray(a, float)), _rank(np.asarray(b, float)))


# ── flip-map oscillation score per output row ───────────────────────────────
def osc_scores(flip_map_path: str) -> dict[str, np.ndarray]:
    fm = np.load(flip_map_path)
    out = {}
    for k in fm.files:
        if k.endswith("/flip_count"):
            mod = k[: -len("/flip_count")]
            fc = np.asarray(fm[k])
            out[mod] = (fc >= 2).sum(axis=1).astype(np.int64)  # per output row
    return out


# ── monkeypatch DeltaTernaryLinear.__call__ to cache raw X,y on probed mods ──
_ORIG_CALL = DeltaTernaryLinear.__call__


def _capturing_call(self, x):
    y = _ORIG_CALL(self, x)
    if getattr(self, "_capture", False):
        self._cap_x = mx.stop_gradient(x)
        self._cap_y = mx.stop_gradient(y)
    return y


def flip_row(dtl: DeltaTernaryLinear, row: int):
    """Negate the sign of every position in output `row` of the delta plate."""
    d = unpack_ternary_mlx(dtl.delta_weight)  # (N, K) int
    d = np.asarray(d)
    d[row, :] = -d[row, :]
    dtl.delta_weight = pack_ternary_mlx(mx.array(d.astype(np.int8)))
    mx.eval(dtl.delta_weight)


def restore_row(dtl: DeltaTernaryLinear, packed_backup):
    dtl.delta_weight = packed_backup
    mx.eval(dtl.delta_weight)


def _label_stats(P, mask):
    def m(key):
        return float(P[key][mask].mean()) if mask.any() else None
    return {"n": int(mask.sum()), "dfp_mean": m("dfp"), "dce_mean": m("dce"),
            "interf_mean": m("interf"), "recon_mean": m("recon")}


def forward_losses(model, ids, tgts):
    _logits, _total = model(ids, tgts)
    fp = model._last_fp_loss
    ce = model._last_ce
    mx.eval(fp, ce)
    return float(fp.item()), float(ce.item())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint",
                    default="checkpoints/v15-td-outer-k2-fp5-5k/step_001000")
    ap.add_argument("--flip-map",
                    default="checkpoints/v15-td-outer-k2-fp5-5k/flip_map_step_001000.npz")
    ap.add_argument("--extracted-model-path",
                    default="checkpoints/v15-extracted/model.npz/model.npz")
    ap.add_argument("--layers", default="0,9,18")
    ap.add_argument("--projs", default="q_proj,k_proj,v_proj,out_proj")
    ap.add_argument("--rows-per-proj", type=int, default=120,
                    help="half top-oscillator, half settled")
    ap.add_argument("--seq-len", type=int, default=1024)
    ap.add_argument("--batch-size", type=int, default=2)
    ap.add_argument("--n-outer", type=int, default=2)
    ap.add_argument("--fp-lambda", type=float, default=5.0)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="results/which-hessian/which_hessian.json")
    args = ap.parse_args()

    mx.random.seed(args.seed)
    np.random.seed(args.seed)

    # ── model ───────────────────────────────────────────────────────────
    cfg = V15Config()
    cfg.seq_len = args.seq_len
    cfg.max_seq_len = args.seq_len
    cfg.batch_size = args.batch_size
    cfg.extracted_model_path = args.extracted_model_path
    cfg.__post_init__()

    model, delta_modules = train_td.create_model_with_deltas(cfg, convert_ffn=False)
    ckpt = Path(args.checkpoint)
    model.load_weights(str(ckpt / "model.npz"), strict=False)
    mx.eval(model.parameters())
    restore_ternary(model)
    freeze_ternary_weights(model)
    freeze_delta_architecture(model)
    model._n_outer_passes = args.n_outer
    model._fixed_point_lambda = args.fp_lambda
    print(f"📂 resumed {ckpt} | n_outer={args.n_outer} λ_fp={args.fp_lambda}",
          file=sys.stderr)

    DeltaTernaryLinear.__call__ = _capturing_call

    dmods = dict(delta_modules)
    layers = [int(x) for x in args.layers.split(",")]
    projs = args.projs.split(",")
    probed = []
    for li in layers:
        for pj in projs:
            path = f"shared_stride_stack.layers.{li}.{pj}"
            if path in dmods:
                probed.append(path)
    for p in probed:
        dmods[p]._capture = True
    print(f"probed {len(probed)} projections", file=sys.stderr)

    oscs = osc_scores(args.flip_map)

    # ── calibration batch ───────────────────────────────────────────────
    from data import ShardedDataLoader
    loader = ShardedDataLoader(
        data_dir=cfg.data_dir, batch_size=cfg.batch_size, seq_len=cfg.seq_len,
        shard_start=0, shard_end=cfg.n_train_shards, seed=args.seed,
    )
    ids_np, tgts_np = next(loader)
    ids, tgts = mx.array(ids_np), mx.array(tgts_np)

    # ── baseline forward (captures X, y) ────────────────────────────────
    fp0, ce0 = forward_losses(model, ids, tgts)
    print(f"baseline fp={fp0:.5f} ce={ce0:.5f}", file=sys.stderr)

    per_proj = {}
    pooled = {k: [] for k in
              ("dfp", "dce", "recon", "interf", "osc", "gamma_abs")}

    for path in probed:
        dtl = dmods[path]
        X = np.asarray(dtl._cap_x).reshape(-1, dtl.in_features)  # (T, K)
        Y = np.asarray(dtl._cap_y).reshape(-1, dtl.out_features)  # (T, N)
        gamma = np.asarray(dtl.gamma)  # (N,)
        N = dtl.out_features
        Tn = X.shape[0]
        XtX = (X.T @ X) / Tn  # (K, K)

        eff = (np.asarray(unpack_ternary_mlx(dtl.base_weight)).astype(np.int32)
               * np.asarray(unpack_ternary_mlx(dtl.delta_weight)).astype(np.int32))
        # (N, K) effective signs in {-1,0,1}

        # diagonal reconstruction weight per row
        recon_power = (gamma ** 2) * (Y ** 2).mean(axis=0)  # (N,)

        # off-diagonal interference per row: Sr · XtX · (Σ_{r'} Sr')  minus self
        SX = eff @ XtX  # (N, K)
        gram = SX @ eff.T  # (N, N) = Sr·XtX·Sr'
        diag = np.diag(gram).copy()
        np.fill_diagonal(gram, 0.0)
        interference = np.abs(gram).sum(axis=1) / (np.abs(diag) + 1e-8)  # (N,)

        osc = oscs.get(path, np.zeros(N, dtype=np.int64))

        # select rows: top-oscillator + settled (zero-flip), no overlap
        half = args.rows_per_proj // 2
        order = np.argsort(-osc)
        top = [r for r in order if osc[r] > 0][:half]
        settled_pool = np.where(osc == 0)[0]
        rng = np.random.default_rng(args.seed)
        settled = (rng.choice(settled_pool, size=min(half, settled_pool.size),
                              replace=False).tolist()
                   if settled_pool.size else [])
        rows = list(top) + list(settled)

        backup = dtl.delta_weight
        recs = []
        t0 = time.time()
        for r in rows:
            flip_row(dtl, r)
            fp, ce = forward_losses(model, ids, tgts)
            restore_row(dtl, backup)
            recs.append({
                "row": int(r),
                "dfp": abs(fp - fp0),
                "dce": abs(ce - ce0),
                "recon": float(recon_power[r]),
                "interf": float(interference[r]),
                "osc": int(osc[r]),
                "gamma_abs": float(abs(gamma[r])),
                "is_osc": bool(osc[r] > 0),
            })
            for k in pooled:
                pooled[k].append(recs[-1][k])
        dt = time.time() - t0

        def col(key, recs=recs):
            return np.array([x[key] for x in recs], float)

        per_proj[path] = {
            "n_rows": len(rows),
            "n_osc": int(sum(x["is_osc"] for x in recs)),
            "elapsed_s": dt,
            "corr": {
                "dfp_recon_spearman": spearman(col("dfp"), col("recon")),
                "dfp_interf_spearman": spearman(col("dfp"), col("interf")),
                "dfp_dce_spearman": spearman(col("dfp"), col("dce")),
                "dce_recon_spearman": spearman(col("dce"), col("recon")),
            },
            "rows": recs,
        }
        c = per_proj[path]["corr"]
        print(f"{path}: n={len(rows)} osc={per_proj[path]['n_osc']} "
              f"dFP~recon r={c['dfp_recon_spearman']:.3f} "
              f"dFP~interf r={c['dfp_interf_spearman']:.3f} "
              f"dFP~dCE r={c['dfp_dce_spearman']:.3f} ({dt:.0f}s)",
              file=sys.stderr)

    # ── pooled verdict ──────────────────────────────────────────────────
    P = {k: np.array(v, float) for k, v in pooled.items()}
    is_osc = P["osc"] > 0
    summary = {
        "config": vars(args),
        "baseline": {"fp": fp0, "ce": ce0},
        "n_total_rows": int(P["dfp"].size),
        "pooled_corr": {
            "dfp_recon_spearman": spearman(P["dfp"], P["recon"]),
            "dfp_interf_spearman": spearman(P["dfp"], P["interf"]),
            "dfp_dce_spearman": spearman(P["dfp"], P["dce"]),
            "dce_recon_spearman": spearman(P["dce"], P["recon"]),
            "dfp_recon_pearson": pearson(P["dfp"], P["recon"]),
            "dfp_dce_pearson": pearson(P["dfp"], P["dce"]),
        },
        "by_label": {
            "oscillator": _label_stats(P, is_osc),
            "settled": _label_stats(P, ~is_osc),
        },
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"summary": summary, "per_proj": per_proj}, indent=2))

    pc = summary["pooled_corr"]
    print("\n==== POOLED VERDICT ====")
    print(f"  rows={summary['n_total_rows']}")
    print(f"  ΔFP ~ recon_power   (Spearman) = {pc['dfp_recon_spearman']:.3f}")
    print(f"  ΔFP ~ interference  (Spearman) = {pc['dfp_interf_spearman']:.3f}")
    print(f"  ΔFP ~ ΔCE           (Spearman) = {pc['dfp_dce_spearman']:.3f}")
    bl = summary["by_label"]
    print(f"  ΔFP mean  osc={bl['oscillator']['dfp_mean']} "
          f"settled={bl['settled']['dfp_mean']}")
    print(f"  interf mean osc={bl['oscillator']['interf_mean']} "
          f"settled={bl['settled']['interf_mean']}")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
