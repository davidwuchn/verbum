#!/usr/bin/env python3
# register: topological/routing
"""Opcode Monitor v2 — recover the compose-arc without reopening the over-read (s231).

s231 (a) BUILT + VALIDATED the over-read killer: RelationalCrystalClassifier no-ops
retrieval (the raw-argmax tracer fired an opcode for 100% of tokens = common-mode).
BUT it OVER-CORRECTED -> UNDER-read: the RAW per-layer traces showed a consistent
C->B compose-arc across ALL 5 lambda prompts (C in L2-12, B in L13-33 = the real s127
compose signature, task-specific not common-mode) and the relational reader at z=3,
last-token no-opped it entirely.

Two diagnosed causes (vsm-opcode-monitor.md §v2), both fixed here:

  1. NULL mis-spec (the KEY fix) — the off-target null was OTHER crystal probes, all
     lambda-mode, so "looks more like B than K/I/C?" had low power. v2 builds a
     CROSS-TASK null from a NON-combinator baseline (bare natural-text tokens, no
     β-reduction). Then "lambda token looks like B vs a natural-text token" clears,
     while retrieval (also natural-text mode) stays silent. (relational_opcode.py
     calibrate(..., null_gate_by_layer=...).)

  2. LAST-TOKEN locus (s227 wrong-locus) — a sentence's final token isn't one opcode;
     the program unfolds across tokens. v2 reads PER-TOKEN across the sequence and
     aggregates a PER-LAYER TRAJECTORY (the C→B program), not a single dominant op.

Plus a z-threshold sweep (z∈{2,3}; z is threshold-independent so swept post-hoc).

CONDITIONS (the only variable across the read is the SENTENCE CONTENT; gate held where
noted):
  • LAMBDA      = COMPILE_GATE + s127 compositional sentences (quantifiers / conditional
                  / relative clause)  → content positions  → expect the C→B arc.
  • GATE_NEUTRAL= COMPILE_GATE + non-compositional declaratives → content positions →
                  the GATE-CONFOUND CONTROL: if it ALSO fires the arc, the arc is
                  gate-driven; if it stays quiet while LAMBDA fires, it is composition-
                  driven (the load-bearing control, λ measure).
  • RETRIEVAL   = bare fact-lookup prompts → all positions → SILENCE GUARD (the
                  over-read must stay killed; held out from the null prompts).
  • ARITHMETIC  = bare arithmetic prompts → all positions → secondary (selection mode).

CROSS-TASK NULL = bare BASELINE_NULL natural-text tokens (no gate, no computation).
CAVEAT (λ measure, recorded): LAMBDA carries the COMPILE_GATE prefix; the null/guards
are bare. Part of any LAMBDA elevation could be the gate-mode shift rather than
β-reduction per se. GATE_NEUTRAL is the direct control for this; the s231 validation
also showed bare retrieval routes W (gauge) not C->B, i.e. the arc is task-specific.

Usage:
    uv run python scripts/experiments/opcode_monitor_v2.py
    uv run python scripts/experiments/opcode_monitor_v2.py --smoke
    uv run python scripts/experiments/opcode_monitor_v2.py --model Qwen/Qwen3-8B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

# ── project root and classifier import ────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from relational_opcode import CRYSTAL, RelationalCrystalClassifier  # noqa: E402

# ── constants ─────────────────────────────────────────────────────────────────
RESULTS_DIR = _ROOT / "results" / "opcode-monitor-v2"
COMPILE_GATE = (_ROOT / "gates" / "compile.txt").read_text(encoding="utf-8")
Z_SWEEP = [2.0, 3.0]
# readable register (readout-register-reduction-readability.md): reduction becomes
# vocab-readable at depth >= ~0.6; the C-late composition signal lives here (s232 v3).
READABLE_FRAC = 0.6

# LAMBDA signal — s127 compositional sentences (gate-prefixed, content read)
LAMBDA_SENTENCES = [
    "The dog runs.",
    "Every student reads a book.",
    "If it rains, the ground is wet.",
    "No bird can swim.",
    "Mary likes the cat that John owns.",
]

# GATE-CONFOUND CONTROL — gate + non-compositional declaratives (content read).
# Also serves as the MATCHED-PREFIX NULL under --null-mode gateneutral (the v3 lever:
# composition-ABOVE-FRAMING). Expanded to ~14 for a robust null (~70+ content tokens).
GATE_NEUTRAL_SENTENCES = [
    "The sky is blue.",
    "Coffee is a drink.",
    "The house is old.",
    "The city is large.",
    "The book is heavy.",
    "The water is cold.",
    "The road is long.",
    "The lamp is bright.",
    "The chair is wooden.",
    "The bread is fresh.",
    "The river is wide.",
    "The mountain is tall.",
    "The garden is green.",
    "The window is open.",
]

# RETRIEVAL silence guard — bare fact-lookup (held out from the null)
RETRIEVAL_PROMPTS = [
    "The capital of France is",
    "The author of Hamlet is",
    "Water is made of hydrogen and",
    "The largest planet is",
    "The first president of the United States was",
]

# ARITHMETIC secondary — bare
ARITHMETIC_PROMPTS = [
    "2 + 3 =",
    "7 * 8 =",
    "15 - 4 =",
    "Compute 12 + 27.",
    "What is 9 times 6?",
]

# CROSS-TASK NULL baseline — bare natural text, no computation, no lists/quantifiers
BASELINE_NULL_SENTENCES = [
    "The sky was clear this morning.",
    "She walked to the store yesterday.",
    "Music played softly in the room.",
    "The old house stood on the hill.",
    "He drinks coffee every morning.",
    "Rain fell throughout the night.",
    "The garden was full of color.",
    "They watched a film last weekend.",
    "A gentle breeze moved the curtains.",
    "The city lights glowed at dusk.",
    "Children played outside in the sun.",
    "The train arrived a little late.",
]


# ═══════════════════════════════════════════════════════════════════════════════
# Gate-capture hook (ALL token positions — the per-token fix)
# ═══════════════════════════════════════════════════════════════════════════════
def _make_hook(store: dict[int, np.ndarray], layer_idx: int):
    """Forward hook: capture the WHOLE gate_proj output [T, d] as float64 CPU."""

    def _hook(_module, _inp, out):
        # out: [B, T, intermediate_size] — keep all positions
        vec = out[0, :, :].detach().float().cpu().numpy()
        store[layer_idx] = vec.astype(np.float64)

    return _hook


# ═══════════════════════════════════════════════════════════════════════════════
# Model loader + forward runner
# ═══════════════════════════════════════════════════════════════════════════════
def load_model_and_tokenizer(model_name: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[v2] Loading tokenizer: {model_name}")
    tok = AutoTokenizer.from_pretrained(model_name)
    print(f"[v2] Loading model: {model_name}  (dtype=auto, device_map=auto)")
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype="auto", device_map="auto"
    )
    model.eval()
    print(f"[v2] Model loaded in {time.time()-t0:.1f}s")
    return model, tok, torch


def forward_all_positions(
    prompt: str, model, tok, torch_mod, layers: list[int]
) -> tuple[dict[int, np.ndarray], int]:
    """Run one prompt forward; return ({li: gate [T, d]}, n_tokens)."""
    store: dict[int, np.ndarray] = {}
    handles = []
    for li in layers:
        h = model.model.layers[li].mlp.gate_proj.register_forward_hook(
            _make_hook(store, li)
        )
        handles.append(h)
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            model(**inputs)
    finally:
        for h in handles:
            h.remove()
    n_tokens = int(inputs["input_ids"].shape[1])
    return store, n_tokens


def gate_prefix_len(tok) -> int:
    """Number of tokens the COMPILE_GATE prefix occupies (content start index)."""
    return len(tok(COMPILE_GATE)["input_ids"])


# ═══════════════════════════════════════════════════════════════════════════════
# Calibration: crystal centroids (last token) + cross-task null (baseline tokens)
# ═══════════════════════════════════════════════════════════════════════════════
def calibrate_v2(
    model, tok, torch_mod, layers: list[int], n_perm: int,
    probes_per_combinator: int | None, null_positions_cap: int | None,
    null_mode: str = "crosstask",
) -> tuple[RelationalCrystalClassifier, dict]:
    """null_mode:
      - "crosstask"   (s232): null = bare natural-text tokens (all positions). Removes
        the natural-text common-mode; the gate-FRAMING (S-late) survives, swamps comp.
      - "gateneutral" (s232 v3 lever): null = GATE_NEUTRAL CONTENT tokens (gate +
        non-compositional sentence, content positions). MATCHED-PREFIX null => z is
        composition-ABOVE-FRAMING (the framing S-late is subtracted)."""
    from verbum.probes.library import crystal_probes

    probes = [p for p in crystal_probes() if p.combinator in CRYSTAL]
    if probes_per_combinator is not None:
        kept, counts = [], Counter()
        for p in probes:
            if counts[p.combinator] < probes_per_combinator:
                kept.append(p)
                counts[p.combinator] += 1
        probes = kept
    print(f"[v2] Crystal probes (last-token centroids): {len(probes)}")

    gate_by_layer: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    labels: list[str] = []
    for i, p in enumerate(probes):
        if i % 50 == 0:
            print(f"[v2]   centroid forward {i}/{len(probes)} ...")
        store, _ = forward_all_positions(p.prompt, model, tok, torch_mod, layers)
        for li in layers:
            gate_by_layer[li].append(store[li][-1])  # last token = the crystal locus
        labels.append(p.combinator)  # type: ignore[arg-type]
    gate_np = {li: np.stack(gate_by_layer[li], axis=0) for li in layers}
    labels_np = np.array(labels)

    null_by_layer: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    if null_mode == "gateneutral":
        gate_n = gate_prefix_len(tok)
        print(f"[v2] Building MATCHED-PREFIX null from {len(GATE_NEUTRAL_SENTENCES)} "
              "gate+non-compositional prompts (content positions) ...")
        for s in GATE_NEUTRAL_SENTENCES:
            store, n = forward_all_positions(
                COMPILE_GATE + s, model, tok, torch_mod, layers)
            lo = min(gate_n, n - 1)
            for li in layers:
                null_by_layer[li].append(store[li][lo:])  # content tokens only
    else:  # crosstask
        print(f"[v2] Building cross-task null from {len(BASELINE_NULL_SENTENCES)} "
              "bare natural-text prompts ...")
        for s in BASELINE_NULL_SENTENCES:
            store, _n = forward_all_positions(s, model, tok, torch_mod, layers)
            for li in layers:
                null_by_layer[li].append(store[li])  # [T, d], all positions
    null_np = {li: np.concatenate(null_by_layer[li], axis=0) for li in layers}
    if null_positions_cap is not None:
        null_np = {li: arr[:null_positions_cap] for li, arr in null_np.items()}
    n_null = next(iter(null_np.values())).shape[0]
    print(f"[v2] Null tokens pooled: {n_null}  (null_mode={null_mode})")

    rcc = RelationalCrystalClassifier(
        layers, n_perm=n_perm, z_thresh=min(Z_SWEEP), sil_z_thresh=2.0,
        consensus_gram="auto",
    )
    rcc.calibrate(gate_np, labels_np, null_gate_by_layer=null_np)
    summ = rcc.calibration_summary()
    summ["n_null_tokens"] = n_null
    summ["n_centroid_probes"] = len(probes)
    summ["null_mode"] = null_mode
    return rcc, summ


# ═══════════════════════════════════════════════════════════════════════════════
# Per-token reading → reduce to per-layer (argmax-op, z) (threshold-independent)
# ═══════════════════════════════════════════════════════════════════════════════
def read_prompt_tokens(
    rcc: RelationalCrystalClassifier, store: dict[int, np.ndarray],
    layers: list[int], positions: list[int],
) -> list[dict[int, tuple[str, float]]]:
    """For each position, classify and reduce each layer to its argmax (op, z)."""
    reads: list[dict[int, tuple[str, float]]] = []
    for pos in positions:
        gate_tok = {li: store[li][pos] for li in layers}
        tok_ops = rcc.classify(gate_tok)
        red: dict[int, tuple[str, float]] = {}
        for li, zmap in tok_ops.per_layer.items():
            op = max(zmap, key=zmap.get)  # argmax over null-calibrated z
            red[li] = (op, float(zmap[op]))
        reads.append(red)
    return reads


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis: per-layer trajectory + emit/no-op rates at a z-threshold
# ═══════════════════════════════════════════════════════════════════════════════
def analyze_category(
    reads_by_prompt: list[list[dict[int, tuple[str, float]]]],
    layers: list[int], crystal_layers: list[int], zthresh: float,
) -> dict:
    crystal_set = set(crystal_layers)
    layer_votes: dict[int, Counter] = {li: Counter() for li in layers}
    cell_emit = cell_total = 0
    token_noop = n_tokens = 0
    for prompt_reads in reads_by_prompt:
        for tok_read in prompt_reads:
            n_tokens += 1
            fired = False
            for li, (op, z) in tok_read.items():
                cell_total += 1
                if z > zthresh:
                    cell_emit += 1
                    layer_votes[li][op] += 1
                    if li in crystal_set:
                        fired = True
            if not fired:
                token_noop += 1
    per_layer_dom = {}
    for li in layers:
        if layer_votes[li]:
            op, c = layer_votes[li].most_common(1)[0]
            per_layer_dom[li] = {"op": op, "votes": c,
                                 "total": sum(layer_votes[li].values())}
    # trajectory over crystal-bearing layers (the C→B program)
    trajectory = [{"layer": li, **per_layer_dom[li]}
                  for li in sorted(crystal_set) if li in per_layer_dom]
    return {
        "z_thresh": zthresh,
        "n_tokens": n_tokens,
        "token_noop_rate": (token_noop / n_tokens) if n_tokens else 0.0,
        "cell_emit_rate": (cell_emit / cell_total) if cell_total else 0.0,
        "per_layer_dominant": {str(li): d for li, d in per_layer_dom.items()},
        "trajectory": trajectory,
        "c_late": detect_c_late(trajectory, len(layers)),
    }


def detect_c_late(trajectory: list[dict], n_layers: int,
                  readable_frac: float = READABLE_FRAC) -> dict:
    """C-LATE detector (s232 v3): fraction of readable-zone (depth>=readable_frac)
    crystal layers where C (composition combinator) dominates. The routing-register
    composition signal is C-LATE, NOT the raw C-early→B-late arc (detect_arc)."""
    zone_lo = int(readable_frac * n_layers)
    zone = [t for t in trajectory if t["layer"] >= zone_lo]
    c_zone = [t for t in zone if t["op"] == "C"]
    return {
        "readable_zone_lo": zone_lo,
        "n_zone_layers": len(zone),
        "n_C_late": len(c_zone),
        "C_late_layers": [t["layer"] for t in c_zone],
        "C_late_frac": (len(c_zone) / len(zone)) if zone else 0.0,
    }


def detect_arc(trajectory: list[dict]) -> dict:
    """C→B compose-arc detector: are C-dominant layers earlier than B-dominant?"""
    c_layers = [t["layer"] for t in trajectory if t["op"] == "C"]
    b_layers = [t["layer"] for t in trajectory if t["op"] == "B"]
    arc = {
        "C_layers": c_layers, "B_layers": b_layers,
        "C_mean_layer": (float(np.mean(c_layers)) if c_layers else None),
        "B_mean_layer": (float(np.mean(b_layers)) if b_layers else None),
        "n_C": len(c_layers), "n_B": len(b_layers),
    }
    arc["C_before_B"] = bool(
        c_layers and b_layers and np.mean(c_layers) < np.mean(b_layers)
    )
    arc["arc_present"] = bool(arc["C_before_B"] and len(c_layers) >= 2
                             and len(b_layers) >= 2)
    return arc


# ═══════════════════════════════════════════════════════════════════════════════
# Battery runner
# ═══════════════════════════════════════════════════════════════════════════════
def run_monitor(
    model, tok, torch_mod, rcc: RelationalCrystalClassifier, layers: list[int],
    n_prompts: int | None,
) -> dict:
    crystal_layers = rcc.crystal_layers
    gate_n = gate_prefix_len(tok)

    # (prompts, gated?) per condition. gate_retrieval/gate_arithmetic = the v4
    # FRAMING-MATCHED guards (valid under a gated null; the bare ones are invalid —
    # they fire purely from framing-contrast, s232 v3 lesson). They are gated
    # non-composition tasks: if C-late is composition-specific they must stay C-late
    # silent; if they also route C-late then C-late is gated-generic not composition.
    conditions = {
        "lambda": ([COMPILE_GATE + s for s in LAMBDA_SENTENCES], True),
        "gate_neutral": ([COMPILE_GATE + s for s in GATE_NEUTRAL_SENTENCES], True),
        "gate_retrieval": ([COMPILE_GATE + s for s in RETRIEVAL_PROMPTS], True),
        "gate_arithmetic": ([COMPILE_GATE + s for s in ARITHMETIC_PROMPTS], True),
        "retrieval": (RETRIEVAL_PROMPTS, False),
        "arithmetic": (ARITHMETIC_PROMPTS, False),
    }

    out: dict = {"conditions": {}}
    for cat, (prompts, gated) in conditions.items():
        if n_prompts is not None:
            prompts = prompts[:n_prompts]
        reads_by_prompt: list[list[dict[int, tuple[str, float]]]] = []
        for prompt in prompts:
            disp = prompt[-50:].replace("\n", "↵")
            print(f"[v2]   [{cat}] forward …{disp!r}")
            store, n = forward_all_positions(prompt, model, tok, torch_mod, layers)
            if gated:
                positions = list(range(min(gate_n, n - 1), n))  # content tokens
            else:
                positions = list(range(1, n)) if n > 1 else [0]  # skip BOS
            reads_by_prompt.append(
                read_prompt_tokens(rcc, store, layers, positions)
            )
        per_z = {}
        for z in Z_SWEEP:
            a = analyze_category(reads_by_prompt, layers, crystal_layers, z)
            if cat in ("lambda", "gate_neutral"):
                a["arc"] = detect_arc(a["trajectory"])
            per_z[f"z={z}"] = a
        out["conditions"][cat] = {"n_prompts": len(prompts),
                                  "gated": gated, "by_z": per_z}
    out["crystal_layers"] = crystal_layers
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# Verdict
# ═══════════════════════════════════════════════════════════════════════════════
def build_verdict(monitor: dict) -> dict:
    """Two-sided read: did the C→B arc recover in lambda while retrieval stays silent
    and the gate-neutral control stays quieter than lambda?"""
    conds = monitor["conditions"]
    v: dict = {}
    margin = 0.10  # C-late specificity margin
    for z in Z_SWEEP:
        key = f"z={z}"
        lam = conds["lambda"]["by_z"][key]
        gn = conds["gate_neutral"]["by_z"][key]
        ret = conds["retrieval"]["by_z"][key]
        arc = lam.get("arc", {})

        def cl(cat: str, _key: str = key) -> float:
            return conds[cat]["by_z"][_key]["c_late"]["C_late_frac"]

        lam_cl = cl("lambda")
        # framing-matched gated guards (v4) — the valid specificity controls
        gated_guards = {c: round(cl(c), 4)
                        for c in ("gate_neutral", "gate_retrieval", "gate_arithmetic")}
        max_guard = max(gated_guards.values()) if gated_guards else 0.0
        v[key] = {
            # ── PRIMARY (v3/v4): C-LATE composition signal ──────────────────────
            "lambda_C_late_frac": round(lam_cl, 4),
            "lambda_C_late_layers": lam["c_late"]["C_late_layers"],
            "gated_guard_C_late_frac": gated_guards,
            "max_gated_guard_C_late_frac": round(max_guard, 4),
            # composition-SPECIFIC iff lambda C-late clears every framing-matched guard
            "composition_specific": bool(lam_cl > max_guard + margin),
            "readable_zone_lo": lam["c_late"]["readable_zone_lo"],
            # ── back-compat: raw-shape arc + bare-guard over-read (now mis-framed) ─
            "lambda_arc_present": arc.get("arc_present", False),
            "lambda_n_C": arc.get("n_C", 0), "lambda_n_B": arc.get("n_B", 0),
            "lambda_cell_emit_rate": round(lam["cell_emit_rate"], 4),
            "retrieval_cell_emit_rate": round(ret["cell_emit_rate"], 4),
            "gate_neutral_cell_emit_rate": round(gn["cell_emit_rate"], 4),
        }
    return v


# ═══════════════════════════════════════════════════════════════════════════════
# Provenance + IO
# ═══════════════════════════════════════════════════════════════════════════════
def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(_ROOT), stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unknown"


def _transformers_version() -> str:
    try:
        import transformers
        return transformers.__version__
    except Exception:
        return "unknown"


def _json_safe(obj):
    import math
    if isinstance(obj, dict):
        return {str(k): _json_safe(x) for k, x in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(x) for x in obj]
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def _print_summary(calib: dict, verdict: dict) -> None:
    print("\n" + "═" * 72)
    print("OPCODE MONITOR v2 — SUMMARY")
    print("═" * 72)
    cl = calib["crystal_layers"]
    print(f"Crystal layers: {len(cl)}/{calib['n_layers']}  "
          f"null_mode={calib.get('null_mode')}  "
          f"null_tokens={calib.get('n_null_tokens')}")
    for z in Z_SWEEP:
        key = f"z={z}"
        d = verdict[key]
        print(f"\n[{key}]  (readable zone L>={d['readable_zone_lo']})")
        print(f"  ★ lambda C-late frac:   {d['lambda_C_late_frac']}  "
              f"layers={d['lambda_C_late_layers']}")
        print(f"    gated-guard C-late:   {d['gated_guard_C_late_frac']}  "
              f"(max={d['max_gated_guard_C_late_frac']})")
        print(f"    => COMPOSITION_SPECIFIC: {d['composition_specific']}")
        print(f"    (back-compat) raw-arc={d['lambda_arc_present']} "
              f"C x{d['lambda_n_C']}/B x{d['lambda_n_B']}; emit lam="
              f"{d['lambda_cell_emit_rate']} gn={d['gate_neutral_cell_emit_rate']} "
              f"ret_bare={d['retrieval_cell_emit_rate']}")
    print("═" * 72 + "\n")


# ═══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    parser = argparse.ArgumentParser(description="Opcode monitor v2 (cross-task null)")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--null-mode", default="crosstask",
                        choices=["crosstask", "gateneutral"],
                        help="crosstask=bare natural-text null (s232); "
                             "gateneutral=matched-prefix null (v3)")
    parser.add_argument("--smoke", action="store_true",
                        help="Qwen3-0.6B, 3 probes/comb, 2 prompts/cat, n_perm=80")
    args = parser.parse_args()
    null_mode = args.null_mode

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, n_prompts, null_cap = 80, 3, 2, 200
        print("[v2] SMOKE MODE")
    else:
        n_perm, ppc, n_prompts, null_cap = 300, None, None, None

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    cfg = model.config
    n_layers = cfg.num_hidden_layers
    layers = list(range(n_layers))
    print(f"[v2] Layers: {n_layers}, intermediate_size: {cfg.intermediate_size}")

    rcc, calib = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                              null_mode=null_mode)
    print(f"[v2] Crystal-bearing layers: {len(calib['crystal_layers'])}/{n_layers} "
          f"-> {calib['crystal_layers'][:12]}  (null_mode={null_mode})")

    print("\n[v2] Running per-token monitor battery ...")
    monitor = run_monitor(model, tok, torch_mod, rcc, layers, n_prompts)
    verdict = build_verdict(monitor)
    _print_summary(calib, verdict)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = {"calibration_summary": calib, "monitor": monitor, "verdict": verdict}
    # filename tagged by model + null_mode (v4: avoids clobber across the model sweep;
    # the committed s232 verdict.json / verdict_gateneutral.json are left untouched).
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    vname = f"verdict_{slug}_{null_mode}.json"
    mname = f"meta_{slug}_{null_mode}.json"
    (RESULTS_DIR / vname).write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "intermediate_size": cfg.intermediate_size,
        "n_perm": n_perm, "probes_per_combinator": ppc, "z_sweep": Z_SWEEP,
        "null_kind": calib.get("null_kind"), "null_mode": null_mode,
        "n_null_tokens": calib.get("n_null_tokens"),
        "n_crystal_layers": len(calib["crystal_layers"]),
    }
    (RESULTS_DIR / mname).write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[v2] wrote {RESULTS_DIR/vname} and {mname}")


if __name__ == "__main__":
    main()
