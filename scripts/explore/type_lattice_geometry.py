#!/usr/bin/env python3
"""P-TYPE-1a — the type LATTICE geometry (is it low-rank + Montague-shaped?).

Follows the s282 register triangulation (state s282): type is a DECODABLE
value-register readout (type-probe 0.88-0.96 all layers) but NOT a causal direction
(v4 type_direction_is_causal=false). So this measures the VALUE-register GEOMETRY of
the 8 Montague type centroids and asks the P-TYPE-1a question:

  Is the type geometry LOW-RANK (few primitive axes, Montague-shaped), or full-rank
  (a generic 8-way simplex with no algebra)?

Reuses the labeled data + capture pipeline from probe_type_qwen3_32b (λ one_way).

Metrics (per layer):
  1. LOW-RANK: participation ratio (PR) of the row-centered 8xD centroid matrix's
     singular values. PR ~= effective number of type axes (max ~7 for 8 classes).
     Low PR (~2-3) => a small primitive lattice; PR ~7 => generic simplex.
  2. NULL (MANDATORY, λ yardstick, pre-committed here): shuffle the type labels K
     times, recompute centroids+PR. Real low-rank counts ONLY if PR_real is below the
     shuffled-null band (p = frac[PR_null <= PR_real]). "Looks low-rank" != "is".
  3. GRAM: cosine similarity of the 8 centered type directions (structure eyeball).
  4. ARITY LADDER (exploratory, labeled): Montague currying ENTITY(e) -> PRED(<e,t>)
     -> REL(<e,<e,t>>). If arity is a consistent axis, cos(PRED-ENTITY, REL-PRED) > 0
     and beats random type-pair offsets. A vector-arithmetic type-algebra signature.
  5. DECODABILITY sanity: confirm centroids are genuinely separated (nearest-centroid
     accuracy) so we are not reading a degenerate collapsed regime.

Crystal(B/C/S) alignment is DEFERRED (cross-space; risks forced-fit — λ measure).

Usage:
    uv run python scripts/explore/type_lattice_geometry.py --model Qwen/Qwen3-0.6B \
        --device mps --layer-stride 2                     # fast prototype
    uv run python scripts/explore/type_lattice_geometry.py --model Qwen/Qwen3-32B \
        --device mps --layer-stride 2                     # the host that matters

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "explore"))

from probe_type_qwen3_32b import (  # noqa: E402
    LABELED_DATA,
    build_probing_dataset,
    load_model,
)

TYPE_ORDER = ["ENTITY", "PRED", "REL", "QUANT", "DET", "MOD", "CONN", "FUNC"]


def standardize(x: np.ndarray) -> np.ndarray:
    """Per-dimension z-score (diagonal whitening). Removes the massive-activation /
    rogue-dimension artifact that dominates raw mid/late residual norms and collapses
    Euclidean centroid geometry (λ measure: match the space the linear probe uses)."""
    mu = x.mean(axis=0, keepdims=True)
    sd = x.std(axis=0, keepdims=True) + 1e-6
    return (x - mu) / sd


def participation_ratio(sv: np.ndarray) -> float:
    """Effective number of components from singular values (scale-free)."""
    sv = sv[sv > 1e-12]
    if sv.size == 0:
        return 0.0
    return float((sv.sum() ** 2) / (sv ** 2).sum())


def centroids(x: np.ndarray, y: np.ndarray, labels: list[str]):
    """Per-label mean rows (labels present only). Returns (C, present_labels)."""
    rows, present = [], []
    for lab in labels:
        m = y == lab
        if m.sum() >= 2:
            rows.append(x[m].mean(axis=0))
            present.append(lab)
    return np.array(rows), present


def centroid_pr(x: np.ndarray, y: np.ndarray, labels: list[str]) -> float:
    c, present = centroids(x, y, labels)
    if len(present) < 3:
        return float("nan")
    cc = c - c.mean(axis=0, keepdims=True)          # spread of the type points
    sv = np.linalg.svd(cc, compute_uv=False)
    return participation_ratio(sv)


def nearest_centroid_acc(x: np.ndarray, y: np.ndarray, labels: list[str]) -> float:
    """Leave-nothing-out nearest-centroid accuracy (separation sanity, not CV)."""
    c, present = centroids(x, y, labels)
    if len(present) < 2:
        return float("nan")
    idx = {lab: i for i, lab in enumerate(present)}
    mask = np.array([t in idx for t in y])
    xs, ys = x[mask], y[mask]
    d = np.linalg.norm(xs[:, None, :] - c[None, :, :], axis=2)
    pred = np.array(present)[d.argmin(axis=1)]
    return float((pred == ys).mean())


def arity_ladder(x: np.ndarray, y: np.ndarray, rng) -> dict:
    """Montague currying ENTITY -> PRED -> REL as a consistent offset axis."""
    c, present = centroids(x, y, ["ENTITY", "PRED", "REL"])
    if len(present) < 3:
        return {"cos": None}
    ent, pred, rel = c[0], c[1], c[2]
    o1, o2 = pred - ent, rel - pred

    def cos(a, b):
        return float(a @ b / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9))

    real = cos(o1, o2)
    # null: random pairs of type-offset directions among all present types
    call, pall = centroids(x, y, TYPE_ORDER)
    null = []
    if len(pall) >= 4:
        for _ in range(200):
            i, j, k, m = rng.choice(len(pall), size=4, replace=False)
            null.append(cos(call[j] - call[i], call[m] - call[k]))
        null = np.array(null)
        p = float(np.mean(null >= real))
    else:
        p = None
    return {"cos": round(real, 3),
            "null_mean": round(float(np.mean(null)), 3) if len(null) else None,
            "p": p}


def axis_loadings(x: np.ndarray, y: np.ndarray, labels: list[str], k: int = 3) -> dict:
    """SVD of the centered type centroids -> each TYPE's loading on the top-k axes.
    Left singular vectors U[:, i] give how each present type projects onto axis i;
    var_frac = the axis's share of centroid spread. (Which types on which axis.)"""
    c, present = centroids(x, y, labels)
    if len(present) < 3:
        return {"present": present, "axes": []}
    cc = c - c.mean(axis=0, keepdims=True)
    u, s, _ = np.linalg.svd(cc, full_matrices=False)
    tot = (s ** 2).sum() + 1e-12
    axes = []
    for i in range(min(k, len(s))):
        # sign-fix: make the largest-magnitude loading positive (SVD sign is arbitrary)
        col = u[:, i]
        col = col * (1.0 if col[np.argmax(np.abs(col))] >= 0 else -1.0)
        axes.append({"i": i, "var_frac": round(float(s[i] ** 2 / tot), 3),
                     "loadings": {t: round(float(v), 3)
                                  for t, v in zip(present, col, strict=False)}})
    return {"present": present, "axes": axes}


