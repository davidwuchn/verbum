#!/usr/bin/env python3
"""End-to-end opcode trace — detect → capture → calibrate → classify → tree.

The whole pipeline, architecture-agnostic, wired together:

  1. **detect**    ``topology.detect_topology`` finds the routing register(s).
  2. **capture**   ``capture.capture_gate`` reads per-layer features for each
     available register: ``gate`` (FFN routing — selection/share/recursion)
     and ``attn`` (attention write — rescues D; s264 register decomposition).
  3. **calibrate** per register: ``RelationalCrystalClassifier`` on the bundled
     crystal probes against a natural-text null → per-layer crystal lattice.
  4. **tree**      each calibration becomes a register-level VSM node; the
     registers stack into the **model-VSM** (``vsm.py``) — the unit that
     family/root trees are built from. Written next to the trace results.
  5. **classify**  per-token per-layer opcode read per register → trajectories
     (the C→B program), null-gated so non-combinator tokens NO-OP.
  6. **operand**   (optional, ``--operand``) J-space logit-lens column: WHAT
     is being routed at the last crystal-bearing layer, per token. Honest
     scope (s263): the operand register never feeds the opcode classifier.

Single-register blindness is structural, not a bug to hide (s264 finding 3:
gate sees {K,I,S,Y,WHNF}, attn-write rescues D, neither resolves {B,C}) — so
the trace reports per-register trajectories side by side, and the model-VSM
holds both registers as sibling children.

No architecture is hard-coded: swap ``--model`` and the same code runs (Qwen
dense, Gemma composite, Qwen3.6 hybrid, GPT-NeoX up-proj proxy). MoE gate is
refused at detect time; its attn register still traces.

Usage:
    uv run python opcodes/trace.py --model Qwen/Qwen3-0.6B --smoke
    uv run python opcodes/trace.py --model Qwen/Qwen3.6-27B --device mps
    uv run python opcodes/trace.py --model Qwen/Qwen3-0.6B --operand

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
import jspace as J  # noqa: E402
import topology as T  # noqa: E402
from classify import CRYSTAL, RelationalCrystalClassifier, register_node  # noqa: E402
from probes import crystal_probes  # noqa: E402
from vsm import VSMNode, save_tree, stack  # noqa: E402

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

# register-level caveats recorded into the tree (worst-child propagation)
REGISTER_NOTES = {
    "gate": {},
    "attn": {
        "caveat": (
            "elevated shuffled-label null floor vs gate (s264): be "
            "conservative on weak attn signals"
        ),
    },
}


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


def calibrate_register(
    model: Any,
    tok: Any,
    topo: T.ModelTopology,
    register: str,
    layers: list[int],
    probes_per_comb: int | None,
    n_perm: int,
    z_thresh: float,
) -> tuple[RelationalCrystalClassifier, dict]:
    """Calibrate the classifier on one register's captured features."""
    probes = [p for p in crystal_probes() if p.combinator in CRYSTAL]
    if probes_per_comb is not None:
        kept, counts = [], Counter()
        for p in probes:
            if counts[p.combinator] < probes_per_comb:
                kept.append(p)
                counts[p.combinator] += 1
        probes = kept
    print(f"[trace] [{register}] calibrating on {len(probes)} crystal probes ...")

    feat: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    labels: list[str] = []
    for i, p in enumerate(probes):
        if i % 100 == 0:
            print(f"[trace] [{register}]   probe {i}/{len(probes)}")
        cap = C.capture_gate(
            model, tok, p.prompt, topo=topo, layers=layers, register=register
        )
        for li in layers:
            feat[li].append(cap.gate[li][-1])  # last-token crystal locus
        labels.append(p.combinator)
    feat_np = {li: np.stack(feat[li]) for li in layers}
    labels_np = np.array(labels)

    print(f"[trace] [{register}] null from {len(NULL_SENTENCES)} natural prompts ...")
    null: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    for s in NULL_SENTENCES:
        cap = C.capture_gate(
            model, tok, s, topo=topo, layers=layers, register=register
        )
        for li in layers:
            null[li].append(cap.gate[li])  # all positions
    null_np = {li: np.concatenate(null[li]) for li in layers}

    rcc = RelationalCrystalClassifier(
        layers, n_perm=n_perm, z_thresh=z_thresh, sil_z_thresh=2.0,
        consensus_gram="auto",
    )
    rcc.calibrate(feat_np, labels_np, null_gate_by_layer=null_np)
    summ = rcc.calibration_summary()
    summ["register"] = register
    summ["n_probes"] = len(probes)
    summ["n_null_tokens"] = int(next(iter(null_np.values())).shape[0])
    return rcc, summ


