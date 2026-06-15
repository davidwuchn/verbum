#!/usr/bin/env python3
# register: topological/routing + functional
"""Per-combinator crystallization clock (mechanism-of-training, s231).

THE QUESTION (Michael, s231): "Can we write probes that show EXACTLY how GD learns?
Past runs: B-dominant first -> loss plateau -> discovers K -> phase transition (figuring
out the best ratios). Spend probes on how ATTENTION organizes against the FFN
projections."

THE INSTRUMENT (s231 reframe). The gradient carries combinator structure FROM INIT and
it is CONSUMED building the inventory (grad_z is high while inventory crystallizes, then
collapses at the inventory->capability handoff). So per combinator, the activation
silhouette is the CLOCK (when does combinator c crystallize) and the gradient silhouette
is the FUEL GAUGE (when does GD stop pushing c). Read BOTH the FFN-gate register
(sign(gate)-CMR, where the consensus crystal lives) AND the attention register
(attn-output-CMR) to test the s127 division of labor.

GROUNDING (recall, not greenfield):
  - s221 fp-spike-is-acquisition: B-FIRST (composition = strided arch's native op) ->
    plateau -> learning K (erasure, against the grain) throws numbers into chaos.
  - s151 montague-is-pre-transition: bootstrap I->K->C->B, scale-gated; transition = 2D
    (comp<->sel) collapse. Below threshold only I,K differentiate (Montague stage).
  - s127 ffn-two-functional-groups: {K,I} SELECTORS live in FFN (large deltas),
    {B,C} COMPOSERS live in ATTENTION routing (tiny FFN deltas). = "attention vs FFN".
  - c-boot-rotation-sequence: attention dominates; combinators are rotations.

FALSIFIABLE PREDICTIONS (λ measure, declare register):
  P1 (s221, CLOCK): B's activation silhouette crosses FIRST, K LAST -> order B<...<K.
     P1-null (s151): at d=128 only I,K differentiate (B,C flat) = PRE-TRANSITION -> no
     B-first->K to see (then escalate to the scale sweep). Either is informative;
     "B-first" is StrideStack-specific (s221) so plain TinyLM tests universality.
  P2 (s221, FUEL): B's gradient silhouette EXHAUSTS (peaks then collapses) BEFORE K's
     (B acquired on-grain/early, K against-grain/late stays hot longer).
  P3 (s127, REGISTER): selectors {K,I} cluster more in the GATE register, composers
     {B,C} more in the ATTENTION register; the split FORMS over training.

Catches (λ measure): per-combinator splits the modest aggregate route_z (~2.7 at
micro, s230) further -> SNR; the per-combinator CLOCK uses RAW silhouette trajectories
(relative crossings, no permutation) at every checkpoint, with permutation-null z
calibration only on the final frame + the aggregate route_z/grad_z for continuity with
s230/s231. The attn register is attn-output-CMR (continuous routing) vs the gate
sign-CMR (the consensus register) -- compared per combinator, not pooled.

Usage:
  uv run python scripts/experiments/gd_percombinator_clock.py --smoke
  uv run python scripts/experiments/gd_percombinator_clock.py --seeds 0,1,2

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
from gd_trajectory_tomography import (  # noqa: E402
    _final,
    _first_step,
    load_consensus,
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

RESULTS_DIR = _PROJECT_ROOT / "results" / "gd-percombinator-clock"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------- #
# Per-combinator silhouette: the CLOCK (raw, no permutation) + a null z (final) #
# --------------------------------------------------------------------------- #
def _percomb_margins(X: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Per-probe silhouette margin = own-centroid cosine - best-other cosine.
    X [N,d] CMR features; labels [N] str. Returns [N] margins."""
    C = np_centroids(X, labels)
    U = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-30)
    Xu = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)
    sims = Xu @ U.T                                    # [N,9]
    lab_idx = np.array([CRYSTAL.index(c) for c in labels])
    rows = np.arange(len(labels))
    own = sims[rows, lab_idx]
    other = sims.copy()
    other[rows, lab_idx] = -np.inf
    return own - other.max(axis=1)


