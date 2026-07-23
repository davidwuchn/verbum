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
  7. **projector** (optional, ``--jspace-projector``) the FULL J-space
     construction (``projector.py``, s270 — closes the s269 projection gap):
     consensus Jacobian-row-space bases at quartile depths, residual-space
     combinator centroids (no ``W_gate^T`` pullback), per-combinator
     workspace fractions + matched-random + shuffled-label gates, and
     verbalization of the basis directions themselves. Sidecar observable:
     never feeds the classifier, not gated into the VSM tree.

     PRE-REGISTERED (s270, before any 27B/sweep data):
       P1  workspace-fraction ordering: content/process vertices {Y, WHNF, S}
           > operator vertices {K, I, B} (E4 s269e restated geometrically);
           gate = shuffled-label partition null on the mean gap.
       P2  some J-space basis directions verbalize coherently (Anthropic's
           core claim replicated on our stack); WHNF-adjacent vocabulary is
           the specific watch (the nameless bus-causal vertex, s269f).
       P3  the 9-vector of fractions is stable across models (the sector
           decomposition is universal, not a 27B fact) — read at sweep time.

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
import projector as P  # noqa: E402
import topology as T  # noqa: E402
from classify import (  # noqa: E402
    CRYSTAL,
    RelationalCrystalClassifier,
    measure_null_floor,
    register_node,
)
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
    return rcc, summ, (feat_np, labels_np, null_np)


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


# P1 sets (pre-registered from s269e E4: identity-specific bus coupling vs
# collapse-to-generic; C excluded = open puzzle, D excluded = lexically
# visible but coupling-generic — both reported, neither gates P1)
JSPACE_CONTENT_OPS = ["Y", "WHNF", "S"]
JSPACE_OPERATOR_OPS = ["K", "I", "B"]


def _balanced_subsets(
    probes: list, n_proj: int, n_cent: int
) -> tuple[list, list]:
    """Disjoint balanced probe subsets: projector prompts vs centroid prompts.

    Disjoint so the basis is never fit on the prompts it is measured with.
    """
    by_comb: dict[str, list] = {}
    for p in probes:
        by_comb.setdefault(p.combinator, []).append(p)
    proj, cent = [], []
    for c in CRYSTAL:
        pool = by_comb.get(c, [])
        proj.extend(pool[:n_proj])
        cent.extend(pool[n_proj : n_proj + n_cent])
    return proj, cent


