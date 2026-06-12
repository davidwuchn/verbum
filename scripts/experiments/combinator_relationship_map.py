#!/usr/bin/env python3
# register: topological/routing
"""Combinator relationship map — what is the SHAPE of the function space?

THE QUESTION (session 217, Michael):
  We have found "function-like things" = the combinator basis
  (K I B C S D W Y WHNF). What are their SEMANTIC RELATIONSHIPS? Is there a
  map/fold? What do the functions look like — what is their shape?

THE INSTRUMENT (this script):
  Measure each combinator's CENTROID in the ROUTING register and build the
  pairwise relationship (Gram) matrix = the literal "map of the functions".

    routing(x) = sign( FFN gate pre-activation )        (s203: gate_proj sign
                                                          carries routing topology)
    centroid_k = mean over probes labelled k of routing(x), AFTER common-mode
                 removal (subtract the per-feature mean across all probes — kills
                 the universal structured-language crystal so the DIFFERENCES
                 between combinators show, not their shared backbone).
    Gram[j,k]  = cosine(centroid_j, centroid_k)          <- THE MAP

  Why this register: in RAW cosine the crystal is a rank-~1 common mode
  (5d-crystal-lattice REFUTED, s211); the combinator structure lives in the
  sign/routing register after CMR (separation p=5e-4, ~65% topological). So the
  shape of the function space is only visible here.

  Controls:
    - hidden_full / hidden_cmr : raw residual register (expect the common-mode mush)
    - route_full               : routing without CMR (common mode still present)
    - route_cmr                : routing with CMR        <-- KEY (the real map)
    - shuffled-label null       : permute combinator labels, recompute silhouette
                                  -> is the clustering real?

  Outputs per layer-fraction + a best layer chosen by silhouette z. Classical
  MDS + centroid-PCA give the 2D embedding (the picture). Cross combinator
  Gram, silhouette, null, and embedding all saved.

Usage:
  uv run python scripts/experiments/combinator_relationship_map.py \
      --model Qwen/Qwen3-0.6B --device mps --dtype bfloat16

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from verbum.probes.library import crystal_probes

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"

# the 9 crystal combinators, in a fixed canonical order
CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]

# depth-normalized layer fractions (align models of different depth)
LAYER_FRACS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# ---- probes -----------------------------------------------------------------
def load_probes(limit_per: int = 0, seed: int = 0):
    """All crystal probes (K I B C S D W Y WHNF), grouped order preserved.
    limit_per: optionally cap probes per combinator (for smoke tests)."""
    probes = crystal_probes()
    by = {c: [] for c in CRYSTAL}
    for p in probes:
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


# ---- model introspection ----------------------------------------------------
def find_gate_modules(model):
    hits = []
    pat = re.compile(r"\.(\d+)\.mlp\.(gate_proj|dense_h_to_4h)$")
    for name, mod in model.named_modules():
        m = pat.search(name)
        if m:
            hits.append((int(m.group(1)), name, mod, m.group(2)))
    hits.sort(key=lambda x: x[0])
    return [(li, name, mod) for (li, name, mod, k) in hits]


def pick_layers(n_layers: int):
    return sorted({min(n_layers - 1, max(0, round(f * (n_layers - 1))))
                   for f in LAYER_FRACS})


# ---- capture ----------------------------------------------------------------
@torch.no_grad()
def collect(model, tokenizer, device, prompts, max_length, want_layers):
    gate_mods = find_gate_modules(model)
    n_layers = len(gate_mods)
    want = set(want_layers)
    buf = {}

    def mk_hook(li):
        def hook(_m, _inp, out):
            buf[li] = out[0, -1].detach().float().cpu().numpy().astype(np.float32)
        return hook

    handles = [mod.register_forward_hook(mk_hook(li))
               for (li, _nm, mod) in gate_mods if li in want]

    n = len(prompts)
    hidden = None
    gate = {li: None for li in want}
    plen = np.empty(n, np.int32)
    try:
        for i, text in enumerate(prompts):
            buf.clear()
            enc = tokenizer(text, return_tensors="pt", truncation=True,
                            max_length=max_length)
            enc = {k: v.to(device) for k, v in enc.items()}
            out = model(**enc, output_hidden_states=True)
            h = out.hidden_states[-1][0, -1].float().cpu().numpy().astype(np.float32)
            if hidden is None:
                hidden = np.empty((n, h.shape[0]), np.float32)
            hidden[i] = h
            plen[i] = int(enc["input_ids"].shape[1])
            for li in want:
                g = buf[li]
                if gate[li] is None:
                    gate[li] = np.empty((n, g.shape[0]), np.float32)
                gate[li][i] = g
            del out
            if (i + 1) % 50 == 0:
                log(f"    {i + 1}/{n}")
    finally:
        for hd in handles:
            hd.remove()
    return hidden, gate, plen, n_layers


# ---- centroid / Gram / silhouette -------------------------------------------
def cmr(X):
    """Common-mode removal: subtract per-feature mean across probes."""
    return X - X.mean(axis=0, keepdims=True)


def unit(v):
    return v / (np.linalg.norm(v) + 1e-30)


def centroids(X, labels):
    """Per-combinator mean vector. Returns [K x d] in CRYSTAL order."""
    C = np.zeros((len(CRYSTAL), X.shape[1]), np.float64)
    for j, c in enumerate(CRYSTAL):
        m = labels == c
        C[j] = X[m].mean(axis=0)
    return C


def gram(C):
    """Cosine Gram matrix between centroids."""
    U = np.array([unit(c) for c in C])
    return np.clip(U @ U.T, -1, 1)


def silhouette(X, labels):
    """Mean over probes of [cos(x, own centroid) - max_other cos(x, centroid)].
    Centroids computed leave-one-combinator-balanced (all probes; bias small at
    n>=50). High -> combinators are real clusters in this register."""
    C = centroids(X, labels)
    U = np.array([unit(c) for c in C])
    Xu = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)
    sims = Xu @ U.T                       # [N x K]
    lab_idx = np.array([CRYSTAL.index(c) for c in labels])
    own = sims[np.arange(len(labels)), lab_idx]
    other = sims.copy()
    other[np.arange(len(labels)), lab_idx] = -np.inf
    best_other = other.max(axis=1)
    return float(np.mean(own - best_other))


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
    """Classical (Torgerson) MDS from a distance matrix -> [n x k] coords."""
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    w, V = np.linalg.eigh(B)
    order = np.argsort(w)[::-1]
    w, V = w[order][:k], V[:, order][:, :k]
    w = np.clip(w, 0, None)
    return V * np.sqrt(w + 1e-30)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--max-length", type=int, default=256)
    ap.add_argument("--limit-per", type=int, default=0,
                    help="cap probes per combinator (smoke test)")
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()

    prompts, labels = load_probes(args.limit_per, args.seed)
    counts = {c: int(np.sum(labels == c)) for c in CRYSTAL}
    log(f"[{args.model}] {len(prompts)} crystal probes  {counts}")

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()

    gate_mods = find_gate_modules(model)
    n_layers = len(gate_mods)
    want_layers = pick_layers(n_layers)
    log(f"  arch: {n_layers} layers; capturing layers {want_layers}")

    log("  forward passes ...")
    hidden, gate, plen, n_layers = collect(
        model, tok, args.device, prompts, args.max_length, want_layers)
    width = int(hidden.shape[1])
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    out = {"model": args.model, "dtype": args.dtype, "register": "topological/routing",
           "n_probes": len(prompts), "counts": counts, "hidden_width": width,
           "n_layers": n_layers, "want_layers": want_layers, "crystal_order": CRYSTAL,
           "n_perm": args.n_perm, "git_sha": git_sha(), "per_layer": {}}

    store = {"labels": labels}

    # control register: final residual (expect common-mode mush)
    out["hidden_full_silhouette"] = silhouette_null(
        hidden, labels, args.n_perm, args.seed)
    out["hidden_cmr_silhouette"] = silhouette_null(
        cmr(hidden), labels, args.n_perm, args.seed)
    store["gram_hidden_cmr"] = gram(centroids(cmr(hidden), labels)).astype(np.float32)

    log("  routing register per layer (sign(gate), raw + CMR) ...")
    for li in want_layers:
        sign = np.sign(gate[li])
        sign_cmr = cmr(sign)
        sil_full = silhouette_null(sign, labels, args.n_perm, args.seed)
        sil_cmr = silhouette_null(sign_cmr, labels, args.n_perm, args.seed)
        G_cmr = gram(centroids(sign_cmr, labels))
        store[f"gram_route_cmr_L{li:02d}"] = G_cmr.astype(np.float32)
        out["per_layer"][str(li)] = {
            "frac": round(li / max(n_layers - 1, 1), 3),
            "d_ff": int(gate[li].shape[1]),
            "route_full_silhouette": sil_full,
            "route_cmr_silhouette": sil_cmr,
        }
        log(f"    L{li:02d} (f={li/max(n_layers-1,1):.2f}) "
            f"route_cmr silhouette={sil_cmr['silhouette']:+.4f} "
            f"z={sil_cmr['z']:+.2f} p={sil_cmr['p_value']:.4f}")

    # best routing layer by CMR silhouette z
    best_li = max(want_layers,
                  key=lambda li: out["per_layer"][str(li)]["route_cmr_silhouette"]["z"])
    out["best_routing_layer"] = int(best_li)
    best_frac = round(best_li / max(n_layers - 1, 1), 3)
    out["best_routing_frac"] = best_frac

    # the MAP at the best layer: Gram, MDS, centroid-PCA
    G = store[f"gram_route_cmr_L{best_li:02d}"].astype(np.float64)
    D = 1.0 - G
    np.fill_diagonal(D, 0.0)
    mds = classical_mds(D, k=2)
    Cb = centroids(cmr(np.sign(gate[best_li])), labels)
    # Persist the full-dimensional best-layer combinator centroids (9 x d_ff).
    # These are the raw material for cross-model alignment / harvest-fold
    # (combinator_harvest_fold.py); prior runs computed them but discarded them,
    # leaving only the relational Gram. Frame-LOCAL (this model's gate space),
    # so only usable after align-before-fold (Procrustes) into a target frame.
    store["centroids_cmr_best"] = Cb.astype(np.float32)
    store["centroids_best_layer"] = np.asarray([best_li], dtype=np.int32)
    Uc = np.array([unit(c) for c in Cb])
    # centroid PCA (2D)
    Ucc = Uc - Uc.mean(axis=0, keepdims=True)
    _, _, Vt = np.linalg.svd(Ucc, full_matrices=False)
    pca = Ucc @ Vt[:2].T

    out["map"] = {
        "layer": int(best_li), "frac": best_frac,
        "gram": {CRYSTAL[i]: {CRYSTAL[j]: round(float(G[i, j]), 4)
                              for j in range(len(CRYSTAL))}
                 for i in range(len(CRYSTAL))},
        "mds_coords": {CRYSTAL[i]: [round(float(mds[i, 0]), 4),
                                    round(float(mds[i, 1]), 4)]
                       for i in range(len(CRYSTAL))},
        "pca_coords": {CRYSTAL[i]: [round(float(pca[i, 0]), 4),
                                    round(float(pca[i, 1]), 4)]
                       for i in range(len(CRYSTAL))},
    }
    # nearest neighbour per combinator (off-diagonal max cosine)
    nn = {}
    for i, c in enumerate(CRYSTAL):
        row = [(CRYSTAL[j], float(G[i, j])) for j in range(len(CRYSTAL)) if j != i]
        row.sort(key=lambda x: -x[1])
        nn[c] = row[:3]
    out["map"]["nearest"] = nn
    out["elapsed_s"] = round(time.time() - t0, 1)

    np.savez_compressed(RESULTS_DIR / f"{safe}.npz", prompt_len=plen, **store)
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))

    # ---- readable summary ----
    log("")
    log(f"  === {args.model} combinator relationship map ===")
    log(f"  register: routing (sign gate) + CMR; best layer L{best_li} (f={best_frac})")
    hf = out["hidden_full_silhouette"]
    rc = out["per_layer"][str(best_li)]["route_cmr_silhouette"]
    log(f"  hidden_full silhouette {hf['silhouette']:+.4f} z={hf['z']:+.2f} "
        f"(control: the common-mode register)")
    log(f"  route_cmr   silhouette {rc['silhouette']:+.4f} z={rc['z']:+.2f} "
        f"p={rc['p_value']:.4f}   <-- combinators as clusters")
    log("")
    log("  Gram (cosine) matrix — the MAP:")
    header = "        " + " ".join(f"{c:>6}" for c in CRYSTAL)
    log(header)
    for i, c in enumerate(CRYSTAL):
        row = " ".join(f"{G[i, j]:+.2f}".rjust(6) for j in range(len(CRYSTAL)))
        log(f"  {c:>5} {row}")
    log("")
    log("  nearest neighbours (top routing-cosine):")
    for c in CRYSTAL:
        ns = ", ".join(f"{n}({s:+.2f})" for n, s in nn[c])
        log(f"    {c:>5} -> {ns}")
    log("")
    log(f"  wrote {safe}.json + .npz  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
