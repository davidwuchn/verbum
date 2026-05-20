"""Holographic Roundtrip Experiment — Deterministic read/write to ternary plates.

Can we write data into a ternary plate and read it back WITHOUT any GD?

Protocol:
  1. Get hidden states H from teacher (the "addresses" into the crystal)
  2. Get target representations T (what we want the crystal to store)
  3. WRITE: plate = sign(pinv(H) @ T)  — deterministic, one-shot
  4. READ:  readout = H @ plate
  5. VERIFY: cosine_rdm(readout) ≈ cosine_rdm(T)

This tests FOUR things:
  A. Single-crystal write: store Q crystal in a plate, read it back
  B. Single-crystal write: store FFN crystal in a plate, read it back
  C. Dual-crystal write: store BOTH in one plate (holographic multiplexing)
  D. Capacity sweep: how many channels before interference kills fidelity?
  E. Out-of-sample: write with train probes, read back with held-out probes

If A-B work at high fidelity, the crystal IS deterministically writable.
If C works, holographic storage is real.
If E works, the crystal GENERALIZES (it's not memorizing probes).

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/hologram_roundtrip_exp.py

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np


MODEL_NAME = "EleutherAI/pythia-2.8b-deduped"
N_LAYERS = 32
D_MODEL = 2560
D_FFN = 10240
TARGET_LAYER = 16


def cosine_rdm(X: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    return (X / norms) @ (X / norms).T


def rdm_correlation(A: np.ndarray, B: np.ndarray) -> float:
    n = A.shape[0]
    idx = np.triu_indices(n, k=1)
    a = A[idx] - A[idx].mean()
    b = B[idx] - B[idx].mean()
    denom = np.sqrt(np.sum(a**2)) * np.sqrt(np.sum(b**2))
    return float(np.sum(a * b) / denom) if denom > 1e-10 else 0.0


def load_probes() -> list[dict]:
    path = Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json"
    with open(path) as f:
        data = json.load(f)
        return data if isinstance(data, list) else data["probes"]


# ══════════════════════════════════════════════════════════════════════
# The WRITE operation — deterministic, no GD
# ══════════════════════════════════════════════════════════════════════

def write_plate(H: np.ndarray, target: np.ndarray, k: int | None = None) -> np.ndarray:
    """Deterministic ternary plate write.

    Given:
      H:      (n_probes, d_model)  — the hidden states (addresses)
      target: (n_probes, n_target) — what we want to store

    Returns:
      plate:  (d_model, n_target)  — ternary {-1, 0, +1}

    Method:
      1. Compute H_pinv via truncated SVD (regularized pseudoinverse)
      2. plate_continuous = H_pinv @ target
      3. plate = sign(plate_continuous)

    If k is given, truncate SVD to rank k for regularization.
    """
    U, S, Vt = np.linalg.svd(H, full_matrices=False)

    if k is not None:
        k = min(k, len(S))
    else:
        # Auto-select: use components with S > 1% of max
        threshold = S[0] * 0.01
        k = max(1, int(np.sum(S > threshold)))

    S_inv = np.zeros_like(S)
    S_inv[:k] = 1.0 / S[:k]

    H_pinv = (Vt.T * S_inv) @ U.T  # (d_model, n_probes)
    plate_continuous = H_pinv @ target  # (d_model, n_target)
    plate_ternary = np.sign(plate_continuous).astype(np.float32)

    return plate_ternary, plate_continuous


def read_plate(H: np.ndarray, plate: np.ndarray) -> np.ndarray:
    """Deterministic plate read. readout = H @ plate."""
    return H @ plate


# ══════════════════════════════════════════════════════════════════════
# Extract teacher data
# ══════════════════════════════════════════════════════════════════════

def extract_teacher_data(probes: list[dict]) -> tuple:
    """Run probes through Pythia, extract H, Q, UP at target layer."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    print(f"  Loading {MODEL_NAME}...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, dtype=torch.bfloat16, device_map="mps",
    )
    model.eval()
    layer = model.gpt_neox.layers[TARGET_LAYER]

    hidden_states, q_acts, up_acts = [], [], []

    def h_hook(module, inp, out):
        hidden_states.append(inp[0][:, -1, :].detach().cpu().float())
    def qkv_hook(module, inp, out):
        q_acts.append(out[:, -1, :D_MODEL].detach().cpu().float())
    def up_hook(module, inp, out):
        up_acts.append(out[:, -1, :].detach().cpu().float())

    hooks = [
        layer.register_forward_hook(h_hook),
        layer.attention.query_key_value.register_forward_hook(qkv_hook),
        layer.mlp.dense_h_to_4h.register_forward_hook(up_hook),
    ]

    t0 = time.time()
    for i, probe in enumerate(probes):
        ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to("mps")
        with torch.no_grad():
            _ = model(ids)
        if (i + 1) % 50 == 0:
            print(f"    {i+1}/{len(probes)}...", flush=True)
    print(f"  Done in {time.time()-t0:.1f}s", flush=True)

    for h in hooks:
        h.remove()

    import torch as _t
    H = _t.cat(hidden_states, dim=0).numpy()
    Q = _t.cat(q_acts, dim=0).numpy()
    UP = _t.cat(up_acts, dim=0).numpy()

    # Also extract raw weight matrices
    qkv_w = layer.attention.query_key_value.weight.detach().cpu().float().numpy()
    W_q = qkv_w[:D_MODEL, :]
    W_up = layer.mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()

    del model, tokenizer
    gc.collect()
    if _t.backends.mps.is_available():
        _t.mps.empty_cache()

    return H, Q, UP, W_q, W_up


