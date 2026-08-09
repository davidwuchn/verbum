#!/usr/bin/env python3
"""§P-STRATIGRAPHY-DATING — differential photography read on the Pythia fossil record.

Pre-reg: mementum/knowledge/explore/types-are-a-modulation-scheme.md
§P-STRATIGRAPHY-DATING (FROZEN s325, Michael GO; SD2 = split-fraction gate,
Michael swap from dip test at freeze review).

Claim (§2 law): amplitude ∝ ∫error dt ≈ time-to-learn ⇒ three strata:
commons sign-freeze EARLY and end FAINT · long-tail accumulates LATE and
ends DENSE · contested churns throughout at net≈0.

The discriminating physics: both mundane accounts (noise-floor churn: small
weights flip trivially ⇒ small↔late; monotone growth: large weights escape
the noise floor sooner ⇒ large↔early) predict ρ(freeze_bin, |W_final|) < 0.
§2's early-AND-faint conjunction predicts ρ > 0. One pre-registered sign.

Register (λ measure): WEIGHT-GEOMETRY across checkpoints. No forward pass,
no wire, no write. Model = EleutherAI/pythia-160m (GPTNeoX dense_h_to_4h —
register mapping ≠ Qwen gate_proj, pinned at freeze; one escalation to
pythia-410m iff SD0 voids). 20 log-uniform checkpoints (Michael-approved
s325): step0 (unexposed plate) + native log2 ramp 1..512 + half-decade tail
1k..143k. ORDINAL strata dating only — 20 samples alias oscillation; no
flip-RATE claims (s324 flip-conflict lesson).

Gates:
  SD0 SANE          — loads/shapes/step0-symmetry/final≡published/non-degenerate bins
  SD1 EARLY-FAINT   — make-or-break: Spearman ρ(freeze_bin, log|W_final|) on the
                      frozen-by-b15 pool, 10k-permutation null; sign discriminates
  SD2 THREE-BAND    — split-fraction: commons(freeze≤b10) fraction in bottom
                      |W_final| decile > isotonic extrapolation from deciles 2-10
                      (10k parametric-binomial bootstrap)
  SD3 LATENT-DEV    — advisory: sign commits before amplitude develops (lag>0)
  SD4 LAYER-PROFILE — advisory: SD1 ρ per layer

Verdicts + a-priori (NOT tuned): STRATIFIED 25 / PARTIAL-STRATA 15 /
INVERTED 25 / UNSTRATIFIED 25 / VOID 10.

License: MIT (lambda provenance).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from fuel_theorem import spearman  # noqa: E402

# ══════════════════════════════════════════════════════════════════════════
# Construction (FROZEN s325)
# ══════════════════════════════════════════════════════════════════════════
STEPS = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512,
         1000, 2000, 4000, 8000, 16000, 33000, 66000, 100000, 143000]
N_BINS = len(STEPS)            # 20
SEED = 325                     # fixed coordinate-sampling seed
N_PER_LAYER = 33334            # x6 layers ≈ 200k coords total
FROZEN_BY_B15 = 15             # SD1 pool: no observed flip at steps >= 16k
COMMONS_MAX_BIN = 10           # commons: sign constant from step<=512 onward
CHURN_MIN_BIN = 16             # churner: >=1 observed flip after b15
N_PERM = 10_000                # SD1 permutation null
N_BOOT = 10_000                # SD2 parametric-binomial bootstrap
ALPHA = 0.05
STEP0_SYM_TOL = 0.02           # SD0: |mean sign| at step0
MIN_BIN_FRAC = 0.01            # SD0 non-degenerate: each stratum bin >=1%
EPS = 1e-12

APRIORI = {"STRATIFIED": 25, "PARTIAL-STRATA": 15, "INVERTED": 25,
           "UNSTRATIFIED": 25, "VOID": 10}


@dataclass(frozen=True)
class ModelCfg:
    repo: str
    layers: tuple[int, ...]
    hidden: int
    inter: int


MODELS = {
    "pythia-160m": ModelCfg("EleutherAI/pythia-160m", tuple(range(6, 12)), 768, 3072),
    "pythia-410m": ModelCfg("EleutherAI/pythia-410m", tuple(range(12, 24)), 1024, 4096),
}


# ══════════════════════════════════════════════════════════════════════════
# Small stats helpers (pure numpy)
# ══════════════════════════════════════════════════════════════════════════
def _rank(x: np.ndarray) -> np.ndarray:
    """Average-tie ranks (dense enough for permutation work)."""
    order = np.argsort(x, kind="stable")
    ranks = np.empty(len(x), float)
    ranks[order] = np.arange(len(x), dtype=float)
    # average ties
    sx = x[order]
    i = 0
    while i < len(sx):
        j = i
        while j + 1 < len(sx) and sx[j + 1] == sx[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = 0.5 * (i + j)
        i = j + 1
    return ranks


def _z(x: np.ndarray) -> np.ndarray:
    s = x.std()
    return (x - x.mean()) / (s + EPS)


def pav_increasing(y: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Weighted pool-adjacent-violators, monotone non-decreasing fit."""
    blocks: list[list[float]] = []  # [mean, weight, count]
    for yi, wi in zip(y, w, strict=True):
        blocks.append([float(yi), float(wi), 1.0])
        while len(blocks) > 1 and blocks[-2][0] > blocks[-1][0]:
            m2, w2, c2 = blocks.pop()
            m1, w1, c1 = blocks[-1]
            blocks[-1] = [(m1 * w1 + m2 * w2) / (w1 + w2), w1 + w2, c1 + c2]
    out: list[float] = []
    for m, _, c in blocks:
        out.extend([m] * int(c))
    return np.array(out)