def percomb_silhouette(X: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """[9] mean silhouette margin per combinator (the CLOCK signal, no null)."""
    margins = _percomb_margins(X, labels)
    out = np.full(len(CRYSTAL), np.nan)
    for j, c in enumerate(CRYSTAL):
        m = labels == c
        if m.any():
            out[j] = float(margins[m].mean())
    return out


def percomb_z(X: np.ndarray, labels: np.ndarray, n_perm: int, seed: int) -> np.ndarray:
    """[9] per-combinator silhouette z vs label-permutation null (FINAL-frame
    calibration; one permutation loop yields all 9 at once)."""
    obs = percomb_silhouette(X, labels)
    rng = np.random.default_rng(seed)
    null = np.stack([percomb_silhouette(X, rng.permutation(labels))
                     for _ in range(n_perm)])          # [n_perm, 9]
    mu = np.nanmean(null, axis=0)
    sd = np.nanstd(null, axis=0) + 1e-30
    return (obs - mu) / sd


def _round_vec(v: np.ndarray) -> dict:
    return {c: (None if np.isnan(x) else round(float(x), 4))
            for c, x in zip(CRYSTAL, v, strict=True)}


def per_row_align(g_student: np.ndarray, g_consensus: np.ndarray) -> np.ndarray:
    """[9] per-ROW relational-fingerprint alignment to consensus = cosine between
    student row c and consensus row c over the 8 OFF-diagonal entries (row c =
    combinator c's similarity pattern to all others). The RELATIONAL clock — the
    register where the micro crystal actually lives (s231b: categorical silhouette
    is flat, the Gram is not). Cosine (not 8-point Pearson) for stability."""
    n = len(CRYSTAL)
    out = np.full(n, np.nan)
    for i in range(n):
        m = np.ones(n, dtype=bool)
        m[i] = False
        a, b = g_student[i, m], g_consensus[i, m]
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        out[i] = 0.0 if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))
    return out


# --------------------------------------------------------------------------- #
# One movie frame: per-combinator clock in BOTH registers (gate + attention)    #
# --------------------------------------------------------------------------- #
def measure_clock(model: TinyLM, p_ids: torch.Tensor, p_len: torch.Tensor,
                  labels: np.ndarray, cap: int, consensus_gram: np.ndarray,
                  n_perm: int, probe_batch: int, seed: int, device: str,
                  final_frame: bool) -> dict:
    """ONE grad-enabled pass per probe-batch. Capture gate (FFN routing) + attn
    (attention write) ACTIVATIONS and their GRADIENTS; build per-combinator
    silhouettes (the clock + fuel gauge) in both registers + aggregate continuity
    metrics (gc_route, gc_grad, route_z, grad_z) matching s230/s231."""
    model.eval()
    attn_mod = model.blocks[cap].attn
    feats = {k: [] for k in ("gate_act", "attn_act", "gate_grad", "attn_grad")}
    for s in range(0, p_ids.shape[0], probe_batch):
        pb = p_ids[s:s + probe_batch]
        pl = p_len[s:s + probe_batch]
        captured: dict = {}
        h = attn_mod.register_forward_hook(
            lambda _m, _i, out, _c=captured: _c.__setitem__("attn", out))
        try:
            logits, _hid, gate = model(pb, capture_layer=cap)
        finally:
            h.remove()
        attn_out = captured["attn"]                    # [B,T,d], in the graph
        B, T, V = logits.shape
        shift_logits = logits[:, :-1, :].reshape(-1, V)
        shift_tgt = pb[:, 1:].reshape(-1)
        ce_tok = F.cross_entropy(shift_logits, shift_tgt, reduction="none").reshape(
            B, T - 1)
        posn = torch.arange(T - 1, device=device)[None, :]
        mask = (posn < (pl[:, None] - 1)).float()
        loss = (ce_tok * mask).sum() / mask.sum().clamp_min(1.0)
        g_gate, g_attn = torch.autograd.grad(loss, [gate, attn_out])
        # ACTIVATIONS at the last real token
        feats["gate_act"].append(gather_last(gate, pl).detach().cpu().numpy())
        feats["attn_act"].append(gather_last(attn_out, pl).detach().cpu().numpy())
        # GRADIENTS mean-pooled over SUPERVISED predictor positions [0, len-2]
        pm = (torch.arange(T, device=device)[None, :] < (pl[:, None] - 1)).float()
        den = pm.sum(1, keepdim=True).clamp_min(1.0)
        feats["gate_grad"].append(
            ((g_gate * pm[..., None]).sum(1) / den).detach().cpu().numpy())
        feats["attn_grad"].append(
            ((g_attn * pm[..., None]).sum(1) / den).detach().cpu().numpy())
    F64 = {k: np.concatenate(v, axis=0).astype(np.float64) for k, v in feats.items()}

    # register features: gate = sign-CMR (consensus register); attn = CMR (continuous)
    gate_act = np_cmr(np.sign(F64["gate_act"]))
    attn_act = np_cmr(F64["attn_act"])
    gate_grad = np_cmr(np.sign(F64["gate_grad"]))
    attn_grad = np_cmr(np.sign(F64["attn_grad"]))

    # aggregate continuity (matches s230/s231): gc_route, route_z, gc_grad, grad_z
    gate_gram = np_gram(np_centroids(gate_act, labels))
    attn_gram = np_gram(np_centroids(attn_act, labels))
    route_sil = np_silhouette_null(gate_act, labels, n_perm, seed)
    gc_route = offdiag_corr(gate_gram, consensus_gram)
    grad_sil = np_silhouette_null(gate_grad, labels, n_perm, seed)
    gc_grad = offdiag_corr(np_gram(np_centroids(gate_grad, labels)), consensus_gram)

    frame = {
        "gc_route": round(float(gc_route), 4),
        "route_z": round(float(route_sil["z"]), 4),
        "gc_grad": round(float(gc_grad), 4),
        "grad_z": round(float(grad_sil["z"]), 4),
        # per-combinator CATEGORICAL clock (raw silhouette; s231b: flat at micro)
        "pc_act_gate": _round_vec(percomb_silhouette(gate_act, labels)),
        "pc_act_attn": _round_vec(percomb_silhouette(attn_act, labels)),
        "pc_grad_gate": _round_vec(percomb_silhouette(gate_grad, labels)),
        "pc_grad_attn": _round_vec(percomb_silhouette(attn_grad, labels)),
        # per-ROW RELATIONAL clock (s231b fix — the register the crystal lives in)
        "pc_row_gc": _round_vec(per_row_align(gate_gram, consensus_gram)),
        "pc_row_gc_attn": _round_vec(per_row_align(attn_gram, consensus_gram)),
    }
    if final_frame:                                    # null-calibrated z, once
        frame["pc_act_gate_z"] = _round_vec(percomb_z(gate_act, labels, n_perm, seed))
        frame["pc_act_attn_z"] = _round_vec(percomb_z(attn_act, labels, n_perm, seed))
        frame["pc_grad_gate_z"] = _round_vec(percomb_z(gate_grad, labels, n_perm, seed))
    return frame