# ══════════════════════════════════════════════════════════════════════
# Experiment A: Single crystal write (Q)
# ══════════════════════════════════════════════════════════════════════

def exp_a_single_crystal_q(H: np.ndarray, Q: np.ndarray, W_q: np.ndarray):
    """Write Q crystal into a ternary plate, read back, verify."""
    print(f"\n{'─'*60}")
    print(f"  Experiment A: Write Q crystal → ternary plate → read back")
    print(f"{'─'*60}")

    rdm_q_truth = cosine_rdm(Q)  # ground truth

    # PCA the Q activations to get a compact target
    Q_mean = Q.mean(axis=0)
    Q_c = Q - Q_mean
    U, S, Vt = np.linalg.svd(Q_c, full_matrices=False)

    results = {}
    for target_k in [8, 16, 32, 64, 128]:
        k = min(target_k, U.shape[1])
        target = U[:, :k] * S[:k]  # (n_probes, k) — PCA scores

        # WRITE
        plate, plate_cont = write_plate(H, target)

        # READ
        readout = read_plate(H, plate)
        readout_cont = read_plate(H, plate_cont)

        # VERIFY
        rdm_tern = cosine_rdm(readout)
        rdm_cont = cosine_rdm(readout_cont)
        fidelity_tern = rdm_correlation(rdm_q_truth, rdm_tern)
        fidelity_cont = rdm_correlation(rdm_q_truth, rdm_cont)

        # Also: PCA-space roundtrip fidelity
        target_rdm = cosine_rdm(target)
        target_fid_tern = rdm_correlation(target_rdm, rdm_tern)

        # For reference: what does sign(W_q) give?
        # (Already measured: 0.974)

        # Plate statistics
        n_zero = np.sum(plate == 0)
        total = plate.size
        sparsity = n_zero / total

        results[target_k] = {
            "fidelity_continuous": fidelity_cont,
            "fidelity_ternary": fidelity_tern,
            "target_roundtrip": target_fid_tern,
            "plate_shape": list(plate.shape),
            "plate_sparsity": float(sparsity),
            "plate_bytes": int(total * 2 / 8),  # 2 bits per ternary
        }

        print(f"    k={target_k:3d}: continuous={fidelity_cont:.4f}  "
              f"ternary={fidelity_tern:.4f}  "
              f"roundtrip={target_fid_tern:.4f}  "
              f"plate={plate.shape} ({sparsity:.1%} sparse)")

    # Also test: direct sign(W_q) as plate
    plate_direct = np.sign(W_q)  # (d_q, d_model) — use transpose for read
    readout_direct = H @ plate_direct.T  # (n_probes, d_q)
    rdm_direct = cosine_rdm(readout_direct)
    fidelity_direct = rdm_correlation(rdm_q_truth, rdm_direct)
    print(f"\n    Direct sign(W_q): fidelity={fidelity_direct:.4f} "
          f"(full rank, {W_q.shape})")

    results["direct_sign_W"] = fidelity_direct
    return results


