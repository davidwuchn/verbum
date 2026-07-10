#!/usr/bin/env python3
"""Does each combinator have its own input-attribution (routing-Jacobian) signature?

The opcode = how arguments route to the output = the structure of the routing
Jacobian. We read that Jacobian as input attribution (grad of the prediction
w.r.t. each source position's embedding; verbum.jacobian) and test whether each
combinator's PREDICTED structural metric separates its ACTIVE probes from its
CONTROL probes:

    K -> concentration   (selection discards positions)
    I -> copy_mass       (identity routes through repeated/copied tokens)
    B -> range           (composition = long-range, mediated dependence)
    C -> front_bias      (flip/passive reorders argument roles)

We build the full combinator x metric matrix of (active - control) deltas; the
PREDICTED DIAGONAL should light up. S is predicted to stay flat on every metric
(a first-order/linear attribution under-reads argument SHARING — the duplication
is second-order), which is itself a thesis-consistent negative.

CONTROLS: matched active/control probe pairs (surface-matched by construction) +
a shuffled-LABEL null (pool the pairs of a combinator, relabel active/control at
random, recompute the delta) — controls "any active/control contrast moves this
metric". N shuffles -> null z per cell (s247/s262 discipline).

PRE-REGISTERED bands (locked before the run; two-sided):
  * SIGNATURE if >=3/4 of {K,I,B,C} have their predicted-diagonal delta in the
    expected direction AND z >= 1.64 vs the shuffled-label null.
  * DIAGONAL-DOMINANT if for those combinators the predicted metric is the argmax
    |delta| over the 4 metrics (its own signature beats the others).
  * S_UNDERREAD if S's max |z| over metrics < min diagonal |z| over {K,I,B,C}.
  Overall: SIGNAL / PARTIAL / NULL. A clean NULL is a finding.

Usage:
  uv run python scripts/experiments/jacobian_opcodes.py --model pythia-160m-deduped
  uv run python scripts/experiments/jacobian_opcodes.py --smoke
  uv run python scripts/experiments/jacobian_opcodes.py --self-test

License: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

os.environ.setdefault("PYTHONUNBUFFERED", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "explore"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from basis_fit_kibc_vs_ski import S_PROBES
from probe_combinators import PROBES as KIBC_PROBES

from verbum import jacobian as jac

MODELS = {
    "pythia-70m-deduped": "EleutherAI/pythia-70m-deduped",
    "pythia-160m-deduped": "EleutherAI/pythia-160m-deduped",
    "pythia-410m-deduped": "EleutherAI/pythia-410m-deduped",
    "qwen3-0.6b": "Qwen/Qwen3-0.6B",
    "qwen3-4b": "Qwen/Qwen3-4B",
    "qwen3-14b": "Qwen/Qwen3-14B",
    "qwen3.6-27b": "Qwen/Qwen3.6-27B",
}
# models loaded in bf16 (float32 too heavy); small pythia stay float32 (MPS fp16 nan)
_BF16 = {"qwen3-4b", "qwen3-14b", "qwen3.6-27b"}
OUT_ROOT = Path("results/jacobian-opcodes")
METRIC_NAMES = ["concentration", "copy_mass", "range", "front_bias"]


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


def _hash(p: dict) -> str:
    return hashlib.sha256(json.dumps(p, sort_keys=True).encode()).hexdigest()[:12]


def load(model_key: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    hf = MODELS[model_key]
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    dtype = torch.bfloat16 if model_key in _BF16 else torch.float32
    print(f"loading {hf} ({dtype}) on {device} ...", file=sys.stderr)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(hf)
    model = AutoModelForCausalLM.from_pretrained(
        hf, dtype=dtype, device_map=device
    ).eval()
    print(f"  loaded in {time.time() - t0:.0f}s", file=sys.stderr)
    return model, tok


def metrics_for(model, tok, text: str) -> dict[str, float]:
    """All 4 structural metrics for one sentence (attribute the last position)."""
    infl, ids, _toks, _tt = jac.input_attribution(model, tok, text, target_pos=-1)
    tp = len(infl) - 1
    return {name: float(fn(infl, ids, tp)) for name, fn in jac.METRICS.items()}


def run(model_key: str, n_shuffle: int, smoke: bool) -> dict:
    t0 = time.time()
    model, tok = load(model_key)

    combos = {k: KIBC_PROBES[k] for k in ("K", "I", "B", "C")}
    combos["S"] = S_PROBES["S"]
    if smoke:
        combos = {k: combos[k] for k in ("K", "I", "S")}
        for c in combos.values():
            c["active"], c["control"] = c["active"][:3], c["control"][:3]

    # per-sentence metrics (cache; sentences may be shared across K/I)
    cache: dict[str, dict[str, float]] = {}

    def M(s: str) -> dict[str, float]:
        if s not in cache:
            cache[s] = metrics_for(model, tok, s)
        return cache[s]

    results: dict[str, dict] = {}
    for name, c in combos.items():
        act = [M(s) for s in c["active"]]
        con = [M(s) for s in c["control"]]
        deltas = {
            m: float(np.mean([a[m] for a in act]) - np.mean([b[m] for b in con]))
            for m in METRIC_NAMES
        }
        # shuffled-label null per metric: relabel pooled pairs
        pooled = c["active"] + c["control"]
        na = len(c["active"])
        rng = np.random.RandomState(11 + hash(name) % 1000)
        null = {m: [] for m in METRIC_NAMES}
        for _ in range(n_shuffle):
            idx = rng.permutation(len(pooled))
            pa = [M(pooled[i]) for i in idx[:na]]
            pc = [M(pooled[i]) for i in idx[na:]]
            for m in METRIC_NAMES:
                null[m].append(
                    np.mean([a[m] for a in pa]) - np.mean([b[m] for b in pc])
                )
        z = {}
        for m in METRIC_NAMES:
            nm, ns = float(np.mean(null[m])), float(np.std(null[m]) + 1e-9)
            z[m] = round((deltas[m] - nm) / ns, 3)
        pred = jac.PREDICTED.get(name)
        results[name] = {
            "delta": {m: round(deltas[m], 4) for m in METRIC_NAMES},
            "z_vs_shuffle": z,
            "predicted_metric": pred,
            "predicted_delta": round(deltas[pred], 4) if pred else None,
            "predicted_z": z.get(pred),
            "argmax_metric": max(METRIC_NAMES, key=lambda m: abs(deltas[m])),
        }
        print(f"  [{name}] pred={pred} dz={z.get(pred)} "
              f"argmax={results[name]['argmax_metric']} "
              f"z={ {m: z[m] for m in METRIC_NAMES} }", file=sys.stderr)

    # ── verdict ──────────────────────────────────────────────────────────
    diag = {k: results[k] for k in ("K", "I", "B", "C") if k in results}
    hit = {
        k: r for k, r in diag.items()
        if r["predicted_z"] is not None and r["predicted_z"] >= 1.64
    }
    diagonal_dominant = {
        k: (r["argmax_metric"] == r["predicted_metric"]) for k, r in hit.items()
    }
    diag_z = [abs(r["predicted_z"]) for r in diag.values() if r["predicted_z"]]
    s_z = []
    if "S" in results:
        s_z = [abs(v) for v in results["S"]["z_vs_shuffle"].values()]
    s_underread = bool(s_z and diag_z and max(s_z) < min(diag_z))
    need = 3 if not smoke else 1
    call = ("SIGNAL" if len(hit) >= need else ("PARTIAL" if hit else "NULL"))

    return {
        "experiment": "jacobian_opcodes: input-attribution structural signatures "
        "(concentration/copy_mass/range/front_bias) per combinator, active vs "
        "control, shuffled-label null; opcode = routing-Jacobian structure",
        "date": datetime.now(UTC).isoformat(),
        "model": model_key,
        "model_hf": MODELS[model_key],
        "git_sha": _git_sha(),
        "probe_hash": _hash({**combos}),
        "config": {"n_shuffle": n_shuffle, "smoke": smoke,
                   "predicted": jac.PREDICTED},
        "locked_bands": {
            "SIGNAL": ">=3/4 of K,I,B,C have predicted-diagonal z>=1.64",
            "DIAGONAL_DOMINANT": "predicted metric is argmax|delta| for the hits",
            "S_UNDERREAD": "max|z|(S) < min diagonal|z|(K,I,B,C)",
        },
        "verdict": {
            "call": call,
            "n_diagonal_hits": len(hit),
            "diagonal_hits": sorted(hit),
            "diagonal_dominant": diagonal_dominant,
            "s_underread": s_underread,
            "predicted_z": {k: results[k]["predicted_z"] for k in diag},
        },
        "results": results,
        "elapsed_s": round(time.time() - t0, 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="pythia-160m-deduped", choices=list(MODELS))
    ap.add_argument("--n-shuffle", type=int, default=50)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        print(json.dumps(jac.self_test(), indent=2))
        return

    n_shuffle = 5 if a.smoke else a.n_shuffle
    res = run(a.model, n_shuffle, a.smoke)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    tag = "smoke-" + a.model if a.smoke else a.model
    out = OUT_ROOT / f"{tag}-{stamp}.json"
    out.write_text(json.dumps(res, indent=2))
    print(json.dumps(res["verdict"], indent=2))
    print(f"\nwrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
