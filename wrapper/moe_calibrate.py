"""MoE crystal calibration through the llama.cpp tree-of-VSM tap.

The dense frame-invariance result (frame_invariance.py) proved the tap reads the
same crystal as transformers. This asks the C2/A2 MoE question the PyTorch
instrument could not (capture.py refuses MoE): does the router route the crystal?

Pipeline (all on the real serving host, via wrapper/vsm_tap):
  1. crystal probes + a natural-text NULL set -> vsm_tap batch dump.
  2. per-token EFFECTIVE gate = router-weighted sum over selected experts
     (tap_loader.load_moe_gate_effective) -> [T, n_ff_expert].
  3. RelationalCrystalClassifier.calibrate: per-layer sign-CMR centroids, 9x9
     Gram vs the bundled consensus crystal, cross-task null (the NULL set).
  4. measure_null_floor: shuffled-label floor (the mandatory yardstick gate).
  5. ffn_moe_topk coverage: per combinator, how many distinct experts fire
     (does 3B-active starve a reduction gate?).

Usage:
  uv run python wrapper/moe_calibrate.py \
      --gguf ~/localai/models/qwen3.5-35b-a3b/Qwen_Qwen3.5-35B-A3B-Q8_0.gguf \
      --per-comb 12 --out results/moe-crystal/qwen3-5-35b-a3b
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "opcodes"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import tap_loader  # noqa: E402
from classify import RelationalCrystalClassifier, measure_null_floor  # noqa: E402
from probes import crystal_probes  # noqa: E402
from vsm import CRYSTAL  # noqa: E402
from trace import NULL_SENTENCES  # noqa: E402


def balanced_probes(per_comb: int) -> list:
    by_comb: dict[str, list] = {}
    for p in crystal_probes():
        if p.combinator in CRYSTAL:
            by_comb.setdefault(p.combinator, []).append(p)
    out = []
    for c in CRYSTAL:
        out.extend(by_comb.get(c, [])[:per_comb])
    return out


def run_tap(tap_bin: Path, gguf: str, prompts: list[str], out_dir: Path, ngl: int) -> None:
    pf = out_dir / "prompts.txt"
    pf.write_text("\n".join(p.replace("\n", " ") for p in prompts) + "\n")
    cmd = [str(tap_bin), "--model", gguf, "--prompts-file", str(pf),
           "--out", str(out_dir), "-ngl", str(ngl)]
    print(f"[moe-cal] running tap on {len(prompts)} prompts ...")
    subprocess.run(cmd, check=True)


def topk_coverage(dump_root: Path, crystal_idx: list[int], labels: np.ndarray,
                  layers: list[int]) -> dict:
    """Per combinator: distinct experts fired (last token, mid-late layers)."""
    mid = [li for li in layers if li >= 0.5 * max(layers)]
    per_comb: dict[str, Counter] = {c: Counter() for c in CRYSTAL}
    for idx, lab in zip(crystal_idx, labels, strict=True):
        tk = tap_loader.load_moe_topk(dump_root / str(idx))
        for li in mid:
            if li in tk:
                per_comb[lab].update(int(e) for e in tk[li][-1].tolist())
    n_expert = None
    man = tap_loader.load_manifest(dump_root / str(crystal_idx[0]))
    for t in man["tensors"]:
        if t["register"] == "ffn_moe_probs":
            n_expert = int(t["ne"][0])
            break
    out = {}
    for c in CRYSTAL:
        cnt = per_comb[c]
        total = sum(cnt.values())
        out[c] = {
            "distinct_experts": len(cnt),
            "total_slots": total,
            "top5": cnt.most_common(5),
        }
    return {"n_expert": n_expert, "mid_late_layers": mid, "per_combinator": out}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gguf", required=True)
    ap.add_argument("--per-comb", type=int, default=12)
    ap.add_argument("--ngl", type=int, default=999)
    ap.add_argument("--tap-bin", default=str(Path(__file__).resolve().parent / "build" / "vsm_tap"))
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    probes = balanced_probes(args.per_comb)
    labels = np.array([p.combinator for p in probes])
    n_c = len(probes)
    n_n = len(NULL_SENTENCES)
    prompts = [p.prompt for p in probes] + list(NULL_SENTENCES)
    print(f"[moe-cal] {n_c} crystal probes "
          f"({dict((c, int((labels == c).sum())) for c in CRYSTAL)}) + {n_n} null")

    workdir = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="moecal_"))
    tap_dir = workdir / "tap"
    tap_dir.mkdir(parents=True, exist_ok=True)

    have_all = all((tap_dir / str(i) / "manifest.json").exists() for i in range(len(prompts)))
    if have_all:
        print(f"[moe-cal] reusing existing dump in {tap_dir}")
    else:
        run_tap(Path(args.tap_bin), args.gguf, prompts, tap_dir, args.ngl)

    # effective gate per probe
    eff = [tap_loader.load_moe_gate_effective(tap_dir / str(i)) for i in range(len(prompts))]
    layers = sorted(eff[0].keys())

    feat = {li: np.stack([eff[i][li][-1] for i in range(n_c)], axis=0) for li in layers}
    null = {li: np.concatenate([eff[i][li] for i in range(n_c, n_c + n_n)], axis=0)
            for li in layers}

    rcc = RelationalCrystalClassifier(layers, consensus_gram="auto")
    rcc.calibrate(feat, labels, null_gate_by_layer=null)
    summ = rcc.calibration_summary()

    floor = measure_null_floor(feat, labels, layers, null_gate_by_layer=null)

    # headline: are there crystal-bearing layers, and do they beat the shuffled floor?
    bearing = summ["crystal_layers"]
    gcs = [c["gc_consensus"] for c in summ["per_layer"].values()
           if isinstance(c["gc_consensus"], (int, float)) and not np.isnan(c["gc_consensus"])]
    result = {
        "model": args.gguf,
        "n_crystal": n_c, "n_null_tokens": int(next(iter(null.values())).shape[0]),
        "n_layers": len(layers),
        "crystal_bearing_layers": bearing,
        "n_bearing": len(bearing),
        "gc_consensus_max": round(float(np.max(gcs)), 3) if gcs else None,
        "gc_consensus_mean": round(float(np.mean(gcs)), 3) if gcs else None,
        "null_floor": floor,
        "per_layer": summ["per_layer"],
    }

    # topk expert-coverage is best-effort (ffn_moe_topk is a strided argsort view)
    try:
        result["topk_coverage"] = topk_coverage(tap_dir, list(range(n_c)), labels, layers)
    except Exception as e:  # noqa: BLE001
        print(f"[moe-cal] topk coverage skipped: {e}")
        result["topk_coverage"] = {"error": str(e)}

    print("\n layer | sil_z | gc_cons | bearing")
    print("-------+-------+---------+--------")
    for li in layers:
        c = summ["per_layer"][li]
        print(f" {li:5d} | {c['sil_z']:5.2f} | {c['gc_consensus']!s:>7} | {c['crystal_bearing']}")
    print(f"\n[moe-cal] crystal-bearing layers: {bearing}")
    print(f"[moe-cal] gc_consensus max={result['gc_consensus_max']} mean={result['gc_consensus_mean']}")
    print(f"[moe-cal] shuffled null: floor_z={floor['null_floor_z']} "
          f"bearing_frac={floor['shuffled_bearing_frac']} suspect={floor['suspect']}")
    cov = result.get("topk_coverage", {})
    if "per_combinator" in cov:
        print("[moe-cal] topk distinct-experts per combinator (mid-late layers):")
        for c in CRYSTAL:
            pc = cov["per_combinator"][c]
            print(f"   {c:4s}: {pc['distinct_experts']:4d} distinct / {pc['total_slots']} slots")

    out_json = workdir / "moe_calibration.json"
    out_json.write_text(json.dumps(result, indent=2))
    print(f"\n[moe-cal] wrote {out_json}")


if __name__ == "__main__":
    main()
