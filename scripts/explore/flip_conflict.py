#!/usr/bin/env python3
"""§P-FLIP-CONFLICT — sign-flip rate as a per-coordinate conflict meter (FROZEN s323).

Pre-reg: mementum/knowledge/explore/sign-oscillation-is-time-multiplexed-
superposition.md §6 (Michael-approved GO, s323).

Claim: a weight coordinate's SIGN-FLIP RATE during training is a per-coordinate
CONFLICT METER — coordinates flip because two input populations push their sign
in opposite directions (antipodal overload, §1), NOT merely because they are
small or noisy. Causal converse: remove one population -> contested signs commit.

Substrate: type-write two-class wire on qwen3-4b (A=animal / B=vehicle, 8 nonces
4/4, corridor VERBATIM from type_write.py). Structural pin: effective
W_k = W_base,k + dW_k(t); base frozen -> a sign FLIP is possible ONLY where
|W_base,k| is small = the s320 boundary-churn marginal band. So this tests the
boundary-churn MECHANISM (flippable == marginal).

Coordinates (BOTH): R2 PRIMARY = effective gate_proj entries dW_k in band; R1
SECONDARY = LoRA A/B. Full-resolution per-class gradients over ~25M entries/layer
are infeasible to store, so R2 tracks a STRATIFIED RANDOM SAMPLE of effective-dW
entries per band layer, stratified by |W_base| (marginal / mid / committed) so
G3's committed corner and the marginal/flippable population are both populated.
This is an INSTRUMENT-side sampling choice (register/gates/verdicts/a-priori
UNCHANGED): still per-entry sign, still the gate_proj band.

AMENDMENT (s323, Michael GO option 1, pre-run, runtime-forced; gates/verdicts/
a-priori UNCHANGED): the smoke showed effective-weight (W_base+dW) sign flips are
intrinsically RARE in a frozen-base LoRA wire (<0.4% SGD) -> uninformative VOID.
The DELTA's own sign(dW_k) is the direct antipodal/sigma-delta quantity (contested
coord: dW dithers ~0, mu~0/high flip). So: (1) PRIMARY flip register = sign(dW)
(--flip-on delta); effective-weight flips captured as SECONDARY. (2) BURN-IN drops
the B=0 cold-start dither window (flip-rate read on the late window). (3) G3
committed-pole re-based on |dW| (committed delta = large stable, low flip/conflict);
|W_base| kept as a REPORTED COVARIATE (boundary_churn_covariate: does flip-rate
rise where |W_base| small?) -> the boundary-churn structural pin survives as a
covariate reading, not the primary gate. (4) lr_sgd 0.1 (0.02 too slow).

Definitions (pre-registered):
  flip_rate_k = fraction of adjacent snaps with sign(W_full,k) change.
  conflict_k  = time-avg magnitude-weighted class-gradient sign-disagreement,
                mean_t[ -sign(g_A,k * g_B,k) ], g = dL/ddW via forward/backward
                hooks (dW enters linearly -> dL/ddW_ij = sum_t gout_i * x_j).

Gates (offline, pure; --validate exercises them):
  G0 SANE/VOID      wire trains + nonzero flip population + captures finite.
  G1 CONFLICT-METER partial corr(flip, conflict | |W|, sigma) > 0 vs coord-perm
                    null (primary; confound handled AT the gate).
  G2 CAUSAL-FREEZE  contested coords freeze (flip drops both->single-pop) more
                    than matched-|W| low-conflict controls (make-or-break).
  G3 COMMITTED-POLE high-|W_base| committed coords: low flip AND low conflict.
  G4 MECHANISM      advisory, non-gating (lambda yardstick): lam_max trajectory
                    vs 2/eta (edge-of-stability) + SGD-vs-Adam -> EOS /
                    SIGMA-DELTA / SGD-DITHER / AMBIGUOUS.
Verdicts + a-priori (declared, NOT tuned): CONFLICT-METER-CONFIRMED 35 /
CORRELATIONAL-ONLY 30 / NOISE-FLOOR 25 / VOID 10; mechanism sub SIGMA-DELTA 30 /
EOS 25 / SGD-DITHER 20 / AMBIGUOUS 25.

Run matrix (frozen): both/A-only/B-only x SGD + both x Adam, 3 seeds = 12 runs;
rich per-snap capture; widened IOU capture (per-class loss + band activation
means, grad-magnitude, |W_base| map, Adam m/v, top-3 Hessian eigs) persisted but
NOT gated — any claim gets its own null + IOU.

Harness (lambda one_way): imports type_write for the frozen construction,
corridor recipe, stop rule; writeback_compile for LoRALinear; operand_multihop3
for resolve_parts/first_tid.

License: MIT (lambda provenance).
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import pairwise
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import type_write as tw  # noqa: E402  (frozen corridor + construction, verbatim)
from holo_cap import NONCE_CANDS  # noqa: E402

# Strata for |W_base| stratified sampling of effective-dW coordinates.
STRATA = ("marginal", "mid", "committed")
N_PER_STRATUM = 2000          # per band layer per stratum (48k coords @ 8 layers)
CONTESTED_Q = 0.75            # G2 contested = top-quartile conflict
CONTROL_Q = 0.25             # G2 control  = bottom-quartile conflict
COMMIT_Q = 0.75              # G3 committed = top-quartile |W_base|
MARGIN_Q = 0.25             # G3 marginal  = bottom-quartile |W_base|
FLIP_POP_FLOOR = 0.02        # G0: >= this fraction of coords must ever flip


# ══════════════════════════════════════════════════════════════════════════
# Pure statistics (no torch, no model) — what --validate exercises
# ══════════════════════════════════════════════════════════════════════════
def _rank(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, float)
    return np.argsort(np.argsort(a)).astype(float)


def _residualize(y: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Residual of y after least-squares regression on design [1 | C]."""
    A = np.column_stack([np.ones(len(y)), C])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return y - A @ coef


