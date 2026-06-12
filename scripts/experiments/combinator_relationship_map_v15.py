#!/usr/bin/env python3
# register: topological/routing
"""Combinator relationship map — the v15 (MLX/ternary) edition.

WHY a separate script (s220):
  combinator_relationship_map.py is HF-only (`AutoModelForCausalLM`, hooks
  `gate_proj`). v15 is an MLX ternary model with a shared-stride VSM stack and an
  outer recurrence — a different forward path. To HARVEST ecosystem-consensus
  combinator structure into the v15 base plate (consensus-delta-folding.md §s220,
  harvest fold Phase 1) we first need v15's OWN combinator Gram + centroids in a
  routing register. This produces the target frame for align-before-fold.

TWO REGISTERS (--target):
  ffn_gate : sign(stack_c.ffn_gate_plate pre-activation), d_ff=5120. The direct
             analog of the HF gate_proj register. CAVEAT: v15's FFN is
             FROZEN-EXTRACTED (only attention is TD-trained), so this measures the
             untrained base. (s220 result: z=+0.52, p=0.29 — NO combinator shape.)
  attn_q   : sign(shared_stride_stack.layers[li].q_proj output), d_model=1280, the
  attn_out : sign(...out_proj output). The TD-TRAINED attention routing (the query
             = which combinator to apply / the integrated attention write). Swept
             over depth-fraction layers; best by silhouette z. (s220 follow-up:
             does the LEARNED routing carry the shape the frozen FFN does not?)

CAPTURE MECHANISM (the s218 orphan lesson):
  We wrap the LIVE module object that the forward actually calls (the reference
  INSIDE stack_c / inside each stride layer), NOT a top-level model attribute —
  convert_ffn rebinds the model attribute but the stacks keep their original
  references (the bug that VOIDed s217 phase-2). The wrapper passes through and
  stashes the last pre-activation it produced (last band of last outer pass).

LOAD (mirrors exp_b_self_verifying_acceptance.py): cfg=V15Config();
  create_model_with_deltas(cfg, convert_ffn=True); load_weights(ckpt, strict=False);
  reduce_all_deltas(model) -> trained operator; n_outer from CLI; fp_lambda=0.
  Checkpoint is READ-ONLY (the running main:1 training writes step_NNNN/).

Usage (GPU/MLX — run alongside main:1, per Michael s220):
  uv run python scripts/experiments/combinator_relationship_map_v15.py \
      --checkpoint checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz \
      --target attn_q --n-outer 2
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
LAYER_FRACS = [0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0]


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


# ---- per-FAMILY binding (the crystallization measurement; s219 method) -------
# WHY (s221): each combinator's β-reduction = a substitution (move/copy/delete of
# args across positions), and attention is the ONLY cross-position op → the
# substructural class of a combinator predicts its attention cost:
#   selection  {K,I,C}  = affine/linear (0 copies)  → single attention pass
#   composition{B,D,S}  = B,D linear; S duplicates  → single pass (+1 fan-out)
#   recursion  {Y,W,WHNF}= W dup, Y unbounded        → NEEDS the OUTER RECURRENCE
# Prediction: selection/composition bind EARLY (low contractivity); recursion
# strengthens ONLY as the operator becomes contractive (Δx→0 ≡ β-reduction to
# WHNF). This helper measures each family's internal binding vs a random-triple
# null on ONE checkpoint's Gram so combinator_crystallization.py can trace it.
FAMILIES = {
    "selection_KIC": ["K", "I", "C"],
    "composition_BDS": ["B", "D", "S"],
    "recursion_YWWHNF": ["Y", "W", "WHNF"],
}


def _internal_edges(node_idx):
    return [(node_idx[a], node_idx[b])
            for a in range(len(node_idx)) for b in range(a + 1, len(node_idx))]


def family_binding(G, n_perm=1000, seed=0):
    """Per-family internal binding vs a random-node-triple null (s219 method).

    G = 9x9 cosine Gram over CRYSTAL. z_bind>0 means the family's mean internal
    cosine exceeds a random triple drawn from the 9 combinators (the relabelling
    symmetry the function shape must break).
    """
    idx = {c: n for n, c in enumerate(CRYSTAL)}
    rng = np.random.default_rng(seed + 7)

    def mean_internal(edges):
        return float(np.mean([G[a, b] for a, b in edges]))

    def triple_null(size):
        out = np.empty(n_perm)
        for t in range(n_perm):
            sub = rng.choice(len(CRYSTAL), size=size, replace=False)
            out[t] = mean_internal(_internal_edges(list(sub)))
        return out

    report = {}
    for fam, nodes in FAMILIES.items():
        ie = _internal_edges([idx[c] for c in nodes])
        cons = mean_internal(ie)
        nb = triple_null(len(nodes))
        z = (cons - nb.mean()) / (nb.std() + 1e-12)
        p = (np.sum(nb >= cons) + 1) / (len(nb) + 1)
        report[fam] = {
            "internal_cos": round(cons, 4),
            "z_bind": round(float(z), 2),
            "p_bind": round(float(p), 4),
            "edges": {f"{CRYSTAL[a]}-{CRYSTAL[b]}": round(float(G[a, b]), 4)
                      for a, b in ie},
        }
    skel = float(np.mean([report["composition_BDS"]["z_bind"],
                          report["selection_KIC"]["z_bind"]]))
    rec = report["recursion_YWWHNF"]["z_bind"]
    report["_summary"] = {
        "skeleton_z_bind": round(skel, 2),
        "recursion_z_bind": round(rec, 2),
        "skeleton_gt_recursion": bool(skel > rec),
    }
    return report


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


# ---- live-module capture (wrap the reference the forward actually calls) -----
class Capture(nn.Module):
    """Pass-through wrapper that stashes the last pre-activation it produced."""

    def __init__(self, inner):
        super().__init__()
        self.inner = inner
        self.last = None

    def __call__(self, x):
        out = self.inner(x)
        self.last = mx.stop_gradient(out)
        return out


def pick_layers(n_layers: int):
    return sorted({min(n_layers - 1, max(0, round(f * (n_layers - 1))))
                   for f in LAYER_FRACS})


def install_captures(model, target: str, cfg):
    """Wrap the target module(s); return ({key: Capture}, width, label_fn)."""
    caps = {}
    if target == "ffn_gate":
        stack = model.stack_c
        cap = Capture(stack.ffn_gate_plate)
        stack.ffn_gate_plate = cap
        caps["ffn_gate_c"] = cap
        return caps, int(cfg.d_ff)
    # attention registers: sweep depth-fraction layers of the shared stride stack
    layers = model.shared_stride_stack.layers
    want = pick_layers(len(layers))
    for li in want:
        layer = layers[li]
        if target == "attn_q":
            cap = Capture(layer.q_proj)
            layer.q_proj = cap
        elif target == "attn_out":
            cap = Capture(layer.out_proj)
            layer.out_proj = cap
        else:
            raise SystemExit(f"unknown --target {target!r}")
        caps[f"L{li:02d}"] = cap
    return caps, int(cfg.d_model)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--checkpoint", type=str,
                    default="checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz",
                    help="TRAINED v15 model.npz (READ-ONLY); '' = frozen base only")
    ap.add_argument("--extracted-model-path", type=str,
                    default="checkpoints/v15-extracted/model.npz/model.npz")
    ap.add_argument("--target", choices=["ffn_gate", "attn_q", "attn_out"],
                    default="attn_q",
                    help="routing register to read (attn_* = TD-trained)")
    ap.add_argument("--n-outer", type=int, default=2,
                    help="outer recurrence passes (match training K=2)")
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

    caps, width = install_captures(model, args.target, cfg)
    log(f"  target={args.target}  capturing {len(caps)} module(s)  width={width}")

    # ── forward each probe, capture last-token pre-activations ──
    reg = {k: np.empty((len(prompts), width), np.float32) for k in caps}
    plen = np.empty(len(prompts), np.int32)
    for i, text in enumerate(prompts):
        ids = tok.encode(text, add_special_tokens=False)[: args.max_length]
        if not ids:
            ids = [0]
        ids = [min(t, cfg.vocab_size - 1) for t in ids]
        tokens = mx.array(np.asarray(ids, np.int64)[None, :])
        model._prev_alg_c = None
        for c in caps.values():
            c.last = None
        _ = model(tokens)
        for k, c in caps.items():
            mx.eval(c.last)
            reg[k][i] = np.asarray(c.last[0, -1], np.float32)
        plen[i] = len(ids)
        if (i + 1) % 50 == 0:
            log(f"    {i + 1}/{len(prompts)}")

    # ── per-capture routing register: sign, CMR, silhouette, Gram ──
    per_key = {}
    best_key, best_z = None, -1e9
    for k in caps:
        sign_cmr = cmr(np.sign(reg[k]))
        sil = silhouette_null(sign_cmr, labels, args.n_perm, args.seed)
        per_key[k] = sil
        log(f"    {k}: route_cmr silhouette={sil['silhouette']:+.4f} "
            f"z={sil['z']:+.2f} p={sil['p_value']:.4f}")
        if sil["z"] > best_z:
            best_z, best_key = sil["z"], k

    # control: raw (no CMR) silhouette on the best key
    best_sign = np.sign(reg[best_key])
    sil_full = silhouette_null(best_sign, labels, args.n_perm, args.seed)
    Cb = centroids(cmr(best_sign), labels)     # (9, width) — harvest material
    G = gram(Cb)
    log(f"\n  BEST register: {best_key}  route_cmr z={best_z:+.2f} "
        f"(control route_full z={sil_full['z']:+.2f})")

    # ── per-layer Gram + per-FAMILY binding (the crystallization measurement) ──
    per_key_gram = {}
    per_key_family = {}
    for k in caps:
        Gk = G if k == best_key else gram(centroids(cmr(np.sign(reg[k])), labels))
        per_key_gram[k] = Gk
        per_key_family[k] = family_binding(Gk, args.n_perm, args.seed)
    fb_best = per_key_family[best_key]
    log(f"  family binding @ {best_key}: "
        f"selection z={fb_best['selection_KIC']['z_bind']:+.2f}  "
        f"composition z={fb_best['composition_BDS']['z_bind']:+.2f}  "
        f"recursion z={fb_best['recursion_YWWHNF']['z_bind']:+.2f}  "
        f"(skeleton {fb_best['_summary']['skeleton_z_bind']:+.2f} "
        f"vs recursion {fb_best['_summary']['recursion_z_bind']:+.2f})")

    D = 1.0 - G
    np.fill_diagonal(D, 0.0)
    mds = classical_mds(D, k=2)
    nn_map = {}
    for i, c in enumerate(CRYSTAL):
        row = [(CRYSTAL[j], float(G[i, j])) for j in range(len(CRYSTAL)) if j != i]
        row.sort(key=lambda x: -x[1])
        nn_map[c] = row[:3]

    log("\n  Gram (cosine) — the v15 MAP (best register):")
    log("       " + "".join(f"{c:>7}" for c in CRYSTAL))
    for i, c in enumerate(CRYSTAL):
        log(f"  {c:>5}" + "".join(f"{G[i, j]:+7.2f}" for j in range(len(CRYSTAL))))

    out = {
        "model": "v15", "register": "topological/routing", "target": args.target,
        "checkpoint": loaded_ckpt, "n_outer": args.n_outer, "width": width,
        "n_probes": len(prompts), "counts": counts, "crystal_order": CRYSTAL,
        "n_perm": args.n_perm, "git_sha": git_sha(),
        "best_key": best_key,
        "per_key_silhouette": per_key,
        "route_cmr_silhouette": per_key[best_key],
        "route_full_silhouette": sil_full,
        "family_binding_best": fb_best,
        "family_binding_per_layer": per_key_family,
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
    ckpt_tag = Path(loaded_ckpt).parent.name if loaded_ckpt else "base"
    tag = args.tag or f"{args.target}_{ckpt_tag}"
    safe = f"v15_{tag}"
    layer_keys = list(caps.keys())
    grams_all = np.stack([per_key_gram[k] for k in layer_keys]).astype(np.float32)
    np.savez_compressed(
        RESULTS_DIR / f"{safe}.npz",
        prompt_len=plen, labels=labels,
        gram_route_cmr_best=G.astype(np.float32),
        centroids_cmr_best=Cb.astype(np.float32),
        layer_keys=np.array(layer_keys),
        grams_all=grams_all,
    )
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))
    log(f"\n  wrote {RESULTS_DIR / safe}.{{json,npz}}  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
