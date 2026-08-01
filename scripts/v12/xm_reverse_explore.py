"""XM Reverse-Explore — Reverse Explorative Modeling over the sign accumulator.

Session 297. Port 1 of the s296 gated list (knowledge/explorative-modeling.md
§XM-REVERSE-1). Forward-XM (s296) diversified the MODEL side (jitter) and was
refuted: deterministic teacher pairs are pre-resolved couplings, no per-pair
ambiguity. The s296 diagnosis: the conflict lives ACROSS pairs in the sign-vote
accumulator. Reverse-XM diversifies the DATA side — it explores WHICH pairs
vote per round (coverage-constrained, mode-seeking coalition selection).

The mechanism it targets
------------------------
`holographic_etch` accumulates per-batch sign votes: acc += sign(grad) over N
voting units, flips weights where |acc|/N > 0.6. CONTESTED weights — where units
disagree so the net washes to ~0 — never cross threshold and stay frozen forever.
Those are the multimodal weights. Averaging (baseline) = mass-covering blur.

Reverse-XM operationalization
-----------------------------
Per round r, per layer:
  1. per-unit sign-vote vectors V[b] in {-1,0,+1}^W (concatenated over 4 plates)
  2. mode-coherent coalition S_r: seed = least-covered unit (coverage driver);
     select the top f*nb units by SIGNED COSINE agreement to the seed.
  3. flip confident-majority WITHIN S_r only (|acc_S|/|S| > 0.6) = mode-commit.
  4. coverage: cov[b]++ for b in S_r; next seed = least-covered → every unit
     leads across rounds (the per-epoch coverage term).

Arms (x probe_counts {50,800}, >=3 init seeds each):
  baseline     all units vote every round (= s115 etch, no coalition)
  revxm        top-f agreement coalition + coverage-rotated seed  (TREATMENT)
  revxm_rand   random f-fraction coalition (SIZE-MATCHED NULL: isolates
               coherence vs mere subsetting)  <- load-bearing (G2)
  revxm_nocov  top-f coalition, FIXED seed (no coverage)          (isolates
               the coverage term)

Gates (frozen, see §XM-REVERSE-1):
  G1  revxm > baseline    (oracle-recovery %)
  G2  revxm > revxm_rand  (lambda yardstick: coherence, not subsetting)
  G3  contested-weight RESOLUTION fraction: of weights contested at round 0
      (|acc_all|/nb < 0.6), fraction driven to a committed flip, revxm vs base.

Reproducibility (s296 fixes, mandatory):
  - np.random.seed AND mx.random.seed set per arm x init (TernaryLinear init
    uses global np.random; nn.Linear uses mx.random).
  - integer seeds passed explicitly (NO salted hash()).
  - >=3 init seeds/arm; report mean +- std; --validate asserts bit-repro.

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mini_holo_crystal import extract_crystal
from mini_holo_d_sweep_v2 import (
    GDModel,
    HoloModel,
    _zero_plate_grads,
    eval_by_depth,
    eval_model,
    generate_batch,
    masked_ce_loss,
)
from mini_holo_distill import (
    distill_loss_single_layer,
    extract_teacher_features,
)

PLATE_NAMES = ["attn.k_plate", "attn.v_plate", "attn.o_plate", "ffn_plate"]
CRYSTAL_KEY = {"attn.k_plate": "k", "attn.v_plate": "v",
               "attn.o_plate": "o", "ffn_plate": "ffn"}
CONF_THRESHOLD = 0.6
CONTESTED_THRESHOLD = 0.6  # |acc_all|/nb < this  => contested at round 0


# ══════════════════════════════════════════════════════════════════════
# Plate access helpers
# ══════════════════════════════════════════════════════════════════════

def _get_plate(layer, pname):
    plate = layer
    for p in pname.split("."):
        plate = getattr(plate, p)
    return plate


def _get_grad(grads, pname):
    g = grads
    for p in pname.split("."):
        g = g[p]
    return g["weight"]


# ══════════════════════════════════════════════════════════════════════
# Per-unit vote computation (one sign-vote vector per feature batch)
# ══════════════════════════════════════════════════════════════════════

def compute_votes(layer, batches):
    """Return {pname: (nb, out, in) int8 sign votes} for one layer."""
    votes = {p: [] for p in PLATE_NAMES}
    for t_in, t_out in batches:
        def loss_fn(lyr, t_in=t_in, t_out=t_out):
            return distill_loss_single_layer(lyr, t_in, t_out)

        _, grads = nn.value_and_grad(layer, loss_fn)(layer)
        mx.eval(grads)
        for pname in PLATE_NAMES:
            g = _get_grad(grads, pname)
            mx.eval(g)
            votes[pname].append(np.sign(np.array(g)).astype(np.int8))
        del grads
    return {p: np.stack(votes[p], axis=0) for p in PLATE_NAMES}


def select_coalition(V_layer, cov, arm, frac, rng, fixed_seed=0):
    """Choose which units vote this round.

    V_layer: (nb, W) concatenated ternary votes across the layer's plates.
    Returns (selected_idx, seed_used).
    """
    nb = V_layer.shape[0]
    if arm == "baseline":
        return np.arange(nb), -1
    ksel = max(1, round(frac * nb))
    if arm == "revxm_nocov":
        seed = fixed_seed
    else:  # revxm, revxm_rand -> coverage-rotated seed (least covered)
        seed = int(np.argmin(cov))
    if arm == "revxm_rand":
        others = [b for b in range(nb) if b != seed]
        rng.shuffle(others)
        sel = np.array([seed, *others[: ksel - 1]], dtype=np.int64)
        return sel, seed
    # revxm / revxm_nocov: top-ksel by signed cosine to seed
    s = V_layer[seed].astype(np.float64)
    num = V_layer.astype(np.float64) @ s
    norms = np.sqrt((V_layer.astype(np.float64) ** 2).sum(axis=1))
    denom = norms * np.sqrt((s * s).sum()) + 1e-9
    cos = num / denom
    order = np.argsort(-cos)  # seed (cos=1) sorts first
    sel = order[:ksel].astype(np.int64)
    return sel, seed


# ══════════════════════════════════════════════════════════════════════
# Reverse-XM etch (baseline arm == s115 holographic_etch exactly)
# ══════════════════════════════════════════════════════════════════════

def reverse_etch(
    student: HoloModel,
    teacher_features: list,
    arm: str,
    frac: float,
    coalition_rng: np.random.RandomState,
    oracle_crystal: list,
    n_rounds: int = 8,
    max_depth: int = 4,
) -> tuple[list[dict], dict]:
    """Etch with coverage-constrained coalition voting.

    Only the plate-flip step differs across arms; beam training is identical
    (all units), so the sole treatment is WHICH units vote for sign flips.
    """
    n_layers = len(student.layers)
    log = []

    # G3 bookkeeping: round-0 contested set + initial signs per plate/layer.
    contested_masks = {}   # (li, pname) -> bool array
    init_signs = {}        # (li, pname) -> int8 array
    coverage = [np.zeros(len(teacher_features[li]), dtype=np.int64)
                for li in range(n_layers)]

    for round_idx in range(n_rounds):
        round_flips = 0
        for li in range(n_layers):
            layer = student.layers[li]
            batches = teacher_features[li]
            nb = len(batches)
            votes = compute_votes(layer, batches)

            # round-0: record contested set (all-unit accumulator) + init signs
            if round_idx == 0:
                for pname in PLATE_NAMES:
                    acc_all = votes[pname].astype(np.float64).sum(axis=0)
                    contested_masks[(li, pname)] = (
                        np.abs(acc_all) / nb < CONTESTED_THRESHOLD)
                    plate = _get_plate(layer, pname)
                    init_signs[(li, pname)] = (
                        np.sign(np.array(plate.weight)).astype(np.int8))

            # per-layer coalition on concatenated votes
            V_layer = np.concatenate(
                [votes[p].reshape(nb, -1) for p in PLATE_NAMES], axis=1)
            sel, _seed = select_coalition(
                V_layer, coverage[li], arm, frac, coalition_rng)
            coverage[li][sel] += 1

            for pname in PLATE_NAMES:
                plate = _get_plate(layer, pname)
                acc = votes[pname][sel].astype(np.float64).sum(axis=0)
                confidence = np.abs(acc) / len(sel)
                target_sign = np.sign(acc)
                current = np.sign(np.array(plate.weight)).astype(np.int8)
                should_flip = (
                    (confidence > CONF_THRESHOLD)
                    & (target_sign != 0)
                    & (target_sign != current))
                plate.weight = mx.array(
                    np.where(should_flip, target_sign, current)
                    .astype(np.float32))
                mx.eval(plate.weight)
                round_flips += int(should_flip.sum())

        # Beam training — identical across arms (all units, distill loss)
        beam_opt = optim.Adam(learning_rate=0.003)
        for beam_step in range(100):
            def full_loss(model, beam_step=beam_step):
                loss = mx.array(0.0)
                for li in range(n_layers):
                    t_i, t_o = teacher_features[li][
                        beam_step % len(teacher_features[li])]
                    s_o = model.layers[li](t_i)
                    diff = s_o - t_o
                    loss = loss + (diff * diff).mean()
                return loss

            loss_val, grads = nn.value_and_grad(student, full_loss)(student)
            mx.eval(loss_val, grads)
            _zero_plate_grads(grads, n_layers)
            student.update(beam_opt.apply_gradients(grads, student))
            mx.eval(student.parameters())
            del loss_val, grads
            if (beam_step + 1) % 25 == 0:
                mx.clear_cache()

        ev = eval_model(student, np.random.RandomState(999), max_depth=max_depth)
        log.append({"round": round_idx + 1, "flips": round_flips, **ev})
        print(f"      round {round_idx+1}: flips={round_flips:5d} "
              f"acc={ev['accuracy']:.1%}", flush=True)
        mx.clear_cache()

    # G3: contested-weight CORRECT-resolution toward the oracle crystal sign.
    #   contested   = weights with |acc_all|/nb < threshold at round 0
    #   at_oracle   = of contested, final sign == oracle crystal sign (PRIMARY)
    #   needs_fix   = of contested, init sign != oracle sign (were wrong)
    #   fixed       = of needs_fix, final sign == oracle sign (diagnostic)
    #   moved       = of contested, final sign != init sign (any-flip, legacy)
    total_contested = 0
    at_oracle = 0
    needs_fix = 0
    fixed = 0
    moved = 0
    for li in range(n_layers):
        layer = student.layers[li]
        for pname in PLATE_NAMES:
            mask = contested_masks[(li, pname)]
            final_sign = np.sign(np.array(
                _get_plate(layer, pname).weight)).astype(np.int8)
            oracle_sign = np.sign(
                oracle_crystal[li][CRYSTAL_KEY[pname]]).astype(np.int8)
            init_sign = init_signs[(li, pname)]
            total_contested += int(mask.sum())
            at_oracle += int((mask & (final_sign == oracle_sign)).sum())
            nf = mask & (init_sign != oracle_sign)
            needs_fix += int(nf.sum())
            fixed += int((nf & (final_sign == oracle_sign)).sum())
            moved += int((mask & (final_sign != init_sign)).sum())
    g3 = {
        "contested": total_contested,
        "at_oracle": at_oracle,
        "resolution_frac": (at_oracle / total_contested
                            if total_contested else 0.0),
        "needs_fix": needs_fix,
        "fixed_frac": (fixed / needs_fix if needs_fix else 0.0),
        "moved_frac": (moved / total_contested if total_contested else 0.0),
    }
    return log, g3


# ══════════════════════════════════════════════════════════════════════
# Per-arm pipeline: seed -> etch -> freeze -> GD
# ══════════════════════════════════════════════════════════════════════

def seed_all(seed: int):
    np.random.seed(seed)   # TernaryLinear init uses global np.random
    mx.random.seed(seed)   # nn.Linear / Embedding init uses mx.random


def run_arm(
    teacher_features: list, oracle_crystal: list,
    arm: str, frac: float, init_seed: int,
    n_probes: int, gd_steps: int, n_rounds: int,
    d_model: int = 48, n_layers: int = 3,
    batch_size: int = 32, lr: float = 0.003, max_depth: int = 4,
) -> dict:
    seed_all(init_seed)
    student = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(student.parameters())

    etch_log, g3 = reverse_etch(
        student, teacher_features, arm=arm, frac=frac,
        coalition_rng=np.random.RandomState(init_seed + 12345),
        oracle_crystal=oracle_crystal,
        n_rounds=n_rounds, max_depth=max_depth)

    for layer in student.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(student, masked_ce_loss)
    rng = np.random.RandomState(42)  # fixed task stream across arms
    gd_log = []
    for step in range(gd_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(student, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        student.update(optimizer.apply_gradients(grads, student))
        mx.eval(student.parameters())
        del loss_val, grads
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 1000 == 0:
            gd_log.append({"step": step + 1, **eval_model(
                student, np.random.RandomState(999), max_depth=max_depth)})

    final = eval_model(student, np.random.RandomState(999), max_depth=max_depth)
    depth = eval_by_depth(student, np.random.RandomState(999),
                          max_depth=max_depth)
    all_accs = ([e["accuracy"] for e in etch_log]
                + [e["accuracy"] for e in gd_log] + [final["accuracy"]])
    return {
        "arm": arm, "frac": frac, "init_seed": init_seed,
        "n_probes": n_probes,
        "best_acc": max(all_accs), "final_acc": final["accuracy"],
        "final_depth": depth, "g3": g3,
        "etch_log": etch_log, "gd_log": gd_log,
    }


# ══════════════════════════════════════════════════════════════════════
# Statistics
# ══════════════════════════════════════════════════════════════════════

def _paired_delta(a: list[float], b: list[float]) -> dict:
    """Paired delta a-b across matched init seeds; sign test + mean/std."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    d = a - b
    n = len(d)
    mean = float(d.mean())
    std = float(d.std(ddof=1)) if n > 1 else 0.0
    se = std / np.sqrt(n) if n > 1 else 0.0
    t = mean / se if se > 0 else 0.0
    wins = int((d > 0).sum())
    return {"mean_delta": mean, "std": std, "t": float(t),
            "n": n, "wins": wins, "per_seed": d.tolist()}


