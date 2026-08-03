"""P-CAPACITY-LAW — capacity, replay, and time-Bragg laws of the ternary store.

Pre-reg: mementum/knowledge/ternary-holographic-memory.md §6b (s301, frozen
before run, Michael-approved fffd4b7). Substrate = src/verbum/memory VERBATIM
(s300 POC, 13 green gates) — measurement only, no new mechanism, no model,
no GD. Pure numpy + verbum.dsp scoring.

Registers (λ measure, declared a priori):
  capacity/SNR = value · replay-exact = causal/deterministic · time-Bragg =
  routing.

Two register forks pre-declared in §6b (design facts, not post-hoc):
  1. independent keys WHITEN data → coherent gain reachable only in the
     shared-address register; its absence under indep keys is prediction G3.
  2. sign() commutes with ±1 unbind → recover() is collapse-invariant;
     snapshot loss lives in correlate-SNR (a-priori x sqrt(2/pi)) and in
     REPEATED collapse-checkpointing (G4b), not in recover().

Gates (frozen; all dsp.gate with declared null + direction, alpha=0.05):
  G1 HRR-FORM        random x indep SNR(k) log-log slope vs beta*=-1/2;
                     |beta-beta*| predict=less vs matched_range (s247).
                     Materiality: monotone decline AND SNR(kmax)<SNR(1)/2.
  G2 COHERENT-GAIN   correlated x shared prototype-SNR slope predict=greater
                     vs c=0 pipeline rerun null (R draws, mean-curve slope
                     each). Form |beta-1/2| ADVISORY vs matched_range.
  G3 ADDRESS-FORK    per-seed dslope = slope_shared(proto) - slope_indep(proto)
                     predict=greater, paired_permutation 10k.
  G4a REPLAY-EXACT   1024-commit log (+undo+squash): shuffled-order re-fold
                     state_hash identical at every prefix. Deterministic.
  G4b CHECKPOINT-SHADOW  C in {0,1,2,4,8} collapse-checkpoints; per-seed
                     fidelity(C=0)-fidelity(C=8) predict=greater, sign_flip
                     10k. C=0 must be exact.
  G5 TIME-BRAGG      k=kmax: mean correlate at true t vs sidelobe draws at
                     offsets {±1,±2,±4,±8} (the sidelobes ARE the null),
                     predict=greater. A-priori peak≈D, sidelobe sigma≈sqrt(kD).

Verdicts (frozen): CAPACITY-LAW-CONFIRMED (G1∧G2∧G4a∧G4b∧G5) / DECLINE-ONLY
(G1∧¬G2) / GAIN-WITHOUT-FORM (¬G1∧G2) / SUBSTRATE-FAULT (NOT G4a or NOT G5) /
INCONCLUSIVE. G3 modulates interpretation only.

License: MIT (λ provenance — standalone math, no model weights anywhere).
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from verbum.dsp import NullDraws, gate, matched_range, paired_permutation, sign_flip
from verbum.memory import (
    DeltaLog,
    collapse,
    correlate,
    encode,
    fold,
    keygen,
    recover,
    state_hash,
)

K_GRID = (1, 2, 4, 8, 16, 32, 64, 128)
C_GRID = (0, 1, 2, 4, 8)  # G4b collapse-checkpoint counts
BRAGG_OFFSETS = (-8, -4, -2, -1, 1, 2, 4, 8)
SNR_FLOOR = 1e-3  # log-fit clip (recorded; c=0 null curves hover near 0)
ALPHA = 0.05

# explicit-seed scheme (s296 law: never hash(), never implicit)
SEED_BANK = 10_000     # + 100*seed_idx + family_code
SEED_KEYS = 20_000     # + 100*seed_idx + family_code
SEED_WRONG = 30_000    # + 100*seed_idx + k
SEED_NULLBANK = 40_000  # + 100*draw_idx (G2 c=0 reruns)
SEED_SCORE = 777       # permutation/sign-flip rng
FAMILY_CODE = {"random": 0, "correlated": 1, "hier": 2}


# ══════════════════════════════════════════════════════════════════════════
# banks (data families)
# ══════════════════════════════════════════════════════════════════════════
def _pm1(rng: np.random.Generator, *shape: int) -> np.ndarray:
    return (rng.integers(0, 2, size=shape, dtype=np.int8) * 2 - 1).astype(np.int8)


def _degrade(rng: np.random.Generator, proto: np.ndarray, c: float) -> np.ndarray:
    """Item correlated with proto at expected cosine c: flip fraction (1-c)/2."""
    flips = rng.random(proto.shape) < (1.0 - c) / 2.0
    out = proto.copy()
    out[flips] *= -1
    return out


def make_bank(seed: int, family: str, k: int, dim: int, c: float = 0.5,
              c_super: float = 0.7) -> dict:
    """Returns {'values': (k,dim) int8, 'proto': (dim,) int8 | None, ...}."""
    rng = np.random.default_rng(seed)
    if family == "random":
        return {"values": _pm1(rng, k, dim), "proto": None}
    if family == "correlated":
        proto = _pm1(rng, dim)
        vals = np.stack([_degrade(rng, proto, c) for _ in range(k)])
        return {"values": vals, "proto": proto}
    if family == "hier":
        root = _pm1(rng, dim)
        supers = np.stack([_degrade(rng, root, c_super) for _ in range(4)])
        vals = np.stack([_degrade(rng, supers[i % 4], c) for i in range(k)])
        return {"values": vals, "proto": root, "supers": supers}
    raise ValueError(f"unknown family {family!r}")


# ══════════════════════════════════════════════════════════════════════════
# write + read (the substrate, driven)
# ══════════════════════════════════════════════════════════════════════════
def write_state(values: np.ndarray, key_seed: int, address: str) -> dict:
    """Fold the bank into a vote state under an address register.

    indep  — per-item key + per-item time (the episodic write)
    shared — one key, t=0 for all (the coherent write)
    """
    k, dim = values.shape
    if address == "indep":
        keys = keygen(key_seed, dim, n=k).reshape(k, dim)
        times = list(range(k))
    elif address == "shared":
        keys = np.repeat(keygen(key_seed, dim)[None, :], k, axis=0)
        times = [0] * k
    else:
        raise ValueError(f"unknown address {address!r}")
    deltas = [encode(keys[i], values[i], times[i]) for i in range(k)]
    state = fold(deltas, np.zeros(dim, dtype=np.int64))
    return {"state": state, "keys": keys, "times": times}


def wrongkey_noise_std(state: np.ndarray, dim: int, seed: int,
                       n_draws: int = 50) -> float:
    """Noise floor: std of correlate(state, wrong-key probe) — the unit-test
    null promoted to yardstick (§6b SNR definition)."""
    wk = keygen(seed, dim, n=n_draws).reshape(n_draws, dim)
    draws = [correlate(state, wk[i], t=0) for i in range(n_draws)]
    return float(np.std(draws))


def item_snr(world: dict, values: np.ndarray, noise_std: float) -> float:
    """Per-item SNR: mean true-probe correlation / wrong-key noise std."""
    k = values.shape[0]
    sigs = []
    for i in range(k):
        probe = encode(world["keys"][i], values[i], world["times"][i])
        sigs.append(correlate(world["state"], probe, t=0))
    return float(np.mean(sigs) / max(noise_std, 1e-12))


def proto_snr(world: dict, proto: np.ndarray, noise_std: float,
              address: str) -> float:
    """Prototype SNR. shared: one probe at the shared address. indep: mean
    over per-item addresses probed with the prototype (§6b G3 definition)."""
    if address == "shared":
        probe = encode(world["keys"][0], proto, world["times"][0])
        sig = correlate(world["state"], probe, t=0)
    else:
        sigs = []
        for i in range(world["keys"].shape[0]):
            probe = encode(world["keys"][i], proto, world["times"][i])
            sigs.append(correlate(world["state"], probe, t=0))
        sig = float(np.mean(sigs))
    return float(sig / max(noise_std, 1e-12))


# ══════════════════════════════════════════════════════════════════════════
# statistics
# ══════════════════════════════════════════════════════════════════════════
def loglog_slope(k_grid: np.ndarray, snr: np.ndarray,
                 floor: float = SNR_FLOOR) -> float:
    """OLS slope of log(clip(snr)) vs log(k). Clip recorded in pre-reg."""
    x = np.log(np.asarray(k_grid, dtype=float))
    y = np.log(np.clip(np.asarray(snr, dtype=float), floor, None))
    x = x - x.mean()
    return float(np.dot(x, y - y.mean()) / np.dot(x, x))


def snr_curves(dim: int, seeds: int, family: str, address: str,
               c: float = 0.5) -> dict:
    """Per-seed item- and prototype-SNR curves over K_GRID."""
    fam = FAMILY_CODE[family]
    item = np.zeros((seeds, len(K_GRID)))
    proto = np.zeros((seeds, len(K_GRID)))
    for s in range(seeds):
        for j, k in enumerate(K_GRID):
            bank = make_bank(SEED_BANK + 100 * s + fam, family, k, dim, c=c)
            world = write_state(bank["values"], SEED_KEYS + 100 * s + fam, address)
            noise = wrongkey_noise_std(world["state"], dim,
                                       SEED_WRONG + 100 * s + k)
            item[s, j] = item_snr(world, bank["values"], noise)
            if bank["proto"] is not None:
                proto[s, j] = proto_snr(world, bank["proto"], noise, address)
    return {"item": item, "proto": proto}


# ══════════════════════════════════════════════════════════════════════════
# gate legs
# ══════════════════════════════════════════════════════════════════════════
def run_g1(dim: int, seeds: int, rng: np.random.Generator) -> dict:
    curves = snr_curves(dim, seeds, "random", "indep")
    mean_curve = curves["item"].mean(axis=0)
    beta = loglog_slope(np.array(K_GRID), mean_curve)
    stat_val = abs(beta + 0.5)
    monotone = bool(np.all(np.diff(mean_curve) <= 0))
    material = bool(mean_curve[-1] < mean_curve[0] / 2)

    def stat(random_curve: np.ndarray) -> float:
        return abs(loglog_slope(np.array(K_GRID), random_curve) + 0.5)

    null = matched_range(stat, mean_curve, rng, n_iter=200)
    g = gate(stat_val, null, predict="less", alpha=ALPHA, name="G1_HRR_FORM")
    verdict = bool(g.verdict and monotone and material)
    return {"curves": curves, "mean_curve": mean_curve, "beta": beta,
            "monotone": monotone, "material": material, "gated": g,
            "verdict": verdict}


def run_g2_g3(dim: int, seeds: int, rng: np.random.Generator) -> dict:
    # observed: correlated banks, both address registers
    cur_sh = snr_curves(dim, seeds, "correlated", "shared")
    cur_in = snr_curves(dim, seeds, "correlated", "indep")
    mean_proto_sh = cur_sh["proto"].mean(axis=0)
    beta2 = loglog_slope(np.array(K_GRID), mean_proto_sh)

    # G2 null: same pipeline, c=0 banks (proto uncorrelated with items),
    # R draws, each a mean-curve slope over `seeds` fresh seeds
    null_draws = []
    for d in range(seeds):
        proto_curve = np.zeros(len(K_GRID))
        for j, k in enumerate(K_GRID):
            seed = SEED_NULLBANK + 100 * d + j
            bank = make_bank(seed, "correlated", k, dim, c=0.0)
            world = write_state(bank["values"], seed + 50, "shared")
            noise = wrongkey_noise_std(world["state"], dim, seed + 70)
            proto_curve[j] = proto_snr(world, bank["proto"], noise, "shared")
        null_draws.append(loglog_slope(np.array(K_GRID), proto_curve))
    null2 = NullDraws("c0_rerun_slopes", np.array(null_draws),
                      {"n_draws": seeds, "c": 0.0, "seed_base": SEED_NULLBANK})
    g2 = gate(beta2, null2, predict="greater", alpha=ALPHA,
              name="G2_COHERENT_GAIN")

    def form_stat(random_curve: np.ndarray) -> float:
        return abs(loglog_slope(np.array(K_GRID), random_curve) - 0.5)

    form_null = matched_range(form_stat, mean_proto_sh, rng, n_iter=200)
    g2_form_advisory = gate(abs(beta2 - 0.5), form_null, predict="less",
                            alpha=ALPHA, name="G2_FORM_ADVISORY")

    # G3: per-seed dslope shared - indep (prototype), paired permutation
    sl_sh = np.array([loglog_slope(np.array(K_GRID), cur_sh["proto"][s])
                      for s in range(seeds)])
    sl_in = np.array([loglog_slope(np.array(K_GRID), cur_in["proto"][s])
                      for s in range(seeds)])
    null3 = paired_permutation(sl_sh, sl_in, rng, n_iter=10_000)
    g3 = gate(float(np.mean(sl_sh - sl_in)), null3, predict="greater",
              alpha=ALPHA, name="G3_ADDRESS_FORK")
    return {"curves_shared": cur_sh, "curves_indep": cur_in, "beta2": beta2,
            "g2": g2, "g2_form_advisory": g2_form_advisory,
            "slopes_shared": sl_sh, "slopes_indep": sl_in, "g3": g3}


def run_g4a(dim: int, n_commits: int = 1024, seed: int = 4_001) -> dict:
    """Deterministic replay gate: shuffled-order re-fold hash-identical at
    every checked prefix; squash preserves the head. No p-value."""
    rng = np.random.default_rng(seed)
    log = DeltaLog(dim)
    for i in range(n_commits):
        key = keygen(seed + 1 + i, dim)
        val = _pm1(rng, dim)
        log.append(encode(key, val, t=i))
        if i > 0 and i % 100 == 0:
            log.undo(rng.integers(0, len(log) - 1))
    prefixes = sorted({p for p in (1, 2, 4, 8, 16, 64, 256, 512, len(log))
                       if p <= len(log)})
    all_ok, checks = True, []
    for p in prefixes:
        h_ordered = state_hash(log.state(p))
        idx = rng.permutation(p)
        h_shuffled = state_hash(fold([log.deltas[i] for i in idx], log.base))
        ok = h_ordered == h_shuffled
        all_ok &= ok
        checks.append({"prefix": int(p), "ok": bool(ok), "hash": h_ordered})
    squashed = log.squash(len(log) // 2)
    squash_ok = state_hash(squashed.state()) == state_hash(log.state())
    all_ok &= squash_ok
    return {"verdict": bool(all_ok), "checks": checks,
            "squash_preserves_head": bool(squash_ok),
            "head_hash": state_hash(log.state())}


def run_g4b(dim: int, seeds: int, rng: np.random.Generator,
            n_items: int = 64) -> dict:
    """Collapse-checkpoint shadow: fold onto collapse(state) at C points."""
    fam = FAMILY_CODE["random"]
    fid = np.zeros((seeds, len(C_GRID)))
    for s in range(seeds):
        bank = make_bank(SEED_BANK + 100 * s + fam, "random", n_items, dim)
        keys = keygen(SEED_KEYS + 100 * s + fam, dim, n=n_items).reshape(n_items, dim)
        deltas = [encode(keys[i], bank["values"][i], t=i) for i in range(n_items)]
        true_state = fold(deltas, np.zeros(dim, dtype=np.int64))
        for cj, n_ckpt in enumerate(C_GRID):
            segments = np.array_split(np.arange(n_items), n_ckpt + 1)
            state = np.zeros(dim, dtype=np.int64)
            for gi, seg in enumerate(segments):
                if gi > 0:
                    state = collapse(state).astype(np.int64)  # lossy base
                state = fold([deltas[i] for i in seg], state)
            agree = np.mean([
                np.mean(recover(state, keys[i], t=i) == bank["values"][i])
                for i in range(n_items)
            ])
            fid[s, cj] = float(agree)
            if n_ckpt == 0 and state_hash(state) != state_hash(true_state):
                raise AssertionError("G4b C=0 must be exact (ties G4a)")
    diffs = fid[:, 0] - fid[:, -1]  # C=0 minus C=8, per seed
    null = sign_flip(diffs, rng, n_iter=10_000)
    g = gate(float(np.mean(diffs)), null, predict="greater", alpha=ALPHA,
             name="G4b_CHECKPOINT_SHADOW")
    return {"fidelity": fid, "c_grid": list(C_GRID), "gated": g}


def run_g4_advisory(dim: int, seeds: int) -> dict:
    """Snapshot/vote correlate-SNR ratio — a-priori sqrt(2/pi)≈0.7979."""
    fam = FAMILY_CODE["random"]
    ratios = np.zeros((seeds, len(K_GRID)))
    for s in range(seeds):
        for j, k in enumerate(K_GRID):
            bank = make_bank(SEED_BANK + 100 * s + fam, "random", k, dim)
            world = write_state(bank["values"], SEED_KEYS + 100 * s + fam, "indep")
            snap = collapse(world["state"]).astype(np.int64)
            n_vote = wrongkey_noise_std(world["state"], dim,
                                        SEED_WRONG + 100 * s + k)
            n_snap = wrongkey_noise_std(snap, dim, SEED_WRONG + 100 * s + k)
            sv = {"state": world["state"], "keys": world["keys"],
                  "times": world["times"]}
            ss = {"state": snap, "keys": world["keys"], "times": world["times"]}
            snr_v = item_snr(sv, bank["values"], n_vote)
            snr_s = item_snr(ss, bank["values"], n_snap)
            ratios[s, j] = snr_s / max(snr_v, 1e-12)
    return {"ratios": ratios, "mean_by_k": ratios.mean(axis=0),
            "a_priori": float(np.sqrt(2 / np.pi))}


def run_g5(dim: int, seeds: int, k: int = K_GRID[-1]) -> dict:
    """Time-Bragg: true-t correlation vs pooled sidelobe draws at offsets."""
    fam = FAMILY_CODE["random"]
    peaks, sidelobes = [], []
    curve: dict[int, list[float]] = {d: [] for d in BRAGG_OFFSETS}
    for s in range(seeds):
        bank = make_bank(SEED_BANK + 100 * s + fam, "random", k, dim)
        world = write_state(bank["values"], SEED_KEYS + 100 * s + fam, "indep")
        for i in range(0, k, 8):  # every 8th item: 16 probes/seed
            bound = encode(world["keys"][i], bank["values"][i], 0)
            peaks.append(correlate(world["state"], bound, t=world["times"][i]))
            for d in BRAGG_OFFSETS:
                v = correlate(world["state"], bound, t=world["times"][i] + d)
                sidelobes.append(v)
                curve[d].append(v)
    null = NullDraws("time_sidelobes", np.array(sidelobes, dtype=float),
                     {"offsets": list(BRAGG_OFFSETS), "k": k,
                      "n_draws": len(sidelobes)})
    g = gate(float(np.mean(peaks)), null, predict="greater", alpha=ALPHA,
             name="G5_TIME_BRAGG")
    return {"gated": g, "peak_mean": float(np.mean(peaks)),
            "sidelobe_std": float(np.std(sidelobes)),
            "selectivity_curve": {str(d): float(np.mean(v))
                                  for d, v in curve.items()},
            "n_sigma": float(np.mean(peaks) / max(np.std(sidelobes), 1e-12))}


def run_hier_advisory(dim: int, seeds: int) -> dict:
    """§6 self-similar family — multi-scale SNR curves, ADVISORY (no gate)."""
    fam = FAMILY_CODE["hier"]
    root = np.zeros((seeds, len(K_GRID)))
    supers = np.zeros((seeds, len(K_GRID)))
    for s in range(seeds):
        for j, k in enumerate(K_GRID):
            bank = make_bank(SEED_BANK + 100 * s + fam, "hier", k, dim)
            world = write_state(bank["values"], SEED_KEYS + 100 * s + fam,
                                "shared")
            noise = wrongkey_noise_std(world["state"], dim,
                                       SEED_WRONG + 100 * s + k)
            root[s, j] = proto_snr(world, bank["proto"], noise, "shared")
            supers[s, j] = float(np.mean([
                proto_snr(world, bank["supers"][m], noise, "shared")
                for m in range(4)
            ]))
    return {"root_mean": root.mean(axis=0), "super_mean": supers.mean(axis=0)}


# ══════════════════════════════════════════════════════════════════════════
# verdict + record
# ══════════════════════════════════════════════════════════════════════════
def assign_verdict(g1: bool, g2: bool, g4a: bool, g4b: bool, g5: bool) -> str:
    if not (g4a and g5):
        return "SUBSTRATE-FAULT"
    if g1 and g2 and g4b:
        return "CAPACITY-LAW-CONFIRMED"
    if g1 and not g2:
        return "DECLINE-ONLY"
    if g2 and not g1:
        return "GAIN-WITHOUT-FORM"
    return "INCONCLUSIVE"


def _json_safe(o):
    if isinstance(o, dict):
        return {k: _json_safe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_json_safe(v) for v in o]
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if hasattr(o, "__dataclass_fields__"):
        return _json_safe(asdict(o))
    return o


def git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
            cwd=Path(__file__).resolve().parents[2], check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def main_run(dim: int, seeds: int, out: Path) -> int:
    rng = np.random.default_rng(SEED_SCORE)
    print(f"── P-CAPACITY-LAW run: D={dim} R={seeds} k={K_GRID} ──")

    g1 = run_g1(dim, seeds, rng)
    print(f"G1 HRR-FORM: beta={g1['beta']:+.3f} (a-priori -0.5) "
          f"|Δ|={g1['gated'].value:.4f} p={g1['gated'].p:.4f} "
          f"monotone={g1['monotone']} material={g1['material']} "
          f"→ {'PASS' if g1['verdict'] else 'FAIL'}")

    g23 = run_g2_g3(dim, seeds, rng)
    print(f"G2 COHERENT-GAIN: beta2={g23['beta2']:+.3f} (a-priori +0.5) "
          f"p={g23['g2'].p:.4f} null_mean={g23['g2'].null_mean:+.3f} "
          f"→ {'PASS' if g23['g2'].verdict else 'FAIL'} "
          f"[form advisory p={g23['g2_form_advisory'].p:.4f}]")
    print(f"G3 ADDRESS-FORK: dslope={g23['g3'].value:+.3f} "
          f"p={g23['g3'].p:.4f} → {'PASS' if g23['g3'].verdict else 'FAIL'}")

    g4a = run_g4a(dim)
    print(f"G4a REPLAY-EXACT: {len(g4a['checks'])} prefixes + squash "
          f"→ {'PASS' if g4a['verdict'] else 'FAIL'}")

    g4b = run_g4b(dim, seeds, rng)
    fid = g4b["fidelity"].mean(axis=0)
    print(f"G4b CHECKPOINT-SHADOW: fidelity C{list(C_GRID)} = "
          f"{[round(float(x), 4) for x in fid]} "
          f"Δ={g4b['gated'].value:+.4f} p={g4b['gated'].p:.4f} "
          f"→ {'PASS' if g4b['gated'].verdict else 'FAIL'}")

    g4adv = run_g4_advisory(dim, seeds)
    print(f"G4 advisory snapshot/vote SNR ratio by k: "
          f"{[round(float(x), 3) for x in g4adv['mean_by_k']]} "
          f"(a-priori {g4adv['a_priori']:.4f})")

    g5 = run_g5(dim, seeds)
    print(f"G5 TIME-BRAGG: peak={g5['peak_mean']:.0f} "
          f"sidelobe_sigma={g5['sidelobe_std']:.0f} "
          f"({g5['n_sigma']:.1f}sigma; a-priori >=5sigma) p={g5['gated'].p:.4f} "
          f"→ {'PASS' if g5['gated'].verdict else 'FAIL'}")

    hier = run_hier_advisory(dim, seeds)
    print(f"hier advisory: root SNR {[round(float(x), 1) for x in hier['root_mean']]}")
    print(f"               super SNR "
          f"{[round(float(x), 1) for x in hier['super_mean']]}")

    verdict = assign_verdict(g1["verdict"], g23["g2"].verdict, g4a["verdict"],
                             g4b["gated"].verdict, g5["gated"].verdict)
    g3note = "gain-lives-in-address-sharing" if g23["g3"].verdict \
        else "address-fork-not-shown"
    print(f"\n▶▶ VERDICT: {verdict} (G3: {g3note})")

    out.mkdir(parents=True, exist_ok=True)
    meta = {
        "run_id": out.name,
        "timestamp": datetime.now(UTC).isoformat(),
        "prereg": "ternary-holographic-memory.md §6b (frozen fffd4b7)",
        "git_sha": git_sha(),
        "numpy": np.__version__,
        "python": platform.python_version(),
        "params": {"dim": dim, "seeds": seeds, "k_grid": list(K_GRID),
                   "c": 0.5, "c_super": 0.7, "c_grid": list(C_GRID),
                   "bragg_offsets": list(BRAGG_OFFSETS),
                   "snr_floor": SNR_FLOOR, "alpha": ALPHA,
                   "seed_scheme": {"bank": SEED_BANK, "keys": SEED_KEYS,
                                   "wrong": SEED_WRONG,
                                   "nullbank": SEED_NULLBANK,
                                   "score": SEED_SCORE}},
        "model": None,  # model-free by construction
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    results = {
        "verdict": verdict,
        "g1": _json_safe(g1), "g2_g3": _json_safe(g23),
        "g4a": _json_safe(g4a), "g4b": _json_safe(g4b),
        "g4_advisory": _json_safe(g4adv), "g5": _json_safe(g5),
        "hier_advisory": _json_safe(hier),
    }
    (out / "results.json").write_text(json.dumps(results, indent=2))
    print(f"recorded → {out}/meta.json + results.json")
    return 0


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds, no full run
# ══════════════════════════════════════════════════════════════════════════
def validate() -> int:
    dim, ok = 1024, True
    print("── P-CAPACITY-LAW --validate (planted, model-free) ──")

    def check(name: str, cond: bool):
        nonlocal ok
        ok &= cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    # 1. single-item exact recovery
    key = keygen(1, dim)
    val = _pm1(np.random.default_rng(2), dim)
    st = fold([encode(key, val, t=3)], np.zeros(dim, dtype=np.int64))
    check("single-item recover exact", bool(np.all(recover(st, key, t=3) == val)))

    # 2. slope machinery on planted sqrt(D/k) curve
    planted = np.sqrt(dim / np.array(K_GRID, dtype=float))
    check("planted HRR curve fits beta=-0.5",
          abs(loglog_slope(np.array(K_GRID), planted) + 0.5) < 1e-9)

    # 3. time-shift selectivity on a single item
    peak = correlate(st, encode(key, val, 0), t=3)
    off = correlate(st, encode(key, val, 0), t=4)
    check("time-address selective (single item)", peak == dim and abs(off) < peak)

    # 4. collapse commutes with recover (§6b fork 2, direct check)
    bank = make_bank(11, "random", 8, dim)
    world = write_state(bank["values"], 12, "indep")
    snap = collapse(world["state"]).astype(np.int64)
    same = all(
        np.all(recover(world["state"], world["keys"][i], t=world["times"][i])
               == recover(snap, world["keys"][i], t=world["times"][i]))
        for i in range(8)
    )
    check("recover() collapse-invariant", bool(same))

    # 5. mini G4a determinism
    g4a = run_g4a(dim, n_commits=64, seed=99)
    check("mini replay-exact (64 commits)", g4a["verdict"])

    # 6. pipeline determinism: same seeds → same curve twice
    c1 = snr_curves(dim, 2, "random", "indep")["item"]
    c2 = snr_curves(dim, 2, "random", "indep")["item"]
    check("pipeline deterministic", bool(np.array_equal(c1, c2)))

    # 7. correlated bank hits target cosine
    b = make_bank(21, "correlated", 16, dim, c=0.5)
    cos = float(np.mean(b["values"].astype(np.int64) @ b["proto"].astype(np.int64))
                / dim)  # int64 cast: int8 matmul overflows (register discipline)
    check("correlated bank c≈0.5", abs(cos - 0.5) < 0.06)

    print(f"── validate: {'ALL PASS' if ok else 'FAILURES'} ──")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="P-CAPACITY-LAW (§6b, model-free)")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--dim", type=int, default=4096)
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--out", type=Path,
                    default=Path("results/capacity-law-s301"))
    args = ap.parse_args()
    if args.validate:
        return validate()
    return main_run(args.dim, args.seeds, args.out)


if __name__ == "__main__":
    sys.exit(main())