# ══════════════════════════════════════════════════════════════════════
# Experiment B: Single crystal write (FFN)
# ══════════════════════════════════════════════════════════════════════

def exp_b_single_crystal_ffn(H: np.ndarray, UP: np.ndarray, W_up: np.ndarray):
    """Write FFN crystal into a ternary plate, read back, verify."""
    print(f"\n{'─'*60}")
    print(f"  Experiment B: Write FFN crystal → ternary plate → read back")
    print(f"{'─'*60}")

    rdm_up_truth = cosine_rdm(UP)

    UP_mean = UP.mean(axis=0)
    UP_c = UP - UP_mean
    U, S, Vt = np.linalg.svd(UP_c, full_matrices=False)

    results = {}
    for target_k in [8, 16, 32, 64, 128]:
        k = min(target_k, U.shape[1])
        target = U[:, :k] * S[:k]

        plate, plate_cont = write_plate(H, target)
        readout = read_plate(H, plate)
        readout_cont = read_plate(H, plate_cont)

        rdm_tern = cosine_rdm(readout)
        rdm_cont = cosine_rdm(readout_cont)
        fidelity_tern = rdm_correlation(rdm_up_truth, rdm_tern)
        fidelity_cont = rdm_correlation(rdm_up_truth, rdm_cont)

        target_rdm = cosine_rdm(target)
        target_fid_tern = rdm_correlation(target_rdm, rdm_tern)

        sparsity = float(np.sum(plate == 0)) / plate.size

        results[target_k] = {
            "fidelity_continuous": fidelity_cont,
            "fidelity_ternary": fidelity_tern,
            "target_roundtrip": target_fid_tern,
            "plate_shape": list(plate.shape),
            "plate_sparsity": float(sparsity),
        }

        print(f"    k={target_k:3d}: continuous={fidelity_cont:.4f}  "
              f"ternary={fidelity_tern:.4f}  "
              f"roundtrip={target_fid_tern:.4f}  "
              f"plate={plate.shape} ({sparsity:.1%} sparse)")

    plate_direct = np.sign(W_up)
    readout_direct = H @ plate_direct.T
    rdm_direct = cosine_rdm(readout_direct)
    fidelity_direct = rdm_correlation(rdm_up_truth, rdm_direct)
    print(f"\n    Direct sign(W_up): fidelity={fidelity_direct:.4f} "
          f"(full rank, {W_up.shape})")
    results["direct_sign_W"] = fidelity_direct
    return results


# ══════════════════════════════════════════════════════════════════════
# Experiment C: Dual-crystal holographic write
# ══════════════════════════════════════════════════════════════════════