# ══════════════════════════════════════════════════════════════════════
# Validate — mechanics self-check (no verdict)
# ══════════════════════════════════════════════════════════════════════

def validate() -> None:
    print("=" * 60)
    print("  --validate : reverse-XM mechanics self-check")
    print("=" * 60)
    ok = True

    # 1. coalition selection: sizes + coherence + baseline-all
    rng = np.random.RandomState(0)
    nb, W = 10, 40
    V = rng.choice([-1, 0, 1], size=(nb, W)).astype(np.int8)
    cov = np.zeros(nb, dtype=np.int64)
    frac = 0.5
    sel_b, _ = select_coalition(V, cov, "baseline", frac, rng)
    assert len(sel_b) == nb, "baseline must select all units"
    sel_r, seed_r = select_coalition(V, cov, "revxm", frac, rng)
    sel_n, _ = select_coalition(V, cov, "revxm_rand", frac, rng)
    assert len(sel_r) == len(sel_n) == round(frac * nb), \
        "revxm and revxm_rand must be SIZE-MATCHED (G2 null validity)"
    # coherence: revxm coalition mean-agreement to seed > random coalition
    def mean_agree(sel, seed):
        s = V[seed].astype(np.float64)
        num = V[sel].astype(np.float64) @ s
        den = (np.sqrt((V[sel].astype(np.float64) ** 2).sum(1))
               * np.sqrt((s * s).sum()) + 1e-9)
        return float((num / den).mean())
    ag_r = mean_agree(sel_r, seed_r)
    ag_n = mean_agree(sel_n, seed_r)
    assert ag_r > ag_n, f"revxm must be more coherent ({ag_r:.3f}>{ag_n:.3f})"
    print(f"  [pass] coalition: baseline=all, sizes matched "
          f"({len(sel_r)}), coherence revxm {ag_r:.3f} > rand {ag_n:.3f}")

    # 2. coverage rotation: seed changes as coverage accumulates
    cov2 = np.zeros(nb, dtype=np.int64)
    seeds_seen = []
    for _ in range(4):
        sel, seed = select_coalition(V, cov2, "revxm", frac, rng)
        cov2[sel] += 1
        seeds_seen.append(seed)
    assert len(set(seeds_seen)) > 1, "coverage must rotate the seed"
    # nocov keeps fixed seed
    cov3 = np.zeros(nb, dtype=np.int64)
    nocov_seeds = []
    for _ in range(3):
        sel, seed = select_coalition(V, cov3, "revxm_nocov", frac, rng)
        cov3[sel] += 1
        nocov_seeds.append(seed)
    assert set(nocov_seeds) == {0}, "nocov must keep the fixed seed"
    print(f"  [pass] coverage: revxm rotates seeds {seeds_seen}; "
          f"nocov fixed {nocov_seeds}")

    # 3. bit-reproducibility: same seed -> identical etched plates
    seed_all(42)
    teacher = GDModel(d_model=48, n_layers=3)
    mx.eval(teacher.parameters())
    opt = optim.Adam(learning_rate=0.003)
    lg = nn.value_and_grad(teacher, masked_ce_loss)
    trng = np.random.RandomState(42)
    for _ in range(60):
        iid, tgt, msk = generate_batch(32, trng, max_depth=4)
        lv, gr = lg(teacher, iid, tgt, msk)
        mx.eval(lv, gr)
        teacher.update(opt.apply_gradients(gr, teacher))
        mx.eval(teacher.parameters())
    feats = extract_teacher_features(
        teacher, n_probes=48, batch_size=8, max_depth=4,
        rng=np.random.RandomState(777))
    crystal = extract_crystal(teacher)

    def etch_fingerprint(arm, seed):
        seed_all(seed)
        st = HoloModel(d_model=48, n_layers=3)
        mx.eval(st.parameters())
        _, g3 = reverse_etch(
            st, feats, arm=arm, frac=0.5,
            coalition_rng=np.random.RandomState(seed + 12345),
            oracle_crystal=crystal, n_rounds=3, max_depth=4)
        fp = np.concatenate([
            np.sign(np.array(_get_plate(layer, p).weight)).ravel()
            for layer in st.layers for p in PLATE_NAMES])
        return fp, g3

    fp1, g3a = etch_fingerprint("revxm", 7)
    fp2, _ = etch_fingerprint("revxm", 7)
    if not np.array_equal(fp1, fp2):
        ok = False
        print("  [FAIL] not bit-reproducible under fixed seed")
    else:
        print(f"  [pass] bit-reproducible (revxm seed=7); "
              f"G3 contested={g3a['contested']} "
              f"at_oracle={g3a['at_oracle']} "
              f"resolution_frac={g3a['resolution_frac']:.3f} "
              f"fixed_frac={g3a['fixed_frac']:.3f}")

    # 4. baseline differs from revxm (arms are distinct)
    fpb, _ = etch_fingerprint("baseline", 7)
    if np.array_equal(fp1, fpb):
        ok = False
        print("  [FAIL] baseline == revxm (no treatment effect on plates)")
    else:
        diff = int((fp1 != fpb).sum())
        print(f"  [pass] baseline != revxm (plate sign diff={diff})")

    print("=" * 60)
    print("  --validate ALL PASS" if ok else "  --validate FAILED")
    print("=" * 60)
    if not ok:
        raise SystemExit(1)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