def gram(x: np.ndarray, y: np.ndarray) -> dict:
    c, present = centroids(x, y, TYPE_ORDER)
    if len(present) < 2:
        return {}
    cc = c - c.mean(axis=0, keepdims=True)
    n = cc / (np.linalg.norm(cc, axis=1, keepdims=True) + 1e-9)
    g = n @ n.T
    return {"labels": present,
            "cos": [[round(float(v), 2) for v in row] for row in g]}


def main() -> None:
    ap = argparse.ArgumentParser(description="P-TYPE-1a type lattice geometry")
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--layer-stride", type=int, default=2)
    ap.add_argument("--n-null", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    model, tok, config = load_model(args.model, device=args.device)
    n_layers = config.num_hidden_layers
    layers = [-1, *range(0, n_layers, args.layer_stride)]
    if (n_layers - 1) not in layers:
        layers.append(n_layers - 1)

    data, n_lab, n_skip = build_probing_dataset(
        model, tok, layers, LABELED_DATA, verbose=True)
    print(f"[lattice] labeled={n_lab} skipped={n_skip} layers={len(data)}",
          file=sys.stderr)

    del model
    import gc
    gc.collect()

    # standardize per layer (diagonal whitening) — see standardize() docstring
    data = {L: (standardize(x), y) for L, (x, y) in data.items()}

    per_layer = {}
    for L in sorted(data.keys()):
        x, y = data[L]
        pr = centroid_pr(x, y, TYPE_ORDER)
        # pre-committed shuffled-label null
        null = []
        for _ in range(args.n_null):
            yp = rng.permutation(y)
            null.append(centroid_pr(x, yp, TYPE_ORDER))
        null = np.array([v for v in null if not np.isnan(v)])
        p = float(np.mean(null <= pr)) if null.size else None
        c, present = centroids(x, y, TYPE_ORDER)
        cc = c - c.mean(axis=0, keepdims=True)
        sv = np.linalg.svd(cc, compute_uv=False)
        tot = (sv ** 2).sum() + 1e-12
        per_layer[str(L)] = {
            "pr_real": round(pr, 3),
            "pr_null_mean": round(float(null.mean()), 3) if null.size else None,
            "pr_null_std": round(float(null.std()), 3) if null.size else None,
            "p_lowrank": p,
            "n_types": len(present),
            "var_top2": round(float((sv[:2] ** 2).sum() / tot), 3),
            "var_top3": round(float((sv[:3] ** 2).sum() / tot), 3),
            "sep_acc": round(nearest_centroid_acc(x, y, TYPE_ORDER), 3),
            "arity": arity_ladder(x, y, rng),
        }
        r = per_layer[str(L)]
        lab = "embed" if L == -1 else f"L{L}"
        print(f"[lattice] {lab:6s} PR={r['pr_real']:.2f} "
              f"null={r['pr_null_mean']}±{r['pr_null_std']} p={p} "
              f"top3var={r['var_top3']} sep={r['sep_acc']} "
              f"arity_cos={r['arity']['cos']}(p={r['arity']['p']})", file=sys.stderr)

    # gram at the most-separated layer (lexical, usually)
    best_L = max(data.keys(), key=lambda k: nearest_centroid_acc(*data[k], TYPE_ORDER))
    gram_best = gram(*data[best_L])

    # 1a-follow: characterize the ~3 primitive axes INSIDE the low-rank band.
    # band layer = interior layer (mid-third) with the most-significant low-rank null.
    interior = [L for L in data if 0 <= L and n_layers * 0.15 <= L <= n_layers * 0.65]
    band_L = (min(interior, key=lambda L: per_layer[str(L)]["p_lowrank"])
              if interior else best_L)
    bx, by = data[band_L]
    gram_band = gram(bx, by)
    load_band = axis_loadings(bx, by, TYPE_ORDER, k=3)
    print(f"\n[lattice] BAND layer L{band_L} axis loadings (type -> top-3 SVD axes):",
          file=sys.stderr)
    for ax in load_band["axes"]:
        pairs = sorted(ax["loadings"].items(), key=lambda kv: -abs(kv[1]))
        top = "  ".join(f"{t}:{v:+.2f}" for t, v in pairs)
        print(f"[lattice]   axis{ax['i']} (var {ax['var_frac']:.2f}): {top}",
              file=sys.stderr)

    slug = args.model.split("/")[-1].lower().replace(".", "-")
    out = (Path(args.output) if args.output
           else _ROOT / "results" / "type-lattice" / slug)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model, "device": args.device,
           "timestamp_utc": datetime.now(UTC).isoformat(),
           "n_layers": n_layers, "n_labeled": n_lab, "n_null": args.n_null,
           "layer_stride": args.layer_stride, "type_order": TYPE_ORDER,
           "gram_best_layer": int(best_L), "gram": gram_best,
           "band_layer": int(band_L), "gram_band": gram_band,
           "axis_loadings_band": load_band,
           "per_layer": per_layer}
    (out / "lattice_geometry.json").write_text(json.dumps(res, indent=2))
    print(f"[lattice] wrote {out}/lattice_geometry.json", file=sys.stderr)


if __name__ == "__main__":
    main()
