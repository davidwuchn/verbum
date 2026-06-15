#!/usr/bin/env python3
# register: functional + topological/routing
"""Gradient-trajectory tomography v1 — reverse-engineering GD in INVARIANT
coordinates over training (session 230).

THE IDEA (Michael, s229): "If models do a holographic inference process, why
can't we reverse-engineer what GD is doing? Use the micro model."

You CANNOT reverse-engineer GD in WEIGHT space (gauge + superposition). But on
the micro model, in INVARIANT coordinates (the routing register, CMR), prediction-
gated, with a GROUND-TRUTH target, watching the relational geometry develop frame-
by-frame over checkpoints IS reverse-engineering what GD is doing.

PRIOR ART (build on, do not reinvent): holographic-tomography.md (SPATIAL, cross-
MODEL) + relational-loss-distillation.md (the instruments + the s223 dissociation)
+ v4.1/v6.1-training-trajectory (trajectory tracking). DELTA HERE = TEMPORAL
(intersect training STEPS, single micro model) + GROUND-TRUTH target + reference-
beam CONTROL run as a movie.

THE GROUND-TRUTH TARGET = the CONSENSUS CRYSTAL (s219 / combinator-map-consensus):
the 9x9 combinator routing Gram AGREED across 10 open models. Highest chance of
being model-agnostic precisely because the models already agreed. NOT one teacher.

THE COLLISION (the reference beam decides this too): naively watching "what changed
this step" mostly reconstructs GAUGE MOTION + FREQUENCY STATS (the common mode) -
a gorgeous movie of the wrong thing (s222 = discrete-topology churn). So we read
the trajectory through TWO registers at once:
  routing (sign(gate)-CMR)  -> the FUNCTION being built (gc_route, route_z)
  raw     (hidden-CMR)       -> the REFERENCE BEAM / common-mode control (gc_raw)
The function is INVISIBLE in the raw register (s223 silhouette ~ -0.035); it appears
only in the routing register after CMR. So gc_raw should stay flat while gc_route
rises - demonstrating that naive GD-watching sees the common mode, not the function.

DESIGN: CE-only TinyLM trains on the s229 beta-reduction curriculum (the CAPABILITY,
kernel-minted, k_varied = the burn-in regime that generalizes). At dense checkpoints
we measure the combinator routing GEOMETRY on the INDEPENDENT crystal probes (the
INVENTORY), correlate to the consensus crystal, and log it as a movie alongside the
s229 held-out rule-generalization metric (the capability curve) + eff_dim (the s105
Q-collapse / flood-lamp watch).

FALSIFIABLE PREDICTIONS:
  reference beam : gc_route + route_z rise (the function); gc_raw stays low/flat
                   (the common mode invisible to the function target) -> reproduces
                   s223 (b) as a TRAJECTORY.
  inventory<capability : routing geometry crystallizes BEFORE held-out
                   generalization rises (geometry=inventory (x) continuation=
                   capability, s224).
  Q-collapse     : eff_dim may collapse toward 1 (flood-lamp, s105); if so THAT is
                   the reverse-engineered GD behavior and the relational/laser
                   constraint is the lever.

Usage:
  uv run python scripts/experiments/gd_trajectory_tomography.py --smoke
  uv run python scripts/experiments/gd_trajectory_tomography.py --steps 6000
  uv run python scripts/experiments/gd_trajectory_tomography.py --seeds 0,1,2

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

# instruments + tiny student (one model definition, no fork)
# curriculum minting + the s229 held-out generalization metric (no fork)
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
from relational_loss_distillation import (  # noqa: E402
    CRYSTAL,
    VOCAB,
    TinyLM,
    gather_last,
    load_crystal_probe_batch,
    np_centroids,
    np_cmr,
    np_gram,
    np_silhouette_null,
    offdiag_corr,
)

RESULTS_DIR = _PROJECT_ROOT / "results" / "gd-trajectory-tomography"
CONSENSUS_PATH = (_PROJECT_ROOT / "results" / "combinator-map-consensus"
                  / "consensus.json")


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------- #
# Ground-truth target: the CONSENSUS CRYSTAL (10-model agreed routing Gram)     #
# --------------------------------------------------------------------------- #
def load_consensus() -> tuple[np.ndarray, dict]:
    d = json.loads(CONSENSUS_PATH.read_text())
    order = list(d["crystal_order"])
    if order != CRYSTAL:
        raise ValueError(f"consensus crystal_order {order} != instrument {CRYSTAL}")
    g = np.array(d["consensus_gram"], dtype=np.float64)
    meta = {
        "consensus_path": str(CONSENSUS_PATH.relative_to(_PROJECT_ROOT)),
        "consensus_git_sha": d.get("git_sha", "unknown"),
        "n_models": d.get("n_models"),
        "models": list(d.get("models", [])),
        "harvest_frac": d.get("harvest_frac"),
        "offdiag_mean": float(g[~np.eye(9, dtype=bool)].mean()),
    }
    return g, meta


# --------------------------------------------------------------------------- #
# Q-collapse watch (s105): effective dimension = participation ratio           #
# --------------------------------------------------------------------------- #
def eff_dim(X: np.ndarray) -> float:
    """Participation ratio of the centered-feature covariance spectrum.
    PR = (sum lambda)^2 / sum(lambda^2) in [1, min(N,d)]. 1 = flood-lamp collapse."""
    Xc = X - X.mean(axis=0, keepdims=True)
    sv = np.linalg.svd(Xc, compute_uv=False)
    ev = sv.astype(np.float64) ** 2
    denom = (ev ** 2).sum()
    if denom < 1e-30:
        return 1.0
    return float((ev.sum() ** 2) / denom)


# --------------------------------------------------------------------------- #
# Geometry measurement on the INDEPENDENT crystal probes (the movie frame)     #
# --------------------------------------------------------------------------- #
@torch.no_grad()
def measure_geometry(model: TinyLM, p_ids: torch.Tensor, p_len: torch.Tensor,
                     labels: np.ndarray, cap: int, consensus_gram: np.ndarray,
                     n_perm: int, probe_batch: int, seed: int) -> dict:
    """One movie frame: routing-register (function) vs raw-register (reference
    beam), both correlated to the consensus crystal + eff_dim (Q-collapse)."""
    model.eval()
    gate_feats, hid_feats = [], []
    for s in range(0, p_ids.shape[0], probe_batch):
        pb = p_ids[s:s + probe_batch]
        _, hid, gate = model(pb, capture_layer=cap)
        pl = p_len[s:s + probe_batch]
        gate_feats.append(gather_last(gate, pl).cpu().numpy())
        hid_feats.append(gather_last(hid, pl).cpu().numpy())
    gate_np = np.concatenate(gate_feats, axis=0).astype(np.float64)
    hid_np = np.concatenate(hid_feats, axis=0).astype(np.float64)

    # routing register = sign(gate)-CMR (the register the consensus was built in)
    sign_cmr = np_cmr(np.sign(gate_np))
    route_sil = np_silhouette_null(sign_cmr, labels, n_perm, seed)
    route_gram = np_gram(np_centroids(sign_cmr, labels))
    gc_route = offdiag_corr(route_gram, consensus_gram)

    # raw register = hidden-CMR (the REFERENCE BEAM / common-mode control)
    hid_cmr = np_cmr(hid_np)
    hidden_sil = np_silhouette_null(hid_cmr, labels, n_perm, seed)
    hid_gram = np_gram(np_centroids(hid_cmr, labels))
    gc_raw = offdiag_corr(hid_gram, consensus_gram)

    return {
        "route_z": round(float(route_sil["z"]), 4),
        "route_p": round(float(route_sil["p_value"]), 5),
        "gc_route": round(float(gc_route), 4),
        "hidden_z": round(float(hidden_sil["z"]), 4),
        "gc_raw": round(float(gc_raw), 4),
        "eff_dim_route": round(eff_dim(gate_np), 3),
        "eff_dim_raw": round(eff_dim(hid_np), 3),
    }


# --------------------------------------------------------------------------- #
# Readout: when does the invariant crystallize vs CE-plateau vs capability?     #
# --------------------------------------------------------------------------- #
def _first_step(curve: list[dict], key: str, thresh: float,
                ge: bool = True) -> int | None:
    for row in curve:
        v = row[key]
        if v is None:
            continue
        if (ge and v >= thresh) or (not ge and v <= thresh):
            return int(row["step"])
    return None


def _final(curve: list[dict], key: str) -> float:
    vals = [r[key] for r in curve if r.get(key) is not None]
    return float(vals[-1]) if vals else 0.0


def readout(curve: list[dict], init: dict, gc_frac: float, acc_frac: float,
            z_thresh: float, ce_tol: float) -> dict:
    """Crossings are measured relative to the INIT (untrained) baseline so we
    time the function GD builds, not the random-init gauge/common mode. init is
    the step-0 frame (gc_route/route_z/heldout_acc of the untrained model)."""
    final_gc = _final(curve, "gc_route")
    final_acc = _final(curve, "heldout_acc")
    final_ce = _final(curve, "ce")
    gc0 = float(init.get("gc_route", 0.0))
    acc0 = float(init.get("heldout_acc", 0.0))
    # crystallization = gc_route gains gc_frac of the init->final DELTA over baseline
    gc_target = gc0 + gc_frac * (final_gc - gc0)
    s_gc = (_first_step(curve, "gc_route", gc_target) if final_gc > gc0 else None)
    s_z = _first_step(curve, "route_z", z_thresh)
    # capability = held-out rule generalization gains acc_frac of its delta
    acc_target = acc0 + acc_frac * (final_acc - acc0)
    s_acc = (_first_step(curve, "heldout_acc", acc_target)
             if final_acc > acc0 else None)
    # CE plateau = within ce_tol of the final CE
    s_ce = _first_step(curve, "ce", final_ce * (1.0 + ce_tol), ge=False)

    def order(a: int | None, b: int | None) -> str:
        if a is None or b is None:
            return "n/a"
        if a < b:
            return "before"
        if a > b:
            return "after"
        return "same"

    return {
        "final": {"gc_route": round(final_gc, 4), "gc_raw": _final(curve, "gc_raw"),
                  "route_z": _final(curve, "route_z"),
                  "heldout_acc": round(final_acc, 4), "ce": round(final_ce, 4),
                  "eff_dim_route": _final(curve, "eff_dim_route"),
                  "eff_dim_raw": _final(curve, "eff_dim_raw")},
        "step_gc_route_cross": s_gc,
        "step_route_z_cross": s_z,
        "step_heldout_acc_cross": s_acc,
        "step_ce_plateau": s_ce,
        "inventory_before_capability": order(s_gc, s_acc),
        "routing_z_before_capability": order(s_z, s_acc),
        "crystallize_before_ce_plateau": order(s_gc, s_ce),
        "reference_beam": {
            "gc_route_final": round(final_gc, 4),
            "gc_raw_final": _final(curve, "gc_raw"),
            "route_tracks_function": final_gc > abs(_final(curve, "gc_raw")),
        },
    }


# --------------------------------------------------------------------------- #
# Train one seed: CE-only, dense checkpoints, geometry movie                    #
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
    corpus = build_corpus(rules, train_fillings, args.format, "k_varied", args.k,
                          np.random.default_rng(seed + 13))
    eval_rng = np.random.default_rng(seed + 777)
    eval_items = build_eval_items(rules, args.m_eval, eval_rng, TRAIN_ATOMS,
                                  train_fillings)  # heldout = combos (rule gen.)
    log(f"  [seed {seed}] rules={len(rules)} corpus={len(corpus.encode())} B "
        f"heldout_eval={len(eval_items)} format={args.format}")

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
        geo = measure_geometry(model, p_ids, p_len, probe_labels, cap,
                               consensus_gram, args.n_perm, args.probe_batch, seed)
        row = {"step": step, "tokens": step * bs * T,
               "ce": round(ce_val, 4), "heldout_acc": round(acc, 4), **geo}
        curve.append(row)
        log(f"  [seed {seed}] step {step:5d} | CE {ce_val:.3f} | acc {acc:.3f} "
            f"| route_z {geo['route_z']:+.2f} | gc_route {geo['gc_route']:+.3f} "
            f"| gc_raw {geo['gc_raw']:+.3f} | effd {geo['eff_dim_route']:.1f} "
            f"| {time.time()-t0:.0f}s")

    # frame at init (step 0) = the gauge baseline before any GD
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

    # readout uses post-init frames only (drop the nan-CE init frame for CE plateau)
    # but baselines crossings against the step-0 init frame (the gauge common mode)
    init_frame = curve[0]
    rd = readout([r for r in curve if not (isinstance(r["ce"], float)
                                           and np.isnan(r["ce"]))],
                 init_frame, args.gc_frac, args.acc_frac, args.z_thresh, args.ce_tol)
    rd["init_baseline"] = {"gc_route": init_frame["gc_route"],
                           "gc_raw": init_frame["gc_raw"],
                           "route_z": init_frame["route_z"],
                           "heldout_acc": init_frame["heldout_acc"]}
    return {"seed": seed, "capture_layer": cap, "corpus_bytes": int(ids.shape[0]),
            "curve": curve, "readout": rd}


def _ms(vals: list[float]) -> list[float]:
    a = np.array([v for v in vals if v is not None], dtype=float)
    if a.size == 0:
        return [None, None]
    return [round(float(a.mean()), 2), round(float(a.std()), 2)]


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps")
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--ckpt-every", type=int, default=200,
                    help="dense checkpoint interval (the movie frame rate)")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--block-size", type=int, default=128)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--d-ff", type=int, default=256)
    ap.add_argument("--capture-layer", type=int, default=-1, help="-1 = middle")
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--format", choices=["redex_nf", "full_trace"],
                    default="redex_nf", help="curriculum photo format (s229)")
    ap.add_argument("--k", type=int, default=8, help="k_varied exposures/rule")
    ap.add_argument("--m-eval", type=int, default=6, help="held-out instances/rule")
    ap.add_argument("--probe-batch", type=int, default=64)
    ap.add_argument("--probe-max-len", type=int, default=96)
    ap.add_argument("--n-perm", type=int, default=300, help="silhouette null perms")
    ap.add_argument("--gc-frac", type=float, default=0.5,
                    help="crystallization = gc_route reaches this frac of final")
    ap.add_argument("--acc-frac", type=float, default=0.5,
                    help="capability rise = heldout_acc reaches this frac of final")
    ap.add_argument("--z-thresh", type=float, default=3.0,
                    help="route_z crossing threshold (significant structure)")
    ap.add_argument("--ce-tol", type=float, default=0.05,
                    help="CE plateau = within this frac of final CE")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", default="",
                    help="csv seeds for multi-seed harden (overrides --seed)")
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
    log(f"  consensus crystal: {cmeta['n_models']} models, offdiag_mean="
        f"{cmeta['offdiag_mean']:+.3f}, sha={cmeta['consensus_git_sha']}")

    probe_ids, probe_len, probe_labels = load_crystal_probe_batch(args.probe_max_len)
    p_ids = torch.tensor(probe_ids, device=device)
    p_len = torch.tensor(probe_len, device=device)
    log(f"  crystal probes={probe_ids.shape[0]} maxlen={probe_ids.shape[1]}")

    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or [args.seed]
    log(f"  seeds={seeds} steps={args.steps} ckpt_every={args.ckpt_every}")

    runs = [train_seed(args, device, consensus_gram, sd, p_ids, p_len, probe_labels)
            for sd in seeds]

    meta = {
        "experiment": "gd-trajectory-tomography",
        "register": "functional + topological/routing",
        "idea": "reverse-engineer GD in invariant coords; consensus-crystal target",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(),
        "device": device,
        "smoke": args.smoke,
        "config": vars(args),
        "consensus": cmeta,
        "seeds": seeds,
        "elapsed_s": round(time.time() - t0, 1),
    }

    if len(seeds) == 1:
        out = {**meta, **runs[0]}
        tag = "smoke" if args.smoke else "run"
        (RESULTS_DIR / f"verdict_{tag}.json").write_text(json.dumps(out, indent=2))
        rd = runs[0]["readout"]
        log("\n  ==== GD TRAJECTORY TOMOGRAPHY (single seed) ====")
        log(f"  final: gc_route={rd['final']['gc_route']:+.3f} "
            f"gc_raw={rd['final']['gc_raw']:+.3f} "
            f"route_z={rd['final']['route_z']:+.2f} "
            f"heldout_acc={rd['final']['heldout_acc']:.3f} "
            f"eff_dim_route={rd['final']['eff_dim_route']}")
        log(f"  crystallize(gc_route 50%)@{rd['step_gc_route_cross']} | "
            f"route_z>={args.z_thresh}@{rd['step_route_z_cross']} | "
            f"heldout_acc 50%@{rd['step_heldout_acc_cross']} | "
            f"CE plateau@{rd['step_ce_plateau']}")
        log(f"  INVENTORY before CAPABILITY: {rd['inventory_before_capability']} "
            f"(route_z: {rd['routing_z_before_capability']})")
        log(f"  REFERENCE BEAM: gc_route {rd['reference_beam']['gc_route_final']:+.3f} "
            f"vs gc_raw {rd['reference_beam']['gc_raw_final']:+.3f} -> "
            f"route_tracks_function={rd['reference_beam']['route_tracks_function']}")
        log(f"\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)")
        return

    # multi-seed aggregate of the readout ordering
    rds = [r["readout"] for r in runs]
    agg = {
        "n_seeds": len(seeds),
        "step_gc_route_cross": _ms([r["step_gc_route_cross"] for r in rds]),
        "step_route_z_cross": _ms([r["step_route_z_cross"] for r in rds]),
        "step_heldout_acc_cross": _ms([r["step_heldout_acc_cross"] for r in rds]),
        "step_ce_plateau": _ms([r["step_ce_plateau"] for r in rds]),
        "gc_route_final": _ms([r["final"]["gc_route"] for r in rds]),
        "gc_raw_final": _ms([r["final"]["gc_raw"] for r in rds]),
        "route_z_final": _ms([r["final"]["route_z"] for r in rds]),
        "heldout_acc_final": _ms([r["final"]["heldout_acc"] for r in rds]),
        "inventory_before_capability": [r["inventory_before_capability"]
                                        for r in rds],
        "route_tracks_function": [r["reference_beam"]["route_tracks_function"]
                                  for r in rds],
    }
    out = {**meta, "aggregate": agg, "runs": runs}
    (RESULTS_DIR / "verdict_multiseed.json").write_text(json.dumps(out, indent=2))
    log("\n  ==== GD TRAJECTORY TOMOGRAPHY (multi-seed) ====")
    log(f"  crystallize(gc_route)@{agg['step_gc_route_cross']} | "
        f"route_z@{agg['step_route_z_cross']} | "
        f"heldout_acc@{agg['step_heldout_acc_cross']} | "
        f"CE plateau@{agg['step_ce_plateau']}  (step mean+-std)")
    log(f"  gc_route_final={agg['gc_route_final']} gc_raw_final={agg['gc_raw_final']} "
        f"route_z_final={agg['route_z_final']}")
    log(f"  inventory_before_capability per-seed: {agg['inventory_before_capability']}")
    log(f"  route_tracks_function per-seed: {agg['route_tracks_function']}")
    log(f"\n  wrote {RESULTS_DIR / 'verdict_multiseed.json'}  ({meta['elapsed_s']}s)")


if __name__ == "__main__":
    main()
