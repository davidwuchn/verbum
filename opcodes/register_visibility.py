#!/usr/bin/env python3
"""Per-combinator VISIBILITY in the gate routing register — is `I` a no-op?

Hypothesis (session design thread): identity ``I`` = λx.x is the *ground state*
of routing — "hold unchanged" imposes no differential gate signal, sits at the
common-mode we subtract, and therefore reads as a **no-op**. Active combinators
(B compose, C permute, S share) impose distinctive routing and fire. If so, ``I``
does not live in the routing register at all (it lives in the value/residual
stream), and the no-op rate is partly *identity-holds the instrument cannot see*.

This is the decisive cheap test. Held-out design:

  1. split the crystal probes calib/test per combinator;
  2. calibrate the ``RelationalCrystalClassifier`` on calib (natural-text null);
  3. classify each *test* probe's last-token gate;
  4. per combinator report:
       - **self-accuracy**  fraction where dominant op == true label
       - **no-op rate**     fraction where dominant == '·' (nothing fired)
       - **mean best-z**    how strongly the TRUE combinator is seen (max z over
                            crystal layers for the true label)
       - **top confusion**  what the combinator is most often called instead

Prediction if the register hypothesis holds: ``I`` (and maybe ``K`` = discard)
show HIGH no-op + LOW self-acc + LOW best-z; B/C/S show LOW no-op + HIGH self-acc
+ HIGH best-z. A shuffled-label control anchors chance.

Usage:
    uv run python opcodes/register_visibility.py --model Qwen/Qwen3-0.6B

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
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

import capture as C  # noqa: E402
import topology as T  # noqa: E402
from relational_opcode import CRYSTAL, RelationalCrystalClassifier  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "register-visibility"

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


def _load(model_name: str, device: str) -> tuple[Any, Any]:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, dtype=torch.bfloat16, low_cpu_mem_usage=True
    ).eval()
    if device != "cpu":
        model = model.to(device)
    return model, tok


def _split(probes: list, test_frac: float, seed: int) -> tuple[list, list]:
    """Per-combinator calib/test split (stratified)."""
    rng = np.random.default_rng(seed)
    by_c: dict[str, list] = {}
    for p in probes:
        by_c.setdefault(p.combinator, []).append(p)
    calib, test = [], []
    for ps in by_c.values():
        idx = rng.permutation(len(ps))
        n_test = max(1, round(test_frac * len(ps)))
        test += [ps[i] for i in idx[:n_test]]
        calib += [ps[i] for i in idx[n_test:]]
    return calib, test


def _last_token_gate(
    model: Any, tok: Any, topo: T.ModelTopology, layers: list[int], prompt: str,
    register: str = "gate",
) -> dict[int, np.ndarray]:
    cap = C.capture_gate(model, tok, prompt, topo=topo, layers=layers,
                         register=register)
    return {li: cap.gate[li][-1] for li in layers}


def _true_label_best_z(res: Any, crystal: set[int], label: str) -> float:
    """Max z assigned to the TRUE label across crystal-bearing layers."""
    best = -np.inf
    for li, zmap in res.per_layer.items():
        if li in crystal and label in zmap:
            best = max(best, zmap[label])
    return float(best) if best != -np.inf else float("nan")


def measure(
    model: Any, tok: Any, topo: T.ModelTopology, layers: list[int],
    test_frac: float, n_perm: int, z_thresh: float, seed: int,
    shuffle_labels: bool = False, register: str = "gate",
) -> dict:
    from verbum.probes.library import crystal_probes

    probes = [p for p in crystal_probes() if p.combinator in CRYSTAL]
    calib, test = _split(probes, test_frac, seed)
    print(f"[vis] register={register} calib={len(calib)} test={len(test)} "
          f"(shuffle_labels={shuffle_labels})")

    # calibrate on calib (last-token gate) + natural-text null
    gate_by_layer: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    labels: list[str] = []
    for i, p in enumerate(calib):
        if i % 100 == 0:
            print(f"[vis]   calib probe {i}/{len(calib)}")
        g = _last_token_gate(model, tok, topo, layers, p.prompt, register)
        for li in layers:
            gate_by_layer[li].append(g[li])
        labels.append(p.combinator)
    lab = np.array(labels)
    if shuffle_labels:
        lab = np.random.default_rng(seed).permutation(lab)
    gate_np = {li: np.stack(gate_by_layer[li]) for li in layers}

    null_by_layer: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    for s in NULL_SENTENCES:
        cap = C.capture_gate(model, tok, s, topo=topo, layers=layers,
                             register=register)
        for li in layers:
            null_by_layer[li].append(cap.gate[li])
    null_np = {li: np.concatenate(null_by_layer[li]) for li in layers}

    rcc = RelationalCrystalClassifier(
        layers, n_perm=n_perm, z_thresh=z_thresh, sil_z_thresh=2.0,
        consensus_gram="auto",
    )
    rcc.calibrate(gate_np, lab, null_gate_by_layer=null_np)
    crystal = set(rcc.crystal_layers)

    # classify each test probe
    per_c: dict[str, dict] = {
        c: {"n": 0, "correct": 0, "noop": 0, "best_z": [], "confusion": Counter()}
        for c in CRYSTAL
    }
    for i, p in enumerate(test):
        if i % 100 == 0:
            print(f"[vis]   test probe {i}/{len(test)}")
        g = _last_token_gate(model, tok, topo, layers, p.prompt, register)
        res = rcc.classify(g)
        c = p.combinator
        d = per_c[c]
        d["n"] += 1
        d["best_z"].append(_true_label_best_z(res, crystal, c))
        if res.dominant == "·":
            d["noop"] += 1
        else:
            if res.dominant == c:
                d["correct"] += 1
            d["confusion"][res.dominant] += 1

    rows = []
    for c in CRYSTAL:
        d = per_c[c]
        n = d["n"] or 1
        bz = [z for z in d["best_z"] if not np.isnan(z)]
        top_conf = d["confusion"].most_common(1)
        rows.append({
            "combinator": c, "n": d["n"],
            "self_acc": round(d["correct"] / n, 3),
            "noop_rate": round(d["noop"] / n, 3),
            "mean_best_z": round(float(np.mean(bz)), 2) if bz else None,
            "top_confusion": (top_conf[0][0] if top_conf else None),
        })
    return {
        "n_calib": len(calib), "n_test": len(test),
        "n_crystal_layers": len(crystal), "n_layers": topo.n_layers,
        "z_thresh": z_thresh, "shuffle_labels": shuffle_labels,
        "rows": rows,
    }


def _print(res: dict, title: str) -> None:
    print("=" * 72)
    print(title)
    print(f"crystal layers {res['n_crystal_layers']}/{res['n_layers']}  "
          f"calib={res['n_calib']} test={res['n_test']}  z>{res['z_thresh']}")
    print(f"{'op':>5} {'n':>4} {'self_acc':>9} {'noop':>7} {'best_z':>7}  confusion")
    print("-" * 60)
    for r in res["rows"]:
        print(f"{r['combinator']:>5} {r['n']:>4} {r['self_acc']:>9} "
              f"{r['noop_rate']:>7} {r['mean_best_z']!s:>7}  "
              f"-> {r['top_confusion']}")
    print("=" * 72)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Per-combinator routing-register visibility")
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="cpu", choices=["cpu", "mps", "cuda"])
    ap.add_argument("--test-frac", type=float, default=0.3)
    ap.add_argument("--n-perm", type=int, default=200)
    ap.add_argument("--z", type=float, default=3.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--register", default="gate", choices=["gate", "attn"],
                    help="gate=FFN routing (K/I/S/Y...); attn=o_proj (composition B/C)")
    ap.add_argument("--with-null", action="store_true",
                    help="also run a shuffled-label control (chance anchor)")
    args = ap.parse_args()

    t0 = time.time()
    model, tok = _load(args.model, args.device)
    topo = T.detect_topology(model, model.config)
    print(f"[vis] {topo.summary()}")
    layers = list(range(topo.n_layers))

    reg = args.register
    reg_desc = topo.read_register if reg == "gate" else f"sign({topo.attn_suffix})"
    real = measure(model, tok, topo, layers, args.test_frac, args.n_perm,
                   args.z, args.seed, register=reg)
    _print(real, f"REGISTER VISIBILITY — {args.model}  [{reg}: {reg_desc}]")

    out: dict = {"model": args.model, "device": args.device, "register": reg,
                 "read_register": reg_desc, "real": real}
    if args.with_null:
        null = measure(model, tok, topo, layers, args.test_frac, args.n_perm,
                       args.z, args.seed, shuffle_labels=True, register=reg)
        _print(null, "SHUFFLED-LABEL CONTROL (chance anchor)")
        out["shuffled"] = null

    out["elapsed_s"] = round(time.time() - t0, 1)
    out["timestamp_utc"] = datetime.now(UTC).isoformat()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = args.model.split("/")[-1].lower().replace(".", "-")
    path = RESULTS_DIR / f"{slug}_{reg}_{args.device}.json"
    path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"[vis] wrote {path}  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
