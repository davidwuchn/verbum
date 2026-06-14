#!/usr/bin/env python3
# register: topological/routing
"""Function-topology consensus — do models agree on the topology of HOFs?

THE QUESTION (session 225, Michael):
  s219 showed the combinator PRIMITIVES {K I B C S D W Y WHNF} have a universal
  relational geometry across the open-weight ecosystem. But `map` is HIGHER
  ORDER (map = B(CB)(CB), s219 REPL). Do multiple models route higher-order
  functions the SAME way, or differently?

  Michael's hypothesis: higher-order functions exist as routing NORMAL FORMS in
  the topology → a normal form is unique → topology should be universal across
  teachers (the same uniqueness that makes the β-output canonical by
  Church-Rosser). If so, the whole extract→fold→compiler pipeline is
  teacher-agnostic: any sufficiently large model emits the same canonical
  reduction traces (capability) AND the consensus topology is teacher-free
  (inventory). "Which teacher" only matters for any IDIOSYNCRATIC HOF (rare).

THE INSTRUMENT (this script): two modes.
  --mode model      run ONE model. Capture routing register (sign(gate)+CMR),
                    pick best layer by COMBINATOR silhouette z (the basis must
                    crystallize), then compute each HOF's FINGERPRINT =
                    cosine(centroid_HOF, centroid_combinator_j) for the 9
                    combinators. The fingerprint is RELATIONAL (all cosines) ⇒
                    frame-invariant ⇒ comparable across models (raw centroids
                    are not; sign-corr 0.000 across frames, s219). Writes
                    <model>.json + .npz.
  --mode consensus  aggregate >=2 model jsons. Per HOF: cross-model agreement of
                    the 9-vector fingerprint (mean pairwise Pearson) vs a
                    combinator-label-permutation null → z, p. CLASSIFY each HOF
                    universal (clears null) vs idiosyncratic. Theory check:
                    controls compose→B, flip→C, const→K, apply→I (argmax must
                    hit); map should load B,C and NOT Y.

  THE VERDICT = a per-HOF SORT (universal vs idiosyncratic) = the direct test of
  Michael's hypothesis.

Usage:
  uv run python scripts/experiments/function_topology_consensus.py \
      --mode model --model Qwen/Qwen3-4B --device mps --dtype bfloat16
  uv run python scripts/experiments/function_topology_consensus.py \
      --mode consensus --n-perm 5000

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
from verbum.probes.higher_order import (
    by_function,
    expected_combinator,
    function_names,
)
from verbum.probes.library import crystal_probes

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "function-topology-consensus"

# universal coordinate frame (s219): the 9 combinators, fixed canonical order
CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
LAYER_FRACS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# ---- probes ------------------------------------------------------------------
def load_probes(limit_per: int = 0, seed: int = 0):
    """Combinator basis (9) + higher-order functions. Labels are disjoint so a
    single label array distinguishes them."""
    rng = np.random.default_rng(seed)
    prompts: list[str] = []
    labels: list[str] = []

    by_comb: dict[str, list[str]] = {c: [] for c in CRYSTAL}
    for p in crystal_probes():
        if p.combinator in by_comb:
            by_comb[p.combinator].append(p.prompt)
    for c in CRYSTAL:
        ps = by_comb[c]
        if limit_per and limit_per < len(ps):
            idx = sorted(rng.permutation(len(ps))[:limit_per])
            ps = [ps[i] for i in idx]
        prompts.extend(ps)
        labels.extend([c] * len(ps))

    for fn in function_names():
        ps = [p.prompt for p in by_function(fn)]
        if limit_per and limit_per < len(ps):
            idx = sorted(rng.permutation(len(ps))[:limit_per])
            ps = [ps[i] for i in idx]
        prompts.extend(ps)
        labels.extend([fn] * len(ps))

    return prompts, np.array(labels)


# ---- model introspection -----------------------------------------------------
# which module's output is the "routing register" — FFN gate (s203) or an
# attention projection (s221: attention-over-positions IS the fold; map's home).
TARGET_PATTERNS = {
    "ffn_gate": r"\.(\d+)\.mlp\.(gate_proj|dense_h_to_4h)$",
    "attn_q": r"\.(\d+)\.self_attn\.(q_proj)$",
    "attn_out": r"\.(\d+)\.self_attn\.(o_proj)$",
}


def find_modules(model, target):
    pat = re.compile(TARGET_PATTERNS[target])
    hits = []
    for name, mod in model.named_modules():
        m = pat.search(name)
        if m:
            hits.append((int(m.group(1)), name, mod))
    hits.sort(key=lambda x: x[0])
    return hits


def pick_layers(n_layers: int):
    return sorted({min(n_layers - 1, max(0, round(f * (n_layers - 1))))
                   for f in LAYER_FRACS})


# ---- capture -----------------------------------------------------------------
@torch.no_grad()
def collect(model, tokenizer, device, prompts, max_length, want_layers, target):
    gate_mods = find_modules(model, target)
    want = set(want_layers)
    buf = {}

    def mk_hook(li):
        def hook(_m, _inp, out):
            buf[li] = out[0, -1].detach().float().cpu().numpy().astype(np.float32)
        return hook

    handles = [mod.register_forward_hook(mk_hook(li))
               for (li, _nm, mod) in gate_mods if li in want]

    n = len(prompts)
    gate = {li: None for li in want}
    try:
        for i, text in enumerate(prompts):
            buf.clear()
            enc = tokenizer(text, return_tensors="pt", truncation=True,
                            max_length=max_length)
            enc = {k: v.to(device) for k, v in enc.items()}
            model(**enc)
            for li in want:
                g = buf[li]
                if gate[li] is None:
                    gate[li] = np.empty((n, g.shape[0]), np.float32)
                gate[li][i] = g
            if (i + 1) % 100 == 0:
                log(f"    {i + 1}/{n}")
    finally:
        for hd in handles:
            hd.remove()
    return gate, len(gate_mods)


# ---- centroid / cosine / silhouette ------------------------------------------
def cmr(X):
    """Common-mode removal: subtract per-feature mean across probes."""
    return X - X.mean(axis=0, keepdims=True)


def unit(v):
    return v / (np.linalg.norm(v) + 1e-30)


def centroid(X, labels, name):
    return X[labels == name].mean(axis=0)


def comb_centroids(X, labels):
    """9 combinator centroids in CRYSTAL order."""
    return np.array([centroid(X, labels, c) for c in CRYSTAL])


def silhouette(X, labels, names):
    """Mean over probes of cos(x, own centroid) - max_other. High -> real
    clusters. Restricted to the given label set (the combinator basis)."""
    mask = np.isin(labels, names)
    Xs, ls = X[mask], labels[mask]
    C = np.array([centroid(Xs, ls, c) for c in names])
    U = np.array([unit(c) for c in C])
    Xu = Xs / (np.linalg.norm(Xs, axis=1, keepdims=True) + 1e-30)
    sims = Xu @ U.T
    idx = {c: j for j, c in enumerate(names)}
    lab_idx = np.array([idx[c] for c in ls])
    own = sims[np.arange(len(ls)), lab_idx]
    other = sims.copy()
    other[np.arange(len(ls)), lab_idx] = -np.inf
    return float(np.mean(own - other.max(axis=1)))


def silhouette_null(X, labels, names, n_perm=1000, seed=0):
    obs = silhouette(X, labels, names)
    mask = np.isin(labels, names)
    ls = labels[mask].copy()
    Xs = X[mask]
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        perm = rng.permutation(ls)
        # rebuild silhouette on permuted labels (inline for speed)
        C = np.array([Xs[perm == c].mean(axis=0) for c in names])
        U = np.array([unit(c) for c in C])
        Xu = Xs / (np.linalg.norm(Xs, axis=1, keepdims=True) + 1e-30)
        sims = Xu @ U.T
        idx = {c: j for j, c in enumerate(names)}
        lab_idx = np.array([idx[c] for c in perm])
        own = sims[np.arange(len(perm)), lab_idx]
        sims[np.arange(len(perm)), lab_idx] = -np.inf
        null[i] = float(np.mean(own - sims.max(axis=1)))
    sd = null.std() + 1e-30
    return {"silhouette": obs, "null_mean": float(null.mean()),
            "null_std": float(null.std()), "z": float((obs - null.mean()) / sd),
            "p_value": float((np.sum(null >= obs) + 1) / (n_perm + 1))}


def fingerprint(fn_centroid, comb_C):
    """9-dim cosine of a function centroid to each combinator centroid."""
    fu = unit(fn_centroid)
    return np.array([float(np.dot(fu, unit(c))) for c in comb_C])


# ---- mode: model -------------------------------------------------------------
def run_model(args):
    out_dir = RESULTS_DIR / args.target
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()

    prompts, labels = load_probes(args.limit_per, args.seed)
    counts = {n: int(np.sum(labels == n)) for n in CRYSTAL + function_names()}
    log(f"[{args.model}] {len(prompts)} probes  {counts}")

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()

    n_layers = len(find_modules(model, args.target))
    want_layers = pick_layers(n_layers)
    log(f"  arch: {n_layers} layers; target={args.target}; capturing {want_layers}")
    gate, n_layers = collect(model, tok, args.device, prompts,
                             args.max_length, want_layers, args.target)
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    # best layer by COMBINATOR silhouette z (basis must crystallize)
    per_layer = {}
    for li in want_layers:
        sign_cmr = cmr(np.sign(gate[li]))
        sil = silhouette_null(sign_cmr, labels, CRYSTAL, args.n_perm, args.seed)
        per_layer[str(li)] = {"frac": round(li / max(n_layers - 1, 1), 3),
                              "d_ff": int(gate[li].shape[1]),
                              "comb_silhouette": sil}
        log(f"    L{li:02d} comb silhouette={sil['silhouette']:+.4f} "
            f"z={sil['z']:+.2f} p={sil['p_value']:.4f}")
    best_li = max(want_layers,
                  key=lambda li: per_layer[str(li)]["comb_silhouette"]["z"])
    best_frac = round(best_li / max(n_layers - 1, 1), 3)
    log(f"  best layer L{best_li} (f={best_frac})")

    # centroids + fingerprints at best layer
    sign_cmr = cmr(np.sign(gate[best_li]))
    comb_C = comb_centroids(sign_cmr, labels)
    fns = function_names()
    fps = {}
    nearest = {}
    fn_C = np.zeros((len(fns), sign_cmr.shape[1]), np.float32)
    for k, fn in enumerate(fns):
        c = centroid(sign_cmr, labels, fn)
        fn_C[k] = c
        fp = fingerprint(c, comb_C)
        fps[fn] = {CRYSTAL[j]: round(float(fp[j]), 4) for j in range(len(CRYSTAL))}
        order = sorted(range(len(CRYSTAL)), key=lambda j: -fp[j])
        nearest[fn] = [(CRYSTAL[j], round(float(fp[j]), 4)) for j in order[:3]]

    out = {
        "model": args.model, "dtype": args.dtype, "register": "topological/routing",
        "target": args.target,
        "n_probes": len(prompts), "counts": counts, "n_layers": n_layers,
        "best_layer": int(best_li), "best_frac": best_frac,
        "crystal_order": CRYSTAL, "functions": fns,
        "fingerprints": fps, "nearest_combinator": nearest,
        "per_layer": per_layer, "n_perm": args.n_perm, "git_sha": git_sha(),
        "elapsed_s": round(time.time() - t0, 1),
    }
    np.savez_compressed(out_dir / f"{safe}.npz",
                        comb_centroids=comb_C.astype(np.float32),
                        fn_centroids=fn_C, best_layer=np.array([best_li]))
    (out_dir / f"{safe}.json").write_text(json.dumps(out, indent=2))

    # readable
    log("")
    log(f"  === {args.model} HOF fingerprints (best L{best_li}) ===")
    for fn in fns:
        exp = expected_combinator(fn)
        tag = f"  [control→{exp}]" if exp else "  [HOF test]"
        ns = ", ".join(f"{n}({s:+.2f})" for n, s in nearest[fn])
        hit = ""
        if exp:
            hit = " ✓" if nearest[fn][0][0] == exp else f" ✗(got {nearest[fn][0][0]})"
        log(f"    {fn:>8} -> {ns}{tag}{hit}")
    log(f"  wrote {safe}.json + .npz  ({out['elapsed_s']}s)")


# ---- mode: consensus ---------------------------------------------------------
def _pairwise_mean_corr(M):
    """Mean pairwise Pearson over rows (models) of M [n_models x 9]."""
    n = M.shape[0]
    if n < 2:
        return float("nan")
    cs = []
    for i in range(n):
        for j in range(i + 1, n):
            a, b = M[i], M[j]
            if a.std() < 1e-12 or b.std() < 1e-12:
                continue
            cs.append(float(np.corrcoef(a, b)[0, 1]))
    return float(np.mean(cs)) if cs else float("nan")


def run_consensus(args):
    out_dir = RESULTS_DIR / args.target
    files = sorted(f for f in out_dir.glob("*.json") if f.stem != "consensus")
    if args.models:
        want = {m.replace("/", "_") for m in args.models}
        files = [f for f in files if f.stem in want]
    if len(files) < 2:
        log(f"need >=2 model jsons in {out_dir} (found {len(files)})")
        sys.exit(1)
    models = [json.loads(f.read_text()) for f in files]
    names = [m["model"] for m in models]
    log(f"consensus over {len(models)} models: {names}")

    fns = function_names()
    rng = np.random.default_rng(args.seed)
    verdict = {}
    for fn in fns:
        M = np.array([[mo["fingerprints"][fn][c] for c in CRYSTAL] for mo in models])
        obs = _pairwise_mean_corr(M)
        # null: independently permute the 9 combinator entries within each model
        null = np.empty(args.n_perm)
        for t in range(args.n_perm):
            Mp = np.array([row[rng.permutation(len(CRYSTAL))] for row in M])
            null[t] = _pairwise_mean_corr(Mp)
        sd = np.nanstd(null) + 1e-30
        z = float((obs - np.nanmean(null)) / sd)
        p = float((np.sum(null >= obs) + 1) / (args.n_perm + 1))
        # consensus fingerprint = mean across models
        mean_fp = M.mean(axis=0)
        order = sorted(range(len(CRYSTAL)), key=lambda j: -mean_fp[j])
        top = [(CRYSTAL[j], round(float(mean_fp[j]), 4)) for j in order[:3]]
        exp = expected_combinator(fn)
        universal = bool(z >= args.z_gate and p < 0.05 and obs >= args.corr_gate)
        verdict[fn] = {
            "kind": "control" if exp else "test", "expected": exp,
            "mean_pairwise_corr": round(obs, 4), "z": round(z, 3),
            "p_value": round(p, 5), "consensus_top": top,
            "control_hit": (top[0][0] == exp) if exp else None,
            "classification": "universal" if universal else "idiosyncratic",
        }

    # map theory check: loads B,C; NOT Y
    map_fp = {c: float(np.mean([mo["fingerprints"]["map"][c] for mo in models]))
              for c in CRYSTAL}
    map_check = {
        "loads_B": round(map_fp["B"], 4), "loads_C": round(map_fp["C"], 4),
        "loads_Y": round(map_fp["Y"], 4),
        "B_and_C_gt_Y": bool(min(map_fp["B"], map_fp["C"]) > map_fp["Y"]),
    }

    out = {
        "models": names, "n_models": len(models), "target": args.target,
        "n_perm": args.n_perm,
        "z_gate": args.z_gate, "corr_gate": args.corr_gate,
        "crystal_order": CRYSTAL, "per_function": verdict,
        "map_theory_check": map_check, "git_sha": git_sha(),
        "n_universal": sum(v["classification"] == "universal"
                           for v in verdict.values()),
        "n_idiosyncratic": sum(v["classification"] == "idiosyncratic"
                               for v in verdict.values()),
        "controls_all_hit": all(verdict[fn]["control_hit"]
                                for fn in fns if verdict[fn]["expected"]),
    }
    (out_dir / "consensus.json").write_text(json.dumps(out, indent=2))

    log("")
    log("  === FUNCTION-TOPOLOGY CONSENSUS ===")
    log(f"  {len(models)} models | n_perm={args.n_perm} | "
        f"gates: z>={args.z_gate} p<.05 corr>={args.corr_gate}")
    log("")
    log(f"  {'function':>8} {'kind':>8} {'corr':>7} {'z':>7} {'p':>7}  "
        f"{'class':>13}  top / check")
    for fn in fns:
        v = verdict[fn]
        top = ", ".join(f"{n}({s:+.2f})" for n, s in v["consensus_top"])
        chk = ""
        if v["expected"]:
            chk = " ✓" if v["control_hit"] else f" ✗(exp {v['expected']})"
        log(f"  {fn:>8} {v['kind']:>8} {v['mean_pairwise_corr']:>+7.3f} "
            f"{v['z']:>+7.2f} {v['p_value']:>7.4f}  {v['classification']:>13}  "
            f"{top}{chk}")
    log("")
    log(f"  map theory: B={map_check['loads_B']:+.2f} C={map_check['loads_C']:+.2f} "
        f"Y={map_check['loads_Y']:+.2f}  (B,C > Y: {map_check['B_and_C_gt_Y']})")
    log(f"  controls all hit: {out['controls_all_hit']}")
    log(f"  UNIVERSAL: {out['n_universal']}/{len(fns)}  "
        f"IDIOSYNCRATIC: {out['n_idiosyncratic']}/{len(fns)}")
    log("  wrote consensus.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["model", "consensus"], required=True)
    ap.add_argument("--target", default="ffn_gate",
                    choices=["ffn_gate", "attn_q", "attn_out"],
                    help="routing register: FFN gate (s203) or attention projection")
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--models", nargs="*", default=None,
                    help="consensus: restrict to these model names")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--max-length", type=int, default=64)
    ap.add_argument("--limit-per", type=int, default=0,
                    help="cap probes per label (smoke test)")
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--z-gate", type=float, default=2.0)
    ap.add_argument("--corr-gate", type=float, default=0.3)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if args.mode == "model":
        run_model(args)
    else:
        run_consensus(args)


if __name__ == "__main__":
    main()
