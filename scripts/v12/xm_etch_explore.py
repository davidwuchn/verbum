"""XM Etch-Explore — Forward Explorative Modeling on the holographic etch.

Session 296. Tests whether best-of-K exploration (arXiv:2607.27372) improves
holographic distillation (s115 harness, mini_holo_distill.py).

Frame: the s115 etch loss ||teacher_out - student_out||^2 is a direct
regressor — per-prediction generative expressivity M=1, the exact case
Explorative Modeling attacks. Exploration here = K jittered beam angles
per probe; etch only the candidate whose output best matches the teacher
(coupling search, the analog of the paper's K-candidate-noise diffusion
hybrid).

PRE-REGISTERED PREDICTIONS (frozen before first full run):
  P1: oracle-recovery%% monotone in K in {1,2,5,10} at fixed sigma.
  P2: the 800-probe regime gains MORE from exploration than the 50-probe
      regime (relief of accumulator tug-of-war -> the s115 50-beats-800
      anomaly narrows or inverts).
  P3: gains concentrate at depth-4 compositional probes.
  NULLS: (a) jitter-only control K=1 sigma=0.1 isolates noise-exposure;
         (b) shuffled-winner K=5 sigma=0.1 random-selection isolates
         selection. XM claim requires best-of-K > both nulls.

Arms (x probe_counts {50, 800}):
  K1_s0    K=1  sigma=0.0  best    <- exact s115 baseline
  K1_j     K=1  sigma=0.1  best    <- jitter-only control
  K2       K=2  sigma=0.1  best
  K5       K=5  sigma=0.1  best
  K10      K=10 sigma=0.1  best
  K5_null  K=5  sigma=0.1  random  <- shuffled-winner null

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
from mini_holo_d_sweep_v2 import (
    GDModel,
    HoloModel,
    _zero_plate_grads,
    eval_by_depth,
    eval_model,
    generate_batch,
    masked_ce_loss,
)
from mini_holo_distill import extract_teacher_features

# ══════════════════════════════════════════════════════════════════════
# Explorative distillation loss
# ══════════════════════════════════════════════════════════════════════

def explore_layer_loss(
    layer,
    t_in: mx.array,
    t_out: mx.array,
    noises: list,          # K noise arrays (or [None] when sigma=0)
    mode: str,             # "best" | "random"
    null_idx: np.ndarray | None,  # (B,) winner indices for mode="random"
) -> mx.array:
    """Best-of-K distillation loss, per-sequence winner (Forward XM).

    Candidates: y_k = layer(t_in + noise_k). Per-sequence MSE against
    t_out gives a (K, B) matrix; winner per sequence b is min_k (mode
    "best") or a random k (mode "random", shuffled-winner null).
    Gradient flows only through winners.
    """
    per_k = []
    for noise in noises:
        x = t_in if noise is None else t_in + noise
        y = layer(x)
        diff = y - t_out
        per_b = (diff * diff).mean(axis=(1, 2))  # (B,)
        per_k.append(per_b)
    stacked = mx.stack(per_k, axis=0)  # (K, B)
    if len(noises) == 1:
        return stacked.mean()
    if mode == "best":
        return mx.min(stacked, axis=0).mean()
    # shuffled-winner null: one-hot selection, grad-safe
    onehot = np.zeros((len(noises), stacked.shape[1]), dtype=np.float32)
    onehot[null_idx, np.arange(stacked.shape[1])] = 1.0
    return (stacked * mx.array(onehot)).sum(axis=0).mean()


def make_noises(
    t_in: mx.array, k: int, sigma: float, rng: np.random.RandomState,
) -> tuple[list, np.ndarray]:
    """Draw K fresh input jitters scaled to sigma * std(t_in)."""
    if sigma <= 0.0:
        return [None] * k, rng.randint(0, k, size=t_in.shape[0])
    scale = sigma * float(mx.sqrt((t_in * t_in).mean()))
    noises = [
        mx.array(rng.standard_normal(t_in.shape).astype(np.float32)) * scale
        for _ in range(k)
    ]
    return noises, rng.randint(0, k, size=t_in.shape[0])


# ══════════════════════════════════════════════════════════════════════
# Explorative holographic etch (s115 holographic_etch + exploration)
# ══════════════════════════════════════════════════════════════════════

def holographic_etch_explore(
    student: HoloModel,
    teacher_features: list,
    k: int,
    sigma: float,
    mode: str,
    jitter_rng: np.random.RandomState,
    n_rounds: int = 5,
    confidence_threshold: float = 0.6,
    max_depth: int = 4,
) -> list[dict]:
    """s115 etch with Forward-XM exploration in plate votes AND beam loss.

    K=1, sigma=0 reproduces the s115 baseline etch exactly (single
    candidate, no jitter, mean loss).
    """
    n_layers = len(student.layers)
    log = []
    plate_names = ["attn.k_plate", "attn.v_plate", "attn.o_plate", "ffn_plate"]

    for round_idx in range(n_rounds):
        round_total_flips = 0

        for layer_idx in range(n_layers):
            layer = student.layers[layer_idx]
            batches = teacher_features[layer_idx]
            n_batches = len(batches)

            accumulators = {}
            for pname in plate_names:
                plate = layer
                for p in pname.split("."):
                    plate = getattr(plate, p)
                accumulators[pname] = np.zeros(
                    (plate.out_features, plate.in_features), dtype=np.float64)

            for t_in, t_out in batches:
                noises, null_idx = make_noises(t_in, k, sigma, jitter_rng)

                def loss_fn(lyr, t_in=t_in, t_out=t_out,
                            noises=noises, null_idx=null_idx):
                    return explore_layer_loss(
                        lyr, t_in, t_out, noises, mode, null_idx)

                loss_val, grads = nn.value_and_grad(
                    student.layers[layer_idx], loss_fn)(
                    student.layers[layer_idx])
                mx.eval(loss_val, grads)

                for pname in plate_names:
                    g = grads
                    for p in pname.split("."):
                        g = g[p]
                    g = g["weight"]
                    mx.eval(g)
                    accumulators[pname] += np.sign(np.array(g))
                del loss_val, grads

            layer_flips = 0
            for pname in plate_names:
                plate = layer
                for p in pname.split("."):
                    plate = getattr(plate, p)
                acc = accumulators[pname]
                confidence = np.abs(acc) / n_batches
                target_sign = np.sign(acc)
                current = np.sign(np.array(plate.weight)).astype(np.int8)
                should_flip = (
                    (confidence > confidence_threshold)
                    & (target_sign != 0)
                    & (target_sign != current)
                )
                plate.weight = mx.array(
                    np.where(should_flip, target_sign, current)
                    .astype(np.float32))
                mx.eval(plate.weight)
                layer_flips += int(should_flip.sum())
            round_total_flips += layer_flips

        # Beam training with the same explorative loss
        beam_optimizer = optim.Adam(learning_rate=0.003)
        for beam_step in range(100):
            # fresh jitters per step, shared across layers for simplicity
            step_draws = [
                make_noises(teacher_features[li][
                    beam_step % len(teacher_features[li])][0],
                    k, sigma, jitter_rng)
                for li in range(n_layers)
            ]

            def full_loss(model, beam_step=beam_step, step_draws=step_draws):
                loss = mx.array(0.0)
                for li in range(n_layers):
                    t_i, t_o = teacher_features[li][
                        beam_step % len(teacher_features[li])]
                    noises_li, null_li = step_draws[li]
                    loss = loss + explore_layer_loss(
                        model.layers[li], t_i, t_o, noises_li, mode, null_li)
                return loss

            loss_val, grads = nn.value_and_grad(student, full_loss)(student)
            mx.eval(loss_val, grads)
            _zero_plate_grads(grads, n_layers)
            student.update(beam_optimizer.apply_gradients(grads, student))
            mx.eval(student.parameters())
            del loss_val, grads
            if (beam_step + 1) % 25 == 0:
                mx.clear_cache()

        ev = eval_model(student, np.random.RandomState(999),
                        max_depth=max_depth)
        log.append({"round": round_idx + 1, "flips": round_total_flips, **ev})
        print(f"      round {round_idx+1}: flips={round_total_flips:5d} "
              f"acc={ev['accuracy']:.1%}", flush=True)
        mx.clear_cache()

    return log


# ══════════════════════════════════════════════════════════════════════
# Per-arm pipeline: etch-explore + freeze + GD
# ══════════════════════════════════════════════════════════════════════

def run_arm(
    teacher: GDModel,
    arm: str, k: int, sigma: float, mode: str,
    n_probes: int, gd_steps: int,
    d_model: int = 48, n_layers: int = 3,
    batch_size: int = 32, lr: float = 0.003, max_depth: int = 4,
) -> dict:
    features = extract_teacher_features(
        teacher, n_probes=n_probes, batch_size=batch_size,
        max_depth=max_depth, rng=np.random.RandomState(777))

    student = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(student.parameters())

    jitter_seed = abs(hash((arm, n_probes))) % (2**31)
    etch_log = holographic_etch_explore(
        student, features, k=k, sigma=sigma, mode=mode,
        jitter_rng=np.random.RandomState(jitter_seed),
        n_rounds=5, max_depth=max_depth)

    for layer in student.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(student, masked_ce_loss)
    rng = np.random.RandomState(42)
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

    final = eval_model(student, np.random.RandomState(999),
                       max_depth=max_depth)
    depth = eval_by_depth(student, np.random.RandomState(999),
                          max_depth=max_depth)
    all_accs = ([e["accuracy"] for e in etch_log]
                + [e["accuracy"] for e in gd_log] + [final["accuracy"]])
    return {
        "arm": arm, "k": k, "sigma": sigma, "mode": mode,
        "n_probes": n_probes, "jitter_seed": jitter_seed,
        "best_acc": max(all_accs), "final_acc": final["accuracy"],
        "final_depth": depth, "etch_log": etch_log, "gd_log": gd_log,
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

ARMS = [
    # (name, K, sigma, mode)
    ("K1_s0", 1, 0.0, "best"),     # s115 baseline
    ("K1_j", 1, 0.1, "best"),      # jitter-only control
    ("K2", 2, 0.1, "best"),
    ("K5", 5, 0.1, "best"),
    ("K10", 10, 0.1, "best"),
    ("K5_null", 5, 0.1, "random"),  # shuffled-winner null
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="tiny run to validate mechanics + measure step rate")
    ap.add_argument("--gd-steps", type=int, default=10500)
    ap.add_argument("--checkpoint-dir", type=str,
                    default="checkpoints/xm-etch-explore")
    args = ap.parse_args()

    out = Path(args.checkpoint_dir)
    out.mkdir(parents=True, exist_ok=True)

    gd_steps = 300 if args.smoke else args.gd_steps
    probe_counts = [50] if args.smoke else [50, 800]
    arms = [ARMS[0], ARMS[3]] if args.smoke else ARMS

    try:
        git_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        git_sha = "unknown"

    meta = {
        "run_id": f"xm-etch-explore-{'smoke' if args.smoke else 'full'}",
        "timestamp": datetime.now(UTC).isoformat(),
        "git_sha": git_sha,
        "d_model": 48, "n_layers": 3, "max_depth": 4,
        "gd_steps": gd_steps, "probe_counts": probe_counts,
        "arms": [a[0] for a in arms],
        "seeds": {"teacher_gd": 42, "features": 777, "eval": 999},
        "preregistered": ["P1 monotone in K", "P2 800>50 gains",
                          "P3 depth-4 concentration",
                          "nulls: K1_j jitter-only, K5_null shuffled-winner"],
    }
    results = {"meta": meta}

    print("=" * 70)
    print(f"  XM ETCH-EXPLORE  ({meta['run_id']})")
    print(f"  arms={[a[0] for a in arms]} probes={probe_counts} "
          f"gd={gd_steps}")
    print("=" * 70, flush=True)

    # Oracle teacher (once, shared)
    print(f"\n  [oracle] training GD teacher ({gd_steps} steps)...",
          flush=True)
    t0 = time.time()
    oracle = GDModel(d_model=48, n_layers=3)
    mx.eval(oracle.parameters())
    optimizer = optim.Adam(learning_rate=0.003)
    loss_and_grad = nn.value_and_grad(oracle, masked_ce_loss)
    rng = np.random.RandomState(42)
    for step in range(gd_steps):
        input_ids, targets, mask = generate_batch(32, rng, max_depth=4)
        loss_val, grads = loss_and_grad(oracle, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        oracle.update(optimizer.apply_gradients(grads, oracle))
        mx.eval(oracle.parameters())
        del loss_val, grads
        if (step + 1) % 50 == 0:
            mx.clear_cache()
    oracle_eval = eval_model(oracle, np.random.RandomState(999), max_depth=4)
    oracle_dt = time.time() - t0
    print(f"    oracle acc={oracle_eval['accuracy']:.1%} "
          f"({oracle_dt:.1f}s, {gd_steps/oracle_dt:.0f} steps/s)", flush=True)
    results["oracle"] = {
        "acc": oracle_eval["accuracy"],
        "depth": eval_by_depth(oracle, np.random.RandomState(999),
                               max_depth=4),
        "train_seconds": oracle_dt,
    }

    # Arms
    for n_probes in probe_counts:
        for arm, k, sigma, mode in arms:
            key = f"{arm}_p{n_probes}"
            print(f"\n  [{key}] K={k} sigma={sigma} mode={mode} "
                  f"probes={n_probes}", flush=True)
            t0 = time.time()
            r = run_arm(oracle, arm, k, sigma, mode, n_probes, gd_steps)
            r["seconds"] = time.time() - t0
            results[key] = r
            pct = (r["best_acc"] / oracle_eval["accuracy"] * 100
                   if oracle_eval["accuracy"] else 0)
            print(f"    best={r['best_acc']:.1%} ({pct:.1f}% of oracle) "
                  f"[{r['seconds']:.0f}s]", flush=True)
            with open(out / "results.json", "w") as f:
                json.dump(results, f, indent=2, default=str)

    # Summary
    print(f"\n{'═' * 70}\n  SUMMARY (oracle={oracle_eval['accuracy']:.1%})")
    print(f"  {'arm':>16} {'probes':>7} {'best':>7} {'%oracle':>8} {'d4':>6}")
    for n_probes in probe_counts:
        for arm, *_ in arms:
            r = results[f"{arm}_p{n_probes}"]
            fd = r["final_depth"]
            d4 = fd.get(4, fd.get("4", 0))
            if isinstance(d4, dict):
                d4 = d4.get("accuracy", 0)
            pct = r["best_acc"] / oracle_eval["accuracy"] * 100
            print(f"  {arm:>16} {n_probes:>7} {r['best_acc']:>6.1%} "
                  f"{pct:>7.1f}% {d4:>5.1%}")

    with open(out / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  saved -> {out}/results.json", flush=True)


if __name__ == "__main__":
    main()