# ══════════════════════════════════════════════════════════════════════════
# Observables (pure; --validate exercises everything below this line)
# ══════════════════════════════════════════════════════════════════════════
def observables(signs: np.ndarray) -> dict[str, np.ndarray]:
    """signs: int8 [N_BINS, N]. Returns freeze_bin, flips, valid mask.

    freeze_bin = first bin f with sign constant (== final sign) for all b>=f.
    Dated against FINAL sign; step0 counts. Ordinal (aliased) — never rates.
    """
    sf = signs[-1]
    valid = sf != 0
    match = signs == sf[None, :]
    trailing = np.logical_and.accumulate(match[::-1], axis=0).sum(axis=0)
    freeze_bin = (signs.shape[0] - trailing).astype(np.int16)
    flips = (signs[1:] != signs[:-1]).sum(axis=0).astype(np.int16)
    return {"freeze_bin": freeze_bin, "flips": flips, "valid": valid}


def gate_sd0(signs: np.ndarray, obs: dict, *, loads_ok: bool,
             final_matches_published: bool) -> dict:
    valid = obs["valid"]
    fb = obs["freeze_bin"][valid]
    n = max(len(fb), 1)
    step0_mean_sign = float(np.abs(signs[0][valid].mean())) if valid.any() else 1.0
    frac_early = float((fb <= 5).sum() / n)
    frac_mid = float(((fb >= 11) & (fb <= 18)).sum() / n)
    frac_unfrozen = float((fb == 19).sum() / n)
    non_degenerate = (frac_early >= MIN_BIN_FRAC and frac_mid >= MIN_BIN_FRAC
                      and frac_unfrozen >= MIN_BIN_FRAC)
    ok = (loads_ok and final_matches_published
          and step0_mean_sign < STEP0_SYM_TOL and non_degenerate
          and float(valid.mean()) > 0.99)
    return {"gate": "SD0", "pass": bool(ok), "loads_ok": loads_ok,
            "final_matches_published": final_matches_published,
            "step0_mean_sign": step0_mean_sign,
            "frac_valid": float(valid.mean()),
            "frac_frozen_by_b5": frac_early, "frac_frozen_b11_b18": frac_mid,
            "frac_unfrozen_b19": frac_unfrozen, "non_degenerate": non_degenerate}


def gate_sd1(obs: dict, w_final: np.ndarray, rng: np.random.Generator,
             n_perm: int = N_PERM) -> dict:
    """Make-or-break. Spearman rho(freeze_bin, log|W_final|) on frozen-by-b15
    pool. Mundane physics => rho<0; §2 stratigraphy => rho>0."""
    valid = obs["valid"]
    pool = valid & (obs["freeze_bin"] <= FROZEN_BY_B15)
    fb = obs["freeze_bin"][pool].astype(float)
    lw = np.log(np.abs(w_final[pool]) + EPS)
    if len(fb) < 100 or fb.std() == 0 or lw.std() == 0:
        return {"gate": "SD1", "n_pool": len(fb), "rho": 0.0,
                "p_pos": 1.0, "p_neg": 1.0, "sign": "ns"}
    rho = spearman(fb, lw)
    zx, zy = _z(_rank(fb)), _z(_rank(lw))
    n = len(zx)
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = float(zx[rng.permutation(n)] @ zy) / n
    p_pos = float((null >= rho).mean())
    p_neg = float((null <= rho).mean())
    sign = "positive" if (rho > 0 and p_pos < ALPHA) else \
           "negative" if (rho < 0 and p_neg < ALPHA) else "ns"
    return {"gate": "SD1", "n_pool": int(n), "rho": float(rho),
            "p_pos": p_pos, "p_neg": p_neg, "sign": sign}