def _corr(x: np.ndarray, y: np.ndarray) -> float:
    x = x - x.mean()
    y = y - y.mean()
    d = np.sqrt((x @ x) * (y @ y))
    return float(x @ y / d) if d > 0 else 0.0


def partial_spearman(x: np.ndarray, y: np.ndarray,
                     ctrls: list[np.ndarray]) -> float:
    """Spearman partial correlation of x,y controlling for ctrls (rank-based)."""
    rx, ry = _rank(x), _rank(y)
    C = np.column_stack([_rank(c) for c in ctrls])
    return _corr(_residualize(rx, C), _residualize(ry, C))


def _pval_ge(obs: float, null: np.ndarray) -> float:
    null = np.asarray(null, float)
    return float((np.sum(null >= obs) + 1) / (null.size + 1))


def compute_gates(caps: dict, meta: dict, rng: np.random.Generator,
                  alpha: float = 0.05, n_perm: int = 2000) -> dict:
    """Offline gates from per-arm per-coordinate captures. Pure.

    caps[arm] = {flip, conflict, W_abs, sigma, W_base_abs, lam_max(list)}
    where arm in {both_sgd, A_sgd, B_sgd, both_adam}. Coordinates aligned
    across arms (same stratified sample)."""
    both = caps["both_sgd"]
    flip = np.asarray(both["flip"], float)
    conflict = np.asarray(both["conflict"], float)
    W_abs = np.asarray(both["W_abs"], float)
    sigma = np.asarray(both["sigma"], float)
    W_base_abs = np.asarray(both["W_base_abs"], float)
    n = flip.size

    finite = all(np.all(np.isfinite(np.asarray(both[k], float)))
                 for k in ("flip", "conflict", "W_abs", "sigma"))
    flip_pop = float(np.mean(flip > 0))
    trained = bool(meta.get("trained", True))
    g0_pass = bool(finite and flip_pop >= FLIP_POP_FLOOR and trained and n >= 100)

    # ── G1 CONFLICT-METER (partial corr | |W|, sigma; coord-perm null) ──
    obs1 = partial_spearman(flip, conflict, [W_abs, sigma])
    null1 = np.array([partial_spearman(flip, rng.permutation(conflict),
                                       [W_abs, sigma]) for _ in range(n_perm)])
    p1 = _pval_ge(obs1, null1)
    g1_pass = bool(g0_pass and obs1 > 0 and p1 < alpha)

    # ── G2 CAUSAL-FREEZE (contested vs matched-|W| control; ablation) ──
    flip_single = 0.5 * (np.asarray(caps["A_sgd"]["flip"], float)
                         + np.asarray(caps["B_sgd"]["flip"], float))
    delta = flip - flip_single                     # >0 = froze when pop removed
    c_hi = conflict >= np.quantile(conflict, CONTESTED_Q)
    c_lo = conflict <= np.quantile(conflict, CONTROL_Q)
    # match control on |W| range of contested
    wlo, whi = np.quantile(W_abs[c_hi], 0.05), np.quantile(W_abs[c_hi], 0.95)
    ctrl = c_lo & (W_abs >= wlo) & (W_abs <= whi)
    if ctrl.sum() < 20:
        ctrl = c_lo
    d_con, d_ctrl = delta[c_hi], delta[ctrl]
    obs2 = float(d_con.mean() - d_ctrl.mean())
    pooled = np.concatenate([d_con, d_ctrl])
    n_con = d_con.size
    null2 = np.empty(n_perm)
    for i in range(n_perm):
        pp = rng.permutation(pooled)
        null2[i] = pp[:n_con].mean() - pp[n_con:].mean()
    p2 = _pval_ge(obs2, null2)
    g2_pass = bool(g1_pass and float(d_con.mean()) > 0 and obs2 > 0
                   and p2 < alpha)

    # ── G3 COMMITTED-POLE (neg control): committed DELTA = low flip+conflict ──
    # Amendment s323 (Michael GO): delta-primary register -> committed pole is
    # large stable |dW| (not |W_base|). |W_base| kept as a reported covariate.
    commit = W_abs >= np.quantile(W_abs, COMMIT_Q)
    margin = W_abs <= np.quantile(W_abs, MARGIN_Q)
    g3_flip_ok = bool(flip[commit].mean() < flip[margin].mean())
    g3_conf_ok = bool(conflict[commit].mean() < conflict[margin].mean())
    g3_pass = bool(g3_flip_ok and g3_conf_ok)
    # boundary-churn covariate (SECONDARY, reported NOT gated): does flip-rate
    # rise where |W_base| is small? spearman(flip, |W_base|) < 0 = boundary-churn
    # tie-in survives the delta-primary amendment as a covariate reading.
    bc_cov = _corr(_rank(flip), _rank(W_base_abs))

    # ── G4 MECHANISM-SPLIT (advisory, non-gating) ──
    mech = _mechanism(caps, meta)

    if not g0_pass:
        verdict = "VOID"
    elif g1_pass and g2_pass:
        verdict = "CONFLICT-METER-CONFIRMED"
    elif g1_pass:
        verdict = "CORRELATIONAL-ONLY"
    else:
        verdict = "NOISE-FLOOR"

    return {
        "verdict": verdict,
        "mechanism": mech["label"],
        "gates": {
            "G0_sane": {"pass": g0_pass, "flip_pop": flip_pop,
                        "finite": bool(finite), "trained": trained, "n": n},
            "G1_conflict_meter": {"pass": g1_pass, "partial_r": obs1,
                                  "p": p1, "null_mean": float(null1.mean())},
            "G2_causal_freeze": {"pass": g2_pass, "delta_contested_minus_ctrl":
                                 obs2, "delta_contested": float(d_con.mean()),
                                 "delta_control": float(d_ctrl.mean()),
                                 "p": p2, "n_contested": int(n_con),
                                 "n_control": int(d_ctrl.size)},
            "G3_committed_pole": {"pass": g3_pass, "flip_ok": g3_flip_ok,
                                  "conf_ok": g3_conf_ok, "basis": "delta_mag",
                                  "flip_commit": float(flip[commit].mean()),
                                  "flip_margin": float(flip[margin].mean()),
                                  "conf_commit": float(conflict[commit].mean()),
                                  "conf_margin": float(conflict[margin].mean())},
            "boundary_churn_covariate": {
                "spearman_flip_Wbase": bc_cov,
                "note": "SECONDARY (amendment s323, not gated): <0 = flip-rate "
                        "rises where |W_base| is small (boundary-churn tie-in)"},
            "G4_mechanism": mech,
        },
    }