def exp_c_dual_crystal(H: np.ndarray, Q: np.ndarray, UP: np.ndarray):
    """Write BOTH Q and FFN crystals into ONE plate, read back independently."""
    print(f"\n{'─'*60}")
    print(f"  Experiment C: Dual-crystal holographic write (both in one plate)")
    print(f"{'─'*60}")

    rdm_q_truth = cosine_rdm(Q)
    rdm_up_truth = cosine_rdm(UP)

    # PCA both
    Q_c = Q - Q.mean(axis=0)
    U_q, S_q, _ = np.linalg.svd(Q_c, full_matrices=False)
    UP_c = UP - UP.mean(axis=0)
    U_up, S_up, _ = np.linalg.svd(UP_c, full_matrices=False)

    results = {}
    for target_k in [8, 16, 32, 64]:
        k_q = min(target_k, U_q.shape[1])
        k_up = min(target_k, U_up.shape[1])

        target_q = U_q[:, :k_q] * S_q[:k_q]
        target_up = U_up[:, :k_up] * S_up[:k_up]

        # COMBINED target: [Q scores | FFN scores]
        target_combined = np.hstack([target_q, target_up])

        # WRITE one plate for both
        plate, plate_cont = write_plate(H, target_combined)

        # READ and split
        readout = read_plate(H, plate)
        q_read = readout[:, :k_q]
        up_read = readout[:, k_q:]

        readout_cont = read_plate(H, plate_cont)
        q_read_cont = readout_cont[:, :k_q]
        up_read_cont = readout_cont[:, k_q:]

        # VERIFY each crystal independently
        fid_q_tern = rdm_correlation(rdm_q_truth, cosine_rdm(q_read))
        fid_q_cont = rdm_correlation(rdm_q_truth, cosine_rdm(q_read_cont))
        fid_up_tern = rdm_correlation(rdm_up_truth, cosine_rdm(up_read))
        fid_up_cont = rdm_correlation(rdm_up_truth, cosine_rdm(up_read_cont))

        # CROSS-TALK: does the Q channel leak FFN, or vice versa?
        xtalk_q_has_up = rdm_correlation(rdm_up_truth, cosine_rdm(q_read))
        xtalk_up_has_q = rdm_correlation(rdm_q_truth, cosine_rdm(up_read))

        sparsity = float(np.sum(plate == 0)) / plate.size

        results[target_k] = {
            "q_continuous": fid_q_cont,
            "q_ternary": fid_q_tern,
            "up_continuous": fid_up_cont,
            "up_ternary": fid_up_tern,
            "crosstalk_q_has_up": xtalk_q_has_up,
            "crosstalk_up_has_q": xtalk_up_has_q,
            "plate_shape": list(plate.shape),
            "plate_cols": k_q + k_up,
            "plate_sparsity": float(sparsity),
        }

        print(f"    k={target_k:3d} (plate {plate.shape[0]}×{k_q+k_up}):")
        print(f"      Q:  cont={fid_q_cont:.4f}  tern={fid_q_tern:.4f}")
        print(f"      UP: cont={fid_up_cont:.4f}  tern={fid_up_tern:.4f}")
        print(f"      Crosstalk: Q→UP={xtalk_q_has_up:.4f}  UP→Q={xtalk_up_has_q:.4f}")

    return results


# ══════════════════════════════════════════════════════════════════════
# Experiment D: Capacity sweep
# ══════════════════════════════════════════════════════════════════════

