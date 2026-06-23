#!/usr/bin/env python3
# register: causal (distributed concept subspace; INLP nullspace projection)
"""Program C-field SUBSPACE ablation — is the C-field load-bearing DISTRIBUTED? (s250).

THE s250 OPEN DOOR. The single-direction C-field ablation (program_cfield_ablation.py)
found the applicative-C routing field READABLE/INJECTABLE but NOT load-bearing: ablating
one diff-of-means direction d_C perturbed output >> random and drove z(C) when injected,
but the c=2-vs-c=0 differential REVERSED and ablating d_C *raised* downstream z(C) (the
gate reconstructs C holographically). The honest caveat: one rank-1 direction is the
wrong probe if the C-computation is DISTRIBUTED. This script closes that caveat.

THE METHOD - INLP (Iterative Nullspace Projection, Ravfogel et al. 2020, "Null It Out").
A diff-of-means is rank-1: once removed the class means coincide and no second direction
appears. A linear CLASSIFIER finds separating directions even when means coincide (via
covariance structure). INLP iterates: fit a linear C-probe -> project its direction OUT
-> refit on the nullspace -> repeat k times. The k orthonormal directions span the
subspace carrying ALL linearly-decodable C information; ablating span(W) ERASES linear
C-decodability (verified). We then re-run the s250 causal arms on this k-dim subspace.

DESIGN (reuses the s250 spine - program_cfield_ablation):
  - Build the C subspace W (d-by-k) by INLP on L30 content-mean residuals, label =
    C-present (c_count>0) vs C-absent (c_count==0), scalar-conditioned (dirs preserved).
  - ERASURE CHECK: linear C-decodability (cross-val logistic acc) BEFORE vs AFTER
    projecting out span(W) - INLP guarantees AFTER ~ majority baseline.
  - ABLATE: project span(W) OUT of the residual at L30 AND L31 across CONTENT positions.
  - CONTROL: a RANDOM k-dim orthonormal subspace (same dim), averaged over n_rand.
  - READOUT: downstream gate z(C) + next-token KL (identical to s250).

ARMS:
  1. NECESSITY (c=2 ditrans): ablate span(W). If the DISTRIBUTED C-field is
     load-bearing, output is perturbed (KL) AND downstream z(C) now DROPS (we removed
     the whole decodable subspace) - both MORE than a random k-dim subspace.
  2. DIFFERENTIAL (c=0 intrans, same ablation): the load-bearing signature is net-KL
     (subspace minus random) SCALING with C-load: c=2 >> c=0.

VERDICT (lambda measure, two-sided - the decisive fork):
  load_bearing_distributed = erasure_ok AND necessity_ok AND differential_ok.
  - erasure_ok AND not differential_ok => even after removing ALL linearly-decodable C,
    the object-application output is not selectively hurt => the C-field is DECISIVELY a
    readout register, not the computation (strong s250 conclusion, distributed-robust).
  - differential_ok => the mechanism IS distributed; single-direction (s250) was the
    wrong probe.

Usage:
    uv run python scripts/experiments/program_cfield_subspace_ablation.py --smoke
    uv run python scripts/experiments/program_cfield_subspace_ablation.py \
        --model Qwen/Qwen3-14B --patch-layers 30 31 --k 16

License: MIT. AGENTS.md S5 λ provenance.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from opcode_monitor_v2 import (  # noqa: E402
    COMPILE_GATE,
    _git_sha,
    _json_safe,
    _transformers_version,
    calibrate_v2,
    gate_prefix_len,
    load_model_and_tokenizer,
)
from program_cfield_ablation import (  # noqa: E402
    forward_capture,
    kl_div,
    load_ladder,
    log_softmax,
    paired,
    two_sample_t,
    zC_downstream,
)

RESULTS_DIR = _ROOT / "results" / "program-cfield-ablation"
READING_PROBES = _ROOT / "data" / "reading-probes.jsonl"


# ═══════════════════════════════════════════════════════════════════════════════
# INLP — iterative nullspace projection → k-dim C-discriminative subspace
# ═══════════════════════════════════════════════════════════════════════════════
def inlp_subspace(x: np.ndarray, y: np.ndarray, k: int, seed: int,
                  cv: int = 5) -> tuple[np.ndarray, list[float]]:
    """Return (Q [d,k] orthonormal, decodability_curve). x is scalar-conditioned so the
    directions live in the residual space. Each iteration fits a logistic C-probe on the
    current (projected) residuals, records its cross-val accuracy, then projects the
    probe direction OUT. QR-orthonormalises the accumulated directions."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score

    xp = x.copy()
    dirs: list[np.ndarray] = []
    curve: list[float] = []
    for _i in range(k):
        clf = LogisticRegression(max_iter=4000, C=1.0)
        acc = float(np.mean(cross_val_score(clf, xp, y, cv=cv)))
        curve.append(round(acc, 4))
        clf.fit(xp, y)
        w = clf.coef_[0].astype(np.float64)
        nrm = np.linalg.norm(w)
        if nrm < 1e-9:
            break
        w = w / nrm
        dirs.append(w)
        xp = xp - (xp @ w)[:, None] * w  # project rows onto nullspace of w
    w_mat = np.asarray(dirs).T  # [d, m]
    q, _r = np.linalg.qr(w_mat)  # orthonormal basis of span(dirs)
    return q[:, : len(dirs)], curve


