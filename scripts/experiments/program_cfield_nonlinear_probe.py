#!/usr/bin/env python3
# register: decodability (linear vs nonlinear C-probe gap; the s250 escape hatch)
"""Nonlinear C decodability-gap — the last linear escape hatch (s250 cont.2).

THE s250 cont. RESULT + ITS ONLY ESCAPE HATCH. INLP (program_cfield_subspace_ablation)
erased ALL *linearly*-decodable C from the L30 residual (decodability 0.919 -> 0.667)
and the c=2-vs-c=0 differential STILL reversed => the applicative-C field is a readout
register, not the object-application mechanism. The one caveat: INLP erases only LINEAR
decodability. If C is encoded NONLINEARLY, INLP would miss it and a nonlinear ablation
could still find a load-bearing C. This script tests whether that escape hatch exists.

THE GATE (decisive, tractable - a full SAE needs ~1e6 activations, infeasible at n=135):
  is there NONLINEAR C-structure that survives linear erasure?
  - Probes: logistic (LINEAR baseline) vs MLP + RBF-SVM (NONLINEAR), 5-fold stratified
    CV inside a StandardScaler pipeline (clean CV).
  - Conditions: RAW residuals AND POST-INLP residuals (linear C projected out, span(W)).
  - Controls: a LABEL-SHUFFLED CV for every probe+condition (the high-d/low-n OVERFIT
    ceiling) AND a PCA-k overfit-controlled feature view (the meaningful regime).
  - Decision: nonlinear escape exists iff a nonlinear probe on POST-INLP features beats
    max(shuffle, majority) by a margin in the PCA-controlled view.

INTERPRETATION (λ measure, two-sided):
  - no escape (nonlinear post-INLP ≈ shuffle ≈ majority) => C is essentially LINEAR,
    already fully erased => s250 cont. is airtight; the C-field is a readout register
    linearly AND nonlinearly; no nonlinear ablation is warranted.
  - escape (nonlinear post-INLP ≫ control) => a real nonlinear C survives INLP => a
    causal nonlinear/SAE ablation becomes the genuine next step.

Usage:
    uv run python scripts/experiments/program_cfield_nonlinear_probe.py --smoke
    uv run python scripts/experiments/program_cfield_nonlinear_probe.py \
        --model Qwen/Qwen3-14B --layers 27 29 30 31 --k-inlp 16 --pca 50

License: MIT. AGENTS.md S5 λ provenance.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from opcode_monitor_v2 import (  # noqa: E402
    COMPILE_GATE,
    _git_sha,
    _json_safe,
    _transformers_version,
    gate_prefix_len,
    load_model_and_tokenizer,
)
from program_cfield_ablation import load_ladder  # noqa: E402
from program_cfield_subspace_ablation import inlp_subspace  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "program-cfield-ablation"
READING_PROBES = _ROOT / "data" / "reading-probes.jsonl"


# ═══════════════════════════════════════════════════════════════════════════════
# Residual collection (content-mean per layer, one forward per item)
# ═══════════════════════════════════════════════════════════════════════════════
def collect_resid(prompt, model, tok, torch_mod, layers, gate_n):
    store: dict[int, np.ndarray] = {}
    handles = []

    def mk(li):
        def hook(_m, _i, out):
            h = out[0] if isinstance(out, tuple) else out
            store[li] = h[0, :, :].detach().float().cpu().numpy().astype(np.float64)
        return hook

    for li in layers:
        handles.append(model.model.layers[li].register_forward_hook(mk(li)))
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            model(**inputs)
    finally:
        for h in handles:
            h.remove()
    n_tok = int(inputs["input_ids"].shape[1])
    start = min(gate_n, n_tok - 1)
    return {li: store[li][start:n_tok].mean(axis=0) for li in layers}


# ═══════════════════════════════════════════════════════════════════════════════
# Probes + cross-validated accuracy (clean pipelines, shuffle control)
# ═══════════════════════════════════════════════════════════════════════════════
def _factory(kind: str, seed: int):
    from sklearn.linear_model import LogisticRegression
    from sklearn.neural_network import MLPClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    if kind == "logistic":
        clf = LogisticRegression(max_iter=4000, C=1.0)
    elif kind == "mlp":
        clf = MLPClassifier(hidden_layer_sizes=(64,), max_iter=2000,
                            random_state=seed, early_stopping=False)
    elif kind == "rbf_svm":
        clf = SVC(kernel="rbf", C=1.0, gamma="scale")
    else:
        raise ValueError(kind)
    return make_pipeline(StandardScaler(), clf)


def cv_acc(kind: str, x: np.ndarray, y: np.ndarray, seed: int,
           shuffled: bool = False) -> float:
    from sklearn.model_selection import StratifiedKFold, cross_val_score

    yy = y.copy()
    if shuffled:
        rng = np.random.default_rng(seed + 7)
        rng.shuffle(yy)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    return float(np.mean(cross_val_score(_factory(kind, seed), x, yy, cv=skf)))


def probe_block(x: np.ndarray, y: np.ndarray, seed: int) -> dict:
    """All probes, real + shuffled, on feature matrix x."""
    out = {}
    for kind in ("logistic", "mlp", "rbf_svm"):
        out[kind] = {
            "acc": round(cv_acc(kind, x, y, seed), 4),
            "shuffle": round(cv_acc(kind, x, y, seed, shuffled=True), 4),
        }
    return out


def pca_reduce(x: np.ndarray, k: int, seed: int) -> np.ndarray:
    from sklearn.decomposition import PCA

    k = min(k, x.shape[0] - 1, x.shape[1])
    return PCA(n_components=k, random_state=seed).fit_transform(x)


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    ap = argparse.ArgumentParser(description="Nonlinear C decodability-gap")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--layers", type=int, nargs="+", default=[27, 29, 30, 31])
    ap.add_argument("--k-inlp", type=int, default=16)
    ap.add_argument("--pca", type=int, default=50,
                    help="PCA dim for overfit-controlled view")
    ap.add_argument("--margin", type=float, default=0.10)
    ap.add_argument("--max-per-group", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model_name = args.model
    layers_req = sorted(args.layers)
    k_inlp = args.k_inlp
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        max_per_group = args.max_per_group or 15
        k_inlp = min(k_inlp, 6)
        print("[nonlin] SMOKE MODE")
    else:
        max_per_group = args.max_per_group

    ladder = load_ladder(READING_PROBES)
    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = [li for li in layers_req if li < n_layers]
    if not layers:
        denom = max(n_layers - 1, 1)
        layers = sorted({min(n_layers - 2, round(f * denom))
                         for f in (0.68, 0.72, 0.75, 0.775)})
        print(f"[nonlin] layers rescaled for {n_layers}L -> {layers}")
    gate_n = gate_prefix_len(tok)
    print(f"[nonlin] model={model_name} layers={layers} k_inlp={k_inlp} pca={args.pca}")

    def grp(cc):
        g = [r for r in ladder if r["c_count"] == cc]
        return g[:max_per_group] if max_per_group else g
    items = grp(0) + grp(1) + grp(2)
    y = np.asarray([1 if r["c_count"] > 0 else 0 for r in items])
    majority = float(max(np.mean(y), 1 - np.mean(y)))
    print(f"[nonlin] items={len(items)} (C-present {int(y.sum())}/{len(y)}) "
          f"majority={majority:.3f}")

    # ── collect residuals ─────────────────────────────────────────────────────────
    resid_by_layer: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    for i, r in enumerate(items):
        rd = collect_resid(COMPILE_GATE + r["input"], model, tok, torch_mod, layers,
                           gate_n)
        for li in layers:
            resid_by_layer[li].append(rd[li])
        if (i + 1) % 20 == 0:
            print(f"[nonlin]   collect {i + 1}/{len(items)}")

    per_layer: dict[str, dict] = {}
    escape_flags: list[bool] = []
    for li in layers:
        x = np.asarray(resid_by_layer[li])                # [n, d]
        scale = float(np.mean(np.linalg.norm(x, axis=1))) or 1.0
        x_s = x / scale
        q_C, curve = inlp_subspace(x_s, y, k_inlp, args.seed)
        x_ab = x - (x @ q_C) @ q_C.T                      # linear C erased

        block = {
            "raw_full": probe_block(x, y, args.seed),
            "inlp_full": probe_block(x_ab, y, args.seed),
            "decodability_curve": curve,
        }
        if args.pca and x.shape[0] > 3:
            xp = pca_reduce(x, args.pca, args.seed)
            xpa = pca_reduce(x_ab, args.pca, args.seed)
            block["raw_pca"] = probe_block(xp, y, args.seed)
            block["inlp_pca"] = probe_block(xpa, y, args.seed)

        # escape decision: nonlinear post-INLP beats control by margin (PCA if avail)
        view = block.get("inlp_pca", block["inlp_full"])
        ctrl_view = view
        nl_best = max(view["mlp"]["acc"], view["rbf_svm"]["acc"])
        nl_shuffle = max(ctrl_view["mlp"]["shuffle"], ctrl_view["rbf_svm"]["shuffle"])
        threshold = max(nl_shuffle, majority) + args.margin
        escape = bool(nl_best > threshold)
        block["escape"] = escape
        block["escape_detail"] = {
            "nl_best_post_inlp": round(nl_best, 4),
            "nl_shuffle": round(nl_shuffle, 4),
            "majority": round(majority, 4),
            "threshold": round(threshold, 4),
            "view": "pca" if "inlp_pca" in block else "full",
        }
        escape_flags.append(escape)
        per_layer[str(li)] = block
        v = block.get("inlp_pca", block["inlp_full"])
        rawv = block.get("raw_pca", block["raw_full"])
        print(f"[nonlin] L{li}: RAW lin={rawv['logistic']['acc']} "
              f"mlp={rawv['mlp']['acc']} rbf={rawv['rbf_svm']['acc']} | "
              f"POST-INLP lin={v['logistic']['acc']} mlp={v['mlp']['acc']} "
              f"rbf={v['rbf_svm']['acc']} (shuffle~{nl_shuffle}) escape={escape}")

    nonlinear_escape = bool(any(escape_flags))
    interpretation = (
        "ESCAPE HATCH: a nonlinear C survives linear INLP erasure -> a causal "
        "nonlinear/SAE C-ablation is the genuine next step." if nonlinear_escape else
        "NO escape hatch: C is essentially LINEAR and already fully erased by INLP -> "
        "s250 cont. is airtight; the applicative-C field is a readout register "
        "linearly AND nonlinearly.")

    verdict = {
        "model": model_name, "n_layers": n_layers, "layers": layers,
        "n_items": len(items), "majority_baseline": round(majority, 4),
        "k_inlp": k_inlp, "pca": args.pca, "margin": args.margin, "seed": args.seed,
        "per_layer": per_layer, "nonlinear_escape": nonlinear_escape,
        "interpretation": interpretation,
    }

    print("\n" + "═" * 82)
    print(f"NONLINEAR C DECODABILITY-GAP — {model_name}")
    print("═" * 82)
    print(f"  items={len(items)} majority={majority:.3f} k={k_inlp} pca={args.pca}")
    print(f"  nonlinear_escape (any layer) = {nonlinear_escape}")
    print(f"  >> {interpretation}")
    print("═" * 82 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    (RESULTS_DIR / f"nonlinear_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "layers": layers, "k_inlp": k_inlp, "pca": args.pca, "margin": args.margin,
        "seed": args.seed, "probe_set": str(READING_PROBES.relative_to(_ROOT)),
        "method": "Linear (logistic) vs nonlinear (MLP, RBF-SVM) C-present probes, "
                  "5-fold stratified CV in a StandardScaler pipeline, on RAW and "
                  "POST-INLP (linear C erased) L-residuals; label-shuffled control + "
                  "PCA-k overfit-controlled view; escape = nonlinear post-INLP beats "
                  "max(shuffle, majority) by margin.",
        "scope": "Tests the last s250 caveat — whether a NONLINEAR C survived linear "
                 "INLP erasure (would warrant a nonlinear/SAE causal ablation).",
    }
    (RESULTS_DIR / f"nonlinear_meta_{slug}.json").write_text(
        json.dumps(_json_safe(meta), indent=2), encoding="utf-8")
    print(f"[nonlin] wrote {RESULTS_DIR}/nonlinear_verdict_{slug}.json (+ meta)")


if __name__ == "__main__":
    main()