def trace_register(
    model: Any,
    tok: Any,
    topo: T.ModelTopology,
    register: str,
    rcc: RelationalCrystalClassifier,
    layers: list[int],
    z_thresh: float,
) -> dict:
    """Per-token per-layer opcode read for one register → trajectory."""
    crystal = set(rcc.crystal_layers)
    layer_votes: dict[int, Counter] = {li: Counter() for li in layers}
    n_tokens = token_noop = 0
    for prompt in LAMBDA_SENTENCES:
        cap = C.capture_gate(
            model, tok, prompt, topo=topo, layers=layers, register=register
        )
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
        "register": register,
        "n_tokens": n_tokens,
        "token_noop_rate": round(token_noop / n_tokens, 4) if n_tokens else 0.0,
        "crystal_layers": sorted(crystal),
        "trajectory": trajectory,
        "C_layers": c_layers, "B_layers": b_layers,
        "C_before_B": bool(c_layers and b_layers
                           and float(np.mean(c_layers)) < float(np.mean(b_layers))),
    }


def operand_column(
    model: Any,
    tok: Any,
    topo: T.ModelTopology,
    read_layer: int,
    *,
    top_k: int = 3,
) -> list[dict]:
    """J-space operand read: per token, WHAT the residual points toward at
    ``read_layer`` (typically the last crystal-bearing layer). Display-only —
    never feeds the opcode classifier (s263)."""
    rows = []
    for prompt in LAMBDA_SENTENCES:
        resids = J.capture_residuals(
            model, tok, prompt, topo=topo, layers=[read_layer]
        )
        ids = tok(prompt)["input_ids"]
        toks = [tok.decode([t]) for t in ids]
        per_tok = [
            J.verbalize_state(
                model, tok, resids[read_layer][pos], topo=topo, top_k=top_k
            )
            for pos in range(len(toks))
        ]
        rows.append({"prompt": prompt, "tokens": toks, "operand": per_tok})
    return rows


def build_model_vsm(
    model_name: str,
    topo: T.ModelTopology,
    calibrated: dict[str, RelationalCrystalClassifier],
) -> VSMNode:
    """Stack the calibrated registers into the model-VSM node."""
    regs = []
    for reg_name, rcc in calibrated.items():
        regs.append(
            register_node(
                rcc,
                reg_name,
                meta={
                    "read_register": (
                        topo.read_register if reg_name == "gate"
                        else f"sign({topo.attn_suffix}) [attn write]"
                    ),
                    **REGISTER_NOTES.get(reg_name, {}),
                },
            )
        )
    ref = next(iter(calibrated.values())).consensus_gram
    return stack(
        regs,
        level="model",
        name=model_name,
        reference_gram=ref,
        meta={
            "arch": topo.arch,
            "n_layers": topo.n_layers,
            "layers_path": topo.layers_path,
            "register_kind": topo.register,
        },
    )


