#!/usr/bin/env python3
# register: topological/routing + functional
"""Frozen-basis gradient tomography — is backprop a PHOTOGRAPH that drives the
weights toward a bimodal soft-routing field routing around a FROZEN topology?

THE HYPOTHESIS (Michael): backprop is "taking a photograph of the input tokens";
each new photograph reduces the system toward a soft routing topology that uses
VERY HIGH and NEAR-ZERO gradients to route around a FROZEN topology.

WHAT IS ALGEBRA (not a hypothesis): for a weight matrix the single-example
gradient is grad_W = delta @ x.T = a rank-1 outer product = one hologram exposure
(x = object beam, delta = reference/error beam). A minibatch is sum_i delta_i x_i.T
= a multi-exposure hologram = consensus-etch. So "backprop photographs the tokens"
IS the algebra of backprop. The TESTABLE part is the DYNAMICS this drives toward.

THREE TESTABLE CLAIMS, each with the shuffled-label NULL as the gate (lambda
yardstick — an unstructured target must NOT produce the structure):

  (A) PHOTOGRAPH  : the minibatch weight-gradient is LOW effective rank (few
                    dominant exposure directions = normal-form directions), and
                    gets LOWER as the inventory crystallizes. NULL: shuffled stays
                    high-rank/diffuse.
  (B) BIMODAL     : the gradient field separates into high|near-zero modes —
                    Spearman rho(grad_mag, weight_mag) rises (s171 Zone-A signal)
                    and log grad_mag becomes bimodal. NULL: shuffled stays
                    unimodal, rho~0.
  (C) ROUTE-AROUND: low-grad (frozen) positions become sign-STABLE while high-grad
                    (active) positions carry the sign flips (the routing/delta).
                    Measured by 2nd-half flip-rate frozen<<active and
                    Spearman(grad_mag_mid, 2nd-half flip count) > 0. NULL: shuffled
                    shows frozen ~ active (everything oscillates).

Grounded prior: s171 gradient-zero-map (bimodal Zone A, rho=+0.77; high-grad =
still-reducing, near-zero = settled); s123 gradient-voting (magnitude crystal
frozen, signs route around it); s231 gradient-shadow (grad structure carves the
inventory then collapses). All snapshot/aggregate; the per-position route-around
DYNAMIC over training is the untested delta. CAVEAT (s171): at micro scale
"everything oscillates" — the freeze signal needs maturity; we measure the TREND
and gate it against the shuffled null, not an absolute threshold.

Usage:
  uv run python scripts/experiments/gd_frozen_basis.py --smoke
  uv run python scripts/experiments/gd_frozen_basis.py --seeds 0,1,2

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
from relational_loss_distillation import VOCAB, TinyLM  # noqa: E402

RESULTS_DIR = _PROJECT_ROOT / "results" / "gd-frozen-basis"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------- #
# Which weight matrices we measure. w_gate = the routing register (the gate    #
# pre-activation is the combinator routing field, mirrors gate_proj).          #
# --------------------------------------------------------------------------- #
def measured_params(model: TinyLM) -> dict[str, torch.nn.Parameter]:
    out: dict[str, torch.nn.Parameter] = {}
    for li, blk in enumerate(model.blocks):
        out[f"L{li}.w_gate"] = blk.w_gate.weight
        out[f"L{li}.w_down"] = blk.w_down.weight
        out[f"L{li}.attn_qkv"] = blk.attn.qkv.weight
        out[f"L{li}.attn_proj"] = blk.attn.proj.weight
    return out


def _routing_names(names: list[str]) -> list[str]:
    return [n for n in names if n.endswith("w_gate")]


# --------------------------------------------------------------------------- #
# Scale-free gradient-field statistics                                          #
# --------------------------------------------------------------------------- #
def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman rho via rank-Pearson; robust to heavy-tailed magnitudes."""
    if a.size < 3:
        return 0.0
    ra = np.argsort(np.argsort(a)).astype(np.float64)
    rb = np.argsort(np.argsort(b)).astype(np.float64)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / denom) if denom > 0 else 0.0