def jspace_projector_step(
    model: Any,
    tok: Any,
    topo: T.ModelTopology,
    *,
    k: int,
    depths: list[float],
    proj_ppc: int,
    cent_ppc: int,
    eps_rel: float,
    n_shuffle: int,
    batch_size: int = 8,
    seed: int = 270,
) -> dict:
    """Full J-space projector sidecar (docstring step 7). Never feeds the
    classifier; not gated into the VSM tree (S3: observe first)."""
    rng = np.random.default_rng(seed)
    target_layer = topo.n_layers - 2
    layers = sorted({
        min(max(round(f * topo.n_layers), 0), target_layer - 1)
        for f in depths
    })
    proj_probes, cent_probes = _balanced_subsets(
        [p for p in crystal_probes() if p.combinator in CRYSTAL],
        proj_ppc, cent_ppc,
    )
    print(f"[trace] [jspace] bases at layers {layers} (target L{target_layer}) "
          f"from {len(proj_probes)} prompts, k={k}, m={2*k} ...")
    bases = P.jspace_bases(
        model, tok, [p.prompt for p in proj_probes],
        layers=layers, target_layer=target_layer, k=k,
        refine=True, eps_rel=eps_rel, topo=topo,
        batch_size=batch_size, seed=seed,
    )
    print(f"[trace] [jspace] residual centroids from {len(cent_probes)} "
          f"disjoint prompts ...")
    centroids, centered = P.capture_residual_centroids(
        model, tok,
        [p.prompt for p in cent_probes],
        [p.combinator for p in cent_probes],
        layers=layers, topo=topo, batch_size=batch_size,
    )
    labels = np.array([p.combinator for p in cent_probes])

    per_layer: dict[str, dict] = {}
    for li in layers:
        basis = bases[li]
        v = basis.basis  # [k, d]
        fracs = {c: P.workspace_fraction(v, mu)
                 for c, mu in centroids[li].items()}
        # per-probe dispersion
        proj_states = centered[li] @ v.T.astype(np.float64)  # [N, k]
        e_in = (proj_states ** 2).sum(axis=1)
        e_all = (centered[li].astype(np.float64) ** 2).sum(axis=1)
        pf = e_in / np.maximum(e_all, 1e-30)
        per_probe = {
            c: {
                "mean": float(pf[labels == c].mean()),
                "sd": float(pf[labels == c].std()),
                "n": int((labels == c).sum()),
            }
            for c in sorted(set(labels))
        }
        # matched-random baseline (E[fraction] = k/d for generic directions)
        rf = P.random_vector_fractions(v, n=200, rng=rng)
        # P1: content-minus-operator centroid-fraction gap vs shuffled labels
        def _gap(lab: np.ndarray, vv: np.ndarray, states: np.ndarray) -> float:
            f = {c: P.workspace_fraction(vv, states[lab == c].mean(axis=0))
                 for c in CRYSTAL}
            return (float(np.mean([f[c] for c in JSPACE_CONTENT_OPS]))
                    - float(np.mean([f[c] for c in JSPACE_OPERATOR_OPS])))
        obs = _gap(labels, v, centered[li])
        null = np.array([_gap(rng.permutation(labels), v, centered[li])
                         for _ in range(n_shuffle)])
        z = float((obs - null.mean()) / max(null.std(), 1e-12))
        pval = float((1 + (null >= obs).sum()) / (1 + n_shuffle))
        # P2: verbalize the basis directions themselves (no pullback map)
        verb = []
        for i in range(min(10, v.shape[0])):
            verb.append({
                "dir": i,
                "strength": float(basis.strengths[i]),
                "plus": J.verbalize(model, tok, v[i], topo=topo, top_k=8),
                "minus": J.verbalize(model, tok, -v[i], topo=topo, top_k=8),
            })
        per_layer[str(li)] = {
            "strengths": [float(s) for s in basis.strengths],
            "fractions": {c: round(f, 6) for c, f in sorted(fracs.items())},
            "per_probe": per_probe,
            "random_baseline": {
                "mean": float(rf.mean()), "sd": float(rf.std()),
                "k_over_d": basis.k / basis.d,
            },
            "p1_gap": {
                "observed": round(obs, 6),
                "null_mean": float(null.mean()), "null_sd": float(null.std()),
                "z": round(z, 3), "p": round(pval, 5),
                "gated": bool(pval < 0.05 and obs > 0),
            },
            "verbalize": verb,
        }
        print(f"[trace] [jspace] L{li}: P1 gap={obs:+.4f} z={z:+.2f} "
              f"p={pval:.4f} gated={per_layer[str(li)]['p1_gap']['gated']} "
              f"| rand≈{rf.mean():.4f} (k/d={basis.k / basis.d:.4f})")

    return {
        "k": k, "m": 2 * k, "target_layer": target_layer,
        "depth_layers": layers, "depths": depths,
        "eps_rel": eps_rel, "seed": seed, "n_shuffle": n_shuffle,
        "proj_probes_per_comb": proj_ppc,
        "centroid_probes_per_comb": cent_ppc,
        "content_set": JSPACE_CONTENT_OPS,
        "operator_set": JSPACE_OPERATOR_OPS,
        "honest_scope": (
            "sidecar observable; never feeds the opcode classifier; "
            "not gated into the VSM tree (s263 discipline)"
        ),
        "preregistrations": {
            "P1": "fraction(Y,WHNF,S) > fraction(K,I,B); shuffled-label gate",
            "P2": "basis directions verbalize coherently; WHNF-adjacent watch",
            "P3": "9-vector stable across models (read at sweep restack)",
        },
        "layers": per_layer,
    }


