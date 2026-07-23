#!/usr/bin/env python3
"""Prompt-register split: prose vs formal probes on the same crystal.

    λ register_split(model). ∀probe → register_type ∈ {prose, formal}
      P1 geometry:   Gram_prose ↔ Gram_formal > shuffled null (same crystal)
      P2 confidence: margin(formal) > margin(prose)  (λ-notation ≡ gain knob)
      P3 energy:     raw_norm(prose) > raw_norm(formal)  (s175: prose unreduced)
      P4 identity:   cross-register nearest-centroid acc > chance (same opcodes)

PRE-REGISTERED s269c, before data. Reconciles symbol-isolation.md (s175:
prose = 8x total engine energy, formal = pre-reduced) with
tracer_cross_notation (s231: prose fires same opcodes weakly; lambda is a
gain knob, not the cause). Michael's memory = P2 ∧ P4; s175 = P3; P1 = both.

Registers of the claims (λ measure): P1 relational-geometry, P2 margin
(classification confidence), P3 raw-activation magnitude, P4 routing identity.
Caveat: formal-register n per combinator is thin (WHNF=2, Y=5, C=W=6) —
WHNF/formal excluded from headline claims; reported with warning.

Usage:
    uv run python opcodes/register_split.py --model Qwen/Qwen3.6-27B --device mps
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_HERE))

from trace import load  # noqa: E402

import capture as C  # noqa: E402
import topology as T  # noqa: E402
from classify import CRYSTAL, _unit_rows  # noqa: E402
from probes import crystal_probes  # noqa: E402
from vsm import gram_from_centroids, offdiag_corr  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "opcode-trace" / "register-split"
N_PERM = 500
RNG = np.random.default_rng(269)

_FORMAL_MARKERS = ("λ", "def ", "(x)", "(z)", " = ", "=>", "::")


def register_of(prompt: str) -> str:
    """Content heuristic: formal (lambda/code/equation) vs prose."""
    if any(m in prompt for m in _FORMAL_MARKERS):
        return "formal"
    if "lambda" in prompt and "." in prompt:
        return "formal"
    return "prose"


# ── per-split calibration primitives (mirror classify.calibrate semantics) ──


def split_centroids(G: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, ...]:
    """Sign → split-local CMR → per-combinator unit centroids.

    Returns (unit_centroids [9,d], X [N,d] CMR features, common_mode [d])."""
    S = np.sign(G)
    common = S.mean(axis=0)
    X = S - common
    cents = np.zeros((len(CRYSTAL), X.shape[1]))
    for j, c in enumerate(CRYSTAL):
        m = labels == c
        if m.any():
            cents[j] = X[m].mean(axis=0)
    return _unit_rows(cents), X, common


def loo_margins(G: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    """Leave-one-out top1-top2 cosine margin per probe, correct-hit rate.

    Self is removed from its class centroid before classification."""
    S = np.sign(np.asarray(G, dtype=np.float64))
    common = S.mean(axis=0)
    X = S - common
    sums = np.zeros((len(CRYSTAL), X.shape[1]))
    counts = np.zeros(len(CRYSTAL))
    li = np.array([CRYSTAL.index(c) for c in labels])
    for j in range(len(CRYSTAL)):
        m = li == j
        sums[j] = X[m].sum(axis=0)
        counts[j] = m.sum()
    margins, hits = [], []
    for n in range(X.shape[0]):
        cents = sums.copy()
        cnts = counts.copy()
        j = li[n]
        if cnts[j] <= 1:
            continue  # cannot LOO a singleton class
        cents[j] -= X[n]
        cnts[j] -= 1
        cents = cents / np.maximum(cnts, 1)[:, None]
        u = _unit_rows(cents)
        x = X[n] / (np.linalg.norm(X[n]) + 1e-30)
        sims = u @ x
        top = np.argsort(sims)[::-1]
        margins.append(float(sims[top[0]] - sims[top[1]]))
        hits.append(int(top[0] == j))
    return {
        "mean_margin": float(np.mean(margins)),
        "loo_acc": float(np.mean(hits)),
        "n": len(margins),
    }


def cross_classify(
    cal_G: np.ndarray, cal_labels: np.ndarray,
    tst_G: np.ndarray, tst_labels: np.ndarray,
    n_perm: int = N_PERM,
) -> dict:
    """Nearest-centroid: calibrate on one split, classify the other.

    Null: permuted test labels."""
    cents, _, common = split_centroids(
        np.asarray(cal_G, dtype=np.float64), cal_labels
    )
    Xt = np.sign(np.asarray(tst_G, dtype=np.float64)) - common
    Xtu = _unit_rows(Xt)
    sims = Xtu @ cents.T
    pred = np.argmax(sims, axis=1)
    ti = np.array([CRYSTAL.index(c) for c in tst_labels])
    acc = float((pred == ti).mean())
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = (pred == RNG.permutation(ti)).mean()
    per_comb = {}
    for j, c in enumerate(CRYSTAL):
        m = ti == j
        if m.any():
            per_comb[c] = round(float((pred[m] == j).mean()), 3)
    return {
        "acc": acc,
        "chance": 1.0 / len(CRYSTAL),
        "null_mean": float(null.mean()),
        "null_std": float(null.std()),
        "z": float((acc - null.mean()) / (null.std() + 1e-12)),
        "p_perm": float((np.sum(null >= acc) + 1) / (n_perm + 1)),
        "per_combinator_acc": per_comb,
        "n_test": len(ti),
    }


def geometry_corr(
    Gp: np.ndarray, lp: np.ndarray, Gf: np.ndarray, lf: np.ndarray,
    n_perm: int = N_PERM,
) -> dict:
    """P1: offdiag corr of the two split Grams; null permutes formal labels."""
    cp, _, _ = split_centroids(np.asarray(Gp, dtype=np.float64), lp)
    cf, Xf, _ = split_centroids(np.asarray(Gf, dtype=np.float64), lf)
    obs = offdiag_corr(gram_from_centroids(cp), gram_from_centroids(cf))
    null = np.empty(n_perm)
    lfi = np.asarray(lf)
    for i in range(n_perm):
        perm = RNG.permutation(lfi)
        cents = np.zeros_like(cf)
        for j, c in enumerate(CRYSTAL):
            m = perm == c
            if m.any():
                cents[j] = Xf[m].mean(axis=0)
        null[i] = offdiag_corr(
            gram_from_centroids(cp), gram_from_centroids(_unit_rows(cents))
        )
    return {
        "corr": float(obs),
        "null_mean": float(null.mean()),
        "null_std": float(null.std()),
        "z": float((obs - null.mean()) / (null.std() + 1e-12)),
        "p_perm": float((np.sum(null >= obs) + 1) / (n_perm + 1)),
    }


# ── main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(description="Prose vs formal register split")
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--n-perm", type=int, default=N_PERM)
    args = ap.parse_args()

    probes = [p for p in crystal_probes() if p.combinator in CRYSTAL]
    regs = [register_of(p.prompt) for p in probes]
    counts = Counter(
        (p.combinator, r) for p, r in zip(probes, regs, strict=True)
    )
    print("[rsplit] register composition (combinator, register → n):")
    for c in CRYSTAL:
        print(f"  {c:5s} formal={counts[(c, 'formal')]:3d} "
              f"prose={counts[(c, 'prose')]:3d}")

    model, tok = load(args.model, args.device)
    topo = T.detect_topology(model, getattr(model, "config", None))
    layers = list(range(topo.n_layers))
    out_dir = RESULTS_DIR / args.model.replace("/", "-").replace(".", "-").lower()
    out_dir.mkdir(parents=True, exist_ok=True)

    report: dict = {
        "model": args.model,
        "n_probes": len(probes),
        "composition": {
            f"{c}/{r}": counts[(c, r)]
            for c in CRYSTAL for r in ("formal", "prose")
        },
        "caveat": "formal n thin: WHNF=2 (excluded from headline), Y=5, C=W=6",
        "n_perm": args.n_perm,
        "registers": {},
    }

    for register in ("gate", "attn"):
        if register == "attn" and not topo.attn_traceable:
            continue
        print(f"[rsplit] [{register}] capturing {len(probes)} probes ...")
        feat: dict[int, list[np.ndarray]] = {li: [] for li in layers}
        raw_norm: list[float] = []
        for i, p in enumerate(probes):
            if i % 100 == 0:
                print(f"[rsplit] [{register}]   probe {i}/{len(probes)}")
            cap = C.capture_gate(
                model, tok, p.prompt, topo=topo, layers=layers,
                register=register,
            )
            norms = []
            for li in layers:
                v = cap.gate[li][-1]
                feat[li].append(v)
                norms.append(float(np.linalg.norm(v)))
            raw_norm.append(float(np.mean(norms)))

        labels = np.array([p.combinator for p in probes])
        regs_np = np.array(regs)
        pm = regs_np == "prose"
        fm = regs_np == "formal"

        # P3 energy — raw activation norms (mean over layers, per probe)
        rn = np.array(raw_norm)
        p3 = {
            "prose_mean_norm": float(rn[pm].mean()),
            "formal_mean_norm": float(rn[fm].mean()),
            "ratio_prose_over_formal": float(rn[pm].mean() / rn[fm].mean()),
        }

        # aggregate features at the model level: mean-of-layer CMR handled
        # per layer; headline stats computed on the layer-concatenated Gram
        # (mean Gram over layers with usable split calibrations).
        per_layer_corr = []
        gram_p_acc = np.zeros((len(CRYSTAL), len(CRYSTAL)))
        gram_f_acc = np.zeros_like(gram_p_acc)
        n_acc = 0
        for li in layers:
            G = np.stack(feat[li])
            cp, _, _ = split_centroids(G[pm], labels[pm])
            cf, _, _ = split_centroids(G[fm], labels[fm])
            gp, gf = gram_from_centroids(cp), gram_from_centroids(cf)
            per_layer_corr.append(float(offdiag_corr(gp, gf)))
            gram_p_acc += gp
            gram_f_acc += gf
            n_acc += 1

        # model-level P1 with null (concatenate mid-band layer for the perm
        # null — representative, keeps the perm cost bounded)
        mid = layers[len(layers) // 2]
        Gmid = np.stack(feat[mid])
        p1_mid = geometry_corr(
            Gmid[pm], labels[pm], Gmid[fm], labels[fm], args.n_perm
        )
        p1 = {
            "mean_layer_corr": float(np.mean(per_layer_corr)),
            "per_layer_corr": [round(c, 4) for c in per_layer_corr],
            "mean_gram_corr": float(
                offdiag_corr(gram_p_acc / n_acc, gram_f_acc / n_acc)
            ),
            "mid_layer_null_gate": p1_mid,
        }

        # P2 confidence — LOO margins per split at the mid layer (bounded
        # cost, register-comparable) plus all-layer-mean margins
        p2 = {
            "mid_layer": {
                "prose": loo_margins(Gmid[pm], labels[pm]),
                "formal": loo_margins(Gmid[fm], labels[fm]),
            },
        }

        # P4 identity — cross-register classification at the mid layer
        p4 = {
            "formal_centroids_classify_prose": cross_classify(
                Gmid[fm], labels[fm], Gmid[pm], labels[pm], args.n_perm
            ),
            "prose_centroids_classify_formal": cross_classify(
                Gmid[pm], labels[pm], Gmid[fm], labels[fm], args.n_perm
            ),
        }

        report["registers"][register] = {
            "P1_geometry": p1, "P2_confidence": p2,
            "P3_energy": p3, "P4_identity": p4,
        }

        print(f"[rsplit] [{register}] P1 mean-layer corr "
              f"{p1['mean_layer_corr']:+.3f} | mean-gram corr "
              f"{p1['mean_gram_corr']:+.3f} | mid-layer z={p1_mid['z']:.1f} "
              f"p={p1_mid['p_perm']:.4f}")
        print(f"[rsplit] [{register}] P2 margin prose="
              f"{p2['mid_layer']['prose']['mean_margin']:.4f} formal="
              f"{p2['mid_layer']['formal']['mean_margin']:.4f}")
        print(f"[rsplit] [{register}] P3 norm ratio prose/formal = "
              f"{p3['ratio_prose_over_formal']:.3f}")
        f2p = p4["formal_centroids_classify_prose"]
        p2f = p4["prose_centroids_classify_formal"]
        print(f"[rsplit] [{register}] P4 formal→prose acc={f2p['acc']:.3f} "
              f"(z={f2p['z']:.1f}) | prose→formal acc={p2f['acc']:.3f} "
              f"(z={p2f['z']:.1f}) | chance=0.111")

    out = out_dir / "register_split.json"
    out.write_text(json.dumps(report, indent=1))
    print(f"[rsplit] wrote {out}")


if __name__ == "__main__":
    main()