# --------------------------------------------------------------------------- #
# Readout: acquisition ORDER, B-vs-K fuel, gate-vs-attn division of labor        #
# --------------------------------------------------------------------------- #
def _pc_series(curve: list[dict], key: str, comb: str) -> list[tuple[int, float]]:
    out = []
    for row in curve:
        v = row[key].get(comb)
        if v is not None and not (isinstance(row["ce"], float) and np.isnan(row["ce"])):
            out.append((row["step"], v))
    return out


def _cross_step(series: list[tuple[int, float]], frac: float) -> int | None:
    """First step where the per-combinator silhouette reaches init + frac*(final-init),
    baseline-relative (init = the step-0 untrained frame)."""
    if len(series) < 2:
        return None
    v0, vf = series[0][1], series[-1][1]
    if vf <= v0:
        return None
    target = v0 + frac * (vf - v0)
    for step, v in series:
        if step > 0 and v >= target:
            return step
    return None


def _peak_then_collapse(
        series: list[tuple[int, float]]) -> tuple[int | None, int | None]:
    """Fuel gauge: peak step, and the first later step where it drops below
    half the (peak - init) rise above init (the exhaustion / collapse)."""
    if len(series) < 3:
        return None, None
    v0 = series[0][1]
    pk_step, pk_val = max(series, key=lambda x: x[1])
    half = v0 + 0.5 * (pk_val - v0)
    coll = next((step for step, v in series if step > pk_step and v < half), None)
    return pk_step, coll


