#!/usr/bin/env python3
# register: functional + topological/routing
"""Gradient-shadow tomography (gd-trajectory v3) — does the routing topology cast a
SHADOW in the gradients, and does the shadow LEAD the activation-inventory? (s230).

THE QUESTION (Michael, s230): "If GD is creating soft topology in the gradients, do
the gradients show shadows of that? Height-from-shadow with known illumination."

THE MECHANISM (gradient-trajectory-tomography.md §s230 v3). The gate activation
g = W_gate·h; the routing topology lives in g-space. The upstream gradient ∂L/∂g is a
vector IN THE SAME g-space ⇒ the gradient-SHADOW and the activation-OBJECT are directly
commensurable. We read the shadow in the routing register (relational Gram, gauge-
invariant), with the per-combinator probe labels as the known illumination.

THE EXPERIMENT. CE-only TinyLM on the s229 β-reduction curriculum. At each checkpoint,
in ADDITION to the activation geometry (gc_route, s230 v1), measure the GRADIENT-shadow:
for each crystal probe, backprop the probe's LM loss to g at the capture layer, mean-
pool the gradient over supervised positions, build the per-combinator gradient-Gram →
gc_grad, correlate to the CONSENSUS CRYSTAL. Raw-residual grad = reference beam.
(NB the last token feeds only the unsupervised next-token => zero grad there; we pool
over the supervised predictor positions, which is nonzero and denoises √N.)

FALSIFIABLE PREDICTION (the shadow LEADS): ∂L/∂g points toward where GD is moving the
activations ⇒ gc_grad(t) ≈ gc_route(t+Δ) ⇒ gc_grad crosses its baseline→final midpoint
EARLIER than gc_route. ⇒ a THREE-STAGE cascade: gradient-shadow (intent) → activation-
inventory (geometry) → capability (usage). If gc_grad does NOT lead, the gradient is a
trailing echo not a leading shadow.

Catches (λ measure): SNR (minibatch grad noisier — √N over probes); reference beam
(raw-grad-Gram common mode vs routing-grad-Gram); frame residue (Jacobian gauge).

Usage:
  uv run python scripts/experiments/gd_gradient_shadow.py --smoke
  uv run python scripts/experiments/gd_gradient_shadow.py --seeds 0,1,2

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))
sys.path.insert(0, str(_SCRIPT_DIR))

from exposure_format_sweep import (  # noqa: E402
    SKELETONS,
    TRAIN_ATOMS,
    build_corpus,
    build_eval_items,
    eval_acc,
    make_fillings,
    to_byte_ids,
    validate_skeletons,
)

# reuse the consensus loader + activation-geometry instrument + readout helpers
from gd_trajectory_tomography import (  # noqa: E402
    _final,
    _first_step,
    load_consensus,
    measure_geometry,
)
from relational_loss_distillation import (  # noqa: E402
    VOCAB,
    TinyLM,
    load_crystal_probe_batch,
    np_centroids,
    np_cmr,
    np_gram,
    np_silhouette_null,
    offdiag_corr,
)

RESULTS_DIR = _PROJECT_ROOT / "results" / "gd-gradient-shadow"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------- #
# The gradient-shadow: ∂(probe LM loss)/∂g, read in the routing register        #
# --------------------------------------------------------------------------- #
def measure_shadow(model: TinyLM, p_ids: torch.Tensor, p_len: torch.Tensor,
                   labels: np.ndarray, cap: int, consensus_gram: np.ndarray,
                   n_perm: int, probe_batch: int, seed: int, device: str) -> dict:
    """For each probe, backprop its LM loss to the gate (routing) + residual (raw)
    activations; MEAN-POOL the gradient over supervised positions; build the per-
    combinator Gram and correlate to the consensus crystal. NOT under no_grad."""
    model.eval()
    grad_gate_feats, grad_hid_feats = [], []
    for s in range(0, p_ids.shape[0], probe_batch):
        pb = p_ids[s:s + probe_batch]
        pl = p_len[s:s + probe_batch]
        logits, hid, gate = model(pb, capture_layer=cap)
        B, T, V = logits.shape
        # masked LM CE on the probe's own tokens (predict t+1 from t, valid only)
        shift_logits = logits[:, :-1, :].reshape(-1, V)
        shift_tgt = pb[:, 1:].reshape(-1)
        ce_tok = F.cross_entropy(shift_logits, shift_tgt, reduction="none").reshape(
            B, T - 1)
        posn = torch.arange(T - 1, device=device)[None, :]
        mask = (posn < (pl[:, None] - 1)).float()
        loss = (ce_tok * mask).sum() / mask.sum().clamp_min(1.0)
        g_gate, g_hid = torch.autograd.grad(loss, [gate, hid])
        # mean-pool the gradient over SUPERVISED predictor positions [0, len-2].
        # (the last token len-1 feeds only the unsupervised next-token => grad 0
        #  there; pooling over supervised positions is nonzero AND denoises, √N.)
        pmask = (torch.arange(T, device=device)[None, :] < (pl[:, None] - 1)).float()
        denom = pmask.sum(1, keepdim=True).clamp_min(1.0)
        pooled_gate = (g_gate * pmask[..., None]).sum(1) / denom
        pooled_hid = (g_hid * pmask[..., None]).sum(1) / denom
        grad_gate_feats.append(pooled_gate.detach().cpu().numpy())
        grad_hid_feats.append(pooled_hid.detach().cpu().numpy())
    grad_gate_np = np.concatenate(grad_gate_feats, axis=0).astype(np.float64)
    grad_hid_np = np.concatenate(grad_hid_feats, axis=0).astype(np.float64)

    # routing-register shadow = sign(∂L/∂gate)-CMR (commensurate w/ consensus build)
    sign_cmr = np_cmr(np.sign(grad_gate_np))
    grad_sil = np_silhouette_null(sign_cmr, labels, n_perm, seed)
    grad_gram = np_gram(np_centroids(sign_cmr, labels))
    gc_grad = offdiag_corr(grad_gram, consensus_gram)

    # raw-residual gradient = the reference-beam control
    hid_cmr = np_cmr(grad_hid_np)
    grad_gram_raw = np_gram(np_centroids(hid_cmr, labels))
    gc_grad_raw = offdiag_corr(grad_gram_raw, consensus_gram)

    return {
        "grad_z": round(float(grad_sil["z"]), 4),
        "gc_grad": round(float(gc_grad), 4),
        "gc_grad_raw": round(float(gc_grad_raw), 4),
        "grad_norm": round(float(np.linalg.norm(grad_gate_np, axis=1).mean()), 6),
    }


# --------------------------------------------------------------------------- #
# Readout — does the SHADOW lead the OBJECT (and capability)?                    #
# --------------------------------------------------------------------------- #
def _order(a: int | None, b: int | None) -> str:
    if a is None or b is None:
        return "n/a"
    return "before" if a < b else ("after" if a > b else "same")


def readout(curve: list[dict], init: dict, gc_frac: float, acc_frac: float) -> dict:
    fin_grad = _final(curve, "gc_grad")
    fin_route = _final(curve, "gc_route")
    fin_acc = _final(curve, "heldout_acc")
    g0, r0, a0 = (float(init["gc_grad"]), float(init["gc_route"]),
                  float(init["heldout_acc"]))
    s_grad = (_first_step(curve, "gc_grad", g0 + gc_frac * (fin_grad - g0))
              if fin_grad > g0 else None)
    s_route = (_first_step(curve, "gc_route", r0 + gc_frac * (fin_route - r0))
               if fin_route > r0 else None)
    s_acc = (_first_step(curve, "heldout_acc", a0 + acc_frac * (fin_acc - a0))
             if fin_acc > a0 else None)
    return {
        "final": {"gc_grad": round(fin_grad, 4), "gc_route": round(fin_route, 4),
                  "gc_grad_raw": _final(curve, "gc_grad_raw"),
                  "heldout_acc": round(fin_acc, 4), "grad_z": _final(curve, "grad_z")},
        "init_baseline": {"gc_grad": init["gc_grad"], "gc_route": init["gc_route"],
                          "gc_grad_raw": init["gc_grad_raw"]},
        "step_gc_grad_cross": s_grad,
        "step_gc_route_cross": s_route,
        "step_heldout_acc_cross": s_acc,
        "shadow_before_inventory": _order(s_grad, s_route),
        "inventory_before_capability": _order(s_route, s_acc),
        "shadow_before_capability": _order(s_grad, s_acc),
        "shadow_gap": round(fin_grad - _final(curve, "gc_grad_raw"), 4),
    }


# --------------------------------------------------------------------------- #
def train_seed(args, device: str, consensus_gram: np.ndarray, seed: int,
               p_ids: torch.Tensor, p_len: torch.Tensor,
               probe_labels: np.ndarray) -> dict:
    torch.manual_seed(seed)
    np.random.seed(seed)
    rules = validate_skeletons(SKELETONS)
    if args.smoke:
        rules = rules[:4]
    fill_rng = np.random.default_rng(seed)
    train_fillings = {tmpl: make_fillings(fill_rng, h, TRAIN_ATOMS, args.k)
                      for tmpl, h in rules}
    corpus = build_corpus(rules, train_fillings, "redex_nf", "k_varied", args.k,
                          np.random.default_rng(seed + 13))
    eval_rng = np.random.default_rng(seed + 777)
    eval_items = build_eval_items(rules, args.m_eval, eval_rng, TRAIN_ATOMS,
                                  train_fillings)
    log(f"  [seed {seed}] rules={len(rules)} corpus={len(corpus.encode())} B "
        f"heldout_eval={len(eval_items)}")

    ids = to_byte_ids(corpus)
    T, bs = args.block_size, args.batch_size
    while ids.shape[0] <= 4 * (T + 1):
        ids = np.concatenate([ids, ids])
    n = ids.shape[0]
    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff, T).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    cap = args.capture_layer if args.capture_layer >= 0 else args.n_layer // 2

    curve: list[dict] = []
    t0 = time.time()

    def snapshot(step: int, ce_val: float) -> None:
        acc = eval_acc(model, eval_items, T, device)
        act = measure_geometry(model, p_ids, p_len, probe_labels, cap,
                               consensus_gram, args.n_perm, args.probe_batch, seed)
        shadow = measure_shadow(model, p_ids, p_len, probe_labels, cap,
                                consensus_gram, args.n_perm, args.probe_batch, seed,
                                device)
        row = {"step": step, "ce": round(ce_val, 4), "heldout_acc": round(acc, 4),
               "gc_route": act["gc_route"], "route_z": act["route_z"],
               "eff_dim_route": act["eff_dim_route"], **shadow}
        curve.append(row)
        log(f"  [s{seed}] step {step:5d} | CE {ce_val:.3f} | acc {acc:.3f} "
            f"| gc_grad {shadow['gc_grad']:+.3f} (raw {shadow['gc_grad_raw']:+.3f}) "
            f"| gc_route {act['gc_route']:+.3f} | grad_z {shadow['grad_z']:+.2f} "
            f"| {time.time()-t0:.0f}s")

    snapshot(0, float("nan"))
    for step in range(1, args.steps + 1):
        model.train()
        ix = torch.randint(0, n - T - 1, (bs,))
        xb = torch.stack([torch.from_numpy(ids[i:i + T]) for i in ix]).to(device)
        yb = torch.stack(
            [torch.from_numpy(ids[i + 1:i + 1 + T]) for i in ix]).to(device)
        logits, _, _ = model(xb)
        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))
        opt.zero_grad()
        ce.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % args.ckpt_every == 0 or step == args.steps:
            snapshot(step, float(ce.item()))

    init_frame = curve[0]
    rd = readout([r for r in curve if not (isinstance(r["ce"], float)
                                           and np.isnan(r["ce"]))],
                 init_frame, args.gc_frac, args.acc_frac)
    return {"seed": seed, "capture_layer": cap, "curve": curve, "readout": rd}


def _ms(vals: list) -> list:
    a = np.array([v for v in vals if v is not None], dtype=float)
    if a.size == 0:
        return [None, None]
    return [round(float(a.mean()), 2), round(float(a.std()), 2)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps")
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--ckpt-every", type=int, default=200)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--block-size", type=int, default=128)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--d-ff", type=int, default=256)
    ap.add_argument("--capture-layer", type=int, default=-1)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--m-eval", type=int, default=6)
    ap.add_argument("--probe-batch", type=int, default=64)
    ap.add_argument("--probe-max-len", type=int, default=96)
    ap.add_argument("--n-perm", type=int, default=300)
    ap.add_argument("--gc-frac", type=float, default=0.5)
    ap.add_argument("--acc-frac", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", default="")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.steps, args.ckpt_every = 120, 40
        args.k, args.m_eval, args.n_perm = 4, 3, 100
        args.d_model, args.d_ff, args.n_layer = 64, 128, 3

    device = args.device
    if device == "mps" and not torch.backends.mps.is_available():
        device = "cpu"
        log("  mps unavailable -> cpu")
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    consensus_gram, cmeta = load_consensus()
    log(f"  consensus crystal: {cmeta['n_models']} models, sha="
        f"{cmeta['consensus_git_sha']}")
    probe_ids, probe_len, probe_labels = load_crystal_probe_batch(args.probe_max_len)
    p_ids = torch.tensor(probe_ids, device=device)
    p_len = torch.tensor(probe_len, device=device)
    log(f"  crystal probes={probe_ids.shape[0]}")

    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or [args.seed]
    log(f"  seeds={seeds} steps={args.steps} ckpt_every={args.ckpt_every}")
    runs = [train_seed(args, device, consensus_gram, sd, p_ids, p_len, probe_labels)
            for sd in seeds]

    meta = {
        "experiment": "gd-gradient-shadow",
        "register": "functional + topological/routing",
        "idea": "does the routing topology cast a SHADOW in the gradients, and does "
                "the shadow LEAD the activation-inventory? (gd-trajectory v3)",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(), "device": device, "smoke": args.smoke,
        "config": vars(args), "consensus": cmeta, "seeds": seeds,
        "elapsed_s": round(time.time() - t0, 1),
    }

    rds = [r["readout"] for r in runs]
    agg = {
        "n_seeds": len(seeds),
        "step_gc_grad_cross": _ms([r["step_gc_grad_cross"] for r in rds]),
        "step_gc_route_cross": _ms([r["step_gc_route_cross"] for r in rds]),
        "step_heldout_acc_cross": _ms([r["step_heldout_acc_cross"] for r in rds]),
        "gc_grad_final": _ms([r["final"]["gc_grad"] for r in rds]),
        "gc_route_final": _ms([r["final"]["gc_route"] for r in rds]),
        "gc_grad_raw_final": _ms([r["final"]["gc_grad_raw"] for r in rds]),
        "shadow_before_inventory": [r["shadow_before_inventory"] for r in rds],
        "shadow_before_capability": [r["shadow_before_capability"] for r in rds],
        "inventory_before_capability": [r["inventory_before_capability"] for r in rds],
        "shadow_gap": _ms([r["shadow_gap"] for r in rds]),
    }
    tag = "smoke" if args.smoke else ("multiseed" if len(seeds) > 1 else "run")
    out = {**meta, "aggregate": agg, "runs": runs}
    (RESULTS_DIR / f"verdict_{tag}.json").write_text(json.dumps(out, indent=2))

    log("\n  ==== GRADIENT-SHADOW TOMOGRAPHY (does the shadow LEAD?) ====")
    log(f"  cross steps (baseline-relative): gc_grad@{agg['step_gc_grad_cross']} "
        f"gc_route@{agg['step_gc_route_cross']} acc@{agg['step_heldout_acc_cross']}")
    log(f"  finals: gc_grad={agg['gc_grad_final']} gc_route={agg['gc_route_final']} "
        f"gc_grad_raw(refbeam)={agg['gc_grad_raw_final']} "
        f"shadow_gap={agg['shadow_gap']}")
    log(f"  SHADOW before INVENTORY (gc_grad<gc_route): "
        f"{agg['shadow_before_inventory']}")
    log(f"  SHADOW before CAPABILITY: {agg['shadow_before_capability']}")
    log("  3-stage cascade = shadow→inventory→capability if both 'before'")
    log(f"\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)")


if __name__ == "__main__":
    main()