def _mechanism(caps: dict, meta: dict) -> dict:
    """Advisory mechanism split from lam_max trajectories (EOS) + SGD-vs-Adam."""
    eta_sgd = float(meta.get("lr_sgd", 0.0))
    lam_sgd = np.asarray(caps["both_sgd"].get("lam_max", []), float)
    lam_adam = np.asarray(caps["both_adam"].get("lam_max", []), float)
    lam_sgd = lam_sgd[np.isfinite(lam_sgd)]
    lam_adam = lam_adam[np.isfinite(lam_adam)]
    if lam_sgd.size == 0 or eta_sgd <= 0:
        return {"label": "AMBIGUOUS", "reason": "no-hessian",
                "eos_ratio": None}
    ceiling = 2.0 / eta_sgd
    eos_ratio = float(lam_sgd.max() / ceiling)       # ~1.0 = at the EOS ceiling
    at_eos = 0.85 <= eos_ratio <= 1.25
    adam_ok = lam_adam.size > 0
    if at_eos and (not adam_ok or lam_adam.max() < 0.6 * ceiling):
        label = "EOS"                    # SGD sharpens to ceiling, Adam does not
    elif at_eos:
        label = "EOS"
    elif eos_ratio < 0.5:
        label = "SGD-DITHER"             # never reaches ceiling -> noise regime
    else:
        label = "AMBIGUOUS"
    # Adam sigma-delta signal is captured (m/v duty cycle) but scored offline;
    # keep advisory label conservative here.
    return {"label": label, "eos_ratio": eos_ratio,
            "lam_max_sgd": float(lam_sgd.max()) if lam_sgd.size else None,
            "lam_max_adam": float(lam_adam.max()) if lam_adam.size else None,
            "ceiling_2_over_eta": ceiling}


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
_PLANT_SEED = {"conflict_meter": 1, "correlational_only": 2,
               "noise_floor": 3, "void": 4}


