#!/usr/bin/env python3
# register: topological/routing
"""Opcode Audit Validation Harness — s127 reproduction + over-read contrast.

Loads a real HF model (default Qwen/Qwen3-14B), captures per-layer gate_proj
outputs, calibrates RelationalCrystalClassifier on crystal_probes(), then runs
both the RELATIONAL classifier and a RAW CONTROL on the s127 task battery.

Scientific point: relational reader emits '·' no-ops on retrieval/common-mode
tokens while the raw argmax control ALWAYS fires an opcode (the over-read
pattern documented as audit-meta-pattern s202→s206).

Usage:
    uv run python scripts/experiments/opcode_audit_validation.py
    uv run python scripts/experiments/opcode_audit_validation.py --smoke
    uv run python scripts/experiments/opcode_audit_validation.py --model Qwen/Qwen3-8B

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
RESULTS_DIR = _ROOT / "results" / "opcode-audit-validation"

COMPILE_GATE = (_ROOT / "gates" / "compile.txt").read_text(encoding="utf-8")

# s127 task battery (category → list[str prompt suffix or full prompt])
LAMBDA_SENTENCES = [
    "The dog runs.",
    "Every student reads a book.",
    "If it rains, the ground is wet.",
    "No bird can swim.",
    "Mary likes the cat that John owns.",
]

ARITHMETIC_PROMPTS = [
    "2 + 3 =",
    "7 * 8 =",
    "15 - 4 =",
    "Compute 12 + 27.",
    "What is 9 times 6?",
]

RETRIEVAL_PROMPTS = [
    "The capital of France is",
    "The author of Hamlet is",
    "Water is made of hydrogen and",
    "The largest planet is",
    "The first president of the United States was",
]


# ═══════════════════════════════════════════════════════════════════════════════
# Raw control classifier
# ═══════════════════════════════════════════════════════════════════════════════


class RawControlClassifier:
    """Deliberate over-reader: raw gate argmax, no CMR, no null, no threshold.

    Reproduces the s202 audit-meta-pattern — always fires an opcode (even on
    retrieval / common-mode tokens that the relational reader correctly no-ops).
    """

    def __init__(self, layers: list[int]) -> None:
        self.layers = list(layers)
        self._raw_centroids: dict[int, np.ndarray] = {}  # li -> [9, d] unit

    def calibrate(
        self,
        gate_by_layer: dict[int, np.ndarray],
        labels: np.ndarray,
    ) -> None:
        """Build per-combinator mean of RAW gate features (no sign, no CMR)."""
        labels = np.asarray(labels)
        for li in self.layers:
            G = np.asarray(gate_by_layer[li], dtype=np.float64)  # [N, d]
            cents = np.zeros((len(CRYSTAL), G.shape[1]), np.float64)
            for j, c in enumerate(CRYSTAL):
                m = labels == c
                if m.any():
                    cents[j] = G[m].mean(axis=0)
            # unit-normalise
            norms = np.linalg.norm(cents, axis=1, keepdims=True) + 1e-30
            self._raw_centroids[li] = cents / norms

    def classify(
        self, gate_by_layer_token: dict[int, np.ndarray]
    ) -> tuple[str, dict[int, str]]:
        """Return (dominant_op, {li: op}) — ALWAYS emits a winner per layer."""
        per_layer: dict[int, str] = {}
        vote_counter: Counter[str] = Counter()
        for li in self.layers:
            cents = self._raw_centroids.get(li)
            if cents is None:
                continue
            g = np.asarray(gate_by_layer_token[li], dtype=np.float64)
            gn = np.linalg.norm(g)
            if gn < 1e-12:
                per_layer[li] = CRYSTAL[0]
                vote_counter[CRYSTAL[0]] += 1
                continue
            sims = cents @ (g / gn)  # [9] cosine
            winner = CRYSTAL[int(np.argmax(sims))]
            per_layer[li] = winner
            vote_counter[winner] += 1
        dominant = vote_counter.most_common(1)[0][0] if vote_counter else CRYSTAL[0]
        return dominant, per_layer


# ═══════════════════════════════════════════════════════════════════════════════
# Gate-capture hook helper
# ═══════════════════════════════════════════════════════════════════════════════


def _make_hook(store: dict[int, np.ndarray], layer_idx: int):
    """Forward hook: capture last-real-token gate_proj output as float64 CPU."""

    def _hook(_module, _inp, out):
        # out: [B, T, intermediate_size]
        vec = out[0, -1, :].detach().float().cpu().numpy().astype(np.float64)
        store[layer_idx] = vec

    return _hook


# ═══════════════════════════════════════════════════════════════════════════════
# Model loader + forward runner
# ═══════════════════════════════════════════════════════════════════════════════


def load_model_and_tokenizer(model_name: str):
    """Load model and tokenizer (lazy import so --help works without torch)."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[harness] Loading tokenizer: {model_name}")
    tok = AutoTokenizer.from_pretrained(model_name)

    print(f"[harness] Loading model: {model_name}  (dtype=auto, device_map=auto)")
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype="auto", device_map="auto"
    )
    model.eval()
    print(f"[harness] Model loaded in {time.time()-t0:.1f}s")
    return model, tok, torch