ARMS = ["baseline", "revxm", "revxm_rand", "revxm_nocov"]


def train_oracle(gd_steps: int, d_model=48, n_layers=3, max_depth=4):
    seed_all(42)
    oracle = GDModel(d_model=d_model, n_layers=n_layers)
    mx.eval(oracle.parameters())
    opt = optim.Adam(learning_rate=0.003)
    lg = nn.value_and_grad(oracle, masked_ce_loss)
    rng = np.random.RandomState(42)
    for step in range(gd_steps):
        iid, tgt, msk = generate_batch(32, rng, max_depth=max_depth)
        lv, gr = lg(oracle, iid, tgt, msk)
        mx.eval(lv, gr)
        oracle.update(opt.apply_gradients(gr, oracle))
        mx.eval(oracle.parameters())
        del lv, gr
        if (step + 1) % 50 == 0:
            mx.clear_cache()
    return oracle


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--gd-steps", type=int, default=10500)
    ap.add_argument("--seeds", type=int, default=5,
                    help="init seeds per arm (>=3 for power)")
    ap.add_argument("--frac", type=float, default=0.5,
                    help="coalition fraction (frozen)")
    ap.add_argument("--n-rounds", type=int, default=8)
    ap.add_argument("--etch-batch", type=int, default=8,
                    help="probes per voting unit (smaller => more units)")
    ap.add_argument("--checkpoint-dir", type=str,
                    default="checkpoints/xm-reverse-explore")
    args = ap.parse_args()

    if args.validate:
        validate()
        return

    out = Path(args.checkpoint_dir)
    out.mkdir(parents=True, exist_ok=True)

    gd_steps = 300 if args.smoke else args.gd_steps
    probe_counts = [50] if args.smoke else [50, 800]
    n_seeds = 2 if args.smoke else args.seeds
    seeds = [1000 + i for i in range(n_seeds)]

    try:
        git_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        git_sha = "unknown"

    meta = {
        "run_id": f"xm-reverse-{'smoke' if args.smoke else 'full'}",
        "timestamp": datetime.now(UTC).isoformat(),
        "git_sha": git_sha,
        "d_model": 48, "n_layers": 3, "max_depth": 4,
        "gd_steps": gd_steps, "probe_counts": probe_counts,
        "arms": ARMS, "init_seeds": seeds, "frac": args.frac,
        "n_rounds": args.n_rounds, "etch_batch": args.etch_batch,
        "conf_threshold": CONF_THRESHOLD,
        "contested_threshold": CONTESTED_THRESHOLD,
        "preregistered": {
            "G1": "revxm > baseline (oracle-recovery %)",
            "G2": "revxm > revxm_rand (coherence, not subsetting)",
            "G3": "contested-weight resolution frac revxm > baseline",
            "verdicts": ["REVERSE-COMPOSES", "SUBSETTING-ARTIFACT",
                         "NO-RELIEF"],
        },
        "repro_fixes": ["np+mx seeded per arm", "integer seeds",
                        ">=3 init seeds", "bit-repro validated"],
    }
    results = {"meta": meta}

    print("=" * 70)
    print(f"  XM REVERSE-EXPLORE  ({meta['run_id']})")
    print(f"  arms={ARMS} probes={probe_counts} seeds={seeds} "
          f"frac={args.frac} rounds={args.n_rounds} gd={gd_steps}")
    print("=" * 70, flush=True)

    print(f"\n  [oracle] training GD teacher ({gd_steps} steps)...", flush=True)
    t0 = time.time()
    oracle = train_oracle(gd_steps)
    oracle_crystal = extract_crystal(oracle)
    oracle_eval = eval_model(oracle, np.random.RandomState(999), max_depth=4)
    print(f"    oracle acc={oracle_eval['accuracy']:.1%} "
          f"({time.time()-t0:.1f}s)", flush=True)
    results["oracle"] = {
        "acc": oracle_eval["accuracy"],
        "depth": eval_by_depth(oracle, np.random.RandomState(999), max_depth=4),
    }

    for n_probes in probe_counts:
        # Teacher features shared across ALL arms and seeds for this probe count
        feats = extract_teacher_features(
            oracle, n_probes=n_probes, batch_size=args.etch_batch,
            max_depth=4, rng=np.random.RandomState(777))
        n_units = len(feats[0])
        print(f"\n  probes={n_probes}: {n_units} voting units "
              f"(etch_batch={args.etch_batch})", flush=True)
        for arm in ARMS:
            for init_seed in seeds:
                key = f"{arm}_p{n_probes}_s{init_seed}"
                t0 = time.time()
                r = run_arm(feats, oracle_crystal, arm, args.frac, init_seed,
                            n_probes, gd_steps, args.n_rounds)
                r["seconds"] = time.time() - t0
                r["n_units"] = n_units
                results[key] = r
                pct = (r["best_acc"] / oracle_eval["accuracy"] * 100
                       if oracle_eval["accuracy"] else 0)
                print(f"    [{key}] best={r['best_acc']:.1%} "
                      f"({pct:.1f}%%oracle) g3={r['g3']['resolution_frac']:.3f} "
                      f"[{r['seconds']:.0f}s]", flush=True)
                with open(out / "results.json", "w") as f:
                    json.dump(results, f, indent=2, default=str)

    # ── Gate scoring (advisory numbers; verdict scored on frozen gates) ──
    print(f"\n{'═' * 70}\n  GATE SCORING (oracle={oracle_eval['accuracy']:.1%})")
    scoring = {}
    for n_probes in probe_counts:
        def recov(arm, n_probes=n_probes):
            return [results[f"{arm}_p{n_probes}_s{s}"]["best_acc"]
                    / oracle_eval["accuracy"] for s in seeds]

        def g3frac(arm, n_probes=n_probes):
            return [results[f"{arm}_p{n_probes}_s{s}"]["g3"]["resolution_frac"]
                    for s in seeds]

        g1 = _paired_delta(recov("revxm"), recov("baseline"))
        g2 = _paired_delta(recov("revxm"), recov("revxm_rand"))
        g3 = _paired_delta(g3frac("revxm"), g3frac("baseline"))
        scoring[f"p{n_probes}"] = {"G1": g1, "G2": g2, "G3": g3}
        print(f"\n  probes={n_probes}:")
        for name, g in [("G1 revxm-base", g1), ("G2 revxm-rand", g2),
                        ("G3 contested", g3)]:
            print(f"    {name:>16}: Δ={g['mean_delta']:+.4f} "
                  f"±{g['std']:.4f} t={g['t']:+.2f} "
                  f"wins={g['wins']}/{g['n']}")
    results["scoring"] = scoring

    with open(out / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  saved -> {out}/results.json", flush=True)


if __name__ == "__main__":
    main()