def exp_d_capacity(H: np.ndarray, Q: np.ndarray):
    """How many independent channels can one plate hold?"""
    print(f"\n{'─'*60}")
    print(f"  Experiment D: Capacity sweep — channels vs fidelity")
    print(f"{'─'*60}")

    rdm_truth = cosine_rdm(Q)
    n_probes, d_model = H.shape

    Q_c = Q - Q.mean(axis=0)
    U, S, _ = np.linalg.svd(Q_c, full_matrices=False)

    results = {}
    # Store increasing numbers of PCA channels
    for n_channels in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]:
        if n_channels > U.shape[1]:
            break

        target = U[:, :n_channels] * S[:n_channels]
        plate, _ = write_plate(H, target)
        readout = read_plate(H, plate)
        rdm_read = cosine_rdm(readout)
        fidelity = rdm_correlation(rdm_truth, rdm_read)

        # Per-channel fidelity: how well is each channel preserved?
        channel_fids = []
        for c in range(n_channels):
            orig = target[:, c]
            recon = readout[:, c]
            cos = np.dot(orig, recon) / (np.linalg.norm(orig) * np.linalg.norm(recon) + 1e-10)
            channel_fids.append(float(cos))

        mean_ch_fid = np.mean(channel_fids)
        min_ch_fid = np.min(channel_fids)

        results[n_channels] = {
            "rdm_fidelity": fidelity,
            "mean_channel_cosine": mean_ch_fid,
            "min_channel_cosine": min_ch_fid,
            "plate_elements": int(d_model * n_channels),
        }

        print(f"    channels={n_channels:5d}: rdm_fidelity={fidelity:.4f}  "
              f"mean_channel_cos={mean_ch_fid:.4f}  "
              f"min_channel_cos={min_ch_fid:.4f}")

    return results


# ══════════════════════════════════════════════════════════════════════
# Experiment E: Out-of-sample generalization
# ══════════════════════════════════════════════════════════════════════

