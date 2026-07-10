#!/usr/bin/env python3
"""Normal-form hold — is the residual-stream token-repeat the I combinator?

Michael's hypothesis: models are reported to "repeat the same token in the
residual stream for several layers before finally emitting it." Read through
our thesis (forward pass = beta reduction): once a token has been reduced to
NORMAL FORM, the remaining layers have nothing left to do but apply I
(identity) — pass it through unchanged. That identity-hold IS the J-space
"motor zone" (late layers collapse to, and hold, the output token).

Made falsifiable (λ yardstick): if the token-repeat is the I combinator, then
contexts that are LITERALLY identity/copy (induction — the next token is a copy
of an earlier one) should reach normal form EARLIER and hold LONGER than
contexts that require COMPOSITION (nested/relative clauses, multi-hop). We
measure, per scored position, the logit-lens top-1 trajectory across all layers:

  converge_layer  — earliest layer L after which top-1(lens_L) == top-1(final)
                    and stays == final through the last layer.
  hold_frac       — (n_layers - converge_layer) / n_layers  (the identity-hold).
  settle_kl[L]    — KL(final ‖ lens_L): the plateau near 0 is the normal-form hold.

lens_L = logit-lens of the layer-L residual (verbum.jlens.logit_lens); note
lens_{last} == the model's true logits by construction, so convergence is
measured against the real output, not a proxy.

PRE-REGISTERED prediction (locked before the run):
  hold_frac(induction) > hold_frac(compose) AND
  converge_layer(induction) < converge_layer(compose).
  Report the distributions + a per-layer token TRAJECTORY demo (the tokens
  Michael wants to see). Two-sided: no separation = the token-repeat is NOT
  regime-specific (not the I combinator, just generic late settling).

CAVEAT (λ measure, stated up front): raw logit-lens is miscalibrated in early
layers (tuned-lens is the fix). A constant lens bias cancels in the
BETWEEN-REGIME contrast, which is the actual test; absolute converge_layer is
indicative, not exact.

Usage:
  uv run python scripts/experiments/jspace_normalform.py --model qwen3.6-27b
  uv run python scripts/experiments/jspace_normalform.py --model qwen3-0.6b --smoke

License: MIT
"""

from __future__ import annotations

import argparse
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
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "explore"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from probe_combinators import NULL_PROBES

from verbum import jlens

MODELS = {
    "qwen3-0.6b": "Qwen/Qwen3-0.6B",
    "qwen3-4b": "Qwen/Qwen3-4B",
    "qwen3-14b": "Qwen/Qwen3-14B",
    "qwen3.6-27b": "Qwen/Qwen3.6-27B",
}
OUT_ROOT = Path("results/jspace-normalform")

# Multi-hop composition prompts: the answer requires composing >=2 relations,
# so normal form should arrive LATE. (single-token answers = J-space readable.)
COMPOSE_PROMPTS = [
    "The capital of the country where the Eiffel Tower stands is",
    "The first letter of the name of the planet closest to the Sun is",
    "The color of the sky on a clear day, spelled backwards, starts with the letter",
    "The number of legs on a spider, plus the number of sides on a triangle, equals",
    "The opposite of the opposite of hot is",
    "The author of Romeo and Juliet was born in the country called",
]


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


def load(model_key: str):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    hf = MODELS[model_key]
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    dtype = torch.bfloat16 if model_key != "qwen3-0.6b" else torch.float32
    print(f"loading {hf} ({dtype}) on {device} ...", file=sys.stderr)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(hf)
    model = AutoModelForCausalLM.from_pretrained(
        hf, dtype=dtype, device_map=device
    ).eval()
    print(f"  loaded in {time.time() - t0:.0f}s", file=sys.stderr)
    return model, tok


# Natural passages tiled for induction (real tokens copy confidently — the
# logit-lens reads them cleanly, unlike random-token induction).
REPEAT_TEXTS = [
    " the quick brown fox jumps over the lazy dog by the river",
    " she sold seashells by the seashore on a bright summer morning",
    " in the beginning the code compiled and then the tests all passed",
]