def readout(curve: list[dict], gc_frac: float, acc_frac: float) -> dict:
    init = curve[0]
    fin = curve[-1]
    # CATEGORICAL clock (s231b: flat at micro) — acquisition order from GATE silhouette
    cross = {c: _cross_step(_pc_series(curve, "pc_act_gate", c), gc_frac)
             for c in CRYSTAL}
    order = sorted(CRYSTAL, key=lambda c: (cross[c] is None, cross[c] or 10**9))
    # RELATIONAL clock (s231b fix) — order from per-ROW Gram alignment to consensus
    rcross = {c: _cross_step(_pc_series(curve, "pc_row_gc", c), gc_frac)
              for c in CRYSTAL}
    rorder = sorted(CRYSTAL, key=lambda c: (rcross[c] is None, rcross[c] or 10**9))
    rb, rk = rcross.get("B"), rcross.get("K")
    # relational P3: does combinator c's fingerprint align better in attn vs gate?
    rregion = {}
    for c in CRYSTAL:
        g = fin["pc_row_gc"].get(c)
        a = fin["pc_row_gc_attn"].get(c)
        rregion[c] = ("attn" if (g is not None and a is not None and a > g)
                      else "gate" if (g is not None and a is not None) else "n/a")
    # B-vs-K fuel exhaustion (gate gradient)
    fuel = {c: _peak_then_collapse(_pc_series(curve, "pc_grad_gate", c))
            for c in CRYSTAL}
    b_cross, k_cross = cross.get("B"), cross.get("K")
    b_coll, k_coll = fuel["B"][1], fuel["K"][1]
    # gate-vs-attn division of labor (final-frame per-combinator silhouette)
    region = {}
    for c in CRYSTAL:
        g = fin["pc_act_gate"].get(c)
        a = fin["pc_act_attn"].get(c)
        region[c] = ("gate" if (g is not None and a is not None and g > a)
                     else "attn" if (g is not None and a is not None) else "n/a")
    return {
        "acquisition_order_gate": order,
        "cross_step": cross,
        "B_cross": b_cross, "K_cross": k_cross,
        "B_before_K_clock": (None if b_cross is None or k_cross is None
                             else b_cross < k_cross),
        # RELATIONAL clock (the s231b fix — primary readout)
        "relational_order": rorder,
        "relational_cross_step": rcross,
        "B_cross_rel": rb, "K_cross_rel": rk,
        "B_before_K_relational": (None if rb is None or rk is None else rb < rk),
        "relational_region_gate_vs_attn": rregion,
        "composers_BC_attn_relational": [rregion.get("B"), rregion.get("C")],
        "selectors_KI_gate_relational": [rregion.get("K"), rregion.get("I")],
        "fuel_peak_collapse": {c: {"peak": fuel[c][0], "collapse": fuel[c][1]}
                               for c in CRYSTAL},
        "B_fuel_exhausts_before_K": (None if b_coll is None or k_coll is None
                                     else b_coll < k_coll),
        "region_gate_vs_attn": region,
        "selectors_KI_gate": [region.get("K"), region.get("I")],
        "composers_BC_attn": [region.get("B"), region.get("C")],
        "final_pc_act_gate_z": fin.get("pc_act_gate_z"),
        "final_pc_act_attn_z": fin.get("pc_act_attn_z"),
        "agg_final": {"gc_route": _final(curve, "gc_route"),
                      "gc_grad": _final(curve, "gc_grad"),
                      "route_z": _final(curve, "route_z"),
                      "heldout_acc": _final(curve, "heldout_acc")},
        "agg_route_cross": _first_step(
            curve, "gc_route",
            float(init["gc_route"]) + gc_frac * (_final(curve, "gc_route")
                                                 - float(init["gc_route"]))),
        "agg_acc_cross": _first_step(
            curve, "heldout_acc",
            float(init["heldout_acc"]) + acc_frac * (_final(curve, "heldout_acc")
                                                     - float(init["heldout_acc"]))),
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
    T = args.block_size
    while ids.shape[0] <= 4 * (T + 1):
        ids = np.concatenate([ids, ids])
    n = ids.shape[0]
    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff, T).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    cap = args.capture_layer if args.capture_layer >= 0 else args.n_layer // 2

    curve: list[dict] = []
    t0 = time.time()

    def snapshot(step: int, ce_val: float, final_frame: bool) -> None:
        acc = eval_acc(model, eval_items, T, device)
        fr = measure_clock(model, p_ids, p_len, probe_labels, cap, consensus_gram,
                           args.n_perm, args.probe_batch, seed, device, final_frame)
        row = {"step": step, "ce": round(ce_val, 4), "heldout_acc": round(acc, 4),
               **fr}
        curve.append(row)
        ag = (f"{row['pc_act_gate'].get('B')}" if row["pc_act_gate"].get("B")
              is None else f"{row['pc_act_gate']['B']:+.3f}")
        ak = (f"{row['pc_act_gate'].get('K')}" if row["pc_act_gate"].get("K")
              is None else f"{row['pc_act_gate']['K']:+.3f}")
        log(f"  [s{seed}] step {step:5d} | CE {ce_val:.3f} | acc {acc:.3f} | "
            f"gc_route {fr['gc_route']:+.3f} | pcB {ag} pcK {ak} | "
            f"grad_z {fr['grad_z']:+.2f} | {time.time()-t0:.0f}s")

    snapshot(0, float("nan"), final_frame=False)
    for step in range(1, args.steps + 1):
        model.train()
        ix = torch.randint(0, n - T - 1, (args.batch_size,))
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
            snapshot(step, float(ce.item()), final_frame=(step == args.steps))

    rd = readout([r for r in curve if not (isinstance(r["ce"], float)
                                           and np.isnan(r["ce"])) or r["step"] == 0],
                 args.gc_frac, args.acc_frac)
    return {"seed": seed, "capture_layer": cap, "curve": curve, "readout": rd}


