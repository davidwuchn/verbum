"""FFN-function bake — STAGE 1 CHARACTERIZATION (pre-bake baseline).

Before constructing any slot we must (i) characterize the KNOWN target — resident
K's per-layer firing signature — and (ii) confirm a novel head token is INERT
(no K firing un-baked), so there is headroom for a bake to install. See
ffn-function-bake-prereg.md (Stage-1 gate i-ii).

Method (all through the s275 llama.cpp tap, dense Qwen3-0.6B):
  1. calibrate the RelationalCrystalClassifier on balanced crystal probes + a
     natural-text null (identical to moe_calibrate / trace).
  2. classify the last token of kernel-certified programs:
       resident : "K a b", "K x y", ...   (kernel fires [K], NF = first arg)
       novel    : "Qz a b", "Qz x y", ...  (kernel inert; Qz has no K association)
  3. report per-layer K z-score profiles. Expect: resident K fires (K z high at
     K's bearing layers); novel Qz does NOT (inert baseline).

Nothing is baked here — this fixes the ground-truth signature the Stage-1 bake
must reproduce, and the inert baseline it must move.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "opcodes"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import tap_loader  # noqa: E402
from classify import RelationalCrystalClassifier  # noqa: E402
from probes import crystal_probes  # noqa: E402
from vsm import CRYSTAL  # noqa: E402
from trace import NULL_SENTENCES  # noqa: E402

# fresh atom pairs (kernel atoms; K is binary -> "HEAD a b")
_PAIRS = [("a", "b"), ("x", "y"), ("f", "g"), ("h", "z"), ("g", "x"), ("y", "f")]


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
    subprocess.run([str(tap_bin), "--model", gguf, "--prompts-file", str(pf),
                    "--out", str(out_dir), "-ngl", str(ngl)], check=True)


def k_profile(rcc: RelationalCrystalClassifier, dump_dir: Path) -> dict[int, float]:
    """Per-layer K z-score for the last token of one program."""
    gate = tap_loader.last_token(dump_dir, "ffn_gate")  # {li: [d]}
    tok = rcc.classify(gate)
    return {li: tok.per_layer[li]["K"] for li in tok.per_layer}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gguf", required=True)
    ap.add_argument("--per-comb", type=int, default=12)
    ap.add_argument("--novel-head", default="Qz")
    ap.add_argument("--ngl", type=int, default=999)
    ap.add_argument("--tap-bin", default=str(Path(__file__).resolve().parent / "build" / "vsm_tap"))
    ap.add_argument("--out", default="results/ffn-bake/stage1-qwen3-0-6b")
    args = ap.parse_args()

    cal = balanced_probes(args.per_comb)
    cal_labels = np.array([p.combinator for p in cal])
    resident = [f"K {a} {b}" for a, b in _PAIRS]
    novel = [f"{args.novel_head} {a} {b}" for a, b in _PAIRS]
    prompts = [p.prompt for p in cal] + list(NULL_SENTENCES) + resident + novel
    n_cal, n_null = len(cal), len(NULL_SENTENCES)
    i_res = n_cal + n_null
    i_nov = i_res + len(resident)

    out = Path(args.out)
    tap = out / "tap"
    tap.mkdir(parents=True, exist_ok=True)
    have = all((tap / str(i) / "manifest.json").exists() for i in range(len(prompts)))
    if have:
        print(f"[stage1] reusing dump {tap}")
    else:
        run_tap(Path(args.tap_bin), args.gguf, prompts, tap, args.ngl)

    # calibrate on crystal probes + cross-task null
    feat = tap_loader.stack_last_token(tap, n_cal, "ffn_gate")
    null = {li: np.concatenate([tap_loader.load_register(tap / str(i), "ffn_gate")[li]
                                for i in range(n_cal, n_cal + n_null)], axis=0)
            for li in feat}
    layers = sorted(feat)
    rcc = RelationalCrystalClassifier(layers, consensus_gram="auto")
    rcc.calibrate(feat, cal_labels, null_gate_by_layer=null)
    bearing = rcc.crystal_layers

    res_prof = [k_profile(rcc, tap / str(i_res + j)) for j in range(len(resident))]
    nov_prof = [k_profile(rcc, tap / str(i_nov + j)) for j in range(len(novel))]

    def agg(profs):
        return {li: float(np.mean([p[li] for p in profs])) for li in layers}
    res_mean, nov_mean = agg(res_prof), agg(nov_prof)

    zt = rcc.z_thresh
    res_fire = [li for li in bearing if res_mean[li] > zt]
    nov_fire = [li for li in bearing if nov_mean[li] > zt]

    print(f"[stage1] crystal-bearing layers: {bearing}")
    print(f"[stage1] z_thresh={zt}  pairs={_PAIRS}")
    print("\n layer | K z (resident 'K a b') | K z (novel '%s a b')" % args.novel_head)
    print("-------+------------------------+---------------------")
    for li in bearing:
        mark = "  <== K fires" if res_mean[li] > zt else ""
        print(f" {li:5d} | {res_mean[li]:22.3f} | {nov_mean[li]:19.3f}{mark}")
    print(f"\n[stage1] resident K fires at bearing layers: {res_fire}")
    print(f"[stage1] novel '{args.novel_head}' fires K at:  {nov_fire}  (want [] = inert)")
    res_peak = max(res_mean[li] for li in bearing)
    nov_peak = max(nov_mean[li] for li in bearing)
    print(f"[stage1] peak K z: resident={res_peak:.3f}  novel={nov_peak:.3f}  "
          f"separation={res_peak - nov_peak:.3f}")

    result = {
        "model": args.gguf, "novel_head": args.novel_head, "pairs": _PAIRS,
        "z_thresh": zt, "bearing_layers": bearing,
        "resident_K_zprofile": res_mean, "novel_K_zprofile": nov_mean,
        "resident_fires_at": res_fire, "novel_fires_at": nov_fire,
        "resident_peak_Kz": res_peak, "novel_peak_Kz": nov_peak,
        "verdict": {
            "resident_K_has_signature": len(res_fire) > 0,
            "novel_head_inert": len(nov_fire) == 0,
            "headroom_ok": len(res_fire) > 0 and len(nov_fire) == 0,
        },
    }
    (out / "stage1_characterization.json").write_text(json.dumps(result, indent=2))
    print(f"\n[stage1] headroom_ok={result['verdict']['headroom_ok']} "
          f"(resident fires & novel inert) -> {out}/stage1_characterization.json")


if __name__ == "__main__":
    main()