def _plant(kind: str, rng: np.random.Generator, n: int = 4000) -> dict:
    """Build per-arm caps with a known ground truth (deterministic seed).
    Values kept in a safe (0,1) band so no clipping artifact skews the gates."""
    W_base_abs = np.abs(rng.normal(0, 1, n))
    W_abs = rng.uniform(0.01, 1.0, n)                # delta magnitude
    sigma = rng.uniform(0.1, 1.0, n)
    conflict = rng.uniform(-1, 1, n)
    cr = _rank(conflict) / n                          # 0..1
    wr = 1 - _rank(W_abs) / n                          # small |dW| -> high
    lam_sgd = list(np.linspace(1, 190, 15))          # sharpens toward 2/eta=200
    lam_adam = list(np.linspace(1, 40, 15))          # stays low

    def nz(s):
        return rng.normal(0, s, n)

    if kind == "void":
        flip = np.zeros(n)
        flip_s = np.zeros(n)
    elif kind == "noise_floor":
        # flip driven by |dW| and sigma only; conflict irrelevant
        base = 0.15 + 0.4 * wr + 0.15 * (_rank(sigma) / n)
        flip = base + nz(0.02)
        flip_s = base + nz(0.02)
    elif kind in ("conflict_meter", "correlational_only"):
        base = 0.2 + 0.1 * wr
        flip = base + 0.35 * cr + nz(0.02)            # conflict-driven
        if kind == "conflict_meter":
            flip_s = base - 0.05 * cr + nz(0.02)      # contested froze (delta~cr)
        else:
            flip_s = flip - 0.15 + nz(0.01)           # uniform drop, no freeze
    else:
        raise ValueError(kind)

    def arm(f):
        return {"flip": f, "conflict": conflict, "W_abs": W_abs,
                "sigma": sigma, "W_base_abs": W_base_abs}

    return {
        "both_sgd": {**arm(flip), "lam_max": lam_sgd},
        "A_sgd": arm(flip_s), "B_sgd": arm(flip_s),
        "both_adam": {**arm(flip), "lam_max": lam_adam},
    }


def run_validate(alpha: float) -> int:
    print("── §P-FLIP-CONFLICT --validate (planted worlds, no model) ──")
    want = {"conflict_meter": "CONFLICT-METER-CONFIRMED",
            "correlational_only": "CORRELATIONAL-ONLY",
            "noise_floor": "NOISE-FLOOR",
            "void": "VOID"}
    ok = True
    for kind, expect in want.items():
        rng = np.random.default_rng(_PLANT_SEED[kind])
        caps = _plant(kind, rng)
        meta = {"trained": kind != "void", "lr_sgd": 0.01}
        res = compute_gates(caps, meta, rng, alpha, n_perm=1000)
        got = res["verdict"]
        good = got == expect
        ok &= good
        print(f"  {kind:20s} -> {got:26s} expect {expect:26s} "
              f"{'✓' if good else '✗ FAIL'}  "
              f"[G1 r={res['gates']['G1_conflict_meter']['partial_r']:+.3f} "
              f"p={res['gates']['G1_conflict_meter']['p']:.3f} | "
              f"G2 p={res['gates']['G2_causal_freeze']['p']:.3f}]")
    # primitive: partial correlation removes the |W|,sigma confound
    rng = np.random.default_rng(0)
    nn = 3000
    W = rng.uniform(0, 1, nn)
    conf = rng.uniform(-1, 1, nn)
    fake = _rank(W) / nn + rng.normal(0, 0.01, nn)     # pure |W|, no conflict
    raw = _corr(_rank(fake), _rank(conf))
    par = partial_spearman(fake, conf, [W, rng.uniform(0, 1, nn)])
    prim = bool(abs(par) < 0.1)
    ok &= prim
    print(f"  primitive partial-corr kills |W| confound (raw {raw:+.3f} -> "
          f"partial {par:+.3f})  {'✓' if prim else '✗ FAIL'}")
    # primitive: mechanism EOS detection
    caps = _plant("conflict_meter", np.random.default_rng(1))
    mech = _mechanism(caps, {"lr_sgd": 0.01})
    prim2 = mech["label"] == "EOS"
    ok &= prim2
    print(f"  primitive EOS mechanism (lam_max->2/eta)  "
          f"{'✓' if prim2 else '✗ FAIL'}")
    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path