def _bimodality_coeff(x: np.ndarray) -> float:
    """Sarle's bimodality coefficient on x. b = (skew^2 + 1) / kurtosis_full.
    b > 0.555 (uniform) suggests bimodality; higher = more bimodal."""
    n = x.size
    if n < 4:
        return 0.0
    m = x.mean()
    d = x - m
    s2 = (d * d).mean()
    if s2 <= 0:
        return 0.0
    g1 = (d ** 3).mean() / (s2 ** 1.5)            # skewness
    g2 = (d ** 4).mean() / (s2 ** 2) - 3.0        # excess kurtosis
    corr = 3.0 * (n - 1) ** 2 / ((n - 2) * (n - 3))
    return float((g1 * g1 + 1.0) / (g2 + corr))


def _effrank(mat: np.ndarray) -> float:
    """Participation ratio of singular values: (sum s)^2 / sum s^2.
    A single rank-1 exposure -> 1.0; a diffuse gradient -> high."""
    try:
        s = np.linalg.svd(mat, compute_uv=False)
    except np.linalg.LinAlgError:
        return float("nan")
    s = s[s > 0]
    if s.size == 0:
        return 0.0
    return float((s.sum() ** 2) / (s * s).sum())


def grad_field(model: TinyLM, sample_batch, n_measure: int, device: str,
               shuffle: bool, rng: np.random.Generator) -> dict:
    """Accumulate per-parameter grad_mag + sign-consistency over n_measure fresh
    minibatches (NO optimizer step), and the effective rank of the first batch's
    gradient. sign_cons = |mean sign(grad)| in [0,1]: 1 = always same direction
    (still reducing), 0 = oscillating/settled."""
    params = measured_params(model)
    absum = {n: torch.zeros_like(p) for n, p in params.items()}
    signsum = {n: torch.zeros_like(p) for n, p in params.items()}
    effrank: dict[str, float] = {}
    model.eval()
    for j in range(n_measure):
        xb, yb = sample_batch()
        if shuffle:
            flat = yb.reshape(-1)
            perm = torch.from_numpy(rng.permutation(flat.shape[0])).to(device)
            yb = flat[perm].reshape(yb.shape)
        logits, _, _ = model(xb)
        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))
        model.zero_grad(set_to_none=True)
        ce.backward()
        for n, p in params.items():
            g = p.grad
            absum[n] += g.abs()
            signsum[n] += g.sign()
            if j == 0:
                effrank[n] = _effrank(g.detach().cpu().numpy().astype(np.float64))
    out = {}
    for n, p in params.items():
        gm = (absum[n] / n_measure).detach().cpu().numpy().astype(np.float64)
        sc = (signsum[n] / n_measure).abs().detach().cpu().numpy().astype(np.float64)
        wm = p.detach().abs().cpu().numpy().astype(np.float64)
        sgn = np.sign(p.detach().cpu().numpy())
        out[n] = {"grad_mag": gm.reshape(-1), "sign_cons": sc.reshape(-1),
                  "weight_mag": wm.reshape(-1), "weight_sign": sgn.reshape(-1),
                  "effrank": effrank[n]}
    return out


def pool(field: dict, names: list[str]) -> dict:
    gm = np.concatenate([field[n]["grad_mag"] for n in names])
    sc = np.concatenate([field[n]["sign_cons"] for n in names])
    wm = np.concatenate([field[n]["weight_mag"] for n in names])
    rho = _spearman(gm, wm)
    bim = _bimodality_coeff(np.log(gm + 1e-30))
    # beam concentration: fraction of total grad L1 mass in the top 5% positions
    k = max(1, int(0.05 * gm.size))
    top = np.sort(gm)[::-1][:k].sum()
    conc = float(top / (gm.sum() + 1e-30))
    effrank = float(np.mean([field[n]["effrank"] for n in names]))
    # active = high sign-consistency among high-grad; settled = low grad
    return {"rho_gw": round(rho, 4), "bimod": round(bim, 4),
            "top5pct_mass": round(conc, 4), "effrank": round(effrank, 3),
            "grad_mag_mean": round(float(gm.mean()), 8),
            "sign_cons_mean": round(float(sc.mean()), 4)}


