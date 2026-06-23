#!/usr/bin/env python3
# register: topological/routing (FFN gate β-program sequence)
"""Program Sequence Trace — align decoded FFN opcode events to `fired_sequence`.

s249 follow-up. `ffn_program_decode.py` showed Qwen3-14B significantly tracks the
corrected constant/applicative C-vs-S program label, while 8B was smeared. But that
script reads dominant/graded structure, not the ordered β-reduction program. This
experiment reuses the validated relational opcode reader (`RelationalCrystalClassifier`)
and the per-token machinery from `opcode_monitor_v2.py` to decode a token-layer event
sequence from the FFN gate register and align it against each probe's certified
`fired_sequence`.

Measurement contract (audit-aware):
  • register: FFN gate routing register (`mlp.gate_proj`), sign(gate)-CMR;
  • null: matched-prefix `gateneutral` by default — composition above gate framing;
  • readout: per content token x crystal layer z-scores over K/I/B/C/S/D/W/Y/WHNF;
  • event: argmax over the fired set {B,C,S} with z >= --z-event;
  • program score: LCS(truth fired_sequence, decoded event sequence), plus compressed
    and layer-dominant variants.

This is intentionally conservative: raw argmax tracers over-read common-mode; this uses
the validated relational reader and reports sequence metrics rather than claiming a
crisp instruction tape from a single layer.

Usage:
    uv run python scripts/experiments/program_sequence_trace.py --smoke
    uv run python scripts/experiments/program_sequence_trace.py \
      --model Qwen/Qwen3-14B --probe-set data/firing-probes.const.jsonl

License: MIT. AGENTS.md S5 λ provenance.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Iterable
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

RESULTS_DIR = _ROOT / "results" / "program-sequence-trace"


def lcs_len(a: list[str], b: list[str]) -> int:
    """Length of the longest common subsequence, preserving duplicates."""
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            cur[j] = prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]


def compress_runs(seq: Iterable[str]) -> list[str]:
    out: list[str] = []
    for x in seq:
        if not out or out[-1] != x:
            out.append(x)
    return out


def event_sequence(
    reads: list[dict[int, dict[str, float]]],
    layers: list[int],
    *,
    z_event: float,
    op_set: list[str],
) -> tuple[list[str], list[dict]]:
    """Flatten token-layer argmax events in layer-major order.

    Layer-major order matches the transformer reduction axis: the residual program state
    advances with depth; token position is the within-layer spatial/program-value axis.
    """
    seq: list[str] = []
    events: list[dict] = []
    for li in layers:
        for pos_i, r in enumerate(reads):
            if li not in r:
                continue
            zmap = r[li]
            op = max(op_set, key=lambda k: zmap[k])
            z = float(zmap[op])
            if z >= z_event:
                seq.append(op)
                events.append({"layer": li, "content_pos": pos_i, "op": op,
                               "z": round(z, 4)})
    return seq, events


def layer_dominant_sequence(
    reads: list[dict[int, dict[str, float]]],
    layers: list[int],
    *,
    z_event: float,
    op_set: list[str],
) -> list[str]:
    """One event per layer: mean z over content tokens, filtered by z_event."""
    seq: list[str] = []
    for li in layers:
        means = {}
        for op in op_set:
            vals = [r[li][op] for r in reads if li in r]
            means[op] = float(np.mean(vals)) if vals else float("nan")
        op = max(op_set, key=lambda k: means[k])
        if not np.isnan(means[op]) and means[op] >= z_event:
            seq.append(op)
    return seq


def seq_metrics(truth: list[str], decoded: list[str]) -> dict:
    lcs = lcs_len(truth, decoded)
    rev = list(reversed(decoded))
    rev_lcs = lcs_len(truth, rev)
    comp = compress_runs(decoded)
    comp_lcs = lcs_len(truth, comp)
    counts_t = Counter(truth)
    counts_d = Counter(decoded)
    bag_hit = sum(min(counts_t[o], counts_d[o]) for o in counts_t)
    return {
        "truth_len": len(truth),
        "decoded_len": len(decoded),
        "lcs": lcs,
        "lcs_frac": round(lcs / len(truth), 4) if truth else 0.0,
        "reverse_lcs": rev_lcs,
        "reverse_lcs_frac": round(rev_lcs / len(truth), 4) if truth else 0.0,
        "compressed_len": len(comp),
        "compressed_lcs": comp_lcs,
        "compressed_lcs_frac": round(comp_lcs / len(truth), 4) if truth else 0.0,
        "bag_hit": bag_hit,
        "bag_frac": round(bag_hit / len(truth), 4) if truth else 0.0,
        "decoded_counts": dict(counts_d),
        "decoded_compressed": comp[:80],
    }


def _safe_slug(model_name: str, probe_set: str | None) -> str:
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    if probe_set:
        stem = Path(probe_set).stem
        slug += "_" + (stem.split(".")[-1] if "." in stem else stem)
    return slug


def _mean(xs: list[float]) -> float | None:
    return round(float(np.mean(xs)), 4) if xs else None


def run(
    model_name: str,
    probe_set: str,
    max_items: int | None,
    null_mode: str,
    zone_lo: float,
    zone_hi: float,
    z_event: float,
    n_perm_calib: int,
    ppc: int | None,
    null_cap: int | None,
    n_perm_stat: int,
    seed: int,
) -> tuple[dict, list[dict], dict]:
    print("═" * 78)
    print("PROGRAM SEQUENCE TRACE — FFN gate β-program vs fired_sequence")
    print("═" * 78)
    paths = [Path(probe_set)]
    firing, nonfiring = build_firing_corpus(paths)
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
    truth_dom: list[str] = []
    pred_lcs_full: list[str] = []
    pred_lcs_layer: list[str] = []
    pred_bag_full: list[str] = []
    truth_has_op = {op: [] for op in FIRING_SET}
    decoded_has_op = {op: [] for op in FIRING_SET}

    print(f"\n[decode] {len(firing)} items z_event={z_event} ...")
    for i, item in enumerate(firing):
        if i % 20 == 0:
            print(f"[decode]   item {i}/{len(firing)} ...")
        prompt = COMPILE_GATE + item["input"]
        store, n_tok = forward_all_positions(prompt, model, tok, torch_mod, layers,
                                             hook="gate")
        positions = list(range(min(gate_n, n_tok - 1), n_tok))
        reads = classify_positions(rcc, store, layers, positions)

        truth = list(item["fired_sequence"])
        full_seq, events = event_sequence(reads, zlayers, z_event=z_event,
                                          op_set=FIRING_SET)
        layer_seq = layer_dominant_sequence(reads, zlayers, z_event=z_event,
                                            op_set=FIRING_SET)
        full_m = seq_metrics(truth, full_seq)
        layer_m = seq_metrics(truth, layer_seq)
        all_seq, _ = event_sequence(reads, crystal_layers, z_event=z_event,
                                    op_set=FIRING_SET)
        all_m = seq_metrics(truth, all_seq)

        # Convert sequence scores to simple item-level labels for permutation nulls.
        # A positive item means at least half the certified program is recoverable.
        pred_lcs_full.append("hit" if full_m["lcs_frac"] >= 0.5 else "miss")
        pred_lcs_layer.append("hit" if layer_m["lcs_frac"] >= 0.5 else "miss")
        pred_bag_full.append("hit" if full_m["bag_frac"] >= 0.5 else "miss")
        truth_dom.append("hit")  # all items have a recoverable truth by definition
        for op in FIRING_SET:
            truth_has = op in truth
            dec_has = op in full_seq
            truth_has_op[op].append(op if truth_has else f"not_{op}")
            decoded_has_op[op].append(op if dec_has else f"not_{op}")

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
            "decoded_event_seq": full_seq[:200],
            "decoded_layer_seq": layer_seq,
            "decoded_all_crystal_seq_prefix": all_seq[:200],
            "events": events[:500],
            "metrics_zone_events": full_m,
            "metrics_zone_layers": layer_m,
            "metrics_all_crystal_events": all_m,
        })

    # Summary statistics.
    full_fracs = [p["metrics_zone_events"]["lcs_frac"] for p in per_item]
    layer_fracs = [p["metrics_zone_layers"]["lcs_frac"] for p in per_item]
    all_fracs = [p["metrics_all_crystal_events"]["lcs_frac"] for p in per_item]
    bag_fracs = [p["metrics_zone_events"]["bag_frac"] for p in per_item]
    reverse_fracs = [p["metrics_zone_events"]["reverse_lcs_frac"] for p in per_item]

    op_presence = {}
    for op in FIRING_SET:
        acc, null, pval = perm_null_accuracy(
            decoded_has_op[op], truth_has_op[op], n_perm_stat, seed)
        op_presence[op] = {
            "presence_acc": round(acc, 4),
            "null_mean": round(null, 4),
            "perm_p": round(pval, 4),
            "truth_counts": dict(Counter(truth_has_op[op])),
            "decoded_counts": dict(Counter(decoded_has_op[op])),
        }

    verdict = {
        "model": model_name,
        "n_layers": n_layers,
        "probe_set": probe_set,
        "n_items": len(per_item),
        "null_mode": null_mode,
        "z_event": z_event,
        "zone_depth": [zone_lo, zone_hi],
        "zone_layers": zlayers,
        "crystal_layers": crystal_layers,
        "truth_distribution": dict(Counter(p["dominant_fired"] for p in per_item)),
        "sequence_alignment": {
            "zone_events_mean_lcs_frac": _mean(full_fracs),
            "zone_layer_mean_lcs_frac": _mean(layer_fracs),
            "all_crystal_events_mean_lcs_frac": _mean(all_fracs),
            "zone_events_mean_bag_frac": _mean(bag_fracs),
            "zone_events_mean_reverse_lcs_frac": _mean(reverse_fracs),
            "n_zone_events_half_recovered": int(sum(x >= 0.5 for x in full_fracs)),
            "n_zone_layers_half_recovered": int(sum(x >= 0.5 for x in layer_fracs)),
            "n_all_crystal_half_recovered": int(sum(x >= 0.5 for x in all_fracs)),
        },
        "op_presence": op_presence,
        "decoded_event_counts": dict(Counter(
            op for p in per_item for op in p["decoded_event_seq"])),
        "decoded_layer_counts": dict(Counter(
            op for p in per_item for op in p["decoded_layer_seq"])),
        "calib": calib,
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
            "z_event": z_event,
            "n_perm_calib": n_perm_calib,
            "ppc": ppc,
            "null_cap": null_cap,
            "n_perm_stat": n_perm_stat,
            "seed": seed,
        },
        "method": "RelationalCrystalClassifier on FFN gate sign-CMR with matched null; "
                  "content token x crystal-layer event sequence aligned to certified "
                  "lambda_ast.fired_sequence via LCS/bag metrics.",
    }
    return verdict, per_item, meta


def write_outputs(verdict: dict, per_item: list[dict], meta: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = _safe_slug(verdict["model"], verdict.get("probe_set"))
    (RESULTS_DIR / f"verdict_{slug}.json").write_text(
        json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
    (RESULTS_DIR / f"per_item_{slug}.json").write_text(
        json.dumps(_json_safe(per_item), indent=2), encoding="utf-8")
    (RESULTS_DIR / f"meta_{slug}.json").write_text(
        json.dumps(_json_safe(meta), indent=2), encoding="utf-8")
    print(f"[write] {RESULTS_DIR / f'verdict_{slug}.json'} (+ per_item, meta)")


def report(verdict: dict) -> None:
    s = verdict["sequence_alignment"]
    print("\n" + "═" * 78)
    print("PROGRAM SEQUENCE TRACE — VERDICT")
    print("═" * 78)
    print(f"items={verdict['n_items']} truth={verdict['truth_distribution']}")
    print(f"crystal_layers={len(verdict['crystal_layers'])}/{verdict['n_layers']} "
          f"zone={verdict['zone_layers']} z_event={verdict['z_event']}")
    print("\nSequence alignment vs fired_sequence:")
    print(f"  zone token-layer events mean LCS:   {s['zone_events_mean_lcs_frac']}")
    print(f"  zone layer-dominant mean LCS:      {s['zone_layer_mean_lcs_frac']}")
    print(
        "  all-crystal events mean LCS:       "
        f"{s['all_crystal_events_mean_lcs_frac']}"
    )
    print(f"  zone events bag coverage:          {s['zone_events_mean_bag_frac']}")
    print(
        "  reverse-order control LCS:         "
        f"{s['zone_events_mean_reverse_lcs_frac']}"
    )
    print(f"  half recovered: zone_events={s['n_zone_events_half_recovered']} "
          f"zone_layers={s['n_zone_layers_half_recovered']} "
          f"all_crystal={s['n_all_crystal_half_recovered']}")
    print("\nOp presence (decoded event contains op vs truth contains op):")
    for op, d in verdict["op_presence"].items():
        print(f"  {op}: acc={d['presence_acc']} null={d['null_mean']} p={d['perm_p']} "
              f"truth={d['truth_counts']} decoded={d['decoded_counts']}")
    print(f"\nDecoded event counts: {verdict['decoded_event_counts']}")
    print("═" * 78 + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="Trace FFN gate β-program sequence")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--probe-set", default="data/firing-probes.const.jsonl")
    ap.add_argument("--max-items", type=int, default=None)
    ap.add_argument("--null-mode", default="gateneutral",
                    choices=["gateneutral", "crosstask"])
    ap.add_argument("--zone-lo", type=float, default=0.70)
    ap.add_argument("--zone-hi", type=float, default=0.86)
    ap.add_argument("--z-event", type=float, default=2.0)
    ap.add_argument("--n-perm-stat", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
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
        args.z_event, n_perm_calib, ppc, null_cap, args.n_perm_stat, args.seed)
    report(verdict)
    write_outputs(verdict, per_item, meta)


if __name__ == "__main__":
    main()
