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

    # K = const/discard: its semantic call is exclusion/selection markers. To avoid
    # conflating "removed a semantic K-trigger" with "broke the last-token composition"
    # (generic/positional function words), we score SEM-trigger drops vs GENERIC drops.
    # If generic dominates, K's firing is NOT anchored on a bakeable semantic token.
    SEM = {"only", "sole", "solely", "single", "just", "isolated", "selected",
           "recovered", "simplest", "one", "five", "no", "nothing", "except",
           "all", "entire", "whole"}

    base = [k_peak(rcc, tap / str(i_tgt + ti)) for ti in range(len(targets))]
    var_k: dict[int, list] = {ti: [] for ti in range(len(targets))}
    for vi, (ti, wi, w, _txt) in enumerate(variants):
        kz = k_peak(rcc, tap / str(i_var + vi))
        var_k[ti].append((wi, w, kz, base[ti] - kz))

    # summarize per target: SEM-trigger vs GENERIC max drop (the corrected metric)
    per_target = []
    sem_wins = 0
    gen_wins = 0
    for ti, p in enumerate(targets):
        rows = var_k[ti]
        rows_sorted = sorted(rows, key=lambda r: -r[3])  # by drop desc
        top = rows_sorted[0]
        sem_d = [d for (_wi, w, _kz, d) in rows if w.lower().strip(".,") in SEM]
        gen_d = [d for (_wi, w, _kz, d) in rows if w.lower().strip(".,") not in SEM]
        max_sem = max(sem_d) if sem_d else 0.0
        max_gen = max(gen_d) if gen_d else 0.0
        sem_dominates = max_sem > max_gen
        if sem_dominates:
            sem_wins += 1
        else:
            gen_wins += 1
        per_target.append({
            "prompt": p.prompt, "base_Kz": round(base[ti], 2),
            "top_word": top[1], "top_drop": round(top[3], 2),
            "max_sem_drop": round(max_sem, 2), "max_gen_drop": round(max_gen, 2),
            "sem_dominates": bool(sem_dominates),
            "top3": [(w, round(d, 2)) for (_wi, w, _kz, d) in rows_sorted[:3]],
        })
    localized_count, diffuse_count = sem_wins, gen_wins

    mean_sem = float(np.mean([r["max_sem_drop"] for r in per_target]))
    mean_gen = float(np.mean([r["max_gen_drop"] for r in per_target]))
    print(f"[localize] z_thresh={zt}  targets={len(targets)}  nonce={args.nonce!r}")
    print("\n base Kz | max-SEM drop | max-GEN drop | dominates | prompt[:48]")
    print("---------+--------------+--------------+-----------+-----------")
    for r in per_target:
        dom = "SEM" if r["sem_dominates"] else "GEN"
        print(f" {r['base_Kz']:7.2f} | {r['max_sem_drop']:12.2f} | {r['max_gen_drop']:12.2f} | "
              f"{dom:9s} | {r['prompt'][:48]}")
    # corrected metric: semantic-trigger anchoring vs generic/positional disruption
    verdict = ("TOKEN-ANCHORED" if sem_wins > gen_wins else "STRUCTURAL")
    print(f"\n[localize] SEM-trigger dominates: {sem_wins}/{len(targets)}  "
          f"GENERIC/positional dominates: {gen_wins}/{len(targets)}")
    print(f"[localize] mean max-SEM drop {mean_sem:.2f}  vs  mean max-GEN drop {mean_gen:.2f}")
    print(f"[localize] VERDICT: K firing is {verdict}  "
          f"({'token-bake viable' if verdict=='TOKEN-ANCHORED' else 'no bakeable semantic K-token — needs routing bake; consistent with s275 circuits-in-compute'})")

    result = {
        "model": args.gguf, "nonce": args.nonce, "z_thresh": zt,
        "n_targets": len(targets), "sem_dominates_count": sem_wins,
        "generic_dominates_count": gen_wins, "mean_max_sem_drop": round(mean_sem, 2),
        "mean_max_gen_drop": round(mean_gen, 2), "verdict": verdict,
        "per_target": per_target,
    }
    (out / "stage1_localization.json").write_text(json.dumps(result, indent=2))
    print(f"[localize] wrote {out}/stage1_localization.json")


if __name__ == "__main__":
    main()
