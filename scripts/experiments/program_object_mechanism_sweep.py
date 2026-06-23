#!/usr/bin/env python3
# register: causal (component knockout localizer; object-application mechanism hunt)
"""Object-application mechanism sweep — WHERE is the computation? (s250 cont.3).

THE QUESTION the C-field thread leaves open. s250 (+cont, +cont.2) proved the decodable
applicative-C routing field is a READOUT REGISTER, not the object-application mechanism
(decodability != causality, at rank-1, rank-16 INLP, and linear-vs-nonlinear). So WHERE
is object-application actually computed? The standing hypothesis (knowledge page §s250
cont.2): in attention OV / the value register (s127 {B,C}=composers->attention, s206),
not the FFN. This script hunts it with a POSITIVE localization search, not another
C-direction null.

THE METHOD — component-knockout sweep with the object-count gradient as the readout.
For each layer and each component in {attention-write (self_attn.o_proj), MLP-write
(mlp)}, mean-ablate (replace with the dataset-mean) ONLY the LAST-token output (a
single, position-MATCHED knockout -> NO length confound vs content-position ablation),
measure the next-token KL per object-count group on the matched ladder
(data/reading-probes.jsonl: intransitive c=0 / transitive c=1 / ditransitive c=2). The
object-application SIGNATURE = KL rises monotonically with object count (Spearman > 0,
significant) AND c2 > c0 (two-sample t) -> that (layer, component) is load-bearing for
object-application. The attention-vs-MLP comparison answers the OV-vs-FFN question.

WHY LAST-TOKEN ONLY: next-token logits read the last position; a single matched position
removes the length confound (c2 sentences are longer) that would inflate any
content-position differential. The skip connection means a single-layer knockout is a
RELATIVE probe across layers/components, which is exactly what localization needs.

VERDICT (λ measure, two-sided):
  mechanism_localized = exists (layer, component) with Spearman(KL, object-count) > 0
  significant AND c2-vs-c0 t > 2. Report the top hits and whether they are ATTN or MLP.
  - hits concentrate in ATTN => object-application lives in the attention pathway
    (confirms the OV / value-register hypothesis; the FFN C-field was a readout of it).
  - no monotonic hit anywhere => object-application is not localized to a single
    component's last-token write (distributed / pattern-level) => next probe = attention
    EDGE knockout (predicate->object), not component write.

Usage:
    uv run python scripts/experiments/program_object_mechanism_sweep.py --smoke
    uv run python scripts/experiments/program_object_mechanism_sweep.py \
        --model Qwen/Qwen3-14B --max-per-group 20

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
from program_cfield_ablation import (  # noqa: E402
    kl_div,
    load_ladder,
    log_softmax,
    two_sample_t,
)

RESULTS_DIR = _ROOT / "results" / "program-object-mechanism"
READING_PROBES = _ROOT / "data" / "reading-probes.jsonl"
COMPONENTS = ("attn", "mlp")


def _module(model, li: int, comp: str):
    layer = model.model.layers[li]
    if comp == "attn":
        return layer.self_attn.o_proj
    if comp == "mlp":
        return layer.mlp
    raise ValueError(comp)


# ═══════════════════════════════════════════════════════════════════════════════
# Baseline capture — last-token attn-write + mlp-write per layer + baseline logits
# ═══════════════════════════════════════════════════════════════════════════════
def baseline_forward(prompt, model, tok, torch_mod, layers):
    store: dict[tuple[str, int], np.ndarray] = {}
    handles = []

    def mk(comp, li):
        def hook(_m, _i, out):
            h = out[0] if isinstance(out, tuple) else out
            store[(comp, li)] = h[0, -1, :].detach().float().cpu().numpy().astype(
                np.float64)
        return hook

    for li in layers:
        for comp in COMPONENTS:
            handles.append(_module(model, li, comp).register_forward_hook(mk(comp, li)))
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            out = model(**inputs)
        logits = out.logits[0, -1, :].detach().float().cpu().numpy().astype(np.float64)
    finally:
        for h in handles:
            h.remove()
    return store, logits


# ═══════════════════════════════════════════════════════════════════════════════
# Knockout — replace the LAST-token component output with a target vector
# ═══════════════════════════════════════════════════════════════════════════════
def make_knockout_hook(target_vec, torch_mod):
    def hook(_m, _i, out):
        h = out[0] if isinstance(out, tuple) else out
        t = torch_mod.as_tensor(target_vec, dtype=h.dtype, device=h.device)
        h[0, -1, :] = t
        return out
    return hook


def knockout_forward(prompt, model, tok, torch_mod, comp, li, target_vec):
    handle = _module(model, li, comp).register_forward_hook(
        make_knockout_hook(target_vec, torch_mod))
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            out = model(**inputs)
        logits = out.logits[0, -1, :].detach().float().cpu().numpy().astype(np.float64)
    finally:
        handle.remove()
    return logits


def spearman(x: list[float], y: list[float]) -> tuple[float | None, float | None]:
    if len(x) < 3 or len(set(x)) < 2 or len(set(y)) < 2:
        return None, None
    from scipy import stats

    r, p = stats.spearmanr(x, y)
    return round(float(r), 4), round(float(p), 5)


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    ap = argparse.ArgumentParser(description="Object-application mechanism sweep")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--layers", type=int, nargs="+", default=None,
                    help="layers to sweep (default: all)")
    ap.add_argument("--ablate", default="mean", choices=["mean", "zero"])
    ap.add_argument("--max-per-group", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        max_per_group = args.max_per_group if args.max_per_group != 20 else 8
        print("[mech] SMOKE MODE")
    else:
        max_per_group = args.max_per_group

    ladder = load_ladder(READING_PROBES)
    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = sorted(args.layers) if args.layers else list(range(n_layers))
    layers = [li for li in layers if li < n_layers]
    gate_n = gate_prefix_len(tok)  # noqa: F841  (kept for provenance/debug symmetry)
    print(f"[mech] model={model_name} n_layers={n_layers} sweep={len(layers)} layers "
          f"ablate={args.ablate}")

    def grp(cc):
        g = [r for r in ladder if r["c_count"] == cc]
        return g[:max_per_group] if max_per_group else g
    groups = {0: grp(0), 1: grp(1), 2: grp(2)}
    items = groups[0] + groups[1] + groups[2]
    print(f"[mech] items c0={len(groups[0])} c1={len(groups[1])} c2={len(groups[2])}")

    # ── baseline pass: capture targets + baseline logp0 ──────────────────────────
    base_logp: dict[str, np.ndarray] = {}
    cc_of: dict[str, int] = {}
    targ_sum: dict[tuple[str, int], np.ndarray] = {}
    n_seen = 0
    print("[mech] baseline pass ...")
    for i, r in enumerate(items):
        store, logits = baseline_forward(COMPILE_GATE + r["input"], model, tok,
                                         torch_mod, layers)
        base_logp[r["input"]] = log_softmax(logits)
        cc_of[r["input"]] = r["c_count"]
        for key, vec in store.items():
            targ_sum[key] = vec if key not in targ_sum else targ_sum[key] + vec
        n_seen += 1
        if (i + 1) % 20 == 0:
            print(f"[mech]   baseline {i + 1}/{len(items)}")
    target = {key: (np.zeros_like(v) if args.ablate == "zero" else v / n_seen)
              for key, v in targ_sum.items()}

    # ── sweep ─────────────────────────────────────────────────────────────────────
    results: list[dict] = []
    for li in layers:
        for comp in COMPONENTS:
            tvec = target[(comp, li)]
            per_item_kl: list[float] = []
            per_item_cc: list[int] = []
            kl_by_cc: dict[int, list[float]] = {0: [], 1: [], 2: []}
            for r in items:
                logits = knockout_forward(COMPILE_GATE + r["input"], model, tok,
                                          torch_mod, comp, li, tvec)
                kl = kl_div(log_softmax(logits), base_logp[r["input"]])
                per_item_kl.append(kl)
                per_item_cc.append(cc_of[r["input"]])
                kl_by_cc[cc_of[r["input"]]].append(kl)
            r_sp, p_sp = spearman(per_item_cc, per_item_kl)
            diff = two_sample_t(kl_by_cc[2], kl_by_cc[0])  # c2 vs c0
            results.append({
                "layer": li, "component": comp,
                "kl_c0": round(float(np.mean(kl_by_cc[0])), 5),
                "kl_c1": round(float(np.mean(kl_by_cc[1])), 5),
                "kl_c2": round(float(np.mean(kl_by_cc[2])), 5),
                "spearman_r": r_sp, "spearman_p": p_sp,
                "c2_vs_c0": diff,
            })
        if (li + 1) % 8 == 0 or li == layers[-1]:
            print(f"[mech]   swept through L{li}")

    # ── localize: monotonic object-load hits ─────────────────────────────────────
    def is_hit(row):
        return bool(row["spearman_r"] is not None and row["spearman_r"] > 0
                    and (row["spearman_p"] or 1) < 0.05
                    and (row["c2_vs_c0"]["diff"] or 0) > 0
                    and (row["c2_vs_c0"]["t"] or 0) > 2.0)

    hits = [r for r in results if is_hit(r)]
    hits_sorted = sorted(hits, key=lambda r: -(r["spearman_r"] or 0))
    top = sorted(results, key=lambda r: -(r["spearman_r"] or 0))[:10]
    n_attn_hits = sum(1 for r in hits if r["component"] == "attn")
    n_mlp_hits = sum(1 for r in hits if r["component"] == "mlp")
    mechanism_localized = len(hits) > 0
    if not mechanism_localized:
        interpretation = (
            "NO monotonic object-load hit in any component's last-token write -> "
            "object-application is NOT localized to a single component (distributed / "
            "attention-PATTERN level); next probe = attention EDGE knockout "
            "(predicate->object), not component write.")
    else:
        dom = "ATTENTION (o_proj)" if n_attn_hits >= n_mlp_hits else "MLP"
        interpretation = (
            f"object-application LOCALIZES to {n_attn_hits} attn + {n_mlp_hits} mlp "
            f"(layer,component) hits; dominant pathway = {dom}. "
            + ("Confirms the OV/value-register hypothesis; FFN C-field was a readout."
               if n_attn_hits >= n_mlp_hits else
               "Object-load lives in MLP-write, not attention - revises hypothesis."))

    verdict = {
        "model": model_name, "n_layers": n_layers, "ablate": args.ablate,
        "n_items": len(items), "n_per_group": {k: len(v) for k, v in groups.items()},
        "n_hits": len(hits), "n_attn_hits": n_attn_hits, "n_mlp_hits": n_mlp_hits,
        "mechanism_localized": mechanism_localized,
        "hits": hits_sorted, "top10_by_spearman": top,
        "interpretation": interpretation, "all_results": results,
    }

    print("\n" + "═" * 82)
    print(f"OBJECT-APPLICATION MECHANISM SWEEP — {model_name}")
    print("═" * 82)
    print(f"  swept {len(layers)}L x {len(COMPONENTS)} comps; "
          f"hits={len(hits)} (attn={n_attn_hits} mlp={n_mlp_hits})")
    print("  top by Spearman(KL, object-count):")
    for r in top[:8]:
        print(f"    L{r['layer']:>2} {r['component']:<4} r={r['spearman_r']} "
              f"p={r['spearman_p']}  KL {r['kl_c0']}/{r['kl_c1']}/{r['kl_c2']}  "
              f"c2-c0 t={r['c2_vs_c0']['t']}")
    print(f"  >> {interpretation}")
    print("═" * 82 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    (RESULTS_DIR / f"verdict_{slug}.json").write_text(
        json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "ablate": args.ablate, "layers": layers, "max_per_group": max_per_group,
        "seed": args.seed, "probe_set": str(READING_PROBES.relative_to(_ROOT)),
        "method": "Mean/zero-ablate the LAST-token output (matched single position, no "
                  "length confound) of each layer's attention-write (o_proj) and "
                  "MLP-write; next-token KL per object-count group; localize via "
                  "Spearman(KL, object-count) + c2-vs-c0 t. Attn-vs-MLP = OV-vs-FFN.",
        "scope": "Hunts the object-application mechanism after s250 showed the FFN "
                 "C-field is a readout register, not the mechanism.",
    }
    (RESULTS_DIR / f"meta_{slug}.json").write_text(
        json.dumps(_json_safe(meta), indent=2), encoding="utf-8")
    print(f"[mech] wrote {RESULTS_DIR}/verdict_{slug}.json (+ meta)")


if __name__ == "__main__":
    main()
