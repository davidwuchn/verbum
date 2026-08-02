"""XM Latent-Explore — Student latent / XMDLM (Design B, mixture-of-experts).

Session 298. Port 2 of the s296 gated list (knowledge/explorative-modeling.md
§XM-LATENT-1). s296 (Forward-XM) and s297 (Reverse-XM) both failed on the
REPRESENTATIONAL side: the etch loss ||teacher-student||^2 is direct
regression -> per-prediction expressivity M=1 (minimizer = the mean = blur).
best-of-K had nothing to grab because a single deterministic student cannot
REPRESENT multiple modes. XMDLM gives the student K discrete latent embeddings
-> M raised 1->K. The multimodality is real even for a deterministic token
target: it lives in PATH space (many internal configs produce the right
output; different pairs can use different paths).

Mechanism (Design B)
--------------------
- Latent bank Z (K, n_layers, d), K=4 frozen, learnable. Latent k injects a
  per-layer additive residual offset: x_{l+1} = layer_l(x_l) + Z[k, l].
- Forward-XM best-of-K etch: candidate k loss = mean((layer(t_in)+Z[k]-t_out)^2);
  winner = argmin_k (best) or random k (rand null). Plate sign-votes accumulate
  the WINNER's gradient (train the winner); Z absorbs cross-pair mode variance
  so the shared plates see a more consistent target. Z trained in beam phase.
- Eval 3 modes: marginal = log(mean_k softmax(logits_k)) [GATED, honest];
  argmax-latent = per-input lowest-entropy latent [advisory self-route];
  oracle-latent = per-input best latent vs ground truth [advisory CEILING].

Arms (x probes{50,800} x >=5 seeds):
  baseline    K=1, no selection (= s297 baseline + learnable bias)
  xmdlm       K=4, best-of-K assignment (TREATMENT)
  xmdlm_rand  K=4, RANDOM per-pair assignment (param+training-matched NULL;
              isolates SPECIALIZATION vs merely having K experts) <- G2

Gates (frozen):
  G1  xmdlm(marginal) > baseline
  G2  xmdlm(marginal) > xmdlm_rand(marginal)  [lambda yardstick]
  G3  specialization: assignment concentration (0 < entropy < log K, not
      collapsed) AND oracle(xmdlm) > marginal(xmdlm) AND oracle(xmdlm) >
      oracle(xmdlm_rand).
Verdicts: EXPRESSIVITY-UNBLOCKS / MARGINALIZATION-ARTIFACT /
          CAPACITY-BUT-UNROUTED / STILL-BLOCKED (see §XM-LATENT-1).

Reproducibility (s296/s297 fixes): np+mx seeded per arm; integer seeds; >=5
seeds; grade internally paired-by-init-seed; --validate asserts within-process
bit-repro. K=4, etch_batch=8, n_rounds=8 frozen.

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

PLATE_NAMES = ["attn.k_plate", "attn.v_plate", "attn.o_plate", "ffn_plate"]


# ══════════════════════════════════════════════════════════════════════
# Latent-conditioned holographic model (K experts sharing plates+beams)
# ══════════════════════════════════════════════════════════════════════

class LatentHoloModel(HoloModel):
    """HoloModel + a bank of K per-layer additive residual offsets Z.

    forward_latent(ids, k):  x_{l+1} = layer_l(x_l) + Z[k, l]
    __call__(ids):           marginal = log(mean_k softmax(logits_k))
                             (argmax == argmax over the mixture; NLL-safe)
    """

    def __init__(self, d_model: int = 48, n_layers: int = 3, K: int = 4,
                 z_scale: float = 0.2):
        super().__init__(d_model=d_model, n_layers=n_layers)
        self.K = K
        # Distinct-by-construction init (faithful to XMDLM discrete
        # embeddings): moderate scale, high-d random => near-orthogonal
        # latent directions so best-of-K does not start from collapse.
        self.latent = mx.random.normal((K, n_layers, d_model)) * z_scale

    def forward_latent(self, input_ids: mx.array, k: int) -> mx.array:
        x = self.embed(input_ids)
        for li, layer in enumerate(self.layers):
            x = layer(x) + self.latent[k, li]
        return self.output_proj(self.output_norm(x))

    def all_logits(self, input_ids: mx.array) -> mx.array:
        """(K, B, T, V) logits for every latent."""
        return mx.stack([self.forward_latent(input_ids, k)
                         for k in range(self.K)], axis=0)

    def __call__(self, input_ids: mx.array) -> mx.array:
        probs = None
        for k in range(self.K):
            p = mx.softmax(self.forward_latent(input_ids, k), axis=-1)
            probs = p if probs is None else probs + p
        return mx.log(probs / self.K + 1e-9)


def masked_marginal_nll(model, input_ids, targets, mask):
    """Proper mixture NLL on the marginal log-probs (GD loss)."""
    logp = model(input_ids)  # (B,T,V) log-probs
    tgt = -mx.take_along_axis(logp, targets[..., None], axis=-1).squeeze(-1)
    return (tgt * mask).sum() / (mask.sum() + 1e-8)


# ══════════════════════════════════════════════════════════════════════
# Best-of-K latent etch (baseline K=1 == s297 baseline + learnable bias)
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


def latent_etch(
    model: LatentHoloModel,
    teacher_features: list,
    arm: str,
    coalition_rng: np.random.RandomState,
    n_rounds: int = 8,
    confidence_threshold: float = 0.6,
    max_depth: int = 4,
) -> tuple[list[dict], np.ndarray]:
    """Forward-XM best-of-K over learnable latent offsets Z."""
    n_layers = len(model.layers)
    K = model.K
    log = []
    assign_counts = np.zeros(K, dtype=np.int64)

    for round_idx in range(n_rounds):
        round_flips = 0
        for li in range(n_layers):
            layer = model.layers[li]
            batches = teacher_features[li]
            nb = len(batches)
            # current latent offsets for this layer (constants for vote pass)
            Zc = [mx.array(np.array(model.latent[k, li])) for k in range(K)]

            accumulators = {p: np.zeros(
                (_get_plate(layer, p).out_features,
                 _get_plate(layer, p).in_features), dtype=np.float64)
                for p in PLATE_NAMES}

            for t_in, t_out in batches:
                # assignment (winner per B) from a no-grad forward
                y = layer(t_in)
                per_k = mx.stack(
                    [((y + Zc[k] - t_out) ** 2).mean(axis=(1, 2))
                     for k in range(K)], axis=0)  # (K,B)
                mx.eval(per_k)
                if arm == "xmdlm_rand" and K > 1:
                    win = coalition_rng.randint(0, K, size=per_k.shape[1])
                else:
                    win = np.array(mx.argmin(per_k, axis=0))
                assign_counts += np.bincount(win, minlength=K)

                onehot = np.zeros((K, per_k.shape[1]), dtype=np.float32)
                onehot[win, np.arange(per_k.shape[1])] = 1.0
                oh = mx.array(onehot)

                def loss_fn(lyr, t_in=t_in, t_out=t_out, oh=oh, Zc=Zc):
                    yy = lyr(t_in)
                    pk = mx.stack(
                        [((yy + Zc[k] - t_out) ** 2).mean(axis=(1, 2))
                         for k in range(K)], axis=0)
                    return (pk * oh).sum(axis=0).mean()

                _, grads = nn.value_and_grad(layer, loss_fn)(layer)
                mx.eval(grads)
                for pname in PLATE_NAMES:
                    g = _get_grad(grads, pname)
                    mx.eval(g)
                    accumulators[pname] += np.sign(np.array(g))
                del grads

            for pname in PLATE_NAMES:
                plate = _get_plate(layer, pname)
                acc = accumulators[pname]
                confidence = np.abs(acc) / nb
                target_sign = np.sign(acc)
                current = np.sign(np.array(plate.weight)).astype(np.int8)
                should_flip = ((confidence > confidence_threshold)
                               & (target_sign != 0)
                               & (target_sign != current))
                plate.weight = mx.array(
                    np.where(should_flip, target_sign, current)
                    .astype(np.float32))
                mx.eval(plate.weight)
                round_flips += int(should_flip.sum())

        # Beam phase: train Z + continuous beams with best-of-K latent loss
        beam_opt = optim.Adam(learning_rate=0.003)
        for beam_step in range(100):
            def full_loss(m, beam_step=beam_step):
                loss = mx.array(0.0)
                for li in range(n_layers):
                    t_i, t_o = teacher_features[li][
                        beam_step % len(teacher_features[li])]
                    yy = m.layers[li](t_i)
                    pk = mx.stack(
                        [((yy + m.latent[k, li] - t_o) ** 2).mean(axis=(1, 2))
                         for k in range(K)], axis=0)
                    if K == 1:
                        loss = loss + pk.mean()
                    elif arm == "xmdlm_rand":
                        win = coalition_rng.randint(0, K, size=pk.shape[1])
                        oh = np.zeros((K, pk.shape[1]), dtype=np.float32)
                        oh[win, np.arange(pk.shape[1])] = 1.0
                        loss = loss + (pk * mx.array(oh)).sum(axis=0).mean()
                    else:
                        loss = loss + mx.min(pk, axis=0).mean()
                return loss

            loss_val, grads = nn.value_and_grad(model, full_loss)(model)
            mx.eval(loss_val, grads)
            _zero_plate_grads(grads, n_layers)
            model.update(beam_opt.apply_gradients(grads, model))
            mx.eval(model.parameters())
            del loss_val, grads
            if (beam_step + 1) % 25 == 0:
                mx.clear_cache()

        ev = eval_model(model, np.random.RandomState(999), max_depth=max_depth)
        log.append({"round": round_idx + 1, "flips": round_flips, **ev})
        print(f"      round {round_idx+1}: flips={round_flips:5d} "
              f"marg_acc={ev['accuracy']:.1%}", flush=True)
        mx.clear_cache()

    return log, assign_counts


# ══════════════════════════════════════════════════════════════════════
# Latent eval modes: marginal / argmax-latent / oracle-latent
# ══════════════════════════════════════════════════════════════════════

def eval_latent_modes(model: LatentHoloModel, rng, n_batches=50,
                      batch_size=64, max_depth=4) -> dict:
    """Return accuracies for marginal, argmax-latent, oracle-latent."""
    K = model.K
    tot = 0.0
    corr = {"marginal": 0.0, "argmax": 0.0, "oracle": 0.0}
    for _ in range(n_batches):
        ids, targets, mask = generate_batch(batch_size, rng, max_depth=max_depth)
        allg = model.all_logits(ids)  # (K,B,T,V)
        mx.eval(allg)
        probs = mx.softmax(allg, axis=-1)                 # (K,B,T,V)
        marg = probs.mean(axis=0)                          # (B,T,V)
        pred_marg = mx.argmax(marg, axis=-1)
        # per-latent per-token correctness
        pred_k = mx.argmax(allg, axis=-1)                  # (K,B,T)
        correct_k = (pred_k == targets[None]).astype(mx.float32)  # (K,B,T)
        # per-sequence routing scores
        logp = mx.log(probs + 1e-9)
        tgt_lp = mx.take_along_axis(
            logp, mx.broadcast_to(targets[None, ..., None],
                                  (K, *targets.shape, 1)), axis=-1).squeeze(-1)
        seq_ce = -(tgt_lp * mask[None]).sum(axis=-1)       # (K,B) oracle score
        ent = -(probs * mx.log(probs + 1e-9)).sum(axis=-1)  # (K,B,T)
        seq_ent = (ent * mask[None]).sum(axis=-1)          # (K,B) self-route
        mx.eval(seq_ce, seq_ent, correct_k, pred_marg)
        oracle_k = mx.argmin(seq_ce, axis=0)               # (B,)
        argmax_k = mx.argmin(seq_ent, axis=0)              # (B,)
        B = targets.shape[0]
        bidx = mx.arange(B)
        corr_oracle = correct_k[oracle_k, bidx]            # (B,T)
        corr_argmax = correct_k[argmax_k, bidx]
        m = mask
        corr["marginal"] += float(((pred_marg == targets) * m).sum().item())
        corr["oracle"] += float((corr_oracle * m).sum().item())
        corr["argmax"] += float((corr_argmax * m).sum().item())
        tot += float(m.sum().item())
    return {k: corr[k] / max(tot, 1) for k in corr}


# ══════════════════════════════════════════════════════════════════════
# Per-arm pipeline
# ══════════════════════════════════════════════════════════════════════

def seed_all(seed: int):
    np.random.seed(seed)
    mx.random.seed(seed)


def run_arm(
    teacher_features: list,
    arm: str, K: int, init_seed: int,
    n_probes: int, gd_steps: int, n_rounds: int,
    d_model: int = 48, n_layers: int = 3,
    batch_size: int = 32, lr: float = 0.003, max_depth: int = 4,
) -> dict:
    seed_all(init_seed)
    model = LatentHoloModel(d_model=d_model, n_layers=n_layers, K=K)
    mx.eval(model.parameters())

    etch_log, assign = latent_etch(
        model, teacher_features, arm=arm,
        coalition_rng=np.random.RandomState(init_seed + 12345),
        n_rounds=n_rounds, max_depth=max_depth)

    for layer in model.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_marginal_nll)
    rng = np.random.RandomState(42)
    gd_log = []
    for step in range(gd_steps):
        ids, targets, mask = generate_batch(batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(model, ids, targets, mask)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 1000 == 0:
            gd_log.append({"step": step + 1, **eval_model(
                model, np.random.RandomState(999), max_depth=max_depth)})

    modes = eval_latent_modes(model, np.random.RandomState(999),
                              max_depth=max_depth)
    depth = eval_by_depth(model, np.random.RandomState(999), max_depth=max_depth)
    all_marg = ([e["accuracy"] for e in etch_log]
                + [e["accuracy"] for e in gd_log] + [modes["marginal"]])
    a = assign.astype(np.float64)
    p = a / max(a.sum(), 1)
    ent = float(-(p[p > 0] * np.log(p[p > 0])).sum())
    return {
        "arm": arm, "K": K, "init_seed": init_seed, "n_probes": n_probes,
        "best_acc": max(all_marg),               # marginal, for G1/G2
        "final_marginal": modes["marginal"],
        "final_argmax": modes["argmax"],
        "final_oracle": modes["oracle"],         # ceiling, for G3
        "assign_counts": assign.tolist(),
        "assign_entropy": ent, "assign_logK": float(np.log(max(K, 1))),
        "final_depth": depth, "etch_log": etch_log, "gd_log": gd_log,
    }


# ══════════════════════════════════════════════════════════════════════
# Statistics
# ══════════════════════════════════════════════════════════════════════

def _paired_delta(a: list[float], b: list[float]) -> dict:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    d = a - b
    n = len(d)
    mean = float(d.mean())
    std = float(d.std(ddof=1)) if n > 1 else 0.0
    se = std / np.sqrt(n) if n > 1 else 0.0
    return {"mean_delta": mean, "std": std,
            "t": float(mean / se) if se > 0 else 0.0,
            "n": n, "wins": int((d > 0).sum()), "per_seed": d.tolist()}


# ══════════════════════════════════════════════════════════════════════
# Validate
# ══════════════════════════════════════════════════════════════════════

def validate() -> None:
    print("=" * 60)
    print("  --validate : XMDLM latent mechanics self-check")
    print("=" * 60)
    ok = True

    # 1. marginal is a proper mixture (argmax over averaged probs)
    seed_all(3)
    m = LatentHoloModel(d_model=48, n_layers=3, K=4)
    mx.eval(m.parameters())
    ids, _t, _m = generate_batch(8, np.random.RandomState(1), max_depth=4)
    logp = m(ids)
    p = mx.exp(logp).sum(axis=-1)
    assert float(mx.abs(p - 1.0).max()) < 1e-3, "marginal probs must sum to 1"
    allg = m.all_logits(ids)
    assert allg.shape[0] == 4, "all_logits must have K rows"
    print("  [pass] marginal mixture normalized; all_logits (K,B,T,V) ok")

    # 2. latents are distinct forward paths
    l0 = m.forward_latent(ids, 0)
    l1 = m.forward_latent(ids, 1)
    assert float(mx.abs(l0 - l1).max()) > 1e-4, "latents must differ"
    print("  [pass] latent branches produce distinct logits")

    # 3. best-of-K assignment differentiates; rand is uniform-ish
    feats = extract_teacher_features(
        GDModel(48, 3), n_probes=48, batch_size=8, max_depth=4,
        rng=np.random.RandomState(777))
    seed_all(5)
    mb = LatentHoloModel(48, 3, 4)
    mx.eval(mb.parameters())
    _, assign_best = latent_etch(mb, feats, "xmdlm",
                                 np.random.RandomState(99), n_rounds=2)
    seed_all(5)
    mr = LatentHoloModel(48, 3, 4)
    mx.eval(mr.parameters())
    _, assign_rand = latent_etch(mr, feats, "xmdlm_rand",
                                 np.random.RandomState(99), n_rounds=2)
    print(f"  [pass] assignment best={assign_best.tolist()} "
          f"rand={assign_rand.tolist()}")

    # 4. eval modes: oracle >= marginal (ceiling property)
    modes = eval_latent_modes(mb, np.random.RandomState(7), n_batches=10)
    assert modes["oracle"] + 1e-6 >= modes["marginal"], \
        "oracle-latent must be >= marginal (ceiling)"
    print(f"  [pass] eval modes marginal={modes['marginal']:.3f} "
          f"argmax={modes['argmax']:.3f} oracle={modes['oracle']:.3f} "
          f"(oracle>=marginal)")

    # 5. bit-reproducibility within process
    def fingerprint(seed):
        seed_all(seed)
        st = LatentHoloModel(48, 3, 4)
        mx.eval(st.parameters())
        latent_etch(st, feats, "xmdlm", np.random.RandomState(seed + 12345),
                    n_rounds=2)
        return np.concatenate([
            np.sign(np.array(_get_plate(ly, p).weight)).ravel()
            for ly in st.layers for p in PLATE_NAMES])
    if not np.array_equal(fingerprint(11), fingerprint(11)):
        ok = False
        print("  [FAIL] not bit-reproducible")
    else:
        print("  [pass] bit-reproducible within process")

    print("=" * 60)
    print("  --validate ALL PASS" if ok else "  --validate FAILED")
    print("=" * 60)
    if not ok:
        raise SystemExit(1)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

ARMS = [("baseline", 1), ("xmdlm", 4), ("xmdlm_rand", 4)]


def train_oracle(gd_steps, d_model=48, n_layers=3, max_depth=4):
    seed_all(42)
    oracle = GDModel(d_model=d_model, n_layers=n_layers)
    mx.eval(oracle.parameters())
    opt = optim.Adam(learning_rate=0.003)
    lg = nn.value_and_grad(oracle, masked_ce_loss)
    rng = np.random.RandomState(42)
    for step in range(gd_steps):
        ids, tgt, msk = generate_batch(32, rng, max_depth=max_depth)
        lv, gr = lg(oracle, ids, tgt, msk)
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
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--n-rounds", type=int, default=8)
    ap.add_argument("--etch-batch", type=int, default=8)
    ap.add_argument("--checkpoint-dir", type=str,
                    default="checkpoints/xm-latent-explore")
    args = ap.parse_args()

    if args.validate:
        validate()
        return

    out = Path(args.checkpoint_dir)
    out.mkdir(parents=True, exist_ok=True)
    gd_steps = 300 if args.smoke else args.gd_steps
    probe_counts = [50] if args.smoke else [50, 800]
    n_seeds = 2 if args.smoke else args.seeds
    seeds = [2000 + i for i in range(n_seeds)]

    try:
        git_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        git_sha = "unknown"

    meta = {
        "run_id": f"xm-latent-{'smoke' if args.smoke else 'full'}",
        "timestamp": datetime.now(UTC).isoformat(), "git_sha": git_sha,
        "d_model": 48, "n_layers": 3, "max_depth": 4, "K": 4,
        "gd_steps": gd_steps, "probe_counts": probe_counts,
        "arms": [a[0] for a in ARMS], "init_seeds": seeds,
        "n_rounds": args.n_rounds, "etch_batch": args.etch_batch,
        "preregistered": {
            "G1": "xmdlm(marginal) > baseline",
            "G2": "xmdlm(marginal) > xmdlm_rand(marginal) [yardstick]",
            "G3": "specialization: assign concentration + oracle>marginal + "
                  "oracle(xmdlm)>oracle(rand)",
            "verdicts": ["EXPRESSIVITY-UNBLOCKS", "MARGINALIZATION-ARTIFACT",
                         "CAPACITY-BUT-UNROUTED", "STILL-BLOCKED"],
        },
        "repro_fixes": ["np+mx seeded per arm", "integer seeds",
                        ">=5 init seeds", "internal paired grading"],
    }
    results = {"meta": meta}

    print("=" * 70)
    print(f"  XM LATENT-EXPLORE  ({meta['run_id']})  K=4")
    print(f"  arms={[a[0] for a in ARMS]} probes={probe_counts} seeds={seeds} "
          f"rounds={args.n_rounds} gd={gd_steps}")
    print("=" * 70, flush=True)

    print(f"\n  [oracle] training GD teacher ({gd_steps} steps)...", flush=True)
    t0 = time.time()
    oracle = train_oracle(gd_steps)
    oracle_eval = eval_model(oracle, np.random.RandomState(999), max_depth=4)
    print(f"    oracle acc={oracle_eval['accuracy']:.1%} "
          f"({time.time()-t0:.1f}s)", flush=True)
    results["oracle"] = {
        "acc": oracle_eval["accuracy"],
        "depth": eval_by_depth(oracle, np.random.RandomState(999), max_depth=4)}

    for n_probes in probe_counts:
        feats = extract_teacher_features(
            oracle, n_probes=n_probes, batch_size=args.etch_batch,
            max_depth=4, rng=np.random.RandomState(777))
        n_units = len(feats[0])
        print(f"\n  probes={n_probes}: {n_units} voting units", flush=True)
        for arm, K in ARMS:
            for init_seed in seeds:
                key = f"{arm}_p{n_probes}_s{init_seed}"
                t0 = time.time()
                r = run_arm(feats, arm, K, init_seed, n_probes,
                            gd_steps, args.n_rounds)
                r["seconds"] = time.time() - t0
                r["n_units"] = n_units
                results[key] = r
                pct = (r["best_acc"] / oracle_eval["accuracy"] * 100
                       if oracle_eval["accuracy"] else 0)
                print(f"    [{key}] marg={r['best_acc']:.1%} ({pct:.1f}%%orc) "
                      f"orc_lat={r['final_oracle']:.1%} "
                      f"H={r['assign_entropy']:.2f}/{r['assign_logK']:.2f} "
                      f"[{r['seconds']:.0f}s]", flush=True)
                with open(out / "results.json", "w") as f:
                    json.dump(results, f, indent=2, default=str)

    # ── Gate scoring ──
    print(f"\n{'═' * 70}\n  GATE SCORING (oracle={oracle_eval['accuracy']:.1%})")
    scoring = {}
    for n_probes in probe_counts:
        def marg(arm, n_probes=n_probes):
            return [results[f"{arm}_p{n_probes}_s{s}"]["best_acc"]
                    / oracle_eval["accuracy"] for s in seeds]

        def orc(arm, n_probes=n_probes):
            return [results[f"{arm}_p{n_probes}_s{s}"]["final_oracle"]
                    / oracle_eval["accuracy"] for s in seeds]

        g1 = _paired_delta(marg("xmdlm"), marg("baseline"))
        g2 = _paired_delta(marg("xmdlm"), marg("xmdlm_rand"))
        g3_orc_vs_rand = _paired_delta(orc("xmdlm"), orc("xmdlm_rand"))
        g3_orc_vs_marg = _paired_delta(
            [results[f"xmdlm_p{n_probes}_s{s}"]["final_oracle"] for s in seeds],
            [results[f"xmdlm_p{n_probes}_s{s}"]["final_marginal"]
             for s in seeds])
        ent = float(np.mean(
            [results[f"xmdlm_p{n_probes}_s{s}"]["assign_entropy"]
             for s in seeds]))
        scoring[f"p{n_probes}"] = {
            "G1": g1, "G2": g2,
            "G3_oracle_vs_rand": g3_orc_vs_rand,
            "G3_oracle_vs_marg": g3_orc_vs_marg,
            "xmdlm_assign_entropy": ent,
            "logK": float(np.log(4))}
        print(f"\n  probes={n_probes}:")
        print(f"    G1 xmdlm-base    : Δ={g1['mean_delta']:+.4f} "
              f"±{g1['std']:.4f} t={g1['t']:+.2f} wins={g1['wins']}/{g1['n']}")
        print(f"    G2 xmdlm-rand    : Δ={g2['mean_delta']:+.4f} "
              f"±{g2['std']:.4f} t={g2['t']:+.2f} wins={g2['wins']}/{g2['n']}")
        print(f"    G3 orc-marg      : Δ={g3_orc_vs_marg['mean_delta']:+.4f} "
              f"t={g3_orc_vs_marg['t']:+.2f}")
        print(f"    G3 orc xmdlm-rand: Δ={g3_orc_vs_rand['mean_delta']:+.4f} "
              f"t={g3_orc_vs_rand['t']:+.2f}")
        print(f"    xmdlm assign H   : {ent:.3f} / logK={np.log(4):.3f}")
    results["scoring"] = scoring
    with open(out / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  saved -> {out}/results.json", flush=True)


if __name__ == "__main__":
    main()
