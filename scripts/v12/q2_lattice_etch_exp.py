"""Q2 Lattice Etch — Reconstruct 5D lattice from overdetermined projections.

The crystal wobble problem: GD mixes CE and crystal gradients, they fight.
CE finds accuracy shortcuts that break the lattice. Crystal loss is 6 numbers
trying to constrain 128 dimensions. The marble slides sideways.

Fix: SEPARATE the concerns completely.

Phase 1: LATTICE RECONSTRUCTION (crystal gradient only, no CE)
  - Use crystal_lattice_loss gradient to etch plates directly
  - The gradient of the 4×4 cosine matrix MSE w.r.t. plate signs
    IS the lattice reconstruction signal
  - Each combinator probe = one projection of the 5D lattice
  - Each layer = one depth angle
  - The gradient solves the overdetermined system via backpropagation
  - No beam changes, no CE, no accuracy — just fix the lattice
  - Accumulate sign(grad) over many batches → flip confident positions

Phase 2: BEAM TRAINING (CE only, plates frozen)
  - Plates are now lattice-correct (crystal ≈ 1.0)
  - Freeze plates, train beams with CE for accuracy
  - No crystal wobble because plates don't change
  - Beams learn to read the correct hologram

The 5D lattice is overdetermined:
  4 combinators in ~3-5D = 12-20 coordinates to determine
  3 layers × 20 probes/combinator × 4 combinators = 240 measurements
  Overdetermination: ~12× → robust to 27% sign damage

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/q2_lattice_etch_exp.py 2>&1 | tee results/q2-lattice-etch/run.log

License: MIT
"""

from __future__ import annotations

import json, sys, time
from pathlib import Path
import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, PAD_ID, EQ_ID, TOK2ID,
    TernaryLinear, Comb, Var, App,
    GDModel, HoloModel,
    masked_ce_loss, eval_model,
    generate_batch, full_reduce,
    _get_plates,
)
from mini_holo_crystal import write_crystal_to_model

def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "q2-lattice-etch"
D_TEACHER = 256; D_STUDENT = 128; N_LAYERS = 3
BATCH_SIZE = 32; LR = 0.003; MAX_DEPTH = 4

# Phase 1: lattice etch config
LATTICE_ROUNDS = 20
LATTICE_BATCHES = 50      # gradient accumulation batches per round
LATTICE_CONFIDENCE = 0.5  # accumulator threshold for flipping

# Phase 2: beam training config
BEAM_STEPS = 3000
EVAL_BATCHES = 30

COMBINATORS = ["K", "I", "B", "C"]


# ══════════════════════════════════════════════════════════════════════
# Crystal measurement
# ══════════════════════════════════════════════════════════════════════

def gen_probes(n=20, seed=42):
    rng = np.random.RandomState(seed)
    vs = ["a", "b", "c", "d", "e", "x", "y", "z"]
    fs = ["f", "g", "h"]
    probes = {}
    for c in COMBINATORS:
        ps = []
        for _ in range(n * 3):
            if len(ps) >= n: break
            v1, v2 = Var(rng.choice(vs)), Var(rng.choice(vs))
            f1, f2 = Var(rng.choice(fs)), Var(rng.choice(fs))
            if c == "K": e = App(App(Comb("K"), v1), v2)
            elif c == "I": e = App(Comb("I"), v1)
            elif c == "B": e = App(App(App(Comb("B"), f1), f2), v1)
            elif c == "C": e = App(App(App(Comb("C"), f1), v1), v2)
            t = ["<bos>"] + e.to_tokens() + ["="]
            if not all(x in TOK2ID for x in t): continue
            ids = [TOK2ID[x] for x in t]
            ids = ids[:20] + [PAD_ID] * max(0, 20 - len(ids))
            ps.append(ids)
        probes[c] = ps[:n]
    return probes


def measure_crystal(model, probes):
    means = []
    for c in COMBINATORS:
        hs = []
        for ids in probes[c]:
            x = model.embed(mx.array(np.array([ids], dtype=np.int32)))
            for layer in model.layers: x = layer(x)
            hs.append(np.array(x[0, -1, :]))
        means.append(np.mean(hs, axis=0))
    M = np.array(means)
    N = np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-8)
    return (M / N @ (M / N).T).tolist()


def crystal_agr(s, t):
    A, B = np.array(s), np.array(t)
    idx = np.triu_indices(4, k=1)
    a, b = A[idx] - A[idx].mean(), B[idx] - B[idx].mean()
    d = np.sqrt(np.sum(a**2)) * np.sqrt(np.sum(b**2))
    return float(np.sum(a * b) / d) if d > 1e-10 else 0.0