def exp_e_generalization(
    H_train: np.ndarray, Q_train: np.ndarray,
    H_test: np.ndarray, Q_test: np.ndarray,
):
    """Write with train probes, read back with test probes."""
    print(f"\n{'─'*60}")
    print(f"  Experiment E: Generalization (train write, test read)")
    print(f"  Train: {H_train.shape[0]} probes, Test: {H_test.shape[0]} probes")
    print(f"{'─'*60}")

    rdm_train = cosine_rdm(Q_train)
    rdm_test = cosine_rdm(Q_test)

    Q_mean = Q_train.mean(axis=0)
    Q_c = Q_train - Q_mean

    U, S, Vt = np.linalg.svd(Q_c, full_matrices=False)

    results = {}
    for target_k in [8, 16, 32, 64]:
        k = min(target_k, U.shape[1])
        target_train = U[:, :k] * S[:k]

        # WRITE from train data
        plate, _ = write_plate(H_train, target_train)

        # READ with train (in-sample)
        readout_train = read_plate(H_train, plate)
        rdm_train_read = cosine_rdm(readout_train)
        fid_train = rdm_correlation(rdm_train, rdm_train_read)

        # READ with test (out-of-sample)
        readout_test = read_plate(H_test, plate)
        rdm_test_read = cosine_rdm(readout_test)
        fid_test = rdm_correlation(rdm_test, rdm_test_read)

        results[target_k] = {
            "train_fidelity": fid_train,
            "test_fidelity": fid_test,
            "generalization_gap": fid_train - fid_test,
        }

        print(f"    k={target_k:3d}: train={fid_train:.4f}  "
              f"test={fid_test:.4f}  "
              f"gap={fid_train - fid_test:+.4f}")

    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    output_dir = Path("/Users/mwhitford/src/verbum/results/hologram-roundtrip")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"  Holographic Roundtrip — Deterministic Read/Write Test")
    print(f"  Model: {MODEL_NAME} layer {TARGET_LAYER}")
    print(f"{'='*70}")

    probes = load_probes()
    print(f"  Probes: {len(probes)}")

    # ── Extract teacher data ──────────────────────────────────
    print(f"\n  Extracting teacher activations + weights...")
    H, Q, UP, W_q, W_up = extract_teacher_data(probes)
    print(f"  H:  {H.shape}  Q:  {Q.shape}  UP:  {UP.shape}")
    print(f"  W_q: {W_q.shape}  W_up: {W_up.shape}")

    # ── Run experiments ───────────────────────────────────────
    results = {}
    results["A_single_q"] = exp_a_single_crystal_q(H, Q, W_q)
    results["B_single_ffn"] = exp_b_single_crystal_ffn(H, UP, W_up)
    results["C_dual_crystal"] = exp_c_dual_crystal(H, Q, UP)
    results["D_capacity"] = exp_d_capacity(H, Q)

    # Train/test split for generalization
    n = H.shape[0]
    idx = np.random.RandomState(42).permutation(n)
    split = n * 3 // 4
    train_idx, test_idx = idx[:split], idx[split:]
    results["E_generalization"] = exp_e_generalization(
        H[train_idx], Q[train_idx], H[test_idx], Q[test_idx])

    # ── Final summary ─────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  FINAL SUMMARY")
    print(f"{'='*70}")

    print(f"\n  A. Q crystal roundtrip (best k):")
    best_a = max(results["A_single_q"].items(),
                 key=lambda x: x[1]["fidelity_ternary"] if isinstance(x[1], dict) else -1)
    if isinstance(best_a[1], dict):
        print(f"     k={best_a[0]}: ternary={best_a[1]['fidelity_ternary']:.4f}  "
              f"continuous={best_a[1]['fidelity_continuous']:.4f}")
    print(f"     sign(W_q) direct: {results['A_single_q']['direct_sign_W']:.4f}")

    print(f"\n  B. FFN crystal roundtrip (best k):")
    best_b = max(results["B_single_ffn"].items(),
                 key=lambda x: x[1]["fidelity_ternary"] if isinstance(x[1], dict) else -1)
    if isinstance(best_b[1], dict):
        print(f"     k={best_b[0]}: ternary={best_b[1]['fidelity_ternary']:.4f}  "
              f"continuous={best_b[1]['fidelity_continuous']:.4f}")
    print(f"     sign(W_up) direct: {results['B_single_ffn']['direct_sign_W']:.4f}")

    print(f"\n  C. Dual crystal (both in one plate, k=16):")
    if 16 in results["C_dual_crystal"]:
        c = results["C_dual_crystal"][16]
        print(f"     Q:  ternary={c['q_ternary']:.4f}")
        print(f"     UP: ternary={c['up_ternary']:.4f}")
        print(f"     Cross-talk: Q→UP={c['crosstalk_q_has_up']:.4f}  "
              f"UP→Q={c['crosstalk_up_has_q']:.4f}")

    print(f"\n  D. Capacity (channels until fidelity < 0.5):")
    for nc, d in sorted(results["D_capacity"].items()):
        if d["rdm_fidelity"] < 0.5:
            print(f"     Capacity limit: ~{nc} channels "
                  f"(fidelity={d['rdm_fidelity']:.4f})")
            break
    else:
        last = sorted(results["D_capacity"].items())[-1]
        print(f"     All tested channels work: {last[0]} channels "
              f"(fidelity={last[1]['rdm_fidelity']:.4f})")

    print(f"\n  E. Generalization (k=32):")
    if 32 in results["E_generalization"]:
        e = results["E_generalization"][32]
        print(f"     Train: {e['train_fidelity']:.4f}  "
              f"Test: {e['test_fidelity']:.4f}  "
              f"Gap: {e['generalization_gap']:+.4f}")

    is_deterministic = (
        isinstance(best_a[1], dict) and best_a[1]["fidelity_ternary"] > 0.7
        and isinstance(best_b[1], dict) and best_b[1]["fidelity_ternary"] > 0.5
    )
    print(f"\n  ──────────────────────────────────────────────")
    if is_deterministic:
        print(f"  ✅ DETERMINISTIC READ/WRITE WORKS.")
        print(f"     Ternary plates can store crystal structure without GD.")
        print(f"     V12 should etch holograms FROM the teacher, not learn them.")
    else:
        print(f"  ❌ Deterministic read/write insufficient.")
        print(f"     Some GD may still be needed for fine-tuning.")

    # ── Save ──────────────────────────────────────────────────
    out_path = output_dir / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2,
                  default=lambda x: x.tolist() if hasattr(x, 'tolist') else str(x))
    print(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