def _decile_labels(w_final: np.ndarray, layer_ids: np.ndarray,
                   valid: np.ndarray) -> np.ndarray:
    """Per-matrix (layer) |W_final| deciles 1..10; 0 = invalid."""
    dec = np.zeros(len(w_final), np.int8)
    for lid in np.unique(layer_ids):
        m = (layer_ids == lid) & valid
        if m.sum() < 100:
            continue
        r = _rank(np.abs(w_final[m]))
        dec[m] = np.minimum((r / m.sum() * 10).astype(int) + 1, 10)
    return dec


def gate_sd2(obs: dict, w_final: np.ndarray, layer_ids: np.ndarray,
             rng: np.random.Generator, n_boot: int = N_BOOT) -> dict:
    """Split-fraction three-band gate (Michael s325). Mundane =>
    P(commons|decile) monotone-increasing => bottom decile lowest, on-trend.
    Three-band => EXCESS commons mass in the bottom decile."""
    valid = obs["valid"]
    fb = obs["freeze_bin"]
    dec = _decile_labels(w_final, layer_ids, valid)
    commons = valid & (fb <= COMMONS_MAX_BIN)
    churn = valid & (fb >= CHURN_MIN_BIN)
    n_d = np.array([(dec == d).sum() for d in range(1, 11)], float)
    k_d = np.array([(commons & (dec == d)).sum() for d in range(1, 11)], float)
    if (n_d < 100).any():
        return {"gate": "SD2", "pass": False, "degenerate": True}
    p_d = k_d / n_d
    fit = pav_increasing(p_d[1:], n_d[1:])         # deciles 2..10
    pred_d1 = float(fit[0])                        # constant left-extension
    obs_d1 = float(p_d[0])
    delta = obs_d1 - pred_d1
    # parametric binomial bootstrap of the delta (coords independent | decile)
    boot = np.empty(n_boot)
    for i in range(n_boot):
        kb = rng.binomial(n_d.astype(int), p_d) / n_d
        boot[i] = kb[0] - float(pav_increasing(kb[1:], n_d[1:])[0])
    p_val = float((boot <= 0).mean())
    d1 = dec == 1
    split = {"commons": float((commons & d1).sum() / max(d1.sum(), 1)),
             "churner": float((churn & d1).sum() / max(d1.sum(), 1)),
             "middle": float(((valid & d1) & ~commons & ~churn).sum()
                             / max(d1.sum(), 1))}
    ok = delta > 0 and p_val < ALPHA
    return {"gate": "SD2", "pass": bool(ok), "degenerate": False,
            "obs_d1": obs_d1, "pred_d1": pred_d1, "delta": float(delta),
            "p": p_val, "frac_commons_by_decile": [float(x) for x in p_d],
            "bottom_decile_split": split}


def gate_sd3(obs: dict, mags: np.ndarray, w_final: np.ndarray,
             layer_ids: np.ndarray, rng: np.random.Generator) -> dict:
    """Advisory (§4 grokking≡development): among early-frozen small-band
    coords, lag = half-max-amplitude bin − freeze_bin. Report, never gate."""
    valid = obs["valid"]
    fb = obs["freeze_bin"]
    dec = _decile_labels(w_final, layer_ids, valid)
    sel = valid & (fb <= COMMONS_MAX_BIN) & (dec == 1)
    if sel.sum() < 50:
        return {"gate": "SD3", "advisory": True, "n": int(sel.sum()),
                "median_lag": None, "p": None}
    m = mags[:, sel]
    half = m >= 0.5 * m.max(axis=0, keepdims=True)
    hm_bin = half.argmax(axis=0).astype(float)
    lag = hm_bin - fb[sel].astype(float)
    med = float(np.median(lag))
    null = np.empty(1000)
    fbs = fb[sel].astype(float)
    for i in range(1000):
        null[i] = float(np.median(hm_bin - fbs[rng.permutation(len(fbs))]))
    p = float((null >= med).mean())
    return {"gate": "SD3", "advisory": True, "n": int(sel.sum()),
            "median_lag": med, "frac_positive": float((lag > 0).mean()), "p": p}