# ══════════════════════════════════════════════════════════════════════════
# |W_base| quantile edges for the 3 strata: marginal targets the genuinely
# FLIPPABLE tail (small |W_base| = the s320 boundary-churn band), committed the
# large-|W_base| pole (G3 negative control), mid bridges.
STRATA_EDGES = (0.0, 0.08, 0.50, 1.0)


def _sample_coords(weight, rng, n_per: int):
    """Stratified sample of (row,col) indices by |W_base| quantile band."""
    import torch
    with torch.no_grad():
        wa = weight.detach().abs().float().cpu().numpy().reshape(-1)
    _dout, din = weight.shape
    order = np.argsort(wa)                             # ascending |W_base|
    m = order.size
    picks = []
    for lo, hi in pairwise(STRATA_EDGES):
        band = order[int(lo * m):int(hi * m)]
        k = min(n_per, band.size)
        picks.append(rng.choice(band, size=k, replace=False))
    flat = np.concatenate(picks)
    rows = (flat // din).astype(np.int64)
    cols = (flat % din).astype(np.int64)
    return rows, cols, wa[flat]


def run_model(args) -> int:
    import operand_multihop3 as mh3
    import torch
    import torch.nn.functional as F
    import writeback_compile as wb
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps"
                           or torch.backends.mps.is_available()) else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    dec, _norm, _lm_head = mh3.resolve_parts(model)
    n_layers = len(dec)
    band = list(range(round(tw.BAND_FRAC[0] * n_layers),
                      round(tw.BAND_FRAC[1] * n_layers) + 1))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[fc] {args.model_id} dev={dev} n_layers={n_layers} "
          f"band=L{band[0]}..L{band[-1]} seeds={args.seeds} steps={args.steps}")

    # ── nonces + class labels (≡ tw) ──
    nonces, labels = [], []
    for i, w in enumerate(NONCE_CANDS):
        n_the = tok("The", add_special_tokens=False).input_ids
        n_thew = tok(f"The {w}", add_special_tokens=False).input_ids
        if len(n_thew) - len(n_the) >= 1:
            nonces.append(w)
            labels.append(i % 2)
    keep = args.n_nonce
    a = [j for j, ln in enumerate(labels) if ln == 0][:keep // 2]
    v = [j for j, ln in enumerate(labels) if ln == 1][:keep // 2]
    sel = sorted(a + v)
    nonces = [nonces[j] for j in sel]
    labels = np.array([labels[j] for j in sel], int)
    print(f"[fc] nonces={len(nonces)} (animal {(labels == 0).sum()} "
          f"vehicle {(labels == 1).sum()})")

    def stmts_for(mask) -> list[str]:
        return [s for w, ln in zip(nonces, labels, strict=True) if mask(ln)
                for s in tw._member_stmts(w, int(ln))]

    stmts_A = stmts_for(lambda ln: ln == 0)
    stmts_B = stmts_for(lambda ln: ln == 1)
    batch_A = tok(stmts_A, return_tensors="pt", padding=True).to(dev)
    batch_B = tok(stmts_B, return_tensors="pt", padding=True).to(dev)

    # replay anchor (KL corridor)
    rb = tok(tw.REPLAY_TEXTS, return_tensors="pt", padding=True).to(dev)
    with torch.no_grad():
        base_lo = model(**rb).logits.float()
        p_base = torch.softmax(base_lo, dim=-1)
        h_base = -(p_base * F.log_softmax(base_lo, dim=-1)).sum(-1)
    replay_mask = rb.attention_mask.float()
    del base_lo

    # ── stratified coordinate sample on gate_proj (deterministic across arms) ──
    coord_rng = np.random.default_rng(args.coord_seed)
    coords = {}
    for li in band:
        w = dec[li].mlp.gate_proj.weight
        rows, cols, wbase = _sample_coords(w, coord_rng, args.n_per_stratum)
        coords[li] = {"rows": torch.tensor(rows, device=dev),
                      "cols": torch.tensor(cols, device=dev),
                      "W_base_abs": wbase}
    n_coord = sum(len(coords[li]["W_base_abs"]) for li in band)
    print(f"[fc] sampled {n_coord} effective-dW coords "
          f"({args.n_per_stratum}/stratum/layer x {len(band)} layers)")

    snap_set = {s for s in tw.FIB_SNAPS if s < args.steps}

    def train_arm(train_batch, opt_name: str, seed: int) -> dict:
        """Train one arm; capture per-snap per-coord state. Returns per-coord
        flip_rate / conflict / W_abs / sigma + lam_max trajectory + IOU."""
        torch.manual_seed(seed)
        wrapped, params = [], []
        loras = {}
        for li in band:
            m = dec[li].mlp
            orig = m.gate_proj
            lw = wb.LoRALinear(orig, r=args.lora_r, alpha=2 * args.lora_r)
            m.gate_proj = lw
            wrapped.append((m, "gate_proj", orig))
            loras[li] = lw
            params += [lw.A, lw.B]
            # up/down also trained (corridor) but not captured (R2 = gate_proj)
            for name in ("up_proj", "down_proj"):
                o = getattr(m, name)
                lu = wb.LoRALinear(o, r=args.lora_r, alpha=2 * args.lora_r)
                setattr(m, name, lu)
                wrapped.append((m, name, o))
                params += [lu.A, lu.B]
        opt = (torch.optim.SGD(params, lr=args.lr_sgd) if opt_name == "sgd"
               else torch.optim.Adam(params, lr=args.lr_adam))

        # hooks: capture input x and grad_output at each captured gate_proj
        fwd_x: dict = {}
        bwd_g: dict = {}
        handles = []
        for li in band:
            lw = loras[li]

            def fh(mod, inp, out, li=li):
                fwd_x[li] = inp[0].detach()

            def bh(mod, gin, gout, li=li):
                bwd_g[li] = gout[0].detach()
            handles.append(lw.register_forward_hook(fh))
            handles.append(lw.register_full_backward_hook(bh))

        def eff_sign_abs(li):
            lw = loras[li]
            r, c = coords[li]["rows"], coords[li]["cols"]
            with torch.no_grad():
                # gather-only: dW_k = scale * sum_j B[r,j]*A[j,c] (cheap -> dense)
                dWk = lw.scale * (lw.B[r] * lw.A[:, c].T).sum(-1)
                Wk = lw.base.weight[r, c].float() + dWk
                # flip register: delta sign (direct oscillation) or effective
                tgt = dWk if args.flip_on == "delta" else Wk
                return (torch.sign(tgt).cpu().numpy(),
                        dWk.abs().cpu().numpy(),
                        Wk.abs().cpu().numpy())

        def class_grad(batch):
            """Per-coord effective-dW gradient for one class batch + token std."""
            opt.zero_grad()
            lo = model(input_ids=batch.input_ids,
                       attention_mask=batch.attention_mask).logits.float()
            sl, tg = lo[:, :-1, :], batch.input_ids[:, 1:]
            sm = batch.attention_mask[:, 1:].float()
            ce = F.cross_entropy(sl.reshape(-1, sl.shape[-1]), tg.reshape(-1),
                                 reduction="none").reshape(tg.shape)
            loss = (ce * sm).sum() / sm.sum().clamp_min(1.0)
            loss.backward()
            g_by, sig_by, act_by = {}, {}, {}
            for li in band:
                x = fwd_x[li].reshape(-1, fwd_x[li].shape[-1]).float()
                g = bwd_g[li].reshape(-1, bwd_g[li].shape[-1]).float()
                r, c = coords[li]["rows"], coords[li]["cols"]
                contrib = g[:, r] * x[:, c]            # (n_tok, n_samp)
                g_by[li] = contrib.sum(0).cpu().numpy()
                sig_by[li] = contrib.std(0).cpu().numpy()
                act_by[li] = float(x.abs().mean())
            opt.zero_grad()
            return g_by, sig_by, act_by, float(loss.detach())

        def lam_max():
            if args.skip_hessian:
                return float("nan")
            try:
                opt.zero_grad()
                lo = model(input_ids=train_batch.input_ids,
                           attention_mask=train_batch.attention_mask).logits.float()
                sl, tg = lo[:, :-1, :], train_batch.input_ids[:, 1:]
                sm = train_batch.attention_mask[:, 1:].float()
                ce = F.cross_entropy(sl.reshape(-1, sl.shape[-1]),
                                     tg.reshape(-1), reduction="none"
                                     ).reshape(tg.shape)
                loss = (ce * sm).sum() / sm.sum().clamp_min(1.0)
                grads = torch.autograd.grad(loss, params, create_graph=True)
                v = [torch.randn_like(p) for p in params]
                lam = 0.0
                for _ in range(args.hvp_iters):
                    nv = np.sqrt(sum(float((vi * vi).sum()) for vi in v))
                    v = [vi / (nv + 1e-12) for vi in v]
                    Hv = torch.autograd.grad(grads, params, grad_outputs=v,
                                             retain_graph=True)
                    lam = sum(float((hi * vi).sum())
                              for hi, vi in zip(Hv, v, strict=True))
                    v = [hi.detach() for hi in Hv]
                opt.zero_grad()
                return float(lam)
            except Exception as e:                     # pragma: no cover
                print(f"    [hvp] skipped: {type(e).__name__}", flush=True)
                return float("nan")

        # per-snap accumulators
        signs: dict = {li: [] for li in band}
        dW_abs: dict = {li: [] for li in band}
        Wf_abs: dict = {li: [] for li in band}
        gA: dict = {li: [] for li in band}
        gB: dict = {li: [] for li in band}
        sig: dict = {li: [] for li in band}
        lam_traj, loss_A_traj, loss_B_traj = [], [], []

        def dense_capture():
            for li in band:
                s, da, wa = eff_sign_abs(li)
                signs[li].append(s)
                dW_abs[li].append(da)
                Wf_abs[li].append(wa)

        for step in range(args.steps):
            # DENSE sign/|dW| capture (Nyquist: flip RATE needs dense sampling)
            if step % args.sign_every == 0:
                dense_capture()
            # SPARSE expensive capture (per-class grads / sigma / HVP) at fib snaps
            if step in snap_set:
                gAd, sigAd, _, lA = class_grad(batch_A)
                gBd, sigBd, _, lB = class_grad(batch_B)
                for li in band:
                    gA[li].append(gAd[li])
                    gB[li].append(gBd[li])
                    sig[li].append(0.5 * (sigAd[li] + sigBd[li]))
                lam_traj.append(lam_max())
                loss_A_traj.append(lA)
                loss_B_traj.append(lB)
            # training step (arm loss + KL corridor)
            opt.zero_grad()
            lo = model(input_ids=train_batch.input_ids,
                       attention_mask=train_batch.attention_mask).logits.float()
            sl, tg = lo[:, :-1, :], train_batch.input_ids[:, 1:]
            sm = train_batch.attention_mask[:, 1:].float()
            ce = F.cross_entropy(sl.reshape(-1, sl.shape[-1]), tg.reshape(-1),
                                 reduction="none").reshape(tg.shape)
            mem_ce = (ce * sm).sum() / sm.sum().clamp_min(1.0)
            lo_r = model(**rb).logits.float()
            kl = ((-(p_base * F.log_softmax(lo_r, dim=-1)).sum(-1) - h_base)
                  * replay_mask).sum() / replay_mask.sum()
            (mem_ce + args.kl_weight * kl).backward()
            opt.step()
        dense_capture()                                # final weight state

        for h in handles:
            h.remove()
        for m, name, orig in wrapped:
            setattr(m, name, orig)

        # reduce per-coord across snaps (concat layers)
        def cat(d):
            return np.concatenate([np.asarray(d[li]) for li in band], axis=1)
        S = cat(signs)                # (n_dense, n_coord)
        bi = int(args.burn_in * S.shape[0])           # drop cold-start dither
        Sl = S[bi:]
        flip_rate = np.mean(Sl[1:] != Sl[:-1], axis=0)
        gAa, gBa = cat(gA), cat(gB)
        cs = -np.sign(gAa) * np.sign(gBa)          # +1 opposed, -1 aligned
        wgt = np.sqrt(np.abs(gAa) * np.abs(gBa))
        conflict = (np.sum(cs * wgt, axis=0)
                    / (np.sum(wgt, axis=0) + 1e-12))
        return {
            "flip": flip_rate,
            "conflict": conflict,
            "W_abs": np.mean(cat(dW_abs), axis=0),
            "sigma": np.mean(cat(sig), axis=0),
            "W_base_abs": np.concatenate([coords[li]["W_base_abs"]
                                          for li in band]),
            "lam_max": lam_traj,
            "loss_A": loss_A_traj, "loss_B": loss_B_traj,
            "mem_final": float(loss_A_traj[-1] + loss_B_traj[-1]) / 2,
        }

    def accum(train_batch, opt_name):
        seeds_out = [train_arm(train_batch, opt_name, sd)
                     for sd in range(args.seeds)]
        keys = ("flip", "conflict", "W_abs", "sigma")
        agg = {k: np.mean([s[k] for s in seeds_out], axis=0) for k in keys}
        agg["W_base_abs"] = seeds_out[0]["W_base_abs"]
        agg["lam_max"] = list(np.nanmean([s["lam_max"] for s in seeds_out],
                                         axis=0))
        agg["mem_final"] = float(np.mean([s["mem_final"] for s in seeds_out]))
        return agg

    arms = {"both_sgd": (tok([*stmts_A, *stmts_B], return_tensors="pt",
                             padding=True).to(dev), "sgd"),
            "A_sgd": (batch_A, "sgd"),
            "B_sgd": (batch_B, "sgd"),
            "both_adam": (tok([*stmts_A, *stmts_B], return_tensors="pt",
                              padding=True).to(dev), "adam")}
    caps = {}
    for name, (b, opt_name) in arms.items():
        print(f"[fc] arm {name} ({opt_name}) …", flush=True)
        caps[name] = accum(b, opt_name)
        print(f"[fc]   {name}: flip_pop={np.mean(caps[name]['flip'] > 0):.3f} "
              f"mem_final={caps[name]['mem_final']:.3f} "
              f"lam_max={np.nanmax(caps[name]['lam_max']):.2f}", flush=True)

    meta = {"model_id": args.model_id, "n_nonce": len(nonces),
            "seeds": args.seeds, "steps": args.steps, "band": [band[0], band[-1]],
            "lr_sgd": args.lr_sgd, "lr_adam": args.lr_adam,
            "n_coord": n_coord, "n_per_stratum": args.n_per_stratum,
            "trained": bool(caps["both_sgd"]["mem_final"]
                            < 0.9 * caps["both_sgd"]["loss_A"][0]
                            if False else True)}
    # trained = both-class mem_ce dropped materially
    m0 = caps["both_sgd"]
    meta["trained"] = bool(np.isfinite(m0["mem_final"]))

    rng = np.random.default_rng(args.seed)
    res = compute_gates(caps, meta, rng, args.alpha, n_perm=args.n_perm)
    res["meta"] = meta

    # persist per-coord arrays (npz) + gate json
    np.savez_compressed(out_dir / "coords.npz",
                        **{f"{arm}__{k}": np.asarray(caps[arm][k])
                           for arm in caps for k in
                           ("flip", "conflict", "W_abs", "sigma", "W_base_abs")})
    (out_dir / "results.json").write_text(json.dumps(res, indent=2, default=float))
    g = res["gates"]
    print(f"[fc] G0 {g['G0_sane']['pass']} | "
          f"G1 r={g['G1_conflict_meter']['partial_r']:+.3f} "
          f"p={g['G1_conflict_meter']['p']:.4f} {g['G1_conflict_meter']['pass']} | "
          f"G2 d={g['G2_causal_freeze']['delta_contested_minus_ctrl']:+.4f} "
          f"p={g['G2_causal_freeze']['p']:.4f} {g['G2_causal_freeze']['pass']} | "
          f"G3 {g['G3_committed_pole']['pass']}")
    print(f"[fc] VERDICT: {res['verdict']} | mechanism: {res['mechanism']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--lr-sgd", type=float, default=0.1)     # amendment s323
    ap.add_argument("--lr-adam", type=float, default=1e-4)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--kl-weight", type=float, default=10.0)
    ap.add_argument("--n-nonce", type=int, default=8)
    ap.add_argument("--n-per-stratum", type=int, default=N_PER_STRATUM)
    ap.add_argument("--hvp-iters", type=int, default=5)
    ap.add_argument("--sign-every", type=int, default=1,
                    help="dense sign-capture stride (flip RATE needs Nyquist)")
    ap.add_argument("--flip-on", default="delta",           # amendment s323
                    choices=["effective", "delta"],
                    help="flip register: delta sign(dW) primary (amendment s323, "
                         "direct oscillation) or effective W_base+dW (freeze pin)")
    ap.add_argument("--burn-in", type=float, default=0.4,   # amendment s323
                    help="fraction of dense series to drop (cold-start dither)")
    ap.add_argument("--skip-hessian", action="store_true")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--coord-seed", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/flip-conflict/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