def forward_one(
    prompt: str,
    model,
    tok,
    torch_mod,
    layers: list[int],
) -> dict[int, np.ndarray]:
    """Run one prompt forward; return {li: gate_last_token [d]}."""
    store: dict[int, np.ndarray] = {}
    handles = []
    for li in layers:
        h = model.model.layers[li].mlp.gate_proj.register_forward_hook(
            _make_hook(store, li)
        )
        handles.append(h)
    try:
        inputs = tok(prompt, return_tensors="pt")
        # move inputs to the same device as the model's first param
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            model(**inputs)
    finally:
        for h in handles:
            h.remove()
    return store


# ═══════════════════════════════════════════════════════════════════════════════
# Calibration
# ═══════════════════════════════════════════════════════════════════════════════


def calibrate_classifiers(
    model,
    tok,
    torch_mod,
    layers: list[int],
    n_perm: int,
    probes_per_combinator: int | None,
) -> tuple[RelationalCrystalClassifier, RawControlClassifier]:
    """Run crystal_probes through the model, build gate_by_layer, calibrate."""
    from verbum.probes.library import crystal_probes

    probes = crystal_probes()
    print(f"[harness] Total crystal probes: {len(probes)}")

    # Optionally cap per combinator (smoke mode)
    if probes_per_combinator is not None:
        kept = []
        counts: Counter[str] = Counter()
        for p in probes:
            if p.combinator in CRYSTAL:
                if counts[p.combinator] < probes_per_combinator:
                    kept.append(p)
                    counts[p.combinator] += 1
        probes = kept
        print(f"[harness] Smoke: using {len(probes)} probes "
              f"({probes_per_combinator}/combinator)")

    # Filter to CRYSTAL-only
    probes = [p for p in probes if p.combinator in CRYSTAL]
    print(f"[harness] Crystal probes after filter: {len(probes)}")

    gate_by_layer: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    labels_list: list[str] = []

    for i, p in enumerate(probes):
        if i % 50 == 0:
            print(f"[harness]   calibration forward {i}/{len(probes)} ...")
        store = forward_one(p.prompt, model, tok, torch_mod, layers)
        for li in layers:
            gate_by_layer[li].append(store[li])
        labels_list.append(p.combinator)  # type: ignore[arg-type]

    gate_np = {li: np.stack(gate_by_layer[li], axis=0) for li in layers}
    labels_np = np.array(labels_list)

    print("[harness] Calibrating RelationalCrystalClassifier ...")
    rcc = RelationalCrystalClassifier(
        layers, n_perm=n_perm, z_thresh=3.0, sil_z_thresh=2.0, consensus_gram="auto"
    )
    rcc.calibrate(gate_np, labels_np)

    print("[harness] Calibrating RawControlClassifier ...")
    raw = RawControlClassifier(layers)
    raw.calibrate(gate_np, labels_np)

    return rcc, raw