def induction_ids(tok, which: int, reps: int) -> tuple[torch.Tensor, int]:
    """Tile a REAL text segment `reps` times; return (ids, period)."""
    seg = tok(
        REPEAT_TEXTS[which % len(REPEAT_TEXTS)],
        return_tensors="pt",
        add_special_tokens=False,
    )["input_ids"][0]
    return seg.repeat(reps), seg.shape[0]


@torch.no_grad()
def profile_positions(
    model, tok, positions, *, text=None, input_ids=None
) -> list[dict]:
    """Per scored position: converge_layer, hold_frac, top-token trajectory."""
    resids, ids = jlens.capture_residuals(model, tok, text, input_ids=input_ids)
    nl = jlens.n_layers(model)
    seq = ids.shape[0]
    positions = [p for p in positions if 0 <= p < seq]
    # per-layer logit-lens -> top-1 id + KL(final ‖ lens) at scored positions
    final = jlens.logit_lens(model, resids[nl - 1]).float()  # (seq, vocab)
    final_lp = torch.log_softmax(final, dim=-1)
    final_top = final.argmax(-1)  # (seq,)
    top_by_layer = np.zeros((nl, len(positions)), dtype=np.int64)
    kl_by_layer = np.zeros((nl, len(positions)), dtype=np.float32)
    fp = final_lp[positions]  # (P, vocab)
    ftop = final_top[positions].cpu().numpy()
    for L in range(nl):
        ll = jlens.logit_lens(model, resids[L]).float()[positions]  # (P, vocab)
        top_by_layer[L] = ll.argmax(-1).cpu().numpy()
        p = fp.exp()
        kl = (p * (fp - torch.log_softmax(ll, dim=-1))).sum(-1)
        kl_by_layer[L] = kl.cpu().numpy()
        del ll
    rows = []
    for j, pos in enumerate(positions):
        matches = top_by_layer[:, j] == ftop[j]
        # converge = earliest L s.t. all layers >= L match final
        conv = nl
        for L in range(nl):
            if matches[L:].all():
                conv = L
                break
        rows.append({
            "pos": int(pos),
            "final_token": tok.decode([int(ftop[j])]),
            "converge_layer": int(conv),
            "hold_frac": round((nl - conv) / nl, 4),
            "traj_top": [int(x) for x in top_by_layer[:, j]],
            "settle_kl": [round(float(x), 4) for x in kl_by_layer[:, j]],
        })
    return rows


def trajectory_str(tok, row: dict, nl: int) -> str:
    """Compress a top-token trajectory into 'layer:tok' run boundaries."""
    parts, prev = [], None
    for L, tid in enumerate(row["traj_top"]):
        if tid != prev:
            parts.append(f"L{L}:{tok.decode([tid])!r}")
            prev = tid
    return " -> ".join(parts)