def gate_sd4(obs: dict, w_final: np.ndarray, layer_ids: np.ndarray) -> dict:
    """Advisory: SD1 rho per layer (BC3 style)."""
    valid = obs["valid"]
    pool = valid & (obs["freeze_bin"] <= FROZEN_BY_B15)
    per = {}
    for lid in sorted(int(x) for x in np.unique(layer_ids)):
        m = pool & (layer_ids == lid)
        if m.sum() < 100:
            continue
        per[str(lid)] = float(spearman(obs["freeze_bin"][m].astype(float),
                                       np.log(np.abs(w_final[m]) + EPS)))
    return {"gate": "SD4", "advisory": True, "rho_per_layer": per}


def verdict(sd0: dict, sd1: dict, sd2: dict) -> str:
    if not sd0["pass"]:
        return "VOID"
    if sd1["sign"] == "positive":
        return "STRATIFIED" if sd2["pass"] else "PARTIAL-STRATA"
    if sd1["sign"] == "negative":
        return "INVERTED"
    return "UNSTRATIFIED"


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (synthetic signs/mags → verdict tree)
# ══════════════════════════════════════════════════════════════════════════
def _mk_world(kind: str, rng: np.random.Generator, n: int = 30_000):
    """Three populations per world; returns signs [20,n], mags [20,n], layers."""
    layer_ids = rng.integers(0, 3, n).astype(np.int8)
    sf = rng.choice([-1, 1], n).astype(np.int8)
    signs = np.repeat(sf[None, :], N_BINS, axis=0).astype(np.int8)
    mags = np.zeros((N_BINS, n), np.float32)
    t = np.arange(N_BINS, dtype=np.float32)[:, None]

    def churn_rows(idx, from_bin):
        for b in range(1, N_BINS - 1):
            if b >= from_bin:
                flip = rng.random(len(idx)) < 0.5
                signs[b, idx[flip]] = -signs[b - 1, idx[flip]]
                signs[b, idx[~flip]] = signs[b - 1, idx[~flip]]
        # force final-transition flips for a subset => unfrozen at b19
        late = idx[rng.random(len(idx)) < 0.5]
        signs[N_BINS - 2, late] = -sf[late]

    def freeze_at(idx, fbin):
        # wrong sign before fbin, final sign from fbin on
        signs[:fbin, idx] = -sf[idx]
        if fbin > 0:
            signs[0, idx] = rng.choice([-1, 1], len(idx)).astype(np.int8)

    third = n // 3
    a, b, c = np.arange(third), np.arange(third, 2 * third), np.arange(2 * third, n)
    if kind in ("STRATIFIED", "PARTIAL"):
        fb_a = rng.integers(1, 5, len(a))    # commons: early freeze, faint
        for fbin in np.unique(fb_a):
            freeze_at(a[fb_a == fbin], int(fbin))
        mags[:, a] = 0.01 * np.minimum(t / 5.0, 1.0) + 0.001
        fb_b = rng.integers(11, 15, len(b))  # long-tail: late freeze, dense
        for fbin in np.unique(fb_b):
            freeze_at(b[fb_b == fbin], int(fbin))
        mags[:, b] = 1.0 * np.minimum(t / 15.0, 1.0) + 0.001
        churn_rows(c, 1)                     # contested: churn, faint
        mags[:, c] = 0.012 * np.ones_like(t) * (1 + 0.1 * rng.random(len(c)))
        if kind == "PARTIAL":
            # kill the bottom-decile commons excess: commons get MID mags
            mags[:, a] = 0.5 * np.minimum(t / 5.0, 1.0) + 0.3
    elif kind == "INVERTED":
        fb_a = rng.integers(1, 5, len(a))    # early freeze, DENSE
        for fbin in np.unique(fb_a):
            freeze_at(a[fb_a == fbin], int(fbin))
        mags[:, a] = 1.0 * np.minimum(t / 5.0, 1.0) + 0.001
        fb_b = rng.integers(11, 15, len(b))  # late freeze, faint
        for fbin in np.unique(fb_b):
            freeze_at(b[fb_b == fbin], int(fbin))
        mags[:, b] = 0.01 * np.minimum(t / 15.0, 1.0) + 0.001
        churn_rows(c, 1)
        mags[:, c] = 0.012 * np.ones_like(t)
    elif kind == "UNSTRATIFIED":
        fb = rng.integers(1, 15, n - third)
        ab = np.concatenate([a, b])
        for fbin in np.unique(fb):
            freeze_at(ab[fb == fbin], int(fbin))
        mags[:, ab] = np.abs(rng.normal(0.5, 0.3, (N_BINS, len(ab)))).astype(np.float32)
        churn_rows(c, 1)
        # null world: churner magnitude drawn from the SAME distribution as
        # the frozen pool — otherwise churners that randomly quiesce late
        # (P≈0.5^k) smuggle in the noise-floor small↔late coupling and the
        # null world reads (correctly!) as INVERTED. The real-data version of
        # that coupling is exactly what SD1's sign is designed to weigh.
        mags[:, c] = np.abs(rng.normal(0.5, 0.3, (N_BINS, len(c)))).astype(np.float32)
    elif kind == "VOID":
        mags[:] = np.abs(rng.normal(0.5, 0.3, (N_BINS, n))).astype(np.float32)
        # everything frozen from b0 => degenerate bins
    # per-coord jitter: breaks magnitude ties so per-matrix deciles populate
    mags *= (1.0 + 0.05 * rng.random(n)).astype(np.float32)[None, :]
    mags[-1] = np.maximum(mags[-1], 1e-6)
    return signs, mags, layer_ids


