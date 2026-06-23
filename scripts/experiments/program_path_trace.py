#!/usr/bin/env python3
# register: topological/routing (FFN gate β-program path)
"""Program Path Trace — monotonic alignment of FFN gate z-maps to `fired_sequence`.

This is the second sequence-level attempt after `program_sequence_trace.py`. The event
stream/LCS tracer found C-presence but not reliable order: long decoded streams made LCS
mostly a coverage metric. This experiment instead asks the sharper question directly:
for a certified β-program such as [S, B, C, C], is the best monotonic layer
path for that exact order stronger than reversed/shuffled same-multiset programs?

Measurement contract:
  • register: FFN gate routing register (`mlp.gate_proj`), sign(gate)-CMR;
  • null: matched-prefix `gateneutral` by default;
  • per item: capture content-token x layer z(op) over B/C/S;
  • layer evidence: for op at layer L, max z(op) over content tokens;
  • path: dynamic program chooses nondecreasing layers for the ordered truth steps;
  • controls: reversed sequence and all unique non-truth permutations of the same steps.

If a discrete-ish β-program order is readable, truth path score should beat
same-multiset permutation controls, not merely have high C load.

Usage:
    uv run python scripts/experiments/program_path_trace.py --smoke
    uv run python scripts/experiments/program_path_trace.py \
      --model Qwen/Qwen3-14B --probe-set data/firing-probes.const.jsonl

License: MIT. AGENTS.md S5 λ provenance.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from ffn_program_decode import (  # noqa: E402
    FIRING_SET,
    build_firing_corpus,
    classify_positions,
    perm_null_accuracy,
    zone_layers,
)
from opcode_monitor_v2 import (  # noqa: E402
    COMPILE_GATE,
    _git_sha,
    _json_safe,
    _transformers_version,
    calibrate_v2,
    forward_all_positions,
    gate_prefix_len,
    load_model_and_tokenizer,
)

RESULTS_DIR = _ROOT / "results" / "program-path-trace"


def unique_permutations(seq: list[str], limit: int = 120) -> list[list[str]]:
    """Unique permutations, capped for future longer traces."""
    out = []
    seen = set()
    for p in itertools.permutations(seq):
        if p in seen:
            continue
        seen.add(p)
        out.append(list(p))
        if len(out) >= limit:
            break
    return out


def layer_op_evidence(
    reads: list[dict[int, dict[str, float]]], layers: list[int], op_set: list[str]
) -> dict[str, dict[int, tuple[float, int | None]]]:
    """op -> layer -> (max_z_over_content_tokens, best_content_pos)."""
    out: dict[str, dict[int, tuple[float, int | None]]] = {op: {} for op in op_set}
    for op in op_set:
        for li in layers:
            best_z = -float("inf")
            best_pos = None
            for pos_i, r in enumerate(reads):
                if li not in r:
                    continue
                z = float(r[li][op])
                if z > best_z:
                    best_z = z
                    best_pos = pos_i
            out[op][li] = (best_z, best_pos)
    return out


def monotonic_path_score(
    seq: list[str], evidence: dict[str, dict[int, tuple[float, int | None]]],
    layers: list[int], *, strict: bool = False,
) -> dict:
    """Best path assigning each op in seq to a nondecreasing layer.

    Score is mean z over steps. The DP maximizes sum z; z values are matched-null
    relational scores, so controls using the same multiset test ORDER rather than load.
    """
    if not seq or not layers:
        return {"score_sum": 0.0, "score_mean": 0.0, "path": []}
    n, m = len(seq), len(layers)
    dp = np.full((n, m), -np.inf, dtype=float)
    back = np.full((n, m), -1, dtype=int)

    for k, li in enumerate(layers):
        dp[0, k] = evidence[seq[0]][li][0]
    for j in range(1, n):
        for k, li in enumerate(layers):
            prev_end = k if not strict else k - 1
            if prev_end < 0:
                continue
            prev_vals = dp[j - 1, : prev_end + 1]
            pk = int(np.argmax(prev_vals))
            pv = float(prev_vals[pk])
            if np.isneginf(pv):
                continue
            dp[j, k] = pv + evidence[seq[j]][li][0]
            back[j, k] = pk

    end = int(np.argmax(dp[-1]))
    score_sum = float(dp[-1, end])
    if np.isneginf(score_sum):
        return {"score_sum": None, "score_mean": None, "path": []}

    idxs = [end]
    for j in range(n - 1, 0, -1):
        idxs.append(int(back[j, idxs[-1]]))
    idxs.reverse()
    path = []
    for j, k in enumerate(idxs):
        li = layers[k]
        z, pos = evidence[seq[j]][li]
        path.append({"step": j, "op": seq[j], "layer": li,
                     "content_pos": pos, "z": round(float(z), 4)})
    return {
        "score_sum": round(score_sum, 4),
        "score_mean": round(score_sum / len(seq), 4),
        "path": path,
    }


def score_controls(
    truth: list[str], evidence: dict[str, dict[int, tuple[float, int | None]]],
    layers: list[int], *, strict: bool = False,
) -> dict:
    truth_score = monotonic_path_score(truth, evidence, layers, strict=strict)
    rev = list(reversed(truth))
    reverse_score = monotonic_path_score(rev, evidence, layers, strict=strict)
    perms = [p for p in unique_permutations(truth) if p != truth]
    perm_scores = [monotonic_path_score(p, evidence, layers, strict=strict)
                   for p in perms]
    perm_means = [p["score_mean"] for p in perm_scores if p["score_mean"] is not None]
    t = truth_score["score_mean"]
    if t is None or not perm_means:
        rank_frac = None
        margin_best = None
        margin_mean = None
        beats_all = False
    else:
        ge = sum(1 for s in perm_means if s >= t)
        rank_frac = round(1.0 - ge / len(perm_means), 4)
        margin_best = round(t - max(perm_means), 4)
        margin_mean = round(t - float(np.mean(perm_means)), 4)
        beats_all = bool(t > max(perm_means))
    best_perm = None
    if perm_scores:
        def _score(x):
            return -float("inf") if x["score_mean"] is None else x["score_mean"]

        best_perm = max(perm_scores, key=_score)
    return {
        "truth": truth_score,
        "reverse_sequence": rev,
        "reverse": reverse_score,
        "n_permutation_controls": len(perm_scores),
        "perm_score_mean": round(float(np.mean(perm_means)), 4) if perm_means else None,
        "perm_score_max": round(float(np.max(perm_means)), 4) if perm_means else None,
        "truth_rank_frac": rank_frac,
        "truth_margin_vs_best_perm": margin_best,
        "truth_margin_vs_mean_perm": margin_mean,
        "truth_beats_all_permutations": beats_all,
        "best_permutation": best_perm,
    }


def _safe_slug(model_name: str, probe_set: str | None) -> str:
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    if probe_set:
        stem = Path(probe_set).stem
        slug += "_" + (stem.split(".")[-1] if "." in stem else stem)
    return slug


def _mean(xs: list[float | None]) -> float | None:
    vals = [x for x in xs if x is not None]
    return round(float(np.mean(vals)), 4) if vals else None


def run(
    model_name: str,
    probe_set: str,
    max_items: int | None,
    null_mode: str,
    zone_lo: float,
    zone_hi: float,
    n_perm_calib: int,
    ppc: int | None,
    null_cap: int | None,
    n_perm_stat: int,
    seed: int,
    strict_layers: bool,
) -> tuple[dict, list[dict], dict]:
    print("═" * 78)
    print("PROGRAM PATH TRACE — monotonic FFN gate path vs fired_sequence")
    print("═" * 78)
    firing, nonfiring = build_firing_corpus([Path(probe_set)])
    if max_items is not None:
        firing = firing[:max_items]
    print(
        f"[corpus] source={probe_set} firing={len(firing)} "
        f"nonfiring={len(nonfiring)}"
    )

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))
    print(f"[model] {model_name} layers={n_layers}")

    print(f"\n[calib] FFN gate register null_mode={null_mode} ...")
    rcc, calib = calibrate_v2(
        model, tok, torch_mod, layers, n_perm_calib, ppc, null_cap,
        null_mode=null_mode, hook="gate")
    crystal_layers = rcc.crystal_layers
    zlayers = zone_layers(crystal_layers, n_layers, zone_lo, zone_hi)
    print(f"[calib] crystal_layers={len(crystal_layers)}/{n_layers} zone={zlayers}")

    gate_n = gate_prefix_len(tok)
    per_item: list[dict] = []
    print(f"\n[decode] {len(firing)} items strict_layers={strict_layers} ...")
    for i, item in enumerate(firing):
        if i % 20 == 0:
            print(f"[decode]   item {i}/{len(firing)} ...")
        prompt = COMPILE_GATE + item["input"]
        store, n_tok = forward_all_positions(prompt, model, tok, torch_mod, layers,
                                             hook="gate")
        positions = list(range(min(gate_n, n_tok - 1), n_tok))
        reads = classify_positions(rcc, store, layers, positions)
        truth = list(item["fired_sequence"])

        ev_zone = layer_op_evidence(reads, zlayers, FIRING_SET)
        ev_all = layer_op_evidence(reads, crystal_layers, FIRING_SET)
        zone_scores = score_controls(truth, ev_zone, zlayers, strict=strict_layers)
        all_scores = score_controls(truth, ev_all, crystal_layers, strict=strict_layers)

        per_item.append({
            "input": item["input"],
            "category": item["category"],
            "dominant_fired": item["dominant_fired"],
            "fired_sequence": truth,
            "fired_multiset": item["fired_multiset"],
            "reduction_len": item["reduction_len"],
            "b_count": item.get("b_count"),
            "s_count": item.get("s_count"),
            "c_count": item.get("c_count"),
            "n_content_tokens": len(positions),
            "zone_layers": zlayers,
            "zone_path": zone_scores,
            "all_crystal_path": all_scores,
        })

    def vals(path_key: str, field: str) -> list[float | None]:
        return [p[path_key][field] for p in per_item]

    zone_truth = [p["zone_path"]["truth"]["score_mean"] for p in per_item]
    zone_rev = [p["zone_path"]["reverse"]["score_mean"] for p in per_item]
    zone_margin = vals("zone_path", "truth_margin_vs_best_perm")
    zone_rank = vals("zone_path", "truth_rank_frac")
    all_margin = vals("all_crystal_path", "truth_margin_vs_best_perm")
    all_rank = vals("all_crystal_path", "truth_rank_frac")

    # Item-level permutation-style null: does truth path beat all same-multiset orders?
    decoded_zone = ["win" if p["zone_path"]["truth_beats_all_permutations"] else "loss"
                    for p in per_item]
    decoded_all = ["win" if p["all_crystal_path"]["truth_beats_all_permutations"]
                   else "loss" for p in per_item]
    truth_win = ["win"] * len(per_item)
    zone_win_acc, zone_win_null, zone_win_p = perm_null_accuracy(
        decoded_zone, truth_win, n_perm_stat, seed)
    all_win_acc, all_win_null, all_win_p = perm_null_accuracy(
        decoded_all, truth_win, n_perm_stat, seed)

    verdict = {
        "model": model_name,
        "n_layers": n_layers,
        "probe_set": probe_set,
        "n_items": len(per_item),
        "null_mode": null_mode,
        "strict_layers": strict_layers,
        "zone_depth": [zone_lo, zone_hi],
        "zone_layers": zlayers,
        "crystal_layers": crystal_layers,
        "truth_distribution": dict(Counter(p["dominant_fired"] for p in per_item)),
        "path_scores": {
            "zone_truth_score_mean": _mean(zone_truth),
            "zone_reverse_score_mean": _mean(zone_rev),
            "zone_truth_minus_reverse_mean": _mean([
                (a - b) if a is not None and b is not None else None
                for a, b in zip(zone_truth, zone_rev, strict=False)
            ]),
            "zone_margin_vs_best_perm_mean": _mean(zone_margin),
            "zone_truth_rank_frac_mean": _mean(zone_rank),
            "zone_truth_beats_all_n": int(sum(
                p["zone_path"]["truth_beats_all_permutations"] for p in per_item)),
            "zone_truth_beats_all_acc": round(zone_win_acc, 4),
            "zone_truth_beats_all_null": round(zone_win_null, 4),
            "zone_truth_beats_all_perm_p": round(zone_win_p, 4),
            "all_crystal_margin_vs_best_perm_mean": _mean(all_margin),
            "all_crystal_truth_rank_frac_mean": _mean(all_rank),
            "all_crystal_truth_beats_all_n": int(sum(
                p["all_crystal_path"]["truth_beats_all_permutations"]
                for p in per_item)),
            "all_crystal_truth_beats_all_acc": round(all_win_acc, 4),
            "all_crystal_truth_beats_all_null": round(all_win_null, 4),
            "all_crystal_truth_beats_all_perm_p": round(all_win_p, 4),
        },
        "by_category": {},
        "calib": calib,
    }

    for cat in sorted({p["category"] for p in per_item}):
        rows = [p for p in per_item if p["category"] == cat]
        verdict["by_category"][cat] = {
            "n": len(rows),
            "truth_distribution": dict(Counter(r["dominant_fired"] for r in rows)),
            "zone_truth_score_mean": _mean([
                r["zone_path"]["truth"]["score_mean"] for r in rows]),
            "zone_margin_vs_best_perm_mean": _mean([
                r["zone_path"]["truth_margin_vs_best_perm"] for r in rows]),
            "zone_truth_rank_frac_mean": _mean([
                r["zone_path"]["truth_rank_frac"] for r in rows]),
            "zone_truth_beats_all_n": int(sum(
                r["zone_path"]["truth_beats_all_permutations"] for r in rows)),
        }

    meta = {
        "model": model_name,
        "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "params": {
            "probe_set": probe_set,
            "max_items": max_items,
            "null_mode": null_mode,
            "zone_lo": zone_lo,
            "zone_hi": zone_hi,
            "n_perm_calib": n_perm_calib,
            "ppc": ppc,
            "null_cap": null_cap,
            "n_perm_stat": n_perm_stat,
            "seed": seed,
            "strict_layers": strict_layers,
        },
        "method": "Dynamic-program best monotonic layer path through FFN gate "
                  "relational z(op) evidence; truth fired_sequence compared against "
                  "reversed and all same-multiset permutation controls.",
    }
    return verdict, per_item, meta


def write_outputs(verdict: dict, per_item: list[dict], meta: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = _safe_slug(verdict["model"], verdict.get("probe_set"))
    if verdict.get("strict_layers"):
        slug += "_strict"
    (RESULTS_DIR / f"verdict_{slug}.json").write_text(
        json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
    (RESULTS_DIR / f"per_item_{slug}.json").write_text(
        json.dumps(_json_safe(per_item), indent=2), encoding="utf-8")
    (RESULTS_DIR / f"meta_{slug}.json").write_text(
        json.dumps(_json_safe(meta), indent=2), encoding="utf-8")
    print(f"[write] {RESULTS_DIR / f'verdict_{slug}.json'} (+ per_item, meta)")


def report(verdict: dict) -> None:
    s = verdict["path_scores"]
    print("\n" + "═" * 78)
    print("PROGRAM PATH TRACE — VERDICT")
    print("═" * 78)
    print(f"items={verdict['n_items']} truth={verdict['truth_distribution']}")
    print(f"crystal_layers={len(verdict['crystal_layers'])}/{verdict['n_layers']} "
          f"zone={verdict['zone_layers']} strict={verdict['strict_layers']}")
    print("\nZone monotonic path vs same-multiset controls:")
    print(f"  truth score mean:          {s['zone_truth_score_mean']}")
    print(f"  reverse score mean:        {s['zone_reverse_score_mean']}")
    print(f"  truth - reverse mean:      {s['zone_truth_minus_reverse_mean']}")
    print(f"  margin vs best perm mean:  {s['zone_margin_vs_best_perm_mean']}")
    print(f"  rank frac mean:            {s['zone_truth_rank_frac_mean']}")
    print(f"  beats all perms:           {s['zone_truth_beats_all_n']}/"
          f"{verdict['n_items']} (p={s['zone_truth_beats_all_perm_p']})")
    print("\nAll-crystal path control:")
    print(f"  margin vs best perm mean:  {s['all_crystal_margin_vs_best_perm_mean']}")
    print(f"  rank frac mean:            {s['all_crystal_truth_rank_frac_mean']}")
    print(f"  beats all perms:           {s['all_crystal_truth_beats_all_n']}/"
          f"{verdict['n_items']} (p={s['all_crystal_truth_beats_all_perm_p']})")
    print("\nBy category:")
    for cat, d in verdict["by_category"].items():
        print(f"  {cat}: n={d['n']} score={d['zone_truth_score_mean']} "
              f"margin={d['zone_margin_vs_best_perm_mean']} "
              f"rank={d['zone_truth_rank_frac_mean']} "
              f"beats={d['zone_truth_beats_all_n']}/{d['n']}")
    print("═" * 78 + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="Monotonic FFN β-program path tracer")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--probe-set", default="data/firing-probes.const.jsonl")
    ap.add_argument("--max-items", type=int, default=None)
    ap.add_argument("--null-mode", default="gateneutral",
                    choices=["gateneutral", "crosstask"])
    ap.add_argument("--zone-lo", type=float, default=0.70)
    ap.add_argument("--zone-hi", type=float, default=0.86)
    ap.add_argument("--n-perm-stat", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--strict-layers", action="store_true",
                    help="Require strictly increasing layers for successive steps")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model = args.model
    max_items = args.max_items
    if args.smoke:
        if model == "Qwen/Qwen3-14B":
            model = "Qwen/Qwen3-0.6B"
        n_perm_calib, ppc, null_cap = 80, 3, 200
        max_items = max_items or 6
        print("[smoke] Qwen3-0.6B small calibration")
    else:
        n_perm_calib, ppc, null_cap = 300, None, None

    verdict, per_item, meta = run(
        model, args.probe_set, max_items, args.null_mode, args.zone_lo, args.zone_hi,
        n_perm_calib, ppc, null_cap, args.n_perm_stat, args.seed,
        args.strict_layers)
    report(verdict)
    write_outputs(verdict, per_item, meta)


if __name__ == "__main__":
    main()
