"""FFN-function bake — STAGE 1 LOCALIZATION: is K's natural-language firing
token-anchored (bakeable via a token slot) or structural (needs a routing bake)?

Leave-one-out on held-out K-firing sentences: replace each word with a neutral
nonce, one at a time, and measure the drop in the last-token K z-score. If a
SPECIFIC word's removal collapses K (fire -> no-fire), K is token-anchored and a
token-bake is the right mechanism. If K survives every single-word swap (diffuse,
small drops), K is STRUCTURAL — consistent with s275 circuits-in-compute (opcodes
are routing, not token/weight-localized) — and the bake must install routing, not
a token slot.

Measurement-only (reuses the s275 tap on dense Qwen3-0.6B). Nothing is baked.
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


def run_tap(tap_bin: Path, gguf: str, prompts: list[str], out_dir: Path, ngl: int) -> None:
    pf = out_dir / "prompts.txt"
    pf.write_text("\n".join(p.replace("\n", " ") for p in prompts) + "\n")
    subprocess.run([str(tap_bin), "--model", gguf, "--prompts-file", str(pf),
                    "--out", str(out_dir), "-ngl", str(ngl)], check=True)


def k_peak(rcc: RelationalCrystalClassifier, dump_dir: Path) -> float:
    gate = tap_loader.last_token(dump_dir, "ffn_gate")
    tok = rcc.classify(gate)
    return max(tok.per_layer[li]["K"] for li in tok.per_layer)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gguf", required=True)
    ap.add_argument("--per-comb", type=int, default=12)
    ap.add_argument("--n-targets", type=int, default=8, help="held-out K sentences to localize")
    ap.add_argument("--nonce", default="thing")
    ap.add_argument("--ngl", type=int, default=999)
    ap.add_argument("--tap-bin", default=str(Path(__file__).resolve().parent / "build" / "vsm_tap"))
    ap.add_argument("--out", default="results/ffn-bake/stage1-localize-qwen3-0-6b")
    args = ap.parse_args()

    kp = [p for p in crystal_probes() if p.combinator == "K"]
    by: dict[str, list] = {}
    for p in crystal_probes():
        if p.combinator in CRYSTAL:
            by.setdefault(p.combinator, []).append(p)
    cal = []
    for c in CRYSTAL:
        cal.extend(by[c][:args.per_comb])
    cal_labels = np.array([p.combinator for p in cal])
    n_cal, n_null = len(cal), len(NULL_SENTENCES)

    # held-out K targets (after the calibration slice)
    targets = kp[args.per_comb:args.per_comb + args.n_targets]

    # build leave-one-out variants (replace each whitespace word with the nonce)
    variants = []          # (target_idx, word_idx, original_word, text)
    for ti, p in enumerate(targets):
        words = p.prompt.split()
        for wi, w in enumerate(words):
            v = words.copy()
            v[wi] = args.nonce
            variants.append((ti, wi, w, " ".join(v)))

    prompts = ([p.prompt for p in cal] + list(NULL_SENTENCES)
               + [p.prompt for p in targets]
               + [t[3] for t in variants])
    i_tgt = n_cal + n_null
    i_var = i_tgt + len(targets)

    out = Path(args.out)
    tap = out / "tap"
    tap.mkdir(parents=True, exist_ok=True)
    if all((tap / str(i) / "manifest.json").exists() for i in range(len(prompts))):
        print(f"[localize] reusing dump {tap}")
    else:
        run_tap(Path(args.tap_bin), args.gguf, prompts, tap, args.ngl)

    feat = tap_loader.stack_last_token(tap, n_cal, "ffn_gate")
    null = {li: np.concatenate([tap_loader.load_register(tap / str(i), "ffn_gate")[li]
                                for i in range(n_cal, n_cal + n_null)], axis=0)
            for li in feat}
    layers = sorted(feat)
    rcc = RelationalCrystalClassifier(layers, consensus_gram="auto")
    rcc.calibrate(feat, cal_labels, null_gate_by_layer=null)
    zt = rcc.z_thresh

    base = [k_peak(rcc, tap / str(i_tgt + ti)) for ti in range(len(targets))]
    var_k: dict[int, list] = {ti: [] for ti in range(len(targets))}
    for vi, (ti, wi, w, _txt) in enumerate(variants):
        kz = k_peak(rcc, tap / str(i_var + vi))
        var_k[ti].append((wi, w, kz, base[ti] - kz))

    # summarize per target: biggest single-word drop, and whether it kills firing
    per_target = []
    diffuse_count = 0
    localized_count = 0
    for ti, p in enumerate(targets):
        rows = var_k[ti]
        rows_sorted = sorted(rows, key=lambda r: -r[3])  # by drop desc
        top = rows_sorted[0]
        # "killed" = a single-word swap drops K below the fire threshold
        killed = base[ti] > zt and (base[ti] - top[3]) < zt
        if killed:
            localized_count += 1
        else:
            diffuse_count += 1
        per_target.append({
            "prompt": p.prompt, "base_Kz": round(base[ti], 2),
            "top_word": top[1], "top_drop": round(top[3], 2),
            "resid_after_top": round(base[ti] - top[3], 2),
            "killed_by_one_word": bool(killed),
            "top3": [(w, round(d, 2)) for (_wi, w, _kz, d) in rows_sorted[:3]],
        })

    print(f"[localize] z_thresh={zt}  targets={len(targets)}  nonce={args.nonce!r}")
    print("\n base Kz | top-drop word (drop) | resid | killed?  | prompt[:52]")
    print("---------+----------------------+-------+----------+-----------")
    for r in per_target:
        print(f" {r['base_Kz']:7.2f} | {r['top_word'][:14]:14s}({r['top_drop']:5.2f}) | "
              f"{r['resid_after_top']:5.2f} | {str(r['killed_by_one_word']):8s} | {r['prompt'][:52]}")
    verdict = ("TOKEN-ANCHORED" if localized_count > diffuse_count else "STRUCTURAL")
    print(f"\n[localize] single-word KILLS firing: {localized_count}/{len(targets)}  "
          f"(survives: {diffuse_count})")
    print(f"[localize] VERDICT: K firing is {verdict}  "
          f"({'token-bake viable' if verdict=='TOKEN-ANCHORED' else 'needs routing bake — consistent with s275 circuits-in-compute'})")

    result = {
        "model": args.gguf, "nonce": args.nonce, "z_thresh": zt,
        "n_targets": len(targets), "localized_count": localized_count,
        "diffuse_count": diffuse_count, "verdict": verdict, "per_target": per_target,
    }
    (out / "stage1_localization.json").write_text(json.dumps(result, indent=2))
    print(f"[localize] wrote {out}/stage1_localization.json")


if __name__ == "__main__":
    main()