# ═══════════════════════════════════════════════════════════════════════════════
# Battery runner
# ═══════════════════════════════════════════════════════════════════════════════


def run_battery(
    model,
    tok,
    torch_mod,
    rcc: RelationalCrystalClassifier,
    raw_clf: RawControlClassifier,
    layers: list[int],
    n_prompts: int | None = None,
) -> dict:
    """Run the s127 task battery; return structured results dict."""
    battery = {
        "lambda": [COMPILE_GATE + s for s in LAMBDA_SENTENCES],
        "arithmetic": ARITHMETIC_PROMPTS,
        "retrieval": RETRIEVAL_PROMPTS,
    }

    all_records: list[dict] = []
    category_agg: dict[str, dict] = {}

    for category, prompts in battery.items():
        if n_prompts is not None:
            prompts = prompts[:n_prompts]

        rel_dominants: list[str] = []
        raw_dominants: list[str] = []
        rel_noop_count = 0
        emitted_ops_all: list[str] = []
        prompt_records: list[dict] = []

        for prompt in prompts:
            display = prompt[:60].replace("\n", "↵") + ("…" if len(prompt) > 60 else "")
            print(f"[harness]   [{category}] forward: {display!r}")
            store = forward_one(prompt, model, tok, torch_mod, layers)

            # RELATIONAL
            tok_ops = rcc.classify(store)
            rel_dom = tok_ops.dominant
            rel_dominants.append(rel_dom)
            if rel_dom == "·":
                rel_noop_count += 1
            for li_ops in tok_ops.emitted.values():
                emitted_ops_all.extend(li_ops)

            # RAW CONTROL
            raw_dom, raw_per_layer = raw_clf.classify(store)
            raw_dominants.append(raw_dom)

            # Collect per-layer z details for record
            per_layer_detail = {}
            for li, zmap in tok_ops.per_layer.items():
                per_layer_detail[li] = {
                    "z_scores": zmap,
                    "emitted": tok_ops.emitted.get(li, []),
                }

            rec = {
                "category": category,
                "prompt_prefix": display,
                "relational_dominant": rel_dom,
                "relational_is_noop": rel_dom == "·",
                "relational_emitted_layers": {
                    str(li): ops for li, ops in tok_ops.emitted.items()
                },
                "raw_dominant": raw_dom,
                "raw_per_layer": {str(li): op for li, op in raw_per_layer.items()},
            }
            prompt_records.append(rec)
            all_records.append(rec)

        n = len(prompts)
        rel_dist = dict(Counter(rel_dominants))
        raw_dist = dict(Counter(raw_dominants))
        emitted_dist = dict(Counter(emitted_ops_all))

        category_agg[category] = {
            "n_prompts": n,
            "relational": {
                "dominant_distribution": rel_dist,
                "noop_rate": rel_noop_count / n,
                "noop_count": rel_noop_count,
                "emitted_op_counts": emitted_dist,
            },
            "raw_control": {
                "dominant_distribution": raw_dist,
                "emit_rate": 1.0,  # by construction: always fires
                "noop_rate": 0.0,
            },
            "prompts": prompt_records,
        }

    return {"category_aggregates": category_agg, "all_records": all_records}


# ═══════════════════════════════════════════════════════════════════════════════
# s127 check: does the relational reader reproduce the s127 findings?
# ═══════════════════════════════════════════════════════════════════════════════


