"""Frame-invariance validation for the pristine llama.cpp tree-of-VSM tap.

The crystal Gram is frame-invariant (C2). So the SAME crystal probes, read
through two numeric frames — (a) transformers hooks on the HF model, (b) the
llama.cpp ``vsm_tap`` residual/register tap on the GGUF — must yield the SAME
9x9 sign-CMR opcode Gram.

  MATCH    -> the wrapper is validated AND we get an independent frame-invariance
              confirmation across the transformers<->llama.cpp numeric boundary.
  MISMATCH -> a finding about the frame; investigate before trusting MoE reads.

This is the read-only milestone of llama-cpp-vsm-wrapper.md. Only the activation
SOURCE differs between frames; the sign-CMR + centroid + Gram science is shared
(opcodes/classify.py, opcodes/vsm.py).

Usage:
  uv run python wrapper/frame_invariance.py \
      --gguf ~/localai/models/verbum-frameinv/Qwen3-0.6B-f16.gguf \
      --hf-model Qwen/Qwen3-0.6B --device mps --per-comb 15
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "opcodes"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import tap_loader  # noqa: E402
from classify import _centroids, load_consensus_gram  # noqa: E402
from probes import crystal_probes  # noqa: E402
from vsm import CRYSTAL, gram_from_centroids, offdiag_corr  # noqa: E402


def balanced_probes(per_comb: int) -> list:
    by_comb: dict[str, list] = {}
    for p in crystal_probes():
        if p.combinator in CRYSTAL:
            by_comb.setdefault(p.combinator, []).append(p)
    out = []
    for c in CRYSTAL:
        out.extend(by_comb.get(c, [])[:per_comb])
    return out


def frame_gram(feat_li: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """sign-CMR -> per-combinator centroids -> 9x9 Gram (identical to calibrate)."""
    G = np.asarray(feat_li, dtype=np.float64)
    S = np.sign(G)
    X = S - S.mean(axis=0)
    cents = _centroids(X, labels)
    return gram_from_centroids(cents)


def run_tap(tap_bin: Path, gguf: str, prompts: list[str], out_dir: Path, ngl: int) -> None:
    pf = out_dir / "prompts.txt"
    pf.write_text("\n".join(p.replace("\n", " ") for p in prompts) + "\n")
    cmd = [str(tap_bin), "--model", gguf, "--prompts-file", str(pf),
           "--out", str(out_dir), "-ngl", str(ngl)]
    print(f"[frame-inv] running tap: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def transformers_features(hf_model: str, device: str, prompts: list[str]) -> dict[int, list]:
    from trace import load  # noqa: E402
    from capture import capture_gate  # noqa: E402
    model, tok = load(hf_model, device)
    feat: dict[int, list] = {}
    for i, prompt in enumerate(prompts):
        cap = capture_gate(model, tok, prompt, register="gate")
        for li in cap.gate:
            feat.setdefault(li, []).append(np.asarray(cap.gate[li][-1], dtype=np.float64))
        if (i + 1) % 20 == 0:
            print(f"[frame-inv] transformers {i + 1}/{len(prompts)}")
    return {li: np.stack(v, axis=0) for li, v in feat.items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gguf", required=True)
    ap.add_argument("--hf-model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="mps", choices=["cpu", "mps", "cuda"])
    ap.add_argument("--per-comb", type=int, default=15)
    ap.add_argument("--ngl", type=int, default=999)
    ap.add_argument("--tap-bin", default=str(Path(__file__).resolve().parent / "build" / "vsm_tap"))
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    probes = balanced_probes(args.per_comb)
    prompts = [p.prompt for p in probes]
    labels = np.array([p.combinator for p in probes])
    print(f"[frame-inv] {len(probes)} probes "
          f"({dict((c, int((labels == c).sum())) for c in CRYSTAL)})")

    workdir = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="frameinv_"))
    tap_dir = workdir / "tap"
    tap_dir.mkdir(parents=True, exist_ok=True)

    # --- frame B: llama.cpp tap ---
    run_tap(Path(args.tap_bin), args.gguf, prompts, tap_dir, args.ngl)
    feat_lc = tap_loader.stack_last_token(tap_dir, len(probes), register="ffn_gate")

    # --- frame A: transformers hooks ---
    feat_tf = transformers_features(args.hf_model, args.device, prompts)

    consensus = load_consensus_gram()

    layers = sorted(set(feat_tf) & set(feat_lc))
    rows = []
    for li in layers:
        g_tf = frame_gram(feat_tf[li], labels)
        g_lc = frame_gram(feat_lc[li], labels)
        rows.append({
            "layer": li,
            "cross_frame_gc": round(offdiag_corr(g_tf, g_lc), 4),
            "tf_vs_consensus": round(offdiag_corr(g_tf, consensus), 4),
            "lc_vs_consensus": round(offdiag_corr(g_lc, consensus), 4),
        })

    cross = np.array([r["cross_frame_gc"] for r in rows])
    summary = {
        "n_probes": len(probes),
        "n_layers": len(layers),
        "cross_frame_gc_mean": round(float(np.nanmean(cross)), 4),
        "cross_frame_gc_median": round(float(np.nanmedian(cross)), 4),
        "cross_frame_gc_min": round(float(np.nanmin(cross)), 4),
        "per_layer": rows,
    }

    print("\n layer | cross-frame | tf~cons | lc~cons")
    print("-------+-------------+---------+--------")
    for r in rows:
        print(f" {r['layer']:5d} | {r['cross_frame_gc']:11.4f} | "
              f"{r['tf_vs_consensus']:7.4f} | {r['lc_vs_consensus']:7.4f}")
    print(f"\n[frame-inv] cross-frame Gram corr: mean={summary['cross_frame_gc_mean']} "
          f"median={summary['cross_frame_gc_median']} min={summary['cross_frame_gc_min']}")

    out_json = workdir / "frame_invariance.json"
    out_json.write_text(json.dumps(summary, indent=2))
    print(f"[frame-inv] wrote {out_json}")


if __name__ == "__main__":
    main()