def run(model_key: str, smoke: bool) -> dict:
    t0 = time.time()
    model, tok = load(model_key)
    nl = jlens.n_layers(model)
    reps = 6
    n_texts = 1 if smoke else len(REPEAT_TEXTS)
    compose = COMPOSE_PROMPTS[:2] if smoke else COMPOSE_PROMPTS
    prose = NULL_PROBES[:2] if smoke else NULL_PROBES

    regimes: dict[str, list[dict]] = {"induction": [], "compose": [], "prose": []}
    demos: dict[str, list[str]] = {}

    # induction: score positions predicting a COPY (2nd repetition onward)
    for w in range(n_texts):
        ids, period = induction_ids(tok, w, reps)
        scored = list(range(2 * period, ids.shape[0] - 1))  # from 3rd rep (stable)
        regimes["induction"] += profile_positions(model, tok, scored, input_ids=ids)
        print(f"  induction text {w} (period {period}) done", file=sys.stderr)

    # compose / prose: score the last position (the model's live next-token)
    for text in compose:
        ids = tok(text, return_tensors="pt")["input_ids"][0]
        regimes["compose"] += profile_positions(
            model, tok, [ids.shape[0] - 1], text=text
        )
    for text in prose:
        ids = tok(text, return_tensors="pt")["input_ids"][0]
        n = ids.shape[0]
        scored = list(range(max(2, n // 2), n - 1))  # 2nd-half positions
        regimes["prose"] += profile_positions(model, tok, scored, text=text)
    print("  compose/prose done", file=sys.stderr)

    def agg(rows: list[dict]) -> dict:
        hf = np.array([r["hold_frac"] for r in rows], dtype=np.float32)
        cl = np.array([r["converge_layer"] for r in rows], dtype=np.float32)
        # mean KL(final ‖ lens_L) curve over positions — the settle dynamics.
        kl = np.array([r["settle_kl"] for r in rows], dtype=np.float32)  # (n, nl)
        kl_curve = kl.mean(0)  # (nl,)
        # robust settle: earliest L after which mean KL stays below 1.0 nat.
        thr = 1.0
        settle = nl
        for L in range(nl):
            if (kl_curve[L:] < thr).all():
                settle = L
                break
        return {
            "n": len(rows),
            "hold_frac_mean": round(float(hf.mean()), 4),
            "hold_frac_median": round(float(np.median(hf)), 4),
            "converge_layer_mean": round(float(cl.mean()), 2),
            "converge_frac_mean": round(float(cl.mean()) / nl, 4),
            "kl_settle_layer": settle,
            "kl_settle_frac": round(settle / nl, 4),
            "kl_curve": [round(float(x), 3) for x in kl_curve],
        }

    stats = {k: agg(v) for k, v in regimes.items() if v}

    # demo trajectories: the earliest-converging induction copy + a compose one
    ind_sorted = sorted(regimes["induction"], key=lambda r: r["converge_layer"])
    if ind_sorted:
        demos["induction_earliest"] = [
            trajectory_str(tok, r, nl) for r in ind_sorted[:3]
        ]
    if regimes["compose"]:
        demos["compose"] = [
            f"{r['final_token']!r}: " + trajectory_str(tok, r, nl)
            for r in regimes["compose"]
        ]

    ind_h = stats.get("induction", {}).get("hold_frac_mean", 0)
    com_h = stats.get("compose", {}).get("hold_frac_mean", 1)
    ind_c = stats.get("induction", {}).get("converge_layer_mean", nl)
    com_c = stats.get("compose", {}).get("converge_layer_mean", 0)
    predicted = bool(ind_h > com_h and ind_c < com_c)
    call = "I-COMBINATOR-VISIBLE" if predicted else "NO-REGIME-SEPARATION"

    return {
        "experiment": "jspace_normalform: logit-lens normal-form hold_frac + "
        "converge_layer per regime (induction/compose/prose); I-combinator test",
        "date": datetime.now(UTC).isoformat(),
        "model": model_key,
        "model_hf": MODELS[model_key],
        "n_layers": nl,
        "git_sha": _git_sha(),
        "config": {"reps": reps, "n_texts": n_texts, "smoke": smoke},
        "locked_prediction": "hold_frac(induction) > hold_frac(compose) AND "
        "converge_layer(induction) < converge_layer(compose)",
        "verdict": {
            "call": call,
            "predicted_holds": predicted,
            "hold_frac": {k: stats[k]["hold_frac_mean"] for k in stats},
            "converge_frac": {k: stats[k]["converge_frac_mean"] for k in stats},
        },
        "stats": stats,
        "demos": demos,
        "elapsed_s": round(time.time() - t0, 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3.6-27b", choices=list(MODELS))
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()

    res = run(a.model, a.smoke)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    tag = "smoke-" + a.model if a.smoke else a.model
    out = OUT_ROOT / f"{tag}-{stamp}.json"
    out.write_text(json.dumps(res, indent=2))
    print(json.dumps({"verdict": res["verdict"], "demos": res["demos"]}, indent=2))
    print(f"\nwrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
