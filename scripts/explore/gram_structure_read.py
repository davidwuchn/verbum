#!/usr/bin/env python3
"""Structural read of the committed 9x9 route Grams (s343, Michael's hypothesis).

ZERO model load, deterministic re-analysis of results/combinator-relationship-map/
*.npz (10 models x 11 fractional-depth layers, 9x9 cosine Grams in CRYSTAL order
[K,I,B,C,S,D,W,Y,WHNF]). Tests Michael's structural reading of the gram:
  (1) "4 opcodes (KIBC)"                          -> effective rank + KIBC block
  (2) "S,D,W,Y = a WHNF geometry for each opcode" -> RED cohesion + OPxRED pairing
  (3) "a final WHNF that flips transform->output  -> WHNF distinctness + OP-block
       in the highest layers"                        coherence vs depth (per model)
  (4) where is the MODEL-SPECIFIC residual?       -> cross-model agreement vs depth

FINDINGS (s343): (1) HALF - KIBC is a genuine separated block but the geometry is
DIFFUSE (PR~6.2/9, top-4 only 66% energy), not a crisp rank-4. (2) NOT SUPPORTED -
S,D,W,Y barely cohere and are neutral to WHNF, no 1:1 opcode->reduced-form pairing.
(3) STRONGLY CONFIRMED 10/10 models - at the top layers the KIBC opcodes converge
(block coherence ~0 -> +0.15) AND WHNF merges in (separation 0.85 -> 0.75): the
transform->output flip. (4) The stage-flip is the MOST UNIVERSAL part (cross-model
agreement highest at the top, 0.955); the model-specific residual does NOT localize
there, has no family structure (arm A), is small -> idiosyncratic noise, nothing
nameable. NET: the gram is two universal INTENSIONAL things - which opcode (KIBC
block) + which stage (transform->output flip); even its dynamic part is content-
free (says "resolving", never WHICH result) -> coheres the co-extensional LEXICAL
capstone (extension is tape-resident).

License: MIT.
"""

from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np

CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
OP = [0, 1, 2, 3]      # K I B C
RED = [4, 5, 6, 7]     # S D W Y
WH = 8                 # WHNF
GRAM_DIR = "results/combinator-relationship-map"
OUT = Path("results/gram_structure_s343")


def load_grams() -> tuple[list[str], np.ndarray]:
    fs = sorted(p for p in glob.glob(f"{GRAM_DIR}/*.npz") if "v15" not in Path(p).name)
    grams, names = [], []
    for f in fs:
        d = np.load(f)
        ks = sorted(k for k in d.files if k.startswith("gram_route_cmr_L"))
        grams.append(np.stack([d[k].astype(float) for k in ks]))
        names.append(Path(f).stem)
    ell = min(g.shape[0] for g in grams)
    return names, np.stack([g[:ell] for g in grams])  # (M, L, 9, 9)


def pr(g: np.ndarray) -> float:
    w = np.clip(np.linalg.eigvalsh((g + g.T) / 2), 0, None)
    return float((w.sum() ** 2) / (np.sum(w ** 2) + 1e-30))


def opcoh(g: np.ndarray) -> float:
    return float(np.mean([g[i, j] for i in OP for j in OP if i != j]))


def whsep(g: np.ndarray) -> float:
    return float(1 - np.mean([abs(g[WH, j]) for j in range(9) if j != WH]))


def main() -> int:
    names, allg = load_grams()
    m, ell = allg.shape[0], allg.shape[1]
    cons = allg.mean(axis=(0, 1))
    cc = cons - cons.mean()
    w = np.sort(np.linalg.eigvalsh((cons + cons.T) / 2))[::-1]

    def blk(a, b):
        return float(np.mean([cc[i, j] for i in a for j in b if i != j]))

    mid = round(0.3 * (ell - 1))
    stageflip = {n: {"opcoh_mid": opcoh(allg[i, mid]), "opcoh_top": opcoh(allg[i, -1]),
                     "whsep_mid": whsep(allg[i, mid]), "whsep_top": whsep(allg[i, -1])}
                 for i, n in enumerate(names)}
    n_up = sum(v["opcoh_top"] > v["opcoh_mid"] for v in stageflip.values())
    n_wh = sum(v["whsep_top"] < v["whsep_mid"] for v in stageflip.values())

    eye = np.eye(m, dtype=bool)
    agree = []
    for li in range(ell):
        fl = np.array([allg[i, li].flatten() - allg[i, li].mean() for i in range(m)])
        fl = fl / (np.linalg.norm(fl, axis=1, keepdims=True) + 1e-30)
        agree.append(float((fl @ fl.T)[~eye].mean()))

    summary = {
        "n_models": m, "n_layers": ell, "crystal_order": CRYSTAL,
        "rank": {"pr_raw_mean": float(np.mean([[pr(allg[i, li]) for li in range(ell)]
                                               for i in range(m)])),
                 "consensus_eigenvalues": [round(float(x), 4) for x in w],
                 "top4_energy_frac": round(float(w[:4].sum() / w.sum()), 3),
                 "top5_energy_frac": round(float(w[:5].sum() / w.sum()), 3)},
        "blocks_meancentered": {
            "within_OP_KIBC": round(blk(OP, OP), 3),
            "within_RED_SDWY": round(blk(RED, RED), 3),
            "OP_x_RED": round(blk(OP, RED), 3),
            "OP_x_WHNF": round(float(np.mean([cc[i, WH] for i in OP])), 3),
            "RED_x_WHNF": round(float(np.mean([cc[i, WH] for i in RED])), 3)},
        "op_x_red_pairing": {CRYSTAL[OP[i]]:
                             {CRYSTAL[RED[j]]: round(float(cons[OP[i], RED[j]]), 3)
                              for j in range(4)} for i in range(4)},
        "stageflip": {"opcoh_rises_top_over_mid": f"{n_up}/{m}",
                      "whnf_sep_falls_top": f"{n_wh}/{m}",
                      "per_model": {k: {kk: round(vv, 3) for kk, vv in v.items()}
                                    for k, v in stageflip.items()}},
        "cross_model_agreement_by_depth": [round(a, 3) for a in agree],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))

    rk = summary["rank"]
    print(f"{m} models x {ell} layers, CRYSTAL order {CRYSTAL}")
    print(f"[1] RANK diffuse: PR {rk['pr_raw_mean']:.2f}/9  "
          f"top4 {rk['top4_energy_frac']:.2f} / top5 {rk['top5_energy_frac']:.2f}  "
          f"eig {rk['consensus_eigenvalues']}")
    print(f"[2] BLOCKS {summary['blocks_meancentered']}")
    print(f"[3] STAGE-FLIP opcoh rises {n_up}/{m}, WHNF_sep falls {n_wh}/{m}")
    print(f"[4] cross-model agreement by depth "
          f"{summary['cross_model_agreement_by_depth']}")
    print(f"wrote {OUT}/summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