def main() -> None:
    ap = argparse.ArgumentParser(
        description="End-to-end arch-agnostic two-register opcode trace"
    )
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="cpu", choices=["cpu", "mps", "cuda"])
    ap.add_argument("--probes-per-comb", type=int, default=None)
    ap.add_argument("--n-perm", type=int, default=300)
    ap.add_argument("--z", type=float, default=3.0)
    ap.add_argument("--registers", default="gate,attn",
                    help="comma list from {gate,attn} (default both)")
    ap.add_argument("--operand", action="store_true",
                    help="add the J-space logit-lens operand column")
    ap.add_argument("--smoke", action="store_true",
                    help="15 probes/comb, n_perm=120 (fast pipeline check)")
    args = ap.parse_args()
    ppc = 15 if args.smoke else args.probes_per_comb
    n_perm = 120 if args.smoke else args.n_perm
    want = [r.strip() for r in args.registers.split(",") if r.strip()]

    model, tok = load(args.model, args.device)
    topo = T.detect_topology(model, model.config)
    print(f"[trace] {topo.summary()}")

    registers = []
    for r in want:
        if r == "gate":
            if topo.traceable:
                registers.append(r)
            else:
                print(f"[trace] gate register unavailable "
                      f"({topo.read_register}); skipping.")
        elif r == "attn":
            if topo.attn_traceable:
                registers.append(r)
            else:
                print("[trace] attn register unavailable; skipping.")
        else:
            raise SystemExit(f"unknown register {r!r}")
    if not registers:
        print(f"[trace] REFUSED: no traceable register on {topo.arch}.")
        for n in topo.notes:
            print(f"[trace]   · {n}")
        sys.exit(2)

    layers = list(range(topo.n_layers))
    t0 = time.time()
    calibrated: dict[str, RelationalCrystalClassifier] = {}
    calib_summ: dict[str, dict] = {}
    traces: dict[str, dict] = {}
    for reg in registers:
        rcc, summ = calibrate_register(
            model, tok, topo, reg, layers, ppc, n_perm, args.z
        )
        calibrated[reg] = rcc
        calib_summ[reg] = summ
        print(f"[trace] [{reg}] crystal-bearing layers: "
              f"{len(summ['crystal_layers'])}/{topo.n_layers}")
        traces[reg] = trace_register(model, tok, topo, reg, rcc, layers, args.z)

    mvsm = build_model_vsm(args.model, topo, calibrated)

    operand = None
    if args.operand:
        # read at the last gate-register crystal-bearing layer (or mid-stack)
        gate_crystal = traces.get("gate", {}).get("crystal_layers", [])
        read_layer = gate_crystal[-1] if gate_crystal else topo.n_layers // 2
        print(f"[trace] operand column at layer {read_layer} ...")
        operand = {
            "read_layer": read_layer,
            "rows": operand_column(model, tok, topo, read_layer),
        }
    elapsed = time.time() - t0

    print("=" * 72)
    print(f"OPCODE TRACE — {args.model}")
    print("=" * 72)
    print(mvsm.summary())
    for reg, tr in traces.items():
        print(f"-- {reg} [{calib_summ[reg]['register']}] "
              f"crystal={len(tr['crystal_layers'])}/{topo.n_layers} "
              f"noop={tr['token_noop_rate']} C_before_B={tr['C_before_B']}")
        for t in tr["trajectory"]:
            bar = "#" * int(20 * t["votes"] / max(1, t["total"]))
            print(f"  L{t['layer']:>3}  {t['op']:>4}  "
                  f"{t['votes']:>3}/{t['total']:<3} {bar}")
    print("=" * 72)

    slug = args.model.split("/")[-1].lower().replace(".", "-")
    out_dir = RESULTS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    save_tree(mvsm, out_dir / "model_vsm")
    out = {
        "model": args.model, "device": args.device,
        "topology": {
            "arch": topo.arch, "register": topo.register,
            "read_register": topo.read_register,
            "layers_path": topo.layers_path,
            "gate_suffix": topo.gate_suffix, "gate_width": topo.gate_width,
            "attn_suffix": topo.attn_suffix, "attn_width": topo.attn_width,
            "n_layers": topo.n_layers,
        },
        "registers": registers,
        "calibration": calib_summ,
        "traces": traces,
        "operand": operand,
        "elapsed_s": round(elapsed, 1),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "smoke": args.smoke, "probes_per_comb": ppc, "n_perm": n_perm,
    }
    (out_dir / "trace.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8"
    )
    print(f"[trace] wrote {out_dir}/trace.json + model_vsm.json ({elapsed:.1f}s)")


if __name__ == "__main__":
    main()
