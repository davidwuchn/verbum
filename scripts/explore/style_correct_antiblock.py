#!/usr/bin/env python3
"""Style-correct the WHNF anti-block (s285, cold-start step b).

The expanded 24-state sweep (opcodes/expanded_gram.py) wrote per-gated-layer
unit-centroid stacks to results/expanded-gram/{slug}/centroids.npz. The RAW
whnf:X x whnf:X cosine block is style-blob dominated: the fire_formal:X states
(same formal programs, truncated BEFORE the halt step -- the built-in style
confound, whnf_probes.py) project ~0.95-0.97 onto a single shared direction,
so every whnf:X row inherits that "formal-lambda-style" component and the block
reads ~+0.7-0.8 off-diagonal regardless of opcode.

This script removes that style subspace (rank-1 primary; the fire_formal block
is empirically rank-1, so rank>=2 barely moves the result -- reported) from the
crystal rows (K..W), the WHNF pole, and the whnf:X rows, PER GATED LAYER, then
renormalizes and recomputes the anti-block geometry, aggregated (mean) over
gated layers.

lambda measure / lambda yardstick discipline: projecting out any shared
high-variance direction can MANUFACTURE anti-correlation among the residuals.
Every corrected statistic is therefore reported (a) beside its RAW value and
(b) against a RANDOM-DIRECTION-REMOVAL NULL (n_null random unit directions drawn
in the centroid span, same rank, same renorm) -- a corrected number "counts"
only if it departs from what removing an arbitrary direction already produces.

Outputs (per model): results/expanded-gram/{slug}/style_corrected.json
Cross-model summary:  results/expanded-gram/antiblock_style_summary.json

No model load. Pure numpy over the persisted centroids. License: MIT.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[2]
_XG = _ROOT / "results" / "expanded-gram"

OPS = ["K", "I", "B", "C", "S", "D", "W"]
CRY_IDX = list(range(7))              # crystal K..W  (basis rows 0..6)
WHNF_POLE = 8                         # generic WHNF pole
WHNF_IDX = list(range(9, 16))         # whnf:K..whnf:W
DIVY = 16                             # div:Y (divergence, NOT halt)
FF_IDX = list(range(17, 24))          # fire_formal:K..W (style confound)
IU = np.triu_indices(7, k=1)


def _unit(x: np.ndarray) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-9)


def _proj_out(rows: np.ndarray, basis: np.ndarray) -> np.ndarray:
    """Remove the row-space of `basis` (orthonormal, [r,d]) from `rows`."""
    if basis.shape[0] == 0:
        return rows
    return rows - (rows @ basis.T) @ basis


def _style_basis(ff_rows: np.ndarray, rank: int) -> tuple[np.ndarray, float]:
    """Top-`rank` right singular vectors of the fire_formal rows + the
    fraction of fire_formal energy they capture."""
    # do NOT mean-center: the shared style blob IS the common (mean) component
    _, s, vt = np.linalg.svd(ff_rows, full_matrices=False)
    energy = float((s[:rank] ** 2).sum() / (s ** 2).sum())
    return vt[:rank], energy


def _block_stats(C: np.ndarray, rank: int, n_null: int, seed: int) -> dict:
    """C: [L,24,d] float centroids. Returns raw + style-corrected + null."""
    L, _, d = C.shape
    rng = np.random.default_rng(seed)

    raw_blk = np.zeros((7, 7))
    cor_blk = np.zeros((7, 7))
    raw_cry = np.zeros((7, 7))        # crystal X x X block
    cor_cry = np.zeros((7, 7))
    raw_cross = np.zeros((7, 7))      # crystal X x whnf:Y cross-block
    cor_cross = np.zeros((7, 7))
    raw_abs = np.zeros(7)             # cos(X, whnf:X)
    cor_abs = np.zeros(7)
    raw_pole = np.zeros(7)            # cos(WHNF_pole, whnf:X)
    cor_pole = np.zeros(7)
    raw_divy = np.zeros(7)            # cos(div:Y, whnf:X)
    cor_divy = np.zeros(7)
    ff_energy = 0.0

    null_blk_off = np.zeros(n_null)   # mean off-diag under random-dir removal
    null_abs = np.zeros(n_null)       # mean cos(X,whnf:X) under random removal

    for li in range(L):
        Xn = _unit(C[li].astype(np.float32))
        cry = Xn[CRY_IDX]
        whnf = Xn[WHNF_IDX]
        pole = Xn[WHNF_POLE]
        divy = Xn[DIVY]
        ff = Xn[FF_IDX]

        # ---- raw ----
        raw_blk += whnf @ whnf.T
        raw_cry += cry @ cry.T
        raw_cross += cry @ whnf.T
        raw_abs += np.sum(cry * whnf, axis=1)
        raw_pole += whnf @ pole
        raw_divy += whnf @ divy

        # ---- style-corrected ----
        S, e = _style_basis(ff, rank)
        ff_energy += e
        cry_c = _unit(_proj_out(cry, S))
        whnf_c = _unit(_proj_out(whnf, S))
        pole_c = _unit(_proj_out(pole[None], S))[0]
        divy_c = _unit(_proj_out(divy[None], S))[0]
        cor_blk += whnf_c @ whnf_c.T
        cor_cry += cry_c @ cry_c.T
        cor_cross += cry_c @ whnf_c.T
        cor_abs += np.sum(cry_c * whnf_c, axis=1)
        cor_pole += whnf_c @ pole_c
        cor_divy += whnf_c @ divy_c

        # ---- null: remove a random rank-`rank` direction drawn in the
        #      centroid span (fair: same subspace the data lives in) ----
        span = Xn                      # [24,d]; its row-space = centroid span
        for k in range(n_null):
            coef = rng.standard_normal((rank, span.shape[0]))
            R = coef @ span            # [rank,d] random dir in the span
            # orthonormalize
            q, _ = np.linalg.qr(R.T)
            Rn = q.T[:rank]
            whnf_n = _unit(_proj_out(whnf, Rn))
            cry_n = _unit(_proj_out(cry, Rn))
            null_blk_off[k] += (whnf_n @ whnf_n.T)[IU].mean()
            null_abs[k] += np.sum(cry_n * whnf_n, axis=1).mean()

    inv = 1.0 / L
    for arr in (raw_blk, cor_blk, raw_cry, cor_cry, raw_cross, cor_cross,
                raw_abs, cor_abs, raw_pole, cor_pole,
                raw_divy, cor_divy, null_blk_off, null_abs):
        arr *= inv
    ff_energy *= inv

    def z(observed, null):
        mu, sd = float(null.mean()), float(null.std() + 1e-12)
        return (observed - mu) / sd, mu, sd

    cor_off = float(cor_blk[IU].mean())
    cor_abs_mean = float(cor_abs.mean())
    z_off, mu_off, sd_off = z(cor_off, null_blk_off)
    z_abs, mu_abs, sd_abs = z(cor_abs_mean, null_abs)

    return {
        "n_gated_layers": L,
        "d_model": d,
        "style_rank": rank,
        "ff_energy_captured": round(ff_energy, 4),
        "ops": OPS,
        "raw": {
            "whnf_block_offdiag_mean": round(float(raw_blk[IU].mean()), 4),
            "whnf_block": [[round(float(v), 4) for v in r] for r in raw_blk],
            "crystal_block": [[round(float(v), 4) for v in r] for r in raw_cry],
            "cross_block": [[round(float(v), 4) for v in r] for r in raw_cross],
            "per_op_absorption_cos": [round(float(v), 4) for v in raw_abs],
            "per_op_absorption_mean": round(float(raw_abs.mean()), 4),
            "pole_to_whnfX_cos": [round(float(v), 4) for v in raw_pole],
            "divY_to_whnfX_cos": [round(float(v), 4) for v in raw_divy],
        },
        "corrected": {
            "whnf_block_offdiag_mean": round(cor_off, 4),
            "whnf_block": [[round(float(v), 4) for v in r] for r in cor_blk],
            "crystal_block": [[round(float(v), 4) for v in r] for r in cor_cry],
            "cross_block": [[round(float(v), 4) for v in r] for r in cor_cross],
            "per_op_absorption_cos": [round(float(v), 4) for v in cor_abs],
            "per_op_absorption_mean": round(cor_abs_mean, 4),
            "pole_to_whnfX_cos": [round(float(v), 4) for v in cor_pole],
            "divY_to_whnfX_cos": [round(float(v), 4) for v in cor_divy],
        },
        "null_random_dir_removal": {
            "n_null": n_null,
            "whnf_block_offdiag": {"mean": round(mu_off, 4),
                                   "sd": round(sd_off, 4),
                                   "corrected_z": round(z_off, 3)},
            "per_op_absorption": {"mean": round(mu_abs, 4),
                                  "sd": round(sd_abs, 4),
                                  "corrected_z": round(z_abs, 3)},
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="style-correct the WHNF anti-block")
    ap.add_argument("--models", nargs="*", default=None,
                    help="slugs; default = all dirs with centroids.npz")
    ap.add_argument("--rank", type=int, default=1)
    ap.add_argument("--n-null", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    slugs = args.models or sorted(
        p.parent.name for p in _XG.glob("*/centroids.npz"))
    summary = {}
    for slug in slugs:
        npz = _XG / slug / "centroids.npz"
        if not npz.exists():
            print(f"[style] {slug}: no centroids.npz, skip")
            continue
        C = np.load(npz)["centroids"].astype(np.float32)
        r = _block_stats(C, args.rank, args.n_null, args.seed)
        out = _XG / slug / "style_corrected.json"
        payload = {"model_slug": slug,
                   "timestamp_utc": datetime.now(UTC).isoformat(),
                   "source": str(npz.relative_to(_ROOT)), **r}
        out.write_text(json.dumps(payload, indent=1))
        summary[slug] = {
            "n_gated": r["n_gated_layers"],
            "ff_energy_rank1": r["ff_energy_captured"],
            "raw_block_off": r["raw"]["whnf_block_offdiag_mean"],
            "cor_block_off": r["corrected"]["whnf_block_offdiag_mean"],
            "null_block_off_mean": r["null_random_dir_removal"]
                                    ["whnf_block_offdiag"]["mean"],
            "cor_block_z": r["null_random_dir_removal"]
                            ["whnf_block_offdiag"]["corrected_z"],
            "raw_abs_mean": r["raw"]["per_op_absorption_mean"],
            "cor_abs_mean": r["corrected"]["per_op_absorption_mean"],
            "cor_abs_z": r["null_random_dir_removal"]
                          ["per_op_absorption"]["corrected_z"],
        }
        print(f"[style] {slug}: raw_off {summary[slug]['raw_block_off']:.3f} "
              f"-> cor {summary[slug]['cor_block_off']:.3f} "
              f"(null {summary[slug]['null_block_off_mean']:.3f}, "
              f"z {summary[slug]['cor_block_z']:+.2f}) | "
              f"abs raw {summary[slug]['raw_abs_mean']:+.3f} -> "
              f"cor {summary[slug]['cor_abs_mean']:+.3f} "
              f"(z {summary[slug]['cor_abs_z']:+.2f}) | "
              f"ff_e {summary[slug]['ff_energy_rank1']:.3f}")

    (_XG / "antiblock_style_summary.json").write_text(json.dumps(
        {"timestamp_utc": datetime.now(UTC).isoformat(),
         "rank": args.rank, "n_null": args.n_null, "seed": args.seed,
         "summary": summary}, indent=1))
    print(f"[style] wrote {_XG / 'antiblock_style_summary.json'}")


if __name__ == "__main__":
    main()