def run_gates(signs, mags, layer_ids, rng, *, loads_ok=True, final_ok=True,
              n_perm=N_PERM, n_boot=N_BOOT):
    obs = observables(signs)
    w_final = mags[-1]
    sd0 = gate_sd0(signs, obs, loads_ok=loads_ok,
                   final_matches_published=final_ok)
    sd1 = gate_sd1(obs, w_final, rng, n_perm=n_perm)
    sd2 = gate_sd2(obs, w_final, layer_ids, rng, n_boot=n_boot)
    sd3 = gate_sd3(obs, mags, w_final, layer_ids, rng)
    sd4 = gate_sd4(obs, w_final, layer_ids)
    return [sd0, sd1, sd2, sd3, sd4], verdict(sd0, sd1, sd2)


def validate() -> bool:
    expected = {"STRATIFIED": "STRATIFIED", "PARTIAL": "PARTIAL-STRATA",
                "INVERTED": "INVERTED", "UNSTRATIFIED": "UNSTRATIFIED",
                "VOID": "VOID"}
    ok_all = True
    for kind, want in expected.items():
        rng = np.random.default_rng(99)
        signs, mags, lids = _mk_world(kind, rng)
        gates, v = run_gates(signs, mags, lids, rng, n_perm=2000, n_boot=2000)
        ok = v == want
        ok_all &= ok
        sd1 = gates[1]
        print(f"  world={kind:<12} verdict={v:<14} want={want:<14} "
              f"rho={sd1.get('rho', float('nan')):+.3f} "
              f"{'PASS' if ok else 'FAIL'}")
    print(f"--validate: {'ALL PASS' if ok_all else 'FAIL'}")
    return ok_all