def decodability(x: np.ndarray, y: np.ndarray, cv: int = 5) -> float:
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score

    return float(np.mean(cross_val_score(
        LogisticRegression(max_iter=4000, C=1.0), x, y, cv=cv)))


# ═══════════════════════════════════════════════════════════════════════════════
# Subspace ablation hook — project span(Q) OUT of content positions
# ═══════════════════════════════════════════════════════════════════════════════
def make_subspace_patch_hook(q_mat: np.ndarray, torch_mod, pos_start: int,
                             pos_end: int):
    """Forward hook: remove the projection onto span(Q) at every content position."""
    def hook(_module, _inp, out):
        h = out[0] if isinstance(out, tuple) else out
        q = torch_mod.as_tensor(q_mat, dtype=h.dtype, device=h.device)  # [d, k]
        end = min(pos_end, h.shape[1])
        if pos_start >= end:
            return out
        v = h[0, pos_start:end, :]           # [P, d]
        proj = (v @ q) @ q.T                 # [P, d] projection onto span(Q)
        h[0, pos_start:end, :] = v - proj
        return out
    return hook


def random_subspace(d: int, k: int, rng) -> np.ndarray:
    g = rng.standard_normal((d, k))
    q, _ = np.linalg.qr(g)
    return q[:, :k]


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    ap = argparse.ArgumentParser(description="Distributed C-subspace ablation (INLP)")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--patch-layers", type=int, nargs="+", default=[30, 31])
    ap.add_argument("--k", type=int, default=16, help="INLP subspace dimension")
    ap.add_argument("--n-rand", type=int, default=3)
    ap.add_argument("--max-per-group", type=int, default=None)
    ap.add_argument("--null-mode", default="gateneutral",
                    choices=["gateneutral", "crosstask"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model_name = args.model
    patch_layers = sorted(args.patch_layers)
    k = args.k
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap = 80, 3, 200
        max_per_group = args.max_per_group or 12
        k = min(k, 6)
        print("[subspace] SMOKE MODE")
    else:
        n_perm, ppc, null_cap = 300, None, None
        max_per_group = args.max_per_group

    ladder = load_ladder(READING_PROBES)
    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    if max(patch_layers) >= n_layers:
        denom = max(n_layers - 1, 1)
        patch_layers = sorted({min(n_layers - 2, round(f * denom))
                               for f in (0.75, 0.775)})
        print(f"[subspace] patch layers rescaled for {n_layers}L -> {patch_layers}")
    resid_layer = patch_layers[0]
    max_patch = max(patch_layers)
    print(f"[subspace] model={model_name} layers={n_layers} patch={patch_layers} k={k}")

    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                            null_mode=args.null_mode, hook="gate")
    crystal_layers = rcc.crystal_layers
    print(f"[subspace] crystal {len(crystal_layers)}/{n_layers}; ds > L{max_patch}")

    gate_n = gate_prefix_len(tok)

    def grp(cc):
        g = [r for r in ladder if r["c_count"] == cc]
        return g[:max_per_group] if max_per_group else g
    c0, c1, c2 = grp(0), grp(1), grp(2)
    print(f"[subspace] c0={len(c0)} c1={len(c1)} c2={len(c2)}")

    # ── Pass A: baseline (residual @ L30 content-mean + labels + baseline logits) ─
    baseline: dict[str, dict] = {}
    resid_rows: list[np.ndarray] = []
    labels: list[int] = []

    def base_pass(items):
        for i, r in enumerate(items):
            store, resid, logits = forward_capture(
                COMPILE_GATE + r["input"], model, tok, torch_mod, layers,
                patch_layers, resid_layer)
            n_tok = store[layers[0]].shape[0]
            start = min(gate_n, n_tok - 1)
            baseline[r["input"]] = {
                "c_count": r["c_count"], "category": r["category"],
                "logp0": log_softmax(logits), "start": start, "n_tok": n_tok,
                "zC_ds0": zC_downstream(rcc, store, layers, crystal_layers, max_patch),
            }
            resid_rows.append(resid[start:n_tok].mean(axis=0))
            labels.append(1 if r["c_count"] > 0 else 0)
            if (i + 1) % 20 == 0:
                print(f"[subspace]   baseline {i + 1}/{len(items)}")

    print("[subspace] Pass A: baseline ...")
    base_pass(c0)
    base_pass(c1)
    base_pass(c2)

    x_raw = np.asarray(resid_rows)            # [n, d]
    y = np.asarray(labels)
    scale = float(np.mean(np.linalg.norm(x_raw, axis=1))) or 1.0
    x_s = x_raw / scale                       # scalar conditioning (dirs preserved)

    # ── INLP subspace + erasure check ────────────────────────────────────────────
    print(f"[subspace] INLP building k={k}-dim C-subspace ...")
    q_C, decode_curve = inlp_subspace(x_s, y, k, args.seed)
    k_eff = q_C.shape[1]
    acc_before = decodability(x_s, y)
    x_ab = x_s - (x_s @ q_C) @ q_C.T
    acc_after = decodability(x_ab, y)
    majority = float(max(np.mean(y), 1 - np.mean(y)))
    print(f"[subspace] decodability before={acc_before:.3f} after={acc_after:.3f} "
          f"majority={majority:.3f} (k_eff={k_eff})")

    rng = np.random.default_rng(args.seed)
    d = x_raw.shape[1]
    rand_subspaces = [random_subspace(d, k_eff, rng) for _ in range(args.n_rand)]

    # ── arm runner ────────────────────────────────────────────────────────────────
    def run_arm(items, q_mat):
        kls, zds = [], []
        for r in items:
            b = baseline[r["input"]]
            hooks = {li: make_subspace_patch_hook(
                q_mat, torch_mod, b["start"], b["n_tok"]) for li in patch_layers}
            store, _resid, logits = forward_capture(
                COMPILE_GATE + r["input"], model, tok, torch_mod, layers,
                patch_layers, resid_layer, patch_hooks=hooks)
            kls.append(kl_div(log_softmax(logits), b["logp0"]))
            zds.append(zC_downstream(rcc, store, layers, crystal_layers, max_patch))
        return kls, zds

    def avg_rand(items):
        kl_stack, z_stack = [], []
        for qr in rand_subspaces:
            kk, zz = run_arm(items, qr)
            kl_stack.append(kk)
            z_stack.append(zz)
        return (list(np.mean(np.asarray(kl_stack), axis=0)),
                list(np.mean(np.asarray(z_stack), axis=0)))

    arms: dict[str, dict] = {}

    print("[subspace] arm 1: NECESSITY (ablate span(W) on c=2) ...")
    kl_c2, z_c2 = run_arm(c2, q_C)
    klr_c2, zr_c2 = avg_rand(c2)
    zbase_c2 = [baseline[r["input"]]["zC_ds0"] for r in c2]
    arms["necessity_c2"] = {
        "n": len(c2),
        "kl_out": paired(kl_c2, klr_c2),
        "zC_ds_delta_sub": round(float(np.nanmean(np.asarray(z_c2) - zbase_c2)), 5),
        "zC_ds_delta_rand": round(float(np.nanmean(np.asarray(zr_c2) - zbase_c2)), 5),
        "zC_ds_after": paired(z_c2, zr_c2),
    }

    print("[subspace] arm 2: SPECIFICITY (ablate span(W) on c=0) ...")
    kl_c0, z_c0 = run_arm(c0, q_C)
    klr_c0, zr_c0 = avg_rand(c0)
    zbase_c0 = [baseline[r["input"]]["zC_ds0"] for r in c0]
    arms["specificity_c0"] = {
        "n": len(c0),
        "kl_out": paired(kl_c0, klr_c0),
        "zC_ds_delta_sub": round(float(np.nanmean(np.asarray(z_c0) - zbase_c0)), 5),
        "zC_ds_delta_rand": round(float(np.nanmean(np.asarray(zr_c0) - zbase_c0)), 5),
        "zC_ds_after": paired(z_c0, zr_c0),
    }

    net_kl_c2 = list(np.asarray(kl_c2) - np.asarray(klr_c2))
    net_kl_c0 = list(np.asarray(kl_c0) - np.asarray(klr_c0))
    differential = two_sample_t(net_kl_c2, net_kl_c0)

    # ── verdict ────────────────────────────────────────────────────────────────────
    nec = arms["necessity_c2"]
    erasure_ok = bool(acc_after <= majority + 0.02)
    necessity_ok = bool(
        (nec["kl_out"]["delta"] or 0) > 0 and (nec["kl_out"]["t"] or 0) > 2.0
        and nec["zC_ds_delta_sub"] < nec["zC_ds_delta_rand"])
    differential_ok = bool(
        (differential["diff"] or 0) > 0 and (differential["t"] or 0) > 2.0)
    load_bearing_distributed = erasure_ok and necessity_ok and differential_ok

    if not erasure_ok:
        interpretation = ("INLP did NOT erase linear C-decodability — k too small or C "
                          "not linearly separable; result inconclusive.")
    elif differential_ok:
        interpretation = ("C-field is load-bearing and DISTRIBUTED — single-direction "
                          "(s250) was the wrong probe; the differential scales with "
                          "C-load under subspace ablation.")
    else:
        interpretation = ("C-field is DECISIVELY a readout register, not the "
                          "computation - even after erasing ALL linearly-decodable C, "
                          "the object-application output is not selectively hurt (c2 "
                          "net-KL not > c0). Distributed-robust confirmation of s250.")

    verdict = {
        "model": model_name, "n_layers": n_layers, "patch_layers": patch_layers,
        "crystal_layers": crystal_layers, "null_mode": args.null_mode, "k": k,
        "k_eff": k_eff, "n_c0": len(c0), "n_c1": len(c1), "n_c2": len(c2),
        "n_rand": args.n_rand, "seed": args.seed, "scale": round(scale, 4),
        "decodability_before": round(acc_before, 4),
        "decodability_after": round(acc_after, 4),
        "majority_baseline": round(majority, 4),
        "decodability_curve": decode_curve,
        "arms": arms, "differential_net_kl_c2_vs_c0": differential,
        "erasure_ok": erasure_ok, "necessity_ok": necessity_ok,
        "differential_ok": differential_ok,
        "load_bearing_distributed": load_bearing_distributed,
        "interpretation": interpretation,
    }

    # ── report ───────────────────────────────────────────────────────────────────
    print("\n" + "═" * 82)
    print(f"PROGRAM C-FIELD SUBSPACE ABLATION (INLP k={k_eff}) — {model_name}  "
          f"L{patch_layers}")
    print("═" * 82)
    print(f"  decodability before={acc_before:.3f} after={acc_after:.3f} "
          f"majority={majority:.3f}  erasure_ok={erasure_ok}")
    print(f"  curve={decode_curve}")
    print("\n  -- NECESSITY (ablate span(W) on c=2) --")
    print(f"     KL_out  sub={nec['kl_out']['k_mean']} "
          f"rand={nec['kl_out']['rand_mean']}"
          f"  d={nec['kl_out']['delta']} t={nec['kl_out']['t']}")
    print(f"     zCds Δ  sub={nec['zC_ds_delta_sub']} rand={nec['zC_ds_delta_rand']}")
    print(f"     => necessity_ok = {necessity_ok}")
    print("\n  -- DIFFERENTIAL (net KL = sub-rand; expect c2 > c0) --")
    print(f"     net_KL c2={differential['mean_a']} c0={differential['mean_b']}  "
          f"diff={differential['diff']} t={differential['t']}")
    print(f"     => differential_ok = {differential_ok}")
    print(f"\n  * LOAD-BEARING (DISTRIBUTED) = {load_bearing_distributed}")
    print(f"  >> {interpretation}")
    print("═" * 82 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    (RESULTS_DIR / f"subspace_verdict_{slug}.json").write_text(
        json.dumps(_json_safe({"verdict": verdict, "calibration_summary": cal}),
                   indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "patch_layers": patch_layers, "k": k, "n_perm": n_perm,
        "n_rand": args.n_rand, "seed": args.seed, "null_mode": args.null_mode,
        "probe_set": str(READING_PROBES.relative_to(_ROOT)),
        "method": "INLP (Ravfogel 2020) builds a k-dim C-discriminative subspace on "
                  "L30 content-mean residuals (C-present vs C-absent); erasure check = "
                  "cross-val logistic decodability before/after; ablate span(W) over "
                  "content positions at L30/L31; readout downstream gate z(C) + "
                  "next-token KL vs random k-dim subspace; load-bearing = erasure AND "
                  "necessity AND c2>c0 differential.",
        "scope": "Closes the s250 single-direction caveat - tests whether the C-field "
                 "is load-bearing as a DISTRIBUTED subspace.",
    }
    (RESULTS_DIR / f"subspace_meta_{slug}.json").write_text(
        json.dumps(_json_safe(meta), indent=2), encoding="utf-8")
    print(f"[subspace] wrote {RESULTS_DIR}/subspace_verdict_{slug}.json (+ meta)")


if __name__ == "__main__":
    main()
