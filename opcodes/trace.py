#!/usr/bin/env python3
"""End-to-end opcode trace — detect → capture → fingerprint → classify.

The whole pipeline, architecture-agnostic, wired together:

  1. **detect**    ``topology.detect_topology`` finds the routing register.
  2. **capture**   ``capture.capture_gate`` reads per-layer gate features.
  3. **fingerprint** calibrate the ``RelationalCrystalClassifier`` on the crystal
     probes (last-token gate) against a natural-text null → the per-model crystal
     lattice and its crystal-bearing layers.
  4. **classify**  read lambda prompts per token → the per-layer opcode
     trajectory (the C→B program), null-gated so non-combinator tokens NO-OP.

No architecture is hard-coded anywhere: swap the ``--model`` and the same code
runs (Qwen dense, Gemma composite, Qwen3.6 hybrid, GPT-NeoX up-proj proxy). MoE
is refused at detect time with a clear message.

Usage:
    uv run python opcodes/trace.py --model Qwen/Qwen3-0.6B
    uv run python opcodes/trace.py --model Qwen/Qwen3.6-27B --device mps
    uv run python opcodes/trace.py --model Qwen/Qwen3-0.6B --smoke

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "opcodes"))

import capture as C  # noqa: E402
import topology as T  # noqa: E402
from classify import CRYSTAL, RelationalCrystalClassifier  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "opcode-trace"

# lambda sentences (the C→B compose program) — content read
LAMBDA_SENTENCES = [
    "The dog runs.",
    "Every student reads a book.",
    "If it rains, the ground is wet.",
    "No bird can swim.",
    "Mary likes the cat that John owns.",
    "Some teacher graded every exam.",
]

# natural-text null — bare, no β-reduction (the cross-task baseline)
NULL_SENTENCES = [
    "The sky was clear this morning.",
    "She walked to the store yesterday.",
    "Music played softly in the room.",
    "The old house stood on the hill.",
    "He drinks coffee every morning.",
    "Rain fell throughout the night.",
    "The garden was full of color.",
    "They watched a film last weekend.",
]


def load(model_name: str, device: str) -> tuple[Any, Any]:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_name)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        model_name, dtype=torch.bfloat16, low_cpu_mem_usage=True
    ).eval()
    if device != "cpu":
        model = model.to(device)
    print(f"[trace] loaded {model_name} on {device} in {time.time()-t0:.1f}s")
    return model, tok


def calibrate(
    model: Any, tok: Any, topo: T.ModelTopology, layers: list[int],
    probes_per_comb: int | None, n_perm: int, z_thresh: float,
) -> tuple[RelationalCrystalClassifier, dict]:
    from verbum.probes.library import crystal_probes

    probes = [p for p in crystal_probes() if p.combinator in CRYSTAL]
    if probes_per_comb is not None:
        kept, counts = [], Counter()
        for p in probes:
            if counts[p.combinator] < probes_per_comb:
                kept.append(p)
                counts[p.combinator] += 1
        probes = kept
    print(f"[trace] calibrating on {len(probes)} crystal probes ...")

    gate_by_layer: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    labels: list[str] = []
    for i, p in enumerate(probes):
        if i % 100 == 0:
            print(f"[trace]   probe {i}/{len(probes)}")
        cap = C.capture_gate(model, tok, p.prompt, topo=topo, layers=layers)
        for li in layers:
            gate_by_layer[li].append(cap.gate[li][-1])  # last-token crystal locus
        labels.append(p.combinator)
    gate_np = {li: np.stack(gate_by_layer[li]) for li in layers}
    labels_np = np.array(labels)

    print(f"[trace] building null from {len(NULL_SENTENCES)} natural-text prompts ...")
    null_by_layer: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    for s in NULL_SENTENCES:
        cap = C.capture_gate(model, tok, s, topo=topo, layers=layers)
        for li in layers:
            null_by_layer[li].append(cap.gate[li])  # all positions
    null_np = {li: np.concatenate(null_by_layer[li]) for li in layers}

    rcc = RelationalCrystalClassifier(
        layers, n_perm=n_perm, z_thresh=z_thresh, sil_z_thresh=2.0,
        consensus_gram="auto",
    )
    rcc.calibrate(gate_np, labels_np, null_gate_by_layer=null_np)
    summ = rcc.calibration_summary()
    summ["n_probes"] = len(probes)
    summ["n_null_tokens"] = int(next(iter(null_np.values())).shape[0])
    return rcc, summ


def trace(
    model: Any, tok: Any, topo: T.ModelTopology,
    rcc: RelationalCrystalClassifier, layers: list[int], z_thresh: float,
) -> dict:
    """Per-token per-layer opcode read over the lambda sentences → trajectory."""
    crystal = set(rcc.crystal_layers)
    layer_votes: dict[int, Counter] = {li: Counter() for li in layers}
    n_tokens = token_noop = 0
    for prompt in LAMBDA_SENTENCES:
        cap = C.capture_gate(model, tok, prompt, topo=topo, layers=layers)
        for pos in range(1, cap.n_tokens):  # skip BOS/first
            n_tokens += 1
            gate_tok = {li: cap.gate[li][pos] for li in layers}
            res = rcc.classify(gate_tok)
            fired = False
            for li, zmap in res.per_layer.items():
                op = max(zmap, key=zmap.get)
                if zmap[op] > z_thresh:
                    layer_votes[li][op] += 1
                    if li in crystal:
                        fired = True
            if not fired:
                token_noop += 1
    trajectory = []
    for li in sorted(crystal):
        if layer_votes[li]:
            op, votes = layer_votes[li].most_common(1)[0]
            trajectory.append({
                "layer": li, "op": op, "votes": votes,
                "total": sum(layer_votes[li].values()),
            })
    c_layers = [t["layer"] for t in trajectory if t["op"] == "C"]
    b_layers = [t["layer"] for t in trajectory if t["op"] == "B"]
    return {
        "n_tokens": n_tokens,
        "token_noop_rate": round(token_noop / n_tokens, 4) if n_tokens else 0.0,
        "crystal_layers": sorted(crystal),
        "trajectory": trajectory,
        "C_layers": c_layers, "B_layers": b_layers,
        "C_before_B": bool(c_layers and b_layers
                           and float(np.mean(c_layers)) < float(np.mean(b_layers))),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="End-to-end arch-agnostic opcode trace")
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="cpu", choices=["cpu", "mps", "cuda"])
    ap.add_argument("--probes-per-comb", type=int, default=None)
    ap.add_argument("--n-perm", type=int, default=300)
    ap.add_argument("--z", type=float, default=3.0)
    ap.add_argument("--smoke", action="store_true",
                    help="15 probes/comb, n_perm=120 (fast pipeline check)")
    args = ap.parse_args()
    ppc = 15 if args.smoke else args.probes_per_comb
    n_perm = 120 if args.smoke else args.n_perm

    model, tok = load(args.model, args.device)
    topo = T.detect_topology(model, model.config)
    print(f"[trace] {topo.summary()}")
    if not topo.traceable:
        print(f"[trace] REFUSED: register={topo.register!r} not traceable "
              f"({topo.read_register}). Nothing to trace.")
        for n in topo.notes:
            print(f"[trace]   · {n}")
        sys.exit(2)

    layers = list(range(topo.n_layers))
    t0 = time.time()
    rcc, calib = calibrate(model, tok, topo, layers, ppc, n_perm, args.z)
    print(f"[trace] crystal-bearing layers: "
          f"{len(calib['crystal_layers'])}/{topo.n_layers} "
          f"-> {calib['crystal_layers'][:16]}")
    tr = trace(model, tok, topo, rcc, layers, args.z)
    elapsed = time.time() - t0

    print("=" * 72)
    print(f"OPCODE TRACE — {args.model}  [{topo.read_register}]")
    print("=" * 72)
    print(f"crystal-bearing layers: {len(tr['crystal_layers'])}/{topo.n_layers}")
    print(f"token no-op rate: {tr['token_noop_rate']} "
          f"(non-combinator tokens that stay silent)")
    print(f"C-layers={tr['C_layers']}  B-layers={tr['B_layers']}  "
          f"C_before_B={tr['C_before_B']}")
    print("trajectory (crystal-bearing layers, dominant op over lambda tokens):")
    for t in tr["trajectory"]:
        bar = "#" * int(20 * t["votes"] / max(1, t["total"]))
        print(f"  L{t['layer']:>3}  {t['op']:>4}  "
              f"{t['votes']:>3}/{t['total']:<3} {bar}")
    print("=" * 72)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = args.model.split("/")[-1].lower().replace(".", "-")
    out = {
        "model": args.model, "device": args.device,
        "topology": {
            "arch": topo.arch, "register": topo.register,
            "read_register": topo.read_register, "layers_path": topo.layers_path,
            "gate_suffix": topo.gate_suffix, "gate_width": topo.gate_width,
            "n_layers": topo.n_layers,
        },
        "calibration": calib, "trace": tr,
        "elapsed_s": round(elapsed, 1),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "smoke": args.smoke, "probes_per_comb": ppc, "n_perm": n_perm,
    }
    path = RESULTS_DIR / f"{slug}_{args.device}.json"
    path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"[trace] wrote {path}  ({elapsed:.1f}s)")


if __name__ == "__main__":
    main()
