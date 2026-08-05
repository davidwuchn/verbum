#!/usr/bin/env python3
"""§SIGN-COMMITMENT-CURVE — image GD's two jobs at two timescales.

Pre-reg: mementum/knowledge/explore/the-verbum-machine.md §M8 SIGN-COMMITMENT-
CURVE (FROZEN s309, Michael-approved). The cheapest probe on the whole board.

Question. In gd_cd wire training (s303 — the wire that ternarizes near-
losslessly, s304/s308 retention ~1.0), does GD commit the ROUTING register
(trit *signs*) EARLIER than it polishes the VALUE register (per-column
*magnitudes*)? I.e. are GD's two jobs separable in TIME?

Instrument. Reuses the gd_cd recipe verbatim from `writeback_compile` (imported
as a module — the frozen s303 generator is UNTOUCHED): LoRA r=16, FFN band
L22–L29 (0.6–0.8 depth, Qwen3-4B), lr 1e-4, 500 steps, KL to the frozen host on
its own committed CoT (TEACHER_PROMPT), 3 seeds; train_cells from the frozen
gate0.json (no re-sweep). Some ~20 lines of the gd_cd loop are re-expressed here
(Michael-approved duplication) because this instrument adds the per-step TWN
observation the frozen generator deliberately omits; the RECIPE constants
(band, LoRALinear, r, lr, prompts) are imported so the two cannot drift on the
science-bearing numerics.

At each t in the FIXED fibonacci schedule L (dense early — where the action is
predicted; frozen a priori, λ yardstick), for every wrapped FFN matrix form
Δ_t = scale·B_tA_t, TWN-project (`ternarize_twn`, reused, thr 0.7): trit state
τ_t = sign·mask ∈ {−1,0,+1} (routing register), per-column γ_t and continuous
|Δ_t| (value register). Because the full trit history is ~9 GB, a fixed seeded
subsample of N_TRACK coords per matrix is tracked across time (an unbiased
estimator of the pooled commit-step distribution; subsample seed frozen).

Metrics (pooled over tracked trits, all band layers × seeds). Sign-stability
S(t)=mean[τ_t==τ_T]; per-trit commit-step c_i = last t with τ_t≠τ_T (fraction
of T; median/IQR/p90); value convergence M(t)=magnitude-cosine(|Δ_t|,|Δ_T|);
flip-rate f(t)=mean[τ_t≠τ_prev]; half-lives t*_sign(θ), t*_mag(θ) (θ=0.9).

Nulls (λ yardstick). N1 TIME-SHUFFLE: permute the intermediate trit snapshots in
time, keep the real final; recompute commit-steps → measured median must beat it
(bootstrap, one-sided p<0.05). N2 (paired within-run): t*_mag>t*_sign, bootstrap
ratio-CI over resampled trits excludes 1.0.

Gates (frozen). G1 SIGN-EARLY: median commit ≤ 0.25·T ∧ S(0.25·T) ≥ 0.90.
G2 TWO-TIMESCALE: t*_mag/t*_sign ≥ 2.0 ∧ bootstrap ratio-CI excludes 1.0.
G3 NULL-BEATS: median-commit earlier than N1 (p<0.05). G4 (advisory) FINAL-
WIRE-SANE: final mag_cos ∈ [0.80,0.95] ∧ sparsity in the s304 band (reported,
never gates).

Verdicts: TWO-TIMESCALE(+SIGN-EARLY) / SIGN-EARLY-ONLY / SINGLE-TIMESCALE /
SIGN-CHURN (falsifier) / MAG-EARLY (surprise).

Cadence: --validate (no model) → smoke (--n-cells/--steps small) → Michael GO →
full run (tmux main:1) → frozen scoring.

License: MIT (`λ provenance`).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_WRAP = _HERE.parents[1] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

import ternarize_delta as td  # noqa: E402  (ternarize_twn, plate_stats — reuse)
import writeback_compile as wb  # noqa: E402  (recipe constants — no fork)
from holo_frag import _json_safe  # noqa: E402

# ── frozen constants (a priori) ──
STEPS_SCHED = [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 499]
THETA = 0.90                 # half-life threshold
QUARTER_FRAC = 0.25          # G1 SIGN-EARLY horizon (fraction of T)
RATIO_MIN = 2.0              # G2 two-timescale ratio floor
FLIP_CHURN = 0.02            # last-interval flip rate above this = not settled
N_TRACK = 20000              # tracked trits per matrix (subsample estimator)
SUBSAMPLE_SEED = 0           # frozen: aligns tracked coords across seeds
BOOT = 10000                 # bootstrap resamples
SANE_MAGCOS = (0.80, 0.95)   # G4 final-wire mag_cos band (s304 anchor)
FFN_PROJ = ("gate_proj", "up_proj", "down_proj")


# ══════════════════════════════════════════════════════════════════════════
# Frozen scoring + verdict (PURE — --validate exercises planted worlds)
# ══════════════════════════════════════════════════════════════════════════
def _mag_cos(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(a @ b / (na * nb))


def _half_life(curve: np.ndarray, steps: np.ndarray, theta: float) -> float:
    """First step at which curve ≥ theta; T if never (curve aligned to steps)."""
    hit = np.nonzero(curve >= theta)[0]
    return float(steps[hit[0]]) if len(hit) else float(steps[-1])


def _commit_steps(tau: np.ndarray, steps: np.ndarray) -> np.ndarray:
    """tau: (n_trit, n_snap) int in {-1,0,1}. Per-trit last step (value) where
    τ_t != τ_final; 0 if already final at t=0. Returns (n_trit,) step values."""
    final = tau[:, -1:]
    differ = tau != final                       # (n_trit, n_snap)
    differ[:, -1] = False                        # never count the final snap
    idx = np.where(differ.any(axis=1),
                   (differ * np.arange(tau.shape[1])[None, :]).argmax(axis=1),
                   0)
    return steps[idx]


def _sign_stability(tau: np.ndarray) -> np.ndarray:
    """S(t) = mean over trits of [τ_t == τ_final], aligned to snapshots."""
    return (tau == tau[:, -1:]).mean(axis=0)


def _flip_rate(tau: np.ndarray) -> np.ndarray:
    """f between consecutive snaps; f[0]=0 (no predecessor)."""
    f = np.zeros(tau.shape[1])
    f[1:] = (tau[:, 1:] != tau[:, :-1]).mean(axis=0)
    return f


def _mag_curve(mag: np.ndarray) -> np.ndarray:
    """M(t) = magnitude-cosine(|Δ_t|, |Δ_T|) over tracked coords."""
    final = mag[:, -1]
    return np.array([_mag_cos(mag[:, j], final) for j in range(mag.shape[1])])


def _sign_cos_curve(tau: np.ndarray) -> np.ndarray:
    """Sc(t) = cosine(τ_t, τ_T) over tracked trits — the ROUTING-register
    convergence curve, deliberately the SAME strictness (a 0.9-cosine
    threshold) as M(t) so the G2 two-timescale ratio compares like with like.
    Exact-match S(t) stays stricter and is reserved for G1/commit-step."""
    final = tau[:, -1].astype(np.float64)
    return np.array([_mag_cos(tau[:, j].astype(np.float64), final)
                     for j in range(tau.shape[1])])


def _null_shuffle_median(tau: np.ndarray, steps: np.ndarray,
                         rng: np.random.Generator, n: int) -> np.ndarray:
    """N1: permute intermediate snapshots in time (keep real final), recompute
    median commit-step. Returns (n,) null medians."""
    n_snap = tau.shape[1]
    inter = np.arange(n_snap - 1)               # positions 0..T-1
    out = np.empty(n)
    for b in range(n):
        perm = rng.permutation(inter)
        order = np.append(perm, n_snap - 1)     # final stays last
        out[b] = np.median(_commit_steps(tau[:, order], steps))
    return out


def score_curve(tau: np.ndarray, mag: np.ndarray, steps_list: list,
                rng: np.random.Generator,
                final_magcos: float, final_sparsity: float) -> dict:
    """tau,mag: (n_trit, n_snap) aligned to steps_list. Frozen gates+verdict."""
    steps = np.asarray(steps_list, float)
    T = steps[-1]
    S = _sign_stability(tau)                            # exact-match (G1)
    Sc = _sign_cos_curve(tau)                           # cosine (G2, fair vs M)
    M = _mag_curve(mag)
    flip = _flip_rate(tau)
    commit = _commit_steps(tau, steps)                 # (n_trit,) step values
    med_commit = float(np.median(commit))
    p90_commit = float(np.percentile(commit, 90))
    iqr = (float(np.percentile(commit, 25)),
           float(np.percentile(commit, 75)))
    t_sign = _half_life(Sc, steps, THETA)              # routing half-life
    t_mag = _half_life(M, steps, THETA)                # value half-life
    ratio = t_mag / max(t_sign, 1.0)

    # S at 0.25·T (nearest scheduled step)
    q = QUARTER_FRAC * T
    qj = int(np.argmin(np.abs(steps - q)))
    s_quarter = float(S[qj])
    s_prefinal = float(S[-2])                          # S(T⁻)
    flip_last = float(flip[-1])

    # ── N2 bootstrap: ratio CI over resampled trits ──
    n_trit = tau.shape[0]
    ratios = np.empty(BOOT)
    for b in range(BOOT):
        idx = rng.integers(0, n_trit, n_trit)
        Scb = _sign_cos_curve(tau[idx])
        Mb = _mag_curve(mag[idx])
        ts = _half_life(Scb, steps, THETA)
        tm = _half_life(Mb, steps, THETA)
        ratios[b] = tm / max(ts, 1.0)
    ratio_ci = (float(np.percentile(ratios, 2.5)),
                float(np.percentile(ratios, 97.5)))

    # ── N1 time-shuffle null: median-commit ──
    null_med = _null_shuffle_median(tau, steps, rng, BOOT)
    p_null = float((null_med <= med_commit).mean())    # one-sided (earlier=lower)

    # ── frozen gates ──
    g1 = bool(med_commit <= QUARTER_FRAC * T and s_quarter >= THETA)
    g2 = bool(ratio >= RATIO_MIN and ratio_ci[0] > 1.0)
    g3 = bool(p_null < 0.05)
    g4 = bool(SANE_MAGCOS[0] <= final_magcos <= SANE_MAGCOS[1])
    stabilized = bool(s_prefinal >= THETA and flip_last <= FLIP_CHURN)

    verdict = _verdict(g1, g2, g3, stabilized, t_mag, t_sign)
    return {
        "S": S.tolist(), "Sc": Sc.tolist(), "M": M.tolist(),
        "flip": flip.tolist(), "steps": list(steps_list),
        "med_commit": med_commit, "commit_frac": med_commit / T,
        "p90_commit": p90_commit, "iqr_commit": iqr,
        "t_sign": t_sign, "t_mag": t_mag, "ratio": ratio,
        "ratio_ci": ratio_ci, "s_quarter": s_quarter, "quarter_step": float(steps[qj]),
        "s_prefinal": s_prefinal, "flip_last": flip_last,
        "p_null": p_null, "stabilized": stabilized,
        "final_magcos": final_magcos, "final_sparsity": final_sparsity,
        "gates": {"G1_sign_early": g1, "G2_two_timescale": g2,
                  "G3_null_beats": g3, "G4_wire_sane": g4},
        "verdict": verdict,
        "n_trit": int(n_trit),
    }


def _verdict(g1: bool, g2: bool, g3: bool, stabilized: bool,
             t_mag: float, t_sign: float) -> str:
    if not stabilized:
        return "SIGN-CHURN"
    if g1 and g2 and g3:
        return "TWO-TIMESCALE (+SIGN-EARLY)"
    if g1 and g3:
        return "SIGN-EARLY-ONLY"
    if t_sign / max(t_mag, 1.0) >= RATIO_MIN:   # value clearly leads routing
        return "MAG-EARLY"
    return "SINGLE-TIMESCALE"


# ══════════════════════════════════════════════════════════════════════════
# --validate (no model): planted worlds — every verdict reachable
# ══════════════════════════════════════════════════════════════════════════
def _plant(rng, n, n_snap, sign_lock, mag_lock, churn=False, hard_mag=False):
    """Build (tau, mag) with per-trit sign lock ~sign_lock (monotone: 0 until
    lock, final after) and a magnitude PROFILE that reshapes (noisy) until it
    stabilizes ~mag_lock. Magnitude-cosine is scale-invariant, so the ramp must
    perturb the DIRECTION (not just scale) to converge late. churn → signs
    never settle."""
    j = np.arange(n_snap)[None, :]
    final_sign = rng.choice([-1, 1], size=n).astype(np.int8)
    sl = np.full(n, min(sign_lock, n_snap - 1))          # deterministic step
    tau = np.where(j >= sl[:, None], final_sign[:, None], 0).astype(np.int8)
    if churn:
        tau[:, :-1] = rng.choice([-1, 0, 1], size=(n, n_snap - 1)).astype(np.int8)
    tau[:, -1] = final_sign
    final_mag = np.abs(rng.normal(size=n)).astype(np.float32) + 0.1
    ml = np.full(n, min(max(mag_lock, 1), n_snap - 1))
    if hard_mag:                                         # co-lock (hard step)
        mag = np.where(j >= ml[:, None], final_mag[:, None],
                       0.0).astype(np.float32)
    else:
        frac = np.minimum(j / ml[:, None], 1.0)
        noise = rng.normal(size=(n, n_snap)) * (1.0 - frac)
        mag = np.abs(final_mag[:, None] * frac
                     + noise * final_mag[:, None]).astype(np.float32)
    mag[:, -1] = final_mag
    return tau, mag


def run_validate() -> int:
    ok = True
    print("── §SIGN-COMMITMENT-CURVE --validate (no model) ──")
    n_snap = len(STEPS_SCHED)
    steps = np.asarray(STEPS_SCHED, float)

    # 0. commit-step / stability primitives
    tau = np.zeros((4, n_snap), dtype=np.int8)
    tau[0] = 1                                  # always final → commit 0
    tau[1, :6] = 0                              # settles at snap 6
    tau[1, 6:] = -1                             # → last diff snap 5
    tau[2] = 1                                  # final 1, all match → commit 0
    tau[3, :] = [(-1) ** j for j in range(n_snap)]  # churny
    tau[3, -1] = 1
    cs = _commit_steps(tau, steps)
    good = (cs[0] == 0 and cs[1] == STEPS_SCHED[5] and cs[2] == 0)
    print(f"[V] commit-steps: {cs.tolist()} (want [0,{STEPS_SCHED[5]},0,*]) "
          f"{'OK' if good else 'FAIL'}")
    ok &= good

    good = abs(_half_life(np.array([0.0, 0.5, 0.9, 1.0, 1.0]),
                          np.array([0, 1, 2, 3, 4.0]), 0.9) - 2.0) < 1e-9
    print(f"[V] half-life monotone {'OK' if good else 'FAIL'}")
    ok &= good

    # planted verdict worlds
    def world(name, want, **kw):
        r = np.random.default_rng(kw.pop("seed", 1))
        tau, mag = _plant(r, kw.pop("n", 4000), n_snap, **kw)
        sc = score_curve(tau, mag, STEPS_SCHED, np.random.default_rng(2),
                         final_magcos=0.88, final_sparsity=0.6)
        hit = want in sc["verdict"]
        print(f"[V] {name}: -> {sc['verdict']!r} (want {want}) "
              f"med_commit={sc['med_commit']:.0f} t_sign={sc['t_sign']:.0f} "
              f"t_mag={sc['t_mag']:.0f} ratio={sc['ratio']:.1f} "
              f"p_null={sc['p_null']:.3f} {'OK' if hit else 'FAIL'}")
        return hit

    # signs by snap 4 (step 5), magnitude by snap 12 (step 233) → two-timescale
    ok &= world("two-timescale", "TWO-TIMESCALE", sign_lock=4, mag_lock=12)
    # both early → sign early, ratio ~1 → SIGN-EARLY-ONLY
    ok &= world("sign-early-only", "SIGN-EARLY-ONLY", sign_lock=3, mag_lock=3)
    # both hard-lock together late (¬G1, ratio≈1) → SINGLE-TIMESCALE
    ok &= world("single-timescale", "SINGLE-TIMESCALE", sign_lock=12,
                mag_lock=12, hard_mag=True)
    # churn: signs never settle → SIGN-CHURN
    ok &= world("sign-churn", "SIGN-CHURN", sign_lock=4, mag_lock=6, churn=True)
    # mag locks snap 2 but signs late snap 12 (¬G1) → MAG-EARLY
    ok &= world("mag-early", "MAG-EARLY", sign_lock=12, mag_lock=2)

    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path — minimal gd_cd training with per-step TWN logging
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import operand_multihop3 as mh3
    import torch
    import torch.nn.functional as F
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps"
                           or torch.backends.mps.is_available()) else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    dec, _norm, _lm = mh3.resolve_parts(model)
    n_layers = len(dec)
    band = list(range(round(wb.BAND[0] * n_layers),
                      round(wb.BAND[1] * n_layers) + 1))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── train_cells from frozen gate0.json (no re-sweep) ──
    g0 = json.loads(Path(args.gate0).read_text())
    valid_train = [r for r in g0["cells"]
                   if r["split"] == "TRAIN" and r.get("g_ok")
                   and r.get("h_ok") and r.get("cot_ok")]
    if args.n_cells:
        valid_train = valid_train[:args.n_cells]
    steps_sched = [s for s in STEPS_SCHED if s < args.steps] + [args.steps - 1]
    steps_sched = sorted(set(steps_sched))
    print(f"[sc] {args.model_id} dev={dev} band=L{band[0]}..L{band[-1]} "
          f"train_cells={len(valid_train)} seeds={args.seeds} steps={args.steps}")
    print(f"[sc] log schedule ({len(steps_sched)}): {steps_sched}")

    def first_tid(w: str) -> int:
        return mh3.first_tid(tok, w)

    def logits_last(prompt: str) -> np.ndarray:
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        return lo

    # teacher probs on TEACHER_PROMPT with the KNOWN country (gd_cd, verbatim)
    tp = {}
    for r in valid_train:
        lo = logits_last(wb.TEACHER_PROMPT.format(lm=r["landmark"],
                                                  c=r["country"]))
        tp[r["landmark"]] = torch.softmax(
            torch.tensor(lo, dtype=torch.float32), dim=-1)
    prompts = [wb.DIRECT_PROMPT.format(lm=r["landmark"]) for r in valid_train]
    batch = tok(prompts, return_tensors="pt", padding=True).to(dev)
    tp_stack = torch.stack([tp[r["landmark"]] for r in valid_train]).to(dev)

    # fixed subsampled coords per (layer,proj) shape — aligned across seeds
    def coords_for(shape, sub_rng):
        size = int(np.prod(shape))
        n = min(N_TRACK, size)
        return np.sort(sub_rng.choice(size, n, replace=False))

    def snapshot(wrapped, coords):
        """Per wrapped (m,name,lw,coords_key): full Δ=scale·B@A → TWN → tracked
        τ, |Δ|. Returns dict key -> (tau_track int8, mag_track f32)."""
        out = {}
        for (_m, _name, lw, key) in wrapped:
            with torch.no_grad():
                delta = (lw.scale * (lw.B @ lw.A)).float().cpu().numpy()
            _t, mask, _gamma = td.ternarize_twn(delta)
            tau = (np.sign(delta) * mask).astype(np.int8)
            flat_tau = tau.reshape(-1)[coords[key]]
            flat_mag = np.abs(delta).reshape(-1)[coords[key]].astype(np.float32)
            out[key] = (flat_tau, flat_mag)
        return out

    def final_wire_stats(wrapped):
        """G4: pooled mag_cos(float delta, ternary plate) + sparsity, full."""
        fv, tv, trits, total = [], [], 0, 0
        for (_m, _name, lw, _key) in wrapped:
            with torch.no_grad():
                delta = (lw.scale * (lw.B @ lw.A)).float().cpu().numpy()
            t, _mask, _g = td.ternarize_twn(delta)
            fv.append(delta.reshape(-1))
            tv.append(t.reshape(-1))
            trits += int((t != 0).sum())
            total += t.size
        fa = np.concatenate(fv)
        ta = np.concatenate(tv)
        return _mag_cos(fa, ta), 1.0 - trits / max(total, 1)

    def marginality(wrapped, coords):
        """NON-FROZEN: per tracked coord, final marginality r=|Δ_T|/thr_j where
        thr_j = td.TERN_THR·mean(|Δ_T|,axis=0) is its COLUMN's TWN threshold.
        r<1 ⇒ final trit is 0 (below threshold); r≈1 ⇒ marginal; r≫1 ⇒
        confident. Needs the full matrix (column means) — cannot be recomputed
        from the subsample offline, so it is captured here."""
        out = {}
        for (_m, _name, lw, key) in wrapped:
            with torch.no_grad():
                delta = (lw.scale * (lw.B @ lw.A)).float().cpu().numpy()
            absw = np.abs(delta)
            thr_j = td.TERN_THR * absw.mean(axis=0)         # (d_in,)
            d_in = delta.shape[1]
            flat = coords[key]
            r = absw.reshape(-1)[flat] / np.maximum(thr_j[flat % d_in], 1e-12)
            out[key] = r.astype(np.float32)
        return out

    # ── per-seed training with logging ──
    per_seed_tau = []       # each: dict key -> list over snaps of (N,) int8
    per_seed_mag = []
    per_seed_loss = []      # NON-FROZEN: (n_snap,) loss at each logged step
    per_seed_r = []         # NON-FROZEN: dict key -> (N,) final marginality r
    final_magcos, final_sparsity = [], []
    sub_rng = np.random.default_rng(SUBSAMPLE_SEED)
    coords = None

    for s in range(args.seeds):
        print(f"[sc] ── seed {s} ──", flush=True)
        torch.manual_seed(args.seed + s)
        wrapped, params = [], []
        for li in band:
            mlp = dec[li].mlp
            for name in FFN_PROJ:
                orig = getattr(mlp, name)
                lw = wb.LoRALinear(orig, r=args.lora_r, alpha=2 * args.lora_r)
                setattr(mlp, name, lw)
                wrapped.append((mlp, name, lw, f"L{li}.{name}"))
                params += [lw.A, lw.B]
        if coords is None:                      # fix coords once (aligned seeds)
            coords = {key: coords_for((lw.B.shape[0], lw.A.shape[1]), sub_rng)
                      for (_m, _name, lw, key) in wrapped}
        opt = torch.optim.Adam(params, lr=args.lr)
        snaps_tau = {key: [] for key in coords}
        snaps_mag = {key: [] for key in coords}
        snaps_loss = []                              # NON-FROZEN: loss @ snap
        for step in range(args.steps):
            opt.zero_grad()
            lo = model(**batch).logits[:, -1, :].float()
            loss = -(tp_stack * F.log_softmax(lo, dim=-1)).sum(-1).mean()
            loss.backward()
            opt.step()
            if step in steps_sched:
                snap = snapshot(wrapped, coords)
                for key in coords:
                    snaps_tau[key].append(snap[key][0])
                    snaps_mag[key].append(snap[key][1])
                snaps_loss.append(float(loss.detach()))
                print(f"    step {step:4d} loss {float(loss.detach()):.4f} "
                      f"[logged]", flush=True)
        fmc, fsp = final_wire_stats(wrapped)
        final_magcos.append(fmc)
        final_sparsity.append(fsp)
        per_seed_tau.append(snaps_tau)
        per_seed_mag.append(snaps_mag)
        per_seed_loss.append(snaps_loss)                     # NON-FROZEN
        if args.dump_history:                                # NON-FROZEN
            per_seed_r.append(marginality(wrapped, coords))
        # restore (bit-exact — unwrap LoRA)
        for (m, name, lw, _key) in wrapped:
            setattr(m, name, lw.base)
        print(f"    seed {s}: final mag_cos {fmc:.3f} sparsity {fsp:.3f}",
              flush=True)

    # ── pool: (n_trit, n_snap) over all layers × seeds (coords aligned) ──
    n_snap = len(steps_sched)
    key_list = list(coords)
    tau_cols, mag_cols, r_cols, blk_cols = [], [], [], []
    for si in range(len(per_seed_tau)):
        for ki, key in enumerate(key_list):
            tau_cols.append(np.stack(per_seed_tau[si][key], axis=1))  # (N,snap)
            mag_cols.append(np.stack(per_seed_mag[si][key], axis=1))
            n_k = tau_cols[-1].shape[0]
            blk_cols.append(np.full(n_k, si * len(key_list) + ki, np.int16))
            if per_seed_r:                                   # NON-FROZEN
                r_cols.append(per_seed_r[si][key])
    tau_all = np.concatenate(tau_cols, axis=0)
    mag_all = np.concatenate(mag_cols, axis=0)
    print(f"[sc] pooled tracked trits: {tau_all.shape[0]} × {n_snap} snaps")

    # ── NON-FROZEN: raw history dump for offline magnitude-split re-score ──
    if args.dump_history:
        dp = Path(args.dump_history)
        dp.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            dp,
            tau=tau_all.astype(np.int8),
            mag=mag_all.astype(np.float32),
            r_final=np.concatenate(r_cols).astype(np.float32),
            block_id=np.concatenate(blk_cols),
            steps=np.asarray(steps_sched, np.int32),
            loss=np.asarray(per_seed_loss, np.float32),      # (seeds, n_snap)
            keys=np.asarray(key_list * len(per_seed_tau)),   # per-block key
        )
        print(f"[sc] NON-FROZEN dumped tracked history -> {dp}")

    # score against the ACTUAL logged schedule (smoke may truncate it)
    sc = score_curve(tau_all, mag_all, steps_sched,
                     np.random.default_rng(args.seed + 999),
                     final_magcos=float(np.mean(final_magcos)),
                     final_sparsity=float(np.mean(final_sparsity)))
    v = sc["verdict"]
    print(f"\n[sc] ════ VERDICT: {v} ════")
    g = sc["gates"]
    print(f"  G1_sign_early={g['G1_sign_early']} "
          f"G2_two_timescale={g['G2_two_timescale']} "
          f"G3_null_beats={g['G3_null_beats']} G4_wire_sane={g['G4_wire_sane']}")
    print(f"  med_commit={sc['med_commit']:.1f} (frac {sc['commit_frac']:.3f}) "
          f"t_sign={sc['t_sign']:.0f} t_mag={sc['t_mag']:.0f} "
          f"ratio={sc['ratio']:.2f} CI={tuple(round(x,2) for x in sc['ratio_ci'])}")
    print(f"  S(0.25T)={sc['s_quarter']:.3f} S(T⁻)={sc['s_prefinal']:.3f} "
          f"flip_last={sc['flip_last']:.4f} p_null={sc['p_null']:.4f}")
    print(f"  final mag_cos={sc['final_magcos']:.3f} "
          f"sparsity={sc['final_sparsity']:.3f}")

    payload = {"model_id": args.model_id, "config": vars(args),
               "band": band, "steps_sched": steps_sched,
               "n_train_cells": len(valid_train),
               "final_magcos_seeds": final_magcos,
               "final_sparsity_seeds": final_sparsity,
               "scoring": sc}
    (out_dir / "results.json").write_text(
        json.dumps(_json_safe(payload), indent=2))
    print(f"[sc] wrote {out_dir}/results.json")
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
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-cells", type=int, default=0,
                    help="smoke: cap train cells (mechanics only)")
    ap.add_argument("--gate0",
                    default="results/writeback-compile/qwen3-4b/gate0.json")
    ap.add_argument("--out", default="results/sign-commitment/qwen3-4b")
    ap.add_argument("--dump-history", default="",
                    help="NON-FROZEN post-hoc analysis: path to save the raw "
                         "tracked (tau, |Δ|, marginality r=|Δ_T|/thr_j, "
                         "block_id, per-step loss) as .npz. Frozen scoring/"
                         "gates/verdict are UNTOUCHED; enables offline "
                         "magnitude-split re-score without a re-run.")
    args = ap.parse_args()
    if args.validate:
        return run_validate()
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
