"""Confident-flip comparison across the Bonsai ladder.

Question: does the optimizer edit signs of CONFIDENT weights
(|w| > absmean of parent group => ternary-RTN codes them ±1), and does
the zero state matter for that?  Compares, per tensor:

  tern_rev|conf  — P(full sign reversal in ternary child | confident)
  1bit_flip|conf — P(sign flip in 1-bit child | confident)

s268 result: both < 0.4% — the confident topology is essentially
immutable at every bitwidth.  The rungs differ in the UNCERTAIN
population: ternary parks it at 0 (abstention register), binary forces
it to declare signs (10-13% churn, boundary-hugging, noise in the
routing register).
"""

from __future__ import annotations

import argparse
import glob
import json
import time
from pathlib import Path

import torch

import sys
sys.path.insert(0, str(Path(__file__).parent))
from bonsai_forensics import DEVICE, GROUP, PARENT_GLOB, build_index, load_tensor

TERN_DIR = Path("/Users/mwhitford/localai/models/bonsai27b-unpacked")
ONEBIT_GLOB = ("/Users/mwhitford/.cache/huggingface/hub/"
               "models--prism-ml--Bonsai-27B-unpacked/snapshots/*/")

DEFAULT_TENSORS = [
    "model.language_model.layers.3.self_attn.q_proj.weight",
    "model.language_model.layers.3.mlp.down_proj.weight",
    "model.language_model.layers.19.self_attn.o_proj.weight",
    "model.language_model.layers.19.mlp.gate_proj.weight",
    "model.language_model.layers.32.mlp.down_proj.weight",
    "model.language_model.layers.32.mlp.gate_proj.weight",
    "model.language_model.layers.44.mlp.down_proj.weight",
    "model.language_model.layers.57.mlp.down_proj.weight",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tensors", nargs="+", default=DEFAULT_TENSORS)
    ap.add_argument("--out", default="results/bonsai-forensics/confident_flips.json")
    args = ap.parse_args()

    pi = build_index(Path(glob.glob(PARENT_GLOB)[0]))
    ti = build_index(TERN_DIR)
    bi = build_index(Path(glob.glob(ONEBIT_GLOB)[0]))

    results = {}
    hdr = f"{'tensor':52s} {'conf_frac':>9s} {'tern_rev|conf':>13s} {'1bit_flip|conf':>14s} {'ratio':>7s}"
    print(hdr)
    for n in args.tensors:
        if n not in ti or n not in bi:
            print(f"SKIP {n}")
            continue
        t0 = time.time()
        w = load_tensor(pi, n).to(DEVICE, torch.float32)
        o, i = w.shape
        wg = w.reshape(o, i // GROUP, GROUP)
        conf = wg.abs() > wg.abs().mean(-1, keepdim=True)
        sgn = torch.sign(wg)
        tq = torch.sign(load_tensor(ti, n).to(DEVICE, torch.float32).reshape_as(wg))
        bq = torch.sign(load_tensor(bi, n).to(DEVICE, torch.float32).reshape_as(wg))
        n_conf = conf.sum().item()
        r = {
            "conf_frac": conf.float().mean().item(),
            "tern_rev_given_conf": (((tq * sgn) == -1) & conf).sum().item() / n_conf,
            "onebit_flip_given_conf": ((bq != sgn) & conf).sum().item() / n_conf,
            "elapsed_s": round(time.time() - t0, 2),
        }
        r["ratio_1bit_over_tern"] = (r["onebit_flip_given_conf"]
                                     / max(r["tern_rev_given_conf"], 1e-12))
        results[n] = r
        print(f"{n:52s} {r['conf_frac']:9.3f} {r['tern_rev_given_conf']:13.5f} "
              f"{r['onebit_flip_given_conf']:14.5f} {r['ratio_1bit_over_tern']:6.1f}x")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"device": DEVICE, "conf_criterion": "|w| > mean|w|_group(parent)",
               "results": results}, open(args.out, "w"), indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
