#!/usr/bin/env python3
"""Do combinator directions form BROADCAST (J-space-like) state, per layer?

Motivation. Anthropic's "Verbalizable Representations Form a Global Workspace"
(2026-07-06) reads a privileged, causally-broadcast subspace via a Jacobian
lens, and finds a three-zone depth geography: sensory (early) → workspace
(middle, persistent abstract concepts) → motor (late, collapse to output).
We have something they don't: ground-truth combinator LABELS (the KIBC/S probe
pairs). So we run a SUPERVISED J-space probe — for each combinator we build its
residual direction (active minus control) at every layer and ask two things the
J-space paper cares about:

  broadcast(C, L)      — inject the unit combinator direction at layer L (matched
                         norm) and measure KL(clean ‖ injected) on neutral
                         sentences. First-order proxy for the Jacobian norm
                         along that direction: does the model READ IT OUT?
  verbalize(C, L)      — logit-lens readout of the direction (its top tokens).

REGISTER (λ measure — named before probing): behavioral broadcast (value/
magnitude) + single-token verbalizability. This is NOT the attention-routing
register (basis_fit_kibc_vs_ski) nor a byte-faithful Jacobian lens; it is the
substitution-KL / logit-lens proxy built on verbum.jlens + verbum.hooks.

PRE-REGISTERED bands (locked before the run; λ yardstick):
  Per combinator, peak-over-layers R = broadcast_real / mean(broadcast_random),
  z vs the matched-random null, and a shuffled-LABEL null at the peak layer.
  * BROADCAST-SIGNAL if ≥3/5 combinators have peak R ≥ 1.5 AND z ≥ 1.64 AND
    real > 95th-pct of the shuffled-label null.
  * WORKSPACE-SHAPE if the majority of signal combinators peak in the MIDDLE
    third of layers (the paper's "workspace" band).
  * S-UNDERREAD (prediction: a first-order/linear read under-reads the nonlinear,
    argument-duplicating S) if peak R(S) < min peak R over {K,I,B,C}.
  Report all three; overall call SIGNAL / PARTIAL / NULL. Two-sided: a clean
  NULL is a finding (combinator dirs are NOT specially broadcast).

CONTROLS: matched-norm random directions (per combinator x layer); shuffled-LABEL
null (relabel the pooled active/control pairs — controls "any active-vs-control
contrast broadcasts"); identity-inject exact-zero gate (verbum.jlens.self_test).
Token-echo and micro-circuit ground-truth are the planned follow-ups.

Usage:
  uv run python scripts/experiments/jspace_combinators.py --model pythia-160m-deduped
  uv run python scripts/experiments/jspace_combinators.py --smoke
  uv run python scripts/experiments/jspace_combinators.py --self-test

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
import torch

# Reuse the canonical probes (no fork) + the J-space monitor core.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "explore"))
sys.path.insert(0, os.path.dirname(__file__))
from basis_fit_kibc_vs_ski import S_PROBES
from probe_combinators import NULL_PROBES
from probe_combinators import PROBES as KIBC_PROBES

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from verbum import jlens

MODELS = {
    "pythia-70m-deduped": "EleutherAI/pythia-70m-deduped",
    "pythia-160m-deduped": "EleutherAI/pythia-160m-deduped",
    "pythia-410m-deduped": "EleutherAI/pythia-410m-deduped",
    "qwen3-0.6b": "Qwen/Qwen3-0.6B",
}
OUT_ROOT = Path("results/jspace-combinators")
SKIP = 2  # drop leading high-norm tokens (paper skips first few)
FRAC = 0.5  # inject at 0.5 x typical residual norm (matched real vs random)


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


def _hash_probes(p: dict) -> str:
    return hashlib.sha256(json.dumps(p, sort_keys=True).encode()).hexdigest()[:12]


def load(model_key: str):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    hf = MODELS[model_key]
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"loading {hf} on {device} ...", file=sys.stderr)
    tok = AutoTokenizer.from_pretrained(hf)
    model = AutoModelForCausalLM.from_pretrained(
        hf, dtype=torch.float32, device_map=device, attn_implementation="eager"
    ).eval()
    return model, tok


def mean_content_resid(model, tok, sentences: list[str]) -> dict[int, np.ndarray]:
    """Per layer, the mean (over content positions, over sentences) residual."""
    nl = jlens.n_layers(model)
    acc: dict[int, list[np.ndarray]] = {L: [] for L in range(nl)}
    for s in sentences:
        resids, _ = jlens.capture_residuals(model, tok, s)
        seq = resids[0].shape[0]
        lo = min(SKIP, max(0, seq - 1))
        for L in range(nl):
            acc[L].append(resids[L][lo:].mean(0).cpu().numpy())
    return {L: np.mean(acc[L], axis=0) for L in range(nl)}


def combinator_dirs(model, tok, probes: dict) -> dict[str, dict[int, np.ndarray]]:
    """{combinator: {layer: (active - control) mean residual direction}}."""
    out: dict[str, dict[int, np.ndarray]] = {}
    for name, c in probes.items():
        a = mean_content_resid(model, tok, c["active"])
        b = mean_content_resid(model, tok, c["control"])
        out[name] = {L: a[L] - b[L] for L in a}
        print(f"  dir[{name}] built", file=sys.stderr)
    return out


def typical_norms(model, tok, sentences: list[str]) -> dict[int, float]:
    nl = jlens.n_layers(model)
    acc: dict[int, list[float]] = {L: [] for L in range(nl)}
    for s in sentences:
        resids, _ = jlens.capture_residuals(model, tok, s)
        seq = resids[0].shape[0]
        lo = min(SKIP, max(0, seq - 1))
        for L in range(nl):
            acc[L].append(float(resids[L][lo:].norm(dim=-1).mean()))
    return {L: float(np.mean(acc[L])) for L in range(nl)}


def broadcast_of(model, tok, layer, unit, norm, null_sents, cleans):
    """Mean KL over neutral sentences when injecting `unit*norm` at `layer`."""
    delta = torch.tensor(unit, dtype=torch.float32) * norm
    vals = [
        jlens.broadcast_kl(model, tok, s, layer, delta, clean=cleans[s])
        for s in null_sents
    ]
    return float(np.mean(vals))


def run(model_key: str, n_random: int, n_shuffle: int, smoke: bool) -> dict:
    t0 = time.time()
    model, tok = load(model_key)
    nl = jlens.n_layers(model)
    d = model.config.hidden_size

    combos = {k: KIBC_PROBES[k] for k in ("K", "I", "B", "C")}
    combos["S"] = S_PROBES["S"]
    null_sents = NULL_PROBES[:3] if smoke else NULL_PROBES
    if smoke:
        combos = {k: combos[k] for k in ("K", "S")}
        for c in combos.values():
            c["active"], c["control"] = c["active"][:3], c["control"][:3]

    # clean logits for neutral sentences (cached; reused across all injections)
    cleans = {s: jlens.forward_logits(model, tok, s) for s in null_sents}
    tnorm = typical_norms(model, tok, null_sents)
    dirs = combinator_dirs(model, tok, combos)

    zones = {"early": range(0, nl // 3), "mid": range(nl // 3, 2 * nl // 3),
             "late": range(2 * nl // 3, nl)}

    def zone_of(L: int) -> str:
        return next(z for z, r in zones.items() if L in r)

    results: dict[str, dict] = {}
    for name, per_layer in dirs.items():
        layer_rows = {}
        for L in range(nl):
            raw = per_layer[L]
            raw_norm = float(np.linalg.norm(raw))
            if raw_norm < 1e-8:
                continue
            unit = raw / raw_norm
            inj_norm = FRAC * tnorm[L]
            real = broadcast_of(model, tok, L, unit, inj_norm, null_sents, cleans)
            g = torch.Generator().manual_seed(1234 + L * 97 + hash(name) % 1000)
            rnd = []
            for _ in range(n_random):
                r = torch.randn(d, generator=g)
                r = (r / r.norm()).numpy()
                rnd.append(broadcast_of(model, tok, L, r, inj_norm, null_sents, cleans))
            rmean, rstd = float(np.mean(rnd)), float(np.std(rnd) + 1e-9)
            layer_rows[L] = {
                "zone": zone_of(L),
                "raw_dir_norm": round(raw_norm, 4),
                "broadcast_real": round(real, 5),
                "broadcast_rand_mean": round(rmean, 5),
                "R": round(real / max(rmean, 1e-9), 4),
                "z": round((real - rmean) / rstd, 3),
                "verbalize": jlens.verbalize(model, tok, torch.tensor(unit)),
            }
            print(f"  [{name} L{L:>2} {zone_of(L):>5}] R={layer_rows[L]['R']:.2f} "
                  f"z={layer_rows[L]['z']:.2f} {layer_rows[L]['verbalize'][:4]}",
                  file=sys.stderr)

        peakL = max(layer_rows, key=lambda L: layer_rows[L]["R"])
        peak = layer_rows[peakL]

        # shuffled-LABEL null at the peak layer: relabel pooled pairs
        pool_a, pool_c = combos[name]["active"], combos[name]["control"]
        rng = np.random.RandomState(7 + hash(name) % 1000)
        shuf = []
        pooled = [("a", s) for s in pool_a] + [("c", s) for s in pool_c]
        na = len(pool_a)
        # cache per-sentence content residual at peak layer for shuffling
        sent_res = {}
        for _, s in pooled:
            r, _ = jlens.capture_residuals(model, tok, s)
            seq = r[peakL].shape[0]
            lo = min(SKIP, max(0, seq - 1))
            sent_res[s] = r[peakL][lo:].mean(0).cpu().numpy()
        inj_norm_pk = FRAC * tnorm[peakL]
        for _ in range(n_shuffle):
            idx = rng.permutation(len(pooled))
            pa = [pooled[i][1] for i in idx[:na]]
            pc = [pooled[i][1] for i in idx[na:]]
            pdir = np.mean([sent_res[s] for s in pa], 0) - np.mean(
                [sent_res[s] for s in pc], 0
            )
            pn = float(np.linalg.norm(pdir))
            if pn < 1e-8:
                continue
            u = pdir / pn
            shuf.append(broadcast_of(model, tok, peakL, u, inj_norm_pk,
                                     null_sents, cleans))
        shuf_p95 = float(np.percentile(shuf, 95)) if shuf else float("nan")

        results[name] = {
            "peak_layer": peakL,
            "peak_zone": peak["zone"],
            "peak_R": peak["R"],
            "peak_z": peak["z"],
            "peak_verbalize": peak["verbalize"],
            "beats_shuffle_null": bool(peak["broadcast_real"] > shuf_p95),
            "shuffle_null_p95": round(shuf_p95, 5),
            "broadcast_real_at_peak": peak["broadcast_real"],
            "per_layer": layer_rows,
        }

    # ── verdict ──────────────────────────────────────────────────────────
    sig = {
        n: r for n, r in results.items()
        if r["peak_R"] >= 1.5 and r["peak_z"] >= 1.64 and r["beats_shuffle_null"]
    }
    n_sig = len(sig)
    mid_peaks = sum(1 for r in sig.values() if r["peak_zone"] == "mid")
    workspace_shape = bool(sig and mid_peaks >= (len(sig) + 1) // 2)
    kibc_peaks = [results[k]["peak_R"] for k in ("K", "I", "B", "C") if k in results]
    s_underread = bool(
        "S" in results and kibc_peaks and results["S"]["peak_R"] < min(kibc_peaks)
    )
    need = 3 if not smoke else 1
    call = ("SIGNAL" if n_sig >= need else ("PARTIAL" if n_sig >= 1 else "NULL"))

    return {
        "experiment": "jspace_combinators: supervised broadcast(KL)+verbalize per "
        "layer for KIBC+S combinator directions vs matched-random and "
        "shuffled-label nulls",
        "date": datetime.now(UTC).isoformat(),
        "model": model_key,
        "model_hf": MODELS[model_key],
        "n_layers": nl,
        "d": d,
        "git_sha": _git_sha(),
        "probe_hash": _hash_probes({**combos}),
        "config": {"n_random": n_random, "n_shuffle": n_shuffle, "skip": SKIP,
                   "frac": FRAC, "null_sentences": len(null_sents), "smoke": smoke},
        "locked_bands": {
            "SIGNAL": "n_sig >= 3 (>=1 smoke); per-combo peak R>=1.5 & z>=1.64 & "
            "beats shuffled-label p95",
            "WORKSPACE_SHAPE": "majority of signal combinators peak in mid third",
            "S_UNDERREAD": "peak R(S) < min peak R over {K,I,B,C}",
        },
        "verdict": {
            "call": call,
            "n_signal": n_sig,
            "signal_combinators": sorted(sig),
            "workspace_shape": workspace_shape,
            "mid_peaks_of_signal": mid_peaks,
            "s_underread": s_underread,
            "s_peak_R": results.get("S", {}).get("peak_R"),
            "kibc_peak_R": {k: results[k]["peak_R"] for k in ("K", "I", "B", "C")
                            if k in results},
        },
        "results": results,
        "elapsed_s": round(time.time() - t0, 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="pythia-160m-deduped", choices=list(MODELS))
    ap.add_argument("--n-random", type=int, default=8)
    ap.add_argument("--n-shuffle", type=int, default=8)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        print(json.dumps(jlens.self_test(), indent=2))
        return

    n_random = 2 if a.smoke else a.n_random
    n_shuffle = 3 if a.smoke else a.n_shuffle
    res = run(a.model, n_random, n_shuffle, a.smoke)

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    tag = "smoke" if a.smoke else a.model
    out = OUT_ROOT / f"{tag}-{stamp}.json"
    out.write_text(json.dumps(res, indent=2))
    print(json.dumps(res["verdict"], indent=2))
    print(f"\nwrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