def build_model_vsm(
    model_name: str,
    topo: T.ModelTopology,
    calibrated: dict[str, RelationalCrystalClassifier],
    floors: dict[str, dict],
) -> VSMNode:
    """Stack the calibrated registers into the model-VSM node.

    ``floors[reg]`` = measured shuffled-label floor (``measure_null_floor``);
    its ``null_floor_z`` fills the register node's health slot and propagates
    up the tree as the worst child (a caveat never vanishes by aggregation).
    """
    regs = []
    for reg_name, rcc in calibrated.items():
        floor = floors.get(reg_name) or {}
        regs.append(
            register_node(
                rcc,
                reg_name,
                null_floor_z=floor.get("null_floor_z", float("nan")),
                meta={
                    "read_register": (
                        topo.read_register if reg_name == "gate"
                        else f"sign({topo.attn_suffix}) [attn write]"
                    ),
                    "null_floor": floor,
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
    ap.add_argument("--jspace-projector", action="store_true",
                    help="add the FULL J-space projector sidecar (step 7)")
    ap.add_argument("--jspace-k", type=int, default=32)
    ap.add_argument("--jspace-depths", default="0.25,0.5,0.75")
    ap.add_argument("--jspace-proj-ppc", type=int, default=3,
                    help="projector prompts per combinator")
    ap.add_argument("--jspace-cent-ppc", type=int, default=12,
                    help="centroid prompts per combinator (disjoint set)")
    ap.add_argument("--jspace-eps-rel", type=float, default=0.02,
                    help="FD injection scale (0.02 tuned for bf16)")
    ap.add_argument("--jspace-shuffles", type=int, default=1000)
    ap.add_argument("--null-floor-shuffles", type=int, default=3,
                    help="shuffled-label floor recalibrations per register "
                         "(0 = skip; fills null_floor_z in the tree)")
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
    floors: dict[str, dict] = {}
    for reg in registers:
        rcc, summ, (feat_np, labels_np, null_np) = calibrate_register(
            model, tok, topo, reg, layers, ppc, n_perm, args.z
        )
        calibrated[reg] = rcc
        calib_summ[reg] = summ
        print(f"[trace] [{reg}] crystal-bearing layers: "
              f"{len(summ['crystal_layers'])}/{topo.n_layers}")
        if args.null_floor_shuffles > 0:
            print(f"[trace] [{reg}] shuffled-label null floor "
                  f"({args.null_floor_shuffles} shuffles) ...")
            floor = measure_null_floor(
                feat_np, labels_np, layers,
                n_shuffles=args.null_floor_shuffles,
                n_perm=max(120, n_perm // 2),
                null_gate_by_layer=null_np,
            )
            floors[reg] = floor
            summ["null_floor"] = floor
            mark = " ⚠ SUSPECT" if floor["suspect"] else ""
            print(f"[trace] [{reg}] null_floor_z={floor['null_floor_z']} "
                  f"(ref~1.64) shuffled_bearing="
                  f"{floor['shuffled_bearing_frac']}{mark}")
        traces[reg] = trace_register(model, tok, topo, reg, rcc, layers, args.z)

    mvsm = build_model_vsm(args.model, topo, calibrated, floors)

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

    jspace_proj = None
    if args.jspace_projector:
        jspace_proj = jspace_projector_step(
            model, tok, topo,
            k=8 if args.smoke else args.jspace_k,
            depths=[float(x) for x in args.jspace_depths.split(",")],
            proj_ppc=2 if args.smoke else args.jspace_proj_ppc,
            cent_ppc=4 if args.smoke else args.jspace_cent_ppc,
            eps_rel=args.jspace_eps_rel,
            n_shuffle=200 if args.smoke else args.jspace_shuffles,
        )
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
    if jspace_proj is not None:
        (out_dir / "jspace_projector.json").write_text(
            json.dumps(jspace_proj, indent=2, default=str), encoding="utf-8"
        )
        print(f"[trace] wrote {out_dir}/jspace_projector.json")
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
        "jspace_projector": ("jspace_projector.json" if jspace_proj else None),
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