def crystal_lattice_loss(model, probes, targets):
    """The loss function that reconstructs the lattice.

    MSE between student's 4×4 cosine matrix and teacher's target.
    The gradient of this w.r.t. plate signs IS the lattice reconstruction
    signal — it tells each sign which way to flip to bring the student's
    combinator geometry closer to the teacher's.
    """
    tgt = mx.array(np.array(targets, dtype=np.float32))
    means = []
    for c in COMBINATORS:
        hs = []
        for ids in probes[c]:
            x = model.embed(mx.array(np.array([ids], dtype=np.int32)))
            for layer in model.layers: x = layer(x)
            hs.append(x[0, -1, :])
        means.append(mx.mean(mx.stack(hs), axis=0))
    M = mx.stack(means)
    N = mx.sqrt(mx.sum(M * M, axis=1, keepdims=True) + 1e-8)
    cos = (M / N) @ (M / N).T
    ir, ic = [0, 0, 0, 1, 1, 2], [1, 2, 3, 2, 3, 3]
    return mx.mean(
        (cos[mx.array(ir), mx.array(ic)] - tgt[mx.array(ir), mx.array(ic)]) ** 2
    )


# ══════════════════════════════════════════════════════════════════════
# Extraction helpers
# ══════════════════════════════════════════════════════════════════════

def q2_simulate_weights(W, n_bits=2, block_size=32):
    W_flat = W.flatten(); n = len(W_flat)
    pad = (block_size - n % block_size) % block_size
    W_padded = np.concatenate([W_flat, np.zeros(pad)])
    W_blocks = W_padded.reshape(-1, block_size)
    n_levels = 2 ** (n_bits - 1)
    scales = np.maximum(np.max(np.abs(W_blocks), axis=1, keepdims=True), 1e-10)
    W_norm = W_blocks / scales
    W_quant = np.round(W_norm * n_levels).clip(-n_levels, n_levels)
    W_dequant = (W_quant / n_levels) * scales
    signs = np.sign(W_dequant.flatten()[:n].reshape(W.shape)).astype(np.float32)
    zeros = signs == 0
    if zeros.any():
        signs[zeros] = np.random.RandomState(42).choice([-1.0, 1.0], size=int(zeros.sum()))
    return signs


def extract_oracle_crystal(teacher, ds):
    crystal = []
    for layer in teacher.layers:
        layer_signs = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:ds, :]; W_proj = P @ W @ P.T
            signs = np.sign(W_proj).astype(np.float32)
            zeros = signs == 0
            if zeros.any():
                signs[zeros] = np.random.RandomState(42).choice(
                    [-1.0, 1.0], size=int(zeros.sum()))
            layer_signs[name] = signs
        crystal.append(layer_signs)
    return crystal


def extract_q2_crystal(teacher, ds, n_bits=2):
    crystal = []
    for layer in teacher.layers:
        layer_signs = {}
        for name, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                           ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:ds, :]; W_proj = P @ W @ P.T
            layer_signs[name] = q2_simulate_weights(W_proj, n_bits=n_bits)
        crystal.append(layer_signs)
    return crystal


def extract_mag(teacher, ds):
    t = []
    for layer in teacher.layers:
        lm = {}
        for nm, proj in [("k", layer.attn.k_proj), ("v", layer.attn.v_proj),
                         ("o", layer.attn.o_proj), ("ffn", layer.ffn)]:
            W = np.array(proj.weight)
            _, S, Vt = np.linalg.svd(W, full_matrices=False)
            P = Vt[:ds, :]
            lm[nm] = np.sqrt(np.mean((P @ W @ P.T) ** 2, axis=1)).astype(np.float32)
        t.append(lm)
    return t


def measure_sign_damage(a, b):
    total = 0; damaged = 0
    for i in range(len(a)):
        for k in a[i]:
            total += a[i][k].size
            damaged += int((a[i][k] != b[i][k]).sum())
    return damaged, total


def sign_agreement_with_oracle(model, oracle_crystal):
    total = 0; matching = 0
    for li, layer in enumerate(model.layers):
        for pn in ["k", "v", "o", "ffn"]:
            plate = getattr(layer.attn, f"{pn}_plate") if pn != "ffn" else layer.ffn_plate
            current = np.sign(np.array(plate.weight))
            oracle = oracle_crystal[li][pn]
            total += oracle.size; matching += int((current == oracle).sum())
    return matching / total if total > 0 else 0.0


