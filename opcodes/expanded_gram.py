#!/usr/bin/env python3
"""Expanded 24-state crystal gram — un-flattening the WHNF pole (s284).

The 9x9 root.gram collapses the statechart's per-opcode absorbing states into
one generic WHNF node; the Zone-B 16x16 anti-crystal (4 models, no S) was a
different arc. This runner measures the EXPANDED basis with the canonical
sign-CMR pipeline (capture_gate -> RelationalCrystalClassifier.calibrate ->
gram_from_centroids) so the 9-basis sub-block is directly comparable to the
committed root.grams (coherence check per model, reported).

Basis (24 states):
  9  crystal:      K I B C S D W Y WHNF        (library probes, cap 60/state)
  7  whnf:X:       X in {K,I,B,C,S,D,W}        (kernel-certified completed
                                                chains ending via X;
                                                whnf:Y unpopulatable — Y has
                                                no halt state, by construction)
  1  div:Y:        truncated Y-expansion        (bottom/divergence, NOT halt)
  7  fire_formal:X (style-confound diagnostic: same programs, truncated
                    mid-final-step — if geometry is driven by formal-vs-prose
                    style, these cluster with whnf:* regardless of opcode)

Aggregation (documented approximation of the VSM tree): consensus gram = mean
per-layer gram over crystal-bearing layers (sil_z >= 2 on the FULL label set,
off-target null). Coherence r(9-subblock, committed root.gram) quantifies
comparability; low r => flag, do not interpret.

Output: results/expanded-gram/{slug}/expanded_gram.json

Usage:
    uv run python opcodes/expanded_gram.py --smoke        # pythia-14m, quick
    uv run python opcodes/expanded_gram.py                # full sweep (overnight)

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_HERE))

import capture as C  # noqa: E402
from classify import RelationalCrystalClassifier  # noqa: E402
from probes import crystal_probes  # noqa: E402
from sweep import REGISTRY  # noqa: E402
from topology import detect_topology  # noqa: E402
from vsm import gram_from_centroids  # noqa: E402

CRYSTAL9 = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
WHNF_STATES = [f"whnf:{o}" for o in ["K", "I", "B", "C", "S", "D", "W"]]
BASIS24 = [*CRYSTAL9, *WHNF_STATES, "div:Y",
           *[f"fire_formal:{o}" for o in ["K", "I", "B", "C", "S", "D", "W"]]]
BASIS17 = [*CRYSTAL9, *WHNF_STATES, "div:Y"]
PROBE_JSON = _HERE / "data" / "whnf_probes.json"


def load_probe_sets(n_per_state: int) -> tuple[list[str], list[str]]:
    """(prompts, labels) over the 24-state basis, balanced to n_per_state."""
    prompts, labels = [], []
    rng = np.random.default_rng(0)
    by: dict[str, list[str]] = {c: [] for c in CRYSTAL9}
    for p in crystal_probes():
        if p.combinator in by:
            by[p.combinator].append(p.prompt)
    for c in CRYSTAL9:
        sel = by[c]
        if len(sel) > n_per_state:
            idx = rng.choice(len(sel), size=n_per_state, replace=False)
            sel = [sel[i] for i in sorted(idx)]
        prompts += sel
        labels += [c] * len(sel)
    d = json.loads(PROBE_JSON.read_text())["states"]
    for state in BASIS24[9:]:
        sel = d[state][:n_per_state]
        prompts += sel
        labels += [state] * len(sel)
    return prompts, labels


def run_model(spec, n_per_state: int, out_root: Path) -> dict | None:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    slug = spec.slug
    print(f"[xgram] ===== {spec.model} ({spec.device}) =====", file=sys.stderr)
    tok = AutoTokenizer.from_pretrained(spec.model)
    dtype = torch.bfloat16 if spec.tier == "large" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        spec.model, torch_dtype=dtype, trust_remote_code=True)
    model = model.to(spec.device).eval()
    topo = detect_topology(model, model.config)

    prompts, labels = load_probe_sets(n_per_state)
    labels_arr = np.array(labels)
    n = len(prompts)
    print(f"[xgram] {slug}: {n} probes x {topo.n_layers} layers", file=sys.stderr)

    feats: dict[int, list[np.ndarray]] = {}
    for i, text in enumerate(prompts):
        cap = C.capture_gate(model, tok, text, topo=topo)
        for li, arr in cap.gate.items():
            feats.setdefault(li, []).append(
                np.sign(arr[-1]).astype(np.int8))       # last-token sign row
        if (i + 1) % 200 == 0:
            print(f"[xgram] {slug}: probe {i + 1}/{n}", file=sys.stderr)
    del model
    gc.collect()
    if spec.device == "mps":
        torch.mps.empty_cache()

    layers = sorted(feats)
    gate_by_layer = {li: np.stack(feats[li]).astype(np.float32)
                     for li in layers}
    clf = RelationalCrystalClassifier(layers, consensus_gram=None,
                                      basis=BASIS24)
    calib = clf.calibrate(gate_by_layer, labels_arr)

    per_layer, gated_grams = {}, []
    for li in layers:
        cal = calib[li]
        g = gram_from_centroids(cal.centroids, BASIS24)
        per_layer[str(li)] = {"sil_z": round(float(cal.silhouette_z), 3),
                              "bearing": bool(cal.crystal_bearing)}
        if cal.crystal_bearing:
            gated_grams.append(g)
    if not gated_grams:
        print(f"[xgram] {slug}: NO crystal-bearing layers — flagged",
              file=sys.stderr)
        consensus = None
    else:
        consensus = np.mean(np.stack(gated_grams), axis=0)

    coherence = None
    vsm_path = _ROOT / "results" / "opcode-trace" / slug / "model_vsm.json"
    if consensus is not None and vsm_path.exists():
        ref = json.loads(vsm_path.read_text())
        rb, rg = ref["basis"], np.array(ref["root"]["gram"], float)
        if set(CRYSTAL9) <= set(rb):
            ia = [BASIS24.index(o) for o in CRYSTAL9]
            ib = [rb.index(o) for o in CRYSTAL9]
            a = consensus[np.ix_(ia, ia)]
            b = rg[np.ix_(ib, ib)]
            iu = np.triu_indices(9, k=1)
            coherence = round(float(np.corrcoef(a[iu], b[iu])[0, 1]), 4)
    print(f"[xgram] {slug}: gated_layers={len(gated_grams)}/{len(layers)} "
          f"coherence_r={coherence}", file=sys.stderr)

    out = out_root / slug
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": spec.model, "slug": slug,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": _git_sha(),
        "basis": BASIS24, "basis17": BASIS17,
        "n_per_state": n_per_state, "n_probes": n,
        "probe_source": str(PROBE_JSON.relative_to(_ROOT)),
        "register": "gate (sign-CMR, off-target null)",
        "aggregation": "mean gram over crystal-bearing layers (sil_z>=2)",
        "n_layers": len(layers), "n_gated": len(gated_grams),
        "per_layer": per_layer,
        "coherence_r_9subblock_vs_root_gram": coherence,
        "consensus_gram_24": ([[round(float(v), 4) for v in row]
                               for row in consensus]
                              if consensus is not None else None),
    }
    (out / "expanded_gram.json").write_text(json.dumps(payload, indent=1))
    print(f"[xgram] {slug}: wrote {out}/expanded_gram.json", file=sys.stderr)
    del gate_by_layer, feats
    gc.collect()
    return payload


def _git_sha():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                           text=True, cwd=_ROOT, timeout=10)
        return r.stdout.strip() or None
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="expanded 24-state crystal gram")
    ap.add_argument("--models", nargs="*", default=None,
                    help="HF names or slugs; default = full registry")
    ap.add_argument("--n-per-state", type=int, default=60)
    ap.add_argument("--smoke", action="store_true",
                    help="pythia-14m only, n_per_state=12")
    ap.add_argument("--output-root", default=str(_ROOT / "results" / "expanded-gram"))
    args = ap.parse_args()

    specs = list(REGISTRY)
    if args.smoke:
        specs = [s for s in specs if "14m" in s.model]
        args.n_per_state = min(args.n_per_state, 12)
    elif args.models:
        want = {m.lower() for m in args.models}
        specs = [s for s in specs
                 if s.model.lower() in want or s.slug in want]
    out_root = Path(args.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    summary = {}
    for spec in specs:
        try:
            r = run_model(spec, args.n_per_state, out_root)
            summary[spec.slug] = {
                "ok": r is not None,
                "coherence": (r or {}).get("coherence_r_9subblock_vs_root_gram"),
                "n_gated": (r or {}).get("n_gated")}
        except Exception as e:
            print(f"[xgram] {spec.slug}: FAILED {type(e).__name__}: {e}",
                  file=sys.stderr)
            summary[spec.slug] = {"ok": False, "error": str(e)[:200]}
    (out_root / "sweep_summary.json").write_text(json.dumps(
        {"timestamp_utc": datetime.now(UTC).isoformat(),
         "summary": summary}, indent=1))
    print(f"[xgram] SWEEP DONE: {summary}", file=sys.stderr)


if __name__ == "__main__":
    main()