def s127_reproduction_check(category_agg: dict) -> dict:
    """Evaluate the three s127 predictions."""
    checks: dict[str, dict] = {}

    # 1. lambda -> composer ops (B/C) present
    lam = category_agg.get("lambda", {})
    lam_rel = lam.get("relational", {})
    lam_dist = lam_rel.get("dominant_distribution", {})
    lam_emitted = lam_rel.get("emitted_op_counts", {})
    bc_dominant = lam_dist.get("B", 0) + lam_dist.get("C", 0)
    bc_emitted = lam_emitted.get("B", 0) + lam_emitted.get("C", 0)
    checks["lambda_composer_BC"] = {
        "prediction": "B/C dominant or emitted in lambda prompts",
        "BC_dominant_count": bc_dominant,
        "BC_emitted_count": bc_emitted,
        "dominant_distribution": lam_dist,
        "emitted_distribution": lam_emitted,
        "passes": (bc_dominant > 0 or bc_emitted > 0),
    }

    # 2. arithmetic -> selector ops (K/I) present
    arith = category_agg.get("arithmetic", {})
    arith_rel = arith.get("relational", {})
    arith_dist = arith_rel.get("dominant_distribution", {})
    arith_emitted = arith_rel.get("emitted_op_counts", {})
    ki_dominant = arith_dist.get("K", 0) + arith_dist.get("I", 0)
    ki_emitted = arith_emitted.get("K", 0) + arith_emitted.get("I", 0)
    checks["arithmetic_selector_KI"] = {
        "prediction": "K/I dominant or emitted in arithmetic prompts",
        "KI_dominant_count": ki_dominant,
        "KI_emitted_count": ki_emitted,
        "dominant_distribution": arith_dist,
        "emitted_distribution": arith_emitted,
        "passes": (ki_dominant > 0 or ki_emitted > 0),
    }

    # 3. retrieval -> high no-op rate
    ret = category_agg.get("retrieval", {})
    ret_rel = ret.get("relational", {})
    ret_noop_rate = ret_rel.get("noop_rate", 0.0)
    ret_raw_noop_rate = ret.get("raw_control", {}).get("noop_rate", 0.0)
    checks["retrieval_silent"] = {
        "prediction": "retrieval -> high no-op rate; raw never no-ops",
        "relational_noop_rate": ret_noop_rate,
        "raw_noop_rate": ret_raw_noop_rate,
        "relational_dominant_distribution": ret_rel.get("dominant_distribution", {}),
        "passes": ret_noop_rate > 0.3,  # at least 30% no-op on retrieval
    }

    # 4. over-read contrast: raw fires on retrieval while relational no-ops
    raw_ret_dist = ret.get("raw_control", {}).get("dominant_distribution", {})
    raw_ret_fires = sum(raw_ret_dist.values())
    checks["over_read_contrast"] = {
        "prediction": "raw emits ~100% while relational no-ops on retrieval",
        "raw_emit_rate": 1.0,
        "relational_noop_rate": ret_noop_rate,
        "raw_dominant_distribution": raw_ret_dist,
        "passes": (raw_ret_fires > 0 and ret_noop_rate > 0.0),
    }

    overall = sum(1 for c in checks.values() if c["passes"])
    checks["_summary"] = {
        "checks_passed": overall,
        "checks_total": len(checks) - 1,  # exclude _summary itself
    }
    return checks


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(_ROOT),
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return "unknown"


def _transformers_version() -> str:
    try:
        import transformers
        return transformers.__version__
    except Exception:
        return "unknown"


def _print_summary(calib_summary: dict, battery_results: dict, s127: dict) -> None:
    print("\n" + "═" * 72)
    print("OPCODE AUDIT VALIDATION — RESULTS SUMMARY")
    print("═" * 72)

    # Calibration
    crystal_ls = calib_summary["crystal_layers"]
    n_total = calib_summary["n_layers"]
    per = calib_summary["per_layer"]
    sil_zs = [v["sil_z"] for v in per.values()]
    gc_vals = [
        v["gc_consensus"] for v in per.values() if not _is_nan(v["gc_consensus"])
    ]
    print("\nCalibration:")
    print(f"  Crystal-bearing layers: {len(crystal_ls)}/{n_total}  "
          f"indices={crystal_ls[:8]}{'...' if len(crystal_ls)>8 else ''}")
    print(f"  sil_z range: [{min(sil_zs):.3f}, {max(sil_zs):.3f}]")
    if gc_vals:
        print(f"  gc_consensus range: [{min(gc_vals):.3f}, {max(gc_vals):.3f}]")
    else:
        print("  gc_consensus: (no consensus file found)")

    # Battery results
    agg = battery_results["category_aggregates"]
    print("\nPer-category results:")
    for cat, data in agg.items():
        rel = data["relational"]
        raw = data["raw_control"]
        print(f"\n  [{cat.upper()}]  n={data['n_prompts']}")
        print(f"    RELATIONAL dominant dist: {rel['dominant_distribution']}")
        print(f"    RELATIONAL no-op rate:    {rel['noop_rate']:.2f} "
              f"({rel['noop_count']}/{data['n_prompts']})")
        print(f"    RELATIONAL emitted ops:   {rel['emitted_op_counts']}")
        print(f"    RAW dominant dist:        {raw['dominant_distribution']}")
        print(f"    RAW emit rate:            {raw['emit_rate']:.2f} (always)")

    # s127
    print("\ns127 Reproduction Checks:")
    for name, c in s127.items():
        if name.startswith("_"):
            continue
        tick = "✅" if c["passes"] else "❌"
        print(f"  {tick} {name}: {c['prediction']}")
    summ = s127.get("_summary", {})
    passed = summ.get("checks_passed", 0)
    total = summ.get("checks_total", 0)
    print(f"\n  Overall: {passed}/{total} checks passed")
    print("═" * 72 + "\n")