# ══════════════════════════════════════════════════════════════════════════
# Real run: download → slice → persist → gates → verdict
# ══════════════════════════════════════════════════════════════════════════
def _download_slices(cfg: ModelCfg, rev: str, idx: dict[int, np.ndarray],
                     dl_dir: Path) -> dict[int, np.ndarray]:
    from huggingface_hub import hf_hub_download
    from huggingface_hub.errors import EntryNotFoundError
    key = "gpt_neox.layers.{}.mlp.dense_h_to_4h.weight"
    out: dict[int, np.ndarray] = {}
    try:
        path = hf_hub_download(cfg.repo, "model.safetensors", revision=rev,
                               local_dir=dl_dir)
        from safetensors import safe_open
        with safe_open(path, framework="numpy") as f:
            for lid in cfg.layers:
                w = np.asarray(f.get_tensor(key.format(lid)), np.float32)
                assert w.shape == (cfg.inter, cfg.hidden), \
                    f"{rev} L{lid} shape {w.shape} != {(cfg.inter, cfg.hidden)}"
                out[lid] = w.reshape(-1)[idx[lid]]
    except EntryNotFoundError:
        import torch
        path = hf_hub_download(cfg.repo, "pytorch_model.bin", revision=rev,
                               local_dir=dl_dir)
        sd = torch.load(path, map_location="cpu", weights_only=True)
        for lid in cfg.layers:
            w = sd[key.format(lid)].float().numpy()
            assert w.shape == (cfg.inter, cfg.hidden), \
                f"{rev} L{lid} shape {w.shape} != {(cfg.inter, cfg.hidden)}"
            out[lid] = w.reshape(-1)[idx[lid]]
        del sd
    Path(path).unlink(missing_ok=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="pythia-160m", choices=sorted(MODELS))
    ap.add_argument("--out", type=Path,
                    default=Path("results/stratigraphy-dating/pythia-160m"))
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return 0 if validate() else 1

    cfg = MODELS[args.model]
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    dl_dir = out / "_dl"
    dl_dir.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)
    idx = {lid: np.sort(rng.choice(cfg.inter * cfg.hidden, N_PER_LAYER,
                                   replace=False)) for lid in cfg.layers}
    n_total = N_PER_LAYER * len(cfg.layers)
    layer_ids = np.concatenate([np.full(N_PER_LAYER, lid, np.int16)
                                for lid in cfg.layers])

    mags = np.zeros((N_BINS, n_total), np.float32)
    signs = np.zeros((N_BINS, n_total), np.int8)
    loads_ok = True
    t0 = time.time()
    for b, step in enumerate(STEPS):
        rev = f"step{step}"
        print(f"[{time.time() - t0:7.1f}s] bin {b:2d} ← {rev}", flush=True)
        sl = _download_slices(cfg, rev, idx, dl_dir)
        flat = np.concatenate([sl[lid] for lid in cfg.layers])
        mags[b] = np.abs(flat)
        signs[b] = np.sign(flat).astype(np.int8)

    print(f"[{time.time() - t0:7.1f}s] published-final check ← main", flush=True)
    sl_main = _download_slices(cfg, "main", idx, dl_dir)
    flat_main = np.concatenate([sl_main[lid] for lid in cfg.layers])
    final_ok = bool(np.array_equal(np.abs(flat_main), mags[-1])
                    and np.array_equal(np.sign(flat_main).astype(np.int8),
                                       signs[-1]))

    np.savez_compressed(
        out / "strata.npz", signs=signs, mags=mags, layer_ids=layer_ids,
        steps=np.array(STEPS), **{f"idx_L{lid}": idx[lid] for lid in cfg.layers})

    gates, v = run_gates(signs, mags, layer_ids, rng,
                         loads_ok=loads_ok, final_ok=final_ok)
    with (out / "results.jsonl").open("w") as f:
        for g in gates:
            f.write(json.dumps(g) + "\n")
        f.write(json.dumps({"verdict": v, "a_priori": APRIORI}) + "\n")

    def _sh(cmd: list[str]) -> str:
        try:
            return subprocess.run(cmd, capture_output=True, text=True,
                                  check=True).stdout.strip()
        except Exception:
            return "unknown"

    import huggingface_hub
    import transformers
    lock = Path("uv.lock")
    meta = {
        "run_id": f"stratigraphy-dating-{args.model}-s325",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": cfg.repo, "revisions": [f"step{s}" for s in STEPS] + ["main"],
        "layers": list(cfg.layers), "n_coords": n_total, "seed": SEED,
        "probe": "§P-STRATIGRAPHY-DATING (FROZEN s325, "
                 "types-are-a-modulation-scheme.md)",
        "git_sha": _sh(["git", "rev-parse", "HEAD"]),
        "lockfile_sha256": hashlib.sha256(lock.read_bytes()).hexdigest()
                           if lock.exists() else "missing",
        "lib_versions": {"numpy": np.__version__,
                         "transformers": transformers.__version__,
                         "huggingface_hub": huggingface_hub.__version__},
        "gate_params": {"n_perm": N_PERM, "n_boot": N_BOOT, "alpha": ALPHA,
                        "frozen_by": FROZEN_BY_B15,
                        "commons_max_bin": COMMONS_MAX_BIN,
                        "churn_min_bin": CHURN_MIN_BIN},
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2))

    for g in gates:
        print(json.dumps(g))
    print(f"VERDICT: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
