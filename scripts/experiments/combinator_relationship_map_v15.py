#!/usr/bin/env python3
# register: topological/routing
"""Combinator relationship map — the v15 (MLX/ternary) edition.

WHY a separate script (s220):
  combinator_relationship_map.py is HF-only (`AutoModelForCausalLM`, hooks
  `gate_proj`). v15 is an MLX ternary model with a shared-stride VSM stack and an
  outer recurrence — a different forward path. To HARVEST ecosystem-consensus
  combinator structure into the v15 base plate (consensus-delta-folding.md §s220,
  harvest fold Phase 1) we first need v15's OWN combinator Gram + centroids in the
  SAME routing register the consensus uses, and in the SAME d_ff space the Exp-B
  acceptance harness perturbs. This produces the target frame for align-before-fold.

THE ROUTING REGISTER (identical definition to the HF script):
  routing(x) = sign( FFN gate pre-activation )
  In v15 the live FFN gate is `stack_c.ffn_gate_plate` (a TernaryLinear); its
  forward is `ffn_gate = nn.silu(self.ffn_gate_plate(ffn_norm(x)))`. The PRE-silu
  output `ffn_gate_plate(ffn_norm(x))` is the gate pre-activation (== HF gate_proj
  output). We capture it at the LAST token of the LAST band of the LAST outer pass
  (the deepest reduction), per probe.
  centroid_k = mean over probes labelled k of sign(routing), AFTER common-mode
  removal (CMR); Gram[j,k] = cosine(centroid_j, centroid_k).  <- THE MAP

CAPTURE MECHANISM (the s218 orphan lesson):
  We wrap the LIVE plate object that `stack_c` actually calls
  (`model.stack_c.ffn_gate_plate`), NOT `model.ffn_gate_plate_c` — convert_ffn
  rebinds the model attribute but stack_c keeps its original reference (the bug
  that VOIDed s217 phase-2). The wrapper passes through and stashes the last output.

LOAD (mirrors exp_b_self_verifying_acceptance.py exactly):
  cfg=V15Config(); create_model_with_deltas(cfg, convert_ffn=True);
  load_weights(checkpoint, strict=False); reduce_all_deltas(model)  -> trained
  operator; n_outer from CLI; fixed_point_lambda=0 (eval only).
  Checkpoint is READ-ONLY (the running main:1 training writes step_NNNN/; we only
  read an already-frozen step).

Usage (GPU/MLX — run in tmux main:2 alongside main:1, per Michael s220):
  uv run python scripts/experiments/combinator_relationship_map_v15.py \
      --checkpoint checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz \
      --n-outer 2
  # smoke: add --limit-per 3 --n-perm 50

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
_V15 = _PROJECT_ROOT / "scripts" / "v15"
sys.path.insert(0, str(_V15))
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import mlx.core as mx  # noqa: E402
import mlx.nn as nn  # noqa: E402
from config import V15Config  # noqa: E402
from td_delta import reduce_all_deltas  # noqa: E402
from train_td import create_model_with_deltas  # noqa: E402

from verbum.probes.library import crystal_probes  # noqa: E402

RESULTS_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"
CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
TOKENIZER_NAME = "Qwen/Qwen3.6-27B"  # the shards-qwen36 BBPE tokenizer


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# ---- pure-numpy analysis helpers (copied from combinator_relationship_map.py
#      to avoid importing torch/transformers via that module) -----------------
def cmr(X):
    return X - X.mean(axis=0, keepdims=True)


def unit(v):
    return v / (np.linalg.norm(v) + 1e-30)


def centroids(X, labels):
    C = np.zeros((len(CRYSTAL), X.shape[1]), np.float64)
    for j, c in enumerate(CRYSTAL):
        m = labels == c
        C[j] = X[m].mean(axis=0)
    return C


def gram(C):
    U = np.array([unit(c) for c in C])
    return np.clip(U @ U.T, -1, 1)


def silhouette(X, labels):
    C = centroids(X, labels)
    U = np.array([unit(c) for c in C])
    Xu = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)
    sims = Xu @ U.T
    lab_idx = np.array([CRYSTAL.index(c) for c in labels])
    own = sims[np.arange(len(labels)), lab_idx]
    other = sims.copy()
    other[np.arange(len(labels)), lab_idx] = -np.inf
    return float(np.mean(own - other.max(axis=1)))


def silhouette_null(X, labels, n_perm=1000, seed=0):
    obs = silhouette(X, labels)
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = silhouette(X, rng.permutation(labels))
    sd = null.std() + 1e-30
    return {"silhouette": obs, "null_mean": float(null.mean()),
            "null_std": float(null.std()),
            "z": float((obs - null.mean()) / sd),
            "p_value": float((np.sum(null >= obs) + 1) / (n_perm + 1))}


def classical_mds(D, k=2):
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    w, V = np.linalg.eigh(B)
    order = np.argsort(w)[::-1]
    w, V = w[order][:k], V[:, order][:, :k]
    w = np.clip(w, 0, None)
    return V * np.sqrt(w + 1e-30)


# ---- probes -----------------------------------------------------------------
def load_probes(limit_per: int = 0, seed: int = 0):
    by = {c: [] for c in CRYSTAL}
    for p in crystal_probes():
        if p.combinator in by:
            by[p.combinator].append(p.prompt)
    rng = np.random.default_rng(seed)
    prompts, labels = [], []
    for c in CRYSTAL:
        ps = by[c]
        if limit_per and limit_per < len(ps):
            idx = sorted(rng.permutation(len(ps))[:limit_per])
            ps = [ps[i] for i in idx]
        prompts.extend(ps)
        labels.extend([c] * len(ps))
    return prompts, np.array(labels)


# ---- live-gate capture (wrap the reference stack_c actually calls) ----------
class GateCapture(nn.Module):
    """Pass-through wrapper that stashes the last pre-activation it produced."""

    def __init__(self, inner):
        super().__init__()
        self.inner = inner
        self.last = None

    def __call__(self, x):
        out = self.inner(x)
        self.last = mx.stop_gradient(out)
        return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--checkpoint", type=str,
                    default="checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz",
                    help="TRAINED v15 model.npz (READ-ONLY); '' = frozen base only")
    ap.add_argument("--extracted-model-path", type=str,
                    default="checkpoints/v15-extracted/model.npz/model.npz")
    ap.add_argument("--n-outer", type=int, default=2,
                    help="outer recurrence passes (match training K=2)")
    ap.add_argument("--stack", choices=["a", "c"], default="c",
                    help="which stack's ffn_gate_plate to read (c = Exp-B target)")
    ap.add_argument("--max-length", type=int, default=256)
    ap.add_argument("--limit-per", type=int, default=0,
                    help="cap probes/combinator (smoke)")
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", type=str, default="", help="output name suffix override")
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    prompts, labels = load_probes(args.limit_per, args.seed)
    counts = {c: int(np.sum(labels == c)) for c in CRYSTAL}
    log(f"[v15] {len(prompts)} crystal probes  {counts}")

    # tokenizer (offline; the shards-qwen36 BBPE)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(
        TOKENIZER_NAME, trust_remote_code=True, local_files_only=True)

    # ── load v15 exactly like exp_b ──
    cfg = V15Config()
    if Path(args.extracted_model_path).exists():
        cfg.extracted_model_path = args.extracted_model_path
    log(f"building v15 operator (n_outer={args.n_outer}) ...")
    model, _converted = create_model_with_deltas(cfg, convert_ffn=True)
    loaded_ckpt = ""
    if args.checkpoint and Path(args.checkpoint).exists():
        log(f"  loading TRAINED checkpoint: {args.checkpoint}")
        model.load_weights(args.checkpoint, strict=False)
        mx.eval(model.parameters())
        n_reduced = reduce_all_deltas(model)
        log(f"  folded {n_reduced} trained delta plates into base")
        mx.eval(model.parameters())
        loaded_ckpt = args.checkpoint
    else:
        log("  no checkpoint — using frozen extracted base only")
    model._n_outer_passes = args.n_outer
    model._fixed_point_lambda = 0.0

    # ── wrap the LIVE gate plate (NOT model.ffn_gate_plate_c — orphan, s218) ──
    stack = model.stack_c if args.stack == "c" else model.stack_a
    cap = GateCapture(stack.ffn_gate_plate)
    stack.ffn_gate_plate = cap
    d_ff = int(cfg.d_ff)
    log(f"  capturing stack_{args.stack}.ffn_gate_plate pre-activation (d_ff={d_ff})")

    # ── forward each probe, capture last-token gate pre-activation ──
    gate = np.empty((len(prompts), d_ff), np.float32)
    plen = np.empty(len(prompts), np.int32)
    for i, text in enumerate(prompts):
        ids = tok.encode(text, add_special_tokens=False)[: args.max_length]
        if not ids:
            ids = [0]
        ids = [min(t, cfg.vocab_size - 1) for t in ids]
        tokens = mx.array(np.asarray(ids, np.int64)[None, :])
        model._prev_alg_c = None
        cap.last = None
        _ = model(tokens)
        mx.eval(cap.last)
        g = np.asarray(cap.last[0, -1], np.float32)  # (d_ff,)
        gate[i] = g
        plen[i] = len(ids)
        if (i + 1) % 50 == 0:
            log(f"    {i + 1}/{len(prompts)}")

    # ── routing register: sign(gate), raw + CMR ──
    sign = np.sign(gate)
    sign_cmr = cmr(sign)
    sil_full = silhouette_null(sign, labels, args.n_perm, args.seed)
    sil_cmr = silhouette_null(sign_cmr, labels, args.n_perm, args.seed)
    Cb = centroids(sign_cmr, labels)          # (9, d_ff) — the harvest material
    G = gram(Cb)
    log(f"  route_cmr silhouette={sil_cmr['silhouette']:+.4f} "
        f"z={sil_cmr['z']:+.2f} p={sil_cmr['p_value']:.4f}  "
        f"(control route_full z={sil_full['z']:+.2f})")

    D = 1.0 - G
    np.fill_diagonal(D, 0.0)
    mds = classical_mds(D, k=2)
    nn_map = {}
    for i, c in enumerate(CRYSTAL):
        row = [(CRYSTAL[j], float(G[i, j])) for j in range(len(CRYSTAL)) if j != i]
        row.sort(key=lambda x: -x[1])
        nn_map[c] = row[:3]

    log("\n  Gram (cosine) — the v15 MAP:")
    head = "       " + "".join(f"{c:>7}" for c in CRYSTAL)
    log(head)
    for i, c in enumerate(CRYSTAL):
        log(f"  {c:>5}" + "".join(f"{G[i, j]:+7.2f}" for j in range(len(CRYSTAL))))

    out = {
        "model": "v15", "register": "topological/routing",
        "checkpoint": loaded_ckpt, "n_outer": args.n_outer,
        "stack": args.stack, "d_ff": d_ff, "n_probes": len(prompts),
        "counts": counts, "crystal_order": CRYSTAL, "n_perm": args.n_perm,
        "git_sha": git_sha(),
        "route_cmr_silhouette": sil_cmr, "route_full_silhouette": sil_full,
        "map": {
            "gram": {CRYSTAL[i]: {CRYSTAL[j]: round(float(G[i, j]), 4)
                                  for j in range(len(CRYSTAL))}
                     for i in range(len(CRYSTAL))},
            "mds_coords": {CRYSTAL[i]: [round(float(mds[i, 0]), 4),
                                        round(float(mds[i, 1]), 4)]
                           for i in range(len(CRYSTAL))},
            "nearest": nn_map,
        },
        "elapsed_s": round(time.time() - t0, 1),
    }
    tag = args.tag or (Path(loaded_ckpt).parent.name if loaded_ckpt else "base")
    safe = f"v15_{tag}"
    np.savez_compressed(
        RESULTS_DIR / f"{safe}.npz",
        prompt_len=plen, labels=labels,
        gram_route_cmr_best=G.astype(np.float32),
        centroids_cmr_best=Cb.astype(np.float32),
    )
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))
    log(f"\n  wrote {RESULTS_DIR / safe}.{{json,npz}}  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