# --------------------------------------------------------------------------- #
# One training arm                                                              #
# --------------------------------------------------------------------------- #
def train_arm(arm: str, args, device: str, seed: int, eval_items, corpus: str,
              same_input: bool) -> dict:
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed + 101)
    ids = to_byte_ids(corpus)
    T, bs = args.block_size, args.batch_size
    while ids.shape[0] <= 4 * (T + 1):
        ids = np.concatenate([ids, ids])
    n = ids.shape[0]
    fixed_ix = torch.randint(0, n - T - 1, (bs,)) if same_input else None

    def sample_batch():
        ix = fixed_ix if same_input else torch.randint(0, n - T - 1, (bs,))
        xb = torch.stack([torch.from_numpy(ids[i:i + T]) for i in ix]).to(device)
        yb = torch.stack(
            [torch.from_numpy(ids[i + 1:i + 1 + T]) for i in ix]).to(device)
        return xb, yb

    shuffle = (arm == "shuffled")
    model = TinyLM(args.d_model, args.n_head, args.n_layer, args.d_ff, T).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    names = list(measured_params(model).keys())
    route_names = _routing_names(names)

    curve: list[dict] = []
    prev_sign: dict[str, np.ndarray] | None = None
    flip_2nd: dict[str, np.ndarray] = {n: np.zeros(0) for n in names}
    gm_mid: dict[str, np.ndarray] = {}
    half = args.steps // 2
    t0 = time.time()

    def snapshot(step: int, ce_val: float) -> None:
        nonlocal prev_sign
        acc = eval_acc(model, eval_items, T, device) if not shuffle else 0.0
        field = grad_field(model, sample_batch, args.n_measure, device, shuffle, rng)
        all_pool = pool(field, names)
        route_pool = pool(field, route_names)
        # sign-flip accounting (route-around): count flips per position in 2nd half
        cur_sign = {n: field[n]["weight_sign"] for n in names}
        if prev_sign is not None and step > half:
            for n in names:
                flips = (cur_sign[n] != prev_sign[n]).astype(np.float64)
                if flip_2nd[n].size == 0:
                    flip_2nd[n] = flips
                else:
                    flip_2nd[n] += flips
        if gm_mid == {} and step >= half:
            for n in names:
                gm_mid[n] = field[n]["grad_mag"].copy()
        prev_sign = cur_sign
        curve.append({"step": step, "ce": round(ce_val, 4), "acc": round(acc, 4),
                      "all": all_pool, "route": route_pool})
        log(f"  [{arm} s{seed}] step {step:5d} | CE {ce_val:.3f} | acc {acc:.3f} "
            f"| rho_gw {route_pool['rho_gw']:+.3f} | bimod {route_pool['bimod']:.3f} "
            f"| effrank {route_pool['effrank']:.1f} | {time.time()-t0:.0f}s")

    snapshot(0, float("nan"))
    for step in range(1, args.steps + 1):
        model.train()
        xb, yb = sample_batch()
        if shuffle:
            flat = yb.reshape(-1)
            perm = torch.from_numpy(rng.permutation(flat.shape[0])).to(device)
            yb = flat[perm].reshape(yb.shape)
        logits, _, _ = model(xb)
        ce = F.cross_entropy(logits.reshape(-1, VOCAB), yb.reshape(-1))
        opt.zero_grad(set_to_none=True)
        ce.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % args.ckpt_every == 0 or step == args.steps:
            snapshot(step, float(ce.item()))

    # ROUTE-AROUND readout: 2nd-half flip rate of frozen (low-grad) vs active
    # (high-grad) positions, on the routing register, gm scored at the mid frame.
    route_flip = np.concatenate([flip_2nd[n] for n in route_names
                                 if flip_2nd[n].size]) if any(
        flip_2nd[n].size for n in route_names) else np.zeros(0)
    route_gm = np.concatenate([gm_mid[n] for n in route_names]) if gm_mid else \
        np.zeros(0)
    ra = {"frozen_flip_rate": None, "active_flip_rate": None,
          "freeze_flip_spearman": None, "n_ckpt_2nd": 0}
    if route_flip.size and route_gm.size == route_flip.size:
        n_ck = max(1, round((args.steps - half) / args.ckpt_every))
        rate = route_flip / n_ck
        order = np.argsort(route_gm)
        t = route_gm.size // 3
        frozen_idx = order[:t]            # lowest grad_mag = frozen
        active_idx = order[-t:]           # highest grad_mag = active
        ra = {"frozen_flip_rate": round(float(rate[frozen_idx].mean()), 5),
              "active_flip_rate": round(float(rate[active_idx].mean()), 5),
              "freeze_flip_spearman": round(_spearman(route_gm, route_flip), 4),
              "n_ckpt_2nd": n_ck}

    fin = curve[-1]
    base = next(c for c in curve if c["step"] == 0)
    return {"arm": arm, "seed": seed, "curve": curve, "route_around": ra,
            "final": {"ce": fin["ce"], "acc": fin["acc"],
                      "rho_gw": fin["route"]["rho_gw"],
                      "bimod": fin["route"]["bimod"],
                      "effrank": fin["route"]["effrank"],
                      "top5pct_mass": fin["route"]["top5pct_mass"]},
            "baseline": {"rho_gw": base["route"]["rho_gw"],
                         "bimod": base["route"]["bimod"],
                         "effrank": base["route"]["effrank"]}}