def make_model(crystal, mag):
    m = HoloModel(d_model=D_STUDENT, n_layers=N_LAYERS); mx.eval(m.parameters())
    write_crystal_to_model(m, crystal)
    for i, l in enumerate(m.layers):
        l.attn.k_scale = mx.array(mag[i]["k"])
        l.attn.v_scale = mx.array(mag[i]["v"])
        l.attn.o_scale = mx.array(mag[i]["o"])
        l.ffn_scale = mx.array(mag[i]["ffn"])
    mx.eval(m.parameters()); return m


def quick_eval(model):
    return eval_model(model, np.random.RandomState(999),
                      n_batches=EVAL_BATCHES, max_depth=MAX_DEPTH)


def train_teacher(d, n=5000):
    m = GDModel(d_model=d, n_layers=N_LAYERS); mx.eval(m.parameters())
    opt = optim.Adam(learning_rate=LR)
    lag = nn.value_and_grad(m, masked_ce_loss)
    rng = np.random.RandomState(42)
    for s in range(n):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(m, ids, tgt, msk); mx.eval(lv, gr)
        m.update(opt.apply_gradients(gr, m)); mx.eval(m.parameters()); del lv, gr
        if (s + 1) % 100 == 0: mx.clear_cache()
        if (s + 1) % 1000 == 0:
            ev = eval_model(m, np.random.RandomState(999), max_depth=MAX_DEPTH)
            log(f"    Step {s+1}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    ev = eval_model(m, np.random.RandomState(999), max_depth=MAX_DEPTH)
    log(f"  Final: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}"); return m


# ══════════════════════════════════════════════════════════════════════
# PHASE 1: Lattice Reconstruction via Crystal Gradient Etch
# ══════════════════════════════════════════════════════════════════════

def lattice_etch_round(model, probes, teacher_crystal):
    """One round of lattice reconstruction.

    Accumulate sign(gradient) of crystal_lattice_loss w.r.t. plate weights.
    The crystal gradient IS the lattice reconstruction signal —
    it tells each sign which way to flip to bring the combinator geometry
    closer to the teacher's 4×4 cosine matrix.

    No CE loss. No beam changes. Pure lattice reconstruction.
    """
    plates = _get_plates(model)
    accumulators = [np.zeros((p.out_features, p.in_features), dtype=np.float64)
                    for _, p in plates]

    plate_paths = []
    for i in range(len(model.layers)):
        plate_paths.append((i, "attn.k_plate"))
        plate_paths.append((i, "attn.v_plate"))
        plate_paths.append((i, "attn.o_plate"))
        plate_paths.append((i, "ffn_plate"))

    def loss_fn(model):
        return crystal_lattice_loss(model, probes, teacher_crystal)

    loss_and_grad = nn.value_and_grad(model, loss_fn)

    total_loss = 0.0
    for b in range(LATTICE_BATCHES):
        loss_val, grads = loss_and_grad(model)
        mx.eval(loss_val, grads)
        total_loss += float(loss_val)

        for pidx, (layer_idx, pname) in enumerate(plate_paths):
            lg = grads.get("layers", [])
            if isinstance(lg, list) and layer_idx < len(lg):
                layer_g = lg[layer_idx]
            else:
                continue
            parts = pname.split(".")
            g = layer_g
            for part in parts:
                if isinstance(g, dict) and part in g:
                    g = g[part]
                else:
                    g = None
                    break
            if g is not None and isinstance(g, dict) and "weight" in g:
                gw = g["weight"]
                mx.eval(gw)
                accumulators[pidx] += np.sign(np.array(gw))

        del loss_val, grads
        if (b + 1) % 25 == 0:
            mx.clear_cache()

    # Flip confident positions
    total_flipped = 0
    for pidx, (_, plate) in enumerate(plates):
        acc = accumulators[pidx]
        confidence = np.abs(acc) / LATTICE_BATCHES
        desired_sign = -np.sign(acc)  # negative gradient direction = toward minimum
        current = np.sign(np.array(plate.weight)).astype(np.float32)

        should_flip = (
            (confidence > LATTICE_CONFIDENCE)
            & (desired_sign != 0)
            & (desired_sign != current)
        )
        new_signs = np.where(should_flip,
                             desired_sign.astype(np.float32),
                             current.astype(np.float32))
        plate.weight = mx.array(new_signs)
        mx.eval(plate.weight)
        total_flipped += int(should_flip.sum())

    avg_loss = total_loss / LATTICE_BATCHES
    return total_flipped, avg_loss


def run_lattice_etch(model, probes, teacher_crystal, oracle_crystal):
    """Phase 1: Reconstruct the lattice by etching plates with crystal gradient.

    Pure crystal loss — no CE, no beam changes, no accuracy optimization.
    Just fix the combinator geometry.
    """
    log("\n  Phase 1: Lattice reconstruction (crystal gradient etch)")
    initial_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
    initial_crystal = crystal_agr(measure_crystal(model, probes), teacher_crystal)
    log(f"    Initial: crystal={initial_crystal:.4f}, sign_agr={initial_sign_agr:.4f}")

    traj = []
    for r in range(LATTICE_ROUNDS):
        flips, avg_loss = lattice_etch_round(model, probes, teacher_crystal)
        crystal = measure_crystal(model, probes)
        agr = crystal_agr(crystal, teacher_crystal)
        sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
        ev = quick_eval(model)

        traj.append({
            "round": r, "flips": flips, "crystal_loss": avg_loss,
            "crystal_agr": agr, "sign_agr": sign_agr,
            "accuracy": ev["accuracy"],
        })

        bar = "█" * max(0, int((agr + 1) * 10))
        log(f"    R{r:2d}: flips={flips:4d}  crystal={agr:+.4f} {bar}  "
            f"sign={sign_agr:.4f}  acc={ev['accuracy']:.4f}  "
            f"loss={avg_loss:.6f}")

        if agr > 0.99:
            log(f"    Lattice converged at round {r}")
            break

        mx.clear_cache()

    final_crystal = crystal_agr(measure_crystal(model, probes), teacher_crystal)
    final_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
    log(f"    Final: crystal={final_crystal:.4f}, sign_agr={final_sign_agr:.4f}")
    log(f"    Crystal: {initial_crystal:.4f} → {final_crystal:.4f}")
    log(f"    Signs:   {initial_sign_agr:.4f} → {final_sign_agr:.4f}")

    return {
        "trajectory": traj,
        "initial_crystal": initial_crystal,
        "final_crystal": final_crystal,
        "initial_sign_agr": initial_sign_agr,
        "final_sign_agr": final_sign_agr,
    }


# ══════════════════════════════════════════════════════════════════════
# PHASE 2: Beam Training (CE only, plates frozen)
# ══════════════════════════════════════════════════════════════════════

def run_beam_training(model, probes, teacher_crystal, oracle_crystal):
    """Phase 2: Train beams with CE, plates frozen.

    The lattice is now correct (crystal ≈ 1.0). Plates don't change.
    Beams learn to read the correct hologram for accuracy.
    """
    log("\n  Phase 2: Beam training (CE only, plates frozen)")

    # Freeze all plates
    for layer in model.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    opt = optim.Adam(learning_rate=LR)
    lag = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    traj = []
    for s in range(BEAM_STEPS):
        ids, tgt, msk = generate_batch(BATCH_SIZE, rng, max_depth=MAX_DEPTH)
        lv, gr = lag(model, ids, tgt, msk); mx.eval(lv, gr)
        model.update(opt.apply_gradients(gr, model))
        mx.eval(model.parameters()); del lv, gr
        if (s + 1) % 50 == 0: mx.clear_cache()
        if (s + 1) % 500 == 0:
            ev = quick_eval(model)
            crystal = crystal_agr(measure_crystal(model, probes), teacher_crystal)
            sign_agr = sign_agreement_with_oracle(model, oracle_crystal)
            traj.append({
                "step": s + 1, "accuracy": ev["accuracy"],
                "loss": ev["loss"], "crystal_agr": crystal,
                "sign_agr": sign_agr,
            })
            log(f"    Step {s+1:4d}: acc={ev['accuracy']:.4f}  "
                f"crystal={crystal:+.4f}  loss={ev['loss']:.4f}")

    final_ev = quick_eval(model)
    final_crystal = crystal_agr(measure_crystal(model, probes), teacher_crystal)
    final_sign_agr = sign_agreement_with_oracle(model, oracle_crystal)

    log(f"    Final: acc={final_ev['accuracy']:.4f}, crystal={final_crystal:.4f}")

    return {
        "trajectory": traj,
        "final_acc": final_ev["accuracy"],
        "final_loss": final_ev["loss"],
        "final_crystal": final_crystal,
        "final_sign_agr": final_sign_agr,
        "best_acc": max(t["accuracy"] for t in traj) if traj else final_ev["accuracy"],
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    results = {}

    # ── Train teacher ──
    log(f"{'═'*60}")
    log(f"Training teacher d={D_TEACHER}...")
    teacher = train_teacher(D_TEACHER, 5000)
    teacher_ev = eval_model(teacher, np.random.RandomState(999), max_depth=MAX_DEPTH)
    results["teacher"] = {"accuracy": teacher_ev["accuracy"], "loss": teacher_ev["loss"]}

    # ── Extractions ──
    probes = gen_probes()
    teacher_crystal = measure_crystal(teacher, probes)
    oracle_crystal = extract_oracle_crystal(teacher, D_STUDENT)
    q2_crystal = extract_q2_crystal(teacher, D_STUDENT, n_bits=2)
    mag = extract_mag(teacher, D_STUDENT)
    damaged, total = measure_sign_damage(oracle_crystal, q2_crystal)
    log(f"\nQ2 sign damage: {damaged}/{total} = {damaged/total*100:.1f}%")
    results["q2_damage"] = {"damaged": damaged, "total": total,
                            "pct": damaged / total * 100}

    log(f"\nTeacher crystal:")
    tc = np.array(teacher_crystal)
    for i, c in enumerate(COMBINATORS):
        log(f"  {c}: " + " ".join(f"{tc[i,j]:+.3f}" for j in range(4)))

    # ══════════════════════════════════════════════════════════════
    # C1: LATTICE ETCH + BEAM TRAINING (THE TEST)
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log(f"C1: LATTICE ETCH + BEAM TRAINING")

    m1 = make_model(q2_crystal, mag)
    phase1 = run_lattice_etch(m1, probes, teacher_crystal, oracle_crystal)
    phase2 = run_beam_training(m1, probes, teacher_crystal, oracle_crystal)
    results["c1_lattice_beam"] = {
        "condition": "LATTICE_ETCH+BEAM",
        "phase1": phase1, "phase2": phase2,
    }
    del m1; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # C2: ORACLE (ceiling — perfect signs, beam training only)
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log(f"C2: ORACLE — perfect projected signs")

    m2 = make_model(oracle_crystal, mag)
    phase2_oracle = run_beam_training(m2, probes, teacher_crystal, oracle_crystal)
    results["c2_oracle"] = {
        "condition": "ORACLE",
        "phase2": phase2_oracle,
    }
    del m2; mx.clear_cache()

    # ══════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════
    elapsed = time.time() - t_start
    results["meta"] = {
        "elapsed_seconds": elapsed,
        "d_teacher": D_TEACHER, "d_student": D_STUDENT,
        "lattice_rounds": LATTICE_ROUNDS,
        "lattice_batches": LATTICE_BATCHES,
        "beam_steps": BEAM_STEPS,
    }

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY — Q2 Lattice Etch")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s")
    log(f"  Teacher: acc={teacher_ev['accuracy']:.4f}")
    log(f"  Q2 damage: {damaged/total*100:.1f}%\n")

    p1 = results["c1_lattice_beam"]["phase1"]
    p2 = results["c1_lattice_beam"]["phase2"]
    log(f"  Phase 1 (lattice etch):")
    log(f"    Crystal: {p1['initial_crystal']:+.4f} → {p1['final_crystal']:+.4f}")
    log(f"    Signs:   {p1['initial_sign_agr']:.4f} → {p1['final_sign_agr']:.4f}")

    log(f"\n  Phase 2 (beam training):")
    log(f"    Accuracy: {p2['final_acc']:.4f} (best={p2['best_acc']:.4f})")
    log(f"    Crystal:  {p2['final_crystal']:+.4f} (should stay stable)")

    p2o = results["c2_oracle"]["phase2"]
    log(f"\n  Oracle ceiling:")
    log(f"    Accuracy: {p2o['final_acc']:.4f} (best={p2o['best_acc']:.4f})")
    log(f"    Crystal:  {p2o['final_crystal']:+.4f}")

    pct = p2['best_acc'] / max(p2o['best_acc'], 1e-8) * 100
    log(f"\n  Lattice etch achieves {pct:.1f}% of oracle accuracy")
    log(f"  Crystal preserved: {'✓' if p2['final_crystal'] > 0.5 else '✗'} "
        f"({p2['final_crystal']:+.4f})")

    log(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
