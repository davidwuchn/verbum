"""FFN-function bake — STAGE 0: the operand-insertion MAP (M1 / M3).

Pre-flight READ for the operand-`INSERT` (ffn-function-bake-prereg.md, database reframe
s276). We cannot `INSERT` a join (a combinator is structural — s276); the surviving door
is `INSERT` a novel OPERAND ROW that the resident join composes. Before writing, we need
the reconnaissance an insert requires:

  M1  which layer carries the operand's row?   (value register)
  M3  is the operand row SEPARABLE / addressable, or superposed like the join?

Method (pure read; nothing baked; resident Qwen3-0.6B through the s275 llama.cpp tap):
  - Operand-swap families: fixed C-applicative structure ("<subj> <verb> a <OBJ>") with
    the OBJECT (the operand the resident C-join composes, s248-252) swapped across a
    vocabulary; surrounding structure (subj/verb) varied as NUISANCE across contexts.
    Label = operand identity.
  - Tap l_out (VALUE register; the row is a value claim, s206 scar) and read the LAST
    token (the join readout; the operand's OWN position decodes it trivially and is
    uninformative -- we want where the JOIN delivered it, cf. s248 C-field late read).
  - Per layer, decode operand identity with a PCA-50 + logistic pipeline (s250 cont.2
    overfit control). Two accuracies:
       within -- StratifiedKFold (decodable at all?)
       LOCO   -- leave-one-CONTEXT-out (context-invariant = a real operand ROW, not a
                 memorized sentence). LOCO is the load-bearing M3 number.
  - Nulls beside every number (s206/s247): shuffled-label (permutation floor, same
    features) + random-feature (Gaussian same shape = the d-overfitting floor).

VERDICT (M3): LOCO acc >> max(shuffled, random-feature, majority) at some layer
  => operand rows are separable/addressable => there is a slot to `INSERT` into.
              LOCO ~ nulls everywhere
  => operand is superposed like the join => the bake premise weakens.

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneGroupOut, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "opcodes"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import tap_loader  # noqa: E402

# ── operand-swap families ────────────────────────────────────────────────────
# OBJECTS = the operand the resident C-applicative join composes (s248-252). Read is at
# the LAST token (join readout), so no operand-position alignment is needed here.
OBJECTS = ["dog", "bird", "fish", "horse", "mouse", "snake",
           "wolf", "sheep", "duck", "bear", "goat", "frog"]

# CONTEXTS = fixed applicative structure, subj/verb varied as NUISANCE. The operand
# ("a <OBJ>.") sits at the end so the last-token readout has consumed it. LOCO across
# these contexts is what makes the decoded signal an operand ROW, not a sentence.
CONTEXTS = [
    "Every cat fears a {obj}.",
    "The farmer saw a {obj}.",
    "She quickly found a {obj}.",
    "They will chase a {obj}.",
    "A child drew a {obj}.",
    "He always wanted a {obj}.",
    "We carefully watched a {obj}.",
    "The hunter tracked a {obj}.",
]


def build_probes() -> list[dict]:
    probes = []
    for ci, ctx in enumerate(CONTEXTS):
        for obj in OBJECTS:
            probes.append({"text": ctx.format(obj=obj), "operand": obj, "ctx": ci})
    return probes


def run_tap(tap_bin: Path, gguf: str, prompts: list[str], out_dir: Path, ngl: int) -> None:
    pf = out_dir / "prompts.txt"
    pf.write_text("\n".join(p.replace("\n", " ") for p in prompts) + "\n")
    subprocess.run(
        [str(tap_bin), "--model", gguf, "--prompts-file", str(pf),
         "--out", str(out_dir), "-ngl", str(ngl)], check=True)


def _cv_acc(X: np.ndarray, y: np.ndarray, groups: np.ndarray, mode: str,
            rng: np.random.Generator, shuffle: bool = False,
            randfeat: bool = False) -> float:
    """Mean CV accuracy for a PCA-50 + logistic pipeline. mode: 'within'|'loco'."""
    yy = rng.permutation(y) if shuffle else y
    XX = rng.standard_normal(X.shape) if randfeat else X
    n_comp = min(50, XX.shape[0] - 1, XX.shape[1])
    accs = []
    if mode == "within":
        skf = StratifiedKFold(n_splits=4, shuffle=True, random_state=0)
        splitter = skf.split(XX, yy)
    else:  # leave-one-context-out
        splitter = LeaveOneGroupOut().split(XX, yy, groups)
    for tr, te in splitter:
        # need every test class present in train for a fair readout
        pipe = make_pipeline(StandardScaler(), PCA(n_components=n_comp),
                             LogisticRegression(max_iter=2000, C=1.0))
        pipe.fit(XX[tr], yy[tr])
        accs.append(pipe.score(XX[te], yy[te]))
    return float(np.mean(accs))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gguf", required=True)
    ap.add_argument("--ngl", type=int, default=999)
    ap.add_argument("--tap-bin",
                    default=str(Path(__file__).resolve().parent / "build" / "vsm_tap"))
    ap.add_argument("--out", default="results/ffn-bake/operand-map-qwen3-0-6b")
    args = ap.parse_args()

    probes = build_probes()
    out = Path(args.out)
    tap = out / "tap"
    tap.mkdir(parents=True, exist_ok=True)
    prompts = [p["text"] for p in probes]
    if all((tap / str(i) / "manifest.json").exists() for i in range(len(prompts))):
        print(f"[operand-map] reusing dump {tap}")
    else:
        run_tap(Path(args.tap_bin), args.gguf, prompts, tap, args.ngl)

    # last-token l_out per probe -> {layer: [N, d]}
    feat = tap_loader.stack_last_token(tap, len(probes), "l_out")
    layers = sorted(feat)
    y = np.array([p["operand"] for p in probes])
    groups = np.array([p["ctx"] for p in probes])
    n_obj = len(set(y.tolist()))
    majority = max(np.bincount([sorted(set(y)).index(v) for v in y])) / len(y)
    rng = np.random.default_rng(0)

    print(f"[operand-map] {len(probes)} probes  ({n_obj} operands x "
          f"{len(CONTEXTS)} contexts)  chance={1/n_obj:.3f}  "
          f"majority={majority:.3f}  layers={len(layers)}")
    print("\n layer | within | LOCO  | shuf(LOCO) | randfeat(LOCO)")
    print("-------+--------+-------+------------+---------------")
    per_layer = []
    for li in layers:
        X = feat[li]
        within = _cv_acc(X, y, groups, "within", rng)
        loco = _cv_acc(X, y, groups, "loco", rng)
        shuf = _cv_acc(X, y, groups, "loco", rng, shuffle=True)
        rand = _cv_acc(X, y, groups, "loco", rng, randfeat=True)
        per_layer.append({"layer": li, "within": round(within, 3),
                          "loco": round(loco, 3), "loco_shuffled": round(shuf, 3),
                          "loco_randfeat": round(rand, 3)})
        print(f" {li:5d} | {within:.3f}  | {loco:.3f} | {shuf:.3f}      | {rand:.3f}")

    best = max(per_layer, key=lambda r: r["loco"])
    null_ceiling = max(best["loco_shuffled"], best["loco_randfeat"], majority)
    verdict = "SEPARABLE (operand rows addressable -> INSERT slot exists)" \
        if best["loco"] > null_ceiling + 0.10 else \
        "SUPERPOSED (operand not an addressable row -> bake premise weak)"
    print(f"\n[operand-map] M1 best LOCO layer = L{best['layer']}  "
          f"loco={best['loco']:.3f}  (nulls: shuf={best['loco_shuffled']:.3f} "
          f"randfeat={best['loco_randfeat']:.3f} majority={majority:.3f})")
    print(f"[operand-map] M3 VERDICT: {verdict}")

    result = {
        "model": args.gguf, "n_probes": len(probes), "n_operands": n_obj,
        "n_contexts": len(CONTEXTS), "chance": round(1 / n_obj, 3),
        "majority": round(majority, 3), "read": "last_token l_out (join readout)",
        "best_layer": best["layer"], "best_loco": best["loco"],
        "null_ceiling": round(null_ceiling, 3), "verdict": verdict,
        "per_layer": per_layer,
    }
    (out / "operand_map.json").write_text(json.dumps(result, indent=2))
    print(f"[operand-map] wrote {out}/operand_map.json")


if __name__ == "__main__":
    main()