# --------------------------------------------------------------------------- #
def _ms(vals: list) -> list:
    a = np.array([v for v in vals if v is not None], dtype=float)
    if a.size == 0:
        return [None, None]
    return [round(float(a.mean()), 4), round(float(a.std()), 4)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps")
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--ckpt-every", type=int, default=300)
    ap.add_argument("--n-measure", type=int, default=16)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--block-size", type=int, default=128)
    ap.add_argument("--d-model", type=int, default=128)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--d-ff", type=int, default=256)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--m-eval", type=int, default=6)
    ap.add_argument("--arms", default="real,shuffled,same")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", default="")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.steps, args.ckpt_every, args.n_measure = 200, 50, 6
        args.k, args.m_eval = 4, 3
        args.d_model, args.d_ff, args.n_layer = 64, 128, 3
        args.arms = "real,shuffled"

    device = args.device
    if device == "mps" and not torch.backends.mps.is_available():
        device = "cpu"
        log("  mps unavailable -> cpu")
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    arms = [a for a in args.arms.split(",") if a.strip()]
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or [args.seed]
    log(f"  arms={arms} seeds={seeds} steps={args.steps} "
        f"ckpt_every={args.ckpt_every} n_measure={args.n_measure}")

    runs: list[dict] = []
    for seed in seeds:
        rules = validate_skeletons(SKELETONS)
        if args.smoke:
            rules = rules[:4]
        fill_rng = np.random.default_rng(seed)
        train_fillings = {tmpl: make_fillings(fill_rng, h, TRAIN_ATOMS, args.k)
                          for tmpl, h in rules}
        corpus = build_corpus(rules, train_fillings, "redex_nf", "k_varied", args.k,
                              np.random.default_rng(seed + 13))
        eval_items = build_eval_items(rules, args.m_eval,
                                      np.random.default_rng(seed + 777),
                                      TRAIN_ATOMS, train_fillings)
        log(f"  [seed {seed}] rules={len(rules)} corpus={len(corpus.encode())} B "
            f"heldout={len(eval_items)}")
        for arm in arms:
            runs.append(train_arm(arm, args, device, seed, eval_items, corpus,
                                  same_input=(arm == "same")))

    # aggregate per arm
    agg: dict[str, dict] = {}
    for arm in arms:
        ar = [r for r in runs if r["arm"] == arm]
        agg[arm] = {
            "n_seeds": len(ar),
            "final_rho_gw": _ms([r["final"]["rho_gw"] for r in ar]),
            "final_bimod": _ms([r["final"]["bimod"] for r in ar]),
            "final_effrank": _ms([r["final"]["effrank"] for r in ar]),
            "final_top5pct_mass": _ms([r["final"]["top5pct_mass"] for r in ar]),
            "baseline_rho_gw": _ms([r["baseline"]["rho_gw"] for r in ar]),
            "baseline_effrank": _ms([r["baseline"]["effrank"] for r in ar]),
            "frozen_flip_rate": _ms([r["route_around"]["frozen_flip_rate"]
                                     for r in ar]),
            "active_flip_rate": _ms([r["route_around"]["active_flip_rate"]
                                     for r in ar]),
            "freeze_flip_spearman": _ms([r["route_around"]["freeze_flip_spearman"]
                                         for r in ar]),
            "final_acc": _ms([r["final"]["acc"] for r in ar]),
        }

    # verdict deltas: real vs shuffled null
    verdict = {}
    if "real" in agg and "shuffled" in agg:
        rr, sh = agg["real"], agg["shuffled"]

        def d(key):
            return round((rr[key][0] or 0) - (sh[key][0] or 0), 4)
        ra_ratio_real = ((rr["active_flip_rate"][0] or 0)
                         / (rr["frozen_flip_rate"][0] or 1e-9))
        ra_ratio_sh = ((sh["active_flip_rate"][0] or 0)
                       / (sh["frozen_flip_rate"][0] or 1e-9))
        verdict = {
            "A_photograph_effrank_real_minus_shuffled": d("final_effrank"),
            "B_bimodal_rho_real_minus_shuffled": d("final_rho_gw"),
            "B_bimod_coeff_real_minus_shuffled": d("final_bimod"),
            "C_routearound_active_over_frozen_real": round(ra_ratio_real, 3),
            "C_routearound_active_over_frozen_shuffled": round(ra_ratio_sh, 3),
            "C_freeze_flip_spearman_real": rr["freeze_flip_spearman"],
            "C_freeze_flip_spearman_shuffled": sh["freeze_flip_spearman"],
        }

    meta = {
        "experiment": "gd-frozen-basis",
        "register": "topological/routing + functional",
        "idea": "is backprop a photograph (delta x.T exposure) that drives a "
                "bimodal soft-routing field routing around a frozen topology? "
                "Three claims (photograph/bimodal/route-around) gated by the "
                "shuffled-label null.",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(), "device": device, "smoke": args.smoke,
        "config": vars(args), "arms": arms, "seeds": seeds,
        "elapsed_s": round(time.time() - t0, 1),
    }
    tag = "smoke" if args.smoke else ("multiseed" if len(seeds) > 1 else "run")
    out = {**meta, "verdict": verdict, "aggregate": agg, "runs": runs}
    (RESULTS_DIR / f"verdict_{tag}.json").write_text(json.dumps(out, indent=2))

    log("\n  ==== FROZEN-BASIS GRADIENT TOMOGRAPHY ====")
    for arm in arms:
        a = agg[arm]
        log(f"  [{arm}] rho_gw {a['final_rho_gw']} bimod {a['final_bimod']} "
            f"effrank {a['final_effrank']} (base {a['baseline_effrank']}) "
            f"| frozen_flip {a['frozen_flip_rate']} active_flip "
            f"{a['active_flip_rate']} | acc {a['final_acc']}")
    if verdict:
        log("\n  VERDICT (real vs shuffled null):")
        log(f"   A photograph  : effrank(real)-effrank(shuf) = "
            f"{verdict['A_photograph_effrank_real_minus_shuffled']} (want < 0)")
        log(f"   B bimodal     : rho(real)-rho(shuf) = "
            f"{verdict['B_bimodal_rho_real_minus_shuffled']} (want > 0)")
        log(f"   C route-around: active/frozen flip real="
            f"{verdict['C_routearound_active_over_frozen_real']} vs shuf="
            f"{verdict['C_routearound_active_over_frozen_shuffled']} (want real>>1)")
    log(f"\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)")


if __name__ == "__main__":
    main()