def _is_nan(v) -> bool:
    try:
        import math
        return math.isnan(v)
    except (TypeError, ValueError):
        return False


def _json_safe(obj):
    """Recursively make object JSON-serialisable (handle nan/inf)."""
    import math
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Opcode audit validation harness (s127 reproduction)"
    )
    parser.add_argument(
        "--model", default="Qwen/Qwen3-14B", help="HF model name or path"
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Smoke mode: Qwen3-0.6B, 3 probes/combinator, 2 prompts/cat, n_perm=80",
    )
    args = parser.parse_args()

    model_name = args.model
    smoke = args.smoke

    if smoke:
        if args.model == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm = 80
        probes_per_combinator = 3
        n_prompts_per_cat = 2
        print("[harness] SMOKE MODE: small model, few probes, fast verification")
    else:
        n_perm = 300
        probes_per_combinator = None  # all probes
        n_prompts_per_cat = None  # all prompts

    print(f"[harness] Model: {model_name}")

    # Load model
    model, tok, torch_mod = load_model_and_tokenizer(model_name)

    # Determine layers + intermediate size from model config
    cfg = model.config
    n_layers: int = cfg.num_hidden_layers
    layers = list(range(n_layers))
    intermediate_size: int = cfg.intermediate_size
    print(f"[harness] Layers: {n_layers}, intermediate_size: {intermediate_size}")

    # Calibrate
    rcc, raw_clf = calibrate_classifiers(
        model, tok, torch_mod, layers, n_perm, probes_per_combinator
    )

    calib_summary = rcc.calibration_summary()
    crystal_ls = calib_summary["crystal_layers"]
    print(f"[harness] Crystal-bearing layers: {len(crystal_ls)}/{n_layers}")
    print(f"[harness] Crystal layer indices (first 10): {crystal_ls[:10]}")

    # Run s127 battery
    print("\n[harness] Running s127 task battery ...")
    battery_results = run_battery(
        model, tok, torch_mod, rcc, raw_clf, layers, n_prompts=n_prompts_per_cat
    )

    # s127 reproduction check
    s127 = s127_reproduction_check(battery_results["category_aggregates"])

    # Print summary
    _print_summary(calib_summary, battery_results, s127)

    # Write results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    verdict = {
        "calibration_summary": calib_summary,
        "battery_results": battery_results,
        "s127_reproduction": s127,
    }
    verdict_path = RESULTS_DIR / "verdict.json"
    verdict_path.write_text(
        json.dumps(_json_safe(verdict), indent=2), encoding="utf-8"
    )
    print(f"[harness] verdict.json written: {verdict_path}")

    meta = {
        "model": model_name,
        "smoke": smoke,
        "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers,
        "intermediate_size": intermediate_size,
        "n_crystal_layers": len(crystal_ls),
        "n_perm": n_perm,
        "probes_per_combinator": probes_per_combinator,
    }
    meta_path = RESULTS_DIR / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[harness] meta.json written: {meta_path}")


if __name__ == "__main__":
    main()