def _mode(vals: list) -> dict:
    out: dict = {}
    for v in vals:
        out[str(v)] = out.get(str(v), 0) + 1
    return out


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
    ap.add_argument("--n-perm", type=int, default=200)
    ap.add_argument("--gc-frac", type=float, default=0.5)
    ap.add_argument("--acc-frac", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", default="")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.steps, args.ckpt_every = 120, 40
        args.k, args.m_eval, args.n_perm = 4, 3, 80
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
    log(f"  crystal probes={probe_ids.shape[0]} | per-combinator counts: "
        f"{ {c: int((probe_labels == c).sum()) for c in CRYSTAL} }")

    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or [args.seed]
    log(f"  seeds={seeds} steps={args.steps} ckpt_every={args.ckpt_every}")
    runs = [train_seed(args, device, consensus_gram, sd, p_ids, p_len, probe_labels)
            for sd in seeds]

    meta = {
        "experiment": "gd-percombinator-clock",
        "register": "topological/routing + functional",
        "idea": "per-combinator crystallization clock + gradient fuel-gauge in BOTH "
                "the FFN-gate and attention registers (mechanism-of-training, s231)",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(), "device": device, "smoke": args.smoke,
        "config": vars(args), "consensus": cmeta, "seeds": seeds,
        "elapsed_s": round(time.time() - t0, 1),
    }
    rds = [r["readout"] for r in runs]
    agg = {
        "n_seeds": len(seeds),
        # RELATIONAL clock (s231b fix — primary)
        "relational_order": [r["relational_order"] for r in rds],
        "B_before_K_relational": _mode([r["B_before_K_relational"] for r in rds]),
        "composers_BC_attn_relational": _mode(
            [tuple(r["composers_BC_attn_relational"]) for r in rds]),
        "selectors_KI_gate_relational": _mode(
            [tuple(r["selectors_KI_gate_relational"]) for r in rds]),
        "relational_region_gate_vs_attn": [
            r["relational_region_gate_vs_attn"] for r in rds],
        # CATEGORICAL clock (s231b: flat at micro — kept for continuity)
        "acquisition_order_gate": [r["acquisition_order_gate"] for r in rds],
        "B_before_K_clock": _mode([r["B_before_K_clock"] for r in rds]),
        "B_fuel_exhausts_before_K": _mode([r["B_fuel_exhausts_before_K"] for r in rds]),
        "region_gate_vs_attn": [r["region_gate_vs_attn"] for r in rds],
    }
    tag = "smoke" if args.smoke else ("multiseed" if len(seeds) > 1 else "run")
    out = {**meta, "aggregate": agg, "runs": runs}
    (RESULTS_DIR / f"verdict_{tag}.json").write_text(json.dumps(out, indent=2))

    log("\n  ==== PER-COMBINATOR CLOCK (how does GD learn?) ====")
    log("  -- RELATIONAL clock (per-row Gram alignment; the s231b fix) --")
    for r in rds:
        log(f"  rel order: {' < '.join(r['relational_order'])} | "
            f"B@{r['B_cross_rel']} K@{r['K_cross_rel']} "
            f"(B<K={r['B_before_K_relational']})")
    log(f"  B_before_K_relational: {agg['B_before_K_relational']}")
    log(f"  composers {{B,C}} fingerprint region (want attn): "
        f"{agg['composers_BC_attn_relational']}")
    log(f"  selectors {{K,I}} fingerprint region (want gate): "
        f"{agg['selectors_KI_gate_relational']}")
    log("  -- CATEGORICAL clock (s231b: flat at micro) --")
    for r in rds:
        log(f"  order(gate): {' < '.join(r['acquisition_order_gate'])} | "
            f"B@{r['B_cross']} K@{r['K_cross']} (B<K={r['B_before_K_clock']})")
    log(f"  B_before_K_clock: {agg['B_before_K_clock']}")
    log(f"\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)")


if __name__ == "__main__":
    main()
