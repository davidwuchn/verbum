# register: functional
"""Ternary sign-fitting: exact 3-way ΔL acceptance vs gradient-proxy.

THE CLAIM (Michael, session 213): instead of TD's gradient-EMA *proxy* for
deciding sign flips, directly evaluate the loss for all three ternary values
{-1, 0, +1} at each position and take the one that improves loss most.

THE FEASIBILITY INSIGHT: for a layer-local quadratic reconstruction target you
do NOT need a forward pass per position. For one linear layer with effective
ternary weight S (per-row scale γ), real calibration input X (n × d_in), and
teacher target T = X @ W_floatᵀ (n × d_out), the rows are independent and the
exact loss-delta of changing S[i,j] from a to v is, in closed form:

    ΔL_ij(v) = 2·γ_i·(v−a)·⟨r_i, X[:,j]⟩  +  γ_i²·(v−a)²·‖X[:,j]‖²
                └────── linear (= gradient) ──┘   └──── curvature ────┘

where r_i = γ_i·(X@S[i,:]) − T[:,i] is the current per-row residual. The whole
(d_out × d_in) grid of ⟨r_i,X[:,j]⟩ is one matmul Rᵀ@X. The LINEAR term is
exactly the gradient TD already uses; the CURVATURE term is what the proxy
throws away. For ternary the step (v−a) is large (up to 2) → curvature is NOT
negligible → it is precisely the missing piece, and only accepting flips with
ΔL<0 makes the search MONOTONE (dissolving the s191 oscillation wall by
construction).

THREE ARMS (all start from S0 = sign(W_float), γ optimal per row):
  PROXY       — rank candidates by |gradient|, flip toward −sign(grad);
                NO curvature check (faithful linear analog of TD acceptance).
  EXACT-BATCH — closed-form 3-way argmin ΔL, take top-B *improving* per step.
  EXACT-SEQ   — greedy ONE-at-a-time with residual compensation (GPTQ/OBS
                gold standard), monotone to convergence.

METRICS: relative reconstruction loss trajectory, oscillation/reversal
fraction, # loss-increasing steps (monotonicity), final sparsity.

Substrate: checkpoints/micro/final (4-layer float32 lambda-calculus model).
License: MIT.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import mlx.core as mx
import mlx.nn as nn

# Import the micro model
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "micro"))
from micro_model import MicroModel, MicroConfig  # noqa: E402


# ══════════════════════════════════════════════════════════════════════
# Load model + capture real layer activations
# ══════════════════════════════════════════════════════════════════════

def load_micro(ckpt: Path) -> MicroModel:
    cfg = MicroConfig()
    model = MicroModel(cfg)
    flat = list(mx.load(str(ckpt / "model.npz")).items())
    model.update(nn.utils.tree_unflatten(flat))
    mx.eval(model.parameters())
    return model


def tokenize_calibration(cfg: MicroConfig, n_examples: int, seq_cap: int) -> mx.array:
    """Tokenize compile-train examples into one packed (B, L) batch."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    examples = []
    with open(REPO / "data" / "compile-train.jsonl") as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    examples = examples[:n_examples]
    stream: list[int] = []
    for ex in examples:
        ids = tok.encode(f"{ex['input']}\n{ex['output']}", add_special_tokens=False)
        ids.append(cfg.eod_id)
        stream.extend(ids)
    # pack into rows of length seq_cap
    n_rows = max(1, len(stream) // seq_cap)
    stream = stream[: n_rows * seq_cap]
    arr = np.array(stream, dtype=np.int32).reshape(n_rows, seq_cap)
    return mx.array(arr)


def capture_layer_io(
    model: MicroModel, tokens: mx.array, layer_idx: int, which: str
) -> tuple[mx.array, mx.array]:
    """Manual forward; return (X, W_float) for the chosen linear.

    which ∈ {"gate_proj", "key_proj", "value_proj", "o_proj"}.
    X is the real input activation to that linear, flattened to (n, d_in).
    """
    cfg = model.cfg
    B, L = tokens.shape
    positions = mx.arange(L)
    x = model.embed(tokens) + model.pos_embed(positions)
    mask = model._get_causal_mask(L)

    X = None
    Wf = None
    for i, block in enumerate(model.blocks):
        normed_attn = block.attn_norm(x)
        x = x + block.attn(normed_attn, mask=mask)
        normed_ffn = block.ffn_norm(x)
        if i == layer_idx:
            ffn = block.ffn
            if which == "gate_proj":
                X, Wf = normed_ffn, ffn.gate_proj.weight
            elif which == "key_proj":
                X, Wf = normed_ffn, ffn.key_proj.weight
            elif which == "value_proj":
                gate = nn.silu(ffn.gate_proj(normed_ffn))
                key = ffn.key_proj(normed_ffn)
                X, Wf = gate * key, ffn.value_proj.weight
            elif which == "o_proj":
                raise NotImplementedError("o_proj capture not wired")
            else:
                raise ValueError(which)
            break
        x = x + block.ffn(normed_ffn)

    X = X.reshape(-1, X.shape[-1])  # (n, d_in)
    mx.eval(X, Wf)
    return X, Wf


# ══════════════════════════════════════════════════════════════════════
# Core fitting math (numpy for clarity + exact control)
# ══════════════════════════════════════════════════════════════════════

def optimal_gamma(P: np.ndarray, T: np.ndarray) -> np.ndarray:
    """Per-row least-squares scale. P,T are (d_out, n). γ_i = <P_i,T_i>/‖P_i‖²."""
    num = np.einsum("in,in->i", P, T)
    den = np.einsum("in,in->i", P, P) + 1e-12
    return num / den


def rel_loss(S: np.ndarray, gamma: np.ndarray, X: np.ndarray, T: np.ndarray) -> float:
    """‖γ⊙(S@Xᵀ) − T‖² / ‖T‖²  (rows = d_out)."""
    P = S @ X.T                     # (d_out, n)
    pred = gamma[:, None] * P       # (d_out, n)
    Tt = T.T                        # (d_out, n)
    return float(np.sum((pred - Tt) ** 2) / (np.sum(Tt ** 2) + 1e-12))


def delta_grid(S, gamma, R, XtX_diag, G):
    """Exact ΔL for v ∈ {-1,0,+1} at every position. Returns (best_v, best_delta).

    G        = (R @ X)               (d_out, d_in)  — ⟨r_i, X[:,j]⟩
    XtX_diag = ‖X[:,j]‖²             (d_in,)
    """
    g = gamma[:, None]              # (d_out,1)
    col = XtX_diag[None, :]         # (1,d_in)
    best_v = S.copy()
    best_delta = np.zeros_like(S, dtype=np.float64)  # v == current → ΔL 0
    for v in (-1.0, 0.0, 1.0):
        step = (v - S)
        dl = 2.0 * g * step * G + (g ** 2) * (step ** 2) * col
        take = dl < best_delta
        best_delta = np.where(take, dl, best_delta)
        best_v = np.where(take, v, best_v)
    return best_v, best_delta


# ══════════════════════════════════════════════════════════════════════
# Arms
# ══════════════════════════════════════════════════════════════════════

def run_proxy(X, T, S0, n_steps, budget, recover_window=4):
    """Gradient-proxy: rank by |gradient|, flip toward −sign(grad). No curvature."""
    d_out, d_in = S0.shape
    S = S0.copy().astype(np.float64)
    XtX_diag = np.einsum("nj,nj->j", X, X)
    hist = {"rel_loss": [], "n_flips": [], "reversal_frac": [], "loss_up": 0}
    prev_S = [S.copy()]
    P = S @ X.T
    gamma = optimal_gamma(P, T.T)
    prev_loss = rel_loss(S, gamma, X, T)
    hist["rel_loss"].append(prev_loss)
    hist["n_flips"].append(0)
    hist["reversal_frac"].append(0.0)
    for _ in range(n_steps):
        P = S @ X.T                          # (d_out, n)
        R = gamma[:, None] * P - T.T         # (d_out, n) residual
        G = R @ X                            # (d_out, d_in)  linear term core
        c = 2.0 * gamma[:, None] * G         # gradient coefficient ∂L/∂S
        v_proxy = -np.sign(c)                # linear-optimal extreme value
        v_proxy[v_proxy == 0] = S[v_proxy == 0]  # zero grad → keep
        score = np.abs(c)
        cand = v_proxy != S
        score = np.where(cand, score, -np.inf)
        flat = score.ravel()
        k = min(budget, int(np.sum(cand)))
        if k <= 0:
            hist["rel_loss"].append(prev_loss)
            hist["n_flips"].append(0)
            hist["reversal_frac"].append(0.0)
            continue
        idx = np.argpartition(flat, -k)[-k:]
        mask = np.zeros(flat.shape, dtype=bool)
        mask[idx] = True
        mask = mask.reshape(S.shape) & cand
        # reversal detection vs `recover_window` steps ago
        ref = prev_S[max(0, len(prev_S) - recover_window)]
        new_S = np.where(mask, v_proxy, S)
        reversals = np.sum(mask & (new_S == ref) & (ref != S))
        nf = int(np.sum(new_S != S))
        S = new_S
        gamma = optimal_gamma(S @ X.T, T.T)
        loss = rel_loss(S, gamma, X, T)
        if loss > prev_loss + 1e-12:
            hist["loss_up"] += 1
        prev_loss = loss
        prev_S.append(S.copy())
        hist["rel_loss"].append(loss)
        hist["n_flips"].append(nf)
        hist["reversal_frac"].append(float(reversals) / max(nf, 1))
    hist["final_sparsity"] = float(np.mean(S == 0))
    hist["S"] = S
    return hist


def run_exact_batch(X, T, S0, n_steps, budget, recover_window=4):
    """Exact 3-way ΔL, take top-B *improving* per step."""
    d_out, d_in = S0.shape
    S = S0.copy().astype(np.float64)
    XtX_diag = np.einsum("nj,nj->j", X, X)
    hist = {"rel_loss": [], "n_flips": [], "reversal_frac": [], "loss_up": 0}
    prev_S = [S.copy()]
    gamma = optimal_gamma(S @ X.T, T.T)
    prev_loss = rel_loss(S, gamma, X, T)
    hist["rel_loss"].append(prev_loss)
    hist["n_flips"].append(0)
    hist["reversal_frac"].append(0.0)
    for _ in range(n_steps):
        P = S @ X.T
        R = gamma[:, None] * P - T.T
        G = R @ X
        best_v, best_delta = delta_grid(S, gamma, R, XtX_diag, G)
        improving = best_delta < -1e-12
        score = np.where(improving, -best_delta, -np.inf)  # bigger = better
        flat = score.ravel()
        k = min(budget, int(np.sum(improving)))
        if k <= 0:
            hist["rel_loss"].append(prev_loss)
            hist["n_flips"].append(0)
            hist["reversal_frac"].append(0.0)
            continue
        idx = np.argpartition(flat, -k)[-k:]
        mask = np.zeros(flat.shape, dtype=bool)
        mask[idx] = True
        mask = mask.reshape(S.shape) & improving
        ref = prev_S[max(0, len(prev_S) - recover_window)]
        new_S = np.where(mask, best_v, S)
        reversals = np.sum(mask & (new_S == ref) & (ref != S))
        nf = int(np.sum(new_S != S))
        S = new_S
        gamma = optimal_gamma(S @ X.T, T.T)
        loss = rel_loss(S, gamma, X, T)
        if loss > prev_loss + 1e-12:
            hist["loss_up"] += 1
        prev_loss = loss
        prev_S.append(S.copy())
        hist["rel_loss"].append(loss)
        hist["n_flips"].append(nf)
        hist["reversal_frac"].append(float(reversals) / max(nf, 1))
    hist["final_sparsity"] = float(np.mean(S == 0))
    hist["S"] = S
    return hist


def run_exact_seq(X, T, S0, max_flips, log_every, recompute_gamma=True):
    """Greedy one-at-a-time with residual compensation (GPTQ/OBS gold).

    Maintains R (d_out,n) and G=R@X (d_out,d_in). Each pick: global argmin ΔL,
    apply single best flip, recompute that row's γ + residual + G row. Monotone.
    """
    d_out, d_in = S0.shape
    S = S0.copy().astype(np.float64)
    XtX_diag = np.einsum("nj,nj->j", X, X)
    Tt = T.T  # (d_out, n)
    P = S @ X.T
    gamma = optimal_gamma(P, Tt)
    R = gamma[:, None] * P - Tt
    G = R @ X
    traj = {"rel_loss": [], "n_flips": [], "loss_up": 0}
    base = float(np.sum(Tt ** 2) + 1e-12)
    cur = float(np.sum(R ** 2) / base)
    traj["rel_loss"].append(cur)
    traj["n_flips"].append(0)
    prev_loss = cur
    flips = 0
    while flips < max_flips:
        best_v, best_delta = delta_grid(S, gamma, R, XtX_diag, G)
        flat = best_delta.ravel()
        pos = int(np.argmin(flat))
        if flat[pos] >= -1e-12:
            break  # no improving move → converged
        i, j = divmod(pos, d_in)
        v = best_v[i, j]
        a = S[i, j]
        # apply flip on pre-scale P_i, recompute γ_i (compensation), residual, G row
        S[i, j] = v
        Pi = P[i] + (v - a) * X[:, j]
        P[i] = Pi
        gi = float((Pi @ Tt[i]) / (Pi @ Pi + 1e-12))
        gamma[i] = gi
        R[i] = gi * Pi - Tt[i]
        G[i] = R[i] @ X
        flips += 1
        if flips % log_every == 0:
            cur = float(np.sum(R ** 2) / base)
            if cur > prev_loss + 1e-12:
                traj["loss_up"] += 1
            prev_loss = cur
            traj["rel_loss"].append(cur)
            traj["n_flips"].append(flips)
    cur = float(np.sum(R ** 2) / base)
    traj["rel_loss"].append(cur)
    traj["n_flips"].append(flips)
    traj["final_sparsity"] = float(np.mean(S == 0))
    traj["total_flips"] = flips
    traj["S"] = S
    return traj


# ══════════════════════════════════════════════════════════════════════
# Self-test: closed-form ΔL vs brute-force recompute
# ══════════════════════════════════════════════════════════════════════

def selftest_delta(X, T, S0, gamma, n_probe=200, seed=0):
    """Assert the closed-form ΔL matches a brute-force loss recompute."""
    rng = np.random.RandomState(seed)
    d_out, d_in = S0.shape
    S = S0.astype(np.float64)
    P = S @ X.T
    R = gamma[:, None] * P - T.T
    G = R @ X
    XtX_diag = np.einsum("nj,nj->j", X, X)
    base_loss = np.sum(R ** 2, axis=1)  # per-row absolute SSE
    max_err = 0.0
    for _ in range(n_probe):
        i = rng.randint(d_out)
        j = rng.randint(d_in)
        a = S[i, j]
        for v in (-1.0, 0.0, 1.0):
            # closed form
            step = v - a
            dl_cf = 2.0 * gamma[i] * step * G[i, j] + (gamma[i] ** 2) * (step ** 2) * XtX_diag[j]
            # brute force (γ held fixed, as in the closed form)
            Pi = P[i] + step * X[:, j]
            ri = gamma[i] * Pi - T.T[i]
            dl_bf = np.sum(ri ** 2) - base_loss[i]
            max_err = max(max_err, abs(dl_cf - dl_bf))
    return max_err


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=str(REPO / "checkpoints" / "micro" / "final"))
    ap.add_argument("--out", default=str(REPO / "results" / "ternary-exact-vs-proxy"))
    ap.add_argument("--layers", default="0,2")
    ap.add_argument("--matrices", default="gate_proj,value_proj")
    ap.add_argument("--n-examples", type=int, default=509)
    ap.add_argument("--seq-cap", type=int, default=64)
    ap.add_argument("--steps", type=int, default=120)
    ap.add_argument("--flip-rate", type=float, default=0.005)
    ap.add_argument("--seq-max-mult", type=float, default=1.5,
                    help="exact-seq max_flips = mult × n_weights")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("TERNARY SIGN-FITTING: exact 3-way ΔL vs gradient-proxy")
    print("register: functional | substrate: checkpoints/micro/final")
    print("=" * 70)

    cfg = MicroConfig()
    model = load_micro(Path(args.ckpt))
    tokens = tokenize_calibration(cfg, args.n_examples, args.seq_cap)
    print(f"calibration tokens: {tokens.shape} = {tokens.size} positions")

    layers = [int(x) for x in args.layers.split(",")]
    matrices = args.matrices.split(",")

    results = {
        "meta": {
            "register": "functional",
            "ckpt": str(args.ckpt),
            "calibration_shape": list(tokens.shape),
            "steps": args.steps,
            "flip_rate": args.flip_rate,
            "git_sha": None,
        },
        "configs": {},
    }

    for layer_idx in layers:
        for which in matrices:
            tag = f"L{layer_idx}.{which}"
            print(f"\n{'─'*70}\n{tag}")
            X_mx, Wf_mx = capture_layer_io(model, tokens, layer_idx, which)
            X = np.array(X_mx, dtype=np.float64)        # (n, d_in)
            Wf = np.array(Wf_mx, dtype=np.float64)      # (d_out, d_in)
            T = X @ Wf.T                                # (n, d_out)
            d_out, d_in = Wf.shape
            n_weights = d_out * d_in
            budget = max(1, int(args.flip_rate * n_weights))
            S0 = np.sign(Wf)
            S0[S0 == 0] = 1.0
            # init optimal gamma for self-test + baseline
            gamma0 = optimal_gamma(S0 @ X.T, T.T)
            base_rel = rel_loss(S0, gamma0, X, T)

            # ── self-test the closed form ──
            err = selftest_delta(X, T, S0, gamma0)
            assert err < 1e-6, f"ΔL closed-form mismatch: {err}"
            print(f"  shape={Wf.shape} n={X.shape[0]} budget={budget}/step "
                  f"| ΔL self-test max_err={err:.2e} ✓")
            print(f"  baseline sign(W) rel_loss = {base_rel:.4f}")

            t0 = time.time()
            proxy = run_proxy(X, T, S0, args.steps, budget)
            batch = run_exact_batch(X, T, S0, args.steps, budget)
            seq = run_exact_seq(
                X, T, S0,
                max_flips=int(args.seq_max_mult * n_weights),
                log_every=budget,
            )
            dt = time.time() - t0

            def summ(h, seq=False):
                return {
                    "final_rel_loss": h["rel_loss"][-1],
                    "min_rel_loss": min(h["rel_loss"]),
                    "loss_up_steps": h["loss_up"],
                    "final_sparsity": h["final_sparsity"],
                    "rel_loss_curve": [round(v, 5) for v in h["rel_loss"]],
                    **({"total_flips": h.get("total_flips")} if seq else
                       {"reversal_frac_mean": float(np.mean(h["reversal_frac"])),
                        "total_flips": int(np.sum(h["n_flips"]))}),
                }

            cfg_res = {
                "shape": [d_out, d_in],
                "n_calib": int(X.shape[0]),
                "n_weights": n_weights,
                "budget_per_step": budget,
                "baseline_sign_rel_loss": base_rel,
                "proxy": summ(proxy),
                "exact_batch": summ(batch),
                "exact_seq": summ(seq, seq=True),
                "wall_s": round(dt, 1),
            }
            results["configs"][tag] = cfg_res

            print(f"  PROXY      final={proxy['rel_loss'][-1]:.4f} "
                  f"min={min(proxy['rel_loss']):.4f} up_steps={proxy['loss_up']} "
                  f"rev={np.mean(proxy['reversal_frac']):.3f} "
                  f"flips={int(np.sum(proxy['n_flips']))}")
            print(f"  EXACT-BATCH final={batch['rel_loss'][-1]:.4f} "
                  f"min={min(batch['rel_loss']):.4f} up_steps={batch['loss_up']} "
                  f"rev={np.mean(batch['reversal_frac']):.3f} "
                  f"flips={int(np.sum(batch['n_flips']))}")
            print(f"  EXACT-SEQ   final={seq['rel_loss'][-1]:.4f} "
                  f"up_steps={seq['loss_up']} flips={seq['total_flips']} "
                  f"sparsity={seq['final_sparsity']:.3f}")
            print(f"  ({dt:.1f}s)")

    # provenance
    try:
        import subprocess
        sha = subprocess.check_output(
            ["git", "-C", str(REPO), "rev-parse", "HEAD"]).decode().strip()
        results["meta"]["git_sha"] = sha
    except Exception:
        pass

    out_path = out_dir / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
